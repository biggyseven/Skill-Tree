# Kubernetes avancé et Sécurité

## 1. Objectifs du niveau expert

Ce cours prolonge les bases de Kubernetes et l'étude du réseau et du stockage. L'objectif n'est plus seulement de déployer une application, mais de savoir concevoir, sécuriser, exploiter et dépanner une plateforme Kubernetes dans un environnement de production.

À ce niveau, il faut comprendre non seulement comment configurer une ressource, mais aussi pourquoi elle existe, quelles garanties elle apporte, quelles sont ses limites et comment elle interagit avec le reste du cluster.

À la fin de ce cours, il faudra être capable de :

- Expliquer le fonctionnement avancé du plan de contrôle, de l'ordonnanceur et des contrôleurs.
- Construire des déploiements résilients capables de supporter la perte d'un Pod ou d'un nœud.
- Contrôler la consommation des ressources et anticiper les problèmes de capacité.
- Sécuriser l'accès à l'API Kubernetes avec RBAC et le principe du moindre privilège.
- Appliquer les Pod Security Standards et renforcer les conteneurs.
- Segmenter les communications avec les NetworkPolicies.
- Protéger les Secrets, les identités applicatives et les images de conteneurs.
- Comprendre les politiques d'admission et les journaux d'audit.
- Mettre en place une stratégie de supervision, de sauvegarde et de reprise après incident.
- Diagnostiquer des problèmes complexes à partir des événements, des métriques et des journaux.
- Concevoir une architecture Kubernetes exploitable en production.

## 2. Préparation de l'environnement

### 2.1. Prérequis

Il est nécessaire de maîtriser les notions suivantes :

- Pods, Deployments, ReplicaSets et Services.
- Namespaces, ConfigMaps et Secrets.
- PVC, PV, StorageClass et StatefulSets.
- DNS interne et communication entre Pods.
- NetworkPolicies et fonctionnement général d'un plugin CNI.
- Images Docker, registres et gestion des versions.
- Commandes Linux, notions TCP/IP, processus, permissions et système de fichiers.
- YAML et utilisation de `kubectl`.

Les exercices peuvent être réalisés sur un cluster de laboratoire. Un environnement local convient pour une grande partie du cours, mais certaines expériences de haute disponibilité, de stockage distribué, d'audit du plan de contrôle et de récupération après panne nécessitent un cluster plus complet.

### 2.2. Vérifier le cluster

```bash
kubectl version
kubectl cluster-info
kubectl get nodes -o wide
kubectl get namespaces
kubectl get pods -A
kubectl config current-context
```

La commande suivante permet de vérifier les ressources disponibles :

```bash
kubectl top nodes
kubectl top pods -A
```

Ces deux dernières commandes nécessitent une source de métriques compatible, généralement Metrics Server.

Inspecter les ressources du cluster sans modifier leur configuration permet de disposer d'un état de référence avant de commencer les travaux.

### 2.3. Règle de sécurité pour le laboratoire

Ne pas réaliser volontairement des tests de privilèges, des suppressions de ressources de contrôle, des modifications de certificats ou des expériences de chiffrement sur un cluster partagé ou de production.

Les exercices impliquant une politique restrictive, une panne ou une modification de configuration du plan de contrôle doivent être conduits dans un environnement isolé, avec une procédure de retour arrière.

## 3. Architecture avancée de Kubernetes

### 3.1. Les composants du plan de contrôle

Le plan de contrôle coordonne les opérations du cluster. Il expose l'API, conserve l'état déclaré, planifie les Pods et fait converger les ressources réelles vers l'état souhaité.

```text
                UTILISATEUR / CI-CD / AUTOMATISATION
                              |
                              v
                       kubectl / API Client
                              |
                              v
                    +----------------------+
                    |     kube-apiserver   |
                    | Authentification     |
                    | Autorisation RBAC    |
                    | Admission            |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |         etcd         |
                    | État persistant      |
                    | Objets Kubernetes    |
                    +----------------------+

             +----------------+----------------+
             |                |                |
             v                v                v
       +-----------+    +-------------+  +-------------+
       | Scheduler |    | Controllers |  | Autres       |
       | Placement |    | Convergence |  | composants   |
       +-----+-----+    +------+------+  +-------------+
             |                 |
             +-----------------+
                     |
                     v
             +--------------------+
             |     Nœuds Worker   |
             | kubelet            |
             | Runtime conteneurs |
             | Réseau / Stockage  |
             +--------------------+
```

Les principaux composants sont les suivants.

**kube-apiserver**

C'est le point d'entrée principal de l'API Kubernetes. Il reçoit les requêtes, applique les contrôles d'accès et les contrôles d'admission, puis traite les opérations sur les objets.

**etcd**

Cette base de données distribuée stocke l'état des ressources du cluster. Son intégrité, sa disponibilité, ses sauvegardes et le contrôle de son accès sont des enjeux majeurs.

**kube-scheduler**

Il choisit un nœud pour chaque Pod qui n'est pas encore planifié. Il considère notamment les ressources disponibles, les contraintes d'affinité, les taints, les tolerations et les règles de répartition.

**kube-controller-manager**

Il exécute les contrôleurs qui surveillent des ressources et cherchent à rapprocher l'état observé de l'état désiré. Un contrôleur de Deployment, par exemple, contribue à maintenir le nombre de réplicas attendu.

**kubelet**

Il fonctionne sur chaque nœud et s'assure que les Pods affectés à ce nœud sont exécutés conformément à leur spécification.

**Runtime de conteneurs**

Il exécute les conteneurs, par exemple au moyen de containerd ou d'un autre runtime compatible avec Kubernetes via CRI.

### 3.2. Le principe de réconciliation

Kubernetes est fondé sur un modèle déclaratif.

L'administrateur indique l'état souhaité. Les contrôleurs observent les écarts et tentent de les corriger.

Exemple :

```text
État souhaité : 3 réplicas
État observé  : 3 réplicas

Aucune correction nécessaire.

Un Pod tombe en panne.

État souhaité : 3 réplicas
État observé  : 2 réplicas

Le contrôleur constate l'écart.
Il provoque la création d'un remplaçant.
Le scheduler choisit un nœud.
Le kubelet démarre le nouveau Pod.

État observé après convergence : 3 réplicas
```

Ce mécanisme ne garantit pas que toute panne soit immédiatement corrigée. La réconciliation dépend notamment de la disponibilité du plan de contrôle, des ressources, du réseau, des volumes et des contraintes de planification.

Il faut donc distinguer :

- **État souhaité** : ce qui est demandé dans la configuration.
- **État observé** : ce qui existe réellement.
- **Convergence** : processus par lequel Kubernetes tente de rétablir l'état souhaité.
- **Disponibilité applicative** : capacité réelle du service à répondre aux utilisateurs.

Un Deployment peut afficher trois réplicas disponibles alors qu'une dépendance externe est en panne. L'état des objets Kubernetes n'est pas, à lui seul, une preuve du bon fonctionnement métier.

### 3.3. Inspecter un objet et comprendre son état

```bash
kubectl get deployment -A
kubectl describe deployment mon-application -n production
kubectl get pods -n production -o wide
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get deployment mon-application -n production -o yaml
```

Pour comprendre une ressource, examiner :

- Les spécifications attendues.
- Les labels et sélecteurs.
- Les événements récents.
- Les conditions de statut.
- Les réplicas désirés, disponibles et indisponibles.
- Les erreurs du scheduler, du contrôleur ou du runtime.

Une erreur de configuration peut être acceptée par l'API, puis conduire à un Pod qui ne démarre jamais. L'acceptation d'un manifeste ne prouve donc pas que l'application peut être exécutée.

## 4. Planification avancée des Pods

### 4.1. Comment le scheduler choisit un nœud

Le scheduler examine les nœuds candidats et élimine ceux qui ne satisfont pas les contraintes applicables. Il évalue ensuite les candidats restants et choisit un emplacement.

Les décisions peuvent dépendre :

- Des demandes de CPU et de mémoire.
- Des taints et tolerations.
- Des `nodeSelector` et règles d'affinité.
- Des règles d'affinité et d'anti-affinité entre Pods.
- Des contraintes de répartition topologique.
- Des volumes et des contraintes de zone.
- Des extensions de scheduler et des politiques de placement.

Le scheduler ne déplace pas automatiquement un Pod déjà actif vers un autre nœud simplement parce qu'un nœud semble plus disponible. Le déplacement dépend notamment du cycle de vie du Pod, de contrôleurs ou d'outils supplémentaires.

### 4.2. Requests et limits

Les `requests` décrivent les ressources utilisées pour la planification. Les `limits` imposent une limite d'utilisation applicable par le runtime et le système sous-jacent.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-metier
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-metier
  template:
    metadata:
      labels:
        app: api-metier
    spec:
      containers:
        - name: api
          image: registry.example.com/api-metier:1.0.0
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1"
              memory: "512Mi"
