
# Google Cloud Platform — Niveau Intermédiaire
## Architecture, réseau, services managés, Infrastructure as Code et exploitation

**Fichier :** `cloud-gcp-intermediaire.md`  
**Niveau :** Intermédiaire  
**Domaine :** Cloud computing, architecture, réseau, sécurité, DevOps et exploitation  
**Plateforme :** Google Cloud Platform (GCP)

## 1. Présentation du cours

Ce cours prolonge les fondations du niveau débutant. L'objectif n'est plus simplement de créer une machine virtuelle ou un bucket : il s'agit de construire une plateforme cohérente, sécurisée, automatisable, observable et capable d'évoluer.

À la fin de ce cours, l'apprenant doit pouvoir concevoir une architecture cloud de taille intermédiaire, organiser les ressources, segmenter les réseaux, déployer des applications conteneurisées, automatiser l'infrastructure et diagnostiquer les problèmes d'exploitation.

### Compétences visées

- Structurer plusieurs projets Google Cloud selon les environnements.
- Comprendre les réseaux VPC, les sous-réseaux, les routes, Cloud NAT, les règles de pare-feu et les connexions hybrides.
- Déployer une application sur Cloud Run ou sur Compute Engine selon les besoins.
- Comprendre les responsabilités liées à GKE et aux bases de données managées.
- Appliquer le principe du moindre privilège avec IAM.
- Utiliser Terraform pour décrire et faire évoluer une infrastructure.
- Construire une chaîne CI/CD avec validation et déploiement contrôlé.
- Centraliser les journaux, créer des alertes et définir des indicateurs de service.
- Contrôler les coûts et supprimer proprement les ressources de laboratoire.

## 2. Prérequis

Il est recommandé de savoir :
- créer un projet GCP et sélectionner ce projet avec `gcloud` ;
- utiliser Cloud Shell ou un terminal avec Google Cloud CLI ;
- créer une machine virtuelle et un bucket Cloud Storage ;
- comprendre les bases de TCP/IP, DNS, HTTP/HTTPS, Linux et Git ;
- lire du YAML et comprendre les variables d'environnement ;
- distinguer une identité utilisateur d'un compte de service.

Commandes de vérification :

```bash
gcloud version
gcloud auth list
gcloud config list
gcloud projects list
terraform version
git --version
```

Si Terraform n'est pas installé, l'installer depuis la documentation officielle. Ne jamais supposer qu'il est préinstallé dans tous les environnements Cloud Shell.

## 3. Architecture pédagogique générale

Le scénario utilisé dans ce cours est celui d'une petite organisation qui héberge une application web, une API et des données persistantes.

```text
                         UTILISATEURS
                              |
                           HTTPS
                              |
                     [ Point d'entrée ]
                              |
                   [ Application web/API ]
                              |
                +-------------+-------------+
                |                           |
         [ Cloud Run ]               [ Services privés ]
                |                           |
                |                    +------+------+
                |                    |             |
                |                 [ SQL ]     [ Storage ]
                |
          [ Cloud Logging ]
                |
          [ Cloud Monitoring ]

Organisation GCP
|
+-- Projet de développement
|   +-- Tests et expérimentations
|
+-- Projet de préproduction
|   +-- Validation avant production
|
+-- Projet de production
    +-- Services réels
    +-- Contrôles renforcés
    +-- Surveillance et alertes
```

Ce schéma représente les rôles logiques. Les services exacts et leur connectivité dépendent de l'architecture choisie. Tous les services ne sont pas automatiquement placés dans le VPC : par exemple, Cloud Run est un service managé qui nécessite une configuration de réseau adaptée pour accéder aux ressources privées.

## 4. Organisation des ressources GCP

### 4.1 Hiérarchie des ressources

```text
Organisation
|
+-- Dossier : Non-production
|   |
|   +-- Projet : application-dev
|   |
|   +-- Projet : application-staging
|
+-- Dossier : Production
    |
    +-- Projet : application-prod
    |
    +-- Projet : réseau-central
```

Les dossiers et l'organisation sont disponibles selon le contexte d'identité et de gestion de l'organisation. Un utilisateur possédant uniquement un projet personnel ne dispose pas nécessairement de ces structures.

La hiérarchie permet notamment :
- d'appliquer des stratégies à un ensemble de projets ;
- de séparer les environnements ;
- de gérer les rôles IAM à différents niveaux ;
- de mieux contrôler les coûts et les responsabilités.

### 4.2 Choisir la bonne séparation

La séparation par projet est souvent préférable à une simple séparation par nom de ressource lorsque les environnements ont des exigences différentes en matière de sécurité, de facturation, de quotas ou de cycle de vie.

Exemple :

| Critère | Développement | Production |
|---|---|---|
| Données | Données de test | Données réelles |
| Accès | Équipe de développement | Accès restreint |
| Déploiement | Fréquent | Contrôlé |
| Alertes | Alertes de test | Alertes opérationnelles |
| Budget | Plafond adapté aux tests | Budget et alertes dédiés |
| Suppression | Ressources temporaires possibles | Procédure contrôlée |

Un projet distinct ne remplace pas la conception IAM. Les rôles hérités de l'organisation ou du dossier doivent aussi être examinés.

### 4.3 Sélectionner un projet

```bash
gcloud config set project PROJECT_ID
gcloud config get-value project
gcloud projects describe PROJECT_ID
```

Activer une API nécessaire :

```bash
gcloud services enable run.googleapis.com \
  --project=PROJECT_ID
```

Une API activée peut entraîner des coûts indirects lorsque des ressources facturables sont ensuite créées. L'activation seule ne signifie pas toujours qu'une facture est générée, mais il faut comprendre les dépendances de chaque service.

