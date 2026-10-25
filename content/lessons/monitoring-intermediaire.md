# Supervision avec Prometheus et Grafana

## Niveau intermédiaire

## 1. Présentation générale

Dans le cours débutant, nous avons appris à lire les journaux, à utiliser `journalctl`, à examiner les événements Windows et à comprendre les principales métriques d’un système.

L’objectif évolue maintenant : il ne suffit plus de consulter manuellement chaque serveur. Nous allons construire une plateforme capable de collecter les métriques de plusieurs machines, de les conserver dans le temps, de les interroger, de les afficher sous forme de tableaux de bord et de détecter automatiquement certaines dégradations.

Les deux outils principaux sont :

- **Prometheus** : collecte, stockage et interrogation des métriques, avec un moteur de règles.
- **Grafana** : visualisation des données, création de tableaux de bord et gestion des alertes selon la configuration choisie.

Nous ajouterons également :

- **Node Exporter** pour exposer les métriques système des machines Linux.
- **Windows Exporter** pour exposer les métriques des machines Windows.
- **Alertmanager** pour regrouper, router, inhiber et notifier les alertes générées notamment par Prometheus.
- **Docker Compose** pour construire un laboratoire reproductible.
- **Mailpit**, dans le laboratoire, pour recevoir les courriels de test sans utiliser de véritable serveur de messagerie.

Les exemples sont conçus pour apprendre et tester les mécanismes essentiels. Ils ne constituent pas une architecture de production prête à déployer sans adaptation, notamment pour les accès, la haute disponibilité, les sauvegardes et les secrets.

## 2. Objectifs pédagogiques

À la fin de ce cours, l’apprenant doit savoir :

1. Concevoir une architecture Prometheus et Grafana adaptée à une petite infrastructure.
2. Expliquer le fonctionnement de la collecte par interrogation (*scraping*).
3. Configurer les cibles de collecte dans Prometheus.
4. Installer et utiliser Node Exporter.
5. Ajouter une machine Windows avec Windows Exporter.
6. Comprendre les métriques, les labels et les séries temporelles.
7. Écrire des requêtes PromQL de difficulté intermédiaire.
8. Calculer l’utilisation CPU, mémoire, stockage et réseau.
9. Créer des tableaux de bord lisibles dans Grafana.
10. Définir des règles de calcul et des règles d’alerte.
11. Configurer un premier routage des alertes avec Alertmanager.
12. Comprendre la différence entre les alertes Prometheus et les alertes gérées par Grafana.
13. Diagnostiquer les problèmes de collecte et les données absentes.
14. Réduire le bruit des alertes et améliorer leur pertinence.
15. Sécuriser l’accès aux interfaces et aux endpoints de métriques.
16. Prévoir la conservation, la sauvegarde et la capacité de stockage des données.
17. Produire un rapport de supervision exploitable en exploitation.
18. Réaliser un laboratoire complet et vérifier le fonctionnement de chaque composant.

## 3. Rappel des notions fondamentales

### 3.1 Journaux, métriques et traces

Les données d’observabilité ne répondent pas toutes aux mêmes questions.

| Type | Question principale | Exemple |
|---|---|---|
| Métrique | Comment le système évolue-t-il ? | CPU à 92 % pendant dix minutes |
| Journal | Quel événement s’est produit ? | Échec de connexion à une base de données |
| Trace distribuée | Par quels composants une requête est-elle passée ? | Reverse proxy → API → base de données |
| Alerte | Une condition exige-t-elle une action ? | Le disque dispose de moins de 10 % d’espace libre |

Prometheus est avant tout un système de métriques. Grafana peut visualiser plusieurs types de données, mais il ne stocke pas automatiquement toutes les données dont les panneaux ont besoin.

Pour superviser les journaux avec l’écosystème Grafana, on peut ajouter Loki et Grafana Alloy. Cette extension sera présentée plus loin.

### 3.2 Une métrique n'est pas une valeur isolée

Supposons que le processeur affiche 95 % d’utilisation.

Cette information seule ne permet pas de déterminer :

- Depuis combien de temps le CPU est sollicité.
- Si le niveau est normal pour cette application.
- Si une seule machine est concernée.
- Si la charge augmente ou diminue.
- Si les utilisateurs subissent une dégradation.
- Si un processus ou une dépendance est responsable.

Prometheus conserve des échantillons horodatés. Il devient possible d’étudier la tendance et de calculer des indicateurs dérivés.

```text
Utilisation CPU
100 % |                         *
 90 % |                    *    *
 80 % |               *    *
 70 % |          *    *
 60 % |     *    *
 50 % |  *
      +--------------------------------
        08h00 08h05 08h10 08h15 08h20

La tendance montre une montée progressive.
Une valeur instantanée ne raconterait pas
la même histoire.
```

Ce dessin est une illustration textuelle et non une mesure réelle.

## 4. Architecture de référence

### 4.1 Architecture générale

Une architecture simple comprend les éléments suivants :

```text
             SERVEUR LINUX-01
                  |
                  v
             Node Exporter
                  |
                  | Métriques HTTP
                  |
                  v
              Prometheus
                  |
          +-------+-------+
          |               |
          v               v
     PromQL / API      Règles d'alerte
          |               |
          v               v
       Grafana        Alertmanager
          |               |
          v               v
     Tableaux de bord   Notifications
                          |
                          v
                  Équipe d'exploitation
```

Node Exporter expose les métriques de la machine. Prometheus les collecte. Grafana interroge Prometheus pour construire les visualisations. Prometheus évalue les règles d’alerte et transmet les alertes à Alertmanager.

Alertmanager organise ensuite leur traitement : regroupement, routage, inhibition, silences et notifications vers les destinataires configurés.

### 4.2 Architecture multi-serveurs

```text
                  INFRASTRUCTURE
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
  Linux Web        Linux Base       Windows Server
       |                |                |
       v                v                v
 Node Exporter     Node Exporter   Windows Exporter
       |                |                |
       +----------------+----------------+
                        |
                        v
                   Prometheus
                        |
              +---------+---------+
              |                   |
              v                   v
           Grafana            Alertmanager
              |                   |
              v                   v
       Tableau de bord        Notifications
```

Les exportateurs n’ont pas besoin d’envoyer spontanément leurs métriques à Prometheus. Dans le modèle classique, ils exposent un endpoint que Prometheus interroge régulièrement.

### 4.3 Architecture de production : le point à retenir

Dans une petite installation, une seule instance de Prometheus peut convenir. Dans un environnement critique, il faut examiner les risques supplémentaires :

- Panne de l’instance Prometheus.
- Saturation du disque de stockage des métriques.
- Indisponibilité du réseau de collecte.
- Perte de données après une erreur de configuration.
- Défaillance de Grafana ou d’Alertmanager.
- Indisponibilité du canal de notification.
- Compromission des interfaces d’administration.

Une interface accessible ne prouve pas que la collecte fonctionne. De même, une collecte en bon état ne prouve pas qu’une notification d’alerte arrive à son destinataire.

## 5. Comprendre Prometheus

### 5.1 Le fonctionnement de la collecte

Prometheus utilise généralement un mécanisme appelé *scraping* : il interroge les endpoints de métriques définis dans sa configuration.

Un cycle de collecte se déroule ainsi :

```text
1. Prometheus lit sa configuration
             |
             v
2. Il identifie les cibles à interroger
             |
             v
3. Il envoie une requête HTTP
             |
             v
4. La cible renvoie ses métriques
             |
             v
5. Prometheus interprète les données
             |
             v
6. Les échantillons sont stockés
             |
             v
7. Les requêtes et règles utilisent les données
```

Une cible qui échoue à répondre peut être marquée indisponible pour la collecte, mais cela ne signifie pas nécessairement que le serveur entier est arrêté.

### 5.2 Le modèle *pull*

Dans le modèle *pull*, c’est Prometheus qui interroge la cible.

Avantages :

- Les cibles n’ont pas besoin d’envoyer en permanence des données.
- Prometheus peut mesurer les échecs de collecte.
- La fréquence est déterminée dans la configuration.
- Il est facile d’examiner les cibles depuis l’interface de Prometheus.

Limites :

- Prometheus doit pouvoir joindre les endpoints.
- Les pare-feu doivent autoriser la collecte depuis les bonnes sources.
- Une machine inaccessible ne fournit plus ses métriques.
- Une cible mal configurée peut rester absente de la supervision.

D’autres mécanismes existent pour des environnements particuliers. Le modèle *pull* demeure le point de départ de ce cours.

### 5.3 Le format des métriques

Un endpoint Prometheus renvoie souvent des données textuelles structurées selon son format d’exposition.

Exemple simplifié :

```text
# HELP example_requests_total Nombre de requêtes
# TYPE example_requests_total counter
example_requests_total{service="web"} 120
example_requests_total{service="api"} 85
```

On y retrouve :

- Le nom de la métrique.
- Son type.
- Ses labels éventuels.
- Sa valeur numérique.

Les lignes `HELP` et `TYPE` apportent des informations utiles sur le sens de la métrique et sur la façon de l’interpréter.

### 5.4 Les types de métriques

Les principaux types rencontrés sont :

| Type | Utilité | Exemple |
|---|---|---|
| Counter | Compteur croissant, remis à zéro lors d'un redémarrage éventuel du processus | Nombre total de requêtes |
| Gauge | Valeur qui peut monter ou descendre | Mémoire disponible |
| Histogram | Distribution d'observations dans des compartiments | Durée des requêtes |
| Summary | Statistiques calculées à partir d'observations | Quantiles et somme d'une durée |

Un compteur ne représente pas directement un débit. Pour mesurer une vitesse à partir d’un compteur, on emploie souvent `rate()` ou `increase()` dans PromQL.

Les histogrammes et les summaries n’ont pas les mêmes propriétés d’agrégation. Il faut connaître la structure de la métrique avant d’utiliser une requête de percentile.

## 6. Comprendre les labels et les séries temporelles

### 6.1 Qu'est-ce qu'un label ?

Un label est une dimension descriptive attachée à une série temporelle.

Exemple :

```text
http_requests_total{
    job="web",
    instance="192.0.2.10:9100",
    method="GET",
    status="200"
} 250
```

La métrique est `http_requests_total`.

Les labels indiquent notamment :

- Le groupe de collecte.
- La cible.
- La méthode HTTP.
- Le code de statut.

L’adresse `192.0.2.10` appartient ici à la plage réservée à la documentation. Elle doit être remplacée dans un environnement réel.

### 6.2 Une série temporelle est identifiée par son nom et ses labels

Les séries suivantes sont distinctes :

```text
http_requests_total{method="GET",status="200"} 100
http_requests_total{method="GET",status="500"} 7
http_requests_total{method="POST",status="200"} 55
```

Elles possèdent le même nom de métrique, mais pas le même ensemble de labels.

Cette distinction permet de filtrer et d’agréger les mesures.

### 6.3 Attention à la cardinalité

La cardinalité correspond au nombre de séries distinctes produites par les noms de métriques et leurs combinaisons de labels.

Une cardinalité excessive peut augmenter la mémoire nécessaire, l’espace disque consommé et le coût des requêtes.

Exemple dangereux :

```text
http_requests_total{
    user_id="utilisateur-123456",
    request_id="req-unique-987654",
    url="/commande/987654"
}
```

Si chaque requête génère des valeurs différentes, le nombre de séries peut devenir très important.

Préférer des dimensions bornées :

```text
http_requests_total{
    service="commande",
    method="POST",
    status_class="2xx"
}
```

Les identifiants individuels et les URL non normalisées sont généralement mieux adaptés aux journaux ou aux traces qu’aux labels de métriques.

### 6.4 Bonnes pratiques pour les labels

Utiliser des labels pour des dimensions dont le nombre de valeurs reste maîtrisé, par exemple :

- `environment="production"`.
- `region="douala"`.
- `service="web"`.
- `role="database"`.
- `job="linux"`.
- `instance="srv-web-01:9100"`.

