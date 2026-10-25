# Service Mesh (Istio, Linkerd)

## 1. Objectifs du niveau expert

Ce cours approfondit les connaissances acquises sur Kubernetes, les réseaux de conteneurs, la sécurité, la supervision, l'automatisation et les déploiements CI/CD.

À la fin de ce niveau, il faut être capable de :

- Concevoir une architecture Service Mesh pour une plateforme distribuée.
- Comprendre le fonctionnement du plan de contrôle et du plan de données.
- Comparer Istio et Linkerd à partir de contraintes techniques et opérationnelles.
- Déployer et faire évoluer un maillage de services sur Kubernetes.
- Mettre en place le chiffrement mTLS et des politiques d'autorisation.
- Réaliser des déploiements canary, des répartitions de trafic et des migrations progressives.
- Configurer les délais d'attente, les tentatives, les disjoncteurs et la gestion des pannes.
- Relier le Service Mesh aux métriques, aux traces, aux journaux et aux objectifs SRE.
- Automatiser l'installation et la configuration avec Terraform, Helm, GitOps et CI/CD.
- Diagnostiquer les problèmes de routage, de certificats, de politiques et de performances.
- Définir une stratégie d'exploitation, de mise à niveau et de retour arrière.

Le niveau expert ne consiste pas à activer toutes les fonctionnalités disponibles. Il consiste à sélectionner celles qui résolvent un problème réel, à mesurer leurs effets et à limiter leur complexité.

## 2. Positionnement dans le parcours DevOps

Les cours précédents fournissent les fondations nécessaires.

| Domaine déjà étudié | Utilisation dans le Service Mesh |
|---|---|
| Docker | Construction et distribution des images des applications et des composants du mesh |
| Kubernetes : bases | Pods, Deployments, Services, namespaces, RBAC et contrôleurs |
| Kubernetes : réseau et stockage | DNS, routage, CNI, NetworkPolicy, connectivité et persistance |
| Kubernetes avancé et sécurité | Identités, politiques, certificats, admission et réduction des privilèges |
| CI/CD avec GitHub Actions et GitLab CI | Tests, validation, publication et promotion des versions |
| Terraform | Provisionnement des clusters et des dépendances d'infrastructure |
| IaC à grande échelle | Réutilisation des modules, séparation des environnements et gouvernance |
| Ansible | Configuration des hôtes et opérations complémentaires hors du cluster |
| SRE : SLI, SLO et incidents | Latence, disponibilité, budgets d'erreur et diagnostic |

### 2.1 Architecture globale du parcours

```text
                    CODE SOURCE
                         |
                         v
               CI : TESTS ET QUALITÉ
                         |
                         v
                IMAGE CONTENEURISÉE
                         |
                         v
                REGISTRE D'IMAGES
                         |
                         v
        TERRAFORM / PLATEFORME KUBERNETES
                         |
                         v
                 CLUSTER KUBERNETES
                         |
                         v
                  SERVICE MESH
              +----------+----------+
              |                     |
              v                     v
        SÉCURITÉ RÉSEAU       TRAFIC APPLICATIF
        mTLS / identités      routage / résilience
              |                     |
              +----------+----------+
                         |
                         v
                 OBSERVABILITÉ
             métriques / traces / logs
                         |
                         v
                   SRE / SLO
                         |
                         v
             AMÉLIORATION CONTINUE
```

Le Service Mesh n'est pas un remplacement de Kubernetes, du CNI, de la CI/CD ou de la supervision. Il complète ces mécanismes.

## 3. Comprendre le Service Mesh en profondeur

### 3.1 Le problème des communications entre microservices

Considérons une application composée de plusieurs services :

```text
                         UTILISATEUR
                              |
                              v
                         API GATEWAY
                              |
                              v
                         SERVICE WEB
                              |
                +-------------+-------------+
                |             |             |
                v             v             v
             CATALOGUE      COMMANDES     IDENTITÉ
                |             |             |
                v             v             v
             PRODUITS       PAIEMENT      UTILISATEURS
```

Sans Service Mesh, chaque application peut devoir implémenter elle-même :

- La sélection des instances disponibles.
- Les délais d'attente réseau.
- Les tentatives de reconnexion.
- La propagation des identifiants de requête.
- La collecte de métriques réseau.
- La validation des certificats.
- Le chiffrement des communications.
- La limitation des appels.
- La gestion de certains échecs.

Cette approche crée des différences entre les langages, les frameworks et les équipes.

Une application Python peut appliquer une politique de délai d'attente différente de celle d'un service Java. Une bibliothèque de journalisation peut également produire des informations différentes.

Le Service Mesh déplace une partie de ces responsabilités dans une infrastructure réseau dédiée.

### 3.2 Définition

Un Service Mesh est une couche d'infrastructure chargée de contrôler, sécuriser et observer les communications entre services.

Il agit principalement sur les communications internes, souvent appelées trafic est-ouest.

Il peut apporter :

- Une identité cryptographique aux workloads.
- Le chiffrement des communications.
- Des politiques d'accès.
- Un routage avancé.
- Des mécanismes de résilience.
- Des métriques réseau et applicatives.
- Une gestion centralisée des configurations de communication.

Le terme « centralisée » désigne la gestion de la configuration. Le trafic lui-même est généralement traité par des composants distribués proches des applications.

### 3.3 Ce que le Service Mesh ne fait pas

Un Service Mesh ne remplace pas :

- Le système de gestion des utilisateurs de l'application.
- L'autorisation métier.
- Le pare-feu réseau de l'infrastructure.
- Les NetworkPolicy du cluster.
- Le système de gestion des secrets applicatifs.
- Les tests fonctionnels.
- La supervision des bases de données.
- Le contrôle des accès à l'API Kubernetes.
- La sauvegarde des données.
- La conception correcte des transactions distribuées.

Par exemple, le mesh peut autoriser un service de commande à contacter un service de paiement. Il ne garantit pas que la commande possède un montant valide ni que le client est autorisé à acheter un produit.

## 4. Architecture interne : plan de contrôle et plan de données

### 4.1 Plan de contrôle

Le plan de contrôle, ou control plane, distribue les configurations et gère les fonctions de coordination.

Selon l'implémentation, il peut notamment :

- Observer les ressources Kubernetes.
- Découvrir les services et leurs instances.
- Générer ou distribuer des configurations de proxy.
- Gérer les identités et les certificats.
- Contrôler les politiques.
- Exposer des métriques sur le fonctionnement du mesh.

### 4.2 Plan de données

Le plan de données, ou data plane, transporte et traite le trafic.

Il comprend les composants qui interceptent ou prennent en charge les communications des workloads.

Dans Istio, le plan de données peut utiliser des proxys Envoy en sidecar ou l'architecture ambient avec ztunnel et, lorsque nécessaire, des proxys waypoint.

Linkerd utilise des proxys légers intégrés aux workloads maillés.

### 4.3 Diagramme d'architecture

```text
                    PLAN DE CONTRÔLE
              +--------------------------+
              | Gestion des configurations|
              | Découverte des services   |
              | Identités et certificats  |
              | Politiques                |
              +-------------+------------+
                            |
                   Configurations
                   et informations
                            |
            +---------------+---------------+
            |                               |
            v                               v
     PLAN DE DONNÉES                 PLAN DE DONNÉES
       NŒUD A                          NŒUD B
  +----------------+              +----------------+
  | Application A  |              | Application B  |
  |      |         |              |      |         |
  |     Proxy      |==============|     Proxy      |
  +----------------+  Trafic      +----------------+
                       sécurisé

     Les proxys traitent le trafic.
     Le plan de contrôle configure les proxys.
```

Le diagramme illustre le modèle sidecar. Les détails changent en mode ambient.

### 4.4 Une distinction essentielle

Le plan de contrôle n'est généralement pas sur le chemin de chaque requête applicative.

Si le plan de contrôle devient temporairement indisponible, les proxys peuvent souvent continuer à utiliser leur dernière configuration valide. Le comportement exact dépend de l'implémentation, des certificats, des mécanismes de renouvellement et de la configuration.

Il faut donc distinguer :

- La disponibilité du trafic applicatif.
- La disponibilité de l'administration du mesh.
- La capacité à modifier les politiques.
- La capacité à renouveler les identités.
- La capacité à intégrer de nouveaux workloads.

Cette distinction est fondamentale pour la conception de haute disponibilité.

## 5. Istio et Linkerd : comparaison architecturale

### 5.1 Istio

Istio est une plateforme Service Mesh riche en fonctionnalités.

Ses composants peuvent inclure :

- `istiod`, qui gère notamment la configuration et les identités du mesh.
- Envoy, utilisé pour le traitement du trafic en mode sidecar et dans les composants waypoint.
- ztunnel en mode ambient.
- Des passerelles d'entrée et de sortie.
- Des intégrations d'observabilité.

Istio convient notamment lorsque l'organisation a besoin de politiques réseau avancées, de routage détaillé, de fonctionnalités L7, de gestion des passerelles et d'architectures variées.

### 5.2 Linkerd

Linkerd vise une expérience opérationnelle plus simple et un plan de données léger.

Il fournit notamment :

