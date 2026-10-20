# Cloud Networking : VPC, subnets, peering et VPN

Le cloud public déplace une partie du réseau dans un environnement virtualisé.
Les principes restent ceux du réseau : adressage, routage, filtrage et
segmentation. Ce qui change, c'est que les routeurs, switches et pare-feu sont
souvent des services managés, configurés par API.

> Analogie : un VPC est un immeuble privé dans une grande ville cloud. Les
> subnets sont les étages, les route tables sont les panneaux de direction, la
> passerelle Internet est la porte d'entrée et les security groups sont les
> serrures de chaque porte.

## 1. Les notions de base

### Région et zone de disponibilité

Un fournisseur cloud organise son infrastructure en **régions** et en **zones
de disponibilité** (AZ). Une région est une zone géographique ; une AZ est un
ou plusieurs datacenters isolés dans cette région.

Pour la haute disponibilité, on répartit les ressources sur plusieurs AZ. Un
VPC ou VNet peut s'étendre sur plusieurs AZ d'une même région.

### VPC et VNet

- **AWS** : VPC (Virtual Private Cloud).
- **Azure** : VNet (Virtual Network).

Les deux permettent de définir un espace d'adressage privé, de le découper en
sous-réseaux et de contrôler les routes et la sécurité.

| Concept | AWS | Azure |
|---|---|---|
| Réseau privé | VPC | VNet |
| Sous-réseau | Subnet | Subnet |
| Routeur virtuel | Route table | Route table / UDR |
| Internet gateway | Internet Gateway | Internet access via public IP |
| NAT sortant | NAT Gateway | NAT Gateway |
| Pare-feu réseau | Security Group + NACL | NSG + Azure Firewall |
| Peering | VPC Peering | VNet Peering |
| VPN site-to-site | Site-to-Site VPN | VPN Gateway |
| Lien privé opérateur | Direct Connect | ExpressRoute |

## 2. Adressage et découpage

Un VPC/VNet possède un bloc CIDR, par exemple :

```text
10.0.0.0/16
```

On le découpe en subnets :

```text
10.0.1.0/24   subnet public
10.0.2.0/24   subnet privé
10.0.3.0/24   subnet réservé aux bases de données
```

### Choisir le CIDR

Il faut prévoir :

- le nombre d'adresses nécessaires aujourd'hui ;
- la croissance future ;
- les autres VPC/VNet avec lesquels on fera du peering ;
- les réseaux on-premise ;
- les plages réservées par le fournisseur.

Deux réseaux qui doivent être peerés ne doivent pas avoir de CIDR qui se
chevauchent. Un chevauchement rend le peering impossible ou nécessite du NAT,
ce qui complique le routage.

> Analogie : deux immeubles ne peuvent pas avoir les mêmes numéros de chambre
> s'ils doivent partager un service de livraison. Il faut des adresses uniques.

### Subnet public et subnet privé

Un subnet est dit **public** lorsqu'il a une route vers une passerelle Internet
et que les ressources peuvent recevoir une adresse publique ou être derrière un
load balancer public.

Un subnet **privé** n'a pas de route directe vers Internet. Il peut sortir via
un NAT Gateway pour les mises à jour, mais il n'accepte pas de connexions
entrantes depuis Internet.

```text
                 Internet
                    |
             Internet Gateway
                    |
          +---------+---------+
          |                   |
   Subnet public       Subnet privé
   10.0.1.0/24          10.0.2.0/24
     Web server           Base de données
          |
       NAT Gateway  ----> Internet pour mises à jour
```

## 3. Route tables

Une route table contient des routes qui décident où envoyer le trafic.

Exemple AWS :

```text
Destination        Target
10.0.0.0/16        local
0.0.0.0/0          igw-123456
```

Exemple de subnet privé :

```text
Destination        Target
10.0.0.0/16        local
0.0.0.0/0          nat-123456
```

Chaque subnet est associé à une route table. Une route table mal associée est
une cause fréquente de panne : la ressource est correcte, mais elle n'a pas la
route attendue.

### Route locale

AWS ajoute automatiquement une route locale pour le VPC. Azure utilise des
routes système pour le VNet. Ces routes permettent aux subnets du même réseau
de communiquer sans passer par Internet.

### Routes plus spécifiques

