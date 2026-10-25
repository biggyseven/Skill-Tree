# Scripting Bash sous Linux — Niveau intermédiaire

> **Fichier :** `scripting-intermediaire.md`  
> **Niveau :** Intermédiaire  
> **Domaine :** Administration Linux, automatisation, traitement de fichiers et fiabilité des scripts  
> **Interpréteur :** GNU Bash  
> **Prérequis :** maîtrise des variables, arguments, conditions, boucles, fonctions, redirections et codes de retour présentés dans le cours débutant  
> **Environnement conseillé :** Debian, Ubuntu ou une autre distribution Linux disposant de Bash et des utilitaires GNU usuels


# 1. Objectifs pédagogiques

Le niveau intermédiaire marque une évolution importante : il ne s'agit plus seulement d'enchaîner des commandes, mais de concevoir des scripts capables de gérer des entrées variées, des erreurs prévisibles, des fichiers aux noms inhabituels et des situations où certaines opérations échouent.

À l'issue de ce cours, vous devez savoir :

- structurer un script d'administration de manière claire ;
- interpréter correctement les expansions de paramètres Bash ;
- analyser des options de ligne de commande avec `getopts` ;
- utiliser les tableaux indexés et associatifs ;
- écrire des fonctions réutilisables avec des responsabilités explicites ;
- distinguer sortie standard, sortie d'erreur et code de retour ;
- comprendre les effets des sous-shells et des pipelines ;
- traiter des fichiers et des chemins contenant des espaces, des tabulations ou des retours à la ligne ;
- utiliser les expressions régulières de Bash ;
- installer des gestionnaires de signaux avec `trap` ;
- créer et nettoyer des fichiers temporaires ;
- produire des rapports de manière prudente ;
- gérer une journalisation exploitable ;
- comprendre les stratégies de gestion des erreurs ;
- éviter les erreurs de concurrence simples avec des mécanismes adaptés ;
- écrire des tests de fonctions et de scripts ;
- utiliser ShellCheck pour améliorer la qualité du code ;
- concevoir un outil d'inventaire de fichiers réutilisable.

Le cours reste consacré à Bash. Il ne couvre pas encore en profondeur les bibliothèques réutilisables complexes, les scripts concurrents avancés, les interfaces interactives sophistiquées ou l'orchestration de systèmes à grande échelle.

# 2. Sommaire

1. Positionnement du niveau intermédiaire
2. Architecture d'un script maintenable
3. Arguments, options et validation
4. Expansion avancée des paramètres
5. Variables d'environnement et configuration
6. Tableaux indexés et associatifs
7. Fonctions avancées et portée des variables
8. Expressions régulières et validation
9. Entrées/sorties et codes de retour
10. Sous-shells, pipelines et substitutions de processus
11. Parcours robuste de fichiers
12. Gestion des erreurs et options Bash
13. Signaux, `trap` et nettoyage
14. Fichiers temporaires et rapports atomiques
15. Journalisation
16. Permissions et exécution avec des privilèges
17. Synchronisation avec `flock`
18. Automatisation avec Cron et systemd
19. Tests, analyse statique et qualité
20. Méthodes de développement et dépannage
21. TP guidés
22. Exercices corrigés
23. Projet final : outil d'inventaire des fichiers journaux
24. Grille de compétences
25. Fiche de révision
26. Glossaire
27. Références officielles


# 3. Positionnement du niveau intermédiaire

## 3.1. Ce qui change par rapport au niveau débutant

Au niveau débutant, un script peut se limiter à une séquence de commandes :

```bash
#!/usr/bin/env bash

date
hostname
whoami
```

C'est suffisant pour automatiser une opération simple.

En revanche, un script d'administration réutilisable doit répondre à des questions supplémentaires :

- Que faire si un argument manque ?
- Comment gérer un chemin qui contient des espaces ?
- Que se passe-t-il si une commande échoue ?
- Comment empêcher un rapport incomplet de remplacer un rapport valide ?
- Comment nettoyer un fichier temporaire si le script est interrompu ?
- Comment distinguer un échec attendu d'une erreur imprévue ?
- Comment vérifier le résultat sans tester manuellement chaque scénario ?
- Comment rendre le script compréhensible par un autre administrateur ?

L'intermédiaire consiste à transformer un script qui fonctionne dans un cas simple en un outil qui se comporte de manière prévisible dans plusieurs situations.

## 3.2. Exemple d'évolution

Version initiale :

```bash
#!/usr/bin/env bash

find /var/log -name "*.log"
```

Problèmes possibles :

- le répertoire peut être inaccessible ;
- l'opération peut produire des erreurs ;
- le répertoire peut être différent selon la machine ;
- la sortie n'est pas enregistrée ;
- le script ne possède pas de paramètres ;
- un échec de `find` n'est pas traité explicitement ;
- l'appelant ne dispose pas d'une convention de codes de retour documentée.

Une version intermédiaire doit ajouter une structure, des validations, une stratégie d'erreur et une sortie exploitable.

## 3.3. Les principes fondamentaux

Les scripts de ce niveau reposent sur cinq principes.

**1. Valider les entrées.**  
Ne supposez jamais qu'une saisie, une option ou un chemin est valide.

**2. Préserver les données.**  
Les espaces et autres caractères présents dans un chemin doivent être conservés.

**3. Vérifier les opérations importantes.**  
Une commande peut échouer même lorsque sa syntaxe est correcte.

**4. Séparer les responsabilités.**  
Une fonction doit avoir un objectif identifiable.

**5. Tester les scénarios d'erreur.**  
Un script ne se juge pas seulement à son comportement lorsque tout se passe bien.


# 4. Architecture d'un script maintenable

## 4.1. Organiser le code

Un script intermédiaire gagne à suivre une structure relativement stable :

```text
SCRIPT
  |
  +-- En-tête et documentation
  |
  +-- Options et constantes
  |
  +-- Fonctions utilitaires
  |
  +-- Validation des entrées
  |
  +-- Préparation de l'environnement
  |
  +-- Traitement principal
  |
  +-- Résumé et code de retour
```

Cette organisation n'est pas une obligation syntaxique. C'est une méthode pour faciliter la lecture et la maintenance.

## 4.2. Exemple de squelette

```bash
#!/usr/bin/env bash

# Nom : outil.sh
# Objet : exemple de structure d'un script intermédiaire.
# Usage : ./outil.sh ARGUMENT
#
# Codes de retour :
#   0 : succès
#   1 : échec du traitement
#   2 : utilisation incorrecte

set -u

VERSION="1.0"

usage() {
    cat <<'EOF'
Usage : outil.sh ARGUMENT

Description :
    Démonstration de la structure d'un script Bash.
EOF
}

erreur() {
    printf 'ERREUR : %s\n' "$*" >&2
}

traiter() {
    local valeur="$1"

    printf 'Traitement de : %s\n' "$valeur"
}

main() {
    if [[ $# -ne 1 ]]; then
        usage >&2
        return 2
    fi

    traiter "$1"
}

main "$@"
exit $?
```

Ce squelette introduit une fonction `main`, qui constitue le point d'entrée logique de l'application.

Les fonctions permettent de séparer la validation, le traitement et la présentation des résultats.

## 4.3. Pourquoi utiliser une fonction `main` ?

Une fonction principale apporte plusieurs avantages :

- elle rend le flux général du script visible ;
- elle permet d'isoler les variables locales ;
- elle facilite les tests ;
- elle empêche le code principal de s'exécuter immédiatement lorsqu'une partie du fichier est chargée dans un contexte adapté.

Dans les petits scripts, son emploi reste facultatif. Dans un outil plus long, elle améliore généralement la lisibilité.

## 4.4. Comprendre la dernière ligne

```bash
main "$@"
exit $?
```

`main "$@"` appelle la fonction en transmettant fidèlement les arguments reçus.

La fonction renvoie un statut, puis `exit $?` termine le script avec le statut de la dernière commande exécutée, ici l'appel à `main`.

Une écriture plus compacte est possible :

```bash
main "$@"
```

Le processus se termine alors normalement lorsque le fichier atteint sa fin, avec le statut de la dernière commande. L'emploi explicite de `exit` rend toutefois le contrat de sortie plus visible.


# 5. Arguments, options et validation

Les paramètres positionnels sont utiles, mais les scripts intermédiaires doivent souvent accepter des options telles que `-d`, `-o` ou `-h`.

## 5.1. Distinguer arguments et options

Exemple d'appel :

```bash
./inventaire.sh -d /var/log -o rapport.txt
```

Dans cet exemple :

- `-d` introduit une option ;
- `/var/log` est la valeur de cette option ;
- `-o` introduit une autre option ;
- `rapport.txt` est la valeur correspondante.

Un script peut également accepter des arguments positionnels après les options.

Il faut définir une interface claire et éviter de laisser l'utilisateur deviner la syntaxe.

## 5.2. Présenter l'utilisation avec `usage`

La fonction suivante affiche une aide :

```bash
usage() {
    cat <<'EOF'
Usage :
  analyse.sh -d REPERTOIRE -o FICHIER
  analyse.sh -h

Options :
  -d REPERTOIRE   Répertoire à analyser
  -o FICHIER      Fichier de sortie
  -h              Afficher cette aide
EOF
}
```

Le texte est délimité par un *here-document*. Le marqueur `EOF` n'a pas de signification spéciale en dehors de cette construction.

Les guillemets dans `<<'EOF'` empêchent l'expansion ordinaire des variables et des substitutions présentes dans le texte d'aide.

## 5.3. Analyser les options avec `getopts`

`getopts` est une commande intégrée de Bash conçue pour analyser des options courtes.

Exemple :

```bash
#!/usr/bin/env bash

set -u

repertoire="."
rapport="rapport.txt"

usage() {
    printf 'Usage : %s [-d REPERTOIRE] [-o FICHIER] [-h]\n' "$0"
}

while getopts ":d:o:h" option; do
    case "$option" in
        d)
            repertoire="$OPTARG"
            ;;
        o)
            rapport="$OPTARG"
            ;;
        h)
            usage
            exit 0
            ;;
        :)
            printf 'Erreur : l’option -%s exige une valeur.\n' "$OPTARG" >&2
            usage >&2
            exit 2
            ;;
        \?)
            printf 'Erreur : option inconnue -%s.\n' "$OPTARG" >&2
            usage >&2
            exit 2
            ;;
    esac
done

shift "$((OPTIND - 1))"

printf 'Répertoire : %s\n' "$repertoire"
printf 'Rapport : %s\n' "$rapport"
```

### Comprendre la chaîne `":d:o:h"`

Dans la chaîne transmise à `getopts` :

- `d:` indique que `-d` attend une valeur ;
- `o:` indique que `-o` attend une valeur ;
- `h` indique que `-h` ne reçoit pas d'argument ;
- le `:` initial demande à `getopts` de laisser au script le soin de gérer certains cas d'option inconnue ou de valeur manquante.

Les détails de diagnostic dépendent de la chaîne de contrôle utilisée. Ici, les branches `:` et `\?` définissent des messages explicites.

### Comprendre `OPTARG`

Lorsque `getopts` reconnaît une option qui attend une valeur, il place cette valeur dans `OPTARG`.

Lorsqu'un appel ressemble à :

```bash
bash analyse.sh -d /var/log
```

la variable `OPTARG` contient `/var/log` lors du traitement de `-d`.

### Comprendre `OPTIND` et `shift`

`OPTIND` désigne l'indice du prochain argument à analyser.

```bash
shift "$((OPTIND - 1))"
```

retire les options et leurs valeurs déjà analysées des paramètres positionnels.

Après ce traitement, les éventuels paramètres restants peuvent être lus avec `$1`, `$2` et `"$@"`.

## 5.4. Options inconnues et valeurs manquantes

Le script doit être testé avec plusieurs appels :

```bash
bash analyse.sh -h
bash analyse.sh -d /var/log -o sortie.txt
bash analyse.sh -z
bash analyse.sh -d
bash analyse.sh -o
```

Attendez-vous à obtenir :

- une aide avec `-h` ;
- les valeurs sélectionnées avec un appel valide ;
- un message explicite avec une option inconnue ;
- un message explicite lorsqu'une valeur obligatoire manque.

Une valeur peut être syntaxiquement présente tout en étant incorrecte. Le contrôle de la présence ne remplace donc pas le contrôle de validité.

## 5.5. Valider le répertoire reçu

Une fois les options analysées, vérifiez la cohérence des valeurs.

```bash
if [[ ! -d "$repertoire" ]]; then
    printf 'Erreur : répertoire inexistant ou invalide : %s\n' "$repertoire" >&2
    exit 1
fi
```