- Le chiffrement mTLS entre workloads compatibles.
- Des identités de service.
- Des métriques de communication.
- Des mécanismes de routage et de répartition selon les fonctionnalités et extensions utilisées.
- Des politiques d'autorisation.
- Des capacités multiclusters.

Linkerd convient notamment aux équipes qui souhaitent sécuriser et observer leurs communications sans adopter immédiatement une plateforme de routage très complexe.

### 5.3 Tableau comparatif

| Critère | Istio | Linkerd |
|---|---|---|
| Objectif général | Plateforme très configurable | Mesh centré sur la simplicité opérationnelle |
| Plan de données | Envoy en sidecar ou ambient | Proxys légers dans les workloads maillés |
| mTLS | Oui | Oui |
| Identités de workload | Oui | Oui |
| Politiques d'autorisation | Très riches | Politiques dédiées |
| Routage L7 avancé | Très riche | Plus ciblé, selon les fonctionnalités utilisées |
| Déploiements canary | Oui | Oui, selon les mécanismes de répartition configurés |
| Observabilité | Métriques, traces, intégrations | Métriques et intégrations |
| Architecture sans sidecar | Ambient | Architecture propre à Linkerd, à évaluer selon la version et les capacités disponibles |
| Complexité de configuration | Peut être importante | Souvent plus faible |
| Intégration à Kubernetes | Forte | Forte |

Il ne faut pas conclure qu'une solution est systématiquement plus performante que l'autre. Le résultat dépend du matériel, du trafic, des fonctionnalités activées, du nombre de services, de la topologie et des versions.

### 5.4 Comment choisir ?

Choisir Istio lorsque les besoins justifient, par exemple :

- Des règles de routage HTTP ou gRPC très précises.
- Une gestion avancée des passerelles.
- Des politiques de sécurité détaillées.
- Un besoin de combiner plusieurs modes de plan de données.
- Des scénarios de trafic et d'intégration particulièrement variés.

Évaluer Linkerd lorsque les priorités sont :

- La simplicité de déploiement.
- Le chiffrement des communications internes.
- Une observabilité directement exploitable.
- Une réduction de la charge opérationnelle.
- Une gestion des politiques qui répond aux besoins sans multiplier les abstractions.

La décision doit être prise après un prototype représentatif, pas uniquement à partir d'une liste de fonctionnalités.

## 6. Les modèles de plan de données d'Istio

### 6.1 Mode sidecar

Un proxy est ajouté à chaque Pod participant au mesh.

```text
+----------------------------------+
| POD                               |
|                                  |
|  +----------------------------+  |
|  | Application                |  |
|  +-------------+--------------+  |
|                |                 |
|  +-------------v--------------+  |
|  | Proxy Envoy                |  |
|  +----------------------------+  |
+----------------------------------+
```

Avantages :

- Modèle bien établi.
- Nombreuses possibilités de configuration L7.
- Bonne intégration aux politiques et au routage Istio.

Inconvénients :

- Ressources supplémentaires pour chaque Pod.
- Cycle de vie du proxy à gérer.
- Injection et redémarrage des workloads à prendre en compte.
- Diagnostic parfois plus complexe.

### 6.2 Mode ambient

Le mode ambient sépare le traitement L4 et le traitement L7 optionnel.

```text
                  NŒUD KUBERNETES
+--------------------------------------------------+
|                                                  |
|  +-------------+       +-------------+           |
|  | Application |       | Application |           |
|  | Pod A       |       | Pod B       |           |
|  +------+------+       +------+------+           |
|         |                     |                  |
|         +----------+----------+                  |
|                    |                             |
|             +------v------+                      |
|             |   ztunnel   |                      |
|             |     L4      |                      |
|             +------+------+                      |
|                    |                             |
+--------------------|-----------------------------+
                     |
             Trafic chiffré
                     |
             +-------v-------+
             | ztunnel       |
             | autre nœud    |
             +---------------+

      Pour des fonctions L7 :
      le trafic peut également passer par un waypoint Envoy.
```

Le composant ztunnel gère notamment la connectivité sécurisée et les fonctions L4. Le waypoint fournit des fonctions L7 lorsque celles-ci sont nécessaires.

Le mode ambient ne signifie donc pas que toutes les fonctions avancées L7 sont activées automatiquement.

### 6.3 Choisir entre sidecar et ambient

Privilégier le sidecar lorsque :

- L'environnement repose déjà fortement sur cette architecture.
- Les besoins L7 sont importants.
- Les procédures d'exploitation existantes sont adaptées.

Évaluer ambient lorsque :

- Le coût du sidecar constitue une contrainte.
- Le chiffrement et les politiques L4 sont les premiers objectifs.
- L'équipe souhaite activer les fonctions L7 uniquement sur certains services.

Les capacités, limitations et niveaux de maturité peuvent évoluer. Avant une migration, consulter la documentation correspondant exactement à la version cible.

## 7. Préparer un laboratoire Kubernetes

Les exemples de ce cours utilisent Kubernetes et Istio comme environnement de référence. Les sections Linkerd montrent les différences de méthode.

### 7.1 Prérequis

Installer ou disposer de :

- Un cluster Kubernetes de test.
- `kubectl`.
- Le client `istioctl` pour les exercices Istio.
- Helm, si l'installation choisie utilise Helm.
- Un accès administrateur suffisant pour installer les CRD et composants système.
- Un registre d'images si l'on déploie des applications personnalisées.

Les exemples ne supposent pas que le cluster est déjà prêt à recevoir une charge de production.

Vérifier l'accès au cluster :

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get namespaces
```

Vérifier la version du client :

```bash
kubectl version --client
```

Le client `istioctl` doit être compatible avec la version d'Istio choisie :

```bash
istioctl version
```

### 7.2 Créer un namespace de laboratoire

```bash
kubectl create namespace mesh-lab
```

Ne pas utiliser le namespace `default` pour tous les exercices. Un namespace dédié facilite l'isolation, les politiques et le nettoyage.

### 7.3 Installer Istio

Choisir une version prise en charge et suivre sa documentation officielle.

Pour un laboratoire, l'installation avec le profil de démonstration peut être utilisée lorsque celui-ci est disponible dans la distribution choisie :

```bash
istioctl install --set profile=demo -y
```

Le profil de démonstration est destiné aux tests et aux évaluations. Il ne constitue pas un profil de production recommandé.

Vérifier l'installation :

```bash
kubectl get pods -n istio-system
kubectl get services -n istio-system
istioctl verify-install
```

La commande de vérification peut prendre un certain temps selon le cluster.

### 7.4 Activer l'injection sidecar

Pour le mode sidecar, l'injection automatique peut être activée sur le namespace :

```bash
kubectl label namespace mesh-lab istio-injection=enabled --overwrite
```

Les nouveaux Pods créés dans ce namespace pourront recevoir un sidecar selon la configuration du webhook.

Vérifier le label :

```bash
kubectl get namespace mesh-lab --show-labels
```

Un Pod déjà créé n'est pas automatiquement modifié par l'ajout du label. Il faut généralement recréer les workloads concernés.

## 8. Déployer une application de référence

Pour étudier le trafic entre services, utilisons trois composants :

- `frontend` : point d'entrée applicatif.
- `reviews` : service qui renvoie des réponses de versions différentes.
- `details` : service auxiliaire.

Dans le cadre de ce laboratoire, on peut utiliser les exemples maintenus dans la distribution Istio. Cela évite de construire une application artificielle différente pour chaque exercice.

### 8.1 Déployer les applications d'exemple

Si le paquet Istio utilisé contient les exemples habituels :

```bash
kubectl apply -n mesh-lab -f samples/bookinfo/platform/kube/bookinfo.yaml
```

Le chemin dépend du répertoire dans lequel le paquet Istio a été extrait.

Vérifier les ressources :

```bash
kubectl get deployments,services,pods -n mesh-lab
```

Vérifier que les conteneurs sont prêts :

```bash
kubectl rollout status deployment/productpage -n mesh-lab
```

Si le nom du déploiement diffère dans l'exemple choisi, adapter la commande.

### 8.2 Vérifier la topologie

```bash
kubectl get pods -n mesh-lab -o wide
kubectl get endpointslices -n mesh-lab
kubectl describe service productpage -n mesh-lab
```

Avec le mode sidecar, vérifier la présence des conteneurs proxy :

```bash
kubectl get pods -n mesh-lab \
  -o jsonpath='{range .items[*]}{.metadata.name}{" : "}{.spec.containers[*].name}{"\n"}{end}'