```

Interprétation :

- `250m` représente un quart de CPU logique.
- `1` représente un CPU logique.
- `256Mi` représente 256 mebioctets.
- `512Mi` représente 512 mebioctets.

Il faut dimensionner ces valeurs à partir de mesures. Des demandes trop élevées peuvent empêcher le placement. Des demandes trop faibles peuvent provoquer une densité excessive, de la contention ou des évictions.

Une limite de mémoire trop basse peut provoquer une terminaison du conteneur pour dépassement de mémoire, souvent visible avec la raison `OOMKilled`.

Une limite de CPU peut entraîner une limitation de l'exécution. Cela ne signifie pas nécessairement que le conteneur est arrêté.

### 4.3. Priorité et préemption

Des `PriorityClass` peuvent établir une hiérarchie entre les Pods.

Un Pod de priorité élevée peut, dans certaines conditions, entraîner l'éviction de Pods de priorité inférieure pour libérer des ressources nécessaires à sa planification.

La priorité ne crée pas de capacité physique supplémentaire. Une mauvaise configuration peut dégrader les autres services.

Les priorités doivent être liées à des objectifs opérationnels documentés : services critiques, composants essentiels, tâches différables et traitements non prioritaires.

### 4.4. Taints et tolerations

Un taint peut empêcher certains Pods de s'exécuter sur un nœud. Une toleration permet à un Pod de tolérer le taint correspondant.

Une toleration ne force pas à elle seule le placement sur le nœud. Pour cibler un groupe particulier de nœuds, il faut généralement combiner les mécanismes nécessaires : labels, affinité ou sélecteurs.

Exemple de nœuds spécialisés :

```bash
kubectl label nodes worker-gpu-01 workload=gpu
kubectl taint nodes worker-gpu-01 workload=gpu:NoSchedule
kubectl describe node worker-gpu-01
```

Le Pod prévu pour ce nœud doit disposer de la toleration et d'une contrainte de placement appropriée.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: calcul-gpu
spec:
  nodeSelector:
    workload: gpu
  tolerations:
    - key: workload
      operator: Equal
      value: gpu
      effect: NoSchedule
  containers:
    - name: calcul
      image: registry.example.com/calcul:1.0.0
```

Ces commandes et manifestes sont des exemples de laboratoire. Les labels et taints doivent respecter les conventions du cluster et ne doivent pas être appliqués sans connaître les workloads déjà exécutés sur le nœud.

### 4.5. Répartir les Pods entre les nœuds et les zones

La répartition topologique permet de réduire le risque de concentrer toutes les répliques dans une seule zone de panne.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-resiliente
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-resiliente
  template:
    metadata:
      labels:
        app: api-resiliente
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api-resiliente
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: api-resiliente
      containers:
        - name: api
          image: registry.example.com/api:1.0.0
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
```

`maxSkew` contrôle l'écart de répartition autorisé.

`DoNotSchedule` privilégie le respect strict de la contrainte, au risque de laisser un Pod en attente.

`ScheduleAnyway` autorise une planification moins équilibrée lorsque nécessaire et privilégie, dans son évaluation, les placements qui améliorent la répartition.

La répartition entre zones ne peut fonctionner correctement que si les nœuds possèdent les labels topologiques attendus et si les ressources sont disponibles dans les zones concernées.

### 4.6. Affinité et anti-affinité

L'affinité entre Pods peut encourager leur placement dans un même domaine. L'anti-affinité peut au contraire encourager ou imposer leur séparation.

Exemple de politique de séparation de deux répliques sur un même hôte :

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: api-resiliente
        topologyKey: kubernetes.io/hostname
```

Cette règle doit être placée dans le `spec` du Pod, par exemple dans `spec.template.spec` d'un Deployment.

Elle peut empêcher la planification si le cluster n'a pas assez de nœuds admissibles. Une politique stricte améliore une garantie de séparation, mais peut diminuer la capacité à maintenir le nombre de réplicas en fonctionnement.

## 5. Disponibilité et résilience des applications

### 5.1. Réplicas et haute disponibilité

Plusieurs réplicas ne suffisent pas à garantir une haute disponibilité.

Il faut également considérer :

- La distribution sur des nœuds distincts.
- Les pannes de zone ou de stockage.
- Les mises à jour de l'application.
- Le nombre de réplicas réellement prêts.
- La capacité résiduelle des nœuds.
- La disponibilité des dépendances.
- La durée de démarrage et d'arrêt de l'application.
- La capacité de l'équilibreur de charge et du réseau.

Trois Pods placés sur un seul nœud forment trois réplicas, mais restent vulnérables à une panne de ce nœud.

### 5.2. Readiness, liveness et startup probes

Les sondes ont des responsabilités différentes.

**Readiness probe**

Elle indique si un conteneur est prêt à recevoir du trafic. Un Pod qui n'est pas prêt peut être exclu des endpoints actifs du Service.

**Liveness probe**

Elle vérifie si un conteneur doit être redémarré lorsqu'il semble bloqué ou incapable de fonctionner correctement.

**Startup probe**

Elle laisse à une application longue à démarrer le temps nécessaire avant que les sondes de liveness et de readiness commencent à exercer pleinement leur rôle.

Exemple :

```yaml
containers:
  - name: api
    image: registry.example.com/api:1.0.0
    ports:
      - name: http
        containerPort: 8080
    startupProbe:
      httpGet:
        path: /health/startup
        port: http
      periodSeconds: 5
      failureThreshold: 30
    readinessProbe:
      httpGet:
        path: /health/ready
        port: http
      periodSeconds: 5
      timeoutSeconds: 2
      failureThreshold: 3
    livenessProbe:
      httpGet:
        path: /health/live
        port: http
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
```

Ces chemins sont des exemples. L'application doit réellement fournir les endpoints correspondants.

La readiness doit vérifier si l'application peut prendre en charge du trafic. La liveness doit plutôt détecter un processus bloqué qui nécessite un redémarrage.

Il faut éviter qu'une indisponibilité d'une base de données distante fasse redémarrer en boucle toutes les instances d'une API. Selon l'architecture, cette panne peut nécessiter une alerte et un retrait temporaire du trafic plutôt qu'un redémarrage.

### 5.3. Protéger les interruptions volontaires

Un PodDisruptionBudget (PDB) permet de limiter certaines interruptions volontaires, par exemple celles effectuées pendant une opération de maintenance.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-resiliente
```

Avec cette politique, les opérations volontaires prises en charge par le mécanisme des disruptions doivent préserver au moins deux Pods disponibles si cela est possible.

Un PDB :

- Ne remplace pas les réplicas.
- Ne crée pas de Pods supplémentaires.
- Ne garantit pas qu'une panne matérielle conservera le nombre minimal de Pods.
- Peut bloquer une opération de maintenance si les conditions demandées ne sont pas réunies.
- Ne bloque pas toutes les opérations qui peuvent interrompre une application.

Le budget doit être cohérent avec le nombre de réplicas, leur temps de démarrage et le niveau d'indisponibilité toléré.

### 5.4. Stratégies de mise à jour

Une mise à jour continue remplace progressivement les anciens Pods par de nouveaux Pods.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

Avec les paramètres adaptés au contexte :

- `maxUnavailable: 0` vise à ne pas réduire le nombre de Pods disponibles pendant la mise à jour.
- `maxSurge: 1` autorise un Pod supplémentaire pendant le remplacement.

Cette configuration peut nécessiter de la capacité supplémentaire. Elle ne garantit pas à elle seule une absence d'interruption, car le résultat dépend notamment des sondes, des dépendances, du routage et de la compatibilité entre versions.

Observer une mise à jour :

```bash
kubectl rollout status deployment/api-resiliente -n production
kubectl rollout history deployment/api-resiliente -n production
kubectl describe deployment api-resiliente -n production
```

En cas d'échec :

```bash
kubectl rollout undo deployment/api-resiliente -n production
```

Un retour arrière de Deployment ne restaure pas automatiquement un schéma de base de données, un volume ou un état métier modifié par la nouvelle version.

### 5.5. Autoscaling horizontal

Le HorizontalPodAutoscaler ajuste le nombre de réplicas d'un workload selon des métriques configurées.

Exemple :

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-resiliente-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-resiliente
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

Pour que cette cible CPU soit calculée correctement, les conteneurs concernés doivent disposer de `requests.cpu`, et une source de métriques opérationnelle doit être disponible.

L'auto-scaling des Pods n'est pas synonyme d'auto-scaling des nœuds. Si le cluster n'a pas la capacité nécessaire, les nouveaux Pods peuvent rester en attente.

Il faut également prendre en compte :

- Le délai avant qu'une charge soit détectée.
- Le temps de démarrage de l'application.
- La capacité des services en aval.
- Les limites de connexion aux bases de données.
- Les métriques adaptées au type de charge.
- Les paramètres de stabilisation de l'autoscaler.

Une augmentation automatique du nombre de Pods ne corrige pas une saturation provoquée par une dépendance unique.

## 6. Gestion avancée des ressources

### 6.1. ResourceQuota

Une ResourceQuota limite la consommation ou la création de certaines ressources dans un namespace.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-equipe
  namespace: equipe-a
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 16Gi
    limits.cpu: "16"
    limits.memory: 32Gi
    pods: "40"
    persistentvolumeclaims: "10"
    requests.storage: 200Gi
```

Cette configuration est illustrative. Les besoins réels, les ressources disponibles et les éventuelles politiques de la plateforme doivent guider les valeurs choisies.

Une quota ne réserve pas automatiquement les ressources physiques indiquées. Elle encadre la consommation déclarée et la création de ressources dans le namespace.

### 6.2. LimitRange

Une LimitRange permet de définir des valeurs par défaut, des minimums et des maximums applicables à certaines ressources.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limites-conteneurs
  namespace: equipe-a
spec:
  limits:
    - type: Container
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      default:
        cpu: "500m"
        memory: "512Mi"
      min:
        cpu: "50m"
        memory: "64Mi"
      max:
        cpu: "2"
        memory: "2Gi"
