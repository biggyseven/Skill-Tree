# IaC à grande échelle

## 1. Positionnement dans le parcours Terraform

Ce cours prolonge les connaissances acquises dans le niveau intermédiaire consacré à Terraform.

Le parcours est organisé en trois étapes :

1. **Débutant :** comprendre l'Infrastructure as Code, écrire des configurations Terraform, utiliser les variables et les outputs, créer des ressources et exécuter `init`, `plan` et `apply`.
2. **Intermédiaire :** structurer les configurations, concevoir des modules réutilisables, gérer les providers, utiliser un backend distant, comprendre le state, automatiser les déploiements et intégrer Terraform dans un pipeline CI/CD.
3. **Expert :** industrialiser Terraform dans une organisation, organiser les états et les environnements, versionner les modules, mettre en place des politiques de sécurité, tester les configurations, contrôler les changements et maintenir une architecture IaC à grande échelle.

Le niveau expert ne doit donc pas reprendre tout le parcours depuis zéro. Il réutilise les mécanismes déjà connus et les place dans une architecture d'entreprise.

### 1.1 Prérequis

Les connaissances suivantes sont considérées comme acquises :

- syntaxe HCL et structure d'un projet Terraform ;
- providers, ressources, sources de données et outputs ;
- variables, locals, collections et expressions ;
- modules enfants et modules racines ;
- `count` et `for_each` ;
- dépendances entre ressources ;
- fichiers de configuration des providers ;
- `terraform init`, `terraform validate`, `terraform plan` et `terraform apply` ;
- état Terraform, backend distant et verrouillage ;
- Git et revue des modifications ;
- notions de CI/CD et de gestion des secrets.

Les exemples utilisent des configurations Terraform et parfois un environnement cloud fictif. Les noms et les attributs propres à AWS, Azure, GCP ou à un autre fournisseur doivent être adaptés au provider choisi.

### 1.2 Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit pouvoir :

- définir une architecture IaC répartie sur plusieurs environnements ;
- choisir la bonne granularité des états Terraform ;
- organiser les responsabilités entre équipes ;
- créer et maintenir un catalogue de modules versionnés ;
- automatiser les tests et la validation des changements ;
- intégrer des contrôles de sécurité et des politiques organisationnelles ;
- utiliser des identités temporaires pour les pipelines ;
- détecter et traiter la dérive d'infrastructure ;
- migrer des ressources et des états sans destruction accidentelle ;
- gérer les mises à jour de Terraform et de ses providers ;
- concevoir des workflows de déploiement avec approbations ;
- définir une stratégie de sauvegarde, de reprise et d'audit.

## 2. Comprendre ce qui change à grande échelle

Une configuration Terraform simple peut fonctionner correctement avec quelques ressources et une seule personne.

Les difficultés apparaissent lorsque plusieurs équipes modifient des infrastructures partagées, que des environnements doivent être isolés, que les déploiements doivent être auditables et que les changements doivent être effectués sans interruption de service.

### 2.1 Du projet individuel à la plateforme

Architecture simplifiée d'un petit projet :

```text
Administrateur
     |
     v
Configuration Terraform
     |
     v
terraform plan / apply
     |
     v
Infrastructure cloud
```

Architecture d'une plateforme IaC d'entreprise :

```text
                         DEVELOPPEURS
                              |
                              v
                         Dépôts Git
                              |
                              v
                    Revues et contrôles CI
                              |
                 +------------+------------+
                 |            |            |
                 v            v            v
              Tests       Sécurité      Politiques
                 |            |            |
                 +------------+------------+
                              |
                              v
                       Plan Terraform
                              |
                              v
                    Approbation contrôlée
                              |
                              v
                       Apply Terraform
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          Environnement    Environnement   Environnement
             de test       de préprod       de production

   Bibliothèque de modules versionnés et approuvés
                              |
                              v
                   Configurations racines

   Gestion sécurisée des identités et des états
                              |
                              v
                     Backend distant
```

Cette architecture introduit plusieurs responsabilités qui doivent être traitées séparément :

- le code décrit l'infrastructure souhaitée ;
- les modules encapsulent des composants réutilisables ;
- les états représentent les objets gérés par chaque configuration racine ;
- les pipelines contrôlent les changements ;
- les politiques encadrent les configurations autorisées ;
- les systèmes d'identité déterminent qui peut agir et sur quelles ressources ;
- les journaux et les sauvegardes permettent de comprendre et de restaurer les opérations.

### 2.2 Les principaux risques d'une mauvaise architecture

| Problème | Conséquence possible | Réponse architecturale |
|---|---|---|
| Un état gigantesque | Plans lents, grand rayon d'impact | Fractionner selon le cycle de vie et les responsabilités |
| Des modules copiés partout | Corrections incohérentes | Bibliothèque de modules versionnés |
| Des droits cloud partagés | Actions excessives ou non attribuables | Identités distinctes et privilèges minimaux |
| Des déploiements manuels | Changements non reproductibles | Pipeline standardisé |
| Des ressources modifiées hors Terraform | Dérive entre code et infrastructure | Détection et traitement de la dérive |
| Des secrets dans Git | Exposition potentielle d'identifiants | Gestionnaire de secrets et identités temporaires |
| Des mises à jour non testées | Régressions et remplacements inattendus | Verrouillage des versions et tests |
| Des dépendances entre états implicites | Déploiements dans le mauvais ordre | Graphe de dépendances explicite et orchestration |

## 3. Concevoir la gouvernance de l'Infrastructure as Code

À grande échelle, une architecture ne repose pas uniquement sur du code. Elle repose aussi sur des règles de propriété, de responsabilité et de changement.

### 3.1 Définir les responsabilités

Une organisation peut répartir les responsabilités entre plusieurs fonctions.

| Fonction | Responsabilités principales |
|---|---|
| Équipe plateforme | Modules communs, conventions, outillage, modèles de pipeline |
| Équipe sécurité | Politiques, identités, exigences de chiffrement, contrôles d'accès |
| Équipes applicatives | Besoins applicatifs, paramètres et ressources de leur périmètre |
| Équipe opérations | Surveillance, capacité de reprise, incidents et disponibilité |
| Responsables des environnements critiques | Approbation des changements à fort impact |
| Mainteneurs des modules | Compatibilité, tests, publication et gestion des versions |

Cette répartition ne signifie pas que toutes les organisations doivent avoir des équipes séparées. Une petite entreprise peut réunir plusieurs rôles dans une même équipe. L'important est que les responsabilités soient identifiées et que les actions sensibles ne dépendent pas uniquement de conventions informelles.

### 3.2 Définir un modèle de responsabilité

Chaque composant important doit avoir :

- un propriétaire identifié ;
- un dépôt ou un emplacement de code de référence ;
- un cycle de vie documenté ;
- des règles d'accès ;
- une méthode de déploiement ;
- des procédures d'incident et de restauration ;
- un mécanisme de mise à jour.

Par exemple, le réseau central peut être possédé par l'équipe plateforme, tandis qu'une base de données applicative peut être gérée par l'équipe responsable de l'application.

Il est dangereux que plusieurs équipes considèrent simultanément qu'elles sont les propriétaires exclusifs d'une même infrastructure.

### 3.3 Créer des conventions organisationnelles

Des conventions utiles concernent :

- les noms des ressources ;
- les noms des variables et outputs ;
- les tags ou labels de gestion ;
- la structure des dépôts ;
- la version minimale de Terraform ;
- les versions de providers admises ;
- les règles de publication des modules ;
- les exigences de sécurité ;
- les validations obligatoires ;
- les exceptions aux règles communes.

L'objectif n'est pas de standardiser chaque détail. Il s'agit surtout de standardiser les éléments qui ont un impact sur la sécurité, la maintenabilité et l'exploitation.

## 4. Choisir l'architecture des dépôts

La structure Git influence directement les workflows de développement et de déploiement.

Il existe plusieurs modèles. Aucun n'est universellement supérieur aux autres.

### 4.1 Monorepo

Un monorepo regroupe plusieurs composants IaC dans un même dépôt.

```text
infrastructure/
├── modules/
│   ├── network/
│   ├── storage/
│   ├── iam-baseline/
│   └── application/
├── live/
│   ├── dev/
│   │   ├── network/
│   │   └── application/
│   ├── staging/
│   │   ├── network/
│   │   └── application/
│   └── prod/
│       ├── network/
│       └── application/
├── policies/
├── tests/
└── README.md
```

Avantages :

- visibilité globale sur l'architecture ;
- modifications coordonnées possibles ;
- changements entre un module et ses consommateurs faciles à examiner ;
- conventions centralisées.

Limites :

- les pipelines doivent détecter les répertoires affectés ;
- les droits peuvent être plus difficiles à isoler par composant ;
- une mauvaise configuration du pipeline peut déclencher trop de déploiements ;
- les modules peuvent devenir fortement couplés.

Dans ce modèle, chaque répertoire racine de déploiement doit avoir un backend et un état adaptés à son périmètre.

Le fait de stocker dix configurations dans un seul dépôt ne signifie pas qu'elles doivent toutes utiliser le même état.

### 4.2 Multirepo

Dans un modèle multirepo, les modules et les configurations de déploiement sont répartis dans différents dépôts.

```text
module-network/
module-storage/
module-iam/
module-application/
infra-dev/
infra-staging/
infra-prod/
```

Avantages :

- propriété et droits par dépôt ;
- pipelines ciblés ;
- versionnement indépendant ;
- séparation claire entre une bibliothèque partagée et ses consommateurs.

Limites :

- coordination des mises à jour ;
- gestion des dépendances entre dépôts ;
- besoin d'un processus de publication des modules ;
- risque de conserver longtemps des versions obsolètes.

### 4.3 Modèle hybride

Une approche fréquente consiste à utiliser :

- un dépôt pour les modules communs ;
- un dépôt par domaine de responsabilité ou par groupe d'applications ;
- des configurations racines distinctes par environnement ou composant ;
- un catalogue central de politiques et de workflows réutilisables.

Cette architecture permet d'équilibrer autonomie et standardisation.

### 4.4 Comment choisir ?

Le choix doit être guidé par :

1. le nombre d'équipes ;
2. les responsabilités et les frontières d'accès ;
3. les cycles de publication ;
4. les dépendances entre composants ;
5. le rayon d'impact des déploiements ;
6. la capacité de maintenance des pipelines.

