# Kubernetes : réseau et stockage

## Présentation du cours

Le réseau et le stockage sont deux composants fondamentaux de Kubernetes. Ils permettent aux applications de communiquer entre elles, d'être accessibles depuis l'extérieur du cluster et de conserver leurs données indépendamment du cycle de vie de leurs Pods.

Ce niveau intermédiaire prolonge les bases de Kubernetes : Pods, Deployments, namespaces, labels, sélecteurs et commandes `kubectl`.

L'objectif est de savoir concevoir, déployer, sécuriser et dépanner une architecture Kubernetes comportant plusieurs services et des données persistantes.

### Compétences visées

À la fin de ce cours, il faudra être capable de :

- expliquer le modèle réseau de Kubernetes et le rôle du CNI ;
- exposer une application avec un Service adapté à son usage ;
- comprendre les ports `port`, `targetPort` et `nodePort` ;
- résoudre les noms DNS des Services et des Pods ;
- diagnostiquer les problèmes de connectivité et d'endpoints ;
- publier une application HTTP avec Ingress ou Gateway API ;
- appliquer des politiques réseau avec NetworkPolicy ;
- distinguer un volume temporaire d'un stockage persistant ;
- créer et utiliser des PersistentVolumes et PersistentVolumeClaims ;
- comprendre les StorageClass et le provisionnement dynamique ;
- déployer une application avec un stockage durable au moyen d'un StatefulSet ;
- diagnostiquer les erreurs de montage et de provisionnement ;
- concevoir une architecture réseau et stockage documentée et sécurisée.

## 1. Préparer l'environnement de travail

Le cours utilise `kubectl` et un cluster Kubernetes de laboratoire. Celui-ci peut être fourni par Minikube, Kind, un environnement d'apprentissage ou une plateforme cloud.

Les commandes de création de Services et de PVC restent similaires d'un environnement à l'autre. En revanche, la configuration du réseau, le contrôleur Gateway, les StorageClass et les pilotes de stockage dépendent du cluster.

### 1.1 Vérifier le contexte Kubernetes

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
kubectl get namespaces
```

Vérifier que les nœuds sont opérationnels :

```bash
kubectl get nodes
```

Un résultat typique :

```text
NAME             STATUS   ROLES           AGE   VERSION
k8s-control-01   Ready    control-plane   15d   v1.xx.x
k8s-worker-01    Ready    <none>          15d   v1.xx.x
```

Les noms et versions affichés dépendent de l'environnement.

### 1.2 Créer un espace de laboratoire

```bash
kubectl create namespace reseau-stockage
kubectl config set-context --current --namespace=reseau-stockage
kubectl get pods
```

Le changement de namespace dans le contexte facilite les commandes du laboratoire. Il ne modifie pas le namespace par défaut pour tous les utilisateurs ou pour tous les contextes.

Pour connaître le namespace d'une ressource :

```bash
kubectl get pods -A
kubectl get services -A
kubectl get pvc -A
```

Pour travailler explicitement dans le namespace du cours, utiliser `-n reseau-stockage`.

## 2. Comprendre le modèle réseau Kubernetes

### 2.1 Le principe fondamental

Dans un cluster Kubernetes classique, chaque Pod possède une adresse IP de réseau de Pods. Les conteneurs d'un même Pod partagent son espace réseau et peuvent communiquer entre eux par `localhost`.

Le réseau de Pods fournit la connectivité entre les Pods, même lorsqu'ils se trouvent sur des nœuds différents. La manière concrète dont les paquets circulent dépend de l'implémentation réseau du cluster.

Kubernetes fournit les objets API permettant de décrire cette connectivité, mais plusieurs mécanismes sont mis en œuvre par des composants du cluster.

### 2.2 Schéma général du réseau

```text
                         CLIENT EXTERNE
                               |
                               | HTTP/HTTPS
                               v
                    +----------------------+
                    | LoadBalancer /       |
                    | Gateway / Ingress    |
                    +----------------------+
                               |
                               v
                    +----------------------+
                    | Service Kubernetes   |
                    | ClusterIP            |
                    +----------------------+
                               |
                      sélection des Pods
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
    +---------------------+          +---------------------+
    | Pod : api-1         |          | Pod : api-2         |
    | IP : 10.244.1.10    |          | IP : 10.244.2.11    |
    | Port : 8080         |          | Port : 8080         |
    +---------------------+          +---------------------+
              |                                 |
              +----------------+----------------+
                               |
                               v
                    +----------------------+
                    | Service : database  |
                    | Port : 5432          |
                    +----------------------+
                               |
                               v
                    +----------------------+
                    | Pod : database-0     |
                    | Port : 5432          |
                    +----------------------+
```

Les adresses IP représentées sont des exemples. Les plages réellement utilisées dépendent de la configuration du cluster.

### 2.3 Les principaux composants

**Pod**

Unité d'exécution réseau de Kubernetes. Chaque Pod dispose normalement de sa propre adresse IP. Cette adresse peut changer lorsqu'un Pod est recréé.

**Service**

Point d'accès stable devant un ensemble de Pods. Le Service permet aux clients de ne pas dépendre de l'adresse IP individuelle des Pods.

**CNI — Container Network Interface**

Interface utilisée par les environnements de conteneurs pour configurer le réseau des Pods. Les solutions réseau Kubernetes implémentent généralement le CNI et peuvent fournir des fonctions complémentaires, comme l'application des NetworkPolicy.

**kube-proxy**

Composant traditionnel de Kubernetes qui surveille les Services et leurs endpoints afin de programmer le routage du trafic. Certaines implémentations réseau prennent en charge le comportement des Services sans utiliser le kube-proxy standard.

**CoreDNS**

Service DNS fréquemment utilisé pour résoudre les noms des Services et certains noms de Pods dans le cluster.

**Gateway API et Ingress**

Mécanismes déclaratifs permettant de gérer l'accès au trafic entrant, notamment HTTP et HTTPS, à travers un contrôleur ou une implémentation adaptée.

### 2.4 Le flux de communication

Supposons qu'un Pod `frontend` souhaite contacter une API.

```text
frontend
   |
   | 1. Résolution DNS
   |    api.reseau-stockage.svc.cluster.local
   v
IP stable du Service api
   |
   | 2. Routage du trafic
   v
EndpointSlice du Service api
   |
   | 3. Choix d'un endpoint prêt
   +--------------------+
   |                    |
   v                    v
Pod api-1             Pod api-2
```

Les Pods backend sont associés au Service à l'aide de labels et de sélecteurs. Kubernetes maintient des objets EndpointSlice décrivant les endpoints associés au Service.

Un Service n'est donc pas simplement un nom DNS : c'est une ressource de découverte et d'accès réseau dont les endpoints évoluent avec les Pods sélectionnés.

## 3. Maîtriser les Services Kubernetes

Un Service expose un ensemble logique d'endpoints réseau selon un nom et un port stables.

Les types les plus courants sont :

| Type | Utilisation |
|---|---|
| `ClusterIP` | Communication interne au cluster |
| `NodePort` | Exposition sur un port de chaque nœud, sous réserve de la configuration réseau |
| `LoadBalancer` | Exposition au moyen d'un équilibreur de charge compatible |
| `ExternalName` | Association d'un nom de Service à un nom DNS externe |

### 3.1 ClusterIP : communication interne

C'est le type par défaut. Le Service reçoit une adresse IP virtuelle interne au cluster.

Exemple de Service :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: reseau-stockage
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 8080
```

Explications :

- `selector` : sélectionne les Pods ayant le label `app: api` ;
- `port` : port sur lequel le Service est accessible ;
- `targetPort` : port cible sur les Pods ;
- `name` : nom du port du Service, utile notamment pour l'identification et certains enregistrements DNS SRV.

Dans cet exemple, le client contacte le Service sur le port 80. Le trafic est transmis au port 8080 des Pods sélectionnés.

### 3.2 Comprendre `port`, `targetPort` et `nodePort`

Ces trois paramètres ne désignent pas la même chose.

```text
CLIENT
  |
  | port 30080
  v
+-------------------------+
| NŒUD KUBERNETES         |
|                         |
| nodePort : 30080        |
+-------------------------+
  |
  | Service
  | port : 80
  v
+-------------------------+
| SERVICE api             |
+-------------------------+
  |
  | targetPort : 8080
  v
+-------------------------+
| POD                     |
| application : 8080      |
+-------------------------+
```

**`port`**

Port du Service, utilisé par les clients qui communiquent avec ce Service.

**`targetPort`**

Port sur lequel l'application reçoit le trafic dans le Pod sélectionné. Il peut s'agir d'un nombre ou d'un nom de port déclaré sur le conteneur.

**`nodePort`**

Port exposé sur les nœuds pour un Service de type `NodePort`, généralement attribué dans une plage configurée par le cluster ou fixé explicitement dans la configuration.

Exemple :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

Si la configuration du cluster autorise ce port, un client peut utiliser l'adresse IP appropriée d'un nœud et le port 30080. L'accessibilité réelle dépend notamment des règles réseau, des pare-feu et de la configuration des nœuds.

