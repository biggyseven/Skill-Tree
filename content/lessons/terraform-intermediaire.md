
# Infrastructure as Code avec Terraform — Niveau intermédiaire

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** connaître HCL, les ressources, les variables, le state et les commandes Terraform fondamentales.  
> **Objectif :** construire une infrastructure réseau modulaire, maîtriser les dépendances, tester les configurations et intégrer Terraform dans une chaîne de validation.

---

## Sommaire

1. Contexte et objectifs
2. Architecture du projet
3. Construire un réseau cloud avec Terraform
4. Variables, validations et sorties
5. Comprendre les dépendances
6. Créer des modules réutilisables
7. Data sources et ressources existantes
8. Tests Terraform
9. State, environnements et plans enregistrés
10. Pipeline CI/CD
11. Sécurité et contrôle des changements
12. Atelier pratique
13. Dépannage
14. Évaluation corrigée
15. Préparation du niveau expert

---

# 1. Contexte et objectifs

## 1.1 Passer d'un exercice local à une infrastructure réelle

Au niveau débutant, nous avons décrit une ressource locale pour comprendre le cycle de Terraform. Le niveau intermédiaire applique les mêmes principes à une architecture réseau.

Dans un cloud, une infrastructure réseau peut comporter :

- un réseau virtuel ;
- des sous-réseaux ;
- des tables de routage ;
- des passerelles ;
- des règles de filtrage ;
- des points d'accès ou des interfaces réseau ;
- des mécanismes d'interconnexion.

Terraform permet de déclarer ces ressources et de calculer un plan de changement. Il ne remplace ni la conception IP, ni la politique de sécurité, ni l'approbation opérationnelle.

## 1.2 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

1. décrire un réseau cloud dans des fichiers Terraform ;
2. déclarer des ressources qui se référencent ;
3. utiliser des variables typées et des validations ;
4. organiser une configuration dans des modules ;
5. consulter une ressource existante avec une data source ;
6. tester des valeurs de configuration sans déployer réellement ;
7. comprendre les plans enregistrés et les limites du state local ;
8. construire une CI de validation ;
9. contrôler les risques liés aux remplacements et destructions ;
10. préparer une configuration exploitable dans plusieurs environnements.

---

# 2. Architecture du projet

Une organisation possible est la suivante :

```text
terraform-intermediaire/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── terraform.tfvars.example
├── .gitignore
├── modules/
│   └── network/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── tests/
│   └── network.tftest.hcl
└── .github/
    └── workflows/
        └── validate.yml
```

Les fichiers `.tf` situés dans le même répertoire forment un module. Le répertoire racine constitue le module racine ; les répertoires appelés par un bloc `module` correspondent à des modules enfants.

## 2.1 Responsabilité des fichiers

| Fichier | Responsabilité |
|---|---|
| `main.tf` | Ressources et appels de modules |
| `variables.tf` | Paramètres d'entrée |
| `outputs.tf` | Valeurs publiées par le module |
| `versions.tf` | Contraintes sur Terraform et les providers |
| `terraform.tfvars.example` | Exemple non sensible de valeurs d'entrée |
| `modules/network/` | Composants réseau réutilisables |
| `tests/` | Tests des comportements attendus |
| `validate.yml` | Étapes de vérification automatisées |

Une bonne structure doit rendre le changement facile à lire, à tester et à expliquer. Le nombre de fichiers n'est pas un objectif en soi.

---

# 3. Construire un réseau cloud avec Terraform

## 3.1 Précautions avant le laboratoire

L'exemple principal utilise le provider AWS. Il nécessite un compte AWS et des identifiants correctement configurés pour toute opération qui contacte AWS.

Les objets VPC et sous-réseau illustrés servent à comprendre la configuration réseau. N'ajoutez pas de machines virtuelles, de passerelles payantes ou d'autres services sans en examiner le coût, les permissions et les conséquences.

Ne stockez pas les clés AWS dans le dépôt.

## 3.2 Déclarer les contraintes du projet

Dans `versions.tf` :