```

La présence du proxy ne prouve pas à elle seule que tout le trafic est correctement intercepté. Il faut aussi vérifier les règles de routage, la configuration du mesh et les résultats des tests.

## 9. Identité des workloads et mTLS

### 9.1 Pourquoi chiffrer le trafic interne ?

Le réseau interne d'un cluster n'est pas automatiquement digne de confiance.

Un workload compromis peut tenter de communiquer avec d'autres services. Une personne disposant d'un accès au cluster peut également avoir des possibilités d'observation ou de modification du trafic selon ses privilèges.

Le mTLS apporte deux fonctions principales :

1. Le chiffrement du canal.
2. L'authentification mutuelle des parties qui utilisent des certificats compatibles.

Il ne garantit pas que l'application est exempte de vulnérabilités. Il ne remplace pas non plus les contrôles d'autorisation.

### 9.2 Identité de service

Un mesh peut représenter une identité de workload à l'aide d'une identité SPIFFE.

Exemple conceptuel :

```text
spiffe://cluster.local/ns/production/sa/orders
```

Cette identité représente ici le compte de service `orders` du namespace `production` dans le domaine d'identité `cluster.local`.

L'identité exacte dépend de la configuration du mesh.

Les certificats doivent être émis, renouvelés et validés correctement. Il faut éviter les certificats statiques partagés entre toutes les applications.

### 9.3 Modèle de confiance

```text
         AUTORITÉ DE CONFIANCE
                   |
          Émet les identités
                   |
          +--------+--------+
          |                 |
          v                 v
      Service A         Service B
      Certificat A      Certificat B
          |                 |
          +--------mTLS------+
                   |
             Canal chiffré
```

Les deux côtés authentifient leurs identités selon la configuration et la chaîne de confiance.

### 9.4 Activer une politique mTLS Istio

En mode sidecar, une politique `PeerAuthentication` peut imposer le mTLS :

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: mesh-lab-strict
  namespace: mesh-lab
spec:
  mtls:
    mode: STRICT
```

Appliquer la politique :

```bash
kubectl apply -f peer-authentication.yaml
```

Le mode `STRICT` exige le mTLS pour le trafic entrant couvert par cette politique.

Avant de l'appliquer, vérifier que tous les clients concernés sont compatibles avec la configuration du mesh. Des clients non maillés ou des systèmes externes peuvent perdre leur connectivité.

Dans les versions et modes de données où les mécanismes de sécurité diffèrent, suivre le guide spécifique à l'architecture utilisée.

### 9.5 Vérifier l'état mTLS

```bash
istioctl x describe pod NOM_DU_POD -n mesh-lab
istioctl proxy-status
```

Selon la version et le mode de données, certaines commandes d'inspection peuvent afficher des informations différentes.

Pour approfondir :

```bash
istioctl authn tls-check \
  productpage.mesh-lab.svc.cluster.local
```

Cette commande est disponible dans les versions d'Istio qui fournissent cette fonctionnalité. Vérifier son aide si elle n'est pas présente :

```bash
istioctl x --help
```

### 9.6 Erreurs fréquentes

Une politique stricte peut échouer si :

- Un client ne possède pas de proxy compatible.
- Une identité n'est pas reconnue.
- Une politique d'authentification est mal définie.
- Une autorité de certification est indisponible.
- Un port est déclaré avec un protocole incorrect.
- Un chemin de trafic ne passe pas par le mécanisme attendu.

Le dépannage doit commencer par la vérification de la topologie réelle, puis des identités, des politiques et des journaux.

## 10. Contrôle d'accès avec Istio

Le chiffrement protège le canal. L'autorisation décide qui peut utiliser un service.

### 10.1 Principe du moindre privilège

Supposons que l'architecture contienne :

```text
FRONTEND ---> ORDERS ---> PAYMENT
                    \
                     ---> INVENTORY
```

Une politique restrictive peut exiger que seul `orders` contacte `payment`.

L'objectif est de réduire les communications possibles au strict nécessaire.

### 10.2 Exemple d'autorisation

Le manifeste suivant illustre une autorisation au niveau du workload `payment`, basée sur l'identité du compte de service du client.

```yaml
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: payment-only-orders
  namespace: mesh-lab
spec:
  selector:
    matchLabels:
      app: payment
  action: ALLOW
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/mesh-lab/sa/orders"
      to:
        - operation:
            ports: ["8080"]
```

Ce manifeste suppose que :

- Les labels correspondent réellement aux Pods du service.
- Le compte de service `orders` est bien utilisé par les Pods clients.
- L'identité de confiance correspond au domaine configuré.
- Le port `8080` est le port de destination pertinent dans le workload.

Le port de destination utilisé par une politique doit être vérifié dans la topologie réelle. Le port exposé par un Service Kubernetes et le port cible du conteneur peuvent être différents.

Appliquer :

```bash
kubectl apply -f payment-authorization.yaml
```

### 10.3 Attention à la sémantique ALLOW

Dans Istio, l'introduction d'une politique `ALLOW` sur un workload peut modifier le comportement par défaut : seules les requêtes correspondant aux règles autorisées sont permises, sous réserve des autres politiques applicables.

Une politique trop restrictive peut donc interrompre des appels légitimes.

Avant un déploiement :

1. Identifier tous les clients réels.
2. Vérifier les identités de leurs comptes de service.
3. Déterminer les ports utilisés.
4. Tester dans un environnement de préproduction.
5. Déployer progressivement.
6. Mesurer les refus et vérifier les chemins critiques.

Les politiques `DENY`, `ALLOW` et `CUSTOM` ont des règles d'évaluation spécifiques. Il faut consulter la référence de sécurité correspondant à la version déployée plutôt que de supposer qu'elles se comportent comme des règles de pare-feu classiques.

## 11. Autorisation avec Linkerd

Linkerd propose des politiques basées notamment sur les workloads, les ports, les routes HTTP et les identités authentifiées.

Le principe est comparable : définir la ressource à protéger, l'identité du client et la règle d'autorisation.

### 11.1 Modèle conceptuel

```text
       CLIENT AUTHENTIFIÉ
                |
                v
          IDENTITÉ mTLS
                |
                v
       RÈGLE D'AUTORISATION
                |
         +------+------+
         |             |
         v             v
       AUTORISÉ       REFUSÉ
         |             |
         v             v
     SERVICE       ERREUR / REJET
```

### 11.2 Exemple de politique Linkerd

La définition exacte des ressources dépend de la version de Linkerd et des CRD installées. L'exemple ci-dessous montre la structure d'une politique de serveur, d'une route et d'une autorisation, à adapter à la référence de la version utilisée.

```yaml
apiVersion: policy.linkerd.io/v1beta3
kind: Server
metadata:
  name: payment-http
  namespace: mesh-lab
spec:
  podSelector:
    matchLabels:
      app: payment
  port: 8080
  proxyProtocol: HTTP/1
---
apiVersion: policy.linkerd.io/v1beta3
kind: MeshTLSAuthentication
metadata:
  name: orders-identity
  namespace: mesh-lab
spec:
  identities:
    - orders.mesh-lab.serviceaccount.identity.linkerd.cluster.local
---
apiVersion: policy.linkerd.io/v1beta3
kind: AuthorizationPolicy
metadata:
  name: payment-allow-orders
  namespace: mesh-lab
spec:
  targetRef:
    group: policy.linkerd.io
    kind: Server
    name: payment-http
  requiredAuthenticationRefs:
    - group: policy.linkerd.io
      kind: MeshTLSAuthentication
      name: orders-identity
```

**Important :** cet exemple doit être validé contre les CRD réellement installées. Les versions de l'API, les protocoles pris en charge et la syntaxe des références peuvent évoluer. Ne pas appliquer une politique de production sans validation préalable.

Inspection des CRD :

```bash
kubectl get crd | grep policy.linkerd.io
kubectl explain server --api-version=policy.linkerd.io/v1beta3
kubectl explain authorizationpolicy --api-version=policy.linkerd.io/v1beta3
```

Si la version installée n'expose pas cette API, consulter sa documentation et adapter les manifestes.

### 11.3 Mode audit

Une politique restrictive doit être introduite progressivement lorsque l'impact sur la disponibilité est important.

Un mode audit, lorsqu'il est pris en charge par le mécanisme utilisé, permet d'identifier les accès qui seraient refusés sans les bloquer immédiatement.

La procédure recommandée :

1. Inventorier les communications.
2. Déployer les règles en mode d'observation lorsqu'il existe.
3. Collecter les refus potentiels.
4. Corriger les règles.
5. Passer à l'application effective.
6. Contrôler les erreurs après déploiement.

Ne pas supposer que toutes les ressources ou tous les mécanismes de politique de chaque version prennent en charge le même mode audit.

## 12. Routage avancé avec Istio

### 12.1 Pourquoi contrôler le trafic ?

Le routage avancé permet notamment :

- De tester une nouvelle version sur une fraction du trafic.
- De séparer les utilisateurs internes et externes.
- De déplacer progressivement les requêtes.
- D'injecter des pannes dans un environnement de test.
- De reproduire un comportement problématique.
- De réduire le risque d'une mise à jour.

Le routage L7 dépend du protocole reconnu par le proxy. Pour une application HTTP, il est possible de prendre en compte les chemins, les en-têtes et les méthodes. Les possibilités diffèrent pour le trafic TCP brut.

### 12.2 Versions d'un service

```text
                  SERVICE
                     |
             +-------+-------+
             |               |
             v               v
        VERSION V1       VERSION V2
           90 %             10 %
```

La répartition peut être contrôlée avec les ressources Istio de gestion du trafic.

### 12.3 Exemple de VirtualService et DestinationRule

Supposons un service `reviews` avec deux versions, identifiées par les labels `version: v1` et `version: v2`.