Il ne faut ni imposer un dépôt par ressource, ni placer toute l'infrastructure dans un unique état monolithique.

## 5. Concevoir les états Terraform à grande échelle

L'état est l'un des éléments les plus importants de l'architecture Terraform.

Il contient l'association entre les adresses de ressources Terraform et les objets réels que Terraform gère, ainsi que des données nécessaires au suivi de ces objets. Selon les providers et les ressources, il peut contenir des informations sensibles.

### 5.1 Pourquoi fractionner les états ?

Un état représente un périmètre de gestion. Il ne doit pas nécessairement correspondre à un environnement entier, ni à un seul service applicatif.

Le choix dépend principalement de trois critères :

- **cycle de vie** : les composants évoluent-ils et sont-ils supprimés ensemble ?
- **responsabilité** : sont-ils gérés par la même équipe ?
- **rayon d'impact** : une modification doit-elle pouvoir affecter tous les composants concernés en une seule opération ?

Exemple d'architecture :

```text
Organisation
|
+-- État 1 : identité et gouvernance
|
+-- État 2 : réseau central
|
+-- État 3 : réseau de production
|
+-- État 4 : services partagés
|
+-- État 5 : application de paiement
|
+-- État 6 : application analytique
|
+-- État 7 : environnement de test
```

Une configuration applicative ne devrait généralement pas être en mesure de détruire le réseau central simplement parce que ces ressources ont été placées dans le même état.

### 5.2 Les erreurs de granularité

**Un état trop grand**

- plans potentiellement longs ;
- nombreuses ressources évaluées simultanément ;
- conflits d'accès plus fréquents ;
- conséquences plus importantes d'une erreur ;
- responsabilités difficiles à séparer.

**Des états trop petits**

- multiplication des backends et des configurations ;
- orchestration plus complexe ;
- dépendances plus nombreuses ;
- difficulté à comprendre l'architecture de bout en bout ;
- coûts de maintenance et d'exploitation plus élevés.

Le bon découpage vise l'indépendance opérationnelle, et non le nombre maximal d'états.

### 5.3 Séparer les environnements

Les environnements ayant des exigences de sécurité différentes doivent bénéficier de frontières d'accès adaptées.

Exemple :

```text
AWS ou autre plateforme cloud
|
+-- Compte de développement
|   +-- État réseau-dev
|   +-- État application-dev
|
+-- Compte de préproduction
|   +-- État réseau-staging
|   +-- État application-staging
|
+-- Compte de production
    +-- État réseau-prod
    +-- État application-prod
```

Lorsque le fournisseur cloud le permet, la séparation en comptes ou abonnements distincts fournit une frontière plus forte que le simple changement du nom d'un workspace.

### 5.4 Workspaces Terraform et isolation

Deux concepts sont souvent confondus :

- les workspaces CLI Terraform, qui permettent de gérer plusieurs états associés à une configuration ;
- les workspaces d'une plateforme d'exécution comme HCP Terraform, qui apportent aussi un contexte d'exécution, des paramètres et des contrôles d'accès.

Les workspaces CLI ne doivent pas être considérés automatiquement comme une frontière de sécurité entre production et développement.

Pour des environnements critiques, il peut être préférable d'utiliser des configurations racines, des états, des identités et des permissions distincts.

### 5.5 Exemple de structure des états

```text
live/
├── organization/
│   └── governance/
├── production/
│   ├── network/
│   ├── shared-services/
│   ├── payments/
│   └── analytics/
├── staging/
│   ├── network/
│   └── applications/
└── development/
    ├── network/
    └── sandbox/
```

Chaque sous-répertoire de déploiement constitue une configuration racine indépendante. Il peut disposer de son propre backend, de ses variables, de son cycle de déploiement et de son identité.

## 6. Sécuriser et exploiter les backends

Un backend distant permet de partager l'état entre les exécutants autorisés et de gérer le verrouillage lorsqu'il est pris en charge.

Il doit être traité comme une ressource critique de l'organisation.

### 6.1 Exigences minimales

Un backend de production devrait fournir, selon les possibilités de la plateforme :

- authentification contrôlée ;
- permissions minimales ;
- chiffrement au repos et en transit ;
- verrouillage des opérations concurrentes ;
- versionnement ou sauvegarde de l'état ;
- journalisation des accès ;
- procédure de restauration ;
- séparation des droits de lecture et de modification, si possible.

Le verrouillage réduit le risque que plusieurs opérations modifient simultanément un même état. Il n'empêche pas les erreurs de conception ou les changements manuels dans le cloud.

### 6.2 Exemple de backend S3

Un backend S3 peut utiliser le verrouillage natif par fichier de verrouillage avec une version Terraform qui prend en charge cette fonctionnalité.

```hcl
terraform {
  backend "s3" {
    bucket       = "company-terraform-state"
    key          = "production/payments/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

Points importants :

- le bucket doit exister avant l'initialisation du backend ;
- le versionnement du bucket doit être activé ;
- l'accès doit être limité aux chemins d'état nécessaires ;
- l'identité de déploiement ne doit pas obtenir des droits généraux sur tous les comptes ;
- les identifiants ne doivent pas être écrits en dur dans la configuration ;
- les permissions nécessaires au fichier de verrouillage doivent être configurées ;
- la récupération d'une ancienne version doit suivre une procédure contrôlée.

Le nom de région dans l'exemple doit être remplacé par la région réellement utilisée. Il ne faut pas copier la configuration de production sans adapter les paramètres et les politiques d'accès.

### 6.3 Exemple de backend HCP Terraform

```hcl
terraform {
  cloud {
    organization = "company-platform"

    workspaces {
      name = "production-payments"
    }
  }
}
```

Cet exemple illustre le rattachement d'une configuration à un workspace HCP Terraform nommé. Le workspace doit être préparé et autorisé selon le modèle d'accès de l'organisation.

HCP Terraform peut centraliser l'exécution, les états, les permissions, l'historique des opérations et certains contrôles de gouvernance.

Le choix entre HCP Terraform et un backend objet autogéré dépend des besoins d'exploitation, des capacités disponibles, des contraintes de sécurité et du niveau d'automatisation souhaité.

### 6.4 Le state contient potentiellement des secrets

La déclaration suivante :

```hcl
output "database_password" {
  value     = var.database_password
  sensitive = true
}
```

masque la valeur dans plusieurs affichages Terraform, mais ne signifie pas que la donnée disparaît de l'état.

La propriété `sensitive` est avant tout une protection d'affichage. Les fichiers d'état, les journaux, les sauvegardes et les plans doivent donc être protégés comme des données potentiellement sensibles.

Bonnes pratiques :

- ne jamais versionner un fichier `.tfstate` ;
- restreindre l'accès au backend ;
- éviter les outputs sensibles inutiles ;
- protéger les sauvegardes ;
- limiter l'accès aux plans sauvegardés ;
- ne pas publier l'état dans des artefacts CI accessibles à tous ;
- préférer, lorsque c'est possible, des mécanismes qui évitent de placer des secrets durables dans l'état.

### 6.5 Les fichiers de plan sont aussi sensibles

La commande suivante sauvegarde un plan :

```bash
terraform plan -out=tfplan
```

Le plan sauvegardé peut contenir des valeurs sensibles, même lorsque celles-ci sont masquées dans l'affichage du terminal.

Il faut traiter `tfplan` comme un artefact confidentiel. Sa conservation, sa durée de vie et ses permissions doivent être contrôlées.

## 7. Organiser un catalogue de modules réutilisables

Le module est l'unité de réutilisation de Terraform. À grande échelle, un catalogue de modules permet de centraliser les bonnes pratiques et de réduire les divergences entre équipes.

Mais un module ne devient pas utile simplement parce qu'une ressource a été placée dans un répertoire.

### 7.1 Les catégories de modules

On peut distinguer trois catégories.

**Modules de base**

Ils encapsulent une capacité précise, par exemple :

- une configuration réseau ;
- un espace de stockage ;
- un rôle IAM ;
- une règle de pare-feu ;
- une identité applicative.

Ils doivent rester relativement génériques et avoir peu de responsabilités.

**Modules de composition**

Ils combinent plusieurs modules ou ressources pour réaliser une fonction plus large, par exemple :

- un service web complet ;
- une plateforme de données ;
- une application avec réseau, base de données et surveillance.

**Configurations racines**

Elles assemblent des modules et fournissent les paramètres propres à un environnement.

```text
Configuration racine : production
|
+-- Module réseau
|
+-- Module identité applicative
|
+-- Module service
|
+-- Module surveillance
```

La configuration racine reste responsable de la composition et des décisions spécifiques à l'environnement. Elle ne devrait pas être remplacée par un module excessivement rigide qui impose tous les choix.

### 7.2 Favoriser la composition plutôt que l'imbrication excessive

Une hiérarchie très profonde est difficile à comprendre.

Architecture peu souhaitable :

```text
root
  |
  +-- platform
        |
        +-- foundation
              |
              +-- network-system
                    |
                    +-- network-component
```

Architecture plus simple :

```text
root
  |
  +-- module-network
  |
  +-- module-identity
  |
  +-- module-application
```

La composition par le module racine facilite la réutilisation des composants dans différentes architectures.

### 7.3 Structure d'un module

Exemple :

```text
modules/
└── network/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── versions.tf
    ├── README.md
    ├── examples/
    └── tests/
```

Le nom des fichiers n'est pas une règle du langage Terraform, mais cette structure rend le module plus facile à parcourir.

Le fichier `README.md` doit notamment expliquer :

- le rôle du module ;
- ses entrées et sorties ;
- les prérequis ;
- les permissions nécessaires ;
- les options de sécurité ;
- les comportements qui provoquent un remplacement ;
- les instructions de test ;
- les versions compatibles ;
- les limites connues.

### 7.4 Concevoir une interface de module stable

Un module partagé est une interface publique. Chaque variable exposée augmente les possibilités, mais aussi la complexité de maintenance.

Exemple :

```hcl
variable "name" {
  description = "Nom logique du composant."
  type        = string

  validation {
    condition     = length(trimspace(var.name)) > 2
    error_message = "Le nom doit comporter au moins trois caractères non blancs."
  }
}

variable "environment" {
  description = "Environnement de déploiement."
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "L'environnement doit être dev, staging ou prod."
  }
}

