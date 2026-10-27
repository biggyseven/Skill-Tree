# Sécurité des conteneurs (Docker/K8s)

> **Mise en contexte**
>
> Les conteneurs ont accéléré le déploiement des applications : une image rassemble le programme et ses dépendances, puis peut être exécutée sur un poste, un serveur ou un cluster. Cette portabilité ne rend pas le logiciel automatiquement sûr. Une image peut embarquer une bibliothèque vulnérable, un secret, un utilisateur privilégié ou des outils inutiles. Un conteneur peut recevoir des capacités Linux excessives, monter le système de fichiers de l’hôte ou obtenir accès au socket du moteur. Dans Kubernetes, une permission de créer des Pods peut parfois ouvrir un chemin vers les secrets ou les nœuds. La sécurité exige donc une chaîne complète, du code source à l’exécution, avec des identités limitées, des politiques d’admission, des contrôles réseau, des preuves et une procédure de réponse.

## Objectifs pédagogiques et scénario fil conducteur

Ce cours expert enseigne comment sécuriser des conteneurs Docker et des applications Kubernetes. Vous apprendrez à distinguer image, conteneur, moteur, runtime, hôte, Pod, nœud et plan de contrôle ; à concevoir une image minimale ; à réduire les privilèges et la surface d’attaque ; à gérer les secrets ; à analyser les dépendances, signatures et preuves de provenance ; à configurer Kubernetes RBAC, Pod Security Standards et NetworkPolicy ; à protéger les nœuds, le plan de contrôle et les données ; à surveiller l’exécution et à réagir à un incident.

Le fil conducteur est **Atlas Formation**, qui déploie un portail pédagogique constitué d’un frontend, d’une API et d’un service de génération de rapports. Les images sont construites par un pipeline CI/CD et publiées dans un registre. Une équipe déploie parfois avec Docker Compose ; un environnement de production utilise Kubernetes. Les objectifs sont de réduire la surface d’attaque, de limiter le rayon d’impact d’une compromission et de prouver que seules des images approuvées peuvent être mises en production.

Les exercices s’effectuent dans un environnement local ou un cluster de laboratoire autorisé, avec des images et données de démonstration. Ne lancez pas de tests de compromission sur un cluster tiers ou de production sans autorisation écrite et plan de retour arrière. Vous pouvez réaliser les analyses de politiques et une grande partie des travaux pratiques en examinant des fichiers statiques.

## 1. Comprendre les couches de conteneurisation

### 1.1 Image, conteneur, moteur et hôte

Une image de conteneur est un artefact immuable composé de couches et de métadonnées. Elle contient le système de fichiers nécessaire à l’application et indique notamment la commande de démarrage. Un conteneur est une instance en exécution à partir de cette image, associée à un environnement, à des limites de ressources et à des paramètres d’isolation. Le moteur ou la plateforme de conteneurs gère le cycle de vie, tandis que l’hôte fournit le noyau partagé, les ressources matérielles et les frontières de sécurité de base.

~~~text
Code source + dépendances
          |
          v
      Image construite
      couches + métadonnées
          |
          v
 Registre d'images contrôlé
          |
          v
  Moteur / runtime conteneur
          |
          v
 Conteneur en exécution
          |
          v
 Noyau de l'hôte / système hôte
~~~

Contrairement à une machine virtuelle classique, un conteneur Linux partage généralement le noyau de l’hôte. Les namespaces isolent certaines vues des ressources, par exemple les processus, le réseau, les montages ou les identifiants. Les cgroups contrôlent et mesurent la consommation de ressources. Les capacités Linux divisent une partie des privilèges traditionnellement associés à root. Seccomp peut réduire l’ensemble des appels système disponibles ; AppArmor ou SELinux peuvent ajouter des règles de confinement selon le système.

L’isolation repose sur une combinaison de mécanismes. Aucun namespace ne remplace un contrôle d’accès, un noyau corrigé ou une configuration correcte. Si un conteneur est exécuté en mode privilégié ou peut contrôler le daemon du moteur, il peut potentiellement franchir la frontière attendue. Les configurations doivent être choisies en fonction du workload et testées plutôt que de supposer que le mot « conteneur » signifie « bac à sable inviolable ».

### 1.2 Surface d’attaque et frontières de confiance

Une analyse de sécurité identifie plusieurs frontières : code source vers pipeline, pipeline vers registre, registre vers cluster, Pod vers nœud, conteneur vers noyau, application vers API Kubernetes et workload vers services cloud. Chaque frontière possède des identités, des données et des contrôles spécifiques.

~~~text
Développeur
    |
    v
Dépôt Git -> pipeline de build -> registre
                                  |
                                  v
                           admission Kubernetes
                                  |
                                  v
                  Pod -> runtime -> noyau du nœud
                   |                  |
                   v                  v
              API métier       API / métadonnées cloud
                   |
                   v
             données persistantes
~~~

La sécurité ne se limite donc pas à la configuration du fichier Dockerfile. Une image sûre déployée par un pipeline compromis peut être remplacée ; une image approuvée peut être exécutée avec des privilèges dangereux ; un Pod bien configuré peut accéder à une base de données sans autorisation métier. Les contrôles doivent être cohérents tout au long du cycle de vie.

### 1.3 Modèle de menace

Posez la question : que peut faire un attaquant qui compromet un composant ? Un compte développeur peut modifier le code ; un jeton CI peut publier une image ; un compte ayant le droit de créer des Pods peut parfois monter des volumes ou obtenir des identifiants plus puissants ; une vulnérabilité d’exécution peut permettre une action dans le conteneur ; une faiblesse du noyau ou une configuration privilégiée peut étendre l’impact au nœud. Un administrateur de cluster compromis peut modifier plusieurs workloads et atteindre des données sensibles.

~~~text
Compromission de l'image
    |
    +--> exécution d'un code inattendu
    +--> exfiltration des secrets accessibles
    +--> abus du réseau autorisé
    |
    X--> ne devrait pas permettre automatiquement :
          - accès root à l'hôte
          - accès à tous les secrets du cluster
          - écriture dans tous les namespaces
          - modification du plan de contrôle
~~~

Le bon objectif n’est pas de promettre un risque nul. Il est de limiter les droits exposés, de réduire les chemins possibles, de détecter les événements et de rendre la récupération praticable. Documentez les hypothèses : sensibilité des données, niveau d’isolation disponible, nombre de tenants, besoins de privilèges réels et conséquences d’un arrêt.

## 2. Sécuriser la construction des images Docker

### 2.1 Images de base minimales et maintenues

Choisissez une image de base officielle ou issue d’une source approuvée, avec une politique de mise à jour connue. La petite taille est utile, mais n’est pas un indicateur suffisant de sécurité. L’image doit recevoir des correctifs, contenir le minimum nécessaire et être compatible avec la méthode de surveillance. Évitez les images inconnues téléchargées sans vérifier le propriétaire, la provenance et le contenu.

Fixez la version de l’image de base selon une politique de mises à jour et enregistrez la référence exacte utilisée pour une release. Le tag latest est mutable : il peut désigner une autre image ultérieurement. Pour une release reproductible, référez-vous à une version explicite et, dans les chaînes de production appropriées, à un digest immuable. Le digest garantit l’identité du contenu référencé, mais ne démontre pas à lui seul que ce contenu est digne de confiance.

### 2.2 Multi-stage build et réduction de la surface

Une compilation peut nécessiter un compilateur, un gestionnaire de paquets et des outils de développement. L’image finale n’a généralement besoin que du binaire ou des fichiers d’exécution. Le multi-stage build sépare ces étapes et évite d’emporter les outils de construction dans l’image de production.

~~~text
Étape de build
  sources + SDK + outils de compilation
              |
              v
        artefact nécessaire
              |
              v
Étape finale
  runtime minimal + artefact + utilisateur non privilégié
  sans compilateur, cache de paquets ou secret de build
~~~

Supprimez les fichiers temporaires, les caches non nécessaires et les outils de débogage qui ne servent pas au fonctionnement. Une image minimale doit rester maintenable : ne retirez pas des composants indispensables au correctif ou au diagnostic sans solution opérationnelle. Les outils d’investigation peuvent être fournis au besoin par une procédure contrôlée plutôt que par une boîte à outils permanente dans chaque conteneur.

### 2.3 Exemple de Dockerfile de principe

L’exemple suivant illustre les contrôles de base pour une application fictive déjà compilée. Le nom et le chemin du binaire doivent être adaptés au projet. Il ne remplace pas l’analyse des dépendances, la validation de l’image de base ni les contrôles de la CI.

~~~dockerfile
FROM gcr.io/distroless/static-debian12:nonroot
WORKDIR /
COPY --chown=nonroot:nonroot app /app
USER nonroot:nonroot
ENTRYPOINT ["/app"]
~~~

Cette forme présume que le binaire est compatible avec l’image de runtime choisie. Pour une application nécessitant une autre bibliothèque ou un runtime, retenez une image adaptée et maintenue. Le principe demeure : utiliser un utilisateur non privilégié, copier uniquement les artefacts requis et éviter les secrets dans les couches.

