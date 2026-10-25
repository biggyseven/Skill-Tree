# Gestion des processus Linux — Niveau Expert

> **Fichier :** `process-expert.md`  
> **Niveau :** Expert  
> **Domaine :** Administration système Linux, performance, diagnostic noyau et supervision  
> **Objectif :** Maîtriser le cycle de vie des processus, les mécanismes noyau, l'ordonnancement, les signaux, les espaces de noms, les groupes de contrôle, le diagnostic de performance et la supervision en production.  
> **Environnement recommandé :** Machine virtuelle Linux de laboratoire, Debian ou Ubuntu, Fedora ou distribution compatible.  
> **Prérequis :** Maîtriser les notions et commandes présentées dans `process-debutant.md` et `process-intermediaire.md`.


# Sommaire

1. Positionnement du niveau expert
2. Architecture interne d'une tâche Linux
3. Création des processus : `fork()`, `clone()` et `clone3()`
4. Exécution des programmes : `execve()`
5. Terminaison, `wait()`, zombies et processus orphelins
6. Identité des processus et sécurité
7. Identifiants, groupes, sessions et espaces de noms
8. PIDFD : identifier un processus sans dépendre uniquement de son PID
9. Signaux : dispositions, masques, signaux en attente et synchronisation
10. Ordonnancement et politiques de priorité
11. Diagnostic avancé du CPU
12. Mémoire des processus : VIRT, RSS, PSS et fautes de page
13. Pression mémoire et OOM killer
14. Descripteurs, fichiers ouverts et fuites de ressources
15. Processus bloqués, attentes noyau et interblocages
16. Diagnostic des appels système avec `strace`
17. Profilage avec `perf`
18. Traces dynamiques et eBPF avec `bpftrace`
19. Groupes de contrôle Linux : cgroups v2
20. Pression système avec PSI
21. Gestion experte des services `systemd`
22. Sécurité des processus, capacités et isolation
23. Diagnostic des conteneurs et environnements isolés
24. Automatisation fiable des opérations
25. Scénarios avancés de dépannage
26. Travaux pratiques guidés
27. Exercices d'application
28. Corrections détaillées des exercices
29. Défi final : incident complexe sur un serveur de production
30. Correction détaillée du défi final
31. Checklist des compétences expertes
32. Fiche de référence des commandes
33. Glossaire technique
34. Documentation officielle


# 1. Positionnement du niveau expert

## 1.1. Ce qui distingue l'administration experte

Au niveau débutant, l'objectif était d'identifier un processus, de consulter son état et d'utiliser des commandes de contrôle.

Au niveau intermédiaire, le diagnostic s'est étendu aux groupes de processus, aux threads, aux statistiques temporelles, aux services, aux scripts et aux limites de ressources.

Le niveau expert doit permettre de diagnostiquer des incidents pour lesquels les observations de premier niveau ne suffisent plus.

Exemples :

- un processus consomme peu de CPU mais l'application présente une latence élevée ;
- un service reste actif alors que certaines requêtes échouent ;
- le CPU semble disponible, mais une application atteint son quota ;
- un service subit des arrêts provoqués par une limite mémoire ;
- des processus restent en attente noyau ;
- un PID mémorisé par un outil automatisé peut avoir été réutilisé ;
- le noyau termine des processus pour récupérer de la mémoire ;
- une application multiplie ses threads ou ses processus enfants ;
- un processus conserve des fichiers supprimés ouverts ;
- une trace révèle des appels système qui attendent sans progresser ;
- une application isolée dans un conteneur n'a pas la même visibilité que l'hôte ;
- le système semble lent alors qu'aucun processus ne paraît consommer beaucoup de CPU.

L'expert ne choisit pas un outil parce qu'il est populaire. Il choisit l'outil qui mesure précisément le phénomène à expliquer.

## 1.2. Les couches d'analyse

La gestion experte des processus se comprend à travers plusieurs couches complémentaires.

```text
                    APPLICATION
                         |
                         v
               PROGRAMME ET THREADS
                         |
                         v
               APPELS SYSTÈME
                         |
                         v
                  NOYAU LINUX
                  /     |      \
                 /      |       \
                v       v        v
          ORDONNANCEMENT MÉMOIRE  E/S
                |       |        |
                +-------+--------+
                        |
                        v
                  RESSOURCES
                 ET CONTENDANCE
                        |
                        v
             MESURES ET OBSERVABILITÉ
                        |
                        v
                DIAGNOSTIC EXPERT
```

Cette organisation rappelle une règle essentielle : une anomalie constatée au niveau applicatif peut provenir du code, d'un appel système, du noyau, d'une ressource matérielle ou d'une limite de l'environnement d'exécution.

## 1.3. Une démarche reproductible

Un diagnostic expert doit comporter cinq éléments.

1. **Symptôme mesurable :** ralentissement, erreur, consommation ou blocage.
2. **Collecte reproductible :** commandes, options, intervalle d'observation et heure.
3. **Hypothèses explicites :** causes possibles qui restent à vérifier.
4. **Preuves discriminantes :** données permettant de confirmer ou d'écarter les hypothèses.
5. **Validation :** nouvelle mesure après intervention, avec un résultat comparable à la situation initiale.

Un diagnostic du type « le CPU est élevé, j'ai arrêté le processus » est incomplet. Il ne montre ni pourquoi le CPU était élevé, ni pourquoi l'arrêt était nécessaire, ni si le problème a été résolu.


# 2. Architecture interne d'une tâche Linux

## 2.1. Du processus à la tâche du noyau

Dans le vocabulaire courant, on parle de processus pour désigner une exécution dotée d'un PID et de ressources.

Dans l'implémentation Linux, le noyau organise le travail autour de structures et de mécanismes internes représentant les tâches planifiables. La structure centrale traditionnellement nommée `task_struct` contient de nombreuses informations nécessaires à la gestion d'une tâche.

Il ne faut pas considérer `task_struct` comme une interface stable que les applications doivent manipuler directement. C'est un détail d'implémentation du noyau, susceptible d'évoluer.

Conceptuellement, une tâche est associée à des informations telles que :

```text
TÂCHE LINUX
|
+-- Identité
|   +-- PID dans un espace de noms
|   +-- Identifiants utilisateur et groupe
|
+-- Ordonnancement
|   +-- État
|   +-- Politique
|   +-- Priorité
|   +-- Statistiques CPU
|
+-- Ressources et contexte
|   +-- Mémoire virtuelle
|   +-- Descripteurs de fichiers
|   +-- Répertoire de travail
|   +-- Credentials de sécurité
|
+-- Relations
|   +-- Parent et enfants
|   +-- Groupe de processus
|   +-- Session
|   +-- Groupe de contrôle
|
+-- Exécution
    +-- Contexte processeur
    +-- Pile d'exécution
    +-- Informations de synchronisation
```

Toutes ces ressources ne sont pas nécessairement exclusives à chaque tâche. Certaines sont partagées entre les threads d'un même processus.

## 2.2. Processus et thread : une distinction opérationnelle

Du point de vue de l'administration, un processus est une unité d'identification et de gestion de haut niveau.

Les threads sont des fils d'exécution qui appartiennent généralement à un même groupe de threads et partagent un certain nombre de ressources.

```text
APPLICATION
PID visible : 8000
|
+-- Mémoire du processus
|
+-- Descripteurs communs
|
+-- Thread principal
|   Identifiant de tâche : 8000
|
+-- Thread de calcul
|   Identifiant de tâche : 8001
|
+-- Thread de communication
    Identifiant de tâche : 8002
```

Les identifiants de tâche de ce schéma sont fictifs. Dans Linux, le PID visible du groupe de threads et les identifiants de threads peuvent être présentés différemment selon l'outil.

La vue détaillée des threads peut être obtenue avec :

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

Ou :

```bash
top -H -p PID
```

Une consommation CPU importante au niveau d'une application n'indique pas nécessairement quel thread réalise le travail. Ces commandes permettent d'affiner l'analyse.

## 2.3. Espaces mémoire distincts et ressources partagées

Deux processus créés séparément possèdent normalement des espaces mémoire distincts, même si des pages peuvent être partagées physiquement.

Les threads créés dans un même groupe de threads partagent généralement un espace mémoire et d'autres ressources.

Le partage n'est pas une simple question de quantité de RAM : il concerne aussi la visibilité des modifications mémoire, les fichiers ouverts, les signaux, les verrous et les communications.

Cette distinction est fondamentale lorsqu'il faut expliquer :

- pourquoi la modification d'une variable dans un processus enfant ne modifie pas automatiquement celle du parent ;
- pourquoi un thread peut accéder aux structures de données d'un autre thread ;
- pourquoi un incident de concurrence peut affecter l'ensemble d'une application multithread ;
- pourquoi les mesures RSS peuvent compter plusieurs fois des pages partagées.


# 3. Création des processus : `fork()`, `clone()` et `clone3()`

## 3.1. Le rôle de `fork()`

L'appel système `fork()` crée un nouveau processus enfant à partir du processus appelant.

Le parent et l'enfant sont ensuite deux processus distincts.

Leurs PID sont différents. Leurs espaces mémoire sont logiquement séparés, même si le noyau peut partager provisoirement des pages physiques.