`DestinationRule` définit les sous-ensembles :

```yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: reviews
  namespace: mesh-lab
spec:
  host: reviews.mesh-lab.svc.cluster.local
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
```

`VirtualService` distribue le trafic :

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: reviews
  namespace: mesh-lab
spec:
  hosts:
    - reviews.mesh-lab.svc.cluster.local
  http:
    - route:
        - destination:
            host: reviews.mesh-lab.svc.cluster.local
            subset: v1
          weight: 90
        - destination:
            host: reviews.mesh-lab.svc.cluster.local
            subset: v2
          weight: 10
```

Appliquer les ressources :

```bash
kubectl apply -f reviews-destination-rule.yaml
kubectl apply -f reviews-virtual-service.yaml
```

Cette configuration suppose que les deux versions existent réellement et que les labels correspondent aux workloads.

Un poids de 10 ne garantit pas exactement 10 % de chaque requête dans une petite série de tests. La répartition est statistique et dépend notamment des connexions, du comportement du proxy et du type de trafic.

### 12.4 Déploiement canary

Une procédure canary typique :

```text
V1 : 100 %
 |
 | Déploiement de V2
 v
V1 : 95 % / V2 : 5 %
 |
 | Vérification des indicateurs
 v
V1 : 90 % / V2 : 10 %
 |
 | Validation SLO et erreurs
 v
V1 : 50 % / V2 : 50 %
 |
 | Validation complète
 v
V1 : 0 % / V2 : 100 %
```

Les étapes et les seuils doivent être adaptés au risque métier, au volume de trafic et aux objectifs SLO.

Ne pas promouvoir automatiquement une version uniquement parce que les Pods sont `Ready`. Une application peut être prête du point de vue Kubernetes tout en présentant une latence ou un taux d'erreur inacceptable.

## 13. Gestion des pannes et résilience

### 13.1 Timeout

Un timeout limite la durée pendant laquelle une opération attend une réponse.

Sans timeout, une requête peut rester bloquée jusqu'à l'expiration d'un délai inférieur imposé par une autre couche, voire immobiliser inutilement des ressources.

Un timeout doit tenir compte :

- Du temps de traitement attendu.
- Du délai réseau.
- Des délais des services appelés.
- Du budget de latence de la requête globale.

Exemple conceptuel :

```text
CLIENT
  |
  | timeout global : 2 s
  v
SERVICE A
  |
  | timeout appel B : 800 ms
  v
SERVICE B
```

Les délais doivent être cohérents. Une requête ne doit pas pouvoir consommer plusieurs fois son budget global à travers une cascade de retries.

### 13.2 Retries

Les retries permettent de réessayer certaines requêtes qui échouent temporairement.

Ils peuvent être utiles en cas d'erreur transitoire, mais dangereux lorsqu'ils amplifient une surcharge.

Supposons que 1 000 requêtes par seconde arrivent sur un service surchargé. Si chaque requête déclenche plusieurs tentatives, le volume total peut augmenter fortement.

```text
1000 requêtes/s
       |
       v
   Service saturé
       |
       +----> Échecs
                 |
                 v
          Retries automatiques
                 |
                 v
       Charge supplémentaire
                 |
                 v
          Saturation accrue
```

Les retries doivent être limités et réservés aux erreurs qui peuvent raisonnablement être transitoires.

Ils doivent être conçus en tenant compte de l'idempotence. Une opération de paiement ne doit pas être répétée aveuglément si le premier traitement a pu réussir malgré une réponse perdue.

### 13.3 Circuit breaker

Un disjoncteur limite les conséquences d'une dépendance défaillante.

Le principe général :

- Fonctionnement normal : les appels sont autorisés.
- Défaillance persistante : certaines requêtes sont rejetées ou limitées.
- Récupération : les appels reprennent selon les mécanismes configurés.

Dans Istio, les paramètres de pool de connexions et d'éjection d'instances permettent de mettre en œuvre plusieurs comportements de résilience. Il ne faut pas confondre une limite de connexions avec un disjoncteur applicatif complet.

### 13.4 Exemple de DestinationRule

```yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata:
  name: inventory-resilience
  namespace: mesh-lab
spec:
  host: inventory.mesh-lab.svc.cluster.local
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 200
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

Ce manifeste est un exemple de configuration à tester, pas une valeur universelle pour la production.

Les seuils doivent être calibrés selon le trafic réel. Des limites trop basses peuvent dégrader le débit ; des limites trop hautes peuvent laisser une surcharge se propager.

### 13.5 Fault injection

Dans un environnement de test, Istio peut injecter des délais ou des erreurs pour vérifier le comportement des clients.

Exemple conceptuel :

```text
Requête normale
     |
     v
Proxy de test
     |
     +---- 10 % des requêtes --> Erreur simulée
     |
     +---- 90 % des requêtes --> Service réel
```

La fault injection est particulièrement utile pour tester :

- Les timeouts.
- Les retries.
- Les fallbacks.
- Les alertes.
- Les limites de dégradation.
- Les procédures d'incident.

Ne pas activer des injections de panne non maîtrisées dans un environnement de production.

## 14. Gateway API et gestion du trafic

Kubernetes propose Gateway API comme modèle extensible pour gérer le trafic entrant. Le projet définit aussi des mécanismes pour les cas d'usage Service Mesh.

Les ressources principales de Gateway API comprennent notamment :

- `GatewayClass` : classe d'implémentation.
- `Gateway` : point d'entrée réseau.
- `HTTPRoute` : règles de routage HTTP.
- `GRPCRoute` : règles de routage gRPC, selon les capacités prises en charge.

Dans un contexte mesh, certaines implémentations permettent d'associer une route directement à un Service.

### 14.1 Différence entre trafic entrant et trafic interne

```text
                  INTERNET
                      |
                      v
                  GATEWAY
                      |
                      v
                 SERVICE WEB
                      |
                      v
                 SERVICE ORDERS
                      |
                      v
                 SERVICE PAYMENT
```

Le trafic Internet vers le service web est un trafic nord-sud. Les communications entre services sont du trafic est-ouest.

Une passerelle d'entrée ne suffit pas à sécuriser les communications internes. Il faut traiter séparément les politiques, les identités et le routage interne.

### 14.2 Quand utiliser Gateway API ?

Gateway API peut être pertinent si l'organisation souhaite :

- Une API Kubernetes standardisée.
- Séparer les responsabilités entre infrastructure et applications.
- Réduire la dépendance à des ressources spécifiques d'un fournisseur.
- Gérer des routes entrantes et, avec une implémentation compatible, certaines routes internes.

Toutes les implémentations ne prennent pas en charge toutes les fonctionnalités de la même manière. Vérifier les niveaux de conformité et les limitations de la version retenue.

## 15. Observabilité du Service Mesh

Un mesh n'est utile que si son comportement peut être compris et diagnostiqué.

### 15.1 Les trois piliers

**Métriques :** volumes, taux d'erreur, latence, saturation et état des proxys.

**Journaux :** événements, erreurs, refus d'accès et problèmes de connexion.

**Traces distribuées :** parcours d'une requête à travers plusieurs services.

```text
Requête utilisateur
        |
        v
      WEB
        |
        v
     COMMANDES
        |
        v
     INVENTAIRE
        |
        v
      PAIEMENT

Trace distribuée :
[WEB]----[COMMANDES]----[INVENTAIRE]
                    \
                     \----[PAIEMENT]
```

### 15.2 Métriques RED

Les métriques RED sont particulièrement utiles pour les services HTTP :

- Rate : nombre de requêtes.
- Errors : proportion de requêtes en erreur.
- Duration : durée des requêtes.

Elles doivent être complétées par des métriques de saturation et par des indicateurs propres à l'application.

Exemple :

| Indicateur | Exemple de mesure |
|---|---|
| Débit | 800 requêtes/s |
| Taux d'erreur | 0,7 % |
| Latence p95 | 120 ms |
| Latence p99 | 420 ms |
| Proxys indisponibles | 1 |
| Refus d'autorisation | 25 sur une période donnée |

Ces chiffres sont illustratifs.

### 15.3 Istio et Prometheus

Istio peut exposer des métriques qui sont collectées par Prometheus lorsque le système de collecte est correctement configuré.

Une requête PromQL doit être adaptée aux noms de métriques et aux labels présents dans l'installation.

Exemple de recherche de métriques :

```promql
istio_requests_total
```

Exemple de taux d'erreur HTTP 5xx, si les métriques et labels standards correspondants sont disponibles :

```promql
sum(rate(istio_requests_total{
  reporter="destination",
  response_code=~"5.."
}[5m]))
/
clamp_min(
  sum(rate(istio_requests_total{
    reporter="destination"
  }[5m])),
  0.001
)
```

Cette expression illustre un ratio d'erreurs. Il faut vérifier la sémantique des labels, les filtres, la cardinalité et la présence effective des séries dans l'environnement.

### 15.4 Traces distribuées

Pour les traces, le proxy ne peut pas toujours déduire la totalité du contexte applicatif.

Les applications doivent généralement propager les en-têtes de traçage appropriés, par exemple selon le format W3C Trace Context ou les formats supportés par la plateforme.

