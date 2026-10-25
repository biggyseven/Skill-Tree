# Journaux et supervision

## Niveau débutant

## 1. Présentation du cours

Un système informatique peut sembler fonctionner correctement alors qu’il rencontre déjà des problèmes : un disque presque plein, un service qui redémarre régulièrement, une application qui répond lentement, des connexions réseau qui échouent ou des tentatives répétées d’authentification.

Sans mécanisme de surveillance, l’administrateur découvre souvent le problème lorsque les utilisateurs commencent à se plaindre.

Les **journaux** et la **supervision** permettent de mieux comprendre ce qui se passe sur un système informatique. Ils fournissent des informations complémentaires :

- Les journaux décrivent les événements qui se sont produits.
- Les métriques mesurent l’évolution d’un système au cours du temps.
- Les contrôles de disponibilité vérifient qu’un service répond.
- Les alertes signalent les conditions qui nécessitent une attention.
- Les tableaux de bord rassemblent les informations utiles au diagnostic.

L’objectif n’est pas simplement de collecter le plus de données possible. Il faut pouvoir répondre à des questions concrètes :

- Le serveur fonctionne-t-il correctement ?
- Pourquoi une application est-elle devenue lente ?
- À quel moment le problème a-t-il commencé ?
- Le disque est-il saturé ?
- Le service a-t-il redémarré ?
- Un utilisateur a-t-il rencontré une erreur ?
- Une alerte nécessite-t-elle une intervention immédiate ?
- Comment démontrer qu’un incident est résolu ?

Ce cours part des bases et progresse vers la mise en place d’une première supervision exploitable.

## 2. Objectifs pédagogiques

À la fin de ce cours, l’apprenant doit être capable de :

1. Expliquer la différence entre journaux, métriques, supervision et alertes.
2. Identifier les principales sources de journaux sous Linux et Windows.
3. Lire et filtrer des journaux avec des commandes adaptées.
4. Comprendre les niveaux de gravité des événements.
5. Surveiller le CPU, la mémoire, le stockage et le réseau.
6. Vérifier la disponibilité d’un service.
7. Découvrir les principes de Prometheus et Grafana.
8. Comprendre le rôle d’un agent ou d’un exportateur de métriques.
9. Créer une règle d’alerte élémentaire.
10. Distinguer un symptôme d’une cause probable.
11. Diagnostiquer un incident en suivant une démarche méthodique.
12. Protéger les journaux contre la perte, l’exposition et la modification non autorisée.
13. Construire un tableau de bord simple.
14. Rédiger un compte rendu d’incident à partir de preuves techniques.

## 3. Prérequis et environnement de travail

Aucun niveau avancé n’est nécessaire.

Il est utile de connaître les notions suivantes :

- Serveur, poste de travail et système d’exploitation.
- Adresse IP et réseau local.
- Service et processus.
- Espace disque, mémoire vive et processeur.
- Commandes de base Linux.
- Commandes de base PowerShell sous Windows.

Les exemples Linux utilisent principalement des distributions récentes basées sur systemd, comme Ubuntu ou Debian. Certains chemins et noms de services peuvent varier selon la distribution.

Les exemples Windows utilisent l’Observateur d’événements et PowerShell.

Les outils étudiés sont notamment :

| Outil | Utilité principale |
|---|---|
| `journalctl` | Lire les journaux du journal systemd sous Linux |
| `rsyslog` | Recevoir, filtrer et transférer des messages de journalisation |
| Observateur d’événements | Consulter les événements Windows |
| `Get-WinEvent` | Lire et filtrer les journaux Windows avec PowerShell |
| `top` et `free` | Observer l’activité système sous Linux |
| `df` et `du` | Examiner l’utilisation du stockage sous Linux |
| `ping` et `ss` | Vérifier certains aspects de la connectivité et des services |
| Prometheus | Collecter et interroger des métriques |
| Node Exporter | Exposer des métriques système Linux à Prometheus |
| Windows Exporter | Exposer des métriques système Windows |
| Grafana | Visualiser les métriques et organiser des tableaux de bord |

Les outils ne remplissent pas tous la même fonction. Grafana est principalement une solution de visualisation et d’alerting ; Prometheus collecte et stocke des métriques. Un système de journaux centralisés répond à un besoin complémentaire.

## 4. Comprendre les journaux

### 4.1 Qu'est-ce qu'un journal ?

Un journal, ou *log*, est un enregistrement décrivant un événement produit par un système, une application, un équipement réseau ou un service.

Exemples :

- Un utilisateur ouvre une session.
- Une application démarre.
- Un service échoue.
- Un serveur reçoit une requête HTTP.
- Une connexion réseau est refusée.
- Un disque signale une erreur.
- Une tâche automatique termine son exécution.
- Une sauvegarde échoue.
- Un administrateur modifie une configuration.

Un événement peut contenir une date, une heure, une source, un niveau de gravité et un message.

Exemple fictif :

```text
2026-10-24 08:15:32
Hôte       : srv-web-01
Service    : nginx
Niveau     : ERROR
Message    : Échec de connexion au serveur applicatif
```

Cet événement ne prouve pas à lui seul que le réseau est en panne. Il indique qu’au moment considéré, le serveur Web n’a pas réussi à joindre un autre composant.

Le diagnostic exige de rechercher des informations complémentaires.

### 4.2 Pourquoi les journaux sont-ils importants ?

Les journaux servent à :

**Diagnostiquer :** identifier les erreurs produites par un service.

**Reconstituer une chronologie :** déterminer ce qui s’est passé avant et après un incident.

**Comprendre un comportement :** examiner les démarrages, arrêts, connexions et opérations importantes.

**Détecter un problème de sécurité :** rechercher des tentatives d’authentification inhabituelles ou des modifications non autorisées.

**Vérifier un changement :** confirmer qu’un service a redémarré ou qu’une configuration a été chargée.

**Documenter un incident :** apporter des éléments techniques pour un rapport.

Les journaux ne sont toutefois pas une vérité absolue. Un événement peut être absent, mal horodaté, mal interprété, incomplet ou perdu avant d’être enregistré.

### 4.3 Une ligne de journal peut être décomposée

Considérons l’exemple suivant :

```text
2026-10-24T08:15:32Z srv-web-01 nginx[2481]:
ERROR upstream connection timed out
```

On peut distinguer :

```text
Date et heure : 2026-10-24T08:15:32Z
Hôte          : srv-web-01
Programme     : nginx
PID           : 2481
Niveau        : ERROR
Événement     : upstream connection timed out
```

`Z` indique ici une heure exprimée en UTC.

Le processus ou le service qui écrit le journal dépend du système. La structure exacte varie : certains journaux sont du texte simple, d’autres utilisent des champs structurés.

### 4.4 Différence entre un événement et une erreur

Tous les événements ne sont pas des erreurs.

Exemple :

```text
08:00:00 INFO  Service démarré
08:01:12 INFO  Connexion établie
08:02:41 WARN  Réponse lente
08:03:15 ERROR Connexion à la base de données impossible
08:04:20 INFO  Connexion rétablie
```

L’événement `INFO` peut être normal. Le `WARN` signale une situation à surveiller. Le `ERROR` décrit un échec.

Il faut interpréter les événements selon leur contexte. Une application peut journaliser une erreur récupérable, tandis qu’un composant peut produire un message d’apparence anodine au moment où un service important s’arrête.

## 5. Les niveaux de gravité

De nombreux systèmes utilisent des niveaux permettant de différencier les événements ordinaires des situations urgentes.

### 5.1 Niveaux courants

| Niveau | Signification habituelle | Exemple |
|---|---|---|
| DEBUG | Informations détaillées utiles au diagnostic | Valeurs intermédiaires d’une opération |
| INFO | Fonctionnement normal | Service démarré |
| NOTICE | Événement normal mais significatif | Changement d’état important |
| WARNING ou WARN | Situation anormale à surveiller | Espace disque faible |
| ERROR | Opération en échec | Connexion à une base impossible |
| CRITICAL | Situation critique | Fonction principale indisponible |
| ALERT | Intervention immédiate nécessaire | Situation exigeant une action rapide |
| EMERGENCY | Système inutilisable ou danger majeur selon le contexte | Défaillance extrêmement grave |

Tous les logiciels ne proposent pas exactement les mêmes niveaux ni les mêmes noms.

Dans syslog, la numérotation usuelle des priorités est différente de l’ordre visuel du tableau : `0` correspond à `emerg`, `1` à `alert`, `2` à `crit`, `3` à `err`, `4` à `warning`, `5` à `notice`, `6` à `info` et `7` à `debug`.

### 5.2 Comment interpréter une gravité ?

La gravité indique comment le producteur classe l’événement. Elle ne donne pas automatiquement sa priorité opérationnelle.

Exemple :

```text
Événement A :
  INFO
  Un service secondaire a démarré.

Événement B :
  WARNING
  La partition principale atteint 95 % d'occupation.

Événement C :
  ERROR
  Une requête utilisateur a échoué ponctuellement.
```

L’événement B, bien qu’il soit seulement de niveau `WARNING`, peut annoncer une interruption prochaine si la partition contient les données critiques du système.

Il faut examiner :

- L’importance du service.
- La fréquence de l’événement.
- La durée du problème.
- Le nombre d’utilisateurs touchés.
- Les conséquences possibles.
- L’existence d’une solution de contournement.

### 5.3 Ne pas confondre gravité et priorité

