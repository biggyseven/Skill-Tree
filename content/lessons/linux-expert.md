# Linux Expert — Performance et Kernel
## Cours complet d'administration avancée et d'analyse des performances

> **Fichier :** `linux-expert.md`
>
> **Parcours :** Administration systèmes, réseaux et infrastructure
>
> **Niveau :** Expert
>
> **Prérequis :** Maîtrise des commandes Linux, des permissions, de systemd, des processus, du stockage, du réseau et des scripts Bash.
>
> **Environnement conseillé :** Machine virtuelle Linux dédiée, avec un accès administrateur contrôlé.
>
> **Thèmes centraux :** Noyau Linux, ordonnancement, CPU, mémoire, stockage, réseau, cgroups, observabilité et profilage.
>
> **Objectif général :** Savoir expliquer les mécanismes internes qui influencent les performances, mesurer un problème, identifier son origine et justifier une correction par des résultats vérifiables.


# Sommaire

1. Objectifs du niveau expert et méthode d'analyse
2. Architecture interne du noyau Linux
3. Les appels système et le chemin d'exécution
4. Ordonnancement CPU et concurrence
5. Mesure approfondie des performances CPU
6. Profilage avec `perf`
7. Mémoire virtuelle et gestion physique de la mémoire
8. Pression mémoire, swap et OOM
9. NUMA, caches et Huge Pages
10. Stockage, systèmes de fichiers et latence des entrées-sorties
11. Diagnostic avancé du réseau Linux
12. Pressure Stall Information — PSI
13. cgroups v2 et isolation des ressources
14. Namespaces, conteneurs et frontières de ressources
15. Tracing du noyau avec ftrace et tracepoints
16. Introduction au traçage eBPF
17. Modules, paramètres et démarrage du noyau
18. Synchronisation, verrous et problèmes de concurrence
19. Optimisation raisonnée des performances
20. Méthodologie professionnelle de benchmark
21. Playbooks de diagnostic d'incidents
22. Travaux pratiques guidés
23. Exercices d'évaluation corrigés
24. Référence des commandes expertes
25. Challenge final : diagnostiquer et optimiser un serveur Linux
26. Correction détaillée du challenge
27. Checklist finale des compétences
28. Références techniques officielles


# 1. Objectifs du niveau expert et méthode d'analyse

L'administration experte de Linux exige une approche différente de celle utilisée pour les tâches quotidiennes.

Un administrateur débutant sait exécuter une commande. Un administrateur intermédiaire sait gérer un service et rechercher des erreurs. Un expert doit comprendre les mécanismes qui produisent les résultats observés et déterminer si les ressources disponibles répondent réellement à la charge de travail.

Lorsqu'une application ralentit, plusieurs couches peuvent être responsables :

- Le code applicatif effectue trop de calculs.
- L'ordonnanceur ne fournit pas le temps CPU attendu.
- Le système attend des opérations de stockage.
- Les accès mémoire provoquent trop de défauts de page.
- Le réseau introduit des pertes, des retransmissions ou de la latence.
- Un groupe de contrôle limite les ressources du processus.
- Le noyau passe beaucoup de temps à gérer des interruptions ou des opérations d'entrée-sortie.
- Un verrou empêche plusieurs threads d'avancer en parallèle.

L'objectif de ce cours est d'apprendre à distinguer ces situations au lieu de modifier des paramètres système au hasard.

## 1.1 Compétences à acquérir

À la fin du parcours, vous devrez être capable de :

- Expliquer les principales responsabilités du noyau Linux.
- Décrire le passage entre l'espace utilisateur et l'espace noyau.
- Interpréter le fonctionnement général de l'ordonnanceur.
- Distinguer utilisation CPU, attente CPU et temps passé hors CPU.
- Lire les métriques de processus et les statistiques système.
- Utiliser `perf stat`, `perf record` et `perf report` pour une analyse adaptée.
- Comprendre les notions d'instructions, cycles CPU, IPC et défauts de cache.
- Analyser les mécanismes de mémoire virtuelle, de cache de pages et de récupération mémoire.
- Identifier des signes de pression mémoire et de thrashing.
- Comprendre NUMA, les Huge Pages et leurs compromis.
- Diagnostiquer les latences du stockage sans confondre débit et temps de réponse.
- Examiner les files réseau, les retransmissions et le traitement des paquets.
- Interpréter les métriques PSI.
- Comprendre comment les cgroups limitent CPU, mémoire et entrées-sorties.
- Différencier cgroups, namespaces et machines virtuelles.
- Explorer le comportement du noyau avec les tracepoints, ftrace et eBPF.
- Examiner les modules et les paramètres du noyau sans provoquer de modification non maîtrisée.
- Concevoir des benchmarks reproductibles.
- Produire un rapport de diagnostic fondé sur des preuves.

## 1.2 Le modèle de raisonnement expert

Une analyse de performances doit commencer par une question précise.

Mauvaise question :

> Pourquoi mon serveur est-il lent ?

Meilleures questions :

> Pourquoi le temps de réponse p99 de cette API est-il passé de 80 ms à 450 ms alors que le débit est resté stable ?

> Pourquoi ce processus consomme-t-il 100 % d'un cœur CPU alors que les autres cœurs sont peu utilisés ?

> Pourquoi le stockage affiche-t-il une latence élevée alors que le débit est faible ?

> Pourquoi le conteneur manque-t-il de mémoire alors que l'hôte possède encore de la RAM disponible ?

Ces questions peuvent être reliées à des indicateurs mesurables.

### Schéma de la méthode d'investigation

```text
+--------------------------------------------------+
| PROBLEME OBSERVE                                 |
| Exemple : hausse du temps de reponse             |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| DEFINIR LE SYMPTOME                              |
| Mesure, periode, charge, perimetre               |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| ETABLIR UNE REFERENCE                            |
| CPU, memoire, stockage, reseau                   |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| FORMULER UNE HYPOTHESE                           |
| Saturation CPU ? Pression memoire ? I/O ?        |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| CHOISIR UN OUTIL ADAPTE                          |
| ps, pidstat, vmstat, iostat, perf, PSI, tracing  |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| MESURER LE MECANISME                             |
| Pas uniquement le symptome                       |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| TESTER UNE CORRECTION CONTROLEE                  |
| Un changement a la fois                          |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| COMPARER AVANT / APRES                           |
| Latence, debit, erreurs, ressources              |
+--------------------------------------------------+
                        |
                        v
+--------------------------------------------------+
| DOCUMENTATION ET RETOUR ARRIERE                  |
+--------------------------------------------------+
```

## 1.3 Principe fondamental : mesurer avant d'optimiser

Une modification peut améliorer une métrique tout en dégradant une autre.

Par exemple :

- Réduire la latence CPU peut augmenter la consommation énergétique.
- Accroître la taille d'un cache peut réduire les accès disque, mais augmenter la pression mémoire.
- Augmenter le parallélisme peut accroître le débit, mais provoquer davantage de contention.
- Réduire la fréquence de collecte des journaux peut alléger le système, mais dégrader la capacité d'investigation.

Une optimisation sérieuse doit donc indiquer :

1. La mesure initiale.
2. Le mécanisme soupçonné.
3. Le changement réalisé.
4. La mesure après modification.
5. Les éventuels effets secondaires.
6. Les conditions de retour arrière.

## 1.4 Les méthodes USE et RED

La méthode USE examine une ressource en recherchant :

- **Utilization :** proportion d'utilisation de la ressource.
- **Saturation :** demande qui ne peut pas être servie immédiatement, souvent représentée par des files ou du temps d'attente.
- **Errors :** erreurs associées à la ressource.

Elle se prête notamment à l'analyse du CPU, du stockage et des interfaces réseau.

Pour un service, la méthode RED examine :

- **Rate :** débit de requêtes.
- **Errors :** erreurs.
- **Duration :** durée de traitement.

Les deux approches sont complémentaires. USE aide à chercher les limitations des ressources ; RED aide à observer le comportement du service.

### Exemple d'utilisation de USE

| Ressource | Utilisation | Saturation | Erreurs |
|---|---|---|---|
| CPU | Temps CPU consommé | Tâches prêtes en attente | Événements matériels éventuels |
| Mémoire | Capacité utilisée | Pression mémoire et récupération répétée | Échecs d'allocation, OOM |
| Stockage | Temps occupé et activité | Files, latence et attente I/O | Erreurs d'entrée-sortie |
| Réseau | Débit et activité de l'interface | Files et pertes de paquets | Erreurs, drops, retransmissions |

Le choix exact des métriques dépend du matériel et des outils disponibles.

**Référence méthodologique :** Brendan Gregg, *The USE Method* et *Performance Analysis Methodology* :
- https://www.brendangregg.com/usemethod.html
- https://www.brendangregg.com/methodology.html


# 2. Architecture interne du noyau Linux

Comprendre la performance nécessite de savoir où s'exécutent les traitements, comment les programmes demandent les services du noyau et quelles couches interviennent lors d'une opération.

## 2.1 Espace utilisateur et espace noyau

Les processeurs modernes proposent plusieurs niveaux de privilèges.

Dans le modèle Linux courant, on distingue principalement :

- L'espace utilisateur, dans lequel s'exécutent les applications ordinaires.
- L'espace noyau, qui fournit les mécanismes privilégiés d'accès aux ressources.

Une application ne peut normalement pas manipuler arbitrairement le matériel. Elle utilise les interfaces du système d'exploitation.

### Schéma

```text
+-----------------------------------------------------+
| ESPACE UTILISATEUR                                  |
|                                                     |
| Application | Bibliotheques | Runtime | Threads     |
|                                                     |
| Code de l'application, donnees et logique metier    |
+-----------------------------------------------------+
                         |
                         | Appel systeme
                         v
+-----------------------------------------------------+
| FRONTIERE UTILISATEUR / NOYAU                       |
|                                                     |
| Validation des arguments et controles d'acces       |
+-----------------------------------------------------+
                         |
                         v
+-----------------------------------------------------+
| ESPACE NOYAU                                        |
|                                                     |
| Ordonnanceur                                       |
| Gestionnaire memoire virtuelle                      |
| VFS et systemes de fichiers                         |
| Pile reseau                                         |
| Pilotes et interruptions                            |
+-----------------------------------------------------+
                         |
                         v
+-----------------------------------------------------+
| MATERIEL                                            |
|                                                     |
| CPU | RAM | SSD | NIC | Controleurs                 |
+-----------------------------------------------------+
```

Le passage dans le noyau ne signifie pas nécessairement qu'un processus devient plus privilégié au sens administratif. Il s'agit d'une transition contrôlée vers du code du noyau exécuté avec les privilèges appropriés.

## 2.2 Le noyau monolithique modulaire

Linux est généralement décrit comme un noyau monolithique modulaire.

Le terme monolithique indique que de nombreuses fonctions centrales sont exécutées dans un espace noyau commun.

Le terme modulaire souligne que certaines fonctionnalités, notamment des pilotes, peuvent être fournies par des modules chargés dynamiquement lorsque la configuration et la politique de sécurité le permettent.

Cela ne signifie pas que tous les pilotes sont chargés à la demande ou qu'ils peuvent tous être retirés sans risque.

### Schéma des grandes sous-parties

```text
+---------------------------------------------------+
|                 NOYAU LINUX                       |
+---------------------------------------------------+
| Ordonnancement                                    |
| Memoire virtuelle                                 |
| Appels systeme                                    |
| Gestion des interruptions                        |
| VFS et systemes de fichiers                       |
| Pile reseau                                       |
| IPC et mecanismes de synchronisation              |
| Pilotes                                           |
| Gestion de l'energie et des ressources            |
+---------------------------------------------------+
                         |
                         v
+---------------------------------------------------+
| CPU | RAM | Stockage | Cartes reseau | Peripheriques|
+---------------------------------------------------+
```

Ces composants coopèrent. Un problème de latence peut se propager entre plusieurs sous-systèmes.

## 2.3 Le Virtual File System

Le VFS (*Virtual File System*) fournit une couche commune d'accès aux opérations de fichiers.

Une application utilise normalement des appels système tels que `openat`, `read`, `write`, `stat` ou `close`.

Le VFS permet au noyau de diriger ces opérations vers le système de fichiers approprié.

### Schéma d'une lecture de fichier

```text
Application
    |
    | openat()
    v
VFS
    |
    v
Resolution du chemin
    |
    v
Systeme de fichiers
    |
    +----> Cache de pages : donnees deja presentes ?
    |                 |
    |                 +-- Oui --> Lecture possible depuis la memoire
    |                 |
    |                 +-- Non --> Entree-sortie necessaire
    |
    v
Resultat transmis au processus
```

Ce schéma simplifie un chemin d'exécution qui peut également inclure des vérifications de permissions, des opérations de stockage asynchrones, du chiffrement, des couches réseau ou d'autres mécanismes.

## 2.4 Interruptions et softirqs

Les périphériques peuvent signaler des événements par des interruptions.

Une interruption permet au système de réagir à un événement matériel, par exemple la disponibilité de données ou la fin d'une opération.

Certaines tâches de traitement différé sont exécutées par d'autres mécanismes du noyau, notamment les softirqs et différents types de threads du noyau.

Le traitement réseau peut ainsi impliquer :

1. La réception d'un événement provenant de la carte réseau.
2. Des traitements liés à l'interruption.
3. Le traitement différé de paquets.
4. La progression dans la pile réseau.
5. La remise des données à la socket et à l'application.

Un excès d'interruptions ou un traitement réseau coûteux peut consommer du CPU même si les processus utilisateurs ne semblent pas être les principaux consommateurs.

## 2.5 Contexte d'exécution

Le noyau exécute du travail dans plusieurs contextes, notamment :

- Le contexte d'un processus en espace utilisateur.
- Le contexte noyau associé à un appel système.
- Le contexte d'interruption.
- Certains contextes de traitement différé.
- Des threads du noyau.

Ces contextes n'ont pas tous les mêmes contraintes. Certaines opérations sont notamment limitées lorsqu'elles s'exécutent dans un contexte où le sommeil ou le blocage n'est pas permis.

Pour l'analyse des performances, il est utile de distinguer le CPU consommé par le code utilisateur de celui consommé par le noyau.

## 2.6 Examiner la version et la configuration du noyau

Pour afficher la version du noyau :

```bash
uname -r
```

Pour afficher la ligne de commande du démarrage :

```bash
cat /proc/cmdline
```

Pour consulter les informations de construction exposées :

```bash
cat /proc/version
```

Selon la distribution, d'autres fichiers ou commandes peuvent fournir des informations sur la configuration du noyau.

Le fichier `.config` du noyau n'est pas nécessairement installé ou accessible sur chaque machine.

Le comportement disponible dépend de la version, des options de compilation, de l'architecture et des politiques du système.


# 3. Les appels système et le chemin d'exécution

Un appel système est une interface contrôlée permettant à un programme de demander une opération au noyau.

Comprendre ces appels aide à analyser les applications qui effectuent un grand nombre d'opérations de fichiers, de communications réseau ou de transitions entre espaces utilisateur et noyau.

## 3.1 Appel de bibliothèque et appel système

Une application peut appeler une fonction de bibliothèque, laquelle utilise éventuellement un ou plusieurs appels système.

Par exemple, une fonction de lecture de bibliothèque peut finir par demander une lecture de données au noyau.

Toutes les fonctions de bibliothèque ne correspondent pas directement à un appel système unique.

### Schéma

```text
Code applicatif
      |
      v
Fonction de bibliotheque
      |
      v
Preparation des arguments
      |
      v
Appel systeme
      |
      v
Code noyau
      |
      v
Resultat ou erreur
      |
      v
Retour vers l'application
```

Le coût d'une opération dépend non seulement du passage dans le noyau, mais aussi du travail réalisé, des données nécessaires et de l'état des ressources.

## 3.2 Pourquoi un programme peut-il effectuer trop d'appels système ?

Exemples :

- Lecture de très petits blocs de données.
- Ouverture et fermeture répétées de fichiers.
- Nombre excessif de requêtes réseau.
- Consultations fréquentes de métadonnées.
- Synchronisation trop fréquente entre threads.

Un profilage peut montrer qu'une application passe beaucoup de temps dans des fonctions liées aux entrées-sorties ou aux appels système.

Il faut alors établir si le coût vient du nombre d'appels, du temps passé dans chaque appel ou de l'attente d'une ressource externe.

## 3.3 Examiner les appels système avec `strace`

`strace` permet d'observer des appels système et les signaux associés à un processus.

Pour examiner une commande de test :

```bash
strace -c ls /tmp
```

L'option `-c` produit un résumé des appels système observés, selon les possibilités de la version.

Pour observer les appels d'une commande :

```bash
strace -f commande
```

L'option `-f` permet de suivre les processus enfants et les threads créés, selon le comportement de l'outil.

**Important :** le traçage peut ralentir significativement un programme et produire beaucoup de données. Ne l'activez pas sans précaution sur une application de production sensible à la latence.

Pour examiner les opérations de fichiers :

```bash
strace -e trace=%file commande
```

La syntaxe et les catégories disponibles dépendent de la version de `strace`.

## 3.4 Lire une sortie de `strace`

Exemple illustratif :

```text
openat(AT_FDCWD, "notes.txt", O_RDONLY) = 3
read(3, "Bonjour\n", 4096) = 8
read(3, "", 4096) = 0
close(3) = 0
```

Interprétation :

- `openat` demande l'ouverture du fichier.
- La valeur de retour `3` est un descripteur de fichier dans le processus.
- `read` lit des données.
- Une lecture retournant `0` indique normalement la fin du fichier.
- `close` ferme le descripteur.

Cette sortie est fictive et sert uniquement à expliquer le fonctionnement général.

