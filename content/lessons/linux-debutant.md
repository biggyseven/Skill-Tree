# Introduction à Linux et au Shell
## Cours complet — Niveau débutant

> **Parcours :** Administration systèmes et réseaux  
> **Niveau :** Débutant  
> **Prérequis :** Savoir utiliser un ordinateur et manipuler des fichiers  
> **Environnement conseillé :** Ubuntu, Debian, Linux Mint ou une machine virtuelle Linux  
> **Objectif général :** Comprendre les bases de Linux, maîtriser les commandes fondamentales du Shell, gérer les fichiers et les permissions, observer les processus et créer un premier script d'automatisation.


# Sommaire

1. Présentation du cours et objectifs pédagogiques
2. Comprendre Linux
3. Architecture d'un système Linux
4. Préparer son environnement de travail
5. Découvrir le terminal et le Shell
6. Comprendre la syntaxe des commandes
7. Naviguer dans l'arborescence Linux
8. Comprendre les fichiers et les répertoires
9. Créer, copier, déplacer et supprimer des fichiers
10. Lire et rechercher des informations
11. Maîtriser les jokers et les caractères spéciaux
12. Comprendre les utilisateurs et les groupes
13. Maîtriser les permissions Linux
14. Comprendre les processus
15. Utiliser les redirections et les pipelines
16. Gérer les logiciels avec un gestionnaire de paquets
17. Découvrir les commandes réseau
18. Comprendre les variables d'environnement
19. Écrire un premier script Shell
20. Diagnostiquer les erreurs courantes
21. Travaux pratiques guidés
22. Exercices d'évaluation corrigés
23. Fiche de révision
24. Challenge final
25. Correction du challenge final
26. Checklist des compétences acquises


# 1. Présentation du cours et objectifs pédagogiques

Linux est utilisé dans de nombreux environnements informatiques : serveurs Web, infrastructures réseau, plateformes cloud, systèmes embarqués, équipements connectés, supercalculateurs et environnements de cybersécurité.

Pour administrer correctement un système Linux, il ne suffit pas de mémoriser quelques commandes. Il faut comprendre comment le système est organisé, comment les utilisateurs accèdent aux fichiers, comment les processus fonctionnent et comment le Shell permet d'automatiser des opérations.

Ce cours suit une progression allant des notions les plus simples vers les premières tâches d'administration. Chaque partie combine des explications, des schémas textuels, des commandes commentées et des exercices.

## 1.1 Compétences à acquérir

À la fin du cours, vous devrez être capable de :

- Expliquer la différence entre le noyau Linux, une distribution et le Shell.
- Reconnaître les principaux répertoires du système.
- Utiliser le terminal pour exécuter des commandes.
- Comprendre la différence entre un chemin absolu et un chemin relatif.
- Créer, copier, déplacer et supprimer des fichiers.
- Lire des fichiers et rechercher des informations.
- Comprendre les utilisateurs, les groupes et les permissions.
- Observer les processus en cours d'exécution.
- Utiliser des redirections et des pipelines.
- Installer un logiciel avec le gestionnaire de paquets approprié.
- Afficher les informations fondamentales d'une interface réseau.
- Écrire un script Bash simple.
- Diagnostiquer certaines erreurs sans recourir à des commandes dangereuses.

## 1.2 Méthode d'apprentissage

Une commande doit être comprise avant d'être utilisée dans une situation importante.

Suivez ce cycle :

```text
+--------------------------------------+
| 1. COMPRENDRE LA NOTION               |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 2. LIRE L'EXPLICATION                 |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 3. EXECUTER LA COMMANDE               |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 4. OBSERVER LE RESULTAT               |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 5. REFAIRE SANS CONSULTER LE COURS    |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 6. PASSER A LA NOTION SUIVANTE        |
+--------------------------------------+
```

Ne vous contentez pas de recopier les exemples. Essayez de prévoir leur résultat avant de les exécuter, puis vérifiez votre réponse.

## 1.3 Précautions avant de commencer

Pour apprendre, utilisez de préférence une machine virtuelle ou un environnement de test.

Pendant ce cours :

- Travaillez dans votre répertoire personnel.
- Évitez de modifier des fichiers système.
- N'utilisez pas `sudo` sans comprendre pourquoi il est nécessaire.
- Vérifiez les chemins avant les opérations de suppression.
- Ne copiez pas aveuglément des commandes trouvées sur Internet.
- N'exécutez pas un script inconnu avec des privilèges administrateur.

Les commandes de suppression et de modification des permissions seront étudiées dans un environnement contrôlé.


# 2. Comprendre Linux

## 2.1 Qu'est-ce que Linux ?

Linux désigne techniquement le noyau du système. Le noyau est le composant central qui coordonne l'utilisation du matériel et fournit des mécanismes permettant aux programmes de fonctionner.

Il intervient notamment dans :

- La gestion du processeur.
- La gestion de la mémoire vive.
- L'exécution des processus.
- L'accès aux systèmes de fichiers.
- Les communications réseau.
- La gestion des périphériques.
- L'application de certaines règles de sécurité.

Dans le langage courant, le terme « Linux » désigne souvent un système complet construit autour du noyau Linux.

Un système Linux complet comprend généralement le noyau, des bibliothèques, des utilitaires, des applications, des mécanismes de gestion des comptes et un environnement permettant d'utiliser la machine.

## 2.2 Le noyau et la distribution

Il faut distinguer plusieurs composants.

**Le noyau Linux :** il gère les ressources matérielles et fournit des mécanismes essentiels au système.

**Les utilitaires système :** ils permettent d'effectuer des opérations comme la consultation des fichiers, la création de répertoires ou l'inspection des processus.

**Le Shell :** il interprète les commandes saisies par l'utilisateur.

**La distribution Linux :** elle rassemble le noyau, des logiciels, des outils d'administration, une organisation des paquets et des configurations adaptées à un usage.

Exemples de distributions :

- Ubuntu
- Debian
- Fedora
- Linux Mint
- Rocky Linux
- Arch Linux

### Schéma : composition d'un système Linux

```text
+------------------------------------------------------+
|                  APPLICATIONS                        |
|                                                      |
|  Navigateur | Editeur | Serveur Web | Scripts        |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
|             ENVIRONNEMENT UTILISATEUR                |
|                                                      |
|  Shell | Commandes | Bibliotheques | Services       |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
|                    NOYAU LINUX                      |
|                                                      |
| Processus | Memoire | Fichiers | Pilotes | Reseau    |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
|                      MATERIEL                        |
|                                                      |
| CPU | RAM | Disques | Carte reseau | Peripheriques   |
+------------------------------------------------------+
```

Une application ne contrôle généralement pas directement le matériel. Elle utilise les interfaces du système et les mécanismes fournis par le noyau.

Par exemple, lorsqu'un programme demande l'ouverture d'un fichier, le système vérifie les accès autorisés puis réalise les opérations nécessaires.

## 2.3 Pourquoi Linux est-il utilisé dans les serveurs ?

Linux possède plusieurs caractéristiques utiles en administration informatique.

### Automatisation

Le Shell permet d'enchaîner des commandes et de créer des scripts réutilisables.

### Gestion des permissions

Les utilisateurs, les groupes et les permissions permettent de contrôler les accès aux fichiers et à certaines ressources.

### Outils réseau

Linux fournit de nombreux outils permettant d'afficher les interfaces, d'observer les routes et de diagnostiquer la connectivité.

### Écosystème logiciel

Les distributions proposent des gestionnaires de paquets et des dépôts facilitant l'installation et la mise à jour des logiciels.

### Adaptabilité

Linux fonctionne dans des environnements très divers, allant de petits systèmes embarqués à de grandes infrastructures serveur.

Ces caractéristiques ne garantissent pas automatiquement la sécurité ou la fiabilité d'une installation. La configuration, les mises à jour et les pratiques d'administration restent déterminantes.

## 2.4 Linux et Windows

Linux et Windows sont deux familles de systèmes d'exploitation. Leurs outils et pratiques d'administration peuvent être différents.

| Élément | Linux | Windows |
|---|---|---|
| Organisation des fichiers | Arborescence unique à partir de `/` | Lecteurs et arborescences, comme `C:` |
| Terminal courant | Bash, Zsh et autres Shells | PowerShell, Invite de commandes |
| Permissions | Modèle Unix, ACL selon la configuration | Modèle de sécurité Windows et ACL NTFS |
| Logiciels | Dépôts, gestionnaires de paquets et autres méthodes | Installateurs, magasins et gestionnaires de paquets |
| Automatisation | Shell, Python, Ansible et autres outils | PowerShell, Python et autres outils |

Les deux systèmes ont des domaines d'utilisation variés. Le choix dépend des besoins, des applications et de l'environnement.


# 3. Architecture d'un système Linux

## 3.1 Une arborescence unique

Sous Linux, les fichiers et les répertoires sont organisés dans une arborescence qui commence à la racine, représentée par `/`.

La racine `/` ne doit pas être confondue avec le compte administrateur `root` ou son répertoire personnel `/root`.

- `/` : racine de l'arborescence.
- `/root` : répertoire personnel habituel du superutilisateur `root`.
- `/home/alice` : exemple de répertoire personnel d'un utilisateur ordinaire.

### Schéma de l'arborescence

```text
/
|
+-- bin       Commandes essentielles, selon l'organisation du systeme
|
+-- boot      Fichiers necessaires au demarrage
|
+-- dev       Entrees representant des peripheriques
|
+-- etc       Fichiers de configuration
|
+-- home      Repertoires personnels des utilisateurs
|   |
|   +-- alice
|   |   +-- Documents
|   |   +-- Images
|   |   +-- Projets
|   |
|   +-- bob
|
+-- lib       Bibliotheques essentielles, selon l'organisation du systeme
|
+-- media     Points de montage de supports amovibles
|
+-- mnt       Points de montage temporaires ou administratifs
|
+-- opt       Logiciels complementaires, selon les installations
|
+-- proc      Informations exposees par le noyau
|
+-- root      Repertoire personnel habituel de root
|
+-- run       Donnees temporaires d'execution
|
+-- sbin      Outils systeme, selon la distribution
|
+-- srv       Donnees utilisees par certains services
|
+-- sys       Informations exposees sur les peripheriques et le noyau
|
+-- tmp       Fichiers temporaires
|
+-- usr       Applications, bibliotheques et ressources
|
+-- var       Donnees variables : journaux, caches et files d'attente
```

L'organisation exacte peut varier selon la distribution. Par exemple, certains systèmes utilisent des liens symboliques entre `/bin` et `/usr/bin`.

## 3.2 Les répertoires importants

### `/etc`

Ce répertoire contient de nombreux fichiers de configuration.

Exemples :

- `/etc/hostname` : nom de la machine.
- `/etc/hosts` : associations locales entre des noms et des adresses IP.
- `/etc/passwd` : informations de compte.
- `/etc/group` : informations sur les groupes.
- `/etc/ssh/` : configuration du service SSH lorsqu'il est installé.

Ne modifiez pas ces fichiers sans comprendre le paramètre concerné. Une mauvaise modification peut perturber un service ou empêcher son fonctionnement.

### `/home`

Ce répertoire contient généralement les répertoires personnels des utilisateurs ordinaires.

```text
/home/
|
+-- alice/
|   +-- Documents/
|   +-- Telechargements/
|   +-- Images/
|
+-- bob/
    +-- Documents/
    +-- Projets/
```

### `/var`

Ce répertoire contient des données qui évoluent durant le fonctionnement du système.

Exemples :

- `/var/log/` : journaux système et applicatifs.
- `/var/cache/` : données de cache.
- `/var/tmp/` : fichiers temporaires qui peuvent être conservés plus longtemps que ceux de `/tmp`, selon les règles du système.

### `/tmp`

Ce répertoire sert à stocker des fichiers temporaires. Sa politique de nettoyage dépend du système. Ne supposez pas que ses fichiers seront conservés après un redémarrage.

### `/usr`

Il contient une grande partie des programmes, bibliothèques et ressources installés.

Exemples :

- `/usr/bin/` : commandes et programmes.
- `/usr/sbin/` : outils système, selon la distribution.
- `/usr/share/` : données partagées par les programmes.

### `/dev`

Les entrées de `/dev` permettent d'accéder à des périphériques ou à des mécanismes particuliers.

Exemples :

- `/dev/null` : élimine les données qui y sont écrites.
- `/dev/zero` : fournit des octets nuls à la lecture.
- `/dev/sda` ou `/dev/nvme0n1` : exemples de noms de périphériques de stockage.

**Attention :** une commande qui écrit sur un périphérique de stockage peut détruire des données. N'effectuez pas d'opération sur un périphérique sans savoir précisément ce qu'elle fait.

## 3.3 Les chemins absolus

Un chemin absolu décrit l'emplacement d'un fichier depuis la racine `/`.

Exemple :

```text
/home/alice/Documents/rapport.txt
```

Ce chemin commence par `/`. Il ne dépend pas du répertoire courant.

Autres exemples :

