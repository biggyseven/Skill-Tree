# Infrastructure as Code avec Terraform

## 1. Place de ce cours dans le parcours

Ce cours constitue le **niveau intermédiaire** du parcours Infrastructure as Code. Il ne reprend pas tout le contenu d'une initiation à Terraform : il s'appuie sur les notions déjà acquises pour apprendre à concevoir, organiser, sécuriser et automatiser une infrastructure maintenable en équipe.

La progression générale est la suivante :

```text
NIVEAU DÉBUTANT
    |
    |-- Comprendre Terraform et HCL
    |-- Déclarer des ressources
    |-- Utiliser variables, outputs et providers
    |-- Exécuter init, plan, apply et destroy
    |
    v
NIVEAU INTERMÉDIAIRE : CE COURS
    |
    |-- Créer des modules réutilisables
    |-- Organiser les environnements
    |-- Partager et protéger l'état Terraform
    |-- Importer et refactoriser des ressources
    |-- Tester et valider les configurations
    |-- Intégrer Terraform à Git et à la CI/CD
    |-- Sécuriser les identités, secrets et pipelines
    |
    v
NIVEAU EXPERT
    |
    |-- Gouvernance à grande échelle
    |-- Architectures multi-comptes et multi-régions
    |-- Modules et plateformes internes
    |-- Politiques de conformité automatisées
    |-- Gestion avancée du drift et des déploiements
    |-- Stratégies de migration et de résilience
```

Ce niveau se connecte également aux autres cours du parcours :

- **Git et gestion de versions** : historiser les changements d'infrastructure, travailler avec des branches et examiner les modifications avant fusion.
- **CI/CD avec GitHub Actions et GitLab CI** : automatiser les contrôles, plans et déploiements Terraform.
- **Docker et sécurité des conteneurs** : comprendre les exigences de sécurité de l'environnement qui héberge les outils d'automatisation.
- **Kubernetes : réseau et stockage** : préparer les infrastructures réseau et stockage nécessaires aux plateformes Kubernetes.

Terraform décrit et gère principalement l'infrastructure sous-jacente. Kubernetes gère ensuite les ressources applicatives du cluster. Leurs responsabilités sont complémentaires, mais doivent être clairement séparées.

## 2. Objectifs pédagogiques

À la fin de ce cours, il faut être capable de :

1. Structurer un dépôt Terraform pour plusieurs environnements.
2. Créer des modules réutilisables avec des interfaces explicites.
3. Manipuler des collections, `for_each`, `for` expressions et `dynamic` blocks.
4. Gérer les dépendances entre ressources sans multiplier les dépendances explicites.
5. Configurer un backend distant et comprendre les verrous d'état.
6. Protéger l'état, les identifiants et les secrets.
7. Importer des ressources existantes sans les recréer.
8. Réorganiser une configuration avec des blocs `moved`.
9. Tester, valider et contrôler une configuration avant déploiement.
10. Concevoir un pipeline CI/CD d'infrastructure avec des permissions minimales.
11. Diagnostiquer les erreurs de planification, d'état, d'authentification et de dérive.

## 3. Prérequis et préparation de l'environnement

Les notions suivantes sont considérées comme connues :

- La syntaxe HCL et les blocs `resource`, `data`, `variable`, `output` et `provider`.
- Le rôle de `terraform init`, `terraform plan`, `terraform apply` et `terraform destroy`.
- Le fonctionnement des commits, branches et pull requests.
- Les principes de base d'un pipeline CI/CD.
- Les notions d'identité, d'autorisation, de réseau et de stockage.

### 3.1 Outils nécessaires

Préparer les outils suivants :

- Terraform CLI, dans une version compatible avec le projet.
- Git.
- Un éditeur de code adapté à HCL.
- Un compte ou environnement de test auprès du fournisseur utilisé si les exercices créent des ressources cloud.
- Des identifiants temporaires ou une identité fédérée pour l'authentification.
- Un outil de vérification de code comme TFLint ou un scanner IaC complémentaire pour les exercices avancés.

Vérifier l'installation :

```bash
terraform version
git --version
terraform -help
```

Une infrastructure réelle peut engendrer des frais. Les exemples AWS de ce cours illustrent des ressources concrètes et nécessitent un compte autorisé. La partie pratique principale doit être réalisée dans un environnement de test.

### 3.2 Principes de travail

À partir de ce niveau, l'objectif n'est plus seulement de faire fonctionner une configuration.

Une configuration professionnelle doit aussi être :

- reproductible ;
- compréhensible par un autre ingénieur ;
- testable ;
- sécurisée ;
- réutilisable ;
- contrôlable par Git ;
- adaptée au travail en équipe ;
- accompagnée d'une procédure de récupération en cas d'incident.

Le code Terraform fait partie du système de production. Il doit être examiné avec autant de sérieux que le code applicatif.

## 4. Organisation d'un dépôt Terraform

Une configuration de quelques ressources peut tenir dans un seul fichier. Cette approche devient difficile à maintenir quand plusieurs environnements, modules et équipes interviennent.

Une organisation possible :

```text
infrastructure/
|
|-- README.md
|-- .gitignore
|-- .terraform.lock.hcl
|
|-- modules/
|   |
|   |-- network/
|   |   |-- versions.tf
|   |   |-- main.tf
|   |   |-- variables.tf
|   |   |-- outputs.tf
|   |   |-- README.md
|   |
|   |-- storage/
|   |   |-- versions.tf
|   |   |-- main.tf
|   |   |-- variables.tf
|   |   |-- outputs.tf
|   |
|   |-- compute/
|       |-- versions.tf
|       |-- main.tf
|       |-- variables.tf
|       |-- outputs.tf
|
|-- environments/
|   |
|   |-- dev.tfvars
|   |-- staging.tfvars
|   |-- prod.tfvars
|
|-- tests/
|   |-- network.tftest.hcl
|
|-- .github/
    |-- workflows/
        |-- terraform.yml
```

Cette structure est une proposition, pas une obligation universelle.

Les répertoires `modules/` contiennent les composants réutilisables. Les fichiers d'environnement contiennent les valeurs propres aux différents déploiements.

Les configurations racines peuvent rester dans le même dépôt, ou être séparées dans plusieurs dépôts selon les besoins de gouvernance et les permissions.

### 4.1 Séparer le code des valeurs d'environnement

Une même configuration peut décrire plusieurs infrastructures sans copier tout le code.

Par exemple :

```text
                     Code Terraform
                           |
              +------------+------------+
              |            |            |
              v            v            v
           DEV          STAGING        PROD
              |            |            |
           Petit         Moyen        Dimensionné
           réseau        réseau      pour production
```

Le code reste commun, tandis que les valeurs diffèrent : plages CIDR, noms, tailles, régions ou paramètres de capacité.

Attention : des fichiers `.tfvars` ne constituent pas une frontière de sécurité. Pour séparer réellement les privilèges, les états, les identités et les droits d'accès, il faut également organiser les backends et les rôles d'exécution.

### 4.2 Exclure les fichiers temporaires et sensibles

Exemple de `.gitignore` :

```gitignore
# Répertoire de travail Terraform
.terraform/

# États locaux et sauvegardes d'état
terraform.tfstate
terraform.tfstate.*
*.tfstate
*.tfstate.*

# Plans binaires pouvant contenir des informations sensibles
*.tfplan
tfplan

# Fichiers de variables contenant potentiellement des secrets
*.secret.tfvars
secrets.auto.tfvars

# Fichiers locaux
crash.log
crash.*.log

# Surcharges locales
override.tf
override.tf.json
*_override.tf
*_override.tf.json
```

Le fichier `.terraform.lock.hcl` doit normalement être versionné. Il permet de conserver les versions sélectionnées des providers, ainsi que leurs sommes de contrôle.

Les règles `.gitignore` ne retirent pas un fichier déjà suivi par Git. Un secret déjà commité doit être considéré comme potentiellement compromis.

## 5. Providers et reproductibilité

Un provider est le composant qui permet à Terraform de communiquer avec une API externe : fournisseur cloud, plateforme SaaS, hyperviseur ou autre système.

La configuration doit définir les contraintes compatibles avec le projet.

Exemple :

```hcl
terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}
```

Cette contrainte de version du provider est illustrative. Dans un projet réel, la plage doit être choisie et testée par rapport à la version de Terraform et aux fonctionnalités effectivement utilisées.

### 5.1 Trois mécanismes différents

| Élément | Rôle |
|---|---|
| `required_version` | Définir les versions de Terraform CLI compatibles. |
| `required_providers` | Déclarer la source et les versions acceptables des providers. |
| `.terraform.lock.hcl` | Enregistrer les versions de providers sélectionnées et leurs sommes de contrôle. |

La contrainte exprime une plage acceptable. Le fichier de verrouillage permet de reproduire une sélection précise dans cette plage.

### 5.2 Initialiser et mettre à jour avec prudence

Initialisation normale :

```bash
terraform init
```

Vérifier le format du code :

```bash
terraform fmt -check -recursive
```

Valider la configuration :

```bash
terraform validate
```

Mettre à jour les providers de façon contrôlée :

```bash
terraform init -upgrade
```

