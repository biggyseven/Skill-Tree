
# Microsoft Azure — Cours intermédiaire
## Administration, réseau, sécurité, infrastructure as code et exploitation cloud

**Niveau :** Intermédiaire  
**Prérequis :** connaissances de base d'Azure, des réseaux IP, de Linux ou Windows et de la ligne de commande.  
**Public cible :** administrateurs systèmes et réseaux, techniciens cloud, ingénieurs infrastructure et développeurs souhaitant maîtriser le déploiement Azure.  
**Objectif général :** concevoir, déployer, sécuriser et exploiter une infrastructure Azure reproductible, observable et maintenable.

---

# Sommaire

1. Objectifs et environnement de travail
2. Architecture Azure et organisation des ressources
3. Azure CLI : administration et automatisation
4. Réseau virtuel, sous-réseaux, routage et DNS
5. NSG, filtrage réseau et connectivité privée
6. Calcul : machines virtuelles et services applicatifs
7. Stockage Azure et protection des données
8. Identités, RBAC et Key Vault
9. Infrastructure as Code avec Bicep
10. Supervision, diagnostic et journalisation
11. Sauvegarde, haute disponibilité et reprise après sinistre
12. Coûts, gouvernance et bonnes pratiques
13. Travaux pratiques guidés
14. Exercices corrigés
15. Défi final sur 100 points
16. Correction détaillée du défi
17. Glossaire et références

---

# 1. Objectifs et environnement de travail

## 1.1 Compétences attendues

À la fin de ce cours, l'apprenant doit être capable de :

- organiser des ressources à l'aide de groupes de ressources, d'abonnements et de conventions de nommage ;
- utiliser Azure CLI pour interroger, créer, modifier et supprimer des ressources ;
- concevoir un adressage IPv4 adapté à plusieurs sous-réseaux ;
- comprendre les routes système, les routes personnalisées et le peering ;
- appliquer un filtrage réseau à l'aide de Network Security Groups ;
- déployer une machine virtuelle et un service de stockage ;
- utiliser les identités managées et les rôles RBAC ;
- stocker les secrets dans Azure Key Vault ;
- décrire une infrastructure avec Bicep ;
- diagnostiquer un problème de connectivité ;
- activer des alertes et des journaux de supervision ;
- construire une infrastructure de laboratoire reproductible.

## 1.2 Environnement recommandé

Outils nécessaires :

- un compte Azure autorisé à créer les ressources du laboratoire ;
- Azure CLI ;
- un terminal PowerShell, Bash ou Azure Cloud Shell ;
- un éditeur de texte ou Visual Studio Code ;
- une connaissance élémentaire de JSON et YAML ;
- Git, recommandé pour versionner les fichiers Bicep.

Vérifier Azure CLI :

```bash
az version
az login
az account list --output table
az account show --output table
```

Sélectionner explicitement l'abonnement de laboratoire :

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
az account show --query "{nom:name,id:id,tenant:tenantId}" --output json
```

Ne jamais supposer que l'abonnement actif est le bon.

Les commandes de création peuvent générer des coûts. Utiliser un environnement de test, vérifier les quotas et supprimer les ressources à la fin.

## 1.3 Convention de nommage

Une convention facilite l'exploitation, les recherches et l'automatisation.

Exemple :

| Ressource | Nom de laboratoire |
|---|---|
| Groupe de ressources | `rg-azint-lab` |
| Réseau virtuel | `vnet-azint-lab` |
| Sous-réseau applicatif | `snet-app` |
| Sous-réseau de gestion | `snet-mgmt` |
| Groupe de sécurité | `nsg-app` |
| Compte de stockage | `stazintlab001` |
| Coffre de secrets | `kv-azint-lab-001` |
| Machine virtuelle | `vm-azint-app01` |
| Espace de travail de supervision | `law-azint-lab` |

Les noms des comptes de stockage sont globalement uniques, en minuscules et limités aux caractères autorisés. Les noms des coffres Key Vault doivent également respecter leurs contraintes d'unicité et de format.

Dans un projet réel, la convention doit intégrer, si nécessaire, l'environnement, la région, l'application et le propriétaire.

---

# 2. Architecture Azure et organisation des ressources

## 2.1 Les principaux niveaux d'organisation

```text
Microsoft Entra ID
└── Tenant
    ├── Management Group : production
    │   ├── Subscription : prod-europe
    │   │   ├── Resource Group : rg-app-prod
    │   │   │   ├── Virtual Network
    │   │   │   ├── Virtual Machine
    │   │   │   ├── Storage Account
    │   │   │   └── Key Vault
    │   │   └── Resource Group : rg-monitoring-prod
    │   └── Subscription : prod-afrique
    └── Management Group : nonproduction
        └── Subscription : dev-test
```

**Tenant :** frontière d'identité Microsoft Entra ID.

**Management Group :** permet d'organiser les abonnements et d'hériter de politiques ou d'affectations RBAC selon le périmètre.

**Subscription :** frontière importante pour la facturation, les quotas et l'organisation des ressources.

**Resource Group :** conteneur logique de ressources partageant généralement un cycle de vie.

**Resource :** composant Azure individuel.

Un groupe de ressources n'est pas une frontière réseau. Deux ressources du même groupe peuvent être isolées ; deux ressources de groupes différents peuvent communiquer.

## 2.2 Région et zone de disponibilité

Une région Azure correspond à une zone géographique desservie par des centres de données.

Une zone de disponibilité est un emplacement physiquement distinct au sein d'une région qui prend en charge les services compatibles.

```text
Région Azure
├── Zone 1
│   ├── Calcul
│   └── Stockage
├── Zone 2
│   ├── Calcul
│   └── Stockage
└── Zone 3
    ├── Calcul
    └── Stockage
```

La disponibilité zonale dépend du service, du SKU, de la région et de la configuration. Elle ne doit pas être présumée.

**Haute disponibilité régionale :** protéger contre certaines pannes locales.

**Reprise après sinistre :** protéger contre une indisponibilité plus large, potentiellement régionale.

La redondance n'est efficace que si le trafic, les données, les dépendances et les procédures de bascule sont également conçus pour elle.

## 2.3 Création du groupe de ressources

```bash
az group create \
  --name rg-azint-lab \
  --location westeurope \
  --tags Environment=Lab Owner=Training