En général, il ne faut pas multiplier inutilement les NodePort pour des applications publiques. Un LoadBalancer ou une Gateway bien configurée est souvent préférable.

### 3.3 Créer et vérifier un Service

Créer deux Pods de test avec un Deployment :

```bash
kubectl create deployment api \
  --image=nginx \
  --replicas=2 \
  --port=80

kubectl label deployment api app=api
```

Attention : ajouter un label au Deployment ne garantit pas, à lui seul, que le template de Pod possède ce label. Pour éviter toute ambiguïté, utiliser un manifeste déclaratif complet dans les déploiements réels.

Créer le Service :

```bash
kubectl expose deployment api \
  --name=api \
  --port=80 \
  --target-port=80 \
  --type=ClusterIP
```

Vérifier :

```bash
kubectl get deployments
kubectl get pods --show-labels
kubectl get svc api
kubectl describe svc api
kubectl get endpointslice \
  -l kubernetes.io/service-name=api
```

Le Service doit sélectionner les Pods attendus. Si aucun endpoint n'est trouvé, vérifier en priorité les labels, le sélecteur et l'état des Pods.

### 3.4 Services sans sélecteur

Un Service peut être créé sans champ `selector`. Ce modèle peut servir, entre autres, à représenter une destination administrée manuellement ou une ressource réseau qui n'est pas un Pod Kubernetes.

Dans ce cas, la gestion des endpoints doit être effectuée selon le mécanisme approprié. Kubernetes ne peut pas déduire automatiquement les Pods backend à partir d'un sélecteur absent.

Ce modèle demande une configuration et une maintenance attentives. Il ne faut pas supprimer le sélecteur d'un Service classique en espérant que Kubernetes retrouvera automatiquement ses endpoints.

### 3.5 Service headless

Un Service standard présente généralement une adresse IP virtuelle stable. Un Service headless utilise `clusterIP: None` et sert à découvrir directement les endpoints, notamment dans certains déploiements avec état.

Exemple :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database
spec:
  clusterIP: None
  selector:
    app: database
  ports:
    - name: postgres
      port: 5432
      targetPort: 5432
```

Utilisations possibles :

- découverte des membres d'un ensemble distribué ;
- découverte des Pods d'un StatefulSet ;
- accès à des endpoints individuels par DNS ;
- architectures dans lesquelles le client doit connaître plusieurs membres.

Un Service headless n'est pas automatiquement meilleur qu'un Service normal. Il répond à un besoin de découverte réseau particulier.

## 4. DNS Kubernetes et découverte des Services

### 4.1 Pourquoi utiliser le DNS ?

Les adresses IP des Pods peuvent changer au fil des redémarrages, mises à jour ou opérations de planification. Les applications ne devraient donc généralement pas dépendre d'une adresse IP de Pod configurée en dur.

Au lieu de cela, elles communiquent au moyen du nom d'un Service.

Un nom DNS Kubernetes classique prend la forme suivante :

```text
<service>.<namespace>.svc.cluster.local
```

`cluster.local` est le domaine de cluster couramment utilisé, mais le domaine réel peut être différent.

### 4.2 Exemple de communication entre namespaces

Imaginons deux espaces de noms :

```text
Namespace : frontend
  Pod : web

Namespace : backend
  Service : api
  Pods : api-1, api-2
```

Le Pod `web` peut généralement contacter le Service avec le nom :

```text
api.backend
```

Ou avec son nom DNS complet :

```text
api.backend.svc.cluster.local
```

En revanche, appeler simplement `api` depuis le namespace `frontend` cherchera généralement le nom dans le namespace courant et ne désignera pas le Service `api` du namespace `backend`.

### 4.3 Tester une résolution DNS

Créer un Pod de dépannage :

```bash
kubectl run dns-test \
  --image=busybox:1.36 \
  --restart=Never \
  --command -- sleep 3600
```

Puis exécuter :

```bash
kubectl exec dns-test -- nslookup kubernetes.default
```

Tester le Service :

```bash
kubectl exec dns-test -- nslookup api
```

Si le Service existe dans un autre namespace :

```bash
kubectl exec dns-test -- nslookup api.backend
```

Le nom `kubernetes.default` est un test utile pour vérifier que la résolution DNS du cluster fonctionne au moins sur un nom de Service fondamental.

### 4.4 Examiner la configuration DNS du Pod

```bash
kubectl exec dns-test -- cat /etc/resolv.conf
```

On peut y retrouver un serveur DNS et des domaines de recherche utilisés pour compléter les noms abrégés.

La configuration exacte dépend du cluster et des politiques DNS appliquées aux Pods.

### 4.5 Diagnostiquer un échec DNS

Une méthode progressive consiste à vérifier :

1. Le nom du Service et son namespace.
2. L'existence du Service.
3. L'état des Pods du système DNS, généralement dans `kube-system`.
4. Le Service DNS, souvent nommé `kube-dns`, y compris lorsque CoreDNS est utilisé.
5. Les EndpointSlice du service DNS.
6. La configuration DNS du Pod client.
7. Les NetworkPolicy et les règles réseau qui pourraient bloquer le trafic DNS.

Commandes utiles :

```bash
kubectl get svc -n kube-system
kubectl get pods -n kube-system
kubectl get endpointslice -n kube-system \
  -l kubernetes.io/service-name=kube-dns
kubectl logs -n kube-system \
  -l k8s-app=kube-dns
```

Le sélecteur de labels des Pods DNS peut varier selon la distribution. Si la dernière commande ne sélectionne rien, récupérer les labels réels avec `kubectl get pods --show-labels -n kube-system`.

### 4.6 DNS et Services headless

Pour un Service headless, les réponses DNS peuvent représenter les différents endpoints plutôt qu'une IP virtuelle unique.

Cette propriété est utile pour des systèmes qui doivent contacter des membres individuels, tels que certains ensembles de bases de données distribuées.

Il faut néanmoins distinguer la résolution DNS, la découverte des membres et le mécanisme de consensus de l'application. DNS ne garantit pas à lui seul la cohérence ou la disponibilité d'un système distribué.

## 5. Examiner les endpoints et les EndpointSlice

Les EndpointSlice représentent les endpoints réseau associés à un Service. Ils permettent notamment à Kubernetes et aux implémentations réseau de traiter les ensembles d'endpoints de façon évolutive.

Vérifier les Services :

```bash
kubectl get svc
```

Afficher les EndpointSlice :

```bash
kubectl get endpointslice
```

Filtrer les endpoints d'un Service :

```bash
kubectl get endpointslice \
  -l kubernetes.io/service-name=api \
  -o yaml
```

Il est également utile d'examiner les événements et les Pods :

```bash
kubectl get pods -o wide
kubectl describe svc api
kubectl describe deployment api
kubectl get events --sort-by=.metadata.creationTimestamp
```

### 5.1 Service sans endpoint : exemple de diagnostic

Le Service sélectionne les Pods qui portent le label `app: api`.

```yaml
selector:
  app: api
```

Mais le template des Pods contient seulement :

```yaml
labels:
  app: api-v2
```

Les noms ne correspondent pas : le Service ne sélectionne aucun de ces Pods.

Schéma du problème :

```text
Service api
Selector : app=api
       |
       | recherche des Pods
       v
Pod 1 : app=api-v2       NON SÉLECTIONNÉ
Pod 2 : app=api-v2       NON SÉLECTIONNÉ
       |
       v
Aucun endpoint correspondant
```

Correction : harmoniser le sélecteur du Service et les labels des Pods, puis vérifier les EndpointSlice.

Les labels constituent le lien logique entre de nombreuses ressources Kubernetes. Une erreur de label peut se traduire par un problème réseau alors que l'application fonctionne parfaitement à l'intérieur de son Pod.

## 6. Publier du trafic HTTP avec Ingress et Gateway API

### 6.1 Comprendre le trafic entrant

Le trafic entrant, souvent qualifié de *north-south*, circule entre les clients situés à l'extérieur du cluster et les applications hébergées dans le cluster.

Une architecture fréquente :

```text
Navigateur
    |
    | HTTPS
    v
Adresse publique
    |
    v
LoadBalancer
ou Gateway
    |
    v
HTTPRoute ou configuration de routage équivalente
    |
    v
Service Kubernetes
    |
    +-------------------+
    |                   |
    v                   v
  Pod web-1           Pod web-2
```

Une Gateway ou un contrôleur Ingress traite les règles de routage et transmet les requêtes aux Services cibles.

### 6.2 Ingress : comprendre l'API existante

Un objet Ingress définit des règles HTTP/HTTPS basées, par exemple, sur les noms d'hôtes et les chemins d'URL.

Exemple pédagogique :

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  ingressClassName: exemple
  rules:
    - host: app.example.test
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 80
```

Le nom `exemple` doit être remplacé par une classe réellement disponible dans le cluster.

**Point essentiel : créer un objet Ingress ne suffit pas à exposer une application.** Il faut un contrôleur Ingress installé et configuré pour traiter cet objet, ainsi qu'un chemin réseau permettant aux clients de joindre ce contrôleur.

