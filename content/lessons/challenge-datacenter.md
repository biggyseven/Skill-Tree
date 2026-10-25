# Challenge d'architecture réseau — Datacenter

> **Fichier :** `challenge-datacenter.md`  
> **Domaine :** architecture réseau de datacenter, virtualisation, stockage, sécurité et haute disponibilité  
> **Progression :** Débutant → Intermédiaire → Expert  
> **Environnement :** datacenter privé de petite à moyenne taille  
> **Technologies étudiées :** Ethernet, VLAN, routage L3, BGP, VRF, virtualisation, stockage, supervision et sauvegarde  
> **Extensions expertes :** architecture leaf-spine, VXLAN EVPN, multihoming et automatisation  
> **Objectif final :** concevoir, documenter, sécuriser et valider une infrastructure de datacenter capable d'héberger des applications critiques.


# 1. Présentation du challenge

## 1.1. Contexte de l'entreprise

Vous êtes ingénieur réseau chargé de concevoir l'infrastructure du datacenter de **NovaCloud Services**, une entreprise qui héberge les applications de plusieurs services internes et de quelques clients professionnels.

L'entreprise possède un petit datacenter composé de plusieurs racks. Elle souhaite faire évoluer son architecture afin de mieux répondre aux besoins suivants :

- Héberger plusieurs applications professionnelles.
- Exécuter des machines virtuelles sur un cluster de serveurs.
- Séparer les environnements de production, de test et d'administration.
- Protéger les bases de données.
- Isoler les serveurs exposés à Internet.
- Réduire les interruptions causées par une panne réseau.
- Sécuriser les opérations d'administration.
- Sauvegarder les machines virtuelles et les données.
- Superviser les performances et la disponibilité.
- Faciliter l'ajout de serveurs et de services.
- Préparer une extension vers une architecture de datacenter plus évolutive.

Le réseau actuel est trop simple pour satisfaire durablement ces exigences.

Les serveurs sont répartis dans différents VLAN sans politique homogène. Certaines interfaces de gestion sont accessibles depuis le réseau des applications. Les sauvegardes empruntent les mêmes chemins que le trafic de production. La documentation ne précise pas toujours quels flux sont nécessaires.

Votre mission consiste à concevoir une architecture qui corrige ces problèmes et qui peut être exploitée par une équipe technique.

## 1.2. Scénario de référence

Pour ce challenge, retenez les hypothèses suivantes.

| Élément | Hypothèse |
|---|---|
| Sites | Un datacenter principal |
| Racks | Deux racks serveurs |
| Serveurs physiques | Six à huit hôtes de virtualisation |
| Machines virtuelles | Plusieurs dizaines, avec croissance prévue |
| Réseau utilisateur | Accès indirect au travers des applications hébergées |
| Stockage | Baie de stockage, NAS ou stockage distribué selon la solution retenue |
| Sauvegarde | Cible dédiée distincte du stockage principal |
| Réseau de gestion | Réseau d'administration contrôlé |
| Gestion hors bande | Réseau OOB séparé pour les interfaces matérielles |
| Sécurité périmétrique | Pare-feu redondant si le budget le permet |
| Accès Internet | Une ou plusieurs connexions selon les exigences de disponibilité |
| Applications internes | Serveurs Web, services applicatifs et bases de données |
| Environnements | Production, test et administration |
| Supervision | Collecte des mesures, journaux et alertes |
| Continuité | Sauvegarde et procédure de reprise documentées |

Ces valeurs servent à l'exercice. Le nombre réel de racks, de serveurs, de machines virtuelles et de liens devra être dimensionné en fonction de la charge attendue.

## 1.3. Besoins fonctionnels

L'architecture doit permettre :

- Aux utilisateurs autorisés d'accéder aux applications publiées.
- Aux serveurs applicatifs de joindre uniquement les bases de données nécessaires.
- Aux administrateurs de gérer les serveurs et le réseau depuis une zone protégée.
- Aux hyperviseurs de communiquer avec les services de gestion nécessaires.
- Aux hôtes de virtualisation d'accéder aux réseaux de stockage prévus.
- Aux systèmes de sauvegarde de récupérer les données sans exposer la cible de sauvegarde à tous les serveurs.
- Aux outils de supervision d'observer l'infrastructure.
- Aux services exposés dans une DMZ de rester séparés des réseaux internes.
- À l'équipe technique de diagnostiquer une panne et de restaurer un service.

## 1.4. Contraintes de conception

Un datacenter doit être conçu selon les besoins de l'entreprise et non uniquement selon les fonctionnalités disponibles sur les équipements.

Vous devez tenir compte :

- Du budget d'investissement.
- Des débits attendus.
- Du nombre de flux est-ouest entre serveurs.
- Du nombre de connexions nord-sud vers les réseaux externes.
- Des besoins de disponibilité.
- Des risques de sécurité.
- Des compétences de l'équipe d'exploitation.
- Du coût des licences.
- De la capacité d'automatisation.
- Des objectifs de restauration.
- De la compatibilité entre les équipements.
- Des contraintes d'alimentation, de refroidissement et de câblage.

**Une architecture complexe qui ne peut pas être correctement exploitée n'est pas automatiquement supérieure à une architecture plus simple.**


# 2. Progression pédagogique

## Niveau 1 — Débutant : concevoir un datacenter fonctionnel

Vous devez :

- Recueillir les besoins.
- Identifier les rôles des équipements.
- Dessiner l'architecture physique.
- Définir les VLAN principaux.
- Construire un plan d'adressage IPv4.
- Distinguer les réseaux de production, de gestion, de stockage et de sauvegarde.
- Comprendre les passerelles et le routage inter-VLAN.
- Définir les accès aux applications.
- Vérifier la connectivité.
- Documenter les tests.

**Livrable :** une architecture de datacenter fonctionnelle avec un plan IP et une matrice de flux.

## Niveau 2 — Intermédiaire : sécuriser et rendre l'infrastructure résiliente

Vous devez :

- Séparer les zones de sécurité.
- Définir les flux autorisés entre les applications.
- Protéger la DMZ.
- Séparer l'administration hors bande.
- Concevoir les chemins réseau redondants.
- Étudier les risques de panne.
- Séparer le trafic de sauvegarde du trafic applicatif.
- Définir une stratégie de supervision.
- Tester les mécanismes de reprise.
- Résoudre des incidents de routage, de VLAN et de stockage.

**Livrable :** une architecture sécurisée et résiliente, avec des procédures de panne et de reprise.

## Niveau 3 — Expert : construire une fabric de datacenter évolutive

Vous devez :

- Concevoir une architecture leaf-spine.
- Définir un underlay routé.
- Étudier le BGP pour le transport des routes de la fabric.
- Concevoir des VRF et une segmentation multi-tenant.
- Étudier VXLAN EVPN.
- Concevoir des passerelles distribuées lorsque la plateforme le permet.
- Définir la gestion du multihoming.
- Vérifier le MTU de bout en bout.
- Préparer l'automatisation et la validation de configuration.
- Étudier la continuité d'activité et la reprise après sinistre.

**Livrable :** un dossier d'architecture avancé comprenant les plans d'adressage, le routage, la segmentation, les mécanismes de redondance et les tests de validation.


# 3. Défi 1 — Recueil des besoins et inventaire

## 3.1. Identifier les catégories de serveurs

Le datacenter héberge plusieurs types de systèmes.

| Catégorie | Exemples | Besoin principal |
|---|---|---|
| Présentation | Serveurs Web ou reverse proxies | Recevoir les connexions autorisées |
| Applications | Services métier, API internes | Traiter les requêtes applicatives |
| Bases de données | SGBD relationnels ou autres | Stocker les données applicatives |
| Virtualisation | Hyperviseurs et gestion centralisée | Héberger et administrer les VM |
| Stockage | Baie SAN, NAS ou stockage distribué | Fournir les volumes et fichiers |
| Sauvegarde | Serveur et cible de sauvegarde | Protéger les données |
| Supervision | Monitoring, alertes et journaux | Détecter les anomalies |
| Administration | Bastion et outils de gestion | Contrôler les accès administratifs |
| Infrastructure | DNS, NTP, authentification | Fournir les services essentiels |

La présence de ces fonctions ne signifie pas que chacune doit obligatoirement être installée sur un serveur physique distinct. Elles peuvent être virtualisées ou fournies par des services externes selon l'architecture choisie.

## 3.2. Questions de conception

Avant de choisir les équipements, répondez aux questions suivantes :

1. Combien de machines virtuelles doivent être hébergées ?
2. Quelle est la croissance prévue sur trois ans ?
3. Quels services sont critiques pour l'activité ?
4. Quels sont les débits nécessaires entre les serveurs ?
5. Les bases de données sont-elles accessibles uniquement par les applications ?
6. Les clients utilisent-ils des services publiés sur Internet ?
7. Les réseaux de stockage doivent-ils prendre en charge des trames de grande taille ?
8. Les sauvegardes peuvent-elles être effectuées pendant les heures de travail ?
9. Quel délai d'interruption est acceptable ?
10. Quelle quantité de données peut être perdue après un incident sans compromettre l'activité ?
11. Le datacenter doit-il fonctionner si un commutateur tombe en panne ?
12. La perte d'un serveur doit-elle provoquer une interruption ?
13. Les équipements de gestion matérielle sont-ils accessibles depuis un réseau séparé ?
14. Les administrateurs se connectent-ils depuis un site distant ?
15. Existe-t-il un site de secours ?
16. Quelles exigences de chiffrement, de conformité et de journalisation s'appliquent ?

## 3.3. Transformer les besoins en exigences mesurables

| Exigence | Test de validation |
|---|---|
| Le service Web public répond | Tester le service publié depuis un réseau externe autorisé |
| La base de données est protégée | Vérifier qu'un réseau non autorisé ne peut pas établir de connexion |
| La gestion matérielle est isolée | Tester l'accès aux interfaces BMC depuis les réseaux utilisateurs |
| Les sauvegardes sont disponibles | Restaurer une VM ou un jeu de données de test |
| Le stockage est accessible depuis les hôtes autorisés | Tester le chemin de stockage et contrôler les journaux |
| Une panne d'un chemin réseau est tolérée | Déconnecter un lien de test pendant une fenêtre autorisée |
| Les journaux sont collectés | Vérifier l'arrivée des événements dans le système de journalisation |
| Le réseau invité ou bureautique n'accède pas à la gestion | Tester le refus de connexions vers les interfaces de gestion |

Chaque exigence doit avoir un résultat attendu, une procédure et une preuve.


# 4. Architecture 1 — Datacenter de base

Cette première architecture convient à l'apprentissage et à un environnement de taille limitée.

Elle privilégie la simplicité : une paire de commutateurs de cœur si le budget le permet, des commutateurs d'accès, un pare-feu et des réseaux logiques distincts.

## 4.1. Schéma physique

