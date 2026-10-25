# Challenge d'architecture réseau — Petite entreprise

> **Fichier :** `challenge-small-business.md`  
> **Domaine :** conception et exploitation d'un réseau professionnel de petite entreprise  
> **Progression :** Débutant → Intermédiaire → Expert  
> **Environnement :** bureau de 15 à 30 utilisateurs  
> **Approche :** architecture physique, segmentation logique, sécurité, mise en service et dépannage  
> **Objectif final :** concevoir un réseau professionnel fiable, sécurisé, évolutif et facile à administrer, sans complexité disproportionnée par rapport à la taille de l'entreprise.


# 1. Présentation du challenge

## 1.1. Le contexte

Vous êtes chargé de concevoir le réseau informatique de **NovaBureau**, une petite entreprise qui emploie 24 personnes.

L'entreprise occupe un même bâtiment et dispose des équipements suivants :

- Des ordinateurs fixes et portables.
- Des smartphones professionnels.
- Une connexion Internet.
- Un commutateur réseau administrable.
- Un pare-feu ou routeur professionnel.
- Des points d'accès Wi-Fi.
- Une imprimante multifonction réseau.
- Un serveur de fichiers ou un NAS.
- Des applications métier hébergées localement ou dans le cloud.
- Quelques téléphones IP, selon les besoins.
- Des équipements de supervision et de sauvegarde.

Le réseau a été installé progressivement. Certains équipements ont été ajoutés sans documentation, les mots de passe d'administration ne sont pas correctement gérés, le Wi-Fi des visiteurs n'est pas toujours séparé du réseau de travail et les sauvegardes ne sont pas régulièrement testées.

La direction souhaite remettre l'infrastructure à niveau sans acheter inutilement du matériel complexe.

Votre mission est de concevoir une architecture adaptée à cette entreprise et de prouver qu'elle répond aux besoins.

## 1.2. Le véritable objectif

Il ne suffit pas de faire fonctionner Internet sur tous les postes.

Vous devez construire un réseau dans lequel :

- Les collaborateurs accèdent aux applications nécessaires à leur travail.
- Les données partagées sont protégées.
- Les visiteurs disposent d'un accès Internet sans accès au réseau interne.
- Les imprimantes et périphériques réseau sont correctement contrôlés.
- Les équipements réseau ne sont administrables que depuis des sources autorisées.
- Le Wi-Fi professionnel est distinct du Wi-Fi visiteurs.
- Une panne peut être localisée méthodiquement.
- Les configurations peuvent être sauvegardées et restaurées.
- Les dépenses et la complexité technique restent proportionnées aux besoins.
- Une autre personne de l'équipe informatique peut comprendre et maintenir le réseau.

## 1.3. Hypothèses du scénario

| Élément | Hypothèse |
|---|---|
| Employés | 24 |
| Bâtiment | Un site |
| Postes informatiques | 24 à 35 équipements selon les usages |
| Imprimantes | 1 à 3 |
| Stockage interne | NAS ou serveur de fichiers |
| Réseau filaire | Ethernet commuté |
| Wi-Fi | Réseau professionnel et réseau visiteurs |
| Accès Internet | Une connexion principale |
| Pare-feu | Équipement capable de gérer des VLAN et des règles de filtrage |
| Commutateur | Modèle administrable avec prise en charge de 802.1Q |
| Alimentation | Onduleur pour les équipements critiques |
| Sauvegardes | Copie locale et copie séparée du site principal |
| Utilisateurs avancés | Quelques personnes chargées de l'administration |
| Croissance prévue | Environ 30 à 40 utilisateurs à moyen terme |

Ces hypothèses servent à l'exercice. Un projet réel doit commencer par un inventaire des équipements, une analyse des applications, une étude des contraintes du bâtiment et une vérification des capacités du matériel.

## 1.4. Contraintes de conception

L'entreprise ne dispose pas d'un budget illimité.

La solution doit donc :

- Utiliser un nombre raisonnable de VLAN.
- Éviter de multiplier les équipements sans justification.
- Privilégier une administration centralisée et documentée.
- Utiliser du matériel administrable compatible avec la segmentation.
- Prévoir des mesures de sécurité faciles à exploiter.
- Maintenir une marge pour l'ajout de nouveaux équipements.
- Éviter les dépendances inutiles à un serveur local.
- Garantir que les sauvegardes restent accessibles en cas d'incident majeur.

Une architecture adaptée à 24 utilisateurs n'est pas nécessairement celle qu'il faut déployer pour un centre de données. L'objectif consiste à trouver un équilibre entre sécurité, coût, disponibilité et capacité d'exploitation.


# 2. Progression des niveaux

Le challenge se déroule en trois niveaux cumulatifs.

## Niveau 1 — Débutant : construire un réseau fonctionnel

Vous devez :

- Recueillir les besoins.
- Identifier les équipements.
- Dessiner l'architecture physique.
- Définir les VLAN principaux.
- Créer un plan IPv4.
- Comprendre les passerelles et le routage.
- Vérifier DHCP, DNS et Internet.
- Connecter les postes et les imprimantes.
- Documenter les résultats.

**Livrable :** une architecture réseau fonctionnelle avec schémas, plan IP et tests de base.

## Niveau 2 — Intermédiaire : sécuriser le réseau

Vous devez :

- Établir une politique de flux entre les VLAN.
- Isoler les visiteurs.
- Protéger le réseau d'administration.
- Contrôler les trunks.
- Limiter les communications des imprimantes et du NAS.
- Sécuriser le Wi-Fi.
- Mettre en place une stratégie de sauvegarde.
- Configurer une supervision minimale.
- Résoudre des incidents combinant plusieurs causes possibles.

**Livrable :** une architecture segmentée avec matrice de flux, contrôles de sécurité et procédures de dépannage.

## Niveau 3 — Expert : préparer l'exploitation et l'évolution

Vous devez :

- Évaluer les points uniques de défaillance.
- Préparer un plan de continuité adapté au budget.
- Définir une procédure de changement.
- Valider la restauration des sauvegardes.
- Analyser les performances.
- Examiner la gestion IPv6.
- Évaluer les risques liés aux équipements cloud et aux accès distants.
- Définir une stratégie d'évolution vers 40 utilisateurs.
- Présenter les risques résiduels et les investissements prioritaires.

**Livrable :** un dossier d'architecture exploitable en production, avec politique de sécurité, plan de continuité et feuille de route.


# 3. Défi 1 — Analyser les besoins de NovaBureau

## 3.1. Identifier les catégories d'utilisateurs

L'entreprise comporte plusieurs catégories :

| Catégorie | Besoins |
|---|---|
| Direction | Applications de gestion, documents sensibles, Internet |
| Comptabilité | Logiciel comptable, factures, documents financiers |
| Administration | Courriel, documents, applications de gestion |
| Employés | Applications métier et partage de fichiers |
| Informatique | Administration des équipements, dépannage et sauvegardes |
| Visiteurs | Accès temporaire à Internet |
| Prestataires | Accès temporaire et limité à une ressource autorisée, si nécessaire |

L'existence de catégories différentes ne signifie pas nécessairement qu'il faut un VLAN par service. Les VLAN doivent être définis en fonction des besoins de communication, des risques et de la capacité d'exploitation.

Par exemple, si les employés utilisent les mêmes applications et ont des droits similaires, un VLAN commun peut être adapté. Les données sensibles doivent toutefois être protégées par des contrôles applicatifs et réseau appropriés.

## 3.2. Inventorier les équipements

Avant la conception, préparez un inventaire.

| Équipement | Quantité indicative | Fonction | Criticité |
|---|---:|---|---|
| Pare-feu | 1 | Filtrage, routage, VPN éventuel | Élevée |
| Commutateur administrable | 1 | Connexion filaire et VLAN | Élevée |
| Points d'accès Wi-Fi | 2 | Couverture sans fil | Moyenne à élevée |
| NAS ou serveur de fichiers | 1 | Documents partagés | Élevée |
| Imprimante réseau | 1 à 3 | Impression | Moyenne |
| PC et portables | 24 à 35 | Travail quotidien | Élevée |
| Téléphones IP | Selon les besoins | Téléphonie | Variable |
| Onduleur | 1 ou plusieurs | Protection électrique | Élevée |
| Serveur ou service de sauvegarde | Selon le choix retenu | Protection des données | Élevée |

Les quantités sont des estimations pour l'exercice. La capacité réelle d'un commutateur, le nombre de ports PoE, les débits et le nombre de points d'accès doivent être vérifiés.

## 3.3. Exigences à transformer en tests

| Exigence | Résultat attendu |
|---|---|
| Un employé se connecte au réseau | Une configuration IP correcte est attribuée |
| Un employé accède à une application métier | Le service requis fonctionne |
| Un visiteur utilise le Wi-Fi | Internet fonctionne sans accès aux ressources internes |
| Un poste imprime un document | Le service d'impression autorisé fonctionne |
| Un utilisateur accède au NAS | L'accès respecte ses permissions |
| Un administrateur gère le commutateur | L'accès est autorisé depuis une source prévue |
| Un poste ne peut pas administrer le pare-feu | L'accès d'administration est refusé |
| Une sauvegarde échoue | L'échec est détecté et signalé |
| Un équipement tombe en panne | L'équipe sait identifier l'impact et appliquer la procédure prévue |

Une exigence n'est pas considérée comme validée parce que la configuration semble correcte. Elle doit être testée dans un environnement autorisé.


# 4. Architecture 1 — Réseau physique de référence

## 4.1. Schéma physique général

Pour une petite entreprise, une architecture simple peut suffire : un pare-feu professionnel, un commutateur administrable, des points d'accès et un NAS.

