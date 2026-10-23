# Azure VNet (Virtual Network) - Expert

**Niveau :** Expert

**Prérequis :** Azure VNet Intermédiaire (`azure-vnet-intermediaire`), maîtrise du routage BGP, des architectures hybrides (VPN IPsec / ExpressRoute), et des concepts d'inspection de trafic (Firewall / NVA).

Ce module traite du design et du déploiement d'architectures réseau complexes dans Microsoft Azure pour les environnements d'entreprise. Nous y abordons l'architecture **Hub-and-Spoke**, l'intégration d'**Azure Virtual WAN (vWAN)**, le routage dynamique via **Azure Route Server (BGP)**, l'inspection centralisée avec **Azure Firewall** et l'architecture **Private DNS Resolver**.

## 1. Topologie Entreprise : Hub-and-Spoke Architecture

L'architecture **Hub-and-Spoke** est la recommandation standard de Microsoft pour structurer les réseaux d'entreprise dans le cloud.

```
                  ┌─────────────────────────────────────────┐
                  │         Site On-Premises / Datacenter   │
                  └────────────────────┬────────────────────┘
                                       │ VPN IPsec / ExpressRoute
                                       ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ VNET HUB (10.0.0.0/16)                                                      │
 │                                                                             │
 │   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
 │   │ GatewaySubnet             │         │ AzureFirewallSubnet           │   │
 │   │ (VPN / ExpressRoute GW)   │────────>│ (Azure Firewall / NVA Central)│   │
 │   └───────────────────────────┘         └───────────────┬───────────────┘   │
 └──────────────────────┬──────────────────────────────────┼───────────────────┘
                        │ (VNet Peering)                   │ (VNet Peering)
       ┌────────────────┴──────────────┐   ┌───────────────┴───────────────┐
       │                               │   │                               │
       ▼                               ▼   ▼                               ▼
┌──────────────┐               ┌──────────────┐               ┌──────────────┐
│ VNET SPOKE A │               │ VNET SPOKE B │               │ VNET SPOKE C │
│ (Prod App)   │               │ (Dev Workload│               │ (Shared Svc) │
│ 10.1.0.0/16  │               │ 10.2.0.0/16  │               │ 10.3.0.0/16  │
└──────────────┘               └──────────────┘               └──────────────┘

```

### Composants clés :

* **VNet Hub :** Réseau central hébergeant les services partagés (Azure Firewall, ExpressRoute / VPN Gateways, DNS Private Resolver, Azure Route Server).

* **VNets Spoke :** Réseaux d'application isolés appairés au Hub (via VNet Peering). Les Spokes ne sont pas appairés directement entre eux.

* **Gateway Transit & Allow Forwarded Traffic :** 
  * `allowGatewayTransit` sur le Hub : permet aux Spokes d'utiliser la passerelle du Hub.
  * `useRemoteGateways` sur le Spoke : active l'utilisation de la passerelle distante.
  * `allowForwardedTraffic` : indispensable pour accepter le trafic transféré qui n'a pas été généré localement.

## 2. Azure Route Server et Integration BGP

**Azure Route Server** simplifie le routage dynamique entre vos équipements virtuels réseau (NVA - *Network Virtual Appliances*) et le réseau virtuel Azure (VNet), en éliminant le besoin d'UDRs statiques complexes.

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │ AZURE VNET                                                                  │
 │                                                                             │
 │   ┌────────────────────────┐  iBGP Session  ┌───────────────────────────┐   │
 │   │   Azure Route Server   │<==============>│  NVA (SD-WAN / Fortinet /  │   │
 │   │  (RouteServerSubnet)   │                │   Palo Alto / Quagga)     │   │
 │   └───────────┬────────────┘                └─────────────┬─────────────┘   │
 │               │                                           │                 │
 │               └──────── Injecte les routes BGP ───────────┘                 │
 │                         directement dans le VNet                            │
 └─────────────────────────────────────────────────────────────────────────────┘

```

### Fonctionnement :

* Azure Route Server échange dynamiquement des routes via **BGP (Border Gateway Protocol)** avec les NVAs.

* Les routes apprises de la NVA sont immédiatement injectées dans la table de routage du VNet (remplaçant la gestion manuelle des UDRs).

* Prise en charge d'**ECMP (Equal-Cost Multi-Path)** pour la répartition de charge et la haute disponibilité des NVAs.

## 3. Azure Virtual WAN (vWAN)

**Azure Virtual WAN** est un service d'architecture réseau globale géré par Microsoft permettant d'interconnecter des milliers de sites, d'utilisateurs distants et de VNets à grande échelle.

```
   [ Site On-Premises ] ──VPN──┐                                ┌──VPN── [ Site Branch 2 ]
                               ▼                                ▼
                      ┌──────────────────────────────────────────────────┐
                      │            AZURE VIRTUAL WAN HUB                 │
                      │   (Hub managé : VPN + ER + NVA + Firewall)     │
                      └────────────────────────┬─────────────────────────┘
                                               │ (Hub Peering)
                                               ▼
                                      ┌─────────────────┐
                                      │   VNet Spoke    │
                                      └─────────────────┘

