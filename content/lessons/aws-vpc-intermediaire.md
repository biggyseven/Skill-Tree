# AWS VPC — Cours complet de niveau intermédiaire

## Concevoir, sécuriser, connecter, observer et dépanner des réseaux AWS

**Nom du fichier :** `aws-vpc-intermediaire.md`  
**Domaine :** Réseaux cloud, architecture AWS et sécurité réseau  
**Niveau :** Intermédiaire  
**Public cible :** Administrateurs systèmes et réseaux, techniciens cloud, ingénieurs débutants sur AWS et apprenants préparant une spécialisation réseau cloud  
**Durée indicative :** 12 à 18 heures, ateliers et révisions compris  
**Prérequis :** Avoir étudié un cours AWS VPC débutant et savoir expliquer les adresses IPv4/CIDR, les sous-réseaux, les tables de routage, Internet Gateway, NAT Gateway, Security Groups et Network ACL  
**Approche pédagogique :** Explications détaillées, schémas textuels, tableaux, exemples, ateliers guidés, commandes de diagnostic, exercices corrigés et challenge final

> **Objectif du document :** apprendre à construire et exploiter une architecture réseau AWS réaliste à plusieurs sous-réseaux et zones de disponibilité, à limiter les communications autorisées, à fournir un accès privé aux services AWS et à diagnostiquer méthodiquement une panne réseau.
>
> Tout le cours, les ateliers, les exercices, le challenge final et sa correction se trouvent dans **ce seul fichier Markdown**. Aucun fichier annexe n'est nécessaire.


# Sommaire

1. Positionnement du niveau intermédiaire
2. Architecture de référence utilisée dans le cours
3. Concevoir un plan d'adressage IPv4 évolutif
4. Comprendre les tables de routage et le choix d'une route
5. Construire une architecture publique/privée sur deux zones
6. Concevoir une politique de sécurité par couches
7. Comprendre les NAT Gateways, leur résilience et leurs coûts
8. Accéder aux services AWS sans passer par Internet
9. Connecter plusieurs VPC avec VPC Peering
10. DNS et résolution de noms dans un VPC
11. Introduction pratique à IPv6 dans VPC
12. Observer le réseau avec VPC Flow Logs
13. Diagnostiquer une connectivité avec Reachability Analyzer
14. Méthode structurée de dépannage réseau
15. Exploitation, gouvernance et contrôle des coûts
16. Ateliers guidés
17. Exercices de consolidation corrigés
18. Challenge final autonome
19. Correction détaillée du challenge
20. Évaluation, checklist et glossaire
21. Documentation officielle


# 1. Positionnement du niveau intermédiaire

## 1.1. Ce qui change par rapport au niveau débutant

Au niveau débutant, l'objectif principal est de comprendre les briques : VPC, sous-réseaux, routes, Internet Gateway, NAT Gateway, Security Groups et Network ACL.

Au niveau intermédiaire, il ne suffit plus de créer les ressources une par une. Il faut être capable de **concevoir une architecture cohérente**, de justifier les choix, de prévoir les pannes et de produire des éléments vérifiables.

Ce cours approfondit notamment :

- La planification des CIDR pour limiter les chevauchements futurs.
- La séparation en couches publiques, privées applicatives et privées de données.
- La résilience réseau sur plusieurs Availability Zones (AZ).
- Les chemins de sortie contrôlés pour les serveurs privés.
- Les VPC endpoints pour réduire le recours au NAT et à l'Internet public.
- Les limites du VPC Peering et les routes requises dans les deux sens.
- Les différences opérationnelles entre Security Groups et Network ACL.
- Le diagnostic par Flow Logs et Reachability Analyzer.
- La gouvernance, la documentation et le contrôle des coûts.

## 1.2. Compétences attendues à la fin du cours

À la fin de ce cours, l'apprenant doit être capable de :

1. Définir un plan CIDR pour deux zones de disponibilité sans chevauchement.
2. Associer chaque sous-réseau à une table de routage adaptée.
3. Expliquer, à partir d'un paquet et de sa destination, quelle route est sélectionnée.
4. Mettre en œuvre des règles de Security Groups fondées sur la source et la destination du flux.
5. Expliquer pourquoi les flux de retour ne sont pas gérés de la même façon par les Security Groups et les Network ACL.
6. Concevoir un accès Internet sortant pour des sous-réseaux privés sans les rendre directement accessibles depuis Internet.
7. Déterminer quand un VPC endpoint peut remplacer un chemin via NAT Gateway.
8. Relier deux VPC non chevauchants et diagnostiquer un VPC Peering incomplet.
9. Activer et interpréter les VPC Flow Logs dans les limites de ce service.
10. Utiliser une séquence de dépannage qui sépare les problèmes de routage, de filtrage, de DNS et d'application.
11. Présenter une architecture documentée, testable et exploitable.

## 1.3. Les cinq questions à poser pour chaque flux réseau

Avant de modifier une route ou un pare-feu, décrire le flux sous cette forme :

| Élément | Question | Exemple |
|---|---|---|
| Source | Qui initie la connexion ? | Serveur applicatif A |
| Destination | Vers quelle ressource ? | Service S3 ou serveur de données |
| Protocole/port | Quel protocole et quel port ? | TCP/5432 |
| Chemin | Par quelles routes et cibles ? | Route locale, endpoint, NAT ou peering |
| Autorisation | Quelles règles laissent passer le flux ? | SG applicatif, SG données, NACL |

Un test comme « ça ne marche pas » ne contient pas assez d'informations. Un diagnostic de qualité précise le sens du flux, le protocole, le port, la source attendue, la destination visée et le résultat observé.


# 2. Architecture de référence utilisée dans le cours

Nous allons utiliser une architecture fictive appelée **Orion**. Elle héberge une application web composée d'un point d'entrée, d'une couche applicative et d'une base de données. Elle doit répartir ses ressources sur deux zones de disponibilité.

## 2.1. Besoin fonctionnel

- Les utilisateurs Internet doivent accéder à l'application en HTTPS.
- Les serveurs applicatifs ne doivent pas être directement accessibles depuis Internet.
- Les bases de données ne doivent accepter que les connexions de la couche applicative.
- Les serveurs privés doivent pouvoir accéder à certains services AWS, par exemple S3, sans utiliser automatiquement un chemin Internet via NAT.
- Les journaux de flux doivent aider à analyser les incidents.
- L'architecture doit supporter la perte d'une AZ avec un impact réduit, sous réserve que les composants applicatifs et les données soient eux-mêmes conçus pour la résilience.

## 2.2. Plan d'adressage de l'exemple

VPC principal : `10.40.0.0/16`

| AZ | Rôle | Sous-réseau | CIDR | Type logique |
|---|---|---|---|---|
| AZ A | Entrée Web / Load Balancer | `orion-public-a` | `10.40.1.0/24` | Public |
| AZ B | Entrée Web / Load Balancer | `orion-public-b` | `10.40.2.0/24` | Public |
| AZ A | Application | `orion-app-a` | `10.40.11.0/24` | Privé avec sortie contrôlée |
| AZ B | Application | `orion-app-b` | `10.40.12.0/24` | Privé avec sortie contrôlée |
| AZ A | Base de données | `orion-data-a` | `10.40.21.0/24` | Privé isolé |
| AZ B | Base de données | `orion-data-b` | `10.40.22.0/24` | Privé isolé |
| AZ A | Outils d'administration facultatifs | `orion-ops-a` | `10.40.31.0/24` | Privé |
| AZ B | Outils d'administration facultatifs | `orion-ops-b` | `10.40.32.0/24` | Privé |

Les sous-réseaux de cet exemple sont tous contenus dans `10.40.0.0/16` et ne se chevauchent pas. Les `/24` sont choisis pour faciliter la lecture pédagogique, pas parce que tous les sous-réseaux de production doivent être des `/24`.

## 2.3. Vue globale de l'architecture

```text
                                INTERNET
                                   |
                          [ DNS public / clients ]
                                   |
                          +-------------------+
                          | Application Load  |
                          | Balancer (ALB)    |
                          +-------------------+
                              |           |
                    +---------+           +---------+
                    |                                 |
                 AZ A                              AZ B
      +-------------------------+      +-------------------------+
      | subnet public-a         |      | subnet public-b         |
      | 10.40.1.0/24            |      | 10.40.2.0/24            |
      +-------------------------+      +-------------------------+
                    |                                 |
                    v                                 v
      +-------------------------+      +-------------------------+
      | subnet app-a            |      | subnet app-b            |
      | 10.40.11.0/24           |      | 10.40.12.0/24           |
      | EC2 / service applicatif|      | EC2 / service applicatif|
      +-------------------------+      +-------------------------+
                    |                                 |
                    v                                 v
      +-------------------------+      +-------------------------+
      | subnet data-a           |      | subnet data-b           |
      | 10.40.21.0/24           |      | 10.40.22.0/24           |
      | Base de données         |      | Base de données         |
      +-------------------------+      +-------------------------+

       Routage et sécurité sont définis séparément pour chaque couche.
```

**Point important :** l'ALB est représenté dans les sous-réseaux publics, mais les serveurs applicatifs ne le sont pas. Dans une architecture réelle, un Application Load Balancer public doit être associé à des sous-réseaux adaptés dans au moins deux zones de disponibilité. Les groupes de sécurité doivent autoriser le trafic de l'ALB vers les cibles, et non ouvrir les serveurs applicatifs à tout Internet.

## 2.4. Vue logique des couches de sécurité

```text
Internet
   |
   | HTTPS/443 autorisé
   v
[ SG-ALB : entrée HTTPS depuis Internet ]
   |
   | HTTP/8080 ou HTTPS/8443, selon l'application
   | Source autorisée : SG-ALB
   v
[ SG-APP : entrée uniquement depuis SG-ALB ]
   |
   | TCP/5432, exemple PostgreSQL
   | Source autorisée : SG-APP
   v
[ SG-DATA : entrée uniquement depuis SG-APP ]
```

Les ports `8080`, `8443` et `5432` sont des exemples illustratifs. Ils doivent être remplacés par les ports réellement utilisés par l'application et le moteur de base de données.


# 3. Concevoir un plan d'adressage IPv4 évolutif

## 3.1. Pourquoi planifier au-delà du premier VPC ?

Une plage CIDR peut être suffisante aujourd'hui et devenir gênante demain, par exemple lorsqu'on souhaite connecter :

- Plusieurs VPC par peering.
- Un réseau local à AWS par VPN.
- Un réseau de transit partagé.
- Des comptes AWS différents.
- Un environnement de développement, de test et de production.

Les plages qui se chevauchent compliquent certaines formes de routage privé. Deux VPC aux CIDR qui se chevauchent ne peuvent pas établir un VPC Peering classique.

Il est donc préférable de prévoir le plan d'adressage avant de multiplier les réseaux.

## 3.2. Exemple de plan global

```text
Organisation fictive ORION
|
+-- Réseau local : 172.20.0.0/16
|
+-- AWS Production : 10.40.0.0/16
|
+-- AWS Préproduction : 10.50.0.0/16
|
+-- AWS Développement : 10.60.0.0/16
|
+-- Services partagés : 10.70.0.0/16
```

Ce tableau est uniquement un exemple. Il ne constitue pas une plage universelle à copier. Le plan doit être adapté aux réseaux existants, aux autres comptes et aux exigences de croissance.

## 3.3. Réserver les blocs par fonction

Pour chaque VPC, on peut réserver des plages par usage :

```text
VPC Production 10.40.0.0/16
|
+-- 10.40.0.0/20    Réserve pour sous-réseaux publics
+-- 10.40.16.0/20   Réserve pour la couche applicative
+-- 10.40.32.0/20   Réserve pour les données
+-- 10.40.48.0/20   Réserve pour administration/outils
+-- Autres blocs     Expansion future
```

Ce découpage n'est pas obligatoire. Son intérêt est de rendre les choix compréhensibles et de limiter l'improvisation. Il faut vérifier mathématiquement l'alignement et l'absence de chevauchement avant d'utiliser un plan réel.

## 3.4. Taille de sous-réseau et adresses disponibles

