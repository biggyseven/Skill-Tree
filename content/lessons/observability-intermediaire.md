# Observabilité : Prometheus et Grafana

## 1. Positionnement dans le parcours DevOps

Ce cours de niveau intermédiaire prolonge les compétences travaillées dans les modules précédents :

- **Git** : versionner les configurations et les règles de supervision.
- **Docker et Compose** : lancer les composants d’observabilité et les services surveillés.
- **Kubernetes** : surveiller les applications, les pods et les nœuds d’un cluster.
- **CI/CD avec GitHub Actions et GitLab CI** : valider automatiquement les configurations avant leur intégration.
- **Terraform** : préparer les ressources d’infrastructure qui hébergeront les outils de supervision.
- **Ansible** : déployer et configurer les agents sur les serveurs.

L’objectif est d’apprendre à construire une chaîne de supervision cohérente, et non de considérer Prometheus et Grafana comme deux outils isolés.

### 1.1 Prérequis

Il est recommandé de connaître :

- Les commandes Linux fondamentales.
- Les notions d’adresse IP, de port TCP, de DNS et de pare-feu.
- Les bases de Git.
- Les concepts d’image, de conteneur, de volume et de réseau Docker.
- Les notions de service, de déploiement et de pod Kubernetes.
- Les principes élémentaires d’un pipeline CI/CD.
- Les fichiers YAML et les variables d’environnement.

Une connaissance préalable de Prometheus ou de Grafana est utile, mais les notions nécessaires sont rappelées dans ce cours.

### 1.2 Objectifs pédagogiques

À la fin de cette formation, il faudra être capable de :

1. Concevoir une architecture de collecte de métriques.
2. Exposer et récupérer les métriques d’un serveur ou d’une application.
3. Configurer les cibles de collecte de Prometheus.
4. Comprendre les types de métriques et leurs étiquettes.
5. Écrire des requêtes PromQL intermédiaires.
6. Construire un tableau de bord Grafana pertinent.
7. Écrire des règles d’alerte et comprendre le rôle d’Alertmanager.
8. Diagnostiquer une cible inaccessible ou une métrique absente.
9. Versionner la configuration de supervision et la valider par CI/CD.
10. Préparer l’intégration avec Kubernetes.
11. Appliquer les principes de sécurité, de rétention et de maîtrise de la cardinalité.

## 2. Monitoring, observabilité et supervision

### 2.1 Qu’est-ce que le monitoring ?

Le monitoring, ou supervision, consiste à mesurer l’état d’un système à partir d’indicateurs prédéfinis.

Exemples :

- Le processeur est-il fortement sollicité ?
- L’espace disque disponible diminue-t-il ?
- L’application répond-elle aux requêtes HTTP ?
- Le nombre d’erreurs augmente-t-il ?
- Une instance est-elle inaccessible ?

Le monitoring aide à répondre à des questions connues à l’avance.

### 2.2 Qu’est-ce que l’observabilité ?

L’observabilité désigne la capacité à comprendre l’état interne d’un système à partir des données qu’il expose.

Elle s’appuie couramment sur trois familles de données :

| Donnée | Question principale | Exemple |
|---|---|---|
| Métriques | Que se passe-t-il et à quelle fréquence ? | Le taux d’erreurs HTTP atteint 8 %. |
| Journaux (logs) | Quels événements se sont produits ? | Une connexion à la base de données a échoué. |
| Traces distribuées | Où le temps est-il consommé dans une requête ? | L’appel au service de paiement prend 1,8 seconde. |

Prometheus est principalement destiné aux métriques. Grafana permet de les explorer et de les visualiser, mais il peut aussi interroger d’autres sources, notamment des plateformes de logs et de traces.

**À retenir :** les métriques révèlent une anomalie, les logs donnent des événements détaillés et les traces aident à comprendre le parcours d’une requête.

### 2.3 Exemple d’incident

Une application devient lente.

Une démarche efficace est la suivante :

1. Grafana révèle que le percentile 95 du temps de réponse augmente.
2. Prometheus montre que la latence augmente au même moment que le nombre de requêtes.
3. Les logs montrent des erreurs de connexion à la base de données.
4. Une trace distribuée révèle que l’attente se concentre sur la requête SQL.
5. L’équipe vérifie les connexions, les requêtes lentes et les ressources de la base.

Aucun outil ne donne nécessairement toute la réponse. La valeur vient de la corrélation des signaux.

## 3. Architecture de référence

### 3.1 Rôle des composants

**Prometheus** collecte, stocke et interroge des séries temporelles. Il récupère généralement les métriques en interrogeant périodiquement les endpoints exposant ces données.

**Exporters** rendent accessibles les métriques de systèmes qui ne les exposent pas directement sous le format attendu. `node_exporter`, par exemple, expose de nombreuses métriques relatives à un système Linux.

**Grafana** interroge les sources de données, construit les tableaux de bord et permet de configurer des alertes selon le mode de gestion retenu.

**Alertmanager** reçoit les alertes générées par les règles Prometheus et gère leur regroupement, leur routage, les silences, les inhibitions et les notifications.

### 3.2 Schéma d'architecture

```text
                         ADMINISTRATEUR
                               |
                               v
                    +---------------------+
                    |       Grafana       |
                    | Tableaux de bord    |
                    | Exploration métrique|
                    +----------+----------+
                               |
                         Requêtes PromQL
                               |
                               v
                    +---------------------+
                    |     Prometheus      |
                    |                     |
                    |  Collecte périodique|
                    |  TSDB / historique  |
                    |  PromQL / règles    |
                    +--+---------------+-+
                       |               |
             Scraping  |               | Alertes
                       |               v
               +-------+-----+  +----------------+
               |             |  |  Alertmanager  |
               v             |  | Regroupement   |
       +----------------+    |  | Routage        |
       |  node_exporter |    |  | Notifications  |
       +----------------+    |  +----------------+
                             |
                             v
                    +------------------+
                    | Endpoint /metrics|
                    | d'une application|
                    +------------------+
```

Le flux principal est le suivant :

1. Les applications et les exporters exposent leurs métriques.
2. Prometheus interroge les cibles selon une fréquence configurée.
3. Les valeurs récupérées sont stockées dans sa base de séries temporelles.
4. PromQL permet d'extraire et de calculer des indicateurs.
5. Grafana affiche les résultats.
6. Les règles d'alerte évaluent certaines conditions.
7. Alertmanager peut ensuite acheminer les alertes vers les destinataires configurés.

Prometheus peut évaluer les alertes sans envoyer de notification. L'envoi effectif nécessite un système de notification configuré.

## 4. Le modèle de données de Prometheus

### 4.1 Une série temporelle

Prometheus stocke des séries temporelles. Une série est identifiée par un nom de métrique et un ensemble d'étiquettes.

Exemple :

```text
http_requests_total{
    job="api",
    instance="10.0.0.12:8080",
    method="GET",
    status="200"
}
```

Cette série représente un compteur de requêtes HTTP correspondant aux étiquettes indiquées.

Chaque combinaison différente de nom de métrique et d'étiquettes forme une série distincte.

Par exemple :

```text
http_requests_total{method="GET",status="200"}
http_requests_total{method="GET",status="500"}
http_requests_total{method="POST",status="200"}
```

Il s'agit du même nom de métrique, mais de trois séries différentes.

### 4.2 Les étiquettes essentielles

Prometheus ajoute généralement des étiquettes comme :

- `job` : nom du travail de collecte.
- `instance` : identification de la cible, souvent son adresse et son port.
- Des étiquettes métier, telles que `method`, `status`, `service` ou `environment`, selon l'instrumentation.

Exemple :

```text
job="api"
instance="10.0.0.12:8080"
environment="production"
```

Les étiquettes facilitent le filtrage et l'agrégation.

### 4.3 Cardinalité

La cardinalité correspond au nombre de séries temporelles distinctes produites par une métrique ou un ensemble de métriques.

Elle peut rapidement augmenter lorsque plusieurs étiquettes sont combinées.

Exemple :

```text
http_requests_total{
    user_id="1001"
}
```

Un identifiant utilisateur peut prendre des milliers ou des millions de valeurs. En l'utilisant comme étiquette, l'application peut créer un nombre très important de séries.

Éviter comme étiquettes les données à forte cardinalité non maîtrisée :

- Identifiants de requêtes uniques.
- Adresses e-mail.
- Identifiants de session.
- URL complètes comportant des identifiants dynamiques.
- Identifiants individuels d'utilisateurs.

Une solution consiste à regrouper les routes par modèle :

```text
route="/users/{id}"
```

au lieu de créer une série différente pour chaque URL :

```text
route="/users/1001"
route="/users/1002"
route="/users/1003"
```

Les valeurs à forte cardinalité sont généralement mieux adaptées aux logs ou aux traces lorsqu'elles sont nécessaires à l'investigation.

## 5. Les types de métriques

### 5.1 Counter : compteur cumulatif

Un compteur augmente au fil des événements. Il est normalement réinitialisé lors d'un redémarrage ou du renouvellement de l'instrumentation.

Exemples :

```text
http_requests_total
process_cpu_seconds_total
```

Il ne faut généralement pas interpréter directement sa valeur cumulée comme un débit.

Pour estimer la vitesse d'augmentation d'un compteur, on utilise `rate()`.

```promql
rate(http_requests_total[5m])
```