```text
/etc/hostname
/var/log
/usr/bin/ls
```

## 3.4 Les chemins relatifs

Un chemin relatif est interprété à partir du répertoire courant.

Considérons :

```text
/home/alice/
|
+-- Documents/
|   +-- rapport.txt
|
+-- Projets/
    +-- application/
```

Si le répertoire courant est `/home/alice`, le chemin :

```text
Documents/rapport.txt
```

désigne le même fichier que :

```text
/home/alice/Documents/rapport.txt
```

Les chemins relatifs sont pratiques lorsqu'on travaille régulièrement dans un projet.

## 3.5 Les symboles `.` et `..`

Le symbole `.` représente le répertoire courant.

Le symbole `..` représente le répertoire parent.

Si le répertoire courant est :

```text
/home/alice/Documents
```

alors :

```text
.       = /home/alice/Documents
..      = /home/alice
../..   = /home
```

## 3.6 Le symbole `~`

Dans les Shells courants, `~` représente le répertoire personnel de l'utilisateur.

```bash
cd ~
```

Cette commande revient normalement dans le répertoire personnel.

Pour un utilisateur nommé `alice`, le répertoire personnel peut être `/home/alice`.


# 4. Préparer son environnement de travail

## 4.1 Les différentes possibilités

### Option A : machine virtuelle

Une machine virtuelle permet d'exécuter Linux dans un environnement isolé du système principal.

Elle est utile pour apprendre, tester des configurations et recommencer des exercices. Lorsque l'outil de virtualisation le permet, des instantanés peuvent servir à revenir à un état précédent.

### Option B : ordinateur Linux

Un ordinateur déjà équipé de Linux convient. Utilisez un compte ordinaire pendant l'apprentissage et réservez les privilèges administrateur aux opérations qui en ont réellement besoin.

### Option C : environnement Linux sous Windows

Windows Subsystem for Linux (WSL) permet d'exécuter une distribution Linux dans Windows.

Il convient à de nombreux exercices de Shell, même si certains aspects de l'administration, du matériel, du démarrage ou du réseau peuvent différer d'une installation Linux classique.

### Option D : serveur distant

Un serveur distant peut être accessible avec SSH. Cette possibilité sera particulièrement utile pour apprendre l'administration de serveurs.

Pour commencer, un environnement de test dont vous maîtrisez la configuration est préférable.

## 4.2 Vérifier l'environnement

Ouvrez un terminal puis exécutez :

```bash
whoami
```

Affiche le nom de l'utilisateur effectif.

```bash
pwd
```

Affiche le répertoire courant.

```bash
uname -s
```

Affiche le nom du noyau.

```bash
uname -r
```

Affiche la version du noyau.

```bash
cat /etc/os-release
```

Affiche des informations sur la distribution, si ce fichier est disponible.

```bash
date
```

Affiche la date et l'heure du système.

### Exemple de résultat

```text
$ whoami
alice

$ pwd
/home/alice

$ uname -s
Linux
```

Le signe `$` représente ici l'invite de commande. Il ne faut généralement pas le saisir lorsque vous copiez une commande.

## 4.3 Comprendre l'invite de commande

Dans de nombreux environnements Bash, une invite ressemble à ceci :

```text
alice@ordinateur:~/Documents$
```

Elle peut fournir les informations suivantes :

```text
alice         -> utilisateur
ordinateur   -> nom de la machine
~/Documents  -> repertoire courant
$             -> invite habituelle d'un utilisateur ordinaire
```

Une session administrateur peut afficher `#`, mais l'invite est personnalisable. Il ne faut donc pas utiliser son apparence comme unique moyen de vérifier les privilèges.

Utilisez `whoami` et `id` lorsque vous devez connaître l'identité de la session.


# 5. Découvrir le terminal et le Shell

## 5.1 Qu'est-ce qu'un terminal ?

Le terminal est l'interface dans laquelle l'utilisateur saisit des commandes et consulte leurs résultats.

Il peut s'agir :

- D'une application graphique.
- D'une console virtuelle.
- D'une session distante SSH.
- D'un terminal intégré à un environnement de développement.

Le terminal fournit un moyen d'interagir avec les programmes par l'intermédiaire de texte.

## 5.2 Qu'est-ce qu'un Shell ?

Le Shell est le programme qui interprète les commandes saisies.

Il peut notamment :

- Interpréter les commandes et leurs arguments.
- Gérer les variables.
- Développer certains motifs de fichiers.
- Exécuter des programmes.
- Mettre en place des redirections.
- Relier plusieurs commandes avec des pipelines.
- Exécuter des scripts.

Bash est un Shell très courant. Zsh, Dash et Fish sont d'autres exemples.

### Schéma : parcours d'une commande

```text
+----------------------------+
| Utilisateur                |
| saisit : ls -l             |
+----------------------------+
              |
              v
+----------------------------+
| Terminal                   |
| gere l'affichage           |
+----------------------------+
              |
              v
+----------------------------+
| Shell                      |
| interprete la commande     |
+----------------------------+
              |
              v
+----------------------------+
| Programme ls               |
| examine les entrees        |
+----------------------------+
              |
              v
+----------------------------+
| Resultat affiche           |
| dans le terminal           |
+----------------------------+
```

Le Shell ne réalise pas nécessairement lui-même l'opération. `ls` est généralement un programme externe. En revanche, `cd` est souvent une commande intégrée au Shell.

## 5.3 Pourquoi `cd` est-il une commande interne ?

La commande :

```bash
cd /tmp
```

modifie le répertoire courant du Shell.

Si elle était exécutée dans un processus enfant indépendant, ce processus pourrait changer de répertoire sans modifier celui du Shell parent. L'invite de commande resterait alors dans le répertoire initial.

C'est pourquoi `cd` est habituellement implémentée comme commande interne.

## 5.4 Obtenir de l'aide avec `man`

La commande `man` affiche une page de manuel lorsqu'elle est disponible.

```bash
man ls
```

Touches utiles :

- `Space` : avancer d'une page.
- `b` : reculer d'une page.
- `/mot` : rechercher un terme.
- `n` : occurrence suivante.
- `q` : quitter.

Les pages de manuel sont organisées en sections. La section 1 contient notamment des commandes utilisateur ; la section 5 décrit de nombreux formats de fichiers.

Exemple :

```bash
man 5 passwd
```

Cette commande demande la page consacrée au format du fichier `passwd`, si elle est installée.

## 5.5 L'option `--help`

De nombreux programmes proposent une aide intégrée.

```bash
ls --help
```

Elle présente souvent les options disponibles. Toutes les commandes ne prennent pas en charge `--help` de la même façon ; la page de manuel ou la documentation officielle peut être nécessaire.

## 5.6 L'auto-complétion

Dans les Shells courants, la touche `Tab` permet de compléter les commandes et les chemins.

Elle réduit les erreurs de frappe et aide à retrouver rapidement un nom de fichier.

## 5.7 L'historique

La commande suivante affiche l'historique de commandes conservé par le Shell :

```bash
history
```

Les flèches vers le haut et vers le bas permettent généralement de parcourir les commandes précédentes.

**Attention :** évitez de saisir des mots de passe ou des secrets directement dans les commandes. L'historique peut conserver des informations sensibles.


# 6. Comprendre la syntaxe des commandes

## 6.1 Structure générale

Une commande suit souvent cette structure :

```text
commande [options] [arguments]
```

- **Commande :** programme ou instruction à exécuter.
- **Options :** modifient le comportement de la commande.
- **Arguments :** indiquent les objets à traiter.

Exemple :

```bash
ls -l /etc
```

Interprétation :

```text
ls      -> commande qui liste des entrees
-l      -> option d'affichage detaille
/etc    -> repertoire a examiner
```

Les options ne sont pas universelles. Il faut se référer à la documentation de la commande.

## 6.2 Options courtes et longues

Une option peut posséder une forme courte et une forme longue.

```bash
ls -a
```

Affiche également les entrées cachées.

```bash
ls --all
```

Sur GNU `ls`, cette forme produit le même type de résultat.

## 6.3 Combiner des options

```bash
ls -lah
```

Sur les versions courantes de `ls` compatibles avec ces options :

- `-l` : affichage détaillé.
- `-a` : inclut les entrées cachées.
- `-h` : affiche les tailles dans un format lisible dans l'affichage détaillé.

## 6.4 Majuscules et minuscules

Linux distingue généralement les majuscules et les minuscules dans les noms de fichiers.

Les noms suivants peuvent désigner des fichiers différents :

```text
rapport.txt
Rapport.txt
RAPPORT.txt
```

Par conséquent :

```bash
cat rapport.txt
```

n'est pas nécessairement équivalent à :

```bash
cat Rapport.txt
```

## 6.5 Comprendre les erreurs

Essayez :

```bash
cat fichier-inexistant.txt
```

Le système peut afficher un message similaire à :

```text
cat: fichier-inexistant.txt: No such file or directory
```

Cela signifie que le chemin demandé n'a pas été trouvé dans le contexte de la commande.

Vérifiez :

1. L'orthographe du nom.
2. Le répertoire courant.
3. L'existence du fichier.
4. Les permissions nécessaires.
5. La syntaxe de la commande.

Un message d'erreur est une information utile pour comprendre le problème.


# 7. Naviguer dans l'arborescence Linux

## 7.1 Afficher le répertoire courant

```bash
pwd
```

`pwd` signifie *print working directory*.

Exemple :

```text
/home/alice/Documents
```

Cette information est essentielle, car les chemins relatifs sont interprétés à partir de ce répertoire.

## 7.2 Afficher le contenu avec `ls`

```bash
ls
```

Affiche les entrées du répertoire courant.

Pour examiner un autre répertoire :

```bash
ls /etc
```

Pour afficher davantage de détails :

```bash
ls -l
```

Pour inclure les entrées cachées :

```bash
ls -a
```

Pour combiner les options :

```bash
ls -lah
```

## 7.3 Comprendre `ls -l`

Exemple illustratif :

```text
-rw-r--r-- 1 alice alice 250 Oct 24 08:30 notes.txt
drwxr-xr-x 2 alice alice 4096 Oct 24 08:35 Documents
```

Une ligne contient plusieurs champs :

```text
-rw-r--r--  1  alice  alice  250  Oct 24 08:30  notes.txt
|           |  |      |      |    |               |
|           |  |      |      |    |               +-- Nom
|           |  |      |      |    +------------------ Date
|           |  |      |      +----------------------- Taille
|           |  |      +------------------------------ Groupe
|           |  +------------------------------------- Proprietaire
|           +---------------------------------------- Liens physiques
+---------------------------------------------------- Type et permissions
```

Le premier caractère indique habituellement le type d'entrée, puis viennent les permissions classiques.

## 7.4 Changer de répertoire

Pour entrer dans un répertoire :

```bash
cd Documents
```

Pour utiliser un chemin absolu :

```bash
cd /etc
```

Pour revenir dans le répertoire personnel :

```bash
cd ~
```

ou simplement :

```bash
cd
```

Pour remonter d'un niveau :

```bash
cd ..
```

Pour revenir au répertoire précédent :

```bash
cd -
```

## 7.5 Exemple guidé

Exécutez :

```bash
pwd
```

Puis :

```bash
cd Documents
pwd
```

Le résultat de `pwd` dépend de l'emplacement initial et de l'existence de `Documents`.

Revenez ensuite au répertoire parent :

```bash
cd ..
pwd
```

Enfin, revenez à votre répertoire personnel :

```bash
cd ~
pwd
```

Cette séquence permet de constater comment les chemins changent.

## 7.6 Exercices de navigation

**Question 1 :** que fait `cd /` ?

**Réponse :** place le répertoire courant à la racine `/`.

**Question 2 :** que fait `cd /tmp` ?

**Réponse :** place le répertoire courant dans `/tmp`, si le répertoire est présent et accessible.

**Question 3 :** que représente `..` depuis `/home/alice/Documents` ?

**Réponse :** `/home/alice`.

**Question 4 :** que fait `cd ~` ?

**Réponse :** revient au répertoire personnel de l'utilisateur.

**Question 5 :** que fait `pwd` ?

**Réponse :** affiche le répertoire courant.


# 8. Comprendre les fichiers et les répertoires

## 8.1 Les fichiers ordinaires

Un fichier ordinaire peut contenir du texte, un programme, une image ou des données binaires.

Exemples :

```text
notes.txt
photo.jpg
configuration.conf
programme.py
archive.tar.gz
```

L'extension fournit souvent un indice sur le format, mais ne garantit pas le contenu réel.

## 8.2 Les répertoires

Les répertoires permettent d'organiser les fichiers et d'autres répertoires.

Exemple :

```text
projet/
|
+-- README.md
|
+-- documents/
|   +-- specification.txt
|
+-- scripts/
|   +-- sauvegarde.sh
|
+-- resultats/
```

Une arborescence cohérente rend les fichiers plus faciles à retrouver et à maintenir.

## 8.3 Les fichiers cachés

Sous Linux, un nom commençant par un point est généralement masqué dans l'affichage normal de `ls`.