L'API Ingress est stable, mais elle n'est plus développée fonctionnellement. Par ailleurs, le projet Kubernetes a annoncé la retraite d'Ingress NGINX à compter de mars 2026. Pour un nouveau déploiement, il faut éviter de choisir une implémentation retirée et privilégier une solution maintenue, notamment une implémentation de Gateway API adaptée à l'environnement.

### 6.3 Gateway API : modèle moderne de routage

Gateway API sépare plusieurs responsabilités :

| Ressource | Rôle |
|---|---|
| `GatewayClass` | Identifie une classe gérée par une implémentation |
| `Gateway` | Décrit l'infrastructure d'entrée et ses listeners |
| `HTTPRoute` | Décrit les règles HTTP dirigées vers les backends |
| `Service` | Identifie l'application ou le groupe d'endpoints cible |

Cette séparation facilite la distinction entre l'administration de l'infrastructure et la configuration des applications.

Les API Gateway ne sont pas mises en œuvre par le seul serveur API Kubernetes : il faut installer les composants et les CRD de l'implémentation retenue.

### 6.4 Vérifier la disponibilité de Gateway API

```bash
kubectl get gatewayclass
kubectl get gateways -A
kubectl api-resources | grep -E 'gateway|httproute'
```

Si aucune GatewayClass n'est présente, cela ne signifie pas nécessairement que Kubernetes est défectueux. L'implémentation peut ne pas être installée.

Avant d'utiliser les manifestes suivants, identifier une GatewayClass existante ou installer une implémentation maintenue adaptée au cluster.

### 6.5 Exemple de Gateway

Le manifeste ci-dessous suppose l'existence d'une classe appelée `public-gateway`. Ce nom est un exemple et doit être adapté à l'implémentation installée.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: gateway-web
spec:
  gatewayClassName: public-gateway
  listeners:
    - name: http
      protocol: HTTP
      port: 80
      allowedRoutes:
        namespaces:
          from: Same
```

Cette Gateway demande à l'implémentation de fournir un point d'accès HTTP.

Par défaut, elle accepte ici des routes du même namespace. Les routes situées dans d'autres namespaces exigent une configuration explicite de `allowedRoutes`.

### 6.6 Ajouter une HTTPRoute

Supposons qu'un Service `web` existe sur le port 80 dans le même namespace.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: route-web
spec:
  parentRefs:
    - name: gateway-web
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
      backendRefs:
        - name: web
          port: 80
```

Le chemin fonctionnel est le suivant :

```text
Client
  |
  v
Gateway : port 80
  |
  v
HTTPRoute : chemin /
  |
  v
Service web : port 80
  |
  v
Pods web
```

Appliquer les manifestes après avoir adapté les noms de ressources :

```bash
kubectl apply -f gateway.yaml
kubectl apply -f httproute.yaml

kubectl get gateway
kubectl get httproute
kubectl describe gateway gateway-web
kubectl describe httproute route-web
```

Il faut vérifier les conditions d'état des ressources, notamment celles qui indiquent si la Gateway est programmée et si la route est acceptée. Une ressource créée mais non acceptée ne garantit pas que le trafic sera routé.

### 6.7 HTTPS et certificats

Pour un accès HTTPS, le listener doit être configuré avec le protocole adapté et référencer le secret de certificat attendu par l'implémentation.

Le détail de la configuration dépend de l'implémentation Gateway, de la façon dont les certificats sont provisionnés et du nom d'hôte visé.

Principes importants :

- conserver les clés privées dans des emplacements appropriés ;
- limiter les droits d'accès aux Secrets ;
- contrôler le renouvellement des certificats ;
- tester la validité des chaînes de certificats ;
- éviter de transmettre des identifiants ou des clés dans les fichiers de configuration publics.

## 7. Sécuriser les communications avec NetworkPolicy

### 7.1 Pourquoi une NetworkPolicy ?

Sans segmentation réseau appropriée, les Pods peuvent souvent communiquer beaucoup plus librement que nécessaire.

Une NetworkPolicy permet de limiter le trafic entrant vers les Pods et/ou le trafic sortant de ces Pods. Elle utilise notamment les labels des Pods, les labels des namespaces, des plages CIDR et des ports.

**Prérequis :** la solution réseau du cluster doit prendre en charge les NetworkPolicy et les appliquer effectivement. Créer une NetworkPolicy dans un cluster dont l'implémentation réseau ne la prend pas en charge ne suffit pas à restreindre le trafic.

### 7.2 Architecture cible

L'application suivante comporte trois couches :

```text
UTILISATEURS
     |
     v
+-------------+
| Frontend    |
+-------------+
     |
     | TCP 8080
     v
+-------------+
| API         |
+-------------+
     |
     | TCP 5432
     v
+-------------+
| Database    |
+-------------+
```

Politique souhaitée :

- les utilisateurs accèdent au frontend par le point d'entrée prévu ;
- le frontend communique avec l'API ;
- l'API communique avec la base de données ;
- la base de données n'accepte pas directement le trafic du frontend ;
- seuls les flux strictement nécessaires sont autorisés.

### 7.3 Exemple : autoriser seulement l'API vers la base

Les Pods de base de données portent le label `app: database`. Les Pods API portent le label `app: api`.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-allow-api
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api
      ports:
        - protocol: TCP
          port: 5432
```

Cette politique :

1. sélectionne les Pods portant `app: database` dans le namespace de la politique ;
2. les isole pour le trafic entrant ;
3. autorise le trafic TCP entrant sur le port 5432 depuis les Pods `app: api` du même namespace ;
4. n'autorise pas automatiquement toutes les autres sources.

Ce dernier point est capital : les Pods API doivent réellement porter le label attendu.

Appliquer et examiner la politique :

```bash
kubectl apply -f database-networkpolicy.yaml
kubectl get networkpolicy
kubectl describe networkpolicy database-allow-api
```

### 7.4 Les sélecteurs de NetworkPolicy

Un `podSelector` placé au niveau supérieur de `spec` sélectionne les Pods auxquels la politique s'applique dans son namespace.

Un `podSelector` placé dans une règle `from` sélectionne les Pods sources du même namespace que la politique, sauf lorsque l'on utilise aussi un `namespaceSelector`.

Pour cibler des Pods qui se trouvent dans un autre namespace, on peut combiner un `namespaceSelector` et un `podSelector` dans la même entrée.

Exemple conceptuel :

```yaml
from:
  - namespaceSelector:
      matchLabels:
        environnement: production
    podSelector:
      matchLabels:
        app: api
```

Cette entrée cible les Pods `app: api` situés dans des namespaces portant le label `environnement: production`.

Attention : placer le `namespaceSelector` et le `podSelector` dans deux entrées distinctes d'une liste `from` représente une logique différente. Les éléments de la liste sont des alternatives ; l'association des deux sélecteurs dans la même entrée permet de les combiner.

### 7.5 Politique par défaut : isoler les entrées d'un namespace

Voici un exemple qui isole le trafic entrant vers tous les Pods du namespace contenant la politique :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

Cette politique ne bloque pas à elle seule tout le trafic sortant. Elle isole l'entrée pour tous les Pods du namespace et laisse les connexions permises par les autres politiques applicables continuer à fonctionner.

Pour créer une segmentation plus complète, il faut étudier séparément les exigences de trafic entrant et sortant.

### 7.6 Isoler également le trafic sortant

Une politique avec `policyTypes: [Ingress, Egress]` et sans règles correspondantes peut isoler les deux directions :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

Cette politique est très restrictive. Elle peut interrompre des fonctions nécessaires, notamment :

- les requêtes DNS ;
- la communication avec les APIs externes ;
- l'accès à une base de données située ailleurs ;
- les appels à des services internes ;
- certains échanges requis par l'environnement.

Il ne faut donc pas appliquer une politique globale de refus sans prévoir ensuite les règles nécessaires au fonctionnement de l'application.

### 7.7 Autoriser le DNS après une isolation sortante

Sur de nombreux clusters, CoreDNS est accessible dans le namespace `kube-system`, avec des labels proches de `k8s-app: kube-dns`. Ces labels doivent être vérifiés sur le cluster cible.

Exemple d'autorisation DNS pour les Pods sélectionnés par la politique :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
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

Ce manifeste doit être adapté si l'implémentation DNS utilise d'autres labels ou une architecture différente.

**Point important :** les règles NetworkPolicy s'additionnent. Si plusieurs politiques s'appliquent à un Pod dans une même direction, le trafic autorisé est l'union des autorisations correspondantes. Le trafic d'une connexion doit aussi satisfaire les restrictions pertinentes des deux côtés : sortie de la source et entrée de la destination.

### 7.8 Tester une politique réseau

Ne pas se contenter de vérifier que l'objet existe. Il faut tester les flux attendus et ceux qui doivent être bloqués.

Exemple d'approche :

1. Créer un Pod de test portant un label autorisé.
2. Essayer de joindre le Service de base de données.
3. Créer un autre Pod qui ne porte pas le label autorisé.
4. Refaire le test.
5. Examiner les logs de l'application et les événements.
6. Confirmer que les Pods applicatifs continuent de résoudre les noms nécessaires.

Une requête bloquée peut expirer ou échouer selon le comportement de l'application et de l'environnement. Un simple refus de connexion ne suffit pas à identifier avec certitude quelle règle a bloqué le flux.

## 8. Comprendre les volumes Kubernetes

### 8.1 Pourquoi le stockage est-il différent ?

Un conteneur peut être arrêté puis remplacé par un autre. L'espace de fichiers propre au conteneur ne constitue donc pas, à lui seul, une solution de stockage durable.

Le besoin consiste à séparer le cycle de vie de l'application et celui des données.

Exemple :

```text
Sans stockage persistant

