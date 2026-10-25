# Haute Performance Web

## 1. Introduction : concevoir un serveur Web performant

La haute performance Web ne consiste pas simplement à augmenter le nombre de processus d'un serveur ou à activer quelques options de configuration.

Une infrastructure performante doit être capable de traiter un volume de requêtes donné, avec une latence acceptable, une consommation maîtrisée de ressources et un comportement prévisible lorsque la charge augmente.

Cette démarche concerne notamment :

- le temps de réponse des applications ;
- le débit de requêtes que le système peut traiter ;
- la gestion des connexions simultanées ;
- l'utilisation du processeur et de la mémoire ;
- les accès au stockage ;
- les performances du réseau ;
- la mise en cache des contenus ;
- la compression des réponses ;
- les connexions entre le reverse proxy et les applications ;
- la gestion de TLS et des protocoles HTTP ;
- la supervision et l'analyse des métriques ;
- la résistance à une montée en charge progressive.

Ce cours constitue la suite du travail consacré aux serveurs Web Nginx et Apache, puis au reverse proxy et au load balancing.

Au niveau expert, l'objectif est de comprendre non seulement quelles directives utiliser, mais aussi **pourquoi les utiliser, dans quelles conditions elles sont efficaces et comment prouver qu'elles améliorent réellement le service**.

### 1.1 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- distinguer latence, débit, concurrence et capacité ;
- établir une référence de performance avant toute optimisation ;
- interpréter les percentiles de latence, notamment p95 et p99 ;
- identifier un goulot d'étranglement CPU, mémoire, stockage, réseau ou application ;
- estimer le nombre de connexions qu'une instance peut gérer ;
- configurer les principaux paramètres de performance de Nginx ;
- optimiser les connexions entre Nginx et les backends ;
- comprendre le rôle du buffering, du cache et de la compression ;
- construire une politique de cache HTTP cohérente ;
- éviter la mise en cache accidentelle de données privées ;
- ajuster Apache et son MPM ;
- comparer les modèles de traitement d'Apache ;
- configurer une stratégie de cache pour les ressources publiques ;
- mesurer le temps DNS, la connexion TCP, la négociation TLS et le temps jusqu'au premier octet ;
- utiliser les tests de charge de manière reproductible ;
- mesurer les effets d'un changement avant de le déployer ;
- dimensionner prudemment les ressources d'un serveur ;
- surveiller les performances et détecter les dégradations ;
- préparer un plan d'optimisation et un retour arrière.

### 1.2 Prérequis

Vous devez maîtriser :

- les commandes d'administration Linux ;
- la gestion des services avec `systemctl` ;
- les configurations de base de Nginx et Apache ;
- les reverse proxies et les upstreams ;
- HTTP, HTTPS, les ports TCP et la résolution DNS ;
- les journaux d'accès et d'erreurs ;
- les permissions et les limites élémentaires du système ;
- les commandes `curl`, `ss`, `ps`, `top` et `journalctl`.

Les exemples utilisent principalement Debian et Ubuntu. Certains principes sont communs à toutes les distributions, mais les chemins, les modules installés, les utilisateurs de service et les versions peuvent différer.


## 2. Architecture de référence pour la haute performance

### 2.1 Architecture simplifiée

Une infrastructure Web peut être représentée ainsi :

```text
                           CLIENTS
                              |
                              | HTTP / HTTPS
                              v
                  +---------------------------+
                  | POINT D'ENTRÉE            |
                  | Nginx ou Apache           |
                  | TLS / Routage / Cache      |
                  +-------------+-------------+
                                |
                         Réseau interne
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
        +------------------+         +------------------+
        | Application 1    |         | Application 2    |
        | Workers / Threads|         | Workers / Threads|
        +---------+--------+         +---------+--------+
                  |                            |
                  +-------------+--------------+
                                |
                                v
                     +---------------------+
                     | Base de données     |
                     | Cache applicatif    |
                     | Stockage / API      |
                     +---------------------+
```

Dans cette architecture, une requête peut consommer des ressources à plusieurs niveaux :

1. le réseau doit acheminer les données ;
2. le serveur Web doit accepter et analyser la requête ;
3. le proxy peut chercher une réponse dans un cache ;
4. un backend peut traiter la requête ;
5. l'application peut consulter une base de données ;
6. les données doivent être transmises au client.

Optimiser uniquement Nginx ou Apache ne garantit donc pas une amélioration si le problème principal se trouve dans la base de données ou dans l'application.

### 2.2 Les différents chemins d'une requête

Un contenu statique peut suivre ce chemin :

```text
Client
  |
  v
Nginx
  |
  +-- Cache disque du système
  |
  +-- Fichier statique
  |
  v
Réponse
```

Une requête dynamique peut suivre un chemin plus long :

```text
Client
  |
  v
Reverse proxy
  |
  v
Application
  |
  v
Cache applicatif ou base de données
  |
  v
Calcul / Assemblage de la réponse
  |
  v
Reverse proxy
  |
  v
Client
```

Le premier chemin est souvent plus simple à optimiser. Le second dépend aussi du comportement de l'application et de ses dépendances.

### 2.3 Une infrastructure peut être limitée à différents niveaux

```text
                DÉBIT INSUFFISANT
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
      CPU            Mémoire          Réseau
       |               |               |
       v               v               v
 Calcul coûteux   Pression mémoire   Bande passante
       |               |               |
       +---------------+---------------+
                       |
                       v
              Stockage / I/O
                       |
                       v
              Application / BDD
                       |
                       v
               Limites de concurrence
```

Il ne faut pas choisir une optimisation avant d'avoir identifié le niveau qui impose réellement la limite.


## 3. Les fondamentaux de la performance Web

### 3.1 Latence

La latence est le temps nécessaire pour obtenir un résultat.

Dans une mesure de requête HTTP, il faut distinguer plusieurs instants possibles :

- démarrage de la résolution DNS ;
- établissement de la connexion TCP ;
- négociation TLS ;
- envoi de la requête ;
- réception du premier octet de réponse ;
- réception complète de la réponse.

Une requête peut obtenir son premier octet rapidement mais mettre beaucoup de temps à transférer un fichier volumineux.

Inversement, une requête peut transférer très peu de données mais attendre longtemps le résultat du backend.

### 3.2 Débit

Le débit peut être exprimé sous différentes formes :

- requêtes par seconde ;
- octets transférés par seconde ;
- nombre d'opérations applicatives réalisées par seconde.

Pour un serveur Web, le nombre de requêtes par seconde est souvent utilisé lors des tests de charge.

Cependant, deux requêtes ne représentent pas nécessairement la même quantité de travail. Servir un petit fichier CSS n'a pas le même coût qu'exécuter une recherche complexe en base de données.

Le débit doit donc être interprété avec le type de requête testé.

### 3.3 Concurrence

La concurrence désigne le nombre d'opérations ou de requêtes simultanément en cours de traitement.

Un serveur peut avoir :

- beaucoup de connexions ouvertes ;
- peu de requêtes actives ;
- plusieurs requêtes en attente ;
- quelques requêtes coûteuses qui occupent les ressources ;
- un grand nombre de connexions HTTP persistantes mais presque inactives.

Le nombre de connexions TCP ne doit donc pas être confondu avec le nombre de requêtes qui consomment activement le processeur.

### 3.4 Capacité

La capacité est la charge que le système peut soutenir dans des conditions définies tout en respectant ses objectifs de performance.

Elle doit être spécifiée avec plusieurs critères :

- type de requête ;
- débit cible ;
- concurrence ;
- latence maximale ou percentiles attendus ;
- taux d'erreur acceptable ;
- consommation de ressources ;
- durée du test.

Un serveur capable d'atteindre ponctuellement un débit élevé pendant quelques secondes ne peut pas nécessairement maintenir ce débit durant plusieurs heures.

### 3.5 Disponibilité et performance

La performance et la disponibilité sont complémentaires, mais distinctes.

Un serveur peut répondre très vite lorsqu'il fonctionne et être indisponible le reste du temps.

Un autre peut répondre à toutes les requêtes, mais avec une latence telle que le service devient inutilisable.

Une stratégie de haute performance doit donc définir des objectifs pour les deux dimensions.


## 4. Comprendre les percentiles de latence

Une moyenne peut masquer des requêtes très lentes.

Supposons que 95 requêtes prennent 100 ms chacune, tandis que 5 requêtes prennent 2 secondes.

La moyenne sera influencée par ces cinq requêtes lentes, mais elle ne décrit pas à elle seule l'expérience de tous les utilisateurs.

Les percentiles apportent une information complémentaire.

| Mesure | Signification |
|---|---|
| p50 | 50 % des observations sont inférieures ou égales à cette valeur |
| p90 | 90 % des observations sont inférieures ou égales à cette valeur |
| p95 | 95 % des observations sont inférieures ou égales à cette valeur |
| p99 | 99 % des observations sont inférieures ou égales à cette valeur |
| p99.9 | 99,9 % des observations sont inférieures ou égales à cette valeur |

Exemple :

```text
Latence p50  :  80 ms
Latence p95  : 250 ms
Latence p99  : 900 ms
```

Cette distribution montre que la majorité des requêtes est rapide, mais qu'une minorité rencontre des délais nettement plus élevés.

La p99 peut révéler des problèmes que la moyenne cache, par exemple :

- des requêtes SQL lentes ;
- des files d'attente ;
- des pauses de récupération mémoire ;
- des blocages de dépendances ;
- des connexions répétées ;
- de la contention sur le stockage ;
- des reprises ou délais d'attente au niveau du proxy.

Pour un service important, les objectifs de performance doivent inclure au moins un objectif de latence de queue, par exemple p95 ou p99.


## 5. La loi de Little et le dimensionnement des requêtes simultanées

La loi de Little relie le nombre moyen d'éléments présents dans un système, le débit moyen et le temps moyen passé dans ce système.

Sous les hypothèses appropriées, elle s'écrit :

\[
L = \lambda W
\]

Avec :

- \(L\) : nombre moyen de requêtes en cours ;
- \(\lambda\) : débit moyen de requêtes ;
- \(W\) : durée moyenne passée dans le système.

### 5.1 Exemple de calcul

Une application traite 500 requêtes par seconde. Le temps de réponse moyen est de 0,2 seconde.

\[
L = 500 \times 0,2 = 100
\]

Le système compte environ 100 requêtes simultanément en cours dans le périmètre de mesure considéré.

Cela ne signifie pas qu'il faut configurer exactement 100 workers. Les requêtes peuvent attendre des ressources, les connexions peuvent être persistantes et chaque architecture possède ses propres mécanismes de concurrence.

La loi donne une estimation de la concurrence moyenne nécessaire au débit observé. Elle ne remplace pas les mesures de pointe ou de latence.

### 5.2 Pourquoi la latence peut faire croître la concurrence

Si le débit reste de 500 requêtes par seconde, mais que la durée moyenne passe de 0,2 à 1 seconde :

\[
L = 500 \times 1 = 500
\]

Le nombre moyen de requêtes en cours devient approximativement cinq fois plus élevé.

Une application lente peut donc consommer davantage de ressources simplement parce que les requêtes restent plus longtemps en cours.

C'est l'une des raisons pour lesquelles augmenter indéfiniment les limites de concurrence peut aggraver la situation au lieu de la corriger.


## 6. La démarche d'optimisation : mesurer avant de modifier

### 6.1 La règle fondamentale

**Ne commencez pas par modifier les paramètres. Commencez par mesurer le comportement du système.**

Sans référence, il est impossible de savoir si une configuration améliore ou dégrade le service.

Une augmentation du nombre de connexions, par exemple, peut améliorer le débit lorsque la limite était trop basse. Elle peut aussi augmenter l'utilisation mémoire, créer davantage de concurrence sur la base de données et dégrader la p99.

### 6.2 Le cycle d'optimisation

```text
            1. MESURER
                |
                v
       2. IDENTIFIER LE GOULET
                |
                v
        3. FORMULER UNE HYPOTHÈSE
                |
                v
        4. MODIFIER UN PARAMÈTRE
                |
                v
           5. RETESTER
                |
                v
       6. COMPARER LES MESURES
                |
        +-------+-------+
        |               |
        v               v
   Amélioration      Dégradation
        |               |
        v               v
  Documenter       Restaurer et
  le changement    diagnostiquer
```

Chaque modification doit être associée à une hypothèse vérifiable.

Exemple :

> Hypothèse : le nombre de connexions inactives entre Nginx et l'application provoque des établissements TCP répétés. L'activation d'un pool de connexions persistantes devrait réduire ce coût.

La validation nécessite ensuite de mesurer le nombre de connexions, le temps de réponse et les erreurs, avant et après la modification.

### 6.3 Établir une référence

Une référence de performance devrait contenir au minimum :

| Indicateur | Exemple de mesure |
|---|---|
| Débit | Requêtes/s |
| Latence moyenne | Millisecondes |
| Latence p95 | Millisecondes |
| Latence p99 | Millisecondes |
| Taux d'erreur | Pourcentage |
| CPU | Pourcentage ou temps processeur |
| Mémoire | RSS, mémoire disponible |
| Réseau | Débit entrant et sortant |
| Stockage | Latence et utilisation I/O |
| Backends | Temps de réponse, erreurs, connexions |
| Cache | Taux de HIT, MISS et BYPASS |

