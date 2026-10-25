# AWS intermédiaire : réseau, infrastructure et automatisation

## Présentation du cours

Ce cours prolonge directement `cloud-aws-debutant.md`.

Les bases acquises — IAM, EC2, S3, régions, zones de disponibilité, VPC, CloudWatch et coûts — vont maintenant être assemblées en infrastructures cohérentes, sécurisées et reproductibles.

La démarche rejoint les compétences développées dans les parcours précédents :
- Docker pour construire et exécuter les applications ;
- Kubernetes pour orchestrer les conteneurs ;
- Git et CI/CD pour versionner et livrer les changements ;
- Terraform pour déclarer l'infrastructure ;
- Ansible pour configurer les systèmes lorsque nécessaire ;
- SRE pour définir la supervision, les objectifs de fiabilité et les procédures d'incident.

### Objectifs

À la fin du cours, il faudra pouvoir :

- Concevoir un VPC segmenté sur plusieurs zones.
- Comprendre le routage public, privé et la sortie Internet.
- Définir des groupes de sécurité cohérents.
- Déployer une architecture applicative avec plusieurs composants.
- Utiliser IAM et les rôles sans multiplier les clés permanentes.
- Gérer les données et les sauvegardes.
- Automatiser l'infrastructure avec Terraform.
- Déployer une application à l'aide d'une chaîne CI/CD.
- Superviser une charge de travail avec CloudWatch.
- Comprendre les bases de la haute disponibilité et de la reprise.
- Préparer une infrastructure pour une évolution vers des architectures expertes.

## 1. Révision des fondations AWS

Le niveau débutant a introduit les principales briques.

| Notion | Utilisation dans ce cours |
|---|---|
| Région et AZ | Répartition et disponibilité |
| IAM | Accès humain et accès des services |
| EC2 | Calcul applicatif ou d'administration |
| S3 | Stockage objet, artefacts et sauvegardes |
| VPC | Isolation et segmentation réseau |
| CloudWatch | Observabilité |
| Facturation | Maîtrise des ressources et transferts |

L'objectif n'est pas de répéter les définitions, mais de les utiliser pour construire une infrastructure complète.

## 2. Concevoir le réseau VPC

### 2.1. Choisir une plage CIDR

Un VPC utilise une ou plusieurs plages IPv4 CIDR.

Exemple :

```text
VPC : 10.40.0.0/16
```

Cette plage contient 65 536 adresses IPv4 théoriques. Les adresses réellement disponibles dans les sous-réseaux dépendent de leur taille et des réservations AWS.

Découpage possible :

```text
VPC 10.40.0.0/16
|
+-- Public AZ-a       10.40.1.0/24
+-- Public AZ-b       10.40.2.0/24
|
+-- Application AZ-a  10.40.11.0/24
+-- Application AZ-b  10.40.12.0/24
|
+-- Données AZ-a      10.40.21.0/24
+-- Données AZ-b      10.40.22.0/24
```

Ce découpage est pédagogique. La taille et le nombre des sous-réseaux doivent être calculés selon le nombre de ressources, les besoins d'évolution et les services utilisés.

Éviter le chevauchement des CIDR avec :
- les réseaux de l'entreprise ;
- les réseaux VPN ;
- les autres VPC ;
- les réseaux des partenaires ;
- les futurs environnements.

### 2.2. Rôle des sous-réseaux

**Sous-réseaux publics**

Ils disposent d'une route vers une Internet Gateway. Une ressource n'est pas pour autant automatiquement exposée.

**Sous-réseaux privés applicatifs**

Ils hébergent les applications qui n'ont pas besoin d'une adresse publique directe.

**Sous-réseaux de données**

Ils hébergent notamment les bases de données et composants de stockage réseau, selon les exigences du service.

```text
                    Internet
                       |
                       v
                Internet Gateway
                       |
        +--------------+--------------+
        |                             |
        v                             v
  Public AZ-a                   Public AZ-b
        |                             |
        +-------------+---------------+
                      |
               Load Balancer
                      |
           +----------+----------+
           |                     |
           v                     v
    Application AZ-a      Application AZ-b
           |                     |
           +----------+----------+
                      |
                      v
                Couche données
```