Éviter les données arbitrairement variables, les jetons secrets, les adresses e-mail des utilisateurs et les identifiants de requête uniques.

Les noms des labels doivent être cohérents entre les services afin de faciliter les filtres et les comparaisons.

## 7. Préparer un laboratoire reproductible

Nous allons construire le laboratoire suivant :

- Prometheus : `http://localhost:9090`
- Grafana : `http://localhost:3000`
- Alertmanager : `http://localhost:9093`
- Mailpit : `http://localhost:8025`
- Node Exporter : accessible uniquement à l’intérieur du réseau du laboratoire.

Mailpit est un serveur de réception de courriels de test. Il permettra de vérifier le trajet d’une alerte jusqu’à une notification sans envoyer de véritable courriel.

### 7.1 Prérequis

Installer une version récente et prise en charge de Docker Engine et du plugin Docker Compose sur l’environnement choisi.

Vérifier les commandes disponibles :

```bash
docker --version
docker compose version
```

Ce laboratoire convient à une machine Linux ou à un environnement Docker correctement configuré. Les montages du système hôte dans Node Exporter peuvent différer sous Windows ou macOS ; les instructions de collecte de métriques de l’hôte sont principalement adaptées à Linux.

### 7.2 Créer l'arborescence

```bash
mkdir -p monitoring-lab/grafana/provisioning/datasources
cd monitoring-lab
```

Nous allons créer les fichiers suivants :

```text
monitoring-lab/
|
+-- compose.yml
|
+-- prometheus.yml
|
+-- rules.yml
|
+-- alertmanager.yml
|
+-- grafana/
    |
    +-- provisioning/
        |
        +-- datasources/
            |
            +-- prometheus.yml
```

Chaque fichier joue un rôle distinct :

| Fichier | Fonction |
|---|---|
| `compose.yml` | Décrit les conteneurs du laboratoire |
| `prometheus.yml` | Définit les cibles, la collecte et les services d’alerte |
| `rules.yml` | Définit les règles de calcul et les alertes |
| `alertmanager.yml` | Configure le regroupement et le routage des alertes |
| `grafana/provisioning/datasources/prometheus.yml` | Configure automatiquement la source de données Grafana |

Les fichiers peuvent être créés avec un éditeur de texte. Respecter l’indentation des fichiers YAML.

## 8. Déployer le laboratoire avec Docker Compose

### 8.1 Fichier `compose.yml`

Créer le fichier avec le contenu suivant :

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: monitoring-prometheus
    restart: unless-stopped
    ports:
      - "127.0.0.1:9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--storage.tsdb.retention.time=15d"
    volumes:
      - "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"
      - "./rules.yml:/etc/prometheus/rules.yml:ro"
      - "prometheus-data:/prometheus"
    depends_on:
      - node-exporter
      - alertmanager

  node-exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: monitoring-node-exporter
    restart: unless-stopped
    pid: host
    command:
      - "--path.procfs=/host/proc"
      - "--path.sysfs=/host/sys"
      - "--path.rootfs=/host"
    volumes:
      - "/proc:/host/proc:ro"
      - "/sys:/host/sys:ro"
      - "/:/host:ro,rslave"
    expose:
      - "9100"

  alertmanager:
    image: prom/alertmanager:latest
    container_name: monitoring-alertmanager
    restart: unless-stopped
    ports:
      - "127.0.0.1:9093:9093"
    command:
      - "--config.file=/etc/alertmanager/alertmanager.yml"
    volumes:
      - "./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro"
      - "alertmanager-data:/alertmanager"
    depends_on:
      - mailpit

  mailpit:
    image: axllent/mailpit:latest
    container_name: monitoring-mailpit
    restart: unless-stopped
    ports:
      - "127.0.0.1:8025:8025"

  grafana:
    image: grafana/grafana:latest
    container_name: monitoring-grafana
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - "grafana-data:/var/lib/grafana"
      - "./grafana/provisioning/datasources/prometheus.yml:/etc/grafana/provisioning/datasources/prometheus.yml:ro"
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  alertmanager-data:
  grafana-data:
```

Points importants :

- Les interfaces Web sont liées à `127.0.0.1`. Elles ne sont donc pas publiées directement sur toutes les interfaces réseau de l’hôte.
- Node Exporter n’a pas de port publié sur l’hôte. Prometheus l’interroge au travers du réseau Docker.
- Les volumes nommés préservent les données entre les redémarrages des conteneurs.
- Les répertoires du système hôte montés dans Node Exporter sont utilisés pour observer la machine Linux, pas uniquement le conteneur.
- La durée de conservation de quinze jours est un paramètre de laboratoire, pas une recommandation universelle.

Les images utilisent volontairement le tag `latest` pour simplifier le démarrage du laboratoire. Pour un usage durable ou en production, choisir des versions compatibles et explicites, puis les valider avant le déploiement. Éviter de faire dépendre un environnement critique d’un tag flottant.

### 8.2 Pourquoi Grafana utilise-t-il `localhost` et Prometheus le nom du conteneur ?

Depuis le navigateur de l’utilisateur, Grafana est accessible à l’adresse locale `http://localhost:3000`.

En revanche, depuis le conteneur Grafana, `localhost` désigne le conteneur Grafana lui-même.

La source de données Grafana utilisera donc l’adresse :

```text
http://prometheus:9090
```

Le nom `prometheus` est résolu dans le réseau du projet Docker Compose.

C’est une distinction fondamentale entre le réseau vu par le navigateur et le réseau vu par les conteneurs.

### 8.3 Fichier `prometheus.yml`

Créer ce fichier à la racine du laboratoire :

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

  external_labels:
    environment: "lab"

rule_files:
  - "/etc/prometheus/rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - "alertmanager:9093"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets:
          - "prometheus:9090"

  - job_name: "linux"
    static_configs:
      - targets:
          - "node-exporter:9100"
```

Explication :

**`scrape_interval`** définit la fréquence normale de collecte.

**`evaluation_interval`** définit à quelle fréquence Prometheus évalue les règles.

**`external_labels`** ajoute un contexte d’identification aux données concernées lorsqu’elles sont transmises vers des systèmes externes compatibles.

**`rule_files`** indique où se trouve le fichier de règles.

**`alerting`** identifie le service Alertmanager auquel transmettre les alertes.

**`scrape_configs`** décrit les groupes de cibles à collecter.

**`job_name`** nomme le groupe de collecte. Ce nom devient notamment un label de la métrique `up`.

**`targets`** contient les adresses des endpoints de métriques.

### 8.4 Fichier `rules.yml`

Créer les règles de calcul et les premières alertes :

```yaml
groups:
  - name: host-recording
    interval: 30s
    rules:
      - record: instance:node_cpu_utilisation:rate5m
        expr: |
          100 * (
            1 - avg by (job, instance) (
              rate(node_cpu_seconds_total{mode="idle"}[5m])
            )
          )

  - name: host-alerts
    rules:
      - alert: MonitoringTargetDown
        expr: up == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Cible de supervision indisponible"
          description: >-
            La cible {{ $labels.instance }} du job
            {{ $labels.job }} n'est pas collectée correctement.

      - alert: HostCpuHigh
        expr: instance:node_cpu_utilisation:rate5m > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation CPU élevée"
          description: >-
            La cible {{ $labels.instance }} présente
            une utilisation CPU élevée depuis au moins dix minutes.

      - alert: HostMemoryAvailableLow
        expr: |
          (
            node_memory_MemAvailable_bytes
            /
            node_memory_MemTotal_bytes
          ) < 0.10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Mémoire disponible faible"
          description: >-
            La mémoire disponible de {{ $labels.instance }}
            est inférieure à 10 % de la mémoire totale.

      - alert: HostDiskSpaceLow
        expr: |
          (
            node_filesystem_avail_bytes{
              fstype!~"tmpfs|overlay|squashfs|nsfs",
              mountpoint!~"/run.*"
            }
            /
            node_filesystem_size_bytes{
              fstype!~"tmpfs|overlay|squashfs|nsfs",
              mountpoint!~"/run.*"
            }
          ) < 0.10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Espace disque faible"
          description: >-
            Le système de fichiers monté sur
            {{ $labels.mountpoint }} sur {{ $labels.instance }}
            dispose de moins de 10 % d'espace disponible.
```

Cette configuration montre deux mécanismes différents.

La règle `record` calcule une métrique dérivée à partir des données CPU. Cette métrique enregistrée est plus facile à réutiliser dans les tableaux de bord et les alertes.

Les règles `alert` évaluent des conditions. Le champ `for` évite ici qu’une anomalie très brève déclenche immédiatement une notification.

Les seuils sont des exemples à ajuster. Un CPU élevé peut être normal sur un serveur de calcul, et 10 % de mémoire disponible peut être acceptable ou insuffisant selon le type de charge.

Le filtre des systèmes de fichiers doit également être adapté à l’environnement. La liste des systèmes de fichiers pertinents dépend notamment du système d’exploitation et de la configuration de stockage.

### 8.5 Fichier `alertmanager.yml`

Créer ce fichier à la racine :

```yaml
global:
  smtp_smarthost: "mailpit:1025"
  smtp_from: "alertmanager@example.test"
  smtp_require_tls: false

route:
  receiver: "lab-email"
  group_by:
    - alertname
    - job
    - instance
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 1h

receivers:
  - name: "lab-email"
    email_configs:
      - to: "ops@example.test"
        send_resolved: true
```

Cette configuration est réservée au laboratoire.

Le service Mailpit reçoit les courriels de test et les présente dans son interface Web. Il ne s’agit pas d’un véritable acheminement vers une boîte de réception externe.

Le paramètre `smtp_require_tls: false` est acceptable uniquement dans ce réseau de test local. Pour un véritable serveur de messagerie, configurer la sécurité du transport, l’authentification et la gestion des secrets conformément à l’environnement.

Ne pas copier cette configuration SMTP sans adaptation dans une infrastructure de production.

### 8.6 Provisionner automatiquement la source de données Grafana

Créer `grafana/provisioning/datasources/prometheus.yml` :

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

Cette configuration permet à Grafana de créer automatiquement sa source de données Prometheus au démarrage.

La connexion est établie depuis Grafana vers le service nommé `prometheus`. Le navigateur de l’utilisateur n’a pas besoin de joindre directement le port de Prometheus pour que les graphiques fonctionnent.

### 8.7 Vérifier la configuration et lancer le laboratoire

Depuis le répertoire `monitoring-lab` :

```bash
docker compose config
```

Cette commande vérifie la structure et les paramètres que Docker Compose comprend. Elle ne valide pas à elle seule la syntaxe de chaque fichier propre aux applications.

Démarrer ensuite les composants :

```bash
docker compose up -d
```

Vérifier leur état :

```bash
docker compose ps
```

Consulter les journaux du conteneur Prometheus :

```bash
docker compose logs --tail=100 prometheus
```

Pour suivre ceux d’Alertmanager :

```bash
docker compose logs -f alertmanager
```

Pour arrêter le laboratoire :

```bash
docker compose down
```

Cette dernière commande conserve normalement les volumes nommés.

La commande suivante supprime également les volumes du laboratoire :

```bash
docker compose down -v
```

**Attention :** cette seconde commande efface les données persistées dans les volumes concernés, notamment les métriques du laboratoire et la base de données Grafana. Ne l’utiliser que si cette suppression est intentionnelle.

## 9. Vérifier la collecte des métriques

### 9.1 Vérifier les endpoints

Depuis la machine hôte, essayer :

```bash
curl -I http://localhost:9090/
curl -I http://localhost:3000/
curl -I http://localhost:9093/
```

Le résultat exact peut varier selon la version et la route demandée. L’objectif est de vérifier que les interfaces Web répondent.

Pour vérifier Node Exporter, utiliser un conteneur du même réseau Docker ou examiner les métriques depuis Prometheus.

Depuis un conteneur temporaire présent sur le réseau par défaut du projet, on peut utiliser un client HTTP disponible, ou exécuter un test depuis le conteneur Prometheus s’il possède l’outil nécessaire.

Le simple fait que le port soit ouvert ne garantit pas que des métriques valides soient collectées.

### 9.2 Vérifier les cibles dans Prometheus

Ouvrir :

`http://localhost:9090/targets`