variable "tags" {
  description = "Métadonnées appliquées aux ressources compatibles."
  type        = map(string)
  default     = {}
}
```

Ce code illustre la validation d'une interface. Il ne remplace pas les contraintes propres au fournisseur cloud ou à la ressource.

Il faut éviter d'exposer des dizaines de variables représentant chaque attribut d'une ressource, sauf si les consommateurs doivent réellement pouvoir les contrôler.

### 7.5 Éviter les valeurs par défaut dangereuses

Une valeur par défaut qui facilite le développement peut être inacceptable en production.

Par exemple :

```hcl
variable "public_access" {
  description = "Autoriser l'accès public si la ressource le permet."
  type        = bool
  default     = false
}
```

Cette valeur est plus sûre qu'un défaut permissif. Toutefois, une valeur par défaut ne remplace pas une politique de gouvernance capable de bloquer les configurations non conformes.

### 7.6 Utiliser correctement `for_each`

`for_each` permet de gérer des collections stables de composants.

```hcl
variable "buckets" {
  type = map(object({
    purpose = string
    tags    = map(string)
  }))
}

module "storage" {
  source   = "../modules/storage"
  for_each = var.buckets

  name    = each.key
  purpose = each.value.purpose
  tags    = each.value.tags
}
```

Le module `storage` doit réellement accepter les variables présentées dans cet exemple. Les attributs sont illustratifs : ils doivent correspondre à l'interface du module créé.

Pour `for_each`, les clés doivent être déterminables au moment de la planification et ne peuvent pas être des valeurs sensibles.

### 7.7 Contrôler les dépendances

Terraform déduit la plupart des dépendances à partir des références entre ressources.

Une référence telle que :

```hcl
subnet_id = module.network.private_subnet_id
```

exprime une dépendance entre le composant qui utilise le sous-réseau et le module réseau.

Il faut éviter d'ajouter systématiquement `depends_on`. Cette déclaration est utile lorsque la dépendance existe réellement, mais n'est pas détectable à travers les références habituelles.

Une utilisation excessive peut rendre le plan plus conservateur et introduire des valeurs inconnues inutiles.

## 8. Versionner et publier les modules

Une bibliothèque de modules ne peut pas être administrée uniquement en copiant les modifications sur la branche principale.

Elle doit avoir un cycle de vie.

### 8.1 Versionnement sémantique

Un modèle courant est le versionnement sémantique :

```text
MAJEURE.MINEURE.CORRECTIF

2.4.1
| | |
| | +-- Correctif compatible
| +---- Nouvelle fonctionnalité compatible
+------ Changement incompatible
```

Exemples :

- `2.4.1` : correction qui conserve l'interface publique ;
- `2.5.0` : fonctionnalité compatible ajoutée ;
- `3.0.0` : changement incompatible qui nécessite une migration.

Une modification n'est pas nécessairement compatible parce que le code HCL reste syntaxiquement valide. Elle peut modifier le comportement, les valeurs par défaut, les règles de remplacement ou le nom des ressources gérées.

### 8.2 Contrôler les versions consommées

Avec un module publié dans un registre :

```hcl
module "network" {
  source  = "app.terraform.io/company/network/cloud"
  version = "2.4.1"

  name        = "production-network"
  environment = "prod"
}
```

Le chemin `source` est un exemple de registre privé. Il doit être remplacé par l'adresse réelle du registre et du module.

Avec un dépôt Git :

```hcl
module "network" {
  source = "git::https://git.example.com/platform/network.git?ref=v2.4.1"

  name        = "production-network"
  environment = "prod"
}
```

Une étiquette Git peut être déplacée par un mainteneur disposant des permissions appropriées. Pour les environnements critiques, il faut protéger les tags et définir une politique d'immuabilité ou utiliser une référence de commit appropriée.

Le fichier `.terraform.lock.hcl` verrouille les dépendances des providers, mais il ne remplace pas le versionnement explicite des modules.

### 8.3 Pipeline de publication d'un module

```text
Pull request
     |
     v
Formatage et validation
     |
     v
Tests du module
     |
     v
Contrôles de sécurité
     |
     v
Revue et fusion
     |
     v
Version et changelog
     |
     v
Publication
     |
     v
Tests de compatibilité des consommateurs
     |
     v
Adoption progressive
```

Une version de module ne doit pas être publiée uniquement parce que son code a été fusionné. Elle doit satisfaire des contrôles documentés.

### 8.4 Stratégie de migration des versions

Pour une mise à jour importante :

1. identifier les configurations qui utilisent l'ancienne version ;
2. consulter les changements incompatibles ;
3. tester la nouvelle version dans un environnement isolé ;
4. produire et examiner le plan ;
5. vérifier les remplacements et destructions ;
6. déployer progressivement ;
7. documenter les exceptions ;
8. retirer les anciennes versions selon une politique explicite.

Il faut éviter de mettre automatiquement à jour toutes les configurations de production lorsqu'une nouvelle version est publiée.

## 9. Standardiser les configurations racines

Une configuration racine est un point de contrôle opérationnel.

Elle détermine les versions requises, le backend, les providers, les variables d'environnement et les modules utilisés.

### 9.1 Exemple d'organisation

```text
live/
└── production/
    └── payments/
        ├── versions.tf
        ├── providers.tf
        ├── variables.tf
        ├── locals.tf
        ├── main.tf
        ├── outputs.tf
        └── README.md
```

Cette configuration racine doit être déployable de manière indépendante et disposer d'une identité ayant uniquement les droits requis.

### 9.2 Verrouiller les versions des providers

Exemple :

```hcl
terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

La contrainte ci-dessus est illustrative et ne constitue pas une recommandation de version actuelle du provider AWS. Une équipe doit choisir une plage compatible avec ses tests et sa stratégie de maintenance.

Le fichier `.terraform.lock.hcl` doit être versionné avec la configuration pour assurer une résolution reproductible des providers.

En CI, une initialisation avec verrouillage en lecture seule peut être utilisée après que le fichier de verrouillage a été créé et validé :

```bash
terraform init -lockfile=readonly
```

Cette option évite qu'un pipeline modifie silencieusement les sélections de providers enregistrées dans le fichier de verrouillage.

### 9.3 Regrouper les tags organisationnels

Les tags ou labels sont utiles pour l'inventaire, le suivi des coûts, la propriété et les opérations.

```hcl
variable "environment" {
  type = string
}

variable "owner" {
  type = string
}

variable "application" {
  type = string
}

locals {
  common_tags = {
    Environment = var.environment
    Owner       = var.owner
    Application = var.application
    ManagedBy   = "Terraform"
  }
}
```

Les tags doivent être propagés vers les ressources compatibles par le module ou le provider. Un bloc `locals` seul ne garantit pas leur application sur toutes les ressources.

Ne placez pas de données personnelles, de secrets ou d'informations de sécurité confidentielles dans les tags.

## 10. Organiser les dépendances entre états

Les dépendances entre ressources dans un même état sont gérées par le graphe Terraform. Les dépendances entre états distincts constituent un problème d'orchestration.

### 10.1 Exemple de dépendances inter-états

```text
État : identité et gouvernance
              |
              v
État : réseau
              |
              v
État : services partagés
              |
              v
État : application
```

Cet ordre signifie que le réseau doit être disponible avant que l'application puisse consommer ses sous-réseaux.

Terraform ne garantit pas automatiquement cet ordre entre plusieurs configurations racines indépendantes. Il faut le gérer dans le pipeline ou dans un outil d'orchestration.

### 10.2 Transmettre les informations nécessaires

Une configuration peut avoir besoin de récupérer l'identifiant d'un réseau créé ailleurs.

Différentes options existent :

- publier explicitement les informations nécessaires comme variables de configuration ;
- exploiter une source de données du provider pour retrouver une ressource par identifiant ou par tag ;
- utiliser un système de publication d'outputs sécurisé ;
- accéder à un état distant lorsque le modèle de droits le permet.

L'accès direct à un état distant doit être examiné avec soin. Selon le backend et les droits accordés, l'identité du consommateur peut obtenir un accès beaucoup plus large que les seuls outputs attendus.

Il ne faut pas exposer un état complet à une équipe simplement pour lui transmettre un identifiant de sous-réseau.

### 10.3 Réduire le couplage

Un module d'application devrait recevoir l'identifiant du réseau dont il a besoin :

```hcl
variable "subnet_ids" {
  description = "Identifiants des sous-réseaux utilisés par l'application."
  type        = list(string)
}
```

La configuration racine transmet ensuite la valeur appropriée à partir d'une source autorisée.

Cette approche réduit le couplage entre le module applicatif et le mécanisme particulier utilisé pour créer le réseau.

### 10.4 Orchestration en plusieurs phases

```text
Phase 1 : fondations
    Identité, gouvernance, réseau central

Phase 2 : services partagés
    DNS, journalisation, observabilité, services communs

Phase 3 : applications
    Ressources applicatives et dépendances

Phase 4 : vérifications
    Tests de connectivité, santé, contrôles post-déploiement
```

Un pipeline doit arrêter ou bloquer les phases suivantes si une dépendance critique n'est pas prête.

Pour une modification du réseau, il ne suffit pas de considérer que `terraform apply` a réussi. Les tests de connectivité et les contrôles opérationnels peuvent être nécessaires avant d'autoriser le déploiement applicatif.

## 11. Automatiser les contrôles dans la CI/CD

Les pipelines CI/CD constituent une barrière importante entre une modification de code et une modification réelle de l'infrastructure.

Le niveau intermédiaire CI/CD a présenté les mécanismes des pipelines. Cette section les applique à une plateforme Terraform partagée.

### 11.1 Pipeline de pull request

Un pipeline de validation peut suivre cet ordre :

```text
Modification de code
       |
       v
Vérification du format
       |
       v
Initialisation sans déploiement
       |
       v
Validation Terraform
       |
       v
Tests des modules
       |
       v
Scan de sécurité
       |
       v
Vérification des politiques
       |
       v
Plan Terraform
       |
       v
Revue humaine
```

Exemples de commandes de base :

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

`terraform init -backend=false` permet d'initialiser la configuration sans activer le backend configuré. Il ne remplace pas une vérification complète contre l'environnement réel.

Le plan de préproduction ou de production nécessite des identités autorisées et un backend approprié. Le modèle de permissions doit également tenir compte du fait que les pipelines de pull request peuvent exécuter du code non encore approuvé.

### 11.2 Pipeline de déploiement

