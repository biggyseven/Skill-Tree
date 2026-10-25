# Serveurs Web : Nginx et Apache

## 1. Présentation générale

Un serveur Web est un logiciel qui reçoit des requêtes provenant de clients, généralement des navigateurs Web, puis leur renvoie des ressources ou transmet leurs demandes à une application.

Nginx et Apache HTTP Server sont deux des logiciels utilisés pour publier des sites Web, héberger des applications et distribuer du contenu sur un réseau.

Ce cours permet d'apprendre à installer, configurer, démarrer, tester et sécuriser les premières instances de ces deux serveurs sous Linux.

### 1.1 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- expliquer le rôle d'un serveur Web ;
- différencier un serveur Web, un navigateur, un serveur DNS et une application ;
- comprendre le fonctionnement élémentaire de HTTP et HTTPS ;
- identifier les différences fondamentales entre Nginx et Apache ;
- installer Nginx ou Apache sur une distribution Linux ;
- gérer les services avec `systemctl` ;
- publier un site Web statique ;
- configurer un hôte virtuel avec Apache ou un bloc `server` avec Nginx ;
- tester une configuration avant de l'activer ;
- consulter les journaux d'accès et d'erreurs ;
- diagnostiquer les erreurs HTTP les plus courantes ;
- appliquer les premières règles de sécurité ;
- réaliser un petit déploiement Web reproductible.

### 1.2 Prérequis

Vous devez posséder les connaissances élémentaires suivantes :

- savoir utiliser un terminal Linux ;
- connaître les commandes `ls`, `cd`, `cat`, `mkdir` et `nano` ;
- comprendre les chemins absolus comme `/var/www/html` ;
- savoir utiliser `sudo` pour effectuer des opérations administratives ;
- connaître les bases des adresses IP et des ports réseau.

Les exemples utilisent principalement Debian et Ubuntu. Les équivalents pour les distributions de la famille Red Hat sont également présentés.

### 1.3 Environnement de travail recommandé

Pour apprendre sans risquer de perturber un serveur utilisé en production, utilisez une machine virtuelle Linux.

Architecture du laboratoire :

```text
+----------------------------------------------------------+
|                  MACHINE DE FORMATION                    |
|                                                          |
|  +----------------------+                                |
|  | Navigateur Web       |                                |
|  | ou commande curl     |                                |
|  +----------+-----------+                                |
|             |                                            |
|             | Requête HTTP                               |
|             |                                            |
|             v                                            |
|  +----------------------+                                |
|  | Serveur Linux        |                                |
|  |                      |                                |
|  | Nginx OU Apache      |                                |
|  | Port TCP 80          |                                |
|  +----------+-----------+                                |
|             |                                            |
|             v                                            |
|  +----------------------+                                |
|  | Fichiers du site     |                                |
|  | /var/www/...         |                                |
|  +----------------------+                                |
+----------------------------------------------------------+
```

Vous pouvez commencer avec une seule machine Linux. Le client et le serveur peuvent être sur la même machine.

**Règle importante :** Nginx et Apache peuvent être installés sur une même machine, mais ils ne peuvent normalement pas écouter simultanément sur la même adresse IP et le même port TCP. Pour les premières manipulations, étudiez-les séparément.


## 2. Comprendre le fonctionnement du Web

### 2.1 Qu'est-ce qu'un client Web ?

Le client est le logiciel qui initie une requête.

Il peut s'agir de :

- Google Chrome ;
- Firefox ;
- Microsoft Edge ;
- un programme utilisant une bibliothèque HTTP ;
- la commande `curl` sous Linux.

Le client demande une ressource identifiée par une URL.

Exemple :

```text
http://www.exemple.test/index.html
```

Décomposition :

```text
http://www.exemple.test/index.html
  |            |              |
  |            |              +---- Chemin de la ressource
  |            |
  |            +------------------- Nom d'hôte
  |
  +-------------------------------- Protocole
```

Une URL peut également contenir un port explicite, des paramètres ou d'autres éléments.

Exemple :

```text
http://192.0.2.10:8080/catalogue?id=15
```

- `http` : protocole utilisé ;
- `192.0.2.10` : adresse IP de destination ;
- `8080` : port de destination ;
- `/catalogue` : chemin demandé ;
- `id=15` : paramètre de requête.

L'adresse IP `192.0.2.10` appartient à une plage réservée à la documentation : cet exemple est fictif.

### 2.2 Qu'est-ce qu'un serveur Web ?

Le serveur Web est le logiciel qui accepte les connexions HTTP ou HTTPS et traite les requêtes correspondantes.

Lorsqu'un client demande un fichier HTML, le serveur peut le lire dans son répertoire de publication et renvoyer son contenu.

```text
CLIENT                                      SERVEUR WEB
  |                                              |
  |  GET /index.html HTTP/1.1                    |
  |--------------------------------------------->|
  |                                              |
  |                    Recherche du fichier      |
  |                    /var/www/site/index.html  |
  |                                              |
  |  HTTP/1.1 200 OK                             |
  |<---------------------------------------------|
  |  Contenu HTML                                |
  |                                              |
```

Le serveur Web ne se limite pas à envoyer des fichiers. Selon sa configuration, il peut également :

- sélectionner un site parmi plusieurs ;
- vérifier certaines autorisations ;
- transmettre une requête à une application ;
- servir les fichiers statiques comme les images, CSS et JavaScript ;
- gérer des connexions HTTPS ;
- enregistrer les requêtes et les erreurs dans des journaux.

### 2.3 Le rôle du DNS

Le DNS permet normalement de traduire un nom d'hôte en une ou plusieurs adresses IP.

Par exemple :

```text
Navigateur
    |
    | Demande : quelle est l'adresse de www.exemple.com ?
    v
Résolution DNS
    |
    | Réponse : adresse IP
    v
Connexion au serveur Web
```

Il faut distinguer deux opérations :

1. Le DNS aide le client à trouver l'adresse IP correspondant au nom demandé.
2. Le serveur Web utilise notamment le nom d'hôte communiqué dans la requête pour choisir le site approprié.

Le DNS n'envoie pas lui-même les pages Web.

Pour un laboratoire local, il est possible de tester un nom sans créer un enregistrement DNS public. Des méthodes seront présentées plus loin.

### 2.4 Le rôle de TCP

HTTP utilise une connexion de transport pour communiquer. Dans les configurations Web classiques étudiées ici, il s'agit de TCP.

Les ports les plus courants sont :

| Port TCP | Utilisation habituelle |
|---|---|
| 80 | HTTP |
| 443 | HTTPS |
| 8080 | Port alternatif fréquemment utilisé en test |
| 8443 | Port alternatif fréquemment utilisé pour HTTPS en test |

Les ports 8080 et 8443 ne remplacent pas automatiquement les ports standards. Ils doivent être configurés explicitement côté serveur et côté client.

### 2.5 HTTP et HTTPS

HTTP définit la manière dont un client demande une ressource et dont le serveur lui répond.

HTTPS ajoute une protection TLS à la communication HTTP. Cette protection permet notamment de chiffrer les échanges et de vérifier l'identité du serveur au moyen d'un certificat correctement validé.

```text
HTTP
Client ===== Requête et réponse HTTP ===== Serveur

HTTPS
Client ===== Connexion TLS + HTTP ======== Serveur
                    |
                    +-- Chiffrement
                    +-- Intégrité des échanges
                    +-- Vérification du certificat
```

HTTP seul ne protège pas la confidentialité des données échangées. Pour un site public en production, HTTPS est généralement indispensable.


## 3. Comprendre les requêtes et réponses HTTP

### 3.1 Les méthodes HTTP

La méthode indique l'opération demandée au serveur.

| Méthode | Rôle fréquent |
|---|---|
| `GET` | Obtenir une ressource |
| `HEAD` | Obtenir les en-têtes sans le corps de la réponse |
| `POST` | Envoyer des données, par exemple un formulaire |
| `PUT` | Créer ou remplacer une ressource selon l'application |
| `PATCH` | Modifier partiellement une ressource |
| `DELETE` | Demander la suppression d'une ressource |

Une méthode ne détermine pas, à elle seule, si l'action est autorisée. L'application et les règles d'accès doivent également contrôler la demande.

Pour tester un site, `GET` et `HEAD` sont particulièrement utiles.

### 3.2 Les codes de statut

Le statut HTTP indique le résultat de traitement de la requête.

| Code | Signification |
|---|---|
| `200 OK` | Requête traitée avec succès |
| `201 Created` | Une ressource a été créée |
| `301 Moved Permanently` | Redirection permanente |
| `302 Found` | Redirection temporaire |
| `304 Not Modified` | La ressource peut être réutilisée depuis le cache |
| `400 Bad Request` | Requête incorrecte |
| `401 Unauthorized` | Authentification requise ou refusée |
| `403 Forbidden` | Accès interdit |
| `404 Not Found` | Ressource introuvable |
| `405 Method Not Allowed` | Méthode non autorisée sur la ressource |
| `413 Content Too Large` | Contenu envoyé trop volumineux |
| `429 Too Many Requests` | Trop de requêtes selon la politique appliquée |
| `500 Internal Server Error` | Erreur interne du serveur ou de l'application |
| `502 Bad Gateway` | Réponse invalide reçue d'un serveur en amont |
| `503 Service Unavailable` | Service indisponible |
| `504 Gateway Timeout` | Délai d'attente dépassé auprès d'un serveur en amont |