```

Afficher les groupes :

```bash
az group list --output table
az group show --name rg-azint-lab --output json
```

Lister les ressources :

```bash
az resource list \
  --resource-group rg-azint-lab \
  --output table
```

Le choix de région doit être validé selon les exigences de résidence des données, la disponibilité des services, la latence et le coût.

## 2.4 Azure Resource Manager

Azure Resource Manager (ARM) constitue la couche de gestion des ressources Azure.

```text
Utilisateur / Pipeline
        |
        v
Azure CLI / SDK / Portail
        |
        v
Azure Resource Manager
        |
        +---- Contrôle des autorisations
        +---- Validation des paramètres
        +---- Déploiement des ressources
        +---- Application des politiques
        |
        v
Ressources Azure
```

Un déploiement ARM peut être décrit par un modèle JSON ou par Bicep, qui est compilé vers ARM.

Les opérations du plan de contrôle ne sont pas identiques aux opérations du plan de données. Par exemple, créer un compte de stockage ne signifie pas que l'identité utilisée pourra lire ses blobs.

---

# 3. Azure CLI : administration et automatisation

## 3.1 Principes

Azure CLI utilise la commande principale `az`, suivie d'un groupe de commandes et d'une opération.

```text
az <service> <ressource> <action> [options]
```

Exemples :

```bash
az group list
az vm list
az network vnet list
az storage account list
```

Les commandes `list`, `show`, `create`, `update`, `delete` sont fréquentes, mais leur disponibilité et leurs paramètres dépendent du service.

## 3.2 Filtrer et extraire des données

Azure CLI prend en charge les formats `json`, `table`, `tsv` et les requêtes JMESPath.

```bash
az vm list \
  --query "[].{Nom:name,Region:location,Etat:powerState}" \
  --output table
```

Selon les informations retournées, `powerState` peut ne pas être présent dans une liste simple. Pour obtenir les états d'instance :

```bash
az vm list \
  --show-details \
  --query "[].{Nom:name,Etat:powerState,IP:privateIps}" \
  --output table
```

Afficher l'identifiant d'une ressource :

```bash
az group show \
  --name rg-azint-lab \
  --query id \
  --output tsv
```

Une requête JMESPath s'exécute côté client sur la réponse de la commande.

## 3.3 Vérifier avant de modifier

Avant une modification importante :

1. vérifier l'abonnement ;
2. vérifier le groupe et le nom de la ressource ;
3. lire la configuration actuelle ;
4. confirmer les impacts et les dépendances ;
5. exécuter la modification ;
6. vérifier le résultat.

```bash
az account show
az network vnet show \
  --resource-group rg-azint-lab \
  --name vnet-azint-lab
```

Une commande `delete` peut supprimer des ressources et leurs dépendances selon l'opération. Elle ne doit pas être utilisée sans comprendre le périmètre.

## 3.4 Script Bash de contrôle

```bash
#!/usr/bin/env bash
set -euo pipefail

RG="rg-azint-lab"

if ! az account show >/dev/null 2>&1; then
  echo "Connectez-vous avec az login."
  exit 1
fi

echo "Abonnement actif :"
az account show --query name --output tsv

echo "Ressources dans ${RG} :"
az resource list \
  --resource-group "$RG" \
  --query "[].{Nom:name,Type:type,Region:location}" \
  --output table
```

`set -euo pipefail` aide à détecter les erreurs et les variables non définies dans un script Bash. Il ne remplace pas une gestion d'erreurs adaptée aux opérations critiques.

---

# 4. Réseau virtuel, sous-réseaux, routage et DNS

## 4.1 Virtual Network

Un Virtual Network (VNet) est un réseau privé logique Azure.

Il contient un ou plusieurs sous-réseaux. Chaque sous-réseau dispose d'un préfixe IP appartenant à l'espace d'adressage du VNet.

```text
VNet : 10.20.0.0/16
|
+-- snet-app : 10.20.1.0/24
|   +-- Serveurs applicatifs
|
+-- snet-data : 10.20.2.0/24
|   +-- Services de données
|
+-- snet-mgmt : 10.20.3.0/24
    +-- Composants de gestion
```

Les préfixes de réseaux interconnectés ne doivent pas se chevaucher.

Azure réserve certaines adresses dans chaque sous-réseau IPv4. Un `/24` contient 256 adresses théoriques, mais toutes ne sont pas attribuables aux interfaces Azure.

## 4.2 Calcul du CIDR

Pour IPv4 :

- `/24` correspond à 256 adresses ;
- `/25` correspond à 128 adresses ;
- `/26` correspond à 64 adresses ;
- `/27` correspond à 32 adresses.

Formule du nombre d'adresses :

`2^(32 - préfixe)`

Pour un réseau `/26` :

`2^(32 - 26) = 64 adresses théoriques`

Le nombre d'adresses réellement utilisables dépend des réservations et du service.

### Exemple d'allocation

| Réseau | Préfixe | Fonction |
|---|---|---|
| VNet | `10.20.0.0/16` | Espace global |
| Application | `10.20.1.0/24` | Calcul |
| Données | `10.20.2.0/24` | Données |
| Gestion | `10.20.3.0/24` | Administration |

Réserver des blocs supplémentaires facilite la croissance, le peering et la connexion au réseau d'entreprise.

## 4.3 Créer un VNet

```bash
az network vnet create \
  --resource-group rg-azint-lab \
  --name vnet-azint-lab \
  --location westeurope \
  --address-prefixes 10.20.0.0/16 \
  --subnet-name snet-app \
  --subnet-prefixes 10.20.1.0/24
```

Créer un second sous-réseau :

```bash
az network vnet subnet create \
  --resource-group rg-azint-lab \
  --vnet-name vnet-azint-lab \
  --name snet-data \
  --address-prefixes 10.20.2.0/24
