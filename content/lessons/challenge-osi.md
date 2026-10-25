# Challenge d’architecture réseau — Réseau de bureau

> **Fichier :** `challenge-osi.md`  
> **Domaine :** architecture réseau, commutation, routage, cybersécurité et dépannage  
> **Niveau :** progression Débutant → Intermédiaire → Expert  
> **Environnement :** réseau d’entreprise avec postes utilisateurs, serveurs, téléphonie IP, Wi-Fi, imprimantes et accès Internet  
> **Mode de travail :** conception, simulation, configuration, tests et justification technique  
> **Objectif final :** concevoir, documenter et valider une architecture de réseau de bureau sécurisée, segmentée, évolutive et exploitable en production.


# 1. Présentation du challenge

## 1.1. Contexte de l’entreprise

Vous êtes chargé de concevoir le réseau informatique de **NovaTech**, une entreprise qui occupe un bâtiment de bureaux comprenant plusieurs équipes.

L’entreprise compte environ 80 collaborateurs et souhaite moderniser son infrastructure réseau.

Le réseau actuel présente plusieurs problèmes :

- Les postes de travail et les imprimantes partagent trop souvent les mêmes segments réseau.
- Les accès aux serveurs ne sont pas suffisamment contrôlés.
- Le Wi-Fi des visiteurs n'est pas correctement isolé du réseau interne.
- Les équipements réseau sont administrés depuis des postes ordinaires.
- Les incidents sont difficiles à diagnostiquer faute de documentation.
- L'entreprise ne dispose pas d'une procédure de validation après modification.
- Les sauvegardes et la continuité de service doivent être améliorées.
- Les performances du réseau doivent rester satisfaisantes lorsque plusieurs utilisateurs transfèrent des fichiers simultanément.

Votre mission consiste à concevoir une architecture répondant à ces besoins, à expliquer les choix réalisés et à démontrer que la solution fonctionne.

L'objectif n'est pas simplement de faire communiquer tous les équipements. Il faut déterminer **qui peut communiquer avec qui, par quel chemin, à quelles conditions et avec quelles preuves de validation**.

## 1.2. Périmètre fonctionnel

Le réseau doit permettre aux utilisateurs de :

- Accéder aux applications internes autorisées.
- Accéder à Internet selon leur profil.
- Utiliser les imprimantes prévues pour leur service.
- Participer aux réunions avec la téléphonie IP et les outils collaboratifs.
- Utiliser le Wi-Fi de l'entreprise avec une authentification appropriée.
- Accueillir des visiteurs sans leur donner accès aux ressources internes.
- Administrer les équipements réseau avec des accès strictement contrôlés.
- Résoudre les incidents à partir d'une méthode de diagnostic reproductible.

## 1.3. Hypothèses de travail

Pour rendre le challenge concret, retenez les hypothèses suivantes :

| Élément | Hypothèse |
|---|---|
| Utilisateurs | Environ 80 |
| Services | Direction, Finance/RH, Employés, Informatique |
| Équipements réseau | Commutateurs d'accès, commutateurs de cœur, pare-feu et points d'accès Wi-Fi |
| Serveurs | DNS, DHCP ou relais DHCP, applications, fichiers, supervision et sauvegarde |
| Téléphonie | Téléphones IP |
| Périphériques | Imprimantes réseau et objets connectés autorisés |
| Wi-Fi interne | Accès réservé aux utilisateurs et équipements autorisés |
| Wi-Fi visiteurs | Accès Internet uniquement |
| Adressage IPv4 privé | Réseau `10.20.0.0/16` |
| Administration | Segment réseau séparé |
| Sécurité | Segmentation, filtrage, journalisation et contrôle des accès |
| Disponibilité | Redondance ciblée sur les composants les plus critiques |

Ces valeurs constituent le scénario de l'exercice. Dans un projet réel, les besoins, les contraintes matérielles, les applications et les exigences réglementaires doivent être recueillis avant de figer l'architecture.


# 2. Objectifs pédagogiques

À la fin du challenge, vous devrez pouvoir :

1. Recueillir les besoins techniques et fonctionnels d'une entreprise.
2. Produire une architecture physique et une architecture logique.
3. Concevoir un plan de VLAN cohérent.
4. Construire un plan d'adressage IPv4 documenté.
5. Expliquer le fonctionnement des trames Ethernet et des paquets IP.
6. Configurer des VLAN et des trunks 802.1Q.
7. Choisir une architecture de routage inter-VLAN.
8. Comprendre le rôle de DHCP, DNS, NTP et du pare-feu.
9. Définir une politique de filtrage entre les différentes zones.
10. Concevoir un Wi-Fi professionnel et un Wi-Fi visiteurs correctement séparés.
11. Identifier les risques liés à STP, aux trunks, aux ACL et à l'administration.
12. Tester la connectivité sans se limiter à la commande `ping`.
13. Diagnostiquer des incidents à partir du modèle OSI.
14. Interpréter des captures de paquets avec Wireshark.
15. Préparer des tests de non-régression et un plan de retour arrière.
16. Documenter et présenter une architecture exploitable par une équipe informatique.


# 3. Organisation des niveaux

Le challenge suit une progression cumulative. Chaque niveau réutilise les éléments du précédent.

## Niveau 1 — Débutant : construire un réseau cohérent

Le participant doit :

- Comprendre le besoin de l'entreprise.
- Dessiner le réseau physique.
- Identifier les équipements.
- Créer les VLAN.
- Définir les sous-réseaux IPv4.
- Comprendre les passerelles par défaut.
- Tester les communications locales et inter-réseaux.
- Vérifier DHCP, DNS et l'accès Internet.

**Livrable :** une architecture fonctionnelle documentée.

## Niveau 2 — Intermédiaire : sécuriser et fiabiliser le réseau

Le participant doit :

- Définir les flux autorisés entre VLAN.
- Appliquer des ACL ou des politiques de filtrage.
- Contrôler les trunks et les VLAN autorisés.
- Séparer l'administration du réseau utilisateur.
- Isoler les visiteurs et les équipements IoT.
- Proposer une architecture Wi-Fi sécurisée.
- Mettre en place la supervision et la journalisation.
- Diagnostiquer des incidents combinant plusieurs couches OSI.

**Livrable :** une architecture sécurisée, accompagnée d'une matrice de flux et d'une stratégie de tests.

## Niveau 3 — Expert : concevoir pour la production

Le participant doit :

- Justifier le placement des passerelles et du pare-feu.
- Analyser les risques de panne.
- Définir les objectifs de disponibilité.
- Préparer les procédures de changement et de retour arrière.
- Analyser les performances et les éventuels problèmes de MTU.
- Étudier IPv6 et ses implications de sécurité.
- Valider la segmentation par des tests positifs et négatifs.
- Présenter une architecture cible argumentée.

**Livrable :** un dossier d'architecture, une politique de sécurité, un plan d'exploitation et un rapport de validation.


# 4. Défi 1 — Recueil des besoins et inventaire

Avant de configurer les équipements, vous devez comprendre ce que le réseau doit transporter et protéger.

## 4.1. Identifier les catégories d'équipements

L'inventaire initial peut être organisé comme suit :

| Catégorie | Exemple | Besoin principal |
|---|---|---|
| Direction | Ordinateurs portables | Applications internes et Internet |
| Finance/RH | Postes de travail | Applications sensibles |
| Employés | PC fixes et portables | Applications métier |
| Informatique | Postes d'administration | Gestion des systèmes et équipements |
| Serveurs | DNS, applications, fichiers | Services internes |
| Téléphonie | Téléphones IP | Appels et services de communication |
| Imprimantes | Imprimantes réseau | Impression contrôlée |
| IoT | Équipements autorisés | Communications limitées |
| Wi-Fi entreprise | PC et terminaux mobiles | Accès interne authentifié |
| Wi-Fi visiteurs | Smartphones et portables invités | Internet uniquement |
| Infrastructure | Commutateurs, pare-feu, points d'accès | Administration protégée |

## 4.2. Questions à poser avant la conception

Le concepteur doit obtenir des réponses précises aux questions suivantes :

- Combien d'utilisateurs sont présents simultanément ?
- Combien d'équipements doivent être raccordés au réseau ?
- Quelles applications sont indispensables à l'activité ?
- Quels utilisateurs accèdent aux applications financières et RH ?
- Les imprimantes sont-elles partagées entre services ?
- La téléphonie utilise-t-elle un VLAN dédié ?
- Les visiteurs ont-ils besoin d'un portail captif ?
- Les utilisateurs doivent-ils pouvoir travailler depuis plusieurs points d'accès Wi-Fi ?
- Quel niveau de disponibilité est exigé ?
- Quelle durée d'interruption est acceptable ?
- Quels équipements sont compatibles avec les fonctions de redondance prévues ?
- Où sont stockées les sauvegardes ?
- Quelles traces doivent être conservées ?
- Qui peut modifier la configuration du réseau ?
- Comment un changement est-il approuvé et annulé ?

## 4.3. Traduire les besoins en exigences vérifiables

Une exigence doit pouvoir être testée.

Exemples :

| Exigence | Test de validation |
|---|---|
| Un visiteur ne peut pas accéder aux serveurs internes | Tester les accès IP et applicatifs depuis le VLAN visiteurs |
| Un poste Finance accède à l'application financière | Tester le service et le port réellement utilisés |
| Un utilisateur reçoit la bonne adresse IP | Contrôler l'adresse, le masque, la passerelle et les DNS |
| Un administrateur peut gérer un commutateur | Tester SSH depuis un poste d'administration autorisé |
| Un poste invité ne peut pas administrer le pare-feu | Tester les ports d'administration depuis le VLAN visiteurs |
| Le DNS résout les noms attendus | Effectuer une requête DNS et vérifier la réponse |
| La téléphonie fonctionne | Contrôler l'enregistrement, la signalisation et le média |
| Les changements sont traçables | Vérifier les journaux et la documentation du changement |

**Règle de conception :** aucune exigence de sécurité ne doit être considérée comme validée uniquement parce que le trafic attendu fonctionne. Il faut également démontrer que le trafic interdit est bloqué.


# 5. Architecture 1 — Architecture physique de référence

Cette architecture sépare les rôles des équipements. Elle constitue une base professionnelle pour le scénario.

## 5.1. Schéma physique général