Le contrôle `-d` permet de confirmer que le chemin correspond à un répertoire.

Si l'opération exige également de pouvoir lire son contenu :

```bash
if [[ ! -r "$repertoire" || ! -x "$repertoire" ]]; then
    printf 'Erreur : répertoire non accessible en lecture ou traversée.\n' >&2
    exit 1
fi
```

La lecture d'un répertoire et sa traversée sont deux aspects distincts des permissions Unix. Leur vérification constitue un contrôle préalable ; elle ne garantit pas que tous les traitements suivants réussiront.


# 6. Expansion avancée des paramètres

Bash fournit plusieurs formes d'expansion qui simplifient la manipulation des variables et réduisent le besoin d'appeler des programmes externes.

## 6.1. Fournir une valeur par défaut

```bash
nom="${NOM_UTILISATEUR:-Invité}"
```

Si `NOM_UTILISATEUR` est non définie ou vide, `nom` reçoit `Invité`.

À l'inverse :

```bash
nom="${NOM_UTILISATEUR-Invité}"
```

utilise `Invité` uniquement si la variable n'est pas définie, même si elle est définie avec une chaîne vide.

La différence est importante lorsqu'une valeur vide possède un sens particulier.

## 6.2. Affecter une valeur par défaut

```bash
: "${REPERTOIRE_RAPPORTS:="$HOME/rapports"}"
```

Cette construction initialise `REPERTOIRE_RAPPORTS` si la variable est absente ou vide.

Le caractère `:` correspond à une commande intégrée qui ne réalise pas de traitement utile mais dont les arguments sont évalués.

Une écriture plus simple est souvent suffisante :

```bash
REPERTOIRE_RAPPORTS="${REPERTOIRE_RAPPORTS:-"$HOME/rapports"}"
```

Dans les deux cas, pensez à protéger les chemins avec des guillemets lorsque vous les utilisez.

## 6.3. Arrêter si une variable est absente

```bash
: "${REPERTOIRE_SOURCE:?La variable REPERTOIRE_SOURCE est obligatoire}"
```

Si la variable est non définie ou vide, Bash affiche un diagnostic et provoque une erreur d'expansion.

Cette technique est utile lorsque la présence d'une configuration est indispensable. Le comportement doit être testé avec les options du shell utilisées par le script.

## 6.4. Mesurer la longueur d'une chaîne

```bash
texte="Administration Linux"

printf 'Longueur : %s\n' "${#texte}"
```

`${#texte}` indique la longueur de la chaîne selon les règles de Bash et l'environnement courant.

## 6.5. Extraire un préfixe ou un suffixe

Supposons :

```bash
chemin="/var/log/serveur.log"
```

Pour récupérer la partie après le dernier `/` :

```bash
nom_fichier="${chemin##*/}"
printf '%s\n' "$nom_fichier"
```

Résultat :

```text
serveur.log
```

Pour retirer le préfixe correspondant au dernier `/` et à ce qui le précède, `##*/` supprime la plus longue partie initiale qui correspond au motif.

Pour retirer un suffixe :

```bash
nom_sans_extension="${nom_fichier%.log}"
printf '%s\n' "$nom_sans_extension"
```

Résultat :

```text
serveur
```

`${variable%motif}` supprime le suffixe le plus court correspondant au motif.

`${variable%%motif}` supprimerait le suffixe le plus long correspondant.

Ces opérations manipulent des chaînes. Elles ne constituent pas un analyseur complet des chemins symboliques, des liens ou de toutes les conventions de fichiers.

## 6.6. Extraire une sous-chaîne

```bash
identifiant="SERVEUR-2026-001"

printf '%s\n' "${identifiant:8:4}"
```

Cet exemple extrait quatre caractères à partir de l'index `8`, qui commence à zéro.

Le résultat est :

```text
2026
```

La syntaxe `${variable:position:longueur}` est une fonctionnalité de Bash.

Utilisez-la lorsque la position des caractères est définie par un format stable. Pour analyser des formats dont les champs varient, une expression régulière ou un outil spécialisé peut être plus adapté.

## 6.7. Remplacer une partie de texte

```bash
fichier="rapport-final.txt"

printf '%s\n' "${fichier/final/archive}"
```

Résultat :

```text
rapport-archive.txt
```

`${variable/motif/remplacement}` remplace la première correspondance du motif. Avec `//`, Bash remplace toutes les correspondances correspondantes dans la forme générale prise en charge par cette expansion.

Pour les noms de fichiers, ne supposez pas que remplacer une chaîne donnera toujours un chemin valide ou unique.


# 7. Variables d'environnement et configuration

## 7.1. Variables ordinaires et variables exportées

Une variable est locale au shell qui l'a créée, sauf si elle est exportée ou transmise d'une autre manière.

```bash
APPLICATION="inventaire"
export ENVIRONNEMENT="laboratoire"
```

Dans cet exemple, `APPLICATION` n'est pas exportée automatiquement, contrairement à `ENVIRONNEMENT`.

Un programme enfant reçoit les variables exportées dans son environnement.

Exemple :

```bash
export ENVIRONNEMENT="laboratoire"
bash -c 'printf "Environnement : %s\n" "$ENVIRONNEMENT"'
```

## 7.2. Donner une valeur à une commande uniquement

La syntaxe suivante définit une variable d'environnement pour la commande appelée :

```bash
LANG=C date
```

Cette affectation ne modifie pas durablement la valeur de `LANG` dans le shell courant.

Les variables d'environnement influencent souvent le comportement des outils, notamment les formats de date, le tri et les messages. Les scripts d'administration doivent donc tenir compte de l'environnement dans lequel ils seront exécutés.

## 7.3. Comprendre `PATH`

`PATH` contient les répertoires dans lesquels le shell recherche les commandes.

```bash
printf '%s\n' "$PATH"
```

Pour vérifier une commande :

```bash
command -v find
command -v stat
command -v bash
```

Évitez de construire arbitrairement un `PATH` à partir de valeurs non fiables. Un répertoire contrôlé par un utilisateur non privilégié placé en tête du `PATH` peut conduire à l'exécution d'un programme inattendu.

Dans un script exécuté avec des privilèges élevés, utilisez un environnement contrôlé et, lorsque c'est approprié, des chemins absolus pour les commandes sensibles.

## 7.4. Charger un fichier de configuration

Un fichier de configuration Bash peut être chargé avec :

```bash
source "$HOME/.config/mon-outil.conf"
```

La forme équivalente sous Bash est :

```bash
. "$HOME/.config/mon-outil.conf"
```

Exemple de fichier de configuration :

```bash
REPERTOIRE_SOURCE="/var/log"
NIVEAU_JOURNAL="INFO"
```

### Point de sécurité essentiel

`source` exécute le contenu du fichier dans le shell courant.

Il ne s'agit pas d'une simple lecture de paramètres. Un fichier de configuration contenant du code arbitraire peut modifier des variables, lancer des commandes et changer le comportement du script.

Ne chargez donc pas un fichier fourni par une source non fiable comme s'il s'agissait d'un simple fichier de données.

Pour des configurations qui doivent être partagées avec des systèmes non Bash ou être traitées comme des données, préférez un format structuré accompagné d'un parseur approprié.


# 8. Tableaux indexés et associatifs

Les tableaux deviennent particulièrement utiles lorsque les scripts doivent manipuler des listes de répertoires, de services, de machines ou de résultats.

## 8.1. Tableaux indexés

```bash
declare -a services=("ssh" "cron" "nginx")
```

Les éléments sont indexés numériquement, en commençant généralement par zéro.

```bash
printf '%s\n' "${services[0]}"
printf '%s\n' "${services[1]}"
```

Pour obtenir le nombre d'éléments :

```bash
printf 'Nombre : %s\n' "${#services[@]}"
```

Pour parcourir chaque élément :

```bash
for service in "${services[@]}"; do
    printf 'Service : %s\n' "$service"
done
```

Utilisez toujours des guillemets autour de `"${tableau[@]}"` lorsqu'il faut préserver chaque élément comme un argument distinct.

## 8.2. Modifier un tableau

```bash
services=("ssh" "cron")
services+=("nginx")
```

Le tableau contient désormais trois éléments.

Pour remplacer un élément :

```bash
services[1]="systemd-timesyncd"
```

Pour supprimer un élément particulier :

```bash
unset 'services[0]'
```

La suppression ne garantit pas que les indices seront renumérotés de manière contiguë. Il faut distinguer l'ensemble des indices existants de la simple quantité d'éléments.

## 8.3. Tableaux associatifs

Un tableau associatif indexe les valeurs à l'aide de clés textuelles plutôt qu'à l'aide d'indices entiers.

Exemple :

```bash
declare -A ports

ports[ssh]=22
ports[http]=80
ports[https]=443
```

Accès à une valeur :

```bash
printf 'Port HTTPS : %s\n' "${ports[https]}"
```

Parcours du tableau :

```bash
for service in "${!ports[@]}"; do
    printf '%s : %s\n' "$service" "${ports[$service]}"
done
```

L'ordre d'itération n'est pas garanti comme un ordre alphabétique. Si cet ordre est important, il faut le définir explicitement, par exemple avec un tri de la liste de clés.

Les tableaux associatifs nécessitent une version de Bash qui les prend en charge. Cette fonctionnalité est disponible dans Bash 4 et les versions suivantes.

## 8.4. Exemple de correspondance service-port

```bash
#!/usr/bin/env bash

declare -A ports=(
    [ssh]=22
    [http]=80
    [https]=443
)

service="${1:-}"

if [[ -z "$service" ]]; then
    printf 'Usage : %s SERVICE\n' "$0" >&2
    exit 2
fi

if [[ -v "ports[$service]" ]]; then
    printf 'Le service %s utilise le port de référence %s.\n' \
        "$service" "${ports[$service]}"
else
    printf 'Service inconnu : %s\n' "$service" >&2
    exit 1
fi
```

L'opérateur `-v` dans `[[ ... ]]` permet de tester si une variable ou un élément de tableau est défini dans Bash. Il est utile de vérifier la compatibilité avec la version de Bash utilisée.

Cet exemple est une table de correspondance pédagogique. Il ne prouve pas que le service est installé, qu'il fonctionne ou qu'il écoute réellement sur ce port.


# 9. Fonctions avancées et portée des variables

## 9.1. Déclarer des fonctions spécialisées

Une fonction doit avoir une responsabilité définie.

Exemple :

```bash
est_repertoire() {
    [[ -d "$1" ]]
}
```

La fonction renvoie le statut du test `[[ -d "$1" ]]`.

Utilisation :

```bash
if est_repertoire "$HOME"; then
    printf 'Le répertoire personnel est accessible comme répertoire.\n'
fi
```

Cette approche évite de répéter le même test à plusieurs endroits.

## 9.2. Valider les arguments d'une fonction

```bash
verifier_argument_repertoire() {
    if [[ $# -ne 1 ]]; then
        printf 'Erreur interne : un chemin est attendu.\n' >&2
        return 2
    fi

    if [[ ! -d "$1" ]]; then
        printf 'Erreur : répertoire invalide : %s\n' "$1" >&2
        return 1
    fi

    return 0
}
```

La fonction définit explicitement son contrat :

- `0` : répertoire accepté ;
- `1` : chemin invalide ;
- `2` : appel incorrect.

Les codes sont une convention de cette fonction. Si elle est utilisée par un programme plus grand, documentez cette convention.

## 9.3. Portée des variables avec `local`

```bash
decrire_fichier() {
    local chemin="$1"
    local nom

    nom="${chemin##*/}"

    printf 'Chemin : %s\n' "$chemin"
    printf 'Nom : %s\n' "$nom"
}
```

Les variables `chemin` et `nom` sont locales à la fonction.

Il est généralement préférable de déclarer les variables locales dans les fonctions afin d'éviter de modifier accidentellement l'état global du script.

Une variable globale est justifiée lorsqu'elle représente un état réellement partagé entre plusieurs fonctions, comme les compteurs d'un traitement global.

## 9.4. Ne pas confondre sortie et valeur de retour

En Bash, le statut d'une fonction est numérique. `return` ne permet pas de renvoyer directement une chaîne de caractères comme en Python.

Pour produire du texte :

```bash
obtenir_nom_machine() {
    hostname
}

machine="$(obtenir_nom_machine)"
printf 'Machine : %s\n' "$machine"
```

Pour produire un statut :

```bash
est_fichier() {
    [[ -f "$1" ]]
}

if est_fichier "$HOME/rapport.txt"; then
    printf 'Fichier détecté.\n'
fi
```