### 2.4 Ne jamais intégrer un secret à l’image

Un secret ajouté par une instruction de build peut rester dans une couche même si un fichier est supprimé dans une instruction ultérieure. Les fichiers de configuration, clés privées, jetons, mots de passe, fichiers .env réels et credentials cloud ne doivent pas être incorporés dans l’image. Le même principe concerne les arguments et variables de build lorsqu’ils peuvent être révélés dans les métadonnées, journaux ou caches.

~~~text
Mauvais chemin
Secret -> instruction COPY/RUN -> couche d'image -> registre -> copies

Meilleur chemin
Secret géré hors de l'image
     |
     v
Identité autorisée au runtime
     |
     v
Secret monté ou récupéré à l'exécution
avec droits et durée limités
~~~

Les mécanismes secrets de build peuvent protéger un secret utilisé temporairement pendant la compilation, mais il faut vérifier les instructions, le cache et le contenu produit. Si une clé est publiée, traitez-la comme compromise : révoquez-la, examinez les usages et reconstruisez les artefacts à partir d’un état propre.

### 2.5 Construire en non-root

L’instruction USER du Dockerfile choisit l’utilisateur du processus dans le conteneur. Un processus non-root réduit les actions disponibles si l’application est compromise. Il faut également vérifier que les répertoires nécessaires sont accessibles en écriture, que les ports et fichiers choisis conviennent et que les dépendances n’exigent pas un privilège inutile.

Ne confondez pas UID 0 dans un conteneur avec un accès root total à l’hôte dans toutes les configurations. Cependant, l’exécution en root augmente les conséquences possibles, notamment avec des montages ou capacités dangereux. Préférez le non-root et documentez toute exception technique, avec un plan de réduction des privilèges.

## 3. Réduire les privilèges au runtime Docker

### 3.1 Capacités Linux, privilèges et système de fichiers

Le mode privileged accorde au conteneur un ensemble très large de privilèges et expose des interfaces sensibles de l’hôte. Il est rarement nécessaire pour une application Web classique. Préférez un profil standard, supprimez les capacités inutiles et n’ajoutez que celle qui correspond à un besoin démontré.

~~~text
Configuration prudente
  utilisateur non-root
  privileged = false
  capacités Linux = DROP ALL
  capacités ajoutées = strict minimum justifié
  élévation de privilèges = interdite
  système de fichiers en lecture seule si possible
  montages hôte = absents ou strictement bornés
~~~

Les capacités Linux donnent des pouvoirs précis qui dépassent parfois les droits ordinaires. Un conteneur n’a généralement pas besoin de modifier les interfaces réseau de l’hôte, de charger des modules ou d’effectuer des opérations d’administration système. Examinez chaque capacité demandée, et n’ajoutez pas un ensemble de capacités « au cas où ».

### 3.2 Système de fichiers en lecture seule

Un root filesystem en lecture seule limite la modification de l’image en exécution et rend certains comportements persistants plus difficiles. L’application peut toutefois avoir besoin d’écrire des fichiers temporaires, cache ou rapports. Dans ce cas, fournissez des volumes explicitement limités et accessibles au seul processus concerné, plutôt que de rendre tout le système de fichiers inscriptible.

~~~text
Image immuable
  |
  +--> code et dépendances : lecture seule
  +--> configuration : lecture seule, sans secret si public
  +--> répertoire temporaire : volume dédié et limité
  +--> données persistantes : volume ciblé, droits restreints
  +--> socket du daemon : jamais monté pour une application ordinaire
~~~

Une couche en lecture seule ne protège pas une donnée écrite dans un volume auquel l’application a un droit excessif. Il faut limiter aussi le stockage, l’identité du processus et les permissions du volume.

### 3.3 Docker daemon et socket

Le daemon Docker est une interface administrative puissante. Un utilisateur capable de contrôler le socket Docker peut souvent lancer des conteneurs, monter des répertoires de l’hôte et obtenir des privilèges très élevés. Ne montez pas le socket du daemon dans un conteneur applicatif standard. Ne rendez pas l’API du daemon accessible sur le réseau sans authentification et protections adaptées.

Un service Web qui reçoit des requêtes et traduit des paramètres utilisateur en commandes Docker représente une frontière particulièrement sensible. Il doit valider strictement le schéma et la liste des options permises, ne pas exécuter de commandes construites par concaténation et utiliser une identité de service très limitée. Le plus sûr peut être de ne pas exposer du tout la fonction de création arbitraire de conteneurs.

### 3.4 Mode rootless et user namespaces

Le mode rootless permet d’exécuter le daemon et les conteneurs sans privilèges root de l’hôte, sous réserve des prérequis et limites de l’environnement. Il réduit l’impact de certains scénarios mais ne supprime pas les vulnérabilités du noyau partagé, les erreurs applicatives ou le besoin de contrôler les fichiers et le réseau. Le mode userns-remap a une différence importante : le daemon peut encore fonctionner avec des privilèges root alors que les identifiants des utilisateurs sont remappés.

~~~text
Moteur classique
Daemon avec privilèges hôte -> conteneurs selon profil

Mode rootless
Utilisateur non-root -> daemon rootless -> conteneurs
                  réduction de la portée, pas garantie absolue

Dans les deux cas :
noyau corrigé + image fiable + moindre privilège + audit
~~~

Le choix de rootless doit tenir compte des ports, volumes, limites de noyau, compatibilité du stockage, outils de supervision et besoins opérationnels. Testez le modèle choisi dans l’environnement cible.

### 3.5 Contrôler les ressources

Un conteneur peut consommer une quantité excessive de CPU, mémoire, processus, connexions ou stockage. Cela peut affecter les autres workloads et devenir un déni de service. Fixez les limites appropriées, mesurez les usages réels et configurez des alertes de saturation. Le choix de valeurs trop faibles peut aussi créer une indisponibilité ; les limites doivent être dérivées de tests de charge et de la criticité.

~~~text
Ressource non limitée
  workload A consomme la mémoire
          |
          v
  pression sur l'hôte -> OOM / arrêt d'autres services

Avec limites / quotas
  workload A limité à son budget
          |
          v
  dépassement détecté -> isolation de l'impact et alerte
~~~

## 4. Chaîne d'approvisionnement des images

### 4.1 Registre, identité et provenance

Le registre doit limiter qui peut publier, remplacer, supprimer ou télécharger les images privées. Les comptes de lecture et de publication doivent être distincts. Les images de production devraient provenir de pipelines contrôlés et d’un processus d’approbation connu. N’utilisez pas une image dont le nom semble officiel sans vérifier le dépôt, l’organisation, la provenance et le digest.

La provenance indique comment un artefact a été produit : sources, pipeline, outils et paramètres peuvent être associés à la build. Une signature permet de vérifier l’intégrité et le signataire selon le modèle de confiance configuré. La signature ne garantit pas que l’application ne contient aucune vulnérabilité ; elle garantit une propriété de provenance ou d’intégrité qui doit être combinée à la revue, aux scans et aux politiques.

~~~text
Code revu
   |
   v
Pipeline authentifié
   |
   +--> dépendances verrouillées
   +--> scan code et image
   +--> génération d'une SBOM
   +--> provenance / signature
   |
   v
Registre protégé
   |
   v
Admission : vérifier source, digest, signature et politique
   |
   v
Déploiement
~~~

### 4.2 Scan des vulnérabilités

Un scanner d’image identifie des composants et les compare à des bases de vulnérabilités. Un résultat doit inclure le nom du paquet, la version, l’identifiant d’avis, la version corrigée lorsqu’elle est connue et le contexte d’exposition. Les faux positifs, composants non utilisés ou vulnérabilités difficiles à exploiter doivent être évalués, mais pas ignorés par réflexe.

Définissez des critères de blocage explicites : par exemple, aucune vulnérabilité critique non traitée dans les composants exposés, et aucune exception sans propriétaire et date de réévaluation. Un scan à un instant T ne garantit pas qu’aucun nouvel avis ne sera publié ; les images déployées doivent être suivies et reconstruites.

### 4.3 SBOM, signatures et images immuables

Une Software Bill of Materials (SBOM) inventorie les composants logiciels d’un artefact. Elle aide à rechercher rapidement quels workloads sont concernés lorsqu’une bibliothèque est vulnérable. La SBOM doit correspondre exactement à l’artefact publié ; une liste indépendante ou incomplète ne donne pas cette assurance.

Le digest d’image permet de référencer une image précise plutôt qu’un tag mutable. Les signatures et attestations doivent être vérifiées au moment du déploiement avec des règles d’identité et de provenance. Définissez qui a le droit de signer, où les clés ou identités sont protégées et comment révoquer un signataire compromis.

### 4.4 Dépendances et images tierces

