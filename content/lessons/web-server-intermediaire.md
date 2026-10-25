# Reverse Proxy et Load Balancing

## 1. Introduction et objectifs pédagogiques

Lorsqu'un site Web reçoit peu de visiteurs, un serveur unique peut suffire à traiter les requêtes. Lorsque le trafic augmente, que plusieurs applications doivent être publiées ou que la disponibilité devient importante, cette architecture peut atteindre ses limites.

Deux mécanismes permettent d'organiser une infrastructure Web plus évolutive :

- **Le reverse proxy** reçoit les requêtes des clients et les transmet aux serveurs ou applications appropriés.
- **Le load balancing**, ou répartition de charge, distribue les requêtes entre plusieurs serveurs capables de traiter le même service.

Nginx et Apache HTTP Server peuvent tous deux remplir ces fonctions.

Ce cours reprend les bases des serveurs Web et approfondit leur utilisation comme intermédiaires entre les clients et les applications.

### 1.1 Compétences attendues

À la fin du cours, vous serez capable de :

- distinguer un proxy direct d'un reverse proxy ;
- expliquer le fonctionnement d'un répartiteur de charge ;
- concevoir une architecture Web avec un point d'entrée et plusieurs serveurs applicatifs ;
- configurer un reverse proxy HTTP avec Nginx ;
- répartir les requêtes entre plusieurs serveurs avec Nginx ;
- utiliser les méthodes de répartition courantes ;
- comprendre les poids, les serveurs de secours et les contrôles de défaillance ;
- configurer un reverse proxy et un répartiteur de charge avec Apache ;
- transmettre correctement les en-têtes HTTP au serveur applicatif ;
- gérer les délais d'attente, les erreurs de passerelle et les tentatives de reprise ;
- comprendre la terminaison TLS et le chiffrement entre le proxy et les applications ;
- diagnostiquer les erreurs 502 et 504 ;
- vérifier la répartition des requêtes au moyen des journaux ;
- construire et tester une architecture locale avec deux serveurs applicatifs ;
- identifier les limites d'une architecture composée d'un seul reverse proxy.

### 1.2 Prérequis

Vous devez maîtriser les éléments suivants :

- utilisation d'un terminal Linux ;
- installation et administration élémentaire de Nginx ou Apache ;
- configuration de sites virtuels ;
- commandes `systemctl`, `ss`, `curl`, `tail` et `journalctl` ;
- notions d'adresses IP, de ports TCP et de DNS ;
- lecture d'un fichier de configuration ;
- fonctionnement élémentaire de HTTP et HTTPS.

Les exemples sont principalement conçus pour Debian et Ubuntu. Les différences entre distributions seront précisées lorsque cela est nécessaire.

### 1.3 Environnement de laboratoire

Nous utiliserons une architecture comportant un point d'entrée et deux serveurs applicatifs.

```text
                         CLIENT
                            |
                            | HTTP
                            v
                  +---------------------+
                  | NGINX               |
                  | Reverse proxy       |
                  | Load balancer       |
                  | Port 8080            |
                  +----------+----------+
                             |
                   +---------+---------+
                   |                   |
                   v                   v
          +----------------+  +----------------+
          | BACKEND 1      |  | BACKEND 2      |
          | Port 8001      |  | Port 8002      |
          | Application A  |  | Application B  |
          +----------------+  +----------------+
```

Dans ce laboratoire, les serveurs applicatifs renverront des pages différentes afin de visualiser la répartition des requêtes.

Les ports 8001, 8002 et 8080 sont choisis pour éviter de dépendre du port HTTP 80, qui peut déjà être utilisé par un service existant.

Les applications de test seront accessibles uniquement depuis la machine locale. Cette précaution convient au laboratoire et évite d'exposer inutilement des serveurs de développement.

**Attention :** le serveur Web, le reverse proxy et les applications peuvent être des processus différents sur une même machine. Dans une infrastructure de production, ils peuvent également se trouver sur des machines, des conteneurs ou des réseaux distincts.


## 2. Comprendre les architectures proxy

### 2.1 Le proxy direct

Un proxy direct, ou *forward proxy*, agit au nom du client.

Il reçoit une demande émise par un client puis réalise l'accès à la ressource distante. Le serveur distant voit généralement la connexion provenant du proxy plutôt que la connexion TCP initiale du client.

```text
CLIENT
   |
   | Requête vers une ressource distante
   v
+-------------------+
| PROXY DIRECT      |
+-------------------+
   |
   | Connexion vers Internet
   v
SERVEUR DISTANT
```

Il peut notamment être utilisé pour :

- appliquer une politique de navigation dans une organisation ;
- contrôler certaines connexions sortantes ;
- mettre en cache des ressources ;
- centraliser des accès à Internet.

Un proxy direct est donc placé du côté des clients.

### 2.2 Le reverse proxy

Le reverse proxy se place devant les serveurs ou applications.

Les clients envoient leurs requêtes au reverse proxy, qui décide où les transmettre.

```text
CLIENTS
   |
   | Requêtes HTTP/HTTPS
   v
+-------------------------+
| REVERSE PROXY           |
|                         |
| - Accepte les requêtes  |
| - Applique des règles   |
| - Choisit une cible     |
| - Journalise les accès  |
+------------+------------+
             |
             v
       SERVEURS INTERNES
```

Le client utilise normalement le nom public du service et n'a pas besoin de connaître l'adresse exacte de chaque serveur applicatif.

Le reverse proxy peut notamment :

- publier plusieurs applications derrière un même point d'entrée ;
- choisir une application selon le nom d'hôte ou le chemin URL ;
- répartir les requêtes entre plusieurs instances ;
- terminer une connexion HTTPS ;
- centraliser des contrôles et des journaux ;
- masquer les détails internes de l'architecture.

Le reverse proxy ne garantit pas automatiquement la sécurité des applications. Il faut toujours contrôler les accès, les en-têtes, les réseaux et les configurations applicatives.

### 2.3 Comparaison

| Élément | Proxy direct | Reverse proxy |
|---|---|---|
| Position habituelle | Côté client | Côté serveur |
| Fonction principale | Organiser les accès sortants | Organiser les accès entrants |
| Client configuré pour utiliser le proxy | Souvent oui | Généralement non |
| Masque habituellement | Les détails du client au serveur distant | Les détails des serveurs internes au client |
| Répartition de charge entrante | Pas sa fonction habituelle | Fonction courante |
| Exemple | Proxy de sortie d'entreprise | Nginx devant plusieurs applications |

La distinction repose essentiellement sur le rôle du proxy et le sens du trafic qu'il organise.


## 3. Comprendre le load balancing

### 3.1 Pourquoi répartir la charge ?

Un serveur applicatif unique peut rencontrer plusieurs limites :

- utilisation excessive du processeur ;
- mémoire insuffisante ;
- saturation des connexions ;
- augmentation du temps de réponse ;
- maintenance difficile sans interruption ;
- indisponibilité totale du service en cas de panne.

La répartition de charge consiste à distribuer les requêtes entre plusieurs serveurs capables de répondre au même service.

```text
                         CLIENTS
                            |
                            v
                  +---------------------+
                  | LOAD BALANCER       |
                  | Répartiteur         |
                  +----------+----------+
                             |
                +------------+------------+
                |            |            |
                v            v            v
            +-------+    +-------+    +-------+
            | APP 1 |    | APP 2 |    | APP 3 |
            +-------+    +-------+    +-------+
```

Cette architecture permet d'augmenter la capacité en ajoutant des instances applicatives, sous réserve que le reste du système puisse suivre.

### 3.2 Reverse proxy et load balancer : quelle différence ?

Les deux notions sont liées, mais ne sont pas identiques.

Un reverse proxy peut transmettre toutes les requêtes à un seul serveur.

Un load balancer choisit une cible parmi plusieurs serveurs ou instances selon une politique de répartition.

```text
REVERSE PROXY SIMPLE

Client --> Proxy --> Application unique
```

```text
REVERSE PROXY AVEC LOAD BALANCING

Client --> Proxy --> +--> Application 1
                     |
                     +--> Application 2
                     |
                     +--> Application 3
```

Un même Nginx peut jouer les deux rôles : recevoir les requêtes, puis choisir un serveur dans un groupe de serveurs applicatifs.

### 3.3 Les objectifs de la répartition

La répartition de charge peut servir à :

- mieux utiliser les ressources disponibles ;
- augmenter le nombre de requêtes traitées ;
- réduire les risques de surcharge d'un serveur ;
- permettre l'ajout d'instances ;
- améliorer la continuité du service lorsqu'un backend devient indisponible.

Elle ne garantit pas une réduction du temps de réponse dans tous les cas. La latence peut être dominée par la base de données, la logique de l'application, le réseau ou d'autres dépendances.

Elle ne rend pas non plus automatiquement une application tolérante aux pannes. Il faut que les applications, leurs données et leurs dépendances soient compatibles avec cette architecture.


## 4. Architecture HTTP avec reverse proxy

### 4.1 Le cheminement d'une requête

Dans une architecture avec Nginx en reverse proxy, une requête suit généralement les étapes suivantes :

```text
1. Le client demande une URL publique.
              |
              v
2. La connexion arrive sur Nginx.
              |
              v
3. Nginx analyse le nom d'hôte et le chemin.
              |
              v
4. Nginx sélectionne une cible.
              |
              v
5. Nginx transmet la requête au backend.
              |
              v
6. Le backend traite la requête.
              |
              v
7. Le backend renvoie une réponse à Nginx.
              |
              v
8. Nginx renvoie la réponse au client.
```

Le client ne communique donc pas nécessairement directement avec le processus applicatif.

### 4.2 Exemple de flux réseau

Supposons :

- Nginx : `192.0.2.10`, port 443 ;
- application : `10.0.0.11`, port 3000.

Ces adresses sont des exemples réservés à la documentation.

```text
CLIENT
  |
  | HTTPS vers 192.0.2.10:443
  v
NGINX
  |
  | HTTP interne vers 10.0.0.11:3000
  v
APPLICATION
```

Nginx peut terminer TLS, puis transmettre la requête en HTTP sur un réseau privé.

