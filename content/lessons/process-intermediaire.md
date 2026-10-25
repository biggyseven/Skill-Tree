# Gestion des processus Linux — Niveau Intermédiaire

> **Fichier :** `process-intermediaire.md`  
> **Niveau :** Intermédiaire  
> **Domaine :** Administration système Linux  
> **Thème :** Diagnostic, supervision, contrôle des processus, signaux, ressources et automatisation  
> **Prérequis :** Avoir étudié `process-debutant.md` et maîtriser les commandes `ps`, `top`, `pgrep`, `kill`, `jobs`, `bg`, `fg`, `free`, `uptime` et les notions de PID, PPID, états et services.


# Sommaire

1. Positionnement du niveau intermédiaire
2. Architecture d'un processus Linux
3. PID, PPID, PGID, SID et TPGID
4. Groupes de processus et sessions de terminal
5. Arbres de processus et création de processus enfants
6. États avancés et symptômes de blocage
7. Signaux Linux : fonctionnement et bonnes pratiques
8. Identification fiable d'un processus
9. Maîtriser les possibilités de `ps`
10. Exploiter `top` pour le diagnostic
11. Mesures historiques avec `pidstat`, `vmstat` et `iostat`
12. Diagnostiquer CPU, mémoire, entrées-sorties et charge
13. Fichiers ouverts, descripteurs et répertoires de processus
14. Tâches Bash avancées : `wait`, `disown`, `nohup` et `timeout`
15. Automatiser la supervision avec Bash
16. Codes de retour et gestion des erreurs
17. Priorités d'ordonnancement et affinité CPU
18. Processus, services et groupes de contrôle
19. Superviser un service avec `systemd`
20. Contrôler les ressources avec `systemd` et les cgroups
21. Journaux, traçabilité et diagnostic
22. Problèmes courants et méthodes de résolution
23. Sécuriser les opérations d'administration
24. Travaux pratiques guidés
25. Exercices d'application
26. Corrections des exercices
27. Défi final : diagnostic et supervision d'un service
28. Correction détaillée du défi final
29. Checklist de compétences
30. Fiche de révision et commandes essentielles
31. Glossaire
32. Documentation de référence


# 1. Positionnement du niveau intermédiaire

## 1.1. Ce qui change par rapport au niveau débutant

Au niveau débutant, l'objectif principal était de savoir observer un processus, retrouver son PID, comprendre son état et envoyer un signal.

À présent, il faut être capable d'expliquer les relations entre plusieurs processus et de déterminer pourquoi un problème apparaît.

La différence est importante.

Un administrateur débutant peut remarquer qu'un processus utilise beaucoup de CPU.

Un administrateur intermédiaire doit pouvoir répondre à plusieurs questions supplémentaires :

- Depuis combien de temps cette consommation est-elle élevée ?
- Le processus exécute-t-il réellement beaucoup de calculs ou attend-il une ressource ?
- Plusieurs processus appartiennent-ils à la même application ?
- Un parent recrée-t-il continuellement ses enfants ?
- Le processus fait-il partie d'un service supervisé ?
- Le manque de mémoire provient-il d'un processus, d'un ensemble de processus ou d'une limite de conteneur ?
- Un signal a-t-il été envoyé au bon processus ou à un groupe entier ?
- Le processus est-il réellement bloqué ou simplement en attente ?
- L'intervention proposée peut-elle affecter d'autres applications ?

Le but n'est plus seulement d'obtenir une information. Il faut relier les informations, formuler des hypothèses, collecter des preuves, agir et vérifier le résultat.

## 1.2. La méthode de diagnostic intermédiaire

La méthode de référence est la suivante :

```text
                    INCIDENT
                       |
                       v
             1. OBSERVER LE SYMPTÔME
                       |
                       v
            2. IDENTIFIER LES CIBLES
                       |
                       v
            3. COLLECTER LES MESURES
                       |
                       v
            4. COMPRENDRE LES RELATIONS
               PID / PPID / PGID / SID
                       |
                       v
            5. RECHERCHER LA CAUSE
                       |
                       v
            6. CHOISIR UNE INTERVENTION
                       |
                       v
            7. MESURER APRÈS L'ACTION
                       |
                       v
            8. DOCUMENTer LE RÉSULTAT
```

Une mesure isolée permet rarement de démontrer une cause. Il faut examiner les tendances, les relations de processus, les événements et le contexte de fonctionnement.

## 1.3. Environnement de référence

Les exemples sont conçus pour les distributions Linux courantes utilisant les outils habituels de l'écosystème Linux.

Certains outils ou certaines options ne sont pas systématiquement installés :

| Outil | Paquet fréquent selon la distribution | Rôle |
|---|---|---|
| `ps`, `top`, `pgrep` | `procps` ou `procps-ng` | Observation des processus |
| `pstree`, parfois `killall` | `psmisc` | Arbres de processus et outils complémentaires |
| `pidstat`, `iostat`, `sar` | `sysstat` | Mesures de performance |
| `strace` | `strace` | Observation des appels système |
| `lsof` | `lsof` | Observation des fichiers et ressources ouvertes |

Les noms des paquets varient selon la distribution.

Les commandes qui modifient un service, les priorités ou les limites de ressources doivent d'abord être testées dans un environnement de laboratoire.


# 2. Architecture d'un processus Linux

## 2.1. Le processus comme contexte d'exécution

Un processus Linux ne se réduit pas à un nom et à un PID.

Il possède un ensemble d'informations et de ressources qui permettent au noyau de gérer son exécution.

On peut représenter le contexte d'un processus ainsi :

```text
PROCESSUS LINUX
|
+-- Identité
|   +-- PID
|   +-- PPID
|   +-- UID et GID effectifs
|
+-- Organisation
|   +-- Groupe de processus : PGID
|   +-- Session : SID
|
+-- Exécution
|   +-- État
|   +-- Priorité
|   +-- Threads
|   +-- Compteurs d'activité
|
+-- Ressources
|   +-- Espace mémoire virtuel
|   +-- Descripteurs de fichiers
|   +-- Connexions et sockets
|   +-- Ressources partagées
|
+-- Environnement
    +-- Arguments de commande
    +-- Variables d'environnement
    +-- Répertoire de travail
    +-- Contexte de sécurité
```

Ce schéma est conceptuel : certains éléments sont partagés avec d'autres processus, et les détails de leur gestion dépendent des mécanismes du noyau.

## 2.2. Le noyau et l'ordonnanceur

Le noyau Linux décide quelles tâches peuvent s'exécuter sur les processeurs logiques disponibles.

Un processus prêt à s'exécuter ne reçoit pas nécessairement le CPU immédiatement.

Le noyau peut devoir tenir compte :

- de la disponibilité des processeurs ;
- du nombre de tâches exécutables ;
- de la politique d'ordonnancement ;
- de la priorité des tâches ;
- des contraintes d'affinité ;
- des quotas ou limites imposés par les groupes de contrôle.

Le terme **ordonnanceur** désigne le mécanisme chargé de décider quelles tâches sont exécutées et quand.

La priorité d'un processus influence l'ordonnancement, mais ne garantit pas une durée ou un délai d'exécution précis.

## 2.3. Un processus peut contenir plusieurs threads

Un processus multithread peut effectuer différentes activités à travers plusieurs threads.

```text
PROCESSUS : application
PID : 5200
|
+-- Espace mémoire du processus
|
+-- Thread principal
|
+-- Thread de traitement
|
+-- Thread de journalisation
|
+-- Thread de communication
```

Les threads d'un même processus partagent généralement l'espace mémoire du processus et de nombreuses ressources, tout en disposant de leur propre contexte d'exécution.

Il faut distinguer le **PID vu par les outils classiques** et les identifiants de tâches internes au noyau, qui peuvent apparaître dans des vues détaillées des threads.

Pour afficher les threads avec `ps` :

```bash
ps -eLf
```

Les colonnes et le détail présenté dépendent de la version de `ps`.

Pour observer les threads d'un PID précis :

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

Remplace `PID` par l'identifiant réel.

Dans ce format, `LWP` indique l'identifiant de thread présenté par `ps`, et `PSR` donne le processeur logique sur lequel le thread s'est exécuté récemment ou auquel il est associé selon le format de l'outil.

Un thread qui utilise beaucoup de CPU peut expliquer une grande partie de la consommation d'une application multithread.

## 2.4. Pourquoi cette distinction est-elle utile ?

Supposons qu'une application possède dix threads.

Un relevé limité aux processus peut montrer une seule ligne d'application, alors que plusieurs threads réalisent le travail.

Le diagnostic peut donc être complété par :

```bash
top -H -p PID
```

Dans de nombreuses versions de `top`, l'option `-H` permet d'afficher les threads individuels.

Cela aide à déterminer si la charge CPU est concentrée sur un thread ou répartie entre plusieurs.

Il faut néanmoins interpréter les mesures selon les conventions de l'outil et vérifier que les threads observés appartiennent réellement au processus ciblé.


# 3. PID, PPID, PGID, SID et TPGID

## 3.1. Pourquoi le PID ne suffit-il pas ?

Au niveau débutant, le PID est l'identifiant le plus important.

Au niveau intermédiaire, il faut comprendre que Linux organise aussi les processus en groupes et en sessions.

Ces notions permettent de contrôler des ensembles de tâches, notamment dans un terminal ou dans certaines applications.

Voici les principales relations :

| Champ | Signification | Utilité |
|---|---|---|
| `PID` | Processus | Identifier une tâche précise |
| `PPID` | Processus parent | Comprendre l'origine d'un processus |
| `PGID` | Groupe de processus | Identifier un groupe de tâches lié |
| `SID` | Session de processus | Identifier une session contenant des groupes |
| `TPGID` | Groupe de processus au premier plan du terminal | Comprendre le contrôle d'un terminal |
| `TTY` | Terminal de contrôle présenté par l'outil | Identifier un terminal associé |

Le terme `SID` désigne ici l'identifiant de session de processus. Il ne faut pas le confondre avec le SID utilisé dans certains environnements Windows ou Active Directory.

## 3.2. Afficher ces informations

Examine un processus avec :

```bash
ps -o pid,ppid,pgid,sid,tpgid,tty,stat,cmd -p PID
```

Cette commande aide à comprendre :

- quel est le processus ;
- qui est son parent ;
- à quel groupe il appartient ;
- à quelle session il appartient ;
- quel groupe est associé au premier plan du terminal, lorsque cela s'applique.

Les valeurs réelles dépendent de la façon dont le processus a été lancé.

## 3.3. Exemple conceptuel

```text
SESSION DE TERMINAL
SID = 4000
|
+-- Groupe du shell
|   PGID = 4000
|   |
|   +-- bash
|
+-- Groupe d'une commande au premier plan
    PGID = 4101
    |
    +-- commande-parent
        |
        +-- processus-enfant
```

Les numéros sont fictifs.

Le PPID et le PGID ne représentent pas la même relation.

Un processus peut avoir un parent donné tout en faisant partie d'un groupe de processus utilisé pour gérer une tâche du terminal.

## 3.4. Pourquoi cette organisation existe-t-elle ?

La gestion des groupes permet au shell de contrôler une commande composée de plusieurs processus.

Par exemple, une pipeline peut contenir plusieurs commandes :

```bash
journalctl -f | grep --line-buffered ERROR | tee erreurs.log
```

Selon le contexte, le shell peut gérer cette pipeline comme un travail et organiser ses processus dans un groupe.

Lorsqu'une interruption de terminal se produit, les mécanismes de contrôle des tâches permettent d'appliquer le signal aux processus concernés.

Cela explique pourquoi un contrôle de tâche ne se limite pas toujours à un seul PID.


# 4. Groupes de processus et sessions de terminal

## 4.1. Qu'est-ce qu'un groupe de processus ?

Un groupe de processus est un ensemble de processus partageant le même PGID.

Il est souvent utilisé pour organiser les processus associés à une même tâche du shell.

```text
GROUPE DE PROCESSUS : PGID 6100
|
+-- commande principale
|
+-- processus de traitement
|
+-- processus de sortie
```

Les PID du schéma sont illustratifs.

Le groupe permet certaines opérations sur plusieurs processus appartenant au même groupe, sous réserve des règles de permission applicables.

## 4.2. Qu'est-ce qu'une session ?

Une session de processus est une organisation qui peut regrouper plusieurs groupes de processus.

Dans un terminal interactif classique :

```text
SESSION
  |
  +-- Groupe du shell
  |
  +-- Groupe de la tâche au premier plan
  |
  +-- Groupe de tâches en arrière-plan
```

Le contrôle du terminal aide à déterminer quel groupe peut interagir avec ce terminal.

Les sessions peuvent également exister sans terminal de contrôle, par exemple pour des processus de service ou des programmes exécutés de manière détachée.

## 4.3. Pourquoi `Ctrl+C` peut-il affecter plusieurs processus ?

Dans un terminal interactif utilisant le contrôle des tâches, `Ctrl+C` provoque normalement l'envoi de `SIGINT` au groupe de processus au premier plan.

Si la commande au premier plan est une pipeline, plusieurs processus peuvent donc recevoir le signal.

```text
TERMINAL
   |
   | Ctrl+C
   v
GROUPE AU PREMIER PLAN
   |
   +-- processus A reçoit SIGINT
   |
   +-- processus B reçoit SIGINT
   |
   +-- processus C reçoit SIGINT
```

Ce comportement explique pourquoi `Ctrl+C` ne doit pas être compris comme une action visant toujours un seul PID.

Il explique aussi pourquoi certains programmes terminent alors que d'autres, qui traitent spécialement le signal, peuvent continuer ou effectuer un nettoyage.

## 4.4. Afficher les groupes et sessions

Pour visualiser les principales informations :

```bash
ps -eo pid,ppid,pgid,sid,tpgid,tty,stat,cmd
```

