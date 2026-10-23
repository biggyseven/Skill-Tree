## node_id: aws-vpc-intermediaire

title: AWS VPC (Virtual Private Cloud) - Intermédiaire

# AWS VPC (Virtual Private Cloud) - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** AWS VPC Débutant (`aws-vpc-debutant`), maîtrise des notions de sous-réseaux, tables de routage, Internet/NAT Gateway, et Security Groups.

Ce module approfondit l'interconnexion de VPCs et l'accès sécurisé aux services AWS ou tiers sans passer par Internet. Vous y découvrirez le **VPC Peering**, **AWS Transit Gateway**, les **VPC Endpoints (Gateway et Interface / PrivateLink)**, ainsi que la journalisation du trafic avec les **VPC Flow Logs**.

## 1. VPC Peering (Appairage de VPC)

Le **VPC Peering** permet d'interconnecter deux VPCs de manière privée en utilisant l'infrastructure réseau sous-jacente d'AWS.

```
   ┌──────────────────────────┐                      ┌──────────────────────────┐
   │    VPC-A (10.1.0.0/16)   │                      │    VPC-B (10.2.0.0/16)   │
   │                          │     VPC Peering      │                          │
   │ ┌──────────────────────┐ │ <==================> │ ┌──────────────────────┐ │
   │ │ Subnet-A (10.1.1.0/24)│ │  Trafic chiffré sur  │ │ Subnet-B (10.2.1.0/24)│ │
   │ └──────────────────────┘ │  le backbone AWS     │ └──────────────────────┘ │
   └──────────────────────────┘                      └──────────────────────────┘


```

### Caractéristiques essentielles :

* **Non-transitivité :** Si le VPC A est appairé au VPC B, et le VPC B au VPC C, le VPC A ne peut **pas** communiquer avec le VPC C au travers du VPC B.

* **Pas de chevauchement d'IP :** Les blocs CIDR des deux VPCs doivent être strictement disjoints.

* **Support Inter-Région et Inter-Compte :** Fonctionne entre différentes régions AWS (*Inter-Region VPC Peering*) et différents comptes AWS.

* **Mise à jour des tables de routage :** L'établissement du Peering nécessite d'ajouter manuellement une route dans chaque VPC ciblant l'autre VPC via le `peering-connection-id` (`pcx-xxx`).

## 2. Connectivité centralisée : AWS Transit Gateway (TGW)

Lorsque le nombre de VPCs augmente, la gestion du VPC Peering devient complexe (maillage complet $N \times (N-1) / 2$). **AWS Transit Gateway (TGW)** agit comme un routeur cloud régional centralisé.

```
                  ┌─────────────────────────────────────────┐
                  │          AWS Transit Gateway            │
                  │               (tgw-xxx)                 │
                  └────┬──────────────┬──────────────┬──────┘
                       │              │              │
        ┌──────────────┘              │              └──────────────┐
        ▼                             ▼                             ▼
┌──────────────┐               ┌──────────────┐              ┌──────────────┐
│ VPC-A (Prod) │               │ VPC-B (Dev)  │              │ VPC-C (Shared│
│ 10.1.0.0/16  │               │ 10.2.0.0/16  │              │ Services)    │
└──────────────┘               └──────────────┘              └──────────────┘


```

### Avantages de Transit Gateway :

* **Routage transitif :** Permet la communication directe inter-VPC et vers les réseaux On-Premises (VPN / Direct Connect) via un point d'attache central.

* **Tables de routage TGW :** Permet de segmenter le trafic (ex: isoler l'environnement `Dev` de l'environnement `Prod` tout en donnant accès aux `Shared Services` pour les deux).

## 3. Accès privé aux services AWS : VPC Endpoints & PrivateLink

Les **VPC Endpoints** permettent à vos instances privées d'accéder aux services AWS (S3, DynamoDB, SQ, etc.) ou à des services tiers sans attribuer d'IP publique ni passer par une NAT Gateway ou Internet.

```
                         ┌────────────────────────────────────────────────────────┐
                         │                      SERVICES AWS                      │
                         │                   (ex: S3 / DynamoDB)                  │
                         └───────────▲────────────────────────▲───────────────────┘
                                     │                        │
               Gateway Endpoint      │                        │ Interface Endpoint
             (Route Table Target)    │                        │ (IP Privée / ENI)
                                     │                        │
                          ┌──────────┴──────────┐  ┌──────────┴──────────┐
                          │  Gateway Endpoint   │  │ Interface Endpoint  │
                          └──────────▲──────────┘  └──────────▲──────────┘
                                     │                        │
    ┌────────────────────────────────┼────────────────────────┼──────────────────┐
    │ AWS VPC                        │                        │                  │
    │                   ┌────────────┴───────────┐┌───────────┴──────────┐       │
    │                   │    Subnet Privé A      ││    Subnet Privé B    │       │
    │                   └────────────────────────┘└──────────────────────┘       │
    └────────────────────────────────────────────────────────────────────────────┘


```