Cette architecture nécessite que le réseau entre le proxy et l'application soit suffisamment protégé. Si ce réseau n'est pas considéré comme fiable, un chiffrement entre le proxy et le backend doit être envisagé.

Le port 3000 représente ici un port applicatif choisi à titre d'exemple. Il ne s'agit pas d'un port obligatoire pour les applications Web.

### 4.3 Routage selon le nom d'hôte

Un reverse proxy peut publier plusieurs applications à partir d'une même adresse IP.

```text
                    https://app-a.exemple.com
                               |
                               v
                        +-------------+
                        | NGINX       |
                        +------+------+
                               |
                               +------> Application A

                    https://app-b.exemple.com
                               |
                               v
                        +-------------+
                        | NGINX       |
                        +------+------+
                               |
                               +------> Application B
```

Cette approche utilise notamment les noms d'hôte reçus dans les requêtes.

Pour une installation réelle, les noms DNS, les certificats et les blocs de configuration doivent correspondre à l'architecture effectivement déployée.

### 4.4 Routage selon le chemin

Une autre possibilité consiste à publier plusieurs applications sous un même nom :

```text
https://exemple.com/
        |
        +---- /api/      --> Application API
        |
        +---- /boutique/ --> Application boutique
        |
        +---- /admin/    --> Interface d'administration
```

Le routage par chemin permet d'organiser plusieurs applications, mais il nécessite une attention particulière aux chemins transmis aux backends.

Une application peut supposer qu'elle est publiée à la racine `/`. Si le proxy la publie sous `/boutique/`, elle doit être conçue ou configurée pour gérer correctement cette base d'URL.


## 5. Nginx : configurer un reverse proxy simple

### 5.1 Le rôle de `proxy_pass`

La directive Nginx `proxy_pass` définit le serveur ou le groupe de serveurs auquel transmettre une requête.

Exemple :

```nginx
location / {
    proxy_pass http://127.0.0.1:8001;
}
```

Dans cet exemple, les requêtes correspondant à `/` sont transmises au service HTTP exécuté sur le port 8001 de la même machine.

Cette configuration est un reverse proxy, même si un seul backend est utilisé.

### 5.2 Configuration complète de base

Supposons qu'une application écoute sur :

```text
127.0.0.1:8001
```

Sur une installation Nginx disposant de `/etc/nginx/conf.d/`, créez :

```bash
sudo nano /etc/nginx/conf.d/reverse-proxy.conf
```

Contenu :

```nginx
server {
    listen 127.0.0.1:8080;
    server_name proxy-lab.test;

    access_log /var/log/nginx/reverse-proxy-access.log;
    error_log  /var/log/nginx/reverse-proxy-error.log;

    location / {
        proxy_pass http://127.0.0.1:8001;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 3s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

Cette configuration utilise le port 8080 et une écoute locale afin de limiter l'exposition du laboratoire.

Selon la distribution, l'emplacement des fichiers chargés par Nginx peut différer. Vérifiez la configuration principale et les directives `include`.

### 5.3 Comprendre les directives

| Directive | Fonction |
|---|---|
| `listen` | Configure l'adresse et le port d'écoute |
| `server_name` | Associe un nom d'hôte à ce serveur virtuel |
| `location /` | Définit les requêtes prises en charge par ce bloc |
| `proxy_pass` | Définit la cible du proxy |
| `proxy_http_version` | Définit la version HTTP utilisée pour la connexion au backend |
| `proxy_set_header` | Définit des en-têtes transmis au backend |
| `proxy_connect_timeout` | Limite le temps d'établissement de la connexion au backend |
| `proxy_send_timeout` | Limite l'intervalle entre des opérations d'envoi au backend |
| `proxy_read_timeout` | Limite l'intervalle entre des opérations de lecture depuis le backend |
| `access_log` | Définit le journal des requêtes |
| `error_log` | Définit le journal des erreurs |

Les délais de `proxy_send_timeout` et `proxy_read_timeout` ne sont pas nécessairement des durées maximales pour toute la requête. Ils s'appliquent notamment aux intervalles entre opérations de transmission ou de lecture, selon la directive.

### 5.4 Pourquoi transmettre le nom d'hôte ?

La directive :

```nginx
proxy_set_header Host $host;
```

permet de transmettre au backend le nom d'hôte attendu.

Sans configuration adaptée, l'application peut recevoir un nom qui ne correspond pas à l'URL publique et générer des liens, redirections ou contrôles incorrects.

La conservation du nom public est fréquente, mais elle doit correspondre aux exigences du backend. Les applications doivent également valider les noms d'hôte qu'elles acceptent.

### 5.5 Comprendre les en-têtes `X-Forwarded-*`

Les applications qui se trouvent derrière un reverse proxy peuvent avoir besoin de connaître certaines informations sur la requête originale.

Les en-têtes courants sont :

- `X-Real-IP` : adresse du client vue par le proxy ;
- `X-Forwarded-For` : adresse ou chaîne d'adresses associées au chemin de la requête ;
- `X-Forwarded-Proto` : schéma utilisé par le client pour accéder au proxy, par exemple `http` ou `https`.

Exemple :

```text
Client
  |
  | HTTPS
  v
Nginx
  |
  | HTTP vers le backend
  | X-Forwarded-Proto: https
  | X-Real-IP: adresse-du-client
  v
Application
```

Dans la configuration du laboratoire, `X-Forwarded-For` reçoit `$remote_addr`, ce qui convient à une architecture où Nginx est le premier proxy de confiance.

Dans une chaîne de plusieurs proxies, on peut utiliser `$proxy_add_x_forwarded_for`, mais l'application doit interpréter la chaîne à partir de proxies explicitement approuvés.

**Un en-tête transmis par un client n'est pas intrinsèquement fiable.** Un client peut envoyer lui-même un faux `X-Forwarded-For`. Il ne faut donc pas autoriser une opération sensible sur la seule base d'un en-tête de ce type sans définir une frontière de confiance.

### 5.6 Tester la configuration

Vérifiez la syntaxe :

```bash
sudo nginx -t
```

Si le test est réussi :

```bash
sudo systemctl reload nginx
```

Vérifiez l'état :

```bash
sudo systemctl status nginx
```

Testez le proxy :

```bash
curl -i http://127.0.0.1:8080/
```

Pour voir les détails de la connexion :

```bash
curl -v http://127.0.0.1:8080/
```

Si aucun service n'écoute sur le port 8001, une erreur de passerelle est attendue. Il faut alors démarrer l'application ou corriger la destination.


## 6. Nginx : répartir les requêtes entre plusieurs serveurs

### 6.1 Le bloc `upstream`

Nginx utilise un bloc `upstream` pour définir un groupe de serveurs applicatifs.

Exemple :

```nginx
upstream application_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

Ce groupe contient deux serveurs.

La directive `proxy_pass` peut ensuite utiliser le nom de ce groupe :

```nginx
location / {
    proxy_pass http://application_backend;
}
```

Nginx choisit un serveur selon la méthode de répartition configurée.

Par défaut, Nginx utilise une méthode de type round robin pondéré. Si les poids ne sont pas spécifiés, les serveurs ont normalement le même poids.

### 6.2 Configuration complète de répartition

Créez un fichier de laboratoire :

```bash
sudo nano /etc/nginx/conf.d/load-balancer.conf
```

Configuration :

```nginx
upstream application_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 127.0.0.1:8080;
    server_name lb-lab.test;

    access_log /var/log/nginx/load-balancer-access.log;
    error_log  /var/log/nginx/load-balancer-error.log;

    location / {
        proxy_pass http://application_backend;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 3s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

**Important :** ce fichier ne doit pas être activé en même temps qu'une autre configuration qui écoute déjà sur la même adresse et le même port avec une définition concurrente. Si vous reprenez le laboratoire précédent, remplacez ou désactivez l'ancien fichier de test pour éviter des conflits.

Vérifiez :

```bash
sudo nginx -t
```

Puis :

```bash
sudo systemctl reload nginx
```

### 6.3 Représentation de la répartition

Supposons que les deux serveurs soient disponibles et qu'ils aient le même poids.

```text
                 NGINX
                   |
          Round Robin pondéré
                   |
       +-----------+-----------+
       |                       |
       v                       v
   BACKEND 1               BACKEND 2
   Port 8001               Port 8002

       Requête 1  ---------->  Backend 1
       Requête 2  ----------------------> Backend 2
       Requête 3  ---------->  Backend 1
       Requête 4  ----------------------> Backend 2
```

Le schéma montre une répartition illustrative. Les connexions réelles, les échecs, les poids et les paramètres du groupe peuvent modifier le résultat.

### 6.4 Tester plusieurs requêtes

Une fois les deux serveurs de test lancés :

```bash
for i in $(seq 1 10); do
    curl -s http://127.0.0.1:8080/
    echo
done
```

Si les backends renvoient des contenus distincts, les réponses doivent montrer que différentes requêtes sont traitées par différentes instances.

Nginx ne garantit pas que chaque groupe de dix requêtes suivra systématiquement une séquence parfaite lorsque des échecs, des poids ou d'autres paramètres interviennent.


## 7. Les algorithmes de load balancing

Il n'existe pas une méthode idéale pour toutes les applications.

Le choix dépend de la charge, de la durée des requêtes, des ressources de chaque serveur, du besoin de persistance des sessions et du comportement des applications.

### 7.1 Round robin

Le round robin répartit successivement les requêtes entre les serveurs du groupe.

```text
Requête 1 --> Backend 1
Requête 2 --> Backend 2
Requête 3 --> Backend 3
Requête 4 --> Backend 1
Requête 5 --> Backend 2
Requête 6 --> Backend 3
```

C'est une bonne base lorsque les serveurs ont des capacités similaires et que les requêtes ont des coûts relativement comparables.

Le round robin peut toutefois donner des charges inégales si certaines requêtes durent beaucoup plus longtemps que d'autres.

### 7.2 Round robin pondéré

Le poids représente la part relative qu'un serveur doit recevoir dans la répartition.

Exemple :

```nginx
upstream application_backend {
    server 127.0.0.1:8001 weight=3;
    server 127.0.0.1:8002 weight=1;
}
```

Avec une répartition stable et des serveurs tous disponibles, le premier serveur recevra approximativement trois fois la part du second.

```text
Poids du Backend 1 : 3
Poids du Backend 2 : 1