Pour filtrer les processus associés à un PID, observe d'abord la ligne correspondante, puis relève son PGID.

Exemple :

```bash
ps -o pid,ppid,pgid,sid,tty,cmd -p PID
```

Une fois le PGID identifié, tu peux rechercher les membres du groupe :

```bash
ps -eo pid,ppid,pgid,stat,cmd | awk -v g=6100 '$3 == g'
```

Dans cet exemple, `6100` doit être remplacé par le PGID réellement observé.

Cette commande suppose que la troisième colonne de la sortie demandée est `PGID`. L'utilisation de `awk` sur une sortie formatée est adaptée à un exemple pédagogique, mais pour des outils de supervision robustes, il vaut mieux privilégier une interface structurée lorsqu'elle est disponible.

## 4.5. Attention aux signaux dirigés vers un groupe

Envoyer un signal à un groupe de processus peut affecter plusieurs processus simultanément.

Sur les systèmes qui prennent en charge la syntaxe correspondante, un PID négatif passé à `kill` peut désigner un groupe de processus.

Exemple conceptuel :

```text
SIGTERM ciblant un PID
       |
       v
Un processus précis

SIGTERM ciblant un PGID
       |
       v
Plusieurs processus du groupe
```

**Ne teste pas l'envoi d'un signal à un PGID sur un système de production.**

Une mauvaise valeur pourrait interrompre une pipeline complète, une session de travail ou un ensemble de processus qui n'étaient pas destinés à être arrêtés.

Avant toute opération de groupe, il faut confirmer le PGID et comprendre exactement quels processus sont membres du groupe.


# 5. Arbres de processus et création de processus enfants

## 5.1. Relation parent-enfant

Un processus peut créer un ou plusieurs processus enfants.

Le parent ne doit pas être confondu avec le superviseur d'une application.

Un superviseur peut lancer un processus puis en gérer le cycle de vie, mais toutes les relations parent-enfant ne sont pas nécessairement des relations de supervision.

```text
systemd
   |
   +-- service A
   |
   +-- service B
   |
   +-- service C
```

Dans cet exemple, `systemd` peut gérer les unités correspondantes. Les relations exactes entre processus dépendent de leur mode de lancement et de leur évolution.

## 5.2. Afficher un arbre

```bash
ps -ef --forest
```

Ou, si l'outil est installé :

```bash
pstree -p
```

Un arbre permet de repérer des processus enfants récurrents ou un programme qui crée continuellement d'autres processus.

## 5.3. Exemple : boucle de création de processus

Une application peut produire de nombreux processus enfants parce qu'elle traite une série de tâches.

Une création rapide et répétée de processus peut aussi être le symptôme d'une erreur.

```text
PROCESSUS PARENT
      |
      +-- enfant 1 terminé
      |
      +-- enfant 2 terminé
      |
      +-- enfant 3 terminé
      |
      +-- enfant 4 toujours actif
```

Il faut déterminer si cette activité correspond au fonctionnement normal de l'application.

Des processus enfants nombreux ne suffisent pas à conclure à un problème.

## 5.4. Comprendre les zombies et les processus orphelins

Un processus zombie a terminé, mais son parent n'a pas encore récupéré son statut de fin.

Un processus orphelin est un processus dont le parent s'est terminé avant lui. Il peut être adopté par un autre processus approprié du système.

Les deux situations sont différentes.

```text
ZOMBIE
Enfant terminé
      |
      v
Statut de fin non récupéré
      |
      v
Entrée conservée temporairement


ORPHELIN
Parent terminé
      |
      v
Enfant toujours actif
      |
      v
Réaffectation à un parent approprié
```

Un zombie persistant peut nécessiter une investigation du parent.

Un processus orphelin peut être parfaitement normal. Sa seule existence ne constitue pas un incident.

## 5.5. Compter les processus d'un utilisateur ou d'une application

Pour compter les processus appartenant à l'utilisateur courant :

```bash
ps -u "$USER" --no-headers | wc -l
```

Cette commande compte les lignes de processus affichées par `ps`. Le résultat est une observation ponctuelle et dépend du format et des filtres appliqués.

Pour rechercher un nom précis :

```bash
pgrep -a nom_application
```

Pour compter les correspondances :

```bash
pgrep -c nom_application
```

Le résultat dépend du motif de recherche et des règles de correspondance de `pgrep`.

Il faut distinguer un nombre de PID d'un nombre exact d'instances fonctionnelles d'une application : certains programmes créent des processus auxiliaires, utilisent des threads ou lancent des composants distincts.


# 6. États avancés et symptômes de blocage

## 6.1. Revoir les états Linux

Les états les plus courants restent :

| État | Interprétation |
|---|---|
| `R` | En exécution ou prêt |
| `S` | Attente interruptible |
| `D` | Attente non interruptible |
| `T` | Suspendu ou arrêté |
| `t` | Arrêté par un mécanisme de traçage, par exemple un débogueur |
| `Z` | Zombie |
| `I` | Thread noyau inactif dans les vues qui le présentent |

Les significations exactes sont définies par les outils et le noyau Linux. Consulte `man ps` pour les détails du système utilisé.

## 6.2. Lire les indicateurs supplémentaires de `STAT`

Dans `ps`, la colonne `STAT` peut contenir une lettre d'état suivie de caractères supplémentaires.

Ces caractères apportent des indications complémentaires.

Par exemple, selon le système, les indicateurs peuvent signaler :

- une session de premier plan ;
- une priorité particulière ;
- un statut multithread ;
- un comportement de mémoire verrouillée.

Ne mémorise pas mécaniquement chaque lettre secondaire. Il est préférable de savoir retrouver sa signification dans la documentation locale :

```bash
man ps
```

Cherche ensuite la section consacrée aux codes d'état.

## 6.3. Pourquoi un processus peut-il rester en état `D` ?

L'état `D` correspond généralement à une attente non interruptible dans le noyau.

Cette situation peut être liée à une opération d'entrée-sortie ou à une autre attente noyau.

Les causes possibles incluent notamment :

- une opération de stockage qui ne progresse plus ;
- un système de fichiers réseau qui ne répond pas ;
- un problème de périphérique ;
- un pilote qui rencontre une difficulté ;
- une attente liée à un mécanisme interne du noyau.

La présence d'un seul processus `D` ne suffit pas à déterminer la cause.

## 6.4. Collecter des indices sur un processus `D`

Commence par :

```bash
ps -p PID -o pid,ppid,stat,wchan:32,etime,cmd
```

La colonne `WCHAN` peut présenter le symbole ou l'indication de l'attente noyau, lorsqu'elle est accessible et disponible.

Son contenu dépend du noyau, des permissions et de la configuration. Il ne faut pas interpréter un nom de fonction isolé comme une preuve définitive.

Consulte ensuite les messages du noyau :

```bash
dmesg -T | tail -n 100
```

Si l'accès à `dmesg` est restreint, consulte les journaux système autorisés, par exemple avec `journalctl`.

Recherche des erreurs correspondant au moment du problème, notamment celles qui concernent les périphériques, les pilotes ou les systèmes de fichiers.

## 6.5. Pourquoi `SIGKILL` peut-il ne pas résoudre immédiatement un état `D` ?

`SIGKILL` ne peut pas être intercepté ou ignoré par un programme.

Cependant, il ne garantit pas que le processus disparaisse instantanément si celui-ci se trouve dans certaines attentes noyau.

La bonne démarche est donc :

```text
PROCESSUS EN D
      |
      v
Confirmer la persistance de l'état
      |
      v
Examiner l'attente et les journaux
      |
      v
Identifier la ressource en cause
      |
      v
Résoudre ou contourner la cause
      |
      v
Vérifier l'évolution du processus
```

Il faut éviter de répéter des commandes `kill -9` sans comprendre pourquoi le processus ne quitte pas son état.

## 6.6. Distinguer un blocage d'une attente normale

Un processus en état `S` peut attendre normalement une requête, un délai ou un événement.

Un processus en état `R` peut être actif, mais cela ne signifie pas nécessairement qu'il progresse utilement.

Un processus en état `D` peut attendre une opération noyau.

L'état est donc une information de diagnostic, mais il doit être relié au comportement observé, aux mesures et à la fonction de l'application.


# 7. Signaux Linux : fonctionnement et bonnes pratiques

## 7.1. Le rôle d'un signal

Un signal permet de notifier un processus d'un événement ou de lui demander une action.

La commande `kill` ne signifie pas toujours « supprimer » : elle permet d'envoyer un signal à un processus ou, dans certains cas, à un groupe.

Par défaut, la commande `kill` envoie `SIGTERM` lorsque aucun signal n'est spécifié. Cela vaut pour la commande externe et pour le builtin Bash dans leur usage courant.

## 7.2. Principaux signaux

| Signal | Fonction générale |
|---|---|
| `SIGTERM` | Demande de terminaison |
| `SIGKILL` | Terminaison forcée |
| `SIGINT` | Interruption, souvent provoquée par `Ctrl+C` |
| `SIGSTOP` | Suspension forcée |
| `SIGCONT` | Reprise d'un processus suspendu |
| `SIGTSTP` | Demande de suspension liée au contrôle du terminal, souvent provoquée par `Ctrl+Z` |
| `SIGHUP` | Historiquement associé à la déconnexion d'un terminal ; son usage dépend aussi du programme |
| `SIGCHLD` | Notification liée aux changements d'état des enfants d'un processus |

Tu peux consulter les signaux disponibles :

```bash
kill -l
```

Les numéros de signal dépendent de l'architecture pour certains signaux. Les noms symboliques sont préférables dans les scripts et la documentation.

## 7.3. `SIGTERM` et `SIGKILL`

`SIGTERM` est une demande de terminaison que l'application peut traiter.

`SIGKILL` ne peut pas être intercepté, bloqué ni ignoré par le programme.

Le choix doit dépendre de la situation :

```text
PROCESSUS À ARRÊTER
        |
        v
La cible est-elle confirmée ?
        |
        +-- NON --> Continuer le diagnostic
        |
        +-- OUI
              |
              v
L'arrêt est-il nécessaire ?
              |
              +-- NON --> Ne pas arrêter
              |
              +-- OUI
                    |
                    v
Envoyer SIGTERM si adapté
                    |
                    v
Vérifier l'état
                    |
                    v
Si nécessaire, analyser l'échec
                    |
                    v
Envisager SIGKILL uniquement
si la situation le justifie
```

## 7.4. Envoyer un signal et vérifier le résultat

Pour un PID connu :

```bash
kill -TERM PID
```

Puis :

```bash
ps -p PID -o pid,ppid,user,stat,etime,cmd
```

Un code de retour nul de `kill` signifie que le signal a été envoyé avec succès selon les règles applicables. Il ne prouve pas que le processus a terminé.

Un processus peut être encore présent après la demande d'arrêt.

## 7.5. Vérifier l'existence ou les permissions

```bash
kill -0 PID
```

Le signal numéro zéro permet notamment de vérifier si le processus est présent et si l'appelant dispose des permissions requises pour lui envoyer des signaux.

Il ne teste pas la santé fonctionnelle de l'application.

Il faut aussi garder à l'esprit qu'un PID peut être réutilisé après la fin d'un processus. Une vérification fondée sur un PID stocké longtemps peut donc viser une autre instance si elle n'est pas accompagnée d'autres contrôles.

## 7.6. Les pièges de `pkill` et `killall`

Des outils tels que `pkill` et `killall` permettent de viser des processus par nom ou motif.

Ils peuvent être utiles, mais leur portée peut être plus large qu'attendu.

Par exemple :

```bash
pgrep -a nom_application
```

est une étape de recherche, pas une commande d'arrêt.

Avant de viser plusieurs processus :

1. examine les correspondances ;
2. vérifie les utilisateurs ;
3. repère les différences entre les commandes ;
4. identifie les services concernés ;
5. sélectionne les cibles avec précision.

N'utilise pas un motif générique comme `python`, `java` ou `worker` pour terminer des processus de production sans analyse préalable.

## 7.7. Le rôle de `SIGHUP`

`SIGHUP` n'a pas un effet universel de rechargement de configuration.

Certaines applications l'utilisent pour relire leur configuration, d'autres ont un comportement différent.

Avant d'envoyer ce signal à un service, consulte la documentation de l'application.

Lorsqu'un service est géré par `systemd`, il est souvent préférable d'utiliser son mécanisme de rechargement si celui-ci est déclaré et pris en charge :

```bash
systemctl reload nom.service
```

Cette commande ne convient que si le service prend en charge une opération de rechargement.

Si ce n'est pas le cas, il faut utiliser la procédure documentée pour l'application concernée.


# 8. Identification fiable d'un processus

## 8.1. Le problème de la réutilisation des PID

Un PID est unique pour un processus donné dans son espace de PID pendant la durée de vie pertinente, mais il peut être réutilisé après la disparition du processus.

Cela crée un risque dans les scripts ou procédures qui conservent des PID pendant longtemps.

Scénario :

```text
08:00 : application A démarre avec PID 5000
08:10 : application A se termine
08:12 : une autre application reçoit le PID 5000
08:20 : un script utilise encore l'ancien PID 5000
```

Le script peut alors examiner ou viser la mauvaise cible.

Ce scénario est illustratif, mais il met en évidence un problème réel de conception.

## 8.2. Contrôler plusieurs informations

Pour limiter ce risque, examine plusieurs propriétés :

```bash
ps -p PID -o pid,ppid,user,lstart,etime,cmd
```

Les colonnes demandées comprennent :

- le PID ;
- le PPID ;
- l'utilisateur ;
- la date de lancement présentée par l'outil ;
- le temps écoulé ;
- la commande.

Comparer plusieurs caractéristiques rend une vérification plus fiable qu'une recherche sur le seul nom.