```text
                         INTERNET
                            |
                    +----------------+
                    | Fournisseur(s) |
                    +----------------+
                            |
                    +----------------+
                    | PARE-FEU       |
                    | NAT / VPN      |
                    | Filtrage WAN   |
                    +----------------+
                            |
                     Lien de transit
                            |
              +---------------------------+
              | CŒUR DE RÉSEAU L3         |
              | Routage inter-VLAN        |
              | ACL inter-zones           |
              | Passerelles des VLAN      |
              +---------------------------+
                    ||             ||
             Liens redondants     ||
                    ||             ||
           +----------------+  +----------------+
           | SWITCH ACCÈS 1 |  | SWITCH ACCÈS 2 |
           | Ports utilisateurs| | Ports utilisateurs|
           +----------------+  +----------------+
              |   |   |             |   |   |
              |   |   |             |   |   +---- Téléphones IP
              |   |   +---------------------- Imprimantes autorisées
              |   +-------------------------- Postes de travail
              +------------------------------ Points d'accès Wi-Fi

                            |
                  +---------------------+
                  | Réseau des serveurs |
                  | Applications        |
                  | DNS / DHCP / NTP    |
                  | Sauvegarde          |
                  +---------------------+
```

Le schéma montre les rôles logiques, et non un câblage exhaustif. Le raccordement physique exact des serveurs, la présence de liens redondants et l'organisation du cœur doivent être précisés dans le dossier final.

## 5.2. Rôle des composants

### Pare-feu

Le pare-feu protège la frontière entre le réseau de l'entreprise et les réseaux externes. Il peut notamment assurer :

- Le filtrage des connexions entrantes et sortantes.
- Le NAT pour l'accès IPv4 à Internet.
- La terminaison VPN.
- La journalisation des connexions.
- Des fonctions de filtrage applicatif, selon le produit.
- La détection ou la prévention d'intrusion, si ces fonctions sont disponibles et correctement configurées.

Le NAT n'est pas une politique de sécurité suffisante à lui seul. Les règles de filtrage doivent être conçues explicitement.

### Commutateur de cœur de réseau

Le cœur de réseau transporte le trafic entre les VLAN et vers le pare-feu.

Dans l'architecture de référence :

- Les interfaces VLAN, appelées SVI, sont configurées sur le cœur L3.
- Les passerelles par défaut des VLAN sont les adresses de ces interfaces.
- Les ACL du cœur limitent les communications inter-VLAN.
- Une route par défaut dirige le trafic externe vers le pare-feu.
- Les équipements d'accès transportent les VLAN nécessaires à leurs ports.

Les équipements doivent prendre en charge le routage L3, les ACL et les fonctions de résilience nécessaires.

### Commutateurs d'accès

Ils raccordent les terminaux :

- PC ;
- téléphones IP ;
- imprimantes ;
- points d'accès Wi-Fi ;
- autres appareils autorisés.

Les ports sont configurés selon le rôle du terminal. Un port utilisateur ordinaire ne doit pas devenir un trunk sans besoin justifié.

### Points d'accès Wi-Fi

Ils fournissent le service sans-fil. Selon leur mode de fonctionnement, les VLAN peuvent être transportés par des trunks vers les commutateurs d'accès, ou les SSID peuvent être raccordés à des zones réseau définies par une architecture centralisée.

### Serveurs

Les serveurs fournissent les services métier et d'infrastructure. Leurs adresses sont généralement réservées dans le plan IP et documentées.


# 6. Architecture 2 — Architecture logique et segmentation

L'architecture logique décrit les zones réseau, les VLAN et les règles qui gouvernent les communications, indépendamment de l'emplacement physique des équipements.

## 6.1. Schéma logique des zones

```text
                         INTERNET
                            |
                       [ PARE-FEU ]
                            |
                    [ CŒUR L3 / ACL ]
                            |
        +-------------------+--------------------+
        |                   |                    |
   VLAN 10              VLAN 20              VLAN 30
   ADMINISTRATION       FINANCE / RH         EMPLOYÉS
        |                   |                    |
  Postes admin          Postes sensibles      Postes standard
        |
   VLAN 90
   GESTION INFRASTRUCTURE
        |
  SSH / SNMPv3 / Syslog
  vers les équipements

        +-------------------+--------------------+
        |                   |                    |
   VLAN 40              VLAN 50              VLAN 60
   SERVEURS             VOIX IP              IMPRIMANTES / IoT
        |                   |                    |
  DNS / applications    Téléphones IP         Périphériques isolés
  NTP / sauvegardes

        +-------------------+--------------------+
        |                                        |
   VLAN 70                                  VLAN 80
   WI-FI VISITEURS                           WI-FI ENTREPRISE
        |                                        |
  Internet uniquement                     Accès selon l'identité
  Aucun accès interne                     et les règles autorisées

                   VLAN 999
           VLAN de parking / native
          Aucun usage utilisateur prévu
```

Le VLAN 90 est ajouté pour distinguer le réseau d'administration des postes bureautiques ordinaires. Le VLAN 10 représente les postes des personnes autorisées à effectuer des tâches d'administration. Le VLAN 90 héberge les interfaces de gestion des équipements.

Cette distinction évite de considérer qu'un ordinateur de bureau devient automatiquement une station d'administration sécurisée.

## 6.2. Pourquoi segmenter le réseau ?

La segmentation sert à réduire les domaines de diffusion et à limiter les communications inutiles ou dangereuses.

Sans segmentation, un poste compromis pourrait disposer d'une visibilité importante sur les équipements voisins et tenter de joindre des services sensibles.

Avec une segmentation adaptée :

- Un visiteur n'accède pas directement aux serveurs internes.
- Une imprimante ne peut pas initier librement des connexions vers les postes.
- Les postes utilisateurs n'administrent pas les commutateurs.
- Les serveurs sensibles ne sont accessibles que sur les flux nécessaires.
- Les règles de filtrage sont compréhensibles et testables.
- Une anomalie dans une zone peut être investiguée plus facilement.

Attention : **un VLAN n'est pas à lui seul une frontière de sécurité complète**. Le routage entre VLAN doit être accompagné de règles de filtrage adaptées, et les équipements de couche 2 doivent être configurés correctement.


# 7. Défi 2 — Plan de VLAN

## 7.1. Plan de référence

Le plan suivant sert de base commune pour les exercices.

| VLAN | Nom | Usage | Exemple de terminaux |
|---:|---|---|---|
| 10 | ADMIN | Postes d'administration autorisés | Stations d'administration |
| 20 | FINANCE-RH | Données et applications sensibles | Postes Finance et RH |
| 30 | EMPLOYES | Utilisateurs bureautiques | PC fixes et portables |
| 40 | SERVEURS | Services internes | DNS, applications, fichiers |
| 50 | VOIP | Téléphonie IP | Téléphones |
| 60 | IMPRIMANTES-IOT | Périphériques réseau limités | Imprimantes, IoT autorisés |
| 70 | WIFI-INVITES | Accès invités | Téléphones et portables visiteurs |
| 80 | WIFI-CORPORATE | Wi-Fi de l'entreprise | Terminaux d'entreprise |
| 90 | MGMT-INFRA | Gestion des équipements | Interfaces de gestion |
| 999 | PARKING-NATIVE | VLAN inutilisé pour les terminaux | Aucun terminal utilisateur |

Les identifiants sont des choix d'organisation. Ils ne sont pas des valeurs universelles imposées par Ethernet ou 802.1Q.

## 7.2. Principes d'affectation

Un port d'accès doit être associé au VLAN correspondant à sa fonction.

Exemples :

- Un PC Finance rejoint le VLAN 20.
- Un poste d'administration autorisé rejoint le VLAN 10.
- Un téléphone IP rejoint le VLAN 50.
- Une imprimante rejoint le VLAN 60.
- Un point d'accès reçoit les VLAN dont il a besoin pour transporter les SSID.
- Un port inutilisé est désactivé et placé dans une configuration de parking adaptée.
- Un équipement de gestion n'est pas raccordé au VLAN visiteurs.

Les ports qui transportent plusieurs VLAN doivent être configurés comme trunks lorsque le matériel et la topologie le nécessitent.

## 7.3. Exemple de port utilisateur

Exemple de configuration Cisco IOS pour un port access dédié à un poste utilisateur du VLAN 30 :

```text
interface GigabitEthernet1/0/10
 description POSTE-UTILISATEUR-30
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 spanning-tree bpduguard enable
```

Cette configuration suppose que le commutateur utilise la syntaxe IOS correspondante et que PortFast est activé uniquement sur un port destiné à un terminal final.

N'appliquez pas automatiquement cette configuration à un lien entre commutateurs, à un trunk ou à un port dont le rôle est inconnu.

### Vérifications

```text
show vlan brief
show interfaces status
show interfaces GigabitEthernet1/0/10 switchport
show spanning-tree interface GigabitEthernet1/0/10
```

À démontrer :

1. Le port appartient au VLAN prévu.
2. Le mode est bien `access`.
3. Le terminal reçoit le bon sous-réseau.
4. Le port n'a pas été configuré comme trunk.
5. Les protections prévues fonctionnent sans bloquer un équipement légitime.

## 7.4. Trunks 802.1Q

Un trunk transporte plusieurs VLAN sur un même lien physique. Le protocole IEEE 802.1Q permet notamment d'identifier le VLAN associé à une trame Ethernet.

Exemple conceptuel :

```text
VLAN 20 ----\
VLAN 30 -----+---- [ TRUNK 802.1Q ] ---- [ COMMUTATEUR ]
VLAN 40 -----+
VLAN 50 ----/
```

Le trunk ne signifie pas que tous les VLAN doivent être autorisés sur le lien.

Exemple Cisco IOS :

```text
interface GigabitEthernet1/0/48
 description TRUNK-VERS-COEUR
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80,90,999
```

Cette liste n'est qu'un exemple. En production, le trunk doit transporter uniquement les VLAN nécessaires sur ce lien.

Selon la plateforme, la configuration du VLAN natif et certaines commandes peuvent différer.

### Contrôles indispensables

```text
show interfaces trunk
show interfaces GigabitEthernet1/0/48 switchport
show vlan brief
show spanning-tree
```

Vérifiez :

- Les VLAN autorisés.
- Les VLAN réellement actifs sur le trunk.
- Le VLAN natif.
- La cohérence avec le commutateur voisin.
- L'état STP.
- L'absence de VLAN inutilement transporté.

Un trunk configuré avec une liste trop large peut exposer des VLAN sur des liens qui n'en ont pas besoin.

## 7.5. VLAN de parking

Les ports inutilisés ne doivent pas rester inutilement disponibles pour un raccordement non autorisé.

Exemple conceptuel :

```text
interface range GigabitEthernet1/0/20-24
 description PORTS-INUTILISES
 switchport mode access
 switchport access vlan 999
 shutdown
```

Le VLAN 999 est utilisé dans cet exercice comme VLAN sans usage utilisateur prévu. Il faut aussi éviter de le transporter sur les trunks si cela n'est pas nécessaire.

Le VLAN natif et le VLAN de parking sont deux concepts qu'il faut distinguer dans la documentation. Le fait d'utiliser un VLAN numérique élevé ne le rend pas automatiquement sûr.


