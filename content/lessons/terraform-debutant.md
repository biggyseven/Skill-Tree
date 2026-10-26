
# Infrastructure as Code avec Terraform — Niveau débutant

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Niveau actuel :** Débutant  
> **Objectif :** apprendre à décrire une infrastructure dans des fichiers, comprendre le fonctionnement de Terraform et effectuer ses premières opérations de manière contrôlée.


> **Lien avec le parcours DevOps IaC :** ici, tu apprends les mécanismes concrets de Terraform et HCL. Le cours « Fondamentaux de l’IaC » présente les principes communs aux outils, la revue d’un changement et les responsabilités d’équipe, sans refaire ce tutoriel technique.

## Sommaire

1. Contexte et objectifs
2. Comprendre l'Infrastructure as Code
3. Découvrir Terraform
4. Installer et vérifier Terraform
5. Comprendre la structure d'un projet
6. Découvrir le langage HCL
7. Créer ses premières ressources
8. Comprendre le cycle de vie Terraform
9. Comprendre le state
10. Variables, sorties et fichiers de valeurs
11. Sécurité et bonnes pratiques
12. Atelier pratique complet
13. Dépannage
14. Évaluation corrigée
15. Préparation du niveau intermédiaire


# 1. Contexte et objectifs

## 1.1 Pourquoi apprendre l'Infrastructure as Code ?

Une infrastructure informatique comprend des réseaux, des serveurs, des machines virtuelles, des stockages, des règles de sécurité et des services.

Lorsqu'un administrateur crée chaque ressource manuellement, il risque de reproduire des configurations différentes, d'oublier certains paramètres ou de perdre la trace des changements.

L'Infrastructure as Code, ou **IaC**, consiste à décrire l'infrastructure dans des fichiers versionnables plutôt que de dépendre uniquement d'opérations manuelles.

Cette approche facilite la répétition, la revue, la documentation et l'automatisation des déploiements.

Terraform permet de décrire des ressources à gérer au moyen d'un langage déclaratif. Ses fournisseurs (*providers*) communiquent avec les API des plateformes et des services concernés. Terraform utilise ensuite un état pour suivre les ressources qu'il gère.

## 1.2 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

1. expliquer le rôle de l'IaC ;
2. expliquer ce que Terraform fait et ce qu'il ne fait pas ;
3. reconnaître la syntaxe HCL ;
4. créer une configuration élémentaire ;
5. comprendre les blocs `terraform`, `provider`, `resource`, `variable` et `output` ;
6. utiliser `terraform init`, `fmt`, `validate`, `plan` et `apply` ;
7. comprendre le rôle du fichier `terraform.tfstate` ;
8. utiliser des variables et des sorties ;
9. distinguer une modification de configuration d'une modification réelle d'infrastructure ;
10. éviter les erreurs de sécurité les plus courantes.

## 1.3 Prérequis

Vous devez savoir :

- naviguer dans les dossiers avec un terminal ;
- créer et modifier des fichiers ;
- utiliser Git de manière élémentaire ;
- identifier une adresse IP et comprendre les notions simples de réseau.

Aucun compte cloud n'est nécessaire pour l'atelier local de ce cours.


# 2. Comprendre l'Infrastructure as Code

## 2.1 L'approche manuelle

Imaginez qu'une équipe doive créer cinq réseaux virtuels et plusieurs sous-réseaux.

Une méthode manuelle peut nécessiter de répéter les mêmes opérations dans une interface graphique. Si un paramètre est oublié, l'environnement peut devenir incohérent.

Avec une approche IaC, les caractéristiques attendues sont décrites dans des fichiers qui peuvent être examinés avant toute modification.

## 2.2 L'approche déclarative

Une approche déclarative décrit le résultat attendu. Terraform compare cette configuration aux informations dont il dispose et aux données accessibles auprès du fournisseur, puis propose des actions pour rapprocher l'infrastructure de l'état déclaré.

Exemple conceptuel :

```hcl
resource "exemple_reseau" "lan" {
  nom       = "LAN-UTILISATEURS"
  cidr_ipv4 = "10.10.0.0/16"
}
```

Ce bloc est illustratif : `exemple_reseau` n'est pas un type de ressource Terraform réel. Pour qu'un bloc fonctionne, son type doit exister dans un fournisseur installé et ses arguments doivent correspondre à sa documentation.

## 2.3 Les avantages de l'IaC