La commande `-upgrade` peut sélectionner de nouvelles versions compatibles. Elle ne doit pas être exécutée machinalement sur un pipeline de production.

La procédure recommandée est :

1. créer une branche dédiée ;
2. mettre à jour les contraintes ou les providers concernés ;
3. exécuter l'initialisation avec mise à jour ;
4. examiner le changement du fichier de verrouillage ;
5. exécuter les validations et tests ;
6. préparer un plan d'infrastructure ;
7. fusionner seulement après examen.

Le fichier `.terraform.lock.hcl` n'est pas un verrou de l'état distant. Il verrouille les dépendances des providers ; ces deux mécanismes répondent à des problèmes différents.

## 6. Maîtriser les expressions Terraform

Le niveau intermédiaire doit savoir transformer une configuration répétitive en une déclaration plus concise sans rendre le code opaque.

### 6.1 Variables fortement typées

Éviter de faire dépendre les ressources d'une multitude de chaînes non validées.

Exemple :

```hcl
variable "environment" {
  description = "Environnement cible"
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "L'environnement doit être dev, staging ou prod."
  }
}
```

La validation bloque une valeur incorrecte avant la création des ressources.

Les types composés servent à exprimer une structure de données :

```hcl
variable "subnets" {
  description = "Sous-réseaux à créer"
  type = map(object({
    cidr_block        = string
    availability_zone = string
    public            = bool
  }))
}
```

Une valeur correspondante :

```hcl
subnets = {
  public_a = {
    cidr_block        = "10.20.1.0/24"
    availability_zone = "eu-west-3a"
    public            = true
  }

  private_a = {
    cidr_block        = "10.20.11.0/24"
    availability_zone = "eu-west-3a"
    public            = false
  }
}
```

Chaque sous-réseau possède une clé stable, un CIDR, une zone de disponibilité et un attribut indiquant son intention.

### 6.2 `for_each` plutôt que des duplications

Une mauvaise approche consiste à écrire une ressource complète par sous-réseau.

Une approche réutilisable :

```hcl
resource "aws_subnet" "this" {
  for_each = var.subnets

  vpc_id            = aws_vpc.this.id
  cidr_block         = each.value.cidr_block
  availability_zone  = each.value.availability_zone
  map_public_ip_on_launch = each.value.public

  tags = {
    Name = "${var.name}-${each.key}"
  }
}
```

Terraform crée une instance par entrée de la map.

Les adresses des ressources prennent cette forme :

```text
aws_subnet.this["public_a"]
aws_subnet.this["private_a"]
```

Chaque clé devient une partie de l'adresse Terraform de l'instance.

Pour une collection représentant des objets nommés et stables, `for_each` est généralement plus lisible que `count`.

### 6.3 Pourquoi les clés sont importantes

Avec `count`, les instances sont souvent adressées par indice :

```text
aws_instance.server[0]
aws_instance.server[1]
aws_instance.server[2]
```

Si la liste change de position, Terraform peut interpréter le changement comme une modification de correspondance entre indices et objets.

Avec `for_each` :

```text
aws_instance.server["api"]
aws_instance.server["worker"]
aws_instance.server["monitoring"]
```

Les noms représentent directement les objets.

Cela ne supprime pas tous les risques de remplacement, mais rend les changements structurels plus explicites.

### 6.4 Compréhensions et transformations

Exemple :

```hcl
variable "services" {
  type = map(object({
    port    = number
    enabled = bool
  }))
}

locals {
  enabled_services = {
    for name, service in var.services :
    name => service
    if service.enabled
  }

  service_ports = {
    for name, service in local.enabled_services :
    name => service.port
  }
}
```

Les expressions construisent une nouvelle map en conservant uniquement les services activés, puis produisent une map de ports.

Autres opérations utiles :

```hcl
locals {
  normalized_name = lower(replace(var.project_name, " ", "-"))

  common_tags = {
    ManagedBy   = "Terraform"
    Environment = var.environment
    Project     = local.normalized_name
  }

  resource_tags = merge(
    local.common_tags,
    var.extra_tags
  )
}
```

Attention à l'ordre des arguments de `merge` : en cas de clés identiques, la dernière valeur l'emporte.

Les tags supplémentaires peuvent donc remplacer des valeurs par défaut. Il faut déterminer explicitement quelles clés sont autorisées à être remplacées.

### 6.5 Dépendances implicites

Terraform construit un graphe de dépendances à partir des références entre ressources.

```hcl
resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr
}

resource "aws_subnet" "this" {
  vpc_id     = aws_vpc.this.id
  cidr_block = var.subnet_cidr
}
```

Le sous-réseau utilise l'identifiant du VPC. Terraform sait donc que le VPC doit exister avant de créer le sous-réseau.

Ajouter `depends_on` systématiquement ne rend pas le code plus sûr. Utiliser ce mécanisme uniquement lorsque la relation de dépendance ne peut pas être exprimée suffisamment clairement par les références normales.

## 7. Concevoir des modules réutilisables

Un module Terraform regroupe des ressources et expose une interface stable.

Le module racine est la configuration exécutée directement. Un module enfant est appelé depuis un autre module.

```text
Configuration racine
        |
        +---- module.network
        |         |
        |         +---- VPC
        |         +---- Sous-réseaux
        |         +---- Routage
        |
        +---- module.storage
        |         |
        |         +---- Stockage
        |
        +---- module.compute
                  |
                  +---- Machines ou services
```

### 7.1 Responsabilité unique

Un module réseau devrait gérer des composants réseau cohérents. Il ne devrait pas également déployer des applications, créer tous les comptes d'utilisateurs et administrer les bases de données sans séparation claire.

Le découpage doit rendre les composants compréhensibles et testables.

Un module trop petit peut n'ajouter aucune abstraction utile. Un module trop grand devient difficile à faire évoluer.

Le bon découpage dépend du cycle de vie, de la réutilisation et des responsabilités opérationnelles des ressources.

### 7.2 Interface d'un module

Un module bien conçu expose :

- des variables d'entrée typées ;
- des validations explicites ;
- des outputs utiles ;
- des valeurs par défaut raisonnables ;
- des conventions de nommage ;
- des tags cohérents ;
- des préconditions lorsque nécessaire ;
- une documentation des limites et hypothèses.

Exemple d'appel depuis une configuration racine :

```hcl
module "network" {
  source = "./modules/network"

  name     = var.project_name
  vpc_cidr = var.vpc_cidr
  subnets  = var.subnets

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

L'utilisation d'un module n'annule pas les règles de dépendance Terraform : les outputs et références continuent de contribuer au graphe de dépendances.

### 7.3 Sources de modules

Exemple d'utilisation d'un module local :

```hcl
module "network" {
  source = "./modules/network"
}
```

Exemple d'un module versionné provenant d'un registre :

```hcl
module "example" {
  source  = "organisation/nom-du-module/fournisseur"
  version = "1.2.0"
}
```

Le second exemple représente la forme générale d'une source de module depuis le registre Terraform. La source réelle doit correspondre à un module publié et à une version existante.

Pour les modules distants, il faut examiner :

- la provenance ;
- les versions publiées ;
- la documentation ;
- les permissions nécessaires ;
- le contenu des scripts et ressources ;
- les changements entre versions.

Un module tiers exécuté avec des identifiants cloud puissants fait partie de la chaîne de confiance du déploiement.

## 8. Atelier principal : créer un module réseau AWS

Cet atelier construit un module réseau réutilisable comprenant :

- un VPC ;
- plusieurs sous-réseaux ;
- une passerelle Internet lorsqu'il existe des sous-réseaux publics ;
- une table de routage publique ;
- les associations de routage des sous-réseaux publics ;
- des outputs réutilisables par d'autres modules.

Les sous-réseaux privés n'ont pas de route Internet sortante via une passerelle NAT dans cet exemple. Ajouter un NAT Gateway relève d'une conception distincte et peut engendrer des coûts. Le caractère public d'un sous-réseau dépend notamment de ses routes, et non simplement du nom ou du réglage d'attribution automatique d'adresses IP.

### 8.1 Arborescence de l'atelier

```text
infrastructure/
|
|-- versions.tf
|-- providers.tf
|-- variables.tf
|-- main.tf
|-- outputs.tf
|
|-- environments/
|   |-- dev.tfvars
|   |-- prod.tfvars
|
|-- modules/
    |-- network/
        |-- versions.tf
        |-- variables.tf
        |-- main.tf
        |-- outputs.tf
```

### 8.2 Versionnement de la configuration racine

Fichier `versions.tf` :

```hcl
terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}
```

Cette plage est volontairement large pour l'exemple. Dans un vrai dépôt, les versions choisies doivent être testées et le fichier `.terraform.lock.hcl` doit être versionné.

### 8.3 Provider AWS

Fichier `providers.tf` :

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Project   = var.project_name
    }
  }
}
```

Ne pas stocker directement des clés AWS dans ce fichier.

L'authentification peut utiliser un profil local pour le développement, une identité de rôle dans le cloud ou une fédération OIDC pour un pipeline compatible.

### 8.4 Variables de la configuration racine

Fichier `variables.tf` :