```

### Hub Standard vWAN vs Hub Custom :

* **Managé par Microsoft :** Le Virtual Hub est provisionné et géré automatiquement dans une région.

* **Routage global automatisé :** Transit direct inter-régional et inter-VNet natif.

* **Azure Firewall Intégré (Secured Virtual Hub) :** Permet une politique de sécurité centralisée (*Azure Firewall Manager*).

## 4. Architecture DNS Privé à l'échelle (Azure Private Resolver)

Pour résoudre les noms DNS privés (*Private Endpoints*) depuis un réseau local (On-Premises) ou entre plusieurs VNets sans maintenir de serveurs IaaS DNS (bind/Windows Server), Azure propose **Azure Private DNS Resolver**.

```
  [ Client On-Premises ]
            │ (Requête DNS vers IP Inbound Endpoint)
            ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ AZURE VNET HUB                                                            │
  │                                                                           │
  │   ┌──────────────────────────────────────────────────────────────────┐   │
  │   │                AZURE PRIVATE DNS RESOLVER                        │   │
  │   │                                                                  │   │
  │   │   ┌─────────────────────────┐      ┌─────────────────────────┐   │   │
  │   │   │  Inbound Endpoint       │      │  Outbound Endpoint      │   │   │
  │   │   │  (Reçoit requêtes DNS)  │      │  (Redirige requêtes)    │   │   │
  │   │   └────────────┬────────────┘      └────────────┬────────────┘   │   │
  │   └────────────────┼────────────────────────────────┼────────────────┘   │
  │                    │                                │                    │
  │                    ▼                                ▼                    │
  │    ┌──────────────────────────────┐  ┌──────────────────────────────┐    │
  │    │ Private DNS Zone (.database) │  │ Ruleset (DNS On-Premises)    │    │
  │    └──────────────────────────────┘  └──────────────────────────────┘    │
  └───────────────────────────────────────────────────────────────────────────┘

```

* **Inbound Endpoint :** Reçoit les requêtes DNS en provenance du réseau On-premises ou d'autres VNets.

* **Outbound Endpoint :** Redirige les requêtes des VNets Azure vers vos serveurs DNS d'entreprise locaux via un **DNS Forwarding Ruleset**.

## 5. Configuration Exemple : Peering Hub-and-Spoke avec Transit de Passerelle (Bicep)

```bicep
// --- Fichier : hub-spoke-peering.bicep ---
param hubVnetName string = 'vnet-hub-westeurope'
param spokeVnetName string = 'vnet-spoke-app'
param resourceGroupHub string = 'rg-network-hub'

// 1. Peering du HUB vers le SPOKE (Allow Gateway Transit)
resource hubToSpokePeering 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-09-01' = {
  name: '${hubVnetName}/peering-to-${spokeVnetName}'
  properties: {
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: true
    useRemoteGateways: false
    remoteVirtualNetwork: {
      id: resourceId('Microsoft.Network/virtualNetworks', spokeVnetName)
    }
  }
}

// 2. Peering du SPOKE vers le HUB (Use Remote Gateways)
resource spokeToHubPeering 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-09-01' = {
  name: '${spokeVnetName}/peering-to-${hubVnetName}'
  properties: {
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: false
    useRemoteGateways: true
    remoteVirtualNetwork: {
      id: resourceId('Microsoft.Network/virtualNetworks', hubVnetName)
    }
  }
}
```

## Commandes de Vérification et Troubleshooting Expert

| Commande / Outil | Description / Objectif |
| ----- | ----- |
| `az network watcher test-ip-flow` | Valide si un paquet IP est autorisé ou bloqué par un NSG ou une règle de routage. |
| `az network watcher next-hop` | Identifie le Next Hop exact emprunté par un paquet depuis une VM spécifique. |
| `az network routeserver peering list` | Vérifie l'état d'appairage BGP avec Azure Route Server. |
| `az network vnet gateway list-bgp-peer-status` | Affiche l'état des voisins BGP sur une passerelle VPN / ExpressRoute. |

## Points à retenir

* **Hub-and-Spoke :** Architecture de référence pour isoler les charges de travail (Spokes) tout en centralisant l'inspection et la connectivité hybride (Hub).

* **Azure Route Server :** Simplifie l'intégration de NVAs tiers (Fortinet, Palo Alto, Cisco) en automatisant le routage BGP dynamique sans UDR statiques.

* **Virtual WAN (vWAN) :** Préférable pour les déploiements multi-régionaux ou d'envergure avec des centaines de sites distants.

* **Private DNS Resolver :** Remplace avantageusement les VMs DNS IaaS pour la résolution hybride privée (Azure <-> On-Premises).