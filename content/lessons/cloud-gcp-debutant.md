
# Google Cloud Platform (GCP) — Cours complet pour débutants

**Fichier :** `cloud-gcp-debutant.md`  
**Niveau :** Débutant  
**Domaine :** Cloud computing, infrastructure, réseau, sécurité et administration  
**Prérequis :** Connaissances informatiques générales. Une familiarité avec les réseaux et la ligne de commande est utile, mais non obligatoire.

## Objectifs pédagogiques

À la fin de ce cours, l'apprenant sera capable de :

- expliquer le fonctionnement du cloud computing ;
- identifier les principaux services Google Cloud ;
- comprendre l'organisation des organisations, dossiers, projets et ressources ;
- configurer un projet et comprendre la facturation ;
- utiliser la console Google Cloud et Cloud Shell ;
- exécuter les commandes essentielles de `gcloud` ;
- comprendre IAM, les rôles et les comptes de service ;
- différencier régions et zones ;
- créer et administrer une machine virtuelle Compute Engine ;
- utiliser Cloud Storage ;
- comprendre les réseaux VPC, les sous-réseaux, les routes et les règles de pare-feu ;
- appliquer les premières mesures de sécurité ;
- superviser les ressources et diagnostiquer les problèmes courants ;
- réaliser un projet complet de déploiement dans un environnement de laboratoire.

## 1. Introduction au cloud computing

### 1.1 Qu'est-ce que le cloud computing ?

Le cloud computing permet d'utiliser des ressources informatiques fournies par un prestataire distant : calcul, stockage, réseau, bases de données, sécurité et outils d'exploitation.

Au lieu d'acheter et d'entretenir tous les serveurs physiques d'un datacenter, une entreprise peut louer des ressources adaptées à ses besoins.

Exemple traditionnel :

```text
Entreprise
    |
    +-- Salle informatique
    |     +-- Serveurs physiques
    |     +-- Stockage
    |     +-- Commutateurs
    |     +-- Routeurs
    |     +-- Onduleurs
    |
    +-- Équipe d'administration
          +-- Maintenance
          +-- Mises à jour
          +-- Remplacement du matériel
```

Exemple dans le cloud :

```text
Entreprise
    |
    +-- Connexion réseau
    |
    +-- Google Cloud
          +-- Machines virtuelles
          +-- Réseaux virtuels
          +-- Stockage
          +-- Bases de données managées
          +-- Supervision
```

L'entreprise conserve des responsabilités concernant les identités, les données, les configurations, les applications et la sécurité. Le fournisseur prend en charge une partie de l'infrastructure physique et des services sous-jacents.

### 1.2 Les principaux modèles de service

**IaaS — Infrastructure as a Service**

Le fournisseur propose des ressources d'infrastructure. Le client conserve généralement une responsabilité importante concernant le système d'exploitation et les applications.

Exemple : Compute Engine.

**PaaS — Platform as a Service**

Le fournisseur prend en charge davantage de composants techniques afin de faciliter le déploiement des applications.

Exemples : Cloud Run et certains services de bases de données managées.

**SaaS — Software as a Service**

Le client utilise une application fournie comme un service, sans administrer directement son infrastructure sous-jacente.

Exemples : Gmail et Google Workspace.

### 1.3 Modèles de déploiement

- **Cloud public :** ressources fournies par un prestataire cloud.
- **Cloud privé :** infrastructure dédiée à une organisation.
- **Cloud hybride :** combinaison d'environnements cloud et d'infrastructures existantes.
- **Multicloud :** utilisation de plusieurs fournisseurs cloud.

Google Cloud peut être intégré à des datacenters privés et à d'autres fournisseurs, notamment au moyen de VPN, de connectivités privées et de solutions de gestion adaptées.

### 1.4 Avantages et limites

Avantages :

- capacité d'adaptation ;
- accès rapide aux ressources ;
- services managés ;
- automatisation ;
- distribution géographique ;
- paiement lié à l'utilisation selon le service ;
- intégration de solutions de sécurité et de supervision.

Limites et risques :

- coûts difficiles à anticiper sans suivi ;
- dépendance à la connectivité ;
- erreurs de configuration ;
- privilèges excessifs ;
- dépendance à certains services propriétaires ;
- complexité des architectures distribuées ;
- nécessité de concevoir la sauvegarde et la reprise.

Le cloud ne supprime pas les problèmes d'exploitation : il modifie la manière de les résoudre.

## 2. Découvrir Google Cloud Platform

### 2.1 Les grandes familles de services

| Domaine | Services Google Cloud | Fonction |
|---|---|---|
| Calcul | Compute Engine | Machines virtuelles |
| Conteneurs | Google Kubernetes Engine (GKE) | Orchestration Kubernetes |
| Applications serverless | Cloud Run | Exécution de conteneurs managés |
| Stockage objet | Cloud Storage | Fichiers et objets |
| Bases relationnelles | Cloud SQL | Bases SQL managées |
| Analyse de données | BigQuery | Analyse de grands volumes de données |
| Réseau | VPC, Cloud NAT, Cloud VPN | Connectivité et routage |
| Équilibrage | Cloud Load Balancing | Répartition du trafic |
| Identité | IAM | Autorisations et contrôle d'accès |
| Secrets | Secret Manager | Gestion des secrets |
| Journaux | Cloud Logging | Collecte et consultation des journaux |
| Métriques | Cloud Monitoring | Mesures, tableaux de bord et alertes |
| Automatisation | Cloud Build | Construction et automatisation des pipelines |
| Images de conteneurs | Artifact Registry | Stockage d'artefacts et d'images |