Les statuts sont regroupés en familles :

```text
1xx  Information
2xx  Succès
3xx  Redirection
4xx  Problème lié à la requête ou à son accès
5xx  Erreur de traitement ou d'un serveur
```

Un `404` ne signifie pas nécessairement que le serveur est arrêté. Il peut fonctionner normalement tout en ne trouvant pas le fichier demandé.

Un `502` est fréquent lorsqu'un serveur Web joue le rôle de reverse proxy et ne parvient pas à obtenir une réponse valide de l'application en amont.

### 3.3 Lire une réponse HTTP avec curl

La commande `curl` permet d'envoyer une requête depuis le terminal.

```bash
curl -I http://127.0.0.1/
```

Cette commande demande les en-têtes HTTP. Elle permet notamment de voir le code de réponse et certains en-têtes.

Pour afficher les en-têtes et le contenu :

```bash
curl -i http://127.0.0.1/
```

Pour afficher des informations détaillées sur la connexion :

```bash
curl -v http://127.0.0.1/
```

Pour limiter l'affichage au code de statut :

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1/
```

Un code `000` avec cette dernière méthode signifie généralement que `curl` n'a pas obtenu de réponse HTTP exploitable, par exemple parce que la connexion a échoué. Il faut alors consulter le message d'erreur détaillé.


## 4. Présentation de Nginx

### 4.1 Qu'est-ce que Nginx ?

Nginx est un serveur Web qui peut également servir de reverse proxy, de répartiteur de charge ou de point d'entrée HTTP/HTTPS devant une application.

Il est notamment utilisé pour :

- fournir des fichiers statiques ;
- accepter des connexions de nombreux clients ;
- transmettre des requêtes à des applications ;
- centraliser l'entrée HTTP/HTTPS de plusieurs services.

Nginx utilise une architecture comportant un processus maître et des processus de travail. Le processus maître lit et contrôle la configuration ainsi que les processus de travail. Ces derniers assurent le traitement des requêtes.

Représentation simplifiée :

```text
                    NGINX
                      |
          +-----------+-----------+
          |                       |
          v                       v
   Processus maître        Processus de travail
   - lit la config         - reçoit les requêtes
   - gère les workers      - traite les connexions
          |                       |
          +-----------------------+
```

Cette représentation est volontairement simplifiée. Le nombre de processus et leur fonctionnement dépendent de la configuration et de l'environnement.

### 4.2 Les principaux chemins de configuration

Sur Debian et Ubuntu, on rencontre couramment :

```text
/etc/nginx/
|
+-- nginx.conf
|
+-- sites-available/
|      |
|      +-- default
|      +-- site1
|
+-- sites-enabled/
|      |
|      +-- lien vers les configurations activées
|
+-- conf.d/
```

Le fichier `/etc/nginx/nginx.conf` contient la configuration principale. Il peut inclure d'autres fichiers, dont ceux déclarés dans `sites-enabled` ou `conf.d`.

Les distributions n'organisent pas toutes les fichiers de la même manière. Sur les systèmes où le répertoire `sites-enabled` n'est pas utilisé, des configurations dans `/etc/nginx/conf.d/` sont fréquentes.

**Il faut toujours vérifier les directives `include` du fichier principal avant de supposer qu'un fichier sera chargé.**

### 4.3 Les blocs essentiels de Nginx

Une configuration Nginx peut contenir plusieurs contextes :

- `events` : paramètres de gestion des connexions ;
- `http` : paramètres globaux au traitement HTTP ;
- `server` : configuration d'un serveur virtuel ;
- `location` : traitement associé à un chemin de requête.

Exemple conceptuel :

```text
nginx.conf
    |
    +-- events
    |
    +-- http
           |
           +-- paramètres HTTP communs
           |
           +-- server
                  |
                  +-- server_name
                  +-- listen
                  +-- root
                  +-- location
```

Les directives et les contextes doivent être correctement placés. Une directive ne peut pas être insérée arbitrairement dans n'importe quel bloc.

### 4.4 Les directives fondamentales

| Directive | Fonction |
|---|---|
| `listen` | Indique l'adresse ou le port d'écoute |
| `server_name` | Déclare les noms d'hôte associés au serveur |
| `root` | Définit le répertoire racine utilisé pour construire le chemin d'un fichier |
| `index` | Définit les noms de fichiers index recherchés par défaut |
| `location` | Définit des règles de traitement pour des URI |
| `try_files` | Vérifie l'existence de fichiers ou répertoires selon l'ordre défini |
| `access_log` | Configure le journal d'accès |
| `error_log` | Configure le journal d'erreurs |

Dans Nginx, le chemin de la ressource est généralement construit à partir de la directive `root` et de l'URI. La directive `alias` obéit à une logique différente : elle remplace la portion de chemin correspondant au `location`.

À ce stade, concentrez-vous sur `root`, `index`, `server_name`, `listen` et `location`.


## 5. Présentation d'Apache HTTP Server

### 5.1 Qu'est-ce qu'Apache ?

Apache HTTP Server, souvent appelé simplement Apache ou `httpd`, est un serveur Web modulaire qui existe depuis de nombreuses années.

Il peut notamment :

- servir des fichiers statiques ;
- héberger plusieurs sites ;
- appliquer des contrôles d'accès ;
- charger des modules ;
- transmettre des requêtes à certaines applications ;
- gérer HTTPS grâce à des modules adaptés.

Apache dispose d'une architecture modulaire. Ses capacités peuvent être étendues selon les besoins et les modules chargés.

### 5.2 Les chemins courants sous Debian et Ubuntu

```text
/etc/apache2/
|
+-- apache2.conf
|
+-- ports.conf
|
+-- sites-available/
|      |
|      +-- 000-default.conf
|      +-- site1.conf
|
+-- sites-enabled/
|      |
|      +-- liens vers les sites activés
|
+-- mods-available/
|
+-- mods-enabled/
|
+-- conf-available/
|
+-- conf-enabled/
```

Le fichier `apache2.conf` est la configuration principale. Les directives `Include` et `IncludeOptional` permettent de charger d'autres fichiers.

Sur Debian et Ubuntu, `a2ensite`, `a2dissite`, `a2enmod` et `a2dismod` servent respectivement à activer ou désactiver les sites et les modules dans les installations qui utilisent cette organisation.

### 5.3 Les chemins courants sous Red Hat, Rocky Linux et AlmaLinux

L'organisation est généralement différente :

```text
/etc/httpd/
|
+-- conf/
|     |
|     +-- httpd.conf
|
+-- conf.d/
      |
      +-- site1.conf
