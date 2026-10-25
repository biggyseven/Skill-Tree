# Git Avancé

## 1. Présentation du cours

Dans le cours débutant, vous avez appris à créer un dépôt Git, enregistrer des commits, utiliser des branches, effectuer des fusions et synchroniser un dépôt local avec un dépôt distant.

À mesure qu'un projet grandit, ces opérations deviennent plus complexes. Plusieurs développeurs peuvent travailler simultanément sur des fonctionnalités dépendantes. Une branche peut prendre du retard sur la branche principale. Une modification doit parfois être déplacée d'une branche vers une autre, plusieurs commits doivent être réorganisés ou une régression doit être localisée parmi des centaines de versions.

La maîtrise intermédiaire de Git consiste à savoir gérer ces situations sans perdre le travail réalisé et sans dégrader inutilement l'historique du projet.

Ce cours approfondit les mécanismes internes de Git et les outils nécessaires pour intervenir sur des dépôts utilisés dans un contexte professionnel, notamment en développement logiciel, en DevOps, en administration système et en automatisation des infrastructures.

L'accent est mis sur la compréhension des conséquences des commandes, la qualité de l'historique, la récupération après une erreur et les méthodes de collaboration.

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez être capable de :

- Comprendre les relations entre commits, branches, références et `HEAD`.
- Lire et interpréter un graphe d'historique Git.
- Comparer une fusion (`merge`) et un rebasage (`rebase`).
- Utiliser le rebasage interactif pour nettoyer un historique local.
- Regrouper, modifier et réorganiser des commits.
- Transférer un commit avec `git cherry-pick`.
- Utiliser `git stash` pour mettre temporairement son travail de côté.
- Diagnostiquer les conflits de fusion et de rebasage.
- Retrouver un commit après une manipulation incorrecte avec `git reflog`.
- Rechercher le commit à l'origine d'un défaut avec `git bisect`.
- Comprendre les références distantes et les branches de suivi.
- Utiliser les options de synchronisation de façon prudente.
- Manipuler les tags pour identifier les versions.
- Exploiter les worktrees pour travailler simultanément sur plusieurs branches.
- Appliquer les bonnes pratiques de sécurité, de collaboration et de maintenance d'un dépôt.

### 1.2. Prérequis

Il est recommandé de maîtriser les opérations suivantes :

```bash
git init
git status
git add
git commit
git log
git diff
git branch
git switch
git merge
git clone
git fetch
git pull
git push
```

Vous devez également connaître les concepts de branche, de commit, de dépôt local, de dépôt distant et de zone de préparation.

Les exemples supposent un terminal Linux, macOS, Git Bash ou PowerShell avec Git installé. Les principes restent applicables sur les principales plateformes utilisant Git.

### 1.3. Environnement recommandé

Pour les travaux pratiques, préparez :

- Git à jour.
- Un éditeur de texte.
- Un terminal.
- Un dépôt de laboratoire que vous pouvez modifier librement.
- Éventuellement un dépôt distant de test sur GitHub ou GitLab.

Ne réalisez pas les exercices destructifs sur un dépôt professionnel contenant des modifications importantes.

Les manipulations de l'historique seront expérimentées dans des dépôts de laboratoire spécialement créés à cet effet.

## 2. Le modèle interne de Git

Pour progresser au-delà des commandes élémentaires, il est nécessaire de comprendre ce que Git enregistre et comment il représente un projet.

### 2.1. Un commit représente un état du projet

Un commit contient principalement une référence à l'état des fichiers suivis du projet, des métadonnées et un ou plusieurs commits parents.

Les informations associées comprennent notamment :

- Un identifiant.
- L'auteur.
- La personne ayant créé le commit.
- Des dates.
- Un message.
- Le ou les commits parents.
- Une référence à l'arborescence représentant l'état enregistré.

L'auteur et le créateur du commit, appelés respectivement *author* et *committer*, ne sont pas nécessairement la même personne. Par exemple, une personne peut créer un commit à partir d'une modification initialement réalisée par un autre développeur.

Le commit n'est pas simplement une archive complète indépendante de chaque version précédente. Git stocke des objets reliés entre eux et peut réutiliser les données identiques entre plusieurs états.

### 2.2. Les objets fondamentaux de Git

Git utilise plusieurs types d'objets internes.

| Type d'objet | Rôle |
|---|---|
| Blob | Contenu d'un fichier. |
| Tree | Structure représentant des fichiers et des sous-répertoires. |
| Commit | Référence à un arbre, métadonnées et liens vers les commits parents. |
| Tag annoté | Objet permettant d'identifier un objet Git avec des métadonnées supplémentaires. |

Pour examiner le type d'un objet :

```bash
git cat-file -t HEAD
```

Dans un dépôt normal, cette commande indique généralement que `HEAD` désigne un objet de type `commit`.

Pour afficher son contenu :

```bash
git cat-file -p HEAD
```

Vous verrez notamment un identifiant d'arbre, les parents éventuels, l'auteur, le créateur du commit et le message.

Pour une utilisation courante, il n'est pas nécessaire de manipuler directement les objets. Cette compréhension aide cependant à interpréter l'historique et à comprendre les opérations de réécriture.

### 2.3. L'historique est un graphe orienté

Git n'impose pas un historique strictement linéaire. Un commit peut avoir un seul parent, plusieurs parents ou aucun parent s'il s'agit d'un commit racine.

Une branche représente généralement une référence vers un commit.

Considérons le graphe suivant :

```text
A---B---C-------------F     main
         \           /
          D---E-----/       feature
```

Les commits A, B et C sont communs aux deux chemins avant leur divergence.

Les commits D et E représentent le travail de la branche `feature`.

Le commit F représente une fusion dans cet exemple.

Une représentation simplifiée de la même situation peut être obtenue avec :

```bash
git log --graph --oneline --decorate --all
```

Cette commande est un outil fondamental pour comprendre les branches et les relations entre les commits.

### 2.4. Comprendre `HEAD`

`HEAD` représente généralement la référence du commit actuellement sélectionné par le dépôt de travail.

Lorsque vous vous trouvez sur la branche `main`, `HEAD` suit normalement cette branche.

Exemple :

```text
HEAD
 |
 v
main
 |
 v
Commit C
```

Lorsqu'un nouveau commit est créé sur cette branche, la référence `main` avance vers le nouveau commit. `HEAD` continue de désigner `main`.

Vous pouvez inspecter les références :

```bash
git symbolic-ref HEAD
```

Lorsque `HEAD` suit normalement une branche, la commande peut afficher quelque chose comme :

```text
refs/heads/main
```

Pour afficher l'identifiant du commit courant :

```bash
git rev-parse HEAD
```

Pour afficher la branche courante :

```bash
git branch --show-current
```

### 2.5. Le mode HEAD détaché

`HEAD` peut également désigner directement un commit sans suivre une branche.

Cette situation est appelée **detached HEAD**, ou HEAD détaché.

Par exemple :

```bash
git switch --detach IDENTIFIANT_DU_COMMIT
```

Le répertoire de travail correspond alors à ce commit, mais les nouveaux commits ne feront pas automatiquement avancer une branche existante.

Ce mode est utile pour :

- Examiner une ancienne version.
- Lancer des tests sur un commit précis.
- Comparer deux versions.
- Effectuer un diagnostic temporaire.

Le risque est de créer des commits qui ne sont référencés par aucune branche habituelle. Ils peuvent devenir difficiles à retrouver si aucune référence ne les conserve.

Si vous devez poursuivre un travail à partir de ce point, créez une branche :

```bash
git switch -c diagnostic-ancienne-version
```

Cette commande crée une branche au niveau du commit courant et vous permet de continuer à travailler sans perdre immédiatement la référence au nouvel historique.

## 3. Lire et comparer des historiques complexes

### 3.1. Le graphe complet

Pour examiner l'historique d'un dépôt :

```bash
git log --graph --oneline --decorate --all
```

Les options ont des rôles distincts :

- `--graph` représente graphiquement les relations entre commits.
- `--oneline` limite chaque entrée à une ligne compacte.
- `--decorate` affiche les références, comme les branches et les tags.
- `--all` inclut les références connues, plutôt que de limiter l'affichage au seul historique courant.

Cette commande est particulièrement utile après plusieurs fusions ou après un rebasage.

### 3.2. Identifier les commits d'une branche qui ne sont pas sur une autre

Pour afficher les commits présents sur `feature-api` mais pas sur `main` :

```bash
git log main..feature-api --oneline
```

Cette syntaxe signifie : afficher les commits accessibles depuis `feature-api` qui ne sont pas accessibles depuis `main`.

L'ordre des références est important.

```bash
git log feature-api..main --oneline
```

affiche, au contraire, les commits présents dans `main` mais absents de l'historique accessible depuis `feature-api`.

### 3.3. Comprendre `A..B` et `A...B`

La notation `A..B` est couramment utilisée pour sélectionner les commits accessibles depuis `B` qui ne sont pas accessibles depuis `A`.

Exemple :

```bash
git log main..feature-api
```

La notation `A...B` a un autre sens : elle identifie les commits appartenant à l'un ou l'autre côté mais pas aux deux, selon les règles de sélection des historiques de Git.

Pour visualiser les différences entre les modifications des branches :

```bash
git log --left-right --oneline main...feature-api
```

Les marqueurs affichés permettent de distinguer les commits propres à chaque côté.

Pour examiner directement les différences de fichiers entre deux références :

```bash
git diff main...feature-api
```