Une requête peut traverser cinq services. Sans propagation correcte, on obtient plusieurs traces fragmentées au lieu d'un parcours cohérent.

### 15.5 Cardinalité des métriques

Un piège important consiste à ajouter des labels à forte cardinalité :

- Identifiants de requête uniques.
- Identifiants d'utilisateurs.
- Valeurs arbitraires d'URL.
- Jetons ou identifiants de session.

Cela peut faire croître fortement le nombre de séries temporelles et la consommation mémoire de Prometheus.

Les identifiants uniques sont généralement mieux adaptés aux journaux ou aux traces qu'aux labels de métriques.

## 16. Intégration avec SRE : SLI, SLO et budgets d'erreur

Le Service Mesh facilite certaines mesures techniques, mais les SLO doivent rester liés à l'expérience réelle de l'utilisateur.

### 16.1 Exemple de SLI

Pour une API de commandes :

- SLI de disponibilité : proportion des requêtes valides réussies.
- SLI de latence : proportion des requêtes terminées en moins d'un seuil.
- SLI de fraîcheur : délai de propagation d'une donnée, si cela compte pour le métier.

Le mesh peut mesurer le débit, les erreurs et la latence entre services. L'application et la plateforme de supervision doivent établir la correspondance entre ces métriques et les objectifs utilisateurs.

### 16.2 Exemple de SLO

Supposons un SLO de disponibilité de 99,9 % sur 30 jours.

Sur 30 jours de 24 heures, le budget théorique d'indisponibilité est :

\[
30 \times 24 \times 60 \times 0{,}001 = 43{,}2\ \text{minutes}
\]

Cette estimation suppose une mesure temporelle simple. Si le SLO est calculé à partir des requêtes, le budget d'erreur dépend du volume et de la définition exacte du SLI.

### 16.3 Décision de déploiement

```text
Déploiement canary
        |
        v
Mesure du SLI
        |
        v
Comparaison au SLO
        |
    +---+---+
    |       |
    v       v
 Conforme  Dégradation
    |       |
    v       v
Promouvoir Retour arrière
```

La promotion doit prendre en compte les erreurs, la latence, les signaux métier et les effets potentiels sur les dépendances.

Une faible proportion de trafic peut être insuffisante pour détecter certaines régressions. Il faut donc adapter la durée et le volume d'observation.

## 17. Sécurité avancée et défense en profondeur

### 17.1 Plusieurs couches complémentaires

Une architecture sécurisée combine :

1. Les contrôles d'accès à l'API Kubernetes.
2. La sécurité des nœuds et du runtime.
3. Les NetworkPolicy du CNI.
4. Les identités et le mTLS du mesh.
5. Les politiques d'autorisation du mesh.
6. L'authentification et l'autorisation métier.
7. La gestion des secrets.
8. La surveillance et l'audit.

```text
          IDENTITÉ UTILISATEUR
                   |
                   v
             API / GATEWAY
                   |
                   v
          AUTORISATION MÉTIER
                   |
                   v
          POLITIQUE SERVICE MESH
                   |
                   v
             NETWORK POLICY
                   |
                   v
            WORKLOAD CIBLE
```

Ce schéma est logique et ne représente pas nécessairement l'ordre exact des traitements réseau.

### 17.2 Les limites de la confiance

Le mTLS permet d'authentifier un workload. Il ne prouve pas que ce workload est sain.

Si un service autorisé est compromis, il peut toujours tenter des opérations malveillantes dans les limites de ses accès.

La sécurité doit donc aussi reposer sur :

- Des comptes de service distincts.
- Des autorisations minimales.
- Des images signées ou vérifiées selon la chaîne de confiance retenue.
- Des contrôles d'admission.
- Des mises à jour de sécurité.
- La surveillance des comportements anormaux.
- La séparation des environnements.

### 17.3 Gestion des certificats

Les certificats du mesh ont un cycle de vie :

```text
ÉMISSION
   |
   v
DISTRIBUTION
   |
   v
UTILISATION
   |
   v
RENOUVELLEMENT
   |
   v
EXPIRATION / RÉVOCATION SELON LE MODÈLE
```

Les certificats courts réduisent la fenêtre d'exposition, mais imposent un mécanisme de renouvellement fiable.

Les opérations à prévoir comprennent :

- Le suivi de l'expiration.
- La disponibilité de l'autorité de confiance.
- Le renouvellement automatique.
- La rotation des clés.
- La gestion des changements de racine de confiance.
- Les procédures d'urgence.

Une rotation de l'autorité de certification doit être planifiée pour éviter une coupure généralisée.

## 18. Déploiement multi-cluster

Un mesh réparti sur plusieurs clusters peut améliorer la résilience, la répartition de charge et la proximité géographique.

Il augmente aussi la complexité.

### 18.1 Architecture

```text
                UTILISATEURS
                     |
           +---------+---------+
           |                   |
           v                   v
      CLUSTER A            CLUSTER B
   +-------------+      +-------------+
   | Web         |      | Web         |
   | Orders      |<---->| Orders      |
   | Payment     |      | Payment     |
   +-------------+      +-------------+
           |                   |
           +---------+---------+
                     |
           Identités et confiance
           entre les clusters
```

Les détails de connectivité et de découverte des services dépendent du mesh, de la topologie réseau et du mode de déploiement.

### 18.2 Questions à résoudre

Avant le déploiement :

- Les clusters disposent-ils d'une connectivité routable entre eux ?
- Les plages IP se chevauchent-elles ?
- Comment les identités sont-elles établies et vérifiées ?
- Comment les certificats sont-ils renouvelés ?
- Quelle est la stratégie de découverte des services ?
- Que se passe-t-il lorsqu'un cluster devient inaccessible ?
- Comment éviter un basculement vers une région dégradée ?
- Les données sont-elles répliquées de manière cohérente ?
- Les routes restent-elles compatibles entre les versions ?

Un Service Mesh ne réplique pas automatiquement les bases de données et ne garantit pas la cohérence métier entre régions.

### 18.3 Stratégie de basculement

Un basculement doit prendre en compte la capacité réelle de la destination.

Si le cluster A reçoit 10 000 requêtes/s et le cluster B n'a qu'une capacité de 4 000 requêtes/s, rediriger tout le trafic vers B risque de provoquer une surcharge.

Le plan de reprise doit définir :

- La capacité de secours.
- Les seuils de déclenchement.
- Les délais de détection.
- Les conséquences sur les sessions et les données.
- La procédure de retour à la normale.

Les fonctionnalités multi-clusters évoluent rapidement. Vérifier les limitations documentées de la version choisie, particulièrement pour les architectures ambient.

## 19. Gestion du trafic sortant

Les communications sortantes doivent être traitées avec la même rigueur que les communications internes.

Exemples de destinations :

- APIs tierces.
- Services de paiement.
- Registres d'images.
- Systèmes d'identité.
- Services de télémétrie.

Une stratégie de sortie peut imposer :

- Des destinations explicitement autorisées.
- Une résolution DNS contrôlée.
- Une politique TLS appropriée.
- Une journalisation des connexions.
- Une séparation entre les flux internes et externes.

Dans Istio, `ServiceEntry` peut permettre de déclarer des services externes dans le modèle de découverte du mesh. Son utilisation doit être cohérente avec la politique de sortie choisie.

Il ne faut pas croire qu'une configuration de Service Mesh remplace nécessairement les règles du pare-feu, du proxy de sortie ou de la passerelle réseau.

## 20. GitOps et gestion déclarative du mesh

Le Service Mesh doit être traité comme une partie de la plateforme, avec une configuration versionnée, testée et revue.

### 20.1 Organisation d'un dépôt

```text
platform/
├── terraform/
│   ├── modules/
│   └── environments/
├── kubernetes/
│   ├── base/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
├── mesh/
│   ├── base/
│   │   ├── peer-authentication.yaml
│   │   ├── authorization-policies/
│   │   └── traffic-management/
│   └── overlays/
│       ├── dev/
│       ├── staging/
│       └── production/
└── .github/
    └── workflows/
```

La structure exacte dépend de l'outil de déploiement et des conventions de l'organisation.

### 20.2 Pipeline recommandé

```text
PULL REQUEST
     |
     v
VALIDATION YAML
     |
     v
VALIDATION SCHÉMAS
     |
     v
TESTS DE POLITIQUES
     |
     v
REVUE DE CODE
     |
     v
ENVIRONNEMENT DE TEST
     |
     v
VÉRIFICATION SLI / SLO
     |
     v
PROMOTION CONTRÔLÉE
```

### 20.3 Contrôles à automatiser

Selon les outils disponibles :

- Validation syntaxique YAML.
- Validation des schémas Kubernetes.
- Vérification des références et des labels.
- Détection de configurations trop permissives.
- Vérification de la présence de limites de ressources.
- Tests de connectivité.
- Tests des politiques d'autorisation.
- Tests de compatibilité entre versions.
- Vérification des résultats du déploiement.

Les validations statiques ne remplacent pas les tests sur un cluster. Une politique peut être syntaxiquement correcte tout en bloquant un flux indispensable.