```hcl
terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

Cette configuration utilise une contrainte de version compatible avec la série majeure 6.x du provider AWS. Le fichier `.terraform.lock.hcl`, créé lors de l'initialisation, enregistre les versions sélectionnées pour le projet.

Pour un environnement d'entreprise, les versions doivent être validées selon la politique de maintenance et de compatibilité retenue.

## 3.3 Définir le réseau

Dans `main.tf` :

```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_subnet" "application" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnet_cidr
  availability_zone = var.availability_zone

  map_public_ip_on_launch = false

  tags = {
    Name        = "${var.project_name}-application-subnet"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  lifecycle {
    precondition {
      condition = (
        tonumber(split("/", var.subnet_cidr)[1]) >=
        tonumber(split("/", var.vpc_cidr)[1])
      )
      error_message = "Le préfixe du sous-réseau ne peut pas être plus large que celui du VPC."
    }
  }
}
```

La référence `aws_vpc.main.id` exprime que le sous-réseau dépend du VPC. Terraform détermine cet ordre à partir du graphe de dépendances.

La précondition présentée vérifie une relation entre les longueurs de préfixes IPv4, mais **elle ne suffit pas à démontrer que le CIDR du sous-réseau se trouve effectivement dans celui du VPC**. La validation complète des plages réseau est abordée plus loin.

## 3.4 Déclarer les variables

Dans `variables.tf` :

```hcl
variable "project_name" {
  description = "Préfixe des ressources du projet"
  type        = string

  validation {
    condition = can(regex(
      "^[a-z][a-z0-9-]{2,30}$",
      var.project_name
    ))
    error_message = "Le nom doit commencer par une lettre minuscule et utiliser uniquement des lettres, chiffres et tirets."
  }
}

variable "environment" {
  description = "Environnement de déploiement"
  type        = string

  validation {
    condition = contains(
      ["dev", "test", "prod"],
      var.environment
    )
    error_message = "L'environnement doit être dev, test ou prod."
  }
}

variable "aws_region" {
  description = "Région AWS cible"
  type        = string
}

variable "vpc_cidr" {
  description = "Bloc CIDR IPv4 du VPC"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr doit être un bloc CIDR IPv4 valide."
  }
}

variable "subnet_cidr" {
  description = "Bloc CIDR IPv4 du sous-réseau"
  type        = string

  validation {
    condition     = can(cidrnetmask(var.subnet_cidr))
    error_message = "subnet_cidr doit être un bloc CIDR IPv4 valide."
  }
}

variable "availability_zone" {
  description = "Zone de disponibilité cible"
  type        = string
}
```

La validation de `cidrnetmask` contrôle la forme du CIDR. Pour vérifier l'appartenance réelle d'un sous-réseau à un VPC, ajoutez un validateur adapté à cette règle ou utilisez des contrôles de plan capables de démontrer cette relation.

Il est important de distinguer une entrée syntaxiquement valide d'une entrée conforme à l'architecture prévue.

## 3.5 Fournir les valeurs de laboratoire

Dans `terraform.tfvars.example` :

```hcl
project_name      = "lab-reseau"
environment       = "dev"
aws_region        = "us-east-1"
vpc_cidr          = "10.20.0.0/16"
subnet_cidr       = "10.20.10.0/24"
availability_zone = "us-east-1a"
```

Copiez ce fichier en `terraform.tfvars` pour votre laboratoire, après avoir vérifié la région et la zone disponibles dans votre compte.

Ne versionnez pas de fichier contenant des secrets.

## 3.6 Définir les sorties

Dans `outputs.tf` :

```hcl
output "vpc_id" {
  description = "Identifiant du VPC créé"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "Identifiant du sous-réseau applicatif"
  value       = aws_subnet.application.id
}