Dans cette forme de `git diff`, la comparaison est effectuée entre la base de fusion commune et la référence de droite, `feature-api`.

Cette différence de comportement entre les commandes utilisant `..` et `...` est importante : ne supposez pas que la notation `...` signifie exactement la même chose dans toutes les commandes Git.

### 3.4. Trouver la base de fusion commune

La base de fusion commune est le commit à partir duquel deux historiques ont divergé selon le calcul des ancêtres communs de Git.

Pour la consulter :

```bash
git merge-base main feature-api
```

Cette information est utile lorsque vous voulez comprendre quelles modifications appartiennent réellement à une branche de fonctionnalité.

Elle intervient notamment dans les opérations de rebasage, les comparaisons de branches et les revues de code.

### 3.5. Compter les commits en avance et en retard

```bash
git rev-list --left-right --count main...origin/main
```

Cette commande compare les commits propres aux deux côtés du graphe.

La sortie contient deux nombres :

- Le premier correspond aux commits propres au côté gauche.
- Le second correspond aux commits propres au côté droit.

Avec les références indiquées, le premier nombre correspond aux commits propres à `main`, tandis que le second correspond aux commits présents dans `origin/main` mais pas dans `main`.

Cela permet de repérer un décalage avant une synchronisation.

## 4. Fusion et rebasage : choisir la bonne méthode

Le cours débutant vous a présenté `git merge`. Cette section approfondit la différence entre la fusion et le rebasage.

### 4.1. Le fonctionnement de `git merge`

Une fusion réunit deux lignes de développement.

Exemple :

```text
A---B---C           main
         \
          D---E     feature-api
```

Si les branches ont divergé, Git peut créer un commit de fusion :

```text
A---B---C---------M     main
         \       /
          D-----E       feature-api
```

Le commit M possède généralement deux parents dans cet exemple.

La fusion conserve les commits originaux et rend visible le point auquel les travaux ont été réunis.

Commande :

```bash
git switch main
git merge feature-api
```

Lorsque la branche cible peut avancer directement jusqu'au commit de la branche source, Git peut réaliser un *fast-forward*, sans créer de commit de fusion distinct.

### 4.2. Le fonctionnement de `git rebase`

Le rebasage prend les changements d'une branche et les rejoue à partir d'une nouvelle base.

Avant :

```text
A---B---C           main
         \
          D---E     feature-api
```

Après :

```text
A---B---C---D'---E'    feature-api
```

Les commits D et E ont été remplacés par de nouveaux commits, représentés par D' et E'.

Même si les modifications de fichiers sont similaires, les identifiants des nouveaux commits sont différents. Un commit dépend notamment de ses métadonnées et de son parent ; changer la base change donc l'identité des commits créés.

Exemple :

```bash
git switch feature-api
git rebase main
```

Git rejoue les commits propres à `feature-api` au-dessus du sommet actuel de `main`.

Si la branche principale ne change pas pendant l'opération, une intégration ultérieure pourra généralement se faire par avance rapide :

```bash
git switch main
git merge feature-api
```

### 4.3. Comparaison

| Aspect | Merge | Rebase |
|---|---|---|
| Historique des commits originaux | Préservé | Les commits rejoués sont remplacés par de nouveaux commits. |
| Commit de fusion | Possible ou créé selon le cas | Pas de commit de fusion créé par le rebase lui-même. |
| Lecture de l'historique | Préserve les embranchements | Peut produire un historique plus linéaire. |
| Résolution de conflit | Pendant la fusion | Peut intervenir lors du rejeu de plusieurs commits. |
| Utilisation courante | Intégrer des travaux distincts en préservant leur chronologie | Mettre à jour une branche de travail ou nettoyer son historique local. |
| Risque principal | Conflits et graphe plus complexe | Réécriture d'historique et confusion si les commits étaient déjà partagés. |

Aucune des deux méthodes n'est universellement meilleure. Le choix dépend de la politique de l'équipe, de la manière dont l'historique doit être conservé et du fait que les commits aient ou non déjà été partagés.

### 4.4. Règle essentielle pour les rebasages

Évitez de rebaser des commits sur lesquels d'autres personnes ont déjà construit leur travail.

Un rebasage réécrit les commits concernés. Si ces commits sont déjà partagés, les collaborateurs peuvent se retrouver avec deux histoires concurrentes contenant des changements similaires.

Une règle pratique est la suivante :

- Rebaser une branche locale non partagée est généralement adapté.
- Rebaser une branche partagée nécessite une coordination explicite.
- Réécrire l'historique d'une branche principale partagée est une opération sensible qui doit suivre la politique du projet.

### 4.5. Désactiver l'avance rapide lorsque l'équipe le souhaite

Pour forcer la création d'un commit de fusion lorsque la fusion ne nécessite pas de résolution de conflit particulière :

```bash
git merge --no-ff feature-api
```

Cette option est utile lorsque l'équipe souhaite garder un commit d'intégration explicite pour chaque fonctionnalité.

Le choix entre `--no-ff`, un merge classique et un rebase doit être documenté dans les règles de contribution du projet.

## 5. Le rebasage interactif

Le rebasage interactif permet de modifier l'organisation d'une série de commits avant de les partager ou de les intégrer.

C'est l'un des outils les plus utiles lorsque l'historique local contient des commits intermédiaires tels que « correction », « oublie fichier » ou « petit fix ».

### 5.1. Afficher les commits à réorganiser

Supposons que votre branche contienne les quatre derniers commits suivants :

```text
a1b2c3d Ajout du calcul de disponibilité
b2c3d4e Correction du calcul
c3d4e5f Ajout des tests
d4e5f6a Correction d'un test
```

Pour examiner les quatre derniers commits en détail :

```bash
git log --oneline -4
```

Vérifiez d'abord que vous travaillez sur la bonne branche :

```bash
git status
git branch --show-current
```

Il est préférable d'avoir un état de travail propre avant de commencer une opération de réécriture.

### 5.2. Lancer un rebasage interactif

```bash
git rebase -i HEAD~4
```

Git ouvre alors un éditeur contenant la liste des commits à traiter.

Le nombre `4` désigne ici les quatre commits récents que vous souhaitez inclure dans l'opération, en supposant un historique linéaire correspondant à cette sélection.

La liste apparaît généralement du plus ancien au plus récent.

Exemple :

```text
pick a1b2c3d Ajout du calcul de disponibilité
pick b2c3d4e Correction du calcul
pick c3d4e5f Ajout des tests
pick d4e5f6a Correction d'un test
```

Chaque ligne indique une action à exécuter sur un commit.

### 5.3. Les actions les plus utiles

| Action | Signification |
|---|---|
| `pick` | Conserver le commit tel quel. |
| `reword` | Conserver le changement, mais modifier le message. |
| `edit` | Arrêter l'opération pour permettre de modifier le commit. |
| `squash` | Regrouper le changement avec le commit précédent et combiner les messages. |
| `fixup` | Regrouper le changement avec le commit précédent en écartant le message du commit regroupé. |
| `drop` | Supprimer le commit de la série réécrite. |

Des opérations supplémentaires, telles que le réordonnancement des lignes, sont également possibles.

Ne modifiez pas les lignes sans comprendre l'action demandée.

### 5.4. Modifier un message de commit

Pour modifier le message du deuxième commit, remplacez `pick` par `reword` :

```text
pick a1b2c3d Ajout du calcul de disponibilité
reword b2c3d4e Correction du calcul
pick c3d4e5f Ajout des tests
pick d4e5f6a Correction d'un test
```

Enregistrez et fermez l'éditeur.

Git vous proposera ensuite de modifier le message concerné.

Après validation, les commits concernés par la réécriture peuvent recevoir de nouveaux identifiants.

### 5.5. Regrouper deux commits

Supposons que les deux derniers commits constituent une seule fonctionnalité et que vous vouliez les réunir.

Avant :

```text
A---B---C---D
```

Vous pourriez obtenir :

```text
A---B---CD
```

Dans l'éditeur interactif :

```text
pick a1b2c3d Ajout du calcul de disponibilité
pick b2c3d4e Ajout des tests
squash c3d4e5f Correction du calcul
fixup d4e5f6a Correction d'un test
```

Ce bloc est illustratif : les identifiants et les messages doivent provenir de votre propre historique, et le choix exact de `squash` ou `fixup` dépend de la manière dont vous voulez construire le message final.

Le principe est que `squash` et `fixup` regroupent un commit avec le commit précédent dans la série.

Après un squash, Git peut ouvrir un éditeur pour préparer le message du commit regroupé.

Un historique compact facilite parfois la revue et la maintenance, mais il ne faut pas sacrifier une information utile pour réduire artificiellement le nombre de commits.

### 5.6. Modifier le contenu d'un ancien commit

Pour modifier le contenu d'un commit, changez `pick` en `edit`.

Exemple :

```text
pick a1b2c3d Initialisation du module
edit b2c3d4e Ajout du calcul
pick c3d4e5f Ajout des tests
```

Lorsque Git s'arrête :

1. Modifiez les fichiers concernés.
2. Préparez les modifications.
3. Corrigez le commit.
4. Reprenez le rebasage.

Commandes :

```bash
git add fichier.py
git commit --amend
git rebase --continue
```

Si plusieurs commits doivent être modifiés, le processus peut s'arrêter à plusieurs reprises.

### 5.7. Supprimer un commit d'un historique local

Dans l'éditeur interactif, la ligne d'un commit peut être retirée ou son action remplacée par `drop`.

