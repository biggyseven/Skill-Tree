# Infrastructure as Code avec Terraform — Débutant

> **Mise en contexte.** Une petite équipe recrée chaque mois le même réseau cloud à la main. Les environnements finissent par différer, les règles de sécurité sont oubliées et personne ne sait exactement ce qui a changé. L’Infrastructure as Code (IaC) décrit l’infrastructure dans des fichiers versionnés et permet d’examiner les changements avant de les appliquer.

## Objectifs d’apprentissage

Tu dois comprendre les principes de l’IaC, reconnaître les blocs Terraform, déclarer un fournisseur et une ressource, utiliser variables et sorties, suivre le cycle init/plan/apply, comprendre le rôle de l’état et protéger les données sensibles.

## Prérequis

Connaître les bases du cloud, des réseaux et de Git. Les premiers exemples utilisent uniquement une ressource locale Terraform afin de ne pas créer de ressource cloud facturable. N’applique jamais un exemple à un compte de production sans vérifier la facturation, les permissions et les effets sur les ressources.

## 1. Pourquoi décrire l’infrastructure ?

L’IaC permet de représenter des ressources telles qu’un réseau, un sous-réseau, un pare-feu, une machine virtuelle, un stockage ou un service géré. Le code décrit l’état désiré. L’outil compare cet état à l’état connu et prépare un plan.

Avantages :
- historique des changements ;
- revue avant application ;
- reproductibilité entre environnements ;
- meilleure détection des écarts ;
- tests et politiques automatisables.

Limites :
- le code peut contenir une erreur dangereuse ;
- le plan peut affecter des ressources existantes ;
- le fichier d’état peut contenir des données sensibles ;
- les fournisseurs et leurs APIs changent ;
- un système réel comporte aussi des données et dépendances extérieures au code.

## 2. Cycle de travail Terraform

~~~text
Fichiers .tf
   |
terraform fmt / validate
   |
terraform init  -> modules et providers
   |
terraform plan  -> changements prévus
   |
Revue du plan
   |
terraform apply -> modification des ressources
   |
vérification + suivi de l'état
~~~

- init prépare le répertoire et récupère les providers nécessaires.
- fmt normalise le format des fichiers.
- validate vérifie la cohérence de la configuration.
- plan prépare un aperçu des actions proposées.
- apply applique les changements approuvés.
- destroy supprime les ressources gérées par la configuration : cette commande a un impact important et ne doit pas être lancée sans revue du périmètre.

## 3. Premier exemple sans fournisseur cloud

Crée un fichier main.tf dans un répertoire isolé :

~~~hcl
terraform {
  required_version = ">= 1.5.0"
}

variable "environment" {
  type        = string
  description = "Nom de l'environnement de laboratoire"
  default     = "lab"
}

resource "terraform_data" "example" {
  input = var.environment
}

output "environment_name" {
  value = terraform_data.example.output
}
~~~

La ressource intégrée terraform_data permet de découvrir le cycle Terraform sans provisionner de machine, de réseau ou de service cloud. Elle nécessite une version de Terraform compatible avec ce type de ressource (Terraform 1.4 ou ultérieur).

Exécute :

~~~bash
terraform fmt
terraform init
terraform validate
terraform plan
~~~

Lis le plan avant de l’appliquer :

~~~bash
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform output environment_name
~~~

L’application crée ici l’objet de données local géré par Terraform, pas une machine virtuelle. Le fichier de plan et l’état peuvent contenir des valeurs sensibles dans d’autres configurations ; protège-les par défaut. Après le TP, inspecte le périmètre puis utilise destroy seulement dans le répertoire de test que tu viens de créer.

## 4. Providers et ressources

Un provider est un plugin qui permet à Terraform de dialoguer avec une API, par exemple celle d’un fournisseur cloud. Une ressource représente un objet géré. La configuration nécessaire dépend du provider, des versions supportées, de l’authentification et des attributs réellement pris en charge.

Avant d’utiliser une ressource réelle :
1. choisis le fournisseur et l’API cible ;
2. consulte la documentation de la version de provider retenue ;
3. épingle une plage de version compatible ;
4. prépare des identifiants aux permissions minimales ;
5. confirme compte, région et environnement ;
6. lis le plan et identifie chaque suppression ou remplacement possible.

Ne copie pas un exemple de fournisseur inconnu en production : la syntaxe seule ne prouve ni la compatibilité ni l’innocuité d’une ressource.

## 5. Variables, types et sorties

Les variables rendent la configuration adaptable sans dupliquer les fichiers. Elles peuvent avoir un type, une description, une valeur par défaut et des validations. Les sorties exposent une information utile après la création d’une ressource.

~~~hcl
variable "service_port" {
  type        = number
  description = "Port du service de laboratoire"
  default     = 8080
  validation {
    condition     = var.service_port >= 1 && var.service_port <= 65535
    error_message = "Le port doit être compris entre 1 et 65535."
  }
}

output "service_port" {
  value = var.service_port
}
~~~

Ne considère pas une valeur comme un secret simplement parce qu’elle n’est pas codée en dur. Les valeurs sensibles peuvent se retrouver dans l’état ou dans les journaux. Utilise le mécanisme de secrets adapté à ton environnement.