# 8. Défi 3 — Plan d'adressage IPv4

## 8.1. Règles de conception

Le plan IP doit être :

- Unique au sein de l'environnement concerné.
- Cohérent avec les VLAN.
- Documenté.
- Facile à résumer et à dépanner.
- Adapté au nombre d'hôtes, avec une marge de croissance.
- Compatible avec les routes, ACL, DHCP et systèmes de supervision.

Pour cet exercice, chaque zone principale reçoit un sous-réseau IPv4 `/24`. Cette stratégie simplifie les calculs pédagogiques, mais elle n'est pas nécessairement la plus efficace pour tous les réseaux de production.

Un `/24` contient 256 adresses IPv4 au total, généralement 254 adresses hôtes utilisables dans le modèle usuel des réseaux Ethernet IPv4.

## 8.2. Plan IP de référence

| VLAN | Réseau | Passerelle | Attribution indicative |
|---:|---|---|---|
| 10 | `10.20.10.0/24` | `10.20.10.1` | Postes d'administration |
| 20 | `10.20.20.0/24` | `10.20.20.1` | Finance et RH |
| 30 | `10.20.30.0/24` | `10.20.30.1` | Employés |
| 40 | `10.20.40.0/24` | `10.20.40.1` | Serveurs |
| 50 | `10.20.50.0/24` | `10.20.50.1` | Téléphones IP |
| 60 | `10.20.60.0/24` | `10.20.60.1` | Imprimantes et IoT autorisés |
| 70 | `10.20.70.0/24` | `10.20.70.1` | Wi-Fi visiteurs |
| 80 | `10.20.80.0/24` | `10.20.80.1` | Wi-Fi corporate |
| 90 | `10.20.90.0/24` | `10.20.90.1` | Gestion des infrastructures |

Les adresses présentées sont des adresses privées destinées à l'exercice. Le réseau réel devra être contrôlé pour éviter les chevauchements avec les réseaux existants, les VPN et les environnements connectés.

## 8.3. Attribution des adresses

Une convention de départ peut être appliquée dans chaque sous-réseau :

| Plage indicative | Usage |
|---|---|
| `.1` | Passerelle du VLAN |
| `.2` à `.9` | Équipements réseau ou services réservés, selon les besoins |
| `.10` à `.49` | Serveurs ou équipements à adresse réservée |
| `.50` à `.99` | Équipements réservés, imprimantes ou appareils particuliers |
| `.100` à `.239` | Plage DHCP indicative pour les postes |
| `.240` à `.254` | Réserve d'adresses à documenter |

Ces plages ne sont pas des normes. Elles doivent être adaptées au nombre d'équipements et aux besoins de chaque VLAN.

Une adresse réservée peut être attribuée par DHCP ou configurée statiquement. Les deux méthodes doivent être documentées pour éviter les conflits.

## 8.4. Exemple de réseau serveur

Le VLAN 40 contient notamment :

| Adresse d'exemple | Fonction |
|---|---|
| `10.20.40.10` | DNS interne principal |
| `10.20.40.11` | DNS interne secondaire, si disponible |
| `10.20.40.20` | Serveur d'applications |
| `10.20.40.30` | Serveur de fichiers |
| `10.20.40.40` | Serveur de supervision ou de journaux, selon le déploiement |

Ces adresses sont des valeurs pédagogiques. Elles ne signifient pas que chaque fonction doit obligatoirement être installée sur un serveur distinct.

La séparation des rôles dépend de la taille de l'organisation, des contraintes de sécurité, de la disponibilité et des ressources matérielles.

## 8.5. Exercice de calcul de sous-réseau

Un poste reçoit la configuration suivante :

```text
Adresse IP :       10.20.30.25
Masque :           255.255.255.0
Passerelle :       10.20.30.1
DNS :              10.20.40.10
```

Questions :

1. Quel est le réseau du poste ?
2. Quelle est son adresse de diffusion IPv4 ?
3. Quelle plage d'adresses hôtes est utilisable dans ce sous-réseau ?
4. Le poste peut-il communiquer directement avec `10.20.30.70` ?
5. Le poste peut-il communiquer directement avec `10.20.40.20` sans passer par un équipement de couche 3 ?
6. Pourquoi doit-il disposer d'une passerelle par défaut ?
7. La présence de l'adresse DNS dans le VLAN 40 garantit-elle que le poste peut l'interroger ?

### Correction attendue

- Réseau : `10.20.30.0/24`.
- Diffusion IPv4 : `10.20.30.255`.
- Plage d'hôtes usuelle : `10.20.30.1` à `10.20.30.254`.
- `10.20.30.70` appartient au même sous-réseau.
- `10.20.40.20` appartient à un autre sous-réseau : une fonction de routage est nécessaire pour l'atteindre.
- La passerelle sert à envoyer les paquets destinés à d'autres réseaux.
- La présence d'une adresse DNS dans la configuration ne prouve pas que le service est joignable, autorisé et fonctionnel.

Le diagnostic doit vérifier l'adresse, le routage, les ACL, le service DNS et le chemin de retour.


# 9. Défi 4 — Architecture de routage inter-VLAN

Les VLAN séparent les domaines de couche 2. Les communications IP entre des sous-réseaux différents nécessitent une fonction de routage.

## 9.1. Architecture retenue pour le challenge

Dans l'architecture de référence :

- Les passerelles des VLAN sont hébergées sur le cœur L3.
- Le cœur effectue le routage inter-VLAN.
- Les ACL du cœur limitent les communications internes.
- Une route par défaut conduit au pare-feu.
- Le pare-feu contrôle les flux entre le réseau de l'entreprise et les réseaux externes.

Schéma :

```text
                    VLAN 20 - FINANCE
                            |
                     [ SVI 10.20.20.1 ]
                            |
                            v
                    +------------------+
                    | CŒUR L3          |
                    | Routage IP       |
                    | ACL inter-VLAN   |
                    +------------------+
                            |
                     Route par défaut
                            |
                            v
                    +------------------+
                    | PARE-FEU         |
                    | Filtrage WAN     |
                    | NAT / VPN        |
                    +------------------+
                            |
                         INTERNET
```

Cette architecture peut être performante, mais elle exige des ACL bien conçues. Le trafic entre deux VLAN routés sur le cœur ne traverse pas automatiquement le pare-feu WAN.

**Ne considérez jamais qu'une politique sur le pare-feu Internet protège implicitement tous les flux entre les VLAN.**

## 9.2. Exemple conceptuel de SVI

La configuration suivante illustre des interfaces VLAN sur un équipement Cisco IOS L3. Les commandes exactes dépendent de la plateforme, de sa version logicielle et de ses capacités.

```text
ip routing

interface Vlan20
 description PASSERELLE-FINANCE-RH
 ip address 10.20.20.1 255.255.255.0
 no shutdown

interface Vlan30
 description PASSERELLE-EMPLOYES
 ip address 10.20.30.1 255.255.255.0
 no shutdown

interface Vlan40
 description PASSERELLE-SERVEURS
 ip address 10.20.40.1 255.255.255.0
 no shutdown
```

Les VLAN correspondants doivent exister et être actifs. Les trunks doivent transporter les VLAN nécessaires et un lien actif doit permettre aux SVI de monter selon le fonctionnement de la plateforme.

### Contrôles

```text
show ip interface brief
show ip route
show vlan brief
show interfaces trunk
show running-config
```

## 9.3. Route par défaut vers le pare-feu

Exemple conceptuel :

```text
ip route 0.0.0.0 0.0.0.0 <IP_DU_PARE_FEU_SUR_LE_RESEAU_DE_TRANSIT>
```

La valeur entre chevrons est un espace réservé à remplacer par l'adresse réelle du prochain saut.

Ne copiez pas cette ligne telle quelle dans un équipement de production sans définir le réseau de transit, les routes de retour, les règles de filtrage et les exigences de résilience.

Le pare-feu doit savoir comment renvoyer le trafic vers les sous-réseaux internes. Cette information peut être fournie par des routes statiques ou un mécanisme de routage convenablement conçu.

## 9.4. Variante : pare-feu comme passerelle inter-VLAN

Une autre architecture consiste à faire terminer les VLAN sur le pare-feu, qui assure directement le routage inter-VLAN et le filtrage.

```text
 VLAN 20 ----\
 VLAN 30 -----+--- TRUNK --- [ PARE-FEU / SOUS-INTERFACES ]
 VLAN 40 -----+                         |
 VLAN 70 ----/                         INTERNET
```

Cette variante permet de centraliser davantage l'application des politiques au pare-feu. Elle peut toutefois imposer des contraintes de débit, de capacité de traitement et de disponibilité.

Le choix entre cœur L3 et pare-feu comme passerelle doit tenir compte :

- Du débit inter-VLAN attendu.
- De la capacité réelle du pare-feu.
- Des besoins d'inspection des flux.
- Du nombre de VLAN.
- Des besoins de haute disponibilité.
- De la complexité opérationnelle.
- Des limites des équipements disponibles.

Il n'existe pas de solution universellement meilleure : il faut choisir une architecture adaptée, puis démontrer que les règles de sécurité sont réellement appliquées.


# 10. Défi 5 — DHCP, DNS et NTP

## 10.1. DHCP

DHCP permet aux clients d'obtenir automatiquement une configuration IP comprenant généralement :

- Une adresse IPv4.
- Un masque de sous-réseau.
- Une passerelle par défaut.
- Un ou plusieurs serveurs DNS.
- Une durée de bail.
- D'autres options nécessaires aux terminaux selon le contexte.

Pour chaque VLAN utilisateur, le plan de DHCP doit indiquer :

- Le réseau concerné.
- La plage attribuable.
- Les exclusions.
- La passerelle.
- Les DNS.
- La durée du bail.
- Les réservations.
- Le serveur DHCP responsable.

### Exemple de fiche DHCP

| Paramètre | VLAN 30 — Employés |
|---|---|
| Réseau | `10.20.30.0/24` |
| Passerelle | `10.20.30.1` |
| Plage indicative | `10.20.30.100` à `10.20.30.239` |
| DNS interne | `10.20.40.10` |
| Attribution | DHCP |
| Réservations | Selon les besoins documentés |

Les équipements disposant d'une réservation ou d'une adresse statique ne doivent pas entrer en conflit avec la plage DHCP.

### DHCP relay

Lorsque le serveur DHCP et le client appartiennent à des sous-réseaux distincts, les requêtes DHCP de diffusion ne traversent normalement pas directement un routeur. Une fonction de relais DHCP peut être nécessaire sur la passerelle.

Exemple conceptuel sur Cisco IOS :

```text
interface Vlan30
 ip address 10.20.30.1 255.255.255.0
 ip helper-address 10.20.40.15
```