Cela supprime le commit de la série réécrite. Les commits suivants seront rejoués sans lui.

Attention : si des commits ultérieurs dépendent de ses changements, le rebasage peut rencontrer des conflits ou produire un résultat incorrect. Il faut inspecter et tester le résultat.

### 5.8. Modifier l'ordre des commits

Supposons que deux commits indépendants soient présents :

```text
A---B---C---D
```

La réorganisation interactive peut placer les changements dans l'ordre C puis B, à condition que cela reste cohérent.

Réordonner des commits dépendants peut toutefois provoquer des conflits ou des erreurs intermédiaires. Un historique propre ne suffit pas si le code résultant ne fonctionne plus.

Après toute réécriture importante, exécutez les tests du projet.

### 5.9. Annuler ou poursuivre le rebasage

Pendant une opération de rebasage :

```bash
git status
```

Vous pouvez souvent continuer après la résolution des conflits avec :

```bash
git rebase --continue
```

Si vous souhaitez abandonner l'opération et revenir à son état de départ :

```bash
git rebase --abort
```

N'utilisez ces commandes que si un rebasage est effectivement en cours.

Si une opération s'est terminée mais que le résultat est incorrect, le mécanisme de récupération est différent. Il peut notamment être possible de retrouver la référence précédente avec `git reflog`, comme expliqué plus loin.

## 6. Mettre à jour une branche avec `git pull --rebase`

Dans une équipe, la branche principale continue parfois d'évoluer pendant le développement d'une fonctionnalité.

Exemple :

```text
A---B---C---D             origin/main
         \
          E---F           feature-api
```

Les commits E et F représentent le travail local. La branche distante contient un nouveau commit D.

Si vous voulez rejouer votre travail au-dessus de la dernière version connue de la branche distante, vous pouvez utiliser :

```bash
git fetch origin
git rebase origin/main
```

Depuis une branche locale qui suit la branche distante attendue, une autre possibilité est :

```bash
git pull --rebase
```

Cette commande récupère les changements distants puis rebase le travail local selon les règles de configuration et la situation de l'historique.

### 6.1. Vérifications avant le rebasage

Avant l'opération :

```bash
git status
git branch --show-current
git log --oneline --graph --decorate --all
```

Un état de travail propre est généralement préférable.

Si des changements locaux non enregistrés sont présents, décidez d'abord comment les conserver ou les isoler.

### 6.2. Configurer le comportement habituel de pull

Pour privilégier le rebasage dans les opérations de `pull` :

```bash
git config --global pull.rebase true
```

Cela modifie le comportement par défaut des opérations de pull pour l'utilisateur courant.

Cette configuration ne doit pas être adoptée aveuglément si l'équipe s'appuie sur un autre modèle d'intégration. La politique du projet reste prioritaire.

### 6.3. Résoudre un conflit pendant un rebase

Si un conflit survient :

```bash
git status
```

Ouvrez les fichiers en conflit, examinez les changements et corrigez le contenu.

Préparez les fichiers résolus :

```bash
git add fichier_resolu.py
```

Puis poursuivez :

```bash
git rebase --continue
```

Le rebasage peut s'arrêter plusieurs fois si plusieurs commits nécessitent une résolution.

Pour abandonner le processus en cours :

```bash
git rebase --abort
```

Après l'opération, contrôlez l'historique et exécutez les tests.

## 7. Transférer un commit avec `git cherry-pick`

Le rebasage déplace généralement une série de commits. `git cherry-pick` sert plutôt à appliquer le changement introduit par un commit spécifique sur la branche courante.

### 7.1. Quand l'utiliser ?

Imaginez deux branches :

```text
A---B---C                 main
     \
      D---E---F           feature-api
```

La branche `feature-api` contient plusieurs changements. Le commit E corrige une vulnérabilité qui doit être corrigée immédiatement dans `main`.

Vous ne souhaitez pas fusionner toute la fonctionnalité.

Vous pouvez appliquer uniquement le changement correspondant à E :

```bash
git switch main
git cherry-pick IDENTIFIANT_DU_COMMIT_E
```

Git applique le changement et crée normalement un nouveau commit sur la branche courante.

### 7.2. Pourquoi le nouvel identifiant peut-il être différent ?

Le commit d'origine est lié à son parent et à ses métadonnées.

Lorsqu'un changement est appliqué sur une autre branche, le nouveau commit aura généralement un parent différent et donc un identifiant distinct.

Cela signifie que le changement logique peut être similaire, mais que les deux commits ne sont pas nécessairement identiques.

### 7.3. Appliquer plusieurs commits

Vous pouvez indiquer plusieurs identifiants :

```bash
git cherry-pick COMMIT_A COMMIT_B
```

Git tente alors d'appliquer les changements des commits dans l'ordre indiqué.

Cette commande doit être utilisée avec prudence si les commits dépendent de changements intermédiaires qui ne sont pas présents sur la branche cible.

### 7.4. Cherry-pick avec conflit

Si Git ne peut pas appliquer un changement automatiquement :

```bash
git status
```

Résolvez les conflits, préparez les fichiers corrigés puis poursuivez l'opération :

```bash
git add fichier_resolu.py
git cherry-pick --continue
```

Pour annuler l'opération en cours :

```bash
git cherry-pick --abort
```

### 7.5. Éviter les duplications de changements

Un cherry-pick peut créer un nouveau commit dont le changement ressemble à celui d'un commit déjà présent ailleurs.

Avant de l'utiliser, demandez-vous si une fusion de branche complète serait plus appropriée.

Le cherry-pick est particulièrement pertinent pour :

- Des corrections urgentes.
- Le transfert d'un changement indépendant.
- La sélection de quelques commits précis.
- Le transfert d'une correction vers une branche de maintenance.

Il est moins adapté lorsqu'une longue série de commits dépendants doit être transférée dans son ensemble.

## 8. Utiliser `git stash`

### 8.1. Le problème du changement de contexte

Vous travaillez sur une fonctionnalité, mais une correction urgente doit être réalisée sur une autre branche.

Votre code local n'est pas encore prêt pour un commit. Vous ne souhaitez ni perdre les modifications ni créer un commit intermédiaire uniquement pour pouvoir changer de branche.

`git stash` permet de mettre temporairement des modifications de côté.

### 8.2. Enregistrer les modifications dans un stash

Pour mettre de côté les modifications suivies :

```bash
git stash push -m "Travail en cours sur la fonctionnalité API"
```

Git conserve alors les modifications suivies concernées dans une entrée de stash et restaure le répertoire de travail vers un état plus propre.

Les fichiers non suivis ne sont pas inclus par défaut.

Pour inclure également les fichiers non suivis :

```bash
git stash push -u -m "Travail API avec nouveaux fichiers"
```

L'option `-u` inclut les fichiers non suivis.

### 8.3. Afficher la liste des stashs

```bash
git stash list
```

Exemple :

```text
stash@{0}: On feature-api: Travail API avec nouveaux fichiers
stash@{1}: On main: Préparation d'une correction
```

Les entrées sont généralement numérotées de la plus récente vers la plus ancienne.

### 8.4. Réappliquer les modifications

Pour réappliquer le stash le plus récent sans le supprimer de la liste :

```bash
git stash apply
```

Pour appliquer une entrée précise :

```bash
git stash apply stash@{1}
```

Pour appliquer les modifications et supprimer l'entrée du stash si l'application réussit :

```bash
git stash pop
```

L'application d'un stash peut produire des conflits si le code a changé entre-temps.

### 8.5. Examiner le contenu d'un stash

```bash
git stash show
```

Pour afficher davantage de détails :

```bash
git stash show -p
```

Cette commande permet de consulter le patch contenu dans le stash.

### 8.6. Supprimer une entrée ou vider la liste

Supprimer une entrée spécifique :

```bash
git stash drop stash@{0}
```

Supprimer toutes les entrées de stash :

```bash
git stash clear
```

**Attention :** `git stash clear` est une opération destructive. Ne l'utilisez pas comme commande de nettoyage habituelle avant d'avoir vérifié que les modifications conservées ne sont plus nécessaires.

### 8.7. Les limites de `git stash`

Le stash n'est pas un système de sauvegarde longue durée.

Il peut être utile pour un changement de contexte rapide, mais les travaux importants doivent généralement être enregistrés dans un commit ou dans une branche adaptée.

Les fichiers ignorés ne sont pas inclus par défaut et les fichiers non suivis nécessitent l'option appropriée pour être stockés.

Une routine prudente est la suivante :

```text
Modifications locales
        |
        v
Vérification avec git status
        |
        v
git stash push -u -m "Description"
        |
        v
Changement de branche
        |
        v
Correction urgente
        |
        v
Retour à la branche de travail
        |
        v
git stash apply
        |
        v
Tests et vérifications
```

## 9. Récupérer du travail avec `git reflog`

### 9.1. Pourquoi le reflog est important

Les opérations de réécriture déplacent parfois une branche vers un nouvel historique.

Par exemple, vous exécutez :

```bash
git reset --hard HEAD~2
```

et vous constatez que des commits que vous vouliez conserver ne sont plus accessibles depuis votre branche courante.

Les commits ne sont pas nécessairement immédiatement supprimés des objets locaux. Le reflog enregistre des changements récents de références et peut aider à retrouver l'ancien emplacement de la branche.

### 9.2. Afficher le reflog

```bash
git reflog
```

Exemple de sortie simplifiée :