output "vpc_cidr" {
  description = "Bloc CIDR du VPC"
  value       = aws_vpc.main.cidr_block
}
```

Les sorties fournissent les identifiants utiles au diagnostic et à d'autres modules. Elles ne remplacent pas un inventaire d'exploitation ou une politique de sécurité.

## 3.7 Comprendre le réseau représenté

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-labelledby="tf-mid-net-title tf-mid-net-desc">
  <title id="tf-mid-net-title">VPC et sous-réseau Terraform</title>
  <desc id="tf-mid-net-desc">Le VPC contient un sous-réseau applicatif. Le sous-réseau référence l'identifiant du VPC, ce qui crée une dépendance Terraform. Aucun accès Internet n'est représenté.</desc>
  <defs>
    <marker id="tf-mid-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .tm-vpc{fill:#102744;stroke:#60a5fa;stroke-width:2.5}
      .tm-sub{fill:#123126;stroke:#4ade80;stroke-width:2}
      .tm-title{font:700 17px Arial,sans-serif;fill:#f8fafc}
      .tm-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .tm-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tf-mid-arrow);animation:tm-dash 1.8s linear infinite}
      @keyframes tm-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">STRUCTURE DÉCLARÉE DANS TERRAFORM</text>
  <rect class="tm-vpc" x="65" y="70" width="830" height="230" rx="18"/>
  <text class="tm-title" x="95" y="102">VPC : 10.20.0.0/16</text>
  <text class="tm-text" x="95" y="125">Réseau virtuel géré par aws_vpc.main</text>
  <rect class="tm-sub" x="285" y="160" width="390" height="100" rx="14"/>
  <text class="tm-title" x="480" y="195" text-anchor="middle">Sous-réseau applicatif</text>
  <text class="tm-text" x="480" y="219" text-anchor="middle">10.20.10.0/24</text>
  <text class="tm-text" x="480" y="241" text-anchor="middle">Référence : aws_vpc.main.id</text>
  <path class="tm-flow" d="M165 137 V180 H275"/>
  <text class="tm-text" x="480" y="328" text-anchor="middle">Le schéma ne représente ni passerelle Internet, ni route, ni règle d'accès.</text>
  <text class="tm-text" x="480" y="347" text-anchor="middle">Un VPC et un sous-réseau ne suffisent pas à garantir une connectivité applicative.</text>
</svg>

---

# 4. Variables, validations et sorties

## 4.1 Pourquoi les validations sont importantes

Les variables permettent de réutiliser une configuration pour différentes valeurs d'entrée. Les validations évitent que des valeurs manifestement incorrectes passent silencieusement jusqu'au plan ou à l'application.

Exemples de contrôles utiles :

- format du nom ;
- format d'une adresse CIDR ;
- valeurs autorisées pour un environnement ;
- plage numérique ;
- cohérence entre plusieurs paramètres ;
- liste de régions ou de zones autorisées.

Une validation ne doit pas être plus permissive que la politique de l'organisation.

## 4.2 Vérifier réellement l'appartenance CIDR

La validation de deux CIDR individuellement ne démontre pas que le sous-réseau est contenu dans le VPC.

Pour une politique de réseau stricte, vérifiez notamment :

- les adresses de réseau ;
- les préfixes ;
- le recouvrement entre plages ;
- l'appartenance du sous-réseau à la plage du VPC ;
- le recouvrement avec les autres réseaux gérés ;
- les contraintes de l'infrastructure existante.

Ces contrôles peuvent être implémentés dans un validateur dédié, puis exécutés en CI avant l'appel à Terraform.

## 4.3 Sorties sensibles

N'exposez pas de secrets dans les sorties. Une sortie peut être affichée dans le terminal ou transmise à d'autres modules.

Pour les données sensibles, appliquez la politique appropriée et vérifiez leur traitement dans le state, le plan et les journaux.

---

# 5. Comprendre les dépendances

## 5.1 Dépendances implicites

La référence suivante établit une dépendance :

```hcl
vpc_id = aws_vpc.main.id
```

Terraform comprend que le sous-réseau a besoin de l'identifiant du VPC. Il ordonne les opérations de manière à tenir compte de cette relation.

## 5.2 Dépendances explicites

`depends_on` peut préciser une dépendance qui n'apparaît pas clairement dans les références d'attributs.

Exemple conceptuel :

```hcl
resource "exemple_service" "application" {
  # Configuration de démonstration uniquement.

  depends_on = [
    exemple_policy.network
  ]
}
```

Les types de ressources précédés de `exemple_` sont fictifs et ne sont pas exécutables.

Évitez d'ajouter `depends_on` systématiquement. Des dépendances inutiles rendent le graphe plus contraint et peuvent limiter les possibilités de planification parallèle.

## 5.3 Graphe de dépendances

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-labelledby="dep-title dep-desc">
  <title id="dep-title">Graphe de dépendances Terraform</title>
  <desc id="dep-desc">Le VPC doit être créé avant le sous-réseau qui référence son identifiant. Une route peut ensuite référencer le sous-réseau ou sa table de routage selon la configuration. Les flèches indiquent l'ordre des dépendances, pas une animation d'objets.</desc>
  <defs>
    <marker id="dep-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .dp-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .dp-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .dp-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .dp-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#dep-arrow);animation:dp-dash 1.8s linear infinite}
      @keyframes dp-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="328" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LE GRAPHE ORDONNE LES OPÉRATIONS</text>
  <rect class="dp-box" x="35" y="100" width="210" height="95" rx="12"/>
  <text class="dp-title" x="140" y="134" text-anchor="middle">VPC</text>
  <text class="dp-text" x="140" y="160" text-anchor="middle">aws_vpc.main</text>
  <rect class="dp-box" x="375" y="100" width="210" height="95" rx="12"/>
  <text class="dp-title" x="480" y="134" text-anchor="middle">Sous-réseau</text>
  <text class="dp-text" x="480" y="160" text-anchor="middle">aws_subnet.application</text>
  <rect class="dp-box" x="715" y="100" width="210" height="95" rx="12"/>
  <text class="dp-title" x="820" y="134" text-anchor="middle">Règle ou route</text>
  <text class="dp-text" x="820" y="160" text-anchor="middle">Ressource dépendante</text>
  <path class="dp-flow" d="M245 147 H367"/>
  <path class="dp-flow" d="M585 147 H707"/>
  <text class="dp-text" x="480" y="245" text-anchor="middle">Les références d'attributs construisent automatiquement une partie du graphe.</text>
  <text class="dp-text" x="480" y="269" text-anchor="middle">Utilisez depends_on seulement lorsque la dépendance nécessaire n'est pas implicite.</text>
</svg>

---

# 6. Créer des modules réutilisables

## 6.1 Pourquoi un module ?

Un module regroupe des ressources qui représentent un composant réutilisable de l'architecture.

Un module réseau peut fournir un VPC, un ou plusieurs sous-réseaux, ainsi que les valeurs utiles à ses consommateurs.

Un module de qualité doit présenter une interface simple et documentée. Il ne doit pas se limiter à envelopper inutilement une seule ressource sans apporter d'abstraction utile.

## 6.2 Exemple d'appel de module

Dans le module racine :

```hcl
module "network" {
  source = "./modules/network"