```text
                        INTERNET / WAN
                              |
                       +--------------+
                       | FOURNISSEUR  |
                       +--------------+
                              |
                       +--------------+
                       | PARE-FEU     |
                       | NAT / ACL    |
                       | VPN éventuel|
                       +--------------+
                              |
                    +---------+----------+
                    |                    |
                    v                    v
             +-------------+      +-------------+
             | CŒUR / L3 A |======| CŒUR / L3 B |
             +-------------+      +-------------+
                    ||                    ||
                    || liens redondants   ||
                    ||                    ||
             +-------------+      +-------------+
             | SWITCH      |      | SWITCH      |
             | SERVEURS A  |      | SERVEURS B  |
             +-------------+      +-------------+
                |   |   |             |   |   |
                |   |   |             |   |   +---- Hôtes de virtualisation
                |   |   +------------------------ Serveurs applicatifs
                |   +---------------------------- Stockage
                +-------------------------------- Cible de sauvegarde

                    Réseau OOB indépendant
                             |
                      +--------------+
                      | SWITCH OOB   |
                      +--------------+
                       |     |     |
                       v     v     v
                     BMC   PDU   Gestion matérielle
```

Ce dessin illustre les fonctions logiques et les liens redondants envisagés. La façon d'interconnecter les commutateurs doit être adaptée à leur capacité et à la topologie retenue.

Il ne faut pas créer des liens redondants sans décider comment les boucles de couche 2 seront évitées, comment les chemins seront utilisés et comment le basculement sera contrôlé.

## 4.2. Rôle du pare-feu

Le pare-feu contrôle les échanges entre le datacenter et les réseaux externes.

Selon les besoins, il peut assurer :

- Le filtrage des connexions entrantes.
- Le filtrage des connexions sortantes.
- Le NAT.
- La terminaison VPN.
- Le filtrage entre la DMZ et les applications internes.
- La journalisation des sessions.
- Des fonctions d'inspection des protocoles.
- La protection des services publiés.

Le pare-feu ne garantit pas à lui seul la sécurité de tous les échanges internes. Si le trafic est routé au niveau des commutateurs, ces flux peuvent ne jamais traverser le pare-feu périmétrique.

Il faut donc décider où se trouvent les passerelles et où les politiques inter-zones sont appliquées.

## 4.3. Rôle du cœur réseau

Le cœur réseau transporte le trafic entre les équipements et peut assurer le routage L3.

Dans une architecture traditionnelle, les interfaces VLAN ou SVI hébergent les passerelles des sous-réseaux.

Le cœur peut également prendre en charge :

- Le routage entre VLAN.
- La redondance des passerelles.
- Les ACL.
- Les routes vers le pare-feu.
- Les mécanismes de disponibilité prévus.
- La supervision des liens.

Une paire de commutateurs ne constitue une solution de haute disponibilité que si les protocoles de redondance, les chemins et les procédures de reprise sont conçus et testés.

## 4.4. Rôle des commutateurs d'accès

Les commutateurs d'accès raccordent les serveurs, les appliances de stockage et les équipements auxiliaires.

Leur configuration doit préciser :

- Les VLAN des ports.
- Les trunks vers les hyperviseurs.
- Les trunks vers les autres commutateurs, s'ils sont nécessaires.
- Les VLAN autorisés.
- Les fonctions STP.
- La configuration MTU.
- Les protections de ports.
- Les interfaces de gestion.

Un serveur qui héberge plusieurs machines virtuelles peut avoir besoin de transporter plusieurs VLAN. Ce besoin doit être documenté et ne doit pas justifier l'autorisation de tous les VLAN sur tous les ports.


# 5. Architecture 2 — Séparer les plans de trafic

Un datacenter transporte plusieurs catégories de trafic qui ne doivent pas nécessairement emprunter les mêmes réseaux.

## 5.1. Les catégories principales

### Trafic nord-sud

Il circule entre le datacenter et les réseaux extérieurs.

Exemples :

- Client Internet vers service Web public.
- Utilisateur d'entreprise vers application hébergée.
- Serveur vers API externe autorisée.
- Connexion VPN vers service interne autorisé.

### Trafic est-ouest

Il circule entre les systèmes du datacenter.

Exemples :

- Serveur Web vers serveur applicatif.
- Serveur applicatif vers base de données.
- Hyperviseur vers stockage.
- Machine virtuelle vers service interne.
- Serveur vers outil de supervision.

Le trafic est-ouest peut être très important dans un environnement virtualisé. Une architecture qui traite uniquement la sortie Internet sans contrôler les flux internes peut laisser des communications sensibles insuffisamment protégées.

### Plan de gestion

Il permet d'administrer les équipements et les systèmes.

Exemples :

- SSH ou HTTPS vers les commutateurs.
- Administration des hyperviseurs.
- Gestion de la baie de stockage.
- Configuration des contrôleurs.
- Accès aux interfaces BMC.

### Plan de stockage

Il transporte les échanges entre les hôtes et le système de stockage.

Selon la technologie utilisée, il peut s'agir de :

- iSCSI.
- NFS.
- NVMe over Fabrics.
- Réseaux de stockage propriétaires.
- Stockage distribué entre nœuds.

Le choix de la technologie détermine les exigences de bande passante, de latence, de MTU et de redondance.

### Plan de sauvegarde

Il transporte les données vers les cibles de sauvegarde et, le cas échéant, vers un site distant.

Ce trafic peut être volumineux. Sa séparation permet d'éviter qu'une opération de sauvegarde saturée dégrade directement les applications.

## 5.2. Schéma logique des plans

```text
                  +------------------------+
                  | TRAFIC NORD-SUD        |
                  | Internet / WAN         |
                  +------------------------+
                              |
                           Pare-feu
                              |
                       Réseau de production
                              |
           +------------------+-------------------+
           |                  |                   |
           v                  v                   v
       Application        Base de données      Services Web


                  +------------------------+
                  | TRAFIC EST-OUEST       |
                  | VM vers VM             |
                  | Application vers DB    |
                  +------------------------+


                  +------------------------+
                  | PLAN DE GESTION        |
                  | Bastion / Admin        |
                  +------------------------+
                              |
                 Hyperviseurs / Switches / BMC


                  +------------------------+
                  | PLAN DE STOCKAGE       |
                  | Hôtes / Baie de stockage|
                  +------------------------+


                  +------------------------+
                  | PLAN DE SAUVEGARDE     |
                  | Sources / Cibles       |
                  +------------------------+
```

Les plans peuvent être physiquement séparés, logiquement séparés ou utiliser une combinaison de ces approches.

Une séparation logique par VLAN ne protège pas automatiquement les données si les ACL sont trop permissives. Une séparation physique améliore parfois l'isolation, mais augmente les coûts de câblage, d'équipement et d'exploitation.


# 6. Défi 2 — Plan de VLAN et de zones

## 6.1. Plan proposé

Le plan ci-dessous constitue une base pédagogique. Il doit être adapté aux rôles des systèmes réellement déployés.

| VLAN | Nom | Usage |
|---:|---|---|
| 110 | APP-PROD | Frontends et applications de production |
| 120 | DB-PROD | Bases de données de production |
| 130 | DMZ | Services publiés ou intermédiaires |
| 140 | VIRT-MGMT | Gestion d'hyperviseurs et de la plateforme |
| 150 | STORAGE | Trafic de stockage |
| 160 | BACKUP | Trafic de sauvegarde |
| 170 | MONITORING | Supervision et collecte de mesures |
| 180 | ADMIN-JUMP | Bastion ou postes d'administration dédiés |
| 190 | TEST-DEV | Environnements de développement ou de test |
| 999 | PARKING | Ports inutilisés ou VLAN sans usage utilisateur |

Le réseau hors bande, OOB, est décrit séparément. Il ne faut pas supposer qu'une simple création de VLAN suffit à isoler les interfaces matérielles si elles partagent tous les mêmes chemins physiques que le réseau de production.

## 6.2. Plan d'adressage de référence

Pour l'exercice, utilisez des sous-réseaux IPv4 privés dans le bloc `10.60.0.0/16`.

| VLAN | Sous-réseau | Passerelle indicative | Zone |
|---:|---|---|---|
| 110 | `10.60.10.0/24` | `10.60.10.1` | Production applicative |
| 120 | `10.60.20.0/24` | `10.60.20.1` | Bases de données |
| 130 | `10.60.30.0/24` | `10.60.30.1` | DMZ |
| 140 | `10.60.40.0/24` | `10.60.40.1` | Gestion de virtualisation |
| 150 | `10.60.50.0/24` | Selon la conception | Stockage |
| 160 | `10.60.60.0/24` | Selon la conception | Sauvegarde |
| 170 | `10.60.70.0/24` | `10.60.70.1` si routé | Supervision |
| 180 | `10.60.80.0/24` | `10.60.80.1` si routé | Administration |
| 190 | `10.60.90.0/24` | `10.60.90.1` si routé | Test et développement |

Les adresses et les masques sont des valeurs pédagogiques. Avant un déploiement, vérifiez les besoins d'hôtes, les routes existantes, les VPN, les autres sites et les réseaux cloud.

## 6.3. Gestion hors bande

Le réseau OOB doit donner accès aux interfaces de gestion matérielle sans dépendre entièrement du plan de données de production.

Exemple de plan OOB :

| Élément | Adresse indicative |
|---|---|
| Sous-réseau OOB | `10.60.100.0/24` |
| Passerelle OOB | `10.60.100.1`, si le routage est nécessaire |
| Bastion OOB | `10.60.100.10` |
| Gestion matérielle des hôtes | `10.60.100.20` à `10.60.100.39` |
| Gestion des commutateurs | `10.60.100.40` à `10.60.100.59` |
| Gestion du stockage | `10.60.100.60` à `10.60.100.79` |
| Gestion des équipements électriques | `10.60.100.80` à `10.60.100.99` |

Ce plan d'adressage ne suffit pas à garantir une séparation hors bande. Pour obtenir une réelle séparation physique, le réseau OOB doit disposer de ses propres commutateurs et chemins de raccordement, sans transport du trafic OOB sur les trunks de production.

L'accès au réseau OOB doit être strictement contrôlé.

## 6.4. Pourquoi le réseau de stockage est particulier

Le stockage ne doit pas être placé dans le même réseau que les postes d'administration simplement parce qu'il faut pouvoir le gérer.

Il faut distinguer :

- Le trafic de données entre hôtes et stockage.
- L'administration de la baie.
- La supervision du stockage.
- Les opérations de sauvegarde.
- La réplication vers un autre système ou un autre site.

Dans une architecture iSCSI ou NFS, le trafic de données peut utiliser des réseaux dédiés. L'administration de la baie doit rester sur le réseau de gestion.

Le stockage ne devrait pas recevoir une route par défaut sans justification. Selon la technologie, il peut fonctionner dans un segment non routé ou dans un réseau spécialement contrôlé.

## 6.5. Exercice

Pour chaque VLAN, fournissez :

1. Son objectif.
2. Les équipements présents.
3. Le plan d'adressage.
4. Le nombre estimé d'adresses nécessaires.
5. Le mode d'attribution des adresses.
6. Les sources autorisées.
7. Les destinations autorisées.
8. Les points de filtrage.
9. La procédure de diagnostic.
10. Les risques liés à une mauvaise configuration.

Un VLAN sans besoin identifié doit être réévalué. La segmentation doit être expliquée, pas seulement comptabilisée.


# 7. Défi 3 — Comprendre les chemins de communication

## 7.1. Flux Web vers base de données

Une application publique ne doit pas donner aux utilisateurs externes un accès direct à la base de données.

Architecture logique :

