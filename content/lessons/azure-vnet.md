# Azure Virtual Network (VNet) & VNet Peering  
**Niveau : Senior Network Administrator / CCIE**  
**Durée estimée : 2 jours intensifs**  

---  

## 1. Introduction à Azure Virtual Network  

| Concept | Description | Équivalent on‑prem |
|---------|-------------|-------------------|
| **VNet** | Conteneur logique d’adressage IP, sous‑réseaux, tables de routage, NSG, etc. | VLAN / VRF |
| **Subnet** | Découpage d’un VNet en blocs CIDR. | Sub‑net VLAN |
| **Network Security Group (NSG)** | ACL d’état (inbound/outbound) appliquées aux NIC ou aux sous‑réseaux. | ACL / Zone de sécurité |
| **Route Table (UDR)** | Table de routage définie par l’utilisateur (User‑Defined Routes). | Route static / Policy |
| **Azure DNS** | Service DNS interne (et option Azure DNS public). | DNS interne d’entreprise |
| **Azure Firewall / Azure DDoS Protection** | Service de filtrage d’état et de protection contre les attaques DDoS. | Pare‑feu périmètre, DDoS appliance |

> **Note** : Un VNet est *isolé* par défaut. Aucun trafic n’est autorisé entre deux VNets tant qu’un lien explicite (peering, VPN, ExpressRoute) n’est créé.

---

## 2. Architecture de base d’un VNet  

```
+---------------------------------------------------+
|                     Azure Region                 |
|                                                   |
|   +-----------------+   +-----------------------+ |
|   |   VNet A        |   |   VNet B              | |
|   | 10.0.0.0/16     |   | 10.1.0.0/16           | |
|   |  +-----------+  |   |  +-----------------+  | |
|   |  | Subnet A1 |  |   |  | Subnet B1       |  | |
|   |  | 10.0.1.0/24|  |   |  | 10.1.1.0/24     |  | |
|   |  +-----------+  |   |  +-----------------+  | |
|   +-----------------+   +-----------------------+ |
|                                                   |
+---------------------------------------------------+
```

### 2.1. Modèles de topologie courants  

| Topologie | Description | Avantages | Inconvénients |
|-----------|-------------|-----------|---------------|
| **Hub‑Spoke** | Un VNet hub (ex. Azure Firewall, VPN GW) centralise la connectivité vers plusieurs VNets spokes. | Centralisation sécurité, simplification de la gestion des routes. | Point unique de défaillance (mitigé avec zone‑redundant). |
| **Mesh** | Tous les VNets sont peered entre eux (full‑mesh). | Latence minimale, pas de saut supplémentaire. | Complexité O(N²) de gestion, limites de peering (max 500 peers/VNet). |
| **Star (Transit)** | Un VNet transit (Azure Virtual WAN ou Azure Firewall) assure le routage entre spokes. | Évolutivité, contrôle granulaire. | Nécessite configuration de route‑propagation et de UDR. |

---

## 3. VNet Peering : Principes fondamentaux  

### 3.1. Types de peering  

| Type | Portée | Latence | Bande passante | Facturation |
|------|--------|---------|----------------|-------------|
| **Regional VNet Peering** | VNets dans la même région Azure. | < 1 ms | Jusqu’à 10 Gbps (limite du SKU). | Data‑out (GB) + $0.01 / GB inbound (selon région). |
| **Global VNet Peering** | VNets dans des régions différentes. | 2‑30 ms (varie) | Jusqu’à 10 Gbps (limite du SKU). | Data‑out + inter‑region data‑transfer (tarif plus élevé). |

### 3.2. Caractéristiques clés  

| Caractéristique | Valeur par défaut | Configurable |
|-----------------|-------------------|--------------|
| **Transitivité** | Non (peering est **non‑transitif**). | Nécessite hub‑spoke ou transit VNet. |
| **Propagation des routes** | Propagation des routes du VNet local vers le peer. | Peut être désactivée via `allowForwardedTraffic`. |
| **Accès aux services Azure** | Accès aux services (Azure Storage, SQL) via **Microsoft backbone**. | `allowGatewayTransit`, `useRemoteGateways`. |
| **Isolation du trafic** | Trafic reste dans le backbone Microsoft, jamais Internet. | N/A |
| **Sécurité** | NSG et UDR s’appliquent aux flux intra‑VNet. | N/A |

### 3.3. Limitations techniques  

| Limite | Valeur | Impact |
|--------|--------|--------|
| **Nombre maximal de peers/VNet** | 500 (Standard) / 100 (Basic) | Planification de la topologie. |
| **CIDR overlapping** | Interdite – les plages IP ne doivent pas se chevaucher. | Re‑design d’adressage. |
| **Propagation du GW** | Un VNet ne peut avoir **qu’un seul** GW actif (VPN/ExpressRoute). | Utiliser `allowGatewayTransit` + hub‑spoke. |
| **Peering entre différentes subscriptions** | Autorisé, mais nécessite **Rôles RBAC** adéquats. | Gestion des permissions. |
| **Peering avec Azure Private Link** | Autorisé, mais le trafic Private Endpoint reste privé. | Connaître le chemin de flux. |