Privilégiez les sources maintenues, vérifiez leurs politiques de version et remplacez les images obsolètes. Évitez de récupérer une image arbitraire à chaque démarrage. La reproductibilité permet de reconstruire un artefact, de comparer les changements et d’enquêter après incident. Les composants téléchargés au build doivent être versionnés et, lorsque possible, vérifiés par checksum ou signature.

### 4.5 Secrets CI/CD et privilèges de publication

Le pipeline de build et de déploiement est une cible privilégiée, car il peut publier du code qui sera ensuite exécuté en production. Séparez les identités, limitez les secrets par job, évitez les jetons accessibles aux builds de contributions non fiables et empêchez un artefact non approuvé de se promouvoir lui-même en production. Le droit de publier une image ne doit pas automatiquement permettre de modifier l’identité de cluster.

~~~text
Identité build : lire source + créer artefact
Identité registre : publier l'image du dépôt ciblé
Identité déploiement : déployer dans namespace autorisé
Identité cluster admin : opérations séparées, pas accessible au build
~~~

## 5. Kubernetes : architecture et plans de contrôle

### 5.1 Composants du cluster

Kubernetes orchestre des workloads à travers un plan de contrôle et des nœuds. L’API server reçoit les opérations ; l’authentification établit le principal, l’autorisation comme RBAC décide les actions permises, les contrôleurs rapprochent l’état observé de l’état désiré, le scheduler sélectionne les nœuds et le kubelet coordonne l’exécution sur le nœud. Le runtime exécute les conteneurs.

~~~text
Utilisateur / pipeline
         |
         v
     API server
         |
         +--> Authentification
         +--> Autorisation RBAC
         +--> Admission et validation
         |
         v
  État désiré dans le datastore
         |
         v
  Scheduler -> nœud -> kubelet -> runtime -> conteneur
                           |
                           v
                       observations
~~~

Le plan de contrôle doit être traité comme un actif critique. L’accès à l’API, au kubelet et au datastore du cluster doit être restreint aux chemins nécessaires. Les composants doivent utiliser leurs identités et certificats attendus, les permissions doivent être minimales et les journaux d’audit protégés. Dans un cluster managé, le fournisseur gère une partie du plan de contrôle, mais les configurations clientes, identités, politiques de namespace et workloads restent à sécuriser.

### 5.2 Namespaces et multi-tenance

Les namespaces permettent d’organiser les ressources, les quotas et certaines politiques de manière logique. Ils ne constituent pas à eux seuls une frontière d’isolation complète. Un utilisateur ayant des permissions transverses peut accéder à plusieurs namespaces ; un Pod trop privilégié peut affecter le nœud ou d’autres workloads ; des réseaux peuvent rester joignables sans NetworkPolicy.

~~~text
Cluster
  |
  +--> namespace cours
  |      +--> frontend
  |      +--> API
  |
  +--> namespace outils
  |      +--> pipeline / observabilité
  |
  +--> namespace données
         +--> traitements sensibles

Chaque espace :
RBAC ciblé + Pod Security + quotas + NetworkPolicy
~~~

La multi-tenance forte peut nécessiter des clusters séparés, des nœuds dédiés, des runtimes plus isolés ou une séparation de comptes cloud. Le niveau nécessaire dépend du risque, de la sensibilité des données, des utilisateurs qui peuvent créer des workloads et des garanties de la plateforme choisie.

### 5.3 Nœuds, kubelet et accès de gestion

Les nœuds doivent utiliser des systèmes maintenus, recevoir des correctifs et limiter les accès d’administration. Le kubelet expose une API de gestion qui doit être protégée et non accessible directement depuis Internet. Le plan de contrôle et les nœuds ne devraient pas accepter de chemins de gestion généraux non documentés. Contrôlez les identités machines, certificats, ports, règles de réseau et accès par console.

Une compromission de nœud peut affecter les Pods qui y sont exécutés et certaines informations locales. Les workloads sensibles peuvent nécessiter une séparation de placement ou un runtime plus isolé. Les règles de placement doivent être contrôlées ; sinon, les Pods pourraient se retrouver sur un nœud moins protégé en raison d’une configuration ou d’une tolérance trop large.

## 6. Kubernetes RBAC et identité des workloads

### 6.1 RBAC à portée minimale

RBAC définit quels principaux peuvent réaliser quels verbes sur quelles ressources et dans quelle portée. Role et RoleBinding sont généralement namespacés ; ClusterRole et ClusterRoleBinding peuvent couvrir des ressources ou portées plus larges. Le choix de la liaison compte autant que le rôle lui-même. Un rôle limité peut devenir très puissant s’il est lié globalement au mauvais principal.

Évitez de donner à un développeur ou à une application le rôle cluster-admin pour simplifier un déploiement. Examinez les droits de création, mise à jour, patch, suppression, exécution dans un conteneur, lecture de secrets, création de bindings et gestion de rôles. Certaines autorisations permettent indirectement une élévation de privilèges : par exemple, créer un Pod qui monte un secret ou utiliser un compte de service différent peut étendre les accès du demandeur selon les autres politiques.

~~~text
Développeur
    |
    +--> peut lire Deployments dans namespace cours
    +--> peut créer un déploiement selon le pipeline approuvé
    X--> ne peut pas créer un ClusterRoleBinding
    X--> ne peut pas lire les secrets de tous les namespaces
    X--> ne peut pas modifier les règles d'admission globales
~~~

### 6.2 Comptes de service Kubernetes

Un ServiceAccount représente l’identité d’un workload dans Kubernetes. N’utilisez pas automatiquement le ServiceAccount default pour toutes les applications. Créez une identité distincte par besoin, limitez les permissions RBAC et désactivez le montage automatique de jeton si l’application ne communique pas avec l’API Kubernetes. Lorsque l’API est nécessaire, utilisez les jetons liés à la charge de travail et les mécanismes courants de durée limitée plutôt que des credentials non expirants.

~~~yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: portal-api
  namespace: cours
automountServiceAccountToken: false
~~~

Ce manifeste est un exemple de principe. Si le code a besoin de lire des objets de l’API, le montage automatique désactivé doit être remplacé par une méthode explicite et les permissions doivent être ciblées. Ne désactivez pas un mécanisme sans vérifier les dépendances de l’application.

### 6.3 Le droit de créer des Pods peut être sensible

Créer ou modifier un Pod ne se limite pas toujours à exécuter une application inoffensive. Si l’auteur peut définir un ServiceAccount, des volumes, des hôtes de montage, un mode privilégié ou certaines options de sécurité, il peut potentiellement utiliser cette capacité pour accéder à des ressources qu’il ne pourrait pas lire directement. Les politiques d’admission et la sécurité des Pods servent à restreindre les configurations possibles.

Il faut donc revoir les permissions de gestion des workloads avec la même attention que celles de lecture des Secrets. Les permissions d’exécution dans un conteneur peuvent également être sensibles, car elles permettent d’agir dans le contexte de l’application et de lire les fichiers ou secrets auxquels le conteneur a accès.

### 6.4 Élévation et sujets sensibles

Les droits permettant de créer ou modifier Roles, RoleBindings, ClusterRoles ou ClusterRoleBindings doivent être limités. Une identité pouvant attribuer un rôle puissant peut souvent se donner ou accorder à un tiers des permissions supplémentaires. Séparez la gestion des applications de l’administration de la sécurité du cluster, et soumettez les changements sensibles à une revue.

## 7. Pod Security Standards et securityContext

### 7.1 Profils Privileged, Baseline et Restricted

Les Pod Security Standards définissent des niveaux de politique. Le niveau Privileged est permissif et destiné aux workloads nécessitant de larges capacités. Baseline vise à empêcher certains élargissements connus tout en conservant une compatibilité assez large. Restricted applique un profil plus strict, notamment sur les privilèges, capacités, systèmes de fichiers et paramètres de sécurité. Choisissez le niveau en fonction des besoins ; ne laissez pas tous les namespaces adopter des Pods privilégiés.

L’application des standards peut être réalisée avec Pod Security Admission selon la configuration du cluster, et peut être complétée par des politiques d’admission. Un refus d’admission doit expliquer la raison et proposer un processus de correction ou d’exception documentée. Une politique plus stricte est utile seulement si les équipes savent livrer leurs workloads sans la contourner.

### 7.2 Exemple de securityContext

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: portal-api
  namespace: cours
spec:
  serviceAccountName: portal-api
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: api
      image: registry.example.invalid/campus/api@sha256:0123456789abcdef
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        privileged: false
        capabilities:
          drop:
            - ALL
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "256Mi"
~~~

Le digest dans cet exemple est fictif et doit être remplacé par le digest réel de l’image approuvée. Le manifeste est un modèle de départ, pas une configuration universelle prête à déployer. Une application peut nécessiter un volume temporaire en écriture ou des paramètres différents ; documentez le besoin et gardez le système de fichiers racine en lecture seule lorsque possible.

### 7.3 Capacités, seccomp et profils du noyau