## 5. IAM : identités, rôles et comptes de service

### 5.1 Les trois éléments à distinguer

- **Principal :** identité à laquelle une autorisation peut être accordée, par exemple un utilisateur, un groupe ou un compte de service.
- **Rôle :** ensemble de permissions.
- **Policy IAM :** associations entre les principaux, les rôles et la ressource sur laquelle ces autorisations s'appliquent.

```text
Principal
   |
   | reçoit un rôle
   v
Rôle IAM
   |
   | contient des permissions
   v
Actions autorisées sur une ressource
```

Une autorisation au niveau d'un projet peut s'appliquer à de nombreuses ressources de ce projet. Une autorisation au niveau d'une ressource est généralement plus ciblée.

### 5.2 Principe du moindre privilège

Ne donnez pas le rôle Owner à chaque membre de l'équipe. Préférez :
- des rôles prédéfinis adaptés à la tâche ;
- des rôles personnalisés lorsque c'est réellement nécessaire ;
- des groupes pour administrer les accès d'équipe ;
- des comptes de service distincts par application ou fonction ;
- des permissions temporaires et contrôlées pour les opérations sensibles.

Exemple conceptuel :

```text
Groupe développeurs
  -> accès de développement adapté

Groupe opérateurs
  -> permissions d'exploitation nécessaires

Compte de service de l'application
  -> accès uniquement aux données nécessaires

Compte de service du pipeline
  -> permissions de déploiement limitées
```

### 5.3 Examiner les attributions de rôles

```bash
gcloud projects get-iam-policy PROJECT_ID \
  --format=json
```

Cette commande affiche la politique IAM du projet. Elle ne suffit pas à reconstituer toutes les autorisations effectives : il faut aussi examiner les héritages de l'organisation et des dossiers, les conditions IAM, les stratégies de refus éventuelles et les contrôles spécifiques aux services.

### 5.4 Créer un compte de service applicatif

```bash
gcloud iam service-accounts create app-runtime \
  --project=PROJECT_ID \
  --display-name="Compte de service de l'application"
```

Pour consulter les comptes :

```bash
gcloud iam service-accounts list \
  --project=PROJECT_ID
```

Ne créez pas de clé JSON par défaut. Lorsque c'est possible, privilégiez les identités managées et les mécanismes d'authentification fournis par l'environnement d'exécution.

Une clé de compte de service est un secret durable. Si elle est compromise, un attaquant peut agir avec les permissions associées à ce compte jusqu'à révocation ou expiration pertinente.

## 6. Réseau VPC : conception et segmentation

### 6.1 Modèle logique

```text
VPC : application-network
|
+-- Sous-réseau : frontend
|   +-- Ressources exposées selon les règles prévues
|
+-- Sous-réseau : backend
|   +-- Services applicatifs internes
|
+-- Sous-réseau : data
    +-- Ressources nécessitant une protection renforcée
```

Les sous-réseaux ne constituent pas à eux seuls une politique de sécurité complète. Il faut aussi contrôler les règles de pare-feu, les routes, les identités, les points d'entrée et les chemins de sortie.

Les VPC Google Cloud sont des réseaux globaux avec des sous-réseaux régionaux. Cette propriété est importante : le réseau est global, mais les plages d'adresses des sous-réseaux sont associées à des régions.

### 6.2 Créer un VPC personnalisé

```bash
gcloud compute networks create app-network \
  --subnet-mode=custom \
  --project=PROJECT_ID
```

Créer un sous-réseau :

```bash
gcloud compute networks subnets create app-subnet \
  --network=app-network \
  --region=REGION \
  --range=10.20.0.0/24 \
  --project=PROJECT_ID
```

Afficher les réseaux :

```bash
gcloud compute networks list \
  --project=PROJECT_ID
```

Afficher les sous-réseaux :

```bash
gcloud compute networks subnets list \
  --project=PROJECT_ID
```

### 6.3 Planification CIDR

Un réseau IPv4 en `/24` contient 256 adresses au total, mais toutes ne sont pas nécessairement disponibles pour les ressources. Dans les sous-réseaux VPC Google Cloud, certaines adresses sont réservées à l'usage du réseau.

Exemple de plan :

| Fonction | Plage indicative |
|---|---|
| Services frontaux | `10.20.0.0/24` |
| Services applicatifs | `10.20.1.0/24` |
| Services de données | `10.20.2.0/24` |
| Extension future | `10.20.16.0/20` |

Les plages ne doivent pas entrer en conflit avec les réseaux locaux, les VPN, les VPC appairés ou les plages des environnements partenaires.

Un plan d'adressage est un document d'architecture, pas simplement une liste de CIDR. Il doit identifier les propriétaires, les usages, les extensions prévues et les réseaux avec lesquels des connexions seront établies.

### 6.4 Règles de pare-feu

Une règle de pare-feu doit être justifiée par un flux métier.

```text
Source autorisée
      |
      v
Règle de pare-feu
  - direction
  - priorité
  - protocole
  - ports
  - cibles
      |
      v
Ressource destinataire
```

Évitez d'autoriser tout Internet vers tous les ports. Pour une application web, il peut être légitime d'exposer HTTP/HTTPS via un point d'entrée approprié, mais pas d'exposer arbitrairement SSH, les bases de données ou les interfaces d'administration.

Exemple de règle interne limitée à un sous-réseau source :

```bash
gcloud compute firewall-rules create allow-app-internal \
  --network=app-network \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:8080 \
  --source-ranges=10.20.1.0/24 \
  --project=PROJECT_ID
```