Il n'est pas nécessaire de maîtriser tous ces services dès le début. Il faut d'abord comprendre leur rôle et savoir sélectionner le service adapté au besoin.

### 2.2 Choisir le bon service de calcul

Considérons une application web.

- Compute Engine convient lorsque l'on souhaite administrer une machine virtuelle.
- Cloud Run convient à de nombreux services conteneurisés sans vouloir gérer directement les serveurs.
- GKE convient aux architectures nécessitant Kubernetes et ses mécanismes d'orchestration.

```text
Application à déployer
        |
        v
Quel niveau de contrôle est nécessaire ?
        |
        +-- Système d'exploitation et VM
        |       |
        |       v
        |   Compute Engine
        |
        +-- Conteneur avec infrastructure managée
        |       |
        |       v
        |   Cloud Run
        |
        +-- Kubernetes et orchestration avancée
                |
                v
               GKE
```

Ces choix ne sont pas absolus. Le niveau de contrôle, la complexité opérationnelle, les contraintes de déploiement et le coût doivent être évalués.

## 3. Organisation des ressources Google Cloud

### 3.1 La hiérarchie des ressources

Google Cloud organise les ressources dans une hiérarchie.

```text
Organisation
    |
    +-- Dossier : Production
    |      |
    |      +-- Projet : application-prod
    |      |      +-- VM
    |      |      +-- Réseau VPC
    |      |      +-- Bucket Cloud Storage
    |      |
    |      +-- Projet : donnees-prod
    |
    +-- Dossier : NonProduction
           |
           +-- Projet : application-dev
           +-- Projet : laboratoire
```

Les organisations et les dossiers sont utiles pour les environnements qui en disposent. Un utilisateur individuel peut commencer sans organisation Google Cloud.

Les projets sont indispensables pour organiser les ressources et les autorisations, activer les API et gérer les paramètres de facturation associés.

### 3.2 Comprendre un projet

Un projet constitue un périmètre de gestion important.

Il permet notamment de :

- regrouper des ressources ;
- activer des API ;
- définir des autorisations IAM ;
- associer une facturation ;
- consulter des métriques et des journaux ;
- organiser des environnements indépendants.

Exemples de noms :

```text
mon-application-dev
mon-application-test
mon-application-prod
```

L'identifiant technique du projet doit être unique dans Google Cloud et ne peut pas être modifié après sa création. Il faut donc choisir cet identifiant avec soin.

### 3.3 Créer un projet

Dans la console Google Cloud :

1. Ouvrir https://console.cloud.google.com/
2. Accéder au sélecteur de projets.
3. Choisir la création d'un projet.
4. Définir un nom.
5. Choisir l'organisation ou le dossier approprié, si disponible.
6. Définir l'identifiant du projet.
7. Créer le projet.

Le compte doit disposer des autorisations nécessaires.

### 3.4 Configurer la CLI

La Google Cloud CLI fournit l'outil `gcloud` pour administrer les ressources depuis un terminal.

Dans Cloud Shell, elle est généralement déjà disponible.

Vérifier :

```bash
gcloud version
```

Afficher la configuration :

```bash
gcloud config list
```

Afficher le projet courant :

```bash
gcloud config get-value project
```

Définir le projet :

```bash
gcloud config set project PROJECT_ID
```

Remplacer `PROJECT_ID` par l'identifiant réel.

Vérifier :

```bash
gcloud projects describe PROJECT_ID
```

La commande ne réussira que si le projet existe et si l'identité possède les autorisations nécessaires.

### 3.5 Pourquoi séparer les environnements ?

Une entreprise peut utiliser des projets différents pour le développement, les tests et la production.

```text
Développement
    |
    +-- Modifications fréquentes
    +-- Tests
    +-- Ressources temporaires

Test
    |
    +-- Validation
    +-- Tests d'intégration
    +-- Tests de charge

Production
    |
    +-- Services métier
    +-- Données réelles
    +-- Surveillance renforcée
```

Cette séparation limite les erreurs et facilite l'attribution des coûts. Elle ne remplace pas les règles IAM ni les contrôles réseau.

## 4. Facturation et maîtrise des coûts

### 4.1 Comprendre la facturation

Google Cloud facture les services selon leurs caractéristiques : ressources consommées, durée d'utilisation, capacité provisionnée, requêtes, stockage ou transfert de données.

Les modalités varient selon le produit et la configuration.

Les principaux éléments à surveiller sont :

- les machines virtuelles en fonctionnement ;
- les disques persistants ;
- les adresses IP et autres ressources réseau facturables ;
- le stockage et les opérations ;
- les transferts de données ;
- les journaux conservés ;
- les services managés ;
- les ressources oubliées après un laboratoire.

### 4.2 Associer un compte de facturation

Dans la console :

