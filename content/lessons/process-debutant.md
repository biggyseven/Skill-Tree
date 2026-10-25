# Gestion des processus Linux — Niveau Débutant

> **Fichier :** `process-debutant.md`  
> **Niveau :** Débutant  
> **Domaine :** Administration système Linux  
> **Thème :** Comprendre, observer, surveiller et contrôler les processus  
> **Environnement :** Linux avec Bash, idéalement Debian, Ubuntu, Linux Mint, Fedora ou une distribution similaire  
> **Prérequis :** Savoir ouvrir un terminal, exécuter des commandes, utiliser les chemins Linux et comprendre les bases des fichiers et des permissions.


# Sommaire

1. Introduction à la gestion des processus
2. Comprendre les programmes et les processus
3. Le cycle de vie d'un processus
4. Les identifiants d'un processus
5. L'arbre des processus Linux
6. Les états des processus
7. Le système de fichiers `/proc`
8. Afficher les processus avec `ps`
9. Rechercher un processus avec `pgrep` et `pidof`
10. Surveiller les processus avec `top`
11. Comprendre le CPU, la mémoire et la charge système
12. Arrêter ou contrôler un processus avec les signaux
13. Comprendre le premier plan et l'arrière-plan
14. Modifier la priorité d'un processus
15. Comprendre la différence entre processus et service
16. Diagnostiquer un processus problématique
17. Bonnes pratiques de sécurité
18. Travaux pratiques guidés
19. Exercices d'application
20. Corrections des exercices
21. Défi final : diagnostic d'un serveur Linux
22. Correction détaillée du défi final
23. Checklist de compétences
24. Fiche de révision
25. Glossaire
26. Documentation officielle


# 1. Introduction à la gestion des processus

## 1.1. Qu'est-ce qu'un processus ?

Lorsque tu ouvres un terminal et que tu exécutes une commande, Linux doit lancer un programme pour effectuer le travail demandé.

Par exemple :

```bash
ls
```

Le programme `ls` affiche le contenu d'un répertoire. Pendant son exécution, le système suit cette activité à travers un **processus**.

Un processus est une instance d'un programme en cours d'exécution, avec son propre contexte d'exécution, des ressources attribuées et un état que le noyau Linux peut suivre.

Un processus peut notamment posséder :

- un identifiant unique pendant sa durée de vie, appelé PID ;
- un propriétaire, généralement un utilisateur Linux ;
- un ou plusieurs threads d'exécution ;
- une mémoire virtuelle ;
- des fichiers ouverts ;
- des connexions réseau éventuelles ;
- une priorité d'ordonnancement ;
- un état d'exécution ;
- un processus parent, lorsqu'il en possède un ;
- un code de retour lorsque son exécution se termine.

Ces éléments permettent au système d'exploitation de gérer plusieurs activités simultanément.

## 1.2. Pourquoi apprendre à gérer les processus ?

L'administration Linux ne consiste pas uniquement à installer des logiciels ou à modifier des fichiers de configuration.

Il faut aussi savoir ce qui fonctionne réellement sur le système.

Imagine les situations suivantes :

- Un programme ne répond plus.
- Un serveur Web utilise beaucoup de processeur.
- Une application consomme progressivement toute la mémoire disponible.
- Une commande lancée dans un terminal doit continuer en arrière-plan.
- Un programme a été démarré deux fois par erreur.
- Un service ne fonctionne plus.
- Un processus semble impossible à arrêter.
- Une machine paraît lente sans raison évidente.

Dans tous ces cas, l'administrateur doit observer les processus avant de choisir une action.

La méthode fondamentale est la suivante :

```text
                 PROBLÈME OBSERVÉ
                        |
                        v
              Identifier le processus
                        |
                        v
               Observer son état
                        |
                        v
            Examiner ses ressources
                        |
                        v
              Chercher la cause
                        |
                        v
             Choisir une action sûre
                        |
                        v
                Vérifier le résultat
```

La règle principale de ce cours est simple :

**Observer avant d'agir. Identifier avant d'arrêter. Vérifier après chaque intervention.**

## 1.3. Les objectifs du cours

À la fin de ce cours, tu dois être capable de :

- expliquer ce qu'est un processus ;
- distinguer un programme, un processus, un thread et un service ;
- identifier un processus avec son PID ;
- retrouver son parent et comprendre les relations entre processus ;
- lire les états les plus courants d'un processus ;
- consulter la liste des processus ;
- rechercher un processus par son nom ;
- surveiller l'utilisation du CPU et de la mémoire ;
- envoyer un signal à un processus ;
- différencier une demande d'arrêt normale d'un arrêt forcé ;
- lancer une commande en arrière-plan ;
- suspendre, reprendre et ramener une tâche au premier plan ;
- comprendre les priorités des processus ;
- distinguer l'administration d'un service de celle d'un processus isolé ;
- effectuer un diagnostic de base sans interrompre inutilement le système.


# 2. Comprendre les programmes et les processus

## 2.1. Un programme n'est pas la même chose qu'un processus

Un programme est généralement un fichier contenant du code exécutable ou un ensemble d'instructions interprétées.

Un processus est une exécution de ce programme.

Prenons un exemple.

Un système possède un interpréteur de commandes qui permet d'exécuter :

```bash
sleep 60
```

La commande `sleep 60` demande au programme `sleep` de patienter pendant 60 secondes.

On peut représenter cette relation ainsi :

```text
FICHIER EXÉCUTABLE
      sleep
        |
        | lancement de la commande
        v
PROCESSUS EN EXÉCUTION
        |
        +-- PID attribué par Linux
        |
        +-- Mémoire et contexte d'exécution
        |
        +-- Ressources utilisées
        |
        +-- Attente de 60 secondes
        |
        v
FIN DU PROCESSUS
```

Lorsque le processus se termine, le fichier exécutable `sleep` reste sur le disque. Il pourra être lancé de nouveau.

## 2.2. Un même programme peut avoir plusieurs processus

Prenons deux terminaux différents.

Dans le premier terminal :

```bash
sleep 120
```

Dans le second terminal :

```bash
sleep 120
```

Linux peut créer deux processus distincts à partir du même programme.

```text
PROGRAMME : sleep
       |
       +----------------------+
       |                      |
       v                      v
PROCESSUS A               PROCESSUS B
PID : 4101                PID : 5274
Durée : 120 s             Durée : 120 s
```

Les PID ci-dessus sont illustratifs. Les véritables identifiants dépendent du système.

Les deux processus sont indépendants du point de vue de leur identité, même s'ils exécutent le même programme.

Cela explique pourquoi le nom du programme ne suffit pas toujours pour identifier une instance précise.

## 2.3. Un processus peut contenir plusieurs threads

Un thread est un fil d'exécution à l'intérieur d'un processus.

Un processus classique peut posséder un seul thread ou plusieurs threads.

Les threads d'un même processus partagent généralement une grande partie des ressources du processus, notamment son espace mémoire, tout en disposant de leur propre contexte d'exécution.

Exemple conceptuel :

```text
PROCESSUS : application-web
PID : 7000
|
+-- Espace mémoire du processus
|
+-- Fichiers ouverts
|
+-- Thread 1 : traitement des requêtes
|
+-- Thread 2 : traitement des requêtes
|
+-- Thread 3 : journalisation
|
+-- Thread 4 : tâches internes
```

Cette structure est simplifiée : les processus peuvent être organisés de différentes manières selon les applications.

À retenir :

- Le **processus** constitue une unité importante d'exécution et de gestion des ressources.
- Le **thread** constitue un fil d'exécution au sein d'un processus.
- Une application peut utiliser plusieurs threads pour traiter plusieurs activités.

Dans ce cours, nous observerons principalement les processus. La gestion détaillée des threads sera étudiée à un niveau ultérieur.

## 2.4. Comment Linux lance-t-il un processus ?

Sur les systèmes de type Unix, la création et le lancement d'un processus font intervenir des mécanismes du noyau.

À un niveau conceptuel :

1. Un processus existant demande la création d'un nouveau processus.
2. Le noyau crée le contexte nécessaire.
3. Le nouveau processus peut ensuite exécuter un autre programme.
4. Le processus utilise les ressources dont il a besoin.
5. Il se termine et transmet un résultat à son parent.

Les appels système `fork()`, `clone()` et `execve()` participent à ces mécanismes selon le contexte. Il n'est pas nécessaire de connaître leur fonctionnement interne pour administrer des processus au niveau débutant.

L'idée essentielle est que le lancement d'une commande n'est pas simplement l'affichage d'un nom dans le terminal : le système doit établir une exécution qu'il peut gérer et surveiller.


# 3. Le cycle de vie d'un processus

## 3.1. Les grandes étapes

Un processus ne reste pas nécessairement actif sur le processeur en permanence.

Il peut être prêt à s'exécuter, en cours d'exécution, en attente d'une ressource ou en train de se terminer.

Le cycle général peut être représenté ainsi :

```text
                  LANCEMENT
                      |
                      v
               CRÉATION DU
                 PROCESSUS
                      |
                      v
             PROCESSUS PRÊT
                      |
                      v
             EXÉCUTION SUR CPU
                      |
             +--------+--------+
             |                 |
             v                 v
       ATTENTE I/O       BESOIN D'UN
       OU ÉVÉNEMENT      AUTRE CRÉNEAU CPU
             |                 |
             v                 |
       RÉVEIL DU PROCESSUS     |
             |                 |
             +--------+--------+
                      |
                      v
             NOUVELLE EXÉCUTION
                      |
                      v
               TERMINAISON
                      |
                      v
          STATUT DE FIN RÉCUPÉRÉ
             PAR LE PARENT
```

Ce schéma est pédagogique. Le noyau peut gérer de nombreuses transitions différentes selon l'activité du processus.

## 3.2. Création

Un processus est lancé lorsqu'un programme ou un mécanisme du système demande son exécution.

Exemples :

```bash
ls
```

```bash
sleep 30
```

```bash
python3 --version
```

Les commandes ne génèrent pas nécessairement toutes le même type de processus : certaines sont des commandes internes du shell, tandis que d'autres sont des programmes externes.

## 3.3. Exécution

Lorsqu'il dispose d'un créneau d'ordonnancement, un processus peut exécuter des instructions sur un processeur logique.

Un système moderne alterne rapidement entre les processus et les threads qui sont prêts à s'exécuter.

Cette alternance donne l'impression que de nombreuses applications travaillent simultanément, même si le système ne possède qu'un seul cœur de calcul.

Sur une machine multicœur, plusieurs tâches peuvent réellement s'exécuter en parallèle.

## 3.4. Attente

Un processus peut devoir attendre :

- une lecture depuis le disque ;
- la réception de données réseau ;
- une réponse d'un autre programme ;
- la libération d'un verrou ;
- l'expiration d'un délai ;
- la disponibilité d'un événement.

Un processus en attente n'est donc pas nécessairement bloqué ou défectueux.

