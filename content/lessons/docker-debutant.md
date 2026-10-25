# Docker : images et conteneurs

## 1. Présentation du cours

Docker est une plateforme qui permet de construire, distribuer et exécuter des applications dans des conteneurs. Ces conteneurs fournissent un environnement isolé dans lequel une application peut fonctionner avec ses dépendances, ses fichiers et sa configuration, sans devoir installer l'ensemble de ces éléments directement sur le système principal.

Docker est utilisé dans le développement logiciel, l'administration système, l'automatisation, le cloud, les laboratoires réseau et les pipelines CI/CD.

Il permet notamment de résoudre un problème fréquent : une application fonctionne correctement sur l'ordinateur de son développeur, mais échoue sur le serveur parce que les versions des logiciels, les bibliothèques ou la configuration sont différentes.

Avec Docker, l'environnement d'exécution peut être décrit et construit de manière reproductible à partir d'une image.

Ce cours présente les fondations indispensables : images, conteneurs, commandes Docker, Dockerfile, construction d'images, ports, stockage, réseaux, diagnostic et bonnes pratiques de sécurité.

L'objectif est de comprendre ce qui se passe réellement lorsqu'une image est construite, qu'un conteneur démarre, qu'une application s'arrête ou qu'un fichier est modifié à l'intérieur d'un conteneur.

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez être capable de :

- Expliquer le rôle de Docker et ses principaux composants.
- Distinguer une image Docker d'un conteneur.
- Comprendre la différence entre un conteneur et une machine virtuelle.
- Installer Docker ou vérifier son installation.
- Télécharger et examiner une image.
- Créer, démarrer, arrêter et supprimer des conteneurs.
- Consulter les journaux et examiner les processus d'un conteneur.
- Construire une image à partir d'un Dockerfile.
- Comprendre les instructions `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `EXPOSE`, `USER` et `CMD`.
- Utiliser les tags pour identifier des versions d'images.
- Publier un port pour accéder à une application conteneurisée.
- Comprendre les limites du stockage interne d'un conteneur.
- Utiliser un volume ou un montage de répertoire.
- Identifier les erreurs les plus courantes lors de la construction et de l'exécution d'une image.
- Appliquer des règles élémentaires de sécurité.
- Construire et exécuter une petite application Python dans Docker.

### 1.2. Prérequis

Aucune expérience préalable de Docker n'est nécessaire.

Il est cependant recommandé de savoir :

- Naviguer dans les répertoires.
- Créer et modifier des fichiers texte.
- Exécuter des commandes dans un terminal.
- Comprendre les notions élémentaires d'application, de processus, de port réseau et de système d'exploitation.

Les commandes seront principalement présentées sous une forme commune à Linux, macOS, Git Bash et PowerShell, avec des indications lorsque le comportement dépend du terminal.

### 1.3. Les notions à distinguer dès le départ

Docker repose sur plusieurs éléments différents.

| Élément | Rôle |
|---|---|
| Docker CLI | Programme qui reçoit les commandes saisies dans le terminal. |
| Docker Engine | Ensemble de composants qui construit et exécute les conteneurs. |
| Docker daemon | Service qui gère notamment les images, conteneurs, réseaux et volumes. |
| Image | Modèle contenant les fichiers et paramètres nécessaires à la création d'un conteneur. |
| Conteneur | Instance exécutable créée à partir d'une image. |
| Dockerfile | Fichier décrivant les étapes de construction d'une image. |
| Registre d'images | Service permettant de stocker et de distribuer des images. |
| Volume | Mécanisme de stockage persistant géré par Docker. |
| Réseau Docker | Mécanisme de communication entre les conteneurs et les autres systèmes. |

Ces éléments sont complémentaires, mais ils ne sont pas interchangeables.

## 2. Pourquoi utiliser Docker ?

### 2.1. Le problème des environnements différents

Imaginons qu'un développeur crée une application Python sur son ordinateur.

Son environnement contient :

- Python 3.12.
- Une bibliothèque installée dans une certaine version.
- Des variables d'environnement spécifiques.
- Des fichiers de configuration locaux.
- Des paramètres du système.

Le serveur de production possède une autre version de Python et une bibliothèque différente. L'application peut échouer, même si le code source n'a pas changé.

Le problème ne vient pas nécessairement du programme lui-même. Il peut venir de la différence entre les environnements.

Représentation :

```text
ORDINATEUR DU DÉVELOPPEUR
+--------------------------------+
| Application                    |
| Python 3.12                     |
| Dépendance version A            |
| Configuration locale            |
+--------------------------------+
                |
                | Le même code
                v
SERVEUR
+--------------------------------+
| Application                    |
| Python 3.10                     |
| Dépendance version B            |
| Configuration différente       |
+--------------------------------+
                |
                v
       Erreur possible
```

L'objectif est d'obtenir un environnement d'exécution suffisamment cohérent pour limiter ces différences.

### 2.2. La solution Docker

Docker permet de construire une image contenant les éléments nécessaires à l'exécution de l'application.

Cette image peut ensuite servir à créer des conteneurs sur différents systèmes compatibles.

```text
                 CODE SOURCE
                      |
                      v
              +---------------+
              |  Dockerfile   |
              +---------------+
                      |
                      v
              +---------------+
              | Construction  |
              | de l'image    |
              +---------------+
                      |
                      v
              +---------------+
              | Image Docker  |
              +---------------+
                 /         \
                v           v
        +-------------+ +-------------+
        | Conteneur A | | Conteneur B |
        | Test        | | Exécution   |
        +-------------+ +-------------+
```

Les deux conteneurs peuvent être créés à partir de la même image, avec des configurations d'exécution différentes si nécessaire.

Cette reproductibilité n'est toutefois pas absolue : le résultat peut encore dépendre de l'architecture processeur, du noyau, des volumes montés, du réseau, des secrets, des services externes et de la configuration fournie au lancement.

Docker réduit les différences d'environnement ; il ne supprime pas toutes les différences possibles.

### 2.3. Les avantages de Docker

Docker facilite :

**La portabilité.** Une image peut être distribuée à d'autres machines disposant d'un environnement Docker compatible.

**La reproductibilité.** Le Dockerfile décrit les étapes de construction et permet de reconstruire l'image selon une procédure explicite.

**L'isolation.** Les processus des conteneurs disposent de mécanismes d'isolation qui limitent leur accès aux ressources du système et aux autres processus, selon la configuration.

**L'automatisation.** Les images peuvent être construites et testées dans des pipelines CI/CD.

**La rapidité de déploiement.** Il est souvent plus simple de lancer un conteneur à partir d'une image prête que de réinstaller manuellement toutes les dépendances.

**La cohérence des environnements.** Les équipes peuvent utiliser une image commune pour le développement, les tests et la livraison.

**La facilité de remplacement.** Un conteneur défectueux peut généralement être recréé à partir de son image et de sa configuration, sans modifier le modèle de base.

### 2.4. Ce que Docker ne garantit pas

Docker ne garantit pas automatiquement :

- Que le code applicatif fonctionne correctement.
- Que l'application est sécurisée.
- Que les données persistent après la suppression d'un conteneur.
- Que l'image contient des versions de logiciels à jour.
- Que le conteneur dispose de suffisamment de mémoire.
- Que le service est accessible depuis le réseau.
- Que l'application peut être déployée sans interruption.
- Que plusieurs conteneurs forment automatiquement une architecture complète.

Il faut toujours définir les tests, la configuration, le stockage, la sécurité, la supervision et les procédures de récupération appropriés.

## 3. Comprendre le fonctionnement de Docker

### 3.1. Docker CLI

La CLI, ou interface en ligne de commande, est le programme utilisé pour envoyer des instructions à Docker.

Exemple :

```bash
docker ps
```

Cette commande demande à Docker d'afficher les conteneurs en cours d'exécution.

Autres exemples :

```bash
docker images
docker pull nginx
docker run nginx
docker logs mon-conteneur
```

La CLI n'est pas le conteneur et n'est pas non plus l'application qui tourne dans le conteneur.

### 3.2. Docker daemon

Le daemon Docker, généralement appelé `dockerd` sur un système Linux utilisant Docker Engine, gère les opérations réalisées par le moteur Docker.

Il intervient notamment pour :

- Télécharger des images.
- Construire des images.
- Créer des conteneurs.
- Démarrer et arrêter des conteneurs.
- Gérer les réseaux.
- Gérer les volumes.
- Communiquer avec les composants d'exécution.

La CLI envoie les requêtes à l'API Docker, généralement via un socket local ou un endpoint configuré.

Schéma :

```text
+-----------------------+
| Utilisateur           |
| Terminal              |
+-----------------------+
            |
            v
+-----------------------+
| Docker CLI            |
| docker run ...        |
+-----------------------+
            |
            v
+-----------------------+
| API Docker            |
+-----------------------+
            |
            v
+-----------------------+
| Docker daemon         |
| Gestion des ressources|
+-----------------------+
      /      |      \
     v       v       v
  Images  Conteneurs Réseaux
                    |
                    v
                  Volumes
```

Sur Docker Desktop, une partie de l'environnement Docker peut fonctionner dans une machine virtuelle ou un environnement Linux intégré. L'architecture exacte dépend du système et du backend utilisé.

### 3.3. Le registre d'images

Un registre est un service qui permet de stocker et de distribuer des images Docker.

Docker Hub est un registre largement utilisé.

D'autres possibilités existent :

- GitHub Container Registry.
- GitLab Container Registry.
- Amazon Elastic Container Registry.
- Azure Container Registry.
- Google Artifact Registry.
- Un registre privé géré par une organisation.

Le flux habituel est le suivant :

```text
Construire une image
        |
        v
Tester l'image
        |
        v
Taguer l'image
        |
        v
Envoyer vers un registre
        |
        v
Télécharger sur un autre système
        |
        v