```

La ResourceQuota et la LimitRange remplissent des rôles complémentaires :

```text
LimitRange
    |
    +--> Encadre ou complète les ressources d'un objet
    |
    v
ResourceQuota
    |
    +--> Limite la consommation déclarée du namespace
    |
    v
Nœuds du cluster
    |
    +--> Doivent disposer de la capacité physique nécessaire
```

Une configuration incohérente peut empêcher la création des Pods ou entraîner leur placement difficile.

### 6.3. Éviter les problèmes de capacité

Exemples de symptômes :

- `Pending` : aucune planification possible ou un autre prérequis n'est pas satisfait.
- `OOMKilled` : arrêt lié à un dépassement mémoire.
- `Evicted` : éviction du Pod, par exemple sous pression sur le nœud.
- Forte limitation CPU : charge qui progresse lentement malgré un Pod actif.
- Échec d'autoscaling : impossibilité de trouver suffisamment de capacité.

Commandes :

```bash
kubectl describe pod nom-du-pod -n production
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl top pods -n production
kubectl top nodes
kubectl describe node nom-du-noeud
kubectl get resourcequota,limitrange -n production
```

Les commandes `top` affichent des métriques d'utilisation observées, pas toutes les données nécessaires à une analyse de capacité. Pour une exploitation durable, il faut suivre des historiques, les tendances et les taux d'échec de placement.

## 7. Modèle de sécurité Kubernetes

### 7.1. Une sécurité en profondeur

La sécurité Kubernetes ne se réduit pas aux paramètres des conteneurs. Elle s'organise en plusieurs couches.

```text
+------------------------------------------------------+
| Identité des administrateurs, développeurs et CI/CD  |
+------------------------------------------------------+
| Authentification, autorisation RBAC, MFA selon IAM    |
+------------------------------------------------------+
| API Kubernetes, admission, audit et politiques        |
+------------------------------------------------------+
| Namespaces, ServiceAccounts et isolation des Pods     |
+------------------------------------------------------+
| NetworkPolicies, DNS, Services et trafic externe      |
+------------------------------------------------------+
| Images, dépendances, SBOM et pipeline de build        |
+------------------------------------------------------+
| Runtime, noyau Linux, nœuds et isolation               |
+------------------------------------------------------+
| Stockage, clés de chiffrement, sauvegardes             |
+------------------------------------------------------+
```

Une défaillance dans une couche doit être contenue autant que possible par les autres.

Exemple : un conteneur vulnérable ne devrait pas disposer automatiquement de droits d'administration du cluster, d'un accès à tous les Secrets ni de la possibilité de communiquer librement avec les autres charges de travail.

### 7.2. Identifier les frontières de confiance

Avant d'ajouter des règles de sécurité, identifier :

- Les personnes autorisées à administrer le cluster.
- Les comptes de service utilisés par les applications.
- Les namespaces qui appartiennent aux différentes équipes.
- Les registres d'images acceptés.
- Les systèmes qui conservent les Secrets.
- Les dépendances réseau et les destinations externes.
- Les workloads qui ont réellement besoin d'accéder au système hôte.
- Les données qui doivent être protégées au repos et en transit.

Les privilèges doivent être accordés selon un besoin opérationnel documenté, plutôt que par commodité.

## 8. Authentification, autorisation et RBAC

### 8.1. Les trois notions à distinguer

**Authentification :** qui effectue la requête ?

**Autorisation :** cette identité est-elle autorisée à réaliser cette action sur cette ressource ?

**Admission :** la requête autorisée peut-elle être acceptée selon les politiques appliquées à l'objet ?

Exemple :

```text
Utilisateur
    |
    v
Authentification
    |
    v
Autorisation RBAC
    |
    v
Contrôles d'admission
    |
    v
Validation et traitement de la requête
    |
    v
État du cluster
```

Cette représentation est simplifiée. Le traitement API comporte d'autres contrôles, et l'ordre détaillé dépend du chemin de traitement de la requête.

### 8.2. Role, ClusterRole et bindings

Un `Role` définit des permissions dans un namespace.

Un `RoleBinding` attribue des permissions dans un namespace à un utilisateur, un groupe ou un ServiceAccount. Il peut référencer un `Role` ou un `ClusterRole`, mais le binding conserve une portée limitée à son namespace.

Un `ClusterRole` définit des permissions à l'échelle du cluster ou réutilisables dans différents namespaces.

Un `ClusterRoleBinding` accorde les permissions du `ClusterRole` à l'échelle du cluster.

### 8.3. Exemple de rôle de lecture limité

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: equipe-a
  labels:
    environnement: test
```

Un compte de service peut recevoir un rôle de lecture sur certaines ressources non confidentielles :

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: observateur
  namespace: equipe-a
automountServiceAccountToken: false
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: lecture-application
  namespace: equipe-a
rules:
  - apiGroups: ["", "apps"]
    resources:
      - pods
      - pods/log
      - services
      - deployments
      - replicasets
    verbs:
      - get
      - list
      - watch
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: observateur-lecture
  namespace: equipe-a
subjects:
  - kind: ServiceAccount
    name: observateur
    namespace: equipe-a
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: lecture-application
```

L'ensemble peut être enregistré dans un fichier manifeste puis appliqué dans le cluster de laboratoire :

```bash
kubectl apply -f rbac-observateur.yaml
```

L'exemple omet volontairement l'accès aux Secrets et les droits d'écriture.

### 8.4. Vérifier les autorisations

Vérifier l'identité utilisée :

```bash
kubectl config current-context
kubectl auth whoami
```

Vérifier les droits de l'utilisateur courant :

```bash
kubectl auth can-i get pods -n equipe-a
kubectl auth can-i delete deployments -n equipe-a
kubectl auth can-i get secrets -n equipe-a
```

Vérifier les droits d'un ServiceAccount précis :

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:equipe-a:observateur \
  -n equipe-a
```

L'option `--as` nécessite que l'identité utilisée par l'opérateur dispose du droit d'impersonation approprié. Elle ne doit pas être utilisée pour contourner les contrôles d'accès.

### 8.5. Les permissions dangereuses

Les droits suivants demandent une analyse approfondie :

- `cluster-admin`.
- `create` sur les Pods ou sur les workloads qui en produisent.
- `create` ou `patch` sur les ressources de contrôleurs.
- `get`, `list` ou `watch` sur les Secrets.
- La création ou modification de RoleBindings et ClusterRoleBindings.
- L'impersonation d'autres identités.
- La gestion de ressources qui peuvent ouvrir un accès à l'hôte.

Attention : un droit permettant de créer un Deployment peut indirectement permettre de monter un Secret dans un Pod ou de lancer un conteneur avec des options sensibles. Les règles RBAC ne représentent pas toujours toutes les conséquences indirectes d'une action.

Il ne suffit donc pas de masquer le droit `get secrets` si l'utilisateur peut créer sans restriction des Pods capables de lire ces mêmes Secrets.

### 8.6. ServiceAccounts et jetons

Chaque namespace possède un ServiceAccount `default`. Il ne doit pas être utilisé par toutes les applications par simple commodité.

Une application qui n'a pas besoin d'accéder à l'API Kubernetes devrait éviter de recevoir inutilement un jeton d'accès.

Dans un Pod, on peut désactiver le montage automatique du jeton :

```yaml
spec:
  automountServiceAccountToken: false
  containers:
    - name: application
      image: registry.example.com/application:1.0.0
```

Si l'accès à l'API est nécessaire, créer une identité dédiée et lui accorder uniquement les droits indispensables.

Les clusters Kubernetes modernes peuvent utiliser des jetons de ServiceAccount de courte durée, projetés et renouvelés selon les mécanismes disponibles. Éviter les anciens jetons longue durée conservés sans justification.

## 9. Pod Security Standards et Pod Security Admission

### 9.1. Les profils de sécurité

Kubernetes définit trois profils de Pod Security Standards.

**Privileged**

Profil largement permissif, adapté uniquement à certains workloads d'infrastructure qui nécessitent des capacités particulières et font l'objet d'une analyse de risque.

**Baseline**

Profil destiné à interdire plusieurs configurations connues pour permettre des élévations de privilèges, tout en conservant une compatibilité plus large.

**Restricted**

Profil plus strict, fondé sur les bonnes pratiques de durcissement des Pods et des conteneurs.

Le profil `Restricted` implique notamment des exigences sur l'exécution sans root, les capabilities Linux et seccomp, ainsi que des limitations sur les volumes et les configurations privilégiées.

### 9.2. Appliquer les contrôles à un namespace

Exemple pour un namespace de production :

```bash
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted \
  --overwrite
```

Les trois modes ont des objectifs différents :

- `enforce` : rejette les créations ou modifications de Pods qui ne respectent pas le profil appliqué.
- `audit` : consigne les violations dans les informations d'audit, selon la configuration de cette fonctionnalité.
- `warn` : affiche un avertissement au client lors d'une opération concernée.

Cette politique peut refuser des workloads existants lorsqu'ils sont recréés ou modifiés. Elle ne transforme pas automatiquement leurs conteneurs en conteneurs sécurisés.

Pour un cluster existant, commencer par mesurer les violations, identifier les applications incompatibles, corriger leurs manifestes, puis activer progressivement l'application stricte.

### 9.3. Utilisation pratique

```bash
kubectl get namespaces --show-labels
kubectl describe namespace production
kubectl apply --dry-run=server -f deployment.yaml
```

Le mode `--dry-run=server` permet de vérifier la requête auprès du serveur sans enregistrer la ressource. Il peut ainsi révéler un rejet de politique d'admission.