- **Reproductibilité :** conserver la description d'une infrastructure dans des fichiers.
- **Traçabilité :** utiliser Git pour examiner l'évolution des changements.
- **Collaboration :** partager les configurations et effectuer des revues.
- **Prévisibilité :** examiner un plan avant son application.
- **Réutilisation :** regrouper des configurations dans des modules.
- **Automatisation :** intégrer les validations et les plans à une chaîne CI/CD.

L'IaC ne garantit pas automatiquement une infrastructure correcte. Un fichier erroné peut produire un changement erroné. Les règles de validation, l'examen du plan et les permissions restent essentiels.


# 3. Découvrir Terraform

## 3.1 Les principaux composants

| Composant | Rôle | Exemple |
|---|---|---|
| Terraform CLI | Outil qui lit les fichiers et orchestre les opérations | `terraform plan` |
| HCL | Langage utilisé pour écrire la configuration | Fichier `.tf` |
| Provider | Plugin qui permet d'interagir avec un service | Fournisseur AWS ou local |
| Resource | Objet dont Terraform gère le cycle de vie | Réseau virtuel |
| Data source | Donnée existante consultée par Terraform | Image ou réseau existant |
| State | Informations reliant les objets gérés à leurs identifiants | `terraform.tfstate` |
| Module | Ensemble de configurations réutilisables | Module réseau |
| Plan | Proposition d'actions calculée par Terraform | `terraform plan` |
| Backend | Mécanisme qui stocke l'état | État local ou distant |

## 3.2 Comment Terraform fonctionne

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-labelledby="tf-begin-title tf-begin-desc">
  <title id="tf-begin-title">Cycle de base de Terraform</title>
  <desc id="tf-begin-desc">Les fichiers HCL passent par l'initialisation, puis Terraform génère un plan à examiner. Après approbation, apply applique les changements et met à jour l'état. Les flèches animées utilisent des tirets directionnels, sans boule mobile.</desc>
  <defs>
    <marker id="tf-begin-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .tb-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .tb-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .tb-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .tb-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .tb-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .tb-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tf-begin-arrow);animation:tb-dash 1.8s linear infinite}
      @keyframes tb-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="33" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DU CODE À L'INFRASTRUCTURE</text>
  <rect class="tb-box" x="25" y="95" width="185" height="100" rx="12"/>
  <text class="tb-title" x="117" y="127" text-anchor="middle">Configuration</text>
  <text class="tb-text" x="117" y="151" text-anchor="middle">Fichiers HCL</text>
  <text class="tb-text" x="117" y="173" text-anchor="middle">Variables + ressources</text>
  <rect class="tb-box" x="270" y="95" width="185" height="100" rx="12"/>
  <text class="tb-title" x="362" y="127" text-anchor="middle">Initialisation</text>
  <text class="tb-text" x="362" y="151" text-anchor="middle">terraform init</text>
  <text class="tb-text" x="362" y="173" text-anchor="middle">Providers + modules</text>
  <rect class="tb-gate" x="515" y="95" width="185" height="100" rx="12"/>
  <text class="tb-title" x="607" y="127" text-anchor="middle">Plan</text>
  <text class="tb-text" x="607" y="151" text-anchor="middle">Voir les changements</text>
  <text class="tb-text" x="607" y="173" text-anchor="middle">Examiner avant action</text>
  <rect class="tb-ok" x="760" y="95" width="175" height="100" rx="12"/>
  <text class="tb-title" x="847" y="127" text-anchor="middle">Apply</text>
  <text class="tb-text" x="847" y="151" text-anchor="middle">Appliquer le plan</text>
  <text class="tb-text" x="847" y="173" text-anchor="middle">Mettre à jour le state</text>
  <path class="tb-flow" d="M210 145 H263"/>
  <path class="tb-flow" d="M455 145 H508"/>
  <path class="tb-flow" d="M700 145 H753"/>
  <text class="tb-text" x="480" y="250" text-anchor="middle">Le plan doit être examiné avant qu'une action réelle soit autorisée.</text>
  <text class="tb-text" x="480" y="274" text-anchor="middle">Le contenu du plan dépend de la configuration, de l'état et du fournisseur.</text>
  <text class="tb-text" x="480" y="316" text-anchor="middle">Un plan peut créer, modifier, remplacer ou détruire des ressources.</text>
</svg>

## 3.3 La différence entre Terraform et un script impératif

Un script impératif décrit directement une suite d'actions à exécuter. Terraform déclare les ressources et calcule les changements nécessaires à partir de la configuration, de l'état et des observations du fournisseur.