```text
f1e2d3c HEAD@{0}: reset: moving to HEAD~2
a2b3c4d HEAD@{1}: commit: Ajout des tests
b3c4d5e HEAD@{2}: commit: Ajout du module
c4d5e6f HEAD@{3}: commit: Initialisation
```

Les identifiants et le contenu varient selon le dépôt.

Le reflog permet de découvrir où `HEAD` pointait avant certaines opérations.

### 9.3. Retrouver un ancien commit

Supposons que `HEAD@{1}` indique la référence qui vous intéresse.

Inspectez d'abord ce commit :

```bash
git show HEAD@{1}
```

Vous pouvez aussi utiliser son identifiant complet ou abrégé affiché par le reflog.

### 9.4. Créer une branche de récupération

La méthode prudente consiste à créer une nouvelle branche sur le commit retrouvé :

```bash
git branch recuperation a2b3c4d
```

Remplacez l'identifiant par celui réellement obtenu dans votre dépôt.

Vous pouvez ensuite examiner cette branche :

```bash
git switch recuperation
git log --oneline --decorate -10
```

Cette méthode permet de retrouver le travail sans déplacer immédiatement la branche principale.

### 9.5. Pourquoi ne pas commencer directement par un reset ?

Il est souvent plus sûr de retrouver le commit, de créer une branche de récupération puis d'examiner le résultat.

Un nouveau reset prématuré peut compliquer la situation si vous n'avez pas encore compris les références en jeu.

### 9.6. Limites du reflog

Le reflog est un mécanisme local, pas une archive universelle.

Il ne garantit pas de retrouver n'importe quel commit supprimé, sur n'importe quelle machine et indéfiniment. Les entrées peuvent expirer et les objets devenus inaccessibles peuvent être nettoyés ultérieurement.

Si vous avez perdu un travail important :

1. Évitez d'exécuter des commandes de nettoyage.
2. Consultez immédiatement le reflog.
3. Identifiez les commits potentiellement utiles.
4. Créez une référence de récupération.
5. Vérifiez le contenu et les tests.

Pour les projets professionnels, des dépôts distants, des sauvegardes adaptées et une politique de gestion du code restent indispensables.

## 10. Diagnostiquer une régression avec `git bisect`

### 10.1. Le problème

Une application fonctionnait correctement il y a plusieurs semaines.

Aujourd'hui, un test échoue. Le dépôt contient cinquante commits depuis la dernière version connue comme fonctionnelle.

Inspecter chaque commit manuellement serait long.

`git bisect` permet d'utiliser une recherche dichotomique pour localiser le commit qui a introduit un défaut, à condition que vous puissiez déterminer si une version testée est fonctionnelle ou défectueuse.

### 10.2. Le principe de la recherche dichotomique

Au lieu de tester les cinquante commits un par un, Git sélectionne progressivement un commit situé dans l'historique.

Vous déterminez si ce commit est bon ou mauvais.

Git réduit alors la zone à examiner.

```text
Historique
     |
     v
+-----------------------+
| 50 commits possibles  |
+-----------------------+
            |
            v
    Tester un commit
            |
       +----+----+
       |         |
       v         v
      Bon      Mauvais
       |         |
       v         v
  Réduire la zone de recherche
            |
            v
    Tester le commit suivant
            |
            v
  Identifier le commit responsable
```

Pour une série linéaire et suffisamment bien définie, cette approche peut réduire nettement le nombre de versions à tester.

### 10.3. Démarrer la recherche

Imaginons que le commit courant soit défectueux, tandis qu'un ancien commit connu est correct.

Démarrez :

```bash
git bisect start
git bisect bad
git bisect good IDENTIFIANT_DU_COMMIT_FONCTIONNEL
```

Git sélectionne alors une version intermédiaire à examiner.

### 10.4. Tester chaque version

À chaque sélection, exécutez le test qui reproduit le problème.

Si le comportement est correct :

```bash
git bisect good
```

Si le comportement est incorrect :

```bash
git bisect bad
```

Git poursuit la recherche jusqu'à identifier le commit qui introduit le changement de comportement.

Il est important d'utiliser exactement la même définition de « bon » et de « mauvais » tout au long de la recherche.

Si le test ne peut pas être exécuté sur une version particulière, consultez l'aide de la commande concernant les commits impossibles à tester et la possibilité de les ignorer.

### 10.5. Afficher le journal de la recherche

```bash
git bisect log
```

Cette commande permet de consulter les décisions prises pendant la recherche.

### 10.6. Terminer la recherche

Lorsque Git identifie le commit recherché, quittez le mode bisect :

```bash
git bisect reset
```

Cette commande restaure généralement la position du dépôt avant le démarrage de la recherche.

Après cela, vous pouvez examiner le commit responsable :

```bash
git show IDENTIFIANT_DU_COMMIT
```

### 10.7. Automatiser la recherche

Si le projet dispose d'un test reproductible qui retourne un code de sortie non nul lorsqu'il détecte le défaut, il est possible d'automatiser certaines étapes.

Exemple indicatif :

```bash
git bisect start
git bisect bad HEAD
git bisect good IDENTIFIANT_DU_COMMIT_FONCTIONNEL
git bisect run python -m unittest tests.test_regression
git bisect reset
```

Cette approche n'est adaptée que si :

- Le test peut être exécuté de manière reproductible sur les versions examinées.
- Ses codes de sortie sont interprétés correctement.
- Ses dépendances sont disponibles.
- Les résultats ne dépendent pas d'un service externe instable.

Le choix du test est déterminant : un mauvais test peut attribuer incorrectement la régression à un commit.

## 11. Gérer les références distantes et les branches de suivi

### 11.1. Comprendre `origin/main`

Lorsque vous clonez un dépôt distant, Git crée généralement une référence distante de suivi telle que :

```text
origin/main
```

Cette référence représente l'état de la branche distante `main` connu par votre dépôt local après les opérations de récupération.

Elle ne change pas instantanément quand une autre personne pousse un nouveau commit sur le serveur. Pour actualiser vos informations, vous devez récupérer les changements.

### 11.2. Mettre à jour les références distantes

```bash
git fetch origin
```

Cette commande actualise les références distantes connues localement et récupère les objets nécessaires.

Pour afficher les branches :

```bash
git branch -a
```

Pour examiner leur historique :

```bash
git log --oneline --graph --decorate --all
```

### 11.3. Configurer une branche de suivi

Lors de la publication d'une nouvelle branche :

```bash
git push -u origin feature-api
```

L'option `-u` configure généralement la relation de suivi de la branche locale avec la branche distante.

Ensuite, des commandes comme :

```bash
git pull
git push
```

peuvent utiliser la branche distante configurée par défaut.

### 11.4. Supprimer une branche distante

Après la fusion d'une fonctionnalité, l'équipe peut supprimer sa branche distante.

```bash
git push origin --delete feature-api
```

Cette commande supprime la référence distante nommée. Elle ne doit être utilisée qu'après avoir confirmé que la branche n'est plus nécessaire.

Pour nettoyer les références distantes locales qui correspondent à des branches supprimées du serveur :

```bash
git fetch --prune
```

`--prune` met à jour les références de suivi obsolètes. Il ne s'agit pas d'une commande qui doit supprimer vos branches locales ordinaires.

### 11.5. Vérifier l'amont d'une branche

Pour afficher la branche distante suivie par la branche courante :

```bash
git status -sb
```

Pour examiner les configurations de branche :

```bash
git branch -vv
```

Ces commandes aident à comprendre pourquoi un `pull` ou un `push` ne cible pas la destination attendue.

## 12. Utiliser le push forcé de façon sûre

### 12.1. Pourquoi un push peut-il être rejeté ?

Un dépôt distant peut refuser une mise à jour si l'envoi ferait perdre des commits présents sur la branche distante.

Ce comportement est une protection normale.

Il ne faut pas considérer tout refus de push comme un problème qu'il faudrait éliminer en ajoutant immédiatement `--force`.

### 12.2. Le risque du push forcé

La commande :

```bash
git push --force
```

demande à Git d'effectuer une mise à jour forcée de la référence distante.

Elle peut remplacer la référence de la branche distante et rendre difficiles à retrouver les commits qui y étaient précédemment accessibles.

Sur une branche partagée, cela peut perturber le travail d'autres développeurs.

### 12.3. L'option `--force-with-lease`

Dans certains cas, après une réécriture intentionnelle d'une branche personnelle déjà publiée, une mise à jour forcée est nécessaire.

Une option plus prudente est :

```bash
git push --force-with-lease
```

Elle demande à Git de vérifier que la référence distante correspond toujours à l'état attendu avant d'effectuer la mise à jour forcée.

Cette protection aide à éviter d'écraser silencieusement un changement distant dont vous n'aviez pas connaissance.

Elle ne rend toutefois pas l'opération sans risque. La bonne pratique consiste à vérifier la situation distante, à comprendre l'historique et à coordonner la réécriture avec les personnes concernées.

### 12.4. Procédure prudente

Avant toute opération forcée :

```bash
git status
git fetch origin
git log --oneline --graph --decorate --all
git branch -vv
```

Posez-vous ensuite les questions suivantes :

- La branche m'appartient-elle ou est-elle partagée ?
- Pourquoi faut-il réécrire l'historique ?
- Des commits distants ont-ils été ajoutés depuis ma dernière récupération ?
- D'autres personnes peuvent-elles dépendre des commits actuels ?
- Existe-t-il une procédure documentée pour cette opération ?