Répartition conceptuelle :

Backend 1 : ███████████████  environ 75 %
Backend 2 : █████            environ 25 %
```

Cette proportion est un objectif de répartition des requêtes, pas une garantie de répartition équivalente du temps processeur ou de la mémoire.

Le poids permet notamment de tenir compte de serveurs de capacités différentes ou de déployer progressivement une nouvelle version.

### 7.3 Least connections

La méthode `least_conn` privilégie le serveur qui possède le moins de connexions actives, en tenant compte des poids.

```nginx
upstream application_backend {
    least_conn;

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

Cette méthode est utile lorsque les requêtes ont des durées très variables ou que les connexions restent ouvertes longtemps.

Elle n'est pas une mesure exacte de la charge CPU. Un serveur peut avoir peu de connexions tout en étant très sollicité par une opération coûteuse.

### 7.4 IP hash

La méthode `ip_hash` utilise l'adresse IP du client pour choisir un serveur.

```nginx
upstream application_backend {
    ip_hash;

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

Cette méthode peut améliorer la persistance approximative des sessions lorsque le client retrouve la même adresse IP et que la composition du groupe ne change pas de façon perturbatrice.

Elle comporte plusieurs limites :

- de nombreux clients peuvent partager la même adresse publique à travers un NAT ;
- une adresse client peut changer ;
- un proxy intermédiaire peut masquer l'adresse réelle ;
- l'ajout ou le retrait de serveurs peut modifier les affectations ;
- elle ne remplace pas un stockage de session partagé.

L'adresse IP ne constitue donc pas une identité utilisateur fiable.

### 7.5 Hash fondé sur une clé

Nginx permet également de choisir une clé de hachage personnalisée.

Exemple :

```nginx
upstream application_backend {
    hash $request_uri consistent;

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

Ici, la clé est l'URI demandée.

Le paramètre `consistent` utilise un hachage cohérent afin de limiter le nombre de clés réaffectées lorsque la composition du groupe change.

Attention : une même URI n'identifie pas nécessairement une session utilisateur. Ce choix convient à certains besoins de répartition fondés sur les requêtes, mais ne doit pas être assimilé à une persistance de session.

Le choix d'une clé basée uniquement sur une URL peut également déséquilibrer la charge si certaines URL sont beaucoup plus sollicitées que d'autres.

### 7.6 Random

La méthode `random` choisit des serveurs de manière aléatoire, en tenant compte des poids lorsque ceux-ci sont définis.

Un exemple simple :

```nginx
upstream application_backend {
    random;

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

Cette méthode n'est pas nécessairement préférable au round robin. Son intérêt dépend de la configuration et du modèle de trafic.

### 7.7 Comparaison rapide

| Méthode | Principe | Cas d'utilisation possible | Limite |
|---|---|---|---|
| Round robin | Répartition successive | Serveurs similaires | Ignore la durée des opérations |
| Round robin pondéré | Proportions définies par poids | Capacités différentes | Ne mesure pas directement la charge |
| `least_conn` | Moins de connexions actives | Connexions de durée variable | Le nombre de connexions ne représente pas toute la charge |
| `ip_hash` | Affectation fondée sur IP | Persistance approximative | NAT, changements d'IP et réaffectations |
| `hash` | Affectation fondée sur une clé | Répartition déterministe par clé | Une mauvaise clé peut créer un déséquilibre |
| `random` | Choix aléatoire | Besoins spécifiques de répartition | Le comportement est moins prévisible requête par requête |

**Conseil :** commencez par le round robin. N'ajoutez une méthode plus complexe que si un besoin mesuré le justifie.


## 8. Gestion des poids et des serveurs de secours

### 8.1 Définir un poids

Exemple :

```nginx
upstream application_backend {
    server 127.0.0.1:8001 weight=5;
    server 127.0.0.1:8002 weight=2;
    server 127.0.0.1:8003 weight=1;
}
```

Le premier serveur reçoit une part relative plus importante.

Cette configuration ne garantit cependant pas que le serveur possédant le plus grand poids disposera toujours du plus grand débit de travail utile : les durées de traitement, les erreurs et la charge des dépendances interviennent aussi.

### 8.2 Serveur de secours avec `backup`

Nginx permet de déclarer des serveurs de secours dans un groupe compatible avec ce paramètre.

```nginx
upstream application_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;

    server 127.0.0.1:8003 backup;
}
```

Le serveur `8003` est prévu pour être utilisé lorsque les serveurs principaux ne sont pas disponibles, selon le fonctionnement du groupe.

```text
                   REQUÊTES
                       |
                       v
                +--------------+
                | NGINX        |
                +------+-------+
                       |
              +--------+--------+
              |                 |
              v                 v
         BACKEND 1         BACKEND 2
              |                 |
              +--------+--------+
                       |
                Si indisponibles
                       |
                       v
                 BACKEND SECOURS
```

Le paramètre `backup` n'est pas compatible avec toutes les méthodes de répartition. Vérifiez la documentation de la version installée avant de combiner les directives.

Un serveur de secours doit contenir les composants et les données nécessaires pour assurer la fonction attendue. Un backend de secours qui n'a pas la même configuration ou les mêmes données n'assure pas automatiquement la continuité du service.

### 8.3 Serveur temporairement retiré

Une entrée peut être marquée comme indisponible dans le groupe :

```nginx
upstream application_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002 down;
}
```

Ce type de configuration peut être utile pour certaines opérations de maintenance. Il faut néanmoins la gérer soigneusement afin de ne pas laisser un serveur retiré après la fin d'une intervention.


## 9. Détection des défaillances et reprise

### 9.1 Contrôles passifs dans Nginx open source

Dans Nginx open source, les mécanismes de contrôle de santé du groupe HTTP reposent notamment sur les résultats des échanges réels avec les serveurs applicatifs.

Un serveur peut être considéré comme indisponible après un certain nombre d'échecs pendant une période définie.

Exemple :

```nginx
upstream application_backend {
    server 127.0.0.1:8001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:8002 max_fails=2 fail_timeout=10s;
}
```

### 9.2 Comprendre `max_fails`

`max_fails` représente le nombre d'échecs pris en compte pendant la période définie par `fail_timeout`, avant de considérer le serveur comme indisponible.

Exemple :

```nginx
max_fails=2
```

Le nombre d'échecs configuré doit être atteint pour déclencher le mécanisme prévu.

Si `max_fails` vaut `0`, le comptage des échecs est désactivé pour ce serveur.

### 9.3 Comprendre `fail_timeout`

`fail_timeout` définit notamment la période utilisée pour compter les échecs et la période pendant laquelle le serveur est considéré comme indisponible après le seuil atteint.

Exemple :

```nginx
fail_timeout=10s
```

Cette période ne constitue pas une garantie que l'application sera effectivement réparée au bout de dix secondes. Nginx pourra réessayer le serveur selon les requêtes réelles qui arrivent et les paramètres du groupe.

Sur un groupe ne contenant qu'un seul serveur, certains paramètres de comptage des échecs ne produisent pas le comportement de répartition attendu d'un groupe comportant plusieurs serveurs.

### 9.4 Contrôles passifs et actifs

Il faut distinguer deux mécanismes.

**Contrôle passif :**

- observation des requêtes réellement transmises ;
- détection d'échecs pendant le trafic ;
- exclusion temporaire selon la configuration ;
- nouvelle tentative lorsque le mécanisme le permet.

**Contrôle actif :**

- envoi de sondes selon un calendrier ;
- vérification d'une route de santé dédiée ;
- contrôle d'une réponse attendue ;
- détection d'un problème indépendamment d'une nouvelle requête client.

La prise en charge des contrôles actifs HTTP pour les upstreams Nginx dépend de l'édition et des fonctionnalités utilisées. Les contrôles actifs documentés pour NGINX Plus ne doivent pas être présentés comme une fonction universellement disponible dans Nginx open source.

Un orchestrateur ou un outil externe peut également réaliser des contrôles de santé.

### 9.5 Que vérifier dans une sonde de santé ?

Une sonde HTTP peut tester un chemin dédié, par exemple :

```text
/health
```

Mais une réponse HTTP 200 n'est utile que si elle correspond réellement à l'état que l'on souhaite vérifier.

Il faut déterminer si la sonde vérifie :

- que le processus Web répond ;
- que l'application peut traiter une requête ;
- que les dépendances critiques sont accessibles ;
- que le service est prêt à recevoir du trafic.

Un contrôle qui teste toutes les dépendances peut devenir coûteux ou provoquer des cascades de vérifications. Le niveau de contrôle doit être choisi en fonction de l'architecture.

### 9.6 Limites du basculement automatique

Une panne d'un backend ne signifie pas toujours que l'autre peut traiter la requête sans erreur.

Par exemple, si le backend principal traite un paiement puis perd la connexion avant de renvoyer sa réponse, le proxy ne peut pas toujours savoir si le paiement a été effectué.

Réessayer automatiquement la requête pourrait provoquer une double opération.

La reprise doit donc tenir compte de la nature de la requête et des garanties applicatives.


## 10. Gestion des reprises avec Nginx

### 10.1 La directive `proxy_next_upstream`

Nginx peut être configuré pour réessayer un autre serveur d'un groupe lorsque certains types d'erreurs surviennent.

Exemple :

```nginx
location / {
    proxy_pass http://application_backend;

    proxy_next_upstream error timeout http_502 http_503 http_504;
    proxy_next_upstream_tries 2;
}
```

Dans cet exemple, Nginx peut tenter d'utiliser un autre serveur à la suite des événements définis, selon les règles de la directive.

`proxy_next_upstream_tries` limite le nombre de tentatives vers les serveurs upstream ; il ne faut pas l'interpréter comme une garantie que chaque requête réussira.

### 10.2 Attention aux requêtes non idempotentes

Une opération idempotente peut être répétée sans modifier le résultat final au-delà du résultat de la première exécution, dans les conditions où cette propriété est assurée.

Une lecture HTTP `GET` correctement conçue est généralement idempotente. Une opération de paiement ou de création peut ne pas l'être.

Si une requête est envoyée au backend puis que la connexion échoue avant la réception de la réponse, l'application peut avoir effectué l'opération même si Nginx ne connaît pas son résultat.

Il faut donc éviter d'autoriser les nouvelles tentatives non sûres sans disposer d'une conception applicative adaptée, par exemple des clés d'idempotence ou une logique de déduplication.

Ne configurez pas automatiquement la reprise de toute requête `POST` simplement parce que plusieurs serveurs sont disponibles.

### 10.3 Une architecture correcte de reprise

```text
Client
  |
  v