`10.20.40.15` est ici une adresse illustrative du serveur DHCP. Elle doit être remplacée par l'adresse réelle du service.

Le relais ne remplace pas les contrôles de routage et de filtrage. Le serveur doit aussi disposer d'une étendue DHCP correspondant au réseau du client.

### Vérifications côté client

Sous Windows :

```powershell
ipconfig /all
ipconfig /release
ipconfig /renew
```

Sous Linux :

```bash
ip addr
ip route
resolvectl status
```

Les commandes de renouvellement dépendent du système et du gestionnaire réseau employé.

## 10.2. DNS

Le DNS associe les noms aux informations de résolution, notamment les adresses IP.

Une connexion peut échouer même lorsque l'adresse IP du service est correcte si la résolution DNS est incorrecte ou bloquée.

Exemples de tests :

```bash
nslookup application.interne.example
```

ou :

```bash
dig application.interne.example
```

Les noms illustratifs doivent être remplacés par les noms réellement configurés dans le domaine de l'entreprise.

À vérifier :

- Le client interroge-t-il le DNS prévu ?
- Le serveur DNS est-il joignable ?
- Le port et le protocole DNS sont-ils autorisés ?
- La zone contient-elle l'enregistrement attendu ?
- La réponse correspond-elle au bon service ?
- Le client utilise-t-il une réponse en cache devenue obsolète ?
- Une règle de sécurité empêche-t-elle la résolution ?

DNS utilise habituellement UDP 53 pour les requêtes courantes, mais TCP 53 est également nécessaire dans certains cas, notamment pour certaines réponses volumineuses et des opérations de transfert de zone. Les règles doivent refléter les besoins réels plutôt que présumer qu'UDP suffit toujours.

## 10.3. NTP

NTP synchronise l'heure des systèmes. Une heure incorrecte peut perturber :

- Les certificats TLS.
- Les journaux.
- L'authentification.
- La corrélation des incidents.
- Les événements de sécurité.

La politique doit définir les serveurs de temps autorisés et les équipements qui peuvent les interroger.

N'exposez pas inutilement l'administration du serveur de temps ou son service à tous les segments.

## 10.4. Test global des services de base

Pour un poste du VLAN 30, validez successivement :

1. L'adresse IP et le masque sont cohérents.
2. La passerelle locale répond lorsque ce test est applicable.
3. Les routes permettent de rejoindre le serveur DHCP, directement ou par relais.
4. Le client dispose de la bonne adresse DNS.
5. Une requête DNS retourne une réponse attendue.
6. L'heure du poste est cohérente.
7. Les applications sont joignables selon les règles prévues.

Une configuration IP correcte ne prouve pas que l'application métier est fonctionnelle.


# 11. Défi 6 — Matrice de sécurité inter-VLAN

La segmentation devient réellement utile lorsque les communications sont définies.

## 11.1. Principe général

Adoptez une politique de départ fondée sur les principes suivants :

1. Autoriser seulement les flux nécessaires.
2. Refuser les autres flux inter-zones par défaut.
3. Documenter les exceptions.
4. Limiter les accès d'administration à des sources dédiées.
5. N'autoriser les connexions vers les serveurs que sur les services nécessaires.
6. Journaliser les refus ou les événements importants selon les capacités disponibles.
7. Tester les communications légitimes et interdites.

La politique finale dépend des applications réelles. La matrice suivante donne un modèle de travail et non une liste complète de règles prêtes à déployer.

## 11.2. Matrice de référence

Légende :

- **Autorisé sous condition** : le flux est permis uniquement pour les services et destinations explicitement nécessaires.
- **Refusé par défaut** : le flux est bloqué sauf exception documentée.
- **Administratif** : accès permis uniquement depuis un poste ou une zone d'administration autorisée.

| Source | Destination | Politique de référence | Justification |
|---|---|---|---|
| VLAN 10 ADMIN | VLAN 90 MGMT-INFRA | Administratif | Gestion des équipements |
| VLAN 10 ADMIN | VLAN 40 SERVEURS | Autorisé sous condition | Administration de serveurs autorisés |
| VLAN 20 FINANCE-RH | VLAN 40 SERVEURS | Autorisé sous condition | Applications Finance/RH nécessaires |
| VLAN 30 EMPLOYES | VLAN 40 SERVEURS | Autorisé sous condition | Applications métier autorisées |
| VLAN 30 EMPLOYES | VLAN 20 FINANCE-RH | Refusé par défaut | Séparation des services |
| VLAN 50 VOIP | VLAN 40 SERVEURS | Autorisé sous condition | Téléphonie, provisioning ou services nécessaires |
| VLAN 60 IMPRIMANTES-IOT | VLAN 30 EMPLOYES | Refusé par défaut | Éviter les connexions initiées par les périphériques |
| VLAN 30 EMPLOYES | VLAN 60 IMPRIMANTES-IOT | Autorisé sous condition | Impression vers les périphériques autorisés |
| VLAN 70 WIFI-INVITES | Réseaux internes | Refusé | Isolement des invités |
| VLAN 70 WIFI-INVITES | Internet | Autorisé sous condition | Accès web selon la politique de l'entreprise |
| VLAN 80 WIFI-CORPORATE | VLAN 40 SERVEURS | Autorisé sous condition | Services internes nécessaires |
| VLAN 80 WIFI-CORPORATE | VLAN 90 MGMT-INFRA | Refusé par défaut | Protéger l'administration |
| VLAN 30 EMPLOYES | VLAN 90 MGMT-INFRA | Refusé | Éviter l'administration depuis les postes standards |
| Réseaux utilisateurs | Services DNS autorisés | Autorisé | Résolution des noms |
| Réseaux utilisateurs | Services DHCP nécessaires | Autorisé selon l'architecture | Attribution de configuration IP |
| Réseaux autorisés | Serveurs NTP approuvés | Autorisé | Synchronisation de l'heure |
| Réseaux non autorisés | Équipements réseau | Refusé par défaut | Réduction de la surface d'attaque |

## 11.3. Clarifier les règles applicatives

Une ligne de matrice doit progressivement être détaillée avec les champs suivants :

| Champ | Exemple |
|---|---|
| Identifiant de règle | `ACL-APP-010` |
| Source | `10.20.30.0/24` |
| Destination | Adresse du serveur d'application |
| Protocole | TCP |
| Port destination | Port réellement requis par l'application |
| Action | Autoriser |
| Journalisation | Selon le besoin de suivi |
| Responsable | Équipe applicative |
| Justification | Accès à l'application métier |
| Date de révision | Date définie dans le processus d'exploitation |

Ne choisissez pas arbitrairement les ports d'une application inconnue. Consultez la documentation du service et observez les flux nécessaires dans un environnement autorisé.

## 11.4. Règles de sécurité du VLAN invités

Le Wi-Fi invités ne doit pas atteindre les ressources internes.

Les contrôles devraient couvrir :

- Les sous-réseaux IPv4 privés de l'entreprise.
- Les réseaux de gestion.
- Les interfaces d'administration.
- Les services internes accessibles par des chemins alternatifs.
- Les routes IPv6, si IPv6 est activé.
- Les mécanismes d'accès aux autres appareils présents sur le même réseau invité.

Le filtrage du réseau invité doit être appliqué au bon endroit : passerelle, pare-feu, contrôleur WLAN, mécanisme d'isolation des clients ou combinaison de ces mécanismes.

**Une règle IPv4 seule n'isole pas les clients si un chemin IPv6 reste ouvert et non contrôlé.**

## 11.5. Principe de vérification

Pour chaque règle, prévoyez au minimum deux tests :

- Un test positif : le service autorisé fonctionne.
- Un test négatif : une communication interdite échoue.

Un refus n'est considéré comme probant que si l'on a confirmé que le test visait la bonne destination, le bon protocole et le bon port. Un service arrêté peut donner le même résultat apparent qu'une règle de filtrage.


# 12. Défi 7 — Architecture Wi-Fi

## 12.1. SSID proposés

La conception de référence prévoit deux SSID principaux :

| SSID | Usage | VLAN associé dans l'exercice |
|---|---|---:|
| `NOVATECH-CORP` | Utilisateurs d'entreprise authentifiés | 80 |
| `NOVATECH-GUEST` | Visiteurs | 70 |

En production, les SSID doivent être limités à ceux qui sont nécessaires. Un trop grand nombre de SSID peut augmenter la complexité d'exploitation et le temps d'occupation radio.

## 12.2. Wi-Fi entreprise

Le Wi-Fi interne doit authentifier les utilisateurs et les terminaux conformément aux moyens disponibles.

Pour une architecture d'entreprise, une méthode fondée sur 802.1X et un serveur d'authentification, telle que RADIUS, peut être adaptée. Une méthode EAP avec certificats peut améliorer la robustesse lorsqu'elle est correctement déployée et administrée.

La conception doit préciser :

- Les méthodes d'authentification utilisées.
- Les exigences de certificats, lorsqu'elles s'appliquent.
- Le renouvellement et la révocation des identifiants.
- Le mode d'affectation du VLAN.
- La stratégie de mobilité entre les points d'accès.
- Les journaux d'authentification.
- Le traitement des terminaux personnels, s'ils sont autorisés.

Un mot de passe partagé entre tous les collaborateurs peut être moins adapté à un environnement où les départs, les pertes d'équipement et les différences de privilèges doivent être gérés individuellement.

## 12.3. Wi-Fi visiteurs

Le Wi-Fi invités doit être séparé des zones de travail.

Politique minimale :

- Autoriser l'attribution d'adresses IP.
- Autoriser les résolveurs DNS prévus.
- Autoriser l'accès Internet conforme à la politique.
- Bloquer l'accès aux réseaux internes.
- Bloquer les interfaces de gestion.
- Activer l'isolation entre clients lorsque le dispositif le permet et que le besoin le justifie.
- Éviter l'accès aux services d'administration des points d'accès.
- Journaliser les événements utiles sans collecter plus de données que nécessaire.

Si un portail captif est mis en place, le flux nécessaire à sa présentation et à son fonctionnement doit être pris en compte dans la politique de filtrage.

## 12.4. Architecture Wi-Fi logique

```text
                     POINTS D'ACCÈS
                            |
                     TRUNK 802.1Q
                            |
                     SWITCH D'ACCÈS
                            |
               +------------+------------+
               |                         |
        SSID ENTREPRISE            SSID INVITÉS
               |                         |
           VLAN 80                  VLAN 70
               |                         |
      Cœur L3 + ACL               Cœur L3 + ACL
               |                         |
       Services autorisés             Pare-feu
                                         |
                                      INTERNET

          VLAN de gestion des points d'accès
                 séparé des SSID
```

Le VLAN de gestion des points d'accès doit être défini selon la plateforme. Il peut s'agir du VLAN 90 dans ce scénario lorsque cette option est adaptée au produit.