## 6. Lire un plan avec méthode

Dans le plan, distingue la création, la mise à jour et la suppression. Une suppression suivie d’une création peut être nécessaire lorsqu’un attribut ne peut pas être modifié sur place. Les détails dépendent de la ressource et du provider, mais la question reste : quelles ressources vont changer, avec quelles dépendances et quelles conséquences ?

Ne valide pas un plan uniquement parce qu’il ne contient pas d’erreur syntaxique. Compare-le à l’objectif du changement. Si une suppression imprévue apparaît, arrête-toi et recherche la cause.

Quand le plan a été revu, la pratique la plus stricte consiste à enregistrer un plan ciblé puis à appliquer précisément ce plan :

~~~bash
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
~~~

Un plan peut contenir des informations sensibles. Ne le publie pas dans un emplacement ouvert et ne le considère pas comme un artefact anodin.

## 7. État Terraform et prudence

L’état relie les objets déclarés à des objets réels. Il est nécessaire pour comprendre ce que Terraform gère. L’état local est utile pour un TP, mais une équipe doit généralement utiliser une solution d’état distant avec contrôle d’accès, sauvegarde et verrouillage adaptés.

Règles essentielles :
- n’édite pas manuellement le fichier d’état comme un fichier de configuration ;
- ne le publie pas dans un dépôt public ;
- ne supprime pas l’état pour « repartir de zéro » sans plan de migration ;
- protège les sauvegardes et les permissions ;
- vérifie le compte, la région et le workspace avant de modifier des ressources ;
- conserve les fichiers de configuration, les verrous de dépendances et le plan approuvé selon la politique de l’équipe.

Le state peut contenir des valeurs sensibles même si le code utilise une variable marquée sensible. Limite l’accès à l’état comme à une donnée confidentielle.

## 8. Environnements et conventions

Sépare les environnements avec une stratégie explicite : répertoires et racines distincts, variables contrôlées, espaces de travail ou modules partagés selon les exigences. Un workspace Terraform ne constitue pas à lui seul une frontière de sécurité suffisante entre développement et production.

Conserve les fichiers lisibles, exécute fmt et validate en CI, et demande une revue sur les plans qui touchent au réseau, au stockage, aux identités ou aux ressources facturées. Le nom de l’environnement, le compte et la région doivent être visibles dans les paramètres contrôlés.

N’ajoute pas à Git les répertoires locaux de plugins, les fichiers d’état, leurs sauvegardes ou des plans contenant des valeurs sensibles. Ajoute des règles d’ignorance adaptées, puis vérifie avec le statut Git que ces fichiers ne sont pas suivis.

## 9. TP guidé : produire et comparer deux plans

**But :** apprendre le cycle Terraform et la revue du plan sans créer de ressource cloud.

1. Crée un répertoire iac-lab et le fichier main.tf avec la ressource terraform_data de l’exemple.
2. Exécute fmt, init et validate.
3. Exécute plan et lis chaque action.
4. Enregistre un plan dans un fichier dédié, puis affiche-le.
5. Modifie la valeur de la variable environment.
6. Produis un second plan et explique la différence.
7. Exécute apply uniquement dans ce répertoire de TP.
8. Vérifie la sortie, inspecte le state local et confirme qu’aucune ressource cloud n’a été créée.
9. Examine le statut Git et vérifie que l’état et les plans n’ont pas été ajoutés au dépôt.

**Critères de réussite :** le cycle de base est compris, les fichiers de configuration sont versionnés, l’état n’est pas publié et aucun service cloud facturable n’a été créé.

## Exercices corrigés

**1. À quoi sert plan ?**  
À préparer un aperçu des changements que Terraform envisage avec la configuration et l’état disponibles. Il aide à détecter les créations, mises à jour et suppressions avant application.

**2. Pourquoi init doit-il être répété dans un environnement CI neuf ?**  
Parce que le runner doit récupérer les plugins et modules déclarés. L’étape prépare un environnement de travail reproductible.

**3. Le code ne contient aucun mot de passe. L’état peut-il contenir un secret ?**  
Oui. Certains attributs renvoyés par un provider sont enregistrés dans l’état. Il faut protéger le stockage, les sauvegardes et les permissions.

**4. Pourquoi ne faut-il pas appliquer un plan sans le lire ?**  
Le plan peut supprimer ou remplacer des ressources. La validation syntaxique ne prouve pas que les effets sont conformes au besoin métier.

## Défi final corrigé

Prépare une configuration d’équipe qui accepte un nom d’environnement et un port validé, applique le formatage et la validation en CI, produit un plan pour revue et empêche l’état d’être publié dans le dépôt.

**Solution attendue :** utiliser des variables typées avec validation, fmt -check, validate, publier le plan dans un espace protégé et exiger une approbation avant application. Ignorer les états, leurs sauvegardes et les fichiers de plan sensibles. Aucun apply automatique ne doit se produire sans que les protections du pipeline aient été conçues et testées.

## À retenir

Terraform décrit une infrastructure souhaitée, mais ne décide pas si chaque changement est acceptable pour le métier. La discipline essentielle consiste à contrôler les versions, inspecter le plan, protéger l’état et appliquer uniquement le périmètre approuvé.