1. Ouvrir la section Facturation.
2. Vérifier le compte de facturation.
3. Associer le projet si nécessaire.
4. Contrôler les permissions.
5. Examiner les rapports de dépenses.

Certains services nécessitent que la facturation soit activée. Les conditions dépendent du service et du projet.

### 4.3 Configurer un budget

Dans la section Facturation, créer un budget associé au périmètre approprié.

Configurer :

- le projet ou l'ensemble de projets à surveiller ;
- le montant cible ;
- les seuils d'alerte ;
- les destinataires des notifications.

**Important : un budget et ses alertes ne constituent pas automatiquement un plafond de dépense.** Les notifications peuvent également arriver après la consommation concernée, selon les délais de traitement de la facturation.

### 4.4 Bonnes pratiques de laboratoire

- Utiliser un projet dédié.
- Éviter les machines surdimensionnées.
- Créer uniquement les ressources nécessaires.
- Arrêter ou supprimer les ressources inutilisées.
- Vérifier les disques et les adresses IP conservés.
- Surveiller la facturation.
- Ne jamais supposer qu'une ressource est gratuite sans vérifier ses conditions.

## 5. Régions et zones

### 5.1 Définition

Une région correspond à une zone géographique contenant des ressources d'infrastructure Google Cloud.

Une région peut comporter plusieurs zones.

```text
Google Cloud
    |
    +-- Région A
    |      +-- Zone A
    |      +-- Zone B
    |      +-- Zone C
    |
    +-- Région B
           +-- Zone A
           +-- Zone B
```

Les zones sont des domaines de déploiement distincts au sein d'une région. Elles peuvent aider à réduire l'impact de certaines pannes, mais ne garantissent pas à elles seules la disponibilité de l'application.

### 5.2 Choisir une région

Les critères incluent :

- la proximité des utilisateurs ;
- la latence ;
- les exigences de résidence des données ;
- la disponibilité du service ;
- les quotas ;
- le coût ;
- les besoins de reprise après sinistre.

Les régions et zones disponibles doivent être vérifiées pour chaque service.

### 5.3 Lister les régions et zones

```bash
gcloud compute regions list
```

Pour les zones :

```bash
gcloud compute zones list
```

Pour filtrer les zones d'une région, utiliser le filtre approprié après avoir vérifié le nom exact de la région.

## 6. Identité et contrôle d'accès (IAM)

### 6.1 Comprendre IAM

IAM signifie Identity and Access Management.

IAM détermine qui peut effectuer quelles actions sur quelles ressources.

Les éléments fondamentaux sont :

- **Principal :** identité qui reçoit une autorisation.
- **Rôle :** ensemble de permissions.
- **Ressource :** objet sur lequel l'action est autorisée.
- **Stratégie IAM :** document qui associe les principaux et les rôles.

```text
Principal
   |
   v
Rôle IAM
   |
   v
Permissions
   |
   v
Ressource Google Cloud
```

Un rôle ne donne pas nécessairement accès à toutes les ressources. Le périmètre de l'attribution et les permissions du rôle déterminent l'accès effectif.

### 6.2 Principaux types de rôles

**Rôles de base**

- Owner
- Editor
- Viewer

Ces rôles sont larges. Ils ne doivent pas être attribués par défaut à tous les utilisateurs.

**Rôles prédéfinis**

Ils sont conçus pour des responsabilités spécifiques, par exemple l'administration de Compute Engine ou la consultation des journaux.

**Rôles personnalisés**

Ils permettent de définir un ensemble de permissions adapté à une responsabilité particulière, sous réserve des restrictions de la plateforme.

### 6.3 Principe du moindre privilège

Un utilisateur qui doit seulement consulter des journaux ne devrait pas recevoir un rôle permettant de modifier toutes les ressources.

Exemple :

```text
Technicien de supervision
    |
    +-- Lecture des journaux
    +-- Consultation des métriques
    |
    +-- Pas de suppression de VM
    +-- Pas de modification des rôles IAM
```

La moindre permission nécessaire doit être accordée au bon périmètre.

### 6.4 Consulter les attributions IAM

```bash
gcloud projects get-iam-policy PROJECT_ID
```

La commande retourne la stratégie IAM du projet, sous réserve des permissions de lecture.

Les stratégies au niveau de l'organisation, des dossiers et des ressources peuvent aussi intervenir dans l'accès effectif.

### 6.5 Comptes de service

Un compte de service est une identité utilisée par une application, une machine ou un processus automatisé.

Exemple :

```text
Application
    |
    v
Compte de service dédié
    |
    v
Permission minimale
    |
    v
Bucket ou API nécessaire
```

Éviter les comptes de service partagés entre des applications sans lien fonctionnel.

Éviter également les clés de comptes de service persistantes lorsque des mécanismes plus sûrs sont disponibles, comme les identités attachées aux ressources ou la fédération d'identité.

### 6.6 Vérifier l'identité active

```bash
gcloud auth list
```

Afficher le compte actif :

```bash
gcloud config get-value account
```

Les identités et les configurations peuvent varier selon le terminal utilisé. Avant une opération importante, vérifier le compte, le projet et les permissions.

## 7. Cloud Shell et commandes essentielles