Un Application Load Balancer peut être placé dans des sous-réseaux publics ou privés selon l'architecture. Une application publique typique utilise un point d'entrée public et des cibles privées.

### 2.3. Tables de routage

Une table de routage indique la destination et la cible utilisées pour acheminer les paquets.

Exemple conceptuel :

| Destination | Cible | Usage |
|---|---|---|
| `10.40.0.0/16` | Local | Communication dans le VPC |
| `0.0.0.0/0` | Internet Gateway | Sortie Internet depuis un sous-réseau public |
| `0.0.0.0/0` | NAT Gateway | Sortie IPv4 depuis un sous-réseau privé |

La route `0.0.0.0/0` correspond à toutes les destinations IPv4 non couvertes par une route plus spécifique.

Une NAT Gateway permet généralement aux ressources privées d'initier certaines connexions sortantes IPv4. Elle ne constitue pas une solution générale d'accès entrant depuis Internet.

### 2.4. NAT Gateway et coûts

La NAT Gateway facilite l'accès sortant de ressources privées, mais entraîne des coûts de fonctionnement et de traitement des données.

Dans une architecture multi-AZ, une NAT Gateway par AZ peut améliorer l'isolation des pannes et éviter certains transferts inter-AZ. La topologie doit être choisie en fonction des exigences de disponibilité et du budget.

Alternatives à examiner :
- VPC endpoints pour certains services AWS ;
- accès privé à des services internes ;
- réduction des téléchargements répétitifs ;
- architecture sans besoin de sortie Internet ;
- proxies contrôlés lorsque pertinents.

## 3. Groupes de sécurité et Network ACL

### 3.1. Groupes de sécurité

Les groupes de sécurité sont des pare-feu avec état.

Ils définissent des règles entrantes et sortantes associées aux interfaces réseau ou ressources compatibles.

Exemple :

```text
Internet
   |
   | TCP 443
   v
SG-ALB
   |
   | Port applicatif, source SG-ALB
   v
SG-APP
   |
   | Port base, source SG-APP
   v
SG-DB
```

Les règles peuvent référencer un autre groupe de sécurité comme source ou destination dans les situations compatibles. Cette approche évite de dépendre uniquement d'adresses IP qui peuvent évoluer.

### 3.2. Network ACL

Les Network ACL filtrent le trafic au niveau du sous-réseau. Elles sont sans état : les règles de retour doivent être considérées séparément.

Il faut donc distinguer :

- groupes de sécurité : règles avec état ;
- Network ACL : règles sans état, évaluées selon leur ordre et leur correspondance.

Les deux mécanismes peuvent se compléter, mais il ne faut pas multiplier les règles complexes sans nécessité opérationnelle.

## 4. Accès privé aux services AWS

### 4.1. VPC endpoints

Les VPC endpoints permettent à certaines ressources d'accéder à des services AWS sans emprunter nécessairement un chemin public vers ces services.

Deux catégories importantes :
- endpoints de passerelle, notamment pour S3 et DynamoDB ;
- endpoints d'interface, basés sur AWS PrivateLink, pour de nombreux services compatibles.

Exemple de chemin :

```text
Instance privée
      |
      v
VPC endpoint
      |
      v
Service AWS compatible
```

Le service, le type d'endpoint, les politiques et les règles réseau doivent être vérifiés.

### 4.2. DNS privé

La résolution DNS joue un rôle important dans les architectures privées.

À examiner :
- options DNS du VPC ;
- zones hébergées Route 53 ;
- noms privés des services ;
- règles de résolution hybrides ;
- connectivité entre VPC ;
- résolution des endpoints.

Une panne DNS peut ressembler à une panne réseau alors que les routes sont correctes.

## 5. Construire une architecture applicative

### 5.1. Architecture de référence

