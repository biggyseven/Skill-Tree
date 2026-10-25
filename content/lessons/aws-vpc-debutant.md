# AWS VPC — Cours complet de niveau débutant

**Fichier :** `aws-vpc-debutant.md`  
**Domaine :** Réseaux, cloud computing et sécurité  
**Plateforme :** Amazon Web Services (AWS)  
**Niveau :** Débutant  
**Durée indicative :** 8 à 12 heures, exercices compris  
**Prérequis :** notions élémentaires d'IPv4, de masque réseau et de TCP/IP  
**Méthode :** cours progressif, schémas textuels, exemples, travaux guidés, exercices corrigés et challenge final  
**Mise à jour pédagogique :** octobre 2026


## Objectifs pédagogiques

À la fin de ce cours, tu devras être capable de :

- expliquer le rôle d'un VPC et sa relation avec les régions et les zones de disponibilité AWS ;
- lire et dimensionner des plages IPv4 en notation CIDR ;
- concevoir des sous-réseaux sans chevauchement ;
- distinguer sous-réseau public, privé et isolé ;
- expliquer le rôle d'une table de routage, d'une Internet Gateway et d'une NAT Gateway ;
- comprendre la différence entre Security Group et Network ACL ;
- construire une architecture simple avec un serveur Web public et un serveur applicatif privé ;
- tester les flux réseau et diagnostiquer les erreurs les plus courantes ;
- appliquer des règles de sécurité minimales et éviter les dépenses inutiles pendant un laboratoire.

## Comment suivre ce cours

Lis les chapitres dans l'ordre. Les exercices sont placés après les notions auxquelles ils se rapportent. Une proposition de correction est fournie à la fin des exercices. Le challenge final, tout à la fin du fichier, doit idéalement être réalisé sans regarder sa correction.

> **Attention aux coûts :** certaines ressources AWS, notamment les NAT Gateways, les adresses IPv4 publiques et les instances EC2, peuvent générer des frais. Les tarifs dépendent de la région et évoluent. Vérifie toujours la page tarifaire AWS avant de créer des ressources. Supprime les ressources de laboratoire quand tu as terminé.


# MODULE 1 — Comprendre les réseaux dans AWS

## 1.1. Pourquoi les réseaux sont-ils indispensables ?

Dans un système informatique, les serveurs doivent échanger des données. Ils utilisent des adresses IP, des routes et des règles de filtrage. Une machine virtuelle peut être démarrée et fonctionner correctement tout en restant inaccessible à cause d'une route manquante, d'une adresse publique absente ou d'une règle de sécurité restrictive.

Dans une infrastructure traditionnelle, l'administrateur configure des routeurs, des commutateurs, des pare-feu et des VLAN physiques. Dans le cloud, il configure principalement des ressources réseau virtuelles au moyen de la console AWS, d'une API, d'une interface en ligne de commande ou d'outils d'infrastructure as code.

```text
INFRASTRUCTURE TRADITIONNELLE

Internet
   |
[Routeur]
   |
[Pare-feu]
   |
[Commutateur]
   |------------------|
[Serveur Web]     [Serveur Applicatif]

INFRASTRUCTURE AWS

Internet
   |
[Internet Gateway]
   |
+----------------------- VPC -----------------------+
|                                                   |
|  [Sous-réseau Web]       [Sous-réseau applicatif] |
|          |                         |              |
|       [EC2 Web]                 [EC2 App]         |
+---------------------------------------------------+
```

La différence principale est que, dans AWS, l'architecture est définie logiquement. AWS exploite l'infrastructure physique sous-jacente, tandis que l'administrateur reste responsable de la conception du réseau, du routage, des autorisations et de la sécurité de ses ressources.

**Principe fondamental : une instance en état `running` n'est pas forcément accessible depuis le réseau.**

## 1.2. Qu'est-ce qu'un VPC ?

VPC signifie **Virtual Private Cloud**. C'est un réseau virtuel isolé logiquement dans AWS, dans lequel tu peux déployer des ressources telles que des instances EC2.

Lors de sa création, on lui associe une plage d'adresses IP. Dans ce cours, nous utiliserons principalement IPv4.

Exemple :

```text
Nom du VPC : vpc-entreprise-lab
CIDR IPv4   : 10.20.0.0/16

Le VPC contient :
  - des sous-réseaux ;
  - des tables de routage ;
  - des groupes de sécurité ;
  - des Network ACL ;
  - éventuellement une Internet Gateway ;
  - éventuellement une ou plusieurs NAT Gateways ;
  - éventuellement des endpoints, VPN ou autres connexions.
```

Un VPC appartient à une région AWS. Il peut s'étendre sur plusieurs zones de disponibilité de cette région. Les sous-réseaux, eux, sont associés individuellement à une seule zone de disponibilité.

## 1.3. La région et les zones de disponibilité

Une **région AWS** est une zone géographique dans laquelle AWS exploite son infrastructure. Une région comprend plusieurs zones de disponibilité.

Une **zone de disponibilité** (Availability Zone, ou AZ) est un emplacement d'infrastructure distinct au sein d'une région. Répartir les ressources sur plusieurs zones permet de concevoir des architectures plus résilientes, à condition de prévoir aussi les mécanismes applicatifs, le stockage, la répartition de charge et la bascule.

```text
RÉGION AWS
|
+-- Zone de disponibilité A
|   +-- subnet-web-a
|   +-- subnet-app-a
|
+-- Zone de disponibilité B
    +-- subnet-web-b
    +-- subnet-app-b
```

Créer deux sous-réseaux dans des zones différentes ne garantit pas automatiquement la haute disponibilité. Il faut également lancer des ressources dans chaque zone et prévoir ce qui se passe si une instance ou une zone devient indisponible.

## 1.4. Pourquoi séparer Web, application et base de données ?

Considérons une application classique à trois niveaux :

- **Web** : reçoit les demandes HTTP/HTTPS des utilisateurs ;
- **Application** : exécute la logique métier ;
- **Base de données** : conserve les données.

```text
Utilisateurs Internet
        |
        | HTTPS 443
        v
+------------------------+
| Sous-réseau Web public |
|     [Serveur Web]      |
+------------------------+
        |
        | TCP 8080, autorisé explicitement
        v
+---------------------------+
| Sous-réseau App privé     |
|     [Serveur App]         |
+---------------------------+
        |
        | TCP 3306, si MySQL est utilisé
        v
+---------------------------+
| Sous-réseau DB privé      |
|     [Base de données]     |
+---------------------------+
```

La segmentation réduit l'exposition des ressources. Un utilisateur Internet doit pouvoir joindre le service Web, mais il ne doit pas accéder directement au serveur applicatif ni à la base de données.

Les noms « public », « privé » et « base de données » décrivent le rôle prévu du sous-réseau ; ce ne sont pas des types spéciaux créés automatiquement par AWS.

## 1.5. VPC et réseau local d'une entreprise

Une entreprise peut posséder le réseau local `192.168.1.0/24` et créer un VPC AWS `10.20.0.0/16`. Ces plages sont distinctes, ce qui facilite une connexion future entre elles.

À l'inverse, si le réseau local et le VPC utilisent des plages qui se chevauchent, le routage entre les deux peut devenir complexe et nécessiter une renumérotation.

**Bonne pratique :** planifier les plages IP avant de créer plusieurs VPC, des connexions VPN ou une interconnexion avec le réseau local.

### À retenir — Module 1

- Le VPC est le réseau virtuel global.
- Une région contient plusieurs zones de disponibilité.
- Un sous-réseau est placé dans une seule zone de disponibilité.
- La segmentation distingue les rôles et aide à contrôler les communications.
- La connectivité dépend du routage, des adresses IP et des règles de sécurité, pas seulement de l'état de l'instance.

### Questions de compréhension

1. Que signifie VPC ?
2. Quelle est la différence entre une région et une zone de disponibilité ?
3. Pourquoi ne faut-il pas exposer directement la base de données à Internet ?
4. Pourquoi est-il préférable d'éviter les chevauchements de plages IP entre le réseau local et le VPC ?


# MODULE 2 — Adressage IPv4 et notation CIDR

## 2.1. Rappel sur IPv4

Une adresse IPv4 est composée de 32 bits, généralement représentés par quatre nombres décimaux séparés par des points.

Exemple : `10.20.1.25`.

Chaque nombre représente un octet de 8 bits et se situe entre 0 et 255. Une adresse IP est interprétée avec un préfixe réseau : la même adresse peut appartenir à des réseaux différents selon le masque utilisé.

## 2.2. Comprendre la notation CIDR