```

Le service est généralement appelé `httpd` sur ces distributions.

N'appliquez donc pas aveuglément les commandes `a2ensite` ou les chemins `/etc/apache2/sites-available` à une installation qui ne les utilise pas.

### 5.4 Les directives fondamentales d'Apache

| Directive | Fonction |
|---|---|
| `Listen` | Configure les ports ou adresses d'écoute |
| `<VirtualHost>` | Définit un hôte virtuel |
| `ServerName` | Définit le nom principal du site |
| `ServerAlias` | Ajoute des noms supplémentaires |
| `DocumentRoot` | Définit le répertoire des documents publiés |
| `DirectoryIndex` | Définit les noms de fichiers index |
| `<Directory>` | Applique des règles à un répertoire physique |
| `Require` | Définit des conditions d'autorisation |
| `ErrorLog` | Configure le journal d'erreurs |
| `CustomLog` | Configure le journal d'accès |
| `Options` | Définit diverses options d'accès aux répertoires |

Un bloc `<VirtualHost *:80>` configure un hôte virtuel associé au port 80 sur les adresses concernées. La sélection entre plusieurs sites peut notamment se faire selon le nom d'hôte.

Les règles dans `<Directory>` concernent un chemin de répertoire sur le système de fichiers. Elles ne sont pas équivalentes à une règle de chemin URL.


## 6. Comparaison entre Nginx et Apache

Les deux logiciels peuvent servir des sites statiques et héberger plusieurs sites sur une même machine. Ils sont tous deux capables de gérer HTTPS et de transmettre des requêtes à des applications.

| Critère | Nginx | Apache |
|---|---|---|
| Fonction principale | Serveur Web et proxy HTTP | Serveur Web modulaire |
| Architecture | Maître et workers, traitement orienté événements | Architecture configurable avec des MPM, dont `event`, `worker` et `prefork` |
| Configuration d'un site | Bloc `server` | Bloc `<VirtualHost>` |
| Règles de chemin URL | Blocs `location` | Directives et sections adaptées, modules selon les besoins |
| Fichier `.htaccess` | Non pris en charge nativement | Pris en charge si autorisé par la configuration |
| Activation des sites sous Debian | Souvent liens dans `sites-enabled` | Souvent `a2ensite` et `a2dissite` |
| Traitement PHP | Habituellement via PHP-FPM ou autre interface d'application | Via PHP-FPM, ou d'autres intégrations selon l'installation |
| Reverse proxy | Pris en charge | Pris en charge |
| Configuration | Directives et contextes Nginx | Directives, contextes et modules Apache |

### 6.1 Quel serveur choisir ?

Le bon choix dépend de l'application, de l'infrastructure, de l'expertise de l'équipe, des extensions nécessaires et des contraintes d'exploitation.

Nginx est fréquemment choisi comme serveur Web et reverse proxy en raison de son modèle de traitement des connexions et de ses fonctions de proxy.

Apache peut être particulièrement adapté lorsqu'une application dépend de ses modules, d'une configuration Apache existante ou de règles `.htaccess` déjà utilisées.

Aucun des deux n'est automatiquement plus rapide ou plus sécurisé dans toutes les situations. Le résultat dépend de la configuration, du trafic, du système, de l'application et du dimensionnement.

### 6.2 Attention à PHP et aux autres langages

Un serveur Web qui renvoie des fichiers HTML, CSS, JavaScript ou des images n'exécute pas automatiquement un programme PHP.

Par exemple, la présence d'un fichier `index.php` ne garantit pas son exécution. Une intégration appropriée, telle que PHP-FPM, doit être installée et configurée.

**Ne publiez jamais un répertoire contenant des sources confidentielles en supposant que le serveur les exécutera ou les protégera automatiquement.** Une configuration incorrecte peut conduire à exposer le contenu de fichiers qui ne devraient pas être accessibles.

La configuration de PHP-FPM et des applications dynamiques constitue un sujet distinct, qui sera étudié après la maîtrise des bases du serveur Web.


## 7. Préparer le système Linux

### 7.1 Vérifier la distribution

```bash
cat /etc/os-release
```

Cette commande affiche les informations relatives au système.

Pour connaître la version du noyau :

```bash
uname -r
```

Pour vérifier si vous disposez des droits administratifs :

```bash
sudo -v
```

### 7.2 Mettre à jour les informations des paquets

Sur Debian ou Ubuntu :

```bash
sudo apt update
```

Cette commande met à jour l'index local des paquets disponibles. Elle n'effectue pas, à elle seule, la mise à niveau de tous les logiciels installés.

Une mise à niveau éventuelle relève d'une opération distincte, qui doit être planifiée correctement sur un serveur en production.

Sur une distribution de la famille Red Hat :

```bash
sudo dnf check-update
```

Cette commande vérifie les mises à jour disponibles. Son code de retour peut être non nul lorsque des mises à jour sont disponibles ; cela ne signifie pas nécessairement une panne.

### 7.3 Vérifier les ports et les services existants

Avant l'installation, regardez si un programme utilise déjà les ports Web.

```bash
sudo ss -lntp
```

Pour rechercher spécifiquement les ports 80 et 443 :

```bash
sudo ss -lntp | grep -E ':(80|443)[[:space:]]'
```

Si aucune ligne ne s'affiche, cela ne prouve pas qu'un port est accessible depuis le réseau. Cela indique simplement qu'aucune ligne correspondante n'a été trouvée dans cette sortie.

Un serveur peut également être bloqué par le pare-feu ou une règle réseau, même si le service écoute localement.


## 8. Installer et gérer Nginx

### 8.1 Installation sur Debian ou Ubuntu

```bash
sudo apt update
sudo apt install nginx
```

Vérifier la version installée :

```bash
nginx -v
```

Afficher la version ainsi que les paramètres de compilation :

```bash
nginx -V
```

Démarrer le service :

```bash
sudo systemctl start nginx
```

Activer son démarrage automatique :

```bash
sudo systemctl enable nginx
```

Démarrer le service et activer simultanément son lancement automatique :

```bash
sudo systemctl enable --now nginx
```

Vérifier son état :

```bash
sudo systemctl status nginx
```

### 8.2 Installation sur une distribution utilisant DNF

Sur une distribution appropriée de la famille Red Hat :

```bash
sudo dnf install nginx
```

Puis :

```bash
sudo systemctl enable --now nginx
sudo systemctl status nginx
```

Les dépôts, versions et paramètres peuvent varier selon la distribution.

### 8.3 Les commandes systemctl à connaître

| Commande | Fonction |
|---|---|
| `systemctl status nginx` | Consulte l'état du service |
| `systemctl start nginx` | Démarre le service |
| `systemctl stop nginx` | Arrête le service |
| `systemctl restart nginx` | Arrête puis redémarre le service |
| `systemctl reload nginx` | Demande au service de recharger sa configuration si cette opération est prise en charge |
| `systemctl enable nginx` | Active le démarrage automatique |
| `systemctl disable nginx` | Désactive le démarrage automatique |
| `systemctl enable --now nginx` | Active le démarrage automatique et démarre le service |

Il faut distinguer `restart` de `reload`.

Un redémarrage arrête et relance le processus de service. Un rechargement permet souvent d'appliquer une nouvelle configuration sans arrêter complètement le service et ses connexions de la même manière.

Avant toute modification, vérifiez la configuration. Ne redémarrez pas inutilement un service en production.

### 8.4 Vérifier que Nginx répond

Depuis le serveur :

```bash
curl -I http://127.0.0.1/
```

Vous pouvez aussi ouvrir dans un navigateur :

```text
http://127.0.0.1/
```

Si la page par défaut s'affiche, le serveur répond localement.

Pour vérifier l'écoute :

```bash
sudo ss -lntp | grep ':80'
```

Pour consulter la configuration compilée et les fichiers chargés :

```bash
sudo nginx -T
```

`nginx -T` affiche l'ensemble de la configuration développée, notamment les fichiers inclus. Examinez sa sortie avant de la partager : elle peut contenir des noms internes, des chemins ou des valeurs sensibles.


## 9. Publier un premier site avec Nginx

### 9.1 Comprendre la racine Web

La racine Web est le répertoire depuis lequel le serveur fournit normalement les fichiers du site configuré.

Sur de nombreuses installations Debian ou Ubuntu, le site par défaut utilise :

```text
/var/www/html
```

Ce chemin n'est pas universel. La valeur effective dépend de la configuration.

Vérifiez les fichiers présents :

```bash
ls -la /var/www/html
```

Pour le premier exercice, nous allons créer une page HTML simple dans un répertoire séparé.

### 9.2 Créer un répertoire pour le site

```bash
sudo mkdir -p /var/www/site1
```

Créer une page HTML :

```bash
sudo nano /var/www/site1/index.html
```

Contenu :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mon premier site</title>
</head>
<body>
    <h1>Bienvenue sur mon site</h1>
    <p>Cette page est servie par Nginx.</p>
</body>
</html>
```

Enregistrez le fichier.

Vous pouvez vérifier son contenu avec :

```bash
sudo cat /var/www/site1/index.html
```

### 9.3 Comprendre les permissions

Le serveur Web doit pouvoir traverser les répertoires du chemin et lire les fichiers à publier.

Examinez les permissions :

```bash
namei -l /var/www/site1/index.html
```

Cette commande affiche les permissions des différents éléments du chemin.

Pour un site statique simple, une configuration courante consiste à rendre les répertoires traversables et les fichiers lisibles par les utilisateurs autorisés à les consulter, sans leur accorder de droits d'écriture inutiles.

Exemple, si les fichiers sont destinés à être lus par le service et que leur administration reste réservée à `root` :

```bash
sudo chown -R root:root /var/www/site1
sudo find /var/www/site1 -type d -exec chmod 755 {} \;
sudo find /var/www/site1 -type f -exec chmod 644 {} \;
```

Ces permissions peuvent convenir à un laboratoire de contenu statique. Elles ne constituent pas une recette universelle pour une application qui doit écrire des fichiers.

**N'utilisez pas `chmod -R 777` pour résoudre un problème de permissions.** Cette commande donnerait des droits d'écriture excessifs et pourrait permettre à des utilisateurs non autorisés de modifier le contenu publié.

### 9.4 Configurer le site

Sur Debian et Ubuntu, créez un fichier :

```bash
sudo nano /etc/nginx/sites-available/site1
```

Configuration :

```nginx
server {
    listen 80;
    listen [::]:80;

    server_name site1.test;

    root /var/www/site1;
    index index.html;

    access_log /var/log/nginx/site1-access.log;
    error_log  /var/log/nginx/site1-error.log;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~ /\. {
        deny all;
    }
}
```

#### Explication de la configuration

- `server` : crée un bloc de serveur virtuel.
- `listen 80` : écoute les requêtes HTTP sur IPv4.
- `listen [::]:80` : écoute sur IPv6 si cette écoute est prise en charge et appropriée.
- `server_name site1.test` : associe le bloc à ce nom d'hôte.
- `root /var/www/site1` : indique le répertoire racine.
- `index index.html` : spécifie le fichier index recherché pour les requêtes de répertoire.
- `access_log` : définit un journal d'accès propre au site.
- `error_log` : définit un journal d'erreurs propre au site.
- `location /` : traite les chemins de requête correspondants.
- `try_files $uri $uri/ =404` : essaie de trouver le fichier ou le répertoire demandé, puis renvoie une erreur 404 si aucun élément correspondant n'existe.
- `location ~ /\.` : bloque les chemins contenant un composant commençant par un point, ce qui évite notamment la publication de fichiers tels que `.env` au travers de cette règle.