L'objectif est de séparer le point d'entrée, la couche applicative et les données.

```text
Utilisateurs
     |
     v
Route 53
     |
     v
Application Load Balancer
     |
     +------------------+
     |                  |
     v                  v
Cible applicative A   Cible applicative B
     |                  |
     +--------+---------+
              |
              v
        Base de données
```

Selon le besoin, les cibles peuvent être :
- des instances EC2 ;
- des conteneurs ECS ;
- des pods sur EKS ;
- une autre cible compatible avec le service de distribution choisi.

### 5.2. Répartition du trafic

Un load balancer répartit le trafic vers des cibles selon sa configuration et les contrôles de santé.

Il ne suffit pas d'avoir deux serveurs : il faut également :
- configurer les contrôles de santé ;
- traiter correctement les connexions ;
- rendre l'application compatible avec plusieurs instances ;
- externaliser les données partagées si nécessaire ;
- superviser les erreurs ;
- définir une stratégie de déploiement.

### 5.3. Gestion de l'état applicatif

Une application web distribuée ne doit pas supposer que toutes les requêtes d'un utilisateur arrivent sur la même instance.

Les sessions et données partagées peuvent être stockées dans un service adapté.

Le choix dépend du modèle de données, de la cohérence requise et des contraintes de performance.

## 6. Stockage, sauvegardes et restauration

### 6.1. Choisir le stockage

| Service | Usage typique |
|---|---|
| S3 | Objets, fichiers, archives, artefacts |
| EBS | Disque de bloc pour EC2 |
| EFS | Système de fichiers partagé |
| RDS | Base relationnelle gérée |
| DynamoDB | Base NoSQL gérée |

Il faut également définir :
- les besoins de performance ;
- la durabilité ;
- la fréquence d'accès ;
- la politique de rétention ;
- le chiffrement ;
- les coûts ;
- les objectifs de restauration.

### 6.2. RPO et RTO

**RPO — Recovery Point Objective**

Perte maximale de données acceptable, exprimée en durée.

**RTO — Recovery Time Objective**

Durée maximale visée pour restaurer le service.

Exemple :

```text
Incident à 12:00
   |
   +-- RPO cible : 15 minutes
   |      -> perte de données maximale visée
   |
   +-- RTO cible : 60 minutes
          -> durée visée pour restaurer le service
```

Les objectifs ne sont pas garantis simplement parce qu'une sauvegarde existe. Ils doivent être validés par des tests.

### 6.3. Sauvegardes

Une stratégie peut combiner :
- snapshots de volumes ;
- sauvegardes de bases de données ;
- versioning S3 ;
- rétention ;
- copie dans un autre compte ou une autre région ;
- protection contre les suppressions ;
- tests de restauration.

La sauvegarde doit être cohérente avec les données applicatives. Une simple copie d'un disque actif ne garantit pas toujours la cohérence de l'application.

## 7. IAM avancé pour les charges de travail

### 7.1. Séparer les identités

Une infrastructure comprend plusieurs types d'identités :
- administrateurs ;
- développeurs ;
- pipeline CI/CD ;
- instances ;
- tâches conteneurisées ;
- fonctions Lambda ;
- outils d'observabilité.

Chaque identité doit disposer des droits nécessaires à sa tâche, et pas de permissions globales par commodité.

### 7.2. Rôles de service

Exemple :

```text
Pipeline CI/CD
      |
      v
Rôle IAM de déploiement
      |
      v
Actions AWS limitées
      |
      v
Environnement cible
```

Pour les charges de travail :
- EC2 peut utiliser un rôle d'instance ;
- ECS peut utiliser des rôles d'exécution et de tâche distincts ;
- EKS peut utiliser des mécanismes d'identité adaptés aux pods ;
- Lambda utilise un rôle d'exécution.

Les mécanismes précis dépendent du service et de l'architecture.

### 7.3. Journaux d'audit

AWS CloudTrail enregistre les événements d'activité AWS pris en charge.

