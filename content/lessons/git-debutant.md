# Git et gestion de versions

## 1. Présentation du cours

Dans le développement logiciel, les fichiers évoluent constamment. Une application reçoit de nouvelles fonctionnalités, des corrections de bugs, des améliorations de sécurité et des changements de configuration. Sans méthode de suivi, il devient rapidement difficile de savoir ce qui a changé, quand le changement a été effectué, pourquoi il a été réalisé et comment revenir à une version précédente.

**Git est un système de gestion de versions distribué** qui permet d'enregistrer l'historique d'un projet, de suivre les modifications, de comparer différentes versions et de collaborer avec d'autres personnes.

Git est utilisé dans de nombreux domaines : développement logiciel, administration système, automatisation réseau, infrastructure as code, documentation technique, scripts, configuration de serveurs et projets DevOps.

La maîtrise de Git est une compétence fondamentale pour travailler avec des plateformes comme GitHub ou GitLab et pour comprendre les mécanismes d'intégration continue et de livraison continue (CI/CD).

Ce cours présente les notions essentielles, depuis l'installation jusqu'à la collaboration avec un dépôt distant. Chaque commande importante est accompagnée d'une explication et, lorsque cela est nécessaire, d'exemples d'utilisation.

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez être capable de :

- Expliquer le rôle de la gestion de versions.
- Distinguer Git de GitHub et de GitLab.
- Installer Git et configurer son identité.
- Créer un dépôt local.
- Comprendre le répertoire de travail, la zone de préparation et l'historique.
- Utiliser les commandes `git status`, `git add`, `git commit` et `git log`.
- Comparer les modifications avant de les enregistrer.
- Créer, utiliser et fusionner des branches.
- Comprendre et résoudre un conflit de fusion simple.
- Ignorer les fichiers temporaires avec `.gitignore`.
- Relier un dépôt local à un dépôt distant.
- Utiliser `git clone`, `git fetch`, `git pull` et `git push`.
- Corriger certaines erreurs courantes sans perdre inutilement son travail.
- Adopter de bonnes pratiques adaptées à une équipe technique.

### 1.2. Prérequis

Aucune connaissance préalable de Git n'est nécessaire.

Il est utile de savoir :

- Naviguer dans les dossiers d'un ordinateur.
- Créer et modifier des fichiers texte.
- Ouvrir un terminal.
- Exécuter une commande et lire le résultat affiché.

Les exemples fonctionneront principalement sous Linux, macOS, Windows PowerShell ou Git Bash, avec de légères adaptations possibles selon l'environnement.

### 1.3. Les outils utilisés

| Outil | Utilité |
|---|---|
| Git | Enregistrer et gérer les versions d'un projet. |
| Terminal | Exécuter les commandes Git. |
| Éditeur de texte ou IDE | Modifier les fichiers du projet. |
| GitHub ou GitLab | Héberger un dépôt distant et faciliter la collaboration. |

Un dépôt distant n'est pas obligatoire pour utiliser Git. Il est parfaitement possible de gérer l'historique d'un projet sur un seul ordinateur.

## 2. Pourquoi utiliser un système de gestion de versions ?

### 2.1. Le problème des copies manuelles

Imaginons que vous développiez un script Python destiné à surveiller des équipements réseau.

Votre répertoire contient un fichier `supervision.py`. Vous modifiez le script, vous ajoutez une fonctionnalité puis vous constatez que le programme ne fonctionne plus.

Sans système de gestion de versions, vous pourriez essayer de conserver plusieurs copies :

```text
projet/
|
+-- supervision.py
+-- supervision_final.py
+-- supervision_final_v2.py
+-- supervision_final_corrige.py
+-- supervision_final_corrige_bis.py
```

Cette méthode pose plusieurs problèmes :

- Il est difficile d'identifier la version réellement fonctionnelle.
- Les différences entre deux fichiers ne sont pas toujours évidentes.
- Les corrections peuvent être perdues.
- Plusieurs personnes risquent de modifier des copies différentes.
- Il n'existe pas d'historique fiable expliquant les changements.
- Le retour à une version antérieure devient une opération manuelle.

Le problème s'aggrave lorsque le projet contient des dizaines, des centaines ou des milliers de fichiers.

### 2.2. La solution apportée par Git

Git conserve un historique des versions d'un projet.

Au lieu de créer manuellement une copie pour chaque modification, vous enregistrez des points de l'historique appelés **commits**.

```text
Projet : supervision-reseau
             |
             v
        Commit A
        Version initiale
             |
             v
        Commit B
        Ajout du ping ICMP
             |
             v
        Commit C
        Ajout des alertes
             |
             v
        Commit D
        Correction des erreurs
```

Chaque commit possède un identifiant et conserve des informations permettant de retrouver l'état du projet correspondant à ce point de l'historique.

Vous pouvez consulter ces versions, comparer les changements et créer une nouvelle modification à partir d'une version antérieure.

### 2.3. Ce que Git permet de faire

Git permet notamment de :

- Suivre les modifications de fichiers.
- Enregistrer des versions successives.
- Comparer deux états du projet.
- Identifier les commits introduisant certaines modifications.
- Travailler sur plusieurs fonctionnalités en parallèle grâce aux branches.
- Fusionner des travaux distincts.
- Annuler certains changements.
- Synchroniser le travail avec d'autres dépôts.
- Collaborer avec plusieurs personnes.

Git ne remplace cependant pas tous les autres outils.

Il ne remplace pas un système de sauvegarde complet, une solution de gestion des secrets, un outil de suivi des tâches ou une plateforme CI/CD.

Il faut également retenir que Git n'enregistre pas automatiquement chaque frappe. Les modifications doivent être préparées et enregistrées dans l'historique par des commandes explicites.

## 3. Git, GitHub et GitLab : comprendre les différences

Ces noms sont souvent utilisés ensemble, mais ils ne désignent pas la même chose.

### 3.1. Git

Git est le programme qui assure la gestion des versions.

Il peut fonctionner localement, sans connexion Internet.

Exemple :

```bash
git init
git add fichier.txt
git commit -m "Ajout du fichier"
```

Ces commandes permettent de créer un dépôt et d'enregistrer une version sur l'ordinateur.

### 3.2. GitHub

GitHub est une plateforme qui héberge des dépôts Git et ajoute des fonctions de collaboration.

Elle propose notamment :

- Le stockage de dépôts distants.
- Les pull requests.
- Les revues de code.
- La gestion des problèmes.
- Les workflows GitHub Actions.
- Des mécanismes de protection des branches.
- Des fonctions de gestion de projet.

GitHub utilise Git, mais Git et GitHub restent deux éléments distincts.

### 3.3. GitLab

GitLab propose également l'hébergement de dépôts Git et des fonctions de collaboration.

Il comprend notamment :

- La gestion de dépôts.
- Les merge requests.
- Les pipelines GitLab CI/CD.
- Les registres de paquets et de conteneurs.
- Des fonctions de sécurité et de gestion de projet.

### 3.4. Schéma de fonctionnement

```text
                 ORDINATEUR LOCAL
              +--------------------+
              |                    |
              |  Fichiers du projet|
              |         |          |
              |         v          |
              |    Commandes Git   |
              |         |          |
              |         v          |
              |    Dépôt local     |
              |                    |
              +--------------------+
                        |
                        | push / fetch / pull
                        |
                        v
              +--------------------+
              |   DÉPÔT DISTANT    |
              |                    |
              |  GitHub ou GitLab  |
              |                    |
              +--------------------+
                        |
                        v
               Collaboration
               Revues de code
               Pipelines CI/CD
```

Git réalise les opérations de gestion des versions. La plateforme distante permet de partager le dépôt et de mettre en place des processus de collaboration.

### 3.5. Git est-il dépendant d'Internet ?

Non.

Les opérations suivantes fonctionnent normalement sans connexion à un serveur distant :

```bash
git init
git status
git add
git commit
git log
git diff
git branch
git switch
```

Les opérations qui échangent des données avec un serveur distant nécessitent généralement un accès réseau :

```bash
git fetch
git pull
git push
git clone
```

L'exception pratique est qu'un dépôt peut également être accessible par un chemin local ou par certains mécanismes réseau privés. Le mot « distant » signifie ici un dépôt distinct, pas nécessairement un serveur situé sur Internet.

## 4. Installer Git

Avant de manipuler un dépôt, vérifiez si Git est déjà installé.

### 4.1. Vérifier l'installation

Dans un terminal :

```bash
git --version
```

Exemple de résultat :

```text
git version 2.5x.x
```

Le numéro exact dépend de la version installée.

Si une version de Git est affichée, la commande est disponible.

Si le terminal indique que la commande est inconnue, Git doit être installé ou son emplacement doit être ajouté au chemin d'exécution du système.

### 4.2. Installation sous Windows

Téléchargez Git depuis son site officiel :

https://git-scm.com/downloads/win

L'installation fournit généralement Git Bash, un terminal permettant d'utiliser Git avec un ensemble de commandes de type Unix.

Vous pouvez également exécuter de nombreuses commandes Git dans Windows PowerShell ou le terminal de Visual Studio Code.

Après l'installation, vérifiez :

```powershell
git --version
```

### 4.3. Installation sous Ubuntu ou Debian

Dans un terminal :

```bash
sudo apt update
sudo apt install git
```

Puis vérifiez :

```bash
git --version
```

### 4.4. Installation sous Fedora

```bash
sudo dnf install git
```

Puis :

```bash
git --version
```

### 4.5. Installation sous macOS

Si Homebrew est déjà installé :

```bash
brew install git
```

