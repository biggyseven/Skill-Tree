# Kubernetes : les bases

## 1. Objectifs du cours

Kubernetes est une plateforme d'orchestration de conteneurs. Il permet de déployer, d'organiser, de mettre à l'échelle et de surveiller des applications sur un ensemble de machines.

Ce cours constitue le premier niveau d'un parcours progressif. Il commence par les principes fondamentaux, puis conduit à la création d'un cluster local, au déploiement d'applications, à l'exposition de services et au diagnostic des incidents courants.

À la fin de ce cours, il faudra être capable de :

- Expliquer le rôle de Kubernetes et ses différences avec Docker.
- Décrire l'architecture d'un cluster Kubernetes.
- Comprendre les notions de Pod, Deployment, ReplicaSet, Service et Namespace.
- Installer ou utiliser un environnement Kubernetes local.
- Manipuler un cluster avec `kubectl`.
- Déployer une application à l'aide d'un manifeste YAML.
- Exposer une application et accéder à celle-ci.
- Mettre à l'échelle un déploiement.
- Effectuer une mise à jour et revenir à une version précédente.
- Lire les événements et les journaux pour diagnostiquer un problème.
- Appliquer les premières règles de sécurité et de bonne gestion des ressources.

### Prérequis

Une connaissance élémentaire de Linux, des lignes de commande, des adresses IP, des ports TCP et des conteneurs Docker facilitera l'apprentissage.

Il n'est pas nécessaire d'avoir déjà administré un cluster Kubernetes.

## 2. Qu'est-ce que Kubernetes ?

### 2.1 Le problème que Kubernetes résout

Imaginons une application Web composée de plusieurs conteneurs Docker.

Au départ, un administrateur peut démarrer manuellement les conteneurs, configurer leur réseau et les redémarrer lorsqu'ils tombent en panne.

Lorsque l'application grandit, cette approche devient difficile à maintenir :

- Plusieurs instances doivent fonctionner simultanément.
- Certaines instances doivent être remplacées lorsqu'elles tombent en panne.
- Le trafic doit être dirigé vers les instances disponibles.
- Une mise à jour ne doit pas nécessairement interrompre toute l'application.
- Les ressources CPU et mémoire doivent être contrôlées.
- Les applications doivent communiquer entre elles.
- Les configurations doivent être reproductibles.

Kubernetes automatise une grande partie de ces opérations.

### 2.2 Le rôle de Kubernetes

Kubernetes reçoit une description de l'état souhaité et tente continuellement de faire correspondre l'environnement réel à cette description.

Par exemple, on peut demander trois instances d'une application :

```text
ÉTAT SOUHAITÉ
Application : boutique-web
Nombre de réplicas : 3

              |
              v

+--------------------------------+
|       CONTRÔLE KUBERNETES      |
|                                |
| - Observe l'état réel           |
| - Compare les deux états        |
| - Crée les ressources manquantes|
| - Remplace les instances perdues|
+--------------------------------+
              |
              v

ÉTAT OBSERVÉ
Pod 1 : disponible
Pod 2 : disponible
Pod 3 : disponible
```

Si un Pod disparaît, Kubernetes constate que l'état réel ne correspond plus à l'état souhaité. Un contrôleur peut alors demander la création d'un nouveau Pod pour rétablir le nombre souhaité.

Il s'agit d'un mécanisme de réconciliation.

**Point essentiel :** Kubernetes ne se contente pas d'exécuter une commande une fois. Il surveille continuellement les ressources déclarées et agit pour maintenir l'état attendu.

### 2.3 Ce que Kubernetes ne fait pas automatiquement

Kubernetes n'est pas une solution magique qui rend toute application résiliente.

Il ne garantit pas, à lui seul :

- Que le code de l'application ne contient aucun défaut.
- Que les données d'une base de données sont sauvegardées.
- Qu'une application est sécurisée.
- Que tous les composants disposent de ressources suffisantes.
- Qu'un cluster à un seul nœud résistera à la panne de ce nœud.
- Qu'une mise à jour applicative est fonctionnellement correcte.
- Qu'une base de données peut être répliquée sans configuration supplémentaire.

Kubernetes fournit des mécanismes d'orchestration. Leur efficacité dépend de leur configuration et de la conception de l'application.

## 3. Docker et Kubernetes : quelles différences ?

Docker est principalement utilisé pour construire et exécuter des conteneurs. Kubernetes orchestre des applications conteneurisées sur un cluster.

| Fonction | Docker seul | Kubernetes |
|---|---|---|
| Construire une image | Oui | Généralement réalisé avec un outil externe |
| Exécuter un conteneur | Oui | Indirectement, à travers les Pods |
| Organiser plusieurs conteneurs | Oui, notamment avec Compose | Oui, au moyen des objets Kubernetes |
| Gérer plusieurs machines | Possibilités limitées selon l'outil utilisé | Fonction centrale |
| Maintenir un nombre souhaité de réplicas | Pas avec Docker seul de manière générale | Oui, avec un Deployment et ses contrôleurs |
| Découvrir les services | Réseau et DNS Docker | Services et DNS Kubernetes |
| Gérer les mises à jour progressives | Selon l'outil utilisé | Intégré aux Deployments |
| Contrôler les ressources | Oui, pour les conteneurs | Oui, avec des mécanismes au niveau des Pods et des conteneurs |

### 3.1 Schéma d'ensemble

```text
              DÉVELOPPEMENT
                    |
                    v
          +--------------------+
          |  Code applicatif   |
          +--------------------+
                    |
                    v
          +--------------------+
          |  Image de conteneur|
          |  construite par    |
          |  Docker ou BuildKit|
          +--------------------+
                    |
                    v
          +--------------------+
          | Registre d'images  |
          +--------------------+
                    |
                    v
          +--------------------------------+
          |       CLUSTER KUBERNETES       |
          |                                |
          |  +----------+  +----------+    |
          |  |   Pod    |  |   Pod    |    |
          |  |  App Web |  |  App Web |    |
          |  +----------+  +----------+    |
          |         \          /           |
          |          \        /            |
          |       +------------+            |
          |       |  Service   |            |
          |       +------------+            |
          +--------------------------------+
```

Une image est construite puis stockée dans un registre. Kubernetes utilise ensuite cette image pour créer les conteneurs nécessaires dans les Pods.

Kubernetes n'exige pas que le moteur utilisé sur les nœuds soit Docker Engine. Il s'appuie sur un environnement d'exécution compatible avec l'interface CRI, par exemple containerd ou CRI-O.

## 4. Comprendre l'architecture d'un cluster

Un cluster Kubernetes est constitué d'un plan de contrôle (*control plane*) et de nœuds qui exécutent les applications.

### 4.1 Le schéma général

```text
                     ADMINISTRATEUR
                           |
                           | kubectl
                           v
              +---------------------------+
              |       CONTROL PLANE      |
              |                           |
              |  kube-apiserver           |
              |  etcd                     |
              |  kube-scheduler           |
              |  kube-controller-manager  |
              +---------------------------+
                           |
                 Décisions et état
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
+------------------------+       +------------------------+
|       NŒUD A            |       |       NŒUD B            |
|                        |       |                        |
| kubelet                |       | kubelet                |
| Runtime de conteneurs  |       | Runtime de conteneurs  |
|                        |       |                        |
| +---------+            |       | +---------+            |
| | Pod A1  |            |       | | Pod B1  |            |
| +---------+            |       | +---------+            |
|                        |       | +---------+            |
|                        |       | | Pod B2  |            |
|                        |       | +---------+            |
+------------------------+       +------------------------+
```

Le plan de contrôle décide de la manière dont les ressources doivent être gérées. Les nœuds fournissent les ressources nécessaires à l'exécution des applications.

### 4.2 Le serveur API : `kube-apiserver`