Vérifier que les cibles des jobs `prometheus` et `linux` apparaissent en état `UP`.

Les états ont la signification générale suivante :

| État | Interprétation |
|---|---|
| UP | Dernière collecte réussie |
| DOWN | Échec du dernier contrôle de collecte |
| Cible absente | Elle n'apparaît pas dans la cible découverte ou configurée |

Une cible en état `UP` indique que Prometheus peut collecter ses métriques. Cela ne prouve pas que tous les services de la machine sont opérationnels.

### 9.3 Explorer la métrique `up`

Dans l’interface de Prometheus, ouvrir le navigateur d’expressions et exécuter :

```promql
up
```

Pour sélectionner uniquement les cibles Linux :

```promql
up{job="linux"}
```

Le résultat attendu dans le laboratoire est une série associée à la cible `node-exporter:9100`.

La valeur `1` indique que la collecte de la cible a réussi. La valeur `0` signale un échec de collecte.

### 9.4 Afficher la liste des métriques système

Interroger :

```promql
node_exporter_build_info
```

Cette métrique permet notamment de confirmer la présence de données associées à l’exportateur.

On peut également essayer :

```promql
node_cpu_seconds_total
```

ou :

```promql
node_memory_MemAvailable_bytes
```

Si une requête ne renvoie aucune série, cela peut signaler :

- Un exportateur absent.
- Une cible non collectée.
- Une métrique non exposée.
- Un nom de métrique incorrect.
- Une période de conservation sans échantillon correspondant.
- Un filtre de collecte ou une configuration inadaptée.

## 10. Ajouter un serveur Linux distant

Le laboratoire expose d’abord les métriques de la machine Linux observée par Node Exporter dans le conteneur.

Pour surveiller un deuxième serveur Linux, il faut installer Node Exporter sur ce serveur ou utiliser un déploiement adapté à son environnement.

### 10.1 Installer Node Exporter

La documentation officielle propose les archives correspondant aux systèmes et architectures pris en charge :

https://prometheus.io/docs/guides/node-exporter/

Les grandes étapes d’une installation native sont les suivantes :

1. Identifier le système d’exploitation et l’architecture.
2. Télécharger la version appropriée depuis la source officielle.
3. Vérifier la provenance et l’intégrité de l’artefact selon la procédure retenue.
4. Créer un compte système dédié.
5. Installer le binaire dans un emplacement contrôlé.
6. Créer un service systemd.
7. Configurer le port d’écoute et le pare-feu.
8. Vérifier l’endpoint `/metrics`.
9. Ajouter la cible dans Prometheus.
10. Confirmer l’état `UP`.

Node Exporter n’a pas besoin de privilèges administrateur globaux pour tous les cas d’usage. Les permissions nécessaires dépendent des collecteurs et des métriques choisies.

### 10.2 Tester l'exportateur sur le serveur distant

Depuis un poste ou un serveur autorisé à accéder à l’exportateur :

```bash
curl http://ADRESSE_DU_SERVEUR:9100/metrics
```

Remplacer `ADRESSE_DU_SERVEUR` par le nom DNS ou l’adresse IP réelle.

Si le test échoue, vérifier :

- L’état du service Node Exporter.
- Le port configuré.
- L’adresse d’écoute.
- Le pare-feu du serveur.
- Le routage entre les machines.
- Les règles de sécurité du réseau.
- La présence d’un proxy ou d’un filtrage intermédiaire.

### 10.3 Limiter les accès

Node Exporter expose des informations opérationnelles. Il ne doit pas être accessible librement depuis Internet.

Dans un réseau d’administration :

```text
                PROMETHEUS
              192.0.2.20
                   |
                   | TCP/9100
                   |
                   v
             PARE-FEU
                   |
                   v
           SERVEUR LINUX DISTANT
             192.0.2.40
             Node Exporter
```

Les adresses appartiennent à une plage de documentation et ne sont pas destinées à être utilisées comme adresses réelles.

Autoriser TCP/9100 uniquement depuis les serveurs de collecte appropriés. En environnement de production, étudier la segmentation réseau, le chiffrement, l’authentification éventuelle de l’accès et la protection du plan d’administration.

### 10.4 Ajouter la cible dans Prometheus

Ajouter un job au fichier `prometheus.yml` :

```yaml
  - job_name: "linux-remote"
    static_configs:
      - targets:
          - "192.0.2.40:9100"
        labels:
          environment: "production"
          role: "web"
```

Remplacer l’adresse par celle de l’hôte réel.

Après modification, valider puis recharger la configuration selon la procédure de déploiement de Prometheus.

La configuration de Prometheus est chargée au démarrage. Le rechargement à chaud nécessite que le mécanisme prévu soit disponible et activé. En production, préférer une procédure d’exploitation testée plutôt que d’activer sans réflexion une interface de rechargement.

## 11. Ajouter un serveur Windows

### 11.1 Le rôle de Windows Exporter

Windows Exporter expose des métriques du système et de certains composants Windows sous une forme exploitable par Prometheus.

Selon les collecteurs activés, les données peuvent inclure :

- CPU.
- Mémoire.
- Réseau.
- Disques logiques.
- Services.
- Informations système.
- Composants Windows ou rôles spécifiques.

La disponibilité de certains collecteurs dépend du système d’exploitation, des permissions et de la configuration.

Documentation officielle :

https://github.com/prometheus-community/windows_exporter

### 11.2 Installer Windows Exporter

Sur un environnement de laboratoire :

1. Télécharger une version prise en charge depuis la publication officielle du projet.
2. Vérifier l’intégrité de l’installateur.
3. Installer le service.
4. Configurer les collecteurs nécessaires.
5. Définir l’accès réseau à l’endpoint.
6. Vérifier que le service est démarré.
7. Tester la page `/metrics`.

Le port par défaut généralement utilisé par Windows Exporter est `9182`, mais la configuration peut le changer.

### 11.3 Vérifier les métriques Windows

Sur la machine Windows, consulter le service Windows Exporter.

Depuis un poste autorisé à joindre son endpoint :

```text
http://NOM_DU_SERVEUR_WINDOWS:9182/metrics
```

La réponse devrait contenir des métriques exposées par l’exportateur. Il ne faut pas publier cet endpoint directement sur Internet.

### 11.4 Ajouter la cible Windows à Prometheus

Dans le fichier de configuration :

```yaml
  - job_name: "windows"
    static_configs:
      - targets:
          - "192.0.2.50:9182"
        labels:
          environment: "production"
          role: "windows-server"
```

Remplacer l’adresse par celle du serveur Windows.

Après chargement de la configuration, consulter la page `/targets` pour confirmer l’état de la collecte.

### 11.5 Pourquoi les métriques Windows peuvent-elles être absentes ?

Plusieurs causes sont possibles :

- Le service Windows Exporter est arrêté.
- Le pare-feu bloque le port.
- La cible est erronée.
- Le collecteur demandé n’est pas activé.
- L’accès aux données dépend de droits insuffisants.
- Une version ne prend pas en charge un collecteur ou une plateforme spécifique.

Ne pas conclure immédiatement que le serveur Windows est défaillant parce que sa cible Prometheus est en état `DOWN`.

## 12. Maîtriser les bases de PromQL

PromQL est le langage d’expression et de requête de Prometheus.

Il permet de sélectionner les séries, de filtrer les labels, de calculer des taux, d’agréger des données et de construire des indicateurs.

### 12.1 Afficher une métrique

```promql
node_memory_MemAvailable_bytes
```

Cette requête renvoie la mémoire disponible exposée par Node Exporter pour chaque cible qui fournit cette métrique.

### 12.2 Sélectionner avec un label

```promql
up{job="linux"}
```

La requête sélectionne les séries `up` dont le label `job` est égal à `linux`.

Plusieurs opérateurs sont disponibles :

| Opérateur | Fonction |
|---|---|
| `=` | Correspondance exacte |
| `!=` | Valeur différente |
| `=~` | Correspondance par expression régulière |
| `!~` | Absence de correspondance avec une expression régulière |

Exemples :

```promql
up{job="linux"}
```

```promql
up{environment="production"}
```

```promql
up{instance=~"srv-web-.*"}
```

Les labels utilisés dans les exemples doivent réellement exister sur les séries concernées.

### 12.3 Sélectionner une période

Une sélection de plage permet de travailler sur plusieurs échantillons :

```promql
node_cpu_seconds_total[5m]
```

Cette expression demande les échantillons du compteur sur les cinq dernières minutes pour chaque série correspondante.

Les fonctions telles que `rate()` et `increase()` utilisent ce type de sélection pour calculer une évolution.

### 12.4 Comprendre `rate()`

La fonction `rate()` estime le taux moyen d’augmentation d’un compteur sur une fenêtre donnée.

Exemple :

```promql
rate(node_cpu_seconds_total[5m])
```

Le résultat n’est pas le total cumulé, mais une estimation du rythme de progression du compteur.

Pour un compteur de requêtes HTTP, `rate(...[5m])` peut représenter le nombre moyen de requêtes par seconde sur cinq minutes.

### 12.5 Comprendre `increase()`

La fonction `increase()` estime l’augmentation d’un compteur sur une période.

Exemple :

```promql
increase(example_requests_total[1h])
```

Cette requête estime le nombre de requêtes supplémentaires sur la dernière heure pour les séries correspondantes.

Le résultat peut être fractionnaire, car Prometheus extrapole les variations observées aux limites de la fenêtre.

### 12.6 Comprendre `sum by`

`sum by` permet de regrouper plusieurs séries selon un ou plusieurs labels.

Exemple :

```promql
sum by (job) (
  rate(example_requests_total[5m])
)
```

Cela calcule le taux de requêtes par job. Les autres dimensions de labels sont agrégées.

### 12.7 Comprendre `avg by`

`avg by` calcule une moyenne en conservant les dimensions indiquées.

Exemple :

```promql
avg by (instance) (
  rate(node_cpu_seconds_total{mode="idle"}[5m])
)
```

Cette requête calcule une moyenne par instance à partir des séries qui correspondent au mode `idle`.

Les agrégations doivent être choisies avec attention : conserver ou supprimer un label change le sens de l’indicateur.

## 13. Requêtes PromQL utiles pour les serveurs

Les noms de métriques ci-dessous correspondent aux métriques habituelles de Node Exporter. Leur présence doit être vérifiée sur les cibles utilisées.

### 13.1 État des cibles

Afficher tous les résultats de collecte :

```promql
up
```

Cibler Linux :

```promql
up{job="linux"}
```

Cibler Windows :

```promql
up{job="windows"}
```

Afficher uniquement les cibles dont le dernier contrôle échoue :

```promql
up == 0
```

Cette dernière requête filtre les séries qui existent et dont la valeur est égale à zéro. Elle ne remplace pas une règle traitant la disparition complète d’un job.

### 13.2 Calculer l'utilisation CPU

```promql
100 * (
  1 - avg by (instance) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  )
)
```

Cette requête estime le pourcentage de temps CPU non idle sur les cinq dernières minutes, agrégé par instance.

Interprétation :

- Une valeur proche de zéro indique une faible activité CPU selon cette mesure.
- Une valeur élevée indique une utilisation importante.
- Une valeur durablement élevée peut nécessiter une analyse.

Elle ne mesure pas directement tous les types de contention observables dans les hyperviseurs. Les métriques d’attente CPU, la latence et les besoins des applications peuvent également être nécessaires.