### 7.1 Cloud Shell

Cloud Shell est un environnement de terminal accessible depuis la console Google Cloud.

Il permet notamment :

- d'exécuter la CLI ;
- d'interroger les ressources ;
- d'utiliser des éditeurs et des outils disponibles ;
- de lancer des scripts ;
- d'effectuer des laboratoires sans installer immédiatement tous les outils sur son poste.

Les fichiers présents dans l'environnement persistant de Cloud Shell ont un cycle de vie propre. Il reste prudent de conserver le code important dans un dépôt versionné.

### 7.2 Commandes de base

Afficher les projets accessibles :

```bash
gcloud projects list
```

Afficher le projet courant :

```bash
gcloud config get-value project
```

Afficher les régions :

```bash
gcloud compute regions list
```

Afficher les machines virtuelles :

```bash
gcloud compute instances list
```

Afficher les réseaux :

```bash
gcloud compute networks list
```

Afficher les buckets accessibles :

```bash
gcloud storage buckets list
```

Les résultats dépendent des permissions de l'identité active.

### 7.3 Comprendre les erreurs

**Permission denied**

L'identité ne possède pas la permission nécessaire, ou une règle organisationnelle empêche l'action.

**API not enabled**

L'API requise n'est pas activée dans le projet.

**Quota exceeded**

Une limite de consommation ou de ressources a été atteinte.

**Resource already exists**

Une ressource portant ce nom ou cet identifiant existe déjà dans le périmètre concerné.

**Invalid argument**

Un paramètre est incorrect ou incompatible avec la ressource.

Méthode de diagnostic :

1. relire le message d'erreur ;
2. vérifier le projet actif ;
3. vérifier l'identité ;
4. vérifier les permissions ;
5. vérifier l'API ;
6. vérifier la région, les paramètres et les quotas ;
7. consulter les journaux si nécessaire.

## 8. Compute Engine : machines virtuelles

### 8.1 Qu'est-ce que Compute Engine ?

Compute Engine permet de créer des machines virtuelles dans l'infrastructure Google Cloud.

Une machine virtuelle possède généralement :

- un système d'exploitation ;
- des processeurs virtuels ;
- de la mémoire ;
- un disque de démarrage ;
- des interfaces réseau ;
- des règles d'accès ;
- une identité de service éventuellement attachée.

### 8.2 Architecture d'une VM

```text
Google Cloud
    |
    +-- Projet
          |
          +-- Réseau VPC
                |
                +-- Sous-réseau
                      |
                      +-- Interface réseau de la VM
                              |
                              +-- Système d'exploitation
                              +-- Application
                              +-- Disque de démarrage
```

Le réseau, les autorisations IAM et les règles de pare-feu doivent être configurés de manière cohérente.

### 8.3 Créer une machine virtuelle de laboratoire

Avant de commencer :

- sélectionner un projet approprié ;
- vérifier que la facturation est configurée si nécessaire ;
- activer l'API Compute Engine si nécessaire ;
- choisir une région et une zone disponibles ;
- sélectionner un type de machine adapté ;
- examiner les règles de sécurité.

Exemple de création d'une petite VM Linux :

```bash
gcloud compute instances create vm-gcp-lab \
  --zone=ZONE \
  --machine-type=e2-micro \
  --image-family=debian-12 \
  --image-project=debian-cloud
```

Remplacer `ZONE` par une zone disponible.

Cette commande peut être soumise aux quotas, à la disponibilité régionale et aux politiques de l'organisation. Le coût doit être vérifié avant l'exécution.

### 8.4 Lister les VM

```bash
gcloud compute instances list
```

Afficher les détails :

```bash
gcloud compute instances describe vm-gcp-lab \
  --zone=ZONE
```

### 8.5 Se connecter à une VM

Lorsque les permissions et les conditions de connexion sont satisfaites :

```bash
gcloud compute ssh vm-gcp-lab \
  --zone=ZONE
```

La commande peut utiliser les mécanismes d'authentification SSH pris en charge par Google Cloud. L'accès peut aussi être soumis à OS Login et aux politiques de sécurité de l'organisation.

Ne pas ouvrir SSH à Internet sans justification.

### 8.6 Arrêter une VM

```bash
gcloud compute instances stop vm-gcp-lab \
  --zone=ZONE
```

Redémarrer :

```bash
gcloud compute instances start vm-gcp-lab \
  --zone=ZONE
```

L'arrêt de la VM réduit généralement certains coûts de calcul, mais les disques, les adresses IP réservées et d'autres ressources peuvent continuer à être facturés.

### 8.7 Supprimer une VM

```bash
gcloud compute instances delete vm-gcp-lab \
  --zone=ZONE
```

Lire la confirmation avant de poursuivre.

La suppression de la VM peut aussi entraîner la suppression de certains disques associés selon leurs propriétés et les options utilisées. Vérifier les ressources conservées avant et après l'opération.

## 9. Cloud Storage

### 9.1 Comprendre le stockage objet

Cloud Storage permet de stocker des objets dans des buckets.

Un objet peut être un document, une image, une archive, un fichier de sauvegarde ou un artefact applicatif.