CIDR signifie *Classless Inter-Domain Routing*. Dans une notation comme `10.20.1.0/24`, le nombre après la barre indique combien de bits constituent le préfixe réseau.

- `/16` : 16 bits réseau, 16 bits pour le reste de l'adresse ;
- `/24` : 24 bits réseau, 8 bits pour le reste ;
- `/26` : 26 bits réseau, 6 bits pour le reste.

Le nombre théorique d'adresses IPv4 est :

`Nombre d'adresses = 2^(32 - préfixe)`

Exemples :

- `/16` : `2^16 = 65 536` adresses ;
- `/24` : `2^8 = 256` adresses ;
- `/26` : `2^6 = 64` adresses.

Un sous-réseau IPv4 AWS réserve cinq adresses par plage : les quatre premières et la dernière. Il faut donc soustraire cinq au nombre théorique pour estimer les adresses utilisables pour des ressources ordinaires.

## 2.3. Tableau de référence CIDR

| Préfixe | Masque IPv4 | Adresses totales | Adresses utilisables dans un sous-réseau AWS IPv4 ordinaire |
|---|---|---:|---:|
| `/16` | `255.255.0.0` | 65 536 | 65 531 |
| `/20` | `255.255.240.0` | 4 096 | 4 091 |
| `/24` | `255.255.255.0` | 256 | 251 |
| `/25` | `255.255.255.128` | 128 | 123 |
| `/26` | `255.255.255.192` | 64 | 59 |
| `/27` | `255.255.255.224` | 32 | 27 |
| `/28` | `255.255.255.240` | 16 | 11 |

Le tableau est un aide-mémoire. Pour un besoin réel, vérifie les contraintes AWS applicables au service et au type de plage utilisé.

## 2.4. Exemple détaillé : le réseau `10.20.1.0/24`

```text
CIDR               : 10.20.1.0/24
Masque             : 255.255.255.0
Adresse de début   : 10.20.1.0
Adresse de fin     : 10.20.1.255
Nombre total       : 256
Réservations AWS   : 5
Nombre utilisable  : 251
```

Les adresses IPv4 réservées par AWS pour un sous-réseau ordinaire de ce type sont :

- `10.20.1.0` : adresse de base du sous-réseau ;
- `10.20.1.1` : réservée au routeur VPC ;
- `10.20.1.2` : réservée au DNS AWS ;
- `10.20.1.3` : réservée pour un usage futur ;
- `10.20.1.255` : adresse de fin réservée, correspondant à l'adresse de diffusion dans cette plage.

## 2.5. Le VPC et ses sous-réseaux

Le VPC possède une plage globale, et les sous-réseaux utilisent des plages plus petites qui doivent rester à l'intérieur de cette plage et ne pas se chevaucher.

```text
VPC : 10.20.0.0/16
|
+-- subnet-public-a : 10.20.1.0/24
+-- subnet-public-b : 10.20.2.0/24
+-- subnet-app-a    : 10.20.11.0/24
+-- subnet-app-b    : 10.20.12.0/24
+-- subnet-db-a     : 10.20.21.0/24
+-- subnet-db-b     : 10.20.22.0/24
```

Les blocs ci-dessus sont distincts et contenus dans `10.20.0.0/16`.

### Exemple incorrect

```text
Sous-réseau A : 10.20.1.0/24
Sous-réseau B : 10.20.1.128/25
```

Le bloc B est inclus dans le bloc A : les plages se chevauchent. Elles ne peuvent pas être utilisées comme deux sous-réseaux IPv4 distincts du même VPC.

### Exemple correct

```text
Sous-réseau A : 10.20.1.0/24
Sous-réseau B : 10.20.2.0/24
```

Les plages sont distinctes.

## 2.6. Plan d'adressage conseillé pour le laboratoire

Nous utiliserons le plan suivant pendant le cours :

| Nom logique | CIDR | Rôle | Zone de disponibilité |
|---|---|---|---|
| `subnet-web-a` | `10.20.1.0/24` | Serveur Web public | AZ A |
| `subnet-web-b` | `10.20.2.0/24` | Réserve Web / deuxième Web | AZ B |
| `subnet-app-a` | `10.20.11.0/24` | Serveur applicatif privé | AZ A |
| `subnet-app-b` | `10.20.12.0/24` | Réserve applicative | AZ B |
| `subnet-db-a` | `10.20.21.0/24` | Base de données privée | AZ A |
| `subnet-db-b` | `10.20.22.0/24` | Réserve de base de données | AZ B |

Pour le premier laboratoire, nous ne créerons que les sous-réseaux Web A et App A. Les autres servent à comprendre comment l'architecture pourrait évoluer.

### Exercice 2A — Calcul CIDR

1. Combien d'adresses contient théoriquement un `/26` ?
2. Combien d'adresses IPv4 sont utilisables dans un sous-réseau AWS IPv4 ordinaire `/26` ?
3. Les plages `10.20.5.0/24` et `10.20.6.0/24` se chevauchent-elles ?
4. Les plages `10.20.5.0/24` et `10.20.5.128/25` se chevauchent-elles ?
5. Un sous-réseau `10.30.1.0/24` est-il contenu dans un VPC `10.20.0.0/16` ?


# MODULE 3 — Sous-réseaux publics, privés et isolés

## 3.1. Qu'est-ce qu'un sous-réseau ?

Un sous-réseau est une plage d'adresses IP à l'intérieur du VPC, associée à une seule zone de disponibilité. On y déploie des ressources compatibles, par exemple des interfaces réseau d'instances EC2.

Le sous-réseau n'est pas rendu public simplement parce que son nom contient le mot `public`. Sa connectivité dépend principalement des routes, des adresses affectées aux ressources et des contrôles de sécurité.

## 3.2. Sous-réseau public

On appelle généralement **sous-réseau public** un sous-réseau dont la table de routage possède une route vers une Internet Gateway pour le trafic Internet IPv4, habituellement `0.0.0.0/0 -> igw-...`.

Pour qu'une instance EC2 soit directement accessible depuis Internet en IPv4, il faut aussi, entre autres :

1. une Internet Gateway attachée au VPC ;
2. une route vers cette passerelle ;
3. une adresse IPv4 publique ou une adresse IPv4 Elastic correctement associée ;
4. des règles Security Group autorisant le flux demandé ;
5. des Network ACL qui ne bloquent pas le flux ;
6. un système d'exploitation et un service qui écoutent sur le bon port.

```text
Internet
   |
[Internet Gateway]
   |
[Table de routage publique]
   |  0.0.0.0/0 -> Internet Gateway
   |
[EC2 Web avec IPv4 publique]
   |
[Security Group autorisant HTTPS 443]
```

**Piège courant :** une route vers une Internet Gateway ne donne pas automatiquement une adresse publique à toutes les instances du sous-réseau.

## 3.3. Sous-réseau privé

Un sous-réseau privé n'a pas de route directe permettant à ses instances d'établir une connexion IPv4 directe vers Internet par une Internet Gateway. Il peut toutefois posséder des routes vers des services internes ou vers une NAT Gateway.

```text
[EC2 App privée]
      |
[Table de routage privée]
      |
      +-- 10.20.0.0/16 -> local
      |
      +-- éventuellement 0.0.0.0/0 -> NAT Gateway
```

Une instance privée peut communiquer avec les autres ressources du VPC si les règles et les routes le permettent. Elle n'a pas besoin d'une IPv4 publique pour communiquer avec une instance Web du même VPC.

## 3.4. Sous-réseau isolé

Un sous-réseau isolé ne possède pas de route vers des réseaux externes, hormis les routes locales et les routes explicitement prévues pour des communications internes. Il convient notamment à certains déploiements de bases de données qui ne doivent pas initier de trafic Internet.

```text
[Application]
     |
     | flux autorisé par les règles
     v
[Base de données en sous-réseau isolé]
     |
     +-- aucune route par défaut vers Internet
```

Un sous-réseau isolé n'est pas, à lui seul, une garantie complète de sécurité. Les autorisations réseau, les identités, la configuration de la base de données et les contrôles d'accès restent importants.

## 3.5. Tableau comparatif

| Propriété | Public | Privé avec NAT | Isolé |
|---|---|---|---|
| Route Internet directe via IGW | Oui, généralement | Non | Non |
| Connexion IPv4 sortante vers Internet | Possible avec les conditions requises | Possible via NAT Gateway | Non, sauf autre chemin explicitement conçu |
| Connexion entrante initiée depuis Internet | Possible si adressage et règles le permettent | Non directement via NAT de sortie | Non directement |
| Exemples de ressources | Reverse proxy, serveur Web public, NAT Gateway publique | Serveur applicatif, mises à jour sortantes via NAT | Base de données ou service interne restreint |