```hcl
variable "aws_region" {
  description = "Région AWS cible"
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Nom court du projet"
  type        = string

  validation {
    condition     = length(var.project_name) >= 3
    error_message = "Le nom du projet doit contenir au moins 3 caractères."
  }
}

variable "environment" {
  description = "Environnement cible"
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Valeurs autorisées : dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "Plage IPv4 du VPC"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Le CIDR du VPC doit être une plage IPv4 valide."
  }
}

variable "subnets" {
  description = "Sous-réseaux à créer"

  type = map(object({
    cidr_block        = string
    availability_zone = string
    public            = bool
  }))
}
```

Une validation de syntaxe CIDR ne vérifie pas à elle seule que les plages sont cohérentes entre elles ou acceptées par le fournisseur. Ces contraintes doivent aussi être contrôlées.

### 8.5 Appeler le module réseau

Fichier `main.tf` :

```hcl
module "network" {
  source = "./modules/network"

  name     = "${var.project_name}-${var.environment}"
  vpc_cidr = var.vpc_cidr
  subnets  = var.subnets

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
```

Le module reçoit les valeurs dont il a besoin. Il ne doit pas dépendre implicitement de fichiers d'environnement ou de valeurs locales cachées.

### 8.6 Outputs de la configuration racine

Fichier `outputs.tf` :

```hcl
output "vpc_id" {
  description = "Identifiant du VPC"
  value       = module.network.vpc_id
}

output "subnet_ids" {
  description = "Identifiants des sous-réseaux"
  value       = module.network.subnet_ids
}

output "public_subnet_ids" {
  description = "Identifiants des sous-réseaux publics"
  value       = module.network.public_subnet_ids
}
```

Un autre module peut consommer directement ces outputs si la configuration lui transmet les valeurs correspondantes.

Les outputs ne doivent pas exposer inutilement des secrets, des clés ou d'autres données sensibles.

### 8.7 Déclarer les dépendances du module

Fichier `modules/network/versions.tf` :

```hcl
terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}
```

Le module enfant déclare sa dépendance au provider. Dans ce cas simple, il utilise la configuration du provider AWS transmise par le module racine.

### 8.8 Variables du module

Fichier `modules/network/variables.tf` :

```hcl
variable "name" {
  description = "Préfixe de nommage du réseau"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR du VPC"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Le CIDR fourni doit être valide."
  }
}

variable "subnets" {
  description = "Sous-réseaux du VPC"

  type = map(object({
    cidr_block        = string
    availability_zone = string
    public            = bool
  }))

  validation {
    condition = alltrue([
      for subnet in values(var.subnets) :
      can(cidrhost(subnet.cidr_block, 0))
    ])

    error_message = "Chaque sous-réseau doit définir un CIDR IPv4 valide."
  }
}

variable "tags" {
  description = "Tags supplémentaires"
  type        = map(string)
  default     = {}
}
```

### 8.9 Ressources du module

Fichier `modules/network/main.tf` :

```hcl
locals {
  public_subnets = {
    for name, subnet in var.subnets :
    name => subnet
    if subnet.public
  }

  has_public_subnets = length(local.public_subnets) > 0
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-vpc"
    }
  )
}

resource "aws_subnet" "this" {
  for_each = var.subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = each.value.public

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-${each.key}"
      Tier = each.value.public ? "public" : "private"
    }
  )
}

resource "aws_internet_gateway" "this" {
  count = local.has_public_subnets ? 1 : 0

  vpc_id = aws_vpc.this.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-igw"
    }
  )
}

resource "aws_route_table" "public" {
  count = local.has_public_subnets ? 1 : 0

  vpc_id = aws_vpc.this.id

  tags = merge(
    var.tags,
    {
      Name = "${var.name}-public"
    }
  )
}

resource "aws_route" "public_default" {
  count = local.has_public_subnets ? 1 : 0

  route_table_id         = aws_route_table.public[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this[0].id
}

resource "aws_route_table_association" "public" {
  for_each = local.public_subnets

  subnet_id      = aws_subnet.this[each.key].id
  route_table_id = aws_route_table.public[0].id
}
```

Les références entre ressources créent les dépendances nécessaires. La table de routage publique n'est créée que si au moins un sous-réseau public est demandé.

Cette architecture partage une table de routage publique entre les sous-réseaux publics. Dans une architecture de production multi-AZ, les routes, les zones de disponibilité, la sortie Internet et les exigences de résilience doivent faire l'objet d'une conception explicite.

### 8.10 Outputs du module

Fichier `modules/network/outputs.tf` :

```hcl
output "vpc_id" {
  description = "Identifiant du VPC"
  value       = aws_vpc.this.id
}

output "subnet_ids" {
  description = "Identifiants indexés des sous-réseaux"
  value = {
    for name, subnet in aws_subnet.this :
    name => subnet.id
  }
}

output "public_subnet_ids" {
  description = "Liste des sous-réseaux publics"
  value = [
    for name, subnet in aws_subnet.this :
    subnet.id
    if var.subnets[name].public
  ]
}
```

### 8.11 Valeurs pour le développement

Fichier `environments/dev.tfvars` :

```hcl
aws_region   = "eu-west-3"
project_name = "atelier-iac"
environment  = "dev"
vpc_cidr     = "10.20.0.0/16"

subnets = {
  public_a = {
    cidr_block        = "10.20.1.0/24"
    availability_zone = "eu-west-3a"
    public            = true
  }

  private_a = {
    cidr_block        = "10.20.11.0/24"
    availability_zone = "eu-west-3a"
    public            = false
  }

  private_b = {
    cidr_block        = "10.20.12.0/24"
    availability_zone = "eu-west-3b"
    public            = false
  }
}
```

Les zones de disponibilité disponibles dépendent de la région et de la configuration du compte. Vérifier leur disponibilité avant d'appliquer la configuration.

Une configuration de production doit posséder des plages CIDR, un nombre de zones de disponibilité, un routage, des règles de filtrage et des paramètres de résilience adaptés. Ne pas réutiliser aveuglément les valeurs de développement.

### 8.12 Vérifier et planifier

À la racine du projet :

```bash
terraform fmt -recursive
terraform init
terraform validate

terraform plan \
  -var-file="environments/dev.tfvars" \
  -out="dev.tfplan"
```

Examiner le plan. Vérifier au minimum :

- le nombre de ressources à créer ;
- les plages réseau ;
- les zones de disponibilité ;
- les routes vers la passerelle Internet ;
- les ressources conditionnelles ;
- les éventuels remplacements ou destructions.

Appliquer uniquement après cette vérification :

```bash
terraform apply dev.tfplan
```

Afficher les outputs :

```bash
terraform output
terraform output vpc_id
terraform output -json subnet_ids
```

Après les exercices, détruire les ressources temporaires si elles ne doivent pas être conservées :

```bash
terraform plan -destroy \
  -var-file="environments/dev.tfvars"
```

Après examen du plan de destruction :

```bash
terraform destroy \
  -var-file="environments/dev.tfvars"
```

Ne jamais lancer une destruction sur une infrastructure partagée ou de production sans procédure de validation et d'autorisation adaptée.

## 9. Gestion des environnements

L'utilisation d'une seule configuration pour plusieurs environnements réduit la duplication, mais ne suffit pas à isoler leurs ressources.

### 9.1 Fichiers de variables

La sélection d'un environnement peut être faite explicitement :

```bash
terraform plan -var-file="environments/dev.tfvars"
```

Ou :

```bash
terraform plan -var-file="environments/prod.tfvars"
```

Éviter de changer les valeurs de production à la main avant un déploiement. Les paramètres doivent être traçables, revus et reliés à une version précise du code.

### 9.2 Workspaces Terraform CLI

Terraform propose des workspaces qui associent plusieurs états à une même configuration.

Commandes :

```bash
terraform workspace list
terraform workspace show
terraform workspace new dev
terraform workspace select dev
```

Les workspaces peuvent convenir lorsque la même configuration doit être déployée plusieurs fois avec une structure comparable.

Ils ne constituent pas, à eux seuls, une frontière de sécurité. Ils ne remplacent pas des identités différentes, des permissions séparées et une isolation explicite des états.

### 9.3 Quand séparer les configurations racines

Il est préférable d'utiliser des configurations et états distincts lorsque les environnements ont :

- des équipes responsables différentes ;
- des permissions ou identités différentes ;
- des cycles de déploiement différents ;
- des exigences de conformité distinctes ;
- des risques de destruction très différents ;
- des fournisseurs ou régions sans rapport.

Exemple :

```text
infrastructure/
|
|-- platform/
|   |-- main.tf
|   |-- versions.tf
|   |-- variables.tf
|
|-- environments/
    |
    |-- dev/
    |   |-- main.tf
    |   |-- backend.tf
    |   |-- dev.tfvars
    |
    |-- staging/
    |   |-- main.tf
    |   |-- backend.tf
    |   |-- staging.tfvars
    |
    |-- prod/
        |-- main.tf
        |-- backend.tf
        |-- prod.tfvars
```

Le répertoire partagé `platform/` est ici un composant de conception. Chaque environnement doit tout de même disposer d'un état, d'un backend et d'une procédure d'accès correctement définis.