Par exemple, la commande suivante attend volontairement :

```bash
sleep 30
```

Elle n'a pas besoin de consommer continuellement du CPU pour atteindre son objectif.

## 3.5. Terminaison et code de retour

Lorsqu'un processus se termine, il peut fournir un code de retour.

Convention courante :

- `0` : réussite ;
- valeur non nulle : problème ou résultat particulier.

Pour l'illustrer :

```bash
true
echo $?
```

La valeur obtenue après la commande `true` doit être `0`.

Essayons maintenant :

```bash
false
echo $?
```

La valeur obtenue après `false` doit être `1`.

La variable spéciale `$?` contient le code de retour de la commande exécutée juste avant.

Attention : toute nouvelle commande remplace cette valeur. Il faut donc lire `$?` immédiatement si l'on veut connaître le résultat de la commande précédente.

Un code non nul ne signifie pas toujours qu'un programme a subi une panne matérielle. Il peut simplement signaler qu'une recherche n'a rien trouvé ou qu'une condition attendue n'est pas remplie.

## 3.6. Parent, enfant et récupération du statut

Lorsqu'un processus crée un autre processus, le premier est appelé le parent et le second l'enfant.

Le parent peut récupérer le statut de fin de son enfant grâce aux mécanismes de synchronisation du système.

```text
PROCESSUS PARENT
      |
      | création
      v
PROCESSUS ENFANT
      |
      | exécution
      v
TERMINAISON DE L'ENFANT
      |
      v
LE PARENT RÉCUPÈRE
LE STATUT DE FIN
```

Ce mécanisme permet au système de suivre la terminaison des processus et d'éviter que leurs informations de fin restent inutilement enregistrées.

Les notions d'enfant, de parent et de récupération du statut deviennent importantes pour comprendre les zombies, les scripts shell et les services.


# 4. Les identifiants d'un processus

## 4.1. Le PID

PID signifie **Process Identifier**, c'est-à-dire identifiant de processus.

Linux attribue un PID à chaque processus.

Pour observer des processus :

```bash
ps -ef
```

Exemple fictif :

```text
UID       PID   PPID  C STIME TTY      TIME     CMD
root        1      0  0 08:00 ?        00:00:02 systemd
alice    4101   4012  0 08:10 pts/0    00:00:00 sleep 120
alice    4107   4020  0 08:11 pts/1    00:00:00 sleep 120
```

Ici :

- `PID` désigne le processus ;
- `4101` est un exemple de PID ;
- `4107` est un autre PID ;
- les deux lignes désignent deux processus distincts.

Les valeurs affichées dans cet exemple ne correspondent pas à des PID garantis sur ta machine.

Les PID sont réutilisables après la disparition d'un processus. Il ne faut donc pas considérer un numéro de PID mémorisé depuis longtemps comme l'identité permanente d'une application.

## 4.2. Le PPID

PPID signifie **Parent Process Identifier**.

Il s'agit de l'identifiant du processus parent.

Dans cet extrait :

```text
UID       PID   PPID  CMD
alice    4101   4012  sleep 120
```

Le processus `4101` possède le PID `4012` comme parent.

Le PPID aide à comprendre l'origine d'un processus.

Par exemple, si un programme a été lancé par un script, ce script peut apparaître comme parent. La relation exacte dépend toutefois du programme et de la manière dont il a été lancé.

## 4.3. L'utilisateur propriétaire

Un processus possède un identifiant d'utilisateur effectif, et d'autres informations relatives à ses identifiants de sécurité.

La colonne `USER` ou `UID` dans les outils de consultation permet généralement de repérer l'utilisateur effectif affiché par l'outil.

Un processus lancé par un utilisateur normal ne possède pas automatiquement les privilèges de `root`.

Cette distinction est essentielle pour la sécurité : un utilisateur ne peut généralement pas envoyer n'importe quel signal à n'importe quel processus appartenant à un autre utilisateur.

## 4.4. Autres identifiants utiles

Au-delà du PID et du PPID, Linux et les outils d'administration utilisent d'autres notions :

| Identifiant | Signification générale |
|---|---|
| PID | Identifiant d'un processus |
| PPID | Identifiant du parent |
| UID | Identifiant d'utilisateur |
| GID | Identifiant de groupe |
| PGID | Identifiant du groupe de processus |
| SID | Identifiant de session de processus |
| TTY | Terminal de contrôle associé, lorsqu'il existe |

Ces identifiants ne remplissent pas la même fonction.

Le PID identifie un processus, tandis que le PGID et le SID aident notamment à organiser des processus liés à une tâche ou à une session.

Ils seront particulièrement utiles lorsque nous étudierons la gestion des tâches dans un terminal.


# 5. L'arbre des processus Linux

## 5.1. Qu'est-ce qu'un arbre de processus ?

Un système Linux ne fonctionne pas comme un ensemble de processus entièrement indépendants.

Les processus peuvent être liés par des relations parent-enfant.

On peut les représenter dans un arbre :

```text
systemd (PID 1)
|
+-- service-web
|   |
|   +-- processus-worker
|   |
|   +-- processus-worker
|
+-- sshd
|   |
|   +-- session utilisateur
|       |
|       +-- bash
|           |
|           +-- ps
|
+-- cron
```

Cet arbre est illustratif. Les noms, PID et relations réels varient selon la distribution et les applications installées.

Dans de nombreuses distributions Linux modernes, `systemd` est le processus d'initialisation principal, souvent appelé PID 1.

Des systèmes Linux peuvent néanmoins utiliser d'autres systèmes d'initialisation.

## 5.2. Pourquoi connaître le parent ?

Le parent donne un indice sur la manière dont un processus a été lancé.

Supposons qu'un programme inconnu consomme beaucoup de ressources.

L'examen de son PPID peut aider à répondre à des questions :

- A-t-il été lancé par une session utilisateur ?
- Provient-il d'un service système ?
- Est-il créé par un script ?
- Est-il l'un de plusieurs processus enfants d'une même application ?

Le parent n'est pas toujours suffisant pour connaître toute l'histoire d'un processus, mais c'est un point de départ utile.

## 5.3. Afficher l'arbre avec `ps`

La commande suivante peut afficher les processus sous forme arborescente :

```bash
ps -ef --forest
```

Dans les systèmes utilisant `procps`, l'option `--forest` permet une représentation visuelle des relations entre les processus.

Pour examiner uniquement les processus de l'utilisateur courant :

```bash
ps -u "$USER" -f
```

Le résultat dépend des processus actuellement présents.

## 5.4. Utiliser `pstree`

Si l'outil `pstree` est disponible :

```bash
pstree
```

Pour inclure les PID :

```bash
pstree -p
```

`pstree` peut ne pas être installé par défaut.

Sur certaines distributions, il est fourni par un paquet tel que `psmisc`.

L'installation éventuelle dépend de ta distribution et de tes privilèges.


# 6. Les états des processus

## 6.1. Pourquoi les états sont-ils importants ?

Deux processus peuvent sembler différents alors qu'ils exécutent le même programme.

L'un peut être actif sur le processeur, l'autre attendre des données et un troisième être suspendu.

L'état du processus permet de comprendre ce qu'il fait du point de vue du système.

Avec `ps`, cette information apparaît généralement dans la colonne `STAT` ou `S`.

## 6.2. Les états les plus importants

| Code | Signification générale | Interprétation de base |
|---|---|---|
| `R` | Running ou runnable | Le processus s'exécute ou est prêt à recevoir du CPU |
| `S` | Interruptible sleep | Le processus attend un événement |
| `D` | Uninterruptible sleep | Il attend généralement une opération noyau qui ne s'interrompt pas immédiatement par un signal |
| `T` | Stopped | Le processus est suspendu ou arrêté par un mécanisme de contrôle |
| `Z` | Zombie | Le processus est terminé, mais son statut n'a pas encore été récupéré par son parent |
| `I` | Idle kernel thread | État que l'on peut rencontrer sur certains threads noyau |

Les codes exacts et les informations complémentaires dépendent de l'outil et de la version du noyau.

## 6.3. État `R` : en exécution ou prêt

Un processus `R` peut être en train d'utiliser le CPU ou simplement prêt à s'exécuter.

Le noyau partage le temps CPU entre les tâches qui peuvent progresser.

Le code `R` ne garantit donc pas que le processus occupe continuellement un cœur de processeur.

## 6.4. État `S` : attente interruptible

Un processus `S` est généralement en attente d'un événement.

Exemples :

- `sleep 300` attend la fin d'un délai ;
- un serveur attend une nouvelle requête ;
- une application attend des données.

Un grand nombre de processus dans l'état `S` est normal sur un serveur qui héberge de nombreux services.

Il ne faut pas chercher à arrêter tous les processus en attente.

## 6.5. État `D` : attente non interruptible

L'état `D` est souvent rencontré lorsqu'un processus attend une opération du noyau, fréquemment liée aux entrées-sorties.

Un processus en état `D` peut rester dans cet état tant que la condition d'attente ne se résout pas.

Cela signifie qu'envoyer `SIGKILL` ne garantit pas une disparition immédiate du processus. Le signal peut ne produire son effet qu'après la fin de l'attente concernée.

Si de nombreux processus restent longtemps en état `D`, il peut être nécessaire d'examiner :

- les journaux du noyau ;
- les erreurs de stockage ;
- l'état des disques ;
- les systèmes de fichiers réseau ;
- les problèmes matériels ou de pilotes.

Il ne faut pas conclure automatiquement à une panne disque à partir d'une seule ligne `D`.

## 6.6. État `T` : processus suspendu

Un processus peut être suspendu à la suite d'un signal ou d'un contrôle de tâche.

Pour le démontrer, dans un terminal, exécute :

```bash
sleep 300
```

Appuie sur `Ctrl+Z`.

Le shell doit reprendre le contrôle et indiquer que la tâche a été suspendue.

Tu peux ensuite consulter :

```bash
jobs -l
```

Le processus n'a pas été terminé : il est suspendu.

## 6.7. État `Z` : zombie

Un zombie est un processus déjà terminé dont le parent n'a pas encore récupéré certaines informations de fin.

Il ne s'agit pas d'un programme qui continue à consommer normalement du CPU.

Schéma simplifié :

```text
PROCESSUS ENFANT
       |
       v
TERMINAISON
       |
       v
STATUT DE FIN À RÉCUPÉRER
       |
       v
ÉTAT ZOMBIE TEMPORAIRE
       |
       v
LE PARENT RÉCUPÈRE LE STATUT
       |
       v
ENTRÉE DU PROCESSUS RETIRÉE
```

Un zombie isolé et de courte durée n'est généralement pas inquiétant.

Des zombies persistants peuvent indiquer un problème dans le programme parent, qui ne récupère pas correctement ses processus enfants.