Nginx
  |
  v
Backend 1
  |
  | Échec avant résultat exploitable
  v
Décision de reprise
  |
  +--> Autre backend si la reprise est sûre
  |
  +--> Erreur au client si la reprise est impossible
```

La décision dépend des erreurs rencontrées, de la configuration, du type de requête et de la possibilité qu'une opération ait déjà été exécutée.


## 11. Comprendre les délais d'attente

Un reverse proxy doit gérer les situations où un backend devient lent ou ne répond plus.

### 11.1 Les principales directives Nginx

```nginx
location / {
    proxy_pass http://application_backend;

    proxy_connect_timeout 3s;
    proxy_send_timeout 30s;
    proxy_read_timeout 30s;
}
```

`proxy_connect_timeout` contrôle le délai d'établissement de la connexion au backend.

`proxy_send_timeout` contrôle l'intervalle maximal entre des opérations d'envoi au backend.

`proxy_read_timeout` contrôle l'intervalle maximal entre des opérations de lecture de la réponse du backend.

### 11.2 Ne pas augmenter les délais sans diagnostic

Si une application répond trop lentement, augmenter tous les délais peut masquer le problème tout en gardant des connexions ouvertes plus longtemps.

Avant de modifier les valeurs, il faut comprendre :

- le temps de traitement normal de l'application ;
- les durées observées sous charge ;
- le comportement de la base de données ;
- les limites du client et du réseau ;
- le nombre de requêtes simultanées ;
- les besoins spécifiques, par exemple pour un téléchargement ou un flux continu.

Les délais doivent refléter les exigences du service et les capacités des ressources disponibles.


## 12. Nginx : comprendre les chemins de `proxy_pass`

La présence ou l'absence d'une URI dans `proxy_pass` peut modifier le chemin transmis au backend.

Cette distinction est essentielle lorsque plusieurs applications sont publiées sous des préfixes.

### 12.1 Préfixe remplacé

Configuration :

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001/;
}
```

Pour une requête publique :

```text
/api/clients
```

Le backend reçoit généralement :

```text
/clients
```

La partie du chemin correspondant au `location` est remplacée par l'URI indiquée dans `proxy_pass`.

### 12.2 Préfixe conservé

Configuration :

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8001;
}
```

Dans cette situation, la requête publique :

```text
/api/clients
```

est normalement transmise au backend avec le chemin :

```text
/api/clients
```

### 12.3 Représentation

```text
REQUÊTE PUBLIQUE : /api/clients
                 |
                 v
Configuration A
location /api/
proxy_pass http://127.0.0.1:8001/
                 |
                 v
BACKEND : /clients
```

```text
REQUÊTE PUBLIQUE : /api/clients
                 |
                 v
Configuration B
location /api/
proxy_pass http://127.0.0.1:8001
                 |
                 v
BACKEND : /api/clients
```

Les comportements détaillés dépendent également de la normalisation de l'URI et des règles applicables. Lorsque le routage dépend d'un préfixe, testez explicitement le chemin reçu par le backend.

### 12.4 Erreurs fréquentes

Une mauvaise combinaison de préfixes peut provoquer :

- des routes introuvables ;
- des doubles préfixes comme `/api/api/clients` ;
- des redirections incorrectes ;
- des ressources CSS ou JavaScript non chargées ;
- des chemins inattendus dans les journaux applicatifs.

Le meilleur diagnostic consiste à comparer l'URI demandée par le client et celle réellement reçue par l'application.


## 13. Journaux et observabilité de Nginx

### 13.1 Pourquoi les journaux standard ne suffisent pas toujours ?

Lorsqu'un reverse proxy reçoit une réponse 502, le journal d'accès peut indiquer le statut renvoyé au client sans rendre immédiatement évident le backend qui a échoué.

Il est souvent utile de journaliser des informations associées à l'upstream.

### 13.2 Créer un format de journal dédié

Dans un fichier chargé à l'intérieur du contexte `http`, comme un fichier placé dans `/etc/nginx/conf.d/` sur les installations adaptées, vous pouvez définir :

```nginx
log_format upstream_details
    '$remote_addr host=$host '
    '"$request" status=$status '
    'upstream=$upstream_addr '
    'upstream_status=$upstream_status '
    'request_time=$request_time '
    'upstream_time=$upstream_response_time';
```

Ce format enregistre notamment :

- l'adresse du client vue par le proxy ;
- le nom d'hôte ;
- la requête ;
- le statut renvoyé au client ;
- l'adresse du serveur upstream ;
- le ou les statuts associés à l'upstream ;
- le temps total de traitement côté proxy ;
- le temps associé à l'upstream.

Dans le bloc `server`, utilisez ensuite :

```nginx
access_log /var/log/nginx/upstream-details.log upstream_details;
```

Le format `upstream_details` doit être défini dans un contexte où `log_format` est autorisé avant son utilisation.

### 13.3 Interpréter les informations

Exemple illustratif :

```text
status=200 upstream=127.0.0.1:8001 upstream_status=200 request_time=0.012 upstream_time=0.008
```

Cette ligne suggère que la requête a reçu une réponse 200 de l'upstream et que le temps observé par le proxy était de l'ordre de quelques millisecondes.

Les champs temporels ne doivent pas être interprétés comme un profil complet des performances de l'application. Il faut considérer la méthode de mesure, les éventuelles tentatives successives et la structure du format de journal.

### 13.4 Suivre les journaux

```bash
sudo tail -f /var/log/nginx/upstream-details.log
```

Pour les erreurs :

```bash
sudo tail -f /var/log/nginx/error.log
```

Il est important de vérifier les emplacements réels définis dans la configuration.

Les journaux peuvent contenir des informations sensibles. Limitez leurs permissions, évitez d'y enregistrer inutilement des données personnelles et définissez une politique de rotation et de conservation.


## 14. Apache HTTP Server comme reverse proxy

Apache peut également transmettre les requêtes vers une application distante.

La fonction est généralement assurée par `mod_proxy` et les modules qui gèrent les protocoles nécessaires.

### 14.1 Modules courants

Sur Debian et Ubuntu, les modules peuvent être activés au moyen de `a2enmod`.

| Module | Rôle |
|---|---|
| `proxy` | Fonctionnalités de base du proxy |
| `proxy_http` | Proxy HTTP |
| `proxy_balancer` | Fonctionnalités de répartition de charge |
| `lbmethod_byrequests` | Algorithme fondé sur le nombre de requêtes |
| `headers` | Modification et gestion des en-têtes HTTP |

Les modules nécessaires dépendent des fonctionnalités utilisées et de la distribution.

### 14.2 Activer les modules nécessaires

Pour un reverse proxy HTTP simple sous Debian ou Ubuntu :

```bash
sudo a2enmod proxy proxy_http headers
```

Pour un répartiteur HTTP :

```bash
sudo a2enmod proxy_balancer lbmethod_byrequests
```

Vérifiez ensuite la configuration :

```bash
sudo apachectl configtest
```

Puis rechargez le service si le test a réussi :

```bash
sudo systemctl reload apache2
```

Sur une distribution utilisant `httpd`, les chemins, méthodes d'activation des modules et noms de service peuvent différer.

### 14.3 Exemple d'un reverse proxy Apache

Supposons que l'application écoute sur `127.0.0.1:8001`.

Créez un hôte virtuel dans un fichier adapté à votre distribution. Sur Debian et Ubuntu, vous pouvez utiliser :

```bash
sudo nano /etc/apache2/sites-available/reverse-proxy-lab.conf
```

Exemple :

```apache
<VirtualHost 127.0.0.1:8081>
    ServerName apache-proxy-lab.test

    ProxyRequests Off
    ProxyPreserveHost On

    ProxyPass        "/" "http://127.0.0.1:8001/"
    ProxyPassReverse "/" "http://127.0.0.1:8001/"

    ErrorLog ${APACHE_LOG_DIR}/reverse-proxy-lab-error.log
    CustomLog ${APACHE_LOG_DIR}/reverse-proxy-lab-access.log combined
</VirtualHost>
```

Cette configuration utilise le port 8081 pour le laboratoire.

Pour que le service écoute sur ce port, ajoutez une directive `Listen` appropriée dans le fichier de ports de la distribution, si elle n'existe pas déjà. Sur Debian et Ubuntu, ce fichier est fréquemment :

```text
/etc/apache2/ports.conf
```

Pour le laboratoire local, la directive peut être :

```apache
Listen 127.0.0.1:8081
```

N'ajoutez pas plusieurs directives contradictoires ou redondantes. Vérifiez la configuration existante avant de modifier ce fichier.

Activez l'hôte virtuel :

```bash
sudo a2ensite reverse-proxy-lab.conf
```

Testez :

```bash
sudo apachectl configtest
```

Puis rechargez Apache :

```bash
sudo systemctl reload apache2
```

Testez le résultat :

```bash
curl -i http://127.0.0.1:8081/
```

### 14.4 Comprendre `ProxyPass`

La directive :

```apache
ProxyPass "/" "http://127.0.0.1:8001/"
```

indique qu'Apache transmet les requêtes correspondant au chemin `/` à l'application distante.

La directive :

```apache
ProxyPassReverse "/" "http://127.0.0.1:8001/"
```

permet notamment d'ajuster certaines en-têtes de redirection de réponse afin que des URL produites par le backend ne conduisent pas inutilement le client à contourner le reverse proxy.

`ProxyPassReverse` ne réécrit pas automatiquement toutes les URL contenues dans le corps HTML. Les applications doivent donc être configurées correctement pour leur URL publique.

### 14.5 Pourquoi `ProxyRequests Off` est important

Un reverse proxy n'a pas besoin d'être un proxy direct ouvert.

Le paramètre :

```apache
ProxyRequests Off
```

désactive la fonction de proxy direct dans cette configuration.

Il est essentiel de ne pas ouvrir par erreur un proxy qui permettrait à des tiers d'utiliser le serveur pour accéder à des destinations non autorisées.

La restriction de l'accès au proxy et le contrôle des destinations font partie de la sécurité de l'installation.


## 15. Apache : configurer un répartiteur de charge

### 15.1 Le principe

Apache utilise un groupe de type `balancer://` pour représenter plusieurs serveurs applicatifs.