Cela ne signifie pas que Terraform élimine toute dépendance à l'ordre. Les références entre ressources définissent des dépendances que Terraform utilise pour ordonner les opérations.


# 4. Installer et vérifier Terraform

## 4.1 Installation

Téléchargez Terraform depuis la documentation officielle :

https://developer.hashicorp.com/terraform/install

Choisissez la méthode correspondant à votre système d'exploitation.

Vérifiez l'installation :

```bash
terraform version
```

La commande doit afficher la version de Terraform CLI.

## 4.2 Créer un dossier de travail

```bash
mkdir terraform-debutant
cd terraform-debutant
```

Chaque exercice doit se trouver dans son propre dossier ou dans un projet clairement organisé. Évitez de mélanger l'état et les fichiers produits par des projets indépendants.


# 5. Comprendre la structure d'un projet

Un projet Terraform élémentaire peut contenir :

```text
terraform-debutant/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── versions.tf
├── .gitignore
└── README.md
```

Ces fichiers sont des conventions de rangement, pas une obligation : Terraform combine les fichiers `.tf` présents dans le même module racine.

| Fichier | Contenu habituel |
|---|---|
| `main.tf` | Ressources et logique principale |
| `variables.tf` | Déclarations de variables |
| `outputs.tf` | Valeurs retournées |
| `terraform.tfvars` | Valeurs d'entrée propres à l'environnement |
| `versions.tf` | Contraintes sur Terraform et les providers |
| `.gitignore` | Fichiers locaux à ne pas versionner |
| `README.md` | Objectif, prérequis et procédures |

Les fichiers `.tfvars` peuvent contenir des données sensibles. Ils doivent être traités en conséquence.


# 6. Découvrir le langage HCL

## 6.1 Les blocs de base

Terraform utilise le langage HCL pour déclarer les paramètres, les ressources, les variables, les sorties et les dépendances.

Exemple de déclaration de variable :

```hcl
variable "project_name" {
  description = "Nom logique du projet"
  type        = string
  default     = "lab-reseau"
}
```

Exemple de sortie :

```hcl
output "project_name" {
  description = "Nom du projet"
  value       = var.project_name
}
```

Ici, `var.project_name` désigne la valeur d'entrée. Une sortie permet d'exposer une valeur calculée ou sélectionnée par la configuration.

## 6.2 Les types de valeurs

| Type | Exemple |
|---|---|
| `string` | `"lab-reseau"` |
| `number` | `3` |
| `bool` | `true` |
| `list(string)` | `["dev", "test"]` |
| `map(string)` | `{ region = "exemple" }` |
| `object(...)` | Objet dont les champs et types sont définis |

Définir explicitement les types rend les interfaces de modules plus claires et aide à détecter les valeurs incompatibles.

## 6.3 Les références

Terraform permet de faire référence aux ressources et aux variables. Une référence entre ressources crée généralement une dépendance implicite.

Il vaut mieux utiliser les références réelles entre objets que d'imposer manuellement un ordre avec `depends_on` sans raison précise.

## 6.4 Formater les fichiers

```bash
terraform fmt
```

Cette commande formate les fichiers Terraform selon les règles standard.

Pour vérifier sans modifier les fichiers :

```bash
terraform fmt -check
```

Le formatage améliore la cohérence du code. Il ne garantit pas que la configuration produira l'infrastructure attendue.


# 7. Créer ses premières ressources

Pour apprendre sans compte cloud, nous allons utiliser le provider `local`, qui permet notamment de gérer un fichier local. L'exercice montre le cycle Terraform sans créer de réseau virtuel externe.

## 7.1 Définir les versions et le provider

Dans `versions.tf` :

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "local" {}
```

La contrainte de version du provider borne les versions autorisées dans la série 2.x. Le fichier `.terraform.lock.hcl` produit par l'initialisation doit être conservé pour stabiliser la sélection du provider dans ce projet.

Dans un projet professionnel, choisissez les contraintes après avoir vérifié les versions compatibles et les besoins de maintenance.

## 7.2 Déclarer une ressource

Dans `main.tf` :

```hcl
resource "local_file" "inventory_note" {
  filename = "${path.module}/inventory-note.txt"

  content = <<-EOT
    Projet : ${var.project_name}
    Environnement : ${var.environment}
    Objectif : exercice Infrastructure as Code
  EOT
}
```

Cette ressource crée un fichier local. Elle ne crée pas de réseau, de machine virtuelle ni de service cloud.

La valeur `path.module` correspond au chemin du module dans lequel l'expression est évaluée.

## 7.3 Ajouter les variables

Dans `variables.tf` :

```hcl
variable "project_name" {
  description = "Nom logique du projet"
  type        = string
  default     = "lab-reseau"
}