Les terminaux sans fil ne doivent pas pouvoir administrer les points d'accès simplement parce qu'ils utilisent le même équipement radio.

## 12.5. Tests Wi-Fi

Les tests doivent inclure :

1. Authentification d'un utilisateur autorisé.
2. Rejet d'un utilisateur non autorisé.
3. Obtention d'une adresse du bon sous-réseau.
4. Accès aux ressources internes prévues.
5. Refus d'accès aux ressources interdites.
6. Accès Internet pour les invités.
7. Isolation des visiteurs selon la politique.
8. Mobilité lors du passage entre les points d'accès.
9. Vérification du roaming et des journaux en cas de coupure.
10. Vérification de la couverture et des interférences.

Un signal radio élevé ne garantit pas que l'authentification, le routage ou l'application fonctionne.


# 13. Défi 8 — Résilience et haute disponibilité

## 13.1. Identifier les points de défaillance

Dans une architecture simple, plusieurs composants peuvent provoquer une interruption générale :

- Un unique pare-feu.
- Un unique commutateur de cœur.
- Un unique lien vers le cœur.
- Un seul fournisseur d'accès Internet.
- Un serveur DHCP ou DNS sans solution de reprise.
- Une alimentation électrique commune.
- Un système de sauvegarde qui ne peut pas être restauré.

Il faut distinguer la redondance d'un équipement de la résilience de bout en bout. Deux commutateurs n'apportent pas une disponibilité réelle si tous les services dépendent encore d'un point de panne commun.

## 13.2. Architecture cible avec redondance

Le schéma suivant illustre une cible plus résiliente. Les fonctions précises dépendent du matériel disponible et des mécanismes pris en charge.

```text
                   +-------------------+
                   | INTERNET / WAN A  |
                   +-------------------+
                            |
                   +-------------------+
                   | PARE-FEU A        |
                   +-------------------+
                            |
                    Mécanisme HA prévu
                            |
                   +-------------------+
                   | PARE-FEU B        |
                   +-------------------+
                            |
                 +-----------------------+
                 | CŒUR L3 REDONDANT     |
                 | Stack / MLAG / autre  |
                 | mécanisme supporté    |
                 +-----------------------+
                     ||             ||
                     ||             ||
             +---------------+  +---------------+
             | SWITCH ACCÈS A|  | SWITCH ACCÈS B|
             +---------------+  +---------------+
                    |                   |
              Utilisateurs         Utilisateurs
              et Wi-Fi             et Wi-Fi
```

Cette représentation montre des rôles et une intention de redondance. Les mécanismes de haute disponibilité ne sont pas interchangeables : ils doivent être conçus en tenant compte des modèles d'équipements, de la topologie, du routage, de STP, des liens et des dépendances de configuration.

## 13.3. Objectifs de disponibilité

Le dossier final doit fixer des objectifs réalistes :

- Temps maximal d'interruption acceptable.
- Délai de détection d'une panne.
- Délai de rétablissement.
- Tolérance à la perte d'un équipement ou d'un lien.
- Conditions de bascule.
- Possibilité de retour à l'état nominal.
- Tests planifiés et responsables.

N'affirmez pas qu'une architecture est « haute disponibilité » uniquement parce qu'elle contient deux équipements du même type.

## 13.4. Plan de continuité

Une procédure de reprise doit préciser :

1. Le défaut attendu.
2. La façon de le détecter.
3. Les services affectés.
4. La bascule prévue.
5. Les vérifications après bascule.
6. La méthode de retour à l'état normal.
7. Les risques de divergence de configuration.
8. La personne autorisée à réaliser l'opération.
9. Les éléments à consigner dans le journal d'incident.

Un test de bascule doit se dérouler dans un cadre autorisé, avec une fenêtre de maintenance et un plan de retour arrière.


# 14. Défi 9 — Administration sécurisée

## 14.1. Séparer le plan de gestion

L'administration du réseau ne doit pas être disponible indistinctement depuis tous les postes.

Dans ce scénario :

- Le VLAN 10 contient les stations d'administration autorisées.
- Le VLAN 90 contient les interfaces de gestion des équipements.
- Les accès aux interfaces de gestion sont autorisés uniquement depuis les sources prévues.
- Les protocoles d'administration obsolètes ou inutiles sont désactivés.
- Les journaux sont centralisés lorsque les moyens le permettent.

## 14.2. Bonnes pratiques

Privilégiez :

- SSH pour l'administration en ligne de commande.
- HTTPS avec des certificats adaptés pour les interfaces Web.
- SNMPv3 lorsque la supervision SNMP est requise.
- Des identifiants individuels et des rôles adaptés.
- L'authentification centralisée si elle est disponible et maîtrisée.
- Le stockage protégé des secrets.
- La journalisation des connexions et des changements.
- La sauvegarde des configurations.
- Le contrôle de l'accès physique aux équipements.

Évitez Telnet et les services d'administration en clair lorsqu'une alternative sécurisée est disponible.

## 14.3. Exemple conceptuel de contrôle

```text
Source autorisée :
  Poste d'administration enregistré

Destination :
  Interface de gestion du commutateur

Service :
  SSH

Action :
  Autoriser

Autres sources :
  Refuser
```

Cette règle doit être appliquée au bon point de contrôle. Créer un VLAN de gestion sans en restreindre l'accès n'est pas suffisant.

## 14.4. Sauvegardes de configuration

Une sauvegarde ne doit pas être considérée comme valide simplement parce qu'un fichier a été créé.

La procédure doit vérifier :

- Que la sauvegarde correspond au bon équipement.
- Qu'elle est datée.
- Qu'elle n'est pas vide ou tronquée.
- Qu'elle est stockée dans un emplacement protégé.
- Qu'une restauration est possible.
- Que les secrets contenus dans les configurations sont traités de manière sécurisée.
- Que l'accès au dépôt est limité.


# 15. Défi 10 — Dépannage par couches OSI

Un bon dépannage commence par une observation et une hypothèse. Il ne consiste pas à modifier simultanément plusieurs paramètres jusqu'à ce que le problème disparaisse.

Le modèle OSI aide à organiser les investigations.

| Couche | Nom | Exemples de vérification |
|---:|---|---|
| 7 | Application | Service disponible, réponse applicative, authentification |
| 6 | Présentation | Encodage, chiffrement, négociation TLS |
| 5 | Session | État et maintien de la session |
| 4 | Transport | TCP/UDP, ports, établissement de connexion |
| 3 | Réseau | IP, masque, passerelle, routage, ACL |
| 2 | Liaison | VLAN, MAC, trunk, STP, ARP |
| 1 | Physique | Câble, fibre, alimentation, lien, signal radio |

Le modèle n'impose pas toujours un ordre unique. Dans la pratique, on peut commencer par la couche où se manifeste le symptôme, puis examiner les dépendances.

## 15.1. Méthode de diagnostic en dix étapes

1. **Décrire le symptôme.** Qui est affecté, depuis quand et pour quelle destination ?
2. **Définir le résultat attendu.** Quel service, protocole et port devraient fonctionner ?
3. **Établir un état de référence.** Le service fonctionnait-il auparavant ? Qu'est-ce qui a changé ?
4. **Vérifier le physique.** Lien actif, câble, puissance et erreurs.
5. **Vérifier la couche 2.** VLAN, MAC, trunk et STP.
6. **Vérifier l'adressage.** IP, masque, passerelle et DNS.
7. **Vérifier le routage et le filtrage.** Routes, ACL, pare-feu et chemin de retour.
8. **Vérifier le transport.** Port TCP/UDP et établissement de connexion.
9. **Vérifier l'application.** Logs, certificat, authentification et état du service.
10. **Reproduire, corriger et valider.** Un changement à la fois, puis tests positifs et négatifs.

Consignez les commandes exécutées, les résultats obtenus, les changements réalisés et les tests de non-régression.


# 16. Scénarios de dépannage

## Scénario A — Le poste n'obtient aucune adresse IPv4

### Symptôme

Un poste raccordé à un port du VLAN 30 ne reçoit pas l'adresse IP attendue.

### Hypothèses

- Port désactivé ou lien physique défectueux.
- Port affecté au mauvais VLAN.
- Serveur DHCP indisponible.
- Étendue DHCP épuisée.
- Relais DHCP absent ou incorrect.
- VLAN 30 absent du trunk.
- Requête ou réponse bloquée.
- Configuration client incorrecte.

### Démarche

1. Vérifier le lien et l'état du port.
2. Vérifier le VLAN access.
3. Examiner le trunk si le trafic doit traverser un autre commutateur.
4. Contrôler le relais DHCP.
5. Contrôler l'étendue et les journaux du serveur DHCP.
6. Observer les échanges DHCP dans une capture.
7. Confirmer le renouvellement et l'adresse finalement obtenue.

### Preuve attendue

Une configuration correcte doit fournir l'adresse du sous-réseau approprié, le masque, la passerelle et les DNS attendus.

La commande `ping` ne permet pas, à elle seule, de diagnostiquer un échec d'attribution DHCP.


## Scénario B — Le poste reçoit une adresse IP, mais n'atteint pas la passerelle

### Symptôme

Le poste reçoit une adresse du VLAN 30, mais les communications avec la passerelle échouent.

### Hypothèses

- Mauvaise adresse ou mauvais masque.
- SVI en panne.
- VLAN absent de la configuration du commutateur.
- Trunk mal configuré.
- Incohérence de VLAN natif ou de liste de VLAN autorisés.
- Problème ARP.
- Filtrage ou protection de port.
- La passerelle n'autorise pas le type de test utilisé.

### Démarche

1. Confirmer l'adresse et le masque du poste.
2. Vérifier l'état du port et le VLAN.
3. Vérifier la présence du VLAN sur les chemins concernés.
4. Vérifier l'état et l'adresse de la SVI.
5. Examiner la table ARP sur les équipements concernés.
6. Examiner les journaux et compteurs d'interface.
7. Confirmer le comportement avec une capture adaptée.

### Point important

Un ping bloqué ne démontre pas automatiquement que l'interface de passerelle est hors service. ICMP peut être filtré alors que d'autres services fonctionnent.


## Scénario C — L'adresse IP répond, mais le nom DNS échoue

### Symptôme

Un poste peut joindre un serveur par son adresse IP, mais l'application ne fonctionne pas lorsqu'elle est appelée par son nom.

### Hypothèses

- Mauvaise adresse DNS distribuée.
- Enregistrement absent ou incorrect.
- Service DNS indisponible.
- Port DNS bloqué.
- Domaine ou suffixe incorrect.
- Cache DNS obsolète.
- Résolution IPv4/IPv6 incohérente.
- L'application dépend d'un nom différent de celui testé.

### Démarche