```text
                         INTERNET
                            |
                     +--------------+
                     | FOURNISSEUR  |
                     | D'ACCÈS      |
                     +--------------+
                            |
                            |
                     +--------------+
                     | PARE-FEU     |
                     | ROUTEUR      |
                     | NAT / VPN    |
                     | VLAN / ACL   |
                     +--------------+
                            |
                     Lien Ethernet
                     TRUNK 802.1Q
                            |
                     +--------------+
                     | COMMUTATEUR  |
                     | ADMINISTRABLE|
                     | VLAN / STP   |
                     | POE si besoin|
                     +--------------+
                       |    |    |   \
                       |    |    |    \
                       |    |    |     +------ NAS / SERVEUR
                       |    |    |
                       |    |    +------------ IMPRIMANTE(S)
                       |    |
                       |    +----------------- POSTES FILAIRES
                       |
                       +---------------------- POINTS D'ACCÈS
                                                    |
                              +---------------------+------------------+
                              |                                        |
                        WI-FI PRO                              WI-FI INVITÉS
                              |                                        |
                     Ordinateurs autorisés                    Appareils invités
```

Le lien entre le pare-feu et le commutateur transporte plusieurs VLAN dans cette architecture. Il doit donc être configuré en cohérence avec les VLAN créés sur les deux équipements.

Le NAS et les imprimantes ne doivent pas être raccordés n'importe où sans vérifier le rôle du port, le VLAN et la politique de filtrage.

## 4.2. Rôle du pare-feu

Le pare-feu est le point central de contrôle de l'architecture.

Dans la conception de référence, il assure :

- La passerelle des différents VLAN.
- Le routage inter-VLAN.
- Le filtrage entre les zones.
- La protection des connexions vers Internet.
- Le NAT pour les sorties IPv4 lorsque nécessaire.
- Le VPN, si un accès distant est prévu et correctement administré.
- La journalisation des événements importants.
- Le contrôle des services accessibles depuis l'extérieur.

Le pare-feu doit être dimensionné en fonction du débit Internet, du trafic inter-VLAN et des fonctions de sécurité réellement utilisées.

Un débit annoncé par le constructeur avec un filtrage minimal ne représente pas forcément le débit obtenu lorsque l'inspection approfondie, le VPN ou d'autres fonctions sont activés.

## 4.3. Rôle du commutateur administrable

Le commutateur relie les terminaux aux services réseau.

Il doit prendre en charge les fonctions nécessaires au projet, notamment :

- VLAN 802.1Q.
- Ports d'accès.
- Trunks.
- Contrôle des ports.
- Spanning Tree.
- Gestion sécurisée.
- Journaux et compteurs utiles.
- PoE si les points d'accès ou téléphones en ont besoin.

Le commutateur est un équipement de couche 2 dans cette conception. Le pare-feu assure le routage entre les VLAN.

Cette séparation réduit la complexité de la solution, mais elle implique que le pare-feu doit pouvoir traiter le trafic inter-VLAN attendu.

## 4.4. Rôle du NAS

Le NAS fournit un espace de stockage partagé.

Il ne doit pas être considéré comme sécurisé uniquement parce qu'il se trouve derrière le pare-feu.

Il faut également :

- Créer des comptes individuels ou utiliser une authentification centralisée adaptée.
- Définir les droits de lecture et d'écriture.
- Désactiver les services inutiles.
- Protéger son interface d'administration.
- Effectuer les mises à jour.
- Sauvegarder les données sur une destination distincte.
- Tester la restauration des fichiers.
- Contrôler l'accès depuis les réseaux visiteurs et les équipements non autorisés.

Un NAS qui contient les fichiers de l'entreprise constitue une ressource critique même si l'infrastructure ne comprend qu'une vingtaine d'utilisateurs.


# 5. Architecture 2 — Architecture logique par VLAN

## 5.1. Plan de segmentation proposé

Pour ce challenge, le réseau est divisé en zones logiques.

| VLAN | Nom | Usage |
|---:|---|---|
| 10 | BUREAU | Postes professionnels |
| 20 | ADMIN-IT | Poste(s) d'administration autorisés |
| 30 | SERVEURS | NAS, serveur interne et services locaux |
| 40 | IMPRIMANTES-IOT | Imprimantes et équipements limités |
| 50 | VOIX | Téléphones IP, si utilisés |
| 60 | INVITES | Wi-Fi visiteurs |
| 70 | WIFI-PRO | Wi-Fi des utilisateurs professionnels |
| 90 | MGMT | Interfaces de gestion des équipements |
| 999 | PARKING | VLAN réservé aux ports inutilisés et aux besoins de configuration documentés |

Le VLAN 50 est facultatif si l'entreprise n'utilise pas de téléphones IP. Un réseau VLAN doit correspondre à un besoin réel ; il ne faut pas ajouter des segments uniquement pour rendre l'architecture plus compliquée.

Le VLAN 20 et le VLAN 90 ont des rôles différents :

- **VLAN 20 :** terminal depuis lequel l'administrateur effectue les opérations de gestion.
- **VLAN 90 :** interfaces de gestion du commutateur, des points d'accès et d'autres équipements.

Cette séparation réduit le risque qu'un poste ordinaire puisse atteindre directement les interfaces de gestion.

## 5.2. Schéma logique

```text
                           INTERNET
                              |
                       +--------------+
                       | PARE-FEU     |
                       | ROUTAGE      |
                       | FILTRAGE ACL |
                       +--------------+
                              |
                       Interfaces VLAN
                              |
       +----------------------+----------------------+
       |                      |                      |
       |                      |                      |
 VLAN 10                  VLAN 20                 VLAN 30
 BUREAU                   ADMIN-IT                SERVEURS
       |                      |                      |
 PC et portables       Poste autorisé          NAS / Services
       |                      |                      |
       |                      +----------+-----------+
       |                                 |
       |                          ADMINISTRATION
       |                                 |
       |                              VLAN 90
       |                             MGMT INFRA
       |
       +----------------------+----------------------+
                              |
                      +-------+--------+
                      |                |
                  VLAN 40          VLAN 50
               IMPRIMANTES-IOT       VOIX
                      |                |
                 Imprimantes      Téléphones IP
                 autorisées       si nécessaires


                  +---------------------------+
                  |                           |
               VLAN 70                     VLAN 60
              WIFI-PRO                    INVITÉS
                  |                           |
             Accès interne              Internet uniquement
             contrôlé                    Aucun accès interne
```

Le schéma représente les flux logiques attendus. La configuration effective doit inclure des règles de filtrage explicites sur le pare-feu.

## 5.3. Pourquoi ne pas conserver un réseau plat ?

Un réseau plat place des équipements de fonctions différentes dans un même segment de couche 2.

Cela peut simplifier une installation très élémentaire, mais entraîne plusieurs limites :

- Les équipements partagent le même domaine de diffusion.
- La séparation entre terminaux professionnels et invités devient difficile à assurer.
- Les périphériques vulnérables ont une visibilité excessive.
- Les politiques de filtrage entre catégories de terminaux sont limitées.
- Le dépannage devient plus difficile lorsque les rôles ne sont pas documentés.

La segmentation ne remplace pas la sécurité des postes, des comptes et des applications. Elle ajoute cependant des frontières techniques que l'on peut surveiller et contrôler.


# 6. Défi 2 — Plan d'adressage IPv4

## 6.1. Principes de conception

Le plan d'adressage doit être :

- Simple à comprendre.
- Sans chevauchement avec les autres réseaux de l'entreprise.
- Compatible avec les accès VPN éventuels.
- Facile à documenter.
- Suffisamment dimensionné pour la croissance prévue.
- Cohérent avec les VLAN et les règles de filtrage.

Le scénario utilise le bloc privé `10.50.0.0/16`, réparti en sous-réseaux `/24`.

Cette répartition simplifie l'apprentissage et permet d'ajouter des segments, mais un réseau `/24` n'est pas obligatoire pour tous les VLAN d'une petite entreprise. Dans un projet réel, les masques doivent être dimensionnés selon les besoins.

## 6.2. Plan IP de référence

| VLAN | Réseau | Passerelle | Fonction |
|---:|---|---|---|
| 10 | `10.50.10.0/24` | `10.50.10.1` | Postes filaires |
| 20 | `10.50.20.0/24` | `10.50.20.1` | Administration |
| 30 | `10.50.30.0/24` | `10.50.30.1` | NAS et serveurs |
| 40 | `10.50.40.0/24` | `10.50.40.1` | Imprimantes et IoT |
| 50 | `10.50.50.0/24` | `10.50.50.1` | Téléphonie IP |
| 60 | `10.50.60.0/24` | `10.50.60.1` | Invités |
| 70 | `10.50.70.0/24` | `10.50.70.1` | Wi-Fi professionnel |
| 90 | `10.50.90.0/24` | `10.50.90.1` | Gestion des équipements |

Les adresses de passerelle sont des conventions choisies pour l'exercice. Elles doivent correspondre aux interfaces VLAN du pare-feu dans la configuration finale.

## 6.3. Attribution des adresses

Une organisation indicative peut être utilisée :

| Plage | Utilisation proposée |
|---|---|
| `.1` | Passerelle du VLAN |
| `.2` à `.19` | Équipements ou services à adresse réservée |
| `.20` à `.49` | Serveurs ou périphériques à adresse documentée |
| `.50` à `.99` | Réserves et équipements particuliers |
| `.100` à `.239` | Plage DHCP indicative |
| `.240` à `.254` | Réserve d'adresses à documenter |

Cette convention n'est pas une norme. Il faut éviter les conflits entre adresses statiques, réservations DHCP et adresses attribuées dynamiquement.

## 6.4. Adresses indicatives des serveurs

Le VLAN 30 peut utiliser des adresses comme celles-ci :