---

## 4. Planification d’adressage IP  

### 4.1. Schéma recommandé (RFC 1918)  

| Découpage | CIDR | Utilisation |
|-----------|------|-------------|
| **VNet Hub** | 10.0.0.0/16 | Azure Firewall, GW, services partagés. |
| **Spoke 1** | 10.1.0.0/16 | Application tier 1. |
| **Spoke 2** | 10.2.0.0/16 | Application tier 2. |
| **On‑prem** | 192.168.0.0/16 | Réseau d’entreprise. |
| **Azure VPN GW** | 172.16.0.0/24 (dans chaque VNet) | IP du GW local. |

> **Astuce** : Réservez un bloc `/20` pour chaque VNet afin de laisser de la place aux sous‑réseaux futurs.

### 4.2. Exemple de sous‑réseaux  

| VNet | Subnet | CIDR | Usage |
|------|--------|------|-------|
| Hub | `AzureFirewallSubnet` | 10.0.0.0/24 | Azure Firewall |
| Hub | `GatewaySubnet` | 10.0.1.0/24 | VPN/ExpressRoute GW |
| Hub | `AppGatewaySubnet` | 10.0.2.0/24 | Application Gateway |
| Spoke‑1 | `WebSubnet` | 10.1.1.0/24 | Serveurs Web |
| Spoke‑1 | `AppSubnet` | 10.1.2.0/24 | Serveurs d’application |
| Spoke‑2 | `DBSubnet` | 10.2.1.0/24 | Base de données |

---

## 5. Création d’un VNet & Peering – Azure CLI & PowerShell  

### 5.1. Prérequis  

```bash
# Azure CLI version >= 2.30
az login
az account set --subscription <SUBSCRIPTION_ID>
```

### 5.2. Création des VNets  

```bash
# VNet Hub
az network vnet create \
  --resource-group RG-Prod \
  --name VNet-Hub \
  --address-prefix 10.0.0.0/16 \
  --subnet-name AzureFirewallSubnet \
  --subnet-prefix 10.0.0.0/24

# VNet Spoke1
az network vnet create \
  --resource-group RG-Prod \
  --name VNet-Spoke1 \
  --address-prefix 10.1.0.0/16 \
  --subnet-name WebSubnet \
  --subnet-prefix 10.1.1.0/24

# VNet Spoke2
az network vnet create \
  --resource-group RG-Prod \
  --name VNet-Spoke2 \
  --address-prefix 10.2.0.0/16 \
  --subnet-name DBSubnet \
  --subnet-prefix 10.2.1.0/24
```

### 5.3. Création du peering (bidirectionnel)  

```bash
# Hub <-> Spoke1
az network vnet peering create \
  --name Hub-to-Spoke1 \
  --resource-group RG-Prod \
  --vnet-name VNet-Hub \
  --remote-vnet VNet-Spoke1 \
  --allow-forwarded-traffic true \
  --allow-gateway-transit true \
  --allow-vnet-access true

az network vnet peering create \
  --name Spoke1-to-Hub \
  --resource-group RG-Prod \
  --vnet-name VNet-Spoke1 \
  --remote-vnet VNet-Hub \
  --use-remote-gateways true \
  --allow-vnet-access true

# Hub <-> Spoke2 (similaire)
az network vnet peering create \
  --name Hub-to-Spoke2 \
  --resource-group RG-Prod \
  --vnet-name VNet-Hub \
  --remote-vnet VNet-Spoke2 \
  --allow-forwarded-traffic true \
  --allow-gateway-transit true \
  --allow-vnet-access true

az network vnet peering create \
  --name Spoke2-to-Hub \
  --resource-group RG-Prod \
  --vnet-name VNet-Spoke2 \
  --remote-vnet VNet-Hub \
  --use-remote-gateways true \
  --allow-vnet-access true
```

### 5.4. Vérification du peering  

```bash
az network vnet peering list \
  --resource-group RG-Prod \
  --vnet-name VNet-Hub \
  -o table
```

---

## 6. Intégration des services Azure (Gateway, Firewall, Private Link)

| Service | Rôle dans le peering | Configuration clé |
|---------|----------------------|-------------------|
| **VPN Gateway** | Point d’entrée on‑prem, partagé via `allowGatewayTransit`. | `GatewaySubnet` obligatoire, SKU VpnGw1+. |
| **ExpressRoute** | Connectivité dédiée, nécessite `allowGatewayTransit` + `useRemoteGateways`. | Circuit ExpressRoute, `Microsoft.ExpressRoute` provider. |
| **Azure Firewall** | Filtrage centralisé, placé dans le hub. | `AzureFirewallSubnet` (must be /24). |
| **Private Endpoint** | Accès privé à PaaS, le trafic passe par le VNet du endpoint. | `Microsoft.Network/privateEndpoints`. |
| **Azure Virtual WAN** | Transit global, remplace le hub‑spoke classique. | `VirtualWAN` + `VirtualHub`. |

