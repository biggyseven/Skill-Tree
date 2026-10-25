# AWS : les bases du cloud computing

## Présentation du cours

Ce cours constitue le premier niveau du parcours AWS. Il permet de comprendre le fonctionnement du cloud Amazon Web Services, de manipuler les services fondamentaux et de déployer une première infrastructure simple.

Les notions étudiées ici seront réutilisées au niveau intermédiaire pour construire des infrastructures réseau, automatiser des déploiements et intégrer AWS dans des pipelines CI/CD. Le niveau expert exploitera ensuite ces bases pour concevoir des architectures sécurisées, multi-comptes, résilientes et optimisées.

### Objectifs pédagogiques

À la fin de ce cours, il faudra être capable de :

- Expliquer le fonctionnement du cloud computing.
- Comprendre les régions, les zones de disponibilité et les services AWS.
- Distinguer les machines virtuelles, le stockage objet, les réseaux et les bases de données.
- Comprendre les principes d'IAM et des permissions.
- Utiliser AWS Management Console et AWS CLI.
- Créer et examiner des ressources simples.
- Comprendre la facturation et éviter les dépenses accidentelles.
- Décrire une architecture web élémentaire sur AWS.
- Identifier les premières erreurs de sécurité et d'exploitation.

### Prérequis

- Connaissances élémentaires en informatique et en réseau.
- Notions d'adressage IP, de DNS et de HTTP.
- Savoir utiliser un terminal.
- Connaissances de base de Linux utiles, mais non obligatoires.

Les notions Docker, Git, CI/CD, Terraform et Kubernetes seront mobilisées progressivement dans les niveaux suivants.

## 1. Comprendre le cloud computing

### 1.1. Définition

Le cloud computing consiste à utiliser des ressources informatiques fournies à la demande par un prestataire, au lieu de devoir acquérir et exploiter soi-même tous les équipements physiques.

Ces ressources peuvent être :

- des machines virtuelles ;
- des réseaux ;
- des disques ;
- des bases de données ;
- des espaces de stockage ;
- des services de sécurité ;
- des plateformes d'exécution applicative ;
- des outils d'analyse, de supervision et d'automatisation.

AWS signifie Amazon Web Services. Il s'agit d'une plateforme proposant de nombreux services cloud.

### 1.2. Infrastructure traditionnelle et cloud

Infrastructure traditionnelle :

```text
Entreprise
   |
   +-- Salle serveur
   |     |
   |     +-- Serveurs physiques
   |     +-- Commutateurs et routeurs
   |     +-- Baie de stockage
   |     +-- Onduleurs et climatisation
   |
   +-- Équipe d'exploitation
   |
   +-- Maintenance et renouvellement matériel
```

Infrastructure cloud :

```text
Administrateur / Développeur
          |
          v
AWS Management Console / AWS CLI / API
          |
          v
Services AWS
   |
   +-- Calcul
   +-- Réseau
   +-- Stockage
   +-- Bases de données
   +-- Sécurité
   +-- Supervision
```

Dans le cloud, une grande partie de l'infrastructure physique est gérée par le fournisseur. L'entreprise reste cependant responsable de la configuration et de l'utilisation sécurisée des ressources qui lui sont confiées.

### 1.3. Les modèles de service

**IaaS — Infrastructure as a Service**

Le fournisseur fournit des ressources d'infrastructure. Le client conserve une responsabilité importante sur le système d'exploitation et les logiciels installés.

Exemple AWS : Amazon EC2.

**PaaS — Platform as a Service**

Le fournisseur gère davantage de composants de la plateforme d'exécution. Le client se concentre principalement sur l'application et sa configuration.

Exemple de service AWS : AWS Elastic Beanstalk.

**SaaS — Software as a Service**

L'utilisateur consomme une application prête à l'emploi sans administrer directement son infrastructure sous-jacente.

Le modèle SaaS est un modèle de fourniture logicielle, pas simplement un synonyme d'application hébergée sur une machine virtuelle.

### 1.4. Les modèles de déploiement

- Cloud public : ressources fournies par un prestataire cloud.
- Cloud privé : infrastructure réservée à une organisation.
- Cloud hybride : combinaison de ressources privées et publiques.
- Multi-cloud : utilisation de plusieurs fournisseurs cloud.