Cet exemple n'est qu'un modèle : il faut vérifier que la plage source et la cible correspondent réellement à l'architecture. Pour un environnement de production, définissez explicitement les cibles de la règle, les journaux pertinents et la stratégie de gestion du pare-feu.

### 6.5 Routes et chemins réseau

Une route détermine le prochain saut pour le trafic correspondant à une destination. La présence d'une route ne signifie pas que le trafic est autorisé : les règles de pare-feu et les autres contrôles réseau continuent de s'appliquer.

```text
Application
   |
   v
Table de routage
   |
   +-- Réseau local au VPC
   |
   +-- Route vers une passerelle
   |
   +-- Route vers un réseau distant
   |
   +-- Absence de route appropriée -> échec
```

Commandes d'inspection :

```bash
gcloud compute routes list \
  --project=PROJECT_ID

gcloud compute firewall-rules list \
  --project=PROJECT_ID
```

## 7. Cloud NAT et accès sortant

Une machine virtuelle sans adresse IP externe peut nécessiter un accès sortant à Internet pour télécharger des mises à jour ou appeler des API publiques.

Cloud NAT permet une connectivité sortante pour des ressources configurées, sans devoir leur attribuer une adresse IP externe. Il ne s'agit pas d'un service qui rend automatiquement les machines accessibles depuis Internet.

### 7.1 Architecture

```text
VM sans IP externe
       |
       v
Sous-réseau VPC
       |
       v
Cloud NAT
       |
       v
Internet
```

Cloud NAT s'appuie sur une passerelle Cloud Router dans une région. La configuration dépend du réseau, du sous-réseau, des plages IP et du mode de réservation des adresses NAT.

### 7.2 Exemple de configuration

```bash
gcloud compute routers create app-router \
  --network=app-network \
  --region=REGION \
  --project=PROJECT_ID
```

Créer la passerelle NAT :

```bash
gcloud compute routers nats create app-nat \
  --router=app-router \
  --region=REGION \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips \
  --project=PROJECT_ID
```

La commande utilise une allocation automatique d'adresses IP NAT. En production, choisissez la stratégie d'adressage après avoir étudié les exigences de stabilité des IP, les quotas, la capacité NAT, les journaux et les coûts.

Examiner les routeurs :

```bash
gcloud compute routers list \
  --project=PROJECT_ID
```

Ne concluez pas que Cloud NAT est opérationnel simplement parce que la passerelle existe. Testez le chemin sortant depuis une ressource configurée sans IP externe, vérifiez les routes, les pare-feu, les journaux NAT et la résolution DNS.

## 8. Connectivité hybride : VPN et interconnexion

Une entreprise peut vouloir relier un réseau local à Google Cloud.

```text
Réseau d'entreprise
        |
   Routeur local
        |
   Tunnel VPN IPsec
        |
   Passerelle VPN GCP
        |
   VPC Google Cloud
        |
   Applications privées
```

### 8.1 Cloud VPN

Cloud VPN chiffre le trafic entre un réseau pair et Google Cloud via IPsec. HA VPN est conçu pour fournir une connectivité à haute disponibilité lorsque les interfaces, les tunnels et le côté distant sont configurés conformément aux exigences de disponibilité.

Les éléments à planifier :
- les plages IP de chaque côté ;
- le type de passerelle ;
- les adresses IP publiques des pairs ;
- les paramètres de tunnels et les clés partagées ;
- le routage statique ou dynamique selon la solution ;
- Cloud Router et BGP lorsqu'ils sont utilisés ;
- la supervision des tunnels ;
- les scénarios de bascule et de reprise.

Un tunnel établi ne prouve pas que tous les flux applicatifs fonctionnent. Il faut aussi vérifier les routes, les règles de pare-feu, le MTU, le DNS et les permissions des services.

### 8.2 Cloud Interconnect

Cloud Interconnect permet des connexions dédiées ou partenaires entre un réseau local et Google Cloud. Le choix dépend du débit, de la latence, de la disponibilité, des besoins de connectivité et du coût.

Cloud VPN et Cloud Interconnect ne sont pas interchangeables dans tous les scénarios. Le choix doit s'appuyer sur les exigences mesurées et le modèle de disponibilité visé.

## 9. Cloud Run : applications conteneurisées managées

Cloud Run permet d'exécuter des conteneurs sans gérer directement un cluster de machines. Il convient à de nombreuses API, applications web et tâches déclenchées par des événements.

### 9.1 Modèle de fonctionnement

```text
Code source
    |
    v
Image de conteneur
    |
    v
Artifact Registry
    |
    v
Révision Cloud Run
    |
    +-- Répartition du trafic
    |
    +-- Mise à l'échelle automatique
    |
    +-- Journalisation et métriques
```

Une révision représente une version du service. Le trafic peut être orienté vers différentes révisions pour permettre des déploiements progressifs ou des retours arrière.

### 9.2 Exemple de service public de démonstration

Pour une application déjà empaquetée dans un conteneur :

```bash
gcloud run deploy demo-api \
  --image=IMAGE_URI \
  --region=REGION \
  --project=PROJECT_ID
```

`IMAGE_URI` doit être remplacé par l'URI réelle d'une image accessible au déploiement. Vérifiez la source, la provenance et les autorisations d'accès à l'image.

Un service Cloud Run peut être privé ou public. Ne rendez pas une API publique uniquement pour simplifier un test. Si l'accès doit être restreint, configurez IAM et le chemin d'accès approprié.

### 9.3 Identité d'exécution

Attribuez au service un compte de service dédié qui possède uniquement les permissions requises pour lire les données, appeler les API ou publier les événements nécessaires.