```

Vérifier :

```bash
az network vnet subnet list \
  --resource-group rg-azint-lab \
  --vnet-name vnet-azint-lab \
  --output table
```

## 4.4 Routage Azure

Azure associe aux interfaces réseau des routes effectives provenant notamment :

- des routes système ;
- des routes définies par l'utilisateur, ou UDR ;
- des routes propagées par les passerelles lorsque cette propagation est activée.

La sélection d'une route dépend notamment de la correspondance du préfixe et de la priorité entre les routes applicables.

Une route plus spécifique peut l'emporter sur une route moins spécifique. À préfixe identique, les règles de priorité du routage Azure s'appliquent ; il faut examiner les routes effectives plutôt que supposer le chemin.

Exemple conceptuel :

| Préfixe de destination | Origine | Prochain saut |
|---|---|---|
| `10.20.0.0/16` | VNet | Réseau virtuel |
| `10.30.0.0/16` | Peering | Réseau virtuel distant |
| `0.0.0.0/0` | UDR | Appliance virtuelle |

Cette table est illustrative. Les routes réelles dépendent de la configuration et du contexte de l'interface.

## 4.5 User Defined Routes

Les UDR permettent de contrôler le prochain saut pour des destinations données.

Exemples de types de prochain saut :

- `VirtualAppliance` ;
- `VirtualNetworkGateway` ;
- `VnetLocal` ;
- `Internet` ;
- `None`.

Une route vers `None` peut supprimer la connectivité vers une destination.

Une route vers une appliance virtuelle n'est efficace que si le chemin réseau, le transfert IP, les règles de sécurité et le retour du trafic sont correctement configurés.

## 4.6 VNet peering

Le peering connecte deux réseaux virtuels au moyen du réseau Azure, sans exiger de VPN entre ces deux VNets.

```text
VNet-A  <======== Peering ========>  VNet-B
10.20.0.0/16                       10.30.0.0/16
```

Conditions et limites :

- les plages d'adresses doivent être compatibles et non chevauchantes ;
- les peerings sont configurés dans les deux directions ;
- un peering n'est pas transitif ;
- le peering ne remplace pas les règles NSG ;
- le routage vers un réseau tiers doit être conçu séparément.

Exemple :

```text
Spoke-A ---- Hub ---- Spoke-B

Spoke-A ne communique pas automatiquement
avec Spoke-B uniquement parce que les deux
sont peerés avec Hub.
```

Une architecture hub-and-spoke peut nécessiter Azure Firewall, une appliance réseau ou des routes appropriées pour permettre et contrôler les communications transitives.

## 4.7 DNS

DNS transforme les noms en informations d'adressage.

Azure fournit un DNS par défaut aux VNets. Des DNS personnalisés peuvent être configurés, notamment pour les environnements hybrides.

Un changement de serveurs DNS au niveau d'un VNet peut nécessiter le renouvellement de la configuration réseau des machines pour prendre effet.

Diagnostic sur Linux :

```bash
cat /etc/resolv.conf
getent hosts example.com
nslookup example.com
```

Diagnostic sur Windows :

```powershell
ipconfig /all
nslookup example.com
Resolve-DnsName example.com
```

Un échec DNS ne prouve pas un échec de routage IP. Il faut tester les deux séparément.

---

# 5. NSG, filtrage réseau et connectivité privée

## 5.1 Network Security Group

Un NSG contient des règles de sécurité entrantes et sortantes.

Une règle possède notamment :

- une priorité ;
- une direction ;
- un protocole ;
- des adresses source et destination ;
- des ports source et destination ;
- une action Allow ou Deny.

Les priorités numériques les plus basses sont évaluées avant les priorités plus élevées. Les règles personnalisées sont évaluées avant les règles par défaut lorsque leurs priorités sont plus élevées dans l'ordre d'évaluation.

## 5.2 Schéma de décision

```text
Paquet entrant
      |
      v
Règles NSG applicables
      |
      v
Recherche de la première règle correspondante
      |
      +---- Allow ----> Trafic autorisé par ce NSG
      |
      +---- Deny -----> Trafic bloqué
```

Un NSG associé à un sous-réseau et un NSG associé à une interface peuvent tous deux participer au filtrage. Les règles effectives doivent être analysées sur le chemin concerné.

## 5.3 Exemple : autoriser HTTP depuis une plage définie

Dans cet exemple, le port 80 est autorisé depuis un réseau de confiance, pas depuis Internet entier.

```bash
az network nsg create \
  --resource-group rg-azint-lab \
  --name nsg-app \
  --location westeurope
```

```bash
az network nsg rule create \
  --resource-group rg-azint-lab \
  --nsg-name nsg-app \
  --name AllowHTTPTrusted \
  --priority 200 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes 10.20.3.0/24 \
  --source-port-ranges '*' \
  --destination-address-prefixes '*' \
  --destination-port-ranges 80
```

Attacher le NSG au sous-réseau :

```bash
az network vnet subnet update \
  --resource-group rg-azint-lab \
  --vnet-name vnet-azint-lab \
  --name snet-app \
  --network-security-group nsg-app
```

Cette règle ne crée ni serveur web, ni route, ni adresse IP publique. Elle ne suffit donc pas à rendre une application accessible.

## 5.4 Règles de sécurité

Bonnes pratiques :

- autoriser uniquement les ports nécessaires ;
- limiter les sources aux plages de confiance ;
- éviter l'administration directe depuis Internet ;
- préférer Azure Bastion, VPN ou des mécanismes d'accès contrôlé ;
- documenter les priorités ;
- vérifier les règles effectives après chaque changement.

Ne pas exposer RDP (3389) ou SSH (22) à toutes les adresses Internet sans justification et contrôle supplémentaires.

## 5.5 Azure Bastion et points d'entrée

Azure Bastion permet d'accéder à des machines virtuelles via le portail ou des mécanismes compatibles sans devoir exposer directement leur adresse IP publique pour l'administration.

Il exige une configuration adaptée, notamment un sous-réseau nommé `AzureBastionSubnet` et un SKU compatible avec les fonctionnalités attendues.

Pour un service web public, une architecture courante utilise un point d'entrée applicatif, un pare-feu ou un répartiteur de charge selon les besoins.

## 5.6 Private Endpoint

Un Private Endpoint donne une interface réseau privée dans un VNet pour accéder à un service Azure compatible.

```text
Application privée
       |
       v