## 21. CI/CD : exemple de pipeline de validation

L'exemple suivant illustre un pipeline GitHub Actions qui valide des manifestes Kubernetes. Il ne déploie pas automatiquement les politiques en production.

```yaml
name: Validate Mesh Configuration

on:
  pull_request:
    paths:
      - "mesh/**"
      - ".github/workflows/mesh-validation.yml"

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install kubectl
        uses: azure/setup-kubectl@v4
        with:
          version: "latest"

      - name: Validate YAML syntax
        run: |
          python -m pip install --user yamllint
          yamllint mesh/

      - name: Validate Kubernetes manifests
        run: |
          find mesh -name '*.yaml' -o -name '*.yml'
```

Cette étape de découverte ne valide pas encore les schémas Kubernetes. Elle doit être complétée par un validateur de manifestes compatible avec les ressources et les CRD utilisées.

Dans un pipeline réel :

- Épingler les versions des actions et des outils.
- Éviter d'utiliser `latest` comme version de production.
- Ajouter un validateur de schémas adapté.
- Installer ou rendre disponibles les CRD nécessaires.
- Ajouter des tests de politiques.
- Protéger les environnements et les secrets de déploiement.
- Exiger une approbation pour la production.

Un pipeline ne doit pas se contenter de vérifier que les fichiers YAML peuvent être lus.

## 22. Mise à niveau d'un Service Mesh

Une mise à niveau peut toucher plusieurs couches :

- Le plan de contrôle.
- Les proxys.
- Les CRD.
- Les opérateurs ou chart Helm.
- Les passerelles.
- Les politiques.
- Les intégrations d'observabilité.

### 22.1 Stratégie de mise à niveau

```text
INVENTAIRE
    |
    v
LECTURE DES NOTES DE VERSION
    |
    v
SAUVEGARDE DES CONFIGURATIONS
    |
    v
TEST EN PRÉPRODUCTION
    |
    v
MISE À NIVEAU DU PLAN DE CONTRÔLE
    |
    v
VALIDATION DES PROXYS
    |
    v
DÉPLOIEMENT PROGRESSIF
    |
    v
VÉRIFICATION DES SLO
    |
    v
VALIDATION OU RETOUR ARRIÈRE
```

L'ordre exact dépend du mode d'installation et de la stratégie de mise à niveau supportée.

### 22.2 Contrôles avant migration

- Lire les notes de version.
- Vérifier les versions Kubernetes prises en charge.
- Vérifier les CRD et leurs changements.
- Identifier les ressources dépréciées.
- Vérifier les contraintes de compatibilité.
- Tester les politiques de sécurité.
- Vérifier le comportement des passerelles.
- Préparer un plan de retour arrière.

Un retour arrière n'est pas toujours équivalent à remettre l'ancienne image. Certaines migrations de CRD ou de configuration peuvent être incompatibles avec une simple rétrogradation.

## 23. Dépannage expert

Le dépannage doit être méthodique. Il faut éviter de modifier plusieurs politiques à la fois sans comprendre l'origine du problème.

### 23.1 Méthode générale

```text
SYMPTÔME
   |
   v
REPRODUCTION
   |
   v
VÉRIFICATION DU SERVICE KUBERNETES
   |
   v
VÉRIFICATION DU RÉSEAU
   |
   v
VÉRIFICATION DU PROXY
   |
   v
VÉRIFICATION IDENTITÉ / POLITIQUE
   |
   v
CORRECTION CIBLÉE
   |
   v
TEST ET MESURE
```

### 23.2 Commandes d'inspection

```bash
kubectl get pods -A
kubectl get services -A
kubectl get endpointslices -A
kubectl get events -A --sort-by=.lastTimestamp
```

Pour Istio :

```bash
istioctl analyze -n mesh-lab
istioctl proxy-status
istioctl proxy-config routes NOM_DU_POD -n mesh-lab
istioctl proxy-config clusters NOM_DU_POD -n mesh-lab
kubectl logs NOM_DU_POD -n mesh-lab -c istio-proxy
```

Les commandes `proxy-config` concernent les proxys Envoy. Elles ne s'appliquent pas de la même manière à tous les composants ambient.

### 23.3 Erreur : connexion refusée

Causes possibles :

- Le Pod cible n'écoute pas sur le port attendu.
- Le Service pointe vers un mauvais `targetPort`.
- Aucun endpoint n'est disponible.
- Le conteneur n'est pas prêt.
- Une politique réseau bloque la connexion.
- Une politique du mesh refuse le trafic.
- Une règle de routage dirige le trafic vers un backend incorrect.

Procédure :

```bash
kubectl get service NOM_DU_SERVICE -n mesh-lab -o yaml
kubectl get endpointslices -n mesh-lab
kubectl describe pod NOM_DU_POD -n mesh-lab
kubectl logs NOM_DU_POD -n mesh-lab
```

### 23.4 Erreur : HTTP 403

Causes possibles :

- Politique d'autorisation restrictive.
- Identité du client incorrecte.
- Principal non reconnu.
- Route ou port non couvert par la règle attendue.
- Requête refusée par un autre composant de sécurité.

Vérifier les politiques :

```bash
kubectl get authorizationpolicy -A
kubectl describe authorizationpolicy NOM -n mesh-lab
```

Pour Linkerd, inspecter les ressources de politique réellement installées et les journaux du proxy.

### 23.5 Erreur : HTTP 503

Un 503 n'a pas une cause unique.

Causes possibles :

- Aucun backend sain.
- Problème de résolution ou de découverte.
- Circuit de connexion ou limite de pool atteinte.
- Timeout ou erreur du backend.
- Configuration de proxy incorrecte.
- Refus ou erreur en amont.

Comparer :

- Les métriques de l'application.
- Les métriques du proxy.
- Les journaux de l'application.
- Les journaux du proxy.
- Les endpoints Kubernetes.
- Les résultats des tests directs et via le mesh.

### 23.6 Le proxy ne reçoit pas la configuration attendue

Vérifier :

```bash
istioctl proxy-status
istioctl analyze -n mesh-lab
kubectl get events -n istio-system --sort-by=.lastTimestamp
kubectl logs deployment/istiod -n istio-system
```

Les noms des ressources et leur disponibilité dépendent de l'installation.

Examiner ensuite :

- Les labels des workloads.
- Les namespaces concernés.
- Les références de Service.
- Les règles de routage.
- Les erreurs de validation.
- Les versions des ressources.

## 24. Capacité, performances et coûts

Le Service Mesh ajoute une couche de traitement. Cette couche doit être mesurée.

### 24.1 Sources de coût

- CPU et mémoire des proxys.
- Temps de traitement supplémentaire.
- Connexions supplémentaires.
- Collecte des métriques.
- Export des traces.
- Stockage des journaux.
- Ressources du plan de contrôle.
- Complexité opérationnelle.

### 24.2 Mesurer avant d'optimiser

Pour comparer deux configurations, contrôler :

- Le même workload.
- Le même volume de trafic.
- Le même nombre de Pods.
- Le même type de requêtes.
- Les mêmes limites de ressources.
- Les mêmes conditions réseau.
- Les mêmes paramètres d'observabilité.

Mesurer au minimum :

- Le débit.
- La latence p50, p95 et p99.
- Le taux d'erreur.
- Le CPU.
- La mémoire.
- Le nombre de connexions.
- Les redémarrages.
- La stabilité pendant la montée en charge.

### 24.3 Optimisation

Actions possibles :

- Réduire les fonctionnalités non utilisées.
- Contrôler la cardinalité des métriques.
- Ajuster les ressources des proxys.
- Dimensionner le plan de contrôle.
- Éviter des règles de routage inutiles.
- Limiter les retries.
- Tester les modes de données disponibles.
- Réduire les traces à forte volumétrie si elles ne sont pas nécessaires.

Ne pas désactiver la sécurité ou l'observabilité sans analyser les conséquences.

## 25. Haute disponibilité du plan de contrôle

La haute disponibilité doit être adaptée au mode d'installation et aux composants concernés.

Points à étudier :

- Nombre de réplicas.
- Répartition entre nœuds et zones.
- PodDisruptionBudget.
- Affinités et anti-affinités.
- Demandes et limites de ressources.
- Autoscaling lorsqu'il est approprié.
- Surveillance de l'état des composants.
- Comportement lors de l'indisponibilité du plan de contrôle.

Exemple de vérification :

```bash
kubectl get deployments,pods -n istio-system -o wide
kubectl get pdb -n istio-system
kubectl top pods -n istio-system
```

La haute disponibilité ne se résume pas à augmenter le nombre de réplicas. Elle exige une répartition physique correcte et des tests de panne.

## 26. Contrôles d'admission et gouvernance

Dans une grande plateforme, il faut éviter que chaque équipe puisse déployer des politiques réseau arbitraires sans contrôle.

Les mécanismes de gouvernance peuvent inclure :

- RBAC Kubernetes.
- Contrôles d'admission.
- Politiques de conformité.
- Validation CI.
- Modèles réutilisables.
- Revue de code.
- Audit des modifications.

Exemples de contrôles organisationnels :