La référence doit également documenter la version du logiciel, les configurations, la machine, le type de trafic et l'état du cache.


## 7. Identifier le goulot d'étranglement

### 7.1 CPU saturé

Signes possibles :

- utilisation CPU durablement élevée ;
- temps de réponse qui augmente avec la concurrence ;
- débit qui ne progresse plus ;
- processus d'application très actifs ;
- compression ou calcul applicatif coûteux.

Commandes utiles :

```bash
top
```

```bash
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 15
```

Sur un système disposant de l'outil `pidstat` :

```bash
pidstat -u 1
```

Une CPU élevée n'identifie pas automatiquement le logiciel responsable. Il faut corréler les observations avec les requêtes, les journaux et les mesures applicatives.

### 7.2 Mémoire insuffisante

Signes possibles :

- utilisation élevée de mémoire ;
- pression mémoire ;
- activité de swap importante ;
- processus tués par le mécanisme OOM ;
- latence qui augmente lorsque plusieurs opérations sont simultanées.

Commandes :

```bash
free -h
```

```bash
vmstat 1
```

```bash
ps -eo pid,comm,rss,%mem --sort=-rss | head -n 15
```

Une grande quantité de mémoire utilisée par le cache de fichiers Linux n'est pas nécessairement problématique. Il faut analyser la mémoire disponible, la pression mémoire, les défauts de page et les activités de swap.

### 7.3 Stockage lent

Un serveur peut être limité par le stockage lorsqu'il sert des fichiers volumineux, lit des données qui ne sont pas en cache ou utilise un cache disque sous forte charge.

Si `iostat` est installé :

```bash
iostat -xz 1
```

Selon le type de périphérique et le système de stockage, les métriques importantes peuvent inclure :

- temps d'attente ;
- latence de lecture et d'écriture ;
- débit ;
- profondeur de file ;
- utilisation du périphérique.

Une forte valeur d'utilisation d'un périphérique ne doit pas être interprétée isolément. Il faut comparer les latences, le débit et les capacités du stockage concerné.

### 7.4 Réseau saturé

Signes possibles :

- débit proche de la capacité de l'interface ;
- transferts plus lents lorsque plusieurs clients téléchargent ;
- pertes ou retransmissions ;
- latence réseau qui augmente sous charge.

Commandes :

```bash
ip -s link
```

```bash
ss -s
```

Sur un système disposant d'outils complémentaires, utilisez aussi les compteurs de l'interface, la télémétrie réseau et les statistiques du routeur ou du fournisseur.

Une interface à 100 % d'utilisation n'est pas le seul signe d'un problème réseau. Les pertes, la congestion sur le chemin et les temps d'aller-retour peuvent également limiter les performances.

### 7.5 Application ou base de données saturée

Le serveur Web peut rester peu chargé alors que les utilisateurs observent une latence élevée.

C'est fréquent lorsque :

- l'application exécute des requêtes SQL coûteuses ;
- le pool de connexions à la base est épuisé ;
- un service externe répond lentement ;
- un verrou bloque des opérations ;
- l'application attend un autre service ;
- la concurrence est limitée par un pool de workers trop petit.

Dans ces situations, optimiser `worker_connections` ou le nombre de threads Apache peut n'apporter aucun gain.


## 8. Mesurer les différentes phases d'une requête avec curl

La commande `curl` peut mesurer plusieurs phases temporelles d'une requête.

Exemple :

```bash
curl -sS -o /dev/null \
  -w 'dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s code=%{http_code} bytes=%{size_download}\n' \
  https://www.exemple.com/
```

Remplacez l'URL par une cible que vous êtes autorisé à tester.

### 8.1 Interprétation des champs

- `time_namelookup` : temps associé à la résolution du nom ;
- `time_connect` : temps écoulé jusqu'à l'établissement de la connexion TCP ;
- `time_appconnect` : temps écoulé jusqu'à la connexion TLS lorsqu'elle est applicable ;
- `time_starttransfer` : temps jusqu'au premier octet de la réponse ;
- `time_total` : durée totale de l'opération ;
- `http_code` : code HTTP obtenu ;
- `size_download` : quantité de données téléchargées.

Ces mesures sont cumulatives pour plusieurs champs. Il ne faut pas additionner directement tous les nombres pour calculer une durée globale.

Le temps DNS peut être très faible lors d'une réutilisation de résolution ou dépendre du cache du système. Le premier octet inclut plusieurs phases antérieures au transfert de la réponse.

### 8.2 Mesurer plusieurs fois

Une seule requête ne constitue pas un benchmark représentatif.

Utilisez plusieurs échantillons, puis comparez les distributions.

Exemple de boucle :

```bash
for i in $(seq 1 10); do
    curl -sS -o /dev/null \
      -w 'ttfb=%{time_starttransfer}s total=%{time_total}s code=%{http_code}\n' \
      http://127.0.0.1:8080/
done
```

Une boucle permet d'observer des variations, mais elle ne crée pas à elle seule une charge concurrente importante.

Il faut aussi distinguer les requêtes froides, qui rencontrent éventuellement des caches vides, des requêtes répétées qui profitent des caches déjà alimentés.


## 9. Performance des connexions et du protocole HTTP

### 9.1 Le coût d'une connexion

Une requête peut nécessiter :

1. une résolution DNS ;
2. une connexion TCP ;
3. une négociation TLS ;
4. l'envoi de la requête ;
5. le traitement serveur ;
6. le transfert de la réponse.

Pour une ressource très petite, le coût de création d'une connexion peut représenter une partie importante de la durée totale.

Pour une ressource volumineuse, le débit réseau et le temps de transfert peuvent dominer.

### 9.2 Connexions persistantes

Les connexions HTTP persistantes permettent de réutiliser une connexion au lieu d'en créer une nouvelle pour chaque requête.

Elles peuvent diminuer le coût de connexion et, pour HTTPS, éviter une nouvelle négociation TLS à chaque requête.

Elles consomment toutefois des ressources et doivent être gérées selon les limites de concurrence.

### 9.3 HTTP/1.1, HTTP/2 et HTTP/3

HTTP/1.1 permet les connexions persistantes et peut utiliser plusieurs connexions pour transférer les ressources.

HTTP/2 permet de multiplexer plusieurs flux sur une même connexion TCP. Il peut réduire certains coûts, notamment lors du chargement de nombreuses ressources, mais n'élimine pas tous les effets d'une congestion TCP.

HTTP/3 utilise QUIC sur UDP et présente un autre modèle de gestion des connexions et des pertes. Son efficacité dépend des clients, du réseau, de l'implémentation et de la charge.

Aucun protocole ne garantit à lui seul une amélioration pour tous les sites. Il faut le tester sur des scénarios représentatifs.


## 10. Nginx : comprendre les processus de travail

Nginx utilise habituellement un processus maître et plusieurs processus de travail.

```text
                    NGINX
                      |
                      v
              Processus maître
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Worker 1    Worker 2    Worker 3
          |           |           |
          v           v           v
       Clients     Clients     Clients
       Upstream    Upstream    Upstream
```

Le processus maître gère notamment la configuration et les processus de travail. Les workers traitent les connexions selon le modèle événementiel de Nginx.

### 10.1 `worker_processes`

La directive `worker_processes` définit le nombre de processus de travail.

Une configuration courante est :

```nginx
worker_processes auto;
```

Cette valeur demande à Nginx d'essayer de déterminer un nombre adapté aux processeurs disponibles.

Ce réglage constitue un point de départ, pas une garantie d'optimalité. Le nombre de workers peut être influencé par l'affinité CPU, les ressources du conteneur, la charge et l'architecture réelle de la machine.

### 10.2 `worker_connections`

La directive `worker_connections` définit le nombre maximal de connexions simultanées ouvertes par un worker.

Exemple :

```nginx
events {
    worker_connections 2048;
}
```

Cette valeur doit être dimensionnée avec les limites de fichiers ouverts et les besoins du service.

**Une connexion au backend compte également parmi les connexions du worker.** Il ne suffit donc pas de multiplier le nombre de workers par le nombre de connexions pour obtenir exactement le nombre de clients pouvant être servis dans toutes les architectures.

### 10.3 Estimation théorique des connexions

Considérons :

```text
4 workers
2048 connexions maximum par worker
```

La limite théorique issue de ces deux paramètres est :

\[
4 \times 2048 = 8192
\]

Cette valeur ne signifie pas que la machine pourra nécessairement servir 8192 clients actifs en permanence.

Il faut également considérer :

- les connexions clientes ;
- les connexions aux backends ;
- les fichiers ouverts ;
- les sockets et autres descripteurs ;
- la mémoire ;
- les limites du système ;
- les besoins de l'application ;
- la charge CPU et les temps de réponse.

Un reverse proxy peut avoir besoin de plusieurs connexions par requête en cours, une vers le client et une vers le backend, tandis qu'une connexion cliente persistante n'implique pas que toutes les requêtes soient simultanément actives.

### 10.4 Limites des descripteurs de fichiers

Chaque socket et chaque fichier ouvert utilise des descripteurs.

Pour observer une limite de processus :

```bash
ulimit -n
```

Cette commande affiche la limite du shell courant, mais elle ne garantit pas que le service systemd utilise la même limite.

Pour le service Nginx :

```bash
systemctl show nginx -p LimitNOFILE
```

Vous pouvez également examiner les limites d'un processus réel :

```bash
cat /proc/$(pgrep -o nginx)/limits
```

Le PID sélectionné dépend de l'organisation des processus. Vérifiez que vous examinez le processus prévu.

### 10.5 `worker_rlimit_nofile`

Nginx dispose de la directive :

```nginx
worker_rlimit_nofile 8192;
```

Elle permet de modifier la limite de fichiers ouverts des workers, sous réserve des limites imposées au processus par le système.

Ne choisissez pas une valeur arbitraire très élevée en pensant qu'elle augmentera automatiquement les performances. La limite doit correspondre aux besoins réels et aux plafonds autorisés par systemd et le noyau.


## 11. Nginx : exemple de configuration de performance

Les valeurs suivantes sont des exemples de départ pour une installation de test. Elles ne doivent pas être copiées aveuglément dans une infrastructure de production.

```nginx
worker_processes auto;

events {
    worker_connections 2048;
}

http {
    sendfile on;
    tcp_nopush on;

    keepalive_timeout 15s;
    keepalive_requests 1000;

    server_tokens off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Déclarations des serveurs, journaux,
    # caches et règles de routage.
}
```

### 11.1 `sendfile`

La directive :

```nginx
sendfile on;
```

permet d'utiliser le mécanisme `sendfile` du système pour transmettre certains fichiers, ce qui peut éviter des copies de données inutiles dans certaines situations.

Elle est notamment pertinente pour un serveur qui sert des fichiers statiques.

Son intérêt dépend du système, du type de fichier et du chemin de transfert.

### 11.2 `tcp_nopush`

La directive :

```nginx
tcp_nopush on;
```

est généralement utilisée avec `sendfile` sur les systèmes compatibles pour contrôler la façon dont les en-têtes et les données sont envoyés dans certains scénarios.

Elle ne doit pas être interprétée comme une optimisation universelle de toutes les requêtes.

### 11.3 `keepalive_timeout`

Exemple :

```nginx
keepalive_timeout 15s;
```

Cette directive contrôle la période pendant laquelle une connexion cliente inactive peut rester ouverte.

Une valeur très basse peut augmenter les connexions répétées. Une valeur très élevée peut conserver davantage de connexions inactives et utiliser des ressources.

Il faut choisir une valeur cohérente avec le trafic, les clients et les limites de capacité.

### 11.4 `keepalive_requests`

Exemple :

```nginx
keepalive_requests 1000;
```

Cette directive limite le nombre de requêtes pouvant être traitées sur une connexion persistante avant sa fermeture selon le comportement configuré.

Une valeur élevée réduit éventuellement les coûts de reconnexion, mais doit être évaluée avec les besoins de répartition de charge, la consommation mémoire et les interactions avec les upstreams.

### 11.5 `server_tokens`

```nginx
server_tokens off;
```

Cette directive limite l'exposition de la version du serveur dans certaines réponses d'erreur.

Elle peut réduire l'information fournie aux clients, mais elle ne remplace ni les mises à jour ni la correction des vulnérabilités.


## 12. Nginx : cache des fichiers et métadonnées

### 12.1 Pourquoi utiliser un cache de fichiers ?

Lorsqu'un serveur sert fréquemment des fichiers statiques, il doit accéder à leur contenu et consulter certaines métadonnées du système de fichiers.

Le cache de fichiers Linux permet déjà de conserver en mémoire des données de fichiers utilisées récemment.

Nginx propose aussi une mise en cache de certaines informations liées aux fichiers ouverts.

Exemple :

```nginx
http {
    open_file_cache max=10000 inactive=30s;
    open_file_cache_valid 60s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
}
```

### 12.2 Rôle des directives

