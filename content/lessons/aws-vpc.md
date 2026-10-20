# AWS VPC – Cours intensif pour Administrateur Réseau Senior  
*(niveau CCIE – profondeur technique, 10 000+ caractères)*  

---  

## 1. Introduction & concepts fondamentaux  

| Concept | Description | Analogie réseau traditionnelle |
|---------|-------------|--------------------------------|
| **VPC (Virtual Private Cloud)** | Réseau logique isolé dans le cloud AWS. Vous décidez du CIDR, des sous‑réseaux, du routage, des ACL, etc. | VLAN / VRF |
| **Subnet** | Découpage du VPC en blocs de /16 à /28. Chaque subnet est soit **public** (route vers IGW) soit **private** (pas d’accès direct à Internet). | Sous‑réseau LAN |
| **IGW (Internet Gateway)** | Point d’ancrage pour le trafic IPv4/IPv6 sortant et entrant depuis Internet. | Router Edge |
| **NAT Gateway / NAT Instance** | Permet aux instances privées d’initier du trafic vers Internet tout en restant non routables depuis l’extérieur. | PAT/masquerading |
| **VPC Peering** | Connexion point‑à‑point entre deux VPC (même ou différents comptes). | Lien point‑à‑point L2 |
| **Transit Gateway (TGW)** | Hub centralisé qui interconnecte plusieurs VPC, VPN, Direct Connect. | Routeur core MPLS |
| **VPN Cloud‑on‑Prem** | IPSec tunnel entre votre datacenter et le VPC. | Tunnel GRE/IPSec |
| **Direct Connect (DX)** | Liaison dédiée 1 Gbps‑100 Gbps entre votre site et AWS. | Liaison fibre dédiée |
| **VPC Endpoint** | Interface ou Gateway endpoint qui expose les services AWS (S3, DynamoDB, etc.) sans passer par Internet. | Private link / Service insertion |
| **Flow Logs** | Capture des métadonnées de trafic (IP, port, action) vers CloudWatch ou S3. | NetFlow / sFlow |

> **Note** : Un VPC n’est jamais partagé entre comptes, mais les *Resource Access Manager* (RAM) permettent d’exporter des sous‑réseaux ou des TGW.

---

## 2. Architecture d’un VPC typique  

```
+-----------------------------------------------------------+
|                         VPC (10.0.0.0/16)                |
|  +-------------------+   +-------------------+            |
|  | Public Subnet A   |   | Private Subnet A  |            |
|  | 10.0.1.0/24       |   | 10.0.2.0/24       |            |
|  |  IGW <---> NAT GW |   |  ENI (EC2)        |            |
|  +-------------------+   +-------------------+            |
|  +-------------------+   +-------------------+            |
|  | Public Subnet B   |   | Private Subnet B  |            |
|  | 10.0.3.0/24       |   | 10.0.4.0/24       |            |
|  |  IGW <---> NAT GW |   |  ENI (RDS)        |            |
|  +-------------------+   +-------------------+            |
|            |                     |                       |
|            +-------- TGW --------+-----------------------+
|                     |                                 |
|                VPN/Direct Connect                     |
+-----------------------------------------------------------+
```

* **Route Table (RT)** : chaque subnet possède une RT.  
  * Public RT → `0.0.0.0/0` → IGW.  
  * Private RT → `0.0.0.0/0` → NAT GW ou TGW.  

* **Security Group (SG)** : état‑ful (stateful). Autorise le trafic entrant **et** le trafic de réponse sortant automatiquement.  

* **Network ACL (NACL)** : état‑less (stateless). Chaque règle doit être symétrique (inbound + outbound).  

---

## 3. Conception du CIDR & sous‑netting  

| Taille VPC | CIDR recommandé | Nombre max de subnets |
|------------|----------------|-----------------------|
| Petit (dev) | 10.0.0.0/20    | 16                    |
| Moyen (prod) | 10.0.0.0/16    | 256                   |
| Grand (multi‑region) | 10.0.0.0/12 | 4096 |

### 3.1. Calcul d’un sous‑réseau  

- **Objectif** : 3 AZ, chaque AZ avec 2 subnets (public / private).  
- **Choix** : VPC `/16` → 65536 IP.  
- **Allocation** : `/24` par subnet → 256 IP (254 utilisables).  

```
AZ-a : 10.0.0.0/24 (pub)  10.0.1.0/24 (priv)
AZ-b : 10.0.2.0/24 (pub)  10.0.3.0/24 (priv)
AZ-c : 10.0.4.0/24 (pub)  10.0.5.0/24 (priv)
```