variable "environment" {
  description = "Environnement de l'exercice"
  type        = string

  validation {
    condition = contains(
      ["dev", "test", "lab"],
      var.environment
    )
    error_message = "L'environnement doit être dev, test ou lab."
  }
}
```

La validation rejette les valeurs qui ne figurent pas dans la liste autorisée.

## 7.4 Définir les valeurs par défaut

Dans `terraform.tfvars` :

```hcl
environment = "lab"
```

Les variables définies dans les fichiers de valeurs sont utilisées par Terraform selon ses règles de priorité. N'ajoutez pas un fichier de valeurs sensible au dépôt si votre politique exige qu'il reste local.

## 7.5 Ajouter une sortie

Dans `outputs.tf` :

```hcl
output "inventory_note_path" {
  description = "Chemin du fichier créé"
  value       = local_file.inventory_note.filename
}
```

Cette sortie expose le chemin du fichier créé par Terraform.


# 8. Comprendre le cycle de vie Terraform

## 8.1 Initialiser

```bash
terraform init
```

Cette opération prépare le répertoire de travail, télécharge les plugins nécessaires et initialise le backend configuré.

`terraform init` peut être relancé après certaines modifications de dépendances ou de configuration du backend. Il est généralement idempotent.

## 8.2 Formater et valider

```bash
terraform fmt -check
terraform validate
```

`terraform validate` vérifie la cohérence syntaxique et structurelle de la configuration initialisée. Il ne prouve pas que les ressources pourront être créées ni que les paramètres sont appropriés en production.

## 8.3 Générer un plan

```bash
terraform plan
```

Le plan présente les actions que Terraform propose à partir de la configuration, de l'état et des informations obtenues par les providers.

Examinez notamment :

- les ressources qui seront créées ;
- les attributs modifiés ;
- les ressources remplacées ;
- les ressources supprimées ;
- les sorties prévues.

**Un plan contenant des destructions doit toujours être examiné avec attention.**

## 8.4 Appliquer les changements

Pour cet exercice local :

```bash
terraform apply
```

Terraform présente un plan et demande normalement une confirmation interactive avant l'application, sauf si le mode d'exécution change ce comportement.

Ne passez pas directement à un `apply` automatisé sur un environnement réel sans définir la politique d'approbation et de sécurité du projet.

## 8.5 Vérifier les sorties et l'état

```bash
terraform output
terraform state list
```

Vous devriez voir la ressource locale suivie par Terraform et le chemin du fichier créé.

Inspectez le fichier :

```text
inventory-note.txt
```

Son contenu provient des valeurs déclarées dans le projet.

## 8.6 Détruire la ressource de laboratoire

```bash
terraform destroy
```

La destruction retire la ressource gérée par Terraform, selon le plan présenté et les capacités du provider. Dans cet exercice, il s'agit du fichier local créé par la ressource.

**Attention :** sur un projet réel, `terraform destroy` peut supprimer des ressources importantes et entraîner une interruption de service ou une perte de données. Ne l'exécutez jamais sans vérifier le périmètre et le plan.


# 9. Comprendre le state

## 9.1 Quel est le rôle du state ?

Terraform conserve un état qui relie les ressources déclarées aux objets suivis dans l'infrastructure.

Le state aide Terraform à déterminer les actions nécessaires lors d'un prochain plan. Il peut contenir des attributs de ressources et des informations sensibles.

Avec le backend local par défaut, Terraform utilise notamment `terraform.tfstate`. Ce fichier ne doit pas être traité comme un simple fichier de documentation.

## 9.2 Pourquoi ne pas modifier directement le state ?

Une modification manuelle incorrecte peut perturber les correspondances entre les ressources déclarées et les objets réels.

Pour inspecter l'état, utilisez :

```bash
terraform state list
terraform state show local_file.inventory_note
```

Pour des opérations de déplacement ou de migration, utilisez les commandes et mécanismes officiellement prévus par Terraform.

## 9.3 Les dangers du state local

Le state local est simple pour un laboratoire, mais présente des limites en équipe :

- il peut être perdu ;
- plusieurs administrateurs peuvent travailler avec des états différents ;
- il peut contenir des secrets ;
- les sauvegardes et les droits d'accès peuvent être insuffisants ;
- il n'est pas adapté à une collaboration concurrente sans mécanisme de coordination.

Les équipes utilisent généralement un backend distant approprié, avec protection d'accès, sauvegarde et mécanisme de verrouillage lorsqu'il est disponible.


# 10. Variables, sorties et fichiers de valeurs

## 10.1 Pourquoi utiliser des variables ?

Les variables évitent de dupliquer la même configuration dans plusieurs environnements.

Une variable peut représenter :

- un nom de projet ;
- une région ;
- un préfixe de ressources ;
- une liste de sous-réseaux ;
- une taille ou une capacité ;
- une valeur de paramétrage.

Les déclarations doivent indiquer le type, la description et, si nécessaire, des validations.

## 10.2 Valeurs et sorties

Les valeurs d'entrée configurent le comportement du module. Les sorties publient certaines valeurs produites ou récupérées par Terraform.

Les sorties peuvent exposer des informations sensibles. Le fait qu'une valeur soit déclarée comme sortie ne rend pas son contenu inoffensif.

## 10.3 Données sensibles

Exemple de variable sensible :

```hcl
variable "api_token" {
  description = "Jeton d'accès au service"
  type        = string
  sensitive   = true
  ephemeral   = true
}
```

`ephemeral` nécessite Terraform 1.10 ou une version plus récente. Il s'agit d'une fonction avancée et non d'un substitut à une gestion correcte des secrets.

La propriété `sensitive` masque certaines valeurs dans l'affichage, mais n'empêche pas à elle seule leur stockage dans le state. Les valeurs éphémères sont conçues pour ne pas être conservées dans les fichiers de state et de plan, sous réserve des restrictions d'utilisation prévues par Terraform.

Dans cet exercice, aucun jeton réel n'est nécessaire. N'en ajoutez pas pour tester la configuration locale.


# 11. Sécurité et bonnes pratiques

## 11.1 Exemple de `.gitignore`

```gitignore
# État et sauvegardes Terraform
*.tfstate
*.tfstate.*
*.tfplan
crash.log
crash.*.log