**Important : on ne supprime généralement pas un zombie en envoyant `kill` à son PID, car il a déjà terminé son exécution.** Il faut comprendre pourquoi son parent ne récupère pas son statut.

Il n'est pas nécessaire de créer artificiellement des zombies pendant les travaux pratiques de ce cours.


# 7. Le système de fichiers `/proc`

## 7.1. Qu'est-ce que `/proc` ?

Sous Linux, `/proc` est un système de fichiers virtuel qui expose de nombreuses informations sur le noyau et les processus.

Il ne s'agit pas simplement d'un répertoire contenant des documents ordinaires stockés sur le disque.

Les informations y sont présentées dynamiquement.

Pour observer les premières entrées :

```bash
ls /proc
```

Tu trouveras notamment des répertoires portant des noms numériques :

```text
/proc/1
/proc/2
/proc/100
/proc/2500
```

Ces répertoires correspondent généralement à des PID présents dans l'espace de PID concerné.

Tous les nombres affichés ne sont pas obligatoirement des PID : `/proc` contient aussi des entrées telles que `cpuinfo`, `meminfo` et `uptime`.

## 7.2. Quelques fichiers importants

| Chemin | Utilité |
|---|---|
| `/proc/cpuinfo` | Informations sur les processeurs |
| `/proc/meminfo` | Informations sur la mémoire |
| `/proc/uptime` | Temps de fonctionnement et temps d'inactivité agrégé |
| `/proc/loadavg` | Informations sur la charge du système |
| `/proc/PID/status` | Informations structurées sur un processus |
| `/proc/PID/cmdline` | Arguments de commande présentés sous forme de données séparées par des octets nuls |
| `/proc/PID/fd/` | Descripteurs de fichiers ouverts par le processus |

Les données exactes et les permissions d'accès dépendent du noyau, de la configuration et des privilèges.

## 7.3. Lire les informations d'un processus

Pour découvrir les informations du PID 1 :

```bash
cat /proc/1/status
```

Le PID 1 est généralement le processus d'initialisation du système dans son espace de PID principal, mais les environnements de conteneurs peuvent présenter une organisation différente.

Tu peux observer des lignes telles que :

```text
Name:   systemd
State:  S (sleeping)
Pid:    1
PPid:   0
Uid:    0    0    0    0
Gid:    0    0    0    0
```

Ce résultat est illustratif. Sur ta machine, le nom du processus peut être différent.

## 7.4. Pourquoi consulter `/proc/PID/status` ?

Supposons que tu connaisses le PID d'une application.

```bash
PID=1234
```

Cette valeur est un exemple : remplace-la par un PID existant.

Tu peux ensuite examiner :

```bash
cat "/proc/$PID/status"
```

Tu peux ainsi trouver le nom du processus, ses identifiants et son état, selon les champs accessibles.

Si le PID n'existe plus, ou si les permissions ne permettent pas l'accès, la commande échouera.

N'affiche pas automatiquement les variables d'environnement ou les descripteurs de tous les processus sur un système partagé : ils peuvent révéler des chemins internes, des jetons d'accès ou d'autres informations confidentielles.


# 8. Afficher les processus avec `ps`

## 8.1. La commande de base

La commande `ps` permet d'obtenir un instantané des processus.

```bash
ps
```

Sans option, elle affiche généralement les processus associés au terminal courant.

Elle ne surveille pas les processus en continu : elle produit un résultat au moment de son exécution.

## 8.2. Afficher les processus sous une forme détaillée

```bash
ps -ef
```

Sur les systèmes Linux utilisant `procps`, cette commande fournit une liste détaillée des processus.

Les colonnes les plus courantes comprennent :

| Colonne | Signification |
|---|---|
| `UID` | Utilisateur effectif affiché |
| `PID` | Identifiant du processus |
| `PPID` | Identifiant du parent |
| `C` | Indication liée à l'utilisation du CPU dans ce format |
| `STIME` | Heure de démarrage ou indication temporelle de début |
| `TTY` | Terminal associé, ou `?` s'il n'y en a pas |
| `TIME` | Temps CPU cumulé présenté par la commande |
| `CMD` | Commande affichée |

Les formats exacts peuvent varier selon les options et la version de `ps`.

## 8.3. Variante fréquente : `ps aux`

Une autre commande classique est :

```bash
ps aux
```

Elle utilise une syntaxe d'options de type BSD.

Il vaut mieux éviter de combiner mécaniquement les conventions d'options BSD et Unix dans une seule commande lorsque le résultat n'est pas clair.

Les administrateurs utilisent couramment `ps -ef` et `ps aux`, mais les présentations ne sont pas identiques.

## 8.4. Observer un seul processus

Supposons que le PID soit `1234`.

```bash
ps -p 1234 -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

Explication :

- `-p 1234` : sélectionne le PID demandé ;
- `-o` : choisit les colonnes à afficher ;
- `pid` : PID ;
- `ppid` : parent ;
- `user` : utilisateur effectif affiché ;
- `stat` : état ;
- `%cpu` : indication d'utilisation du CPU ;
- `%mem` : part approximative de mémoire physique associée au processus ;
- `etime` : temps écoulé depuis le démarrage ;
- `cmd` : commande affichée.

Si le processus s'est terminé, aucune ligne de processus correspondante ne sera affichée.

## 8.5. Afficher uniquement les processus de l'utilisateur courant

```bash
ps -u "$USER" -f
```

La variable `$USER` contient généralement le nom de l'utilisateur dans la session courante.

Cette commande est pratique pour repérer les commandes ou applications lancées par ton compte.

## 8.6. Trier les processus selon le CPU

Avec une version de `ps` qui prend en charge les options utilisées ci-dessous :

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,comm --sort=-%cpu | head -n 15
```

Explication :

- `-e` sélectionne tous les processus visibles par l'outil ;
- `-o` définit les colonnes ;
- `--sort=-%cpu` demande un tri décroissant selon la colonne CPU ;
- `head -n 15` limite l'affichage aux premières lignes du résultat.

Cette commande produit un instantané, pas un relevé continu.

Les pourcentages CPU dépendent de la méthode de calcul et de la période observée.

## 8.7. Trier par mémoire

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,rss,comm --sort=-%mem | head -n 15
```

La colonne `RSS` donne une estimation de la mémoire résidente du processus, exprimée dans les unités du format `ps`, généralement en kilo-octets sur Linux avec `procps`.

Il faut éviter de sommer aveuglément la mémoire RSS de tous les processus pour calculer la consommation exacte de la machine : des pages mémoire peuvent être partagées entre plusieurs processus.

## 8.8. Afficher les relations entre processus

```bash
ps -ef --forest
```

Cette variante est particulièrement utile quand tu souhaites comprendre quel programme a lancé une autre commande.


# 9. Rechercher un processus avec `pgrep` et `pidof`

## 9.1. Pourquoi rechercher un processus ?

Une sortie complète de `ps` peut contenir des centaines de lignes.

Il est souvent plus pratique de rechercher directement une application.

Les outils `pgrep` et `pidof` peuvent aider, selon le système et les logiciels installés.

## 9.2. Rechercher par nom

Exemple :

```bash
pgrep sleep
```

La commande affiche généralement les PID qui correspondent au nom ou au motif recherché.

Pour afficher les PID ainsi que les commandes correspondantes :

```bash
pgrep -a sleep
```

Si aucun résultat n'apparaît, cela signifie qu'aucune correspondance visible n'a été trouvée dans les conditions de la recherche.

## 9.3. Recherche exacte

```bash
pgrep -x sleep
```

L'option `-x` demande une correspondance exacte du nom de processus selon les règles de `pgrep`.

Une recherche exacte évite certains résultats non désirés, mais elle ne remplace pas la vérification du PID et de la commande réelle.

## 9.4. Utiliser `pidof`

Exemple :

```bash
pidof sleep
```

Selon la distribution, les caractéristiques du programme et les options, `pidof` peut retourner un ou plusieurs PID associés à un nom de programme.

Il n'est pas toujours installé par défaut.

## 9.5. Pourquoi le nom ne suffit-il pas ?

Plusieurs processus peuvent partager le même nom.

Par exemple :

```text
sleep 300    PID 4101
sleep 600    PID 4102
```

Si tu utilises une recherche par nom, tu peux obtenir les deux PID.

Avant d'envoyer un signal, vérifie le résultat :

```bash
ps -p 4101,4102 -o pid,ppid,user,stat,cmd
```

Ne lance pas une commande d'arrêt uniquement parce qu'un nom de processus ressemble à celui de l'application ciblée.


# 10. Surveiller les processus avec `top`

## 10.1. À quoi sert `top` ?

`top` permet de suivre l'activité des processus et les ressources du système dans une interface actualisée périodiquement.

Lance :

```bash
top
```

Une interface interactive apparaît généralement dans le terminal.

Pour quitter :

```text
q
```

Contrairement à `ps`, qui produit un instantané, `top` affiche régulièrement des informations actualisées.

## 10.2. Lire l'écran général

L'affichage peut présenter des informations sur :

- le temps depuis le démarrage ;
- la charge moyenne ;
- le nombre de tâches ;
- l'utilisation du CPU ;
- la mémoire ;
- les processus actifs.

Exemple schématique :

```text
top - 08:30:15 up 2 days,  3:10,  2 users,  load average: 0.45, 0.62, 0.71

Tasks: 180 total, 2 running, 178 sleeping, 0 stopped, 0 zombie

%Cpu(s):  5.0 us, 2.0 sy, 0.0 ni, 92.0 id, 1.0 wa

MiB Mem :  7800 total, 1200 free, 4100 used, 2500 buff/cache