```text
Projet Google Cloud
    |
    +-- Bucket
          |
          +-- objet-1.txt
          +-- image.png
          +-- archive.tar.gz
          +-- sauvegarde.db
```

Un bucket n'est pas un système de fichiers POSIX classique. Les outils peuvent présenter une structure de chemins, mais le modèle fondamental reste celui du stockage objet.

### 9.2 Créer un bucket

Choisir un nom globalement unique et une région adaptée.

```bash
gcloud storage buckets create gs://BUCKET_NAME \
  --location=REGION \
  --uniform-bucket-level-access
```

Remplacer :

- `BUCKET_NAME` par un nom disponible ;
- `REGION` par une région prise en charge.

Le bucket doit respecter les règles de nommage et les politiques de l'organisation.

L'accès uniforme au niveau du bucket permet de gérer les autorisations avec IAM plutôt que de s'appuyer sur des listes de contrôle d'accès individuelles aux objets.

### 9.3 Envoyer un fichier

```bash
gcloud storage cp fichier.txt gs://BUCKET_NAME/
```

Lister les objets :

```bash
gcloud storage ls gs://BUCKET_NAME/
```

Télécharger un objet :

```bash
gcloud storage cp gs://BUCKET_NAME/fichier.txt .
```

### 9.4 Sécuriser un bucket

Bonnes pratiques :

- éviter l'accès public sans justification ;
- attribuer les permissions au niveau nécessaire ;
- utiliser des identités dédiées ;
- activer les mécanismes de protection des données adaptés ;
- examiner les besoins de rétention ;
- contrôler les accès et les journaux ;
- protéger les données sensibles ;
- tester les procédures de récupération.

La suppression d'un projet peut affecter les ressources qu'il contient. Les données importantes doivent être protégées contre les suppressions accidentelles ou malveillantes par une stratégie appropriée.

### 9.5 Supprimer un bucket de laboratoire

Vérifier d'abord son contenu :

```bash
gcloud storage ls gs://BUCKET_NAME/
```

Puis, uniquement si le bucket ne contient aucune donnée à conserver :

```bash
gcloud storage rm --recursive gs://BUCKET_NAME/**
```

Cette opération est destructive. Vérifier soigneusement le nom du bucket avant l'exécution. Les mécanismes de rétention, de versionnage ou de protection peuvent modifier le résultat.

## 10. Réseaux VPC

### 10.1 Qu'est-ce qu'un VPC ?

Un VPC est un réseau virtuel permettant de connecter et de contrôler les communications entre les ressources Google Cloud.

Il fournit notamment :

- des sous-réseaux ;
- des routes ;
- des règles de pare-feu ;
- une connectivité interne ;
- des mécanismes de connexion à d'autres réseaux.

Les VPC Google Cloud sont des ressources globales, tandis que les sous-réseaux sont régionaux.

### 10.2 Architecture de base

```text
Projet Google Cloud
    |
    +-- VPC : vpc-lab
          |
          +-- Sous-réseau régional
          |      |
          |      +-- VM Web
          |      +-- VM Administration
          |
          +-- Routes
          |
          +-- Règles de pare-feu
```

Une VM doit disposer d'une configuration réseau adaptée pour communiquer avec ses destinations.

### 10.3 Créer un VPC personnalisé

```bash
gcloud compute networks create vpc-lab \
  --subnet-mode=custom
```

Créer un sous-réseau :

```bash
gcloud compute networks subnets create subnet-lab \
  --network=vpc-lab \
  --region=REGION \
  --range=10.10.0.0/24
```

Remplacer `REGION` par une région disponible.

### 10.4 Vérifier les réseaux

```bash
gcloud compute networks list
```

Afficher les sous-réseaux :

```bash
gcloud compute networks subnets list
```

Inspecter un réseau :

```bash
gcloud compute networks describe vpc-lab
```

### 10.5 Pare-feu réseau

Les règles de pare-feu VPC déterminent les communications autorisées ou refusées selon les règles applicables.

Une règle doit être définie en tenant compte :

- de la direction du trafic ;
- des sources ou destinations ;
- des protocoles et ports ;
- des cibles ;
- de la priorité ;
- des autres règles applicables.

Ne pas ouvrir tous les ports à toutes les sources pour résoudre un problème de connexion.

### 10.6 Exemple de règle SSH

Pour permettre SSH, une règle peut être conçue pour une source administrative restreinte.

Exemple illustratif :

```bash
gcloud compute firewall-rules create allow-ssh-admin \
  --network=vpc-lab \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=ADMIN_CIDR \
  --target-tags=ssh-admin
```

Remplacer `ADMIN_CIDR` par le préfixe réellement autorisé, par exemple celui d'un réseau d'administration maîtrisé.

La règle ne s'applique qu'aux cibles correspondant à la balise réseau indiquée. La source doit être choisie avec soin.

Pour un environnement de production, examiner également les mécanismes d'accès administratifs sans exposition directe, tels que les solutions de bastion et les accès SSH pris en charge par Google Cloud.

### 10.7 IP publique et IP privée

Une adresse IP privée permet la communication dans des réseaux autorisés sans constituer à elle seule un accès public direct.

Une adresse IP externe permet une connectivité externe selon le routage et les règles de sécurité.