Puis :

```bash
git --version
```

macOS peut également proposer les outils de ligne de commande d'Apple. La méthode précise dépend de la configuration de la machine.

### 4.6. Règle importante

Les commandes d'installation dépendent du système d'exploitation. Ne copiez pas une commande Linux dans PowerShell si elle n'est pas adaptée à cet environnement.

En revanche, la majorité des commandes Git utilisées dans ce cours restent identiques.

## 5. Configurer Git pour la première utilisation

### 5.1. Configurer le nom et l'adresse électronique

Git peut enregistrer un nom et une adresse électronique comme informations d'auteur dans les commits.

Configurer le nom :

```bash
git config --global user.name "Votre Nom"
```

Configurer l'adresse électronique :

```bash
git config --global user.email "votre.adresse@example.com"
```

Remplacez ces valeurs par les informations adaptées à votre contexte.

L'option `--global` applique ces paramètres aux dépôts de l'utilisateur courant.

Ces informations ne sont pas des identifiants de connexion. Elles servent principalement à attribuer les commits à un auteur.

**Attention :** les informations d'auteur peuvent être visibles par les personnes qui ont accès au dépôt. Pour un projet professionnel, utilisez l'identité appropriée et respectez les règles de votre organisation.

### 5.2. Vérifier la configuration

Afficher toute la configuration visible :

```bash
git config --list
```

Afficher uniquement le nom configuré :

```bash
git config user.name
```

Afficher uniquement l'adresse électronique :

```bash
git config user.email
```

Pour afficher l'origine d'un paramètre lorsqu'elle est prise en charge par la version de Git :

```bash
git config --show-origin --get user.name
```

### 5.3. Configurer le nom de la branche initiale

Sur les versions de Git qui prennent en charge ce réglage :

```bash
git config --global init.defaultBranch main
```

Cette commande définit `main` comme nom de branche initiale pour les nouveaux dépôts créés avec `git init`.

Elle ne renomme pas automatiquement les branches des dépôts déjà existants.

### 5.4. La notion de portée de configuration

Git peut lire des paramètres définis à plusieurs niveaux.

| Portée | Commande d'exemple | Utilisation |
|---|---|---|
| Dépôt local | `git config user.name "Nom"` | Appliquer un paramètre au dépôt courant. |
| Utilisateur | `git config --global user.name "Nom"` | Appliquer un paramètre à l'utilisateur courant. |
| Système | `git config --system ...` | Configurer Git pour plusieurs utilisateurs d'un système, avec les droits nécessaires. |

Un paramètre local peut remplacer la valeur globale correspondante dans le dépôt concerné.

Cette possibilité est utile lorsqu'une même machine est utilisée pour des projets personnels et professionnels.

## 6. Comprendre la structure d'un dépôt Git

### 6.1. Qu'est-ce qu'un dépôt ?

Un dépôt Git, ou *repository*, contient les informations nécessaires pour suivre l'historique d'un projet.

Un dépôt comprend généralement :

- Les fichiers de travail du projet.
- Un répertoire interne `.git` qui conserve l'historique et les métadonnées Git.
- Une configuration locale du dépôt.

Exemple :

```text
mon-projet/
|
+-- app.py
+-- README.md
+-- config.example.yml
+-- .gitignore
|
+-- .git/
    |
    +-- objects/
    +-- refs/
    +-- HEAD
    +-- config
```

Le contenu exact de `.git` dépend de la version de Git et de la configuration du dépôt.

Il ne faut généralement pas modifier manuellement les fichiers internes de `.git`.

### 6.2. Le répertoire de travail

Le répertoire de travail contient les fichiers que vous consultez et modifiez.

Exemple :

```text
app.py
README.md
tests/test_app.py
```

Lorsque vous ouvrez `app.py` dans un éditeur et que vous modifiez son contenu, la modification se trouve dans le répertoire de travail.

Elle n'est pas automatiquement enregistrée dans l'historique Git.

### 6.3. La zone de préparation

La zone de préparation, appelée *staging area* ou *index*, contient les modifications sélectionnées pour le prochain commit.

On y ajoute les changements avec :

```bash
git add app.py
```

La zone de préparation permet de choisir précisément ce qui sera enregistré dans le prochain commit.

Vous pouvez modifier trois fichiers, mais décider de n'en enregistrer que deux dans le commit courant.

### 6.4. L'historique des commits

Le dépôt contient les commits déjà enregistrés.

Un commit représente un état du projet et les informations associées à cet enregistrement.

La commande suivante permet de consulter cet historique :

```bash
git log
```

### 6.5. Le modèle mental essentiel

Le fonctionnement de Git devient plus simple à comprendre si vous distinguez trois zones.

```text
+------------------------+
|  1. RÉPERTOIRE DE       |
|     TRAVAIL             |
|                        |
|  Modifications locales |
+------------------------+
             |
             | git add
             v
+------------------------+
|  2. ZONE DE            |
|     PRÉPARATION        |
|                        |
|  Changements choisis   |
|  pour le prochain      |
|  commit                |
+------------------------+
             |
             | git commit
             v
+------------------------+
|  3. HISTORIQUE GIT     |
|                        |
|  Commits enregistrés   |
+------------------------+
```

Les commandes correspondantes sont :

| Commande | Rôle |
|---|---|
| `git status` | Observer l'état du dépôt. |
| `git add` | Préparer des modifications. |
| `git commit` | Enregistrer les modifications préparées dans l'historique. |

Cette distinction est fondamentale. Beaucoup d'erreurs de débutant proviennent de la confusion entre une modification présente dans un fichier, une modification préparée et une modification déjà enregistrée dans un commit.

## 7. Créer son premier dépôt local

### 7.1. Créer un répertoire

Sous Linux ou macOS :

```bash
mkdir git-premier-projet
cd git-premier-projet
```

Sous PowerShell :

```powershell
New-Item -ItemType Directory -Name git-premier-projet
Set-Location git-premier-projet
```

Vous êtes maintenant dans le répertoire du projet.

### 7.2. Initialiser Git

Exécutez :

```bash
git init
```

Git initialise un dépôt dans le répertoire courant.

Un message indique normalement que le dépôt a été créé.

Si la branche initiale porte un autre nom que `main`, cela dépend notamment de la configuration de Git.

### 7.3. Créer un fichier

Créez un fichier `README.md` contenant :

```markdown
# Mon premier projet Git

Ce projet sert à apprendre la gestion de versions.

Objectifs :
- Créer un dépôt.
- Suivre les modifications.
- Enregistrer des commits.
```

Vous pouvez créer ce fichier avec un éditeur de texte.

Sous un terminal compatible avec les commandes Unix, vous pouvez également utiliser :

```bash
cat > README.md <<'EOF'
# Mon premier projet Git

Ce projet sert à apprendre la gestion de versions.

Objectifs :
- Créer un dépôt.
- Suivre les modifications.
- Enregistrer des commits.
EOF
```

Cette dernière méthode dépend du shell et n'est pas directement utilisable telle quelle dans toutes les versions de PowerShell.

### 7.4. Vérifier l'état du dépôt

```bash
git status
```

Git indique que `README.md` est un fichier non suivi, généralement désigné comme *untracked*.

Cela signifie que Git connaît le dépôt, mais que ce fichier n'a pas encore été ajouté à l'historique ni préparé pour un commit.

### 7.5. Préparer le fichier

```bash
git add README.md
```

Cette commande ajoute le fichier à la zone de préparation.

Vérifiez ensuite :

```bash
git status
```

Git doit maintenant indiquer que le fichier est prêt à être enregistré.

### 7.6. Créer le premier commit

```bash
git commit -m "Initialisation du projet"
```

Le commit enregistre l'état du fichier préparé.

Le message `Initialisation du projet` décrit l'objectif de ce changement.

Si Git signale que le nom ou l'adresse électronique n'est pas configuré, revenez à la section consacrée à la configuration initiale.

### 7.7. Vérifier le résultat

```bash
git log --oneline
```

Vous devriez voir le commit que vous venez de créer.

Le résultat ressemble à ceci :

```text
a1b2c3d Initialisation du projet
```

L'identifiant affiché n'est qu'un exemple ; celui obtenu sur votre machine sera différent.

### 7.8. Le cycle complet

```text
Créer un dossier
       |
       v
     git init
       |
       v
Créer ou modifier un fichier
       |
       v
    git status
       |
       v
   git add fichier
       |
       v
 git commit -m "Message"
       |
       v
    git log
```

Vous venez de réaliser un cycle Git élémentaire.

## 8. Comprendre les états des fichiers

Git distingue plusieurs états utiles pour comprendre ce qui se passe dans le dépôt.

### 8.1. Fichier non suivi

Un fichier non suivi existe dans le répertoire de travail, mais Git ne le suit pas encore.

Exemple :

```text
README.md
app.py
```

Si seul `README.md` a été enregistré dans l'historique et que vous venez de créer `app.py`, le nouveau fichier peut apparaître comme non suivi.

Pour le préparer :

```bash
git add app.py
```

### 8.2. Fichier modifié

Un fichier suivi est dit modifié lorsque son contenu dans le répertoire de travail diffère de la version de référence considérée par Git.

Exemple : vous ajoutez une ligne à `README.md`.

```bash
git status
```

Git indique alors que le fichier a été modifié.

Tant que vous n'avez pas préparé la modification, le contenu modifié n'est pas inclus dans le prochain commit.

### 8.3. Fichier préparé

Après :

```bash
git add README.md
```

les modifications sélectionnées sont placées dans la zone de préparation.