Il aide à répondre à des questions telles que :
- quelle identité a effectué une action ?
- quelle API a été appelée ?
- quand l'événement a-t-il eu lieu ?
- quelle ressource était concernée ?

Les événements et la rétention doivent être configurés selon les besoins. L'audit doit être protégé contre la modification non autorisée.

## 8. Terraform pour AWS

Le cours `iac-intermediaire.md` présente déjà les principes généraux d'Infrastructure as Code. Cette section les applique à AWS.

### 8.1. Architecture du dépôt

```text
aws-infrastructure/
|
+-- modules/
|    +-- network/
|    +-- security/
|    +-- compute/
|
+-- environments/
|    +-- dev/
|    +-- staging/
|    +-- prod/
|
+-- .gitignore
+-- README.md
```

Cette organisation est un exemple. Les modules doivent correspondre à des frontières réutilisables et bien définies.

### 8.2. Exemple Terraform minimal

Le fragment suivant illustre la déclaration d'un VPC. Il ne constitue pas une architecture complète.

```hcl
terraform {
  required_version = ">= 1.6.0"

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

variable "aws_region" {
  type        = string
  description = "Région AWS du déploiement"
  default     = "eu-west-1"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.40.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "lab-vpc"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

output "vpc_id" {
  value = aws_vpc.main.id
}
```

Les contraintes de version doivent être vérifiées dans la documentation du fournisseur AWS utilisé par le projet. La version effective est déterminée par le verrouillage du fournisseur dans le dépôt.

### 8.3. Commandes de base

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
```

`terraform apply` crée ou modifie les ressources selon le plan approuvé.

Il faut vérifier le plan avant de l'appliquer, notamment dans les environnements partagés.

Pour nettoyer un laboratoire :

```bash
terraform plan -destroy
```

Après inspection, `terraform destroy` peut supprimer les ressources gérées par cette configuration. Il faut comprendre ses effets avant de confirmer.

### 8.4. État Terraform

L'état Terraform permet de faire correspondre les objets déclarés aux ressources suivies.

Dans une équipe :
- stocker l'état dans un backend adapté ;
- activer le verrouillage lorsque le backend le permet ;
- restreindre les permissions ;
- chiffrer et protéger les données ;
- séparer les environnements ;
- éviter les modifications manuelles non coordonnées.

Ne pas versionner un fichier d'état contenant des informations sensibles dans un dépôt public.

### 8.5. Séparer les environnements

Les environnements de développement, de recette et de production doivent être isolés de manière cohérente.

Selon le contexte, l'isolation peut s'appuyer sur :
- des comptes AWS séparés ;
- des rôles distincts ;
- des backends d'état séparés ;
- des variables propres à chaque environnement ;
- des pipelines distincts ;
- des politiques de validation différentes.

Le niveau expert approfondira l'organisation multi-comptes et les garde-fous de gouvernance.

## 9. CI/CD et déploiement AWS

Les connaissances de `cicd-intermediaire.md` s'appliquent ici à l'infrastructure et aux applications hébergées sur AWS.

### 9.1. Chaîne de livraison

```text
Commit Git
    |
    v
Tests et lint
    |
    v
Construction de l'artefact
    |
    v
Analyse de sécurité
    |
    v
Déploiement en développement
    |
    v
Tests d'intégration
    |
    v
Approbation selon la politique
    |
    v
Déploiement de production
    |
    v