Le serveur API est le point d'entrée principal du plan de contrôle.

Quand `kubectl` demande la création d'un Deployment, la requête passe par l'API Kubernetes.

Le serveur API valide les objets, applique les contrôles nécessaires et permet aux autres composants de consulter ou modifier l'état du cluster selon leurs responsabilités et autorisations.

Exemple :

```bash
kubectl get nodes
```

Cette commande interroge l'API pour obtenir la liste des nœuds visibles par l'utilisateur.

### 4.3 La base de données : `etcd`

`etcd` est un magasin de données distribué qui conserve l'état persistant du cluster, notamment les objets Kubernetes gérés par le plan de contrôle.

Exemples de données associées à cet état :

- Les Deployments déclarés.
- Les Pods et leurs métadonnées.
- Les Services.
- Les ConfigMaps et Secrets.
- Les informations d'état enregistrées par les contrôleurs.

Dans un environnement de production, la sauvegarde et la protection de cette base de données sont importantes.

Un utilisateur débutant ne doit généralement pas administrer `etcd` directement : l'interaction normale s'effectue à travers l'API Kubernetes.

### 4.4 Le planificateur : `kube-scheduler`

Le scheduler choisit le nœud sur lequel un Pod non encore affecté doit être exécuté.

Il tient compte, entre autres, des ressources demandées et des contraintes de placement.

```text
                 NOUVEAU POD
                      |
                      v
             +------------------+
             | KUBE-SCHEDULER   |
             +------------------+
                      |
            Analyse des contraintes
                      |
             +--------+--------+
             |                 |
             v                 v
       +-----------+     +-----------+
       |   NŒUD A  |     |   NŒUD B  |
       | Ressources|     | Ressources|
       | disponibles|    | disponibles|
       +-----------+     +-----------+
             |
             v
        NŒUD SÉLECTIONNÉ
```

Le scheduler attribue le Pod à un nœud approprié. Il ne construit pas l'image et ne remplace pas le processus de l'application.

### 4.5 Les contrôleurs : `kube-controller-manager`

Les contrôleurs observent l'état réel et tentent de le rapprocher de l'état souhaité.

Exemple : un ReplicaSet demande trois Pods, mais seulement deux existent. Son contrôleur constate l'écart et contribue à la création du troisième Pod.

Plusieurs contrôleurs assument des responsabilités différentes : gestion des nœuds, des réplicas, de certains objets de stockage et d'autres ressources.

### 4.6 Les composants d'un nœud

Le composant `kubelet` est un agent qui fonctionne sur chaque nœud Kubernetes. Il veille à ce que les Pods affectés à ce nœud soient exécutés conformément à leur spécification.

Le runtime de conteneurs est chargé de gérer les conteneurs eux-mêmes.

`kube-proxy`, lorsqu'il est utilisé, contribue à la mise en œuvre du réseau des Services. Certains environnements réseau utilisent d'autres mécanismes et n'ont donc pas nécessairement besoin de `kube-proxy`.

**À retenir :** le plan de contrôle organise le cluster, tandis que les nœuds exécutent les charges de travail.

## 5. Le vocabulaire fondamental

Avant de lancer des commandes, il est nécessaire de distinguer plusieurs objets.

### 5.1 Cluster

Un cluster est l'environnement Kubernetes dans lequel sont gérés les objets et les applications.

Il comprend un plan de contrôle et au moins un nœud de travail capable d'exécuter les charges de travail. Dans certains environnements d'apprentissage, un même nœud héberge également les composants du plan de contrôle.

### 5.2 Nœud (*Node*)

Un nœud est une machine physique ou virtuelle qui participe au cluster.

Il fournit notamment du CPU, de la mémoire, un système d'exploitation, un runtime de conteneurs et les composants nécessaires à Kubernetes.

### 5.3 Pod

Le Pod est la plus petite unité déployable dans Kubernetes.

Un Pod contient un ou plusieurs conteneurs qui partagent certains éléments, notamment le réseau et, lorsque cela est configuré, des volumes.

Chaque Pod possède sa propre identité réseau au sein du cluster. Son adresse IP peut changer lorsqu'il est remplacé.

```text
+----------------------------------+
|               POD                |
|                                  |
|  Adresse IP du Pod : 10.x.x.x    |
|                                  |
|  +----------------------------+  |
|  | Conteneur : application    |  |
|  +----------------------------+  |
|                                  |
|  Volumes éventuellement partagés |
+----------------------------------+
```

Dans une architecture simple, un Pod contient souvent un seul conteneur principal.

Plusieurs conteneurs peuvent être placés dans le même Pod lorsqu'ils doivent être étroitement liés, par exemple un conteneur principal et un conteneur auxiliaire.

Un Pod n'est pas une machine virtuelle. Il ne faut pas non plus considérer son adresse IP comme une adresse permanente.

### 5.4 ReplicaSet

Un ReplicaSet maintient un nombre cible de Pods correspondant à un sélecteur et à un modèle de Pod.

Si le nombre souhaité est trois et que seulement deux Pods correspondants existent, le ReplicaSet cherche à en créer un autre.

Il est généralement préférable de laisser un Deployment gérer le ReplicaSet.

### 5.5 Deployment

Un Deployment gère les déploiements d'applications généralement sans état (*stateless*).

Il permet notamment de :

- Définir le nombre de réplicas.
- Mettre à jour l'image de l'application.
- Modifier la configuration du Pod.
- Organiser les mises à jour progressives.
- Revenir à une révision antérieure lorsque les conditions le permettent.

### 5.6 Service

Un Service fournit un point d'accès réseau stable à un ensemble de Pods correspondant à ses sélecteurs.

Comme les Pods peuvent être détruits et remplacés, il serait fragile de configurer les applications clientes directement avec leurs adresses IP.

Le Service masque une partie de cette instabilité.

### 5.7 Namespace

Un Namespace est un espace de noms logique au sein du cluster.

Il permet notamment de séparer des ressources par équipe, projet ou environnement.

Exemples :

```text
Cluster Kubernetes
|
+-- Namespace : dev
|   +-- Deployments
|   +-- Pods
|   +-- Services
|
+-- Namespace : test
|   +-- Deployments
|   +-- Pods
|   +-- Services
|
+-- Namespace : production
    +-- Deployments
    +-- Pods
    +-- Services
```

Un Namespace ne constitue pas, à lui seul, une frontière de sécurité complète. Des politiques réseau, des permissions RBAC et d'autres contrôles peuvent être nécessaires.

## 6. Comprendre la relation entre les objets

Le flux classique d'un déploiement repose sur plusieurs objets liés.

```text
+----------------------+
|      Deployment      |
|                      |
| Réplicas souhaités: 3|
+----------------------+
           |
           v
+----------------------+
|      ReplicaSet      |
|                      |
| Maintient les Pods   |
+----------------------+
           |
           v
+----------------------+
|         Pods         |
|                      |
| Pod A    Pod B   Pod C
+----------------------+
           |
           | Correspondance via labels
           v
+----------------------+
|       Service        |
|                      |
| Point d'accès réseau |
+----------------------+
```

Le Deployment gère la stratégie de déploiement. Le ReplicaSet maintient le nombre souhaité de Pods. Les Pods exécutent les conteneurs. Le Service permet aux clients de joindre les Pods sélectionnés.

Le Service ne crée pas les Pods. Il les sélectionne en fonction de leurs labels.

## 7. Préparer un environnement d'apprentissage

Il est préférable de commencer par un cluster local plutôt que par un cluster de production.

Deux solutions courantes sont `kind` et `minikube`.

### 7.1 Comparaison des environnements