```text
                       INTERNET
                           |
                           v
                  +------------------+
                  | PARE-FEU / WAF   |
                  | Publication      |
                  +------------------+
                           |
                           v
                  +------------------+
                  | VLAN 130 - DMZ   |
                  | Reverse proxy    |
                  +------------------+
                           |
                  Flux applicatif autorisé
                           |
                           v
                  +------------------+
                  | VLAN 110 - APP   |
                  | Service métier   |
                  +------------------+
                           |
                  Flux vers DB précis
                           |
                           v
                  +------------------+
                  | VLAN 120 - DB    |
                  | Base de données  |
                  +------------------+
```

Cette chaîne comporte plusieurs zones de sécurité.

Le flux public est dirigé vers le service publié. Le reverse proxy ou la couche d'accès frontal communique ensuite avec les composants autorisés. La base de données n'est pas directement accessible depuis Internet.

Selon la plateforme, la DMZ, les applications et les bases peuvent utiliser des pare-feu physiques, des pare-feu virtuels, des politiques distribuées ou une combinaison de ces éléments.

## 7.2. Flux d'administration

```text
           ADMINISTRATEUR AUTORISÉ
                       |
               VPN ou accès interne
                       |
                       v
              +------------------+
              | BASTION ADMIN    |
              | Authentification |
              | Journalisation   |
              +------------------+
                       |
           Accès administratif limité
                       |
            +----------+-----------+
            |          |           |
            v          v           v
         Hyperviseur  Réseau     Stockage
            |          |           |
         Gestion     Gestion     Gestion
```

Le bastion fournit un point de contrôle pour les connexions d'administration. Il doit être protégé par des identités individuelles, une authentification forte adaptée au contexte, des droits minimaux et une journalisation.

Le bastion ne doit pas devenir un poste de travail généraliste utilisé pour naviguer librement sur Internet.

## 7.3. Flux de stockage

```text
                  HÔTES DE VIRTUALISATION
                     |             |
                     |             |
                  Chemin A       Chemin B
                     |             |
                     v             v
                 +---------------------+
                 | RÉSEAU DE STOCKAGE  |
                 +---------------------+
                           |
                           v
                  +------------------+
                  | BAIE / STOCKAGE  |
                  +------------------+
```

Le nombre de chemins, la redondance et les mécanismes de bascule dépendent de la technologie de stockage.

Un diagramme à deux liens ne garantit pas une véritable redondance. Les chemins doivent être indépendants autant que possible et la solution de stockage doit prendre en charge le multipathing ou un mécanisme équivalent.


# 8. Défi 4 — Architecture de sécurité

## 8.1. Principes

La politique de sécurité repose sur les principes suivants :

- Refuser par défaut les communications qui ne sont pas nécessaires.
- Autoriser les flux sur la base d'un besoin identifié.
- Séparer les services exposés des services internes.
- Protéger les bases de données.
- Restreindre le plan de gestion.
- Isoler les interfaces OOB.
- Contrôler les flux entre les machines virtuelles.
- Limiter les droits des comptes de service.
- Séparer les sauvegardes des systèmes d'origine.
- Journaliser les événements importants.
- Tester les communications autorisées et interdites.

Un VLAN n'est pas automatiquement une zone de sécurité complète. Le routage entre VLAN doit être contrôlé par des ACL, un pare-feu ou un autre mécanisme adapté.

## 8.2. Matrice de flux de référence

| Source | Destination | Politique |
|---|---|---|
| Internet | Service publié dans la DMZ | Autoriser uniquement les ports publiés |
| Internet | Réseau des bases de données | Refuser |
| DMZ | Applications internes | Autoriser uniquement les flux requis |
| DMZ | Bases de données | Refuser par défaut, exceptions à justifier |
| Applications | Bases de données | Autoriser les ports nécessaires |
| Employés | Interfaces de gestion | Refuser |
| Bastion d'administration | Hyperviseurs | Autoriser selon les rôles |
| Bastion d'administration | Commutateurs | Autoriser les protocoles de gestion nécessaires |
| Bastion d'administration | Stockage | Autoriser l'administration prévue |
| Hôtes de virtualisation | Stockage | Autoriser les protocoles de stockage nécessaires |
| Utilisateurs | Réseau de stockage | Refuser |
| Serveurs de production | Cible de sauvegarde | Autoriser les flux nécessaires, sans donner d'accès d'administration global |
| Supervision | Équipements monitorés | Autoriser les mécanismes de collecte prévus |
| Équipements monitorés | Supervision | Autoriser les flux nécessaires au fonctionnement des agents |
| Réseaux de test | Production | Refuser par défaut |
| OOB | Interfaces matérielles | Autoriser depuis les sources d'administration prévues |
| Réseaux de production | OOB | Refuser par défaut |

Cette matrice est un point de départ. Les règles finales doivent mentionner les adresses, protocoles, ports, points de filtrage et responsables concernés.

## 8.3. Règles de la DMZ

Les services exposés à Internet doivent être traités comme des composants plus exposés que les applications internes.

Une politique de DMZ doit préciser :

- Quels services sont publiés.
- Quelles adresses et quels ports sont accessibles.
- Quel équipement assure la terminaison TLS, si nécessaire.
- Quels flux la DMZ peut initier vers les applications.
- Quels mécanismes de journalisation sont utilisés.
- Comment les mises à jour sont gérées.
- Comment les comptes d'administration sont protégés.
- Quelles procédures s'appliquent en cas de compromission.

L'existence d'une DMZ ne prouve pas que l'application est sécurisée. Elle permet de délimiter les communications et de réduire les conséquences potentielles d'une compromission.

## 8.4. Sécurité des bases de données

Les bases de données sont des ressources critiques.

Elles doivent bénéficier :

- D'une exposition réseau limitée.
- D'une authentification robuste.
- De droits applicatifs minimaux.
- De mises à jour maîtrisées.
- D'une journalisation pertinente.
- De sauvegardes vérifiées.
- D'une séparation entre comptes d'administration et comptes applicatifs.
- D'une procédure de récupération.
- D'une politique de chiffrement adaptée aux données.

Une base de données qui n'est pas accessible depuis Internet peut quand même être vulnérable si tous les serveurs internes peuvent la contacter sans contrôle.

## 8.5. Vérification de la segmentation

Pour chaque règle importante, préparez :

- Un test positif depuis une source autorisée.
- Un test négatif depuis une source non autorisée.
- Une vérification des journaux.
- Une preuve du chemin réseau.
- Une vérification de l'absence de chemin alternatif.
- Une validation des règles IPv4 et IPv6 si les deux sont utilisés.

Le test ne doit pas se limiter à `ping`. Il faut vérifier le protocole et le service qui sont réellement concernés.


# 9. Défi 5 — Virtualisation et réseaux des hyperviseurs

## 9.1. Les besoins réseau d'un hyperviseur

Un hôte de virtualisation peut avoir plusieurs besoins réseau :

- Administration de l'hyperviseur.
- Trafic des machines virtuelles.
- Migration de machines virtuelles entre hôtes.
- Accès au stockage.
- Réplication.
- Sauvegarde.
- Tolérance de panne.
- Trafic de cluster.

Ces catégories ne doivent pas être mélangées sans justification.

## 9.2. Schéma d'un hôte de virtualisation

```text
                +---------------------------------+
                | HÔTE DE VIRTUALISATION          |
                |                                 |
                | +-------------+ +-------------+ |
                | | VM WEB      | | VM APP      | |
                | +-------------+ +-------------+ |
                | +-------------+ +-------------+ |
                | | VM DB       | | VM OUTILS   | |
                | +-------------+ +-------------+ |
                |                                 |
                | Commutateur virtuel / vSwitch   |
                +---------------------------------+
                      |         |          |
                      |         |          |
                   PROD/DMZ  GESTION    STOCKAGE
                      |         |          |
                      v         v          v
                 Réseau de   Réseau de   Réseau de
                 production  gestion     stockage
```

Les interfaces physiques et virtuelles doivent être documentées. Le nombre de cartes réseau, le bonding, le teaming, le multipathing et la distribution des flux dépendent de la plateforme.

## 9.3. Trunks vers les hyperviseurs

Un hyperviseur qui héberge plusieurs réseaux de machines virtuelles peut avoir besoin d'un trunk 802.1Q.

Cela ne signifie pas qu'il faut autoriser tous les VLAN sur chaque port.

Pour chaque hôte, documentez :

- Les VLAN nécessaires.
- Le mode access ou trunk.
- Les interfaces physiques utilisées.
- Les mécanismes de redondance.
- Les limites de MTU.
- Les réseaux de gestion.
- Les chemins de stockage.
- Les politiques de filtrage virtuel.

## 9.4. Migration de machines virtuelles

La migration d'une machine virtuelle entre hôtes peut nécessiter :

- La connectivité entre les hôtes.
- La disponibilité des réseaux virtuels attendus.
- Un accès cohérent au stockage ou un mécanisme de migration du disque.
- Des capacités CPU et mémoire suffisantes.
- Des réglages de sécurité adaptés.
- Une bande passante suffisante.

La migration ne doit pas être autorisée indistinctement depuis les réseaux utilisateurs.

## 9.5. Exercice

Concevez une fiche réseau pour un hôte de virtualisation qui précise :

| Élément | Informations à fournir |
|---|---|
| Gestion | Réseau, adresse et sources autorisées |
| Machines virtuelles | VLAN ou réseaux virtuels utilisés |
| Stockage | Chemins, protocole et MTU |
| Migration | Réseau et conditions d'autorisation |
| Sauvegarde | Réseau et chemins utilisés |
| Redondance | Interfaces, liens et comportement attendu |
| Supervision | Métriques, journaux et alertes |

Justifiez chaque réseau et indiquez les dépendances en cas de panne.


# 10. Défi 6 — Concevoir le réseau de stockage

## 10.1. Choisir le type de stockage

La conception dépend de la technologie retenue.

### Stockage en blocs

Exemples de technologies : iSCSI ou NVMe over Fabrics.

Les hôtes accèdent à des volumes présentés par le système de stockage. La latence, la perte de paquets, le MTU et le multipathing peuvent être déterminants.

### Stockage en fichiers

Exemple : NFS.

Les hôtes ou les machines utilisent des fichiers accessibles par le réseau. Les droits, la disponibilité du service, le comportement en cas de coupure et la cohérence doivent être considérés.

### Stockage distribué

Plusieurs nœuds contribuent au stockage.

Il faut notamment tenir compte :

- De la latence entre les nœuds.
- De la bande passante.
- Du nombre de chemins.
- De la réplication.
- Du trafic de reconstruction.
- De l'impact d'une perte de nœud.
- De la capacité restante en cas de panne.

## 10.2. Principes de conception

Le réseau de stockage doit :

- Répondre aux besoins de performance.
- Disposer de chemins adaptés à la disponibilité requise.
- Être limité aux initiateurs autorisés.
- Éviter les communications arbitraires avec les réseaux utilisateurs.
- Être monitoré.
- Disposer d'une procédure de diagnostic.
- Utiliser un MTU cohérent de bout en bout.
- Prévoir le comportement pendant une panne.
- Être documenté selon la technologie utilisée.

## 10.3. MTU et grandes trames

Certaines architectures de stockage utilisent un MTU supérieur à 1500 octets.

Les grandes trames peuvent améliorer certains scénarios de transfert, mais seulement si tous les composants du chemin les prennent en charge correctement.

Vous devez vérifier :