Exemples :

```text
.bashrc
.profile
.gitconfig
```

Pour les afficher :

```bash
ls -a
```

Les fichiers cachés peuvent contenir des paramètres personnels. Ne les supprimez pas simplement parce qu'ils commencent par un point.

## 8.4 Les fichiers de configuration

Les applications utilisent souvent des fichiers pour enregistrer leurs paramètres.

Avant de modifier une configuration importante :

1. Lisez le fichier.
2. Identifiez le paramètre concerné.
3. Sauvegardez le fichier si nécessaire.
4. Effectuez une modification minimale.
5. Vérifiez le résultat.
6. Consultez les journaux en cas d'échec.

Cette méthode réduit les erreurs difficiles à diagnostiquer.


# 9. Créer, copier, déplacer et supprimer des fichiers

Cette section est fondamentale. Les commandes sont simples, mais certaines opérations peuvent entraîner une perte de données.

Travaillez d'abord dans un répertoire de test.

## 9.1 Créer un répertoire avec `mkdir`

```bash
mkdir laboratoire
```

Crée un répertoire nommé `laboratoire` dans le répertoire courant.

Pour créer plusieurs répertoires :

```bash
mkdir documents images sauvegardes
```

Pour créer toute une arborescence :

```bash
mkdir -p laboratoire/cours/linux
```

L'option `-p` crée les répertoires parents manquants.

## 9.2 Créer un fichier avec `touch`

```bash
touch notes.txt
```

Si le fichier n'existe pas, `touch` le crée généralement vide.

S'il existe déjà, la commande met à jour certains horodatages. Elle ne vide pas son contenu.

## 9.3 Copier un fichier avec `cp`

```bash
cp notes.txt notes-copie.txt
```

Copie `notes.txt` dans `notes-copie.txt`.

Pour copier vers un répertoire :

```bash
cp notes.txt laboratoire/
```

Si une destination portant le même nom existe déjà, la commande peut remplacer son contenu. Vérifiez la destination avant d'exécuter la commande.

## 9.4 Copier un répertoire

```bash
cp -r laboratoire laboratoire-copie
```

L'option `-r` indique une copie récursive du répertoire et de son contenu.

Pour des sauvegardes complexes nécessitant de préserver davantage de métadonnées, de liens ou d'attributs, d'autres options ou outils peuvent être préférables.

## 9.5 Déplacer ou renommer avec `mv`

Renommer un fichier :

```bash
mv notes.txt notes-finales.txt
```

Déplacer un fichier vers un répertoire :

```bash
mv notes-finales.txt laboratoire/
```

Déplacer et renommer :

```bash
mv laboratoire/notes-finales.txt laboratoire/rapport.txt
```

Une destination existante peut être remplacée selon les circonstances. Vérifiez toujours les chemins.

## 9.6 Supprimer un fichier avec `rm`

```bash
rm fichier-inutile.txt
```

Supprime le fichier indiqué si les permissions nécessaires sont disponibles.

La suppression avec `rm` ne correspond pas automatiquement à un déplacement dans une corbeille.

Pour demander une confirmation :

```bash
rm -i fichier-inutile.txt
```

Ne supprimez pas des données importantes sans vérifier le chemin.

## 9.7 Supprimer un répertoire vide

```bash
rmdir ancien-repertoire
```

Cette commande supprime un répertoire vide. Elle échoue généralement si le répertoire contient encore des éléments.

## 9.8 Suppression récursive

```bash
rm -r ancien-projet
```

Cette commande supprime récursivement le répertoire et son contenu.

**Précaution importante :** avant une suppression, examinez l'emplacement et le contenu :

```bash
pwd
ls -la ancien-projet
```

Ne copiez jamais aveuglément une commande comme `rm -rf`. Une erreur de chemin peut entraîner une perte de données difficile à réparer.

## 9.9 Écrire dans un fichier avec `echo`

```bash
echo "Bonjour Linux" > message.txt
```

Cette commande écrit le texte dans le fichier. Si celui-ci existe déjà, son contenu est remplacé.

Pour ajouter une ligne :

```bash
echo "Deuxieme ligne" >> message.txt
```

La différence entre `>` et `>>` sera expliquée dans le chapitre consacré aux redirections.

## 9.10 Atelier : créer une arborescence

Exécutez dans votre répertoire personnel :

```bash
mkdir -p atelier-linux/documents
mkdir -p atelier-linux/scripts
mkdir -p atelier-linux/archives

touch atelier-linux/documents/notes.txt
touch atelier-linux/documents/commandes.txt
```

Affichez l'arborescence :

```bash
find atelier-linux -print
```

Copiez ensuite un fichier :

```bash
cp atelier-linux/documents/notes.txt atelier-linux/documents/notes-copie.txt
```

Renommez la copie :

```bash
mv atelier-linux/documents/notes-copie.txt atelier-linux/documents/notes-finales.txt
```

Vérifiez :

```bash
ls -l atelier-linux/documents
```

L'objectif est de comprendre chaque opération et de contrôler son résultat.


# 10. Lire et rechercher des informations

## 10.1 Afficher le contenu avec `cat`

```bash
cat notes.txt
```

Affiche le contenu du fichier.

Cette commande convient bien aux fichiers courts. Pour de très longs fichiers, utilisez plutôt `less`, `head` ou `tail`.

## 10.2 Lire progressivement avec `less`

```bash
less notes.txt
```

`less` permet de parcourir un fichier sans afficher nécessairement tout son contenu d'un seul coup.

Touches utiles :

- `Space` : avancer d'une page.
- `b` : reculer d'une page.
- `/mot` : rechercher un terme.
- `n` : occurrence suivante.
- `q` : quitter.

## 10.3 Afficher les premières lignes avec `head`

```bash
head notes.txt
```

Affiche généralement les dix premières lignes.

Pour en afficher cinq :

```bash
head -n 5 notes.txt
```

## 10.4 Afficher les dernières lignes avec `tail`

```bash
tail notes.txt
```

Affiche généralement les dix dernières lignes.

Pour afficher les vingt dernières lignes :

```bash
tail -n 20 notes.txt
```

Pour suivre les nouvelles lignes d'un journal :

```bash
tail -f application.log
```

Quittez généralement avec `Ctrl+C`.

## 10.5 Compter avec `wc`

```bash
wc notes.txt
```

La commande affiche généralement le nombre de lignes, de mots et d'octets.

Compter les lignes :

```bash
wc -l notes.txt
```

Compter les mots :

```bash
wc -w notes.txt
```

Compter les octets :

```bash
wc -c notes.txt
```

Le nombre d'octets n'est pas nécessairement égal au nombre de caractères, en particulier avec du texte UTF-8.

## 10.6 Rechercher du texte avec `grep`

```bash
grep "erreur" application.log
```

Affiche les lignes correspondant au motif `erreur`.

Pour rendre la recherche insensible à la casse :

```bash
grep -i "erreur" application.log
```

Pour afficher les numéros des lignes :

```bash
grep -n "erreur" application.log
```

Pour rechercher récursivement dans les fichiers d'un répertoire :

```bash
grep -R "configuration" documents/
```

Une recherche récursive peut produire beaucoup de résultats. Choisissez un chemin pertinent et un motif suffisamment précis.

## 10.7 Rechercher des fichiers avec `find`

Pour afficher les entrées d'un répertoire :

```bash
find atelier-linux -print
```

Pour rechercher les fichiers ordinaires dont le nom se termine par `.txt` :

```bash
find atelier-linux -type f -name "*.txt"
```

Interprétation :

```text
find atelier-linux -> point de depart de la recherche
-type f            -> fichiers ordinaires uniquement
-name "*.txt"      -> noms termines par .txt
```

Les guillemets empêchent le Shell de développer le motif avant de le transmettre à `find`.

Pour rechercher les répertoires :

```bash
find atelier-linux -type d
```

Pour trouver les fichiers dont le nom contient `notes` :

```bash
find atelier-linux -type f -name "*notes*"
```

## 10.8 Différence entre `find` et `grep`

```text
find
 |
 +-- Recherche des fichiers et repertoires
     selon leur nom, type ou autres criteres.

grep
 |
 +-- Recherche du contenu textuel
     correspondant a un motif.
```

Exemples :

- Trouver tous les fichiers `.txt` : `find`.
- Trouver les lignes contenant `ERROR` : `grep`.
- Trouver des fichiers puis examiner leur contenu : combiner les outils de manière adaptée.


# 11. Maîtriser les jokers et les caractères spéciaux

Les jokers sont des motifs interprétés par le Shell pour sélectionner des noms de fichiers.

## 11.1 Le joker `*`

Le caractère `*` correspond généralement à zéro ou plusieurs caractères dans un motif de nom de fichier.

```bash
ls *.txt
```

Le Shell développe le motif en une liste de noms correspondant au modèle `*.txt`, lorsque des correspondances existent.

Exemples :

```text
notes.txt
rapport.txt
cours-linux.txt
```

## 11.2 Le joker `?`

Le caractère `?` correspond à un caractère.

```bash
ls fichier?.txt
```

Cela peut correspondre à :

```text
fichier1.txt
fichierA.txt
```

mais pas nécessairement à `fichier12.txt`, car celui-ci contient deux caractères à cet emplacement.

## 11.3 Les classes de caractères

Les crochets permettent de sélectionner un ensemble de caractères.

```bash
ls fichier[123].txt
```

Cela peut correspondre à :

```text
fichier1.txt
fichier2.txt
fichier3.txt
```

## 11.4 Pourquoi utiliser les guillemets ?

Sans guillemets :

```bash
ls *.txt
```

Le Shell peut développer le motif en noms de fichiers avant l'exécution de `ls`.

Avec des guillemets :

```bash
ls "*.txt"
```

le motif est transmis littéralement dans cet argument. Cette commande peut échouer si aucun fichier ne porte exactement le nom `*.txt`.

### Schéma : développement d'un joker

```text
Commande saisie :
    ls *.txt
         |
         v
Le Shell examine le repertoire courant
         |
         v
Il recherche les noms correspondants
         |
         v
Le motif est remplace par les noms trouves
         |
         v
ls affiche les entrees correspondantes
```

## 11.5 Les espaces dans les noms de fichiers

Pour un fichier nommé `rapport final.txt`, utilisez :

```bash
cat "rapport final.txt"
```

Les guillemets permettent de transmettre le nom comme un seul argument.

Une autre méthode consiste à échapper l'espace :

```bash
cat rapport\ final.txt
```

Dans les scripts, les guillemets sont souvent plus faciles à lire et à maintenir.

## 11.6 Exercice pratique

Dans un répertoire de test, créez plusieurs fichiers :

```bash
touch jour1.txt jour2.txt jour3.txt rapport.pdf
```

Puis exécutez :

```bash
ls *.txt
```

Essayez aussi :

```bash
ls jour?.txt
```

Comparez avec :

```bash
ls "jour?.txt"
```

Expliquez pourquoi les résultats peuvent être différents.


# 12. Comprendre les utilisateurs et les groupes

## 12.1 Pourquoi plusieurs utilisateurs ?

Un système Linux peut héberger plusieurs comptes.

Les comptes servent à attribuer une identité aux actions, à organiser les permissions et à séparer les environnements.

Exemples :

```text
alice      -> utilisateur ordinaire
bob        -> autre utilisateur ordinaire
www-data   -> compte utilise par certains services Web
root       -> superutilisateur traditionnel
```

Ces noms sont des exemples. Les comptes présents dépendent de la distribution et des logiciels installés.

## 12.2 Le compte `root`

`root` est le compte superutilisateur traditionnel de Linux. Il possède des privilèges très étendus.

Une commande exécutée avec ces privilèges peut modifier des fichiers système, gérer des comptes ou interrompre des services.

Évitez de travailler en permanence avec ces privilèges. Utilisez un compte ordinaire et élevez les privilèges uniquement quand c'est nécessaire.

## 12.3 Identifier l'utilisateur courant

```bash
whoami
```

Affiche le nom de l'utilisateur effectif.

## 12.4 Examiner les identifiants et les groupes

```bash
id
```

Exemple illustratif :

```text
uid=1000(alice) gid=1000(alice) groups=1000(alice),27(sudo)
```

Les valeurs dépendent du système.

- `uid` : identifiant de l'utilisateur.
- `gid` : identifiant du groupe principal.
- `groups` : groupes supplémentaires.

## 12.5 Examiner les sessions

```bash
who
```

Affiche des informations sur les utilisateurs connectés, selon les informations disponibles.

```bash
w
```

Affiche un aperçu des sessions et de leur activité.

Le résultat dépend de l'environnement.

## 12.6 Comprendre `sudo`

`sudo` permet à un utilisateur autorisé d'exécuter une commande avec des privilèges différents, souvent ceux de `root`.

Exemple sur un système utilisant APT :

```bash
sudo apt update
```

Cette commande actualise les informations locales relatives aux paquets disponibles.

Avant d'utiliser `sudo`, posez-vous les questions suivantes :