Ces modèles répondent à des contraintes différentes : coût, conformité, latence, compétences, disponibilité et dépendance à un fournisseur.

## 2. Découvrir AWS

### 2.1. AWS Management Console

La console AWS est l'interface web permettant de consulter et de gérer les services.

Elle est utile pour :
- découvrir les ressources ;
- vérifier les configurations ;
- examiner les journaux ;
- apprendre le fonctionnement des services ;
- effectuer des opérations ponctuelles.

Elle ne remplace pas nécessairement l'automatisation. Pour des déploiements reproductibles, les équipes utilisent notamment AWS CLI, CloudFormation, Terraform et les pipelines CI/CD.

### 2.2. Les principales catégories

| Catégorie | Services | Utilité |
|---|---|---|
| Calcul | EC2, Lambda, ECS, EKS | Exécuter des applications |
| Réseau | VPC, Route 53, ELB | Connectivité et distribution du trafic |
| Stockage | S3, EBS, EFS | Conserver fichiers et données |
| Bases de données | RDS, DynamoDB | Persister les données applicatives |
| Identité | IAM, IAM Identity Center | Gérer les identités et permissions |
| Sécurité | KMS, CloudTrail, GuardDuty | Chiffrement, audit et détection |
| Supervision | CloudWatch | Mesures, journaux et alertes |
| Automatisation | CloudFormation | Décrire et déployer l'infrastructure |
| Gouvernance | AWS Organizations | Organiser plusieurs comptes AWS |

La liste est volontairement introductive. Les services seront approfondis aux niveaux suivants.

## 3. Régions et zones de disponibilité

### 3.1. Région AWS

Une région est une zone géographique dans laquelle AWS met à disposition des services.

Une application doit être déployée dans une région compatible avec ses contraintes :
- latence des utilisateurs ;
- exigences de résidence des données ;
- disponibilité des services ;
- coûts ;
- exigences réglementaires ;
- stratégie de reprise après sinistre.

Exemples de régions AWS :
- `eu-west-1` : Irlande ;
- `eu-central-1` : Francfort ;
- `us-east-1` : Virginie du Nord.

La disponibilité d'un service et de certaines de ses fonctionnalités dépend de la région.

### 3.2. Zone de disponibilité

Une zone de disponibilité, ou Availability Zone (AZ), est un ensemble de ressources de centres de données isolé des autres zones de la même région.

```text
Région AWS
|
+-- AZ-a
|    +-- Calcul
|    +-- Stockage
|
+-- AZ-b
|    +-- Calcul
|    +-- Stockage
|
+-- AZ-c
     +-- Calcul
     +-- Stockage
```

L'utilisation de plusieurs zones peut réduire le risque qu'une panne localisée interrompe toute l'application.

Attention : créer des ressources dans plusieurs zones ne garantit pas automatiquement la haute disponibilité. Il faut également prévoir le routage, la réplication des données, la capacité, les mécanismes de bascule et les tests de panne.

### 3.3. Résilience régionale

Une architecture multi-AZ protège contre certaines défaillances localisées dans une région.

Une architecture multi-région peut protéger contre des incidents régionaux, mais elle implique davantage de complexité et de coûts.

La stratégie doit être proportionnée aux besoins réels de disponibilité et de reprise.

## 4. Comprendre les comptes AWS

Un compte AWS constitue une frontière importante de gestion, d'accès et de facturation.

Il possède notamment :
- un identifiant de compte ;
- des identités et des rôles ;
- des ressources ;
- des quotas ;
- des paramètres de sécurité ;
- une activité de facturation.

Pour débuter, un compte de laboratoire dédié est préférable à un compte contenant des systèmes de production.

### 4.1. Protéger le compte

Mesures de base :

1. Activer l'authentification multifacteur (MFA).
2. Protéger l'identité root.
3. Ne pas utiliser root pour les tâches quotidiennes.
4. Créer des identités ou rôles adaptés aux tâches.
5. Éviter les permissions administratives permanentes.
6. Configurer les alertes de coûts.
7. Ne jamais publier les clés d'accès.
8. Supprimer les ressources de laboratoire inutilisées.

L'identité root possède des privilèges particuliers. Elle doit être protégée et utilisée uniquement lorsque cela est nécessaire.

## 5. IAM : identités et permissions

IAM signifie Identity and Access Management.

