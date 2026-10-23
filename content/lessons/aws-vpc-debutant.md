## node_id: aws-vpc-debutant

title: AWS VPC (Virtual Private Cloud) - Débutant

# AWS VPC (Virtual Private Cloud) - Débutant

**Niveau :** Débutant

**Prérequis :** Notions de base sur le Cloud Computing, compréhension de l'adressage IP (IPv4) et du masquage de sous-réseau (notation CIDR).

Ce module introduit les concepts fondamentaux du réseau virtuel dans AWS via le service **Amazon Virtual Private Cloud (VPC)**. Vous y apprendrez à structurer un réseau isolé, créer des sous-réseaux publics et privés, et gérer la sécurité d'accès au niveau des instances et des sous-réseaux.

## 1. Qu'est-ce qu'un AWS VPC ?

Un **VPC (Virtual Private Cloud)** est un réseau virtuel logiquement isolé dédié à votre compte AWS. Il vous donne un contrôle total sur votre environnement réseau virtuel (adressage IP, sous-réseaux, tables de routage et passerelles réseau).

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ REGION AWS (ex: eu-west-3 / Paris)                                          │
 │                                                                             │
 │ ┌─────────────────────────────────────────────────────────────────────────┐ │
 │ │ AWS VPC (10.0.0.0/16)                                                   │ │
 │ │                                                                         │ │
 │ │  ┌───────────────────────────┐         ┌─────────────────────────────┐  │ │
 │ │  │ Subnet Public (AZ-A)      │         │ Subnet Privé (AZ-B)         │  │ │
 │ │  │ 10.0.1.0/24                │         │ 10.0.2.0/24                 │  │ │
 │ │  └───────────────────────────┘         └─────────────────────────────┘  │ │
 │ └─────────────────────────────────────────────────────────────────────────┘ │
 └─────────────────────────────────────────────────────────────────────────────┘


```

### Concept de base :

* **Régional :** Un VPC est confiné à une seule région AWS, mais s’étend sur toutes les zones de disponibilité (*Availability Zones* ou AZs) de cette région.

* **Blocs CIDR IPv4 :** Lors de la création, vous attribuez une plage IP principale au VPC (ex: `10.0.0.0/16`, de `10.0.0.0` à `10.0.255.255`).

## 2. Sous-réseaux (Subnets) et Zones de Disponibilité

Un sous-réseau est une plage d'adresses IP dans votre VPC. **Chaque sous-réseau réside impérativement dans une seule Zone de Disponibilité (AZ)**.

```
                  ┌─────────────────────────────────────────┐
                  │            VPC (10.0.0.0/16)            │
                  └────┬───────────────────────────────┬────┘
                       │                               │
                       ▼                               ▼
        ┌─────────────────────────────┐ ┌─────────────────────────────┐
        │ Zone d'Disponibilité A (AZ-A)│ │ Zone de Disponibilité B (AZ-B)│
        │ ┌─────────────────────────┐ │ │ ┌─────────────────────────┐ │
        │ │ Subnet-1 (10.0.1.0/24)  │ │ │ │ Subnet-2 (10.0.2.0/24)  │ │
        │ └─────────────────────────┘ │ │ └─────────────────────────┘ │
        └─────────────────────────────┘ └─────────────────────────────┘


```

### Adresses IP réservées par AWS :

Dans chaque sous-réseau, AWS réserve systématiquement **5 adresses IP** (non attribuables à vos instances) :

* `.0` : Adresse réseau.

* `.1` : Réservée par AWS pour le routeur du VPC.

* `.2` : Réservée par AWS pour la résolution DNS (`AmazonProvidedDNS`).

* `.3` : Réservée par AWS pour un usage futur.

* `.255` : Adresse de diffusion (Broadcast réseau).

*Exemple : Un sous-réseau `/24` compte $256 - 5 = 251$ adresses IP utilisables.*

## 3. Connectivité Internet : Internet Gateway & NAT Gateway

Pour gérer le trafic entrant et sortant vers Internet, AWS propose deux passerelles distinctes :

```
                                [ INTERNET ]
                                     ▲
                                     │
                    ┌────────────────┴────────────────┐
                    │      Internet Gateway (IGW)     │
                    └────────────────▲────────────────┘
                                     │
             ┌───────────────────────┴───────────────────────┐
             │                                               │
             │ (Accès Direct)                                │ (Trafic Sortant Uniquement)
             ▼                                               ▼
  ┌──────────────────────┐                       ┌──────────────────────┐
  │ Subnet Public        │                       │ Subnet Privé         │
  │                      │                       │                      │
  │ ┌──────────────────┐ │                       │ ┌──────────────────┐ │
  │ │ Instance EC2     │ │                       │ │ NAT Gateway      │ │
  │ │ (IP Publique)    │ │                       │ │ (dans Subnet Pub)│ │
  │ └──────────────────┘ │                       │ └─────────▲────────┘ │
  └──────────────────────┘                       │           │          │
                                                 │ ┌─────────┴────────┐ │
                                                 │ │ Instance EC2     │ │
                                                 │ │ (IP Privée)      │ │
                                                 │ └──────────────────┘ │
                                                 └──────────────────────┘