Le routage choisit la route la plus spécifique. Une route `10.1.0.0/16` est
préférée à `0.0.0.0/0` pour une destination correspondante.

## 4. Passerelles et sortie Internet

### Internet Gateway

Dans AWS, l'Internet Gateway est attachée au VPC. Elle permet aux ressources
qui ont une adresse publique de communiquer avec Internet. Elle ne fait pas de
NAT à elle seule.

### NAT Gateway

Le NAT Gateway permet aux instances d'un subnet privé d'initier des connexions
vers Internet sans être accessibles depuis Internet. Il est placé dans un
subnet public et possède une adresse publique.

Il faut prévoir un NAT par AZ pour éviter qu'une panne d'AZ coupe la sortie des
subnets privés. Le NAT a un coût et peut devenir un point de contention.

### Azure

Dans Azure, une VM avec une IP publique peut sortir par Internet. Un NAT
Gateway permet une sortie contrôlée pour un subnet. Un Azure Firewall ou un
pare-feu tiers peut aussi assurer la sortie et l'inspection.

## 5. Security Groups et NACL

### AWS Security Groups

Un Security Group est un pare-feu virtuel attaché à une ressource, par exemple
une instance, une ENI ou un load balancer.

Caractéristiques :

- **stateful** : le retour d'une connexion autorisée est automatiquement permis ;
- règles allow uniquement ;
- deny implicite ;
- peut référencer un autre Security Group ;
- s'applique au niveau de la ressource.

Exemple :

```text
Inbound
TCP 443 depuis 0.0.0.0/0
TCP 22 depuis 10.0.0.0/8

Outbound
Tous les trafics autorisés
```

Un Security Group ne remplace pas une ACL réseau. Il est plus proche du pare-feu
de l'instance.

### AWS Network ACL

Une NACL s'applique au niveau du subnet. Elle est **stateless** : il faut
autoriser explicitement le retour. Elle possède des règles allow et deny et est
évaluée dans l'ordre des numéros.

| Élément | Security Group | NACL |
|---|---|---|
| Niveau | Ressource | Subnet |
| État | Stateful | Stateless |
| Règles | Allow uniquement | Allow et deny |
| Retour | Automatique | À autoriser |
| Ordre | Toutes les règles | Numéro de règle |

### Azure Network Security Group

Un NSG Azure filtre le trafic entrant et sortant. Il peut être attaché à une
interface réseau ou à un subnet. Les règles ont une priorité, un sens, un
protocole, des plages source/destination et une action allow/deny.

Les NSG sont stateful pour les flux autorisés. Les règles par défaut autorisent
la communication interne du VNet et le load balancer, et bloquent le reste.

### Bonnes pratiques de filtrage

- autoriser uniquement les ports nécessaires ;
- limiter les sources à des CIDR ou des Security Groups ;
- ne pas exposer SSH ou RDP à Internet sans bastion ;
- séparer les subnets par rôle ;
- utiliser un pare-feu central pour l'inspection ;
- journaliser les flux ;
- revoir les règles régulièrement.

## 6. VPC Peering et VNet Peering

Le peering relie deux VPC/VNet pour permettre la communication par adresses
privées. Il ne passe pas par Internet.

### AWS VPC Peering

Une connexion peering est créée entre deux VPC. Elle doit être acceptée par
l'autre côté. Les route tables des deux VPC doivent avoir une route vers le CIDR
du pair.

Le peering AWS est **non transitif** : si A est peeré avec B et B avec C, A ne
peut pas joindre C via B. Pour une topologie hub-and-spoke, on utilise souvent
un Transit Gateway.

### Azure VNet Peering

Le peering Azure fonctionne de la même façon : les deux VNets doivent avoir des
CIDR non chevauchants et des règles de routage adaptées. Le peering est également
non transitif par défaut.

### Hub-and-spoke

```text
              Hub VPC/VNet
          +------------------+
          | Firewall / TGW   |
          +---+----------+---+
              |          |
         Spoke A      Spoke B
```

Le hub centralise la sécurité, le VPN, le DNS et le routage. Les spokes
contiennent les applications. Le Transit Gateway AWS ou Azure Virtual WAN peut
simplifier le routage entre de nombreux spokes.

### Vérifier le peering