PID   USER    PR  NI   VIRT   RES   SHR S  %CPU %MEM  TIME+  COMMAND
...
```

Les valeurs et la mise en page sont fictives. Les colonnes varient selon la version et la configuration de `top`.

## 10.3. Les colonnes principales

| Colonne | Signification |
|---|---|
| `PID` | Identifiant |
| `USER` | Utilisateur effectif affiché |
| `PR` | Priorité d'ordonnancement présentée par l'outil |
| `NI` | Valeur de nice |
| `VIRT` | Taille de la mémoire virtuelle associée |
| `RES` | Mémoire résidente |
| `SHR` | Estimation de mémoire partagée |
| `S` | État |
| `%CPU` | Utilisation estimée du CPU |
| `%MEM` | Part de mémoire estimée |
| `TIME+` | Temps CPU cumulé selon le format de l'outil |
| `COMMAND` | Nom ou représentation de la commande |

Les colonnes `VIRT`, `RES` et `SHR` ne mesurent pas exactement la même chose. Elles ne doivent pas être interprétées comme trois quantités directement additionnables.

## 10.4. Trier les processus

Dans de nombreuses versions de `top` :

- `P` trie les processus selon le CPU ;
- `M` trie les processus selon la mémoire ;
- `q` permet de quitter.

Les raccourcis exacts peuvent dépendre de la version et de la configuration.

## 10.5. Comparer `ps` et `top`

| Critère | `ps` | `top` |
|---|---|---|
| Type de consultation | Instantané | Actualisation périodique |
| Format | Sortie texte facilement redirigeable | Interface interactive |
| Recherche rapide dans un script | Très pratique | Moins adaptée |
| Observation continue | Non, pas seul | Oui |
| Tri des processus | Options de commande | Interactif et selon options |
| Diagnostic initial | Très utile | Très utile |

Les deux outils se complètent.

Une méthode efficace consiste à repérer une anomalie avec `top`, puis à examiner le PID concerné avec `ps`.

## 10.6. Alternative : `htop`

Si `htop` est installé :

```bash
htop
```

Il fournit une interface interactive qui peut être plus facile à parcourir.

Il n'est cependant pas systématiquement installé sur toutes les distributions.

Savoir utiliser `ps` et `top` reste important, car ces outils sont courants sur de nombreux systèmes Linux.


# 11. Comprendre le CPU, la mémoire et la charge système

## 11.1. Qu'est-ce que le CPU ?

Le CPU exécute les instructions des processus et des threads.

L'utilisation du processeur dépend notamment :

- du nombre de tâches actives ;
- de la quantité de travail à réaliser ;
- du nombre de cœurs disponibles ;
- de l'attente des entrées-sorties ;
- de la nature des applications.

Un processus qui effectue beaucoup de calculs peut utiliser beaucoup de CPU.

Un processus qui attend des données peut rester inactif pendant de longues périodes, même s'il est essentiel au fonctionnement d'un service.

## 11.2. Interpréter `%CPU`

La colonne `%CPU` est une estimation liée à l'utilisation du temps processeur.

Il faut interpréter sa valeur selon l'outil, sa version, la période de mesure et les options.

Sur un système multicœur, certains outils peuvent afficher un pourcentage de CPU supérieur à 100 % pour un processus multithread qui utilise plusieurs processeurs logiques.

Par conséquent :

- une valeur élevée n'est pas automatiquement anormale ;
- une valeur faible ne garantit pas qu'une application fonctionne correctement ;
- une mesure instantanée doit être comparée aux observations suivantes.

## 11.3. Afficher la charge système

```bash
uptime
```

La commande affiche notamment les moyennes de charge sur différentes périodes.

Exemple fictif :

```text
08:30:00 up 2 days, 3:10, 2 users, load average: 0.45, 0.62, 0.71
```

Ces valeurs représentent les moyennes de charge du système, et non directement des pourcentages d'utilisation du CPU.

La charge tient notamment compte des tâches exécutables et de certaines tâches en attente non interruptible.

Une charge de `2.0` n'a donc pas la même signification pratique sur une machine disposant d'un seul processeur logique et sur une machine qui en possède seize.

## 11.4. Le rôle de la mémoire

Chaque processus peut utiliser de la mémoire virtuelle.

Une partie de cette mémoire peut correspondre à de la mémoire physique résidente, à des pages partagées, à des pages mappées depuis des fichiers ou à d'autres types de mappages.

Il faut donc distinguer :

- la mémoire virtuelle ;
- la mémoire résidente ;
- les pages partagées ;
- la mémoire disponible pour le système ;
- le cache utilisé par le noyau.

La mémoire affichée comme utilisée n'est pas nécessairement perdue ou indisponible. Linux utilise aussi de la mémoire pour des caches qui peuvent être réutilisés selon les besoins.

## 11.5. Afficher la mémoire avec `free`

```bash
free -h
```

L'option `-h` demande une présentation lisible des quantités.

Exemple fictif :

```text
               total        used        free      shared  buff/cache   available
Mem:            7.6Gi       3.8Gi       1.1Gi       0.3Gi       2.7Gi       3.1Gi
Swap:           2.0Gi       0.0Gi       2.0Gi
```

La colonne `available` est particulièrement utile pour estimer la mémoire encore disponible pour de nouvelles applications sans provoquer immédiatement une pression importante sur la mémoire.

Ne confonds pas une valeur `free` faible avec une panne automatique de mémoire.

## 11.6. Examiner une forte utilisation CPU

Si `top` montre une utilisation CPU élevée, adopte cette méthode :

```text
CPU ÉLEVÉ
   |
   v
Identifier le PID concerné
   |
   v
Relever la commande et l'utilisateur
   |
   v
Examiner l'évolution sur plusieurs mesures
   |
   v
Comprendre le rôle du processus
   |
   v
Consulter les journaux si nécessaire
   |
   v
Choisir une action adaptée
```

Il est possible qu'un processus consomme beaucoup de CPU parce qu'il effectue un travail légitime : compression, compilation, calcul scientifique, indexation ou traitement de données.

L'administrateur doit déterminer si cette consommation est attendue avant d'arrêter le processus.

## 11.7. Examiner une forte utilisation mémoire

Pour afficher les processus les plus consommateurs de mémoire :

```bash
ps -eo pid,user,%mem,rss,comm --sort=-%mem | head -n 15
```

Une croissance persistante de la mémoire peut révéler :

- une charge de travail qui augmente ;
- des données mises en cache ;
- une allocation importante mais légitime ;
- une fuite mémoire ;
- une configuration inadaptée.

Une seule mesure ne suffit pas à conclure à une fuite mémoire. Il faut observer l'évolution et connaître le fonctionnement de l'application.


# 12. Arrêter ou contrôler un processus avec les signaux

## 12.1. Qu'est-ce qu'un signal ?

Un signal est un mécanisme utilisé par Linux pour notifier un processus d'un événement ou lui demander de réagir.

Un signal peut être envoyé par un utilisateur, un autre processus ou le système, sous réserve des règles de permission applicables.

Certains signaux entraînent une terminaison par défaut ; d'autres suspendent ou reprennent un processus.

La commande `kill` permet d'envoyer un signal. Malgré son nom, elle ne signifie donc pas systématiquement « supprimer immédiatement ».

## 12.2. Les signaux les plus courants

| Signal | Numéro courant sur Linux | Rôle général |
|---|---:|---|
| `SIGTERM` | 15 | Demande de terminaison |
| `SIGKILL` | 9 | Terminaison forcée, impossible à intercepter |
| `SIGINT` | 2 | Interruption, souvent associée à `Ctrl+C` |
| `SIGSTOP` | 19 sur les architectures Linux usuelles, mais le numéro dépend de l'architecture | Suspension forcée |
| `SIGCONT` | 18 sur les architectures Linux usuelles, mais le numéro dépend de l'architecture | Reprise d'un processus suspendu |
| `SIGHUP` | 1 | Signal historiquement associé à la fermeture d'un terminal et aussi utilisé par certaines applications pour recharger leur configuration |

Pour des commandes portables et lisibles, privilégie souvent les noms symboliques des signaux plutôt que leurs numéros.

Tu peux consulter les signaux disponibles sur le système :

```bash
kill -l
```

## 12.3. Envoyer `SIGTERM`

`SIGTERM` demande au processus de se terminer.

La commande de principe est :

```bash
kill -TERM PID
```

Remplace `PID` par l'identifiant réel du processus.

Exemple :

```bash
kill -TERM 1234
```

Cet exemple ne doit pas être exécuté avec un PID choisi au hasard : vérifie d'abord que le processus `1234` est bien celui que tu souhaites arrêter.

Le processus peut recevoir le signal et effectuer certaines opérations avant de quitter, par exemple fermer des fichiers ou terminer un travail en cours.

Il peut aussi intercepter le signal ou choisir un comportement particulier.

## 12.4. Pourquoi commencer par `SIGTERM` ?

Une terminaison propre donne à l'application l'occasion de réagir à la demande d'arrêt.

Cette approche est généralement préférable lorsque l'application prend en charge ce comportement.

Exemple de séquence :

```text
ADMINISTRATEUR
      |
      | kill -TERM PID
      v
PROCESSUS
      |
      | reçoit la demande
      v
FERMETURE DES RESSOURCES
      |
      v
TERMINAISON
      |
      v
DISPARITION DU PROCESSUS
```

Ce schéma représente un cas idéal. Le comportement dépend du logiciel et de son état.

## 12.5. Envoyer `SIGKILL`

`SIGKILL` force la terminaison d'un processus que le noyau peut terminer.

```bash
kill -KILL PID
```

Cette action empêche le processus de traiter lui-même ce signal et d'effectuer sa logique normale de fermeture.

Il faut donc éviter d'utiliser `SIGKILL` comme première solution.

Réserve-le aux situations dans lesquelles une terminaison forcée est justifiée et où les solutions moins brutales ont échoué.

Même `SIGKILL` ne garantit pas que toute anomalie apparente disparaîtra instantanément : un processus bloqué dans certaines attentes noyau peut ne quitter son état qu'une fois l'attente résolue.

## 12.6. Comparer `SIGTERM` et `SIGKILL`

```text
SIGTERM
   |
   +-- Demande de terminaison
   |
   +-- Peut être traité par le programme
   |
   +-- Permet une fermeture propre si l'application le prévoit


SIGKILL
   |
   +-- Terminaison forcée par le noyau
   |
   +-- Ne peut pas être intercepté ou ignoré
   |
   +-- Peut empêcher la fermeture propre des ressources
```

Retenir cette priorité :

1. Comprendre le processus.
2. Vérifier que son arrêt est nécessaire.
3. Envoyer `SIGTERM` si l'arrêt direct est adapté.
4. Vérifier le résultat.
5. En dernier recours, envisager `SIGKILL` si la situation le justifie.

## 12.7. Vérifier avant et après l'envoi d'un signal

Avant :

```bash
ps -p 1234 -o pid,ppid,user,stat,etime,cmd
```

Après :

```bash
ps -p 1234 -o pid,ppid,user,stat,etime,cmd
```

Utilise ici le véritable PID.

Si aucune ligne n'apparaît après l'action, le processus peut s'être terminé, mais vérifie aussi le contexte : un PID peut être réutilisé et le programme peut éventuellement être redémarré par un superviseur.

## 12.8. Tester l'existence et l'accessibilité avec `kill -0`

Le signal numéro zéro ne demande pas une terminaison.

```bash
kill -0 PID
```

Il permet notamment de vérifier si le processus existe et si l'appelant a les permissions nécessaires pour lui envoyer des signaux.

Il ne garantit pas que le processus fonctionne correctement, qu'il répond aux requêtes ou que son application est en bonne santé.

## 12.9. Éviter les arrêts par motif trop large

Des commandes comme `pkill` peuvent viser plusieurs processus.

Par exemple, une recherche basée sur un motif trop large risque de sélectionner des processus non désirés.

Il est préférable de :

1. rechercher les processus ;
2. examiner leur commande ;
3. contrôler leur propriétaire ;
4. vérifier les PID ;
5. choisir précisément la cible.

Sur un serveur partagé, l'arrêt d'un processus peut affecter une autre personne ou un service essentiel.


# 13. Comprendre le premier plan et l'arrière-plan

## 13.1. Le premier plan

Lorsqu'une commande est lancée normalement dans un terminal :

```bash
sleep 60
```

Le shell attend généralement sa fin avant de présenter une nouvelle invite de commande.

On dit que la commande occupe le premier plan du terminal.

Pendant ce temps, tu peux interrompre l'exécution avec :

```text
Ctrl+C
```

Dans un terminal interactif classique, cette combinaison demande généralement une interruption au groupe de processus au premier plan au moyen de `SIGINT`.

Il ne faut pas considérer `Ctrl+C` comme l'équivalent universel d'un arrêt brutal : le programme peut recevoir et traiter le signal selon son comportement.

## 13.2. Lancer une commande en arrière-plan

En ajoutant `&` à la fin de la commande :

```bash
sleep 60 &
```

Le shell lance la tâche en arrière-plan et rend normalement la main sans attendre que la commande se termine.

Tu verras éventuellement une sortie semblable à :

```text
[1] 4101
```

Cela signifie, dans l'exemple :

- `[1]` : numéro de tâche dans le shell ;
- `4101` : PID du processus associé à cette commande simple.

Les nombres réels seront différents.

Le numéro de tâche et le PID ne désignent pas la même chose.

```text
NUMÉRO DE TÂCHE SHELL     PID LINUX
        [1]                 4101
         |                    |
         v                    v