Cela ne fournit pas une garantie absolue d'identité permanente, mais aide à confirmer la cible avant une action.

## 8.3. `pgrep` pour découvrir et non décider automatiquement

Pour rechercher des processus :

```bash
pgrep -a -f 'motif'
```

L'option `-f` utilise la ligne de commande complète pour la correspondance.

Cela peut être utile, mais peut également entraîner des correspondances supplémentaires.

La chaîne doit être suffisamment précise pour limiter les faux positifs.

Exemple :

```bash
pgrep -a -f 'script_traitement.py --mode test'
```

Cette recherche n'est illustrative que si cette commande est réellement utilisée sur la machine.

Pour une administration sûre, vérifie toujours les résultats avant d'envoyer un signal.

## 8.4. Vérifier les arguments et le contexte

Une application peut être lancée avec le même nom mais avec des options différentes :

```text
application --mode test
application --mode production
```

Ces deux commandes peuvent représenter des usages très différents.

L'identification par nom seul peut donc être insuffisante.

Une vérification rigoureuse prend en compte le PID, les arguments, le propriétaire, le PPID, le service éventuel et le contexte de l'application.


# 9. Maîtriser les possibilités de `ps`

## 9.1. Construire un affichage adapté au diagnostic

Plutôt que d'afficher toutes les colonnes, sélectionne celles qui répondent à la question.

Exemple :

```bash
ps -eo pid,ppid,pgid,sid,user,stat,ni,pri,pcpu,pmem,etime,cmd
```

Cette commande donne une vue détaillée des processus visibles.

Les colonnes suivantes sont particulièrement utiles :

| Colonne | Utilité |
|---|---|
| `PID` | Identifier le processus |
| `PPID` | Examiner le parent |
| `PGID` | Examiner le groupe |
| `SID` | Examiner la session |
| `USER` | Identifier l'utilisateur effectif affiché |
| `STAT` | Lire l'état |
| `NI` | Observer nice |
| `PRI` | Observer la priorité présentée par l'outil |
| `PCPU` | Consulter l'indication CPU |
| `PMEM` | Consulter l'indication mémoire |
| `ETIME` | Temps écoulé |
| `CMD` | Examiner la commande |

`PCPU` et `PMEM` peuvent être reconnus comme noms de spécificateurs par `ps` selon les versions ; si une variante ne fonctionne pas, consulte le manuel local et utilise les spécificateurs compatibles, souvent `%cpu` et `%mem`.

## 9.2. Sélectionner un PID

```bash
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

Cette commande est adaptée à l'examen d'une cible déjà identifiée.

## 9.3. Sélectionner par nom d'exécutable

Avec une version courante de `ps` :

```bash
ps -C nom_programme -o pid,ppid,user,stat,cmd
```

La sélection `-C` se fonde sur le nom de commande de l'exécutable, pas nécessairement sur la ligne de commande complète.

Il ne faut pas supposer que ce filtre trouvera toutes les formes possibles d'un script ou d'une application.

## 9.4. Examiner l'évolution dans le temps

`ps` fournit généralement un instantané.

Pour obtenir plusieurs mesures, tu peux l'exécuter périodiquement :

```bash
watch -n 2 'ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15'
```

`watch` réexécute la commande à l'intervalle demandé, ici environ deux secondes.

L'actualisation est utile pour voir si une tendance évolue, mais chaque sortie reste une mesure instantanée. Les valeurs peuvent être bruitées ou dépendre de la période de calcul du champ CPU.

Pour suivre précisément les statistiques de tâches au cours du temps, `pidstat` est souvent plus adapté.

## 9.5. Comparer `ps` et `top`

Le pourcentage CPU affiché par `ps` peut dépendre de la durée de vie du processus ou des conventions de calcul de la version utilisée. Il ne faut pas l'interpréter comme une mesure instantanée strictement équivalente à toutes les mesures de `top`.

`top` actualise les statistiques périodiquement et permet d'observer les variations.

Une méthode utile consiste à :

1. utiliser `top` pour repérer le symptôme ;
2. identifier le PID ;
3. utiliser `ps` pour examiner ses informations détaillées ;
4. utiliser `pidstat` ou un autre outil de mesure temporelle pour confirmer la tendance.


# 10. Exploiter `top` pour le diagnostic

## 10.1. Les informations générales

Lance :

```bash
top
```

Les premières lignes affichent notamment la charge moyenne, les tâches et des statistiques CPU et mémoire.

La présentation exacte dépend de la version de `top`.

### Charge moyenne

La charge moyenne est une mesure de la charge du système, sur plusieurs périodes.

Elle ne doit pas être interprétée directement comme un pourcentage CPU.

Elle dépend notamment du nombre de processeurs logiques et des tâches exécutables ou dans certaines attentes noyau.

### CPU

Dans les vues courantes de `top`, les colonnes CPU peuvent séparer différentes catégories :

- temps utilisateur ;
- temps noyau ;
- temps associé aux tâches de priorité modifiée ;
- temps d'inactivité ;
- attente d'entrées-sorties ;
- autres catégories prévues par la version.

Une forte part de temps noyau n'a pas nécessairement la même cause qu'une forte part de calcul en espace utilisateur.

Une forte attente d'entrées-sorties peut orienter le diagnostic vers le stockage ou les opérations bloquantes, mais elle ne constitue pas, à elle seule, la preuve d'une panne.

## 10.2. Observer un seul processus

Tu peux lancer :

```bash
top -p PID
```

Pour afficher les threads :

```bash
top -H -p PID
```

Cette méthode est utile lorsque tu as déjà identifié la cible.

## 10.3. Les raccourcis interactifs

Les raccourcis courants incluent :

- `P` : tri selon le CPU ;
- `M` : tri selon la mémoire ;
- `T` : tri selon le temps CPU cumulé dans les versions qui le proposent ;
- `1` : affichage individuel des processeurs logiques dans les vues qui le prennent en charge ;
- `q` : quitter.

Les raccourcis peuvent dépendre de la version et de la configuration de `top`.

## 10.4. Un pourcentage CPU supérieur à 100 %

Sur un système multicœur, certains outils peuvent présenter pour un processus multithread un pourcentage CPU supérieur à 100 %, si leur convention de calcul permet d'exprimer l'utilisation de plusieurs processeurs logiques.

Une valeur de 200 % peut ainsi correspondre à l'utilisation d'environ deux processeurs logiques selon cette convention.

Il ne faut pas considérer cette valeur comme une anomalie automatique.

Il faut tenir compte du nombre de processeurs logiques, de la méthode de calcul et de la durée de mesure.


# 11. Mesures historiques avec `pidstat`, `vmstat` et `iostat`

## 11.1. Pourquoi introduire d'autres outils ?

`ps` et `top` sont très utiles, mais ne répondent pas à toutes les questions.

Pour comprendre une tendance, il faut parfois enregistrer des mesures successives et comparer leurs évolutions.

Les outils du paquet `sysstat` apportent notamment des statistiques sur les tâches, la mémoire virtuelle, le CPU et les entrées-sorties.

Ils ne sont pas nécessairement installés par défaut.

## 11.2. Utiliser `pidstat`

`pidstat` permet de suivre l'activité des tâches sur plusieurs intervalles.

Pour surveiller les statistiques CPU du système toutes les secondes, pendant cinq relevés :

```bash
pidstat 1 5
```

Pour cibler un PID :

```bash
pidstat -p PID 1 5
```

Selon les options prises en charge, tu peux aussi demander plusieurs types de statistiques :

```bash
pidstat -dru -p PID 1 5
```

Les options courantes correspondent notamment à :

- `-d` : statistiques d'entrées-sorties ;
- `-r` : statistiques mémoire ;
- `-u` : statistiques CPU.

Vérifie `man pidstat` si les options disponibles sur ta distribution diffèrent.

### Exemple d'interprétation

Supposons qu'un processus utilise peu de CPU, mais présente une activité élevée d'entrées-sorties.

Cette observation peut orienter la recherche vers des opérations de lecture et d'écriture, sans démontrer à elle seule que le disque est défectueux.

Les mesures doivent être comparées à celles du système et aux besoins réels de l'application.

## 11.3. Utiliser `vmstat`

```bash
vmstat 1 5
```

Cette commande demande plusieurs relevés, espacés d'environ une seconde.

Les colonnes peuvent renseigner sur :

- les processus exécutables et bloqués ;
- les interruptions et changements de contexte ;
- l'activité CPU ;
- la mémoire ;
- le swap ;
- certaines activités d'entrée-sortie.

**Attention : le premier relevé de `vmstat` est généralement une moyenne calculée depuis le démarrage. Les relevés suivants représentent les intervalles successifs.**

Il faut donc éviter d'interpréter la première ligne comme si elle représentait exactement la même période que les lignes suivantes.

### Pourquoi le contexte importe-t-il ?

Une hausse des changements de contexte peut être liée à un nombre élevé de tâches, à des synchronisations ou à d'autres aspects de l'exécution.

Elle ne suffit pas à identifier une cause unique.

De même, une activité de swap peut mériter une investigation, mais elle doit être comparée à la mémoire disponible et au comportement des applications.

## 11.4. Utiliser `iostat`

Si `sysstat` est installé :

```bash
iostat -xz 1 5
```

Les options et colonnes détaillées dépendent de la version.

Cet outil fournit notamment des informations sur l'activité CPU et les périphériques de stockage.

Des statistiques telles que la taille des transferts, les opérations par seconde, le débit et les temps d'attente peuvent aider à comprendre les performances d'entrée-sortie.

Il ne faut toutefois pas utiliser un pourcentage isolé comme preuve définitive d'une panne : l'interprétation dépend du type de périphérique, de sa capacité et du profil de charge.

## 11.5. Quelle mesure choisir ?

| Problème | Point de départ | Complément |
|---|---|---|
| Processus consommant du CPU | `top` | `pidstat` |
| Utilisation mémoire élevée | `free -h`, `ps` | `pidstat -r` |
| Activité d'entrée-sortie | `iostat` | `pidstat -d` |
| Pression globale sur la mémoire et le CPU | `vmstat` | Journaux et `free` |
| Arbre de processus complexe | `ps --forest` | `pstree` |
| Application indisponible | `systemctl status` | `journalctl` et `ps` |

Le meilleur outil est celui qui mesure le phénomène concerné et dont le résultat est compris dans son contexte.


# 12. Diagnostiquer CPU, mémoire, entrées-sorties et charge

## 12.1. La différence entre symptôme et cause

Une machine lente peut résulter de plusieurs mécanismes.

```text
MACHINE LENTE
     |
     +-- CPU saturé
     |
     +-- Mémoire sous pression
     |
     +-- Opérations de stockage lentes
     |
     +-- Dépendance réseau indisponible
     |
     +-- Processus bloqués
     |
     +-- Limite de ressources
     |
     +-- Erreur applicative
```

Aucun de ces mécanismes ne doit être considéré comme la cause sans preuve.

Un pourcentage CPU élevé n'explique pas forcément une application indisponible. Une consommation mémoire élevée ne signifie pas nécessairement qu'une fuite mémoire est présente.

## 12.2. Cas A : CPU élevé

Étape 1 :

```bash
top
```

Étape 2 :

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15
```

Étape 3 : suivre les mesures du PID :

```bash
pidstat -p PID 1 5
```

Étape 4 : examiner le contexte :

- le processus effectue-t-il une opération attendue ?
- s'agit-il d'un calcul ponctuel ?
- un seul thread concentre-t-il la charge ?
- le processus est-il redémarré en boucle ?
- l'application produit-elle des erreurs ?
- une limite CPU s'applique-t-elle au service ?

Les commandes `pidstat` et `top` ne sont pas les seules solutions possibles, mais elles fournissent un bon point de départ.

## 12.3. Cas B : mémoire élevée

Afficher la mémoire :

```bash
free -h
```

Rechercher les principaux consommateurs :

```bash
ps -eo pid,ppid,user,%mem,rss,etime,cmd --sort=-%mem | head -n 15
```

Observer les tendances avec `pidstat` si disponible :

```bash
pidstat -r 1 5
```

Questions à poser :

- La consommation augmente-t-elle continuellement ?
- Plusieurs processus partagent-ils une partie de leur mémoire ?
- Le cache du noyau contribue-t-il à l'utilisation affichée ?
- La machine utilise-t-elle du swap ?
- Le processus est-il soumis à une limite mémoire ?
- Une application vient-elle de recevoir une charge inhabituelle ?

Pour démontrer une fuite mémoire, il faut examiner une tendance et comprendre le comportement attendu de l'application.

## 12.4. Cas C : activité d'entrée-sortie élevée

Commence par des observations générales :

```bash
vmstat 1 5
```

Puis, si disponible :

```bash
iostat -xz 1 5
```

Pour une tâche connue :

```bash
pidstat -d -p PID 1 5
```

L'objectif est de déterminer si l'activité d'entrée-sortie est concentrée sur un processus ou reflète la charge globale de la machine.

Une forte activité d'entrée-sortie peut être normale pour une base de données, une sauvegarde ou une opération d'indexation.

## 12.5. Cas D : processus apparemment bloqué

Collecte d'abord :

```bash
ps -p PID -o pid,ppid,user,stat,wchan:32,etime,cmd
```

Examine ensuite les journaux pertinents et les dépendances de l'application.

Si nécessaire, vérifie également si la machine attend une ressource externe.

Un processus en attente n'est pas nécessairement défectueux. La question essentielle est de savoir si cette attente correspond au comportement attendu et si elle empêche la progression du travail.

## 12.6. Cas E : limites de ressources

Une application peut sembler ralentie sans saturer toute la machine.

Exemples :

- CPU limité par le service ;
- mémoire plafonnée par un groupe de contrôle ;
- nombre de tâches limité ;
- contrainte d'affinité CPU ;
- limitation appliquée par un environnement de conteneur.