Pod application-1
      |
      v
Fichiers enregistrés dans le conteneur
      |
      v
Pod supprimé
      |
      v
Un nouveau Pod repart avec un nouvel espace de fichiers


Avec stockage persistant

Pod application-1
      |
      v
PersistentVolumeClaim
      |
      v
Stockage persistant
      ^
      |
Pod application-2
```

Un nouveau Pod peut réutiliser un stockage persistant si les conditions de montage, d'accès et d'ordonnancement le permettent.

Cela ne constitue cependant pas une sauvegarde. Un volume persistant peut lui-même être endommagé, supprimé ou rendre un système de fichiers inutilisable.

### 8.2 Les principaux types de volumes

| Type | Durée de vie et usage |
|---|---|
| `emptyDir` | Espace temporaire associé à la vie du Pod |
| `configMap` | Fichiers de configuration provenant d'une ConfigMap |
| `secret` | Données sensibles fournies par un Secret Kubernetes |
| `persistentVolumeClaim` | Stockage associé à une demande persistante |
| Volume éphémère CSI | Stockage temporaire fourni par une implémentation compatible |
| Volume persistant CSI | Stockage géré par un pilote CSI |

Les volumes `ConfigMap` et `Secret` servent à distribuer des données aux Pods. Ils ne sont pas des remplacements universels d'une base de données ou d'un stockage objet.

### 8.3 `emptyDir` : stockage temporaire

Exemple :

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: temporary-storage
spec:
  containers:
    - name: app
      image: busybox:1.36
      command:
        - sh
        - -c
        - "echo donnees > /tmp/work/fichier.txt; sleep 3600"
      volumeMounts:
        - name: workdir
          mountPath: /tmp/work
  volumes:
    - name: workdir
      emptyDir: {}
```

L'espace `emptyDir` est créé pour le Pod et perd son contenu lorsque ce Pod est retiré. Il ne faut pas le considérer comme un stockage durable après recréation du Pod.

Selon la configuration, `emptyDir` peut aussi utiliser un système de fichiers en mémoire. Cela peut modifier la consommation de mémoire du conteneur ou du Pod et doit être dimensionné avec soin.

## 9. Comprendre PersistentVolume et PersistentVolumeClaim

### 9.1 Les deux ressources principales

**PersistentVolume (PV)**

Ressource qui représente un stockage disponible pour le cluster. Elle peut provenir d'un provisionnement statique ou dynamique.

**PersistentVolumeClaim (PVC)**

Demande de stockage formulée par une application ou un utilisateur. Elle déclare notamment une capacité et des modes d'accès souhaités.

Le Pod utilise habituellement le PVC, et non directement les détails techniques du système de stockage.

```text
Application
    |
    v
Pod
    |
    | référence
    v
PVC : 10 Gi
    |
    | liaison
    v
PV : capacité disponible
    |
    v
Stockage fourni par le cluster
```

Cette abstraction permet à l'application de demander un stockage sans devoir connaître tous les détails du fournisseur.

### 9.2 Cycle de vie d'un PVC

```text
Création du PVC
       |
       v
Recherche ou création d'un PV adapté
       |
       v
État Pending ?
       |
       +---- Oui : stockage indisponible,
       |           classe ou contraintes à vérifier
       |
       +---- Non
             |
             v
           Bound
             |
             v
      Le Pod utilise le PVC
             |
             v
      Montage du volume
             |
             v
       Application active
```

Les états les plus utiles à connaître sont `Pending`, `Bound` et, pour les Pods qui consomment un PVC, les états ou événements montrant si le volume a pu être attaché puis monté.

Un PVC peut demeurer `Pending` lorsqu'aucun stockage correspondant n'est disponible. Ce n'est pas nécessairement une erreur de syntaxe.

### 9.3 Les modes d'accès

Les principaux modes d'accès sont :

- `ReadWriteOnce` (RWO) : montage en lecture-écriture depuis un seul nœud à la fois, selon les capacités du volume ;
- `ReadOnlyMany` (ROX) : montage en lecture seule depuis plusieurs nœuds, si le stockage le permet ;
- `ReadWriteMany` (RWX) : montage en lecture-écriture depuis plusieurs nœuds, si le stockage le permet ;
- `ReadWriteOncePod` (RWOP) : montage en lecture-écriture par un seul Pod à la fois, avec les prérequis de prise en charge nécessaires.

Les modes réellement disponibles dépendent du type de stockage et du pilote.

Attention : RWO ne signifie pas nécessairement « un seul Pod ». Plusieurs Pods placés sur le même nœud peuvent, selon les conditions et les contraintes du volume, utiliser un volume RWO. RWOP est le mode conçu pour restreindre le montage en écriture à un seul Pod à la fois.

Les modes d'accès ne remplacent pas les permissions du système de fichiers ou les contrôles d'autorisation de l'application.

### 9.4 Créer un PVC

Exemple demandant 2 Gio de stockage :

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: donnees-app
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2Gi
```

Dans cet exemple, aucune `storageClassName` n'est fournie. Si le cluster a une StorageClass par défaut, celle-ci peut être utilisée pour le provisionnement dynamique.

Si aucune StorageClass par défaut appropriée n'existe, ou si le cluster ne dispose pas d'un provisionneur fonctionnel adapté, le PVC peut rester en attente.

Pour demander une classe spécifique, vérifier d'abord les classes disponibles :

```bash
kubectl get storageclass
kubectl get sc
```

Puis ajouter à la configuration, si cela correspond à l'environnement :

```yaml
storageClassName: nom-de-la-classe
```

Ne pas recopier aveuglément le nom d'une classe issue d'un autre cluster.

### 9.5 Utiliser le PVC dans un Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: application-stockage
spec:
  containers:
    - name: app
      image: busybox:1.36
      command:
        - sh
        - -c
        - "echo donnees-persistantes > /data/fichier.txt; sleep 3600"
      volumeMounts:
        - name: donnees
          mountPath: /data
  volumes:
    - name: donnees
      persistentVolumeClaim:
        claimName: donnees-app
```

Déployer :

```bash
kubectl apply -f pvc.yaml
kubectl apply -f pod-stockage.yaml
```

Vérifier :

```bash
kubectl get pvc
kubectl get pv
kubectl get pod application-stockage
kubectl describe pod application-stockage
```

Lire les données :

```bash
kubectl exec application-stockage -- cat /data/fichier.txt
```

Le PVC doit être lié et le volume monté avec succès pour que ce test fonctionne.

### 9.6 Vérifier la persistance

Cette manipulation illustre la différence entre le Pod et les données :

```bash
kubectl delete pod application-stockage
kubectl apply -f pod-stockage.yaml
```

Après le redémarrage du Pod, lire de nouveau le fichier :

```bash
kubectl exec application-stockage -- cat /data/fichier.txt
```

Si la configuration du stockage permet bien le remontage du PVC, le fichier doit encore être présent.

La persistance du volume ne garantit toutefois ni la réplication des données ni leur restauration après une suppression volontaire ou une panne du système de stockage.

## 10. StorageClass et provisionnement dynamique

### 10.1 À quoi sert une StorageClass ?

Une StorageClass décrit une classe de stockage proposée aux utilisateurs du cluster. Elle peut représenter des caractéristiques telles que :

- le type de support ;
- le niveau de performance ;
- le fournisseur ou le pilote de stockage ;
- certaines options du provisionneur ;
- la politique de récupération des volumes ;
- le comportement d'attente du provisionnement.

Le nom de la StorageClass est important : un PVC peut la demander pour obtenir un stockage correspondant à cette classe.

### 10.2 Fonctionnement du provisionnement dynamique

Dans un environnement configuré pour le provisionnement dynamique, le flux ressemble à ceci :

```text
PVC
 |
 | demande 10 Gi
 v
StorageClass
 |
 | identifie un provisionneur
 v
Pilote de stockage / CSI
 |
 | crée ou attribue un volume
 v
PersistentVolume
 |
 | liaison du PVC
 v
PVC : Bound
 |
 v
Le Pod peut utiliser le volume
```

Kubernetes peut alors orchestrer la demande de stockage sans qu'un administrateur ait à préparer manuellement chaque PV.

Cela exige néanmoins un provisionneur et un système de stockage correctement installés, configurés et accessibles.

### 10.3 Lister les classes de stockage

```bash
kubectl get storageclass
kubectl describe storageclass
```

Une StorageClass peut être marquée comme classe par défaut.

Pour examiner une classe précise :

```bash
kubectl describe storageclass nom-de-la-classe
kubectl get storageclass nom-de-la-classe -o yaml
```