### 13.3 Calculer le pourcentage de mémoire utilisée

```promql
100 * (
  1 -
  (
    node_memory_MemAvailable_bytes
    /
    node_memory_MemTotal_bytes
  )
)
```

Cette expression estime le pourcentage de mémoire non disponible à partir de la mémoire totale et de `MemAvailable`.

Il faut éviter de confondre mémoire disponible et mémoire strictement inutilisée. Linux utilise une partie de la mémoire à des fins de cache et peut la récupérer selon les besoins.

### 13.4 Calculer l'utilisation d'un système de fichiers

```promql
100 * (
  1 -
  (
    node_filesystem_avail_bytes{
      fstype!~"tmpfs|overlay|squashfs|nsfs",
      mountpoint!~"/run.*"
    }
    /
    node_filesystem_size_bytes{
      fstype!~"tmpfs|overlay|squashfs|nsfs",
      mountpoint!~"/run.*"
    }
  )
)
```

Cette requête estime le pourcentage occupé d’après l’espace disponible et la taille totale exposée.

Les systèmes de fichiers exclus ne représentent qu’un exemple de filtrage. Il faut adapter la sélection aux volumes réellement utiles.

Les systèmes de fichiers de taille nulle, en erreur ou temporaires peuvent nécessiter des filtres supplémentaires. Avant d’utiliser cette requête dans une alerte, inspecter les séries renvoyées et valider les résultats.

### 13.5 Calculer le débit réseau entrant

```promql
sum by (instance) (
  rate(
    node_network_receive_bytes_total{
      device!~"lo|veth.*|docker.*"
    }[5m]
  )
) * 8
```

Le résultat est exprimé en bits par seconde, à partir du taux d’évolution du compteur d’octets reçus.

Pour obtenir un débit en mégabits par seconde, on peut diviser le résultat par un million :

```promql
sum by (instance) (
  rate(
    node_network_receive_bytes_total{
      device!~"lo|veth.*|docker.*"
    }[5m]
  )
) * 8 / 1000000
```

Le filtre d’interfaces doit être adapté au serveur. Ne pas exclure automatiquement une interface sans avoir vérifié son rôle.

### 13.6 Calculer le débit réseau sortant

```promql
sum by (instance) (
  rate(
    node_network_transmit_bytes_total{
      device!~"lo|veth.*|docker.*"
    }[5m]
  )
) * 8 / 1000000
```

Le résultat est exprimé ici en mégabits par seconde selon une convention décimale.

### 13.7 Compter les requêtes HTTP

Si une application expose un compteur compatible nommé `http_requests_total` :

```promql
sum by (job) (
  rate(http_requests_total[5m])
)
```

Cette requête estime le taux de requêtes par seconde, regroupé par job.

Node Exporter ne fournit pas automatiquement toutes les métriques applicatives. Pour obtenir les métriques HTTP, il faut une instrumentation de l’application ou un exportateur adapté.

### 13.8 Calculer un taux d'erreur HTTP

Si l’application expose un label `status` sur la métrique de requêtes :

```promql
100 *
sum by (job) (
  rate(http_requests_total{status=~"5.."}[5m])
)
/
sum by (job) (
  rate(http_requests_total[5m])
)
```

Cette expression estime le pourcentage de requêtes HTTP de classe 5xx.

Elle suppose que les labels et les séries sont cohérents entre les deux sélections et que le total de requêtes est non nul.

Si le dénominateur est nul ou si les métriques sont absentes, le résultat peut être absent ou indéfini. Il faut traiter ces cas lorsque l’indicateur alimente des alertes de production.

## 14. Requêtes plus avancées : latence et agrégation

### 14.1 Comprendre les percentiles

Une moyenne peut masquer les lenteurs rencontrées par une partie des utilisateurs.

Par exemple, si la majorité des requêtes répond en quelques dizaines de millisecondes mais que quelques-unes prennent plusieurs secondes, une moyenne peut donner une impression trop favorable.

Le percentile 95, ou p95, désigne une valeur sous laquelle se situent environ 95 % des observations de la distribution considérée.

Pour calculer un p95 à partir d’un histogramme classique exposant `http_request_duration_seconds_bucket` :

```promql
histogram_quantile(
  0.95,
  sum by (le, job) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

Cette requête suppose que la métrique existe et que les buckets sont correctement exposés. Elle n’est pas applicable telle quelle à une application qui n’expose pas ces séries.

Le p95 d’un histogramme classique est une estimation à partir de ses compartiments. La précision dépend de la distribution et des bornes des buckets.

### 14.2 Comparer plusieurs serveurs

Pour calculer le CPU par instance :

```promql
instance:node_cpu_utilisation:rate5m
```

Pour regrouper les mesures par environnement, à condition que les labels soient présents sur les séries concernées :

```promql
avg by (environment) (
  instance:node_cpu_utilisation:rate5m
)
```

La moyenne d’un environnement peut cacher une machine en surcharge. Il est donc utile de conserver des vues individuelles et des vues agrégées.

### 14.3 Le piège de l'agrégation

Une moyenne sur dix serveurs n’implique pas que chaque serveur fonctionne correctement.

Exemple :

```text
Serveur A : 20 %
Serveur B : 25 %
Serveur C : 27 %
Serveur D : 95 %

Moyenne : 41,75 %
```

Le résultat moyen ne montre pas à lui seul le niveau élevé du serveur D.

Pour une supervision opérationnelle, prévoir :

- La vue globale.
- La vue par instance.
- La liste des cibles indisponibles.
- La vue des valeurs maximales ou des exceptions.
- Les tendances dans le temps.

## 15. Créer et organiser les tableaux de bord Grafana

### 15.1 Première connexion

Ouvrir :

`http://localhost:3000`

Dans le laboratoire, une installation neuve de Grafana propose généralement un compte initial avec des identifiants par défaut. Les étapes de première connexion peuvent imposer un changement de mot de passe.

Changer immédiatement le mot de passe initial et ne pas réutiliser ces identifiants dans une installation exposée sur un réseau partagé.

La source de données Prometheus est déjà déclarée par le fichier de provisionnement.

### 15.2 Vérifier la source de données

Dans Grafana :

1. Ouvrir **Connections** ou la section des sources de données selon la version.
2. Sélectionner la source **Prometheus**.
3. Vérifier son URL.
4. Tester la connexion avec la fonction disponible dans l’interface.

L’URL doit correspondre à la façon dont Grafana atteint Prometheus.

Dans notre laboratoire, le nom `prometheus` est résolu dans le réseau Docker.

### 15.3 Créer un tableau de bord

Le chemin exact des menus varie selon la version, mais les étapes générales sont :

1. Créer un nouveau tableau de bord.
2. Ajouter une visualisation.
3. Choisir Prometheus comme source de données.
4. Saisir une requête PromQL.
5. Choisir un type de visualisation.
6. Ajuster le titre, les unités et les légendes.
7. Enregistrer le panneau.
8. Enregistrer le tableau de bord.

### 15.4 Panneau CPU

Requête :

```promql
instance:node_cpu_utilisation:rate5m
```

Options suggérées :

- Type : série temporelle.
- Unité : pourcentage.
- Légende : instance.
- Titre : `Utilisation CPU par serveur`.
- Plage : dernières heures.

Le but est de repérer les périodes de charge, pas uniquement d’afficher une valeur.

### 15.5 Panneau mémoire

Requête :

```promql
100 * (
  1 -
  (
    node_memory_MemAvailable_bytes
    /
    node_memory_MemTotal_bytes
  )
)
```

Choisir le pourcentage comme unité et utiliser le label `instance` dans la légende.

Une valeur de mémoire utilisée élevée doit être examinée dans son contexte. Elle n’indique pas toujours une panne imminente.

### 15.6 Panneau espace disque

Requête :

```promql
100 * (
  1 -
  (
    node_filesystem_avail_bytes{
      fstype!~"tmpfs|overlay|squashfs|nsfs",
      mountpoint!~"/run.*"
    }
    /
    node_filesystem_size_bytes{
      fstype!~"tmpfs|overlay|squashfs|nsfs",
      mountpoint!~"/run.*"
    }
  )
)
```

Privilégier une légende qui inclut l’instance et le point de montage afin de ne pas confondre les volumes.

### 15.7 Panneau disponibilité

Requête :

```promql
up
```

Un panneau d’état ou une représentation sous forme de tableau peut aider à repérer les cibles dont la collecte échoue.

La métrique `up` répond à une question sur la collecte Prometheus. Pour vérifier la disponibilité d’un site depuis un point externe, utiliser un mécanisme de test synthétique adapté.

### 15.8 Construire une page de supervision opérationnelle

Exemple d’organisation :

```text
+-------------------------------------------------------------+
| SUPERVISION INFRASTRUCTURE                                  |
+-------------------------------------------------------------+
| Cibles indisponibles         | Alertes actives               |
+-------------------------------------------------------------+
| CPU par instance             | Mémoire par instance          |
+-------------------------------------------------------------+
| Occupation des systèmes de fichiers                         |
+-------------------------------------------------------------+
| Trafic entrant et sortant                                   |
+-------------------------------------------------------------+
| Tendance des ressources et principaux incidents             |
+-------------------------------------------------------------+
```

Ce schéma est un exemple d’organisation visuelle, pas une capture réelle de Grafana.

Un tableau de bord destiné à l’exploitation doit permettre de repérer rapidement une anomalie et d’accéder aux informations nécessaires à son diagnostic.

## 16. Variables, filtres et réutilisation des tableaux de bord

### 16.1 Pourquoi utiliser des variables ?

Un tableau de bord peut surveiller beaucoup de serveurs. Il est préférable de filtrer les données par environnement, job ou instance que de créer un tableau complètement séparé pour chaque machine.

Les variables Grafana rendent les tableaux plus réutilisables.

Exemples de variables :

- `environment`
- `job`
- `instance`

### 16.2 Exemple de filtre PromQL

Si une variable Grafana `instance` est configurée et contient le nom d’une instance :

```promql
instance:node_cpu_utilisation:rate5m{
  instance=~"$instance"
}
```

Si le filtre doit accepter plusieurs valeurs, l’expression régulière est généralement plus adaptée que l’égalité stricte.

La syntaxe finale dépend de la définition de la variable, de ses options et du mode de sélection utilisé dans Grafana.

### 16.3 Bonnes pratiques

Les variables doivent simplifier la consultation sans faire disparaître les alertes importantes.

Prévoir notamment :

- Une valeur permettant d’afficher toutes les instances pertinentes.
- Des noms et des libellés compréhensibles.
- Une sélection par environnement.
- Une cohérence des labels dans les métriques.
- Des valeurs par défaut qui ne masquent pas les problèmes.

## 17. Créer des règles d'alerte pertinentes

### 17.1 Qu'est-ce qu'une règle d'alerte ?

Une règle d’alerte exprime une condition que le système de supervision évalue régulièrement.

Exemple :

```text
Condition :
  CPU supérieur à 85 %

Durée :
  10 minutes

Gravité :
  WARNING

Action :
  Notification à l'équipe système
```

L’intérêt est de distinguer un pic ponctuel d’une dégradation persistante.

Les durées et seuils doivent être adaptés au service observé. Une application critique peut nécessiter des règles de latence plutôt que des alertes fondées uniquement sur la consommation CPU.

### 17.2 Pourquoi `for` est-il utile ?

Sans durée de confirmation, une condition peut déclencher une alerte même si elle ne dure que quelques secondes.

Le champ `for` permet de déclarer qu’une condition doit rester vraie pendant une période avant que l’alerte passe à l’état actif.

Cela aide à réduire le bruit, mais peut également retarder la détection si la durée est trop longue.

Il faut calibrer cette durée selon le type de problème.

### 17.3 Ajouter une alerte d'espace disque

La règle suivante fournit un exemple simplifié :