La vérification peut néanmoins différer du résultat réel si des autorisations, politiques ou conditions changent entre les deux opérations.

## 10. Durcissement des conteneurs

### 10.1. Exécuter sans root

Un utilisateur non privilégié limite les conséquences de certaines vulnérabilités applicatives.

Exemple :

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  seccompProfile:
    type: RuntimeDefault
```

L'image utilisée doit permettre l'exécution sous cet UID et ce GID. Les fichiers et répertoires nécessaires à l'application doivent disposer des permissions adéquates.

Le fait de définir un UID non nul ne corrige pas une image vulnérable, un accès excessif au réseau ou des droits RBAC trop larges. Il s'agit d'une couche de sécurité supplémentaire.

### 10.2. Réduire les capacités Linux

Les capabilities Linux découpent certaines opérations historiquement associées au superutilisateur en privilèges distincts.

Pour une application classique, il est généralement préférable de retirer toutes les capabilities puis de n'ajouter que celles dont le besoin est démontré.

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

Une application qui doit écouter sur un port privilégié ou effectuer une opération système particulière peut nécessiter une configuration différente. Cette exception doit être justifiée.

### 10.3. Réduire la surface modifiable

Un système de fichiers racine en lecture seule limite les modifications persistantes réalisées depuis le conteneur.

```yaml
securityContext:
  readOnlyRootFilesystem: true
```

Si l'application doit écrire dans un répertoire temporaire :

```yaml
volumes:
  - name: tmp
    emptyDir:
      sizeLimit: 128Mi
containers:
  - name: application
    image: registry.example.com/application:1.0.0
    volumeMounts:
      - name: tmp
        mountPath: /tmp
```

Le `emptyDir` fournit un espace de travail temporaire lié au cycle de vie du Pod. Il ne constitue pas un stockage durable. Sans autre configuration, son contenu peut être perdu lorsque le Pod disparaît.

### 10.4. Exemple complet de Pod durci

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: application-durcie
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: application-durcie
  template:
    metadata:
      labels:
        app: application-durcie
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: application
          image: registry.example.com/application:1.0.0
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
          readinessProbe:
            httpGet:
              path: /health/ready
              port: http
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health/live
              port: http
            periodSeconds: 10
            failureThreshold: 3
      volumes:
        - name: tmp
          emptyDir:
            sizeLimit: 64Mi
```

Cet exemple doit être adapté à l'application réelle, en particulier aux chemins des sondes, aux fichiers nécessaires, à la gestion des certificats et aux éventuels répertoires d'écriture.

Un conteneur qui nécessite réellement un accès privilégié à l'hôte doit être isolé et traité comme une exception d'architecture, et non comme la configuration normale d'une application métier.

## 11. Protection du plan de contrôle et des nœuds

### 11.1. Accès à l'API

L'API Kubernetes représente une frontière de confiance majeure.

Les mesures de protection comprennent :

- Des identités individuelles pour les opérateurs.
- Des droits RBAC limités.
- Des mécanismes d'authentification forts lorsque l'environnement les prend en charge.
- La protection des fichiers de configuration client et de leurs certificats.
- Un contrôle des accès réseau au point d'entrée de l'API.
- L'utilisation de TLS.
- La collecte des événements d'audit.
- La rotation et la révocation des identifiants compromis.
- La limitation et la surveillance des accès aux machines du plan de contrôle.

Ne jamais distribuer une configuration administrative de cluster à tous les développeurs ou à des pipelines non maîtrisés.

### 11.2. Kubelet et accès au nœud

Le kubelet dispose d'un accès important au nœud, aux Pods et aux opérations du runtime.

La configuration de production doit notamment :

- Activer une authentification et une autorisation adaptées sur le kubelet.
- Éviter l'exposition non nécessaire de ses endpoints.
- Restreindre les accès réseau administratifs.
- Protéger les certificats et les identifiants de nœuds.
- Maintenir le système d'exploitation et le runtime à jour.
- Contrôler les services accessibles depuis les Pods.
- Protéger les répertoires et sockets du runtime.

Ne pas supposer que la restriction RBAC d'un utilisateur Kubernetes protège automatiquement les interfaces d'administration système du nœud.

### 11.3. Séparer les droits de nœud et les droits Kubernetes

Les droits root sur un nœud peuvent permettre un contrôle très important sur les conteneurs locaux et sur des données sensibles accessibles à ce nœud.

Un accès administrateur au système d'exploitation doit donc être traité comme un accès de niveau élevé.

Les mesures de défense incluent :

- Une administration système centralisée.
- Une journalisation des accès privilégiés.
- Une gestion sécurisée des clés.
- Des mises à jour contrôlées.
- Un contrôle des modules noyau et des services.
- Une surveillance de l'intégrité.
- Des procédures documentées de remplacement ou de réinstallation d'un nœud suspect.

## 12. Secrets, chiffrement et gestion des identités

### 12.1. Ce qu'est un Secret Kubernetes

Un objet `Secret` fournit un mécanisme Kubernetes pour stocker et distribuer des données sensibles.

Exemples :

- Mot de passe.
- Jeton d'accès.
- Clé privée.
- Certificat client.
- Identifiant d'authentification.

Un Secret n'est pas automatiquement une donnée chiffrée partout où elle circule ou est stockée.

L'encodage Base64 utilisé dans certains manifestes n'est pas du chiffrement. Toute personne ayant accès à la valeur encodée peut généralement la décoder.

### 12.2. Créer et utiliser un Secret

Dans un laboratoire :

```bash
kubectl create secret generic connexion-db \
  --from-literal=username=application \
  --from-literal=password='MotDePasseDeLaboratoire' \
  -n production
```

La chaîne utilisée ici est uniquement illustrative. Pour un vrai secret, préférer une source de secrets adaptée et éviter les valeurs sensibles dans l'historique du terminal, les scripts, les journaux ou les dépôts de code.

L'application peut recevoir les valeurs en variables d'environnement :

```yaml
env:
  - name: DB_USERNAME
    valueFrom:
      secretKeyRef:
        name: connexion-db
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: connexion-db
        key: password
```

Une autre possibilité consiste à monter le Secret dans un volume. Le mode de distribution doit être choisi en fonction des besoins et des risques de l'application.

### 12.3. Bonnes pratiques sur les Secrets

- Restreindre les droits de lecture des Secrets.
- Ne pas inscrire de données sensibles dans Git.
- Éviter l'accès aux Secrets pour les workloads qui n'en ont pas besoin.
- Ne pas écrire les valeurs des Secrets dans les logs.
- Restreindre les personnes et services capables de créer des Pods.
- Contrôler l'accès aux sauvegardes et aux exports d'objets Kubernetes.
- Prévoir une rotation des identifiants.
- Utiliser une solution de gestion des secrets externe lorsqu'elle apporte un contrôle approprié.
- Vérifier le comportement des volumes et des applications lors d'une rotation.

Une valeur sensible placée dans un fichier manifeste peut être exposée même si le dépôt est privé. Le contrôle d'accès au dépôt ne remplace pas une gestion adéquate du cycle de vie des secrets.

### 12.4. Chiffrement au repos

Les données enregistrées dans etcd ne sont pas automatiquement protégées par le simple fait qu'elles sont représentées par un objet Secret.

Il faut distinguer :

- Le chiffrement des communications TLS.
- Le chiffrement des ressources enregistrées par l'API dans etcd.
- Le chiffrement du disque ou du système de fichiers qui héberge etcd.
- Le chiffrement des volumes persistants utilisés par les applications.
- Le chiffrement effectué par l'application elle-même.

Le chiffrement au repos des ressources de l'API doit être configuré selon la plateforme. Dans une plateforme administrée, le fournisseur peut exposer des paramètres spécifiques. Pour un cluster autogéré, la configuration de l'API server et la gestion des clés doivent être traitées explicitement.

Une stratégie correcte doit définir :

1. L'algorithme et le mécanisme de chiffrement pris en charge.
2. L'emplacement et la protection des clés.
3. Les procédures de rotation.
4. Les droits d'accès aux clés.
5. Le comportement des sauvegardes.
6. La procédure de restauration.
7. Le traitement des anciennes données déjà stockées.

Activer une configuration de chiffrement n'entraîne pas nécessairement le rechiffrement immédiat de toutes les données existantes. Cette opération doit être planifiée et vérifiée.

### 12.5. Pourquoi les sauvegardes compliquent la sécurité

Une sauvegarde peut contenir des Secrets, des configurations réseau, des certificats et des informations qui révèlent l'architecture du cluster.

Une sauvegarde chiffrée n'est utile que si :

- Sa clé de déchiffrement est disponible de façon contrôlée.
- Son accès est limité.
- Elle n'est pas modifiable par les mêmes identités qui gèrent le cluster en fonctionnement.
- Son intégrité est vérifiée.
- Sa restauration a été testée.

La politique de sécurité doit couvrir à la fois les données en production et leurs copies de sauvegarde.

## 13. Sécurité réseau et NetworkPolicies

### 13.1. Pourquoi segmenter les communications

Dans de nombreux environnements, des Pods peuvent communiquer librement si aucune politique ne limite le trafic et si le plugin réseau applique le comportement attendu.

Cette liberté facilite les tests, mais augmente les possibilités de déplacement latéral lorsqu'une application est compromise.

Une architecture segmentée peut suivre les flux suivants :