# MODULE 4 — Routage, tables de routage et passerelles

## 4.1. Le rôle du routage

Le routage consiste à déterminer où envoyer un paquet en fonction de son adresse de destination. Dans AWS, une table de routage contient des routes constituées d'une destination et d'une cible.

Exemples de cibles possibles :

- `local` : communication à l'intérieur des plages du VPC ;
- une Internet Gateway ;
- une NAT Gateway ;
- une connexion VPC Peering ;
- une Virtual Private Gateway ou d'autres cibles réseau prises en charge.

Une table de routage est un ensemble de règles, et les sous-réseaux l'utilisent par association. Si aucune association explicite n'est configurée, le sous-réseau utilise la table principale du VPC.

## 4.2. La route locale `local`

Lorsqu'un VPC possède le CIDR `10.20.0.0/16`, une route locale permet la communication entre les ressources qui utilisent les plages du VPC, sous réserve des autres contrôles réseau.

Exemple :

```text
Destination      Cible
10.20.0.0/16     local
```

Cette route ne donne pas accès à Internet. Elle permet le routage au sein du VPC.

## 4.3. La table de routage publique

Pour un VPC `10.20.0.0/16`, une table publique peut être configurée ainsi :

| Destination | Cible | Utilité |
|---|---|---|
| `10.20.0.0/16` | `local` | Communication à l'intérieur du VPC |
| `0.0.0.0/0` | Internet Gateway | Trafic IPv4 dont la destination n'est pas plus spécifique dans le VPC |

Schéma :

```text
                    INTERNET
                       ^
                       |
                 [Internet Gateway]
                       ^
                       |
          0.0.0.0/0 -> IGW
                       |
                [Table publique]
                       |
                 [Subnet Web]
```

`0.0.0.0/0` désigne toutes les destinations IPv4. La route est une route par défaut : elle s'applique lorsqu'aucune route plus spécifique ne l'emporte.

## 4.4. La table de routage privée sans accès Internet

Pour le laboratoire initial :

| Destination | Cible | Utilité |
|---|---|---|
| `10.20.0.0/16` | `local` | Communication à l'intérieur du VPC |

Cette table ne contient pas de route IPv4 par défaut vers Internet. L'instance applicative privée peut tout de même communiquer avec le serveur Web public par l'intermédiaire du routage local, si les règles de sécurité l'autorisent.

## 4.5. Internet Gateway (IGW)

Une **Internet Gateway** permet la communication entre le VPC et Internet. Pour utiliser le chemin Internet IPv4 depuis un sous-réseau, la passerelle doit être attachée au VPC et la table de routage doit diriger les destinations appropriées vers elle.

L'IGW ne remplace pas les règles de sécurité et n'attribue pas automatiquement une IPv4 publique à chaque instance.

```text
Client Internet
      |
      v
[Internet Gateway]
      |
[Table publique : 0.0.0.0/0 -> IGW]
      |
[Interface réseau EC2]
      |
[IPv4 privée + IPv4 publique associée, selon configuration]
```

## 4.6. NAT Gateway

Une **NAT Gateway publique** permet généralement aux ressources de sous-réseaux privés d'initier des communications vers Internet sans accepter de nouvelles connexions entrantes non sollicitées depuis Internet à destination de ces ressources privées.

Pour un scénario IPv4 classique, la NAT Gateway publique est créée dans un sous-réseau public, reçoit une adresse IP Elastic et utilise l'Internet Gateway du VPC pour atteindre Internet.

```text
                    INTERNET
                       ^
                       |
                 [Internet Gateway]
                       ^
                       |
                [NAT Gateway]
               dans subnet public
                       ^
                       |
        route 0.0.0.0/0 -> NAT Gateway
                       ^
                       |
            [Table privée associée]
                       ^
                       |
                [EC2 App privée]
```

Dans l'exemple, l'instance privée initie la connexion. La NAT Gateway effectue la traduction d'adresse nécessaire, puis le trafic de réponse est associé à la connexion initiée. La NAT Gateway n'est pas un moyen d'exposer directement l'application privée à des connexions entrantes non sollicitées.

**Attention aux coûts :** une NAT Gateway peut entraîner des frais de création, de fonctionnement et de traitement du trafic selon la région et la tarification applicable. Ne la crée pas pour un exercice si tu n'en as pas réellement besoin.

Une seule NAT Gateway pour plusieurs zones peut créer une dépendance interzone et un point de défaillance. Dans une architecture de production, il faut étudier les exigences de disponibilité et les coûts. Une NAT Gateway par zone peut améliorer la résilience, mais augmente généralement le coût.

## 4.7. Une adresse publique est-elle suffisante ?

Non. Une instance ne devient accessible que si l'ensemble du chemin est correct.

Exemple de checklist pour accéder à un serveur Web :

```text
[ ] L'instance est démarrée.
[ ] Le service Web écoute sur le port attendu.
[ ] L'instance possède l'adresse IPv4 publique requise.
[ ] Le VPC possède une Internet Gateway attachée.
[ ] Le sous-réseau utilise une table avec 0.0.0.0/0 -> IGW.
[ ] Le Security Group autorise le port depuis la source voulue.
[ ] La Network ACL ne bloque pas les paquets nécessaires.
[ ] Le système d'exploitation ne bloque pas le port.
[ ] L'adresse IP ou le DNS utilisé est correct.
```

### Exercice 4A — Choisir la bonne route

Pour chaque besoin, identifie la route ou le composant approprié :

1. Deux instances de deux sous-réseaux du même VPC doivent communiquer.
2. Une instance Web publique doit répondre aux clients Internet.
3. Une instance privée doit télécharger des mises à jour via Internet sans recevoir de nouvelles connexions entrantes non sollicitées.
4. Une instance privée ne doit posséder aucun chemin Internet par défaut.


# MODULE 5 — Security Groups et Network ACL

## 5.1. Pourquoi faut-il filtrer le trafic ?

Le routage détermine le chemin possible des paquets. Les mécanismes de filtrage déterminent quels flux sont autorisés ou bloqués.

Dans un VPC, les contrôles réseau fondamentaux étudiés ici sont :

- les **Security Groups (SG)**, associés aux interfaces réseau des ressources ;
- les **Network Access Control Lists (Network ACL ou NACL)**, associées aux sous-réseaux.

Ces contrôles sont complémentaires.

## 5.2. Security Group

Un Security Group est un pare-feu virtuel associé à une ou plusieurs interfaces réseau. Il contient des règles entrantes et sortantes.

Caractéristiques principales :

- les règles entrantes définissent quels flux entrants sont autorisés ;
- les règles sortantes définissent quels flux sortants sont autorisés ;
- les règles sont autorisantes : on ajoute les autorisations nécessaires, il n'existe pas de règle de refus explicite dans le SG ;
- le filtrage est avec état (*stateful*) : le trafic de réponse à une connexion autorisée est pris en compte automatiquement.

Exemple de SG pour un serveur Web :

| Direction | Protocole | Port | Source ou destination | Raison |
|---|---|---:|---|---|
| Entrante | TCP | 443 | `0.0.0.0/0` | HTTPS public, si le service est destiné à Internet |
| Entrante | TCP | 80 | `0.0.0.0/0` | HTTP, uniquement si nécessaire ou pour rediriger vers HTTPS |
| Entrante | TCP | 22 | Adresse IP d'administration `/32` | SSH restreint, seulement si utilisé |
| Sortante | Selon le besoin | Selon le besoin | Destinations nécessaires | Limiter si une politique de sortie stricte est recherchée |

Pour un serveur Web public, ouvrir le port 22 à `0.0.0.0/0` est une mauvaise pratique. Si SSH est nécessaire, restreins la source à une adresse IP d'administration reconnue et préfère une méthode d'administration gérée, par exemple AWS Systems Manager Session Manager, lorsque ton environnement le permet.

## 5.3. Exemple de groupe de sécurité applicatif

Supposons que le serveur Web appelle l'application sur TCP 8080.

| Direction | Protocole | Port | Source ou destination | Raison |
|---|---|---:|---|---|
| Entrante | TCP | 8080 | SG du serveur Web (`sg-web-lab`) | Seul le niveau Web doit joindre ce port |

La règle fait référence au groupe de sécurité du serveur Web, et non à `0.0.0.0/0`. Elle permet d'exprimer une intention : seules les interfaces associées au SG Web peuvent être à l'origine du flux autorisé, sous réserve des autres contrôles réseau.

## 5.4. Network ACL

Une Network ACL est un pare-feu au niveau du sous-réseau. Elle possède des règles entrantes et sortantes numérotées. Elle est **sans état** (*stateless*) : le trafic retour doit être autorisé séparément dans l'autre sens.