- Pourquoi les privilèges élevés sont-ils nécessaires ?
- Quel fichier ou service sera modifié ?
- Est-ce que je comprends la commande ?
- Peut-elle supprimer des données ou interrompre un service ?

`sudo` ne rend pas une commande automatiquement correcte ou sûre.

## 12.7 Les informations sur les comptes

Le fichier `/etc/passwd` contient des informations sur les comptes locaux.

Pour consulter quelques lignes :

```bash
head /etc/passwd
```

Il ne s'agit pas d'une liste de mots de passe en clair. Les mécanismes d'authentification dépendent également d'autres fichiers ou services.

Ne modifiez pas directement les fichiers des comptes dans ce cours.


# 13. Maîtriser les permissions Linux

Les permissions définissent les opérations autorisées pour les utilisateurs sur des fichiers et des répertoires.

Elles sont fondamentales pour la confidentialité, l'intégrité des données et la sécurité du système.

## 13.1 Les trois catégories classiques

Le modèle classique distingue :

- `u` : propriétaire (*user*).
- `g` : groupe associé (*group*).
- `o` : autres utilisateurs (*others*).

L'option symbolique `a` peut désigner toutes les catégories.

## 13.2 Les trois permissions fondamentales

| Symbole | Nom | Signification habituelle pour un fichier |
|---|---|---|
| `r` | Read | Lire le contenu |
| `w` | Write | Modifier le contenu |
| `x` | Execute | Exécuter le fichier si son type et le contexte le permettent |

Pour un répertoire, la signification diffère :

- `r` permet généralement de lire la liste des entrées.
- `w` permet de modifier les entrées, habituellement en combinaison avec `x`.
- `x` permet de traverser le répertoire et d'accéder aux objets par leur chemin, sous réserve des autres contrôles.

Les permissions d'un répertoire ne doivent donc pas être interprétées exactement comme celles d'un fichier ordinaire.

## 13.3 Lire les permissions

Exemple :

```text
-rwxr-xr-- 1 alice developpeurs 1800 Oct 24 09:00 script.sh
```

Découpage :

```text
-rwxr-xr--
|
+-- -         -> fichier ordinaire
    rwx       -> proprietaire
       r-x    -> groupe
          r-- -> autres utilisateurs
```

Le premier caractère indique généralement le type d'entrée. `d` indique habituellement un répertoire et `l` un lien symbolique.

## 13.4 Modifier les permissions avec `chmod`

Ajouter l'exécution au propriétaire :

```bash
chmod u+x script.sh
```

Retirer cette permission :

```bash
chmod u-x script.sh
```

Ajouter la lecture et l'écriture au propriétaire :

```bash
chmod u+rw fichier.txt
```

Retirer l'écriture aux autres :

```bash
chmod o-w fichier.txt
```

Définir explicitement les permissions classiques :

```bash
chmod u=rw,g=r,o= fichier.txt
```

Dans cet exemple, le propriétaire peut lire et écrire, le groupe peut lire et les autres n'ont aucune permission classique.

## 13.5 La notation numérique

Les valeurs de base sont :

```text
r = 4
w = 2
x = 1
```

Les valeurs s'additionnent pour chaque catégorie.

| Permission | Calcul | Valeur |
|---|---:|---:|
| `---` | 0 | 0 |
| `--x` | 1 | 1 |
| `-w-` | 2 | 2 |
| `-wx` | 2 + 1 | 3 |
| `r--` | 4 | 4 |
| `r-x` | 4 + 1 | 5 |
| `rw-` | 4 + 2 | 6 |
| `rwx` | 4 + 2 + 1 | 7 |

### Exemple : mode `755`

```bash
chmod 755 script.sh
```

Les permissions classiques deviennent :

```text
rwxr-xr-x
```

Interprétation :

```text
7 -> proprietaire : rwx
5 -> groupe       : r-x
5 -> autres       : r-x
```

Le propriétaire peut lire, modifier et exécuter. Le groupe et les autres peuvent lire et exécuter.

### Exemple : mode `644`

```bash
chmod 644 notes.txt
```

Les permissions deviennent :

```text
rw-r--r--
```

Le propriétaire peut lire et écrire. Le groupe et les autres peuvent lire.

### Exemple : mode `600`

```bash
chmod 600 secret.txt
```

Les permissions deviennent :

```text
rw-------
```

Le propriétaire peut lire et écrire. Le groupe et les autres n'ont aucune permission classique.

Ces valeurs sont des exemples courants. Le choix réel doit dépendre des besoins et des règles de sécurité.

## 13.6 Changer le propriétaire avec `chown`

La commande `chown` permet de modifier le propriétaire ou le groupe associé à un fichier, lorsque les privilèges nécessaires sont disponibles.

Exemple :

```bash
sudo chown alice fichier.txt
```

Définir un propriétaire et un groupe :

```bash
sudo chown alice:developpeurs fichier.txt
```

Les comptes et groupes doivent exister. Ne changez pas au hasard le propriétaire des fichiers système.

## 13.7 Vérifier les permissions

```bash
ls -l fichier.txt
```

Pour examiner davantage de métadonnées :

```bash
stat fichier.txt
```

## 13.8 Les permissions des répertoires parents

Pour accéder à :

```text
/home/alice/Documents/rapport.txt
```

les permissions du fichier ne sont pas les seuls éléments importants.

Il faut généralement disposer de la permission de traversée `x` sur chaque répertoire du chemin nécessaire à l'accès.

```text
/home
  |
  v
alice/
  |
  v
Documents/
  |
  v
rapport.txt
```

Un fichier lisible peut rester inaccessible si un répertoire parent bloque la traversée.

## 13.9 Pourquoi éviter `chmod 777` ?

La commande :

```bash
chmod 777 fichier.txt
```

attribue les permissions classiques de lecture, d'écriture et d'exécution au propriétaire, au groupe et aux autres.

Ce n'est pas une solution universelle aux problèmes d'accès. Elle peut autoriser des utilisateurs non souhaités à modifier le contenu.

Il vaut mieux identifier la véritable cause du problème, puis accorder uniquement les permissions nécessaires.

## 13.10 Exercices sur les permissions

**Exercice A :** que signifie `-rw-r--r--` ?

**Correction :**

- Propriétaire : lecture et écriture.
- Groupe : lecture.
- Autres : lecture.

**Exercice B :** que signifie `chmod 700 dossier` ?

**Correction :**

Le propriétaire reçoit `rwx`. Le groupe et les autres n'obtiennent aucune permission classique. Pour un répertoire, le propriétaire peut le parcourir et y accéder sous réserve des autres contrôles.

**Exercice C :** que signifie `chmod 600 secret.txt` ?

**Correction :**

Le propriétaire reçoit la lecture et l'écriture ; le groupe et les autres n'obtiennent aucune permission classique.

D'autres mécanismes, comme les ACL ou les politiques de sécurité, peuvent également influencer les accès.


# 14. Comprendre les processus

## 14.1 Qu'est-ce qu'un processus ?

Un processus est une instance d'un programme en cours d'exécution.

Exemples :

- Un navigateur.
- Un serveur Web.
- Un Shell.
- Un script.
- Une commande de diagnostic.

Chaque processus possède un identifiant appelé PID (*Process ID*).

Un processus peut lancer d'autres processus. Ces relations parent-enfant forment une structure utile pour l'observation et le dépannage.

### Schéma des processus

```text
+----------------------------+
| Systeme Linux              |
+----------------------------+
               |
               v
+----------------------------+
| Processus parent           |
| Shell Bash                 |
+----------------------------+
          |             |
          v             v
+----------------+  +----------------+
| Processus ls   |  | Processus grep |
+----------------+  +----------------+
```

Ce schéma est conceptuel. Le détail dépend des commandes et du Shell.

## 14.2 Afficher les processus avec `ps`

```bash
ps
```

Affiche les processus associés au contexte courant selon le comportement de la commande.

Pour obtenir une vue plus large sur de nombreux systèmes Linux :

```bash
ps -ef
```

Une autre forme courante est :

```bash
ps aux
```

Les options de ces deux styles suivent des conventions différentes.

La sortie peut comprendre :

- Le PID.
- L'utilisateur.
- Le temps CPU.
- La commande.
- Le processus parent dans les formats qui l'affichent.

## 14.3 Surveiller les processus avec `top`

```bash
top
```

`top` affiche une vue régulièrement actualisée des processus et de certaines ressources système.

Les informations peuvent inclure :

- L'utilisation du CPU.
- L'utilisation de la mémoire.
- La charge système.
- Le nombre de processus.
- Les identifiants des processus.

Quittez généralement avec `q`.

## 14.4 Rechercher des processus avec `pgrep`

```bash
pgrep -a bash
```

Cette commande recherche les processus correspondant à `bash` et affiche leur ligne de commande lorsque l'option est disponible.

Elle peut être plus pratique qu'une recherche manuelle dans une longue sortie de `ps`.

## 14.5 Arrêter un processus avec `kill`

La syntaxe générale est :

```bash
kill PID
```

Remplacez `PID` par l'identifiant numérique du processus visé.

Par exemple, si le PID réel est `12345` :

```bash
kill 12345
```

La commande envoie normalement le signal `TERM`, qui demande au processus de se terminer.

Le processus peut réagir à ce signal, différer sa terminaison ou ne pas être en mesure de le traiter.

## 14.6 Comprendre les signaux

Parmi les signaux connus :

- `SIGTERM` : demande de terminaison.
- `SIGINT` : interruption, souvent envoyée avec `Ctrl+C` dans le terminal.
- `SIGKILL` : terminaison forcée, non interceptable par le processus.

Exemple explicite :

```bash
kill -TERM 12345
```

L'arrêt forcé utilise :

```bash
kill -KILL 12345
```

ou :

```bash
kill -9 12345
```

`SIGKILL` doit rester un dernier recours. Le processus ne peut pas intercepter ce signal pour effectuer un nettoyage habituel avant de terminer.

**Règle de sécurité :** identifiez le processus avant d'envoyer un signal. Un mauvais PID peut désigner une application importante.


# 15. Utiliser les redirections et les pipelines

Les redirections et les pipelines permettent de combiner des programmes simples pour réaliser des opérations plus élaborées.

## 15.1 Les flux standards

De nombreux programmes utilisent trois flux standards :

- Entrée standard : `stdin`, numéro 0.
- Sortie standard : `stdout`, numéro 1.
- Sortie d'erreur : `stderr`, numéro 2.

### Schéma

```text
+-----------------------------+
| Entree standard : stdin     |
| Numero 0                    |
+-----------------------------+
                |
                v
+-----------------------------+
| Programme                   |
+-----------------------------+
          |             |
          v             v
+----------------+ +----------------+
| Sortie standard| | Sortie erreur  |
| stdout : 1     | | stderr : 2     |
+----------------+ +----------------+
```

La sortie standard contient généralement le résultat normal. La sortie d'erreur permet de transmettre des messages d'erreur ou de diagnostic.

## 15.2 Rediriger avec `>`

```bash
echo "Formation Linux" > formation.txt
```

La sortie standard est écrite dans `formation.txt`.

Si le fichier existe, son contenu est généralement remplacé.

```text
echo "Formation Linux"
            |
            v
      Sortie standard
            |
            v
            >
            |
            v
+---------------------------+
| formation.txt             |
| Formation Linux           |
+---------------------------+
```

## 15.3 Ajouter avec `>>`

```bash
echo "Premiere ligne" > journal.txt
echo "Deuxieme ligne" >> journal.txt
```

La première commande crée ou remplace le contenu du fichier.

La deuxième ajoute une nouvelle ligne à la fin.

Contenu attendu :

```text
Premiere ligne
Deuxieme ligne
```

## 15.4 Rediriger les erreurs avec `2>`

```bash
commande-inexistante 2> erreurs.txt
```

Si la commande ne peut pas être exécutée, le Shell peut écrire son message d'erreur dans `erreurs.txt`.

L'erreur indique ici que la commande n'a pas pu être résolue.

## 15.5 Rediriger les deux sorties

Dans Bash, une forme courante est :

```bash
commande > sortie.txt 2>&1
```

La sortie standard est envoyée vers `sortie.txt`, puis la sortie d'erreur est dirigée vers la destination actuelle de la sortie standard.

Dans Bash et plusieurs Shells compatibles, on peut également employer :

```bash
commande &> sortie.txt
```

Cette dernière forme n'est pas prise en charge de façon universelle par tous les Shells.

## 15.6 Utiliser `/dev/null`

```bash
commande > /dev/null
```

La sortie standard est envoyée vers `/dev/null`, qui élimine les données écrites.

Dans Bash :

```bash
commande > /dev/null 2>&1
```

élimine aussi la sortie d'erreur.

Cette technique peut masquer des informations utiles. Elle ne rend pas une commande plus sûre : elle supprime simplement une partie de ses sorties visibles.

## 15.7 Le pipeline `|`

Le caractère `|` transmet la sortie standard d'une commande à l'entrée standard d'une autre.

Exemple :

```bash
cat journal.txt | grep "ERREUR"
```

