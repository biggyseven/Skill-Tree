## node_id: aws-vpc-expert

title: AWS VPC (Virtual Private Cloud) - Expert

# AWS VPC (Virtual Private Cloud) - Expert

**Niveau :** Expert

**Prérequis :** AWS VPC Intermédiaire (`aws-vpc-intermediaire`), maîtrise du routage dynamique BGP, des architectures multi-comptes AWS Organizations, et des principes d'inspection du trafic de niveau 7.

Ce module aborde la conception et l'implémentation d'architectures réseau complexes dans AWS pour des environnements d'entreprise. Vous y étudierez les topologies **Landing Zone Multi-Comptes**, l'intégration d'**AWS Direct Connect**, l'inspection centralisée du trafic avec **AWS Network Firewall** et **Gateway Load Balancer (GWLB)**, ainsi que la résolution hybride avec **Route 53 Resolver**.

## 1. Topologie Entreprise Multi-Comptes (Hub-and-Spoke / Landing Zone)

Dans un environnement d'entreprise multi-comptes (*AWS Organizations*), la connectivité et la sécurité réseau sont centralisées dans des comptes dédiés (*Network/Inspection Account*).

```
                  ┌─────────────────────────────────────────┐
                  │         Site On-Premises / Datacenter   │
                  └────┬────────────────────┘
                                       │ Direct Connect / VPN BGP
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ AWS TRANSIT GATEWAY CENTRAL (Compte Network)                                │
 └───────┬─────────────────────────────┬─────────────────────────────┬─────────┘
         │                             │                             │
         ▼                             ▼                             ▼
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│ VPC Inspection          │   │ VPC Spoke Workload A    │   │ VPC Spoke Workload B    │
│ (Compte Security)       │   │ (Compte Application A)  │   │ (Compte Application B)  │
│ ┌─────────────────────┐ │   │ ┌─────────────────────┐ │   │ ┌─────────────────────┐ │
│ │ Network Firewall    │ │   │ │ App / Microservices │ │   │ │ Database Cluster    │ │
│ └─────────────────────┘ │   │ └─────────────────────┘ │   │ └─────────────────────┘ │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘


```

### Principes architecturaux :

* **Separation of Concerns :** Le compte *Network* gère la connectivité d'entrée/sortie et les passerelles ; le compte *Security* gère l'inspection du trafic.

* **Resource Access Manager (RAM) :** AWS Transit Gateway et AWS Subnets (via *VPC Sharing*) sont partagés aux comptes applicatifs à travers AWS RAM.

* **Transit Gateway Route Tables :** Utilisation de tables de routage TGW distinctes (*Spoke TGW Route Table*, *Inspection TGW Route Table*) pour forcer tout le trafic inter-VPC ou Internet à travers le VPC d'inspection.

## 2. Connectivité Hybride Avancée : AWS Direct Connect & Transit VIF

**AWS Direct Connect (DX)** fournit une connexion réseau dédiée à faible latence et haut débit entre votre datacenter sur site et AWS.

```
 [ On-Premises Router ]
          │
          │ Fibre Dédiée (1Gbps / 10Gbps / 100Gbps)
          ▼
 ┌────────────────────────┐
 │ Direct Connect Location│
 └────────┬───────────────┘
          │ (Transit Virtual Interface - Transit VIF)
          ▼
 ┌────────────────────────┐  Interconnexion BGP  ┌────────────────────────┐
 │ Direct Connect Gateway │<====================>│  AWS Transit Gateway   │
 └────────┬───────────────┘                      └───────────┬────────────┘
                                                             │
                                                   ┌─────────┴─────────┐
                                                   ▼                   ▼
                                             [ VPC Spoke 1 ]     [ VPC Spoke 2 ]


```

### Composants clés :

* **Transit VIF (Virtual Interface) :** Interface virtuelle BGP nécessaire pour connecter Direct Connect à une **Direct Connect Gateway (DXGW)** rattachée à une Transit Gateway.

* **Direct Connect Gateway (DXGW) :** Composant mondial permettant de relier une connexion Direct Connect à des VPCs ou TGWs dans n'importe quelle région AWS (hors Chine).

* **Chiffrement avec MACsec / IPsec sur Direct Connect :** Pour chiffrer le trafic sur la fibre dédiée, on utilise soit **MACsec** (niveau 2, haut débit), soit un tunnel **IPsec sur Direct Connect** (niveau 3).

## 3. Inspection du Trafic Centralisée : Gateway Load Balancer & Network Firewall

Pour analyser le trafic applicatif (L4-L7) en profondeur, deux approches majeures sont déployées :

```
                        ┌─────────────────────────────────────────┐
                        │      Trafic Entrant / Inter-Spoke       │
                        └────┬────────────────────┘
                                             │
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │       GWLB Endpoint (VPC Endpoint)      │
                        └────┬────────────────────┘
                                             │ Encapsulation GENEVE (Port UDP 6081)
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │        Gateway Load Balancer (GWLB)     │
                        └────┬────────────────────┘
                                             │
                                 ┌───────────┴───────────┐
                                 ▼                       ▼
                      ┌─────────────────────┐ ┌─────────────────────┐
                      │ NVA Appliance 1     │ │ NVA Appliance 2     │
                      │ (Palo Alto/Fortinet)│ │ (Palo Alto/Fortinet)│
                      └─────────────────────┘ └─────────────────────┘


```