```text
Commit approuvé
       |
       v
Plan Terraform
       |
       v
Analyse du plan
       |
       +-- Destruction importante ?
       |          |
       |          v
       |      Revue renforcée
       |
       v
Approbation requise
       |
       v
Application du plan sauvegardé
       |
       v
Tests après déploiement
       |
       v
Audit et notification
```

La planification doit être effectuée avec une identité appropriée et les accès nécessaires au backend.

Une validation humaine ne doit pas se limiter à un message « plan réussi ». Elle doit tenir compte du nombre de ressources créées, modifiées, remplacées et détruites, ainsi que de l'impact métier potentiel.

### 11.3 Utiliser le plan sauvegardé

Exemple local de workflow :

```bash
terraform init
terraform validate
terraform plan -out=tfplan

# Examiner le plan avant tout changement réel.
terraform show tfplan

# Seulement après la validation et l'approbation nécessaires.
terraform apply tfplan
```

Ce modèle évite de calculer un nouveau plan lors de l'étape d'application. Le plan doit néanmoins correspondre au code, à l'état et au contexte approuvés.

Dans un pipeline séparant les étapes, l'artefact doit être protégé et la chaîne doit garantir qu'il provient de la révision approuvée. Si le code, l'état ou le contexte ont changé, il peut être nécessaire de recalculer et de réexaminer le plan.

### 11.4 Protéger les pipelines de production

Pratiques importantes :

- exiger une revue pour les changements sensibles ;
- utiliser les environnements protégés de la plateforme CI/CD ;
- limiter qui peut déclencher une application en production ;
- séparer les droits de planification et d'application lorsque cela est pertinent ;
- utiliser des identités distinctes par environnement ;
- protéger les artefacts contenant des plans ;
- éviter les secrets dans les logs ;
- éviter de donner un accès de production aux pipelines exécutant du code de contributeurs non approuvés ;
- conserver l'identifiant du commit, le plan approuvé et le résultat de l'application.

La configuration exacte dépend du service CI/CD utilisé et de ses capacités de protection des environnements.

## 12. Authentification des pipelines et identités temporaires

Une erreur fréquente consiste à stocker des clés cloud permanentes dans les variables de CI/CD.

Cela peut fonctionner, mais augmente les risques liés au vol, à la fuite ou à la réutilisation de ces clés.

### 12.1 Préférer les identités temporaires

Lorsque le fournisseur le permet, une fédération d'identité fondée sur OIDC peut permettre à un pipeline d'obtenir des droits temporaires.

```text
Pipeline CI/CD
      |
      v
Jeton d'identité OIDC
      |
      v
Vérification de la relation de confiance
      |
      v
Rôle autorisé pour le dépôt,
la branche et l'environnement
      |
      v
Identifiants temporaires
      |
      v
Terraform
      |
      v
API cloud
```

Le détail de la configuration dépend du fournisseur cloud et de la plateforme CI/CD.

### 12.2 Réduire les permissions

Un pipeline qui déploie une application dans un compte ne devrait pas automatiquement pouvoir :

- administrer l'ensemble de l'organisation ;
- modifier les politiques de sécurité globales ;
- supprimer les comptes cloud ;
- lire tous les états Terraform ;
- modifier les identités d'autres équipes ;
- accéder aux environnements sans rapport avec le déploiement.

Le rôle doit être limité aux opérations nécessaires, au compte concerné et, lorsque cela est possible, aux types de ressources ou périmètres concernés.

### 12.3 Séparer les identités selon les tâches

Exemple conceptuel :

```text
Identité validation
    -> droits de lecture nécessaires

Identité déploiement développement
    -> droits limités à dev

Identité déploiement préproduction
    -> droits limités à staging

Identité déploiement production
    -> droits de production, approbation et audit

Identité administration plateforme
    -> opérations exceptionnelles fortement contrôlées
```

Les permissions effectives doivent également permettre les opérations du backend, pas uniquement celles des ressources cloud.

### 12.4 Sécurité des événements CI

Un pipeline peut devenir un point d'entrée si les workflows de contribution et les secrets sont mal contrôlés.

Il faut examiner :

- les événements qui déclenchent les workflows ;
- la provenance du code exécuté ;
- les permissions du jeton CI ;
- les actions et dépendances externes utilisées ;
- les accès OIDC ;
- le partage des logs et des artefacts ;
- les approbations pour les environnements critiques.

Il faut notamment éviter qu'une modification non approuvée puisse déclencher un déploiement avec une identité de production.

## 13. Gouvernance avec les politiques « as code »

Une politique de gouvernance définit des règles qui doivent s'appliquer à plusieurs équipes.

Sans politique automatisée, chaque équipe peut appliquer les conventions différemment et les contrôles humains deviennent difficiles à maintenir.

### 13.1 Exemples de règles

Une organisation peut imposer :

- des régions cloud autorisées ;
- le chiffrement des données sensibles ;
- la journalisation obligatoire ;
- des tags de propriété ;
- l'absence d'accès public non autorisé ;
- des tailles minimales ou maximales ;
- des catégories de services interdites ;
- des exigences de sauvegarde ;
- des environnements de production protégés ;
- des limites de coûts ou de capacité.

### 13.2 Contrôle local et contrôle centralisé

**Contrôles dans la configuration**

Ils peuvent vérifier les entrées et certaines conditions :

```hcl
variable "environment" {
  type = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Environnement non autorisé."
  }
}
```

**Contrôles centralisés**

Une plateforme peut analyser le plan Terraform et bloquer les changements non conformes, indépendamment de la manière dont le module a été écrit.

Une politique centralisée est particulièrement utile lorsque plusieurs équipes consomment des modules provenant de différentes sources.

### 13.3 Choisir un moteur de politiques

Selon l'architecture et les services utilisés, les possibilités comprennent :

- Sentinel dans les environnements qui le prennent en charge ;
- Open Policy Agent (OPA) et le langage Rego ;
- les fonctionnalités de politique disponibles dans HCP Terraform ;
- des outils de contrôle de configuration dans le pipeline.

Ces solutions n'ont pas exactement les mêmes capacités et ne s'exécutent pas toutes au même endroit. Il faut sélectionner l'outil en fonction du processus d'exécution, des données disponibles et du niveau d'application attendu.

### 13.4 Exemple de pipeline de politiques

```text
Plan Terraform
      |
      v
Représentation JSON du plan
      |
      v
Moteur de politiques
      |
      +-- Politique respectée
      |       |
      |       v
      |    Continuer
      |
      +-- Avertissement
      |       |
      |       v
      |    Revue ou exception
      |
      +-- Violation bloquante
              |
              v
          Déploiement interdit
```

`terraform show -json` permet d'obtenir une représentation JSON d'un plan sauvegardé :

```bash
terraform show -json tfplan > tfplan.json
```

Le JSON peut contenir des informations sensibles. Il ne doit pas être publié dans un artefact général, un dépôt ou un service externe sans une analyse des risques et des permissions.

### 13.5 Avertissement ou blocage ?

Toutes les règles ne devraient pas nécessairement bloquer immédiatement le développement.

Une politique peut avoir un niveau :

- informatif ;
- consultatif ;
- bloquant.

Exemple de progression :

```text
Étape 1 : mesurer les non-conformités
Étape 2 : informer les équipes
Étape 3 : corriger les principaux écarts
Étape 4 : bloquer les violations critiques
Étape 5 : auditer les exceptions
```

Pour les règles critiques, le passage à un contrôle bloquant doit être explicite. Une dérogation doit avoir un propriétaire, une justification et une durée de validité.

## 14. Tester les modules Terraform

Le test est essentiel dès que les modules sont consommés par plusieurs équipes.

Un module incorrect peut reproduire la même erreur dans des dizaines d'environnements.

### 14.1 Pyramide de tests

```text
               Tests de déploiement
              /                    \
             /   Tests intégration   \
            /------------------------\
           /    Tests de modules      \
          /----------------------------\
         / Syntaxe, types, lint et règles\
        /________________________________\
```

Les contrôles les plus rapides doivent être exécutés fréquemment. Les tests qui créent de véritables ressources peuvent être plus lents et nécessiter des permissions et des coûts.

### 14.2 Tests statiques

Contrôles de base :

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

D'autres contrôles peuvent être ajoutés :

- analyse du code HCL ;
- vérification des versions et de la structure des modules ;
- détection de configurations dangereuses ;
- vérification des règles organisationnelles ;
- comparaison du plan avec des conditions attendues.

Un contrôle statique ne prouve pas que l'infrastructure sera opérationnelle ou que les permissions sont suffisantes.

### 14.3 Tests Terraform natifs

Terraform propose un mécanisme de test qui utilise des fichiers tels que :

```text
tests/
└── module.tftest.hcl
```

Les tests peuvent valider certaines conditions après une planification ou après un déploiement de test.

Exemple conceptuel :

```hcl
run "validate_environment" {
  command = plan

  variables {
    environment = "prod"
  }

  assert {
    condition     = output.environment == "prod"
    error_message = "La valeur de l'environnement n'est pas correcte."
  }
}
```

Ce test suppose que la configuration possède un output `environment` et une interface compatible avec la variable utilisée. Il doit être adapté au module réel.

### 14.4 Mocks et tests sans infrastructure réelle

Les mécanismes de mocking permettent de remplacer certains comportements des providers pendant les tests pris en charge par Terraform.

Ils sont utiles pour tester certaines parties de la logique sans créer systématiquement les ressources sur un cloud.

Ils ne vérifient cependant pas tout le comportement d'une API distante. Les tests avec mocks doivent compléter, et non remplacer complètement, les tests d'intégration nécessaires.

### 14.5 Tests d'intégration

Un test d'intégration peut :

1. créer un environnement éphémère ;
2. déployer un module ou un ensemble de modules ;
3. vérifier la présence et la configuration des ressources ;
4. tester les accès et la connectivité ;
5. vérifier les contraintes de sécurité ;
6. supprimer les ressources de test ;
7. enregistrer le résultat.

Ces tests doivent prévoir le nettoyage, y compris lorsqu'une étape échoue.

Pour les ressources critiques, il faut aussi confirmer que la suppression de l'environnement temporaire ne peut pas toucher les ressources de production.

### 14.6 Exigences minimales avant publication d'un module