Exemple conceptuel :

```text
Clients
   |
   v
Apache HTTP Server
   |
   v
balancer://application_cluster
   |
   +----> Backend 1
   |
   +----> Backend 2
```

Le groupe contient des membres, puis un algorithme détermine comment répartir les requêtes.

### 15.2 Configuration de base

Dans un laboratoire où Apache peut écouter sur le port 8081, une configuration peut ressembler à ceci :

```apache
<VirtualHost 127.0.0.1:8081>
    ServerName apache-lb-lab.test

    ProxyRequests Off
    ProxyPreserveHost On

    <Proxy "balancer://application_cluster">
        BalancerMember "http://127.0.0.1:8001"
        BalancerMember "http://127.0.0.1:8002"

        ProxySet lbmethod=byrequests
    </Proxy>

    ProxyPass        "/" "balancer://application_cluster/"
    ProxyPassReverse "/" "balancer://application_cluster/"

    ErrorLog ${APACHE_LOG_DIR}/apache-lb-error.log
    CustomLog ${APACHE_LOG_DIR}/apache-lb-access.log combined
</VirtualHost>
```

Dans cet exemple, Apache utilise un algorithme de répartition fondé sur le nombre de requêtes grâce à `lbmethod=byrequests`.

Vérifiez que le module correspondant est chargé et que la configuration est valide avant de recharger le service.

### 15.3 Ajouter des paramètres de membre

Les membres du groupe peuvent être configurés avec des paramètres adaptés à leurs rôles, leurs capacités et la politique du répartiteur.

Il faut toutefois distinguer la configuration de la répartition, les mécanismes de reprise et les vérifications de disponibilité. La présence de plusieurs `BalancerMember` ne suffit pas à garantir un basculement correct dans tous les cas.

Avant une mise en production, vérifiez la documentation de la version d'Apache utilisée, notamment celle de `mod_proxy_balancer` et des modules `mod_lbmethod_*`.

### 15.4 Algorithmes courants sous Apache

Apache peut utiliser différents modules d'ordonnancement, selon les modules installés.

| Méthode | Principe général |
|---|---|
| `byrequests` | Répartition basée sur le nombre de requêtes |
| `bytraffic` | Répartition basée sur le volume de trafic |
| `bybusyness` | Répartition fondée sur les requêtes en cours |
| `byheartbeat` | Utilise des informations de heartbeat lorsqu'un environnement compatible est configuré |

Ces méthodes ne sont pas interchangeables. Le module d'ordonnancement adéquat doit être disponible et les paramètres du groupe doivent être adaptés à la charge réelle.


## 16. Persistance des sessions

### 16.1 Pourquoi parler de sessions ?

Certaines applications conservent l'état d'une session utilisateur dans la mémoire d'une instance.

Exemple :

```text
Utilisateur A --> Backend 1
Utilisateur A --> Backend 2
```

Si les données de session sont exclusivement conservées dans le processus de la première instance, la seconde instance peut ne pas reconnaître l'état de session.

Cela peut provoquer :

- une déconnexion ;
- la perte du contenu d'un panier ;
- une demande de connexion répétée ;
- un parcours de navigation incohérent.

### 16.2 Première solution : stockage partagé

Une approche consiste à placer les données de session dans un stockage partagé, par exemple une base de données ou un service de cache conçu à cette fin.

```text
                +----------------+
                | Load balancer  |
                +-------+--------+
                        |
               +--------+--------+
               |                 |
               v                 v
          Backend 1          Backend 2
               |                 |
               +--------+--------+
                        |
                        v
                Stockage de session
```

Cette solution facilite le changement de backend, mais le stockage lui-même doit être dimensionné, sécurisé et rendu disponible.

### 16.3 Deuxième solution : affinité de session

L'affinité de session, aussi appelée *sticky session*, vise à renvoyer un client vers une instance donnée.

Cela peut être réalisé par des mécanismes fondés sur une adresse IP, un cookie ou un identifiant de route, selon le produit et la configuration utilisés.

Cependant, l'affinité ne résout pas à elle seule la panne du serveur qui conserve l'état. Si cette instance disparaît et que la session n'existe nulle part ailleurs, son état peut être perdu.

### 16.4 Ce qu'il faut retenir

```text
Sticky session
    |
    +-- Peut aider à conserver l'affectation d'un client
    |
    +-- Ne remplace pas la disponibilité des données
    |
    +-- Peut réduire la liberté de répartition de charge
```

Il est généralement préférable de concevoir les applications pour qu'elles puissent fonctionner avec plusieurs instances et un stockage d'état partagé lorsque cela correspond aux besoins du système.


## 17. TLS et terminaison HTTPS

### 17.1 Le rôle du reverse proxy dans HTTPS

Un reverse proxy peut terminer la connexion TLS au point d'entrée public.

Il déchiffre la requête HTTP puis la transmet à l'application.

```text
Client
   |
   | HTTPS
   v
+-------------------------+
| NGINX                   |
| Certificat TLS          |
| Terminaison TLS         |
+------------+------------+
             |
             | HTTP interne
             v
       Application
```

Cette architecture simplifie parfois la gestion centralisée des certificats et des paramètres TLS.

Mais le trafic entre le proxy et le backend est alors en HTTP. Si le réseau interne est partagé, exposé ou non fiable, ce choix peut être inadapté.

### 17.2 Trois modèles courants

**Modèle A : TLS au proxy et HTTP interne**

```text
Client -- HTTPS --> Proxy -- HTTP --> Backend
```

Ce modèle est parfois acceptable sur un réseau interne maîtrisé et protégé.

**Modèle B : TLS au proxy et TLS vers le backend**

```text
Client -- HTTPS --> Proxy -- HTTPS --> Backend
```

Ce modèle assure un chiffrement sur les deux segments. Le proxy doit vérifier correctement le certificat du backend lorsque l'identité de celui-ci doit être garantie.

**Modèle C : terminaison TLS en amont**

```text
Client -- HTTPS --> Load balancer amont -- HTTP/TLS --> Proxy
```

La sécurité dépend alors du rôle de chaque équipement, du réseau utilisé, des certificats et des règles de confiance.

Il faut documenter clairement où le chiffrement commence et où il se termine.

### 17.3 Configuration HTTPS conceptuelle avec Nginx

Exemple simplifié :

```nginx
server {
    listen 443 ssl;
    server_name app.exemple.com;

    ssl_certificate     /chemin/vers/certificat.pem;
    ssl_certificate_key /chemin/vers/cle-privee.pem;

    location / {
        proxy_pass http://application_backend;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

Les chemins sont illustratifs. Cette configuration ne fonctionnera qu'avec des certificats appropriés, une clé privée protégée et un upstream valide.

Dans cet exemple, le schéma externe est fixé à `https` parce que le bloc écoute en HTTPS. Dans un environnement comprenant plusieurs points d'entrée, le schéma transmis doit représenter le protocole réellement utilisé par le client et provenir d'une source de confiance.

### 17.4 Attention aux redirections

Une application peut construire ses redirections à partir des informations reçues du proxy.

Si elle pense que la requête externe est en HTTP alors que le client utilise HTTPS, elle peut :

- rediriger vers HTTP ;
- produire des URL incorrectes ;
- entrer dans une boucle de redirection ;
- définir certains cookies sans leurs attributs de sécurité attendus.

Il faut donc configurer correctement la reconnaissance du schéma public et les paramètres de confiance de l'application.


## 18. En-têtes de sécurité et chaîne de confiance

### 18.1 Qui a fourni l'en-tête ?

Quand un proxy ajoute ou transmet un en-tête, l'application doit déterminer si elle peut faire confiance à sa valeur.

Un client malveillant peut essayer de fournir lui-même :

```text
X-Forwarded-For: 127.0.0.1
```

ou :

```text
X-Forwarded-Proto: https
```

Si l'application interprète aveuglément ces valeurs, elle peut prendre une décision incorrecte sur l'origine ou le protocole de la requête.

### 18.2 Définir une frontière de confiance

Il est recommandé de :

- connaître les proxies autorisés à transmettre des requêtes ;
- n'accepter les en-têtes de proxy que depuis ces équipements ;
- supprimer ou réécrire les en-têtes non fiables à l'entrée ;
- configurer l'application pour qu'elle n'interprète pas n'importe quel en-tête comme une preuve d'identité ;
- limiter l'accès direct aux applications si elles doivent être consultées uniquement via le proxy.

### 18.3 Ne pas confondre en-têtes et authentification

Les en-têtes `X-Real-IP`, `X-Forwarded-For` et `X-Forwarded-Proto` ne remplacent pas l'authentification.

Une application qui doit vérifier l'identité d'un utilisateur doit le faire avec un mécanisme d'authentification approprié.

L'adresse IP du client peut être utile pour le diagnostic ou certaines politiques réseau, mais elle ne prouve pas à elle seule l'identité de cet utilisateur.


## 19. Reverse proxy et WebSocket

Les connexions WebSocket permettent notamment des échanges interactifs et persistants entre un client et un serveur.

Contrairement à une succession de requêtes HTTP ordinaires, une connexion WebSocket peut rester ouverte longtemps après la négociation initiale.

### 19.1 Schéma général

```text
Client WebSocket
       |
       | HTTP Upgrade
       v
+------------------+
| Reverse proxy    |
+--------+---------+
         |
         | Transmission de la négociation
         v
   Application WebSocket
```

Pour qu'une application fonctionne derrière le reverse proxy, celui-ci doit transmettre correctement les en-têtes de mise à niveau et permettre le maintien de la connexion.

### 19.2 Configuration Nginx

Le bloc `map` suivant doit être placé dans le contexte `http`, et non à l'intérieur d'un bloc `server` ou `location`.

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
```

Puis, dans le bloc approprié :