### Comparaison : AWS Network Firewall vs Gateway Load Balancer (GWLB)

| Feature | AWS Network Firewall | Gateway Load Balancer (GWLB) | 
| ----- | ----- | ----- | 
| **Nature du service** | Service d'inspection managé (basé sur Suricata) | Équilibreur de charge L3/L4 transparent pour NVAs tiers | 
| **Protocole d'encapsulation** | Transparent / Natif VPC | Encapsulation **GENEVE** (UDP 6081) préservant l'IP source/destination | 
| **Cas d'usage principal** | Filtrage d'URL, détection d'intrusions (IDS/IPS) managée | Intégration transparente de firewalls virtuels tiers (Palo Alto, Check Point, Fortinet) | 
| **Haute Disponibilité** | Auto-managé par AWS par AZ | Répartition de charge automatique sur plusieurs instances NVA IaaS | 

## 4. Résolution DNS Hybride : Route 53 Resolver (Inbound/Outbound Endpoints)

Pour résoudre de manière bidirectionnelle les noms de domaines privés entre AWS (`*.amazonaws.com`, zones privées Route 53) et le datacenter On-Premises (`*.corp.internal`), on utilise **Route 53 Resolver Endpoints**.

```
  [ Server On-Premises ]
            │ (Requête pour *.aws.internal)
            ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ VPC NETWORK CENTRAL                                                       │
  │                                                                           │
  │   ┌───────────────────────────┐        ┌──────────────────────────────┐   │
  │   │ Inbound Resolver Endpoint │        │ Outbound Resolver Endpoint   │   │
  │   │ (IPs privées dans Subnets)│        │ (Règles de transfert/Rules)  │   │
  │   └─────────────┬─────────────┘        └──────────────┬───────────────┘   │
  │                 │                                     │                   │
  └─────────────────┼─────────────────────────────────────┼───────────────────┘
                    │                                     │
                    ▼                                     ▼
     ┌──────────────────────────────┐     ┌──────────────────────────────┐
     │ Route 53 Private Hosted Zone │     │ DNS Server On-Premises       │
     │ (*.aws.internal)             │     │ (*.corp.internal)            │
     └──────────────────────────────┘     └──────────────────────────────┘


```

* **Inbound Endpoint :** Permet aux serveurs DNS On-Premises de transférer les requêtes pour des domaines AWS vers des IPs privées spécifiques dans votre VPC.

* **Outbound Endpoint :** Transfère les requêtes DNS générées dans AWS pour vos domaines On-Premises (`*.corp.internal`) vers vos serveurs DNS locaux via des **Resolver Rules**.

## 5. Configuration Exemple : Attachement Transit Gateway & VPC Peering TGW (IaC Terraform)

```hcl
# --- main.tf ---

# 1. Création de la Transit Gateway
resource "aws_ec2_transit_gateway" "central_tgw" {
  description                     = "Central Enterprise TGW"
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"
  dns_support                      = "enable"

  tags = {
    Name = "tgw-central-prod"
  }
}

# 2. Attachement du VPC Spoke à la Transit Gateway
resource "aws_ec2_transit_gateway_vpc_attachment" "spoke_a_attachment" {
  transit_gateway_id = aws_ec2_transit_gateway.central_tgw.id
  vpc_id             = "vpc-0spoke123456789a"
  subnet_ids         = ["subnet-0az1a11111", "subnet-0az2b22222"]

  tags = {
    Name = "tgw-attach-spoke-a"
  }
}

# 3. Route statique dans la table de routage TGW vers le VPC Spoke A
resource "aws_ec2_transit_gateway_route" "route_to_spoke_a" {
  destination_cidr_block         = "10.1.0.0/16"
  transit_gateway_attachment_id = aws_ec2_transit_gateway_vpc_attachment.spoke_a_attachment.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway.central_tgw.propagation_default_route_table_id
}
```

## Commandes de Diagnostic et Diagnostic Avancé

| Outil / Commande AWS CLI | Description / Objectif |
| ----- | ----- |
| `aws ec2 get-transit-gateway-route-table-propagations` | Affiche les propagations de routes dynamiques actives sur une table de routage TGW. |
| `aws networkmanager get-vpc-attachment-shows` | Inspecte l'état d'intégration dans AWS Network Manager (Global Network). |
| **VPC Reachability Analyzer** | Outil d'analyse statique de configuration pour tester la connectivité entre deux ressources (ex: EC2 à GWLB Endpoint) sans envoyer de paquets. |
| **AWS Network Access Analyzer** | Analyse de conformité et de sécurité pour identifier les accès réseau non intentionnels au niveau infrastructure. |

## Points à retenir

* **Landing Zone Network :** Isolation stricte des comptes de connectivité (*Network*) et d'inspection (*Security*) via AWS RAM et Transit Gateway.

* **Transit VIF :** Requis pour interconnecter un AWS Direct Connect avec une Transit Gateway (via Direct Connect Gateway).

* **GWLB & GENEVE :** Le Gateway Load Balancer préserve l'intégrité des paquets réseau (IP source/destination d'origine) grâce au protocole GENEVE lors de la redirection vers des NVAs.

* **Route 53 Resolver :** Solution standard pour orchestrer la résolution DNS bidirectionnelle entre AWS et le datacenter d'entreprise.