Vous pouvez maintenant les examiner avec :

```bash
git diff --cached
```

Cette commande affiche les différences préparées pour le prochain commit.

### 8.4. Fichier enregistré

Après :

```bash
git commit -m "Mise à jour de la documentation"
```

les modifications préparées sont enregistrées dans l'historique du dépôt.

Elles peuvent ensuite être consultées avec `git log` et comparées à d'autres versions.

### 8.5. Tableau récapitulatif

| État | Signification | Action courante |
|---|---|---|
| Non suivi | Nouveau fichier non encore suivi. | `git add fichier` |
| Modifié | Un fichier suivi a changé dans le répertoire de travail. | `git diff`, puis `git add` |
| Préparé | Les changements sélectionnés attendent un commit. | `git diff --cached`, puis `git commit` |
| Enregistré | Les changements font partie de l'historique. | `git log`, `git show` |

Ces états ne sont pas nécessairement exclusifs au niveau d'un même fichier : vous pouvez préparer une modification puis modifier à nouveau le fichier. La version préparée et la version courante peuvent alors différer.

### 8.6. Exemple de changement préparé puis modifié

Supposons qu'un fichier contienne :

```text
Version A
```

Vous le modifiez en :

```text
Version B
```

Puis vous exécutez :

```bash
git add fichier.txt
```

La version B est préparée.

Si vous changez ensuite le fichier pour obtenir :

```text
Version C
```

alors la version B reste dans la zone de préparation tandis que la version C existe dans le répertoire de travail.

Le prochain commit n'enregistrera pas automatiquement toutes les modifications ultérieures. Il enregistrera ce qui est dans la zone de préparation au moment du commit.

Cette particularité explique pourquoi il est important de vérifier l'état du dépôt avant de créer un commit.

## 9. Les commandes essentielles de Git

### 9.1. `git status`

Affiche l'état actuel du dépôt.

```bash
git status
```

Utilisez cette commande régulièrement, notamment :

- Après avoir modifié des fichiers.
- Avant de préparer des changements.
- Après `git add`.
- Avant `git commit`.
- Après une fusion.
- Lorsqu'une commande produit un résultat inattendu.

Pour un débutant, `git status` est la commande de diagnostic à privilégier.

### 9.2. `git add`

Ajoute des changements à la zone de préparation.

Pour un fichier :

```bash
git add README.md
```

Pour plusieurs fichiers :

```bash
git add app.py tests/test_app.py
```

Pour préparer toutes les modifications pertinentes du répertoire courant :

```bash
git add .
```

La dernière commande peut inclure de nombreux changements. Avant de l'utiliser, vérifiez ce que contient le répertoire et contrôlez les fichiers qui seront suivis.

`git add` ne crée pas de commit.

### 9.3. `git commit`

Enregistre dans l'historique les changements préparés.

```bash
git commit -m "Ajout de la fonction de calcul"
```

Un commit devrait idéalement représenter un changement cohérent.

Un message comme `correction` est moins informatif qu'un message comme :

```bash
git commit -m "Correction du calcul du montant total"
```

Il est préférable d'éviter de regrouper des changements sans rapport dans un même commit lorsque cela complique la revue ou le diagnostic.

### 9.4. `git log`

Affiche l'historique des commits.

```bash
git log
```

Pour afficher un historique compact :

```bash
git log --oneline
```

Pour visualiser les branches et leurs relations :

```bash
git log --oneline --graph --decorate --all
```

Cette dernière commande est particulièrement utile lorsque le projet utilise plusieurs branches.

### 9.5. `git diff`

Affiche les différences entre certains états du projet.

Pour examiner les modifications non préparées :

```bash
git diff
```

Pour examiner les modifications préparées :

```bash
git diff --cached
```

Pour comparer le répertoire de travail avec le dernier commit de la branche courante :

```bash
git diff HEAD
```

Cela permet de vérifier le contenu d'un changement avant de l'enregistrer.

### 9.6. `git show`

Affiche les informations d'un objet Git, notamment un commit.

```bash
git show
```

Pour examiner un commit précis :

```bash
git show IDENTIFIANT_DU_COMMIT
```

Remplacez le texte d'exemple par l'identifiant réel du commit.

### 9.7. `git rm`

Supprime un fichier suivi du répertoire de travail et prépare cette suppression pour le prochain commit.

```bash
git rm ancien-fichier.txt
```

La suppression ne devient définitive dans l'historique qu'après le commit correspondant.

Pour arrêter de suivre un fichier tout en le conservant localement :

```bash
git rm --cached fichier.txt
```

Cette dernière commande est utile lorsqu'un fichier ne devrait plus être suivi, mais elle n'efface pas les anciennes copies du fichier dans l'historique.

### 9.8. `git mv`

Renomme ou déplace un fichier en préparant le changement dans Git.

```bash
git mv ancien_nom.txt nouveau_nom.txt
```

Git détermine souvent les renommages en comparant les contenus, même si son historique interne ne conserve pas nécessairement un événement de renommage distinct.

### 9.9. Tableau des commandes principales

| Commande | Utilité |
|---|---|
| `git init` | Créer un dépôt Git dans le répertoire courant. |
| `git status` | Examiner l'état du dépôt. |
| `git add` | Préparer les changements. |
| `git commit` | Enregistrer les changements préparés. |
| `git log` | Consulter l'historique. |
| `git diff` | Comparer les modifications. |
| `git show` | Examiner un commit ou un objet Git. |
| `git rm` | Supprimer un fichier suivi ou cesser de le suivre. |
| `git mv` | Renommer ou déplacer un fichier en préparant le changement. |
| `git help` | Accéder à l'aide Git. |

## 10. Maîtriser les messages de commit

### 10.1. Pourquoi le message est-il important ?

Un commit enregistre un changement technique, mais son message explique ce changement aux personnes qui liront l'historique.

Un bon message aide à comprendre :

- Ce qui a été modifié.
- Pourquoi le changement a été réalisé.
- Quelle partie du projet est concernée.

Les messages de commit sont particulièrement utiles lorsqu'une anomalie est découverte plusieurs semaines après la modification initiale.

### 10.2. Exemples de messages

Messages peu informatifs :

```text
modif
correction
test
version finale
changement important
```

Messages plus explicites :

```text
Ajout de la vérification de connectivité
Correction du calcul du total de commande
Mise à jour de la documentation d'installation
Ajout des tests de validation des adresses IP
```

### 10.3. Une règle pratique

Le message devrait décrire l'intention du changement avec des mots suffisamment précis.

Exemple :

```bash
git commit -m "Ajout de la validation des adresses IP"
```

Pour un changement important, le message peut être accompagné d'une description détaillée. Git permet notamment d'ouvrir un éditeur pour rédiger un message plus long.

```bash
git commit
```

L'éditeur configuré pour Git s'ouvre alors normalement pour saisir le message.

### 10.4. Limiter la taille des commits

Un commit qui modifie simultanément la documentation, la configuration réseau, les tests et le système d'authentification peut être difficile à comprendre.

Il est souvent préférable de séparer les changements indépendants.

Exemple :

```text
Commit 1 : ajout de la fonction de connexion
Commit 2 : ajout des tests de connexion
Commit 3 : mise à jour de la documentation
```

Cette organisation facilite l'analyse, la revue et les éventuelles corrections.

Elle ne signifie pas qu'un commit doit toujours modifier un seul fichier. Le critère principal est la cohérence du changement.

## 11. Utiliser `.gitignore`

### 11.1. Pourquoi ignorer certains fichiers ?

Un projet peut produire de nombreux fichiers qui n'ont pas vocation à être suivis par Git :

- Fichiers temporaires.
- Journaux d'exécution.
- Fichiers compilés.
- Répertoires générés par un éditeur.
- Environnements virtuels.
- Fichiers de configuration contenant des secrets.
- Résultats de tests reproductibles.

Le fichier `.gitignore` définit les motifs que Git doit ignorer pour les fichiers non suivis.

Il permet notamment d'éviter de polluer le dépôt avec des fichiers générés localement.

### 11.2. Exemple de `.gitignore` pour un projet Python

À la racine du projet, créez un fichier nommé exactement `.gitignore` :

```gitignore
# Fichiers temporaires Python
__pycache__/
*.py[cod]

# Environnements virtuels Python
.venv/
venv/

# Rapports et caches de tests
.pytest_cache/
.coverage
htmlcov/

# Fichiers journaux
*.log
logs/

# Configuration locale et secrets
.env
.env.*
!.env.example

# Paramètres d'éditeurs courants
.vscode/
.idea/

# Fichiers système
.DS_Store
Thumbs.db
```

Cette configuration est un exemple de départ, pas une règle universelle.

Dans une équipe, adaptez le fichier aux technologies utilisées. Certains fichiers de configuration d'éditeur peuvent être utiles et doivent éventuellement être suivis par le dépôt.

La règle `!.env.example` permet de conserver un fichier d'exemple non secret même si le motif précédent ignore les fichiers correspondants.

Un fichier `.env.example` ne doit cependant pas contenir de véritable mot de passe, jeton ou clé privée.

### 11.3. Ajouter `.gitignore` au dépôt

Une fois le fichier créé :

```bash
git add .gitignore
git commit -m "Ajout des règles de fichiers ignorés"
```

Les règles sont partagées avec les autres personnes qui récupèrent le dépôt.

### 11.4. Attention : `.gitignore` ne retire pas un fichier déjà suivi

Supposons que `secret.env` ait déjà été ajouté au dépôt et enregistré dans un commit.

L'ajout de cette ligne à `.gitignore` :

