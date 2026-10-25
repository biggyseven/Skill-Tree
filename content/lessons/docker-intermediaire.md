# Docker Compose et registres

## 1. Présentation du cours

Dans le cours débutant, vous avez appris à construire une image Docker, à créer un conteneur, à publier un port et à utiliser un Dockerfile pour préparer l'environnement d'exécution d'une application.

Cependant, une application réelle est rarement constituée d'un seul conteneur. Une architecture courante peut comporter une API, une base de données, un cache, un serveur web, un système de supervision et plusieurs services auxiliaires.

Gérer manuellement tous ces conteneurs devient rapidement compliqué. Il faut mémoriser les commandes de démarrage, les ports, les volumes, les variables d'environnement, les dépendances et les paramètres réseau.

**Docker Compose** permet de décrire une application multi-conteneurs dans un fichier déclaratif, généralement nommé `compose.yaml`. Il permet ensuite de construire les images, de démarrer les services, de gérer leurs réseaux et leurs volumes, de consulter leurs journaux et de les arrêter de manière cohérente.

Les **registres d'images**, quant à eux, permettent de stocker et de distribuer les images construites. Ils constituent un élément important du processus de livraison : l'image peut être construite et testée dans un pipeline CI, publiée dans un registre, puis récupérée sur le serveur qui exécutera l'application.

Ce cours relie ces deux sujets pour établir un flux de travail complet :

```text
Code source
    |
    v
Dockerfile
    |
    v
Construction de l'image
    |
    v
Docker Compose
    |
    v
Application multi-conteneurs
    |
    v
Tests et validation
    |
    v
Publication dans un registre
    |
    v
Téléchargement sur une autre machine
    |
    v
Déploiement de la version validée
```

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez savoir :

- Expliquer le fonctionnement de Docker Compose.
- Structurer un projet contenant plusieurs services.
- Écrire et comprendre un fichier `compose.yaml`.
- Définir des services, des réseaux, des volumes et des contrôles de santé.
- Organiser les dépendances entre les conteneurs.
- Utiliser les commandes essentielles de Docker Compose.
- Gérer la configuration avec des variables d'environnement et des fichiers `.env`.
- Comprendre la différence entre configuration Compose, variables d'environnement et secrets.
- Utiliser plusieurs fichiers Compose pour distinguer le développement et la livraison.
- Créer et versionner des images pour un registre.
- Utiliser Docker Hub, GitHub Container Registry ou GitLab Container Registry.
- S'authentifier auprès d'un registre sans exposer les identifiants.
- Construire, taguer, publier et télécharger une image.
- Distinguer un tag d'un digest.
- Déployer une image publiée sans reconstruire inutilement l'application sur le serveur.
- Diagnostiquer les erreurs de réseau, de configuration, de construction et de publication.
- Préparer un pipeline CI/CD simple pour construire et publier une image.
- Appliquer des principes de sécurité et de traçabilité aux applications conteneurisées.

### 1.2. Prérequis

Il est recommandé de connaître :

- Les images et les conteneurs Docker.
- Les commandes `docker build`, `docker run`, `docker ps` et `docker logs`.
- Les Dockerfiles.
- Les ports et les principes élémentaires de réseau.
- Les fichiers YAML.
- Git et les dépôts distants.
- Les bases de l'intégration continue et de la livraison continue.

Le laboratoire pratique utilisera Python, Flask et Redis. Il ne sera pas nécessaire de connaître Redis en profondeur pour comprendre les notions de Compose.

### 1.3. Les composants étudiés

| Composant | Fonction |
|---|---|
| Dockerfile | Décrit les étapes de construction d'une image. |
| Image Docker | Modèle contenant l'application et ses dépendances. |
| Conteneur | Instance créée à partir d'une image. |
| Docker Compose | Décrit et gère une application composée de plusieurs services. |
| Service Compose | Définit la configuration d'un type de conteneur dans l'application. |
| Réseau Docker | Permet aux services de communiquer entre eux. |
| Volume Docker | Permet de conserver des données indépendamment de la couche inscriptible d'un conteneur. |
| Registre | Stocke et distribue les images. |
| Tag | Nom permettant d'identifier une version logique d'une image. |
| Digest | Identifiant de contenu utilisé pour référencer précisément une image ou un manifeste. |
| Pipeline CI/CD | Automatise les tests, la construction, la publication et éventuellement le déploiement. |

## 2. Comprendre Docker Compose

### 2.1. Pourquoi Docker Compose est-il nécessaire ?

Imaginez une application composée de trois éléments :

- Une API Python.
- Une base de données PostgreSQL.
- Un cache Redis.

Sans Compose, vous pourriez devoir exécuter plusieurs commandes distinctes :

```bash
docker network create mon-reseau

docker volume create donnees-postgres

docker run -d \
  --name base-postgres \
  --network mon-reseau \
  -v donnees-postgres:/var/lib/postgresql/data \
  postgres:18

docker run -d \
  --name cache-redis \
  --network mon-reseau \
  redis:7.4-alpine

docker run -d \
  --name api-python \
  --network mon-reseau \
  -p 127.0.0.1:8080:8000 \
  mon-api:1.0
```

Cet exemple illustre le nombre de paramètres qu'il faut coordonner. Dans un véritable projet, il faudrait également gérer les variables d'environnement, les mots de passe, les dépendances de démarrage, les contrôles de santé et les mises à jour.

Une erreur dans une commande peut empêcher un service de démarrer ou le faire communiquer avec une mauvaise ressource.

Docker Compose permet de centraliser la description de l'application dans un fichier versionnable.

### 2.2. Le principe déclaratif

Avec Compose, vous décrivez l'état souhaité de l'application.

Par exemple :

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "127.0.0.1:8080:80"

  redis:
    image: redis:7.4-alpine
```

Ce fichier décrit deux services :

- `web`, basé sur une image Nginx et accessible depuis le poste local sur le port 8080.
- `redis`, basé sur une image Redis, sans port publié sur l'hôte.

La commande :

```bash
docker compose up -d
```

demande à Compose de créer ou de mettre à jour les ressources nécessaires et de démarrer les services déclarés.

Compose détermine les actions à effectuer à partir de la configuration et de l'état connu des ressources.

### 2.3. Docker Compose n'est pas un registre

Les deux outils remplissent des fonctions différentes.

Docker Compose permet de gérer les services d'une application.

Un registre permet de stocker et de distribuer les images.

```text
                  DOCKER COMPOSE
                        |
             Décrit les services
                        |
             +----------+----------+
             |                     |
             v                     v
       Construction             Exécution
             |                     |
             v                     v
        Image Docker           Conteneur
             |
             v
       Publication dans
        un registre
             |
             v
        Image distante
```

Compose peut utiliser une image locale, récupérer une image depuis un registre ou construire une image à partir d'un Dockerfile lorsque la configuration le prévoit.

Un registre ne démarre pas, à lui seul, les services de l'application.

### 2.4. Docker Compose V2

La commande moderne est :

```bash
docker compose
```

L'ancienne syntaxe utilisait un tiret :

```bash
docker-compose
```

Compose V2 est intégré aux installations courantes de Docker Desktop et peut également être installé comme plugin de la CLI Docker sur les systèmes compatibles.

Pour vérifier sa disponibilité :

```bash
docker compose version
```

Pour vérifier la version du moteur Docker :

```bash
docker version
```

Il faut distinguer la version du moteur de conteneurs de la version de Compose.

### 2.5. La spécification Compose

Les fichiers Compose modernes utilisent la Compose Specification.

Un fichier actuel peut commencer par :

```yaml
name: mon-projet

services:
  web:
    image: nginx:alpine
```

Il n'est généralement plus nécessaire d'ajouter une ancienne clé supérieure `version: "3.8"`.

Les anciennes versions du format Compose ont été réunies dans la spécification moderne. Il est préférable de suivre la documentation de la version de Compose effectivement installée.

## 3. Comprendre les services, les réseaux et les volumes

### 3.1. Les services

Un service représente une définition de composant de l'application.

Exemples :

```yaml
services:
  api:
    image: mon-api:1.0

  redis:
    image: redis:7.4-alpine

  nginx:
    image: nginx:alpine
```

Chaque service précise les caractéristiques des conteneurs qui seront créés pour l'application.

Selon le besoin, il peut définir :

- Une image.
- Une procédure de construction.
- Des ports.
- Des variables d'environnement.
- Des volumes.
- Des dépendances.
- Un contrôle de santé.
- Une politique de redémarrage.
- Des ressources et des paramètres de réseau.

Il est possible de créer plusieurs conteneurs pour un service lorsque l'architecture et la configuration le permettent.

### 3.2. Les réseaux

Par défaut, Compose crée un réseau pour le projet et connecte les services à ce réseau.

Les services peuvent généralement se joindre par leur nom de service grâce à la résolution DNS interne.

Exemple :

```text
+--------------------------------------+
| Réseau Compose du projet             |
|                                      |
| +------------+      +-------------+  |
| | API        | ---> | Redis       |  |
| | service:   |      | service:    |  |
| | api        |      | redis       |  |
| +------------+      +-------------+  |
|                                      |
+--------------------------------------+
```

L'API peut utiliser le nom `redis` comme nom d'hôte pour joindre Redis sur le port interne correspondant.

Il n'est pas nécessaire de coder en dur l'adresse IP du conteneur Redis. Docker peut attribuer une autre adresse lors d'une recréation, tandis que le nom du service reste la référence prévue.

### 3.3. Les volumes

Un volume permet de conserver les données indépendamment du cycle de vie habituel d'un conteneur.

Dans Compose :

```yaml
services:
  redis:
    image: redis:7.4-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Le volume nommé `redis_data` est monté dans `/data` du conteneur Redis.

La persistance réelle dépend toutefois de la manière dont l'application stocke ses données. Un volume monté dans un répertoire que le programme n'utilise pas ne conservera pas les données attendues.

### 3.4. Le rôle de chaque section

| Section | Fonction |
|---|---|
| `services` | Définit les composants de l'application. |
| `networks` | Définit les réseaux partagés ou séparés. |
| `volumes` | Déclare les volumes nommés utilisés par les services. |
| `secrets` | Déclare certains secrets à monter dans les services, selon les capacités et le contexte d'exécution. |
| `configs` | Décrit des éléments de configuration pouvant être fournis aux services selon la plateforme. |

Toutes ces sections ne sont pas obligatoires. Un fichier simple peut uniquement déclarer des services.

## 4. Créer son premier fichier Compose

### 4.1. Préparer le répertoire

Créez un dossier :

```bash
mkdir compose-premier-projet
cd compose-premier-projet
```

Créez ensuite le fichier `compose.yaml`.

### 4.2. Contenu de `compose.yaml`

```yaml
name: compose-premier-projet

services:
  web:
    image: nginx:alpine
    ports:
      - "127.0.0.1:8080:80"
    restart: unless-stopped
```

Ce fichier définit un projet Compose avec un seul service.

### 4.3. Valider la configuration

Avant le démarrage :

```bash
docker compose config
```

Cette commande parse le fichier Compose, résout les références et affiche la configuration interprétée.

Pour vérifier la configuration sans afficher tout le résultat :

```bash
docker compose config --quiet
```

Cette validation détecte notamment certaines erreurs de structure et de configuration.

Elle ne garantit pas que toutes les images sont disponibles ni que les services fonctionneront correctement à l'exécution.

### 4.4. Démarrer le projet

```bash
docker compose up -d
```

Compose récupère l'image si nécessaire, crée le conteneur et configure le réseau ainsi que les autres ressources nécessaires.

L'option `-d` permet de laisser les services fonctionner en arrière-plan.

### 4.5. Afficher les conteneurs du projet

```bash
docker compose ps
```

Cette commande affiche les conteneurs appartenant au projet Compose courant ainsi que leur état.

Pour afficher aussi les conteneurs arrêtés :

```bash
docker compose ps --all
```

### 4.6. Consulter les journaux

```bash
docker compose logs
```