Dans ce cas, il faut examiner la configuration du service et des groupes de contrôle en plus des statistiques globales.

Une machine disposant de ressources libres peut héberger une application qui atteint néanmoins sa limite individuelle.


# 13. Fichiers ouverts, descripteurs et répertoires de processus

## 13.1. Les descripteurs de fichiers

Un processus peut maintenir ouverts des fichiers, des sockets, des tubes et d'autres objets manipulés au travers de descripteurs.

Cette information explique pourquoi un processus peut continuer à utiliser une ressource alors que le fichier semble avoir disparu du répertoire.

Un processus peut également détenir un grand nombre de descripteurs, ce qui peut contribuer à certaines pannes.

## 13.2. Examiner les descripteurs via `/proc`

Sur un système Linux, les descripteurs d'un processus peuvent apparaître sous :

```bash
ls -l /proc/PID/fd
```

Remplace `PID` par l'identifiant réel du processus.

Selon les permissions, certaines informations peuvent ne pas être accessibles.

Une sortie illustrative peut ressembler à :

```text
0 -> /dev/null
1 -> /var/log/application.log
2 -> /var/log/application-error.log
3 -> socket:[123456]
```

Les numéros de descripteur et les cibles sont fictifs.

Les descripteurs `0`, `1` et `2` correspondent conventionnellement à l'entrée standard, à la sortie standard et à la sortie d'erreur standard, mais leur redirection dépend du lancement du processus.

## 13.3. Utiliser `lsof`

Si l'outil est installé :

```bash
lsof -p PID
```

Il peut afficher les fichiers et certaines autres ressources ouvertes par le processus.

Cet outil est utile pour examiner :

- les fichiers ouverts ;
- les journaux ;
- certains sockets ;
- les fichiers supprimés mais encore ouverts ;
- le nombre et la nature des descripteurs.

Une sortie de `lsof` peut être volumineuse. Il faut sélectionner les informations pertinentes.

## 13.4. Un fichier supprimé mais encore utilisé

Un programme peut continuer à utiliser un fichier après que son entrée de répertoire a été supprimée, tant que le fichier reste référencé par des descripteurs ouverts ou d'autres références du système.

Cela peut expliquer qu'un espace disque ne soit pas libéré immédiatement après la suppression d'un journal.

Démarche de diagnostic possible :

1. vérifier l'espace disque ;
2. rechercher des fichiers supprimés mais encore ouverts ;
3. identifier le processus qui les détient ;
4. comprendre pourquoi ce processus les garde ouverts ;
5. utiliser la procédure appropriée pour fermer ou faire tourner les journaux.

Ne termine pas automatiquement un processus important pour récupérer de l'espace disque sans évaluer ses conséquences.

## 13.5. Examiner le répertoire de travail et l'exécutable

Les liens suivants peuvent fournir des informations utiles :

```bash
readlink "/proc/PID/cwd"
```

```bash
readlink "/proc/PID/exe"
```

Le premier indique le répertoire de travail du processus, lorsque l'information est accessible.

Le second indique le chemin de l'exécutable associé au processus, lorsqu'il est disponible.

Ces informations sont utiles lorsqu'une commande est lancée depuis un répertoire inattendu ou lorsqu'un processus est difficile à identifier.

Le contenu peut être inaccessible ou changer entre deux observations. Les permissions d'accès doivent être respectées.


# 14. Tâches Bash avancées : `wait`, `disown`, `nohup` et `timeout`

## 14.1. Les tâches connues du shell

Dans une session Bash interactive, le contrôle des tâches permet de suivre les commandes exécutées au premier plan ou en arrière-plan.

```bash
jobs -l
```

Cette commande ne répertorie pas tous les processus du système.

Elle présente les tâches connues du shell courant.

Le numéro de tâche, comme `%1`, ne doit pas être confondu avec un PID ou un PGID.

## 14.2. Comprendre `$!`

Après le lancement d'une commande en arrière-plan :

```bash
sleep 30 &
PID=$!
```

`$!` permet de récupérer le PID du dernier travail asynchrone lancé par le shell.

C'est préférable à une recherche approximative du PID à partir du nom du programme.

## 14.3. Utiliser `wait`

Exemple :

```bash
sleep 3 &
PID=$!

wait "$PID"
STATUS=$?

printf 'Code de retour : %s\n' "$STATUS"
```

`wait` attend ici la fin du processus enfant connu du shell et permet de récupérer son statut de retour.

Le code de retour est placé dans une variable immédiatement après `wait`, car toute commande suivante peut remplacer `$?`.

Si un script lance plusieurs tâches, il doit organiser leur attente et leur récupération de statut de façon explicite.

## 14.4. Attendre plusieurs tâches

Exemple de script simple :

```bash
#!/usr/bin/env bash

set -u

sleep 2 &
PID1=$!

sleep 4 &
PID2=$!

wait "$PID1"
STATUS1=$?

wait "$PID2"
STATUS2=$?

printf 'Tâche 1 : %s\n' "$STATUS1"
printf 'Tâche 2 : %s\n' "$STATUS2"
```

Les deux tâches sont lancées en arrière-plan. Le script récupère ensuite leur statut.

Cette structure est pédagogique. Pour un script de production, il faut prévoir les interruptions, les erreurs de lancement, le nettoyage des tâches et les cas dans lesquels un processus se termine avant les autres.

## 14.5. `disown`

Dans Bash interactif, `disown` modifie la manière dont le shell suit une tâche.

Exemples :

```bash
jobs -l
```

Puis, si une tâche de test connue existe :

```bash
disown %1
```

Cette commande retire la tâche désignée de la table des tâches de Bash dans l'usage courant.

`disown -h` permet de marquer une tâche pour que Bash ne lui envoie pas `SIGHUP` lorsque le shell reçoit ce signal, selon le comportement documenté du shell.

**`disown` ne transforme pas un processus en service fiable et ne garantit pas à lui seul qu'il survivra à une fermeture de session, à une panne ou à un redémarrage.**

Il ne remplace pas un gestionnaire de services adapté.

## 14.6. `nohup`

`nohup` permet de lancer une commande de façon à ce qu'elle ignore `SIGHUP`.

Exemple de test :

```bash
nohup sleep 300 > /tmp/sleep-test.log 2>&1 &
PID=$!

printf 'PID : %s\n' "$PID"
```

Ce lancement illustre le mécanisme. Dans un environnement partagé, veille à choisir un emplacement de journal approprié et à nettoyer les fichiers de test après usage.

La redirection :

```bash
> /tmp/sleep-test.log 2>&1
```

redirige la sortie standard vers le fichier et redirige ensuite la sortie d'erreur standard vers la même destination.

`nohup` n'est pas un superviseur. Il ne redémarre pas automatiquement le processus en cas d'échec et ne remplace pas la gestion d'un service.

## 14.7. Pourquoi `&` ne suffit-il pas pour un travail durable ?

Le symbole `&` indique au shell de lancer la commande de manière asynchrone.

Il ne garantit pas :

- une reprise après redémarrage ;
- une supervision ;
- un redémarrage après échec ;
- une journalisation adaptée ;
- un contrôle des ressources ;
- une gestion complète de la fermeture de la session.

Pour une application durable, un service géré par `systemd` ou un autre superviseur adapté est généralement plus fiable.

## 14.8. Limiter la durée d'une commande avec `timeout`

L'utilitaire `timeout` permet d'imposer une limite de durée.

Exemple :

```bash
timeout 10s sleep 30
```

La commande s'arrête normalement lorsqu'elle atteint la limite, selon le comportement des signaux et de l'application.

Pour demander explicitement `SIGTERM` après cinq secondes :

```bash
timeout --signal=TERM 5s sleep 30
```

Il est également possible de prévoir un délai avant un signal forcé :

```bash
timeout --signal=TERM --kill-after=5s 10s commande
```

La dernière commande est un modèle à adapter : remplace `commande` par un programme et des arguments réels.

La séquence est généralement la suivante :

```text
LANCEMENT
   |
   v
EXÉCUTION JUSQU'À LA LIMITE
   |
   v
SIGTERM
   |
   v
DÉLAI DE GRÂCE
   |
   v
SIGKILL SI NÉCESSAIRE
```

L'effet exact dépend de l'application, de la hiérarchie de processus et des options utilisées. Ne suppose pas que toutes les tâches descendantes seront nécessairement contrôlées de la même manière dans toutes les configurations.


# 15. Automatiser la supervision avec Bash

## 15.1. Pourquoi automatiser ?

Sur un système administré, certaines vérifications sont répétitives :

- vérifier la présence d'un processus ;
- relever sa consommation ;
- compter les processus ;
- vérifier un service ;
- enregistrer un résultat ;
- détecter une situation qui nécessite une inspection humaine.

Un script peut standardiser ces vérifications.

Il doit néanmoins rester prudent. Un script qui prend automatiquement des décisions destructrices à partir d'une seule mesure peut aggraver un incident.

## 15.2. Premier script : vérifier un PID

Créer un fichier :

```bash
nano verifier-processus.sh
```

Contenu :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s PID\n' "$0" >&2
    exit 2
fi

PID=$1

if [[ ! "$PID" =~ ^[0-9]+$ ]] || [[ "$PID" -eq 0 ]]; then
    printf 'Erreur : PID invalide.\n' >&2
    exit 2
fi

if ps -p "$PID" -o pid=,ppid=,user=,stat=,etime=,cmd=; then
    printf 'Processus visible : PID %s\n' "$PID"
else
    printf 'Aucun processus correspondant visible pour PID %s.\n' "$PID"
    exit 1
fi
```

Rendre le script exécutable :

```bash
chmod +x verifier-processus.sh
```

Lancer la vérification sur un PID connu :

```bash
./verifier-processus.sh 1234
```

`1234` est ici un exemple. Utilise un PID présent sur ta machine.

### Explication

- `#!/usr/bin/env bash` indique l'interpréteur souhaité ;
- `set -u` aide à détecter l'utilisation de variables non définies ;
- `$#` donne le nombre d'arguments ;
- `$1` représente le premier argument ;
- la vérification numérique limite les erreurs de saisie ;
- `ps` récupère les informations du processus ;
- `exit` renvoie un statut au shell appelant.

Ce script effectue une observation. Il n'envoie aucun signal.

## 15.3. Limite de la validation d'un PID

Vérifier qu'un argument est numérique ne garantit pas que le processus existe.

De plus, même un PID présent peut être réutilisé entre deux contrôles.

Pour les actions sensibles, le script doit vérifier le contexte de la cible, et ne pas se contenter d'une validation de forme.

## 15.4. Deuxième script : surveiller un service

Sur un système utilisant `systemd`, créer :

```bash
nano surveiller-service.sh
```

Contenu :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s nom.service\n' "$0" >&2
    exit 2
fi

SERVICE=$1

if ! command -v systemctl >/dev/null 2>&1; then
    printf 'Erreur : systemctl est indisponible.\n' >&2
    exit 2
fi

printf '%s\n' "=== État du service : $SERVICE ==="

if systemctl is-active --quiet "$SERVICE"; then
    printf 'État : actif\n'
else
    printf 'État : non actif ou état non confirmé\n'
    systemctl status "$SERVICE" --no-pager
    exit 1
fi

printf '\n%s\n' "=== PID principal déclaré ==="
systemctl show "$SERVICE" -p MainPID

printf '\n%s\n' "=== Groupe de contrôle ==="
systemctl show "$SERVICE" -p ControlGroup
```

Rendre le script exécutable :

```bash
chmod +x surveiller-service.sh
```

Exemple d'utilisation :

```bash
./surveiller-service.sh ssh.service
```

Le nom doit correspondre à un service réellement installé sur la machine. Selon la distribution, il peut être différent.

### Limites de ce script

Un service peut être actif tout en présentant un dysfonctionnement applicatif. Le script vérifie l'état rapporté par le gestionnaire, mais ne teste pas toutes les fonctions du service.

Pour confirmer la disponibilité d'une application, il faut éventuellement ajouter un test adapté à son protocole ou à son interface.

## 15.5. Journaliser les mesures

Un script de surveillance peut enregistrer la date et le résultat :

```bash
#!/usr/bin/env bash

set -u

DATE=$(date '+%F %T')

printf '[%s] Début du relevé\n' "$DATE"
uptime
free -h
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 10
```

Ce modèle affiche les mesures dans le terminal.

Pour l'utiliser dans un laboratoire avec une journalisation persistante, tu peux rediriger la sortie vers un fichier dont tu maîtrises les permissions et la durée de conservation.

Les fichiers de mesure peuvent contenir des noms de processus, des arguments ou des informations d'environnement. Ils doivent donc être gérés comme des données d'administration.

## 15.6. Pourquoi une surveillance automatique doit-elle être prudente ?

Une règle telle que « arrêter tout processus qui dépasse 80 % de CPU » est trop simpliste.

Elle pourrait interrompre :

- une compilation attendue ;
- une sauvegarde ;
- une indexation ;
- un calcul scientifique ;
- une opération de maintenance ;
- une application qui traite normalement une charge élevée.

Une surveillance robuste commence par collecter les mesures et signaler les anomalies. Les actions automatiques doivent être encadrées par des règles précises, testées et documentées.


# 16. Codes de retour et gestion des erreurs

## 16.1. Comprendre le code de retour

Dans un shell, une commande renvoie généralement un code de retour.

La convention habituelle est :

- `0` : réussite ;
- non nul : erreur ou résultat particulier.

Un code non nul ne signifie pas nécessairement une panne du système. Il peut signaler que la recherche n'a trouvé aucun résultat ou que la condition attendue n'est pas satisfaite.

## 16.2. Récupérer le code de retour

Exemple :

```bash
ps -p 1 >/dev/null
STATUS=$?