```text
                    TRAFIC EXTERNE
                          |
                          v
                  +---------------+
                  | Ingress / LB  |
                  +-------+-------+
                          |
                          v
                  +---------------+
                  | Frontend      |
                  +-------+-------+
                          |
                          v
                  +---------------+
                  | API métier    |
                  +-------+-------+
                          |
                          v
                  +---------------+
                  | Base de       |
                  | données       |
                  +---------------+
```

La base de données ne devrait pas accepter le trafic de tous les Pods du cluster si elle ne sert qu'une API spécifique.

### 13.2. Conditions de fonctionnement des NetworkPolicies

Il faut distinguer la ressource Kubernetes `NetworkPolicy` et la mise en application réelle des règles par le réseau du cluster.

La capacité d'application dépend du plugin CNI. Une politique peut être acceptée par l'API même si l'environnement réseau ne prend pas en charge son application.

Les NetworkPolicies Kubernetes standard permettent principalement de filtrer le trafic TCP, UDP et, si l'implémentation le prend en charge, SCTP. Elles ne remplacent pas un pare-feu complet ni tous les contrôles de niveau applicatif.

### 13.3. Refuser par défaut

Pour isoler le trafic entrant et sortant dans un namespace :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: refus-par-defaut
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

Cette politique ne remplace pas les autres règles d'autorisation nécessaires. Lorsque plusieurs NetworkPolicies sélectionnent les mêmes Pods, les autorisations applicables sont combinées selon les règles Kubernetes.

Un refus par défaut peut interrompre des communications légitimes, notamment DNS, accès à une API externe, accès à un service de métriques ou connexion à un système d'identité.

Il faut donc construire les autorisations nécessaires et les vérifier avant de l'appliquer à une application critique.

### 13.4. Autoriser DNS

Exemple d'autorisation DNS vers les Pods du namespace système identifiés par le label indiqué :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: autoriser-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

Les labels des Pods DNS diffèrent selon les distributions et les installations. Il faut examiner les Pods DNS réels, leur namespace, leur adresse et leur fonctionnement avant d'utiliser cette règle.

```bash
kubectl get pods -n kube-system --show-labels
kubectl get services -n kube-system
cat /etc/resolv.conf
```

Le dernier fichier concerne le conteneur ou l'environnement dans lequel la commande est exécutée. Il ne représente pas nécessairement la configuration du DNS d'un Pod particulier.

### 13.5. Exemple de communication entre API et base de données

Supposons que les Pods API utilisent le label `app: api-metier` et que les Pods de base de données utilisent `app: base-donnees`, dans le namespace `production`.

La politique suivante permet au trafic provenant de l'API d'atteindre les Pods de base de données sur le port TCP 5432 :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: acces-db-depuis-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: base-donnees
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-metier
      ports:
        - protocol: TCP
          port: 5432
```

Cette politique autorise le flux entrant correspondant. Elle ne constitue pas à elle seule une politique complète de sortie, une authentification à la base de données ou un chiffrement TLS.

Le trafic autorisé doit également correspondre au port réellement utilisé par la base de données.

### 13.6. Exemple de sortie limitée de l'API

Une API peut devoir joindre :

- Le DNS du cluster.
- Une base de données.
- Un service externe explicitement autorisé.
- Un fournisseur d'identité ou un endpoint de télémétrie.

Il vaut mieux établir une liste de dépendances et de destinations nécessaires plutôt que d'autoriser immédiatement tout le trafic sortant.

Les règles qui filtrent les adresses IP externes doivent tenir compte des changements d'adresses, de l'emploi éventuel de proxys et du fonctionnement des services cloud. Une politique basée sur une IP temporaire peut devenir incorrecte sans modifier le manifeste.

### 13.7. Vérifier la segmentation

Pour diagnostiquer une communication :

```bash
kubectl get networkpolicies -A
kubectl describe networkpolicy autoriser-dns -n production
kubectl get pods -n production -o wide
kubectl get svc -n production
```

Tester ensuite la résolution DNS et la connexion depuis un Pod de test autorisé.

Le diagnostic doit distinguer les cas suivants :

- Échec de résolution DNS.
- Service sans endpoint.
- Mauvais port ou mauvaise adresse.
- Application qui n'écoute pas.
- NetworkPolicy qui refuse le flux.
- Pare-feu externe ou règle de routage.
- Problème TLS ou d'authentification applicative.

Ne pas désactiver globalement les politiques réseau pour résoudre un problème dont la cause n'a pas été identifiée.

## 14. Admission et gouvernance des workloads

### 14.1. Rôle des contrôles d'admission

Les contrôles d'admission interviennent lors du traitement des requêtes adressées à l'API Kubernetes.

Ils peuvent notamment contribuer à :

- Refuser certaines configurations.
- Appliquer des exigences organisationnelles.
- Empêcher des images provenant de registres interdits.
- Garantir la présence de paramètres obligatoires.
- Valider des attributs de sécurité.
- Ajouter des valeurs ou des champs via des mécanismes de mutation adaptés.

Le contrôle d'admission est particulièrement utile lorsque des règles doivent être appliquées à toutes les équipes et ne peuvent pas reposer uniquement sur la bonne volonté des développeurs.

### 14.2. Pod Security Admission et règles spécifiques

Le Pod Security Admission intégré permet d'appliquer les profils Pod Security Standards à des namespaces.

Pour des besoins plus spécifiques, Kubernetes propose également des ValidatingAdmissionPolicies qui utilisent CEL pour exprimer certaines conditions de validation. Des solutions de l'écosystème, telles que Kyverno ou OPA Gatekeeper, peuvent fournir d'autres formes de politique.

Il faut choisir le mécanisme selon les besoins, les compétences opérationnelles, la maintenance et la compatibilité avec la version du cluster.

### 14.3. Exemple de validation d'un registre

L'exemple suivant illustre une politique qui exige que les conteneurs ordinaires d'un Pod utilisent des images dont le nom commence par `registry.example.com/`.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: registre-approuve
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
  validations:
    - expression: "object.spec.containers.all(c, c.image.startsWith('registry.example.com/'))"
      message: "Les conteneurs doivent utiliser le registre approuve."
      reason: Forbidden
```

Pour que la politique soit appliquée, il faut également la lier à une `ValidatingAdmissionPolicyBinding`.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: registre-approuve-binding
spec:
  policyName: registre-approuve
  validationActions:
    - Deny
```

Ces exemples sont des points de départ, pas une politique de production complète.

Avant de l'utiliser, il faut notamment :

- Adapter le registre à l'environnement réel.
- Gérer les init containers et, si nécessaire, les ephemeral containers.
- Déterminer quels namespaces sont concernés.
- Vérifier les images des composants d'infrastructure.
- Tester les comportements de création et de mise à jour.
- Prévoir le processus de dérogation autorisée.
- Éviter une règle qui bloquerait une opération critique sans procédure de récupération.

Une politique sur les images peut être complétée par la vérification des digests, la signature des artefacts et une stratégie de mise à jour du catalogue d'images autorisées.

## 15. Sécurité de la chaîne d'approvisionnement logicielle

### 15.1. Le cycle de vie d'une image

La sécurité de l'image doit être envisagée depuis le code source jusqu'au déploiement.

```text
Code source
    |
    v
Dépendances déclarées
    |
    v
Pipeline de build contrôlé
    |
    v
Construction de l'image
    |
    v
Analyse des vulnérabilités
    |
    v
SBOM et provenance
    |
    v
Publication dans le registre
    |
    v
Vérification des artefacts
    |
    v
Déploiement Kubernetes
    |
    v