### Comparaison : Gateway Endpoint vs Interface Endpoint (PrivateLink)

| Critère | Gateway Endpoint | Interface Endpoint (AWS PrivateLink) | 
| ----- | ----- | ----- | 
| **Services supportés** | **Amazon S3** et **Amazon DynamoDB** uniquement | Presque tous les services AWS, services partenaires et vos propres services | 
| **Technologie sous-jacente** | Cible de route dans la Table de Routage (`vpce-xxx`) | Elastic Network Interface (ENI) attribuée dans le sous-réseau avec une IP privée | 
| **Coût** | **Gratuit** | Facturation à l'heure + volume de données transféré | 
| **Accès distant (VPN/Direct Connect)** | Non accessible depuis On-Premises | Accessible directement depuis le réseau On-Premises | 

## 4. Surveillance et Analyse : VPC Flow Logs

**VPC Flow Logs** est une fonctionnalité qui capture les informations sur le trafic IP entrant et sortant des interfaces réseau de votre VPC.

### Destination des logs :

* **Amazon CloudWatch Logs** (Analyse et alertes en temps réel).

* **Amazon S3** (Stockage long terme et analyse décisionnelle via **Amazon Athena**).

* **Amazon Kinesis Data Firehose** (Ingestion de données en continu).

### Structure d'un fichier de log standard :

```
<version> <account-id> <interface-id> <srcaddr> <dstaddr> <srcport> <dstport> <protocol> <packets> <bytes> <start> <end> <action> <log-status>
```

* **REJECT :** Trafic bloqué par un Security Group ou une Network ACL (Indicateur clé pour le diagnostic d'incidents de sécurité).

* **ACCEPT :** Trafic explicitement autorisé.

## 5. Exemples de déploiement (AWS CLI)

### 1. Création d'une connexion VPC Peering

```
# 1. Demande d'appairage depuis VPC-A vers VPC-B
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-0a111111111111111 \
  --peer-vpc-id vpc-0b222222222222222 \
  --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=VPC-A-to-VPC-B}]'

# 2. Acceptation de l'appairage (exécuté par le propriétaire du VPC-B)
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-0123456789abcdef0

# 3. Ajout de la route dans la table de routage du VPC-A
aws ec2 create-route \
  --route-table-id rtb-vpc-a-private \
  --destination-cidr-block 10.2.0.0/16 \
  --vpc-peering-connection-id pcx-0123456789abcdef0

```

### 2. Création d'un Gateway Endpoint pour Amazon S3

```
# Création du Gateway Endpoint S3 et association aux tables de routage privées
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-0a111111111111111 \
  --service-name com.amazonaws.eu-west-3.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids rtb-vpc-a-private1 rtb-vpc-a-private2

```

## Commandes de Vérification Essentielles

| Commande (AWS CLI) | Description / Objectif | 
| ----- | ----- | 
| `aws ec2 describe-vpc-peering-connections` | Affiche l'état des connexions de Peering (`active`, `pending-acceptance`, etc.). | 
| `aws ec2 describe-vpc-endpoints` | Liste les VPC Endpoints configurés et leur statut. | 
| `aws ec2 describe-transit-gateways` | Inspecte l'état d'une instance AWS Transit Gateway. | 
| `aws ec2 describe-flow-logs` | Vérifie la configuration des Flow Logs actifs sur un VPC ou sous-réseau. | 

## Points à retenir

* **VPC Peering :** Idéal pour relier un petit nombre de VPCs, mais **non transitif**.

* **Transit Gateway :** Architecture recommandée à grande échelle pour centraliser le routage multi-VPC et la connectivité hybride.

* **Gateway Endpoint vs Interface Endpoint :** Préférez les Gateway Endpoints pour S3 et DynamoDB (gratuits), et les Interface Endpoints (PrivateLink) pour les autres services ou l'accès distant via VPN/Direct Connect.

* **VPC Flow Logs :** Outil essentiel pour la sécurité et le diagnostic d'interconnexion (action `REJECT` vs `ACCEPT`).