- les CIDR ne se chevauchent pas ;
- les routes existent des deux côtés ;
- les Security Groups/NSG autorisent le trafic ;
- le peering est dans l'état actif ;
- le DNS privé est correctement configuré ;
- les tables de routage ne renvoient pas le trafic vers Internet.

## 7. VPN site-to-site

Un VPN site-to-site relie un réseau on-premise à un VPC/VNet via un tunnel
IPsec sur Internet. Il est utile pour un site distant, un datacenter ou un
partenaire.

```text
Site on-premise                     Cloud
+-------------+                 +-------------+
| Routeur VPN |==== IPsec ======| VPN Gateway |
+-------------+                 +------+------+
       |                               |
   LAN 10.10.0.0/16              VPC 10.20.0.0/16
```

### IPsec et IKE

IPsec fournit le chiffrement et l'authentification. IKE négocie les paramètres
et les clés. Les deux extrémités doivent partager :

- les propositions de chiffrement et de hash ;
- le groupe Diffie-Hellman ;
- la durée de vie des clés ;
- les réseaux locaux et distants ;
- la méthode d'authentification ;
- éventuellement le ASN et les adresses BGP.

Une différence de paramètres est une cause classique de tunnel qui ne monte
pas.

### AWS Site-to-Site VPN

AWS fournit une passerelle VPN et des tunnels redondants. On peut utiliser du
routage statique ou BGP. Le client VPN (accès nomade) est différent du
site-to-site.

### Azure VPN Gateway

Azure VPN Gateway propose plusieurs SKU et modes actif-actif ou actif-passif.
Le site-to-site utilise une passerelle locale pour représenter le site distant.

### Haute disponibilité du VPN

Un seul tunnel est un point de panne. On prévoit :

- deux tunnels vers deux équipements ;
- deux fournisseurs Internet ;
- BGP pour la convergence ;
- un monitoring des tunnels ;
- des routes de secours.

## 8. Connexions privées et hybrides

### AWS Direct Connect

Direct Connect est une liaison privée entre un site et AWS, hors Internet. Elle
peut être couplée à un VPN pour le chiffrement ou servir de chemin principal.

### Azure ExpressRoute

ExpressRoute est l'équivalent Azure : une connexion privée via un partenaire.
Elle n'est pas chiffrée par défaut, il faut ajouter IPsec ou une autre couche
de protection si nécessaire.

### SD-WAN

Un SD-WAN peut router le trafic vers Internet, un VPN ou un lien privé selon
la politique applicative. Il faut vérifier la cohérence avec les routes cloud
et les préfixes annoncés.

## 9. DNS, load balancing et endpoints privés

### DNS privé

Les noms internes doivent résoudre vers des adresses privées. AWS Route 53
Private Hosted Zones et Azure Private DNS permettent de gérer ces zones.

Un nom public qui résout vers une adresse privée peut être une erreur de
configuration ou une fuite d'information.

### Load balancer

Un load balancer public expose un service à Internet ; un load balancer interne
le réserve au VPC/VNet. Il faut vérifier :

- les subnets du load balancer ;
- les Security Groups/NSG ;
- les health checks ;
- les certificats TLS ;
- le DNS.

### Endpoints privés

Les endpoints privés permettent d'accéder à un service managé sans passer par
Internet. Ils simplifient la sécurité et évitent l'exposition publique.

## 10. Exemples de configuration

### AWS CLI

Créer un VPC et un subnet :

```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-xxxx --cidr-block 10.0.1.0/24
```

Décrire les route tables :

```bash
aws ec2 describe-route-tables --filters Name=vpc-id,Values=vpc-xxxx
```

### Azure CLI

Créer un VNet et un subnet :

```bash
az network vnet create \
  --resource-group rg-network \
  --name vnet-prod \
  --address-prefixes 10.0.0.0/16 \
  --subnet-name subnet-web \
  --subnet-prefixes 10.0.1.0/24
```

Lister les NSG :

```bash
az network nsg list --resource-group rg-network --output table
```

## 11. Dépannage cloud

### Une ressource ne sort pas vers Internet

- subnet associé à la bonne route table ?
- route `0.0.0.0/0` vers Internet Gateway ou NAT ?
- adresse publique ou NAT configuré ?
- Security Group sortant ?
- NACL de retour ?
- DNS fonctionnel ?

### Un peering ne fonctionne pas