Adresse privée du Private Endpoint
       |
       v
Service Azure compatible
```

Un Private Endpoint ne désactive pas automatiquement l'accès public au service cible. Les paramètres d'accès réseau, le DNS privé et les stratégies de sécurité doivent être configurés ensemble.

---

# 6. Calcul : machines virtuelles et services applicatifs

## 6.1 Choisir le modèle de calcul

| Besoin | Option courante | Responsabilité principale |
|---|---|---|
| Contrôle complet du système | Azure Virtual Machines | OS, correctifs et configuration |
| Application web gérée | Azure App Service | Code et configuration applicative |
| Conteneurs orchestrés | Azure Kubernetes Service | Cluster, workloads et politiques |
| Exécution événementielle | Azure Functions | Code, déclencheurs et dépendances |
| Traitement de conteneurs simplifié | Azure Container Apps | Application conteneurisée |

Le service approprié dépend du besoin de contrôle, de la charge, de la disponibilité et des coûts.

## 6.2 Déployer une machine virtuelle

Avant le déploiement, vérifier la disponibilité du SKU dans la région et les quotas du souscripteur.

Exemple de création d'une VM Linux pour un laboratoire :

```bash
az vm create \
  --resource-group rg-azint-lab \
  --name vm-azint-app01 \
  --location westeurope \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --vnet-name vnet-azint-lab \
  --subnet snet-app \
  --admin-username azureuser \
  --generate-ssh-keys
```

Ce déploiement est un exemple pédagogique. Il ne constitue pas, à lui seul, une architecture de production sécurisée. Vérifier notamment l'adresse publique éventuelle, les NSG, les clés, le stockage et les accès autorisés.

Afficher les détails :

```bash
az vm show \
  --resource-group rg-azint-lab \
  --name vm-azint-app01 \
  --show-details \
  --output table
```

Démarrer, arrêter et libérer les ressources de calcul :

```bash
az vm start \
  --resource-group rg-azint-lab \
  --name vm-azint-app01
```

```bash
az vm deallocate \
  --resource-group rg-azint-lab \
  --name vm-azint-app01
```

L'arrêt depuis le système d'exploitation n'est pas équivalent à la désallocation Azure. Une VM désallouée ne facture généralement plus son calcul, mais ses disques et d'autres ressources associées peuvent continuer à être facturés.

## 6.3 Haute disponibilité

Pour améliorer la résilience, envisager selon le scénario :

- Availability Zones ;
- Virtual Machine Scale Sets ;
- répartiteur de charge ;
- Azure Application Gateway ;
- redondance du stockage ;
- sauvegardes et réplication ;
- déploiements reproductibles.

Deux VM ne garantissent pas la haute disponibilité si elles partagent une dépendance unique non redondée.

---

# 7. Stockage Azure et protection des données

## 7.1 Types de stockage

| Service | Usage |
|---|---|
| Blob Storage | Objets, fichiers statiques, journaux et données |
| Azure Files | Partages de fichiers SMB/NFS selon configuration |
| Queue Storage | Files de messages simples |
| Table Storage | Données NoSQL clé-valeur |
| Managed Disks | Disques des machines virtuelles |

## 7.2 Créer un compte de stockage

Le nom doit être unique et respecter les règles du service.

```bash
az storage account create \
  --resource-group rg-azint-lab \
  --name stazintlab001 \
  --location westeurope \
  --sku Standard_LRS \
  --kind StorageV2 \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false
```

Les options de sécurité et de redondance doivent être adaptées au contexte réel.

`Standard_LRS` désigne une redondance locale. Ce choix ne fournit pas la même protection qu'une redondance zonale ou géographique.

## 7.3 Créer un conteneur Blob

```bash
az storage container create \
  --account-name stazintlab001 \
  --name documents \
  --auth-mode login
```

Cette commande utilise l'identité connectée. Elle nécessite les autorisations de plan de données appropriées, par exemple un rôle permettant d'écrire dans les blobs.

Une autorisation de gestion du compte de stockage n'accorde pas systématiquement les permissions de lecture ou d'écriture sur le contenu.

## 7.4 Identité et accès au stockage

Modèle recommandé :

```text
Application
    |
    v
Identité managée
    |
    v
Microsoft Entra ID
    |
    v
Rôle de données approprié
    |
    v
Blob Storage
```

Éviter d'intégrer des clés de compte ou des secrets permanents dans le code.

## 7.5 Protection des données

Selon les besoins, envisager :

- versioning des blobs ;
- soft delete ;
- politiques de rétention ;
- réplication adaptée ;
- sauvegarde ;
- immutabilité lorsque nécessaire ;
- chiffrement ;
- contrôle d'accès réseau ;
- surveillance des accès.

Une réplication géographique ne remplace pas toutes les formes de sauvegarde. Une suppression logique ou une corruption peut se propager selon les mécanismes de réplication.

---

# 8. Identités, RBAC et Key Vault

## 8.1 Microsoft Entra ID

Microsoft Entra ID fournit les identités et l'authentification pour les utilisateurs, groupes, applications et identités managées.

Différencier :

- **authentification** : vérifier l'identité ;
- **autorisation** : déterminer les actions permises ;
- **RBAC Azure** : attribuer des rôles sur des périmètres de ressources ;
- **RBAC de données** : attribuer des permissions sur les données d'un service compatible.

## 8.2 Étendue RBAC

```text
Management Group
      |
      v
Subscription
      |
      v
Resource Group
      |
      v
Resource
```

Une attribution au niveau d'un abonnement peut s'appliquer aux ressources descendantes. Une attribution sur une ressource est plus limitée.

Le principe du moindre privilège consiste à donner le minimum de droits nécessaire, à la plus petite étendue adaptée.

## 8.3 Inspecter les attributions

```bash
az role assignment list \
  --resource-group rg-azint-lab \
  --output table