Surveillance et gestion des vulnérabilités
```

Aucune étape ne garantit à elle seule qu'une image est sûre. Une analyse sans vulnérabilité connue ne prouve pas l'absence de défauts.

### 15.2. Réduire la surface de l'image

Bonnes pratiques :

- Utiliser une image de base adaptée et régulièrement maintenue.
- Préférer les images minimales lorsque leur compatibilité a été vérifiée.
- Réduire les paquets et outils présents dans l'image finale.
- Éviter les secrets dans les couches d'image et les fichiers de build.
- Construire les artefacts dans un environnement contrôlé.
- Utiliser des versions et digests immuables lorsque le processus le permet.
- Analyser les dépendances et les images avec des outils maintenus.
- Documenter le processus de reconstruction et de mise à jour.

Une image minimale n'est pas automatiquement sûre. Il reste nécessaire d'appliquer les mises à jour, de maîtriser les dépendances et de vérifier la configuration d'exécution.

### 15.3. Tags et digests

Un tag comme `application:1.4.0` est un nom lisible utilisé pour référencer une image. Le tag peut être modifié pour pointer vers un autre contenu.

Un digest identifie un contenu d'image par son empreinte cryptographique.

Exemple conceptuel :

```text
registry.example.com/application:1.4.0
registry.example.com/application@sha256:<digest>
```

Le digest améliore la reproductibilité du déploiement. Il ne prouve pas en lui-même l'identité de l'auteur, la fiabilité de la source ou l'absence de vulnérabilités.

### 15.4. SBOM et provenance

Une SBOM, ou Software Bill of Materials, décrit les composants logiciels contenus dans un artefact.

La provenance fournit des informations sur la manière dont un artefact a été produit, selon le format et le système utilisés.

Ces informations peuvent aider à déterminer :

- Les images qui contiennent une bibliothèque vulnérable.
- Le pipeline qui a produit un artefact.
- Les sources utilisées pour construire l'image.
- Les applications qui doivent être reconstruites après une alerte de sécurité.
- Les différences entre deux versions d'une image.

Les attestations ne sont utiles que si elles sont protégées contre la falsification et vérifiées par le système qui prend les décisions de déploiement.

### 15.5. Secrets de build

Ne jamais incorporer un jeton de registre, une clé privée ou un mot de passe dans une instruction d'image qui les laisse dans une couche ou dans un artefact de build.

Les systèmes de build modernes proposent des mécanismes de transmission temporaire des secrets pendant la construction.

Ces mécanismes doivent être utilisés avec un pipeline fiable, des journaux contrôlés et des permissions limitées.

### 15.6. Réduire les risques dans le pipeline CI/CD

Le pipeline doit disposer uniquement des droits nécessaires à l'opération qu'il effectue.

Il faut séparer, quand cela est pertinent :

- La construction des artefacts.
- L'analyse de sécurité.
- La publication d'images.
- La signature et l'attestation.
- Le déploiement en test.
- Le déploiement en production.

Un pipeline de compilation ne devrait pas recevoir automatiquement des droits d'administration complets sur Kubernetes.

Les identifiants doivent être courts ou renouvelables lorsque cela est possible, et leur exposition dans les journaux, variables ou artefacts doit être contrôlée.

## 16. Journaux d'audit Kubernetes

### 16.1. Pourquoi l'audit est important

Les journaux d'audit permettent de retracer les requêtes effectuées sur l'API Kubernetes.

Ils peuvent contribuer à répondre à des questions comme :

- Qui a modifié un Deployment ?
- Quand un Secret a-t-il été consulté ?
- Quelle identité a créé un RoleBinding ?
- Une ressource a-t-elle été supprimée ?
- Quelle opération a précédé un incident ?

Les logs applicatifs et les événements Kubernetes ne remplacent pas l'audit des requêtes à l'API.

### 16.2. Politiques d'audit

Le mécanisme d'audit peut être configuré pour enregistrer les événements avec différents niveaux de détail, selon le type de ressource et l'action.

Les niveaux usuels incluent :

- `None` : ne pas enregistrer l'événement.
- `Metadata` : enregistrer les métadonnées pertinentes de la requête.
- `Request` : enregistrer également le contenu de la requête.
- `RequestResponse` : enregistrer le contenu de la requête et de la réponse.

Un niveau plus détaillé augmente les besoins de stockage et peut entraîner l'exposition de données sensibles. Il faut donc définir le niveau en fonction du risque et des obligations de traçabilité.

### 16.3. Exemple de politique d'audit

Le manifeste suivant est un exemple destiné à illustrer les niveaux d'audit. Il doit être adapté avant d'être utilisé sur un véritable plan de contrôle.

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - RequestReceived
rules:
  - level: None
    users:
      - system:kube-proxy
    verbs:
      - watch
    resources:
      - group: ""
        resources:
          - endpoints
          - services

  - level: Metadata
    resources:
      - group: ""
        resources:
          - secrets
          - configmaps

  - level: Metadata
    resources:
      - group: ""
        resources:
          - pods
          - pods/log

  - level: Metadata
    verbs:
      - create
      - update
      - patch
      - delete
    resources:
      - group: rbac.authorization.k8s.io
        resources:
          - roles
          - rolebindings
          - clusterroles
          - clusterrolebindings

  - level: Metadata
```

Cette configuration sert à expliquer le principe de sélection des règles. L'ordre des règles, les identités réellement utilisées par le cluster, les volumes d'événements et les obligations de sécurité doivent être étudiés avant toute adoption. Les règles plus générales s'appliquent aux événements qui ne correspondent pas aux règles précédentes.

La politique doit ensuite être configurée sur l'API server selon le mode d'exploitation du cluster. Sur une plateforme administrée, l'accès à cette configuration peut être limité ou remplacé par les fonctionnalités d'audit du fournisseur.

### 16.4. Protéger les journaux

Une bonne stratégie comprend :

- La collecte centralisée des logs d'audit.
- Une durée de conservation adaptée.
- Des accès en lecture et administration distincts.
- Une protection contre l'altération.
- Une synchronisation horaire fiable.
- Des alertes sur les opérations sensibles.
- Un traitement explicite des données confidentielles.
- Une procédure d'investigation documentée.

Les journaux ne doivent pas être accessibles sans restriction à toutes les charges de travail. Ils peuvent contenir des métadonnées d'identité et de configuration utiles à un attaquant.

## 17. Observabilité et diagnostic avancé

### 17.1. Les trois catégories de données

**Métriques**

Elles indiquent des valeurs mesurables dans le temps : CPU, mémoire, latence, nombre de requêtes, erreurs et disponibilité.

**Logs**

Ils décrivent des événements ou des messages émis par les applications et les composants.

**Traces**

Elles permettent de suivre le parcours d'une requête à travers différents services et de localiser des temps d'attente ou des erreurs dans un système distribué.

Ces données sont complémentaires. Une hausse de latence peut être visible dans une métrique, expliquée par un log et localisée dans une trace.

### 17.2. Vérifier la disponibilité des Pods

```bash
kubectl get pods -A
kubectl get deploy,rs,sts -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl top pods -A
kubectl top nodes
```

Pour un Pod particulier :

```bash
kubectl describe pod nom-du-pod -n production
kubectl logs nom-du-pod -n production
kubectl logs nom-du-pod -n production --previous
kubectl get pod nom-du-pod -n production -o yaml
```

`--previous` peut afficher les journaux de l'instance de conteneur précédente lorsque le conteneur a été redémarré et que ces logs sont encore accessibles.

### 17.3. Diagnostic d'un Pod en Pending

Procédure :

1. Examiner les événements du Pod.
2. Vérifier les demandes CPU et mémoire.
3. Examiner les quotas et limites du namespace.
4. Vérifier les taints et tolerations.
5. Vérifier `nodeSelector`, affinités et contraintes topologiques.
6. Examiner les contraintes liées aux volumes.
7. Vérifier que le cluster dispose de nœuds admissibles.

```bash
kubectl describe pod nom-du-pod -n production
kubectl get nodes
kubectl describe node nom-du-noeud
kubectl get resourcequota,limitrange -n production
```

Ne pas supprimer immédiatement le Pod : les informations de diagnostic sont souvent plus faciles à comprendre tant que l'objet et ses événements sont présents.

### 17.4. Diagnostic d'un CrashLoopBackOff

`CrashLoopBackOff` indique que le conteneur échoue à démarrer ou à rester en fonctionnement et que Kubernetes augmente le délai entre des tentatives de redémarrage.

Ce n'est pas la cause de l'erreur.

Examiner :

- Les logs actuels et précédents.
- Le code de sortie.
- Les variables de configuration.
- Les montages et permissions des fichiers.
- La disponibilité des dépendances.
- Les sondes et leurs paramètres.
- Les limites de ressources.
- Les modifications récentes de l'image ou de la configuration.

```bash
kubectl logs nom-du-pod -n production --previous
kubectl describe pod nom-du-pod -n production
kubectl get pod nom-du-pod -n production -o jsonpath='{.status.containerStatuses[*].lastState}'
```

La correction doit être basée sur la cause réelle : une permission incorrecte, une configuration invalide, une dépendance indisponible ou un dépassement mémoire ne nécessitent pas les mêmes actions.

### 17.5. Diagnostic d'un Service inaccessible

Vérifier successivement :

```bash
kubectl get svc -n production
kubectl describe svc api-service -n production
kubectl get endpointslice -n production
kubectl get pods -n production --show-labels
```

Les erreurs fréquentes sont :

- Le sélecteur du Service ne correspond pas aux labels des Pods.
- Les Pods ne sont pas prêts.
- Le port du Service est incorrect.
- Le `targetPort` ne correspond pas au port d'écoute.
- Une NetworkPolicy bloque le trafic.
- L'application n'écoute que sur une interface locale.
- Le DNS, le routage ou le pare-feu est incorrect.

Un Service créé avec succès peut ne posséder aucun endpoint utilisable.

### 17.6. Diagnostiquer l'API et les composants du cluster

Dans un cluster autogéré, les journaux système peuvent être consultés selon l'installation et le système d'exploitation.

```bash
journalctl -u kubelet --since "30 minutes ago"
journalctl -u containerd --since "30 minutes ago"
```

Les noms de services, l'emplacement des journaux et les permissions varient selon la distribution Kubernetes.

Dans un cluster géré, utiliser les outils et consoles d'observabilité exposés par le fournisseur plutôt que de supposer que le nœud du plan de contrôle est directement accessible.

## 18. Sauvegarde et reprise après incident

### 18.1. Ce qu'il faut sauvegarder

Une stratégie de sauvegarde doit distinguer plusieurs catégories :

- État du plan de contrôle, notamment etcd lorsqu'il est administré par l'équipe.
- Manifestes Kubernetes et dépôts Git de configuration.
- Données persistantes des applications.
- Secrets et clés nécessaires à la restauration.
- Configuration des systèmes de stockage.
- Configuration des politiques de sécurité.
- Informations et procédures de récupération.
- Artéfacts et images nécessaires au redéploiement.

Une sauvegarde de etcd ne remplace pas une sauvegarde des volumes de données applicatives. De même, un dépôt Git contenant les manifestes ne suffit pas à reconstruire une base de données avec son état métier.

### 18.2. Différence entre sauvegarde et haute disponibilité

La haute disponibilité vise à continuer de fonctionner pendant certaines pannes.

La sauvegarde permet de récupérer un état antérieur après une perte ou une corruption de données.