printf 'Code : %s\n' "$STATUS"
```

La variable `STATUS` contient le code de retour de `ps`.

Cette méthode est utile dans un script lorsque l'on souhaite conserver le code pour une décision ultérieure.

## 16.3. Utiliser une condition

```bash
if ps -p 1 >/dev/null 2>&1; then
    printf 'Le PID 1 est visible.\n'
else
    printf 'Aucune ligne correspondant au PID 1 n'a été trouvée.\n'
fi
```

L'exemple vérifie la visibilité d'un PID dans le contexte d'exécution. Il ne prouve pas que le système fonctionne correctement.

## 16.4. Attention à `set -e`

De nombreux scripts Bash utilisent :

```bash
set -e
```

Cette option fait quitter le shell sur certaines erreurs de commandes, sous réserve de règles particulières concernant les conditions, les listes et les fonctions.

Elle peut améliorer la détection d'erreurs simples, mais ne remplace pas la conception d'une gestion explicite des erreurs.

Pour un script de supervision, il peut être préférable de traiter explicitement les codes de retour des commandes dont l'échec est attendu ou significatif.

## 16.5. Exemple : distinguer absence et erreur

Une commande de recherche de processus peut ne retourner aucune correspondance sans qu'il y ait de problème d'exécution de l'outil.

Le script doit distinguer :

- une recherche valide sans correspondance ;
- une erreur d'utilisation ;
- un outil absent ;
- une permission insuffisante ;
- une autre erreur d'exécution.

L'analyse exacte dépend de la commande utilisée et de ses codes de retour documentés.


# 17. Priorités d'ordonnancement et affinité CPU

## 17.1. La valeur de nice

Pour les processus ordinaires, la valeur de nice influence la priorité relative de planification.

La plage courante s'étend de `-20` à `19` :

```text
-20                    0                     +19
  |--------------------|-----------------------|
Plus favorable       Standard             Moins favorable
```

Une valeur de nice plus positive rend le processus moins favorisé relativement aux tâches comparables.

Cela n'impose pas un pourcentage de CPU précis et ne garantit pas un délai d'exécution particulier.

## 17.2. Lancer une tâche avec une valeur différente

Exemple de laboratoire :

```bash
nice -n 10 sleep 60 &
PID=$!
```

Vérifier ensuite :

```bash
ps -p "$PID" -o pid,ni,pri,stat,cmd
```

La colonne `NI` permet de consulter la valeur de nice.

L'effet réel des priorités dépend des autres tâches, de la politique d'ordonnancement et du contexte de la machine.

## 17.3. Modifier la valeur avec `renice`

```bash
renice 10 -p PID
```

Cette commande demande une valeur de nice de `10` pour le PID indiqué.

Pour un utilisateur ordinaire, les possibilités de modification sont limitées par les permissions et la configuration du système.

Une priorité plus favorable nécessite généralement des privilèges adaptés.

Avant de modifier une priorité, vérifie le rôle du processus et l'objectif recherché.

## 17.4. Affinité CPU

L'affinité CPU permet de restreindre les processeurs logiques sur lesquels une tâche peut s'exécuter.

Sur Linux, `taskset` peut être utilisé pour consulter ou modifier le masque d'affinité d'un processus lorsque les permissions et les possibilités du système le permettent.

Pour consulter l'affinité d'un PID :

```bash
taskset -pc PID
```

Pour voir les CPU autorisés pour ta session, vérifie également les informations disponibles dans :

```bash
lscpu
```

La sortie et les possibilités dépendent de la machine et de son environnement.

**Ne modifie pas l'affinité d'un processus de production sans avoir identifié les conséquences.** Une affinité trop restrictive peut réduire les performances ou interagir défavorablement avec une configuration déjà limitée par un conteneur ou un service.


# 18. Processus, services et groupes de contrôle

## 18.1. Pourquoi `systemd` est-il important ?

Dans de nombreuses distributions Linux modernes, `systemd` sert de gestionnaire de services.

Il peut gérer le cycle de vie des applications, leurs dépendances, leur démarrage, leur arrêt, leurs journaux et certaines limites de ressources.

Une application administrée comme service ne doit pas être traitée uniquement comme un PID isolé.

```text
SYSTEMD
   |
   v
UNITÉ DE SERVICE
   |
   +-- Processus principal
   |
   +-- Processus auxiliaires éventuels
   |
   +-- Threads
   |
   +-- Ressources associées
       +-- CPU
       +-- Mémoire
       +-- Tâches
```

Un service peut comporter plusieurs processus et bénéficier de règles de supervision et de gestion des ressources.

## 18.2. Les groupes de contrôle — cgroups

Les groupes de contrôle, ou **cgroups**, permettent au noyau d'organiser des ensembles de processus pour contrôler ou comptabiliser certaines ressources.

Selon la configuration et les contrôleurs activés, ils peuvent aider à gérer :

- l'utilisation du CPU ;
- la mémoire ;
- le nombre de tâches ;
- l'affinité CPU ;
- d'autres ressources disponibles dans la hiérarchie.

`systemd` utilise les groupes de contrôle pour administrer de nombreux services et leurs ressources.

## 18.3. Processus individuel et groupe de contrôle

Un PID identifie un processus individuel.

Un groupe de contrôle regroupe les tâches appartenant à une unité ou à un ensemble déterminé.

```text
PID
 |
 v
Un processus individuel


CGROUP
 |
 +-- Processus principal
 |
 +-- Processus enfant A
 |
 +-- Processus enfant B
 |
 +-- Autres tâches associées
```

Les relations exactes dépendent du service et de son mode de fonctionnement.

La gestion du cycle de vie et des ressources d'une application peut donc nécessiter de regarder au-delà du PID principal.

## 18.4. Pourquoi une machine peut-elle avoir des ressources libres alors qu'un service est limité ?

Supposons qu'une machine dispose de plusieurs processeurs logiques, mais qu'un service ait un quota CPU.

Le service peut atteindre sa limite même si d'autres ressources CPU paraissent disponibles au niveau global.

De même, un service peut atteindre sa limite mémoire sans que toute la mémoire physique de la machine soit consommée.

Le diagnostic doit distinguer :

- les ressources globales ;
- les limites du service ;
- les limites de ses unités parentes ;
- les contraintes éventuelles du conteneur ou de l'environnement.


# 19. Superviser un service avec `systemd`

## 19.1. Examiner le statut

```bash
systemctl status nom.service
```

Remplace `nom.service` par une unité existante.

Cette commande peut présenter :

- l'état de l'unité ;
- le PID principal ;
- des informations de lancement ;
- des messages de journal récents ;
- l'état de certains processus associés.

Elle ne remplace pas une vérification fonctionnelle de l'application.

## 19.2. Identifier le PID principal et le groupe de contrôle

```bash
systemctl show nom.service -p MainPID -p ControlGroup
```

`MainPID` donne le PID principal déclaré par le gestionnaire lorsque cette information s'applique.

`ControlGroup` indique le chemin du groupe de contrôle associé à l'unité selon la configuration.

Un `MainPID` nul ou absent peut avoir une signification différente selon le type de service et son état.

Il faut interpréter le résultat dans le contexte de l'unité.

## 19.3. Examiner l'état d'activité

```bash
systemctl is-active nom.service
```

Pour obtenir une réponse utilisable dans un script :

```bash
if systemctl is-active --quiet nom.service; then
    printf 'Service actif\n'
else
    printf 'Service non actif ou état non confirmé\n'
fi
```

Un statut actif ne garantit pas que le service répond correctement aux requêtes applicatives.

## 19.4. Arrêter et redémarrer un service

Les commandes générales sont :

```bash
systemctl stop nom.service
```

```bash
systemctl restart nom.service
```

Ces actions peuvent interrompre des connexions ou un traitement en cours.

Avant un arrêt ou un redémarrage :

1. vérifie le nom de l'unité ;
2. consulte son statut ;
3. examine les dépendances ;
4. relève les journaux nécessaires ;
5. confirme la fenêtre d'intervention si le système est en production ;
6. vérifie le résultat après l'opération.

## 19.5. Recharger la configuration

Certains services prennent en charge :

```bash
systemctl reload nom.service
```

Cette commande demande un rechargement lorsque l'unité et l'application permettent cette opération.

D'autres services ne prennent en charge que le redémarrage.

Il faut consulter la documentation de l'application et la configuration de l'unité avant de choisir l'opération.

## 19.6. Consulter les journaux

```bash
journalctl -u nom.service -n 100 --no-pager
```

Cette commande affiche les dernières lignes disponibles pour l'unité.

Pour suivre les nouveaux messages en temps réel :

```bash
journalctl -u nom.service -f
```

Quitte le suivi avec `Ctrl+C`.

Les journaux doivent être associés à la chronologie de l'incident : comparer l'heure des erreurs avec celle des mesures et des changements de configuration permet de formuler de meilleures hypothèses.


# 20. Contrôler les ressources avec `systemd` et les cgroups

## 20.1. Pourquoi limiter un service ?

Un service mal configuré ou soumis à une charge exceptionnelle peut consommer une part excessive des ressources d'une machine.

Les limites de ressources peuvent aider à protéger le reste du système.

Elles ne remplacent pas la résolution de la cause applicative.

Les contrôles utiles peuvent inclure :

- une limite de CPU ;
- un niveau de pression mémoire à partir duquel le noyau récupère plus agressivement de la mémoire ;
- une limite mémoire absolue ;
- une limite sur le nombre de tâches.

## 20.2. Examiner la configuration actuelle

Avant de modifier des limites :

```bash
systemctl show nom.service -p CPUQuotaPerSecUSec -p MemoryHigh -p MemoryMax -p TasksMax
```

Les propriétés rapportées dépendent de la version de `systemd` et de la configuration disponible.

Tu peux également consulter le fichier d'unité et ses éventuels suppléments :

```bash
systemctl cat nom.service
```

Cette commande aide à examiner la configuration assemblée de l'unité, notamment les fichiers de surcharge.

## 20.3. Comprendre `CPUQuota=`

La propriété `CPUQuota=` configure une limite de temps CPU pour les processus de l'unité, dans les environnements qui prennent en charge cette fonctionnalité.

Exemple illustratif :

```ini
[Service]
CPUQuota=50%
```

Une valeur de `50%` correspond à la moitié de la capacité d'un processeur logique selon la convention de cette propriété, et non à la moitié de la capacité totale de tous les processeurs de la machine.

Une valeur supérieure à `100%` permet, dans les configurations compatibles, d'allouer une capacité équivalente à plusieurs processeurs.

Il ne faut pas choisir une limite sans connaître les besoins de l'application et les caractéristiques de la charge.

## 20.4. Comprendre `MemoryHigh=` et `MemoryMax=`

Exemple illustratif :

```ini
[Service]
MemoryHigh=700M
MemoryMax=900M
```

Ces propriétés ne remplissent pas la même fonction.

- `MemoryHigh=` constitue principalement un mécanisme de pression et de limitation progressive : le système peut ralentir fortement le service et récupérer de la mémoire lorsque le seuil est dépassé.
- `MemoryMax=` définit une limite dure pour la mémoire prise en compte par le groupe de contrôle ; si la consommation ne peut pas être contenue, un mécanisme d'épuisement de mémoire peut intervenir dans le périmètre concerné.

Les unités et la gestion exacte dépendent de la version et de l'environnement.

Une limite mémoire trop basse peut faire échouer une application ou provoquer des arrêts de processus liés à l'épuisement de mémoire.

Ne copie pas ces valeurs comme si elles étaient adaptées à tous les serveurs.

## 20.5. Comprendre `TasksMax=`

Exemple :

```ini
[Service]
TasksMax=256
```

Cette propriété limite le nombre de tâches gérées dans l'unité, selon la configuration de `systemd` et du noyau.

Les tâches comptabilisées peuvent inclure des processus et des threads.

Une limite trop basse peut empêcher l'application de créer de nouveaux travailleurs ou threads.

Une valeur appropriée doit être choisie en fonction de l'architecture de l'application et de sa charge attendue.

## 20.6. Exemple de surcharge contrôlée

**Cet exemple est un modèle de laboratoire, pas une configuration universelle de production.**

Supposons qu'une unité de test réelle existe sous le nom `application-test.service`.

Pour créer une surcharge :

```bash
sudo systemctl edit application-test.service
```

L'éditeur permet d'ajouter :

```ini
[Service]
CPUQuota=50%
MemoryHigh=700M
MemoryMax=900M
TasksMax=256
```

Ces valeurs sont des exemples fictifs et doivent être adaptées au laboratoire.

Après modification du fichier :

```bash
sudo systemctl daemon-reload
```

Le rechargement de la configuration du gestionnaire ne garantit pas à lui seul que toutes les nouvelles propriétés seront appliquées à un processus déjà actif. Selon la propriété modifiée et le type d'unité, une opération supplémentaire peut être nécessaire.

Avant de redémarrer un service :

```bash
systemctl status application-test.service
```

Si cela fait partie de l'expérience autorisée et que la conséquence est comprise, applique la procédure de prise en compte adaptée, généralement avec un redémarrage contrôlé :

```bash
sudo systemctl restart application-test.service
```

Puis vérifie :

```bash
systemctl status application-test.service
```

Et examine les propriétés déclarées :

```bash
systemctl show application-test.service -p CPUQuotaPerSecUSec -p MemoryHigh -p MemoryMax -p TasksMax
```

Les propriétés effectives peuvent aussi être contraintes par les unités parentes et l'environnement d'exécution.

## 20.7. Retirer la surcharge de laboratoire

Si tu as ajouté la surcharge uniquement pour un exercice, supprime le fichier de surcharge avec le mécanisme approprié de `systemctl edit`, ou modifie le fichier de manière contrôlée afin de retirer les propriétés ajoutées.

Puis :

```bash
sudo systemctl daemon-reload
```

Vérifie la configuration :

```bash
systemctl cat application-test.service
```

L'opération ne doit être réalisée que sur l'unité de laboratoire dont la configuration a été modifiée.


# 21. Journaux, traçabilité et diagnostic

## 21.1. Pourquoi les journaux sont-ils essentiels ?

Une mesure permet d'observer un état.

Un journal peut expliquer un événement.

Par exemple, une consommation CPU élevée peut coïncider avec un message signalant un nombre élevé de tentatives, une erreur de configuration ou un redémarrage.

La corrélation temporelle ne démontre pas toujours la causalité, mais elle permet de réduire les hypothèses à examiner.

## 21.2. Examiner les journaux d'un service

```bash
journalctl -u nom.service --since "30 minutes ago" --no-pager
```

Cette commande demande les messages de l'unité sur une période récente selon la compréhension temporelle de `journalctl`.

Pour rechercher les derniers messages du noyau :

```bash
journalctl -k -n 100 --no-pager
```

Selon les permissions et la configuration, l'accès aux journaux peut être limité.

## 21.3. Construire une chronologie

Un diagnostic utile relie les éléments suivants :

```text
08:00 — Première observation de la lenteur
08:02 — Hausse du CPU d'un processus
08:03 — Message d'erreur dans le journal
08:05 — Vérification du service
08:08 — Intervention contrôlée
08:10 — Nouvelle mesure
08:12 — État final et conclusion
```

Les heures sont fictives.

Cette chronologie aide à distinguer les symptômes initiaux, les événements associés, l'action réalisée et son résultat.

## 21.4. Corréler les mesures

Si un processus utilise beaucoup de CPU au moment d'une erreur, il faut se demander si l'activité est normale pour l'opération ou liée au problème.

Une corrélation ne suffit pas à démontrer une cause.

Il faut rechercher d'autres preuves, telles que les journaux, la configuration, la répétition de l'événement et les mesures sur des périodes différentes.

## 21.5. Tracer les interventions

Pour une intervention d'administration, note au minimum :

- la date et l'heure ;
- le nom de l'unité ou le PID ;
- le symptôme ;
- les commandes d'observation ;
- les informations importantes ;
- l'action effectuée ;
- le résultat après l'action ;
- les risques ou incertitudes restants.

La traçabilité facilite la maintenance, les audits et les diagnostics ultérieurs.


# 22. Problèmes courants et méthodes de résolution

## 22.1. Un processus utilise beaucoup de CPU

### Symptôme

L'utilisation CPU d'un processus reste élevée.

### Procédure

```bash
top
```

```bash
ps -p PID -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