Pour produire à la fois une donnée et un statut, concevez explicitement les sorties de la fonction ou stockez le résultat dans une variable de sortie définie par contrat.

## 9.5. Éviter les effets de bord inutiles

Cette fonction est difficile à réutiliser :

```bash
fonction_mauvaise() {
    cd /var/log
    rm -f *.tmp
    echo "Terminé"
}
```

Elle change le répertoire courant et supprime des fichiers en même temps qu'elle produit un message.

Une fonction réutilisable possède généralement un objectif unique. Les changements du répertoire courant, de l'environnement global ou du système doivent être explicitement justifiés et documentés.


# 10. Expressions régulières et validation

Bash permet de tester une expression régulière avec l'opérateur `=~` à l'intérieur de `[[ ... ]]`.

## 10.1. Vérifier une suite de chiffres

```bash
numero="123456"

if [[ "$numero" =~ ^[0-9]+$ ]]; then
    printf 'La valeur contient uniquement des chiffres.\n'
else
    printf 'Format invalide.\n' >&2
fi
```

Signification des éléments :

| Élément | Signification |
|---|---|
| `^` | début de chaîne |
| `[0-9]` | un chiffre de 0 à 9 |
| `+` | une ou plusieurs occurrences |
| `$` | fin de chaîne |

Cette expression vérifie le format. Elle ne garantit pas que la valeur soit un entier représentable dans l'arithmétique Bash.

## 10.2. Valider un identifiant simple

Exemple :

```bash
identifiant="serveur_01"

if [[ "$identifiant" =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]; then
    printf 'Identifiant accepté.\n'
else
    printf 'Identifiant invalide.\n' >&2
    exit 1
fi
```

Cette règle impose :

- une première lettre ;
- puis uniquement des lettres, chiffres, tirets ou traits de soulignement.

C'est une politique de validation inventée pour cet exemple. Elle n'est pas une règle universelle pour les noms Linux, qui peuvent accepter d'autres caractères selon le contexte.

## 10.3. Capturer des groupes

Bash fournit la variable `BASH_REMATCH` après une correspondance réussie avec une expression régulière.

```bash
version="app-2.14.7"

if [[ "$version" =~ ^app-([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    majeur="${BASH_REMATCH[1]}"
    mineur="${BASH_REMATCH[2]}"
    correctif="${BASH_REMATCH[3]}"

    printf 'Version majeure : %s\n' "$majeur"
    printf 'Version mineure : %s\n' "$mineur"
    printf 'Correctif : %s\n' "$correctif"
else
    printf 'Version invalide.\n' >&2
    exit 1
fi
```

Les parenthèses définissent des groupes capturés.

`BASH_REMATCH[0]` représente la correspondance complète, tandis que les indices suivants représentent les groupes dans leur ordre d'apparition.

La variable est réinitialisée par les correspondances ultérieures ; copiez les données nécessaires avant d'effectuer d'autres tests regex.

## 10.4. Valider un code avant un calcul

```bash
lire_entier() {
    local saisie="$1"

    [[ "$saisie" =~ ^[0-9]+$ ]]
}
```

Appel :

```bash
valeur="42"

if lire_entier "$valeur"; then
    printf 'Format valide.\n'
fi
```

Ne confondez jamais la validité lexicale et la validité métier.

Une valeur peut contenir uniquement des chiffres tout en étant trop grande pour le calcul prévu. Un identifiant peut être syntaxiquement valide tout en ne désignant aucun objet existant.


# 11. Entrées/sorties et codes de retour

## 11.1. Les trois flux standards

Un processus dispose normalement de trois flux standards :

| Flux | Descripteur | Fonction |
|---|---:|---|
| Entrée standard | `0` | recevoir des données |
| Sortie standard | `1` | transmettre un résultat normal |
| Sortie d'erreur standard | `2` | transmettre les diagnostics |

La distinction entre la sortie normale et la sortie d'erreur permet à l'appelant de traiter séparément les résultats et les problèmes.

## 11.2. Écrire une erreur sur `stderr`

```bash
printf 'Erreur : argument manquant.\n' >&2
```

Cette écriture conserve le résultat utile sur la sortie standard et les diagnostics sur la sortie d'erreur.

C'est une convention importante pour les outils que l'on souhaite utiliser dans des pipelines.

## 11.3. Capture de la sortie et des erreurs

Pour récupérer la sortie standard :

```bash
resultat="$(commande)"
```

Pour enregistrer les erreurs dans une autre variable, une approche fréquente consiste à rediriger temporairement la sortie d'erreur vers un fichier ou à afficher les erreurs séparément.

Exemple :

```bash
fichier_erreurs="$(mktemp)" || exit 1

if resultat="$(commande_inconnue 2>"$fichier_erreurs")"; then
    printf 'Résultat : %s\n' "$resultat"
else
    printf 'Échec de la commande.\n' >&2
    cat -- "$fichier_erreurs" >&2
fi

rm -f -- "$fichier_erreurs"
```

Cet exemple sert à illustrer la distinction des flux. Dans un outil durable, le nettoyage du fichier temporaire doit également être garanti en cas d'interruption ; cette technique est détaillée plus loin.

## 11.4. L'erreur silencieuse

Évitez les constructions qui ignorent un échec sans l'expliquer :

```bash
mkdir -p "$repertoire" 2>/dev/null
```

Cette commande peut être justifiée si le silence est voulu et si son statut est vérifié. Sinon, elle masque un diagnostic utile.

Une version plus explicite :

```bash
if ! mkdir -p "$repertoire"; then
    printf 'Impossible de préparer le répertoire : %s\n' "$repertoire" >&2
    exit 1
fi
```

## 11.5. Le statut d'un pipeline

Par défaut, le statut d'un pipeline Bash reflète généralement le statut de sa dernière commande.

```bash
commande_a | commande_b
```

Il est possible que `commande_a` échoue alors que `commande_b` termine avec succès.

Pour modifier ce comportement :

```bash
set -o pipefail
```

Avec cette option, le statut du pipeline devient non nul lorsqu'une commande du pipeline échoue, selon les règles de Bash.

Exemple :

```bash
set -o pipefail

false | cat
statut=$?

printf 'Statut du pipeline : %s\n' "$statut"
```

Le statut est non nul, car `false` échoue.

Attention : les règles d'un pipeline contenant plusieurs commandes sont plus détaillées que ce seul exemple. Pour les opérations importantes, examinez aussi les statuts des commandes et définissez une stratégie d'erreur explicite.


# 12. Sous-shells, pipelines et substitutions de processus

Les sous-shells expliquent plusieurs erreurs fréquentes dans les scripts.

## 12.1. Pourquoi une variable change-t-elle de valeur seulement dans une boucle ?

Exemple :

```bash
compteur=0

printf '%s\n' a b c | while IFS= read -r ligne; do
    compteur=$((compteur + 1))
done

printf 'Compteur : %s\n' "$compteur"
```

Selon le comportement normal de Bash avec cette construction, la boucle exécutée dans un pipeline tourne dans un sous-shell. Les modifications de `compteur` ne sont donc pas conservées dans le shell parent.

La valeur affichée reste `0`.

## 12.2. Correction avec une redirection d'entrée

```bash
compteur=0

while IFS= read -r ligne; do
    compteur=$((compteur + 1))
done < <(printf '%s\n' a b c)

printf 'Compteur : %s\n' "$compteur"
```

Dans cette construction, la boucle s'exécute dans le shell courant et peut modifier `compteur`.

La syntaxe `< <(...)` utilise une **substitution de processus**.

Elle permet d'exposer la sortie d'une commande sous la forme d'un chemin lisible par une autre commande.

Cette fonctionnalité est propre à Bash et dépend des mécanismes pris en charge par le système, notamment `/dev/fd` ou des tubes nommés.

## 12.3. Limite de la substitution de processus

La substitution de processus ne constitue pas à elle seule une solution universelle à la gestion des erreurs de la commande substituée.

Dans le cas suivant :

```bash
while IFS= read -r ligne; do
    printf '%s\n' "$ligne"
done < <(commande_productrice)
```

le statut de la boucle ne représente pas nécessairement le statut de `commande_productrice`.

Si la réussite de cette dernière commande est essentielle, choisissez une technique qui permet de contrôler son statut explicitement, par exemple en écrivant d'abord sa sortie dans un fichier temporaire et en vérifiant son code de retour.

## 12.4. Substitution de commande

```bash
resultat="$(commande)"
```

Cette construction exécute la commande dans un environnement de sous-shell et récupère sa sortie standard.

Points importants :

- les retours à la ligne terminaux sont supprimés ;
- le résultat est du texte, pas un objet structuré ;
- le code de retour doit être traité séparément ;
- une valeur contenant des espaces doit être utilisée avec les guillemets appropriés.

Exemple de contrôle explicite :

```bash
if resultat="$(hostname)"; then
    printf 'Machine : %s\n' "$resultat"
else
    printf 'Impossible de déterminer la machine.\n' >&2
    exit 1
fi
```

## 12.5. Ne pas utiliser `$(commande)` pour conserver des données binaires

La substitution de commande n'est pas conçue pour transporter fidèlement une suite d'octets arbitraires.

Elle est adaptée aux petits résultats textuels, aux identifiants et aux informations simples fournies par les commandes.

Pour les données binaires, utilisez des fichiers ou des flux adaptés.


# 13. Parcours robuste de fichiers

Manipuler les noms de fichiers est un point majeur de différenciation entre un script fragile et un script correctement conçu.

## 13.1. Pourquoi les espaces sont-ils un problème ?

Un fichier peut s'appeler :

```text
rapport annuel.txt
```

Si un script stocke son nom dans une variable et l'utilise sans guillemets, Bash peut découper la valeur en plusieurs arguments.

Fragile :

```bash
fichier="rapport annuel.txt"
cat $fichier
```

Correct :

```bash
fichier="rapport annuel.txt"
cat -- "$fichier"
```

Les guillemets préservent le nom comme une seule valeur. Le séparateur `--` empêche le nom d'être interprété comme une option par les commandes compatibles.

## 13.2. Pourquoi `ls` n'est-il pas une liste fiable pour le code ?

Cette construction est à éviter :

```bash
for fichier in $(ls); do
    printf '%s\n' "$fichier"
done
```

Elle combine deux opérations fragiles :

1. elle découpe la sortie en mots ;
2. elle peut interpréter les caractères spéciaux présents dans les noms.

Un nom contenant des espaces ou des retours à la ligne ne sera donc pas traité fidèlement.

Pour parcourir les fichiers qui correspondent à un motif simple dans le répertoire courant, on peut utiliser :

```bash
for fichier in ./*.log; do
    [[ -f "$fichier" ]] || continue
    printf 'Fichier : %s\n' "$fichier"
done
```

Lorsque le motif ne correspond à aucun fichier, Bash peut conserver le motif littéral. Le test `-f` évite alors de traiter cette valeur comme un fichier existant.

## 13.3. Pourquoi `find -print0` est-il utile ?

Les noms de fichiers Unix peuvent contenir des espaces, des tabulations et des retours à la ligne. Ils ne peuvent pas contenir un octet NUL.

Par conséquent, le caractère NUL permet de séparer les noms de fichiers sans ambiguïté.

Commande :

```bash
find "$HOME/lab-scripting" -type f -name '*.log' -print0
```

Elle produit une liste de chemins terminés par des caractères NUL.

Ce flux doit être consommé par un mécanisme qui reconnaît la même délimitation.

## 13.4. Lire des chemins avec `read -d ''`

En Bash, `read -d ''` permet de lire jusqu'à un caractère NUL.

```bash
while IFS= read -r -d '' fichier; do
    printf 'Fichier trouvé : %q\n' "$fichier"
done < <(find "$HOME/lab-scripting" -type f -name '*.log' -print0)
```

Les choix importants :

- `IFS=` préserve les espaces initiaux et finaux ;
- `read -r` préserve les antislashs ;
- `-d ''` utilise NUL comme délimiteur ;
- `%q` affiche une représentation échappée du chemin dans Bash, ce qui facilite le diagnostic des noms inhabituels.

Cette construction conserve la variable dans le shell courant, contrairement à la boucle placée directement dans un pipeline.

Cependant, le statut de `find` n'est pas vérifié explicitement dans cette forme. Pour un traitement fiable où un échec de `find` ne doit pas être confondu avec une liste vide, utilisez plutôt un fichier temporaire.

## 13.5. Parcours robuste avec contrôle de l'erreur