## 10. Comprendre l'état Terraform

L'état, ou *state*, relie les déclarations Terraform aux objets réels gérés par le fournisseur.

```text
CONFIGURATION HCL
        |
        v
    PLANIFICATION <------ État Terraform
        |                       ^
        |                       |
        v                       |
    Fournisseur/API  ----------+
        |
        v
  Infrastructure réelle
```

Terraform utilise l'état pour reconnaître les ressources qu'il gère, leurs adresses et les informations nécessaires au suivi de leur cycle de vie.

L'état n'est pas simplement un cache. Le modifier sans comprendre ses conséquences peut provoquer des créations, des remplacements ou des destructions inattendus.

### 10.1 Ce que l'état peut contenir

Selon les ressources et les providers :

- identifiants de ressources ;
- attributs calculés ;
- informations de connexion ;
- éléments de configuration ;
- valeurs marquées comme sensibles ;
- métadonnées nécessaires au suivi.

Il faut donc traiter l'état comme une donnée sensible, même lorsqu'aucun mot de passe n'est volontairement écrit dans le code.

### 10.2 Pourquoi ne pas partager un état local par fichier

Deux ingénieurs utilisant chacun une copie locale peuvent travailler à partir d'états différents. Les fichiers peuvent diverger ou être écrasés.

Pour le travail en équipe, il faut un backend distant approprié ou une plateforme de collaboration qui centralise l'état et organise les opérations.

La solution doit également prévoir :

- des permissions minimales ;
- le chiffrement en transit et au repos ;
- la sauvegarde ou la récupération ;
- la protection des versions ;
- le verrouillage lorsque le backend le prend en charge ;
- le contrôle des accès en lecture.

## 11. Backends distants et verrouillage

Un backend détermine où l'état est stocké et, selon le type choisi, comment il est verrouillé.

Le verrouillage empêche plusieurs opérations concurrentes d'écrire simultanément dans le même état lorsqu'il est pris en charge par le backend.

### 11.1 Exemple de backend S3

Fichier `backend.tf` :

```hcl
terraform {
  backend "s3" {
    bucket       = "nom-du-bucket-d-etat"
    key          = "atelier-iac/dev/terraform.tfstate"
    region       = "eu-west-3"
    use_lockfile = true
  }
}
```

Ce bloc illustre une configuration du backend S3 avec verrouillage natif par fichier. Le bucket doit déjà exister et les permissions IAM doivent autoriser les opérations nécessaires.

Les paramètres du backend ne se comportent pas comme les variables habituelles du module. Ils sont configurés lors de l'initialisation et ne doivent pas contenir de secrets en dur.

Pour une utilisation réelle, la documentation officielle du backend doit être consultée, en particulier pour les permissions, le chiffrement, la version des objets et les options de verrouillage.

### 11.2 Initialiser le backend

```bash
terraform init
```

Si le projet passe d'un backend à un autre, Terraform peut demander de migrer l'état. La migration doit être organisée et vérifiée avant d'accepter le changement.

Ne pas modifier arbitrairement la configuration du backend sur un projet de production.

### 11.3 Protéger le bucket d'état

Les mesures habituelles comprennent :

- blocage de l'accès public ;
- chiffrement activé ;
- versionnement des objets ;
- droits IAM limités aux chemins nécessaires ;
- séparation des droits de lecture et d'écriture lorsque cela est possible ;
- journaux d'audit ;
- restauration testée ;
- verrouillage d'état activé si pris en charge.

Le droit de lire l'état doit être considéré comme sensible. Une personne capable de lire le fichier peut obtenir des informations qu'elle ne devrait pas connaître.

### 11.4 Gérer un verrou bloqué

Un verrou peut rester présent à la suite d'un arrêt brutal ou d'un problème de backend.

Procédure :

1. Lire le message d'erreur et identifier l'opération qui détient le verrou.
2. Vérifier qu'aucun autre pipeline ou ingénieur ne travaille sur cet état.
3. Examiner l'identifiant du verrou.
4. Ne le libérer qu'après confirmation de l'absence d'une opération active.

Exemple de commande de dernier recours :

```bash
terraform force-unlock IDENTIFIANT_DU_VERROU
```

Cette commande est dangereuse lorsqu'elle est utilisée sans investigation. Un déverrouillage prématuré peut autoriser plusieurs écrivains à travailler sur le même état.

Ne pas utiliser `-lock=false` comme solution habituelle à un problème de verrouillage.

## 12. Outils de manipulation de l'état

Les commandes `terraform state` servent à diagnostiquer et à modifier les associations entre adresses Terraform et objets suivis.

Lister les ressources :

```bash
terraform state list
```

Afficher une ressource précise :

```bash
terraform state show aws_vpc.this
```

Déplacer une adresse dans l'état :

```bash
terraform state mv \
  aws_subnet.old \
  aws_subnet.new
```

Supprimer une association de l'état :

```bash
terraform state rm aws_subnet.old
```

`state rm` ne détruit pas automatiquement l'objet réel chez le fournisseur. Il retire sa gestion de l'état courant. La prochaine planification peut ensuite proposer de créer un nouvel objet à l'adresse déclarée dans la configuration.

Avant toute manipulation :

- vérifier le backend et le workspace actifs ;
- confirmer le bon environnement ;
- sauvegarder l'état si nécessaire ;
- effectuer l'opération pendant une fenêtre de changement ;
- examiner le plan obtenu ensuite.

Ne jamais utiliser ces commandes pour « faire disparaître » un changement inattendu sans comprendre l'origine du problème.

## 13. Importer une infrastructure existante

Dans les organisations réelles, des ressources peuvent avoir été créées manuellement, par un autre outil ou avant l'adoption de Terraform.

Il n'est pas toujours nécessaire de les supprimer et de les recréer. Elles peuvent être importées dans la gestion Terraform.

### 13.1 Principe

```text
Ressource déjà existante
          |
          v
Identification de la ressource
          |
          v
Déclaration HCL correspondante
          |
          v
Import dans l'état
          |
          v
Examen du plan
          |
          v
Gestion Terraform contrôlée
```

Une importation ne signifie pas automatiquement que Terraform a produit une configuration parfaite. Il faut adapter le code afin qu'il représente correctement la ressource réelle.

### 13.2 Import déclaré dans la configuration

À partir de Terraform 1.5, les blocs `import` permettent de déclarer l'importation dans la configuration.

Exemple générique :

```hcl
import {
  to = aws_instance.example
  id = "i-0123456789abcdef0"
}
```

L'adresse de destination doit correspondre à une ressource déclarée. L'identifiant dépend du type de ressource et du provider.

L'exemple suppose que la ressource `aws_instance.example` existe dans la configuration et que son identifiant est valide dans le compte cible.

Procédure :

```bash
terraform init
terraform validate
terraform plan
```

Examiner le plan d'importation, puis appliquer lorsque la correspondance est correcte.

Il faut éviter d'importer le même objet réel à plusieurs adresses Terraform. Cela peut entraîner une gestion incohérente.

### 13.3 Importation dans un module

Une ressource d'un module peut être importée en utilisant son adresse complète.

Exemple conceptuel :

```hcl
import {
  to = module.network.aws_vpc.this
  id = "vpc-0123456789abcdef0"
}
```

La ressource doit exister dans le code du module et la configuration doit être compatible avec les attributs réels de l'objet.

### 13.4 Importer ne suffit pas

Après l'importation :

1. examiner les attributs suivis ;
2. compléter la configuration ;
3. vérifier les valeurs implicites et les valeurs par défaut ;
4. relancer un plan ;
5. expliquer tout changement proposé ;
6. corriger les différences avant de considérer le code comme stabilisé.

L'objectif est d'éviter que le premier `apply` suivant l'importation remplace ou reconfigure accidentellement la ressource existante.

## 14. Refactoriser sans détruire : les blocs `moved`

Les adresses Terraform sont importantes. Déplacer un bloc d'un fichier à un autre ne change généralement pas son adresse, mais le déplacer dans un module ou renommer la ressource peut la modifier.

Sans indication explicite, Terraform peut considérer l'ancienne ressource comme supprimée et la nouvelle comme devant être créée.

### 14.1 Exemple de déplacement