Créer un conteneur
```

Une image locale peut être utilisée sans être publiée dans un registre.

### 3.4. Docker Engine et Docker Desktop

Docker Engine constitue le moteur de conteneurs habituellement utilisé sur les serveurs Linux.

Docker Desktop propose une expérience intégrée pour les postes de travail et peut inclure une interface graphique, la CLI, le moteur Docker et des outils complémentaires.

Sur Windows, Docker Desktop utilise généralement un backend adapté à l'exécution de conteneurs Linux, par exemple WSL 2.

Sur macOS, l'environnement d'exécution repose également sur une couche de virtualisation.

Il ne faut donc pas supposer qu'un conteneur Linux utilise directement le noyau Windows ou macOS : le conteneur Linux partage généralement le noyau Linux de son environnement d'exécution.

## 4. Conteneur ou machine virtuelle ?

Docker et les machines virtuelles répondent à des besoins qui se recoupent, mais leur fonctionnement est différent.

### 4.1. Machine virtuelle

Une machine virtuelle utilise un hyperviseur et exécute généralement son propre système d'exploitation invité avec son noyau.

Chaque machine virtuelle peut contenir :

- Un système d'exploitation complet.
- Des bibliothèques.
- Des services système.
- Une ou plusieurs applications.

Exemple :

```text
+--------------------------------+
| Serveur physique               |
|                                |
| +----------------------------+ |
| | Hyperviseur                | |
| +----------------------------+ |
|             |                  |
|      +------+-------+          |
|      v              v          |
| +----------+  +----------+      |
| | VM 1     |  | VM 2     |      |
| | OS invité|  | OS invité|      |
| | App A    |  | App B    |      |
| +----------+  +----------+      |
+--------------------------------+
```

### 4.2. Conteneurs

Les conteneurs sont des processus isolés qui utilisent les mécanismes d'isolation du système d'exploitation sous-jacent.

Les conteneurs Linux partagent le même noyau Linux que leur environnement d'exécution.

```text
+--------------------------------+
| Serveur ou environnement hôte  |
|                                |
| Noyau Linux                    |
|                                |
| +------------+ +------------+  |
| | Conteneur A| | Conteneur B|  |
| | App A      | | App B      |  |
| | Dépendances| | Dépendances|  |
| +------------+ +------------+  |
+--------------------------------+
```

Chaque conteneur possède notamment sa propre vue isolée du système de fichiers et des processus, ainsi qu'une configuration réseau qui peut être différente de celle des autres conteneurs.

L'isolation exacte dépend des mécanismes utilisés et des permissions accordées.

### 4.3. Tableau comparatif

| Critère | Conteneur | Machine virtuelle |
|---|---|---|
| Noyau | Partagé entre les processus de conteneurs utilisant le même noyau hôte | Généralement un noyau par système invité |
| Démarrage | Généralement rapide | Généralement plus long |
| Empreinte | Souvent plus faible | Souvent plus importante |
| Isolation | Isolation au niveau des processus et des ressources du système | Frontière d'isolation de la machine virtuelle |
| Portabilité | Dépend de l'image, de la plateforme et de l'environnement d'exécution | Dépend de l'hyperviseur, des formats et du système invité |
| Usage courant | Applications, services, tests et traitements isolés | Systèmes complets, noyaux différents, environnements fortement séparés |

Il ne faut pas considérer les conteneurs comme une simple substitution universelle aux machines virtuelles.

Les deux technologies sont souvent utilisées ensemble : les conteneurs peuvent fonctionner à l'intérieur de machines virtuelles pour combiner isolation de l'infrastructure et déploiement applicatif léger.

### 4.4. Docker ne virtualise pas automatiquement tout un système d'exploitation

Une image Linux peut contenir de nombreux fichiers système, des bibliothèques et des exécutables. Cela ne signifie pas qu'elle inclut un noyau Linux indépendant.

C'est une distinction fondamentale pour comprendre pourquoi une image de conteneur Linux n'est pas directement équivalente à une machine virtuelle Linux.

## 5. Comprendre une image Docker

### 5.1. Définition

Une image Docker est un modèle immuable utilisé pour créer des conteneurs.

Elle contient les fichiers, bibliothèques, exécutables et métadonnées nécessaires à l'exécution d'un processus dans l'environnement prévu.

Par exemple, une image Python peut inclure :

- Des fichiers système nécessaires.
- L'interpréteur Python.
- Les bibliothèques installées.
- Le code de l'application.
- Des métadonnées concernant la commande à lancer.

Une image ne correspond pas à un processus en cours d'exécution. Elle représente ce qui sera utilisé lors de la création du conteneur.

### 5.2. Une image peut créer plusieurs conteneurs

Supposons que vous possédiez une image nommée `mon-api:1.0`.

Vous pouvez créer plusieurs conteneurs à partir de cette même image :

```text
             IMAGE mon-api:1.0
                    |
          +---------+---------+
          |         |         |
          v         v         v
     Conteneur A Conteneur B Conteneur C
       Tests      Démo       Traitement