Drop ALL retire les capacités Linux supplémentaires, puis seules les capacités nécessaires sont ajoutées explicitement après analyse. Seccomp peut limiter les appels système ; AppArmor ou SELinux peuvent appliquer des profils supplémentaires selon les nœuds. Ces mécanismes sont complémentaires. Un profil trop permissif réduit la protection ; un profil trop strict peut empêcher le démarrage ou certaines fonctions.

Testez la politique dans un environnement de préproduction, observez les refus et adaptez le profil au programme. Ne désactivez pas globalement une protection parce qu’un conteneur échoue : identifiez d’abord l’appel ou la permission nécessaire et évaluez si cette fonctionnalité devrait être autorisée.

### 7.4 Hôte, namespaces et montages dangereux

Évitez hostPID, hostNetwork, hostIPC, les montages hôte étendus, les périphériques et le mode privilégié sauf justification rare. Un montage inscriptible de chemins sensibles peut exposer le système hôte. Les Pods ne devraient pas accéder aux fichiers du nœud ou sockets d’administration sans besoin explicite. L’accès à un socket de moteur de conteneur peut donner un pouvoir élevé, même si le conteneur ne tourne pas lui-même en root.

### 7.5 Exécution non-root et permissions de fichiers

Un conteneur non-root échouera si les répertoires applicatifs sont inscriptibles uniquement par root. Préparez les permissions d’image correctement, choisissez un UID stable si approprié et utilisez fsGroup seulement lorsque c’est nécessaire. Vérifiez aussi les permissions des volumes persistants ; un securityContext correct ne compense pas un volume accessible à tous.

## 8. Secrets Kubernetes et données sensibles

### 8.1 Secret n’est pas synonyme de chiffrement automatique

Un objet Secret Kubernetes représente des données sensibles, mais sa présence dans l’API ne garantit pas à elle seule le chiffrement au repos, la confidentialité des journaux ou l’absence d’accès excessif. Vérifiez la configuration de chiffrement du datastore, les permissions RBAC, la sauvegarde, les accès administratifs et la manière dont la valeur est injectée dans le conteneur. Ne mettez pas un mot de passe dans un ConfigMap destiné à des données non confidentielles.

### 8.2 Injecter un secret sans le publier dans l’image

Les secrets peuvent être montés en volume ou transmis via un mécanisme externe pris en charge. Les variables d’environnement sont pratiques mais peuvent être exposées par des dumps, diagnostics, journaux ou outils d’inspection. Un fichier monté avec des droits étroits est souvent plus facile à limiter, sans être automatiquement sûr : il faut aussi contrôler les permissions du fichier, les processus et la durée de vie du secret.

~~~text
Gestionnaire de secrets
       |
       v
Identité du workload autorisée
       |
       v
Injection à l'exécution
       |
       v
Application lit uniquement le secret nécessaire

À éviter :
secret -> Dockerfile -> image -> registre -> environnements multiples
~~~

Évitez d’accorder à chaque Pod le droit de lire tous les Secrets du namespace. Injectez seulement les secrets requis, limitez la portée et documentez leur propriétaire et leur rotation. Lorsqu’un secret change, vérifiez comment l’application reçoit la nouvelle valeur et si un redémarrage est nécessaire.

### 8.3 Jetons de ServiceAccount

Ne montez pas un jeton d’API Kubernetes dans chaque Pod par défaut si l’application n’en a pas besoin. Lorsque nécessaire, préférez des jetons liés et de durée limitée. La portée d’un jeton dépend aussi de l’identité, des règles RBAC et de la manière dont l’application le protège. Une fuite de jeton doit entraîner une révocation ou une suppression de l’accès pertinente et une revue des actions observées.

### 8.4 Secrets externes et rotation

Un fournisseur de secrets externe ou un CSI driver peut aider à éviter de stocker certaines valeurs dans le datastore Kubernetes, mais il introduit ses propres identités, politiques et dépendances. Vérifiez le mode de récupération, le cache, les permissions, la journalisation, le comportement en panne et la procédure de rotation. Un secret externe ne protège pas si tous les Pods possèdent la même identité qui peut lire tous les secrets.

## 9. Réseau Kubernetes : isolation et flux

### 9.1 Le réseau plat est un risque

Dans un cluster, des Pods peuvent pouvoir communiquer entre eux selon la configuration réseau. Sans politique adaptée, un service exposé ou compromis peut essayer d’atteindre des API internes, bases de données, systèmes de métriques ou endpoints d’administration. Les NetworkPolicies permettent de limiter les flux entrant et sortant quand le plugin réseau utilisé les prend effectivement en charge.

~~~text
Ingress utilisateur
       |
       v
Service frontend
       |
       | autorisé
       v
API du portail
       |
       | autorisé vers port DB uniquement
       v
Base de données

Frontend -X-> base directe
Namespace cours -X-> outils d'administration
Pod quelconque -X-> API cluster si inutile
~~~

Une politique n’a d’effet que si la plateforme réseau supporte et applique les NetworkPolicies. Vérifiez le plugin CNI, le comportement des flux DNS et les règles de sortie. Une politique qui sélectionne zéro Pod ou ne correspond pas aux labels attendus peut donner une illusion de sécurité sans réduire les flux réels.

### 9.2 Deny-by-default et exceptions explicites

Une approche robuste commence souvent par un refus par défaut des flux non nécessaires, puis ajoute les chemins indispensables. Dans un namespace applicatif, autorisez l’entrée depuis le point d’entrée approuvé vers le frontend, du frontend vers l’API et de l’API vers les services de données requis. Les sorties vers le DNS ou les API externes nécessaires doivent être traitées explicitement, avec les particularités du cluster.

~~~yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-unlisted-ingress
  namespace: cours
spec:
  podSelector: {}
  policyTypes:
    - Ingress
~~~

Ce manifeste illustre un refus par défaut des flux entrants dans le namespace sélectionné ; il faut vérifier les règles existantes, les dépendances et l’implémentation CNI avant application. Une politique d’entrée ne contrôle pas automatiquement les sorties. La stratégie complète doit couvrir ingress et egress selon le modèle de menace.

### 9.3 DNS et métadonnées cloud

Les Pods peuvent nécessiter DNS, mais un accès DNS complet peut également servir à exfiltrer des données ou à atteindre des domaines indésirables. Définissez ce qui est nécessaire et surveillez les anomalies. Dans un cloud, contrôlez l’accès des workloads aux endpoints de métadonnées de l’hôte, car une configuration insuffisante peut exposer des informations ou identifiants selon la plateforme. N’autorisez pas l’accès si le workload n’en a pas besoin.

### 9.4 Ingress, LoadBalancer et endpoints externes

Un Service de type LoadBalancer, Ingress ou ExternalIPs peut publier un workload au-delà du cluster. L’exposition doit être approuvée, limitée aux routes et ports nécessaires, protégée par TLS et authentification applicative et surveillée. Les API Kubernetes, kubelet et datastore ne doivent pas être exposés publiquement. Le fait qu’un cluster soit géré par le fournisseur ne rend pas ses endpoints publics inoffensifs.

### 9.5 DNS, service mesh et chiffrement interne

Un service mesh peut fournir identité service-à-service, chiffrement et politiques de communication, selon le produit et son déploiement. Il introduit également un plan de contrôle, des certificats, des proxies et des politiques à sécuriser. Le maillage ne remplace ni l’autorisation métier ni les NetworkPolicies, et ne protège pas automatiquement les workloads hors de sa couverture.

## 10. Isolation et sécurité du cluster

### 10.1 Nœuds dédiés et workloads sensibles

Si le cluster héberge des workloads de sensibilités différentes, une séparation par nœuds, pools ou clusters peut réduire les possibilités de mouvement latéral. Les labels, taints, tolerations, affinités et RuntimeClass peuvent contribuer au placement, mais leurs permissions de modification doivent être restreintes. Une équipe autorisée à altérer les labels de placement peut parfois orienter un workload vers un nœud inattendu.

Les charges sensibles peuvent nécessiter un runtime plus isolé ou une séparation plus forte. Le choix dépend du niveau de menace, de la compatibilité et des performances. Une fonctionnalité d’isolation n’est pas une raison pour négliger la mise à jour du noyau, les permissions ou les contrôles d’accès.

### 10.2 RuntimeClass et autres mécanismes d'isolation

Les environnements d’exécution tels que les runtimes sandboxés peuvent fournir une frontière supplémentaire pour certains workloads. Ils nécessitent un support spécifique sur les nœuds et une configuration de plateforme. Testez les appels système, volumes, diagnostics et contraintes de performance avant de les appliquer à une application importante.

### 10.3 API server et datastore

Restreignez l’accès réseau à l’API server et protégez ses identités d’administration. Les journaux d’audit doivent couvrir les événements importants, en particulier les lectures de secrets et les changements de rôles, politiques, workloads ou paramètres sensibles selon les capacités du cluster. Protégez les journaux contre les utilisateurs qui peuvent déjà administrer le cluster.