```yaml
- alert: HostDiskSpaceLow
  expr: |
    (
      node_filesystem_avail_bytes{
        fstype!~"tmpfs|overlay|squashfs|nsfs",
        mountpoint!~"/run.*"
      }
      /
      node_filesystem_size_bytes{
        fstype!~"tmpfs|overlay|squashfs|nsfs",
        mountpoint!~"/run.*"
      }
    ) < 0.10
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Espace disque inférieur à 10 %"
    description: >-
      {{ $labels.instance }} :
      le point de montage {{ $labels.mountpoint }}
      présente un espace disponible inférieur à 10 %.
```

Cette règle doit être placée dans une section `rules` d’un groupe YAML valide.

Avant de l’activer en production, vérifier la cohérence des métriques, les systèmes de fichiers visés et le comportement de l’alerte en cas de métriques absentes.

### 17.4 Ajouter une règle pour une cible indisponible

```yaml
- alert: MonitoringTargetDown
  expr: up == 0
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Échec de collecte de {{ $labels.instance }}"
    description: >-
      Prometheus ne collecte plus correctement
      la cible {{ $labels.instance }}.
```

Cette alerte suppose que la série `up` existe et vaut zéro.

Elle ne couvre pas tous les cas où une cible disparaît complètement du système de découverte. Une supervision complète doit aussi détecter les cibles qui ne sont plus découvertes lorsqu’elles devraient l’être.

### 17.5 Vérifier les alertes dans Prometheus

Après le chargement correct du fichier de règles, consulter :

`http://localhost:9090/alerts`

Vérifier :

- Le nom de la règle.
- La condition PromQL.
- L’état de l’alerte.
- La durée de confirmation.
- Les labels.
- Les annotations.
- Les éventuelles erreurs d’évaluation.

Un résultat `FIRING` indique que la règle d’alerte est active. Il reste à vérifier que l’alerte est transmise, routée et notifiée correctement.

## 18. Comprendre Alertmanager

### 18.1 À quoi sert Alertmanager ?

Alertmanager reçoit les alertes provenant notamment de Prometheus.

Il permet :

- De regrouper plusieurs alertes liées.
- De router les notifications selon leurs labels.
- De réduire les doublons.
- De définir des silences temporaires.
- D’inhiber certaines alertes lorsqu’une alerte plus importante est active.
- De gérer l’envoi vers différents canaux.

La responsabilité est séparée :

```text
Prometheus
  |
  | Détecte la condition
  v
Alerte active
  |
  v
Alertmanager
  |
  +----> Regroupement
  |
  +----> Routage
  |
  +----> Inhibition ou silence
  |
  v
Notification
  |
  v
Équipe responsable
```

### 18.2 Le regroupement

Supposons que plusieurs systèmes d’un même environnement tombent en panne.

Sans regroupement, l’équipe peut recevoir une notification distincte pour chaque métrique en erreur.

Alertmanager peut regrouper les alertes qui partagent certains labels et envoyer une notification synthétique.

Le but est de réduire le bruit tout en conservant les informations nécessaires au diagnostic.

### 18.3 Le routage

Le routage permet d’envoyer des alertes différentes vers des destinataires différents.

Exemple conceptuel :

```text
Toutes les alertes
       |
       +---- severity=critical
       |           |
       |           v
       |      Astreinte critique
       |
       +---- job=linux
       |           |
       |           v
       |       Equipe système
       |
       +---- job=windows
                   |
                   v
              Equipe Windows
```

Ce schéma représente une politique logique. La configuration réelle dépend des labels que les alertes portent effectivement.

### 18.4 Les silences

Un silence permet de suspendre les notifications correspondant à des critères définis pendant une période donnée.

Exemple : lors d’une maintenance approuvée, on peut suspendre certaines notifications liées aux systèmes concernés.

Un silence n’arrête pas la collecte et ne corrige pas le problème. Il limite le routage des notifications selon les conditions définies.

Les silences doivent avoir une durée et un périmètre maîtrisés. Ils ne doivent pas servir à cacher durablement les alertes d’un service en panne.

### 18.5 Les inhibitions

Une inhibition empêche certaines alertes d’être notifiées lorsqu’une autre alerte indiquant une situation plus générale est présente.

Exemple :

```text
Alerte majeure :
  Hôte inaccessible

Alertes secondaires :
  CPU absent
  Mémoire absente
  Exportateur inaccessible
```

Quand l’hôte est inaccessible, les alertes secondaires peuvent être peu utiles et être inhibées selon une règle adaptée.

L’inhibition réduit le bruit, mais doit être configurée avec attention. Une règle trop large peut masquer une alerte indépendante et importante.

## 19. Tester la chaîne d'alerte avec Mailpit

Le laboratoire inclut Mailpit pour recevoir localement les courriels de test.

### 19.1 Vérifier Alertmanager

Ouvrir :

`http://localhost:9093`

Les alertes reçues par Alertmanager doivent être visibles lorsqu’elles lui sont envoyées.

Si une alerte apparaît dans Prometheus mais pas dans Alertmanager, vérifier :

- La section `alerting` de Prometheus.
- L’adresse `alertmanager:9093`.
- La connectivité entre les conteneurs.
- La configuration chargée.
- Les journaux du conteneur Prometheus.
- Les journaux du conteneur Alertmanager.

### 19.2 Vérifier Mailpit

Ouvrir :

`http://localhost:8025`

L’interface permet de consulter les messages de test reçus.

Lorsqu’une alerte est active et qu’Alertmanager envoie une notification par e-mail, un message doit apparaître selon les délais de regroupement et les règles configurées.

### 19.3 Tester le cycle complet

```text
1. Une condition PromQL devient vraie
                   |
                   v
2. Prometheus évalue la règle
                   |
                   v
3. L'alerte passe à l'état actif
                   |
                   v
4. Prometheus transmet à Alertmanager
                   |
                   v
5. Alertmanager applique le routage
                   |
                   v
6. Un e-mail de test est envoyé à Mailpit
                   |
                   v
7. Le message apparaît dans l'interface Mailpit
```

Un test complet vérifie chaque étape. La présence d’une alerte active dans Prometheus ne démontre pas à elle seule que le canal de notification fonctionne.

### 19.4 Pourquoi l'e-mail de production demande-t-il plus de contrôles ?

Un service de messagerie réel peut nécessiter :

- Une authentification SMTP.
- TLS.
- Des identifiants conservés comme secrets.
- Une politique de relance.
- Un contrôle des destinataires.
- Une vérification des limites de débit.
- Un traitement des erreurs du serveur de messagerie.
- Des tests de réception.

Il faut également vérifier que les notifications ne contiennent pas d’informations confidentielles qui ne devraient pas être transmises au canal choisi.

## 20. Choisir entre alertes Prometheus et alertes Grafana

Les deux approches sont possibles, mais elles ne doivent pas être dupliquées sans réflexion.

### 20.1 Alertes Prometheus

Les règles sont définies dans des fichiers de configuration.

Avantages :

- Configuration versionnable.
- Règles explicites.
- Réutilisation des expressions PromQL.
- Transmission classique vers Alertmanager.
- Adaptation à une gestion de l’infrastructure par fichiers.

Elles conviennent bien lorsque les équipes veulent conserver les règles de métriques avec le code de configuration et appliquer un processus de revue.

### 20.2 Alertes gérées par Grafana

Grafana permet également de créer des règles d’alerte depuis son interface et sa configuration.

Ces règles peuvent interroger les sources de données configurées et router les notifications selon les mécanismes d’alerting de Grafana.

Avantages :

- Configuration accessible dans l’interface.
- Association directe avec les sources de données.
- Organisation des règles et des contacts au niveau de Grafana.
- Intégration avec les tableaux de bord et l’exploitation.

### 20.3 Éviter les doublons

Si la même condition est configurée à la fois dans Prometheus et dans Grafana, les deux systèmes peuvent produire des notifications pour le même événement.

Avant de déployer, décider :

- Où chaque règle est définie.
- Où elle est évaluée.
- Quel système envoie les notifications.
- Comment les alertes sont regroupées.
- Comment les silences sont administrés.
- Qui possède les règles.

Une architecture peut utiliser les deux approches, mais la gouvernance des alertes doit être claire.

## 21. Gestion avancée de la configuration Prometheus

### 21.1 Validation de la configuration

Les erreurs YAML ou les paramètres incompatibles peuvent empêcher le chargement de la configuration.

Si les outils appropriés sont disponibles :

```bash
promtool check config prometheus.yml
```

Pour les règles :

```bash
promtool check rules rules.yml
```

`promtool` est livré avec les distributions officielles de Prometheus. La version de l’outil doit correspondre à celle de Prometheus autant que possible.

Ces commandes valident la syntaxe et certaines contraintes structurelles, mais ne prouvent pas que les endpoints sont accessibles ni que les requêtes renvoient des résultats métier corrects.

### 21.2 Recharger la configuration

Prometheus peut recharger sa configuration et les fichiers de règles selon la méthode activée.

Dans le laboratoire Docker de ce cours, le moyen le plus simple après une modification consiste à recréer le conteneur concerné :

```bash
docker compose up -d prometheus
```

Vérifier ensuite les journaux et les cibles :

```bash
docker compose logs --tail=100 prometheus
```

Cette commande n’est pas nécessairement un rechargement à chaud pur. Elle permet à Compose de réconcilier le service avec sa configuration de conteneur.

Dans un déploiement natif, utiliser la procédure de rechargement définie par l’équipe d’exploitation.

L’endpoint de rechargement Prometheus ne doit pas être exposé sans protection sur un réseau non fiable.

### 21.3 Découverte statique et découverte dynamique

La découverte statique consiste à inscrire directement les cibles dans la configuration.

Exemple :

```yaml
- job_name: "linux"
  static_configs:
    - targets:
        - "srv-web-01.example.internal:9100"
        - "srv-db-01.example.internal:9100"
```

Cette approche convient à un petit parc.

Dans des environnements plus vastes, la découverte dynamique peut utiliser des mécanismes adaptés à l’infrastructure, comme des systèmes de découverte réseau, des API cloud ou des orchestrateurs.

Elle réduit le besoin de modifier manuellement une liste de serveurs, mais nécessite une configuration rigoureuse pour éviter que des systèmes inattendus soient intégrés à la collecte.

### 21.4 Labels d'environnement

Il est utile de différencier les environnements :

```yaml
- job_name: "linux-production"
  static_configs:
    - targets:
        - "srv-prod-01.example.internal:9100"
      labels:
        environment: "production"

- job_name: "linux-test"
  static_configs:
    - targets:
        - "srv-test-01.example.internal:9100"
      labels:
        environment: "test"
```

La distinction permet de filtrer les données dans PromQL et Grafana.

Les labels doivent rester cohérents entre les jobs et les cibles. Une convention différente pour chaque serveur complique les agrégations et l’administration.

## 22. Les règles d'enregistrement

### 22.1 Pourquoi utiliser une règle `record` ?

Certaines expressions PromQL sont utilisées dans plusieurs panneaux et alertes. Les recalculer partout peut être inutile et compliquer la maintenance.

Une règle d’enregistrement calcule périodiquement une nouvelle série temporelle à partir d’une expression.

Exemple :

```yaml
groups:
  - name: recording-rules
    interval: 30s
    rules:
      - record: instance:node_cpu_utilisation:rate5m
        expr: |
          100 * (
            1 - avg by (job, instance) (
              rate(node_cpu_seconds_total{mode="idle"}[5m])
            )
          )
```

La métrique enregistrée peut ensuite être interrogée directement :

```promql
instance:node_cpu_utilisation:rate5m
```

### 22.2 Quand les règles d'enregistrement sont-elles utiles ?

Elles sont particulièrement intéressantes lorsque :

- Une expression est répétée dans plusieurs tableaux de bord.
- Un calcul doit être standardisé entre les équipes.
- Une agrégation est coûteuse.
- L’équipe veut maintenir des indicateurs réutilisables.
- Les règles doivent être versionnées et relues.