Un système répliqué peut reproduire une suppression accidentelle sur toutes ses répliques. Dans ce cas, la redondance ne constitue pas une sauvegarde suffisante.

### 18.3. Définir RPO et RTO

Le **RPO (Recovery Point Objective)** est la quantité maximale de données que l'organisation accepte de perdre, exprimée en durée.

Le **RTO (Recovery Time Objective)** est le délai cible pour rétablir le service.

Exemple :

```text
Application : plateforme de commandes

RPO cible : 15 minutes
RTO cible : 2 heures

Cela implique :
- une stratégie de sauvegarde compatible avec la perte admissible ;
- un stockage de sauvegardes protégé ;
- une procédure de restauration documentée ;
- des tests permettant de mesurer le temps réel de reprise.
```

Les valeurs sont des exemples. Elles doivent provenir des exigences métier et des moyens techniques disponibles.

### 18.4. Tester les restaurations

Un test de restauration doit vérifier :

1. Que la sauvegarde est lisible et intègre.
2. Que les clés nécessaires sont disponibles.
3. Que les ressources applicatives peuvent être redéployées.
4. Que les volumes peuvent être restaurés.
5. Que les identifiants et dépendances peuvent être rétablis.
6. Que le service peut être validé par des tests fonctionnels.
7. Que le RPO et le RTO peuvent être respectés.
8. Que les droits et contrôles de sécurité sont toujours cohérents après restauration.

Les sauvegardes doivent être testées régulièrement et isolées autant que possible des identités et systèmes susceptibles d'être compromis lors d'un incident.

## 19. Mise à jour et maintenance du cluster

### 19.1. Préparer une mise à jour

Avant une mise à niveau, il faut :

- Identifier la version actuelle et les versions cibles prises en charge.
- Consulter les changements incompatibles et les API dépréciées.
- Vérifier la compatibilité des plugins CNI, CSI et des add-ons.
- Vérifier les contrôleurs et opérateurs installés.
- Tester les applications en environnement de préproduction.
- Disposer d'une stratégie de retour arrière ou de reconstruction.
- Prévoir la capacité nécessaire pendant l'opération.
- Confirmer la validité des sauvegardes et des procédures de reprise.

Une mise à niveau ne se résume pas à changer la version d'une image de conteneur. Elle peut modifier le comportement du plan de contrôle, du runtime et de certaines ressources.

### 19.2. Drainer un nœud

Dans un environnement adapté et après avoir vérifié les workloads concernés, une opération de maintenance peut commencer par un cordon puis un drain.

```bash
kubectl cordon worker-01
kubectl drain worker-01 --ignore-daemonsets
```

Le drain peut échouer si des Pods ne peuvent pas être évacués, notamment à cause des PodDisruptionBudgets, des Pods non gérés par un contrôleur ou des contraintes de stockage.

Ne pas ajouter automatiquement des options qui ignorent les protections. Évaluer la cause de l'échec et planifier l'interruption.

Après la maintenance, si le nœud peut être remis en service :

```bash
kubectl uncordon worker-01
kubectl get nodes -o wide
kubectl describe node worker-01
```

Ces opérations ne remplacent pas la procédure propre à une distribution Kubernetes ou à une plateforme cloud donnée.

## 20. Projet pratique : plateforme Kubernetes sécurisée

### 20.1. Scénario

Une équipe doit déployer une application composée de trois couches :

```text
                 Utilisateur
                     |
                     v
              +-------------+
              | Frontend    |
              +------+------+
                     |
                     v
              +-------------+
              | API métier  |
              +------+------+
                     |
                     v
              +-------------+
              | Base de      |
              | données      |
              +-------------+
```

Les exigences sont les suivantes :

- Au moins trois réplicas de l'API en production.
- Des demandes et limites de ressources.
- Des sondes applicatives adaptées.
- Une répartition des Pods pour limiter les pannes concentrées.
- Un PDB cohérent avec le nombre de réplicas.
- Une politique Pod Security restrictive.
- Des droits RBAC limités par namespace.
- Des NetworkPolicies qui contrôlent les communications entre couches.
- Des Secrets protégés et non enregistrés dans Git.
- Des images provenant d'un registre approuvé.
- Une stratégie de supervision.
- Des sauvegardes et une procédure de restauration documentées.

### 20.2. Étape 1 : créer les namespaces

Créer les namespaces correspondant aux environnements, par exemple `test` et `production`, et déterminer les labels communs utilisés par les politiques organisationnelles.

Il faut éviter d'utiliser un namespace partagé sans politique de séparation lorsque plusieurs équipes ne se font pas mutuellement confiance.

### 20.3. Étape 2 : configurer les ressources

Pour chaque conteneur, définir :

- Les `requests` CPU et mémoire.
- Les `limits` correspondant aux besoins.
- Les sondes de readiness, liveness et startup si elles sont pertinentes.
- Les ports réellement utilisés.
- Les répertoires qui doivent être accessibles en écriture.

Les valeurs doivent être vérifiées avec des mesures de charge représentatives.

### 20.4. Étape 3 : rendre l'API résiliente

Configurer au moins trois réplicas, un mécanisme de répartition et une stratégie de déploiement.

Ajouter des contraintes de placement pour répartir les réplicas entre les domaines de panne disponibles.

Créer un PDB cohérent avec le niveau d'indisponibilité accepté et vérifier qu'il n'empêche pas toute opération de maintenance.

### 20.5. Étape 4 : renforcer les Pods

Pour l'API et le frontend, lorsque l'application le permet :

- Exécuter sous un UID non privilégié.
- Désactiver l'escalade de privilèges.
- Retirer les capabilities inutiles.
- Utiliser le profil seccomp par défaut.
- Rendre le système de fichiers racine en lecture seule.
- Désactiver le montage automatique du jeton si l'accès à l'API est inutile.
- Appliquer le profil Pod Security adapté.

Ne pas modifier les workloads d'infrastructure de manière aveugle. Identifier leurs besoins et séparer les exceptions justifiées des charges applicatives ordinaires.

### 20.6. Étape 5 : configurer RBAC

Définir des identités distinctes pour :

- L'exploitation en lecture.
- Les opérations de déploiement dans l'espace autorisé.
- La surveillance.
- Les composants qui doivent réellement appeler l'API.

Ne pas accorder des droits d'écriture sur les Secrets ou les RoleBindings si cela n'est pas nécessaire.

Tester les autorisations positives et négatives avec `kubectl auth can-i`.

### 20.7. Étape 6 : construire les politiques réseau

Définir les flux nécessaires avant d'appliquer un refus par défaut :

```text
Frontend -> API : autorisé sur le port applicatif
API -> Base     : autorisé sur le port base de données
Frontend -> Base: interdit
Autres Pods -> Base : interdits par défaut
Pods -> DNS     : autorisé selon le DNS réel du cluster
```

Le contrôle doit être réalisé depuis des Pods représentatifs des différentes couches.

Vérifier également les flux légitimes de supervision, de collecte de logs et de sauvegarde qui seraient concernés par les règles.

### 20.8. Étape 7 : valider la sécurité des images

Le pipeline doit produire des images identifiées par des références contrôlées.

Mettre en place les vérifications appropriées pour les vulnérabilités, les dépendances, l'origine des images et les attestations si disponibles.

Les déploiements doivent utiliser un mécanisme qui assure l'application de la politique choisie, au lieu de s'appuyer uniquement sur une recommandation destinée aux développeurs.

### 20.9. Étape 8 : observer et tester

Collecter les événements, métriques et journaux nécessaires.

Réaliser des tests contrôlés :

- Suppression d'un Pod de l'API.
- Perte d'une instance frontend.
- Échec volontaire d'une mise à jour en environnement de test.
- Vérification d'une requête réseau interdite.
- Vérification des droits de lecture des Secrets.
- Tentative de déploiement d'une image interdite.
- Vérification d'une montée en charge.
- Exercice de restauration dans un environnement isolé.

Pour chaque test, noter le résultat attendu, le résultat réel, le signal permettant de détecter le problème et la procédure de retour à la normale.

### 20.10. Critères de réussite

Le projet est considéré comme réussi lorsque :

- Les workloads fonctionnent avec des ressources correctement déclarées.
- La perte d'un Pod est compensée par le contrôleur.
- La répartition des réplicas correspond aux contraintes définies.
- La politique Pod Security est appliquée comme prévu.
- Les utilisateurs ont uniquement les droits attendus.
- Les communications non nécessaires sont bloquées.
- Les secrets ne sont pas exposés dans les dépôts ou les journaux.
- Les images respectent la politique d'origine définie.
- Les problèmes courants peuvent être diagnostiqués par des données observables.
- Une restauration a été réalisée et validée dans un environnement de test.

## 21. Exercices corrigés

### Exercice 1 : le Pod reste Pending

Un Deployment demande quatre réplicas. Les Pods sont `Pending`.

Quelle est la première démarche ?

**Correction :**

Ne pas augmenter immédiatement le nombre de nœuds ou réduire arbitrairement les ressources. Examiner les événements avec `kubectl describe pod` et `kubectl get events`, puis vérifier les ressources disponibles, les quotas, les contraintes de planification et les volumes.

L'objectif est d'identifier la cause avant d'effectuer une modification.

### Exercice 2 : un conteneur redémarre continuellement

Un Pod présente `CrashLoopBackOff`.

**Correction :**

Consulter les logs du conteneur et ceux de l'instance précédente. Examiner son code de sortie, ses sondes, ses permissions, sa configuration et ses limites de ressources. Ne pas considérer le mot `CrashLoopBackOff` comme une cause suffisante.