```

Chaque conteneur possède son propre état d'exécution et sa propre couche inscriptible.

Une modification apportée à la couche inscriptible d'un conteneur ne modifie pas automatiquement l'image à partir de laquelle il a été créé.

### 5.3. Les images sont composées de couches

Les images Docker utilisent des couches qui représentent des changements successifs du système de fichiers.

Exemple conceptuel :

```text
+--------------------------------------+
| Couche application                   |
| app.py, fichiers applicatifs         |
+--------------------------------------+
| Couche dépendances                   |
| Bibliothèques installées             |
+--------------------------------------+
| Couche environnement Python          |
| Interpréteur et fichiers associés    |
+--------------------------------------+
| Couche de base                       |
| Système de fichiers de référence     |
+--------------------------------------+
```

Les couches peuvent être réutilisées entre plusieurs images lorsqu'elles correspondent aux mêmes contenus.

Cela permet de réduire les téléchargements répétitifs et de bénéficier du cache de construction.

Le nombre et le contenu des couches réels dépendent du Dockerfile et du résultat de la construction.

### 5.4. Pourquoi les images sont-elles dites immuables ?

Une image déjà construite ne se transforme pas lorsqu'un conteneur modifie un fichier dans sa couche inscriptible.

Si vous modifiez le code source ou le Dockerfile, vous devez généralement reconstruire une nouvelle image pour intégrer ces changements.

Le tag d'une image peut être réaffecté à une nouvelle image lors d'une construction ou d'une publication. Il ne faut donc pas confondre le nom mutable d'un tag et l'identité du contenu sous-jacent.

### 5.5. Image, tag et identifiant

Exemple :

```text
mon-api:1.0
```

Cette référence se compose de :

- `mon-api` : nom du dépôt d'image.
- `1.0` : tag identifiant une version logique de l'image.

Un identifiant d'image permet d'identifier un objet image sur le moteur local.

On peut afficher les images disponibles avec :

```bash
docker image ls
```

Exemple de sortie simplifiée :

```text
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
mon-api      1.0       abc123def456   2 minutes ago  120MB
python       3.12-slim def456abc123   1 week ago     130MB
```

Les valeurs et les tailles sont illustratives.

### 5.6. Le tag `latest`

Si vous exécutez :

```bash
docker pull nginx
```

Docker utilise normalement le tag `latest` lorsque aucun tag n'est précisé.

Cependant, `latest` ne signifie pas automatiquement « dernière version stable vérifiée par mon organisation ». Il s'agit d'un tag dont l'affectation dépend du registre et de l'image concernée.

Pour un projet reproductible, il est préférable de choisir une version explicite adaptée au besoin.

Exemple :

```bash
docker pull nginx:alpine
```

Pour une livraison nécessitant une identification stricte du contenu, un digest peut être utilisé.

Exemple de forme :

```text
nginx@sha256:IDENTIFIANT_COMPLET
```

Le digest doit être obtenu depuis une source fiable. Il ne faut pas inventer ni réutiliser un digest sans vérifier l'image correspondante.

## 6. Télécharger et examiner une image

### 6.1. Télécharger une image

Utilisez une image connue provenant d'une source fiable.

Exemple :

```bash
docker pull nginx:alpine
```

Docker recherche l'image dans le registre configuré, la télécharge si nécessaire et la rend disponible dans le moteur local.

Cette commande ne lance pas de serveur web.

Elle prépare uniquement l'image pour une utilisation ultérieure.

### 6.2. Afficher les images locales

```bash
docker image ls
```

Autre forme courante :

```bash
docker images
```

Ces deux commandes affichent les images locales selon les options employées.

### 6.3. Inspecter une image

```bash
docker image inspect nginx:alpine
```

Cette commande retourne des informations détaillées, notamment :

- L'identité de l'image.
- Les tags connus.
- Des métadonnées.
- L'architecture.
- Les paramètres d'exécution par défaut.
- Les couches et les informations de construction disponibles.

Pour une sortie plus lisible, certains champs peuvent être extraits avec `--format`, mais les propriétés exactes dépendent de l'objet inspecté.

### 6.4. Examiner les couches d'une image

```bash
docker image history nginx:alpine
```

Cette commande affiche l'historique de construction visible de l'image.

Elle peut aider à comprendre les différentes étapes qui ont contribué à la création de l'image.

L'historique ne révèle pas nécessairement tous les détails de provenance ou toutes les informations de sécurité. Il faut utiliser les outils adaptés lorsque l'on doit vérifier la provenance complète d'une image.

### 6.5. Télécharger plusieurs tags

Vous pouvez utiliser plusieurs versions d'une image dans un laboratoire.

Exemples :

```bash
docker pull python:3.12-slim
docker pull nginx:alpine
docker pull alpine:3.22
```

Les tags doivent être vérifiés avant d'être employés dans un projet réel. La disponibilité, le support et le contenu des images évoluent.

### 6.6. Supprimer une image

```bash
docker image rm mon-api:1.0
```

Cette commande supprime une référence ou une image locale si les conditions le permettent.

Docker peut refuser la suppression si l'image est utilisée par des conteneurs existants.

Ne supprimez pas aveuglément les images d'un serveur : certaines peuvent être nécessaires pour des déploiements ou des redémarrages.

## 7. Comprendre les conteneurs

### 7.1. Définition

Un conteneur est une instance créée à partir d'une image.

Il possède notamment :

- Un identifiant.
- Un nom.
- Une configuration d'exécution.
- Un état.
- Une couche inscriptible.
- Des éventuels montages de stockage.
- Une configuration réseau.
- Un processus principal.

Un conteneur n'est pas simplement un fichier ou un dossier. C'est un objet géré par le moteur Docker, avec un cycle de vie.

### 7.2. Les états courants d'un conteneur

Un conteneur peut être :

- Créé, mais pas encore démarré.
- En cours d'exécution.
- Arrêté.
- En cours de redémarrage selon la configuration.
- En pause dans certaines situations.
- Supprimé.

La terminologie et les informations exactes dépendent des commandes et de l'état du moteur.

### 7.3. Un conteneur peut s'arrêter normalement

Un conteneur exécute un processus principal.

Lorsque ce processus termine, le conteneur passe généralement à l'état arrêté.

Par exemple :

```bash
docker run alpine:3.22 echo "Bonjour Docker"
```

Le conteneur démarre, exécute la commande `echo`, affiche le texte puis s'arrête.

Il ne s'agit pas d'une erreur.

Docker n'est pas obligé de conserver chaque conteneur en fonctionnement après la fin de son processus principal.

### 7.4. Créer et lancer un conteneur

Commande :

```bash
docker run nginx:alpine
```

Docker prépare un conteneur à partir de l'image demandée et le lance.

Dans cet exemple, le serveur web fonctionne normalement au premier plan dans le terminal. Le port du conteneur n'est cependant pas automatiquement publié sur le port hôte.

Il faut distinguer deux opérations :

- Créer et exécuter le conteneur.
- Rendre son service accessible depuis l'extérieur du conteneur.

### 7.5. Lancer en arrière-plan

```bash
docker run -d --name mon-nginx nginx:alpine
```

Explications :

- `docker run` crée et lance un conteneur.
- `-d` le fait fonctionner en arrière-plan.
- `--name mon-nginx` donne un nom explicite au conteneur.
- `nginx:alpine` désigne l'image utilisée.

Le nom est utile pour les commandes de suivi, de diagnostic et d'arrêt.

### 7.6. Lister les conteneurs en cours d'exécution

```bash
docker ps
```

Cette commande affiche normalement les conteneurs actifs.

Pour afficher aussi les conteneurs arrêtés :

```bash
docker ps -a
```

La différence est essentielle : un conteneur arrêté peut toujours exister et conserver sa couche inscriptible.

### 7.7. Lire l'état et les métadonnées

```bash
docker inspect mon-nginx
```

Cette commande retourne des informations détaillées sur le conteneur.

Pour afficher uniquement l'état courant :

```bash
docker inspect --format '{{.State.Status}}' mon-nginx
```

Sous les shells usuels, les guillemets simples de cet exemple permettent de préserver le modèle de formatage. Les règles de citation peuvent différer dans certains terminaux.

## 8. Créer un premier conteneur interactif

### 8.1. Utiliser une image légère

L'image Alpine Linux est couramment utilisée pour des exemples simples.

Lancez :

```bash
docker run --rm -it alpine:3.22 sh
```

Explication :

- `--rm` demande la suppression automatique du conteneur lorsqu'il se termine.
- `-i` garde l'entrée standard ouverte.
- `-t` crée un terminal virtuel.
- `alpine:3.22` désigne l'image.
- `sh` lance un shell dans le conteneur.

Vous obtenez un terminal fonctionnant dans l'environnement du conteneur.

### 8.2. Exécuter quelques commandes

Dans le conteneur :

```sh
cat /etc/os-release
```

Cette commande affiche des informations sur l'environnement Linux de l'image.

Consultez les processus visibles :

```sh
ps
```

Le résultat varie selon l'image et les outils installés.

Créez un fichier temporaire :

```sh
echo "Fichier du conteneur" > /tmp/message.txt
cat /tmp/message.txt
```

Vous pouvez ensuite quitter le shell :

```sh
exit
```

Le conteneur s'arrête et l'option `--rm` demande sa suppression automatique.

### 8.3. Pourquoi le conteneur disparaît-il ?

Le conteneur a été lancé avec `--rm`.

Cette option supprime le conteneur lorsque son processus se termine, au lieu de conserver un conteneur arrêté.

Cette suppression ne supprime pas automatiquement les images utilisées ni les volumes nommés indépendants du conteneur.

### 8.4. Sans `--rm`

Exécutez :

```bash
docker run -it --name labo-alpine alpine:3.22 sh
```

Dans le conteneur :

```sh
echo "Essai de persistance" > /tmp/labo.txt
exit
```

Puis, dans le terminal hôte :

```bash
docker ps -a
```

Le conteneur `labo-alpine` doit rester visible dans la liste, à l'état arrêté.

Vous pouvez vérifier cet état, puis redémarrer le conteneur :

```bash
docker start -ai labo-alpine
```

La commande démarre le conteneur et rattache le terminal au processus prévu par sa configuration, avec les options d'interaction demandées.

Vérifiez ensuite le fichier :

```sh
cat /tmp/labo.txt
```

Dans ce scénario, le fichier peut encore être présent parce que la couche inscriptible du conteneur existe toujours.

Cela ne signifie pas qu'il constitue un stockage persistant fiable : si le conteneur est supprimé, sa couche inscriptible est supprimée avec lui.

Pour nettoyer le laboratoire :

```bash
exit
docker rm labo-alpine
```

Si le conteneur est encore en cours d'exécution, arrêtez-le avant de le supprimer, ou utilisez les options adaptées à votre intention.

## 9. Les commandes essentielles pour gérer les conteneurs

### 9.1. Démarrer un conteneur existant

```bash
docker start mon-nginx
```

Cette commande démarre un conteneur déjà créé.

Elle ne crée pas un nouveau conteneur à partir d'une image.

### 9.2. Arrêter un conteneur

```bash
docker stop mon-nginx
```

Docker demande normalement au processus principal de s'arrêter proprement, puis peut le terminer de force si le délai prévu expire.

L'arrêt est préférable à une terminaison immédiate lorsqu'une application doit fermer des fichiers, terminer une transaction ou libérer des ressources correctement.

### 9.3. Redémarrer un conteneur

```bash
docker restart mon-nginx
```

Cette commande arrête puis redémarre le conteneur.

Un redémarrage ne reconstruit pas l'image et n'efface pas automatiquement la couche inscriptible.

### 9.4. Consulter les journaux

```bash
docker logs mon-nginx
```

Pour suivre les nouveaux messages :

```bash
docker logs -f mon-nginx
```

Pour n'afficher que les dernières lignes :

```bash
docker logs --tail 100 mon-nginx
```

Pour ajouter les horodatages :

```bash
docker logs -t mon-nginx
```

Les journaux disponibles dépendent de l'application et de la configuration du pilote de journalisation. Il faut que le programme produise des messages exploitables pour que cette commande soit utile.

### 9.5. Exécuter une commande dans un conteneur actif

```bash
docker exec -it mon-nginx sh
```

Cette commande démarre un processus supplémentaire dans un conteneur déjà en cours d'exécution.

Si l'image contient Bash, vous pouvez utiliser :

```bash
docker exec -it mon-conteneur bash
```

Mais toutes les images ne possèdent pas Bash. Une image minimale peut uniquement fournir `sh` ou ne contenir aucun shell.

### 9.6. Examiner les processus

```bash
docker top mon-nginx
```

Cette commande permet d'examiner les processus associés au conteneur.

Elle est utile lorsqu'un conteneur démarre puis s'arrête, lorsqu'une application semble bloquée ou lorsqu'un comportement inattendu doit être diagnostiqué.

### 9.7. Afficher les ressources utilisées

```bash
docker stats
```

Cette commande affiche des statistiques d'utilisation des ressources pour les conteneurs actifs.

Vous pouvez consulter notamment la consommation de CPU, de mémoire et certaines statistiques de réseau et de stockage.

Une consommation élevée ne signifie pas automatiquement qu'il faut supprimer le conteneur. Il faut examiner l'application, ses limites de ressources et sa charge réelle.

### 9.8. Supprimer un conteneur

Un conteneur arrêté peut être supprimé avec :

```bash
docker rm mon-nginx
```

S'il fonctionne encore, arrêtez-le d'abord :

```bash
docker stop mon-nginx
docker rm mon-nginx
```

Un conteneur supprimé n'est plus disponible sous son ancien nom ou identifiant comme objet géré.

### 9.9. Tableau récapitulatif

| Commande | Rôle |
|---|---|
| `docker run` | Créer et lancer un conteneur. |
| `docker create` | Créer un conteneur sans le démarrer. |
| `docker ps` | Afficher les conteneurs actifs. |
| `docker ps -a` | Afficher les conteneurs actifs et arrêtés. |
| `docker start` | Démarrer un conteneur existant. |
| `docker stop` | Arrêter un conteneur. |
| `docker restart` | Redémarrer un conteneur. |
| `docker logs` | Consulter les journaux. |
| `docker exec` | Exécuter un processus supplémentaire dans un conteneur actif. |
| `docker inspect` | Examiner les métadonnées d'un objet Docker. |
| `docker top` | Examiner les processus du conteneur. |
| `docker stats` | Observer certaines ressources consommées. |
| `docker rm` | Supprimer un conteneur. |

## 10. Comprendre précisément `docker run`

La commande `docker run` combine plusieurs opérations.

Sa forme générale est :

```bash
docker run [OPTIONS] IMAGE[:TAG] [COMMAND] [ARG...]
```

Exemple :

```bash
docker run -d --name web-demo -p 127.0.0.1:8080:80 nginx:alpine
```

### 10.1. Décomposer la commande

| Élément | Signification |
|---|---|
| `docker run` | Crée et démarre un conteneur. |
| `-d` | Exécute le conteneur en arrière-plan. |
| `--name web-demo` | Définit son nom. |
| `-p 127.0.0.1:8080:80` | Publie le port 80 du conteneur sur le port 8080 de l'adresse locale de l'hôte. |
| `nginx:alpine` | Image source du conteneur. |

Lorsque le conteneur démarre avec succès, Docker affiche généralement un identifiant de conteneur.

### 10.2. Quelle est la différence entre `run` et `create` ?

`docker run` crée et démarre le conteneur.

`docker create` crée le conteneur sans démarrer son processus principal.

Exemple :

```bash
docker create --name web-en-attente nginx:alpine
```

Puis :

```bash
docker start web-en-attente
```

Le conteneur existe dès la commande `create`, même avant d'être démarré.

### 10.3. Donner un nom explicite

Si aucun nom n'est défini, Docker attribue normalement un nom généré.

Exemple :

```bash
docker run -d nginx:alpine
```

Le nom peut être moins facile à retenir qu'un nom défini :

```bash
docker run -d --name serveur-web nginx:alpine
```

Dans un laboratoire ou un environnement professionnel, un nom explicite facilite les diagnostics et les opérations de maintenance.

### 10.4. Option `--rm`

Pour un conteneur utilisé dans un test ponctuel :

```bash
docker run --rm alpine:3.22 echo "Test terminé"
```

Le conteneur est supprimé après la fin de son processus.

N'utilisez pas cette option sans comprendre ses conséquences si vous comptez conserver l'état du conteneur pour un diagnostic ultérieur.

### 10.5. Remplacer la commande par défaut

Une image peut définir un comportement de démarrage par défaut.

Il est possible de passer une autre commande :

```bash
docker run --rm alpine:3.22 uname -a
```

Cette commande utilise l'image Alpine pour exécuter `uname -a`, puis le conteneur s'arrête.

La commande remplace ici le comportement prévu par défaut pour ce lancement, selon la configuration de l'image.

## 11. Les ports et l'accès réseau

### 11.1. Pourquoi publier un port ?

Une application peut écouter sur un port à l'intérieur du conteneur sans être directement accessible depuis les autres machines.

Pour rendre le service accessible depuis l'hôte ou depuis des clients autorisés, Docker peut publier un port.

Considérons un serveur web écoutant sur le port 80 dans un conteneur.

```text
Navigateur sur l'hôte
        |
        v
127.0.0.1:8080
        |
        v
Mappage de port Docker
8080 ----> 80
        |
        v
+---------------------+
| Conteneur Nginx     |
| Serveur web : 80    |
+---------------------+
```

La syntaxe :

```bash
-p PORT_HOTE:PORT_CONTENEUR
```

permet de définir la correspondance.

### 11.2. Exemple Nginx

```bash
docker run -d \
  --name nginx-labo \
  -p 127.0.0.1:8080:80 \
  nginx:alpine