  project_name      = var.project_name
  environment       = var.environment
  vpc_cidr          = var.vpc_cidr
  subnet_cidr       = var.subnet_cidr
  availability_zone = var.availability_zone
}
```

Le module reçoit les valeurs nécessaires. Ses ressources internes doivent être déclarées dans `modules/network/`.

## 6.3 Le module enfant

Dans `modules/network/main.tf` :

```hcl
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_subnet" "application" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnet_cidr
  availability_zone = var.availability_zone

  map_public_ip_on_launch = false

  tags = {
    Name        = "${var.project_name}-application-subnet"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

Dans `modules/network/variables.tf` :

```hcl
variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "subnet_cidr" {
  type = string
}

variable "availability_zone" {
  type = string
}
```

Dans `modules/network/outputs.tf` :

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_id" {
  value = aws_subnet.application.id
}
```

Le module racine peut récupérer ces sorties avec :

```hcl
output "vpc_id" {
  value = module.network.vpc_id
}

output "subnet_id" {
  value = module.network.subnet_id
}
```

## 6.4 Versionner les modules

Les sources locales conviennent à un projet unique. Pour partager un module dans plusieurs dépôts, utilisez une source versionnée ou un registre interne selon les capacités de votre plateforme.

Fixez des versions compatibles et examinez les changements avant de mettre un module partagé à jour.

---

# 7. Data sources et ressources existantes

## 7.1 Ressource et data source

Une ressource Terraform gère le cycle de vie d'un objet.

Une data source lit les informations d'un objet existant ou d'une source externe, sans déclarer sa création comme responsabilité de ce bloc.

Exemple AWS :

```hcl
data "aws_availability_zones" "available" {
  state = "available"
}
```

Une sortie ou une ressource peut ensuite faire référence à cette data source.

Les data sources peuvent nécessiter des droits de lecture et des appels à l'API. Leur succès dépend de la connectivité, des permissions et de la disponibilité du service.

## 7.2 Ne pas confondre découverte et adoption

Découvrir une ressource existante ne signifie pas automatiquement que Terraform en prend le contrôle.

Pour gérer une ressource préexistante, il faut choisir la procédure adaptée : import, référence en lecture ou autre approche.

Une adoption mal planifiée peut créer des changements inattendus. Comparez la configuration voulue avec l'état existant avant de mettre la ressource sous gestion.

---

# 8. Tests Terraform

## 8.1 Le rôle des tests

Les tests peuvent vérifier le comportement de modules et de configurations.

Ils ne dispensent pas de la lecture du plan. Un test mal conçu peut réussir tout en laissant passer un problème qui n'a pas été couvert.

Terraform possède une commande dédiée aux fichiers de test. Les tests peuvent effectuer des opérations de planification ou d'application ; ceux qui appliquent réellement des ressources peuvent créer des dépenses et des objets persistants.

## 8.2 Exemple de test avec provider simulé

Terraform prend en charge les `mock_provider` dans les versions qui proposent cette fonction. L'exemple suivant utilise un test de plan avec un provider AWS simulé. Il sert à vérifier certaines propriétés de la configuration sans provisionner une VPC réelle.

Dans `tests/network.tftest.hcl` :

```hcl
mock_provider "aws" {}