Les Network ACL peuvent contenir des règles d'autorisation et de refus. Les règles sont évaluées par ordre numérique, en commençant par le plus petit numéro applicable.

Pour un premier laboratoire, il est généralement plus simple de conserver la Network ACL par défaut si elle correspond à la configuration attendue, puis de gérer les autorisations de l'application avec les Security Groups. Dans une organisation réelle, la politique NACL peut être différente.

## 5.5. Security Group et NACL : comparaison

| Propriété | Security Group | Network ACL |
|---|---|---|
| Niveau | Interface réseau / ressource | Sous-réseau |
| État | Stateful | Stateless |
| Règles | Autorisations | Autorisations et refus |
| Ordre d'évaluation | Toutes les règles applicables participent à l'autorisation | Règles numérotées évaluées dans l'ordre |
| Trafic retour | Géré par le caractère stateful | Doit être autorisé séparément |
| Utilisation typique dans ce cours | Définir précisément quels serveurs peuvent communiquer | Couche de contrôle supplémentaire au niveau du sous-réseau |

## 5.6. Une règle de sécurité ne crée pas une route

Un Security Group peut autoriser TCP 8080, mais si la route vers la destination est incorrecte, la connexion ne fonctionnera pas. Inversement, une route valide n'autorise pas le flux si le SG bloque le port.

```text
Connexion réussie = chemin réseau valide
                    + adressage correct
                    + règles SG autorisantes
                    + NACL compatible
                    + pare-feu du système correct
                    + application à l'écoute
```

### Exercice 5A — Évaluer les règles

1. Le SG applicatif autorise TCP 8080 uniquement depuis `sg-web-lab`. Une machine Internet qui connaît l'adresse IP privée du serveur peut-elle directement joindre l'application depuis Internet ?
2. Le SG Web autorise HTTPS 443 mais aucune route ne permet l'accès depuis Internet. Le service sera-t-il joignable ?
3. Pourquoi faut-il être prudent lorsqu'on ouvre SSH à `0.0.0.0/0` ?
4. Quelle est la différence principale entre le caractère stateful d'un SG et le caractère stateless d'une NACL ?


# MODULE 6 — Architecture de référence du cours

## 6.1. Scénario

Nous allons concevoir un petit réseau d'entreprise avec :

- un VPC personnalisé ;
- un sous-réseau Web public ;
- un sous-réseau applicatif privé ;
- une Internet Gateway ;
- une table de routage publique et une table de routage privée ;
- un Security Group Web ;
- un Security Group Applicatif ;
- une instance EC2 Web et une instance EC2 Applicative.

L'objectif est de permettre aux utilisateurs d'atteindre le serveur Web, puis au serveur Web de joindre le serveur applicatif sur TCP 8080. L'instance applicative ne recevra pas d'adresse IPv4 publique.

## 6.2. Schéma global

```text
                           UTILISATEURS
                                |
                                | HTTP 80 / HTTPS 443
                                v
                       +--------------------+
                       |      INTERNET      |
                       +--------------------+
                                |
                                v
                       [Internet Gateway]
                                |
                                v
+================================================================+
|                    VPC : 10.20.0.0/16                          |
|                                                                |
|   +---------------------- AZ A -----------------------------+   |
|   |                                                         |   |
|   |  SUBNET WEB PUBLIC : 10.20.1.0/24                       |   |
|   |  Route : 10.20.0.0/16 -> local                          |   |
|   |          0.0.0.0/0 -> Internet Gateway                  |   |
|   |                                                         |   |
|   |       [EC2 WEB]                                         |   |
|   |       IPv4 privée + IPv4 publique                       |   |
|   |       SG : sg-web-lab                                   |   |
|   +---------------------------+-----------------------------+   |
|                               |                                |
|                               | TCP 8080                       |
|                               | autorisé depuis sg-web-lab     |
|                               v                                |
|   +---------------------------+-----------------------------+   |
|   |  SUBNET APP PRIVÉ : 10.20.11.0/24                      |   |
|   |  Route : 10.20.0.0/16 -> local                         |   |
|   |                                                         |   |
|   |       [EC2 APP]                                         |   |
|   |       IPv4 privée uniquement                            |   |
|   |       SG : sg-app-lab                                   |   |
|   +---------------------------------------------------------+   |
|                                                                |
+================================================================+
```

Le diagramme est logique : l'adresse publique du serveur Web et l'accès Internet doivent être configurés correctement. L'instance applicative n'a ni IPv4 publique ni route Internet par défaut dans la configuration initiale.

## 6.3. Plan d'adressage de référence

| Élément | Valeur d'exemple |
|---|---|
| VPC | `10.20.0.0/16` |
| Sous-réseau Web public | `10.20.1.0/24` |
| Sous-réseau applicatif privé | `10.20.11.0/24` |
| Table publique | `rtb-public-lab` |
| Table privée | `rtb-private-lab` |
| Internet Gateway | `igw-lab` |
| Security Group Web | `sg-web-lab` |
| Security Group Applicatif | `sg-app-lab` |
| Port HTTP de démonstration | TCP 80 |
| Port applicatif de démonstration | TCP 8080 |

Les noms sont des exemples : adapte-les à la région et à la convention de nommage de ton compte.

## 6.4. Matrice des communications attendues

| Source | Destination | Port | Attendu | Justification |
|---|---|---:|---|---|
| Client autorisé sur Internet | EC2 Web | TCP 80 | Autorisé si HTTP est activé | Démonstration Web |
| Client autorisé sur Internet | EC2 Web | TCP 443 | Autorisé si HTTPS est configuré | Accès Web chiffré |
| Internet | EC2 App | TCP 8080 | Non accessible directement | Application privée sans IP publique et sans route Internet directe |
| EC2 Web | EC2 App | TCP 8080 | Autorisé par `sg-app-lab` depuis `sg-web-lab` | Flux applicatif prévu |
| EC2 App | Internet | Tout | Non prévu dans la configuration initiale | Pas de route par défaut vers Internet |
| EC2 Web | EC2 App | TCP 22 | Non autorisé par la conception initiale | Administration distincte du flux applicatif |

Cette matrice décrit la politique voulue. Le fonctionnement réel doit être vérifié avec les routes, les SG, les NACL, le système d'exploitation et le service applicatif.


# MODULE 7 — Atelier guidé : construire le VPC

## 7.1. Préparer le laboratoire

Avant de commencer :

1. Connecte-toi à la console AWS avec un compte autorisé à créer les ressources nécessaires.
2. Sélectionne une région pour le laboratoire et conserve-la pour toutes les étapes.
3. Vérifie les coûts éventuels des ressources que tu vas créer.
4. Évite d'utiliser des données sensibles ou un environnement de production.
5. Prépare une adresse IP publique d'administration si tu dois autoriser SSH. Utilise une règle `/32`, pas une ouverture mondiale.

Les libellés exacts de la console peuvent évoluer. Si une page a changé, recherche la ressource par son nom dans la console AWS ou consulte la documentation officielle.

## 7.2. Étape 1 — Créer le VPC

Dans la console VPC :

1. Choisis la création d'un VPC.
2. Sélectionne un VPC uniquement si l'assistant propose plusieurs types de ressources à créer automatiquement, afin de comprendre les composants un par un.
3. Attribue le nom `vpc-entreprise-lab`.
4. Configure le CIDR IPv4 `10.20.0.0/16`.
5. Conserve les autres options par défaut qui conviennent au laboratoire.
6. Crée le VPC.

Vérifie ensuite le CIDR dans les détails du VPC.

**Résultat attendu :** le VPC existe avec la plage `10.20.0.0/16`.

## 7.3. Étape 2 — Créer les sous-réseaux

Crée le sous-réseau Web public :

- nom : `subnet-web-a` ;
- CIDR : `10.20.1.0/24` ;
- zone de disponibilité : une AZ de la région choisie.

Crée ensuite le sous-réseau applicatif privé :

- nom : `subnet-app-a` ;
- CIDR : `10.20.11.0/24` ;
- zone de disponibilité : idéalement la même AZ que le Web pour ce premier laboratoire.

Vérifie que les deux plages sont distinctes et comprises dans le VPC.

## 7.4. Étape 3 — Créer et attacher l'Internet Gateway

1. Dans la section Internet Gateways, crée `igw-lab`.
2. Attache-la à `vpc-entreprise-lab`.
3. Vérifie que son état indique qu'elle est attachée au bon VPC.

Sans attachement, une route vers cette passerelle ne peut pas fournir le chemin Internet attendu.