```

Attribuer un rôle nécessite de connaître l'identité cible, son identifiant et l'étendue correcte.

Exemple conceptuel :

```bash
az role assignment create \
  --assignee-object-id "<OBJECT_ID>" \
  --assignee-principal-type ServicePrincipal \
  --role "Reader" \
  --scope "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-azint-lab"
```

Remplacer les valeurs entre chevrons. L'identité qui effectue l'attribution doit elle-même disposer des autorisations nécessaires.

## 8.4 Identités managées

Une identité managée permet à un service Azure compatible d'obtenir des jetons Microsoft Entra ID sans stocker explicitement un secret d'application dans le code.

Deux grandes formes :

- identité affectée par le système : liée au cycle de vie de la ressource ;
- identité affectée par l'utilisateur : ressource indépendante pouvant être partagée entre plusieurs ressources.

Exemple d'activation d'une identité système sur une VM :

```bash
az vm identity assign \
  --resource-group rg-azint-lab \
  --name vm-azint-app01
```

Afficher son identité :

```bash
az vm show \
  --resource-group rg-azint-lab \
  --name vm-azint-app01 \
  --query identity \
  --output json
```

L'identité doit ensuite recevoir les rôles nécessaires sur les services cibles.

## 8.5 Azure Key Vault

Key Vault permet de stocker des secrets, des clés et des certificats selon les fonctionnalités activées.

Exemple de création :

```bash
az keyvault create \
  --resource-group rg-azint-lab \
  --name kv-azint-lab-001 \
  --location westeurope \
  --enable-rbac-authorization true
```

Le nom doit être globalement unique.

Dans un environnement réel, évaluer les paramètres de protection contre la suppression, la récupération, le réseau privé et les exigences de conformité.

Le modèle RBAC de Key Vault doit être distingué des anciennes politiques d'accès par coffre.

**Ne jamais inscrire un vrai mot de passe ou une vraie clé dans un fichier de cours, un dépôt Git ou un journal de pipeline.**

---

# 9. Infrastructure as Code avec Bicep

## 9.1 Pourquoi utiliser Bicep ?

L'Infrastructure as Code (IaC) permet de décrire l'infrastructure dans des fichiers versionnés.

Avantages :

- reproductibilité ;
- revue des changements ;
- historique Git ;
- déploiements cohérents ;
- réduction des opérations manuelles ;
- automatisation ;
- meilleure collaboration.

Bicep est un langage déclaratif Azure qui se compile en modèle ARM.

## 9.2 Premier fichier Bicep

Créer `main.bicep` :

```bicep
targetScope = 'resourceGroup'

@description('Région du réseau')
param location string = resourceGroup().location

@description('Préfixe du VNet')
param vnetPrefix string = '10.20.0.0/16'

@description('Préfixe du sous-réseau applicatif')
param appSubnetPrefix string = '10.20.1.0/24'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: 'vnet-azint-lab'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetPrefix
      ]
    }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: appSubnetPrefix
        }
      }
    ]
  }
}

output vnetId string = vnet.id
```

Les versions d'API doivent être contrôlées et adaptées aux ressources utilisées. Si une version n'est pas disponible dans un environnement, choisir une version prise en charge par Azure pour ce type de ressource.

## 9.3 Valider et déployer

```bash
az bicep build --file main.bicep
```

Créer le groupe de ressources si nécessaire :

```bash
az group create \
  --name rg-azint-lab \
  --location westeurope
```

Valider le déploiement :

```bash
az deployment group validate \
  --resource-group rg-azint-lab \
  --template-file main.bicep
```

Examiner les changements prévus :

```bash
az deployment group what-if \
  --resource-group rg-azint-lab \
  --template-file main.bicep
```

Déployer :

```bash
az deployment group create \
  --resource-group rg-azint-lab \
  --name deploy-network \
  --template-file main.bicep
```

`what-if` aide à comprendre les changements mais ne remplace ni la revue du modèle, ni l'analyse des dépendances, ni les tests.

## 9.4 Paramètres séparés

Fichier `main.bicepparam` :

```bicep
using './main.bicep'

param location = 'westeurope'
param vnetPrefix = '10.20.0.0/16'
param appSubnetPrefix = '10.20.1.0/24'
```

Déploiement :

```bash
az deployment group create \
  --resource-group rg-azint-lab \
  --template-file main.bicep \
  --parameters main.bicepparam
```

Les paramètres ne doivent pas être utilisés comme dépôt de secrets en clair.

## 9.5 Modules

Les modules permettent de séparer l'infrastructure en composants réutilisables.

```text
infra/
├── main.bicep
├── main.bicepparam
└── modules/
    ├── network.bicep
    ├── storage.bicep
    ├── monitoring.bicep
    └── security.bicep
```

Une bonne architecture IaC sépare les responsabilités, définit clairement les entrées et sorties et évite les dépendances implicites.

---

# 10. Supervision, diagnostic et journalisation

## 10.1 Azure Monitor

Azure Monitor rassemble les mécanismes de collecte, d'analyse et d'alerte des données de supervision.

Concepts essentiels :

- métriques : mesures numériques, généralement adaptées à la surveillance en temps quasi réel ;
- journaux : événements et données interrogeables ;
- alertes : déclenchement d'une action selon une condition ;
- tableaux de bord : visualisation ;
- Log Analytics : analyse des journaux ;
- Application Insights : observabilité applicative.

## 10.2 Métriques et journaux

Exemple :

```text
VM / Application / Réseau
          |
          v
Azure Monitor
    +-----+------+
    |            |
 Métriques     Journaux
    |            |
 Alertes     Log Analytics
    |            |
    +------> Diagnostic
```

Les métriques peuvent servir à déclencher rapidement une alerte de CPU. Les journaux peuvent expliquer pourquoi un service renvoie des erreurs ou pourquoi une connexion a été refusée.

## 10.3 Créer un espace Log Analytics

```bash
az monitor log-analytics workspace create \
  --resource-group rg-azint-lab \
  --workspace-name law-azint-lab \
  --location westeurope