Repère dans le shell      Identifiant du processus
```

## 13.3. Afficher les tâches du shell

```bash
jobs
```

Pour afficher également les PID lorsque pris en charge :

```bash
jobs -l
```

Attention : `jobs` ne donne pas une liste générale de tous les processus Linux. Il affiche les tâches connues du shell courant.

Un processus lancé depuis un autre terminal ne sera généralement pas listé dans la table des tâches de ton shell.

## 13.4. Utiliser `$!`

Après avoir lancé une commande en arrière-plan, la variable spéciale `$!` contient le PID du dernier travail asynchrone lancé par le shell.

Exemple :

```bash
sleep 300 &
PID=$!

printf 'PID lancé : %s\n' "$PID"
```

Cette technique évite de devoir deviner le PID.

La variable doit être récupérée au bon moment, avant qu'un autre lancement en arrière-plan ne remplace sa valeur.

## 13.5. Suspendre une tâche avec `Ctrl+Z`

Lance :

```bash
sleep 300
```

Puis appuie sur :

```text
Ctrl+Z
```

Dans un terminal Bash interactif avec le contrôle des tâches activé, la tâche est normalement suspendue.

Tu peux consulter :

```bash
jobs -l
```

La suspension n'est pas une terminaison.

Le processus reste présent, mais il ne poursuit pas normalement son exécution tant qu'il est suspendu.

## 13.6. Reprendre une tâche avec `bg`

Pour reprendre en arrière-plan la tâche courante ou une tâche désignée :

```bash
bg
```

Ou :

```bash
bg %1
```

Le symbole `%1` désigne la tâche numéro 1 dans la table des tâches du shell courant.

La tâche doit être connue de ce shell. Remplace le numéro par celui réellement affiché.

## 13.7. Ramener une tâche au premier plan avec `fg`

```bash
fg
```

Ou pour une tâche spécifique :

```bash
fg %1
```

La commande fait revenir la tâche au premier plan du terminal.

Si elle était suspendue, `fg` la reprend normalement.

## 13.8. Arrêter une tâche en arrière-plan

Pour tester une méthode prudente :

```bash
sleep 300 &
PID=$!
printf 'PID : %s\n' "$PID"
```

Vérifie le processus :

```bash
ps -p "$PID" -o pid,ppid,user,stat,cmd
```

Envoie une demande de terminaison à ce PID précis :

```bash
kill -TERM "$PID"
```

Vérifie ensuite :

```bash
ps -p "$PID" -o pid,ppid,user,stat,cmd
```

La ligne peut avoir disparu si le processus est terminé.

## 13.9. La commande `wait`

La commande interne `wait` permet notamment d'attendre la fin d'un processus enfant connu du shell et de récupérer son statut de retour.

Exemple :

```bash
sleep 3 &
PID=$!

wait "$PID"
printf 'Code de retour : %s\n' "$?"
```

Le shell attend alors la fin du processus enfant concerné.

`wait` ne sert pas à attendre arbitrairement n'importe quel PID sur l'ensemble du système : son usage dépend des relations et des tâches connues de la session shell.


# 14. Modifier la priorité d'un processus

## 14.1. Pourquoi existe-t-il des priorités ?

Le processeur doit partager son temps entre les tâches qui peuvent s'exécuter.

L'ordonnanceur Linux utilise plusieurs informations pour déterminer quelle tâche exécuter et quand.

La notion de priorité influence ce partage, mais elle ne constitue pas une garantie de délai précis.

Pour les processus ordinaires, la valeur de `nice` est un moyen simple d'influencer la priorité relative d'ordonnancement.

## 14.2. Comprendre la valeur de nice

Pour les processus ordinaires, la plage courante de nice est :

```text
-20  ----------------  0  ----------------  +19
Priorité relative                 Valeur        Priorité relative
plus favorable                    standard      moins favorable
```

Dans ce cadre :

- une valeur négative correspond à une priorité relative plus favorable ;
- `0` est la valeur standard ;
- une valeur positive correspond à une priorité relative moins favorable.

Le terme « plus favorable » ne garantit pas qu'un processus obtienne immédiatement davantage de CPU : l'ordonnanceur tient compte du contexte global et d'autres mécanismes.

## 14.3. Lancer un programme avec `nice`

Exemple :

```bash
nice -n 10 sleep 60
```

Cette commande lance `sleep` avec une valeur de nice positive, ce qui réduit sa priorité relative par rapport à un processus comparable de nice `0`.

Pour observer ce type de processus, utilise un autre terminal :

```bash
ps -eo pid,ni,pri,stat,cmd | grep '[s]leep'
```

La valeur de nice est affichée dans la colonne `NI`.

## 14.4. Modifier la priorité avec `renice`

Supposons qu'un processus existe et que son PID soit `1234`.

```bash
renice 10 -p 1234
```

Cette commande demande de modifier sa valeur de nice.

Dans le cas courant, un utilisateur non privilégié peut généralement augmenter la valeur de nice de ses propres processus, mais ne peut pas nécessairement réduire cette valeur vers une priorité plus favorable.

Les modifications de priorité exigent des privilèges adaptés selon le système et l'action demandée.

## 14.5. Quand utiliser la priorité ?

Une priorité moins favorable peut être pertinente pour une tâche de fond peu urgente, par exemple un traitement de données non prioritaire.

Cependant, modifier la priorité ne résout pas automatiquement :

- une fuite mémoire ;
- une boucle infinie ;
- un problème de stockage ;
- une panne réseau ;
- une application mal configurée.

La priorité est un outil d'ajustement, pas un substitut au diagnostic.


# 15. Comprendre la différence entre processus et service

## 15.1. Un processus est une exécution ; un service est une fonction administrée

Les termes « processus » et « service » sont souvent utilisés comme s'ils étaient synonymes. Ils ne le sont pas.

Un processus correspond à une exécution gérée par le système.

Un service représente une fonction ou une application administrée par un mécanisme de gestion des services, par exemple `systemd`.

Un service peut :

- lancer un processus ;
- posséder plusieurs processus ;
- être redémarré automatiquement ;
- dépendre d'autres services ;
- être associé à des paramètres de démarrage ;
- produire des journaux ;
- être contrôlé par le gestionnaire de services.

## 15.2. Représentation

```text
GESTIONNAIRE DE SERVICES
          |
          v
      SERVICE WEB
          |
          +-- Processus principal
          |
          +-- Processus enfants éventuels
          |
          +-- Threads éventuels
          |
          +-- Fichiers et connexions ouverts
```

Cette organisation varie selon l'application.

Certains services possèdent un seul processus principal, tandis que d'autres utilisent de nombreux processus ou threads.

## 15.3. Afficher l'état d'un service

Sur un système utilisant `systemd`, tu peux consulter :

```bash
systemctl status ssh.service
```

Le nom du service dépend de la distribution et de l'installation.

Sur certaines distributions, le service SSH porte le nom `sshd.service` plutôt que `ssh.service`.

Si le service recherché n'existe pas sur la machine, la commande indiquera qu'il n'est pas connu.

## 15.4. Distinguer l'état du service et l'état d'un PID

`systemctl status` renseigne sur l'unité de service gérée par `systemd`.

`ps` renseigne sur les processus visibles.

Les deux informations peuvent être complémentaires :

```text
systemctl status nom.service
              |
              v
État et contexte du service
              |
              v
PID principal éventuellement indiqué
              |
              v
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,cmd
              |
              v
Détails du processus correspondant
```

Un service peut être actif tout en possédant plusieurs processus. À l'inverse, un processus peut exister sans être géré par une unité de service `systemd`.

## 15.5. Démarrer, arrêter et redémarrer un service

Avec `systemd`, les commandes générales sont :

```bash
systemctl start nom.service
```

Pour arrêter :

```bash
systemctl stop nom.service
```

Pour redémarrer :

```bash
systemctl restart nom.service
```

Ces opérations peuvent modifier l'état d'une application importante.

Ne les exécute pas sur un service de production sans avoir vérifié son rôle, les dépendances et les conséquences de l'opération.

Selon la configuration, certaines commandes exigent des droits administratifs, souvent par l'intermédiaire de `sudo`.

## 15.6. Pourquoi ne pas simplement tuer le PID du service ?

Si un processus appartient à un service administré, arrêter le service avec son gestionnaire est généralement plus adapté que d'envoyer directement un signal au PID principal.

Le gestionnaire connaît sa configuration et peut appliquer ses règles de supervision.

L'arrêt manuel d'un processus peut aussi provoquer son redémarrage automatique, laisser certains processus enfants actifs ou perturber l'état observé par le superviseur.

Pour administrer un service, commence par le gestionnaire correspondant, puis utilise les outils de processus pour le diagnostic.

## 15.7. Consulter les journaux d'un service

Avec `systemd`, tu peux examiner les journaux ainsi :

```bash
journalctl -u nom.service -n 50 --no-pager
```

Cette commande demande les dernières lignes disponibles pour l'unité indiquée.

Pour une analyse chronologique, les journaux peuvent révéler :

- une erreur de configuration ;
- un port déjà occupé ;
- un problème de permission ;
- une dépendance absente ;
- des redémarrages répétés ;
- une erreur au démarrage.

Le nom de l'unité doit être remplacé par celui du service concerné.


# 16. Diagnostiquer un processus problématique

## 16.1. La méthode générale

Lorsque tu soupçonnes un problème de processus, évite les réactions immédiates.

Utilise une démarche progressive :

```text
OBSERVATION
    |
    v
Identifier le symptôme
    |
    v