```nginx
location /ws/ {
    proxy_pass http://application_backend;

    proxy_http_version 1.1;

    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_read_timeout 3600s;
}
```

Le délai d'une heure est une valeur d'exemple, pas une recommandation universelle. Il faut définir les délais selon les besoins et le mécanisme de maintien en vie de la connexion.

### 19.3 Pourquoi cette configuration est-elle particulière ?

Les en-têtes `Upgrade` et `Connection` interviennent dans le mécanisme de mise à niveau du protocole.

Un reverse proxy configuré pour les requêtes HTTP ordinaires peut ne pas transmettre automatiquement les informations nécessaires à WebSocket.

Il faut tester le comportement réel de l'application, notamment après les changements de configuration, les interruptions réseau et les délais d'inactivité.


## 20. Erreurs 502 et 504 : diagnostic approfondi

### 20.1 Erreur 502 Bad Gateway

L'erreur 502 signifie qu'un serveur agissant comme passerelle ou proxy a reçu une réponse qu'il n'a pas pu traiter correctement, ou qu'une communication avec l'amont a échoué d'une manière correspondant à ce statut.

Causes possibles :

- le backend est arrêté ;
- la mauvaise adresse ou le mauvais port est configuré ;
- le protocole est incorrect ;
- le backend ferme la connexion de façon inattendue ;
- le serveur applicatif renvoie une réponse invalide ;
- un problème de socket ou de permissions empêche la connexion.

### 20.2 Erreur 504 Gateway Timeout

Le statut 504 indique qu'une passerelle n'a pas obtenu une réponse à temps du serveur en amont.

Causes possibles :

- l'application est très lente ;
- une dépendance applicative est bloquée ;
- une requête de base de données dure trop longtemps ;
- le réseau entre le proxy et le backend subit un problème ;
- les délais configurés ne correspondent pas au comportement attendu du service.

### 20.3 Tableau de diagnostic

| Symptôme | Contrôle initial |
|---|---|
| 502 immédiat | Vérifier la disponibilité du backend et le port |
| 504 après un délai | Vérifier le temps de traitement et les dépendances |
| 404 seulement derrière le proxy | Vérifier les chemins transmis |
| Redirections vers le mauvais domaine | Vérifier le nom d'hôte et les en-têtes |
| URL en HTTP malgré HTTPS | Vérifier le schéma de confiance transmis à l'application |
| Un seul backend reçoit les requêtes | Vérifier le groupe chargé, les poids et les journaux |
| Échec après l'arrêt d'un backend | Vérifier les mécanismes de reprise et les états de santé |

### 20.4 Procédure de diagnostic

```text
1. Reproduire l'erreur avec curl
                |
                v
2. Tester directement le backend
                |
                v
3. Vérifier le port en écoute
                |
                v
4. Vérifier la configuration du proxy
                |
                v
5. Lire les journaux Nginx/Apache
                |
                v
6. Lire les journaux de l'application
                |
                v
7. Examiner les délais et les dépendances
                |
                v
8. Corriger la cause, puis retester
```

L'objectif est d'identifier si le problème se situe dans le proxy, le backend, le réseau ou l'application.


## 21. Performances, connexions et mise en mémoire tampon

### 21.1 Garder les connexions au bon niveau

Un reverse proxy reçoit des connexions de clients et établit des connexions vers les backends. La gestion des connexions influe sur les ressources consommées et les performances.

Nginx permet de configurer la version HTTP entre le proxy et le backend ainsi que les paramètres associés aux connexions.

La directive `keepalive` dans un groupe upstream peut servir à conserver des connexions inactives prêtes à être réutilisées, selon la configuration du module et le protocole utilisé.

Il ne faut pas ajouter des valeurs arbitraires sans observer le nombre de connexions simultanées, les limites système et le comportement des applications.

### 21.2 Mise en mémoire tampon

La mise en mémoire tampon permet au proxy de lire ou de stocker temporairement certaines données pendant qu'il traite une requête ou une réponse.

Elle peut aider à séparer la vitesse du client de celle du backend et à gérer plus efficacement certains flux.

Cependant, pour certaines applications de streaming ou certains événements envoyés en continu, une mise en mémoire tampon inadaptée peut retarder l'arrivée des données au client.

Avant de désactiver la mise en mémoire tampon, identifiez précisément le comportement attendu. Cette modification n'est pas automatiquement bénéfique.

### 21.3 Taille des requêtes

Une application qui accepte des fichiers volumineux doit définir correctement ses limites de taille.

Dans Nginx, la directive `client_max_body_size` peut limiter la taille du corps d'une requête entrante.

Exemple :

```nginx
server {
    listen 127.0.0.1:8080;

    client_max_body_size 10m;

    location / {
        proxy_pass http://application_backend;
    }
}
```

Cette valeur est illustrative. Il faut définir la limite en fonction du service, de la capacité de stockage, des contraintes de sécurité et des besoins métier.

Augmenter la limite de taille ne garantit pas que l'application ou le backend peut traiter le fichier correspondant.


## 22. Sécurité d'une architecture reverse proxy

### 22.1 Ne pas exposer inutilement les backends

Dans une architecture où seul le proxy doit être accessible publiquement, les applications peuvent être limitées à des adresses privées ou à une interface locale.

```text
Internet
   |
   v
Reverse proxy public
   |
   | Réseau privé
   v
Backends non publics
```

Cette séparation réduit les possibilités d'accès direct aux applications, mais elle doit être appliquée aux règles réseau et aux services eux-mêmes.

### 22.2 Éviter un proxy ouvert

Un proxy ouvert peut servir de relais à des tiers non autorisés.

Il faut notamment :

- limiter les destinations que le proxy peut joindre ;
- ne pas activer de fonction de proxy direct inutile ;
- restreindre l'accès aux interfaces administratives ;
- contrôler les noms d'hôte et les routes ;
- empêcher qu'un utilisateur fournisse une destination arbitraire qui conduirait à une ressource interne.

Le reverse proxy doit transmettre les requêtes vers des destinations définies par l'administration, pas devenir un mécanisme général d'accès à des adresses arbitraires.

### 22.3 Protéger les en-têtes sensibles

Il faut définir une politique cohérente pour :

- les en-têtes d'identification du client ;
- le nom d'hôte ;
- le schéma public ;
- les informations de proxy intermédiaire ;
- les en-têtes utilisés par les applications pour prendre des décisions de sécurité.

Évitez de faire confiance à une valeur simplement parce qu'elle commence par `X-Forwarded-`.

### 22.4 Restreindre les interfaces d'administration

Une interface d'administration ne doit pas devenir publiquement accessible simplement parce qu'un reverse proxy est configuré pour transmettre toutes les requêtes.

Pour une route administrative, il peut être nécessaire d'appliquer des restrictions réseau, de l'authentification et des contrôles supplémentaires.

Ces règles doivent être conçues en fonction de l'application et de son modèle de menace.

### 22.5 Sécuriser le transport interne

La connexion entre le proxy et les backends doit faire l'objet d'une politique claire.

Selon l'infrastructure, cela peut inclure :

- un réseau privé ;
- des règles de filtrage ;
- TLS vers les backends ;
- une vérification correcte des certificats ;
- des droits de connexion limités ;
- des journaux et alertes.

Un réseau interne n'est pas automatiquement sûr parce qu'il n'est pas directement public.


## 23. Travaux pratiques complets

Les exercices suivants utilisent Nginx, deux serveurs applicatifs de test et des ports élevés.

Le service Python `http.server` est utilisé uniquement pour simuler des backends simples. Il n'est pas destiné à héberger une application de production.

### TP 1 — Créer deux backends distincts

**Objectif :** préparer deux réponses différentes permettant de vérifier le routage.

Créez les répertoires :

```bash
mkdir -p /tmp/lb-lab/backend1
mkdir -p /tmp/lb-lab/backend2
```

Créez la page du premier backend :

```bash
printf '<h1>Réponse du Backend 1</h1>\n' \
    > /tmp/lb-lab/backend1/index.html
```

Créez la page du second backend :

```bash
printf '<h1>Réponse du Backend 2</h1>\n' \
    > /tmp/lb-lab/backend2/index.html
```

Vérifiez le contenu :

```bash
cat /tmp/lb-lab/backend1/index.html
cat /tmp/lb-lab/backend2/index.html
```

### TP 2 — Démarrer les applications de test

Lancez ces commandes en tant qu'utilisateur non privilégié.

Premier backend :

```bash
nohup python3 -m http.server 8001 \
    --bind 127.0.0.1 \
    --directory /tmp/lb-lab/backend1 \
    > /tmp/lb-lab/backend1.log 2>&1 &

echo $! > /tmp/lb-lab/backend1.pid
```

Second backend :

```bash
nohup python3 -m http.server 8002 \
    --bind 127.0.0.1 \
    --directory /tmp/lb-lab/backend2 \
    > /tmp/lb-lab/backend2.log 2>&1 &

echo $! > /tmp/lb-lab/backend2.pid
```

Vérifiez les processus :

```bash
ps -ef | grep '[h]ttp.server'
```

Vérifiez les ports :

```bash
ss -lnt | grep -E ':(8001|8002)[[:space:]]'
```

Testez chaque backend directement :

```bash
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8002/
```

Résultat attendu :

- le port 8001 renvoie la page du Backend 1 ;
- le port 8002 renvoie la page du Backend 2.

Si un démarrage échoue, consultez les journaux correspondants.

### TP 3 — Configurer Nginx pour répartir les requêtes

Créez le fichier de configuration :

```bash
sudo nano /etc/nginx/conf.d/lb-lab.conf
```

Contenu :