Pour afficher les journaux du service `web` :

```bash
docker compose logs web
```

Pour suivre les journaux en direct :

```bash
docker compose logs -f web
```

Appuyez sur `Ctrl+C` pour arrêter le suivi des journaux. Cette action n'arrête pas les services qui continuent de fonctionner en arrière-plan.

### 4.7. Tester le service

Ouvrez dans un navigateur :

```text
http://127.0.0.1:8080
```

Vous devriez voir la page par défaut de Nginx.

### 4.8. Arrêter le projet

Pour arrêter les conteneurs tout en les conservant :

```bash
docker compose stop
```

Pour redémarrer les services existants :

```bash
docker compose start
```

Pour arrêter et supprimer les conteneurs ainsi que le réseau géré par le projet :

```bash
docker compose down
```

L'image Nginx n'est pas supprimée par cette dernière commande.

## 5. Construire une application multi-services

Ce laboratoire principal reliera une API Python à un service Redis.

L'API comptera les requêtes reçues et conservera le compteur dans Redis. Compose gérera le démarrage des deux services, leur communication réseau et la persistance des données Redis.

### 5.1. Architecture du laboratoire

```text
                  CLIENT HTTP
                      |
                      v
             127.0.0.1:8080
                      |
                      v
             +----------------+
             | Service API    |
             | Python / Flask |
             | Port interne   |
             | 8000            |
             +----------------+
                      |
                      | DNS interne : redis
                      |
                      v
             +----------------+
             | Service Redis  |
             | Port interne   |
             | 6379            |
             +----------------+
                      |
                      v
             +----------------+
             | Volume nommé   |
             | redis_data     |
             +----------------+
```

Seul le service API publie un port sur l'hôte. Redis reste accessible à l'intérieur du réseau Compose, sans port directement publié.

Cette disposition réduit l'exposition réseau de Redis dans le laboratoire.

### 5.2. Structure des fichiers

Créez le répertoire et les fichiers suivants :

```text
compteur-compose/
|
+-- app.py
|
+-- requirements.txt
|
+-- Dockerfile
|
+-- compose.yaml
|
+-- .dockerignore
|
+-- .env.example
|
+-- .gitignore
```

### 5.3. Créer `app.py`

Le programme suivant expose deux routes HTTP.

La route `/` incrémente un compteur stocké dans Redis.

La route `/health` vérifie que l'API peut communiquer avec Redis.

```python
import os

import redis
from flask import Flask, jsonify

app = Flask(__name__)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


@app.get("/")
def index():
    try:
        visits = redis_client.incr("page_views")

        return jsonify(
            service="compteur-api",
            visites=visits,
            version=os.getenv("APP_VERSION", "dev"),
        )
    except redis.RedisError:
        return jsonify(
            error="Le service Redis est indisponible."
        ), 503


@app.get("/health")
def health():
    try:
        redis_client.ping()
    except redis.RedisError:
        return jsonify(status="unhealthy"), 503

    return jsonify(status="healthy"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### 5.4. Comprendre la fonction du programme

L'API utilise Flask pour traiter les requêtes HTTP.

La connexion à Redis utilise les variables d'environnement `REDIS_HOST` et `REDIS_PORT`.

La valeur par défaut du nom d'hôte est `redis`, car nous utiliserons ce nom dans le fichier Compose.

La route `/` demande à Redis d'incrémenter une clé appelée `page_views`.

Exemple de réponse :

```json
{
  "service": "compteur-api",
  "visites": 1,
  "version": "dev"
}
```

À chaque nouvelle requête, le compteur devrait augmenter tant que les données correspondantes sont conservées dans Redis.

La route `/health` vérifie la communication avec Redis. Elle retourne un état sain uniquement si le test de connexion réussit.

Un contrôle de santé ne remplace pas une surveillance complète de l'application, mais il peut aider Compose à identifier certaines situations de défaillance.

### 5.5. Créer `requirements.txt`

```text
Flask==3.1.3
redis==8.1.0
gunicorn==26.2.0
```

Ces versions illustrent un environnement Python adapté à ce laboratoire. Lors d'un projet réel, vérifiez les versions compatibles, leur état de maintenance et les vulnérabilités connues.

L'utilisation de versions explicitement identifiées rend la construction plus prévisible qu'une installation sans contrainte de version. Elle ne garantit toutefois pas à elle seule la reproductibilité complète de toutes les dépendances transitives.

### 5.6. Créer le Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser app.py .

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
```

### 5.7. Comprendre le Dockerfile

`FROM` sélectionne l'image Python de base.

`WORKDIR` définit le répertoire de travail.

`COPY requirements.txt .` copie d'abord les dépendances, afin que l'étape d'installation puisse être réutilisée lorsque seul le code applicatif change.

`RUN` installe les dépendances et crée un utilisateur non privilégié.

`COPY --chown` copie le code applicatif en attribuant sa propriété au compte choisi.

`USER` permet de lancer le processus applicatif avec un utilisateur autre que `root`.

`EXPOSE` documente le port utilisé par l'API.

`CMD` définit la commande de démarrage avec Gunicorn, un serveur WSGI adapté au déploiement d'applications Flask.

Le serveur de développement intégré à Flask convient aux exercices locaux, mais il ne constitue pas le serveur recommandé pour une application professionnelle exposée à des utilisateurs.

### 5.8. Créer `.dockerignore`

```dockerignore
.git/
.venv/
venv/
__pycache__/
*.py[cod]
*.log
.env
.env.*
!.env.example
```

Ce fichier empêche les éléments correspondants d'être inclus dans le contexte de construction.

Le fichier `.env` local doit contenir uniquement les paramètres prévus pour l'environnement de travail et ne doit pas être copié dans l'image.

### 5.9. Créer `.gitignore`

```gitignore
.env
.env.*
!.env.example

.venv/
venv/
__pycache__/
*.py[cod]
*.log
```

`.gitignore` concerne le suivi des fichiers par Git.

`.dockerignore` concerne le contexte de construction Docker.

Les deux fichiers ont des fonctions distinctes.

### 5.10. Créer `.env.example`

```dotenv
IMAGE_NAME=compteur-api
IMAGE_TAG=1.0.0
APP_PORT=8080
```

Ce fichier constitue un exemple de configuration que les contributeurs peuvent copier.

Il ne contient aucun mot de passe ni jeton d'accès.

Créez ensuite votre fichier local `.env` à partir de cet exemple.

Sous Linux ou macOS :

```bash
cp .env.example .env
```

Sous PowerShell :

```powershell
Copy-Item .env.example .env
```

Le fichier `.env` local ne doit pas être commité s'il fait partie des fichiers ignorés.

### 5.11. Créer `compose.yaml`

```yaml
name: compteur-compose

services:
  api:
    image: ${IMAGE_NAME:-compteur-api}:${IMAGE_TAG:-dev}

    build:
      context: .
      dockerfile: Dockerfile

    environment:
      REDIS_HOST: redis
      REDIS_PORT: "6379"
      APP_VERSION: ${IMAGE_TAG:-dev}

    ports:
      - "127.0.0.1:${APP_PORT:-8080}:8000"

    depends_on:
      redis:
        condition: service_healthy

    healthcheck:
      test:
        - CMD
        - python
        - -c
        - "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 10s

    restart: unless-stopped

  redis:
    image: redis:7.4-alpine

    command:
      - redis-server
      - --appendonly
      - "yes"

    volumes:
      - redis_data:/data

    healthcheck:
      test:
        - CMD
        - redis-cli
        - ping
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s

    restart: unless-stopped

volumes:
  redis_data:
```

Ce fichier constitue le point central de l'application.

Il décrit l'image de l'API, sa construction, les variables utilisées à l'exécution, le port publié, la dépendance vis-à-vis de Redis et les contrôles de santé.

Pour Redis, il définit l'image, la commande de démarrage, le volume de données et le contrôle de santé.

Le service Redis ne publie aucun port sur l'hôte.

### 5.12. Comprendre la configuration de l'API

L'attribut `image` définit le nom de référence de l'image à utiliser.

```yaml
image: ${IMAGE_NAME:-compteur-api}:${IMAGE_TAG:-dev}
```

La syntaxe `${VARIABLE:-valeur}` permet d'utiliser une valeur par défaut lorsque la variable est absente ou vide.

Compose peut récupérer ces variables depuis l'environnement du shell et les fichiers d'interpolation prévus par sa configuration.

L'attribut `build` indique comment construire l'image :

```yaml
build:
  context: .
  dockerfile: Dockerfile
```

La construction utilise le répertoire courant et le Dockerfile défini.

L'attribut `environment` définit les variables disponibles dans le conteneur.

```yaml
environment:
  REDIS_HOST: redis
  REDIS_PORT: "6379"
```

Le nom `redis` correspond au service Redis du projet.

L'attribut `ports` publie le port interne 8000 sur le port local défini par `APP_PORT`.

Le mapping ne signifie pas que le conteneur doit écouter sur ce même port interne : le port hôte et le port du conteneur sont indépendants.

### 5.13. Comprendre `depends_on` et `service_healthy`

```yaml
depends_on:
  redis:
    condition: service_healthy
```

Cette configuration demande à Compose d'attendre que Redis soit déclaré sain par son contrôle de santé avant de démarrer le service API dépendant.

Un simple `depends_on` sans condition de santé permet notamment de gérer l'ordre de démarrage, mais ne garantit pas que le service dépendant soit prêt à accepter toutes les opérations applicatives.

C'est un point essentiel lorsqu'une application dépend d'une base de données ou d'un cache.

### 5.14. Comprendre le volume Redis

```yaml
volumes:
  redis_data:/data
```

Le volume nommé `redis_data` est monté dans `/data` du conteneur.

La commande Redis active la persistance append-only :

```yaml
command:
  - redis-server
  - --appendonly
  - "yes"
```

Cette configuration est utile pour démontrer que les données peuvent survivre au remplacement du conteneur lorsque Redis les a effectivement écrites dans son mécanisme de persistance.

Elle ne remplace pas une stratégie de sauvegarde, une procédure de restauration ni une configuration Redis adaptée à la production.

## 6. Démarrer et vérifier une application Compose

### 6.1. Vérifier la configuration avant le démarrage

Dans le répertoire du projet :

```bash
docker compose config
```

Vérifiez notamment :

- Que le fichier est correctement structuré.
- Que les variables sont résolues comme prévu.
- Que l'image de l'API possède un nom valide.
- Que les services, volumes et contrôles de santé sont présents.

Pour uniquement vérifier la validité de la configuration :

```bash
docker compose config --quiet
```

N'oubliez pas que l'affichage de la configuration résolue peut contenir des informations sensibles si vous y avez placé des secrets. Évitez de publier cette sortie sans l'avoir examinée.

### 6.2. Construire et démarrer les services

```bash
docker compose up --build -d
```

Cette commande construit ou actualise l'image de l'API lorsque nécessaire, puis crée et démarre les services.

La commande peut télécharger l'image Redis si elle n'est pas présente localement.

### 6.3. Vérifier l'état des services

```bash
docker compose ps
```

Le service Redis devrait devenir sain après que son contrôle de santé réussit.

Le service API devrait ensuite démarrer et réussir son propre contrôle lorsque l'API peut communiquer avec Redis.

Le statut peut changer après le démarrage. Vérifiez les résultats plutôt que de supposer que les deux services sont prêts immédiatement.

### 6.4. Examiner les journaux

Pour les deux services :

```bash
docker compose logs
```

Pour suivre les journaux :

```bash
docker compose logs -f
```

Pour n'observer que l'API :

```bash
docker compose logs -f api
```

Pour Redis :

```bash
docker compose logs -f redis
```

Le préfixe des lignes permet normalement d'identifier le service dont provient le message.

### 6.5. Tester l'API

Dans un navigateur, ouvrez :

```text
http://127.0.0.1:8080/
```

Ou utilisez :

```bash
curl http://127.0.0.1:8080/
```

La réponse devrait contenir le nom du service, la version configurée et le nombre de visites.