run "network_configuration_is_coherent" {
  command = plan

  variables {
    project_name      = "lab-reseau"
    environment       = "dev"
    aws_region        = "us-east-1"
    vpc_cidr          = "10.20.0.0/16"
    subnet_cidr       = "10.20.10.0/24"
    availability_zone = "us-east-1a"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.20.0.0/16"
    error_message = "Le VPC doit utiliser le CIDR attendu."
  }

  assert {
    condition     = aws_subnet.application.cidr_block == "10.20.10.0/24"
    error_message = "Le sous-réseau doit utiliser le CIDR attendu."
  }
}
```

Ce test suppose que les ressources sont déclarées directement dans le module racine, comme dans la première configuration de ce cours. Si vous les déplacez dans `module.network`, adaptez les références d'assertion aux sorties du module.

## 8.3 Lancer les tests

```bash
terraform init
terraform validate
terraform test
```

Le test simulé vérifie certaines propriétés du plan. Il ne confirme pas la disponibilité des zones AWS, la validité fonctionnelle de toutes les règles ou l'absence de coûts dans un vrai déploiement.

N'utilisez pas de tests d'application réelle dans la CI sans prévoir le périmètre, les coûts, les autorisations et le nettoyage.

---

# 9. State, environnements et plans enregistrés

## 9.1 Environnements séparés

Les environnements de développement, test et production doivent être isolés de manière cohérente.

L'isolation peut inclure :

- des comptes ou projets séparés ;
- des rôles et identités distincts ;
- des backends et states séparés ;
- des variables différentes ;
- des permissions différentes ;
- des politiques de fusion et d'approbation différentes.

Un nom d'environnement dans une variable ne constitue pas, à lui seul, une séparation de sécurité.

## 9.2 State et collaboration

Le state relie les ressources de la configuration aux objets suivis dans l'infrastructure.

Pour une équipe, un backend distant avec contrôle d'accès et verrouillage lorsqu'il est disponible est généralement préférable à un state local partagé manuellement.

Le state peut contenir des données sensibles. Sa protection doit couvrir les droits d'accès, le chiffrement, les sauvegardes et les politiques de conservation.

## 9.3 Plans enregistrés

Un plan peut être enregistré :

```bash
terraform plan -out=network.tfplan
```

Puis inspecté :

```bash
terraform show network.tfplan
```

Si le plan a été examiné et autorisé, il peut être appliqué par son fichier :

```bash
terraform apply network.tfplan
```

Un plan enregistré permet d'appliquer les actions qui ont été préparées, mais il ne dispense pas de protéger le fichier. Les fichiers de plan peuvent contenir des informations sensibles et doivent être considérés comme des artefacts protégés.

## 9.4 Ne pas partager des states par simple copie de fichiers

Ne faites pas circuler un fichier `terraform.tfstate` entre administrateurs comme s'il s'agissait d'un document quelconque.

Pour une équipe, configurez un backend adapté. Utilisez les mécanismes de verrouillage lorsqu'ils sont pris en charge et ne supprimez jamais un verrou actif par réflexe.

---

# 10. Pipeline CI/CD

## 10.1 Ce que la CI doit vérifier

Une CI Terraform intermédiaire peut exécuter :

1. `terraform fmt -check` ;
2. `terraform init -backend=false` lorsque la configuration le permet ;
3. `terraform validate` ;
4. les validateurs complémentaires ;
5. les tests de modules ou de plans simulés ;
6. éventuellement un plan contrôlé avec les permissions prévues.

Les tests qui nécessitent des identifiants cloud doivent être séparés des validations purement syntaxiques.

## 10.2 Exemple de workflow de validation

Pour un dépôt GitHub, créez `.github/workflows/validate.yml` :

```yaml
name: Terraform validation

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v4
        with:
          terraform_version: "1.10.0"

      - name: Format check
        run: terraform fmt -check -recursive

      - name: Initialize without backend
        run: terraform init -backend=false

      - name: Validate configuration
        run: terraform validate

      - name: Run Terraform tests
        run: terraform test