La taille doit être basée sur la capacité nécessaire et les réserves futures. Dans AWS, cinq adresses IPv4 par sous-réseau sont réservées. La capacité réelle dépend donc du nombre total d'adresses et de ces réservations.

Exemples théoriques :

| CIDR | Total d'adresses | Adresses IPv4 non réservées par AWS, à titre de calcul simple |
|---|---:|---:|
| `/24` | 256 | 251 |
| `/25` | 128 | 123 |
| `/26` | 64 | 59 |
| `/27` | 32 | 27 |
| `/28` | 16 | 11 |

Ces valeurs constituent un repère de capacité, et non une garantie que chaque adresse pourra être affectée à n'importe quelle ressource dans toutes les circonstances. Les besoins des services déployés et les réservations propres à certaines fonctions doivent aussi être pris en compte.

## 3.5. Vérifier un plan CIDR avant de déployer

Pour chaque sous-réseau, vérifier les points suivants :

1. Le CIDR est contenu dans le CIDR du VPC.
2. Il ne chevauche aucun autre sous-réseau du même VPC.
3. Il est associé à la zone de disponibilité prévue.
4. Sa capacité suffit aux interfaces et ressources attendues.
5. Il laisse de la place à la croissance.
6. Il ne crée pas de chevauchement problématique avec les réseaux que l'on prévoit de connecter.

### Exercice 3.1 — Détecter un chevauchement

Un VPC utilise `10.40.0.0/16`. Le concepteur prévoit les sous-réseaux suivants :

```text
A = 10.40.1.0/24
B = 10.40.2.0/24
C = 10.40.2.128/25
D = 10.40.11.0/24
```

Questions :

1. Quels sous-réseaux se chevauchent ?
2. Propose une plage pour C qui ne chevauche ni A, ni B, ni D.

**Correction :** B (`10.40.2.0/24`) couvre toute la plage `10.40.2.0` à `10.40.2.255`. C (`10.40.2.128/25`) est incluse dans B ; le chevauchement est donc invalide pour deux sous-réseaux distincts du même VPC. On peut remplacer C par `10.40.3.0/24` si cette plage est libre.


# 4. Comprendre les tables de routage et le choix d'une route

## 4.1. Rôle d'une table de routage

Une table de routage contient des routes. Chaque route indique une destination et une cible (target).

Exemple :

| Destination | Cible | Sens pratique |
|---|---|---|
| `10.40.0.0/16` | `local` | Trafic vers le VPC |
| `0.0.0.0/0` | Internet Gateway | Route IPv4 par défaut vers Internet |
| `0.0.0.0/0` | NAT Gateway | Route IPv4 par défaut vers la sortie NAT |
| `10.50.0.0/16` | VPC Peering | Trafic vers le VPC appairé |
| Préfixe de service AWS | VPC endpoint | Trafic vers le service correspondant, selon le type d'endpoint |

Une route ne crée pas à elle seule une autorisation de sécurité. Les Security Groups, les Network ACL et les contrôles du service de destination doivent également permettre la communication.

## 4.2. Route locale

AWS crée une route locale pour la plage du VPC. Elle permet aux sous-réseaux du VPC de router le trafic IPv4 destiné à cette plage dans le VPC.

Exemple :

```text
VPC : 10.40.0.0/16
Route locale : 10.40.0.0/16 -> local
```

Cette route ne remplace pas les règles des Security Groups ou des Network ACL.

## 4.3. Routage public

Une table de routage publique typique en IPv4 peut ressembler à ceci :

```text
Table : rtb-public
+----------------+--------------------------+
| Destination    | Cible                    |
+----------------+--------------------------+
| 10.40.0.0/16   | local                    |
| 0.0.0.0/0      | igw-xxxxxxxx             |
+----------------+--------------------------+
```

Pour qu'une instance IPv4 communique directement avec Internet, le chemin doit être cohérent : route vers l'Internet Gateway, adressage public adapté et règles de sécurité autorisant le trafic. Une route `0.0.0.0/0 -> IGW` seule ne rend pas toutes les instances automatiquement joignables depuis Internet.

## 4.4. Routage privé via NAT Gateway

Une table de routage de sous-réseau applicatif peut être :

```text
Table : rtb-app-a
+----------------+--------------------------+
| Destination    | Cible                    |
+----------------+--------------------------+
| 10.40.0.0/16   | local                    |
| 0.0.0.0/0      | nat-xxxxxxxx             |
+----------------+--------------------------+
```

La NAT Gateway doit être une NAT Gateway publique dans un sous-réseau public, avec une route vers l'Internet Gateway et une adresse Elastic IP associée. Une instance privée utilise sa route vers la NAT Gateway pour initier des connexions IPv4 sortantes.

Ce mécanisme ne signifie pas que l'instance privée devient accessible directement depuis Internet. La NAT Gateway ne permet pas les connexions entrantes spontanées initiées par un hôte Internet vers cette instance privée.

## 4.5. Routage d'un VPC vers un autre VPC

Pour router le trafic vers un VPC appairé, les routes doivent être configurées des deux côtés.

Exemple :

```text
VPC A : 10.40.0.0/16
VPC B : 10.50.0.0/16
Peering : pcx-abcd1234
```

Dans le VPC A :

```text
10.40.0.0/16 -> local
10.50.0.0/16 -> pcx-abcd1234
```

Dans le VPC B :

```text
10.50.0.0/16 -> local
10.40.0.0/16 -> pcx-abcd1234
```

Ajouter seulement la route dans A ne suffit pas pour établir une communication bidirectionnelle complète. Il faut aussi vérifier les Security Groups, les Network ACL et le bon état de la connexion de peering.

## 4.6. La route la plus spécifique

Lorsque plusieurs routes correspondent à une destination, AWS suit les règles de sélection des routes, notamment le principe du préfixe le plus spécifique. Une route vers un bloc plus petit est plus spécifique qu'une route par défaut.

Exemple conceptuel :

```text
10.40.0.0/16  -> local
10.50.0.0/16  -> pcx-abcd1234
0.0.0.0/0     -> nat-xxxxxxxx
```

Pour une destination `10.50.8.12`, la route `10.50.0.0/16` est plus spécifique que `0.0.0.0/0`. Le trafic suit donc la route vers le peering, sous réserve de la validité du chemin et des contrôles de sécurité.

**Méthode pratique :** lire la destination IP, identifier toutes les routes applicables, déterminer la route sélectionnée, puis vérifier que sa cible est disponible et que le trafic est autorisé.

## 4.7. Sous-réseau et table de routage associée

Un sous-réseau utilise une table de routage explicitement associée ou, s'il n'a pas d'association explicite, la table principale (main route table) du VPC.

C'est un point de dépannage important : une route peut être correcte dans une table, mais le sous-réseau peut être associé à une autre table.

Checklist :

- Quel est le sous-réseau source ?
- Quelle table lui est effectivement associée ?
- Quelle route correspond à la destination ?
- La cible de route est-elle disponible ?
- Existe-t-il une route de retour ?
- Les règles de sécurité autorisent-elles le flux ?


# 5. Construire une architecture publique/privée sur deux zones

## 5.1. Principe d'une architecture à plusieurs couches

Une architecture de production courante sépare :

1. L'entrée utilisateur (par exemple un ALB public).
2. Les serveurs applicatifs privés.
3. Les bases de données privées, sans route Internet par défaut.
4. Les services transverses : journalisation, administration, services AWS privés, monitoring.

```text
                           INTERNET
                              |
                        [ ALB public ]
                         /          \
                        /            \
                    AZ A              AZ B
                     |                 |
               [ App A ]           [ App B ]
                     |                 |
               [ Data A ]          [ Data B ]

Entrée : HTTPS uniquement vers ALB
ALB -> application : port applicatif dédié
Application -> données : port de base uniquement
Données -> Internet : aucune route par défaut, sauf besoin explicitement validé
```

## 5.2. Tables de routage attendues

### Sous-réseaux publics

Les sous-réseaux publics associés à l'ALB utilisent une route IPv4 par défaut vers l'IGW.

```text
rtb-public
10.40.0.0/16 -> local
0.0.0.0/0     -> IGW
```

### Sous-réseaux applicatifs privés

Si les instances applicatives doivent récupérer des mises à jour ou accéder à des destinations IPv4 publiques, on peut leur fournir une sortie contrôlée via NAT Gateway.

```text
rtb-app-a
10.40.0.0/16 -> local
0.0.0.0/0     -> NAT Gateway de l'AZ A
```

```text
rtb-app-b
10.40.0.0/16 -> local
0.0.0.0/0     -> NAT Gateway de l'AZ B
```

Il est aussi possible de choisir une architecture sans NAT pour certaines charges, par exemple si elles ont uniquement besoin de services AWS accessibles par endpoints et n'ont aucun besoin de sortie Internet générale.

### Sous-réseaux de données

Si les bases de données ne doivent pas initier de connexions Internet, leur table peut être minimale :

```text
rtb-data
10.40.0.0/16 -> local
```

Une table sans route par défaut vers Internet limite le routage vers des destinations extérieures au VPC, mais elle ne remplace pas les contrôles de sécurité. Les flux à l'intérieur du VPC doivent rester strictement filtrés par les Security Groups et, si pertinent, par les NACL.

## 5.3. Architecture textuelle complète

```text
VPC ORION : 10.40.0.0/16
|
+-- IGW : igw-orion
|
+-- AZ A
|   |
|   +-- Public A : 10.40.1.0/24
|   |   Route : local + 0.0.0.0/0 -> IGW
|   |   Rôle : nœud ALB, NAT Gateway publique si retenue
|   |
|   +-- App A : 10.40.11.0/24
|   |   Route : local + 0.0.0.0/0 -> NAT-A (si sortie Internet requise)
|   |   Rôle : instances applicatives
|   |
|   +-- Data A : 10.40.21.0/24
|       Route : local uniquement, plus routes explicitement justifiées
|       Rôle : base de données ou données privées
|
+-- AZ B
    |
    +-- Public B : 10.40.2.0/24
    |   Route : local + 0.0.0.0/0 -> IGW
    |   Rôle : nœud ALB, NAT Gateway publique si retenue
    |
    +-- App B : 10.40.12.0/24
    |   Route : local + 0.0.0.0/0 -> NAT-B (si sortie Internet requise)
    |   Rôle : instances applicatives
    |
    +-- Data B : 10.40.22.0/24
        Route : local uniquement, plus routes explicitement justifiées
        Rôle : base de données ou données privées
```

## 5.4. Pourquoi garder les serveurs d'application privés ?

Les serveurs applicatifs contiennent souvent du code métier, des identifiants de service et des accès aux données. Leur exposition directe accroît la surface d'attaque.

Une approche plus restrictive consiste à n'autoriser les requêtes entrantes que depuis le Security Group de l'ALB. Le point d'entrée public peut être accessible sur HTTPS, tandis que les serveurs applicatifs ne reçoivent pas de connexions directes depuis `0.0.0.0/0`.

## 5.5. Résilience entre AZ

Un bon dessin n'est pas nécessairement résilient. La résilience dépend entre autres :

- De la distribution des instances sur plusieurs AZ.
- De la capacité de l'application à fonctionner avec plusieurs instances.
- De la santé des cibles derrière l'ALB.
- De la réplication ou de la disponibilité de la base de données.
- Du choix des NAT Gateways.
- De la manière dont les routes sont configurées.
- Des mécanismes de déploiement, de sauvegarde et de reprise.

Un service qui possède deux sous-réseaux mais une seule instance dans une seule AZ reste dépendant de cette instance.


# 6. Concevoir une politique de sécurité par couches

## 6.1. Security Groups : contrôle au niveau des interfaces réseau

Les Security Groups sont des pare-feu virtuels associés aux interfaces réseau des ressources.

Rappels à retenir :

- Ils contiennent des règles d'autorisation, pas des règles explicites de refus.
- Ils sont stateful : les réponses d'une connexion autorisée sont traitées comme faisant partie de cette connexion suivie.
- Leurs règles sont agrégées lorsqu'une ressource utilise plusieurs Security Groups.
- Les règles peuvent référencer un autre Security Group lorsque le contexte réseau le permet.
- Un groupe neuf ne possède pas de règle entrante autorisant le trafic. Un ensemble de règles sortantes par défaut peut exister à la création ; il faut vérifier et appliquer le principe du moindre privilège.