`open_file_cache` contrôle le cache de descripteurs ouverts et d'informations de fichiers.

`max` indique le nombre maximal d'entrées dans le cache.

`inactive` définit une période après laquelle une entrée inutilisée peut être retirée.

`open_file_cache_valid` définit la fréquence de vérification de la validité des informations conservées.

`open_file_cache_min_uses` limite le maintien des entrées à celles qui sont utilisées assez fréquemment dans la période concernée.

`open_file_cache_errors on` permet également de conserver certains résultats d'erreur liés à l'ouverture ou à l'accès aux fichiers.

### 12.3 Précautions

Ce type de cache est à évaluer particulièrement pour les serveurs qui servent des contenus statiques très sollicités.

Il faut considérer :

- la fréquence de modification des fichiers ;
- la visibilité des changements de permission ;
- le nombre de fichiers distincts ;
- la quantité de mémoire disponible ;
- les comportements observés sous charge.

N'ajoutez pas ce cache à une configuration uniquement parce qu'il semble avantageux. Mesurez le coût actuel des accès au système de fichiers et vérifiez que la configuration conserve le comportement attendu lors des mises à jour.


## 13. Nginx : connexions persistantes vers les backends

### 13.1 Le problème des connexions répétées

Un reverse proxy qui transmet de nombreuses requêtes à une application peut devoir établir régulièrement des connexions vers le backend.

Cela peut ajouter des coûts de connexion TCP, de gestion des sockets et éventuellement de négociation TLS si le backend utilise HTTPS.

Les pools de connexions persistantes permettent de réutiliser certaines connexions inactives.

### 13.2 Configurer un pool upstream

Exemple :

```nginx
upstream application_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;

    keepalive 32;
}
```

Puis, dans le bloc de proxy :

```nginx
location / {
    proxy_pass http://application_backend;

    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
```

Le paramètre `keepalive` dans le bloc `upstream` correspond au nombre maximal de connexions inactives conservées dans le cache par worker pour ce groupe. Il ne représente pas une limite globale du nombre de connexions actives vers les backends.

La réutilisation exige un comportement compatible du serveur applicatif et une configuration appropriée du protocole.

### 13.3 Déterminer si cette optimisation est utile

Mesurez notamment :

- le nombre de connexions TCP vers les backends ;
- la fréquence de création des connexions ;
- le temps de réponse ;
- la consommation de sockets et de descripteurs ;
- les erreurs et délais d'attente ;
- le comportement du backend avec des connexions persistantes.

Un pool excessivement grand peut conserver des ressources dont l'application a besoin pour d'autres tâches.

### 13.4 Connexions persistantes et répartition de charge

Un pool de connexions persistantes n'est pas la même chose qu'une session cliente persistante.

La première notion concerne la réutilisation de connexions entre le proxy et les serveurs applicatifs.

La seconde concerne la décision de renvoyer un utilisateur ou une session vers une instance particulière.

Ces deux mécanismes ont des objectifs différents.


## 14. Nginx : buffering des requêtes et des réponses

### 14.1 Comprendre le buffering

Le buffering permet à Nginx de lire ou de stocker temporairement certaines données plutôt que de transmettre chaque fragment immédiatement dans toutes les situations.

Pour une réponse d'application, le mécanisme peut permettre à Nginx de lire plus rapidement les données du backend et d'envoyer la réponse au client selon son propre rythme.

```text
Application
    |
    | Réponse
    v
+--------------------+
| Buffering Nginx    |
| Mémoire / temporaire|
+--------------------+
    |
    | Envoi contrôlé
    v
Client
```

### 14.2 Pourquoi le buffering peut aider

Le buffering peut :

- limiter le temps pendant lequel le backend reste occupé par un client lent ;
- séparer le débit du backend de celui du client ;
- améliorer la gestion de certaines réponses volumineuses ;
- utiliser des fichiers temporaires lorsque les données ne tiennent pas en mémoire.

### 14.3 Quand le buffering peut gêner

Pour une application qui envoie des événements en continu, une réponse progressive ou un flux interactif, un buffering trop important peut retarder la livraison des données.

Il faut alors adapter le comportement du proxy au protocole et aux objectifs applicatifs.

Exemple conceptuel :

```nginx
location /events/ {
    proxy_pass http://application_backend;
    proxy_buffering off;
}
```

Ne désactivez pas le buffering sur toutes les routes pour résoudre un problème d'une seule application.

### 14.4 Taille des buffers

Les directives de buffering doivent être ajustées seulement après avoir observé les besoins réels :

- taille habituelle des réponses ;
- mémoire consommée par requête ;
- débit entre le backend et le proxy ;
- débit entre le proxy et le client ;
- fréquence d'utilisation de fichiers temporaires ;
- durée des requêtes.

Augmenter toutes les tailles de buffers peut augmenter la consommation mémoire et réduire la capacité totale du serveur.


## 15. Compression HTTP

### 15.1 Pourquoi compresser les réponses ?

La compression réduit la quantité de données envoyées sur le réseau pour les contenus qui s'y prêtent.

Les contenus textuels sont généralement de bons candidats :

- HTML ;
- CSS ;
- JavaScript ;
- JSON ;
- XML ;
- certains fichiers SVG.

Les images JPEG ou PNG, les archives ZIP et les vidéos déjà compressées apportent souvent peu de gain supplémentaire.

### 15.2 Compression et ressources

La compression implique un compromis entre :

- taille du transfert ;
- temps CPU ;
- mémoire ;
- latence ;
- réutilisation des réponses.

Si le réseau est le principal goulot d'étranglement, la compression peut améliorer les performances.

Si le CPU est déjà saturé, une compression trop coûteuse peut dégrader les temps de réponse.

### 15.3 Configurer gzip avec Nginx

Dans le contexte `http` :

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 4;

gzip_types
    text/plain
    text/css
    application/json
    application/javascript
    application/xml
    image/svg+xml;
```

Le type `text/html` est pris en charge par Nginx lorsque gzip est activé et ne doit pas nécessairement être ajouté explicitement à `gzip_types`.

### 15.4 Explication des directives

`gzip on` active la compression gzip.

`gzip_vary on` permet de gérer l'en-tête `Vary: Accept-Encoding`, important pour que les caches tiennent compte des préférences de compression.

`gzip_min_length` évite notamment de compresser les réponses trop petites selon le seuil défini.

`gzip_comp_level` contrôle le niveau de compression. Une valeur élevée peut réduire davantage la taille de certaines réponses, mais demander davantage de CPU.

`gzip_types` définit les types de contenu supplémentaires concernés.

### 15.5 Vérifier la compression

Envoyez une requête qui indique au serveur que gzip est accepté :

```bash
curl -sSI -H 'Accept-Encoding: gzip' http://127.0.0.1:8080/
```

Examinez la présence éventuelle de :

```text
Content-Encoding: gzip
Vary: Accept-Encoding
```

Le comportement dépend de la taille de la réponse, de son type, de la configuration et des filtres appliqués.

Pour mesurer le gain réel, comparez la taille transférée, la latence et le CPU avant et après la modification.

### 15.6 Risques de sécurité de la compression

La compression de réponses TLS contenant simultanément des secrets et des données influencées par un attaquant peut contribuer à certaines attaques de type BREACH dans des scénarios spécifiques.

La compression ne doit pas être désactivée partout sans examen, mais les réponses dynamiques contenant des secrets réfléchis doivent être étudiées avec attention.

Une politique de compression doit tenir compte du contenu, du modèle de menace et du chemin d'exécution.


## 16. Apache : comprendre les modèles MPM

Apache HTTP Server utilise un MPM, ou *Multi-Processing Module*, qui détermine une partie de son modèle de création et de gestion des processus, threads et requêtes.

Les modèles courants comprennent notamment :

- `prefork` ;
- `worker` ;
- `event`.

### 16.1 MPM prefork

Le modèle `prefork` utilise des processus enfants distincts pour servir les requêtes.

Schéma simplifié :

```text
              Apache parent
                    |
       +------------+------------+
       |            |            |
       v            v            v
   Processus 1  Processus 2  Processus 3
      |             |             |
      v             v             v
   Requête       Requête       Requête
```

Ce modèle peut être approprié pour certaines configurations anciennes ou certains modules qui ne sont pas compatibles avec un modèle multithread, mais il peut consommer davantage de mémoire à forte concurrence.

### 16.2 MPM worker

Le modèle `worker` utilise plusieurs processus et des threads au sein de ces processus.

```text
              Apache parent
                    |
           +--------+--------+
           |                 |
           v                 v
        Processus 1       Processus 2
         /  |  \           /  |  \
        T1  T2  T3        T4  T5  T6
```

Cette architecture permet de traiter plusieurs requêtes avec des threads, tout en conservant plusieurs processus.

### 16.3 MPM event

Le modèle `event` s'appuie aussi sur des processus et des threads, avec une gestion améliorée des connexions persistantes inactives.

Il est souvent un bon point de départ pour un serveur Apache moderne qui utilise des modules compatibles avec le multithreading.

Il ne garantit pas automatiquement de meilleures performances dans toutes les applications. La configuration, les modules chargés et le type de trafic restent déterminants.

### 16.4 Vérifier le MPM actif

Sur Debian ou Ubuntu :

```bash
apachectl -V
```

Pour examiner les modules chargés :

```bash
sudo apachectl -M
```

Vous pouvez rechercher le module MPM, par exemple `mpm_event_module`.

**Ne changez pas le MPM sans vérifier la compatibilité des modules d'application.** Certains environnements utilisant un module PHP intégré peuvent imposer des contraintes différentes de ceux qui utilisent PHP-FPM.


## 17. Apache : dimensionner les threads et les workers

Les directives importantes du MPM comprennent notamment :

- `StartServers` ;
- `ThreadsPerChild` ;
- `MaxRequestWorkers` ;
- `MinSpareThreads` ;
- `MaxSpareThreads` ;
- `ServerLimit` ;
- `MaxConnectionsPerChild`.

### 17.1 `ThreadsPerChild`

Cette directive détermine le nombre de threads créés dans chaque processus enfant pour les MPM qui utilisent des threads.

Exemple :

```apache
ThreadsPerChild 25
```

Le nombre effectif doit être cohérent avec les limites globales, la mémoire et les capacités du système.

### 17.2 `MaxRequestWorkers`

Cette directive limite le nombre maximal de requêtes simultanément servies par Apache selon son modèle MPM.

Exemple :

```apache
MaxRequestWorkers 150
```

Cette valeur ne doit pas être interprétée comme un débit de 150 requêtes par seconde. Elle représente une limite de concurrence.

Pour les MPM multithreadés, la relation avec `ThreadsPerChild` et `ServerLimit` doit être cohérente. `MaxRequestWorkers` doit être au moins égal à `ThreadsPerChild` et être un multiple convenable de ce dernier.

### 17.3 Exemple de configuration de base

Dans une configuration Apache qui utilise `mpm_event`, un exemple de départ pourrait être :

```apache
<IfModule mpm_event_module>
    StartServers             2
    MinSpareThreads         25
    MaxSpareThreads         75
    ThreadsPerChild         25
    MaxRequestWorkers      150
    MaxConnectionsPerChild 10000
</IfModule>
```

Les nombres sont illustratifs. Ils ne constituent pas un dimensionnement recommandé pour toutes les machines.

### 17.4 Mémoire et concurrence

Pour choisir `MaxRequestWorkers`, il faut mesurer la consommation mémoire de l'ensemble du service et examiner la variation avec la concurrence.

Une approche pratique consiste à :

1. relever la mémoire du service à charge faible ;
2. mesurer la consommation lorsque la concurrence augmente ;
3. identifier les processus ou threads actifs ;
4. garder une marge pour les autres services et les pics ;
5. configurer une limite cohérente ;
6. effectuer un test de charge représentatif.

Il ne faut pas calculer le nombre de workers à partir de la RAM totale sans tenir compte de la mémoire nécessaire à l'OS, au cache de fichiers, aux applications, aux modules et aux autres services.

### 17.5 `MaxConnectionsPerChild`

Cette directive détermine combien de connexions un processus enfant peut servir avant d'être recyclé, selon les règles du MPM.

Elle n'est pas identique à `MaxRequestWorkers`.

Le recyclage peut être utile dans certains environnements, notamment lorsqu'une accumulation de ressources doit être contenue, mais un recyclage trop fréquent peut augmenter le coût de création des processus.

Utilisez-le comme un paramètre d'exploitation mesuré, et non comme un remède générique aux problèmes de mémoire.


## 18. Apache : garder les connexions sous contrôle

### 18.1 Connexions persistantes

Apache permet de configurer les connexions persistantes.

Exemple :

```apache
KeepAlive On
MaxKeepAliveRequests 100
KeepAliveTimeout 2
```

Ces paramètres doivent être évalués dans le contexte du MPM et du type de trafic.

`KeepAlive On` active les connexions persistantes.

`MaxKeepAliveRequests` définit le nombre maximal de requêtes permises sur une connexion persistante.

`KeepAliveTimeout` fixe le délai pendant lequel Apache attend une autre requête sur une connexion persistante inactive.

### 18.2 Pourquoi le délai est important

Un délai trop bas peut augmenter les connexions et négociations répétées.

Un délai trop haut peut conserver inutilement des connexions inactives et consommer des ressources, surtout dans des modèles qui mobilisent davantage de workers pour gérer ces connexions.

Le MPM `event` gère différemment certaines connexions inactives, mais il reste nécessaire d'observer le comportement réel du service.

### 18.3 Éviter les changements aveugles

Avant de modifier ces paramètres, observez :

- le nombre de connexions actives ;
- le nombre de connexions en attente ;
- la durée de connexion ;
- les temps de réponse ;
- la consommation mémoire ;
- les connexions au backend ;
- les erreurs réseau.

Les valeurs habituelles d'un site à fort trafic statique ne seront pas nécessairement adaptées à une application dynamique avec des traitements longs.


## 19. Compression avec Apache

Apache utilise notamment `mod_deflate` pour compresser certaines réponses.

Sur Debian ou Ubuntu, vérifiez que le module est disponible puis activez-le :

```bash
sudo a2enmod deflate
```

Pour les en-têtes, si nécessaire :

```bash
sudo a2enmod headers
```

Une configuration peut prendre la forme suivante :

```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE \
        text/html \
        text/plain \
        text/css \
        application/javascript \
        application/json \
        application/xml \
        image/svg+xml