- Les cartes réseau.
- Les commutateurs.
- Les interfaces des hyperviseurs.
- Le réseau de stockage.
- Les interfaces de la baie.
- Les chemins redondants.
- Les tunnels ou encapsulations éventuels.

Dans un réseau VXLAN, l'underlay doit également prendre en charge la taille du paquet transporté avec l'encapsulation. Il faut dimensionner le MTU d'après l'ensemble des en-têtes réellement utilisés et la configuration de la plateforme.

Ne modifiez pas le MTU sans mesurer le comportement et vérifier tous les équipements du chemin.

## 10.4. Exercice de panne de stockage

Simulez une panne de lien dans un environnement de test autorisé.

Observez :

1. Le comportement des chemins.
2. Les alertes reçues.
3. La latence.
4. Les erreurs.
5. Le mécanisme de bascule.
6. L'impact sur les machines virtuelles.
7. Les journaux du stockage et des hyperviseurs.
8. Le rétablissement après retour du lien.
9. L'absence de dégradation persistante.
10. Les corrections à apporter à la documentation.

Une architecture à deux liens n'est pas nécessairement redondante si les deux passent par le même composant ou le même chemin physique.


# 11. Défi 7 — Sauvegarde et reprise après incident

## 11.1. Distinguer stockage et sauvegarde

Le stockage de production fournit les données nécessaires au fonctionnement courant.

La sauvegarde sert à récupérer des données après une suppression, une corruption, une erreur humaine ou une compromission.

La réplication assure parfois une continuité plus rapide, mais elle peut également reproduire une corruption ou une suppression.

Ces fonctions ne sont pas interchangeables.

## 11.2. Architecture de sauvegarde

```text
                 +--------------------+
                 | MACHINES VIRTUELLES|
                 | PRODUCTION         |
                 +--------------------+
                           |
                     Sauvegarde
                           |
                           v
                 +--------------------+
                 | SERVEUR DE BACKUP  |
                 | Orchestration      |
                 +--------------------+
                           |
                           v
                 +--------------------+
                 | CIBLE DE BACKUP    |
                 | Accès limité       |
                 +--------------------+
                           |
              +------------+------------+
              |                         |
              v                         v
       Copie immuable             Copie hors site
       si disponible              ou site de secours
```

La cible de sauvegarde doit être protégée des comptes de production ordinaires.

Lorsque cela est possible, utilisez une solution immuable ou une copie disposant de contrôles d'accès distincts. Si un compte compromis peut supprimer à la fois les données originales et toutes les sauvegardes, l'architecture ne fournit pas une protection suffisante.

## 11.3. Objectifs RPO et RTO

Le **RPO** correspond à la quantité maximale de données que l'entreprise accepte de perdre dans le scénario étudié.

Le **RTO** correspond à la durée cible de remise en service du système après un incident.

Exemple purement pédagogique :

| Service | RPO cible | RTO cible |
|---|---|---|
| Application métier critique | À définir avec le métier | À définir avec le métier |
| Base de données | Dépend du mécanisme de sauvegarde ou de réplication | Dépend du processus de restauration |
| Environnement de test | Peut être plus souple | Peut être plus souple |
| Services de gestion | Dépend de l'impact d'une perte | Doit permettre de rétablir l'administration |
| Journaux de supervision | Selon les besoins d'enquête | Selon les objectifs de reprise |

Vous devez choisir les valeurs avec les responsables métier et démontrer qu'elles sont techniquement réalisables.

## 11.4. Exercice de restauration

Vous devez restaurer au moins une machine virtuelle ou un jeu de données représentatif.

Procédure :

1. Sélectionner une sauvegarde connue.
2. Vérifier son état.
3. Isoler l'environnement de restauration.
4. Restaurer la machine ou les fichiers.
5. Vérifier l'intégrité des données.
6. Démarrer le service selon une procédure contrôlée.
7. Tester les dépendances nécessaires.
8. Mesurer le temps de restauration.
9. Comparer le résultat au RTO cible.
10. Documenter les limites observées.

Ne considérez pas une sauvegarde comme validée tant qu'une restauration représentative n'a pas été effectuée.


# 12. Défi 8 — Haute disponibilité

## 12.1. Identifier les points uniques de panne

Un datacenter peut dépendre de plusieurs composants critiques :

- Un seul pare-feu.
- Un seul commutateur.
- Un lien unique vers le stockage.
- Une seule carte réseau sur un serveur.
- Un seul fournisseur électrique.
- Une seule cible de sauvegarde.
- Une seule connexion Internet.
- Un seul système d'authentification.
- Un seul chemin de gestion.
- Une configuration dont personne d'autre ne connaît les détails.

Chaque dépendance doit être évaluée selon son impact sur l'activité.

## 12.2. Redondance des équipements réseau

La redondance peut porter sur :

- Les liens physiques.
- Les commutateurs.
- Les chemins de routage.
- Les passerelles.
- Les pare-feu.
- Les liaisons vers l'extérieur.
- Les alimentations.
- Les chemins de stockage.

La redondance ne doit pas être ajoutée sans définition du comportement attendu lors d'une panne.

## 12.3. Architecture redondante de référence

```text
                     INTERNET / WAN
                            |
                     +--------------+
                     | PARE-FEU A   |
                     +--------------+
                            ||
                      Mécanisme HA
                            ||
                     +--------------+
                     | PARE-FEU B   |
                     +--------------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
          +-----------+           +-----------+
          | FABRIC /  |           | CHEMINS   |
          | CŒUR A    |===========| REDONDANTS|
          +-----------+           +-----------+
                |                       |
                +-----------+-----------+
                            |
                    Hôtes de virtualisation
                            |
                  +---------+---------+
                  |                   |
                  v                   v
            Stockage chemin A   Stockage chemin B
```

Ce schéma illustre l'objectif. Le mécanisme HA réel du pare-feu et les fonctions du cœur doivent correspondre aux capacités du matériel choisi.

Deux équipements identiques ne garantissent pas une continuité automatique. Il faut vérifier la synchronisation de l'état, les chemins, les adresses, le routage, les règles et le comportement après bascule.

## 12.4. Exercices de panne

Dans un environnement de laboratoire autorisé, étudiez l'effet des événements suivants :

- Perte d'un lien entre serveur et commutateur.
- Perte d'un chemin vers le stockage.
- Panne d'un commutateur.
- Perte d'une passerelle.
- Bascule du pare-feu.
- Perte d'un hôte de virtualisation.
- Indisponibilité de la cible de sauvegarde.
- Perte du réseau d'administration.
- Perte du réseau OOB.

Pour chaque scénario, indiquez :

1. Ce qui doit continuer à fonctionner.
2. Ce qui peut subir une interruption.
3. Comment la panne est détectée.
4. Quel mécanisme assure la reprise.
5. Comment l'équipe vérifie le rétablissement.
6. Comment éviter une perte de données ou une incohérence.
7. Comment revenir à l'état nominal.


# 13. Défi 9 — Supervision et journalisation

## 13.1. Éléments à superviser

| Domaine | Mesures utiles |
|---|---|
| Commutateurs | État des interfaces, erreurs, saturation et changements de topologie |
| Routage | Voisins BGP ou autres adjacences, routes et changements |
| Pare-feu | État, sessions, ressources et événements de sécurité |
| Hyperviseurs | CPU, mémoire, réseau, stockage et état du cluster |
| Machines virtuelles | Disponibilité, latence et consommation |
| Stockage | Latence, débit, erreurs, capacité et état des chemins |
| Sauvegarde | Résultat, durée, taille, âge des copies et tests de restauration |
| Réseau physique | Débits, pertes, erreurs et utilisation des liens |
| Supervision | Disponibilité de la collecte et rétention des données |
| OOB | Disponibilité et accès administratif |
| Énergie | État des alimentations et onduleurs lorsque ces fonctions sont disponibles |

Une bonne supervision doit être utile à la prise de décision. Collecter toutes les mesures possibles sans alertes ni seuils exploitables peut augmenter la charge sans améliorer le diagnostic.

## 13.2. Journalisation

Centralisez, lorsque les moyens le permettent :

- Les connexions administratives.
- Les changements de configuration.
- Les erreurs de routage.
- Les pertes de lien.
- Les changements de topologie.
- Les événements de stockage.
- Les échecs de sauvegarde.
- Les connexions refusées importantes.
- Les alertes de sécurité.
- Les changements des mécanismes de haute disponibilité.

Les horloges doivent être cohérentes afin de rapprocher les événements.

Les journaux doivent être protégés contre les modifications non autorisées, avec une durée de conservation définie selon les exigences de l'organisation.


# 14. Niveau expert — Architecture leaf-spine

Cette partie fait évoluer la conception vers une fabric de datacenter moderne.

Une architecture leaf-spine est intéressante lorsque les communications entre serveurs représentent une part importante du trafic, que la capacité doit évoluer et que la plateforme prend en charge les mécanismes nécessaires.

Elle n'est pas obligatoire pour tous les datacenters. Une architecture de cœur et d'accès bien conçue peut rester adaptée à une petite infrastructure.

## 14.1. Principe

Dans une fabric leaf-spine :

- Les leafs raccordent les serveurs, les hyperviseurs, les systèmes de stockage ou les équipements de bordure.
- Chaque leaf est relié à chaque spine de la fabric.
- Les spines transportent le trafic entre les leafs.
- Les connexions entre leafs et spines sont routées au niveau L3 dans une architecture moderne courante.
- L'underlay fournit la connectivité IP entre les équipements réseau de la fabric.
- Un overlay peut fournir des réseaux logiques au-dessus de cet underlay.

## 14.2. Schéma physique leaf-spine

```text
                      +----------------+
                      | SPINE-01       |
                      +----------------+
                        |   |   |   |
                +-------+   |   |   +-------+
                |           |   |           |
                v           v   v           v

             +--------+  +--------+  +--------+  +--------+
             | LEAF-1 |  | LEAF-2 |  | LEAF-3 |  | LEAF-4 |
             +--------+  +--------+  +--------+  +--------+
                |  |        |  |        |  |        |  |
                |  |        |  |        |  |        |  |
             Serveurs     Serveurs   Stockage     Services
             Rack A       Rack A     autorisé     de bordure

                ^           ^   ^           ^
                |           |   |           |
                +-----------+---+-----------+
                            |
                      +----------------+
                      | SPINE-02       |
                      +----------------+
```

Le diagramme est schématique : dans une fabric leaf-spine, chaque leaf se connecte à chaque spine. Les liens ne doivent pas être interprétés comme une simple chaîne ou comme des liaisons entre leafs successifs.

Une topologie réelle doit faire apparaître chacun des liens leaf-spine.

## 14.3. Schéma leaf-spine détaillé

```text
                 +----------------+      +----------------+
                 | SPINE-01       |      | SPINE-02       |
                 +----------------+      +----------------+
                    |\  \  \  \             /  /  /  /|
                    | \  \  \  \           /  /  /  / |
                    |  \  \  \  \         /  /  /  /  |
                    |   \  \  \  \       /  /  /  /   |
                    |    \  \  \  \     /  /  /  /    |
                    |     \  \  \  \   /  /  /  /     |
                    v      v  v  v     v  v  v  v
                 +--------+ +--------+ +--------+ +--------+
                 | LEAF-1 | | LEAF-2 | | LEAF-3 | | LEAF-4 |
                 +--------+ +--------+ +--------+ +--------+
                    |  |       |  |       |  |       |  |
                    v  v       v  v       v  v       v  v
                   Hôtes      Hôtes     Stockage   Services
                   Rack A     Rack B    autorisé   de bordure
```