```text
Requête HTTP
    |
    v
Service Cloud Run
    |
    v
Compte de service d'exécution
    |
    v
Permission limitée sur la ressource
```

Le compte qui déploie le service et le compte utilisé pendant son exécution sont deux identités différentes. Cette séparation réduit le risque d'accorder des permissions de déploiement à l'application elle-même.

### 9.4 Paramètres d'exploitation

Évaluez notamment :
- le nombre minimal et maximal d'instances ;
- le délai d'expiration des requêtes ;
- la concurrence par instance ;
- les ressources CPU et mémoire ;
- les variables d'environnement ;
- la gestion des secrets ;
- les accès réseau ;
- les sondes applicatives et les journaux ;
- les limites de débit et les protections contre les abus.

Les réglages influencent les performances, les coûts et la disponibilité. Il faut les mesurer avec une charge représentative.

## 10. Compute Engine : quand conserver les machines virtuelles

Compute Engine reste pertinent lorsqu'une charge exige un contrôle plus direct du système d'exploitation, une compatibilité particulière ou un modèle de déploiement spécifique.

```text
Équipe d'exploitation
       |
       v
Image de machine maîtrisée
       |
       v
Instance Compute Engine
       |
       +-- Compte de service dédié
       +-- Pare-feu ciblé
       +-- Journalisation
       +-- Mises à jour
       +-- Sauvegarde et récupération
```

### 10.1 Inspection

```bash
gcloud compute instances list \
  --project=PROJECT_ID

gcloud compute instances describe INSTANCE_NAME \
  --zone=ZONE \
  --project=PROJECT_ID
```

Pour examiner les disques :

```bash
gcloud compute disks list \
  --project=PROJECT_ID
```

Pour arrêter une instance de laboratoire :

```bash
gcloud compute instances stop INSTANCE_NAME \
  --zone=ZONE \
  --project=PROJECT_ID
```

L'arrêt d'une instance réduit généralement les coûts liés au calcul, mais ne supprime pas automatiquement les disques persistants, les adresses IP réservées ou les autres ressources facturables.

### 10.2 Accès administratif

Privilégiez des mécanismes d'accès contrôlés, tels qu'OS Login et IAP TCP forwarding lorsque l'architecture et les permissions le permettent. Évitez d'ouvrir SSH à toutes les adresses Internet.

Un accès administratif doit être :
- authentifié ;
- autorisé par IAM ;
- journalisé lorsque c'est possible ;
- limité aux personnes et aux opérations nécessaires ;
- révoqué quand il n'est plus nécessaire.

## 11. Bases de données et stockage

### 11.1 Choisir le bon service

| Besoin | Option à étudier |
|---|---|
| Base relationnelle compatible PostgreSQL ou MySQL | Cloud SQL |
| Base relationnelle avec exigences de disponibilité et d'échelle spécifiques | AlloyDB ou autre solution adaptée |
| Entrepôt analytique | BigQuery |
| Objets, documents et fichiers | Cloud Storage |
| Base NoSQL orientée documents | Firestore |
| Données clé-valeur à grande échelle et faible latence | Bigtable |

La liste n'est pas exhaustive. Le choix dépend du modèle de données, du débit, de la cohérence, de la latence, de la disponibilité, des compétences et du coût.

### 11.2 Cloud SQL

Cloud SQL est un service de base de données relationnelle managé. Il réduit la charge de gestion de certaines tâches, mais ne dispense pas de concevoir les sauvegardes, les accès, la capacité, la haute disponibilité, les mises à jour et la reprise.

Principes :
- ne pas exposer une base de données à Internet sans nécessité et contrôles appropriés ;
- utiliser les mécanismes d'accès privé lorsque c'est adapté ;
- limiter les identités et les comptes SQL ;
- conserver les secrets dans un gestionnaire de secrets ;
- tester les restaurations, pas seulement la présence des sauvegardes ;
- surveiller les connexions, le stockage, la charge et les requêtes lentes.

### 11.3 Cloud Storage

Les buckets doivent être conçus selon leur usage :
- données temporaires ou permanentes ;
- région, double région ou multirégion selon les exigences ;
- règles de rétention ;
- versionnement des objets lorsque nécessaire ;
- politiques de cycle de vie ;
- contrôles IAM ;
- prévention des accès publics non souhaités.

Le choix de l'emplacement influence la latence, la résilience, la résidence des données et les coûts. Une copie ou une réplication ne remplace pas automatiquement une stratégie de sauvegarde avec tests de restauration.

## 12. GKE : Kubernetes managé

Google Kubernetes Engine (GKE) exécute des applications conteneurisées sur Kubernetes. Il apporte des fonctionnalités managées, mais demande davantage de connaissances opérationnelles qu'un service de conteneurs sans cluster à administrer.

### 12.1 Architecture conceptuelle

```text
Développeur
    |
    v
Image conteneurisée
    |
    v
Déploiement Kubernetes
    |
    v
Cluster GKE
    |
    +-- Plan de contrôle managé
    |
    +-- Nœuds de calcul
    |
    +-- Pods
    |
    +-- Services et règles réseau
    |
    +-- Journalisation et métriques
```

Les responsabilités exactes dépendent du mode GKE choisi. Le plan de contrôle est managé par Google, mais les charges de travail, les droits, les ressources Kubernetes, les mises à jour et de nombreux paramètres restent sous la responsabilité du client.

### 12.2 Objets fondamentaux