La gravité technique est souvent indiquée dans les journaux.

La priorité opérationnelle détermine dans quel ordre l’équipe doit agir.

Un événement de faible gravité peut devenir prioritaire s’il concerne un système critique. À l’inverse, une erreur répétée dans un environnement de test peut ne pas nécessiter d’intervention immédiate.

## 6. Les différences entre journaux, métriques, supervision et alertes

Ces quatre notions sont liées, mais elles ne doivent pas être confondues.

### 6.1 Les journaux

Les journaux enregistrent des événements.

Exemple :

```text
08:30:04 ERROR Échec d'authentification pour le compte admin
08:30:05 ERROR Échec d'authentification pour le compte admin
08:30:06 ERROR Échec d'authentification pour le compte admin
```

Ils aident à comprendre ce qui s’est produit et à identifier les événements associés.

### 6.2 Les métriques

Une métrique est une mesure numérique observée au cours du temps.

Exemples :

```text
CPU utilisé          : 72 %
Mémoire utilisée     : 6,4 Go
Disque occupé        : 89 %
Connexions TCP       : 137
Requêtes HTTP/s      : 420
Latence moyenne      : 180 ms
```

Les métriques permettent d’observer les tendances, les pics de consommation et les comportements inhabituels.

### 6.3 La supervision

La supervision collecte et évalue des informations afin de déterminer si un système ou un service fonctionne conformément aux attentes.

Elle peut vérifier :

- La disponibilité d’un serveur.
- La charge CPU.
- L’espace disque libre.
- La durée de réponse d’une API.
- Le fonctionnement d’une base de données.
- L’état d’un service.
- Le succès des sauvegardes.
- La présence de certaines erreurs.

### 6.4 Les alertes

Une alerte est une notification déclenchée lorsqu’une condition définie est remplie.

Exemple :

```text
Condition :
  Partition utilisée à plus de 90 %
  pendant 10 minutes

Action :
  Créer une alerte de gravité élevée
  et notifier l'équipe d'exploitation
```

L’alerte n’explique pas nécessairement la cause. Elle signale une situation qui doit être vérifiée.

### 6.5 Schéma global

```text
      SERVEURS / APPLICATIONS / RESEAUX
                      |
          +-----------+-----------+
          |                       |
          v                       v
     JOURNAUX                  METRIQUES
  Evénements détaillés      Mesures numériques
          |                       |
          v                       v
 Collecte et stockage       Collecte et stockage
          |                       |
          +-----------+-----------+
                      |
                      v
             ANALYSE ET REGLES
                      |
           +----------+----------+
           |                     |
           v                     v
      TABLEAUX DE BORD         ALERTES
           |                     |
           v                     v
       VISUALISATION       NOTIFICATION
                                 |
                                 v
                          DIAGNOSTIC HUMAIN
                                 |
                                 v
                         ACTION / CORRECTION
```

Une organisation bien conçue utilise les journaux pour enquêter et les métriques pour comprendre l’évolution de la situation. Les deux approches se complètent.

## 7. Où sont stockés les journaux sous Linux ?

### 7.1 Le répertoire `/var/log`

Sur de nombreuses distributions Linux, les fichiers de journaux se trouvent dans `/var/log`.

Exemples fréquents :

| Chemin | Contenu habituel |
|---|---|
| `/var/log/syslog` | Messages système sur certaines distributions Debian/Ubuntu |
| `/var/log/messages` | Messages système sur certaines distributions de la famille Red Hat |
| `/var/log/auth.log` | Authentification et sécurité sur de nombreuses installations Debian/Ubuntu |
| `/var/log/secure` | Messages d'authentification sur certaines distributions de la famille Red Hat |
| `/var/log/kern.log` | Messages du noyau sur certaines configurations |
| `/var/log/nginx/access.log` | Requêtes reçues par Nginx |
| `/var/log/nginx/error.log` | Erreurs Nginx |
| `/var/log/apache2/access.log` | Requêtes Apache sur de nombreuses installations Debian/Ubuntu |
| `/var/log/apache2/error.log` | Erreurs Apache sur de nombreuses installations Debian/Ubuntu |

Les chemins, les noms et la présence des fichiers dépendent de la distribution, des services installés et de leur configuration.

Certaines machines utilisent essentiellement le journal systemd, tandis que d’autres écrivent également dans des fichiers classiques.

### 7.2 Lister les fichiers de journaux

```bash
ls -lah /var/log
```

Pour afficher la taille des répertoires :

```bash
sudo du -sh /var/log/*
```

La deuxième commande donne une estimation de la place occupée par les fichiers et répertoires. Elle peut nécessiter des privilèges supplémentaires pour accéder à certaines données.

### 7.3 Lire un fichier

La commande `cat` affiche tout le fichier :

```bash
sudo cat /var/log/syslog
```

Elle peut produire une sortie trop volumineuse pour les grands fichiers.

Pour consulter le début :

```bash
sudo head -n 20 /var/log/syslog
```

Pour consulter la fin :

```bash
sudo tail -n 50 /var/log/syslog
```

Pour suivre les nouvelles lignes :

```bash
sudo tail -f /var/log/syslog
```

`tail -f` est utile pendant un test, car les nouveaux événements sont affichés à mesure qu’ils sont ajoutés au fichier.

Utiliser `Ctrl+C` pour arrêter le suivi.

### 7.4 Rechercher un mot

```bash
sudo grep -i "error" /var/log/syslog
```

Explication :

- `grep` recherche du texte.
- `-i` ignore la différence entre majuscules et minuscules.
- `"error"` est le texte recherché.
- Le dernier argument indique le fichier.

Pour afficher les lignes contenant un mot parmi plusieurs possibilités :

```bash
sudo grep -Ei "error|failed|critical" /var/log/syslog
```

Cette recherche ne détecte que les mots indiqués. Une application peut signaler une erreur sans employer ces termes.

### 7.5 Afficher les lignes avec leur numéro

```bash
sudo grep -n "error" /var/log/syslog
```

Pour rechercher dans plusieurs fichiers :

```bash
sudo grep -Rni "connection refused" /var/log/
```

Une recherche récursive peut être coûteuse et rencontrer des fichiers binaires, des permissions insuffisantes ou des données très volumineuses. Il est souvent préférable de cibler d’abord le service concerné.

## 8. Lire les journaux avec `journalctl`

### 8.1 Qu'est-ce que le journal systemd ?

Sur les systèmes utilisant systemd, `systemd-journald` collecte et stocke des événements de différentes sources.

La commande `journalctl` sert à consulter ces événements.

Contrairement à une simple recherche dans un fichier texte, le journal systemd permet de filtrer les événements selon des champs comme le service, le temps ou la priorité.

### 8.2 Afficher les événements

```bash
sudo journalctl
```

Les événements sont affichés avec leur horodatage et leur contenu.

Pour lire les événements les plus récents :

```bash
sudo journalctl -n 50
```

Pour suivre les nouveaux événements :

```bash
sudo journalctl -f
```

### 8.3 Filtrer par période

Afficher les événements depuis le début de la journée :

```bash
sudo journalctl --since today
```

Afficher ceux des deux dernières heures :

```bash
sudo journalctl --since "2 hours ago"
```

Afficher une plage horaire :

```bash
sudo journalctl \
  --since "2026-10-24 08:00:00" \
  --until "2026-10-24 09:00:00"
```

Les dates et heures doivent correspondre à la période que l’on souhaite examiner. Vérifier le fuseau horaire de la machine avant de comparer des journaux provenant de plusieurs serveurs.

### 8.4 Filtrer par service

Pour un service SSH :

```bash
sudo journalctl -u ssh
```

Sur certaines distributions, le service porte le nom `sshd` :

```bash
sudo journalctl -u sshd
```

Pour afficher les événements récents d’un serveur Web :

```bash
sudo journalctl -u nginx -n 100
```

Pour suivre le service en direct :

```bash
sudo journalctl -u nginx -f
```

Si la commande n’affiche rien, cela ne signifie pas nécessairement que le service n’a jamais produit de journaux. Le service peut ne pas exister, ne pas utiliser le journal systemd ou avoir un nom différent.

### 8.5 Filtrer par priorité

Afficher les erreurs et les niveaux plus graves :

```bash
sudo journalctl -p err
```

Afficher les avertissements et les erreurs :

```bash
sudo journalctl -p warning
```

Ces filtres utilisent les priorités du journal systemd. L’interprétation exacte doit tenir compte du niveau choisi et des conventions du logiciel qui produit l’événement.

### 8.6 Consulter les erreurs du démarrage précédent

Après un redémarrage, les événements du démarrage précédent peuvent aider à comprendre une panne.

```bash
sudo journalctl -b -1
```

Pour examiner les erreurs du démarrage précédent :

```bash
sudo journalctl -b -1 -p err
```

L’accès aux anciens démarrages dépend de la configuration de conservation du journal. Si le journal est uniquement stocké en mémoire volatile, les données peuvent ne plus être disponibles après un redémarrage.

### 8.7 Vérifier l'état d'un service

```bash
systemctl status nginx
```

Cette commande donne notamment l’état du service et peut afficher des messages récents.

Pour connaître l’état sans la sortie détaillée :

```bash
systemctl is-active nginx
```

Pour vérifier si le service est activé au démarrage :

```bash
systemctl is-enabled nginx
```

Ces commandes répondent à des questions différentes :