```text
Internet
    |
    v
Adresse IP externe
    |
    v
VM
    |
    +-- Adresse IP interne
    |
    +-- Réseau VPC
```

Une adresse IP externe ne signifie pas que tous les ports sont accessibles. Le routage, les règles de pare-feu et les contrôles d'accès restent déterminants.

## 11. Services applicatifs et bases de données

### 11.1 Cloud Run

Cloud Run permet de déployer des applications conteneurisées sur une plateforme managée.

L'utilisateur fournit une image de conteneur compatible et configure le service. Google Cloud gère une grande partie de l'infrastructure d'exécution.

Cas d'usage :

- API ;
- services web ;
- traitements déclenchés par des événements ;
- applications HTTP ;
- tâches compatibles avec les modes d'exécution disponibles.

### 11.2 Google Kubernetes Engine

GKE fournit un environnement Kubernetes managé.

Il convient notamment lorsque l'application a besoin :

- d'orchestration de conteneurs ;
- de déploiements Kubernetes ;
- de mécanismes avancés de planification ;
- d'une gestion fine des charges de travail distribuées.

Kubernetes apporte des capacités puissantes, mais augmente les besoins de conception, de sécurité et d'exploitation.

### 11.3 Cloud SQL

Cloud SQL est un service de bases de données relationnelles managées prenant en charge les moteurs disponibles dans son offre.

Il permet de réduire la charge d'administration de certains composants de base de données.

Il reste nécessaire de concevoir :

- les autorisations ;
- les connexions ;
- la sauvegarde ;
- les performances ;
- la disponibilité ;
- les mises à jour ;
- la sécurité des données.

### 11.4 BigQuery

BigQuery est une plateforme d'analyse de données permettant d'exécuter des requêtes analytiques sur de grands volumes.

Il est destiné à l'analyse et aux traitements de données. Il ne remplace pas systématiquement une base relationnelle transactionnelle.

## 12. Sécurité de base

### 12.1 Modèle de responsabilité partagée

Le fournisseur et le client ont des responsabilités distinctes.

Google Cloud prend en charge l'infrastructure physique et une partie des couches de plateforme. Le client demeure responsable, selon les services choisis, de ses identités, de ses données, de ses configurations, de ses applications et des autorisations.

```text
Sécurité du cloud
    |
    +-- Infrastructure physique
    +-- Datacenters
    +-- Couches gérées par le fournisseur

Sécurité dans le cloud
    |
    +-- Identités
    +-- Permissions
    +-- Réseaux
    +-- Données
    +-- Applications
    +-- Configurations
```

La répartition précise dépend du service et du modèle de responsabilité correspondant.

### 12.2 Principes essentiels

- Activer uniquement les API nécessaires.
- Éviter les rôles trop larges.
- Utiliser des comptes de service dédiés.
- Éviter les clés persistantes inutiles.
- Protéger les secrets.
- Limiter les accès réseau.
- Surveiller les opérations sensibles.
- Sauvegarder les données importantes.
- Appliquer les mises à jour.
- Vérifier les coûts et les ressources oubliées.

### 12.3 Gestion des secrets

Les secrets comprennent les mots de passe, clés privées, jetons et autres informations d'authentification sensibles.

Ils ne doivent pas être écrits en clair dans le code source ou un dépôt Git.

Secret Manager fournit un service destiné à stocker et gérer des secrets. L'application doit recevoir uniquement les permissions nécessaires pour accéder à ses propres secrets.

## 13. Supervision et dépannage

### 13.1 Cloud Logging

Cloud Logging permet de collecter, consulter et analyser des journaux.

Les journaux peuvent provenir des applications, des services Google Cloud et des opérations d'administration.

### 13.2 Cloud Monitoring

Cloud Monitoring permet de consulter des métriques, de créer des tableaux de bord et de configurer des alertes.

Les indicateurs utiles peuvent comprendre :

- utilisation du processeur ;
- mémoire lorsqu'elle est disponible via la collecte appropriée ;
- taux d'erreur ;
- latence ;
- nombre de requêtes ;
- disponibilité ;
- capacité consommée.

### 13.3 Diagnostiquer une VM inaccessible

```text
La VM ne répond pas
       |
       v
Vérifier l'état de la VM
       |
       v
Vérifier l'adresse IP
       |
       v
Vérifier le routage
       |
       v
Vérifier les règles de pare-feu
       |
       v
Vérifier le service et le système
       |
       v
Consulter les journaux
```

Ne pas modifier simultanément toutes les règles réseau. Isoler une hypothèse, la tester et documenter le résultat.

### 13.4 Diagnostiquer un problème IAM

1. Vérifier l'identité active.
2. Vérifier le projet ciblé.
3. Lire le message d'erreur.
4. Identifier la permission requise.
5. Examiner les rôles et leur périmètre.
6. Vérifier les politiques d'organisation.
7. Attribuer uniquement l'autorisation nécessaire.
8. Tester à nouveau.

## 14. Travaux pratiques guidés

### TP 1 — Préparer un projet

**Objectif :** configurer un environnement GCP de laboratoire.

Étapes :