| Solution | Principe | Utilisation typique |
|---|---|---|
| `kind` | Utilise des conteneurs pour exécuter les nœuds Kubernetes | Tests, apprentissage, automatisation |
| `minikube` | Exécute Kubernetes localement, avec un ou plusieurs nœuds selon la configuration | Apprentissage et expérimentation |
| Cluster cloud | Utilise une infrastructure gérée ou hébergée chez un fournisseur | Tests d'intégration, préproduction et production selon l'offre |

Pour ce cours, `minikube` constitue le parcours principal. Les personnes disposant déjà de Docker et préférant une solution légère peuvent utiliser `kind`.

### 7.2 Installer les outils

Les prérequis du parcours principal sont :

- Un ordinateur sous Linux, Windows ou macOS.
- Un environnement d'exécution compatible, selon la solution choisie.
- `kubectl`, l'outil de ligne de commande Kubernetes.
- `minikube`.

Les procédures d'installation varient selon le système d'exploitation et évoluent avec les versions. Il est préférable de suivre les guides officiels plutôt que d'utiliser un binaire non vérifié.

Documentation officielle :

- Installation de `kubectl` : https://kubernetes.io/docs/tasks/tools/
- Environnements d'apprentissage : https://kubernetes.io/docs/setup/learning-environment/
- Installation de Minikube : https://minikube.sigs.k8s.io/docs/start/
- Démarrage de `kind` : https://kind.sigs.k8s.io/docs/user/quick-start/

### 7.3 Démarrer un cluster Minikube

Avec un environnement Docker installé et configuré, la commande suivante permet généralement de démarrer un cluster local :

```bash
minikube start --driver=docker
```

Selon la configuration de la machine, un autre pilote peut être nécessaire.

Vérifier ensuite l'état du cluster :

```bash
minikube status
```

Afficher les nœuds :

```bash
kubectl get nodes
```

Un résultat peut ressembler à ceci :

```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   2m    v1.xx.x
```

La version exacte dépend de celle installée localement.

Le statut `Ready` indique que le nœud est déclaré prêt pour les tâches Kubernetes selon les conditions signalées. Il ne prouve pas que toutes les applications futures fonctionneront correctement.

### 7.4 Vérifier la connexion au cluster

Afficher le contexte courant :

```bash
kubectl config current-context
```

Afficher les informations de connexion :

```bash
kubectl cluster-info
```

Demander la liste des Pods du Namespace actuel :

```bash
kubectl get pods
```

Afficher les composants du Namespace système :

```bash
kubectl get pods -n kube-system
```

Si `kubectl` n'arrive pas à contacter le cluster, il faut vérifier notamment que le cluster fonctionne et que le contexte utilisé est correct.

## 8. Comprendre `kubectl`

`kubectl` est l'outil de commande principal pour communiquer avec l'API Kubernetes.

### 8.1 Syntaxe générale

```text
kubectl VERBE RESSOURCE NOM OPTIONS
```

Exemples :

```bash
kubectl get pods
kubectl get deployments
kubectl describe pod mon-pod
kubectl logs mon-pod
kubectl delete deployment mon-application
```

Le verbe indique l'opération. La ressource indique le type d'objet concerné.

### 8.2 Commandes à connaître

| Commande | Fonction |
|---|---|
| `kubectl get pods` | Liste les Pods |
| `kubectl get deployments` | Liste les Deployments |
| `kubectl get services` | Liste les Services |
| `kubectl get nodes` | Liste les nœuds |
| `kubectl describe pod NOM` | Affiche les détails d'un Pod et ses événements |
| `kubectl logs NOM` | Affiche les journaux d'un conteneur |
| `kubectl exec -it NOM -- sh` | Ouvre un shell dans un conteneur si celui-ci possède un shell utilisable |
| `kubectl apply -f fichier.yaml` | Crée ou met à jour des objets déclarés |
| `kubectl delete -f fichier.yaml` | Supprime les objets décrits par le fichier |
| `kubectl get all` | Affiche plusieurs types courants de ressources, mais pas absolument toutes les ressources du cluster |

### 8.3 Afficher des informations supplémentaires

```bash
kubectl get pods -o wide
```

L'option `-o wide` affiche des informations supplémentaires, comme le nœud du Pod.

Pour visualiser les labels :

```bash
kubectl get pods --show-labels
```

Pour observer les ressources en continu :

```bash
kubectl get pods -w
```

Pour quitter ce mode d'observation, utiliser `Ctrl+C`.

## 9. Premier déploiement avec une commande

Nous allons déployer un serveur Web NGINX.

### 9.1 Créer le Deployment

```bash
kubectl create deployment site-web --image=nginx:stable
```

Cette commande demande à Kubernetes de créer un Deployment nommé `site-web`, dont le modèle de Pod utilise l'image `nginx:stable`.

Kubernetes télécharge généralement l'image depuis un registre si elle n'est pas déjà présente sur le nœud et si la politique de téléchargement l'exige.

### 9.2 Observer le Deployment

```bash
kubectl get deployments
```

Afficher les Pods :

```bash
kubectl get pods
```

Le Pod peut passer successivement par plusieurs états observables, le temps que l'image soit téléchargée, que le conteneur démarre et que les contrôleurs actualisent le statut.

Pour attendre la disponibilité du Deployment :

```bash
kubectl rollout status deployment/site-web
```

### 9.3 Afficher les détails

```bash
kubectl describe deployment site-web
```

Cette commande aide à comprendre :

- Le nombre de réplicas souhaités.
- Le nombre de réplicas disponibles.
- L'image configurée.
- Les labels et sélecteurs.
- Les événements associés au Deployment.

### 9.4 Mettre à l'échelle

Demander trois réplicas :

```bash
kubectl scale deployment site-web --replicas=3
```

Vérifier :

```bash
kubectl get deployments
kubectl get pods -o wide
```

On devrait retrouver trois Pods correspondant au Deployment lorsque le cluster dispose des ressources nécessaires.

```text
Deployment site-web
Réplicas souhaités : 3
          |
          v
+------------------+
| ReplicaSet       |
+------------------+
     |    |    |
     v    v    v
   Pod 1 Pod 2 Pod 3
```

Attention : cette manipulation change l'état du cluster. Si le manifeste utilisé pour le même Deployment indique ensuite un seul replica, une nouvelle application de ce manifeste ramènera le nombre souhaité à un.

## 10. Le langage YAML et les manifestes

Les commandes impératives sont pratiques pour découvrir Kubernetes. Pour conserver une configuration, la réutiliser et la versionner, les manifestes déclaratifs sont essentiels.

Un manifeste décrit un objet Kubernetes dans un format tel que YAML.

### 10.1 Structure générale

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: site-web
spec:
  replicas: 2
```

Les champs principaux sont :

- `apiVersion` : groupe et version de l'API.
- `kind` : type de ressource.
- `metadata` : nom, Namespace, labels et autres métadonnées.
- `spec` : description de l'état souhaité.

Cette structure seule ne suffit pas pour déployer un Deployment fonctionnel complet : le champ `spec` doit aussi contenir un sélecteur et un modèle de Pod cohérents.

### 10.2 Règles YAML élémentaires

L'indentation doit être correcte. Les espaces sont utilisés pour représenter la structure ; les tabulations ne doivent pas remplacer l'indentation par espaces.

Exemple :

```yaml
metadata:
  name: application-web
  labels:
    app: application-web