Repérer le PID et la commande
    |
    v
Vérifier l'utilisateur et le parent
    |
    v
Examiner état, CPU et mémoire
    |
    v
Rechercher des indices dans les journaux
    |
    v
Déterminer si le processus est légitime
    |
    v
Choisir une action proportionnée
    |
    v
Vérifier que le problème est résolu
```

Un bon diagnostic explique pourquoi une action est nécessaire.

## 16.2. Cas 1 : un processus consomme beaucoup de CPU

Commence par :

```bash
top
```

Repère le processus qui présente une consommation élevée.

Récupère son PID et son nom, puis examine :

```bash
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

Utilise le PID réel à la place de `PID`.

Pose-toi les questions suivantes :

- L'application est-elle censée effectuer un calcul ?
- La consommation est-elle continue ou temporaire ?
- Existe-t-il une erreur dans les journaux ?
- Est-ce un service essentiel ?
- Le problème a-t-il commencé après une modification ?

Ne tue pas automatiquement le processus le plus consommateur.

## 16.3. Cas 2 : le système semble manquer de mémoire

Observe :

```bash
free -h
```

Puis :

```bash
ps -eo pid,user,%mem,rss,comm --sort=-%mem | head -n 15
```

Ces informations aident à repérer les processus les plus consommateurs de mémoire.

Il faut ensuite déterminer si la consommation est normale, si la charge a augmenté ou si une application montre une croissance anormale.

## 16.4. Cas 3 : une application ne répond plus

La première question consiste à distinguer plusieurs situations :

- processus absent ;
- processus toujours présent, mais application indisponible ;
- processus en attente ;
- processus suspendu ;
- service arrêté ;
- processus bloqué dans une opération d'entrée-sortie.

Vérifie le processus avec `ps`, puis le service avec `systemctl status` si l'application est gérée par un service.

L'état d'un processus n'indique pas à lui seul si l'application répond correctement aux utilisateurs.

## 16.5. Cas 4 : un processus réapparaît après son arrêt

Plusieurs explications sont possibles :

- un service le relance ;
- un superviseur le redémarre ;
- un ordonnanceur exécute régulièrement une commande ;
- un autre processus le recrée ;
- un script est toujours actif.

Dans ce cas, ne multiplie pas les signaux d'arrêt sans comprendre l'origine du processus.

Examine :

```bash
ps -ef --forest
```

Si le processus appartient à un service, examine également :

```bash
systemctl status nom.service
```

Une réapparition peut être un comportement normal de supervision.

## 16.6. Cas 5 : un processus reste en état `D`

Commence par vérifier qu'il reste réellement dans cet état au cours du temps.

```bash
ps -p PID -o pid,ppid,user,stat,etime,cmd
```

Si le processus est bloqué durablement en `D`, l'examen peut nécessiter :

```bash
dmesg -T | tail -n 50
```

Sur certaines distributions, l'accès à `dmesg` peut être restreint. Le format `-T` donne une représentation horaire approximative à partir des horodatages du noyau, selon les versions.

Il faut alors rechercher des éléments concrets dans les messages système avant de conclure.

Le but n'est pas d'envoyer `SIGKILL` de façon répétée, mais de trouver la cause de l'attente.

## 16.7. Cas 6 : un processus appartient à un autre utilisateur

Examine d'abord :

```bash
ps -p PID -o pid,ppid,user,stat,cmd
```

Si le processus ne t'appartient pas, les permissions peuvent empêcher certaines actions.

Ne tente pas de contourner aveuglément ce comportement.

Il peut s'agir d'un service système ou d'une application importante pour un autre utilisateur.

L'emploi de privilèges administratifs doit être justifié par le rôle de l'administrateur et les besoins de l'intervention.


# 17. Bonnes pratiques de sécurité

## 17.1. Ne pas arrêter un processus simplement parce que son nom est inconnu

Linux exécute de nombreux processus dont le rôle n'est pas immédiatement évident.

Certains sont nécessaires à la session, à la journalisation, au réseau, au stockage, aux services de sécurité ou à l'administration de la machine.

Avant une intervention, vérifie au minimum :

```bash
ps -p PID -o pid,ppid,user,stat,etime,cmd
```

Si le processus est inconnu, cherche à comprendre son origine avant de l'arrêter.

## 17.2. Éviter `kill -9` comme réflexe

Une terminaison forcée peut interrompre le travail en cours sans laisser à l'application la possibilité d'effectuer ses opérations de fermeture.

Privilégie une demande de terminaison normale quand elle est adaptée.

Un arrêt forcé doit être motivé par la situation et suivi d'une vérification.

## 17.3. Être prudent avec `sudo`

Les privilèges administratifs permettent d'agir sur davantage de processus.

Cette capacité implique une responsabilité supplémentaire.

Avant d'exécuter une commande avec `sudo`, vérifie :

- le PID concerné ;
- le rôle de l'application ;
- les conséquences d'un arrêt ;
- la nécessité réelle des privilèges administratifs.

## 17.4. Ne pas confondre un processus inactif avec un processus inutile

Un service Web qui attend les requêtes est généralement peu actif entre deux requêtes.

Un processus en état `S` peut parfaitement fonctionner normalement.

De même, un processus dont le CPU est à zéro peut être indispensable au système.

## 17.5. Toujours vérifier l'effet d'une action

Après un arrêt ou une modification, contrôle le résultat.

Exemples :

```bash
ps -p PID -o pid,ppid,user,stat,cmd
```

Pour un service :

```bash
systemctl status nom.service
```

Pour les ressources :

```bash
free -h
```

```bash
uptime
```

Le diagnostic n'est pas terminé simplement parce qu'une commande a été exécutée sans afficher d'erreur.


# 18. Travaux pratiques guidés

Les travaux pratiques suivants utilisent volontairement des commandes simples et des processus de test. Ils doivent être exécutés sur une machine de laboratoire ou une session utilisateur où tu peux observer les processus sans risquer d'interrompre une application importante.

## TP 1 — Découvrir les processus de la machine

### Objectif

Afficher les processus, distinguer PID et PPID et examiner les processus de l'utilisateur courant.

### Étape 1 : afficher les processus

Exécute :

```bash
ps -ef
```

Observe les colonnes `UID`, `PID`, `PPID`, `TTY` et `CMD`.

### Étape 2 : afficher les processus de ton utilisateur

```bash
ps -u "$USER" -f
```

Compare les résultats.

### Étape 3 : afficher l'arbre

```bash
ps -ef --forest
```

Observe les relations parent-enfant lorsqu'elles sont visibles.

### Étape 4 : identifier une commande simple

Exécute :

```bash
sleep 120 &
PID=$!
printf 'PID du test : %s\n' "$PID"
```

Affiche ensuite :

```bash
ps -p "$PID" -o pid,ppid,user,stat,etime,cmd
```

### Étape 5 : terminer le test

```bash
kill -TERM "$PID"
```

Vérifie :

```bash
ps -p "$PID" -o pid,ppid,user,stat,cmd
```

### Résultat attendu

Tu dois avoir identifié un PID réel, examiné son PPID, observé sa commande et vérifié ce qu'il est devenu après l'envoi de `SIGTERM`.


## TP 2 — Comprendre les tâches au premier plan et en arrière-plan

### Objectif

Lancer une tâche, la suspendre, la reprendre puis la terminer.

### Étape 1 : lancer une tâche au premier plan

Exécute :

```bash
sleep 300
```

Le terminal attend normalement la fin de la commande.

### Étape 2 : suspendre la tâche

Appuie sur `Ctrl+Z`.

### Étape 3 : consulter les tâches

```bash
jobs -l
```

Identifie le numéro de tâche et le PID affichés.

### Étape 4 : reprendre en arrière-plan

```bash
bg
```

Puis :

```bash
jobs -l
```

### Étape 5 : revenir au premier plan

```bash
fg
```

### Étape 6 : terminer la tâche de test

Appuie sur `Ctrl+C`.

La tâche doit se terminer dans le cas normal de cet exercice.

### Étape 7 : vérifier

```bash
jobs -l
```

Le travail peut ne plus apparaître dans la table du shell si la tâche s'est terminée.

### Résultat attendu

Tu dois pouvoir expliquer la différence entre :

- une commande exécutée au premier plan ;
- une tâche suspendue ;
- une tâche exécutée en arrière-plan ;
- une tâche terminée.


## TP 3 — Observer les ressources

### Objectif

Comparer les informations de `top`, `ps`, `free` et `uptime`.

### Étape 1 : observer les processus

```bash
top
```

Repère les colonnes CPU, mémoire, état et commande.

Quitte avec `q`.

### Étape 2 : afficher les processus les plus consommateurs de CPU

```bash
ps -eo pid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15
```

### Étape 3 : afficher les informations mémoire

```bash
free -h
```

### Étape 4 : afficher la charge

```bash
uptime
```

### Étape 5 : comparer

Relève les différences entre :

- une utilisation CPU par processus ;
- une utilisation de mémoire par processus ;
- les statistiques générales du système ;
- la moyenne de charge.

### Résultat attendu

Tu dois comprendre pourquoi les colonnes affichées par les outils ne mesurent pas toutes le même phénomène.


## TP 4 — Étudier les informations d'un processus avec `/proc`

### Objectif

Observer les informations structurées exposées par Linux.

### Étape 1 : lancer une tâche

```bash
sleep 300 &
PID=$!
```

### Étape 2 : afficher ses informations

```bash
cat "/proc/$PID/status"
```

### Étape 3 : afficher la commande et le temps écoulé

```bash
ps -p "$PID" -o pid,ppid,user,stat,etime,cmd
```

### Étape 4 : examiner les champs disponibles

Observe le nom, le PID, le PPID et l'état présentés par `/proc/$PID/status`.

### Étape 5 : terminer le test

```bash
kill -TERM "$PID"
```

### Étape 6 : vérifier le répertoire

```bash
ls "/proc/$PID"
```

Si le processus a terminé et que le PID n'a pas été réutilisé, son répertoire ne sera plus présent.

Le résultat peut être différent si le processus reste présent ou si le PID est réutilisé entre les commandes.

### Résultat attendu

Tu dois comprendre que `/proc` expose des informations dynamiques, liées à l'état du système, et qu'un répertoire de PID peut disparaître lorsque le processus est terminé.


## TP 5 — Simuler une terminaison propre

### Objectif

Envoyer une demande d'arrêt à un processus contrôlé et vérifier le résultat.

### Étape 1 : démarrer le processus

```bash
sleep 300 &
PID=$!
```

### Étape 2 : vérifier son identité

```bash
ps -p "$PID" -o pid,ppid,user,stat,cmd
```

### Étape 3 : envoyer `SIGTERM`

```bash
kill -TERM "$PID"
```

### Étape 4 : examiner le résultat

```bash
ps -p "$PID" -o pid,ppid,user,stat,cmd
```