```bash
pidstat -p PID 1 5
```

### Hypothèses à examiner

- calcul normalement intensif ;
- boucle active dans l'application ;
- traitement volumineux ;
- nombre de threads élevé ;
- redémarrages répétés ;
- contrainte de quota ou d'affinité ;
- erreur applicative.

### Décision

Ne pas arrêter automatiquement le processus. Vérifier d'abord sa fonction et la nécessité d'une intervention.

## 22.2. Une application semble manquer de mémoire

### Procédure

```bash
free -h
```

```bash
ps -eo pid,user,%mem,rss,etime,cmd --sort=-%mem | head -n 15
```

```bash
pidstat -r 1 5
```

### Hypothèses à examiner

- augmentation du nombre de requêtes ;
- croissance de la mémoire d'un processus ;
- cache ;
- limite de groupe de contrôle ;
- activité d'une application auxiliaire ;
- consommation partagée entre plusieurs processus.

### Décision

Confirmer une tendance avant de conclure à une fuite mémoire.

## 22.3. Un processus réapparaît après son arrêt

### Hypothèses

- unité `systemd` qui le redémarre ;
- superviseur d'application ;
- ordonnanceur ;
- script qui relance la commande ;
- processus parent qui crée de nouveaux enfants.

### Procédure

```bash
ps -ef --forest
```

Puis, si un service est identifié :

```bash
systemctl status nom.service
```

Consulte les journaux associés avant de décider comment intervenir.

## 22.4. Un processus reste en état `D`

### Procédure

```bash
ps -p PID -o pid,ppid,stat,wchan:32,etime,cmd
```

Puis :

```bash
journalctl -k -n 100 --no-pager
```

Ou, si l'accès est autorisé :

```bash
dmesg -T | tail -n 100
```

### Décision

Chercher la cause de l'attente. Ne pas répéter des `SIGKILL` sans diagnostic.

## 22.5. Beaucoup de processus zombies sont présents

### Procédure

Identifier les PID concernés et relever leurs PPID :

```bash
ps -eo pid,ppid,stat,user,cmd | awk '$3 ~ /^Z/'
```

Examiner ensuite les parents des zombies.

Cette commande utilise le format de `ps` demandé, avec l'état en troisième colonne. Pour une investigation plus précise, contrôle les lignes correspondantes sans te limiter au seul résultat du filtre.

### Décision

Chercher pourquoi le parent ne récupère pas les statuts de fin. Ne pas traiter les zombies comme des processus actifs ordinaires.

## 22.6. Un service actif ne répond pas

### Procédure

```bash
systemctl status nom.service
```

```bash
journalctl -u nom.service -n 100 --no-pager
```

Identifier le PID principal déclaré :

```bash
systemctl show nom.service -p MainPID
```

Examiner le processus si nécessaire.

### Décision

Déterminer si le problème concerne le démarrage, une dépendance, une erreur applicative ou la disponibilité fonctionnelle du service.

Un statut `active` ne prouve pas à lui seul que toutes les requêtes réussissent.

## 22.7. Un script de surveillance retourne un code inattendu

### Procédure

- afficher la commande exacte ;
- vérifier la syntaxe ;
- examiner les arguments ;
- relever immédiatement le code de retour ;
- vérifier si l'absence de correspondance est un résultat prévu ;
- contrôler les permissions ;
- distinguer l'état du processus de l'état du service.

Un code non nul ne doit pas être assimilé automatiquement à une panne applicative.


# 23. Sécuriser les opérations d'administration

## 23.1. Identifier la bonne cible

Avant d'envoyer un signal, relève :

```bash
ps -p PID -o pid,ppid,user,stat,lstart,etime,cmd
```

Vérifie notamment l'utilisateur, la commande et le temps de lancement.

Si le processus appartient à un service, identifie aussi son unité.

## 23.2. Minimiser la portée de l'action

Privilégie l'action la plus ciblée qui convient à la situation.

Exemples :

- examiner un processus avec `ps` avant d'envoyer un signal ;
- viser un PID connu plutôt qu'un motif trop large ;
- utiliser le gestionnaire de services pour un service administré ;
- éviter de signaler un groupe entier si un processus unique suffit ;
- collecter les journaux avant un redémarrage lorsqu'ils sont nécessaires au diagnostic.

## 23.3. Privilèges administratifs

L'utilisation de `sudo` permet d'agir sur davantage de processus et de services.

Avant d'utiliser des privilèges administratifs, assure-toi que :

- la cible est confirmée ;
- l'action est nécessaire ;
- la commande a été relue ;
- ses effets sont compris ;
- la procédure de retour à l'état antérieur est disponible si nécessaire.

## 23.4. Ne pas exposer des informations sensibles

Les arguments de commande, variables d'environnement, fichiers ouverts et journaux peuvent révéler des informations sensibles.

Les scripts de supervision ne doivent pas publier inutilement des données privées ou des secrets.

Les résultats de commandes comme `ps`, `/proc` et `lsof` doivent être traités en fonction du contexte de sécurité du système.

## 23.5. Vérifier le résultat après l'action

Un signal envoyé ne signifie pas qu'un problème est résolu.

Un redémarrage de service ne garantit pas qu'il fonctionne correctement après son retour.

Après l'intervention, vérifie :

```bash
systemctl status nom.service
```

Ou, pour un processus :

```bash
ps -p PID -o pid,ppid,user,stat,etime,cmd
```

Puis, selon le problème, contrôle de nouveau les ressources, les journaux ou la fonction applicative.


# 24. Travaux pratiques guidés

Les travaux pratiques doivent être effectués dans un environnement de laboratoire, particulièrement lorsqu'ils portent sur des groupes de processus, des services ou des limites de ressources.

## TP 1 — Observer PID, PPID, PGID et SID

### Objectif

Comprendre les identifiants d'un processus et la façon dont le shell organise les tâches.

### Étape 1 : lancer une tâche

```bash
sleep 300 &
PID=$!

printf 'PID de test : %s\n' "$PID"
```

### Étape 2 : examiner le processus

```bash
ps -o pid,ppid,pgid,sid,tpgid,tty,stat,cmd -p "$PID"
```

### Étape 3 : examiner les membres du groupe

Relever le PGID retourné, puis utiliser :

```bash
ps -eo pid,ppid,pgid,stat,cmd
```

Compare les processus dont le PGID correspond à celui du test.

### Étape 4 : terminer la tâche

```bash
kill -TERM "$PID"
```

### Étape 5 : vérifier

```bash
ps -p "$PID" -o pid,ppid,stat,cmd
```

### Résultat attendu

Tu dois savoir différencier un PID, un PPID, un PGID et un SID, et expliquer pourquoi ils ne décrivent pas la même relation.


## TP 2 — Identifier le thread le plus actif

### Objectif

Observer les threads d'une application.

### Étape 1 : créer un processus de test

```bash
sleep 300 &
PID=$!
```

### Étape 2 : afficher les threads

```bash
ps -L -p "$PID" -o pid,lwp,psr,stat,pcpu,comm
```

### Étape 3 : observer dans `top`

```bash
top -H -p "$PID"
```

### Étape 4 : interpréter

Le programme `sleep` est un exemple simple. Il n'est pas conçu pour générer une charge CPU importante.

Le but du TP est de comprendre les colonnes et la relation entre le PID du processus et les identifiants de threads.

### Étape 5 : arrêter le test

```bash
kill -TERM "$PID"
```

### Résultat attendu

Tu dois pouvoir expliquer pourquoi une application multithread nécessite parfois une observation au niveau des threads plutôt qu'au seul niveau du processus.


## TP 3 — Suivre les mesures dans le temps

### Objectif

Comparer les mesures instantanées et les mesures répétées.

