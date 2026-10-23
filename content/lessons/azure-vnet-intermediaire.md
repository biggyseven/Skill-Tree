# Azure VNet (Virtual Network) - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** Azure VNet Débutant (`azure-vnet-debutant`), compréhension de l'adressage CIDR, du fonctionnement des sous-réseaux et des Network Security Groups (NSG).

Ce module approfondit les mécanismes d'architecture réseau avancés dans Microsoft Azure. Vous y découvrirez l'interconnexion de réseaux via **VNet Peering**, la personnalisation du routage avec les **User Defined Routes (UDR)**, ainsi que la sécurisation des accès aux services PaaS Azure via **Service Endpoints**, **Private Endpoints** et l'utilisation de **NAT Gateway**.

## 1. VNet Peering (Interconnexion de réseaux)

Le **VNet Peering** permet de relier deux Virtual Networks de manière transparente au sein du réseau d'infrastructure haute performance de Microsoft (sans passer par Internet ni nécessiter de passerelle VPN).

```
   ┌──────────────────────────┐                      ┌──────────────────────────┐
   │    VNet-A (10.1.0.0/16)  │                      │    VNet-B (10.2.0.0/16)  │
   │                          │    VNet Peering      │                          │
   │ ┌──────────────────────┐ │ <==================> │ ┌──────────────────────┐ │
   │ │ Subnet-A (10.1.1.0/24)│ │  Faible latence /    │ │ Subnet-B (10.2.1.0/24)│ │
   │ └──────────────────────┘ │  Bande passante max  │ └──────────────────────┘ │
   └──────────────────────────┘                      └──────────────────────────┘

```

### Types de Peering :

1. **VNet Peering régional :** Interconnecte des VNets situés dans la même région Azure.
2. **Global VNet Peering :** Interconnecte des VNets situés dans des régions Azure différentes.

### Caractéristiques et contraintes importantes :

* **Non-transitivité :** Si le VNet A est appairé au VNet B, et le VNet B au VNet C, le VNet A ne peut **pas** communiquer directement avec le VNet C.
* **Plages IP non chevauchantes :** Les espaces d'adressage IP des deux VNets ne doivent avoir aucun chevauchement.
* **Transitivité de passerelle (Gateway Transit) :** Permet à un VNet d'utiliser la passerelle VPN/ExpressRoute d'un autre VNet (architecture Hub-and-Spoke).

## 2. User Defined Routes (UDR) et Route Tables

Par défaut, Azure gère automatiquement le routage via des *System Routes*. Pour forcer le trafic à travers un équipement spécifique (ex: Network Virtual Appliance / NVA, Azure Firewall), on utilise des **User Defined Routes (UDR)** regroupées dans une **Route Table**.

```
    [ Subnet Frontend ]
           │
           │ (Trafic à destination de 0.0.0.0/0)
           ▼
    ┌──────────────┐   UDR Next-Hop : 10.0.1.4
    │ Route Table  │ ─────────────────────────┐
    └──────────────┘                          │
                                              ▼
                                   ┌────────────────────┐
                                   │  Network Virtual   │
                                   │  Appliance (NVA)   │
                                   │     10.0.1.4       │
                                   └──────────┬─────────┘
                                              │ (Trafic Inspecté)
                                              ▼
                                         [ Internet ]

```

### Types de Next-Hop disponibles :

* **Virtual Appliance :** Redirige le trafic vers une adresse IP privée (NVA, Azure Firewall).
* **Virtual Network Gateway :** Redirige vers une passerelle VPN ou ExpressRoute.
* **Internet :** Redirige le trafic directement vers la sortie Internet d'Azure.
* **None :** Supprime (drop) les paquets envoyés à cette destination (blackholing).

## 3. Communication sécurisée PaaS : Service Endpoints vs Private Endpoints

Pour connecter des ressources privées du VNet à des services PaaS Azure (Azure Storage, Azure SQL, Event Hubs), deux approches principales existent :

```
                        ┌────────────────────────────────────────────────────────┐
                        │                      AZURE PAAS                        │
                        │                 (ex: Azure Storage)                    │
                        └───────────▲────────────────────────▲───────────────────┘
                                    │                        │
               Public IP Service    │                        │ IP Privée VNet
             (Traffic reste backbone)                        │ (Carte réseau NIC)
                                    │                        │
                         ┌──────────┴──────────┐  ┌──────────┴──────────┐
                         │  Service Endpoint   │  │   Private Endpoint   │
                         └──────────▲──────────┘  └──────────▲──────────┘
                                    │                        │
   ┌────────────────────────────────┼────────────────────────┼──────────────────┐
   │ AZURE VNET                     │                        │                  │
   │                   ┌────────────┴───────────┐┌───────────┴──────────┐       │
   │                   │    Subnet App Server   ││    Subnet DB Private │       │
   │                   └────────────────────────┘└──────────────────────┘       │
   └────────────────────────────────────────────────────────────────────────────┘

```