```

Le label `app` appartient à la section `labels`, qui appartient elle-même à `metadata`.

### 10.3 Approche impérative et approche déclarative

**Approche impérative :**

```bash
kubectl create deployment site-web --image=nginx:stable
```

On demande directement la création d'un objet.

**Approche déclarative :**

```bash
kubectl apply -f site-web.yaml
```

On décrit l'état désiré dans un fichier et on le soumet à Kubernetes.

La deuxième approche est généralement préférable pour des configurations durables, car le fichier peut être versionné avec Git, relu et réappliqué.

## 11. Créer un Deployment déclaratif

Créons le fichier `site-web.yaml`.

Le manifeste suivant contient un Deployment complet pour un serveur NGINX.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: site-web
  labels:
    app: site-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: site-web
  template:
    metadata:
      labels:
        app: site-web
    spec:
      containers:
        - name: nginx
          image: nginx:stable
          ports:
            - name: http
              containerPort: 80
          resources:
            requests:
              cpu: 100m
              memory: 64Mi
            limits:
              cpu: 250m
              memory: 128Mi
```

### 11.1 Comprendre le manifeste

`kind: Deployment` indique le type de ressource.

`replicas: 2` demande deux Pods.

`selector.matchLabels` indique les labels que le Deployment doit retrouver sur les Pods qu'il gère.

`template.metadata.labels` définit les labels que porteront les Pods créés par ce Deployment.

Le sélecteur et les labels du modèle doivent correspondre. Un sélecteur incohérent peut empêcher le Deployment de gérer les Pods attendus.

`containers` décrit les conteneurs du Pod. Le champ `image` précise l'image à exécuter.

`containerPort: 80` documente le port utilisé par le conteneur. Ce champ ne suffit pas, à lui seul, à rendre l'application accessible à l'extérieur du Pod.

Enfin, `resources` définit les demandes et les limites de ressources. Ces notions seront approfondies plus loin.

### 11.2 Valider et appliquer le fichier

Avant l'application :

```bash
kubectl apply --dry-run=client -f site-web.yaml
```

Cette validation locale permet de détecter certaines erreurs de construction du manifeste, mais elle ne garantit pas que le serveur API acceptera l'ensemble de la configuration.

Appliquer le manifeste :

```bash
kubectl apply -f site-web.yaml
```

Vérifier le résultat :

```bash
kubectl get deployment site-web
kubectl get pods -l app=site-web
```

Vérifier la disponibilité :

```bash
kubectl rollout status deployment/site-web
```

### 11.3 Modifier le fichier

Remplacer :

```yaml
replicas: 2
```

par :

```yaml
replicas: 4
```

Puis exécuter :

```bash
kubectl apply -f site-web.yaml
kubectl get pods -l app=site-web
```

Kubernetes prend la nouvelle valeur comme état souhaité.

Si le fichier conserve `replicas: 2`, la commande suivante :

```bash
kubectl apply -f site-web.yaml
```

réconciliera également le Deployment vers deux réplicas. Le fichier doit donc être traité comme une source importante de vérité de la configuration déclarée.

## 12. Comprendre le cycle de vie d'un Pod

Un Pod est une ressource éphémère. Il peut être remplacé, déplacé vers un autre nœud ou recréé par un contrôleur.

### 12.1 États courants

| État affiché | Signification générale |
|---|---|
| `Pending` | Le Pod attend une étape, par exemple sa planification ou le téléchargement d'une image |
| `Running` | Le Pod a été affecté à un nœud et au moins un conteneur est en cours d'exécution ou de démarrage |
| `Succeeded` | Les conteneurs se sont terminés avec succès, notamment pour certaines tâches ponctuelles |
| `Failed` | Les conteneurs se sont terminés et au moins l'un d'eux a échoué |
| `Unknown` | L'état du Pod ne peut pas être déterminé correctement |

`Running` ne veut pas nécessairement dire que l'application répond correctement aux requêtes. Une sonde de disponibilité peut apporter une information plus précise.

### 12.2 Suppression d'un Pod géré

Repérer un Pod :

```bash
kubectl get pods -l app=site-web
```

Supprimer un Pod :

```bash
kubectl delete pod NOM_DU_POD
```

Remplacer `NOM_DU_POD` par le nom réel affiché par la commande précédente.

Observer ensuite les Pods :

```bash
kubectl get pods -l app=site-web -w
```

Le Deployment et son ReplicaSet cherchent à maintenir le nombre souhaité de réplicas.

Ce comportement n'implique pas que tous les Pods restent à la même place. Un Pod supprimé peut être remplacé par un Pod portant un autre nom et possédant une autre adresse IP.

## 13. Les Services : communiquer avec une application

Le Pod possède une adresse IP utilisable au sein du réseau Kubernetes, mais cette adresse peut changer à son remplacement.

Un Service fournit un point d'accès stable à un ensemble de Pods sélectionnés.

### 13.1 Schéma du trafic

```text
          CLIENT
             |
             | Requête HTTP
             v
+----------------------------+
|          SERVICE           |
|        site-web-svc        |
|                            |
| IP stable dans le cluster  |
+----------------------------+
             |
        Sélection des Pods
             |
       +-----+-----+
       |           |
       v           v
+-----------+ +-----------+
|  Pod A    | |  Pod B    |
| NGINX :80 | | NGINX :80 |
+-----------+ +-----------+
```

Le Service choisit les Pods à partir de sélecteurs, puis distribue le trafic vers les points de terminaison disponibles selon le comportement réseau du cluster.

### 13.2 Les labels

Le Deployment utilise le label :

```yaml
labels:
  app: site-web
```

Le Service peut sélectionner ce label :

```yaml
selector:
  app: site-web
```

Si le sélecteur du Service ne correspond à aucun Pod, le Service peut exister sans avoir de points de terminaison utilisables.

### 13.3 Créer un Service avec une commande

```bash
kubectl expose deployment site-web \
  --name=site-web-svc \
  --port=80 \
  --target-port=80 \
  --type=ClusterIP
```

Explication :

- `--name` définit le nom du Service.
- `--port=80` définit le port exposé par le Service.
- `--target-port=80` désigne le port cible des conteneurs.
- `--type=ClusterIP` limite l'accès direct au réseau interne du cluster.

Vérifier :

```bash
kubectl get services
kubectl describe service site-web-svc
```

### 13.4 Port-forward : accéder au service depuis l'ordinateur

Depuis un terminal :

```bash
kubectl port-forward service/site-web-svc 8080:80
```

La commande maintient un transfert de port entre le port local `8080` et le port `80` du Service.

Tant que cette commande reste active, ouvrir un navigateur à l'adresse suivante :

```text
http://127.0.0.1:8080
```

La page d'accueil de NGINX devrait s'afficher.

Le `port-forward` est avant tout un mécanisme pratique pour les tests et le diagnostic. Il ne constitue pas, à lui seul, une architecture d'exposition publique destinée à la production.

### 13.5 Les types de Services

| Type | Rôle |
|---|---|
| `ClusterIP` | Rend le Service accessible au sein du réseau du cluster ; c'est le type par défaut |
| `NodePort` | Expose un port sur les nœuds du cluster |
| `LoadBalancer` | Demande un équilibreur de charge externe dans les environnements qui le prennent en charge |
| `ExternalName` | Associe le Service à un nom DNS externe à travers un enregistrement CNAME |

Le choix du type de Service dépend du besoin et de l'environnement d'exécution.

`LoadBalancer` ne signifie pas que tout cluster local va automatiquement fournir une adresse IP publique. Cela dépend du fournisseur, de l'intégration réseau et de l'environnement.

## 14. Configurer une application avec ConfigMap

Une application a souvent besoin de paramètres de configuration : nom d'environnement, adresse d'un service, mode de fonctionnement ou options applicatives.

Kubernetes fournit `ConfigMap` pour gérer des données de configuration qui ne sont pas sensibles.

### 14.1 Créer une ConfigMap

Exemple de fichier `application-config.yaml` :

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: application-config
data:
  APP_ENV: "development"
  LOG_LEVEL: "info"