### Étape 5 : interpréter

La commande `sleep` de cet exercice n'a pas de travail complexe à finaliser. Elle doit normalement terminer après la réception du signal.

Dans une application réelle, le résultat dépend du traitement du signal par le programme.

### Résultat attendu

Tu dois savoir expliquer que `kill -TERM` demande une terminaison plutôt que d'imposer systématiquement une destruction immédiate.


# 19. Exercices d'application

Réponds aux questions sans consulter immédiatement la correction.

## Exercice 1 — Programme et processus

Explique la différence entre un programme et un processus.

Une même application peut-elle avoir deux processus différents ?

## Exercice 2 — PID et PPID

Tu observes :

```text
UID       PID   PPID  CMD
alice    4101   4012  sleep 120
```

Quel est le PID du processus ?

Quel est son PPID ?

Que représente le PPID ?

## Exercice 3 — Affichage des processus

Quelle commande permet de présenter l'ensemble des processus sous une forme détaillée courante ?

Propose également une commande pour afficher les processus de l'utilisateur courant.

## Exercice 4 — Recherche par nom

Quelle commande permet de rechercher les PID correspondant au nom `sleep` ?

Quelle commande permet d'afficher les PID ainsi que les lignes de commande correspondantes ?

## Exercice 5 — États

Associe chaque état à son interprétation :

- `R`
- `S`
- `D`
- `T`
- `Z`

## Exercice 6 — Signaux

Tu dois demander à un processus de se terminer proprement.

Quel signal privilégier dans le cas général ?

Quel signal force la terminaison sans permettre au programme de l'intercepter ?

## Exercice 7 — Arrière-plan

Que fait cette commande ?

```bash
sleep 300 &
```

Quelle variable spéciale peut récupérer le PID du dernier travail asynchrone lancé ?

## Exercice 8 — Tâches du shell

Quelle commande affiche les tâches connues du shell courant ?

Quelle commande permet de reprendre une tâche suspendue en arrière-plan ?

Quelle commande la ramène au premier plan ?

## Exercice 9 — Ressources

Quelle commande permet une surveillance interactive des processus ?

Quelle commande affiche des informations générales sur la mémoire ?

Pourquoi la charge moyenne ne doit-elle pas être interprétée directement comme un pourcentage de CPU ?

## Exercice 10 — Processus et service

Explique pourquoi arrêter directement un PID n'est pas toujours la meilleure manière d'arrêter une application gérée par `systemd`.

## Exercice 11 — Diagnostic

Un processus consomme beaucoup de CPU.

Cite au moins quatre vérifications à effectuer avant de décider de l'arrêter.

## Exercice 12 — Processus zombie

Pourquoi un signal `SIGKILL` adressé au PID d'un zombie ne constitue-t-il généralement pas la solution au problème ?


# 20. Corrections des exercices

## Correction 1 — Programme et processus

Un programme est un ensemble d'instructions représenté notamment par un fichier exécutable ou interprété.

Un processus est une instance de ce programme en cours d'exécution.

Oui, une même application peut avoir plusieurs processus distincts, chacun possédant son propre PID.

## Correction 2 — PID et PPID

Le PID vaut `4101`.

Le PPID vaut `4012`.

Le PPID est l'identifiant du processus parent.

Les nombres de l'exemple sont fictifs.

## Correction 3 — Affichage des processus

Une commande détaillée courante est :

```bash
ps -ef
```

Pour afficher les processus de l'utilisateur courant :

```bash
ps -u "$USER" -f
```

## Correction 4 — Recherche par nom

Pour rechercher les PID :

```bash
pgrep sleep
```

Pour afficher aussi les lignes de commande :

```bash
pgrep -a sleep
```

Les résultats dépendent des processus présents et des règles de correspondance de l'outil.

## Correction 5 — États

- `R` : processus en exécution ou prêt ;
- `S` : attente interruptible ;
- `D` : attente non interruptible ;
- `T` : processus suspendu ou arrêté ;
- `Z` : processus terminé dont le statut n'a pas encore été récupéré par son parent.

Un état isolé ne suffit pas à diagnostiquer une panne.

## Correction 6 — Signaux

Dans le cas général d'une demande normale de terminaison, on privilégie `SIGTERM`.

`SIGKILL` impose la terminaison par le noyau sans laisser au programme la possibilité de traiter ce signal.

## Correction 7 — Arrière-plan

La commande :

```bash
sleep 300 &
```

lance le programme en arrière-plan et rend normalement la main au shell.

La variable spéciale est :

```bash
$!
```

Exemple :

```bash
sleep 300 &
PID=$!
```

## Correction 8 — Tâches du shell

Pour afficher les tâches :

```bash
jobs -l
```

Pour reprendre une tâche en arrière-plan :

```bash
bg %1
```

Pour la ramener au premier plan :

```bash
fg %1
```

Le numéro `%1` doit correspondre à une tâche existante du shell courant.

## Correction 9 — Ressources

Surveillance interactive :

```bash
top
```

Informations générales sur la mémoire :

```bash
free -h
```

La charge moyenne représente une mesure de la charge de travail du système, et pas un simple pourcentage de temps CPU. Son interprétation dépend notamment du nombre de processeurs logiques et du type de tâches présentes.

## Correction 10 — Processus et service

Un gestionnaire de services peut surveiller le processus, le relancer automatiquement, gérer ses dépendances et organiser son arrêt.

Il est donc généralement préférable de passer par le gestionnaire du service pour arrêter une application gérée par `systemd`.

## Correction 11 — Diagnostic

Une réponse correcte peut inclure :

1. identifier le PID et la commande ;
2. vérifier l'utilisateur propriétaire ;
3. examiner le PPID ;
4. observer si la consommation est persistante ;
5. vérifier l'état du processus ;
6. connaître le rôle de l'application ;
7. consulter les journaux si nécessaire ;
8. vérifier si le processus appartient à un service essentiel.

## Correction 12 — Processus zombie

Le processus a déjà terminé son exécution. Le problème consiste généralement à comprendre pourquoi son parent n'a pas récupéré son statut.

Envoyer `SIGKILL` au zombie n'effectue pas cette récupération. Il faut examiner le parent et le fonctionnement de l'application concernée.


# 21. Défi final : diagnostic d'un serveur Linux

## 21.1. Contexte

Tu administres une machine Linux de laboratoire.

Un collègue signale que la machine semble ralentir et te transmet les informations suivantes :

```text
Symptôme A :
Un processus utilise beaucoup de CPU dans top.

Symptôme B :
Un processus inconnu apparaît plusieurs fois dans la liste de processus.

Symptôme C :
Une application gérée par systemd semble indisponible.

Symptôme D :
Tu dois vérifier si un processus de test peut être arrêté
sans toucher aux autres processus.
```

Les observations ne contiennent pas de PID réel, de nom de service précis ou de journaux. Tu dois donc commencer par une procédure de collecte, plutôt que d'inventer la cause du problème.

## 21.2. Mission

Produis un diagnostic qui répond aux questions suivantes :

1. Comment identifier le processus qui consomme le plus de CPU ?
2. Comment examiner son propriétaire, son PPID et sa commande ?
3. Comment rechercher plusieurs processus portant un même nom ?
4. Comment différencier une application et le service qui la gère ?
5. Quelles commandes permettent d'observer les journaux d'un service ?
6. Comment arrêter un processus de test en toute prudence ?
7. Comment vérifier le résultat de l'intervention ?
8. Quelles informations doivent être collectées avant de proposer une correction définitive ?

## 21.3. Contraintes

- Ne tue pas un processus uniquement parce qu'il consomme beaucoup de ressources.
- N'envoie pas de `SIGKILL` comme première action.
- Ne suppose pas qu'un service particulier est installé.
- Ne confonds pas une commande affichant des PID avec une commande affichant les tâches du shell courant.
- Pour le processus de test, utilise uniquement une commande contrôlée telle que `sleep`.
- Vérifie le résultat de chaque action.


# 22. Correction détaillée du défi final

## 22.1. Étape 1 : identifier le processus le plus consommateur de CPU

Lancer :

```bash
top
```

Repérer les lignes présentant une utilisation CPU élevée.

Quitter avec `q`.

Pour obtenir ensuite un relevé texte classé par CPU :

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15
```

Cette seconde commande aide à examiner le classement des processus à un instant donné.

## 22.2. Étape 2 : examiner un processus précis

Une fois le PID réel identifié, exécuter :

```bash
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

Remplacer `PID` par le numéro de processus observé.

Cette étape permet de réunir l'identité, le propriétaire, l'état et la commande dans un même affichage.

L'examen du PPID permet ensuite de rechercher l'origine du processus :

```bash
ps -p PID -o pid,ppid,cmd
```

On peut consulter l'arbre complet si la relation parent-enfant reste difficile à comprendre :

```bash
ps -ef --forest
```

## 22.3. Étape 3 : rechercher les processus portant le même nom

Supposons que le nom recherché soit `sleep` :

```bash
pgrep -a sleep
```

Pour examiner le propriétaire et l'état des PID trouvés, utiliser `ps` avec les identifiants réels.

Par exemple, si les PID observés sont `4101` et `4102` :

```bash
ps -p 4101,4102 -o pid,ppid,user,stat,etime,cmd
```

Ne copie pas ces PID fictifs sur ton système : utilise les valeurs réellement retournées par ta machine.

## 22.4. Étape 4 : examiner le service

Si l'application est gérée par `systemd`, identifier d'abord le nom de l'unité.

Puis consulter :

```bash
systemctl status nom.service
```

Cette commande indique notamment si le service est actif, arrêté ou en échec, ainsi que des informations utiles sur son état.

Le nom de l'unité doit correspondre à un service réellement installé.

## 22.5. Étape 5 : consulter les journaux

```bash
journalctl -u nom.service -n 50 --no-pager
```

Examiner les messages récents pour rechercher des erreurs concrètes.

Les hypothèses peuvent comprendre :

- une erreur de configuration ;
- un problème de permission ;
- un conflit de port ;
- un fichier absent ;
- un problème de dépendance ;
- une erreur d'entrée-sortie.

Il faut rechercher les éléments qui confirment une hypothèse plutôt que retenir arbitrairement la première explication possible.

## 22.6. Étape 6 : créer un processus contrôlé

Pour démontrer un arrêt de processus sans viser une application inconnue :

```bash
sleep 300 &
PID=$!

printf 'PID du processus de test : %s\n' "$PID"
```

Examiner le processus :

```bash
ps -p "$PID" -o pid,ppid,user,stat,etime,cmd
```

Envoyer une demande de terminaison :

```bash
kill -TERM "$PID"
```

Vérifier :

```bash
ps -p "$PID" -o pid,ppid,user,stat,cmd
```

Si le PID ne correspond plus à un processus présent, la ligne de processus doit normalement disparaître. Dans un environnement partagé ou très actif, il faut toujours tenir compte de la possibilité de réutilisation du PID et examiner le contexte du résultat.