```bash
#!/usr/bin/env bash

set -u

repertoire="$HOME/lab-scripting"

liste_temporaire="$(mktemp)" || {
    printf 'Impossible de créer le fichier temporaire.\n' >&2
    exit 1
}

if ! find "$repertoire" -type f -name '*.log' -print0 > "$liste_temporaire"; then
    printf 'Erreur pendant la recherche de fichiers.\n' >&2
    rm -f -- "$liste_temporaire"
    exit 1
fi

while IFS= read -r -d '' fichier; do
    printf 'Trouvé : %q\n' "$fichier"
done < "$liste_temporaire"

rm -f -- "$liste_temporaire"
```

La commande `find` écrit d'abord ses résultats dans le fichier temporaire.

Le script vérifie ensuite son statut avant de parcourir les résultats. Si `find` échoue, le script ne poursuit pas le traitement comme si la recherche avait réussi.

Pour un programme destiné à la production, il faudra également garantir le nettoyage du fichier temporaire en cas d'interruption. Le chapitre consacré à `trap` montre comment le faire.


# 14. Gestion des erreurs et options Bash

## 14.1. Pourquoi la gestion des erreurs est-elle difficile ?

Bash exécute de nombreuses commandes externes qui possèdent leurs propres statuts de retour.

Un échec peut être :

- inattendu, par exemple l'impossibilité de créer un rapport ;
- attendu, par exemple la recherche d'un fichier absent ;
- acceptable dans un contexte particulier, mais dangereux dans un autre.

Il faut distinguer ces cas plutôt que de traiter tous les codes non nuls de manière identique.

## 14.2. Vérification explicite

```bash
if ! cp -- "$source" "$destination"; then
    printf 'Erreur : copie impossible.\n' >&2
    exit 1
fi
```

L'échec est traité directement à l'endroit où il se produit.

Pour les opérations importantes, les vérifications explicites ont souvent l'avantage d'être plus faciles à comprendre qu'une règle générale appliquée à tout le script.

## 14.3. `set -e` : usage et limites

On rencontre souvent :

```bash
set -e
```

Cette option demande généralement à Bash de terminer lorsqu'une commande échoue dans plusieurs contextes. Elle ne constitue toutefois pas une garantie universelle de gestion des erreurs.

Le comportement dépend notamment de l'utilisation de commandes dans des conditions, des listes `&&` et `||`, des fonctions et des pipelines.

Un script qui utilise `set -e` peut donc continuer après certains échecs qui semblent intuitivement devoir interrompre son exécution.

Pour cette raison, ne vous contentez jamais d'ajouter `set -e` en pensant avoir résolu toute la gestion des erreurs. Les opérations critiques doivent être contrôlées explicitement.

## 14.4. `set -u` : variables non définies

```bash
set -u
```

Cette option signale les expansions de variables non définies dans des contextes concernés.

Elle aide à détecter les fautes de nommage et les valeurs oubliées.

Exemple :

```bash
#!/usr/bin/env bash

set -u

nom="Amina"
printf 'Nom : %s\n' "$nom"
```

Cependant, les variables optionnelles doivent être manipulées explicitement :

```bash
nom="${NOM_UTILISATEUR:-Invité}"
```

Une variable dont l'absence est prévue ne doit pas être traitée de la même façon qu'une variable indispensable.

## 14.5. `set -o pipefail`

```bash
set -o pipefail
```

Cette option permet de détecter l'échec d'une commande au sein d'un pipeline, au lieu de se baser uniquement sur le succès potentiel de la dernière commande.

Elle est souvent utile dans les scripts qui s'appuient sur des pipelines.

## 14.6. Le mode strict n'est pas une garantie absolue

On rencontre fréquemment cette combinaison :

```bash
set -euo pipefail
```

Elle peut être adaptée à un script qui a été conçu et testé pour ces règles, mais elle ne remplace pas la conception de la gestion des erreurs.

Points à considérer :

- `-e` possède des exceptions ;
- `-u` impose une discipline sur les variables optionnelles ;
- `pipefail` modifie la propagation des échecs des pipelines ;
- les expansions arithmétiques et les fonctions doivent être testées dans les contextes utilisés.

Dans un programme intermédiaire, vous devez être capable d'expliquer pourquoi chaque option a été choisie.

## 14.7. Une stratégie explicite

La structure suivante convient à de nombreuses opérations importantes :

```bash
if resultat="$(commande_importante)"; then
    printf 'Opération réussie : %s\n' "$resultat"
else
    statut=$?
    printf 'Échec de l’opération, statut %s.\n' "$statut" >&2
    exit 1
fi
```

Le statut est récupéré immédiatement dans la branche d'échec.

Cette forme évite qu'une commande de diagnostic exécutée entre-temps remplace la valeur de `$?`.

## 14.8. Définir une convention de codes de retour

Exemple de convention propre à un outil :

| Code | Signification dans cet outil |
|---:|---|
| `0` | traitement terminé sans erreur |
| `1` | échec du traitement |
| `2` | arguments ou options invalides |
| `3` | ressource requise absente |

Cette convention n'est pas universelle. Elle permet aux scripts appelants de distinguer les cas si elle est documentée et respectée partout dans le programme.


# 15. Signaux, `trap` et nettoyage

Les scripts peuvent être interrompus ou recevoir des signaux. Une interruption peut survenir lorsque l'utilisateur appuie sur `Ctrl+C`, lorsqu'un processus d'administration envoie un signal ou lorsqu'un environnement de supervision arrête le programme.

## 15.1. Comprendre les signaux courants

| Signal | Usage courant |
|---|---|
| `SIGINT` | interruption interactive, souvent via `Ctrl+C` |
| `SIGTERM` | demande d'arrêt d'un processus |
| `SIGKILL` | arrêt forcé, non interceptable |
| `SIGHUP` | signal traditionnellement associé à la fermeture d'un terminal ou à une demande de rechargement, selon le programme |

Un processus ne peut pas installer de gestionnaire permettant d'intercepter `SIGKILL`. Aucun script ne peut garantir son nettoyage normal lorsque ce signal termine son processus.

Les gestionnaires de signaux doivent donc être conçus comme une amélioration de la robustesse, et non comme une garantie absolue.

## 15.2. Installer un gestionnaire avec `trap`

```bash
#!/usr/bin/env bash

trap 'printf "\nInterruption reçue.\n" >&2; exit 130' INT

while true; do
    printf 'Le script travaille...\n'
    sleep 2
done
```

Le gestionnaire traite le signal `INT` et termine le script avec le code `130`, une convention courante pour une interruption par `SIGINT`.

## 15.3. Garantir le nettoyage à la fin

`trap` peut exécuter une fonction lors de la sortie du script.

```bash
#!/usr/bin/env bash

fichier_temporaire=""

nettoyer() {
    if [[ -n "$fichier_temporaire" && -e "$fichier_temporaire" ]]; then
        rm -f -- "$fichier_temporaire"
    fi
}

trap nettoyer EXIT

fichier_temporaire="$(mktemp)" || {
    printf 'Erreur : impossible de créer le fichier temporaire.\n' >&2
    exit 1
}

printf 'Données temporaires\n' > "$fichier_temporaire"

cat -- "$fichier_temporaire"
```

Le gestionnaire `EXIT` exécute `nettoyer` lors de la sortie normale du shell du script ou après une terminaison normale par `exit`.

La fonction vérifie qu'un fichier temporaire a bien été défini et qu'il existe avant de le supprimer.

## 15.4. Traiter également `INT` et `TERM`

```bash
#!/usr/bin/env bash

fichier_temporaire=""

nettoyer() {
    if [[ -n "$fichier_temporaire" && -e "$fichier_temporaire" ]]; then
        rm -f -- "$fichier_temporaire"
    fi
}

trap nettoyer EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

fichier_temporaire="$(mktemp)" || exit 1
printf 'Travail en cours...\n'
```

Lorsqu'un signal entraîne `exit`, le gestionnaire de sortie `EXIT` s'exécute à son tour.

Les statuts `130` et `143` sont des conventions usuelles associées respectivement à une interruption par `SIGINT` et à une terminaison par `SIGTERM`. Les conventions doivent être adaptées si le programme possède un contrat particulier.

## 15.5. Pourquoi initialiser la variable avant `trap` ?

Avec `set -u`, utiliser une variable non définie peut provoquer une erreur.

Définir :

```bash
fichier_temporaire=""
```

avant d'enregistrer le gestionnaire garantit que le nettoyage peut examiner la variable même si l'échec survient avant la création du fichier.

C'est une bonne habitude lorsque le nettoyage dépend de ressources qui ne seront disponibles qu'après plusieurs étapes.


# 16. Fichiers temporaires et rapports atomiques

## 16.1. Pourquoi utiliser `mktemp` ?

Un fichier temporaire permet de stocker des données intermédiaires sans écraser un document existant.

Exemple :

```bash
fichier_temporaire="$(mktemp)" || {
    printf 'Impossible de créer un fichier temporaire.\n' >&2
    exit 1
}
```

`mktemp` crée un fichier temporaire et renvoie son chemin.

Évitez de fabriquer un nom temporaire prévisible tel que :

```text
/tmp/rapport-temporaire.txt
```

Un nom prévisible dans un répertoire partagé peut exposer le script à des conflits ou à des risques de sécurité.

## 16.2. Pourquoi ne pas écrire directement dans le rapport final ?

Supposons que votre script analyse plusieurs milliers de fichiers.

S'il écrit directement dans le rapport final, un arrêt inattendu peut laisser un fichier incomplet.

Une méthode plus prudente consiste à :

1. préparer un fichier temporaire ;
2. y écrire la totalité du résultat ;
3. vérifier que le traitement s'est terminé correctement ;
4. remplacer le rapport final uniquement lorsque le fichier temporaire est prêt.

## 16.3. Remplacement atomique d'un fichier de rapport

```bash
#!/usr/bin/env bash

set -u

rapport="$HOME/lab-scripting/rapport.txt"
repertoire_sortie="${rapport%/*}"

if ! mkdir -p "$repertoire_sortie"; then
    printf 'Erreur : impossible de préparer la sortie.\n' >&2
    exit 1
fi

rapport_temporaire="$(mktemp "$repertoire_sortie/.rapport.XXXXXX")" || {
    printf 'Erreur : impossible de créer le fichier temporaire.\n' >&2
    exit 1
}

nettoyer() {
    if [[ -n "$rapport_temporaire" && -e "$rapport_temporaire" ]]; then
        rm -f -- "$rapport_temporaire"
    fi
}

trap nettoyer EXIT

if ! {
    printf 'Rapport de test\n'
    printf 'Date : %s\n' "$(date)"
    printf 'Machine : %s\n' "$(hostname)"
} > "$rapport_temporaire"; then
    printf 'Erreur : écriture du rapport impossible.\n' >&2
    exit 1
fi

if ! mv -f -- "$rapport_temporaire" "$rapport"; then
    printf 'Erreur : remplacement du rapport impossible.\n' >&2
    exit 1
fi

printf 'Rapport publié : %s\n' "$rapport"
```

### Pourquoi créer le fichier temporaire dans le répertoire de sortie ?

Le déplacement final est généralement plus simple et plus sûr lorsque les deux fichiers se trouvent sur le même système de fichiers.

Dans ce cas, le renommage effectué par `mv` peut être atomique au niveau du système de fichiers. Cela évite aux lecteurs de voir normalement un fichier remplacé progressivement par morceaux.

Ce mécanisme ne constitue pas une garantie universelle de durabilité face à toutes les pannes matérielles. Il améliore l'intégrité de publication, mais ne remplace pas les stratégies de sauvegarde, de synchronisation ou de restauration.

### Précaution importante

Le code ci-dessus suppose que `rapport` est un chemin dont la nature est comprise. Dans un outil réutilisable, vérifiez que la destination ne désigne pas un répertoire et documentez le comportement lorsque le rapport existe déjà.


# 17. Journalisation

Un script d'administration doit fournir des messages qui permettent de comprendre ce qu'il a fait et, surtout, pourquoi il a échoué.

## 17.1. Distinguer les messages

On peut organiser les diagnostics selon plusieurs niveaux :

- `INFO` : information normale ;
- `WARN` : anomalie non bloquante ;
- `ERROR` : échec ;
- `DEBUG` : détail de diagnostic destiné au développement.

## 17.2. Créer une fonction de journalisation

```bash
log() {
    local niveau="$1"
    shift

    printf '%s [%s] %s\n' \
        "$(date '+%Y-%m-%d %H:%M:%S')" \
        "$niveau" \
        "$*" >&2
}
```

Utilisation :

```bash
log INFO "Démarrage de l'inventaire"
log WARN "Un fichier optionnel est absent"
log ERROR "Écriture impossible"
```

Dans cet exemple, les messages sont envoyés sur la sortie d'erreur. Cela permet de réserver la sortie standard à un résultat éventuellement consommé par une autre commande.

Pour un outil de production, il faut également définir le format attendu, la politique de conservation et la destination des journaux.

## 17.3. Ajouter un niveau de détail

```bash
MODE_DEBUG=0

debug() {
    if (( MODE_DEBUG == 1 )); then
        log DEBUG "$@"
    fi
}
```

Activation :

```bash
MODE_DEBUG=1
debug "Valeur de configuration reçue"
```

Dans un script à options, `MODE_DEBUG` peut être activé par une option `-v` ou `-D`, selon l'interface choisie.

Évitez d'imprimer automatiquement des secrets ou des valeurs sensibles dans les traces de débogage.

## 17.4. Enregistrer la sortie dans un fichier

Une commande peut rediriger les messages vers un fichier de journal :

```bash
bash outil.sh >> "$HOME/outil.log" 2>&1
```

La sortie standard est d'abord redirigée vers le journal. La sortie d'erreur est ensuite dirigée vers la destination courante de la sortie standard.

Il faut vérifier les droits d'accès au fichier journal et prévoir un mécanisme de rotation si ce fichier peut grossir continuellement.


# 18. Permissions et exécution avec des privilèges

## 18.1. Le principe du moindre privilège

Un script doit être exécuté avec les privilèges strictement nécessaires.

Un outil qui lit des fichiers accessibles à l'utilisateur ne doit pas être lancé avec `sudo` simplement parce qu'il s'agit d'un script d'administration.

Un accès privilégié doit correspondre à une opération précise et justifiée.

## 18.2. Ne pas se fier au nom de l'utilisateur

Cette vérification :

```bash
if [[ "$USER" == "root" ]]; then
    printf 'Utilisateur root détecté.\n'
fi
```

n'est pas une vérification fiable de l'identité effective du processus. `USER` est une variable d'environnement et peut être incorrecte ou modifiée.

Pour vérifier l'identifiant effectif de l'utilisateur sous Linux, on peut utiliser :

```bash
if (( EUID != 0 )); then
    printf 'Ce script doit être lancé avec les privilèges nécessaires.\n' >&2
    exit 1
fi
```

Cette vérification ne doit être ajoutée que lorsqu'une exécution en tant que root est réellement nécessaire. Elle n'est pas une bonne pratique universelle pour tous les scripts.

## 18.3. Protéger le `PATH`

Les scripts lancés avec des privilèges élevés ne doivent pas faire confiance à un environnement arbitraire.

Les commandes externes peuvent être trouvées par `PATH`. Si un répertoire contrôlé par une personne non autorisée apparaît avant les répertoires système, un programme portant un nom familier pourrait être lancé à sa place.

Pour un outil privilégié :

- utilisez un environnement d'exécution contrôlé ;
- évitez les modifications inutiles de `PATH` ;
- ne chargez pas de configuration non fiable avec `source` ;
- vérifiez les chemins et les permissions des fichiers ;
- évitez d'exécuter du code issu d'une saisie utilisateur.

## 18.4. Les permissions d'un rapport

Un rapport peut contenir des noms de fichiers, des informations de configuration ou d'autres données internes.

Ne choisissez pas ses permissions sans considérer sa sensibilité.

Une politique restrictive peut être définie dans le script :

```bash
umask 077
```

Les nouveaux fichiers créés par le processus seront alors limités par ce masque de création. Les permissions effectives dépendent aussi des permissions demandées par l'outil de création et du contexte.

Cette configuration est utile pour des données personnelles ou des fichiers temporaires qui ne doivent pas être lisibles par les autres utilisateurs.


# 19. Synchronisation avec `flock`

Plusieurs exécutions du même script peuvent se chevaucher. Cette situation peut provoquer des rapports écrasés, des traitements redondants ou des modifications concurrentes.

Sous Linux, `flock` fournit un mécanisme de verrouillage consultatif disponible dans les environnements qui le proposent, notamment avec les utilitaires usuels de nombreuses distributions.

## 19.1. Comprendre le principe

```text
Processus A             Processus B
    |                       |
    | demande le verrou     | demande le verrou
    v                       v
  Obtient le verrou       Attend ou échoue
    |
    v
  Effectue le traitement
    |
    v
  Ferme le descripteur
    |
    v
  Libère le verrou
```

Le verrouillage est consultatif : il protège les ressources contre les autres processus qui respectent le même mécanisme. Il n'empêche pas automatiquement un programme qui ignore le verrou d'écrire dans le fichier.

## 19.2. Exemple avec des descripteurs de fichiers

```bash
#!/usr/bin/env bash

set -u

command -v flock >/dev/null 2>&1 || {
    printf 'Erreur : flock est indisponible.\n' >&2
    exit 1
}

fichier_verrou="$HOME/.cache/outil-inventaire.lock"
repertoire_verrou="${fichier_verrou%/*}"

if ! mkdir -p "$repertoire_verrou"; then
    printf 'Erreur : impossible de préparer le répertoire du verrou.\n' >&2
    exit 1
fi

exec 9>"$fichier_verrou"

if ! flock -n 9; then
    printf 'Une autre exécution semble déjà active.\n' >&2
    exit 1
fi

printf 'Verrou obtenu, traitement autorisé.\n'

# Effectuer ici le traitement protégé.

printf 'Traitement terminé.\n'
```

Explications :

- `exec 9>"$fichier_verrou"` ouvre le fichier associé au descripteur `9` ;
- `flock -n 9` tente d'obtenir le verrou sans attendre ;
- si un autre processus détient le verrou compatible, la tentative échoue ;
- le verrou est associé au descripteur et sera libéré lorsque celui-ci sera fermé ou lorsque le processus se terminera.

Le fichier de verrou ne doit pas être supprimé arbitrairement pendant que des processus peuvent l'utiliser. Supprimer et recréer un fichier de verrou partagé peut créer plusieurs objets de verrouillage distincts.

## 19.3. Quand employer ce mécanisme ?

Utilisez un verrou lorsque deux exécutions simultanées risquent de modifier les mêmes ressources et que leur exécution concurrente n'est pas prévue.

Un verrou n'est pas nécessaire à tous les scripts. Sa présence doit correspondre à un risque réel de concurrence.


# 20. Automatisation avec Cron et systemd

L'automatisation planifiée est une étape naturelle après l'apprentissage de Bash.

Elle exige cependant de connaître la différence entre une exécution dans un terminal interactif et une exécution par un planificateur.

## 20.1. Pourquoi un script peut fonctionner dans un terminal mais échouer dans Cron

Cron fournit souvent un environnement plus limité que celui d'une session interactive.

Par exemple :

- `PATH` peut être différent ;
- le répertoire courant peut ne pas être celui attendu ;
- aucune saisie interactive n'est disponible ;
- les variables personnelles peuvent manquer ;
- les messages peuvent être transmis par un mécanisme différent ;
- l'absence d'un terminal peut modifier le comportement de certaines commandes.

Il faut donc éviter de dépendre implicitement d'un environnement interactif.

## 20.2. Utiliser des chemins absolus

Une commande comme :

```bash
./rapport.sh
```

dépend du répertoire courant.

Un chemin absolu est plus prévisible :

```bash
/home/utilisateur/scripts/rapport.sh
```

Le chemin doit être adapté à la machine où le script sera exécuté.

## 20.3. Préparer les journaux

Un appel de planification peut rediriger les sorties :

```cron
0 6 * * * /home/utilisateur/scripts/rapport.sh >> /home/utilisateur/logs/rapport.log 2>&1
```

Cet exemple illustre une exécution quotidienne à 06 h selon le fuseau horaire et la configuration du planificateur.

Les chemins doivent être adaptés, les répertoires créés au préalable et les permissions vérifiées.

## 20.4. Préférer une tâche système adaptée à son besoin

Sur les distributions utilisant systemd, un service `oneshot` et un timer peuvent constituer une alternative à Cron pour certaines opérations planifiées.

Cette organisation permet notamment de définir le contexte d'exécution, l'utilisateur, les limites de ressources et les relations avec les autres unités.

Il n'est pas nécessaire de choisir systemd pour tous les scripts. Le planificateur doit correspondre à l'architecture d'exploitation du système.

## 20.5. Vérifier le résultat plutôt que le seul lancement

Pour une tâche automatisée, vérifiez :

- son statut de sortie ;
- les messages générés ;
- l'âge et le contenu du rapport ;
- l'existence des fichiers attendus ;
- les erreurs consignées dans les journaux.

Une tâche qui a été lancée n'est pas nécessairement une tâche qui a réussi.


# 21. Tests, analyse statique et qualité

Un script intermédiaire doit être contrôlé au-delà d'un simple lancement réussi.

## 21.1. Vérifier la syntaxe avec Bash

```bash
bash -n script.sh
```

Cette commande demande à Bash d'analyser le script sans exécuter normalement ses commandes.

Elle permet de repérer de nombreuses erreurs de syntaxe. Elle ne détecte pas tous les bugs logiques.

## 21.2. Activer le traçage

```bash
bash -x script.sh
```

Le mode `-x` affiche les commandes au fur et à mesure de leur exécution après expansion.

Il est utile pour comprendre :

- la valeur d'une variable ;
- l'ordre des appels ;
- le chemin choisi par une condition ;
- les arguments transmis à une commande.

Le mode de traçage peut exposer des secrets dans la sortie. Ne l'activez pas imprudemment lorsqu'un script manipule des données confidentielles.

## 21.3. Utiliser ShellCheck

ShellCheck est un outil d'analyse statique spécialement conçu pour détecter de nombreuses erreurs et constructions problématiques dans les scripts shell.

Exécution :

```bash
shellcheck script.sh
```

Il peut signaler, par exemple, une variable qui n'est probablement pas correctement citée ou une construction susceptible de produire un résultat incorrect.

Les diagnostics doivent être compris avant d'être corrigés. Une modification mécanique n'est pas forcément adaptée au comportement attendu du script.

## 21.4. Tester des fonctions isolées

Il est souvent plus simple de tester une petite fonction que de tester un script entier.

Exemple :

```bash
est_identifiant_valide() {
    [[ "$1" =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]
}
```

Test manuel :

```bash
if est_identifiant_valide "serveur_01"; then
    printf 'Test réussi.\n'
else
    printf 'Test échoué.\n'
fi
```

Les fonctions dont les entrées et les sorties sont clairement définies sont plus faciles à tester.

## 21.5. Écrire une assertion simple

Une assertion est un contrôle qui arrête le test lorsque son résultat ne correspond pas à ce qui est attendu.

```bash
assert_egal() {
    local attendu="$1"
    local obtenu="$2"

    if [[ "$attendu" == "$obtenu" ]]; then
        printf 'OK : attendu = obtenu = %s\n' "$attendu"
    else
        printf 'ÉCHEC : attendu <%s>, obtenu <%s>\n' \
            "$attendu" "$obtenu" >&2
        return 1
    fi
}
```

Utilisation :

```bash
assert_egal "bonjour" "bonjour"
assert_egal "42" "42"
```

Une assertion qui retourne un statut non nul peut être employée par un outil d'exécution de tests pour signaler un échec.

## 21.6. Tester le statut de sortie

```bash
commande_test
statut=$?

if (( statut != 0 )); then
    printf 'Le test a échoué avec le statut %s.\n' "$statut" >&2
fi
```

Le statut doit être récupéré immédiatement après la commande ciblée.

Pour des tests automatiques, il est généralement préférable de terminer le test avec un statut non nul lorsqu'une assertion échoue, afin que le résultat puisse être consommé par un outil de test ou une chaîne d'intégration continue.

## 21.7. Découvrir Bats

Bats, ou *Bash Automated Testing System*, est un framework de tests pour les programmes Bash et les outils Unix.

Il permet d'écrire des cas de test qui vérifient les sorties, les statuts et le comportement du programme.

Exemple conceptuel :

```bash
@test "l'outil affiche une erreur sans argument" {
    run ./outil.sh

    [ "$status" -eq 2 ]
}
```

Cet exemple utilise la syntaxe Bats ; il ne s'exécute pas comme un script Bash ordinaire.

La documentation officielle de Bats explique l'installation, la création des tests, les assertions et l'organisation des suites de tests.


# 22. Méthodes de développement et dépannage

## 22.1. Tester d'abord dans un répertoire temporaire contrôlé

Avant de modifier une arborescence importante, utilisez un environnement de laboratoire :

```bash
laboratoire="$(mktemp -d)" || exit 1
printf 'Répertoire de laboratoire : %s\n' "$laboratoire"
```

Cette commande crée un répertoire temporaire et affiche son chemin.

Pour un script durable, prévoyez le nettoyage de ce répertoire avec `trap`, et n'utilisez jamais une variable de chemin non vérifiée dans une opération destructive.

## 22.2. Tester plusieurs scénarios

Un bon plan de test contient au minimum :

| Scénario | Objectif |
|---|---|
| Entrée valide | confirmer le fonctionnement normal |
| Argument absent | contrôler la validation |
| Fichier absent | vérifier le diagnostic |
| Chemin avec espaces | vérifier les guillemets |
| Permission refusée | vérifier les erreurs système |
| Répertoire vide | confirmer le cas sans résultat |
| Écriture impossible | vérifier que l'ancien rapport reste intact |
| Interruption | vérifier le nettoyage prévu |

Les scénarios pertinents varient selon le script. Il faut retenir ceux qui correspondent à ses responsabilités réelles.

## 22.3. Ne pas mélanger calcul, affichage et accès disque

Une fonction peut être organisée autour d'une opération unique.

Par exemple :

- `valider_chemin` vérifie une entrée ;
- `collecter_fichiers` découvre les fichiers ;
- `generer_ligne` construit une sortie ;
- `publier_rapport` écrit ou remplace le rapport.

Cette séparation facilite la compréhension, le test et le diagnostic.

## 22.4. Documenter les limites

Un script correctement documenté décrit aussi ce qu'il ne garantit pas.

Par exemple, un outil qui contrôle la présence de fichiers à un instant donné ne garantit pas qu'ils resteront présents après le contrôle.

De même, un rapport produit avec succès peut être incomplet du point de vue métier si certaines sources sont absentes ou si des données sont illisibles.

La documentation doit décrire les hypothèses, les permissions requises et le sens des statuts de sortie.


# 23. Travaux pratiques guidés

Les TP suivants regroupent les nouvelles compétences. Ils doivent être réalisés dans le répertoire de laboratoire du cours débutant ou dans une arborescence équivalente.

## TP 1 — Créer une CLI avec `getopts`

### Objectif

Créer un script qui accepte `-n NOM`, `-e ENVIRONNEMENT` et `-h`.

### Code

Fichier : `cli-intermediaire.sh`

```bash
#!/usr/bin/env bash

set -u

nom=""
environnement="laboratoire"

usage() {
    cat <<'EOF'
Usage : cli-intermediaire.sh -n NOM [-e ENVIRONNEMENT] [-h]

Options :
  -n NOM             Nom obligatoire
  -e ENVIRONNEMENT   Environnement, par défaut laboratoire
  -h                 Afficher l'aide
EOF
}

while getopts ":n:e:h" option; do
    case "$option" in
        n)
            nom="$OPTARG"
            ;;
        e)
            environnement="$OPTARG"
            ;;
        h)
            usage
            exit 0
            ;;
        :)
            printf 'Erreur : -%s exige un argument.\n' "$OPTARG" >&2
            usage >&2
            exit 2
            ;;
        \?)
            printf 'Erreur : option inconnue -%s.\n' "$OPTARG" >&2
            usage >&2
            exit 2
            ;;
    esac
done

shift "$((OPTIND - 1))"

if [[ $# -ne 0 ]]; then
    printf 'Erreur : arguments positionnels non prévus.\n' >&2
    usage >&2
    exit 2
fi

if [[ -z "$nom" ]]; then
    printf 'Erreur : -n NOM est obligatoire.\n' >&2
    usage >&2
    exit 2
fi

printf 'Nom : %s\n' "$nom"
printf 'Environnement : %s\n' "$environnement"
```

### Tests

```bash
bash cli-intermediaire.sh -h
bash cli-intermediaire.sh -n serveur01
bash cli-intermediaire.sh -n serveur01 -e production
bash cli-intermediaire.sh -e production
bash cli-intermediaire.sh -z
```

Les deux premières commandes doivent afficher respectivement l'aide et les paramètres. Les deux dernières illustrent des erreurs d'utilisation différentes.

### Compétences acquises

- interface de commande ;
- validation des options ;
- gestion des arguments restants ;
- codes de retour cohérents.


## TP 2 — Utiliser un tableau associatif

### Objectif

Définir une correspondance entre environnements et répertoires.

### Code

Fichier : `environnements.sh`

```bash
#!/usr/bin/env bash

set -u

declare -A repertoires=(
    [laboratoire]="$HOME/lab-scripting"
    [rapports]="$HOME/lab-scripting/rapports"
    [donnees]="$HOME/lab-scripting/donnees"
)

environnement="${1:-}"

if [[ -z "$environnement" ]]; then
    printf 'Usage : %s ENVIRONNEMENT\n' "$0" >&2
    exit 2
fi

if [[ -v "repertoires[$environnement]" ]]; then
    printf 'Environnement : %s\n' "$environnement"
    printf 'Répertoire associé : %s\n' "${repertoires[$environnement]}"
else
    printf 'Environnement inconnu : %s\n' "$environnement" >&2
    exit 1
fi
```

### Exécution

```bash
bash environnements.sh laboratoire
bash environnements.sh rapports
bash environnements.sh inconnu
```

### Point important

Cette association constitue une configuration en mémoire. Elle ne prouve pas que le répertoire existe. Pour vérifier son état, ajoutez un test `[[ -d ... ]]` et décidez de la conduite à tenir lorsque le chemin n'est pas disponible.


## TP 3 — Lire une liste de fichiers en préservant les noms

### Objectif

Parcourir tous les fichiers `.log` d'un répertoire sans utiliser la sortie de `ls` comme une liste de chemins.

### Préparation

```bash
mkdir -p "$HOME/lab-scripting/fichiers"
touch "$HOME/lab-scripting/fichiers/serveur.log"
touch "$HOME/lab-scripting/fichiers/rapport annuel.log"
```

### Code

Fichier : `parcourir-logs.sh`

```bash
#!/usr/bin/env bash

set -u

repertoire="${1:-$HOME/lab-scripting/fichiers}"

if [[ ! -d "$repertoire" ]]; then
    printf 'Erreur : répertoire invalide.\n' >&2
    exit 1
fi

liste_temporaire="$(mktemp)" || {
    printf 'Erreur : création du fichier temporaire impossible.\n' >&2
    exit 1
}

nettoyer() {
    if [[ -n "$liste_temporaire" && -e "$liste_temporaire" ]]; then
        rm -f -- "$liste_temporaire"
    fi
}

trap nettoyer EXIT

if ! find "$repertoire" -type f -name '*.log' -print0 > "$liste_temporaire"; then
    printf 'Erreur : recherche impossible.\n' >&2
    exit 1
fi

nombre=0

while IFS= read -r -d '' chemin; do
    nombre=$((nombre + 1))
    printf 'Fichier %d : %q\n' "$nombre" "$chemin"
done < "$liste_temporaire"

printf 'Nombre de fichiers trouvés : %d\n' "$nombre"
```

### Vérification

```bash
bash parcourir-logs.sh
```

Le rapport doit contenir les deux noms de fichiers créés, chacun traité comme un chemin unique.

### Compétences acquises

- `find` ;
- séparateurs NUL ;
- lecture avec `read -d ''` ;
- compteur ;
- `trap` ;
- contrôle du statut de la commande de recherche.


## TP 4 — Publier un rapport sans remplacer prématurément l'ancien

### Objectif

Créer un rapport temporaire, contrôler l'écriture puis publier le résultat.

### Code

Fichier : `rapport-atomique.sh`

```bash
#!/usr/bin/env bash

set -u

repertoire="$HOME/lab-scripting"
rapport="$repertoire/rapport-atomique.txt"

if ! mkdir -p "$repertoire"; then
    printf 'Erreur : préparation du répertoire impossible.\n' >&2
    exit 1
fi

temporaire="$(mktemp "$repertoire/.rapport.XXXXXX")" || {
    printf 'Erreur : création du temporaire impossible.\n' >&2
    exit 1
}

nettoyer() {
    if [[ -n "$temporaire" && -e "$temporaire" ]]; then
        rm -f -- "$temporaire"
    fi
}

trap nettoyer EXIT

if ! {
    printf 'Rapport d’exemple\n'
    printf 'Date : %s\n' "$(date)"
    printf 'Machine : %s\n' "$(hostname)"
} > "$temporaire"; then
    printf 'Erreur : écriture impossible.\n' >&2
    exit 1
fi

if ! mv -f -- "$temporaire" "$rapport"; then
    printf 'Erreur : publication impossible.\n' >&2
    exit 1
fi

printf 'Rapport publié : %s\n' "$rapport"
```

### Travail complémentaire

Modifiez ce script pour ajouter :

- un compteur ;
- une fonction de journalisation ;
- un code distinct pour une erreur de configuration ;
- un test de syntaxe automatisé.


# 24. Exercices corrigés

## Exercice 1 — Valider le nombre d'arguments

**Énoncé :** écrivez une fonction qui exige exactement deux arguments et renvoie `2` si le nombre d'arguments est incorrect.

### Correction

```bash
verifier_nombre_arguments() {
    if [[ $# -ne 2 ]]; then
        return 2
    fi

    return 0
}
```

Utilisation :

```bash
if verifier_nombre_arguments "a" "b"; then
    printf 'Nombre d’arguments correct.\n'
else
    printf 'Nombre d’arguments incorrect.\n' >&2
fi
```

La fonction valide le nombre d'arguments qui lui sont transmis, pas celui de l'appelant original. Elle doit donc être appelée en lui passant les valeurs que l'on souhaite vérifier.

## Exercice 2 — Extraire un nom de fichier

**Énoncé :** récupérez `serveur.log` à partir de `/var/log/serveur.log`.

### Correction

```bash
chemin="/var/log/serveur.log"
nom="${chemin##*/}"

printf '%s\n' "$nom"
```

La construction supprime le plus long préfixe correspondant au motif `*/`.

## Exercice 3 — Valider une version

**Énoncé :** acceptez uniquement les chaînes de la forme `app-X.Y.Z`, où `X`, `Y` et `Z` contiennent chacun au moins un chiffre.

### Correction

```bash
version="app-2.14.7"

if [[ "$version" =~ ^app-([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    printf 'Version valide.\n'
    printf 'Majeure : %s\n' "${BASH_REMATCH[1]}"
    printf 'Mineure : %s\n' "${BASH_REMATCH[2]}"
    printf 'Correctif : %s\n' "${BASH_REMATCH[3]}"
else
    printf 'Version invalide.\n' >&2
    exit 1
fi
```

L'expression vérifie le format. Elle n'effectue pas de comparaison sémantique entre les versions.

## Exercice 4 — Comprendre l'effet d'un pipeline

**Énoncé :** pourquoi cette boucle ne conserve-t-elle pas nécessairement la valeur finale du compteur dans le shell parent ?

```bash
compteur=0

printf '%s\n' a b c | while IFS= read -r ligne; do
    compteur=$((compteur + 1))
done

printf '%s\n' "$compteur"
```

### Correction

La boucle placée dans le pipeline s'exécute normalement dans un sous-shell avec Bash. Les modifications du compteur sont donc réalisées dans cet environnement séparé.

Une correction lorsque l'on souhaite conserver le compteur consiste à rediriger l'entrée de la boucle :

```bash
compteur=0

while IFS= read -r ligne; do
    compteur=$((compteur + 1))
done < <(printf '%s\n' a b c)

printf '%s\n' "$compteur"
```

Le statut de la commande productrice doit toutefois être traité séparément si sa réussite est essentielle.

## Exercice 5 — Nettoyer un fichier temporaire

**Énoncé :** créez un fichier temporaire puis programmez sa suppression lors de la sortie du script.

### Correction

```bash
#!/usr/bin/env bash

set -u

temporaire=""

nettoyer() {
    if [[ -n "$temporaire" && -e "$temporaire" ]]; then
        rm -f -- "$temporaire"
    fi
}

trap nettoyer EXIT

temporaire="$(mktemp)" || {
    printf 'Création impossible.\n' >&2
    exit 1
}

printf 'Travail en cours.\n' > "$temporaire"
cat -- "$temporaire"
```

Le fichier est supprimé lors de la sortie normale. Un signal non interceptable comme `SIGKILL` peut empêcher le nettoyage.

## Exercice 6 — Distinguer un argument absent d'une chaîne vide

**Énoncé :** expliquez la différence entre :

```bash
valeur="${1:-défaut}"
```

et :

```bash
valeur="${1-défaut}"
```

### Correction

La première forme utilise `défaut` lorsque le premier argument est absent ou vide.

La seconde utilise `défaut` seulement lorsque le premier argument est absent. Si l'argument existe mais contient une chaîne vide, cette chaîne vide est conservée.

## Exercice 7 — Corriger un traitement de chemins

**Énoncé :** expliquez pourquoi cette commande n'est pas robuste :

```bash
for fichier in $(find "$repertoire" -type f); do
    printf '%s\n' "$fichier"
done
```

### Correction

La sortie de `find` est substituée en texte puis découpée en mots. Les chemins contenant des espaces ou des retours à la ligne peuvent donc être fragmentés.

Une meilleure approche est :

```bash
while IFS= read -r -d '' fichier; do
    printf '%q\n' "$fichier"
done < <(find "$repertoire" -type f -print0)
```

Si le statut de `find` doit être vérifié avant le traitement, enregistrez d'abord sa sortie dans un fichier temporaire, contrôlez son statut puis parcourez le fichier.

## Exercice 8 — Définir une convention d'erreur

**Énoncé :** un outil doit utiliser `0` pour le succès, `1` pour un échec de traitement et `2` pour une utilisation incorrecte. Montrez comment traiter un argument manquant.

### Correction

```bash
#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s CHEMIN\n' "$0" >&2
    exit 2
fi

if [[ ! -d "$1" ]]; then
    printf 'Erreur : répertoire invalide.\n' >&2
    exit 1
fi

printf 'Répertoire accepté.\n'
exit 0
```

Les codes sont clairement définis par le programme et peuvent donc être utilisés par un autre script appelant.


# 25. Projet final — Outil d'inventaire des fichiers journaux

## 25.1. Contexte

Vous devez créer un outil réutilisable qui recense les fichiers se terminant par `.log` dans une arborescence.

Le programme doit être utilisable depuis un terminal et par un autre script.

Il doit accepter des options, gérer des erreurs, conserver les noms de fichiers particuliers, produire un rapport et renvoyer un statut cohérent.

## 25.2. Cahier des charges

Le script doit :

1. accepter `-d REPERTOIRE` pour définir la source ;
2. accepter `-o FICHIER` pour définir le rapport ;
3. accepter `-h` pour afficher l'aide ;
4. vérifier l'existence du répertoire source ;
5. vérifier la présence des outils nécessaires ;
6. détecter les fichiers ordinaires se terminant par `.log` ;
7. conserver les chemins avec espaces ou caractères particuliers ;
8. relever la taille de chaque fichier ;
9. calculer le nombre de fichiers et leur taille cumulée ;
10. créer le rapport par l'intermédiaire d'un fichier temporaire ;
11. remplacer le rapport final seulement lorsque le traitement de recherche a réussi ;
12. nettoyer les fichiers temporaires lors de la sortie normale ou des interruptions interceptables ;
13. retourner `0` si le traitement aboutit sans erreur ;
14. retourner `1` en cas d'échec de traitement ;
15. retourner `2` en cas d'arguments ou d'options incorrects.

Le traitement cible ici les fichiers locaux d'une arborescence Linux. Il ne cherche pas à inventorier des montages distants ou des fichiers dont la taille n'est pas accessible.

## 25.3. Code complet

Fichier : `inventaire-logs.sh`

```bash
#!/usr/bin/env bash

# Nom : inventaire-logs.sh
# Objet : inventorier les fichiers .log d'un répertoire.
#
# Usage :
#   ./inventaire-logs.sh [-d REPERTOIRE] [-o RAPPORT] [-h]
#
# Codes de retour :
#   0 : inventaire terminé sans erreur
#   1 : erreur de traitement
#   2 : arguments ou options invalides
#
# Dépendances :
#   Bash, find, stat, mktemp, dirname, mkdir, mv, rm et date.
#   stat est utilisé selon la syntaxe GNU disponible sous Linux.

set -u
set -o pipefail

repertoire="${PWD}"
rapport="${HOME:-$PWD}/lab-scripting/rapports/inventaire-logs.txt"

declare -a temporaires=()

usage() {
    cat <<'EOF'
Usage :
  inventaire-logs.sh [-d REPERTOIRE] [-o RAPPORT] [-h]

Options :
  -d REPERTOIRE   Répertoire à analyser. Par défaut : répertoire courant.
  -o RAPPORT      Fichier de rapport.
  -h              Afficher cette aide.

Description :
  Recherche récursivement les fichiers ordinaires en .log,
  en relève la taille et génère un rapport.
EOF
}

erreur() {
    printf 'ERREUR : %s\n' "$*" >&2
}

nettoyer() {
    local fichier

    for fichier in "${temporaires[@]}"; do
        if [[ -n "$fichier" && -e "$fichier" ]]; then
            rm -f -- "$fichier"
        fi
    done
}

quitter_erreur() {
    erreur "$*"
    exit 1
}

trap nettoyer EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

while getopts ":d:o:h" option; do
    case "$option" in
        d)
            repertoire="$OPTARG"
            ;;
        o)
            rapport="$OPTARG"
            ;;
        h)
            usage
            exit 0
            ;;
        :)
            erreur "l'option -$OPTARG exige une valeur."
            usage >&2
            exit 2
            ;;
        \?)
            erreur "option inconnue : -$OPTARG."
            usage >&2
            exit 2
            ;;
    esac
done

shift "$((OPTIND - 1))"

if [[ $# -ne 0 ]]; then
    erreur "arguments positionnels non prévus."
    usage >&2
    exit 2
fi

if [[ -z "$repertoire" ]]; then
    erreur "le répertoire source ne peut pas être vide."
    exit 2
fi

if [[ -z "$rapport" ]]; then
    erreur "le chemin du rapport ne peut pas être vide."
    exit 2
fi

if [[ ! -d "$repertoire" ]]; then
    quitter_erreur "répertoire source invalide : $repertoire"
fi

if [[ -d "$rapport" ]]; then
    quitter_erreur "la destination du rapport désigne un répertoire."
fi

for commande in find stat mktemp dirname mkdir mv rm date; do
    if ! command -v "$commande" >/dev/null 2>&1; then
        quitter_erreur "commande requise indisponible : $commande"
    fi
done

if [[ ! -r "$repertoire" || ! -x "$repertoire" ]]; then
    quitter_erreur "le répertoire source n'est pas accessible en lecture ou traversée."
fi

date_controle="$(date '+%Y-%m-%d %H:%M:%S')" || {
    quitter_erreur "impossible de lire la date."
}

repertoire_sortie="$(dirname -- "$rapport")" || {
    quitter_erreur "impossible de déterminer le répertoire du rapport."
}

if ! mkdir -p -- "$repertoire_sortie"; then
    quitter_erreur "impossible de préparer le répertoire de sortie."
fi

liste_temporaire="$(mktemp)" || {
    quitter_erreur "impossible de créer la liste temporaire."
}

temporaires+=("$liste_temporaire")

rapport_temporaire="$(mktemp "$repertoire_sortie/.inventaire.XXXXXX")" || {
    quitter_erreur "impossible de créer le rapport temporaire."
}

temporaires+=("$rapport_temporaire")

if ! find "$repertoire" -type f -name '*.log' -print0 > "$liste_temporaire"; then
    quitter_erreur "la recherche des fichiers a échoué."
fi

if ! {
    printf '%s\n' "=== Inventaire des fichiers journaux ==="
    printf 'Date du contrôle : %s\n' "$date_controle"
    printf 'Répertoire source : %q\n' "$repertoire"
    printf 'Rapport demandé : %q\n' "$rapport"
    printf '\n'
} > "$rapport_temporaire"; then
    quitter_erreur "impossible d'écrire l'en-tête du rapport."
fi

nombre_fichiers=0
taille_totale=0
nombre_erreurs=0

while IFS= read -r -d '' chemin; do
    if taille="$(stat -c '%s' -- "$chemin")"; then
        :
    else
        nombre_erreurs=$((nombre_erreurs + 1))

        if ! printf 'ERREUR_TAILLE : %q\n' "$chemin" >> "$rapport_temporaire"; then
            quitter_erreur "impossible de poursuivre l'écriture du rapport."
        fi

        continue
    fi

    if [[ ! "$taille" =~ ^[0-9]+$ ]]; then
        nombre_erreurs=$((nombre_erreurs + 1))

        if ! printf 'ERREUR_FORMAT_TAILLE : %q\n' "$chemin" >> "$rapport_temporaire"; then
            quitter_erreur "impossible de poursuivre l'écriture du rapport."
        fi

        continue
    fi

    nombre_fichiers=$((nombre_fichiers + 1))
    taille_totale=$((taille_totale + taille))

    if ! printf 'FICHIER : %q | TAILLE_OCTETS : %s\n' \
        "$chemin" "$taille" >> "$rapport_temporaire"; then
        quitter_erreur "impossible d'écrire une ligne du rapport."
    fi
done < "$liste_temporaire"

if ! {
    printf '\n'
    printf 'Nombre de fichiers mesurés : %s\n' "$nombre_fichiers"
    printf 'Taille cumulée en octets : %s\n' "$taille_totale"
    printf 'Nombre d'erreurs de mesure : %s\n' "$nombre_erreurs"
} >> "$rapport_temporaire"; then
    quitter_erreur "impossible d'écrire le résumé."
fi

if ! mv -f -- "$rapport_temporaire" "$rapport"; then
    quitter_erreur "impossible de publier le rapport."
fi

printf 'Inventaire terminé.\n'
printf 'Fichiers mesurés : %s\n' "$nombre_fichiers"
printf 'Taille cumulée : %s octets\n' "$taille_totale"
printf 'Erreurs de mesure : %s\n' "$nombre_erreurs"
printf 'Rapport : %s\n' "$rapport"

if (( nombre_erreurs > 0 )); then
    exit 1
fi

exit 0
```

## 25.4. Comprendre l'architecture du projet

```text
                    OPTIONS
                       |
                       v
              Validation des chemins
                       |
                       v
                Vérification outils
                       |
                       v
            Création des temporaires
                       |
                       v
             Recherche avec find -print0
                       |
                       v
           Lecture des chemins avec read
                       |
                       v
                Mesure avec stat
                       |
                       v
               Génération rapport
                       |
                       v
             Publication avec mv
                       |
                       v
               Statut final
```

### Étape 1 : les options

`getopts` gère les options `-d`, `-o` et `-h`.

Le script vérifie également qu'aucun argument positionnel inattendu ne reste après l'analyse.

### Étape 2 : la validation

Le script contrôle la présence des chemins, le type du répertoire source et la disponibilité des outils nécessaires.

Cela permet de détecter certaines erreurs avant de commencer les traitements.

### Étape 3 : la recherche

`find -print0` préserve la délimitation des noms de fichiers, y compris lorsqu'ils contiennent des espaces ou des retours à la ligne.

La sortie est écrite dans un fichier temporaire. Le programme vérifie le statut de `find` avant de commencer l'exploitation des résultats.

### Étape 4 : la mesure

`stat -c '%s'` récupère la taille d'un fichier en octets dans les environnements qui fournissent la syntaxe GNU de `stat`.

Un fichier peut disparaître ou devenir inaccessible entre sa découverte et sa mesure. Le script enregistre ce cas comme une erreur de mesure.

### Étape 5 : le rapport

Le fichier temporaire est créé dans le répertoire de destination du rapport.

Le rapport final n'est remplacé qu'après le traitement et l'écriture du résumé.

Les lignes utilisent `%q` pour produire une représentation échappée des chemins, ce qui facilite la lecture de noms inhabituels. Cette représentation est destinée au diagnostic humain et ne constitue pas un format universel d'échange de données.

### Étape 6 : le statut

Le script renvoie `1` lorsqu'une ou plusieurs mesures échouent, même si un rapport a pu être publié.

Il renvoie `0` si l'inventaire ne comporte pas d'erreur de mesure et que les étapes de traitement se sont déroulées normalement.

Il renvoie `2` pour les erreurs de ligne de commande.

## 25.5. Préparer un environnement de test

```bash
mkdir -p "$HOME/lab-scripting/logs-test"
mkdir -p "$HOME/lab-scripting/rapports"
```

Créer quelques fichiers :

```bash
printf 'Ligne 1\nLigne 2\n' > "$HOME/lab-scripting/logs-test/serveur.log"
printf 'Erreur simulée\n' > "$HOME/lab-scripting/logs-test/erreur serveur.log"
```

Tester la commande :

```bash
bash inventaire-logs.sh \
    -d "$HOME/lab-scripting/logs-test" \
    -o "$HOME/lab-scripting/rapports/inventaire-logs.txt"
```

Consulter le rapport :

```bash
cat "$HOME/lab-scripting/rapports/inventaire-logs.txt"
```

Vérifier la syntaxe :

```bash
bash -n inventaire-logs.sh
```

Vérifier le code avec ShellCheck si l'outil est installé :

```bash
shellcheck inventaire-logs.sh
```

## 25.6. Tests à effectuer

| Test | Résultat attendu |
|---|---|
| Répertoire contenant deux fichiers `.log` | deux fichiers mesurés, si leur lecture réussit |
| Aucun fichier `.log` | rapport valide avec zéro fichier mesuré |
| Répertoire inexistant | échec explicite |
| Option inconnue | erreur d'utilisation et code `2` |
| Valeur manquante après `-d` | erreur d'utilisation et code `2` |
| Fichier avec des espaces | chemin préservé |
| Échec de création du rapport | erreur, sans publication du nouveau rapport |
| Erreur de mesure | ligne diagnostique et code final non nul |

Une opération de test peut également confirmer que l'ancien rapport n'est pas remplacé si la recherche échoue.

## 25.7. Limites du projet

Ce programme est plus robuste qu'un script débutant, mais il possède encore des limites.

- La taille cumulée est calculée avec l'arithmétique entière de Bash ; un inventaire exceptionnellement grand peut dépasser les limites de l'arithmétique de la plateforme.
- Les informations relevées sont des instantanés : l'état des fichiers peut changer après le contrôle.
- Le rapport est un format textuel destiné à l'administration, pas un format d'échange structuré garanti.
- Les erreurs de mesure sont documentées, mais les questions de droits, de montages spéciaux et de concurrence avancée ne sont pas entièrement résolues.
- Le remplacement du rapport ne constitue pas à lui seul une garantie de durabilité matérielle.
- Le script n'efface pas les fichiers sources et ne modifie pas leur contenu.

Un niveau expert pourra approfondir les contrôles transactionnels, les formats de sortie structurés, la gestion des données à grande échelle, les tests automatisés complets et l'observabilité des tâches d'administration.


# 26. Grille de compétences

Avant de passer au niveau expert, vérifiez que vous pouvez démontrer les capacités suivantes.

## Ligne de commande

- [ ] Je sais analyser des options avec `getopts`.
- [ ] Je sais afficher une aide cohérente.
- [ ] Je sais valider des arguments et renvoyer un statut documenté.
- [ ] Je sais distinguer une erreur d'utilisation d'un échec du traitement.

## Variables et fonctions

- [ ] Je sais utiliser les expansions `${var:-défaut}` et `${var:?message}`.
- [ ] Je sais extraire un préfixe ou un suffixe avec les expansions Bash.
- [ ] Je sais travailler avec des tableaux indexés.
- [ ] Je sais utiliser des tableaux associatifs.
- [ ] Je sais organiser un script autour d'une fonction `main`.
- [ ] Je sais employer `local` pour limiter la portée des variables.

## Fichiers et flux

- [ ] Je sais préserver les chemins contenant des espaces.
- [ ] Je sais expliquer pourquoi `for fichier in $(find ...)` est fragile.
- [ ] Je sais utiliser `find -print0` avec `read -d ''`.
- [ ] Je sais distinguer sortie standard et sortie d'erreur.
- [ ] Je sais contrôler le statut d'une commande importante.
- [ ] Je sais expliquer le comportement d'un pipeline et d'un sous-shell.

## Fiabilité

- [ ] Je sais distinguer les options `-e`, `-u` et `pipefail`.
- [ ] Je sais installer un nettoyage avec `trap`.
- [ ] Je sais utiliser `mktemp`.
- [ ] Je sais créer un rapport temporaire puis le publier.
- [ ] Je sais mettre en place une journalisation cohérente.
- [ ] Je sais expliquer les limites d'un verrou `flock`.

## Qualité

- [ ] Je sais contrôler la syntaxe avec `bash -n`.
- [ ] Je sais déboguer avec `bash -x`.
- [ ] Je sais utiliser ShellCheck.
- [ ] Je sais écrire une fonction testable.
- [ ] Je sais concevoir des scénarios de test normaux et d'erreur.
- [ ] Je sais documenter les hypothèses et les codes de retour.


# 27. Fiche de révision

## Analyser des options

```bash
while getopts ":d:o:h" option; do
    case "$option" in
        d) repertoire="$OPTARG" ;;
        o) rapport="$OPTARG" ;;
        h) usage; exit 0 ;;
        :) printf 'Valeur manquante.\n' >&2; exit 2 ;;
        \?) printf 'Option inconnue.\n' >&2; exit 2 ;;
    esac
done

shift "$((OPTIND - 1))"
```

## Valeurs par défaut

```bash
valeur="${VARIABLE:-défaut}"
```

## Exiger une variable

```bash
: "${VARIABLE:?Cette variable est obligatoire}"
```

## Extraire le nom final d'un chemin

```bash
nom="${chemin##*/}"
```

## Retirer une extension connue

```bash
sans_extension="${nom%.log}"
```

## Tableau indexé

```bash
declare -a elements=("a" "b" "c")

for element in "${elements[@]}"; do
    printf '%s\n' "$element"
done
```

## Tableau associatif

```bash
declare -A ports=(
    [ssh]=22
    [http]=80
)
```

## Tester une expression régulière

```bash
if [[ "$valeur" =~ ^[0-9]+$ ]]; then
    printf 'Format valide.\n'
fi
```

## Préserver les compteurs

```bash
while IFS= read -r ligne; do
    compteur=$((compteur + 1))
done < <(commande)
```

Cette construction ne garantit pas à elle seule que l'échec de `commande` sera propagé à la boucle.

## Parcourir des noms de fichiers complexes

```bash
while IFS= read -r -d '' fichier; do
    printf '%q\n' "$fichier"
done < <(find "$repertoire" -type f -print0)
```

Utilisez un fichier temporaire intermédiaire si vous devez contrôler explicitement la réussite de `find` avant de consommer les résultats.

## Nettoyage

```bash
nettoyer() {
    if [[ -n "$temporaire" && -e "$temporaire" ]]; then
        rm -f -- "$temporaire"
    fi
}

trap nettoyer EXIT
```

## Verrouillage non bloquant

```bash
exec 9>"$fichier_verrou"
flock -n 9
```

Le mécanisme exige que les autres processus coopèrent avec le même verrou.

## Contrôle de qualité

```bash
bash -n script.sh
bash -x script.sh
shellcheck script.sh
```

## Principes à conserver

1. Les guillemets protègent les arguments, mais ne remplacent pas la validation des données.
2. La présence d'un chemin ne garantit pas que l'opération suivante réussira.
3. La sortie standard et la sortie d'erreur doivent être gérées intentionnellement.
4. Les codes de retour doivent être définis et documentés.
5. Un fichier temporaire doit être créé avec une méthode adaptée et nettoyé autant que possible.
6. Une publication par renommage peut améliorer l'intégrité d'un rapport, mais ne remplace pas les sauvegardes.
7. `set -e` n'est pas un mécanisme universel de gestion des erreurs.
8. Les opérations à privilèges élevés exigent un environnement et des chemins contrôlés.
9. Les noms de fichiers Unix peuvent contenir des caractères qui rendent une liste ligne par ligne ambiguë.
10. Les tests doivent inclure les cas d'erreur, pas uniquement les cas normaux.


# 28. Glossaire

**Argument positionnel** : valeur reçue par un script ou une fonction à une position donnée.

**Assertion** : vérification utilisée dans un test pour comparer le résultat obtenu à un résultat attendu.

**Bats** : framework de tests destiné aux scripts Bash et aux programmes Unix.

**Code de retour** : statut numérique communiqué par une commande ou un script.

**Configuration** : ensemble de paramètres qui influencent le comportement du programme.

**Descripteur de fichier** : identifiant d'un flux ouvert par un processus, notamment les descripteurs standards 0, 1 et 2.

**Expression régulière** : motif permettant de reconnaître ou de valider une chaîne selon des règles définies.

**Fichier temporaire** : fichier créé pour stocker un résultat intermédiaire ou préparer un traitement.

**`flock`** : outil Linux de verrouillage consultatif, lorsque l'utilitaire et le système de fichiers employés le prennent en charge.

**Journalisation** : production structurée de messages permettant de suivre et de diagnostiquer une exécution.

**`getopts`** : commande intégrée de Bash qui analyse des options courtes de ligne de commande.

**Sous-shell** : environnement de shell distinct utilisé pour certaines opérations, notamment les substitutions de commande.

**Substitution de commande** : mécanisme `$(...)` permettant de récupérer la sortie standard d'une commande.

**Substitution de processus** : mécanisme Bash permettant d'exposer l'entrée ou la sortie d'un processus au moyen d'un chemin.

**Tableau associatif** : tableau dont les clés sont textuelles plutôt que numériques.

**`trap`** : commande intégrée de Bash permettant d'associer des actions à certains signaux ou à la sortie du shell.

**Validation** : contrôle visant à vérifier qu'une entrée respecte le format, les limites et les exigences du programme.

**Publication atomique** : technique qui remplace une destination par un fichier préparé en amont, généralement au moyen d'un renommage sur le même système de fichiers.

**`pipefail`** : option Bash qui modifie le statut renvoyé par un pipeline lorsque l'une de ses commandes échoue.


# 29. Documentation et références officielles

Les ressources ci-dessous constituent les références principales pour approfondir les fonctionnalités utilisées dans ce cours.

## Manuel officiel de Bash

- **GNU Bash Reference Manual** — expansions, variables, tableaux, fonctions, gestion des paramètres, redirections, signaux et commandes intégrées :  
  https://www.gnu.org/software/bash/manual/bash.html

- **Expansions de Bash** — ordre des expansions, découpage en mots et expansion des noms de fichiers :  
  https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html

- **Substitution de processus** — mécanisme `<(...)` et `>(...)` :  
  https://www.gnu.org/software/bash/manual/html_node/Process-Substitution.html

## Analyse statique

- **ShellCheck** — outil d'analyse des scripts shell :  
  https://www.shellcheck.net/

- **Documentation du projet ShellCheck** — explications des avertissements, règles et exemples :  
  https://github.com/koalaman/shellcheck

## Tests automatisés

- **Bats — Bash Automated Testing System** — documentation, tutoriel et organisation de suites de tests :  
  https://bats-core.readthedocs.io/en/stable/

## Utilitaires GNU

- **GNU Coreutils** — documentation des outils usuels comme `stat`, `sort`, `comm` et `timeout` :  
  https://www.gnu.org/software/coreutils/manual/coreutils.html

Pour `find`, consultez la documentation GNU Findutils :  
https://www.gnu.org/software/findutils/manual/html_mono/find.html

## Bonnes pratiques d'apprentissage

Pour chaque nouvelle fonctionnalité, suivez une progression :

1. lisez la syntaxe officielle ;
2. écrivez un exemple minimal ;
3. testez le comportement attendu ;
4. testez un cas d'erreur ;
5. vérifiez les effets sur les variables et les fichiers ;
6. contrôlez le script avec ShellCheck ;
7. documentez les hypothèses qui influencent le résultat.

Il n'est pas nécessaire de mémoriser l'intégralité du manuel Bash. Il est plus important de comprendre les mécanismes sur lesquels vos scripts reposent et de savoir retrouver la documentation lorsque le comportement devient subtil.


# Conclusion

Le scripting intermédiaire vise à rendre les automatisations Linux plus solides et plus faciles à maintenir.

Vous avez approfondi la gestion des paramètres, la manipulation des tableaux, les fonctions, les expressions régulières, les flux d'entrée et de sortie, le comportement des sous-shells, les parcours robustes de fichiers, les erreurs, les signaux, les fichiers temporaires, la journalisation, les verrous et les tests.

Le projet final réunit ces compétences dans un véritable outil d'inventaire, avec une interface de commande, un contrôle des dépendances, une exploration récursive, un rapport temporaire, une publication contrôlée et une convention de statuts.

**Critère de validation du niveau intermédiaire :** vous devez être capable de développer seul un script d'administration qui possède une interface définie, valide ses entrées, traite correctement les noms de fichiers, distingue les erreurs, produit un résultat contrôlable et passe des tests normaux comme des tests d'échec.

Le niveau expert pourra alors approfondir la conception de bibliothèques Bash, les pièges avancés du shell, les traitements parallèles, la supervision de processus, la sécurité d'exécution, les stratégies de déploiement et l'intégration des scripts dans des chaînes d'automatisation Linux plus importantes.