La présence d'une classe dans l'API ne garantit pas que le système de stockage en dessous fonctionne actuellement.

### 10.4 `volumeBindingMode`

Une classe peut utiliser notamment :

- `Immediate` : le provisionnement ou la liaison peut intervenir dès que le PVC est traité ;
- `WaitForFirstConsumer` : le provisionnement ou la liaison attend qu'un Pod consommateur soit planifié, afin de tenir compte de contraintes telles que la topologie.

`WaitForFirstConsumer` est utile pour certaines infrastructures dans lesquelles les volumes sont attachés à une zone, à un nœud ou à une topologie particulière.

Exemple d'une classe conceptuelle :

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: exemple-stockage
provisioner: exemple.csi.provider.invalid
volumeBindingMode: WaitForFirstConsumer
```

Ce manifeste est illustratif : le nom du provisionneur est volontairement fictif. Il doit être remplacé par celui d'un pilote réellement installé.

Créer une StorageClass n'installe pas le pilote qu'elle référence.

### 10.5 Erreurs typiques de provisionnement

Un PVC reste `Pending` :

- la StorageClass demandée n'existe pas ;
- le provisionneur ne fonctionne pas ;
- la capacité est indisponible ;
- le mode d'accès demandé n'est pas pris en charge ;
- la taille demandée ne peut pas être satisfaite ;
- un PV statique compatible est absent ;
- la topologie ou les contraintes de planification empêchent le placement ;
- l'architecture du pilote ou du fournisseur n'est pas adaptée.

Examiner les ressources :

```bash
kubectl get pvc
kubectl describe pvc donnees-app
kubectl get pv
kubectl get storageclass
kubectl get pods -A
kubectl get events --sort-by=.metadata.creationTimestamp
```

La commande `describe pvc` est souvent l'un des premiers moyens d'identifier la cause de l'attente.

## 11. Cycle de vie d'un volume : reclaim policy

### 11.1 Deux politiques importantes

La `persistentVolumeReclaimPolicy` définit le comportement du volume après la libération du PVC associé, selon les ressources et le provisionnement concernés.

Les politiques courantes sont :

- `Retain` : le PV et les données nécessitent une intervention explicite pour être réutilisés ou nettoyés ;
- `Delete` : le PV est supprimé et le stockage sous-jacent peut également être supprimé par le provisionneur.

Le comportement exact dépend du volume et de son provisionneur.

### 11.2 Pourquoi cette politique est-elle essentielle ?

Prenons une base de données qui contient plusieurs mois de commandes :

```text
Base de données
       |
       v
PVC : commandes-db
       |
       v
PV
       |
       v
Volume du fournisseur
```

Si le PVC est supprimé, il faut comprendre à l'avance ce que le provisionneur fera du PV et du stockage réel.

Il serait dangereux de considérer que toutes les données sont automatiquement conservées après la suppression d'un PVC.

### 11.3 Vérifier la politique

```bash
kubectl get pv
kubectl get pv nom-du-pv -o yaml
kubectl describe pv nom-du-pv
```

Examiner notamment le champ :

```yaml
persistentVolumeReclaimPolicy: Retain
```

Le choix de la politique doit faire partie de la conception du stockage et de la stratégie de protection des données.

**Une politique `Retain` ne constitue pas une sauvegarde.** Elle peut préserver des données après certaines opérations de suppression, mais elle ne protège pas à elle seule d'une corruption, d'une panne du volume ou d'une suppression manuelle.

## 12. StatefulSet et stockage des applications avec état

### 12.1 Pourquoi un StatefulSet ?

Un Deployment est approprié pour les applications dont les réplicas peuvent généralement être remplacés sans identité persistante particulière.

Un StatefulSet est conçu pour les applications dont les Pods ont besoin d'identités stables et, souvent, de volumes persistants distincts.

Caractéristiques utiles :

- noms de Pods ordonnés et stables ;
- identité réseau stable dans le modèle prévu ;
- identité de stockage stable, lorsque des revendications persistantes sont configurées ;
- mises à jour et opérations de remplacement pouvant respecter un ordre.

Le StatefulSet ne transforme pas automatiquement une application en système distribué fiable. La réplication, le consensus, l'intégrité des données et la reprise après incident restent des responsabilités importantes de l'application et de son architecture.

### 12.2 Architecture avec StatefulSet

```text
                StatefulSet : database
                         |
            +------------+------------+
            |                         |
            v                         v
       database-0                database-1
            |                         |
            v                         v
         PVC-0                     PVC-1
            |                         |
            v                         v
          PV-0                      PV-1
            |                         |
            v                         v
      Volume durable           Volume durable
```

Chaque Pod peut ainsi disposer de sa propre revendication, générée à partir d'un modèle `volumeClaimTemplates`.

### 12.3 Service headless associé

Voici un exemple de Service destiné à identifier les Pods d'un StatefulSet :

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database
spec:
  clusterIP: None
  selector:
    app: database
  ports:
    - name: client
      port: 5432
      targetPort: 5432
```

Le champ `clusterIP: None` indique un Service headless.

### 12.4 Exemple de StatefulSet de laboratoire

L'exemple ci-dessous utilise une image BusyBox pour démontrer l'identité et le stockage des Pods. Ce n'est pas une base de données réelle.

Le PVC sera provisionné dynamiquement si le cluster dispose d'une StorageClass et d'un provisionneur appropriés.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: stock-stateful
spec:
  serviceName: stock-stateful
  replicas: 2
  selector:
    matchLabels:
      app: stock-stateful
  template:
    metadata:
      labels:
        app: stock-stateful
    spec:
      containers:
        - name: app
          image: busybox:1.36
          command:
            - sh
            - -c
            - "echo demarrage-$HOSTNAME >> /data/demarrages.log; sleep 3600"
          volumeMounts:
            - name: donnees
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: donnees
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 1Gi
```

Le Service headless associé au StatefulSet doit être nommé `stock-stateful`, afin de correspondre à `spec.serviceName`.

Appliquer les deux manifestes :

```bash
kubectl apply -f stock-stateful-service.yaml
kubectl apply -f stock-stateful.yaml
```

Examiner les ressources :

```bash
kubectl get statefulset
kubectl get pods
kubectl get pvc
kubectl get pv
```

Les noms des Pods devraient suivre le modèle `stock-stateful-0`, `stock-stateful-1`, etc.

Les noms des PVC créés par le modèle suivent une convention qui combine le nom de la revendication, celui du StatefulSet et l'identité de l'ordinal du Pod.

Pour observer les fichiers, utiliser le PVC ou le Pod correspondant :

```bash
kubectl exec stock-stateful-0 -- cat /data/demarrages.log
kubectl exec stock-stateful-1 -- cat /data/demarrages.log
```

Les deux Pods possèdent des revendications indépendantes dans ce modèle.

### 12.5 Limites de l'exemple StatefulSet

Un StatefulSet ne fournit pas à lui seul :

- la réplication logique des données applicatives ;
- la synchronisation entre les membres ;
- une politique de sauvegarde ;
- un basculement applicatif cohérent ;
- un mécanisme automatique de réparation d'une base de données corrompue.

Pour une base de données de production, utiliser une architecture ou un opérateur adapté au moteur de base de données, avec des procédures de sauvegarde et de restauration testées.

## 13. Sauvegarde, restauration et snapshots

### 13.1 Persistance ne signifie pas protection complète

Un volume persistant protège principalement les données contre la disparition de l'espace de fichiers éphémère associé au conteneur. Il ne constitue pas, par défaut, une stratégie de sauvegarde complète.

Une stratégie de protection des données doit examiner :

- la fréquence des sauvegardes ;
- le point de reprise nécessaire ;
- la durée maximale de perte de données acceptable ;
- la durée maximale de restauration acceptable ;
- les copies hors du domaine de panne principal ;
- les contrôles d'intégrité ;
- les tests de restauration périodiques.

### 13.2 Snapshots de volumes

Certains systèmes de stockage prennent en charge des snapshots intégrés à Kubernetes par l'intermédiaire des composants et API de snapshots de volumes.

Le principe général :

```text
PVC de production
       |
       v
Volume source
       |
       | snapshot compatible
       v
VolumeSnapshot
       |
       v
Possibilité de restauration
ou création d'un nouveau volume
```

Un snapshot n'est pas disponible automatiquement dans tous les clusters. Il faut vérifier que les composants de snapshot et le pilote de stockage disposent de la prise en charge requise.

Les snapshots peuvent aussi être dépendants du même système de stockage et du même domaine de panne que le volume original. Pour des données critiques, compléter cette approche par des sauvegardes adaptées.

### 13.3 Vérifier la disponibilité des ressources de snapshot

```bash
kubectl api-resources | grep -i snapshot
kubectl get volumesnapshot -A
kubectl get volumesnapshotclass
```

Ces commandes permettent d'examiner la disponibilité de ces ressources, si les API correspondantes sont installées.

### 13.4 Exemple conceptuel de VolumeSnapshot

Le nom de la classe doit correspondre à une classe de snapshot réellement installée.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: snapshot-donnees-app
spec:
  volumeSnapshotClassName: classe-snapshot-exemple
  source:
    persistentVolumeClaimName: donnees-app
```