## 7.5. Étape 4 — Créer la table de routage publique

1. Crée une table de routage nommée `rtb-public-lab` dans le VPC.
2. Vérifie la route locale `10.20.0.0/16 -> local`.
3. Ajoute la route `0.0.0.0/0 -> igw-lab`.
4. Dans les associations de sous-réseaux, associe explicitement `subnet-web-a` à `rtb-public-lab`.
5. Vérifie l'association après enregistrement.

Table attendue :

| Destination | Cible |
|---|---|
| `10.20.0.0/16` | `local` |
| `0.0.0.0/0` | `igw-lab` |

## 7.6. Étape 5 — Créer la table de routage privée

1. Crée `rtb-private-lab` dans le VPC.
2. Vérifie la route locale `10.20.0.0/16 -> local`.
3. N'ajoute pas de route `0.0.0.0/0` vers Internet Gateway.
4. Associe explicitement `subnet-app-a` à `rtb-private-lab`.

Table attendue :

| Destination | Cible |
|---|---|
| `10.20.0.0/16` | `local` |

**Important :** si tu ne l'associes pas explicitement, le sous-réseau utilisera la table principale du VPC. Vérifie toujours la table réellement associée au sous-réseau.

## 7.7. Étape 6 — Créer le Security Group Web

Crée `sg-web-lab` dans `vpc-entreprise-lab`.

Exemple de règles entrantes pour une démonstration HTTP :

| Type | Protocole | Port | Source |
|---|---|---:|---|
| HTTP | TCP | 80 | `0.0.0.0/0` si le service est volontairement public |

Si tu configures HTTPS, ajoute TCP 443 uniquement lorsque le service et le certificat sont prêts.

Pour SSH, uniquement si nécessaire :

| Type | Protocole | Port | Source |
|---|---|---:|---|
| SSH | TCP | 22 | `ADRESSE_IP_ADMIN/32` |

Remplace `ADRESSE_IP_ADMIN/32` par la véritable IPv4 publique de l'adresse d'administration autorisée. Ne colle pas ce texte littéral dans la console.

Pour le premier test HTTP, SSH peut être omis si tu utilises une méthode d'administration alternative. Le SG est un contrôle réseau, pas un remplacement de l'authentification du système d'exploitation.

## 7.8. Étape 7 — Créer le Security Group applicatif

Crée `sg-app-lab` dans le même VPC.

Règle entrante :

| Type | Protocole | Port | Source |
|---|---|---:|---|
| Personnalisé TCP | TCP | 8080 | `sg-web-lab` |

Sélectionne le Security Group Web comme source de la règle, plutôt que d'autoriser toutes les adresses IP.

Cette règle autorise le flux TCP 8080 en provenance des ressources concernées par `sg-web-lab`. Elle ne configure pas automatiquement l'application : le service doit écouter sur le bon port et le pare-feu du système doit l'autoriser.

## 7.9. Étape 8 — Lancer l'instance EC2 Web

Lance une instance de laboratoire dans `subnet-web-a`.

Points essentiels à vérifier pendant le lancement :

- image système adaptée à ton exercice ;
- type d'instance adapté aux besoins ;
- VPC : `vpc-entreprise-lab` ;
- sous-réseau : `subnet-web-a` ;
- attribution d'une IPv4 publique activée pour le test Internet ;
- Security Group : `sg-web-lab` ;
- clés et méthode d'administration configurées de façon sécurisée.

Vérifie ensuite les détails réseau de l'instance : IPv4 privée, adresse publique éventuelle, sous-réseau et Security Group.

## 7.10. Étape 9 — Lancer l'instance EC2 Applicative

Lance une seconde instance dans `subnet-app-a`.

Vérifie les points suivants :

- VPC : `vpc-entreprise-lab` ;
- sous-réseau : `subnet-app-a` ;
- aucune IPv4 publique attribuée ;
- Security Group : `sg-app-lab` ;
- méthode d'administration prévue sans exposer directement le serveur à Internet.

L'adresse IPv4 privée de l'instance applicative doit être disponible dans la console. Note-la pour les tests réalisés depuis le serveur Web.

## 7.11. Étape 10 — Installer et démarrer les services

L'installation dépend de l'image système choisie. Pour un système Linux compatible, voici un exemple de démonstration simple. Adapte les commandes à la distribution installée et aux politiques de ton entreprise.

Sur le serveur Web, il faut installer un service HTTP qui écoute sur TCP 80. Par exemple, sur une distribution qui utilise `apt` :

```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl enable --now nginx
sudo systemctl status nginx
```

Sur d'autres distributions, le gestionnaire de paquets et le nom du service peuvent différer.

Depuis un navigateur, teste :

```text
http://IPV4_PUBLIQUE_DU_SERVEUR_WEB
```

Utilise HTTP uniquement pour cette démonstration simple. Une application réelle doit privilégier HTTPS et une gestion correcte des certificats.

Sur le serveur applicatif, démarre un service de démonstration qui écoute sur TCP 8080. Il peut s'agir d'une application déjà fournie dans le cadre de ton environnement de formation. Si tu écris un petit service de test, vérifie qu'il écoute sur l'interface privée appropriée et non uniquement sur `127.0.0.1`.

**À ne pas confondre :** le Security Group autorise le flux réseau ; il ne crée ni le service applicatif ni le processus qui écoute sur le port.

## 7.12. Étape 11 — Tester le flux Web vers App

Depuis le serveur Web, teste le port 8080 sur l'adresse IPv4 privée de l'instance applicative.

Par exemple, avec un outil disponible tel que `nc` :

```bash
nc -vz IP_PRIVEE_DE_L_APP 8080
```

Remplace `IP_PRIVEE_DE_L_APP` par l'adresse privée réelle.

Si l'outil n'est pas installé, utilise un autre outil de diagnostic disponible. Une connexion TCP réussie prouve que le port est joignable depuis cette source, mais ne garantit pas à elle seule le bon fonctionnement de toute l'application.

Résultat attendu : la connexion est acceptée si le service est à l'écoute et si le routage et les règles réseau sont corrects.

## 7.13. Étape 12 — Vérifier que l'application n'est pas directement publique

Depuis un poste extérieur au VPC, tente de joindre directement l'adresse privée de l'application : cette adresse n'est pas normalement routable depuis Internet.

Ne cherche pas à exposer l'application en lui attribuant une adresse publique simplement pour contourner une erreur de configuration. Le but est de conserver le niveau applicatif privé et de corriger le chemin Web vers App.

### Contrôle final de l'atelier

```text
[ ] VPC créé avec 10.20.0.0/16
[ ] Deux sous-réseaux non chevauchants créés
[ ] Internet Gateway attachée au VPC
[ ] Route publique 0.0.0.0/0 -> IGW
[ ] Route locale présente dans les deux tables
[ ] Sous-réseau Web associé à la table publique
[ ] Sous-réseau App associé à la table privée
[ ] EC2 Web possède le profil d'adressage public requis
[ ] EC2 App ne possède pas d'IPv4 publique
[ ] SG Web n'ouvre que les ports nécessaires
[ ] SG App autorise TCP 8080 depuis SG Web
[ ] Page Web accessible sur le port configuré
[ ] Flux Web -> App vérifié sur TCP 8080
```


# MODULE 8 — Dépannage réseau méthodique

## 8.1. Une page Web ne s'ouvre pas

Ne modifie pas toutes les règles au hasard. Vérifie une couche après l'autre :

1. **Application** : le service Web est-il démarré et écoute-t-il sur le port attendu ?
2. **Système d'exploitation** : un pare-feu local bloque-t-il le port ?
3. **Security Group** : le port entrant est-il autorisé depuis la bonne source ?
4. **Network ACL** : des règles de sous-réseau bloquent-elles le trafic ou les réponses ?
5. **Adresse** : utilises-tu la bonne IPv4 publique ou le bon nom DNS ?
6. **Adressage public** : l'instance possède-t-elle une IPv4 publique ou une adresse Elastic adaptée ?
7. **Routage** : la table associée au sous-réseau contient-elle la route vers l'Internet Gateway ?
8. **Passerelle** : l'Internet Gateway est-elle attachée au bon VPC ?

## 8.2. Le serveur Web ne joint pas le serveur applicatif

Vérifie dans cet ordre :

1. L'adresse de destination est-elle l'IPv4 privée correcte de l'application ?
2. Les deux ressources sont-elles dans le bon VPC, ou existe-t-il un chemin réseau explicitement configuré entre leurs réseaux ?
3. La route locale du VPC est-elle présente et le sous-réseau utilise-t-il la bonne table ?
4. Le SG applicatif autorise-t-il TCP 8080 depuis le SG Web ?
5. Le SG Web autorise-t-il le trafic sortant nécessaire ?
6. La NACL de chaque sous-réseau permet-elle le trafic aller et retour ?
7. Le service applicatif écoute-t-il sur l'adresse et le port attendus ?
8. Le pare-feu local du serveur applicatif autorise-t-il le port ?