- `is-active` indique l’état d’exécution actuel.
- `is-enabled` indique si le service est configuré pour démarrer selon les mécanismes systemd.
- `journalctl` aide à comprendre les événements associés.

Un service peut être actif et néanmoins rencontrer des erreurs applicatives.

## 9. Générer et tester un événement sous Linux

Il est utile d’apprendre à rechercher un événement que l’on a soi-même créé.

### 9.1 Avec `logger`

La commande `logger` permet d’envoyer un message au système de journalisation.

```bash
logger "TEST-SUPERVISION : message de demonstration"
```

Rechercher le message :

```bash
sudo journalctl -b --grep="TEST-SUPERVISION"
```

Si la version de `journalctl` ne prend pas en charge `--grep`, utiliser une recherche sur la sortie :

```bash
sudo journalctl -b | grep "TEST-SUPERVISION"
```

### 9.2 Définir une priorité

```bash
logger -p user.warning "TEST-SUPERVISION : avertissement"
```

On peut ensuite examiner les événements :

```bash
sudo journalctl -b --grep="TEST-SUPERVISION"
```

Les options disponibles dépendent de l’implémentation de `logger`. L’objectif est de comprendre le chemin suivi par un événement entre son émission et sa consultation.

### 9.3 Ce que cet exercice démontre

```text
Commande logger
      |
      v
Système de journalisation
      |
      v
Journal disponible
      |
      v
journalctl
      |
      v
Recherche de l'événement
```

La réussite de cet exercice confirme que le message de test est visible dans le journal consulté. Elle ne garantit pas que tous les services envoient leurs journaux au même endroit.

## 10. Découvrir rsyslog

### 10.1 À quoi sert rsyslog ?

`rsyslog` est un service de journalisation qui permet de recevoir, traiter, filtrer et transmettre des messages.

Selon la configuration, il peut :

- Écrire des messages dans des fichiers.
- Filtrer les messages selon leur origine ou leur priorité.
- Recevoir des journaux provenant d’autres machines.
- Transférer les messages vers un serveur central.
- Utiliser des files d’attente et des mécanismes de livraison.
- Envoyer les messages vers des systèmes de collecte adaptés.

Toutes les distributions ne l’utilisent pas exactement de la même façon. Le fait qu’une machine dispose de `journalctl` ne signifie pas que rsyslog est installé.

### 10.2 Vérifier son état

```bash
systemctl status rsyslog
```

Vérifier si le paquet est installé dépend du gestionnaire de paquets. Sous Debian ou Ubuntu :

```bash
dpkg -l rsyslog
```

Installation si nécessaire :

```bash
sudo apt update
sudo apt install rsyslog
```

Sur les distributions basées sur RPM, la commande d’installation est généralement différente :

```bash
sudo dnf install rsyslog
```

Avant toute modification, vérifier la documentation de la distribution et les services déjà en place.

### 10.3 Tester la configuration

```bash
sudo rsyslogd -N1
```

Cette commande vérifie la syntaxe de la configuration rsyslog. Elle ne prouve pas à elle seule que les messages arrivent bien à destination.

Après une modification, suivre la procédure de validation et de rechargement adaptée à la configuration utilisée.

### 10.4 Centralisation des journaux

Dans un environnement comprenant plusieurs serveurs, il peut être utile de regrouper les journaux sur un système central.

```text
  SERVEUR WEB          SERVEUR BASE          SERVEUR FICHIERS
      |                     |                       |
      v                     v                       v
  Journaux locaux      Journaux locaux        Journaux locaux
      |                     |                       |
      +---------------------+-----------------------+
                            |
                            v
                   SERVEUR DE JOURNAUX
                            |
                            v
                  Stockage et indexation
                            |
                            v
                    Recherche centralisée
                            |
                            v
                  Diagnostic / investigations
```

Les journaux centralisés simplifient les recherches entre plusieurs systèmes et permettent d’observer une chronologie commune.

La centralisation nécessite cependant des mesures de sécurité : authentification ou restriction des sources, transport protégé, contrôle d’accès, gestion de la rétention et surveillance du serveur de collecte.

### 10.5 Pourquoi centraliser les journaux ?

Supposons qu’une application utilise trois composants :

```text
Navigateur utilisateur
        |
        v
Serveur Web
        |
        v
Serveur applicatif
        |
        v
Base de données
```

Si la requête échoue, l’erreur peut se trouver dans le serveur Web, l’application ou la base de données.

Le regroupement des journaux permet de rapprocher les événements produits par les différents composants.

Pour éviter les mauvaises corrélations, il faut synchroniser les horloges, conserver le fuseau horaire ou l’offset, et utiliser si possible un identifiant de requête commun.

## 11. Les journaux sous Windows

### 11.1 L'Observateur d'événements

Windows possède un système de journalisation accessible via l’Observateur d’événements.

Il permet de consulter notamment :

- Application : événements liés aux applications.
- Système : événements du système d’exploitation et de plusieurs composants.
- Sécurité : événements d’audit, selon la politique activée.
- Journaux spécifiques à certains rôles, services ou logiciels.

Le journal Security peut nécessiter des autorisations particulières. Tous les événements possibles ne sont pas automatiquement enregistrés : leur collecte dépend notamment de la configuration d’audit.

### 11.2 Ouvrir l'outil

Dans Windows :

1. Ouvrir le menu Démarrer.
2. Rechercher `Observateur d'événements`.
3. Lancer l’outil.
4. Ouvrir **Journaux Windows**.
5. Sélectionner Application, Sécurité ou Système selon le besoin.

On peut filtrer les événements selon leur niveau, leur date, leur source ou leur identifiant.

### 11.3 Comprendre un événement Windows

Un événement peut contenir :

- Le nom du journal.
- La date et l’heure.
- La source ou le fournisseur.
- L’identifiant de l’événement.
- Le niveau.
- Un message explicatif.
- Des données détaillées.
- Le nom de l’ordinateur.

Un identifiant d’événement ne doit pas être interprété isolément. Il faut vérifier le fournisseur, le texte et la documentation du composant concerné.

### 11.4 Lire les événements avec PowerShell

Lister les journaux disponibles :

```powershell
Get-WinEvent -ListLog *
```

Lire les 30 événements les plus récents du journal système :

```powershell
Get-WinEvent -LogName System -MaxEvents 30
```

Afficher les propriétés les plus utiles :

```powershell
Get-WinEvent -LogName System -MaxEvents 20 |
    Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message
```

Lire les événements récents du journal Application :

```powershell
Get-WinEvent -LogName Application -MaxEvents 50
```

Selon le journal demandé, des privilèges supplémentaires peuvent être nécessaires.

### 11.5 Filtrer par date et niveau

Exemple : rechercher les événements Error du journal System générés pendant les dernières 24 heures.

```powershell
$since = (Get-Date).AddHours(-24)

Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = $since
    Level     = 2
} | Select-Object TimeCreated, Id, ProviderName, Message
```

Dans ce contexte, le niveau `2` correspond aux événements Error.

Autres niveaux courants de Windows :

| Niveau | Signification habituelle |
|---|---|
| Critical | Critique |
| Error | Erreur |
| Warning | Avertissement |
| Information | Information |

Certains journaux peuvent aussi contenir des événements verbeux.

### 11.6 Filtrer sur un identifiant d'événement

Une fois un identifiant pertinent confirmé dans la documentation du composant concerné, on peut filtrer les occurrences :

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    Id      = 7036
} -MaxEvents 20
```

Cette commande illustre le filtrage par identifiant. Il faut interpréter le résultat selon le fournisseur qui a émis l’événement, car un même identifiant n’a pas une signification universelle entre toutes les sources.

### 11.7 Exporter une sélection

Pour produire un rapport CSV exploitable :

```powershell
Get-WinEvent -LogName System -MaxEvents 100 |
    Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message |
    Export-Csv -Path ".\system-events.csv" -NoTypeInformation -Encoding utf8
```

Ce fichier peut contenir des noms d’utilisateurs, des chemins internes et d’autres informations sensibles. Il faut le stocker et le transmettre selon les règles de sécurité de l’organisation.

## 12. Comprendre le fonctionnement d'un système de supervision

### 12.1 Une surveillance permanente

Un système de supervision effectue régulièrement des contrôles et collecte des valeurs.

Exemple de contrôle de disponibilité :

```text
Toutes les 30 secondes :
      |
      v
Tester le serveur
      |
      v
Réponse valide ?
   /       \
 OUI       NON
  |          |
  v          v
Etat OK    Echec détecté
              |
              v
      Confirmation éventuelle
              |
              v
        Alerte si nécessaire
```

Un contrôle peut échouer ponctuellement à cause d’une perte réseau ou d’un délai dépassé. Des confirmations et des règles appropriées aident à réduire les fausses alertes.

### 12.2 Supervision avec agent ou sans agent

**Avec agent :** un logiciel installé sur la machine fournit des métriques ou des informations au système de supervision.

Avantages :

- Accès à des informations internes plus détaillées.
- Possibilité de suivre des métriques du système d’exploitation.
- Contrôle potentiellement plus complet.

Inconvénients :

- Installation et maintenance d’un composant supplémentaire.
- Gestion de ses permissions et de ses mises à jour.
- Risque de collecte interrompue si l’agent ne fonctionne plus.

**Sans agent :** le système de supervision teste directement un service ou utilise des mécanismes réseau déjà disponibles.

Exemples :

- Vérifier une réponse HTTP.
- Tester la résolution DNS.
- Contrôler si un port TCP répond.
- Effectuer un ping lorsque le réseau l’autorise.

La supervision sans agent ne permet pas toujours de connaître la cause d’un problème interne à la machine.

### 12.3 Supervision interne et externe

La supervision interne mesure l’état observé depuis l’infrastructure elle-même.

La supervision externe teste le service depuis un point proche de l’expérience réelle de l’utilisateur.

Exemple :

```text
          SERVEUR WEB
               |
       Contrôle interne
               |
       Service actif ?
               |
               v
          Résultat OK

          UTILISATEUR
               |
      Contrôle externe
               |
     DNS + réseau + HTTPS
               |
               v
     Page réellement accessible ?