Envoyez ensuite plusieurs requêtes :

```bash
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/
```

La valeur de `visites` devrait augmenter.

Vérifiez également :

```bash
curl http://127.0.0.1:8080/health
```

La réponse attendue est :

```json
{
  "status": "healthy"
}
```

### 6.6. Vérifier la persistance

Arrêtez le projet :

```bash
docker compose down
```

Cette commande retire les conteneurs et le réseau géré par le projet, mais ne supprime normalement pas le volume nommé déclaré dans le fichier.

Redémarrez :

```bash
docker compose up -d
```

Puis envoyez une requête :

```bash
curl http://127.0.0.1:8080/
```

Le compteur devrait conserver sa valeur si les données Redis ont été écrites dans le volume et restaurées au démarrage.

Une interruption brutale ou une configuration de persistance différente peut modifier le comportement. Pour ce laboratoire, l'option append-only permet d'illustrer le rôle du stockage persistant.

### 6.7. Arrêter proprement le laboratoire

```bash
docker compose down
```

Si vous souhaitez également supprimer les volumes nommés du projet :

```bash
docker compose down -v
```

**Attention : `down -v` peut supprimer les données persistantes du laboratoire.** Ne l'utilisez pas sur un projet contenant des données importantes sans avoir vérifié ce qui sera supprimé et sans disposer d'une sauvegarde exploitable.

## 7. Les commandes essentielles de Docker Compose

### 7.1. Démarrer les services

```bash
docker compose up
```

En arrière-plan :

```bash
docker compose up -d
```

Reconstruire les images de services avant le démarrage :

```bash
docker compose up --build -d
```

### 7.2. Construire une image

```bash
docker compose build
```

Construire uniquement l'API :

```bash
docker compose build api
```

Forcer une construction sans le cache :

```bash
docker compose build --no-cache api
```

La dernière commande est utile pour certains diagnostics, mais elle peut augmenter considérablement le temps de construction.

### 7.3. Télécharger les images déclarées

```bash
docker compose pull
```

Pour le service API seulement :

```bash
docker compose pull api
```

Compose peut télécharger les images définies dans la configuration. Si un service possède une configuration de build, cette commande ne construit pas automatiquement son image à partir du Dockerfile.

### 7.4. Publier les images

```bash
docker compose push
```

Pour un service :

```bash
docker compose push api
```

Cette commande suppose que les références d'images sont correctement définies et que les permissions nécessaires sont disponibles sur le registre.

### 7.5. Lister les services

```bash
docker compose ps
```

Pour les conteneurs arrêtés également :

```bash
docker compose ps --all
```

### 7.6. Consulter les journaux

```bash
docker compose logs
docker compose logs api
docker compose logs -f redis
docker compose logs --tail 100 api
```

### 7.7. Exécuter une commande dans un service

```bash
docker compose exec api sh
```

Cette commande exécute un processus supplémentaire dans un conteneur actif du service `api`, si l'image contient le shell demandé.

Pour consulter les variables d'environnement :

```bash
docker compose exec api env
```

Attention : cette commande peut afficher des paramètres sensibles si des secrets ont été fournis dans l'environnement. Examinez les résultats avant de les partager.

### 7.8. Exécuter une commande ponctuelle

```bash
docker compose run --rm api python -c "print('Test Compose')"
```

`docker compose run` crée un conteneur ponctuel à partir de la définition du service, en remplaçant la commande pour cette exécution.

Il ne s'agit pas de la même opération que `docker compose exec`, qui lance une commande dans un conteneur déjà actif.

### 7.9. Redémarrer un service

```bash
docker compose restart api
```

Cette commande redémarre le conteneur du service. Elle ne reconstruit pas l'image.

Si le code source a changé, un redémarrage seul ne garantit pas que les modifications soient présentes dans l'image utilisée.

### 7.10. Arrêter le projet

Pour arrêter sans supprimer :

```bash
docker compose stop
```

Pour supprimer les conteneurs et le réseau du projet :

```bash
docker compose down
```

Ces opérations n'ont pas les mêmes conséquences sur les ressources persistantes.

### 7.11. Résumé des commandes

| Commande | Fonction |
|---|---|
| `docker compose config` | Valider et afficher la configuration résolue. |
| `docker compose up -d` | Créer ou mettre à jour les services et les démarrer en arrière-plan. |
| `docker compose down` | Arrêter et supprimer les conteneurs ainsi que les réseaux gérés par le projet. |
| `docker compose build` | Construire les images des services qui possèdent une configuration de build. |
| `docker compose pull` | Télécharger les images depuis leurs registres. |
| `docker compose push` | Publier les images des services vers leurs registres. |
| `docker compose ps` | Afficher l'état des conteneurs du projet. |
| `docker compose logs` | Lire les journaux des services. |
| `docker compose exec` | Exécuter une commande dans un conteneur actif. |
| `docker compose run` | Créer un conteneur pour une commande ponctuelle. |
| `docker compose stop` | Arrêter les services sans supprimer leurs conteneurs. |
| `docker compose start` | Démarrer des conteneurs existants. |
| `docker compose restart` | Redémarrer les services concernés. |

## 8. Réseaux Compose et communication entre services

### 8.1. Le réseau par défaut

Compose crée généralement un réseau propre au projet.

Si le projet s'appelle `compteur-compose`, le réseau par défaut porte souvent un nom dérivé de ce nom de projet, suivi de `_default`.

Les conteneurs du réseau peuvent communiquer entre eux en utilisant les noms de service.

Dans notre laboratoire :

```text
API
 |
 | REDIS_HOST=redis
 |
 v
Redis
```

Le nom de service `redis` est utilisé comme nom d'hôte dans le client Python.

### 8.2. Pourquoi ne pas coder les adresses IP ?

Les adresses IP des conteneurs peuvent changer lors d'une recréation.

Un code qui dépend de l'adresse IP d'un ancien conteneur peut donc cesser de fonctionner après une mise à jour.

Il est préférable de se baser sur les noms de services ou sur les noms DNS définis dans l'architecture.

### 8.3. Port interne et port hôte

Dans :

```yaml
ports:
  - "127.0.0.1:8080:8000"
```

le port `8080` appartient à l'hôte et le port `8000` correspond au service dans le conteneur.

Les communications entre services Compose utilisent normalement le port interne du service.

Par exemple, l'API se connecte à Redis sur son port interne `6379`, pas sur un port publié de l'hôte.

### 8.4. Pourquoi ne pas publier Redis ?

Dans notre configuration, Redis n'a pas de section `ports`.

Il est donc accessible aux services connectés à son réseau Docker, selon les règles réseau du moteur, mais aucun port n'est explicitement publié sur l'hôte.

Cette configuration réduit l'exposition de Redis.

Elle ne constitue pas une protection absolue : un utilisateur ayant des droits suffisants sur le moteur Docker, ou un autre service connecté au réseau, peut encore avoir des possibilités d'accès.

En production, il faut également tenir compte de l'authentification, du chiffrement lorsque nécessaire, des permissions et de la segmentation du réseau.

### 8.5. Créer des réseaux explicites

Pour une application plus complexe, plusieurs réseaux peuvent séparer les responsabilités.

Exemple :

```yaml
services:
  frontend:
    image: nginx:alpine
    networks:
      - front_net

  api:
    image: exemple-api:1.0
    networks:
      - front_net
      - data_net

  redis:
    image: redis:7.4-alpine
    networks:
      - data_net

networks:
  front_net:
  data_net:
```

Dans cet exemple :

- Le frontal peut communiquer avec l'API.
- L'API peut communiquer avec Redis.
- Redis n'est pas attaché au réseau du frontal.

Cette séparation réduit le nombre de services qui peuvent joindre directement certains composants.

La configuration doit correspondre aux besoins réels de communication de l'application.

## 9. Santé des services et ordre de démarrage

### 9.1. Pourquoi l'ordre de démarrage est important

Lorsqu'une application dépend d'une base de données, l'ordre de création des conteneurs ne garantit pas nécessairement que la base soit prête à accepter des requêtes.

Une base peut être en cours d'initialisation après que son processus principal a démarré.

Sans contrôle de santé, une application peut tenter une connexion avant que le service ne soit disponible.

### 9.2. `depends_on` simple

Exemple :

```yaml
services:
  api:
    depends_on:
      - redis
```

Cette configuration définit une dépendance entre les services.

Elle permet de gérer l'ordre des opérations Compose, mais ne suffit pas à prouver que Redis est prêt à répondre aux commandes applicatives.

### 9.3. Contrôle de santé

Un contrôle de santé permet d'évaluer une condition définie pour un conteneur.

Exemple Redis :

```yaml
healthcheck:
  test:
    - CMD
    - redis-cli
    - ping
  interval: 5s
  timeout: 3s
  retries: 10
  start_period: 5s
```

La commande `redis-cli ping` doit recevoir une réponse valide pour que le contrôle réussisse.

Le statut du conteneur devient sain lorsque les contrôles définis réussissent selon les règles du moteur.

### 9.4. Dépendance à un service sain

```yaml
depends_on:
  redis:
    condition: service_healthy
```

Compose attend que le contrôle de santé de Redis réussisse avant de démarrer le service dépendant.

C'est plus fiable qu'une simple dépendance de démarrage lorsqu'une application exige que Redis soit prêt pour fonctionner.

### 9.5. La santé ne remplace pas la gestion des erreurs

Un service sain au moment du démarrage peut tomber en panne plus tard.

L'API doit donc gérer les erreurs de connexion et les délais d'attente.

Dans notre exemple, les appels Redis utilisent des délais d'attente explicites et retournent une réponse HTTP `503` si Redis devient indisponible.

Pour une application plus importante, il peut être nécessaire d'ajouter :

- Des tentatives de reconnexion contrôlées.
- Une politique de temporisation.
- Une gestion des erreurs.
- Une stratégie de reprise.
- Une surveillance des échecs.
- Une protection contre les cascades de défaillances.

Le contrôle de santé fournit un signal. Il n'empêche pas à lui seul l'apparition d'un incident.

### 9.6. Contrôler l'état de santé

```bash
docker compose ps
```

Les informations affichées peuvent inclure l'état de santé si les services disposent de contrôles adaptés.

Vous pouvez aussi inspecter un conteneur précis :

```bash
docker inspect NOM_DU_CONTENEUR
```

Examinez les informations relatives à l'état, aux erreurs de contrôle et aux journaux avant de modifier le fichier Compose.

## 10. Variables d'environnement et fichier `.env`

### 10.1. Pourquoi séparer la configuration du code ?

Une même application peut être exécutée dans plusieurs environnements :

- Développement.
- Test.
- Préproduction.
- Production.

Il est souhaitable d'éviter de modifier le code applicatif uniquement parce qu'un port, un nom d'hôte ou un tag d'image change.

Compose permet d'utiliser des variables pour adapter la configuration.

### 10.2. Le fichier `.env`

Un fichier `.env` peut servir à fournir les variables utilisées pour l'interpolation du fichier Compose.

Exemple :

```dotenv
IMAGE_NAME=compteur-api
IMAGE_TAG=1.0.0
APP_PORT=8080
```

Dans `compose.yaml` :

```yaml
image: ${IMAGE_NAME:-compteur-api}:${IMAGE_TAG:-dev}
```

Compose remplace les expressions par les valeurs disponibles lorsque le fichier est interprété.

Le fichier `.env` ne transmet pas automatiquement toutes ses variables à chaque conteneur. Il faut les référencer explicitement dans la configuration du service lorsque l'application doit les recevoir.

### 10.3. Différence entre interpolation et environnement du conteneur

Supposons :

```dotenv
APP_PORT=8080
```

Et :

```yaml
services:
  api:
    image: compteur-api:1.0
    ports:
      - "127.0.0.1:${APP_PORT}:8000"
```

Compose utilise `APP_PORT` pour construire la configuration du port.

Cela ne signifie pas nécessairement que la variable `APP_PORT` existe dans l'environnement du processus applicatif.