## 8.3. L'instance privée ne peut pas télécharger de mises à jour

Dans le laboratoire initial, ce résultat est attendu : aucune route Internet par défaut n'est définie pour le sous-réseau privé.

Solutions possibles selon le besoin :

- ne pas donner d'accès Internet si ce n'est pas requis ;
- utiliser une NAT Gateway configurée correctement pour le trafic IPv4 sortant ;
- utiliser des VPC endpoints lorsque les services AWS visés et l'architecture le permettent ;
- employer une architecture de gestion et de mise à jour prévue par l'organisation.

N'ajoute pas une route par défaut vers l'Internet Gateway en espérant que cela rende l'instance privée correctement privée tout en lui donnant Internet. Pour une sortie IPv4 habituelle depuis un sous-réseau privé, le chemin classique utilise une NAT Gateway.

## 8.4. Distinguer les symptômes

| Symptôme | Causes possibles |
|---|---|
| Délai d'attente (timeout) | Route incorrecte, filtrage SG/NACL, service absent, pare-feu local, mauvaise adresse |
| Connexion refusée | Hôte joignable mais aucun processus n'écoute sur le port, ou refus local actif |
| Nom DNS introuvable | Nom incorrect, problème de résolution DNS, configuration du résolveur |
| Web fonctionne mais App échoue | SG App, port applicatif, écoute locale, route ou filtrage entre sous-réseaux |
| App peut sortir avec NAT mais n'est pas directement joignable d'Internet | Comportement généralement attendu pour une ressource privée avec NAT de sortie |

Un même symptôme peut avoir plusieurs causes : traite ce tableau comme un point de départ et valide chaque hypothèse par un test.

## 8.5. VPC Flow Logs

VPC Flow Logs permettent de collecter des informations sur le trafic IP vers et depuis les interfaces réseau, les sous-réseaux ou le VPC, selon la configuration choisie. Ils peuvent aider au diagnostic.

Les Flow Logs ne remplacent pas une capture complète de tous les paquets et ne montrent pas automatiquement chaque détail applicatif. Il faut les interpréter avec les règles de sécurité, les journaux système et les tests de connectivité.


# MODULE 9 — Bonnes pratiques et erreurs fréquentes

## 9.1. Bonnes pratiques

1. **Planifier les plages IP.** Choisis un CIDR qui permet l'évolution et évite les chevauchements avec les réseaux locaux et les autres VPC.
2. **Séparer les rôles.** Web, application et base de données n'ont pas nécessairement besoin des mêmes flux réseau.
3. **Limiter les autorisations.** N'ouvre que les ports nécessaires, depuis les sources nécessaires.
4. **Éviter SSH public mondial.** Si SSH est indispensable, limite la source ; étudie également une méthode d'administration gérée.
5. **Ne pas donner d'IP publique par défaut.** Les ressources privées ne doivent pas être exposées sans raison.
6. **Documenter les routes.** Chaque route doit répondre à un besoin identifié.
7. **Associer explicitement les tables.** Vérifie quelle table chaque sous-réseau utilise réellement.
8. **Tester avec une méthode reproductible.** Note la source, la destination, le protocole, le port et le résultat.
9. **Prévoir la résilience.** Pour une architecture de production, évalue plusieurs zones, le comportement en cas de panne et les dépendances interzones.
10. **Surveiller les coûts.** Les ressources réseau et les adresses publiques peuvent être facturées. Supprime le laboratoire après utilisation.

## 9.2. Erreurs de débutant fréquentes

### Erreur 1 — Croire qu'un sous-réseau est public parce que son nom dit `public`

Le nom n'a aucun effet de routage. La table associée, les adresses et les règles déterminent la connectivité.

### Erreur 2 — Oublier l'association de la table de routage

Une table peut être parfaitement configurée mais non utilisée par le sous-réseau ciblé. Contrôle l'association réelle.

### Erreur 3 — Ouvrir tous les ports pour « faire fonctionner » l'application

Cette méthode réduit la sécurité sans identifier la cause. Il faut autoriser le port précis depuis la source précise.

### Erreur 4 — Confondre adresse privée et adresse publique

Une IPv4 privée sert aux échanges sur des réseaux privés et n'est pas directement routable depuis Internet. Une instance EC2 a généralement besoin d'une adresse publique associée pour recevoir directement des connexions IPv4 d'Internet via l'IGW.

### Erreur 5 — Croire que NAT Gateway rend l'application accessible d'Internet

Une NAT Gateway publique sert au trafic initié depuis le réseau privé vers l'extérieur. Elle ne constitue pas une publication entrante directe du serveur privé.

### Erreur 6 — Oublier le service applicatif

Un port autorisé dans le SG ne démarre pas de processus. Vérifie que l'application écoute réellement sur le bon port et la bonne interface.

### Erreur 7 — Oublier les ressources facturables

Une expérience oubliée peut continuer à engendrer des frais. Vérifie les ressources actives, les adresses Elastic et les passerelles avant de fermer le laboratoire.


# MODULE 10 — Exercices récapitulatifs avec corrections

## Exercice 10A — Reconnaître les composants

Associe chaque élément à sa fonction :

1. VPC
2. Sous-réseau
3. Table de routage
4. Internet Gateway
5. NAT Gateway
6. Security Group
7. Network ACL

Fonctions :

A. Pare-feu avec état associé aux interfaces réseau.  
B. Réseau virtuel global.  
C. Plage d'adresses située dans le VPC et associée à une AZ.  
D. Règles indiquant vers quelle cible envoyer le trafic.  
E. Passerelle reliant le VPC à Internet.  
F. Filtrage stateless au niveau du sous-réseau.  
G. Service de traduction permettant habituellement aux ressources privées IPv4 d'initier des connexions vers l'extérieur.

## Exercice 10B — Diagnostic de routage

Un sous-réseau nommé `subnet-web-a` contient une instance EC2 qui possède une IPv4 publique. L'instance ne répond pas sur HTTP. La table réellement associée au sous-réseau contient uniquement :

```text
10.20.0.0/16 -> local
```

Quelle est l'une des erreurs les plus probables ? Quelle route et quelle cible devraient être envisagées pour un serveur Web publiquement accessible en IPv4 ? Donne également deux autres contrôles à effectuer.

## Exercice 10C — Flux entre Web et App

Le serveur Web `10.20.1.20` doit joindre le serveur applicatif `10.20.11.30` sur TCP 8080.

Le SG applicatif autorise TCP 8080 depuis `0.0.0.0/0`. Propose une règle plus restrictive et explique pourquoi elle est préférable.

## Exercice 10D — Internet depuis une instance privée

L'instance applicative privée n'a pas d'IPv4 publique et son sous-réseau n'a pas de route par défaut. Elle ne peut pas télécharger des paquets depuis Internet.

1. Est-ce nécessairement un défaut ?
2. Quelle architecture IPv4 classique permettrait une sortie Internet sans exposer directement l'instance privée ?
3. Quelle route par défaut serait typiquement configurée dans la table privée ?

## Exercice 10E — Sécurité

Une équipe ajoute la règle suivante au SG de la base de données :

```text
TCP 3306 depuis 0.0.0.0/0
```

Explique le risque et propose une règle de remplacement adaptée à une architecture à trois niveaux.


# MODULE 11 — Synthèse avant le challenge

## 11.1. Carte mentale textuelle

```text
AWS VPC
|
+-- ADRESSAGE
|   +-- CIDR du VPC
|   +-- CIDR de chaque sous-réseau
|   +-- Pas de chevauchement
|
+-- SOUS-RÉSEAUX
|   +-- Un sous-réseau = une AZ
|   +-- Public : route vers IGW pour Internet IPv4
|   +-- Privé : pas de route directe vers IGW
|   +-- Isolé : pas de route externe par défaut
|
+-- ROUTAGE
|   +-- Route local = communications dans les plages du VPC
|   +-- Route publique 0.0.0.0/0 -> IGW
|   +-- Route privée 0.0.0.0/0 -> NAT Gateway, si nécessaire
|
+-- SÉCURITÉ
|   +-- Security Group : stateful, associé aux interfaces
|   +-- Network ACL : stateless, associée au sous-réseau
|   +-- Minimum de privilèges
|
+-- DIAGNOSTIC
    +-- Adressage
    +-- Routes et associations
    +-- SG et NACL
    +-- Pare-feu du système
    +-- Service à l'écoute
```