- CIDR chevauchants ?
- peering accepté des deux côtés ?
- routes vers le CIDR pair des deux côtés ?
- Security Groups/NSG autorisent le flux ?
- le peering est non transitif : une route vers un third VPC ne suffit pas.

### Un VPN ne monte pas

- paramètres IKE/IPsec différents ?
- réseaux locaux/distants incorrects ?
- clé prépartagée ou certificat ?
- UDP 500/4500 filtré ?
- route vers le subnet distant ?
- BGP ASN ou voisin absent ?

### Le trafic passe mais le DNS échoue

- serveur DNS privé associé au VPC/VNet ?
- zone privée liée ?
- résolution depuis le bon subnet ?
- règles de pare-feu sur le port 53 ?

### Le trafic est asymétrique

Le retour peut passer par un autre chemin que l'aller. Les pare-feu stateful
peuvent alors bloquer. Vérifier les routes, le NAT, les load balancers et les
tunnels.

## 12. Concevoir un VPC multi-AZ

Un VPC de production ne se limite pas à un subnet public et un subnet privé. On
prévoit souvent trois niveaux :

| Niveau | Exemple | Accès Internet |
|---|---|---|
| Public | Load balancer, bastion | Entrant et sortant contrôlés |
| Applicatif privé | Serveurs d'application | Sortant via NAT |
| Données privé | Bases de données | Aucun accès Internet |

Exemple de plan d'adressage :

```text
VPC 10.20.0.0/16

AZ A
10.20.1.0/24   public-a
10.20.11.0/24  app-a
10.20.21.0/24  data-a

AZ B
10.20.2.0/24   public-b
10.20.12.0/24  app-b
10.20.22.0/24  data-b
```

Chaque AZ possède son NAT Gateway et ses subnets. Si l'AZ A tombe, les
ressources de l'AZ B continuent de fonctionner. Les route tables des subnets
publics pointent vers l'Internet Gateway ; celles des subnets applicatifs
pointent vers le NAT de leur AZ.

### Haute disponibilité

- Load balancer réparti sur au moins deux AZ ;
- instances ou services répartis sur plusieurs AZ ;
- base de données avec réplique ou service multi-AZ ;
- NAT Gateway par AZ ;
- VPN avec deux tunnels ;
- DNS avec health checks.

Un VPC multi-AZ ne garantit pas la haute disponibilité si l'application n'est
pas conçue pour tourner sur plusieurs instances. Le réseau prépare le terrain,
il ne remplace pas la redondance applicative.

### Sous-réseaux et adresses réservées

AWS réserve quelques adresses dans chaque subnet : l'adresse réseau, la
passerelle, la DNS et une adresse de broadcast. Azure réserve également
certaines adresses. Il faut en tenir compte dans le dimensionnement.

Un subnet trop petit peut empêcher l'ajout d'instances ou de pods. Prévoir de
la marge et documenter les plages.

## 13. Exemples de filtrage et de flux

### Security Group AWS

Une application web derrière un load balancer :

```text
Security Group du load balancer
Inbound  TCP 443 depuis 0.0.0.0/0
Outbound TCP 8080 vers le Security Group applicatif

Security Group applicatif
Inbound  TCP 8080 depuis le Security Group du load balancer
Outbound TCP 3306 vers le Security Group de base de données

Security Group base de données
Inbound  TCP 3306 depuis le Security Group applicatif
Outbound aucun trafic Internet
```

Le Security Group référence un autre Security Group plutôt qu'un CIDR. Les
règles restent valables si les adresses changent.

### NACL et ports éphémères

Une NACL AWS est stateless. Si un client initie une connexion vers le port 443,
le retour du serveur arrive vers un port source éphémère du client. Il faut
autoriser ce retour dans la NACL.

```text
NACL entrante
Autoriser TCP 443 depuis Internet
Autoriser TCP 1024-65535 depuis Internet pour le retour

NACL sortante
Autoriser TCP 1024-65535 vers Internet
Autoriser TCP 443 vers Internet si nécessaire
```

Une erreur fréquente consiste à autoriser l'aller mais pas le retour. Le
Security Group, lui, gère automatiquement le retour d'un flux autorisé.

### NSG Azure

Les règles NSG sont évaluées par priorité croissante. Une règle avec une
priorité plus petite est évaluée avant. Il faut laisser de l'espace entre les
numéros pour insérer des règles plus tard.