```

Les numéros de version des actions et de Terraform sont des choix explicites pour l'exemple. Dans un dépôt professionnel, sélectionnez et maintenez des versions approuvées, mettez à jour les dépendances régulièrement et vérifiez la compatibilité avec vos modules.

La commande `terraform init -backend=false` évite d'initialiser le backend réel lors de cette validation. Elle ne supprime pas la nécessité de disposer des providers et modules requis pour le travail demandé.

## 10.3 Pourquoi ne pas appliquer automatiquement ?

La CI de validation ne doit pas recevoir des permissions de production uniquement parce qu'elle vérifie des fichiers.

Le déploiement peut constituer un workflow distinct, protégé par les permissions du dépôt, l'approbation requise et un plan examiné.

Les identifiants de production doivent être limités aux jobs autorisés et ne doivent pas être accessibles aux workflows exécutant du code non fiable.

---

# 11. Sécurité et contrôle des changements

## 11.1 Protection contre les destructions

Le bloc `lifecycle` propose notamment :

```hcl
lifecycle {
  prevent_destroy = true
}
```

Cette protection fait échouer certaines opérations qui tenteraient de détruire la ressource tant que cette règle est présente dans la configuration.

Elle ne constitue pas une garantie absolue : retirer la déclaration de la ressource peut contourner cette protection dans le contexte prévu par Terraform. Elle ne remplace pas une politique d'approbation, une sauvegarde ni une vérification du plan.

## 11.2 Examiner les changements destructifs

Avant un apply, vérifiez :

- les ressources à créer ;
- les mises à jour en place ;
- les remplacements ;
- les suppressions ;
- les modifications de réseau et de sécurité ;
- la cohérence avec le besoin ;
- le périmètre réel ;
- les conditions de retour arrière.

Les modifications de CIDR, de routes ou de filtrage peuvent affecter fortement l'infrastructure. Un plan doit être interprété selon l'architecture et le service concerné.

## 11.3 Git et revue

Un changement doit être versionné et relu avant sa promotion.

La revue doit rechercher les valeurs codées en dur, les permissions excessives, les suppressions inattendues, les règles d'accès trop ouvertes et les changements qui sortent du périmètre approuvé.

Un pipeline vert n'annule pas la nécessité de vérifier ce que le plan va réellement faire.

---

# 12. Atelier pratique

## Situation

Vous devez définir un VPC de laboratoire et un sous-réseau applicatif, puis les valider automatiquement avant leur création.

### Étape A — Créer une branche

```bash
git switch -c feature/reseau-laboratoire
```

### Étape B — Écrire les fichiers

Ajoutez `versions.tf`, `main.tf`, `variables.tf`, `outputs.tf` et un fichier de valeurs de laboratoire à partir des exemples du cours.

### Étape C — Contrôler localement

```bash
terraform fmt -recursive
terraform init
terraform validate
terraform test
```

Vérifiez que les contraintes et les tests correspondent à la configuration réellement présente.

### Étape D — Examiner un plan

Dans un compte de laboratoire autorisé :

```bash
terraform plan -out=network.tfplan
terraform show network.tfplan
```

Ne poursuivez que si les ressources et les paramètres correspondent au besoin. Protégez le fichier de plan.

### Étape E — Vérifier le périmètre

Confirmez que le projet cible le bon compte et la bonne région. Les identifiants doivent avoir les permissions nécessaires et pas davantage.

### Étape F — Appliquer si autorisé

```bash
terraform apply network.tfplan
```

Vérifiez ensuite les identifiants produits, les paramètres des ressources et la connectivité attendue.

### Étape G — Nettoyer le laboratoire

Lorsque le laboratoire n'est plus nécessaire :

```bash
terraform plan -destroy
```

Examinez le plan de destruction et utilisez la procédure de nettoyage approuvée.

**Attention :** la destruction d'une infrastructure réelle peut interrompre un service. Ne la faites jamais sur un environnement partagé ou de production sans autorisation.

---

# 13. Dépannage

## 13.1 Terraform signale une contrainte de CIDR invalide

Vérifiez la notation du préfixe et la plage utilisée. Un CIDR individuellement valide peut néanmoins être incompatible avec le réseau parent.

## 13.2 Le provider ne peut pas se connecter au service cloud

Contrôlez l'identité utilisée, les permissions, la région, la connectivité et les limites du compte.

## 13.3 Le plan propose de remplacer une ressource

Recherchez l'attribut qui force le remplacement dans la documentation du provider. Évaluez les conséquences sur les dépendances, la disponibilité et les données associées.

## 13.4 Les tests réussissent mais l'application échoue

Les tests vérifient uniquement le comportement couvert. Les permissions, quotas, contraintes du service, collisions d'adressage ou conditions externes peuvent encore empêcher la création.

## 13.5 Le state distant est verrouillé

Vérifiez si une opération est toujours active avant de tenter de récupérer un verrou. Le forçage d'un déverrouillage alors qu'un autre opérateur travaille peut entraîner des conflits et une corruption de l'état suivi.

---

# 14. Évaluation corrigée

## Questions

1. Pourquoi utiliser un module ?
2. Quelle différence existe entre une ressource et une data source ?
3. Pourquoi une validation CIDR simple ne suffit-elle pas ?
4. À quoi sert le graphe de dépendances ?
5. Quelle différence existe entre `terraform validate` et `terraform plan` ?
6. Quel est l'intérêt des tests avec provider simulé ?
7. Pourquoi protéger un plan enregistré ?
8. Pourquoi séparer le state des différents environnements ?
9. Pourquoi `prevent_destroy` n'est-il pas une protection complète ?
10. Pourquoi ne pas donner les droits de production à tous les jobs CI ?

## Corrigé

1. À encapsuler un composant d'architecture réutilisable avec une interface explicite.
2. Une ressource est gérée ; une data source lit les informations d'un objet existant ou d'une source externe.
3. Parce qu'elle ne vérifie pas nécessairement l'inclusion dans le réseau parent ni l'absence de chevauchement.
4. À déterminer l'ordre des opérations selon les relations entre ressources.
5. `validate` vérifie la cohérence de la configuration ; `plan` calcule les changements proposés en tenant compte de l'état et des données du provider.
6. À valider certaines propriétés de la configuration sans provisionner de ressources réelles.
7. Parce qu'il peut contenir des informations sensibles et représente un ensemble d'actions préparées.
8. Pour isoler les ressources, les autorisations, les changements et la coordination.
9. Parce que son effet dépend de la déclaration maintenue et qu'il ne remplace pas les protections organisationnelles.
10. Pour limiter les effets d'un workflow compromis, d'un code non fiable ou d'une erreur de configuration.

---

# 15. Préparation du niveau expert

Le niveau expert abordera :

- les backends distants et le verrouillage ;
- les migrations de state ;
- les plans immuables et leur promotion ;
- les politiques de sécurité et la validation des plans ;
- les opérations d'importation et de refactorisation ;
- la détection des dérives ;
- la gouvernance multi-environnements ;
- l'utilisation avancée des secrets ;
- les contrôles avant et après déploiement ;
- les stratégies d'approbation et de récupération.

Le niveau intermédiaire apprend à structurer et tester une infrastructure réelle. Le niveau expert organisera la livraison avec des états protégés, des règles de sécurité et des procédures de changement contrôlées.

---

## Références officielles

- Langage Terraform : https://developer.hashicorp.com/terraform/language
- Providers et ressources AWS : https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Ressource VPC : https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc
- Ressource subnet : https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet
- Modules : https://developer.hashicorp.com/terraform/language/modules/develop
- Tests Terraform : https://developer.hashicorp.com/terraform/language/tests
- Contraintes de versions : https://developer.hashicorp.com/terraform/language/expressions/version-constraints
- Meta-arguments : https://developer.hashicorp.com/terraform/language/meta-arguments

**Fichier :** `terraform-intermediaire.md`  
**Niveau :** Intermédiaire  
**Fin du cours**