Pour transmettre une variable au conteneur :

```yaml
environment:
  APP_VERSION: "1.0.0"
```

Il faut donc distinguer :

- Les variables utilisées pour interpréter le fichier Compose.
- Les variables transmises au processus dans le conteneur.

### 10.4. Utiliser un fichier différent

Compose permet de sélectionner un fichier d'environnement :

```bash
docker compose --env-file .env.test up -d
```

On peut également utiliser plusieurs fichiers selon la configuration souhaitée, dans les limites de la syntaxe et des règles de priorité de Compose.

Exemple :

```text
.env
.env.dev
.env.test
.env.prod
```

Le choix du fichier doit être explicite dans les scripts et la documentation du projet.

### 10.5. Priorité des variables

La priorité dépend de la source et de l'usage de la variable.

Pour l'interpolation Compose, les variables présentes dans l'environnement du shell ont normalement priorité sur celles du fichier `.env` par défaut.

Il existe également des règles distinctes pour déterminer la valeur finale d'une variable transmise à un conteneur.

Lorsque les résultats semblent inattendus, utilisez :

```bash
docker compose config --environment
```

Cette commande aide à examiner les variables utilisées pour l'interpolation.

Soyez prudent : les sorties peuvent contenir des valeurs sensibles si elles ont été placées dans la configuration.

### 10.6. Secrets et `.env`

Un fichier `.env` ne constitue pas à lui seul un gestionnaire de secrets sécurisé.

Il peut être commité accidentellement, copié dans une archive, lu par un autre utilisateur ou transmis lors d'un diagnostic.

Pour les secrets de production, privilégiez les mécanismes prévus par la plateforme : gestionnaire de secrets, identités de service ou mécanismes spécifiques du runtime.

Le traitement des secrets doit être distinct de la simple configuration de paramètres tels qu'un port ou un tag d'image.

## 11. Utiliser plusieurs fichiers Compose

### 11.1. Pourquoi plusieurs fichiers ?

Une application peut nécessiter des paramètres différents selon l'environnement.

En développement, on peut vouloir :

- Reconstruire fréquemment l'image.
- Monter le code source.
- Exposer des ports de diagnostic.
- Activer des paramètres de debug.
- Ajouter des outils de test.

En production, on peut préférer :

- Utiliser des images publiées.
- Éviter les montages du code source.
- Désactiver les paramètres de debug.
- Limiter les ports exposés.
- Utiliser des paramètres de redémarrage et de ressources adaptés.

Plusieurs fichiers Compose permettent de superposer une configuration de base et des modifications propres à un environnement.

### 11.2. Fichier de base

`compose.yaml` :

```yaml
name: compteur-compose

services:
  api:
    image: ${IMAGE_NAME:-compteur-api}:${IMAGE_TAG:-dev}
    build:
      context: .
      dockerfile: Dockerfile

    environment:
      REDIS_HOST: redis
      REDIS_PORT: "6379"
      APP_VERSION: ${IMAGE_TAG:-dev}

    ports:
      - "127.0.0.1:${APP_PORT:-8080}:8000"

    depends_on:
      redis:
        condition: service_healthy

    restart: unless-stopped

  redis:
    image: redis:7.4-alpine
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Ce fichier déclare la configuration de base.

### 11.3. Fichier de développement

`compose.dev.yaml` :

```yaml
services:
  api:
    environment:
      DEBUG: "true"

    volumes:
      - type: bind
        source: .
        target: /workspace
        read_only: true
```

Ce fichier illustre une possibilité de surcharge.

Attention : le montage est réalisé ici vers `/workspace`, alors que l'application du Dockerfile s'exécute dans `/app`. Le montage seul ne modifie donc pas automatiquement le code qui est lancé.

Dans un véritable environnement de développement, il faut choisir une stratégie cohérente : montage vers le répertoire d'exécution, commande de développement adaptée ou construction de l'image à chaque modification.

### 11.4. Fichier de production

`compose.production.yaml` :

```yaml
services:
  api:
    environment:
      DEBUG: "false"

    ports:
      - "127.0.0.1:8080:8000"
```

Ce fichier est volontairement minimal et ne constitue pas une architecture de production complète.

Dans un déploiement réel, les règles d'exposition réseau, le proxy inverse, TLS, l'authentification, la persistance, la supervision et la gestion des secrets doivent être étudiés selon le contexte.

### 11.5. Combiner les fichiers

Pour le développement :

```bash
docker compose \
  -f compose.yaml \
  -f compose.dev.yaml \
  up --build -d
```

Pour utiliser la configuration de base et le fichier de production :

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  config
```

Puis, après vérification :

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  up -d
```

L'ordre des fichiers est important. Compose combine les modèles et applique les règles de fusion de configuration.

Les chemins relatifs des fichiers fusionnés sont généralement interprétés par rapport au premier fichier Compose fourni, sauf configuration spécifique.

### 11.6. Attention aux listes fusionnées

Les règles de fusion varient selon le type d'attribut.

Certains champs sont remplacés, tandis que certaines listes peuvent être fusionnées ou ajoutées.

Si un fichier supplémentaire contient une liste de ports, il ne faut pas supposer automatiquement que celle du fichier de base est supprimée.

Vérifiez systématiquement le résultat final :

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  config
```

Le résultat résolu doit correspondre à la configuration réellement souhaitée.

## 12. Les profils Compose

### 12.1. Pourquoi utiliser des profils ?

Certains services ne sont nécessaires que dans des situations particulières :

- Outils de diagnostic.
- Interface d'administration.
- Tests ponctuels.
- Génération de rapports.
- Export de données.
- Outils d'observation.
- Environnement de débogage.

Les profils permettent de déclarer ces services tout en les activant seulement lorsque cela est nécessaire.

### 12.2. Exemple

```yaml
services:
  api:
    image: compteur-api:1.0
    ports:
      - "127.0.0.1:8080:8000"

  redis:
    image: redis:7.4-alpine

  debug:
    image: alpine:3.22
    profiles:
      - debug
    command: ["sh", "-c", "echo Outil de diagnostic"]
```

Le service `debug` est associé au profil `debug`.

### 12.3. Démarrer un profil

```bash
docker compose --profile debug up -d
```

Les services sans profil particulier restent inclus dans le modèle actif, avec les services activés par le profil demandé.

### 12.4. Cas d'utilisation

Les profils permettent notamment de séparer :

```text
Utilisation normale
    |
    +-- API
    |
    +-- Redis

Utilisation de diagnostic
    |
    +-- API
    |
    +-- Redis
    |
    +-- Outils supplémentaires
```

Un service de diagnostic ne devrait pas être exposé sans contrôle sur un environnement sensible.

Les profils facilitent l'organisation de la configuration, mais ne constituent pas une frontière de sécurité en eux-mêmes.

## 13. Les registres d'images

### 13.1. Définition

Un registre d'images est un service qui stocke et distribue des images de conteneurs.

Le registre permet de partager les images entre les développeurs, les environnements de test, les pipelines CI/CD et les serveurs de déploiement.

Sans registre, une image peut être utilisée localement, mais il devient plus compliqué de la distribuer de manière organisée à plusieurs machines.

### 13.2. Les principaux registres

| Registre | Usage courant |
|---|---|
| Docker Hub | Stockage et distribution d'images publiques ou privées. |
| GitHub Container Registry | Publication d'images liées à des organisations ou dépôts GitHub. |
| GitLab Container Registry | Publication d'images associées aux projets et groupes GitLab. |
| Amazon Elastic Container Registry (ECR) | Registre intégré aux services AWS. |
| Azure Container Registry (ACR) | Registre intégré aux services Azure. |
| Google Artifact Registry | Stockage d'artefacts et d'images dans l'environnement Google Cloud. |
| Registre privé auto-hébergé | Distribution contrôlée d'images dans une infrastructure interne. |

Le choix dépend notamment du fournisseur cloud, du système CI/CD, des permissions et des règles de gouvernance.

### 13.3. Pourquoi utiliser un registre ?

Un registre permet de :

- Partager les images entre plusieurs machines.
- Centraliser les versions publiées.
- Séparer la construction de l'exécution.
- Contrôler l'accès aux images privées.
- Conserver l'historique des publications.
- Distribuer les images dans un pipeline CI/CD.
- Faciliter le déploiement sur un environnement qui n'a pas les sources de construction locales.
- S'intégrer aux mécanismes de scan et de provenance disponibles dans la plateforme.

### 13.4. Image locale et image distante

Une image locale existe dans le moteur Docker du système courant.

Une image distante est disponible auprès d'un registre.

Le fait de créer une image localement ne la publie pas automatiquement.

Il faut normalement :

1. Construire l'image.
2. Lui attribuer une référence adaptée au registre.
3. S'authentifier si nécessaire.
4. Publier l'image.
5. Vérifier que la version est disponible.

### 13.5. Schéma complet

```text
MACHINE DE DÉVELOPPEMENT
+---------------------------+
| Code et Dockerfile        |
|           |               |
|           v               |
|      docker build         |
|           |               |
|           v               |
|       Image locale        |
+---------------------------+
            |
            | tag + push
            v
+---------------------------+
| REGISTRE D'IMAGES         |
|                           |
| compteur-api:1.0.0        |
| compteur-api:1.0.1        |
+---------------------------+
            |
            | pull
            v
+---------------------------+
| SERVEUR DE DÉPLOIEMENT    |
|                           |
| Image récupérée           |
|           |               |
|           v               |
| Conteneur exécuté         |
+---------------------------+
```

Le serveur de déploiement n'a pas nécessairement besoin de reconstruire l'image. Il peut récupérer l'artefact publié et lancer les services à partir de cet artefact.

## 14. Comprendre le nom d'une image

### 14.1. Structure générale

Une référence d'image peut suivre cette structure :

```text
REGISTRE/NAMESPACE/IMAGE:TAG
```

Exemple :

```text
docker.io/equipe/compteur-api:1.0.0
```

Les composants sont :

- `docker.io` : registre Docker Hub.
- `equipe` : espace de noms de l'image.
- `compteur-api` : nom du dépôt d'image.
- `1.0.0` : tag.

Le registre, l'espace de noms, le nom et le tag doivent respecter les règles de nommage de la plateforme.

### 14.2. Docker Hub

Une image destinée au compte `monidentifiant` peut être référencée comme :

```text
monidentifiant/compteur-api:1.0.0
```

Une référence explicite peut aussi utiliser :

```text
docker.io/monidentifiant/compteur-api:1.0.0
```

Remplacez `monidentifiant` par le nom réel du compte ou de l'organisation.

### 14.3. GitHub Container Registry

Une référence typique est :

```text
ghcr.io/organisation/compteur-api:1.0.0
```

L'image est hébergée dans GitHub Container Registry.

La configuration des permissions doit permettre de publier ou de télécharger l'image selon le besoin.

### 14.4. GitLab Container Registry

Une référence peut ressembler à :

```text
registry.gitlab.com/groupe/projet/compteur-api:1.0.0
```

Le chemin exact dépend du groupe, du projet et de la configuration du registre.

### 14.5. Registre privé

Une organisation peut disposer d'un registre interne :

```text
registry.exemple.local:5000/equipe/compteur-api:1.0.0
```

Dans cette notation, `5000` est le port du registre.

Le registre doit être configuré avec les mécanismes de sécurité nécessaires, notamment une communication protégée et une gestion appropriée des identifiants.

Évitez de configurer un registre non sécurisé sans justification et sans comprendre les conséquences.

## 15. Taguer correctement les images

### 15.1. Construire avec un tag

Dans un projet dont le Dockerfile existe :

```bash
docker build -t compteur-api:1.0.0 .
```

Cette commande construit une image et lui attribue la référence `compteur-api:1.0.0`.

### 15.2. Ajouter une référence destinée au registre

```bash
docker tag compteur-api:1.0.0 MON_IDENTIFIANT/compteur-api:1.0.0
```

Remplacez `MON_IDENTIFIANT` par l'espace de noms réel.