Si la réponse n'est pas claire, ne forcez pas le push.

## 13. Corriger l'historique sans perdre de changements

Plusieurs commandes peuvent intervenir sur les commits. Elles n'ont toutefois pas la même intention.

### 13.1. `git commit --amend`

Modifie le dernier commit en le remplaçant par un nouveau commit.

Exemple : un fichier oublié doit être inclus dans le dernier commit local.

```bash
git add fichier-oublie.py
git commit --amend
```

Cette méthode est utile avant le partage d'un commit.

Si le commit a déjà été partagé, réfléchissez aux conséquences de sa réécriture avant de l'utiliser.

### 13.2. `git reset`

La commande `git reset` déplace une référence et peut aussi modifier la zone de préparation et le répertoire de travail selon l'option choisie.

Exemple :

```bash
git reset --soft HEAD~1
```

Cette variante déplace généralement la branche d'un commit en arrière tout en conservant la zone de préparation et les fichiers de travail.

Avec le mode mixte :

```bash
git reset --mixed HEAD~1
```

Git déplace la référence et réinitialise la zone de préparation, mais conserve normalement les modifications dans les fichiers de travail.

Le mode mixte est le comportement par défaut lorsqu'aucune option de mode n'est fournie.

Avec :

```bash
git reset --hard HEAD~1
```

Git modifie la référence, l'index et le répertoire de travail. Des changements peuvent être perdus.

N'utilisez pas ce dernier exemple sur un dépôt qui contient un travail important que vous n'avez pas protégé.

### 13.3. `git revert`

Inverse le changement associé à un commit en créant un nouveau commit.

```bash
git revert IDENTIFIANT_DU_COMMIT
```

Cette approche est souvent adaptée lorsqu'il faut annuler une modification déjà partagée tout en conservant la chronologie du projet.

### 13.4. Tableau de choix

| Situation | Approche envisageable |
|---|---|
| Le dernier commit local doit être complété | `git commit --amend` |
| Annuler un commit local tout en gardant les changements préparés | `git reset --soft` |
| Annuler un commit local et remettre ses changements dans le répertoire de travail | `git reset --mixed` |
| Revenir à l'état d'un commit en remplaçant aussi les modifications du répertoire de travail | `git reset --hard`, uniquement après vérifications |
| Inverser un commit partagé sans réécrire l'historique | `git revert` |
| Retrouver une ancienne position d'une branche après une erreur | Examiner `git reflog` |

Il ne faut pas choisir une commande uniquement parce qu'elle est courte. Il faut déterminer quel état doit être conservé : l'historique, la zone de préparation et le répertoire de travail.

## 14. Comprendre les conflits plus profondément

### 14.1. Un conflit ne concerne pas toujours une seule ligne

Les conflits peuvent affecter :

- Des lignes d'un même fichier.
- Des fichiers renommés.
- Des suppressions et modifications simultanées.
- Des fichiers créés indépendamment.
- Des modifications de structures ou de dépendances.
- Des changements complexes de configuration.

Le conflit peut nécessiter une compréhension du comportement attendu du programme, et pas seulement un choix textuel.

### 14.2. Les trois versions d'une fusion

Lors d'une fusion à trois voies, Git s'appuie sur trois états conceptuels :

- **Base** : état commun à partir duquel les branches ont divergé.
- **Ours** (*ours*) : état de la branche courante.
- **Theirs** (*theirs*) : état de l'autre branche que vous essayez d'intégrer.

Les marqueurs de conflit usuels représentent les deux côtés de la fusion. Des outils de comparaison peuvent afficher les trois versions pour aider à reconstruire l'intention.

La signification d'« ours » et « theirs » varie selon l'opération en cours. Pendant un rebasage, il faut être particulièrement attentif : les branches et les commits sont rejoués dans un contexte différent de celui d'une fusion classique.

### 14.3. Utiliser un outil de comparaison

Git peut afficher des différences :

```bash
git diff
```

Pendant un conflit, utilisez également :

```bash
git status
```

Selon la configuration du dépôt, des outils graphiques peuvent aider à examiner les différentes versions.

Vous pouvez consulter les paramètres des outils de fusion :

```bash
git config --get merge.tool
```

Cette commande peut ne rien afficher si aucun outil n'est configuré.

### 14.4. Ne pas résoudre un conflit uniquement pour faire disparaître les marqueurs

Après la résolution, vérifiez :

- Que tous les marqueurs ont été supprimés.
- Que les fonctionnalités concernées conservent le comportement voulu.
- Que les imports et dépendances restent cohérents.
- Que les tests pertinents réussissent.
- Que les fichiers de configuration restent valides.

Un fichier peut ne plus contenir de marqueurs de conflit tout en étant incorrect.

## 15. Les worktrees : plusieurs répertoires de travail pour un même dépôt

### 15.1. Quel problème résolvent-ils ?

Vous travaillez sur une fonctionnalité dans un dépôt. Une correction urgente exige de passer sur une autre branche, mais vous ne voulez pas interrompre ni modifier votre répertoire de travail actuel.

Une solution classique serait de mettre les changements dans un stash, de changer de branche, puis de réappliquer le stash.

Git propose également les **worktrees**, qui permettent d'utiliser plusieurs répertoires de travail associés au même dépôt.

### 15.2. Créer un worktree pour une branche

Depuis le dépôt principal :

```bash
git worktree add ../hotfix-api -b hotfix/api main
```

Cette commande demande à Git de créer un nouveau répertoire de travail `../hotfix-api`, associé à la nouvelle branche `hotfix/api` créée à partir de `main`.

Vous pouvez ensuite travailler dans ce répertoire :

```bash
cd ../hotfix-api
git status
```

Le répertoire principal continue d'exister et de conserver son propre état de travail.

### 15.3. Afficher les worktrees

```bash
git worktree list
```

Cette commande affiche les répertoires de travail associés au dépôt.

### 15.4. Supprimer un worktree

Lorsque le travail est terminé, quittez le répertoire concerné puis supprimez le worktree :

```bash
git worktree remove ../hotfix-api
```

La commande peut refuser l'opération si le répertoire de travail contient des changements que Git considère comme non protégés.

Ne forcez pas la suppression avant d'avoir contrôlé ces changements.

### 15.5. Worktree et clone : quelle différence ?

Un clone crée généralement une copie distincte du dépôt avec sa propre configuration locale et ses propres références locales.

Un worktree crée un répertoire de travail supplémentaire associé au même dépôt administratif.

Les worktrees sont utiles pour travailler simultanément sur plusieurs branches, mais certaines références et certaines branches ne peuvent pas être utilisées simultanément dans plusieurs worktrees de la même manière.

### 15.6. Cas d'utilisation

Les worktrees sont adaptés à des scénarios comme :

- Correction urgente pendant le développement d'une fonctionnalité.
- Comparaison de deux versions d'un programme.
- Tests sur plusieurs branches.
- Préparation d'une version de maintenance.
- Analyse d'une régression sans interrompre le travail principal.

## 16. Automatiser l'application de certaines résolutions avec `rerere`

### 16.1. À quoi sert `rerere` ?

Le nom `rerere` signifie *reuse recorded resolution*.

Cette fonctionnalité permet à Git d'enregistrer certaines résolutions de conflits et de les réutiliser lorsqu'un conflit similaire réapparaît.

Elle peut être utile dans des branches longues ou dans des opérations de rebasage répétées.

### 16.2. Activer `rerere`

Pour le dépôt courant :

```bash
git config rerere.enabled true
```

Pour tous les dépôts de l'utilisateur courant :

```bash
git config --global rerere.enabled true
```

L'option globale doit être choisie uniquement si vous souhaitez adopter ce comportement de manière générale.

### 16.3. Ce que `rerere` ne fait pas

`rerere` ne remplace pas l'analyse technique.

Une résolution enregistrée antérieurement peut ne plus être correcte si le contexte fonctionnel a changé.

Après toute résolution réutilisée, examinez le diff et exécutez les tests.

Cette fonctionnalité est un moyen de réduire certaines tâches répétitives, pas une autorisation de fusionner automatiquement des changements sans contrôle.

## 17. Sélectionner précisément les modifications avec `git add -p`

### 17.1. Le besoin

Un même fichier contient deux modifications indépendantes.

Vous souhaitez enregistrer la première dans un commit, mais laisser la seconde pour plus tard.

Un simple :

```bash
git add fichier.py
```

préparerait généralement toutes les modifications du fichier.

L'ajout interactif permet de sélectionner certaines parties du diff.

### 17.2. Utiliser l'ajout interactif

```bash
git add -p fichier.py
```

Git affiche les changements par blocs, appelés *hunks*, puis propose plusieurs actions.

Les options exactes affichées dépendent du contexte et de la version de Git, mais les plus fréquentes comprennent :

- `y` : préparer le bloc affiché.
- `n` : ne pas préparer le bloc affiché.
- `s` : tenter de diviser un bloc en blocs plus petits.
- `e` : modifier manuellement le patch préparé.
- `q` : arrêter la sélection.

Utilisez l'option affichée par votre version de Git et lisez les indications avant de répondre.

### 17.3. Exemple pratique

Supposons que `app.py` contienne :

1. Une correction urgente.
2. Une nouvelle fonctionnalité encore incomplète.

Vous souhaitez d'abord créer un commit contenant uniquement la correction.

Procédure :

```bash
git diff app.py
git add -p app.py
git diff --cached
git diff
```

Examinez le diff préparé et le diff restant.