1. Créer ou sélectionner un projet.
2. Vérifier son identifiant.
3. Configurer `gcloud`.
4. Vérifier l'identité active.
5. Examiner la facturation.
6. Consulter les régions et zones.
7. Documenter les paramètres.

Commandes :

```bash
gcloud config list
gcloud auth list
gcloud projects describe PROJECT_ID
gcloud compute regions list
```

Résultat attendu : l'apprenant peut identifier sans ambiguïté son projet et son identité active.

### TP 2 — Déployer une VM

**Objectif :** créer, inspecter, arrêter et supprimer une machine virtuelle.

Étapes :

1. Vérifier le projet.
2. Vérifier l'API Compute Engine et les quotas.
3. Créer une petite VM.
4. Consulter ses détails.
5. Se connecter si les permissions le permettent.
6. Arrêter la VM.
7. Supprimer la VM si elle n'est plus nécessaire.
8. Contrôler les ressources restantes.

Résultat attendu : l'apprenant comprend le cycle de vie d'une VM et les conséquences financières possibles.

### TP 3 — Créer un bucket

**Objectif :** manipuler des objets Cloud Storage.

Étapes :

1. Choisir un nom de bucket unique.
2. Créer le bucket dans une région appropriée.
3. Activer l'accès uniforme.
4. Envoyer un fichier de test.
5. Lister les objets.
6. Télécharger le fichier.
7. Supprimer uniquement les objets de laboratoire.
8. Supprimer le bucket si aucune donnée n'est à conserver.

Résultat attendu : l'apprenant sait transférer des fichiers et comprend que le contrôle d'accès doit être explicite.

### TP 4 — Créer un VPC personnalisé

**Objectif :** comprendre les réseaux et sous-réseaux.

Étapes :

1. Créer un réseau VPC personnalisé.
2. Créer un sous-réseau.
3. Examiner le réseau.
4. Examiner le sous-réseau.
5. Comprendre le rôle des règles de pare-feu.
6. Documenter les plages d'adresses.
7. Supprimer les ressources du laboratoire après vérification.

Résultat attendu : l'apprenant peut expliquer la relation entre VPC, sous-réseau, VM et pare-feu.

## 15. Exercices corrigés

### Exercice 1 — Projet et ressources

**Question :** pourquoi utiliser plusieurs projets plutôt qu'un seul projet contenant toutes les ressources ?

**Correction :** plusieurs projets peuvent séparer les environnements, les autorisations, les API, les ressources et les coûts. La séparation doit correspondre aux besoins de sécurité et d'exploitation, et non à une règle arbitraire.

### Exercice 2 — Permissions

**Question :** un technicien doit uniquement consulter les journaux. Faut-il lui donner le rôle Owner ?

**Correction :** non. Il faut sélectionner un rôle de consultation adapté au besoin et au périmètre. Owner accorde des privilèges beaucoup trop larges pour ce cas.

### Exercice 3 — Machine virtuelle

**Question :** une VM arrêtée ne génère-t-elle plus aucun coût ?

**Correction :** pas nécessairement. Les disques persistants, certaines adresses IP réservées et d'autres ressources peuvent rester facturables.

### Exercice 4 — Réseau

**Question :** une VM possède une adresse IP externe. Est-elle automatiquement accessible sur tous ses ports ?

**Correction :** non. Le routage, les règles de pare-feu, le service à l'écoute et les autres contrôles déterminent l'accessibilité.

### Exercice 5 — Stockage

**Question :** pourquoi éviter de rendre public un bucket qui contient des fichiers de travail ?

**Correction :** un accès public peut exposer les données à des utilisateurs non autorisés. Il faut limiter les permissions, vérifier la configuration et protéger les contenus sensibles.

### Exercice 6 — Facturation

**Question :** une alerte de budget garantit-elle que la dépense ne dépassera pas le montant fixé ?

**Correction :** non. Les alertes signalent une consommation selon les paramètres du budget et les données de facturation disponibles. Elles ne constituent pas un mécanisme général de plafonnement strict.

## 16. Projet final corrigé — Déployer une petite infrastructure GCP

### 16.1 Scénario

Une petite entreprise veut disposer d'un environnement de laboratoire comprenant :

- un projet dédié ;
- un réseau VPC personnalisé ;
- un sous-réseau ;
- une VM Linux ;
- un bucket privé ;
- une stratégie de contrôle des accès ;
- une supervision de base ;
- une procédure de nettoyage.

### 16.2 Architecture cible

```text
Google Cloud
    |
    +-- Projet : projet-lab
          |
          +-- Réseau : vpc-lab
          |      |
          |      +-- Sous-réseau : subnet-lab
          |             |
          |             +-- VM Linux
          |
          +-- Cloud Storage
          |      |
          |      +-- Bucket privé
          |
          +-- IAM
          |      |
          |      +-- Identités et rôles limités
          |
          +-- Observabilité
                 |
                 +-- Journaux
                 +-- Métriques
```

### 16.3 Ordre de réalisation

1. Créer le projet et vérifier la facturation.
2. Configurer l'identité et la CLI.
3. Activer les API nécessaires.
4. Créer le réseau.
5. Créer le sous-réseau.
6. Créer la VM.
7. Créer le bucket.
8. Vérifier les autorisations.
9. Examiner les journaux disponibles.
10. Documenter les coûts et les ressources.
11. Nettoyer les ressources de laboratoire.