```

La collecte des journaux d'une ressource nécessite une configuration de diagnostic appropriée. La simple création d'un espace de travail ne collecte pas automatiquement tous les journaux de toutes les ressources.

## 10.4 Diagnostic réseau

Outils à connaître :

- Network Watcher ;
- IP flow verify ;
- Next hop ;
- Connection troubleshoot ;
- capture de paquets lorsque prise en charge ;
- journaux de flux de réseau virtuel ;
- journaux de pare-feu ;
- journaux DNS et applicatifs.

Les journaux de flux de réseau virtuel (VNet flow logs) sont à privilégier pour les nouveaux déploiements de journalisation du trafic réseau. Les journaux de flux NSG sont en retrait : leur création de nouveaux flux n'est plus prise en charge depuis le 30 juin 2025 et leur retrait est prévu le 30 septembre 2027. Il faut donc concevoir les nouveaux laboratoires autour des VNet flow logs et planifier la migration des anciens déploiements.

## 10.5 Méthode de dépannage

Lorsqu'une application est inaccessible :

1. vérifier l'état du service ;
2. vérifier l'adresse IP et le nom DNS ;
3. vérifier les routes effectives ;
4. examiner les NSG ;
5. vérifier les règles du pare-feu et les ports d'écoute ;
6. examiner les journaux ;
7. tester le chemin réseau ;
8. isoler la couche en panne ;
9. corriger un seul facteur à la fois ;
10. vérifier de nouveau le fonctionnement.

Un test réussi depuis une VM ne prouve pas que l'accès fonctionne depuis Internet. Le point de départ du test doit correspondre au scénario réel.

---

# 11. Sauvegarde, haute disponibilité et reprise après sinistre

## 11.1 Définitions

**Sauvegarde :** copie récupérable des données ou de l'état d'un système.

**Haute disponibilité :** réduction de l'interruption grâce à la redondance et à la détection des pannes.

**Reprise après sinistre :** procédure permettant de restaurer un service après un événement majeur.

**RPO :** quantité maximale de données que l'organisation accepte de perdre, exprimée en durée.

**RTO :** durée maximale visée pour rétablir le service.

Exemple :

- RPO : 15 minutes ;
- RTO : 2 heures.

Ces objectifs ne sont réalistes que si les solutions techniques et les procédures ont été conçues et testées pour les atteindre.

## 11.2 Exemple d'architecture résiliente

```text
                 Utilisateurs
                      |
                      v
              Point d'entrée
                      |
            +---------+---------+
            |                   |
            v                   v
       Instance A           Instance B
        Zone 1               Zone 2
            |                   |
            +---------+---------+
                      |
                      v
                Données durables
                      |
             Sauvegardes protégées
                      |
             Procédure de restauration
```

La base de données, les identités, les secrets, le DNS et le point d'entrée doivent aussi être examinés. Une application redondante dépendant d'une base unique non protégée reste vulnérable.

## 11.3 Tester les sauvegardes

Une sauvegarde dont la restauration n'a jamais été testée n'offre pas une garantie suffisante.

Plan de test :

1. identifier le jeu de données ;
2. vérifier la date et l'intégrité de la sauvegarde ;
3. restaurer dans un environnement isolé ;
4. contrôler les permissions et les dépendances ;
5. exécuter des tests applicatifs ;
6. mesurer le temps de restauration ;
7. consigner le résultat ;
8. corriger les écarts.

---

# 12. Coûts, gouvernance et bonnes pratiques

## 12.1 Principaux facteurs de coût

Les coûts peuvent dépendre :

- de la taille et de la durée d'exécution des VM ;
- du stockage consommé ;
- des transactions ;
- du trafic réseau sortant ;
- des journaux conservés ;
- des passerelles et pare-feu ;
- des adresses IP et services associés ;
- des licences et engagements tarifaires.

Arrêter une VM ne signifie pas que toutes ses ressources cessent d'être facturées.

## 12.2 Réduire les dépenses

- choisir un SKU adapté à la charge ;
- désallouer les VM de laboratoire ;
- limiter la rétention des journaux selon les besoins ;
- définir des budgets et des alertes ;
- contrôler les ressources orphelines ;
- choisir une redondance adaptée aux objectifs métier ;
- utiliser les recommandations de coût avec validation humaine.

## 12.3 Azure Policy

Azure Policy permet d'auditer ou de contrôler certaines configurations.

Exemples de gouvernance :

- régions autorisées ;
- exigences de balisage ;
- audit des ressources publiques ;
- exigences de diagnostic ;
- restrictions sur certains SKU.

Une politique `Deny` peut bloquer un déploiement. Il faut tester les affectations et comprendre leurs effets sur les ressources existantes et nouvelles.

## 12.4 Checklist avant production

- [ ] Adressage sans chevauchement.
- [ ] Contrôle des flux réseau documenté.
- [ ] Accès administratifs limités.
- [ ] Identités managées privilégiées.
- [ ] Secrets hors du code source.
- [ ] Sauvegardes restaurables.
- [ ] Supervision et alertes configurées.
- [ ] Journalisation adaptée.
- [ ] Objectifs RPO/RTO définis.
- [ ] Coûts et quotas vérifiés.
- [ ] Infrastructure versionnée.
- [ ] Procédure de suppression et de retour arrière documentée.

---

# 13. Travaux pratiques guidés

## TP 1 — Construire un réseau isolé

### Objectif

Créer un VNet avec deux sous-réseaux, puis contrôler l'adressage.

### Étapes

1. Vérifier l'abonnement et la région.
2. Créer `rg-azint-lab`.
3. Créer `vnet-azint-lab` en `10.20.0.0/16`.
4. Créer `snet-app` en `10.20.1.0/24`.
5. Créer `snet-data` en `10.20.2.0/24`.
6. Afficher les sous-réseaux.
7. Vérifier l'absence de chevauchement.

### Commandes de contrôle

```bash
az network vnet show \
  --resource-group rg-azint-lab \
  --name vnet-azint-lab \
  --query addressSpace.addressPrefixes \
  --output json
```

```bash
az network vnet subnet list \
  --resource-group rg-azint-lab \
  --vnet-name vnet-azint-lab \
  --query "[].{Nom:name,CIDR:addressPrefix}" \
  --output table