Cette requête estime le nombre moyen de requêtes par seconde sur les cinq dernières minutes, pour chaque série correspondante.

### 5.2 Gauge : valeur instantanée

Une jauge peut augmenter ou diminuer.

Exemples :

```text
node_memory_MemAvailable_bytes
node_load1
process_open_fds
```

Une jauge peut représenter une utilisation mémoire, un nombre de connexions actives ou un espace disponible.

On peut la sélectionner directement :

```promql
node_memory_MemAvailable_bytes
```

Il ne faut pas utiliser `rate()` sur une jauge ordinaire pour mesurer sa valeur. `rate()` est principalement destiné aux compteurs.

### 5.3 Histogram : distribution d'observations

Un histogramme représente une distribution d'observations, notamment des durées ou des tailles.

Un histogramme classique de latence peut exposer des séries telles que :

```text
http_request_duration_seconds_bucket{le="0.1"}
http_request_duration_seconds_bucket{le="0.5"}
http_request_duration_seconds_bucket{le="1"}
http_request_duration_seconds_bucket{le="+Inf"}
http_request_duration_seconds_sum
http_request_duration_seconds_count
```

Les buckets représentent des limites cumulatives. L'étiquette spéciale `le` indique la limite supérieure.

Les histogrammes sont utiles pour calculer des quantiles à partir de buckets adaptés.

### 5.4 Summary : résumé statistique

Un Summary expose généralement un compte, une somme et, selon son instrumentation, certains quantiles calculés par l'application cliente.

Il ne se comporte pas exactement comme un histogramme. En particulier, il n'est généralement pas possible d'agréger simplement les quantiles pré-calculés de plusieurs instances pour obtenir un quantile global correct.

Lorsque des quantiles agrégés sont nécessaires, un histogramme avec des buckets bien choisis est souvent plus adapté.

### 5.5 Tableau récapitulatif

| Type | Signification | Exemple d'utilisation |
|---|---|---|
| Counter | Total cumulatif | Nombre de requêtes traitées |
| Gauge | Valeur instantanée | Mémoire disponible |
| Histogram | Distribution par buckets | Latences HTTP |
| Summary | Résumé calculé côté client | Distribution locale d'observations |

### 5.6 Conventions de nommage

Favoriser :

- Des noms explicites.
- Une unité cohérente.
- Les unités de base, par exemple les secondes et les octets.
- Le suffixe `_total` pour les compteurs cumulatifs.
- Des étiquettes pour les dimensions variables, plutôt que des noms de métriques construits dynamiquement.

Exemples :

```text
api_http_requests_total
api_request_duration_seconds
worker_queue_items
database_connections_active
```

Une métrique doit représenter une quantité cohérente. Éviter de mélanger plusieurs grandeurs sans rapport dans une même métrique.

## 6. Préparer le laboratoire Docker

Le laboratoire de ce cours utilise Docker Compose pour lancer Prometheus et Grafana.

Il est conçu en priorité pour un hôte Linux utilisant Docker Engine. `node_exporter` utilise ici le réseau et l'espace des processus de l'hôte pour recueillir les métriques système. Sur Docker Desktop, les métriques obtenues peuvent correspondre à l'environnement Linux de la machine virtuelle Docker plutôt qu'au système d'exploitation de l'ordinateur hôte.

### 6.1 Arborescence du projet

Créer la structure suivante :

```text
observability/
├── compose.yaml
├── .env
├── .gitignore
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
│       ├── recording.yml
│       └── alerts.yml
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── prometheus.yml
        └── dashboards/
            └── dashboards.yml
```

Cette structure sépare les responsabilités :

- `compose.yaml` décrit les services et leurs volumes.
- `prometheus/prometheus.yml` configure la collecte.
- `prometheus/rules/` contient les règles de calcul et d'alerte.
- `grafana/provisioning/` déclare la source de données et le chargement des tableaux de bord.

Cette organisation prépare aussi la mise sous Git.

### 6.2 Fichier `.env`

Créer le fichier `.env` à la racine du projet :

```dotenv
GRAFANA_ADMIN_PASSWORD=ChangerCeMotDePassePourLeLaboratoire
```

Ce mot de passe est un exemple à remplacer avant l'exécution.

Ne pas publier ce fichier dans un dépôt Git. Le mot de passe présenté ici est une valeur de démonstration ; il ne doit pas être réutilisé en production.

### 6.3 Fichier `.gitignore`

Créer le fichier `.gitignore` :

```gitignore
.env
*.log
.DS_Store
```

Le fichier `.env` reste local à l'environnement d'exécution.

En production, préférer un gestionnaire de secrets ou un mécanisme sécurisé de déploiement des secrets plutôt qu'un mot de passe stocké en clair dans le dépôt.

## 7. Lancer Prometheus et Grafana

### 7.1 Fichier `compose.yaml`

Créer le fichier suivant dans le dossier `observability/` :

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --storage.tsdb.retention.time=15d
      - --web.enable-lifecycle
    ports:
      - "127.0.0.1:9090:9090"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./prometheus/rules:/etc/prometheus/rules:ro
      - prometheus_data:/prometheus
    depends_on:
      - node-exporter

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    network_mode: host
    pid: host
    command:
      - --path.rootfs=/host
    volumes:
      - /:/host:ro,rslave

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD:?Definir GRAFANA_ADMIN_PASSWORD dans le fichier .env}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
```

Dans ce laboratoire, les tags `latest` facilitent une première mise en route, mais ne garantissent pas des déploiements reproductibles. En production, utiliser des versions explicitement choisies et testées, voire des digests d'images, puis les mettre à jour selon une procédure maîtrisée.

L'activation de `--web.enable-lifecycle` permet le rechargement de configuration par l'API de cycle de vie. L'endpoint correspondant ne doit pas être rendu accessible à des utilisateurs non autorisés.

Les ports Web de Prometheus et de Grafana sont liés à l'adresse de boucle locale. Ils ne sont donc pas directement publiés sur toutes les interfaces réseau de l'hôte.

Le conteneur `node-exporter` utilise le réseau hôte. En conséquence, il ne faut pas lui ajouter de section `ports:` ou de réseau Compose classique.

### 7.2 Expliquer les volumes et les ports

Le volume `prometheus_data` conserve les données Prometheus en dehors du cycle de vie du conteneur.

Le volume `grafana_data` conserve notamment les données locales de Grafana.

Les montages de configuration sont en lecture seule :

```yaml
volumes:
  - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

Le suffixe `:ro` évite que le conteneur modifie ce fichier de configuration.

Les ports sont les suivants :

| Port | Service | Usage |
|---|---|---|
| 9090 | Prometheus | Interface Web et API |
| 3000 | Grafana | Tableaux de bord |
| 9100 | node_exporter | Endpoint de métriques système |

Le port `9100` n'est pas publié par un mapping Compose dans cet exemple : `node_exporter` utilise le réseau de l'hôte. Sur Linux, Prometheus utilise l'entrée `host.docker.internal` associée à `host-gateway` pour joindre ce service.

La configuration doit être adaptée si l'environnement utilise une autre topologie réseau.

### 7.3 Démarrer les services

Depuis le dossier contenant `compose.yaml` :

```bash
docker compose config
docker compose pull
docker compose up -d
docker compose ps
```

`docker compose config` vérifie et affiche la configuration Compose résolue. Il ne remplace pas tous les contrôles d'exécution.

Afficher les journaux :

```bash
docker compose logs -f prometheus
docker compose logs -f grafana
docker compose logs -f node-exporter
```

Contrôler les états :

```bash
docker inspect prometheus
docker inspect grafana
```

### 7.4 Accéder aux interfaces

Ouvrir :

- Prometheus : `http://localhost:9090`
- Grafana : `http://localhost:3000`

Se connecter à Grafana avec le compte défini dans Compose.

La source de données sera provisionnée dans une section suivante. Tant que les fichiers de configuration ne sont pas tous présents, il peut être nécessaire de compléter le projet avant que le démarrage soit pleinement fonctionnel.

## 8. Configurer la collecte Prometheus

### 8.1 Fichier `prometheus/prometheus.yml`

Créer le fichier suivant :

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets:
          - prometheus:9090

  - job_name: node
    scrape_interval: 15s
    static_configs:
      - targets:
          - host.docker.internal:9100
```

### 8.2 Comprendre la configuration

#### `global`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
```

`scrape_interval` détermine la fréquence de collecte par défaut.

`evaluation_interval` détermine la fréquence d'évaluation des règles.

Une fréquence plus faible améliore parfois la résolution temporelle, mais augmente le volume de données, le travail de collecte et les coûts de calcul.

#### `rule_files`

```yaml
rule_files:
  - /etc/prometheus/rules/*.yml
```

Prometheus charge les fichiers de règles correspondant à ce chemin.

Les règles servent à pré-calculer des métriques ou à déclencher des états d'alerte.

#### `scrape_configs`

Chaque travail de collecte, ou job, décrit comment découvrir et interroger un ensemble de cibles.

Dans cet exemple :

- `prometheus` surveille le serveur Prometheus lui-même.
- `node` surveille les métriques exposées par `node_exporter`.

Les noms des jobs sont aussi utilisés comme étiquette `job`.

### 8.3 Pourquoi les adresses sont différentes