La documentation officielle de [`fork(2)`](https://man7.org/linux/man-pages/man2/fork.2.html) décrit ce mécanisme et les différences entre les contextes du parent et de l'enfant.

## 3.2. Schéma de création

```text
PROCESSUS PARENT
       |
       | fork()
       |
       +----------------------+
       |                      |
       v                      v
PARENT CONTINUE          PROCESSUS ENFANT
PID = PARENT             PID = NOUVEAU PID
       |                      |
       v                      v
Retour de fork()         Retour de fork()
avec valeur positive     avec valeur 0
```

Dans un programme C, le retour de `fork()` permet généralement de distinguer le parent de l'enfant :

- `-1` signale un échec ;
- `0` est retourné à l'enfant ;
- une valeur positive correspondant au PID enfant est retournée au parent.

Ceci décrit l'interface de programmation, pas un comportement directement visible dans toutes les commandes shell.

## 3.3. Copy-on-write

Après un `fork()`, Linux n'a pas besoin de copier immédiatement toute la mémoire du parent vers l'enfant.

Le mécanisme dit **copy-on-write**, ou copie à l'écriture, permet généralement de partager certaines pages physiques tant qu'aucun des processus ne doit les modifier séparément.

Quand une page doit être modifiée dans un contexte où elle ne peut plus rester partagée de cette façon, le noyau peut créer une copie.

```text
APRÈS FORK
|
+-- Parent --------+
|                  |
+-- Enfant --------+---- pages physiques partagées
                         |
                         v
                  ÉCRITURE D'UNE PAGE
                         |
                         v
               COPIE SI NÉCESSAIRE
                         |
              +----------+----------+
              |                     |
              v                     v
       Page du parent         Page de l'enfant
```

Les détails dépendent des mappages, des permissions mémoire et des mécanismes du noyau.

### Conséquence pratique

La création d'un processus enfant à partir d'un grand processus n'entraîne pas obligatoirement une copie physique immédiate de toute sa mémoire.

Cependant, des processus enfants qui modifient une grande quantité de mémoire peuvent provoquer des allocations et des copies de pages importantes.

Cela peut contribuer à une hausse de la mémoire physique, des fautes de page et du temps de traitement.

## 3.4. `clone()` et `clone3()`

`clone()` permet de créer une tâche avec des options qui déterminent quelles ressources seront partagées.

Il constitue l'un des mécanismes fondamentaux employés par Linux pour mettre en œuvre les threads et d'autres formes de création de tâches.

`clone3()` offre une interface plus récente fondée sur une structure d'arguments extensible.

Les détails dépendent du noyau et des bibliothèques utilisées.

Les indicateurs de création peuvent notamment définir le partage de ressources et la création dans certains espaces de noms.

Il n'est pas nécessaire de reproduire directement ces appels dans les scripts d'administration habituels. Il faut néanmoins comprendre qu'un lancement de programme, une création de processus et une création de thread ne reposent pas tous sur des contextes identiques.

## 3.5. Pourquoi un `fork()` peut-il échouer ?

La création d'un processus peut échouer, par exemple lorsque :

- une limite de tâches est atteinte ;
- le système manque de ressources nécessaires ;
- une limite de processus par utilisateur est atteinte ;
- le groupe de contrôle refuse une nouvelle tâche ;
- une restriction de sécurité s'applique ;
- le noyau ne peut pas allouer les ressources nécessaires.

Un message tel que `Resource temporarily unavailable` ne désigne donc pas automatiquement un problème de CPU.

Il faut vérifier les limites de tâches, la configuration de l'utilisateur, les cgroups et les journaux avant de conclure.

## 3.6. Diagnostic de la création de processus

Pour observer le nombre de processus visibles :

```bash
ps -e --no-headers | wc -l
```

Pour consulter la limite de PID ou de tâches déclarée par le système :

```bash
cat /proc/sys/kernel/pid_max
```

Cette valeur représente la limite de l'espace des numéros PID, et non le nombre de processus qu'un utilisateur peut lancer sans restriction.

Pour examiner les limites du shell :

```bash
ulimit -a
```

Pour une tâche administrée par `systemd` :

```bash
systemctl show nom.service -p TasksCurrent -p TasksMax
```

Les champs disponibles dépendent de la version de `systemd`.

Il faut distinguer le nombre de PID allouables, le nombre de tâches présentes, les limites par utilisateur et les limites propres au service.


# 4. Exécution des programmes : `execve()`

## 4.1. Créer un processus et exécuter un programme sont deux opérations différentes

La création d'un processus ne signifie pas forcément qu'un nouveau fichier exécutable est immédiatement lancé.

Un parent peut créer un enfant, puis cet enfant utiliser `execve()` pour remplacer son programme courant.

La documentation de [`execve(2)`](https://man7.org/linux/man-pages/man2/execve.2.html) décrit le remplacement du programme et l'initialisation du nouvel environnement d'exécution.

## 4.2. Le modèle classique d'un shell

Un shell qui lance une commande externe suit souvent un schéma de ce type :

```text
SHELL
  |
  | création d'un enfant
  v
PROCESSUS ENFANT
  |
  | execve()
  v
NOUVEAU PROGRAMME
  |
  v
EXÉCUTION
  |
  v
TERMINAISON
  |
  v
LE PARENT RÉCUPÈRE LE STATUT
```

Le détail varie selon le shell, le type de commande et les optimisations possibles.

Les commandes internes du shell peuvent être exécutées directement sans lancement d'un programme externe.

## 4.3. Ce que `execve()` remplace

Lorsque `execve()` réussit, le programme en cours est remplacé par le nouveau programme dans le même processus.

Le PID reste généralement celui du processus qui effectue l'opération.

Il ne faut donc pas interpréter un changement de commande avec un PID conservé comme une preuve que le processus n'a jamais été remplacé.

Certains attributs du processus sont conservés, d'autres peuvent être modifiés ou réinitialisés selon les règles de l'interface d'exécution et les attributs de sécurité.

## 4.4. Descripteurs de fichiers et `execve()`

Les descripteurs ouverts sont généralement conservés lors d'un `execve()`, sauf ceux marqués pour être fermés à l'exécution, notamment avec le mécanisme close-on-exec.

C'est important pour les redirections, les pipelines et la communication entre processus.

Une erreur de gestion des descripteurs peut entraîner :

- des fichiers restant ouverts trop longtemps ;
- des tubes dont l'extrémité d'écriture reste ouverte ;
- une commande qui attend indéfiniment une fin de fichier ;
- des ressources qui ne sont pas libérées comme prévu.

Ce type de défaut nécessite parfois un diagnostic au niveau des descripteurs et non un simple examen du PID.


# 5. Terminaison, `wait()`, zombies et processus orphelins

## 5.1. La terminaison ne supprime pas instantanément toute information

Lorsqu'un enfant termine, le noyau doit permettre à son parent de récupérer le statut de fin.

Les appels `wait()`, `waitpid()` et `waitid()` servent notamment à attendre un changement d'état d'un processus enfant et à obtenir des informations sur ce changement.

La référence [`wait(2)`](https://man7.org/linux/man-pages/man2/waitpid.2.html) détaille ces interfaces.

## 5.2. Le zombie

Un zombie est un enfant terminé dont le statut n'a pas encore été récupéré dans les conditions attendues.

Il ne s'agit pas d'un programme qui exécute encore normalement des instructions.

```text
ENFANT EN COURS D'EXÉCUTION
            |
            v
          FIN
            |
            v
STATUT À RÉCUPÉRER
            |
            v
ZOMBIE TEMPORAIRE
            |
            v
wait() / waitpid() / waitid()
            |
            v
ENTRÉE RETIRÉE
```

Un zombie persistant peut révéler un problème dans le programme parent.

La réponse appropriée consiste à examiner le parent et sa logique de récupération des enfants.

Un `SIGKILL` adressé au zombie lui-même ne remplace pas la récupération du statut.

## 5.3. Processus orphelins

Un processus orphelin continue de fonctionner alors que son parent a terminé.

Il peut être adopté par un processus approprié du système, selon l'organisation des processus et les mécanismes de supervision en place.

Un processus orphelin n'est pas automatiquement anormal.

Le problème se pose surtout lorsque l'application a besoin de son parent pour gérer correctement son cycle de vie, sa fermeture ou ses ressources.

## 5.4. Sous-récolteurs de processus

Linux fournit un mécanisme permettant à certains processus de devenir des sous-récolteurs d'orphelins, notamment par l'interface `PR_SET_CHILD_SUBREAPER` de `prctl()`.

Ce mécanisme peut être utile pour les superviseurs qui gèrent des processus descendants et doivent récupérer leur statut après la disparition d'un parent intermédiaire.

Il ne s'agit pas d'un réglage à activer au hasard dans un script shell. Son usage est normalement associé à un programme de supervision capable de gérer les statuts et le cycle de vie des descendants.

## 5.5. Pourquoi un superviseur doit gérer les enfants

Un programme qui crée des enfants doit définir une stratégie de récupération de leur statut.

Si cette gestion est absente ou incorrecte, des zombies peuvent s'accumuler.

Dans un service qui crée fréquemment des processus temporaires, cette anomalie peut devenir une fuite de ressources liée au cycle de vie.

Un diagnostic doit établir :

1. quels processus sont zombies ;
2. quels sont leurs parents ;
3. si le parent fonctionne normalement ;
4. si le problème concerne une bibliothèque, une application ou le superviseur ;
5. si une correction logicielle ou un redémarrage contrôlé est nécessaire.


# 6. Identité des processus et sécurité

## 6.1. Les identifiants de sécurité

Un processus n'est pas uniquement défini par son PID.

Linux utilise plusieurs identifiants d'utilisateur et de groupe pour déterminer les droits associés à ses opérations.

Parmi eux figurent les identifiants réels, effectifs et sauvegardés, ainsi que les identifiants de groupe correspondants.

Il faut distinguer :

- l'identité associée au lancement ;
- l'identité effective utilisée dans de nombreuses décisions de permission ;
- les groupes supplémentaires ;
- les capacités accordées au processus ;
- le contexte de sécurité supplémentaire éventuellement présent.

Les commandes d'observation peuvent fournir différentes parties de ces informations.

## 6.2. Examiner les identifiants

Pour un processus donné :

```bash
grep -E '^(Name|Pid|PPid|Uid|Gid|Groups|CapInh|CapPrm|CapEff|NoNewPrivs|Seccomp):' "/proc/PID/status"
```

Cette commande utilise un PID réel et lit les champs disponibles dans `/proc/PID/status`.

Les champs qui apparaissent dépendent du noyau et du contexte. Certaines informations peuvent être restreintes.

Les valeurs de capacités sont souvent représentées sous forme de masques. Leur interprétation nécessite la documentation des capacités Linux.

## 6.3. Pourquoi l'utilisateur effectif ne suffit-il pas ?

Un processus exécuté sous un compte privilégié peut être limité par d'autres mécanismes.

Inversement, un service exécuté sous un compte de service peut recevoir des capacités spécifiques ou accéder à des ressources par l'intermédiaire de permissions particulières.

Il faut donc éviter de résumer la sécurité d'un processus à la seule colonne `USER`.

## 6.4. Capacités Linux

Les capacités divisent certaines prérogatives traditionnellement associées au superutilisateur en catégories plus ciblées.

Cela permet de donner à un processus certaines permissions administratives sans lui accorder automatiquement toutes les possibilités de `root`.

Les capacités peuvent être observées avec des outils spécialisés ou dans les informations de `/proc`.

Pour un processus connu, si l'outil `capsh` est installé, il peut aider à examiner les capacités disponibles dans le contexte courant. L'interprétation des masques dans `/proc/PID/status` demande davantage de prudence.

Les capacités sont importantes pour les services, les conteneurs et les applications qui doivent effectuer une opération privilégiée précise.

## 6.5. `NoNewPrivs` et seccomp

Le champ `NoNewPrivs` peut indiquer qu'un processus est soumis au mécanisme `no_new_privs`.

Ce mécanisme limite certaines possibilités de gagner de nouveaux privilèges lors de futurs changements d'exécutable.

Seccomp est un mécanisme qui permet de filtrer les appels système utilisables par un processus.

Dans `/proc/PID/status`, les informations de seccomp peuvent aider à déterminer si un filtre s'applique.

La présence d'un filtre seccomp ne signifie pas automatiquement que le programme est bloqué : il faut connaître la politique appliquée et les appels qu'elle autorise.

## 6.6. Principe du moindre privilège

Un service doit recevoir uniquement les droits nécessaires à sa fonction.

Lors du diagnostic, vérifie :

- l'utilisateur et les groupes ;
- les capacités ;
- les permissions des fichiers ;
- les restrictions de l'unité ;
- les filtres d'appels système éventuels ;
- les limites de ressources ;
- les journaux de sécurité.

Une commande qui échoue peut donc être liée à une restriction de sécurité, et pas uniquement à une erreur applicative.


# 7. Identifiants, groupes, sessions et espaces de noms

## 7.1. PID, PPID, PGID et SID

Les identifiants continuent de jouer des rôles différents.

| Identifiant | Fonction |
|---|---|
| PID | Identifiant du processus |
| PPID | Identifiant de son parent |
| PGID | Groupe de processus |
| SID | Session de processus |
| TPGID | Groupe associé au premier plan d'un terminal, lorsqu'il est applicable |
| UID/GID | Identifiants de sécurité utilisateur et groupe |

Afficher ces informations :

```bash
ps -eo pid,ppid,pgid,sid,tpgid,user,stat,cmd
```

Pour un processus donné :

```bash
ps -p PID -o pid,ppid,pgid,sid,tpgid,tty,user,stat,cmd
```

Ces champs ne décrivent pas tous la même relation.

## 7.2. Les espaces de noms Linux

Les espaces de noms, ou *namespaces*, isolent certaines vues des ressources du système.

Il existe notamment des espaces de noms liés :

- aux PID ;
- aux utilisateurs ;
- au réseau ;
- aux points de montage ;
- aux noms d'hôtes ;
- aux communications interprocessus ;
- aux identifiants de temps dans les noyaux qui prennent en charge ces mécanismes.

Ils constituent des éléments importants de l'isolation des conteneurs.

## 7.3. Pourquoi les PID peuvent-ils différer entre l'hôte et un conteneur ?

Un processus peut avoir un PID différent selon l'espace de noms dans lequel il est observé.

Exemple conceptuel :

```text
HÔTE LINUX
|
+-- Processus X : PID 5200
    |
    +-- VUE DE L'ESPACE DE NOMS CONTENEUR
        |
        +-- Même processus : PID 42
```

Les valeurs sont fictives.

Cette différence ne signifie pas qu'il s'agit nécessairement de deux applications indépendantes.

Il faut distinguer le PID vu dans l'espace de noms courant des identifiants visibles depuis d'autres espaces.

## 7.4. Examiner les espaces de noms d'un processus

Pour un PID connu :

```bash
ls -l "/proc/PID/ns"
```

Les liens présentés peuvent montrer les identifiants d'espaces de noms auxquels la tâche est associée.

Pour observer les informations de statut :

```bash
grep -E '^(NSpid|NStgid|NSpgid|NSsid):' "/proc/PID/status"
```

Ces champs sont disponibles selon la version du noyau et le contexte.

Leur absence ne suffit pas à conclure qu'aucun mécanisme d'isolation n'est utilisé.

## 7.5. `nsenter` et diagnostic

`nsenter` permet d'exécuter un programme dans certains espaces de noms d'une autre tâche, si les permissions et la configuration le permettent.

Il peut être utilisé lors du diagnostic de conteneurs, mais il ne doit pas être utilisé comme une commande exploratoire sans comprendre les effets du changement de contexte.

Avant de l'employer, identifie :

- le PID cible ;
- l'espace de noms concerné ;
- les privilèges requis ;
- le programme lancé ;
- les effets sur les chemins de fichiers, le réseau et la visibilité des processus.

## 7.6. Un PID ne constitue pas une identité globale permanente

Le PID peut être limité à un espace de noms et être réutilisé après la disparition du processus.

Cela pose un problème particulier aux outils de supervision et aux programmes qui stockent des PID.

Le niveau expert doit donc connaître les solutions permettant de rattacher les opérations de contrôle à une référence stable, notamment les descripteurs de processus lorsque le noyau les prend en charge.


# 8. PIDFD : identifier un processus sans dépendre uniquement de son PID

## 8.1. Le risque de réutilisation des PID

Un PID est pratique pour l'administration, mais un PID stocké dans un fichier ou une variable n'est pas une référence permanente.

Exemple :

```text
10:00 — Processus A reçoit PID 6000
10:05 — Processus A termine
10:06 — PID 6000 est attribué à un autre processus
10:10 — Un ancien script tente de contrôler PID 6000
```

L'ancien script risque de viser une autre tâche.

Ce risque est connu sous le nom de **course liée à la réutilisation des PID**.

## 8.2. Le principe de PIDFD

Linux fournit une interface appelée *PID file descriptor*, ou PIDFD, qui permet de détenir un descripteur faisant référence à un processus particulier.

Les interfaces comprennent notamment `pidfd_open()` et `pidfd_send_signal()`.

Le descripteur représente une référence au processus, plutôt que de demander au noyau de rechercher chaque fois un numéro PID susceptible d'avoir été réutilisé.

La documentation de [`pidfd_open(2)`](https://man7.org/linux/man-pages/man2/pidfd_open.2.html) et de [`pidfd_send_signal(2)`](https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html) décrit ces mécanismes.

## 8.3. La différence conceptuelle

```text
MÉTHODE BASÉE SUR PID
|
+-- Stocker le numéro
|
+-- Le processus peut terminer
|
+-- Le numéro peut être réutilisé
|
+-- Une action tardive risque de viser une autre tâche


MÉTHODE BASÉE SUR PIDFD
|
+-- Obtenir un descripteur de processus
|
+-- Conserver la référence
|
+-- Surveiller la fin ou envoyer un signal via l'interface prévue
|
+-- Éviter la confusion créée par la réutilisation du numéro
```

Les PIDFD sont des interfaces de programmation Linux, et non de simples commandes shell universelles.

Leur disponibilité dépend de la version du noyau et des interfaces système utilisées. Le support de `pidfd_send_signal()` a été introduit à partir de Linux 5.1 ; `pidfd_open()` a été introduit plus tard, à partir de Linux 5.3.

## 8.4. Quand utiliser cette approche ?

Les PIDFD sont particulièrement pertinents pour :

- les superviseurs écrits en C ou dans des langages capables d'utiliser les interfaces appropriées ;
- les gestionnaires de processus de longue durée ;
- les outils qui surveillent plusieurs processus de façon asynchrone ;
- les programmes qui doivent éviter les erreurs de cible liées à la réutilisation des PID.

Un script Bash classique s'appuie généralement sur des PID et les commandes disponibles. Dans ce cas, une validation rigoureuse de la cible reste nécessaire, sans fournir la même garantie conceptuelle qu'une référence PIDFD conservée par le programme.

## 8.5. Pourquoi cette notion est-elle importante en expert ?

L'administration experte ne consiste pas seulement à connaître une commande `kill`.

Elle doit également comprendre les limites du modèle d'identification et les mécanismes conçus pour les éviter dans les outils de supervision.


# 9. Signaux : dispositions, masques, signaux en attente et synchronisation

## 9.1. Un signal est un mécanisme de notification

Les signaux Linux peuvent notifier un événement, interrompre un traitement, demander une terminaison ou participer au contrôle des processus.

Un processus peut, selon le signal et les possibilités de l'interface, définir un comportement particulier, ignorer certains signaux ou bloquer temporairement leur livraison.

Il faut distinguer la génération d'un signal de sa livraison effective et de l'action réalisée en conséquence.

## 9.2. Dispositions des signaux

Pour de nombreux signaux, le processus peut disposer d'un comportement par défaut ou installer un gestionnaire.

Les possibilités sont néanmoins limitées.

`SIGKILL` et `SIGSTOP` ne peuvent pas être interceptés, bloqués ni ignorés comme les signaux ordinaires.

Les dispositions exactes des autres signaux dépendent du programme.

## 9.3. Masques de signaux

Un processus ou un thread peut bloquer temporairement certains signaux.

Le signal peut alors rester en attente selon sa nature et les règles applicables.

Il existe des distinctions entre signaux dirigés vers un processus et signaux dirigés vers un thread.

Cette différence compte dans les programmes multithread, car un signal destiné à un groupe de threads n'est pas nécessairement remis au thread que le développeur avait implicitement en tête.

## 9.4. Signaux en attente

L'interface `/proc/PID/status` peut exposer des informations concernant certains masques et ensembles de signaux en attente.

Exemple :

```bash
grep -E '^(SigPnd|ShdPnd|SigBlk|SigIgn|SigCgt):' "/proc/PID/status"
```

Ces champs sont des représentations sous forme de masques. Leur décodage demande de consulter les interfaces de signaux et la documentation locale.

Une commande qui affiche un masque non nul ne suffit pas à expliquer la cause d'un retard ou d'un blocage.

## 9.5. Signaux et contrôle des tâches

Dans un terminal interactif :

- `Ctrl+C` provoque généralement un `SIGINT` vers le groupe au premier plan ;
- `Ctrl+Z` provoque généralement une demande de suspension associée à `SIGTSTP` ;
- `fg` ramène une tâche au premier plan ;
- `bg` permet de reprendre une tâche suspendue en arrière-plan.

Ces mécanismes dépendent du shell et du contrôle des tâches activé.

Un signal de terminal peut affecter plusieurs processus d'une pipeline, car le contrôle s'effectue souvent au niveau d'un groupe de processus.

## 9.6. `signalfd` et gestion des signaux

Linux fournit aussi l'interface `signalfd()`, qui permet à un programme de recevoir des informations sur certains signaux via un descripteur de fichier.

Cette approche peut faciliter l'intégration de la gestion des signaux dans une boucle d'événements utilisant notamment `poll`, `select` ou `epoll`.

Ce mécanisme relève de la programmation système avancée. Dans un script shell, il n'est généralement pas nécessaire de le mettre en œuvre directement.

## 9.7. Diagnostic d'une interruption

Lorsqu'un programme ne semble pas réagir à un signal :

1. confirme l'identité du processus ;
2. vérifie les permissions de l'appelant ;
3. distingue le signal demandé ;
4. examine l'état du processus ;
5. détermine si un gestionnaire personnalisé existe ;
6. vérifie si le processus attend dans le noyau ;
7. consulte les journaux et les traces si nécessaire.

Il ne faut pas conclure automatiquement qu'un processus « ignore les signaux » simplement parce qu'il ne disparaît pas instantanément.


# 10. Ordonnancement et politiques de priorité

## 10.1. Le rôle de l'ordonnanceur

L'ordonnanceur décide quelle tâche est exécutée sur un processeur logique et quand.

Il doit tenir compte des tâches prêtes, des priorités, des politiques applicables, de l'affinité CPU et des contraintes provenant de l'environnement.

Une charge élevée ne suffit donc pas à identifier l'origine d'un ralentissement.

## 10.2. La valeur de nice

Pour les tâches ordinaires, la valeur de nice influence la priorité relative.

```text
-20                        0                        +19
 |-------------------------|--------------------------|
Priorité relative plus     Valeur                   Priorité relative
favorable                  standard                 moins favorable
```

Un nice plus positif rend généralement une tâche moins favorisée par rapport à des tâches comparables.

Cela ne garantit pas une quantité précise de CPU et ne constitue pas un quota.

## 10.3. Examiner la priorité

```bash
ps -eo pid,ppid,user,stat,ni,pri,cls,cmd
```

Les colonnes `NI`, `PRI` et `CLS` donnent des informations sur la valeur de nice, la priorité présentée et la classe d'ordonnancement selon la version de `ps`.

Pour un processus précis :

```bash
ps -p PID -o pid,ni,pri,cls,stat,cmd
```

## 10.4. Politiques d'ordonnancement

Linux prend en charge plusieurs politiques d'ordonnancement, notamment les classes ordinaires et certaines classes temps réel.

Selon le noyau, les privilèges et la configuration, les politiques peuvent comprendre :

- `SCHED_OTHER`, souvent présenté comme `OTHER` ou une variante `NORMAL` par les outils ;
- `SCHED_BATCH` ;
- `SCHED_IDLE` ;
- `SCHED_FIFO` ;
- `SCHED_RR` ;
- `SCHED_DEADLINE` sur les configurations qui prennent en charge cette politique.

Ces politiques ne sont pas interchangeables.

Les politiques temps réel peuvent donner à certaines tâches des propriétés de planification très différentes de celles des tâches ordinaires.

## 10.5. Examiner une politique avec `chrt`

Si l'outil est installé :

```bash
chrt -p PID
```

Cette commande affiche les informations de politique et de priorité pour le PID indiqué.

Ne modifie pas la politique d'un processus système sans comprendre son rôle.

Les politiques temps réel mal configurées peuvent empêcher des tâches ordinaires de recevoir suffisamment de temps CPU.

## 10.6. `SCHED_FIFO` et `SCHED_RR`

Ces politiques relèvent de l'ordonnancement temps réel.

Une tâche temps réel peut être favorisée par rapport aux tâches ordinaires selon les règles de la politique.

Un programme qui conserve indûment l'exécution avec une politique temps réel peut provoquer une forte dégradation de la réactivité de la machine.

Les réglages temps réel nécessitent une compréhension approfondie des besoins applicatifs, des privilèges et des mécanismes de protection.

Ne les expérimente pas sur un serveur de production.

## 10.7. Affinité CPU

L'affinité CPU limite les processeurs logiques sur lesquels une tâche peut s'exécuter.

Pour observer le masque d'affinité d'un PID :

```bash
taskset -pc PID
```

Pour consulter l'architecture CPU :

```bash
lscpu
```

Une affinité restrictive peut être intentionnelle pour une application sensible à la localisation mémoire ou pour une configuration de service.

Elle peut aussi limiter inutilement les performances.

Il faut vérifier les processeurs autorisés dans le contexte réel, notamment dans un conteneur ou un groupe de contrôle.


# 11. Diagnostic avancé du CPU

## 11.1. Un processus peut-il dépasser 100 % CPU ?

Certains outils présentent l'utilisation CPU d'un processus multithread sur une échelle où un processeur logique pleinement utilisé correspond à environ 100 %.

Un processus qui exploite deux processeurs logiques peut donc apparaître autour de 200 % selon la convention de calcul.

Ce résultat ne constitue pas automatiquement une erreur.

Il faut comprendre :

- la convention de calcul de l'outil ;
- le nombre de processeurs logiques disponibles ;
- le nombre de threads actifs ;
- les limites du groupe de contrôle ;
- la période de mesure.

## 11.2. Identifier les principaux consommateurs

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 20
```

Cette commande est utile pour un premier classement.

Elle ne démontre pas à elle seule la consommation exacte au moment précis de l'exécution ni la cause de cette consommation.

## 11.3. Comparer les mesures temporelles

Si `sysstat` est installé :

```bash
pidstat -u -p PID 1 10
```

Cette commande demande des relevés CPU répétés pour le PID concerné.

Les intervalles successifs sont plus utiles qu'un seul chiffre lorsqu'il faut identifier une charge soutenue.

Pour une application multithread :

```bash
pidstat -t -p PID 1 10
```

Les options exactes doivent être vérifiées dans `man pidstat` sur le système utilisé.

## 11.4. Utilisation CPU utilisateur et noyau

Le temps CPU associé à une tâche peut être consommé :

- en espace utilisateur, lors de l'exécution du code de l'application ;
- en espace noyau, lors de l'exécution de code du noyau pour le compte de la tâche.

Une forte activité en espace utilisateur peut orienter vers un calcul, une boucle ou un traitement intensif.

Une forte activité en espace noyau peut orienter vers des appels système fréquents, des opérations d'entrée-sortie, des changements de contexte ou certains traitements du noyau.

Ce ne sont que des orientations : il faut confirmer la cause avec une trace ou des mesures supplémentaires.

## 11.5. Changements de contexte

Un changement de contexte permet au noyau de passer d'une tâche à une autre.

Des changements de contexte nombreux peuvent être normaux pour certaines charges de travail.

Ils peuvent aussi être associés à :

- un grand nombre de threads actifs ;
- des synchronisations fréquentes ;
- des communications entre processus ;
- des réveils répétés ;
- des applications fortement concurrentes.

La présence d'un nombre élevé ne prouve pas qu'un problème existe. Elle doit être interprétée avec la latence et le débit de l'application.

## 11.6. Profilage avec `perf stat`

Si `perf` est installé et autorisé :

```bash
perf stat -- timeout 5s sha256sum /dev/zero
```

Cette commande est un exemple de laboratoire. Elle exécute un calcul pendant une durée limitée et collecte des statistiques de performance selon les événements disponibles.

`perf stat` peut compter notamment certains événements du processeur, les cycles, les instructions et les défauts de page, en fonction de l'architecture et des permissions.

Les événements pris en charge sont spécifiques au système. Consulte :

```bash
perf list
```

Un événement non pris en charge ou non autorisé peut échouer.

## 11.7. Interpréter les compteurs

Le nombre d'instructions exécutées n'est pas une mesure directe de la qualité du programme.

Les cycles CPU, les instructions, les défauts de cache, les défauts de page et les changements de contexte mesurent des phénomènes différents.

Un ratio tel que le nombre d'instructions par cycle peut aider à explorer certaines caractéristiques du calcul, mais il doit être interprété avec l'architecture, le code, les événements effectivement mesurés et le contexte de la charge.

La documentation de [`perf stat`](https://man7.org/linux/man-pages/man1/perf-stat.1.html) décrit les possibilités et les limites de cet outil.


# 12. Mémoire des processus : VIRT, RSS, PSS et fautes de page

## 12.1. Mémoire virtuelle et mémoire résidente

Un processus possède un espace d'adressage virtuel.

Cet espace n'est pas équivalent à la quantité de mémoire physique qu'il consomme réellement.

Les notions suivantes doivent être distinguées :

- **VIRT / VSZ :** quantité de mémoire virtuelle associée au processus selon les conventions de l'outil ;
- **RSS :** mémoire résidente du processus ;
- **PSS :** mémoire proportionnellement attribuée au processus, en tenant compte des pages partagées ;
- **Swap :** pages qui peuvent avoir été transférées dans l'espace d'échange ;
- **Pages partagées :** pages utilisées par plusieurs processus ou mappages ;
- **Pages privées :** pages attribuées plus spécifiquement à un processus.

## 12.2. Pourquoi RSS peut-il être trompeur ?

Lorsque plusieurs processus utilisent des pages partagées, la somme de leurs RSS peut compter ces pages plusieurs fois.

Cela signifie que la somme des RSS de tous les processus n'est pas une mesure exacte de la mémoire physique totale consommée.

PSS attribue une fraction des pages partagées à chaque utilisateur de ces pages et peut aider à comparer la consommation mémoire réelle entre des processus.

## 12.3. Examiner `smaps_rollup`

Sur les systèmes qui exposent ce fichier :

```bash
cat /proc/PID/smaps_rollup
```

Il fournit un résumé de plusieurs statistiques de mémoire d'un processus.

L'accès peut être restreint. Certaines informations peuvent ne pas être disponibles selon la version du noyau ou la configuration de sécurité.

Le PSS est particulièrement utile pour examiner un ensemble de processus qui partagent des bibliothèques ou d'autres pages mémoire.

## 12.4. Défauts de page

Une faute de page se produit lorsque l'accès à une adresse mémoire nécessite une intervention du mécanisme de gestion mémoire.

Toutes les fautes de page ne signifient pas que le programme a une erreur.

Certaines sont résolues normalement, par exemple lorsqu'une page doit être chargée ou lorsqu'un mécanisme copy-on-write doit créer une copie.

Il faut distinguer les défauts qui se résolvent rapidement de ceux qui nécessitent une opération plus coûteuse.

## 12.5. Observer les statistiques mémoire

Avec `pidstat` :

```bash
pidstat -r -p PID 1 10
```

Pour un relevé global :

```bash
vmstat 1 10
```

Pour une vue générale de la mémoire :

```bash
free -h
```

Un diagnostic mémoire doit rapprocher la mémoire disponible, le swap, les défauts de page, les mesures du processus et les éventuelles limites de ressources.

## 12.6. Croissance mémoire et fuite

Une consommation qui augmente pendant une charge peut être normale.

Exemples :

- cache de l'application qui se remplit ;
- accumulation temporaire de requêtes ;
- mise en mémoire de données attendues ;
- préchargement de ressources.

Une fuite mémoire est une situation dans laquelle la mémoire demeure retenue ou augmente de manière anormale par rapport au comportement attendu.

Pour confirmer cette hypothèse, mesure l'évolution sous une charge comparable et examine les mécanismes d'allocation de l'application si nécessaire.


# 13. Pression mémoire et OOM killer

## 13.1. Comprendre l'épuisement mémoire

Lorsque les ressources mémoire deviennent insuffisantes, le noyau peut récupérer des pages, utiliser le swap lorsque disponible, ralentir des tâches ou, dans certaines situations, déclencher un mécanisme OOM (*Out Of Memory*).

Dans un environnement utilisant des cgroups, un événement d'épuisement peut être limité à un groupe de contrôle.

Le problème ne concerne donc pas nécessairement l'ensemble de la machine.

## 13.2. Vérifier les messages liés à l'OOM

Consulte les journaux du noyau :

```bash
journalctl -k --since "2 hours ago" --no-pager
```

Recherche les événements associés à l'épuisement mémoire, aux limites de cgroups et aux processus terminés par le noyau.

Les messages présents dépendent du noyau, de la configuration de journalisation et des événements qui se sont produits.

L'absence d'un message visible ne prouve pas qu'aucune limite n'a été atteinte.

## 13.3. `oom_score` et `oom_score_adj`

Dans `/proc/PID/status`, certaines informations permettent d'examiner le contexte de sélection des processus par l'OOM killer.

Tu peux consulter :

```bash
cat /proc/PID/oom_score
```

et :

```bash
cat /proc/PID/oom_score_adj
```

Ces fichiers ne constituent pas des scores de qualité applicative.

`oom_score_adj` influence la sélection du processus dans certains scénarios d'épuisement mémoire. Ses valeurs peuvent être ajustées selon les permissions et les règles de sécurité.

**Ne modifie pas `oom_score_adj` sans comprendre les conséquences.** Protéger arbitrairement un processus de l'OOM killer peut déplacer le risque vers d'autres composants plus importants.

## 13.4. Distinguer OOM système et OOM de cgroup

Un processus peut être terminé parce que :

- la machine entière manque de mémoire ;
- le cgroup du service atteint sa limite ;
- un conteneur possède une limite mémoire ;
- un groupe de contrôle enfant est soumis à une contrainte spécifique.

L'examen des journaux, des limites et des compteurs de cgroups aide à distinguer ces situations.

## 13.5. Contrôler les événements mémoire dans cgroups v2

Dans un groupe de contrôle utilisant le contrôleur mémoire, certains fichiers peuvent présenter les compteurs d'événements.

Par exemple :

```text
memory.events
memory.current
memory.high
memory.max
```

Les fichiers réellement présents dépendent des contrôleurs activés et de la hiérarchie utilisée.

Une lecture possible, après identification du chemin de cgroup, est :

```bash
cat /sys/fs/cgroup/CHEMIN_DU_CGROUP/memory.events
```

Remplace le chemin par celui du groupe de contrôle réel. Ne suppose pas qu'un répertoire portant un nom prédéfini existe sur toutes les machines.


# 14. Descripteurs, fichiers ouverts et fuites de ressources

## 14.1. Un processus peut épuiser des ressources sans consommer beaucoup de CPU

Des applications peuvent rencontrer des problèmes après avoir ouvert trop de fichiers, sockets ou autres descripteurs.

Les symptômes peuvent comprendre :

- `Too many open files` ;
- échec de création de sockets ;
- impossibilité d'ouvrir un journal ;
- difficulté à accepter de nouvelles connexions ;
- consommation croissante de descripteurs.

## 14.2. Compter les descripteurs

Pour un PID :

```bash
find "/proc/PID/fd" -maxdepth 1 -type l | wc -l
```

La commande compte les liens symboliques visibles dans le répertoire `fd`. Elle doit être exécutée avec un PID réel et peut échouer si le processus disparaît pendant l'opération ou si les permissions sont insuffisantes.

Pour examiner les descripteurs :

```bash
ls -l /proc/PID/fd
```

Avec `lsof`, si l'outil est installé :

```bash
lsof -nP -p PID
```

Les options exactes et les possibilités de filtrage dépendent de la version installée.

## 14.3. Limites des fichiers ouverts

Dans le shell courant :

```bash
ulimit -n
```

Cette commande affiche la limite pertinente pour le nombre de descripteurs de fichiers ouverts dans le contexte du shell.

Elle ne prouve pas que tous les processus ont la même limite.

Pour un processus particulier, les limites peuvent être affichées via :

```bash
cat /proc/PID/limits
```

Cela permet de comparer les limites du processus au nombre de ressources effectivement utilisées.

## 14.4. Descripteur ou fichier : une différence importante

La suppression de l'entrée d'un fichier dans le système de fichiers ne signifie pas nécessairement que le contenu est immédiatement libéré.

Un processus peut continuer à détenir un descripteur vers un fichier dont le nom a été supprimé.

Cette situation peut être particulièrement importante pour les journaux.

Le diagnostic doit alors établir :

1. quel fichier est encore ouvert ;
2. quel processus le détient ;
3. pourquoi il reste ouvert ;
4. quelle procédure permet de fermer ou de faire tourner ce journal ;
5. si un redémarrage est réellement nécessaire.

## 14.5. Tubes et fins de fichier

Pour un tube ou un mécanisme de communication similaire, la fermeture des extrémités ouvertes influence la détection de la fin des données.

Si un processus conserve inutilement une extrémité d'écriture, un lecteur peut attendre plus longtemps que prévu la fin du flux.

Ce type de problème ne se résout pas nécessairement en examinant la mémoire ou le CPU. Il peut être nécessaire de comprendre le graphe des communications entre processus et leurs descripteurs.


# 15. Processus bloqués, attentes noyau et interblocages

## 15.1. État et progression ne sont pas synonymes

Un processus peut être dans un état apparemment normal sans progresser vers son objectif.

Par exemple :

- attente d'une réponse réseau ;
- attente d'un verrou ;
- attente d'un enfant ;
- attente d'une opération de stockage ;
- boucle active qui consomme du CPU sans avancer utilement ;
- attente sur un événement qui ne se produit plus.

L'état visible du processus n'explique pas, à lui seul, pourquoi l'application est lente.

## 15.2. Examiner `wchan`

Pour un PID connu :

```bash
ps -p PID -o pid,ppid,stat,wchan:32,etime,cmd
```

`wchan` peut donner une indication sur le point d'attente noyau lorsqu'il est disponible.

Le nom affiché n'est pas une preuve suffisante. Il doit être rapproché du code, de la configuration, des journaux et d'autres mesures.

## 15.3. Plusieurs processus en attente

Si plusieurs processus attendent au même endroit, cela peut être un indice d'une dépendance commune.

Exemples :

- plusieurs travailleurs attendent une base de données ;
- un groupe de processus attend la même ressource d'entrée-sortie ;
- plusieurs threads attendent un même verrou ;
- un service attend une dépendance réseau.

Le diagnostic doit examiner les relations entre les processus et les ressources qu'ils utilisent.

## 15.4. Interblocage et attente

Un interblocage (*deadlock*) peut se produire lorsque plusieurs opérations attendent mutuellement des ressources que les autres détiennent.

Ce n'est pas nécessairement visible sous la forme d'une forte consommation CPU.

```text
THREAD A
détient le verrou 1
attend le verrou 2
         |
         v
THREAD B
détient le verrou 2
attend le verrou 1
         |
         v
INTERBLOCAGE
```

Ce schéma est illustratif.

Le diagnostic d'un véritable interblocage peut nécessiter une trace des threads, une analyse de l'application ou un outil de débogage.

## 15.5. Débogage et inspection des piles

Dans certains environnements, `gdb` peut examiner les piles d'exécution d'un processus, avec les permissions et les symboles nécessaires.

Exemple de forme de commande pour un environnement de laboratoire :

```bash
gdb -p PID
```

L'attachement d'un débogueur peut suspendre brièvement la cible ou perturber son fonctionnement.

**Ne l'utilise pas sans autorisation sur un service sensible ou critique.**

La disponibilité des symboles et les politiques de sécurité déterminent le niveau d'information réellement accessible.

## 15.6. Quand utiliser un outil de trace ?

Si le processus est présent mais semble attendre, une trace d'appels système peut révéler qu'il attend une lecture, un verrou noyau exposé par une interface, un descripteur ou un autre événement.

L'outil doit toutefois être choisi selon la question :

- `strace` pour observer les appels système et les signaux ;
- `perf` pour profiler l'exécution et certains événements matériels ;
- `bpftrace` pour observer dynamiquement des événements pris en charge ;
- un débogueur pour examiner les piles et l'état interne du programme, lorsque cela est possible.


# 16. Diagnostic des appels système avec `strace`

## 16.1. À quoi sert `strace` ?

`strace` observe les appels système et les signaux associés à un processus.

Il est particulièrement utile lorsque l'on cherche à comprendre ce qu'un programme demande au noyau et pourquoi il semble attendre ou échouer.

La documentation de [`strace(1)`](https://man7.org/linux/man-pages/man1/strace.1.html) décrit les options de suivi, les filtres et les modes de sortie.

## 16.2. Observer une commande de test

Pour tracer une commande simple :

```bash
strace -f -o /tmp/trace-ls.log ls /tmp
```

Cette commande enregistre les appels système dans un fichier de laboratoire.

`-f` demande le suivi des processus descendants selon les possibilités de l'outil.

Le contenu du fichier peut révéler des chemins, des arguments ou d'autres informations internes. Le fichier ne doit pas être publié sans contrôle.

## 16.3. Tracer un processus existant

Pour s'attacher à un PID :

```bash
strace -p PID
```

Cette opération demande des permissions appropriées et peut être restreinte par la configuration du système.

L'attachement peut perturber temporairement le comportement de la cible, notamment si elle est sensible à la latence.

Il est important de limiter la durée d'observation et de connaître les effets de l'outil avant son utilisation sur un service critique.

## 16.4. Mesurer la durée des appels système

Une option fréquemment utile est :

```bash
strace -ttT -p PID
```

La sortie peut inclure des horodatages et la durée de certains appels.

Cela aide à repérer des appels système qui passent beaucoup de temps à attendre.

Cependant, la durée d'un appel ne prouve pas à elle seule la cause de l'attente. Il faut comprendre l'appel, son descripteur, les paramètres et le contexte.

## 16.5. Filtrer les appels intéressants

Pour réduire le volume de données, `strace` permet de filtrer certaines catégories d'appels.

Exemple sur une commande de laboratoire :

```bash
strace -e trace=openat,read,write,close -o /tmp/trace-fichiers.log ls /tmp
```

Les appels sélectionnés donnent une vue plus ciblée des opérations sur les fichiers et les descripteurs.

Les catégories et options doivent être vérifiées dans la documentation locale.

## 16.6. Résumé statistique avec `-c`

```bash
strace -c -f ls /tmp
```

Cette forme produit un résumé statistique des appels observés pendant l'exécution de la commande.

Elle peut aider à repérer quels appels système contribuent au volume d'activité observé.

Ce résumé n'est pas un profilage complet du temps CPU dans les fonctions internes du programme.

## 16.7. Cas d'utilisation de `strace`

### Problème : ouverture de fichier qui échoue

La trace peut montrer un appel tel que `openat()` avec un code d'erreur.

L'investigation doit alors vérifier le chemin, les permissions, les espaces de noms de montage et les fichiers concernés.

### Problème : processus qui attend

La trace peut montrer un appel qui bloque ou une opération d'attente répétée.

Il faut alors examiner la ressource associée.

### Problème : création d'enfants

Le suivi de la création et de l'exécution des processus peut aider à comprendre la manière dont une commande lance d'autres programmes.

### Précaution

Une trace volumineuse peut ralentir la cible, produire beaucoup de données et exposer des informations sensibles. Il faut limiter le périmètre et la durée d'observation.


# 17. Profilage avec `perf`

## 17.1. `perf` : une famille d'outils

`perf` regroupe différents mécanismes de mesure et de profilage des performances Linux.

Il peut utiliser des compteurs matériels, des événements logiciels et d'autres sources disponibles sur la machine.

Les possibilités exactes dépendent de l'architecture, du noyau, des permissions et de la configuration.

## 17.2. Lister les événements

```bash
perf list
```

Cette commande présente les événements disponibles dans l'environnement.

Tous les événements d'une architecture ne sont pas disponibles sur une autre.

Il est donc préférable de sélectionner des événements réellement pris en charge plutôt que de copier une liste arbitraire depuis un autre système.

## 17.3. Compter les événements

```bash
perf stat -- timeout 5s sha256sum /dev/zero
```

Cet exemple lance un calcul de durée limitée et collecte des statistiques.

Pour analyser une commande existante, il faut choisir un scénario reproductible et tenir compte de la charge introduite par la mesure elle-même.

## 17.4. Profiler une commande

Pour enregistrer un profil d'une commande de laboratoire :

```bash
perf record -g -- timeout 5s sha256sum /dev/zero
```

Puis :

```bash
perf report
```

`perf record` enregistre un profil. `perf report` permet d'examiner les résultats.

Les options et la qualité des traces de pile dépendent de la configuration et des symboles disponibles.

La documentation de [`perf record`](https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/perf-record.txt) décrit l'enregistrement du profil.

## 17.5. Ce que montre le profil

Un profil peut aider à identifier les fonctions ou zones de code associées à une part importante de l'exécution observée.

Il faut distinguer :

- le temps CPU échantillonné ;
- le temps passé en attente ;
- les appels système ;
- les défauts mémoire ;
- les événements matériels disponibles ;
- les pertes de données ou restrictions de l'outil.

Un profil CPU ne suffit pas à expliquer une latence provoquée par une longue attente réseau ou disque.

## 17.6. Permissions et sécurité

Sur certains systèmes, les événements disponibles pour `perf` sont limités par une configuration de sécurité.

Une collecte globale ou l'observation d'autres utilisateurs peut exiger des privilèges supplémentaires.

N'assouplis pas globalement les restrictions de profilage sans comprendre le risque. Les traces de performance peuvent révéler des informations sur l'exécution et les charges de travail.

## 17.7. Différence entre `strace` et `perf`

| Besoin | Outil privilégié |
|---|---|
| Voir les appels système et leurs erreurs | `strace` |
| Mesurer le temps d'exécution d'appels observés | `strace -T` |
| Compter des événements et des cycles | `perf stat` |
| Profiler les zones de code actives | `perf record` et `perf report` |
| Étudier des événements dynamiques plus spécifiques | `bpftrace`, si disponible et autorisé |
| Examiner les piles internes du programme | Débogueur approprié, par exemple `gdb` |

Ces outils sont complémentaires et n'ont pas la même portée.


# 18. Traces dynamiques et eBPF avec `bpftrace`

## 18.1. Pourquoi eBPF ?

eBPF permet d'observer certains événements système et d'appliquer des programmes d'observation dans les limites prévues par le noyau et ses mécanismes de sécurité.

`bpftrace` est un outil qui facilite l'écriture de scripts de traçage pour les systèmes compatibles.

Le support des sondes et des champs disponibles dépend du noyau, de sa configuration et de la version de `bpftrace`.

La documentation officielle est disponible sur [bpftrace.org](https://bpftrace.org/docs/).

## 18.2. Premier exemple : observer les créations de processus

Les installations de `bpftrace` peuvent exposer des tracepoints liés aux événements de création de processus.

Pour découvrir les sondes disponibles :

```bash
sudo bpftrace -l 'tracepoint:sched:*'
```

Cette commande liste les sondes dont le nom correspond au motif, si l'accès est disponible.

La sortie varie selon le système. Il faut identifier une sonde réellement présente avant d'écrire un script qui dépend de ses champs.

## 18.3. Exemple de script d'observation

Le script suivant illustre le principe d'un compteur de créations de processus par nom de commande.

Il suppose que le tracepoint `sched:sched_process_fork` et les champs présentés dans cet exemple sont disponibles dans l'environnement.

```bpftrace
tracepoint:sched:sched_process_fork
{
    @[comm] = count();
}

interval:s:10
{
    print(@);
    clear(@);
}
```

Enregistrer le contenu dans un fichier de laboratoire tel que `forks.bt`, puis exécuter :

```bash
sudo bpftrace forks.bt
```

Le script compte les événements de création observés pendant l'intervalle. Il ne mesure pas nécessairement le nombre de processus encore présents à la fin de la période.

Selon l'environnement, il peut être nécessaire d'adapter les champs pour distinguer le processus parent, le processus enfant et les informations souhaitées.

## 18.4. Pourquoi vérifier les tracepoints ?

Les noms des tracepoints et leurs champs dépendent de la version et de la configuration du noyau.

Avant d'écrire une sonde, il faut consulter les événements disponibles et leur format :

```bash
sudo bpftrace -lv 'tracepoint:sched:sched_process_fork'
```

Si l'option ou le format diffère selon la version de l'outil, consulte la documentation locale.

Ne suppose pas que tous les exemples de scripts eBPF fonctionnent identiquement sur chaque distribution.

## 18.5. Limites de l'observation

Une trace ne fournit pas automatiquement une explication causale.

Un événement fréquent peut être normal pour la charge observée.

L'observation doit être ciblée, limitée dans le temps et associée à une hypothèse précise.

Les programmes eBPF sont soumis à des restrictions et contrôles. L'accès peut être limité par les permissions ou la politique de sécurité du système.

Évite de lancer des collectes globales coûteuses sur un serveur chargé sans mesurer leur impact.


# 19. Groupes de contrôle Linux : cgroups v2

## 19.1. Pourquoi les cgroups sont-ils importants ?

Les groupes de contrôle, ou **cgroups**, organisent des processus en hiérarchies afin de gérer et de comptabiliser certaines ressources.

La documentation officielle du noyau décrit l'interface [cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html).

Les cgroups sont notamment utilisés par les conteneurs, `systemd` et d'autres outils d'administration.

## 19.2. Différence entre PID et cgroup

Un PID identifie une tâche.

Un cgroup regroupe les tâches relevant d'une même unité ou d'une même frontière de gestion des ressources.

```text
GROUPE DE CONTRÔLE DU SERVICE
|
+-- Processus principal
|
+-- Processus enfants
|
+-- Autres tâches associées
|
+-- Threads relevant du groupe
```

Les relations détaillées dépendent de la hiérarchie, de l'unité et de l'environnement.

L'étude d'un seul PID peut donc être insuffisante pour diagnostiquer un service soumis à une limite de ressources.

## 19.3. Vérifier la version des cgroups

La version et la hiérarchie actives peuvent être déterminées en inspectant les montages et la configuration du système.

```bash
findmnt -t cgroup,cgroup2
```

Une hiérarchie unifiée `cgroup2` est couramment utilisée sur les distributions modernes, mais les configurations anciennes ou particulières peuvent encore comporter une hiérarchie cgroup v1.

Il faut examiner la configuration réelle avant d'utiliser des chemins ou des contrôleurs spécifiques.

## 19.4. Trouver le cgroup d'un service

Pour un service géré par `systemd` :

```bash
systemctl show nom.service -p ControlGroup
```

La propriété fournit le chemin du groupe de contrôle associé à l'unité, lorsque cette information est disponible.

Sur une installation utilisant cgroup v2 montée sous `/sys/fs/cgroup`, les fichiers de cette hiérarchie peuvent être consultés à partir du chemin retourné.

Exemple de procédure :

```bash
CGROUP=$(systemctl show --value -p ControlGroup nom.service)

printf 'Cgroup : %s\n' "$CGROUP"
```

Vérifie d'abord que le chemin n'est pas vide et que le répertoire existe avant de lire ses fichiers.

## 19.5. Contrôleur CPU

Les cgroups v2 peuvent exposer des fichiers comme :

```text
cpu.stat
cpu.max
cpu.weight
```

Leur présence dépend des contrôleurs activés.

- `cpu.stat` fournit des statistiques d'utilisation et, selon les cas, de limitation ;
- `cpu.max` représente un quota CPU dans les configurations compatibles ;
- `cpu.weight` sert à répartir la priorité relative CPU entre des groupes de contrôle concurrents.

Un processus peut rencontrer une limitation CPU locale même lorsque la machine dispose de capacité inutilisée ailleurs.

## 19.6. Contrôleur mémoire

Les fichiers courants de cgroup v2 comprennent, selon les contrôleurs disponibles :

```text
memory.current
memory.high
memory.max
memory.events
memory.stat
```

Ces fichiers permettent de consulter la mémoire attribuée au groupe, ses limites, certains événements et une ventilation des statistiques.

Ils sont utiles pour déterminer si la pression mémoire concerne un service, un conteneur ou le système entier.

## 19.7. Contrôleur des tâches

Le contrôleur `pids` permet de limiter le nombre de tâches présentes dans un cgroup.

Les fichiers peuvent notamment inclure :

```text
pids.current
pids.max
pids.events
```

Une limite trop basse peut empêcher une application de créer de nouveaux processus ou threads.

Lorsque la création de tâches échoue, cette piste doit être examinée avant de conclure à un manque de CPU ou de mémoire.

## 19.8. Lire les compteurs sans modifier les ressources

Après avoir identifié le chemin exact du cgroup et vérifié l'accès :

```bash
cat "/sys/fs/cgroup${CGROUP}/cpu.stat"
```

Et, si les fichiers sont présents :

```bash
cat "/sys/fs/cgroup${CGROUP}/memory.events"
```

```bash
cat "/sys/fs/cgroup${CGROUP}/pids.current"
```

Ces commandes sont des exemples pour une hiérarchie cgroup v2 montée sous `/sys/fs/cgroup`.

**Ne copie pas de valeurs d'écriture dans les fichiers de cgroup sur un système de production sans avoir identifié la hiérarchie et compris les conséquences.** La modification des fichiers de contrôle peut affecter directement les processus.

## 19.9. Limites hiérarchiques

Les limites peuvent s'appliquer à plusieurs niveaux.

Un service peut dépendre d'une slice ou d'un groupe parent qui impose sa propre contrainte.

Une limite effective peut donc être plus restrictive que celle visible dans une seule unité.

Pour un diagnostic complet, examine les propriétés du service et les limites des groupes parents quand cela est pertinent.


# 20. Pression système avec PSI

## 20.1. Pourquoi la pression est-elle importante ?

Une ressource peut être consommée sans que tous les processus deviennent nécessairement lents.

La **Pressure Stall Information**, ou PSI, vise à mesurer l'impact de la contention sur les tâches.

La documentation officielle du noyau se trouve dans [PSI — Pressure Stall Information](https://www.kernel.org/doc/html/latest/accounting/psi.html).

La PSI aide à déterminer si les tâches subissent une attente significative liée au CPU, à la mémoire ou aux entrées-sorties.

## 20.2. Lire la pression globale

Les fichiers peuvent inclure :

```text
/proc/pressure/cpu
/proc/pressure/memory
/proc/pressure/io
```

Pour examiner la pression mémoire :

```bash
cat /proc/pressure/memory
```

Pour examiner le CPU :

```bash
cat /proc/pressure/cpu
```

Pour les entrées-sorties :

```bash
cat /proc/pressure/io
```

La disponibilité de PSI dépend de la version et de la configuration du noyau.

## 20.3. Comprendre `some` et `full`

Les lignes PSI comprennent généralement des indicateurs tels que `some` et, lorsqu'il est pris en charge pour la ressource concernée, `full`.

- `some` représente le temps durant lequel au moins certaines tâches concernées ont été bloquées ou retardées par la contention de la ressource ;
- `full` représente une forme plus sévère de pression, lorsque toutes les tâches non inactives concernées sont simultanément bloquées selon les règles de la métrique.

Les champs `avg10`, `avg60` et `avg300` correspondent à des moyennes sur différentes fenêtres temporelles.

`total` exprime un compteur de temps cumulé dans l'unité définie par l'interface.

Il faut lire les unités et les définitions officielles avant d'écrire un système d'alerte.

## 20.4. Pourquoi PSI apporte-t-elle une information différente ?

Un CPU peut être très occupé tout en exécutant efficacement le travail attendu.

La PSI cherche à quantifier l'effet de la contention sur les tâches.

De même, une machine peut conserver un peu de mémoire disponible tout en subissant une pression mémoire significative, si les tâches passent beaucoup de temps à attendre la récupération de pages ou d'autres opérations associées.

PSI complète les outils de consommation, elle ne les remplace pas.

## 20.5. PSI et diagnostic du service

Si une application devient lente, compare :

1. le temps de réponse ;
2. l'utilisation CPU ;
3. la pression CPU ;
4. la pression mémoire ;
5. la pression d'entrée-sortie ;
6. les limites du cgroup ;
7. les journaux du service.

Une pression élevée peut aider à orienter l'investigation, mais il faut encore identifier la ressource concernée et comprendre la charge applicative.

Ne définis pas des seuils d'alerte universels sans données de référence pour ton environnement.


# 21. Gestion experte des services `systemd`

## 21.1. Processus principal et cycle de vie du service

Un service `systemd` ne se résume pas à un PID.

Son unité peut déclarer son type, son mode de lancement, ses dépendances, ses délais, ses limites de ressources et sa politique de redémarrage.

Pour examiner une unité :

```bash
systemctl cat nom.service
```

Pour consulter ses propriétés :

```bash
systemctl show nom.service
```

Ces commandes aident à relier les symptômes du processus à la configuration du gestionnaire.

## 21.2. Types de service

Selon son type, une unité peut décrire différents modes de lancement, par exemple :

- `simple` ;
- `exec` ;
- `forking` ;
- `oneshot` ;
- `notify`.

Il faut consulter la documentation de `systemd.service` pour comprendre les exigences propres à chaque type.

Un service qui lance un programme en arrière-plan peut nécessiter un modèle d'unité différent d'un programme qui reste au premier plan et utilise un mécanisme de notification.

## 21.3. Redémarrage automatique

Une unité peut comporter une politique `Restart=`.

Cette politique peut provoquer un redémarrage après certaines terminaisons.

Il faut donc comprendre la configuration avant d'interpréter un PID qui réapparaît.

Le service peut être actif, en train de redémarrer ou soumis à une limite de tentatives selon sa configuration.

## 21.4. Délais d'arrêt

Un arrêt de service peut comporter un délai permettant au programme de terminer son travail avant que le mécanisme d'arrêt plus forcé ne s'applique.

La propriété `TimeoutStopSec=` est pertinente dans la configuration des services.

Il faut comprendre le protocole d'arrêt de l'application avant de modifier ce délai.

Un délai trop court peut interrompre des opérations légitimes ; un délai trop long peut ralentir les procédures de maintenance.

## 21.5. `KillMode=`

La politique de terminaison détermine la façon dont les processus de l'unité sont traités lors de certaines opérations d'arrêt.

Le comportement du groupe de contrôle est particulièrement important, car une unité peut comprendre plusieurs processus.

La valeur effective doit être examinée dans la configuration de l'unité. Il ne faut pas supposer que chaque service possède exactement le même modèle de processus.

## 21.6. Lire les journaux du service

```bash
journalctl -u nom.service --since "1 hour ago" --no-pager
```

Compare les messages à l'heure des mesures et aux événements de redémarrage.

Une chronologie de qualité permet de déterminer si un processus a échoué avant l'indisponibilité, si une action de maintenance a précédé le problème ou si le gestionnaire a déclenché un redémarrage.

## 21.7. Limites de ressources d'une unité

Les propriétés de contrôle de ressources peuvent être examinées avec :

```bash
systemctl show nom.service -p CPUQuotaPerSecUSec -p CPUWeight -p MemoryHigh -p MemoryMax -p TasksMax
```

Les propriétés disponibles et leur présentation dépendent de `systemd` et de la configuration.

La documentation de référence est [systemd.resource-control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html).

## 21.8. Pourquoi le statut actif n'est-il pas suffisant ?

Un service peut être considéré actif par le gestionnaire tout en subissant :

- un problème applicatif ;
- une dépendance indisponible ;
- une saturation des ressources ;
- une erreur dans le traitement des requêtes ;
- une limite de capacité ;
- une file de requêtes trop longue.

Le statut du service doit donc être complété par une vérification fonctionnelle et les mesures nécessaires.


# 22. Sécurité des processus, capacités et isolation

## 22.1. L'identification avant l'action

Une action d'administration doit être liée à une cible clairement identifiée.

Avant un signal :

```bash
ps -p PID -o pid,ppid,user,stat,lstart,etime,cmd
```

Si la cible est un service, examiner aussi l'unité.

Si elle est dans un conteneur, confirmer l'espace de noms pertinent et vérifier si l'identifiant provient de l'hôte ou du conteneur.

## 22.2. Privilèges minimaux

Les commandes administratives doivent utiliser les privilèges nécessaires, sans ajouter inutilement des droits globaux.

Les capacités Linux, les utilisateurs de service, les groupes et les restrictions d'unité peuvent fournir une sécurité plus précise que l'exécution systématique sous `root`.

## 22.3. Ne pas transformer le diagnostic en modification automatique

Les outils d'observation peuvent produire des informations sensibles.

Une politique de sécurité doit prendre en compte :

- les permissions des journaux ;
- les chemins de fichiers ;
- les arguments de commande ;
- les données d'environnement ;
- les résultats de `strace` ou `perf` ;
- les traces produites par les outils dynamiques.

Les fichiers de diagnostic doivent être stockés dans un emplacement protégé et conservés pendant une durée adaptée.

## 22.4. Les risques des signaux de groupe

Un signal ciblant un groupe peut affecter plusieurs processus.

Avant d'utiliser une opération sur un PGID :

1. identifie le groupe ;
2. vérifie ses membres ;
3. confirme qu'ils peuvent être arrêtés ensemble ;
4. vérifie les permissions ;
5. privilégie une opération plus ciblée si elle suffit.

Le fait qu'une commande syntaxiquement correcte s'exécute sans erreur n'indique pas que sa portée est correcte.

## 22.5. Éviter les scripts de correction trop agressifs

Un script qui tue automatiquement les processus dépassant un seuil CPU peut interrompre des traitements normaux.

Un script qui redémarre un service à chaque erreur peut créer une boucle de redémarrages et empêcher la collecte d'indices.

La supervision doit distinguer :

- la collecte ;
- l'alerte ;
- la décision ;
- l'action ;
- la vérification après action.

Les actions automatiques doivent être justifiées par les objectifs de service, testées et documentées.


# 23. Diagnostic des conteneurs et environnements isolés

## 23.1. Le processus vu depuis l'hôte et depuis le conteneur

Un conteneur peut exposer une vue différente des processus en raison des espaces de noms.

Le PID principal d'une application dans le conteneur n'est pas forcément égal au PID visible sur l'hôte.

La relation doit être vérifiée dans le contexte réel.

## 23.2. Cgroups et quotas

Un conteneur peut être soumis à :

- une limite CPU ;
- une limite mémoire ;
- une limite de tâches ;
- une contrainte d'affinité ;
- d'autres restrictions selon son environnement.

Un service peut donc être ralenti même si la machine hôte semble disposer de ressources disponibles.

## 23.3. Mémoire globale et mémoire du conteneur

La consommation mémoire de la machine et celle d'un conteneur ne représentent pas la même chose.

Une limite de cgroup peut être atteinte avant que le système hôte manque globalement de mémoire.

Il faut examiner les compteurs et limites du cgroup pertinent.

## 23.4. Diagnostic depuis deux perspectives

```text
HÔTE
 |
 +-- Ressources globales
 |
 +-- Espaces de noms et cgroups
 |
 +-- Processus visible sur l'hôte
       |
       v
CONTENEUR
 |
 +-- PID visible localement
 |
 +-- Applications et dépendances
 |
 +-- Limites locales de ressources
```

Un diagnostic complet doit rapprocher les deux perspectives.

Les outils disponibles et les permissions déterminent ce qui peut être observé depuis chaque contexte.


# 24. Automatisation fiable des opérations

## 24.1. Pourquoi un script expert doit-il éviter les hypothèses implicites ?

Un script doit vérifier ses arguments, traiter les échecs attendus et éviter les décisions destructrices fondées sur une recherche approximative.

En particulier, un processus qui disparaît entre deux commandes peut faire échouer une opération pourtant correcte au moment où la cible a été identifiée.

La conception doit donc tenir compte de la concurrence et de la réutilisation des PID.

## 24.2. Collecteur de diagnostic non destructif

Le script suivant rassemble plusieurs informations générales et, lorsque c'est possible, les informations d'un PID fourni.

Il n'envoie aucun signal et ne modifie pas le service.

Créer `collecte-processus.sh` :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -gt 1 ]]; then
    printf 'Usage : %s [PID]\n' "$0" >&2
    exit 2
fi

PID=${1:-}

if [[ -n "$PID" ]]; then
    if [[ ! "$PID" =~ ^[1-9][0-9]*$ ]]; then
        printf 'Erreur : le PID doit être un entier strictement positif.\n' >&2
        exit 2
    fi
fi

printf '\n%s\n' '=== Date ==='
date '+%F %T'

printf '\n%s\n' '=== Charge système ==='
uptime

printf '\n%s\n' '=== Mémoire ==='
free -h

printf '\n%s\n' '=== Pression système disponible ==='

for resource in cpu memory io; do
    file="/proc/pressure/$resource"

    if [[ -r "$file" ]]; then
        printf '\n--- %s ---\n' "$resource"
        cat "$file"
    else
        printf 'PSI indisponible pour %s\n' "$resource"
    fi
done

printf '\n%s\n' '=== Principaux processus selon le CPU ==='
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd \
    --sort=-%cpu | head -n 15

if [[ -n "$PID" ]]; then
    printf '\n%s\n' "=== Processus PID $PID ==="

    if ps -p "$PID" \
        -o pid,ppid,pgid,sid,user,stat,ni,pri,etime,cmd; then
        if [[ -r "/proc/$PID/status" ]]; then
            printf '\n%s\n' '=== Informations /proc/status ==='
            grep -E '^(Name|State|Pid|PPid|Uid|Gid|Threads|voluntary_ctxt_switches|nonvoluntary_ctxt_switches):' \
                "/proc/$PID/status" || true
        fi

        if [[ -r "/proc/$PID/smaps_rollup" ]]; then
            printf '\n%s\n' '=== Résumé mémoire ==='
            cat "/proc/$PID/smaps_rollup"
        fi

        if [[ -r "/proc/$PID/limits" ]]; then
            printf '\n%s\n' '=== Limites du processus ==='
            cat "/proc/$PID/limits"
        fi
    else
        printf 'Le PID %s ne correspond plus à un processus visible.\n' "$PID"
        exit 1
    fi
fi
```

Rendre le script exécutable :

```bash
chmod +x collecte-processus.sh
```

Exécution globale :

```bash
./collecte-processus.sh
```

Avec un PID réel :

```bash
./collecte-processus.sh 1234
```

Le PID `1234` est illustratif.

## 24.3. Limites du collecteur

Le script effectue plusieurs lectures successives. Il ne garantit donc pas que toutes les informations proviennent exactement du même instant.

Un processus peut se terminer pendant la collecte.

Certaines informations peuvent être indisponibles en raison des permissions, de la configuration du noyau ou de la disparition du processus.

Un diagnostic sensible peut nécessiter une collecte plus cohérente, un mécanisme de référence de processus comme PIDFD dans un outil adapté, ou une instrumentation spécifique.

## 24.4. Automatiser sans redémarrer aveuglément

Une supervision peut d'abord produire un état et un code de retour.

Elle peut ensuite transmettre une alerte à un système de surveillance.

Le redémarrage automatique doit être réservé aux cas dans lesquels la politique de service a été conçue pour ce comportement, en tenant compte des limites de tentatives, de la collecte des erreurs et des effets de la perte de service.


# 25. Scénarios avancés de dépannage

## 25.1. Scénario A : CPU élevé, débit faible

### Symptôme

Un processus consomme un processeur logique en continu, mais les résultats applicatifs restent faibles.

### Méthode

1. Observer la consommation avec `top`.
2. Examiner les threads.
3. Enregistrer un profil CPU avec `perf`, dans un environnement autorisé.
4. Vérifier si l'activité se concentre dans le code applicatif ou dans les appels noyau.
5. Examiner la présence d'une boucle inutile, d'une attente active ou d'une contention.
6. Comparer le comportement avec une charge connue.

### Conclusion attendue

Le CPU élevé est le symptôme. Il faut déterminer si le travail exécuté produit un résultat utile ou si une boucle, une synchronisation ou une limitation empêche la progression.

## 25.2. Scénario B : latence élevée, CPU faible

### Symptôme

L'application répond lentement alors que son CPU semble faible.

### Méthode

1. Examiner les états des processus.
2. Observer les appels système avec `strace` lorsque c'est autorisé.
3. Examiner les statistiques d'entrée-sortie.
4. Contrôler la PSI pour la mémoire et les entrées-sorties.
5. Examiner les dépendances externes et les journaux.
6. Comparer le temps d'attente à la chronologie de l'application.

### Conclusion attendue

Une faible utilisation CPU n'exclut ni une attente longue, ni une dépendance indisponible, ni une limite de ressources.

## 25.3. Scénario C : échec de création de threads

### Symptôme

Une application ne parvient plus à créer de nouveaux travailleurs.

### Causes possibles

- limite de tâches du cgroup ;
- limite de processus ou de ressources de l'utilisateur ;
- limite de descripteurs ou autres ressources ;
- mémoire insuffisante ;
- erreur interne du programme.

### Méthode

```bash
systemctl show nom.service -p TasksCurrent -p TasksMax
```

Puis :

```bash
cat /proc/PID/limits
```

et, si disponibles, les compteurs du cgroup et les journaux.

### Conclusion attendue

Il faut déterminer quelle limite ou quelle ressource provoque l'échec, plutôt que d'augmenter aveuglément toutes les limites.

## 25.4. Scénario D : service tué pour épuisement mémoire

### Symptôme

Le service redémarre, mais ses journaux ou ceux du noyau indiquent un événement OOM.

### Méthode

1. Identifier les messages d'OOM.
2. Déterminer si la limite est globale ou liée au cgroup.
3. Examiner `memory.current`, `memory.max` et `memory.events`, lorsque disponibles.
4. Comparer la consommation avec la charge de l'application.
5. Établir si la croissance mémoire est normale ou anormale.
6. Choisir un ajustement de capacité, une correction applicative ou une limite mieux dimensionnée.

### Conclusion attendue

Il ne suffit pas d'augmenter la limite : il faut comprendre la relation entre la charge, les allocations mémoire et la politique de ressources.

## 25.5. Scénario E : espace disque non récupéré après suppression d'un journal

### Symptôme

Un fichier de journal a été supprimé, mais l'espace utilisé ne diminue pas comme prévu.

### Méthode

1. Examiner les systèmes de fichiers avec les outils de stockage appropriés.
2. Rechercher des fichiers supprimés mais encore ouverts avec `lsof`, si disponible.
3. Identifier le processus qui détient les descripteurs.
4. Examiner la configuration du journal et de sa rotation.
5. Utiliser la procédure documentée pour faire fermer le fichier ou faire tourner le journal.

### Conclusion attendue

Un fichier qui n'a plus d'entrée de répertoire peut encore exister tant qu'il est référencé par un processus ou une autre référence du système.

Il faut corriger la gestion du journal plutôt que tuer arbitrairement le processus.


# 26. Travaux pratiques guidés

Les TP suivants doivent être réalisés dans une machine de laboratoire. Les exercices qui génèrent une charge CPU sont limités en durée. Les opérations de configuration de service doivent être effectuées uniquement sur une unité dont tu maîtrises l'usage.

## TP 1 — Examiner le cycle de vie d'un processus

### Objectif

Observer le lancement, les identifiants, la durée de vie et la terminaison d'un processus.

### Étape 1 : lancer un processus de test

```bash
sleep 120 &
PID=$!

printf 'PID de test : %s\n' "$PID"
```

### Étape 2 : examiner son contexte

```bash
ps -p "$PID" -o pid,ppid,pgid,sid,user,stat,etime,cmd
```

### Étape 3 : observer son état

```bash
cat "/proc/$PID/status"
```

### Étape 4 : envoyer une demande de terminaison

```bash
kill -TERM "$PID"
```

### Étape 5 : vérifier

```bash
ps -p "$PID" -o pid,ppid,stat,cmd
```

### Résultat attendu

Tu dois pouvoir décrire les identifiants, l'état, la disparition de la tâche et les limites d'un contrôle fondé uniquement sur le PID.


## TP 2 — Examiner les limites d'un processus

### Objectif

Lire les limites de ressources déclarées pour un processus.

### Étape 1

```bash
sleep 120 &
PID=$!
```

### Étape 2

```bash
cat "/proc/$PID/limits"
```

### Étape 3

Observer notamment les limites pertinentes pour le nombre de fichiers ouverts ou les ressources de processus, selon ce que le système expose.

### Étape 4

```bash
kill -TERM "$PID"
```

### Résultat attendu

Tu dois savoir différencier une limite déclarée et une consommation réelle.


## TP 3 — Observer la pression PSI

### Objectif

Lire les informations de pression système.

### Étape 1

```bash
cat /proc/pressure/cpu
```

### Étape 2

```bash
cat /proc/pressure/memory
```

### Étape 3

```bash
cat /proc/pressure/io
```

### Étape 4

Relever les champs `some`, `full`, `avg10`, `avg60`, `avg300` et `total`, lorsque disponibles.

### Étape 5

Expliquer pourquoi ces métriques ne sont pas équivalentes à l'utilisation CPU ou à la mémoire utilisée.

### Résultat attendu

Tu dois pouvoir expliquer que PSI quantifie la pression et le temps perdu à attendre des ressources, selon les définitions du noyau.


## TP 4 — Utiliser `strace` sur une commande contrôlée

### Objectif

Observer quelques appels système sans viser un service de production.

### Étape 1

```bash
strace -f -o /tmp/process-expert-trace.log ls /tmp
```

### Étape 2

Examiner le fichier :

```bash
less /tmp/process-expert-trace.log
```

### Étape 3

Faire une version filtrée :

```bash
strace -e trace=openat,read,write,close -o /tmp/process-expert-files.log ls /tmp
```

### Étape 4

Examiner le résultat :

```bash
less /tmp/process-expert-files.log
```

### Étape 5

Supprimer les traces de laboratoire après leur examen :

```bash
rm -f /tmp/process-expert-trace.log /tmp/process-expert-files.log
```

Ces chemins correspondent aux fichiers de test créés par ce TP. Ne réutilise pas cette suppression pour des journaux ou traces d'origine inconnue.

### Résultat attendu

Tu dois pouvoir expliquer ce que la trace représente et pourquoi elle ne donne pas automatiquement la cause complète d'un problème.


## TP 5 — Profilage CPU avec une durée limitée

### Objectif

Découvrir `perf stat`.

### Étape 1 : vérifier la disponibilité

```bash
command -v perf
```

### Étape 2 : exécuter un calcul limité dans le temps

```bash
perf stat -- timeout 3s sha256sum /dev/zero
```

### Étape 3

Observer les statistiques produites et identifier les valeurs qui correspondent à des compteurs ou à des mesures temporelles.

### Étape 4

Expliquer pourquoi il est nécessaire de connaître le contexte et l'architecture pour interpréter les compteurs de performance.

### Résultat attendu

Tu dois pouvoir lancer une collecte simple, identifier ses limites et expliquer qu'un compteur n'est pas à lui seul un diagnostic.


## TP 6 — Examiner le cgroup d'un service

### Objectif

Relier un service `systemd` à ses ressources.

### Étape 1

Choisir un service de laboratoire réellement installé :

```bash
systemctl status nom.service
```

### Étape 2

Afficher son chemin de groupe de contrôle :

```bash
systemctl show nom.service -p ControlGroup
```

### Étape 3

Relever le chemin retourné.

### Étape 4

Si cgroup v2 est monté sous `/sys/fs/cgroup`, construire le chemin de lecture du cgroup à partir du chemin réel et vérifier les fichiers présents.

Ne suppose pas qu'un contrôleur est activé simplement parce que le service existe.

### Étape 5

Lire uniquement les fichiers de statistiques accessibles et pertinents.

### Résultat attendu

Tu dois pouvoir expliquer pourquoi la consommation d'un service ne s'évalue pas uniquement à partir de son PID principal.


## TP 7 — Construire un collecteur de diagnostic

### Objectif

Créer un script qui collecte les mesures sans arrêter le processus.

### Étape 1

Créer le fichier `collecte-processus.sh` avec le script de la section 24.

### Étape 2

Le rendre exécutable :

```bash
chmod +x collecte-processus.sh
```

### Étape 3

Exécuter la collecte générale :

```bash
./collecte-processus.sh
```

### Étape 4

Lancer une tâche de test :

```bash
sleep 120 &
PID=$!
```

Puis :

```bash
./collecte-processus.sh "$PID"
```

### Étape 5

Terminer le processus de test :

```bash
kill -TERM "$PID"
```

### Étape 6

Réexécuter la collecte avec le PID de test et interpréter le résultat.

### Résultat attendu

Tu dois obtenir un rapport utile et non destructif, tout en comprenant les erreurs de lecture possibles et les limites d'une collecte réalisée en plusieurs étapes.


# 27. Exercices d'application

## Exercice 1 — Création et exécution

Explique la différence entre `fork()` et `execve()`.

Pourquoi un changement de programme ne signifie-t-il pas nécessairement qu'un nouveau PID est attribué ?

## Exercice 2 — Copy-on-write

Pourquoi une création de processus ne provoque-t-elle pas obligatoirement une copie physique immédiate de toute la mémoire du parent ?

Dans quelles circonstances la mémoire physique peut-elle ensuite augmenter ?

## Exercice 3 — Zombies

Un service produit beaucoup de processus zombies persistants.

Quelle relation dois-tu examiner en premier ?

Pourquoi `SIGKILL` adressé à chaque zombie n'est-il pas une solution adaptée ?

## Exercice 4 — Identité et PIDFD

Quel risque existe lorsque l'on stocke un PID pendant une longue durée ?

Quel problème un PIDFD cherche-t-il à éviter ?

## Exercice 5 — Espaces de noms

Pourquoi un processus peut-il avoir un PID différent dans un conteneur et sur l'hôte ?

Quelle commande permet d'examiner les informations d'espaces de noms d'un PID ?

## Exercice 6 — CPU et progression

Un processus utilise beaucoup de CPU, mais son travail n'avance pas.

Quelles approches de diagnostic peux-tu utiliser pour rechercher la cause ?

## Exercice 7 — Profilage

Quelle est la différence entre `strace` et `perf` ?

Dans quel cas chacun peut-il aider ?

## Exercice 8 — Pression système

Explique la différence entre la consommation CPU et la pression CPU.

Pourquoi PSI peut-elle fournir une information complémentaire à `top` ?

## Exercice 9 — Mémoire partagée

Pourquoi la somme des RSS de tous les processus peut-elle surestimer l'utilisation physique réelle de la mémoire ?

Quelle métrique peut aider à attribuer les pages partagées ?

## Exercice 10 — OOM

Un processus est terminé alors que la machine conserve de la mémoire disponible.

Comment expliquer cette situation et quelles données examiner ?

## Exercice 11 — Fichiers ouverts

Pourquoi l'espace disque peut-il ne pas être libéré immédiatement après la suppression d'un journal ?

Quelles commandes peuvent aider à identifier le processus qui détient encore ce fichier ?

## Exercice 12 — cgroups

Un service atteint sa limite CPU alors que la machine reste globalement peu occupée.

Pourquoi est-ce possible ?

Quelles propriétés ou mesures faut-il examiner ?

## Exercice 13 — Threads et processus

Pourquoi examiner uniquement les PID peut-il masquer le comportement d'une application multithread ?

Cite deux outils adaptés à l'observation des threads.

## Exercice 14 — Supervision

Pourquoi le statut `active` d'un service ne suffit-il pas à prouver que l'application est fonctionnelle ?

## Exercice 15 — Sécurité

Cite au moins cinq informations à vérifier avant de modifier ou arrêter un processus sur un serveur important.


# 28. Corrections détaillées des exercices

## Correction 1 — Création et exécution

`fork()` crée un processus enfant.

`execve()` remplace le programme exécuté par le processus courant par un autre programme.

Un processus qui utilise avec succès `execve()` conserve généralement son PID. L'identité du processus et le programme qu'il exécute sont donc deux choses distinctes.

## Correction 2 — Copy-on-write

Le mécanisme copy-on-write permet de partager certaines pages physiques entre parent et enfant tant qu'une copie séparée n'est pas nécessaire.

Si le parent ou l'enfant modifie une page qui doit devenir privée, le noyau peut créer une copie.

La mémoire physique peut alors augmenter, notamment lorsque beaucoup de pages deviennent privées ou lorsque les processus allouent de nouvelles pages.

## Correction 3 — Zombies

Il faut examiner le parent des zombies et sa gestion des statuts de fin.

Un zombie a déjà terminé son exécution. Lui envoyer `SIGKILL` ne remplace pas l'opération `wait()` que son parent doit réaliser.

Il faut comprendre pourquoi le parent ne récupère pas les enfants.

## Correction 4 — Identité et PIDFD

Un PID peut être réutilisé après la fin du processus.

Un outil qui réutilise un PID ancien peut donc viser une nouvelle tâche.

Un PIDFD maintient une référence à un processus particulier via un descripteur, ce qui réduit le risque associé à la réutilisation du numéro.

## Correction 5 — Espaces de noms

Les espaces de noms PID donnent une vue locale des identifiants de processus.

Le même processus peut donc être visible sous un PID dans un conteneur et sous un autre PID depuis l'hôte.

Pour examiner les espaces de noms :

```bash
ls -l /proc/PID/ns
```

Pour examiner certains champs :

```bash
grep -E '^(NSpid|NStgid|NSpgid|NSsid):' /proc/PID/status
```

## Correction 6 — CPU et progression

Tu peux examiner :

- les threads du processus ;
- les statistiques CPU répétées ;
- les appels système ;
- les traces `perf` ;
- les journaux ;
- les éventuels verrous ou attentes ;
- les limites de cgroup ;
- le comportement attendu de l'application.

La consommation CPU élevée peut être due à une boucle active, à une contention, à un travail intensif ou à un autre mécanisme. Il faut distinguer ces causes.

## Correction 7 — Profilage

`strace` observe les appels système et les signaux.

`perf` peut recueillir des compteurs de performance et profiler certaines parties de l'exécution.

`strace` est utile pour examiner les erreurs et les attentes au niveau des appels système ; `perf` est utile pour analyser certaines caractéristiques de l'exécution CPU.

## Correction 8 — Pression système

La consommation CPU mesure l'utilisation de la capacité de traitement.

La pression CPU renseigne sur le temps pendant lequel des tâches sont retardées par la contention de cette ressource, selon les métriques du noyau.

PSI apporte donc une information complémentaire sur les conséquences de la contention pour les tâches.

## Correction 9 — Mémoire partagée

Plusieurs processus peuvent utiliser les mêmes pages physiques, mais chaque RSS peut compter la page partagée comme résidente.

La somme des RSS peut ainsi compter certaines pages plusieurs fois.

Le PSS permet de répartir proportionnellement les pages partagées entre les processus concernés, selon les conventions de la mesure.

## Correction 10 — OOM

Une limite de mémoire peut s'appliquer au service ou au conteneur même si la machine conserve de la mémoire disponible.

Il faut examiner les journaux du noyau, les limites du cgroup et les compteurs tels que `memory.events`, lorsqu'ils sont présents.

## Correction 11 — Fichiers ouverts

La suppression d'une entrée de répertoire ne libère pas nécessairement immédiatement le contenu si une référence ouverte est encore détenue.

On peut examiner :

```bash
lsof -nP -p PID
```

et :

```bash
ls -l /proc/PID/fd
```

Il faut identifier le processus concerné avant d'intervenir.

## Correction 12 — cgroups

Le service peut être soumis à un quota ou à une contrainte CPU propre à son cgroup.

Il faut examiner les propriétés `CPUQuota=` et `CPUWeight=`, le chemin de `ControlGroup` et les statistiques CPU du cgroup.

Une disponibilité CPU globale ne garantit pas qu'une unité donnée puisse utiliser toute cette capacité.

## Correction 13 — Threads et processus

Une application multithread peut présenter un seul PID de groupe dans certaines vues, alors que plusieurs threads exécutent le travail.

`top -H -p PID` et `ps -L -p PID ...` permettent d'observer les threads.

## Correction 14 — Supervision

Un service actif peut encore présenter une erreur fonctionnelle, une dépendance indisponible, une saturation ou un problème dans le traitement des requêtes.

Il faut compléter le statut avec des tests fonctionnels, des journaux et des mesures adaptés.

## Correction 15 — Sécurité

Les informations à vérifier comprennent notamment :

1. PID ;
2. propriétaire ;
3. commande et arguments ;
4. PPID et groupe de processus ;
5. état ;
6. service ou cgroup d'appartenance ;
7. consommation et limites de ressources ;
8. journaux ;
9. permissions ;
10. conséquences de l'intervention.


# 29. Défi final : incident complexe sur un serveur de production

## 29.1. Contexte

Tu administres un serveur Linux qui héberge une application gérée par `systemd`.

Le service présente une dégradation intermittente.

Les observations disponibles sont les suivantes :

```text
OBSERVATION A
Le service est déclaré actif par systemd.

OBSERVATION B
Un ou plusieurs processus semblent utiliser beaucoup de CPU.

OBSERVATION C
Certains utilisateurs signalent des réponses lentes.

OBSERVATION D
La machine ne semble pas complètement saturée en CPU.

OBSERVATION E
Un processus a été redémarré au cours de la période observée.

OBSERVATION F
L'équipe souhaite un diagnostic reproductible et une procédure
de surveillance qui ne détruise pas les preuves.
```

Ces informations ne permettent pas encore de connaître la cause.

Il faut construire une procédure qui distingue une charge normale, un blocage, une limite CPU, un problème mémoire, une difficulté d'entrée-sortie et un dysfonctionnement applicatif.

## 29.2. Mission

Ton rapport doit répondre aux questions suivantes :

1. Quels processus et threads participent à l'application ?
2. Quelles sont leurs relations de parenté et leur organisation en groupes ?
3. Le CPU est-il consommé par du calcul applicatif ou par une autre activité ?
4. La machine présente-t-elle une pression CPU, mémoire ou entrée-sortie ?
5. Le service est-il limité par un cgroup ?
6. Le redémarrage correspond-il à une règle de supervision ou à un incident ?
7. Des erreurs apparaissent-elles dans les journaux au moment de la dégradation ?
8. Les mesures indiquent-elles un problème de mémoire ou de descripteurs ouverts ?
9. Quelle instrumentation supplémentaire est nécessaire ?
10. Quelle intervention est justifiée par les preuves ?
11. Comment vérifier que le problème est résolu ?
12. Comment éviter que la même situation se reproduise ?

## 29.3. Contraintes

- Ne redémarre pas le service comme première réaction.
- Ne tue pas les processus qui consomment le plus de CPU sans analyse.
- Ne modifie pas les limites de ressources avant d'avoir relevé les valeurs effectives.
- Ne confonds pas le statut actif avec la bonne santé applicative.
- Ne suppose pas qu'un PID est identique dans tous les espaces de noms.
- Ne collecte pas de traces globales indéfiniment.
- Ne modifie pas les paramètres de sécurité du noyau sans justification.
- Documente les résultats négatifs comme les résultats positifs.
- Garde une méthode de vérification après l'intervention.


# 30. Correction détaillée du défi final

## 30.1. Étape 1 — Identifier le service et son contexte

Commence par :

```bash
systemctl status nom.service
```

Puis :

```bash
systemctl show nom.service -p MainPID -p ControlGroup
```

Examine la configuration :

```bash
systemctl cat nom.service
```

Le nom de service doit être remplacé par une unité réelle.

L'objectif est de connaître le statut du service, son PID principal déclaré, son groupe de contrôle et les règles de cycle de vie pertinentes.

## 30.2. Étape 2 — Cartographier les processus

Affiche :

```bash
ps -eo pid,ppid,pgid,sid,user,stat,ni,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 30
```

Puis :

```bash
ps -ef --forest
```

Identifie les processus associés à l'application.

Si le service possède plusieurs processus enfants, note leurs PID, PPID et commande.

Il faut éviter de supposer qu'un seul PID représente toute l'activité du service.

## 30.3. Étape 3 — Observer les threads

Pour les processus multithread pertinents :

```bash
top -H -p PID
```

Ou :

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

Comparer les threads et vérifier si l'activité est concentrée sur une partie de l'application.

Une forte utilisation par un thread peut indiquer un calcul séquentiel, une boucle ou un point de contention, mais il faut examiner le programme pour savoir lequel.

## 30.4. Étape 4 — Confirmer la tendance CPU

Si `pidstat` est disponible :

```bash
pidstat -u -p PID 1 10
```

Observer les mesures successives plutôt que de retenir uniquement un pourcentage de `ps`.

Le relevé doit être effectué pendant la période de dégradation ou dans une situation reproductible.

## 30.5. Étape 5 — Examiner la pression système

Lire les métriques PSI disponibles :

```bash
cat /proc/pressure/cpu
```

```bash
cat /proc/pressure/memory
```

```bash
cat /proc/pressure/io
```

Puis :

```bash
vmstat 1 10
```

Comparer ces mesures avec le temps de réponse de l'application.

Si la pression CPU est faible mais que la latence reste élevée, il faut examiner d'autres causes, notamment les entrées-sorties, les dépendances, les appels système et les limites de service.

## 30.6. Étape 6 — Vérifier les limites du cgroup

Relever le cgroup :

```bash
systemctl show --value -p ControlGroup nom.service
```

Examiner les propriétés déclarées par `systemd` :

```bash
systemctl show nom.service -p CPUQuotaPerSecUSec -p CPUWeight -p MemoryHigh -p MemoryMax -p TasksMax
```

Si l'environnement utilise cgroup v2, vérifier les statistiques disponibles dans le répertoire correspondant à l'unité.

Il faut lire les compteurs et les limites réellement appliquées, sans supposer qu'une propriété absente équivaut à une limite particulière.

## 30.7. Étape 7 — Examiner la mémoire et les descripteurs

Pour le PID principal ou un processus suspect :

```bash
cat /proc/PID/smaps_rollup
```

Puis :

```bash
cat /proc/PID/limits
```

Et, si nécessaire :

```bash
find "/proc/PID/fd" -maxdepth 1 -type l | wc -l
```

Le nombre de descripteurs doit être comparé à la limite et à la fonction du processus.

Il ne faut pas conclure à une fuite simplement parce qu'un service possède beaucoup de fichiers ouverts.

## 30.8. Étape 8 — Vérifier la chronologie et les journaux

Examiner les messages récents du service :

```bash
journalctl -u nom.service --since "2 hours ago" --no-pager
```

Examiner les messages du noyau :

```bash
journalctl -k --since "2 hours ago" --no-pager
```

Rechercher :

- redémarrages ;
- erreurs applicatives ;
- messages d'OOM ;
- échecs de création de tâches ;
- erreurs d'entrée-sortie ;
- événements liés aux dépendances.

Comparer les messages à la période exacte de dégradation.

## 30.9. Étape 9 — Sélectionner l'instrumentation appropriée

Si les mesures montrent une activité CPU dominante mais que la cause reste inconnue, une trace `perf` peut être pertinente.

Pour une commande de laboratoire :

```bash
perf record -g -- timeout 5s sha256sum /dev/zero
```

Dans une investigation sur un service existant, il faut choisir une méthode d'attachement adaptée au contexte et comprendre l'impact de la collecte.

Si le problème semble lié à un appel système qui attend, `strace` peut aider :

```bash
strace -ttT -p PID
```

Cette opération doit être courte, autorisée et limitée au processus pertinent.

Si le noyau et la politique de sécurité le permettent, une sonde `bpftrace` correctement conçue peut apporter une mesure complémentaire.

Le choix de l'outil dépend de l'hypothèse à vérifier.

## 30.10. Étape 10 — Classer les hypothèses

Un rapport expert doit distinguer les catégories suivantes.

| Hypothèse | Éléments à rechercher |
|---|---|
| Calcul CPU excessif | Mesures CPU répétées, profils et activité des threads |
| Quota CPU | Propriétés de l'unité, statistiques du cgroup |
| Pression mémoire | PSI, mémoire disponible, swap, limites et événements mémoire |
| OOM | Journaux du noyau, compteurs du cgroup |
| Entrées-sorties lentes | `iostat`, `pidstat -d`, états et journaux |
| Fuite de descripteurs | Nombre de descripteurs, limites, évolution dans le temps |
| Blocage applicatif | Journaux, attentes, appels système, piles de threads |
| Redémarrages répétés | Journaux du service, configuration de supervision |
| Limite de tâches | `TasksMax`, `pids.current`, `pids.events` si disponibles |

Une même application peut subir plusieurs de ces problèmes. Il faut éviter de choisir une cause unique si les preuves révèlent plusieurs facteurs.

## 30.11. Étape 11 — Définir une intervention

Le traitement dépend de la cause confirmée.

Exemples :

- corriger une boucle applicative ;
- ajuster une limite CPU après validation de la charge attendue ;
- corriger une fuite mémoire ;
- dimensionner la mémoire d'un service selon des mesures réelles ;
- résoudre une attente d'entrée-sortie ;
- corriger une fuite de descripteurs ;
- adapter la politique de redémarrage ;
- améliorer la collecte des journaux ;
- corriger la logique de gestion des processus enfants.

Un redémarrage peut servir de mesure temporaire de rétablissement dans certains incidents, mais il ne constitue pas nécessairement la correction de fond.

Avant une intervention, documente la cible, le symptôme, les risques, le résultat attendu et le moyen de vérifier ce résultat.

## 30.12. Étape 12 — Valider la résolution

Après intervention :

1. répéter les mesures CPU ;
2. relire les statistiques mémoire et PSI ;
3. vérifier l'état et les journaux du service ;
4. observer les threads et les processus concernés ;
5. vérifier la fonctionnalité applicative ;
6. comparer les résultats aux mesures initiales ;
7. confirmer que le symptôme a disparu ou préciser les éléments restant à investiguer.

Une commande qui réussit n'est pas une validation complète.

La résolution doit être démontrée par un résultat observable.

## 30.13. Étape 13 — Prévenir la récidive

Selon la cause, les mesures préventives peuvent inclure :

- une collecte régulière de métriques ;
- des alertes fondées sur des tendances ;
- des limites de ressources adaptées ;
- des améliorations de gestion des erreurs ;
- un mécanisme correct de récupération des processus enfants ;
- des tests de charge ;
- une gestion documentée des journaux ;
- une politique de redémarrage contrôlée ;
- une amélioration de l'instrumentation applicative ;
- des procédures de diagnostic reproductibles.

La prévention doit répondre à la cause et non simplement masquer le symptôme.


# 31. Checklist des compétences expertes

## Architecture et cycle de vie

- [ ] Je distingue le processus, le thread et la tâche noyau.
- [ ] Je peux expliquer le rôle de `fork()`, `clone()` et `execve()`.
- [ ] Je comprends le principe du copy-on-write.
- [ ] Je comprends la récupération du statut d'un enfant avec `wait()`.
- [ ] Je peux distinguer un zombie d'un processus orphelin.
- [ ] Je comprends le rôle d'un sous-récolteur de processus.

## Identité et isolation

- [ ] Je distingue PID, PPID, PGID et SID.
- [ ] Je comprends les espaces de noms PID.
- [ ] Je sais pourquoi un PID peut différer dans un conteneur.
- [ ] Je comprends le risque de réutilisation des PID.
- [ ] Je peux expliquer le rôle conceptuel des PIDFD.
- [ ] Je sais examiner les informations de sécurité de `/proc/PID/status`.

## Ordonnancement et performance

- [ ] Je comprends la différence entre temps CPU, temps d'attente et charge moyenne.
- [ ] Je sais analyser les threads.
- [ ] Je sais utiliser `pidstat` et `vmstat`.
- [ ] Je sais expliquer les limites de RSS et le rôle de PSS.
- [ ] Je sais analyser les descripteurs et les limites d'un processus.
- [ ] Je sais quand utiliser `strace`.
- [ ] Je sais quand utiliser `perf`.
- [ ] Je comprends les limites des traces dynamiques.

## Ressources et supervision

- [ ] Je comprends le rôle des cgroups.
- [ ] Je sais relier un service à son groupe de contrôle.
- [ ] Je comprends la différence entre ressources globales et limites de service.
- [ ] Je sais consulter les limites et événements mémoire.
- [ ] Je comprends la pression PSI.
- [ ] Je sais examiner les politiques de supervision de `systemd`.
- [ ] Je peux distinguer état de service et santé applicative.

## Sécurité et qualité opérationnelle

- [ ] Je sais identifier les permissions et capacités d'un processus.
- [ ] Je ne confonds pas réussite d'envoi de signal et terminaison effective.
- [ ] Je ne lance pas une collecte de traces sans évaluer son impact.
- [ ] Je sais limiter le périmètre et la durée d'une instrumentation.
- [ ] Je documente les hypothèses, preuves, actions et résultats.
- [ ] Je sais concevoir une supervision non destructive avant d'automatiser une correction.


# 32. Fiche de référence des commandes

## Identifiants et processus

```bash
ps -eo pid,ppid,pgid,sid,tpgid,user,stat,cmd
```

```bash
ps -ef --forest
```

```bash
pstree -p
```

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

## Informations internes

```bash
cat /proc/PID/status
```

```bash
cat /proc/PID/limits
```

```bash
cat /proc/PID/smaps_rollup
```

```bash
ls -l /proc/PID/ns
```

```bash
ls -l /proc/PID/fd
```

## Ressources

```bash
top -H -p PID
```

```bash
pidstat -u -p PID 1 10
```

```bash
pidstat -r -p PID 1 10
```

```bash
pidstat -d -p PID 1 10
```

```bash
vmstat 1 10
```

```bash
iostat -xz 1 10
```

## Pression système

```bash
cat /proc/pressure/cpu
```

```bash
cat /proc/pressure/memory
```

```bash
cat /proc/pressure/io
```

## Traces et profilage

```bash
strace -ttT -p PID
```

```bash
strace -c -f commande
```

```bash
perf list
```

```bash
perf stat -- timeout 5s commande
```

```bash
perf record -g -- timeout 5s commande
```

```bash
perf report
```

## Services et cgroups

```bash
systemctl status nom.service
```

```bash
systemctl show nom.service -p MainPID -p ControlGroup
```

```bash
systemctl show nom.service -p CPUQuotaPerSecUSec -p CPUWeight -p MemoryHigh -p MemoryMax -p TasksMax
```

```bash
systemctl cat nom.service
```

```bash
journalctl -u nom.service -n 100 --no-pager
```

```bash
findmnt -t cgroup,cgroup2
```

## Limites et sécurité

```bash
ulimit -a
```

```bash
cat /proc/PID/oom_score
```

```bash
cat /proc/PID/oom_score_adj
```

```bash
cat /proc/PID/limits
```

Ces commandes servent à la collecte et à l'inspection. Les commandes qui modifient des services, des priorités, des limites ou des mécanismes de sécurité doivent être adaptées et validées dans le contexte réel.


# 33. Glossaire technique

**Appel système :** interface par laquelle un programme demande un service au noyau.

**Cgroup :** mécanisme du noyau Linux permettant d'organiser des groupes de tâches et de contrôler ou comptabiliser leurs ressources.

**Copy-on-write :** mécanisme permettant de partager certaines pages mémoire jusqu'à ce qu'une copie séparée soit nécessaire.

**`execve()` :** appel système qui remplace le programme courant par un nouveau programme dans le même processus.

**eBPF :** infrastructure du noyau permettant notamment l'exécution de programmes d'observation et de traitement d'événements dans des cadres vérifiés.

**Fuite de descripteurs :** situation dans laquelle une application conserve des descripteurs ouverts inutilement ou au-delà de la durée attendue.

**Fuite mémoire :** consommation mémoire qui augmente ou reste retenue de manière anormale par rapport au comportement attendu.

**Groupe de processus :** ensemble de processus partageant un identifiant PGID.

**`fork()` :** appel système qui crée un processus enfant à partir du processus appelant.

**Interblocage :** situation dans laquelle des tâches attendent mutuellement des ressources ou conditions empêchant la progression.

**OOM killer :** mécanisme qui peut terminer certaines tâches lorsque la mémoire ne peut plus être fournie dans le contexte concerné.

**Ordonnanceur :** composant du noyau qui sélectionne les tâches à exécuter sur les processeurs logiques.

**PIDFD :** descripteur de fichier faisant référence à un processus et permettant certains contrôles sans dépendre uniquement d'un numéro PID réutilisable.

**PSS :** mémoire proportionnellement attribuée à un processus en tenant compte des pages partagées.

**PSI :** Pressure Stall Information, métrique du noyau permettant d'estimer l'impact de la contention CPU, mémoire ou entrées-sorties sur les tâches.

**`perf` :** famille d'outils Linux de mesure et de profilage des performances.

**`pidfd_open()` :** interface système permettant d'obtenir un descripteur associé à une tâche.

**`pidfd_send_signal()` :** interface système permettant d'envoyer un signal à une tâche référencée par un PIDFD, sous réserve des permissions.

**`pidstat` :** outil permettant d'observer des statistiques de tâches sur plusieurs intervalles.

**PID :** identifiant d'un processus dans l'espace de noms concerné.

**PPID :** identifiant du parent.

**PGID :** identifiant d'un groupe de processus.

**SID :** identifiant d'une session de processus.

**Processus orphelin :** processus qui continue à exister après la disparition de son parent.

**Processus zombie :** processus terminé dont le statut de fin n'a pas encore été récupéré dans les conditions attendues.

**`clone()` :** interface de création de tâches dont les options contrôlent le partage de ressources.

**`clone3()` :** interface plus récente de création de tâches avec des paramètres extensibles, selon le support du noyau.

**RSS :** mémoire résidente associée à un processus selon les conventions de l'outil.

**`smaps_rollup` :** fichier de `/proc` qui fournit un résumé de statistiques de mémoire pour un processus, lorsqu'il est disponible.

**`strace` :** outil de suivi des appels système et des signaux.

**Thread :** fil d'exécution associé à un processus ou à un groupe de threads.

**Namespace :** mécanisme d'isolation permettant à un processus d'avoir une vue distincte de certaines ressources du système.

**`task_struct` :** structure interne du noyau Linux qui représente les informations d'une tâche ; ce n'est pas une interface stable d'administration.

**`waitpid()` :** interface permettant d'attendre un changement d'état d'un enfant et de récupérer son statut.


# 34. Documentation officielle

Les références suivantes permettent d'approfondir les interfaces, les outils et les mécanismes abordés dans ce cours.

## Cycle de vie et interfaces système

1. `fork(2)` — création d'un processus enfant  
   https://man7.org/linux/man-pages/man2/fork.2.html

2. `execve(2)` — exécution d'un nouveau programme  
   https://man7.org/linux/man-pages/man2/execve.2.html

3. `wait(2)` — attente et récupération du statut des processus enfants  
   https://man7.org/linux/man-pages/man2/waitpid.2.html

4. `pidfd_open(2)` — référence à un processus par descripteur  
   https://man7.org/linux/man-pages/man2/pidfd_open.2.html

5. `pidfd_send_signal(2)` — signaux via un PIDFD  
   https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html

## Processus et espace de noms

6. Documentation Linux sur `/proc`  
   https://docs.kernel.org/filesystems/proc.html

7. Documentation sur les espaces de noms PID  
   https://man7.org/linux/man-pages/man7/pid_namespaces.7.html

8. Documentation Linux sur les signaux  
   https://man7.org/linux/man-pages/man7/signal.7.html

## Performance et observation

9. `strace(1)`  
   https://man7.org/linux/man-pages/man1/strace.1.html

10. `perf stat(1)`  
    https://man7.org/linux/man-pages/man1/perf-stat.1.html

11. Documentation du projet `bpftrace`  
    https://bpftrace.org/docs/

12. Documentation Linux sur PSI  
    https://www.kernel.org/doc/html/latest/accounting/psi.html

## Ressources et supervision

13. Documentation du noyau Linux — cgroup v2  
    https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html

14. Documentation officielle `systemd.resource-control`  
    https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html

15. Documentation officielle `systemd.service`  
    https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html

Les versions du noyau, de `systemd`, de `perf`, de `strace` et de `bpftrace` peuvent modifier les options disponibles. Vérifie toujours les pages de manuel locales et les possibilités de ta machine avant de reproduire un exemple sur un système important.


# Conclusion générale

La gestion experte des processus Linux exige de comprendre le lien entre l'application, ses processus, ses threads, les appels système, les ressources du noyau, l'ordonnanceur et les mécanismes de supervision.

Tu as étudié les mécanismes de création et de remplacement de programme, le cycle de vie des enfants, les identifiants de processus, les espaces de noms et les PIDFD. Tu as aussi approfondi le diagnostic CPU et mémoire, les limites de ressources, les descripteurs de fichiers, l'OOM killer, les groupes de contrôle, la pression PSI ainsi que les outils de traçage et de profilage.

Ces notions doivent être utilisées ensemble.

Un processus peut consommer beaucoup de CPU sans progresser. Une application peut être lente avec un CPU peu utilisé. Un service peut être actif tout en présentant une panne fonctionnelle. Un conteneur peut atteindre une limite alors que la machine hôte conserve des ressources libres. Un processus peut conserver une référence à un fichier supprimé. Une mesure isolée ne suffit donc pas toujours à déterminer la cause d'un incident.

La démarche experte est la suivante :

```text
                  INCIDENT
                     |
                     v
            DÉFINIR LE SYMPTÔME
                     |
                     v
          IDENTIFIER LA CIBLE RÉELLE
                     |
                     v
       COLLECTER DES MESURES COHÉRENTES
                     |
                     v
    RELIER PROCESSUS, THREADS ET RESSOURCES
                     |
                     v
        TESTER LES HYPOTHÈSES TECHNIQUES
                     |
                     v
           JUSTIFIER L'INTERVENTION
                     |
                     v
            VÉRIFIER LE RÉSULTAT
                     |
                     v
           PRÉVENIR LA RÉCIDIVE
```

**La compétence centrale du niveau expert est de pouvoir expliquer une anomalie à partir de preuves, puis de choisir une intervention proportionnée dont le résultat peut être vérifié.**