### 22.3 Attention aux noms

La convention d’écriture est souvent :

```text
niveau:nom_indicateur:fenetre_ou_operation
```

Le nom choisi doit rester explicite et cohérent.

Une règle mal nommée ou dont la définition change sans documentation peut produire des tableaux de bord trompeurs.

## 23. Bonnes pratiques de PromQL

### 23.1 Utiliser le bon type de fonction

Pour un compteur :

```promql
rate(example_total[5m])
```

Pour une augmentation sur une période :

```promql
increase(example_total[1h])
```

Pour un gauge représentant une valeur instantanée, il n’est généralement pas pertinent d’appliquer `rate()` sans raison particulière.

Exemple de gauge :

```promql
node_memory_MemAvailable_bytes
```

Il faut comprendre la nature de la métrique avant de calculer sa dérivée ou son taux de changement.

### 23.2 Choisir une fenêtre adaptée

Une fenêtre courte permet de voir plus rapidement les variations, mais peut être sensible au bruit.

Une fenêtre longue lisse davantage les fluctuations, mais peut retarder la perception d’un changement rapide.

Exemples :

```promql
rate(example_total[1m])
```

```promql
rate(example_total[5m])
```

```promql
rate(example_total[15m])
```

La fenêtre doit être choisie selon la fréquence de collecte, la nature du compteur et l’objectif du panneau ou de l’alerte.

### 23.3 Ne pas confondre absence et zéro

Une série absente n’est pas la même chose qu’une série dont la valeur est zéro.

- `0` peut représenter une mesure valide.
- Une série absente peut signifier que la métrique n’est pas exposée ou collectée.
- Un résultat absent peut également venir d’un filtre trop restrictif.

Une règle qui ne renvoie aucune série peut ne pas déclencher d’alerte, même si l’on pensait surveiller une valeur dangereuse.

Pour un indicateur critique, tester explicitement les cas où les données sont absentes.

### 23.4 Les unités

Toujours afficher des unités compréhensibles :

- Octets ou unités adaptées.
- Secondes ou millisecondes.
- Pourcentages.
- Requêtes par seconde.
- Bits par seconde.
- Nombre d’événements.

Ne pas comparer deux courbes dont les unités ou les périmètres diffèrent sans l’expliquer.

## 24. Supervision de services HTTP avec Blackbox Exporter

Node Exporter surveille l’état de la machine. Il ne suffit pas à vérifier que les utilisateurs peuvent accéder correctement à un site Web.

Blackbox Exporter permet d’effectuer des sondes actives, selon les modules configurés, notamment pour :

- HTTP et HTTPS.
- TCP.
- DNS.
- ICMP, lorsque le système et les permissions le permettent.

Documentation officielle :

https://github.com/prometheus/blackbox_exporter

### 24.1 Différence entre Node Exporter et Blackbox Exporter

| Outil | Question principale |
|---|---|
| Node Exporter | Comment se comporte le système Linux ? |
| Windows Exporter | Comment se comporte le système Windows ? |
| Blackbox Exporter | Le service cible répond-il au test configuré ? |

Exemple :

```text
Serveur Web :
  CPU = normal
  Mémoire = normale
  Node Exporter = UP

Sonde HTTPS :
  Délai dépassé
  Code de réponse inattendu

Conclusion :
  La machine peut fonctionner
  alors que le service Web est dégradé.
```

Il faut donc surveiller à la fois les ressources internes et les fonctions visibles par les utilisateurs.

### 24.2 Exemple de configuration de sonde HTTP

La configuration précise de Blackbox Exporter doit être adaptée à la version et au type de sonde.

Le principe est le suivant :

```text
Prometheus
    |
    v
Blackbox Exporter
    |
    v
Sonde HTTP vers le service
    |
    v
Résultat : succès / échec / latence
    |
    v
Prometheus conserve les métriques
```

Une sonde peut notamment mesurer si la requête a réussi et combien de temps elle a pris.

Un succès HTTP ne prouve toutefois pas que toutes les opérations de l’application sont correctes. Les contrôles doivent correspondre au besoin métier.

## 25. Sécuriser Prometheus, Grafana et les exportateurs

### 25.1 Pourquoi la sécurité est importante

Les outils de supervision contiennent des informations détaillées sur l’infrastructure : noms de serveurs, consommations, versions, services, problèmes et parfois des données sensibles.

Un accès non autorisé peut fournir des informations utiles à un attaquant ou permettre de modifier les tableaux de bord, les règles et les notifications.

### 25.2 Mesures importantes

- Limiter l’accès aux interfaces Web.
- Utiliser des comptes individuels.
- Appliquer le moindre privilège.
- Activer des mécanismes d’authentification appropriés.
- Renforcer l’authentification des comptes privilégiés.
- Protéger les interfaces avec HTTPS lorsque nécessaire.
- Restreindre les endpoints des exportateurs.
- Éviter d’exposer Prometheus sur Internet sans protection.
- Contrôler les API et les mécanismes de rechargement.
- Mettre à jour les composants.
- Sauvegarder la configuration et les données nécessaires.
- Surveiller l’état des systèmes de collecte eux-mêmes.

### 25.3 Les endpoints d'exportateurs

Un endpoint de métriques peut révéler des informations sur :

- Le nom de la machine.
- Les interfaces réseau.
- Le stockage.
- Le système d’exploitation.
- Les versions.
- Les états des services.

La collecte doit rester accessible aux systèmes autorisés, mais l’accès général doit être restreint.

### 25.4 Contrôle d'accès Grafana

Créer des utilisateurs et des rôles adaptés à la répartition des responsabilités :

- Administrateurs de la plateforme.
- Équipe d’exploitation.
- Lecteurs de tableaux de bord.
- Responsables applicatifs.
- Autres équipes ayant besoin d’une visibilité limitée.

Les fonctions et portées de permissions peuvent varier selon l’édition, la version et la configuration de Grafana.

Un utilisateur qui consulte des tableaux de bord n’a pas automatiquement besoin du droit de modifier les sources de données ou les règles d’alerte.

### 25.5 Protéger les secrets

Ne pas stocker les mots de passe, les clés privées ou les jetons d’accès dans :

- Les dépôts Git.
- Les fichiers de tableau de bord exportés.
- Les descriptions d’alertes.
- Les journaux de déploiement.
- Les scripts partagés.
- Les captures d’écran destinées à une documentation publique.

Employer un mécanisme de gestion des secrets adapté, contrôler l’accès et prévoir la rotation des identifiants.

### 25.6 Accès distant au laboratoire

Dans notre laboratoire, les interfaces sont liées à `127.0.0.1`.

Pour administrer le laboratoire à distance, il est préférable d’utiliser un accès d’administration contrôlé ou un tunnel sécurisé plutôt que d’exposer directement tous les ports.

Ne pas modifier aveuglément les mappings en `0.0.0.0` si l’authentification, le filtrage réseau et le chiffrement ne sont pas correctement préparés.

## 26. Conservation et dimensionnement des données

### 26.1 La rétention

Prometheus stocke ses métriques sous forme de séries temporelles. La durée de conservation détermine la période d’historique disponible dans le stockage local.

Dans le laboratoire, nous avons défini :

```text
--storage.tsdb.retention.time=15d
```

Cela correspond à une rétention temporelle de quinze jours pour les données gérées par cette configuration, sous réserve des autres limites applicables.

Une rétention plus longue augmente généralement la quantité de données conservées et peut augmenter les besoins de stockage.

### 26.2 Durée de collecte et rétention

Le temps pendant lequel l’on collecte une métrique et le temps pendant lequel l’on conserve son historique sont deux notions différentes.

Exemple :

```text
Fréquence de collecte : toutes les 15 secondes
Rétention             : 30 jours
```

Prometheus conserve alors les échantillons collectés selon sa configuration pendant la période de rétention retenue.

Les besoins réels dépendent du nombre de séries, de leur fréquence, de la compression, du type de métriques, des labels et des autres paramètres de stockage.

### 26.3 Estimer les besoins de stockage

Il n’existe pas de taille universelle valable pour toutes les plateformes.

Les principaux facteurs sont :

- Le nombre de cibles.
- Le nombre de séries par cible.
- La fréquence de collecte.
- La cardinalité des labels.
- Le nombre d’exportateurs.
- Les règles d’enregistrement.
- La durée de rétention.
- Les besoins d’historique et de requêtes.
- La croissance prévue de l’infrastructure.

Exemple :

```text
10 serveurs
     |
     v
Nombre de séries par serveur
     |
     v
Nombre total de séries actives
     |
     v
Echantillonnage périodique
     |
     v
Croissance du stockage
     |
     v
Projection sur la rétention choisie
```

Le dimensionnement doit être vérifié à l’aide de données mesurées sur l’installation réelle. Il faut conserver une marge pour les pics et éviter que le disque de Prometheus devienne lui-même un point de défaillance.

### 26.4 Contrôler l'espace disque

Sur l’hôte :

```bash
df -h
```

Pour les volumes Docker, examiner leur emplacement et leur consommation selon la plateforme.

Une saturation du disque de Prometheus peut provoquer des erreurs de stockage, une dégradation de son fonctionnement et une perte d’historique.

Créer une alerte sur le stockage utilisé par la supervision elle-même.

## 27. Sauvegarder et restaurer la configuration

### 27.1 Qu'est-ce qu'il faut sauvegarder ?

Pour une plateforme de supervision, les éléments à protéger peuvent comprendre :

- Les fichiers de configuration Prometheus.
- Les règles d’enregistrement.
- Les règles d’alerte.
- La configuration d’Alertmanager.
- Les sources de données.
- Les tableaux de bord.
- Les variables de configuration.
- Les politiques et informations nécessaires au rétablissement.
- Les données historiques dont la conservation est requise.

Le choix dépend du besoin. Tous les environnements n’ont pas besoin de conserver indéfiniment toutes les métriques, mais ils doivent savoir quelles données sont indispensables.

### 27.2 Versionner les configurations

Les fichiers de configuration peuvent être stockés dans un dépôt Git avec :

- Des changements revus.
- Des versions identifiables.
- Des tests de syntaxe.
- Une documentation de déploiement.
- Une procédure de retour arrière.
- Une séparation des paramètres sensibles.

Les secrets ne doivent pas être ajoutés directement au dépôt.

### 27.3 Plan de restauration

Un plan de restauration devrait définir :

1. Les fichiers à récupérer.
2. Les versions des composants nécessaires.
3. Les permissions attendues.
4. Les données historiques à préserver.
5. Les dépendances réseau.
6. La procédure de redémarrage.
7. Les contrôles des cibles.
8. Les tests des règles et notifications.
9. Les critères de validation.
10. La documentation du résultat.

Une restauration de configuration ne démontre pas automatiquement que les métriques historiques ou les notifications sont récupérables. Il faut tester les différents éléments du service.

## 28. Superviser la supervision elle-même

La plateforme de monitoring doit être surveillée.

Autrement, un problème de Prometheus ou d’Alertmanager pourrait empêcher la détection ou la notification des incidents.

### 28.1 Indicateurs utiles

Surveiller notamment :

- La disponibilité de Prometheus.
- L’état de chaque cible.
- Les erreurs de collecte.
- La durée des collectes.
- La consommation mémoire de Prometheus.
- L’espace disque disponible.
- Les erreurs de requête.
- L’état d’Alertmanager.
- Les notifications échouées.
- Le retard ou la perte de données selon les besoins.
- L’état de Grafana.
- L’accessibilité des canaux de notification.

### 28.2 Limites d'une seule instance

Si Prometheus est la seule source d’alerte et qu’il s’arrête, il peut ne plus être capable de signaler sa propre panne.

Pour une plateforme critique, on peut compléter sa supervision par :

- Une sonde externe.
- Un contrôle périodique depuis une autre plateforme.
- Un système de notification indépendant.
- Un mécanisme de disponibilité adapté.
- Des procédures de vérification manuelle.