## 3.5 Distinguer le coût CPU de l'attente

Une application peut passer beaucoup de temps dans un appel système pour différentes raisons :

- Travail CPU réel dans le noyau.
- Attente de données.
- Attente d'un verrou.
- Attente d'une ressource externe.
- Attente d'une opération de stockage ou de réseau.

Un grand nombre d'appels système ne constitue donc pas, à lui seul, une preuve de ralentissement.

Il faut rapprocher les appels de leurs durées, du contexte d'exécution et des résultats de profilage.


# 4. Ordonnancement CPU et concurrence

L'ordonnanceur détermine quels threads sont exécutés sur les CPU disponibles, selon leur état, leur classe d'ordonnancement et les contraintes applicables.

Une partie importante de l'analyse des performances consiste à déterminer si un programme manque de temps CPU ou s'il attend autre chose.

## 4.1 Processus et threads

Un processus représente un environnement d'exécution. Il peut contenir plusieurs threads partageant certaines ressources du processus.

Chaque thread peut être planifié par l'ordonnanceur.

### Schéma

```text
+---------------------------------+
| Processus applicatif             |
|                                 |
| Memoire partagee                |
| Descripteurs et ressources      |
+---------------------------------+
          |           |
          v           v
+---------------+ +---------------+
| Thread A      | | Thread B      |
| Calcul        | | Traitement I/O|
+---------------+ +---------------+
          |           |
          +-----+-----+
                |
                v
+---------------------------------+
| Ordonnanceur Linux               |
+---------------------------------+
         |               |
         v               v
+--------------+  +--------------+
| CPU logique 0|  | CPU logique 1|
+--------------+  +--------------+
```

Les threads n'avancent pas tous simultanément sur un même cœur. L'ordonnanceur répartit le temps CPU entre les tâches planifiables.

## 4.2 États de processus et disponibilité CPU

Un thread peut être :

- En cours d'exécution.
- Prêt à être exécuté, mais en attente de CPU.
- Endormi en attendant un événement.
- En attente d'une opération interne ou d'une ressource.
- Arrêté ou terminé.

Le fait qu'un thread ne consomme pas de CPU ne signifie pas automatiquement qu'il est bloqué.

Un thread qui attend une réponse réseau peut consommer peu de CPU tout en contribuant à une forte latence applicative.

## 4.3 Le rôle des classes d'ordonnancement

Linux prend en charge plusieurs classes d'ordonnancement.

Les principales familles comprennent :

- Les tâches ordinaires, généralement dans la politique `SCHED_OTHER` ou `SCHED_NORMAL`.
- Les tâches de traitement par lots, notamment via `SCHED_BATCH`.
- Certains comportements à faible latence, comme `SCHED_IDLE`.
- Des classes à temps réel, telles que `SCHED_FIFO` et `SCHED_RR`.
- Des mécanismes spécialisés et évolutifs selon les versions du noyau.

Il ne faut pas supposer que tous les threads sont traités avec les mêmes règles.

Le comportement exact des classes ordinaires évolue dans le noyau. La documentation officielle décrit notamment l'évolution entre les mécanismes historiques CFS et EEVDF.

Référence technique :
https://docs.kernel.org/scheduler/

## 4.4 Comprendre les valeurs nice

Pour examiner les valeurs nice :

```bash
ps -eo pid,tid,ni,pri,comm
```

Les colonnes et le niveau de détail dépendent du format demandé.

La valeur nice influence le partage relatif du CPU pour les tâches ordinaires concernées.

Lancer une commande avec une valeur nice :

```bash
nice -n 10 commande
```

Modifier un processus existant :

```bash
renice 10 -p PID
```

Le changement de priorité peut affecter la progression d'une tâche, mais ne répare pas un problème de verrou, de réseau ou de stockage.

## 4.5 Affinité CPU

L'affinité CPU restreint les processeurs logiques sur lesquels un processus ou un thread peut être planifié.

Examiner l'affinité d'un processus :

```bash
taskset -pc PID
```

Lancer un programme de test avec une affinité limitée :

```bash
taskset -c 0 commande
```

Cette commande est illustrative et suppose que le CPU logique `0` existe et qu'il est autorisé dans l'environnement.

L'affinité peut aider dans des scénarios spécifiques, mais elle peut également :

- Réduire la flexibilité de l'ordonnanceur.
- Concentrer la charge sur un sous-ensemble de CPU.
- Dégrader la répartition de charge.
- Modifier l'accès aux caches ou à la mémoire NUMA.

N'isolez pas des cœurs sans mesure préalable.

## 4.6 Détecter la contention CPU

Un CPU peut être occupé à exécuter du travail, tandis que d'autres threads attendent dans une file d'exécution.

La présence d'une forte charge CPU doit être rapprochée :

- Du nombre de CPU logiques.
- Du nombre de threads prêts.
- Du taux d'utilisation par CPU.
- Du temps passé en mode utilisateur et noyau.
- Des limitations de cgroups.
- De l'attente liée à d'autres ressources.

Un processus consommant 100 % d'un cœur ne signifie pas forcément que l'ensemble d'une machine multicœur est saturé.

## 4.7 Le problème des moyennes

Une moyenne peut masquer des pics courts.

Exemple :

```text
Fenetre de mesure : 60 secondes

Charge pendant 55 secondes : faible
Charge pendant 5 secondes  : tres elevee

Moyenne sur 60 secondes    : relativement faible
Latence pendant le pic     : tres elevee
```

C'est pourquoi l'analyse doit tenir compte des percentiles, des intervalles de mesure et du comportement réel de l'application.

## 4.8 Examiner la charge moyenne

```bash
uptime
```

La charge moyenne reflète des tâches dans certains états d'exécution et d'attente. Elle ne correspond pas directement à un pourcentage CPU.

Une charge moyenne de `4` peut être relativement forte sur une machine limitée à deux CPU logiques, mais représenter une situation différente sur une machine dotée de nombreuses unités de calcul.

La charge doit être interprétée selon la topologie, la période d'observation et les ressources réellement accessibles au processus.

## 4.9 Vérifier les limites CPU d'un conteneur

Un conteneur peut être limité par sa configuration cgroups.

Il est possible que l'hôte dispose de CPU disponibles alors que le conteneur subit une limitation.

La capacité réellement disponible peut être influencée par :

- La configuration de quota.
- Le nombre de CPU autorisés.
- L'affinité.
- Les contraintes d'un ordonnanceur supérieur.
- Les limites imposées par la plateforme.

Il faut distinguer la saturation physique de l'hôte et la saturation d'une limite de ressources.


# 5. Mesure approfondie des performances CPU

L'analyse CPU consiste à déterminer ce que les processeurs exécutent, pourquoi ils sont occupés et si le travail effectué produit le résultat attendu.

## 5.1 Mode utilisateur et mode noyau

Le CPU peut exécuter du code utilisateur ou du code noyau.

Les statistiques système courantes distinguent notamment :

- `user` : temps passé en mode utilisateur.
- `system` : temps passé en mode noyau.
- `idle` : temps inactif.
- `iowait` : temps comptabilisé comme attente d'entrées-sorties dans les statistiques Linux.
- `irq` : temps associé à certains traitements d'interruptions.
- `softirq` : temps associé aux traitements différés concernés.
- `steal` : temps de CPU non fourni à la machine virtuelle par l'hyperviseur, selon l'environnement.

Le sens précis des champs doit être vérifié dans la documentation de la version du système.

## 5.2 Examiner `/proc/stat`

```bash
head -n 5 /proc/stat
```

Le fichier expose des statistiques du noyau. La ligne `cpu` regroupe les temps CPU cumulés.

Une lecture ponctuelle ne suffit pas à calculer directement un pourcentage fiable. Il faut comparer des échantillons pris à des instants distincts, en tenant compte de la définition des champs.

Pour des analyses plus pratiques, des outils spécialisés calculent ces différences.

## 5.3 Utiliser `mpstat`

Si l'outil est disponible :

```bash
mpstat -P ALL 1 5
```

Cette commande demande généralement des statistiques CPU par processeur pendant cinq intervalles d'une seconde.

Elle permet de repérer :

- Un CPU davantage sollicité que les autres.
- Un comportement déséquilibré.
- Une activité importante en mode noyau.
- Des différences entre les CPU logiques.
- Une attente ou un temps de vol significatif selon l'environnement.

L'outil est souvent fourni par le paquet `sysstat`, selon la distribution.

## 5.4 Utiliser `pidstat`

```bash
pidstat -u 1 5
```

Affiche des statistiques CPU par processus selon les options et les intervalles demandés.

Pour examiner les entrées-sorties des processus :

```bash
pidstat -d 1 5
```

Pour examiner certaines statistiques mémoire :

```bash
pidstat -r 1 5
```

La disponibilité exacte des options dépend de la version.

## 5.5 Comparer charge totale et charge par processus

Supposons que `top` indique une activité CPU élevée.

La question suivante est essentielle :

**Quel processus ou quel ensemble de threads explique cette activité ?**

Utilisez :

```bash
ps -eo pid,ppid,user,%cpu,%mem,stat,comm --sort=-%cpu | head
```

Puis examinez les processus concernés, leur commande, leurs journaux et les opérations qu'ils réalisent.

Une liste instantanée peut manquer une charge de courte durée. Plusieurs échantillons sont préférables.

## 5.6 Comprendre les cycles et les instructions

Les processeurs exécutent des instructions en consommant des cycles matériels.

Deux programmes exécutant un même volume de travail peuvent présenter des caractéristiques différentes.

Les causes possibles comprennent :

- Un nombre d'instructions différent.
- Des instructions de coûts différents.
- Des défauts de cache.
- Des branches mal prédites.
- Des accès mémoire coûteux.
- Des attentes sur des ressources matérielles.
- Un parallélisme insuffisant.
- Des verrous ou une synchronisation fréquente.

## 5.7 L'indicateur IPC

IPC signifie *Instructions Per Cycle*.

Il représente le nombre d'instructions retirées ou comptabilisées par cycle CPU selon la définition de l'événement utilisé.

Un IPC élevé peut indiquer que le processeur exécute efficacement certaines charges. Il ne permet pas à lui seul de conclure qu'une application est optimale.

L'IPC dépend :

- Du processeur.
- Du type d'instructions.
- De la charge.
- De la mémoire.
- Des compteurs matériels disponibles.
- Des événements choisis.

Il ne faut donc pas comparer aveuglément des IPC issus de processeurs ou de charges différentes.

## 5.8 Mesurer avec `perf stat`

Si `perf` est installé et autorisé :

```bash
perf stat -- sleep 2
```

Cette commande exécute une commande pendant que `perf stat` collecte des statistiques accessibles.

Un exemple plus intéressant consiste à examiner un programme de test :

```bash
perf stat -- ./programme-test
```

Les événements disponibles et les permissions nécessaires varient selon la version du noyau, la configuration et l'architecture matérielle.

Pour examiner les événements disponibles :

```bash
perf list
```

## 5.9 Comprendre les principaux événements

Selon le processeur, `perf stat` peut rendre disponibles des événements tels que :

- `cycles`
- `instructions`
- `branches`
- `branch-misses`
- `cache-references`
- `cache-misses`

Exemple :

```bash
perf stat \
    -e cycles,instructions,branches,branch-misses \
    -- ./programme-test
```

Cette commande ne fonctionnera que si le programme existe et si les événements sont disponibles et autorisés.

Les noms des événements matériels et leurs limites peuvent varier.

## 5.10 Pourquoi un événement matériel peut être indisponible

Tous les CPU ne proposent pas les mêmes compteurs matériels. Certains événements nécessitent une prise en charge spécifique du processeur ou du noyau.

L'accès peut aussi être restreint par les paramètres de sécurité, les capacités du processus ou les politiques de la plateforme.

Ne diminuez pas aveuglément les protections de `perf` pour faire fonctionner un outil. Les données collectées peuvent exposer des informations sensibles.

Référence officielle :
https://docs.kernel.org/admin-guide/perf-security.html

## 5.11 Temps CPU contre temps écoulé

Il faut distinguer le temps CPU du temps réel écoulé.

Supposons :

```text
Temps ecoule : 10 secondes
Temps CPU total : 2 secondes
```

Le programme a peut-être passé une partie du temps à attendre ou a été exécuté en parallèle sur plusieurs threads, selon la mesure et la manière dont le temps CPU est comptabilisé.

Il ne faut pas conclure directement à une cause unique.

Une application peut être lente malgré une faible consommation CPU lorsque son exécution est dominée par l'attente de ressources.

## 5.12 Détecter les commutations de contexte

Une commutation de contexte se produit lorsque l'ordonnanceur change la tâche exécutée sur un CPU.

Un nombre important de commutations peut provenir :

- D'un grand nombre de threads.
- D'une charge fortement concurrente.
- De tâches fréquemment réveillées.
- D'une synchronisation intensive.
- De contraintes de planification.

Un nombre élevé n'est pas automatiquement mauvais. Il faut l'interpréter avec la charge, la durée de traitement et les résultats applicatifs.

Si l'outil est disponible :

```bash
vmstat 1 5
```

La sortie comprend plusieurs statistiques système, dont certaines liées aux changements de contexte et à la planification.

## 5.13 Identifier un problème CPU

Une hypothèse CPU devient plus crédible lorsque plusieurs éléments concordent :

- Le CPU est fortement sollicité pendant l'incident.
- Une ou plusieurs tâches expliquent cette consommation.
- Les temps de réponse augmentent.
- Les tâches sont en concurrence pour la ressource CPU.
- Les événements de profilage identifient une portion coûteuse du code.

Si la charge provient surtout d'attentes de stockage, de verrous ou du réseau, une augmentation de CPU n'est pas forcément la meilleure correction.


# 6. Profilage avec `perf`

`perf` est une suite d'outils de performance pour Linux. Elle utilise notamment les interfaces d'événements de performance disponibles dans le noyau et, selon le cas, les compteurs matériels.

## 6.1 Pourquoi profiler ?

Un profilage cherche à répondre à des questions telles que :

- Quelles fonctions consomment le plus de CPU ?
- Quel code revient fréquemment dans les échantillons ?
- Le temps est-il passé dans l'espace utilisateur ou le noyau ?
- Quelles fonctions sont associées aux défauts de cache observés ?
- Quel chemin d'exécution devient dominant pendant l'incident ?

Un profil aide à localiser les coûts. Il ne remplace pas l'interprétation du programme.

## 6.2 `perf stat` : mesurer des compteurs

```bash
perf stat -- ./programme-test
```

L'outil collecte un ensemble de compteurs et de statistiques pendant l'exécution.

Il est utile pour comparer des mesures répétées, à condition de conserver une charge et un environnement suffisamment comparables.

## 6.3 `perf record` : enregistrer des échantillons

```bash
perf record -- ./programme-test
```

Cette commande enregistre les échantillons produits pendant l'exécution du programme.

Elle génère généralement un fichier de données `perf.data` dans le répertoire courant, sauf configuration différente.

Les données peuvent contenir des noms de processus, des chemins, des symboles, des adresses et d'autres éléments sensibles. Protégez les fichiers générés.

## 6.4 Examiner le profil avec `perf report`

```bash
perf report
```

Cette commande présente les informations enregistrées dans le fichier de profil.

Les résultats peuvent afficher :

- Des symboles et fonctions.
- Des pourcentages d'échantillons.
- Des chemins d'appel.
- Des objets binaires.
- Des informations liées à la pile.

La qualité de l'analyse dépend de la disponibilité des symboles, de l'architecture, de la méthode de collecte et du type d'échantillonnage.

## 6.5 Profiler une commande spécifique

Exemple :

```bash
perf record -g -- ./programme-test
```

L'option `-g` demande la collecte d'informations de pile lorsque le mode choisi et l'environnement le permettent.

Le déroulement peut dépendre :

- De la méthode de collecte.
- De la présence des symboles.
- Du support de l'architecture.
- Du type de compilation.
- Des permissions du noyau.
- Des politiques de sécurité.

## 6.6 Comprendre le profil d'échantillonnage

Un profil d'échantillonnage collecte des observations à certains moments. Les échantillons représentent une approximation statistique du comportement pendant la période observée.

Un pourcentage de 20 % dans une fonction ne signifie pas nécessairement que la fonction représente exactement 20 % de tout le temps d'exécution dans toutes les situations.

Il faut comprendre :

- L'événement échantillonné.
- La fenêtre d'observation.
- Le type de charge.
- La méthode d'agrégation.
- Les limites de la collecte.

## 6.7 Comprendre les symboles

Un exécutable compilé peut contenir des informations de débogage ou des symboles qui facilitent l'identification des fonctions.

Sans symboles, certaines fonctions peuvent apparaître comme des adresses ou sous des noms incomplets.

Les distributions peuvent proposer des paquets de symboles de débogage. Leur installation doit être adaptée à la version exacte du noyau ou du logiciel.

Ne téléchargez pas des symboles arbitraires qui ne correspondent pas au binaire examiné.

## 6.8 Exemple d'analyse guidée

Supposons qu'un programme consomme beaucoup de CPU.

Étape 1 : établir le temps total et les compteurs.

```bash
perf stat -- ./programme-test
```

Étape 2 : collecter le profil.

```bash
perf record -g -- ./programme-test
```

Étape 3 : examiner les fonctions dominantes.

```bash
perf report
```

Étape 4 : formuler une hypothèse.

Exemples :

- Une fonction de conversion consomme trop de cycles.
- Une opération de traitement de texte est exécutée de manière répétée.
- Le programme effectue des copies inutiles.
- Un chemin coûteux dépend d'une bibliothèque.
- Une fonction du noyau apparaît dans le profil parce que l'application effectue beaucoup d'entrées-sorties.