```gitignore
secret.env
```

n'arrête pas automatiquement le suivi du fichier.

Si le fichier doit rester présent sur votre ordinateur mais ne plus être suivi, vous pouvez utiliser :

```bash
git rm --cached secret.env
git add .gitignore
git commit -m "Arrêt du suivi du fichier local sensible"
```

Cela ne supprime pas les anciennes versions du fichier dans l'historique Git.

Si un secret a déjà été exposé, il faut le révoquer ou le renouveler, examiner les conséquences possibles et traiter l'historique conformément à la procédure de l'organisation.

### 11.5. Vérifier si un fichier est ignoré

Exemple :

```bash
git check-ignore -v .env
```

Git peut afficher la règle qui provoque l'ignorance du fichier.

Cette commande est utile pour comprendre pourquoi un fichier apparaît ou n'apparaît pas dans les changements à préparer.

### 11.6. Ce qu'il ne faut généralement pas ignorer

N'ignorez pas les fichiers nécessaires à la reproduction ou à la compréhension du projet sans raison valable.

Selon le projet, il peut notamment être important de suivre :

- Les fichiers source.
- Les tests.
- La documentation.
- Les fichiers de dépendances.
- Les fichiers de configuration non sensibles.
- Les définitions de construction.
- Les scripts d'installation et de déploiement.

L'objectif est de conserver un projet cohérent, pas de cacher les modifications à Git.

## 12. Comprendre les branches

### 12.1. Qu'est-ce qu'une branche ?

Une branche est un nom qui référence un commit dans l'historique Git.

Les branches permettent de développer plusieurs changements en parallèle sans devoir modifier immédiatement la branche principale.

Exemple :

```text
A---B---C---D       main
         \
          E---F     feature-alertes
```

Dans cette représentation :

- `main` désigne la branche principale.
- `feature-alertes` désigne une branche de travail.
- Les commits E et F appartiennent à l'historique de la branche de fonctionnalité.

Cette vue est volontairement simplifiée.

Les branches Git ne sont pas des copies complètes et indépendantes de tous les fichiers du projet. Elles sont des références légères qui permettent de se déplacer dans l'historique et de construire des développements distincts.

### 12.2. Pourquoi travailler avec des branches ?

Imaginons que l'application en production fonctionne correctement, mais qu'une nouvelle fonctionnalité soit en cours de développement.

Modifier directement la branche principale peut rendre plus difficile la séparation entre le code stable et le travail en cours.

Une branche permet de réaliser le changement indépendamment, de le tester puis de le fusionner lorsqu'il est prêt.

Cas d'utilisation :

- Développer une nouvelle fonctionnalité.
- Corriger un bug.
- Tester une modification expérimentale.
- Préparer une version.
- Séparer plusieurs travaux d'équipe.

### 12.3. Afficher les branches

Lister les branches locales :

```bash
git branch
```

Afficher les branches locales et distantes connues :

```bash
git branch -a
```

La branche courante est généralement précédée d'un astérisque.

Exemple :

```text
* main
  feature-alertes
```

### 12.4. Créer une branche

Pour créer une branche sans s'y déplacer :

```bash
git branch feature-alertes
```

Pour créer une branche et s'y déplacer immédiatement :

```bash
git switch -c feature-alertes
```

La deuxième méthode est souvent la plus pratique pour commencer un nouveau travail.

### 12.5. Changer de branche

```bash
git switch main
```

Cette commande sélectionne la branche `main`.

Pour passer sur une branche existante :

```bash
git switch feature-alertes
```

Avant de changer de branche, vérifiez l'état du dépôt :

```bash
git status
```

Git peut empêcher un changement si des modifications locales risquent d'être écrasées. Il ne faut pas chercher à contourner cette protection sans comprendre les changements concernés.

### 12.6. Ancienne commande : `git checkout`

On rencontre fréquemment cette commande dans les tutoriels :

```bash
git checkout feature-alertes
```

Elle permet aussi de changer de branche, mais elle a plusieurs usages.

Pour les opérations élémentaires de branche et de restauration de fichiers, les commandes modernes `git switch` et `git restore` sont souvent plus explicites.

Il reste néanmoins utile de savoir lire `git checkout` dans des documents existants.

### 12.7. Bonnes pratiques de nommage

Utilisez des noms courts et descriptifs.

Exemples :

```text
feature/export-csv
feature/alertes-email
fix/timeout-api
fix/validation-ip
docs/guide-installation
```

Les conventions exactes dépendent de l'organisation.

Le nom d'une branche devrait aider à comprendre le sujet du travail.

## 13. Fusionner des branches

### 13.1. Pourquoi fusionner ?

Lorsqu'un travail réalisé sur une branche est terminé, il doit généralement être intégré dans la branche cible.

L'opération de fusion s'appelle un **merge**.

Exemple :

```text
A---B---C             main
         \
          D---E       feature-alertes
```

Après une fusion simple, l'historique peut ressembler à ceci :

```text
A---B---C-------------M    main
         \           /
          D---------E      feature-alertes
```

Le commit M représente le commit de fusion dans cet exemple.

Git peut aussi réaliser une fusion sans créer de commit de fusion distinct lorsqu'il peut simplement avancer la référence de la branche cible. Ce mécanisme est appelé *fast-forward*.

### 13.2. Procédure complète

Supposons que la branche `feature-alertes` contienne une fonctionnalité terminée.

Commencez par vérifier la situation :

```bash
git status
git branch
```

Passez sur la branche cible :

```bash
git switch main
```

Fusionnez la branche de travail :

```bash
git merge feature-alertes
```

Si Git peut fusionner les changements sans conflit, il termine l'opération.

Vérifiez ensuite :

```bash
git status
git log --oneline --graph --decorate --all
```

### 13.3. Schéma du cycle de branche

```text
                  main
                   |
                   v
           Créer une branche
                   |
                   v
            feature-alertes
                   |
                   v
           Modifier les fichiers
                   |
                   v
             git add ...
                   |
                   v
            git commit ...
                   |
                   v
          Vérifier et tester
                   |
                   v
             Revenir sur main
                   |
                   v
         git merge feature-alertes
                   |
                   v
          Branche intégrée à main
```

### 13.4. Supprimer une branche terminée

Après une fusion réussie, vous pouvez supprimer la branche locale si elle n'est plus nécessaire :

```bash
git branch -d feature-alertes
```

Git refuse normalement de supprimer avec `-d` une branche contenant des commits qui n'ont pas été intégrés dans l'historique connu de la branche courante.

Il est préférable de comprendre le motif du refus plutôt que d'utiliser systématiquement une option plus agressive.

### 13.5. Une fusion ne doit pas être automatique sans vérification

Avant de fusionner une branche importante :

- Vérifiez les changements.
- Exécutez les tests disponibles.
- Examinez les modifications du code.
- Confirmez que le travail est prêt à être intégré.
- Vérifiez les règles de l'équipe.

Dans un contexte professionnel, la fusion peut passer par une pull request ou une merge request. Cette étape permet d'organiser la revue du code et les contrôles automatiques avant l'intégration.

## 14. Comprendre et résoudre un conflit de fusion

### 14.1. Qu'est-ce qu'un conflit ?

Git sait fusionner de nombreuses modifications automatiquement.

Un conflit survient lorsque Git ne peut pas déterminer de manière sûre comment réunir certains changements.

Cela peut arriver lorsque deux branches modifient les mêmes lignes d'un fichier de façons incompatibles.

Un conflit n'est pas nécessairement une erreur dans le logiciel. Il signale que les changements doivent être examinés par une personne.

### 14.2. Exemple de situation

La branche `main` contient :

```python
message = "Bienvenue"
```

La branche `feature-message` modifie la même ligne :

```python
message = "Bienvenue dans l'application"
```

Dans le même temps, un autre changement sur `main` produit :

```python
message = "Bienvenue sur le portail"
```

Lors de la fusion, Git ne sait pas quelle formulation doit être conservée.

### 14.3. À quoi ressemble un conflit ?

Git peut insérer des marqueurs dans le fichier :

```python
<<<<<<< HEAD
message = "Bienvenue sur le portail"
=======
message = "Bienvenue dans l'application"
>>>>>>> feature-message
```

Ces marqueurs délimitent les deux versions en conflit.

Dans un merge classique :

- `<<<<<<< HEAD` introduit la version de la branche courante.
- `=======` sépare les deux versions.
- `>>>>>>> feature-message` identifie l'autre branche à l'origine de ce changement.

Le contenu exact dépend des branches et du type d'opération en cours.

### 14.4. Résoudre le conflit

Il faut examiner le contexte et choisir le contenu qui correspond au comportement voulu.

Par exemple :

```python
message = "Bienvenue dans l'application"
```

Le fichier doit ensuite être enregistré sans les marqueurs de conflit.

Si une combinaison des deux versions est nécessaire, vous pouvez aussi écrire une troisième formulation.

### 14.5. Terminer la fusion

Après avoir résolu le conflit :

```bash
git status
```

Vérifiez quels fichiers restent concernés.

Préparez le fichier résolu :

```bash
git add fichier_en_conflit.py
```

Puis, si une fusion est en cours :

```bash
git commit
```

Git peut ouvrir un éditeur avec un message de commit de fusion proposé.

Dans les configurations habituelles, `git merge` peut avoir terminé automatiquement la fusion sans conflit. Dans ce cas, il n'y a pas nécessairement de commit supplémentaire à créer.

Exécutez les tests après la résolution : le fait de supprimer les marqueurs ne prouve pas que le résultat est fonctionnel.

### 14.6. Annuler une fusion en cours