Prometheus et Grafana communiquent sur le réseau Compose. Prometheus peut donc joindre le service `prometheus` par son nom DNS de service.

`node_exporter`, en revanche, partage le réseau de l'hôte dans ce laboratoire. Prometheus le joint par l'adresse `host.docker.internal:9100`.

Ne pas confondre :

- `localhost` dans un conteneur, qui désigne généralement ce conteneur lui-même.
- Le nom DNS d'un service Compose, qui désigne un service du réseau Compose.
- L'adresse de l'hôte, qui dépend de l'environnement réseau.

Cette distinction est fondamentale pour résoudre les erreurs de collecte.

### 8.4 Valider la configuration

Lorsqu'un fichier de configuration a été modifié, exécuter :

```bash
docker compose exec prometheus \
  promtool check config /etc/prometheus/prometheus.yml
```

Si la configuration est valide, `promtool` affiche un résultat de validation positif.

Le même outil peut valider les fichiers de règles :

```bash
docker compose exec prometheus \
  promtool check rules /etc/prometheus/rules/alerts.yml \
  /etc/prometheus/rules/recording.yml
```

Les chemins doivent correspondre aux fichiers présents dans le conteneur.

### 8.5 Recharger la configuration

Avec le cycle de vie Web activé dans ce laboratoire :

```bash
curl -X POST http://localhost:9090/-/reload
```

La requête demande à Prometheus de recharger la configuration et les règles.

Si les nouveaux fichiers sont invalides, la nouvelle configuration ne doit pas être considérée comme appliquée avec succès. Toujours consulter les journaux et les pages d'état.

En production, l'endpoint de rechargement doit rester protégé, et le rechargement doit faire partie d'une procédure de déploiement contrôlée.

## 9. Vérifier les cibles et les métriques

### 9.1 Vérifier les cibles

Dans Prometheus, ouvrir :

`http://localhost:9090/targets`

La page indique l'état de chaque cible. Une cible saine apparaît généralement dans l'état `UP`. Une cible inaccessible ou dont la collecte échoue peut apparaître `DOWN`.

Une cible `UP` signifie que la collecte a réussi au dernier contrôle. Cela ne prouve pas que l'application surveillée est fonctionnelle du point de vue utilisateur.

### 9.2 Vérifier les métriques de Prometheus

Dans l'interface de requête, exécuter :

```promql
up
```

Prometheus expose cette métrique pour indiquer si la dernière collecte a réussi :

- `1` : collecte réussie.
- `0` : échec de la dernière collecte pour la série concernée.

Filtrer un job :

```promql
up{job="node"}
```

Vérifier ensuite :

```promql
node_memory_MemAvailable_bytes
```

Cette métrique fournit la mémoire disponible mesurée par `node_exporter` sous Linux.

Pour consulter l'endpoint de métriques lui-même :

```bash
curl http://localhost:9090/metrics
```

Pour consulter l'endpoint de `node_exporter`, depuis l'hôte Linux :

```bash
curl http://localhost:9100/metrics
```

L'endpoint doit rester accessible uniquement depuis les réseaux et les identités qui en ont besoin.

## 10. Bases de PromQL

PromQL est le langage de requête de Prometheus.

Une expression peut sélectionner des séries, appliquer des fonctions, agréger des valeurs et réaliser des opérations arithmétiques.

### 10.1 Sélectionner une métrique

```promql
up
```

Retourne les séries de la métrique `up`.

Pour ne sélectionner que les cibles du job `node` :

```promql
up{job="node"}
```

Le filtre `=` correspond à une égalité.

Le filtre `!=` exclut une valeur.

L'opérateur `=~` correspond à une expression régulière.

L'opérateur `!~` exclut les valeurs correspondant à une expression régulière.

Exemple :

```promql
http_requests_total{status=~"5.."}
```

Cette expression sélectionne les séries dont l'étiquette `status` correspond aux codes commençant par `5`, sous réserve que l'application expose cette métrique et cette étiquette.

### 10.2 Sélection instantanée et plage temporelle

Une sélection instantanée :

```promql
node_memory_MemAvailable_bytes
```

Retourne les dernières valeurs disponibles des séries sélectionnées.

Une plage temporelle :

```promql
http_requests_total[5m]
```

Sélectionne les échantillons d'une période de cinq minutes. Une plage seule est souvent utilisée à l'intérieur d'une fonction telle que `rate()`.

### 10.3 Calculer un débit avec `rate()`

```promql
rate(http_requests_total[5m])
```

`rate()` estime le taux moyen de variation par seconde d'un compteur sur la période spécifiée. Il prend en compte les réinitialisations normales des compteurs.

Pour obtenir le débit global, toutes étiquettes confondues :

```promql
sum(
  rate(http_requests_total[5m])
)
```

Pour conserver une ventilation par statut HTTP :

```promql
sum by (status) (
  rate(http_requests_total[5m])
)
```

La métrique utilisée doit réellement exister. Ces exemples concernent une application instrumentée, et non une métrique standard garantie par `node_exporter`.

### 10.4 Calculer une augmentation avec `increase()`

```promql
increase(http_requests_total[1h])
```

Cette expression estime l'augmentation du compteur pendant la dernière heure.

Elle est pratique pour répondre à des questions comme : « Combien de requêtes ont été traitées approximativement pendant cette période ? »

### 10.5 Agréger les métriques

Total :

```promql
sum(rate(http_requests_total[5m]))
```

Moyenne :

```promql
avg(node_load1)
```

Maximum :

```promql
max(node_load1)
```

Regroupement par instance :

```promql
sum by (instance) (
  rate(http_requests_total[5m])
)
```

Le choix de l'agrégation dépend de la signification de la métrique.

Il ne faut pas appliquer automatiquement `sum()` ou `avg()` à toutes les séries d'un tableau de bord : une agrégation peut masquer une instance défaillante ou calculer une valeur sans signification métier.

### 10.6 Mesurer l'utilisation CPU

Le compteur `node_cpu_seconds_total` représente le temps CPU cumulé par état de processeur.

Une estimation de l'utilisation CPU, à l'exclusion du temps inactif, est :

```promql
1 - avg by (instance) (
  rate(node_cpu_seconds_total{mode="idle"}[5m])
)
```

La valeur est un ratio compris normalement entre `0` et `1`.

Dans Grafana, configurer l'unité du panneau en pourcentage et vérifier que la formule et le format de la valeur sont cohérents.

Une valeur de `0.75` correspond à `75 %` lorsque le panneau l'affiche en pourcentage sur une base de zéro à un.

### 10.7 Calculer la proportion d'erreurs HTTP

Dans une application exposant `http_requests_total` avec une étiquette `status` :

```promql
sum(
  rate(http_requests_total{status=~"5.."}[5m])
)
/
clamp_min(
  sum(rate(http_requests_total[5m])),
  1
)
```

Ce calcul produit une fraction estimée des réponses HTTP 5xx.

Pour un panneau en pourcentage, utiliser une unité et un formatage adaptés.

Il faut vérifier que le compteur inclut bien toutes les requêtes concernées et que le même périmètre est utilisé au numérateur et au dénominateur.

### 10.8 Calculer un percentile de latence

Pour un histogramme classique de latence HTTP :

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

Cette requête estime le percentile 95 de la distribution observée, à partir des buckets. Elle suppose que la métrique correspond à un histogramme classique avec une étiquette `le`.

Le percentile 95 indique une estimation du seuil en dessous duquel se situent 95 % des observations de la distribution pendant la fenêtre évaluée.

Il ne faut pas interpréter ce résultat comme le temps de réponse maximal, ni comme le percentile 95 d'une période arbitraire calculée sans tenir compte de la distribution.

### 10.9 Comparer plusieurs services

Si les métriques de l'application contiennent une étiquette `service` :

```promql
sum by (service) (
  rate(http_requests_total[5m])
)
```

Cette requête permet de comparer les débits de plusieurs services.

On peut aussi filtrer un environnement :

```promql
sum by (service) (
  rate(http_requests_total{environment="production"}[5m])
)
```

Les étiquettes doivent être définies de façon cohérente dans l'instrumentation ou les règles de collecte.

### 10.10 Bonnes pratiques PromQL

1. Utiliser `rate()` pour les compteurs lorsqu'on cherche un débit.
2. Choisir une fenêtre temporelle adaptée à la fréquence d'échantillonnage et à la variabilité du phénomène.
3. Agréger les numérateurs et dénominateurs séparément pour calculer correctement un ratio global.
4. Préserver les étiquettes nécessaires à l'analyse.
5. Vérifier les unités renvoyées avant de construire un panneau Grafana.
6. Tester les requêtes dans Prometheus avant de les utiliser dans une règle d'alerte.
7. Vérifier le comportement lorsque le trafic est nul, absent ou très faible.

## 11. Créer des recording rules

Une recording rule calcule périodiquement une expression et enregistre son résultat sous un nouveau nom de métrique.

Cette approche est utile lorsque plusieurs tableaux de bord ou plusieurs alertes réutilisent le même calcul.

### 11.1 Fichier `prometheus/rules/recording.yml`

```yaml
groups:
  - name: host-recording-rules
    interval: 30s
    rules:
      - record: instance:node_cpu_utilisation:rate5m
        expr: |
          1 - avg by (instance) (
            rate(node_cpu_seconds_total{mode="idle"}[5m])
          )

      - record: instance:node_memory_available_ratio
        expr: |
          node_memory_MemAvailable_bytes
          /
          node_memory_MemTotal_bytes
```