Puis créez le commit :

```bash
git commit -m "Correction du traitement des erreurs"
```

Les modifications non préparées restent dans le répertoire de travail.

Cette pratique permet de constituer des commits plus cohérents, même lorsque plusieurs changements ont été réalisés dans un même fichier.

## 18. Comparer des séries de commits avec `git range-diff`

### 18.1. Quand utiliser cet outil ?

Après un rebasage interactif, les identifiants des commits ont changé. Vous souhaitez vérifier si la nouvelle série conserve les changements de la série précédente.

Une comparaison classique de graphes montre les différences de références et de commits, mais elle n'est pas toujours suffisante pour comprendre si les patches ont été modifiés.

`git range-diff` compare deux séries de commits en recherchant les changements qui correspondent d'une version à l'autre.

### 18.2. Exemple général

```bash
git range-diff main..ancienne-branche main..nouvelle-branche
```

Cet exemple est indicatif : les références doivent être choisies selon l'historique réel. Il faut comparer deux plages représentant le même travail avant et après la transformation.

Cette commande est utile pour :

- Vérifier un rebasage interactif.
- Examiner une série de commits avant une pull request.
- Comparer une version précédente d'une branche à sa nouvelle version.
- Contrôler les modifications introduites pendant une réorganisation des commits.

### 18.3. Limites

`range-diff` est conçu pour faciliter la lecture humaine des séries de commits. Son affichage ne doit pas être traité comme un format stable destiné à un programme sans précaution.

Il ne remplace pas les tests et ne prouve pas, à lui seul, que les deux séries ont exactement le même comportement.

## 19. Les tags et la gestion des versions

Les tags permettent d'identifier certains points de l'historique, souvent associés à une publication.

### 19.1. Créer un tag annoté

```bash
git tag -a v1.2.0 -m "Publication de la version 1.2.0"
```

Le tag est associé au commit courant si aucun autre point de l'historique n'est indiqué.

Pour désigner explicitement un commit :

```bash
git tag -a v1.2.0 IDENTIFIANT_DU_COMMIT -m "Publication de la version 1.2.0"
```

### 19.2. Examiner un tag

```bash
git show v1.2.0
```

Cette commande permet de consulter les informations du tag et le commit associé.

### 19.3. Envoyer un tag au serveur

```bash
git push origin v1.2.0
```

Cette opération publie le tag désigné vers le dépôt distant.

La création du tag et l'envoi d'un tag sont deux opérations distinctes.

### 19.4. Déplacer un tag : attention

Un tag publié est souvent utilisé pour identifier une version stable.

Le déplacer vers un autre commit peut semer la confusion, notamment si une version a déjà été téléchargée ou déployée par d'autres personnes.

Évitez de réutiliser un nom de version publié pour un contenu différent, sauf si le processus de publication du projet prévoit explicitement cette opération.

Une version stable doit correspondre à un point identifié et reproductible de l'historique.

## 20. Sécurité et hygiène d'un dépôt

### 20.1. Les secrets ne doivent pas être versionnés

Git peut conserver les anciennes versions des fichiers suivis.

Si une clé d'API est ajoutée à un fichier puis supprimée dans un commit ultérieur, le secret peut encore être présent dans l'historique et accessible aux personnes qui peuvent consulter ce dernier.

La suppression dans le dernier commit ne suffit donc pas à éliminer une exposition.

Si un secret a été publié :

1. Révoquez ou renouvelez le secret.
2. Vérifiez les accès susceptibles d'avoir été effectués.
3. Identifiez les dépôts et copies concernés.
4. Appliquez la procédure de nettoyage d'historique si elle est nécessaire.
5. Informez les personnes concernées et vérifiez le résultat.

La réécriture de l'historique peut perturber les clones existants. Elle doit donc être coordonnée.

### 20.2. Prévenir les publications involontaires

Avant un commit :

```bash
git status
git diff --cached
```

Examinez les fichiers préparés.

Recherchez les éléments qui ne devraient pas être publiés :

- Mots de passe.
- Clés privées.
- Jetons d'accès.
- Fichiers `.env`.
- Données personnelles.
- Archives contenant des informations confidentielles.
- Fichiers temporaires ou résultats locaux.

Le fichier `.gitignore` aide à éviter l'ajout accidentel, mais il ne remplace pas un contrôle du diff.

### 20.3. Vérifier les changements avant une fusion

Dans un projet partagé, les changements doivent être examinés avant leur intégration.

Les contrôles peuvent inclure :

- Une revue de code.
- Des tests automatisés.
- Des analyses statiques.
- Une vérification des dépendances.
- Des règles de protection de branche.
- Des approbations adaptées au niveau de risque.

Git facilite l'identification des modifications. Il ne garantit pas que le code est sécurisé.

### 20.4. Signatures de commits et de tags

Git permet de signer des commits et des tags avec des mécanismes cryptographiques pris en charge.

Par exemple, dans une configuration compatible avec GPG :

```bash
git commit -S -m "Ajout de la validation des entrées"
```

Cette commande suppose qu'une configuration de signature est disponible et fonctionnelle.

Vous pouvez vérifier les paramètres configurés :

```bash
git config --get commit.gpgsign
git config --get user.signingkey
```

La commande peut ne rien retourner si aucun paramètre correspondant n'est défini.

Une signature permet de vérifier une identité ou l'intégrité du contenu signé dans le contexte de la clé utilisée. Elle ne démontre pas automatiquement que le contenu est correct ou sûr.

Les règles de signature doivent être définies en fonction des exigences du dépôt et de l'équipe.

## 21. Accélérer Git sans dégrader le dépôt

### 21.1. Utiliser des alias

Git permet de définir des alias pour les commandes fréquentes.

Exemple :

```bash
git config --global alias.lg "log --graph --oneline --decorate --all"
```

Vous pouvez ensuite exécuter :

```bash
git lg
```

Autre exemple :

```bash
git config --global alias.st "status -sb"
```

Puis :

```bash
git st
```

Les alias raccourcissent les commandes, mais ils doivent rester compréhensibles par les personnes qui utiliseront votre terminal.

Dans une équipe, documentez les alias nécessaires si les procédures reposent dessus.

### 21.2. Créer un modèle de message de commit

Un modèle peut aider l'équipe à structurer les messages de commit.

Par exemple, créez un fichier `~/.gitmessage` contenant :

```text
Résumé du changement

Contexte :
- Pourquoi ce changement est nécessaire.

Modification :
- Ce qui a été modifié.

Vérifications :
- Tests exécutés.
```

Configurez ensuite Git pour utiliser le fichier :

```bash
git config --global commit.template ~/.gitmessage
```

Cette syntaxe correspond aux environnements utilisant le répertoire `~` pour le dossier personnel. Adaptez le chemin si nécessaire.

Le modèle peut être utile pour les changements importants, mais il n'est pas obligatoire pour chaque commit.

### 21.3. Ne pas confondre alias et fonction

Un alias Git raccourcit une commande. Il ne change pas la sémantique sous-jacente des opérations.

Un alias qui masque une commande risquée peut rendre les interventions moins sûres.

Choisissez des noms explicites et évitez de créer des alias ambigus pour les commandes qui peuvent perdre du travail.

## 22. Atelier pratique complet : récupérer, réorganiser et livrer une fonctionnalité

Cet atelier met en œuvre plusieurs techniques du cours dans un dépôt de laboratoire.

### 22.1. Préparer le dépôt

Créez un nouveau dépôt :

```bash
mkdir git-intermediaire-lab
cd git-intermediaire-lab
git init
```

Créez un fichier `README.md` contenant :

```markdown
# Laboratoire Git intermédiaire

Ce dépôt sert à pratiquer :
- Les branches et les fusions.
- Le rebasage interactif.
- Le cherry-pick.
- Le stash.
- La récupération d'un commit.
```

Enregistrez le fichier :

```bash
git add README.md
git commit -m "Initialisation du laboratoire"
```

### 22.2. Créer une branche de fonctionnalité

```bash
git switch -c feature/etat-service
```

Créez `service.py` :

```python
def etat_service(disponible):
    if disponible:
        return "disponible"

    return "indisponible"
```

Enregistrez le changement :

```bash
git add service.py
git commit -m "Ajout du calcul de l'état du service"
```

### 22.3. Ajouter un test

Créez `test_service.py` :

```python
from service import etat_service


def test_service_disponible():
    assert etat_service(True) == "disponible"


def test_service_indisponible():
    assert etat_service(False) == "indisponible"
```

Enregistrez ce test :

```bash
git add test_service.py
git commit -m "Ajout des tests de l'état du service"
```

Si `pytest` est installé, vous pouvez tester le module avec :

```bash
pytest -q
```

Sinon, installez l'outil dans un environnement adapté ou utilisez ce laboratoire pour étudier les mécanismes Git indépendamment de l'exécution des tests.

### 22.4. Créer un commit de correction

Ajoutez une docstring à la fonction :

```python
def etat_service(disponible):
    """Retourne un état lisible selon la disponibilité du service."""
    if disponible:
        return "disponible"

    return "indisponible"
```

Puis :

```bash
git add service.py
git commit -m "Documentation de la fonction d'état"
```

Vous disposez maintenant de plusieurs commits sur la branche de fonctionnalité.

### 22.5. Examiner l'historique

```bash
git log --graph --oneline --decorate --all
```

Identifiez les commits associés au module, aux tests et à la documentation.

### 22.6. Réorganiser les derniers commits

Sur la branche de fonctionnalité :