```

Les deux résultats peuvent différer. Un serveur peut être actif sans être accessible depuis le réseau extérieur.

## 13. Les principales métriques à surveiller

### 13.1 Processeur (CPU)

L’utilisation CPU représente la part de temps ou de capacité consommée selon la méthode de mesure.

Une utilisation élevée et durable peut indiquer :

- Une charge de travail importante.
- Un traitement bloqué ou inefficace.
- Trop de processus actifs.
- Une activité inhabituelle.
- Une capacité insuffisante.

Une utilisation CPU élevée n’est pas forcément un problème. Un serveur de calcul peut normalement fonctionner à un niveau élevé pendant un traitement prévu.

Il faut examiner la durée, la latence, la charge et l’impact sur les utilisateurs.

Sous Linux :

```bash
top
```

Ou, si l’outil est disponible :

```bash
htop
```

`htop` doit parfois être installé séparément.

### 13.2 Mémoire vive

La mémoire est utilisée par les processus, le noyau et le cache du système.

Sous Linux :

```bash
free -h
```

Pour consulter les informations détaillées du noyau :

```bash
cat /proc/meminfo
```

Une faible quantité de mémoire dite « libre » n’implique pas automatiquement un problème, car Linux utilise aussi la mémoire disponible pour les caches.

Il faut regarder notamment la mémoire réellement disponible, l’évolution dans le temps et le comportement du swap.

### 13.3 Stockage

Un disque peut être en bon état physique tout en manquant d’espace libre.

Sous Linux :

```bash
df -h
```

Cette commande indique l’utilisation des systèmes de fichiers montés.

Pour rechercher les répertoires volumineux :

```bash
sudo du -sh /var/log
sudo du -sh /var/cache
```

Avant de supprimer des fichiers, déterminer ce qui occupe l’espace. Il ne faut pas effacer arbitrairement des journaux actifs ou des fichiers système.

Pour observer l’utilisation d’un volume au cours du temps, la supervision devrait conserver une métrique d’espace libre, et pas seulement exécuter une vérification ponctuelle.

### 13.4 Réseau

Les métriques réseau utiles comprennent :

- Le débit entrant.
- Le débit sortant.
- Les erreurs d’interface.
- Les paquets perdus.
- La latence.
- Le nombre de connexions.
- Les erreurs DNS.
- Les connexions refusées.
- Les délais de connexion.

Commandes Linux utiles :

```bash
ip -br address
ip route
ip -s link
ss -lntup
```

`ip -s link` affiche des compteurs liés aux interfaces. `ss -lntup` aide à identifier les sockets en écoute et certains processus associés, selon les permissions disponibles.

### 13.5 Disponibilité d'un service

Un service peut être vérifié de plusieurs façons.

État systemd :

```bash
systemctl is-active nginx
```

Port TCP :

```bash
nc -vz 127.0.0.1 80
```

Cette vérification exige que `nc` soit installé. Elle confirme seulement la réussite ou l’échec de la connexion TCP vers la cible.

Test HTTP :

```bash
curl -I --max-time 5 http://127.0.0.1/
```

Le test HTTP vérifie davantage qu’un simple port, mais il ne valide pas nécessairement le contenu métier de l’application.

Un contrôle complet doit correspondre à la fonction que l’on souhaite réellement garantir.

## 14. Définir ce qu'il faut surveiller

La supervision doit être organisée à partir des services essentiels, et non uniquement à partir des ressources physiques.

Pour chaque service, se poser ces questions :

1. À quoi sert-il ?
2. Qui en est responsable ?
3. Comment vérifier son fonctionnement ?
4. Quelle interruption est acceptable ?
5. Quelles métriques permettent de détecter une dégradation ?
6. Quels journaux aident à en comprendre la cause ?
7. Qui reçoit les alertes ?
8. Que doit faire la personne qui reçoit l’alerte ?
9. Comment confirmer le retour à la normale ?

### 14.1 Exemple : serveur Web

| Élément | Surveillance possible |
|---|---|
| Processus | État du service |
| Port HTTP/HTTPS | Disponibilité TCP |
| Endpoint HTTP | Code de réponse et latence |
| CPU | Utilisation et tendance |
| Mémoire | Disponibilité et pression mémoire |
| Stockage | Espace disponible |
| Journaux d'accès | Requêtes, codes HTTP, volume |
| Journaux d'erreur | Échecs, problèmes de connexion |
| Application en amont | Réponse du service dépendant |
| Certificat TLS | Date d'expiration, validité |

### 14.2 Exemple : serveur de fichiers

| Élément | Surveillance possible |
|---|---|
| Disponibilité du serveur | Réponse aux contrôles |
| Volume principal | Espace disponible |
| Disques | État matériel selon les outils disponibles |
| Réseau | Débit, erreurs et latence |
| Service de partage | État du service |
| Accès utilisateur | Tests d'accès autorisés |
| Sauvegarde | Dernier succès |
| Journaux | Erreurs et événements importants |

## 15. Construire une première stratégie d'alertes

### 15.1 Pourquoi ne pas tout alerter ?

Si chaque événement génère une notification, l’équipe reçoit trop de messages et risque d’ignorer les plus importants.

Une bonne alerte doit être exploitable.

Elle devrait inclure :

- Le nom du système.
- Le service concerné.
- La condition détectée.
- L’heure de début.
- La gravité.
- L’impact connu ou probable.
- Un lien vers les métriques ou les journaux, si disponibles.
- Une procédure de diagnostic.
- Le responsable ou la file de support.

### 15.2 Exemples de règles de départ

| Contrôle | Condition illustrative | Réaction |
|---|---|---|
| Espace disque | Plus de 90 % pendant 10 minutes | Alerte à l'équipe système |
| CPU | Plus de 90 % pendant 10 minutes | Vérifier processus et impact |
| Mémoire | Mémoire disponible très faible et pression durable | Vérifier charge, swap et processus |
| Endpoint Web | Échec répété du contrôle HTTP | Contrôler service, réseau et application |
| Sauvegarde | Dernier succès trop ancien selon la politique | Vérifier l'exécution et la restauration |
| Agent de supervision | Données absentes au-delà du délai défini | Vérifier agent, réseau et collecte |

Ces valeurs sont des exemples pédagogiques, pas des seuils universels. Le seuil adapté dépend du système, du service et du niveau de criticité.

### 15.3 Une alerte doit conduire à une action

Exemple :

```text
ALERTE
  |
  v
Partition à 94 %
  |
  v
Identifier le système de fichiers
  |
  v
Rechercher les répertoires volumineux
  |
  v
Identifier le contenu responsable
  |
  v
Appliquer une correction adaptée
  |
  v
Vérifier le nouvel espace disponible
  |
  v
Confirmer le retour à la normale
  |
  v
Documenter si nécessaire
```

Il ne suffit pas d’augmenter la taille du disque ou de supprimer des fichiers sans comprendre l’origine de la consommation.

## 16. Découvrir Prometheus

### 16.1 À quoi sert Prometheus ?

Prometheus est un outil de collecte et de stockage de métriques sous forme de séries temporelles.

Une série temporelle contient des valeurs associées à des horodatages et peut être identifiée par des étiquettes.

Prometheus interroge habituellement des cibles qui exposent un endpoint HTTP de métriques. Ce modèle est souvent appelé *scraping*.

Prometheus permet notamment :

- D’interroger des métriques.
- De suivre leur évolution.
- De créer des règles d’enregistrement.
- D’évaluer des règles d’alerte.
- D’alimenter des tableaux de bord avec les données collectées.

Prometheus n’est pas, à lui seul, un système complet de collecte et d’indexation de tous les journaux textuels. Pour ces besoins, il faut un outil complémentaire.

### 16.2 Architecture de base

```text
               SERVEUR LINUX
                    |
                    v
              Node Exporter
                    |
            Endpoint de métriques
                    |
                    v
                Prometheus
                    |
          +---------+---------+
          |                   |
          v                   v
     Requêtes              Règles
          |                   |
          v                   v
     Exploration            Alertes
          |
          v
       Grafana
          |
          v
   Tableaux de bord visuels
```

Node Exporter expose des métriques système Linux. Prometheus les collecte. Grafana peut ensuite utiliser Prometheus comme source de données pour produire des graphiques et des tableaux de bord.

### 16.3 Qu'est-ce qu'un exportateur ?

Un exportateur est un composant qui rend disponibles des données sous une forme que Prometheus peut lire.

Exemples :

- Node Exporter pour les métriques système Linux.
- Windows Exporter pour certaines métriques système Windows.
- Des exportateurs dédiés à certaines bases de données, applications ou équipements.

La disponibilité et le détail des métriques dépendent du composant utilisé et de sa configuration.

Un exportateur ne doit pas être exposé sans contrôle sur un réseau non fiable. Il faut limiter les accès à ses endpoints selon les besoins.

### 16.4 Première configuration Prometheus

Le fichier `prometheus.yml` utilise ici un exemple simple. Il suppose que Prometheus et Node Exporter sont accessibles sur les ports indiqués.

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets:
          - "127.0.0.1:9090"

  - job_name: "linux"
    static_configs:
      - targets:
          - "127.0.0.1:9100"
```