La première règle calcule un ratio d'utilisation CPU par instance.

La seconde calcule la proportion de mémoire disponible par rapport à la mémoire totale.

Ces deux métriques enregistrées peuvent ensuite être utilisées dans les panneaux et les règles d'alerte.

Les noms contenant des deux-points sont réservés aux métriques produites par les recording rules selon les conventions Prometheus.

### 11.2 Pourquoi les utiliser ?

Avantages :

- Éviter la duplication des expressions complexes.
- Simplifier les panneaux et les alertes.
- Réduire le coût de répétition de certaines requêtes.
- Uniformiser les calculs utilisés par plusieurs équipes.

Limites :

- Elles consomment de l'espace de stockage.
- Elles doivent être documentées.
- Une erreur dans la règle peut se répercuter dans de nombreux tableaux de bord.
- Elles ajoutent un délai lié à leur intervalle d'évaluation.

Les recording rules doivent donc être versionnées et testées au même titre que les autres fichiers de configuration.

## 12. Créer des alerting rules

Les alerting rules transforment des conditions mesurables en alertes.

### 12.1 Les états d'une alerte

Une règle peut passer par plusieurs états :

```text
Condition fausse
      |
      v
    INACTIVE
      |
      | Condition vraie
      v
    PENDING
      |
      | Condition maintenue pendant la durée "for"
      v
    FIRING
      |
      | Condition redevenue fausse
      v
    RESOLVED / INACTIVE
```

Le délai `for` évite de déclencher immédiatement une alerte sur chaque dépassement temporaire.

Il ne faut pas confondre la résolution logique d'une alerte avec le moment où une notification est envoyée ou reconnue par un destinataire.

### 12.2 Fichier `prometheus/rules/alerts.yml`

```yaml
groups:
  - name: host-alerts
    interval: 30s
    rules:
      - alert: NodeExporterDown
        expr: up{job="node"} == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "La collecte de node_exporter échoue"
          description: "La cible {{ $labels.instance }} est inaccessible depuis au moins deux minutes."

      - alert: HostHighCPU
        expr: instance:node_cpu_utilisation:rate5m > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation CPU élevée"
          description: "L'instance {{ $labels.instance }} dépasse 85 % d'utilisation CPU depuis dix minutes."

      - alert: HostLowMemory
        expr: |
          node_memory_MemAvailable_bytes
          /
          node_memory_MemTotal_bytes < 0.10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Mémoire disponible faible"
          description: "L'instance {{ $labels.instance }} dispose de moins de 10 % de mémoire disponible."

      - alert: HostDiskSpaceLow
        expr: |
          (
            node_filesystem_avail_bytes{
              fstype!~"tmpfs|overlay|squashfs|nsfs"
            }
            /
            node_filesystem_size_bytes{
              fstype!~"tmpfs|overlay|squashfs|nsfs"
            }
          ) < 0.10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Espace disque disponible faible"
          description: "Le système de fichiers {{ $labels.mountpoint }} sur {{ $labels.instance }} dispose de moins de 10 % d'espace disponible."
```

Les noms de types de systèmes de fichiers et les métriques disponibles peuvent varier selon les environnements. Il faut ajuster les filtres à partir des séries réellement exposées.

### 12.3 Comprendre les règles

Une règle de cette forme :

```yaml
expr: instance:node_cpu_utilisation:rate5m > 0.85
for: 10m
```

signifie que la condition doit rester vraie pendant dix minutes avant que l'alerte devienne `FIRING`.

Les labels servent à catégoriser et à router les alertes.

Les annotations fournissent des informations lisibles par l'opérateur et peuvent inclure des valeurs d'étiquettes.

### 12.4 Valider les règles

```bash
docker compose exec prometheus \
  promtool check rules /etc/prometheus/rules/alerts.yml \
  /etc/prometheus/rules/recording.yml
```

Recharger ensuite la configuration :

```bash
curl -X POST http://localhost:9090/-/reload
```

Puis ouvrir dans Prometheus :

`http://localhost:9090/alerts`

Cette page permet de vérifier les états des règles d'alerte.

**Important :** dans le laboratoire présenté, ces règles sont évaluées par Prometheus, mais aucune notification n'est envoyée tant qu'un système de notification n'a pas été raccordé.

## 13. Alertmanager et notifications

### 13.1 Pourquoi Alertmanager ?

Prometheus évalue les conditions et déclenche des alertes. Alertmanager prend en charge leur traitement opérationnel :

- Regroupement de plusieurs alertes liées.
- Routage selon les labels.
- Silences temporaires.
- Inhibition de certaines alertes.
- Transmission aux destinataires configurés.

Exemple : si un serveur entier tombe en panne, plusieurs alertes secondaires peuvent apparaître. Une règle d'inhibition peut éviter de générer de nombreuses notifications redondantes lorsque la panne du serveur explique déjà les symptômes.

### 13.2 Exemple de configuration de routage

Le fragment suivant illustre la structure d'un fichier `alertmanager.yml`. Les adresses et paramètres SMTP sont des valeurs d'exemple à remplacer.

```yaml
route:
  receiver: operations-email
  group_by:
    - alertname
    - instance
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: operations-email
    email_configs:
      - to: "operations@example.org"
        send_resolved: true
```

Cette configuration montre le routage et les paramètres de regroupement. Pour envoyer effectivement des courriels, Alertmanager doit aussi disposer de paramètres SMTP valides, fournis par un mécanisme sécurisé.

Ne pas confondre les adresses d'exemple avec une configuration prête pour la production.

### 13.3 Regroupement

Si 20 instances émettent une même alerte, envoyer une notification distincte pour chaque instance peut submerger l'équipe.

Le regroupement rassemble plusieurs alertes apparentées dans une même notification.

Le bon regroupement dépend du contexte : service, cluster, environnement ou nature de l'incident.

### 13.4 Silences et inhibitions

Un silence supprime temporairement les notifications correspondant à des critères précis, par exemple pendant une maintenance.

Une inhibition supprime des notifications secondaires lorsqu'une alerte plus fondamentale est déjà active.

Ces mécanismes ne remplacent pas la résolution du problème. Une politique de silence doit préciser le périmètre et la durée, et les alertes critiques doivent rester visibles dans les outils de supervision.

## 14. Provisionner Grafana

Le provisionnement permet de définir les sources de données et les tableaux de bord dans des fichiers versionnés.

Cette méthode est plus reproductible que la création manuelle de chaque paramètre directement dans l'interface.

### 14.1 Déclarer la source Prometheus

Créer `grafana/provisioning/datasources/prometheus.yml` :

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

L'URL utilise le nom DNS du service sur le réseau Compose. Il ne faut pas remplacer arbitrairement cette adresse par `localhost`, car Grafana s'exécute dans son propre conteneur.

### 14.2 Déclarer un fournisseur de tableaux de bord

Créer `grafana/provisioning/dashboards/dashboards.yml` :

```yaml
apiVersion: 1

providers:
  - name: dashboards
    orgId: 1
    folder: Observability
    type: file
    disableDeletion: true
    editable: true
    options:
      path: /var/lib/grafana/dashboards
```

Ce fichier décrit le mécanisme de chargement des tableaux de bord depuis un répertoire.

Pour provisionner des tableaux de bord JSON, il faut également monter un répertoire qui contient ces fichiers JSON dans le chemin déclaré, par exemple avec un volume supplémentaire dans le service Grafana.

Dans le laboratoire minimal ci-dessus, ce répertoire n'est pas encore créé. La déclaration prépare le mécanisme : avant de l'utiliser, créer `grafana/dashboards/`, y ajouter les fichiers de tableaux de bord exportés, puis monter ce répertoire sur `/var/lib/grafana/dashboards`.

Après toute modification de provisionnement, contrôler les journaux de Grafana.

### 14.3 Vérifier la source de données

Après démarrage :

1. Ouvrir Grafana sur `http://localhost:3000`.
2. Ouvrir la section des sources de données.
3. Sélectionner `Prometheus`.
4. Vérifier l'URL `http://prometheus:9090`.
5. Tester la connexion avec le bouton prévu par l'interface.

La source de données doit être joignable depuis Grafana, pas seulement depuis l'hôte.

### 14.4 Explorer les données

Utiliser l'explorateur de Grafana pour tester :

```promql
up
```

Puis :

```promql
node_memory_MemAvailable_bytes
```

Enfin :

```promql
instance:node_cpu_utilisation:rate5m
```

Ce dernier indicateur n'apparaîtra qu'une fois la recording rule correctement chargée et évaluée.

## 15. Construire un tableau de bord pertinent

Un bon tableau de bord facilite la décision. Il ne doit pas simplement afficher le plus grand nombre possible de courbes.

### 15.1 Tableau de bord système

Créer un tableau de bord nommé `Infrastructure - Vue générale`.

Ajouter les panneaux suivants.

#### Panneau 1 : disponibilité des cibles

Requête :

```promql
up
```

Visualisation suggérée : état, tableau ou série temporelle.

Objectif : repérer rapidement les cibles dont la dernière collecte a échoué.

#### Panneau 2 : utilisation CPU

Requête :

```promql
instance:node_cpu_utilisation:rate5m * 100
```