Cette commande ajoute une nouvelle référence à l'image locale existante, sans nécessairement reconstruire son contenu.

### 15.3. Vérifier les tags

```bash
docker image ls
```

Vous pouvez voir plusieurs références qui partagent le même identifiant d'image.

Cela permet notamment de préparer plusieurs noms logiques pour la publication.

### 15.4. Ne pas considérer `latest` comme une version précise

Le tag `latest` est un nom conventionnel, pas une garantie de version.

Il peut être réaffecté à un autre contenu.

Dans un processus de livraison, utilisez des tags cohérents avec la politique de versionnement du projet et conservez les informations permettant d'identifier le contenu réellement publié.

### 15.5. Exemple de convention

```text
1.0.0
1.0.1
1.1.0
2.0.0
```

Une convention comme Semantic Versioning aide à communiquer la nature d'un changement lorsque le projet adopte cette spécification.

Il faut adapter l'interprétation des numéros aux règles du produit : toutes les applications ne suivent pas nécessairement le même modèle.

### 15.6. Tag de version et digest

Un tag est un nom qui peut être déplacé.

Un digest permet d'identifier le contenu d'une image ou d'un manifeste à partir de son empreinte cryptographique.

Exemple de forme :

```text
monidentifiant/compteur-api@sha256:IDENTIFIANT_COMPLET
```

Pour une livraison reproductible, le digest est utile lorsqu'il a été obtenu et vérifié dans le contexte du registre utilisé.

Un nom de tag est pratique pour la gestion des versions ; un digest est plus adapté à l'identification exacte d'un contenu immuable.

## 16. S'authentifier auprès d'un registre

### 16.1. Se connecter à Docker Hub

La commande générale est :

```bash
docker login
```

Pour préciser un identifiant :

```bash
docker login --username MON_IDENTIFIANT
```

La CLI peut demander les informations d'authentification selon la configuration du système.

Il est recommandé d'utiliser un mécanisme adapté de stockage des identifiants ou un jeton d'accès plutôt que de mettre un mot de passe en clair dans une commande partagée.

### 16.2. Utiliser un jeton d'accès

Pour l'automatisation, un jeton d'accès peut être utilisé avec `--password-stdin`.

Exemple sous un shell de type Unix :

```bash
printf '%s' "$DOCKERHUB_TOKEN" \
  | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
```

Les variables doivent être fournies par un mécanisme sécurisé.

Ne remplacez pas le jeton par sa valeur directement dans le fichier ou dans un script commité.

Sous PowerShell, l'équivalent peut être :

```powershell
$env:DOCKERHUB_TOKEN |
  docker login --username $env:DOCKERHUB_USERNAME --password-stdin
```

La manière de fournir et de supprimer les variables doit être adaptée à l'environnement utilisé.

### 16.3. Pourquoi utiliser `--password-stdin` ?

Cette option permet de transmettre le secret via l'entrée standard plutôt que de l'inscrire directement dans la ligne de commande.

Elle réduit certains risques liés à l'historique du shell et à l'exposition accidentelle des arguments.

Elle ne rend pas tous les environnements sûrs automatiquement. Il faut toujours contrôler les journaux, les variables et le stockage des identifiants.

### 16.4. Se connecter à GitHub Container Registry

La commande de base est :

```bash
docker login ghcr.io --username NOM_UTILISATEUR
```

Pour un pipeline, un jeton ou une méthode d'authentification autorisée par la plateforme peut être fourni via `--password-stdin`.

Les permissions requises dépendent du registre, du dépôt, du type de jeton et des règles de l'organisation.

### 16.5. Se connecter à GitLab Container Registry

La commande de base est :

```bash
docker login registry.gitlab.com
```

Les droits nécessaires dépendent de la méthode d'authentification et des permissions accordées au projet ou au groupe.

Un processus CI/CD doit utiliser un mécanisme d'identité ou des identifiants adaptés à la publication d'images, avec des droits limités.

### 16.6. Se déconnecter

```bash
docker logout
```

Pour préciser un registre :

```bash
docker logout registry.gitlab.com
```

La déconnexion peut retirer les informations d'authentification correspondantes de la configuration locale selon le mécanisme de stockage utilisé.

## 17. Publier une image vers Docker Hub

Cette section met en pratique le processus complet de publication.

### 17.1. Préparer le dépôt

Vous devez disposer :

- D'un compte Docker Hub.
- D'un dépôt d'image approprié.
- D'une image construite localement.
- D'un accès autorisé à la publication.

Pour l'application Compose de ce cours, définissez dans votre fichier `.env` un nom correspondant à votre espace de noms Docker Hub.

Exemple :

```dotenv
IMAGE_NAME=MON_IDENTIFIANT/compteur-api
IMAGE_TAG=1.0.0
APP_PORT=8080
```

Remplacez `MON_IDENTIFIANT` par le nom réel du compte ou de l'organisation.

### 17.2. Valider le modèle Compose

```bash
docker compose config
```

Vérifiez que l'image résolue utilise bien le nom prévu pour le registre.

Vous pouvez demander à Compose d'afficher les noms des images de la configuration :

```bash
docker compose config --images
```

Cette vérification est utile avant la publication.

### 17.3. Construire l'image

```bash
docker compose build api
```

Vérifiez la présence de l'image :

```bash
docker image ls
```

### 17.4. S'authentifier

```bash
docker login --username MON_IDENTIFIANT
```

Utilisez un mécanisme d'authentification adapté.

### 17.5. Publier l'image

```bash
docker compose push api
```

Compose utilise la référence définie dans la configuration du service.

La publication peut échouer si :

- Le nom d'image est incorrect.
- Le dépôt distant n'existe pas ou n'est pas accessible.
- Le registre refuse l'authentification.
- L'utilisateur ne possède pas les droits de publication.
- Le réseau est indisponible.

### 17.6. Vérifier la publication

Consultez le registre pour confirmer que le tag attendu existe.

Il est également possible de télécharger explicitement l'image :

```bash
docker pull MON_IDENTIFIANT/compteur-api:1.0.0
```

La réussite du pull confirme que le contenu référencé par ce nom est accessible avec les permissions utilisées.

### 17.7. Publier plusieurs tags

Une même image peut être associée à plusieurs tags avant publication :

```bash
docker tag \
  MON_IDENTIFIANT/compteur-api:1.0.0 \
  MON_IDENTIFIANT/compteur-api:stable
```

Puis :

```bash
docker push MON_IDENTIFIANT/compteur-api:stable
```

Le tag `stable` est seulement un exemple de convention. Il faut définir qui peut le mettre à jour et dans quelles conditions.

Pour un pipeline de production, il est préférable d'appliquer les tags dans le cadre d'un processus de publication contrôlé plutôt que d'attribuer manuellement un tag de production à une image non validée.

## 18. Utiliser les registres GitHub et GitLab

### 18.1. GitHub Container Registry

GitHub Container Registry utilise généralement des références commençant par `ghcr.io`.

Exemple :

```text
ghcr.io/organisation/compteur-api:1.0.0
```

Dans `.env` :

```dotenv
IMAGE_NAME=ghcr.io/organisation/compteur-api
IMAGE_TAG=1.0.0
APP_PORT=8080
```

Après configuration de l'authentification :

```bash
docker compose build api
docker compose push api
```

La publication dépend des permissions associées au jeton ou à l'identité utilisée.

### 18.2. GitLab Container Registry

GitLab Container Registry utilise une référence adaptée au chemin du projet.

Exemple :

```text
registry.gitlab.com/groupe/projet/compteur-api:1.0.0
```

Dans `.env` :

```dotenv
IMAGE_NAME=registry.gitlab.com/groupe/projet/compteur-api
IMAGE_TAG=1.0.0
APP_PORT=8080
```

Après authentification :

```bash
docker compose build api
docker compose push api
```

Les rôles, les jetons et les permissions du projet déterminent les opérations autorisées.

### 18.3. Comparaison

| Critère | Docker Hub | GitHub Container Registry | GitLab Container Registry |
|---|---|---|---|
| Référence typique | `docker.io/compte/image:tag` | `ghcr.io/organisation/image:tag` | `registry.gitlab.com/groupe/projet/image:tag` |
| Collaboration | Comptes et organisations Docker Hub | Intégration avec l'écosystème GitHub | Intégration avec les projets et groupes GitLab |
| Usage public | Possible selon le dépôt | Possible selon le dépôt | Possible selon la configuration |
| Usage privé | Possible selon les droits et l'offre | Possible selon les droits | Possible selon les droits |
| Automatisation | Docker CLI et CI/CD | Docker CLI et workflows CI/CD | Docker CLI et pipelines GitLab CI/CD |

Les détails des permissions et des offres peuvent évoluer. Consultez la documentation du registre concerné avant de configurer un processus de publication professionnel.

## 19. Construire et publier depuis Docker Compose

### 19.1. Le rôle de `build` et `image`

Dans un fichier Compose :

```yaml
services:
  api:
    image: monidentifiant/compteur-api:1.0.0
    build:
      context: .
      dockerfile: Dockerfile
```

`build` indique comment construire l'image.

`image` indique la référence d'image que Compose doit associer au service.

Si l'image doit être publiée dans un registre, il est important que le nom d'image soit conforme au registre cible.

### 19.2. Construire uniquement

```bash
docker compose build api
```

Cette commande construit l'image déclarée pour le service.

### 19.3. Publier uniquement

```bash
docker compose push api
```

Cette commande publie l'image déjà construite pour le service, en utilisant la référence configurée.

Elle ne remplace pas les contrôles de qualité que le pipeline doit réaliser avant la publication.

### 19.4. Télécharger les images configurées

```bash
docker compose pull
```

Cette commande récupère les images distantes définies dans le projet.

Elle est utile pour préparer une machine de déploiement lorsque les images ont déjà été publiées.

### 19.5. Éviter les erreurs de référence

Avant un build ou un push :

```bash
docker compose config --images
```

Vérifiez que les références correspondent au registre, au namespace et au tag voulus.

Une image nommée uniquement `compteur-api:1.0.0` peut être disponible localement, mais elle n'identifie pas nécessairement un dépôt distant auquel vous avez le droit de publier.

## 20. Déployer une image publiée sur une autre machine

### 20.1. Principe

Le serveur de déploiement ne doit pas nécessairement reconstruire l'image.

Le flux peut être :

```text
DÉVELOPPEMENT OU CI
        |
        v
Construction de l'image
        |
        v
Tests et contrôles
        |
        v
Publication dans le registre
        |
        v
SERVEUR DE DÉPLOIEMENT
        |
        v
Téléchargement de l'image
        |
        v
Création ou remplacement
du conteneur
        |
        v
Vérification du service
```

Cette séparation permet d'utiliser l'image validée comme artefact de livraison.

### 20.2. Préparer la machine

Le serveur doit disposer de Docker et de Docker Compose compatibles avec le projet, ainsi que de l'accès réseau nécessaire au registre.

Il doit également avoir la configuration d'exécution adaptée.

### 20.3. Récupérer l'image

Sur le serveur :

```bash
docker login
```

Puis :

```bash
docker compose pull api
```

Les identifiants doivent avoir le droit de télécharger l'image.

Pour un registre privé, vérifiez également la disponibilité du réseau, le certificat TLS et les permissions du compte.

### 20.4. Démarrer avec l'image téléchargée

Si le fichier Compose de déploiement contient une instruction `build`, utilisez un workflow qui évite de reconstruire l'image lorsqu'une construction locale n'est pas souhaitée.

Par exemple :

```bash
docker compose up -d --no-build
```

Cette commande demande à Compose de démarrer les services sans construire les images.

Vérifiez ensuite :

```bash
docker compose ps
docker compose logs api
```

Cette méthode suppose que la configuration de déploiement possède toutes les informations et les ressources nécessaires à l'exécution, et que la référence d'image correspond à celle qui a été publiée.

### 20.5. Configuration de déploiement séparée