Ancienne adresse :

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.20.0.0/16"
}
```

Après refactorisation, la ressource est déplacée dans `module.network`.

Ajouter un bloc de déplacement à la configuration racine :

```hcl
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.this
}
```

Ce bloc indique à Terraform que l'adresse change mais que l'objet géré doit conserver son identité.

### 14.2 Procédure de refactorisation

1. Identifier l'adresse initiale.
2. Préparer le nouveau module et sa ressource.
3. Ajouter le bloc `moved`.
4. Exécuter `terraform plan`.
5. Vérifier que Terraform signale le déplacement plutôt qu'une destruction suivie d'une recréation.
6. Appliquer avec la procédure normale de contrôle.

Ne jamais supprimer un bloc `moved` avant d'avoir vérifié que tous les états devant utiliser ce déplacement ont effectué la transition attendue. Une politique de conservation des blocs de déplacement permet aussi de faciliter les mises à niveau des utilisateurs d'un module partagé.

## 15. Dépendances, `lifecycle` et maîtrise des changements

Le bloc `lifecycle` permet d'ajuster certains comportements relatifs au cycle de vie des ressources.

### 15.1 Prévenir une destruction accidentelle

```hcl
resource "aws_s3_bucket" "critical" {
  bucket = var.bucket_name

  lifecycle {
    prevent_destroy = true
  }
}
```

`prevent_destroy` peut bloquer une destruction demandée par Terraform tant que la protection est présente. Ce n'est pas un système de sauvegarde et ce n'est pas une politique d'autorisation générale.

Une suppression du bloc de ressource peut également retirer cette protection de la configuration.

### 15.2 Créer avant de détruire

```hcl
resource "aws_instance" "service" {
  # Arguments du fournisseur

  lifecycle {
    create_before_destroy = true
  }
}
```

Cette option demande à Terraform de privilégier la création du nouvel objet avant la destruction de l'ancien lorsque les contraintes le permettent.

Elle peut réduire une interruption, mais ne garantit pas qu'un remplacement sera sans risque. Certains noms sont uniques, certaines ressources ne peuvent pas coexister et certaines dépendances imposent un ordre différent.

### 15.3 Ignorer certaines différences

```hcl
lifecycle {
  ignore_changes = [
    tags["LastScanned"]
  ]
}
```

`ignore_changes` peut être justifié si un autre système est autorisé à gérer un attribut précis. Il ne doit pas servir à masquer les dérives ou les modifications qui devraient normalement être contrôlées par Terraform.

La règle professionnelle est simple : n'ignorer un changement que si la responsabilité de cet attribut est explicitement définie.

## 16. Validation avancée : variables, préconditions et postconditions

Il existe plusieurs mécanismes de validation, à utiliser selon l'objet contrôlé.

### 16.1 Validation de variable

```hcl
variable "instance_count" {
  description = "Nombre d'instances"
  type        = number

  validation {
    condition = (
      var.instance_count >= 1 &&
      var.instance_count <= 10
    )

    error_message = "Le nombre d'instances doit être compris entre 1 et 10."
  }
}
```

Cette validation contrôle les valeurs reçues par la configuration.

### 16.2 Précondition

Une précondition vérifie une hypothèse nécessaire avant l'utilisation d'une ressource ou d'un résultat.

Exemple conceptuel :

```hcl
resource "example_resource" "service" {
  # Arguments adaptés au provider

  lifecycle {
    precondition {
      condition     = var.environment != "prod" || var.production_approved
      error_message = "Le déploiement en production exige une approbation."
    }
  }
}
```

`example_resource` représente ici un type fictif. Ce bloc illustre la logique, mais doit être placé dans une ressource réelle et compatible avec le provider utilisé.

Attention : une variable d'approbation dans le code ne remplace pas une approbation externe, un environnement protégé ou des permissions d'exécution. Un acteur capable de modifier la configuration pourrait également modifier cette valeur.

### 16.3 Postcondition

Une postcondition peut contrôler un attribut après la lecture ou la création d'une ressource.

Exemple conceptuel :

```hcl
resource "example_resource" "service" {
  # Arguments adaptés au provider

  lifecycle {
    postcondition {
      condition     = self.status == "ready"
      error_message = "La ressource n'a pas atteint l'état attendu."
    }
  }
}
```

`example_resource` et `self.status` sont illustratifs : leur équivalent réel dépend du provider.

### 16.4 Bloc `check`

Les blocs `check` servent à exprimer des assertions qui surveillent des propriétés de l'infrastructure. Ils ne remplacent pas tous les mécanismes de validation et ne doivent pas être traités comme une garantie absolue bloquant toute opération.

Pour chaque condition, déterminer si une violation doit :

- empêcher la déclaration d'une valeur ;
- bloquer l'opération sur une ressource ;
- signaler un problème de conformité ;
- déclencher une alerte ou une enquête.

Une règle bloquante doit utiliser le mécanisme adapté à son objectif.

## 17. Tester une configuration Terraform

Une configuration qui passe `terraform validate` peut toujours déployer une architecture incorrecte, exposer une ressource ou employer des valeurs dangereuses.

La stratégie de vérification doit être composée de plusieurs niveaux.

```text
1. Format du code
       |
       v
2. Validation HCL
       |
       v
3. Analyse statique
       |
       v
4. Tests des modules
       |
       v
5. Plan d'infrastructure
       |
       v
6. Examen humain et contrôles de sécurité
       |
       v
7. Application autorisée
       |
       v
8. Vérification après déploiement
```

### 17.1 Format et validation

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

L'option `-backend=false` permet d'initialiser la configuration pour certaines validations sans connecter le backend configuré. Elle ne remplace pas une initialisation normale nécessaire pour un plan réel.

### 17.2 Tests avec `terraform test`

Terraform inclut une commande de test destinée aux configurations et aux modules.

```bash
terraform test
```

Les fichiers de test utilisent généralement l'extension `.tftest.hcl` et se trouvent dans un répertoire `tests/`.

Les tests peuvent vérifier des assertions sur une configuration, des outputs ou le comportement du plan. Selon leur contenu et leur environnement, ils peuvent également créer de vraies ressources.

Ne pas exécuter des tests créant des ressources sans connaître leurs effets, leurs coûts et leur procédure de nettoyage. Utiliser un compte de test isolé lorsque cela est possible.

### 17.3 Analyse statique complémentaire

Des outils tels que TFLint ou des scanners de sécurité IaC peuvent détecter des configurations douteuses et des erreurs courantes.

Ils complètent Terraform, mais ne remplacent pas :

- l'analyse du plan ;
- la revue humaine ;
- les tests ;
- le contrôle des identités ;
- la vérification de l'infrastructure déployée.

Une analyse sans erreur ne prouve pas que l'architecture est sécurisée ou adaptée aux besoins métier.

## 18. Sécurité des secrets et des identités

Les secrets doivent être considérés comme une donnée distincte du code d'infrastructure.

Ils ne doivent pas être inscrits en clair dans :

- les fichiers HCL ;
- les fichiers de variables versionnés ;
- les scripts de pipeline ;
- les messages de commit ;
- les logs ;
- les artefacts partagés sans contrôle.

### 18.1 La limite de `sensitive = true`

Exemple :

```hcl
variable "api_token" {
  description = "Jeton API"
  type        = string
  sensitive   = true
}
```

Le marqueur `sensitive` masque la valeur dans certains affichages Terraform. Il ne signifie pas que la valeur ne sera jamais stockée dans l'état ou dans les fichiers de planification.

Il faut donc contrôler la façon dont les secrets sont transmis et vérifier le comportement du provider et du backend.

### 18.2 Préférer une identité temporaire

Dans un pipeline cloud, privilégier une identité fédérée ou un mécanisme d'authentification temporaire lorsque le fournisseur le permet.

Les principes à appliquer sont :

- permissions minimales ;
- identité différente selon l'environnement ;
- durée de vie limitée des identifiants ;
- absence de clés permanentes dans le dépôt ;
- séparation des droits de planification et de déploiement lorsque possible ;
- journalisation des opérations ;
- rotation et révocation en cas d'incident.

### 18.3 Valeurs éphémères et arguments non persistés

Les versions récentes de Terraform comportent des mécanismes permettant, dans certaines conditions, de faire transiter des valeurs sensibles sans les enregistrer dans l'état ou les plans.

Ces mécanismes incluent des valeurs éphémères et des arguments en écriture seule, lorsque les constructions et les providers concernés les prennent en charge.

Il faut vérifier les contraintes de la documentation officielle, car ces valeurs ne peuvent pas être utilisées partout. Il ne faut pas supposer qu'une donnée fournie à un provider sera automatiquement omise de l'état.

### 18.4 L'état reste une donnée sensible

Même lorsqu'un mot de passe est marqué comme sensible, les valeurs nécessaires à la gestion des ressources peuvent rester présentes dans des artefacts Terraform.

Mesures recommandées :

- restreindre l'accès à l'état ;
- limiter la rétention des plans ;
- chiffrer les artefacts ;
- éviter l'affichage intégral de fichiers de plan dans les logs ;
- ne pas publier d'état ni de plan dans un dépôt public ;
- contrôler les accès aux journaux de pipeline.

## 19. Terraform et les outils CI/CD

Les cours précédents sur Git et la CI/CD fournissent le cadre de ce chapitre.

Le dépôt Git contient la configuration versionnée. Le pipeline applique des contrôles automatiques. Le plan Terraform représente les changements proposés. L'étape d'application doit suivre une autorisation explicite adaptée à l'environnement.

```text
Développeur
    |
    v
Branche Git
    |
    v
Pull request / Merge request
    |
    v
Contrôles statiques
    |
    +-- Format HCL
    +-- Validation Terraform
    +-- Analyse de sécurité
    +-- Tests
    |
    v
Plan Terraform
    |
    v
Revue du changement
    |
    v
Fusion autorisée
    |
    v
Approbation de déploiement
    |
    v
Identité CI/CD autorisée
    |
    v
terraform apply
    |
    v