```bash
git rebase -i HEAD~2
```

Dans l'éditeur, vous pouvez par exemple choisir de regrouper les changements de documentation avec le commit d'ajout du module, à condition que cela soit cohérent avec les dépendances et le contenu réel des commits.

Après le rebasage :

```bash
git log --graph --oneline --decorate --all
```

Exécutez de nouveau les tests.

### 22.7. Créer une modification indépendante sur une autre branche

Revenez sur la branche principale :

```bash
git switch main
```

Créez une correction indépendante dans le fichier `README.md`, par exemple en ajoutant une courte section sur la procédure de test.

Enregistrez-la :

```bash
git add README.md
git commit -m "Documentation de la procédure de test"
```

Si vous souhaitez transférer ce changement sur une branche distincte, identifiez son commit avec :

```bash
git log --oneline -5
```

La sélection et le transfert par cherry-pick doivent se faire à partir des identifiants réels de votre historique.

### 22.8. Tester le stash

Sur la branche de fonctionnalité, modifiez `service.py` sans créer de commit.

Vérifiez :

```bash
git status
```

Mettez le changement de côté :

```bash
git stash push -m "Expérimentation sur le service"
```

Affichez les stashs :

```bash
git stash list
```

Réappliquez le changement :

```bash
git stash apply
```

Vérifiez que la modification a été réappliquée, puis annulez-la ou conservez-la selon vos besoins.

Ne supprimez pas le stash avant d'avoir confirmé que vous avez retrouvé et enregistré le travail attendu.

### 22.9. Explorer la récupération

Dans le dépôt de laboratoire, créez une branche dédiée à l'exercice de récupération, ou utilisez une branche de test temporaire.

Consultez :

```bash
git reflog
```

Identifiez plusieurs positions récentes de `HEAD` et observez les références associées.

Ne lancez pas un `reset --hard` sur un dépôt contenant un travail précieux pour reproduire artificiellement une erreur.

Si vous souhaitez aller plus loin, créez un dépôt de test séparé, réalisez quelques commits sans importance puis expérimentez une réinitialisation sur ce dépôt.

### 22.10. Bilan de l'atelier

À la fin de cette pratique, vous devez savoir :

- Repérer les commits concernés dans le graphe.
- Réorganiser une courte série de commits.
- Mettre un changement temporairement de côté.
- Examiner les références enregistrées dans le reflog.
- Vérifier le résultat d'une réécriture avec les tests.
- Utiliser des techniques de récupération sans agir aveuglément sur la branche principale.

## 23. Exercices de compréhension

### Exercice 1 : lire un graphe

Considérez l'historique suivant :

```text
A---B---C---F       main
     \
      D---E         feature
```

Répondez :

1. Quels commits sont communs aux deux branches ?
2. Quels commits sont spécifiques à `feature` dans cet exemple ?
3. Quelles méthodes peuvent servir à intégrer le travail de `feature` dans `main` ?
4. Si vous rebasez `feature` sur `main`, que devient l'identité des commits D et E ?

### Exercice 2 : merge ou rebase ?

Une équipe souhaite conserver la trace explicite du point où chaque fonctionnalité a été intégrée à la branche principale.

Quelle stratégie peut convenir et pourquoi ?

Une autre équipe veut que les branches de fonctionnalité possèdent un historique linéaire avant leur intégration. Quelle stratégie peut convenir ?

### Exercice 3 : rebasage interactif

Vous avez les commits suivants :

```text
A : Initialisation
B : Ajout de la fonction
C : Correction de la fonction
D : Ajout des tests
```

Vous souhaitez conserver A, regrouper B et C, puis garder D comme commit séparé.

Quelle commande permet d'ouvrir le rebasage interactif adapté et quelle opération doit être choisie pour le regroupement ?

### Exercice 4 : cherry-pick

Le commit `abc1234` contient une correction urgente sur une branche de fonctionnalité. Vous voulez appliquer cette correction sur `main` sans fusionner toute la branche.

Écrivez les commandes et expliquez une précaution à prendre avant de les exécuter.

### Exercice 5 : conflit pendant un rebase

Un rebasage s'arrête sur un conflit.

Quels sont les contrôles et les étapes nécessaires pour terminer le rebasage en conservant le résultat voulu ?

### Exercice 6 : commit perdu

Vous venez d'effectuer un reset qui a déplacé la branche courante avant deux commits que vous vouliez conserver.

Comment rechercher l'ancien état de la branche et sécuriser les commits retrouvés ?

### Exercice 7 : stash

Vous possédez une modification suivie ainsi qu'un nouveau fichier non suivi. Vous devez changer de branche sans commiter le travail.

Quelle commande permet de mettre de côté ces deux catégories de modifications ?

Comment réappliquer le stash et quelle vérification devez-vous effectuer avant de le supprimer ?

### Exercice 8 : bisect

Un test réussissait au commit A et échoue sur le commit Z. Il y a de nombreux commits intermédiaires.

Expliquez comment `git bisect` permet de localiser le commit responsable.

### Exercice 9 : force-with-lease

Une branche personnelle a été rebasée et a déjà été publiée. Avant de pousser sa nouvelle histoire, pourquoi est-il préférable de récupérer les dernières informations distantes et pourquoi `--force-with-lease` reste-t-il une opération à utiliser avec prudence ?

### Exercice 10 : interpréter `git log main..feature`

Que sélectionne cette commande ?

```bash
git log main..feature --oneline
```

Comment obtenir les commits présents sur `main` mais absents de `feature` ?

### Exercice 11 : worktrees

Vous travaillez sur une fonctionnalité et devez corriger en parallèle un bug de production.

Expliquez pourquoi un worktree peut être utile et proposez une commande pour en créer un pour la correction urgente.

### Exercice 12 : sécurité du dépôt

Une clé d'API a été commitée puis supprimée dans un commit ultérieur.

Pourquoi la suppression ne suffit-elle pas ? Quelles actions faut-il prendre ?

## 24. Corrigés des exercices

### Corrigé 1

1. A et B sont les ancêtres communs représentés dans le schéma.
2. D et E sont les commits spécifiques à la branche `feature` dans l'exemple.
3. Il est possible d'utiliser `merge` pour préserver la structure de l'historique, ou `rebase` pour rejouer les changements de la branche sur une base actualisée.
4. Les commits D et E sont rejoués et produisent normalement de nouveaux commits, dont les identifiants diffèrent de ceux des commits originaux.

### Corrigé 2

Une équipe qui veut conserver un point d'intégration explicite peut préférer une fusion avec commit de merge, éventuellement en utilisant `--no-ff` lorsque sa politique le prévoit.

Une équipe qui souhaite des branches linéaires avant leur intégration peut préférer rebaser la branche de fonctionnalité sur la branche cible, puis effectuer une intégration par avance rapide si possible.

Le choix doit rester cohérent avec le processus du projet.

### Corrigé 3

Pour inclure les trois derniers commits après A dans une série linéaire :

```bash
git rebase -i HEAD~3
```

Dans l'éditeur, il faut conserver B, puis utiliser `squash` ou `fixup` sur C afin de le regrouper avec B. D doit rester séparé.

Le choix entre `squash` et `fixup` dépend du message souhaité pour le commit résultant.

### Corrigé 4

```bash
git switch main
git cherry-pick abc1234
```

Avant l'opération, vérifiez que le commit est adapté à `main`, que les changements dont il dépend existent déjà et que le répertoire de travail est propre.

### Corrigé 5

La procédure typique est la suivante :

```bash
git status
```

Examinez et corrigez les fichiers en conflit, puis :

```bash
git add fichier_resolu
git rebase --continue
```

Si le processus doit être abandonné :

```bash
git rebase --abort
```

Après la fin du rebasage, inspectez l'historique et exécutez les tests.

### Corrigé 6

Utilisez :

```bash
git reflog
```

Repérez l'ancien commit, inspectez-le puis créez une branche de récupération :

```bash
git show IDENTIFIANT_DU_COMMIT
git branch recuperation IDENTIFIANT_DU_COMMIT
```

Cette méthode sécurise une référence vers le travail retrouvé avant d'envisager une autre manipulation sur la branche principale.

### Corrigé 7

Pour inclure les modifications suivies et les fichiers non suivis :

```bash
git stash push -u -m "Travail temporaire"
```

Pour réappliquer :

```bash
git stash apply
```

Vérifiez le résultat avec `git status` et examinez les fichiers réappliqués. Ne supprimez l'entrée du stash qu'après avoir confirmé que les changements ont été correctement récupérés.

### Corrigé 8

Il faut marquer une version connue comme défectueuse avec `git bisect bad` et une version connue comme fonctionnelle avec `git bisect good`.

Git sélectionne des commits intermédiaires à tester et réduit progressivement l'intervalle de recherche. Il est nécessaire de définir un test reproductible et d'utiliser des critères constants pour désigner les versions bonnes et mauvaises.

À la fin :

```bash
git bisect reset
```

### Corrigé 9

La récupération des dernières informations permet de comprendre si la branche distante a été modifiée depuis la dernière consultation.

`--force-with-lease` aide à éviter d'écraser un état distant inattendu, mais il ne remplace ni l'inspection de l'historique ni la coordination avec les collaborateurs. Une réécriture peut perturber toute personne qui utilise déjà les anciens commits.

### Corrigé 10

```bash
git log main..feature --oneline
```

affiche les commits accessibles depuis `feature` mais pas depuis `main`.