```nginx
upstream lb_lab_backends {
    server 127.0.0.1:8001 max_fails=2 fail_timeout=5s;
    server 127.0.0.1:8002 max_fails=2 fail_timeout=5s;
}

log_format lb_lab_format
    '$remote_addr "$request" status=$status '
    'upstream=$upstream_addr '
    'upstream_status=$upstream_status '
    'request_time=$request_time '
    'upstream_time=$upstream_response_time';

server {
    listen 127.0.0.1:8080 default_server;
    server_name _;

    access_log /var/log/nginx/lb-lab-access.log lb_lab_format;
    error_log  /var/log/nginx/lb-lab-error.log;

    location / {
        proxy_pass http://lb_lab_backends;

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

Vérifiez que le fichier est chargé par la configuration principale de Nginx. Vérifiez aussi qu'aucune autre configuration n'essaie de définir un serveur incompatible sur la même adresse et le même port.

Testez la syntaxe :

```bash
sudo nginx -t
```

Rechargez Nginx :

```bash
sudo systemctl reload nginx
```

### TP 4 — Vérifier la répartition de charge

Exécutez dix requêtes :

```bash
for i in $(seq 1 10); do
    curl -s http://127.0.0.1:8080/
    echo
done
```

Les réponses doivent montrer que les requêtes sont dirigées vers les deux backends lorsque les deux sont disponibles et que les paramètres de groupe autorisent cette répartition.

### TP 5 — Observer le backend utilisé

Examinez le journal :

```bash
sudo tail -n 30 /var/log/nginx/lb-lab-access.log
```

Recherchez les champs :

```text
upstream=
upstream_status=
request_time=
upstream_time=
```

Ils permettent notamment de comprendre quel backend a été utilisé et quel statut lui est associé.

Les journaux des deux processus Python peuvent également montrer les requêtes reçues :

```bash
tail -f /tmp/lb-lab/backend1.log
```

Dans un autre terminal :

```bash
tail -f /tmp/lb-lab/backend2.log
```

Quittez le suivi des journaux avec `Ctrl+C`.

### TP 6 — Simuler l'indisponibilité d'un backend

Identifiez le processus du premier backend :

```bash
cat /tmp/lb-lab/backend1.pid
```

Arrêtez-le :

```bash
kill "$(cat /tmp/lb-lab/backend1.pid)"
```

Testez à nouveau le proxy :

```bash
for i in $(seq 1 10); do
    curl -sS --max-time 5 http://127.0.0.1:8080/
    echo
done
```

Selon les paramètres de reprise et les échecs observés, certaines requêtes pourront échouer pendant le changement d'état du backend. Le laboratoire ne simule pas un dispositif de contrôle actif, mais permet d'étudier l'effet d'une cible qui ne répond plus.

Examinez les journaux Nginx pour comprendre le comportement observé.

### TP 7 — Rétablir le backend

Redémarrez le premier serveur de test :

```bash
nohup python3 -m http.server 8001 \
    --bind 127.0.0.1 \
    --directory /tmp/lb-lab/backend1 \
    > /tmp/lb-lab/backend1.log 2>&1 &

echo $! > /tmp/lb-lab/backend1.pid
```

Attendez que le processus soit effectivement prêt, puis envoyez plusieurs requêtes et observez si le trafic revient vers ce backend.

Le retour au trafic normal dépend du mécanisme de détection, des paramètres de répartition et des requêtes qui sont réellement envoyées.

### TP 8 — Nettoyer le laboratoire

Arrêtez les processus de test lorsqu'ils ne sont plus nécessaires :

```bash
kill "$(cat /tmp/lb-lab/backend1.pid)" 2>/dev/null || true
kill "$(cat /tmp/lb-lab/backend2.pid)" 2>/dev/null || true
```

Désactivez ou supprimez ensuite le fichier de configuration de laboratoire avec précaution.

Si vous le supprimez, vérifiez de nouveau la configuration avant de recharger le service :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Ne supprimez jamais des fichiers de configuration de production simplement parce qu'ils ressemblent à ceux du laboratoire.


## 24. Exercices de compréhension avec corrigés

### Exercice 1 — Reverse proxy ou proxy direct ?

Un navigateur envoie ses requêtes à Nginx, qui les transmet ensuite à une application interne.

**Question :** s'agit-il d'un proxy direct ou d'un reverse proxy ?

**Corrigé :** il s'agit d'un reverse proxy car Nginx est placé du côté du service pour organiser les requêtes entrantes.

### Exercice 2 — Répartition de charge

Deux serveurs applicatifs reçoivent du trafic par l'intermédiaire de Nginx.

**Question :** quelle configuration Nginx permet de déclarer le groupe de serveurs ?

**Corrigé :** un bloc `upstream` qui déclare les membres, puis une directive `proxy_pass` qui utilise le nom du groupe.

### Exercice 3 — Choix de l'algorithme

Trois serveurs ont des capacités comparables, et les requêtes ont des durées relativement proches.

**Question :** quelle méthode constitue un bon point de départ ?

**Corrigé :** le round robin, méthode par défaut du groupe upstream Nginx lorsque rien d'autre n'est configuré.

### Exercice 4 — Serveurs de capacités différentes

Un serveur a une capacité approximativement deux fois supérieure à celle d'un second serveur.

**Question :** quel paramètre permet d'accorder une part relative plus importante au premier serveur ?

**Corrigé :** le paramètre `weight`, en tenant compte du fait que la part de requêtes n'est pas une mesure exacte de l'utilisation des ressources.

### Exercice 5 — Erreur 502

Le proxy renvoie une erreur 502 immédiatement après une modification de configuration.

**Question :** quels contrôles effectuer en premier ?

**Corrigé :** vérifier le statut de l'application, son adresse et son port, la possibilité de l'atteindre directement, puis les journaux du proxy et de l'application.

### Exercice 6 — Erreur 504

Le backend fonctionne, mais une opération très lente provoque une erreur 504.

**Question :** faut-il simplement augmenter tous les délais ?

**Corrigé :** non. Il faut mesurer les temps observés, rechercher les blocages de l'application ou de ses dépendances, puis adapter les délais en fonction du service.

### Exercice 7 — `X-Forwarded-For`

Un utilisateur peut envoyer lui-même un en-tête `X-Forwarded-For`.

**Question :** pourquoi une application ne doit-elle pas lui faire confiance automatiquement ?

**Corrigé :** parce que l'en-tête peut avoir été fourni ou modifié par un client non fiable. L'application doit connaître les proxies autorisés et suivre une politique claire de confiance.

### Exercice 8 — Persistance

Une application stocke ses sessions uniquement en mémoire dans chaque instance.

**Question :** pourquoi la répartition peut-elle provoquer la perte d'une session apparente ?

**Corrigé :** parce que deux requêtes du même utilisateur peuvent arriver sur des instances dont les mémoires de session sont différentes. Un stockage partagé ou une stratégie de persistance adaptée est nécessaire.

### Exercice 9 — HTTPS

Le client utilise HTTPS vers Nginx, mais le backend reçoit une requête HTTP.

**Question :** comment l'application peut-elle comprendre que le client utilisait HTTPS ?

**Corrigé :** le proxy peut transmettre des informations de schéma, notamment `X-Forwarded-Proto`, et l'application doit être configurée pour ne faire confiance à cet en-tête que lorsqu'il provient d'un proxy approuvé.

### Exercice 10 — Reprise d'une requête

Une application effectue une opération de paiement puis perd la connexion avant d'envoyer sa réponse.

**Question :** pourquoi le proxy ne doit-il pas nécessairement réessayer aveuglément cette requête sur un autre serveur ?

**Corrigé :** parce que l'opération peut déjà avoir été exécutée. Une nouvelle tentative peut provoquer un doublon, sauf si l'application dispose de mécanismes adaptés, par exemple une gestion sûre de l'idempotence.


## 25. Défi final : publier une application résiliente

### Objectif

Créer une configuration Nginx qui répartit le trafic entre deux backends et permet d'observer le comportement du proxy lorsqu'une instance tombe en panne.

### Cahier des charges

L'architecture doit comprendre :

```text
Client local
     |
     v
Nginx : 127.0.0.1:8080
     |
     +-----------> Backend 1 : 127.0.0.1:8001
     |
     +-----------> Backend 2 : 127.0.0.1:8002
```

Les exigences sont les suivantes :

- le proxy utilise un groupe `upstream` ;
- les deux backends possèdent des contenus différents ;
- la requête est transmise au bon groupe ;
- les en-têtes transmis à l'application sont explicitement définis ;
- les délais d'attente sont configurés ;
- les journaux permettent d'identifier le backend et le statut ;
- la configuration est testée avant rechargement ;
- l'arrêt d'un backend est simulé ;
- le comportement lors d'une panne est documenté ;
- le backend est remis en service puis le fonctionnement est vérifié.

### Étape 1 — Écrire le groupe de backends

Créez ou adaptez le groupe :

```nginx
upstream application_backend {
    server 127.0.0.1:8001 max_fails=2 fail_timeout=5s;
    server 127.0.0.1:8002 max_fails=2 fail_timeout=5s;
}
```

### Étape 2 — Configurer le proxy

Configurez l'écoute, les en-têtes, les délais et les journaux de façon cohérente avec le laboratoire précédent.

### Étape 3 — Tester avant l'activation

```bash
sudo nginx -t
```

### Étape 4 — Vérifier le service

```bash
sudo systemctl reload nginx
sudo systemctl status nginx
```

### Étape 5 — Tester la répartition

```bash
for i in $(seq 1 20); do
    curl -sS --max-time 5 http://127.0.0.1:8080/
    echo
done
```

### Étape 6 — Simuler une panne et analyser le résultat

Arrêtez un backend, envoyez à nouveau des requêtes, puis examinez :

```bash
sudo tail -n 50 /var/log/nginx/lb-lab-access.log
sudo tail -n 50 /var/log/nginx/lb-lab-error.log
```

Identifiez quelles requêtes échouent, lesquelles réussissent et comment Nginx journalise les serveurs upstream.

### Étape 7 — Rédiger un bilan

Le bilan doit répondre aux questions suivantes :

- Les deux backends ont-ils reçu du trafic avant la panne ?
- Que se passe-t-il immédiatement après l'arrêt d'une instance ?
- Les autres requêtes continuent-elles à être traitées ?
- Quels messages apparaissent dans les journaux ?
- Le trafic revient-il vers le backend après sa remise en service ?
- Quels seraient les risques si l'application ne pouvait pas traiter une requête sur n'importe quelle instance ?

### Critères de réussite

Le défi est réussi si :

- les deux backends répondent individuellement ;
- Nginx transmet les requêtes au groupe configuré ;
- plusieurs backends reçoivent des requêtes ;
- les configurations sont valides ;
- les journaux permettent un diagnostic ;
- le comportement lors d'une panne a été observé ;
- le retour en service a été testé ;
- les limites de la stratégie de reprise sont comprises.

Le résultat du laboratoire ne doit pas être assimilé à une garantie de haute disponibilité en production. Il démontre le comportement local du reverse proxy dans les conditions testées.


## 26. Les pièges fréquents à éviter

### 26.1 Un seul proxy pour plusieurs backends

Plusieurs backends améliorent la capacité et peuvent permettre de continuer à servir des requêtes lorsqu'un backend tombe en panne.

Mais si l'unique reverse proxy tombe, toutes les requêtes qui passent par lui peuvent échouer.

```text
Client
  |
  v