# Répertoire local de travail
.terraform/

# Fichiers de variables pouvant être sensibles
*.tfvars
*.tfvars.json

# Exceptions : conserver les modèles non sensibles
!example.tfvars
```

Les fichiers `.tfvars` peuvent contenir des paramètres non sensibles, mais ils peuvent aussi inclure des secrets. Si vous décidez d'en versionner certains, vérifiez soigneusement leur contenu et utilisez une liste d'autorisation précise.

Conservez le fichier `.terraform.lock.hcl` dans le contrôle de versions d'un projet racine pour stabiliser les sélections de providers.

## 11.2 Ne pas enregistrer les secrets en clair

Les secrets ne doivent pas être placés dans :

- des variables codées en dur ;
- des fichiers versionnés ;
- des journaux ;
- des sorties de diagnostic partagées ;
- des plans ou des états accessibles sans protection.

Terraform peut enregistrer des valeurs sensibles dans le state selon les ressources et les arguments utilisés. La protection des données doit donc couvrir le state, les plans et les sauvegardes.

## 11.3 Séparer les opérations

Le cycle recommandé pour apprendre est :

```text
Modifier
   ↓
Formater
   ↓
Valider
   ↓
Générer le plan
   ↓
Examiner le plan
   ↓
Appliquer si autorisé
   ↓