Visualisation suggérée : série temporelle.

Unité : pourcentage.

#### Panneau 3 : mémoire disponible

Requête :

```promql
node_memory_MemAvailable_bytes
```

Unité : octets, avec affichage en unités lisibles.

#### Panneau 4 : proportion de mémoire disponible

Requête :

```promql
100 *
node_memory_MemAvailable_bytes
/
node_memory_MemTotal_bytes
```

Unité : pourcentage.

#### Panneau 5 : espace disque disponible

Requête :

```promql
100 *
node_filesystem_avail_bytes{
  fstype!~"tmpfs|overlay|squashfs|nsfs"
}
/
node_filesystem_size_bytes{
  fstype!~"tmpfs|overlay|squashfs|nsfs"
}
```

Unité : pourcentage.

Afficher les étiquettes `instance` et `mountpoint` dans la légende pour distinguer les systèmes de fichiers.

#### Panneau 6 : charge système

Requête :

```promql
node_load1
```

La charge système n'est pas un pourcentage CPU. Son interprétation dépend du nombre de processeurs et de la nature de la charge.

### 15.2 Adapter les unités

Une bonne pratique consiste à vérifier les unités renvoyées par PromQL :

- Les durées sont en secondes lorsque le nom de métrique les exprime ainsi.
- La mémoire et les volumes sont souvent exprimés en octets.
- Les ratios sont généralement compris entre 0 et 1.
- Un ratio multiplié par 100 devient une valeur comprise entre 0 et 100 lorsqu'elle est interprétée en pourcentage.

Ne pas multiplier une requête par 100 tout en configurant le panneau pour appliquer une seconde conversion de pourcentage. Cela produirait une valeur erronée.

### 15.3 Utiliser les variables de tableau de bord

Une variable peut permettre de choisir l'instance affichée sans créer un tableau de bord par serveur.

Par exemple, créer une variable `instance` basée sur une requête de type :

```promql
label_values(up{job="node"}, instance)
```

La disponibilité de cette syntaxe dépend des fonctionnalités de requête et de la version de Grafana utilisée. Dans les versions récentes, utiliser l'éditeur de variables proposé pour la source Prometheus si la requête historique n'est pas disponible.

Puis filtrer un panneau :

```promql
node_memory_MemAvailable_bytes{
  instance=~"$instance"
}
```

Le filtre regex permet à une variable multivaleur de sélectionner plusieurs instances lorsque cette option est activée.

### 15.4 Ajouter des annotations

Les annotations placent des événements sur les graphiques, par exemple :

- Un déploiement.
- Une maintenance.
- Une modification de configuration.
- Le début d'un incident confirmé.

Une série temporelle devient plus utile lorsque les changements de comportement peuvent être rapprochés des changements techniques.

### 15.5 Erreurs de conception à éviter

Éviter les pratiques suivantes :

- Afficher 30 courbes sans regroupement ni légende claire.
- Utiliser un même seuil pour tous les environnements.
- Mélanger secondes, millisecondes et ratios.
- Afficher des valeurs moyennes sans considérer les pics.
- Masquer les erreurs en ne présentant que des moyennes globales.
- Construire un tableau de bord sans objectif opérationnel.
- Utiliser des couleurs alarmantes pour des informations qui ne nécessitent aucune action.

Un tableau de bord devrait répondre à des questions opérationnelles concrètes et guider vers les causes possibles.

## 16. Mesures de service : latence, trafic, erreurs et saturation

La supervision d'un hôte est nécessaire, mais elle ne suffit pas à démontrer qu'une application fonctionne correctement.

Il faut suivre également les indicateurs perçus par les utilisateurs.

### 16.1 Les quatre signaux

| Signal | Question | Exemple |
|---|---|---|
| Latence | Le service répond-il rapidement ? | Temps de réponse HTTP |
| Trafic | Quelle charge le service reçoit-il ? | Requêtes par seconde |
| Erreurs | Quelle proportion de requêtes échoue ? | Taux HTTP 5xx |
| Saturation | Une ressource approche-t-elle de sa limite ? | File d'attente ou pool de connexions saturé |

Ces signaux se complètent.

Un CPU à 95 % n'implique pas toujours une dégradation visible par les utilisateurs. À l'inverse, une application peut répondre très lentement avec une utilisation CPU faible si elle attend une dépendance externe.

### 16.2 Exemple de contrat de métriques applicatives

Une API instrumentée pourrait exposer :

```text
api_http_requests_total
api_http_request_duration_seconds
api_active_requests
api_database_connections_active
api_database_connections_max
```

Avec des étiquettes cohérentes, le service devient plus facile à analyser.

Éviter de définir des étiquettes à partir de données individuelles ou d'informations sensibles.

### 16.3 Disponibilité

Pour une API instrumentée avec un endpoint de disponibilité, un probe externe peut compléter les métriques internes.

Le fait que Prometheus puisse interroger un endpoint `/metrics` ne garantit pas nécessairement que le parcours métier de l'application fonctionne.

Pour des scénarios plus avancés, utiliser des sondes qui testent réellement un endpoint HTTP ou une transaction fonctionnelle. L'exporter Blackbox de l'écosystème Prometheus est une option pour les sondes HTTP, TCP, DNS ou ICMP selon sa configuration.

## 17. Environnements Docker et Kubernetes

Le parcours précédent utilisait déjà les conteneurs et l'orchestration. L'observabilité doit maintenant être adaptée à ces environnements.

### 17.1 Docker

Pour Docker, distinguer :

- Les métriques du système hôte.
- Les métriques des conteneurs.
- Les métriques de l'application à l'intérieur des conteneurs.

`node_exporter` cible principalement les métriques système. Il ne remplace pas un outil adapté à la collecte des métriques des conteneurs ni l'instrumentation de l'application.

L'intégration peut inclure :

- Des métriques du système hôte.
- Des métriques exposées par chaque application.
- Des métriques du runtime et des conteneurs.
- Des sondes de disponibilité HTTP.
- Des métriques de la base de données ou du proxy.

La sélection des composants dépend des besoins, des droits d'accès et de l'architecture du moteur de conteneurs.

### 17.2 Kubernetes

Dans Kubernetes, les pods et les adresses peuvent évoluer fréquemment.

Une configuration de cibles statiques devient insuffisante lorsque le nombre de services et de pods varie constamment.

Les solutions habituelles s'appuient sur la découverte de services Kubernetes, les mécanismes de découverte de Prometheus et, dans une installation basée sur Prometheus Operator, des objets tels que `ServiceMonitor` ou `PodMonitor`.

### 17.3 Exemple de ServiceMonitor

Le fragment suivant illustre la collecte d'un service dont le port nommé `metrics` expose les métriques HTTP.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api
  namespace: observability
  labels:
    release: monitoring
spec:
  namespaceSelector:
    matchNames:
      - applications
  selector:
    matchLabels:
      app.kubernetes.io/name: api
  endpoints:
    - port: metrics
      path: /metrics
      interval: 30s