```

### Comparaison : Subnet Public vs Subnet Privé

| Composant | Sous-réseau Public (Public Subnet) | Sous-réseau Privé (Private Subnet) | 
| ----- | ----- | ----- | 
| **Internet Gateway (IGW)** | Associé via la table de routage (`0.0.0.0/0` -> IGW) | Pas de route directe vers IGW | 
| **Accès Internet entrant** | Autorisé (si l'instance a une IP Publique) | **Interdit** | 
| **Accès Internet sortant** | Direct via IGW | Via **NAT Gateway** ou **NAT Instance** | 
| **Cas d'usage** | Load Balancers, Bastion Hosts, Serveurs Web publics | Bases de données, Microservices backend, API internes | 

## 4. Sécurité réseau : Security Groups vs Network ACLs (NACL)

La sécurité dans AWS VPC repose sur un modèle de sécurité en profondeur combinant deux mécanismes complémentaires.

```
     [ Trafic Entrant ]
             │
             ▼
    ┌─────────────────┐
    │  Network ACL    │  <--- Niveau Sous-réseau (Stateless)
    └────────┬────────┘
             │ (Si autorisé)
             ▼
    ┌─────────────────┐
    │ Security Group  │  <--- Niveau Instance / Carte réseau (Stateful)
    └────────┬────────┘
             │ (Si autorisé)
             ▼
    ┌─────────────────┐
    │  Instance EC2   │
    └─────────────────┘


```

### Tableau comparatif Security Group vs Network ACL

| Critère | Security Group (SG) | Network ACL (NACL) | 
| ----- | ----- | ----- | 
| **Niveau d'action** | Carte réseau d'instance (ENI) | Sous-réseau (Subnet) | 
| **État (Stateful / Stateless)** | **Stateful** (Le trafic de retour est autorisé automatiquement) | **Stateless** (Le trafic de retour doit être explicite) | 
| **Règles de refus (DENY)** | Ne permet que des règles d'autorisation (**ALLOW**) | Permet d'écrire des règles d'autorisation (**ALLOW**) et de refus (**DENY**) | 
| **Ordre d'évaluation** | Toutes les règles sont évaluées ensemble | Évalué dans l'ordre croissant des numéros de règle | 

## 5. Exemples de déploiement (AWS CLI)

### 1. Création d'un VPC et d'un sous-réseau public

```bash
# 1. Création du VPC (10.0.0.0/16)
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-first-vpc}]'

# 2. Création du sous-réseau (10.0.1.0/24)
aws ec2 create-subnet \
  --vpc-id vpc-0123456789abcdef0 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone eu-west-3a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-a}]'

# 3. Création et attachement de l'Internet Gateway (IGW)
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]'

aws ec2 attach-internet-gateway \
  --vpc-id vpc-0123456789abcdef0 \
  --internet-gateway-id igw-0123456789abcdef0

```

### 2. Configuration de la table de routage publique

```bash
# 1. Création d'une table de routage personnalisée
aws ec2 create-route-table \
  --vpc-id vpc-0123456789abcdef0 \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-rt}]'

# 2. Ajout de la route vers Internet (0.0.0.0/0) via l'IGW
aws ec2 create-route \
  --route-table-id rtb-0123456789abcdef0 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-0123456789abcdef0

# 3. Association de la table de routage au sous-réseau public
aws ec2 associate-route-table \
  --subnet-id subnet-0123456789abcdef0 \
  --route-table-id rtb-0123456789abcdef0

```

## Commandes de Vérification

| Commande (AWS CLI) | Description / Objectif | 
| ----- | ----- | 
| `aws ec2 describe-vpcs --vpc-ids <vpc-id>` | Affiche le statut et la plage CIDR d'un VPC. | 
| `aws ec2 describe-subnets --filters "Name=vpc-id,Values=<vpc-id>"` | Liste tous les sous-réseaux associés à un VPC. | 
| `aws ec2 describe-route-tables --route-table-ids <rtb-id>` | Inspecte la table de routage et ses associations. | 
| `aws ec2 describe-security-groups --group-ids <sg-id>` | Vérifie les règles entrantes et sortantes d'un Security Group. | 

## Points à retenir

* **Portée du VPC :** Régional (confiné à une région AWS).
* **Portée du sous-réseau :** Limité à une seule Zone de Disponibilité (AZ).
* **Sous-réseau Public :** Possède une route directe vers un Internet Gateway (`0.0.0.0/0 -> igw-xxx`).
* **Security Group (Stateful) :** Filtrage au niveau instance ; si le trafic entrant est autorisé, la réponse sortante est automatiquement permise.