### Étape 1 : afficher un instantané

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15
```

### Étape 2 : observer plusieurs relevés

```bash
vmstat 1 5
```

### Étape 3 : utiliser `pidstat` si disponible

```bash
pidstat 1 5
```

### Étape 4 : comparer les résultats

Distingue :

- le CPU observé sur un processus ;
- les statistiques générales de la machine ;
- les intervalles de mesure ;
- le relevé initial de `vmstat` et ses relevés suivants.

### Résultat attendu

Tu dois pouvoir expliquer pourquoi plusieurs relevés dans le temps donnent un diagnostic plus utile qu'une seule mesure isolée.


## TP 4 — Examiner les descripteurs d'un processus

### Objectif

Comprendre comment un processus peut conserver des fichiers et d'autres ressources ouverts.

### Étape 1 : lancer un processus de test

```bash
sleep 300 &
PID=$!
```

### Étape 2 : examiner les descripteurs

```bash
ls -l "/proc/$PID/fd"
```

### Étape 3 : utiliser `lsof`, si disponible

```bash
lsof -p "$PID"
```

### Étape 4 : terminer le processus

```bash
kill -TERM "$PID"
```

### Résultat attendu

Tu dois comprendre la relation entre un processus et les descripteurs de fichiers ouverts qui lui sont associés.


## TP 5 — Écrire un vérificateur de PID

### Objectif

Créer un script qui contrôle un PID fourni en argument.

### Étape 1 : créer le fichier

```bash
nano verifier-processus.sh
```

Utilise le script présenté à la section 15.

### Étape 2 : rendre le fichier exécutable

```bash
chmod +x verifier-processus.sh
```

### Étape 3 : lancer un test

Dans le terminal :

```bash
sleep 300 &
PID=$!
```

Puis :

```bash
./verifier-processus.sh "$PID"
```

### Étape 4 : terminer la tâche de test

```bash
kill -TERM "$PID"
```

### Étape 5 : refaire la vérification

```bash
./verifier-processus.sh "$PID"
```

### Résultat attendu

Le script doit présenter les informations du processus lorsqu'il est visible, puis signaler l'absence de correspondance si le PID ne désigne plus un processus visible.


## TP 6 — Limiter la durée d'un programme

### Objectif

Comprendre l'utilisation de `timeout`.

### Étape 1

```bash
timeout 3s sleep 30
```

La commande doit normalement interrompre le test après la limite.

### Étape 2 : récupérer le statut immédiatement

```bash
printf 'Code : %s\n' "$?"
```

Dans le comportement courant de GNU `timeout`, une commande terminée parce que la limite a été atteinte retourne généralement `124`, sauf option modifiant le comportement du statut.

### Étape 3 : expliquer la séquence

Décris :

- le lancement ;
- la durée maximale ;
- le signal initial ;
- la possibilité d'un délai de grâce ;
- le code de retour.

### Résultat attendu

Tu dois savoir quand une limite de durée est utile et pourquoi elle doit être testée sur des commandes contrôlées avant son utilisation dans un script de production.


# 25. Exercices d'application

Réponds aux questions avant de consulter la correction.

## Exercice 1 — Identifiants

Explique la différence entre `PID`, `PPID`, `PGID` et `SID`.

## Exercice 2 — Groupe de processus

Pourquoi `Ctrl+C` peut-il arrêter plusieurs commandes d'une pipeline ?

## Exercice 3 — Réutilisation des PID

Un script conserve le PID d'une application pendant plusieurs heures.

Quel problème peut survenir si le processus initial se termine entre-temps ?

Propose une méthode pour rendre la vérification plus fiable.

## Exercice 4 — État `D`

Un processus reste en état `D`.

Pourquoi `SIGKILL` ne constitue-t-il pas forcément une solution immédiate ?

Cite deux moyens de collecter des indices.

## Exercice 5 — Zombie et orphelin

Explique la différence entre un processus zombie et un processus orphelin.

## Exercice 6 — Threads

Une application possède un seul PID visible dans `ps`, mais consomme beaucoup de CPU.

Comment examiner son activité au niveau des threads ?

## Exercice 7 — Mesures de performance

Quelle est la différence générale entre `ps`, `top`, `pidstat` et `iostat` ?

## Exercice 8 — Entrées-sorties

Une application est lente et utilise peu de CPU.

Pourquoi faut-il examiner les entrées-sorties et les attentes possibles avant de conclure que le programme est en panne ?

## Exercice 9 — `wait`

À quoi sert la commande `wait` dans un script Bash qui lance un processus avec `&` ?

## Exercice 10 — `nohup`

Pourquoi `nohup commande &` n'est-il pas équivalent à une unité de service `systemd` ?

## Exercice 11 — Codes de retour

Une commande de recherche de processus retourne un code non nul.

Cela signifie-t-il obligatoirement que le système est en panne ? Explique.

## Exercice 12 — Cgroups

Un service atteint une limite CPU alors que la machine dispose encore de ressources CPU libres.

Comment cela est-il possible ?

## Exercice 13 — Limites mémoire

Quelle est la différence générale entre `MemoryHigh=` et `MemoryMax=` dans `systemd` ?

## Exercice 14 — Diagnostic CPU

Un processus consomme beaucoup de CPU.

Propose une séquence de cinq vérifications avant de décider d'une intervention.

## Exercice 15 — Service

Pourquoi faut-il souvent utiliser `systemctl` plutôt que tuer directement le PID principal d'un service administré par `systemd` ?


# 26. Corrections des exercices

## Correction 1 — Identifiants

- `PID` identifie un processus.
- `PPID` identifie son parent.
- `PGID` identifie son groupe de processus.
- `SID` identifie sa session de processus.

Ils répondent à des questions différentes : identité individuelle, relation parent-enfant, organisation en groupe et organisation en session.

## Correction 2 — Groupe de processus

Dans un terminal interactif, `Ctrl+C` provoque généralement l'envoi de `SIGINT` au groupe de processus au premier plan.

Une pipeline peut contenir plusieurs processus associés à cette tâche. Plusieurs processus peuvent donc recevoir le signal.

## Correction 3 — Réutilisation des PID

Après la disparition d'un processus, son PID peut être réutilisé.

Un script qui ne vérifie que le PID risque alors de viser une autre instance.

Pour limiter ce risque, il doit contrôler plusieurs informations : l'utilisateur, la commande, le PPID et les caractéristiques temporelles. Les applications et superviseurs peuvent aussi fournir des identifiants plus adaptés à leur gestion.

## Correction 4 — État `D`

Un processus en état `D` attend généralement une opération noyau non interruptible immédiatement.

Le signal `SIGKILL` ne garantit donc pas sa disparition instantanée.

Les indices peuvent être collectés avec :

```bash
ps -p PID -o pid,ppid,stat,wchan:32,etime,cmd
```

et :

```bash
journalctl -k -n 100 --no-pager
```

Selon les permissions, `dmesg` peut également être utile.

## Correction 5 — Zombie et orphelin

Un zombie a terminé son exécution, mais son parent n'a pas encore récupéré son statut de fin.

Un processus orphelin continue à s'exécuter après la terminaison de son parent et peut être adopté par un autre processus approprié du système.

Un zombie est terminé ; un orphelin peut toujours être actif.

## Correction 6 — Threads

Utiliser :

```bash
top -H -p PID
```

ou :

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

Ces commandes permettent d'examiner la répartition de l'activité au niveau des threads.

## Correction 7 — Mesures de performance

- `ps` présente un instantané des processus.
- `top` permet une observation interactive actualisée périodiquement.
- `pidstat` produit des statistiques répétées sur les tâches.
- `iostat` présente des informations sur l'activité du CPU et des périphériques de stockage.

Ils se complètent et ne doivent pas être considérés comme des substituts parfaits.

## Correction 8 — Entrées-sorties

Un processus peut attendre un disque, un système de fichiers réseau ou une autre ressource.

Dans ce cas, il peut utiliser peu de CPU tout en ralentissant une application.

Il est utile d'examiner l'état du processus, les statistiques d'entrée-sortie et les journaux avant de conclure à une panne.

## Correction 9 — `wait`

`wait` permet au shell d'attendre la fin d'un processus enfant connu ou d'une tâche qu'il gère, puis de récupérer son statut de retour.

Il permet au script de synchroniser les étapes et de contrôler le résultat des tâches lancées en arrière-plan.

## Correction 10 — `nohup`

`nohup` modifie le traitement de `SIGHUP` et peut aider une commande à continuer après certaines déconnexions de terminal.

Il n'apporte pas, à lui seul, une gestion complète des dépendances, une politique de redémarrage, une supervision ou une gestion de ressources équivalente à celle d'un service correctement configuré.

## Correction 11 — Codes de retour

Non.

Une recherche valide peut retourner un statut non nul simplement parce qu'aucune correspondance n'a été trouvée. Il faut interpréter le code selon la documentation de la commande et le contexte.

## Correction 12 — Cgroups

Un service peut être soumis à un quota ou à une autre contrainte CPU qui limite son utilisation indépendamment des ressources encore disponibles sur la machine entière.

Le diagnostic doit donc examiner les limites du service et de ses unités parentes, en plus des statistiques globales.

## Correction 13 — Limites mémoire

`MemoryHigh=` constitue principalement un mécanisme de pression mémoire et de limitation progressive.

`MemoryMax=` impose une limite absolue de mémoire prise en compte dans le groupe de contrôle. Si la consommation ne peut pas être contenue, un mécanisme d'épuisement mémoire peut intervenir.

Ces paramètres doivent être dimensionnés et testés avec soin.

## Correction 14 — Diagnostic CPU

Une séquence correcte peut être :

1. observer `top` ;
2. identifier le PID et sa commande ;
3. examiner l'utilisateur, le PPID et l'état avec `ps` ;
4. suivre les mesures répétées avec `pidstat` ;
5. consulter les journaux et comprendre la fonction de l'application.

Une fois la cause mieux établie, l'administrateur peut choisir une intervention adaptée.

## Correction 15 — Service

`systemd` peut gérer le démarrage, l'arrêt, le redémarrage, les dépendances et les limites de ressources du service.

Tuer directement le processus principal peut perturber la gestion du service ou déclencher un redémarrage automatique.

Il est généralement préférable d'utiliser le gestionnaire pour les opérations sur le cycle de vie, puis les outils de processus pour examiner les détails.


# 27. Défi final : diagnostic et supervision d'un service

## 27.1. Contexte

Tu administres un serveur Linux de laboratoire qui héberge une application gérée par `systemd`.

Les symptômes observés sont les suivants :

```text
SYMPTÔME 1
L'application semble parfois lente.

SYMPTÔME 2
Un processus utilise beaucoup de CPU dans top.

SYMPTÔME 3
Plusieurs processus semblent appartenir à la même application.

SYMPTÔME 4
Le statut du service indique que l'unité est active,
mais l'application paraît encore indisponible.

SYMPTÔME 5
L'équipe souhaite mettre en place une vérification
régulière sans arrêter automatiquement le processus.
```

Les informations fournies ne contiennent pas encore les PID réels, les journaux, la configuration du service ou les caractéristiques de la charge.

Tu dois donc construire une procédure de collecte et éviter de conclure avant d'avoir des éléments vérifiables.

## 27.2. Mission

Réalise un diagnostic qui répond aux points suivants :

1. Identifier les processus les plus actifs.
2. Examiner leur identité et leurs relations parent-enfant.
3. Déterminer les groupes de processus et les threads, lorsque cela est utile.
4. Suivre les statistiques CPU de façon répétée.
5. Examiner la mémoire et les entrées-sorties.
6. Vérifier l'état du service, son PID principal et son groupe de contrôle.
7. Comparer le statut avec les journaux.
8. Concevoir un script de vérification qui n'effectue aucune action destructive.
9. Définir une méthode de vérification après intervention.
10. Présenter les hypothèses retenues et les preuves disponibles.

## 27.3. Contraintes

- Ne suppose pas que le nom du service est connu.
- N'arrête pas un processus uniquement parce qu'il consomme beaucoup de CPU.
- Ne confonds pas le PID principal du service avec tous ses processus.
- Ne conclus pas à une panne sur un seul relevé de ressources.
- Ne suppose pas qu'un état `active` garantit le bon fonctionnement applicatif.
- Ne modifie pas les limites de ressources avant d'avoir évalué les besoins du service.
- Le script de supervision doit collecter des informations et signaler le problème, sans envoyer automatiquement de signal aux processus.


# 28. Correction détaillée du défi final

## 28.1. Étape 1 — Repérer les processus les plus actifs

Lance :

```bash
top
```

Relève le PID, la commande, l'utilisateur et les mesures pertinentes.

Complète avec :

```bash
ps -eo pid,ppid,user,pgid,sid,stat,ni,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 20
```

L'objectif est d'obtenir une vue détaillée des processus les plus consommateurs de CPU selon l'indication de `ps`.

Cette sortie doit être considérée comme un relevé à un instant donné.

## 28.2. Étape 2 — Examines les identifiants

Pour un PID observé :

```bash
ps -p PID -o pid,ppid,pgid,sid,tpgid,tty,user,stat,etime,cmd
```

Remplace `PID` par la valeur réelle.

Si plusieurs processus semblent liés à l'application, examine leur arbre :

```bash
ps -ef --forest
```

Cette étape aide à déterminer si plusieurs processus enfants dépendent d'une même application ou si certains résultats correspondent à des programmes indépendants.

## 28.3. Étape 3 — Examiner les threads si nécessaire

Si le processus est multithread et que le CPU semble concentré sur certains threads :

```bash
top -H -p PID
```

Ou :

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

Ces commandes permettent de voir si l'activité se concentre sur un thread ou se répartit entre plusieurs.

La consommation CPU doit être interprétée dans le contexte du travail effectué.

## 28.4. Étape 4 — Suivre les mesures

Si `sysstat` est disponible :

```bash
pidstat -p PID 1 5
```

Pour compléter les statistiques mémoire :

```bash
pidstat -r -p PID 1 5
```

Si l'activité d'entrée-sortie paraît pertinente :

```bash
pidstat -d -p PID 1 5
```

Comparer les observations au fil du temps.

Si les outils nécessaires ne sont pas installés, tu peux utiliser les outils disponibles et documenter cette limitation. Ne considère pas l'absence d'un outil comme une preuve de dysfonctionnement.

## 28.5. Étape 5 — Examiner la mémoire globale

```bash
free -h
```

Puis :

```bash
ps -eo pid,ppid,user,%mem,rss,etime,cmd --sort=-%mem | head -n 15
```

Comparer la mémoire globale avec les principaux consommateurs.

Il faut tenir compte de la mémoire disponible, des caches, des pages partagées et des limites de l'environnement, plutôt que de sommer sans précaution les valeurs RSS de tous les processus.

## 28.6. Étape 6 — Examiner les entrées-sorties

Si nécessaire :

```bash
vmstat 1 5
```

Puis, si disponible :

```bash
iostat -xz 1 5
```

Le but est d'évaluer si la lenteur peut être associée à une attente ou à une activité de stockage.

Les métriques doivent être interprétées selon le type de périphérique et la charge observée.

## 28.7. Étape 7 — Vérifier le service

Une fois le nom de l'unité identifié :

```bash
systemctl status nom.service
```

Identifier le PID principal et le groupe de contrôle :

```bash
systemctl show nom.service -p MainPID -p ControlGroup
```

Ces informations permettent de relier la supervision du service aux processus visibles dans `ps`.

## 28.8. Étape 8 — Examiner les journaux

```bash
journalctl -u nom.service --since "30 minutes ago" --no-pager
```

Recherche les messages liés à la période de lenteur.

Selon le résultat, les hypothèses peuvent inclure :

- une erreur d'application ;
- un problème de configuration ;
- un manque de ressource ;
- une dépendance indisponible ;
- un redémarrage répété ;
- une opération attendue qui prend plus de temps que d'habitude.

Il faut retenir uniquement les hypothèses soutenues par des observations suffisantes.

## 28.9. Étape 9 — Construire un script de supervision non destructif

Le script suivant effectue des vérifications et affiche des informations. Il n'envoie aucun signal aux processus et ne redémarre pas le service.

Créer :

```bash
nano diagnostic-service.sh
```

Contenu :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s nom.service\n' "$0" >&2
    exit 2
fi

SERVICE=$1

if ! command -v systemctl >/dev/null 2>&1; then
    printf 'Erreur : systemctl est indisponible.\n' >&2
    exit 2
fi

if ! systemctl cat "$SERVICE" >/dev/null 2>&1; then
    printf 'Erreur : unité non trouvée ou inaccessible : %s\n' "$SERVICE" >&2
    exit 2
fi

printf '\n%s\n' "=== Date ==="
date '+%F %T'

printf '\n%s\n' "=== État du service ==="
systemctl status "$SERVICE" --no-pager

printf '\n%s\n' "=== PID principal et groupe de contrôle ==="
systemctl show "$SERVICE" -p MainPID -p ControlGroup

printf '\n%s\n' "=== Principaux processus selon le CPU ==="
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15

printf '\n%s\n' "=== Mémoire générale ==="
free -h

printf '\n%s\n' "=== Charge système ==="
uptime

printf '\n%s\n' "=== Derniers journaux du service ==="
journalctl -u "$SERVICE" -n 30 --no-pager
```

Rendre le script exécutable :

```bash
chmod +x diagnostic-service.sh
```