```

### Résultat attendu

Un VNet en `/16` contenant deux sous-réseaux `/24` distincts.

## TP 2 — Déployer et contrôler une VM

### Objectif

Déployer une VM Linux et distinguer l'état du système de l'état de la ressource Azure.

### Étapes

1. Vérifier le SKU disponible.
2. Déployer une VM dans `snet-app`.
3. Afficher ses propriétés.
4. Examiner l'adresse IP privée.
5. Vérifier les NSG associés.
6. Désallouer la VM.
7. Confirmer son état.
8. Évaluer les ressources qui continuent d'exister.

Ne pas ouvrir SSH à toutes les sources pour simplifier le laboratoire. Préférer Azure Bastion, un accès privé ou une source de gestion contrôlée.

## TP 3 — Déployer un compte de stockage privé

### Objectif

Créer un compte de stockage, un conteneur privé et examiner les autorisations.

### Étapes

1. Choisir un nom de compte unique.
2. Créer le compte avec l'accès anonyme désactivé.
3. Créer le conteneur `documents`.
4. Tenter l'accès avec l'identité connectée.
5. Examiner les autorisations de plan de données.
6. Vérifier que les données ne sont pas publiques.
7. Documenter la différence entre RBAC de gestion et RBAC des blobs.

## TP 4 — Déployer avec Bicep

### Objectif

Décrire un VNet en Bicep et appliquer le modèle.

### Étapes

1. Écrire `main.bicep`.
2. Compiler le fichier.
3. Valider le déploiement.
4. Lancer `what-if`.
5. Déployer.
6. Comparer les propriétés réelles aux propriétés déclarées.
7. Modifier le préfixe du sous-réseau dans un environnement de test.
8. Réexécuter `what-if` et interpréter les changements.

---

# 14. Exercices corrigés

## Exercice 1 — Adressage

Un VNet utilise `10.40.0.0/16`. Il faut trois sous-réseaux distincts pour les applications, les données et la gestion.

Proposer trois préfixes `/24`.

### Correction

Une solution possible :

- Applications : `10.40.1.0/24`
- Données : `10.40.2.0/24`
- Gestion : `10.40.3.0/24`

Ils appartiennent tous au VNet et ne se chevauchent pas.

## Exercice 2 — Peering

Le VNet A est peeré avec B. Le VNet B est peeré avec C. A peut-il automatiquement joindre C ?

### Correction

Non. Le peering n'est pas transitif. Il faut un peering direct entre A et C ou une architecture de transit configurée, par exemple avec une appliance réseau et des routes adaptées.

## Exercice 3 — Filtrage

Une règle autorise TCP/443 depuis `10.40.3.0/24`. Un utilisateur situé sur Internet ne peut pas se connecter au serveur HTTPS. Est-ce nécessairement un défaut Azure ?

### Correction

Non. La règle ne permet l'accès qu'à la source spécifiée. De plus, il faut vérifier l'existence d'un service en écoute, le point d'entrée, le routage, les NSG et les autres règles de filtrage.

## Exercice 4 — Stockage

Une identité possède un rôle de lecture sur le groupe de ressources mais ne peut pas lire les blobs. Pourquoi ?

### Correction

Le rôle de lecture du plan de contrôle ne donne pas nécessairement accès au contenu des blobs. Il faut attribuer un rôle de données approprié sur le compte ou le conteneur, puis vérifier l'identité et l'étendue effectives.

## Exercice 5 — Disponibilité

Deux VM sont déployées dans la même zone et utilisent une seule base de données non redondée. L'application est-elle hautement disponible ?

### Correction

Pas nécessairement. Les VM peuvent partager des points de défaillance communs. Il faut examiner les zones, le point d'entrée, les données, les dépendances et les procédures de bascule.

## Exercice 6 — Infrastructure as Code

Pourquoi exécuter `what-if` avant un déploiement ?

### Correction

Pour examiner les changements prévus, détecter les créations, modifications ou suppressions inattendues et réduire le risque d'une modification destructive. La revue du modèle reste indispensable.

---

# 15. Défi final — Projet Azure intermédiaire (100 points)

## Scénario

Une petite entreprise veut héberger une application interne sur Azure.

Exigences :

- un réseau privé avec des sous-réseaux distincts ;
- un serveur applicatif Linux ;
- un stockage privé pour les documents ;
- des accès réseau limités ;
- une architecture décrite en Bicep ;
- une supervision minimale ;
- une procédure de sauvegarde et de restauration ;
- une estimation et une maîtrise des coûts.

Tu dois fournir un dossier technique reproductible. Les déploiements payants sont facultatifs pour la validation écrite.

## Partie A — Architecture et adressage (20 points)

1. Proposer un VNet et trois sous-réseaux sans chevauchement. (8 points)
2. Expliquer les flux autorisés entre les composants. (6 points)
3. Expliquer comment l'administration est réalisée sans exposer SSH à Internet. (6 points)

## Partie B — Sécurité (20 points)

1. Définir une stratégie NSG minimale. (8 points)
2. Expliquer comment l'application accède au stockage sans secret en clair. (6 points)
3. Expliquer le rôle de RBAC et de Key Vault. (6 points)

## Partie C — Déploiement reproductible (20 points)

1. Fournir un fichier Bicep pour le réseau. (10 points)
2. Décrire les commandes de validation et de déploiement. (5 points)
3. Expliquer comment utiliser Git et les paramètres par environnement. (5 points)

## Partie D — Exploitation (20 points)

1. Définir les contrôles de santé et la journalisation. (6 points)
2. Décrire le dépannage d'une connexion refusée. (6 points)
3. Définir les objectifs de sauvegarde et de restauration. (4 points)
4. Décrire les mesures de contrôle des coûts. (4 points)

## Partie E — Mise en situation (20 points)

Une application ne peut plus accéder à son conteneur Blob après une modification de sécurité.

1. Proposer une démarche de diagnostic sans désactiver globalement la sécurité. (8 points)
2. Identifier les couches possibles du problème. (6 points)
3. Décrire une correction minimale et une procédure de validation. (6 points)

---

# 16. Correction détaillée du défi final

## 16.1 Partie A — Architecture (20 points)

Proposition :

```text
VNet : 10.50.0.0/16
|
+-- snet-app : 10.50.1.0/24
|   +-- Serveur applicatif
|
+-- snet-data : 10.50.2.0/24
|   +-- Accès privé aux services de données
|
+-- snet-mgmt : 10.50.3.0/24
    +-- Administration contrôlée