## 6.2. Modèle de règles recommandé pour Orion

### SG-ALB

| Direction | Protocole/port | Source ou destination | Intention |
|---|---|---|---|
| Entrant | TCP/443 | `0.0.0.0/0` | Autoriser HTTPS depuis Internet |
| Sortant | TCP/8080 | `SG-APP` ou cibles autorisées selon la conception | Contacter les cibles applicatives |

Si IPv6 public est activé, réfléchir à la règle IPv6 équivalente uniquement si elle est réellement nécessaire. Une règle IPv4 ne couvre pas automatiquement IPv6.

### SG-APP

| Direction | Protocole/port | Source ou destination | Intention |
|---|---|---|---|
| Entrant | TCP/8080 | `SG-ALB` | Autoriser l'ALB à contacter l'application |
| Sortant | TCP/5432 | `SG-DATA` ou destination de base précise | Autoriser l'application à contacter les données |
| Sortant | TCP/443 | Endpoints ou destinations approuvées, selon la conception | Accès HTTPS nécessaire aux services |

Le port `8080` est un exemple. Ne pas ouvrir `8080` depuis tout Internet si seul l'ALB doit appeler les serveurs applicatifs.

### SG-DATA

| Direction | Protocole/port | Source ou destination | Intention |
|---|---|---|---|
| Entrant | TCP/5432 | `SG-APP` | Autoriser la couche applicative à contacter PostgreSQL |
| Sortant | Selon le besoin réel | Destinations approuvées | Limiter les connexions sortantes si la politique l'exige |

**Important :** `SG-DATA` accepte ici des connexions issues des interfaces associées à `SG-APP`, et non de toutes les adresses du VPC. Le port doit être adapté au moteur réellement utilisé.

## 6.3. Schéma des références de Security Groups

```text
                          Internet
                              |
                       TCP/443 autorisé
                              |
                       +--------------+
                       |    SG-ALB    |
                       +--------------+
                              |
              TCP/8080 : source = SG-ALB
                              |
                       +--------------+
                       |    SG-APP    |
                       +--------------+
                              |
              TCP/5432 : source = SG-APP
                              |
                       +--------------+
                       |   SG-DATA    |
                       +--------------+
```

Cette conception est plus robuste que des règles entrantes basées sur tout le CIDR du VPC, lorsque les flux sont bien limités à des rôles précis.

## 6.4. Security Groups et règles sortantes

Une erreur de configuration fréquente est de sécuriser uniquement l'entrée et de laisser toutes les sorties sans réflexion.

Pour réduire l'accès sortant, déterminer les besoins réels :

- DNS vers le résolveur DNS pris en charge par AWS (en tenant compte des limites spécifiques de filtrage DNS).
- HTTPS vers des API externes nécessaires.
- Accès à S3 ou à d'autres services AWS par endpoint.
- Connexion vers la base de données.
- Supervision, gestion ou mises à jour.

Ne supprime pas une règle sortante sans comprendre les dépendances. Une règle trop restrictive peut interrompre les mises à jour ou les appels API légitimes. Une règle trop large augmente le risque d'exfiltration ou de communication non attendue.

## 6.5. Network ACL : contrôle au niveau du sous-réseau

Les Network ACL (NACL) sont associées aux sous-réseaux. Elles peuvent autoriser ou refuser des flux, sont évaluées selon leurs numéros de règle et sont **stateless**.

Leur caractère stateless signifie que l'aller et le retour doivent être permis séparément. Une règle entrante autorisant TCP/443 ne suffit pas nécessairement à permettre la réponse sur un port éphémère.

Les NACL peuvent être utiles comme couche de défense complémentaire, notamment pour un garde-fou au niveau d'un sous-réseau. Elles sont souvent plus difficiles à maintenir lorsqu'on tente de reproduire, à grande échelle, toutes les règles d'une politique applicative.

## 6.6. Comparaison opérationnelle

| Critère | Security Group | Network ACL |
|---|---|---|
| Portée | Interface réseau / ressource associée | Sous-réseau |
| État | Stateful | Stateless |
| Règles de refus explicites | Non, règles d'autorisation | Oui |
| Ordre des règles | Pas de priorité séquentielle par numéro comme une NACL | Règles évaluées par numéro, la première correspondance applicable décide |
| Filtrage de retour | Réponses d'un flux autorisé gérées avec l'état de connexion | Le retour doit être autorisé explicitement par les règles dans l'autre direction |
| Usage fréquent | Contrôle principal des accès aux charges | Garde-fou réseau complémentaire |

## 6.7. Ports éphémères et NACL

Lorsqu'un client établit une connexion TCP, le port source du client est souvent un port éphémère. Si une NACL filtre le retour, il faut tenir compte de la plage de ports utilisée par le client et par le système concerné.

Exemple conceptuel :

```text
Client : 198.51.100.25:53000
       |
       | TCP destination port 443
       v
Serveur : 10.40.11.20:443
       |
       | Réponse TCP source 443 -> destination 53000
       v
Client
```

La valeur `53000` n'est qu'un exemple de port source. Ne copie pas une plage éphémère arbitraire dans une NACL de production : vérifie les systèmes et les flux réels, puis autorise la plage minimale nécessaire.

## 6.8. Matrice de flux avant mise en production

| Source | Destination | Port | Autorisé ? | Contrôle principal |
|---|---|---:|---|---|
| Internet | ALB | TCP/443 | Oui | SG-ALB |
| Internet | Serveur App | TCP/8080 | Non directement | SG-APP |
| ALB | Serveur App | TCP/8080 | Oui | SG-APP, source SG-ALB |
| Serveur App | Base PostgreSQL | TCP/5432 | Oui | SG-DATA, source SG-APP |
| Internet | Base de données | TCP/5432 | Non | SG-DATA et absence de chemin public |
| Serveur App | S3 | HTTPS/service AWS | Selon endpoint et politique | Routes, endpoint, SG/NACL lorsque applicables, politique IAM et bucket policy |

La matrice doit être tenue à jour. Lorsqu'une règle est ajoutée, elle doit correspondre à un besoin métier explicite.


# 7. NAT Gateways : sortie, résilience et coûts

## 7.1. Ce qu'une NAT Gateway fait

Une NAT Gateway publique permet à des ressources disposant uniquement d'adresses IPv4 privées d'initier des connexions vers l'extérieur, généralement Internet, sans accepter de nouvelles connexions entrantes spontanées depuis Internet vers ces ressources.

```text
Instance privée
10.40.11.25
     |
     | Route 0.0.0.0/0 -> NAT Gateway
     v
NAT Gateway publique
dans subnet public-a
     |
     | Route 0.0.0.0/0 -> IGW
     v
Internet
```

La NAT Gateway traduit les adresses et ports nécessaires. Elle ne constitue pas une règle de pare-feu applicative attachée à une instance : les Security Groups des instances restent importants.

## 7.2. Conditions pour une NAT Gateway publique fonctionnelle

Contrôler les éléments suivants :

1. La NAT Gateway a été créée comme NAT Gateway publique.
2. Elle se trouve dans un sous-réseau public.
3. Une Elastic IP a été associée lors de sa création.
4. La table de routage du sous-réseau de la NAT Gateway possède une route par défaut vers l'IGW.
5. La route des sous-réseaux privés pointe vers cette NAT Gateway.
6. Les Security Groups et les NACL n'empêchent pas le flux.
7. La destination Internet ou service distant est disponible.

Si un seul de ces éléments manque, le résultat peut être une absence de sortie, même si la ressource NAT affiche un état disponible.

## 7.3. NAT Gateway par AZ ou NAT Gateway partagée ?

### Option A — Une NAT Gateway dans chaque AZ

```text
AZ A                                AZ B
+-------------------------+         +-------------------------+
| subnet-app-a            |         | subnet-app-b            |
| 0.0.0.0/0 -> NAT-A       |         | 0.0.0.0/0 -> NAT-B       |
+------------+------------+         +------------+------------+
             |                                   |
             v                                   v
          [ NAT-A ]                           [ NAT-B ]
             |                                   |
             +---------------+-------------------+
                             |
                            IGW
                             |
                          Internet
```

Avantages possibles :

- Le chemin de sortie reste local à l'AZ dans une architecture correctement configurée.
- La dépendance à une seule AZ est réduite.
- Les flux évitent de traverser inutilement les AZ.

Inconvénient principal : coût plus élevé, car plusieurs NAT Gateways et leur trafic sont facturés selon la tarification en vigueur.

### Option B — Une NAT Gateway partagée

```text
AZ A: subnet-app-a ----\
                        +---- NAT-A (AZ A) ---- IGW ---- Internet
AZ B: subnet-app-b ----/
```

Cette architecture peut réduire certains coûts de ressource, mais elle crée une dépendance inter-AZ et un domaine de panne plus large. Si l'AZ qui héberge la NAT Gateway est indisponible, les sous-réseaux d'autres AZ qui l'utilisent peuvent perdre leur sortie Internet.

Il n'existe pas une réponse universelle : la décision dépend des objectifs de disponibilité, du trafic, du budget et des exigences de reprise.

## 7.4. Estimer les coûts sans inventer de prix

Les coûts exacts varient selon la région, la date et les services utilisés. Une estimation doit consulter la tarification AWS en vigueur.

Pour une NAT Gateway, examiner au minimum :

- Le coût horaire de la ressource.
- Le coût de traitement des données.
- Les frais de transfert de données applicables.
- Le trafic inter-AZ éventuellement généré.
- Le nombre de NAT Gateways nécessaires pour l'architecture.

Des endpoints adaptés peuvent diminuer le volume de trafic qui passerait autrement par une NAT Gateway, selon les services utilisés. Cette optimisation doit être évaluée avec les coûts d'endpoint, le volume réel et les besoins d'accès.

## 7.5. NAT ne remplace pas un VPC endpoint

La NAT Gateway est utile pour des destinations qui doivent être atteintes via le chemin de sortie IPv4 correspondant. Un endpoint permet d'accéder à certains services AWS depuis le VPC selon un chemin et un modèle de contrôle spécifiques.

Pour S3 et DynamoDB, les gateway endpoints peuvent permettre un accès sans Internet Gateway ni NAT Gateway. Pour d'autres services, les interface endpoints basés sur AWS PrivateLink peuvent être adaptés.

La bonne décision commence par la liste précise des destinations utilisées par les applications, et non par l'ajout automatique d'une NAT Gateway à chaque VPC.


# 8. Accéder aux services AWS sans passer par Internet

## 8.1. Pourquoi utiliser un VPC endpoint ?

Une instance privée peut devoir appeler un service AWS, par exemple récupérer un objet S3, pousser des métriques, utiliser une API AWS ou contacter un service de gestion.

Sans endpoint approprié, son chemin peut passer par une NAT Gateway pour atteindre un endpoint public du service. Cela introduit un chemin différent et peut entraîner des coûts de NAT ou un besoin de sortie Internet générale.

Les VPC endpoints permettent d'accéder à certains services AWS à travers un chemin pris en charge par AWS, sans exiger de passer par une Internet Gateway ou une NAT dans les cas couverts.

## 8.2. Les deux grandes catégories à connaître

### Gateway endpoints

Les gateway endpoints sont pris en charge pour Amazon S3 et Amazon DynamoDB. Ils s'appuient sur des entrées de routage dans les tables de routage choisies et ne reposent pas sur AWS PrivateLink.

```text
Instance privée
      |
      v
Table de routage du sous-réseau
      |
      +-- Route/prefix list du service -> Gateway endpoint
                                      |
                                      v
                              Amazon S3 ou DynamoDB
```

Les gateway endpoints ne nécessitent pas de NAT Gateway ou d'IGW pour le trafic vers ces services au travers de l'endpoint. Ils n'ont pas de frais supplémentaires d'utilisation de l'endpoint lui-même selon la documentation AWS actuelle ; les autres éléments facturables liés aux services ou transferts doivent toutefois être évalués séparément.

### Interface endpoints