- formatage validé ;
- configuration syntaxiquement valide ;
- interfaces documentées ;
- tests de validation réussis ;
- politique de compatibilité définie ;
- absence de secrets intégrés ;
- changements incompatibles identifiés ;
- exemples documentés ;
- changelog mis à jour ;
- approbation de publication obtenue.

## 15. Gérer les dérives d'infrastructure

Une dérive apparaît lorsque l'infrastructure réelle n'est plus conforme à la configuration attendue.

Elle peut résulter :

- d'une modification manuelle dans le cloud ;
- d'une opération d'urgence ;
- d'un changement effectué par un autre outil ;
- d'une évolution externe d'une ressource ;
- d'une configuration Terraform mise à jour sans application correspondante.

### 15.1 Cycle de détection

```text
Configuration Git
       |
       v
Plan Terraform
       |
       v
Lecture de l'infrastructure
       |
       v
Comparaison avec l'état et la configuration
       |
       +-- Aucune différence significative
       |        |
       |        v
       |      Continuer
       |
       +-- Dérive détectée
                |
                v
          Analyse de l'origine
                |
         +------+------+
         |             |
         v             v
  Modifier le code   Réconcilier la
  et appliquer       ressource réelle
```

### 15.2 Ne pas corriger automatiquement toutes les dérives

Une différence entre le code et la ressource réelle n'est pas toujours une erreur qu'il faut corriger immédiatement.

Par exemple, un administrateur peut avoir changé temporairement une règle de pare-feu lors d'un incident.

Avant d'appliquer une correction, il faut comprendre :

- qui a modifié la ressource ;
- pourquoi le changement a eu lieu ;
- si la configuration du dépôt doit être modifiée ;
- si le changement manuel était une exception temporaire ;
- si une correction automatique peut interrompre un service.

### 15.3 Workflow de traitement

1. détecter la dérive ;
2. identifier la ressource concernée ;
3. consulter les journaux cloud et les événements de déploiement ;
4. déterminer la configuration souhaitée ;
5. modifier la configuration Terraform si nécessaire ;
6. produire un plan et l'examiner ;
7. appliquer la correction approuvée ;
8. vérifier l'état final ;
9. documenter la cause et prévenir une récidive.

### 15.4 Utiliser le mode refresh-only avec prudence

Le mode refresh-only permet d'actualiser les informations de l'état à partir de l'infrastructure réelle sans chercher à appliquer les modifications normales de configuration.

Exemple de plan :

```bash
terraform plan -refresh-only
```

Il peut servir à examiner les différences entre l'état et les valeurs observées dans l'infrastructure.

Il ne doit pas être utilisé pour faire disparaître une dérive sans comprendre ses conséquences. Actualiser un état n'équivaut pas à valider l'architecture réelle.

### 15.5 Détection régulière

Une organisation peut programmer des plans de contrôle à intervalles réguliers, ou utiliser les fonctionnalités de détection de dérive de sa plateforme d'exécution.

La fréquence dépend de la criticité, de la vitesse d'évolution et du coût des opérations de lecture.

Pour une infrastructure de production, la détection régulière doit être associée à un processus de traitement, pas seulement à un rapport ignoré.

## 16. Refactoriser les configurations sans détruire les ressources

À mesure que les modules se développent, les équipes doivent renommer des ressources, déplacer des blocs et extraire des modules.

Un renommage naïf peut conduire Terraform à considérer qu'une ressource ancienne doit être supprimée et qu'une nouvelle doit être créée.

### 16.1 Exemple de renommage

Avant :

```hcl
resource "example_resource" "old_name" {
  name = "production-service"
}
```

Après :

```hcl
resource "example_resource" "service" {
  name = "production-service"
}
```

Terraform voit deux adresses différentes :

```text
example_resource.old_name
example_resource.service
```

Sans mécanisme de migration de l'adresse, Terraform peut proposer une destruction suivie d'une création.

### 16.2 Utiliser un bloc `moved`

```hcl
moved {
  from = example_resource.old_name
  to   = example_resource.service
}
```

Ce bloc indique à Terraform que l'adresse suivie dans l'état doit être transférée vers la nouvelle adresse.

Il peut être utilisé pour plusieurs scénarios de refactorisation compatibles, notamment des renommages ou des déplacements dans des modules.

Il faut ensuite examiner le plan pour confirmer que le déplacement ne déclenche pas une recréation inattendue.

### 16.3 Pourquoi éviter les migrations improvisées ?

Une migration improvisée peut entraîner :

- une perte de suivi des ressources ;
- des remplacements non prévus ;
- une divergence entre la configuration et l'état ;
- des erreurs lors des déploiements suivants ;
- une interruption du service ;
- des difficultés de retour arrière.

Une migration doit être traitée comme un changement d'infrastructure à part entière.

### 16.4 Procédure de refactorisation

```text
1. Geler les changements concurrents
             |
             v
2. Sauvegarder l'état selon la procédure prévue
             |
             v
3. Modifier le code et déclarer les déplacements
             |
             v
4. Initialiser et valider la configuration
             |
             v
5. Produire le plan
             |
             v
6. Vérifier les destructions et remplacements
             |
             v
7. Appliquer avec contrôle
             |
             v
8. Vérifier le plan après migration
             |
             v
9. Mettre à jour la documentation
```

La commande `terraform state mv` peut être utile dans certains scénarios de migration, mais une modification directe de l'état doit faire l'objet d'un contrôle renforcé. La méthode de migration doit être choisie après analyse de la structure et des contraintes du backend.

## 17. Importer et reprendre la gestion des ressources existantes

Dans une organisation, toutes les ressources ne sont pas nécessairement créées initialement par Terraform.

Certaines peuvent provenir de configurations manuelles, d'anciens scripts ou d'un outil précédent.

Il est alors nécessaire de les associer correctement à une configuration Terraform.

### 17.1 Principe de l'import

L'import associe une ressource existante à une adresse de ressource Terraform. Il ne signifie pas automatiquement que le code représente exactement la configuration réelle.

Après l'import, la configuration doit être examinée et un plan produit pour vérifier la convergence entre l'infrastructure et le code souhaité.

### 17.2 Import déclaratif

Terraform prend en charge les blocs `import` pour déclarer des opérations d'import dans la configuration.

Exemple de forme générale :

```hcl
import {
  to = example_resource.existing
  id = "existing-resource-id"
}
```

Le type `example_resource` et la structure de l'identifiant sont fictifs. Le provider réel définit les ressources importables et les formats d'identifiant attendus.

### 17.3 Approche de reprise en gestion

1. inventorier les ressources ;
2. confirmer leur propriétaire ;
3. vérifier qu'aucune autre configuration ne les gère déjà ;
4. identifier le format d'import fourni par le provider ;
5. écrire une configuration cohérente avec l'état réel ;
6. importer la ressource ;
7. produire un plan ;
8. corriger les différences ;
9. définir la responsabilité future et la procédure d'exploitation.

Il faut éviter d'importer une ressource dans deux états distincts. Cette situation peut provoquer des conflits de gestion et des actions destructrices.

## 18. Gérer les mises à jour de Terraform et des providers

À grande échelle, un simple changement de version peut affecter de nombreuses configurations.

Les mises à jour doivent donc être organisées.

### 18.1 Les différentes versions à contrôler

Une organisation doit distinguer :

- la version du binaire Terraform ;
- les versions des providers ;
- les versions des modules internes ;
- les versions des actions et outils CI/CD ;
- les versions des moteurs de politiques ;
- les versions des outils de scan.

Ces composants évoluent indépendamment et peuvent avoir des contraintes de compatibilité.

### 18.2 Stratégie de mise à jour

```text
Veille de sécurité et de compatibilité
               |
               v
Environnement de test
               |
               v
Suite de tests et validation
               |
               v
Plans comparatifs
               |
               v
Déploiement pilote
               |
               v
Déploiement progressif
               |
               v
Suivi des résultats
```

### 18.3 Éviter les changements multiples non contrôlés

Il est généralement plus facile d'expliquer un plan si la modification concerne une version de provider, une version de module ou un changement fonctionnel clairement identifié.

Une mise à jour simultanée de multiples dépendances peut produire des changements difficiles à attribuer.

Il faut également surveiller les avis de sécurité et les changements incompatibles des outils utilisés.

### 18.4 Ne pas ignorer les contraintes de version

Une contrainte telle que :

```hcl
required_version = ">= 1.7.0, < 2.0.0"
```

exprime une plage de versions Terraform compatibles avec la configuration.

Elle n'impose pas à elle seule un binaire identique pour tous les environnements. La version exacte utilisée par le pipeline doit aussi être contrôlée.

Les versions sélectionnées doivent correspondre à celles avec lesquelles la suite de tests a été exécutée.

## 19. Maîtriser le rayon d'impact et les opérations dangereuses

Toutes les modifications Terraform n'ont pas le même niveau de risque.

Un ajustement de description et une destruction de base de données ne doivent pas suivre exactement le même niveau d'approbation.

### 19.1 Catégoriser les changements

| Catégorie | Exemple | Contrôle conseillé |
|---|---|---|
| Faible | Documentation, métadonnées non critiques | Contrôles automatisés |
| Modérée | Ajout de ressource sans interruption attendue | Plan et revue habituelle |
| Élevée | Modification réseau ou IAM | Revue spécialisée et plan détaillé |
| Critique | Destruction de données, remplacement d'une base, changement d'identité centrale | Approbation renforcée et procédure d'exploitation |

La catégorie doit être déterminée à partir de l'impact réel. Certaines modifications apparemment mineures peuvent avoir un effet majeur si elles concernent une politique d'accès partagée.

### 19.2 Examiner les remplacements

Pendant la revue d'un plan, il faut distinguer :

- les créations ;
- les modifications en place ;
- les destructions ;
- les remplacements impliquant destruction et création ;
- les déplacements d'adresses ;
- les changements de dépendances.

Une modification signalée comme remplacement doit être examinée à la lumière du comportement réel du provider.

### 19.3 Utiliser `-replace` avec discernement

Terraform permet de demander explicitement le remplacement d'une ressource :

```bash
terraform plan -replace=example_resource.service
```

La ressource fictive doit être remplacée par l'adresse exacte de celle concernée.

Cette option doit être réservée à un cas identifié. Elle ne doit pas être utilisée comme solution générale à un plan difficile à comprendre.

De même, `-target` est un outil de ciblage utile dans certains scénarios exceptionnels, mais ne doit pas remplacer le workflow normal de planification. Il peut conduire à une application partielle qui ne reflète pas les changements attendus de l'ensemble de la configuration.