Pour afficher les commits présents sur `main` mais absents de `feature` :

```bash
git log feature..main --oneline
```

### Corrigé 11

Un worktree permet d'avoir deux répertoires de travail associés au même dépôt, ce qui évite de devoir modifier en permanence le répertoire principal ou de mettre le travail courant de côté.

Par exemple :

```bash
git worktree add ../hotfix-api -b hotfix/api main
```

La commande suppose que le dépôt et la branche de base `main` existent.

### Corrigé 12

Le secret peut encore se trouver dans les anciens commits, les clones, les caches ou d'autres copies du dépôt.

Il faut révoquer ou renouveler immédiatement la clé exposée, examiner les accès potentiellement réalisés, puis suivre la procédure de nettoyage d'historique appropriée si nécessaire.

La suppression du fichier dans un commit ultérieur ne révoque pas la clé et n'efface pas les versions antérieures.

## 25. Projet de fin de niveau : maintenance avancée d'un dépôt Git

### 25.1. Objectif

Mettre en œuvre les techniques intermédiaires de Git sur un dépôt de laboratoire représentant un projet logiciel ou d'automatisation.

Le projet doit montrer que vous savez gérer l'historique, transférer une correction, diagnostiquer une régression et récupérer une référence après une erreur contrôlée.

### 25.2. Scénario

Vous maintenez un outil de supervision réseau.

Le dépôt contient :

- Une branche principale stable.
- Une branche de développement pour une fonctionnalité.
- Des commits intermédiaires nécessitant un nettoyage.
- Une correction urgente qui doit être transférée séparément.
- Un problème dont vous devez trouver le commit d'origine.

### 25.3. Travail demandé

1. Préparer un dépôt de laboratoire avec plusieurs commits.
2. Créer une branche de fonctionnalité et effectuer plusieurs changements indépendants.
3. Utiliser `git log --graph` pour expliquer l'historique.
4. Rebaser la branche de fonctionnalité sur la branche principale.
5. Réorganiser plusieurs commits avec `git rebase -i`.
6. Vérifier la série réécrite avec les commandes de comparaison appropriées.
7. Transférer une correction indépendante avec `git cherry-pick`.
8. Mettre de côté puis réappliquer un changement avec `git stash`.
9. Rechercher un état antérieur avec `git reflog` dans un exercice contrôlé.
10. Localiser une régression artificielle avec `git bisect`.
11. Créer un tag annoté pour identifier une version du projet.
12. Documenter les commandes utilisées et leurs conséquences.
13. Exécuter les tests après les modifications d'historique.

### 25.4. Livrables attendus

Le dépôt doit contenir :

- Un historique compréhensible.
- Des commits cohérents.
- Une branche de fonctionnalité intégrée.
- Une correction transférée avec cherry-pick ou une justification expliquant pourquoi une autre méthode serait préférable.
- Un tag annoté identifiant une version de test.
- Une documentation décrivant les procédures de rebasage et de récupération.
- Des tests permettant de vérifier le comportement de l'application.

### 25.5. Critères de validation

Le projet est réussi si vous pouvez démontrer que vous savez :

- Lire un graphe d'historique.
- Distinguer merge et rebase.
- Modifier l'historique local sans perdre les changements attendus.
- Comprendre la différence entre un commit original et un commit rejoué.
- Résoudre un conflit et poursuivre une opération.
- Transférer un commit précis.
- Retrouver une référence antérieure avec le reflog.
- Utiliser bisect pour localiser une régression reproductible.
- Expliquer les risques d'une mise à jour forcée.
- Vérifier la cohérence finale du dépôt.

## 26. Checklist opérationnelle pour les interventions sur un dépôt

Avant de réaliser une opération délicate :

```bash
git status
git branch --show-current
git log --oneline --graph --decorate --all
git diff
git diff --cached
```

Avant un rebasage :

```bash
git fetch origin
git status
git log --oneline --graph --decorate --all
```

Après un rebasage :

```bash
git status
git log --oneline --graph --decorate --all
```

Après une fusion :

```bash
git status
git diff
```

Après une résolution de conflit :

```bash
git status
git diff --check
```

Après une récupération :

```bash
git log --oneline --decorate -10
```

Après chaque transformation importante, exécutez également les tests et contrôles du projet.

`git diff --check` peut détecter certains problèmes de formatage dans les différences, notamment des espaces en fin de ligne. Il ne vérifie pas la logique du programme.

## 27. Glossaire

**Amend :** opération qui remplace le dernier commit par un nouveau commit, souvent pour corriger son contenu ou son message.

**Base de fusion :** commit commun utilisé comme référence pour comprendre la divergence de plusieurs historiques.

**Bisect :** outil qui aide à localiser le commit à l'origine d'un changement de comportement par recherche dichotomique.

**Cherry-pick :** opération qui applique le changement introduit par un commit sur la branche courante.

**Commit parent :** commit auquel un commit fait référence dans son historique.

**Detached HEAD :** état dans lequel `HEAD` désigne directement un commit plutôt qu'une branche suivie.

**Fast-forward :** mise à jour d'une référence vers un commit descendant sans créer de commit de fusion.

**Fetch :** récupération des informations et commits d'un dépôt distant sans intégration automatique à la branche courante.

**Fixup :** opération de rebasage interactif qui regroupe un commit avec le précédent en écartant normalement le message du commit regroupé.

**Force-with-lease :** option de push forcé qui vérifie que la référence distante correspond à l'état attendu avant sa mise à jour.

**Merge :** fusion des historiques de plusieurs branches.

**Rebase :** réapplication d'une série de changements sur une nouvelle base, généralement avec création de nouveaux commits.

**Rebase interactif :** mode de rebasage permettant notamment de réordonner, regrouper, modifier ou retirer des commits.

**Reflog :** journal local de mouvements des références, utile pour retrouver une position antérieure de `HEAD` ou d'une branche.

**Rerere :** fonctionnalité de Git qui peut mémoriser et réutiliser certaines résolutions de conflits.

**Reset :** commande qui déplace une référence et peut réinitialiser la zone de préparation ou le répertoire de travail selon son mode.

**Revert :** opération qui inverse un changement en créant un nouveau commit.

**Range-diff :** outil qui compare deux séries de commits afin de mieux comprendre leurs différences.

**Squash :** regroupement de plusieurs changements en un commit, par exemple lors d'un rebasage interactif.

**Stash :** mécanisme de mise de côté temporaire de modifications locales.

**Tag annoté :** référence de version associée à des métadonnées supplémentaires.

**Worktree :** répertoire de travail supplémentaire associé au même dépôt Git.

## 28. Références officielles pour approfondir

### Documentation Git

- Documentation officielle Git : https://git-scm.com/docs
- Manuel utilisateur de Git : https://git-scm.com/docs/user-manual
- Livre Pro Git en français : https://git-scm.com/book/fr/v2
- Git — Rebasage des branches : https://git-scm.com/book/en/v2/Git-Branching-Rebasing
- Git — Réécriture de l'historique : https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History
- Référence de `git rebase` : https://git-scm.com/docs/git-rebase
- Référence de `git merge` : https://git-scm.com/docs/git-merge
- Référence de `git cherry-pick` : https://git-scm.com/docs/git-cherry-pick
- Référence de `git stash` : https://git-scm.com/docs/git-stash
- Référence de `git reflog` : https://git-scm.com/docs/git-reflog
- Référence de `git bisect` : https://git-scm.com/docs/git-bisect
- Référence de `git worktree` : https://git-scm.com/docs/git-worktree
- Référence de `git range-diff` : https://git-scm.com/docs/git-range-diff
- Référence de `git add` : https://git-scm.com/docs/git-add
- Référence de `git push` : https://git-scm.com/docs/git-push
- Référence de `git tag` : https://git-scm.com/docs/git-tag

### Collaboration et sécurité

- GitHub Docs — À propos des pull requests : https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
- GitHub Docs — Protection des branches : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- GitHub Docs — Sécurité de GitHub Actions : https://docs.github.com/en/actions/how-tos/secure-your-work
- GitLab Docs — Dépôts de projet : https://docs.gitlab.com/user/project/repository/

Les documentations officielles restent la référence pour vérifier les options exactes et les comportements associés à la version de Git installée.

## 29. Synthèse du niveau intermédiaire

À ce niveau, Git n'est plus seulement un outil pour enregistrer des fichiers. Il devient un instrument de gestion et de diagnostic de l'historique.

Vous devez notamment savoir :

- Lire la structure du graphe des commits et comprendre le rôle de `HEAD`.
- Choisir entre merge et rebase selon la politique du projet.
- Réorganiser une série de commits locaux avec le rebasage interactif.
- Déplacer un changement indépendant avec cherry-pick.
- Mettre temporairement de côté des modifications avec stash.
- Retrouver une ancienne référence avec reflog.
- Localiser une régression avec bisect.
- Comprendre les références distantes, les relations de suivi et les conséquences d'un push forcé.
- Utiliser les worktrees et les outils de comparaison pour faciliter le travail quotidien.
- Protéger les secrets et ne pas traiter la réécriture de l'historique comme une opération anodine.

La règle la plus importante reste la suivante : **avant de manipuler l'historique, comprendre l'état du dépôt, savoir quels commits sont partagés et identifier ce qui doit être préservé**.

Un Git maîtrisé ne se mesure pas au nombre de commandes mémorisées, mais à la capacité de choisir l'opération adaptée, de prévoir ses conséquences et de vérifier que le résultat obtenu est correct.