Interprétation :

- `scrape_interval` définit ici la fréquence de collecte.
- `job_name` identifie un groupe de cibles.
- `targets` contient les endpoints interrogés.
- `127.0.0.1` désigne la machine locale.

Le deuxième endpoint ne fonctionnera que si Node Exporter est effectivement installé, démarré et accessible sur la même machine. Si les composants sont sur des hôtes différents, utiliser les adresses et noms réseau adaptés.

### 16.5 Vérifier la collecte

Dans l’interface Web de Prometheus, généralement accessible sur le port `9090` dans une installation de test :

1. Ouvrir la page de l'interface.
2. Consulter les cibles de collecte.
3. Vérifier que la cible attendue est en état `UP`.
4. Exécuter une requête simple.

Une cible `UP` indique que la collecte de cette cible fonctionne au moment du contrôle. Cela ne signifie pas que toutes les applications de l’hôte sont disponibles.

### 16.6 Comprendre la métrique `up`

Prometheus fournit une métrique appelée `up` pour les cibles collectées.

Dans un environnement où les cibles sont bien configurées :

```promql
up
```

Pour filtrer un groupe nommé `linux` :

```promql
up{job="linux"}
```

Une valeur de `1` indique une collecte réussie au dernier contrôle ; `0` indique un échec de collecte de la cible.

Si une cible disparaît complètement de la configuration ou de la découverte de services, son comportement ne sera pas nécessairement le même qu'une cible conservée mais en échec. Les règles d'alerte doivent être pensées selon le mode de découverte et de collecte.

## 17. Comprendre quelques requêtes PromQL

PromQL est le langage de requête de Prometheus.

Il sert à rechercher des métriques, appliquer des filtres, calculer des taux et agréger des séries temporelles.

### 17.1 Afficher une métrique

```promql
up
```

Cette requête affiche les séries correspondant aux cibles suivies.

### 17.2 Calculer un taux à partir d'un compteur

Certaines métriques sont des compteurs qui augmentent au fil du temps.

Exemple avec les secondes CPU :

```promql
rate(node_cpu_seconds_total[5m])
```

`rate()` estime le taux moyen d’augmentation du compteur pendant la période indiquée.

Une métrique de compteur ne doit pas toujours être interprétée directement comme une valeur instantanée.

### 17.3 Examiner les systèmes de fichiers

Avec Node Exporter :

```promql
node_filesystem_avail_bytes
```

Cette métrique expose l’espace disponible en octets pour les systèmes de fichiers concernés, selon les métriques exposées par l’exportateur.

Pour comprendre correctement le résultat, il faut identifier le système de fichiers, le point de montage et les éventuels filtres de collecte.

### 17.4 Calculer une utilisation CPU illustrative

```promql
100 * (
  1 - avg by (instance) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  )
)
```

Cette requête estime le pourcentage de temps CPU non idle par instance, à partir des séries attendues de Node Exporter.

Les métriques disponibles et leur interprétation doivent être vérifiées dans l’environnement réellement supervisé.

## 18. Découvrir Grafana

### 18.1 Quel est le rôle de Grafana ?

Grafana permet de visualiser des données provenant de sources compatibles : métriques, journaux ou autres données selon les connecteurs configurés.

Il sert notamment à créer :

- Des tableaux de bord.
- Des graphiques de tendances.
- Des indicateurs d'état.
- Des vues pour les équipes.
- Des visualisations destinées au diagnostic.
- Des règles d’alerte selon la configuration choisie.

Grafana ne remplace pas automatiquement les collecteurs ou les stockages derrière les tableaux de bord. Il faut lui fournir une source de données adaptée.

### 18.2 Exemple de tableau de bord

Un tableau de bord système peut contenir :

```text
+-----------------------------------------------------+
| TABLEAU DE BORD : SERVEURS                          |
+-----------------------------------------------------+
| Etat des hôtes       | Disponibilité des services   |
| CPU par serveur      | Mémoire disponible           |
| Espace disque        | Réseau entrant / sortant     |
+-----------------------------------------------------+
| Erreurs importantes des dernières heures            |
+-----------------------------------------------------+
| Alertes actives      | Dernier succès de sauvegarde |
+-----------------------------------------------------+
```

Ce schéma représente une organisation logique, pas une capture d’écran réelle de Grafana.

### 18.3 Concevoir un tableau de bord utile

Un tableau de bord de débutant doit répondre à quelques questions simples :

- Quels systèmes sont indisponibles ?
- Quels services ont une alerte active ?
- Quels serveurs approchent leurs limites ?
- Quelle ressource évolue anormalement ?
- Depuis quand la dégradation est-elle visible ?
- Où trouver les journaux associés ?

Éviter d’afficher des dizaines de graphiques sans hiérarchie. Les informations les plus importantes doivent être immédiatement identifiables.

## 19. Créer une règle d'alerte simple avec Prometheus

Une règle d’alerte peut signaler qu’une cible n’est plus joignable par Prometheus.

Exemple de fichier `alert.rules.yml` :

```yaml
groups:
  - name: basic-monitoring
    rules:
      - alert: MonitoringTargetUnavailable
        expr: up == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Cible de supervision indisponible"
          description: "Prometheus ne collecte plus correctement cette cible."
```

Explication :

- `alert` donne un nom à la règle.
- `expr` définit la condition.
- `for: 2m` impose ici que la condition reste vraie pendant deux minutes avant que l’alerte soit considérée comme active.
- `labels` permet d’ajouter des informations de classement.
- `annotations` contient des éléments lisibles pour les personnes qui traitent l’alerte.

Le nom `MonitoringTargetUnavailable` décrit un échec de collecte, pas forcément une panne complète du serveur ou du service métier.

Il faut également charger ce fichier dans la configuration Prometheus. Exemple :

```yaml
global:
  scrape_interval: 15s

rule_files:
  - "alert.rules.yml"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets:
          - "127.0.0.1:9090"

  - job_name: "linux"
    static_configs:
      - targets:
          - "127.0.0.1:9100"
```

Les chemins des fichiers sont interprétés selon l’environnement d’exécution et la manière dont Prometheus est lancé.

Cette configuration illustre l’évaluation d’une alerte. Pour envoyer des notifications, il faut aussi configurer un mécanisme de notification adapté, par exemple Alertmanager ou l’alerting de Grafana.

## 20. Comprendre le cycle de vie d'une alerte

Une alerte n’est pas simplement un message qui apparaît une fois.

Selon l’outil, une règle peut passer par plusieurs états :

```text
       CONDITION NORMALE
              |
              v
        AUCUNE ALERTE
              |
     Condition anormale détectée
              |
              v
        ATTENTE / PENDING
              |
   Condition maintenue assez longtemps
              |
              v
          ACTIVE / FIRING
              |
     Notification et diagnostic
              |
              v
        Correction du problème
              |
              v
         RETOUR A LA NORMALE
              |
              v
         ALERTE RESOLUE
```

Les termes précis varient selon les outils. Il faut vérifier comment le système gère les délais, les données absentes, les répétitions de notifications et la résolution.

### 20.1 Éviter les fausses alertes

Une alerte peut être déclenchée par :

- Une valeur temporairement anormale.
- Une interruption réseau très courte.
- Une erreur de collecte.
- Un seuil mal choisi.
- Une maintenance planifiée.
- Une source de données indisponible.

Pour réduire les fausses alertes :

1. Définir un seuil approprié.
2. Utiliser une durée de confirmation lorsque c’est adapté.
3. Distinguer une panne du service d’une panne de collecte.
4. Regrouper les événements liés.
5. Documenter les exceptions et les fenêtres de maintenance.
6. Tester les alertes avant de les utiliser en production.

Ne pas allonger artificiellement les délais au point de masquer les incidents réellement importants.

## 21. Les journaux et les métriques racontent une histoire commune

Les métriques aident à identifier quand la situation change. Les journaux aident à comprendre ce qui a pu provoquer ce changement.

### 21.1 Exemple de diagnostic

Un serveur Web semble lent.

Métriques observées :

```text
08:00 CPU : 35 %
08:05 CPU : 42 %
08:10 CPU : 94 %
08:15 CPU : 96 %
```

Journaux observés :

```text
08:09:58 WARN  Temps de réponse élevé
08:10:03 ERROR Connexion à la base de données expirée
08:10:09 ERROR Requête échouée
```

On peut suspecter un lien entre la charge élevée et les problèmes d'accès à la base de données, mais il faut encore tester cette hypothèse.

Les bonnes questions sont :

- Quelle requête ou quel processus consomme le CPU ?
- La base de données est-elle accessible ?
- Les erreurs apparaissent-elles sur plusieurs serveurs ?
- Y a-t-il eu un changement juste avant 08:10 ?
- La latence de la base de données a-t-elle augmenté ?
- La charge élevée précède-t-elle ou suit-elle les erreurs ?

### 21.2 Rechercher les événements autour d'une heure précise

Sous Linux :

```bash
sudo journalctl \
  --since "2026-10-24 08:05:00" \
  --until "2026-10-24 08:20:00"
```