Le manifeste illustre la structure de la demande. Il ne doit être appliqué que lorsque les composants de snapshot, la classe de snapshot et les capacités du pilote ont été vérifiés.

Pour une base de données, la cohérence applicative du snapshot doit également être étudiée. Une capture du volume ne remplace pas automatiquement une procédure de sauvegarde spécifique au moteur.

## 14. Permissions des fichiers montés

Le fait qu'un PVC soit `Bound` ne garantit pas que le processus de l'application puisse écrire dans le répertoire monté.

Les erreurs de permissions peuvent provenir :

- de l'identité de l'utilisateur dans le conteneur ;
- des propriétaires et permissions du système de fichiers ;
- du support de `fsGroup` par la plateforme de stockage ;
- des options du pilote ;
- des politiques de sécurité appliquées au Pod ;
- des modes de montage imposés par le système.

### 14.1 Exemple de contexte de sécurité

Un manifeste peut utiliser un contexte de sécurité adapté à l'application :

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 20001
```

Ces valeurs sont illustratives. L'image, les permissions existantes et les capacités du pilote doivent être compatibles avec ces identités.

`fsGroup` peut permettre au processus d'accéder à certains volumes en groupe, mais son effet dépend du type de volume, du pilote et des paramètres de la plateforme. Il ne faut pas supposer qu'il corrigera toutes les permissions sur tous les systèmes de stockage.

### 14.2 Diagnostiquer les erreurs d'écriture

```bash
kubectl describe pod nom-du-pod
kubectl logs nom-du-pod
kubectl exec nom-du-pod -- id
kubectl exec nom-du-pod -- ls -ld /data
kubectl exec nom-du-pod -- sh -c 'touch /data/test-ecriture'
```

Si l'accès échoue :

1. identifier l'utilisateur réel du processus ;
2. examiner les permissions du répertoire ;
3. vérifier les événements du Pod ;
4. examiner la documentation du pilote ;
5. corriger les permissions de façon contrôlée.

Éviter de résoudre arbitrairement le problème avec des permissions universelles en écriture. Cela peut introduire des risques de sécurité supplémentaires.

## 15. Dépanner le réseau : méthode structurée

Lorsqu'une application ne répond pas, il faut isoler les couches du chemin réseau au lieu de modifier plusieurs composants simultanément.

### 15.1 Étape 1 : le Pod est-il opérationnel ?

```bash
kubectl get pods -o wide
kubectl describe pod nom-du-pod
kubectl logs nom-du-pod
```

Vérifier le statut, les redémarrages, les sondes de disponibilité et les événements.

### 15.2 Étape 2 : l'application écoute-t-elle sur le bon port ?

Examiner la configuration du conteneur et les logs.

```bash
kubectl describe pod nom-du-pod
kubectl logs nom-du-pod
```

Si les outils réseau sont présents dans l'image, vérifier également les sockets en écoute. Il est souvent préférable d'utiliser un conteneur de diagnostic adapté plutôt que d'installer des outils manuellement dans un conteneur de production.

### 15.3 Étape 3 : le Service sélectionne-t-il les bons Pods ?

```bash
kubectl get svc
kubectl describe svc nom-du-service
kubectl get pods --show-labels
kubectl get endpointslice \
  -l kubernetes.io/service-name=nom-du-service
```

Un Service avec de mauvais labels peut avoir une adresse IP valide tout en ne disposant d'aucun endpoint utilisable.

### 15.4 Étape 4 : la résolution DNS fonctionne-t-elle ?

```bash
kubectl exec nom-du-pod -- nslookup nom-du-service
```

Si la résolution échoue, tester aussi `kubernetes.default`, vérifier le Service DNS dans `kube-system` et examiner les NetworkPolicy.

### 15.5 Étape 5 : la connexion réseau est-elle autorisée ?

Examiner :

- les NetworkPolicy ;
- les règles de pare-feu ;
- les ports et protocoles ;
- le routage du réseau de Pods ;
- l'existence d'endpoints prêts ;
- les contraintes du CNI.

Un test en IP peut aider à distinguer un problème DNS d'un problème de connectivité, mais il faut utiliser une adresse de service ou d'endpoint actuellement valide.

### 15.6 Étape 6 : le problème se situe-t-il à l'entrée du cluster ?

Si le Service fonctionne depuis un Pod, mais pas depuis l'extérieur, examiner :

- l'adresse du LoadBalancer ou de la Gateway ;
- la classe du contrôleur ;
- les conditions de la Gateway et de la HTTPRoute ;
- la configuration DNS publique ;
- les ports exposés et règles de pare-feu ;
- le certificat TLS, si HTTPS est utilisé.

### 15.7 Matrice de dépannage réseau

| Symptôme | Vérifications initiales |
|---|---|
| Service introuvable par DNS | Nom, namespace, CoreDNS, NetworkPolicy DNS |
| Connexion refusée | Application à l'écoute, `targetPort`, endpoints, protocole |
| Connexion expirée | Routage, pare-feu, NetworkPolicy, disponibilité de la destination |
| Aucun endpoint | Labels, sélecteurs, Pods prêts |
| IP du Service accessible, nom DNS non résolu | Configuration DNS |
| Service fonctionnel dans le cluster, externe inaccessible | LoadBalancer, Gateway, DNS public, règles réseau |
| HTTP 404 depuis une Gateway | Host, chemin, HTTPRoute, backend |
| HTTP 502 ou 503 | État du backend, endpoints, port cible, configuration de l'implémentation |

Cette matrice donne un ordre de recherche. Les codes HTTP et les erreurs réseau ne permettent pas, à eux seuls, d'identifier toutes les causes possibles.

## 16. Dépanner le stockage : méthode structurée

### 16.1 Le PVC reste `Pending`

```bash
kubectl get pvc
kubectl describe pvc donnees-app
kubectl get pv
kubectl get storageclass
```

Lire les événements du PVC et du Pod consommateur.

Vérifier :

- que la classe demandée existe ;
- que les modes d'accès sont pris en charge ;
- que la capacité est disponible ;
- que le provisionneur fonctionne ;
- que les contraintes de topologie sont compatibles ;
- que le Pod consommateur peut être planifié.

### 16.2 Le Pod reste en attente de montage

```bash
kubectl describe pod nom-du-pod
kubectl describe pvc donnees-app
kubectl get events --sort-by=.metadata.creationTimestamp
```

Les événements peuvent signaler un échec d'attachement, de montage, d'autorisation ou d'accès au volume.

Le diagnostic exact dépend du système de stockage. Sur un cluster administré, les logs des composants CSI ou du fournisseur peuvent être nécessaires.

### 16.3 Le Pod démarre, mais l'écriture échoue

```bash
kubectl exec nom-du-pod -- id
kubectl exec nom-du-pod -- ls -ld /data
kubectl exec nom-du-pod -- sh -c 'touch /data/test'
```

Examiner les permissions, l'identité du processus, le mode de montage et les options de sécurité.

### 16.4 Le volume ne peut pas être monté sur le nouveau nœud

Certaines solutions de stockage imposent des contraintes de topologie ou de montage. Un volume peut être attaché à un nœud, à une zone ou à une infrastructure particulière.

Vérifier :

- la disponibilité du volume ;
- les événements d'attachement ;
- le mode d'accès ;
- la zone du volume ;
- les règles de placement ;
- la documentation du pilote.

Il ne faut pas supposer que tout volume peut être monté simultanément sur n'importe quel nombre de nœuds.

## 17. Atelier pratique 1 : réseau et découverte DNS

### Objectif

Créer une API de test, l'exposer avec un Service interne et valider la résolution DNS.

### Étape 1 : créer les ressources

Créer `api-lab.yaml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-lab
  template:
    metadata:
      labels:
        app: api-lab
    spec:
      containers:
        - name: web
          image: nginx
          ports:
            - name: http
              containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: api-lab
spec:
  type: ClusterIP
  selector:
    app: api-lab
  ports:
    - name: http
      port: 80
      targetPort: http
```

Appliquer :

```bash
kubectl apply -f api-lab.yaml
kubectl rollout status deployment/api-lab
```

### Étape 2 : vérifier le Service

```bash
kubectl get svc api-lab
kubectl get pods --show-labels
kubectl get endpointslice \
  -l kubernetes.io/service-name=api-lab
```

### Étape 3 : tester le DNS et HTTP

```bash
kubectl run curl-test \
  --image=curlimages/curl \
  --restart=Never \
  --command -- sleep 3600
```

Puis :

```bash
kubectl exec curl-test -- \
  curl -I http://api-lab
```

La requête doit atteindre les Pods sélectionnés si les ressources et le réseau du cluster fonctionnent correctement.

### Étape 4 : modifier le nombre de réplicas

```bash
kubectl scale deployment api-lab --replicas=3
kubectl get pods
kubectl get endpointslice \
  -l kubernetes.io/service-name=api-lab