1. Afficher la configuration DNS du client.
2. Interroger directement le serveur DNS attendu.
3. Vérifier l'enregistrement demandé.
4. Examiner la réponse DNS.
5. Vérifier l'accessibilité du service applicatif.
6. Comparer les résultats depuis un autre client autorisé.
7. Contrôler le chemin IPv4 et IPv6 si les deux sont actifs.

### Preuve attendue

Une requête DNS doit retourner la réponse attendue et le client doit pouvoir utiliser l'adresse renvoyée pour accéder au service, sous réserve du filtrage et de l'état de l'application.


## Scénario D — Un visiteur accède à une ressource interne

### Symptôme

Un appareil du VLAN visiteurs atteint un serveur interne ou une interface de gestion.

### Gravité

Élevée : le principe d'isolement du réseau visiteurs n'est pas respecté.

### Hypothèses

- ACL absente ou placée au mauvais endroit.
- VLAN visiteurs routé sans filtrage suffisant.
- Route alternative.
- Filtrage IPv4 présent mais politique IPv6 incomplète.
- Mauvaise affectation de VLAN.
- Trunk qui transporte des VLAN inutiles.
- Accès à un service publié de manière excessive.
- Mauvaise conception du pare-feu ou de l'isolation WLAN.

### Démarche

1. Vérifier le VLAN et l'adresse IP du visiteur.
2. Identifier la destination et le protocole réellement utilisés.
3. Déterminer le chemin réseau.
4. Examiner les ACL et règles de pare-feu applicables.
5. Vérifier les routes IPv4 et IPv6.
6. Reproduire le test avec une destination de contrôle autorisée et une destination interdite.
7. Corriger la règle au point de contrôle approprié.
8. Vérifier que les services invités légitimes fonctionnent encore.

### Validation

- Internet fonctionne conformément à la politique.
- Les ressources internes restent inaccessibles.
- Les interfaces de gestion restent inaccessibles.
- Les journaux permettent de comprendre le refus.
- Les chemins IPv4 et IPv6 sont contrôlés.


## Scénario E — Les utilisateurs Finance accèdent à un service non autorisé

### Symptôme

Un utilisateur Finance atteint un serveur ou une application qui devrait être réservé à un autre service.

### Hypothèses

- Politique de filtrage trop permissive.
- ACL appliquée dans le mauvais sens.
- Règle d'autorisation trop large.
- Routage inter-VLAN sans contrôle approprié.
- Filtrage appliqué uniquement au trafic Internet.
- Flux existant autorisé par un autre chemin.
- Application accessible via plusieurs adresses.

### Démarche

1. Identifier précisément la source, la destination, le port et le protocole.
2. Rechercher la règle qui autorise ou bloque le flux.
3. Examiner les règles précédentes dans l'ordre d'évaluation applicable.
4. Vérifier les chemins alternatifs.
5. Appliquer la restriction minimale qui respecte le besoin métier.
6. Tester l'application légitime et la connexion interdite.
7. Documenter la modification et le retour arrière.


## Scénario F — Les téléphones IP sont connectés, mais les appels échouent

### Symptôme

Les téléphones reçoivent une adresse IP, mais ils ne s'enregistrent pas ou aucun média audio n'est échangé.

### Hypothèses

- VLAN voix incorrect.
- DHCP ou option de provisioning incorrecte.
- DNS incorrect.
- Accès au serveur de téléphonie bloqué.
- Problème de signalisation.
- Ports médias non autorisés.
- Problème de QoS.
- MTU ou routage défaillant.
- Téléphone mal provisionné.

### Démarche

1. Vérifier le VLAN et l'adresse du téléphone.
2. Vérifier les services nécessaires à son démarrage.
3. Vérifier la résolution DNS.
4. Tester la connectivité au service de téléphonie.
5. Examiner la signalisation et les journaux du système.
6. Examiner le flux média pendant un appel de test.
7. Vérifier les règles de sécurité et la QoS.
8. Tester un appel local et un appel représentatif du besoin.

Un téléphone qui obtient une adresse IP ne prouve pas que le service de téléphonie est pleinement opérationnel.


## Scénario G — Un serveur est accessible depuis un VLAN, mais pas depuis un autre

### Symptôme

Le même service fonctionne depuis un poste Finance, mais échoue depuis un poste Employés.

### Hypothèses

- Politique inter-VLAN différente.
- ACL ou pare-feu.
- Route de retour absente.
- Service lié à une seule interface.
- Filtrage local sur le serveur.
- Résolution DNS différente.
- Utilisation d'une adresse IP ou d'un port différent.

### Démarche

1. Comparer les configurations IP des deux postes.
2. Vérifier la même destination et le même port.
3. Vérifier les routes.
4. Examiner les ACL et règles de pare-feu.
5. Examiner les logs du serveur.
6. Tester la connexion TCP ou le protocole réel.
7. Corriger la règle sans ouvrir tous les flux entre les deux VLAN.


## Scénario H — Le réseau est lent seulement lors des transferts volumineux

### Symptôme

Les applications simples répondent correctement, mais les gros transferts ralentissent, se figent ou échouent.

### Hypothèses

- Congestion ou interfaces saturées.
- Erreurs physiques.
- Duplex ou négociation incorrecte sur du matériel qui le permet.
- Problème de MTU.
- Filtrage ou inspection coûteuse.
- Perte de paquets.
- Équipement de sécurité sous-dimensionné.
- Problème applicatif ou de stockage.

### Démarche

1. Mesurer le débit attendu et le débit observé.
2. Examiner les compteurs des interfaces.
3. Rechercher erreurs, pertes et drops.
4. Vérifier l'utilisation des liens et des équipements.
5. Examiner le MTU de bout en bout.
6. Utiliser une capture pour rechercher retransmissions et anomalies.
7. Comparer le chemin local et le chemin passant par le pare-feu.
8. Mesurer avant et après chaque changement.

Ne modifiez pas le MTU au hasard. Une modification doit reposer sur des mesures et préserver la cohérence du chemin.


# 17. Défi Wireshark — Observer le fonctionnement réel

Wireshark permet de voir les échanges réellement observés sur l'interface de capture. Une capture réalisée à un endroit donné n'expose pas nécessairement tout le trafic du réseau.

Il est donc important de connaître le point de capture :

- Sur le poste client.
- Sur un port miroir du commutateur.
- Sur une interface de pare-feu.
- Sur le serveur.
- Sur un point de capture Wi-Fi adapté.

Les résultats diffèrent selon le point choisi.

## 17.1. Filtres d'affichage utiles

### DHCP

```text
dhcp
```

### DNS

```text
dns
```

### ARP

```text
arp
```

### ICMP

```text
icmp
```

### TCP SYN

```text
tcp.flags.syn == 1
```

Pour isoler les paquets SYN sans l'indicateur ACK :

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

### Trafic vers une adresse IPv4 donnée

```text
ip.addr == 10.20.40.20
```

### Trafic entre deux adresses IPv4

```text
ip.src == 10.20.30.25 && ip.dst == 10.20.40.20
```

### Port TCP donné

```text
tcp.port == 443
```

Ces expressions sont des filtres d'affichage. Les filtres de capture utilisent une syntaxe différente.

## 17.2. Exercice DHCP

Capturez le processus d'attribution d'adresse d'un client.

Identifiez, lorsque les échanges sont visibles :

1. DHCP Discover.
2. DHCP Offer.
3. DHCP Request.
4. DHCP ACK.

Expliquez à quel moment le serveur propose une configuration et à quel moment le client confirme l'utilisation du bail.

Si certains paquets ne sont pas visibles, vérifiez le point de capture avant d'en conclure que l'échange est absent.

## 17.3. Exercice DNS

1. Interrogez un nom connu.
2. Capturez la requête et la réponse.
3. Identifiez le serveur interrogé.
4. Examinez le type de requête.
5. Lisez le code de réponse.
6. Vérifiez les adresses retournées.
7. Comparez avec le résultat obtenu lorsque le nom n'existe pas.

## 17.4. Exercice TCP

Pour une connexion TCP de test :

1. Repérez le SYN du client.
2. Recherchez le SYN-ACK du serveur.
3. Recherchez l'ACK du client.
4. Vérifiez la poursuite des échanges.
5. Observez les retransmissions éventuelles.
6. Vérifiez si la connexion se ferme normalement ou est réinitialisée.

Une capture sur le client peut montrer un SYN transmis sans révéler immédiatement pourquoi le serveur ne répond pas. Il faudra peut-être une deuxième capture ou les journaux du point de contrôle pour localiser le blocage.

## 17.5. Exercice MTU

Sur un environnement de test contrôlé, observez le comportement lors d'un transfert volumineux.

Cherchez notamment :

- Retransmissions.
- Paquets trop volumineux pour un segment.
- Messages ICMP liés au MTU ou à la fragmentation, selon la version IP et le chemin.
- Différences entre le trafic local et celui qui traverse un tunnel.
- Indices de blocage de la découverte du MTU de chemin.

Le diagnostic doit tenir compte d'IPv4, d'IPv6, des tunnels et des équipements traversés.


# 18. Architecture 3 — Vue complète des flux

Cette architecture de flux représente les grandes communications attendues dans le scénario.

```text
                    +----------------------+
                    | INTERNET             |
                    +----------------------+
                              ^
                              |
                       [ PARE-FEU / NAT ]
                              ^
                              |
                       [ CŒUR L3 / ACL ]
                              |
          +-------------------+----------------------+
          |                   |                      |
          v                   v                      v
   VLAN 30 EMPLOYÉS     VLAN 20 FINANCE        VLAN 80 WIFI-CORP
          |                   |                      |
          +-------------------+----------------------+
                              |
                              v
                     VLAN 40 SERVEURS
                     DNS / Applications
                     Fichiers / Services
                              ^
                              |
                  Accès uniquement autorisés
                              |
          +-------------------+----------------------+
          |                   |                      |
       VLAN 50             VLAN 60                VLAN 10
       VOIP             IMPRIMANTES / IOT       ADMIN
          |                   |                      |
     Services voix       Flux limités                 v
     autorisés           vers imprimantes       VLAN 90 MGMT
                                                  INFRASTRUCTURE


                  VLAN 70 WIFI-INVITES
                            |
                            v
                       [ CŒUR L3 ]
                            |
                       [ PARE-FEU ]
                            |
                         INTERNET

                  AUCUN ACCÈS INTERNE
                  SELON LA POLITIQUE
```

Ce schéma représente des intentions de flux. Le comportement réel dépend des règles configurées, du routage et des chemins IPv4/IPv6.

Le cœur L3 effectue le routage inter-VLAN dans cette architecture. Les ACL doivent donc appliquer les restrictions inter-zones, tandis que le pare-feu contrôle les flux relevant de son périmètre, notamment l'accès WAN.