Le contenu transmis par `cat` est traité par `grep`, qui affiche les lignes correspondant au motif.

Dans ce cas, la forme plus directe est :

```bash
grep "ERREUR" journal.txt
```

### Schéma du pipeline

```text
+----------------------------+
| Commande A                 |
| produit du texte           |
+----------------------------+
               |
               | stdout
               v
             PIPE
               |
               v
+----------------------------+
| Commande B                 |
| traite le texte recu       |
+----------------------------+
               |
               v
+----------------------------+
| Resultat final             |
+----------------------------+
```

## 15.8 Combiner `ps`, `grep` et `wc`

```bash
ps -ef | grep ssh
```

Cette commande recherche les lignes associées à `ssh`.

Elle peut afficher la ligne de `grep` elle-même et ne constitue pas une méthode parfaite d'identification d'un service. Lorsqu'il est disponible, `pgrep` peut être plus adapté.

Pour compter les lignes d'une sortie :

```bash
ps -ef | wc -l
```

Le résultat peut inclure une ligne d'en-tête. Il ne représente donc pas nécessairement le nombre exact de processus actifs.

## 15.9 Comprendre le code de retour

Une commande retourne généralement un code au Shell.

Par convention :

- `0` indique généralement une réussite.
- Une valeur différente de `0` indique généralement un échec ou une autre situation particulière.

Dans Bash, affichez le code de retour avec :

```bash
echo $?
```

Exemple :

```bash
true
echo $?
```

Résultat habituel :

```text
0
```

Puis :

```bash
false
echo $?
```

Résultat habituel :

```text
1
```

`$?` représente le code de retour de la commande exécutée précédemment dans le contexte du Shell.


# 16. Gérer les logiciels avec un gestionnaire de paquets

## 16.1 Pourquoi utiliser un gestionnaire de paquets ?

Un gestionnaire de paquets permet notamment :

- D'installer des logiciels.
- De mettre à jour les listes de paquets disponibles.
- De mettre à niveau les logiciels.
- De gérer les dépendances.
- De désinstaller certains logiciels.

Les gestionnaires de paquets facilitent la maintenance et permettent de s'appuyer sur les dépôts configurés par la distribution.

## 16.2 Comprendre APT

APT est utilisé sur Debian, Ubuntu et plusieurs distributions dérivées.

Les commandes qui suivent concernent ces systèmes. Vérifiez votre distribution avant de les utiliser.

## 16.3 Actualiser les listes de paquets

```bash
sudo apt update
```

Cette commande actualise les informations locales sur les paquets disponibles dans les dépôts configurés.

Elle n'installe pas à elle seule toutes les nouvelles versions des logiciels.

L'opération nécessite des privilèges et un accès aux dépôts configurés, sauf cas particulier.

## 16.4 Mettre à niveau les paquets

```bash
sudo apt upgrade
```

Cette commande propose des mises à niveau selon les informations disponibles et les règles d'APT.

Lisez les modifications proposées, les éventuelles suppressions et les avertissements avant de confirmer.

Dans un environnement professionnel, les mises à jour doivent être intégrées à une stratégie de maintenance et de validation.

## 16.5 Rechercher un logiciel

```bash
apt search tree
```

Recherche les paquets associés au terme `tree` dans les dépôts configurés.

## 16.6 Installer un logiciel

```bash
sudo apt install tree
```

Cette commande demande à APT d'installer le paquet `tree` si celui-ci est disponible.

Examinez la liste des modifications et confirmez uniquement si vous comprenez l'opération.

## 16.7 Vérifier l'installation

```bash
tree --version
```

Ou :

```bash
command -v tree
```

`command -v` indique comment le Shell résout ce nom. Le résultat peut différer selon que le nom correspond à un programme externe, une fonction ou un alias.

## 16.8 Désinstaller un logiciel

```bash
sudo apt remove tree
```

Cette commande demande la désinstallation du paquet. Une suppression ne retire pas nécessairement toutes les données de configuration associées.

Examinez toujours les modifications proposées avant de confirmer une suppression de paquets.

## 16.9 D'autres gestionnaires de paquets

| Famille ou distribution | Gestionnaire courant |
|---|---|
| Debian et Ubuntu | APT |
| Fedora | DNF |
| Arch Linux | Pacman |
| Certaines distributions SUSE | Zypper |

Les commandes diffèrent selon la distribution. Ne copiez pas une commande de gestion de paquets sans vérifier votre environnement.


# 17. Découvrir les commandes réseau

Les outils réseau sont particulièrement utiles en administration système et réseau.

Ce chapitre présente quelques commandes d'observation. Il ne remplace pas un cours complet sur TCP/IP, le routage, DNS ou le dépannage réseau.

## 17.1 Afficher les interfaces réseau

```bash
ip addr
```

Cette commande affiche les informations sur les interfaces réseau et leurs adresses.

Une forme courte couramment utilisée est :

```bash
ip a
```

Les informations peuvent inclure :

- Le nom de l'interface.
- Son état.
- L'adresse MAC.
- Les adresses IPv4.
- Les adresses IPv6.
- D'autres éléments de configuration.

Schéma conceptuel :

```text
+--------------------------------+
| Interface : eth0               |
+--------------------------------+
| Etat : UP                      |
| Adresse MAC : aa:bb:cc:dd:ee:ff|
| IPv4 : 192.168.1.20/24         |
+--------------------------------+
```

Ces informations sont illustratives. Votre machine peut employer d'autres noms d'interface et d'autres adresses.

Exemples de noms possibles :

```text
eth0
ens33
enp0s3
wlan0
```

## 17.2 Afficher les routes

```bash
ip route
```

Cette commande affiche des routes IPv4 dans la table consultée.

Une route par défaut peut apparaître sous cette forme :

```text
default via 192.168.1.1 dev eth0
```

Interprétation :

```text
default      -> route utilisee pour certaines destinations non couvertes
via ...      -> prochain saut, souvent le routeur
dev eth0     -> interface associee
```

Le résultat exact dépend de la configuration.

## 17.3 Tester la connectivité avec `ping`

```bash
ping -c 4 192.168.1.1
```

Sur un système qui prend en charge cette option, la commande envoie quatre requêtes ICMP vers l'adresse indiquée.

Elle teste certains aspects de la connectivité IP.

Un échec ne signifie pas nécessairement que l'hôte est hors service, car le trafic ICMP peut être filtré.

Un succès ne garantit pas non plus que tous les services applicatifs du destinataire fonctionnent.

## 17.4 Tester la résolution de noms

```bash
getent hosts example.com
```

Cette commande demande au système de résoudre le nom en utilisant les mécanismes de résolution configurés.

Les résultats peuvent dépendre de DNS, du fichier `/etc/hosts` et d'autres mécanismes disponibles.

## 17.5 Examiner les sockets en écoute

```bash
ss -tuln
```

Options courantes :

- `-t` : connexions TCP.
- `-u` : connexions UDP.
- `-l` : sockets en écoute.
- `-n` : représentation numérique des adresses et ports lorsque cela s'applique.

La commande donne un aperçu de certaines sockets réseau.

Le résultat peut dépendre des privilèges de l'utilisateur, des options utilisées et des mécanismes réseau disponibles.

## 17.6 Quelques ports courants

| Port TCP | Service fréquemment associé |
|---:|---|
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS sur TCP, lorsque utilisé |
| 80 | HTTP |
| 443 | HTTPS |

Ces associations sont conventionnelles. Elles ne garantissent pas qu'un service est installé ou actif sur une machine donnée.

DNS peut utiliser UDP ou TCP selon les besoins. Un service peut également être configuré pour écouter sur un autre port.

## 17.7 Atelier réseau

Exécutez :

```bash
ip addr
ip route
getent hosts example.com
ss -tuln
```

Répondez ensuite :

1. Combien d'interfaces réseau sont affichées ?
2. Quelle adresse IPv4 est attribuée à votre interface principale, si elle en possède une ?
3. Une route par défaut est-elle présente ?
4. Le système parvient-il à résoudre `example.com` ?
5. Quels ports apparaissent en écoute ?

Les résultats varient selon l'environnement. Le but est d'apprendre à lire les informations réelles de votre système.


# 18. Comprendre les variables d'environnement

## 18.1 Qu'est-ce qu'une variable ?

Une variable contient une valeur que le Shell ou un programme peut utiliser.

Dans Bash :

```bash
nom="Alice"
```

Pour afficher sa valeur :

```bash
echo "$nom"
```

Résultat :

```text
Alice
```

Les guillemets autour de l'expansion protègent généralement les valeurs contre les problèmes de découpage des arguments et d'expansion des motifs.

## 18.2 Pourquoi utiliser `$` ?

Lors de l'affectation, le nom de la variable s'écrit sans `$` :

```bash
ville="Douala"
```

Pour lire sa valeur :

```bash
echo "$ville"
```

Le caractère `$` indique au Shell qu'il doit développer la variable.

## 18.3 La variable `HOME`

```bash
echo "$HOME"
```

Affiche la valeur de la variable d'environnement `HOME`, normalement le répertoire personnel de l'utilisateur.

Exemple :

```text
/home/alice
```

## 18.4 La variable `USER`

```bash
echo "$USER"
```

Affiche généralement le nom d'utilisateur associé à la session. La valeur peut dépendre de l'environnement et de la façon dont elle a été définie.

Pour examiner l'identité effective de l'utilisateur, `whoami` reste utile.

## 18.5 La variable `PATH`

`PATH` contient une liste de répertoires dans lesquels le Shell recherche certains programmes externes.

```bash
echo "$PATH"
```

Exemple :

```text
/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin
```

Les deux-points séparent généralement les répertoires.

### Schéma : résolution d'une commande

```text
Utilisateur saisit une commande
              |
              v
Le Shell recherche comment resoudre le nom
              |
              v
Alias, fonction ou commande integree
              |
              v
Recherche d'un programme externe si necessaire
              |
              v
Recherche dans PATH selon le contexte
              |
              v
Execution du programme trouve
```

## 18.6 Définir une variable d'environnement

```bash
export FORMATION="Linux debutant"
```

Afficher sa valeur :

```bash
echo "$FORMATION"
```

`export` rend la variable disponible dans l'environnement des processus enfants qui seront lancés ensuite par le Shell.

## 18.7 Variable de Shell et variable d'environnement

Exemple :

```bash
nom="Alice"
export prenom="Awa"
```

Les deux variables peuvent être utilisées dans le Shell courant, mais `prenom` est exportée dans l'environnement des processus enfants.

Une variable non exportée n'est généralement pas transmise automatiquement comme variable d'environnement.

## 18.8 Supprimer une variable

```bash
unset FORMATION
```

Cette commande retire la variable du Shell courant.

Elle ne modifie pas rétroactivement l'environnement des processus déjà lancés.

## 18.9 Bonnes pratiques

Évitez de stocker des mots de passe ou des jetons d'accès dans des variables visibles sans protection suffisante.

Les variables d'environnement ne remplacent pas un gestionnaire de secrets adapté.


# 19. Écrire un premier script Shell

Un script Shell est un fichier contenant des instructions exécutées par un interpréteur, comme Bash.

Il permet de regrouper des commandes et d'automatiser les tâches répétitives.

## 19.1 Pourquoi créer un script ?

Imaginons que vous deviez régulièrement :

1. Vérifier votre utilisateur.
2. Afficher le répertoire courant.
3. Afficher la date.
4. Préparer un répertoire de travail.

Vous pourriez exécuter les commandes une par une, mais un script rend la procédure réutilisable.

## 19.2 Créer le premier script

Ouvrez un éditeur comme Nano :

```bash
nano bonjour.sh
```

Saisissez :

```bash
#!/usr/bin/env bash

echo "Bienvenue dans Linux"
echo "Utilisateur : $(whoami)"
echo "Repertoire courant : $(pwd)"
date
```

Enregistrez le fichier et quittez l'éditeur.

Dans Nano, les raccourcis courants sont :

- `Ctrl+O` : enregistrer.
- `Entrée` : confirmer le nom du fichier.
- `Ctrl+X` : quitter.

## 19.3 Comprendre le script

La première ligne est le *shebang* :

```bash
#!/usr/bin/env bash
```

Elle indique comment rechercher l'interpréteur Bash lorsque le fichier est lancé comme programme, dans un environnement compatible.

La commande :

```bash
echo "Bienvenue dans Linux"
```

affiche un message.

L'expression :

```bash
$(whoami)
```

demande au Shell d'exécuter `whoami`, puis d'insérer sa sortie.

L'expression :

```bash
$(pwd)
```

insère le résultat de `pwd`.

Enfin :

```bash
date
```

affiche les informations de date et d'heure du système.

## 19.4 Exécuter le script avec Bash

```bash
bash bonjour.sh
```

Cette méthode lance le script à travers Bash. Le fichier doit être lisible, mais n'a pas nécessairement besoin du bit d'exécution.

## 19.5 Rendre le script exécutable

```bash
chmod u+x bonjour.sh
```

Puis :

```bash
./bonjour.sh
```