```

Créer l'objet :

```bash
kubectl apply -f application-config.yaml
```

Afficher les données :

```bash
kubectl get configmap application-config
kubectl describe configmap application-config
```

### 14.2 Injecter la configuration dans un Pod

Dans la définition d'un conteneur, on peut récupérer les valeurs de la ConfigMap par des variables d'environnement.

Exemple de fragment de manifeste :

```yaml
envFrom:
  - configMapRef:
      name: application-config
```

Le fragment doit être placé dans la section du conteneur, au même niveau que `image`, `ports` et `resources`.

Le conteneur recevra alors les variables d'environnement `APP_ENV` et `LOG_LEVEL`.

L'application doit réellement lire ces variables pour que la configuration ait un effet.

Une ConfigMap n'est pas conçue pour stocker des mots de passe ou des clés privées.

## 15. Première distinction sur les Secrets

Un objet `Secret` sert à stocker des données sensibles, par exemple des identifiants, des jetons et des clés.

Cependant, le mot « Secret » ne signifie pas que les données sont automatiquement protégées contre tous les accès non autorisés.

Les précautions comprennent :

- Limiter l'accès aux Secrets avec RBAC.
- Ne pas committer de vrais identifiants dans Git.
- Activer le chiffrement au repos lorsqu'il est requis et disponible.
- Restreindre les comptes autorisés à créer des Pods et des Deployments.
- Protéger les sauvegardes et l'accès à la base de données du cluster.
- Éviter d'afficher ou d'enregistrer les valeurs sensibles dans les journaux.

Les valeurs d'un Secret encodées en Base64 ne sont pas nécessairement chiffrées. Base64 est un encodage, pas un mécanisme de chiffrement.

Pour ce niveau, il suffit de retenir qu'une ConfigMap est destinée à une configuration non sensible, tandis qu'un Secret est prévu pour des données sensibles et doit être accompagné de contrôles d'accès adaptés.

La gestion avancée des Secrets, du RBAC et des politiques de sécurité sera abordée dans les niveaux suivants.

## 16. Les ressources CPU et mémoire

Un cluster possède des ressources limitées. Il est important de spécifier les ressources dont une application a besoin et les limites qu'elle ne doit pas dépasser.

### 16.1 Requests et limits

`requests` indique les ressources demandées par le conteneur. Ces valeurs sont notamment prises en compte par le scheduler lorsqu'il choisit un nœud.

`limits` définit des plafonds de consommation pour les ressources concernées.

Exemple :

```yaml
resources:
  requests:
    cpu: 100m
    memory: 64Mi
  limits:
    cpu: 250m
    memory: 128Mi
```

Comprendre les unités :

- `100m` CPU représente un dixième de CPU, soit 0,1 CPU.
- `250m` représente un quart de CPU, soit 0,25 CPU.
- `64Mi` représente 64 mébioctets.
- `128Mi` représente 128 mébioctets.

### 16.2 Différence entre demande et limite

Supposons qu'un conteneur dispose de :

```text
CPU request : 100m
CPU limit   : 250m

RAM request : 64Mi
RAM limit   : 128Mi
```

```text
CPU
0m             100m                 250m
|----------------|--------------------|
       demande            plafond

Mémoire
0Mi             64Mi                 128Mi
|----------------|--------------------|
       demande            plafond
```

La demande n'est pas une limite stricte d'utilisation CPU. Si les conditions du nœud le permettent, le conteneur peut consommer davantage que sa demande, jusqu'aux contraintes applicables.

À l'inverse, une limite de mémoire dépassée peut conduire le système à terminer le conteneur, souvent avec un motif `OOMKilled`.

Des requests et limits mal adaptées peuvent empêcher le placement d'un Pod ou dégrader le fonctionnement de l'application.

## 17. Les sondes de santé

Un conteneur en cours d'exécution n'est pas forcément prêt à recevoir du trafic. Kubernetes fournit des sondes pour suivre certains aspects de la santé de l'application.

### 17.1 Les trois sondes

**`startupProbe`**

Vérifie que l'application a terminé son démarrage. Pendant que cette sonde reste en attente de réussite, les sondes de démarrage ou de disponibilité associées sont suspendues selon les règles Kubernetes applicables.

**`livenessProbe`**

Vérifie si le conteneur semble fonctionner correctement. Si la sonde échoue suffisamment souvent, Kubernetes peut redémarrer le conteneur selon sa configuration.

**`readinessProbe`**

Vérifie si l'application est prête à recevoir du trafic. Si elle échoue, le Pod n'est pas considéré comme prêt et ne doit normalement pas recevoir le trafic des Services qui utilisent ses points de terminaison prêts.

### 17.2 Diagramme fonctionnel

```text
              CONTENEUR DÉMARRÉ
                     |
                     v
             +-----------------+
             | startupProbe ?  |
             +-----------------+
                     |
               Réussite obtenue
                     |
                     v
             +-----------------+
             | readinessProbe  |
             +-----------------+
                |           |
              OK          Échec
                |           |
                v           v
        Trafic autorisé   Pas de trafic
                |
                v
             Application

        livenessProbe : surveillance distincte
        qui peut déclencher un redémarrage
        lorsqu'un échec durable est détecté.
```

### 17.3 Exemple de sondes HTTP

Voici un extrait de configuration pour une application qui répond à des requêtes HTTP sur le port 80 et fournit le chemin `/` :

```yaml
startupProbe:
  httpGet:
    path: /
    port: 80
  periodSeconds: 5
  failureThreshold: 30

readinessProbe:
  httpGet:
    path: /
    port: 80
  periodSeconds: 5
  failureThreshold: 3

livenessProbe:
  httpGet:
    path: /
    port: 80
  periodSeconds: 10
  failureThreshold: 3
```

Les sondes doivent être placées dans la définition du conteneur.

Ces valeurs constituent un exemple pédagogique, pas un réglage universel. Un service de production doit fournir des points de contrôle réellement significatifs pour son fonctionnement.

Il faut notamment éviter une sonde de vivacité qui échoue simplement parce qu'une dépendance externe est temporairement indisponible : cela pourrait déclencher des redémarrages inutiles.

## 18. Mettre à jour une application

Les Deployments permettent de modifier l'image d'une application et de gérer une mise à jour progressive.

### 18.1 Mise à jour de l'image

Commande :

```bash
kubectl set image deployment/site-web nginx=nginx:stable
```

Dans cet exemple, l'image est réassignée à la valeur `nginx:stable`. Comme il s'agit de la même référence que celle du cours, il ne faut pas s'attendre à une nouvelle version fonctionnelle.

Pour apprendre réellement la mise à jour, il faut sélectionner une autre référence d'image appropriée, par exemple une version validée dans le registre utilisé. Le nom du conteneur `nginx` doit correspondre à celui du Deployment.

Une fois une nouvelle image configurée, suivre le déploiement :

```bash
kubectl rollout status deployment/site-web
```

Consulter l'historique :

```bash
kubectl rollout history deployment/site-web
```

### 18.2 Comprendre le déploiement progressif

```text
VERSION A : 3 Pods
+--------+  +--------+  +--------+
| vA     |  | vA     |  | vA     |
+--------+  +--------+  +--------+
     |
     | Mise à jour progressive
     v
VERSION MIXTE PENDANT LA TRANSITION
+--------+  +--------+  +--------+
| vA     |  | vB     |  | vB     |
+--------+  +--------+  +--------+
     |
     | Mise à jour terminée
     v