Les interface endpoints créent des interfaces réseau privées dans les sous-réseaux sélectionnés et utilisent AWS PrivateLink pour certains services AWS ou services d'endpoint pris en charge.

```text
Instance privée
      |
      | connexion vers le nom DNS du service
      v
Interface endpoint (ENI privée)
      |
      v
Service AWS via PrivateLink
```

Les interface endpoints ont des considérations de coût différentes et nécessitent de vérifier les règles de sécurité, le DNS privé et la disponibilité de l'endpoint pour le service ciblé.

## 8.3. S3 gateway endpoint — démarche de configuration

L'objectif est de permettre à une instance privée de contacter S3 sans envoyer le trafic S3 par la route par défaut vers NAT.

Étapes conceptuelles :

1. Ouvrir la console Amazon VPC dans la région de travail.
2. Créer un VPC endpoint de type Gateway pour le service S3 approprié à la région.
3. Associer l'endpoint aux tables de routage des sous-réseaux qui doivent l'utiliser.
4. Examiner la politique de l'endpoint, si elle est définie.
5. Vérifier les permissions IAM de l'instance ou de son rôle.
6. Vérifier la politique du bucket S3 et les conditions éventuelles.
7. Tester l'accès à un bucket autorisé, idéalement via un rôle IAM temporaire et des permissions minimales.
8. Vérifier les journaux et le comportement réseau.

### Schéma avant endpoint

```text
Instance privée -> NAT Gateway -> IGW -> endpoint public S3
```

### Schéma après gateway endpoint

```text
Instance privée -> route associée au gateway endpoint -> S3
```

L'existence d'un endpoint ne garantit pas automatiquement qu'une requête S3 soit autorisée. Le routage, la politique de l'endpoint, IAM, la politique du bucket et les autres contrôles applicables doivent être cohérents.

## 8.4. Endpoint de type interface : points à vérifier

Pour un interface endpoint, examiner :

- La région et le service pris en charge.
- Les sous-réseaux dans lesquels créer les interfaces endpoint.
- Le Security Group associé à ces interfaces.
- Les règles sortantes de la ressource cliente et les règles entrantes de l'endpoint.
- Le DNS privé activé ou non, lorsque le service le permet et selon le scénario.
- La résolution du nom du service depuis l'instance.
- La politique de l'endpoint lorsque disponible.
- Les frais horaires et les frais de traitement des données de l'endpoint.

## 8.5. Endpoint, IAM et sécurité : quatre contrôles distincts

Il faut distinguer ces questions :

| Contrôle | Question |
|---|---|
| Routage | Le trafic peut-il atteindre l'endpoint ? |
| Sécurité réseau | Les règles autorisent-elles la connexion ? |
| IAM | L'identité a-t-elle le droit d'effectuer l'action AWS ? |
| Politique du service | Le bucket, le secret ou la ressource accepte-t-il cette requête ? |

Un problème d'autorisation IAM ne se résout pas en ajoutant une route. Un problème de résolution DNS ne se résout pas nécessairement en modifiant la politique S3.


# 9. Connecter plusieurs VPC avec VPC Peering

## 9.1. À quoi sert un VPC Peering ?

Un VPC Peering connecte deux VPC afin de permettre le routage entre leurs ressources à l'aide de leurs adresses privées, sous réserve des routes, des Security Groups et des NACL.

Exemple : une application en production doit accéder à un service partagé, ou un VPC de développement doit joindre une ressource dédiée de test.

## 9.2. Préconditions à valider

Avant de créer le peering :

1. Les plages CIDR ne doivent pas se chevaucher.
2. La connexion doit être demandée puis acceptée lorsque l'acceptation est requise.
3. Les tables de routage doivent contenir les routes vers le CIDR du VPC pair.
4. Les règles de sécurité doivent autoriser les flux attendus.
5. La résolution DNS doit être configurée si l'utilisation des noms privés l'exige.
6. Les deux côtés doivent être documentés et testés.

## 9.3. Exemple de deux VPC

```text
VPC PROD                           VPC SERVICES
10.40.0.0/16                       10.70.0.0/16
+-------------------+              +-------------------+
| App : 10.40.11.20 |              | API : 10.70.4.30  |
+-------------------+              +-------------------+
          |                                  |
          +---------- VPC Peering ------------+
```

Routes côté PROD :

```text
10.40.0.0/16 -> local
10.70.0.0/16 -> pcx-prod-services
```

Routes côté SERVICES :

```text
10.70.0.0/16 -> local
10.40.0.0/16 -> pcx-prod-services
```

Si l'application en production doit accéder à l'API sur TCP/8443, une règle entrante du SG de l'API peut autoriser TCP/8443 avec le SG applicatif source, si cette référence est prise en charge dans la configuration de peering et le contexte retenu. Sinon, utiliser un CIDR source précis conforme à la stratégie réseau.

## 9.4. Le peering n'est pas transitif

Supposons :

```text
VPC A <---- peering ----> VPC B <---- peering ----> VPC C
```

Cela ne signifie pas que VPC A peut automatiquement utiliser VPC B comme routeur pour atteindre VPC C.

```text
          VPC A
             |
          Peering
             |
          VPC B
             |
          Peering
             |
          VPC C

A -> C en transit via B : NON, pas par défaut avec le VPC Peering classique
```

Le peering est une relation un-à-un pour le routage et ne fournit pas le routage transitif. Si une organisation doit relier de nombreux VPC de façon centralisée, examiner AWS Transit Gateway ou d'autres options de connectivité supportées. Ce sujet dépasse les objectifs détaillés du présent cours, mais constitue la suite logique au niveau avancé.

## 9.5. Pourquoi le CIDR est critique

Une connexion de peering classique ne peut pas être établie entre deux VPC dont les plages IPv4 ou IPv6 se chevauchent. La planification de l'adressage est donc une précondition, pas un simple détail administratif.

## 9.6. Dépannage d'un peering qui ne fonctionne pas

Vérifier dans l'ordre :

1. État de la connexion : active, acceptée si nécessaire.
2. CIDR des deux VPC et absence de chevauchement.
3. Route du CIDR distant dans la table du sous-réseau source.
4. Route de retour dans la table du sous-réseau destination.
5. Security Group source : sortie autorisée.
6. Security Group destination : entrée autorisée.
7. NACL des deux sous-réseaux et ports de retour si elles sont restrictives.
8. DNS privé et paramètres de résolution si l'accès utilise un nom au lieu d'une IP.
9. Application réellement à l'écoute sur le port attendu.
10. VPC Flow Logs et Reachability Analyzer si disponibles pour ce chemin.


# 10. DNS et résolution de noms dans un VPC

## 10.1. Le rôle du DNS

Le DNS transforme un nom en informations permettant de localiser un service. Dans une architecture cloud, un problème DNS peut ressembler à un problème réseau : le serveur n'atteint pas le service parce que le nom ne se résout pas ou se résout vers une destination inattendue.

Exemples de symptômes :

- La connexion par adresse IP fonctionne, mais pas par nom.
- Un service AWS se résout vers un endpoint public alors qu'un endpoint privé était attendu.
- Les noms d'instances privées ne sont pas résolus depuis un autre VPC.
- Une application conserve une ancienne adresse en cache.

## 10.2. Paramètres DNS du VPC

Un VPC possède des paramètres DNS qui influencent l'utilisation du résolveur DNS fourni par AWS et la prise en charge des noms d'hôtes DNS. Lorsqu'un service s'appuie sur les noms DNS privés, vérifier les paramètres de résolution nécessaires dans le VPC et, le cas échéant, les paramètres de la connexion inter-VPC.

Ne présume pas qu'une connexion réseau fonctionnelle implique automatiquement que le même nom privé soit résolu de la même manière depuis tous les VPC.

## 10.3. Méthode de diagnostic DNS

Sur une instance Linux, selon les outils installés :

```bash
getent hosts service.exemple.internal
nslookup service.exemple.internal
```

ou :

```bash
dig service.exemple.internal
```

Interpréter le résultat :

- **Nom résolu avec une adresse attendue :** poursuivre le diagnostic réseau si la connexion échoue.
- **NXDOMAIN ou nom absent :** vérifier le nom, la zone, l'association et les enregistrements.
- **Timeout DNS :** vérifier l'accès au résolveur et la configuration locale, en gardant à l'esprit les particularités DNS d'AWS.
- **Adresse inattendue :** vérifier le type d'enregistrement, les zones, les réponses privées/publiques et les caches.

Les commandes exactes varient selon le système et les paquets disponibles. L'absence d'une commande (`dig`, `nslookup`) ne prouve pas à elle seule une panne DNS.

## 10.4. DNS et endpoints

Lorsqu'un interface endpoint utilise la résolution DNS privée, le nom DNS normal du service peut être résolu vers les interfaces privées de l'endpoint, selon les paramètres et le service pris en charge.

Lors du dépannage, ne teste pas uniquement la connectivité vers une IP copiée depuis un écran : vérifie également la résolution du nom effectivement utilisé par l'application.


# 11. Introduction pratique à IPv6 dans VPC

## 11.1. IPv4 et IPv6 doivent être traités séparément

Une route IPv4 par défaut `0.0.0.0/0` ne configure pas automatiquement le routage IPv6. Les plages, les routes, les règles de sécurité et les options d'accès doivent être vérifiées séparément.

En IPv6, une route par défaut vers une Internet Gateway peut permettre l'accès Internet lorsque les adresses et les règles sont configurées. Pour permettre à des ressources IPv6 d'initier du trafic vers Internet sans être joignables directement par de nouvelles connexions entrantes, un egress-only internet gateway peut être approprié.

## 11.2. Exemples de routes IPv6

```text
Routes IPv4
10.40.0.0/16 -> local
0.0.0.0/0    -> nat-xxxxxxxx   (si sortie IPv4 via NAT)

Routes IPv6, exemple conceptuel
Plage IPv6 du VPC -> local
::/0             -> egress-only IGW (pour sortie IPv6 seulement)
```

Cette table est illustrative. La configuration doit correspondre aux capacités du sous-réseau, au type de connectivité IPv6, au service cible et aux exigences de sécurité.

## 11.3. Attention au double périmètre de sécurité

Si l'application est configurée en double pile IPv4/IPv6, vérifier que les règles de Security Groups et de Network ACL couvrent les protocoles et plages réellement nécessaires dans les deux familles d'adresses.

Une instance peut sembler privée en IPv4 tout en disposant d'un chemin IPv6 public si l'architecture et les règles le permettent. Ne pas supposer que l'absence d'adresse IPv4 publique protège automatiquement l'instance sur IPv6.

## 11.4. Questions de validation IPv6

- Le VPC possède-t-il un bloc IPv6 associé ?
- Le sous-réseau est-il correctement configuré pour IPv6 ?
- L'interface de la ressource possède-t-elle l'adresse IPv6 prévue ?
- La table de routage contient-elle la route IPv6 nécessaire ?
- La règle de sécurité autorise-t-elle le flux IPv6 ?
- Le DNS retourne-t-il une adresse IPv6 lorsqu'attendu ?
- Le service distant est-il joignable en IPv6 ?


# 12. Observer le réseau avec VPC Flow Logs

## 12.1. Qu'est-ce qu'un VPC Flow Log ?

VPC Flow Logs capture des informations sur le trafic IP qui entre dans ou sort des interfaces réseau d'un VPC, d'un sous-réseau ou d'une interface réseau (ENI), selon la portée de la configuration.

Les données peuvent être publiées vers des destinations prises en charge telles que CloudWatch Logs, Amazon S3 ou Amazon Data Firehose. Flow Logs est utile pour diagnostiquer certains problèmes de connectivité, comprendre le trafic et examiner les rejets réseau.

Flow Logs ne capture pas le contenu intégral des paquets comme le ferait une capture applicative avec un analyseur de paquets. Il fournit des métadonnées de flux selon le format choisi.

## 12.2. Les états ACCEPT et REJECT

Dans les enregistrements classiques, le champ `action` peut notamment indiquer :

- `ACCEPT` : le trafic a été autorisé par les contrôles réseau observés dans le contexte du flux.
- `REJECT` : le trafic a été rejeté par un contrôle réseau observé.