- **Pod :** unité d'exécution Kubernetes.
- **Deployment :** déclare l'état désiré d'un ensemble de Pods.
- **Service :** fournit un point d'accès stable aux Pods.
- **ConfigMap :** contient une configuration non secrète.
- **Secret :** représente des données sensibles, dont la protection doit être conçue avec soin.
- **Namespace :** sépare logiquement des objets au sein d'un cluster.
- **Ingress ou Gateway :** permet de configurer des chemins d'entrée selon le contrôleur et la solution utilisés.

### 12.3 Exemple de manifeste

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-demo
  template:
    metadata:
      labels:
        app: web-demo
    spec:
      containers:
        - name: web
          image: IMAGE_URI
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
```

Remplacez `IMAGE_URI` par une image valide qui écoute réellement sur le port configuré. Les ressources indiquées sont des valeurs d'exemple, pas des valeurs universelles pour la production.

Commandes Kubernetes :

```bash
kubectl get deployments
kubectl get pods
kubectl describe deployment web-demo
kubectl logs deployment/web-demo
```

N'utilisez pas GKE par défaut pour toutes les applications. Si Cloud Run satisfait les exigences fonctionnelles, de sécurité et de performance, il peut réduire la complexité d'exploitation.

## 13. Infrastructure as Code avec Terraform

Terraform décrit l'infrastructure dans des fichiers déclaratifs. Il permet de versionner la configuration, de revoir les changements et de reproduire les environnements.

### 13.1 Cycle Terraform

```text
Code Terraform
      |
      v
terraform init
      |
      v
terraform fmt / validate
      |
      v
terraform plan
      |
      v
Revue du plan
      |
      v
terraform apply
      |
      v
Infrastructure réelle
```

Un plan doit être examiné avant application. Il peut contenir des changements destructifs, des modifications d'accès ou des ressources facturables.

### 13.2 Exemple : réseau et sous-réseau

Fichier `main.tf` :

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

variable "project_id" {
  description = "Identifiant du projet GCP"
  type        = string
}

variable "region" {
  description = "Région du sous-réseau"
  type        = string
  default     = "europe-west1"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_compute_network" "app" {
  name                    = "tf-app-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "app" {
  name          = "tf-app-subnet"
  region        = var.region
  network       = google_compute_network.app.id
  ip_cidr_range = "10.30.0.0/24"
}

output "network_name" {
  value = google_compute_network.app.name
}

output "subnetwork_name" {
  value = google_compute_subnetwork.app.name
}
```

Ce code est un exemple de laboratoire. Il ne crée pas de règles de pare-feu, de Cloud NAT ni de contrôles de production. Le CIDR et le nom des ressources doivent être vérifiés avant utilisation.

### 13.3 Initialisation et validation

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -var="project_id=PROJECT_ID"
```

Après examen du plan :

```bash
terraform apply -var="project_id=PROJECT_ID"
```

Pour détruire uniquement l'infrastructure du laboratoire gérée par cette configuration :

```bash
terraform plan -destroy -var="project_id=PROJECT_ID"
terraform destroy -var="project_id=PROJECT_ID"
```

N'exécutez pas `destroy` dans un environnement partagé ou de production sans procédure d'approbation et vérification de l'état. Terraform ne gère que les ressources présentes dans son état et déclarées par sa configuration ; des ressources créées manuellement peuvent rester en place.

### 13.4 État Terraform

Le fichier d'état contient des informations nécessaires pour faire le lien entre la configuration et les ressources réelles. Il peut contenir des données sensibles.

Bonnes pratiques :
- ne pas versionner l'état local dans Git ;
- utiliser un backend distant approprié pour le travail en équipe ;
- limiter l'accès à l'état ;
- activer le verrouillage lorsque le backend le prend en charge ;
- protéger les identifiants utilisés par le pipeline ;
- ne pas stocker de secrets en clair dans les fichiers de variables ;
- examiner les plans avant application.

### 13.5 Importation et dérive

Une ressource créée manuellement peut nécessiter une importation avant d'être gérée par Terraform. L'importation ne signifie pas que la configuration est complète : il faut ensuite aligner le code et l'état réel.

La dérive désigne une différence entre la configuration attendue et l'infrastructure réelle. Une revue régulière des plans permet de la détecter, mais les mécanismes de détection doivent être intégrés au processus d'exploitation.

## 14. CI/CD et livraison continue

Une chaîne CI/CD fiable ne se limite pas à lancer une commande de déploiement à chaque commit. Elle doit valider le code, tester l'application, produire une image traçable et appliquer un contrôle d'accès adapté.

### 14.1 Chaîne type

```text
Commit Git
   |
   v
Tests automatiques
   |
   v
Vérification du code et dépendances
   |
   v
Construction de l'image
   |
   v
Analyse de l'image
   |
   v
Publication dans Artifact Registry
   |
   v
Déploiement en préproduction
   |
   v
Tests de validation
   |
   v
Approbation éventuelle
   |
   v
Déploiement en production
   |
   v
Surveillance et retour arrière si nécessaire
```

### 14.2 Sécurité du pipeline

- Ne stockez pas les clés de comptes de service dans le dépôt.
- Préférez Workload Identity Federation lorsque la plateforme CI et le contexte le permettent.
- Séparez les identités de construction et de déploiement.
- Limitez les permissions aux projets et ressources nécessaires.
- Protégez les branches et les secrets.
- Conservez la traçabilité de l'image et du commit déployés.
- Ajoutez des validations pour les changements d'infrastructure.
- Contrôlez les dépendances et les images de base.
- Évitez de déployer directement un artefact non testé.

### 14.3 Retour arrière

Un retour arrière doit restaurer une version connue et testée, sans provoquer une incompatibilité de schéma de données ou de configuration.

```text
Version A : stable
     |
     v