VERSION B : 3 Pods
+--------+  +--------+  +--------+
| vB     |  | vB     |  | vB     |
+--------+  +--------+  +--------+
```

Le comportement exact dépend de la stratégie du Deployment, de sa configuration, de la disponibilité des nouvelles instances et des limites de ressources.

Une mise à jour progressive n'assure pas, à elle seule, la compatibilité fonctionnelle entre deux versions de l'application.

### 18.3 Revenir à une révision précédente

Si le Deployment dispose d'une révision antérieure exploitable :

```bash
kubectl rollout undo deployment/site-web
```

Puis :

```bash
kubectl rollout status deployment/site-web
```

Cette opération revient sur une révision précédente de la configuration du Deployment. Elle n'annule pas automatiquement une migration de base de données ou une autre modification externe à cette ressource.

Pour une exploitation sérieuse, les mises à jour doivent être versionnées, testées et accompagnées d'une procédure de retour arrière.

## 19. Les journaux et le diagnostic

Le diagnostic est une compétence fondamentale en administration Kubernetes.

### 19.1 Afficher les Pods

```bash
kubectl get pods
```

Si le nom d'un Pod est connu :

```bash
kubectl describe pod NOM_DU_POD
```

Le résultat affiche de nombreux détails, notamment les événements associés au Pod.

### 19.2 Lire les journaux

```bash
kubectl logs NOM_DU_POD
```

Pour suivre les nouveaux messages :

```bash
kubectl logs -f NOM_DU_POD
```

Pour un Pod contenant plusieurs conteneurs, il peut être nécessaire de sélectionner le conteneur :

```bash
kubectl logs NOM_DU_POD -c NOM_DU_CONTENEUR
```

### 19.3 Consulter les événements

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

Les événements fournissent des indications sur les échecs de téléchargement d'images, le placement des Pods, les sondes et d'autres opérations du cluster.

Ils ne remplacent pas les journaux de l'application et peuvent être conservés pendant une durée limitée.

### 19.4 Tableau de diagnostic

| Symptôme | Causes possibles | Première vérification |
|---|---|---|
| `Pending` | Ressources insuffisantes, contraintes de placement, volume indisponible | `kubectl describe pod NOM` |
| `ImagePullBackOff` | Image inexistante, registre inaccessible, authentification incorrecte | Vérifier `image` et les événements |
| `CrashLoopBackOff` | Application qui s'arrête répétitivement, commande invalide, configuration incorrecte | `kubectl logs NOM` |
| `OOMKilled` | Consommation de mémoire ayant dépassé les limites applicables | `kubectl describe pod NOM` et ressources |
| `ErrImagePull` | Échec de téléchargement de l'image | Vérifier l'image, le réseau et les identifiants du registre |
| Service sans trafic | Sélecteur incorrect, Pods non prêts, port cible incorrect | `kubectl describe service NOM` |
| `0/1` réplique disponible | Pod non prêt ou échec de démarrage | `kubectl get pods`, `kubectl describe pod NOM` |

Les statuts donnent des indices, pas nécessairement la cause finale. Il faut vérifier les événements et les journaux avant de conclure.

## 20. Les namespaces en pratique

Le Namespace `default` est utilisé lorsqu'aucun autre Namespace n'est sélectionné.

Il est possible de créer un espace de travail séparé pour les exercices.

Créer un Namespace :

```bash
kubectl create namespace laboratoire
```

Vérifier :

```bash
kubectl get namespaces
```

Créer un Deployment directement dans ce Namespace :

```bash
kubectl create deployment demo-web \
  --image=nginx:stable \
  -n laboratoire
```

Afficher les ressources :

```bash
kubectl get deployments -n laboratoire
kubectl get pods -n laboratoire
```

Pour demander des Pods dans ce Namespace, il faut fournir `-n laboratoire` à la commande ou configurer le contexte courant pour utiliser ce Namespace.

La séparation logique facilite l'organisation des ressources, mais elle ne remplace ni la gestion des permissions ni les politiques de sécurité.

## 21. Premières règles de sécurité

Kubernetes donne beaucoup de pouvoir aux utilisateurs et aux applications qui disposent de ses autorisations. Une erreur de configuration peut exposer des ressources ou permettre des opérations non souhaitées.

Même au niveau débutant, il faut adopter quelques principes.

### 21.1 Protéger le cluster

- Ne pas partager les fichiers de configuration d'accès au cluster sans contrôle.
- Éviter de travailler avec des droits administrateur lorsque des droits limités suffisent.
- Ne pas exposer publiquement le serveur API sans configuration appropriée.
- Ne pas stocker de vrais mots de passe dans les fichiers de cours ou les dépôts Git.
- Maintenir à jour les images et les composants utilisés.
- Limiter l'accès aux journaux, aux Secrets et aux ressources sensibles.
- Tester les commandes de suppression dans un environnement d'apprentissage avant de les exécuter en production.

### 21.2 Attention aux privilèges

Un conteneur Kubernetes ne doit pas être exécuté avec des privilèges élevés sans besoin démontré.

Les configurations de sécurité pertinentes comprennent les contextes de sécurité des Pods et des conteneurs, les comptes de service, RBAC, les politiques réseau et les Pod Security Standards.

Ces mécanismes seront étudiés plus en profondeur dans le niveau intermédiaire ou dans un cours dédié à la sécurité Kubernetes.

### 21.3 Les sauvegardes

Un cluster ne remplace pas une politique de sauvegarde des données.

Une application avec état peut avoir besoin de volumes persistants, de sauvegardes cohérentes, d'une procédure de restauration testée et d'une stratégie adaptée aux pannes de stockage.

La suppression ou la recréation d'un Pod ne doit pas être confondue avec la sauvegarde ou la restauration des données.

## 22. Travaux pratiques guidés

Les travaux pratiques suivants réutilisent les notions apprises. Ils doivent être exécutés sur un cluster local de test.

### TP 1 — Découverte du cluster

**Objectif :** vérifier que le cluster fonctionne et identifier ses composants visibles.

Exécuter :

```bash
kubectl cluster-info
kubectl get nodes
kubectl get namespaces
kubectl get pods -n kube-system
```

Questions :

1. Combien de nœuds le cluster expose-t-il ?
2. Quel est le statut du nœud ?
3. À quoi sert le Namespace `kube-system` ?
4. Pourquoi le statut `Ready` du nœud ne garantit-il pas la santé de toutes les applications futures ?

**Résultats attendus :** identifier le cluster, le ou les nœuds, les Namespaces et les Pods système visibles. La composition exacte dépend de l'environnement utilisé.

### TP 2 — Déployer une application

**Objectif :** créer et observer un Deployment.

Exécuter :

```bash
kubectl create deployment tp-web --image=nginx:stable
kubectl rollout status deployment/tp-web
kubectl get deployment tp-web
kubectl get pods -o wide
```

Questions :

1. Quel objet as-tu créé directement ?
2. Quel objet maintient les réplicas derrière le Deployment ?
3. Combien de Pods sont actuellement souhaités ?
4. Pourquoi ne faut-il pas considérer l'adresse IP d'un Pod comme permanente ?

**Résultats attendus :** repérer le Deployment, son ReplicaSet et le Pod associé.

### TP 3 — Créer trois réplicas

**Objectif :** observer la réconciliation d'un Deployment.

```bash
kubectl scale deployment tp-web --replicas=3
kubectl get deployment tp-web
kubectl get pods -l app=tp-web
```

Identifier le nombre souhaité, le nombre actualisé et le nombre disponible.

Si la machine manque de ressources, certains Pods peuvent ne pas devenir disponibles immédiatement. Il faut alors consulter les événements plutôt que supposer que Kubernetes a ignoré la demande.

### TP 4 — Exposer le serveur Web

**Objectif :** communiquer avec l'application à travers un Service.

```bash
kubectl expose deployment tp-web \
  --name=tp-web-svc \
  --port=80 \
  --target-port=80 \
  --type=ClusterIP
```

Afficher le Service :

```bash
kubectl get services
kubectl describe service tp-web-svc
```

Puis lancer :

```bash
kubectl port-forward service/tp-web-svc 8080:80
```

Ouvrir `http://127.0.0.1:8080` dans un navigateur, ou tester la réponse dans un autre terminal :