# 19. Défi 11 — Sécurité de couche 2

Les protections de couche 2 doivent être adaptées au matériel et au contexte.

## 19.1. Protections à évaluer

Selon les fonctionnalités disponibles, examinez :

- Port security.
- BPDU Guard sur les ports d'accès adaptés.
- Root Guard lorsque la topologie et le rôle du port le justifient.
- DHCP snooping.
- Dynamic ARP Inspection.
- Contrôle d'accès au réseau.
- Désactivation des ports inutilisés.
- Limitation des trunks.
- Désactivation de la négociation automatique de trunk lorsque la plateforme l'exige ou le permet.
- Contrôle des tempêtes de broadcast.
- Contrôle et surveillance des changements de topologie STP.

Toutes ces protections ne doivent pas être activées sans analyse : leur fonctionnement dépend de la topologie, des équipements et des dépendances de service.

## 19.2. DHCP snooping

Le DHCP snooping permet, sur les équipements qui le prennent en charge, de distinguer les ports autorisés à fournir des réponses DHCP des ports qui ne doivent normalement pas le faire.

Une erreur de configuration peut bloquer des réponses légitimes. Lors du déploiement, documentez explicitement les ports considérés comme fiables.

## 19.3. Spanning Tree

STP empêche les boucles de niveau 2 dans les topologies Ethernet où plusieurs chemins physiques peuvent exister.

À vérifier :

- Le commutateur racine attendu.
- Les ports racines.
- Les ports bloqués.
- Les changements inattendus de topologie.
- L'activation appropriée de PortFast.
- L'utilisation de BPDU Guard sur les ports terminaux prévus.
- La cohérence avec les liens redondants et les mécanismes de commutation utilisés.

Une boucle de niveau 2 peut provoquer une instabilité importante, une multiplication des trames et une perturbation de l'ensemble d'un domaine de diffusion.


# 20. Défi 12 — IPv6 et cohérence des politiques

IPv6 ne doit pas être traité comme un simple détail à ignorer.

Le dossier d'architecture doit préciser si IPv6 :

- Est activé et utilisé.
- Est prévu dans une phase future.
- Est désactivé intentionnellement lorsque cette décision est justifiée et compatible avec les systèmes utilisés.

L'absence de documentation ne constitue pas une politique IPv6.

## 20.1. Questions à résoudre

1. Les postes obtiennent-ils des adresses IPv6 ?
2. Le réseau utilise-t-il SLAAC, DHCPv6 ou une combinaison ?
3. Comment les résolveurs DNS sont-ils annoncés ?
4. Les règles de filtrage IPv6 sont-elles définies ?
5. Les équipements de gestion sont-ils protégés en IPv6 ?
6. Les visiteurs disposent-ils d'un chemin IPv6 vers les ressources internes ?
7. Les mécanismes de découverte et de contrôle nécessaires à IPv6 sont-ils autorisés ?
8. La supervision observe-t-elle aussi IPv6 ?

IPv6 possède notamment des mécanismes de découverte de voisins et de configuration qui ne se confondent pas directement avec ARP et DHCPv4.

## 20.2. Règle de validation

Une politique de sécurité doit être cohérente pour chaque protocole IP utilisé.

Bloquer une communication interdite en IPv4 tout en laissant une communication IPv6 équivalente disponible ne constitue pas une segmentation complète.


# 21. Défi 13 — Supervision et exploitation

Une architecture de production doit être observable et maintenable.

## 21.1. Éléments à surveiller

| Élément | Mesures ou états utiles |
|---|---|
| Commutateurs | État des ports, erreurs, saturation, changements STP |
| Cœur L3 | État des SVI, routes, charge, pertes |
| Pare-feu | Sessions, règles, ressources, événements de sécurité |
| Points d'accès | Clients, canaux, utilisation radio, erreurs d'authentification |
| DHCP | Baux, épuisement des plages, erreurs |
| DNS | Disponibilité, latence et erreurs de résolution |
| Serveurs | Charge, mémoire, stockage, disponibilité des services |
| Liens | Débit, pertes et disponibilité |
| Sauvegardes | Succès, échecs, capacité et tests de restauration |
| Infrastructure | Alimentation, température et incidents matériels |

## 21.2. Journalisation

Les événements à conserver peuvent inclure :

- Connexions d'administration.
- Changements de configuration.
- Refus d'accès significatifs.
- Échecs d'authentification.
- Changements de topologie.
- Pannes d'interface.
- Événements de bascule.
- Incidents de sécurité pertinents.

La durée de conservation doit respecter les obligations et la politique de l'entreprise. Les journaux ne doivent pas être stockés dans un emplacement dont les utilisateurs ordinaires peuvent librement modifier le contenu.

## 21.3. Documentation minimale

Le dossier d'exploitation doit contenir :

- Schéma physique.
- Schéma logique.
- Inventaire des équipements.
- Plan IP.
- Plan de VLAN.
- Matrice de flux.
- Description des trunks.
- Liste des passerelles.
- Référentiel des règles de sécurité.
- Procédures de sauvegarde.
- Procédure de restauration.
- Procédure de retour arrière.
- Contacts et responsabilités.
- Historique des changements.


# 22. Défi final — Incident combiné

Vous êtes appelé à la suite d'une série de plaintes signalées en même temps.

Les utilisateurs indiquent que :

1. Certains postes reçoivent une adresse IP incorrecte.
2. Des utilisateurs ne peuvent plus résoudre le nom d'une application interne.
3. Le Wi-Fi visiteurs semble parfois accéder à une ressource qui devrait être interne.
4. L'administration SSH d'un commutateur échoue depuis le poste d'administration.
5. Certains transferts de fichiers sont anormalement lents.
6. La téléphonie fonctionne pour certains utilisateurs mais pas pour d'autres.

Vous ne disposez pas de la certitude que ces incidents possèdent une cause commune.

## 22.1. Règles de l'investigation

Vous devez :

- Ne pas réinitialiser toute l'infrastructure.
- Ne pas désactiver globalement les ACL.
- Ne pas autoriser tous les VLAN sur tous les trunks.
- Ne pas modifier le MTU sans preuve.
- Ne pas désactiver les protections de couche 2 sans comprendre leur effet.
- Conserver une trace de chaque changement.
- Traiter en priorité les expositions de sécurité.
- Évaluer l'étendue de chaque incident avant d'appliquer une correction.

## 22.2. Première phase : collecte des faits

Construisez un tableau des symptômes :

| Symptôme | Source | Destination | Protocole/service | Première preuve |
|---|---|---|---|---|
| Adresse IP incorrecte | Poste affecté | DHCP | DHCP | Adresse, masque, passerelle et serveur observés |
| DNS échoue | Poste affecté | DNS interne | DNS | Résultat de la requête |
| Accès interne depuis invités | Terminal invité | Ressource concernée | À identifier | Adresse source, destination et journal |
| SSH échoue | Poste d'administration | Commutateur | TCP/SSH | Route, port, ACL et journal |
| Transfert lent | Poste affecté | Serveur de fichiers | TCP/application | Débit, erreurs et capture |
| Appels échoués | Téléphone | Système de téléphonie | Signalisation et média | État du téléphone et traces |

## 22.3. Deuxième phase : établir les dépendances

Pour chaque symptôme, identifiez les dépendances pertinentes.

Exemples :

- Le problème d'adresse IP peut dépendre d'un port access, d'un trunk, du relais DHCP ou du serveur DHCP.
- Le problème DNS peut dépendre de l'adresse reçue, du routage et des règles de filtrage.
- L'accès invité à une ressource interne peut dépendre d'une mauvaise affectation de VLAN ou d'un filtrage incomplet.
- L'échec SSH peut dépendre de la source autorisée, du VLAN de gestion et du service d'administration.
- La lenteur des transferts peut dépendre de la charge, d'erreurs physiques, du MTU ou du chemin traversé.
- La téléphonie peut dépendre du VLAN voix, du provisioning, de la signalisation ou des flux médias.

## 22.4. Troisième phase : prioriser les actions

Une approche raisonnable consiste à :

1. Vérifier et contenir le chemin d'accès interne depuis le réseau visiteurs.
2. Préserver l'accès d'administration nécessaire à l'équipe de dépannage.
3. Contrôler les attributions IP anormales.
4. Vérifier le DNS et les services essentiels.
5. Diagnostiquer les incidents de téléphonie.
6. Mesurer la lenteur des transferts.
7. Déterminer si les symptômes ont une cause commune.
8. Valider l'ensemble après chaque correction.

L'ordre exact peut changer selon les faits observés et l'impact de l'incident. La priorité sécurité est forte, mais il faut préserver une voie d'administration autorisée et éviter une modification qui couperait l'accès de dépannage.

## 22.5. Rapport final obligatoire

Le rapport doit contenir :

- Les symptômes initiaux.
- L'étendue des utilisateurs et équipements affectés.
- Les hypothèses envisagées.
- Les tests réalisés.
- Les résultats bruts importants.
- La cause racine démontrée pour chaque incident.
- Les changements effectués.
- Les tests de validation.
- Les effets secondaires éventuels.
- Les risques résiduels.
- Les recommandations de prévention.

Une hypothèse plausible n'est pas une cause racine tant qu'elle n'est pas étayée par des observations.


# 23. Architecture cible complète à remettre

Cette section rassemble les principaux choix du challenge dans un modèle unique.

## 23.1. Schéma global

```text
                               INTERNET
                                  |
                         +------------------+
                         | PARE-FEU         |
                         | Filtrage / NAT   |
                         | VPN / Journaux   |
                         +------------------+
                                  |
                             Réseau transit
                                  |
                         +------------------+
                         | CŒUR L3          |
                         | Passerelles SVI  |
                         | Routage IPv4     |
                         | ACL inter-VLAN   |
                         +------------------+
                          |   |    |    |   |
             +------------+   |    |    +------------+
             |                |    |                 |
        VLAN 40           VLAN 50 VLAN 60         VLAN 90
        SERVEURS          VOIP    PÉRIPHÉRIQUES   GESTION
             |                |    |                 |
       DNS / Applications   Téléphones Imprimantes  Équipements
       DHCP / NTP           IP        / IoT         réseau
             |
      +------+-------------------------------+
      |                                      |
   VLAN 20                                VLAN 30
   FINANCE-RH                             EMPLOYÉS
      |                                      |
   Postes                                 Postes
   sensibles                              standards

      +-------------------+------------------+
                          |
                     VLAN 10 ADMIN
                          |
                 Postes d'administration

           +-------------------------------+
           |                               |
       VLAN 80                          VLAN 70
       WI-FI ENTREPRISE                 WI-FI VISITEURS
           |                               |
       Accès interne                    Internet
       contrôlé                         uniquement
```