### 19.4 Plan d'urgence

Une procédure d'urgence doit préciser :

- qui peut déclencher l'opération ;
- quelles permissions peuvent être accordées exceptionnellement ;
- comment le changement est journalisé ;
- comment la configuration est réconciliée après l'incident ;
- qui examine le changement a posteriori ;
- comment les accès temporaires sont révoqués.

L'objectif est de conserver la traçabilité même lorsque les délais normaux de validation doivent être adaptés.

## 20. Optimiser les performances de Terraform

Les performances deviennent importantes lorsque les configurations contiennent de nombreuses ressources et que plusieurs pipelines fonctionnent simultanément.

### 20.1 Identifier la véritable source de lenteur

Un pipeline lent peut être dû à :

- un graphe de dépendances complexe ;
- des appels API distants ;
- des limites de débit des providers ;
- un backend lent ;
- une configuration racine trop large ;
- des opérations de lecture redondantes ;
- des tests d'intégration coûteux ;
- des files d'attente et des verrous ;
- une initialisation répétitive des providers et modules.

Avant de modifier l'architecture, il faut mesurer les phases les plus lentes.

### 20.2 Ajuster le parallélisme avec prudence

Terraform permet de contrôler le parallélisme avec l'option `-parallelism`.

```bash
terraform plan -parallelism=5
```

La valeur est illustrative, pas une recommandation universelle.

Augmenter le parallélisme peut accélérer certaines opérations, mais peut aussi aggraver les limitations de débit ou la charge d'un service distant.

### 20.3 Fractionner les configurations lorsqu'il y a une bonne raison

Le fractionnement peut être utile lorsque :

- les composants ont des propriétaires distincts ;
- ils disposent de cycles de vie différents ;
- leur déploiement est indépendant ;
- les plans sont devenus difficiles à examiner ;
- une frontière de sécurité impose un état séparé.

Il ne faut toutefois pas créer un état par ressource. Chaque état supplémentaire ajoute des coûts d'orchestration et de maintenance.

### 20.4 Éviter les dépendances artificielles

Un grand nombre de `depends_on` placés au niveau des modules peut contraindre Terraform à considérer des opérations inconnues jusqu'à des étapes ultérieures.

Il est préférable d'exprimer les relations nécessaires en transmettant les valeurs utiles entre composants.

La qualité du graphe de dépendances est souvent plus importante qu'un simple ajustement du nombre d'opérations parallèles.

## 21. Gouverner les coûts de l'infrastructure

L'IaC à grande échelle doit prendre en compte la consommation financière.

La possibilité de créer rapidement de nombreuses ressources est aussi un risque lorsque les quotas, les environnements temporaires ou les ressources coûteuses ne sont pas surveillés.

### 21.1 Contrôles de coûts possibles

- budgets par équipe ou environnement ;
- tags obligatoires pour la facturation ;
- quotas cloud ;
- limites d'utilisation des environnements temporaires ;
- analyse des ressources coûteuses dans les plans ;
- planification de la suppression des environnements de test ;
- revue des volumes de stockage et des sauvegardes ;
- politiques sur les tailles et catégories de ressources autorisées.

### 21.2 L'analyse des coûts n'est pas une garantie

Une estimation calculée à partir d'un plan peut ne pas couvrir tous les coûts indirects, les changements de consommation ou les frais dépendant de l'utilisation.

Elle doit être combinée à la facturation réelle et à la surveillance des consommations.

### 21.3 Cycle de vie des environnements éphémères

Un environnement créé pour un test doit avoir un responsable et une procédure de nettoyage.

```text
Demande de test
      |
      v
Création de l'environnement
      |
      v
Exécution des validations
      |
      v
Collecte des résultats
      |
      v
Suppression contrôlée
      |
      v
Vérification du nettoyage
```

Le nettoyage ne doit pas supprimer des ressources partagées. La séparation des états et les règles de nommage doivent rendre le périmètre temporaire identifiable.

## 22. Sauvegarde, restauration et reprise après incident

Le backend doit être disponible, mais il faut aussi prévoir les situations où un état est corrompu, supprimé ou modifié de manière incorrecte.

### 22.1 Principes de reprise

Une stratégie de reprise comprend :

- la sauvegarde ou le versionnement du state ;
- la protection des identités utilisées pour la restauration ;
- une procédure d'accès aux anciennes versions ;
- la vérification de l'intégrité des sauvegardes ;
- la documentation des opérations à risque ;
- une procédure de réconciliation après restauration.

### 22.2 Restaurer un état n'est pas restaurer l'infrastructure

Cette distinction est essentielle.

```text
Sauvegarde du state
       |
       v
Restauration de l'état
       |
       v
État Terraform récupéré

MAIS

Infrastructure cloud
       |
       v
Peut avoir continué à évoluer
       |
       v
Requiert une réconciliation
```

Le state est une représentation de gestion. Restaurer un ancien état ne ramène pas automatiquement les ressources cloud à leur configuration passée.

### 22.3 Procédure en cas de corruption présumée

1. suspendre les opérations concurrentes ;
2. identifier le backend et l'état concernés ;
3. préserver les journaux et les versions disponibles ;
4. vérifier la cause de l'incident ;
5. sélectionner la méthode de récupération ;
6. restaurer ou corriger l'état sous contrôle ;
7. produire un plan et vérifier les différences ;
8. confirmer l'absence de destructions imprévues ;
9. reprendre les opérations progressivement ;
10. documenter les causes et les corrections nécessaires.

Il faut éviter de lancer immédiatement un `apply` après une restauration sans examiner la différence entre l'infrastructure et l'état récupéré.

## 23. Exemple d'architecture IaC d'entreprise

Considérons une entreprise comportant :

- plusieurs équipes ;
- des applications de production ;
- des environnements de préproduction et de développement ;
- une plateforme cloud ;
- des exigences de sécurité et de traçabilité.

### 23.1 Architecture logique

```text
                         Dépôts Git
                             |
             +---------------+---------------+
             |                               |
             v                               v
    Dépôt des modules              Dépôts des déploiements
             |                               |
             v                               v
     Publication versionnée          Pipelines par périmètre
             |                               |
             +---------------+---------------+
                             |
                             v
                   Contrôles centralisés
                    /       |       \
                   /        |        \
                  v         v         v
               Tests    Politiques  Analyse coûts
                   \        |        /
                    \       |       /
                             |
                             v
                       Plan approuvé
                             |
                             v
                      Identité dédiée
                             |
               +-------------+-------------+
               |             |             |
               v             v             v
             Dev          Staging          Prod
               |             |             |
               v             v             v
            État(s)       État(s)        État(s)
               |             |             |
               +-------------+-------------+
                             |
                             v
                    Audit et surveillance
```

### 23.2 Structure de dépôt possible

```text
infrastructure/
├── modules/
│   ├── network/
│   ├── identity/
│   ├── storage/
│   ├── observability/
│   └── application/
├── live/
│   ├── development/
│   │   ├── network/
│   │   └── applications/
│   ├── staging/
│   │   ├── network/
│   │   └── applications/
│   └── production/
│       ├── network/
│       ├── shared-services/
│       ├── payments/
│       └── analytics/
├── policies/
├── scripts/
├── tests/
└── README.md
```

Cette structure est un point de départ. Dans une organisation multirepo, les modules et les configurations de déploiement peuvent être séparés dans différents dépôts.

### 23.3 Exemple de composition d'une configuration racine

```hcl
module "network" {
  source  = "app.terraform.io/company/network/cloud"
  version = "2.4.1"

  name        = "payments-prod"
  environment = "prod"
}

module "application" {
  source  = "app.terraform.io/company/application/cloud"
  version = "1.8.0"

  name        = "payments-api"
  environment = "prod"

  subnet_ids = module.network.private_subnet_ids
}
```

Cet exemple illustre la composition de deux modules. Les noms des sources et les variables doivent être remplacés par ceux des modules réellement publiés dans l'organisation.

La référence aux sous-réseaux exprime une dépendance détectable par Terraform. Il n'est pas nécessaire d'ajouter un `depends_on` artificiel entre ces deux blocs.

La configuration racine ne contient pas les détails de toutes les ressources. Elle assemble les capacités tout en gardant le contrôle sur les décisions propres à l'environnement.

## 24. Atelier pratique : créer une architecture IaC multi-environnements

### 24.1 Objectif

Construire une architecture de dépôt dans laquelle :

- les modules sont distincts des configurations racines ;
- les environnements sont séparés ;
- les versions sont explicites ;
- les validations peuvent être exécutées en CI ;
- le déploiement de production nécessite un contrôle renforcé.

Le laboratoire peut être réalisé sans créer de ressources cloud réelles, en commençant par l'organisation des fichiers et les validations statiques.

### 24.2 Préparer le dépôt

Créer la structure suivante :

```text
iac-platform-lab/
├── modules/
│   └── example-service/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
└── live/
    ├── dev/
    │   └── example-service/
    ├── staging/
    │   └── example-service/
    └── prod/
        └── example-service/
```

Chaque répertoire `example-service` sous `live` représente une configuration racine distincte.

### 24.3 Créer un module simple

Fichier `modules/example-service/variables.tf` :

```hcl
variable "name" {
  description = "Nom du service."
  type        = string

  validation {
    condition     = length(trimspace(var.name)) >= 3
    error_message = "Le nom doit contenir au moins trois caractères."
  }
}

variable "environment" {
  description = "Environnement cible."
  type        = string

  validation {
    condition = contains(
      ["dev", "staging", "prod"],
      var.environment
    )

    error_message = "Environnement non autorisé."
  }
}
```

Fichier `modules/example-service/main.tf` :

```hcl
locals {
  service_name = "${var.name}-${var.environment}"
}
```

Fichier `modules/example-service/outputs.tf` :

```hcl
output "service_name" {
  description = "Nom logique du service."
  value       = local.service_name
}
```

Ce module ne crée volontairement aucune ressource cloud. Il sert à illustrer l'organisation d'un module et son interface.

### 24.4 Créer la configuration racine de développement

Fichier `live/dev/example-service/main.tf` :

```hcl
module "service" {
  source = "../../../modules/example-service"

  name        = "demo"
  environment = "dev"
}

output "service_name" {
  value = module.service.service_name
}
```