> **Rappel** : AWS réserve 5 adresses par subnet (ex. .0, .1, .2, .3, .255).  

---

## 4. Tables de routage détaillées  

### 4.1. Exemple de table publique (RT‑pub)  

| Destination | Target          | Description |
|-------------|----------------|-------------|
| 10.0.0.0/16 | local          | VPC intra‑subnet |
| 0.0.0.0/0   | igw‑xxxxxxxx   | Internet (IPv4) |
| ::/0        | igw‑xxxxxxxx   | Internet (IPv6) |

### 4.2. Exemple de table privée (RT‑priv)  

| Destination | Target               | Description |
|-------------|----------------------|-------------|
| 10.0.0.0/16 | local                | VPC intra‑subnet |
| 0.0.0.0/0   | nat‑gw‑xxxxxxxx      | Sortie Internet via NAT |
| 172.31.0.0/16 | vpc‑peering‑xxxxxx | Accès à VPC peer (si appliqué) |
| 192.168.0.0/16 | tgw‑xxxxxx        | Transit Gateway |

---

## 5. Security Groups vs Network ACLs  

| Feature | Security Group (SG) | Network ACL (NACL) |
|---------|----------------------|--------------------|
| **Stateful** | Oui (réponse autorisée) | Non (stateless) |
| **Scope** | Instance/ENI | Subnet |
| **Règles max** | 60 (ingress) + 60 (egress) par SG | 20 inbound + 20 outbound (défaut) |
| **Évaluation** | OR logique (any rule matches) | Numérotée, première correspondance s’applique |
| **Logging** | Flow Logs (via ENI) | N/A (pas de logs natifs) |
| **Utilisation typique** | Filtrage applicatif (ports, protocoles) | Filtrage de couche réseau, blocage d’IP publiques |  

### 5.1. Exemple de SG pour serveur web  

```text
Inbound
  - TCP 80  0.0.0.0/0   (HTTP)
  - TCP 443 0.0.0.0/0   (HTTPS)
  - TCP 22  203.0.113.12/32 (SSH admin)

Outbound
  - All traffic 0.0.0.0/0 (default allow)
```

### 5.2. Exemple de NACL pour subnet privé  

| Rule # | Type | Protocol | Port Range | Source/Destination | Allow/Deny |
|--------|------|----------|------------|--------------------|------------|
| 100    | SSH  | TCP      | 22         | 203.0.113.0/24     | ALLOW      |
| 110    | HTTP | TCP      | 80-443     | 0.0.0.0/0          | ALLOW      |
| 120    | *    | *        | *          | 0.0.0.0/0          | DENY       |

---

## 6. NAT – Gateway vs Instance  

| Caractéristique | NAT Gateway | NAT Instance |
|-----------------|-------------|--------------|
| **Performance** | 5 Gbps (scalable) | Dépend de l’instance EC2 |
| **HA** | Multi‑AZ (auto‑failover) | Doit être géré via scripts/Auto Scaling |
| **Coût** | $0.045/heure + $0.045/GB | EC2 + ENI + EIP (potentiellement moins cher pour faible trafic) |
| **Gestion** | Aucun patch, pas d’OS | OS à maintenir, sécurité (iptables) |
| **IP source** | Adresse IP Elastic du NAT GW | IP de l’instance (EIP) |

### 6.1. Création d’une NAT Gateway (CLI)  

```
aws ec2 create-nat-gateway \
    --subnet-id subnet-0a1b2c3d \
    --allocation-id eipalloc-12345678 \
    --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=NGW-PubA}]'
```

### 6.2. Configuration d’une instance NAT (Linux)  

```bash
# 1. Activer le forwarding IP
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p

# 2. Configurer iptables (MASQUERADE)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o eth1 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT

# 3. Vérifier
iptables -t nat -L -n -v
```

---

## 7. VPC Peering – limitations & bonnes pratiques  

| Limite | Valeur |
|--------|--------|
| CIDR overlapping | **Interdit** (les deux VPC ne doivent pas se chevaucher) |
| Transitivité | **Non transitif** (A↔B, B↔C → A ne voit pas C) |
| Route propagation | **Manuelle** (ajouter les routes dans chaque RT) |
| Services supportés | EC2, RDS, Lambda (via ENI), etc. |
| Bande passante | Limité par le trafic EC2 (pas de quota dédié) |

### 7.1. Exemple de création de peering (CLI)  

```
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-11111111 \
    --peer-vpc-id vpc-22222222 \
    --peer-owner-id 123456789012 \
    --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=Peer-Prod}]'
```

Puis accepter depuis le compte peer :

```
aws ec2 accept-vpc-peering-connection \
    --vpc-peering-connection-id pcx-0a1b2c3d4e5f6g7h8
```