Le préfixe `./` désigne le fichier situé dans le répertoire courant.

Le Shell ne recherche généralement pas automatiquement les programmes dans le répertoire courant lorsqu'on saisit seulement leur nom.

## 19.6 Utiliser des variables

Créez `informations.sh` :

```bash
#!/usr/bin/env bash

nom="Alice"
formation="Linux debutant"

echo "Nom : $nom"
echo "Formation : $formation"
```

Exécutez :

```bash
bash informations.sh
```

## 19.7 Créer un répertoire automatiquement

```bash
#!/usr/bin/env bash

mkdir -p atelier-automatique
echo "Le repertoire atelier-automatique est disponible."
```

La commande `mkdir -p` ne signale normalement pas d'erreur simplement parce que le répertoire existe déjà.

Cependant, le message final ne doit pas être interprété comme une preuve absolue de réussite sans vérifier le résultat de l'opération.

## 19.8 Vérifier le résultat d'une commande

Une forme plus fiable consiste à utiliser une condition :

```bash
#!/usr/bin/env bash

if mkdir -p atelier-automatique; then
    echo "Repertoire disponible."
else
    echo "Impossible de preparer le repertoire."
fi
```

Le bloc `if` évalue le code de retour de la commande.

## 19.9 Utiliser une condition

```bash
#!/usr/bin/env bash

if [ -d "atelier-linux" ]; then
    echo "Le repertoire existe."
else
    echo "Le repertoire n'existe pas."
fi
```

Interprétation :

- `[ -d "atelier-linux" ]` teste si le chemin désigne un répertoire.
- `then` introduit les instructions exécutées si le test réussit.
- `else` introduit les instructions exécutées dans le cas contraire.
- `fi` termine la condition.

D'autres tests existent :

- `-f` : fichier ordinaire.
- `-d` : répertoire.
- `-e` : chemin existant.
- `-r` : possibilité de lecture selon les mécanismes habituels du Shell.

## 19.10 Lire les arguments

Variables spéciales courantes :

- `$1` : premier argument.
- `$2` : deuxième argument.
- `$#` : nombre d'arguments.
- `$@` : liste des arguments.
- `$0` : nom utilisé pour invoquer le script, selon le contexte.

Exemple :

```bash
#!/usr/bin/env bash

echo "Premier argument : $1"
echo "Nombre d'arguments : $#"
```

Exécution :

```bash
bash arguments.sh bonjour Linux
```

Résultat attendu :

```text
Premier argument : bonjour
Nombre d'arguments : 2
```

## 19.11 Vérifier la présence d'un argument

```bash
#!/usr/bin/env bash

if [ "$#" -lt 1 ]; then
    echo "Usage : $0 NOM"
    exit 1
fi

nom="$1"

echo "Bonjour, $nom"
```

Exécution :

```bash
bash salutation.sh Alice
```

Le script vérifie que le premier argument existe. Si aucun argument n'est fourni, il affiche un message d'utilisation et termine avec un code non nul.

## 19.12 Les guillemets dans les scripts

Une variable peut contenir des espaces. Il faut donc protéger correctement les arguments.

Forme risquée dans de nombreux contextes :

```bash
cp $source $destination
```

Forme généralement préférable :

```bash
cp "$source" "$destination"
```

Les guillemets évitent plusieurs problèmes liés au découpage des arguments et à l'expansion des motifs.

## 19.13 Les erreurs fréquentes

### Oublier le bit d'exécution

Pour lancer directement un script, il faut généralement lui donner les permissions adaptées :

```bash
chmod u+x bonjour.sh
```

### Utiliser un mauvais chemin

```bash
bash /home/alice/scripts/bonjour.sh
```

Le chemin doit correspondre à l'emplacement réel.

### Ne pas vérifier les échecs

Un script fiable doit vérifier le résultat des opérations importantes avant d'annoncer leur succès.


# 20. Diagnostiquer les erreurs courantes

Un administrateur Linux doit observer avant de modifier.

Les erreurs font partie de l'apprentissage. L'objectif est de comprendre leur cause plutôt que de supprimer les symptômes au hasard.

## 20.1 Méthode de dépannage en six étapes

```text
+--------------------------------------+
| 1. OBSERVER                          |
| Lire le message d'erreur             |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 2. LOCALISER                         |
| Identifier le fichier ou service     |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 3. VERIFIER                          |
| Chemin, permissions, syntaxe         |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 4. RECHERCHER                        |
| Consulter la documentation           |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 5. CORRIGER                          |
| Effectuer une modification minimale  |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 6. VALIDER                           |
| Refaire le test                      |
+--------------------------------------+
```

## 20.2 Erreur : `No such file or directory`

Exemple :

```bash
cat rapport.txt
```

Le fichier peut ne pas exister dans le répertoire courant.

Vérifiez :

```bash
pwd
ls -la
find . -name "rapport.txt"
```

Causes possibles :

- Le fichier n'existe pas.
- Le nom est incorrect.
- Le fichier se trouve ailleurs.
- Le chemin relatif part d'un autre répertoire.
- Un répertoire parent est manquant.

## 20.3 Erreur : `Permission denied`

Vérifiez :

```bash
ls -l secret.txt
id
```

Le problème peut être lié aux permissions du fichier, aux permissions d'un répertoire parent, à une ACL ou à un autre mécanisme de sécurité.

N'appliquez pas automatiquement `chmod 777`. Identifiez d'abord le niveau d'accès nécessaire et la cause du refus.

## 20.4 Erreur : `command not found`

Exemple :

```bash
outl
```

Le Shell peut ne pas trouver de commande correspondant à ce nom.

Causes possibles :

- Faute de frappe.
- Programme non installé.
- Répertoire absent de `PATH`.
- Commande disponible dans un autre environnement.

Vérifiez :

```bash
command -v outl
echo "$PATH"
```

## 20.5 Vérifier l'espace disque

```bash
df -h
```

Affiche les informations sur l'espace des systèmes de fichiers montés, avec des tailles lisibles.

Pour estimer l'espace utilisé par un répertoire :

```bash
du -sh ~/Documents
```

Les résultats peuvent dépendre des liens, des fichiers supprimés encore ouverts et d'autres particularités du système de fichiers.

Ne supprimez pas de fichiers système au hasard pour libérer de la place.

## 20.6 Consulter les journaux

Sur un système utilisant systemd :

```bash
journalctl -b
```

Affiche les messages du démarrage courant, selon la configuration et les permissions.

Pour limiter la quantité d'informations :

```bash
journalctl -b -n 50
```

Certains journaux se trouvent aussi dans `/var/log/`.

Pour examiner le répertoire :

```bash
ls -lah /var/log
```

L'accès à certains journaux peut nécessiter des privilèges.

## 20.7 Vérifier un service

Sur un système utilisant systemd :

```bash
systemctl status nom-du-service
```

Remplacez `nom-du-service` par une unité réelle.

Pour le service SSH, le nom peut être `ssh` ou `sshd` selon la distribution.

Ne redémarrez pas un service de production sans comprendre les conséquences.


# 21. Travaux pratiques guidés

Les travaux pratiques doivent être réalisés dans votre répertoire personnel de test.

## TP 1 — Prise en main du terminal

### Objectifs

- Identifier l'utilisateur courant.
- Connaître le répertoire courant.
- Explorer des répertoires.
- Comprendre la navigation.

### Étape 1 : identifier la session

```bash
whoami
pwd
uname -r
```

Notez les résultats.

### Étape 2 : explorer

```bash
ls
ls -la
ls /etc
```

Comparez les sorties et expliquez pourquoi `ls -la` affiche davantage d'informations que `ls`.

### Étape 3 : naviguer

```bash
cd /
pwd

cd /tmp
pwd

cd ~
pwd
```

### Résultat attendu

Vous devez pouvoir expliquer où vous vous trouvez après chacune des commandes.


## TP 2 — Construire une arborescence

### Objectif

Créer un espace organisé pour les documents et scripts d'un projet.

### Étape 1 : créer les répertoires

```bash
mkdir -p ~/formation-linux/documents
mkdir -p ~/formation-linux/scripts
mkdir -p ~/formation-linux/journaux
mkdir -p ~/formation-linux/archives
```

### Étape 2 : créer les fichiers

```bash
touch ~/formation-linux/documents/notes.txt
touch ~/formation-linux/documents/commandes.txt
touch ~/formation-linux/journaux/activite.log
```

### Étape 3 : ajouter du contenu

```bash
echo "Premiere note Linux" > ~/formation-linux/documents/notes.txt

echo "pwd : afficher le repertoire courant" \
    > ~/formation-linux/documents/commandes.txt

echo "Projet initialise" \
    >> ~/formation-linux/journaux/activite.log
```

### Étape 4 : vérifier

```bash
cat ~/formation-linux/documents/notes.txt
cat ~/formation-linux/documents/commandes.txt
cat ~/formation-linux/journaux/activite.log
```

### Étape 5 : inspecter l'arborescence

```bash
find ~/formation-linux -print
```

### Résultat attendu

Vous devez obtenir quatre sous-répertoires sous `formation-linux`, avec les fichiers créés dans les bons emplacements.


## TP 3 — Rechercher des fichiers et du texte

### Objectif

Retrouver des fichiers et rechercher des informations à l'intérieur.

### Étape 1 : créer les fichiers

```bash
touch ~/formation-linux/documents/serveur.txt
touch ~/formation-linux/documents/reseau.txt
touch ~/formation-linux/documents/securite.txt
```

### Étape 2 : ajouter du contenu

```bash
echo "Linux peut heberger des services reseau." \
    > ~/formation-linux/documents/serveur.txt

echo "Une interface possede une configuration IP." \
    > ~/formation-linux/documents/reseau.txt

echo "Les permissions limitent certains acces." \
    > ~/formation-linux/documents/securite.txt
```

### Étape 3 : rechercher les fichiers texte

```bash
find ~/formation-linux -type f -name "*.txt"
```

### Étape 4 : rechercher le mot Linux

```bash
grep -R -n "Linux" ~/formation-linux/documents
```

### Étape 5 : rechercher IP

```bash
grep -R -n "IP" ~/formation-linux/documents
```

### Questions

1. Quelle commande recherche des fichiers par leur nom ?
2. Quelle commande recherche un terme dans le contenu ?
3. Que fait l'option `-n` de `grep` ?
4. Pourquoi utiliser `-R` ?

### Réponses

1. `find`.
2. `grep`.
3. Elle affiche généralement le numéro des lignes correspondantes.
4. Elle étend la recherche aux fichiers des sous-répertoires.


## TP 4 — Appliquer des permissions

### Objectif

Comprendre comment les permissions classiques limitent l'accès.

### Étape 1 : créer un fichier

```bash
touch ~/formation-linux/documents/confidentiel.txt

echo "Donnees de test" \
    > ~/formation-linux/documents/confidentiel.txt
```

### Étape 2 : examiner les permissions

```bash
ls -l ~/formation-linux/documents/confidentiel.txt
```

### Étape 3 : limiter les permissions

```bash
chmod 600 ~/formation-linux/documents/confidentiel.txt
```

### Étape 4 : vérifier

```bash
ls -l ~/formation-linux/documents/confidentiel.txt
```

### Questions

1. Que représentent les chiffres `600` ?
2. Qui possède la permission de lecture selon le mode classique ?
3. Pourquoi les permissions des répertoires parents sont-elles importantes ?
4. Pourquoi éviter `chmod 777` comme réponse automatique ?

### Réponses

1. Le propriétaire reçoit `rw-`; le groupe et les autres n'obtiennent aucune permission classique.
2. Le propriétaire.
3. Parce que la traversée des répertoires est nécessaire pour accéder au fichier.
4. Parce que cette commande autorise des accès et modifications trop larges dans de nombreux contextes.


## TP 5 — Observer les processus

### Objectif

Utiliser quelques outils d'observation des processus.

### Étape 1 : afficher les processus

```bash
ps -ef
```

### Étape 2 : rechercher Bash

```bash
pgrep -a bash
```

### Étape 3 : observer les ressources

```bash
top
```

Quittez avec `q`.

### Questions

1. Que représente le PID ?
2. Quelle différence existe entre un programme et un processus ?
3. Pourquoi faut-il identifier un processus avant de lui envoyer un signal ?
4. Pourquoi utiliser `SIGKILL` avec prudence ?

### Réponses

1. L'identifiant du processus.
2. Un programme est un ensemble d'instructions ; un processus est une instance en cours d'exécution.
3. Un mauvais PID peut désigner une application importante ou différente de celle visée.
4. Le processus ne peut pas intercepter ce signal pour effectuer son nettoyage habituel.


## TP 6 — Utiliser les redirections

### Objectif

Écrire un journal, ajouter des événements et rechercher une information.

### Étape 1 : créer le journal

```bash
echo "Demarrage du laboratoire" \
    > ~/formation-linux/journaux/tp-redirections.log
```

### Étape 2 : ajouter des événements

```bash
echo "Verification des fichiers" \
    >> ~/formation-linux/journaux/tp-redirections.log

echo "Verification terminee" \
    >> ~/formation-linux/journaux/tp-redirections.log
```