```

Observer les changements d'endpoints du Service sans changer son nom DNS.

### Étape 5 : examiner une erreur de sélecteur

Modifier temporairement le sélecteur du Service dans un manifeste séparé, puis appliquer la modification. Vérifier les EndpointSlice.

Restaurer ensuite le sélecteur correct et confirmer le retour des endpoints.

### Résultat attendu

Le nom du Service reste stable tandis que la liste des Pods backend évolue avec le Deployment.

## 18. Atelier pratique 2 : segmentation réseau

### Objectif

Autoriser l'accès à un Pod backend seulement depuis un Pod disposant du label prévu.

**Prérequis :** la solution réseau du cluster doit appliquer les NetworkPolicy.

### Étape 1 : créer une API et une base de données simulées

Créer les Pods de test avec des labels distincts, par exemple :

```text
app=api
app=database
```

Pour effectuer un laboratoire reproductible, on peut utiliser deux Deployments de test et un Service `ClusterIP` pour le backend.

### Étape 2 : appliquer la politique

Utiliser `database-allow-api` décrit dans la section NetworkPolicy, en s'assurant que le Service cible le Pod `app: database` et que le Pod client autorisé porte `app: api`.

### Étape 3 : tester plusieurs chemins

- Depuis un Pod autorisé, essayer de joindre le port backend.
- Depuis un Pod sans le label `app: api`, effectuer le même test.
- Vérifier les labels et les événements si le résultat ne correspond pas aux attentes.

### Étape 4 : interpréter le résultat

La politique vise uniquement le trafic entrant vers les Pods de base de données et ne définit pas les restrictions de sortie des Pods API.

Pour une politique de production, compléter l'analyse par les flux sortants nécessaires, le DNS, la supervision et les tests de non-régression.

## 19. Atelier pratique 3 : PVC et données persistantes

### Objectif

Créer un PVC, écrire un fichier, recréer le Pod et vérifier que le fichier est toujours présent.

### Étape 1 : inspecter le stockage disponible

```bash
kubectl get storageclass
kubectl get pv
```

Confirmer qu'un provisionneur et une classe appropriés sont disponibles. Si le cluster ne possède aucun stockage dynamique adapté, le PVC peut rester en `Pending` ; dans ce cas, suivre la procédure de stockage propre à l'environnement.

### Étape 2 : appliquer le PVC et le Pod

Créer `pvc-lab.yaml` :

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-lab
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-lab-stockage
spec:
  containers:
    - name: app
      image: busybox:1.36
      command:
        - sh
        - -c
        - "echo donnees-durables > /data/donnees.txt; sleep 3600"
      volumeMounts:
        - name: stockage
          mountPath: /data
  volumes:
    - name: stockage
      persistentVolumeClaim:
        claimName: pvc-lab
```

Appliquer :

```bash
kubectl apply -f pvc-lab.yaml
kubectl get pvc
kubectl get pod pod-lab-stockage
```

Attendre que le PVC et le Pod soient prêts, puis vérifier le fichier :

```bash
kubectl exec pod-lab-stockage -- cat /data/donnees.txt
```

### Étape 3 : supprimer et recréer le Pod

```bash
kubectl delete pod pod-lab-stockage
kubectl apply -f pvc-lab.yaml
```

Attendre que le Pod redevienne opérationnel.

Puis :

```bash
kubectl exec pod-lab-stockage -- cat /data/donnees.txt
```

### Résultat attendu

Le fichier reste présent car les données se trouvent sur le volume persistant, et non uniquement dans le système de fichiers éphémère du conteneur.

Si le volume ne se monte pas, examiner le PVC, le PV, les événements et les contraintes du pilote avant de relancer plusieurs fois les commandes.

## 20. Projet final : déployer une application web avec réseau et stockage

### 20.1 Cahier des charges

Construire une architecture qui comprend :

- un frontend HTTP ;
- un Service stable pour le frontend ;
- une API interne ;
- un Service pour l'API ;
- une base de données ou un composant de stockage simulé ;
- un PVC pour les données persistantes ;
- un StatefulSet pour le composant qui a besoin d'une identité et d'un stockage stables ;
- une NetworkPolicy qui restreint l'accès à la base ;
- un moyen documenté d'accéder à l'application depuis l'extérieur ;
- des commandes de diagnostic reproductibles.

### 20.2 Architecture cible

```text
                       CLIENT
                         |
                         v
                +-----------------+
                | Gateway /       |
                | contrôleur HTTP |
                +-----------------+
                         |
                         v
                +-----------------+
                | Service frontend|
                +-----------------+
                         |
                         v
                +-----------------+
                | Pods frontend   |
                +-----------------+
                         |
                         v
                +-----------------+
                | Service API     |
                +-----------------+
                         |
                         v
                +-----------------+
                | Pods API        |
                +-----------------+
                         |
                         | autorisé par NetworkPolicy
                         v
                +-----------------+
                | Base de données |
                | StatefulSet     |
                +-----------------+
                         |
                         v
                +-----------------+
                | PVC / PV         |
                +-----------------+
                         |
                         v
                +-----------------+
                | Stockage durable|
                +-----------------+
```

Pour un projet de laboratoire, la base de données peut être remplacée dans un premier temps par un service simulé. Pour un environnement de production, choisir une image de base de données prise en charge, configurer l'initialisation sécurisée, les secrets, les sauvegardes et les mécanismes applicatifs de reprise.

### 20.3 Étapes de réalisation

**Étape 1 : préparer le namespace et les labels**

Créer le namespace dédié, définir les labels des Pods et documenter les sélecteurs de tous les Services.

**Étape 2 : déployer l'application**

Créer les Deployments nécessaires, les sondes, les ressources et les Services correspondants. Confirmer que les Pods sont prêts.

**Étape 3 : créer le stockage**

Créer le PVC et vérifier son état. Si le composant est stateful, utiliser un StatefulSet avec un `volumeClaimTemplates` adapté au besoin.

**Étape 4 : contrôler le réseau interne**

Vérifier les EndpointSlice, résoudre les Services par DNS et tester les communications attendues.

**Étape 5 : appliquer les NetworkPolicy**

Définir les communications autorisées. Tester aussi les flux qui doivent être bloqués. Vérifier la prise en charge effective des NetworkPolicy par le réseau du cluster.

**Étape 6 : exposer le frontend**

Utiliser une Gateway API prise en charge ou une autre solution d'entrée maintenue, selon l'infrastructure. Configurer les noms d'hôtes et le protocole HTTPS si nécessaire.

**Étape 7 : valider le stockage**

Écrire des données de test, recréer un Pod consommateur lorsque cela est approprié et vérifier que les données attendues restent disponibles.

**Étape 8 : rédiger le plan d'exploitation**

Documenter les vérifications, les alertes, la procédure de sauvegarde, les restaurations, les limites du stockage et la procédure de dépannage.

### 20.4 Critères de réussite

Le projet est réussi lorsque :

- le frontend est accessible par le point d'entrée prévu ;
- les Services possèdent les endpoints attendus ;
- le DNS fonctionne entre les composants ;
- l'API ne dépend pas d'adresses IP de Pods configurées en dur ;
- l'accès réseau à la base est limité aux sources prévues ;
- les données persistent selon le modèle de stockage choisi ;
- les erreurs réseau et stockage peuvent être investiguées avec une méthode claire ;
- la configuration est conservée dans des manifestes versionnés ;
- la procédure de restauration a été testée et documentée.

## 21. Exercices de révision

### Exercice 1 : Service inaccessible

Un Pod API répond sur le port 8080. Le Service est configuré avec `port: 80` et `targetPort: 8000`.

Quel est le problème potentiel ?

### Exercice 2 : DNS entre namespaces

Un Pod du namespace `frontend` doit contacter le Service `api` du namespace `backend`.

Quel nom DNS peut-il utiliser ?

### Exercice 3 : aucun endpoint

Le Service cible le label `app: api`, mais les Pods portent `app: api-v2`.

Quelles ressources faut-il examiner et corriger ?

### Exercice 4 : PVC en attente

Un PVC de 100 Gio reste en `Pending`. Le cluster ne dispose que d'un volume statique disponible de 20 Gio et aucun provisionneur dynamique ne peut créer de nouveau volume.

Pourquoi la demande ne peut-elle pas être satisfaite dans cet état ?

### Exercice 5 : persistance

Pourquoi un fichier écrit uniquement dans le système de fichiers du conteneur peut-il disparaître lorsque le Pod est remplacé ?

### Exercice 6 : NetworkPolicy

Une politique limite le trafic entrant vers la base de données aux Pods `app: api`. Un autre Pod du même namespace n'a pas ce label.

Que faut-il vérifier pour conclure que ce Pod ne peut pas communiquer avec la base ?

### Exercice 7 : StatefulSet

Pourquoi utiliser un StatefulSet avec des revendications de volume distinctes plutôt qu'un Deployment ordinaire pour certains membres d'une base de données distribuée ?

### Exercice 8 : exposition HTTP

Pourquoi la création d'une ressource Ingress ou HTTPRoute ne garantit-elle pas qu'une application soit accessible depuis Internet ?

## 22. Corrigés des exercices

### Corrigé 1

Le Service transmet le trafic vers le port 8000 des Pods, alors que l'application écoute sur 8080. Si aucun processus n'écoute sur 8000, la connexion échouera. Il faut corriger `targetPort` ou la configuration de l'application.