```

Cette commande utilise une syntaxe multi-ligne compatible avec les shells de type Unix.

Dans PowerShell, utilisez une seule ligne ou adaptez le caractère de continuation.

Ouvrez ensuite dans votre navigateur :

```text
http://127.0.0.1:8080
```

Vous devriez obtenir la page par défaut servie par Nginx si le conteneur fonctionne et si le port est disponible.

### 11.3. Les deux ports ont des rôles différents

Dans :

```bash
-p 127.0.0.1:8080:80
```

- `127.0.0.1` est l'adresse hôte sur laquelle le port sera publié.
- `8080` est le port de l'hôte.
- `80` est le port du conteneur.

Le service Nginx continue d'écouter sur le port 80 à l'intérieur de son environnement. Le navigateur utilise le port 8080 de l'hôte.

### 11.4. Pourquoi préciser `127.0.0.1` ?

Si vous utilisez :

```bash
-p 8080:80
```

Docker publie habituellement le port sur les interfaces hôte correspondantes, et pas uniquement sur la boucle locale.

Cela peut rendre le service accessible à d'autres systèmes selon le réseau et le pare-feu.

Pour un laboratoire local, la forme suivante limite normalement l'accès au système local :

```bash
-p 127.0.0.1:8080:80
```

La portée réelle de l'accès dépend également de l'environnement Docker, du routage et de la configuration du système.

### 11.5. Plusieurs conteneurs peuvent utiliser le même port interne

Deux conteneurs peuvent écouter chacun sur le port 80 à l'intérieur de leur environnement respectif.

Ils ne peuvent généralement pas publier simultanément le même couple adresse hôte et port hôte.

Exemple :

```bash
docker run -d --name site-a -p 127.0.0.1:8080:80 nginx:alpine
docker run -d --name site-b -p 127.0.0.1:8081:80 nginx:alpine
```

Les deux services utilisent le port 80 dans leurs conteneurs, mais sont accessibles localement via deux ports hôte différents.

### 11.6. Vérifier les ports publiés

```bash
docker ps
```

Vous pouvez également examiner les mappings d'un conteneur :

```bash
docker port site-a
```

Si l'application n'est pas accessible, vérifiez :

- Que le conteneur est actif.
- Que le port cible correspond à celui de l'application.
- Que le service écoute sur la bonne interface dans le conteneur.
- Que le port hôte n'est pas déjà occupé.
- Que les règles réseau et de pare-feu permettent l'accès attendu.

### 11.7. `EXPOSE` et `-p` ne sont pas équivalents

Dans un Dockerfile :

```dockerfile
EXPOSE 8000
```

cette instruction indique un port de l'application prévu pour la communication.

Elle ne publie pas automatiquement ce port sur l'hôte.

La publication se fait au démarrage, par exemple :

```bash
docker run -p 127.0.0.1:8080:8000 mon-api:1.0
```

Il s'agit de deux opérations distinctes : la documentation du port dans l'image et le mappage effectif sur l'hôte.

## 12. Les images officielles et les registres

### 12.1. Télécharger une image

Pour récupérer une image :

```bash
docker pull nginx:alpine
```

Docker télécharge les couches nécessaires si elles ne sont pas déjà disponibles localement.

### 12.2. Identifier la source d'une image

Une référence d'image peut comporter un registre et un espace de noms.

Exemple :

```text
docker.io/library/nginx:alpine
```

La référence plus courte :

```text
nginx:alpine
```

correspond habituellement à cette image officielle de Docker Hub.

Pour une image privée, la référence peut ressembler à :

```text
registry.example.com/equipe/mon-api:1.0
```

Il faut adapter le registre et le nom à la configuration réelle de l'organisation.

### 12.3. Se connecter à un registre privé

Lorsqu'une authentification est nécessaire :

```bash
docker login registry.example.com
```

Les modalités d'authentification dépendent du registre.

Ne placez pas un mot de passe ou un jeton d'accès en clair dans un Dockerfile, dans un fichier suivi par Git ou dans les commandes partagées avec l'équipe.

### 12.4. Les tags d'image

Une même image logique peut être associée à plusieurs tags.

Exemple :

```text
mon-api:1.0
mon-api:stable
```

Ces tags peuvent désigner le même identifiant d'image au moment où ils sont créés, mais ils peuvent être déplacés ultérieurement vers d'autres contenus.

Une convention de version doit donc être accompagnée d'une gestion fiable des publications.

### 12.5. Télécharger n'est pas publier

Ces commandes ont des rôles différents :

```bash
docker pull nginx:alpine
```

télécharge une image.

```bash
docker push registry.example.com/equipe/mon-api:1.0
```

envoie une image vers un registre distant.

Pour qu'un push réussisse, l'image doit être correctement taguée et l'utilisateur doit disposer des permissions nécessaires.

## 13. Construire une image avec un Dockerfile

### 13.1. Définition du Dockerfile

Un Dockerfile est un fichier texte contenant des instructions utilisées pour construire une image.

Il décrit notamment :

- L'image de base.
- Le répertoire de travail.
- Les fichiers à copier.
- Les commandes de construction.
- Les variables d'environnement.
- L'utilisateur d'exécution.
- La commande de démarrage.

Le Dockerfile permet d'automatiser la création de l'environnement au lieu de suivre manuellement une série de commandes.

### 13.2. Principe de construction

```text
Répertoire du projet
 |
 +-- Dockerfile
 |
 +-- Fichiers de l'application
 |
 +-- Dépendances
          |
          v
    docker build
          |
          v
    Moteur de construction
          |
          v
    Image résultante
          |
          v
     docker run
          |
          v
      Conteneur
```

Le répertoire transmis à la commande de construction constitue le contexte de build. Il détermine les fichiers accessibles aux instructions de construction telles que `COPY`.

### 13.3. Créer un projet de démonstration

Nous allons créer une petite API HTTP en Python utilisant uniquement la bibliothèque standard.

Structure :

```text
mon-api-docker/
|
+-- app.py
|
+-- Dockerfile
|
+-- .dockerignore
```

Le programme répondra avec un objet JSON lors de l'accès à la racine ou à l'URL `/health`.

### 13.4. Créer `app.py`

Créez le fichier `app.py` avec le contenu suivant :

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            payload = {
                "status": "ok"
            }
        else:
            payload = {
                "message": "Bienvenue dans mon API Docker",
                "service": "mon-api",
                "hostname": os.getenv("HOSTNAME", "inconnu")
            }

        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), RequestHandler)

    print(f"Serveur démarré sur le port {port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Arrêt demandé", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
```

### 13.5. Comprendre le programme

`BaseHTTPRequestHandler` permet de définir le comportement de traitement des requêtes HTTP.

`do_GET()` est appelée lorsque le serveur reçoit une requête HTTP GET.

Lorsque le chemin demandé est `/health`, le programme retourne :

```json
{
  "status": "ok"
}
```

Pour les autres chemins, il retourne un message d'accueil accompagné du nom d'hôte du processus si la variable `HOSTNAME` est disponible.

`HTTPServer(("0.0.0.0", port), RequestHandler)` permet au serveur d'écouter sur toutes les interfaces réseau disponibles à l'intérieur de son environnement.

Cette écoute est importante : si le service n'écoute que sur `127.0.0.1` à l'intérieur du conteneur, le port publié ne permet généralement pas d'atteindre le service depuis l'interface réseau du conteneur.

Cette application est conçue pour un exercice pédagogique. Le serveur HTTP fourni par la bibliothèque standard n'est pas destiné à servir une application de production exposée à un trafic important.

### 13.6. Tester le programme localement

Sur le système hôte, exécutez :

```bash
python app.py
```

Si votre installation utilise `python3` :

```bash
python3 app.py
```

Le serveur écoute normalement sur le port 8000.

Dans un autre terminal, testez :

```bash
curl http://127.0.0.1:8000/
```

Puis :

```bash
curl http://127.0.0.1:8000/health
```

Si `curl` n'est pas disponible, un navigateur ou un client HTTP équivalent peut être utilisé.

Arrêtez le programme local avec `Ctrl+C` avant de passer à la construction Docker.

### 13.7. Créer le Dockerfile

Créez un fichier nommé exactement `Dockerfile` :

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser app.py .

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
```

### 13.8. Comprendre `FROM`

```dockerfile
FROM python:3.12-slim
```

`FROM` définit l'image de base du build.

Dans cet exemple, nous utilisons une image Python 3.12 avec un environnement système allégé.

Il est préférable de choisir une image provenant d'une source fiable et compatible avec le projet.

Dans un environnement professionnel, il faut aussi vérifier :

- Le cycle de support de la version Python.
- L'architecture prise en charge.
- Les vulnérabilités connues.
- Les mises à jour de sécurité.
- La provenance de l'image.
- La politique de versionnement utilisée.

### 13.9. Comprendre `ENV`

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
```

`ENV` définit des variables d'environnement dans l'image.

Dans notre exemple :

- `PYTHONDONTWRITEBYTECODE` désactive l'écriture habituelle de fichiers bytecode Python `.pyc`.
- `PYTHONUNBUFFERED` permet de rendre la sortie standard de Python plus immédiatement observable dans les journaux.
- `PORT` définit le port attendu par l'application si aucune autre valeur n'est fournie.

Une variable `ENV` n'est pas un mécanisme adapté à la conservation de secrets. Les variables d'environnement peuvent être visibles à travers les métadonnées ou les paramètres d'exécution du conteneur.

### 13.10. Comprendre `WORKDIR`

```dockerfile
WORKDIR /app
```

Cette instruction définit le répertoire de travail utilisé pour les instructions suivantes et pour le processus démarré à partir de cette configuration, sauf remplacement explicite.

Les instructions relatives telles que `COPY` sont interprétées par rapport au contexte défini par l'instruction appropriée, notamment le répertoire de travail pour la destination relative.

### 13.11. Comprendre `RUN`

```dockerfile
RUN useradd --create-home --uid 10001 appuser
```

`RUN` exécute une commande pendant la construction de l'image.

Ici, la commande crée un compte utilisateur non privilégié nommé `appuser`.

Il s'agit d'une étape de construction. Elle ne s'exécute pas à chaque redémarrage du conteneur.

### 13.12. Comprendre `COPY`

```dockerfile
COPY --chown=appuser:appuser app.py .
```

Cette instruction copie le fichier `app.py` du contexte de construction vers le répertoire de travail de l'image.

`--chown` définit la propriété du fichier copié pour les systèmes de fichiers et images qui prennent en charge cette option.

La source `app.py` doit être incluse dans le contexte de construction et ne pas être exclue par une règle d'ignorance applicable.

### 13.13. Comprendre `USER`

```dockerfile
USER appuser
```

Cette instruction définit l'utilisateur utilisé pour les instructions suivantes et le processus principal du conteneur, sauf remplacement au lancement.

L'exécution avec un compte non privilégié réduit les conséquences possibles d'une compromission par rapport à une application qui fonctionne inutilement en tant que `root`.

Cette mesure ne remplace pas les autres contrôles d'isolation et de sécurité.

### 13.14. Comprendre `EXPOSE`

```dockerfile
EXPOSE 8000
```

Cette instruction documente le port utilisé par le service dans le conteneur.

Elle ne publie pas automatiquement ce port sur le système hôte. Il faudra utiliser une option telle que `-p` lors du démarrage.

### 13.15. Comprendre `CMD`

```dockerfile
CMD ["python", "app.py"]
```

`CMD` définit la commande par défaut exécutée lorsque le conteneur démarre, en l'absence d'une commande différente.

La syntaxe entre crochets est appelée forme exec. Elle transmet l'exécutable et ses arguments sans passer implicitement par un shell.

Cette forme est généralement adaptée au lancement d'un processus principal.

### 13.16. `RUN`, `CMD` et `ENTRYPOINT` : différences

| Instruction | Quand agit-elle ? | Rôle |
|---|---|---|
| `RUN` | Pendant la construction | Exécuter une commande de construction. |
| `CMD` | Au démarrage du conteneur | Définir la commande ou les arguments par défaut. |
| `ENTRYPOINT` | Au démarrage du conteneur | Définir l'exécutable principal de l'image. |

Exemple :

```dockerfile
FROM alpine:3.22

RUN echo "Préparation de l'image"

CMD ["echo", "Démarrage du conteneur"]
```

Lors de la construction, la commande `RUN` est exécutée et son résultat contribue au build.

Lors du lancement du conteneur, le `CMD` définit le comportement par défaut, sauf remplacement.

Cette distinction est essentielle pour comprendre pourquoi une commande peut réussir au moment du build puis ne pas se produire au lancement, ou inversement.

## 14. Le contexte de construction et `.dockerignore`

### 14.1. Qu'est-ce que le contexte de build ?

Lorsque vous exécutez :

```bash
docker build -t mon-api:1.0 .
```

le point final désigne le répertoire courant comme contexte de construction.

Le moteur de construction peut accéder aux fichiers du contexte pour les instructions du Dockerfile.

Il ne peut pas simplement copier n'importe quel fichier du système hôte situé en dehors de ce contexte comme s'il faisait partie du projet.