La conception dépend du niveau de service attendu.

## 29. Diagnostic des problèmes courants

### 29.1 Une cible reste `DOWN`

Examiner les éléments suivants :

```text
Cible DOWN
   |
   v
Adresse et port corrects ?
   |
   v
Service d'exportateur actif ?
   |
   v
Endpoint /metrics accessible ?
   |
   v
Réseau et pare-feu autorisent la collecte ?
   |
   v
Prometheus utilise-t-il la bonne configuration ?
   |
   v
Erreur visible dans les journaux ?
```

Vérifier l’URL de la cible et le port. Contrôler le service d’exportateur, puis la connectivité depuis la machine qui exécute Prometheus.

Dans Docker, ne pas utiliser `localhost` pour désigner un autre conteneur : ce nom désigne le conteneur courant.

### 29.2 Grafana affiche « No data »

Une absence de données peut avoir plusieurs causes :

- La source de données ne fonctionne pas.
- La cible n’est pas collectée.
- Le nom de métrique est incorrect.
- La période affichée ne contient pas de données.
- Un filtre exclut toutes les séries.
- Une variable Grafana possède une valeur incorrecte.
- La requête PromQL produit un résultat vide.

Démarche :

1. Tester la source de données.
2. Exécuter la requête dans Prometheus.
3. Comparer le résultat dans Grafana.
4. Examiner les filtres et variables.
5. Vérifier la période temporelle.
6. Examiner les journaux du composant qui échoue.

### 29.3 La collecte fonctionne mais l'alerte ne se déclenche pas

Vérifier :

- La syntaxe de la règle.
- L’état de la règle dans Prometheus.
- L’expression PromQL.
- La durée du champ `for`.
- Le seuil défini.
- L’existence des séries nécessaires.
- Les labels et filtres.
- L’intervalle d’évaluation.
- L’absence éventuelle de données.

Une alerte n’est pas déclenchée si l’expression ne renvoie pas les séries attendues, même si une métrique semble anormale dans un autre panneau.

### 29.4 L'alerte est active mais aucun courriel n'arrive

Inspecter les étapes :

```text
Prometheus : alerte active ?
         |
         v
Alertmanager : alerte reçue ?
         |
         v
Routage : destinataire sélectionné ?
         |
         v
Configuration SMTP : correcte ?
         |
         v
Connexion au serveur de messagerie ?
         |
         v
Notification remise au destinataire ?
```

Dans le laboratoire, vérifier également l’interface Mailpit.

Dans un système réel, la livraison du message peut échouer même si Alertmanager a bien tenté l’envoi. Il faut distinguer l’état de l’alerte, la tentative de notification et la réception effective.

### 29.5 La consommation mémoire de Prometheus augmente

Examiner notamment :

- Le nombre de séries actives.
- La cardinalité des labels.
- La fréquence de collecte.
- Le nombre de cibles.
- Les règles d’enregistrement.
- Les requêtes coûteuses.
- La durée de conservation.
- La croissance réelle des données.

Ne pas réduire la fréquence de collecte ou la rétention sans vérifier les conséquences sur le diagnostic et les engagements de service.

### 29.6 Le tableau de bord est lent

Les causes possibles comprennent :

- Trop de panneaux.
- Des requêtes très coûteuses.
- Des séries à forte cardinalité.
- Une période trop longue.
- Une fréquence de rafraîchissement excessive.
- Une forte charge sur Prometheus.
- Des calculs répétés qui pourraient être standardisés.

Mesures possibles :

- Réduire le nombre de séries interrogées.
- Filtrer les données utiles.
- Améliorer les agrégations.
- Adapter la fenêtre temporelle.
- Éviter le rafraîchissement trop fréquent.
- Utiliser des règles d’enregistrement pour certains calculs répétés.

## 30. Journaliser les composants de supervision

Les outils de supervision produisent eux-mêmes des journaux.

Dans le laboratoire Docker :

```bash
docker compose logs --tail=100 prometheus
docker compose logs --tail=100 grafana
docker compose logs --tail=100 alertmanager
docker compose logs --tail=100 node-exporter
```

Pour suivre un composant en direct :

```bash
docker compose logs -f prometheus
```

Ces journaux peuvent révéler :

- Une erreur de configuration.
- Une erreur de résolution DNS.
- Un délai dépassé.
- Un problème de permission.
- Une erreur de notification.
- Un accès refusé.
- Un échec de stockage.

Les journaux ne doivent pas être négligés sous prétexte que le but du système est de superviser d’autres systèmes.

## 31. Intégrer les journaux dans Grafana avec Loki

Prometheus traite principalement les métriques. Pour rechercher les événements, on peut ajouter un système de collecte et d’indexation de journaux.

Dans l’écosystème Grafana :

- **Loki** sert au stockage et à l’interrogation des journaux.
- **Grafana Alloy** peut collecter et transférer les journaux vers Loki.
- **Grafana** permet ensuite d’interroger les métriques et les journaux dans une interface commune.

Documentation officielle :

- Loki : https://grafana.com/docs/loki/latest/
- Alloy : https://grafana.com/docs/alloy/latest/
- Collecter des journaux avec Alloy : https://grafana.com/docs/loki/latest/send-data/alloy/

### 31.1 Architecture combinée

```text
            SERVEUR LINUX
                 |
          +------+------+
          |             |
          v             v
      Node Exporter   Grafana Alloy
          |             |
          v             v
      Prometheus       Loki
          |             |
          +------+------+
                 |
                 v
              Grafana
                 |
        +--------+--------+
        |                 |
        v                 v
  Courbes métriques   Recherche logs
```

Cette architecture permet de rapprocher une dégradation de métrique d’un événement consigné dans les journaux.

### 31.2 Exemple d'utilisation

Une métrique montre une hausse de latence à 10 h 05.

Dans Grafana, l’administrateur peut examiner la fenêtre temporelle correspondante et rechercher les erreurs des composants impliqués.

```text
10 h 00 : latence normale
10 h 03 : CPU en hausse
10 h 05 : latence anormale
10 h 05 : erreurs applicatives
10 h 07 : connexions à la base expirées
```

La chronologie fournit des pistes, mais ne prouve pas automatiquement une relation de causalité. Il faut examiner le contexte et tester les hypothèses.

### 31.3 Pourquoi séparer les outils ?

Les métriques, journaux et traces ont des caractéristiques différentes.

Les métriques conviennent bien aux tendances et aux agrégations numériques. Les journaux conservent des événements détaillés. Les traces permettent d’observer les étapes d’une requête entre plusieurs composants.

Un système d’observabilité peut les réunir dans une même interface tout en conservant des systèmes de collecte et de stockage adaptés à chaque type de données.

## 32. Automatiser les contrôles de configuration

### 32.1 Pourquoi automatiser ?

Dans une infrastructure qui compte plusieurs dizaines de cibles, la configuration manuelle devient difficile à maintenir.

Il faut standardiser :

- La nomenclature des jobs.
- Les labels d’environnement.
- Les règles d’alerte.
- Les fichiers de configuration.
- Les tests de syntaxe.
- La mise à jour des cibles.
- Les tableaux de bord.
- Les procédures de déploiement.

### 32.2 Exemple de validation

Dans un pipeline ou une procédure d’intégration, vérifier les fichiers avant déploiement :

```bash
promtool check config prometheus.yml
promtool check rules rules.yml
```

Puis relire les modifications avant leur application à l’environnement cible.

Un pipeline peut également vérifier les fichiers de provisionnement, les versions des images et la cohérence des noms de métriques utilisés.

### 32.3 Gestion des versions

Les configurations doivent pouvoir être rattachées à un changement identifiable.

Exemple de cycle :

```text
Modification
     |
     v
Dépôt Git
     |
     v
Vérification syntaxique
     |
     v
Revue par un pair
     |
     v
Déploiement sur un environnement de test
     |
     v
Vérification des cibles et alertes
     |
     v
Déploiement contrôlé
     |
     v
Validation et journalisation
```

Cette démarche réduit le risque d’introduire une erreur de configuration dans une plateforme qui surveille toute l’infrastructure.

## 33. Exercices pratiques avec corrigés

### Exercice 1 — Une cible est en état `DOWN`

La cible `srv-web-01:9100` est en état `DOWN`, mais les utilisateurs peuvent toujours accéder au site Web.

**Question :** est-il possible que le service Web fonctionne malgré cette alerte ?

**Correction :** oui. L’alerte indique que Prometheus ne collecte plus correctement les métriques de l’exportateur. Le serveur Web peut être fonctionnel tandis que Node Exporter, son port ou le chemin réseau de supervision est indisponible.

Il faut contrôler la disponibilité de l’exportateur et du site par des méthodes séparées.

### Exercice 2 — CPU élevé

On observe 92 % d’utilisation CPU pendant dix secondes, puis le niveau revient à 35 %.

Une règle déclenche une alerte si le CPU dépasse 85 % pendant dix minutes.

**Question :** l’alerte doit-elle devenir active à la suite de ce seul pic ?

**Correction :** non, si la condition a bien été vraie uniquement pendant dix secondes. La durée `for: 10m` permet de distinguer un pic bref d’une condition persistante.

Cela n’exclut pas qu’un pic très bref puisse être important pour une application sensible à la latence. Les règles doivent correspondre à l’objectif de surveillance.

### Exercice 3 — Absence de métrique

La requête suivante ne renvoie aucun résultat :

```promql
node_memory_MemAvailable_bytes
```

**Question :** citer quatre pistes de diagnostic.

**Correction :**

- La cible ne fournit pas la métrique.
- L’exportateur n’est pas installé ou ne fonctionne pas.
- Prometheus ne collecte pas la cible.
- Le nom de la métrique est incorrect.
- Un filtre de configuration exclut la métrique.
- La période interrogée ne dispose pas des échantillons attendus.

Commencer par vérifier les cibles, puis l’endpoint `/metrics` de l’exportateur.

### Exercice 4 — Pourcentage mémoire

Une machine possède 16 Go de mémoire totale et 2 Go de mémoire disponible. Estimer la mémoire non disponible à partir de ces deux valeurs.

**Correction :**

```text
Mémoire non disponible estimée :
(16 - 2) / 16 x 100

= 14 / 16 x 100
= 87,5 %
```

Le résultat est une estimation fondée sur la définition de la mémoire disponible utilisée dans la mesure. Il ne signifie pas que tous les 14 Go sont utilisés par des applications et qu’ils ne peuvent pas être récupérés.

### Exercice 5 — Espace disque

Une partition de 500 Go a 40 Go disponibles.

**Correction :**

```text
Pourcentage disponible :
40 / 500 x 100 = 8 %

Pourcentage occupé :
100 - 8 = 92 %
```

Une règle avec un seuil de 10 % d’espace disponible peut donc déclencher une alerte si les métriques sont cohérentes et si la condition est maintenue pendant la durée configurée.

### Exercice 6 — Requête de débit

Un compteur d’octets réseau augmente de 300 Mo pendant une période de 60 secondes. Estimer le débit moyen en mégabits par seconde avec une convention décimale.

**Correction :**

```text
Débit en octets/s :
300 000 000 / 60
= 5 000 000 octets/s

Débit en bits/s :
5 000 000 x 8
= 40 000 000 bits/s

Débit :
40 Mbit/s
```

La commande PromQL `rate()` fournit une estimation du taux à partir des échantillons réels ; un calcul manuel à partir de deux valeurs ne représente pas nécessairement exactement le résultat d’une requête Prometheus.

### Exercice 7 — Pourquoi les alertes sont-elles dupliquées ?

Une alerte de CPU élevé est définie dans Prometheus et dans Grafana. Les deux systèmes envoient un courriel.

**Correction :** les deux règles sont indépendantes et peuvent chacune produire des notifications. Il faut déterminer le système responsable de cette alerte, ou définir une stratégie qui contrôle explicitement les doublons.