Infrastructure
```

### 19.1 Règles de pipeline

Une chaîne d'intégration sérieuse doit :

- s'exécuter sur les changements touchant l'infrastructure ;
- utiliser une version maîtrisée de Terraform ;
- respecter le fichier de verrouillage ;
- contrôler le format et la validité ;
- analyser les risques ;
- préparer un plan pour le bon environnement ;
- réserver l'application aux contextes autorisés ;
- conserver des journaux utiles sans publier de secrets ;
- empêcher les applications concurrentes sur le même état ;
- fournir un moyen d'audit et de récupération.

Il faut éviter d'autoriser tout auteur de pull request à exécuter un plan ou une application avec des permissions de production. Les pipelines qui exécutent du code provenant de branches non fiables nécessitent une attention particulière.

## 20. Exemple de pipeline GitHub Actions

Le fichier suivant présente une base de validation statique et de planification pour une configuration située dans `infrastructure/`.

Fichier `.github/workflows/terraform.yml` :

```yaml
name: Terraform CI

on:
  pull_request:
    paths:
      - "infrastructure/**"
      - ".github/workflows/terraform.yml"
  push:
    branches:
      - main
    paths:
      - "infrastructure/**"
      - ".github/workflows/terraform.yml"

permissions:
  contents: read

concurrency:
  group: terraform-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

jobs:
  validate:
    name: Format and validate
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: infrastructure

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.9.8"

      - name: Check formatting
        run: terraform fmt -check -recursive

      - name: Initialize without backend
        run: terraform init -backend=false -input=false

      - name: Validate
        run: terraform validate
```

Cette version de l'exemple utilise une version explicite de Terraform pour illustrer le principe de reproductibilité. Dans un nouveau dépôt, choisir une version encore prise en charge et compatible avec les contraintes du projet, puis la mettre à jour de manière contrôlée.

### 20.1 Pourquoi cette étape n'applique-t-elle rien ?

Ce premier job vérifie le code, mais ne dispose pas des identifiants nécessaires au déploiement réel. Cela réduit l'exposition aux opérations cloud pour les changements qui n'ont pas encore été approuvés.

Pour un plan réel, il faut initialiser le backend voulu, accéder aux credentials du fournisseur et choisir l'environnement correct.

### 20.2 Ajouter la planification

Le job de planification doit être conçu en fonction de l'organisation :

- accès au backend d'état ;
- identité de lecture ou de planification autorisée ;
- environnement cible ;
- fichiers de variables corrects ;
- conservation protégée du plan si sa réutilisation est nécessaire ;
- contrôle des sorties pour ne pas révéler les informations sensibles.

Pour une infrastructure AWS, une identité OIDC peut être mise en place avec une confiance limitée au dépôt, à la branche et au contexte de travail autorisés. Il faut alors ajouter les permissions `id-token: write` au job qui en a besoin, et configurer le fournisseur cloud pour faire confiance à cette identité.

Ne pas attribuer inutilement ces permissions à tous les jobs.

### 20.3 Appliquer après approbation

L'application de production doit s'exécuter avec une identité disposant des droits nécessaires uniquement au déploiement autorisé.

On peut utiliser un environnement GitHub protégé qui exige une approbation avant l'exécution du job d'application.

L'application doit se baser sur un plan examiné, ou recalculer un plan après approbation selon le modèle de gouvernance choisi. Si le plan est transmis comme artefact, son accès, sa durée de vie et son contenu doivent être protégés.

Le job ne doit pas utiliser automatiquement le dernier fichier de plan trouvé dans un répertoire ou produit par une exécution sans rapport avec la demande actuelle.

## 21. Exemple de pipeline GitLab CI

Le principe est similaire avec GitLab CI : validation, planification puis application contrôlée.

Fichier `.gitlab-ci.yml` :

```yaml
stages:
  - validate
  - plan
  - apply

variables:
  TF_ROOT: "infrastructure"
  TF_IN_AUTOMATION: "true"
  TF_INPUT: "false"

default:
  image:
    name: hashicorp/terraform:1.9.8
    entrypoint: [""]

validate:
  stage: validate
  script:
    - cd "$TF_ROOT"
    - terraform fmt -check -recursive
    - terraform init -backend=false -input=false
    - terraform validate
  rules:
    - changes:
        - infrastructure/**/*

plan:
  stage: plan
  script:
    - cd "$TF_ROOT"
    - terraform init -input=false
    - terraform plan -input=false
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      changes:
        - infrastructure/**/*
  # Configurer ici l'authentification et le backend
  # en utilisant les mécanismes de secrets ou d'identité approuvés.

apply:
  stage: apply
  script:
    - cd "$TF_ROOT"
    - terraform init -input=false
    - terraform plan -input=false -out=tfplan
    - terraform apply -input=false -auto-approve tfplan
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      changes:
        - infrastructure/**/*
      when: manual
  # Protéger l'environnement de production dans GitLab.
  # Limiter ce job à une identité et à des rôles autorisés.