## 23.2. Résumé des décisions

| Domaine | Décision de référence | Justification |
|---|---|---|
| Segmentation | Un VLAN par fonction logique | Limiter les domaines de diffusion et organiser les flux |
| Passerelles | SVI sur cœur L3 | Routage inter-VLAN performant |
| Sécurité interne | ACL inter-VLAN documentées | Éviter les accès implicites |
| Internet | Pare-feu dédié | Contrôler les flux WAN et les services associés |
| Administration | VLAN 10 et VLAN 90 distincts | Séparer les postes d'administration des interfaces de gestion |
| Serveurs | VLAN 40 | Regrouper les services internes selon les besoins |
| Téléphonie | VLAN 50 | Séparer la voix et gérer les exigences associées |
| Périphériques | VLAN 60 | Limiter les droits des imprimantes et IoT |
| Wi-Fi entreprise | VLAN 80 | Accès interne selon l'identité et les règles prévues |
| Wi-Fi visiteurs | VLAN 70 | Accès Internet sans accès interne |
| Adressage | `10.20.0.0/16` avec sous-réseaux distincts | Plan d'adressage cohérent pour l'exercice |
| Trunks | VLAN autorisés explicitement | Réduire l'exposition inutile |
| Disponibilité | Redondance des composants critiques selon le budget | Réduire les points uniques de panne |
| Supervision | Mesures et journaux pertinents | Accélérer le diagnostic |
| Changements | Tests et retour arrière documentés | Réduire le risque d'interruption |


# 24. Barème d'évaluation sur 100 points

L'évaluation doit mesurer à la fois la qualité de la conception et la capacité à la prouver.

| Domaine évalué | Points |
|---|---:|
| Analyse des besoins et inventaire | 8 |
| Architecture physique | 8 |
| Architecture logique et segmentation | 10 |
| Plan IP et DHCP | 10 |
| VLAN et trunks | 10 |
| Routage et flux | 10 |
| Sécurité inter-VLAN et administration | 12 |
| Wi-Fi entreprise et visiteurs | 7 |
| Services DNS, NTP et téléphonie | 5 |
| Dépannage OSI et utilisation de Wireshark | 8 |
| Résilience et supervision | 5 |
| Documentation, tests et retour arrière | 7 |
| **Total** | **100** |

## 24.1. Critères de qualité

Une bonne solution doit :

- Être cohérente avec les besoins.
- Présenter des schémas lisibles.
- Utiliser un plan IP sans chevauchement.
- Distinguer les VLAN et les zones de sécurité.
- Expliquer le routage inter-VLAN.
- Démontrer l'application des politiques de filtrage.
- Inclure des tests de communications autorisées et interdites.
- Respecter le rôle de chaque équipement.
- Prévoir la sauvegarde et le retour arrière.
- Être exploitable par un autre administrateur.

## 24.2. Erreurs graves

Les erreurs suivantes doivent entraîner une pénalité importante :

- Donner un accès général aux visiteurs vers le réseau interne.
- Permettre l'administration depuis tous les VLAN.
- Utiliser des trunks sans connaître leur fonction.
- Désactiver des protections de couche 2 sans analyse.
- Confondre NAT et contrôle complet de sécurité.
- Supposer qu'un ping réussi garantit le bon fonctionnement d'une application.
- Déduire la cause d'un incident sans preuve.
- Modifier plusieurs paramètres en même temps, sans possibilité de déterminer l'effet de chaque changement.
- Omettre les tests de non-régression.

Une solution qui fonctionne par hasard n'est pas équivalente à une architecture correctement conçue.


# 25. Modèle du dossier final

Utilisez le modèle suivant pour présenter votre travail.

## 25.1. Résumé exécutif

Décrivez en quelques paragraphes :

- Le problème initial.
- L'architecture proposée.
- Les bénéfices attendus.
- Les principaux risques et limites.

## 25.2. Besoins et hypothèses

Présentez :

- Le nombre d'utilisateurs et d'équipements.
- Les services essentiels.
- Les besoins de disponibilité.
- Les besoins de sécurité.
- Les contraintes matérielles et budgétaires.
- Les hypothèses restant à confirmer.

## 25.3. Architecture physique

Fournissez un schéma montrant :

- Le pare-feu.
- Le cœur réseau.
- Les commutateurs d'accès.
- Les serveurs.
- Les points d'accès.
- Les liens principaux.
- Les mécanismes de redondance retenus, s'il y en a.

## 25.4. Architecture logique

Fournissez un schéma montrant :

- Les VLAN.
- Les sous-réseaux.
- Les passerelles.
- Les zones de sécurité.
- Le routage.
- Les frontières de filtrage.
- Les chemins vers les services internes et Internet.

## 25.5. Plan d'adressage

Documentez pour chaque réseau :

- Le VLAN.
- Le sous-réseau.
- La passerelle.
- La plage DHCP.
- Les réservations.
- Les serveurs DNS.
- Les éventuels relais DHCP.
- Les objectifs d'évolution.

## 25.6. Matrice de flux

Pour chaque communication nécessaire, indiquez :

- La source.
- La destination.
- Le protocole.
- Le port.
- La justification.
- Le point de filtrage.
- Les tests positifs et négatifs.
- Le responsable métier ou technique.

## 25.7. Configuration

Fournissez les extraits pertinents et anonymisés de configuration, en précisant :

- L'équipement concerné.
- Le rôle de la configuration.
- Les prérequis.
- Les commandes de vérification.
- Les risques éventuels.
- La procédure de retour arrière.

Ne publiez pas les secrets, mots de passe, clés privées ou jetons d'authentification dans le rapport.

## 25.8. Tests de validation

Présentez un tableau de résultats :

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | Attribution IP VLAN 30 | Adresse correcte | À renseigner | À exécuter |
| T02 | Résolution DNS interne | Réponse attendue | À renseigner | À exécuter |
| T03 | Accès à l'application autorisée | Connexion réussie | À renseigner | À exécuter |
| T04 | Accès interdit depuis invités | Connexion bloquée | À renseigner | À exécuter |
| T05 | Administration depuis VLAN 10 | SSH autorisé | À renseigner | À exécuter |
| T06 | Administration depuis VLAN 70 | SSH bloqué | À renseigner | À exécuter |
| T07 | Trunks | VLAN conformes | À renseigner | À exécuter |
| T08 | Téléphonie | Appel de test réussi | À renseigner | À exécuter |
| T09 | Transfert de fichiers | Performance mesurée | À renseigner | À exécuter |
| T10 | Retour après panne simulée | Comportement documenté | À renseigner | À exécuter |

**Important :** ne remplacez pas un résultat inconnu par « OK ». Le statut doit correspondre à un test effectivement réalisé.


# 26. Checklist finale

Avant de remettre l'architecture, vérifiez les éléments suivants.

## Conception

- [ ] Les besoins sont documentés.
- [ ] Les hypothèses sont identifiées.
- [ ] L'architecture physique est cohérente.
- [ ] L'architecture logique est cohérente.
- [ ] Les VLAN ont une fonction claire.
- [ ] Les sous-réseaux ne se chevauchent pas.
- [ ] Les passerelles sont définies.
- [ ] Les flux nécessaires sont identifiés.

## Configuration

- [ ] Les ports d'accès ont le bon VLAN.
- [ ] Les trunks n'autorisent que les VLAN nécessaires.
- [ ] Le VLAN natif est cohérent avec la conception.
- [ ] Les ports inutilisés sont traités.
- [ ] Le routage inter-VLAN est fonctionnel.
- [ ] Les routes de retour sont présentes.
- [ ] Les ACL correspondent à la matrice de flux.
- [ ] Les services DHCP et DNS sont validés.
- [ ] Les règles IPv6 sont étudiées lorsque IPv6 est actif.

## Sécurité

- [ ] Le VLAN visiteurs est isolé.
- [ ] Les interfaces d'administration sont protégées.
- [ ] Les périphériques IoT sont limités aux flux nécessaires.
- [ ] Les services accessibles aux utilisateurs sont documentés.
- [ ] Les journaux sont disponibles.
- [ ] Les comptes d'administration sont protégés.
- [ ] Les configurations sont sauvegardées.
- [ ] Les secrets ne figurent pas dans le rapport.

## Validation

- [ ] Les communications autorisées fonctionnent.
- [ ] Les communications interdites sont bloquées.
- [ ] Les résultats sont consignés.
- [ ] Les captures pertinentes sont conservées.
- [ ] Les performances ont été mesurées.
- [ ] Les scénarios de panne sont documentés.
- [ ] Le retour arrière est défini.
- [ ] Le dossier peut être compris par un autre administrateur.


# 27. Références techniques à consulter

Les références ci-dessous permettent de vérifier les principes abordés et d'approfondir les technologies concernées.

- **RFC 1918 — Address Allocation for Private Internets** : plages IPv4 privées.
- **IEEE 802.1Q** : pontage VLAN et marquage des trames Ethernet.
- **RFC 2131 — Dynamic Host Configuration Protocol** : fonctionnement de DHCPv4.
- **RFC 1034 et RFC 1035** : architecture et fonctionnement du DNS.
- **RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification** : spécification IPv6.
- **Documentation officielle de l'équipementier** : VLAN, trunks, routage L3, STP, ACL, DHCP relay et fonctions de haute disponibilité.
- **Documentation Wireshark** : filtres d'affichage, capture et analyse des protocoles.
- **Documentation officielle du système d'exploitation** : outils réseau, routes, DNS et diagnostic.

Les commandes données dans ce document utilisent des exemples Cisco IOS ou des outils courants. Elles doivent être adaptées au système réellement installé et vérifiées avant utilisation sur un réseau de production.


# Conclusion

Ce challenge doit aboutir à une architecture dont le fonctionnement est démontré et dont les règles sont compréhensibles.

Un réseau de bureau professionnel ne se limite pas à raccorder des postes à des commutateurs. Il faut définir des frontières de confiance, contrôler les chemins de communication, gérer les services d'infrastructure, protéger l'administration et prévoir la reprise après incident.

La réussite du challenge repose sur quatre éléments :

1. **Une architecture compréhensible** : physique, logique et documentée.
2. **Une politique de sécurité explicite** : les flux autorisés et interdits sont identifiés.
3. **Des preuves techniques** : les tests et les captures démontrent le comportement réel.
4. **Une exploitation maîtrisée** : sauvegarde, supervision, traçabilité et retour arrière sont prévus.

La meilleure architecture n'est pas celle qui autorise tout à fonctionner sans distinction. C'est celle qui permet aux utilisateurs d'effectuer leur travail, qui limite les communications inutiles, et dont le comportement peut être vérifié, expliqué et maintenu.*Note** : Ce cours est en cours de rédaction. Utilisez Gemini pour générer le contenu complet !