### 14.2. Pourquoi le contexte est-il important ?

Un contexte trop volumineux peut :

- Ralentir les constructions.
- Augmenter les transferts vers le moteur de construction.
- Introduire des fichiers inutiles.
- Exposer accidentellement des données locales au processus de construction.
- Rendre l'utilisation du cache moins efficace lorsque des fichiers non pertinents changent.

Il faut limiter le contexte aux fichiers nécessaires.

### 14.3. Créer `.dockerignore`

Dans le même répertoire que le Dockerfile, créez `.dockerignore` :

```dockerignore
.git/
.venv/
venv/
__pycache__/
*.pyc
*.pyo
*.log
.env
.env.*
!.env.example
tests/
dist/
build/
```

Ce fichier exclut les motifs correspondants du contexte transmis au moteur de construction, selon les règles de correspondance de Docker.

Il est important de vérifier que les fichiers nécessaires au build ne sont pas exclus par erreur.

Dans cet exemple, `tests/` est exclu car le petit Dockerfile n'en a pas besoin pour construire l'application. Dans un projet réel, les tests peuvent avoir besoin d'être inclus dans une étape de test ou dans un contexte de build distinct.

### 14.4. `.gitignore` et `.dockerignore` ne sont pas identiques

| Fichier | Fonction |
|---|---|
| `.gitignore` | Définit les fichiers que Git doit ignorer lorsqu'ils ne sont pas déjà suivis. |
| `.dockerignore` | Exclut des fichiers du contexte de construction Docker. |

Un fichier peut être suivi par Git mais exclu du contexte Docker.

Inversement, un fichier local ignoré par Git peut être inclus dans une construction Docker si le motif correspondant n'est pas couvert par `.dockerignore`.

Les deux mécanismes sont indépendants.

### 14.5. Les secrets et le contexte

N'envoyez pas de secrets inutiles dans le contexte Docker.

Par exemple, ne laissez pas un fichier `.env` contenant de vrais mots de passe être copié dans l'image.

`.dockerignore` est une protection utile contre les inclusions accidentelles, mais la sécurité doit aussi être assurée dans le Dockerfile, dans le processus de build et dans la gestion des paramètres d'exécution.

Pour des secrets nécessaires au build, utilisez les mécanismes dédiés de gestion des secrets et des montages de build plutôt que de les intégrer aux couches de l'image.

## 15. Construire et lancer votre propre image

### 15.1. Construire l'image

Dans le répertoire qui contient le Dockerfile :

```bash
docker build -t mon-api:1.0 .
```

Explication :

- `docker build` lance une construction.
- `-t mon-api:1.0` affecte le nom `mon-api` et le tag `1.0` à l'image.
- `.` définit le contexte local.

Docker traite les instructions du Dockerfile et utilise le cache lorsque les conditions le permettent.

### 15.2. Vérifier que l'image existe

```bash
docker image ls
```

Vous devriez trouver une référence similaire à :

```text
mon-api   1.0   IDENTIFIANT_IMAGE   ...
```

Les identifiants, dates et tailles seront différents sur votre machine.

### 15.3. Lancer le conteneur

```bash
docker run -d \
  --name mon-api-labo \
  -p 127.0.0.1:8080:8000 \
  mon-api:1.0
```

Cette commande lance le service en arrière-plan et publie le port 8000 du conteneur sur le port 8080 de l'hôte, uniquement sur son interface locale.

### 15.4. Vérifier l'exécution

```bash
docker ps
```

Si le conteneur n'apparaît pas dans la liste, examinez aussi :

```bash
docker ps -a
```

Un conteneur peut avoir démarré puis s'être arrêté à cause d'une erreur dans le programme ou la configuration.

### 15.5. Tester l'API

À partir de l'hôte :

```bash
curl http://127.0.0.1:8080/
```

Réponse attendue sous forme JSON :

```json
{
  "message": "Bienvenue dans mon API Docker",
  "service": "mon-api",
  "hostname": "..."
}
```

La valeur de `hostname` varie selon le nom ou l'identifiant effectif du conteneur.

Tester ensuite l'endpoint de santé :

```bash
curl http://127.0.0.1:8080/health
```

Réponse attendue :

```json
{
  "status": "ok"
}
```

Sous PowerShell, `curl` peut être interprété différemment selon la version de PowerShell et les alias disponibles. Vous pouvez également utiliser :

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health
```

### 15.6. Vérifier le processus et les journaux

```bash
docker logs mon-api-labo
```

Afficher les informations :

```bash
docker inspect mon-api-labo
```

Exécuter une commande supplémentaire :

```bash
docker exec -it mon-api-labo sh
```

Cette dernière commande peut échouer parce que l'image ou l'utilisateur d'exécution ne permet pas de lancer le shell demandé. Notre image utilise un utilisateur non privilégié, et la disponibilité de `sh` dépend du contenu de l'image de base.

### 15.7. Arrêter et supprimer le conteneur

```bash
docker stop mon-api-labo
docker rm mon-api-labo
```

L'image `mon-api:1.0` reste disponible localement.

Pour supprimer ensuite l'image, si elle n'est plus nécessaire :

```bash
docker image rm mon-api:1.0
```

Dans un environnement de travail, vérifiez que cette image ne sert plus à aucun autre conteneur avant de la supprimer.

## 16. Comprendre le cache de construction

### 16.1. Pourquoi Docker utilise-t-il un cache ?

Lors d'une construction, Docker peut réutiliser les résultats d'étapes précédentes si les conditions du cache sont satisfaites.

Cela permet d'éviter de réexécuter inutilement certaines opérations coûteuses.

Par exemple :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]
```

Si le fichier `app.py` change, l'étape de copie et les étapes suivantes peuvent devoir être recalculées.

Les étapes antérieures inchangées peuvent rester réutilisables.

### 16.2. L'ordre des instructions est important

Supposons un projet plus complexe qui possède des dépendances Python.

Dockerfile moins efficace :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
```

Dans cet exemple, une modification d'un fichier quelconque copié par `COPY . .` peut invalider le cache de l'étape et empêcher la réutilisation de l'installation des dépendances.

Dockerfile généralement plus efficace :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

L'étape d'installation des dépendances dépend désormais principalement de `requirements.txt`.

Si seul `app.py` change, les étapes précédentes peuvent être réutilisées lorsque les conditions du cache le permettent.

### 16.3. Attention à l'ordre logique

Optimiser le cache ne consiste pas seulement à déplacer des lignes.

Il faut s'assurer que :

- Les fichiers nécessaires sont déjà présents.
- Les dépendances sont réellement installées au bon moment.
- Les opérations ne dépendent pas de fichiers copiés plus tard.
- Le résultat de construction reste correct.
- Les informations sensibles ne sont pas inscrites dans des couches.

### 16.4. Reconstruire sans utiliser le cache

Pour forcer une reconstruction sans réutilisation du cache standard :

```bash
docker build --no-cache -t mon-api:test .
```

Cette commande est utile pour certains diagnostics.

Elle ne signifie pas qu'il faut systématiquement désactiver le cache dans toutes les constructions : cela peut ralentir inutilement le processus.

### 16.5. Examiner l'historique de l'image

```bash
docker image history mon-api:1.0
```

Cette commande peut aider à observer les couches visibles et les instructions ayant contribué à l'image.

Elle ne fournit pas à elle seule un audit complet de la provenance de tous les fichiers.

## 17. Stockage : couche du conteneur, volume et bind mount

L'un des pièges les plus importants de Docker est la persistance des données.

### 17.1. La couche inscriptible

Lorsqu'un conteneur est créé, Docker ajoute normalement une couche inscriptible au-dessus du contenu fourni par l'image.

Les modifications réalisées dans le système de fichiers du conteneur peuvent être enregistrées dans cette couche.

Schéma :

```text
+----------------------------------+
| Couche inscriptible du conteneur |
| Fichiers modifiés à l'exécution  |
+----------------------------------+
| Couches immuables de l'image     |
| Application et dépendances       |
+----------------------------------+
```

Si le conteneur est arrêté, cette couche existe généralement encore.

Si le conteneur est supprimé, la couche inscriptible associée est supprimée.

Ce stockage ne doit donc pas être utilisé comme unique emplacement de données qui doivent survivre au remplacement du conteneur.

### 17.2. Qu'est-ce qu'un volume ?

Un volume Docker est un espace de stockage géré par Docker et destiné à persister indépendamment du cycle de vie habituel d'un conteneur.

Les volumes sont couramment utilisés pour :

- Les données d'une base de données.
- Les fichiers générés qu'il faut conserver.
- Les données applicatives.
- Les informations qui doivent survivre au remplacement d'un conteneur.

### 17.3. Créer un volume nommé

```bash
docker volume create mon-volume
```

Lister les volumes :

```bash
docker volume ls
```

Inspecter un volume :

```bash
docker volume inspect mon-volume
```

### 17.4. Monter un volume dans un conteneur

Exemple :

```bash
docker run --rm \
  --mount type=volume,source=mon-volume,target=/data \
  alpine:3.22 \
  sh -c 'echo "Donnée persistante" > /data/message.txt'
```

Cette commande monte le volume dans `/data`, écrit un fichier puis arrête le conteneur.

Le conteneur est supprimé grâce à `--rm`, mais le volume nommé n'est pas automatiquement supprimé.

Vous pouvez vérifier la persistance en lançant un autre conteneur :

```bash
docker run --rm \
  --mount type=volume,source=mon-volume,target=/data \
  alpine:3.22 \
  cat /data/message.txt
```

Le texte écrit lors du premier lancement devrait être encore disponible.

### 17.5. Pourquoi utiliser `--mount` ?

Docker propose plusieurs syntaxes de montage.

La forme `--mount` décrit explicitement le type et les paramètres du montage.

Exemple :

```bash
--mount type=volume,source=mon-volume,target=/data
```

Pour un volume nommé, la commande rend le rôle du volume et son point de montage faciles à comprendre.

### 17.6. Qu'est-ce qu'un bind mount ?

Un bind mount monte un fichier ou un répertoire du système hôte dans le conteneur.

Il est utile lorsqu'un programme dans un conteneur doit accéder à des fichiers du projet qui restent sur le poste de développement.

Exemple sous Linux ou macOS, exécuté depuis un répertoire de projet :

```bash
docker run --rm \
  --mount type=bind,source="$(pwd)",target=/workspace,readonly \
  alpine:3.22 \
  ls -la /workspace