```

Ce manifeste suppose que :

- Prometheus Operator est installé.
- Le type personnalisé `ServiceMonitor` existe dans le cluster.
- Le Service applicatif se trouve dans le namespace `applications`.
- Ce Service porte le label `app.kubernetes.io/name: api`.
- Ce Service expose un port nommé `metrics`.
- Les labels du `ServiceMonitor` correspondent aux sélecteurs utilisés par la configuration Prometheus déployée.

Les noms de labels et les sélecteurs dépendent de l'installation. Avec un chart Helm tel que `kube-prometheus-stack`, les paramètres doivent être adaptés à la release et aux conventions de cette installation.

Ce manifeste n'installe pas Prometheus Operator à lui seul.

### 17.4 Contrôler la collecte dans Kubernetes

Les vérifications comprennent notamment :

```bash
kubectl get pods -A
kubectl get services -A
kubectl get servicemonitors -A
kubectl describe servicemonitor api -n observability
```

Si le type personnalisé existe dans le cluster.

Vérifier également :

- Que le pod applicatif expose bien le port de métriques.
- Que le Service sélectionne les bons pods.
- Que le `ServiceMonitor` cible le bon Service.
- Que les sélecteurs de l'opérateur autorisent sa découverte.
- Que les politiques réseau et les droits RBAC permettent la collecte.

La disparition d'une cible n'est pas nécessairement un problème PromQL. Elle peut provenir de la découverte de services, des sélecteurs ou de la configuration de déploiement.

## 18. Sécuriser la plateforme d'observabilité

Les métriques peuvent révéler des détails sensibles sur l'infrastructure, les applications et les dépendances.

### 18.1 Contrôler l'exposition réseau

Ne pas publier sans protection les interfaces de Prometheus, Grafana, Alertmanager ou les endpoints des exporters sur Internet.

Utiliser selon le contexte :

- Des réseaux privés.
- Un VPN ou un accès administratif contrôlé.
- Un reverse proxy correctement configuré.
- TLS.
- Une authentification forte.
- Des règles de pare-feu.
- Des restrictions d'accès au niveau réseau.

Le mappage `127.0.0.1` du laboratoire restreint l'écoute aux accès locaux de l'hôte, mais ce n'est pas une solution complète de sécurité en production.

### 18.2 Protéger les endpoints de métriques

Un endpoint `/metrics` peut exposer :

- Des noms de services et des versions.
- Des noms d'hôtes ou d'instances.
- Des informations sur les bases de données.
- Des noms de files d'attente.
- Des détails sur l'état du système.

Les endpoints d'exporters ne doivent pas être accessibles à des utilisateurs non autorisés.

### 18.3 Protéger les secrets

Ne pas stocker dans les métriques, les noms de métriques ou leurs labels :

- Des mots de passe.
- Des jetons d'accès.
- Des clés d'API.
- Des chaînes de connexion contenant des secrets.
- Des données personnelles non nécessaires.

Ne pas intégrer de secrets dans les tableaux de bord exportés ou les journaux de CI/CD.

### 18.4 Contrôler les droits Grafana

Appliquer le principe du moindre privilège :

- Les administrateurs gèrent la configuration globale.
- Les équipes disposent des accès aux dossiers et tableaux de bord nécessaires.
- Les comptes de consultation n'ont pas de droits d'administration.
- Les sources de données et les destinations d'alerte sont modifiables uniquement par les personnes autorisées.

Les comptes et identités de supervision sont des comptes techniques à protéger comme les autres composants d'infrastructure.

## 19. Rétention, stockage et capacité

Prometheus stocke les échantillons dans une base de séries temporelles locale.

### 19.1 Configurer la rétention

Le laboratoire utilise :

```text
--storage.tsdb.retention.time=15d
```

Cela demande de conserver les données pendant une durée de rétention de quinze jours, sous réserve de la capacité de stockage et des autres paramètres actifs.

La durée de rétention doit être décidée selon :

- Les besoins d'analyse d'incidents.
- Les obligations éventuelles de conservation.
- Le volume de données.
- Les limites de stockage disponibles.
- Le coût de la conservation.

### 19.2 Mesurer l'impact de la cardinalité

Un volume élevé de séries peut augmenter :

- La mémoire utilisée.
- Les opérations de stockage.
- Le temps de calcul des requêtes.
- Le volume disque.
- Le coût des solutions distantes de stockage ou de traitement.

Avant d'allonger la rétention, analyser l'évolution du nombre de séries, les métriques inutiles et les labels à forte cardinalité.

### 19.3 Examiner les métriques Prometheus

Exemples de requêtes utiles pour diagnostiquer Prometheus :

```promql
prometheus_tsdb_head_series
```

Cette métrique indique le nombre de séries présentes dans la tête de la base de données TSDB.

```promql
prometheus_tsdb_head_samples_appended_total
```

Ce compteur mesure les échantillons ajoutés à la tête de la base. Pour obtenir un débit estimé, utiliser :

```promql
rate(prometheus_tsdb_head_samples_appended_total[5m])
```

Les noms exacts disponibles peuvent dépendre de la version de Prometheus. Vérifier les métriques exposées par l'instance avant de construire les panneaux.

## 20. Automatiser avec Git et la CI/CD

La supervision fait partie de l'infrastructure exploitable. Ses configurations doivent être versionnées, revues et validées avant déploiement.

### 20.1 Organisation du dépôt

Exemple :

```text
devops-platform/
├── observability/
│   ├── compose.yaml
│   ├── .gitignore
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── rules/
│   │       ├── recording.yml
│   │       └── alerts.yml
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           └── dashboards/
├── .github/
│   └── workflows/
│       └── validate-observability.yml
└── .gitlab-ci.yml
```

Ne pas versionner les secrets et les données persistantes de Prometheus.

### 20.2 Valider avant de déployer

Les contrôles devraient couvrir :

1. La validité YAML et la structure de la configuration.
2. La validité des fichiers de règles.
3. La cohérence des chemins.
4. Les tests de requêtes critiques lorsque des tests adaptés existent.
5. L'intégration des changements dans une branche revue.
6. Le déploiement dans un environnement de test avant la production.

### 20.3 Exemple GitHub Actions

Créer `.github/workflows/validate-observability.yml` à la racine du dépôt.

```yaml
name: Validate observability configuration

on:
  pull_request:
    paths:
      - "observability/prometheus/**"
      - ".github/workflows/validate-observability.yml"
  push:
    paths:
      - "observability/prometheus/**"
      - ".github/workflows/validate-observability.yml"

jobs:
  validate-prometheus:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Validate Prometheus configuration
        run: |
          docker run --rm \
            -v "$PWD/observability/prometheus:/etc/prometheus:ro" \
            --entrypoint=promtool \
            prom/prometheus:latest \
            check config /etc/prometheus/prometheus.yml

      - name: Validate recording and alerting rules
        run: |
          docker run --rm \
            -v "$PWD/observability/prometheus:/etc/prometheus:ro" \
            --entrypoint=promtool \
            prom/prometheus:latest \
            check rules \
            /etc/prometheus/rules/recording.yml \
            /etc/prometheus/rules/alerts.yml
```

Cette pipeline utilise Docker pour exécuter `promtool` sans installer directement l'outil sur le runner.

Pour une utilisation en production, épingler les versions des actions et des images de conteneurs selon la politique du dépôt. Les validations doivent être complétées lorsque de nouveaux types de configuration ou de nouvelles dépendances sont introduits.

La validation syntaxique ne prouve pas que les cibles sont accessibles ni que les expressions répondent correctement aux besoins métiers.

### 20.4 Exemple GitLab CI

Créer un fichier `.gitlab-ci.yml` à la racine du dépôt.

```yaml
stages:
  - validate

validate_prometheus:
  stage: validate
  image:
    name: prom/prometheus:latest
    entrypoint: [""]
  script:
    - promtool check config observability/prometheus/prometheus.yml
    - >
      promtool check rules
      observability/prometheus/rules/recording.yml
      observability/prometheus/rules/alerts.yml
  rules:
    - changes:
        - observability/prometheus/**/*
        - .gitlab-ci.yml
```

Vérifier le comportement du runner, notamment la présence d'un environnement shell compatible dans l'image utilisée et la manière dont il exécute les commandes. Si l'image ou le runner ne convient pas, utiliser une image de CI dédiée qui contient le client et les outils nécessaires.

### 20.5 Déployer après validation

Un flux de livraison typique est :

```text
Modification de configuration
            |
            v
     Commit sur une branche
            |
            v
    Revue et merge request
            |
            v
 Validation automatique YAML/règles
            |
            v
   Déploiement en environnement test
            |
            v
 Vérification des cibles et des alertes
            |
            v
       Validation humaine
            |
            v
  Déploiement dans l'environnement cible
            |
            v
 Vérification post-déploiement
```

Le pipeline ne doit pas se contenter de vérifier que les fichiers sont syntaxiquement corrects. Il doit aussi s'assurer que les modifications n'ont pas rendu la supervision inutilisable.

## 21. Intégration avec Terraform et Ansible

Les cours précédents permettent d'automatiser le provisionnement et la configuration de la plateforme.

### 21.1 Rôle de Terraform

Terraform peut préparer :

- Les machines ou les ressources cloud.
- Les réseaux et sous-réseaux.
- Les règles d'accès réseau.
- Les volumes et disques persistants.
- Les environnements nécessaires à la plateforme d'observabilité.

Terraform ne remplace pas Prometheus ni Grafana : il prépare et gère les ressources d'infrastructure.

### 21.2 Rôle d'Ansible

Ansible peut installer et configurer :

- `node_exporter` sur les serveurs Linux.
- Les services système associés.
- Les fichiers de configuration.
- Les utilisateurs et permissions.
- Les règles de pare-feu nécessaires.
- Les mécanismes de mise à jour et de redémarrage.

La configuration Ansible doit rester cohérente avec les tâches de Terraform et le mécanisme de découverte des cibles.

### 21.3 Séparer les responsabilités

Une architecture typique sépare les rôles :

```text
Terraform
   |
   v
Infrastructure, réseau, machines
   |
   v
Ansible
   |
   v
Installation des exporters et configuration système
   |
   v
Prometheus
   |
   v
Collecte et stockage des métriques
   |
   v
Grafana / Alertmanager
   |
   v