### Exercice 8 — Le tableau de bord est vide

La cible est `UP` dans Prometheus, mais le panneau Grafana indique `No data`.

**Correction :** tester la même requête dans l’interface Prometheus, vérifier la source de données dans Grafana, la plage temporelle, les filtres, les variables et le nom de métrique. Une cible `UP` ne garantit pas que la métrique particulière demandée existe.

### Exercice 9 — Alerte active, absence de notification

Une alerte est `FIRING` dans Prometheus, mais aucun message ne parvient à l’équipe.

**Correction :** vérifier la réception par Alertmanager, le routage, les labels, le destinataire, la configuration du canal et les journaux d’envoi. Tester le canal de notification séparément. Dans le laboratoire, consulter aussi l’interface Mailpit.

### Exercice 10 — Choix de l'outil

On veut suivre le CPU et la mémoire des serveurs et afficher leur évolution dans une interface graphique.

**Correction :** Node Exporter ou Windows Exporter expose les métriques du système approprié, Prometheus les collecte et Grafana les visualise.

Pour tester l’accessibilité d’un site depuis un point réseau externe, compléter cette supervision avec une sonde adaptée, comme Blackbox Exporter.

## 34. Projet de fin de niveau

### Construire une plateforme de supervision pour une petite infrastructure

L’objectif est de superviser plusieurs serveurs, de construire un tableau de bord opérationnel et de vérifier le traitement des alertes.

L’infrastructure de projet comprend :

- Deux serveurs Linux.
- Un serveur Windows.
- Un service Web.
- Un service de base de données ou un service simulé.
- Une source de collecte Prometheus.
- Un tableau de bord Grafana.
- Alertmanager.
- Un canal de notification de test.

### Livrable A — Architecture

Présenter :

- Les composants.
- Les machines.
- Les adresses et ports nécessaires.
- Les chemins de collecte.
- Les frontières de sécurité.
- Les dépendances entre composants.
- Les points de défaillance possibles.

### Livrable B — Configuration Prometheus

Fournir :

- Le fichier de configuration.
- Les jobs.
- Les cibles.
- Les labels.
- Les règles d’enregistrement.
- Les règles d’alerte.
- Les résultats de validation.

### Livrable C — Tableaux de bord

Créer au moins deux tableaux de bord.

Le premier sera orienté infrastructure :

- Disponibilité des cibles.
- CPU.
- Mémoire.
- Espace disque.
- Débit réseau.

Le second sera orienté service :

- Disponibilité HTTP.
- Latence lorsque la métrique est disponible.
- Taux d’erreur si les données existent.
- État des dépendances.
- Alertes actives.

### Livrable D — Alertes

Mettre en place au minimum :

- Une alerte de cible indisponible.
- Une alerte CPU.
- Une alerte mémoire.
- Une alerte d’espace disque.
- Une alerte liée à la disponibilité du service.
- Une notification de test.

Chaque alerte devra inclure une description et une procédure initiale de diagnostic.

### Livrable E — Sécurité

Documenter :

- Les ports publiés.
- Les restrictions d’accès.
- Les identités autorisées.
- Les secrets et leur stockage.
- Les mises à jour des composants.
- Les durées de conservation.
- La sauvegarde des configurations.

### Livrable F — Test d'incident

Simuler un incident dans le laboratoire : exporter des métriques indisponibles, service HTTP défaillant ou seuil d’espace disque dépassé.

Fournir un compte rendu avec :

- Heure de début.
- Heure de détection.
- Alerte générée.
- Données consultées.
- Cause confirmée ou hypothèse.
- Action corrective.
- Heure de rétablissement.
- Vérification finale.
- Amélioration proposée.

### Critères de réussite

Le projet est réussi lorsque l’apprenant démontre que :

1. Les cibles sont collectées.
2. Les métriques donnent des résultats cohérents.
3. Les tableaux de bord sont lisibles.
4. Les règles d’alerte s’activent dans les conditions attendues.
5. Les notifications sont effectivement reçues par le canal de test.
6. Le système peut être diagnostiqué quand une collecte échoue.
7. Les accès aux interfaces et aux exportateurs sont maîtrisés.
8. La configuration peut être restaurée ou redéployée de manière reproductible.

## 35. Bonnes pratiques à retenir

### Prometheus

- Choisir des fréquences de collecte adaptées.
- Utiliser des labels cohérents.
- Surveiller le nombre de séries.
- Éviter les labels à cardinalité élevée.
- Valider les fichiers avant déploiement.
- Réserver des ressources pour le stockage et les requêtes.
- Surveiller les cibles et Prometheus lui-même.
- Définir une rétention compatible avec les besoins.

### Grafana

- Construire des tableaux de bord orientés vers les décisions.
- Afficher des unités claires.
- Prévoir des filtres utiles.
- Éviter les panneaux redondants.
- Limiter les requêtes coûteuses.
- Protéger les accès.
- Documenter les tableaux de bord utilisés en exploitation.

### Alertmanager

- Regrouper les alertes liées.
- Router vers les bonnes équipes.
- Utiliser les silences avec une durée et un périmètre définis.
- Éviter les inhibitions trop larges.
- Tester les canaux de notification.
- Contrôler les notifications échouées.
- Éviter les règles en double entre plusieurs systèmes.

### Sécurité et exploitation

- Ne pas exposer publiquement les endpoints de métriques sans contrôle.
- Utiliser des comptes et privilèges adaptés.
- Protéger les secrets.
- Mettre à jour les composants.
- Documenter les changements.
- Sauvegarder les configurations nécessaires.
- Tester les restaurations.
- Vérifier le fonctionnement de la chaîne de bout en bout.

## 36. Référence opérationnelle rapide

| Besoin | Commande, requête ou écran |
|---|---|
| Vérifier les conteneurs | `docker compose ps` |
| Lire les journaux du conteneur | `docker compose logs -f prometheus` |
| Vérifier la configuration | `promtool check config prometheus.yml` |
| Vérifier les règles | `promtool check rules rules.yml` |
| Lister les cibles | `http://localhost:9090/targets` |
| Voir les alertes Prometheus | `http://localhost:9090/alerts` |
| Interroger la disponibilité des cibles | `up` |
| Filtrer une cible Linux | `up{job="linux"}` |
| Examiner le CPU par instance | `instance:node_cpu_utilisation:rate5m` |
| Examiner la mémoire disponible | `node_memory_MemAvailable_bytes` |
| Examiner l'espace disque disponible | `node_filesystem_avail_bytes` |
| Accéder à Grafana | `http://localhost:3000` |
| Accéder à Alertmanager | `http://localhost:9093` |
| Consulter les courriels de test | `http://localhost:8025` |

Les interfaces locales sont celles du laboratoire décrit dans ce cours. Les adresses changent selon le déploiement.

## 37. Glossaire

**Alertmanager :** composant qui reçoit les alertes, les regroupe, les route et gère les silences et inhibitions.

**Blackbox Exporter :** composant qui réalise des sondes actives vers des services selon la configuration.

**Cardinalité :** nombre de séries temporelles distinctes générées par les noms de métriques et leurs ensembles de labels.

**Counter :** compteur monotone qui augmente, avec possibilité de remise à zéro dans certains événements du cycle de vie du processus.

**Dashboard :** tableau de bord réunissant les visualisations pertinentes.

**Exportateur :** composant qui expose des métriques pour leur collecte.

**Gauge :** métrique représentant une valeur qui peut augmenter ou diminuer.

**Grafana :** plateforme de visualisation et de gestion de tableaux de bord et d’alertes selon sa configuration.

**Histogram :** représentation de la distribution d’observations par compartiments, utile notamment pour des durées.

**Inhibition :** mécanisme qui réduit les notifications d’alertes secondaires lorsqu’une alerte plus générale est active.

**Label :** dimension descriptive associée à une série temporelle.

**Node Exporter :** exportateur de métriques système pour Linux et les environnements compatibles.

**PromQL :** langage d’interrogation et de calcul de métriques de Prometheus.

**Prometheus :** système de collecte, de stockage et d’interrogation de métriques, qui peut aussi évaluer des règles d’alerte.

**Recording rule :** règle qui calcule et enregistre une série temporelle dérivée.

**Scraping :** mécanisme par lequel Prometheus interroge un endpoint de métriques.

**Silence :** mécanisme qui suspend temporairement les notifications correspondant à certains critères.

**Série temporelle :** ensemble d’échantillons numériques horodatés associés à un nom de métrique et à un ensemble de labels.

**SLI :** indicateur mesurant un aspect d’un service.

**SLO :** objectif quantifié associé à un indicateur de service.

**SLA :** engagement de niveau de service défini entre des parties.

**Windows Exporter :** exportateur de métriques pour des systèmes Windows pris en charge.

## 38. Documentation officielle

### Prometheus

- Documentation générale : https://prometheus.io/docs/
- Premiers pas : https://prometheus.io/docs/introduction/first_steps/
- Configuration : https://prometheus.io/docs/prometheus/latest/configuration/configuration/
- Bases de PromQL : https://prometheus.io/docs/prometheus/latest/querying/basics/
- Fonctions PromQL : https://prometheus.io/docs/prometheus/latest/querying/functions/
- Règles d'alerte : https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
- Guide Node Exporter : https://prometheus.io/docs/guides/node-exporter/
- Stockage : https://prometheus.io/docs/prometheus/latest/storage/

### Grafana

- Documentation générale : https://grafana.com/docs/grafana/latest/
- Installer Grafana sur Debian ou Ubuntu : https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/
- Source de données Prometheus : https://grafana.com/docs/grafana/latest/datasources/prometheus/
- Tableaux de bord : https://grafana.com/docs/grafana/latest/dashboards/
- Alerting : https://grafana.com/docs/grafana/latest/alerting/

### Alertmanager

- Concepts et fonctionnement : https://prometheus.io/docs/alerting/latest/alertmanager/
- Configuration : https://prometheus.io/docs/alerting/latest/configuration/

### Exportateurs et journaux

- Windows Exporter : https://github.com/prometheus-community/windows_exporter
- Blackbox Exporter : https://github.com/prometheus/blackbox_exporter
- Loki : https://grafana.com/docs/loki/latest/
- Grafana Alloy : https://grafana.com/docs/alloy/latest/
- Collecter les journaux avec Alloy : https://grafana.com/docs/loki/latest/send-data/alloy/

### Docker

- Documentation Docker Compose : https://docs.docker.com/compose/
- Référence du fichier Compose : https://docs.docker.com/reference/compose-file/

Avant un déploiement, vérifier les instructions correspondant aux versions réellement installées. Les configurations présentées ici sont pédagogiques et peuvent nécessiter des adaptations selon les versions, le système d’exploitation et l’architecture retenue.

## 39. Conclusion du niveau intermédiaire

Prometheus et Grafana forment une base efficace pour superviser les ressources et les services d’une infrastructure.

Prometheus collecte les métriques et permet de les interroger. PromQL transforme ces mesures en indicateurs exploitables. Les règles identifient les conditions anormales. Alertmanager organise les notifications. Grafana transforme les données en tableaux de bord et facilite l’analyse.

La maîtrise de la plateforme demande cependant plus qu’une installation fonctionnelle :

- Les métriques doivent avoir un sens.
- Les labels doivent rester maîtrisés.
- Les tableaux de bord doivent aider à la décision.
- Les alertes doivent correspondre à des actions concrètes.
- Les notifications doivent être testées.
- La plateforme doit être protégée et surveillée elle-même.
- Les configurations doivent être versionnées et restaurables.

Le passage au niveau suivant consistera à industrialiser la supervision : règles d’alerte complexes, corrélation avec les journaux, observabilité applicative, gestion des volumes importants de séries temporelles, haute disponibilité, découverte dynamique des cibles, automatisation de la configuration et amélioration des objectifs de service.