### Exercice 3 : un développeur peut lire un Secret

Un développeur n'a pas le droit `get secrets`, mais il peut créer des Pods dans le namespace. Il crée un Pod qui monte un Secret et lit le fichier.

Pourquoi cela fonctionne-t-il ?

**Correction :**

Le droit de créer un workload peut permettre d'utiliser un Secret existant sans disposer directement du droit de lire l'objet Secret via l'API. Il faut contrôler les droits de création et de modification des workloads, les politiques d'admission et l'accès aux identités, en plus des permissions de lecture des Secrets.

### Exercice 4 : DNS ne fonctionne plus après le refus par défaut

L'application ne peut plus résoudre les noms internes.

**Correction :**

La politique de sortie peut bloquer DNS. Vérifier les règles egress et les Pods DNS réellement présents dans le cluster. Autoriser DNS de manière contrôlée, sur les bons ports et vers les bons endpoints, puis tester la résolution depuis un Pod.

### Exercice 5 : l'image est considérée comme sûre

Une image ne présente aucune vulnérabilité détectée par le scanner.

Cela suffit-il ?

**Correction :**

Non. Le scan ne prouve pas l'absence de vulnérabilités inconnues, de comportement malveillant ou de mauvaise configuration. Vérifier également l'origine, les dépendances, la provenance, les signatures ou attestations disponibles et les paramètres d'exécution.

### Exercice 6 : le PDB empêche une maintenance

Une évacuation de nœud échoue à cause du budget d'interruption.

**Correction :**

Examiner le nombre de réplicas prêts, le PDB, les sondes et les contraintes de placement. Déterminer si le cluster dispose de la capacité pour déplacer les Pods. Ne pas contourner systématiquement le PDB : il signale potentiellement que la maintenance entraînerait une indisponibilité supérieure à celle qui est acceptée.

### Exercice 7 : deux Pods ne peuvent pas communiquer

Une API n'arrive plus à joindre sa base de données.

**Correction :**

Vérifier d'abord la résolution DNS, le Service et ses EndpointSlices, l'état du Pod de base de données et le port d'écoute. Examiner ensuite les NetworkPolicies dans les deux sens du flux, puis le routage, le pare-feu et les paramètres TLS ou d'authentification.

## 22. Checklist de sécurité avant production

### Identités et accès

- [ ] Les administrateurs disposent d'identités individuelles et protégées.
- [ ] Les rôles RBAC respectent le principe du moindre privilège.
- [ ] Les droits `cluster-admin` sont limités et contrôlés.
- [ ] Les droits de création ou de modification des workloads sont maîtrisés.
- [ ] Les Secrets et les bindings RBAC ont des permissions restreintes.
- [ ] Les ServiceAccounts sont adaptés aux besoins réels des applications.

### Pods et conteneurs

- [ ] Les workloads ordinaires s'exécutent sans root lorsque cela est possible.
- [ ] L'escalade de privilèges est désactivée.
- [ ] Les capabilities inutiles sont retirées.
- [ ] Seccomp est configuré de manière adaptée.
- [ ] Le système de fichiers racine est en lecture seule lorsque compatible.
- [ ] Les limites de ressources et sondes ont été définies selon les besoins.
- [ ] Les workloads privilégiés sont identifiés et justifiés.
- [ ] Les profils Pod Security sont appliqués aux namespaces concernés.

### Réseau et données

- [ ] Les flux entre applications sont documentés.
- [ ] Les NetworkPolicies ont été testées avec le CNI réel.
- [ ] Les flux DNS et les dépendances nécessaires sont explicitement vérifiés.
- [ ] Les Secrets ne sont pas enregistrés en clair dans les dépôts.
- [ ] Le chiffrement au repos est configuré lorsque requis.
- [ ] La rotation des secrets et des clés est documentée.
- [ ] Les sauvegardes sont protégées et leur restauration est testée.

### Chaîne d'approvisionnement

- [ ] Les images proviennent de sources approuvées.
- [ ] Les images et dépendances font l'objet d'analyses régulières.
- [ ] Les builds n'incorporent pas de secrets.
- [ ] Les artefacts sont identifiables et reproductibles autant que possible.
- [ ] Les mécanismes de signature ou d'attestation sont vérifiés lorsqu'ils sont utilisés.
- [ ] Les pipelines CI/CD ne disposent pas de privilèges excessifs.

### Exploitation

- [ ] Les logs, métriques et événements sont collectés.
- [ ] Les opérations sensibles peuvent être retracées.
- [ ] Les mises à jour sont testées et planifiées.
- [ ] Les incidents et procédures de retour arrière sont documentés.
- [ ] Le cluster dispose d'une stratégie de sauvegarde et de reprise.
- [ ] La capacité est mesurée et les limites sont comprises.
- [ ] Les tests de restauration et de sécurité sont répétés périodiquement.

## 23. Glossaire expert

**Admission** : contrôle effectué lors du traitement d'une requête à l'API Kubernetes, pouvant notamment valider ou modifier des objets.

**Audit** : mécanisme d'enregistrement des requêtes pertinentes adressées à l'API.

**CNI** : interface standard utilisée pour intégrer les solutions de réseau des conteneurs.

**Capability Linux** : privilège système spécifique pouvant être accordé séparément de l'ensemble des droits root.

**etcd** : base de données qui conserve l'état du plan de contrôle Kubernetes.

**HPA** : HorizontalPodAutoscaler, qui ajuste le nombre de réplicas en fonction de métriques.

**Kubelet** : agent qui assure l'exécution des Pods affectés à un nœud.

**NetworkPolicy** : ressource qui définit des règles de filtrage du trafic pour des Pods, sous réserve de la prise en charge par le réseau du cluster.

**Pod Security Standards** : profils de sécurité définis par Kubernetes : Privileged, Baseline et Restricted.

**PDB** : PodDisruptionBudget, qui limite certaines interruptions volontaires de Pods.

**Provenance** : informations qui décrivent l'origine et le processus de production d'un artefact.

**RBAC** : contrôle d'accès fondé sur des rôles et des permissions.

**RPO** : quantité de données, exprimée en durée, qu'une organisation accepte de perdre après un incident.

**RTO** : délai cible de rétablissement d'un service.

**SBOM** : inventaire des composants logiciels d'un artefact.

**Seccomp** : mécanisme Linux de filtrage des appels système.

**ServiceAccount** : identité utilisée notamment par les workloads qui doivent interagir avec l'API Kubernetes.

**Taint** : propriété d'un nœud utilisée pour restreindre les Pods pouvant y être planifiés.

**Toleration** : configuration d'un Pod lui permettant de tolérer un taint correspondant.

**Topology spread** : contraintes de répartition des Pods entre des domaines topologiques comme les hôtes et les zones.

**Validation de provenance** : contrôle des informations d'origine et de production d'un artefact avant de lui accorder une confiance.

## 24. Documentation officielle

La documentation officielle doit rester la référence pour confirmer les comportements liés à la version du cluster, à la distribution et aux composants utilisés.

### Architecture et exploitation

- Vue d'ensemble de l'architecture Kubernetes : https://kubernetes.io/docs/concepts/architecture/
- Gestion des workloads : https://kubernetes.io/docs/concepts/workloads/controllers/
- Deployment et stratégies de mise à jour : https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Répartition topologique : https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
- Disruptions de Pods : https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
- Quotas de ressources : https://kubernetes.io/docs/concepts/policy/resource-quotas/
- LimitRange : https://kubernetes.io/docs/concepts/policy/limit-range/

### Sécurité

- Vue d'ensemble de la sécurité : https://kubernetes.io/docs/concepts/security/
- Liste de contrôle de sécurité : https://kubernetes.io/docs/concepts/security/security-checklist/
- Pod Security Standards : https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Pod Security Admission : https://kubernetes.io/docs/concepts/security/pod-security-admission/
- Bonnes pratiques RBAC : https://kubernetes.io/docs/concepts/security/rbac-good-practices/
- ServiceAccounts : https://kubernetes.io/docs/concepts/security/service-accounts/
- Secrets : https://kubernetes.io/docs/concepts/configuration/secret/
- Chiffrement des données au repos : https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
- Sécuriser un cluster : https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/

### Réseau, admission et audit

- NetworkPolicies : https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Contrôles d'admission : https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/
- ValidatingAdmissionPolicy : https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
- Audit Kubernetes : https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/

### Diagnostic

- Dépannage d'un cluster : https://kubernetes.io/docs/tasks/debug/debug-cluster/
- Dépannage des applications : https://kubernetes.io/docs/tasks/debug/debug-application/

## Conclusion

L'expertise Kubernetes consiste à maîtriser les interactions entre les ressources déclaratives, la planification, la résilience, les identités, le réseau, le runtime et l'exploitation.

Une plateforme bien conçue doit pouvoir expliquer non seulement comment une application est déployée, mais aussi :

- Qui peut la modifier.
- Quelles ressources elle peut consommer.
- Avec quels composants elle peut communiquer.
- Quels privilèges elle possède.
- Comment ses artefacts sont construits et vérifiés.
- Comment les actions sensibles sont tracées.
- Comment elle réagit à une panne.
- Comment son état et ses données sont restaurés après un incident.

Le niveau expert est atteint lorsque ces garanties ne reposent plus uniquement sur des habitudes individuelles, mais sur des politiques vérifiables, des configurations reproductibles, des tests réguliers et des procédures d'exploitation documentées.