- Interdire des politiques trop permissives en production.
- Exiger des comptes de service distincts pour les applications.
- Exiger des limites de ressources pour les workloads.
- Contrôler les labels qui sélectionnent les services.
- Empêcher les changements non revus dans les namespaces critiques.

Ces contrôles doivent rester compatibles avec les besoins de déploiement. Une politique d'admission mal conçue peut bloquer des mises à jour urgentes.

## 27. Linkerd : inspection et exploitation

Les commandes de Linkerd sont différentes de celles d'Istio.

Après installation et intégration des composants nécessaires :

```bash
linkerd check
linkerd check --pre
linkerd version
linkerd viz stat deploy -n mesh-lab
```

La disponibilité de certaines commandes dépend des extensions installées et de la version.

Pour observer les communications, vérifier que les workloads sont réellement maillés et que les proxys sont prêts.

Exemples d'inspection :

```bash
kubectl get pods -n mesh-lab
kubectl describe pod NOM_DU_POD -n mesh-lab
kubectl logs NOM_DU_POD -n mesh-lab
```

La CLI et les ressources exactes doivent être vérifiées dans la documentation de la version utilisée.

### 27.1 Comparaison opérationnelle

Dans une équipe exploitant Linkerd, l'objectif est de tirer parti de ses outils de diagnostic et de ses politiques natives plutôt que de transposer systématiquement les commandes et objets Istio.

Les concepts sont comparables, mais les ressources, les modèles de routage et les paramètres ne sont pas interchangeables.

## 28. Projet pratique : sécuriser et exploiter une plateforme de commandes

### 28.1 Contexte

Une entreprise exploite une application composée de :

- `frontend` : interface web.
- `orders` : gestion des commandes.
- `inventory` : gestion du stock.
- `payment` : traitement des paiements.
- `notifications` : envoi des notifications.

L'architecture initiale fonctionne sur Kubernetes, mais les communications sont difficiles à observer. Les déploiements introduisent parfois des régressions et les accès entre services sont trop permissifs.

### 28.2 Objectifs

Construire une architecture qui permet de :

1. Déployer les workloads dans des namespaces adaptés.
2. Activer le Service Mesh.
3. Vérifier les identités et le mTLS.
4. Limiter les communications aux flux nécessaires.
5. Déployer une nouvelle version en canary.
6. Collecter les métriques et les traces.
7. Définir un SLO.
8. Automatiser la validation des manifestes.
9. Tester une panne et un retour arrière.
10. Documenter les procédures d'exploitation.

### 28.3 Architecture cible

```text
                    UTILISATEURS
                         |
                         v
                   GATEWAY / API
                         |
                         v
                     FRONTEND
                         |
                         v
                       ORDERS
                    /     |     \
                   v      v      v
              INVENTORY PAYMENT NOTIFICATIONS
                   |      |          |
                   v      v          v
                 STOCK   PAIEMENT   MESSAGERIE

       Sécurité : identités, mTLS et politiques d'accès
       Trafic   : canary, timeouts et résilience
       SRE      : métriques, traces, SLI et alertes
       CI/CD    : validation, promotion et retour arrière
```

### 28.4 Étape 1 : inventaire des flux

Créer un tableau des communications :

| Source | Destination | Port | Justification |
|---|---|---:|---|
| frontend | orders | 8080 | Créer et consulter les commandes |
| orders | inventory | 8080 | Vérifier le stock |
| orders | payment | 8080 | Autoriser le paiement |
| orders | notifications | 8080 | Envoyer les événements de commande |

Ce tableau est un point de départ. Les communications réelles doivent être observées et vérifiées avant d'imposer les règles.

### 28.5 Étape 2 : activer le mesh

- Déployer l'implémentation retenue.
- Vérifier la présence des proxys ou composants ambient attendus.
- Contrôler la connectivité entre les services.
- Vérifier le comportement des sondes de santé.
- Tester les parcours métier.

### 28.6 Étape 3 : sécuriser

- Utiliser des comptes de service dédiés.
- Activer le mTLS selon la topologie.
- Créer des politiques d'autorisation minimales.
- Vérifier les flux de chaque service.
- Tester les accès légitimes et les accès interdits.
- Vérifier l'effet des changements sur les clients non maillés.

### 28.7 Étape 4 : déployer une nouvelle version

Déployer `orders-v2` avec un faible pourcentage de trafic.

Contrôler :

- Le taux d'erreur.
- La latence p95 et p99.
- Les erreurs métier.
- La charge de `inventory` et de `payment`.
- Les traces distribuées.
- Les alertes SLO.

Augmenter le trafic uniquement si les critères définis sont satisfaits.

### 28.8 Étape 5 : simuler un incident

Scénario : `inventory` devient lent.

Procédure :

1. Observer l'augmentation de la latence.
2. Vérifier si les timeouts sont cohérents.
3. Contrôler les retries et leur amplification.
4. Vérifier la saturation du service.
5. Déterminer si le canary est responsable ou simplement affecté.
6. Réduire le trafic si nécessaire.
7. Restaurer un fonctionnement normal.
8. Documenter la cause et les mesures correctives.

### 28.9 Livrables attendus

Le projet doit produire :

- Les manifestes Kubernetes.
- Les ressources du Service Mesh.
- Les politiques de sécurité.
- Les règles de routage.
- Les tests automatisés.
- Le tableau des flux.
- Les dashboards de supervision.
- La définition des SLI et SLO.
- Un runbook d'incident.
- Un plan de retour arrière.
- Une documentation des choix architecturaux.

## 29. Exercices corrigés

### Exercice 1 : choix de technologie

Une équipe de dix personnes veut chiffrer ses communications internes, visualiser les erreurs et limiter les communications entre services. Elle dispose de peu de temps pour exploiter une infrastructure complexe.

Quelle démarche suivre pour choisir entre Istio et Linkerd ?

**Correction :**

1. Recenser les exigences de sécurité et d'observabilité.
2. Vérifier si le routage avancé, les passerelles ou les politiques L7 d'Istio sont indispensables.
3. Construire un prototype avec Linkerd et un autre avec Istio si les contraintes le justifient.
4. Mesurer le coût des proxys, le temps d'exploitation et les performances.
5. Choisir la solution qui satisfait les exigences avec une complexité acceptable.

Une équipe plus petite ne doit pas choisir automatiquement Linkerd, et une grande entreprise ne doit pas choisir automatiquement Istio.

### Exercice 2 : comprendre un HTTP 403

Après l'application d'une `AuthorizationPolicy`, `orders` ne parvient plus à appeler `payment`.

Quelles vérifications effectuer ?

**Correction :**

- Vérifier les labels des Pods ciblés.
- Vérifier le compte de service de `orders`.
- Vérifier l'identité utilisée par le mesh.
- Vérifier le port de destination.
- Vérifier les autres politiques applicables.
- Examiner les journaux et métriques des proxys.
- Tester une requête autorisée et une requête interdite.

Il ne faut pas supprimer toutes les politiques pour rétablir le service sans comprendre l'erreur.

### Exercice 3 : dimensionnement des retries

Un service traite 500 requêtes/s. Une panne provoque l'échec de nombreuses requêtes. Chaque requête peut être tentée jusqu'à trois fois au total.

Quel est le risque ?

**Correction :**

Le trafic vers la dépendance peut augmenter fortement. Si chaque requête initiale déclenche trois tentatives au total, le volume théorique peut approcher 1 500 tentatives/s lorsque toutes les requêtes sont réessayées.

Il faut préciser si « trois retries » signifie trois tentatives supplémentaires ou trois tentatives au total. Dans le premier cas, quatre tentatives par requête sont possibles.

Il faut limiter les retries, définir des timeouts cohérents, considérer l'idempotence et mesurer la charge supplémentaire.

### Exercice 4 : analyser un canary

Une version V2 reçoit 10 % du trafic. La latence p99 augmente et le taux d'erreur double.

Quelle est la décision la plus prudente ?

**Correction :**

Suspendre la progression du déploiement et analyser les indicateurs. Si la régression est confirmée et dépasse les seuils prévus, réduire le trafic de V2 ou effectuer un retour arrière. Examiner les traces, les erreurs et les dépendances avant de reprendre la promotion.

### Exercice 5 : plan de contrôle indisponible

Le plan de contrôle devient indisponible, mais les applications continuent de communiquer.

Est-ce une contradiction ?

**Correction :**

Non. Le plan de données peut continuer à utiliser une configuration précédemment reçue. Cependant, les modifications de configuration, l'intégration de nouveaux workloads et certaines opérations d'identité peuvent être affectées. Il faut tester le comportement exact de l'implémentation, notamment le renouvellement des certificats.

### Exercice 6 : problème de latence

Après activation du mesh, la latence p95 augmente de 20 %.

Quelles sont les étapes d'investigation ?

**Correction :**

1. Vérifier que le scénario de mesure est identique.
2. Contrôler le CPU et la mémoire des applications et proxys.
3. Examiner le nombre de connexions et les timeouts.
4. Vérifier le volume de traces et de métriques.
5. Contrôler les règles de routage et les retries.
6. Comparer les résultats avec les fonctions activées et désactivées dans un environnement de test.
7. Optimiser seulement après avoir identifié une cause probable.