Étape 5 : tester une modification limitée puis comparer.

La modification doit être justifiée par le profil. Évitez d'optimiser une fonction simplement parce qu'elle est visible dans le rapport si elle n'a pas d'effet significatif sur les résultats qui comptent.

## 6.9 Profils CPU et flame graphs

Un flame graph est une représentation des piles d'appels collectées pendant un profilage.

Dans une représentation de ce type :

- La largeur correspond généralement à l'importance relative des échantillons ou de la valeur affichée.
- Les blocs représentent des fonctions.
- Les relations verticales représentent les niveaux de pile.
- Les piles partagent des chemins d'appel.

La largeur n'est pas une mesure directe de la durée individuelle d'une invocation de fonction. Elle reflète la métrique et la méthode d'agrégation utilisées pour produire le graphique.

Les outils de génération dépendent de l'environnement et peuvent nécessiter une préparation des données.

## 6.10 Profiler sans modifier la charge étudiée

Le profilage introduit un coût. Il peut changer le comportement du programme, surtout avec des fréquences d'échantillonnage élevées ou une trace très détaillée.

Il est recommandé de :

1. Mesurer une référence sans profilage.
2. Effectuer une mesure avec profilage.
3. Évaluer l'impact de l'outil.
4. Utiliser une collecte suffisante pour répondre à la question.
5. Comparer les données dans le contexte du coût de mesure.

## 6.11 Sécurité des fichiers de profilage

Les fichiers produits par `perf` peuvent contenir des informations relatives aux programmes surveillés et à leur contexte d'exécution.

Ils doivent être protégés comme des données de diagnostic potentiellement sensibles.

L'accès au profilage peut être contrôlé par des paramètres du noyau et des capacités Linux. Évitez de désactiver globalement les protections ou de rendre la collecte accessible à tous les utilisateurs.


# 7. Mémoire virtuelle et gestion physique de la mémoire

La mémoire est l'un des sous-systèmes les plus complexes à interpréter.

Linux gère des adresses virtuelles, des pages physiques, des caches, des tables de pages, des mécanismes de partage et des stratégies de récupération mémoire.

Une consommation mémoire élevée ne signifie pas automatiquement une fuite ou une panne.

## 7.1 Mémoire virtuelle

Un processus utilise normalement un espace d'adresses virtuelles.

Le système associe les adresses virtuelles à des pages physiques selon les mécanismes de mémoire virtuelle.

### Schéma conceptuel

```text
+-----------------------------------+
| Processus A                       |
| Espace d'adresses virtuelles      |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Tables de pages                   |
| Associations virtuel / physique   |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Pages physiques                   |
| RAM                               |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Cache, partage et mecanismes MM   |
+-----------------------------------+
```

Ce schéma est simplifié. Les mécanismes comprennent notamment le partage de pages, les mappings de fichiers, les défauts de page et les protections d'accès.

## 7.2 Pourquoi ne pas assimiler mémoire virtuelle et RAM utilisée ?

Un espace virtuel réservé n'est pas nécessairement entièrement présent en RAM.

Un processus peut avoir :

- Des zones virtuelles réservées.
- Des pages effectivement résidentes.
- Des pages partagées.
- Des mappings de fichiers.
- Des pages récupérables.
- Des pages privées.
- Des pages non encore matérialisées physiquement.

La somme de certaines tailles virtuelles ne doit donc pas être interprétée directement comme la quantité de RAM que le processus occupe.

## 7.3 RSS et VSZ

Les outils `ps` ou `top` peuvent afficher des informations sur la mémoire.

- RSS : taille de la mémoire résidente associée au processus selon la métrique utilisée.
- VSZ : taille de l'espace virtuel associé au processus.

Ces valeurs ont des significations différentes.

La RSS ne permet pas toujours d'attribuer précisément la mémoire physique au processus, car certaines pages sont partagées.

La VSZ peut comprendre des mappings qui ne correspondent pas à une consommation physique immédiate.

## 7.4 Examiner la mémoire d'un processus

```bash
ps -o pid,comm,vsz,rss,%mem -p PID
```

Remplacez `PID` par un identifiant réel.

Pour des informations détaillées sur les mappings mémoire, lorsque les permissions le permettent :

```bash
cat /proc/PID/status
```

Le fichier expose diverses statistiques et caractéristiques du processus.

Pour des analyses par mapping, `/proc/PID/smaps` peut fournir davantage d'informations, mais sa sortie est plus volumineuse et plus complexe.

## 7.5 Examiner la mémoire globale

```bash
free -h
```

La commande fournit une synthèse de la mémoire, du cache et du swap.

Pour afficher les statistiques détaillées exposées par le noyau :

```bash
less /proc/meminfo
```

Parmi les champs intéressants :

- `MemTotal`
- `MemFree`
- `MemAvailable`
- `Buffers`
- `Cached`
- `SwapTotal`
- `SwapFree`
- Certaines statistiques de récupération et de page

Les noms et détails exacts dépendent de la version du noyau et des fonctionnalités disponibles.

## 7.6 Comprendre `MemAvailable`

La mémoire libre est la quantité de RAM qui n'est pas actuellement utilisée selon la définition des statistiques.

La mémoire disponible tente d'estimer la quantité de mémoire que le système peut fournir à de nouvelles charges sans recourir à une pression excessive sur le swap.

Il ne faut donc pas conclure qu'un système est à court de mémoire simplement parce que `MemFree` est faible.

Linux utilise la RAM disponible pour conserver des données en cache, ce qui peut améliorer les performances.

## 7.7 Cache de pages

Le cache de pages permet de conserver en mémoire des données associées aux fichiers afin de réduire les accès au stockage.

### Schéma

```text
Application demande un fichier
             |
             v
+------------------------------+
| Cache de pages               |
+------------------------------+
        |              |
        | Trouve       | Absence ou page non disponible
        | la page      |
        v              v
 Lecture depuis     Demande d'I/O
 la memoire         au stockage
        |              |
        +------+-------+
               |
               v
       Donnees disponibles
```

Le comportement réel peut varier selon les mappings, les systèmes de fichiers, la synchronisation et les opérations effectuées.

La présence d'un grand cache de pages n'est pas en elle-même un problème. Le noyau peut récupérer certaines pages lorsque d'autres besoins mémoire apparaissent.

## 7.8 Défauts de page

Un défaut de page se produit lorsque le traitement d'une adresse mémoire nécessite une intervention du mécanisme de mémoire virtuelle.

Il existe plusieurs situations :

- Défaut mineur : la page peut être rendue accessible sans lire les données depuis le stockage dans le scénario concerné.
- Défaut majeur : le traitement peut nécessiter une entrée-sortie, par exemple pour charger une page absente depuis un fichier ou une zone de swap.

Cette classification est liée au mécanisme effectivement utilisé et ne représente pas directement une gravité applicative.

Un programme peut générer beaucoup de défauts mineurs sans présenter de problème.

Un nombre élevé de défauts majeurs peut être plus préoccupant s'il s'accompagne d'attentes et d'une hausse de latence.

## 7.9 Examiner les défauts de page

```bash
pidstat -r 1 5
```

Cette commande permet d'observer certaines statistiques mémoire par processus si l'outil est disponible.

D'autres outils de mesure peuvent exposer les défauts mineurs et majeurs.

Il faut examiner les variations pendant la charge et les rapprocher des latences et des ressources disponibles.

## 7.10 Comprendre la récupération mémoire

Lorsque le noyau a besoin de libérer des pages physiques, il peut notamment :

- Récupérer certaines pages de cache.
- Écrire des pages modifiées vers leur stockage approprié.
- Déplacer certaines pages anonymes vers le swap lorsque cette stratégie est utilisée.
- Déclencher d'autres opérations de gestion mémoire.

La récupération mémoire est normale. Elle devient problématique lorsqu'elle génère un coût important pour les applications.

## 7.11 Pression mémoire et thrashing

Le thrashing désigne une situation où une activité excessive de récupération ou d'échange mémoire dégrade fortement la progression utile des programmes.

Un système peut passer une grande partie de son temps à déplacer ou récupérer des pages au lieu de faire avancer efficacement les applications.

Signes possibles :

- Latences applicatives croissantes.
- Activité de swap soutenue.
- Nombreux défauts de page majeurs.
- Pression mémoire élevée.
- Utilisation CPU importante liée à la gestion mémoire.
- Temps d'attente important.

Aucun indicateur unique ne suffit à confirmer le thrashing.

## 7.12 Examiner le swap

```bash
swapon --show
```

Affiche les zones de swap actives lorsqu'elles existent.

```bash
free -h
```

Permet de consulter les statistiques mémoire et swap.

La présence de données dans le swap ne prouve pas qu'une charge est actuellement en difficulté. Des pages peu utilisées peuvent y rester sans que le système présente une dégradation notable.

L'analyse doit porter sur l'activité, la pression et les conséquences sur les temps de réponse.

## 7.13 Comprendre l'OOM killer

Lorsque le système ne parvient plus à satisfaire les besoins mémoire dans certains contextes, un mécanisme d'out-of-memory peut intervenir.

Le noyau ou un gestionnaire associé à l'environnement peut sélectionner des processus à terminer afin de tenter de rétablir une situation acceptable.

Dans les conteneurs, l'OOM peut également se produire à l'intérieur d'un cgroup soumis à une limite mémoire.

Pour examiner les messages liés à la mémoire :

```bash
journalctl -k | grep -i -E 'oom|out of memory|killed process'
```

Cette commande recherche certains termes dans les journaux du noyau accessibles au contexte courant.

L'absence de correspondance ne signifie pas que toute hypothèse de pression mémoire est exclue.

## 7.14 Éviter les conclusions erronées

Une machine qui utilise beaucoup de RAM peut fonctionner correctement.

Une machine qui possède encore de la RAM peut néanmoins rencontrer une limite mémoire dans un conteneur.

Une machine qui utilise peu de RAM peut tout de même présenter une forte latence à cause du stockage ou d'un verrou.

Le diagnostic expert consiste à relier la consommation, la pression, les erreurs et le comportement applicatif.


# 8. Pression mémoire, swap et OOM

Ce chapitre approfondit le diagnostic de la mémoire à l'aide de plusieurs sources d'observation.

## 8.1 Comprendre les zones de mémoire

La mémoire du système peut être utilisée par des pages anonymes, des pages associées aux fichiers, des caches et de nombreuses structures internes au noyau.

Les détails sont complexes et dépendent de la version du noyau, de l'architecture et des workloads.

Il faut éviter de réduire l'analyse à une seule valeur de mémoire consommée.

## 8.2 Examiner les statistiques de mémoire

```bash
grep -E 'MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree' /proc/meminfo
```

Cette commande sélectionne quelques champs utiles.

Leur interprétation doit tenir compte de la définition de chaque statistique.

## 8.3 Examiner les statistiques de récupération mémoire

Selon les outils disponibles :

```bash
vmstat 1 5
```

Les colonnes fournissent un aperçu de plusieurs statistiques système, notamment certaines liées au swap, aux entrées-sorties et à l'activité CPU.

Pour comprendre une situation, examinez plusieurs intervalles successifs plutôt qu'un seul instantané.

## 8.4 Les limites du diagnostic par swap

Il existe plusieurs situations :

**Situation A : swap présent, latence normale.**

Des pages peu utilisées peuvent avoir été placées dans le swap sans entraîner de dégradation notable.

**Situation B : swap actif, latence dégradée.**

Des pages nécessaires peuvent être régulièrement déplacées ou rechargées, ce qui augmente le temps de réponse.

**Situation C : pression mémoire dans un conteneur.**

Le conteneur peut atteindre sa limite de mémoire alors que l'hôte dispose encore de ressources.

La correction doit dépendre du scénario.

## 8.5 Examiner la pression mémoire avec PSI

Linux expose des informations de pression de ressources par l'interface Pressure Stall Information, lorsqu'elle est disponible.

Inspecter :

```bash
cat /proc/pressure/memory
```

Exemple illustratif :

```text
some avg10=0.35 avg60=0.20 avg300=0.10 total=123456
full avg10=0.00 avg60=0.00 avg300=0.00 total=0
```

Les valeurs et leur format dépendent du système.

Interprétation générale :

- `some` mesure du temps durant lequel au moins certaines tâches non inactives subissent une attente liée à la ressource.
- `full` correspond à des périodes où toutes les tâches non inactives concernées sont simultanément bloquées par la pression de cette ressource.

Les valeurs `avg10`, `avg60` et `avg300` sont des moyennes sur des fenêtres temporelles différentes, exprimées selon la définition PSI.

Référence officielle :
https://docs.kernel.org/accounting/psi.html

## 8.6 Pourquoi PSI améliore le diagnostic

Une simple utilisation mémoire ne dit pas nécessairement combien de progression utile est perdue.

PSI vise à mesurer la pression subie par les tâches.

Un système peut posséder de la mémoire libre ou récupérable, tout en perdant du temps à attendre certaines ressources.

L'intérêt est de relier la pression observable aux conséquences sur les applications.

## 8.7 Examiner les limites mémoire d'un cgroup

Un service peut avoir une limite mémoire qui diffère de celle de l'hôte.

Si le système utilise cgroups v2, les informations pertinentes peuvent apparaître dans son arborescence de contrôle, notamment dans les fichiers `memory.current`, `memory.max` et `memory.events`.

Il faut identifier le cgroup réel du service avant d'interpréter ces fichiers.

La présence d'une limite est particulièrement importante lorsqu'un conteneur est tué alors que l'hôte semble disposer de RAM.

## 8.8 Choisir une correction

Selon le diagnostic, les mesures possibles peuvent comprendre :

- Réduire les allocations inutiles.
- Limiter le parallélisme.
- Corriger une fuite mémoire.
- Réduire le working set.
- Ajuster les limites d'un cgroup après analyse.
- Augmenter les ressources disponibles.
- Corriger un cache ou une stratégie de rétention.
- Réduire des données conservées inutilement.

Augmenter la taille du swap ou modifier les paramètres de récupération mémoire n'est pas une solution automatique.

La modification doit répondre à une cause démontrée.


# 9. NUMA, caches et Huge Pages

Les systèmes modernes peuvent présenter une organisation mémoire et CPU plus complexe qu'une machine à processeur unique.

L'analyse avancée doit tenir compte de la topologie du matériel.

## 9.1 Comprendre NUMA

NUMA signifie *Non-Uniform Memory Access*.

Sur une plateforme NUMA, l'accès à la mémoire peut présenter des coûts différents selon la proximité de la mémoire par rapport au CPU qui réalise l'accès.

### Schéma simplifié

```text
+----------------------------------+
| Noeud NUMA 0                     |
|                                  |
| CPU 0, CPU 1                     |
| Memoire locale                   |
+----------------------------------+
               |
               | Interconnexion
               |
+----------------------------------+
| Noeud NUMA 1                     |
|                                  |
| CPU 2, CPU 3                     |
| Memoire locale                   |
+----------------------------------+
```

Le schéma est conceptuel. Les architectures réelles peuvent posséder plusieurs sockets, de nombreux cœurs et plusieurs niveaux d'interconnexion.

L'accès à la mémoire d'un autre nœud peut être plus coûteux que l'accès à la mémoire locale, selon la plateforme.

## 9.2 Pourquoi la localisation mémoire compte-t-elle ?

Une application peut présenter :

- Des accès mémoire fréquents.
- Une forte dépendance à la latence mémoire.
- Un trafic inter-nœuds important.
- Un déséquilibre entre les CPU et la mémoire utilisée.
- Des migrations de threads ou de pages.

Ces situations peuvent réduire les performances même lorsque la capacité mémoire totale est suffisante.

## 9.3 Examiner la topologie

Si les outils sont disponibles :

```bash
lscpu
```

Et :

```bash
numactl --hardware
```

`numactl --hardware` peut présenter les nœuds et certaines informations de mémoire et de distance NUMA.

La disponibilité et la sortie dépendent de la plateforme.

## 9.4 Examiner l'allocation NUMA

Si `numastat` est disponible :

```bash
numastat
```

Cette commande présente des statistiques liées à NUMA.

Pour certains processus, des options spécifiques permettent d'obtenir davantage d'informations.

Il faut comprendre ce qui est mesuré, car un déséquilibre n'implique pas automatiquement un problème.

## 9.5 Affinité et politique NUMA

Des outils comme `numactl` permettent d'appliquer des contraintes d'affinité ou des politiques d'allocation mémoire.

Ils peuvent être utiles pour des workloads spécifiques, mais une politique imposée arbitrairement peut dégrader le système.

Avant de modifier une politique :

1. Examinez la topologie.
2. Identifiez le profil mémoire de l'application.
3. Mesurez les accès et les migrations.
4. Vérifiez la configuration existante.
5. Testez un changement isolé.
6. Comparez les performances et les effets sur les autres charges.

## 9.6 Comprendre les caches CPU

Les processeurs disposent généralement de plusieurs niveaux de cache.

Ces caches réduisent le coût moyen d'accès aux données par rapport à certains accès mémoire plus éloignés.

Une application peut devenir limitée par :

- Des défauts de cache fréquents.
- Des accès mémoire dispersés.
- Un working set trop volumineux pour un niveau de cache.
- Des conflits d'accès.
- Une contention entre threads.
- Des limites de bande passante mémoire.

Les compteurs disponibles dépendent du processeur. Ils doivent être choisis avec soin.

## 9.7 Localité temporelle et spatiale

La localité temporelle signifie que des données récemment utilisées ont des chances d'être utilisées de nouveau.

La localité spatiale signifie que des données proches de celles qui viennent d'être utilisées peuvent être consultées prochainement.

Les structures de données et les algorithmes peuvent influencer ces propriétés.