Le datastore du plan de contrôle contient un état précieux : objets Kubernetes, métadonnées et potentiellement valeurs sensibles selon la configuration. Il ne doit pas être exposé à Internet ; les communications utilisent les protections cryptographiques appropriées et les accès sont limités. Dans un cluster managé, les responsabilités exactes dépendent de l’offre, mais l’organisation cliente doit toujours évaluer les configurations et options exposées.

### 10.4 Admission controllers et politiques

Les mécanismes d’admission peuvent valider ou modifier les objets avant leur enregistrement. Pod Security Admission applique les standards de sécurité des Pods selon le mode configuré. Des webhooks ou politiques de validation supplémentaires peuvent vérifier les registries autorisés, les digests, les signatures, les labels, les références de secrets et les restrictions de privilèges.

Ces contrôles font partie du chemin critique de déploiement. Un webhook en panne peut bloquer des déploiements si la politique est configurée pour échouer en cas d’erreur ; un mode trop permissif peut laisser passer des objets non vérifiés. Documentez les comportements en panne et testez l’extension d’admission comme un composant de production.

## 11. Ressources, disponibilité et quotas

### 11.1 Requests, limits, quotas et LimitRange

Les requests servent au placement et à la réservation de ressources ; les limits encadrent la consommation selon le type de ressource et le comportement de la plateforme. Les quotas de namespace peuvent empêcher une équipe ou un processus de consommer toutes les ressources du cluster. Une configuration correcte contribue à la stabilité et à la sécurité, car le déni de service peut provenir d’une boucle de calcul ou d’un flux de requêtes incontrôlé.

~~~text
Namespace cours
  quota CPU / mémoire / volumes
       |
       v
Pod API : requests et limits adaptés
       |
       +--> usage normal : service disponible
       +--> dépassement : limite ou alerte
       |
       v
Les autres namespaces conservent leur budget
~~~

Dimensionnez les limites après des tests de charge. Des limites trop faibles peuvent provoquer des redémarrages ou des erreurs ; des limites trop larges rendent les quotas inefficaces. Contrôlez aussi le nombre de Pods, objets, volumes, connexions et journaux lorsque ces ressources influencent le coût ou la disponibilité.

### 11.2 Probes et boucle de redémarrage

Les probes de démarrage, de disponibilité et de vivacité ont des objectifs différents. Une mauvaise probe peut provoquer des redémarrages répétitifs, masquer un incident ou détourner du trafic vers une instance non prête. Définissez les endpoints et seuils selon l’application et évitez d’exposer un endpoint de santé qui divulgue des informations sensibles.

### 11.3 Limites et autoscaling

L’autoscaling améliore la capacité, mais ne remplace pas les limites de coût ni la protection contre l’abus. Un workload exposé peut déclencher une montée en charge coûteuse. Mettez en place des budgets, quotas, alertes de consommation et mécanismes applicatifs de rate limiting. Testez le comportement quand les ressources sont rares.

## 12. Surveillance et détection à l'exécution

### 12.1 Événements utiles

Les événements à surveiller incluent les créations de Pods privilégiés, les changements de rôles et bindings, les lectures de Secrets, l’usage de conteneurs éphémères, les montages inattendus, les connexions réseau inhabituelles, les échecs d’admission, les changements de politiques et les redémarrages répétés. Les journaux d’application et d’infrastructure doivent être corrélés par horodatage, namespace, image, workload et identité lorsque possible.

~~~text
Sources
  +--> audit API Kubernetes
  +--> logs des workloads
  +--> événements du cluster
  +--> télémétrie runtime / hôte
  +--> flux réseau / DNS
  +--> scans / posture du registre
          |
          v
Normalisation + corrélation
          |
          v
Alerte avec ressource et principal
          |
          v
Triage / confinement / preuve / récupération
~~~

Ne journalisez pas les secrets ou les corps de requête confidentiels par défaut. Les logs doivent être protégés contre la lecture ou la modification non autorisée. Une collecte complète en théorie mais jamais testée peut manquer un événement en pratique ; générez régulièrement des événements de test et vérifiez leur réception.

### 12.2 Détection de comportement

Une activité inhabituelle peut inclure des tentatives d’accès à des fichiers du nœud, des connexions vers des destinations inattendues, un téléchargement massif de données, la consultation de nombreux secrets ou une création de privilèges inhabituelle. Les règles doivent tenir compte du contexte opérationnel : une fenêtre de maintenance peut légitimement produire davantage de changements, mais elle doit être approuvée et identifiable.

### 12.3 Réponse à un conteneur compromis

La procédure peut inclure la restriction réseau du Pod ou du namespace, la révocation de secrets et jetons accessibles, la préservation des journaux, l’identification du digest et de la provenance de l’image, l’arrêt ou remplacement selon le plan et l’analyse des workloads voisins. Ne supprimez pas automatiquement tous les éléments sans préserver les preuves nécessaires. Le confinement doit équilibrer continuité et propagation du risque.

~~~text
Alerte runtime
   |
   v
Identifier Pod / nœud / digest / identité / heure
   |
   v
Limiter les flux et révoquer les secrets concernés
   |
   v
Préserver logs et preuves selon la procédure
   |
   v
Rechercher les autres déploiements de la même image
   |
   v
Reconstruire depuis une source approuvée, déployer et surveiller
   |
   v
Cause racine + remédiation + tests anti-récidive
~~~

## 13. Sécurité des workloads et applications

### 13.1 La sécurité du cluster ne corrige pas la faille applicative

Une application peut rester vulnérable aux injections, erreurs d’autorisation, XSS, SSRF et défauts de gestion de session même si le Pod respecte les standards. La sécurité applicative doit contrôler les identités, les objets, les entrées et les sorties. Kubernetes fournit des mécanismes d’isolation et d’orchestration, pas une garantie que le code métier est sûr.

### 13.2 Configuration externe et immutabilité

Séparez la configuration non sensible de l’image, mais vérifiez que ses valeurs ne permettent pas d’activer le mode debug, de désactiver TLS ou d’exposer une interface de gestion. Les ConfigMaps ne doivent pas contenir des secrets. Évitez les modifications manuelles à l’intérieur du conteneur : elles rendent les déploiements non reproductibles et compliquent l’investigation. Construisez une nouvelle image approuvée pour un changement applicatif.

### 13.3 Validation des entrées et permissions de sortie

Une API de contrôle qui accepte des paramètres utilisateur puis crée un Pod ou une ressource cloud est particulièrement sensible. Définissez un schéma strict, une liste de champs permis, des limites de ressources et un ensemble réduit d’options. Ne transformez jamais une chaîne contrôlée par l’utilisateur en commande système ou manifeste Kubernetes arbitraire sans validation structurée et autorisation.

### 13.4 Fichiers et volumes

Les volumes persistants peuvent conserver des données après le remplacement d’un Pod. Vérifiez leurs règles d’accès, leur classe de stockage, les politiques de sauvegarde, le chiffrement et les droits du processus. Les montages en lecture-écriture ne doivent être accordés que si l’application en a besoin. Les fichiers temporaires et caches doivent être séparés des données persistantes.

### 13.5 Interfaces de debug et conteneurs éphémères

Les conteneurs éphémères peuvent être utiles pour diagnostiquer un workload, mais l’autorisation de les créer ou d’entrer dans un conteneur est sensible. Limitez-la aux personnes de support autorisées et journalisez l’usage. Évitez de conserver des outils ou shell de débogage dans chaque image de production sans nécessité. Une session de diagnostic doit respecter le périmètre et la confidentialité des données.

## 14. Gouvernance et maturité opérationnelle

### 14.1 Politique standard et exceptions

Définissez une baseline pour toutes les images et workloads : provenance connue, image maintenue, analyse de vulnérabilités, utilisateur non-root, absence de secrets dans l’image, capacités minimales, limites de ressources, identité de service spécifique, accès réseau réduit et journaux utiles. Les exceptions doivent avoir un propriétaire, une justification, une portée, des mesures compensatoires et une date de fin.

### 14.2 Responsabilités par équipe

Les développeurs sont responsables de la conception applicative et de la gestion des dépendances ; la plateforme gère les nœuds, runtimes et mécanismes de cluster relevant de son périmètre ; l’équipe sécurité définit les standards et surveille les risques ; l’équipe CI/CD protège la chaîne de build ; les propriétaires métier valident les besoins d’exposition et de disponibilité. Une matrice claire évite que les alertes restent sans responsable.

### 14.3 Mesurer ce qui réduit réellement le risque

Suivez la proportion d’images de production référencées par digest, la couverture de scan, le temps de correction des vulnérabilités critiques, le nombre de Pods privilégiés, les workloads root, les secrets exposés, la couverture des NetworkPolicies, les permissions RBAC trop larges, les écarts d’admission et les délais de révocation. Chaque indicateur doit avoir une source, un dénominateur, un responsable et une fréquence.