Pour une architecture de livraison plus rigoureuse, une configuration Compose peut être partagée entre plusieurs fichiers ou adaptée à l'environnement cible.

Le fichier de base peut déclarer les services et les images, tandis qu'une configuration de développement spécifie les éléments nécessaires à la construction locale.

Il faut toutefois vérifier le modèle résolu pour s'assurer qu'aucun attribut de développement indésirable ne reste actif dans la configuration de déploiement.

### 20.6. Vérifier que la bonne version est exécutée

Ne vous contentez pas de vérifier que le conteneur fonctionne.

Conservez les informations suivantes :

- Référence d'image.
- Tag déployé.
- Digest connu de l'image.
- Identifiant du commit source.
- Résultat des tests.
- Identifiant du pipeline de publication.
- Date du déploiement.
- Environnement cible.

Ces informations facilitent les investigations en cas de régression ou de différence entre les environnements.

## 21. Comprendre les digests et la reproductibilité des images

### 21.1. Pourquoi un tag ne suffit-il pas toujours ?

Un tag peut être déplacé vers une autre image.

Par exemple :

```text
compteur-api:stable
```

peut désigner un contenu aujourd'hui puis un autre contenu lors d'une publication ultérieure.

Cela peut être pratique pour une référence de déploiement évolutive, mais ce n'est pas toujours adapté à la traçabilité d'une release.

### 21.2. Identifier une image par digest

Les références basées sur un digest ressemblent à :

```text
registre.exemple/compteur-api@sha256:DIGEST_COMPLET
```

Le digest doit être récupéré auprès du registre ou à partir des informations de publication réellement obtenues.

Pour un système qui doit exécuter exactement le contenu approuvé, il peut être préférable de déployer par digest.

### 21.3. Pourquoi la reproductibilité est importante

Une procédure de livraison doit permettre de répondre aux questions suivantes :

- Quelle image a été testée ?
- Quelle image a été publiée ?
- Quelle image tourne en production ?
- Le contenu de cette image a-t-il changé ?
- Quel code source a servi à construire l'image ?
- Quelles dépendances ont été utilisées ?
- Peut-on reconstruire ou retrouver l'artefact utilisé ?

Un tag seul ne répond pas toujours à toutes ces questions.

### 21.4. Les différents niveaux de reproductibilité

Il faut distinguer :

**La répétabilité opérationnelle.** Le même processus peut être exécuté plusieurs fois.

**La reproductibilité de construction.** La même source et les mêmes dépendances produisent un résultat identique ou suffisamment contrôlé selon les objectifs.

**La traçabilité de livraison.** Le contenu testé peut être relié à l'artefact publié puis au déploiement.

Ces objectifs sont complémentaires, mais ne doivent pas être confondus.

## 22. Construire une pipeline de publication d'images

Le processus de publication peut être automatisé dans GitHub Actions, GitLab CI/CD ou un autre système.

### 22.1. Étapes habituelles

Un pipeline peut comprendre :

1. Récupération du code.
2. Validation du Dockerfile et des fichiers Compose.
3. Exécution des tests applicatifs.
4. Construction de l'image.
5. Contrôles de sécurité.
6. Attribution des tags attendus.
7. Publication dans le registre.
8. Conservation des métadonnées et du digest.
9. Déploiement éventuel après approbation.

### 22.2. Séparer les validations de la publication

Il est souvent préférable de distinguer les workflows selon les événements.

Exemple :

```text
Pull request
     |
     v
Tests + construction
     |
     v
Résultats visibles
     |
     v
Fusion dans main
     |
     v
Tests et construction de publication
     |
     v
Scan + tag
     |
     v
Push dans le registre
     |
     v
Déploiement contrôlé
```

Une pull request provenant d'un contexte non fiable ne doit pas recevoir automatiquement les secrets nécessaires pour publier une image ou accéder à la production.

### 22.3. Exemple de workflow de validation GitHub Actions

Le fichier suivant illustre une validation qui ne publie pas l'image. Il suppose que le projet contient les fichiers de ce cours.

```yaml
name: Validation Docker Compose

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Installer Docker Compose
        run: docker compose version

      - name: Valider la configuration Compose
        run: docker compose config --quiet

      - name: Construire l'image de l'API
        run: docker compose build api
```

Les références d'actions doivent être vérifiées et maintenues selon la politique de sécurité du projet. Pour une chaîne d'approvisionnement stricte, les actions critiques peuvent être épinglées à un SHA complet et vérifié.

Ce workflow réalise la validation et la construction, mais il ne publie pas l'image dans un registre.

### 22.4. Pourquoi séparer la publication ?

La publication doit généralement être liée à un événement contrôlé, par exemple une fusion approuvée ou un tag de version.

Cela permet de réduire le risque qu'une branche de fonctionnalité publie accidentellement une image considérée comme stable.

Il faut également limiter les autorisations du jeton utilisé par le pipeline aux opérations nécessaires.

## 23. Exemple de pipeline de publication vers un registre

La publication automatisée doit être configurée selon le registre et le fournisseur CI/CD.

### 23.1. Variables et secrets

Un pipeline utilisant Docker Hub peut avoir besoin de :

- `DOCKERHUB_USERNAME` : identifiant du compte.
- `DOCKERHUB_TOKEN` : jeton autorisé à publier les images.

Ces valeurs doivent être configurées dans le gestionnaire de secrets du pipeline.

Ne les stockez pas dans le dépôt, le Dockerfile ou un fichier Compose versionné.

### 23.2. Exemple GitHub Actions

Le workflow suivant montre le principe général. Il utilise les actions officielles Docker pour configurer Buildx, s'authentifier et construire puis publier l'image.

Il suppose que les secrets `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN` sont configurés dans les paramètres du dépôt ou de l'organisation.

```yaml
name: Publication de l'image Docker

on:
  push:
    tags:
      - "v*"

permissions:
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Configurer Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Connexion à Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Construire et publier l'image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/compteur-api:${{ github.ref_name }}
```

Les références de versions des actions sont des exemples d'utilisation des actions officielles Docker. Avant de mettre ce fichier en production, vérifiez les versions disponibles et épinglez les actions selon votre politique de sécurité.

Ce workflow publie une image lorsque le push correspond à un tag Git dont le nom commence par `v`.

### 23.3. Attention à la version de tag

Si le tag Git s'appelle :

```text
v1.0.0
```

le workflow publie une image portant le tag :

```text
compteur-api:v1.0.0
```

Le tag de l'image peut être identique au tag Git, ce qui facilite la traçabilité.

Une autre politique peut retirer le préfixe `v` ou produire plusieurs tags. Dans tous les cas, définissez une convention explicite.

### 23.4. Ce que ce pipeline ne fait pas

Ce workflow ne déploie pas l'image sur un serveur.

Il ne réalise pas non plus automatiquement :

- Les tests fonctionnels de l'application.
- Un scan complet des vulnérabilités.
- L'approbation d'un déploiement.
- La validation du comportement en préproduction.
- La vérification du fonctionnement après mise en production.

Ces étapes doivent être ajoutées au processus de livraison selon le risque et les exigences du produit.

## 24. Images multi-architectures

### 24.1. Pourquoi plusieurs architectures ?

Les conteneurs peuvent être exécutés sur différentes architectures matérielles, notamment `amd64` et `arm64`.

Une image construite pour une architecture donnée n'est pas nécessairement adaptée à l'autre.

Un registre peut contenir une image associée à plusieurs variantes de plateforme, souvent réunies dans un index de manifeste.

### 24.2. Exemple de besoin

```text
                Image publiée
                      |
             +--------+--------+
             |                 |
             v                 v
          linux/amd64       linux/arm64
             |                 |
             v                 v
        Serveur x86       Serveur ARM
```

L'architecture exacte dépend de l'image et de la construction.

### 24.3. Utiliser Buildx

Buildx permet de configurer des constructions plus avancées, notamment des images multi-architectures.

Exemple de commande :

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t MON_IDENTIFIANT/compteur-api:1.0.0 \
  --push .