Vérifier le résultat
```

Ne remplacez pas l'examen du plan par une confiance aveugle dans la configuration.


# 12. Atelier pratique complet

## Scénario

Vous devez créer une configuration Terraform qui produit un fichier de documentation d'inventaire pour un laboratoire réseau.

L'exercice ne nécessite pas d'identifiants cloud ni de ressource facturée.

### Étape A — Créer les fichiers

Créez :

```text
versions.tf
main.tf
variables.tf
outputs.tf
terraform.tfvars
```

Utilisez les exemples des sections précédentes.

### Étape B — Initialiser le projet

```bash
terraform init
```

L'initialisation doit télécharger le provider local et créer ou mettre à jour le verrouillage des dépendances.

### Étape C — Contrôler la configuration

```bash
terraform fmt
terraform validate
```

Corrigez chaque erreur signalée avant de poursuivre.

### Étape D — Examiner le plan

```bash
terraform plan
```

Vérifiez que Terraform propose uniquement la ressource locale attendue. Ne vous contentez pas de vérifier que la commande se termine sans erreur.

### Étape E — Appliquer

```bash
terraform apply
```

Examinez le plan présenté et confirmez uniquement si les actions correspondent à l'exercice.

### Étape F — Vérifier le résultat

```bash
terraform output
terraform state list
```

Examinez le fichier produit et vérifiez que le chemin correspond à la sortie déclarée.

### Étape G — Nettoyer le laboratoire

```bash
terraform destroy
```

Vérifiez le plan de destruction avant de confirmer.

Le laboratoire est terminé lorsque la ressource a été créée, identifiée dans le state, vérifiée puis supprimée selon le plan attendu.


# 13. Dépannage

## 13.1 Terraform n'est pas reconnu

Vérifiez l'installation et la variable d'environnement PATH, puis ouvrez un nouveau terminal si nécessaire.

## 13.2 Le provider n'est pas installé

Relancez `terraform init` et vérifiez la connectivité du poste, la source du provider et les contraintes de version.

## 13.3 `terraform validate` échoue

Lisez le fichier et le numéro de ligne signalés. Vérifiez les accolades, les noms de variables, les types et l'existence des arguments.

## 13.4 Le plan propose un remplacement inattendu

Examinez les attributs dont la modification provoque le remplacement et consultez la documentation du provider. Certains arguments ne peuvent pas être changés en place.

## 13.5 L'état ne correspond plus à l'infrastructure

Un changement manuel ou une suppression externe peut créer un décalage. Examinez l'état avec les commandes prévues et consultez le plan. N'effacez pas le state simplement pour faire disparaître un problème.

## 13.6 Un secret apparaît dans le state

Traitez le state comme une donnée sensible. Révoquez ou renouvelez les secrets exposés et mettez en œuvre la procédure de sécurisation de l'organisation.


# 14. Évaluation corrigée

## Questions

1. Qu'est-ce que l'Infrastructure as Code ?
2. Quel est le rôle d'un provider ?
3. Quelle différence existe entre une ressource et une data source ?
4. Pourquoi utiliser `terraform plan` ?
5. À quoi sert `terraform init` ?
6. Pourquoi ne pas modifier directement le state ?
7. Pourquoi faut-il examiner un plan qui contient des destructions ?
8. Quelle est la différence entre `sensitive` et `ephemeral` ?
9. Pourquoi versionner `.terraform.lock.hcl` ?
10. Pourquoi l'IaC ne garantit-elle pas automatiquement une infrastructure correcte ?

## Corrigé

1. Une méthode qui décrit et gère l'infrastructure à l'aide de configurations versionnables.
2. Il fournit l'intégration avec un service ou une plateforme.
3. Une ressource est gérée par Terraform ; une data source lit des informations existantes.
4. Pour examiner les actions prévues avant leur application.
5. Pour préparer le répertoire, installer les plugins requis et initialiser le backend.
6. Pour éviter de corrompre les correspondances entre les ressources et l'état suivi.
7. Parce que les destructions peuvent supprimer des ressources ou interrompre des services.
8. `sensitive` masque des valeurs dans certains affichages ; `ephemeral` permet à certaines valeurs de ne pas être enregistrées dans le state et les plans.
9. Pour conserver les sélections et contrôles des versions de providers du projet.
10. Parce que Terraform applique une configuration qui peut être incorrecte ou inadaptée. Les validations et revues restent essentielles.


# 15. Préparation du niveau intermédiaire

Le niveau intermédiaire prolongera ce socle avec :

- des infrastructures réseau concrètes ;
- des providers cloud et des contraintes de version ;
- des variables et objets complexes ;
- des modules réutilisables ;
- des data sources et des dépendances ;
- des tests Terraform ;
- la séparation des environnements ;
- les plans enregistrés ;
- une première chaîne CI.

**À retenir :** Terraform décrit l'état attendu, calcule les écarts et applique un plan. Le rôle de l'administrateur est de s'assurer que le plan correspond bien à l'intention.


## Références officielles

- Présentation de Terraform : https://developer.hashicorp.com/terraform/intro
- Langage Terraform : https://developer.hashicorp.com/terraform/language
- Installation : https://developer.hashicorp.com/terraform/install
- Commande `init` : https://developer.hashicorp.com/terraform/cli/commands/init
- Gestion du state : https://developer.hashicorp.com/terraform/language/state
- Gestion des données sensibles : https://developer.hashicorp.com/terraform/language/manage-sensitive-data
- Tutoriels officiels : https://developer.hashicorp.com/terraform/tutorials