Visualisation et notifications
```

Les frontières peuvent varier selon la plateforme, mais chaque outil doit avoir une responsabilité claire.

## 22. Diagnostic des incidents de supervision

### 22.1 La cible est `DOWN`

Symptômes :

- `up{job="node"}` retourne `0`.
- La page `/targets` affiche une erreur de collecte.
- Les métriques de l'exporter ne sont plus actualisées.

Procédure :

1. Examiner le message d'erreur dans la page `/targets`.
2. Vérifier que le processus de l'exporter est actif.
3. Vérifier que le port est en écoute.
4. Tester l'endpoint depuis l'endroit où tourne Prometheus.
5. Vérifier l'adresse réseau et le DNS.
6. Examiner les règles de pare-feu.
7. Vérifier que le chemin `/metrics` est accessible.
8. Consulter les journaux des composants.

Une erreur « connection refused » ne se diagnostique pas de la même façon qu'un délai d'attente réseau ou qu'une erreur HTTP 401/403.

### 22.2 La cible est `UP`, mais la métrique est absente

Causes possibles :

- La métrique n'est pas exposée par l'exporter.
- Le nom de métrique a changé.
- La métrique n'existe que lorsqu'un événement s'est produit.
- Une étiquette sélectionnée dans la requête est incorrecte.
- La requête utilise le mauvais job ou la mauvaise instance.
- Une règle d'enregistrement n'est pas chargée ou n'a pas encore été évaluée.

Procédure :

1. Consulter directement l'endpoint `/metrics`.
2. Chercher le nom exact de la métrique.
3. Tester une requête simple sans filtre.
4. Ajouter progressivement les filtres.
5. Vérifier les règles enregistrées dans Prometheus.

### 22.3 Grafana ne parvient pas à contacter Prometheus

Vérifications :

- La source de données pointe-t-elle vers le bon service ?
- Grafana et Prometheus partagent-ils un réseau où le DNS de service fonctionne ?
- Prometheus est-il démarré ?
- Le port configuré est-il celui qui est réellement écouté ?
- Les logs affichent-ils une erreur DNS, un refus de connexion ou un timeout ?

Dans un conteneur Grafana, `localhost:9090` n'est généralement pas l'adresse du conteneur Prometheus. Il s'agit du conteneur Grafana lui-même.

### 22.4 Une alerte ne se déclenche pas

Vérifier :

1. L'expression dans l'interface de Prometheus.
2. La présence des séries retournées par l'expression.
3. Les seuils et les unités.
4. La durée `for`.
5. L'état de la règle dans `/alerts`.
6. L'intervalle d'évaluation.
7. Les étiquettes utilisées par l'expression.
8. Les logs de Prometheus.
9. La configuration d'Alertmanager si l'alerte est active mais qu'aucune notification n'arrive.

Une alerte `PENDING` n'a pas nécessairement satisfait la durée nécessaire pour passer à `FIRING`.

Une alerte `FIRING` peut être visible dans Prometheus sans qu'une notification soit envoyée si Alertmanager n'est pas configuré ou si la route vers le destinataire est incorrecte.

### 22.5 Les tableaux de bord sont lents

Causes possibles :

- Trop de séries retournées.
- Une cardinalité excessive.
- Des requêtes complexes répétées.
- Une période d'analyse trop longue.
- Un intervalle de rafraîchissement trop court.
- Des transformations coûteuses dans Grafana.
- Une instance Prometheus sous-dimensionnée.

Actions possibles :

- Simplifier les requêtes.
- Réduire le nombre de séries affichées.
- Utiliser des recording rules pour les calculs réutilisés.
- Réduire la cardinalité.
- Adapter la période et l'intervalle de rafraîchissement.
- Vérifier les métriques de performance de Prometheus et Grafana.

### 22.6 Le disque se remplit

Les causes possibles comprennent une rétention excessive, un grand nombre de séries ou un volume mal dimensionné.

Procédure :

1. Vérifier l'espace disque disponible.
2. Examiner le volume de données Prometheus.
3. Vérifier les paramètres de rétention.
4. Examiner l'évolution du nombre de séries.
5. Identifier les familles de métriques et labels responsables.
6. Ajuster la rétention et la collecte.
7. Mettre en place une alerte sur l'espace disponible.

Ne pas supprimer manuellement des fichiers internes de la TSDB lorsque Prometheus fonctionne. Appliquer une stratégie de maintenance documentée et respecter le fonctionnement du moteur de stockage.

## 23. Travaux pratiques guidés

### TP 1 — Construire la plateforme locale

**Objectif :** lancer Prometheus, Grafana et `node_exporter`.

Étapes :

1. Créer l'arborescence du projet.
2. Créer `.env` et `.gitignore`.
3. Écrire `compose.yaml`.
4. Créer `prometheus/prometheus.yml`.
5. Créer les fichiers de provisionnement Grafana.
6. Démarrer les services avec Docker Compose.
7. Consulter les logs.
8. Vérifier `/targets`.
9. Exécuter la requête `up`.
10. Vérifier la présence des métriques système.

Résultat attendu : Prometheus collecte ses propres métriques et celles de la cible `node_exporter`.

### TP 2 — Écrire des requêtes PromQL

À partir des données disponibles, exécuter :

```promql
up
```

```promql
node_memory_MemAvailable_bytes
```

```promql
rate(prometheus_tsdb_head_samples_appended_total[5m])
```

```promql
1 - avg by (instance) (
  rate(node_cpu_seconds_total{mode="idle"}[5m])
)
```

Travail demandé :

- Identifier la métrique, les labels et les unités.
- Expliquer l'objectif de chaque requête.
- Vérifier les valeurs obtenues.
- Modifier une requête pour comparer plusieurs cibles, si plusieurs cibles sont présentes.

### TP 3 — Créer un tableau de bord Grafana

Créer un tableau de bord intitulé `Infrastructure - Vue générale`.

Ajouter :

1. L'état des cibles.
2. L'utilisation CPU.
3. La mémoire disponible.
4. La proportion de mémoire disponible.
5. L'espace disque disponible.
6. La charge système.

Pour chaque panneau :

- Choisir une visualisation pertinente.
- Définir l'unité correcte.
- Configurer un titre explicite.
- Afficher les étiquettes utiles.
- Vérifier la période temporelle.
- Éviter les agrégations qui masquent les instances en difficulté.

### TP 4 — Ajouter des alertes

Créer une règle d'alerte sur l'utilisation CPU élevée.

Condition :

```promql
instance:node_cpu_utilisation:rate5m > 0.85
```

Paramètres suggérés :

- Durée `for` : 10 minutes.
- Label de sévérité : `warning`.
- Annotation : instance, seuil et description lisible.

Valider les règles avec `promtool`, les recharger, puis observer leur état dans Prometheus.

Si le système ne présente pas assez de charge pour déclencher la règle, ne pas en conclure que la règle est défectueuse. Tester sa logique avec des données appropriées ou une règle de test temporaire dans un environnement isolé.

### TP 5 — Intégrer la validation dans Git

1. Ajouter les fichiers de configuration au dépôt.
2. Créer une branche de travail.
3. Modifier une règle.
4. Exécuter `promtool check config`.
5. Exécuter `promtool check rules`.
6. Corriger toute erreur.
7. Soumettre le changement dans une pull request ou une merge request.
8. Vérifier que la CI passe avant la fusion.

Le livrable est une configuration versionnée et validée automatiquement.

## 24. Exercices corrigés

### Exercice 1 — Calculer le nombre de requêtes par seconde

Une API expose `http_requests_total`.

Écrire une requête qui calcule le débit global moyen sur cinq minutes.

**Correction :**

```promql
sum(
  rate(http_requests_total[5m])
)
```

`rate()` estime le débit de chaque série. `sum()` les agrège ensuite.

### Exercice 2 — Calculer le taux d'erreurs 5xx

L'application expose un compteur `http_requests_total` avec le label `status`.

Écrire une expression qui calcule la proportion de réponses 5xx dans le trafic total.

**Correction :**

```promql
sum(
  rate(http_requests_total{status=~"5.."}[5m])
)
/
clamp_min(
  sum(rate(http_requests_total[5m])),
  1
)
```

Le numérateur mesure le débit des réponses 5xx. Le dénominateur représente le débit total. `clamp_min()` évite une division par une valeur trop faible ou nulle.

### Exercice 3 — Estimer le percentile 95 de latence

Une API expose un histogramme classique `http_request_duration_seconds_bucket`.

**Correction :**

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

La requête agrège les buckets puis estime le percentile 95.

### Exercice 4 — Détecter une cible inaccessible

Écrire une règle qui se déclenche si le job `node` échoue pendant deux minutes.

**Correction :**

```yaml
- alert: NodeExporterDown
  expr: up{job="node"} == 0
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Cible node_exporter inaccessible"
    description: "La collecte échoue depuis plus de deux minutes."
```

Cette règle suppose que la série `up` existe pour la cible. Si la cible disparaît complètement de la découverte, une stratégie complémentaire peut être nécessaire.

### Exercice 5 — Détecter une mémoire disponible faible

Créer une alerte lorsque la mémoire disponible passe sous 10 % pendant cinq minutes.

**Correction :**

```yaml
- alert: HostLowMemory
  expr: |
    node_memory_MemAvailable_bytes
    /
    node_memory_MemTotal_bytes < 0.10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Mémoire disponible faible"
```

La formule utilise un ratio compris normalement entre zéro et un. La conversion en pourcentage est inutile pour une comparaison au seuil `0.10`.

### Exercice 6 — Expliquer une cible `UP`

Une cible est `UP`, mais les utilisateurs signalent que l'API ne répond plus correctement.

**Correction :**

`UP` signifie que Prometheus a pu collecter les métriques au dernier contrôle. Cela ne prouve pas que la logique métier fonctionne, que le service est rapide ou que toutes ses dépendances sont disponibles.

Il faut examiner les métriques de service, les logs et, si nécessaire, les traces distribuées.

## 25. Projet final — Plateforme de supervision DevOps

### 25.1 Contexte

Une équipe dispose de plusieurs composants :

- Un hôte Linux.
- Une API exécutée en conteneur.
- Une base de données.
- Un service orchestré par Kubernetes dans un environnement de test.
- Un dépôt Git et un pipeline CI/CD.

L'objectif est de fournir une visibilité commune sur l'état de l'infrastructure et les indicateurs applicatifs.

### 25.2 Architecture attendue

```text
                         DÉPÔT GIT
                             |
                             v
                    Pipeline de validation
                             |
                 +-----------+-----------+
                 |                       |
                 v                       v
          Configuration P8s       Configuration Grafana
                 |                       |
                 +-----------+-----------+
                             |
                             v
                       Prometheus
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
        node_exporter    API /metrics   Cibles Kubernetes
             |               |               |
             +---------------+---------------+
                             |
                             v
                     Base temporelle
                             |
                    +--------+--------+
                    |                 |
                    v                 v
                 Grafana        Règles d'alerte
                                      |
                                      v
                                Alertmanager
                                      |
                                      v
                              Équipe d'exploitation
