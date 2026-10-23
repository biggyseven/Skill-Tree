# Azure VNet (Virtual Network) - Débutant

**Niveau :** Débutant

**Prérequis :** Notions fondamentales de réseau IP (adressage IPv4, sous-réseaux/CIDR, masque de sous-réseau) et concepts de base du Cloud Computing.

Ce cours présente les concepts essentiels de **Azure Virtual Network (VNet)**. Il aborde la structure d'un VNet, le rôle des sous-réseaux (*subnets*), le filtrage du trafic avec les **Network Security Groups (NSG)**, ainsi que les règles de routage et de connectivité de base dans Microsoft Azure.

---

## 1. Qu'est-ce qu'un Azure Virtual Network (VNet) ?

Un **Virtual Network (VNet)** est la brique fondamentale du réseau privé dans Microsoft Azure. Il permet à plusieurs types de ressources Azure (comme des machines virtuelles) de communiquer de manière sécurisée entre elles, avec Internet et avec des réseaux locaux (*on-premises*).

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                       AZURE VNET (10.0.0.0/16)                  │
   │                                                                 │
   │   ┌──────────────────────────┐     ┌──────────────────────────┐ │
   │   │  Subnet-Frontend         │     │  Subnet-Backend          │ │
   │   │  (10.0.1.0/24)           │     │  (10.0.2.0/24)           │ │
   │   │                          │     │                          │ │
   │   │   [ VM-Web ]             │     │   [ VM-DB ]              │ │
   │   │   10.0.1.4               │     │   10.0.2.4               │ │
   │   └────────────┬─────────────┘     └────────────▲─────────────┘ │
   │                │                                │               │
   │                └──────── Flux Interne ──────────┘               │
   └─────────────────────────────────────────────────────────────────┘
```

### Caractéristiques principales :
* **Isolation et Sécurité :** Chaque VNet est totalement isolé des autres VNets (sauf configuration explicite via VNet Peering ou VPN).
* **Espace d'adressage privé (CIDR) :** Défini par un ou plusieurs blocs d'adresses (ex: `10.0.0.0/16`, `172.16.0.0/12`, `192.168.0.0/16`).
* **Portée régionale :** Un VNet réside au sein d'une seule région Azure (ex: *westeurope*), mais peut couvrir plusieurs zones de disponibilité (*Availability Zones*).

---

## 2. Découpage en Sous-Réseaux (Subnets)

Un VNet doit être découpé en un ou plusieurs sous-réseaux (*subnets*).

### Règle des 5 adresses réservées par Azure :
Dans chaque sous-réseau Azure, **5 adresses IP sont automatiquement réservées** par la plateforme et ne peuvent pas être attribuées aux ressources :
1. $x.x.x.0$ : Adresse de réseau (Network Address).
2. $x.x.x.1$ : Passrelle par défaut (Default Gateway Azure).
3. $x.x.x.2$ et $x.x.x.3$ : Réservées par Azure pour la résolution DNS.
4. $x.x.x.255$ : Adresse de diffusion (Broadcast address - non pris en charge en VNet).

> **Exemple :** Pour un sous-réseau `10.0.1.0/24` (256 adresses IPv4 théoriques), seules **251 adresses** sont disponibles pour vos ressources.

---

## 3. Sécurisation du trafic : Network Security Group (NSG)

Un **Network Security Group (NSG)** contient une liste de règles de sécurité permettant d'autoriser ou de bloquer le trafic entrant (*Inbound*) ou sortant (*Outbound*).

### Fonctionnement des règles NSG :
* Les règles sont évaluées par ordre de **priorité** (un chiffre entre 100 et 4096).
* Plus le numéro est petit, plus la règle a une priorité élevée.
* Dès qu'un flux correspond à une règle, l'évaluation s'arrête.

```
       [ Trafic Entrant ]
               │
               ▼
  ┌───────────────────────────┐
  │  Règle 100 : Allow-HTTP   │  ──> Matches ? ──> (OUI) ──> TRAFIC AUTORISÉ
  └────────────┬──────────────┘
               │ (NON)
               ▼
  ┌───────────────────────────┐
  │  Règle 200 : Allow-SSH    │  ──> Matches ? ──> (NON)
  └────────────┬──────────────┘
               │
               ▼
  ┌───────────────────────────┐
  │  Règle 65500 : DenyAll    │  ──> TRAFIC BLOQUÉ (Règle par défaut)
  └───────────────────────────┘
```

### Association d'un NSG :
Un NSG peut être associé à :
1. Un **Sous-réseau (Subnet)** : s'applique à toutes les ressources du sous-réseau.
2. Une **Interface Réseau (NIC)** : s'applique uniquement à la carte réseau spécifique d'une VM.

---

## 4. Routage de base et System Routes

Azure crée automatiquement une table de routage système pour chaque sous-réseau (*System Routes*).

### Routes système par défaut :
* **Intra-VNet :** Le trafic entre sous-réseaux d'un même VNet est autorisé directement par défaut.
* **Internet :** Le trafic sortant vers Internet est autorisé par défaut via la passerelle Internet Azure.
* **On-premises / Inter-VNet :** Désactivé par défaut (nécessite VNet Peering ou VPN Gateway).

---

## 5. Exemple de Configuration (Azure CLI & Bicep)

### 1. Création via Azure CLI

```bash
# 1. Création d'un groupe de ressources
az group create --name rg-network-demo --location westeurope

# 2. Création du Virtual Network et d'un sous-réseau initial
az network vnet create \
  --resource-group rg-network-demo \
  --name vnet-corp-westeurope \
  --address-prefixes 10.0.0.0/16 \
  --subnet-name snet-web \
  --subnet-prefixes 10.0.1.0/24

# 3. Création d'un sous-réseau supplémentaire pour la base de données
az network vnet subnet create \
  --resource-group rg-network-demo \
  --vnet-name vnet-corp-westeurope \
  --name snet-db \
  --address-prefixes 10.0.2.0/24
```

### 2. Exemple de déploiement en Bicep

```bicep
param location string = 'westeurope'

resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'vnet-corp-westeurope'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.0.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'snet-web'
        properties: {
          addressPrefix: '10.0.1.0/24'
        }
      }
      {
        name: 'snet-db'
        properties: {
          addressPrefix: '10.0.2.0/24'
        }
      }
    ]
  }
}
```

---

## 6. Commandes de Vérification Essentielles (Azure CLI)

| Commande | Description |
| --- | --- |
| `az network vnet list -o table` | Liste l'ensemble des VNets du souscription. |
| `az network vnet show --name <vnet-name> --resource-group <rg-name>` | Affiche les détails et plages IP d'un VNet. |
| `az network vnet subnet list --vnet-name <vnet-name> --resource-group <rg-name>` | Liste tous les sous-réseaux d'un VNet spécifique. |
| `az network nsg list -o table` | Liste les Network Security Groups (NSG) existants. |

---

## Points à retenir

* Un **VNet** est un réseau virtuel privé isolé, limité à une région Azure.
* Azure réserve **5 adresses IP** par sous-réseau.
* Les **NSGs** filtrent le trafic entrant et sortant selon des règles de priorité numériques.
* Par défaut, la communication entre tous les sous-réseaux d'un même VNet est autorisée via les **System Routes**.