La dernière règle est une mesure supplémentaire, pas une garantie générale. Les fichiers confidentiels doivent de préférence rester en dehors de la racine publiée.

### 9.5 Activer le site

Sur une installation qui utilise `sites-available` et `sites-enabled` :

```bash
sudo ln -s /etc/nginx/sites-available/site1 /etc/nginx/sites-enabled/site1
```

Si le lien existe déjà, ne répétez pas la commande aveuglément. Vérifiez d'abord son état.

Vérifiez ensuite toute la configuration :

```bash
sudo nginx -t
```

Un résultat indiquant que la syntaxe est correcte et que le test a réussi signifie que Nginx a accepté la configuration testée.

Si le test échoue, lisez le message d'erreur, corrigez le problème puis relancez le test.

Si un site par défaut utilise des règles qui entrent en conflit avec votre essai, examinez ses paramètres avant de le désactiver. Il n'est pas toujours nécessaire de supprimer ou de désactiver la configuration par défaut.

Une fois le test réussi :

```bash
sudo systemctl reload nginx
```

Contrôlez son état :

```bash
sudo systemctl status nginx
```

### 9.6 Tester le site sans configurer de DNS public

Puisque `site1.test` est un nom de test, il n'est pas nécessaire de l'enregistrer sur un DNS public.

Utilisez :

```bash
curl --resolve site1.test:80:127.0.0.1 http://site1.test/
```

Cette commande demande à `curl` de se connecter à `127.0.0.1` pour l'hôte `site1.test`, sur le port 80, tout en conservant le nom d'hôte dans la requête HTTP.

Elle permet de vérifier le choix du site virtuel sur la même machine.

Pour afficher les seuls en-têtes :

```bash
curl --resolve site1.test:80:127.0.0.1 -I http://site1.test/
```

Résultat attendu : une réponse HTTP réussie, normalement `200 OK`, ainsi que le contenu HTML lorsque le corps est demandé.

Si le résultat n'est pas celui attendu, poursuivez le diagnostic au lieu de supposer que le fichier est nécessairement absent.


## 10. Installer et gérer Apache

### 10.1 Installation sur Debian ou Ubuntu

```bash
sudo apt update
sudo apt install apache2
```

Afficher la version :

```bash
apache2 -v
```

Démarrer le service et activer son lancement automatique :

```bash
sudo systemctl enable --now apache2
```

Vérifier l'état :

```bash
sudo systemctl status apache2
```

Tester la réponse locale :

```bash
curl -I http://127.0.0.1/
```

### 10.2 Installation sur une distribution de la famille Red Hat

Sur les systèmes qui utilisent le paquet `httpd` :

```bash
sudo dnf install httpd
sudo systemctl enable --now httpd
sudo systemctl status httpd
```

La commande suivante peut être utilisée pour tester la réponse locale :

```bash
curl -I http://127.0.0.1/
```

Le nom du service et les chemins de configuration changent selon la distribution.

### 10.3 Les fichiers d'un site Apache

Sur Debian et Ubuntu, les fichiers d'un site sont fréquemment placés dans :

```text
/etc/apache2/sites-available/
```

La configuration du site activé est reliée à :

```text
/etc/apache2/sites-enabled/
```

Le contenu publié se situe souvent sous :

```text
/var/www/
```

Il faut distinguer :

- le fichier de configuration du site ;
- le répertoire qui contient les pages publiées ;
- les journaux du serveur ;
- les fichiers de certificats, si HTTPS est configuré.

### 10.4 Vérifier la configuration Apache

Sur Debian ou Ubuntu :

```bash
sudo apachectl configtest
```

Une réponse `Syntax OK` indique que le test de syntaxe est réussi.

Pour afficher les hôtes virtuels connus :

```bash
sudo apachectl -S
```

Ces deux commandes ne font pas la même chose :

- `configtest` contrôle la syntaxe et certains problèmes de configuration ;
- `-S` aide à comprendre la configuration des hôtes virtuels et leur association aux adresses et ports.

Sur certaines distributions, la commande `httpd` fournit les opérations équivalentes, par exemple :

```bash
sudo httpd -t
sudo httpd -S
```


## 11. Publier un premier site avec Apache

### 11.1 Créer les fichiers du site

Si vous avez déjà créé `/var/www/site1/index.html` dans la partie Nginx, vous pouvez réutiliser ce même fichier.

Sinon :

```bash
sudo mkdir -p /var/www/site1
sudo nano /var/www/site1/index.html
```

Utilisez une page HTML semblable à celle de la section précédente.

Vérifiez les droits :

```bash
namei -l /var/www/site1/index.html
```

Pour le laboratoire de contenu statique décrit plus haut, le répertoire ne doit pas nécessiter de droits d'écriture pour le processus Apache.

### 11.2 Créer un hôte virtuel

Sur Debian ou Ubuntu :

```bash
sudo nano /etc/apache2/sites-available/site1.conf
```

Contenu :

```apache
<VirtualHost *:80>
    ServerName site1.test

    DocumentRoot /var/www/site1
    DirectoryIndex index.html

    ErrorLog ${APACHE_LOG_DIR}/site1-error.log
    CustomLog ${APACHE_LOG_DIR}/site1-access.log combined

    <Directory /var/www/site1>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

#### Explication des directives

`<VirtualHost *:80>` définit un hôte virtuel lié au port HTTP 80 sur les adresses concernées.

`ServerName site1.test` déclare le nom principal du site.

`DocumentRoot /var/www/site1` détermine le répertoire des documents.

`DirectoryIndex index.html` demande au serveur de rechercher `index.html` comme page d'index.

`ErrorLog` définit le journal d'erreurs.

`CustomLog` définit le journal des accès.

Dans la section `<Directory>` :

- `Options -Indexes` désactive l'affichage automatique du contenu d'un répertoire lorsque celui-ci ne possède pas de page index, dans le contexte où cette option s'applique ;
- `+FollowSymLinks` active le suivi des liens symboliques selon les règles et restrictions applicables ;
- `AllowOverride None` interdit aux fichiers `.htaccess` de remplacer les paramètres couverts par `AllowOverride` ;
- `Require all granted` autorise les accès à ce répertoire au niveau de cette règle, sous réserve des autres restrictions applicables.

Cette configuration convient à une publication statique simple. Les applications plus complexes nécessitent des règles spécifiques.

### 11.3 Activer le site

Sur Debian et Ubuntu :

```bash
sudo a2ensite site1.conf
```

Vérifier la configuration :

```bash
sudo apachectl configtest
```

Si le résultat est `Syntax OK` :

```bash
sudo systemctl reload apache2
```

Puis :

```bash
sudo systemctl status apache2
```

### 11.4 Tester l'hôte virtuel

```bash
curl --resolve site1.test:80:127.0.0.1 http://site1.test/
```

Vous devez obtenir la page HTML publiée.

Vous pouvez consulter la liste des sites et leur ordre de sélection :

```bash
sudo apachectl -S
```

Cela aide notamment à comprendre pourquoi une requête arrive sur le site par défaut au lieu du site prévu.

### 11.5 Désactiver un site

Sur Debian et Ubuntu :

```bash
sudo a2dissite site1.conf
```

Puis vérifiez et appliquez le changement :

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

Désactiver un site n'efface normalement pas son fichier de configuration ni ses documents. L'opération modifie les liens de configuration utilisés par le mécanisme d'activation des sites.

**Ne désactivez pas la configuration en cours d'utilisation sur un serveur de production sans vérifier les conséquences.**


## 12. Comprendre les hôtes virtuels

### 12.1 Pourquoi héberger plusieurs sites sur une même machine ?

Il est possible de publier plusieurs noms de domaine sur une même adresse IP, pour autant que le réseau et la configuration du serveur soient appropriés.

Exemple :

```text
                     Adresse IP du serveur
                       192.0.2.20
                            |
                 +----------+----------+
                 |                     |
                 v                     v
           www.site-a.test       www.site-b.test
                 |                     |
                 v                     v
          /var/www/site-a       /var/www/site-b
```

Les noms `.test` sont utilisés ici à des fins de test.

Le serveur sélectionne le site en fonction des paramètres de la connexion et de la requête, notamment le nom d'hôte. En HTTPS, le nom peut également intervenir dès la négociation TLS par le mécanisme SNI.

### 12.2 Sélection du site avec Nginx

Pour Nginx, la directive principale est :

```nginx
server_name site1.test;
```

Chaque site peut avoir son propre bloc `server`, sa racine, ses journaux et ses règles de traitement.

Exemple conceptuel :

```nginx
server {
    listen 80;
    server_name site1.test;
    root /var/www/site1;
}

server {
    listen 80;
    server_name site2.test;
    root /var/www/site2;
}
```

Cet exemple illustre la sélection du site. Dans une configuration complète, il faut aussi définir les fichiers index, les règles de chemin et les journaux appropriés.

### 12.3 Sélection du site avec Apache

Apache utilise notamment :

```apache
<VirtualHost *:80>
    ServerName site1.test
    DocumentRoot /var/www/site1
</VirtualHost>