```

Le répertoire courant de l'hôte est monté en lecture seule sous `/workspace`.

Le chemin exact à utiliser varie selon le système et le terminal. Sous PowerShell, utilisez un chemin hôte compatible avec Docker Desktop.

### 17.7. Volume et bind mount : comparaison

| Critère | Volume Docker | Bind mount |
|---|---|---|
| Emplacement principal | Géré par Docker | Chemin du système hôte |
| Usage courant | Données persistantes d'application | Code source ou fichiers de configuration locaux |
| Dépendance au chemin hôte | Faible pour l'utilisateur | Forte |
| Contrôle direct par l'hôte | Par les mécanismes Docker | Directement via le répertoire monté |
| Portabilité | Souvent plus simple à gérer avec Docker | Dépend de l'existence du chemin |
| Sécurité | Dépend des permissions et du contenu | L'accès en écriture peut modifier le système de fichiers hôte |

### 17.8. Attention aux bind mounts en écriture

Par défaut, les bind mounts sont généralement accessibles en lecture et écriture.

Un processus exécuté dans un conteneur peut alors modifier ou supprimer des fichiers du répertoire hôte monté, dans la limite de ses permissions et des protections de l'environnement.

Pour un montage qui doit uniquement servir à lire les fichiers :

```bash
--mount type=bind,source="$(pwd)",target=/workspace,readonly
```

Privilégiez la lecture seule lorsque l'application n'a pas besoin de modifier les données du système hôte.

### 17.9. Supprimer un volume

```bash
docker volume rm mon-volume
```

Cette commande supprime le volume nommé si les conditions le permettent.

**Attention : elle peut supprimer les données stockées dans ce volume.**

Avant de supprimer un volume de production ou de test contenant des données importantes, vérifiez son contenu, ses usages et l'existence d'une sauvegarde exploitable.

## 18. Images et conteneurs : cycle de vie complet

### 18.1. Le cycle normal d'une image

```text
Dockerfile et fichiers
          |
          v
    docker build
          |
          v
      Image locale
          |
          v
     docker tag
          |
          v
      docker push
          |
          v
     Registre distant
          |
          v
      docker pull
          |
          v
    Image sur la cible
          |
          v
      docker run
          |
          v
       Conteneur
```

Les étapes `tag`, `push` et `pull` sont utiles lorsqu'une image doit être distribuée vers un autre système.

Un environnement de test local peut fonctionner sans registre distant.

### 18.2. Le cycle de vie du conteneur

```text
Image disponible
       |
       v
docker create
       |
       v
Conteneur créé
       |
       v
docker start
       |
       v
Conteneur actif
       |
       +-----> docker stop
       |             |
       |             v
       |       Conteneur arrêté
       |             |
       |             +-----> docker start
       |
       v
docker rm
       |
       v
Conteneur supprimé
```

La commande `docker run` réalise la création et le démarrage dans une seule opération.

### 18.3. Un conteneur arrêté n'est pas une image

Si vous arrêtez un conteneur, vous ne modifiez pas automatiquement l'image source.

Si vous supprimez un conteneur, l'image reste disponible tant qu'elle n'a pas été supprimée séparément.

Si vous reconstruisez une image avec le même tag, les conteneurs déjà créés ne se transforment pas automatiquement en conteneurs utilisant le nouveau contenu.

Pour obtenir un conteneur basé sur une nouvelle image, il faut généralement le recréer depuis cette image.

### 18.4. Pourquoi reconstruire plutôt que modifier le conteneur en production ?

Modifier directement un fichier dans un conteneur actif peut dépanner temporairement, mais cette modification risque de disparaître lorsqu'il sera supprimé et recréé.

Une procédure plus reproductible consiste à :

1. Modifier le code source.
2. Modifier le Dockerfile si nécessaire.
3. Reconstruire l'image.
4. Exécuter les tests.
5. Créer un conteneur à partir de cette image.
6. Vérifier le résultat.
7. Déployer selon le processus prévu.

Les conteneurs sont généralement plus faciles à maintenir lorsqu'ils peuvent être remplacés à partir d'une image identifiée et d'une configuration explicite.

## 19. Taguer, exporter et distribuer une image

### 19.1. Taguer une image

Supposons que l'image existe sous le nom :

```text
mon-api:1.0
```

Vous pouvez lui attribuer une nouvelle référence :

```bash
docker tag mon-api:1.0 mon-api:test
```

La commande crée une nouvelle référence vers l'image correspondante, sans nécessairement reconstruire le contenu.

Les références `mon-api:1.0` et `mon-api:test` peuvent alors désigner la même identité d'image.

### 19.2. Préparer une référence de registre

Exemple :

```bash
docker tag mon-api:1.0 registry.example.com/equipe/mon-api:1.0
```

Cette commande prépare un nom d'image correspondant au registre et au projet visés.

L'adresse `registry.example.com/equipe/mon-api` est un exemple fictif : remplacez-la par le nom réel du registre.

### 19.3. Envoyer l'image

Après authentification et vérification des droits :

```bash
docker push registry.example.com/equipe/mon-api:1.0
```

Le contenu de l'image est envoyé au registre selon les couches qui doivent être transférées.

### 19.4. Télécharger depuis le registre

Sur une autre machine disposant des droits d'accès :

```bash
docker pull registry.example.com/equipe/mon-api:1.0
```

Puis :

```bash
docker run -d \
  --name mon-api-production-test \
  -p 127.0.0.1:8080:8000 \
  registry.example.com/equipe/mon-api:1.0
```

Cet exemple montre la création d'un nouveau conteneur à partir d'une image distante. La mise en production réelle doit également inclure les contrôles de sécurité, la configuration des secrets, la surveillance et les règles réseau adaptées.

### 19.5. Exporter et importer une image

Il est possible de sauvegarder une image dans une archive :

```bash
docker image save -o mon-api-image.tar mon-api:1.0
```

Puis de la charger dans un autre moteur Docker :

```bash
docker image load -i mon-api-image.tar
```

Cette méthode peut être utile pour un environnement isolé ou un transfert contrôlé.

Elle ne remplace pas nécessairement un registre, notamment lorsque plusieurs équipes doivent distribuer régulièrement des versions.

### 19.6. Ne pas confondre `save` et `export`

`docker image save` enregistre une ou plusieurs images avec les informations nécessaires à leur chargement.

`docker container export` exporte le système de fichiers d'un conteneur dans une archive, sans constituer une sauvegarde équivalente de l'image, de ses tags, de son historique de construction et de toutes les métadonnées de l'image.

Pour distribuer une image, privilégiez les méthodes prévues pour la sauvegarde ou la publication d'images.

## 20. Variables d'environnement et configuration

### 20.1. Définir une variable à l'exécution

Une image peut contenir des valeurs par défaut, mais le lancement d'un conteneur peut fournir une configuration différente.

Exemple :

```bash
docker run --rm \
  -e PORT=8000 \
  alpine:3.22 \
  sh -c 'echo "Port configuré : $PORT"'
```

Cette commande définit une variable d'environnement visible par le processus exécuté.

### 20.2. Configurer notre API

Notre application utilise la variable `PORT`.

Vous pouvez démarrer l'image en remplaçant la valeur par défaut :

```bash
docker run -d \
  --name mon-api-alternative \
  -e PORT=8001 \
  -p 127.0.0.1:8081:8001 \
  mon-api:1.0
```

Le service écoute alors sur le port 8001 à l'intérieur du conteneur et est accessible localement sur le port 8081 de l'hôte, si le démarrage réussit.

Tester :

```bash
curl http://127.0.0.1:8081/health
```

Cette possibilité permet de séparer le code de certaines valeurs de configuration.

### 20.3. Valeurs de configuration et secrets

Les variables d'environnement peuvent être adaptées pour les paramètres de fonctionnement, mais les secrets exigent une attention particulière.

Évitez de fournir de véritables secrets dans des commandes partagées, des fichiers suivis ou les journaux.

Dans les environnements professionnels, utilisez les mécanismes de gestion des secrets prévus par la plateforme de déploiement ou par l'infrastructure.

Les mécanismes spécifiques dépendent du système utilisé. Il faut choisir une solution qui protège les secrets au repos, limite leur accès et permet de les renouveler.

## 21. Sécurité élémentaire des conteneurs

Un conteneur fournit un environnement isolé, mais cela ne signifie pas qu'il est invulnérable.

La sécurité dépend de l'image, des permissions, du moteur, des ressources accessibles, des ports publiés et de la configuration du système.

### 21.1. Utiliser des images provenant de sources fiables

Avant d'utiliser une image :

- Vérifiez son origine.
- Examinez sa documentation.
- Identifiez les versions de logiciels contenues.
- Vérifiez les mises à jour de sécurité.
- Recherchez les vulnérabilités connues.
- Vérifiez les architectures compatibles.
- Évitez de télécharger et d'exécuter des images inconnues sans investigation.

Une image populaire n'est pas nécessairement adaptée à toutes les exigences de sécurité.

### 21.2. Éviter l'exécution inutile en tant que root

Sur Linux, `root` dispose de privilèges élevés dans l'espace du conteneur. Selon la configuration et les mécanismes d'isolation, ces privilèges peuvent aussi augmenter les risques pour l'hôte.

Lorsque cela est possible, définissez un utilisateur non privilégié dans le Dockerfile :

```dockerfile
USER appuser
```

Cet utilisateur doit disposer des permissions nécessaires à l'application, sans autorisations excessives.

Notre Dockerfile de laboratoire montre un exemple de cette approche.

### 21.3. Ne pas utiliser `--privileged` sans justification

L'option `--privileged` accorde des capacités supplémentaires à un conteneur et peut réduire significativement son isolation.

Une commande telle que :

```bash
docker run --privileged ...
```

ne doit pas être ajoutée simplement pour faire disparaître une erreur de permission.

Il faut déterminer quelle capacité est réellement nécessaire et rechercher une configuration moins permissive.

### 21.4. Limiter les ports publiés

Pour un service destiné uniquement au poste local, préférez :

```bash
-p 127.0.0.1:8080:8000
```

plutôt que de publier le port sur toutes les interfaces sans justification.

Pour les applications exposées sur un réseau, configurez également le pare-feu, les règles de routage et les mécanismes d'authentification adaptés.

### 21.5. Limiter l'accès aux fichiers de l'hôte

Les bind mounts peuvent exposer des fichiers de l'hôte au conteneur.

Évitez de monter inutilement :

- Le répertoire personnel complet.
- Des répertoires système sensibles.
- Les fichiers contenant les secrets d'accès.
- Les sockets qui accordent des privilèges élevés.
- Les répertoires contenant des données d'autres applications.

Lorsque le conteneur doit seulement lire un dossier, utilisez un montage en lecture seule.

### 21.6. Ne pas mettre de secrets dans l'image

Évitez notamment :

```dockerfile
ENV DB_PASSWORD="mot-de-passe-secret"
```

et :

```dockerfile
COPY .env /app/.env
```

Les secrets intégrés à une image peuvent rester visibles dans ses couches ou ses métadonnées.

Les supprimer dans une instruction ultérieure ne suffit pas nécessairement à les éliminer de l'historique de construction.

Utilisez un mécanisme de gestion des secrets adapté au contexte.

### 21.7. Comprendre l'accès au daemon Docker

L'accès au socket de contrôle du daemon Docker est une autorisation sensible.

Selon la configuration, contrôler le daemon peut donner la possibilité de créer des conteneurs avec des privilèges importants ou de monter des répertoires de l'hôte.

L'appartenance à un groupe permettant de contrôler Docker ne doit donc pas être considérée comme une permission anodine.

Limitez l'accès au daemon aux personnes et aux services qui en ont réellement besoin.

### 21.8. Mettre à jour les images

Les images doivent être reconstruites et mises à jour selon un processus défini.

Une image ancienne peut contenir des bibliothèques vulnérables, même si le code applicatif n'a pas changé.

Les procédures professionnelles devraient intégrer :

- La gestion des versions de base.
- Les contrôles de vulnérabilités.
- Les tests après mise à jour.
- La traçabilité de l'image publiée.
- Un processus de correction des vulnérabilités.

### 21.9. Docker ne remplace pas une politique de sécurité

Il faut considérer conjointement :

- L'image.
- Le processus de construction.
- Le registre.
- Les permissions.
- Les variables et secrets.
- Le réseau.
- Le stockage.
- Le moteur Docker.
- Le système hôte.
- La surveillance.

Une image bien construite n'empêche pas automatiquement une mauvaise configuration des ports ou des volumes.

## 22. Les erreurs fréquentes et leurs solutions

### 22.1. Erreur : le daemon Docker ne répond pas

Une commande peut retourner un message indiquant que le daemon n'est pas accessible.

Vérifiez :

```bash
docker version
docker info
```

Si le client est disponible, mais que le serveur ne répond pas, vérifiez que le moteur ou Docker Desktop fonctionne.

Sous un système Linux utilisant le service Docker, les commandes de diagnostic peuvent inclure :

```bash
systemctl status docker
```

Les commandes `systemctl` ne sont pas adaptées à tous les environnements, notamment à certains contextes Docker Desktop.

### 22.2. Erreur : le port est déjà utilisé

Exemple :

```text
port is already allocated
```

Cela signifie généralement que le port hôte demandé est déjà occupé ou qu'un autre mapping l'utilise.

Solutions possibles :

- Arrêter le conteneur qui utilise déjà le port si cela est prévu.
- Choisir un autre port hôte.
- Vérifier qu'un autre service du système n'occupe pas ce port.

Exemple :

```bash
docker run -d \
  --name nginx-test-8081 \
  -p 127.0.0.1:8081:80 \
  nginx:alpine