### 16.4 Exemple de commandes réseau et calcul

Les commandes suivantes illustrent le déploiement. Elles nécessitent un projet correctement configuré et des permissions suffisantes.

```bash
gcloud compute networks create vpc-lab \
  --subnet-mode=custom

gcloud compute networks subnets create subnet-lab \
  --network=vpc-lab \
  --region=REGION \
  --range=10.20.0.0/24

gcloud compute instances create vm-gcp-lab \
  --zone=ZONE \
  --machine-type=e2-micro \
  --subnet=subnet-lab \
  --image-family=debian-12 \
  --image-project=debian-cloud
```

`REGION` et `ZONE` doivent être choisis de manière cohérente : la zone de la VM doit appartenir à la région du sous-réseau.

Cette architecture est volontairement minimale. Les règles de pare-feu, les permissions d'administration, les besoins de connectivité et la supervision doivent être complétés selon le scénario réel.

### 16.5 Exemple de création du bucket

```bash
gcloud storage buckets create gs://BUCKET_NAME \
  --location=REGION \
  --uniform-bucket-level-access
```

Choisir un nom unique et vérifier la configuration d'accès avant d'y placer des données.

### 16.6 Validation finale

Le projet est considéré comme réussi lorsque :

- le projet actif est identifié ;
- le VPC et le sous-réseau existent ;
- la VM est correctement créée ;
- le bucket est privé ;
- les autorisations sont justifiées ;
- les ressources peuvent être inspectées ;
- les coûts potentiels sont compris ;
- le nettoyage est documenté.

### 16.7 Nettoyage

Supprimer la VM après avoir vérifié son nom et sa zone :

```bash
gcloud compute instances delete vm-gcp-lab \
  --zone=ZONE
```

Examiner le bucket avant de le supprimer. Supprimer uniquement les données de laboratoire, puis supprimer le bucket si cela est approprié.

La suppression d'un réseau nécessite de traiter les ressources dépendantes. Avant de supprimer le VPC, vérifier les VM, sous-réseaux et autres composants associés.

Ne jamais supprimer un projet ou une ressource sans confirmer son périmètre et les conséquences de l'opération.

## 17. Glossaire

- **API :** interface permettant à un logiciel d'interagir avec un service.
- **Bucket :** conteneur de stockage objet dans Cloud Storage.
- **Cloud Shell :** terminal accessible depuis la console Google Cloud.
- **Compute Engine :** service de machines virtuelles.
- **IAM :** gestion des identités et des autorisations.
- **Instance :** ressource de calcul, notamment une VM.
- **Projet :** périmètre de gestion fondamental des ressources Google Cloud.
- **Région :** zone géographique hébergeant des ressources cloud.
- **Service account :** identité utilisée par une application ou un processus.
- **Sous-réseau :** plage d'adresses associée à un réseau virtuel dans une région.
- **VPC :** réseau virtuel Google Cloud.
- **Zone :** domaine de déploiement au sein d'une région.

## 18. Documentation officielle

- Premiers pas avec Google Cloud : https://cloud.google.com/docs/get-started?hl=fr
- Documentation générale : https://cloud.google.com/docs
- Google Cloud CLI : https://cloud.google.com/sdk/docs
- Projets : https://cloud.google.com/resource-manager/docs/creating-managing-projects
- IAM : https://cloud.google.com/iam/docs/overview
- Compute Engine : https://cloud.google.com/compute/docs
- Cloud Storage : https://cloud.google.com/storage/docs
- Réseau VPC : https://cloud.google.com/vpc/docs/overview
- Cloud Run : https://cloud.google.com/run/docs
- Google Kubernetes Engine : https://cloud.google.com/kubernetes-engine/docs
- Cloud SQL : https://cloud.google.com/sql/docs
- Cloud Logging : https://cloud.google.com/logging/docs
- Cloud Monitoring : https://cloud.google.com/monitoring/docs
- Bonnes pratiques d'architecture : https://cloud.google.com/architecture/framework

## 19. Checklist de validation du niveau débutant

- [ ] Expliquer les différences entre IaaS, PaaS et SaaS.
- [ ] Identifier les principaux services Google Cloud.
- [ ] Comprendre la hiérarchie des ressources.
- [ ] Configurer un projet et vérifier son contexte.
- [ ] Comprendre la facturation et les alertes de budget.
- [ ] Utiliser Cloud Shell et `gcloud`.
- [ ] Expliquer les principes fondamentaux d'IAM.
- [ ] Créer et administrer une VM de laboratoire.
- [ ] Créer et utiliser un bucket.
- [ ] Comprendre VPC, sous-réseaux et règles de pare-feu.
- [ ] Appliquer le moindre privilège.
- [ ] Consulter les journaux et diagnostiquer une erreur.
- [ ] Nettoyer les ressources inutilisées.

**Fin du cours GCP — niveau débutant.**

Le niveau intermédiaire réutilisera ces fondations pour concevoir une plateforme plus complète : segmentation réseau, connectivité, services managés, automatisation Terraform, CI/CD, observabilité et sécurité opérationnelle.