<VirtualHost *:80>
    ServerName site2.test
    DocumentRoot /var/www/site2
</VirtualHost>
```

Les sites ont chacun un `DocumentRoot` indépendant.

La première définition et l'ordre de chargement peuvent avoir des conséquences sur le site utilisé par défaut lorsqu'aucun nom ne correspond. Il est donc utile de connaître l'ordre effectif des hôtes virtuels avec `apachectl -S`.

### 12.4 Tester deux noms localement

Vous pouvez créer deux sites, puis tester :

```bash
curl --resolve site1.test:80:127.0.0.1 http://site1.test/
curl --resolve site2.test:80:127.0.0.1 http://site2.test/
```

Les commandes envoient les requêtes à la même adresse IP mais avec des noms d'hôte différents.

Si les deux réponses affichent le même contenu de manière inattendue, vérifiez :

1. que les deux configurations sont chargées ;
2. que les noms sont correctement écrits ;
3. que les racines sont différentes ;
4. que le service a rechargé sa configuration ;
5. que le site par défaut ne capture pas les requêtes attendues.


## 13. Tester un site depuis une autre machine

### 13.1 Identifier l'adresse IP du serveur

Sur Linux :

```bash
ip -br address
```

Cette commande présente les interfaces et les adresses IP qui leur sont associées.

Vous pouvez également consulter la route par défaut :

```bash
ip route
```

Attention : toutes les adresses affichées ne sont pas nécessairement accessibles depuis un autre réseau.

### 13.2 Tester la connexion réseau

Depuis un client disposant de `curl`, utilisez l'adresse du serveur :

```bash
curl -I http://ADRESSE_IP_DU_SERVEUR/
```

Remplacez `ADRESSE_IP_DU_SERVEUR` par l'adresse réelle correspondant à votre environnement.

Si le serveur écoute sur le port 80 mais que la requête échoue depuis le client, le problème peut provenir :

- du pare-feu local ;
- d'un pare-feu réseau ;
- de la route entre le client et le serveur ;
- de l'adresse ou de l'interface d'écoute ;
- de la virtualisation ou de la configuration réseau ;
- du fait que le service n'est pas démarré.

### 13.3 Vérifier les écoutes

Sur le serveur :

```bash
sudo ss -lntp
```

Une écoute sur `127.0.0.1:80` n'a pas la même portée qu'une écoute sur `0.0.0.0:80` ou sur une adresse réseau spécifique.

- `127.0.0.1` correspond à l'interface de boucle locale IPv4.
- `0.0.0.0` signifie généralement que le service écoute sur toutes les adresses IPv4 locales concernées.
- Une adresse IPv4 précise limite l'écoute à cette adresse.
- Une adresse IPv6 doit être interprétée selon sa configuration propre.

L'écoute sur toutes les interfaces ne signifie pas que les connexions externes réussiront automatiquement. Les routes et les filtres restent déterminants.


## 14. Pare-feu et exposition réseau

### 14.1 Pourquoi ouvrir un port ?

Un service peut être démarré sans être accessible depuis le réseau si le pare-feu bloque les connexions.

Cependant, ouvrir un port augmente aussi la surface exposée du système. N'autorisez que les flux nécessaires.

### 14.2 Avec UFW sur Ubuntu ou Debian

Vérifier son état :

```bash
sudo ufw status verbose
```

Pour autoriser HTTP, si UFW est utilisé et si cette exposition est souhaitée :

```bash
sudo ufw allow 80/tcp
```

Pour autoriser HTTPS :

```bash
sudo ufw allow 443/tcp
```

N'activez pas UFW à l'aveugle sur un serveur distant. Si les règles SSH ne sont pas correctes, vous risquez de perdre l'accès d'administration.

### 14.3 Avec firewalld

Sur une installation qui utilise `firewalld`, vérifiez d'abord son état et les zones applicables.

Exemple d'ouverture de HTTP :

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

Pour HTTPS :

```bash
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

Vérifiez les règles effectives :

```bash
sudo firewall-cmd --list-all
```

Ces commandes ne doivent pas être appliquées sans examen du périmètre réseau souhaité.

En production, l'exposition à Internet peut aussi dépendre d'un pare-feu périmétrique, d'un routeur ou de règles du fournisseur d'hébergement.


## 15. Journaux et diagnostic

Les journaux permettent de comprendre ce que le serveur reçoit, renvoie et rencontre comme problème.

### 15.1 Journaux Nginx

Sur une installation courante :

```text
/var/log/nginx/
|
+-- access.log
+-- error.log
```

Le journal d'accès enregistre les requêtes et leurs résultats selon le format configuré.

Le journal d'erreurs permet d'identifier des problèmes de configuration, de permissions ou de traitement.

Exemple :

```bash
sudo tail -n 50 /var/log/nginx/error.log
```

Pour suivre les nouvelles entrées :

```bash
sudo tail -f /var/log/nginx/error.log
```

Quittez le mode de suivi avec `Ctrl+C`.

Si le site dispose de journaux propres, consultez également les fichiers définis dans sa configuration.

### 15.2 Journaux Apache

Sur Debian et Ubuntu, les emplacements courants sont :

```text
/var/log/apache2/
|
+-- access.log
+-- error.log
```

Pour lire les dernières erreurs :

```bash
sudo tail -n 50 /var/log/apache2/error.log
```

Pour suivre le journal :

```bash
sudo tail -f /var/log/apache2/error.log
```

Sur d'autres distributions, notamment celles utilisant le paquet `httpd`, les journaux peuvent se trouver sous `/var/log/httpd/`.

Les emplacements effectifs dépendent de la configuration.

### 15.3 Journaux systemd

Le journal du service est également utile :

```bash
sudo journalctl -u nginx
```

Pour consulter les entrées récentes :

```bash
sudo journalctl -u nginx -n 50
```

Pour Apache sur Debian ou Ubuntu :

```bash
sudo journalctl -u apache2 -n 50
```

Sur une distribution qui utilise `httpd` :

```bash
sudo journalctl -u httpd -n 50
```

Pour suivre les nouvelles entrées :

```bash
sudo journalctl -u nginx -f
```

Les journaux systemd et les journaux applicatifs ne contiennent pas forcément les mêmes informations. Il faut les utiliser de manière complémentaire.

### 15.4 Une méthode de diagnostic ordonnée

Face à un site inaccessible, procédez dans cet ordre :

```text
1. La configuration est-elle valide ?
              |
              v
2. Le service est-il démarré ?
              |
              v
3. Un processus écoute-t-il sur le port attendu ?
              |
              v
4. Le test local fonctionne-t-il ?
              |
              v
5. Le nom d'hôte choisit-il le bon site ?
              |
              v
6. Les permissions des fichiers sont-elles correctes ?
              |
              v
7. Le pare-feu et le routage autorisent-ils le trafic ?
              |
              v
8. Que disent les journaux ?
```

Cette méthode évite de modifier de nombreux paramètres sans connaître la cause réelle.


## 16. Les erreurs courantes et leurs solutions

### 16.1 Erreur 404 : Not Found

**Symptôme :** le serveur répond, mais la ressource demandée n'est pas trouvée.

Causes possibles :

- le fichier n'existe pas ;
- le chemin d'URL ne correspond pas à celui attendu ;
- la racine du site est incorrecte ;
- la configuration de l'application ne prévoit pas cette route ;
- Nginx utilise une règle `try_files` inadaptée.

Diagnostic :

```bash
ls -la /var/www/site1/
```

Vérifiez aussi le `root` de Nginx ou le `DocumentRoot` d'Apache.

### 16.2 Erreur 403 : Forbidden

**Symptôme :** le serveur comprend la requête mais refuse l'accès.

Causes possibles :

- permissions de lecture ou de traversée insuffisantes ;
- règle `deny` ou `Require` restrictive ;
- restriction imposée par un contexte de configuration ;
- répertoire sans index avec l'indexation des répertoires désactivée.

Diagnostic :

```bash
namei -l /var/www/site1/index.html
```

Puis consultez le journal d'erreurs.

Ne résolvez pas cette situation en donnant des droits complets à tous les utilisateurs.

### 16.3 Erreur 502 : Bad Gateway

Cette erreur peut se produire lorsque Nginx ou Apache agit comme proxy et reçoit une réponse invalide, ou ne peut pas communiquer correctement avec le serveur en amont.

Causes possibles :

- application arrêtée ;
- mauvais port ;
- mauvaise adresse du service ;
- socket indisponible ;
- permissions incorrectes sur une socket Unix ;
- délai d'attente dépassé.

Pour un site strictement statique, une erreur 502 n'est pas le symptôme le plus habituel. Si vous en rencontrez une, examinez la présence d'une configuration de proxy ou d'une couche applicative.

### 16.4 Erreur 500 : Internal Server Error

Causes possibles :

- erreur de l'application ;
- erreur dans des règles ou instructions dynamiques ;
- mauvaise configuration ;
- problème de droits ou de ressources.

La réponse HTTP seule n'identifie pas la cause. Consultez les journaux du serveur Web et ceux de l'application.

### 16.5 Le service refuse de démarrer

Pour Nginx :

```bash
sudo nginx -t
sudo systemctl status nginx
sudo journalctl -u nginx -n 50
```