Proxy unique  <-- Point de défaillance possible
  |
  +--> Backend 1
  |
  +--> Backend 2
```

Pour une architecture hautement disponible, il faut également considérer la redondance du point d'entrée et la façon dont les clients y accèdent.

### 26.2 Utiliser `ip_hash` comme substitut au stockage partagé

Une affectation fondée sur l'adresse IP peut faciliter certaines formes d'affinité. Elle ne constitue pas un stockage fiable de session et ne protège pas contre la perte de l'instance.

### 26.3 Croire que le load balancing rend l'application stateless

La répartition de charge ne transforme pas automatiquement l'application en application sans état. Il faut examiner les sessions, les fichiers locaux, les connexions de base de données et toute donnée mémorisée dans une instance.

### 26.4 Modifier les délais pour masquer un problème applicatif

Une erreur 504 peut révéler un traitement trop lent, une requête de base de données bloquée ou une dépendance indisponible. Des délais plus longs peuvent simplement prolonger l'attente.

### 26.5 Laisser les backends directement accessibles

Si l'architecture prévoit que toutes les requêtes passent par le proxy, l'accès direct aux applications peut contourner certaines protections. Le contrôle réseau doit correspondre à cette intention.

### 26.6 Réessayer toutes les requêtes sans distinction

Les opérations non idempotentes peuvent être exécutées plus d'une fois si le résultat d'une tentative est incertain. La politique de reprise doit prendre en compte les garanties applicatives.

### 26.7 Négliger les en-têtes de redirection

Une application peut renvoyer une URL interne dans une réponse de redirection. Il faut vérifier si les en-têtes sont correctement adaptés et si l'application connaît son URL publique.

### 26.8 Confondre réponse HTTP et état de santé

Un backend peut renvoyer HTTP 200 tout en étant incapable d'effectuer une opération essentielle, par exemple parce qu'une dépendance critique est en panne. La définition d'une sonde doit représenter l'état que l'on cherche réellement à vérifier.


## 27. Checklist d'exploitation

Avant de valider une architecture reverse proxy, vérifiez les éléments suivants.

### Configuration

- [ ] Le nom d'hôte et le port d'écoute correspondent à l'environnement.
- [ ] Les backends attendus sont correctement déclarés.
- [ ] Les chemins et les préfixes sont cohérents.
- [ ] Les en-têtes transmis sont explicitement définis.
- [ ] Les configurations ont passé le test de syntaxe.
- [ ] Les paramètres spécifiques à la version installée ont été vérifiés.

### Disponibilité

- [ ] Le comportement en cas de panne d'un backend a été testé.
- [ ] Les seuils et périodes de détection sont cohérents.
- [ ] Les nouveaux essais sont adaptés au type de requête.
- [ ] Le rôle et les limites des mécanismes de santé sont compris.
- [ ] Le point d'entrée du reverse proxy n'est pas ignoré dans l'analyse des risques de panne.

### Sécurité

- [ ] Les backends sont accessibles uniquement depuis les zones autorisées.
- [ ] Le proxy n'est pas ouvert à des destinations arbitraires.
- [ ] Les en-têtes de proxy proviennent de sources de confiance.
- [ ] Les certificats TLS et leurs clés sont protégés.
- [ ] Le chiffrement du trafic interne est adapté au réseau.
- [ ] Les routes d'administration ne sont pas publiées inutilement.

### Observabilité

- [ ] Les journaux d'accès sont disponibles.
- [ ] Le backend ayant traité une requête peut être identifié.
- [ ] Les erreurs 502 et 504 peuvent être analysées.
- [ ] Les délais sont mesurés, pas simplement devinés.
- [ ] Les journaux sont protégés et font l'objet d'une rotation adaptée.


## 28. Fiche de révision rapide

### Nginx — Reverse proxy

```nginx
location / {
    proxy_pass http://127.0.0.1:8001;

    proxy_http_version 1.1;
    proxy_set_header Connection "";

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Nginx — Load balancing

```nginx
upstream application_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 127.0.0.1:8080;

    location / {
        proxy_pass http://application_backend;
    }
}
```

### Nginx — Méthode least connections

```nginx
upstream application_backend {
    least_conn;

    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### Nginx — Poids

```nginx
upstream application_backend {
    server 127.0.0.1:8001 weight=3;
    server 127.0.0.1:8002 weight=1;
}
```

### Nginx — Vérification et rechargement

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status nginx
```

### Apache — Reverse proxy

```apache
ProxyRequests Off
ProxyPreserveHost On

ProxyPass        "/" "http://127.0.0.1:8001/"
ProxyPassReverse "/" "http://127.0.0.1:8001/"
```

### Apache — Load balancing

```apache
<Proxy "balancer://application_cluster">
    BalancerMember "http://127.0.0.1:8001"
    BalancerMember "http://127.0.0.1:8002"

    ProxySet lbmethod=byrequests
</Proxy>

ProxyPass        "/" "balancer://application_cluster/"
ProxyPassReverse "/" "balancer://application_cluster/"
```

### Apache — Test

Sur Debian et Ubuntu :

```bash
sudo apachectl configtest
sudo apachectl -S
sudo systemctl reload apache2
```

### Diagnostic réseau

```bash
sudo ss -lntp
curl -v http://127.0.0.1:8080/
sudo journalctl -u nginx -n 50
```


## 29. Glossaire

**Backend** : serveur ou application qui traite les requêtes transmises par le proxy.

**Balancer** : composant qui choisit un serveur parmi un groupe afin de répartir la charge.

**Failover** : passage vers une autre ressource lorsqu'une ressource initiale devient indisponible, selon les mécanismes prévus.

**Health check** : contrôle destiné à évaluer la disponibilité ou l'état de préparation d'un service.

**Load balancing** : répartition des requêtes ou du trafic entre plusieurs serveurs.

**Least connections** : méthode de répartition qui privilégie le serveur ayant le moins de connexions actives, en tenant compte des paramètres de la méthode.

**Reverse proxy** : serveur intermédiaire qui reçoit les requêtes clientes et les transmet à des services en amont.

**Round robin** : méthode de répartition qui distribue les requêtes successivement entre les membres d'un groupe.

**Sticky session** : stratégie qui cherche à maintenir un client sur une même instance pendant une période ou une session.

**TLS termination** : terminaison d'une connexion TLS sur un équipement, comme un reverse proxy.

**Upstream** : serveur ou groupe de serveurs vers lequel un proxy transmet des requêtes.

**Weighted round robin** : répartition de type round robin qui prend en compte des poids configurés pour les serveurs.

**X-Forwarded-For** : en-tête couramment utilisé pour transmettre des informations sur l'adresse du client et la chaîne de proxies.

**X-Forwarded-Proto** : en-tête couramment utilisé pour indiquer le schéma externe de la requête, par exemple HTTP ou HTTPS.

**502 Bad Gateway** : erreur indiquant qu'une passerelle ou un proxy n'a pas obtenu une réponse amont qu'il peut traiter correctement.

**504 Gateway Timeout** : erreur indiquant qu'une passerelle ou un proxy n'a pas reçu à temps une réponse du serveur en amont.


## 30. Documentation officielle

Pour approfondir les paramètres et vérifier leur disponibilité selon la version du logiciel utilisé, consultez les documentations officielles.

### Nginx

- Guide officiel du load balancing HTTP :  
  https://nginx.org/en/docs/http/load_balancing.html

- Module `ngx_http_upstream_module` :  
  https://nginx.org/en/docs/http/ngx_http_upstream_module.html

- Module `ngx_http_proxy_module` :  
  https://nginx.org/en/docs/http/ngx_http_proxy_module.html

- Configuration HTTPS :  
  https://nginx.org/en/docs/http/configuring_https_servers.html

- Documentation générale :  
  https://nginx.org/en/docs/

### Apache HTTP Server

- Guide officiel du reverse proxy :  
  https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html

- Module `mod_proxy` :  
  https://httpd.apache.org/docs/2.4/mod/mod_proxy.html

- Module `mod_proxy_balancer` :  
  https://httpd.apache.org/docs/2.4/mod/mod_proxy_balancer.html

- Méthode de répartition `byrequests` :  
  https://httpd.apache.org/docs/2.4/mod/mod_lbmethod_byrequests.html

- Configuration TLS :  
  https://httpd.apache.org/docs/2.4/ssl/


## Conclusion

Le reverse proxy et le load balancing permettent de structurer une infrastructure Web en séparant le point d'entrée public des applications qui traitent les requêtes.

Nginx et Apache peuvent assurer ces fonctions, avec des syntaxes et des mécanismes de configuration différents.

La compétence essentielle ne consiste pas seulement à déclarer deux backends. Elle consiste aussi à comprendre le comportement de la répartition, les conséquences d'une panne, les limites des reprises automatiques, les en-têtes transmis aux applications, les temps d'attente et les informations nécessaires au diagnostic.

Le parcours recommandé est le suivant :

```text
Reverse proxy simple
        |
        v
Groupe de serveurs applicatifs
        |
        v
Algorithmes de répartition
        |
        v
Gestion des erreurs et des reprises
        |
        v
En-têtes et confiance entre proxies
        |
        v
TLS et configuration des applications
        |
        v
Logs et observabilité
        |
        v
Tests de panne et validation
```

Avant de passer à la mise en production, il reste indispensable d'étudier la supervision, les déploiements sans interruption, la redondance du point d'entrée, la gestion des certificats, la sécurité réseau et la conception d'applications capables de fonctionner correctement sur plusieurs instances.