Par exemple, un parcours séquentiel d'un tableau en mémoire présente souvent un comportement de localité spatiale plus favorable qu'une succession d'accès aléatoires dispersés.

Le résultat réel dépend de l'architecture, du compilateur, de la charge et des données.

## 9.8 Huge Pages

Les Huge Pages utilisent des tailles de page plus grandes que la taille de page ordinaire, lorsque la configuration et l'application le permettent.

Elles peuvent réduire certains coûts liés à la gestion des tables de pages et à la traduction d'adresses.

Mais elles peuvent aussi :

- Augmenter la granularité d'allocation.
- Réduire la flexibilité de certains usages mémoire.
- Introduire des contraintes de réservation.
- Modifier le comportement de mémoire de l'application.

Les Huge Pages ne sont pas automatiquement bénéfiques pour tous les workloads.

## 9.9 Transparent Huge Pages

Transparent Huge Pages, ou THP, permettent au noyau d'utiliser certaines pages de grande taille de façon transparente pour les applications compatibles.

Le comportement et les possibilités de configuration évoluent selon les versions du noyau.

Avant de modifier THP :

1. Mesurez le comportement actuel.
2. Examinez les défauts de page et l'activité mémoire.
3. Consultez la documentation de la version concernée.
4. Testez sur une charge représentative.
5. Vérifiez la latence, le CPU et la mémoire après changement.

## 9.10 Multi-Gen LRU

Le noyau Linux peut proposer un mécanisme appelé Multi-Gen LRU, une implémentation alternative de la gestion de récupération des pages visant à mieux représenter leur récence d'utilisation.

Sa disponibilité et son activation dépendent de la configuration et de la version du noyau.

La présence du mécanisme ne prouve pas qu'un problème mémoire existe.

Référence officielle :
https://docs.kernel.org/admin-guide/mm/multigen_lru.html


# 10. Stockage, systèmes de fichiers et latence des entrées-sorties

Une application peut être lente parce qu'elle attend des données.

Dans ce scénario, ajouter du CPU ou modifier l'ordonnanceur ne résout pas nécessairement le problème.

## 10.1 Comprendre les couches du stockage

Un chemin d'entrée-sortie peut comprendre :

```text
Application
    |
    v
Appel systeme
    |
    v
VFS
    |
    v
Systeme de fichiers
    |
    v
Couche bloc
    |
    v
Pilote et controleur
    |
    v
SSD, NVMe ou autre stockage
```

Le détail dépend du système de fichiers, du matériel et des chemins utilisés.

Une opération peut être servie depuis la mémoire ou nécessiter un accès au stockage.

## 10.2 Débit, IOPS et latence

Trois notions doivent être distinguées.

**Débit :** quantité de données transférées par unité de temps.

**IOPS :** nombre d'opérations d'entrée-sortie par seconde.

**Latence :** temps nécessaire pour traiter une opération dans les conditions de mesure retenues.

Un stockage peut afficher un débit faible mais une latence élevée lorsqu'il effectue peu d'opérations et qu'elles attendent longtemps.

Inversement, un système peut présenter un débit élevé et une bonne latence sous charge si les opérations sont bien parallélisées.

## 10.3 Examiner l'espace disque

```bash
df -h
```

Cette commande fournit une vue des systèmes de fichiers montés.

Pour examiner les inodes :

```bash
df -i
```

Un manque d'inodes peut limiter la création de nouveaux fichiers même lorsque l'espace en octets n'est pas épuisé.

## 10.4 Examiner les statistiques d'entrées-sorties

Si `iostat` est disponible :

```bash
iostat -xz 1 5
```

Cette commande fournit un aperçu des statistiques de périphériques d'entrée-sortie.

Les indicateurs peuvent inclure :

- Les opérations par seconde.
- Le débit.
- La latence ou le temps moyen d'attente selon le format.
- Le temps d'activité.
- Certaines statistiques de file.

Les champs exacts varient selon la version.

## 10.5 Attention à la colonne d'utilisation du périphérique

Une utilisation élevée du périphérique n'a pas la même signification sur tous les matériels.

Sur un disque mécanique, un temps d'activité proche de 100 % peut indiquer une charge importante.

Sur des SSD modernes ou des périphériques NVMe capables de traiter de nombreuses requêtes parallèles, une seule métrique d'utilisation ne suffit pas à déterminer la saturation.

La latence, le débit, la file et la charge du workload doivent être interprétés ensemble.

## 10.6 Examiner les processus responsables des entrées-sorties

```bash
pidstat -d 1 5
```

La sortie peut aider à identifier les processus qui génèrent une activité d'entrée-sortie.

Cependant, toutes les interactions avec le stockage ne sont pas nécessairement imputées de façon simple au processus attendu. Les caches, les opérations différées et les couches système compliquent parfois l'attribution.

## 10.7 Comprendre les entrées-sorties synchrones et asynchrones

Une application peut soumettre une opération et attendre son résultat avant de continuer.

D'autres modèles permettent de traiter plusieurs opérations en parallèle ou de poursuivre d'autres tâches pendant une attente.

Le choix du modèle influence :

- Le nombre d'opérations en vol.
- La latence observée.
- Le débit atteignable.
- Le coût CPU.
- La complexité du programme.

Un modèle plus parallèle n'est pas nécessairement meilleur dans tous les cas.

## 10.8 Tester un stockage sans détruire les données

`fio` est un outil courant de benchmark des entrées-sorties.

**Règle de sécurité :** les exercices doivent utiliser un fichier de test dans un répertoire contrôlé. N'utilisez pas un périphérique bloc réel comme cible sans plan d'essai explicite et validation du périphérique.

Exemple de test limité à un fichier :

```bash
fio \
  --name=lab-sequentiel \
  --filename="$HOME/fio-test.bin" \
  --size=256M \
  --rw=write \
  --bs=1M \
  --ioengine=sync \
  --iodepth=1 \
  --direct=0 \
  --numjobs=1 \
  --runtime=10 \
  --time_based
```

Cette commande demande un test de fichier avec un workload séquentiel et une durée cible. Le comportement exact dépend de la version de fio et de ses paramètres.

Elle écrit réellement dans un fichier de test et peut consommer de l'espace et de l'activité d'entrée-sortie. Choisissez un emplacement disposant de suffisamment d'espace et utilisez une machine de laboratoire.

Pour examiner un workload de lecture, créez d'abord un fichier de test approprié, vérifiez son contenu, puis adaptez les paramètres sans pointer vers des données importantes.

## 10.9 Interpréter un benchmark

Un résultat de benchmark n'a de sens que par rapport au workload qu'il représente.

Considérez :

- Taille des opérations.
- Lecture ou écriture.
- Séquentiel ou aléatoire.
- Profondeur de file.
- Nombre de jobs.
- Cache utilisé ou contourné.
- Durée et répétitions.
- État du système.
- Autres utilisateurs du stockage.

Il ne faut pas comparer directement deux résultats issus de paramètres différents sans tenir compte des différences.

## 10.10 Examiner les erreurs du noyau

Pour rechercher certains messages liés au stockage :

```bash
journalctl -k | grep -i -E 'I/O error|timeout|reset|nvme|scsi'
```

Cette recherche est indicative. Les messages réels dépendent des pilotes, du matériel et de la version du noyau.

Un message de timeout ou de réinitialisation doit être replacé dans son contexte : il peut concerner un chemin de stockage, un périphérique, un contrôleur ou une autre couche.

## 10.11 Atelier de stockage

Dans un environnement de test :

1. Examinez `lsblk -f`.
2. Examinez `df -h` et `df -i`.
3. Comparez les résultats de `df` et `du` pour un répertoire de travail.
4. Examinez `iostat` si l'outil est disponible.
5. Identifiez l'outil nécessaire pour un benchmark fichier.
6. Effectuez un test de fichier de taille limitée.
7. Examinez débit et latence.
8. Répétez avec un paramètre différent.
9. Expliquez les différences et les limites du test.


# 11. Diagnostic avancé du réseau Linux

Les performances réseau dépendent de la carte réseau, des interruptions, des files, de la pile TCP/IP, des sockets, du routage et du traitement applicatif.

Une bonne analyse suit le chemin du paquet plutôt que de conclure à partir d'un simple `ping`.

## 11.1 Chemin simplifié d'un paquet entrant

```text
+--------------------------------+
| CABLE / RESEAU / SUPPORT RADIO |
+--------------------------------+
                |
                v
+--------------------------------+
| Carte reseau et pilote         |
+--------------------------------+
                |
                v
+--------------------------------+
| Reception et traitement noyau  |
| Interruptions, NAPI, softirq    |
+--------------------------------+
                |
                v
+--------------------------------+
| Pile reseau Linux              |
| IP, TCP/UDP, filtrage            |
+--------------------------------+
                |
                v
+--------------------------------+
| Socket                         |
+--------------------------------+
                |
                v
+--------------------------------+
| Application                    |
+--------------------------------+
```

Le détail dépend de la technologie réseau, du pilote et de la configuration.

## 11.2 Examiner les interfaces

```bash
ip -s link
```

Cette commande affiche les interfaces et des statistiques de trafic.

Recherchez notamment :

- Les paquets reçus et transmis.
- Les octets reçus et transmis.
- Les erreurs.
- Les abandons de paquets.

Un compteur élevé peut être normal sur une interface très sollicitée. Il faut examiner les variations dans le temps et le rapport au volume de trafic.

## 11.3 Examiner les statistiques du pilote

Si `ethtool` est disponible :

```bash
ethtool -S eth0
```

Remplacez `eth0` par le nom réel de votre interface.

Cette commande demande des statistiques spécifiques au pilote. Les noms et définitions des compteurs dépendent du matériel et du pilote.

Certains compteurs peuvent être difficiles à interpréter sans documentation du constructeur.

## 11.4 Examinateur des sockets

```bash
ss -s
```

Affiche une synthèse des sockets.

Pour examiner les connexions TCP :

```bash
ss -tan
```

Pour examiner les sockets en écoute TCP :

```bash
ss -tln
```

Pour examiner davantage d'informations de processus lorsqu'elles sont accessibles :

```bash
ss -tunap
```

Les informations de processus et les détails affichés dépendent des permissions et des options.

## 11.5 Examiner les retransmissions TCP

Les retransmissions peuvent signaler des pertes ou des situations qui provoquent des réémissions.

Si la commande est disponible :

```bash
nstat
```

Elle affiche différentes statistiques réseau du noyau.

Les noms des compteurs et leur disponibilité dépendent de la version.

Il faut examiner les variations sur une période donnée plutôt que de conclure uniquement à partir d'un total cumulé.

## 11.6 Latence, pertes et débit

Ces mesures ne sont pas équivalentes.

**Latence :** durée d'un échange ou d'une opération.

**Pertes :** paquets ou opérations qui n'atteignent pas le résultat attendu dans les conditions observées.

**Débit :** quantité de données transférées par unité de temps.

Une application peut souffrir d'une latence élevée tout en utilisant une faible bande passante.

Une connexion peut présenter un bon débit moyen mais des pics de latence qui dégradent les requêtes courtes.

## 11.7 Examiner le traitement CPU réseau

Lorsque le trafic est important, le temps CPU peut être consacré à :

- La réception des paquets.
- Le traitement de la pile réseau.
- Le filtrage.
- Le chiffrement.
- La gestion des sockets.
- La copie de données.
- Le traitement applicatif.

Des statistiques CPU peuvent montrer une activité élevée en interruptions ou en softirqs.

Des outils comme `mpstat`, `top`, `perf` et des compteurs réseau peuvent aider à établir la relation entre trafic et CPU.

## 11.8 Offloads réseau

Certaines cartes réseau et certains pilotes prennent en charge des mécanismes d'offload.

Ils peuvent notamment décharger certaines opérations liées aux paquets ou aux calculs.

Les mécanismes et les possibilités dépendent du matériel, du pilote et de la configuration.

Modifier les offloads sans mesure peut réduire les performances ou compliquer l'interprétation des captures.

## 11.9 Files réseau et qdisc

Linux propose des mécanismes de mise en file et de discipline de trafic.

Examiner les disciplines de file d'une interface :

```bash
tc qdisc show
```

Cette commande permet de consulter les disciplines actuellement configurées.

La gestion de trafic peut influencer la latence et la répartition du débit.

Ne modifiez pas la qdisc d'une interface de production sans comprendre la politique existante, les dépendances et les effets attendus.

## 11.10 Réseau et performance applicative

Une opération applicative peut être décomposée comme suit :

```text
Requete recue
     |
     v
Traitement CPU
     |
     v
Acces a des donnees
     |
     v
Appel externe ou requete reseau
     |
     v
Attente de reponse
     |
     v
Traitement final
     |
     v
Reponse envoyee
```

Si le temps de réponse est élevé, le problème peut provenir d'une étape précise. Une mesure globale du réseau ne permet pas nécessairement d'identifier cette étape.

Pour une analyse avancée, il faut rapprocher la durée des opérations de l'application des métriques du noyau.


# 12. Pressure Stall Information — PSI

PSI est une interface de mesure de la pression des ressources dans Linux.

Elle est particulièrement utile pour comprendre quand des tâches perdent du temps à attendre des ressources telles que le CPU, la mémoire ou les entrées-sorties.

## 12.1 Pourquoi PSI est important

Une consommation élevée ne suffit pas toujours à prouver qu'une ressource provoque une dégradation.

PSI fournit une approche centrée sur les périodes pendant lesquelles les tâches sont bloquées ou ralenties par une pression de ressources.

Les fichiers disponibles peuvent se trouver sous :

```text
/proc/pressure/cpu
/proc/pressure/memory
/proc/pressure/io
```

La disponibilité dépend du noyau, de sa configuration et de l'environnement.

## 12.2 Examiner la pression CPU

```bash
cat /proc/pressure/cpu
```

Exemple illustratif :

```text
some avg10=5.25 avg60=3.10 avg300=1.80 total=1234567
```

Les valeurs sont fictives.

`some` indique ici la part de temps où au moins certaines tâches non inactives subissent une attente de CPU, selon la définition de PSI.

Une valeur élevée peut signaler que des tâches ne reçoivent pas le temps CPU qu'elles souhaiteraient obtenir.

Il faut tenir compte de la charge, des cgroups, du nombre de CPU disponibles et du type de workload.

## 12.3 Examiner la pression mémoire

```bash
cat /proc/pressure/memory
```

L'interface fournit des statistiques permettant de comprendre certaines périodes d'attente associées à la pression mémoire.

Les lignes `some` et `full` n'ont pas la même signification.

Une pression mémoire importante doit être rapprochée :

- Des statistiques de mémoire.
- Des défauts de page.
- Du swap.
- Des événements OOM.
- Des limites de cgroups.
- Des temps de réponse.

## 12.4 Examiner la pression d'entrées-sorties

```bash
cat /proc/pressure/io
```

Ces statistiques permettent d'évaluer les périodes pendant lesquelles des tâches subissent une attente associée aux entrées-sorties.

Une pression I/O importante peut être liée à diverses situations :

- Latence du stockage.
- Forte concurrence.
- Écriture différée.
- Accès synchrones.
- Problème matériel.
- Comportement applicatif.

PSI ne donne pas automatiquement la cause exacte. Il identifie un effet sur la progression des tâches.

## 12.5 Distinguer pression et utilisation

Considérez deux systèmes fictifs :

| Mesure | Système A | Système B |
|---|---:|---:|
| Utilisation CPU moyenne | 90 % | 45 % |
| Pression CPU | Faible | Élevée |
| Latence applicative | Faible | Élevée |

Le système A peut exécuter efficacement une charge intensive, tandis que le système B peut souffrir de concurrence, de limites CPU ou d'une charge mal répartie.

La combinaison des mesures est plus informative que le seul pourcentage CPU.

## 12.6 Examiner PSI en continu

Une lecture ponctuelle fournit un instantané.

Pour suivre les valeurs :

```bash
watch -n 1 cat /proc/pressure/memory
```

Cette commande utilise `watch`, si l'outil est disponible, pour afficher régulièrement le fichier.

Une collecte de surveillance professionnelle doit tenir compte des intervalles, de la conservation des mesures et du coût de l'observation.

## 12.7 PSI et cgroups

PSI peut être disponible à une échelle plus fine pour certains cgroups.

Cela aide à distinguer une pression affectant un conteneur de celle qui concerne l'hôte entier.

Le chemin exact doit être identifié à partir de la hiérarchie cgroups et des fichiers présents.

Il ne faut pas supposer que tous les systèmes exposent les mêmes fichiers au même emplacement.


# 13. cgroups v2 et isolation des ressources

Les cgroups, ou *control groups*, permettent d'organiser des processus en groupes auxquels des ressources et des limites peuvent être associées.

Ils sont particulièrement importants pour les conteneurs, les services systemd et les environnements mutualisés.

## 13.1 Pourquoi les cgroups sont-ils nécessaires ?

Sur un serveur partagé, l'utilisation des ressources par un service peut affecter d'autres applications.

Les cgroups permettent notamment de contrôler ou de comptabiliser des ressources comme :

- CPU.
- Mémoire.
- Entrées-sorties.
- Nombre de processus.
- Certaines autres ressources selon la configuration.

### Schéma conceptuel

```text
+--------------------------------------+
| Hote Linux                           |
|                                      |
| Ressources CPU / RAM / I/O           |
+--------------------------------------+
                   |
                   v
+--------------------------------------+
| Hierarchie cgroups                   |
+--------------------------------------+
         |                    |
         v                    v
+----------------+   +----------------+
| Service A      |   | Service B      |
| CPU, memoire   |   | CPU, memoire   |
+----------------+   +----------------+
```

L'isolation exacte dépend des contrôleurs activés et de la configuration.