```

Les trois plages sont distinctes et incluses dans `10.50.0.0/16`.

Les flux doivent être définis selon les besoins réels : administration depuis une source de confiance, application vers les services de données, et refus des communications inutiles.

L'administration peut passer par Azure Bastion ou un chemin privé contrôlé. Si un accès public est exceptionnellement nécessaire, il doit être restreint et protégé.

## 16.2 Partie B — Sécurité (20 points)

La stratégie NSG doit être restrictive et documentée. Il faut autoriser seulement les ports requis depuis les sources nécessaires. Un NSG ne remplace pas l'authentification de l'application ni le contrôle d'accès aux données.

Une identité managée attachée à la VM peut recevoir un rôle de données adapté au conteneur Blob. Le code obtient un jeton auprès de Microsoft Entra ID, sans conserver une clé de compte.

Key Vault conserve les secrets qui restent nécessaires, tandis que RBAC détermine les permissions sur les ressources et, selon le rôle, sur les données.

## 16.3 Partie C — Exemple Bicep (20 points)

Fichier `main.bicep` :

```bicep
targetScope = 'resourceGroup'

param location string = resourceGroup().location

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: 'vnet-azint-project'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.50.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: '10.50.1.0/24'
        }
      }
      {
        name: 'snet-data'
        properties: {
          addressPrefix: '10.50.2.0/24'
        }
      }
      {
        name: 'snet-mgmt'
        properties: {
          addressPrefix: '10.50.3.0/24'
        }
      }
    ]
  }
}

output vnetId string = vnet.id
```

Commandes :

```bash
az bicep build --file main.bicep

az deployment group validate \
  --resource-group rg-azint-lab \
  --template-file main.bicep

az deployment group what-if \
  --resource-group rg-azint-lab \
  --template-file main.bicep

az deployment group create \
  --resource-group rg-azint-lab \
  --template-file main.bicep
```

Les paramètres par environnement doivent permettre de séparer développement, test et production. Le dépôt Git doit contenir le code et la documentation, mais pas de secrets en clair.

## 16.4 Partie D — Exploitation (20 points)

La supervision doit inclure l'état de la VM, les métriques pertinentes, les journaux applicatifs et des alertes associées à des seuils ou événements significatifs.

Pour une connexion refusée, vérifier dans l'ordre :

1. identité utilisée ;
2. rôle attribué ;
3. étendue du rôle ;
4. configuration du service de stockage ;
5. règles de réseau et DNS ;
6. journaux disponibles ;
7. éventuelles restrictions de jetons ou de configuration.

Les sauvegardes doivent avoir un RPO et un RTO définis et faire l'objet de tests de restauration. Les coûts sont contrôlés par des budgets, le choix des SKU, la désallocation des VM inutilisées et la surveillance des ressources persistantes.

## 16.5 Partie E — Diagnostic (20 points)

Il faut commencer par déterminer si l'erreur est une erreur d'authentification, d'autorisation, de résolution DNS ou de connectivité.

Contrôles possibles :

```bash
az account show

az role assignment list \
  --scope "<SCOPE_RESOURCE_ID>" \
  --output table
```

Le second contrôle nécessite de remplacer `<SCOPE_RESOURCE_ID>` par l'identifiant réel du périmètre pertinent.

La correction minimale peut être de rétablir le rôle de données requis sur le conteneur, ou de corriger le réseau privé ou le DNS si le problème vient de la connectivité. Il ne faut pas rendre le stockage public comme solution de dépannage par défaut.

Après correction :

1. vérifier les attributions effectives ;
2. retester avec l'identité de l'application ;
3. confirmer l'accès uniquement au périmètre requis ;
4. examiner les journaux ;
5. documenter le changement ;
6. ajouter un test de non-régression.

### Barème de maîtrise

- **90–100 :** autonomie solide pour les déploiements Azure intermédiaires.
- **75–89 :** bonne maîtrise ; quelques approfondissements sont nécessaires.
- **60–74 :** connaissances fonctionnelles, mais plusieurs contrôles doivent être renforcés.
- **Moins de 60 :** revoir le réseau, les identités et les bases de l'IaC avant de passer à l'expertise.

---

# 17. Glossaire et références

## Glossaire

- **ARM :** Azure Resource Manager.
- **Bicep :** langage déclaratif pour décrire des ressources Azure.
- **CIDR :** notation de préfixe réseau IP.
- **IaC :** Infrastructure as Code.
- **Key Vault :** service de gestion des secrets, clés et certificats.
- **NSG :** Network Security Group.
- **RBAC :** Role-Based Access Control.
- **RPO :** objectif de point de reprise.
- **RTO :** objectif de délai de reprise.
- **UDR :** User Defined Route.
- **VNet :** Virtual Network.

## Documentation officielle

- Azure CLI : https://learn.microsoft.com/cli/azure/
- Azure Virtual Network : https://learn.microsoft.com/azure/virtual-network/
- Architecture hub-and-spoke : https://learn.microsoft.com/azure/networking/design-guide/hub-spoke
- Azure RBAC : https://learn.microsoft.com/azure/role-based-access-control/overview
- Azure Key Vault : https://learn.microsoft.com/azure/key-vault/general/overview
- Bicep : https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview
- Azure Monitor : https://learn.microsoft.com/azure/azure-monitor/
- VNet flow logs : https://learn.microsoft.com/azure/network-watcher/vnet-flow-logs-overview

---

**Fin du cours Azure intermédiaire.**

Le passage au niveau expert suppose de maîtriser les réseaux, le RBAC, les déploiements reproductibles et les bases de l'observabilité présentés dans ce fichier.