~~~text
Indicateur                    Question
Images approuvées             Toutes les releases ont-elles une provenance ?
Non-root                      Quels workloads exécutent un processus privilégié ?
Réseau                         Quels namespaces ont une politique effective ?
RBAC                           Qui peut créer Pods, secrets ou rôles ?
Secrets                        Les identifiants dépassés sont-ils révoqués ?
Vulnérabilités                 Quel délai entre avis et image corrigée ?
Runtime                        Les alertes sont-elles reçues et traitées ?
Récupération                   Le retour à une image saine est-il testé ?
~~~

## 15. Travaux pratiques corrigés

### TP 1 — Durcir une image Docker

**Objectif :** passer d’une image de développement à une image de production moins privilégiée.

**Contexte :** une API fictive est construite dans une image basée sur une distribution complète, démarre en root, conserve des outils de compilation, copie un fichier de configuration et exécute un gestionnaire de processus de débogage. Le but est d’améliorer le Dockerfile sans modifier la logique métier.

**Étape 1.** Identifiez les besoins d’exécution réels : runtime, bibliothèques, port, fichiers écrits, certificats nécessaires et logs. Supprimez les dépendances de développement inutiles de l’image finale. Utilisez une image de base maintenue dont la provenance est vérifiée.

**Étape 2.** Séparez compilation et exécution avec un multi-stage build si le projet le permet. Copiez seulement le binaire ou le résultat requis. Définissez un utilisateur non privilégié et les permissions des répertoires.

**Étape 3.** Retirez le secret du Dockerfile et de tous les fichiers copiés. Fournissez la configuration non sensible séparément et le secret par une méthode d’exécution adaptée. Fixez un système de fichiers en lecture seule si le programme le permet et un espace temporaire dédié pour les écritures nécessaires.

**Étape 4.** Construisez l’image, scannez-la, inspectez les utilisateurs et volumes, puis exécutez un test fonctionnel. Vérifiez qu’elle ne nécessite ni mode privilégié, ni socket Docker, ni capacité ajoutée sans raison.

~~~text
Avant
image de base complète -> root -> secret copié -> outils inutiles
                 |
                 v
        surface d'attaque élevée

Après
image finale minimale -> utilisateur non-root
secret injecté au runtime -> FS en lecture seule si possible
scan + digest + tests -> artefact traçable
~~~

**Correction expliquée.** Le Dockerfile final doit refléter le strict besoin d’exécution. L’étape de build peut contenir les outils nécessaires, mais ils ne doivent pas être inclus inutilement dans l’image publiée. Le secret doit être révoqué si l’image précédente a été distribuée et doit être remplacé, pas seulement supprimé dans une version ultérieure.

**Critères d’acceptation :** l’image n’exécute pas l’application en root sans justification ; aucun secret n’est présent dans les couches ; l’image et ses dépendances sont scannées ; le démarrage fonctionne avec les permissions réduites ; l’artefact publié est identifié par un digest.

### TP 2 — Appliquer une politique Pod et Kubernetes RBAC

**Objectif :** limiter ce qu’un développeur et un workload peuvent faire dans le cluster.

**Contexte :** le namespace cours contient l’API. Un développeur doit voir l’état de son déploiement mais ne doit pas lire les Secrets de production, créer des ClusterRoleBindings ni exécuter des conteneurs privilégiés.

**Étape 1.** Concevez un Role namespacé qui autorise uniquement les lectures nécessaires des Deployments, Pods et Events. Créez un RoleBinding au principal de développement, sans lier de rôle cluster-admin.

**Étape 2.** Attribuez un ServiceAccount dédié à l’API et désactivez le montage automatique du jeton si l’application ne contacte pas l’API Kubernetes. Donnez-lui seulement les permissions nécessaires si cette communication est requise.

**Étape 3.** Activez une politique de sécurité de Pod adaptée au namespace et définissez les contrôles souhaités : non-root, absence de privilèges, capacités supprimées, élévation interdite et système de fichiers en lecture seule lorsque possible.

**Étape 4.** Testez un déploiement conforme et des tentatives non conformes. Vérifiez les décisions réellement appliquées par l’API et l’admission. Le test doit inclure un refus de lecture des Secrets par le développeur et un refus de Pod privilégié.

~~~text
Développeur
  autorisé : lire Pods et Deployments dans le namespace prévu
  refusé : lire Secrets de production
  refusé : créer ClusterRoleBinding
  refusé : déployer un Pod privileged

Service API
  autorisé : opérations métier attendues
  refusé : gérer les identités et politiques du cluster
~~~

**Correction expliquée.** Le modèle RBAC doit être minimal et namespacé quand possible. Le rôle ne devrait pas accorder la création ou modification des rôles si ce n’est pas le besoin de travail. Les politiques d’admission sont un contrôle distinct : les autorisations RBAC ne garantissent pas que la spécification d’un Pod respecte les paramètres de sécurité.

**Critères d’acceptation :** l’identité développeur ne lit pas les Secrets non nécessaires ; les permissions sont limitées au namespace ; la création de Pod non conforme est rejetée ; le workload utilise son identité dédiée ; les preuves sont capturées sans secrets.

### TP 3 — Segmenter les flux d’un namespace

**Objectif :** autoriser les chemins nécessaires entre frontend, API et base de données.

**Contexte :** le frontend et l’API s’exécutent dans un cluster de test, et la base est dans un réseau de données protégé. Sans politique explicite, plusieurs Pods peuvent communiquer entre eux. Les labels et noms utilisés sont des exemples à adapter.

**Étape 1.** Cartographiez les flux : entrée vers le frontend, frontend vers API, API vers base de données et DNS vers le service nécessaire. Listez les flux de supervision et sauvegarde légitimes.

**Étape 2.** Définissez une politique par défaut pour bloquer les flux entrants non autorisés dans le namespace. Ajoutez une règle entrante vers le frontend depuis l’ingress approuvé, puis une règle pour le flux vers l’API. Ajoutez les règles de sortie correspondantes, en tenant compte de la résolution DNS et du support CNI.

**Étape 3.** Testez depuis des Pods autorisés et non autorisés. Confirmez que l’API est accessible depuis le frontend mais pas depuis un namespace inattendu et que la base n’est pas accessible directement depuis un Pod frontend.

**Étape 4.** Documentez l’effet réel de la politique sur la plateforme de laboratoire. Si le plugin réseau ne prend pas en charge NetworkPolicy, ne considérez pas le fichier YAML comme une protection active ; choisissez une plateforme supportée ou un autre contrôle de segmentation.

~~~text
Frontend -> API : autorisé
API -> Base de données : autorisé sur port prévu
Frontend -> Base de données : refusé
Namespace non autorisé -> API : refusé
Pod quelconque -> API Kubernetes : refusé si inutile
~~~

**Correction expliquée.** La politique réseau doit correspondre aux labels et aux flux réellement observés. Les règles ingress et egress sont distinctes. Une politique qui ne s’applique pas à la bonne sélection de Pods, ou un plugin CNI qui ne l’applique pas, ne crée aucune garantie. Les tests doivent prouver le comportement du réseau, pas seulement l’existence des objets YAML.

**Critères d’acceptation :** flux nécessaires autorisés ; flux non prévus refusés ; DNS fonctionne selon la politique choisie ; la prise en charge CNI est confirmée ; les changements sont documentés et disposent d’un plan de retour arrière.

### TP 4 — Détecter une image vulnérable et simuler une réponse

**Objectif :** relier l’analyse de build à l’admission et à la réponse à incident.

**Contexte :** un scanner signale une bibliothèque vulnérable dans l’image du service rapports. Le registre contient plusieurs tags et le cluster exécute des versions différentes. Le pipeline doit empêcher la publication non conforme, puis une procédure doit remplacer les workloads concernés.

**Étape 1.** Identifiez chaque déploiement qui utilise le digest vulnérable. Ne vous fiez pas seulement aux tags, qui peuvent être modifiés. Vérifiez la SBOM, la base utilisée et la version corrigée.

**Étape 2.** Mettez à jour la dépendance et reconstruisez une image depuis une source approuvée. Scannez l’image, produisez la SBOM, attachez la provenance et signez l’artefact selon le mécanisme de l’organisation.

**Étape 3.** Définissez la politique d’admission : refuser les images non approuvées ou les digests non autorisés, selon l’architecture. Testez le comportement avec une image conforme et une image qui ne répond pas aux exigences dans un cluster de laboratoire.

**Étape 4.** Simulez le traitement de l’incident : identifier les workloads impactés, contenir selon le risque, préserver les événements, déployer la version corrigée, vérifier les Pods réellement actifs et consigner la clôture.

~~~text
Alerte scanner
   |
   v
Inventaire des digests déployés
   |
   v
Build corrigé -> scan -> SBOM -> provenance / signature
   |
   v
Admission vérifie l'artefact
   |
   v
Déploiement progressif et vérification des Pods
   |
   v
Ancien digest retiré et ticket clôturé
~~~