```

Cet exemple est un squelette pédagogique. Il doit être complété avant un usage réel : configuration du backend, authentification, environnement cible et permissions.

Il faut aussi coordonner les jobs, les états et les artefacts lorsque la planification et l'application sont réparties entre plusieurs étapes. Le plan d'un job ne doit pas être consommé aveuglément par une autre exécution.

### 21.1 Comparaison des deux plateformes

| Besoin | GitHub Actions | GitLab CI |
|---|---|---|
| Déclenchement | Événements et filtres `on` | `rules`, sources et filtres |
| Ordre des étapes | Jobs et dépendances | Stages et dépendances |
| Protection de production | Environnement protégé et approbation | Environnement protégé et job manuel |
| Identifiants | Secrets, variables et OIDC selon le fournisseur | Variables protégées, secrets et identité selon le fournisseur |
| Contrôle des changements | Pull request | Merge request |
| Contrôle de l'infrastructure | Même processus Terraform | Même processus Terraform |

La plateforme CI/CD ne remplace pas les règles de sécurité Terraform. Les deux doivent fonctionner ensemble.

## 22. Détecter la dérive de configuration

La dérive, ou *drift*, correspond à une différence entre l'infrastructure réelle et ce que la configuration et l'état déclarent comme souhaité.

Exemples :

- une personne modifie une règle réseau manuellement ;
- une ressource est supprimée hors Terraform ;
- un attribut est modifié par un outil tiers ;
- une configuration du fournisseur change au cours du temps.

Le plan Terraform peut détecter certaines de ces différences lorsqu'il interroge le provider.

### 22.1 Procédure de détection

```bash
terraform plan -var-file="environments/dev.tfvars"
```

Le plan doit être examiné pour distinguer :

- une modification attendue du code ;
- une dérive réelle ;
- un changement imposé par le fournisseur ;
- une différence liée au fonctionnement de la ressource ;
- un comportement lié au provider ou à sa version.

La détection de la dérive n'implique pas qu'il faille immédiatement appliquer le plan. Il faut d'abord déterminer si la modification réelle était autorisée ou si elle révèle un incident.

### 22.2 Pipeline de détection périodique

Une organisation peut programmer un plan périodique et contrôler son résultat.

Cette opération doit employer les identifiants et le backend appropriés. Elle doit aussi différencier une différence informative d'une erreur d'accès au backend ou d'un échec d'authentification.

Ne pas interpréter automatiquement un plan impossible à calculer comme une dérive d'infrastructure.

## 23. Les risques d'un `apply` automatique

L'application automatique est utile lorsqu'elle se limite à un contexte clairement défini, mais elle devient dangereuse si elle ne distingue pas les environnements ou les autorisations.

Risques fréquents :

- mauvais fichier de variables ;
- mauvais état ;
- mauvaises credentials ;
- destruction non prévue ;
- application basée sur un plan périmé ;
- exécutions concurrentes ;
- exposition d'un artefact sensible ;
- exécution d'un changement de production depuis une branche non autorisée.

Avant d'autoriser l'application automatique, vérifier :

1. le code source et la branche ;
2. l'environnement et le backend actifs ;
3. l'identité qui exécute l'opération ;
4. les changements affichés par le plan ;
5. la stratégie de concurrence et de verrouillage ;
6. la politique d'approbation ;
7. le plan de retour arrière ou de récupération.

L'automatisation accélère l'exécution, elle ne supprime pas la responsabilité de valider le changement.

## 24. Gestion des coûts et de la capacité

Terraform peut créer des ressources facturées : machines, stockage, bases de données, transferts, adresses IP et composants réseau.

Un plan techniquement valide n'est pas nécessairement rentable.

Les contrôles possibles incluent :

- estimation du coût avant application ;
- quotas et limites dans le compte cloud ;
- tailles et quantités maximales autorisées ;
- tags permettant l'attribution des coûts ;
- environnements de test temporaires ;
- politiques de nettoyage ;
- alertes de consommation ;
- séparation entre ressources permanentes et temporaires.

Une estimation de coût est une approximation basée sur un modèle et des hypothèses. Elle doit être rapprochée des tarifs, de la région, du volume d'utilisation et des services réels.

### 24.1 Exemple de contrôle de capacité

```hcl
variable "instance_count" {
  description = "Nombre d'instances"
  type        = number

  validation {
    condition = (
      var.instance_count >= 1 &&
      var.instance_count <= 5
    )

    error_message = "La capacité demandée dépasse les limites de cet environnement."
  }
}
```

Cette règle réduit les erreurs de saisie. Elle ne remplace pas les quotas cloud, les autorisations ni les contrôles de coût de la plateforme.

## 25. Règles de qualité pour des modules partagés

Un module destiné à plusieurs équipes doit être maintenu comme un composant logiciel.

### 25.1 Politique de versionnement

Un module partagé devrait posséder :

- une documentation d'interface ;
- une version identifiable ;
- une politique de compatibilité ;
- des tests ;
- un historique des changements ;
- une procédure de dépréciation ;
- une liste des versions maintenues.

Une modification incompatible de l'interface ne devrait pas être publiée silencieusement comme une simple correction mineure.

### 25.2 Versionner le module consommé

Lorsqu'un module est publié dans un registre, préciser une version testée.

Cela évite que des consommateurs reçoivent involontairement une nouvelle version dont les changements n'ont pas encore été validés pour leur usage.

Les mises à jour doivent elles-mêmes passer par un processus de revue et de test.

### 25.3 Documenter les limites

Un module réseau doit préciser, par exemple :

- s'il crée ou non des passerelles NAT ;
- s'il configure les routes Internet ;
- s'il traite IPv6 ;
- s'il configure des ACL réseau ;
- s'il crée des endpoints privés ;
- comment il nomme les ressources ;
- les plages CIDR attendues ;
- les régions ou services compatibles.

Une bonne documentation énonce aussi ce que le module ne fait pas.

## 26. Erreurs fréquentes et diagnostic

### 26.1 `terraform init` échoue

Causes possibles :

- réseau inaccessible ;
- authentification au registre impossible ;
- source de module incorrecte ;
- contrainte de provider incompatible ;
- configuration de backend invalide ;
- droits insuffisants.

Démarche :

```bash
terraform version
terraform init
```

Lire le premier message d'erreur utile et vérifier s'il concerne le backend, le provider ou un module. Ne pas supprimer systématiquement le fichier de verrouillage pour tenter de contourner le problème.

### 26.2 Provider introuvable ou version incompatible

Vérifier :

- le bloc `required_providers` ;
- la source officielle ou privée ;
- les contraintes de version ;
- le fichier `.terraform.lock.hcl` ;
- la version de Terraform CLI.

La mise à jour du fichier de verrouillage doit être une action intentionnelle et revue.

### 26.3 Le plan propose une destruction

Identifier d'abord l'adresse exacte et le motif du remplacement.

Causes possibles :

- modification d'un attribut immuable ;
- changement de clé `for_each` ;
- modification d'une expression ;
- déplacement d'une ressource sans bloc `moved` ;
- import incorrect ;
- changement d'environnement ou d'état.

Ne pas appliquer par réflexe. Réduire le problème à la ressource concernée et examiner le plan détaillé.

### 26.4 Une ressource est manquante dans l'état

Avant de la recréer :

- rechercher sa présence chez le fournisseur ;
- vérifier la configuration d'accès ;
- vérifier le backend et le workspace ;
- confirmer l'adresse Terraform ;
- envisager une importation si l'objet existe réellement.

Une ressource absente de l'état n'est pas nécessairement absente de l'infrastructure.

### 26.5 Erreur de concurrence

Si une autre opération détient le verrou, attendre la fin de cette opération ou enquêter sur son état. Ne pas déverrouiller sans identifier le propriétaire du verrou et l'origine de la situation.

### 26.6 Échec d'authentification

Vérifier :

- l'identité active ;
- l'environnement visé ;
- les permissions sur les ressources ;
- les permissions du backend ;
- la durée de vie des credentials ;
- les restrictions de rôle et de compte ;
- le contexte d'exécution du pipeline.

Les droits sur le backend d'état et les droits sur les ressources cloud constituent deux besoins distincts.

## 27. Laboratoire pratique complet

### Objectif

Réaliser un petit projet d'infrastructure reproductible, capable de déployer un réseau dans un environnement de test et de passer par une chaîne de validation similaire à celle d'une équipe.

### Étape 1 : préparer le dépôt

Créer l'arborescence de l'atelier, le `.gitignore` et le fichier README.

Initialiser Git si le dépôt n'existe pas :

```bash
git init
git add .
git commit -m "Initialisation de l'infrastructure Terraform"
```

### Étape 2 : valider le code

```bash
terraform fmt -recursive
terraform init
terraform validate
```

Résoudre les erreurs avant toute opération de création.

### Étape 3 : préparer un plan

```bash
terraform plan \
  -var-file="environments/dev.tfvars" \
  -out="dev.tfplan"
```

Examiner les ressources à créer et identifier les éventuels changements inattendus.

### Étape 4 : appliquer dans un environnement de test

```bash
terraform apply dev.tfplan
```

Vérifier ensuite les ressources chez le fournisseur et comparer leur configuration avec les outputs Terraform.

### Étape 5 : versionner les améliorations

Créer une branche :

```bash
git switch -c feature/network-module
```

Après avoir validé les améliorations :

```bash
git add .
git commit -m "Ajout du module réseau"
```

Ouvrir une pull request ou merge request. Ajouter les contrôles statiques et la revue du plan à la procédure de changement.

### Étape 6 : simuler une refactorisation

Déplacer une ressource existante dans un module.

Ajouter un bloc `moved` adapté aux anciennes et nouvelles adresses. Produire un plan et vérifier que le changement ne provoque pas une destruction injustifiée.

### Étape 7 : nettoyer

Si l'environnement de test n'est plus nécessaire, effectuer une destruction contrôlée.

```bash
terraform plan -destroy \
  -var-file="environments/dev.tfvars"