Déploiement version B
     |
     +-- Tests réussis -> poursuivre
     |
     +-- Erreurs détectées
             |
             v
       Réorienter le trafic
       vers la version A
```

Le retour arrière n'est pas toujours une simple inversion. Les migrations de base de données doivent être conçues pour supporter, lorsque c'est nécessaire, plusieurs versions de l'application durant la transition.

## 15. Observabilité : logs, métriques et alertes

### 15.1 Les trois piliers

- **Logs :** événements détaillés et contextualisés.
- **Métriques :** mesures numériques dans le temps.
- **Traces :** chemin d'une requête à travers plusieurs composants.

```text
Requête utilisateur
       |
       v
Frontend
       |
       v
API
       |
       v
Base de données

Logs   -> événements de chaque composant
Métriques -> latence, débit, erreurs, saturation
Traces -> temps passé dans chaque étape
```

### 15.2 Signaux à surveiller

Pour une API :
- débit des requêtes ;
- taux d'erreur ;
- latence médiane et percentiles élevés ;
- saturation CPU et mémoire ;
- temps de réponse des dépendances ;
- nombre de connexions à la base ;
- erreurs d'authentification ;
- échecs de déploiement.

### 15.3 Lire des journaux Cloud Run

```bash
gcloud logging read \
  'resource.type="cloud_run_revision"' \
  --project=PROJECT_ID \
  --limit=20 \
  --format=json
```

Cette requête est volontairement générale. En production, filtrez par service, révision, sévérité et période pour éviter de lire des événements sans rapport avec l'incident.

### 15.4 Alertes

Une alerte utile indique :
- le symptôme détecté ;
- la gravité ;
- le service concerné ;
- l'impact utilisateur probable ;
- la procédure de diagnostic ;
- la personne ou l'équipe responsable.

Évitez les alertes qui se déclenchent constamment sans action claire. Une alerte doit déclencher une investigation ou une réponse opérationnelle définie.

## 16. Sécurité des applications

### 16.1 Gestion des secrets

Les mots de passe, clés API et certificats privés ne doivent pas être inscrits en clair dans Git ou dans une image de conteneur.

Utilisez un gestionnaire de secrets approprié, par exemple Secret Manager, avec des permissions limitées au service qui doit lire chaque secret.

```text
Secret Manager
      |
      | accès autorisé
      v
Compte de service applicatif
      |
      v
Application
```

La rotation des secrets, les journaux d'accès et les procédures de révocation doivent être prévus.

### 16.2 Défense en profondeur

```text
Couche 1 : identité et authentification
Couche 2 : permissions IAM
Couche 3 : contrôles réseau
Couche 4 : sécurité du conteneur et du système
Couche 5 : validation des entrées
Couche 6 : gestion des secrets
Couche 7 : logs, alertes et réponse aux incidents
```

Aucune couche ne remplace toutes les autres. Un pare-feu ne corrige pas une autorisation IAM trop large, et un rôle IAM restreint ne corrige pas une vulnérabilité applicative.

## 17. Sauvegarde et disponibilité

### 17.1 Disponibilité et sauvegarde

La haute disponibilité réduit l'impact de certaines pannes. La sauvegarde protège contre la perte ou la corruption de données. Ce sont des objectifs différents.

```text
Haute disponibilité
  -> réduire l'interruption de service

Sauvegarde
  -> disposer d'une copie récupérable

Restauration testée
  -> prouver que la copie peut être utilisée
```

### 17.2 RPO et RTO

- **RPO (Recovery Point Objective) :** perte maximale de données acceptable, exprimée en durée.
- **RTO (Recovery Time Objective) :** durée maximale acceptable pour rétablir le service.

Exemple : un RPO de 15 minutes signifie que l'organisation vise à ne pas perdre plus de 15 minutes de données dans le scénario considéré. Cela ne garantit ce résultat que si l'architecture, la réplication, les sauvegardes et les procédures le permettent réellement.

### 17.3 Plan de reprise

Pour chaque service critique :
1. identifier les dépendances ;
2. définir le RPO et le RTO ;
3. sélectionner les mécanismes de sauvegarde ou de réplication ;
4. documenter les étapes de restauration ;
5. sécuriser les copies ;
6. tester la restauration ;
7. mesurer le temps réel de reprise ;
8. corriger les écarts.

## 18. FinOps : maîtriser les coûts

Les coûts ne proviennent pas uniquement du calcul. Ils peuvent aussi venir du stockage, des opérations de stockage, des transferts réseau, des adresses IP, des journaux, des services managés et des ressources oubliées.

### 18.1 Méthode de contrôle

```text
Identifier les ressources
       |
       v
Attribuer projets et labels
       |
       v
Mesurer la consommation
       |
       v
Définir budgets et alertes
       |
       v
Analyser les tendances
       |
       v
Optimiser et vérifier le résultat
```

### 18.2 Bonnes pratiques

- définir un budget par projet ou environnement ;
- examiner les coûts de transfert de données ;
- choisir les tailles d'instances à partir de mesures ;
- ajuster les limites de mise à l'échelle ;
- définir les politiques de cycle de vie du stockage ;
- supprimer les ressources temporaires ;
- éviter les clusters surdimensionnés ;
- suivre les coûts des journaux et des métriques ;
- vérifier les coûts régionaux avant de choisir une architecture.

Un budget sert à suivre la consommation et à déclencher des alertes. Il ne bloque pas automatiquement tous les nouveaux frais.

## 19. Travaux pratiques guidés

### TP 1 — Construire un réseau personnalisé

**Objectif :** créer un VPC et un sous-réseau sans activer de sous-réseaux automatiques.

1. Sélectionner un projet de laboratoire.
2. Vérifier les autorisations nécessaires.
3. Créer `app-network`.
4. Créer `app-subnet` en `10.40.0.0/24`.
5. Lister le réseau et le sous-réseau.
6. Examiner les routes.
7. Documenter les plages réservées et les plages futures.

Commandes principales :

```bash
gcloud compute networks create app-network \
  --subnet-mode=custom \
  --project=PROJECT_ID