Pour Apache sur Debian ou Ubuntu :

```bash
sudo apachectl configtest
sudo systemctl status apache2
sudo journalctl -u apache2 -n 50
```

Une erreur fréquente est un port déjà occupé. Pour le vérifier :

```bash
sudo ss -lntp
```

Si Apache et Nginx essaient d'utiliser la même adresse et le même port, l'un peut échouer au démarrage.

### 16.6 Le navigateur affiche toujours l'ancienne page

Causes possibles :

- cache du navigateur ;
- modification non enregistrée ;
- mauvaise racine de publication ;
- mauvais hôte virtuel ;
- configuration rechargée sur le mauvais service ;
- réponse fournie par un proxy intermédiaire.

Commencez par vérifier le contenu depuis la machine serveur avec `curl`. Cela permet de distinguer un problème de publication d'un problème propre au navigateur ou au chemin réseau.


## 17. Notions élémentaires de HTTPS

### 17.1 Pourquoi utiliser HTTPS ?

HTTPS est la manière habituelle de fournir HTTP sur TLS.

Il permet :

- de chiffrer la communication entre le client et le serveur ;
- de vérifier l'intégrité des données échangées ;
- de vérifier l'identité du serveur grâce au certificat présenté et à sa chaîne de confiance.

Un certificat autosigné peut être utile dans un laboratoire, mais il ne sera pas automatiquement approuvé par les navigateurs de clients. Un certificat correctement délivré et configuré est nécessaire pour un site public.

### 17.2 Certificat, clé privée et nom d'hôte

Une configuration HTTPS classique implique notamment :

- un certificat correspondant au nom d'hôte ;
- la clé privée associée ;
- les certificats intermédiaires nécessaires à une chaîne de confiance valide ;
- une configuration TLS adéquate ;
- un service accessible sur le port prévu ;
- un nom d'hôte qui pointe vers le serveur concerné.

La clé privée doit être protégée. Elle ne doit pas être publiée dans la racine Web ou copiée dans un dépôt public.

### 17.3 Exemple conceptuel Nginx

Une configuration HTTPS peut prendre cette forme :

```nginx
server {
    listen 443 ssl;
    server_name www.exemple.com;

    root /var/www/site1;
    index index.html;

    ssl_certificate     /chemin/vers/certificat.pem;
    ssl_certificate_key /chemin/vers/cle-privee.pem;
}
```

Les chemins sont des exemples : le serveur ne fonctionnera pas avec cette configuration tant que les fichiers appropriés et la configuration complète ne seront pas en place.

Ne copiez pas cet exemple dans un serveur public en remplaçant uniquement le nom de domaine. Le certificat, la clé privée et la chaîne de confiance doivent correspondre à la situation réelle.

### 17.4 Exemple conceptuel Apache

Sur une installation disposant du module SSL, une base de configuration HTTPS ressemble à ceci :

```apache
<VirtualHost *:443>
    ServerName www.exemple.com
    DocumentRoot /var/www/site1

    SSLEngine on
    SSLCertificateFile /chemin/vers/certificat.pem
    SSLCertificateKeyFile /chemin/vers/cle-privee.pem
</VirtualHost>
```

Le module SSL doit être disponible et la prise en charge de l'écoute HTTPS doit être correctement configurée. Les chemins fournis sont des exemples, pas des fichiers existants garantis.

### 17.5 Quand configurer la redirection HTTP vers HTTPS ?

Il faut d'abord avoir un HTTPS fonctionnel.

Une fois le certificat valide, le serveur peut répondre par une redirection permanente ou temporaire pour envoyer les clients vers l'URL sécurisée.

Ne mettez pas en place une redirection forcée vers HTTPS avant d'avoir vérifié que la destination HTTPS fonctionne. Sinon, les clients peuvent être redirigés vers un service inaccessible.

HTTPS et la gestion des certificats méritent un laboratoire dédié, notamment pour comprendre le renouvellement automatique, les chaînes de certificats, les erreurs de nom et les diagnostics TLS.


## 18. Premières règles de sécurité

Un serveur Web accessible sur un réseau constitue une surface d'exposition. Une configuration fonctionnelle n'est pas nécessairement une configuration sûre.

### 18.1 Maintenir les logiciels à jour

Appliquez les mises à jour de sécurité selon la politique d'exploitation de la distribution et les procédures de votre organisation.

Ne remplacez pas sans préparation la version fournie par la distribution par une version obtenue d'une source non vérifiée.

### 18.2 Publier uniquement le contenu nécessaire

La racine Web ne doit pas contenir de sauvegardes, de dépôts Git, de clés privées, de mots de passe, de fichiers `.env` ou d'autres secrets.

Exemple à éviter :

```text
/var/www/site1/
|
+-- index.html
+-- .env
+-- backup.sql
+-- private-key.pem
+-- .git/
```

Même si certaines règles bloquent l'accès à des fichiers, les données secrètes ne doivent pas être placées inutilement dans un répertoire publiable.

### 18.3 Respecter le principe du moindre privilège

Le serveur Web ne doit pas recevoir des droits administratifs simplement pour résoudre un problème de lecture.

Évitez notamment :

- `chmod -R 777` ;
- de lancer tout le serveur Web en tant que `root` sans raison ;
- de donner au processus Web la possibilité d'écrire dans tous les fichiers du site ;
- de stocker les secrets dans des fichiers publiés.

Les processus maîtres et les processus de travail peuvent avoir des privilèges différents selon l'architecture. Ne modifiez pas arbitrairement l'utilisateur de service dans les fichiers de configuration.

### 18.4 Désactiver l'exposition inutile

Publiez uniquement les fichiers et les applications nécessaires.

Désactivez les listes de répertoires si elles ne sont pas souhaitées. Limitez les accès aux interfaces d'administration et aux ressources confidentielles.

N'exposez pas d'interface de gestion sur Internet simplement parce que le serveur fonctionne.

### 18.5 Protéger les informations sensibles

Ne copiez pas dans les fichiers publics :

- les mots de passe ;
- les clés privées ;
- les jetons d'accès ;
- les sauvegardes de bases de données ;
- les fichiers de configuration applicative contenant des secrets.

Une règle de blocage HTTP supplémentaire n'est pas un substitut à une bonne séparation des fichiers.

### 18.6 Préserver l'accès administratif

Avant de modifier un pare-feu, un port SSH ou les règles réseau d'un serveur distant, vérifiez que vous disposez d'un moyen de récupération.

Une modification incorrecte peut interrompre le service Web ou vous empêcher d'administrer la machine.

### 18.7 Tester les configurations avant rechargement

Pour Nginx :

```bash
sudo nginx -t
```

Pour Apache sous Debian ou Ubuntu :

```bash
sudo apachectl configtest
```

Ne rechargez pas une configuration après un test en échec sans avoir corrigé les erreurs.

### 18.8 Contrôler les journaux

Surveillez les erreurs de configuration, les demandes inhabituelles, les accès non autorisés et les problèmes de ressources.

Les journaux peuvent contenir des informations sensibles. Il faut contrôler leurs permissions, leur rotation, leur durée de conservation et les modalités de consultation.


## 19. Nginx comme reverse proxy : introduction

Cette section présente un concept essentiel, sans aller jusqu'à une configuration avancée.

Un reverse proxy reçoit la requête du client puis la transmet à une autre application ou à un autre serveur.

```text
Client
  |
  | HTTP ou HTTPS
  v
+----------------------+
| Nginx                |
| Reverse proxy        |
+----------+-----------+
           |
           | Requête transmise
           v
+----------------------+
| Application          |
| Exemple : port 3000  |
+----------------------+
```

Le client échange avec Nginx. Nginx échange ensuite avec l'application selon la configuration.

### 19.1 Pourquoi utiliser un reverse proxy ?

Un reverse proxy peut servir à :

- présenter un point d'entrée commun ;
- gérer HTTPS ;
- envoyer les requêtes vers différentes applications ;
- conserver le serveur applicatif hors d'une exposition directe ;
- centraliser certains contrôles et journaux ;
- répartir certaines requêtes entre plusieurs serveurs.

Il n'offre pas, à lui seul, une sécurité complète. Les applications, les réseaux, les droits et les règles d'accès doivent être configurés correctement.

### 19.2 Distinction avec le contenu statique

Pour un simple site HTML :

```text
Client -> Nginx -> Fichier HTML
```

Pour une application dynamique en reverse proxy :

```text
Client -> Nginx -> Application -> Résultat
```

Dans le second cas, Nginx ne génère pas nécessairement lui-même le contenu dynamique. Il transmet une requête à l'application et renvoie sa réponse au client.

Apache peut également jouer le rôle de reverse proxy avec les modules appropriés.


## 20. Travaux pratiques guidés

### TP 1 — Installer et vérifier Nginx

**Objectif :** installer Nginx et vérifier qu'il répond localement.

Sur Debian ou Ubuntu :

```bash
sudo apt update
sudo apt install nginx
sudo systemctl enable --now nginx
sudo systemctl status nginx
curl -I http://127.0.0.1/
sudo ss -lntp | grep ':80'
```

**Résultat attendu :**