Puis, si l'application écrit dans un fichier :

```bash
sudo grep "2026-10-24 08:1" /var/log/nginx/error.log
```

Cette deuxième commande suppose que le format d’horodatage du fichier correspond à la chaîne recherchée. Dans un environnement réel, adapter le filtre au format du journal.

L’objectif consiste à limiter la période de recherche et à comparer les événements des composants impliqués.

## 22. Faire un diagnostic méthodique

### 22.1 Ne pas commencer par redémarrer

Face à un problème, un redémarrage immédiat peut faire disparaître des éléments utiles au diagnostic.

Il peut aussi provoquer une interruption supplémentaire ou masquer temporairement la cause initiale.

Une démarche plus fiable consiste à :

1. Confirmer le problème.
2. Mesurer son impact.
3. Définir le périmètre touché.
4. Recueillir les journaux et les métriques.
5. Examiner les changements récents.
6. Formuler une hypothèse.
7. Tester cette hypothèse sans aggraver l’incident.
8. Appliquer une correction appropriée.
9. Vérifier le résultat.
10. Documenter les actions.

### 22.2 Exemple : site Web inaccessible

```text
       Site Web inaccessible
                 |
                 v
      Le serveur est-il joignable ?
          /               \
        NON                OUI
         |                  |
         v                  v
 Vérifier réseau       Tester le port
 et routage            et le service
                            |
                            v
                   Le service répond-il ?
                      /           \
                    NON            OUI
                     |              |
                     v              v
              Journaux système   Tester HTTP,
              et application    DNS et TLS
                     |              |
                     +------+-------+
                            |
                            v
                   Identifier la cause
                            |
                            v
                  Corriger puis vérifier
```

### 22.3 Exemple : disque presque plein

```text
Alerte : disque à 95 %
          |
          v
Vérifier les systèmes de fichiers
          |
          v
Identifier le point de montage saturé
          |
          v
Trouver les répertoires volumineux
          |
          v
Examiner les fichiers responsables
          |
          v
Décider de l'action :
  - rotation des journaux
  - nettoyage contrôlé
  - extension du volume
  - correction d'une croissance anormale
          |
          v
Vérifier l'espace libéré
          |
          v
Contrôler l'application
```

Ne pas supprimer des fichiers simplement parce qu’ils sont volumineux. Un fichier de base de données ou un fichier de journal actif peut être indispensable.

### 22.4 Exemple : service qui redémarre

Sous Linux, commencer par :

```bash
systemctl status nginx
sudo journalctl -u nginx --since "30 minutes ago"
```

Puis examiner les journaux applicatifs, la configuration et les ressources système.

Selon le service, les causes peuvent inclure :

- Une erreur de configuration.
- Un port déjà utilisé.
- Un fichier ou certificat manquant.
- Des permissions incorrectes.
- Un manque de mémoire.
- Une dépendance indisponible.
- Une mise à jour récente.
- Un défaut logiciel.

Il ne faut retenir une cause qu’après avoir obtenu des éléments qui la soutiennent.

## 23. Les journaux de sécurité

### 23.1 Que peut-on rechercher ?

Les journaux peuvent aider à identifier :

- Des échecs d’authentification répétés.
- Des connexions à des heures inhabituelles.
- Des modifications de comptes.
- Des changements de configuration.
- Des services lancés de manière inattendue.
- Des erreurs de permission.
- Des activités inhabituelles sur un serveur.

Une anomalie ne constitue pas nécessairement une attaque. Elle doit être analysée avec son contexte.

### 23.2 Sous Linux

Sur une distribution utilisant systemd, examiner les messages du service SSH :

```bash
sudo journalctl -u ssh --since today
```

Ou selon le nom du service :

```bash
sudo journalctl -u sshd --since today
```

Pour rechercher certains termes dans les fichiers de journalisation classiques :

```bash
sudo grep -Ei "failed|invalid user|authentication failure" /var/log/auth.log
```

Cette commande suppose que le fichier existe et que les messages correspondants y sont enregistrés. Selon la distribution, la source pourra être différente.

### 23.3 Sous Windows

Les événements de sécurité dépendent de la stratégie d’audit activée et des autorisations de lecture.

On peut examiner les journaux dans l’Observateur d’événements ou avec PowerShell :

```powershell
Get-WinEvent -LogName Security -MaxEvents 50
```

Cette commande peut nécessiter une console élevée ou un compte disposant des permissions adéquates.

Les événements de sécurité peuvent contenir des informations sensibles. Il faut limiter l’accès et respecter les exigences de conservation de l’organisation.

### 23.4 Principe important

Les journaux ne remplacent pas :

- La gestion des identités.
- Les contrôles d’accès.
- Les correctifs de sécurité.
- Les sauvegardes.
- Les pare-feu.
- La protection des postes et des serveurs.
- Les mécanismes de détection et de réponse adaptés.

Ils constituent une source d'observation qui aide à comprendre et à documenter ce qui s’est passé.

## 24. Protéger les journaux

### 24.1 Limiter les données sensibles

Les journaux peuvent contenir :

- Des noms d’utilisateurs.
- Des adresses IP.
- Des chemins internes.
- Des fragments de requêtes.
- Des identifiants de session.
- Des données personnelles.
- Des informations sur les erreurs applicatives.

Il faut éviter d’y enregistrer les mots de passe, les clés privées et les jetons d’accès complets.

Un journal trop bavard peut devenir une source de fuite de données.

### 24.2 Contrôler les permissions

Les journaux doivent être accessibles aux personnes qui en ont besoin, mais pas à tous les utilisateurs.

Sous Linux, examiner les permissions :

```bash
ls -l /var/log
```

Ne pas appliquer aveuglément des permissions globales ou récursives pour résoudre un problème d’accès. Les droits doivent suivre le fonctionnement attendu des services.

### 24.3 La rétention

La rétention détermine combien de temps les journaux sont conservés.

Elle dépend de plusieurs facteurs :

- Capacité de stockage.
- Besoins opérationnels.
- Exigences de sécurité.
- Contraintes contractuelles.
- Besoins d’audit.
- Règles applicables à l’organisation.
- Sensibilité des données.

Une conservation trop courte peut faire perdre des preuves nécessaires. Une conservation excessive augmente les coûts et peut accroître les risques liés à l’accès aux données.

### 24.4 Rotation des journaux

Un service qui écrit continuellement dans un fichier peut remplir le disque.

La rotation consiste à archiver, renommer, compresser ou supprimer des journaux selon une politique définie.

Linux utilise fréquemment `logrotate` pour les fichiers de journaux classiques.

Vérifier sa présence :

```bash
logrotate --version
```

Lister les configurations courantes :

```bash
ls /etc/logrotate.conf /etc/logrotate.d/
```

La rotation doit être adaptée au service concerné. Certains programmes nécessitent un rechargement ou un signal particulier pour recommencer à écrire dans un nouveau fichier.

Le journal systemd possède ses propres paramètres de rétention, qui ne se gèrent pas nécessairement de la même façon que les fichiers classiques.

### 24.5 Protéger la collecte centralisée

Une architecture de production doit prendre en compte :

- Les droits d’administration.
- La sécurité des communications.
- La séparation entre collecte et consultation.
- La protection contre la suppression accidentelle.
- Les copies de sauvegarde nécessaires.
- La surveillance de l’espace disponible.
- Les politiques de conservation.
- Le contrôle des exports et téléchargements.
- Les accès des équipes et des clients.

La centralisation ne garantit pas automatiquement l’intégrité des journaux : le système central doit lui aussi être sécurisé et administré.

## 25. Structurer les messages et les horodatages

### 25.1 Pourquoi les formats sont-ils importants ?

Les messages structurés facilitent le filtrage et les corrélations.

Un message difficile à analyser :

```text
Une erreur s'est produite pour le client hier.
```

Un message plus exploitable :

```json
{
  "timestamp": "2026-10-24T08:15:32Z",
  "level": "ERROR",
  "service": "payment-api",
  "host": "srv-app-01",
  "event": "database_timeout",
  "request_id": "req-12345"
}
```

Cet exemple est fictif. Il illustre des champs qui permettent de filtrer les événements par service, date ou identifiant de requête.

Dans un système réel, ne pas utiliser un identifiant de requête prévisible si cela compromet la confidentialité ou la sécurité. Éviter également d’insérer des données sensibles dans les champs descriptifs.

### 25.2 Synchronisation de l'heure

Les serveurs doivent utiliser une synchronisation horaire cohérente, généralement via un mécanisme NTP adapté.

Si deux machines ont une différence d’horloge importante, il peut sembler qu’un événement se soit produit avant un autre alors que ce n’est pas le cas.

Lors d’un incident multi-serveurs, vérifier :

- Le fuseau horaire.
- La synchronisation de l’horloge.
- Le format des horodatages.
- La présence d’un identifiant de requête commun, si disponible.

### 25.3 Corrélation des événements

Supposons qu’une requête passe par un reverse proxy, une application et une base de données.

Si chaque composant enregistre un identifiant de corrélation cohérent, la recherche devient plus simple.

```text
Requête req-12345
       |
       v
Reverse proxy
  req-12345
       |
       v
Application
  req-12345
       |
       v
Base de données
  req-12345
```

Sans identifiant commun, il faut davantage s’appuyer sur les horodatages, les adresses et les paramètres de requête, avec un risque accru de confusion.

## 26. Choisir une solution de supervision