Si la fusion n'est pas terminée et que vous souhaitez revenir à l'état précédent, Git permet généralement :

```bash
git merge --abort
```

Utilisez cette commande uniquement lorsqu'une fusion est effectivement en cours et après avoir compris les modifications locales présentes.

Comme pour toute opération de récupération, vérifiez votre état de travail avant et après.

### 14.7. Exemple de procédure de résolution

```text
git merge feature-alertes
          |
          v
   Conflit détecté
          |
          v
   git status
          |
          v
  Ouvrir le fichier concerné
          |
          v
 Examiner les deux versions
          |
          v
 Choisir ou combiner le contenu
          |
          v
 Supprimer les marqueurs
          |
          v
    git add fichier
          |
          v
    git commit
          |
          v
 Exécuter les tests
```

### 14.8. Les précautions à prendre

Ne choisissez pas automatiquement la version la plus longue, la plus récente ou la plus familière.

Les deux versions peuvent contenir des changements importants.

Si le conflit concerne une configuration réseau, une politique de sécurité ou un fichier de production, vérifiez les conséquences techniques avant de choisir le contenu final.

## 15. Annuler ou corriger des modifications

Les erreurs font partie de l'apprentissage. Il est important de savoir distinguer les commandes qui modifient les fichiers, celles qui modifient la zone de préparation et celles qui interviennent sur l'historique.

Certaines opérations peuvent faire perdre des changements. Commencez par examiner l'état du dépôt :

```bash
git status
git diff
git diff --cached
```

### 15.1. Retirer un fichier de la zone de préparation

Vous avez préparé un fichier, mais vous ne voulez pas l'inclure dans le prochain commit.

```bash
git restore --staged fichier.txt
```

Cette commande retire les changements du fichier de la zone de préparation, sans supprimer les modifications du répertoire de travail.

Exemple :

```bash
git add README.md
git restore --staged README.md
```

Le fichier reste modifié localement, mais la modification n'est plus préparée.

### 15.2. Abandonner les modifications locales d'un fichier

Pour restaurer un fichier à partir de l'état de référence de la branche courante :

```bash
git restore fichier.txt
```

**Attention : cette commande peut remplacer les modifications non préparées du fichier.** Les changements concernés risquent alors d'être perdus.

Avant de l'utiliser :

```bash
git diff -- fichier.txt
```

Si vous souhaitez conserver le travail, faites une copie ou enregistrez-le dans un endroit sûr avant de restaurer le fichier.

### 15.3. Retirer certains fichiers préparés

Pour retirer un seul fichier de la zone de préparation :

```bash
git restore --staged fichier.txt
```

Pour retirer tous les changements de la zone de préparation :

```bash
git restore --staged .
```

Cette dernière commande ne supprime normalement pas les modifications du répertoire de travail. Elle retire les changements préparés.

Contrôlez ensuite :

```bash
git status
```

### 15.4. Corriger le dernier commit

Supposons que vous ayez créé un commit, puis découvert qu'un fichier aurait dû y être ajouté.

Si le commit n'a pas été partagé et que vous êtes sûr de vouloir le modifier, vous pouvez préparer le fichier oublié :

```bash
git add fichier-oublie.txt
```

Puis corriger le dernier commit :

```bash
git commit --amend
```

Git ouvre généralement un éditeur pour confirmer ou modifier le message.

`git commit --amend` remplace le dernier commit par un nouveau commit. L'identifiant change.

Cette opération doit être utilisée avec prudence si le commit a déjà été partagé avec d'autres personnes, car elle modifie l'historique.

### 15.5. Annuler un commit partagé sans réécrire l'historique

Lorsqu'un commit a déjà été publié et que son effet doit être annulé, `git revert` est souvent plus approprié.

```bash
git revert IDENTIFIANT_DU_COMMIT
```

Cette commande crée un nouveau commit qui inverse les modifications du commit ciblé.

L'historique conserve donc le commit original et le commit d'annulation.

Vous devrez remplacer `IDENTIFIANT_DU_COMMIT` par l'identifiant réel.

Si l'opération inverse un commit complexe ou une fusion, l'analyse préalable est importante.

### 15.6. Comprendre `git reset` sans prendre de risques

Vous rencontrerez également ces commandes :

```bash
git reset
git reset --soft
git reset --mixed
git reset --hard
```

Elles n'ont pas exactement le même effet.

En particulier :

- `--soft` déplace la référence de branche tout en conservant la zone de préparation et le répertoire de travail.
- `--mixed`, mode par défaut de `reset`, déplace la référence et réinitialise la zone de préparation, mais conserve normalement les modifications dans le répertoire de travail.
- `--hard` déplace la référence et remplace la zone de préparation ainsi que le répertoire de travail. Des modifications peuvent être perdues.

**Évitez `git reset --hard` tant que vous ne maîtrisez pas les conséquences de cette opération.** Il ne s'agit pas d'une commande ordinaire de correction de fichiers.

En cas de doute, commencez par :

```bash
git status
git log --oneline --decorate -5
git diff
git diff --cached
```

### 15.7. Comparaison des méthodes d'annulation

| Besoin | Commande généralement adaptée |
|---|---|
| Retirer un fichier de la zone de préparation | `git restore --staged fichier` |
| Abandonner une modification locale non préparée | `git restore fichier`, avec précaution |
| Modifier le dernier commit local | `git commit --amend` |
| Annuler un commit publié sans supprimer son historique | `git revert` |
| Déplacer une branche et réinitialiser l'état du travail | `git reset`, après étude de ses effets |

Il faut choisir une commande selon l'état du dépôt et le résultat recherché, pas selon une liste de commandes mémorisées.

## 16. Les dépôts distants

### 16.1. Qu'est-ce qu'un dépôt distant ?

Un dépôt distant est un autre dépôt Git avec lequel votre dépôt local peut échanger des données.

Il peut être hébergé sur GitHub, GitLab, un serveur privé ou un autre emplacement accessible.

Le dépôt distant permet de partager le code et l'historique entre plusieurs environnements.

### 16.2. Local et distant

```text
ORDINATEUR A                   SERVEUR DISTANT

Fichiers                       Dépôt distant
   |                                ^
   v                                |
Dépôt local -------- push ---------+
   |
   +------------- fetch <----------+
   |
   +-------------- pull <----------+
```

Dans la pratique :

- `push` envoie certains commits vers le dépôt distant.
- `fetch` récupère les informations nouvelles du dépôt distant.
- `pull` récupère les changements puis tente de les intégrer à la branche courante selon la configuration.

### 16.3. Créer un dépôt distant

Sur GitHub ou GitLab :

1. Connectez-vous à la plateforme.
2. Créez un dépôt.
3. Choisissez son nom.
4. Définissez sa visibilité.
5. Copiez l'adresse de clonage proposée.

Pour un premier exercice, vous pouvez créer un dépôt vide sur la plateforme.

Si votre dépôt local existe déjà et contient un historique, évitez de créer simultanément un fichier README et d'autres fichiers initiaux sur le serveur sans comprendre comment les deux historiques seront réunis. Il est plus simple pour un débutant de créer un dépôt distant vide puis de lui envoyer le contenu local.

### 16.4. Ajouter le dépôt distant

Dans votre dépôt local :

```bash
git remote add origin ADRESSE_DU_DEPOT
```

Remplacez `ADRESSE_DU_DEPOT` par l'adresse réelle obtenue sur la plateforme.

`origin` est un nom conventionnel pour le dépôt distant principal. Vous pourriez utiliser un autre nom, mais `origin` est le choix le plus courant lors du clonage.

Pour afficher les dépôts distants :

```bash
git remote -v
```

### 16.5. Envoyer la branche principale

Si votre branche s'appelle `main` :

```bash
git push -u origin main
```

L'option `-u` configure généralement la branche distante suivie par votre branche locale, ce qui simplifie les prochains envois.

Les droits d'accès doivent être configurés sur la plateforme. GitHub et GitLab peuvent demander une authentification par navigateur, par clé SSH ou par un autre mécanisme pris en charge.

N'inscrivez jamais un mot de passe ou un jeton secret directement dans le code source pour faciliter l'accès au dépôt.

### 16.6. Cloner un dépôt existant

Si un dépôt existe déjà sur une plateforme, la commande habituelle pour en obtenir une copie locale est :

```bash
git clone ADRESSE_DU_DEPOT
```

Git crée un répertoire pour le dépôt cloné et configure généralement un dépôt distant appelé `origin`.

Vous pouvez ensuite entrer dans le projet :

```bash
cd nom-du-depot
```

Le nom du répertoire dépend de l'adresse du dépôt, sauf si vous précisez un nom différent lors du clonage.

## 17. Comprendre `fetch`, `pull` et `push`

Ces trois commandes sont essentielles pour travailler avec un dépôt distant.

### 17.1. `git fetch`

Cette commande récupère les nouvelles données d'un dépôt distant sans intégrer automatiquement les changements dans la branche courante.

```bash
git fetch origin
```

Vous pouvez ensuite examiner les nouvelles informations, par exemple :

```bash
git log --oneline --graph --decorate --all
```

Cette opération est utile lorsque vous souhaitez voir ce qui existe sur le serveur avant de modifier votre travail local.

### 17.2. `git pull`

Cette commande récupère les changements du dépôt distant et tente de les intégrer à la branche courante selon la configuration et la situation de l'historique.

```bash
git pull
```

Lorsque la branche locale suit une branche distante, Git utilise généralement cette relation pour déterminer les changements à récupérer.

Une version explicite, lorsque vous savez que le distant est `origin` et que la branche est `main`, est :

