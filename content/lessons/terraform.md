# 📚 Cours intensif : Infrastructure as Code avec **Terraform**  
*Niveau : Administrateur Réseau Senior (CCIE)*  

---

## Table des matières
| # | Section |
|---|---------|
| 1 | Introduction & concepts clés |
| 2 | Architecture de Terraform |
| 3 | Installation & configuration (Linux / macOS / Windows) |
| 4 | Gestion du **state** – backends, verrouillage, chiffrement |
| 5 | Providers réseau – Cisco IOS, IOS‑XR, NX‑OS, Juniper, Arista |
| 6 | Modules, workspaces et stratégies de versionning |
| 7 | Comparatif des principaux outils IaC |
| 8 | Bonnes pratiques & patterns (DRY, CI/CD, GitOps) |
| 9 | Sécurité & conformité (Vault, Sentinel, OPA) |
|10 | Intégration avec Ansible / Python / Go |
|11 | Déploiement avancé – Terraform Cloud & Enterprise |
|12 | **Atelier de dépannage** – Scénarios réels |
|13 | Ressources complémentaires & lectures recommandées |

> **Objectif** : Vous permettre de concevoir, déployer, versionner et dépanner une infrastructure réseau complète (data‑center, WAN, SD‑WAN) à l’aide de Terraform, en appliquant les standards de l’ingénierie logicielle.

---

## 1️⃣ Introduction & concepts clés

| Concept | Description | Analogie réseau |
|---------|-------------|-----------------|
| **Infrastructure as Code (IaC)** | Définir l’infrastructure via du code déclaratif versionnable. | *Blueprint* d’un réseau stocké dans un dépôt Git. |
| **Terraform** | Outil open‑source de HashiCorp qui transforme le code HCL en API calls vers les providers. | *Orchestrateur* qui pousse les configurations sur les équipements. |
| **Provider** | Plugin qui traduit les ressources Terraform en appels API/CLI du système cible. | *Driver* d’un dispositif (Cisco, AWS, Azure…). |
| **State** | Base de données locale ou distante qui conserve le mapping entre les ressources déclarées et leur ID réel. | *Table de correspondance* entre le plan et le réseau réel. |
| **Plan → Apply** | Deux‑phases : Terraform calcule le delta (plan) puis l’applique (apply). | *Simulation* avant mise en production. |
| **Idempotence** | Re‑exécution sans effet secondaire si l’état désiré est déjà atteint. | *Re‑application* sûre d’une configuration. |

---

## 2️⃣ Architecture de Terraform

```
+-------------------+          +-------------------+          +-------------------+
|   Configuration   |  HCL →   |   Terraform Core  |  API →   |   Provider Plug‑in |
|   (main.tf, *.tf) |--------->| (plan, graph,    |--------->| (Cisco IOS, AWS…) |
|                   |          |  state mgmt)      |          |                   |
+-------------------+          +-------------------+          +-------------------+
        |                                 |                         |
        |                                 |                         |
        |                                 v                         v
        |                         +-------------------+      +-------------------+
        |                         |   Backend (S3,   |      |   Remote API      |
        |                         |   Consul, etc.)  |      |   (RESTCONF, NETCONF) |
        |                         +-------------------+      +-------------------+
        |                                 |
        v                                 v
+-------------------+          +-------------------+
|   Git / CI/CD     |          |   Terraform Cloud |
|   (versioning)    |          |   (run, remote)   |
+-------------------+          +-------------------+
```

* **Core** : parseur HCL, moteur de dépendances, générateur de graphe d’exécution.  
* **Backend** : persistance du *state* (local, S3, Azure Blob, Terraform Cloud).  
* **Provider** : implémente les CRUD (`Create`, `Read`, `Update`, `Delete`) via les API du vendor.

---

## 3️⃣ Installation & configuration (Linux)

### 3.1 Prérequis système
| OS | Version minimale | Packages |
|----|------------------|----------|
| Ubuntu 20.04 LTS | 20.04 | `unzip`, `curl`, `git` |
| RHEL 8 | 8 | `unzip`, `curl`, `git` |
| macOS 12 (Monterey) | 12 | `brew` |

### 3.2 Installation (CLI)

```bash
# 1️⃣ Télécharger la dernière version stable (v1.9.5 au 20‑Oct‑2026)
curl -LO https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip

# 2️⃣ Décompresser et placer dans le PATH
sudo unzip terraform_1.9.5_linux_amd64.zip -d /usr/local/bin/

# 3️⃣ Vérifier l'installation
terraform version
# Terraform v1.9.5
# on linux_amd64
```

### 3.3 Configuration d’un workspace de travail

```bash
mkdir -p ~/tf-workspaces/network
cd ~/tf-workspaces/network
git init
git remote add origin git@github.com:yourorg/network-iac.git
```