Il n’existe pas un seul outil idéal pour tous les environnements.

### 26.1 Principales approches

| Solution | Usage courant | Point d'attention |
|---|---|---|
| Zabbix | Supervision d'infrastructures, hôtes, services et équipements | Configurer les modèles, agents et alertes |
| Prometheus | Collecte et interrogation de métriques | Nécessite des cibles ou exportateurs adaptés |
| Grafana | Visualisation et tableaux de bord | Dépend des sources de données configurées |
| rsyslog | Collecte et transfert de journaux | Nécessite une politique de routage et de stockage |
| Loki | Stockage et interrogation de journaux avec un écosystème associé | Demande une conception de collecte et de rétention |
| OpenSearch | Recherche et analyse de données indexées, dont des journaux | Dimensionnement, exploitation et sécurité à prévoir |
| Solutions natives Windows | Journaux et mécanismes de supervision Windows | Les besoins centralisés peuvent nécessiter des composants complémentaires |

L’outil se choisit selon les systèmes à surveiller, le volume de données, les compétences de l’équipe, les contraintes de sécurité et la complexité acceptable.

### 26.2 Une architecture peut combiner plusieurs outils

```text
Linux -----------------> Journaux Linux
   |                          |
   |                          v
   |                    Collecteur de logs
   |                          |
   v                          v
Node Exporter             Stockage logs
   |                          |
   v                          |
Prometheus                   |
   |                          |
   +------------+-------------+
                |
                v
             Grafana
                |
                v
        Tableaux de bord
                |
                v
             Alertes
```

Il s’agit d’une architecture illustrative. Les connecteurs, les composants de stockage et les mécanismes de notification doivent être choisis et configurés selon le besoin.

### 26.3 Commencer petit

Pour une première installation, il est souvent préférable de surveiller quelques éléments essentiels :

1. Disponibilité des serveurs.
2. Utilisation CPU et mémoire.
3. Espace disque.
4. Disponibilité des services importants.
5. Dernier succès des sauvegardes.
6. Erreurs importantes des journaux.

Une fois le dispositif compris et utile, l’équipe peut l’étendre à des contrôles plus avancés.

## 27. Travaux pratiques guidés

Les travaux pratiques suivants peuvent être effectués sur des machines de test ou un laboratoire. Ne pas modifier volontairement un système de production pour apprendre les commandes.

### TP 1 — Explorer les journaux Linux

**Objectif :** identifier les sources de journaux et rechercher un événement.

Étapes :

1. Lister les fichiers de `/var/log`.
2. Afficher les 20 dernières lignes d’un fichier disponible.
3. Examiner les événements avec `journalctl`.
4. Afficher les événements du service SSH.
5. Envoyer un message de test avec `logger`.
6. Rechercher ce message.

Commandes de départ :

```bash
ls -lah /var/log
sudo journalctl -n 30
sudo journalctl -u ssh -n 30
logger "LAB-MONITORING-01"
sudo journalctl -b --grep="LAB-MONITORING-01"
```

Adapter le nom du service SSH à la distribution.

**Résultat attendu :** l’apprenant sait où chercher et peut retrouver un événement dont il connaît le contenu.

### TP 2 — Examiner la santé d'un serveur

**Objectif :** relever les principales métriques d’un système Linux.

Exécuter :

```bash
uptime
top
free -h
df -h
ip -s link
ss -lnt
```

Pour chaque commande, noter :

- Ce qui est mesuré.
- La signification des colonnes importantes.
- Les éléments qui semblent normaux.
- Les éléments qui nécessiteraient une enquête.

**Résultat attendu :** une fiche décrivant l’état CPU, mémoire, stockage et réseau du serveur observé.

### TP 3 — Consulter les événements Windows

**Objectif :** apprendre à filtrer les événements.

Dans PowerShell :

```powershell
Get-WinEvent -LogName System -MaxEvents 20 |
    Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message
```

Puis filtrer les erreurs récentes :

```powershell
$since = (Get-Date).AddHours(-24)

Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    StartTime = $since
    Level     = 2
} | Select-Object TimeCreated, Id, ProviderName, Message
```

Interpréter les événements à partir du fournisseur, du texte et du contexte.

**Résultat attendu :** un court rapport contenant les événements intéressants et la raison de leur sélection.

### TP 4 — Construire une matrice de supervision

**Objectif :** décider quoi surveiller.

Créer un tableau avec au moins cinq services :

- Serveur Web.
- Serveur de fichiers.
- DNS.
- Base de données.
- Service de sauvegarde.

Pour chaque service, préciser :

- La méthode de contrôle.
- La fréquence de contrôle.
- Les métriques importantes.
- Les journaux à consulter.
- Le seuil d’alerte initial.
- La gravité.
- L’équipe responsable.
- La première action à effectuer.

**Résultat attendu :** une matrice pouvant servir de base à une première configuration de supervision.

### TP 5 — Créer un tableau de bord

**Objectif :** organiser les indicateurs de santé.

Avec un outil de supervision disponible, construire un tableau de bord contenant :

- État des hôtes.
- CPU.
- Mémoire.
- Stockage.
- Disponibilité d’un service.
- Événements ou alertes significatifs.

Le tableau doit donner une vue d’ensemble puis permettre d’identifier le système à examiner.

**Résultat attendu :** un tableau de bord simple, accompagné d’une phrase expliquant ce que chaque panneau permet de décider.

### TP 6 — Tester une alerte

**Objectif :** vérifier le cycle de vie d’une alerte.

Définir un contrôle adapté à un environnement de laboratoire, par exemple la disponibilité d’un endpoint de test.

Effectuer les étapes suivantes :

1. Vérifier que la cible fonctionne.
2. Vérifier que la métrique indique un état normal.
3. Simuler une indisponibilité contrôlée.
4. Observer le délai de détection.
5. Vérifier si la notification est émise.
6. Rétablir le service.
7. Vérifier que l’état revient à la normale.
8. Documenter le résultat.

**Résultat attendu :** un compte rendu qui distingue le délai de détection, le délai de notification et le délai de rétablissement.

## 28. Exercices d'application

### Exercice 1 — Identifier le type de donnée

Classer chaque élément comme journal, métrique, contrôle de disponibilité ou alerte.

A. `CPU utilisé : 87 %`

B. `08:14:00 ERROR Connexion à la base de données échouée`

C. `Le test HTTPS n'a pas obtenu de réponse valide`

D. `Le disque dépasse 90 % depuis 10 minutes ; notification envoyée`

**Correction :**

- A : métrique.
- B : journal.
- C : résultat d’un contrôle de disponibilité.
- D : alerte déclenchée à partir d’une règle.

### Exercice 2 — Disque saturé

Un serveur déclenche une alerte lorsque l’occupation d’un volume dépasse 90 %. Le volume atteint 97 %.

Quelle est la première démarche ?

**Correction :**

Identifier le point de montage concerné, mesurer l’espace utilisé, rechercher les répertoires volumineux et examiner la cause de la croissance. Ensuite, choisir une correction adaptée et contrôler que l’espace disponible est revenu à un niveau acceptable.

Il ne faut pas supprimer arbitrairement les fichiers les plus volumineux.

### Exercice 3 — Service actif mais site inaccessible

`systemctl is-active nginx` indique `active`, mais les utilisateurs n’arrivent pas à ouvrir le site.

Citer quatre vérifications possibles.

**Correction :**

- Tester la réponse HTTP.
- Vérifier le port d’écoute.
- Consulter les journaux Nginx.
- Vérifier le DNS, le routage et les règles réseau.
- Examiner le service applicatif en amont.
- Vérifier les certificats TLS si le problème concerne HTTPS.

Le statut `active` confirme uniquement l’état rapporté par systemd. Il ne garantit pas que toutes les requêtes utilisateurs fonctionnent.

### Exercice 4 — Alerte CPU

Une alerte signale 95 % de CPU pendant dix minutes.

Pourquoi ne faut-il pas redémarrer immédiatement la machine ?

**Correction :**

Le redémarrage peut interrompre le service et détruire des éléments utiles à l’analyse. Il faut d’abord examiner la charge, les processus, les métriques, les journaux et les changements récents. Une mesure corrective doit reposer sur une hypothèse vérifiée autant que possible.

### Exercice 5 — Journaux Windows

Tu souhaites afficher les 15 derniers événements du journal Application.

Écrire la commande PowerShell.

**Correction :**

```powershell
Get-WinEvent -LogName Application -MaxEvents 15
```

### Exercice 6 — Métrique `up`

Une cible Prometheus présente la valeur `up = 0`.

Quelle conclusion peut-on tirer ?

**Correction :**

Prometheus n’a pas réussi à collecter cette cible lors du contrôle correspondant. Cela peut résulter d’un problème du service exposant les métriques, du réseau, de l’exportateur ou de la configuration de collecte.

On ne peut pas conclure à coup sûr que tout le serveur est arrêté.

### Exercice 7 — Trop d'alertes

L’équipe reçoit 400 alertes par heure, dont beaucoup concernent le même incident.

Que peut-on améliorer ?

**Correction :**

Examiner les alertes réellement actionnables, regrouper les événements liés, adapter les seuils et délais, éviter les doublons et configurer un routage vers les bons responsables. Il faut également vérifier si plusieurs alertes techniques correspondent à une seule panne plus large.

### Exercice 8 — Journaux manquants

Après un redémarrage, des événements anciens ne sont plus visibles avec `journalctl`.

Donner une cause possible et une vérification.