```bash
curl http://127.0.0.1:8080
```

Interpréter le rôle respectif du Service, des Pods et du port-forward.

### TP 5 — Supprimer un Pod

**Objectif :** comprendre le rôle du contrôleur.

Afficher les noms :

```bash
kubectl get pods -l app=tp-web
```

Choisir l'un des Pods et le supprimer :

```bash
kubectl delete pod NOM_DU_POD
```

Observer :

```bash
kubectl get pods -l app=tp-web -w
```

Expliquer pourquoi un nouveau Pod peut apparaître alors qu'aucune commande de création n'a été exécutée manuellement.

### TP 6 — Pratiquer le diagnostic

**Objectif :** apprendre à rechercher les causes d'un problème.

Afficher les détails d'un Pod :

```bash
kubectl describe pod NOM_DU_POD
```

Afficher les journaux :

```bash
kubectl logs NOM_DU_POD
```

Afficher les événements :

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

Écrire une courte synthèse indiquant le symptôme observé, les indices obtenus et la prochaine vérification à effectuer.

## 23. Projet de fin de niveau

### Sujet : déployer un petit serveur Web résilient

L'objectif est de créer un mini-environnement Web reproductible en utilisant des manifestes Kubernetes.

#### Cahier des charges

L'environnement doit contenir :

1. Un Namespace nommé `projet-web`.
2. Un Deployment nommé `web`.
3. Deux réplicas NGINX.
4. Des labels cohérents et un sélecteur fonctionnel.
5. Des demandes et limites CPU/mémoire.
6. Un Service nommé `web-svc` de type `ClusterIP`.
7. Une procédure d'accès au site avec `kubectl port-forward`.
8. Une procédure de diagnostic.
9. Une procédure de nettoyage.

#### Arborescence attendue

```text
projet-web/
|
+-- namespace.yaml
|
+-- deployment.yaml
|
+-- service.yaml
|
+-- README.md
```

#### Étape 1 : créer le Namespace

Dans `namespace.yaml` :

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: projet-web
```

#### Étape 2 : créer le Deployment

Le fichier `deployment.yaml` doit contenir :

- `apiVersion: apps/v1`
- `kind: Deployment`
- Le nom `web`
- Deux réplicas
- Un sélecteur qui correspond aux labels des Pods
- Un conteneur utilisant `nginx:stable`
- Le port de conteneur 80
- Des ressources `requests` et `limits`

Pour limiter les risques de mauvaise indentation, reprendre le manifeste complet de la section 11 et adapter le nom, les labels et le nombre de réplicas.

Il faudra également placer la ressource dans le Namespace `projet-web`, soit en déclarant le Namespace dans les métadonnées du Deployment, soit en appliquant le manifeste avec le contexte approprié. Dans ce projet, la méthode recommandée est d'ajouter :

```yaml
metadata:
  name: web
  namespace: projet-web
```

Le manifeste du Deployment doit ensuite conserver sa structure interne correcte.

#### Étape 3 : créer le Service

Le fichier `service.yaml` doit contenir un objet `Service` avec :

- Le nom `web-svc`.
- Le Namespace `projet-web`.
- Le type `ClusterIP`.
- Le port du Service `80`.
- Le port cible `80`.
- Un sélecteur correspondant exactement aux labels des Pods du Deployment.

#### Étape 4 : appliquer les manifestes

```bash
kubectl apply -f namespace.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

Contrôler les résultats :

```bash
kubectl get all -n projet-web
kubectl rollout status deployment/web -n projet-web
kubectl describe service web-svc -n projet-web
```

#### Étape 5 : tester l'application

```bash
kubectl port-forward service/web-svc 8080:80 -n projet-web
```

Accéder ensuite à :

```text
http://127.0.0.1:8080
```

#### Étape 6 : tester le remplacement d'un Pod

Supprimer un Pod du projet, constater son remplacement, puis confirmer que le Service reste utilisable.

#### Étape 7 : nettoyer l'environnement

Une fois le travail terminé :

```bash
kubectl delete namespace projet-web
```

Cette commande supprime le Namespace et ses ressources Kubernetes ordinaires associées. Les effets sur les ressources externes et certains volumes dépendent de leur configuration et des politiques du cluster.

**Critères de réussite :** le projet doit pouvoir être recréé à partir des fichiers, présenter deux Pods disponibles, fournir un Service fonctionnel et être accompagné d'instructions simples permettant à une autre personne de le tester.

## 24. Exercices de compréhension

### Exercice 1 — Identifier les composants

Associer chaque terme à sa fonction :

| Terme | Fonction |
|---|---|
| A. Pod | 1. Point d'accès réseau stable |
| B. Service | 2. Agent qui veille à l'exécution des Pods sur un nœud |
| C. Deployment | 3. Unité déployable contenant un ou plusieurs conteneurs |
| D. kubelet | 4. Gestion des réplicas et des mises à jour de Pods |

### Exercice 2 — Comprendre les réplicas

Un Deployment demande cinq réplicas. Trois Pods sont disponibles et deux autres sont en cours de création.

1. Quel est le nombre de réplicas souhaité ?
2. Combien de réplicas sont actuellement disponibles ?
3. Quelle commande permet d'observer les Pods ?
4. Quelle commande aide à examiner les événements d'un Pod qui ne devient pas disponible ?

### Exercice 3 — Diagnostiquer un Service

Un Service existe, mais le client ne reçoit aucune réponse.

Citer quatre éléments à vérifier avant de conclure que le réseau du cluster est défaillant.

### Exercice 4 — Comprendre l'état désiré

Un manifeste indique :

```yaml
spec:
  replicas: 2
```

Le Deployment possède actuellement quatre Pods en exécution.

Quel nombre de réplicas le contrôleur cherchera-t-il normalement à maintenir après l'application du manifeste ? Expliquer pourquoi les fichiers déclaratifs doivent rester cohérents avec les changements effectués en ligne de commande.

### Exercice 5 — Reconnaître les limites

Indiquer si les affirmations suivantes sont vraies ou fausses :

1. Une adresse IP de Pod est nécessairement permanente.
2. Un Service de type `ClusterIP` est normalement destiné à l'accès interne au cluster.
3. `kubectl logs` affiche les journaux applicatifs du conteneur sélectionné.
4. Un Secret Kubernetes est automatiquement chiffré simplement parce que ses valeurs sont encodées en Base64.
5. La suppression d'un Pod géré par un Deployment conduit généralement son contrôleur à essayer de rétablir le nombre souhaité de réplicas.

## 25. Corrigés des exercices

### Corrigé 1

A → 3 : le Pod est l'unité déployable regroupant un ou plusieurs conteneurs.

B → 1 : le Service fournit un point d'accès réseau stable vers des Pods sélectionnés.

C → 4 : le Deployment gère les réplicas et les mises à jour au travers de contrôleurs associés.

D → 2 : `kubelet` veille à l'exécution des Pods affectés au nœud.

### Corrigé 2

1. Cinq réplicas sont souhaités.
2. Trois réplicas sont disponibles.
3. `kubectl get pods` affiche les Pods.
4. `kubectl describe pod NOM_DU_POD` aide à identifier les événements et les raisons possibles du blocage.

L'application reste en transition tant que les réplicas attendus ne sont pas disponibles. La cause peut être un délai de démarrage, un échec de téléchargement d'image, un problème de ressources ou une autre erreur.

### Corrigé 3

Il faut notamment vérifier :

1. Que les sélecteurs du Service correspondent aux labels des Pods.
2. Que les Pods sont prêts à recevoir du trafic.
3. Que les ports du Service et du conteneur sont correctement définis.
4. Que les événements et les journaux n'indiquent pas un défaut de démarrage ou d'application.

Il faut également vérifier le chemin réseau et les règles de politique réseau lorsqu'elles existent.