Il faut interpréter le champ dans son contexte. Un enregistrement `ACCEPT` ne prouve pas que l'application a répondu correctement, qu'un port écoute, que l'authentification a réussi ou que la requête a atteint le service métier.

Un enregistrement `REJECT` permet d'orienter le diagnostic vers un contrôle réseau, mais il faut examiner le sens, les adresses, le port et les règles concernées.

## 12.3. Exemple de champs utiles

Un format de Flow Logs peut contenir des champs tels que :

```text
version account-id interface-id
srcaddr dstaddr srcport dstport protocol
packets bytes start end action log-status
```

La forme et l'ordre des champs dépendent du format configuré. Ne copie pas un exemple brut comme s'il s'agissait d'un schéma universel applicable à toutes les configurations : consulte la liste exacte des champs choisis dans la configuration de Flow Logs.

## 12.4. Exemple d'interprétation

Flux attendu :

```text
ALB / source autorisée -> App 10.40.11.20:8080
```

Scénario A : Flow Logs indique un `REJECT` sur le flux TCP/8080.

Pistes :

1. Vérifier le Security Group de l'application et sa règle entrante.
2. Vérifier le SG associé réellement à l'interface réseau de l'instance.
3. Vérifier les NACL des sous-réseaux source et destination.
4. Vérifier que le test correspond bien à la bonne adresse et au bon port.

Scénario B : Flow Logs indique `ACCEPT`, mais la connexion échoue toujours.

Pistes :

1. Vérifier que le service écoute sur le bon port.
2. Vérifier le pare-feu du système d'exploitation, le conteneur ou le processus.
3. Vérifier la résolution DNS.
4. Vérifier les journaux applicatifs et les health checks.
5. Confirmer que le flux observé correspond à la tentative en échec, et non à un autre flux.

## 12.5. Limitations à connaître

Flow Logs n'est pas une capture de tout le trafic sans exception. Certains types de trafic sont exclus de la journalisation et certains enregistrements peuvent être absents. Il faut aussi tenir compte du délai d'agrégation et de publication.

Par conséquent :

- L'absence d'un enregistrement ne prouve pas systématiquement l'absence de trafic.
- Il peut y avoir un délai entre un test et la disponibilité de l'enregistrement.
- Les valeurs affichées doivent être interprétées selon la configuration réelle des champs.
- Flow Logs ne remplace pas les journaux applicatifs, les métriques et les tests de connectivité.

## 12.6. Procédure de mise en place d'un Flow Log

1. Déterminer la portée : VPC entier, sous-réseau ou interface réseau.
2. Déterminer la destination des logs : CloudWatch Logs, S3 ou autre destination supportée.
3. Vérifier les permissions et les rôles nécessaires à la publication.
4. Choisir un format de champs adapté au diagnostic et à la conservation requise.
5. Prévoir rétention, chiffrement, accès et coût de stockage/ingestion.
6. Générer un trafic de test connu.
7. Rechercher la combinaison adresse source, destination, ports, protocole, heure et action.
8. Documenter les résultats avec la correction apportée.


# 13. Diagnostiquer une connectivité avec Reachability Analyzer

## 13.1. Rôle de l'outil

AWS VPC Reachability Analyzer est un outil d'analyse statique de la configuration réseau. Il permet de définir une source et une destination parmi les ressources prises en charge, puis d'analyser le chemin réseau virtuel résultant. Il peut fournir des détails étape par étape lorsque le chemin est joignable ou identifier un composant bloquant lorsque la configuration empêche la connectivité.

Il est particulièrement utile pour analyser des erreurs liées aux routes, aux Security Groups, aux NACL ou à des composants réseau pris en charge.

## 13.2. Ce que l'outil ne prouve pas

Reachability Analyzer ne remplace pas un test applicatif complet. Une analyse de configuration peut montrer un chemin réseau possible, sans prouver que :

- Le processus serveur écoute réellement sur le port.
- Le pare-feu de l'OS autorise le flux.
- Le service est correctement configuré.
- L'authentification ou l'autorisation métier fonctionne.
- Le serveur distant est sain.

L'analyse porte sur la configuration de connectivité prise en charge, et non sur la logique complète de l'application.

## 13.3. Quand utiliser Reachability Analyzer ?

Utilise-le notamment lorsque :

- Deux interfaces réseau dans un VPC ne semblent pas communiquer.
- Un flux vers un endpoint ou une passerelle est bloqué.
- Une règle vient d'être modifiée et il faut vérifier l'intention de connectivité.
- Une architecture comporte plusieurs tables de routage, Security Groups et sous-réseaux.

Vérifie les ressources source et destination disponibles dans l'interface AWS et les limites du service pour le type de chemin souhaité.

## 13.4. Procédure de diagnostic

1. Ouvrir VPC Reachability Analyzer.
2. Créer une analyse de chemin en choisissant la source et la destination prises en charge.
3. Définir le protocole et les paramètres de port si requis par le scénario.
4. Lancer l'analyse.
5. Lire le résultat et le composant bloquant s'il existe.
6. Corriger une seule cause à la fois.
7. Relancer l'analyse.
8. Compléter par un test réel (`curl`, `nc`, client de base de données ou test applicatif).
9. Documenter ce que l'outil a confirmé et ce qu'il ne pouvait pas confirmer.


# 14. Méthode structurée de dépannage réseau

## 14.1. Ne pas modifier plusieurs couches en même temps

Lorsqu'une connexion échoue, ouvrir tous les ports, remplacer des routes et désactiver des NACL au hasard peut donner l'impression de résoudre le problème, tout en détruisant la sécurité et en masquant la cause initiale.

Utilise une démarche reproductible :

1. Décrire la source, la destination, le protocole et le port.
2. Reproduire le problème.
3. Vérifier le DNS si un nom est utilisé.
4. Vérifier le chemin de routage aller et retour.
5. Vérifier les Security Groups.
6. Vérifier les NACL si elles sont restrictives.
7. Vérifier le pare-feu de l'OS et l'écoute du service.
8. Examiner Flow Logs et Reachability Analyzer si le scénario s'y prête.
9. Corriger une cause précise, puis retester.
10. Documenter le résultat et supprimer les règles temporaires.

## 14.2. Arbre de décision textuel

```text
La connexion échoue
       |
       v
Le nom DNS se résout-il correctement ?
       |
       +-- NON --> Vérifier nom, DNS, zones et caches
       |
       +-- OUI
             |
             v
La route aller correspond-elle au chemin attendu ?
             |
             +-- NON --> Corriger table/association/target
             |
             +-- OUI
                   |
                   v
La route de retour existe-t-elle si nécessaire ?
                   |
                   +-- NON --> Corriger route retour
                   |
                   +-- OUI
                         |
                         v
Security Groups et NACL autorisent-ils le flux ?
                         |
                         +-- NON --> Corriger règle minimale nécessaire
                         |
                         +-- OUI
                               |
                               v
Le service écoute-t-il sur le bon port ?
                               |
                               +-- NON --> Corriger service/OS/container
                               |
                               +-- OUI
                                     |
                                     v
Examiner logs, protocole applicatif, santé et authentification
```

## 14.3. Commandes Linux utiles

Ces commandes sont des exemples. Elles supposent que les outils correspondants soient installés et autorisés.

### Vérifier la résolution DNS

```bash
getent hosts api.exemple.internal
nslookup api.exemple.internal
```

### Tester une connexion TCP

```bash
nc -vz 10.40.11.20 8080
```

Le retour dépend de la version de `nc`. Un succès indique en général que la poignée de main TCP a été établie, mais ne prouve pas que l'application fonctionne correctement.

### Tester une requête HTTP(S)

```bash
curl -v --connect-timeout 5 https://api.exemple.internal/health
```

`curl -v` montre le détail de la connexion et du dialogue HTTP/TLS. Ne place pas de secrets dans une commande susceptible d'être conservée dans l'historique du shell.

### Examiner les sockets d'écoute

```bash
sudo ss -lntup
```

Cette commande aide à vérifier qu'un processus écoute sur le bon port et sur la bonne adresse. Un service qui écoute uniquement sur `127.0.0.1` peut être inaccessible depuis une autre machine même si les règles réseau AWS sont correctes.

### Examiner le pare-feu local

Les outils disponibles diffèrent selon la distribution, par exemple `nft`, `iptables`, `firewall-cmd` ou `ufw`. Examiner la configuration réellement utilisée par le système plutôt que supposer qu'un outil particulier est actif.

## 14.4. Matrice « symptôme → causes probables »

| Symptôme | Causes probables | Premier contrôle |
|---|---|---|
| Instance privée sans accès Internet sortant | Route vers NAT absente, NAT indisponible, route de subnet NAT vers IGW manquante, SG/NACL | Tables des deux sous-réseaux et état de NAT |
| Application inaccessible sur HTTPS | SG ALB, listener, DNS public, certificat, route publique, health check | ALB/listener/SG et cible de santé |
| ALB voit les cibles comme unhealthy | Port applicatif, endpoint de health check, SG de cible, OS, application | Port et chemin ALB → cible |
| App ne joint pas la base de données | SG-DATA, route locale, port, DNS privé, base non à l'écoute | SG et test TCP du port de base |
| Peering actif mais trafic bloqué | Routes manquantes dans un sens, SG/NACL, CIDR incorrect | Routes des deux VPC |
| Accès à S3 échoue après création d'un endpoint | Mauvaise table associée, politique endpoint, IAM, bucket policy, DNS/SDK | Routage endpoint + identité IAM |
| `curl` par IP fonctionne mais pas par nom | DNS, enregistrement, zone privée, cache | Résolution du nom depuis la source |
| Flow Logs affiche ACCEPT mais le service échoue | Service non à l'écoute, OS, TLS/HTTP, authentification, mauvaise tentative observée | `ss`, `curl -v`, logs applicatifs |
| Ressource privée accessible par IPv6 de façon inattendue | Route IPv6, adresse publique IPv6, SG IPv6 trop large | Tables et règles IPv6 |


# 15. Exploitation, gouvernance et contrôle des coûts

## 15.1. Documenter le réseau

Pour chaque VPC, maintenir un document indiquant :

- Identifiant, nom, compte et région.
- CIDR IPv4/IPv6.
- Sous-réseaux et zones de disponibilité.
- Tables de routage et associations.
- Internet Gateway, NAT Gateways et endpoints.
- Connexions vers d'autres VPC ou réseaux locaux.
- Groupes de sécurité critiques et flux métier associés.
- Configuration de Flow Logs et rétention.
- Propriétaire technique, contacts et environnement.
- Dépendances et procédures de reprise.

## 15.2. Convention de nommage

Exemple de convention :

```text
<application>-<environment>-<component>-<az>

orion-prod-subnet-public-a
orion-prod-subnet-app-a
orion-prod-rtb-app-a
orion-prod-sg-alb
orion-prod-sg-app
orion-prod-sg-data
orion-prod-vpce-s3
```

Le nom ne remplace pas les tags. Prévoir des tags cohérents, tels que `Application`, `Environment`, `Owner`, `CostCenter` et `ManagedBy`, selon les politiques de l'organisation.

## 15.3. Gestion des changements

Avant chaque changement réseau important :

1. Décrire le besoin et le flux.
2. Identifier les ressources touchées.
3. Évaluer l'impact sur la sécurité, la disponibilité, le coût et les dépendances.
4. Préparer un plan de retour arrière.
5. Planifier le changement selon les exigences de l'environnement.
6. Appliquer une modification limitée.
7. Tester le comportement attendu et les refus attendus.
8. Mettre à jour la documentation.

## 15.4. Contrôle du coût réseau

Quelques points à surveiller :

- NAT Gateways : coût de fonctionnement et traitement des données.
- Interfaces endpoints : coûts horaires et coûts de données selon le service/région.
- Transferts inter-AZ, inter-région ou vers Internet selon les conditions applicables.
- VPC Flow Logs : ingestion, stockage, requêtes et conservation.
- Ressources de test oubliées après un atelier.
- Adresses IPv4 publiques et ressources associées, selon les règles de tarification en vigueur.

Le coût le plus bas n'est pas nécessairement le meilleur choix s'il dégrade la résilience ou complique l'exploitation. L'objectif est de rendre le compromis visible et délibéré.