> **Astuce** : créez un *branch* `dev` pour les tests, `main` pour la prod. Utilisez les *GitHub Actions* ou *GitLab CI* pour déclencher `terraform plan` automatiquement.

---

## 4️⃣ Gestion du **state** – backends, verrouillage, chiffrement

### 4.1 Pourquoi le state est crucial
* Il stocke les IDs des ressources (ex. `interface Gig0/1` → `id = "Gig0/1"`).  
* Il permet le calcul du **diff** entre l’état actuel et le désiré.  
* Un **state corrompu** = désynchronisation, risque de doublons ou de suppression involontaire.

### 4.2 Backends recommandés pour le réseau d’entreprise

| Backend | Stockage | Verrouillage | Chiffrement | Cas d’usage |
|--------|----------|--------------|-------------|-------------|
| **local** | fichier `terraform.tfstate` | ❌ | ❌ | Lab, tests rapides |
| **S3 + DynamoDB** | AWS S3 bucket | ✅ (DynamoDB) | ✅ (SSE‑KMS) | Multi‑user, production |
| **Azure Blob + Cosmos DB** | Azure Storage | ✅ (Cosmos) | ✅ (CMK) | Environnements Azure |
| **Terraform Cloud** | Gestion interne | ✅ | ✅ | Collaboration SaaS |
| **Consul** | KV store | ✅ (session lock) | ✅ (TLS) | Environnements hybrides |

### 4.3 Exemple de configuration backend S3

```hcl
terraform {
  backend "s3" {
    bucket         = "tf-state-prod"
    key            = "network/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "tf-locks"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:eu-west-1:123456789012:key/abcd-ef01-2345"
  }
}
```

### 4.4 Opérations courantes sur le state

| Commande | Description |
|----------|-------------|
| `terraform state list` | Liste toutes les ressources connues. |
| `terraform state show <address>` | Affiche les attributs d’une ressource. |
| `terraform state pull > state.backup` | Export du state brut (JSON). |
| `terraform state push state.backup` | Remise en place d’un state sauvegardé. |
| `terraform state rm <address>` | Supprime la référence d’une ressource (utile avant `import`). |
| `terraform state replace-provider` | Migration entre versions de provider (ex. `ciscoios` → `ciscoiosv2`). |

---

## 5️⃣ Providers réseau – Cisco IOS, IOS‑XR, NX‑OS, Juniper, Arista

### 5.1 Principes généraux
* Les providers utilisent **RESTCONF**, **NETCONF**, **NX‑API** ou **gRPC**.  
* La plupart requièrent **authentification basique** ou **token**.  
* Il faut activer les services API sur le dispositif.

### 5.2 Activation des API sur un routeur Cisco IOS‑XE (exemple)

```cisco
!--- Mode configuration globale
conf t
! Activer le serveur HTTP sécurisé
ip http secure-server
! Activer le service NETCONF over SSH
netconf-yang
! Créer un utilisateur dédié à Terraform
username tfadmin privilege 15 secret 0 Tf$R00t!
! Limiter l’accès à l’IP du serveur CI
ip access-list standard TF-CI
  permit 10.0.10.0 0.0.0.255
line vty 0 4
  access-class TF-CI in
  login local
exit
```

### 5.3 Provider `ciscoios` (exemple de configuration)

```hcl
terraform {
  required_providers {
    ciscoios = {
      source  = "cisco/ciscoios"
      version = "~> 0.6"
    }
  }
}

provider "ciscoios" {
  host     = "10.0.10.10"
  username = "tfadmin"
  password = "Tf$R00t!"
  transport = "ssh"          # ou "https" si RESTCONF
  insecure = false           # true pour auto‑accept cert self‑signed
}
```

### 5.4 Ressource réseau typique : création d’une interface VLAN

```hcl
resource "ciscoios_interface_vlan" "vlan10" {
  name        = "Vlan10"
  description = "VLAN pour le réseau de management"
  ip_address  = "192.168.10.1"
  subnet_mask = "255.255.255.0"
}
```

### 5.5 Exemple complet – Fabric d’Arista EOS

```hcl
provider "arista" {
  host     = "10.0.20.5"
  username = "tfadmin"
  password = "Ar!$t@123"
  transport = "https"
  verify_ssl = false
}

resource "arista_eos_interface" "leaf1_eth1" {
  name        = "Ethernet1"
  description = "Uplink to spine1"
  mode        = "routed"
  ip_address  = "10.10.0.2/31"
}
```

---

## 6️⃣ Modules, workspaces et stratégies de versionning

### 6.1 Modules – réutilisabilité et DRY

| Niveau | Exemple de répertoire |
|--------|-----------------------|
| **Root** | `main.tf`, `variables.tf`, `outputs.tf` |
| **Module** | `modules/interface_vlan/` |
| **Sous‑module** | `modules/interface_vlan/subnet/` |