---

## 8. Transit Gateway (TGW) – hub central  

### 8.1. Architecture simplifiée  

```
+-------------------+          +-------------------+
|   VPC A (10.0.0)  |          |   VPC B (10.1.0)  |
|  +-------------+  |          |  +-------------+  |
|  |  TGW attach |---+----------+--|  TGW attach |  |
|  +-------------+  |          |  +-------------+  |
+-------------------+          +-------------------+
          |                               |
          +----------- TGW ---------------+
                      |
          +-----------+-----------+
          |  VPN / Direct Connect |
          +-----------------------+
```

* **Route propagation** : TGW peut propager automatiquement les routes VPN/DX vers les tables d’attache.  
* **Multicast** (en preview) : support du trafic multicast via TGW.  

### 8.2. Commandes Terraform (extrait)  

```hcl
resource "aws_ec2_transit_gateway" "tgw" {
  description = "TGW central"
  amazon_side_asn = 64512
  tags = {
    Name = "TGW-Prod"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "attach_a" {
  transit_gateway_id = aws_ec2_transit_gateway.tgw.id
  vpc_id             = aws_vpc.prod_a.id
  subnet_ids         = [aws_subnet.prod_a_pub.id]
}
```

---

## 9. VPC Endpoints – PrivateLink & Gateway  

| Type | Service | Mode | Prix |
|------|---------|------|------|
| **Interface Endpoint** | S3, DynamoDB, API Gateway, Service Marketplace, vos propres services via **AWS PrivateLink** | ENI + Elastic IP | $0.01/heure + $0.005/GB |
| **Gateway Endpoint** | S3, DynamoDB | Route table entry | Gratuit (pas de frais de data) |
| **Interface Endpoint (Cross‑Account)** | Votre SaaS interne | VPC‑endpoint‑service + acceptance | Variable |

### 9.1. Création d’un Interface Endpoint (CLI)  

```
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-0a1b2c3d \
    --service-name com.amazonaws.us-east-1.s3 \
    --subnet-ids subnet-11111111 subnet-22222222 \
    --security-group-ids sg-0123456789abcdef0 \
    --private-dns-enabled
```

---

## 10. IPv6 dans le VPC  

| Étape | Action | Commande CLI |
|------|--------|--------------|
| **Activer IPv6** | `associate-vpc-cidr-block` avec `AmazonProvidedIpv6CidrBlock` | `aws ec2 associate-vpc-cidr-block --vpc-id vpc-12345678 --amazon-provided-ipv6-cidr-block` |
| **Attribuer IPv6 à un subnet** | `modify-subnet-attribute` | `aws ec2 modify-subnet-attribute --subnet-id subnet-11111111 --assign-ipv6-address-on-launch` |
| **Route IPv6** | `::/0 → igw‑xxxxxxxx` | `aws ec2 create-route --route-table-id rtb-xxxx --destination-ipv6-cidr-block ::/0 --gateway-id igw-xxxx` |

* **Security Groups** supportent IPv6 nativement (règles séparées).  
* **NACL** possède un champ `IPv6 CIDR`.  

---

## 11. VPC Flow Logs – capture & analyse  

### 11.1. Création d’un Flow Log (CLI)  

```
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-0a1b2c3d \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name vpc-flow-logs \
    --deliver-logs-permission-arn arn:aws:iam::123456789012:role/FlowLogRole
```

### 11.2. Analyse avec **awslogs** (Linux)  

```bash
# Installer awslogs (pip)
pip install awslogs

# Filtrer les connexions SSH sortantes depuis le subnet privé
awslogs get /aws/vpc/flow-logs \
    --start='-1h' \
    --filter-pattern '{ $.dstport = 22 && $.action = "ACCEPT" }' \
    --region us-east-1
```

---

## 12. Connexion On‑Prem – VPN IPSec & Direct Connect  

### 12.1. Diagramme simplifié  

```
[Datacenter]---IPSec---[VGW]---[VPC]
      |
      +---BGP (ASN 65000) <-> (ASN 64512)
```

### 12.2. Config Cisco ASA (exemple)  

```
crypto ipsec ikev1 transform-set ESP-AES256-SHA esp-aes-256 esp-sha-hmac
crypto ipsec ikev1 transform-set ESP-AES256-SHA mode transport
crypto map outside_map 10 match address vpn-acl
crypto map outside_map 10 set peer <AWS_VGW_PUBLIC_IP>
crypto map outside_map 10 set ikev1 transform-set ESP-AES256-SHA
crypto map outside_map 10 set pfs group14
crypto map outside