Dans cette conception, chaque leaf possède des liens L3 vers les deux spines.

Les débits, la diversité physique et le nombre de ports doivent être définis à partir des besoins. Les spines sont généralement des éléments de transit de la fabric et ne servent pas à connecter directement les serveurs.

## 14.4. Pourquoi cette architecture est évolutive

Elle permet de développer le réseau en ajoutant des leafs et des liaisons vers les spines, sous réserve des capacités matérielles et des protocoles retenus.

Les avantages potentiels comprennent :

- Des chemins multiples entre les leafs.
- Une architecture adaptée au trafic est-ouest.
- Une évolution par ajout de leafs.
- Des mécanismes de routage et de convergence cohérents.
- La possibilité d'utiliser un overlay pour étendre les réseaux logiques.

La fabric n'élimine pas tous les points de panne. Un serveur raccordé à un seul leaf, un service sans réplication ou une cible de sauvegarde unique peut rester vulnérable à une panne.


# 15. Défi expert — Underlay IP et BGP

## 15.1. Rôle de l'underlay

L'underlay est le réseau IP de transport de la fabric.

Dans un modèle leaf-spine routé :

- Les liens leaf-spine sont des liens L3.
- Chaque lien possède son adressage IP.
- Les loopbacks servent souvent d'identifiants stables pour les sessions de routage ou les extrémités de tunnel.
- BGP ou un autre protocole de routage assure l'échange des routes nécessaires.
- Les chemins redondants permettent au trafic de circuler après une panne, dans les limites du mécanisme de convergence.

L'underlay doit rester compréhensible et testable indépendamment de l'overlay.

## 15.2. Plan d'adressage underlay

Pour cet exercice, utilisez :

- Bloc underlay : `10.255.0.0/16`.
- Liens point à point : sous-réseaux `/31`, si la plateforme les prend en charge.
- Loopbacks : `10.255.255.0/24`, attribuées individuellement.

Exemple de loopbacks :

| Équipement | Loopback |
|---|---|
| SPINE-01 | `10.255.255.1/32` |
| SPINE-02 | `10.255.255.2/32` |
| LEAF-01 | `10.255.255.11/32` |
| LEAF-02 | `10.255.255.12/32` |
| LEAF-03 | `10.255.255.13/32` |
| LEAF-04 | `10.255.255.14/32` |

Ces adresses sont réservées à l'underlay de l'exercice et ne doivent pas être réutilisées dans les réseaux de production.

## 15.3. Plan des liens leaf-spine

| Liaison | Réseau point à point | Adresse côté spine | Adresse côté leaf |
|---|---|---|---|
| SPINE-01 ↔ LEAF-01 | `10.255.0.0/31` | `10.255.0.0` | `10.255.0.1` |
| SPINE-02 ↔ LEAF-01 | `10.255.0.2/31` | `10.255.0.2` | `10.255.0.3` |
| SPINE-01 ↔ LEAF-02 | `10.255.0.4/31` | `10.255.0.4` | `10.255.0.5` |
| SPINE-02 ↔ LEAF-02 | `10.255.0.6/31` | `10.255.0.6` | `10.255.0.7` |
| SPINE-01 ↔ LEAF-03 | `10.255.0.8/31` | `10.255.0.8` | `10.255.0.9` |
| SPINE-02 ↔ LEAF-03 | `10.255.0.10/31` | `10.255.0.10` | `10.255.0.11` |
| SPINE-01 ↔ LEAF-04 | `10.255.0.12/31` | `10.255.0.12` | `10.255.0.13` |
| SPINE-02 ↔ LEAF-04 | `10.255.0.14/31` | `10.255.0.14` | `10.255.0.15` |

Ces réseaux point à point sont des valeurs pédagogiques. Confirmez la prise en charge des préfixes `/31` et la syntaxe du système d'exploitation réseau avant tout déploiement.

## 15.4. BGP dans l'underlay

BGP peut être utilisé pour annoncer les loopbacks et les routes nécessaires à la connectivité entre les équipements de la fabric.

Pour le challenge, adoptez le plan conceptuel suivant :

| Équipement | ASN privé d'exemple |
|---|---:|
| SPINE-01 | 65001 |
| SPINE-02 | 65002 |
| LEAF-01 | 65101 |
| LEAF-02 | 65102 |
| LEAF-03 | 65103 |
| LEAF-04 | 65104 |

Cette convention utilise des ASN privés d'exemple. Le choix entre eBGP, iBGP, les modèles d'AS et les mécanismes d'authentification dépend de la plateforme et de l'architecture.

### Travail demandé

Vous devez expliquer :

1. Pourquoi les liaisons leaf-spine sont routées.
2. Pourquoi les loopbacks sont utiles.
3. Quelles routes sont annoncées.
4. Comment les voisins BGP sont établis.
5. Comment la perte d'une session est détectée.
6. Comment les routes sont retirées après une panne.
7. Comment empêcher une annonce de préfixes non autorisés.
8. Comment vérifier la route réellement utilisée.

## 15.5. Contrôles à réaliser

Les commandes exactes varient selon les équipements. Le dossier doit inclure les commandes équivalentes à :

```text
show ip interface brief
show ip route
show bgp summary
show bgp ipv4 unicast
show interfaces counters
show logging
```

Ne recopiez pas ces commandes aveuglément. Certaines plateformes utilisent une syntaxe différente pour BGP, les compteurs et les tables de routage.

### Preuves attendues

- Chaque liaison leaf-spine est active.
- Les adresses de liens sont cohérentes.
- Les sessions de routage attendues sont établies.
- Les loopbacks nécessaires sont joignables.
- Les routes sont cohérentes.
- La perte d'un lien provoque le comportement prévu.
- Aucune route injustifiée n'est propagée.


# 16. Défi expert — VRF, VXLAN et EVPN

Cette partie est un approfondissement. Elle doit être abordée une fois que la segmentation par VLAN et l'underlay routé sont compris et maîtrisés.

## 16.1. Pourquoi utiliser un overlay ?

Dans un réseau traditionnel, l'extension des VLAN peut être limitée par les besoins de topologie, de gestion et d'exploitation.

Un overlay permet de construire des réseaux logiques au-dessus d'un underlay IP.

Dans une architecture VXLAN EVPN :

- VXLAN fournit l'encapsulation des trames Ethernet dans des paquets IP/UDP.
- VTEP désigne un point de terminaison de l'encapsulation VXLAN.
- EVPN est utilisé comme plan de contrôle pour échanger les informations nécessaires à la connectivité de l'overlay.
- Les VNI identifient les segments VXLAN.
- Les VRF séparent des tables de routage logiques.

L'architecture exacte dépend des fonctions prises en charge par les équipements et de la manière dont les passerelles sont déployées.

## 16.2. Schéma conceptuel

```text
                 OVERLAY : RÉSEAUX LOGIQUES
          +--------------------------------------+
          |                                      |
          | VNI 10110 : APPLICATIONS             |
          | VNI 10120 : BASES DE DONNÉES         |
          | VNI 10130 : DMZ                      |
          |                                      |
          +--------------------------------------+
                     |                 |
                     v                 v
                  +------+          +------+
                  | VTEP |          | VTEP |
                  |LEAF-1|          |LEAF-3|
                  +------+          +------+
                     |                 |
                     +--------+--------+
                              |
                       UNDERLAY IP
                       BGP / ROUTAGE
                              |
                       +-------------+
                       | SPINE LAYER |
                       +-------------+
```

Le dessin montre la séparation logique entre l'overlay et l'underlay. Le trafic VXLAN ne doit pas être traité comme un VLAN étendu sans contrôle : les routes, le MTU, les passerelles et les règles de sécurité doivent être conçus explicitement.

## 16.3. VRF proposées

Dans le cadre du challenge :

| VRF | Fonction |
|---|---|
| `VRF-PROD` | Applications et bases de données de production |
| `VRF-DMZ` | Services exposés ou intermédiaires |
| `VRF-MGMT` | Gestion logique des systèmes et de la fabric |
| `VRF-BACKUP` | Transport de sauvegarde |
| `VRF-TEST` | Développement et tests |

Le stockage peut rester dans un réseau dédié non routé ou utiliser une VRF dédiée selon la technologie, les besoins de connectivité et les recommandations du constructeur.

Le réseau OOB demeure physiquement séparé dans cette architecture. Le placer simplement dans une VRF de production ne fournirait pas la même isolation physique.

## 16.4. Exemple conceptuel de VNI

| VLAN | Rôle | VNI d'exemple |
|---:|---|---:|
| 110 | APP-PROD | 10110 |
| 120 | DB-PROD | 10120 |
| 130 | DMZ | 10130 |
| 140 | VIRT-MGMT | 10140 |
| 170 | MONITORING | 10170 |
| 180 | ADMIN-JUMP | 10180 |
| 190 | TEST-DEV | 10190 |

Les numéros de VNI sont des choix de conception pour l'exercice. Ils ne sont pas imposés par les identifiants VLAN.

Les segments de stockage et de sauvegarde doivent être conçus avec une attention particulière à l'isolation, au routage et aux exigences de leur protocole. Il ne faut pas les ajouter automatiquement à l'overlay sans vérifier que cela convient au produit de stockage et à l'architecture.

## 16.5. Passerelle distribuée

Certaines fabrics permettent une passerelle Anycast distribuée sur plusieurs leafs.

Le principe permet à un réseau logique d'utiliser une passerelle cohérente sur plusieurs points du réseau, selon la plateforme.

Les travaux demandés :

1. Expliquer la différence entre une passerelle centralisée et une passerelle distribuée.
2. Identifier les bénéfices et les contraintes.
3. Étudier le chemin du trafic entre deux machines virtuelles sur des leafs différents.
4. Déterminer où sont appliquées les politiques de sécurité.
5. Expliquer le comportement après une panne de leaf.
6. Valider la cohérence des adresses de passerelle et des règles associées.

Une passerelle distribuée ne remplace pas le contrôle des flux. Les politiques de filtrage doivent toujours être appliquées au point approprié.

## 16.6. Multihoming des serveurs

Un serveur peut être connecté à plusieurs leafs pour améliorer la disponibilité.

Le mécanisme doit être supporté par les commutateurs et le serveur. Selon la conception, cela peut faire intervenir :

- Une technologie de multichâssis.
- EVPN multihoming.
- LACP.
- Des mécanismes de redondance de liens.
- Des fonctions spécifiques de la plateforme.

Ne raccordez pas un serveur sur deux commutateurs indépendants en supposant que l'agrégation de liens fonctionnera automatiquement.

Vous devez préciser :

- Le mécanisme utilisé.
- Les paramètres identiques ou cohérents attendus.
- Le comportement en cas de perte d'un lien.
- Le comportement en cas de perte d'un leaf.
- Les commandes de vérification.
- La procédure de retour à l'état nominal.


# 17. Défi 10 — Segmentation multi-tenant

Si le datacenter héberge plusieurs clients ou plusieurs environnements de sécurité, il faut empêcher les tenants de communiquer sans autorisation.

## 17.1. Exemple de séparation