## 11.2. Les cinq questions à se poser face à un problème réseau

1. **Quelle est la source et quelle est la destination ?** Note les adresses et le port.
2. **Le chemin existe-t-il ?** Vérifie les routes et les passerelles.
3. **Les règles autorisent-elles le flux ?** Vérifie SG et NACL dans les deux directions pertinentes.
4. **Le service fonctionne-t-il ?** Vérifie le processus et l'écoute locale.
5. **Le résultat est-il conforme à la politique prévue ?** Un accès refusé peut être un comportement de sécurité attendu plutôt qu'une panne.


# MODULE 12 — CHALLENGE FINAL : concevoir et dépanner un réseau AWS

> **Le challenge fait partie de ce même cours.** Il doit être réalisé après les modules précédents. Aucun fichier complémentaire n'est nécessaire.

## 12.1. Scénario

Tu es administrateur réseau junior dans une entreprise qui souhaite héberger une application de démonstration dans AWS.

L'application possède trois niveaux :

- Web : reçoit le trafic utilisateur ;
- App : traite les requêtes métier ;
- DB : stocke les données.

L'équipe veut une architecture simple, segmentée et préparée pour une évolution vers deux zones de disponibilité. Pour limiter les dépenses de formation, le laboratoire initial ne doit pas créer de NAT Gateway. L'accès à Internet est nécessaire uniquement pour le serveur Web de démonstration.

Ton travail consiste à proposer le plan d'adressage, construire ou décrire les routes, écrire les règles de sécurité attendues et diagnostiquer les incidents indiqués.

## 12.2. Contraintes obligatoires

- CIDR du VPC : `10.30.0.0/16`.
- Les sous-réseaux ne doivent pas se chevaucher.
- Les serveurs applicatif et base de données ne doivent pas avoir d'IPv4 publique.
- Le serveur Web doit pouvoir recevoir du HTTP de démonstration depuis Internet.
- Le serveur Web doit pouvoir joindre App sur TCP 8080.
- App doit pouvoir joindre DB sur TCP 3306.
- Internet ne doit pas pouvoir joindre directement App ou DB.
- SSH, s'il est utilisé, doit être limité à l'adresse d'administration `/32`.
- Aucune NAT Gateway ne doit être créée dans le laboratoire initial.
- Le plan doit prévoir une répartition des sous-réseaux dans deux AZ, même si toutes les instances ne sont pas lancées.

## 12.3. Travail demandé

### Mission A — Plan d'adressage

Propose six sous-réseaux sans chevauchement : Web A et B, App A et B, DB A et B. Utilise des plages `/24` comprises dans `10.30.0.0/16`.

Pour chacun, précise le nom, le CIDR, le rôle et la zone de disponibilité.

### Mission B — Routage

Décris les routes nécessaires pour :

1. la table publique ;
2. la table privée de l'application ;
3. la table de base de données isolée.

Indique les sous-réseaux qui doivent être associés à chaque table. Explique pourquoi App n'a pas besoin d'une route vers Internet pour recevoir les communications du serveur Web dans le même VPC.

### Mission C — Security Groups

Écris les règles entrantes minimales pour :

- `sg-web` ;
- `sg-app` ;
- `sg-db`.

Les règles doivent faire référence à des sources cohérentes. Évite d'ouvrir les ports applicatifs et de base de données à `0.0.0.0/0`.

### Mission D — Matrice des flux

Complète une matrice avec les colonnes : source, destination, protocole/port, attendu (autorisé/refusé), justification.

La matrice doit contenir au minimum ces cas :

- Internet vers Web TCP 80 ;
- Internet vers App TCP 8080 ;
- Web vers App TCP 8080 ;
- App vers DB TCP 3306 ;
- Web vers DB TCP 3306 ;
- App vers Internet TCP 443 dans le laboratoire initial ;
- poste d'administration vers Web TCP 22 depuis une adresse `/32`, si SSH est activé.

### Mission E — Dépannage

Diagnostique les incidents suivants sans supprimer toutes les règles de sécurité.

**Incident 1 :** l'instance Web est démarrée et possède une IPv4 publique. La page Web ne s'ouvre pas. Le SG autorise TCP 80, mais la table du sous-réseau ne contient que la route locale.

**Incident 2 :** Web peut joindre App en TCP 8080, mais App ne peut plus joindre DB en TCP 3306 après une modification du SG de DB.

**Incident 3 :** l'instance App ne peut pas télécharger de mises à jour depuis Internet. La table privée ne contient aucune route par défaut.

**Incident 4 :** les tests Web vers App échouent alors que la route locale et les règles SG paraissent correctes. L'application n'écoute que sur `127.0.0.1:8080`.

Pour chaque incident, donne la cause probable, le contrôle de confirmation et la correction adaptée.

### Mission F — Sécurité et exploitation

Rédige une courte procédure de fermeture du laboratoire. Elle doit indiquer comment vérifier les ressources actives et supprimer les composants créés, tout en évitant de supprimer une ressource partagée ou utilisée par un autre environnement.

## 12.4. Livrables attendus

Ton rendu doit contenir :

1. un schéma textuel général ;
2. le tableau des six sous-réseaux ;
3. les routes des tables publique, privée et isolée ;
4. les règles entrantes des trois Security Groups ;
5. la matrice des flux ;
6. le diagnostic des quatre incidents ;
7. la procédure de nettoyage du laboratoire.

## 12.5. Barème sur 100 points

| Critère | Points |
|---|---:|
| Plan d'adressage cohérent, sans chevauchement | 15 |
| Compréhension des sous-réseaux et des zones de disponibilité | 10 |
| Tables et associations de routage correctes | 20 |
| Règles Security Groups respectant le moindre privilège | 20 |
| Matrice des flux cohérente | 10 |
| Diagnostic des quatre incidents | 20 |
| Nettoyage des ressources et attention aux coûts | 5 |
| **Total** | **100** |

Repères de réussite :

- **90–100 :** bases très solides ; prêt à aborder un cours intermédiaire ;
- **75–89 :** bon niveau débutant ; revoir les notions ayant perdu des points ;
- **60–74 :** compréhension partielle ; refaire l'atelier guidé ;
- **moins de 60 :** reprendre les modules sur le CIDR, le routage et les Security Groups avant de recommencer.


# CORRECTION DU CHALLENGE FINAL

> Essaie de terminer le challenge avant de consulter cette section.

## Correction A — Exemple de plan d'adressage

| Nom | CIDR | Rôle | AZ |
|---|---|---|---|
| `subnet-web-a` | `10.30.1.0/24` | Web public | AZ A |
| `subnet-web-b` | `10.30.2.0/24` | Web public / réserve | AZ B |
| `subnet-app-a` | `10.30.11.0/24` | Application privée | AZ A |
| `subnet-app-b` | `10.30.12.0/24` | Application privée / réserve | AZ B |
| `subnet-db-a` | `10.30.21.0/24` | Base de données isolée | AZ A |
| `subnet-db-b` | `10.30.22.0/24` | Base de données isolée / réserve | AZ B |

Tous les blocs sont compris dans `10.30.0.0/16` et ne se chevauchent pas.

## Correction B — Tables de routage

### Table publique

| Destination | Cible |
|---|---|
| `10.30.0.0/16` | `local` |
| `0.0.0.0/0` | Internet Gateway |

Associer cette table à `subnet-web-a` et `subnet-web-b`.

### Table privée applicative

| Destination | Cible |
|---|---|
| `10.30.0.0/16` | `local` |

Associer cette table à `subnet-app-a` et `subnet-app-b`. Dans le laboratoire initial, aucune route Internet par défaut n'est nécessaire.

### Table isolée de base de données

| Destination | Cible |
|---|---|
| `10.30.0.0/16` | `local` |

Associer cette table à `subnet-db-a` et `subnet-db-b`. Aucune route externe par défaut ne doit être ajoutée dans ce scénario.

La route locale permet aux ressources du VPC de communiquer selon les routes et règles de sécurité. App peut donc joindre DB et Web peut joindre App sans disposer d'un accès Internet.

## Correction C — Security Groups

### `sg-web`

| Direction | Protocole | Port | Source |
|---|---|---:|---|
| Entrante | TCP | 80 | `0.0.0.0/0` pour le HTTP de démonstration public |
| Entrante | TCP | 22 | Adresse IP d'administration `/32`, uniquement si SSH est requis |

Ajouter TCP 443 seulement si HTTPS est réellement configuré. Les règles sortantes doivent correspondre aux besoins et à la politique retenue.

### `sg-app`