```

### 22.3. Erreur : le nom du conteneur existe déjà

Docker peut refuser de créer un nouveau conteneur avec un nom déjà attribué.

Vérifiez :

```bash
docker ps -a
```

Si l'ancien conteneur n'est plus nécessaire, arrêtez-le puis supprimez-le.

```bash
docker stop nginx-labo
docker rm nginx-labo
```

Si vous souhaitez conserver l'ancien conteneur, utilisez un autre nom.

### 22.4. Erreur : `docker build` ne trouve pas un fichier

Vérifiez :

- Que le fichier existe.
- Que le nom respecte les majuscules et minuscules attendues.
- Que le contexte de build est correct.
- Que le fichier n'est pas exclu par `.dockerignore`.
- Que le chemin source de `COPY` est bien relatif au contexte.

Exemple :

```bash
docker build -t mon-api:1.0 .
```

Le point final doit être présent lorsque le contexte utilisé est le répertoire courant.

### 22.5. Erreur : le conteneur démarre puis s'arrête

Consultez :

```bash
docker ps -a
```

Puis :

```bash
docker logs NOM_DU_CONTENEUR
```

Recherchez notamment :

- Une erreur de syntaxe.
- Une variable de configuration manquante.
- Une commande de démarrage incorrecte.
- Une dépendance absente.
- Un port ou un répertoire incorrect.
- Une permission insuffisante.
- Un processus principal qui termine normalement.

Ne supposez pas que le moteur Docker est défectueux avant d'avoir examiné les journaux de l'application.

### 22.6. Erreur : le port est publié, mais le service reste inaccessible

Vérifiez :

```bash
docker ps
docker port NOM_DU_CONTENEUR
docker logs NOM_DU_CONTENEUR
```

Confirmez que l'application écoute effectivement sur le port prévu et sur une interface accessible à travers la configuration réseau.

Un service qui écoute uniquement sur `127.0.0.1` à l'intérieur du conteneur peut ne pas être accessible comme prévu depuis un port publié.

### 22.7. Erreur : les fichiers ont disparu après suppression du conteneur

Si les fichiers étaient uniquement dans la couche inscriptible du conteneur, leur disparition après suppression est le comportement attendu.

Pour éviter ce problème, utilisez un volume ou un bind mount adapté et testez la persistance.

N'utilisez pas la couche du conteneur comme unique emplacement de données importantes.

### 22.8. Erreur : l'image a été modifiée, mais le conteneur utilise encore l'ancien contenu

Un conteneur existant ne se transforme pas automatiquement lorsqu'une nouvelle image est construite avec le même tag.

Il faut généralement créer un nouveau conteneur à partir de la nouvelle image, puis vérifier que le service fonctionne.

Dans un environnement de production, le remplacement doit être intégré à une procédure de déploiement contrôlée.

## 23. Bonnes pratiques Docker pour débuter

### 23.1. Utiliser un Dockerfile versionné

Conservez le Dockerfile dans le dépôt Git avec le code et la documentation du projet.

Cela facilite la revue et la reproduction de la construction.

### 23.2. Limiter le contexte de build

Utilisez `.dockerignore` pour exclure les fichiers qui ne sont pas nécessaires.

Évitez d'inclure les environnements virtuels, les caches et les secrets.

### 23.3. Choisir des images de base adaptées

Utilisez des images fiables et des versions compatibles.

Le choix d'une image plus petite peut réduire les transferts, mais ne doit pas dégrader la compatibilité ou rendre le diagnostic impossible.

### 23.4. Construire des images prévisibles

Évitez de faire dépendre la construction de valeurs non contrôlées.

Fixez les versions pertinentes et vérifiez les mises à jour des dépendances.

Pour une version destinée à une livraison, conservez les identifiants permettant de retrouver le contenu exact de l'image.

### 23.5. Faire fonctionner l'application avec des permissions limitées

N'exécutez pas systématiquement tous les services en tant que `root`.

Accordez uniquement les permissions nécessaires à l'application.

### 23.6. Séparer les données du cycle de vie du conteneur

Les fichiers importants doivent être stockés dans des volumes ou des systèmes de stockage externes appropriés.

La suppression d'un conteneur ne doit pas provoquer une perte de données non prévue.

### 23.7. Ne pas publier tous les ports par défaut

Publiez uniquement les ports nécessaires.

Pour un service local, une publication sur `127.0.0.1` est souvent adaptée.

### 23.8. Observer les journaux et l'état

Apprenez à utiliser :

```bash
docker ps -a
docker logs NOM_DU_CONTENEUR
docker inspect NOM_DU_CONTENEUR
docker stats
```

Ces commandes constituent une base solide pour la majorité des diagnostics de débutant.

### 23.9. Préférer la reconstruction à la modification manuelle du conteneur

Les corrections doivent être effectuées dans le code, les fichiers de configuration ou le Dockerfile, puis intégrées dans une nouvelle image.

Il devient ainsi plus facile de reproduire le résultat et de comprendre quelles modifications ont été livrées.

### 23.10. Nettoyer avec prudence

Les commandes de suppression et de nettoyage peuvent retirer des ressources encore utiles.

Avant une opération de nettoyage, examinez :

```bash
docker ps -a
docker image ls
docker volume ls
```

Ne supprimez pas les volumes contenant des données importantes sans avoir vérifié les sauvegardes et les dépendances.

## 24. Laboratoire pratique : servir une page web avec Nginx

Ce laboratoire permet de manipuler une image existante avant de construire une image personnalisée.

### 24.1. Télécharger l'image

```bash
docker pull nginx:alpine
```

Vérifiez :

```bash
docker image ls
```

### 24.2. Démarrer le conteneur

```bash
docker run -d \
  --name site-labo \
  -p 127.0.0.1:8085:80 \
  nginx:alpine
```

### 24.3. Vérifier l'état

```bash
docker ps
```

### 24.4. Accéder au site

Ouvrez :

```text
http://127.0.0.1:8085
```

Vous devriez voir la page par défaut de Nginx.

### 24.5. Examiner les journaux

```bash
docker logs site-labo
```

Puis suivez les nouveaux messages :

```bash
docker logs -f site-labo
```

Arrêtez le suivi avec `Ctrl+C`. Cela interrompt le suivi du terminal, pas nécessairement le serveur Nginx.

### 24.6. Examiner le conteneur

```bash
docker inspect site-labo
```

Vous pouvez observer le port publié, la configuration du conteneur et ses métadonnées.

### 24.7. Arrêter le site

```bash
docker stop site-labo
```

Vérifiez :

```bash
docker ps -a
```

Le conteneur doit être présent dans la liste des conteneurs arrêtés.

### 24.8. Redémarrer le site

```bash
docker start site-labo
```

Vérifiez à nouveau le site dans votre navigateur.

### 24.9. Supprimer le conteneur

```bash
docker stop site-labo
docker rm site-labo
```

L'image `nginx:alpine` reste généralement disponible localement.

### 24.10. Résultat attendu

À la fin du laboratoire, vous devez avoir compris la différence entre :

- Télécharger une image.
- Créer un conteneur.
- Publier un port.
- Exécuter un conteneur.
- Observer son état.
- Arrêter un conteneur.
- Supprimer un conteneur.
- Conserver une image locale pour une prochaine exécution.

## 25. Exercices de compréhension

### Exercice 1 : image et conteneur

Expliquez la différence entre une image Docker et un conteneur.

Une image peut-elle servir à créer plusieurs conteneurs ?

### Exercice 2 : analyser une commande

Décomposez cette commande :

```bash
docker run -d --name api-test -p 127.0.0.1:8080:8000 mon-api:1.0
```

Précisez le rôle de chaque option.

### Exercice 3 : comprendre `RUN` et `CMD`

Dans un Dockerfile :

```dockerfile
FROM alpine:3.22
RUN echo "Construction"
CMD ["echo", "Exécution"]
```

À quel moment chaque commande est-elle exécutée ?

### Exercice 4 : port publié

Une application écoute sur le port 5000 dans son conteneur.

Vous voulez y accéder localement sur le port 9000 de l'hôte.

Écrivez la commande de lancement correspondante en limitant la publication à l'interface locale.

### Exercice 5 : données persistantes

Vous écrivez un fichier dans `/data/message.txt` à l'intérieur d'un conteneur, sans utiliser de montage.

Que peut-il se passer si vous arrêtez le conteneur ? Que se passe-t-il si vous le supprimez ?

Quelle solution convient si le fichier doit survivre à la suppression du conteneur ?

### Exercice 6 : conteneur qui s'arrête

Après un `docker run -d`, le conteneur n'apparaît plus dans `docker ps`.

Quelles commandes faut-il exécuter pour déterminer son état et rechercher la cause de son arrêt ?

### Exercice 7 : `.dockerignore`

Expliquez la différence entre `.gitignore` et `.dockerignore`.

Donnez trois exemples de fichiers ou répertoires qu'il est souvent pertinent d'exclure du contexte de construction.

### Exercice 8 : Dockerfile

Écrivez un Dockerfile minimal qui :

- Utilise une image Python de base.
- Définit `/app` comme répertoire de travail.
- Copie `app.py`.
- Expose le port 8000 à titre de documentation.
- Lance `python app.py` par défaut.

### Exercice 9 : sécurité

Pourquoi est-il dangereux d'inscrire un secret directement dans une instruction `ENV` d'un Dockerfile ?

Citez deux autres mesures de sécurité utiles pour une application conteneurisée.

### Exercice 10 : reconstruire une image

Vous modifiez `app.py` et exécutez de nouveau `docker build -t mon-api:1.0 .`.

Un conteneur existant utilise toujours l'ancien comportement.

Expliquez pourquoi et proposez une démarche pour lancer un conteneur basé sur la nouvelle image.

## 26. Corrigés des exercices

### Corrigé 1

Une image est un modèle contenant les fichiers et les métadonnées nécessaires à la création d'un conteneur.

Un conteneur est une instance exécutable créée à partir d'une image.

Une même image peut servir à créer plusieurs conteneurs, chacun avec son propre état d'exécution.

### Corrigé 2

- `docker run` crée et démarre un conteneur.
- `-d` lance le conteneur en arrière-plan.
- `--name api-test` lui attribue un nom.
- `-p 127.0.0.1:8080:8000` publie le port 8000 du conteneur sur le port 8080 de l'interface locale de l'hôte.
- `mon-api:1.0` désigne l'image et son tag.

### Corrigé 3

`RUN` est exécutée pendant la construction de l'image.

`CMD` définit la commande par défaut au démarrage du conteneur.

Ainsi, `Construction` est affiché pendant le build si cette instruction est exécutée comme prévu, tandis que `Exécution` est affiché lorsque le conteneur démarre et exécute sa commande.

### Corrigé 4

```bash
docker run -d \
  --name service-test \
  -p 127.0.0.1:9000:5000 \
  IMAGE_DU_SERVICE