```text
Priorité 100 : autoriser 443 depuis Internet vers le subnet web
Priorité 200 : autoriser 22 depuis le subnet bastion
Priorité 4096 : règle par défaut
```

Les règles par défaut d'Azure autorisent la communication dans le VNet et le
trafic du load balancer. Il ne faut pas les considérer comme une politique de
sécurité complète.

### Flux asymétrique

Un pare-feu stateful qui voit l'aller mais pas le retour bloque la connexion.
Les causes fréquentes sont :

- deux routes par défaut différentes ;
- NAT sur un seul chemin ;
- load balancer qui change le chemin de retour ;
- VPN avec route plus spécifique d'un côté ;
- peering non transitif.

Il faut toujours vérifier le chemin aller **et** le chemin retour.

## 14. VPN et BGP en pratique

### Choisir le routage

Un VPN site-to-site peut utiliser :

- du routage statique : simple, mais peu de convergence ;
- du routage dynamique BGP : plus flexible, idéal pour plusieurs réseaux.

Avec BGP, le routeur on-premise et la passerelle cloud échangent des préfixes.
Il faut définir les ASN, les voisins et les réseaux annoncés.

### Exemple de paramètres

```text
IKE version        : IKEv2
Chiffrement IKE    : AES-256
Hash IKE           : SHA-256
DH group           : 14
IPsec chiffrement  : AES-256
IPsec hash         : SHA-256
PFS                : group 14
Réseau local       : 10.10.0.0/16
Réseau distant     : 10.20.0.0/16
BGP local AS       : 65010
BGP cloud AS       : 64512
```

Ces valeurs doivent être identiques ou compatibles des deux côtés. Un seul
paramètre différent peut empêcher la phase IKE ou IPsec.

### Exemple strongSwan simplifié

```text
conn cloud
    left=203.0.113.10
    leftsubnet=10.10.0.0/16
    right=198.51.100.20
    rightsubnet=10.20.0.0/16
    authby=secret
    ike=aes256-sha256-modp2048
    esp=aes256-sha256-modp2048
    keyexchange=ikev2
    auto=start
```

Le mot de passe ou le certificat ne doit pas être stocké en clair dans un
dépôt public. On utilise un coffre-fort de secrets.

### Redondance VPN

Une passerelle cloud peut proposer deux adresses IP publiques et deux tunnels.
Le routeur on-premise doit avoir deux tunnels configurés, idéalement sur deux
fournisseurs différents. BGP permet de préférer un chemin et de basculer si
l'autre tombe.

### Vérifications

```bash
ipsec statusall
ipsec trafficstatus
ping -c 3 10.20.1.10
traceroute 10.20.1.10
```

Côté cloud, on vérifie l'état des tunnels, les routes apprises, les logs de la
passerelle et les Security Groups. Un tunnel `UP` ne signifie pas que le
routage est correct : il faut aussi une route et un filtre autorisant le flux.

## 15. Sécurité et bonnes pratiques

- segmenter en subnets public, applicatif et données ;
- appliquer le moindre privilège dans les Security Groups/NSG ;
- utiliser des endpoints privés pour les services managés ;
- chiffrer les VPN et les données ;
- journaliser les flux et les changements ;
- utiliser un bastion ou un accès juste-à-temps pour l'administration ;
- éviter les CIDR qui se chevauchent ;
- documenter les routes et les tables ;
- tester la reprise après panne d'une AZ ;
- surveiller les coûts de NAT, de transfert et de VPN.

## 16. À retenir

- Un VPC/VNet est un réseau privé découpé en subnets.
- Un subnet public a une route vers Internet ; un subnet privé sort par NAT.
- Les route tables décident du chemin ; une mauvaise association casse tout.
- Security Groups et NSG sont stateful ; les NACL AWS sont stateless.
- Le peering est privé mais non transitif.
- Un VPN site-to-site repose sur IPsec/IKE et doit être redondé.
- Direct Connect/ExpressRoute sont des liens privés opérateur.
- Le DNS privé et les endpoints privés font partie de l'architecture.
- Le dépannage cloud commence par la route, le filtre, le DNS et le chemin de
  retour.

Le cloud ne supprime pas les fondamentaux réseau : il les expose dans une API.
Savoir lire une route table, un Security Group et un tunnel VPN reste
indispensable pour concevoir et dépanner.