| Adresse | Fonction |
|---|---|
| `10.50.30.10` | NAS |
| `10.50.30.20` | Serveur d'applications internes |
| `10.50.30.30` | Service de sauvegarde, si présent |
| `10.50.30.40` | Serveur DNS interne, si nécessaire |

Ces adresses sont illustratives. Une entreprise peut utiliser des services cloud au lieu d'héberger tous ces rôles localement.

Le plan réel doit préciser quelles fonctions existent réellement et quels serveurs sont responsables de chacune.

## 6.5. Exercice de calcul

Un PC possède les paramètres suivants :

```text
Adresse IPv4 : 10.50.10.25
Masque       : 255.255.255.0
Passerelle   : 10.50.10.1
DNS          : serveur défini par l'entreprise
```

Répondez aux questions suivantes :

1. Quel est le réseau IP du PC ?
2. Quelle est l'adresse de diffusion de ce réseau ?
3. Le PC peut-il communiquer directement avec `10.50.10.80` ?
4. Le PC peut-il communiquer directement avec `10.50.30.10` sans routeur ?
5. Quel rôle joue la passerelle ?
6. Que se passe-t-il si le masque configuré sur le poste est incorrect ?
7. Pourquoi un poste peut-il disposer d'une bonne adresse IP mais ne pas atteindre le NAS ?

### Correction

1. Le réseau est `10.50.10.0/24`.
2. L'adresse de diffusion est `10.50.10.255`.
3. Oui, `10.50.10.80` appartient au même sous-réseau.
4. Non, `10.50.30.10` appartient au VLAN 30, donc à un autre sous-réseau. Une fonction de routage est nécessaire.
5. La passerelle transmet les paquets destinés aux autres réseaux.
6. Le poste peut prendre de mauvaises décisions de routage et tenter une communication directe lorsqu'il devrait utiliser la passerelle, ou l'inverse.
7. Le routage, une ACL, le pare-feu du serveur, le service applicatif ou le chemin de retour peuvent être responsables.


# 7. Défi 3 — Configurer les VLAN et les ports

## 7.1. Créer les VLAN

La syntaxe exacte dépend de la plateforme. L'exemple suivant illustre une configuration Cisco IOS :

```text
vlan 10
 name BUREAU

vlan 20
 name ADMIN-IT

vlan 30
 name SERVEURS

vlan 40
 name IMPRIMANTES-IOT

vlan 50
 name VOIX

vlan 60
 name INVITES

vlan 70
 name WIFI-PRO

vlan 90
 name MGMT

vlan 999
 name PARKING
```

Le VLAN 50 peut être omis si l'entreprise n'utilise pas de téléphones IP ou si leur architecture est différente.

### Vérifications

```text
show vlan brief
show interfaces status
```

Vous devez confirmer que les VLAN existent et que leurs identifiants correspondent au plan documenté.

## 7.2. Configurer un port utilisateur

Exemple pour un poste de travail dans le VLAN 10 :

```text
interface GigabitEthernet1/0/5
 description PC-BUREAU-01
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
```

Ce port est destiné à un terminal final. PortFast et BPDU Guard doivent être appliqués selon la politique du réseau, uniquement sur les ports appropriés.

Ne réutilisez pas automatiquement cette configuration sur un lien entre commutateurs ou sur un port transportant plusieurs VLAN.

### Vérifications

```text
show interfaces GigabitEthernet1/0/5 switchport
show vlan brief
show spanning-tree interface GigabitEthernet1/0/5
```

Contrôlez également l'adresse IP reçue par le poste.

## 7.3. Configurer le port du NAS

Le NAS appartient au VLAN 30.

Exemple :

```text
interface GigabitEthernet1/0/12
 description NAS-NOVABUREAU
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 spanning-tree bpduguard enable
```

Avant d'appliquer cette configuration, vérifiez que le port est réellement destiné au NAS et non à un équipement dont le fonctionnement nécessite un trunk.

L'accès réseau au NAS doit ensuite être limité par le pare-feu, les règles de sécurité locales et les permissions sur les fichiers.

## 7.4. Configurer un port d'imprimante

Exemple :

```text
interface GigabitEthernet1/0/15
 description IMPRIMANTE-BUREAU
 switchport mode access
 switchport access vlan 40
 spanning-tree portfast
 spanning-tree bpduguard enable
```

L'imprimante reçoit une adresse du réseau `10.50.40.0/24`, si elle utilise DHCP dans ce scénario.

Les postes autorisés doivent être capables d'atteindre le service d'impression requis. Les connexions initiées par l'imprimante vers les réseaux utilisateurs doivent être limitées selon les capacités des équipements.

## 7.5. Configurer le trunk vers le pare-feu

Le lien vers le pare-feu transporte les VLAN utilisés dans l'architecture.

```text
interface GigabitEthernet1/0/24
 description TRUNK-VERS-PARE-FEU
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60,70,90
```

Cette liste constitue un exemple à adapter. Le VLAN 50 peut être absent si la voix n'est pas utilisée.

Le VLAN 999 est exclu de la liste dans cet exemple parce qu'il n'a pas besoin d'être transporté vers le pare-feu dans le scénario proposé.

Selon le commutateur, la configuration du VLAN natif et les commandes disponibles peuvent différer. La configuration des deux extrémités doit être cohérente.

### Vérifications

```text
show interfaces trunk
show interfaces GigabitEthernet1/0/24 switchport
show spanning-tree
```

Vérifiez :

- Les VLAN autorisés.
- Le mode trunk effectif.
- Le VLAN natif.
- La concordance avec le pare-feu.
- L'état des liens.
- Les événements STP.

Un trunk n'est pas un port que l'on active sans raison : il transporte plusieurs VLAN et doit être limité à ceux nécessaires.

## 7.6. Traiter les ports inutilisés

Exemple :

```text
interface range GigabitEthernet1/0/20-23
 description PORTS-INUTILISES
 switchport mode access
 switchport access vlan 999
 shutdown
```

Adaptez les numéros de port à la configuration réelle.

La désactivation des ports inutilisés réduit le risque de raccordement non autorisé. Le VLAN de parking ne remplace pas le contrôle physique ni l'authentification réseau lorsque celle-ci est requise.


# 8. Défi 4 — Configurer les passerelles et le routage

## 8.1. Architecture retenue

Le pare-feu est la passerelle des VLAN.

```text
              VLAN 10 : 10.50.10.0/24
                          |
              VLAN 20 : 10.50.20.0/24
                          |
              VLAN 30 : 10.50.30.0/24
                          |
              VLAN 40 : 10.50.40.0/24
                          |
              VLAN 60 : 10.50.60.0/24
                          |
              VLAN 70 : 10.50.70.0/24
                          |
              VLAN 90 : 10.50.90.0/24
                          |
                   TRUNK 802.1Q
                          |
                  +----------------+
                  | PARE-FEU       |
                  | Passerelles    |
                  | Routage IP     |
                  | ACL / POLITIQUES|
                  +----------------+
                          |
                       INTERNET
```

Chaque interface VLAN du pare-feu doit disposer de l'adresse correspondant à la passerelle du plan IP.

Exemple pour le VLAN 10 :

```text
Adresse de la passerelle : 10.50.10.1
Masque                  : 255.255.255.0
Réseau                  : 10.50.10.0/24
```

Pour le VLAN 30, la passerelle sera `10.50.30.1`.

La configuration exacte dépend du fabricant : certains équipements utilisent des interfaces VLAN, d'autres des sous-interfaces et des objets de configuration spécifiques.

## 8.2. Pourquoi utiliser le pare-feu comme passerelle ?

Pour une petite entreprise, cette architecture présente plusieurs avantages :

- Une centralisation du routage inter-VLAN.
- Une politique de filtrage plus facile à retrouver.
- Une visibilité sur les flux entre les zones.
- Une administration relativement simple.
- Un nombre limité d'équipements.

Elle impose toutefois des contraintes :

- Le pare-feu doit traiter les communications internes.
- Un trafic important entre postes et NAS peut consommer des ressources.
- Le pare-feu constitue un point unique de panne si aucun mécanisme de secours n'existe.
- Une règle trop restrictive peut interrompre une application métier.

Le débit inter-VLAN et les besoins de disponibilité doivent donc être évalués avant de retenir cette architecture en production.

## 8.3. Route par défaut

Le pare-feu doit disposer d'une route appropriée vers le fournisseur d'accès et d'une politique autorisant les sorties nécessaires.

Il doit également appliquer la traduction d'adresses ou le mécanisme d'accès WAN requis par le réseau.

Ne copiez pas un exemple de route générique dans un équipement sans vérifier :

- Les interfaces réellement présentes.
- Les adresses de transit.
- Le prochain saut.
- Les routes de retour.
- Les règles de filtrage.
- Le fonctionnement du NAT.
- Les éventuelles dépendances au fournisseur.

## 8.4. Tests de routage

Depuis un poste du VLAN 10 :

1. Vérifier l'adresse IP et la passerelle.
2. Tester l'accès à une ressource du même sous-réseau.
3. Tester une ressource interne autorisée.
4. Tester une destination interne interdite.
5. Tester un service Internet.
6. Vérifier la résolution DNS.
7. Contrôler les journaux du pare-feu en cas d'échec.

Le résultat attendu est déterminé par la politique. Une communication bloquée peut être un comportement correct, et non un incident.


# 9. Défi 5 — DHCP et DNS

## 9.1. DHCP

Le DHCP fournit automatiquement la configuration IP aux terminaux.

Dans cette architecture, le pare-feu peut assurer le service DHCP s'il dispose des fonctionnalités adaptées. Cela évite d'ajouter un serveur uniquement pour cette fonction.

Une autre solution consiste à utiliser un serveur DHCP dédié, auquel cas il faudra vérifier le relais DHCP lorsque les clients appartiennent à des réseaux différents.