```text
                    +----------------------+
                    | FABRIC DATACENTER    |
                    +----------------------+
                       |                |
                       v                v
                 +-----------+    +-----------+
                 | TENANT A  |    | TENANT B  |
                 | VRF-A     |    | VRF-B     |
                 +-----------+    +-----------+
                      |                 |
                   VM-A1 / VM-A2     VM-B1 / VM-B2
                      |                 |
                   Réseaux A         Réseaux B

                 Aucun échange entre A et B
                 sauf service explicitement
                 autorisé et contrôlé.
```

La séparation logique des VRF réduit les possibilités de communication directe entre tenants, mais le routage, la publication de services partagés et les points de connexion externes doivent être contrôlés.

## 17.2. Services partagés

Des services peuvent être partagés entre tenants, par exemple :

- DNS.
- NTP.
- Supervision.
- Sauvegarde.
- Authentification.
- Accès Internet.

Chaque service partagé doit avoir une politique qui précise :

- Les tenants autorisés.
- Les adresses et ports nécessaires.
- Les restrictions d'accès.
- Les informations collectées.
- Les risques de fuite de données.
- Les conséquences d'une compromission du service.

Une route importée d'une VRF vers une autre doit être justifiée, limitée aux préfixes nécessaires et testée.


# 18. Défi 11 — IPv6 dans le datacenter

IPv6 doit être conçu explicitement lorsqu'il est utilisé.

Le dossier doit déterminer :

- Si IPv6 est activé.
- Quelles zones l'utilisent.
- Comment les adresses sont attribuées.
- Comment le routage fonctionne.
- Quelles règles de filtrage s'appliquent.
- Comment la supervision observe IPv6.
- Comment la DMZ et l'administration sont protégées.
- Comment les tunnels ou overlays transportent IPv6, si cette fonction est nécessaire.

Une politique de sécurité uniquement IPv4 n'est pas complète si des chemins IPv6 restent actifs.

Les protocoles de découverte de voisins et de configuration IPv6 doivent être pris en compte. Il ne faut pas bloquer aveuglément tout trafic IPv6 de contrôle sous prétexte qu'il n'est pas associé aux applications utilisateur.

## 18.1. Exercice

Pour chaque zone, fournissez :

1. Le statut IPv6.
2. Le préfixe utilisé, si applicable.
3. La passerelle.
4. La méthode d'attribution.
5. Les routes.
6. Les règles de filtrage.
7. Les mécanismes de supervision.
8. Les tests positifs et négatifs.

Si IPv6 n'est pas déployé, documentez cette décision et les prérequis nécessaires à une future adoption.


# 19. Défi 12 — Automatisation et gestion de configuration

Un datacenter peut comporter de nombreux équipements et configurations répétitives.

L'automatisation peut aider à :

- Générer un plan d'adressage.
- Déployer une configuration de VLAN.
- Vérifier les routes.
- Collecter des états d'interface.
- Comparer les configurations.
- Détecter des écarts par rapport au modèle attendu.
- Créer des rapports de conformité.
- Vérifier que les VLAN autorisés correspondent au plan.

L'automatisation doit être conçue pour éviter la propagation rapide d'une erreur.

## 19.1. Principes

Toute automatisation de configuration doit comprendre :

- Une source de vérité documentée.
- Une validation des données d'entrée.
- Des contrôles syntaxiques.
- Un environnement de test.
- Une méthode de déploiement par étapes.
- Une sauvegarde préalable.
- Une vérification après changement.
- Une procédure de retour arrière.
- Une journalisation.
- Une validation humaine adaptée au risque.

## 19.2. Exercice d'automatisation

Produisez un script ou un playbook qui réalise au moins l'une des opérations suivantes :

- Vérifier la présence des VLAN attendus.
- Vérifier l'état des voisins de routage.
- Détecter des trunks avec des VLAN non prévus.
- Contrôler le statut des interfaces.
- Collecter des informations sur les versions et les configurations.
- Comparer les paramètres observés à un fichier de référence.

Le programme doit distinguer :

- Un échec de connexion.
- Un résultat invalide.
- Une configuration réellement incorrecte.
- Une absence de données.
- Une différence qui nécessite une validation humaine.

Ne déployez pas automatiquement une modification destructive sur l'ensemble de la fabric à partir d'une simple comparaison de texte.


# 20. Défi 13 — Dépannage par couches et par plan

Le modèle OSI est utile, mais le diagnostic du datacenter doit aussi tenir compte de la fonction réseau concernée.

Il faut distinguer les problèmes de production, de gestion, de stockage, de sauvegarde, de routage et d'overlay.

## 20.1. Couches OSI

| Couche | Contrôles |
|---:|---|
| 7 — Application | État du service, authentification, erreurs applicatives |
| 6 — Présentation | TLS, certificats, encodage |
| 5 — Session | État et maintien de session |
| 4 — Transport | TCP/UDP, ports, retransmissions |
| 3 — Réseau | IP, routes, passerelles, BGP, VRF |
| 2 — Liaison | VLAN, MAC, trunks, STP, LACP |
| 1 — Physique | Optiques, câbles, alimentation, état du lien |

## 20.2. Plans de trafic

| Plan | Vérifications prioritaires |
|---|---|
| Production | VLAN, passerelles, routage, ACL et service applicatif |
| Gestion | Source autorisée, bastion, route et journalisation |
| OOB | Commutateur OOB, alimentation, accès matériel |
| Stockage | Chemins, MTU, multipathing, latence et erreurs |
| Sauvegarde | Connectivité, droits, capacité et état de la cible |
| Underlay | Interfaces L3, adresses, BGP et routes |
| Overlay | VTEP, VNI, EVPN, VRF et passerelles |
| Supervision | Collecte, rétention des mesures et état des agents |

## 20.3. Méthode de diagnostic

1. Définir le service attendu.
2. Déterminer le périmètre de l'incident.
3. Identifier le plan de trafic concerné.
4. Vérifier le chemin de bout en bout.
5. Examiner les compteurs et journaux.
6. Confirmer l'état du routage.
7. Vérifier les règles de sécurité.
8. Tester le service réel.
9. Modifier un élément à la fois.
10. Réaliser les tests positifs et négatifs.
11. Mettre à jour la documentation.

Ne concluez pas automatiquement que le problème provient du réseau simplement parce que l'application échoue. Le stockage, l'hyperviseur, le système d'exploitation ou le service lui-même peuvent être responsables.


# 21. Scénarios de dépannage

## Scénario A — Une machine virtuelle ne peut plus joindre sa passerelle

### Symptôme

Une VM reçoit une adresse IP mais ne peut pas joindre sa passerelle.

### Hypothèses

- Port group ou réseau virtuel incorrect.
- VLAN absent du trunk vers l'hyperviseur.
- Mauvaise adresse IP ou mauvais masque.
- Passerelle indisponible.
- SVI ou interface VLAN inactive.
- Table MAC incorrecte.
- Politique de filtrage.
- Problème de routage de la plateforme virtuelle.

### Démarche

1. Vérifier l'adresse IP de la VM.
2. Vérifier le réseau virtuel attribué à la VM.
3. Vérifier le VLAN configuré sur le port group.
4. Vérifier les VLAN autorisés sur le trunk.
5. Vérifier l'état de la passerelle.
6. Vérifier les tables ARP et MAC lorsque cela est pertinent.
7. Tester depuis une autre VM du même réseau.
8. Examiner les journaux de l'hyperviseur et du commutateur.
9. Corriger la cause démontrée.

### Preuve attendue

La VM doit joindre la passerelle et les services prévus sans rendre accessibles les réseaux qui doivent rester interdits.


## Scénario B — Une application ne peut plus joindre sa base de données

### Symptôme

Le serveur applicatif est actif, mais les requêtes vers la base échouent.

### Hypothèses

- ACL ou pare-feu.
- Route de retour absente.
- Mauvaise adresse DNS.
- Port de base de données bloqué.
- Service arrêté.
- Changement d'adresse IP.
- Problème de certificat ou d'authentification.
- Saturation ou panne de stockage.

### Démarche

1. Identifier la source, la destination et le port applicatif.
2. Vérifier la résolution DNS.
3. Contrôler les routes.
4. Vérifier les règles de filtrage.
5. Observer les connexions côté serveur et côté base.
6. Examiner les journaux du service.
7. Vérifier les ressources de la base.
8. Tester une requête représentative.
9. Confirmer que les flux interdits restent bloqués.

### Important

Ne remplacez pas une règle précise par une autorisation générale entre les deux VLAN pour rétablir l'application.


## Scénario C — Un serveur ne voit plus le stockage

### Symptôme

Un hôte perd l'accès à ses volumes ou voit ses chemins de stockage se dégrader.

### Hypothèses

- Lien physique défaillant.
- VLAN ou réseau de stockage incorrect.
- MTU incohérent.
- Configuration de multipathing.
- Port de baie inactif.
- Erreurs de carte réseau.
- Saturation.
- Problème de service de stockage.
- Modification non documentée.

### Démarche

1. Vérifier les alertes de stockage.
2. Examiner l'état des interfaces physiques.
3. Vérifier les chemins et leur statut.
4. Contrôler le MTU sur l'ensemble du chemin.
5. Examiner les compteurs et pertes.
6. Tester la connectivité selon la technologie.
7. Vérifier la configuration de l'initiateur et de la cible.
8. Examiner les événements sur la baie.
9. Vérifier si un chemin redondant continue de fonctionner.
10. Ne pas supprimer ou reformater de volumes pendant le diagnostic.

### Preuve attendue

Le service de stockage doit retrouver un état conforme, les chemins doivent être documentés et aucune opération destructive ne doit avoir été effectuée sans justification.


## Scénario D — Une session BGP tombe entre un leaf et un spine

### Symptôme

Un leaf perd un voisin BGP.

### Hypothèses

- Lien physique en panne.
- Adresse IP incorrecte.
- Mauvais ASN.
- Erreur de configuration du voisinage.
- MTU ou transport défaillant.
- Politique de filtrage.
- Problème de temporisation ou d'interface.
- Incohérence de configuration.

### Démarche

1. Vérifier l'état de l'interface.
2. Vérifier les adresses des deux extrémités.
3. Vérifier le voisin configuré.
4. Examiner l'état BGP.
5. Vérifier les routes vers les loopbacks si la session s'appuie dessus.
6. Lire les journaux.
7. Vérifier les filtres de préfixes.
8. Contrôler les routes après rétablissement.
9. Tester le comportement avec un autre chemin disponible.

### Preuve attendue

Les routes nécessaires sont disponibles via les chemins prévus et aucune annonce non autorisée n'a été acceptée.


## Scénario E — Une VM située sur un autre leaf ne reçoit plus le trafic

### Symptôme

Une machine virtuelle communique avec les VM locales mais pas avec un service hébergé sur un autre leaf.

### Hypothèses

- Underlay IP incorrect.
- Route BGP manquante.
- VTEP inaccessible.
- VNI incorrect.
- Route EVPN manquante.
- VRF incorrecte.
- Passerelle incohérente.
- Politique de filtrage.
- MTU insuffisant pour les paquets encapsulés.

### Démarche

1. Vérifier la connectivité underlay.
2. Vérifier les loopbacks des VTEP.
3. Vérifier les sessions de routage.
4. Vérifier la présence du VNI attendu.
5. Examiner les routes EVPN pertinentes.
6. Contrôler l'association du VLAN au VNI.
7. Vérifier la VRF utilisée.
8. Vérifier le MTU.
9. Examiner les politiques de sécurité.
10. Comparer avec un flux équivalent qui fonctionne.