## 15.5. Nettoyage des environnements de laboratoire

À la fin d'un atelier :

- Supprimer les ressources de test non nécessaires.
- Vérifier qu'aucune NAT Gateway ou instance facturable n'a été laissée active par oubli.
- Examiner les endpoints et les Flow Logs créés.
- Ne pas supprimer un VPC partagé ou une ressource de production par erreur.
- Ne pas retirer une ressource si elle est utilisée par d'autres workloads.


# 16. Ateliers guidés

Les ateliers doivent être réalisés dans un compte autorisé, idéalement un environnement de formation isolé. Vérifie les coûts avant de créer des ressources facturables. Ne déploie pas un laboratoire dans un compte de production sans validation explicite.

## Atelier 1 — Examiner un VPC existant

### Objectif

Savoir reconstituer le chemin réseau à partir de la console AWS.

### Étapes

1. Ouvrir la console VPC et sélectionner la région voulue.
2. Choisir un VPC de laboratoire autorisé.
3. Relever son CIDR.
4. Lister les sous-réseaux et leurs zones de disponibilité.
5. Pour chaque sous-réseau, déterminer la table de routage réellement associée.
6. Relever les routes et leurs cibles.
7. Identifier les IGW, NAT Gateways et endpoints présents.
8. Examiner les Security Groups des ressources concernées.
9. Produire un schéma textuel ressemblant aux exemples du cours.

### Livrable

Une fiche de réseau contenant le CIDR, les sous-réseaux, les tables et les principales règles de sécurité.

### Critères de réussite

- Chaque sous-réseau est associé à la bonne table.
- Les routes sont retranscrites sans inversion destination/cible.
- Les zones de disponibilité sont identifiées.
- Les flux autorisés et refusés sont décrits séparément.

## Atelier 2 — Construire une segmentation à deux AZ

### Objectif

Concevoir un VPC avec des sous-réseaux publics, applicatifs et de données.

### Plan

Utiliser le VPC `10.40.0.0/16` et les six sous-réseaux suivants :

```text
Public A : 10.40.1.0/24
Public B : 10.40.2.0/24
App A    : 10.40.11.0/24
App B    : 10.40.12.0/24
Data A   : 10.40.21.0/24
Data B   : 10.40.22.0/24
```

### Étapes de réalisation

1. Créer le VPC avec le CIDR défini.
2. Activer ou vérifier les paramètres DNS nécessaires au scénario.
3. Créer les sous-réseaux dans deux zones différentes.
4. Créer et attacher une Internet Gateway.
5. Créer une table publique et y placer la route `0.0.0.0/0 -> IGW`.
6. Associer les deux sous-réseaux publics à cette table, si la conception et les ressources le permettent.
7. Créer les tables applicatives et y ajouter uniquement les routes de sortie réellement souhaitées.
8. Créer une table de données avec la route locale et les routes supplémentaires justifiées par le besoin.
9. Créer des Security Groups distincts pour ALB, application et base de données.
10. Vérifier la configuration à l'aide de la carte de ressources du VPC et des tables de routage.

### Livrable

Un schéma et une matrice de flux indiquant ce qui doit fonctionner et ce qui doit échouer.

### Attention

La création de ressources telles qu'un ALB, une NAT Gateway, des instances EC2 ou une base gérée peut générer des coûts. L'atelier peut être réalisé en deux phases : conception et création des seules ressources nécessaires au test.

## Atelier 3 — Ajouter une sortie contrôlée aux sous-réseaux applicatifs

### Objectif

Comparer deux options : NAT Gateway par AZ et absence de NAT avec accès privé aux services AWS nécessaires.

### Phase A : scénario NAT

1. Créer une NAT Gateway publique dans un sous-réseau public si ce coût est acceptable.
2. Vérifier que le sous-réseau public de la NAT dispose d'une route vers l'IGW.
3. Configurer la table du sous-réseau applicatif pour acheminer `0.0.0.0/0` vers la NAT retenue.
4. Tester une destination HTTPS connue et autorisée.
5. Vérifier les journaux et les coûts attendus.
6. Documenter les conséquences d'une panne de l'AZ de la NAT partagée.

### Phase B : scénario endpoint

1. Déterminer si le workload doit accéder à S3, DynamoDB ou à un autre service compatible avec un endpoint.
2. Créer l'endpoint adapté selon la documentation du service.
3. Associer les tables de routage ou sous-réseaux concernés.
4. Vérifier les politiques IAM et ressources.
5. Tester uniquement l'opération autorisée.
6. Comparer le chemin réseau et les coûts à l'option NAT.

### Livrable

Un tableau comparatif précisant les destinations accessibles, la résilience, les coûts à vérifier et les hypothèses de sortie Internet.

## Atelier 4 — Tester une politique Security Groups

### Objectif

Restreindre le serveur applicatif à une source autorisée.

### Scénario

- `SG-ALB` : entrée HTTPS depuis les clients.
- `SG-APP` : entrée TCP/8080 depuis `SG-ALB` uniquement.
- `SG-DATA` : entrée TCP/5432 depuis `SG-APP` uniquement.

### Tests attendus

| Test | Résultat attendu |
|---|---|
| Client autorisé vers ALB en HTTPS | Autorisé si les autres paramètres sont corrects |
| Client Internet vers IP d'instance App en TCP/8080 | Pas d'accès direct attendu |
| ALB vers App en TCP/8080 | Autorisé par la politique de SG, si route et service corrects |
| App vers Data en TCP/5432 | Autorisé par la politique de SG, si route et service corrects |
| Client Internet vers Data en TCP/5432 | Refusé / aucun chemin public prévu |

Le résultat réel dépend de la présence des ressources, des autres Security Groups associés, des NACL et du fonctionnement du service. Tester depuis une source appropriée et documenter la méthode.

## Atelier 5 — Activer Flow Logs et diagnostiquer un rejet

### Objectif

Collecter une trace de flux et l'utiliser pour guider le diagnostic.

### Étapes

1. Choisir une portée de Flow Logs adaptée au laboratoire.
2. Configurer la destination et la conservation des logs.
3. Émettre un flux de test autorisé et un flux de test destiné à être refusé dans un environnement autorisé.
4. Attendre la publication des enregistrements selon le mécanisme du service.
5. Filtrer par interface, source, destination, ports et période.
6. Comparer les actions ACCEPT et REJECT.
7. Associer chaque enregistrement à une tentative connue.
8. Corriger une règle minimale si un flux légitime est rejeté.
9. Rejouer le test et vérifier le résultat.
10. Nettoyer les ressources non nécessaires.

### Livrable

Un compte rendu qui contient : le flux initial, le symptôme, les journaux pertinents, la cause confirmée, la correction et le résultat du nouveau test.


# 17. Exercices de consolidation corrigés

## Exercice 1 — Lire des routes

Table de routage :

```text
10.40.0.0/16  -> local
10.70.0.0/16  -> pcx-services
0.0.0.0/0     -> nat-app-a
```

Pour chaque destination, indique la route attendue :

1. `10.40.21.15`
2. `10.70.4.30`
3. `1.1.1.1`

### Correction

1. `10.40.21.15` appartient au CIDR `10.40.0.0/16` : route `local`.
2. `10.70.4.30` appartient au CIDR `10.70.0.0/16` : route vers `pcx-services`.
3. `1.1.1.1` ne correspond pas aux deux routes privées précédentes : route par défaut `0.0.0.0/0 -> nat-app-a`.

La sélection de route ne garantit pas que la connexion aboutisse. La cible, les routes de retour et les règles de sécurité doivent encore être valides.

## Exercice 2 — Rendre un flux applicatif possible

Une instance ALB doit joindre une instance applicative sur TCP/8080. Le SG de l'application autorise seulement TCP/8080 depuis le CIDR du sous-réseau applicatif. L'ALB se trouve dans des sous-réseaux publics.

Questions :

1. Quel risque présente une autorisation basée sur le CIDR applicatif plutôt que sur le SG de l'ALB ?
2. Quelle modification est généralement préférable ?
3. Quelles autres vérifications sont nécessaires si le flux ne fonctionne toujours pas ?

### Correction

1. Autoriser tout le CIDR applicatif peut permettre à d'autres ressources de ce CIDR de tenter la même connexion, alors que le besoin concerne l'ALB.
2. Lorsque le scénario le permet, utiliser une règle entrante dans le SG de l'application sur TCP/8080 avec le SG de l'ALB comme source.
3. Vérifier que le bon SG est attaché à l'ALB et à la cible, que les routes et NACL conviennent, que l'application écoute sur le bon port et que le test cible la bonne adresse. Si un ALB est utilisé, examiner aussi le health check.

## Exercice 3 — NACL et flux de retour

Une NACL permet un flux entrant TCP/443 mais n'autorise pas la plage de ports de retour nécessaire. L'application semble recevoir la requête, mais le client n'obtient pas de réponse complète.

Pourquoi cela peut-il se produire ?

### Correction

Les NACL sont stateless. La règle entrante TCP/443 n'autorise pas automatiquement tous les paquets de retour. Il faut examiner le flux de retour, notamment les ports source/destination et la plage éphémère du client concerné, puis créer les règles minimales requises. Les Security Groups, eux, sont stateful.

## Exercice 4 — Peering actif, connexion impossible

VPC A (`10.40.0.0/16`) et VPC B (`10.70.0.0/16`) ont un peering actif. Un serveur de A doit atteindre TCP/8443 sur un serveur de B. Les routes vers le VPC distant existent seulement dans la table du VPC A.

### Correction

Ajouter/valider la route de retour dans la table associée au sous-réseau de B, vers `10.40.0.0/16` à travers le peering. Vérifier ensuite les Security Groups, les NACL et le service à l'écoute. Un peering actif ne crée pas automatiquement toutes les routes nécessaires.

## Exercice 5 — Endpoint S3 et accès refusé

Une instance privée utilise un gateway endpoint S3. La route semble correcte, mais l'appel à S3 renvoie une erreur d'autorisation.

### Correction

Vérifier dans cet ordre :

1. L'identité IAM utilisée et ses permissions.
2. La politique du bucket.
3. La politique du VPC endpoint, si elle est définie.
4. Les conditions de politique qui contraignent les sources ou les endpoints.
5. Le nom de bucket, la région et l'action demandée.

Si la requête atteint S3 et reçoit un refus d'autorisation, ajouter une route ne constitue généralement pas la correction pertinente.

## Exercice 6 — Flow Logs affiche ACCEPT

Flow Logs indique qu'un flux TCP vers `10.40.11.20:8080` est accepté, mais `curl` échoue.

### Correction

`ACCEPT` ne prouve pas que l'application répond. Vérifier si le service écoute (`ss -lntup`), s'il écoute sur l'adresse de réseau appropriée, le pare-feu local, le processus applicatif, la négociation TLS/HTTP si applicable, les logs applicatifs et le fait que le log corresponde exactement à la requête en échec.

## Exercice 7 — NAT Gateway partagée

Deux sous-réseaux applicatifs sont dans deux AZ et utilisent la même NAT Gateway placée dans AZ A. Quel est le principal compromis ?

### Correction

Cette conception peut réduire le nombre de NAT Gateways, mais introduit une dépendance à la NAT de AZ A et un chemin inter-AZ pour le trafic qui vient d'autres AZ. Si cette AZ devient indisponible, ces sous-réseaux peuvent perdre leur sortie Internet. Une NAT Gateway par AZ améliore généralement l'isolation de panne, au prix de ressources et de frais supplémentaires.

## Exercice 8 — VPC Peering transitif

VPC A est appairé avec VPC B, et VPC B avec VPC C. Pourquoi A ne peut-il pas automatiquement rejoindre C au travers de B ?

### Correction

Le VPC Peering classique n'est pas transitif. Il faut une connexion directement adaptée entre A et C ou une architecture de transit prise en charge, par exemple AWS Transit Gateway selon le besoin.


# 18. Challenge final autonome — Architecture réseau Orion

> Cette section est l'évaluation finale du cours. Elle est incluse dans le même fichier que les leçons et les ateliers. Il est recommandé de résoudre les questions avant de lire la correction de la section 19.