### Exemple d'étendue DHCP

Pour le VLAN 10 :

| Paramètre | Valeur indicative |
|---|---|
| Réseau | `10.50.10.0/24` |
| Passerelle | `10.50.10.1` |
| Plage d'attribution | `10.50.10.100` à `10.50.10.239` |
| DNS | Résolveurs validés par l'entreprise |
| Durée du bail | Selon la politique et la mobilité des clients |
| Exclusions | Adresses réservées et équipements statiques documentés |

Les autres VLAN doivent posséder des étendues adaptées lorsque leurs équipements utilisent DHCP.

Les interfaces de gestion, le NAS, les imprimantes et les services critiques peuvent utiliser des adresses statiques ou des réservations DHCP documentées.

### Vérification sous Windows

```powershell
ipconfig /all
ipconfig /release
ipconfig /renew
```

### Vérification sous Linux

```bash
ip addr
ip route
resolvectl status
```

Les commandes exactes peuvent varier suivant le système et son gestionnaire réseau.

## 9.2. Dépannage DHCP

Si un poste reçoit une mauvaise adresse :

1. Vérifier le VLAN du port.
2. Vérifier l'adresse obtenue.
3. Vérifier le serveur DHCP qui a répondu.
4. Vérifier que la bonne étendue correspond au VLAN.
5. Vérifier les trunks.
6. Vérifier le relais DHCP si un serveur externe est utilisé.
7. Rechercher les configurations DHCP incorrectes ou les serveurs non autorisés.

Un poste qui reçoit une adresse d'un sous-réseau inattendu peut signaler une erreur de VLAN ou un serveur DHCP indésirable.

## 9.3. DNS

Le DNS permet aux postes d'utiliser des noms plutôt que de dépendre uniquement des adresses IP.

Une petite entreprise peut utiliser les services DNS de son fournisseur ou un résolveur approuvé. Si des noms internes sont nécessaires, elle peut également déployer un DNS interne ou un service de nommage adapté.

Le choix dépend notamment :

- Du domaine de l'entreprise.
- Des applications locales.
- De l'authentification.
- Des besoins de résolution interne.
- De la stratégie de filtrage.
- Des services hébergés dans le cloud.

### Vérifications

```powershell
nslookup nom-du-service
```

Ou sous Linux :

```bash
dig nom-du-service
```

Les noms d'exemple doivent être remplacés par des noms réellement configurés.

Vérifiez :

- Le serveur DNS utilisé.
- Le nom demandé.
- La réponse obtenue.
- Les enregistrements retournés.
- L'accessibilité du service.
- Les éventuelles différences entre les clients.

Si l'accès par IP fonctionne mais l'accès par nom échoue, examinez la résolution DNS avant de modifier les routes ou le VLAN.


# 10. Défi 6 — Matrice de sécurité

## 10.1. Principes

L'entreprise doit autoriser les communications nécessaires sans permettre des accès généraux entre toutes les zones.

La politique de référence repose sur les principes suivants :

1. Le trafic inter-VLAN est contrôlé.
2. Les communications non documentées sont refusées par défaut.
3. Les postes utilisateurs ne peuvent pas administrer les équipements réseau.
4. Le Wi-Fi invités n'accède pas aux ressources internes.
5. Les imprimantes sont accessibles uniquement pour les fonctions nécessaires.
6. Le NAS n'est accessible que depuis les utilisateurs autorisés.
7. Les services de gestion du pare-feu ne sont pas disponibles depuis Internet ou les VLAN ordinaires, sauf architecture spécifique fortement contrôlée.
8. Les règles sont testées après chaque modification.

## 10.2. Matrice de flux proposée

| Source | Destination | Politique | Justification |
|---|---|---|---|
| VLAN 10 BUREAU | Internet | Autorisé selon politique | Travail quotidien |
| VLAN 10 BUREAU | VLAN 30 SERVEURS | Autorisé sous condition | Applications et fichiers nécessaires |
| VLAN 10 BUREAU | VLAN 40 IMPRIMANTES-IOT | Autorisé sous condition | Impression |
| VLAN 10 BUREAU | VLAN 90 MGMT | Refusé | Protéger l'administration |
| VLAN 20 ADMIN-IT | VLAN 90 MGMT | Autorisé sous condition | Administration |
| VLAN 20 ADMIN-IT | VLAN 30 SERVEURS | Autorisé sous condition | Gestion des serveurs |
| VLAN 30 SERVEURS | VLAN 10 BUREAU | Refusé par défaut | Limiter les connexions initiées par les serveurs |
| VLAN 40 IMPRIMANTES-IOT | VLAN 10 BUREAU | Refusé par défaut | Limiter les connexions initiées par les périphériques |
| VLAN 60 INVITES | Réseaux internes | Refusé | Isoler les visiteurs |
| VLAN 60 INVITES | Internet | Autorisé selon politique | Accès invité |
| VLAN 70 WIFI-PRO | VLAN 30 SERVEURS | Autorisé sous condition | Applications nécessaires |
| VLAN 70 WIFI-PRO | VLAN 90 MGMT | Refusé | Protéger les interfaces de gestion |
| VLAN 90 MGMT | Réseaux utilisateurs | Refusé par défaut | Limiter l'accès au plan de gestion |
| VLAN 10 BUREAU | Administration pare-feu | Refusé | Limiter les sources de gestion |
| VLAN 20 ADMIN-IT | Administration pare-feu | Autorisé sous condition | Administration contrôlée |

La matrice doit être adaptée aux applications réellement utilisées. Les flux retour d'une connexion initiée et autorisée peuvent être suivis automatiquement par un pare-feu à état, mais les règles précises dépendent du produit.

## 10.3. Limiter l'accès au NAS

Le NAS contient potentiellement les documents de toute l'entreprise.

Les contrôles doivent comprendre :

- L'accès depuis les VLAN autorisés.
- L'authentification des utilisateurs.
- Les permissions par dossier.
- La limitation des interfaces d'administration.
- La désactivation des protocoles inutiles.
- Les mises à jour.
- La journalisation lorsque disponible.
- Des sauvegardes séparées du stockage principal.

Le fait de bloquer le trafic provenant du Wi-Fi invités est nécessaire, mais insuffisant si tous les utilisateurs internes disposent ensuite des mêmes permissions sur les dossiers.

## 10.4. Limiter l'accès aux imprimantes

L'imprimante doit être accessible pour les services nécessaires et ne doit pas devenir une porte d'entrée vers les autres postes.

La politique devrait :

- Autoriser l'impression depuis les postes prévus.
- Limiter l'interface d'administration à une source autorisée.
- Désactiver les protocoles d'impression inutilisés.
- Restreindre les connexions initiées par l'imprimante vers les autres réseaux.
- Modifier les identifiants par défaut.
- Installer les mises à jour disponibles.

Les ports doivent être définis en fonction des protocoles effectivement utilisés et de la documentation de l'imprimante. Ne choisissez pas les ports uniquement à partir d'une liste générique.

## 10.5. Tester les règles

Chaque règle importante doit avoir deux catégories de tests :

**Test positif :** une communication autorisée fonctionne.

**Test négatif :** une communication interdite échoue.

Exemple :

| Test | Résultat attendu |
|---|---|
| Employé vers application autorisée | Connexion réussie |
| Employé vers interface de gestion du commutateur | Connexion refusée |
| Administrateur autorisé vers commutateur en SSH | Connexion réussie |
| Visiteur vers NAS | Connexion refusée |
| Visiteur vers Internet | Connexion conforme à la politique |
| Poste autorisé vers imprimante | Impression fonctionnelle |

Un refus doit être interprété à partir des journaux et du contexte. Un service arrêté peut produire un résultat apparent similaire à une règle de filtrage.


# 11. Défi 7 — Concevoir le Wi-Fi

## 11.1. SSID de référence

| SSID | Usage | VLAN |
|---|---|---:|
| `NOVABUREAU-PRO` | Utilisateurs professionnels | 70 |
| `NOVABUREAU-GUEST` | Visiteurs | 60 |

Dans ce scénario, le Wi-Fi professionnel utilise le VLAN 70 et les postes filaires utilisent le VLAN 10.

Cette séparation est un choix d'architecture. Si le matériel ne permet pas les fonctionnalités nécessaires, la conception doit être adaptée sans compromettre l'isolement des visiteurs.

## 11.2. Wi-Fi professionnel

Le réseau Wi-Fi professionnel doit utiliser une méthode d'authentification adaptée au contexte.

Lorsque c'est possible et correctement pris en charge, une authentification fondée sur 802.1X et des identifiants individuels, avec un service RADIUS, constitue une option d'entreprise.

Pour une petite structure, une solution plus simple peut être retenue si le matériel ou les moyens d'administration sont limités. Dans tous les cas :

- Utiliser un chiffrement moderne pris en charge par les terminaux.
- Éviter les mots de passe faciles à deviner.
- Limiter le partage non contrôlé des identifiants.
- Révoquer les accès qui ne sont plus nécessaires.
- Installer les mises à jour.
- Séparer les visiteurs du réseau professionnel.
- Contrôler l'accès aux interfaces de gestion des points d'accès.

## 11.3. Wi-Fi visiteurs

Le réseau visiteurs doit donner accès à Internet et non au réseau privé de l'entreprise.

Schéma logique :

```text
                   POINT D'ACCÈS WI-FI
                           |
                    TRUNK 802.1Q
                           |
                    COMMUTATEUR
                           |
                       PARE-FEU
                           |
                 +---------+---------+
                 |                   |
              VLAN 70             VLAN 60
              WI-FI-PRO           INVITÉS
                 |                   |
           Services autorisés       Internet
                                    uniquement
                                    |
                           Refus des réseaux internes
```