### Important

Ne cherchez pas uniquement la panne dans l'overlay. Une défaillance underlay peut provoquer des symptômes qui ressemblent à un problème EVPN.


## Scénario F — Les sauvegardes saturent les liens pendant les heures de travail

### Symptôme

Les applications deviennent lentes lorsque les sauvegardes s'exécutent.

### Hypothèses

- Trafic de sauvegarde partagé avec la production.
- Capacité insuffisante.
- Absence de limitation ou de planification.
- Cible de sauvegarde saturée.
- Sauvegardes complètes mal planifiées.
- Réplication exécutée au même moment.
- Problème de stockage ou de compression.

### Démarche

1. Identifier les liens saturés.
2. Mesurer le débit de sauvegarde.
3. Vérifier la charge de la cible.
4. Examiner le planning des tâches.
5. Déterminer si la production utilise les mêmes chemins.
6. Tester les options de limitation de débit.
7. Ajuster la fenêtre de sauvegarde.
8. Mesurer les performances après modification.
9. Contrôler la durée totale de sauvegarde.
10. Vérifier que le RPO reste respecté.

Une limitation de débit ne doit pas être mise en œuvre sans vérifier que la fenêtre restante permet toujours de protéger les données dans les délais requis.


## Scénario G — Les interfaces de gestion deviennent inaccessibles

### Symptôme

L'équipe ne peut plus gérer les commutateurs ou les hyperviseurs.

### Hypothèses

- Bastion indisponible.
- Erreur de VLAN.
- Route de gestion absente.
- ACL trop restrictive.
- Service SSH ou HTTPS arrêté.
- Problème d'authentification.
- Panne du réseau OOB.
- Adresse IP de gestion modifiée.

### Démarche

1. Vérifier si l'incident concerne l'administration en bande, l'OOB ou les deux.
2. Vérifier la disponibilité du bastion.
3. Contrôler le chemin de gestion.
4. Examiner les règles et les journaux.
5. Vérifier les adresses de gestion.
6. Utiliser la voie d'accès de secours autorisée.
7. Rétablir un accès minimal et sécurisé.
8. Documenter la cause et les changements.

La procédure d'urgence doit permettre de rétablir l'administration sans exposer largement les interfaces de gestion aux réseaux de production.


# 22. Défi 14 — Wireshark et analyse des paquets

Wireshark peut aider à identifier les échanges réellement observés sur un point de capture.

Dans un datacenter, le point de capture est important. Une capture sur une VM ne voit pas nécessairement le trafic d'une autre VM, celui du stockage ou l'ensemble des échanges qui circulent dans la fabric.

## 22.1. Filtres d'affichage utiles

### ARP

```text
arp
```

### ICMP

```text
icmp
```

### DNS

```text
dns
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
ip.addr == 10.60.20.20
```

### Flux entre deux serveurs

```text
ip.addr == 10.60.10.20 && ip.addr == 10.60.20.20
```

### Port TCP spécifique

```text
tcp.port == 443
```

Ces expressions sont des filtres d'affichage Wireshark. Les filtres de capture ont une syntaxe différente.

## 22.2. Exercice de connexion TCP

1. Lancer une capture sur un point adapté.
2. Établir une connexion de test.
3. Identifier le SYN.
4. Chercher le SYN-ACK.
5. Vérifier l'ACK.
6. Examiner les échanges suivants.
7. Rechercher les retransmissions.
8. Comparer avec les journaux du pare-feu ou du serveur.

Une connexion qui échoue peut être due à un refus, une absence de réponse, une route incorrecte ou un service arrêté. La capture doit être interprétée avec le contexte.

## 22.3. Exercice de congestion

Pendant une opération de transfert autorisée :

1. Mesurer le débit.
2. Examiner les retransmissions.
3. Vérifier les compteurs d'interface.
4. Identifier les liens saturés.
5. Comparer les chemins de production et de sauvegarde.
6. Corréler les mesures avec les journaux.
7. Proposer une correction.
8. Mesurer à nouveau.

Un petit nombre de paquets ne permet pas toujours de conclure à une congestion. Utilisez des mesures cohérentes et suffisamment représentatives.


# 23. Défi 15 — Gestion des changements

Une configuration réseau peut être correcte pendant des mois puis être altérée par une modification mal planifiée.

Le datacenter doit disposer d'un processus de changement adapté au risque.

## 23.1. Procédure de changement

Chaque modification importante doit contenir :

1. Un objectif documenté.
2. L'identification des équipements concernés.
3. Une analyse des impacts.
4. Une sauvegarde préalable.
5. Les tests avant changement.
6. Les étapes d'exécution.
7. Les tests de validation.
8. Une procédure de retour arrière.
9. Les critères d'arrêt.
10. La personne responsable.
11. Le résultat final.
12. La mise à jour de la documentation.

## 23.2. Exemple de changement

Vous devez ajouter un nouveau VLAN pour une application interne.

Avant le changement, vérifiez :

- Le réseau IP prévu.
- Le rôle de la nouvelle zone.
- La VRF éventuelle.
- Les trunks concernés.
- Les passerelles.
- Les routes.
- Les règles de filtrage.
- Les besoins de supervision.
- Les éventuelles dépendances de virtualisation.
- Les contraintes MTU.
- Les systèmes qui auront besoin d'accéder au service.

Après le changement, vérifiez :

- Que le VLAN est présent uniquement où nécessaire.
- Que les terminaux reçoivent la bonne configuration.
- Que le routage est correct.
- Que seuls les flux autorisés fonctionnent.
- Que les flux interdits restent bloqués.
- Que les journaux et alertes sont cohérents.


# 24. Défi expert — Incident global de datacenter

Vous êtes de garde lorsqu'une série d'incidents apparaît :

1. Certaines machines virtuelles ne joignent plus leur passerelle.
2. Les sessions BGP d'un leaf montrent des instabilités.
3. Une application ne peut plus accéder à sa base de données.
4. Les sauvegardes n'atteignent pas leur cible.
5. Le trafic de stockage présente des erreurs.
6. Les accès au bastion d'administration sont dégradés.

Vous ne savez pas si ces incidents ont une cause commune.

## 24.1. Règles de l'intervention

Vous devez :

- Préserver les preuves.
- Identifier le périmètre.
- Prioriser les services critiques et les expositions de sécurité.
- Ne pas reconfigurer toute la fabric.
- Ne pas désactiver globalement les politiques de filtrage.
- Ne pas modifier le MTU sans mesures.
- Ne pas supprimer les configurations sans sauvegarde.
- Ne pas effectuer de tests destructifs sur le stockage de production.
- Documenter chaque modification.
- Utiliser la voie d'administration de secours lorsque nécessaire.

## 24.2. Tableau de collecte

| Symptôme | Domaine | Première vérification |
|---|---|---|
| VM sans passerelle | VLAN / hyperviseur / routage | IP, port group, VLAN, passerelle |
| BGP instable | Underlay | Interface, adresse, voisin et journaux |
| Application vers base en échec | Routage / filtrage / service | Destination, port, route et journaux |
| Sauvegarde inaccessible | Réseau backup / cible | Connectivité, authentification, capacité |
| Erreurs de stockage | Réseau stockage / baie | Chemins, MTU, compteurs et événements |
| Bastion dégradé | Administration | Services, routes, charge et journaux |

## 24.3. Première phase — Isoler les incidents

Pour chaque incident, déterminez :

- Le nombre d'équipements affectés.
- Le moment de début.
- Les modifications récentes.
- Le chemin réseau utilisé.
- Le plan de trafic concerné.
- Le service exact en échec.
- Les éléments qui continuent de fonctionner.

Ne supposez pas que tous les symptômes possèdent une cause commune.

## 24.4. Deuxième phase — Vérifier les dépendances

Exemples :

- Une VM sans passerelle peut être affectée par son VLAN, son port group ou le réseau virtuel.
- Un BGP instable peut refléter un problème physique ou une configuration de routage.
- Une application incapable de joindre une base peut rencontrer un problème d'ACL ou un service défaillant.
- Une sauvegarde en échec peut être affectée par le réseau, l'authentification ou la cible.
- Le trafic de stockage peut être perturbé par un MTU incohérent ou la perte d'un chemin.
- Un bastion indisponible peut bloquer l'administration sans empêcher tout le trafic de production.

## 24.5. Troisième phase — Corriger et valider

Pour chaque correction :

1. Énoncez l'hypothèse.
2. Recueillez une preuve.
3. Identifiez le changement minimal.
4. Sauvegardez la configuration.
5. Effectuez le changement.
6. Vérifiez le résultat.
7. Contrôlez les effets secondaires.
8. Réalisez les tests de non-régression.
9. Documentez la cause racine.

La cause racine doit être étayée par les faits, pas seulement par une explication plausible.

## 24.6. Rapport final

Le rapport de l'incident doit contenir :

- La chronologie.
- Les symptômes.
- Le périmètre.
- Les hypothèses.
- Les preuves recueillies.
- Les changements réalisés.
- La cause démontrée.
- Les tests après correction.
- Les conséquences sur la disponibilité.
- Les risques résiduels.
- Les actions de prévention.


# 25. Architecture cible consolidée

## 25.1. Vue globale

Le schéma suivant rassemble les principaux composants du datacenter.

```text
                            INTERNET / WAN
                                  |
                           +--------------+
                           | PARE-FEU HA  |
                           +--------------+
                                  |
                            LIENS DE BORDURE
                                  |
                    +---------------------------+
                    | FABRIC LEAF-SPINE         |
                    | Underlay IP / Routage     |
                    | Overlay optionnel         |
                    +---------------------------+
                       |        |        |
                       |        |        |
                       v        v        v
                   +-------+ +-------+ +--------+
                   | LEAF 1| | LEAF 2| | LEAF 3 |
                   +-------+ +-------+ +--------+
                       |        |        |
                       v        v        v
                    Hôtes de virtualisation
                         |           |
                         |           |
                         v           v
                    PROD / DMZ     STOCKAGE
                         |
                         v
                    Bases de données


              RÉSEAU DE SAUVEGARDE SÉPARÉ
                         |
                         v
                 Serveur de sauvegarde
                         |
                         v
                    Cible protégée


              RÉSEAU OOB PHYSIQUEMENT SÉPARÉ
                         |
                         v
                 Bastion d'administration
                         |
            +------------+-------------+
            |            |             |
            v            v             v
          BMC          Switches      Baie / PDU
```

Ce schéma est un résumé de la cible. Dans le dossier final, fournissez un schéma plus détaillé qui montre les liens entre chaque spine et leaf, les raccordements serveurs, les chemins de stockage et les équipements de bordure.

## 25.2. Résumé des décisions

| Domaine | Décision de référence |
|---|---|
| Architecture simple | Cœur et accès, avec séparation des rôles |
| Architecture avancée | Leaf-spine routée |
| Underlay | Routage IP et BGP dans le scénario expert |
| Overlay | VXLAN EVPN si le besoin et le matériel le justifient |
| Production | Réseaux applicatifs segmentés |
| DMZ | Réseau distinct et filtrage vers l'interne |
| Bases de données | Accès limité aux applications autorisées |
| Gestion | Bastion et réseau d'administration |
| OOB | Chemins physiques distincts |
| Stockage | Réseaux et politiques dédiés |
| Sauvegarde | Réseau contrôlé et cible protégée |
| Virtualisation | VLAN et port groups documentés |
| Sécurité | Matrice de flux explicite |
| Haute disponibilité | Redondance testée selon les exigences |
| Supervision | Mesures et journaux centralisés |
| Automatisation | Validation, déploiement progressif et retour arrière |