Le chemin relatif est calculé à partir du répertoire de la configuration racine.

Fichier `live/dev/example-service/versions.tf` :

```hcl
terraform {
  required_version = ">= 1.7.0, < 2.0.0"
}
```

Cette configuration d'exercice ne requiert pas de provider puisqu'elle ne crée aucune ressource et n'en interroge aucune. Dans un véritable module cloud, il faudra déclarer et verrouiller les providers nécessaires.

### 24.5 Valider la configuration

Se placer dans la configuration racine :

```bash
cd live/dev/example-service

terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform plan
```

La commande `plan` permet ici de vérifier la configuration et les outputs. Le comportement exact dépend de la version Terraform installée, qui doit respecter la contrainte indiquée.

### 24.6 Créer les autres environnements

Créer les configurations racines `staging` et `prod` avec les paramètres correspondants.

Chaque répertoire doit avoir une méthode de gestion de l'état adaptée au contexte. Il ne faut pas ajouter un backend de production avant d'avoir préparé et sécurisé les ressources nécessaires à ce backend.

### 24.7 Points de contrôle

Vérifier que :

- les modules sont séparés du code propre à chaque environnement ;
- le nom de l'environnement ne peut prendre que les valeurs admises ;
- les validations fonctionnent ;
- chaque configuration racine peut être validée indépendamment ;
- les secrets ne sont pas présents dans Git ;
- les permissions de production ne sont pas utilisées par le workflow de développement.

## 25. Atelier pratique : mettre en place une chaîne de validation

### 25.1 Objectif

Créer un pipeline qui contrôle une configuration Terraform avant de permettre son utilisation dans un environnement partagé.

Le pipeline doit au minimum :

1. vérifier la mise en forme ;
2. initialiser les dépendances ;
3. valider la syntaxe ;
4. exécuter les tests disponibles ;
5. exécuter les contrôles de sécurité choisis ;
6. produire un rapport de plan lorsque l'identité et le backend le permettent.

### 25.2 Étapes de validation communes

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

L'initialisation avec `-backend=false` est adaptée à plusieurs contrôles statiques. Elle n'active pas le backend qui serait utilisé lors d'un déploiement réel.

### 25.3 Ajouter les tests

Pour les modules disposant de tests Terraform :

```bash
terraform test
```

Cette commande doit être exécutée dans le contexte de la configuration ou du module concerné.

Les tests qui déploient des ressources doivent être exécutés dans un environnement de test contrôlé. Ils ne doivent pas pouvoir accéder librement à la production.

### 25.4 Contrôler le plan

Dans un environnement qui dispose des autorisations nécessaires :

```bash
terraform plan -out=tfplan
terraform show tfplan
```

Le résultat doit être examiné avant le déploiement.

Un pipeline de production doit préserver la provenance du plan, son lien avec le commit et les approbations exigées. Le fichier de plan doit être traité comme un artefact confidentiel.

### 25.5 Ajouter la revue et l'application

L'application ne doit être accessible qu'après les étapes prévues par la politique de l'organisation.

```text
Code approuvé
     |
     v
Validation
     |
     v
Plan
     |
     v
Revue humaine si requise
     |
     v
Application contrôlée
     |
     v
Vérification post-déploiement
```

L'automatisation ne supprime pas le besoin de contrôle : elle le rend cohérent, reproductible et traçable.

## 26. Atelier pratique : introduire une politique de gouvernance

### 26.1 Objectif

Définir une règle simple au niveau d'un module puis réfléchir à la façon de l'appliquer centralement.

Règle de l'exercice :

> Un environnement doit appartenir à l'ensemble des environnements officiellement autorisés.

### 26.2 Validation locale

Le module précédent utilise déjà une validation de variable pour imposer cette règle.

Essayer une valeur invalide :

```hcl
environment = "experimental-prod"
```

La validation doit échouer avant toute création de ressource.

### 26.3 Pourquoi cette validation ne suffit pas

Une règle dans un module peut être contournée si un autre module ne l'implémente pas, si un autre chemin de déploiement est utilisé ou si des ressources sont créées sans passer par le module standard.

Pour une exigence importante, une politique centralisée doit également inspecter les modifications envisagées ou contrôler l'environnement cible.

### 26.4 Travail demandé

Concevoir une politique organisationnelle qui impose au minimum :

- la présence d'un propriétaire ;
- l'utilisation de modules approuvés en production ;
- les régions cloud autorisées ;
- les règles de chiffrement requises ;
- les restrictions d'accès public ;
- une procédure d'exception tracée.

L'implémentation exacte dépendra du fournisseur cloud, des données du plan et du moteur de politiques sélectionné.

## 27. Diagnostic des problèmes fréquents

### 27.1 Verrouillage d'état

Symptôme : Terraform ne peut pas acquérir le verrou de l'état.

Causes possibles :

- une autre opération utilise déjà l'état ;
- une opération précédente s'est terminée anormalement ;
- le mécanisme de verrouillage n'est pas correctement configuré ;
- les permissions du backend sont insuffisantes.

Démarche :

1. vérifier les opérations en cours ;
2. consulter l'historique du pipeline ;
3. vérifier l'état du verrou ;
4. déterminer si une opération détient encore légitimement le verrou ;
5. ne retirer un verrou qu'après confirmation qu'il est réellement orphelin et selon la procédure du backend.

La commande `terraform force-unlock` ne doit pas être utilisée pour contourner automatiquement un verrou actif.

### 27.2 Le plan propose des destructions inattendues

Causes possibles :

- déplacement ou renommage de ressources ;
- modification d'un paramètre entraînant un remplacement ;
- mauvais environnement ou mauvais backend ;
- modification des clés de `for_each` ;
- changement de provider ;
- divergence entre le code et l'infrastructure réelle.

Démarche :

1. ne pas appliquer le plan ;
2. vérifier le workspace, le backend et l'identité ;
3. analyser les adresses des ressources ;
4. contrôler les changements qui provoquent un remplacement ;
5. examiner les refactorisations et les paramètres ;
6. ajuster le code et recalculer le plan.

### 27.3 Une équipe ne peut pas lire un état distant

Causes possibles :

- permissions insuffisantes sur le backend ;
- rôle incorrect ;
- état situé dans un autre périmètre ;
- mauvaise référence à la sortie attendue ;
- politiques de la plateforme d'exécution.

Il ne faut pas résoudre automatiquement le problème en accordant un accès global. Il faut vérifier quelle information est nécessaire et accorder les droits minimaux appropriés.

### 27.4 Une mise à jour de provider provoque des différences inattendues

Démarche :

1. vérifier la version réellement installée ;
2. examiner `.terraform.lock.hcl` ;
3. identifier la version introduite par le changement ;
4. consulter les notes de version du provider ;
5. reproduire dans un environnement isolé ;
6. vérifier les remplacements et modifications proposés ;
7. mettre à jour les tests si le changement est volontaire.

### 27.5 Les pipelines sont trop lents

Démarche :

1. mesurer chaque phase ;
2. déterminer si le problème vient des tests, du backend, du provider ou du graphe de ressources ;
3. identifier les dépendances artificielles ;
4. examiner le découpage de l'état ;
5. vérifier les limites d'API ;
6. modifier le parallélisme seulement après analyse ;
7. comparer les durées avant et après modification.

## 28. Projet final : construire une plateforme IaC industrialisée

### 28.1 Contexte

Une entreprise veut gérer plusieurs applications réparties dans des environnements de développement, de préproduction et de production.

Les équipes doivent pouvoir créer les ressources autorisées sans obtenir des permissions administratives globales.

L'équipe plateforme doit garantir :

- la cohérence des modules ;
- la traçabilité des changements ;
- la séparation des états ;
- la protection des secrets ;
- les validations automatiques ;
- les approbations adaptées au risque ;
- la détection des dérives ;
- la possibilité de restaurer un état ;
- la maintenance des versions.

### 28.2 Travail attendu

Concevoir un dépôt ou un ensemble de dépôts contenant :

1. une bibliothèque de modules versionnés ;
2. des configurations racines séparées ;
3. un schéma de découpage des états ;
4. un backend distant sécurisé ;
5. un pipeline de validation ;
6. un workflow de planification et d'application ;
7. une stratégie d'authentification de pipeline ;
8. une politique de gouvernance ;
9. une suite de tests ;
10. un processus de détection de dérive ;
11. une procédure de refactorisation ;
12. un plan de reprise après incident.

Le travail doit privilégier une architecture compréhensible et testable plutôt qu'un nombre élevé d'outils.

### 28.3 Livrables

Le projet doit fournir :

- le code Terraform ;
- les modules et leur documentation ;
- les fichiers de verrouillage nécessaires ;
- les workflows de CI/CD ;
- les contrôles et politiques ;
- un schéma d'architecture ;
- une documentation d'exploitation ;
- une procédure de déploiement et de retour arrière ;
- une procédure de migration d'état ;
- un rapport de tests ;
- une liste des risques et des limites connues.

### 28.4 Critères d'évaluation

| Domaine | Critères |
|---|---|
| Architecture | Responsabilités et états clairement séparés |
| Modules | Interfaces stables, versions contrôlées |
| Sécurité | Permissions minimales et secrets protégés |
| CI/CD | Validation, revue et application séparées |
| Gouvernance | Contrôles documentés et applicables |
| Tests | Tests adaptés au risque et automatisés |
| Exploitation | Dérive, sauvegarde et reprise traitées |
| Maintenance | Versions, changements et migrations maîtrisés |
| Documentation | Procédures utilisables par une autre équipe |

## 29. Exercices corrigés

### Exercice 1 : un état unique pour toute l'entreprise

Une entreprise place le réseau, les bases de données, les identités et toutes les applications de production dans un unique état.

Quel est le principal problème et quelle solution proposer ?

**Correction :**

Le problème est l'absence d'un périmètre de gestion adapté aux cycles de vie, aux responsabilités et aux rayons d'impact. Un changement applicatif peut être associé à un grand nombre de ressources sans rapport direct avec l'application.

Il faut étudier un découpage par domaines cohérents, par exemple réseau, services partagés et applications. Chaque découpage doit justifier les dépendances qu'il crée et les droits accordés à ses consommateurs.

L'objectif n'est pas de fragmenter chaque ressource, mais de rendre les opérations indépendantes lorsque cela est utile.

### Exercice 2 : partager un état avec toutes les équipes