## 18.1. Contexte

L'entreprise Orion déploie une application sur AWS. Elle possède le VPC suivant :

```text
VPC PROD : 10.40.0.0/16
```

Sous-réseaux :

```text
Public A : 10.40.1.0/24  (AZ A)
Public B : 10.40.2.0/24  (AZ B)
App A    : 10.40.11.0/24 (AZ A)
App B    : 10.40.12.0/24 (AZ B)
Data A   : 10.40.21.0/24 (AZ A)
Data B   : 10.40.22.0/24 (AZ B)
```

Le service comporte :

- Un ALB public devant les serveurs applicatifs.
- Des instances applicatives privées qui écoutent sur TCP/8080.
- Une base PostgreSQL accessible sur TCP/5432 uniquement par l'application.
- Un besoin d'accès à un bucket S3 autorisé pour les sauvegardes applicatives.
- Une exigence de journalisation des flux pour aider les équipes d'exploitation.
- Un VPC de services partagés `10.70.0.0/16` contenant une API privée sur TCP/8443.

Le VPC de services partagés et le VPC de production doivent communiquer à travers un VPC Peering. Les sous-réseaux de base de données ne doivent pas avoir de sortie Internet générale. L'équipe veut réduire les accès inutiles et éviter d'ouvrir les ports à tout le monde pour résoudre les incidents.

## 18.2. État initial volontairement imparfait

Voici les problèmes signalés :

1. Le SG des instances applicatives autorise TCP/8080 depuis `0.0.0.0/0`.
2. Le SG de la base PostgreSQL autorise TCP/5432 depuis tout le CIDR `10.40.0.0/16`.
3. Le sous-réseau App A route `0.0.0.0/0` vers `NAT-A`, mais la table du sous-réseau public de NAT-A ne possède pas de route par défaut vers l'IGW.
4. Le sous-réseau App B utilise la NAT Gateway placée dans AZ A.
5. Le VPC Peering est actif, mais la table du sous-réseau de destination dans le VPC de services ne contient pas de route de retour vers `10.40.0.0/16`.
6. L'accès à S3 passe par la NAT Gateway, même lorsqu'un accès par gateway endpoint pourrait convenir.
7. Les logs montrent une tentative de connexion à `10.40.11.20:8080`, mais l'équipe ne sait pas distinguer un rejet réseau d'une application qui n'écoute pas.
8. Une équipe propose d'autoriser tout TCP en entrée sur les Security Groups pour aller plus vite.

## 18.3. Travail demandé

### Mission A — Concevoir la segmentation

1. Explique le rôle de chaque famille de sous-réseaux.
2. Précise les routes attendues pour les sous-réseaux publics, applicatifs et de données.
3. Explique pourquoi la seule présence d'une route vers l'IGW ne rend pas automatiquement une instance privée accessible depuis Internet.

### Mission B — Corriger les Security Groups

Propose une matrice de règles pour :

- `SG-ALB`
- `SG-APP`
- `SG-DATA`
- Le SG ou les règles appropriées de l'API du VPC de services

Le résultat doit respecter le moindre privilège. Utilise une référence de SG lorsque cela est supporté et pertinent. N'ouvre pas tous les ports.

### Mission C — Corriger la sortie réseau

1. Explique pourquoi la NAT-A ne permet pas correctement la sortie tant que sa table n'a pas de route vers l'IGW.
2. Compare une NAT Gateway par AZ et une NAT Gateway partagée.
3. Indique ce que tu vérifierais avant de décider si les sous-réseaux applicatifs ont réellement besoin d'une sortie Internet générale.

### Mission D — Accès à S3

1. Décris comment introduire un S3 gateway endpoint.
2. Cite au moins trois contrôles non liés à la route qui peuvent encore empêcher l'accès.
3. Explique comment tu confirmerais que le trafic utilise la conception attendue.

### Mission E — VPC Peering

1. Indique les routes qui doivent exister dans les deux VPC.
2. Liste les vérifications de sécurité nécessaires pour TCP/8443.
3. Explique pourquoi le peering ne doit pas être utilisé comme route de transit vers d'autres VPC non appairés directement.

### Mission F — Diagnostic

Propose un plan de diagnostic, dans l'ordre, pour le flux ALB → application sur TCP/8080 lorsque l'accès échoue. Mentionne les outils et ce que chacun peut confirmer.

### Mission G — Exploitabilité

Définis cinq éléments de documentation ou de gouvernance à ajouter pour rendre l'architecture plus fiable.

## 18.4. Barème sur 100 points

| Domaine évalué | Points |
|---|---:|
| Segmentation et tables de routage | 20 |
| Sécurité par Security Groups et moindre privilège | 20 |
| NAT Gateway, résilience et coût | 15 |
| Accès S3 par endpoint et contrôles d'autorisation | 15 |
| VPC Peering bidirectionnel | 10 |
| Diagnostic par étapes | 15 |
| Documentation et exploitation | 5 |
| **Total** | **100** |

Repères d'évaluation :

- **90–100 :** architecture cohérente, règles précises, raisonnement de dépannage structuré.
- **75–89 :** bonnes bases, quelques oublis limités.
- **60–74 :** compréhension partielle, erreurs de chemin ou de sécurité à corriger.
- **Moins de 60 :** revoir les sections sur le routage, les Security Groups, les endpoints et le dépannage avant une nouvelle tentative.


# 19. Correction détaillée du challenge final

Cette correction est volontairement placée après l'énoncé. Le challenge et sa correction restent dans le même fichier Markdown.

## 19.1. Mission A — Segmentation et routes

### Rôles

- **Public A/Public B :** héberger les composants qui doivent être accessibles par une entrée publique, typiquement les nœuds d'un ALB public, et éventuellement la NAT Gateway publique selon la conception.
- **App A/App B :** héberger les instances applicatives privées. Elles ne doivent pas être accessibles directement depuis Internet.
- **Data A/Data B :** héberger les ressources de données. Elles reçoivent seulement les flux explicitement autorisés depuis la couche applicative.

### Routes attendues

Table publique :

```text
10.40.0.0/16 -> local
0.0.0.0/0    -> IGW
```

Table applicative si sortie via NAT :

```text
10.40.0.0/16 -> local
0.0.0.0/0    -> NAT de l'AZ prévue
```

Table des données si aucune sortie externe n'est requise :

```text
10.40.0.0/16 -> local
```

Chaque route doit être associée à la bonne table et chaque sous-réseau doit effectivement utiliser cette table. Si certaines opérations nécessitent un endpoint ou une connectivité privée supplémentaire, ajouter uniquement les routes et ressources exigées par cette fonction.

### Route IGW et accès direct

Une route vers l'IGW est une partie du chemin, mais l'accès IPv4 public exige également une configuration d'adressage public adaptée, une route cohérente et des autorisations de sécurité. Dans cette conception, les serveurs d'application n'ont pas besoin d'adresse IPv4 publique et leur SG accepte uniquement le SG de l'ALB sur TCP/8080.

## 19.2. Mission B — Politique Security Groups

### SG-ALB

| Direction | Port | Source/destination | But |
|---|---|---|---|
| Entrant | TCP/443 | `0.0.0.0/0` si l'application est publique en IPv4 | Accepter HTTPS des clients |
| Sortant | TCP/8080 | `SG-APP`/cibles autorisées selon la conception | Appeler les serveurs applicatifs |

Ajouter une règle IPv6 entrante `::/0` uniquement si l'application est volontairement publiée en IPv6 et si le besoin est validé.

### SG-APP

| Direction | Port | Source/destination | But |
|---|---|---|---|
| Entrant | TCP/8080 | `SG-ALB` | N'accepter que les connexions de l'ALB |
| Sortant | TCP/5432 | `SG-DATA` ou destination précise | Connexion à PostgreSQL |
| Sortant | TCP/8443 | SG ou CIDR précis de l'API services, si nécessaire | Appel de l'API partagée |
| Sortant | HTTPS vers les destinations requises | Selon la politique de sortie | S3/services AWS, idéalement chemin endpoint quand adapté |

Les règles de sortie doivent être ajustées au besoin réel et aux capacités des endpoints utilisés. Les flux DNS, la supervision, les mises à jour ou les agents de gestion doivent être pris en compte explicitement s'ils sont nécessaires.

### SG-DATA

| Direction | Port | Source | But |
|---|---|---|---|
| Entrant | TCP/5432 | `SG-APP` | Autoriser PostgreSQL uniquement depuis l'application |
| Sortant | Minimum nécessaire | Destinations approuvées | Limiter l'accès sortant selon les besoins opérationnels |

L'autorisation depuis tout `10.40.0.0/16` est plus large que nécessaire. Elle permettrait à d'autres ressources de cette plage d'essayer d'atteindre le port PostgreSQL. La source devrait être le SG de la couche applicative lorsque le scénario le permet.

### SG de l'API dans VPC de services

Règle entrante illustrative :

```text
TCP/8443
Source : SG-APP ou CIDR source précis autorisé
```

La référence de SG à travers le peering doit être compatible avec la configuration précise et les contraintes d'AWS. Sinon, une règle utilisant le CIDR source le plus étroit possible peut être employée, en documentant la raison.

### Pourquoi ne pas autoriser tout TCP ?

Une règle entrante `TCP all` depuis `0.0.0.0/0` expose de nombreux ports sans justification. Elle peut transformer une erreur de configuration ou un service oublié en surface d'attaque exploitable. Le bon principe consiste à autoriser le protocole, le port, la source et la destination nécessaires, puis à tester le résultat.

## 19.3. Mission C — NAT et choix de résilience

### Cause de la panne NAT-A

Une route dans le sous-réseau applicatif vers NAT-A n'est qu'une partie du chemin. La NAT Gateway publique doit elle-même avoir une route de sortie vers l'IGW via la table associée à son sous-réseau. Sans cette route, le trafic ne peut pas suivre le chemin de sortie Internet attendu.

### Option recommandée selon l'objectif

- Si la disponibilité inter-AZ est prioritaire et que la sortie Internet est réellement nécessaire, une NAT Gateway par AZ avec les sous-réseaux applicatifs de chaque AZ routés vers la NAT locale est souvent le choix de résilience le plus clair.
- Si le budget est très contraint et que le risque d'une panne de sortie lors de l'indisponibilité de l'AZ de la NAT est accepté, une NAT partagée peut être étudiée, après validation du compromis et du trafic inter-AZ.

Aucun choix n'est justifié sans les exigences de disponibilité et le coût estimé.

### Vérifications avant de retenir la NAT

- Quelles destinations sont appelées par l'application ?
- Les destinations sont-elles des services AWS disposant d'endpoints adaptés ?
- Les mises à jour système exigent-elles un accès Internet général ou peuvent-elles être organisées autrement ?
- Peut-on limiter les sorties aux endpoints ou destinations autorisées ?
- Quel est le volume et le profil du trafic ?
- Quelle perte de service est acceptable en cas de panne d'une AZ ?
- Quels coûts horaires, coûts de traitement et transferts de données sont attendus ?

## 19.4. Mission D — S3 endpoint

Étapes :

1. Créer un gateway endpoint S3 dans la région correspondant au workload.
2. Associer les tables de routage des sous-réseaux qui doivent utiliser cet endpoint.
3. Vérifier que la table contient l'entrée liée au préfixe du service selon la configuration AWS.
4. Vérifier les permissions IAM de l'identité utilisée par l'application.
5. Vérifier la politique du bucket et la politique de l'endpoint, si cette dernière est configurée.
6. Tester une opération précise sur un bucket autorisé.
7. Examiner les logs disponibles et le chemin réseau pour confirmer la conception.

Autres contrôles qui peuvent bloquer l'accès :

- Permissions IAM insuffisantes.
- Bucket policy qui refuse l'action ou la source.
- Endpoint policy trop restrictive.
- Mauvais nom de bucket ou région.
- Appel API qui demande une action différente de celle autorisée.

Le trafic peut être validé en examinant la table de routage associée, la présence du gateway endpoint, les politiques et le résultat contrôlé d'une requête. Il ne faut pas conclure uniquement à partir d'un test HTTP générique.