### Étape 3 : afficher le journal

```bash
cat ~/formation-linux/journaux/tp-redirections.log
```

### Étape 4 : compter les lignes

```bash
wc -l ~/formation-linux/journaux/tp-redirections.log
```

### Étape 5 : rechercher un événement

```bash
grep -n "Verification" ~/formation-linux/journaux/tp-redirections.log
```

### Questions

1. Que fait `>` ?
2. Que fait `>>` ?
3. Que renvoie `wc -l` ?
4. À quoi sert un journal ?

### Réponses

1. Il redirige la sortie standard vers un fichier et remplace généralement son contenu.
2. Il ajoute la sortie à la fin du fichier.
3. Il affiche le nombre de lignes.
4. Un journal conserve une trace des événements et facilite l'analyse.


# 22. Exercices d'évaluation corrigés

Essayez de répondre avant de lire les corrections.

## Exercice 1 — Architecture Linux

**Question :** quelle différence existe entre le noyau Linux et une distribution ?

**Correction :** le noyau gère les ressources et fournit les mécanismes fondamentaux du système. Une distribution rassemble le noyau et un ensemble cohérent d'utilitaires, de logiciels, de configurations et d'outils de gestion.

## Exercice 2 — Chemin absolu ou relatif

**Question :** depuis `/home/alice`, que désigne `Documents/notes.txt` ?

**Correction :**

```text
/home/alice/Documents/notes.txt
```

Il s'agit d'un chemin relatif, car il ne commence pas par `/`.

## Exercice 3 — Navigation

**Question :** depuis `/var/log`, où mène `cd ..` ?

**Correction :**

```text
/var
```

## Exercice 4 — Créer une arborescence

**Question :** quelle commande crée `projet/scripts/tests` même si les parents n'existent pas ?

**Correction :**

```bash
mkdir -p projet/scripts/tests
```

## Exercice 5 — Copier un fichier

**Question :** comment copier `rapport.txt` vers `rapport-copie.txt` ?

**Correction :**

```bash
cp rapport.txt rapport-copie.txt
```

Vérifiez toujours que la destination n'écrase pas un fichier important.

## Exercice 6 — Déplacer un fichier

**Question :** comment déplacer `notes.txt` dans `archives` ?

**Correction :**

```bash
mv notes.txt archives/
```

Le répertoire doit exister et être accessible.

## Exercice 7 — Lire un fichier long

**Question :** quelle commande permet de parcourir progressivement un fichier ?

**Correction :**

```bash
less fichier.txt
```

## Exercice 8 — Rechercher sans distinguer la casse

**Question :** comment rechercher `ERREUR` dans `application.log`, sans distinction entre majuscules et minuscules ?

**Correction :**

```bash
grep -i "ERREUR" application.log
```

## Exercice 9 — Rechercher les fichiers `.conf`

**Question :** comment retrouver les fichiers ordinaires se terminant par `.conf` sous `/etc` ?

**Correction :**

```bash
find /etc -type f -name "*.conf"
```

Certains chemins peuvent ne pas être accessibles selon l'utilisateur et la configuration.

## Exercice 10 — Permissions

**Question :** que signifie `chmod 640 fichier.txt` ?

**Correction :**

```text
6 = rw- pour le proprietaire
4 = r-- pour le groupe
0 = --- pour les autres
```

Le propriétaire peut lire et écrire, le groupe peut lire et les autres n'obtiennent aucune permission classique.

## Exercice 11 — Utilisateur courant

**Question :** quelle commande affiche le nom de l'utilisateur effectif ?

**Correction :**

```bash
whoami
```

## Exercice 12 — Observer les processus

**Question :** quelle commande fournit un aperçu interactif des processus ?

**Correction :**

```bash
top
```

Quittez généralement avec `q`.

## Exercice 13 — Redirections

**Question :** quelle différence existe entre les deux commandes ?

```bash
echo "A" > journal.txt
echo "B" >> journal.txt
```

**Correction :** la première remplace généralement le contenu du fichier. La deuxième ajoute `B` à la fin.

## Exercice 14 — Pipeline

**Question :** que fait cette commande ?

```bash
cat journal.txt | grep "ERREUR"
```

**Correction :** elle transmet le contenu affiché par `cat` à `grep`, qui filtre les lignes correspondant au motif.

La forme directe est :

```bash
grep "ERREUR" journal.txt
```

## Exercice 15 — Variable

**Question :** comment afficher la variable Bash `formation` ?

**Correction :**

```bash
echo "$formation"
```

La variable doit avoir été définie dans le contexte courant.

## Exercice 16 — Script

**Question :** quel est le rôle de `#!/usr/bin/env bash` ?

**Correction :** il indique comment rechercher l'interpréteur Bash lors du lancement direct du script, dans un environnement compatible.

## Exercice 17 — Réseau

**Question :** quelle commande affiche les adresses des interfaces réseau ?

**Correction :**

```bash
ip addr
```

## Exercice 18 — Dépannage

**Question :** pourquoi `chmod 777 fichier.txt` n'est-il pas une bonne première réponse à une erreur de permission ?

**Correction :** il attribue des permissions très larges. Il faut d'abord comprendre la cause du refus, examiner les permissions et identifier le niveau d'accès nécessaire.


# 23. Fiche de révision

## 23.1 Navigation

| Commande | Utilité |
|---|---|
| `pwd` | Afficher le répertoire courant |
| `ls` | Lister le contenu |
| `ls -la` | Afficher les détails et les entrées cachées |
| `cd repertoire` | Entrer dans un répertoire |
| `cd ..` | Remonter au parent |
| `cd ~` | Revenir au répertoire personnel |
| `cd -` | Revenir au répertoire précédent |

## 23.2 Fichiers et répertoires

| Commande | Utilité |
|---|---|
| `mkdir dossier` | Créer un répertoire |
| `mkdir -p a/b/c` | Créer une arborescence |
| `touch fichier.txt` | Créer un fichier vide s'il n'existe pas |
| `cp source destination` | Copier un fichier |
| `cp -r source destination` | Copier récursivement |
| `mv source destination` | Déplacer ou renommer |
| `rm fichier.txt` | Supprimer un fichier |
| `rmdir dossier` | Supprimer un répertoire vide |
| `find . -type f` | Rechercher des fichiers ordinaires |

## 23.3 Lecture et recherche

| Commande | Utilité |
|---|---|
| `cat fichier.txt` | Afficher le contenu |
| `less fichier.txt` | Consulter un long fichier |
| `head fichier.txt` | Afficher les premières lignes |
| `tail fichier.txt` | Afficher les dernières lignes |
| `tail -f fichier.log` | Suivre les nouvelles lignes |
| `grep "mot" fichier.txt` | Rechercher un motif |
| `grep -i "mot" fichier.txt` | Recherche insensible à la casse |
| `wc -l fichier.txt` | Compter les lignes |
| `find . -name "*.txt"` | Rechercher par nom |

## 23.4 Utilisateurs et permissions

| Commande | Utilité |
|---|---|
| `whoami` | Afficher l'utilisateur effectif |
| `id` | Afficher les identifiants et groupes |
| `sudo commande` | Exécuter avec des privilèges autorisés |
| `ls -l` | Examiner les permissions |
| `chmod 644 fichier.txt` | Définir les permissions classiques |
| `chmod u+x script.sh` | Ajouter l'exécution au propriétaire |
| `chown alice fichier.txt` | Changer le propriétaire lorsque cela est autorisé |
| `stat fichier.txt` | Examiner les métadonnées |

## 23.5 Processus

| Commande | Utilité |
|---|---|
| `ps` | Examiner les processus du contexte courant |
| `ps -ef` | Afficher un ensemble de processus |
| `pgrep -a bash` | Rechercher des processus correspondant à Bash |
| `top` | Surveiller les processus |
| `kill PID` | Envoyer normalement `SIGTERM` au PID |
| `kill -KILL PID` | Envoyer `SIGKILL`, à utiliser en dernier recours |

## 23.6 Redirections

| Syntaxe | Utilité |
|---|---|
| `commande > fichier` | Remplacer généralement le contenu avec la sortie standard |
| `commande >> fichier` | Ajouter la sortie standard à la fin |
| `commande 2> fichier` | Rediriger la sortie d'erreur |
| `commande > sortie 2>&1` | Réunir les flux dans les Shells compatibles |
| `commande1 \| commande2` | Transmettre la sortie standard à une autre commande |

## 23.7 Système et réseau

| Commande | Utilité |
|---|---|
| `uname -r` | Afficher la version du noyau |
| `cat /etc/os-release` | Identifier la distribution |
| `df -h` | Examiner l'espace des systèmes de fichiers |
| `du -sh repertoire` | Estimer l'espace utilisé par un répertoire |
| `ip addr` | Afficher les interfaces et les adresses |
| `ip route` | Afficher les routes |
| `ping -c 4 adresse` | Tester certains aspects de la connectivité IP |
| `getent hosts nom` | Demander la résolution d'un nom |
| `ss -tuln` | Examiner certaines sockets TCP et UDP en écoute |

## 23.8 Caractères à connaître

```text
/     Racine ou separateur de chemin
.     Repertoire courant
..    Repertoire parent
~     Repertoire personnel dans les Shells courants
*     Joker correspondant generalement a zero ou plusieurs caracteres
?     Joker correspondant a un caractere
>     Redirection avec remplacement general du fichier
>>    Redirection en ajout
|     Pipeline
$     Expansion de variable dans le Shell
```


# 24. Challenge final — Organiser et automatiser un environnement de travail

## 24.1 Scénario

Vous êtes chargé de préparer un petit espace de travail pour une équipe de support informatique.

L'équipe souhaite disposer :

- D'une arborescence organisée.
- De documents de référence.
- D'un journal d'activité.
- De permissions adaptées.
- D'un script vérifiant la structure du projet.

Vous devez créer cet environnement et automatiser une partie des vérifications.

**Le challenge est un exercice de synthèse :** il mobilise les notions vues dans le cours, mais ne remplace pas les explications et les travaux pratiques précédents.

## 24.2 Compétences évaluées

Vous devrez :

- Créer des répertoires.
- Manipuler des fichiers.
- Écrire des informations dans un journal.
- Rechercher du contenu.
- Appliquer des permissions.
- Utiliser des variables Bash.
- Vérifier l'existence de chemins.
- Créer un script réutilisable.
- Contrôler les résultats.

## 24.3 Précautions

Réalisez tout le challenge dans votre répertoire personnel.

Le chemin choisi est :

```text
~/projet-support
```

N'exécutez pas ce challenge dans `/etc`, `/usr`, `/var` ou dans un répertoire de production.

N'utilisez pas `sudo` pour ces exercices.

## 24.4 Étape 1 — Créer l'arborescence

Créez la structure suivante :

```text
projet-support/
|
+-- documents/
|
+-- scripts/
|
+-- journaux/
|
+-- archives/
|
+-- rapports/
```

Utilisez `mkdir`.

**Validation :** le répertoire principal et les cinq sous-répertoires doivent exister.

## 24.5 Étape 2 — Créer les documents

Dans `documents/`, créez :

```text
documentation.txt
reseau.txt
securite.txt
```

Le contenu doit expliquer :

- Que le projet sert de support à l'administration Linux.
- Qu'une adresse IP identifie une interface dans un contexte réseau.
- Que les permissions limitent les opérations autorisées sur les fichiers.

Vous pouvez employer vos propres formulations.

## 24.6 Étape 3 — Créer le journal

Dans `journaux/`, créez :

```text
activite.log
```

Le journal doit contenir au minimum les événements suivants :

```text
Initialisation du projet
Creation de l'arborescence
Creation des documents
Verification du projet
```

## 24.7 Étape 4 — Vérifier les fichiers

Affichez le contenu des documents et du journal.

Utilisez également une commande qui retrouve tous les fichiers dont le nom se termine par `.txt`.

**Validation :** les trois documents doivent exister et être lisibles. Le journal doit comporter plusieurs lignes.

## 24.8 Étape 5 — Appliquer les permissions

Appliquez le mode `644` aux trois fichiers de documentation.

Pour le fichier de journal, choisissez un mode limitant les permissions classiques à la lecture et à l'écriture du propriétaire.

Vérifiez les permissions avec `ls -l`.

Expliquez pourquoi accorder toutes les permissions à tout le monde n'est pas une bonne stratégie par défaut.

## 24.9 Étape 6 — Créer un script de vérification

Dans `scripts/`, créez :

```text
verifier-projet.sh
```

Le script doit :

1. Afficher un titre.
2. Vérifier l'existence du répertoire principal.
3. Vérifier l'existence de `documents/`.
4. Vérifier l'existence de `journaux/`.
5. Vérifier la présence des trois documents attendus.
6. Afficher la liste des documents.
7. Ajouter une ligne de vérification au journal.
8. Afficher un message de succès uniquement si les contrôles requis ont réussi.

Le script doit définir des variables pour le chemin principal et le chemin du journal.