## 30. Défi final : architecture de production

Concevoir une plateforme Kubernetes composée de plusieurs services, avec un mesh sécurisé et observable.

### Contraintes

- Les communications sensibles doivent être chiffrées.
- Seuls les services autorisés doivent pouvoir accéder à chaque backend.
- Une nouvelle version doit être déployée progressivement.
- Les timeouts et retries doivent être documentés.
- Les SLO doivent contrôler la promotion.
- Les politiques doivent être validées en CI.
- Le plan de contrôle doit disposer d'une stratégie de haute disponibilité.
- Une procédure d'incident doit permettre de restaurer le service.
- Les changements de version du mesh doivent être testés avant production.

### Correction attendue : plan de réalisation

**Phase 1 — Conception**

- Définir les flux et les identités.
- Choisir Istio ou Linkerd selon les besoins.
- Choisir le mode de données et le modèle de routage.
- Définir les objectifs de latence et de disponibilité.

**Phase 2 — Installation**

- Provisionner l'infrastructure.
- Installer le mesh dans un environnement de test.
- Valider la connectivité et la santé des composants.
- Documenter les versions et dépendances.

**Phase 3 — Sécurité**

- Configurer les identités.
- Activer le mTLS selon les besoins.
- Définir les politiques d'autorisation.
- Tester les accès légitimes et interdits.
- Vérifier les interactions avec les NetworkPolicy.

**Phase 4 — Routage**

- Définir les versions des services.
- Configurer les règles de répartition.
- Tester les timeouts, retries et mécanismes de limitation.
- Vérifier le comportement en cas de panne.

**Phase 5 — Observabilité**

- Collecter les métriques.
- Relier les traces distribuées.
- Construire les dashboards.
- Définir les alertes et les SLO.
- Vérifier que les labels ne provoquent pas une cardinalité excessive.

**Phase 6 — Automatisation**

- Versionner les manifestes.
- Valider les schémas.
- Tester les politiques.
- Exiger une revue des changements sensibles.
- Déployer progressivement.
- Contrôler les résultats avant promotion.

**Phase 7 — Exploitation**

- Tester une indisponibilité du plan de contrôle.
- Tester une panne applicative.
- Vérifier les procédures de retour arrière.
- Tester la rotation des certificats.
- Préparer les mises à niveau.
- Organiser des exercices de reprise.

La réussite ne se mesure pas au nombre de ressources déployées. Elle se mesure à la capacité de la plateforme à protéger les communications, à limiter les effets d'une panne, à fournir des preuves observables et à permettre des changements sûrs.

## 31. Checklist de mise en production

### Architecture

- [ ] Le choix Istio ou Linkerd est documenté.
- [ ] Le mode de données est adapté aux besoins.
- [ ] Les flux interservices sont inventoriés.
- [ ] Les limites de l'architecture sont connues.

### Sécurité

- [ ] Les identités de workloads sont distinctes.
- [ ] Le mTLS est configuré selon le modèle de confiance.
- [ ] Les politiques d'autorisation ont été testées.
- [ ] Les communications externes sont maîtrisées.
- [ ] Les comptes de service disposent de privilèges minimaux.
- [ ] La rotation des certificats est surveillée.

### Résilience

- [ ] Les timeouts sont cohérents.
- [ ] Les retries sont limités.
- [ ] Les opérations non idempotentes sont protégées.
- [ ] Les limites de connexions sont dimensionnées.
- [ ] Les procédures de retour arrière sont testées.

### Observabilité

- [ ] Les métriques essentielles sont collectées.
- [ ] Les traces distribuées sont corrélées.
- [ ] Les journaux sont accessibles.
- [ ] Les alertes sont exploitables.
- [ ] La cardinalité des métriques est contrôlée.
- [ ] Les SLO reflètent l'expérience utilisateur.

### Automatisation

- [ ] Les manifestes sont versionnés.
- [ ] Les validations sont automatisées.
- [ ] Les changements sensibles sont revus.
- [ ] Les versions des composants sont maîtrisées.
- [ ] Les mises à niveau ont été testées.

### Exploitation

- [ ] Le plan de contrôle est surveillé.
- [ ] La capacité des proxys est mesurée.
- [ ] Les runbooks sont documentés.
- [ ] Les scénarios de panne sont testés.
- [ ] Le support et les limitations des versions sont connus.

## 32. Glossaire

**Service Mesh :** couche d'infrastructure qui sécurise, contrôle et observe les communications entre services.

**Control plane :** composants qui distribuent les configurations et gèrent les fonctions de coordination du mesh.

**Data plane :** composants qui traitent le trafic entre les workloads.

**Sidecar :** proxy déployé à côté du conteneur applicatif dans un Pod.

**Ambient Mesh :** mode Istio dans lequel les fonctions de base sont fournies par des composants au niveau des nœuds, avec des proxys L7 optionnels.

**Envoy :** proxy utilisé par Istio pour plusieurs fonctions de traitement du trafic.

**ztunnel :** composant L4 du plan de données ambient d'Istio.

**Waypoint :** proxy Envoy utilisé en ambient pour les fonctionnalités L7 lorsqu'elles sont nécessaires.

**mTLS :** TLS mutuel, qui permet l'authentification des deux parties et le chiffrement du canal.

**SPIFFE :** spécification d'identité destinée aux workloads.

**SLI :** indicateur mesurant un aspect de la qualité de service.

**SLO :** objectif défini pour un SLI.

**Canary :** stratégie consistant à exposer progressivement une nouvelle version à une fraction du trafic.

**Timeout :** durée maximale d'attente avant l'abandon d'une opération.

**Retry :** nouvelle tentative après un échec.

**Circuit breaker :** mécanisme limitant l'effet d'une dépendance défaillante ou saturée.

**Cardinalité :** nombre de combinaisons distinctes de labels pouvant créer des séries temporelles.

**Gateway API :** API Kubernetes pour définir le routage réseau de manière structurée.

**GitOps :** approche dans laquelle un dépôt versionné représente l'état souhaité de la plateforme.

## 33. Références officielles

Les fonctionnalités et les syntaxes évoluent. Toujours consulter la documentation correspondant à la version réellement installée.

### Istio

- Documentation générale : https://istio.io/latest/docs/
- Architecture des modes de données : https://istio.io/latest/docs/overview/dataplane-modes/
- Mode ambient : https://istio.io/latest/docs/ambient/
- Architecture ambient : https://istio.io/latest/docs/ambient/overview/
- Authentification : https://istio.io/latest/docs/concepts/security/
- Politiques d'autorisation : https://istio.io/latest/docs/reference/config/security/authorization-policy/
- PeerAuthentication : https://istio.io/latest/docs/reference/config/security/peer_authentication/
- Routage du trafic : https://istio.io/latest/docs/concepts/traffic-management/
- DestinationRule : https://istio.io/latest/docs/reference/config/networking/destination-rule/
- VirtualService : https://istio.io/latest/docs/reference/config/networking/virtual-service/
- Observabilité : https://istio.io/latest/docs/concepts/observability/
- Multi-cluster : https://istio.io/latest/docs/ops/configuration/traffic-management/multicluster/

### Linkerd

- Documentation générale : https://linkerd.io/docs/
- Installation : https://linkerd.io/docs/getting-started/
- Sécurité : https://linkerd.io/docs/features/security/
- Politiques de serveur : https://linkerd.io/docs/features/server-policy/
- Référence des politiques : https://linkerd.io/docs/reference/authorization-policy/
- Observabilité : https://linkerd.io/docs/features/observability/
- Multi-cluster : https://linkerd.io/docs/features/multicluster/

### Kubernetes et standards

- Gateway API : https://gateway-api.sigs.k8s.io/
- Introduction à Gateway API : https://gateway-api.sigs.k8s.io/docs/introduction/
- Réseau Kubernetes : https://kubernetes.io/docs/concepts/services-networking/
- RBAC Kubernetes : https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- NetworkPolicy : https://kubernetes.io/docs/concepts/services-networking/network-policies/
- SPIFFE : https://spiffe.io/docs/latest/spiffe-about/overview/

## 34. Conclusion

Un Service Mesh apporte une couche commune pour gérer les communications entre services. Il peut renforcer le chiffrement, les identités, l'autorisation, le routage, la résilience et l'observabilité.

La maîtrise experte exige cependant de comprendre les limites de cette couche :

- Le mesh ne remplace pas la sécurité applicative.
- Le chiffrement ne remplace pas l'autorisation.
- Les retries peuvent amplifier une panne.
- Les proxys ont un coût en ressources et en latence.
- Une politique incorrecte peut provoquer une interruption de service.
- Une architecture multicluster demande une stratégie de capacité et de reprise.
- Une installation fonctionnelle n'est pas nécessairement une installation exploitable en production.

La démarche à conserver est la suivante :

**Concevoir les flux, établir les identités, appliquer des politiques minimales, mesurer le comportement réel, tester les pannes et automatiser les changements.**

C'est cette démarche qui transforme Istio ou Linkerd d'un composant supplémentaire en un outil fiable au service d'une plateforme Kubernetes.