Une équipe accorde à tous les développeurs un droit de lecture global sur le backend Terraform afin qu'ils récupèrent l'identifiant d'un sous-réseau.

Pourquoi ce modèle est-il risqué ?

**Correction :**

Le state peut contenir des valeurs sensibles et la permission accordée peut dépasser le besoin réel. L'identifiant du sous-réseau ne justifie pas automatiquement l'accès à toutes les données de l'état.

Il faut privilégier une transmission explicite de l'information nécessaire, une source de données autorisée ou un mécanisme de publication d'outputs adapté. L'accès au state complet doit rester limité aux identités qui en ont réellement besoin.

### Exercice 3 : mise à jour globale d'un module

Un module réseau commun passe de la version 2.x à la version 3.0.0. Le responsable souhaite mettre à jour toutes les applications directement en production.

Quelle approche proposer ?

**Correction :**

Il faut examiner les changements incompatibles, exécuter les tests du module, sélectionner des consommateurs pilotes et analyser les plans dans des environnements isolés.

Le déploiement doit ensuite être progressif, avec une procédure permettant d'arrêter la migration en cas de comportement inattendu. Les versions restantes et les exceptions doivent être inventoriées.

### Exercice 4 : dérive après une intervention d'urgence

Un administrateur modifie manuellement une règle de sécurité pendant un incident. Le prochain plan Terraform propose d'annuler cette modification.

Que faut-il faire ?

**Correction :**

Il faut d'abord déterminer si la modification manuelle était temporaire ou si elle correspond désormais à la configuration attendue.

Si elle était temporaire, le retour à la configuration déclarée peut être adapté après vérification. Si elle doit persister, le code Terraform doit être mis à jour pour refléter la décision approuvée.

Dans les deux cas, le changement doit être tracé, revu et suivi d'une vérification.

### Exercice 5 : refactorisation d'une ressource

Un développeur renomme une ressource Terraform et le plan propose de détruire l'ancienne puis de créer une nouvelle ressource.

Comment éviter ce comportement lorsque l'objet réel doit être conservé ?

**Correction :**

Il faut examiner l'adresse précédente et l'adresse attendue, puis utiliser un mécanisme de déplacement approprié, tel qu'un bloc `moved` lorsque le scénario est compatible.

Le plan doit être recalculé et examiné pour confirmer que Terraform transfère le suivi de l'objet sans remplacement non souhaité.

### Exercice 6 : clés cloud permanentes dans un pipeline

Un pipeline utilise une clé d'accès cloud permanente stockée dans les variables CI/CD.

Quelle amélioration proposer ?

**Correction :**

Lorsque la plateforme le permet, une fédération d'identité telle qu'OIDC permet d'obtenir des identifiants temporaires. Le rôle obtenu doit être limité au dépôt, à l'environnement et aux opérations nécessaires.

Les secrets existants doivent être révoqués ou renouvelés selon une procédure adaptée après migration, et les journaux doivent être examinés pour rechercher une exposition éventuelle.

### Exercice 7 : un `apply` réussi, mais un service indisponible

Terraform indique que l'application s'est terminée sans erreur, mais un test fonctionnel échoue.

Pourquoi la procédure n'est-elle pas terminée ?

**Correction :**

L'application Terraform confirme principalement que les opérations gérées par Terraform ont été exécutées avec le résultat attendu par le provider. Elle ne prouve pas nécessairement que le service métier fonctionne.

Il faut inclure des contrôles post-déploiement, par exemple la santé du service, l'accès réseau, les permissions d'application et les tests métier pertinents. Le pipeline doit traiter leur échec conformément à la procédure d'exploitation.

## 30. Checklist d'industrialisation

Avant d'autoriser un nouveau périmètre Terraform en production, vérifier les points suivants.

### Architecture et états

- [ ] Le propriétaire du périmètre est identifié.
- [ ] La configuration racine possède un cycle de vie clair.
- [ ] Le découpage de l'état tient compte du rayon d'impact.
- [ ] Les environnements sensibles disposent de frontières d'accès adaptées.
- [ ] Les dépendances inter-états sont documentées.
- [ ] Les permissions du backend sont minimales.
- [ ] Le verrouillage et la sauvegarde sont configurés selon les possibilités du backend.

### Modules et versions

- [ ] Les modules partagés disposent d'une interface documentée.
- [ ] Les versions des modules sont contrôlées.
- [ ] Les providers sont déclarés et verrouillés.
- [ ] Les tests et les règles de compatibilité sont documentés.
- [ ] Les changements incompatibles sont identifiés.
- [ ] Les migrations des adresses Terraform sont examinées.

### Sécurité et gouvernance

- [ ] Aucun secret n'est intégré au dépôt.
- [ ] L'état et les plans sont traités comme des données potentiellement sensibles.
- [ ] Les identités de pipeline utilisent des permissions minimales.
- [ ] Les identifiants temporaires sont privilégiés lorsqu'ils sont disponibles.
- [ ] Les règles de sécurité critiques sont automatisées.
- [ ] Les dérogations sont justifiées, approuvées et traçables.
- [ ] Les workflows de contribution non approuvée n'ont pas un accès libre à la production.

### CI/CD et exploitation

- [ ] Les validations statiques sont exécutées automatiquement.
- [ ] Les tests adaptés au module existent.
- [ ] Les plans sont examinés avant application.
- [ ] Les approbations correspondent au risque réel.
- [ ] Les plans sauvegardés sont protégés.
- [ ] Le déploiement est lié à une version de code déterminée.
- [ ] Les tests post-déploiement sont prévus.
- [ ] La dérive fait l'objet d'une détection régulière.
- [ ] Une procédure d'incident et de reprise du state existe.
- [ ] Les migrations et mises à jour font l'objet de tests.

## 31. Glossaire

**Infrastructure as Code (IaC)**  
Gestion de l'infrastructure à l'aide de fichiers versionnés et de procédures reproductibles.

**Terraform**  
Outil déclaratif permettant de décrire, planifier et gérer des infrastructures au moyen de providers.

**Configuration racine**  
Configuration exécutée directement par Terraform et qui compose les ressources et les modules d'un périmètre donné.

**Module**  
Ensemble de fichiers Terraform regroupant une capacité réutilisable et son interface.

**Provider**  
Extension permettant à Terraform d'interagir avec une API ou une plateforme.

**State**  
Données permettant à Terraform de suivre les objets associés à sa configuration.

**Backend**  
Mécanisme de stockage et, selon le backend, de verrouillage du state.

**Drift, ou dérive**  
Différence entre la configuration attendue et l'infrastructure réellement observée.

**Policy as Code**  
Expression et application de règles de gouvernance sous une forme automatisable.

**OIDC**  
Protocole d'identité souvent utilisé pour établir une relation de confiance entre un pipeline et un fournisseur d'identités.

**Blast radius, ou rayon d'impact**  
Ensemble des ressources et services qui peuvent être affectés par une opération ou une erreur.

**Monorepo**  
Dépôt unique regroupant plusieurs composants ou configurations.

**Multirepo**  
Organisation dans laquelle plusieurs composants sont maintenus dans des dépôts distincts.

**Versionnement sémantique**  
Convention de numérotation des versions permettant de communiquer la nature des changements.

**Refactorisation**  
Modification de la structure du code ou des adresses sans nécessairement modifier l'infrastructure réelle.

**Import**  
Association d'une ressource existante à une adresse gérée par Terraform.

**Fédération d'identité**  
Mécanisme établissant une relation de confiance permettant d'utiliser une identité externe pour obtenir des droits auprès d'un service cible.

**État éphémère**  
Expression parfois utilisée pour parler d'un état associé à un environnement temporaire. Il ne faut pas confondre la durée de vie de l'environnement avec la possibilité de supprimer sans risque les données de l'état.

## 32. Références officielles

### Documentation Terraform

- Terraform : documentation principale  
  https://developer.hashicorp.com/terraform/docs

- Bonnes pratiques de style et d'organisation des configurations  
  https://developer.hashicorp.com/terraform/language/style

- Création et maintenance des modules  
  https://developer.hashicorp.com/terraform/language/modules/develop

- Composition des modules  
  https://developer.hashicorp.com/terraform/language/modules/develop/composition

- State, backends et verrouillage  
  https://developer.hashicorp.com/terraform/language/state

- Backend S3  
  https://developer.hashicorp.com/terraform/language/backend/s3

- Tests Terraform  
  https://developer.hashicorp.com/terraform/language/tests

- Simulation des providers dans les tests  
  https://developer.hashicorp.com/terraform/language/tests/mocking

- Refactorisation des modules et déplacement des ressources  
  https://developer.hashicorp.com/terraform/language/modules/develop/refactoring

- Bloc `moved`  
  https://developer.hashicorp.com/terraform/language/block/moved

- Commande `terraform plan`  
  https://developer.hashicorp.com/terraform/cli/commands/plan

- Formatage et validation  
  https://developer.hashicorp.com/terraform/cli/code

### Gouvernance et exécution centralisée

- Présentation de HCP Terraform  
  https://developer.hashicorp.com/terraform/cloud-docs

- Politiques et gouvernance dans HCP Terraform  
  https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement

- Identifiants dynamiques et authentification des providers  
  https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials

Les fonctionnalités disponibles dépendent de la plateforme, de sa configuration et de l'édition utilisée. Il faut vérifier les prérequis avant de concevoir une chaîne de déploiement autour d'une fonctionnalité particulière.

## 33. Conclusion

Passer à l'Infrastructure as Code à grande échelle consiste à aller bien au-delà de l'écriture de fichiers Terraform.

Il faut concevoir un système dans lequel :

- chaque périmètre d'infrastructure est clairement défini ;
- les états sont protégés et découpés selon les responsabilités ;
- les modules sont réutilisables, testés et versionnés ;
- les identités de déploiement sont limitées à leurs besoins ;
- les politiques de sécurité sont appliquées de manière cohérente ;
- les plans sont contrôlés avant les opérations critiques ;
- les dérives sont détectées et traitées ;
- les migrations et les mises à jour sont maîtrisées ;
- les équipes peuvent travailler de manière autonome sans perdre la cohérence de l'ensemble.

La maturité IaC se mesure donc moins au nombre de ressources provisionnées qu'à la capacité de l'organisation à **déployer, auditer, maintenir et faire évoluer son infrastructure de façon sûre, reproductible et prévisible**.