Il ne doit pas nécessiter de privilèges administrateur.

## 24.10 Étape 7 — Tester le script

Rendez le script exécutable :

```bash
chmod u+x ~/projet-support/scripts/verifier-projet.sh
```

Exécutez-le :

```bash
~/projet-support/scripts/verifier-projet.sh
```

Vérifiez ensuite le journal :

```bash
cat ~/projet-support/journaux/activite.log
```

Si une erreur apparaît, identifiez sa cause avant de modifier le code.

## 24.11 Étape 8 — Contrôle final

Vérifiez que :

- Le répertoire principal existe.
- Les sous-répertoires sont présents.
- Les trois fichiers de documentation sont corrects.
- Le journal contient les événements attendus.
- Les permissions correspondent au choix effectué.
- Le script est exécutable.
- Le script détecte une structure valide.
- Les messages affichés correspondent réellement aux contrôles effectués.

## 24.12 Barème

| Compétence | Points |
|---|---:|
| Création correcte de l'arborescence | 15 |
| Création et contenu des documents | 15 |
| Gestion du journal | 15 |
| Utilisation des commandes de vérification | 10 |
| Permissions cohérentes | 15 |
| Variables et conditions Shell | 15 |
| Fiabilité du script | 10 |
| Vérification finale et explication | 5 |
| **Total** | **100** |

Une bonne solution doit être compréhensible, vérifiable et suffisamment robuste pour signaler les erreurs importantes.


# 25. Correction détaillée du challenge final

Essayez de terminer le challenge avant de recopier cette solution.

## 25.1 Créer l'arborescence

```bash
mkdir -p ~/projet-support/documents
mkdir -p ~/projet-support/scripts
mkdir -p ~/projet-support/journaux
mkdir -p ~/projet-support/archives
mkdir -p ~/projet-support/rapports
```

L'option `-p` permet de créer les répertoires parents manquants.

Vérifiez la structure :

```bash
find ~/projet-support -print
```

## 25.2 Créer les documents

```bash
echo "Espace de support et d'administration Linux." \
    > ~/projet-support/documents/documentation.txt
```

Créer le document réseau :

```bash
echo "Une adresse IP identifie une interface dans un contexte reseau." \
    > ~/projet-support/documents/reseau.txt
```

Créer le document sécurité :

```bash
echo "Les permissions limitent les operations autorisees sur les fichiers et repertoires." \
    > ~/projet-support/documents/securite.txt
```

Chaque commande écrit une ligne dans le fichier indiqué.

La redirection `>` remplace le contenu existant du fichier de destination. Dans cet exercice, ce comportement est intentionnel.

## 25.3 Créer le journal

```bash
echo "Initialisation du projet" \
    > ~/projet-support/journaux/activite.log
```

Ajouter ensuite les autres événements :

```bash
echo "Creation de l'arborescence" \
    >> ~/projet-support/journaux/activite.log

echo "Creation des documents" \
    >> ~/projet-support/journaux/activite.log

echo "Verification du projet" \
    >> ~/projet-support/journaux/activite.log
```

La première commande crée le journal ou remplace son contenu existant. Les suivantes ajoutent des lignes.

## 25.4 Vérifier les documents

```bash
cat ~/projet-support/documents/documentation.txt
cat ~/projet-support/documents/reseau.txt
cat ~/projet-support/documents/securite.txt
```

Afficher le journal :

```bash
cat ~/projet-support/journaux/activite.log
```

Retrouver les fichiers texte :

```bash
find ~/projet-support -type f -name "*.txt"
```

Compter les lignes du journal :

```bash
wc -l ~/projet-support/journaux/activite.log
```

Avec les quatre événements ajoutés, le résultat devrait indiquer quatre lignes si aucune autre opération n'a modifié le fichier.

## 25.5 Appliquer les permissions

```bash
chmod 644 ~/projet-support/documents/documentation.txt
chmod 644 ~/projet-support/documents/reseau.txt
chmod 644 ~/projet-support/documents/securite.txt
```

Pour le journal :

```bash
chmod 600 ~/projet-support/journaux/activite.log
```

Le mode `600` permet au propriétaire de lire et modifier le journal, sans accorder les permissions classiques au groupe et aux autres.

Vérifiez :

```bash
ls -l ~/projet-support/documents
ls -l ~/projet-support/journaux/activite.log
```

Les permissions des répertoires parents restent importantes.

## 25.6 Script de vérification corrigé

Créez le script :

```bash
nano ~/projet-support/scripts/verifier-projet.sh
```

Collez le contenu suivant :

```bash
#!/usr/bin/env bash

# Chemin principal du projet.
PROJET="$HOME/projet-support"

# Chemin du fichier de journal.
JOURNAL="$PROJET/journaux/activite.log"

echo "======================================"
echo " VERIFICATION DU PROJET DE SUPPORT"
echo "======================================"

# Verifier le repertoire principal.
if [ ! -d "$PROJET" ]; then
    echo "ERREUR : le repertoire principal est absent."
    exit 1
fi

# Verifier le repertoire des documents.
if [ ! -d "$PROJET/documents" ]; then
    echo "ERREUR : le repertoire documents est absent."
    exit 1
fi

# Verifier le repertoire des journaux.
if [ ! -d "$PROJET/journaux" ]; then
    echo "ERREUR : le repertoire journaux est absent."
    exit 1
fi

# Verifier l'existence des documents attendus.
for fichier in documentation.txt reseau.txt securite.txt; do
    if [ ! -f "$PROJET/documents/$fichier" ]; then
        echo "ERREUR : document manquant : $fichier"
        exit 1
    fi
done

# Verifier l'existence du journal.
if [ ! -f "$JOURNAL" ]; then
    echo "ERREUR : le fichier de journal est absent."
    exit 1
fi

# Afficher les documents.
echo
echo "Documents disponibles :"
ls -l "$PROJET/documents"

# Ajouter une trace au journal.
if ! echo "Verification executee le $(date)" >> "$JOURNAL"; then
    echo "ERREUR : impossible d'ecrire dans le journal."
    exit 1
fi

echo
echo "Verification terminee avec succes."
exit 0
```

## 25.7 Analyser le script

### Les variables

```bash
PROJET="$HOME/projet-support"
JOURNAL="$PROJET/journaux/activite.log"
```

Le chemin principal est stocké dans `PROJET`. Le chemin du journal est construit à partir de cette variable pour éviter les répétitions.

Les guillemets contribuent à protéger les chemins qui contiendraient des espaces.

### Les conditions

```bash
if [ ! -d "$PROJET" ]; then
```

Cette condition vérifie si le chemin ne désigne pas un répertoire existant et accessible selon le test `-d`.

Le symbole `!` inverse le résultat du test.

Si le répertoire est absent, le script affiche une erreur puis se termine avec :

```bash
exit 1
```

Le code de sortie `1` est utilisé ici pour signaler un échec.

### La boucle `for`

```bash
for fichier in documentation.txt reseau.txt securite.txt; do
```

La boucle parcourt les trois noms.

À chaque passage, la variable `fichier` contient le nom courant.

Le test :

```bash
[ ! -f "$PROJET/documents/$fichier" ]
```

permet de détecter l'absence d'un fichier ordinaire.

Si un fichier manque, le script signale le problème et quitte.

### L'écriture dans le journal

```bash
echo "Verification executee le $(date)" >> "$JOURNAL"
```

La sortie est ajoutée à la fin du journal. `$(date)` insère le résultat de la commande `date`.

Le script vérifie ensuite le résultat de l'opération. Si l'écriture échoue, un message d'erreur est affiché.

### Le code final

```bash
exit 0
```

Dans ce script, le code `0` indique que les contrôles implémentés ont réussi.

Il ne garantit pas que l'ensemble du système informatique est parfaitement opérationnel. Il signale uniquement que les vérifications prévues par ce script ont abouti.

## 25.8 Rendre le script exécutable et le lancer

```bash
chmod u+x ~/projet-support/scripts/verifier-projet.sh
```

Puis :

```bash
~/projet-support/scripts/verifier-projet.sh
```

Le résultat attendu doit indiquer que la vérification s'est terminée avec succès si tous les contrôles aboutissent.

Pour examiner le code de retour immédiatement après le script :

```bash
echo $?
```

Un résultat `0` indique que le script a réussi selon sa logique.

Un code différent de zéro peut signaler qu'un répertoire ou un document manque, ou qu'une opération a échoué.

## 25.9 Contrôle final

Exécutez :

```bash
find ~/projet-support -print
```

Puis :

```bash
cat ~/projet-support/journaux/activite.log
```

Enfin :

```bash
ls -l ~/projet-support/documents
ls -l ~/projet-support/journaux/activite.log
ls -l ~/projet-support/scripts
```

L'arborescence attendue ressemble à ceci :

```text
~/projet-support/
|
+-- documents/
|   +-- documentation.txt
|   +-- reseau.txt
|   +-- securite.txt
|
+-- scripts/
|   +-- verifier-projet.sh
|
+-- journaux/
|   +-- activite.log
|
+-- archives/
|
+-- rapports/
```

Le journal contient les événements initiaux et les lignes ajoutées lors des exécutions du script.

Si votre résultat diffère, recherchez la cause avant de modifier les commandes.


# 26. Checklist finale des compétences acquises

Utilisez cette liste pour évaluer votre autonomie.

## Compréhension de Linux

- [ ] Je sais distinguer le noyau Linux et une distribution.
- [ ] Je comprends le rôle du Shell.
- [ ] Je sais distinguer le terminal du Shell.
- [ ] Je connais les principaux répertoires Linux.
- [ ] Je comprends les chemins absolus et relatifs.

## Utilisation du Shell

- [ ] Je sais afficher le répertoire courant avec `pwd`.
- [ ] Je sais lister les fichiers avec `ls`.
- [ ] Je sais naviguer avec `cd`.
- [ ] Je sais consulter une page de manuel avec `man`.
- [ ] Je sais utiliser l'aide d'une commande.
- [ ] Je sais interpréter les options et arguments.

## Gestion des fichiers

- [ ] Je sais créer des répertoires avec `mkdir`.
- [ ] Je sais créer des fichiers avec `touch`.
- [ ] Je sais copier des fichiers avec `cp`.
- [ ] Je sais déplacer et renommer avec `mv`.
- [ ] Je comprends les risques liés à `rm`.
- [ ] Je sais lire des fichiers avec `cat` et `less`.
- [ ] Je sais rechercher des fichiers avec `find`.
- [ ] Je sais rechercher du texte avec `grep`.

## Utilisateurs et permissions

- [ ] Je sais identifier l'utilisateur courant avec `whoami`.
- [ ] Je sais examiner les groupes avec `id`.
- [ ] Je comprends le rôle de `sudo`.
- [ ] Je sais interpréter `r`, `w` et `x`.
- [ ] Je sais lire une permission comme `-rw-r--r--`.
- [ ] Je sais expliquer les modes `644`, `600` et `755`.
- [ ] Je comprends pourquoi `chmod 777` n'est pas une solution universelle.
- [ ] Je sais examiner les permissions avec `ls -l` et `stat`.

## Processus et diagnostic

- [ ] Je sais examiner les processus avec `ps`.
- [ ] Je sais utiliser `top`.
- [ ] Je comprends le rôle du PID.
- [ ] Je sais pourquoi il faut identifier le processus avant d'envoyer un signal.
- [ ] Je sais distinguer une erreur de chemin d'une erreur de permission.
- [ ] Je sais examiner des informations réseau.
- [ ] Je sais vérifier l'espace disque avec `df` et `du`.

## Redirections et automatisation

- [ ] Je comprends `>`, `>>` et `2>`.
- [ ] Je sais expliquer le fonctionnement d'un pipeline.
- [ ] Je sais lire et définir une variable Bash.
- [ ] Je sais utiliser une condition simple.
- [ ] Je sais créer et exécuter un script Shell.
- [ ] Je sais examiner le code de retour d'une commande.
- [ ] Je sais vérifier qu'une opération a réussi avant d'annoncer son succès.


# Conclusion générale

Linux devient plus facile à administrer lorsque l'on comprend les relations entre les commandes, les chemins, les fichiers, les permissions et les processus.

Le Shell fournit un moyen direct d'observer et de contrôler le système. Il permet également de combiner de petits outils pour automatiser des tâches répétitives.

Les compétences de ce cours constituent une base pour poursuivre vers :

- L'administration Linux.
- La gestion des serveurs.
- Les réseaux informatiques.
- L'automatisation avec Bash et Python.
- Les conteneurs et les plateformes cloud.
- La gestion des journaux.
- La sécurité des systèmes.
- Les outils d'infrastructure comme Ansible.

La prochaine étape consiste à refaire les travaux pratiques sans consulter les corrections, puis à adapter le challenge final à un autre projet.

**Objectif à retenir :** ne pas seulement mémoriser les commandes, mais comprendre leurs effets, vérifier leurs résultats et les utiliser sans mettre les données ou le système en danger.

Fin du cours — Introduction à Linux et au Shell, niveau débutant.