| Direction | Protocole | Port | Source |
|---|---|---:|---|
| Entrante | TCP | 8080 | `sg-web` |

### `sg-db`

| Direction | Protocole | Port | Source |
|---|---|---:|---|
| Entrante | TCP | 3306 | `sg-app` |

La base de données ne doit pas accepter MySQL depuis Internet ni depuis le Security Group Web si seule l'application doit accéder aux données.

## Correction D — Exemple de matrice des flux

| Source | Destination | Protocole/port | Attendu | Justification |
|---|---|---|---|---|
| Internet | Web | TCP 80 | Autorisé | Page de démonstration publique |
| Internet | App | TCP 8080 | Refusé / aucun chemin public prévu | App n'a pas d'IPv4 publique et reste privée |
| Web | App | TCP 8080 | Autorisé | SG App autorise depuis SG Web |
| App | DB | TCP 3306 | Autorisé | SG DB autorise depuis SG App |
| Web | DB | TCP 3306 | Refusé | Web ne doit pas accéder directement à la base |
| App | Internet | TCP 443 | Non disponible dans le laboratoire initial | Pas de route par défaut vers Internet et pas de NAT |
| Administration autorisée | Web | TCP 22 | Autorisé uniquement si nécessaire | Source limitée à une IPv4 `/32` |

La notion « refusé » doit être comprise dans le contexte des chemins et règles prévus. Une ressource peut être inaccessible parce qu'aucune route n'existe ou parce que le filtrage l'interdit ; les deux sont des protections distinctes.

## Correction E — Dépannage

### Incident 1

**Cause probable :** absence de route par défaut vers l'Internet Gateway dans la table associée au sous-réseau Web.

**Confirmation :** examiner l'association réelle de `subnet-web-a` et les routes de sa table.

**Correction :** attacher une Internet Gateway au VPC si nécessaire, puis ajouter `0.0.0.0/0 -> Internet Gateway` à la table publique. Vérifier aussi l'adresse publique, les règles SG/NACL et le service Web.

### Incident 2

**Cause probable :** le SG de la base de données n'autorise plus TCP 3306 depuis le SG applicatif, ou la règle a été modifiée avec une source incorrecte.

**Confirmation :** lire les règles entrantes de `sg-db`, confirmer le SG associé à l'instance de base de données, et vérifier que le service écoute sur le port attendu.

**Correction :** autoriser TCP 3306 depuis `sg-app` uniquement, si c'est bien le flux attendu. Ne pas ouvrir le port à `0.0.0.0/0`.

### Incident 3

**Cause probable :** absence intentionnelle de route Internet par défaut dans la table privée.

**Confirmation :** vérifier les routes de `subnet-app-a` et confirmer qu'aucune NAT Gateway ni autre chemin de sortie n'est configuré.

**Correction :** si les mises à jour Internet sont véritablement nécessaires, concevoir un mécanisme de sortie approprié, par exemple une NAT Gateway publique dans un sous-réseau public puis une route privée `0.0.0.0/0 -> NAT Gateway`. Vérifier au préalable les coûts. Dans le laboratoire imposé, l'absence de sortie Internet est un comportement attendu ; ne pas créer la NAT Gateway sans nécessité.

### Incident 4

**Cause probable :** l'application écoute uniquement sur l'interface de boucle locale `127.0.0.1`, donc elle accepte les connexions du serveur lui-même mais pas celles venant de l'interface réseau privée.

**Confirmation :** examiner la configuration d'écoute de l'application et utiliser un outil système pour identifier les interfaces et ports d'écoute.

**Correction :** configurer l'application pour écouter sur l'adresse privée attendue ou sur l'interface adéquate, en tenant compte des exigences de sécurité. Puis vérifier le pare-feu local et refaire le test depuis Web.

## Correction F — Nettoyage du laboratoire

1. Identifier les instances EC2 créées pour ce laboratoire et confirmer qu'elles ne sont pas utilisées ailleurs.
2. Arrêter ou supprimer les instances selon la consigne de formation. L'arrêt seul ne supprime pas nécessairement tous les coûts associés.
3. Libérer les adresses IPv4 Elastic créées si elles ne sont plus utilisées et si leur libération est appropriée.
4. Supprimer les NAT Gateways si une extension les a créées, puis vérifier les ressources associées et les frais possibles.
5. Détacher puis supprimer l'Internet Gateway du VPC de laboratoire, si elle a été créée uniquement pour cet exercice.
6. Supprimer les Security Groups personnalisés et les tables de routage personnalisées quand ils ne sont plus référencés et si la console le permet.
7. Supprimer les sous-réseaux et le VPC uniquement après avoir vérifié qu'ils ne contiennent plus de ressources utiles.
8. Vérifier dans la console de facturation et de gestion des coûts les ressources restant actives.

Ne supprime jamais une ressource partagée ou de production simplement parce que son nom ressemble à celui du laboratoire.


# ÉVALUATION FINALE ET CHECKLIST PERSONNELLE

Avant de considérer le cours terminé, assure-toi de pouvoir expliquer sans consulter les notes :

- [ ] ce qu'est un VPC et à quoi sert le CIDR du VPC ;
- [ ] pourquoi un sous-réseau dépend d'une zone de disponibilité ;
- [ ] comment calculer le nombre d'adresses IPv4 d'un CIDR ;
- [ ] pourquoi cinq adresses sont réservées dans un sous-réseau IPv4 AWS ordinaire ;
- [ ] la différence entre un sous-réseau public, privé et isolé ;
- [ ] la fonction d'une route locale ;
- [ ] pourquoi une route `0.0.0.0/0 -> IGW` est associée à une table publique ;
- [ ] comment une NAT Gateway permet une sortie IPv4 depuis un sous-réseau privé ;
- [ ] la différence entre Security Group stateful et Network ACL stateless ;
- [ ] comment limiter les flux Web vers App et App vers DB ;
- [ ] comment diagnostiquer méthodiquement un port inaccessible ;
- [ ] comment supprimer les ressources de laboratoire sans oublier les coûts.

Si plusieurs cases restent incertaines, reprends les modules correspondants et refais l'atelier avant de passer au niveau intermédiaire.


# GLOSSAIRE

| Terme | Définition simple |
|---|---|
| AWS | Amazon Web Services, plateforme de services cloud |
| VPC | Réseau virtuel isolé logiquement dans AWS |
| CIDR | Notation indiquant une plage réseau et la longueur de son préfixe |
| AZ | Zone de disponibilité dans une région AWS |
| EC2 | Service AWS permettant de lancer des instances de calcul virtuelles |
| Sous-réseau | Plage IP du VPC associée à une seule AZ |
| Route | Règle indiquant la destination et la cible du trafic |
| Table de routage | Ensemble de routes utilisées par un sous-réseau ou une passerelle |
| IGW | Internet Gateway, passerelle de connectivité Internet pour un VPC |
| NAT Gateway | Service réseau permettant notamment aux ressources privées IPv4 d'initier des connexions sortantes |
| Security Group | Pare-feu stateful associé aux interfaces réseau des ressources |
| Network ACL | Filtrage stateless associé à un sous-réseau |
| IPv4 publique | Adresse IPv4 utilisée pour la connectivité publique, selon le routage et les règles |
| IPv4 privée | Adresse utilisée pour les communications sur des réseaux privés |
| TCP | Protocole de transport orienté connexion |
| Port | Numéro identifiant un service de transport sur un hôte |
| VPC Flow Logs | Journaux contenant des informations sur le trafic IP vers ou depuis les ressources sélectionnées |


# DOCUMENTATION OFFICIELLE AWS

Les interfaces de la console et les fonctionnalités peuvent évoluer. Pour une configuration réelle, vérifie toujours la documentation officielle correspondant au service et à la région utilisés.

- [Qu'est-ce qu'Amazon VPC ?](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [Fonctionnement d'Amazon VPC](https://docs.aws.amazon.com/fr_fr/vpc/latest/userguide/how-it-works.html)
- [Bases de VPC et sous-réseaux](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-subnet-basics.html)
- [Dimensionnement des sous-réseaux et réservations d'adresses](https://docs.aws.amazon.com/fr_fr/vpc/latest/userguide/subnet-sizing.html)
- [Configuration des tables de routage](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html)
- [Groupes de sécurité](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [Network ACL](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [NAT Gateways](https://docs.aws.amazon.com/fr_fr/vpc/latest/userguide/vpc-nat-gateway.html)
- [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [Tarification Amazon VPC](https://aws.amazon.com/vpc/pricing/)


**Fin du cours `aws-vpc-debutant.md` — cours complet suivi d'un challenge final intégré.**