## 22.7. Étape 7 : rédiger un compte rendu

Un compte rendu de diagnostic doit permettre à un autre administrateur de comprendre ce qui a été observé.

Exemple de structure :

```text
DIAGNOSTIC DES PROCESSUS LINUX

1. Symptôme observé
   Description précise du ralentissement ou de l'indisponibilité.

2. Processus concerné
   PID :
   PPID :
   Utilisateur :
   Commande :
   État :
   CPU :
   Mémoire :

3. Vérifications réalisées
   Commandes utilisées :
   Résultats significatifs :

4. Service concerné, si applicable
   Nom de l'unité :
   État :
   Messages du journal :

5. Hypothèses confirmées
   Informations qui appuient chaque hypothèse.

6. Action effectuée
   Action :
   Motif :
   Cible vérifiée :

7. Contrôle après intervention
   Résultat :
   État actuel :
   Symptôme résolu ou toujours présent :

8. Actions complémentaires
   Investigation nécessaire :
   Informations manquantes :
```

Cette structure évite les décisions basées uniquement sur des suppositions.


# 23. Checklist de compétences

Avant de passer au niveau intermédiaire, vérifie que tu peux réaliser les tâches suivantes sans suivre mécaniquement une procédure.

## Compréhension

- [ ] Je peux expliquer la différence entre un programme et un processus.
- [ ] Je comprends le rôle d'un thread.
- [ ] Je sais expliquer la relation entre PID et PPID.
- [ ] Je comprends les relations parent-enfant.
- [ ] Je distingue le processus, l'application et le service.
- [ ] Je peux expliquer pourquoi un processus en attente peut être parfaitement normal.

## Observation

- [ ] Je sais utiliser `ps -ef`.
- [ ] Je sais utiliser `ps aux`.
- [ ] Je sais afficher un PID précis.
- [ ] Je sais rechercher un processus avec `pgrep`.
- [ ] Je sais suivre l'activité avec `top`.
- [ ] Je sais examiner `/proc/PID/status`.
- [ ] Je comprends la différence entre `%CPU`, `%MEM`, mémoire résidente et charge moyenne.

## Contrôle

- [ ] Je sais envoyer `SIGTERM` à un processus de test identifié.
- [ ] Je comprends le rôle de `SIGKILL`.
- [ ] Je sais lancer une commande avec `&`.
- [ ] Je sais utiliser `$!`.
- [ ] Je sais afficher les tâches du shell avec `jobs`.
- [ ] Je sais suspendre et reprendre une tâche avec `Ctrl+Z`, `bg` et `fg`.
- [ ] Je sais utiliser `wait` pour attendre un processus enfant de ma session.

## Administration

- [ ] Je sais vérifier l'état d'un service avec `systemctl status`.
- [ ] Je sais consulter les journaux d'un service avec `journalctl`.
- [ ] Je sais pourquoi un processus peut être redémarré par un superviseur.
- [ ] Je sais vérifier une intervention au lieu de supposer qu'elle a réussi.

## Sécurité

- [ ] Je vérifie l'identité d'un processus avant de l'arrêter.
- [ ] Je n'utilise pas `kill -9` comme premier réflexe.
- [ ] Je comprends le risque des recherches par motif trop large.
- [ ] Je sais qu'un processus en état `D` peut ne pas disparaître immédiatement.
- [ ] Je sais qu'un zombie doit être diagnostiqué à travers son parent.


# 24. Fiche de révision

## 24.1. Affichage et recherche

Afficher les processus :

```bash
ps -ef
```

Autre format courant :

```bash
ps aux
```

Afficher l'arbre :

```bash
ps -ef --forest
```

Afficher les processus de l'utilisateur courant :

```bash
ps -u "$USER" -f
```

Afficher un processus précis :

```bash
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

Rechercher un nom :

```bash
pgrep nom
```

Rechercher un nom et afficher la commande :

```bash
pgrep -a nom
```

## 24.2. Surveillance des ressources

Surveillance interactive :

```bash
top
```

Mémoire générale :

```bash
free -h
```

Temps de fonctionnement et charge :

```bash
uptime
```

Processus classés par CPU :

```bash
ps -eo pid,user,stat,%cpu,%mem,cmd --sort=-%cpu | head -n 15
```

Processus classés par mémoire :

```bash
ps -eo pid,user,%mem,rss,cmd --sort=-%mem | head -n 15
```

## 24.3. Signaux et arrêt

Demander une terminaison :

```bash
kill -TERM PID
```

Forcer une terminaison lorsque cela est justifié :

```bash
kill -KILL PID
```

Vérifier l'existence ou les permissions pour envoyer un signal :

```bash
kill -0 PID
```

Lister les signaux disponibles :

```bash
kill -l
```

## 24.4. Tâches du shell

Lancer en arrière-plan :

```bash
sleep 300 &
```

Récupérer le PID :

```bash
PID=$!
```

Lister les tâches :

```bash
jobs -l
```

Reprendre en arrière-plan :

```bash
bg
```

Ramener au premier plan :

```bash
fg
```

Attendre la fin d'un enfant connu du shell :

```bash
wait "$PID"
```

## 24.5. Priorité

Lancer avec une priorité relative moins favorable :

```bash
nice -n 10 sleep 60
```

Modifier la valeur de nice d'un PID :

```bash
renice 10 -p PID
```

## 24.6. Services

Afficher l'état :

```bash
systemctl status nom.service
```

Arrêter un service géré par `systemd` :

```bash
systemctl stop nom.service
```

Consulter les journaux :

```bash
journalctl -u nom.service -n 50 --no-pager
```

## 24.7. Informations `/proc`

Afficher les informations structurées d'un processus :

```bash
cat /proc/PID/status
```

Afficher des informations générales sur le processeur :

```bash
cat /proc/cpuinfo
```

Afficher des informations générales sur la mémoire :

```bash
cat /proc/meminfo
```


# 25. Glossaire

**Application :** logiciel qui réalise une fonction pour l'utilisateur ou pour le système.

**Arbre des processus :** représentation des relations parent-enfant entre processus.

**CPU :** unité qui exécute les instructions des processus et des threads.

**Code de retour :** valeur communiquée à l'issue d'une commande ou d'un processus afin de signaler un résultat.

**Commande :** instruction saisie ou exécutée par un interpréteur de commandes, susceptible de lancer un programme.

**Daemon :** processus de service qui fonctionne généralement sans interaction directe avec un terminal utilisateur. Le terme est souvent employé dans les systèmes Unix et Linux.

**Gestionnaire de services :** composant chargé de gérer le cycle de vie des services ; `systemd` est un exemple courant.

**Job :** tâche suivie par le shell dans le cadre du contrôle des tâches.

**Load average :** moyenne de charge du système calculée sur différentes périodes. Elle ne correspond pas directement à un pourcentage d'utilisation CPU.

**Mémoire résidente :** partie de l'espace mémoire d'un processus actuellement présente en mémoire physique, selon les mesures et conventions de l'outil.

**Nice :** valeur influençant la priorité relative des processus ordinaires au sein de l'ordonnancement.

**PID :** identifiant attribué à un processus.

**PPID :** identifiant du parent d'un processus.

**Processus :** instance d'un programme en cours d'exécution.

**Processus enfant :** processus créé par un autre processus.

**Processus parent :** processus associé à la création d'un processus enfant.

**Processus zombie :** processus terminé dont le statut de fin n'a pas encore été récupéré par son parent.

**`/proc` :** système de fichiers virtuel exposant des informations sur le noyau et les processus Linux.

**Signal :** mécanisme de notification et de contrôle pouvant être envoyé à un processus.

**`SIGKILL` :** signal de terminaison forcée qui ne peut pas être intercepté ou ignoré par le programme.

**`SIGTERM` :** signal de demande de terminaison.

**Service :** fonction ou application dont le cycle de vie est administré par un mécanisme de gestion ou de supervision.

**Thread :** fil d'exécution au sein d'un processus.

**`top` :** outil permettant d'observer de façon interactive l'activité des processus et les ressources du système.

**`ps` :** outil qui présente un instantané des processus sélectionnés.

**`pgrep` :** outil de recherche de processus à partir d'un nom ou d'un motif.


# 26. Documentation officielle

Pour approfondir les notions abordées dans ce cours, consulte les références suivantes :

1. **Manuel GNU Bash — contrôle des tâches**  
   https://www.gnu.org/software/bash/manual/html_node/Job-Control.html

2. **Manuel GNU Bash — commandes `bg`, `fg` et `jobs`**  
   https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html

3. **Pages de manuel Linux — `ps`**  
   https://man7.org/linux/man-pages/man1/ps.1.html

4. **Pages de manuel Linux — `top`**  
   https://man7.org/linux/man-pages/man1/top.1.html

5. **Pages de manuel Linux — `kill`**  
   https://man7.org/linux/man-pages/man1/kill.1.html

6. **Pages de manuel Linux — `signal(7)`**  
   https://man7.org/linux/man-pages/man7/signal.7.html

7. **Documentation du noyau Linux — système de fichiers `/proc`**  
   https://docs.kernel.org/filesystems/proc.html

8. **Documentation officielle systemd — `systemctl`**  
   https://www.freedesktop.org/software/systemd/man/latest/systemctl.html

9. **Pages de manuel Linux — `nice`**  
   https://man7.org/linux/man-pages/man1/nice.1.html

10. **Pages de manuel Linux — `renice`**  
    https://man7.org/linux/man-pages/man1/renice.1.html

Les commandes et les possibilités présentées peuvent varier selon la distribution, la version des outils, les permissions et le système d'initialisation utilisé. En cas de différence, consulte le manuel local avec `man nom_commande`, par exemple `man ps`, `man kill` ou `man systemctl`.


# Conclusion

La gestion des processus est une compétence fondamentale de l'administration Linux.

Avant ce cours, une commande lancée dans le terminal pouvait sembler n'être qu'une action ponctuelle. Tu sais maintenant qu'elle peut créer un processus doté d'un identifiant, d'un propriétaire, d'un état, de ressources, d'une relation avec un parent et d'un cycle de vie.

Tu as également appris à consulter les processus, rechercher un PID, interpréter les états les plus fréquents, surveiller le CPU et la mémoire, envoyer des signaux, contrôler les tâches du shell et distinguer un processus d'un service administré.

La progression à conserver est la suivante :

```text
COMPRENDRE
    |
    v
IDENTIFIER
    |
    v
OBSERVER
    |
    v
DIAGNOSTIQUER
    |
    v
AGIR PRUDEMMENT
    |
    v
VÉRIFIER
```

**Principe à retenir :** un administrateur Linux compétent ne se contente pas d'arrêter un processus qui semble problématique. Il cherche à comprendre son rôle, sa consommation de ressources et son origine, puis choisit l'intervention la moins risquée qui permet de résoudre le problème.