```bash
git pull origin main
```

Le résultat peut varier selon que les historiques peuvent avancer directement ou qu'ils ont divergé.

Si votre objectif est d'exiger une simple avance sans créer de fusion, vous pouvez utiliser :

```bash
git pull --ff-only
```

Cette commande échoue si une avance directe n'est pas possible.

### 17.3. `git push`

Cette commande envoie des commits vers un dépôt distant.

```bash
git push
```

Si la branche suit une branche distante configurée, cette commande utilise généralement cette relation.

Pour préciser la destination :

```bash
git push origin main
```

Si une autre personne a envoyé des commits incompatibles avec votre historique local, le serveur peut refuser le push.

Ce refus protège le dépôt contre une mise à jour qui ferait perdre ou ignorerait des changements distants.

Il faut alors récupérer et intégrer les changements, résoudre les éventuels conflits et envoyer de nouveau le travail.

### 17.4. Comparaison des commandes

| Commande | Récupère les données distantes | Intègre les changements à la branche courante | Envoie les commits locaux |
|---|---|---|---|
| `git fetch` | Oui | Non, pas automatiquement | Non |
| `git pull` | Oui | Oui, selon le mode d'intégration | Non |
| `git push` | Non, pas pour intégrer de nouveaux changements distants | Non | Oui |

### 17.5. Routine de travail sur un dépôt partagé

Une routine élémentaire peut être la suivante :

```text
1. Vérifier l'état local
        |
        v
2. Récupérer les changements distants
        |
        v
3. Intégrer les changements compatibles
        |
        v
4. Créer ou modifier sa branche de travail
        |
        v
5. Modifier les fichiers
        |
        v
6. Tester
        |
        v
7. Préparer et enregistrer un commit
        |
        v
8. Envoyer la branche distante
        |
        v
9. Ouvrir une pull request si nécessaire
```

Dans une équipe, l'ordre exact dépend du flux de travail adopté. La règle importante est d'éviter de travailler longtemps sans intégrer les changements des autres personnes lorsque cela augmente le risque de conflits.

## 18. Collaborer avec les branches distantes

### 18.1. Les branches locales et les branches distantes

Une branche locale est une référence présente dans votre dépôt local.

Une branche de suivi distant, telle que `origin/main`, représente l'état distant de cette branche connu par votre dépôt local à la suite d'une récupération.

Exemple :

```text
main              -> branche locale
origin/main       -> état distant connu localement
feature-alertes   -> branche de fonctionnalité locale
```

`origin/main` n'est pas simplement un autre nom pour votre branche `main`. Les deux références peuvent pointer vers des commits différents.

### 18.2. Récupérer l'état distant

```bash
git fetch origin
```

Afficher les branches :

```bash
git branch -a
```

Examiner l'historique :

```bash
git log --oneline --graph --decorate --all
```

Ces commandes permettent de repérer un éventuel décalage entre la branche locale et la branche distante connue.

### 18.3. Envoyer une nouvelle branche

Créer une branche de travail :

```bash
git switch -c feature/documentation
```

Modifier les fichiers, préparer les changements et créer un commit :

```bash
git add README.md
git commit -m "Amélioration de la documentation"
```

Envoyer la branche :

```bash
git push -u origin feature/documentation
```

La branche est maintenant disponible sur le serveur si l'opération réussit.

Une pull request ou une merge request peut ensuite être ouverte pour proposer l'intégration de ce travail dans la branche principale.

### 18.4. La pull request

Une pull request permet de proposer des changements pour examen avant leur intégration.

Elle sert notamment à :

- Présenter les changements.
- Examiner le diff.
- Discuter des choix techniques.
- Exécuter ou consulter les tests automatiques.
- Demander des corrections.
- Obtenir les approbations exigées par le projet.

La pull request est une fonctionnalité de la plateforme collaborative. Git, à lui seul, ne crée pas nécessairement ce type d'objet.

## 19. Première approche des tags et des versions

### 19.1. Qu'est-ce qu'un tag ?

Un tag est une référence utilisée pour identifier un point précis de l'historique.

Les tags servent notamment à repérer les versions logicielles publiées.

Exemples :

```text
v1.0.0
v1.1.0
v1.1.1
```

Un numéro de version peut suivre une convention comme le versionnement sémantique, mais toutes les équipes n'utilisent pas nécessairement la même règle.

### 19.2. Créer un tag simple

Sur le commit courant :

```bash
git tag v1.0.0
```

Afficher les tags :

```bash
git tag
```

### 19.3. Créer un tag annoté

Un tag annoté enregistre des informations supplémentaires, notamment un message et l'identité de la personne qui l'a créé.

```bash
git tag -a v1.0.0 -m "Première version stable"
```

Pour consulter le tag :

```bash
git show v1.0.0
```

Pour un jalon de publication, le tag annoté est souvent préférable à un tag léger.

### 19.4. Envoyer un tag vers le dépôt distant

```bash
git push origin v1.0.0
```

Pour envoyer tous les tags locaux :

```bash
git push origin --tags
```

Cette deuxième commande envoie tous les tags locaux concernés. Avant de l'utiliser dans un projet professionnel, vérifiez qu'ils correspondent bien aux versions que vous souhaitez publier.

### 19.5. À quoi servent les tags dans CI/CD ?

Un pipeline peut être configuré pour réagir à la création d'un tag.

Par exemple :

```text
Modifications du code
        |
        v
Tests et vérifications
        |
        v
Commit de validation
        |
        v
Création du tag v1.0.0
        |
        v
Pipeline de publication
        |
        v
Artefact de version
```

Le tag identifie la version visée, mais il ne garantit pas à lui seul la qualité ou la sécurité de l'artefact publié. Les contrôles nécessaires doivent toujours être définis.

## 20. Les erreurs fréquentes des débutants

### 20.1. Modifier les fichiers sans vérifier l'état du dépôt

Avant une opération importante, exécutez :

```bash
git status
```

Cela aide à savoir si des changements non préparés ou non enregistrés sont présents.

### 20.2. Croire que `git add` enregistre définitivement les changements

`git add` prépare les changements.

Le commit est une opération distincte :

```bash
git add fichier.txt
git commit -m "Description du changement"
```

### 20.3. Faire un commit sans consulter le diff

Il peut arriver que le fichier préparé contienne plus de changements que prévu.

Vérifiez :

```bash
git diff --cached
```

avant de créer un commit important.

### 20.4. Utiliser `git add .` sans vérifier les fichiers

Un répertoire peut contenir des journaux, des fichiers temporaires ou des secrets.

Avant un ajout global :

```bash
git status
```

Examinez les fichiers proposés et vérifiez que `.gitignore` couvre les éléments qui ne doivent pas être suivis.

### 20.5. Travailler directement sur la branche principale

Cette pratique peut être acceptable dans un petit exercice personnel, mais une branche de travail permet généralement de séparer les changements et de simplifier la revue.

Exemple :

```bash
git switch -c feature/nouvelle-fonction
```

### 20.6. Utiliser des commandes de suppression sans en comprendre l'effet

Les commandes comme `git restore`, `git reset` ou certaines variantes de `git clean` peuvent supprimer des modifications locales.

Ne lancez pas une commande destructive simplement parce qu'une page web la recommande.

Commencez par examiner l'état du dépôt, le diff et les conséquences possibles.

### 20.7. Ignorer les conflits de fusion

Un conflit doit être résolu, pas contourné aveuglément.

Examinez les deux versions, choisissez le résultat correct puis exécutez les tests pertinents.

### 20.8. Publier un secret par erreur

Si un secret est commité, le supprimer du fichier et créer un nouveau commit ne supprime pas les anciennes versions de ce secret dans l'historique.

Il faut révoquer ou renouveler le secret exposé et appliquer la procédure de sécurité adaptée.

### 20.9. Penser qu'un dépôt Git est une sauvegarde complète

Git conserve l'historique des fichiers suivis, mais il ne protège pas automatiquement contre toutes les pertes.

Par exemple, les fichiers non suivis, les données externes, les secrets mal gérés et certains fichiers générés peuvent ne pas être disponibles dans l'historique.

Un dépôt distant et une véritable stratégie de sauvegarde répondent à des besoins différents.

## 21. Bonnes pratiques à appliquer dès le début

### 21.1. Vérifier régulièrement l'état du dépôt

```bash
git status
```

C'est une commande simple qui aide à éviter de nombreux malentendus.

### 21.2. Utiliser des commits cohérents

Un commit devrait décrire un changement compréhensible et limiter les modifications sans rapport entre elles.

### 21.3. Lire les différences avant de valider

```bash
git diff
git diff --cached
```

Ces commandes permettent de distinguer ce qui a été modifié de ce qui sera enregistré.

### 21.4. Utiliser `.gitignore`

Ignorer les fichiers temporaires et les éléments qui ne doivent pas être versionnés.

Ne pas confondre une règle d'ignorance avec un mécanisme de suppression de l'historique.

### 21.5. Utiliser des branches pour les changements séparés

Créer une branche dédiée à une fonctionnalité ou à une correction facilite la revue et l'intégration.

### 21.6. Éviter de réécrire l'historique partagé sans coordination

Des commandes telles que `git commit --amend` et certaines formes de `git reset` modifient l'historique local.

Si des commits ont déjà été partagés, coordonnez-vous avec l'équipe avant d'en réécrire l'historique.

### 21.7. Récupérer les changements distants avec prudence

Avant un push important, vérifiez la situation du dépôt.