# 26. Barème d'évaluation sur 100 points

| Domaine | Points |
|---|---:|
| Analyse des besoins et inventaire | 6 |
| Architecture physique | 8 |
| Segmentation VLAN et plan IP | 8 |
| Routage et chemins de communication | 8 |
| Sécurité de la DMZ et des bases | 10 |
| Virtualisation et port groups | 8 |
| Stockage et MTU | 8 |
| Sauvegarde et restauration | 8 |
| Redondance et disponibilité | 8 |
| Supervision et journalisation | 5 |
| Underlay BGP et architecture leaf-spine | 8 |
| VRF, VXLAN EVPN et multihoming | 7 |
| Dépannage et analyse de paquets | 5 |
| Documentation et gestion des changements | 3 |
| **Total** | **100** |

Le niveau expert doit être évalué selon la cohérence et la justesse de la conception, pas simplement selon le nombre de technologies citées.

Une solution classique bien justifiée peut obtenir une bonne note même si VXLAN EVPN n'est pas retenu, à condition que le périmètre du challenge et les exigences soient respectés.

## 26.1. Erreurs graves

Les erreurs suivantes doivent entraîner une pénalité importante :

- Exposer directement une base de données à Internet sans justification ni protection appropriée.
- Autoriser tous les flux entre les réseaux de production.
- Rendre les interfaces OOB accessibles depuis les réseaux utilisateurs.
- Confondre réseau de stockage et réseau de sauvegarde.
- Considérer une copie répliquée comme une sauvegarde suffisante sans analyser les risques.
- Croire qu'une paire de liens assure automatiquement la haute disponibilité.
- Ajouter des trunks sans limiter les VLAN.
- Utiliser un MTU non vérifié de bout en bout.
- Mettre en place BGP sans filtrer les annonces nécessaires.
- Déployer VXLAN sans vérifier l'underlay.
- Effectuer des changements sans sauvegarde ni retour arrière.
- Valider les tests sans conserver de preuve.


# 27. Modèle du dossier final

## 27.1. Résumé exécutif

Présentez :

- L'objectif du datacenter.
- Le périmètre.
- L'architecture retenue.
- Les décisions principales.
- Les bénéfices attendus.
- Les principaux risques et limites.

## 27.2. Architecture physique

Fournissez un schéma indiquant :

- Les pare-feu.
- Les commutateurs.
- Les racks.
- Les serveurs.
- Les équipements de stockage.
- Les chemins de sauvegarde.
- Les liens de bordure.
- Les liens redondants.
- Le réseau OOB.
- Les dépendances électriques critiques.

## 27.3. Architecture logique

Fournissez :

- Le plan de VLAN.
- Le plan IP.
- Les VRF.
- La matrice de flux.
- Les réseaux de gestion.
- Les réseaux de stockage.
- Les réseaux de sauvegarde.
- Les passerelles.
- Les zones de sécurité.
- Les mécanismes de routage et d'overlay, si utilisés.

## 27.4. Dossier de routage

Documentez :

- Les routes principales.
- Les voisins de routage.
- Les loopbacks.
- Les sous-réseaux point à point.
- Les filtres de préfixes.
- Les mécanismes de convergence.
- Les procédures de diagnostic.
- Les comportements attendus en cas de panne.

Pour BGP, le dossier doit spécifier les sessions attendues, les préfixes autorisés, les politiques d'annonce et les éléments permettant de confirmer la convergence.

## 27.5. Dossier de sécurité

Documentez :

- Les flux autorisés et interdits.
- Les règles de la DMZ.
- Les accès aux bases de données.
- La politique d'administration.
- La séparation OOB.
- Les règles d'accès au stockage.
- La protection des sauvegardes.
- La journalisation.
- La politique IPv6.
- Les procédures de gestion des comptes.

N'incluez pas de mots de passe, clés privées, jetons ou autres secrets réels dans le dossier partagé.

## 27.6. Dossier de continuité

Précisez :

- Les services critiques.
- Les RPO et RTO.
- Les composants redondants.
- Les points uniques de panne.
- Les procédures de bascule.
- Les procédures de restauration.
- Les dépendances du site de secours.
- Les résultats des tests.
- Les limites restantes.

## 27.7. Tableau de validation

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | Connectivité underlay | Routes et voisins conformes | À renseigner | À exécuter |
| T02 | Connexion à une application interne autorisée | Service fonctionnel | À renseigner | À exécuter |
| T03 | Connexion DB depuis réseau non autorisé | Refusée | À renseigner | À exécuter |
| T04 | Administration depuis le bastion | Autorisée selon les droits | À renseigner | À exécuter |
| T05 | Administration depuis un réseau utilisateur | Refusée | À renseigner | À exécuter |
| T06 | Chemin de stockage redondant | Comportement conforme au plan | À renseigner | À exécuter |
| T07 | Perte d'un lien leaf-spine | Convergence conforme au plan | À renseigner | À exécuter |
| T08 | Accès aux interfaces OOB | Limité aux sources prévues | À renseigner | À exécuter |
| T09 | Restauration d'une VM de test | Service restauré et vérifié | À renseigner | À exécuter |
| T10 | Isolation entre tenants | Aucun flux non autorisé | À renseigner | À exécuter |
| T11 | MTU de stockage | Chemin conforme à la conception | À renseigner | À exécuter |
| T12 | Collecte de journaux | Événements disponibles | À renseigner | À exécuter |

Un statut « OK » doit être associé à un test effectivement exécuté et à une preuve vérifiable.


# 28. Checklist finale

## Architecture

- [ ] Les exigences métier sont documentées.
- [ ] Les services critiques sont identifiés.
- [ ] L'architecture physique est cohérente.
- [ ] L'architecture logique correspond au schéma physique.
- [ ] Les réseaux de production et de gestion sont distincts.
- [ ] Le réseau de stockage est conçu selon la technologie utilisée.
- [ ] La sauvegarde est séparée du stockage de production.
- [ ] Les points uniques de panne sont identifiés.
- [ ] Les besoins de capacité sont mesurés.

## Routage

- [ ] Les sous-réseaux ne se chevauchent pas.
- [ ] Les passerelles sont documentées.
- [ ] Les routes de retour existent.
- [ ] Les flux sont contrôlés.
- [ ] Les voisins BGP sont documentés lorsqu'ils sont utilisés.
- [ ] Les préfixes annoncés sont limités.
- [ ] L'underlay est vérifié indépendamment de l'overlay.
- [ ] Les routes et politiques de VRF sont cohérentes.

## Sécurité

- [ ] La DMZ est séparée.
- [ ] Les bases de données ne sont accessibles que depuis les sources prévues.
- [ ] Les accès d'administration sont contrôlés.
- [ ] Le réseau OOB est isolé.
- [ ] Les VRF ou autres mécanismes d'isolation sont documentés.
- [ ] Les règles IPv4 et IPv6 sont cohérentes.
- [ ] Les journaux sont collectés et protégés.
- [ ] Les flux autorisés et interdits ont été testés.

## Virtualisation et stockage

- [ ] Les VLAN des machines virtuelles sont documentés.
- [ ] Les trunks sont limités.
- [ ] Le trafic de migration est contrôlé.
- [ ] Les chemins de stockage sont redondants selon le besoin.
- [ ] Le MTU est cohérent de bout en bout.
- [ ] Les alertes de stockage sont testées.
- [ ] Les procédures de panne sont documentées.

## Sauvegarde et disponibilité

- [ ] Les sauvegardes sont exécutées selon une planification définie.
- [ ] Les échecs sont détectés.
- [ ] Les copies sont protégées contre les suppressions non autorisées.
- [ ] Une restauration représentative a été testée.
- [ ] Les objectifs RPO et RTO sont documentés.
- [ ] Les mécanismes de bascule sont testés.
- [ ] Les procédures de retour à l'état nominal sont disponibles.

## Exploitation

- [ ] Les configurations sont sauvegardées.
- [ ] Les journaux et mesures sont disponibles.
- [ ] Les changements sont documentés.
- [ ] Les procédures d'urgence sont accessibles.
- [ ] L'équipe maîtrise le retour arrière.
- [ ] Les schémas correspondent à l'état réel du réseau.
- [ ] Les limites et risques résiduels sont déclarés.


# 29. Références techniques à consulter

Les références suivantes permettent d'approfondir les mécanismes employés dans le challenge :

- **RFC 1918 — Address Allocation for Private Internets** : plages IPv4 privées.
- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : fonctionnement de BGP.
- **RFC 7348 — Virtual eXtensible Local Area Network (VXLAN)** : encapsulation VXLAN.
- **RFC 7432 — BGP MPLS-Based Ethernet VPN** : concepts et mécanismes EVPN.
- **RFC 8365 — A Network Virtualization Overlay Solution Using EVPN** : utilisation d'EVPN dans les architectures d'overlay.
- **IEEE 802.1Q** : VLAN et pontage Ethernet.
- **Documentation du constructeur** : architecture leaf-spine, BGP, EVPN, multihoming, MTU et mécanismes de redondance.
- **Documentation de l'hyperviseur** : vSwitch, port groups, migration, gestion et réseaux de stockage.
- **Documentation du système de stockage** : multipathing, connectivité, MTU, réplication et restauration.
- **Documentation Wireshark** : capture et analyse des paquets.
- **Documentation de la solution de sauvegarde** : restauration, copies immuables, contrôle des accès et rapports de validation.

Les configurations finales doivent être vérifiées dans la documentation de la plateforme utilisée. Les fonctions BGP, VXLAN EVPN, multihoming et haute disponibilité peuvent différer fortement selon le matériel et les versions logicielles.


# Conclusion

Ce challenge doit démontrer qu'un datacenter n'est pas uniquement un ensemble de serveurs raccordés à des commutateurs.

C'est une infrastructure composée de plusieurs plans de trafic, de réseaux de sécurité, de systèmes de stockage, de mécanismes de virtualisation, de procédures de sauvegarde et de fonctions d'exploitation.

La réussite repose sur cinq principes :

1. **Une architecture compréhensible :** les rôles, les liens et les dépendances sont documentés.
2. **Une segmentation justifiée :** les réseaux sont séparés en fonction des besoins et des risques.
3. **Une disponibilité démontrée :** les mécanismes de redondance sont testés.
4. **Une sécurité vérifiable :** les flux autorisés et interdits sont prouvés.
5. **Une exploitation maîtrisée :** supervision, sauvegarde, restauration et retour arrière sont documentés.

L'architecture leaf-spine, BGP et VXLAN EVPN peut apporter une évolutivité importante lorsqu'elle répond aux besoins du datacenter. Elle doit toutefois reposer sur un underlay stable, un plan d'adressage rigoureux, une politique de sécurité explicite et une équipe capable de l'exploiter.

La meilleure architecture est celle dont les choix sont justifiés, dont les pannes sont anticipées et dont le fonctionnement peut être mesuré et démontré.