gcloud compute networks subnets create app-subnet \
  --network=app-network \
  --region=REGION \
  --range=10.40.0.0/24 \
  --project=PROJECT_ID

gcloud compute networks describe app-network \
  --project=PROJECT_ID

gcloud compute networks subnets list \
  --filter="network:app-network" \
  --project=PROJECT_ID
```

**Résultat attendu :** le réseau et son sous-réseau sont visibles dans le projet et la région prévus.

### TP 2 — Déployer une application Cloud Run

**Objectif :** déployer un conteneur existant et vérifier son fonctionnement.

1. Sélectionner une image de confiance.
2. Vérifier les permissions et l'API Cloud Run.
3. Déployer le service.
4. Examiner la configuration et l'URL.
5. Tester l'application.
6. Lire les journaux.
7. Vérifier si le service doit être public ou privé.

Exemple :

```bash
gcloud services enable run.googleapis.com \
  --project=PROJECT_ID

gcloud run deploy demo-api \
  --image=IMAGE_URI \
  --region=REGION \
  --project=PROJECT_ID
```

N'ajoutez pas une option d'accès public sans avoir décidé que l'application doit être accessible sans authentification.

### TP 3 — Décrire une infrastructure avec Terraform

1. Créer un répertoire de travail.
2. Ajouter le fichier `main.tf` présenté au chapitre Terraform.
3. Définir le projet.
4. Initialiser Terraform.
5. Formater et valider la configuration.
6. Générer un plan.
7. Vérifier chaque ressource prévue.
8. Appliquer le plan.
9. Inspecter les ressources avec `gcloud`.
10. Détruire le laboratoire après vérification du plan de destruction.

Critère de réussite : le code, le plan et les ressources créées doivent correspondre.

### TP 4 — Diagnostiquer une panne de service

**Scénario :** un service Cloud Run répond par des erreurs.

Procédure :
1. confirmer le service, la région et la révision ;
2. lire les journaux ;
3. vérifier les erreurs de démarrage et le port d'écoute ;
4. vérifier les variables d'environnement et les secrets ;
5. examiner l'identité d'exécution et les permissions ;
6. tester les dépendances ;
7. déterminer si le problème vient du code, du réseau, des permissions ou d'une dépendance ;
8. documenter la cause et la correction.

Ne modifiez pas plusieurs paramètres simultanément sans garder de trace : cela rend l'identification de la cause plus difficile.

## 20. Exercices corrigés

### Exercice 1

**Question :** pourquoi séparer développement et production dans deux projets ?

**Correction :** cette séparation permet de limiter les permissions, d'isoler les ressources et les quotas, de différencier la facturation et de réduire le risque qu'une manipulation de développement affecte les ressources de production. Elle doit être accompagnée d'une gestion correcte des identités et des permissions héritées.

### Exercice 2

**Question :** Cloud NAT rend-il une VM accessible depuis Internet ?

**Correction :** non. Cloud NAT fournit une connectivité sortante aux ressources configurées. Il ne constitue pas un mécanisme d'accès entrant général à une VM.

### Exercice 3

**Question :** quel est le rôle de Terraform state ?

**Correction :** il maintient la correspondance entre les objets décrits dans la configuration Terraform et les ressources gérées. Il peut contenir des informations sensibles et doit être protégé.

### Exercice 4

**Question :** faut-il utiliser GKE pour chaque application conteneurisée ?

**Correction :** non. Cloud Run peut être plus simple pour des services compatibles avec son modèle d'exécution. GKE se justifie notamment lorsque les besoins Kubernetes, les contrôles du cluster ou l'écosystème d'orchestration sont nécessaires.

### Exercice 5

**Question :** une sauvegarde configurée garantit-elle la reprise ?

**Correction :** non. La capacité de restauration doit être testée, mesurée et documentée. Les permissions, les clés, les dépendances et le temps de reprise doivent aussi être vérifiés.

### Exercice 6

**Question :** un budget GCP empêche-t-il automatiquement les dépassements ?

**Correction :** non. Un budget et ses alertes permettent de suivre la consommation. Il faut mettre en place séparément les contrôles opérationnels nécessaires pour réduire les dépenses non souhaitées.

## 21. Projet final corrigé — Application web cloud

### Objectif

Concevoir une plateforme de préproduction pour une application web avec :
- un projet dédié ;
- un VPC personnalisé et un plan CIDR documenté ;
- un service Cloud Run ;
- un compte de service d'exécution dédié ;
- une politique d'accès adaptée ;
- une journalisation exploitable ;
- une infrastructure décrite avec Terraform ;
- une procédure de déploiement et de retour arrière ;
- un budget et une procédure de nettoyage.

### Architecture cible

```text
Équipe de développement
       |
       v
Dépôt Git
       |
       v
Tests et validation
       |
       v
Artifact Registry
       |
       v
Cloud Run
       |
       +----> Cloud Logging
       |
       +----> Cloud Monitoring
       |
       +----> Service de données si nécessaire

Terraform
   |
   +----> VPC et sous-réseau
   +----> Ressources prises en charge par le code
   +----> Révision et contrôle des changements