```

`IMAGE_DU_SERVICE` doit être remplacé par le nom réel de l'image.

### Corrigé 5

Lors de l'arrêt, le conteneur et sa couche inscriptible existent généralement encore. Le fichier peut donc rester disponible lorsqu'on redémarre le même conteneur.

Lors de la suppression, la couche inscriptible du conteneur est normalement supprimée.

Pour conserver le fichier indépendamment du conteneur, utilisez un volume ou un bind mount adapté.

### Corrigé 6

Commencez par :

```bash
docker ps -a
```

Puis :

```bash
docker logs NOM_DU_CONTENEUR
```

Vous pouvez également examiner :

```bash
docker inspect NOM_DU_CONTENEUR
```

L'état et les journaux aident à déterminer si le conteneur a échoué, s'il a terminé normalement ou si la configuration de démarrage est incorrecte.

### Corrigé 7

`.gitignore` définit les fichiers que Git ignore lorsqu'ils ne sont pas déjà suivis.

`.dockerignore` exclut des fichiers du contexte transmis lors de la construction de l'image.

Exemples fréquents :

```text
.git/
.venv/
__pycache__/
.env
```

Le choix des motifs doit être adapté aux fichiers réellement nécessaires à la construction.

### Corrigé 8

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY app.py .

EXPOSE 8000

CMD ["python", "app.py"]
```

Ce Dockerfile illustre les instructions demandées. Un projet réel doit également examiner les dépendances, les permissions, le contexte de build et les exigences de sécurité.

### Corrigé 9

Une valeur inscrite dans `ENV` peut être visible dans les métadonnées du conteneur ou de l'image et peut apparaître dans certaines sorties de diagnostic.

Il est préférable d'utiliser un mécanisme de gestion des secrets adapté.

Autres mesures utiles :

- Exécuter le processus sous un utilisateur non privilégié.
- Limiter les ports publiés.
- Ne monter que les répertoires nécessaires.
- Utiliser des images provenant de sources fiables.
- Contrôler les vulnérabilités.
- Limiter les permissions accordées au daemon et aux conteneurs.

### Corrigé 10

La reconstruction met à jour l'image locale, mais ne remplace pas automatiquement les conteneurs déjà créés.

Il faut vérifier la nouvelle image, puis remplacer le conteneur selon une procédure appropriée.

Dans un laboratoire, cela peut consister à arrêter et supprimer l'ancien conteneur, puis à en créer un nouveau à partir de l'image actualisée.

Dans un environnement de production, ce remplacement doit être effectué par un processus de déploiement contrôlé.

## 27. Projet de fin de niveau : conteneuriser une petite application

### 27.1. Objectif

Construire une application HTTP simple, en créer une image Docker, exécuter un conteneur, publier un port et vérifier son fonctionnement.

Le projet doit montrer que vous maîtrisez le cycle complet d'une image et d'un conteneur, et pas seulement les commandes `docker run`.

### 27.2. Travail demandé

1. Créer le répertoire `mon-api-docker`.
2. Créer le fichier `app.py`.
3. Tester l'application en dehors de Docker.
4. Écrire le Dockerfile.
5. Créer le fichier `.dockerignore`.
6. Construire l'image `mon-api:1.0`.
7. Afficher les images locales.
8. Démarrer le conteneur avec un nom explicite.
9. Publier le port de façon adaptée à un laboratoire local.
10. Tester la racine de l'API et `/health`.
11. Consulter les journaux.
12. Vérifier les métadonnées avec `docker inspect`.
13. Arrêter le conteneur.
14. Supprimer le conteneur.
15. Vérifier que l'image est encore disponible.
16. Reconstruire l'image après une modification du code.
17. Relancer un nouveau conteneur sur la nouvelle image.
18. Documenter les commandes et les résultats.

### 27.3. Critères de réussite

Le projet est validé si :

- Le Dockerfile peut construire une image.
- L'application démarre dans un conteneur.
- Le port publié permet d'accéder à l'application.
- L'endpoint `/health` répond.
- Les journaux permettent d'observer le démarrage.
- Le conteneur peut être arrêté et recréé.
- Le Dockerfile et `.dockerignore` sont conservés dans le dépôt.
- Les données importantes ne dépendent pas uniquement de la couche inscriptible du conteneur.
- Aucun secret n'est incorporé à l'image.
- Le processus de reconstruction et de remplacement du conteneur est expliqué.

### 27.4. Améliorations facultatives

Après validation du projet de base, vous pouvez :

- Ajouter des tests automatisés.
- Introduire un contrôle de santé plus complet.
- Ajouter un volume pour des données persistantes.
- Configurer des limites de ressources.
- Publier l'image dans un registre de test.
- Ajouter un pipeline CI qui construit et teste l'image.
- Scanner l'image à la recherche de vulnérabilités.
- Améliorer la gestion des erreurs de l'application.
- Construire une image multi-stage pour un projet qui nécessite compilation ou empaquetage.
- Tester le lancement avec un utilisateur non privilégié et des permissions limitées.

Chaque ajout doit répondre à un besoin clair et être testé.

## 28. Glossaire essentiel

**Bind mount :** montage d'un fichier ou répertoire du système hôte dans un conteneur.

**Build context :** ensemble de fichiers que le moteur de construction peut utiliser pour construire une image.

**Cache de build :** mécanisme qui permet de réutiliser certains résultats de construction lorsque les conditions du cache sont satisfaites.

**Conteneur :** instance exécutable créée à partir d'une image.

**Daemon :** service qui gère les ressources Docker.

**Docker CLI :** interface en ligne de commande utilisée pour communiquer avec Docker.

**Docker Engine :** moteur permettant notamment de construire et de gérer les conteneurs, images, réseaux et volumes.

**Dockerfile :** fichier décrivant les instructions de construction d'une image.

**`.dockerignore` :** fichier qui exclut certains fichiers du contexte de construction.

**Image :** modèle contenant les fichiers et métadonnées nécessaires à la création de conteneurs.

**Image de base :** image utilisée comme point de départ d'une construction.

**Layer, ou couche :** ensemble de modifications du système de fichiers associé à une image.

**Port publié :** port du conteneur rendu accessible via un port et une adresse de l'hôte selon une configuration donnée.

**Registre :** service permettant de stocker et de distribuer des images.

**Tag :** nom associé à une référence d'image, généralement utilisé pour identifier une version logique.

**Volume :** stockage géré par Docker qui peut persister indépendamment du cycle de vie habituel d'un conteneur.

**`CMD` :** instruction qui définit la commande ou les arguments par défaut au démarrage du conteneur.

**`COPY` :** instruction qui copie des fichiers depuis le contexte de construction vers l'image.

**`ENTRYPOINT` :** instruction qui définit l'exécutable principal prévu pour le conteneur.

**`ENV` :** instruction permettant de définir des variables d'environnement dans l'image.

**`EXPOSE` :** instruction qui documente un port utilisé par l'application sans le publier automatiquement sur l'hôte.

**`FROM` :** instruction qui définit l'image de base d'une étape de construction.

**`RUN` :** instruction qui exécute une commande pendant la construction.

**`USER` :** instruction qui définit l'utilisateur utilisé pour les instructions suivantes et le processus principal du conteneur.

**`WORKDIR` :** instruction qui définit le répertoire de travail utilisé pour les opérations ultérieures.

## 29. Références officielles pour approfondir

### Installation et premiers pas

- Documentation générale Docker : https://docs.docker.com/
- Installation de Docker Engine : https://docs.docker.com/engine/install/
- Installation de Docker Desktop sous Windows : https://docs.docker.com/desktop/setup/install/windows-install/
- Premiers pas avec les conteneurs : https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container
- Comprendre les images : https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image

### Images et Dockerfile

- Référence du Dockerfile : https://docs.docker.com/reference/dockerfile/
- Bonnes pratiques de construction : https://docs.docker.com/build/building/best-practices/
- Contexte de construction : https://docs.docker.com/build/concepts/context/
- Gestion des images par la CLI : https://docs.docker.com/reference/cli/docker/image/
- Liste des images : https://docs.docker.com/reference/cli/docker/image/ls/

### Gestion des conteneurs

- Exécution des conteneurs : https://docs.docker.com/engine/containers/run/
- Commandes de gestion des conteneurs : https://docs.docker.com/reference/cli/docker/container/
- Consultation des journaux : https://docs.docker.com/reference/cli/docker/container/logs/

### Réseau et stockage

- Publication et mappage des ports : https://docs.docker.com/engine/network/port-publishing/
- Volumes Docker : https://docs.docker.com/engine/storage/volumes/
- Bind mounts : https://docs.docker.com/engine/storage/bind-mounts/

### Sécurité

- Mode rootless : https://docs.docker.com/engine/security/rootless/
- Sécurité du moteur Docker : https://docs.docker.com/engine/security/
- Bonnes pratiques de construction : https://docs.docker.com/build/building/best-practices/

Les documentations officielles constituent les références pour vérifier la syntaxe exacte, les options prises en charge et les comportements associés à la version de Docker utilisée.

## 30. Synthèse du niveau débutant

Les notions essentielles à retenir sont les suivantes.

**Une image est un modèle.** Elle contient les fichiers et les métadonnées nécessaires à la création d'un conteneur. Elle est généralement construite à partir d'un Dockerfile et peut être distribuée par un registre.

**Un conteneur est une instance en exécution ou conservée à l'état arrêté.** Il possède son propre état et une couche inscriptible qui ne doit pas être considérée comme un stockage durable.

**Docker CLI et Docker Engine ont des rôles différents.** La CLI envoie des commandes, tandis que le moteur gère les images, conteneurs, réseaux et volumes.

**Le Dockerfile décrit la construction.** Les instructions `FROM`, `RUN`, `COPY`, `WORKDIR`, `ENV`, `USER`, `EXPOSE` et `CMD` ont chacune un rôle distinct.

**Les ports doivent être publiés explicitement lorsque l'accès depuis l'hôte est nécessaire.** `EXPOSE` documente un port ; `-p` configure sa publication.

**Les données persistantes doivent être stockées dans un mécanisme adapté.** Les volumes Docker et les bind mounts répondent à des besoins différents.

**La sécurité doit être intégrée dès la construction.** Il faut utiliser des images fiables, limiter les permissions, protéger les secrets et contrôler les montages ainsi que les ports exposés.

Enfin, **reconstruire une image ne remplace pas automatiquement les conteneurs existants**. Une nouvelle image doit être utilisée par un nouveau conteneur ou par un processus de remplacement contrôlé.

Ces fondations permettent d'aborder le niveau suivant : optimisation des Dockerfiles, gestion avancée des volumes et des réseaux, Docker Compose, construction multi-stage et intégration de Docker dans les pipelines CI/CD.