</IfModule>
```

Les types exacts doivent correspondre à ceux servis par le site. Vérifiez le fichier de configuration et le type MIME effectivement transmis.

Apache doit disposer des modules nécessaires et d'une configuration qui permet la compression du contenu concerné.

### 19.1 Comprendre le coût

La compression diminue le volume transmis pour les contenus qui s'y prêtent, mais consomme du CPU.

Un niveau de compression plus élevé peut améliorer le ratio au prix d'un calcul plus important.

La stratégie doit donc correspondre au goulot d'étranglement mesuré.

Si le serveur est principalement limité par la bande passante, la compression peut être très utile. Si le CPU est saturé, une compression excessive peut produire l'effet inverse.

### 19.2 Contrôle

Testez la réponse :

```bash
curl -sSI -H 'Accept-Encoding: gzip' http://127.0.0.1/
```

Contrôlez notamment :

```text
Content-Encoding
Vary
Content-Type
```

Le résultat dépend des filtres, des modules et de la configuration du serveur.


## 20. Mise en cache : concepts essentiels

Le cache est souvent l'un des leviers les plus efficaces pour réduire les coûts d'un site, à condition d'être correctement utilisé.

### 20.1 Les différents niveaux de cache

```text
                  CLIENT
                    |
                    v
          +-------------------+
          | Cache navigateur  |
          +-------------------+
                    |
                    v
          +-------------------+
          | CDN / cache edge  |
          +-------------------+
                    |
                    v
          +-------------------+
          | Cache reverse     |
          | proxy              |
          +-------------------+
                    |
                    v
          +-------------------+
          | Application       |
          +-------------------+
                    |
                    v
          +-------------------+
          | Cache applicatif  |
          +-------------------+
                    |
                    v
          +-------------------+
          | Base de données   |
          +-------------------+
```

Tous ces caches n'ont pas le même rôle.

Le cache navigateur évite parfois de redemander un contenu déjà stocké localement.

Un CDN peut servir des contenus depuis une infrastructure proche du client.

Le cache reverse proxy peut éviter de solliciter l'application pour certaines requêtes.

Le cache applicatif peut éviter des recalculs ou des accès répétitifs aux données.

Chaque niveau doit avoir une politique de cohérence et d'invalidation adaptée.

### 20.2 Quel est le gain d'un cache ?

Si une requête coûte 50 ms lorsqu'elle atteint l'application et 5 ms lorsqu'elle est servie depuis le cache, le coût moyen peut diminuer fortement si une grande proportion des requêtes produit des hits.

Mais ce résultat suppose que les réponses peuvent être réutilisées correctement et que les mesures incluent les mêmes opérations.

Un cache mal configuré peut :

- servir des données périmées ;
- mélanger des réponses personnalisées ;
- diminuer le taux de succès ;
- consommer de la mémoire ou du stockage ;
- masquer les erreurs de l'application ;
- rendre les invalidations difficiles.

### 20.3 Choisir les bonnes ressources

Les ressources généralement candidates sont :

- les fichiers statiques versionnés ;
- les pages publiques dont le contenu évolue peu ;
- les résultats de recherche publics avec une politique de fraîcheur adaptée ;
- certaines réponses d'API publiques ;
- certains contenus pré-calculés.

Les ressources sensibles, personnalisées ou dépendant de l'identité de l'utilisateur exigent des précautions beaucoup plus fortes.


## 21. Nginx : cache reverse proxy

### 21.1 Définir un espace de cache

Une zone de cache doit être définie dans le contexte `http`.

Exemple :

```nginx
proxy_cache_path /var/cache/nginx/public-cache
    levels=1:2
    keys_zone=public_cache:50m
    max_size=2g
    inactive=60m
    use_temp_path=off;