```

Remplacez le nom de l'image par une référence valide du registre et assurez-vous que le builder possède une configuration compatible avec les plateformes choisies.

L'option `--push` publie le résultat au registre au lieu de se limiter à une image locale classique.

### 24.4. Vérifier la compatibilité

Une image multi-architectures doit être testée sur les plateformes et environnements réellement ciblés, ou à l'aide d'une stratégie de test appropriée.

Certaines dépendances ou bibliothèques natives peuvent se comporter différemment selon l'architecture.

La simple réussite de la construction ne garantit pas que tous les scénarios d'exécution fonctionneront.

## 25. Utiliser Compose dans un environnement de production

### 25.1. Composer le projet ne suffit pas à créer une architecture de production

Docker Compose permet de gérer une application multi-conteneurs sur un hôte compatible.

Cela ne signifie pas que les besoins de haute disponibilité, de répartition de charge, de reprise après sinistre ou d'orchestration multi-hôtes sont automatiquement couverts.

Il faut évaluer les exigences opérationnelles.

### 25.2. Différences entre développement et production

En développement, il est courant d'utiliser :

- Des bind mounts du code source.
- Des paramètres de debug.
- Des ports de diagnostic.
- Des outils supplémentaires.
- Des images construites fréquemment.

En production, on privilégie souvent :

- Des images publiées et identifiées.
- Des configurations reproductibles.
- Des secrets protégés.
- Des permissions limitées.
- Une gestion de stockage appropriée.
- Des contrôles de santé.
- Une surveillance du service.
- Une procédure de mise à jour et de retour arrière documentée.

### 25.3. Ne pas reconstruire arbitrairement sur le serveur

Si l'image a été testée et publiée par un pipeline, il est généralement préférable de déployer cette image plutôt que de reconstruire à partir d'un environnement différent sur le serveur.

Une construction différente pourrait récupérer des dépendances modifiées ou produire un contenu qui n'a pas été validé.

### 25.4. Éviter les déploiements non contrôlés

La commande :

```bash
docker compose up -d
```

peut créer ou actualiser des conteneurs selon le modèle et les images disponibles.

Sur un système sensible, le déploiement doit s'appuyer sur des tags ou des digests identifiés, des validations et une stratégie de remplacement adaptée.

Il faut également prévoir comment surveiller le nouveau service et revenir à la version précédente en cas de problème.

### 25.5. Limites de Compose

Compose est souvent adapté au développement local, aux laboratoires, aux tests d'intégration et à certains déploiements sur un seul hôte.

Lorsque le service nécessite des capacités distribuées avancées, de l'auto-réparation à grande échelle, une orchestration multi-nœuds ou un système de placement complexe, une plateforme d'orchestration adaptée peut être nécessaire.

Le choix dépend des besoins réels : toutes les applications n'ont pas besoin de Kubernetes, et tous les scénarios de production ne sont pas adaptés à un simple déploiement Compose sur un seul serveur.

## 26. Bonnes pratiques d'organisation du projet

### 26.1. Structure recommandée

Une application utilisant Compose peut être organisée ainsi :

```text
mon-projet/
|
+-- app/
|   |
|   +-- app.py
|   +-- requirements.txt
|
+-- tests/
|
+-- Dockerfile
|
+-- compose.yaml
|
+-- compose.dev.yaml
|
+-- compose.production.yaml
|
+-- .dockerignore
|
+-- .gitignore
|
+-- .env.example
|
+-- README.md
```

La structure doit rester adaptée à la taille du projet. Il n'est pas nécessaire de créer tous ces fichiers dans une petite application.

### 26.2. Versionner les bons fichiers

Il est généralement utile de conserver dans Git :

- Le Dockerfile.
- Les fichiers Compose non sensibles.
- Les fichiers de dépendances.
- Le fichier `.dockerignore`.
- Le fichier `.gitignore`.
- La documentation.
- Les tests.
- Les fichiers de workflow CI/CD.

Il faut éviter de versionner des secrets, des identifiants personnels, des journaux locaux et des fichiers générés inutiles.

### 26.3. Documenter les commandes de démarrage

Le README devrait expliquer :

- Les prérequis.
- La structure du projet.
- La méthode de configuration.
- Les commandes de validation.
- La commande de démarrage.
- Les ports.
- Les données persistantes.
- La procédure d'arrêt.
- Les commandes de diagnostic.
- La manière de construire et de publier l'image.

Un projet Compose doit pouvoir être compris par une autre personne sans qu'elle ait besoin de reconstruire toutes les informations oralement.

### 26.4. Séparer les responsabilités

Chaque conteneur devrait généralement se concentrer sur une responsabilité clairement définie.

Dans notre laboratoire :

- L'API gère les requêtes HTTP.
- Redis conserve le compteur.
- Compose décrit la relation entre les services.

Cette séparation facilite la mise à jour, le diagnostic et le remplacement des composants.

Ce principe est un guide, pas une obligation absolue d'exécuter un seul processus technique par conteneur dans toutes les situations.

## 27. Diagnostic des problèmes courants

### 27.1. Erreur de syntaxe YAML

Vérifiez la configuration :

```bash
docker compose config
```

Les problèmes peuvent venir de :

- Mauvaise indentation.
- Guillemets manquants.
- Liste mal formée.
- Nom de propriété incorrect.
- Variable non résolue.
- Incompatibilité avec la spécification ou la version de Compose.

YAML utilise l'indentation pour structurer le document. Les espaces doivent donc être cohérents.

### 27.2. Image introuvable

Si Compose ne peut pas récupérer une image :

```bash
docker compose pull
```

Vérifiez ensuite :

- La référence de registre.
- Le nom du dépôt.
- Le tag.
- Les droits d'accès.
- L'authentification.
- La connectivité.
- La disponibilité de l'image pour l'architecture utilisée.

Une référence d'image erronée peut être interprétée comme le nom d'une image différente.

### 27.3. Erreur de publication dans un registre

Vérifiez :

```bash
docker login
docker image ls
docker compose config --images
```

Assurez-vous que l'image est correctement taguée et que la référence contient le registre ou l'espace de noms approprié.

Une erreur d'autorisation nécessite de vérifier le compte, le jeton et les permissions de publication.

### 27.4. Le service API ne démarre pas

Vérifiez :

```bash
docker compose ps -a
docker compose logs api
```

Puis examinez le service Redis :

```bash
docker compose logs redis
```

Confirmez que Redis a réussi son contrôle de santé.

Vérifiez aussi que les variables `REDIS_HOST` et `REDIS_PORT` correspondent à la configuration.

### 27.5. L'API ne peut pas joindre Redis

Contrôlez la configuration du service :

```bash
docker compose config
```

Puis vérifiez l'état de Redis :

```bash
docker compose ps redis
docker compose logs redis
```

La valeur attendue pour le nom d'hôte dans le laboratoire est :

```text
redis
```

Il ne faut pas utiliser `localhost` pour joindre un autre conteneur du projet : depuis l'API, `localhost` désigne le conteneur API lui-même.

### 27.6. Erreur de port déjà utilisé

Si le port 8080 est occupé, modifiez `APP_PORT` dans `.env`.

Par exemple :

```dotenv
APP_PORT=8081
```

Puis recréez ou actualisez la configuration :

```bash
docker compose up -d
```

Vérifiez les ports réellement publiés avec :

```bash
docker compose ps
```

### 27.7. Les modifications du code ne sont pas prises en compte

Si le code est copié dans l'image au moment du build, un simple redémarrage du conteneur n'actualise pas cette copie.

Reconstruisez l'image et recréez le conteneur :

```bash
docker compose build api
docker compose up -d api
```

Vérifiez ensuite les journaux et le comportement HTTP.

Dans un environnement de déploiement utilisant un registre, assurez-vous que le serveur récupère bien l'image souhaitée avant de recréer le conteneur.

### 27.8. Données perdues après une mise à jour

Vérifiez que le volume nommé est bien déclaré et monté au bon emplacement.

Examinez :

```bash
docker volume ls
docker volume inspect compteur-compose_redis_data
```

Le nom exact du volume peut varier selon le nom du projet et les paramètres Compose.

Assurez-vous que les données sont écrites dans le répertoire persistant prévu et que les opérations de nettoyage n'ont pas supprimé le volume.

### 27.9. Un conteneur est sain, mais l'application ne répond pas comme attendu

Un contrôle de santé peut vérifier une condition limitée.

Il ne garantit pas que toutes les fonctionnalités de l'application fonctionnent.

Vérifiez :

- La réponse HTTP.
- Les journaux.
- Les dépendances.
- La configuration.
- Les permissions.
- La connectivité.
- Les données.
- Les tests fonctionnels.

Il peut être nécessaire d'ajouter des tests de disponibilité et des contrôles fonctionnels distincts du healthcheck.

## 28. Sécurité des images et des registres

### 28.1. Protéger les identifiants de publication

Les jetons de publication doivent être stockés dans le système de secrets du fournisseur CI/CD ou dans un gestionnaire approprié.

Les privilèges doivent être limités au strict nécessaire.

Évitez de réutiliser un jeton administrateur global pour toutes les tâches de construction.

### 28.2. Séparer les images de test et de production

Il est utile de définir une politique de tag claire.

Exemple :

```text
compteur-api:sha-abcdef1
compteur-api:1.0.0-rc1
compteur-api:1.0.0
```

Les conventions doivent permettre d'identifier les images testées, les versions candidates et les versions officiellement publiées.

Il faut éviter qu'un tag de production soit attribué automatiquement à une image issue d'une branche non contrôlée.

### 28.3. Scanner les images

Un contrôle de vulnérabilités peut analyser l'image et ses dépendances.

Il peut notamment identifier :

- Des bibliothèques vulnérables.
- Des paquets système obsolètes.
- Certaines mauvaises pratiques.
- Des fichiers ou composants à risque.

Les scans doivent être interprétés dans leur contexte. Un rapport ne garantit pas qu'une image est totalement sécurisée.

### 28.4. Contrôler les images de base

Le choix de l'image de base influence :

- Le système de fichiers.
- Les bibliothèques présentes.
- Les versions des outils.
- La surface d'attaque.
- Le processus de mise à jour.

Choisissez une image provenant d'une source fiable et maintenez une politique d'actualisation.

### 28.5. Attention aux tags mutables

Si un tag est réutilisé pour publier une nouvelle image, le même nom peut désigner un contenu différent à des dates différentes.

Pour améliorer la traçabilité :

- Utilisez des tags de version cohérents.
- Conservez les digests publiés.
- Reliez les images aux commits source.
- Documentez les pipelines.
- Vérifiez le contenu réellement déployé.

### 28.6. Ne pas placer les secrets dans les couches

Évitez de copier des fichiers contenant des secrets dans l'image.

Un secret peut rester présent dans une couche même si un Dockerfile supprime le fichier dans une étape ultérieure.

Utilisez des mécanismes de gestion des secrets adaptés et vérifiez le contexte de build avec `.dockerignore`.

### 28.7. La sécurité couvre toute la chaîne de livraison

Le registre n'est qu'un élément de la chaîne.

Il faut aussi protéger :

- Le dépôt source.
- Le Dockerfile.
- La configuration Compose.
- Le pipeline CI/CD.
- Les secrets de publication.
- L'accès au registre.
- Les machines qui construisent les images.
- Le moteur Docker et le serveur de déploiement.

Une image valide au niveau technique ne constitue pas une preuve de sécurité globale.

## 29. Projet de fin de niveau : construire, publier et déployer une application Compose

### 29.1. Objectif

Mettre en place une application multi-conteneurs, construire son image, exécuter les services avec Compose puis publier l'image de l'API dans un registre.

Le projet doit démontrer que vous comprenez la relation entre l'application, les services, la construction d'images, le registre et le déploiement.

### 29.2. Travail demandé

1. Créer le projet `compteur-compose`.
2. Créer l'application Python qui expose `/` et `/health`.
3. Définir les dépendances dans `requirements.txt`.
4. Écrire le Dockerfile.
5. Créer `.dockerignore` et `.gitignore`.
6. Créer `.env.example` et un fichier local `.env`.
7. Écrire `compose.yaml` avec l'API et Redis.
8. Configurer le réseau par défaut et le volume Redis.
9. Ajouter les contrôles de santé.
10. Valider la configuration avec `docker compose config`.
11. Construire et démarrer les services.
12. Tester le compteur HTTP.
13. Vérifier la persistance des données.
14. Arrêter puis relancer le projet.
15. Créer un dépôt d'image dans un registre.
16. Taguer et publier l'image de l'API.
17. Télécharger la version publiée.
18. Démarrer les services à partir de l'image publiée.
19. Documenter la méthode de déploiement.
20. Vérifier les journaux et le fonctionnement final.

### 29.3. Critères de réussite

Le projet est validé si :

- Le fichier Compose est valide.
- Les services démarrent correctement.
- L'API peut communiquer avec Redis.
- Le compteur augmente lors des requêtes.
- L'endpoint `/health` reflète la disponibilité de l'application et de Redis.
- Les données persistent conformément au mécanisme défini.
- L'API est accessible sur le port prévu.
- L'image peut être construite à partir du Dockerfile.
- L'image peut être publiée dans un registre avec les droits appropriés.
- L'image publiée peut être téléchargée.
- Le déploiement utilise une référence d'image identifiable.
- Aucun secret n'est intégré au code, au Dockerfile ou à l'image.
- Les procédures d'arrêt et de nettoyage ne détruisent pas accidentellement les données importantes.

### 29.4. Améliorations facultatives

Après validation du projet de base, vous pouvez ajouter :

- Une base PostgreSQL au lieu de stocker uniquement le compteur dans Redis.
- Des tests automatisés exécutés avant la construction.
- Un pipeline CI/CD qui publie l'image uniquement sur un tag autorisé.
- Un scan de vulnérabilités de l'image.
- Une configuration Compose spécifique à la production.
- Une version multi-architectures de l'image.
- Un registre privé.
- Des réseaux distincts pour le frontal et les services internes.
- Une supervision de l'API et de Redis.
- Une procédure de retour arrière après publication.
- Une stratégie de sauvegarde et de restauration des volumes.

Chaque évolution doit être accompagnée de tests et d'une documentation appropriée.

## 30. Exercices de compréhension

### Exercice 1 : rôle de Compose

Expliquez pourquoi Docker Compose est plus adapté qu'une série de commandes `docker run` répétées lorsqu'une application contient plusieurs services.

### Exercice 2 : configuration de service

Dans le fichier suivant :

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "127.0.0.1:8080:80"

  redis:
    image: redis:7.4-alpine
```

Répondez aux questions :

1. Combien de services sont définis ?
2. Quel service publie un port sur l'hôte ?
3. Sur quel port le navigateur local peut-il accéder à Nginx ?
4. Redis est-il directement publié sur un port hôte dans cette configuration ?

### Exercice 3 : ordre de démarrage

Une API dépend d'une base PostgreSQL.

Pourquoi un simple `depends_on` peut-il être insuffisant pour garantir que les premières requêtes SQL réussissent ?

Proposez un mécanisme permettant d'améliorer la séquence de démarrage.

### Exercice 4 : variables d'environnement

Un fichier `.env` contient :

```dotenv
APP_PORT=8081
IMAGE_TAG=1.2.0
```

Le fichier Compose contient :

```yaml
ports:
  - "127.0.0.1:${APP_PORT}:8000"
```

Quel port hôte sera utilisé, si aucune autre valeur prioritaire n'est fournie ?

Le fichier `.env` transmet-il automatiquement `APP_PORT` à l'application à l'intérieur du conteneur ?

### Exercice 5 : persistance

Le projet utilise un volume nommé Redis.

Que risque-t-on si l'on exécute :

```bash
docker compose down -v
```

Pourquoi cette commande doit-elle être utilisée avec prudence ?

### Exercice 6 : publier une image

Vous avez construit l'image locale :

```text
compteur-api:1.0.0
```