Le Wi-Fi invités doit être isolé par la configuration des VLAN, le routage, les règles de filtrage et, lorsque nécessaire, l'isolation entre clients.

Un portail captif peut faciliter la gestion des visiteurs, mais il ne remplace pas les règles de sécurité réseau.

## 11.4. Tests Wi-Fi

Effectuez les tests suivants :

1. Un utilisateur autorisé s'authentifie.
2. Un client reçoit une adresse IP du bon sous-réseau.
3. L'accès Internet fonctionne.
4. L'accès à une application interne autorisée fonctionne.
5. L'accès au NAS depuis un visiteur est refusé.
6. Les interfaces de gestion sont inaccessibles depuis les réseaux utilisateurs.
7. La connexion reste stable dans les zones de travail.
8. Les changements de point d'accès ne provoquent pas de coupures excessives.
9. Les journaux permettent de diagnostiquer un échec d'authentification.

Une bonne couverture radio ne garantit pas que la résolution DNS, le routage ou les applications fonctionnent.


# 12. Défi 8 — Sécuriser l'administration

## 12.1. Administration centralisée

Le réseau ne doit pas être administrable indistinctement depuis tous les postes.

Dans cette architecture :

- Les postes standards utilisent le VLAN 10.
- Le poste d'administration utilise le VLAN 20.
- Les interfaces de gestion des équipements appartiennent au VLAN 90.
- Seules les sources autorisées peuvent atteindre les interfaces de gestion.
- L'accès administratif depuis Internet est bloqué sauf architecture spécifique et sécurisée.
- Les changements de configuration sont consignés.

Schéma :

```text
        POSTES UTILISATEURS
              VLAN 10
                 |
                 X
                 |
          ACCÈS MGMT REFUSÉ


       POSTE D'ADMINISTRATION
              VLAN 20
                 |
          Règles d'accès
          explicitement prévues
                 |
                 v
          VLAN 90 MGMT
                 |
        +--------+--------+
        |        |        |
    Commutateur Pare-feu Points d'accès
```

## 12.2. Protocoles de gestion

Privilégiez les moyens d'administration sécurisés pris en charge par l'équipement :

- SSH plutôt que Telnet.
- HTTPS avec une gestion appropriée des certificats.
- SNMPv3 lorsque SNMP est utilisé et correctement configuré.
- Des identifiants individuels ou une authentification centralisée.
- Des rôles adaptés aux responsabilités.
- La journalisation des opérations importantes.

Désactivez les services de gestion inutiles.

## 12.3. Gestion des secrets

Les secrets ne doivent pas être copiés dans un document partagé en clair.

Prévoyez :

- Un stockage protégé.
- Un accès limité aux personnes autorisées.
- Une procédure de rotation.
- Un retrait des accès en cas de départ ou de changement de fonction.
- Une sauvegarde protégée des configurations contenant potentiellement des informations sensibles.

Ne placez jamais les mots de passe réels dans le fichier Markdown du challenge.


# 13. Défi 9 — Sauvegarde et protection des données

## 13.1. Le risque

Le NAS peut contenir les fichiers comptables, les documents commerciaux, les contrats et les dossiers de travail.

Une panne matérielle n'est pas le seul risque. Les fichiers peuvent également être supprimés par erreur, chiffrés par un logiciel malveillant ou rendus indisponibles par la compromission d'un compte disposant de trop de droits.

La sauvegarde doit donc être conçue indépendamment du simple stockage principal.

## 13.2. Architecture de sauvegarde de référence

```text
                 POSTES UTILISATEURS
                         |
                         v
                  +--------------+
                  | NAS PRINCIPAL|
                  | FICHIERS     |
                  +--------------+
                         |
                 Sauvegardes planifiées
                         |
                         v
                  +--------------+
                  | CIBLE DE     |
                  | SAUVEGARDE   |
                  +--------------+
                         |
            +------------+-------------+
            |                          |
            v                          v
      Copie séparée             Copie hors site
      avec accès limité         ou service distant
```

La cible de sauvegarde ne doit pas être accessible en écriture par tous les comptes du réseau.

Une copie toujours accessible avec les mêmes identifiants que le NAS principal peut être compromise en même temps que les données d'origine.

## 13.3. Politique de sauvegarde

Le dossier doit définir :

- La fréquence des sauvegardes.
- Les données concernées.
- La durée de conservation.
- La responsabilité de vérifier les résultats.
- La protection des copies.
- La procédure de restauration.
- Les objectifs de perte de données acceptable.
- Les délais cibles de remise en service.

Les fréquences et durées de conservation doivent être choisies selon les besoins réels de l'entreprise. Une valeur universelle n'est pas adaptée à toutes les activités.

## 13.4. Exercice de restauration

Vous devez démontrer la restauration d'un fichier supprimé volontairement dans un environnement de test.

Procédure :

1. Créer un fichier de test.
2. Vérifier qu'il est inclus dans la sauvegarde.
3. Supprimer le fichier de test selon la procédure de l'exercice.
4. Restaurer la version attendue.
5. Vérifier son contenu.
6. Mesurer le temps nécessaire.
7. Consigner les résultats.

Une sauvegarde dont la restauration n'a jamais été testée ne doit pas être considérée comme totalement validée.


# 14. Défi 10 — Disponibilité et continuité

## 14.1. Identifier les points uniques de panne

Dans une petite entreprise, les principaux points de défaillance peuvent être :

- Le pare-feu unique.
- Le commutateur unique.
- Le fournisseur d'accès Internet.
- Le NAS unique.
- Une alimentation électrique commune.
- L'unique point d'accès couvrant un espace de travail.
- Une sauvegarde stockée sur le même équipement que les données d'origine.

Le niveau de redondance doit être déterminé à partir du coût d'une interruption.

## 14.2. Architecture de départ

```text
                 INTERNET
                    |
               [ PARE-FEU ]
                    |
              [ SWITCH MANAGÉ ]
                /     |      \
               /      |       \
              v       v        v
             PC      NAS     POINTS D'ACCÈS
                              WI-FI
```

Cette architecture est simple et économique, mais le pare-feu et le commutateur sont des points uniques de panne.

## 14.3. Architecture améliorée

Selon le budget, l'entreprise peut envisager :

- Un pare-feu de remplacement préconfiguré.
- Une configuration sauvegardée et une procédure de remplacement rapide.
- Un onduleur adapté aux équipements critiques.
- Une connexion Internet de secours si l'activité le justifie.
- Un commutateur de remplacement disponible.
- Des sauvegardes hors site.
- Un point d'accès supplémentaire pour les zones critiques.

```text
                    +--------------------+
                    | INTERNET PRINCIPAL |
                    +--------------------+
                              |
                              |
                    +--------------------+
                    | PARE-FEU PRINCIPAL |
                    +--------------------+
                              |
                    +--------------------+
                    | SWITCH PRINCIPAL   |
                    +--------------------+
                       |      |      |
                       v      v      v
                      PC     NAS     WI-FI
                              |
                              v
                    SAUVEGARDE SÉPARÉE

             Éléments de secours documentés :
             - Pare-feu de remplacement
             - Configuration sauvegardée
             - Accès Internet alternatif, si requis
             - Procédure de restauration
```

Cette seconde représentation n'implique pas une bascule automatique. Elle décrit une stratégie de reprise possible pour une petite organisation.

## 14.4. Choisir les investissements selon le risque

Avant d'acheter du matériel redondant, répondez à ces questions :

- Combien coûte une heure d'interruption ?
- Quels processus peuvent continuer sans Internet ?
- Les données critiques sont-elles sauvegardées ailleurs ?
- Peut-on remplacer le pare-feu en quelques heures ?
- Le fournisseur d'accès propose-t-il une solution de secours ?
- Les utilisateurs peuvent-ils continuer à travailler depuis une connexion alternative ?
- Quel délai de remise en service l'entreprise exige-t-elle ?

Un équipement de secours non testé peut être aussi peu fiable qu'une procédure inexistante.


# 15. Défi 11 — Supervision et documentation

## 15.1. Éléments à surveiller

| Élément | Indicateurs |
|---|---|
| Pare-feu | Disponibilité, charge, erreurs et événements de sécurité |
| Commutateur | État des ports, erreurs, saturation, changements STP |
| Wi-Fi | Disponibilité, clients, authentifications et qualité radio |
| NAS | Espace libre, état des disques, disponibilité et alertes |
| Sauvegardes | Succès, échecs, taille et résultats des restaurations |
| DHCP | Disponibilité et utilisation des plages |
| DNS | Disponibilité et résultats des requêtes |
| Internet | Disponibilité, latence et perte de paquets |
| Onduleur | Charge, autonomie et événements de batterie |

Le niveau de supervision doit rester exploitable par une petite équipe. L'important est d'identifier rapidement les pannes qui affectent les utilisateurs et les données.

## 15.2. Journaux à examiner

Les événements importants incluent :

- Échec de connexion administrative.
- Modification de configuration.
- Perte du lien Internet.
- Changement de topologie.
- Échec d'authentification Wi-Fi.
- Refus d'accès significatif.
- Échec de sauvegarde.
- Alerte de stockage.
- Indisponibilité du NAS.

Les journaux doivent être protégés contre les modifications non autorisées et conservés selon une politique définie.

## 15.3. Documentation minimale à tenir à jour

L'entreprise doit conserver :

1. Un schéma physique.
2. Un schéma logique.
3. Un inventaire des équipements.
4. Le plan de VLAN.
5. Le plan IP.
6. Le tableau des adresses réservées.
7. La matrice des flux.
8. Les informations de gestion protégées.
9. Les sauvegardes des configurations.
10. Les procédures de restauration et de dépannage.
11. L'historique des changements.
12. La liste des contacts techniques.