## 13.2 cgroups v1 et v2

Il existe plusieurs générations de cgroups.

cgroups v2 fournit une hiérarchie unifiée dont l'organisation diffère de celle de cgroups v1.

Les services systemd et les conteneurs peuvent utiliser cgroups pour appliquer des limites.

Pour vérifier le type de système de fichiers associé à la hiérarchie unifiée :

```bash
findmnt -t cgroup2
```

Sur un système utilisant cgroups v2, il est courant de trouver une hiérarchie montée sous `/sys/fs/cgroup`, mais l'emplacement et l'organisation réels doivent être vérifiés.

## 13.3 Examiner la hiérarchie

```bash
ls -la /sys/fs/cgroup
```

Les fichiers disponibles dépendent des contrôleurs activés.

Dans un environnement cgroups v2, on peut notamment rencontrer :

```text
cpu.max
cpu.stat
memory.current
memory.max
memory.events
io.stat
pids.current
pids.max
```

Tous les fichiers ne sont pas présents dans tous les cgroups.

## 13.4 Comprendre `cpu.max`

Dans cgroups v2, `cpu.max` peut définir une limite de temps CPU sur une période.

Sa structure habituelle contient deux valeurs :

```text
quota periode
```

Par exemple, une configuration fictive :

```text
50000 100000
```

représente un quota de 50 000 microsecondes sur une période de 100 000 microsecondes.

Sous les conditions prévues par le contrôleur, cela correspond à un budget CPU équivalent à environ un demi-CPU sur la période. La répartition réelle et les effets observés dépendent des tâches, de la configuration et du reste du système.

La valeur `max` à la place du quota indique généralement qu'il n'y a pas de quota CPU explicite à ce niveau.

## 13.5 Pourquoi un conteneur peut être limité avec un CPU disponible ?

Supposons que l'hôte dispose de huit CPU logiques, mais qu'un conteneur soit limité par un quota correspondant à un CPU.

Le conteneur peut atteindre son budget avant la fin de la période de contrôle et être ralenti, même si d'autres CPU de l'hôte sont peu utilisés.

Les limites héritées des cgroups parents peuvent également avoir un effet.

Le diagnostic doit donc examiner la hiérarchie complète, et non seulement les métriques globales de l'hôte.

## 13.6 Examiner `cpu.stat`

```bash
cat /sys/fs/cgroup/cpu.stat
```

Dans un cgroup concerné, le fichier peut contenir des statistiques telles que le temps CPU consommé et des événements de limitation, selon le contrôleur et le noyau.

Pour interpréter les écarts, comparez plusieurs échantillons dans une fenêtre de temps connue.

Une valeur cumulée seule ne mesure pas directement la pression instantanée.

## 13.7 Comprendre `memory.current`

Le fichier `memory.current`, dans cgroups v2, expose l'utilisation mémoire comptabilisée pour le cgroup concerné, selon les règles de comptabilisation du contrôleur.

```bash
cat /sys/fs/cgroup/memory.current
```

Cette commande ne doit pas être supposée fournir automatiquement l'utilisation d'un conteneur arbitraire. Il faut être placé dans le bon cgroup ou lire son chemin exact.

## 13.8 Comprendre `memory.max`

```bash
cat /sys/fs/cgroup/memory.max
```

Le fichier indique la limite mémoire du cgroup concerné, selon les règles du contrôleur.

Une valeur `max` est utilisée pour représenter l'absence de cette limite explicite à ce niveau.

Les limites héritées des parents et les autres ressources peuvent néanmoins s'appliquer.

## 13.9 Examiner `memory.events`

```bash
cat /sys/fs/cgroup/memory.events
```

Ce fichier peut exposer des compteurs d'événements liés à la pression et aux limites mémoire, notamment ceux définis par cgroups v2.

Un compteur cumulatif doit être analysé à travers des différences temporelles.

Il faut également examiner les journaux, le cgroup exact et le comportement de l'application.

## 13.10 Contrôler l'I/O avec les cgroups

Selon les possibilités du système :

```bash
cat /sys/fs/cgroup/io.stat
```

Ce fichier peut fournir des statistiques d'entrées-sorties pour les périphériques comptabilisés par le contrôleur.

Une politique de limitation I/O peut influencer la latence et le débit d'une application.

Il faut vérifier le cgroup effectif, les limites du parent et le matériel utilisé.

## 13.11 cgroups et systemd

Les services systemd peuvent être associés à des cgroups.

L'état et les propriétés d'une unité peuvent être examinés avec les commandes de systemd.

Pour inspecter certaines propriétés :

```bash
systemctl show nom-du-service
```

La sortie est volumineuse. Il est possible d'utiliser des propriétés ciblées adaptées à l'unité.

La configuration des limites doit suivre une procédure documentée, avec une mesure initiale et une validation après changement.


# 14. Namespaces, conteneurs et frontières de ressources

Les namespaces et les cgroups sont deux mécanismes différents qui participent à l'isolation des processus.

Un conteneur peut utiliser les deux.

## 14.1 Rôle des namespaces

Les namespaces offrent des vues isolées de certaines ressources ou objets du système.

Parmi les catégories courantes :

- PID : visibilité des identifiants de processus.
- Network : interfaces et ressources réseau isolées.
- Mount : vue des montages.
- UTS : nom d'hôte et domaine NIS dans le contexte concerné.
- IPC : mécanismes IPC.
- User : identifiants utilisateurs et groupes associés au namespace.
- Cgroup : vue de la hiérarchie cgroups selon les mécanismes concernés.
- Time : certains aspects de l'espace temporel dans les versions qui le prennent en charge.

La disponibilité et les détails dépendent du noyau et des fonctionnalités activées.

## 14.2 Rôle des cgroups

Les cgroups servent surtout à organiser les processus et à comptabiliser ou contrôler leurs ressources.

### Comparaison

| Mécanisme | Fonction principale |
|---|---|
| Namespaces | Isoler la visibilité de certaines ressources et identités |
| cgroups | Comptabiliser et contrôler des ressources |
| Permissions Unix | Contrôler certains accès aux fichiers et ressources |
| Capabilities | Séparer certains privilèges administratifs |
| Seccomp | Restreindre certains appels système |
| LSM | Appliquer des politiques de sécurité selon le module utilisé |

Ces mécanismes se complètent.

## 14.3 Comprendre les PID namespaces

Dans un namespace PID, les processus peuvent observer une vue des identifiants différente de celle de l'hôte.

Un processus peut donc posséder un identifiant visible depuis le conteneur qui ne correspond pas directement à l'identifiant observé depuis l'hôte.

C'est important lors du diagnostic d'un conteneur. Il faut savoir depuis quel namespace on observe le processus.

## 14.4 Comprendre les namespaces réseau

Un namespace réseau peut fournir une vue isolée des interfaces, des routes, de certaines règles réseau et des sockets.

Une application dans un conteneur ne voit donc pas nécessairement les mêmes interfaces que l'hôte.

Il faut distinguer :

- Les interfaces du conteneur.
- Les interfaces de l'hôte.
- Les ponts ou autres mécanismes de connexion.
- Les routes.
- Le filtrage.
- Les interfaces virtuelles.
- Les règles appliquées à chaque niveau.

## 14.5 Limites d'une isolation par conteneur

Un conteneur n'est pas simplement une petite machine virtuelle.

Les processus du conteneur partagent le noyau de l'hôte, même lorsqu'ils disposent de vues isolées de certaines ressources.

Une modification d'un paramètre système peut donc avoir des conséquences sur plusieurs applications.

Dans un environnement mutualisé, il est essentiel de distinguer les paramètres propres à un conteneur des paramètres globaux du noyau.


# 15. Tracing du noyau avec ftrace et tracepoints

Le traçage permet d'observer le comportement du noyau plus finement que les compteurs globaux.

Il est particulièrement utile lorsque les outils de haut niveau ne suffisent pas à expliquer un phénomène.

## 15.1 Profilage ou traçage ?

Le profilage d'échantillonnage observe le système à certains moments et construit une approximation des activités dominantes.

Le traçage enregistre des événements ou des transitions répondant à un mécanisme donné.

Un traçage détaillé peut offrir une chronologie précise, mais il peut aussi générer beaucoup de données et modifier le comportement observé.

Il faut choisir la granularité en fonction de la question.

## 15.2 ftrace

ftrace est une infrastructure de traçage du noyau Linux.

Elle permet de surveiller certains événements et certaines fonctions selon les fonctionnalités disponibles.

L'interface de traçage est souvent exposée dans tracefs, fréquemment monté sous :

```text
/sys/kernel/tracing
```

Des configurations historiques ou spécifiques peuvent utiliser un autre chemin, notamment `/sys/kernel/debug/tracing`.

Vérifiez l'emplacement réel avant d'utiliser les fichiers.

## 15.3 Vérifier le système de fichiers de traçage

```bash
findmnt -t tracefs
```

Puis, si l'arborescence est accessible :

```bash
ls /sys/kernel/tracing
```

L'accès en lecture et en écriture peut être restreint.

Certaines opérations de traçage peuvent consommer des ressources et exposer des détails internes. Elles ne doivent pas être laissées actives sans nécessité.

## 15.4 Examiner les tracepoints disponibles

Les événements disponibles dépendent de la version et de la configuration.

Lorsque l'interface est accessible :

```bash
cat /sys/kernel/tracing/available_events
```

La liste peut être longue.

Elle peut présenter des événements provenant de sous-systèmes tels que :

- Scheduler.
- Entrées-sorties.
- Mémoire.
- Réseau.
- Appels système.
- Pilotes.
- Gestion de l'énergie.

Il faut identifier l'événement le plus pertinent au lieu de tracer toutes les activités disponibles.

## 15.5 Pourquoi les tracepoints sont-ils utiles ?

Un tracepoint correspond à un point d'observation instrumenté dans le code concerné.

Il peut permettre de collecter des données structurées sur des événements connus.

Par exemple, les événements de scheduler peuvent aider à analyser des transitions de tâches. Les événements de stockage peuvent aider à étudier les entrées-sorties, selon les tracepoints disponibles.

La documentation de l'événement reste indispensable pour comprendre les champs fournis.

## 15.6 `trace-cmd`

`trace-cmd` est un outil utilisé pour interagir avec le système de traçage lorsqu'il est disponible.

Il peut permettre de sélectionner des événements, de collecter des traces et d'examiner les résultats.

Sa disponibilité dépend de la distribution.

La syntaxe et les possibilités doivent être vérifiées dans la documentation installée :

```bash
man trace-cmd
```

N'activez pas une collecte globale très détaillée sur un serveur sensible sans comprendre son coût et le volume de données attendu.

## 15.7 Comprendre l'impact du tracing

Le coût du traçage dépend :

- Du nombre d'événements.
- De leur fréquence.
- Du nombre de champs collectés.
- De la quantité de données.
- Du matériel.
- De la configuration.
- Du volume d'écriture et d'analyse des traces.

Une trace peut provoquer une surcharge importante lorsqu'elle enregistre des événements très fréquents.

Pour réduire l'impact :

1. Choisissez un événement précis.
2. Limitez la durée.
3. Limitez le périmètre lorsque l'outil le permet.
4. Évaluez le volume de sortie.
5. Comparez avec une mesure sans tracing.
6. Désactivez la collecte après l'expérience.

## 15.8 Référence officielle

La documentation du noyau consacre un guide à ses mécanismes de traçage :

https://docs.kernel.org/trace/

Elle présente notamment ftrace, les tracepoints, kprobes, fprobes et les mécanismes associés.


# 16. Introduction au traçage eBPF

eBPF désigne un ensemble de mécanismes du noyau permettant de charger et d'exécuter des programmes vérifiés dans des contextes prévus par le système.

Il est utilisé dans des domaines comme l'observabilité, le réseau, la sécurité et l'analyse des performances.

## 16.1 Pourquoi eBPF est-il utile ?

eBPF peut permettre de collecter des informations ciblées avec une granularité élevée.

Selon le programme, le point d'attachement et les capacités disponibles, il peut contribuer à observer :

- Des appels système.
- Des événements réseau.
- Des activités de scheduler.
- Des événements de fichiers.
- Certaines latences d'opérations.
- Des événements de sécurité.

La disponibilité dépend du noyau, de la configuration, des permissions et des outils.

## 16.2 Schéma d'un programme eBPF

```text
+-----------------------------------+
| Application ou outil d'observation|
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Chargement du programme eBPF      |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Verification des contraintes      |
| du programme                      |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Point d'attachement               |
| Tracepoint, kprobe, autre          |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Execution encadree dans le noyau  |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Donnees collectees                |
+-----------------------------------+
                  |
                  v
+-----------------------------------+
| Analyse en espace utilisateur     |
+-----------------------------------+
```

Ce schéma est conceptuel. Tous les programmes eBPF n'utilisent pas nécessairement les mêmes types de points d'attachement ou les mêmes interfaces de collecte.

## 16.3 L'importance du vérificateur

Avant l'exécution, le noyau utilise un vérificateur pour examiner le programme eBPF et imposer les contraintes prévues par son modèle d'exécution.

Ce contrôle ne constitue pas une garantie générale que le programme est utile, non intrusif ou exempt de défauts logiques.

Le concepteur reste responsable du choix des événements, de la quantité de données et de l'interprétation des résultats.

## 16.4 Outils utilisant eBPF

Selon l'environnement, on peut rencontrer :

- `bpftrace`
- BCC
- Des outils fondés sur libbpf
- Des outils d'observabilité construits autour d'eBPF

Leurs dépendances et capacités peuvent varier selon le noyau et les paquets installés.

Il faut consulter la documentation associée à la version installée.

## 16.5 Exemple conceptuel de traçage d'événement

Un outil eBPF peut compter certains événements par processus ou par nom de commande.

Ce type de collecte peut aider à répondre à une question telle que :

> Quel processus déclenche le plus fréquemment une opération observée pendant la fenêtre étudiée ?

Mais un nombre élevé d'événements ne signifie pas nécessairement qu'une opération est coûteuse. Il faut aussi mesurer sa durée, son contexte et son importance dans le workload.

## 16.6 Contrôler les privilèges

Le chargement et l'utilisation d'eBPF peuvent nécessiter des permissions importantes.

N'accordez pas des capacités privilégiées à un utilisateur ou à un binaire sans comprendre le périmètre d'accès obtenu.

Les programmes de traçage peuvent exposer des informations sensibles provenant de processus ou de l'activité du système.

## 16.7 eBPF et ftrace

Ces approches se recoupent dans certains usages mais ne sont pas identiques.

| Critère | ftrace / tracepoints | eBPF |
|---|---|---|
| Objectif | Tracer certains comportements du noyau | Exécuter des programmes d'observation ou d'autres usages permis |
| Flexibilité | Dépend des fonctions de traçage disponibles | Dépend des programmes, hooks et helpers autorisés |
| Collecte | Peut produire des événements de trace | Peut agréger ou filtrer des événements selon le programme |
| Préparation | Outils de tracing et tracefs selon le scénario | Outils, bibliothèques et support eBPF |
| Coût | Dépend de la densité des événements | Dépend du programme, du point d'attachement et du volume traité |

Le choix doit se faire à partir de la question à résoudre, des possibilités du système et du coût de collecte.


# 17. Modules, paramètres et démarrage du noyau

Les modules et paramètres permettent d'adapter le noyau à du matériel et à des fonctionnalités spécifiques.

Ils doivent être administrés avec précaution car certaines modifications affectent directement le fonctionnement global du système.

## 17.1 Examiner les modules chargés

```bash
lsmod
```

La commande affiche les modules du noyau actuellement chargés, selon les informations disponibles.

Pour examiner un module particulier :

```bash
modinfo nom_du_module
```

Remplacez le nom par celui d'un module réellement présent.

`modinfo` peut afficher des renseignements comme la description, la version, les dépendances ou les paramètres exposés par le module.

## 17.2 Examiner les messages du noyau

```bash
dmesg
```

Affiche les messages du tampon du noyau, selon les permissions et la configuration.

Pour consulter des messages plus récents :

```bash
dmesg --ctime | tail -n 100
```

Cette forme dépend des options disponibles dans l'outil.

Autre méthode, si le noyau et la journalisation le permettent :

```bash
journalctl -k
```

La sortie peut contenir des informations sur les pilotes, les périphériques, les événements de mémoire et d'autres sous-systèmes.

## 17.3 Comprendre les modules

Les modules permettent notamment d'ajouter certaines fonctionnalités sans intégrer nécessairement tout le code au noyau principal.

Un module peut être :

- Un pilote.
- Un composant de système de fichiers.
- Un composant réseau.
- Une fonctionnalité de sécurité.
- Un autre élément prévu pour le chargement modulaire.

Le retrait d'un module peut être impossible lorsque le module est utilisé. Il peut aussi avoir des conséquences sur les périphériques ou services concernés.

Ne retirez pas un module système par simple curiosité sur une machine importante.

## 17.4 Paramètres du noyau avec sysctl

`sysctl` permet de consulter ou modifier certains paramètres exposés par le noyau.

Afficher tous les paramètres disponibles :

```bash
sysctl -a
```

Cette sortie peut être très volumineuse.

Examiner un paramètre précis :

```bash
sysctl net.ipv4.ip_forward
```

Le paramètre est présenté comme exemple. Sa valeur dépend de la configuration.

## 17.5 Modification temporaire et persistance

Une modification appliquée avec `sysctl -w` peut changer un paramètre pendant le fonctionnement courant.

Exemple de syntaxe :

```bash
sudo sysctl -w nom.parametre=valeur
```

N'utilisez cette forme qu'après avoir compris la signification et les conséquences du paramètre choisi.