IAM détermine quelles identités peuvent effectuer quelles actions sur quelles ressources, éventuellement sous certaines conditions.

### 5.1. Les concepts essentiels

**Utilisateur IAM**

Identité AWS traditionnelle associée à des permissions. Les utilisateurs IAM ne sont pas la méthode à privilégier systématiquement pour les personnes : les accès fédérés et les rôles temporaires sont généralement préférables.

**Groupe IAM**

Ensemble d'utilisateurs IAM auxquels on peut associer des politiques communes.

**Rôle IAM**

Identité assumable par un utilisateur, un service ou une autre entité autorisée. Un rôle fournit des permissions temporaires.

**Politique IAM**

Document JSON décrivant des autorisations ou restrictions.

### 5.2. Exemple de politique IAM

Voici une politique d'illustration permettant de lire des objets dans un préfixe déterminé d'un bucket S3.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::exemple-bucket/laboratoire/*"
    }
  ]
}
```

Cette politique ne permet pas de lister le contenu du bucket, de supprimer des objets ou d'administrer le compte.

Les autorisations doivent être adaptées aux ressources réelles. Une politique d'illustration ne doit pas être copiée sans vérification dans un environnement de production.

### 5.3. Refuser par défaut

Les principes fondamentaux sont :

- accès refusé par défaut ;
- autorisations explicites et minimales ;
- permissions limitées à la tâche ;
- utilisation de rôles temporaires quand cela est possible ;
- révision régulière des droits.

Une politique autorisant une action ne suffit pas toujours à garantir l'accès : d'autres politiques, restrictions et conditions peuvent intervenir.

## 6. AWS CLI : piloter AWS en ligne de commande

AWS CLI est l'interface en ligne de commande d'AWS.

Elle permet d'exécuter des opérations scriptées, d'inspecter les ressources et de construire des automatisations.

### 6.1. Vérifier l'installation

```bash
aws --version
```

Une sortie typique contient le numéro de version de la CLI.

### 6.2. Configurer l'accès

Pour une session de laboratoire, utiliser de préférence un mécanisme d'authentification fédérée ou un profil utilisant des identifiants temporaires.

Avec AWS IAM Identity Center, un exemple de configuration est :

```bash
aws configure sso
aws sso login --profile laboratoire
```

Puis :

```bash
aws sts get-caller-identity --profile laboratoire
```

Cette commande permet de vérifier l'identité utilisée.

Exemple de résultat :

```json
{
  "UserId": "EXEMPLE",
  "Account": "123456789012",
  "Arn": "arn:aws:sts::123456789012:assumed-role/RoleLaboratoire/session"
}
```

Les valeurs sont illustratives.

Ne jamais mettre de véritables clés AWS dans un dépôt Git, dans un Dockerfile, dans une image de conteneur ou dans un fichier de cours public.

### 6.3. Vérifier la région

```bash
aws configure list --profile laboratoire
```

Une région peut être spécifiée explicitement :

```bash
aws sts get-caller-identity \
  --profile laboratoire \
  --region eu-west-1
```

Toutes les commandes ne dépendent pas de la région de la même manière. Il faut comprendre si une ressource est régionale ou globale.

## 7. EC2 : les machines virtuelles

Amazon EC2 fournit des instances de calcul configurables.

Une instance possède notamment :
- un type d'instance ;
- une image système (AMI) ;
- des interfaces réseau ;
- un ou plusieurs volumes ;
- un rôle IAM éventuel ;
- des règles de sécurité réseau.

### 7.1. Comprendre le cycle de vie

```text
Choisir une AMI
      |
      v
Choisir un type d'instance
      |
      v
Configurer réseau et permissions
      |
      v
Lancer l'instance
      |
      v
Vérifier son état et sa connectivité
      |
      v
Administrer et superviser
      |
      v
Arrêter ou supprimer selon le besoin
```

Arrêter une instance et la supprimer sont deux opérations différentes.

Selon le type de ressource, l'arrêt ne met pas fin à tous les frais. Les volumes, adresses IP et autres ressources associées peuvent continuer à être facturés.

### 7.2. Accès réseau

Une instance n'est pas nécessairement accessible depuis Internet.

Il faut notamment examiner :
- les règles du groupe de sécurité ;
- les routes du sous-réseau ;
- la présence d'une adresse IP publique si nécessaire ;
- les Network ACL ;
- le pare-feu local ;
- les mécanismes d'administration.

Ne pas ouvrir SSH ou RDP à l'ensemble d'Internet sans justification.

Préférer, lorsque cela convient, AWS Systems Manager Session Manager pour administrer des instances sans exposer directement un port SSH public.

### 7.3. Rôle IAM pour EC2

Une application qui s'exécute sur EC2 peut obtenir des permissions par l'intermédiaire d'un rôle IAM associé à l'instance.

```text
Application sur EC2
       |
       v
Rôle IAM de l'instance
       |
       v
Identifiants temporaires
       |
       v
API AWS autorisées
```

Cela évite de stocker durablement des clés d'accès dans les fichiers de configuration de l'application.

## 8. S3 : stockage objet

Amazon S3 permet de stocker des objets dans des buckets.

Un objet comprend notamment :
- une clé ;
- un contenu ;
- des métadonnées ;
- éventuellement des versions et des propriétés de chiffrement.

### 8.1. Concepts importants

**Bucket**

Conteneur logique d'objets.

**Objet**

Donnée stockée dans un bucket.

**Clé**

Nom permettant d'identifier un objet dans un bucket.

**Versioning**

Mécanisme permettant de conserver plusieurs versions d'un objet.

**Lifecycle**

Règles de transition ou d'expiration des objets.

### 8.2. Exemple d'utilisation

Créer un bucket exige un nom disponible globalement dans l'espace de noms S3, ainsi qu'une configuration appropriée.

Les exemples ci-dessous supposent un bucket existant nommé `mon-bucket-laboratoire-unique`.

```bash
aws s3 ls
```

Lister les objets d'un bucket :

```bash
aws s3 ls s3://mon-bucket-laboratoire-unique/
```

Envoyer un fichier :

```bash
aws s3 cp rapport.txt \
  s3://mon-bucket-laboratoire-unique/laboratoire/rapport.txt
```

Télécharger un objet :

```bash
aws s3 cp \
  s3://mon-bucket-laboratoire-unique/laboratoire/rapport.txt \
  rapport-recupere.txt
```

Supprimer un objet précis :

```bash
aws s3 rm \
  s3://mon-bucket-laboratoire-unique/laboratoire/rapport.txt
```

Ces commandes ne créent pas le bucket automatiquement.

### 8.3. Sécuriser S3

Pour un stockage privé :
- activer S3 Block Public Access lorsque cela convient ;
- utiliser des politiques IAM et des politiques de bucket minimales ;
- activer le chiffrement ;
- activer le versioning si une protection contre certaines suppressions est nécessaire ;
- utiliser des règles de cycle de vie ;
- surveiller les accès sensibles.

Le versioning n'est pas une sauvegarde complète : un utilisateur autorisé peut supprimer des versions ou modifier la configuration. Une protection plus forte peut nécessiter des sauvegardes séparées et des contrôles supplémentaires.

## 9. VPC : le réseau virtuel AWS

Amazon VPC permet de définir un réseau virtuel isolé dans AWS.

Il comprend notamment :
- des plages CIDR ;
- des sous-réseaux ;
- des tables de routage ;
- des groupes de sécurité ;
- des Network ACL ;
- des passerelles et des points de terminaison.

### 9.1. Architecture élémentaire

```text
VPC : 10.20.0.0/16
|
+-- Sous-réseau public : 10.20.1.0/24
|      |
|      +-- Ressource accessible selon les règles
|      +-- Route vers Internet Gateway
|
+-- Sous-réseau privé : 10.20.2.0/24
       |
       +-- Ressource non directement exposée
       +-- Routage contrôlé
```

Un sous-réseau est dit public lorsqu'une route appropriée vers une passerelle Internet existe. Une adresse IP publique et des règles de sécurité adaptées restent nécessaires pour rendre une ressource joignable depuis Internet.

Un sous-réseau privé ne possède pas de route directe vers une passerelle Internet. Il peut néanmoins accéder à certains services par NAT ou par VPC endpoints, selon la configuration.

### 9.2. Groupes de sécurité

Les groupes de sécurité agissent comme des pare-feu virtuels associés aux interfaces réseau ou aux ressources compatibles.

Exemple conceptuel :

```text
Internet
   |
   | HTTPS autorisé
   v
Groupe de sécurité du frontal
   |
   | Trafic applicatif autorisé
   v
Groupe de sécurité applicatif
   |
   | Accès base de données autorisé
   v
Groupe de sécurité de la base
```

Une règle de groupe de sécurité doit être aussi restrictive que possible.

Il faut distinguer le filtrage des groupes de sécurité de celui des Network ACL, qui interviennent au niveau du sous-réseau et sont sans état.

## 10. Stockage de blocs et stockage de fichiers

AWS propose plusieurs modèles de stockage.

| Service | Modèle | Exemple d'utilisation |
|---|---|---|
| S3 | Objet | Fichiers, sauvegardes, archives |
| EBS | Bloc | Volume disque associé à une instance EC2 |
| EFS | Fichiers partagés | Système de fichiers accessible par plusieurs clients compatibles |

Le choix dépend des exigences d'accès, des performances, de la durabilité, de la disponibilité et des coûts.

Un disque EBS n'est pas un bucket S3. Un système de fichiers partagé n'a pas le même comportement qu'un stockage objet.

## 11. Bases de données

Deux catégories importantes :

**Bases relationnelles**

Amazon RDS facilite l'exploitation de moteurs relationnels compatibles, notamment PostgreSQL et MySQL.

**Bases NoSQL**

Amazon DynamoDB est une base de données clé-valeur et document conçue pour fournir des performances prévisibles à grande échelle selon la conception et la configuration choisies.

Le choix dépend :
- du modèle de données ;
- des requêtes ;
- des transactions ;
- de la cohérence ;
- des performances attendues ;
- des exigences d'exploitation ;
- des coûts.

Il ne faut pas choisir une base de données uniquement parce qu'elle est disponible dans le cloud.

## 12. CloudWatch : observer les ressources

Amazon CloudWatch permet de collecter et de consulter des métriques, des journaux et des alarmes.

Exemples :
- utilisation CPU d'une instance EC2 ;
- métriques d'un service AWS ;
- journaux d'une application ;
- alarmes liées à certains seuils ;
- tableaux de bord opérationnels.

### 12.1. Exemple de raisonnement opérationnel

```text
Application
    |
    v
Métriques et journaux
    |
    v
CloudWatch
    |
    +-- Tableau de bord
    |
    +-- Alarme
           |
           v
      Notification ou action
```

Une alarme ne remplace pas un processus de traitement d'incident. Il faut définir les seuils, les destinataires, les procédures et les conditions d'escalade.

## 13. AWS et le modèle de responsabilité partagée

AWS sécurise l'infrastructure du cloud, notamment une partie des installations physiques et de la plateforme sous-jacente.

Le client reste responsable de nombreux éléments dans le cloud, selon le service utilisé :
- les permissions ;
- les données ;
- les règles réseau ;
- la configuration des ressources ;
- les secrets ;
- le système d'exploitation lorsque celui-ci est à sa charge ;
- les applications ;
- les sauvegardes et les procédures de restauration adaptées.

```text
Responsabilité du fournisseur
   |
   +-- Infrastructures physiques
   +-- Installations et matériel
   +-- Composants de la plateforme gérés
       selon le service

Responsabilité du client
   |
   +-- Identités et permissions
   +-- Données et classification
   +-- Configuration réseau
   +-- Application
   +-- Secrets
   +-- Contrôles et restauration
```

La répartition précise varie entre EC2, les services gérés et les services sans serveur.

## 14. Comprendre la facturation AWS

Le cloud n'est pas automatiquement gratuit.

Les coûts peuvent provenir :
- du temps d'exécution des ressources ;
- du stockage ;
- des requêtes ;
- des transferts de données ;
- des adresses IP ;
- des sauvegardes ;
- des services de journalisation ;
- des services de sécurité ;
- des ressources laissées actives.

### 14.1. Bonnes pratiques

1. Lire la tarification avant de créer une ressource.
2. Utiliser AWS Pricing Calculator pour les estimations.
3. Configurer des budgets et des alertes.
4. Vérifier les frais de transfert.
5. Identifier les volumes et snapshots inutilisés.
6. Supprimer les ressources de laboratoire.
7. Vérifier la facture et les coûts réels.
8. Ne pas confondre une alerte de budget avec un plafond bloquant.

Les programmes de gratuité AWS ont des conditions et des limites qui peuvent évoluer. Il faut vérifier l'offre applicable au compte au moment de l'utilisation.

## 15. Première architecture web sur AWS

Imaginons une application web simple.

```text
Utilisateur
    |
    v
Internet
    |
    v
Point d'entrée public
    |
    v
Serveur applicatif
    |
    v
Base de données privée
```

Cette architecture est volontairement simplifiée.

Dans un environnement de production, il faudra examiner :
- la haute disponibilité ;
- les certificats TLS ;
- les règles réseau ;
- les sauvegardes ;
- les secrets ;
- les mises à jour ;
- la supervision ;
- le dimensionnement ;
- les coûts ;
- les exigences de reprise.

Le niveau intermédiaire construira une architecture plus structurée avec un VPC, des sous-réseaux, des règles de sécurité et une infrastructure déclarative.

## 16. Travaux pratiques

### TP 1 — Vérifier l'environnement AWS

Objectifs :
- installer AWS CLI ;
- configurer un accès temporaire ;
- identifier le compte utilisé ;
- vérifier la région ;
- inspecter quelques services sans créer de ressources coûteuses.

Commandes :

```bash
aws --version
aws sts get-caller-identity --profile laboratoire
aws configure list --profile laboratoire
```

Résultats attendus :
- AWS CLI fonctionne ;
- l'identité est identifiée ;
- le compte et le profil utilisés sont connus ;
- les commandes ne nécessitent pas de clé inscrite dans le dépôt.

### TP 2 — Découvrir S3

1. Créer un bucket de laboratoire avec une configuration adaptée.
2. Conserver le bucket privé.
3. Envoyer un fichier non sensible.
4. Lister les objets.
5. Télécharger le fichier.
6. Supprimer l'objet.
7. Vérifier la configuration du bucket.
8. Supprimer le bucket seulement lorsqu'il est vide et qu'il n'est plus nécessaire.

Le nom du bucket doit être unique. Certaines configurations S3 et certains paramètres varient selon la région.

### TP 3 — Examiner une instance EC2

Dans la console :
1. Identifier une AMI.
2. Examiner les types d'instances.
3. Lire les règles du groupe de sécurité.
4. Identifier le sous-réseau.
5. Examiner les volumes associés.
6. Identifier le rôle IAM éventuel.
7. Vérifier les mécanismes d'accès.
8. Terminer l'instance de laboratoire si elle a été créée pour cet exercice.

Ne pas lancer d'instance sans avoir vérifié les coûts et les autorisations.

### TP 4 — Construire un schéma d'architecture

Produire un schéma présentant :
- un VPC ;
- un sous-réseau public ;
- un sous-réseau privé ;
- un frontal web ;
- une application ;
- une base de données ;
- les règles de flux ;
- les journaux et les sauvegardes.

Justifier les flux autorisés et les ressources qui doivent rester privées.

## 17. Dépannage

### Problème : `AccessDenied`

Causes possibles :
- permission IAM manquante ;
- politique de ressource restrictive ;
- refus explicite ;
- restriction d'organisation ;
- condition IAM non satisfaite ;
- mauvais compte ou rôle.

Démarche :
1. Vérifier l'identité active.
2. Vérifier le compte et la région.
3. Identifier l'action refusée.
4. Examiner les politiques pertinentes.
5. Demander uniquement la permission nécessaire.

### Problème : ressource introuvable

Vérifier :
- la région ;
- le nom de ressource ;
- le compte ;
- l'état de la ressource ;
- les droits de lecture ;
- le type de service concerné.

### Problème : connexion impossible à EC2

Examiner :
- l'adresse utilisée ;
- le groupe de sécurité ;
- les routes ;
- la connectivité du sous-réseau ;
- les permissions d'administration ;
- le pare-feu local ;
- l'état de l'instance.

Ne pas résoudre un problème réseau en ouvrant tous les ports à Internet.

### Problème : coûts inattendus

1. Examiner les coûts par service et région.
2. Rechercher les ressources actives.
3. Vérifier les volumes, snapshots et adresses IP.
4. Consulter les transferts de données.
5. Arrêter ou supprimer les ressources non nécessaires après vérification.

## 18. Exercices corrigés

### Exercice 1 — Choisir un service

Quel service convient le mieux pour stocker des fichiers statiques ?

**Correction :** Amazon S3 convient généralement au stockage objet. EBS répond à un besoin de stockage bloc, tandis qu'EFS fournit un système de fichiers partagé.

### Exercice 2 — Protéger une instance

Une instance EC2 n'a besoin que d'accéder à S3. Faut-il placer une clé d'accès permanente dans son code ?

**Correction :** Non. Un rôle IAM associé à l'instance permet généralement d'obtenir des identifiants temporaires. Les permissions du rôle doivent être limitées aux ressources nécessaires.

### Exercice 3 — Haute disponibilité

Deux instances sont lancées dans la même zone de disponibilité. Est-ce une architecture multi-AZ ?

**Correction :** Non. Pour une architecture multi-AZ, les ressources concernées doivent être réparties sur plusieurs zones et les mécanismes de bascule doivent être conçus et testés.

### Exercice 4 — Accès public

Une ressource est placée dans un sous-réseau public. Est-elle automatiquement accessible depuis Internet ?

**Correction :** Non. Le routage, les adresses, les groupes de sécurité, les pare-feu et les autres conditions d'accès doivent également être adaptés.

### Exercice 5 — Coût d'une instance arrêtée

L'arrêt d'une instance EC2 garantit-il l'absence de toute facturation liée à cette instance ?

**Correction :** Non. Certains coûts, comme les volumes de stockage conservés, peuvent subsister. Il faut examiner chaque ressource associée.

## 19. Projet final — Décrire et sécuriser une petite infrastructure AWS

### Objectif

Proposer une architecture pour héberger une application web de démonstration.

### Livrables

1. Un schéma d'architecture.
2. Une description des services choisis.
3. Un plan réseau.
4. Une politique d'accès conceptuelle.
5. Une stratégie de sauvegarde.
6. Un plan de supervision.
7. Une estimation de coûts.
8. Une procédure de suppression des ressources de laboratoire.

### Critères d'évaluation

- Les ressources publiques et privées sont clairement distinguées.
- Les permissions sont limitées.
- Les coûts sont pris en compte.
- Les données sont protégées.
- Les erreurs et incidents peuvent être détectés.
- Les choix d'architecture sont justifiés.

## 20. Préparation au niveau intermédiaire

Le niveau intermédiaire reprendra les connaissances de ce cours pour construire une infrastructure cohérente.

Il approfondira :
- le découpage CIDR ;
- les VPC et sous-réseaux ;
- les tables de routage ;
- les Internet Gateways et NAT Gateways ;
- les groupes de sécurité et Network ACL ;
- les VPC endpoints ;
- le stockage EBS, EFS et S3 ;
- les sauvegardes ;
- la répartition du trafic ;
- Terraform et la gestion du cycle de vie de l'infrastructure.

Il ne s'agira plus seulement de connaître les services : il faudra les assembler correctement.

## 21. Glossaire

- **AMI** : image utilisée pour lancer une instance EC2.
- **AWS CLI** : outil de ligne de commande pour AWS.
- **AZ** : zone de disponibilité.
- **Bucket** : conteneur d'objets S3.
- **EC2** : service de calcul par instances.
- **IAM** : gestion des identités et des permissions.
- **Instance** : ressource de calcul EC2.
- **MFA** : authentification multifacteur.
- **Région** : zone géographique AWS.
- **Rôle IAM** : identité assumable fournissant des permissions.
- **S3** : stockage objet.
- **VPC** : réseau virtuel AWS.

## 22. Documentation officielle

- AWS — Présentation : https://aws.amazon.com/what-is-aws/
- AWS — Documentation : https://docs.aws.amazon.com/
- AWS CLI : https://docs.aws.amazon.com/cli/latest/userguide/
- IAM : https://docs.aws.amazon.com/IAM/latest/UserGuide/
- EC2 : https://docs.aws.amazon.com/ec2/
- S3 : https://docs.aws.amazon.com/s3/
- VPC : https://docs.aws.amazon.com/vpc/
- CloudWatch : https://docs.aws.amazon.com/cloudwatch/
- AWS Pricing Calculator : https://calculator.aws/
- AWS Budgets : https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- AWS Well-Architected : https://docs.aws.amazon.com/wellarchitected/