```

### 25.3 Exigences fonctionnelles

Le projet doit permettre :

- De collecter les métriques de l'hôte.
- De collecter les métriques de Prometheus.
- De collecter les métriques d'une application correctement instrumentée.
- De présenter la disponibilité des cibles.
- De visualiser l'utilisation CPU, la mémoire et le stockage.
- De calculer les débits et les taux d'erreurs de l'application.
- De définir des règles d'alerte documentées.
- De valider les configurations de supervision dans la CI/CD.
- De séparer les secrets des fichiers versionnés.
- De documenter la procédure de diagnostic.

### 25.4 Exigences de qualité

La réalisation doit également respecter les points suivants :

1. Les requêtes PromQL sont commentées ou documentées.
2. Les unités des panneaux Grafana sont correctes.
3. Les seuils d'alerte ont un objectif opérationnel.
4. Les labels ne créent pas de cardinalité inutile.
5. Les endpoints de métriques ne sont pas publiés sans protection.
6. Les données persistantes ne sont pas confondues avec la configuration.
7. Les changements de règles passent par Git et la CI/CD.
8. Le déploiement peut être vérifié après chaque modification.

### 25.5 Livrables

Le projet final doit contenir :

```text
observability/
├── compose.yaml
├── .gitignore
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
│       ├── recording.yml
│       └── alerts.yml
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       └── dashboards/
└── README.md
```

Ajouter également le pipeline CI/CD choisi, par exemple `.github/workflows/validate-observability.yml` ou `.gitlab-ci.yml`.

Le `README.md` doit expliquer l'architecture, le démarrage, les contrôles, les requêtes principales, les alertes et les opérations de maintenance.

### 25.6 Critères d'évaluation

| Domaine | Attendu |
|---|---|
| Collecte | Les cibles attendues sont correctement surveillées |
| PromQL | Les calculs sont corrects et les unités cohérentes |
| Grafana | Le tableau de bord est lisible et exploitable |
| Alerting | Les règles sont documentées et validées |
| CI/CD | La configuration est contrôlée automatiquement |
| Sécurité | Les accès et secrets sont protégés |
| Exploitation | Le diagnostic et les opérations sont documentés |

Le projet est considéré comme terminé lorsque la collecte fonctionne, que les tableaux de bord sont compréhensibles, que les règles sont validées et que les changements peuvent être contrôlés avant déploiement.

## 26. Checklist d'exploitation

### Collecte

- [ ] Les cibles attendues apparaissent dans `/targets`.
- [ ] Les échecs de collecte sont examinés.
- [ ] Les endpoints de métriques sont accessibles uniquement aux composants autorisés.
- [ ] Les noms de jobs et labels sont cohérents.

### PromQL

- [ ] Les compteurs sont analysés avec `rate()` ou `increase()` selon l'objectif.
- [ ] Les jauges ne sont pas traitées à tort comme des compteurs.
- [ ] Les agrégations préservent les dimensions nécessaires.
- [ ] Les ratios utilisent des numérateurs et dénominateurs compatibles.
- [ ] Les fenêtres temporelles sont adaptées au phénomène analysé.

### Grafana

- [ ] Chaque panneau répond à une question opérationnelle.
- [ ] Les unités et légendes sont claires.
- [ ] Les tableaux de bord peuvent être provisionnés ou exportés.
- [ ] Les permissions d'accès sont adaptées.

### Alertes

- [ ] Chaque alerte possède un nom explicite.
- [ ] Les conditions et délais sont justifiés.
- [ ] Les alertes disposent d'annotations lisibles.
- [ ] Les alertes critiques disposent d'un routage opérationnel.
- [ ] Les silences sont limités et documentés.

### Stockage et sécurité

- [ ] La rétention correspond au besoin.
- [ ] Le disque dispose d'une capacité suffisante.
- [ ] La cardinalité est maîtrisée.
- [ ] Les identifiants et secrets sont protégés.
- [ ] Les interfaces de supervision ne sont pas exposées sans contrôle d'accès.

### Automatisation

- [ ] Les fichiers de configuration sont versionnés.
- [ ] La CI/CD exécute les validations requises.
- [ ] Les versions des images et outils sont maîtrisées en production.
- [ ] Le déploiement est suivi d'une vérification fonctionnelle.

## 27. Glossaire

**Alerting rule** : règle évaluée périodiquement pour déterminer si une condition doit produire une alerte.

**Alertmanager** : composant qui regroupe, route, inhibe et transmet les alertes de Prometheus.

**Cardinalité** : nombre de séries temporelles distinctes, déterminé par les noms de métriques et les combinaisons de labels.

**Counter** : compteur cumulatif d'événements.

**Exporter** : composant qui expose des métriques pour Prometheus.

**Gauge** : métrique représentant une valeur qui peut augmenter ou diminuer.

**Histogram** : métrique utilisée pour représenter la distribution d'observations au travers de buckets.

**Label** : paire clé-valeur qui identifie une dimension d'une série temporelle.

**PromQL** : langage de requête de Prometheus.

**Recording rule** : règle qui calcule une expression et enregistre son résultat sous une nouvelle série temporelle.

**Scrape** : opération par laquelle Prometheus interroge une cible pour récupérer ses métriques.

**Série temporelle** : succession d'échantillons identifiés par un nom de métrique et ses labels.

**Source de données Grafana** : connexion utilisée par Grafana pour interroger une plateforme de stockage ou de calcul.

**TSDB** : base de données optimisée pour les séries temporelles.

**SLI** : indicateur quantifiant une dimension de qualité de service.

**SLO** : objectif de niveau de service défini à partir d'indicateurs.

## 28. Références officielles

### Prometheus

- Documentation générale : https://prometheus.io/docs/introduction/overview/
- Prise en main : https://prometheus.io/docs/introduction/first_steps/
- Configuration : https://prometheus.io/docs/prometheus/latest/configuration/configuration/
- Modèle de données : https://prometheus.io/docs/concepts/
- Bases de PromQL : https://prometheus.io/docs/prometheus/latest/querying/basics/
- Fonctions PromQL : https://prometheus.io/docs/prometheus/latest/querying/functions/
- Convention de nommage : https://prometheus.io/docs/practices/naming/
- Instrumentation : https://prometheus.io/docs/practices/instrumentation/
- Exporters : https://prometheus.io/docs/instrumenting/exporters/
- Recording rules : https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/
- Alerting rules : https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Alertmanager : https://prometheus.io/docs/alerting/latest/alertmanager/
- Configuration d'Alertmanager : https://prometheus.io/docs/alerting/latest/configuration/
- Stockage : https://prometheus.io/docs/prometheus/latest/storage/
- API de gestion : https://prometheus.io/docs/prometheus/latest/management_api/

### node_exporter

- Dépôt officiel et instructions de déploiement : https://github.com/prometheus/node_exporter
- Guide de prise en main : https://prometheus.io/docs/guides/node-exporter/

### Grafana

- Documentation générale : https://grafana.com/docs/grafana/latest/
- Source de données Prometheus : https://grafana.com/docs/grafana/latest/datasources/prometheus/
- Sources de données : https://grafana.com/docs/grafana/latest/datasources/
- Provisionnement : https://grafana.com/docs/grafana/latest/administration/provisioning/
- Règles d'alerte : https://grafana.com/docs/grafana/latest/alerting/alerting-rules/
- Points de contact : https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/contact-points/

### Kubernetes

- Documentation officielle : https://kubernetes.io/docs/home/
- Prometheus Operator : https://prometheus-operator.dev/
- Chart Helm kube-prometheus-stack : https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack

### Docker

- Documentation Docker Compose : https://docs.docker.com/compose/
- Documentation Docker Engine : https://docs.docker.com/engine/

## 29. Bilan du niveau intermédiaire

À l'issue de ce cours, les notions essentielles à maîtriser sont les suivantes :

- Une architecture d'observabilité sépare l'instrumentation, la collecte, le stockage, la visualisation et le routage des alertes.
- Prometheus organise les métriques en séries temporelles, identifiées par leur nom et leurs labels.
- PromQL sert à filtrer, calculer, agréger et analyser les métriques.
- Grafana transforme ces données en tableaux de bord lisibles et réutilisables.
- Les alerting rules évaluent les conditions, tandis qu'Alertmanager assure le traitement et le routage des alertes.
- Les recording rules simplifient les requêtes réutilisées et peuvent réduire le coût de calcul.
- La sécurité, la rétention et la cardinalité font partie de la conception de la plateforme.
- Git, la CI/CD, Terraform et Ansible permettent de rendre le déploiement reproductible et contrôlé.
- Kubernetes demande une approche adaptée à la découverte dynamique des cibles.

La prochaine étape naturelle sera d'aller vers une plateforme d'observabilité plus complète : collecte à grande échelle, haute disponibilité, gestion de la rétention longue durée, alerting avancé, gouvernance des tableaux de bord et supervision multi-cluster.