#### 6.1.1 Structure d’un module **interface_vlan**

```
modules/
└─ interface_vlan/
   ├─ main.tf          # ressources
   ├─ variables.tf    # variables d’entrée
   ├─ outputs.tf      # valeurs exportées
   └─ README.md
```

#### 6.1.2 Utilisation du module

```hcl
module "mgmt_vlan" {
  source      = "./modules/interface_vlan"
  name        = "Vlan10"
  description = "Management VLAN"
  ip_address  = "192.168.10.1"
  subnet_mask = "255.255.255.0"
}
```

### 6.2 Workspaces – isolation d’environnements

```bash
terraform workspace new dev
terraform workspace select dev
# Déploiement sur l’environnement de dev
terraform apply -var-file=dev.tfvars
```

| Workspace | Backend key (S3) |
|-----------|------------------|
| `dev`     | `network/dev/terraform.tfstate` |
| `prod`    | `network/prod/terraform.tfstate` |

### 6.3 Versionning du code et du provider

```hcl
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    ciscoios = {
      source  = "cisco/ciscoios"
      version = "~> 0.6.3"
    }
  }
}
```

> **Tip** : Utilisez `terraform providers lock` pour créer un fichier `terraform.lock.hcl` qui garantit la même version du provider sur tous les runners CI.

---

## 7️⃣ Comparatif des principaux outils IaC

| Feature | **Terraform** | **Ansible** (Playbooks) | **AWS CloudFormation** | **Pulumi** |
|---------|---------------|--------------------------|------------------------|------------|
| **Langage** | HCL (déclaratif) | YAML + Jinja2 (déclaratif/impératif) | JSON/YAML (déclaratif) | TypeScript/Go/Python (imperative + declarative) |
| **Gestion du state** | Obligatoire (remote/local) | Pas de state persistant (idempotence via fact gathering) | Géré par AWS (stack) | Stocké dans le cloud (Pulumi Service) |
| **Idempotence** | Garantie via plan | Dépend du module, parfois non‑idempotent | Garanties par le service | Garanties via le moteur Pulumi |
| **Extensibilité** | Providers (C, Go) | Modules, Collections | Ressources natives AWS | SDKs natifs |
| **Support multi‑cloud** | ✅ (AWS, Azure, GCP, OCI, etc.) | ✅ (via modules) | ❌ (AWS only) | ✅ |
| **Débogage** | `terraform plan`, `apply -target`, `state` | `ansible-playbook -vvv` | `aws cloudformation describe-stacks` | `pulumi preview` |
| **Policy as Code** | Sentinel (Terraform Cloud) / OPA | Ansible Tower RBAC | IAM policies | Pulumi Policy Packs |
| **Coût** | Gratuit (OSS) + Cloud (optionnel) | Gratuit (OSS) + Tower (payant) | Gratuit (payant selon usage) | Gratuit (OSS) + Service (payant) |

---

## 8️⃣ Bonnes pratiques & patterns (DRY, CI/CD, GitOps)

| Pratique | Implémentation Terraform | Pourquoi c’est crucial |
|----------|--------------------------|------------------------|
| **Modularisation** | Modules réutilisables, versionnés via Git sub‑modules ou Terraform Registry. | Réduction du *technical debt* et uniformité du réseau. |
| **State remote + verrouillage** | Backend S3 + DynamoDB, ou Terraform Cloud. | Empêche les courses de modification concurrentes. |
| **Plan‑only dans CI** | `terraform fmt -check`, `terraform validate`, `terraform plan -out=tfplan` | Détection précoce des erreurs avant le merge. |
| **Apply uniquement via CD** | GitHub Actions → `terraform apply tfplan` sur `main` uniquement. | Séparation claire entre validation et mise en production. |
| **Policy as Code** | Sentinel policies (ex. interdiction de créer des VLAN > 100). | Conformité réseau (PCI‑DSS, ISO‑27001). |
| **Secrets management** | HashiCorp Vault + `vault_generic_secret` data source. | Pas de mots de passe en clair dans le repo. |
| **Tagging & naming convention** | `name = "${var.site}-${var.role}-${var.id}"` | Facilite le suivi et la facturation. |
| **Testing** | `terraform validate`, `terratest` (Go), `kitchen‑terraform`. | Garantie de non‑régression. |
| **Documentation auto‑générée** | `terraform-docs` → `README.md` des modules. | Maintien de la doc à jour. |

### 8.1 Exemple de pipeline GitHub Actions (simplifié)

```yaml
name: Terraform CI/CD

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  fmt-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.9.5
      - name: Terraform fmt
        run: terraform fmt -check
      - name: Terraform validate
        run: terraform validate

  plan:
    needs: fmt-validate
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.9.5
      - name: