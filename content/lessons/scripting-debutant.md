# Scripting Bash sous Linux — Niveau débutant

> **Fichier :** `scripting-debutant.md`  
> **Niveau :** Débutant  
> **Domaine :** Administration Linux, automatisation et scripting système  
> **Shell étudié :** GNU Bash  
> **Prérequis :** savoir naviguer dans un terminal Linux, utiliser les commandes courantes et manipuler les fichiers et répertoires  
> **Environnement conseillé :** une machine virtuelle Linux Debian ou Ubuntu, ou une autre distribution Linux disposant de Bash


# 1. Objectifs pédagogiques

À la fin de ce cours, vous devez être capable de concevoir et d'exécuter un script Bash simple, de comprendre son fonctionnement et de corriger les erreurs courantes.

Vous apprendrez notamment à :

- expliquer le rôle d'un shell et d'un script ;
- créer un fichier de script, choisir son interpréteur et gérer ses permissions ;
- utiliser les variables et les paramètres d'un script ;
- distinguer les guillemets simples, les guillemets doubles et l'absence de guillemets ;
- demander une information à l'utilisateur ;
- afficher des messages et rediriger des sorties ;
- exploiter le résultat d'une commande ;
- utiliser les conditions `if`, `elif`, `else` et `case` ;
- répéter des opérations avec `for`, `while` et `until` ;
- écrire des fonctions simples ;
- vérifier l'existence d'un fichier ou d'un répertoire ;
- traiter correctement les codes de retour ;
- gérer les erreurs courantes et déboguer un script ;
- limiter les risques liés à l'automatisation ;
- construire un petit outil d'administration Linux reproductible.

Ce niveau ne vise pas encore à créer des frameworks d'automatisation complexes. Il doit vous donner des bases solides, compréhensibles et fiables.

# 2. Sommaire

1. Comprendre le scripting
2. Comprendre le rôle du shell et de Bash
3. Préparer son environnement de travail
4. Créer et exécuter un premier script
5. Comment Bash interprète un script
6. Les commentaires et la documentation
7. Les variables
8. Les guillemets et les espaces
9. Les paramètres positionnels
10. Les entrées et les sorties
11. La substitution de commande
12. Les codes de retour
13. Les conditions
14. Les tests sur les fichiers et les répertoires
15. Les opérations arithmétiques
16. Les instructions `case`
17. Les boucles
18. Les fonctions
19. Les tableaux Bash : première approche
20. Les redirections et les pipelines
21. Le traitement simple de fichiers et de listes
22. Les bonnes pratiques de sécurité
23. Le débogage et les outils de contrôle
24. TP guidés
25. Exercices corrigés
26. Défi final : outil de contrôle de répertoires
27. Liste de compétences
28. Fiche de révision
29. Glossaire
30. Ressources officielles


# 3. Comprendre le scripting

## 3.1. Qu'est-ce qu'un script ?

Un script est un fichier texte qui contient une suite d'instructions destinées à être exécutées par un interpréteur.

Sous Linux, un script Bash peut regrouper plusieurs commandes qui seraient normalement saisies manuellement dans un terminal.

Exemple de commandes saisies une par une :

```bash
date
hostname
whoami
```

Ces trois commandes affichent respectivement la date, le nom de la machine et l'identité de l'utilisateur courant.

Vous pouvez enregistrer ces instructions dans un même fichier et les exécuter en une seule opération.

```bash
#!/usr/bin/env bash

date
hostname
whoami
```

Le fichier devient un petit programme d'automatisation.

## 3.2. Pourquoi utiliser des scripts ?

Le scripting est utile pour :

- automatiser les tâches répétitives ;
- appliquer une procédure toujours de la même manière ;
- vérifier l'état d'un système ;
- rechercher des fichiers ;
- contrôler des répertoires ;
- produire des rapports ;
- préparer des tâches planifiées ;
- réduire les erreurs liées aux manipulations manuelles.

Prenons l'exemple d'un administrateur qui doit vérifier chaque matin l'identité de la machine, l'espace disque et la date.

Sans script, il doit saisir plusieurs commandes.

Avec un script, il peut réunir ces contrôles dans un fichier unique.

Attention : l'automatisation accélère aussi les erreurs. Un script mal écrit peut répéter une mauvaise opération très rapidement. Il faut donc savoir contrôler ce qu'un script va faire avant de le lancer.

## 3.3. Script, commande et programme : quelle différence ?

Une **commande** est une instruction exécutée dans le shell.

Un **script** est un fichier contenant plusieurs instructions organisées.

Un **programme** est un ensemble d'instructions exécutables. Il peut être compilé en langage machine ou interprété par un environnement d'exécution.

Un script Bash est un programme interprété.

## 3.4. Exemple de cas d'usage en administration Linux

Imaginons une machine de laboratoire appelée `serveur-lab`.

L'administrateur souhaite produire un petit rapport.

```text
Rapport système
├── Date du contrôle
├── Nom de la machine
├── Utilisateur courant
└── Espace disque
```

Un script peut réunir ces informations, les afficher ou les enregistrer dans un fichier.

La logique générale est la suivante :

```text
        DÉBUT
          |
          v
  Collecter les informations
          |
          v
  Préparer les résultats
          |
          v
  Afficher ou enregistrer
          |
          v
         FIN
```

Un script n'est pas obligatoirement complexe. Sa valeur vient surtout de sa capacité à exécuter correctement une procédure définie.


# 4. Comprendre le rôle du shell et de Bash

## 4.1. Qu'est-ce qu'un shell ?

Le shell est un interpréteur de commandes. Il reçoit des instructions, analyse leur syntaxe puis exécute les commandes correspondantes.

Il sert d'interface entre l'utilisateur et les outils du système.

```text
Utilisateur
    |
    | saisit une commande
    v
Shell
    |
    | analyse et prépare l'exécution
    v
Commande ou programme
    |
    | produit un résultat
    v
Terminal
```

Le shell peut être utilisé de manière interactive, dans un terminal, ou de manière non interactive, pour exécuter un script.

## 4.2. Qu'est-ce que Bash ?

Bash signifie *Bourne Again SHell*.

C'est un shell très utilisé dans les environnements Linux. Il possède des fonctionnalités pour manipuler des variables, exécuter des commandes, prendre des décisions, répéter des opérations et organiser du code en fonctions.

Dans ce cours, nous utiliserons principalement Bash.

## 4.3. Bash et les autres shells

Plusieurs shells peuvent être présents sur un système.

| Shell | Particularité générale |
|---|---|
| `bash` | Shell étudié dans ce cours, riche en fonctionnalités |
| `sh` | Interface de shell dont le comportement dépend de l'implémentation utilisée |
| `dash` | Shell léger, souvent utilisé pour `/bin/sh` sur Debian et Ubuntu |
| `zsh` | Shell interactif avec de nombreuses fonctionnalités |
| `fish` | Shell interactif avec une syntaxe différente |

Un script Bash n'est pas automatiquement compatible avec `sh`, `dash`, `zsh` ou `fish`.

Par exemple :

```bash
#!/usr/bin/env bash

nom="Linux"
echo "Bonjour $nom"
```

Cette syntaxe est courante en Bash. Elle ne doit pas être considérée comme une garantie de compatibilité avec tous les shells.

**Règle :** si le script a été écrit pour Bash, exécutez-le avec Bash et indiquez cet interpréteur dans son en-tête.

## 4.4. Vérifier le shell utilisé

Pour connaître l'interpréteur indiqué dans la variable d'environnement `SHELL` :

```bash
echo "$SHELL"
```

Cette variable représente généralement le shell de connexion configuré pour l'utilisateur. Elle ne garantit pas qu'elle corresponde au processus shell actuellement utilisé.

Pour identifier le processus shell courant, vous pouvez utiliser :

```bash
ps -p "$$" -o comm=
```

Pour vérifier la version de Bash :

```bash
bash --version
```

Pour vérifier si Bash est disponible dans le `PATH` :

```bash
command -v bash
```

La commande `command -v` indique où la commande est trouvée ou si elle est disponible.


# 5. Préparer son environnement de travail

Nous allons utiliser un répertoire de laboratoire pour éviter de mélanger les exercices avec les fichiers personnels ou ceux du système.

## 5.1. Créer un répertoire de travail

Dans un terminal :

```bash
mkdir -p "$HOME/lab-scripting"
cd "$HOME/lab-scripting"
```

Explications :

- `mkdir` crée un répertoire ;
- `-p` permet notamment de créer les répertoires parents nécessaires et évite une erreur si le répertoire existe déjà ;
- `$HOME` désigne le répertoire personnel de l'utilisateur ;
- `cd` change le répertoire courant.

Vérifiez votre position :

```bash
pwd
```

Affichez le contenu du répertoire :

```bash
ls -la
```

## 5.2. Organiser les exercices

Vous pouvez prévoir une organisation simple :

```text
lab-scripting/
├── 01-premier-script.sh
├── 02-variables.sh
├── 03-conditions.sh
├── 04-boucles.sh
├── 05-fonctions.sh
├── 06-rapport.sh
└── rapports/
```

Créer le sous-répertoire pour les rapports :

```bash
mkdir -p "$HOME/lab-scripting/rapports"
```

## 5.3. Créer ou modifier un fichier

Si un éditeur de terminal est disponible, vous pouvez employer `nano` :

```bash
nano 01-premier-script.sh
```

Dans `nano` :

- `Ctrl + O` enregistre le fichier ;
- `Entrée` confirme le nom ;
- `Ctrl + X` quitte l'éditeur.

Vous pouvez aussi employer un éditeur graphique ou un autre éditeur de texte.

**Important :** un script Bash est un fichier texte ordinaire. Il n'a pas besoin d'une extension `.sh` pour fonctionner, mais cette extension est une convention utile.


# 6. Créer et exécuter un premier script

## 6.1. Écrire le script

Créez `01-premier-script.sh` avec le contenu suivant :

```bash
#!/usr/bin/env bash

echo "Bonjour et bienvenue dans le scripting Bash."
echo "Date du contrôle :"
date

echo "Nom de la machine :"
hostname

echo "Utilisateur courant :"
whoami
```

## 6.2. Comprendre la première ligne

La première ligne est appelée le *shebang* :

```bash
#!/usr/bin/env bash
```

Elle indique au système qu'il doit rechercher `bash` à travers l'environnement puis l'utiliser pour interpréter le fichier lorsqu'il est lancé directement comme un programme.

Cette forme suppose que `env` est disponible à l'emplacement indiqué par le système.

Une autre forme courante est :

```bash
#!/bin/bash
```

Cette seconde forme suppose que Bash est installé à `/bin/bash`.

Il faut choisir une convention adaptée à l'environnement cible. Les deux formes sont courantes, mais elles ne sont pas interchangeables dans toutes les configurations.

## 6.3. Première méthode : lancer Bash directement

Placez-vous dans le répertoire du laboratoire :

```bash
cd "$HOME/lab-scripting"
```

Puis exécutez :

```bash
bash 01-premier-script.sh
```

Bash lit le fichier et exécute les instructions dans l'ordre.

Cette méthode ne nécessite pas que le fichier possède le droit d'exécution.

## 6.4. Deuxième méthode : rendre le script exécutable

Pour pouvoir lancer le script directement :

```bash
chmod u+x 01-premier-script.sh
```

La signification de la commande :

- `chmod` modifie les permissions ;
- `u` désigne le propriétaire du fichier ;
- `+x` ajoute le droit d'exécution.

Exécutez ensuite le fichier depuis son emplacement :

```bash
./01-premier-script.sh
```

Le préfixe `./` signifie que le fichier se trouve dans le répertoire courant.

Le répertoire courant n'est généralement pas recherché automatiquement lors de la saisie d'un nom de commande. C'est pourquoi `01-premier-script.sh` et `./01-premier-script.sh` ne désignent pas exactement la même manière d'accéder au fichier.

## 6.5. Vérifier les permissions

```bash
ls -l 01-premier-script.sh
```

Vous pourriez obtenir une sortie ressemblant à :

```text
-rwxr--r-- 1 utilisateur utilisateur 190 oct. 24 09:00 01-premier-script.sh
```

Les caractères de permission indiquent notamment :

- `r` : lecture ;
- `w` : écriture ;
- `x` : exécution.

Les détails exacts de la sortie peuvent varier.

**À retenir :** lancer un fichier avec `bash fichier.sh` et lancer directement `./fichier.sh` sont deux modes d'exécution différents.


# 7. Comment Bash interprète un script

Bash ne traite pas toutes les lignes comme du simple texte. Il reconnaît une syntaxe et effectue plusieurs opérations avant d'exécuter les commandes.

Par exemple :

```bash
#!/usr/bin/env bash

nom="Amina"
echo "Bonjour $nom"
```

Bash doit :

1. reconnaître l'instruction d'affectation ;
2. enregistrer la valeur de la variable `nom` ;
3. interpréter les guillemets et l'expansion de `$nom` ;
4. exécuter `echo` avec le texte obtenu.

Résultat :

```text
Bonjour Amina
```

## 7.1. Une instruction par ligne

Pour commencer, écrivez une instruction par ligne.

```bash
echo "Première instruction"
echo "Deuxième instruction"
echo "Troisième instruction"
```

Cela améliore la lecture, la maintenance et le repérage des erreurs.

Il est possible de séparer certaines commandes par des points-virgules, mais cette pratique est moins lisible pour un débutant.

## 7.2. L'ordre d'exécution

Les commandes sont généralement exécutées dans l'ordre où elles apparaissent.

```bash
echo "Étape 1"
date
echo "Étape 2"
```

Le script ne passe normalement à l'instruction suivante qu'après la fin de la commande précédente, sauf lorsqu'une opération est lancée en arrière-plan ou que d'autres mécanismes de concurrence sont utilisés.

## 7.3. Bash et les programmes externes

Certaines commandes sont des fonctionnalités intégrées du shell. D'autres sont des programmes externes.

Exemples :

- `cd` est généralement une commande intégrée à Bash ;
- `read` est une commande intégrée ;
- `pwd` peut être fourni par le shell et exister également comme programme externe ;
- `date`, `hostname` et `mkdir` sont généralement des programmes externes.

Vérifiez comment une commande est résolue :

```bash
type cd
type date
```

Cette distinction aide à comprendre le fonctionnement du shell, mais il n'est pas nécessaire de connaître toutes les subtilités internes pour écrire les premiers scripts.


# 8. Les commentaires et la documentation

Un commentaire est une information destinée au lecteur. Il n'est pas exécuté comme une commande.

En Bash, `#` commence généralement un commentaire lorsque ce caractère est interprété comme un introducteur de commentaire.

Exemple :

```bash
#!/usr/bin/env bash

# Identifie l'utilisateur courant.
whoami
```

Le shebang utilise également `#`, mais possède un rôle particulier lorsqu'il apparaît au début du fichier.

## 8.1. Documenter l'objectif d'un script

Un script professionnel simple peut commencer ainsi :

```bash
#!/usr/bin/env bash

# Fichier : informations-systeme.sh
# Objectif : afficher quelques informations locales.
# Environnement : Bash sous Linux.
# Usage : ./informations-systeme.sh

echo "Informations système"
hostname
date
```

Une bonne documentation permet de répondre rapidement à quatre questions :

- À quoi sert le script ?
- Comment l'exécuter ?
- Quelles informations ou quels paramètres attend-il ?
- Peut-il modifier des fichiers ou le système ?

## 8.2. Ne pas commenter chaque ligne inutilement

Commentaire peu utile :

```bash
# Affiche Bonjour
echo "Bonjour"
```

Commentaire plus utile lorsqu'un contexte est nécessaire :

```bash
# Les rapports de ce laboratoire sont stockés dans un répertoire distinct.
mkdir -p "$HOME/lab-scripting/rapports"
```

Le commentaire doit expliquer une intention, une décision ou une contrainte, et non simplement répéter l'instruction.


# 9. Les variables

Une variable permet de conserver une valeur et de la réutiliser.

## 9.1. Déclarer une variable

En Bash :

```bash
nom="Amina"
ville="Douala"
service="reseau"
```

Le signe `=` ne doit pas être entouré d'espaces dans une affectation simple.

Correct :

```bash
nom="Amina"
```

Incorrect :

```bash
nom = "Amina"
```

Dans le second cas, Bash interprète les éléments comme une commande et ses arguments, ce qui ne crée pas la variable attendue.

## 9.2. Lire le contenu d'une variable

Le symbole `$` permet généralement d'obtenir la valeur d'une variable :

```bash
echo "$nom"
```

Avec plusieurs variables :

```bash
echo "Nom : $nom"
echo "Ville : $ville"
echo "Service : $service"
```

Résultat :

```text
Nom : Amina
Ville : Douala
Service : reseau
```

## 9.3. Pourquoi mettre les variables entre guillemets ?

Privilégiez :

```bash
echo "$nom"
```

plutôt que :

```bash
echo $nom
```

Lorsque la valeur contient des espaces ou certains caractères spéciaux, l'absence de guillemets peut provoquer une séparation en plusieurs mots ou l'interprétation de motifs de fichiers.

Exemple :

```bash
nom="Amina N."
printf 'Nom : %s\n' "$nom"
```

Résultat :

```text
Nom : Amina N.
```

L'utilisation systématique de guillemets doubles autour des expansions de variables constitue une habitude très importante.

## 9.4. Nommer les variables

Utilisez des noms explicites.

À éviter :

```bash
a="rapport"
b="/tmp"
c="fichier.txt"
```

Plus lisible :

```bash
nom_rapport="rapport"
repertoire_temporaire="/tmp"
nom_fichier="fichier.txt"
```

Les noms de variables Bash sont sensibles à la casse.

```bash
nom="Amina"
Nom="Paul"
```

`nom` et `Nom` sont deux variables distinctes.

Convention recommandée :

- `nom_utilisateur` pour une variable ordinaire ;
- `REPERTOIRE_RAPPORTS` pour une constante de configuration que le script ne modifiera pas.

Les majuscules ne rendent pas automatiquement une variable constante. Elles constituent une convention de nommage.

## 9.5. Afficher une variable avec `printf`

`printf` fournit un contrôle précis du format d'affichage.

```bash
nom="Amina"
age=25

printf 'Nom : %s\n' "$nom"
printf 'Âge : %s ans\n' "$age"
```

Quelques formats courants :

| Format | Usage |
|---|---|
| `%s` | texte |
| `%d` | entier décimal |
| `\n` | retour à la ligne |

Exemple numérique :

```bash
nombre=12
printf 'Le nombre vaut %d\n' "$nombre"
```

Utilisez `%s` pour afficher une valeur textuelle. Avec `%d`, assurez-vous que la valeur peut être interprétée comme un entier valide.

## 9.6. Variables non définies ou vides

Une variable non définie ne possède pas de valeur affectée dans le shell.

```bash
echo "$variable_inconnue"
```

Dans un contexte habituel, la commande affiche une ligne vide.

On peut distinguer plusieurs notions :

- variable définie avec une valeur ;
- variable définie avec une chaîne vide ;
- variable non définie.

Le paramètre spécial `${variable:-valeur}` permet de fournir une valeur par défaut lorsque la variable est vide ou non définie :

```bash
nom="${NOM_UTILISATEUR:-Invité}"
printf 'Bonjour %s\n' "$nom"
```

Si `NOM_UTILISATEUR` contient `Amina`, le script l'utilise. Sinon, il affiche `Invité`.

## 9.7. Variable et environnement

Une variable Bash ordinaire appartient au shell qui l'a définie.

Pour transmettre une variable à un programme lancé depuis ce shell, on peut l'exporter.

```bash
APPLICATION="monitoring"
export APPLICATION
```

Ou écrire :

```bash
export APPLICATION="monitoring"
```

Un programme enfant peut alors recevoir cette variable dans son environnement.

Exemple :

```bash
export LANGUE="fr"
bash -c 'printf "Langue reçue : %s\n" "$LANGUE"'
```

Attention : une variable non exportée n'est généralement pas transmise comme variable d'environnement aux programmes enfants.


# 10. Les guillemets et les espaces

La gestion des guillemets est l'une des bases les plus importantes du scripting Bash.

## 10.1. Les guillemets doubles

Les guillemets doubles permettent généralement de conserver une valeur comme un seul argument tout en autorisant l'expansion des variables.

```bash
nom="Amina N."
echo "Bonjour $nom"
```

Résultat :

```text
Bonjour Amina N.
```

Pour les opérations sur des fichiers :

```bash
nom_fichier="rapport hebdomadaire.txt"
touch "$nom_fichier"
```

Les guillemets empêchent ici le découpage de la variable en deux arguments.

## 10.2. Les guillemets simples

Les guillemets simples préservent le contenu littéral de leur intérieur, sans expansion ordinaire des variables.

```bash
nom="Amina"

printf '%s\n' 'Bonjour $nom'
printf '%s\n' "Bonjour $nom"
```

Résultat :

```text
Bonjour $nom
Bonjour Amina
```

Le premier affichage conserve le texte `$nom`. Le second remplace `$nom` par la valeur de la variable.

## 10.3. Sans guillemets

L'absence de guillemets autorise notamment le découpage en mots et l'expansion des motifs de fichiers après certaines expansions.

Exemple :

```bash
message="Bonjour tout le monde"
printf '<%s>\n' $message
```

La commande peut afficher plusieurs lignes, car le contenu de la variable est découpé en mots.

Avec :

```bash
printf '<%s>\n' "$message"
```

l'ensemble de la valeur est transmis comme un seul argument.

**Règle essentielle :** mettez les expansions de variables entre guillemets doubles, sauf lorsque vous souhaitez volontairement un comportement différent et que vous en comprenez les conséquences.

## 10.4. Les espaces dans les noms de fichiers

Un fichier peut contenir des espaces dans son nom.

```bash
nom_fichier="rapport de test.txt"
touch "$nom_fichier"
```

Pour vérifier sa présence :

```bash
if [[ -f "$nom_fichier" ]]; then
    printf 'Le fichier existe : %s\n' "$nom_fichier"
fi
```

Les guillemets autour de `"$nom_fichier"` sont importants pour que le nom soit traité comme une seule valeur.

## 10.5. Le caractère d'échappement

Dans certains contextes, l'antislash `\` permet de neutraliser l'interprétation spéciale du caractère qui suit.

Exemple :

```bash
printf 'Un retour à la ligne\n'
```

Dans le format de `printf`, `\n` signifie un retour à la ligne.

Dans le code suivant :

```bash
printf '%s\n' "Le prix est \$10"
```

le caractère `$` est affiché littéralement.


# 11. Les paramètres positionnels

Un script peut recevoir des arguments au moment de son lancement.

Ces arguments permettent de réutiliser le même script avec différentes valeurs sans modifier son code.

## 11.1. Écrire un script qui reçoit un argument

Créez `02-salutation.sh` :

```bash
#!/usr/bin/env bash

nom="${1:-Invité}"

printf 'Bonjour %s !\n' "$nom"
```

Exécution :

```bash
bash 02-salutation.sh Amina
```

Résultat :

```text
Bonjour Amina !
```

Sans argument :

```bash
bash 02-salutation.sh
```

Résultat :

```text
Bonjour Invité !
```

## 11.2. Comprendre `$1`, `$2` et `$3`

Les paramètres positionnels représentent les arguments reçus par le script.

| Paramètre | Signification |
|---|---|
| `$0` | nom ou chemin utilisé pour appeler le script |
| `$1` | premier argument |
| `$2` | deuxième argument |
| `$3` | troisième argument |
| `${10}` | dixième argument |
| `$#` | nombre d'arguments positionnels |
| `"$@"` | ensemble des arguments, en préservant chaque argument séparément lorsqu'il est cité |

Exemple :

```bash
#!/usr/bin/env bash

printf 'Script : %s\n' "$0"
printf 'Premier argument : %s\n' "${1:-absent}"
printf 'Deuxième argument : %s\n' "${2:-absent}"
printf 'Nombre d’arguments : %s\n' "$#"
```

Lancez le script :

```bash
bash 03-arguments.sh serveur1 production
```

## 11.3. Pourquoi `"$@"` est important

Supposons ce script :

```bash
#!/usr/bin/env bash

printf 'Argument : <%s>\n' "$@"
```

Exécutez-le ainsi :

```bash
bash 04-arguments.sh "fichier avec espaces.txt" sauvegarde
```

Le script traite correctement deux arguments :

1. `fichier avec espaces.txt`
2. `sauvegarde`

Utiliser `"$@"` est une pratique essentielle lorsqu'un script doit transmettre fidèlement des arguments à une autre commande.

À l'inverse, `"$*"` a un comportement différent : entre guillemets, il regroupe les arguments en une seule chaîne, généralement séparée par le premier caractère de `IFS`.

Pour débuter, retenez surtout ceci :

```bash
commande "$@"
```

transmet les arguments reçus sans décomposer artificiellement ceux qui contiennent des espaces.

## 11.4. Vérifier les arguments obligatoires

Un script peut refuser de poursuivre si un argument essentiel manque.

```bash
#!/usr/bin/env bash

if [[ $# -lt 1 ]]; then
    printf 'Usage : %s NOM\n' "$0" >&2
    exit 1
fi

nom="$1"
printf 'Nom reçu : %s\n' "$nom"
```

Le programme affiche ici un message d'utilisation sur la sortie d'erreur et termine avec un code non nul.


# 12. Les entrées et les sorties

Un script interagit avec son environnement grâce à des entrées, des sorties et des flux d'erreur.

## 12.1. Afficher un message avec `echo`

La commande `echo` est simple :

```bash
echo "Bonjour"
echo "Le contrôle est terminé."
```

Pour commencer, elle convient aux messages ordinaires.

## 12.2. Afficher un message avec `printf`

`printf` est souvent préférable pour les scripts, car son format d'affichage est plus prévisible.

```bash
printf 'Bonjour\n'
printf 'Utilisateur : %s\n' "$USER"
printf 'Répertoire personnel : %s\n' "$HOME"
```

## 12.3. Demander une saisie avec `read`

Le programme peut demander une valeur à l'utilisateur.

```bash
#!/usr/bin/env bash

printf 'Quel est votre prénom ? '
read -r prenom

printf 'Bonjour %s !\n' "$prenom"
```

L'option `-r` de `read` empêche l'interprétation habituelle des antislashs dans la saisie.

Exécution :

```text
Quel est votre prénom ? Amina
Bonjour Amina !
```

Une forme compacte est :

```bash
read -r -p "Votre prénom : " prenom
printf 'Bonjour %s\n' "$prenom"
```

Le comportement de `-p` est propre à Bash, ce qui est acceptable dans un cours consacré à Bash.

## 12.4. Gérer une saisie obligatoire

```bash
#!/usr/bin/env bash

read -r -p "Nom du serveur : " serveur

if [[ -z "$serveur" ]]; then
    printf 'Erreur : le nom du serveur est obligatoire.\n' >&2
    exit 1
fi

printf 'Serveur sélectionné : %s\n' "$serveur"
```

L'expression `-z` vérifie si une chaîne est vide.

La saisie utilisateur ne doit pas être automatiquement considérée comme fiable. Pour les opérations sensibles, il faut vérifier le format et les valeurs acceptables.

## 12.5. Saisie masquée

Pour un secret que l'on ne souhaite pas afficher à l'écran :

```bash
#!/usr/bin/env bash

read -r -s -p "Saisissez un secret de test : " secret
printf '\n'
printf 'La saisie a été reçue.\n'
```

L'option `-s` empêche l'affichage des caractères saisis dans le terminal. Elle ne protège pas à elle seule la valeur contre tous les risques de stockage, de journalisation ou d'exposition.

Évitez d'afficher ou d'enregistrer des mots de passe et autres secrets dans les journaux.


# 13. La substitution de commande

La substitution de commande permet de récupérer la sortie standard d'une commande et de l'utiliser dans une variable ou une autre expression.

## 13.1. Syntaxe recommandée

Utilisez :

```bash
variable="$(commande)"
```

Exemple :

```bash
date_actuelle="$(date)"
printf 'Date actuelle : %s\n' "$date_actuelle"
```

Autre exemple :

```bash
nom_machine="$(hostname)"
printf 'Machine : %s\n' "$nom_machine"
```

Bash exécute la commande à l'intérieur de `$(...)`, récupère sa sortie standard et remplace l'expression par le texte obtenu.

La substitution retire les retours à la ligne terminaux de la sortie capturée. Elle n'est donc pas un moyen de conserver fidèlement tous les octets d'un fichier.

## 13.2. Forme ancienne

On rencontre parfois :

```bash
variable=`date`
```

Cette syntaxe fonctionne dans de nombreux cas, mais `$(...)` est généralement plus lisible et facilite l'imbrication de substitutions.

Préférez :

```bash
variable="$(date)"
```

## 13.3. Utiliser le résultat d'une commande

Exemple de rapport :

```bash
#!/usr/bin/env bash

date_controle="$(date '+%Y-%m-%d %H:%M:%S')"
machine="$(hostname)"
utilisateur="$(whoami)"

printf 'Date : %s\n' "$date_controle"
printf 'Machine : %s\n' "$machine"
printf 'Utilisateur : %s\n' "$utilisateur"
```

Remarque : chaque commande doit exister sur le système et être accessible avec les permissions adaptées.

## 13.4. Ne pas confondre sortie et code de retour

Cette instruction :

```bash
resultat="$(hostname)"
```

récupère la sortie standard de `hostname`.

Elle ne transforme pas son code de retour en texte dans `resultat`.

Pour consulter le code de retour de la dernière commande :

```bash
printf 'Code de retour : %s\n' "$?"
```

Mais il faut le faire immédiatement après la commande concernée, car chaque nouvelle commande peut remplacer la valeur de `$?`.

Une meilleure organisation consiste souvent à tester directement le résultat de l'opération :

```bash
if resultat="$(hostname)"; then
    printf 'Machine : %s\n' "$resultat"
else
    printf 'Impossible de déterminer le nom de la machine.\n' >&2
    exit 1
fi
```


# 14. Les codes de retour

## 14.1. Qu'est-ce qu'un code de retour ?

À la fin d'une commande, le shell dispose d'un code de retour appelé *exit status*.

Convention générale :

- `0` : succès ;
- valeur non nulle : échec ou situation particulière.

Un code non nul n'explique pas toujours, à lui seul, la cause précise du problème. Son sens dépend de la commande.

## 14.2. Examiner le code de retour

```bash
true
printf 'Code : %s\n' "$?"
```

Résultat :

```text
Code : 0
```

Avec `false` :

```bash
false
printf 'Code : %s\n' "$?"
```

Résultat :

```text
Code : 1
```

Ces commandes permettent de comprendre comment les conditions Bash se basent sur les statuts d'exécution.

## 14.3. Terminer un script avec `exit`

Le script peut renvoyer son propre code de retour.

```bash
#!/usr/bin/env bash

printf 'Opération réussie.\n'
exit 0
```

Exemple d'échec :

```bash
#!/usr/bin/env bash

printf 'Erreur : opération impossible.\n' >&2
exit 1
```

Par convention, utilisez `exit 0` pour indiquer la réussite et un code non nul pour signaler un échec.

Les valeurs non nulles n'ont pas toutes une signification universelle. Il est néanmoins possible de définir une convention propre à son script.

## 14.4. Utiliser `&&` et `||`

`&&` permet d'exécuter la commande suivante si la précédente réussit.

```bash
mkdir -p "$HOME/lab-scripting/test" && printf 'Répertoire prêt.\n'
```

`||` permet d'exécuter la commande suivante si la précédente échoue.

```bash
mkdir "$HOME/lab-scripting" || printf 'Le répertoire ne peut pas être créé.\n' >&2
```

Dans ce deuxième exemple, le répertoire existe peut-être déjà. Ce cas peut provoquer un échec de `mkdir`, ce qui explique le message.

Il faut distinguer ce comportement d'une condition réellement inattendue.

## 14.5. Vérifier explicitement une opération

```bash
if mkdir -p "$HOME/lab-scripting/rapports"; then
    printf 'Répertoire de rapports disponible.\n'
else
    printf 'Échec : impossible de préparer les rapports.\n' >&2
    exit 1
fi
```

C'est une manière explicite d'associer une action à un résultat.


# 15. Les conditions

Une condition permet de prendre une décision en fonction d'un résultat ou d'un test.

## 15.1. Structure de base : `if`

```bash
if condition; then
    # Instructions si la condition réussit
fi
```

En Bash, la condition peut être un test, une commande ou une autre construction qui fournit un code de retour.

Exemple :

```bash
if [[ -f "rapport.txt" ]]; then
    printf 'Le fichier existe.\n'
fi
```

Si `rapport.txt` est un fichier ordinaire existant, le message est affiché.

## 15.2. Ajouter `else`

```bash
if [[ -f "rapport.txt" ]]; then
    printf 'Le fichier existe.\n'
else
    printf 'Le fichier est absent.\n'
fi
```

La branche `else` s'exécute lorsque le test de la condition échoue.

## 15.3. Ajouter `elif`

```bash
#!/usr/bin/env bash

read -r -p "Saisissez un nombre : " nombre

if [[ ! "$nombre" =~ ^[0-9]+$ ]]; then
    printf 'Veuillez saisir un entier positif ou nul.\n' >&2
    exit 1
elif (( nombre < 10 )); then
    printf 'Le nombre est inférieur à 10.\n'
elif (( nombre == 10 )); then
    printf 'Le nombre est égal à 10.\n'
else
    printf 'Le nombre est supérieur à 10.\n'
fi
```

Cet exemple vérifie d'abord que la saisie contient uniquement des chiffres. Il effectue ensuite des comparaisons numériques.

La construction `[[ ... =~ ... ]]` est une fonctionnalité de Bash permettant de tester une expression régulière.

La validation utilisée ici accepte des nombres entiers positifs ou nuls sans signe. Elle ne couvre pas les nombres négatifs ni les décimaux.

## 15.4. Les opérateurs de comparaison de chaînes

Dans les conditions Bash, on emploie notamment :

| Expression | Signification |
|---|---|
| `[[ "$a" == "$b" ]]` | les chaînes sont égales |
| `[[ "$a" != "$b" ]]` | les chaînes sont différentes |
| `[[ -z "$a" ]]` | la chaîne est vide |
| `[[ -n "$a" ]]` | la chaîne n'est pas vide |

Exemple :

```bash
mot_de_passe_test="linux"

if [[ "$mot_de_passe_test" == "linux" ]]; then
    printf 'Valeur de test reconnue.\n'
fi
```

Cet exemple sert uniquement à montrer une comparaison de chaînes. En situation réelle, n'utilisez pas de mot de passe codé en dur dans un script pour contrôler un accès.

## 15.5. Les comparaisons numériques

Avec la syntaxe arithmétique de Bash :

| Opérateur | Signification |
|---|---|
| `<` | inférieur à |
| `>` | supérieur à |
| `==` | égal à |
| `!=` | différent de |
| `<=` | inférieur ou égal |
| `>=` | supérieur ou égal |

Exemple :

```bash
nombre=18

if (( nombre >= 18 )); then
    printf 'La valeur atteint le seuil 18.\n'
fi
```

Dans une expression `(( ... ))`, Bash évalue une expression arithmétique.

Ne confondez pas ces comparaisons avec celles de la commande `[` dont les opérateurs numériques traditionnels sont notamment `-lt`, `-gt`, `-eq`, `-ne`, `-le` et `-ge`.

## 15.6. Combiner plusieurs conditions

Bash permet d'utiliser des opérateurs logiques.

Avec `[[ ... ]]` :

- `&&` signifie ET logique ;
- `||` signifie OU logique ;
- `!` signifie NON logique.

Exemple :

```bash
utilisateur="admin"
environnement="laboratoire"

if [[ "$utilisateur" == "admin" && "$environnement" == "laboratoire" ]]; then
    printf 'Conditions réunies pour le scénario de laboratoire.\n'
fi
```

N'interprétez pas ce test comme une véritable autorisation de sécurité. Il compare seulement les variables reçues ou définies par le script.

## 15.7. Pourquoi préférer `[[ ... ]]` en Bash ?

`[[ ... ]]` est une construction propre à Bash, plus riche que l'ancien test `[ ... ]`.

Elle évite notamment plusieurs problèmes de découpage des arguments et permet d'utiliser des expressions régulières avec `=~`.

Exemple recommandé pour un script Bash :

```bash
if [[ -n "$nom" ]]; then
    printf 'Nom renseigné : %s\n' "$nom"
fi
```

Dans ce cours, privilégiez `[[ ... ]]` pour les tests de chaînes et de fichiers lorsque le script est explicitement destiné à Bash.


# 16. Les tests sur les fichiers et les répertoires

Les scripts d'administration manipulent souvent des chemins. Il est donc essentiel de savoir tester leur présence et leur nature.

## 16.1. Tests essentiels

| Test | Signification |
|---|---|
| `-e chemin` | le chemin existe |
| `-f chemin` | le chemin est un fichier ordinaire |
| `-d chemin` | le chemin est un répertoire |
| `-r chemin` | le chemin est accessible en lecture |
| `-w chemin` | le chemin est accessible en écriture |
| `-x chemin` | le chemin est accessible en exécution ou traversée, selon le type de fichier |
| `-s chemin` | le fichier existe et sa taille est non nulle |

La réussite d'un test de permission ne garantit pas que toutes les opérations ultérieures réussiront. Les permissions, l'état du système de fichiers et d'autres mécanismes peuvent changer.

## 16.2. Vérifier un fichier

```bash
fichier="$HOME/lab-scripting/rapport.txt"

if [[ -f "$fichier" ]]; then
    printf 'Le fichier existe.\n'
else
    printf 'Le fichier est absent ou n’est pas un fichier ordinaire.\n'
fi
```

## 16.3. Vérifier un répertoire

```bash
repertoire="$HOME/lab-scripting/rapports"

if [[ -d "$repertoire" ]]; then
    printf 'Le répertoire existe.\n'
else
    printf 'Le répertoire est absent.\n'
fi
```

## 16.4. Vérifier l'existence puis créer un répertoire

```bash
#!/usr/bin/env bash

repertoire="$HOME/lab-scripting/rapports"

if [[ -d "$repertoire" ]]; then
    printf 'Le répertoire existe déjà.\n'
else
    if mkdir -p "$repertoire"; then
        printf 'Le répertoire a été créé.\n'
    else
        printf 'Erreur : création impossible.\n' >&2
        exit 1
    fi
fi
```

Remarque : `mkdir -p` permet déjà de créer le répertoire s'il n'existe pas. Dans un script réel, une simple tentative suivie d'un contrôle du résultat peut être plus courte et limiter les cas où l'état du répertoire change entre le test et l'opération.

## 16.5. La précaution sur les fichiers temporaires

Un fichier temporaire ne doit pas être créé avec un nom prévisible dans un répertoire partagé si une autre personne peut exploiter ce nom.

Pour un script réel, privilégiez un mécanisme adapté comme `mktemp`, qui permet de générer un nom temporaire unique.

Exemple de laboratoire :

```bash
#!/usr/bin/env bash

fichier_temporaire="$(mktemp)" || {
    printf 'Erreur : impossible de créer un fichier temporaire.\n' >&2
    exit 1
}

printf 'Fichier temporaire créé : %s\n' "$fichier_temporaire"

rm -f -- "$fichier_temporaire"
```

Ce script supprime le fichier temporaire qu'il vient lui-même de créer.

Attention : `rm` est une commande destructive. Ici, le chemin supprimé provient directement de `mktemp`. Ne remplacez pas cette variable par un chemin arbitraire sans comprendre les conséquences.


# 17. Les opérations arithmétiques

Bash permet d'effectuer des calculs entiers directement.

## 17.1. Additionner des nombres

```bash
a=10
b=5

somme=$((a + b))

printf 'Somme : %d\n' "$somme"
```

Résultat :

```text
Somme : 15
```

L'expression `$(( ... ))` réalise une expansion arithmétique.

## 17.2. Opérateurs courants

| Opérateur | Opération |
|---|---|
| `+` | addition |
| `-` | soustraction |
| `*` | multiplication |
| `/` | division entière |
| `%` | reste de division |

Exemple :

```bash
a=17
b=5

printf 'Addition : %d\n' "$((a + b))"
printf 'Soustraction : %d\n' "$((a - b))"
printf 'Multiplication : %d\n' "$((a * b))"
printf 'Division entière : %d\n' "$((a / b))"
printf 'Reste : %d\n' "$((a % b))"
```

La division avec des entiers ne produit pas un résultat décimal. Ainsi, `17 / 5` donne `3`.

La division par zéro doit être évitée, car elle provoque une erreur.

## 17.3. Calculer une moyenne entière

```bash
note1=12
note2=15
note3=18

moyenne=$(((note1 + note2 + note3) / 3))

printf 'Moyenne entière : %d\n' "$moyenne"
```

Le résultat est `15`.

Pour des calculs financiers ou des résultats nécessitant des décimales, l'arithmétique entière de Bash ne suffit pas à elle seule. Il faudra utiliser un outil adapté.

## 17.4. Attention aux valeurs reçues de l'utilisateur

Bash n'est pas une calculatrice qui valide automatiquement la saisie selon vos attentes.

Exemple de validation simple avant un calcul :

```bash
read -r -p "Saisissez un entier positif ou nul : " nombre

if [[ ! "$nombre" =~ ^[0-9]+$ ]]; then
    printf 'Entrée invalide.\n' >&2
    exit 1
fi

double=$((nombre * 2))
printf 'Double : %d\n' "$double"
```

La validation vérifie que la saisie est composée de chiffres. Elle ne traite pas ici les séparateurs de milliers, les nombres décimaux ou les signes.


# 18. Les instructions `case`

`case` permet de choisir une action selon la valeur d'une variable. Cette construction est très utile pour les menus et les options simples.

## 18.1. Structure générale

```bash
case "$variable" in
    valeur1)
        # Instructions
        ;;
    valeur2)
        # Instructions
        ;;
    *)
        # Cas par défaut
        ;;
esac
```

Le symbole `;;` termine chaque branche dans la forme courante. `esac` termine la structure `case`.

## 18.2. Exemple de menu

```bash
#!/usr/bin/env bash

printf '1. Afficher la date\n'
printf '2. Afficher le nom de la machine\n'
printf '3. Afficher l’utilisateur\n'

read -r -p "Votre choix : " choix

case "$choix" in
    1)
        date
        ;;
    2)
        hostname
        ;;
    3)
        whoami
        ;;
    *)
        printf 'Choix invalide.\n' >&2
        exit 1
        ;;
esac
```

Le menu permet à l'utilisateur de choisir l'opération.

## 18.3. Reconnaître plusieurs valeurs

Les motifs peuvent être regroupés :

```bash
case "$choix" in
    1|date)
        date
        ;;
    2|machine)
        hostname
        ;;
    *)
        printf 'Choix non reconnu.\n' >&2
        ;;
esac
```

L'utilisateur peut ainsi saisir `1` ou `date` pour obtenir la date.

## 18.4. Quand choisir `if` et quand choisir `case` ?

Utilisez généralement `if` lorsque vous comparez des conditions, des valeurs numériques ou des propriétés de fichiers.

Utilisez généralement `case` lorsqu'une variable correspond à plusieurs valeurs prédéfinies.

Ce sont des conventions de lisibilité, pas des règles absolues.


# 19. Les boucles

Une boucle permet de répéter des instructions sans écrire plusieurs fois le même code.

## 19.1. La boucle `for`

La forme la plus simple est :

```bash
for valeur in element1 element2 element3; do
    printf '%s\n' "$valeur"
done
```

La variable `valeur` prend successivement chacune des valeurs indiquées.

Exemple :

```bash
#!/usr/bin/env bash

for service in ssh cron nginx; do
    printf 'Service étudié : %s\n' "$service"
done
```

Cet exemple affiche les noms indiqués. Il ne vérifie pas si ces services sont installés ou actifs.

## 19.2. Répéter une opération sur plusieurs nombres

```bash
for nombre in 1 2 3 4 5; do
    printf 'Nombre : %s\n' "$nombre"
done
```

Bash propose aussi une expansion d'accolades :

```bash
for nombre in {1..5}; do
    printf 'Nombre : %s\n' "$nombre"
done
```

Cette forme est une fonctionnalité de Bash et ne doit pas être supposée disponible dans tous les shells.

## 19.3. La boucle `while`

`while` répète les instructions tant que sa condition réussit.

```bash
#!/usr/bin/env bash

compteur=1

while (( compteur <= 5 )); do
    printf 'Compteur : %d\n' "$compteur"
    compteur=$((compteur + 1))
done
```

Déroulement :

```text
Compteur = 1
     |
     v
Vérifier compteur <= 5
     |
     +-- vrai --> Afficher --> Ajouter 1 --> Recommencer
     |
     +-- faux --> Sortir de la boucle
```

Le compteur doit progresser. Sans changement de valeur, le script risque de produire une boucle infinie.

## 19.4. La boucle `until`

`until` répète des instructions jusqu'à ce que sa condition réussisse.

```bash
#!/usr/bin/env bash

compteur=1

until (( compteur > 5 )); do
    printf 'Compteur : %d\n' "$compteur"
    compteur=$((compteur + 1))
done
```

Le résultat est similaire à celui de la boucle `while` précédente. Seule la manière d'exprimer la condition change.

## 19.5. Parcourir des noms de fichiers

Pour parcourir les fichiers correspondant à un motif, on peut utiliser :

```bash
#!/usr/bin/env bash

for fichier in "$HOME"/lab-scripting/*.sh; do
    if [[ -f "$fichier" ]]; then
        printf 'Script trouvé : %s\n' "$fichier"
    fi
done
```

Pourquoi ce choix ?

- Le motif `*.sh` correspond aux noms de fichiers qui se terminent par `.sh` dans ce répertoire.
- Le préfixe `"$HOME"/` protège la partie contenant une variable.
- Le motif `*.sh` reste volontairement non cité pour permettre son expansion.
- Le test `-f` évite d'afficher un chemin qui ne correspondrait pas à un fichier ordinaire.

Si aucun nom ne correspond au motif, Bash peut conserver le motif littéral. Le test `-f` empêche alors de le traiter comme un fichier existant.

**Attention :** ne mettez pas `"$HOME/lab-scripting/*.sh"` entièrement entre guillemets, car le caractère `*` ne sera alors pas développé en une liste de fichiers.

## 19.6. Parcourir correctement une liste de noms

Évitez cette construction pour parcourir des noms de fichiers contenant éventuellement des espaces :

```bash
for fichier in $(ls); do
    printf '%s\n' "$fichier"
done
```

Elle peut découper les noms de fichiers et produire un résultat incorrect.

Pour une première approche, utilisez plutôt l'expansion de motif présentée précédemment. Pour des traitements plus avancés ou récursifs, `find` et les délimitations par caractères NUL sont des outils plus adaptés ; ils seront étudiés à un niveau plus avancé.


# 20. Les fonctions

Une fonction permet de donner un nom à un groupe d'instructions et de le réutiliser.

Elle facilite la lecture, limite les répétitions et sépare les responsabilités.

## 20.1. Déclarer une fonction

```bash
dire_bonjour() {
    printf 'Bonjour !\n'
}
```

La déclaration ne suffit pas pour exécuter le contenu. Il faut appeler la fonction :

```bash
dire_bonjour
```

Exemple complet :

```bash
#!/usr/bin/env bash

dire_bonjour() {
    printf 'Bonjour !\n'
}

dire_bonjour
dire_bonjour
```

La fonction est exécutée deux fois.

## 20.2. Passer des arguments à une fonction

Les fonctions Bash peuvent recevoir des arguments positionnels.

```bash
saluer() {
    local nom="$1"
    printf 'Bonjour %s !\n' "$nom"
}

saluer "Amina"
saluer "Paul"
```

Résultat :

```text
Bonjour Amina !
Bonjour Paul !
```

Le mot-clé `local` déclare une variable dont la portée est limitée à la fonction dans Bash.

## 20.3. Pourquoi utiliser `local` ?

Sans `local`, une affectation effectuée dans une fonction peut modifier une variable du shell englobant.

Avec :

```bash
afficher_nom() {
    local nom="Serveur de test"
    printf '%s\n' "$nom"
}
```

la variable `nom` est locale à cette fonction.

Cela réduit les effets inattendus et améliore la lisibilité.

## 20.4. Exemple de fonction de vérification

```bash
verifier_repertoire() {
    local chemin="$1"

    if [[ -d "$chemin" ]]; then
        printf 'OK : %s existe.\n' "$chemin"
    else
        printf 'ERREUR : %s est absent.\n' "$chemin" >&2
        return 1
    fi
}
```

Appel :

```bash
verifier_repertoire "$HOME/lab-scripting"
```

## 20.5. `return` et `exit`

Ces deux instructions n'ont pas le même rôle.

- `return` termine une fonction ou un fichier de script chargé dans le shell courant, selon le contexte, avec un statut ;
- `exit` termine le shell courant ou le processus exécutant le script.

Pour un contrôle dans une fonction, préférez généralement `return`.

Exemple :

```bash
verifier_nombre() {
    local valeur="$1"

    if [[ "$valeur" =~ ^[0-9]+$ ]]; then
        return 0
    else
        return 1
    fi
}

if verifier_nombre "123"; then
    printf 'Nombre valide selon cette règle.\n'
else
    printf 'Valeur invalide.\n'
fi
```

Le message précise que la valeur est valide selon cette règle : il s'agit ici d'une validation lexicale, pas d'une analyse complète de toutes les représentations numériques possibles.

## 20.6. Renvoyer un résultat : sortie ou statut ?

En Bash, `return` sert à renvoyer un code de statut compris dans la plage autorisée des statuts du shell. Il ne renvoie pas directement une chaîne de caractères.

Pour produire du texte, une fonction peut écrire sur la sortie standard :

```bash
nom_machine() {
    hostname
}

resultat="$(nom_machine)"
printf 'Machine : %s\n' "$resultat"
```

Pour signaler une réussite ou un échec, utilisez le code de retour :

```bash
est_fichier() {
    [[ -f "$1" ]]
}

if est_fichier "rapport.txt"; then
    printf 'Fichier reconnu.\n'
fi
```

Ce modèle sépare bien les deux besoins : retourner un texte et indiquer un statut.


# 21. Les tableaux Bash : première approche

Un tableau permet de conserver plusieurs valeurs sous un même nom.

Cette section est une introduction. La manipulation avancée des tableaux sera étudiée au niveau intermédiaire.

## 21.1. Déclarer un tableau indexé

```bash
services=("ssh" "cron" "nginx")
```

Les éléments disposent d'indices à partir de zéro.

Pour accéder au premier élément :

```bash
printf '%s\n' "${services[0]}"
```

Pour accéder au deuxième élément :

```bash
printf '%s\n' "${services[1]}"
```

## 21.2. Afficher les éléments

```bash
services=("ssh" "cron" "nginx")

for service in "${services[@]}"; do
    printf 'Service : %s\n' "$service"
done
```

L'expression `"${services[@]}"` permet de développer chaque élément du tableau comme un argument distinct.

Les guillemets conservent notamment les espaces contenus dans les éléments.

## 21.3. Connaître le nombre d'éléments

```bash
services=("ssh" "cron" "nginx")

printf 'Nombre de services : %s\n' "${#services[@]}"
```

Le résultat est `3`.

## 21.4. Tableau ou variable simple ?

Utilisez une variable simple pour une valeur unique :

```bash
nom_machine="serveur-lab"
```

Utilisez un tableau pour plusieurs valeurs :

```bash
machines=("serveur-lab-01" "serveur-lab-02" "serveur-lab-03")
```

N'utilisez pas une simple chaîne séparée par des espaces comme remplacement automatique d'un tableau si les valeurs peuvent elles-mêmes contenir des espaces.


# 22. Les redirections et les pipelines

Par défaut, les commandes utilisent généralement trois flux :

| Flux | Descripteur | Rôle |
|---|---:|---|
| Entrée standard | `0` | recevoir une entrée |
| Sortie standard | `1` | produire un résultat normal |
| Sortie d'erreur standard | `2` | produire un message d'erreur |

## 22.1. Rediriger la sortie standard

L'opérateur `>` redirige la sortie standard vers un fichier et remplace normalement son contenu s'il existe déjà.

```bash
printf 'Rapport de laboratoire\n' > "$HOME/lab-scripting/rapports/rapport.txt"
```

L'opérateur `>>` ajoute du texte à la fin du fichier :

```bash
printf 'Contrôle terminé\n' >> "$HOME/lab-scripting/rapports/rapport.txt"
```

La différence est importante :

```text
>   remplace le contenu existant
>>  ajoute du contenu à la fin
```

Évitez d'utiliser `>` sur un fichier important sans avoir vérifié les conséquences. Il peut effacer immédiatement son ancien contenu.

## 22.2. Rediriger les erreurs

Pour envoyer un message d'erreur vers la sortie d'erreur :

```bash
printf 'Erreur : opération impossible.\n' >&2
```

Pour enregistrer uniquement les erreurs d'une commande :

```bash
commande_inexistante 2> "$HOME/lab-scripting/erreurs.txt"
```

Cette instruction utilise volontairement une commande inexistante pour démontrer la redirection. L'erreur peut être enregistrée dans le fichier.

Dans un script réel, utilisez une commande qui correspond à l'opération à effectuer.

## 22.3. Rediriger la sortie et les erreurs

Pour enregistrer la sortie standard et la sortie d'erreur dans un même fichier :

```bash
commande_de_test > "$HOME/lab-scripting/journal.txt" 2>&1
```

L'ordre des redirections compte. Cette forme redirige d'abord la sortie standard vers le fichier, puis fait pointer la sortie d'erreur vers la destination actuelle de la sortie standard.

La forme suivante est également courante en Bash :

```bash
commande_de_test &> "$HOME/lab-scripting/journal.txt"
```

Elle constitue une syntaxe Bash ; ne la supposez pas compatible avec tous les shells.

## 22.4. Utiliser un pipeline

Le symbole `|` transmet la sortie standard d'une commande vers l'entrée standard de la suivante.

Exemple :

```bash
hostname | tr '[:lower:]' '[:upper:]'
```

Le nom de la machine est transmis à `tr`, qui convertit les lettres minuscules en majuscules.

Autre exemple :

```bash
printf '%s\n' "pomme" "banane" "orange" | sort
```

Le résultat est trié alphabétiquement.

Schéma :

```text
Commande A
    |
    | sortie standard
    v
  Pipeline
    |
    v
Commande B
    |
    v
Résultat final
```

Un pipeline peut comporter plusieurs commandes :

```bash
commande_a | commande_b | commande_c
```

Les pipelines sont puissants, mais le code de retour d'un pipeline peut nécessiter des précautions. Par défaut, son statut correspond généralement à celui de la dernière commande, et non nécessairement à celui de toutes les commandes précédentes.

Bash offre l'option `pipefail` pour modifier ce comportement. Son emploi sera présenté dans le chapitre consacré à la fiabilité.


# 23. Le traitement simple de fichiers et de listes

## 23.1. Compter les fichiers d'un répertoire

Pour un répertoire de laboratoire dont vous connaissez le contenu :

```bash
ls -1 "$HOME/lab-scripting"
```

Affiche les entrées du répertoire sur plusieurs lignes.

Attention : l'option `-1` affiche une entrée par ligne, mais analyser la sortie de `ls` dans un script n'est pas une méthode robuste pour manipuler tous les noms de fichiers. Un nom de fichier peut notamment contenir un retour à la ligne.

Pour des contrôles simples, utilisez les constructions Bash et les tests de fichiers. Pour des traitements complexes, utilisez des outils conçus pour parcourir les entrées de répertoire sans ambiguïté.

## 23.2. Vérifier des fichiers connus

```bash
#!/usr/bin/env bash

for fichier in \
    "$HOME/lab-scripting/01-premier-script.sh" \
    "$HOME/lab-scripting/02-variables.sh"
do
    if [[ -f "$fichier" ]]; then
        printf 'PRÉSENT : %s\n' "$fichier"
    else
        printf 'ABSENT : %s\n' "$fichier"
    fi
done
```

Cette approche permet de tester une liste explicite de chemins.

## 23.3. Lire un fichier ligne par ligne

La construction classique suivante permet de lire les lignes d'un fichier :

```bash
#!/usr/bin/env bash

fichier="$HOME/lab-scripting/liste.txt"

if [[ ! -f "$fichier" ]]; then
    printf 'Erreur : fichier absent.\n' >&2
    exit 1
fi

while IFS= read -r ligne || [[ -n "$ligne" ]]; do
    printf 'Ligne : %s\n' "$ligne"
done < "$fichier"
```

Comprendre les éléments importants :

- `while` répète la lecture ;
- `IFS=` évite le découpage automatique de la ligne selon les espaces ;
- `read -r` évite que les antislashs soient interprétés comme des échappements ;
- `< "$fichier"` redirige le contenu du fichier vers l'entrée standard de la boucle ;
- `|| [[ -n "$ligne" ]]` permet de traiter aussi une dernière ligne non terminée par un retour à la ligne.

Cette méthode convient à de nombreux fichiers texte simples. Elle ne remplace pas un véritable parseur pour les formats complexes comme JSON, XML ou CSV avec champs entre guillemets.

## 23.4. Créer un fichier d'exemple

```bash
cat > "$HOME/lab-scripting/liste.txt" <<'EOF'
serveur-lab-01
serveur-lab-02
serveur-lab-03
EOF
```

Cette syntaxe utilise un *here-document*.

Le marqueur `EOF` n'est pas une commande spéciale : il délimite le texte envoyé à `cat`. Lorsqu'il est entouré de guillemets simples dans `<<'EOF'`, le contenu est traité littéralement, sans expansion ordinaire des variables ou substitutions de commande.

Pour débuter, vous pouvez utiliser cette méthode afin de préparer des fichiers de test.


# 24. Les bonnes pratiques de sécurité

Un script d'administration peut manipuler des données, des fichiers et parfois des services critiques. Il est donc important d'adopter de bonnes habitudes dès le niveau débutant.

## 24.1. Ne pas exécuter systématiquement les scripts avec `sudo`

N'écrivez pas un script de laboratoire en partant du principe qu'il doit être lancé avec les privilèges administrateur.

Un script doit être exécuté avec les permissions minimales nécessaires à sa tâche.

Un script qui affiche simplement la date ne nécessite pas `sudo`.

```bash
#!/usr/bin/env bash

date
```

Exécutez-le normalement :

```bash
bash date.sh
```

Les privilèges administrateur ne doivent être ajoutés que lorsqu'une opération précise les exige et que ses conséquences sont comprises.

## 24.2. Éviter les commandes destructives au début

Les commandes `rm`, `mv`, `chmod` et certaines commandes de gestion de services peuvent modifier significativement le système.

Avant toute opération destructive, vérifiez :

- le chemin ciblé ;
- la valeur des variables utilisées ;
- le type de fichier concerné ;
- les droits effectifs ;
- la possibilité de restaurer les données.

N'utilisez jamais un chemin calculé sans vérification dans une commande destructive.

Exemple de contrôle préalable :

```bash
cible="$HOME/lab-scripting/rapport-a-supprimer.txt"

printf 'Cible sélectionnée : %s\n' "$cible"

if [[ -f "$cible" ]]; then
    printf 'Un fichier ordinaire existe à cet emplacement.\n'
else
    printf 'Le fichier ciblé est absent ou n’est pas un fichier ordinaire.\n'
fi
```

Ce code ne supprime rien. Il sert à illustrer la vérification préalable.

## 24.3. Ne pas utiliser `eval` pour les entrées utilisateur

`eval` demande au shell de réinterpréter un texte comme du code shell.

Une entrée apparemment anodine peut alors devenir une instruction inattendue.

À éviter :

```bash
# À ne pas utiliser pour interpréter une saisie utilisateur.
# eval "$saisie"
```

Pour choisir une action, utilisez plutôt `case`, `if` ou une liste de valeurs autorisées.

Exemple :

```bash
case "$choix" in
    date)
        date
        ;;
    machine)
        hostname
        ;;
    *)
        printf 'Action non autorisée.\n' >&2
        exit 1
        ;;
esac
```

Le script ne transforme pas une chaîne arbitraire en code exécutable.

## 24.4. Protéger les variables de chemins

Préférez :

```bash
mkdir -p "$repertoire"
```

à :

```bash
mkdir -p $repertoire
```

Les guillemets permettent de préserver un chemin contenant des espaces.

Utilisez également `--` lorsqu'une commande compatible accepte cette convention et qu'un chemin pourrait commencer par un tiret.

Exemple :

```bash
rm -- "$fichier"
```

`--` indique à la commande que les options sont terminées. Il ne rend pas la suppression moins destructive et ne remplace pas la validation du chemin.

## 24.5. Éviter les hypothèses cachées

Un script doit traiter les cas prévisibles :

- fichier absent ;
- argument manquant ;
- valeur vide ;
- commande non disponible ;
- répertoire non accessible ;
- opération qui échoue.

Exemple :

```bash
#!/usr/bin/env bash

if ! command -v hostname >/dev/null 2>&1; then
    printf 'Erreur : hostname est indisponible.\n' >&2
    exit 1
fi

if ! nom_machine="$(hostname)"; then
    printf 'Erreur : impossible de lire le nom de la machine.\n' >&2
    exit 1
fi

printf 'Machine : %s\n' "$nom_machine"
```

`>/dev/null 2>&1` redirige la sortie standard et la sortie d'erreur de `command -v` vers le périphérique qui ignore les données.

Cette vérification préalable n'est pas toujours nécessaire pour les commandes de base, mais elle est utile lorsque la disponibilité d'un outil est incertaine.


# 25. Le débogage et les outils de contrôle

Écrire un script ne suffit pas : il faut aussi le tester et comprendre les erreurs.

## 25.1. Lire les messages d'erreur

Une erreur peut signaler :

- une faute de syntaxe ;
- un fichier absent ;
- une permission insuffisante ;
- une commande inconnue ;
- un argument incorrect ;
- une variable mal utilisée.

Exemple volontairement incorrect :

```bash
#!/usr/bin/env bash

if [[ -f "rapport.txt" ]
then
    printf 'Fichier présent.\n'
fi
```

Il manque un crochet fermant dans la condition.

Bash signale une erreur de syntaxe au lieu d'exécuter correctement le bloc.

Version corrigée :

```bash
#!/usr/bin/env bash

if [[ -f "rapport.txt" ]]; then
    printf 'Fichier présent.\n'
fi
```

## 25.2. Vérifier la syntaxe sans exécuter normalement le script

Utilisez :

```bash
bash -n 01-premier-script.sh
```

`-n` demande à Bash de lire et contrôler la syntaxe sans exécuter normalement les commandes du script.

Si aucune erreur n'est détectée, Bash ne produit généralement aucun message.

Cela ne garantit pas que le script fonctionnera correctement à l'exécution. Les erreurs de logique, les fichiers absents et les problèmes de permissions peuvent subsister.

## 25.3. Afficher les commandes exécutées

Utilisez temporairement :

```bash
bash -x 01-premier-script.sh
```

L'option `-x` active le mode de traçage. Bash affiche les commandes développées avant leur exécution.

Cette méthode aide à suivre les expansions des variables et l'ordre des instructions.

**Attention :** le traçage peut afficher des données sensibles présentes dans les arguments ou les variables. Ne l'utilisez pas sans précaution sur un script qui manipule des secrets.

## 25.4. Utiliser `set -u`

L'option :

```bash
set -u
```

demande à Bash de signaler les expansions de certaines variables non définies au lieu de les traiter silencieusement comme des valeurs vides.

Cela peut aider à repérer les fautes de nommage, mais modifie le comportement du script. Il faut tester les chemins qui utilisent des variables optionnelles.

Par exemple :

```bash
#!/usr/bin/env bash

set -u

nom="Amina"
printf 'Bonjour %s\n' "$nom"
```

Dans un script utilisant cette option, une variable non définie peut provoquer une terminaison anticipée.

Pour les valeurs optionnelles, vous pouvez fournir une valeur par défaut :

```bash
nom="${NOM_UTILISATEUR:-Invité}"
```

## 25.5. Comprendre `set -e`

On rencontre fréquemment :

```bash
set -e
```

Cette option demande généralement à Bash de terminer lorsqu'une commande échoue dans de nombreux contextes. Cependant, ses règles comportent des exceptions, notamment dans les conditions, les listes de commandes et les pipelines.

Elle ne doit pas être comprise comme une garantie universelle de gestion des erreurs.

Une vérification explicite reste souvent plus lisible :

```bash
if ! mkdir -p "$HOME/lab-scripting/rapports"; then
    printf 'Impossible de préparer les rapports.\n' >&2
    exit 1
fi
```

Dans ce cours, nous privilégions les vérifications explicites avant de présenter une stratégie globale de gestion d'erreurs.

## 25.6. Comprendre `set -o pipefail`

Par défaut, le statut d'un pipeline comme :

```bash
commande_a | commande_b
```

reflète généralement le statut de la dernière commande.

Avec :

```bash
set -o pipefail
```

le pipeline peut signaler l'échec d'une commande située plus tôt dans la chaîne.

Exemple :

```bash
#!/usr/bin/env bash

set -o pipefail

false | cat

printf 'Statut du pipeline : %s\n' "$?"
```

Avec `pipefail`, le pipeline renvoie ici un statut non nul. Sans cette option, `cat` pourrait réussir et masquer l'échec de `false`.

Cette option ne remplace pas les vérifications des opérations critiques.

## 25.7. Faut-il toujours écrire `set -euo pipefail` ?

Non. Cette combinaison est fréquente dans certains scripts Bash, mais elle modifie la façon dont les erreurs et les variables sont traitées.

Avant de l'utiliser, comprenez :

- les effets de `-e` ;
- la détection des variables non définies avec `-u` ;
- le comportement des pipelines avec `pipefail` ;
- les valeurs optionnelles et les cas d'échec attendus.

Une configuration robuste dépend du comportement souhaité. Aucun ensemble d'options ne remplace une conception et des tests corrects.

## 25.8. Vérifier un script avec ShellCheck

ShellCheck est un outil d'analyse statique destiné aux scripts shell. Il détecte de nombreux problèmes fréquents, notamment des erreurs de citation et des constructions suspectes.

Après installation via le gestionnaire de paquets approprié à votre distribution, vous pouvez lancer :

```bash
shellcheck 01-premier-script.sh
```

Si ShellCheck propose des avertissements, lisez-les et comprenez leur signification avant de modifier le script.

Une suggestion d'analyse statique n'est pas automatiquement applicable dans tous les contextes. Il faut toujours vérifier que la correction conserve le comportement souhaité.


# 26. TP guidés

Ces travaux pratiques permettent de réutiliser les concepts dans des situations concrètes.

Toutes les opérations doivent se dérouler dans le répertoire de laboratoire. Aucun des TP ne nécessite de privilèges administrateur.

## TP 1 — Premier script d'information système

### Objectif

Écrire un script qui affiche la date, la machine et l'utilisateur courant.

### Étape 1 : créer le fichier

```bash
cd "$HOME/lab-scripting"
nano informations-systeme.sh
```

Contenu :

```bash
#!/usr/bin/env bash

printf '%s\n' "=== Informations système ==="
printf 'Date : %s\n' "$(date)"
printf 'Machine : %s\n' "$(hostname)"
printf 'Utilisateur : %s\n' "$(whoami)"
```

### Étape 2 : vérifier la syntaxe

```bash
bash -n informations-systeme.sh
```

### Étape 3 : exécuter le script

```bash
bash informations-systeme.sh
```

### Résultat attendu

Les valeurs exactes dépendent de votre machine et de l'heure d'exécution. L'organisation générale du rapport doit ressembler à ceci :

```text
=== Informations système ===
Date : ...
Machine : ...
Utilisateur : ...
```

### Compétences mobilisées

- création d'un script ;
- affichage formaté ;
- substitution de commande ;
- lecture et contrôle de la syntaxe.


## TP 2 — Calculer avec des variables

### Objectif

Créer un script qui demande deux entiers positifs ou nuls et affiche leur somme.

### Script

Enregistrez le fichier sous `calculatrice-simple.sh`.

```bash
#!/usr/bin/env bash

read -r -p "Premier entier : " premier
read -r -p "Deuxième entier : " deuxieme

if [[ ! "$premier" =~ ^[0-9]+$ || ! "$deuxieme" =~ ^[0-9]+$ ]]; then
    printf 'Erreur : veuillez saisir deux entiers positifs ou nuls.\n' >&2
    exit 1
fi

somme=$((premier + deuxieme))

printf 'La somme de %s et %s vaut %s.\n' \
    "$premier" "$deuxieme" "$somme"
```

### Vérification

Exemple :

```text
Premier entier : 12
Deuxième entier : 8
La somme de 12 et 8 vaut 20.
```

Testez également les cas suivants :

- `0` et `5` ;
- `10` et `20` ;
- `abc` et `20` ;
- une chaîne vide.

Les deux premiers doivent produire une somme. Les deux derniers doivent déclencher le message d'erreur.

### Point d'attention

Ce script convient à de petits entiers. Il ne met pas en place de contrôle des dépassements arithmétiques et ne convient pas à des calculs de précision financière.


## TP 3 — Contrôler des répertoires

### Objectif

Écrire un script qui examine plusieurs répertoires définis dans une liste.

### Préparer le laboratoire

```bash
mkdir -p "$HOME/lab-scripting/donnees"
mkdir -p "$HOME/lab-scripting/rapports"
```

### Script

Fichier : `controle-repertoires.sh`

```bash
#!/usr/bin/env bash

repertoires=(
    "$HOME/lab-scripting"
    "$HOME/lab-scripting/donnees"
    "$HOME/lab-scripting/rapports"
    "$HOME/lab-scripting/inexistant"
)

for repertoire in "${repertoires[@]}"; do
    if [[ -d "$repertoire" ]]; then
        printf 'OK      : %s\n' "$repertoire"
    else
        printf 'ABSENT  : %s\n' "$repertoire"
    fi
done
```

### Résultat attendu

Les trois premiers répertoires doivent normalement être trouvés après la préparation du laboratoire. Le dernier doit apparaître comme absent, sauf si vous l'avez déjà créé.

### Compétences mobilisées

- tableaux Bash ;
- boucle `for` ;
- condition `if` ;
- test `-d` ;
- utilisation de chemins absolus issus de `$HOME`.


## TP 4 — Générer un rapport dans un fichier

### Objectif

Produire un rapport texte enregistré dans le répertoire `rapports`.

### Script

Fichier : `generer-rapport.sh`

```bash
#!/usr/bin/env bash

repertoire="$HOME/lab-scripting/rapports"
fichier_rapport="$repertoire/rapport-systeme.txt"

if ! mkdir -p "$repertoire"; then
    printf 'Erreur : impossible de préparer le répertoire.\n' >&2
    exit 1
fi

{
    printf '%s\n' "=== Rapport système ==="
    printf 'Date : %s\n' "$(date)"
    printf 'Machine : %s\n' "$(hostname)"
    printf 'Utilisateur : %s\n' "$(whoami)"
} > "$fichier_rapport" || {
    printf 'Erreur : impossible d’écrire le rapport.\n' >&2
    exit 1
}

printf 'Rapport créé : %s\n' "$fichier_rapport"
```

### Exécution

```bash
bash generer-rapport.sh
```

Puis vérifiez le contenu :

```bash
cat "$HOME/lab-scripting/rapports/rapport-systeme.txt"
```

### Pourquoi les accolades sont-elles utilisées ?

Le groupe :

```bash
{
    commande1
    commande2
    commande3
}
```

permet de rediriger les sorties des commandes groupées vers le même fichier.

Dans ce cas, `>` remplace le contenu précédent du rapport à chaque exécution.


# 27. Exercices corrigés

Essayez d'abord de résoudre chaque exercice sans consulter immédiatement sa correction.

## Exercice 1 — Afficher une identité

**Énoncé :** écrivez un script qui déclare les variables `prenom` et `ville` puis affiche une phrase indiquant le prénom et la ville.

### Correction

```bash
#!/usr/bin/env bash

prenom="Amina"
ville="Douala"

printf '%s habite à %s.\n' "$prenom" "$ville"
```

**Explication :** les affectations n'ont pas d'espaces autour de `=` et les expansions des variables sont mises entre guillemets doubles.

## Exercice 2 — Recevoir un argument

**Énoncé :** écrivez un script qui accepte un nom en premier argument. S'il manque, utilisez `Invité`.

### Correction

```bash
#!/usr/bin/env bash

nom="${1:-Invité}"

printf 'Bonjour %s !\n' "$nom"
```

**Explication :** `${1:-Invité}` utilise `Invité` lorsque le premier argument est absent ou vide.

## Exercice 3 — Vérifier un fichier

**Énoncé :** vérifiez que `rapport.txt` existe dans le répertoire courant et affichez un message adapté.

### Correction

```bash
#!/usr/bin/env bash

fichier="rapport.txt"

if [[ -f "$fichier" ]]; then
    printf 'Le fichier existe.\n'
else
    printf 'Le fichier est absent ou n’est pas un fichier ordinaire.\n'
fi
```

**Explication :** `-f` vérifie qu'un fichier ordinaire existe au chemin donné.

## Exercice 4 — Classer une valeur

**Énoncé :** demandez un entier positif ou nul, puis indiquez si sa valeur est inférieure à 100 ou supérieure ou égale à 100.

### Correction

```bash
#!/usr/bin/env bash

read -r -p "Saisissez un entier positif ou nul : " nombre

if [[ ! "$nombre" =~ ^[0-9]+$ ]]; then
    printf 'Valeur invalide.\n' >&2
    exit 1
fi

if (( nombre < 100 )); then
    printf 'La valeur est inférieure à 100.\n'
else
    printf 'La valeur est supérieure ou égale à 100.\n'
fi
```

**Explication :** le script valide la saisie avant de procéder à une comparaison arithmétique.

## Exercice 5 — Compter de 1 à 10

**Énoncé :** utilisez `for` pour afficher les nombres de 1 à 10.

### Correction

```bash
#!/usr/bin/env bash

for nombre in {1..10}; do
    printf '%s\n' "$nombre"
done
```

**Explication :** `{1..10}` est une expansion d'accolades prise en charge par Bash.

## Exercice 6 — Répéter jusqu'à la bonne réponse

**Énoncé :** demandez à l'utilisateur de saisir `oui` jusqu'à ce qu'il le fasse. Le script doit accepter `oui` et `non` comme réponses connues, mais répéter la demande tant que la réponse n'est pas `oui`.

### Correction

```bash
#!/usr/bin/env bash

while true; do
    read -r -p "Saisissez oui pour terminer : " reponse

    case "$reponse" in
        oui)
            printf 'Réponse validée.\n'
            break
            ;;
        non)
            printf 'La confirmation est toujours attendue.\n'
            ;;
        *)
            printf 'Réponse non reconnue.\n'
            ;;
    esac
done
```

**Explication :** `while true` crée une boucle répétée jusqu'à ce qu'une instruction `break` en sorte. Le programme attend explicitement `oui`.

## Exercice 7 — Écrire une fonction

**Énoncé :** écrivez une fonction `afficher_machine` qui affiche le nom de la machine. Appelez-la deux fois.

### Correction

```bash
#!/usr/bin/env bash

afficher_machine() {
    hostname
}

afficher_machine
afficher_machine
```

**Explication :** une fonction n'est exécutée que lorsqu'elle est appelée. Cette version peut effectuer deux appels distincts à `hostname`.

## Exercice 8 — Comprendre un code de retour

**Énoncé :** écrivez un script qui vérifie si un chemin fourni en argument est un répertoire. Renvoyez `0` si c'est le cas et `1` sinon.

### Correction

```bash
#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s CHEMIN\n' "$0" >&2
    exit 2
fi

if [[ -d "$1" ]]; then
    printf 'Répertoire reconnu.\n'
    exit 0
else
    printf 'Chemin absent ou non répertoire.\n' >&2
    exit 1
fi
```

**Explication :** le script choisit ici `2` pour signaler une erreur d'utilisation, `0` pour la réussite et `1` pour le cas où le chemin ne correspond pas à un répertoire. Ces codes sont une convention propre à ce script.

## Exercice 9 — Corriger une mauvaise pratique

**Énoncé :** corrigez le code suivant pour qu'il traite correctement un nom de fichier contenant des espaces.

```bash
#!/usr/bin/env bash

fichier="rapport de test.txt"
cat $fichier
```

### Correction

```bash
#!/usr/bin/env bash

fichier="rapport de test.txt"

if [[ -f "$fichier" ]]; then
    cat -- "$fichier"
else
    printf 'Fichier absent : %s\n' "$fichier" >&2
    exit 1
fi
```

**Explication :** les guillemets conservent le chemin en un seul argument. `--` termine l'interprétation des options pour `cat`.

## Exercice 10 — Identifier une erreur

**Énoncé :** pourquoi le script suivant est-il incorrect ?

```bash
#!/usr/bin/env bash

nom = "Amina"
echo "$nom"
```

### Correction

```bash
#!/usr/bin/env bash

nom="Amina"
printf '%s\n' "$nom"
```

**Explication :** une affectation Bash simple ne doit pas contenir d'espaces autour de `=`.

## Exercice 11 — Lire un fichier ligne par ligne

**Énoncé :** affichez chaque ligne du fichier `liste.txt` sous la forme `Élément : ...`.

### Correction

```bash
#!/usr/bin/env bash

fichier="$HOME/lab-scripting/liste.txt"

if [[ ! -f "$fichier" ]]; then
    printf 'Fichier absent.\n' >&2
    exit 1
fi

while IFS= read -r ligne || [[ -n "$ligne" ]]; do
    printf 'Élément : %s\n' "$ligne"
done < "$fichier"
```

**Explication :** la boucle conserve le contenu des lignes sans découper les champs sur les espaces et traite également une dernière ligne sans retour à la ligne final.

## Exercice 12 — Comprendre une substitution

**Énoncé :** expliquez ce que fait la commande suivante :

```bash
machine="$(hostname)"
```

### Correction

Cette commande exécute `hostname`, récupère sa sortie standard et l'affecte à la variable `machine`. Les retours à la ligne terminaux sont retirés par le mécanisme de substitution de commande.

Le code de retour de la commande est distinct du texte récupéré.


# 28. Défi final — Créer un outil de contrôle de répertoires

## 28.1. Contexte

Vous êtes un administrateur Linux débutant. Vous souhaitez disposer d'un petit outil capable d'examiner des répertoires, de produire un rapport et de signaler les chemins absents.

Le programme ne doit pas modifier les fichiers contrôlés.

## 28.2. Cahier des charges

Le script doit :

1. recevoir un ou plusieurs chemins en arguments ;
2. afficher une erreur d'utilisation si aucun chemin n'est fourni ;
3. afficher une date de contrôle ;
4. vérifier chaque chemin ;
5. distinguer les répertoires existants des autres cas ;
6. compter le nombre de répertoires présents et absents ;
7. enregistrer le rapport dans un fichier situé sous `"$HOME/lab-scripting/rapports"` ;
8. retourner un statut non nul si au moins un chemin n'est pas un répertoire ;
9. conserver les chemins comportant des espaces ;
10. ne jamais supprimer ou modifier les chemins contrôlés.

## 28.3. Travail demandé

Créez `controle-complet.sh`.

Avant d'examiner la correction :

- définissez les variables nécessaires ;
- prévoyez une fonction pour traiter chaque chemin ;
- utilisez une boucle pour parcourir les arguments ;
- enregistrez le résultat dans le rapport ;
- choisissez un code de retour cohérent.

## 28.4. Correction complète

```bash
#!/usr/bin/env bash

# Fichier : controle-complet.sh
# Objectif : contrôler des répertoires et générer un rapport.
# Usage : ./controle-complet.sh CHEMIN [CHEMIN...]

set -u

if [[ $# -lt 1 ]]; then
    printf 'Usage : %s CHEMIN [CHEMIN...]\n' "$0" >&2
    exit 2
fi

repertoire_rapports="$HOME/lab-scripting/rapports"
date_controle="$(date '+%Y-%m-%d %H:%M:%S')" || {
    printf 'Erreur : impossible de récupérer la date.\n' >&2
    exit 1
}

if ! mkdir -p "$repertoire_rapports"; then
    printf 'Erreur : impossible de préparer le répertoire des rapports.\n' >&2
    exit 1
fi

fichier_rapport="$repertoire_rapports/controle-repertoires.txt"

presents=0
absents=0

verifier_repertoire() {
    local chemin="$1"

    if [[ -d "$chemin" ]]; then
        printf 'PRÉSENT : %s\n' "$chemin"
        presentes=$((presentes + 1))
        return 0
    else
        printf 'ABSENT  : %s\n' "$chemin"
        absents=$((absents + 1))
        return 1
    fi
}

{
    printf '%s\n' "=== Rapport de contrôle des répertoires ==="
    printf 'Date du contrôle : %s\n' "$date_controle"
    printf 'Nombre de chemins contrôlés : %s\n' "$#"
    printf '\n'
} > "$fichier_rapport" || {
    printf 'Erreur : impossible de créer le rapport.\n' >&2
    exit 1
}

for chemin in "$@"; do
    if verifier_repertoire "$chemin"; then
        resultat="PRÉSENT"
    else
        resultat="ABSENT"
    fi

    if ! printf '%s : %s\n' "$resultat" "$chemin" >> "$fichier_rapport"; then
        printf 'Erreur : impossible de compléter le rapport.\n' >&2
        exit 1
    fi
done

{
    printf '\n'
    printf 'Nombre de répertoires présents : %s\n' "$presents"
    printf 'Nombre de chemins absents ou non répertoires : %s\n' "$absents"
} >> "$fichier_rapport" || {
    printf 'Erreur : impossible de finaliser le rapport.\n' >&2
    exit 1
}

printf '\nRésumé :\n'
printf 'Présents : %s\n' "$presents"
printf 'Absents ou non répertoires : %s\n' "$absents"
printf 'Rapport : %s\n' "$fichier_rapport"

if (( absents > 0 )); then
    exit 1
fi

exit 0
```

## 28.5. Comment fonctionne cette correction ?

### Étape 1 : validation des arguments

```bash
if [[ $# -lt 1 ]]; then
```

Le script refuse de continuer si aucun chemin n'a été fourni.

### Étape 2 : préparation du rapport

```bash
mkdir -p "$repertoire_rapports"
```

Le répertoire est préparé avant les écritures.

### Étape 3 : contrôle individuel

La fonction `verifier_repertoire` utilise `-d` pour déterminer si le chemin désigne un répertoire accessible comme tel dans le contexte du test.

Elle incrémente ensuite un compteur et renvoie un statut.

### Étape 4 : parcours des arguments

```bash
for chemin in "$@"; do
```

Les guillemets autour de `"$@"` conservent les arguments séparés, y compris lorsqu'ils contiennent des espaces.

### Étape 5 : création du rapport

Le fichier reçoit une ligne pour chaque chemin, puis un résumé final.

Attention : ce script remplace le rapport existant au début de chaque exécution. Il ne supprime pas les répertoires contrôlés.

### Étape 6 : code de retour final

Le script renvoie `1` lorsque le compteur `absents` est supérieur à zéro. Il renvoie `0` si tous les chemins correspondent à des répertoires.

Un code `2` signale ici une erreur d'utilisation. Le sens des codes est défini par le programme ; les scripts appelants doivent connaître cette convention.

## 28.6. Tester le défi

Créez des répertoires de test :

```bash
mkdir -p "$HOME/lab-scripting/serveur A"
mkdir -p "$HOME/lab-scripting/serveur B"
```

Vérifiez deux répertoires existants :

```bash
bash controle-complet.sh \
    "$HOME/lab-scripting/serveur A" \
    "$HOME/lab-scripting/serveur B"
```

Le script devrait finir avec le statut `0` si les deux répertoires existent et que toutes les opérations de rapport réussissent.

Testez un cas où un chemin est absent :

```bash
bash controle-complet.sh \
    "$HOME/lab-scripting/serveur A" \
    "$HOME/lab-scripting/serveur inexistant"
```

Dans ce cas, le script doit signaler le chemin absent et retourner `1`, sauf si une autre erreur empêche le traitement.

Consultez le rapport :

```bash
cat "$HOME/lab-scripting/rapports/controle-repertoires.txt"
```

Pour afficher le code de retour de la commande que vous venez d'exécuter :

```bash
printf 'Code de retour : %s\n' "$?"
```

Cette dernière commande doit être saisie immédiatement après le lancement du script si vous souhaitez examiner son statut.

## 28.7. Limites assumées du défi

Ce programme est conçu pour un laboratoire de débutant. Il ne gère pas encore tous les cas d'une application d'administration de production.

Par exemple :

- il n'effectue pas un contrôle atomique de l'état des répertoires ;
- il ne crée pas un historique de rapports horodatés ;
- il ne valide pas la longueur ou la politique des chemins reçus ;
- il ne garantit pas la détection de toutes les erreurs d'écriture dans un système de fichiers inhabituel ;
- il ne gère pas un environnement hostile dans lequel d'autres processus changent les fichiers ou les chemins simultanément.

Il constitue néanmoins un bon exercice de synthèse sur les arguments, les variables, les fonctions, les boucles, les conditions et les codes de retour.


# 29. Liste de compétences

Cochez chaque compétence seulement lorsque vous pouvez la démontrer sans recopier mécaniquement une correction.

## Fondamentaux

- [ ] Je sais expliquer la différence entre un shell et un script.
- [ ] Je sais identifier Bash et vérifier sa version.
- [ ] Je sais créer un fichier `.sh`.
- [ ] Je sais expliquer le rôle du shebang.
- [ ] Je sais lancer un script avec `bash fichier.sh`.
- [ ] Je sais ajouter le droit d'exécution et lancer le script directement.

## Variables et données

- [ ] Je sais déclarer une variable sans mettre d'espaces autour de `=`.
- [ ] Je sais afficher une variable avec `printf`.
- [ ] Je sais expliquer la différence entre guillemets simples et doubles.
- [ ] Je sais préserver les noms de fichiers comportant des espaces.
- [ ] Je sais utiliser `$1`, `$2`, `$#` et `"$@"`.
- [ ] Je sais lire une saisie avec `read -r`.
- [ ] Je sais récupérer la sortie d'une commande avec `$(...)`.

## Logique du programme

- [ ] Je sais écrire un `if`, un `elif` et un `else`.
- [ ] Je sais tester un fichier avec `-f`.
- [ ] Je sais tester un répertoire avec `-d`.
- [ ] Je sais comparer des entiers avec `(( ... ))`.
- [ ] Je sais écrire un `case`.
- [ ] Je sais créer une boucle `for`.
- [ ] Je sais créer une boucle `while`.
- [ ] Je sais créer et appeler une fonction.
- [ ] Je sais employer `return` dans une fonction.

## Fiabilité

- [ ] Je sais utiliser les codes de retour.
- [ ] Je sais rediriger la sortie standard.
- [ ] Je sais rediriger les erreurs avec `>&2`.
- [ ] Je sais vérifier la syntaxe avec `bash -n`.
- [ ] Je sais déboguer avec `bash -x`.
- [ ] Je sais pourquoi les expansions de variables doivent généralement être citées.
- [ ] Je sais pourquoi `eval` est dangereux avec des entrées non fiables.
- [ ] Je sais analyser les suggestions de ShellCheck.

Si plusieurs compétences restent difficiles, reprenez les chapitres correspondants et répétez les TP avant de poursuivre au niveau intermédiaire.


# 30. Fiche de révision

## Créer et lancer un script

```bash
nano script.sh
bash script.sh
chmod u+x script.sh
./script.sh
```

## Déclarer et afficher une variable

```bash
nom="Amina"
printf 'Bonjour %s\n' "$nom"
```

## Recevoir un argument

```bash
nom="${1:-Invité}"
printf 'Nom : %s\n' "$nom"
```

## Demander une saisie

```bash
read -r -p "Votre nom : " nom
printf 'Nom : %s\n' "$nom"
```

## Récupérer une sortie de commande

```bash
machine="$(hostname)"
printf 'Machine : %s\n' "$machine"
```

## Vérifier un fichier ou un répertoire

```bash
if [[ -f "$fichier" ]]; then
    printf 'Fichier présent.\n'
fi

if [[ -d "$repertoire" ]]; then
    printf 'Répertoire présent.\n'
fi
```

## Faire un choix

```bash
if [[ "$choix" == "oui" ]]; then
    printf 'Choix accepté.\n'
else
    printf 'Choix différent.\n'
fi
```

## Utiliser une boucle

```bash
for nombre in {1..5}; do
    printf '%s\n' "$nombre"
done
```

## Définir une fonction

```bash
dire_bonjour() {
    local nom="$1"
    printf 'Bonjour %s\n' "$nom"
}

dire_bonjour "Amina"
```

## Rediriger la sortie et les erreurs

```bash
commande > sortie.txt
commande >> sortie.txt
commande 2> erreurs.txt
commande > journal.txt 2>&1
```

## Contrôler et déboguer

```bash
bash -n script.sh
bash -x script.sh
shellcheck script.sh
```

## Terminer avec un statut explicite

```bash
exit 0
```

Pour signaler un échec :

```bash
exit 1
```

## Règles à retenir absolument

1. Un script Bash commence généralement par un shebang adapté à son environnement.
2. Une affectation simple s'écrit `nom="valeur"`, sans espaces autour de `=`.
3. Les expansions de variables doivent généralement être citées.
4. `"$@"` conserve les arguments individuels, y compris ceux qui contiennent des espaces.
5. Un code `0` indique généralement la réussite ; un code non nul signale un échec ou un état particulier.
6. Avant une opération risquée, vérifiez précisément les chemins, les arguments et les permissions.
7. `bash -n` contrôle la syntaxe, mais ne garantit pas que le programme est correct.
8. Les scripts doivent être testés avec des données représentatives et des cas d'erreur.
9. `set -e` n'est pas un système universel de gestion des erreurs.
10. N'utilisez pas `eval` pour exécuter arbitrairement du texte reçu en entrée.


# 31. Glossaire

**Argument** : valeur transmise à un programme ou à un script au moment de son lancement.

**Bash** : interpréteur de commandes disposant de variables, de conditions, de boucles et de fonctions.

**Boucle** : construction permettant de répéter un groupe d'instructions.

**Commande intégrée** : commande exécutée directement par le shell, comme `cd` ou `read`.

**Code de retour** : valeur numérique renvoyée à la fin d'une commande pour signaler son résultat.

**Commentaire** : texte du code destiné aux lecteurs et non exécuté comme une commande ordinaire.

**Condition** : expression ou commande utilisée pour choisir un chemin d'exécution.

**Débogage** : recherche et correction des erreurs dans un programme.

**Environnement** : ensemble de variables et d'informations transmis à un processus lors de son démarrage.

**Expansion de variable** : opération qui remplace une référence à une variable par sa valeur.

**Fonction** : groupe d'instructions identifié par un nom et réutilisable.

**Interpréteur** : programme qui lit et exécute des instructions d'un langage.

**Pipeline** : mécanisme utilisant `|` pour relier la sortie standard d'une commande à l'entrée standard d'une autre.

**Redirection** : mécanisme qui change la destination de l'entrée, de la sortie ou des erreurs d'une commande.

**Répertoire courant** : répertoire de référence du shell au moment d'exécuter une commande.

**Shebang** : première ligne d'un script exécutable, commençant par `#!`, qui indique l'interpréteur à utiliser.

**Shell** : interpréteur de commandes servant d'interface au système.

**ShellCheck** : outil d'analyse statique aidant à détecter des erreurs et des constructions suspectes dans les scripts shell.

**Sous-shell** : environnement de shell distinct créé pour certaines exécutions ; la substitution de commande utilise un environnement de ce type dans Bash.

**Substitution de commande** : mécanisme, écrit `$(commande)`, permettant d'intégrer la sortie standard d'une commande dans une expression.

**Tableau** : structure permettant de conserver plusieurs valeurs dans une variable structurée.

**Variable** : nom associé à une valeur réutilisable.


# 32. Documentation et références officielles

Pour approfondir ce cours, utilisez en priorité les documents de référence des outils étudiés.

## Documentation GNU Bash

- **Bash Reference Manual** — référence principale pour la syntaxe, les variables, les paramètres, les conditions, les boucles, les fonctions, les redirections et les codes de retour :  
  https://www.gnu.org/software/bash/manual/bash.html

- **Page officielle de documentation Bash** — versions et formats disponibles :  
  https://www.gnu.org/software/bash/manual/

## Documentation GNU Coreutils

- **Manuel GNU Coreutils** — documentation des outils usuels comme `cat`, `mkdir` et `printf`, ainsi que d'autres commandes utilisées dans les scripts :  
  https://www.gnu.org/software/coreutils/manual/coreutils.html

- **Documentation de `test`** — tests sur les fichiers, chaînes et valeurs :  
  https://www.gnu.org/software/coreutils/manual/html_node/test-invocation.html

## Analyse des scripts

- **ShellCheck** — site officiel de l'outil d'analyse statique :  
  https://www.shellcheck.net/

- **Documentation ShellCheck** — explications des avertissements et exemples de corrections :  
  https://github.com/koalaman/shellcheck

## Comment utiliser ces références

Ne cherchez pas à mémoriser tout le manuel Bash. Apprenez d'abord les constructions utilisées dans ce cours, puis consultez la documentation lorsque vous rencontrez une fonctionnalité que vous ne comprenez pas.

Pour chaque nouveau script, adoptez cette routine :

1. écrire le code avec des noms de variables explicites ;
2. contrôler la syntaxe ;
3. exécuter le script dans le laboratoire ;
4. tester au moins un cas normal et un cas d'erreur ;
5. analyser les avertissements de ShellCheck lorsque l'outil est disponible ;
6. vérifier que les résultats correspondent au besoin avant d'utiliser le script sur une autre machine.


# Conclusion

Le scripting Bash transforme des commandes individuelles en procédures automatisées. Pour bien débuter, il est plus important de maîtriser les bases et d'écrire du code fiable que de créer immédiatement des scripts longs.

Vous devez désormais comprendre comment créer un script, utiliser des variables, recevoir des arguments, demander une saisie, prendre des décisions, répéter des instructions, définir des fonctions et gérer les fichiers.

Vous avez également découvert des principes essentiels de fiabilité : protéger les expansions de variables avec des guillemets, contrôler les arguments, traiter les erreurs, examiner les codes de retour et tester le code avant de l'exécuter dans un environnement important.

**Critère de validation du niveau débutant :** vous devez être capable de créer seul un script qui reçoit des arguments, contrôle des fichiers ou répertoires, effectue un traitement simple, écrit un résultat et signale clairement une erreur lorsque l'opération échoue.

Le niveau intermédiaire pourra ensuite approfondir les tableaux, les paramètres avancés, les expressions régulières, les fonctions réutilisables, le traitement robuste de fichiers, la journalisation, les signaux et la structuration de scripts d'administration plus complets.