Lancer le script avec le véritable nom de service :

```bash
./diagnostic-service.sh nom.service
```

### Ce que fait le script

1. vérifie qu'un argument a été fourni ;
2. vérifie la présence de `systemctl` ;
3. vérifie que l'unité est accessible ;
4. affiche son statut ;
5. affiche le PID principal déclaré et le groupe de contrôle ;
6. relève les processus les plus consommateurs de CPU selon `ps` ;
7. affiche la mémoire et la charge générale ;
8. affiche les derniers journaux du service.

### Limites

Ce script ne prouve pas que l'application répond correctement à ses utilisateurs.

Il effectue une collecte de base. Selon l'application, il peut être nécessaire d'ajouter un test fonctionnel, par exemple une vérification HTTP ou une requête applicative adaptée.

Le script affiche aussi des informations sur d'autres processus visibles, pas uniquement ceux du service. Il convient de limiter l'accès aux relevés et leur conservation lorsqu'ils contiennent des données sensibles.

## 28.10. Étape 10 — Présenter les conclusions

Un rapport intermédiaire de qualité doit distinguer trois éléments :

### Faits observés

Exemples :

- le PID identifié présente une utilisation CPU élevée sur plusieurs mesures ;
- un processus enfant est associé au parent étudié ;
- le statut du service est `active` ;
- un message d'erreur apparaît dans les journaux au moment de l'incident.

### Hypothèses

Exemples :

- la charge CPU contribue à la lenteur ;
- le problème est lié à une dépendance ;
- une contrainte de ressources s'applique au service.

Ces formulations restent des hypothèses jusqu'à ce qu'elles soient appuyées par des preuves suffisantes.

### Actions proposées

Une action doit être reliée au diagnostic.

Exemple :

- si le service signale une erreur de configuration, corriger et valider cette configuration ;
- si une limite CPU est trop restrictive par rapport aux besoins confirmés, planifier son ajustement ;
- si le processus est bloqué sur une ressource d'entrée-sortie, poursuivre l'investigation sur cette ressource ;
- si aucun élément ne confirme la cause, collecter davantage de mesures plutôt que d'appliquer une modification au hasard.

## 28.11. Étape 11 — Vérifier après l'action

Après une intervention autorisée et documentée, refaire les mesures utiles :

```bash
systemctl status nom.service
```

```bash
journalctl -u nom.service -n 50 --no-pager
```

```bash
uptime
```

```bash
free -h
```

Puis répéter les mesures ciblées du processus.

Vérifier également le fonctionnement réel de l'application lorsque c'est possible.

L'objectif final n'est pas seulement d'avoir exécuté une commande avec succès, mais de démontrer que le symptôme a été résolu ou de préciser ce qui reste à investiguer.


# 29. Checklist de compétences

Avant de passer au niveau expert, vérifie que tu sais réaliser les opérations suivantes.

## Compréhension avancée

- [ ] Je distingue PID, PPID, PGID, SID et TPGID.
- [ ] Je comprends les groupes de processus et les sessions de terminal.
- [ ] Je peux expliquer pourquoi un signal peut affecter plusieurs processus.
- [ ] Je comprends la différence entre processus parent, enfant, zombie et orphelin.
- [ ] Je comprends le rôle des threads.

## Diagnostic

- [ ] Je sais construire une sortie `ps` adaptée au problème étudié.
- [ ] Je sais examiner les processus d'une application sous forme arborescente.
- [ ] Je sais observer les threads d'un PID.
- [ ] Je peux utiliser `pidstat` pour comparer plusieurs relevés.
- [ ] Je peux interpréter les grandes lignes de `vmstat`.
- [ ] Je sais quand utiliser `iostat`.
- [ ] Je comprends pourquoi un processus en état `D` peut ne pas disparaître immédiatement.
- [ ] Je sais distinguer une hypothèse et un fait observé.

## Automatisation

- [ ] Je sais récupérer un PID avec `$!`.
- [ ] Je sais attendre un enfant avec `wait`.
- [ ] Je comprends les limites de `nohup` et `disown`.
- [ ] Je sais utiliser `timeout` pour limiter la durée d'une commande.
- [ ] Je peux écrire un script qui valide ses arguments.
- [ ] Je vérifie les codes de retour de manière explicite.
- [ ] Je sais pourquoi un script ne doit pas arrêter automatiquement un processus sur la seule base d'une métrique.

## Services et ressources

- [ ] Je sais identifier le PID principal d'un service.
- [ ] Je sais consulter le groupe de contrôle d'une unité.
- [ ] Je sais examiner les journaux d'un service avec `journalctl`.
- [ ] Je comprends le rôle des cgroups.
- [ ] Je peux expliquer les différences générales entre `CPUQuota=`, `MemoryHigh=`, `MemoryMax=` et `TasksMax=`.
- [ ] Je sais qu'une limite doit être adaptée et testée avant son application en production.

## Sécurité et traçabilité

- [ ] Je vérifie plusieurs propriétés avant une intervention sur un PID.
- [ ] Je ne traite pas la réussite de `kill` comme une preuve de terminaison.
- [ ] Je documente le symptôme et le résultat de l'intervention.
- [ ] Je sais limiter l'accès aux résultats de diagnostic.
- [ ] Je privilégie une intervention ciblée et réversible quand elle est adaptée.


# 30. Fiche de révision et commandes essentielles

## 30.1. Identifiants et état

```bash
ps -o pid,ppid,pgid,sid,tpgid,tty,stat,cmd -p PID
```

Arbre des processus :

```bash
ps -ef --forest
```

Threads d'un processus :

```bash
ps -L -p PID -o pid,lwp,psr,stat,pcpu,comm
```

## 30.2. Surveillance des ressources

Surveillance interactive :

```bash
top
```

Threads dans `top` :

```bash
top -H -p PID
```

Processus classés par CPU :

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15
```

Mémoire :

```bash
free -h
```

Charge :

```bash
uptime
```

Mesures CPU par tâche :

```bash
pidstat 1 5
```

Mesures système :

```bash
vmstat 1 5
```

Stockage :

```bash
iostat -xz 1 5
```

## 30.3. Recherche et identification

Rechercher par nom :

```bash
pgrep -a nom
```

Rechercher une commande complète :

```bash
pgrep -a -f 'motif précis'
```

Examiner un PID :

```bash
ps -p PID -o pid,ppid,user,stat,lstart,etime,cmd
```

Examiner les descripteurs :

```bash
ls -l /proc/PID/fd
```

Examiner les fichiers ouverts avec `lsof` :

```bash
lsof -p PID
```

## 30.4. Signaux

Demande de terminaison :

```bash
kill -TERM PID
```

Terminaison forcée, uniquement si justifiée :

```bash
kill -KILL PID
```

Vérifier l'existence ou les permissions :

```bash
kill -0 PID
```

Afficher la liste des signaux :

```bash
kill -l
```

## 30.5. Bash

Lancer une tâche :

```bash
commande &
```

Récupérer son PID :

```bash
PID=$!
```

Attendre la fin :

```bash
wait "$PID"
STATUS=$?
```

Afficher les tâches du shell :

```bash
jobs -l
```

Reprendre une tâche en arrière-plan :

```bash
bg %1
```

Ramener une tâche au premier plan :

```bash
fg %1
```

Lancer un test avec une limite de temps :

```bash
timeout 10s commande
```

## 30.6. Services

Afficher le statut :

```bash
systemctl status nom.service
```

Afficher le PID principal et le groupe de contrôle :

```bash
systemctl show nom.service -p MainPID -p ControlGroup
```

Afficher les propriétés de ressources :

```bash
systemctl show nom.service -p CPUQuotaPerSecUSec -p MemoryHigh -p MemoryMax -p TasksMax
```

Afficher la configuration assemblée :

```bash
systemctl cat nom.service
```

Consulter les journaux :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Suivre les journaux :

```bash
journalctl -u nom.service -f
```


# 31. Glossaire

**Affinité CPU :** ensemble des processeurs logiques sur lesquels une tâche est autorisée à s'exécuter.

**Appel système :** mécanisme qui permet à un programme de demander un service au noyau.

**Cgroup :** groupe de contrôle permettant d'organiser et de gérer des ressources pour un ensemble de processus.

**Code de retour :** valeur qui indique le résultat d'une commande ou d'un processus.

**Descripteur de fichier :** identifiant utilisé par un processus pour accéder à un fichier, une socket, un tube ou une autre ressource de type fichier.

**Daemon :** processus de service qui fonctionne généralement sans interaction directe avec un terminal utilisateur.

**`disown` :** commande interne de Bash permettant de modifier la gestion d'une tâche dans la table des tâches du shell.

**Entrée-sortie :** opération d'échange de données avec une ressource, par exemple un fichier, un disque ou un périphérique.

**Groupe de processus :** ensemble de processus partageant un PGID.

**Groupe de contrôle :** mécanisme noyau qui permet de regrouper des tâches pour comptabiliser ou limiter certaines ressources.

**`iostat` :** outil qui présente des statistiques sur l'activité CPU et les entrées-sorties.

**`nice` :** valeur qui influence la priorité relative de l'ordonnancement des processus ordinaires.

**`nohup` :** utilitaire qui permet d'exécuter une commande en ignorant `SIGHUP`, selon le fonctionnement décrit dans sa documentation.

**Ordonnanceur :** composant du noyau qui décide quelles tâches exécuter sur les processeurs logiques.

**PID :** identifiant d'un processus.

**PGID :** identifiant d'un groupe de processus.

**PPID :** identifiant du parent d'un processus.

**Processus orphelin :** processus dont le parent s'est terminé alors que lui-même continue à exister.

**Processus zombie :** processus terminé dont le statut de fin n'a pas encore été récupéré par son parent.

**`pidstat` :** outil qui produit des statistiques sur les tâches Linux, souvent à intervalles successifs.

**`ps` :** outil qui présente un instantané des processus sélectionnés.

**`SIGCHLD` :** signal lié aux changements d'état des processus enfants.

**`SIGKILL` :** signal de terminaison forcée qui ne peut pas être intercepté ou ignoré par le programme.

**`SIGTERM` :** signal de demande de terminaison.

**`SID` :** identifiant d'une session de processus.

**`systemd` :** gestionnaire de services largement utilisé dans les distributions Linux modernes.

**`timeout` :** utilitaire permettant de limiter la durée d'exécution d'une commande.

**Thread :** fil d'exécution au sein d'un processus.

**`top` :** outil interactif de surveillance des processus et des ressources du système.

**`vmstat` :** outil qui présente des statistiques relatives à la mémoire virtuelle, aux processus, au CPU et aux entrées-sorties.

**`WCHAN` :** indication du point d'attente noyau d'un processus lorsqu'elle est disponible dans l'outil.


# 32. Documentation de référence

Les références suivantes permettent d'approfondir les sujets étudiés. Les commandes disponibles et certaines options peuvent différer selon la distribution et la version installée.

## Processus et états

1. Manuel Linux `ps`  
   https://man7.org/linux/man-pages/man1/ps.1.html

2. Documentation du noyau Linux sur `/proc`  
   https://docs.kernel.org/filesystems/proc.html

3. Manuel Linux sur les signaux  
   https://man7.org/linux/man-pages/man7/signal.7.html

## Bash et contrôle des tâches

4. Manuel officiel GNU Bash — contrôle des tâches  
   https://www.gnu.org/software/bash/manual/html_node/Job-Control.html

5. Manuel officiel GNU Bash — commandes de contrôle des tâches  
   https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html

## Performance et diagnostic

6. Manuel Linux `pidstat`  
   https://man7.org/linux/man-pages/man1/pidstat.1.html

7. Documentation de référence `sysstat`  
   https://sysstat.github.io/

8. Manuel Linux `nice`  
   https://man7.org/linux/man-pages/man1/nice.1.html

9. Manuel Linux `timeout`  
   https://man7.org/linux/man-pages/man1/timeout.1.html

## Services et ressources

10. Documentation officielle de `systemctl`  
    https://www.freedesktop.org/software/systemd/man/latest/systemctl.html

11. Documentation officielle `systemd.resource-control`  
    https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html

Ces références précisent les options disponibles, les états, les limites de ressources et les comportements propres aux versions concernées.


# Conclusion

La gestion intermédiaire des processus consiste à dépasser l'observation d'un PID pour comprendre l'ensemble de son contexte d'exécution.

Tu as appris à différencier PID, PPID, PGID et SID, à examiner les threads, à interpréter les états et les signaux, à distinguer les mesures instantanées des observations répétées et à utiliser les journaux pour relier un symptôme à des événements.

Tu as également étudié la relation entre les processus et les services, les groupes de contrôle, les limites CPU et mémoire, ainsi que l'automatisation de contrôles non destructifs avec Bash.

La méthode à conserver est la suivante :

```text
OBSERVER
   |
   v
IDENTIFIER
   |
   v
MESURER DANS LE TEMPS
   |
   v
COMPRENDRE LES RELATIONS
   |
   v
FORMULER ET VÉRIFIER LES HYPOTHÈSES
   |
   v
CHOISIR UNE ACTION CIBLÉE
   |
   v
MESURER LE RÉSULTAT
   |
   v
DOCUMENTer L'INTERVENTION
```

Le point essentiel de ce niveau est de ne plus confondre un symptôme avec sa cause. Une consommation CPU élevée, un processus en attente, un service actif ou une mémoire utilisée ne suffisent pas, pris isolément, à démontrer une panne.

**L'objectif est de pouvoir expliquer ce que fait le système, pourquoi le symptôme apparaît et sur quelles preuves repose l'intervention.**

Le niveau expert pourra ensuite approfondir l'analyse des appels système, les mécanismes avancés d'ordonnancement, les traces noyau, les limites et pressions des cgroups, les diagnostics de contention et l'observabilité des applications en production.