**Correction expliquée.** L’alerte doit être reliée aux artefacts et workloads réellement déployés. Un tag peut pointer vers un contenu différent plus tard ; le digest est plus fiable pour identifier la version. La signature prouve une relation avec une identité et un contenu selon le mécanisme choisi, mais il faut aussi vérifier la politique du signataire et la qualité du build.

**Critères d’acceptation :** l’image vulnérable est identifiée par digest ; la nouvelle image est reconstruite et scannée ; l’image non conforme échoue au test d’admission ; le déploiement de remplacement est vérifié ; les preuves et la cause racine sont documentées.

## 16. Exercices corrigés

### Exercice 1 — Un conteneur est-il une machine virtuelle ?

Un responsable affirme que chaque conteneur possède son propre noyau, comme une machine virtuelle traditionnelle.

**Correction :** un conteneur Linux partage généralement le noyau de l’hôte et s’appuie sur des mécanismes tels que namespaces, cgroups et contrôles de sécurité. L’isolation n’est donc pas identique à celle d’une VM ; la configuration du runtime, le noyau et les privilèges restent essentiels.

### Exercice 2 — Utilisateur root dans le Dockerfile

L’image démarre en root car « le conteneur est isolé de toute façon ».

**Correction :** l’exécution non-root réduit les pouvoirs disponibles en cas de compromission. Vérifiez les permissions de fichiers et les besoins d’écriture, puis définissez un utilisateur dédié. L’isolation ne justifie pas de donner des privilèges supplémentaires.

### Exercice 3 — Socket Docker monté

Une API monte le socket Docker pour créer les conteneurs demandés par les utilisateurs.

**Correction :** le socket donne un accès administratif puissant au moteur et peut permettre d’agir sur l’hôte. Évitez ce montage pour les applications ordinaires. Si un orchestrateur de conteneurs est nécessaire, créez un service séparé avec API et options strictement limitées, authentification forte et permissions réduites.

### Exercice 4 — Secret supprimé après copie

Le Dockerfile copie un secret, puis le supprime dans l’instruction suivante.

**Correction :** le secret peut rester dans une couche précédente. Supprimez-le des sources, révoquez-le si l’image a été partagée et reconstruisez une image propre. Injectez les secrets au runtime et auditez le pipeline.

### Exercice 5 — Tag latest en production

Un déploiement utilise le tag latest et l’équipe affirme qu’il garantit toujours la version la plus récente et approuvée.

**Correction :** un tag est mutable et ne garantit pas la provenance ou la conformité. Utilisez des versions explicites et des digests pour les releases critiques, associés à des scans, signatures et politiques d’admission.

### Exercice 6 — Image légère mais abandonnée

Une image non maintenue est choisie uniquement parce qu’elle est très petite.

**Correction :** la taille ne prouve ni la maintenance ni la sécurité. Choisissez une base maintenue, vérifiez la provenance et les correctifs, réduisez les composants inutiles et intégrez le scan au cycle de build.

### Exercice 7 — Pod privilégié pour corriger un problème

Une équipe passe un Pod en privileged parce qu’une opération échoue, sans analyse complémentaire.

**Correction :** identifiez la permission réellement nécessaire. Le mode privilégié élargit fortement les capacités et peut affecter l’hôte. Recherchez une capacité limitée, un volume ciblé ou une configuration alternative, puis documentez toute exception indispensable.

### Exercice 8 — Rôle cluster-admin pour un pipeline

Le pipeline utilise cluster-admin pour déployer une seule application dans un namespace.

**Correction :** créez une identité de déploiement namespacée, limitez les verbs et ressources nécessaires et séparez l’administration du cluster. Testez les refus d’accès aux Secrets et aux politiques globales.

### Exercice 9 — Namespace pris pour une frontière complète

Une organisation place deux équipes dans des namespaces différents et autorise toutes les communications entre Pods.

**Correction :** les namespaces organisent les ressources et certaines politiques, mais ne suffisent pas à isoler les flux ou toutes les permissions. Utilisez RBAC, NetworkPolicy, standards de Pod et, si le risque le demande, des nœuds ou clusters séparés.

### Exercice 10 — NetworkPolicy non prise en charge

Des objets NetworkPolicy existent dans le cluster, mais le plugin réseau ne les applique pas.

**Correction :** les manifestes ne créent pas une protection effective sans une implémentation qui les applique. Confirmez le support CNI et testez les flux depuis des workloads de laboratoire. Définissez un contrôle alternatif si nécessaire.

### Exercice 11 — ServiceAccount par défaut

Tous les Pods utilisent le compte default et montent un jeton même s’ils n’appellent jamais l’API Kubernetes.

**Correction :** créez des comptes dédiés et désactivez le montage automatique lorsque le jeton n’est pas nécessaire. Pour les applications qui utilisent l’API, attribuez des permissions minimales et des jetons liés de durée limitée.

### Exercice 12 — ConfigMap utilisé pour un mot de passe

Un mot de passe de base de données est placé dans un ConfigMap.

**Correction :** un ConfigMap est destiné à la configuration non sensible. Placez le secret dans le mécanisme de gestion approuvé, contrôlez l’accès et le chiffrement au repos, et limitez son injection au seul workload qui en a besoin.

### Exercice 13 — Secret Kubernetes accessible au namespace entier

Chaque développeur peut lire tous les Secrets du namespace pour faciliter les diagnostics.

**Correction :** limitez la lecture des Secrets aux identités qui en ont besoin. Les droits de créer ou exécuter des Pods peuvent aussi offrir des chemins indirects d’accès à des secrets, donc les permissions sur les workloads et les politiques d’admission doivent être revues ensemble.

### Exercice 14 — Système de fichiers toujours inscriptible

Le conteneur doit écrire un fichier temporaire, donc le développeur rend tout le système de fichiers inscriptible.

**Correction :** fournissez un volume temporaire ciblé et des permissions minimales. Gardez l’image et les répertoires applicatifs en lecture seule lorsque possible. Testez que le programme fonctionne avec le volume limité.

### Exercice 15 — Limites CPU et mémoire absentes

Un service public n’a ni requests ni limits et lance des calculs coûteux sur des entrées utilisateur.

**Correction :** mesurez le besoin, fixez requests et limits appropriées, définissez des quotas et une limitation de débit applicative. Surveillez l’usage et ajustez les valeurs pour éviter aussi bien la surconsommation que les arrêts fréquents.

### Exercice 16 — Admission désactivée après un blocage

Un webhook d’admission rejette un Pod non conforme ; l’administrateur désactive globalement le contrôle afin que la release passe.

**Correction :** corrigez la spécification ou créez une exception approuvée et temporaire. Un contrôle global désactivé peut laisser passer tous les workloads suivants. Testez les webhooks, le comportement en panne et la procédure d’urgence.

### Exercice 17 — Signature considérée comme une garantie de sécurité totale

Une image est signée, donc l’équipe saute les scans de vulnérabilité.

**Correction :** la signature apporte une preuve d’intégrité ou de provenance selon la confiance configurée. Elle ne prouve pas l’absence de code vulnérable. Combinez identité du signataire, source approuvée, scan, SBOM, revue et validation de la politique.

### Exercice 18 — Journal d’audit non protégé

Les administrateurs du cluster surveillé peuvent supprimer les journaux qui documentent leurs propres actions.

**Correction :** envoyez les journaux critiques vers un périmètre à droits séparés, protégez l’accès et la conservation, surveillez les arrêts de collecte et testez la réception. La séparation réduit le risque mais ne remplace pas la gouvernance des preuves.

### Exercice 19 — Image corrigée mais vieux Pod actif

Le pipeline publie une version corrigée, mais les Pods en cours utilisent encore un ancien digest.

**Correction :** l’image dans le registre ne prouve pas que le cluster l’exécute. Vérifiez les références réellement déployées, l’état du rollout, les réplicas et les anciens workloads. Ne clôturez l’incident qu’après avoir confirmé le remplacement et les tests fonctionnels.

### Exercice 20 — Conteneur compromis

Une alerte runtime se déclenche dans un Pod qui détient un secret d’API et peut joindre une base.

**Correction :** identifiez l’image, le digest, le Pod, le nœud, les permissions et les flux ; appliquez le confinement prévu, révoquez ou faites tourner le secret selon le risque, préservez les preuves utiles et recherchez les déploiements de la même image. Reconstruisez depuis une source approuvée et corrigez la cause racine avant clôture.

## 17. Défi final corrigé — sécuriser la chaîne Atlas Formation

### Situation

Le pipeline Atlas Formation construit et publie une image d’API. L’image utilise une base ancienne, exécute l’application en root et inclut un secret dans un fichier de configuration. Dans Kubernetes, le Pod utilise le ServiceAccount default, a un système de fichiers inscriptible et aucune limite de ressources. Le namespace dispose de permissions larges et de communications réseau non restreintes.

### Travail demandé