### Comparison : Service Endpoint vs Private Endpoint

| Critère | Service Endpoint | Private Endpoint (Private Link) |
| ----- | ----- | ----- |
| **Adresse IP cible** | Adresse IP publique du service PaaS | **Adresse IP privée** locale au sous-réseau |
| **Emplacement de l'accès** | Accessible depuis le sous-réseau uniquement | Accessible depuis le sous-réseau, VNet Peerings et VPN/ExpressRoute |
| **Sécurité DNS** | Utilise le DNS public Azure | Nécessite une **Private DNS Zone** |
| **Protection contre l'exfiltration** | Limitée (ou via Service Endpoint Policies) | Élevée (unicité du lien vers l'instance PaaS spécifique) |

## 4. NAT Gateway (Azure Virtual Network NAT)

Le service **Azure NAT Gateway** fournit une connectivité Internet sortante (*Outbound*) hautement sécurisée et totalement évolutive pour un ou plusieurs sous-réseaux.

### Avantages :

* **IP Publique Sortante Fixe :** Garantit une ou plusieurs adresses IP publiques statiques dédiées pour tous les flux sortants.
* **Résilience SNAT :** Évite les problèmes d'épuisement de ports SNAT (*SNAT Port Exhaustion*) rencontrés avec le routage sortant par défaut ou les Load Balancers.
* **Sécurité :** Empêche tout trafic entrant non sollicité (*Inbound*) d'atteindre les ressources (seul le trafic de réponse aux requêtes sortantes est autorisé).

## 5. Exemples de Configuration (Azure CLI)

### 1. Configuration d'un VNet Peering bidirectionnel

```bash
# 1. Peering de VNet-A vers VNet-B
az network vnet peering create \
  --name Peer-VNetA-to-VNetB \
  --resource-group rg-network-demo \
  --vnet-name vnet-a \
  --remote-vnet vnet-b \
  --allow-vnet-access

# 2. Peering retour de VNet-B vers VNet-A (nécessaire pour autoriser le flux bidirectionnel)
az network vnet peering create \
  --name Peer-VNetB-to-VNetA \
  --resource-group rg-network-demo \
  --vnet-name vnet-b \
  --remote-vnet vnet-a \
  --allow-vnet-access
```

### 2. Création et association d'une UDR (Route Table)

```bash
# 1. Création de la Route Table
az network route-table create \
  --resource-group rg-network-demo \
  --name rt-spoke-to-firewall

# 2. Ajout d'une route par défaut (0.0.0.0/0) vers un Firewall/NVA (ex: 10.0.1.4)
az network route-table route create \
  --resource-group rg-network-demo \
  --route-table-name rt-spoke-to-firewall \
  --name DefaultRouteToFirewall \
  --address-prefix 0.0.0.0/0 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.1.4

# 3. Association de la Route Table à un sous-réseau
az network vnet subnet update \
  --resource-group rg-network-demo \
  --vnet-name vnet-spoke \
  --name snet-workload \
  --route-table rt-spoke-to-firewall
```

## Commandes de Vérification Essentielles

| Commande (Azure CLI) | Description / Objectif |
| ----- | ----- |
| `az network vnet peering list --vnet-name <vnet> -g <rg> -o table` | Vérifie le statut du peering (`Connected`, `Initiated`, etc.). |
| `az network route-table route list --route-table-name <rt> -g <rg>` | Affiche la liste des routes définies dans une Route Table. |
| `az network nic show-effective-route-table --name <nic-name> -g <rg>` | **Crucial :** Affiche la table de routage finale effective appliquée à une VM (UDR + System Routes). |
| `az network private-endpoint list -g <rg> -o table` | Liste les Private Endpoints déployés et leur état de connexion. |

## Points à retenir

* **VNet Peering :** Connectivité privée haute performance entre VNets, mais **non transitive** par défaut.
* **Effective Routes :** Toujours vérifier les *effective routes* d'une interface réseau pour diagnostiquer les problèmes de routage complexes (UDR vs System Routes).
* **Private Endpoint :** Option recommandée pour sécuriser l'accès aux services PaaS Azure via une **IP privée** locale.
* **NAT Gateway :** Solution recommandée pour gérer la sortie Internet sécurisée avec des IP publiques dédiées sans risque d'épuisement SNAT.