### Corrigé 2

Le client peut utiliser `api.backend` ou le nom complet `api.backend.svc.cluster.local`, en supposant que `cluster.local` soit le domaine de cluster.

### Corrigé 3

Examiner le sélecteur du Service avec `kubectl describe svc`, les labels des Pods et les EndpointSlice. Corriger les labels ou le sélecteur afin qu'ils correspondent.

### Corrigé 4

Le volume de 20 Gio ne satisfait pas une demande de 100 Gio et aucun provisionneur ne peut créer le stockage supplémentaire. Il faut disposer d'un stockage compatible et suffisamment grand ou revoir la demande.

### Corrigé 5

Le système de fichiers du conteneur n'est pas un stockage durable indépendant du cycle de vie du conteneur. Les données doivent être placées sur un volume approprié pour répondre à un besoin de persistance.

### Corrigé 6

Vérifier que les NetworkPolicy sont réellement prises en charge par le CNI, que la politique sélectionne les bons Pods et qu'aucune autre politique ne permet le flux. Vérifier également l'adresse et le port réellement contactés. Les politiques qui s'appliquent s'additionnent : une politique de refus ne neutralise pas une autorisation ajoutée par une autre politique.

### Corrigé 7

Un StatefulSet fournit des identités stables et peut créer une revendication persistante distincte pour chaque ordinal. C'est utile lorsque chaque membre doit conserver ses propres données. Cela ne remplace toutefois pas la réplication logique ou le consensus propre à l'application.

### Corrigé 8

Il faut un contrôleur ou une implémentation qui traite la ressource, ainsi qu'une infrastructure réseau permettant d'atteindre le point d'entrée. Il faut aussi des règles valides, une Gateway ou un contrôleur opérationnel, des backends prêts et, si nécessaire, un DNS public correctement configuré.

## 23. Bonnes pratiques en production

### Réseau

- Utiliser des Services pour éviter la dépendance aux IP individuelles des Pods.
- Choisir soigneusement `port` et `targetPort`.
- Vérifier les labels et les EndpointSlice après chaque modification importante.
- Utiliser le DNS du cluster pour la découverte des Services.
- Prévoir un contrôleur d'entrée maintenu et adapté au cluster.
- Préférer une implémentation de Gateway API adaptée pour les nouveaux projets lorsque ce choix correspond aux besoins et à la plateforme.
- Utiliser HTTPS pour les communications publiques sensibles.
- Définir des NetworkPolicy correspondant aux flux nécessaires.
- Tester les effets des politiques avant leur déploiement en production.
- Documenter les règles réseau et les procédures de diagnostic.

### Stockage

- Utiliser des PVC pour les besoins de persistance.
- Vérifier la StorageClass, le pilote et les modes d'accès.
- Choisir soigneusement la politique de récupération des volumes.
- Ne jamais supposer qu'un PVC en `Bound` garantit une sauvegarde.
- Mettre en place des sauvegardes adaptées et tester les restaurations.
- Surveiller la capacité disponible et l'état du provisionneur.
- Contrôler les permissions des fichiers montés.
- Utiliser un StatefulSet lorsque l'identité et le stockage des Pods doivent être stables.
- Vérifier les contraintes de topologie et de montage du fournisseur.
- Documenter les conditions de reprise après panne.

### Exploitation

- Conserver les manifestes dans un système de gestion de versions.
- Préférer les déploiements déclaratifs et reproductibles.
- Utiliser des labels cohérents et documentés.
- Surveiller les événements, l'état des Pods et les métriques du réseau et du stockage.
- Limiter les privilèges et les accès aux Secrets.
- Tester les procédures de reprise avant qu'un incident réel ne se produise.

## 24. Fiche de commandes essentielles

### Réseau et Services

```bash
kubectl get pods -o wide
kubectl get svc
kubectl get svc -A
kubectl describe svc nom-du-service

kubectl get endpointslice
kubectl get endpointslice \
  -l kubernetes.io/service-name=nom-du-service

kubectl get networkpolicy
kubectl describe networkpolicy nom-de-la-politique

kubectl get gatewayclass
kubectl get gateway -A
kubectl get httproute -A
kubectl describe gateway nom-de-la-gateway
kubectl describe httproute nom-de-la-route
```

### DNS

```bash
kubectl get svc -n kube-system
kubectl get pods -n kube-system
kubectl get endpointslice -n kube-system
kubectl exec nom-du-pod -- nslookup kubernetes.default
kubectl exec nom-du-pod -- cat /etc/resolv.conf
```

### Stockage

```bash
kubectl get pvc
kubectl get pvc -A
kubectl describe pvc nom-du-pvc

kubectl get pv
kubectl describe pv nom-du-pv

kubectl get storageclass
kubectl describe storageclass nom-de-la-classe

kubectl get statefulset
kubectl describe statefulset nom-du-statefulset
```

### Événements et logs

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl describe pod nom-du-pod
kubectl logs nom-du-pod
kubectl logs nom-du-pod --previous
```

Les logs précédents sont utiles lorsqu'un conteneur a redémarré et que les journaux de son instance antérieure sont encore accessibles.

## 25. Glossaire

**CNI** : interface permettant à un environnement de conteneurs de configurer le réseau.

**ClusterIP** : adresse de Service destinée à la communication interne au cluster.

**CoreDNS** : serveur DNS couramment utilisé pour la découverte des ressources réseau Kubernetes.

**EndpointSlice** : ressource qui représente les endpoints associés à un Service.

**Egress** : trafic sortant d'un Pod.

**Ingress** : trafic entrant dans un Pod ; le terme désigne aussi une API Kubernetes historique de routage HTTP/HTTPS.

**Gateway API** : famille d'API et de ressources permettant de décrire l'infrastructure d'entrée et les règles de routage.

**NetworkPolicy** : ressource qui définit des règles d'accès réseau entre Pods, espaces et destinations ciblées.

**PersistentVolume (PV)** : ressource représentant un volume de stockage disponible dans Kubernetes.

**PersistentVolumeClaim (PVC)** : demande de stockage consommée par un Pod.

**Provisionnement dynamique** : création ou attribution d'un volume à partir d'une demande de stockage et d'une StorageClass.

**ReadWriteMany (RWX)** : mode d'accès permettant, si le stockage le prend en charge, un montage en lecture-écriture depuis plusieurs nœuds.

**ReadWriteOnce (RWO)** : mode d'accès en lecture-écriture associé à un seul nœud à la fois, selon les capacités du volume.

**ReadWriteOncePod (RWOP)** : mode restreignant le montage en lecture-écriture à un seul Pod lorsque les prérequis sont réunis.

**Service headless** : Service dont le champ `clusterIP` est réglé sur `None`, couramment utilisé pour la découverte directe des endpoints.

**StatefulSet** : contrôleur destiné aux applications dont les Pods ont besoin d'identités stables et souvent de volumes persistants distincts.

**StorageClass** : ressource qui décrit une classe de stockage et le mécanisme utilisé pour la provisionner.

**TargetPort** : port cible vers lequel le Service transmet le trafic sur les Pods sélectionnés.

## 26. Références officielles

- Modèle réseau, Services et découverte réseau : https://kubernetes.io/docs/concepts/services-networking/
- Services Kubernetes : https://kubernetes.io/docs/concepts/services-networking/service/
- DNS des Services et des Pods : https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
- Diagnostic des Services : https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/
- Diagnostic DNS : https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/
- Ingress : https://kubernetes.io/docs/concepts/services-networking/ingress/
- Gateway API : https://kubernetes.io/docs/concepts/services-networking/gateway/
- Politiques réseau : https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Documentation du stockage : https://kubernetes.io/docs/concepts/storage/
- Volumes persistants : https://kubernetes.io/docs/concepts/storage/persistent-volumes/
- StorageClass : https://kubernetes.io/docs/concepts/storage/storage-classes/
- Volumes Kubernetes : https://kubernetes.io/docs/concepts/storage/volumes/
- StatefulSets : https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- Snapshots de volumes : https://kubernetes.io/docs/concepts/storage/volume-snapshots/
- Dépannage général : https://kubernetes.io/docs/tasks/debug/
- Annonce officielle de la retraite d'Ingress NGINX : https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/

## Conclusion

Le réseau Kubernetes fournit une découverte stable des applications et une connectivité qui ne dépend pas directement des adresses IP individuelles des Pods. Les Services, le DNS, les EndpointSlice, Gateway API et les NetworkPolicy jouent chacun un rôle distinct dans cette architecture.

Le stockage Kubernetes sépare les données du cycle de vie des conteneurs. Les PVC, PV, StorageClass et StatefulSets permettent de formaliser les demandes de stockage et de gérer les identités persistantes, à condition que les pilotes et l'infrastructure soient correctement configurés.

La compétence intermédiaire consiste à ne pas seulement créer ces ressources, mais aussi à vérifier leur fonctionnement réel : tester les connexions, examiner les endpoints, analyser les événements, valider les montages, limiter les accès et prouver que les données peuvent être récupérées après une interruption.