```

Examiner la sortie puis appliquer la procédure de destruction approuvée.

La destruction doit être considérée comme une opération d'infrastructure à part entière et non comme une simple commande de ménage.

## 28. Exercices corrigés

### Exercice 1 : choix de `for_each`

Une équipe doit gérer les sous-réseaux `public_a`, `private_a` et `private_b`. Elle envisage d'utiliser une liste et `count`.

**Question :** pourquoi une map avec `for_each` peut-elle être plus appropriée ?

**Correction :**

Une map associe chaque sous-réseau à une clé stable et explicite. Les adresses Terraform deviennent lisibles et une suppression ne réinterprète pas automatiquement les indices des autres sous-réseaux.

`for_each` ne supprime pas tous les risques de remplacement, mais améliore la correspondance entre le code et les objets nommés.

### Exercice 2 : séparation des environnements

Deux équipes administrent le développement et la production. Elles disposent de droits différents et doivent pouvoir déployer indépendamment.

**Question :** un workspace Terraform CLI suffit-il à assurer l'isolation ?

**Correction :**

Non. Les workspaces partagent une configuration et ne constituent pas à eux seuls une frontière d'autorisation. Il faut déterminer comment séparer les identités, les permissions, les états, les backends et les procédures de déploiement.

Des configurations racines et états distincts peuvent être plus adaptés.

### Exercice 3 : secret marqué `sensitive`

Une variable contenant un jeton est déclarée avec `sensitive = true`.

**Question :** le jeton ne peut-il plus apparaître dans aucun fichier Terraform ?

**Correction :**

Non. Le marqueur limite certains affichages, mais ne garantit pas l'absence de la valeur dans l'état ou les plans. Il faut contrôler le mécanisme de transmission du secret, le backend et les artefacts. Lorsque les constructions et providers le permettent, des mécanismes éphémères et des arguments en écriture seule peuvent réduire la persistance.

### Exercice 4 : ressource importée avec remplacement prévu

Une équipe importe une ressource existante. Le prochain plan propose de remplacer cette ressource.

**Question :** quelle doit être la première réaction ?

**Correction :**

Ne pas appliquer. Il faut comparer la configuration déclarée aux attributs réels, vérifier les valeurs par défaut et les options immuables, puis corriger la déclaration ou la stratégie d'importation. La première application après importation doit être examinée attentivement.

### Exercice 5 : déverrouillage

Un pipeline indique que l'état est verrouillé. Un ingénieur veut immédiatement exécuter `terraform force-unlock`.

**Question :** quelle démarche suivre ?

**Correction :**

Identifier d'abord l'opération qui a acquis le verrou. Vérifier les pipelines actifs et les personnes intervenant sur le même état. Ne libérer le verrou qu'après confirmation qu'il est devenu obsolète et en utilisant l'identifiant correct.

### Exercice 6 : bloc `moved`

Une ressource passe de `aws_vpc.main` à `module.network.aws_vpc.this`.

**Question :** quelle précaution évite une recréation non souhaitée ?

**Correction :**

Déclarer un bloc `moved` indiquant les anciennes et nouvelles adresses, puis contrôler le plan. Le déplacement doit être confirmé par l'absence d'une destruction injustifiée de l'objet réel.

### Exercice 7 : pipeline sécurisé

Une pull request doit exécuter `terraform validate`, puis appliquer directement les changements à la production.

**Question :** quels contrôles manquent ?

**Correction :**

Il manque notamment une planification réelle, un examen du plan, une vérification du contexte d'environnement, une identité de déploiement limitée, une approbation adaptée et des protections contre les exécutions concurrentes. Les changements d'infrastructure ne doivent pas être appliqués en production uniquement parce que la syntaxe est valide.

### Exercice 8 : backend et état

Un membre de l'équipe peut lire les fichiers HCL mais n'a pas le droit de lire l'état distant.

**Question :** ce choix de permissions est-il cohérent ?

**Correction :**

Il peut l'être. Le code source et l'état n'ont pas nécessairement les mêmes niveaux de sensibilité. L'état peut contenir des identifiants, des valeurs sensibles ou des détails internes. Les accès doivent être accordés selon le rôle opérationnel réel.

## 29. Défi final corrigé : industrialiser un déploiement réseau

### Situation

Une équipe doit gérer trois environnements :

- `dev` pour les expérimentations ;
- `staging` pour la validation ;
- `prod` pour les déploiements autorisés.

Le réseau doit être défini dans un module réutilisable. Le dépôt Git doit garder les modifications traçables. Le pipeline doit valider le code, préparer un plan et permettre une application contrôlée.

### Travail demandé

1. Créer le module réseau.
2. Déclarer les interfaces et validations.
3. Préparer des valeurs différentes pour les environnements.
4. Choisir un backend et protéger son état.
5. Configurer la validation statique.
6. Organiser la planification.
7. Protéger la production.
8. Importer une ressource existante dans une variante de l'exercice.
9. Refactoriser une ressource avec `moved`.
10. Documenter le diagnostic et la récupération.

### Proposition de correction

**Organisation :**

- un module réseau commun ;
- des configurations racines ou des états séparés selon les exigences d'isolation ;
- un fichier de valeurs par environnement ;
- un backend distant adapté au fournisseur ;
- des variables de configuration sans secret en clair ;
- un fichier de verrouillage versionné.

**Contrôle de version :**

- branche dédiée aux changements ;
- commits lisibles ;
- pull request ou merge request obligatoire ;
- revue du plan ;
- fusion uniquement après les contrôles requis.

**Pipeline :**

- formatage HCL ;
- validation ;
- analyse statique ;
- tests ;
- planification dans le bon environnement ;
- approbation de production ;
- application avec identité autorisée ;
- journalisation et vérification après déploiement.

**Gestion de l'état :**

- stockage distant protégé ;
- droits d'accès minimaux ;
- verrouillage quand il est disponible ;
- versionnement ou sauvegarde ;
- procédure de récupération documentée ;
- interdiction des modifications manuelles non contrôlées.

**Résultat attendu :**

La même conception est réutilisable, les différences d'environnement sont explicites, les changements sont examinables avant application et les opérations sensibles disposent d'une procédure contrôlée.

### Critères d'évaluation

| Critère | Résultat attendu |
|---|---|
| Architecture | Responsabilités clairement séparées |
| Modules | Interface documentée, stable et typée |
| Expressions | `for_each` et transformations maîtrisés |
| Environnements | Valeurs et états correctement séparés |
| Backend | Stockage distant sécurisé et accès limités |
| Sécurité | Pas de secrets en clair dans le dépôt |
| Tests | Formatage, validation et contrôles exécutés |
| CI/CD | Plan examiné et application autorisée |
| Migration | Import et déplacement vérifiés |
| Documentation | Procédures de déploiement et de récupération explicites |

## 30. Checklist professionnelle avant application

Avant chaque application importante, vérifier les points suivants.

### Configuration

- [ ] Le bon répertoire Terraform est utilisé.
- [ ] Le provider et ses versions sont compatibles.
- [ ] Le fichier de verrouillage est cohérent.
- [ ] `terraform fmt` ne détecte pas d'erreur.
- [ ] `terraform validate` réussit.
- [ ] Les paramètres appartiennent au bon environnement.

### État et identité

- [ ] Le backend correspond au bon environnement.
- [ ] L'état n'est pas déjà modifié par une opération concurrente.
- [ ] Les droits sur l'état sont restreints.
- [ ] L'identité cloud utilisée est celle attendue.
- [ ] Les secrets et artefacts sont protégés.

### Plan

- [ ] Les ressources à créer sont attendues.
- [ ] Les destructions sont comprises.
- [ ] Les remplacements sont justifiés.
- [ ] Le réseau, les règles de sécurité et les routes sont examinés.
- [ ] Les impacts de coût sont compris.
- [ ] Le plan correspond à une version identifiable du code.

### Application et suivi

- [ ] L'autorisation requise a été obtenue.
- [ ] La bonne identité exécute l'opération.
- [ ] Le verrouillage est utilisé lorsque disponible.
- [ ] Les résultats sont vérifiés chez le fournisseur.
- [ ] Les dérives éventuelles sont investiguées.
- [ ] Les ressources temporaires sont nettoyées selon la procédure.

## 31. Glossaire

**Infrastructure as Code (IaC)** : gestion de l'infrastructure à l'aide de déclarations ou de programmes versionnés.

**HCL** : HashiCorp Configuration Language, utilisé pour écrire les configurations Terraform.

**Provider** : composant qui permet à Terraform de communiquer avec un système externe.

**Module** : ensemble cohérent de ressources et d'interface réutilisable.

**Module racine** : configuration depuis laquelle Terraform est exécuté.

**Module enfant** : module appelé depuis un autre module.

**State** : état Terraform qui relie les ressources déclarées aux objets gérés.

**Backend** : mécanisme de stockage de l'état et, selon le type, de verrouillage.

**Verrouillage d'état** : mécanisme qui limite les écritures concurrentes sur un état pris en charge.

**Drift** : différence entre la réalité et la configuration attendue.

**Import** : opération par laquelle Terraform commence à suivre un objet existant.

**`moved`** : bloc qui déclare un changement d'adresse d'une ressource ou d'un module.

**`for_each`** : mécanisme qui crée une instance de ressource ou de module par élément d'une map ou d'un ensemble compatible.

**Plan Terraform** : représentation des changements envisagés avant l'application.

**Pipeline** : chaîne automatisée de vérifications et d'opérations.

**OIDC** : protocole pouvant permettre une fédération d'identité et l'obtention de credentials temporaires.

**Least privilege** : principe selon lequel une identité reçoit uniquement les permissions nécessaires.

**Artefact** : fichier produit ou conservé par un outil de build ou un pipeline, notamment un plan Terraform.

**Refactorisation** : modification de l'organisation du code sans changement fonctionnel ou opérationnel non voulu.

## 32. Références officielles

Consulter en priorité les documentations officielles suivantes. Les exemples de ce cours doivent être adaptés à la version Terraform, aux providers et aux règles de l'organisation.

- Documentation générale de Terraform : https://developer.hashicorp.com/terraform/docs
- Providers et contraintes de version : https://developer.hashicorp.com/terraform/language/providers/requirements
- Modules et bonnes pratiques : https://developer.hashicorp.com/terraform/tutorials/modules/module
- Backends et stockage d'état : https://developer.hashicorp.com/terraform/language/state/backends
- Verrouillage de l'état : https://developer.hashicorp.com/terraform/language/state/locking
- Backend S3 : https://developer.hashicorp.com/terraform/language/backend/s3
- Gestion des données sensibles : https://developer.hashicorp.com/terraform/language/manage-sensitive-data
- Valeurs et arguments non persistés : https://developer.hashicorp.com/terraform/language/manage-sensitive-data/write-only
- Importation de ressources : https://developer.hashicorp.com/terraform/language/import
- Bloc `moved` et refactorisation : https://developer.hashicorp.com/terraform/language/block/moved
- Validation de configuration : https://developer.hashicorp.com/terraform/language/validate
- Tests Terraform : https://developer.hashicorp.com/terraform/cli/commands/test
- Automatisation avec GitHub Actions : https://developer.hashicorp.com/terraform/tutorials/automation/github-actions

La documentation officielle des providers doit également être consultée pour connaître les arguments exacts de chaque ressource, ses contraintes de remplacement, les permissions requises et les options de sécurité disponibles.

## 33. À retenir avant le niveau expert

Le niveau intermédiaire marque le passage d'une configuration Terraform qui fonctionne à une configuration que l'on peut maintenir en équipe.

Les acquis essentiels sont les suivants :

- les modules définissent des composants réutilisables et documentés ;
- les providers et leurs versions doivent être maîtrisés ;
- l'état est une donnée critique qu'il faut protéger ;
- les environnements doivent être séparés selon leurs responsabilités et permissions ;
- les importations et refactorisations doivent préserver l'identité des objets ;
- les validations et tests doivent être intégrés au cycle de développement ;
- un pipeline ne doit pas appliquer automatiquement n'importe quel changement à la production ;
- l'identité d'exécution, l'état, les secrets et les artefacts font partie du périmètre de sécurité ;
- tout changement important doit pouvoir être examiné, expliqué et audité.

Le prochain niveau pourra s'appuyer sur ces fondations pour traiter la gouvernance Terraform à grande échelle, les architectures multi-comptes, la publication de modules internes, les politiques de conformité, les stratégies de déploiement et la gestion avancée des risques.