Une documentation utile décrit l'état réel du réseau, pas seulement la configuration initialement prévue.


# 16. Défi 12 — Dépannage avec le modèle OSI

Le modèle OSI aide à organiser les vérifications. Il ne faut pas l'utiliser comme une liste rigide dans laquelle il serait toujours obligatoire de commencer à la couche 1.

L'investigation doit partir du symptôme et des éléments disponibles.

| Couche | Nom | Exemples de contrôles |
|---:|---|---|
| 7 | Application | État du service, authentification, réponse de l'application |
| 6 | Présentation | Certificats, chiffrement, encodage |
| 5 | Session | État et maintien de session |
| 4 | Transport | TCP/UDP, port, établissement de connexion |
| 3 | Réseau | Adresse IP, masque, route, passerelle, filtrage |
| 2 | Liaison | VLAN, MAC, trunk, ARP, STP |
| 1 | Physique | Câble, fibre, alimentation, lien et signal radio |

## 16.1. Méthode de diagnostic

Pour chaque incident :

1. Décrire le symptôme et les utilisateurs concernés.
2. Déterminer la destination et le service attendus.
3. Vérifier si l'incident est généralisé ou limité à un équipement.
4. Examiner les changements récents.
5. Contrôler la couche la plus directement liée au symptôme.
6. Vérifier les dépendances de routage et de filtrage.
7. Examiner les journaux.
8. Tester le service avec le protocole approprié.
9. Effectuer une modification à la fois.
10. Réaliser des tests de non-régression.
11. Documenter la cause démontrée et les corrections.

Ne désactivez pas globalement le pare-feu pour « vérifier si cela fonctionne ». Cette méthode peut exposer les ressources et ne permet pas d'identifier proprement la cause.


# 17. Scénarios de dépannage

## Scénario A — Aucun poste ne peut accéder à Internet

### Symptôme

Les utilisateurs indiquent que leurs applications Internet ne répondent plus.

### Hypothèses

- Coupure du fournisseur d'accès.
- Pare-feu indisponible.
- Mauvaise route par défaut.
- Problème de DNS.
- Erreur de NAT.
- Règles de filtrage trop restrictives.
- Lien entre le pare-feu et le commutateur en panne.
- Problème d'adresse IP sur les postes.

### Démarche

1. Vérifier si tous les VLAN sont concernés.
2. Contrôler l'état du lien WAN.
3. Vérifier l'état du pare-feu.
4. Tester la passerelle locale.
5. Tester une adresse externe autorisée.
6. Tester une résolution DNS.
7. Vérifier les routes et la politique de sortie.
8. Examiner les journaux du pare-feu.
9. Confirmer si le problème concerne la connectivité IP ou uniquement les noms DNS.

### Preuve attendue

Vous devez identifier à quel point du chemin le trafic cesse de fonctionner.

Le fait qu'une page Web échoue ne prouve pas que la connexion Internet entière est indisponible : un problème DNS ou applicatif peut provoquer un symptôme similaire.


## Scénario B — Un seul poste n'a pas accès au réseau

### Hypothèses

- Câble ou carte réseau.
- Port désactivé.
- VLAN incorrect.
- Configuration IP incorrecte.
- Conflit d'adresses.
- Pare-feu local.
- Problème de pilote.
- Authentification réseau échouée.

### Démarche

1. Comparer avec un poste fonctionnel.
2. Vérifier le lien physique.
3. Vérifier l'adresse IP, le masque, la passerelle et le DNS.
4. Vérifier le VLAN du port.
5. Examiner les journaux du port et les éventuelles protections.
6. Tester la passerelle.
7. Tester le service nécessaire.
8. Corriger uniquement la cause établie.

Ne réinstallez pas le système d'exploitation avant d'avoir éliminé les causes de configuration et de connectivité.


## Scénario C — Les utilisateurs ne peuvent plus imprimer

### Hypothèses

- Imprimante hors ligne.
- Adresse IP modifiée.
- Port du commutateur mal configuré.
- VLAN incorrect.
- Règle inter-VLAN trop restrictive.
- Service d'impression arrêté.
- File d'attente bloquée.
- Pilote ou configuration du poste incorrect.

### Démarche

1. Vérifier l'état de l'imprimante.
2. Contrôler son adresse IP.
3. Vérifier son VLAN.
4. Tester l'accès au service d'impression utilisé.
5. Examiner les règles entre VLAN 10 et VLAN 40.
6. Vérifier le service d'impression et le poste.
7. Comparer les résultats entre un poste fonctionnel et un poste en échec.
8. Tester une impression après correction.

Un ping réussi vers l'imprimante ne prouve pas que le service d'impression fonctionne.


## Scénario D — Le NAS est visible, mais les dossiers sont inaccessibles

### Hypothèses

- Permissions incorrectes.
- Problème d'authentification.
- Protocole de partage bloqué.
- Compte expiré ou désactivé.
- Service de fichiers indisponible.
- Mauvais nom DNS.
- Règle de sécurité trop restrictive.

### Démarche

1. Vérifier l'adresse du NAS.
2. Tester la résolution DNS.
3. Vérifier le service de partage utilisé.
4. Examiner les journaux d'authentification.
5. Contrôler les permissions sur le partage et les fichiers.
6. Comparer avec un compte autorisé de test.
7. Ne pas contourner les permissions en donnant des droits administratifs à tous les utilisateurs.

Le diagnostic doit distinguer une panne de réseau d'un refus d'accès au niveau des permissions.


## Scénario E — Un visiteur accède à une ressource interne

### Gravité

Élevée, car le principe d'isolement n'est pas respecté.

### Hypothèses

- Mauvais VLAN affecté au SSID invité.
- VLAN invités autorisé sur un chemin non prévu.
- Règles de pare-feu trop permissives.
- Route alternative.
- Politiques IPv4 et IPv6 incohérentes.
- Isolation des clients incorrecte.
- Interface de gestion exposée à un réseau trop large.

### Démarche

1. Vérifier l'adresse IP du visiteur.
2. Identifier la ressource atteinte.
3. Relever les protocoles et les ports utilisés.
4. Examiner les journaux et règles de filtrage.
5. Vérifier le VLAN du SSID.
6. Contrôler les routes et les politiques IPv4/IPv6.
7. Corriger l'affectation ou la règle au bon point de contrôle.
8. Vérifier qu'Internet fonctionne encore.
9. Tester plusieurs ressources internes représentatives.

Ne laissez pas l'accès interne ouvert sous prétexte que le Wi-Fi invités fonctionne mieux ainsi.


## Scénario F — Le réseau est lent

### Hypothèses

- Lien saturé.
- Commutateur insuffisant.
- Erreurs physiques.
- Wi-Fi surchargé.
- Interférences radio.
- NAS saturé.
- Sauvegarde exécutée pendant les heures de travail.
- Problème applicatif.
- Pare-feu sous-dimensionné.

### Démarche

1. Déterminer si tous les utilisateurs sont concernés.
2. Comparer Ethernet et Wi-Fi.
3. Contrôler les compteurs d'interface.
4. Mesurer le débit.
5. Vérifier l'utilisation du NAS.
6. Examiner l'utilisation CPU et mémoire du pare-feu.
7. Identifier les périodes d'activité élevée.
8. Observer les retransmissions éventuelles dans une capture.
9. Mesurer avant et après toute modification.

La lenteur est un symptôme. Elle n'indique pas à elle seule l'emplacement de la cause.


# 18. Défi 13 — Analyse avec Wireshark

Wireshark permet d'examiner les paquets visibles depuis un point de capture.

Il faut d'abord identifier ce que l'interface de capture peut observer. Une capture sur le PC n'expose pas nécessairement tout le trafic du réseau.

## 18.1. Filtres de base

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

### TCP SYN sans ACK

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

### Adresse IPv4 spécifique

```text
ip.addr == 10.50.30.10
```

### Trafic entre un poste et le NAS

```text
ip.addr == 10.50.10.25 && ip.addr == 10.50.30.10
```

### Port TCP spécifique

```text
tcp.port == 443
```

Ces expressions sont des filtres d'affichage Wireshark. Les filtres de capture utilisent une syntaxe différente.

## 18.2. Exercice DHCP

1. Lancer une capture sur le poste de test.
2. Renouveler l'adresse IP.
3. Rechercher les échanges DHCP visibles.
4. Identifier le serveur ayant répondu.
5. Vérifier le sous-réseau attribué.
6. Comparer les paramètres reçus avec le plan IP.

Lorsqu'ils sont visibles, les échanges peuvent comprendre Discover, Offer, Request et ACK.

Un DHCP incorrect peut provenir d'une étendue mal configurée, d'une mauvaise affectation de VLAN ou d'un serveur non autorisé.

## 18.3. Exercice DNS

1. Capturer une requête pour un nom connu.
2. Identifier le serveur DNS utilisé.
3. Examiner la réponse.
4. Vérifier le code de réponse.
5. Comparer l'adresse obtenue à celle attendue.
6. Effectuer un test similaire avec un nom qui ne doit pas exister.

## 18.4. Exercice TCP

Pour un service de test :

1. Identifier le SYN envoyé par le client.
2. Rechercher le SYN-ACK du serveur.
3. Rechercher l'ACK du client.
4. Vérifier si l'échange se poursuit.
5. Observer les retransmissions ou les réinitialisations.

Si le SYN apparaît dans la capture client mais qu'aucune réponse n'est visible, il faut examiner le chemin réseau et les journaux des points de contrôle avant de conclure.


# 19. Défi 14 — Sécurité de couche 2

## 19.1. Protections à étudier

Selon les fonctionnalités disponibles, évaluez :