- le paquet est installé ;
- le service est actif ;
- une requête locale obtient une réponse HTTP ;
- un processus écoute sur le port attendu.

Si la connexion échoue, examinez l'état du service et les journaux avant de poursuivre.

### TP 2 — Publier une page personnalisée avec Nginx

**Objectif :** publier une page HTML dans un répertoire dédié.

Étape 1 : créer le répertoire.

```bash
sudo mkdir -p /var/www/formation-nginx
```

Étape 2 : créer la page.

```bash
sudo nano /var/www/formation-nginx/index.html
```

Utilisez par exemple :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Formation Nginx</title>
</head>
<body>
    <h1>Serveur Nginx opérationnel</h1>
    <p>Première page de formation.</p>
</body>
</html>
```

Étape 3 : créer la configuration.

```bash
sudo nano /etc/nginx/sites-available/formation-nginx
```

Contenu :

```nginx
server {
    listen 80;
    server_name formation-nginx.test;

    root /var/www/formation-nginx;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Étape 4 : activer et tester le site.

```bash
sudo ln -s /etc/nginx/sites-available/formation-nginx /etc/nginx/sites-enabled/formation-nginx
sudo nginx -t
sudo systemctl reload nginx
```

Étape 5 : effectuer le test :

```bash
curl --resolve formation-nginx.test:80:127.0.0.1 http://formation-nginx.test/
```

Si le lien symbolique existe déjà, vérifiez qu'il pointe vers la bonne configuration au lieu de le recréer.

### TP 3 — Publier une page avec Apache

**Précaution :** si Nginx utilise déjà le port 80, arrêtez-le dans ce laboratoire ou configurez les deux serveurs sur des ports distincts. Pour des débutants, il est plus simple de les tester séparément.

Sur Debian ou Ubuntu, arrêtez Nginx pour libérer le port si nécessaire :

```bash
sudo systemctl stop nginx
```

Créez le répertoire :

```bash
sudo mkdir -p /var/www/formation-apache
```

Créez le fichier :

```bash
sudo nano /var/www/formation-apache/index.html
```

Contenu :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Formation Apache</title>
</head>
<body>
    <h1>Serveur Apache opérationnel</h1>
    <p>Première page de formation.</p>
</body>
</html>
```

Créez un hôte virtuel :

```bash
sudo nano /etc/apache2/sites-available/formation-apache.conf
```

Configuration :

```apache
<VirtualHost *:80>
    ServerName formation-apache.test
    DocumentRoot /var/www/formation-apache
    DirectoryIndex index.html

    ErrorLog ${APACHE_LOG_DIR}/formation-apache-error.log
    CustomLog ${APACHE_LOG_DIR}/formation-apache-access.log combined

    <Directory /var/www/formation-apache>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

Activez le site :

```bash
sudo a2ensite formation-apache.conf
```

Testez la configuration puis rechargez le service :

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

Testez le résultat :

```bash
curl --resolve formation-apache.test:80:127.0.0.1 http://formation-apache.test/
```

Le résultat attendu est la page HTML de formation.

### TP 4 — Étudier un problème de permissions

**Objectif :** apprendre à diagnostiquer un accès refusé sans donner des droits excessifs.

Vérifiez le chemin :

```bash
namei -l /var/www/formation-apache/index.html
```

Vérifiez le journal d'erreurs Apache :

```bash
sudo tail -n 50 /var/log/apache2/formation-apache-error.log
```

Puis vérifiez :

- le propriétaire des fichiers ;
- les permissions des répertoires parents ;
- la configuration de l'hôte virtuel ;
- les restrictions supplémentaires du système, si elles existent.

N'appliquez pas de modification de permissions avant d'avoir identifié la restriction réelle.

### TP 5 — Comprendre un site virtuel qui ne répond pas comme prévu

**Objectif :** identifier quel site est sélectionné.

Avec Apache :

```bash
sudo apachectl -S
```

Avec Nginx :

```bash
sudo nginx -T
```

Ensuite, envoyez une requête contenant le nom d'hôte attendu :

```bash
curl --resolve formation-apache.test:80:127.0.0.1 http://formation-apache.test/
```

Si la réponse est celle d'un autre site, vérifiez la valeur de `ServerName` sous Apache ou de `server_name` sous Nginx, ainsi que les fichiers réellement chargés.


## 21. Exercices de compréhension avec corrigés

### Exercice 1 — Rôle du serveur Web

**Question :** quelle est la différence entre un navigateur Web et un serveur Web ?

**Corrigé :**

Le navigateur est un client qui envoie des requêtes et affiche ou exploite les réponses. Le serveur Web reçoit les requêtes, sélectionne les ressources ou transmet les demandes à une application, puis renvoie les réponses.

### Exercice 2 — Port HTTP

**Question :** sur quel port TCP un serveur écoute-t-il habituellement pour HTTP ?

**Corrigé :**

Le port standard est TCP 80. HTTPS utilise habituellement TCP 443.

### Exercice 3 — Codes de statut

**Question :** que signifient les codes HTTP 200, 404 et 500 ?

**Corrigé :**

- `200` indique un succès.
- `404` indique qu'une ressource demandée n'a pas été trouvée.
- `500` indique une erreur interne du serveur ou de l'application.

### Exercice 4 — Configuration Nginx

**Question :** quelle directive indique le répertoire racine d'un site dans une configuration Nginx simple ?

**Corrigé :**

La directive `root`.

Exemple :

```nginx
root /var/www/site1;
```

### Exercice 5 — Configuration Apache

**Question :** quelle directive Apache définit le répertoire des documents publiés ?

**Corrigé :**

La directive `DocumentRoot`.

Exemple :

```apache
DocumentRoot /var/www/site1
```

### Exercice 6 — Contrôle de configuration

**Question :** pourquoi exécuter `nginx -t` avant de recharger le service ?

**Corrigé :**

Pour vérifier la syntaxe et certains problèmes de configuration avant d'appliquer la nouvelle configuration. Cela réduit le risque d'introduire une erreur lors du rechargement.

### Exercice 7 — Plusieurs sites

**Question :** comment Nginx et Apache peuvent-ils héberger plusieurs noms de sites sur une même machine et un même port ?

**Corrigé :**

Ils utilisent des configurations de sites virtuels. Nginx emploie notamment `server_name` dans un bloc `server`. Apache emploie notamment `ServerName` dans un bloc `<VirtualHost>`.

Le serveur sélectionne le site à partir des informations disponibles dans la connexion et la requête.

### Exercice 8 — Erreur 403

**Question :** un site renvoie une erreur 403. Pourquoi est-il déconseillé d'appliquer `chmod -R 777` au répertoire ?

**Corrigé :**

Cette commande accorderait des droits excessifs aux utilisateurs. Il faut identifier si le blocage vient des permissions, d'une règle d'autorisation ou d'une autre restriction, puis appliquer le changement minimal nécessaire.

### Exercice 9 — Nginx et PHP

**Question :** un fichier `index.php` est placé dans la racine de Nginx. Est-il forcément exécuté ?

**Corrigé :**

Non. Il faut une intégration adaptée, par exemple PHP-FPM, et une configuration correcte. Sans cela, le résultat dépend de la configuration du serveur, qui ne doit pas exposer le code source par erreur.

### Exercice 10 — Diagnostic réseau

**Question :** le service fonctionne avec `curl http://127.0.0.1/`, mais le poste client ne peut pas accéder au serveur. Quels éléments faut-il contrôler ?

**Corrigé :**

Il faut notamment vérifier l'adresse d'écoute, l'adresse IP du serveur, la connectivité réseau, le routage, les pare-feu locaux et intermédiaires, puis les journaux. Le fonctionnement local ne garantit pas l'accessibilité depuis un autre réseau.


## 22. Défi final : déployer deux sites statiques

### Objectif

Mettre en place un serveur Web Linux qui publie deux sites différents et permet de vérifier leur sélection.

Réalisez d'abord le défi avec Nginx, puis, dans un environnement séparé ou après avoir libéré le port, reproduisez le résultat avec Apache.

### Cahier des charges

Le serveur doit publier deux noms de test :

```text
site-a.test
site-b.test
```

Les contenus doivent être différents.

Arborescence :

```text
/var/www/
|
+-- site-a/
|     |
|     +-- index.html
|
+-- site-b/
      |
      +-- index.html
```

Les deux sites doivent répondre sur le port HTTP standard dans le laboratoire.

### Étape A — Créer les répertoires et les pages

```bash
sudo mkdir -p /var/www/site-a /var/www/site-b
```

Créer la première page :

```bash
sudo nano /var/www/site-a/index.html
```

Contenu :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Site A</title>
</head>
<body>
    <h1>Bienvenue sur le site A</h1>
</body>
</html>
```

Créer la seconde :

```bash
sudo nano /var/www/site-b/index.html
```

Contenu :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Site B</title>
</head>
<body>
    <h1>Bienvenue sur le site B</h1>
</body>
</html>
```

### Étape B — Configuration Nginx

Créez `/etc/nginx/sites-available/site-a` :

```nginx
server {
    listen 80;
    server_name site-a.test;

    root /var/www/site-a;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Créez `/etc/nginx/sites-available/site-b` :

```nginx
server {
    listen 80;
    server_name site-b.test;

    root /var/www/site-b;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Activez les fichiers sur une installation disposant de `sites-enabled` :

```bash
sudo ln -s /etc/nginx/sites-available/site-a /etc/nginx/sites-enabled/site-a
sudo ln -s /etc/nginx/sites-available/site-b /etc/nginx/sites-enabled/site-b
```

Vérifiez avant le rechargement :

```bash
sudo nginx -t
```

Puis :

```bash
sudo systemctl reload nginx
```

### Étape C — Tester les deux sites

```bash
curl --resolve site-a.test:80:127.0.0.1 http://site-a.test/
```

Puis :

```bash
curl --resolve site-b.test:80:127.0.0.1 http://site-b.test/
```

**Résultat attendu :**

- la première requête renvoie le contenu du site A ;
- la seconde requête renvoie le contenu du site B.

Si les deux réponses sont identiques, examinez les configurations chargées et le nom d'hôte transmis.

### Étape D — Reproduire avec Apache

Dans un laboratoire Apache séparé, créez les hôtes virtuels suivants.

Pour le site A, dans `/etc/apache2/sites-available/site-a.conf` :

```apache
<VirtualHost *:80>
    ServerName site-a.test
    DocumentRoot /var/www/site-a
    DirectoryIndex index.html

    ErrorLog ${APACHE_LOG_DIR}/site-a-error.log
    CustomLog ${APACHE_LOG_DIR}/site-a-access.log combined

    <Directory /var/www/site-a>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

Pour le site B, dans `/etc/apache2/sites-available/site-b.conf` :

```apache
<VirtualHost *:80>
    ServerName site-b.test
    DocumentRoot /var/www/site-b
    DirectoryIndex index.html

    ErrorLog ${APACHE_LOG_DIR}/site-b-error.log
    CustomLog ${APACHE_LOG_DIR}/site-b-access.log combined

    <Directory /var/www/site-b>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

Activez les deux sites :

```bash
sudo a2ensite site-a.conf
sudo a2ensite site-b.conf
```

Vérifiez la configuration :

```bash
sudo apachectl configtest
sudo apachectl -S
```

Appliquez le changement :

```bash
sudo systemctl reload apache2
```

Testez :

```bash
curl --resolve site-a.test:80:127.0.0.1 http://site-a.test/
curl --resolve site-b.test:80:127.0.0.1 http://site-b.test/
```

### Critères de réussite

Le défi est réussi si :

- les deux répertoires existent ;
- les deux fichiers HTML sont lisibles par le serveur ;
- les deux configurations sont chargées ;
- le test de configuration ne retourne aucune erreur ;
- le service Web est actif ;
- chaque nom renvoie le contenu qui lui correspond ;
- les journaux ne révèlent pas de problème inattendu.


## 23. Fiche de révision rapide

### Commandes Nginx

Installation sur Debian ou Ubuntu :

```bash
sudo apt install nginx
```

État du service :

```bash
sudo systemctl status nginx
```

Test de configuration :

```bash
sudo nginx -t
```

Afficher la configuration complète :

```bash
sudo nginx -T
```

Rechargement :

```bash
sudo systemctl reload nginx
```

Journal d'erreurs :

```bash
sudo tail -f /var/log/nginx/error.log
```

Test HTTP :

```bash
curl -I http://127.0.0.1/
```

### Commandes Apache sous Debian ou Ubuntu

Installation :

```bash
sudo apt install apache2
```

État :

```bash
sudo systemctl status apache2
```

Test de configuration :

```bash
sudo apachectl configtest
```

Afficher les hôtes virtuels :

```bash
sudo apachectl -S
```

Activer un site :

```bash
sudo a2ensite site1.conf
```

Désactiver un site :

```bash
sudo a2dissite site1.conf
```

Rechargement :

```bash
sudo systemctl reload apache2
```

Journal d'erreurs :

```bash
sudo tail -f /var/log/apache2/error.log
```

### Commandes système utiles

Vérifier les interfaces et les adresses IP :

```bash
ip -br address
```

Lister les connexions en écoute :

```bash
sudo ss -lntp
```

Examiner les journaux d'un service :

```bash
sudo journalctl -u nginx -n 50
```

Envoyer une requête HTTP :

```bash
curl -I http://127.0.0.1/
```

Tester un nom d'hôte localement :

```bash
curl --resolve site1.test:80:127.0.0.1 http://site1.test/
```


## 24. Glossaire

**Apache HTTP Server** : serveur Web modulaire, fréquemment appelé Apache ou `httpd`.

**Application Web** : logiciel qui traite les opérations de l'application et peut générer des réponses dynamiques.

**Code HTTP** : nombre transmis dans une réponse HTTP pour indiquer son résultat.

**Configuration** : ensemble de directives qui définissent le comportement du service.

**DNS** : système qui permet notamment d'associer des noms de domaine à des informations de résolution.

**DocumentRoot** : directive Apache qui indique le répertoire racine des documents du site.

**Fichier index** : fichier que le serveur recherche pour servir la page d'accueil d'un répertoire.

**Hôte virtuel** : configuration qui permet de servir un site en fonction d'une adresse, d'un port et/ou d'un nom.

**HTTP** : protocole de communication utilisé par les clients et les serveurs Web.

**HTTPS** : HTTP protégé par TLS.

**Journal d'accès** : fichier enregistrant les requêtes HTTP reçues et leurs résultats selon le format configuré.

**Journal d'erreurs** : fichier ou flux de journal qui contient les erreurs et avertissements du serveur.

**Nginx** : serveur Web pouvant également agir comme reverse proxy et répartiteur de charge.

**Port** : numéro utilisé par TCP ou UDP pour identifier un point de communication d'un service.

**Racine Web** : répertoire de départ utilisé par la configuration d'un site pour rechercher les ressources à publier.

**Reverse proxy** : serveur intermédiaire qui reçoit les requêtes et les transmet à un ou plusieurs serveurs en amont.

**Socket** : point de communication utilisé par un processus, généralement associé à une adresse de transport ou à un chemin local.

**TLS** : protocole assurant notamment le chiffrement et l'intégrité des échanges et permettant l'authentification du serveur.

**URL** : identifiant d'une ressource comprenant notamment un schéma, un nom d'hôte et un chemin.


## 25. Checklist avant de considérer le site fonctionnel

Utilisez cette liste à la fin de chaque mise en pratique.

- [ ] Le paquet attendu est installé.
- [ ] Le nom du service correspond à la distribution.
- [ ] Le service est actif.
- [ ] La configuration a passé le test de syntaxe.
- [ ] Le port d'écoute est celui attendu.
- [ ] Le fichier HTML existe.
- [ ] Les répertoires permettent l'accès en lecture et en traversée selon les besoins.
- [ ] Le site virtuel ou bloc `server` est chargé.
- [ ] Le nom d'hôte est correctement configuré.
- [ ] La requête locale renvoie le bon contenu.
- [ ] Les journaux ont été vérifiés en cas d'erreur.
- [ ] Le pare-feu n'autorise que les flux nécessaires.
- [ ] Aucun secret n'est placé dans le répertoire publié.
- [ ] La procédure de retour arrière est connue avant toute modification importante.


## 26. Documentation officielle

Pour approfondir les notions étudiées et vérifier les directives adaptées à la version installée, utilisez en priorité les documentations officielles.

### Nginx

- Guide pour débutants : https://nginx.org/en/docs/beginners_guide.html
- Documentation générale : https://nginx.org/en/docs/
- Configuration HTTPS : https://nginx.org/en/docs/http/configuring_https_servers.html

### Apache HTTP Server

- Guide de démarrage : https://httpd.apache.org/docs/2.4/getting-started.html
- Documentation Apache 2.4 : https://httpd.apache.org/docs/2.4/
- Configuration des hôtes virtuels : https://httpd.apache.org/docs/2.4/vhosts/
- Documentation SSL/TLS : https://httpd.apache.org/docs/2.4/ssl/

### Linux et outils associés

- systemd : https://www.freedesktop.org/software/systemd/man/
- curl : https://curl.se/docs/
- Debian : https://www.debian.org/doc/
- Ubuntu Server : https://documentation.ubuntu.com/server/


## Conclusion

Vous disposez désormais des bases nécessaires pour installer et exploiter un serveur Web avec Nginx ou Apache sous Linux.

La compétence essentielle n'est pas seulement de faire afficher une page. Il faut également savoir déterminer quelle configuration est active, vérifier le service, tester la sélection du site, interpréter les codes HTTP, lire les journaux et diagnostiquer les problèmes de permissions ou de réseau.

Le parcours recommandé est le suivant :

```text
Installation
    |
    v
Gestion du service
    |
    v
Publication d'une page statique
    |
    v
Configuration d'un site virtuel
    |
    v
Tests HTTP et lecture des journaux
    |
    v
Diagnostic des erreurs
    |
    v
Premières mesures de sécurité
    |
    v
Préparation aux applications dynamiques
   et à HTTPS en production
```

La maîtrise de ces étapes constitue une base solide avant d'étudier les reverse proxies avancés, PHP-FPM, les certificats TLS, la mise en production et la supervision des serveurs Web.