---

## 7. Routage & User‑Defined Routes (UDR)

### 7.1. Propagation par défaut  

- **Peering** : les routes du préfixe du VNet local sont automatiquement propagées vers le peer (ex. `10.0.0.0/16` vers Spoke1).  
- **Gateway** : si `allowGatewayTransit` est activé, le VNet hub annonce ses routes GW aux spokes.

### 7.2. Exemple d’UDR pour forcer le trafic vers Azure Firewall  

```bash
# Crée la route table
az network route-table create \
  --resource-group RG-Prod \
  --name RT-Hub-Default \
  --location westeurope

# Ajoute la route vers le firewall (next hop = IP du firewall)
az network route-table route create \
  --resource-group RG-Prod \
  --route-table-name RT-Hub-Default \
  --name Route-To-FW \
  --address-prefix 0.0.0.0/0 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.0.4   # IP du firewall

# Associe la RT au subnet du hub
az network vnet subnet update \
  --vnet-name VNet-Hub \
  --name AzureFirewallSubnet \
  --resource-group RG-Prod \
  --route-table RT-Hub-Default
```

### 7.3. Table de routage finale (exemple)

| Destination | Next Hop | Type | Commentaire |
|-------------|----------|------|-------------|
| 10.0.0.0/16 | **Local** | VNet | VNet Hub (itself) |
| 10.1.0.0/16 | **VirtualNetwork** | Peering | Spoke1 |
| 10.2.0.0/16 | **VirtualNetwork** | Peering | Spoke2 |
| 0.0.0.0/0 | **VirtualAppliance** | Azure Firewall | Filtrage internet |
| 172.16.0.0/12 | **VirtualNetworkGateway** | GW | On‑prem via VPN |

---

## 8. Sécurité – NSG & Azure Firewall  

### 8.1. Exemple d’NSG (WebSubnet)  

| Direction | Priority | Source | Destination | Port/Protocol | Action |
|-----------|----------|--------|-------------|---------------|--------|
| Inbound | 100 | Internet (Any) | `WebSubnet` | TCP 80,443 | Allow |
| Inbound | 200 | `VNet-Spoke1` | `WebSubnet` | TCP 22 | Deny |
| Outbound| 100 | `WebSubnet` | `VNet-Hub` | Any | Allow |
| Outbound| 200 | `WebSubnet` | Internet | Any | Deny (except via FW) |

```bash
az network nsg create \
  --resource-group RG-Prod \
  --name NSG-WebSubnet

az network nsg rule create \
  --resource-group RG-Prod \
  --nsg-name NSG-WebSubnet \
  --name Allow-HTTP-HTTPS \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 80 443 \
  --source-address-prefixes '*'

az network nsg rule create \
  --resource-group RG-Prod \
  --nsg-name NSG-WebSubnet \
  --name Deny-SSH-From-Spoke \
  --priority 200 \
  --direction Inbound \
  --access Deny \
  --protocol Tcp \
  --destination-port-ranges 22 \
  --source-address-prefixes 10.1.0.0/16
```

### 8.2. Azure Firewall Policy (exemple)  

```bash
# Crée la policy
az network firewall policy create \
  --resource-group RG-Prod \
  --name FWPolicy-Prod \
  --location westeurope

# Règle d’autorisation HTTP vers Internet via FW
az network firewall policy rule-collection-group create \
  --resource-group RG-Prod \
  --policy-name FWPolicy-Prod \
  --name RC-Application \
  --priority 100 \
  --action-type Allow \
  --rule-collection-type Application

az network firewall policy rule-collection-group rule create \
  --resource-group RG-Prod \
  --policy-name FWPolicy-Prod \
  --rule-collection-group-name RC-Application \
  --collection-name AppRuleCollection \
  --name Allow-HTTP-HTTPS \
  --protocols Http=80 Https=443 \
  --target-fqdns '*'
```

---

## 9. Surveillance & Diagnostic  

| Outil | Fonction | Commande CLI |
|-------|----------|--------------|
| **Network Watcher – Topology** | Visualise le graphe VNet + peering. | `az network watcher topology show -g RG-Prod -n VNet-Hub` |
| **Network Watcher – Connection Monitor** | Test de connectivité continu (ICMP/TCP). | `az network watcher connection-monitor create ...` |
| **Azure Monitor – Metrics** | `PeeringInBytes`, `PeeringOutBytes`, `PeeringIngressPackets`. | `az monitor metrics list --resource /subscriptions/.../vnetPeering/...` |
| **NSG Flow Logs** | Capture du trafic autorisé/denié. | `az network nsg flow-log create ...` |
| **Azure Firewall Logs** | Log d’application et de réseau. | `az monitor diagnostic-settings create ...` |

### 9.1. Exemple : capture d’un flux NSG  

```bash
az network nsg flow-log create \
  --resource-group RG-Prod \
  --nsg-name NSG-WebSubnet \
  --storage-account mydiagstorage \
  --enabled true \
  --retention