Pour rendre des paramètres persistants, les distributions utilisent souvent des fichiers sous `/etc/sysctl.conf` ou `/etc/sysctl.d/`.

La priorité et la manière de charger ces fichiers peuvent varier. Consultez la documentation de votre système.

## 17.6 Pourquoi éviter les recettes universelles de tuning ?

Un paramètre utile pour un workload peut dégrader un autre workload.

Les résultats dépendent notamment :

- Du noyau.
- Du matériel.
- Des ressources disponibles.
- De la charge applicative.
- Des limites de conteneur.
- De la configuration réseau.
- Des contraintes de latence.
- De la sécurité.

Une modification de paramètre doit être accompagnée d'une hypothèse vérifiable et d'une procédure de retour arrière.

## 17.7 Commande de démarrage

```bash
cat /proc/cmdline
```

Cette commande affiche les paramètres de la ligne de commande du noyau au démarrage.

Certaines options peuvent modifier le comportement du noyau, de pilotes ou de mécanismes de démarrage.

Ne changez pas une option de démarrage sans comprendre ses effets et sans conserver une méthode de retour arrière.

## 17.8 Panic et oops du noyau

Une erreur noyau peut provoquer différents symptômes, notamment une trace d'erreur ou une panique dans les cas graves.

Pour examiner les informations disponibles :

```bash
journalctl -k -b
```

Si la machine a redémarré après un incident, examinez également les journaux persistants ou les mécanismes de collecte des rapports lorsqu'ils sont configurés.

Les informations disponibles dépendent de la configuration et de la persistance des journaux.

Un message d'erreur noyau doit être interprété avec le contexte matériel, la version du noyau, les pilotes et la chronologie.


# 18. Synchronisation, verrous et problèmes de concurrence

Une application multithread peut consommer peu de CPU tout en présentant de mauvaises performances.

Un thread peut attendre un verrou, une condition, une ressource ou un autre thread.

L'analyse doit donc examiner non seulement le travail exécuté, mais aussi les périodes pendant lesquelles le travail ne progresse pas.

## 18.1 Pourquoi les verrous existent-ils ?

Les verrous protègent certaines données partagées contre des accès concurrents incompatibles.

Ils peuvent être nécessaires pour préserver la cohérence des données.

Cependant, un verrou utilisé trop fréquemment ou conservé trop longtemps peut limiter le parallélisme.

### Schéma

```text
+---------------------------+
| Thread A                  |
| obtient le verrou         |
+---------------------------+
             |
             v
+---------------------------+
| Section critique          |
| acces aux donnees partagees|
+---------------------------+
             |
             v
+---------------------------+
| Thread A libere le verrou |
+---------------------------+
       |              |
       v              v
+-------------+  +-------------+
| Thread B    |  | Thread C    |
| peut avancer|  | peut avancer|
+-------------+  +-------------+
```

Dans ce schéma, les threads en attente d'un verrou ne progressent pas dans la section critique tant que les conditions d'accès ne le permettent pas.

## 18.2 Contention

La contention se produit lorsque plusieurs threads souhaitent accéder à une ressource ou à une section protégée.

Elle peut entraîner :

- Attente.
- Commutations de contexte.
- Réveils inutiles.
- Coût de synchronisation.
- Réduction du parallélisme.
- Latence variable.

Ajouter des threads peut augmenter la contention plutôt que le débit.

## 18.3 Examiner le temps hors CPU

Un profil CPU classique met surtout en évidence les parties qui consomment du CPU pendant la collecte.

Il peut ne pas expliquer directement le temps passé à attendre des événements.

Le diagnostic hors CPU cherche à comprendre ce que les threads font ou attendent lorsqu'ils ne sont pas en train d'exécuter du code sur le CPU.

Les outils nécessaires dépendent du noyau, des événements disponibles et du type de programme.

## 18.4 Distinguer attente réseau, I/O et verrou

Un thread qui attend peut être endormi pour des raisons différentes.

Un diagnostic doit examiner :

- Les appels système.
- Les événements associés.
- La pile du thread.
- Les ressources utilisées.
- Les journaux applicatifs.
- Les relations entre threads.

Il faut éviter d'inférer automatiquement qu'un thread endormi est bloqué sur un verrou.

## 18.5 Interpréter les traces de piles

Les informations de pile aident à reconstruire le chemin ayant conduit à une attente ou à une opération.

La collecte et l'interprétation dépendent notamment :

- Des symboles.
- De l'architecture.
- De la méthode de collecte.
- Des données disponibles.
- Du niveau d'optimisation du programme.

Une pile partielle peut ne pas montrer toute l'origine du problème.

## 18.6 Pourquoi les optimisations de concurrence sont délicates

Des modifications comme :

- Augmenter le nombre de threads.
- Réduire le nombre de verrous.
- Changer la granularité des tâches.
- Modifier une politique d'affinité.
- Introduire une file asynchrone.

peuvent changer les résultats de plusieurs façons.

Elles doivent être testées avec une charge représentative, en suivant la correction fonctionnelle, le débit, la latence et l'utilisation des ressources.


# 19. Optimisation raisonnée des performances

L'optimisation doit cibler le mécanisme démontré comme limitant, et pas seulement modifier des paramètres visibles.

## 19.1 Définir le résultat attendu

Avant l'optimisation, choisissez l'indicateur qui représente le besoin.

Exemples :

- Réduire la latence p99.
- Augmenter le débit.
- Réduire la consommation CPU par requête.
- Diminuer le taux d'erreur.
- Réduire le temps de restauration.
- Maintenir une latence stable sous une charge connue.

Les métriques doivent être cohérentes avec l'objectif de service.

## 19.2 Latence moyenne et percentiles

La moyenne peut masquer une petite proportion de requêtes très lentes.

Les percentiles servent à examiner la distribution des durées.

Exemple fictif :

| Mesure | Avant | Après |
|---|---:|---:|
| Latence médiane p50 | 30 ms | 29 ms |
| Latence p95 | 95 ms | 58 ms |
| Latence p99 | 310 ms | 90 ms |
| Débit | 2 000 req/s | 2 050 req/s |
| Erreurs | 0,2 % | 0,2 % |

Ces valeurs sont illustratives. Elles montrent qu'une amélioration des percentiles élevés peut être plus importante pour certains usages qu'une faible évolution de la moyenne.

## 19.3 Éviter l'optimisation sans objectif

Une commande ou un réglage ne devient pas une optimisation simplement parce qu'il est populaire.

Une pratique professionnelle exige :

1. Une charge représentative.
2. Une métrique cible.
3. Une mesure initiale.
4. Une hypothèse.
5. Un changement limité.
6. Une comparaison.
7. Un contrôle des effets secondaires.

## 19.4 Le modèle du goulot d'étranglement

Dans une chaîne de traitement, la capacité globale peut être limitée par un composant.

### Exemple conceptuel

```text
Reception requete
       |
       v
+------------------+
| CPU              |
| Capacite elevee  |
+------------------+
       |
       v
+------------------+
| Base de donnees  |
| Capacite faible  |
+------------------+
       |
       v
+------------------+
| Reseau           |
| Capacite elevee  |
+------------------+
       |
       v
Reponse
```

Si la base de données limite le débit, augmenter la capacité du CPU peut ne pas améliorer sensiblement le débit global.

Cependant, les goulots d'étranglement peuvent être multiples ou se déplacer pendant l'optimisation.

## 19.5 Réduire le travail inutile

Les améliorations les plus efficaces viennent souvent de la réduction du travail qui n'est pas nécessaire.

Exemples :

- Éviter des appels réseau redondants.
- Réutiliser des connexions lorsqu'une architecture appropriée le permet.
- Réduire les copies.
- Éviter les requêtes répétées.
- Améliorer la localité mémoire.
- Réduire les réveils et la synchronisation inutile.
- Utiliser un algorithme plus adapté.

Les mécanismes noyau sont importants, mais une partie considérable des problèmes de performance provient du code applicatif ou de la manière dont il utilise le système.

## 19.6 Tuning de CPU

Une optimisation CPU peut viser :

- La réduction du travail exécuté.
- L'amélioration du parallélisme utile.
- La réduction du temps passé dans le noyau.
- L'amélioration de la localité.
- La réduction de la contention.
- Une meilleure répartition de la charge.

Changer l'affinité ou les priorités ne doit venir qu'après l'identification du problème.

## 19.7 Tuning de mémoire

Les axes possibles comprennent :

- Réduction de l'empreinte mémoire.
- Réduction des allocations inutiles.
- Correction des fuites.
- Contrôle du parallélisme.
- Optimisation des structures de données.
- Ajustement justifié des limites.
- Gestion adaptée des caches.

Modifier un paramètre de récupération mémoire sans comprendre la pression et la charge peut déplacer le problème plutôt que le résoudre.

## 19.8 Tuning du stockage

Les axes possibles comprennent :

- Réduction du nombre d'opérations.
- Regroupement des écritures lorsque c'est approprié.
- Réduction des synchronisations coûteuses.
- Adaptation de la taille des opérations.
- Utilisation correcte du cache.
- Évaluation de la concurrence.
- Choix d'un stockage adapté à la charge.

L'objectif doit être défini : débit, latence, durabilité ou compromis entre ces facteurs.

## 19.9 Tuning réseau

Les axes possibles comprennent :

- Réduction des échanges inutiles.
- Réutilisation de connexions.
- Réduction de la taille des données transmises.
- Correction des pertes.
- Ajustement du traitement applicatif.
- Réduction du coût du chiffrement lorsque le problème est démontré.
- Adaptation des files ou des offloads lorsque des mesures le justifient.

Il ne faut pas modifier les paramètres TCP ou les buffers réseau sans mesurer leur effet et comprendre les contraintes de la charge.

## 19.10 Le coût d'une optimisation

Une amélioration doit être évaluée dans son contexte.

Une configuration peut améliorer une application tout en dégradant :

- Une autre application.
- Le comportement sous forte charge.
- La stabilité.
- La consommation mémoire.
- La latence de queue.
- La disponibilité.
- La sécurité.

Le résultat final doit être validé sur l'ensemble des objectifs importants.


# 20. Méthodologie professionnelle de benchmark

Un benchmark sert à mesurer un comportement sous une charge donnée.

Il ne peut pas être interprété correctement si son contexte et ses paramètres ne sont pas connus.

## 20.1 Définir le workload

Documentez :

- L'application.
- Le type de requêtes.
- Le nombre de clients.
- Le débit attendu.
- La distribution des données.
- La taille des requêtes.
- Les paramètres de concurrence.
- Les dépendances externes.
- La durée du test.

Une charge trop simple peut ne pas représenter la production.

## 20.2 Établir une référence

Avant une optimisation, collectez les informations de base.

```text
Machine :
Distribution :
Noyau :
CPU :
Memoire :
Stockage :
Reseau :
Application :
Version :
Configuration :
Charge :
```

Cette fiche rend les mesures plus faciles à interpréter et à reproduire.

## 20.3 Répéter les mesures

Une seule mesure peut être influencée par :

- La chauffe du système.
- Le cache.
- Les tâches de fond.
- Les variations du réseau.
- La fréquence CPU.
- Les opérations de maintenance.
- Le comportement de l'ordonnanceur.

Répétez les tests et comparez les variations.

## 20.4 Comparer des configurations équivalentes

Pour comparer deux versions, conservez autant que possible les mêmes :

- Données.
- Requêtes.
- Paramètres de benchmark.
- Durées.
- Dépendances.
- Conditions de charge.
- Versions des outils.
- Conditions matérielles.

Toute différence doit être documentée.

## 20.5 Mesurer à plusieurs niveaux

Exemple d'analyse :

```text
Niveau application
    |
    v
Latence et taux d'erreur
    |
    v
Niveau processus
    |
    v
CPU, memoire et attente
    |
    v
Niveau noyau
    |
    v
Ordonnancement, PSI, appels systeme
    |
    v
Niveau materiel
    |
    v
CPU, RAM, stockage et interfaces
```

Le niveau le plus détaillé n'est pas toujours nécessaire. Une bonne analyse commence par l'indicateur le plus simple susceptible de répondre à la question.

## 20.6 Documenter une hypothèse

Exemple :

```text
Observation :
La latence p99 augmente de 120 ms a 450 ms.

Hypothese :
Une pression I/O augmente pendant les pics.

Prediction :
Les mesures PSI I/O et les statistiques de latence devraient
montrer une hausse qui coincide avec le probleme.

Test :
Collecte simultanee de la latence applicative, PSI et iostat.

Critere :
La correlation doit etre repetable sur plusieurs periodes.
```

Cette structure oblige à préciser ce qui confirmerait ou invaliderait l'hypothèse.

## 20.7 Éviter les benchmarks trompeurs

Ne comparez pas directement :

- Une lecture depuis un cache chaud avec une lecture depuis un cache froid.
- Deux tests de tailles différentes sans tenir compte de ce changement.
- Deux systèmes utilisant des paramètres de concurrence différents.
- Des résultats provenant de versions différentes sans documenter le contexte.
- Un benchmark de fichier avec un benchmark de périphérique bloc.
- Un système inactif avec un système qui traite d'autres charges.

Un chiffre n'est utile que si les conditions qui l'ont produit sont comprises.


# 21. Playbooks de diagnostic d'incidents

Cette section regroupe des méthodes de diagnostic par symptôme.

Chaque playbook suit un principe : observer, formuler une hypothèse, mesurer, puis corriger si les preuves le justifient.

## 21.1 Incident A — CPU élevé et application lente

### Étape 1 : confirmer le symptôme

```bash
uptime
mpstat -P ALL 1 5
```

Si `mpstat` est disponible, examinez l'activité CPU pendant plusieurs intervalles.

### Étape 2 : rechercher les processus dominants

```bash
ps -eo pid,ppid,user,%cpu,%mem,stat,comm --sort=-%cpu | head
```

### Étape 3 : examiner le profil

```bash
perf stat -- commande-de-test
```

Si la question exige de localiser les fonctions coûteuses et si `perf` est disponible :

```bash
perf record -g -- commande-de-test
perf report
```

### Étape 4 : interpréter

Questions :

- Le CPU est-il réellement saturé ?
- Le processus principal consomme-t-il l'essentiel du CPU ?
- Est-ce du travail utile ou une boucle répétitive ?
- La charge provient-elle de l'espace utilisateur ou du noyau ?
- Y a-t-il un goulot d'étranglement dans une fonction particulière ?
- Le service est-il limité par un cgroup ?

### Étape 5 : corriger

Choisissez une correction correspondant aux preuves.

Ne modifiez pas l'affinité CPU, les priorités ou les paramètres d'ordonnancement simplement parce que le CPU est élevé.


## 21.2 Incident B — RAM presque entièrement utilisée

### Étape 1 : examiner la mémoire globale

```bash
free -h
grep -E 'MemAvailable|SwapTotal|SwapFree' /proc/meminfo
```

### Étape 2 : examiner les processus

```bash
ps -eo pid,user,%mem,rss,comm --sort=-%mem | head
```

### Étape 3 : examiner le swap et les événements OOM

```bash
swapon --show
journalctl -k | grep -i -E 'oom|out of memory|killed process'
```

### Étape 4 : examiner PSI

```bash
cat /proc/pressure/memory
```

### Étape 5 : choisir une hypothèse

Causes possibles :

- Cache récupérable important.
- Charge mémoire normale.
- Fuite mémoire applicative.
- Working set trop volumineux.
- Limite mémoire d'un cgroup.
- Pression provoquant des accès au swap.
- OOM dans un conteneur.

### Étape 6 : corriger

La correction peut relever du code applicatif, de la configuration du conteneur, de la capacité physique ou de la stratégie de rétention.

Ne concluez pas que la mémoire doit être vidée ou que le swap doit être désactivé sans diagnostic.


## 21.3 Incident C — Temps de réponse élevé, CPU faible

Ce scénario indique que l'application peut passer beaucoup de temps à attendre.

### Étape 1 : observer le stockage

```bash
iostat -xz 1 5
```

### Étape 2 : observer les processus

```bash
pidstat -d 1 5
```

### Étape 3 : examiner PSI

```bash
cat /proc/pressure/io
```

### Étape 4 : examiner les appels système si nécessaire

```bash
strace -c commande-de-test
```

### Étape 5 : examiner les dépendances externes

Si le stockage ne semble pas expliquer la lenteur, examinez le réseau, les services distants, les verrous et les attentes applicatives.

### Étape 6 : corriger

La correction doit cibler le temps d'attente démontré. Ajouter du CPU n'améliorera pas nécessairement une opération dominée par l'attente.


## 21.4 Incident D — Conteneur limité en CPU

### Étape 1 : examiner la vue de l'hôte

```bash
uptime
mpstat -P ALL 1 5
```

### Étape 2 : identifier le cgroup du service

Utilisez les outils et les informations systemd ou conteneur disponibles pour trouver le cgroup exact.

### Étape 3 : examiner les limites CPU

Dans le cgroup concerné, inspectez les fichiers pertinents, notamment `cpu.max` et `cpu.stat` si présents.

### Étape 4 : interpréter les statistiques

Les compteurs sont souvent cumulatifs. Examinez leur progression dans le temps et la configuration du parent.

### Étape 5 : corriger

La modification éventuelle d'une limite doit être justifiée par le besoin de charge et les contraintes de la plateforme.

Ne supposez pas que les CPU disponibles sur l'hôte sont automatiquement disponibles en totalité pour le conteneur.


## 21.5 Incident E — Réseau lent ou connexion intermittente

### Étape 1 : examiner l'interface

```bash
ip -s link
```

### Étape 2 : examiner les routes

```bash
ip route
```

### Étape 3 : examiner les sockets

```bash
ss -s
ss -tan
```