Vérification et surveillance
```

### 9.2. Authentification CI/CD

Éviter de stocker des clés AWS à longue durée de vie dans les secrets d'un dépôt si un mécanisme fédéré est disponible.

GitHub Actions peut utiliser OpenID Connect (OIDC) pour obtenir une session AWS temporaire, sous réserve de configurer correctement le fournisseur d'identité et le rôle IAM.

Les conditions de confiance doivent limiter :
- le dépôt autorisé ;
- l'organisation ;
- la branche ou l'environnement ;
- l'audience ;
- les permissions accordées au rôle.

### 9.3. Séparer les permissions

Un pipeline de test ne doit pas nécessairement pouvoir modifier la production.

Une conception raisonnable sépare :
- les permissions de test ;
- les permissions de publication ;
- les permissions de déploiement ;
- les permissions d'administration.

L'élévation de privilèges doit être contrôlée et traçable.

## 10. Conteneurs sur AWS

### 10.1. Amazon ECS

Amazon ECS est un service d'orchestration de conteneurs.

Il permet de gérer :
- des définitions de tâches ;
- des services ;
- des déploiements ;
- des stratégies de placement ;
- l'intégration avec les réseaux et les équilibreurs de charge.

ECS peut utiliser AWS Fargate ou des instances EC2 selon le mode de calcul choisi.

### 10.2. Amazon EKS

Amazon EKS est un service Kubernetes géré.

Il permet d'utiliser Kubernetes avec les intégrations AWS nécessaires à l'identité, au réseau, au stockage et à l'exploitation.

Le cours Kubernetes précédent fournit les concepts d'orchestration. L'étape suivante consiste à comprendre les spécificités AWS, les coûts et les responsabilités d'un cluster EKS.

### 10.3. Choisir ECS ou EKS

Le choix dépend :
- des compétences de l'équipe ;
- des besoins Kubernetes ;
- des intégrations existantes ;
- des exigences de portabilité ;
- du coût d'exploitation ;
- du niveau de contrôle requis.

EKS n'est pas automatiquement supérieur à ECS. Un service managé plus simple peut être préférable lorsqu'il répond au besoin.

## 11. Observabilité avec CloudWatch

### 11.1. Les trois catégories

- Métriques : valeurs numériques mesurées.
- Journaux : événements et messages.
- Alarmes : conditions qui déclenchent une notification ou une action.

Exemples :
- taux d'erreurs HTTP ;
- latence ;
- utilisation CPU ;
- nombre de requêtes ;
- erreurs de connexion à la base ;
- état des cibles d'un load balancer.

### 11.2. De la métrique à l'action

```text
Application
    |
    +-- Métriques
    +-- Journaux
    +-- Traces, si instrumentées
          |
          v
     Observabilité
          |
          v
      Alerte utile
          |
          v
   Diagnostic et réponse
          |
          v
      Amélioration