Lorsque les historiques divergent, comprenez la cause du décalage avant d'utiliser une commande destinée à forcer l'envoi.

### 21.8. Tester les changements avant de les intégrer

Git conserve des versions. Il ne certifie pas que le code est correct.

Les tests automatisés, les revues de code et les contrôles du pipeline complètent donc le contrôle de versions.

### 21.9. Protéger les secrets

Ne versionnez pas de mots de passe, de clés privées ni de jetons d'accès.

Utilisez un stockage adapté des secrets et des mécanismes d'authentification sécurisés.

### 21.10. Documenter la procédure de contribution

Un fichier `README.md` utile peut expliquer :

- L'objectif du projet.
- Les prérequis.
- L'installation.
- Les commandes de test.
- La structure du dépôt.
- Le mode de contribution.
- Les règles de commit.
- Les précautions de sécurité.

## 22. Laboratoire pratique : construire un mini-projet versionné

Ce laboratoire réunit les principales commandes du cours dans un scénario concret.

L'objectif est de créer un petit projet de scripts réseau, d'enregistrer plusieurs versions, de travailler sur une branche, de fusionner le changement puis de connecter le projet à un dépôt distant.

### 22.1. Étape 1 : créer le projet

```bash
mkdir supervision-reseau
cd supervision-reseau
git init
```

Vérifiez l'état initial :

```bash
git status
```

### 22.2. Étape 2 : créer le README

Créez `README.md` :

```markdown
# Supervision réseau

Projet pédagogique pour apprendre Git.

Fonctions prévues :
- Afficher les informations du projet.
- Préparer l'ajout de contrôles réseau.
- Organiser les changements avec des branches.
```

Ajoutez ensuite un `.gitignore` :

```gitignore
# Fichiers temporaires
*.log
*.tmp

# Secrets et configuration locale
.env

# Fichiers système
.DS_Store
Thumbs.db
```

### 22.3. Étape 3 : créer le premier commit

```bash
git status
git add README.md .gitignore
git diff --cached
git commit -m "Initialisation du projet de supervision"
```

Vérifiez l'historique :

```bash
git log --oneline
```

### 22.4. Étape 4 : créer un fichier Python

Créez `supervision.py` :

```python
def afficher_etat():
    """Affiche un état simplifié du projet."""
    return "Supervision réseau : prête"


if __name__ == "__main__":
    print(afficher_etat())
```

Testez le script :

```bash
python supervision.py
```

Si votre système utilise `python3` :

```bash
python3 supervision.py
```

Résultat attendu :

```text
Supervision réseau : prête
```

Préparez et enregistrez le fichier :

```bash
git add supervision.py
git commit -m "Ajout du point d'entrée de supervision"
```

### 22.5. Étape 5 : créer une branche de fonctionnalité

```bash
git switch -c feature/etat-service
```

Modifiez `supervision.py` pour obtenir :

```python
def afficher_etat():
    """Affiche un état simplifié du projet."""
    return "Supervision réseau : prête"


def afficher_service(nom, disponible):
    """Retourne un état lisible pour un service."""
    etat = "disponible" if disponible else "indisponible"
    return f"{nom} : {etat}"


if __name__ == "__main__":
    print(afficher_etat())
    print(afficher_service("Serveur DNS", True))
```

Exécutez :

```bash
python supervision.py
```

Résultat attendu :

```text
Supervision réseau : prête
Serveur DNS : disponible
```

Contrôlez le changement :

```bash
git diff
git status
```

Puis enregistrez-le :

```bash
git add supervision.py
git commit -m "Ajout de l'affichage de l'état d'un service"
```

### 22.6. Étape 6 : examiner l'historique

```bash
git log --oneline --graph --decorate --all
```

Vous devez voir plusieurs commits et la branche `feature/etat-service`.

Le graphe exact dépend de l'historique obtenu pendant les étapes précédentes.

### 22.7. Étape 7 : fusionner la fonctionnalité

Passez sur la branche principale :

```bash
git switch main
```

Fusionnez la fonctionnalité :

```bash
git merge feature/etat-service
```

Si votre branche principale porte un autre nom, utilisez ce nom.

Vérifiez ensuite :

```bash
git status
python supervision.py
git log --oneline --graph --decorate --all
```

La fonction ajoutée doit être présente après la fusion.

### 22.8. Étape 8 : supprimer la branche terminée

Une fois la fusion réussie et le résultat vérifié :

```bash
git branch -d feature/etat-service
```

Cette opération supprime la référence locale de la branche. Elle ne supprime pas les commits devenus accessibles depuis la branche principale.

### 22.9. Étape 9 : créer un dépôt distant

Créez un dépôt vide sur GitHub ou GitLab, puis copiez son adresse.

Dans votre dépôt local :

```bash
git remote add origin ADRESSE_DU_DEPOT
```

Vérifiez l'adresse configurée :

```bash
git remote -v
```

Envoyez la branche principale :

```bash
git push -u origin main
```

Si votre branche porte un autre nom, adaptez la commande.

### 22.10. Étape 10 : vérifier le résultat

Sur la plateforme distante, vérifiez que les éléments suivants sont présents :

```text
supervision-reseau/
|
+-- README.md
+-- .gitignore
+-- supervision.py
```

L'historique des commits doit également être accessible.

Vous avez ainsi créé un dépôt local, enregistré plusieurs versions, travaillé sur une branche, fusionné une fonctionnalité et publié le résultat sur une plateforme distante.

## 23. Exercices de compréhension

### Exercice 1 : distinguer Git et GitHub

Une personne affirme : « Je n'ai pas besoin de Git, car j'utilise déjà GitHub. »

Expliquez pourquoi cette affirmation confond deux éléments différents.

### Exercice 2 : comprendre `add` et `commit`

Vous modifiez `app.py`, puis exécutez :

```bash
git add app.py
```

Vous modifiez ensuite une nouvelle fois `app.py`, sans exécuter un nouvel `add`.

Quelle version du fichier est préparée pour le prochain commit ? Quelle commande permet de vérifier ce qui reste non préparé ?

### Exercice 3 : analyser un état Git

La commande `git status` indique :

```text
Changes to be committed:
    modified: README.md

Changes not staged for commit:
    modified: app.py

Untracked files:
    notes.txt
```

Répondez aux questions suivantes :

1. Quel fichier possède une modification préparée ?
2. Quel fichier a une modification qui n'est pas préparée ?
3. Quel fichier n'est pas encore suivi ?
4. Quels fichiers seront concernés par le prochain commit si vous ne faites aucune autre opération ?

### Exercice 4 : créer une branche

Vous travaillez sur `main` et souhaitez développer une fonction sans modifier immédiatement la branche principale.

Donnez la commande pour créer une branche nommée `feature/api` et vous y déplacer.

### Exercice 5 : fusionner une fonctionnalité

Vous avez terminé le travail sur `feature/api` et souhaitez le fusionner dans `main`.

Écrivez les commandes nécessaires, en supposant que les changements sont enregistrés dans des commits et que le dépôt n'a pas de conflit en cours.

### Exercice 6 : résoudre un conflit

Pendant une fusion, un fichier présente les marqueurs suivants :

```text
<<<<<<< HEAD
timeout = 5
=======
timeout = 10
>>>>>>> feature-timeout
```

Expliquez :

1. Pourquoi ce conflit s'est produit.
2. Pourquoi il ne faut pas supprimer les marqueurs sans examiner le contexte.
3. Comment terminer la fusion après avoir choisi la valeur correcte.

### Exercice 7 : ignorer un secret

Un fichier `.env` contient une clé d'API. Le fichier a déjà été commité.

Vous ajoutez ensuite `.env` dans `.gitignore`.

Le secret a-t-il disparu de l'historique ? Quelle mesure faut-il prendre si cette clé a pu être exposée ?

### Exercice 8 : comprendre les commandes distantes

Associez chaque besoin à une commande : `fetch`, `pull`, `push` ou `clone`.

A. Obtenir une copie locale d'un dépôt existant.

B. Récupérer les informations nouvelles d'un dépôt distant sans intégrer automatiquement son contenu à la branche courante.

C. Récupérer et intégrer les changements d'une branche distante suivie.

D. Envoyer ses commits vers le dépôt distant.

### Exercice 9 : choisir une méthode d'annulation

Un commit a déjà été partagé avec le reste de l'équipe. Vous souhaitez inverser son effet tout en conservant l'historique.

Quelle commande est généralement la plus appropriée et pourquoi ?

### Exercice 10 : diagnostiquer un push refusé

Vous exécutez :

```bash
git push origin main
```

Git refuse l'envoi parce que le dépôt distant contient des changements que votre branche locale ne possède pas.

Expliquez pourquoi ce refus peut être normal et proposez une démarche prudente pour résoudre la situation.

## 24. Corrigés des exercices

### Corrigé 1

Git est le système de gestion de versions. GitHub est une plateforme qui héberge des dépôts Git et ajoute des fonctionnalités collaboratives.

Git peut fonctionner localement sans GitHub. Inversement, GitHub utilise les mécanismes de gestion de versions fournis par Git.

### Corrigé 2

La version préparée est celle qui se trouvait dans la zone de préparation au moment du dernier `git add`.

La modification effectuée ensuite dans `app.py` reste non préparée.

Pour examiner les changements non préparés :

```bash
git diff
```

Pour examiner la version préparée :

```bash
git diff --cached
```

### Corrigé 3

1. `README.md` possède une modification préparée.
2. `app.py` contient une modification non préparée.
3. `notes.txt` est un fichier non suivi.
4. Seule la modification préparée de `README.md` sera incluse dans le prochain commit. Il faudra préparer les autres changements pour les inclure.