### Étape 4 : examiner les statistiques TCP

```bash
nstat
```

si l'outil est disponible.

### Étape 5 : examiner le service

Vérifiez le port d'écoute, les journaux et les limites applicatives.

### Étape 6 : formuler une hypothèse

Le problème peut être situé dans la pile réseau locale, un lien réseau, une règle de filtrage, un équipement intermédiaire ou l'application elle-même.

### Étape 7 : valider

Comparez les symptômes observés localement et à distance. Ne concluez pas à une panne réseau uniquement à partir d'un échec de `ping`.


# 22. Travaux pratiques guidés

Les travaux pratiques suivants doivent être réalisés dans un environnement de laboratoire.

## TP 1 — Construire un état de référence

### Objectif

Collecter un état initial du système avant toute analyse de performance.

Exécutez :

```bash
uname -r
uname -m
lscpu
free -h
df -h
df -i
lsblk -f
ip addr
ip route
uptime
```

Puis, si disponibles :

```bash
mpstat -P ALL 1 5
vmstat 1 5
```

### Questions

1. Combien de CPU logiques sont visibles ?
2. Quelle quantité de mémoire est détectée ?
3. Quel est l'état général de l'espace disque ?
4. Quelles interfaces disposent d'une adresse ?
5. Quelle est la charge moyenne ?
6. Quelles informations manquent pour évaluer réellement les performances d'une application ?

### Résultat attendu

Vous devez disposer d'un état de référence documenté, sans avoir modifié la configuration.


## TP 2 — Examiner les appels système

### Objectif

Comprendre le comportement d'une commande grâce à `strace`.

Si `strace` est disponible :

```bash
strace -c ls /tmp
```

Examinez ensuite les opérations de fichiers :

```bash
strace -e trace=%file ls /tmp
```

### Questions

1. Quels appels système apparaissent ?
2. Quels appels sont associés à l'accès aux fichiers ?
3. Pourquoi une trace n'est-elle pas une mesure parfaite du coût sans instrumentation ?
4. Pourquoi éviter de tracer très longuement une application sensible à la latence ?

### Résultat attendu

Vous devez pouvoir expliquer plusieurs appels système observés et les limites du traçage.


## TP 3 — Mesurer une commande avec `perf`

### Objectif

Comparer des statistiques sur une commande contrôlée.

Si `perf` est installé et autorisé :

```bash
perf stat -- sleep 2
```

Examinez les événements disponibles :

```bash
perf list
```

Si un programme de test est disponible :

```bash
perf stat -- ./programme-test
```

### Questions

1. Quels compteurs sont collectés ?
2. Les compteurs matériels sont-ils tous disponibles ?
3. Quelles permissions sont nécessaires ?
4. Pourquoi faut-il comparer des exécutions équivalentes ?
5. Que mesure le temps écoulé par rapport au temps CPU ?

### Résultat attendu

Vous devez pouvoir décrire les mesures collectées et identifier les limites de l'expérience.


## TP 4 — Examiner la pression mémoire

### Objectif

Comparer la consommation mémoire et la pression observée.

Exécutez :

```bash
free -h
cat /proc/meminfo
cat /proc/pressure/memory
swapon --show
vmstat 1 5
```

### Questions

1. Quelle quantité de mémoire est disponible ?
2. Le swap est-il actif ?
3. Les statistiques PSI sont-elles présentes ?
4. Y a-t-il des signes d'attente mémoire ?
5. Quelles autres mesures seraient nécessaires pour identifier une cause ?

### Résultat attendu

Vous devez expliquer pourquoi la mémoire utilisée n'est pas à elle seule un indicateur suffisant d'incident.


## TP 5 — Comprendre cgroups v2

### Objectif

Examiner la hiérarchie de contrôle des ressources.

Commencez par :

```bash
findmnt -t cgroup2
```

Puis, si le chemin est accessible :

```bash
ls -la /sys/fs/cgroup
```

Examinez les fichiers qui existent réellement :

```bash
cat /sys/fs/cgroup/cpu.stat
```

Si le fichier est présent et accessible :

```bash
cat /sys/fs/cgroup/memory.current
cat /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.events
```

### Questions

1. Le système utilise-t-il cgroups v2 à l'emplacement attendu ?
2. Quels contrôleurs sont disponibles ?
3. Quelle est la différence entre utilisation mémoire et limite mémoire ?
4. Pourquoi faut-il identifier le cgroup d'un service avant d'interpréter ces valeurs ?

### Résultat attendu

Vous devez pouvoir reconnaître les interfaces de contrôle des ressources sans modifier les limites.


## TP 6 — Analyser un profil CPU

### Objectif

Utiliser `perf record` et `perf report` sur une charge de test existante.

Si le programme `programme-test` est disponible :

```bash
perf record -g -- ./programme-test
perf report
```

Examinez les fonctions dominantes.

### Questions

1. Quelles fonctions apparaissent dans le profil ?
2. Les symboles sont-ils suffisamment informatifs ?
3. Quel événement a été échantillonné ?
4. Le profil correspond-il au workload étudié ?
5. Quelle hypothèse pourrait être testée ?
6. Comment vérifier qu'une optimisation améliore vraiment la latence ?

### Résultat attendu

Vous devez produire une hypothèse d'optimisation appuyée sur les observations, et non une simple liste de fonctions.


## TP 7 — Observer les statistiques du stockage

### Objectif

Examiner le stockage avant d'exécuter un benchmark fichier.

```bash
lsblk -f
df -h
df -i
```

Si `iostat` est disponible :

```bash
iostat -xz 1 5
```

### Questions

1. Quels systèmes de fichiers sont montés ?
2. Quel est l'espace disponible ?
3. Quels périphériques présentent une activité ?
4. Pourquoi l'utilisation d'un périphérique ne suffit-elle pas à conclure à une saturation ?
5. Pourquoi le type de workload doit-il être documenté ?

### Résultat attendu

Vous devez être capable de distinguer capacité, débit, activité et latence.


# 23. Exercices d'évaluation corrigés

Répondez avant de consulter les corrections.

## Exercice 1 — Noyau et espace utilisateur

**Question :** pourquoi une application ne peut-elle pas généralement accéder directement à n'importe quelle ressource matérielle ?

**Correction :** les mécanismes du processeur et du système d'exploitation séparent les privilèges d'exécution. Les applications passent par des interfaces contrôlées et le noyau applique les règles d'accès appropriées.

## Exercice 2 — Appel système

**Question :** pourquoi un grand nombre d'appels système ne prouve-t-il pas automatiquement que l'application est lente ?

**Correction :** le coût dépend du nombre d'appels, de leurs opérations, du contexte, des attentes et du comportement de l'application. Une mesure doit établir le rapport avec la latence ou le coût CPU.

## Exercice 3 — CPU

**Question :** qu'indique un processus qui utilise 100 % d'un CPU logique ?

**Correction :** il consomme approximativement toute la capacité d'un CPU logique selon la convention de la mesure, pendant la période considérée. Cela ne signifie pas automatiquement que tous les CPU de la machine sont saturés.

## Exercice 4 — IPC

**Question :** pourquoi un IPC supérieur n'est-il pas nécessairement synonyme d'une meilleure performance applicative ?

**Correction :** l'IPC dépend des instructions, de la charge, du processeur et du mode de mesure. Le temps total, le débit, la latence et le travail réellement accompli doivent également être examinés.

## Exercice 5 — Profilage

**Question :** à quoi sert `perf record` ?

**Correction :** il permet de collecter des échantillons de performance pendant l'exécution d'une commande ou d'un programme, dans les limites des événements et permissions disponibles.

## Exercice 6 — RSS et VSZ

**Question :** pourquoi ne faut-il pas additionner naïvement les VSZ de plusieurs processus pour estimer la RAM occupée ?

**Correction :** l'espace virtuel ne correspond pas nécessairement à des pages résidentes en RAM, et certains mappings peuvent être partagés. Il faut tenir compte des métriques mémoire adaptées.

## Exercice 7 — PSI mémoire

**Question :** quelle information PSI peut-elle apporter au-delà du simple pourcentage de mémoire utilisée ?

**Correction :** elle renseigne sur les périodes pendant lesquelles des tâches subissent une attente associée à la pression mémoire.

## Exercice 8 — cgroups

**Question :** pourquoi un conteneur peut-il être limité alors que l'hôte semble avoir du CPU disponible ?

**Correction :** le conteneur peut atteindre son quota ou ses contraintes de ressources, y compris des limites héritées de groupes parents.

## Exercice 9 — Stockage

**Question :** un périphérique avec une utilisation proche de 100 % est-il toujours saturé ?

**Correction :** non. La signification dépend du périphérique et de son fonctionnement parallèle. Il faut examiner la latence, le débit, la file et le workload.

## Exercice 10 — NUMA

**Question :** pourquoi l'emplacement mémoire peut-il influencer les performances ?

**Correction :** sur une plateforme NUMA, les coûts d'accès peuvent varier selon la proximité entre CPU et mémoire. La localisation des threads et des pages peut donc influencer la latence et le débit.

## Exercice 11 — Tracing

**Question :** pourquoi un traçage très détaillé peut-il perturber l'application étudiée ?

**Correction :** la collecte et le traitement des événements consomment eux-mêmes des ressources, ce qui peut modifier la latence et le comportement du système.

## Exercice 12 — eBPF

**Question :** le fait qu'un programme eBPF soit accepté par le vérificateur prouve-t-il qu'il produit une analyse correcte ?

**Correction :** non. Le vérificateur impose des contraintes d'exécution, mais la qualité de la logique, la pertinence des données et l'interprétation restent à la charge de l'analyste.

## Exercice 13 — Benchmark

**Question :** pourquoi faut-il répéter les mesures ?

**Correction :** pour repérer les variations, limiter l'influence d'événements ponctuels et estimer si les différences observées sont reproductibles.

## Exercice 14 — Latence et débit

**Question :** peut-on augmenter le débit tout en dégradant la latence p99 ?

**Correction :** oui. Une augmentation du parallélisme ou de la profondeur de file peut améliorer le débit tout en accroissant l'attente pour certaines requêtes.

## Exercice 15 — Tuning

**Question :** pourquoi faut-il éviter d'appliquer une liste de paramètres noyau sans diagnostic ?

**Correction :** les paramètres interagissent avec le matériel, le noyau et le workload. Une valeur adaptée à une charge peut dégrader une autre charge.

## Exercice 16 — Diagnostic CPU faible, latence élevée

**Question :** quelles hypothèses faut-il examiner ?

**Correction :** attente I/O, dépendance réseau, verrous, files de traitement, limitations de ressources ou autres attentes applicatives. Il faut mesurer le mécanisme plutôt que conclure que le CPU est le problème.


# 24. Référence des commandes expertes

Cette section récapitule les commandes employées dans le cours.

## 24.1 Informations système

| Commande | Utilité |
|---|---|
| `uname -r` | Version du noyau |
| `uname -m` | Architecture |
| `cat /proc/cmdline` | Paramètres du démarrage |
| `cat /proc/version` | Informations de version exposées |
| `lscpu` | Informations CPU |
| `uptime` | Charge moyenne et durée de fonctionnement |
| `free -h` | Mémoire et swap |
| `vmstat 1 5` | Statistiques système sur plusieurs intervalles |

## 24.2 CPU et processus

| Commande | Utilité |
|---|---|
| `ps -eo pid,ppid,user,%cpu,%mem,comm` | Aperçu des processus |
| `ps -eo pid,ni,pri,comm` | Examiner les priorités |
| `mpstat -P ALL 1 5` | Statistiques CPU par processeur |
| `pidstat -u 1 5` | Utilisation CPU par processus |
| `pidstat -r 1 5` | Statistiques mémoire par processus |
| `pidstat -d 1 5` | Statistiques I/O par processus |
| `taskset -pc PID` | Examiner l'affinité CPU |
| `nice -n 10 commande` | Lancer avec une valeur nice |
| `renice 10 -p PID` | Ajuster la valeur nice |

## 24.3 Profilage et tracing

| Commande | Utilité |
|---|---|
| `perf list` | Lister les événements disponibles |
| `perf stat -- commande` | Mesurer des statistiques |
| `perf record -g -- commande` | Collecter un profil d'échantillonnage |
| `perf report` | Examiner un profil enregistré |
| `strace -c commande` | Résumer les appels système observés |
| `strace -e trace=%file commande` | Examiner certaines opérations de fichiers |
| `journalctl -k` | Consulter les journaux du noyau |
| `cat /sys/kernel/tracing/available_events` | Examiner les tracepoints disponibles si l'interface est accessible |

## 24.4 Mémoire

| Commande | Utilité |
|---|---|
| `cat /proc/meminfo` | Examiner les statistiques mémoire |
| `cat /proc/pressure/memory` | Examiner la pression mémoire PSI |
| `cat /proc/pressure/cpu` | Examiner la pression CPU PSI |
| `cat /proc/pressure/io` | Examiner la pression I/O PSI |
| `swapon --show` | Examiner le swap actif |
| `ps -o pid,comm,vsz,rss,%mem -p PID` | Examiner certaines métriques mémoire d'un processus |
| `numactl --hardware` | Examiner la topologie NUMA si disponible |
| `numastat` | Examiner des statistiques NUMA si disponible |

## 24.5 Stockage

| Commande | Utilité |
|---|---|
| `lsblk -f` | Examiner le stockage et les systèmes de fichiers |
| `df -h` | Espace utilisé et disponible |
| `df -i` | Utilisation des inodes |
| `du -sh repertoire` | Estimer l'espace utilisé par un répertoire |
| `findmnt` | Examiner les points de montage |
| `iostat -xz 1 5` | Statistiques de périphériques si disponible |
| `pidstat -d 1 5` | Activité I/O par processus |
| `tar -tzf archive.tar.gz` | Lister le contenu d'une archive |
| `rsync -a --dry-run source/ destination/` | Simuler une synchronisation |

## 24.6 Réseau

| Commande | Utilité |
|---|---|
| `ip -s link` | Statistiques d'interfaces |
| `ip route` | Table de routage |
| `ss -s` | Synthèse des sockets |
| `ss -tan` | Connexions TCP |
| `ss -tln` | Sockets TCP en écoute |
| `nstat` | Statistiques réseau du noyau si disponible |
| `ethtool -S interface` | Statistiques du pilote si disponible |
| `tc qdisc show` | Examiner les disciplines de file |

## 24.7 Noyau, modules et paramètres

| Commande | Utilité |
|---|---|
| `lsmod` | Examiner les modules chargés |
| `modinfo module` | Informations sur un module |
| `dmesg` | Messages du noyau |
| `journalctl -k` | Journaux du noyau |
| `sysctl -a` | Examiner les paramètres accessibles |
| `sysctl parametre` | Examiner un paramètre précis |
| `findmnt -t tracefs` | Examiner tracefs |
| `systemctl show service` | Examiner les propriétés d'une unité systemd |


# 25. Challenge final — Diagnostiquer et optimiser un serveur Linux

## 25.1 Scénario

Vous êtes chargé d'analyser un serveur Linux de laboratoire qui présente un problème de performances.

Les utilisateurs signalent une augmentation du temps de réponse. Le CPU semble parfois sollicité, mais la cause n'est pas connue.

Vous devez établir une référence, collecter les indicateurs utiles, formuler une hypothèse, proposer un test et produire un rapport.

**Ce challenge ne consiste pas à appliquer des réglages au hasard.** Le but est de démontrer une méthode d'analyse fondée sur des mesures.

## 25.2 Objectifs

Vous devez :

1. Documenter le système.
2. Examiner le CPU et les processus.
3. Examiner la mémoire et PSI.
4. Examiner l'espace de stockage et les I/O.
5. Examiner le réseau.
6. Identifier les outils de profilage disponibles.
7. Formuler au moins deux hypothèses.
8. Définir des critères permettant de tester les hypothèses.
9. Proposer une correction conditionnelle.
10. Produire un rapport clair et reproductible.

## 25.3 Conditions de sécurité

Réalisez le challenge sur une machine virtuelle ou un serveur de test.

Ne modifiez pas le noyau, le pare-feu, les paramètres de démarrage ou les limites globales sans nécessité démontrée.

Ne lancez pas de benchmark destructif.

N'effectuez aucune opération de formatage ou d'écriture directe sur un périphérique bloc.

Ne changez pas les options SSH ou les règles de pare-feu d'une machine distante sans une procédure de secours.

## 25.4 Étape 1 — Documenter l'environnement

Collectez :

```bash
cat /etc/os-release
uname -r
uname -m
lscpu
free -h
lsblk -f
df -h
ip addr
ip route
uptime
```

Notez les informations essentielles :

- Distribution et version.
- Noyau.
- CPU et mémoire.
- Stockage.
- Interfaces et routes.
- Charge de référence.

## 25.5 Étape 2 — Examiner le CPU

Exécutez :

```bash
ps -eo pid,ppid,user,%cpu,%mem,stat,comm --sort=-%cpu | head
```

Si `mpstat` est disponible :

```bash
mpstat -P ALL 1 5
```

Si `pidstat` est disponible :

```bash
pidstat -u 1 5
```

Notez les processus dominants et les différences entre les CPU logiques.

## 25.6 Étape 3 — Examiner la mémoire

Exécutez :

```bash
free -h
grep -E 'MemAvailable|SwapTotal|SwapFree' /proc/meminfo
swapon --show
```

Puis, si PSI est disponible :

```bash
cat /proc/pressure/memory
cat /proc/pressure/cpu
```

Notez les valeurs et expliquez leurs limites.

## 25.7 Étape 4 — Examiner le stockage

Exécutez :

```bash
df -h
df -i
findmnt
```