- La désactivation des ports inutilisés.
- Port security.
- BPDU Guard sur les ports d'accès appropriés.
- DHCP snooping.
- Dynamic ARP Inspection.
- La limitation des trunks.
- La désactivation des fonctions de négociation de trunk non nécessaires.
- La surveillance de STP.
- Le contrôle des événements de port.

Ces fonctions doivent être adaptées à la plateforme et à la topologie. Une protection mal configurée peut bloquer des équipements légitimes.

## 19.2. Port security

Cette fonction peut limiter les adresses MAC autorisées sur certains ports.

Elle peut être pertinente sur des ports utilisés par des terminaux simples, mais il faut tenir compte des cas suivants :

- Téléphone IP avec PC raccordé derrière.
- Stations d'accueil.
- Virtualisation.
- Remplacement de matériel.
- Bornes ou équipements qui changent d'adresse MAC visible.

Ne définissez pas une limite arbitraire sans connaître le comportement normal du port.

## 19.3. STP et prévention des boucles

Spanning Tree prévient les boucles de niveau 2 dans les topologies qui disposent de chemins redondants.

Vous devez :

- Identifier le rôle des commutateurs.
- Vérifier les ports bloqués.
- Surveiller les changements de topologie.
- Appliquer PortFast et BPDU Guard aux ports qui conviennent.
- Éviter de créer des connexions redondantes sans comprendre leur effet.
- Documenter les liens vers les points d'accès, téléphones et commutateurs supplémentaires.

Une boucle peut provoquer une multiplication des trames et rendre le réseau instable.


# 20. Défi 15 — Accès distant et services cloud

Une petite entreprise peut utiliser le cloud pour la messagerie, le partage de documents, la comptabilité ou les applications métier.

Le fait que ces services soient hébergés ailleurs ne signifie pas que leur sécurité est entièrement gérée par le fournisseur.

## 20.1. Questions à résoudre

- Qui administre les comptes ?
- L'authentification multifacteur est-elle activée lorsqu'elle est disponible ?
- Les comptes inactifs sont-ils désactivés ?
- Les droits sont-ils adaptés aux fonctions ?
- Les appareils personnels sont-ils autorisés ?
- Les données peuvent-elles être partagées à l'extérieur ?
- Les sauvegardes ou mécanismes de récupération sont-ils suffisants ?
- Les accès d'administration sont-ils séparés des accès ordinaires ?
- Comment les comptes d'un collaborateur partant sont-ils traités ?

## 20.2. VPN

Si les collaborateurs doivent accéder à des ressources internes à distance, un VPN peut être envisagé.

La conception doit préciser :

- Les utilisateurs autorisés.
- Le mécanisme d'authentification.
- Les ressources accessibles.
- Les sous-réseaux annoncés.
- Les journaux conservés.
- Les procédures de révocation.
- La stratégie de mise à jour.
- L'accès limité aux fonctions réellement nécessaires.

Un VPN ne doit pas automatiquement donner au poste distant le même accès qu'un administrateur du réseau.

## 20.3. Schéma d'accès distant

```text
                 UTILISATEUR DISTANT
                         |
                  Connexion Internet
                         |
                         v
                  +--------------+
                  | VPN / ACCÈS  |
                  | DISTANT      |
                  +--------------+
                         |
                  Authentification
                  et politique d'accès
                         |
                         v
                  +--------------+
                  | PARE-FEU     |
                  | RÈGLES VPN   |
                  +--------------+
                         |
              +----------+-----------+
              |                      |
              v                      v
         Application           Ressource autorisée
         métier                selon le profil
```

Les utilisateurs distants doivent accéder aux seules ressources nécessaires à leur travail.


# 21. Défi expert — Incident combiné

La direction signale plusieurs problèmes au même moment :

1. Certains utilisateurs ne reçoivent plus la bonne adresse IP.
2. L'imprimante n'est plus accessible.
3. Le Wi-Fi invités atteint une ressource interne.
4. Le NAS est lent et certaines opérations de fichiers échouent.
5. Le poste d'administration ne peut plus gérer le commutateur.
6. Les sauvegardes de la nuit précédente n'ont pas abouti.

Vous ne savez pas si les incidents sont liés.

## 21.1. Règles de l'intervention

Vous devez :

- Préserver les informations utiles à l'enquête.
- Prioriser le risque d'exposition du réseau interne.
- Garder un accès d'administration autorisé.
- Ne pas désactiver globalement le pare-feu.
- Ne pas réinitialiser tous les équipements.
- Ne pas modifier plusieurs paramètres simultanément.
- Contrôler l'impact des changements.
- Vérifier les sauvegardes avant de réaliser des opérations destructives.
- Documenter chaque action.

## 21.2. Tableau de collecte

| Incident | Sources | Destination | Première vérification |
|---|---|---|---|
| Mauvaise adresse IP | Postes touchés | DHCP / VLAN | Adresse, masque, passerelle, serveur DHCP |
| Impression impossible | Postes | Imprimante | Adresse, VLAN, service d'impression |
| Accès interne depuis invités | Visiteur | Ressource interne | VLAN, route, règle, adresse cible |
| NAS lent | Utilisateurs | NAS | Débit, erreurs, charge, espace |
| Administration impossible | VLAN 20 | VLAN 90 | Route, règle, interface de gestion |
| Sauvegarde échouée | NAS | Cible de sauvegarde | Journaux, capacité, authentification |

## 21.3. Priorisation

Une séquence possible est :

1. Vérifier et contenir l'accès anormal depuis le réseau invités.
2. Préserver ou rétablir une voie d'administration autorisée.
3. Examiner la cause des mauvaises adresses IP.
4. Diagnostiquer les incidents d'impression.
5. Contrôler la santé du NAS et les erreurs de stockage.
6. Identifier la cause d'échec des sauvegardes.
7. Vérifier si les incidents ont une origine commune.
8. Exécuter les tests de non-régression.

L'ordre peut être adapté selon l'impact constaté. Une exposition de sécurité critique peut nécessiter une action immédiate, mais les corrections doivent éviter de rendre impossible la gestion du réseau.

## 21.4. Rapport final

Pour chaque incident, documentez :

- Le symptôme initial.
- L'étendue du problème.
- Les hypothèses.
- Les preuves recueillies.
- Les tests réalisés.
- La cause démontrée.
- La correction appliquée.
- Les tests de validation.
- Les risques restants.
- Les actions préventives.

Une hypothèse plausible ne devient une cause racine que lorsqu'elle est étayée par des faits.


# 22. Architecture cible complète

## 22.1. Schéma global consolidé

```text
                            INTERNET
                               |
                       +----------------+
                       | FOURNISSEUR    |
                       +----------------+
                               |
                       +----------------+
                       | PARE-FEU       |
                       | Passerelles    |
                       | Routage VLAN   |
                       | NAT / VPN      |
                       | Filtrage       |
                       +----------------+
                               |
                         TRUNK 802.1Q
                               |
                       +----------------+
                       | SWITCH MANAGÉ  |
                       | VLAN / STP     |
                       | Ports d'accès  |
                       +----------------+
                          |   |   |   \
                          |   |   |    \
                          |   |   |     +-------------------+
                          |   |   |                         |
                          |   |   |                 VLAN 30 SERVEURS
                          |   |   |                         |
                          |   |   |                       NAS
                          |   |   |
                          |   |   +-------------- VLAN 40 IMPRIMANTES
                          |   |
                          |   +------------------ VLAN 10 BUREAU
                          |
                          +---------------------- POINTS D'ACCÈS
                                                     |
                                  +------------------+-----------------+
                                  |                                    |
                              VLAN 70                              VLAN 60
                              WI-FI PRO                            INVITÉS
                                  |                                    |
                         Accès professionnel                    Internet seul
                         contrôlé par règles                    selon politique

                   VLAN 20 ADMIN-IT
                           |
                    Poste d'administration
                           |
                    Accès autorisé par ACL
                           |
                     VLAN 90 MGMT
                           |
                 Gestion des équipements réseau
```

## 22.2. Résumé de l'architecture

| Domaine | Décision |
|---|---|
| Routage | Pare-feu comme passerelle des VLAN |
| Segmentation | VLAN définis selon les rôles |
| Poste standard | VLAN 10 |
| Administration | Poste dédié en VLAN 20 |
| Serveurs | VLAN 30 |
| Imprimantes/IoT | VLAN 40 |
| Téléphonie | VLAN 50 si nécessaire |
| Wi-Fi invités | VLAN 60 |
| Wi-Fi professionnel | VLAN 70 |
| Gestion des équipements | VLAN 90 |
| Ports inutilisés | Désactivés et documentés |
| Sécurité | Politique inter-VLAN restrictive et justifiée |
| Sauvegardes | Copies séparées et restaurations testées |
| Supervision | État des équipements, journaux et alertes |
| Continuité | Procédures de reprise proportionnées au risque |


# 23. Feuille de route vers 40 utilisateurs

La solution doit permettre une évolution raisonnable sans exiger une refonte immédiate.

## 23.1. Points à vérifier

Avant de passer de 24 à 40 utilisateurs, réévaluez :

- Le nombre de ports disponibles.
- La puissance PoE disponible.
- Le nombre et la capacité des points d'accès.
- La qualité de la couverture Wi-Fi.
- Le nombre d'adresses DHCP disponibles.
- La capacité du pare-feu.
- Le débit du NAS.
- La capacité de sauvegarde.
- Le nombre de sessions VPN.
- Les droits et besoins des nouveaux collaborateurs.
- Les besoins de journalisation et de supervision.

## 23.2. Stratégie d'évolution

Une évolution progressive peut suivre les étapes suivantes :