### Corrigé 4

```bash
git switch -c feature/api
```

Cette commande crée la branche et sélectionne immédiatement celle-ci.

### Corrigé 5

```bash
git switch main
git merge feature/api
git status
```

Après la fusion, il faut vérifier l'état du dépôt, puis exécuter les tests pertinents.

### Corrigé 6

Le conflit s'est produit parce que les deux branches ont proposé des valeurs différentes pour une zone que Git ne peut pas fusionner automatiquement avec certitude.

Il faut examiner le contexte pour déterminer quelle valeur correspond au comportement attendu.

Après avoir corrigé le fichier et supprimé tous les marqueurs :

```bash
git add fichier_concerne
git commit
```

Cette procédure suppose que la fusion est toujours en cours. Si les tests existent, il faut les exécuter après la résolution.

### Corrigé 7

Non. `.gitignore` n'efface pas les anciennes versions du fichier dans l'historique.

Si la clé a pu être exposée, il faut la révoquer ou la renouveler, examiner les accès possibles et traiter l'historique selon la procédure de sécurité appropriée.

Pour arrêter de suivre le fichier tout en le conservant localement :

```bash
git rm --cached .env
git add .gitignore
git commit -m "Arrêt du suivi du fichier local sensible"
```

Ces commandes ne suffisent pas à retirer le secret des commits antérieurs.

### Corrigé 8

- A : `git clone`
- B : `git fetch`
- C : `git pull`
- D : `git push`

### Corrigé 9

```bash
git revert IDENTIFIANT_DU_COMMIT
```

`git revert` crée un nouveau commit qui inverse le changement ciblé. Cette approche conserve l'historique et convient généralement mieux à un commit déjà partagé qu'une réécriture de l'historique.

### Corrigé 10

Le serveur refuse le push pour éviter qu'une mise à jour ne rende inaccessibles des changements distants dans la branche partagée.

Une démarche prudente consiste à inspecter l'état local, récupérer les nouveautés, examiner les différences et intégrer les changements de manière appropriée. Après résolution des éventuels conflits et exécution des tests, il est possible de retenter le push.

Exemple de première étape :

```bash
git status
git fetch origin
git log --oneline --graph --decorate --all
```

Ne recourez pas automatiquement à un push forcé : il pourrait écraser ou rendre difficilement accessible le travail d'autres personnes.

## 25. Projet de fin de niveau : gérer un dépôt Git de bout en bout

### 25.1. Objectif

Créer un petit projet versionné, organiser son historique et publier le dépôt vers une plateforme distante.

Le projet peut être un programme Python, un script Bash, un ensemble de configurations d'équipements réseau ou un outil de supervision.

### 25.2. Travail demandé

1. Installer Git et vérifier sa version.
2. Configurer le nom et l'adresse électronique d'auteur.
3. Créer un répertoire de projet.
4. Initialiser un dépôt Git.
5. Ajouter un `README.md`.
6. Créer un fichier `.gitignore`.
7. Réaliser au moins trois commits ayant des objectifs différents.
8. Examiner l'historique avec `git log`.
9. Créer une branche de fonctionnalité.
10. Développer et enregistrer une modification sur cette branche.
11. Fusionner la fonctionnalité dans la branche principale.
12. Connecter le dépôt à un dépôt distant.
13. Envoyer le projet vers la plateforme.
14. Vérifier l'historique et les fichiers sur la plateforme.
15. Documenter les commandes utilisées.

### 25.3. Structure indicative du livrable

```text
projet-git/
|
+-- README.md
+-- .gitignore
+-- src/
|   |
|   +-- application.py
|
+-- tests/
|   |
|   +-- test_application.py
|
+-- docs/
    |
    +-- utilisation.md
```

Cette structure est indicative. Elle peut être adaptée à un projet qui ne contient pas de code Python.

### 25.4. Critères de réussite

Le projet doit démontrer que vous savez :

- Distinguer les fichiers de travail, la zone de préparation et l'historique.
- Enregistrer des commits cohérents.
- Examiner les changements avec `git diff`.
- Utiliser une branche sans modifier immédiatement la branche principale.
- Fusionner le travail terminé.
- Configurer et utiliser un dépôt distant.
- Expliquer la différence entre `fetch`, `pull` et `push`.
- Éviter de publier des secrets.
- Expliquer les principales précautions relatives aux commandes de restauration et d'annulation.

### 25.5. Améliorations facultatives

Pour aller plus loin :

- Créer une pull request.
- Ajouter un workflow CI qui exécute les tests.
- Ajouter des tags pour identifier deux versions.
- Introduire volontairement un conflit de fusion dans un fichier de test.
- Résoudre ce conflit et documenter la procédure.
- Ajouter des règles de `.gitignore` adaptées aux outils du projet.
- Mettre en place une revue de code avant fusion.

## 26. Glossaire essentiel

**Branche :** référence qui permet de suivre une ligne de développement dans l'historique Git.

**Commit :** enregistrement d'un état du projet accompagné d'informations sur le changement.

**Conflit :** situation dans laquelle Git ne peut pas fusionner automatiquement certains changements.

**Dépôt local :** dépôt Git présent sur l'ordinateur de travail.

**Dépôt distant :** autre dépôt Git avec lequel le dépôt local peut échanger des données.

**Diff :** représentation des différences entre deux états de fichiers ou de l'historique.

**Fetch :** opération qui récupère les informations d'un dépôt distant sans intégrer automatiquement les changements à la branche courante.

**Git :** système de gestion de versions distribué.

**GitHub :** plateforme d'hébergement et de collaboration utilisant Git.

**GitLab :** plateforme proposant notamment l'hébergement Git, les merge requests et l'intégration continue.

**Historique :** ensemble des commits accessibles dans un dépôt.

**Index :** autre nom de la zone de préparation utilisée avant un commit.

**Merge :** opération de fusion de changements provenant de branches différentes.

**Origin :** nom couramment utilisé pour désigner le dépôt distant principal.

**Pull :** opération de récupération de changements distants suivie d'une tentative d'intégration à la branche courante.

**Push :** opération d'envoi de commits vers un dépôt distant.

**Référentiel de travail :** ensemble de fichiers du projet consultés et modifiés localement.

**Répertoire de travail :** fichiers présents dans le dossier du projet et actuellement manipulés.

**Restore :** commande permettant notamment de restaurer des fichiers ou de retirer des changements de la zone de préparation, selon les options employées.

**Staging area :** zone de préparation qui détermine les changements inclus dans le prochain commit.

**Tag :** référence permettant d'identifier un point précis de l'historique, par exemple une version publiée.

**Versionnage :** gestion des différentes versions successives d'un projet.

**`.gitignore` :** fichier définissant des motifs de fichiers que Git doit ignorer lorsqu'ils ne sont pas déjà suivis.

## 27. Références officielles pour approfondir

Les ressources suivantes permettent de consulter les explications officielles, les exemples de commandes et les comportements précis de Git.

### Documentation Git

- Site officiel de Git : https://git-scm.com/
- Documentation de référence des commandes : https://git-scm.com/docs
- Manuel utilisateur de Git : https://git-scm.com/docs/user-manual
- Tutoriel Git : https://git-scm.com/docs/gittutorial
- Livre Pro Git en français : https://git-scm.com/book/fr/v2
- Pro Git — Les bases de Git : https://git-scm.com/book/fr/v2/Les-bases-de-Git
- Pro Git — Les branches avec Git : https://git-scm.com/book/fr/v2/Les-branches-avec-Git
- Pro Git — Travailler avec des dépôts distants : https://git-scm.com/book/fr/v2/Les-bases-de-Git-Travailler-avec-des-dépôts-distants

### GitHub et collaboration

- GitHub Docs — Ignorer des fichiers : https://docs.github.com/en/get-started/git-basics/ignoring-files
- GitHub Docs — À propos des pull requests : https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests
- GitHub Docs — Comprendre GitHub Actions : https://docs.github.com/en/actions/get-started/understanding-github-actions

### GitLab

- GitLab Docs — Dépôts Git : https://docs.gitlab.com/user/project/repository/
- GitLab Docs — Présentation des pipelines CI/CD : https://docs.gitlab.com/ci/pipelines/

Les documentations officielles doivent rester la référence pour vérifier les options exactes, les versions et les comportements particuliers des commandes.

## 28. Synthèse du niveau débutant

Git permet de conserver un historique structuré des modifications d'un projet et de collaborer sur des versions communes.

Les notions fondamentales à retenir sont :

**Le dépôt** conserve les données et l'historique du projet.

**Le répertoire de travail** contient les fichiers en cours de modification.

**La zone de préparation** sélectionne les changements destinés au prochain commit.

**Le commit** enregistre les changements préparés dans l'historique.

**La branche** permet de développer un changement séparément avant de l'intégrer à une autre branche.

**La fusion** réunit les changements de plusieurs branches. Un conflit demande une décision lorsque Git ne peut pas fusionner automatiquement.

**Le dépôt distant** permet de partager les commits. `fetch`, `pull` et `push` répondent à des besoins différents.

**Le fichier `.gitignore`** évite de suivre certains fichiers non souhaités, mais n'efface pas les éléments déjà enregistrés dans l'historique.

Enfin, il faut savoir examiner l'état du dépôt, vérifier les différences avant un commit, comprendre les conséquences d'une commande et protéger les secrets.

La maîtrise de ces fondamentaux constitue une base nécessaire pour progresser vers les workflows collaboratifs, les stratégies de branches, les revues de code et les pipelines CI/CD.