```

Une alerte doit être actionnable. Les alertes trop nombreuses ou sans lien avec un impact utilisateur peuvent provoquer de la fatigue opérationnelle.

### 11.3. Relier les métriques aux SLO

Le parcours SRE a présenté les SLI et SLO.

Exemple de SLI :
- proportion de requêtes HTTP réussies ;
- latence au 95e percentile ;
- disponibilité d'une fonction métier.

Exemple de SLO :
- 99,9 % des requêtes conformes à un critère de succès sur une fenêtre définie.

Il faut définir précisément le dénominateur, la fenêtre de mesure, les exclusions et le comportement attendu en cas de panne.

## 12. Haute disponibilité et reprise

### 12.1. Éviter le point de défaillance unique

Un point de défaillance unique (SPOF) peut interrompre l'ensemble du service.

Exemples :
- un seul serveur applicatif ;
- une base de données sans stratégie de reprise adaptée ;
- une seule zone utilisée pour toutes les ressources critiques ;
- une unique identité d'administration sans mécanisme de récupération.

### 12.2. Architecture multi-AZ

Une architecture multi-AZ répartit les composants pertinents sur plusieurs zones.

Il faut également prendre en compte :
- la réplication des données ;
- la répartition du trafic ;
- la détection de panne ;
- le basculement ;
- les dépendances externes ;
- les quotas ;
- les procédures de restauration.

### 12.3. Test de reprise

Un test doit vérifier les résultats, et pas seulement l'existence d'une configuration.

Exemple :
1. Définir un scénario de panne.
2. Déterminer le résultat attendu.
3. Exécuter le test dans un environnement autorisé.
4. Mesurer le temps de détection.
5. Mesurer le temps de récupération.
6. Vérifier l'intégrité des données.
7. Documenter les écarts.
8. Corriger puis retester.

## 13. Travaux pratiques

### TP 1 — Concevoir un VPC

Construire un plan d'adressage pour :
- deux sous-réseaux publics ;
- deux sous-réseaux applicatifs privés ;
- deux sous-réseaux de données ;
- une stratégie de sortie Internet ;
- une stratégie de résolution DNS.

Livrables :
- tableau CIDR ;
- tables de routage ;
- matrice des flux ;
- justification des choix.

### TP 2 — Déployer un réseau avec Terraform

1. Créer un dépôt Git.
2. Déclarer le VPC.
3. Déclarer les sous-réseaux.
4. Déclarer les tables de routage.
5. Configurer les associations.
6. Examiner `terraform plan`.
7. Appliquer dans un compte de laboratoire.
8. Vérifier les ressources.
9. Détruire le laboratoire lorsque les tests sont terminés.

Ne pas inclure de secrets ou de données sensibles dans le dépôt.

### TP 3 — Déployer une application derrière un load balancer

Concevoir une architecture avec :
- un point d'entrée ;
- des cibles applicatives privées ;
- des groupes de sécurité distincts ;
- des contrôles de santé ;
- des métriques ;
- des journaux.

Vérifier le fonctionnement et la réaction à la perte d'une cible.

### TP 4 — Pipeline CI/CD sécurisé

Créer un pipeline qui :
1. lance les tests ;
2. vérifie le formatage Terraform ;
3. valide la configuration ;
4. produit un plan ;
5. exige une validation avant application si nécessaire ;
6. utilise une identité temporaire ;
7. conserve les journaux de déploiement.

Les déploiements destructifs doivent être soumis à des contrôles explicites.

## 14. Dépannage avancé

### Une instance privée ne peut pas accéder à Internet

Vérifier :
- les routes ;
- la NAT Gateway ;
- son sous-réseau ;
- l'association de la table de routage ;
- les groupes de sécurité ;
- les Network ACL ;
- le DNS ;
- les quotas et l'état des ressources.

Si seul S3 est nécessaire, un VPC endpoint peut être plus approprié qu'une sortie Internet générale.

### Une cible du load balancer est déclarée non saine

Examiner :
- le port et le protocole de contrôle ;
- le chemin de santé ;
- le code HTTP attendu ;
- la connectivité entre le load balancer et la cible ;
- les journaux de l'application ;
- les délais de démarrage ;
- les règles des groupes de sécurité.

### Terraform veut remplacer une ressource

Lire le plan et identifier les attributs concernés. Certaines modifications nécessitent un remplacement.

Ne pas appliquer automatiquement un plan qui détruit des données ou remplace des ressources critiques.

### Le pipeline obtient `AccessDenied`

Vérifier :
- le rôle effectivement assumé ;
- les conditions de confiance OIDC ;
- les permissions du rôle ;
- les politiques de ressource ;
- les restrictions d'organisation ;
- les permissions nécessaires à l'action exacte.

Ne pas corriger le problème en attribuant immédiatement `AdministratorAccess`.

## 15. Exercices corrigés

### Exercice 1 — Segmenter le réseau

Une application possède un frontal public, un service applicatif et une base de données.

**Correction :**
- frontal : point d'entrée public contrôlé ;
- application : sous-réseaux privés ;
- base : sous-réseaux de données ;
- accès autorisés entre groupes de sécurité selon les flux nécessaires.

### Exercice 2 — Choisir une stratégie de sauvegarde

Une base de données doit être restaurable après une erreur de manipulation.

**Correction :** définir une politique de sauvegarde, une rétention, des permissions de restauration et des tests. La fréquence et la conservation dépendent du RPO et du RTO attendus.

### Exercice 3 — Automatiser un VPC

Pourquoi déclarer l'infrastructure dans Terraform plutôt que la créer manuellement ?

**Correction :** l'infrastructure devient versionnable, révisable, reproductible et contrôlable par plan. Cela ne supprime pas les risques : les permissions, l'état et les changements destructifs doivent être gérés correctement.

### Exercice 4 — CI/CD

Un pipeline de test doit-il avoir les mêmes permissions que le pipeline de production ?

**Correction :** non. Les permissions doivent être limitées aux tâches de chaque pipeline et à son environnement.

### Exercice 5 — Multi-AZ

Deux instances se trouvent dans deux AZ, mais la base de données est un point de défaillance unique.

**Correction :** la couche applicative est distribuée, mais l'architecture complète n'est pas nécessairement hautement disponible. La base et ses dépendances doivent être examinées séparément.

## 16. Projet final — Infrastructure AWS automatisée

### Scénario

Une équipe doit déployer une application conteneurisée avec un environnement de développement et un environnement de recette.

### Livrables obligatoires

1. Architecture réseau et plan CIDR.
2. Matrice des flux.
3. Infrastructure Terraform.
4. Règles IAM.
5. Configuration de stockage et sauvegarde.
6. Déploiement applicatif.
7. Pipeline CI/CD.
8. Supervision et alertes.
9. Procédure de déploiement et de retour arrière.
10. Estimation des coûts.
11. Procédure de destruction du laboratoire.

### Critères de réussite

- Infrastructure reproductible.
- Ressources privées par défaut lorsque cela est possible.
- Permissions limitées.
- Secrets absents du dépôt.
- Pipeline traçable.
- Sauvegardes testables.
- Supervision exploitable.
- Coûts identifiés.
- Changements destructifs contrôlés.

## 17. Préparation au niveau expert

Le niveau expert s'appuiera sur cette infrastructure pour approfondir :
- l'organisation multi-comptes ;
- AWS Organizations et Control Tower ;
- les politiques de contrôle des services ;
- les architectures multi-régions ;
- les stratégies de reprise après sinistre ;
- l'identité fédérée et l'accès privilégié ;
- la détection centralisée ;
- la gouvernance Terraform à grande échelle ;
- les déploiements progressifs ;
- la réponse aux incidents ;
- les coûts et la capacité à grande échelle.

## 18. Glossaire

- **ALB** : Application Load Balancer.
- **AZ** : zone de disponibilité.
- **CIDR** : notation d'une plage d'adresses IP.
- **ECS** : orchestration de conteneurs AWS.
- **EKS** : Kubernetes géré sur AWS.
- **IGW** : Internet Gateway.
- **NACL** : Network Access Control List.
- **NAT Gateway** : service de traduction d'adresses pour certains accès sortants.
- **OIDC** : protocole d'identité fédérée.
- **RPO** : objectif de perte maximale de données.
- **RTO** : objectif de durée de restauration.
- **SG** : groupe de sécurité.
- **SLO** : objectif de niveau de service.
- **VPC endpoint** : point d'accès privé à un service compatible.

## 19. Documentation officielle

- VPC : https://docs.aws.amazon.com/vpc/
- VPC endpoints : https://docs.aws.amazon.com/vpc/latest/privatelink/
- Route 53 : https://docs.aws.amazon.com/route53/
- Elastic Load Balancing : https://docs.aws.amazon.com/elasticloadbalancing/
- IAM : https://docs.aws.amazon.com/IAM/latest/UserGuide/
- CloudTrail : https://docs.aws.amazon.com/awscloudtrail/
- CloudWatch : https://docs.aws.amazon.com/cloudwatch/
- AWS Backup : https://docs.aws.amazon.com/aws-backup/
- ECS : https://docs.aws.amazon.com/ecs/
- EKS : https://docs.aws.amazon.com/eks/
- Terraform AWS Provider : https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Bonnes pratiques Terraform pour AWS : https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/
- GitHub Actions et AWS : https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/create-a-ci-cd-pipeline-to-deploy-containerized-applications-to-amazon-ecs-using-github-actions.html
- AWS Well-Architected : https://docs.aws.amazon.com/wellarchitected/