**Correction :**

Le journal peut être configuré pour utiliser uniquement un stockage volatil, ou la durée de conservation peut avoir expiré. Vérifier la configuration de journald, la disponibilité des anciens démarrages et les limites de rétention.

### Exercice 9 — Corrélation entre serveurs

Une application comprend un serveur Web et une base de données. Les journaux indiquent une erreur à 14 h 00 sur le serveur Web et une erreur à 13 h 58 sur la base de données.

Que faut-il vérifier avant d’établir un lien ?

**Correction :**

Vérifier la synchronisation des horloges, les fuseaux horaires, la chronologie, les identifiants de requête et les événements intermédiaires. Deux événements proches dans le temps ne prouvent pas automatiquement une relation de cause à effet.

### Exercice 10 — Choix d'outil

Une équipe doit suivre les valeurs CPU et mémoire de plusieurs serveurs Linux et afficher leur évolution sur un tableau de bord.

Quel assemblage peut convenir ?

**Correction :**

Node Exporter pour exposer les métriques des hôtes, Prometheus pour les collecter et les stocker, et Grafana pour les visualiser. Une autre solution de supervision intégrée peut également convenir selon le contexte.

## 29. Projet de fin de niveau

### Mettre en place une supervision élémentaire

Le projet consiste à concevoir un dispositif de surveillance pour une petite infrastructure comprenant :

- Un serveur Linux.
- Un serveur Windows.
- Un service Web.
- Un stockage contenant des données importantes.
- Un service ou une tâche de sauvegarde.

L’objectif est de déterminer comment observer ces systèmes, détecter un problème et retrouver les informations nécessaires au diagnostic.

### Livrable A — Inventaire

Pour chaque système, documenter :

- Nom.
- Rôle.
- Responsable.
- Adresse ou méthode d’accès.
- Services importants.
- Niveau de criticité.
- Sources de journaux.

### Livrable B — Stratégie de collecte

Indiquer :

- Les journaux à consulter.
- Les métriques à collecter.
- Les contrôles de disponibilité.
- Les exigences de conservation.
- Les moyens de protection des données.

### Livrable C — Règles d'alerte

Créer au moins cinq règles adaptées, par exemple :

- Disque presque plein.
- Service Web indisponible.
- Hôte non joignable.
- Échec d’une sauvegarde.
- Absence de données de supervision.

Pour chaque règle, expliquer son objectif, le seuil retenu, la gravité, la personne à notifier et l’action initiale.

### Livrable D — Tableau de bord

Construire une vue regroupant les informations prioritaires.

Le tableau de bord doit aider à repérer rapidement :

- Les systèmes en difficulté.
- Les alertes actives.
- Les tendances de consommation.
- Les dernières erreurs importantes.
- Les derniers succès de sauvegarde.

### Livrable E — Rapport d'incident

Simuler un problème, comme un service Web indisponible ou un disque presque plein.

Rédiger un rapport comprenant :

- Heure de détection.
- Symptômes observés.
- Périmètre impacté.
- Journaux et métriques consultés.
- Hypothèse retenue.
- Action corrective.
- Validation du rétablissement.
- Prévention ou amélioration proposée.

### Critères de réussite

Le projet est réussi lorsque l’apprenant sait expliquer :

1. Ce qui est surveillé.
2. Comment l’information est collectée.
3. Quelle condition déclenche une alerte.
4. Comment les journaux permettent de diagnostiquer le problème.
5. Comment vérifier que le service est revenu à la normale.
6. Comment protéger les données collectées.

La création d’un tableau de bord seule ne suffit pas : les contrôles, les alertes et la démarche de diagnostic doivent également être compris.

## 30. Bonnes pratiques à mémoriser

### Journaux

- Rechercher les événements autour de l’heure du problème.
- Filtrer par service ou composant.
- Comparer plusieurs sources.
- Vérifier l’horodatage et le fuseau horaire.
- Ne pas interpréter un message isolément.
- Protéger les informations sensibles.
- Prévoir la rotation et la rétention.
- Centraliser les journaux lorsque le besoin le justifie.

### Métriques

- Surveiller des indicateurs utiles à la décision.
- Examiner les tendances, pas uniquement une valeur instantanée.
- Adapter les seuils aux besoins de chaque service.
- Conserver une marge de ressources.
- Distinguer l’utilisation d’une ressource de la santé du service.

### Alertes

- Créer des alertes actionnables.
- Indiquer clairement l’hôte et le service concernés.
- Réduire les notifications répétitives.
- Définir une procédure pour chaque alerte importante.
- Tester les notifications et le retour à la normale.
- Distinguer une panne réelle d’un problème de collecte.

### Diagnostic

- Confirmer l’impact avant d'agir.
- Examiner les changements récents.
- Préserver les informations utiles.
- Formuler des hypothèses testables.
- Éviter les redémarrages sans diagnostic.
- Vérifier le service après la correction.
- Documenter les incidents significatifs.

## 31. Glossaire

**Alerte :** notification produite lorsqu’une condition de supervision est remplie.

**Agent :** composant installé sur un système afin de fournir des informations ou d’effectuer des contrôles.

**Centralisation des journaux :** regroupement de messages provenant de plusieurs systèmes dans une plateforme commune.

**Collecte :** processus qui récupère les journaux ou métriques d’une source.

**Dashboard :** tableau de bord présentant des informations de supervision.

**Exportateur :** composant qui rend des métriques disponibles pour un système de collecte compatible.

**Gravité :** niveau associé à l’importance technique d’un événement.

**Grafana :** plateforme de visualisation de données permettant notamment de construire des tableaux de bord et de gérer des alertes selon la configuration choisie.

**Journal :** enregistrement d’un événement produit par un système, une application ou un équipement.

**Journal systemd :** ensemble d’événements stockés et gérés par systemd-journald sur les systèmes qui utilisent ce mécanisme.

**Métrique :** mesure numérique observée dans le temps.

**Node Exporter :** exportateur de métriques système pour les environnements Linux et apparentés.

**Prometheus :** système de collecte et de stockage de métriques en séries temporelles.

**Rétention :** durée pendant laquelle les données sont conservées.

**Rotation :** mécanisme qui gère les fichiers de journaux anciens et la création de nouveaux fichiers.

**rsyslog :** service de journalisation capable de recevoir, filtrer et transmettre des messages.

**Série temporelle :** suite de valeurs associées à des horodatages.

**Supervision :** observation régulière de systèmes ou services afin de détecter les dégradations et vérifier leur fonctionnement.

**Syslog :** famille de formats et de mécanismes utilisés pour la transmission de messages de journalisation.

**Windows Event Log :** mécanisme Windows permettant de stocker et de consulter des événements système et applicatifs.

**SLI :** indicateur mesurant un aspect concret de la qualité d’un service.

**SLO :** objectif quantifié associé à un indicateur de service.

**SLA :** engagement de niveau de service défini entre des parties.

## 32. Documentation officielle

### Linux et journaux

- Manuel `journalctl` : https://www.freedesktop.org/software/systemd/man/latest/journalctl.html
- Documentation systemd : https://systemd.io/
- Documentation officielle rsyslog : https://docs.rsyslog.com/doc/
- Premiers pas avec rsyslog : https://docs.rsyslog.com/doc/getting_started/index.html

### Windows

- Documentation PowerShell `Get-WinEvent` : https://learn.microsoft.com/fr-fr/powershell/module/microsoft.powershell.diagnostics/get-winevent
- Événements Windows : https://learn.microsoft.com/en-us/windows/win32/eventlog/event-identifiers

### Prometheus

- Présentation de Prometheus : https://prometheus.io/docs/introduction/overview/
- Premiers pas avec Prometheus : https://prometheus.io/docs/introduction/first_steps/
- Supervision des systèmes Linux avec Node Exporter : https://prometheus.io/docs/guides/node-exporter/
- Documentation des règles d'alerte : https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/

### Grafana

- Documentation générale : https://grafana.com/docs/grafana/latest/
- Configuration des règles d'alerte : https://grafana.com/docs/grafana/latest/alerting/alerting-rules/
- Gestion des notifications : https://grafana.com/docs/grafana/latest/alerting/fundamentals/notifications/

### Autres solutions

- Documentation officielle Zabbix : https://www.zabbix.com/documentation/current/en/manual
- Documentation officielle Loki : https://grafana.com/docs/loki/latest/

Les documentations évoluent. Avant de déployer en production, sélectionner la version correspondant à l’environnement utilisé et consulter les procédures de sécurité, de configuration et de mise à niveau.

## 33. Conclusion du niveau débutant

Les journaux expliquent ce que les systèmes ont enregistré. Les métriques décrivent leur évolution. La supervision vérifie leur fonctionnement et les alertes signalent les situations qui méritent une intervention.

La démarche essentielle est simple :

```text
OBSERVER
   |
   v
DETECTER
   |
   v
COMPRENDRE
   |
   v
AGIR
   |
   v
VERIFIER
   |
   v
DOCUMENTER
```

Un bon administrateur ne se contente pas de constater qu’un serveur fonctionne ou qu’une erreur apparaît. Il doit savoir où chercher, comprendre les informations, mesurer l’impact, agir avec méthode et confirmer le résultat.

Ce cours constitue la base nécessaire pour aborder ensuite la collecte centralisée avancée, les tableaux de bord multi-systèmes, les alertes complexes, la corrélation d’événements et l’observabilité à l’échelle d’une infrastructure entière.