1. Identifier les frontières et les actifs en danger.
2. Définir une chaîne de build, de scan, de signature et d’admission.
3. Corriger le Dockerfile et les paramètres du Pod.
4. Définir les permissions Kubernetes et les flux réseau nécessaires.
5. Proposer des preuves et une procédure de réponse si l’image avait déjà été exécutée.

### Correction détaillée

**1. Actifs et frontières.** Les secrets, données de la base, identifiants cloud, registre, API Kubernetes, nœuds et pipeline sont des actifs. Les frontières incluent dépôt vers build, build vers registre, registre vers admission, Pod vers nœud, API vers base et workload vers secrets. Le pipeline et le Pod représentent des identités différentes qui ne doivent pas partager leurs privilèges.

**2. Chaîne d’approvisionnement.** Corrigez la dépendance et utilisez une base maintenue. Construisez de façon reproductible, scannez le code et l’image, générez une SBOM, attachez une provenance et une signature selon la politique. Publiez un digest approuvé dans le registre et vérifiez sa conformité dans le pipeline puis à l’admission.

**3. Image et Pod.** Retirez le secret des fichiers, révoquez-le si l’image a été publiée, puis injectez la nouvelle valeur à l’exécution. Construisez une image finale minimale, définissez un utilisateur non-root et évitez les capacités et montages dangereux. Dans le Pod, activez runAsNonRoot, allowPrivilegeEscalation false, privileged false, drop ALL, seccomp RuntimeDefault, readOnlyRootFilesystem lorsque possible et des ressources adaptées. Utilisez un ServiceAccount dédié.

**4. RBAC et réseau.** Créez un rôle de déploiement limité à l’application et au namespace. Le ServiceAccount de l’API n’obtient que les permissions nécessaires, ou aucun jeton s’il n’a pas besoin de l’API. Établissez les NetworkPolicies pour autoriser l’entrée depuis l’ingress prévu, les communications frontend vers API, API vers base et DNS requis. Refusez les chemins directs non nécessaires et vérifiez que le CNI applique les règles.

**5. Preuves et incident.** Prouvez que l’image active est le digest approuvé, que les tests de sécurité passent, que les Secrets ne sont pas accessibles à d’autres workloads et que les flux interdits échouent. Si l’ancienne image a tourné, examinez les journaux d’audit, les accès aux secrets, les communications et les versions déployées. Révoquez le secret exposé et surveillez les usages après rotation. Clôturez seulement après avoir remplacé tous les Pods concernés, documenté la cause racine et ajouté des contrôles anti-récidive.

~~~text
Phase 1 : contenir le secret exposé et évaluer le risque
Phase 2 : reconstruire une image minimale, corrigée et non-root
Phase 3 : scan + SBOM + provenance / signature
Phase 4 : admission et politique Pod cohérentes
Phase 5 : RBAC minimal + identité de workload dédiée
Phase 6 : NetworkPolicy + limites + journaux
Phase 7 : vérifier les digests actifs et clôturer les preuves
~~~

### Grille de notation suggérée

~~~text
Analyse de menace et chaîne d'approvisionnement       20 points
Dockerfile, runtime et privilèges                     20 points
Kubernetes RBAC, identité et admission               25 points
Réseau, ressources, secrets et journalisation         20 points
Réponse à incident et preuves                         15 points
Total                                                100 points
Seuil recommandé de validation                        80 points
~~~

Une réponse limitée à installer un scanner ne suffit pas. Les contrôles doivent empêcher les configurations à risque, limiter les permissions, protéger les secrets et prouver que l’image et le manifeste effectivement exécutés respectent la politique.

## 18. Checklist de production Docker/Kubernetes

- [ ] Les images proviennent de sources approuvées, maintenues et identifiées par version ou digest.
- [ ] Les builds sont reproductibles et les artefacts critiques disposent d’une provenance vérifiable.
- [ ] Les images sont scannées, les résultats triés et les exceptions suivies.
- [ ] Les images de production contiennent uniquement les composants d’exécution nécessaires.
- [ ] Les secrets ne figurent ni dans les couches d’image ni dans les journaux et artefacts.
- [ ] Les conteneurs fonctionnent en non-root lorsque possible.
- [ ] Le mode privilégié, les capacités supplémentaires et les montages hôte sont interdits sauf justification approuvée.
- [ ] Le socket du daemon n’est pas accessible aux applications ordinaires.
- [ ] Rootless est évalué pour les workloads compatibles.
- [ ] Les systèmes de fichiers sont en lecture seule lorsque possible et les volumes sont ciblés.
- [ ] Les ressources CPU, mémoire et quotas sont adaptés.
- [ ] Le cluster, l’API, le kubelet et le datastore sont protégés et non exposés inutilement.
- [ ] Les droits RBAC sont limités par principal, ressource, verbes et namespace.
- [ ] Les ServiceAccounts sont spécifiques et les jetons inutiles ne sont pas montés.
- [ ] Les Pod Security Standards sont appliqués selon le niveau de risque.
- [ ] Les capacités, seccomp et mécanismes de confinement sont configurés et testés.
- [ ] Les secrets sont chiffrés selon la configuration et accessibles uniquement aux workloads nécessaires.
- [ ] Les NetworkPolicies contrôlent effectivement l’entrée et la sortie avec un CNI compatible.
- [ ] Les endpoints publics, LoadBalancer, Ingress et accès de gestion sont documentés et protégés.
- [ ] Les événements d’audit, runtime et réseau sont centralisés et protégés.
- [ ] L’admission vérifie les règles critiques et son comportement en panne est testé.
- [ ] Les procédures de révocation, remplacement d’image, confinement et récupération ont été exercées.
- [ ] Les écarts ont un propriétaire, des mesures compensatoires et une date de réévaluation.

## 19. Glossaire

**Image :** artefact en couches qui sert de modèle de système de fichiers et de lancement.  
**Conteneur :** instance en exécution d’une image, avec une configuration de ressources et d’isolation.  
**Daemon Docker :** service de gestion des conteneurs et des opérations du moteur.  
**Runtime :** composant qui crée et exécute les conteneurs selon la plateforme.  
**Namespace Linux :** mécanisme d’isolation de vues de certaines ressources.  
**Cgroup :** mécanisme de comptabilité et de limitation des ressources.  
**Capacité Linux :** privilège précis qui peut être accordé à un processus.  
**Rootless :** mode d’exécution où le daemon et les conteneurs fonctionnent sans privilèges root de l’hôte, selon les contraintes du système.  
**Digest :** identifiant cryptographique qui référence un contenu d’image précis.  
**SBOM :** inventaire des composants logiciels associés à un artefact.  
**Provenance :** éléments attestant comment et à partir de quoi un artefact a été produit.  
**Pod :** unité de déploiement Kubernetes contenant un ou plusieurs conteneurs partageant certains contextes.  
**Namespace Kubernetes :** périmètre logique d’organisation et de politique dans un cluster.  
**RBAC :** autorisation basée sur les rôles et la portée.  
**ServiceAccount :** identité Kubernetes destinée aux workloads ou à des processus du cluster.  
**Pod Security Standards :** niveaux de règles qui limitent les configurations de sécurité des Pods.  
**NetworkPolicy :** ressource qui décrit des règles de flux pour les Pods lorsqu’elle est appliquée par le réseau du cluster.  
**CNI :** interface et plugins qui configurent le réseau des conteneurs et Pods.  
**Admission controller :** composant qui valide ou modifie des objets avant leur acceptation par l’API.  
**RuntimeClass :** sélection d’un environnement d’exécution spécifique pour des Pods compatibles.  
**Break-glass :** mécanisme d’accès exceptionnel d’urgence, contrôlé et journalisé.  
**Drift :** divergence entre l’état attendu et l’état réel d’une image ou ressource.

## 20. Références officielles

- Docker Engine security : https://docs.docker.com/engine/security/
- Docker Rootless mode : https://docs.docker.com/engine/security/rootless/
- Docker Build best practices : https://docs.docker.com/build/building/best-practices/
- Docker build secrets : https://docs.docker.com/build/building/secrets/
- Kubernetes Security Checklist : https://kubernetes.io/docs/concepts/security/security-checklist/
- Kubernetes Application Security Checklist : https://kubernetes.io/docs/concepts/security/application-security-checklist/
- Kubernetes Pod Security Standards : https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Kubernetes RBAC good practices : https://kubernetes.io/docs/concepts/security/rbac-good-practices/
- Kubernetes Network Policies : https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Kubernetes Secrets : https://kubernetes.io/docs/concepts/configuration/secret/
- NIST SP 800-190, *Application Container Security Guide* : https://csrc.nist.gov/pubs/sp/800/190/final
- OWASP Docker Security Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- Kubernetes Audit Logging : https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/

Les fonctionnalités et paramètres varient selon la distribution Kubernetes, le plugin réseau, le runtime et l’offre managée. Vérifiez les capacités effectives, en particulier l’application des NetworkPolicies, le chiffrement des Secrets au repos, la couverture des journaux et les politiques d’admission. Reliez chaque contrôle à un test reproductible et à un propriétaire.

Fin du cours.