Vous souhaitez la publier sur Docker Hub dans votre compte `monidentifiant`.

Écrivez les commandes nécessaires pour lui attribuer une référence distante puis la publier.

### Exercice 7 : tag et digest

Quelle est la différence entre :

```text
monidentifiant/compteur-api:1.0.0
```

et :

```text
monidentifiant/compteur-api@sha256:DIGEST_COMPLET
```

Pourquoi le digest est-il utile dans un processus de livraison contrôlé ?

### Exercice 8 : erreur de réseau

Une application Python tente de joindre Redis sur `localhost:6379`, mais elle échoue.

Les deux services fonctionnent dans des conteneurs distincts et partagent le réseau Compose par défaut.

Quelle valeur devrait normalement être utilisée comme nom d'hôte pour joindre Redis ?

### Exercice 9 : image reconstruite

Vous reconstruisez l'image de l'API avec le même nom et le même tag, mais le conteneur actif conserve l'ancien comportement.

Pourquoi cela peut-il se produire ?

Quelles opérations permettent de démarrer un conteneur basé sur la nouvelle image ?

### Exercice 10 : publication CI/CD

Une pull request non fusionnée peut déclencher une construction d'image.

Pourquoi ne devrait-elle pas recevoir automatiquement les secrets de production nécessaires à la publication ou au déploiement ?

### Exercice 11 : contrôle de santé

Le processus Redis est démarré, mais il n'est pas encore prêt à répondre aux requêtes.

Expliquez comment un `healthcheck` associé à `condition: service_healthy` peut aider à gérer ce cas.

### Exercice 12 : déploiement reproductible

Un serveur déploie chaque fois l'image `compteur-api:stable`.

Pourquoi ce tag peut-il être insuffisant pour retrouver exactement la version qui était en production la semaine dernière ?

Quelle information supplémentaire faut-il conserver ?

## 31. Corrigés des exercices

### Corrigé 1

Compose centralise les paramètres de l'application, ses dépendances, ses réseaux, ses volumes et ses contrôles. Il permet de démarrer, de diagnostiquer et d'arrêter les services de manière cohérente.

Cela réduit le risque de divergence entre les commandes manuelles utilisées par les développeurs et celles utilisées pour l'exploitation.

### Corrigé 2

1. Deux services sont définis : `web` et `redis`.
2. `web` publie un port sur l'hôte.
3. Le navigateur local peut accéder à Nginx sur `127.0.0.1:8080`.
4. Redis n'a pas de section `ports`, donc aucun port n'est explicitement publié sur l'hôte.

### Corrigé 3

Une dépendance simple permet de gérer l'ordre de démarrage, mais n'attend pas nécessairement que PostgreSQL soit prêt à recevoir des connexions.

Il est possible d'ajouter un contrôle de santé, puis de configurer la dépendance avec `condition: service_healthy`, en utilisant une commande de vérification adaptée à PostgreSQL.

### Corrigé 4

Le port hôte sera `8081`, dans les conditions indiquées.

Le fichier `.env` sert ici à l'interpolation du fichier Compose. Il ne transmet pas automatiquement `APP_PORT` au processus applicatif. Pour transmettre une variable, il faut la définir dans l'environnement du service ou la fournir avec un mécanisme adapté.

### Corrigé 5

`docker compose down -v` supprime les volumes nommés déclarés par le projet, lorsque les conditions de suppression sont réunies.

Les données stockées dans ces volumes peuvent être perdues. Il faut vérifier leur contenu et les sauvegardes avant d'utiliser cette commande.

### Corrigé 6

Pour Docker Hub :

```bash
docker tag \
  compteur-api:1.0.0 \
  monidentifiant/compteur-api:1.0.0
```

Puis, après authentification :

```bash
docker push monidentifiant/compteur-api:1.0.0
```

### Corrigé 7

Le premier exemple utilise un tag, qui constitue un nom de version logique et peut être réaffecté.

Le deuxième utilise un digest pour identifier précisément un contenu de registre.

Le digest facilite la traçabilité et aide à garantir que le contenu référencé est celui qui a été validé.

### Corrigé 8

L'application devrait normalement utiliser :

```text
redis:6379
```

Le nom `redis` correspond au service Compose. `localhost` désigne le conteneur API lui-même dans ce contexte, pas le conteneur Redis.

### Corrigé 9

La reconstruction modifie l'image locale, mais les conteneurs existants ne changent pas automatiquement leur couche de base.

Pour utiliser la nouvelle image :

```bash
docker compose build api
docker compose up -d api
```

Il faut ensuite vérifier l'état, les journaux et le comportement de l'API.

### Corrigé 10

Une pull request peut exécuter du code dont le contenu n'est pas encore approuvé.

Les secrets de production pourraient être exposés à ce code, notamment si une modification malveillante tente de les lire ou de les transmettre ailleurs.

Il faut séparer les validations non fiables des tâches privilégiées de publication, limiter les permissions et ne rendre accessibles que les secrets nécessaires dans un contexte de confiance approprié.

### Corrigé 11

Le contrôle de santé exécute une vérification définie pour le service.

Lorsque la dépendance est configurée avec `condition: service_healthy`, Compose attend que le contrôle de santé réussisse avant de démarrer le service dépendant.

Cela permet d'éviter certains échecs liés à une dépendance qui n'est pas encore prête. Les erreurs survenant après le démarrage doivent toutefois être gérées par l'application.

### Corrigé 12

Le tag `stable` peut être réaffecté à une nouvelle image.

Pour retrouver exactement le contenu déployé, il faut conserver l'identifiant de l'image ou le digest, la référence de publication, le commit source et les informations de livraison associées.

## 32. Glossaire essentiel

**Build context :** ensemble de fichiers transmis au moteur de construction et disponibles pour les instructions du Dockerfile.

**Compose Specification :** spécification utilisée pour décrire les applications multi-conteneurs dans les fichiers Compose modernes.

**Conteneur :** instance créée à partir d'une image.

**Digest :** identifiant de contenu utilisé pour référencer précisément une image ou un manifeste.

**Docker Compose :** outil permettant de définir et de gérer une application multi-conteneurs.

**Docker Hub :** service de registre d'images Docker.

**Dockerfile :** fichier décrivant les étapes de construction d'une image.

**Healthcheck :** contrôle qui évalue un état de santé défini pour un conteneur.

**Image :** modèle contenant les fichiers et les métadonnées utilisés pour créer un conteneur.

**Image tag :** référence nommée d'une image, souvent utilisée pour identifier une version logique.

**Interpolation :** remplacement de variables par leurs valeurs dans la configuration Compose.

**Registre :** service qui stocke et distribue les images.

**Service Compose :** définition d'un composant de l'application, utilisée pour gérer un ou plusieurs conteneurs.

**Volume :** stockage géré par Docker permettant de conserver des données indépendamment du cycle de vie habituel des conteneurs.

**Réseau Compose :** réseau qui permet aux services d'un projet de communiquer selon la configuration définie.

**`.dockerignore` :** fichier qui exclut certains éléments du contexte de construction.

**`.env` :** fichier généralement utilisé pour fournir des variables d'interpolation à Compose.

**`depends_on` :** attribut permettant de déclarer les dépendances et l'ordre de traitement des services.

**`docker compose build` :** commande qui construit les images des services ayant une configuration de build.

**`docker compose config` :** commande qui parse et résout la configuration Compose.

**`docker compose down` :** commande qui arrête et supprime les ressources du projet prévues par Compose, avec des options supplémentaires pour certaines catégories de ressources.

**`docker compose pull` :** commande qui récupère les images depuis les registres.

**`docker compose push` :** commande qui publie les images des services vers leurs registres respectifs.

**`docker compose up` :** commande qui crée ou met à jour les ressources nécessaires et démarre les services.

## 33. Références officielles pour approfondir

### Docker Compose

- Documentation générale Docker Compose : https://docs.docker.com/compose/
- Présentation du modèle d'application Compose : https://docs.docker.com/compose/intro/compose-application-model/
- Référence de la spécification Compose : https://docs.docker.com/reference/compose-file/
- Documentation CLI Compose : https://docs.docker.com/reference/cli/docker/compose/
- Référence `docker compose config` : https://docs.docker.com/reference/cli/docker/compose/config/
- Référence `docker compose ps` : https://docs.docker.com/reference/cli/docker/compose/ps/
- Référence `docker compose logs` : https://docs.docker.com/reference/cli/docker/compose/logs/
- Contrôle de l'ordre de démarrage des services : https://docs.docker.com/compose/how-tos/startup-order/
- Réseau dans Compose : https://docs.docker.com/compose/how-tos/networking/
- Utilisation de variables d'environnement : https://docs.docker.com/compose/how-tos/environment-variables/
- Interpolation des variables : https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation
- Utilisation de plusieurs fichiers Compose : https://docs.docker.com/compose/how-tos/multiple-compose-files/
- Utilisation de Compose en production : https://docs.docker.com/compose/how-tos/production/
- Bonnes pratiques de construction : https://docs.docker.com/build/building/best-practices/

### Images et registres

- Référence `docker image tag` : https://docs.docker.com/reference/cli/docker/image/tag/
- Référence `docker image push` : https://docs.docker.com/reference/cli/docker/image/push/
- Référence `docker login` : https://docs.docker.com/reference/cli/docker/login/
- Documentation Docker Hub : https://docs.docker.com/docker-hub/
- Docker Build avec GitHub Actions : https://docs.docker.com/build/ci/github-actions/
- GitHub Container Registry : https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- GitLab Container Registry : https://docs.gitlab.com/user/packages/container_registry/

### Python et dépendances

- Documentation officielle Flask : https://flask.palletsprojects.com/
- Documentation du client Python Redis : https://redis.readthedocs.io/
- Documentation Gunicorn : https://gunicorn.org/

Les documentations officielles restent les références à consulter pour vérifier les options exactes, les permissions, les règles de sécurité et les comportements des versions utilisées.

## 34. Synthèse du niveau intermédiaire

Docker Compose permet de décrire et de gérer plusieurs services dans un même projet. Il centralise les images, les paramètres d'exécution, les réseaux, les volumes, les dépendances et les contrôles de santé.

Les points essentiels à retenir sont les suivants.

**Un service Compose n'est pas un registre.** Compose gère les composants de l'application, tandis que le registre stocke les images destinées à être distribuées.

**Le nom de service constitue généralement la référence réseau à privilégier.** Dans notre laboratoire, l'API communique avec Redis via le nom `redis`, sans dépendre d'une adresse IP fixe.

**Le démarrage n'est pas toujours synonyme de disponibilité.** Les contrôles de santé et les dépendances conditionnelles améliorent l'ordre de démarrage, mais chaque application doit aussi gérer les erreurs et les indisponibilités ultérieures.

**Les données persistantes doivent être séparées du cycle de vie des conteneurs.** Les volumes permettent de conserver les données lorsque les conteneurs sont recréés, mais leur suppression peut entraîner une perte de données.

**Le fichier `.env` ne remplace pas un gestionnaire de secrets.** Il faut distinguer l'interpolation des variables, l'environnement des processus et le stockage sécurisé des informations sensibles.

**Un registre permet de séparer la construction de l'exécution.** Une image testée peut être publiée, téléchargée sur un autre système et utilisée pour créer un conteneur.

**Les tags et les digests n'ont pas le même rôle.** Un tag est pratique pour désigner une version logique, tandis qu'un digest permet d'identifier plus précisément un contenu.

**La publication doit être contrôlée.** Les pipelines doivent valider l'image, limiter les permissions, protéger les identifiants et éviter d'exposer les secrets à des travaux non fiables.

Enfin, un processus de livraison professionnel doit relier le code source, l'image construite, les contrôles réalisés, la référence publiée et le déploiement effectif.

La prochaine étape consiste à approfondir l'optimisation des Dockerfiles, les constructions multi-stage, les images plus petites, la gestion avancée des secrets, la sécurité de la chaîne d'approvisionnement et l'intégration de Docker dans un pipeline CI/CD complet.