### Corrigé 4

Le Deployment cherchera normalement à maintenir deux réplicas. Le nombre de Pods pourrait temporairement être différent pendant la réconciliation.

Un manifeste déclaratif décrit l'état cible. Réappliquer un fichier qui indique deux réplicas peut annuler une modification effectuée précédemment avec `kubectl scale` pour passer à quatre.

### Corrigé 5

1. Faux. Un Pod peut être remplacé et recevoir une autre adresse IP.
2. Vrai. `ClusterIP` sert principalement à l'accès interne au cluster.
3. Vrai, à condition de cibler le bon Pod et le bon conteneur.
4. Faux. Base64 est un encodage, pas un chiffrement.
5. Vrai, sous réserve du fonctionnement du contrôleur et des ressources disponibles.

## 26. Erreurs fréquentes à éviter

### Erreur 1 — Confondre conteneur et Pod

Un conteneur est exécuté à l'intérieur d'un Pod. Kubernetes orchestre les Pods, qui peuvent contenir un ou plusieurs conteneurs.

### Erreur 2 — Gérer directement les Pods d'une application durable

Un Pod isolé peut servir pour un test, mais une application qui doit maintenir plusieurs réplicas devrait généralement être gérée par un Deployment ou un autre contrôleur approprié.

### Erreur 3 — Utiliser l'adresse IP d'un Pod comme adresse fixe

Un remplacement peut changer l'adresse IP. Les communications entre applications doivent généralement s'appuyer sur des Services et la résolution DNS correspondante.

### Erreur 4 — Confondre port de conteneur et exposition réseau

Déclarer `containerPort: 80` ne crée pas un accès public. L'accès dépend du réseau des Pods, des Services et, le cas échéant, d'un mécanisme d'exposition externe.

### Erreur 5 — Considérer `Running` comme une preuve de bon fonctionnement

Un conteneur peut être en cours d'exécution tout en ne répondant pas correctement. Les journaux, les tests et les sondes fournissent des informations complémentaires.

### Erreur 6 — Croire que Kubernetes sauvegarde automatiquement les données

Kubernetes gère les ressources déclarées, mais une vraie stratégie de sauvegarde et de restauration reste nécessaire pour les données importantes.

### Erreur 7 — Modifier le cluster sans mettre à jour les manifestes

Une commande directe peut modifier temporairement l'état du cluster par rapport aux fichiers conservés dans Git. Il est important de maintenir les manifestes cohérents avec l'état souhaité.

## 27. Fiche de révision

| Notion | À retenir |
|---|---|
| Kubernetes | Orchestre des applications conteneurisées |
| Cluster | Ensemble de ressources coordonnées par Kubernetes |
| Control plane | Composants responsables de la gestion du cluster |
| Node | Machine participant au cluster |
| kube-apiserver | Point d'entrée de l'API |
| etcd | Stockage persistant de l'état du cluster |
| kube-scheduler | Affecte les Pods à des nœuds |
| kubelet | Veille à l'exécution des Pods sur son nœud |
| Pod | Plus petite unité déployable |
| ReplicaSet | Maintient un nombre cible de Pods correspondants |
| Deployment | Gère le déploiement et les mises à jour d'applications généralement stateless |
| Service | Point d'accès stable vers des Pods sélectionnés |
| Namespace | Espace logique de regroupement de ressources |
| ConfigMap | Configuration non sensible |
| Secret | Objet destiné aux données sensibles, à protéger par des contrôles appropriés |
| requests | Ressources demandées, notamment pour la planification |
| limits | Plafonds de ressources applicables |
| `kubectl` | Outil en ligne de commande pour interagir avec Kubernetes |
| Manifest | Description déclarative d'un objet Kubernetes |

## 28. Mini-glossaire

**API Kubernetes :** interface utilisée pour créer, lire, modifier et supprimer les objets du cluster.

**Conteneur :** processus applicatif isolé exécuté à partir d'une image.

**Control plane :** composants chargés de gérer l'état et les décisions du cluster.

**Déploiement :** opération consistant à mettre une application à disposition dans l'environnement cible ; le terme *Deployment* désigne aussi une ressource Kubernetes spécifique.

**Image :** paquet contenant l'application et les dépendances nécessaires à son exécution.

**Label :** paire clé-valeur permettant notamment d'organiser et de sélectionner des objets.

**Manifeste :** fichier décrivant un objet Kubernetes.

**Namespace :** espace logique permettant de regrouper certaines ressources.

**Nœud :** machine physique ou virtuelle participant au cluster.

**Pod :** unité déployable Kubernetes qui regroupe un ou plusieurs conteneurs.

**Réconciliation :** processus qui compare l'état réel et l'état souhaité afin de les rapprocher.

**Réplicas :** instances d'un modèle de Pod exécutées selon le nombre souhaité.

**Registry :** registre qui stocke des images de conteneurs.

**Runtime :** logiciel chargé d'exécuter les conteneurs.

**Sonde :** mécanisme de contrôle permettant d'évaluer certains aspects du démarrage, du fonctionnement ou de la disponibilité d'un conteneur.

**État souhaité :** état déclaré dans les objets Kubernetes et que les contrôleurs cherchent à maintenir.

## 29. Ressources officielles

Les documents suivants constituent les références principales pour approfondir et vérifier les concepts du cours.

- Vue d'ensemble de Kubernetes : https://kubernetes.io/docs/concepts/overview/
- Architecture du cluster : https://kubernetes.io/docs/concepts/architecture/
- Pods : https://kubernetes.io/docs/concepts/workloads/pods/
- Deployments : https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- ReplicaSets : https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/
- Services et réseau : https://kubernetes.io/docs/concepts/services-networking/service/
- Namespaces : https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/
- ConfigMaps : https://kubernetes.io/docs/concepts/configuration/configmap/
- Secrets : https://kubernetes.io/docs/concepts/configuration/secret/
- Gestion des ressources : https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- Cycle de vie des Pods et sondes : https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- Installation et outils : https://kubernetes.io/docs/tasks/tools/
- Environnement d'apprentissage : https://kubernetes.io/docs/setup/learning-environment/
- Tutoriel interactif Kubernetes Basics : https://kubernetes.io/docs/tutorials/kubernetes-basics/

## 30. Validation finale des acquis

Avant de passer au niveau intermédiaire, vérifier que les compétences suivantes sont maîtrisées :

- [ ] Expliquer les différences entre Docker et Kubernetes.
- [ ] Identifier les principaux composants du plan de contrôle.
- [ ] Expliquer les fonctions du Pod, du ReplicaSet, du Deployment et du Service.
- [ ] Démarrer un cluster local et vérifier son état.
- [ ] Utiliser `kubectl get`, `describe`, `logs` et `apply`.
- [ ] Déployer une application avec un manifeste YAML.
- [ ] Comprendre les labels et les sélecteurs.
- [ ] Créer trois réplicas et observer leur fonctionnement.
- [ ] Exposer un serveur Web par un Service.
- [ ] Utiliser `port-forward` pour accéder à une application depuis la machine locale.
- [ ] Identifier les premières causes possibles de `Pending`, `ImagePullBackOff` et `CrashLoopBackOff`.
- [ ] Expliquer le rôle des requests, des limits et des sondes.
- [ ] Distinguer la configuration non sensible des données sensibles.
- [ ] Recréer un petit environnement à partir de manifestes versionnés.
- [ ] Nettoyer les ressources de test sans supprimer involontairement les ressources d'un autre projet.

La prochaine étape du parcours consiste à approfondir les Deployments, les ReplicaSets, les Services, les labels et sélecteurs, les stratégies de mise à jour, les probes, les ressources et l'organisation des manifestes afin de pouvoir exploiter une application Kubernetes plus structurée.