```

### Étape 1 — Définir les exigences

Avant de déployer, documenter :
- l'identifiant du projet ;
- la région ;
- les données utilisées ;
- le caractère public ou privé du service ;
- les permissions de l'application ;
- les objectifs de disponibilité ;
- les limites de coût ;
- les exigences de suppression et de restauration.

### Étape 2 — Créer le réseau

Utiliser le TP 1 et vérifier le plan CIDR. Si Cloud Run doit accéder à des ressources privées dans le VPC, concevoir le mécanisme de connectivité approprié et vérifier ses limites, ses permissions et ses coûts.

### Étape 3 — Sécuriser l'exécution

Créer un compte de service dédié. Accorder uniquement les rôles nécessaires à l'accès aux données ou aux API utilisées. Ne pas utiliser un compte de service administrateur comme identité d'exécution.

### Étape 4 — Déployer et vérifier

Déployer une image de confiance sur Cloud Run. Vérifier :
- le statut de la révision ;
- l'URL et le contrôle d'accès ;
- les journaux ;
- le port d'écoute ;
- la configuration ;
- les permissions sur les dépendances.

### Étape 5 — Automatiser l'infrastructure

Utiliser Terraform pour les ressources qu'il doit gérer. Exécuter `fmt`, `validate` et `plan`. Faire examiner les changements avant application. Ne pas mélanger sans stratégie l'administration manuelle et la gestion automatisée des mêmes ressources.

### Étape 6 — Définir l'exploitation

Établir :
- une procédure de diagnostic ;
- des alertes sur les symptômes importants ;
- un propriétaire de service ;
- une procédure de retour arrière ;
- une procédure de restauration des données ;
- un contrôle des coûts.

### Étape 7 — Vérifier le nettoyage

Avant de supprimer :
1. identifier les ressources créées par le projet ;
2. vérifier les données à conserver ;
3. examiner le plan de destruction Terraform ;
4. vérifier les ressources créées manuellement ;
5. supprimer les ressources de laboratoire autorisées ;
6. contrôler les disques, adresses IP, journaux et autres ressources restantes.

### Critères de validation

Le projet est réussi si :
- l'application fonctionne ;
- l'accès est conforme aux exigences ;
- les permissions sont limitées ;
- le réseau est documenté ;
- les journaux permettent le diagnostic ;
- l'infrastructure est reproductible ;
- le retour arrière est décrit ;
- les coûts sont suivis ;
- le nettoyage ne laisse pas de ressources de laboratoire oubliées.

## 22. Glossaire

- **API GCP :** interface activée pour permettre l'utilisation d'un service.
- **Artifact Registry :** stockage des artefacts, notamment les images de conteneurs.
- **BGP :** protocole de routage dynamique utilisé dans certaines architectures hybrides.
- **CIDR :** notation de plage d'adresses IP.
- **Cloud NAT :** service de traduction d'adresses pour la connectivité sortante.
- **Cloud Run :** plateforme managée d'exécution de conteneurs.
- **GKE :** service Kubernetes managé de Google Cloud.
- **IAM :** gestion des identités et des accès.
- **RPO :** objectif de point de reprise.
- **RTO :** objectif de temps de reprise.
- **Terraform :** outil déclaratif d'Infrastructure as Code.
- **VPC :** réseau virtuel privé Google Cloud.

## 23. Documentation officielle

- Présentation de Google Cloud : https://cloud.google.com/docs
- Google Cloud CLI : https://cloud.google.com/sdk/docs
- IAM : https://cloud.google.com/iam/docs
- VPC : https://cloud.google.com/vpc/docs
- Cloud NAT : https://cloud.google.com/nat/docs
- Cloud VPN : https://cloud.google.com/network-connectivity/docs/vpn
- Cloud Run : https://cloud.google.com/run/docs
- Compute Engine : https://cloud.google.com/compute/docs
- Google Kubernetes Engine : https://cloud.google.com/kubernetes-engine/docs
- Cloud SQL : https://cloud.google.com/sql/docs
- Cloud Storage : https://cloud.google.com/storage/docs
- Cloud Logging : https://cloud.google.com/logging/docs
- Cloud Monitoring : https://cloud.google.com/monitoring/docs
- Terraform pour Google Cloud : https://cloud.google.com/docs/terraform
- Terraform Google provider : https://registry.terraform.io/providers/hashicorp/google/latest/docs
- Budgets et alertes de facturation : https://cloud.google.com/billing/docs/how-to/budgets

## 24. Checklist de fin de niveau

- [ ] Je sais organiser plusieurs projets et environnements.
- [ ] Je comprends les VPC, sous-réseaux, routes et règles de pare-feu.
- [ ] Je sais expliquer le rôle de Cloud NAT.
- [ ] Je comprends les bases d'une connexion hybride.
- [ ] Je sais distinguer Cloud Run, Compute Engine et GKE.
- [ ] Je sais concevoir des permissions IAM limitées.
- [ ] Je sais utiliser Terraform avec une revue du plan.
- [ ] Je comprends les bases d'une chaîne CI/CD sécurisée.
- [ ] Je sais diagnostiquer un service avec les journaux et les métriques.
- [ ] Je sais différencier haute disponibilité, sauvegarde et reprise.
- [ ] Je sais identifier les principaux facteurs de coût.
- [ ] Je sais supprimer proprement les ressources d'un laboratoire.

**Passage au niveau expert :** le prochain cours aborde la gouvernance multi-projets à l'échelle de l'organisation, les landing zones, les contrôles de sécurité avancés, la conception multi-région, le SRE, la reprise après sinistre et l'optimisation opérationnelle et financière.