Si les outils correspondants sont présents :

```bash
iostat -xz 1 5
pidstat -d 1 5
```

Identifiez les points de montage importants et les indicateurs que vous souhaiteriez suivre plus longtemps.

## 25.8 Étape 5 — Examiner le réseau

Exécutez :

```bash
ip -s link
ip route
ss -s
ss -tan
```

Si `nstat` est disponible :

```bash
nstat
```

Décrivez les signes de problème que vous chercheriez dans les compteurs.

## 25.9 Étape 6 — Examiner le profilage

Si `perf` est installé et autorisé :

```bash
perf list
perf stat -- sleep 2
```

Le deuxième test sert à vérifier le fonctionnement élémentaire de la collecte. Il ne représente pas un benchmark applicatif utile en lui-même.

Si un programme de test est disponible :

```bash
perf stat -- ./programme-test
```

Ne fabriquez pas une charge lourde sans objectif défini.

## 25.10 Étape 7 — Formuler les hypothèses

Vous devez écrire au moins deux hypothèses.

Exemples :

### Hypothèse A — Saturation CPU

Prédictions :

- Le CPU est fortement sollicité pendant les pics.
- Certains processus concentrent la consommation.
- Les mesures de pression CPU et la latence varient de manière cohérente.

### Hypothèse B — Pression mémoire

Prédictions :

- PSI mémoire augmente pendant les pics.
- Des événements de récupération ou d'échange sont visibles.
- Les temps de réponse se dégradent en parallèle.

### Hypothèse C — Latence des entrées-sorties

Prédictions :

- Les mesures de stockage révèlent une attente accrue.
- Des processus attendent des opérations de stockage.
- PSI I/O augmente pendant l'incident.

### Hypothèse D — Limitation cgroup

Prédictions :

- Les ressources globales de l'hôte semblent disponibles.
- Le cgroup du service présente une limite ou des événements de restriction.
- La latence se dégrade lorsque cette limite est atteinte.

Les hypothèses ci-dessus sont des exemples. Le challenge doit conclure à partir de données réelles, et non d'un résultat supposé.

## 25.11 Étape 8 — Construire un rapport

Créez :

```text
rapport-performance.md
```

Le rapport doit contenir :

```text
# Rapport de diagnostic

## 1. Environnement
Distribution, noyau, CPU, memoire et stockage.

## 2. Symptome
Description et periode observee.

## 3. Mesures initiales
CPU, memoire, stockage, reseau et PSI.

## 4. Hypotheses
Explication de chaque hypothese.

## 5. Tests
Commandes, parametres, periode et resultats.

## 6. Interpretation
Faits observes et limites des mesures.

## 7. Cause probable
Conclusion justifiee par les resultats.

## 8. Correction proposee
Modification ciblee et criteres de validation.

## 9. Retour arriere
Procedure de restauration de la configuration initiale.

## 10. Validation
Mesures avant et apres, effets secondaires et conclusion.
```

## 25.12 Barème du challenge

| Compétence | Points |
|---|---:|
| Inventaire technique | 10 |
| Analyse CPU | 15 |
| Analyse mémoire et PSI | 15 |
| Analyse stockage | 15 |
| Analyse réseau | 10 |
| Choix des outils de profilage | 10 |
| Hypothèses et tests | 10 |
| Qualité de la correction proposée | 5 |
| Rapport et reproductibilité | 5 |
| Gestion des risques et retour arrière | 5 |
| **Total** | **100** |

Une excellente réponse ne doit pas inventer une cause en l'absence de données suffisantes. Elle doit exposer ce qui est établi, ce qui reste incertain et quelle mesure permettrait de trancher.


# 26. Correction détaillée du challenge

Cette section présente une correction méthodologique. Elle ne suppose pas qu'un problème particulier est réellement présent sur votre machine.

## 26.1 Créer une arborescence de diagnostic

```bash
mkdir -p ~/linux-expert-lab/mesures
mkdir -p ~/linux-expert-lab/rapports
mkdir -p ~/linux-expert-lab/scripts
```

Le répertoire de laboratoire servira à conserver les notes et les résultats.

## 26.2 Créer un script de collecte non destructif

Créez :

```bash
nano ~/linux-expert-lab/scripts/collecte-initiale.sh
```

Contenu :

```bash
#!/usr/bin/env bash

set -u
set -o pipefail

BASE="$HOME/linux-expert-lab"
MESURES="$BASE/mesures"
RAPPORT="$MESURES/etat-initial.txt"

erreur() {
    echo "ERREUR : $*" >&2
    exit 1
}

if [ ! -d "$BASE" ]; then
    erreur "Le repertoire de laboratoire est absent."
fi

if [ ! -d "$MESURES" ]; then
    erreur "Le repertoire de mesures est absent."
fi

for commande in date uname uptime free df ps; do
    if ! command -v "$commande" >/dev/null 2>&1; then
        erreur "Commande indisponible : $commande"
    fi
done

if ! {
    echo "ETAT INITIAL DU SYSTEME"
    echo "Date : $(date '+%F %T')"
    echo
    echo "VERSION DU NOYAU"
    uname -r
    echo
    echo "ARCHITECTURE"
    uname -m
    echo
    echo "DUREE DE FONCTIONNEMENT"
    uptime
    echo
    echo "MEMOIRE"
    free -h
    echo
    echo "STOCKAGE"
    df -h
    echo
    echo "PROCESSUS DOMINANTS"
    ps -eo pid,user,%cpu,%mem,stat,comm --sort=-%cpu | head
    echo
    echo "PRESSION CPU"
    if [ -r /proc/pressure/cpu ]; then
        cat /proc/pressure/cpu
    else
        echo "PSI CPU indisponible"
    fi
    echo
    echo "PRESSION MEMOIRE"
    if [ -r /proc/pressure/memory ]; then
        cat /proc/pressure/memory
    else
        echo "PSI memoire indisponible"
    fi
    echo
    echo "PRESSION I/O"
    if [ -r /proc/pressure/io ]; then
        cat /proc/pressure/io
    else
        echo "PSI I/O indisponible"
    fi
} > "$RAPPORT"; then
    erreur "Impossible de produire le rapport."
fi

if [ ! -s "$RAPPORT" ]; then
    erreur "Le rapport est vide."
fi

echo "Rapport cree : $RAPPORT"
exit 0
```

## 26.3 Vérifier et exécuter le script

Contrôlez la syntaxe :

```bash
bash -n ~/linux-expert-lab/scripts/collecte-initiale.sh
```

Rendez-le exécutable :

```bash
chmod u+x ~/linux-expert-lab/scripts/collecte-initiale.sh
```

Exécutez-le :

```bash
~/linux-expert-lab/scripts/collecte-initiale.sh
```

Affichez le rapport :

```bash
less ~/linux-expert-lab/mesures/etat-initial.txt
```

Le rapport fournit un état initial. Il ne mesure pas toute l'activité pendant un incident et ne remplace pas une collecte temporelle.

## 26.4 Examiner les résultats

Utilisez les mesures du rapport pour remplir une fiche.

| Domaine | Observation | Hypothèse | Mesure complémentaire |
|---|---|---|---|
| CPU | Valeurs observées | Saturation ou charge normale | Statistiques dans le temps |
| Mémoire | Valeurs observées | Pression ou cache récupérable | PSI et événements |
| Stockage | Valeurs observées | Latence ou capacité insuffisante | `iostat` et `pidstat` |
| Réseau | Valeurs observées | Perte, route ou service | Compteurs et mesures ciblées |
| cgroups | Valeurs observées | Limitation ou absence de limite | Compteurs du cgroup réel |

Il ne faut pas remplir la colonne de conclusion avec une cause certaine si les observations ne permettent pas de la démontrer.

## 26.5 Exemple de raisonnement CPU

Supposons, à titre illustratif, que les mesures montrent :

- Un CPU fortement sollicité pendant l'incident.
- Un processus concentrant une grande partie de cette charge.
- Une pression CPU qui augmente en même temps que la latence.
- Un profil où une fonction applicative domine les échantillons.

La conclusion devient plus solide si ces éléments sont reproductibles sous la même charge.

Une correction possible pourrait consister à réduire le travail effectué par cette fonction ou à améliorer le parallélisme utile.

Le simple ajout d'un cœur ne garantit pas une amélioration si le code est séquentiel ou dominé par une autre ressource.

## 26.6 Exemple de raisonnement mémoire

Supposons que :

- `MemAvailable` reste relativement faible.
- PSI mémoire augmente pendant les pics.
- L'activité de récupération mémoire devient importante.
- La latence s'accroît en parallèle.

Cela peut justifier une investigation approfondie du working set et de la récupération mémoire.

Il faut toutefois examiner les données applicatives, les limites cgroups, les défauts de page et les journaux avant de retenir une cause précise.

## 26.7 Exemple de raisonnement stockage

Supposons que les statistiques montrent une hausse de latence des entrées-sorties, accompagnée d'une pression I/O et de temps d'attente de processus.

Ces indices peuvent indiquer que le stockage contribue au ralentissement.

Il reste nécessaire de savoir :

- Quel périphérique est concerné.
- Quel workload l'utilise.
- Quelle taille d'opération est effectuée.
- Si des écritures synchrones dominent.
- Si un autre processus produit la charge.
- Si des erreurs ou des timeouts apparaissent.

La correction peut relever du code, de la configuration de la base de données, de la mise en cache ou du stockage lui-même.

## 26.8 Exemple de raisonnement sur les cgroups

Supposons que l'hôte possède plusieurs CPU disponibles, mais que le service soit soumis à une limite CPU stricte.

Si les compteurs du cgroup montrent une limitation qui augmente pendant les pics, il faut examiner la relation entre cette limite et le débit attendu.

Une augmentation de la limite peut être proposée si elle respecte la capacité globale de l'hôte et les objectifs des autres services.

Cette décision doit être testée et suivie d'une mesure après changement.

## 26.9 Construire une comparaison avant/après

Une comparaison doit distinguer les facteurs qui changent :

```text
AVANT
- Charge connue
- Configuration connue
- Mesures de reference
- Temps de reponse p50/p95/p99
- Taux d'erreur
- Ressources

MODIFICATION CONTROLEE
- Un changement documente
- Procedure de retour arriere disponible

APRES
- Meme charge autant que possible
- Meme perimetre de mesure
- Memes indicateurs
- Comparaison des percentiles
- Verification des effets secondaires
```

Les changements doivent être isolés autant que possible. Si plusieurs paramètres sont modifiés en même temps, il devient plus difficile d'identifier la cause d'une amélioration ou d'une dégradation.

## 26.10 Conclusion attendue du challenge

Un rapport expert doit expliquer :

- Le symptôme et sa mesure.
- Les ressources étudiées.
- Les résultats observés.
- Les hypothèses rejetées ou conservées.
- Les limites de la collecte.
- La cause la plus probable si les preuves sont suffisantes.
- La correction proposée.
- Les critères de validation.
- Le retour arrière.

Si aucune cause n'est démontrée, le rapport doit le préciser. Une conclusion honnête avec un plan de mesure supplémentaire est préférable à une optimisation arbitraire.


# 27. Checklist finale des compétences

## Architecture et noyau

- [ ] Je sais distinguer l'espace utilisateur de l'espace noyau.
- [ ] Je comprends le rôle des appels système.
- [ ] Je connais le rôle du VFS.
- [ ] Je comprends les grandes catégories de contextes d'exécution.
- [ ] Je sais examiner les informations de version du noyau.
- [ ] Je sais consulter les messages du noyau.

## CPU et ordonnancement

- [ ] Je comprends le rôle de l'ordonnanceur.
- [ ] Je sais distinguer processus et threads.
- [ ] Je comprends les valeurs nice.
- [ ] Je sais examiner l'affinité CPU.
- [ ] Je sais distinguer utilisation CPU et latence applicative.
- [ ] Je comprends pourquoi la charge moyenne n'est pas un pourcentage CPU.
- [ ] Je sais rechercher les processus dominants.
- [ ] Je comprends les limites d'une mesure ponctuelle.

## Profilage et tracing

- [ ] Je sais expliquer la différence entre profilage et traçage.
- [ ] Je comprends le rôle de `perf stat`.
- [ ] Je sais collecter et examiner un profil avec `perf record` et `perf report`.
- [ ] Je comprends les limites des compteurs matériels.
- [ ] Je sais pourquoi les symboles sont importants.
- [ ] Je comprends les effets du coût de collecte.
- [ ] Je sais expliquer le rôle des tracepoints.
- [ ] Je connais les principes de ftrace et d'eBPF.
- [ ] Je sais protéger les données produites par le profilage.

## Mémoire et NUMA

- [ ] Je sais distinguer RSS et VSZ.
- [ ] Je comprends la différence entre mémoire libre et mémoire disponible.
- [ ] Je comprends le rôle du cache de pages.
- [ ] Je sais distinguer défauts de page mineurs et majeurs.
- [ ] Je sais examiner le swap et les événements OOM.
- [ ] Je comprends les métriques PSI mémoire.
- [ ] Je comprends le principe de NUMA.
- [ ] Je sais pourquoi les Huge Pages peuvent aider certains workloads et en dégrader d'autres.

## Stockage et réseau

- [ ] Je sais distinguer débit, IOPS et latence.
- [ ] Je comprends la différence entre `df`, `du` et les statistiques des périphériques.
- [ ] Je sais lire les résultats d'un outil de mesure d'entrées-sorties.
- [ ] Je sais pourquoi un benchmark doit décrire son workload.
- [ ] Je sais examiner les sockets et les interfaces réseau.
- [ ] Je comprends les retransmissions et les pertes de paquets.
- [ ] Je comprends le rôle des files et des traitements réseau.
- [ ] Je sais distinguer une limitation réseau d'une limitation applicative.

## cgroups et isolation

- [ ] Je sais distinguer namespaces et cgroups.
- [ ] Je comprends le rôle des contrôleurs CPU, mémoire et I/O.
- [ ] Je sais examiner les limites d'un cgroup.
- [ ] Je comprends pourquoi les ressources disponibles sur l'hôte peuvent différer de celles d'un conteneur.
- [ ] Je sais interpréter les compteurs temporels avec prudence.

## Tuning et diagnostic

- [ ] Je sais établir une référence avant modification.
- [ ] Je sais formuler une hypothèse mesurable.
- [ ] Je sais choisir un outil adapté à une question.
- [ ] Je sais effectuer une comparaison avant/après.
- [ ] Je sais examiner les effets secondaires d'une optimisation.
- [ ] Je sais préparer un retour arrière.
- [ ] Je sais documenter une conclusion et ses limites.
- [ ] Je sais reconnaître quand les données disponibles ne suffisent pas à identifier une cause.


# 28. Références techniques officielles

Ces références permettent d'approfondir les mécanismes du noyau et les outils utilisés dans le cours.

## 28.1 Documentation du noyau Linux

Documentation générale du noyau :

https://docs.kernel.org/

Guide sur les technologies de traçage :

https://docs.kernel.org/trace/

Documentation de Pressure Stall Information :

https://docs.kernel.org/accounting/psi.html

Documentation du planificateur :

https://docs.kernel.org/scheduler/

Documentation de Multi-Gen LRU :

https://docs.kernel.org/admin-guide/mm/multigen_lru.html

Documentation de la sécurité des événements de performance :

https://docs.kernel.org/admin-guide/perf-security.html

## 28.2 Documentation des commandes

Pages de manuel de `perf stat` :

https://man7.org/linux/man-pages/man1/perf-stat.1.html

Documentation générale de `perf` et de ses sous-commandes :

https://perf.wiki.kernel.org/

Pages de manuel de `strace` :

https://man7.org/linux/man-pages/man1/strace.1.html

Documentation de systemd :

https://www.freedesktop.org/software/systemd/man/

## 28.3 Méthodologie de performance

Brendan Gregg — *The USE Method* :

https://www.brendangregg.com/usemethod.html

Brendan Gregg — *Performance Analysis Methodology* :

https://www.brendangregg.com/methodology.html

Ces ressources complètent le cours. Les fonctionnalités disponibles, les noms d'événements et les commandes peuvent dépendre de la version du noyau, des outils, de l'architecture et de la distribution.


# Conclusion générale

L'expertise Linux en performance et en noyau repose sur une compréhension des interactions entre les applications, le noyau, les ressources matérielles et les politiques de contrôle.

Le CPU peut être limité par la concurrence, l'ordonnancement ou le travail inutile. La mémoire peut provoquer des attentes et des récupérations coûteuses. Le stockage peut introduire de la latence malgré un débit faible. Le réseau peut perdre du temps dans les files, les retransmissions ou le traitement des paquets. Les conteneurs peuvent subir des limites invisibles lorsqu'on observe uniquement l'hôte.

Les outils tels que `perf`, PSI, `ftrace`, eBPF, `iostat`, `pidstat` et les interfaces cgroups donnent des angles de vue complémentaires. Aucun outil ne fournit à lui seul une explication complète de toutes les situations.

Le travail expert consiste à choisir les mesures pertinentes, à comprendre leurs limites, à tester les hypothèses et à vérifier que la correction améliore réellement le résultat attendu.

**Les principes à retenir :**

1. Mesurer avant de modifier.
2. Distinguer les symptômes des causes.
3. Choisir les outils selon la question posée.
4. Comparer des workloads équivalents.
5. Éviter les réglages arbitraires du noyau.
6. Protéger les données de profilage et de diagnostic.
7. Vérifier les effets secondaires des optimisations.
8. Documenter les preuves et les limites.
9. Préparer le retour arrière avant les changements sensibles.
10. Ne jamais confondre une hypothèse plausible avec une cause démontrée.

Fin du cours — **Linux Expert : Performance et Kernel**.