## 19.5. Mission E — VPC Peering

Routes côté production :

```text
10.40.0.0/16 -> local
10.70.0.0/16 -> pcx-prod-services
```

Routes côté services :

```text
10.70.0.0/16 -> local
10.40.0.0/16 -> pcx-prod-services
```

Ensuite, contrôler :

- La connexion de peering est active.
- Les CIDR ne se chevauchent pas.
- Le sous-réseau de chaque ressource utilise une table qui contient la bonne route.
- SG-APP autorise la sortie TCP/8443 vers la destination approuvée.
- Le SG de l'API autorise l'entrée TCP/8443 depuis la source appropriée.
- Les NACL ne bloquent pas le flux ni son retour.
- Le service écoute bien sur TCP/8443.
- La résolution DNS fonctionne si un nom est utilisé.

Le peering ne fournit pas de transit automatique entre des VPC non appairés directement. Si la topologie doit devenir un réseau centralisé de nombreux VPC, étudier un service de transit comme AWS Transit Gateway plutôt que multiplier des hypothèses de routage transitif.

## 19.6. Mission F — Plan de diagnostic ALB vers application

### Étape 1 : confirmer le symptôme

Préciser l'ALB, la cible, le port `8080`, le type de health check, l'heure du test et le résultat exact.

### Étape 2 : vérifier les cibles et le service

- Confirmer que l'instance ou la cible est enregistrée dans le groupe cible.
- Vérifier si le health check est sain.
- Vérifier que le service écoute réellement sur TCP/8080.
- Vérifier si le service écoute sur l'adresse réseau appropriée et non seulement sur loopback.

### Étape 3 : vérifier le chemin réseau

- Vérifier que le SG des cibles accepte TCP/8080 depuis le SG de l'ALB.
- Vérifier les règles de sortie du SG de l'ALB.
- Vérifier les NACL des sous-réseaux si elles sont restrictives.
- Vérifier que le sous-réseau et la table de routage correspondent à la conception.

### Étape 4 : Reachability Analyzer

Utiliser Reachability Analyzer si la paire de ressources et le chemin sont pris en charge. L'outil peut signaler une route ou une règle de filtrage bloquante dans la configuration analysée. Il ne prouve pas que le processus de l'application est vivant.

### Étape 5 : VPC Flow Logs

Chercher les flux correspondant aux adresses, aux ports, au protocole et à l'heure du test. Un `REJECT` peut orienter vers le filtrage réseau. Un `ACCEPT` ne prouve pas que le service réponde : poursuivre vers l'OS et l'application.

### Étape 6 : tester le service

Depuis un point de test autorisé, utiliser un test TCP approprié et examiner les journaux applicatifs. Pour HTTPS, analyser la résolution DNS, la connexion TCP, le handshake TLS, le code HTTP et la réponse de santé.

### Étape 7 : corriger et retester

Modifier une seule cause confirmée à la fois, puis rejouer le même test. Ne pas laisser de règle ouverte temporairement sans suivi ni suppression.

## 19.7. Mission G — Exploitabilité

Cinq éléments parmi les suivants sont attendus :

1. Diagramme réseau et plan d'adressage versionnés.
2. Matrice de flux validée par les propriétaires applicatifs.
3. Convention de nommage et tags uniformes.
4. Flow Logs activés avec destination, rétention et contrôle d'accès documentés.
5. Procédure de dépannage avec tests et résultats attendus.
6. Plan de changement et procédure de retour arrière.
7. Estimation de coût NAT/endpoints/transferts.
8. Suivi de santé des cibles ALB et alertes pertinentes.
9. Revue périodique des règles de Security Groups.
10. Procédure de nettoyage des environnements de test.


# 20. Évaluation, checklist et glossaire

## 20.1. Checklist avant mise en service

### Adressage et topologie

- [ ] Le CIDR VPC est documenté.
- [ ] Les plages des sous-réseaux sont contenues dans le VPC et ne se chevauchent pas.
- [ ] Les sous-réseaux sont placés dans les AZ voulues.
- [ ] Le plan laisse une marge de croissance.
- [ ] Les chevauchements avec les réseaux connectés ont été examinés.

### Routage

- [ ] Chaque sous-réseau utilise la table prévue.
- [ ] La route locale est comprise et vérifiée.
- [ ] Les routes par défaut sont présentes uniquement lorsque nécessaires.
- [ ] La cible de chaque route est disponible.
- [ ] Les routes de retour sont prévues pour les communications inter-réseaux.
- [ ] Les routes IPv4 et IPv6 ont été considérées séparément.

### Sécurité

- [ ] Les Security Groups suivent le principe du moindre privilège.
- [ ] Les ports ne sont pas ouverts à tout Internet sans besoin explicite.
- [ ] La couche applicative accepte les flux attendus de l'ALB uniquement.
- [ ] La base de données accepte uniquement la source applicative attendue.
- [ ] Les règles de sortie ont été examinées.
- [ ] Les NACL, si utilisées, tiennent compte du caractère stateless et des flux de retour.

### Connectivité et endpoints

- [ ] La NAT Gateway possède le chemin réseau attendu, si utilisée.
- [ ] La dépendance à une AZ est connue.
- [ ] Les VPC endpoints sont évalués pour les services AWS nécessaires.
- [ ] Les politiques IAM, endpoint et ressources sont cohérentes.
- [ ] Le VPC Peering possède les routes requises dans les deux VPC.
- [ ] Les hypothèses DNS sont vérifiées.

### Exploitation

- [ ] Les flux critiques sont documentés.
- [ ] Flow Logs est configuré si nécessaire.
- [ ] Les tests de connectivité sont reproductibles.
- [ ] Les journaux applicatifs et les health checks sont consultables.
- [ ] Les coûts des ressources réseau sont estimés.
- [ ] Les ressources de laboratoire non nécessaires ont été supprimées.

## 20.2. Glossaire

| Terme | Signification |
|---|---|
| VPC | Réseau virtuel isolé logiquement dans AWS |
| CIDR | Notation qui représente une plage d'adresses réseau et la longueur de préfixe |
| AZ | Availability Zone, zone de disponibilité d'une région AWS |
| Sous-réseau | Plage d'adresses au sein d'un VPC, rattachée à une seule AZ |
| Route table | Ensemble de routes indiquant la cible du trafic selon sa destination |
| IGW | Internet Gateway, composant permettant le chemin Internet du VPC lorsque la configuration le prévoit |
| NAT Gateway | Service de traduction réseau permettant la sortie initiée depuis certains réseaux privés |
| Security Group | Pare-feu stateful associé aux interfaces/ressources prises en charge |
| NACL | Network Access Control List, filtre stateless au niveau du sous-réseau |
| Endpoint | Point d'accès réseau vers un service AWS ou un service exposé via PrivateLink |
| Gateway endpoint | Endpoint pour S3 ou DynamoDB s'appuyant sur des routes de tables de routage |
| Interface endpoint | Endpoint utilisant des interfaces réseau privées et AWS PrivateLink |
| Peering | Connexion de routage entre deux VPC non chevauchants, sans transitivité automatique |
| Flow Logs | Métadonnées de trafic IP collectées pour l'observation et le diagnostic |
| ENI | Elastic Network Interface, interface réseau virtuelle d'une ressource AWS |
| Reachability Analyzer | Outil d'analyse statique de la connectivité réseau AWS |
| Stateful | Le système suit le contexte de la connexion et traite les réponses du flux autorisé en conséquence |
| Stateless | Les directions aller et retour doivent être évaluées et autorisées indépendamment |
| Moindre privilège | N'autoriser que les accès nécessaires au fonctionnement |
| Résilience | Capacité d'une architecture à maintenir ou rétablir son service face à une panne |

## 20.3. Questions de révision

1. Pourquoi un VPC public/privé ne peut-il pas être défini uniquement par son nom ?
2. Quelles conditions doivent être vérifiées pour qu'une instance privée sorte via NAT Gateway ?
3. Pourquoi la route de retour est-elle importante pour le VPC Peering ?
4. Quelle différence fondamentale existe entre Security Groups et NACL ?
5. Pourquoi Flow Logs `ACCEPT` ne prouve-t-il pas que l'application fonctionne ?
6. Quels contrôles subsistent lorsqu'un gateway endpoint S3 est configuré ?
7. Pourquoi un peering entre A-B et B-C n'autorise-t-il pas automatiquement A-C ?
8. Comment diagnostiquer une différence entre accès par IP et accès par nom DNS ?
9. Pourquoi faut-il examiner les routes IPv4 et IPv6 séparément ?
10. Quels compromis faut-il présenter lorsqu'on choisit une NAT Gateway partagée ?

### Réponses synthétiques

1. Le caractère public dépend des routes et du chemin réseau ; l'exposition réelle dépend aussi de l'adressage et des règles de sécurité.
2. Route privée vers NAT, NAT publique avec EIP, route de sa table vers IGW, état de la NAT, règles de sécurité et destination disponible.
3. Le paquet de réponse doit trouver le chemin correspondant ; le peering ne crée pas automatiquement toutes les routes.
4. Le SG est stateful et associé à la ressource/interface ; la NACL est stateless et s'applique au sous-réseau avec des règles numérotées autorisant ou refusant le trafic.
5. Les contrôles réseau peuvent laisser passer les paquets alors que le service est arrêté, mal configuré ou refuse la requête au niveau applicatif.
6. IAM, politique endpoint éventuelle, politique bucket, bonnes routes, bon nom/région et service réellement autorisé.
7. Le VPC Peering classique n'est pas transitif.
8. Tester la résolution depuis la source, contrôler la zone et les enregistrements, puis comparer l'adresse résolue avec le chemin attendu.
9. Ce sont deux familles d'adresses et de routes distinctes, avec des règles et des cibles potentiellement différentes.
10. Le coût peut être réduit, mais la NAT partagée crée une dépendance à son AZ et peut augmenter le trafic inter-AZ.


# 21. Documentation officielle et ressources de référence

Les consoles et options AWS peuvent évoluer. Utilise la documentation officielle à jour pour vérifier les quotas, les prix, les noms des menus et les limitations propres à la région ou au service avant une mise en production.

## Documentation Amazon VPC

- Présentation d'Amazon VPC : https://docs.aws.amazon.com/vpc/latest/userguide/
- Fonctionnement d'un VPC : https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html
- Bases des VPC et sous-réseaux : https://docs.aws.amazon.com/vpc/latest/userguide/vpc-subnet-basics.html
- Tables de routage : https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html
- Sécurité du trafic dans un VPC : https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html

## NAT et endpoints

- NAT devices et NAT Gateway : https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat.html
- Principes des NAT Gateways : https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-basics.html
- Gateway endpoints : https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html

## Sécurité réseau

- Règles des Security Groups : https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- Infrastructure et sécurité réseau VPC : https://docs.aws.amazon.com/vpc/latest/userguide/infrastructure-security.html

## VPC Peering et connectivité

- Principes du VPC Peering : https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html
- Options de connectivité AWS : https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/vpc-peering.html

## Observabilité et diagnostic

- VPC Flow Logs : https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
- Limitations de Flow Logs : https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
- Reachability Analyzer : https://docs.aws.amazon.com/vpc/latest/userguide/reachability-analyzer.html
- Carte des ressources VPC : https://docs.aws.amazon.com/vpc/latest/userguide/view-vpc-resource-map.html


# Conclusion

Le niveau intermédiaire consiste à passer de la connaissance des composants à une capacité de conception, de validation et de dépannage.

Une architecture AWS fiable ne repose pas sur une route unique ou un Security Group permissif. Elle repose sur un plan d'adressage cohérent, des tables de routage adaptées, une séparation réfléchie des couches, des règles de sécurité minimales, un choix explicite des mécanismes de sortie, une connectivité inter-VPC maîtrisée et une démarche d'observation reproductible.

Le challenge final doit démontrer cette logique : **décrire le flux, vérifier le chemin, valider les autorisations, observer le résultat, corriger une cause précise et retester**.

Le document est volontairement autonome : le cours, les ateliers, les exercices, le challenge et sa correction sont inclus dans ce seul fichier `aws-vpc-intermediaire.md`.