```

Les paramètres signifient notamment :

- `levels` : organisation des fichiers du cache ;
- `keys_zone` : nom de la zone de mémoire partagée et taille de sa zone d'index ;
- `max_size` : limite de taille du cache sur le stockage ;
- `inactive` : durée après laquelle une entrée inutilisée peut être supprimée ;
- `use_temp_path=off` : permet d'utiliser le chemin du cache pour les fichiers temporaires liés à cette mise en cache, selon le fonctionnement du module.

La taille de la zone `keys_zone` ne représente pas la taille totale des réponses stockées sur disque.

### 21.2 Préparer les permissions

Sur Debian et Ubuntu, l'utilisateur Nginx est souvent `www-data`, mais il faut vérifier l'utilisateur réel dans la configuration.

Un exemple d'initialisation :

```bash
sudo install -d -m 0750 -o www-data -g www-data /var/cache/nginx/public-cache
```

Adaptez le propriétaire si votre installation utilise un autre compte.

### 21.3 Définir un backend

Exemple :

```nginx
upstream catalogue_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;

    keepalive 32;
}
```

### 21.4 Configurer le cache

Exemple pour une route exclusivement publique :

```nginx
server {
    listen 127.0.0.1:8080;
    server_name cache-lab.test;

    location /catalogue-public/ {
        proxy_pass http://catalogue_backend;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_cache public_cache;
        proxy_cache_methods GET HEAD;
        proxy_cache_key "$scheme$host$request_uri";

        proxy_cache_valid 200 10m;
        proxy_cache_lock on;

        proxy_cache_bypass $http_authorization $cookie_session;
        proxy_no_cache $http_authorization $cookie_session $upstream_http_set_cookie;

        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

Ce bloc doit être intégré à une configuration dont le contexte et les upstreams sont définis correctement.

### 21.5 Pourquoi cette configuration exclut certaines réponses ?

Le cache est limité aux méthodes `GET` et `HEAD`.

L'en-tête d'autorisation et le cookie de session permettent de contourner le cache lorsque ces éléments indiquent que la réponse peut être privée.

La directive `proxy_no_cache` empêche notamment le stockage de certaines réponses associées à une authentification ou à un cookie de session, ainsi que des réponses contenant `Set-Cookie` dans l'exemple ci-dessus.

Cette protection ne remplace pas une politique de cache conçue en fonction de l'application. Les ressources publiques doivent être séparées des ressources privées et le backend doit fournir des en-têtes HTTP de fraîcheur cohérents.

### 21.6 Interpréter les statuts du cache

Le champ `$upstream_cache_status` permet notamment d'observer les états de cache.

Les valeurs rencontrées peuvent inclure :

- `MISS` : le cache ne contenait pas une réponse réutilisable ;
- `HIT` : une réponse a été servie depuis le cache ;
- `BYPASS` : le cache a été contourné selon la configuration ;
- `EXPIRED` : une entrée était expirée ;
- `STALE` : une réponse périmée a été servie selon une politique applicable ;
- `UPDATING` : une mise à jour du cache est en cours dans un scénario compatible.

Les statuts disponibles dépendent du chemin suivi par la requête et des règles applicables.

### 21.7 Vérifier le cache

Testez une première requête :

```bash
curl -sSI http://127.0.0.1:8080/catalogue-public/
```

Puis répétez-la :

```bash
curl -sSI http://127.0.0.1:8080/catalogue-public/
```

Si la réponse est cacheable et que le backend renvoie les en-têtes appropriés, la deuxième requête peut devenir un hit.

La présence d'un `MISS` au premier passage ne garantit pas qu'une réponse sera stockée. Les réponses non cacheables, les directives HTTP, les cookies et l'authentification peuvent empêcher la mise en cache.

### 21.8 Empêcher le cache d'exposer des données privées

Ne mettez pas en cache des réponses personnalisées sans une conception explicite de la clé, de la politique de stockage et de l'invalidation.

Une mauvaise clé de cache peut conduire à servir à un utilisateur les données préparées pour un autre utilisateur.

Pour une API privée, il est généralement préférable de désactiver le cache partagé tant qu'une analyse complète n'a pas montré que les réponses peuvent être réutilisées de manière sûre.

### 21.9 Servir temporairement du contenu périmé

Nginx permet, dans certaines configurations, d'autoriser le service de réponses périmées lors d'erreurs de backend ou d'une mise à jour en cours.

Exemple à envisager uniquement pour des ressources publiques qui acceptent ce comportement :

```nginx
proxy_cache_use_stale
    error
    timeout
    updating
    http_500
    http_502
    http_503
    http_504;

proxy_cache_background_update on;
```

Cette stratégie peut améliorer la disponibilité perçue de contenus publics, mais elle n'est pas appropriée à toutes les données.

Elle doit être accompagnée d'une politique sur la fraîcheur maximale acceptable et la gestion des invalidations.


## 22. Cache HTTP côté navigateur

### 22.1 Cache-Control

Les navigateurs et les caches conformes à HTTP interprètent des en-têtes qui définissent la politique de cache.

Par exemple :

```text
Cache-Control: public, max-age=3600
```

Cette valeur indique une durée de fraîcheur d'une heure pour une réponse destinée à pouvoir être stockée par les caches concernés.

D'autres directives existent, notamment `private`, `no-store`, `no-cache` et `must-revalidate`. Elles n'ont pas toutes la même signification.

Il faut distinguer :

- l'autorisation de stocker une réponse ;
- la durée pendant laquelle elle est considérée fraîche ;
- la nécessité de valider une réponse avant réutilisation ;
- l'interdiction de conserver certaines réponses.

### 22.2 Ressources versionnées

Une stratégie courante consiste à inclure un identifiant de version ou un hash dans le nom du fichier :

```text
app.3fa921.css
main.7b2c103.js
logo.9188aa.svg
```

Lorsque le contenu change, le nom change également. Cela permet de conserver une politique de cache longue pour les versions immuables.

Une configuration Nginx pour des ressources effectivement versionnées peut utiliser :

```nginx
location ~* \.(?:css|js|svg|woff2)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

Ne placez pas de ressources susceptibles de changer sous cette politique sans modifier leur URL à chaque changement.

Sinon, les clients peuvent continuer à utiliser une ancienne version durant la période de fraîcheur.

### 22.3 Ressources non versionnées

Une page HTML ou un fichier susceptible d'être remplacé à la même URL doit généralement suivre une politique plus prudente.

Le cache peut être plus court ou utiliser des validateurs tels que `ETag` et `Last-Modified`.

Le client peut alors demander au serveur si la représentation a changé. Le serveur peut répondre `304 Not Modified` lorsque la réponse stockée reste valide.

Le choix entre une longue durée de cache et une revalidation dépend du cycle de publication du site.


## 23. Cache dans Apache

Apache dispose de mécanismes de cache, notamment `mod_cache` et des gestionnaires de stockage tels que `mod_cache_disk`.

### 23.1 Activer les modules nécessaires

Sur Debian ou Ubuntu :

```bash
sudo a2enmod cache cache_disk
```

Vérifiez ensuite la configuration :

```bash
sudo apachectl configtest
```

Le cache disque nécessite un répertoire adapté au stockage.

### 23.2 Exemple de configuration

Une configuration de base pour un ensemble de ressources publiques peut prendre la forme suivante :

```apache
CacheRoot "/var/cache/apache2/mod_cache_disk"

CacheDirLevels 2
CacheDirLength 1

CacheEnable disk /assets/
```

Le chemin du cache doit exister et être accessible par le service selon les exigences de la configuration.

### 23.3 Préparer le répertoire

Sur une installation Debian ou Ubuntu dont le compte de service est `www-data` :

```bash
sudo install -d -m 0750 -o www-data -g www-data /var/cache/apache2/mod_cache_disk
```

Adaptez le propriétaire et les permissions à votre installation réelle.

### 23.4 Comprendre le comportement de la mise en cache

L'activation de `CacheEnable` ne signifie pas que toutes les réponses peuvent être stockées sans condition.

Le contenu doit être cacheable selon les règles HTTP, les en-têtes du backend, les règles d'Apache et les modules de stockage disponibles.

Il faut contrôler la fraîcheur, les réponses privées, les en-têtes `Set-Cookie`, les validations et les conditions de revalidation.

### 23.5 Comparaison avec Nginx

Les deux logiciels peuvent mettre en cache des réponses, mais leurs syntaxes, leurs modules et leurs possibilités de configuration diffèrent.

Le choix doit tenir compte :

- du comportement attendu ;
- du type de ressources ;
- du modèle de proxy ;
- du contrôle de fraîcheur ;
- de l'invalidation ;
- des besoins de supervision ;
- des connaissances opérationnelles de l'équipe.

Un cache doit toujours être conçu pour le contenu qu'il sert.


## 24. HTTP/2 et HTTP/3 : optimisation des protocoles

### 24.1 HTTP/2

HTTP/2 apporte notamment la possibilité de multiplexer plusieurs flux sur une connexion et de compresser les en-têtes.

Il peut réduire les coûts associés au chargement de nombreuses ressources, mais ses gains dépendent du réseau, du serveur, de la charge et du comportement des clients.

Pour Nginx, la disponibilité du module HTTP/2 dépend de la compilation et de la version installée.

Une configuration HTTPS moderne peut ressembler à ceci :

```nginx
server {
    listen 443 ssl;
    http2 on;

    server_name app.exemple.com;

    ssl_certificate     /chemin/vers/certificat.pem;
    ssl_certificate_key /chemin/vers/cle-privee.pem;

    location / {
        root /var/www/site;
        index index.html;
    }
}
```

Les chemins des certificats sont des exemples.

Sur des versions plus anciennes, la syntaxe d'activation de HTTP/2 peut différer. Vérifiez la documentation de la version installée avant de déployer cette directive.

### 24.2 HTTP/3

HTTP/3 utilise QUIC et UDP, plutôt qu'une connexion TCP classique pour le transport HTTP.

L'intérêt peut être notable dans certains scénarios de mobilité réseau, de pertes ou de connexions renouvelées. Le résultat doit néanmoins être mesuré.

La prise en charge dépend notamment :

- de la version de Nginx ;
- des options de compilation ;
- des bibliothèques TLS ;
- du navigateur ;
- du pare-feu ;
- de la disponibilité d'UDP sur le port concerné ;
- de l'infrastructure réseau.

Ne confondez pas l'existence d'une directive de configuration avec la disponibilité du protocole dans le binaire installé.

### 24.3 Protocole et réseau

Une configuration HTTP/3 nécessite aussi une configuration réseau appropriée. Un serveur peut écouter correctement en TCP tout en restant inaccessible par QUIC si UDP est filtré.

Avant de considérer HTTP/3 comme activé, il faut vérifier le trafic, les négociations et les réponses effectivement observées depuis les clients.

### 24.4 Ne pas activer HTTP/3 comme optimisation automatique

La bonne démarche est de comparer :

- la latence ;
- le temps jusqu'au premier octet ;
- les temps de chargement complets ;
- la fiabilité de connexion ;
- les taux d'échec ;
- la consommation CPU ;
- les résultats selon les réseaux clients.

Le protocole le plus récent n'est pas nécessairement le plus efficace pour chaque scénario.


## 25. TLS et réutilisation des connexions

### 25.1 Le coût de TLS

TLS apporte le chiffrement et des garanties de sécurité, mais la négociation peut représenter un coût de connexion.

Une mauvaise politique de réutilisation des connexions peut conduire à répéter inutilement les négociations.

Le serveur doit utiliser une configuration TLS adaptée aux exigences de sécurité et aux versions supportées.

### 25.2 Cache de sessions Nginx

Un exemple de paramètres souvent utilisés est :

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

Ils configurent un cache partagé de sessions TLS et une durée de conservation.

Les valeurs sont illustratives. La configuration exacte doit correspondre à la version, au trafic et à la politique de sécurité.

### 25.3 Ne pas sacrifier la sécurité au profit de la latence

Ne désactivez pas la vérification des certificats, n'autorisez pas des protocoles obsolètes et ne choisissez pas des suites cryptographiques faibles uniquement pour gagner quelques millisecondes.

Il faut réduire les coûts inutiles en conservant une configuration TLS sûre.

La performance doit se mesurer à l'intérieur des exigences de sécurité, pas en les remplaçant.


## 26. Rate limiting et protection contre la surcharge

### 26.1 Pourquoi limiter les requêtes ?

Lorsqu'une application approche de sa capacité maximale, une hausse soudaine du trafic peut entraîner une augmentation de latence et d'erreurs.

Un mécanisme de limitation de requêtes peut réduire la pression en contrôlant le rythme des requêtes admises.

Il ne remplace pas le dimensionnement du service ni la protection réseau. Il constitue un contrôle supplémentaire.

### 26.2 Configuration Nginx

Dans le contexte `http` :

```nginx
limit_req_zone $binary_remote_addr
    zone=api_rate_limit:10m
    rate=10r/s;
```

Dans une route :

```nginx
location /api/ {
    limit_req zone=api_rate_limit burst=20 nodelay;

    proxy_pass http://application_backend;
}
```

Cette configuration constitue un exemple, pas une limite universelle appropriée à toutes les API.

### 26.3 Comprendre les paramètres

`limit_req_zone` définit la clé, l'espace de mémoire partagé et le rythme de requêtes.

`rate=10r/s` définit un taux moyen par clé selon le mécanisme de limitation.

`burst=20` autorise un excédent temporaire au-delà du rythme de base, selon le comportement du module.

`nodelay` influence la manière dont les requêtes dans la zone de dépassement sont traitées.

### 26.4 Choisir la clé

Limiter par adresse IP peut avoir des inconvénients lorsqu'un grand nombre d'utilisateurs partagent une adresse à travers un NAT.

Une politique basée sur l'IP peut affecter plusieurs utilisateurs légitimes, tout comme un client utilisant de nombreuses adresses peut contourner certaines limites.

Le choix de la clé doit refléter le service, le modèle d'identité, le proxy de confiance et le risque de surcharge.

Ne faites pas confiance aveuglément à l'adresse issue d'un en-tête fourni par le client.

### 26.5 Limitation de connexions

Nginx peut également contrôler certaines connexions simultanées par clé au moyen du module correspondant.

Une limite de connexions ne remplace pas une limite de débit : une connexion peut servir une seule requête ou plusieurs requêtes successives, selon le protocole et le comportement du client.

Le choix des limites doit donc correspondre à la ressource que vous cherchez à protéger.


## 27. Observabilité de Nginx

### 27.1 Pourquoi les journaux doivent contenir des mesures temporelles

Un journal qui enregistre uniquement l'URL et le statut peut être insuffisant pour comprendre une dégradation.

Les temps de traitement et les informations sur le backend permettent de distinguer plusieurs scénarios :

- le proxy passe du temps avant la réponse ;
- le backend répond lentement ;
- le transfert est long ;
- une réponse est servie depuis le cache ;
- le backend échoue ;
- plusieurs tentatives ont été nécessaires.

### 27.2 Format de journal

Dans un contexte `http`, un format peut être défini ainsi :

```nginx
log_format performance
    '$remote_addr host=$host '
    '"$request" status=$status '
    'bytes=$body_bytes_sent '
    'request_time=$request_time '
    'upstream=$upstream_addr '
    'upstream_status=$upstream_status '
    'upstream_time=$upstream_response_time '
    'cache=$upstream_cache_status';
```

Puis dans le bloc `server` :

```nginx
access_log /var/log/nginx/performance.log performance;
```

Les champs indiquent notamment :

- le statut final renvoyé au client ;
- le volume transmis ;
- le temps de traitement mesuré par Nginx ;
- l'adresse du serveur upstream ;
- les statuts associés à l'upstream ;
- le temps observé au niveau upstream ;
- le statut du cache.

Selon le chemin suivi par la requête, certains champs peuvent être vides ou contenir plusieurs valeurs.

### 27.3 Utilisation

Suivre les requêtes en temps réel :

```bash
sudo tail -f /var/log/nginx/performance.log
```

Compter certains statuts ou extraire des champs demande un traitement adapté au format exact de journal.

Les journaux doivent également être soumis à une politique de rotation et de conservation, et ne pas enregistrer inutilement des données sensibles.

### 27.4 Mesures globales

Nginx dispose de fonctionnalités de statut qui peuvent exposer des métriques d'activité selon la compilation et la configuration.

Il faut restreindre les interfaces de statut à un périmètre autorisé. Une interface de diagnostic ouverte publiquement peut exposer des informations sur le serveur.


## 28. Observabilité d'Apache

### 28.1 `mod_status`

Le module Apache `mod_status` expose des informations sur l'activité du service.

Ces informations peuvent inclure :

- le nombre de workers occupés ;
- le nombre de workers inactifs ;
- les requêtes traitées ;
- certains compteurs de trafic ;
- les requêtes en cours ;
- des informations d'utilisation des ressources.

### 28.2 Activer le module

Sur Debian ou Ubuntu :

```bash
sudo a2enmod status
```

Exemple de configuration locale :

```apache
<Location "/server-status">
    SetHandler server-status
    Require local
</Location>
```

Cette configuration limite l'accès selon la règle `Require local`. Vérifiez que le site et le contexte où la directive est appliquée correspondent à l'intention.

### 28.3 Vérifier

Après validation et rechargement :

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

Depuis la machine autorisée, vous pouvez tester la ressource :

```bash
curl -i http://127.0.0.1/server-status
```

L'URL exacte dépend de l'hôte virtuel et de son port.

### 28.4 Sécurité de l'interface

Ne publiez pas l'état détaillé du serveur à tous les clients Internet.

La page peut dévoiler des informations opérationnelles utiles pour identifier les ressources sollicitées et les requêtes actives.

L'accès doit rester limité à l'équipe ou au système de supervision autorisé.


## 29. Journalisation et confidentialité

Les mesures de performance peuvent exiger des journaux détaillés, mais les journaux contiennent parfois :

- des adresses IP ;
- des chemins privés ;
- des identifiants ;
- des paramètres d'URL ;
- des informations sur l'architecture interne ;
- des détails d'erreurs.

Évitez d'enregistrer des jetons d'accès, des mots de passe ou des secrets dans les URL et les journaux.

La journalisation détaillée doit être équilibrée avec :

- le volume d'écriture ;
- le coût du stockage ;
- la protection des informations ;
- les durées de conservation ;
- la capacité de recherche ;
- la conformité aux obligations applicables.

Une instrumentation excessive peut elle-même modifier les performances mesurées.


## 30. Tests de charge : principes

### 30.1 Objectif d'un test de charge

Un test de charge cherche à comprendre le comportement d'un système lorsque le volume de requêtes ou la concurrence augmente.

Il peut être utilisé pour :

- mesurer le débit soutenable ;
- mesurer l'évolution de la latence ;
- identifier le moment où le service sature ;
- observer la consommation de ressources ;
- comparer deux configurations ;
- détecter des erreurs sous charge ;
- déterminer les limites opérationnelles.

### 30.2 Tests contrôlés

Les tests de charge doivent être effectués sur un environnement que vous contrôlez ou pour lequel vous avez une autorisation explicite.

Ne lancez pas un test agressif sur un service de tiers ou sur une infrastructure de production sans autorisation et préparation.

Un générateur de charge peut lui-même saturer sa machine ou son réseau, ce qui rend les résultats trompeurs.

### 30.3 Définir un scénario

Un scénario de test doit spécifier :

- les routes testées ;
- la proportion de chaque type de requête ;
- la taille des réponses ;
- la durée du test ;
- le nombre de connexions ;
- les niveaux de concurrence ;
- les conditions de cache ;
- les résultats attendus ;
- les seuils d'erreur ;
- les ressources surveillées.

Il ne suffit pas d'envoyer des milliers de requêtes à une seule URL et de considérer le résultat comme représentatif de tout le site.

### 30.4 Éviter les tests trop courts

Un test extrêmement court peut surtout mesurer le démarrage des processus, le remplissage du cache ou les variations initiales.

Pour comparer des configurations, il faut prévoir :

1. une phase de démarrage ;
2. une phase de montée en charge ;
3. une phase de stabilisation ;
4. une période de mesure ;
5. une phase de retour à une charge faible.

La durée dépend du système et du comportement recherché.


## 31. Utiliser wrk pour mesurer la charge

`wrk` est un outil de génération de trafic HTTP qui permet de maintenir plusieurs connexions et de mesurer les réponses.

### 31.1 Exemple

Sur un serveur de laboratoire autorisé :

```bash
wrk -t4 -c100 -d30s --latency http://127.0.0.1:8080/
```

Les options indiquent notamment :

- `-t4` : quatre threads de génération ;
- `-c100` : cent connexions maintenues ;
- `-d30s` : durée de trente secondes ;
- `--latency` : affichage des informations de latence.

Le nombre de threads du générateur n'est pas le nombre de workers du serveur. Les deux ont des rôles distincts.

### 31.2 Comparaison avec différents niveaux de concurrence

Exemples de commandes :

```bash
wrk -t2 -c20 -d30s --latency http://127.0.0.1:8080/
```

```bash
wrk -t4 -c100 -d30s --latency http://127.0.0.1:8080/
```

```bash
wrk -t4 -c200 -d30s --latency http://127.0.0.1:8080/
```

Ces commandes doivent être exécutées dans un environnement où le générateur ne perturbe pas le serveur ni les autres services.

### 31.3 Interpréter les résultats

Examinez :

- le nombre de requêtes par seconde ;
- la distribution de la latence ;
- la quantité de données transférées ;
- les erreurs ;
- la progression du débit avec la concurrence.

Si le débit augmente puis se stabilise tandis que la latence s'accroît fortement, le système peut atteindre une limite de capacité.

Il faut ensuite examiner le CPU, la mémoire, les files d'attente, les temps upstream et les dépendances avant de conclure.

### 31.4 Attention aux résultats artificiels

Si le test vise une page statique en boucle sur `localhost`, il peut mesurer presque exclusivement les performances du serveur local, du cache et de la pile réseau locale.

Cela ne représente pas nécessairement l'expérience d'un utilisateur distant, ni les performances d'une application dynamique.

Pour une analyse réaliste, utilisez un générateur suffisamment puissant, un chemin réseau approprié et un scénario correspondant au trafic réel.


## 32. Tester les différents scénarios

Un benchmark utile ne teste pas uniquement un type de contenu.

Il faut étudier plusieurs classes de requêtes.

| Scénario | Ce qu'il permet d'observer |
|---|---|
| Petit fichier statique | Coût minimal de traitement et de connexion |
| Gros fichier statique | Débit et coût de transfert |
| Contenu compressible | Gains de compression et coût CPU |
| Réponse dynamique rapide | Coût du proxy et du traitement normal |
| Réponse dynamique lente | Saturation, attente et concurrence |
| Cache froid | Coût de la génération ou de la récupération initiale |
| Cache chaud | Coût de service d'une réponse réutilisée |
| Backend indisponible | Délais, erreurs et comportement de reprise |
| Connexions persistantes | Effet de la réutilisation de connexions |
| HTTPS | Coût de la connexion sécurisée et du transfert |

Le résultat d'un scénario ne doit pas être généralisé à tous les autres.


## 33. Comparer avant et après une optimisation

Supposons que vous modifiez la configuration pour activer le cache d'un contenu public.

Un rapport de comparaison devrait contenir :

| Indicateur | Avant | Après |
|---|---:|---:|
| Débit | Mesure initiale | Nouvelle mesure |
| p50 | Mesure initiale | Nouvelle mesure |
| p95 | Mesure initiale | Nouvelle mesure |
| p99 | Mesure initiale | Nouvelle mesure |
| Taux d'erreur | Mesure initiale | Nouvelle mesure |
| CPU | Mesure initiale | Nouvelle mesure |
| Mémoire | Mesure initiale | Nouvelle mesure |
| Temps upstream | Mesure initiale | Nouvelle mesure |
| Taux de cache HIT | Mesure initiale | Nouvelle mesure |

Ne remplissez pas ce tableau avec des valeurs estimées. Utilisez des mesures réellement obtenues.

### 33.1 Une seule variable à la fois

Si vous modifiez en même temps le cache, la compression, le nombre de workers et les délais, il devient difficile d'identifier la cause d'une amélioration.

La méthode recommandée est :

1. établir la référence ;
2. changer un paramètre ou un groupe de paramètres liés ;
3. retester avec le même scénario ;
4. comparer les résultats ;
5. garder ou annuler le changement ;
6. documenter la décision.

### 33.2 Prévoir un retour arrière

Toute optimisation de production doit avoir une procédure de retour arrière.

Il faut conserver la configuration précédente, valider la nouvelle syntaxe et savoir comment revenir à un état connu.

Les modifications doivent être déployées progressivement lorsque le contexte le permet.


## 34. Dimensionnement de la mémoire

Le dimensionnement mémoire est un compromis entre la concurrence, les buffers, le cache, les applications et les autres services du système.

### 34.1 Budget mémoire

Un serveur utilise de la mémoire pour :

- le noyau ;
- les processus Nginx ou Apache ;
- les applications ;
- les buffers ;
- les caches de fichiers ;
- les caches applicatifs ;
- les bibliothèques et structures de données ;
- les outils de supervision ;
- les autres services.

Il faut conserver une marge pour les pointes et le fonctionnement normal du système.

### 34.2 Calcul indicatif

Si une famille de processus consomme en moyenne 40 Mio par instance active et que 50 instances sont réellement simultanées, la mémoire brute correspondante est de l'ordre de :

\[
40 \times 50 = 2000\ \text{Mio}
\]

Ce calcul ne tient pas compte du partage de mémoire entre processus, des caches, des pics de consommation, des autres services ou du comportement de l'allocateur.

Il sert à former une hypothèse de capacité, pas à déterminer directement une limite de workers.

### 34.3 Ne pas surdimensionner sans preuve

Un serveur contenant beaucoup de mémoire ne doit pas nécessairement être configuré pour ouvrir un très grand nombre de connexions.

La capacité doit être déterminée à partir de la demande réelle, de la consommation observée et des objectifs de latence.

Une concurrence excessive peut provoquer des files d'attente plus longues, davantage de contention et une pression plus importante sur les dépendances.


## 35. Dimensionnement du CPU

### 35.1 Tous les workers n'utilisent pas continuellement le processeur

Nginx peut traiter de nombreuses connexions qui attendent du réseau ou des données.

Une application qui réalise des calculs intensifs aura un profil différent d'une application qui attend principalement une base de données ou un service externe.

Le nombre de processus ou de threads optimal dépend donc du type de travail.

### 35.2 Identifier un goulot CPU

Observe :

- l'utilisation CPU globale et par processus ;
- le temps de réponse ;
- la progression du débit lorsque la concurrence augmente ;
- le comportement des workers applicatifs ;
- les coûts de compression ;
- les coûts de chiffrement ;
- les tâches en arrière-plan.

Si le CPU reste proche de sa capacité et que le débit ne progresse plus, il faut identifier quelles opérations consomment le temps processeur.

### 35.3 Affinité CPU

L'affinité CPU permet de lier des processus à certains cœurs.

Cette optimisation peut être utile dans des environnements spécifiques, mais elle ne doit pas être appliquée aveuglément. Elle peut aussi empêcher un processus d'utiliser des cœurs qui seraient autrement disponibles.

Le choix doit se baser sur des mesures de planification, de cache CPU et de comportement de la charge.


## 36. Files d'attente et surcharge

Un serveur Web peut recevoir des requêtes plus vite qu'il ne peut les traiter.

```text
Requêtes entrantes
        |
        v
+-------------------+
| File d'attente    |
+-------------------+
        |
        v
Workers disponibles
        |
        v
Traitement
```

Si la file d'attente se remplit, les requêtes attendent plus longtemps. Certaines peuvent finir par dépasser leur délai d'attente et échouer.

Augmenter la taille de la file n'augmente pas nécessairement la capacité de traitement. Cela peut simplement augmenter le temps passé en attente.

### 36.1 Contrôle de la concurrence

Une stratégie de performance doit déterminer :

- quand accepter des requêtes supplémentaires ;
- quand limiter le débit ;
- quand refuser rapidement une surcharge ;
- comment protéger les dépendances ;
- comment préserver la latence des requêtes prioritaires.

Une erreur rapide et contrôlée peut être préférable à un système qui accepte toutes les demandes puis s'effondre sous la charge.


## 37. HTTP keep-alive : trouver un compromis

Les connexions persistantes permettent de réutiliser des connexions existantes.

Mais elles doivent être dimensionnées en fonction des clients, des backends et des limites de connexion.

Une politique de keep-alive doit examiner :

- la durée d'inactivité acceptée ;
- le nombre de requêtes par connexion ;
- la capacité des backends ;
- le nombre de connexions clientes ;
- les délais réseau ;
- les comportements de reprise ;
- la consommation de descripteurs.

Un keep-alive très long ne réduit pas nécessairement la latence globale si les connexions inactives utilisent des ressources dont le service a besoin.

Inversement, une valeur très courte peut multiplier les connexions et les négociations TLS.

Les paramètres doivent être observés dans le scénario de trafic réel.


## 38. CDN et distribution géographique

Un CDN peut réduire la latence ressentie lorsque les ressources peuvent être servies depuis des points de présence plus proches du client.

Il peut également réduire le trafic arrivant directement sur l'origine, lorsque les réponses sont cacheables.

```text
                    CLIENTS
                       |
          +------------+------------+
          |                         |
          v                         v
      Edge CDN 1                Edge CDN 2
          |                         |
          +------------+------------+
                       |
                       v
                Serveur d'origine
```

Un CDN ne remplace pas le besoin de rendre l'origine performante.

Si le contenu n'est pas cacheable, si chaque requête doit atteindre l'origine ou si la logique applicative est coûteuse, le gain peut être plus limité.

Il faut aussi contrôler les en-têtes de cache, les règles de purge, la sécurité de l'origine et les mécanismes de contournement autorisés.


## 39. Éviter les optimisations contre-productives

### 39.1 Augmenter toutes les limites

Augmenter les workers, les connexions, les buffers et les délais ne constitue pas une stratégie.

Chaque augmentation peut consommer davantage de mémoire, garder des requêtes actives plus longtemps ou transférer la pression vers les backends.

### 39.2 Désactiver la journalisation sans mesure

La journalisation a un coût, mais elle constitue aussi une source essentielle d'observabilité.

Avant de réduire les journaux, mesurez leur effet et évaluez si une configuration moins coûteuse permet de conserver les informations nécessaires.

### 39.3 Supprimer tous les caches pour « éviter les données périmées »

Un cache bien conçu réduit le travail, mais doit gérer correctement la fraîcheur.

Le supprimer entièrement peut réintroduire une forte charge sur l'application et la base de données.

La bonne réponse consiste à définir la politique de cache et d'invalidation appropriée aux données.

### 39.4 Activer la compression partout

La compression peut améliorer le réseau, mais augmenter le coût CPU et exposer certains scénarios spécifiques de sécurité.

Il faut choisir les types de contenu et les routes concernées.

### 39.5 Augmenter les délais de réponse

Un délai plus long peut empêcher une erreur prématurée, mais il peut également maintenir des requêtes bloquées et accroître la concurrence.

Un délai doit correspondre aux exigences métier et aux temps de traitement observés.

### 39.6 Copier des paramètres issus d'une autre machine

Les paramètres publiés pour un serveur à très grand trafic ne sont pas nécessairement adaptés à une petite VM ou à un conteneur.

Les différences de CPU, de mémoire, de versions, de modules et de type de charge rendent les comparaisons directes trompeuses.


## 40. Sécurité et performance

La performance doit être évaluée dans un cadre de sécurité cohérent.

### 40.1 Limiter l'exposition des services

Les backends qui doivent être accessibles uniquement par le reverse proxy devraient être protégés par des règles réseau et des adresses d'écoute adaptées.

Une application directement accessible peut permettre de contourner certaines règles du point d'entrée.

### 40.2 Protéger les ressources administratives

Les interfaces de statut, les panneaux d'administration et les diagnostics détaillés doivent être accessibles uniquement aux personnes ou systèmes autorisés.

Ils peuvent révéler des requêtes, des noms de serveurs ou des informations d'utilisation des ressources.

### 40.3 Validation de cache

Une réponse personnalisée ne doit pas être mise en cache comme si elle était publique.

Il faut vérifier :

- l'authentification ;
- les cookies ;
- les en-têtes `Cache-Control` ;
- les clés de cache ;
- la variation des réponses ;
- les éventuels en-têtes `Set-Cookie`.

Un cache qui sert rapidement une donnée privée au mauvais utilisateur reste une défaillance majeure.

### 40.4 Compression et secrets

Évaluez attentivement la compression des réponses TLS qui combinent des secrets et des données influencées par un attaquant.

Le gain de transfert ne doit pas être obtenu en ignorant le modèle de menace.

### 40.5 Limitation de charge

Les mécanismes de limitation peuvent protéger les ressources contre certaines pointes de trafic, mais ils peuvent aussi bloquer des utilisateurs légitimes.

Les limites doivent être testées, surveillées et adaptées à la route concernée.


## 41. Procédure complète de diagnostic d'une dégradation

Lorsqu'une application Web devient lente, suivez un ordre stable.

### Étape 1 — Reproduire le problème

Utilisez une requête contrôlée :

```bash
curl -sS -o /dev/null \
  -w 'ttfb=%{time_starttransfer}s total=%{time_total}s code=%{http_code}\n' \
  http://127.0.0.1:8080/
```

Comparez avec le comportement attendu.

### Étape 2 — Vérifier le service

```bash
sudo systemctl status nginx
```

ou :

```bash
sudo systemctl status apache2
```

### Étape 3 — Contrôler l'écoute réseau

```bash
sudo ss -lntp
```

### Étape 4 — Examiner les ressources

```bash
top
free -h
vmstat 1
```

### Étape 5 — Examiner le chemin applicatif

Comparez le temps de réponse du proxy et celui du backend testé directement.

Si le backend est lent lui aussi, le problème n'est probablement pas limité au reverse proxy.

### Étape 6 — Examiner les journaux

Pour Nginx :

```bash
sudo tail -n 100 /var/log/nginx/error.log
```

Pour Apache sous Debian ou Ubuntu :

```bash
sudo tail -n 100 /var/log/apache2/error.log
```

### Étape 7 — Examiner le cache

Vérifiez les statuts de cache, les en-têtes HTTP et le temps passé dans l'upstream.

Un cache qui génère beaucoup de `MISS` peut indiquer un problème de clé, de fraîcheur, de politique HTTP ou de diversité du trafic.

### Étape 8 — Tester à plusieurs niveaux de concurrence

Exécutez des tests graduels dans un environnement contrôlé. Observez à quel moment la latence augmente et le débit cesse de progresser.

### Étape 9 — Formuler une hypothèse

Exemple :

> Les réponses sont rapides en charge faible, mais p99 augmente sous concurrence. CPU reste peu sollicité et les temps upstream sont élevés. L'application ou une dépendance semble limiter le débit.

### Étape 10 — Modifier et valider

Ne modifiez que les paramètres pertinents. Reproduisez le même scénario, comparez les métriques et restaurez la configuration si l'amélioration n'est pas démontrée.


## 42. Travaux pratiques guidés

Les exercices suivants utilisent une infrastructure locale.

Les serveurs Python utilisés pour simuler des backends sont des outils de laboratoire, pas des serveurs de production.

### TP 1 — Mesurer une référence HTTP

**Objectif :** établir une mesure de base avant toute optimisation.

Testez une URL locale existante :

```bash
curl -sS -o /dev/null \
  -w 'code=%{http_code} dns=%{time_namelookup}s connect=%{time_connect}s ttfb=%{time_starttransfer}s total=%{time_total}s bytes=%{size_download}\n' \
  http://127.0.0.1:8080/
```

Répétez dix fois.

Notez les temps et identifiez :

- la variation entre les requêtes ;
- les codes HTTP ;
- la taille de la réponse ;
- la différence éventuelle entre premier accès et accès répétés.

Ne modifiez pas encore le serveur.

### TP 2 — Installer et lancer les backends de test

Préparez deux répertoires :

```bash
mkdir -p /tmp/web-perf/backend1
mkdir -p /tmp/web-perf/backend2
```

Créez deux fichiers :

```bash
printf '<h1>Backend 1</h1>\n' > /tmp/web-perf/backend1/index.html
printf '<h1>Backend 2</h1>\n' > /tmp/web-perf/backend2/index.html
```

Démarrez le premier serveur :

```bash
nohup python3 -m http.server 8001 \
  --bind 127.0.0.1 \
  --directory /tmp/web-perf/backend1 \
  > /tmp/web-perf/backend1.log 2>&1 &

echo $! > /tmp/web-perf/backend1.pid
```

Démarrez le second :

```bash
nohup python3 -m http.server 8002 \
  --bind 127.0.0.1 \
  --directory /tmp/web-perf/backend2 \
  > /tmp/web-perf/backend2.log 2>&1 &

echo $! > /tmp/web-perf/backend2.pid
```

Testez les deux applications :

```bash
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8002/
```

### TP 3 — Mesurer le temps direct des backends

Testez le premier :

```bash
for i in $(seq 1 10); do
    curl -sS -o /dev/null \
      -w 'backend1 ttfb=%{time_starttransfer}s total=%{time_total}s\n' \
      http://127.0.0.1:8001/
done
```

Testez le second de la même manière.

Ces mesures constituent une référence simplifiée. Les résultats restent dépendants de la machine, du cache, du système et de l'outil de test.

### TP 4 — Configurer Nginx comme proxy

Créez une configuration de laboratoire adaptée à l'installation :

```nginx
upstream web_perf_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;

    keepalive 16;
}

server {
    listen 127.0.0.1:8080;
    server_name web-perf.test;

    access_log /var/log/nginx/web-perf-access.log;
    error_log /var/log/nginx/web-perf-error.log;

    location / {
        proxy_pass http://web_perf_backend;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 3s;
        proxy_send_timeout 15s;
        proxy_read_timeout 15s;
    }
}
```

Vérifiez la syntaxe :

```bash
sudo nginx -t
```

Puis rechargez :

```bash
sudo systemctl reload nginx
```

Si une configuration précédente utilise déjà le port 8080, examinez-la avant d'activer ce serveur. Il ne faut pas créer des conflits d'écoute.

### TP 5 — Comparer l'accès direct et l'accès au proxy

Mesurez les backends directs puis le proxy :

```bash
for i in $(seq 1 10); do
    curl -sS -o /dev/null \
      -w 'proxy ttfb=%{time_starttransfer}s total=%{time_total}s code=%{http_code}\n' \
      http://127.0.0.1:8080/
done
```

Comparez les temps. Pour de petites pages et des applications locales, l'overhead peut être très faible et difficile à distinguer des variations de mesure.

Ne concluez pas à un gain significatif à partir de quelques microsecondes sur une seule exécution.

### TP 6 — Tester une charge graduelle

Si `wrk` est installé et si vous contrôlez l'environnement :

```bash
wrk -t2 -c20 -d30s --latency http://127.0.0.1:8080/
```

Puis :

```bash
wrk -t4 -c100 -d30s --latency http://127.0.0.1:8080/
```

Observez les résultats et surveillez simultanément les ressources :

```bash
top
```

```bash
free -h
```

```bash
sudo tail -f /var/log/nginx/web-perf-error.log
```

Le but est d'apprendre à corréler le débit, la latence, la concurrence et les ressources système.

### TP 7 — Ajouter la journalisation des temps upstream

Ajoutez un format de journal contenant :

```nginx
log_format perf_upstream
    '$remote_addr "$request" status=$status '
    'request_time=$request_time '
    'upstream=$upstream_addr '
    'upstream_status=$upstream_status '
    'upstream_time=$upstream_response_time';
```

Dans le bloc `server` :

```nginx
access_log /var/log/nginx/perf-upstream.log perf_upstream;
```

Testez la syntaxe avant le rechargement :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Envoyez plusieurs requêtes, puis lisez le journal :

```bash
sudo tail -n 50 /var/log/nginx/perf-upstream.log
```

Expliquez quelle part du temps est associée au traitement global côté proxy et quelles informations sont disponibles sur le serveur upstream.

### TP 8 — Activer gzip

Ajoutez la configuration gzip appropriée dans le contexte `http` :

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 4;

gzip_types
    text/plain
    text/css
    application/json
    application/javascript
    application/xml
    image/svg+xml;
```

Testez la configuration :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Vérifiez la réponse avec `curl`.

Pour mesurer un gain de compression, créez ou utilisez une ressource textuelle suffisamment grande. Les deux pages HTML très courtes des backends ne permettent pas nécessairement d'observer un gain significatif.

Comparez la taille du transfert, le CPU utilisé et le temps de réponse.

### TP 9 — Simuler une panne

Arrêtez l'un des backends de test :

```bash
kill "$(cat /tmp/web-perf/backend1.pid)"
```

Envoyez plusieurs requêtes au proxy :

```bash
for i in $(seq 1 10); do
    curl -sS --max-time 5 http://127.0.0.1:8080/
    echo
done
```

Observez les erreurs, les journaux et la réponse de l'autre backend.

Le laboratoire n'a pas vocation à démontrer une haute disponibilité complète, mais à montrer que les erreurs de backend ont un effet sur le comportement de l'infrastructure.

### TP 10 — Nettoyer l'environnement

Arrêtez les processus de test :

```bash
kill "$(cat /tmp/web-perf/backend1.pid)" 2>/dev/null || true
kill "$(cat /tmp/web-perf/backend2.pid)" 2>/dev/null || true
```

Désactivez ou supprimez la configuration de laboratoire selon vos besoins, sans toucher aux autres sites.

Vérifiez toujours la syntaxe avant le rechargement :

```bash
sudo nginx -t
sudo systemctl reload nginx
```


## 43. Étude de cas : une application qui ralentit sous charge

### Situation

Une application présente les symptômes suivants :

- les requêtes sont rapides sous faible charge ;
- la latence p95 augmente quand la concurrence progresse ;
- le CPU du reverse proxy reste relativement bas ;
- les temps upstream augmentent ;
- les journaux montrent des réponses lentes du backend.

### Analyse

Ces observations suggèrent que le reverse proxy n'est peut-être pas le principal goulot d'étranglement.

L'application peut être limitée par :

- le nombre de workers applicatifs ;
- un pool de connexions à la base saturé ;
- des requêtes SQL coûteuses ;
- des dépendances externes ;
- de la contention sur un verrou ;
- des opérations bloquantes.

### Plan de diagnostic

1. Mesurer séparément les temps directs et les temps proxy.
2. Examiner les temps upstream dans les journaux.
3. Contrôler les métriques de l'application.
4. Examiner les pools de connexions à la base.
5. Identifier les routes les plus lentes.
6. Corréler les temps de réponse et les dépendances.
7. Tester une seule modification, puis comparer les distributions.

L'augmentation des workers Nginx ne résoudra pas automatiquement cette situation. Si l'application est saturée, une concurrence supplémentaire peut même accentuer la pression sur la base de données.


## 44. Étude de cas : servir des ressources statiques à grande échelle

### Situation

Un site publie de nombreux fichiers JavaScript, CSS, icônes et polices.

Les fichiers changent principalement lors des déploiements et portent un hash dans leur nom.

### Stratégie

Une stratégie cohérente peut combiner :

1. la publication statique efficace avec Nginx ;
2. des en-têtes de cache navigateur ;
3. des noms de fichiers versionnés ;
4. la compression pour les ressources textuelles appropriées ;
5. une distribution CDN lorsque la géographie ou le trafic le justifie ;
6. la surveillance du débit et des erreurs.

### Pourquoi cette approche est utile

Les fichiers versionnés peuvent être considérés comme immuables pour une durée définie. Le navigateur ou le CDN peut les conserver sans devoir les redemander à chaque navigation.

La réponse HTML qui référence ces fichiers doit, elle, être gérée avec une politique de fraîcheur adaptée aux mises à jour du site.

### Points de contrôle

- Les chemins versionnés changent-ils à chaque publication pertinente ?
- La politique `Cache-Control` correspond-elle à cette propriété ?
- Les fichiers compressés sont-ils effectivement plus petits ?
- Les types MIME sont-ils corrects ?
- Les ressources absentes ne reçoivent-elles pas des en-têtes de cache trop longs ?
- La purge ou le renouvellement du contenu est-il compris ?


## 45. Étude de cas : cache reverse proxy pour une route publique

### Situation

Une route renvoie un catalogue public qui change toutes les dix minutes.

La réponse est identique pour tous les visiteurs et ne dépend ni de l'utilisateur ni de son authentification.

### Stratégie possible

Un cache partagé peut être utile si :

- la réponse est réellement publique ;
- sa durée de fraîcheur est définie ;
- son contenu ne dépend pas d'un cookie de session ;
- la clé identifie correctement la ressource ;
- les réponses privées ne sont pas mélangées ;
- l'application tolère le délai de mise à jour.

### Points de contrôle

Le responsable doit vérifier :

1. le nombre de requêtes servies depuis le cache ;
2. le nombre de requêtes transmises au backend ;
3. la fraîcheur des données ;
4. le comportement lors d'une erreur d'application ;
5. la cohérence entre les réponses servies et le contenu attendu ;
6. l'effet sur la mémoire, le stockage et le backend.

Un cache est utile seulement si son comportement est correct pour le contenu concerné.


## 46. Projet final : construire un plan d'optimisation Web

### Objectif

Établir un plan d'optimisation complet, mesuré et reproductible pour une application publiée derrière Nginx ou Apache.

### Cahier des charges

Le projet doit traiter les aspects suivants :

- définition du service et des routes importantes ;
- établissement d'une référence de performance ;
- collecte des latences p50, p95 et p99 ;
- mesure du débit et du taux d'erreur ;
- contrôle des ressources système ;
- mesure des temps upstream ;
- analyse des réponses cacheables ;
- définition des ressources pouvant utiliser le cache navigateur ;
- évaluation de la compression ;
- analyse des connexions persistantes ;
- dimensionnement prudent des workers ;
- test de charge à plusieurs niveaux de concurrence ;
- comparaison avant et après ;
- procédure de validation ;
- plan de retour arrière.

### Étape A — Définir les objectifs

Exemple de tableau à compléter :

| Indicateur | Valeur de départ | Objectif |
|---|---:|---:|
| Débit | À mesurer | À définir |
| Latence p50 | À mesurer | À définir |
| Latence p95 | À mesurer | À définir |
| Latence p99 | À mesurer | À définir |
| Taux d'erreur | À mesurer | À définir |
| CPU | À mesurer | À définir |
| Mémoire | À mesurer | À définir |

Les objectifs doivent correspondre aux besoins de l'application et aux moyens disponibles.

### Étape B — Collecter la référence

Reproduisez un scénario représentatif avec les mêmes routes, la même concurrence et les mêmes conditions de cache.

Conservez les commandes, les versions et les résultats.

### Étape C — Identifier le principal goulot

Déterminez si le système est principalement limité par :

- CPU ;
- mémoire ;
- réseau ;
- stockage ;
- concurrence ;
- cache ;
- application ;
- base de données.

### Étape D — Formuler une hypothèse

Exemple :

> Les ressources publiques sont redemandées fréquemment au backend. Une politique de cache navigateur adaptée devrait diminuer le nombre de requêtes répétées vers l'origine.

### Étape E — Réaliser une seule amélioration

Modifiez uniquement les paramètres nécessaires à l'hypothèse.

Testez la syntaxe avant application.

### Étape F — Refaire les mesures

Reproduisez le même scénario de charge et comparez les métriques.

Ne considérez pas un gain comme démontré si les conditions de test ont changé ou si les résultats sont trop variables.

### Étape G — Décider

Trois résultats sont possibles :

- la modification améliore les indicateurs et respecte les contraintes de sécurité ;
- elle n'apporte pas d'amélioration notable ;
- elle dégrade un ou plusieurs indicateurs.

Dans les deux derniers cas, restaurez ou ajustez la configuration et formulez une nouvelle hypothèse.

### Critères de réussite

Le projet est réussi lorsque vous pouvez expliquer :

- quel était le principal goulot d'étranglement ;
- quelles mesures ont permis de l'identifier ;
- quelle modification a été testée ;
- quel changement a été observé ;
- quels risques restent présents ;
- comment revenir à la configuration précédente ;
- quelles mesures doivent rester surveillées en production.


## 47. Erreurs d'ingénierie fréquentes

### 47.1 Chercher uniquement à maximiser les requêtes par seconde

Un débit élevé obtenu avec une latence excessive ou un taux d'erreur important n'est pas nécessairement un résultat acceptable.

Il faut mesurer la latence, les erreurs et la consommation des ressources simultanément.

### 47.2 Tester uniquement sur localhost

Les tests locaux ne reflètent pas toujours les contraintes réseau, les latences géographiques, les pare-feu ou les comportements des clients distants.

### 47.3 Utiliser un générateur trop faible

Un générateur qui manque de CPU ou de ports éphémères peut limiter le débit du test. Le résultat mesurerait alors la capacité du générateur plutôt que celle du serveur.

### 47.4 Comparer deux tests aux conditions différentes

Si le cache est chaud lors d'un essai et vide lors de l'autre, les résultats ne sont pas directement comparables.

Il faut documenter les conditions et reproduire le même protocole de mesure.

### 47.5 Augmenter `MaxRequestWorkers` sans calcul

La concurrence supplémentaire consomme des ressources et peut provoquer un afflux plus important vers une base de données déjà saturée.

### 47.6 Mettre toutes les réponses en cache

Une réponse privée ou personnalisée peut être exposée si la politique de cache ne prend pas en compte l'identité et les conditions de la requête.

### 47.7 Réduire tous les délais

Des délais très courts peuvent augmenter le nombre d'erreurs. Des délais très longs peuvent garder des requêtes bloquées plus longtemps.

### 47.8 Activer toutes les fonctionnalités modernes

HTTP/2, HTTP/3, la compression, les caches et les pools de connexions doivent être sélectionnés et mesurés selon le scénario. Leur présence ne garantit pas une meilleure performance dans toutes les configurations.

### 47.9 Négliger la base de données

Si les requêtes SQL représentent le principal coût de traitement, le serveur Web ne peut pas corriger le problème à lui seul.

### 47.10 Oublier le retour arrière

Une optimisation qui ne peut pas être annulée rapidement augmente le risque opérationnel. La configuration et les procédures de déploiement doivent être préparées avant une modification importante.


## 48. Checklist d'exploitation haute performance

### Mesure

- [ ] Une référence de performance existe.
- [ ] Le débit est mesuré avec un scénario défini.
- [ ] Les latences p50, p95 et p99 sont observées.
- [ ] Le taux d'erreur est surveillé.
- [ ] Les conditions de cache sont connues.
- [ ] Les mesures sont répétables.

### Nginx

- [ ] `worker_processes` est cohérent avec l'environnement.
- [ ] `worker_connections` est dimensionné sans dépasser les ressources réelles.
- [ ] Les limites de descripteurs ont été vérifiées.
- [ ] Le comportement des connexions persistantes est mesuré.
- [ ] Le buffering correspond au type de réponse.
- [ ] Les pools upstream ne conservent pas inutilement des ressources.
- [ ] Les journaux exposent les métriques utiles.

### Apache

- [ ] Le MPM actif est connu.
- [ ] Les modules chargés sont compatibles avec le MPM.
- [ ] `MaxRequestWorkers` correspond à la capacité mémoire et à la charge.
- [ ] `ThreadsPerChild` et les limites associées sont cohérents.
- [ ] Le comportement keep-alive est mesuré.
- [ ] `mod_status` est limité aux accès autorisés.
- [ ] Les changements ont passé `apachectl configtest`.

### Cache et compression

- [ ] Seules les ressources appropriées sont cacheables.
- [ ] Les contenus personnalisés sont protégés.
- [ ] Les en-têtes de fraîcheur sont corrects.
- [ ] La politique d'invalidation est documentée.
- [ ] La compression vise les types de contenu appropriés.
- [ ] Le coût CPU de la compression est surveillé.

### Tests et exploitation

- [ ] Les tests sont effectués sur une cible autorisée.
- [ ] La machine génératrice ne limite pas le benchmark.
- [ ] Les résultats sont comparés dans des conditions équivalentes.
- [ ] Les modifications sont documentées.
- [ ] Une procédure de retour arrière existe.
- [ ] La supervision reste active après le déploiement.


## 49. Fiche de révision rapide

### Mesures HTTP

```bash
curl -sS -o /dev/null \
  -w 'ttfb=%{time_starttransfer}s total=%{time_total}s code=%{http_code}\n' \
  http://127.0.0.1:8080/
```

### Diagnostic système

```bash
top
free -h
vmstat 1
ss -s
sudo ss -lntp
```

### Limites Nginx

```bash
ulimit -n
systemctl show nginx -p LimitNOFILE
```

### Test de charge

```bash
wrk -t4 -c100 -d30s --latency http://127.0.0.1:8080/
```

### Test de configuration Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Test de configuration Apache

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

### Concepts Nginx importants

| Directive | Rôle |
|---|---|
| `worker_processes` | Nombre de workers |
| `worker_connections` | Limite de connexions par worker |
| `sendfile` | Optimisation de certains transferts de fichiers |
| `keepalive_timeout` | Gestion de l'inactivité des connexions clientes |
| `keepalive` dans `upstream` | Cache de connexions upstream inactives |
| `proxy_buffering` | Contrôle du buffering des réponses proxy |
| `proxy_cache_path` | Définition d'un espace de cache |
| `proxy_cache_valid` | Durées de cache configurées selon les statuts |
| `gzip` | Compression des réponses prises en charge |
| `limit_req_zone` | Définition d'une zone de limitation de débit |

### Concepts Apache importants

| Directive ou module | Rôle |
|---|---|
| `mpm_event` | Modèle multithreadé avec gestion spécifique des connexions |
| `ThreadsPerChild` | Nombre de threads par processus enfant |
| `MaxRequestWorkers` | Limite de requêtes simultanées |
| `MaxConnectionsPerChild` | Recyclage des processus après un nombre défini de connexions |
| `mod_deflate` | Compression de réponses |
| `mod_cache` | Fonctionnalités de cache |
| `mod_cache_disk` | Stockage du cache sur disque |
| `mod_status` | Informations d'activité du serveur |


## 50. Glossaire

**Bande passante** : capacité de transfert des données d'un lien réseau.

**Buffering** : stockage temporaire de données pendant leur réception, leur traitement ou leur transmission.

**Cache** : mécanisme qui conserve des données ou des réponses pour éviter de les recalculer ou de les récupérer à chaque demande.

**Cache HIT** : réponse servie à partir d'un cache.

**Cache MISS** : absence de réponse cacheable correspondante lors de la consultation du cache.

**Cache-Control** : en-tête HTTP qui contribue à définir la politique de mise en cache d'une réponse.

**CDN** : réseau de distribution de contenu qui peut servir des ressources depuis des points de présence répartis.

**Concurrence** : nombre d'opérations ou de requêtes simultanément en cours.

**Débit** : volume de travail effectué par unité de temps, par exemple en requêtes par seconde.

**Descripteur de fichier** : identifiant utilisé par un processus pour manipuler un fichier, une socket ou une autre ressource de type fichier.

**Goulot d'étranglement** : ressource ou opération qui limite la capacité globale d'un système.

**HTTP/2** : version du protocole HTTP qui permet notamment le multiplexage de flux sur une connexion.

**HTTP/3** : version de HTTP utilisant QUIC pour son transport.

**Latence** : durée observée entre un point de départ et un résultat ou un événement mesuré.

**Loi de Little** : relation entre le nombre moyen d'éléments dans un système, le débit moyen et le temps moyen passé dans ce système.

**MPM** : module Apache qui définit une partie du modèle de processus et de threads.

**p95** : percentile de latence en dessous duquel se situent 95 % des observations.

**p99** : percentile de latence en dessous duquel se situent 99 % des observations.

**Reverse proxy** : serveur intermédiaire qui reçoit les requêtes des clients et les transmet à des services en amont.

**RSS** : taille de la mémoire résidente d'un processus, correspondant aux pages actuellement présentes en mémoire physique selon la mesure du système.

**TLS** : protocole permettant notamment le chiffrement et l'intégrité des communications.

**TTFB** : temps jusqu'au premier octet de réponse mesuré par le client.

**Upstream** : serveur ou groupe de serveurs vers lequel le proxy transmet les requêtes.

**Worker** : processus ou thread qui participe au traitement des connexions et requêtes, selon l'architecture du serveur.


## 51. Documentation officielle

Les directives, valeurs par défaut et fonctionnalités dépendent de la version installée, de la compilation, des modules chargés et de la distribution. Consultez la documentation de votre version avant de déployer une modification.

### Nginx

- Documentation générale :  
  https://nginx.org/en/docs/

- Paramètres du cœur et processus :  
  https://nginx.org/en/docs/ngx_core_module.html

- Module de proxy HTTP :  
  https://nginx.org/en/docs/http/ngx_http_proxy_module.html

- Module upstream et répartition de charge :  
  https://nginx.org/en/docs/http/ngx_http_upstream_module.html

- Compression gzip :  
  https://nginx.org/en/docs/http/ngx_http_gzip_module.html

- En-têtes et cache navigateur :  
  https://nginx.org/en/docs/http/ngx_http_headers_module.html

- Module HTTP/2 :  
  https://nginx.org/en/docs/http/ngx_http_v2_module.html

- Module HTTP/3 :  
  https://nginx.org/en/docs/http/ngx_http_v3_module.html

### Apache HTTP Server

- Documentation Apache 2.4 :  
  https://httpd.apache.org/docs/2.4/

- MPM commun et dimensionnement des workers :  
  https://httpd.apache.org/docs/2.4/mod/mpm_common.html

- MPM worker :  
  https://httpd.apache.org/docs/2.4/mod/worker.html

- MPM event :  
  https://httpd.apache.org/docs/2.4/mod/event.html

- Compression avec `mod_deflate` :  
  https://httpd.apache.org/docs/2.4/mod/mod_deflate.html

- Cache Apache :  
  https://httpd.apache.org/docs/2.4/mod/mod_cache.html

- Supervision avec `mod_status` :  
  https://httpd.apache.org/docs/2.4/mod/mod_status.html

### Mesure et diagnostic

- Documentation curl :  
  https://curl.se/docs/

- Projet et documentation de wrk :  
  https://github.com/wg/wrk

- Documentation systemd :  
  https://www.freedesktop.org/software/systemd/man/


## Conclusion générale

La haute performance Web repose sur une démarche méthodique.

Les réglages de Nginx et d'Apache sont importants, mais ils ne constituent qu'une partie de l'équation. La conception des applications, la base de données, le cache, le réseau, les limites du système et les conditions de charge influencent ensemble les résultats.

Un ingénieur doit être capable de mesurer les latences, d'identifier les goulots d'étranglement, de comprendre les limites de concurrence et de vérifier qu'une optimisation améliore effectivement le service sans créer de problème de sécurité ou de disponibilité.

Le parcours de travail recommandé est le suivant :

```text
Comprendre l'architecture
          |
          v
Mesurer la référence
          |
          v
Identifier le goulot
          |
          v
Optimiser le composant concerné
          |
          v
Tester sous charge contrôlée
          |
          v
Comparer le débit, la latence et les erreurs
          |
          v
Valider la sécurité et la cohérence
          |
          v
Déployer progressivement
          |
          v
Surveiller et pouvoir revenir en arrière
```

La véritable maîtrise de la performance ne consiste pas à accumuler les directives, mais à être capable de justifier chaque réglage avec des mesures, d'en comprendre les limites et de démontrer que le résultat répond aux objectifs du service.