1. Prévoir suffisamment de ports et d'adresses.
2. Documenter les interfaces et réserves disponibles.
3. Mesurer les performances avant l'augmentation.
4. Ajouter les équipements uniquement lorsque le besoin est confirmé.
5. Vérifier la cohérence des VLAN et des politiques.
6. Refaire les tests de segmentation.
7. Mettre à jour les schémas.
8. Réviser la stratégie de sauvegarde.
9. Actualiser les procédures d'administration et de continuité.

Une plage d'adresses disponible ne garantit pas à elle seule que le pare-feu, le commutateur ou les points d'accès pourront supporter l'augmentation de charge.


# 24. Barème d'évaluation sur 100 points

| Domaine | Points |
|---|---:|
| Analyse des besoins et inventaire | 8 |
| Architecture physique | 8 |
| Architecture logique et VLAN | 12 |
| Plan IPv4 et DHCP | 8 |
| Configuration des ports et trunks | 10 |
| Routage inter-VLAN | 8 |
| Politique de sécurité | 14 |
| Wi-Fi professionnel et invités | 7 |
| Administration sécurisée | 5 |
| Sauvegarde et restauration | 7 |
| Dépannage OSI et Wireshark | 6 |
| Documentation et procédure de changement | 7 |
| **Total** | **100** |

## 24.1. Critères d'excellence

Un dossier de qualité doit :

- Présenter des schémas lisibles et cohérents.
- Justifier les choix techniques et économiques.
- Définir des VLAN utiles et compréhensibles.
- Éviter les chevauchements d'adresses.
- Appliquer une politique inter-VLAN explicite.
- Démontrer l'isolation du réseau visiteurs.
- Protéger les interfaces d'administration.
- Prévoir des tests positifs et négatifs.
- Prévoir la restauration des données.
- Décrire une procédure de retour arrière.
- Être compréhensible par un autre administrateur.

## 24.2. Erreurs graves

Les erreurs suivantes doivent entraîner une pénalité importante :

- Donner un accès général au réseau interne aux visiteurs.
- Permettre l'administration depuis tous les VLAN.
- Autoriser tous les VLAN sur les trunks sans justification.
- Croire que le NAT remplace une politique de sécurité.
- Considérer le NAS comme sécurisé sans contrôler ses permissions.
- Omettre les sauvegardes hors de l'équipement principal.
- Affirmer qu'une sauvegarde fonctionne sans test de restauration.
- Désactiver toutes les ACL pour résoudre un incident.
- Modifier plusieurs paramètres sans mesurer leur impact.
- Ne pas conserver la trace des changements.


# 25. Modèle du dossier final

## 25.1. Résumé exécutif

Présentez :

- Le contexte de l'entreprise.
- Les problèmes à résoudre.
- L'architecture retenue.
- Les bénéfices attendus.
- Les principaux risques résiduels.
- Les décisions qui nécessitent un arbitrage budgétaire.

## 25.2. Inventaire

Fournissez :

- La liste des équipements.
- Leur rôle.
- Leur modèle et leur version logicielle.
- Leur adresse de gestion.
- Leur criticité.
- Leur état de support.
- La personne responsable.

Évitez d'inclure dans le dossier partagé des secrets ou informations qui faciliteraient un accès non autorisé.

## 25.3. Architecture

Fournissez :

- Un schéma physique.
- Un schéma logique.
- Un plan VLAN.
- Un plan IPv4.
- Les passerelles.
- Les trunks.
- Les dépendances des services.
- Les points uniques de panne.

## 25.4. Sécurité

Fournissez :

- Une matrice de flux.
- Les règles d'administration.
- La politique du Wi-Fi invités.
- Les permissions du NAS.
- Les contrôles des imprimantes et IoT.
- La politique d'accès distant.
- Les mesures de journalisation.
- Les hypothèses restant à vérifier.

## 25.5. Tests de validation

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | Attribution IP poste filaire | Réseau correct | À renseigner | À exécuter |
| T02 | Résolution DNS | Réponse correcte | À renseigner | À exécuter |
| T03 | Accès application métier | Fonctionne | À renseigner | À exécuter |
| T04 | Accès au NAS depuis utilisateur autorisé | Conforme aux permissions | À renseigner | À exécuter |
| T05 | Accès au NAS depuis visiteur | Refusé | À renseigner | À exécuter |
| T06 | Accès à l'imprimante | Fonctionne selon la politique | À renseigner | À exécuter |
| T07 | Administration du switch | Autorisée depuis la source prévue | À renseigner | À exécuter |
| T08 | Administration depuis le VLAN visiteurs | Refusée | À renseigner | À exécuter |
| T09 | Trunks | VLAN conformes au plan | À renseigner | À exécuter |
| T10 | Sauvegarde | Exécution vérifiée | À renseigner | À exécuter |
| T11 | Restauration d'un fichier | Contenu restauré et vérifié | À renseigner | À exécuter |
| T12 | Accès Internet | Conforme à la politique | À renseigner | À exécuter |

Le statut doit correspondre à un test réellement effectué. Ne marquez pas un test « OK » sur la seule base d'une configuration théorique.

## 25.6. Gestion des changements

Pour chaque modification importante, notez :

- L'objectif.
- Le risque.
- L'équipement concerné.
- Les paramètres modifiés.
- La sauvegarde préalable.
- Les tests avant modification.
- Les tests après modification.
- Le résultat attendu.
- La procédure de retour arrière.
- La personne qui valide le changement.


# 26. Checklist finale

## Conception

- [ ] Les besoins des utilisateurs sont documentés.
- [ ] Les équipements existants ont été inventoriés.
- [ ] Le schéma physique correspond au câblage prévu.
- [ ] Le schéma logique correspond aux VLAN configurés.
- [ ] Le plan IPv4 est sans chevauchement.
- [ ] Les passerelles sont documentées.
- [ ] Les services internes sont identifiés.
- [ ] Les points uniques de panne sont connus.

## Configuration réseau

- [ ] Les VLAN existent.
- [ ] Les ports d'accès utilisent le bon VLAN.
- [ ] Les trunks transportent uniquement les VLAN nécessaires.
- [ ] Les ports inutilisés sont traités.
- [ ] Le pare-feu assure le routage attendu.
- [ ] Les règles de filtrage correspondent à la matrice.
- [ ] Les services DHCP et DNS sont testés.
- [ ] La gestion des équipements est séparée des utilisateurs.

## Sécurité

- [ ] Les visiteurs sont isolés.
- [ ] Les interfaces d'administration sont protégées.
- [ ] Les droits d'accès au NAS sont documentés.
- [ ] Les imprimantes et IoT disposent de permissions limitées.
- [ ] Les services inutiles sont désactivés.
- [ ] Les mises à jour sont planifiées.
- [ ] Les journaux importants sont accessibles aux personnes autorisées.
- [ ] La politique IPv6 est définie si IPv6 est utilisé.

## Continuité

- [ ] Les sauvegardes sont planifiées.
- [ ] Les échecs de sauvegarde sont détectés.
- [ ] Les copies sont séparées des données principales.
- [ ] Une restauration a été testée.
- [ ] Les configurations des équipements sont sauvegardées.
- [ ] La procédure de reprise est documentée.
- [ ] Les équipements de secours prévus sont identifiés.

## Validation

- [ ] Les flux autorisés fonctionnent.
- [ ] Les flux interdits sont bloqués.
- [ ] Le Wi-Fi visiteurs est testé.
- [ ] L'accès administratif est contrôlé.
- [ ] Les tests de performance ont été mesurés.
- [ ] Les tests sont consignés.
- [ ] Les changements sont documentés.
- [ ] Le retour arrière est défini.


# 27. Références techniques

Pour approfondir les technologies utilisées dans ce challenge, consultez les documentations et standards suivants :

- **RFC 1918 — Address Allocation for Private Internets** : plages IPv4 privées.
- **IEEE 802.1Q** : VLAN et identification des trames Ethernet.
- **RFC 2131 — Dynamic Host Configuration Protocol** : fonctionnement de DHCPv4.
- **RFC 1034 et RFC 1035** : principes et fonctionnement du DNS.
- **RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification** : spécification IPv6.
- **Documentation du constructeur du pare-feu** : VLAN, routage, NAT, ACL, VPN et journalisation.
- **Documentation du constructeur du commutateur** : VLAN, trunks, STP, sécurité des ports et supervision.
- **Documentation Wireshark** : filtres, capture et analyse des protocoles.
- **Documentation du NAS** : permissions, mises à jour, sauvegardes et restauration.
- **Documentation des systèmes d'exploitation** : diagnostic IP, DNS, routes et services.

Les commandes de configuration fournies dans le document sont des exemples pédagogiques. Elles doivent être adaptées au matériel et au système réellement employés.


# Conclusion

Le challenge doit aboutir à une architecture que l'entreprise peut exploiter au quotidien sans dépendre d'une seule personne qui connaît toute la configuration par cœur.

La qualité d'un réseau de petite entreprise ne se mesure pas au nombre de VLAN ou d'équipements installés. Elle se mesure à sa capacité à répondre aux besoins, à limiter les risques, à protéger les données et à permettre une remise en service maîtrisée.

Une architecture réussie repose sur cinq principes :

1. **Simplicité maîtrisée :** limiter la complexité sans sacrifier les contrôles essentiels.
2. **Segmentation pertinente :** séparer les usages selon les besoins et les risques.
3. **Sécurité démontrable :** valider les flux autorisés et les flux interdits.
4. **Données protégées :** disposer de sauvegardes distinctes et de restaurations testées.
5. **Exploitation documentée :** savoir surveiller, dépanner, modifier et restaurer l'infrastructure.

La meilleure solution pour NovaBureau n'est pas nécessairement celle qui possède le plus de fonctionnalités. C'est celle qui répond aux exigences de l'entreprise, dont le coût est justifié, et que l'équipe peut comprendre, tester et maintenir.