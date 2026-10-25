# Administration Linux avancée
## Cours complet — Niveau intermédiaire

> **Fichier :** `linux-intermediaire.md`  
> **Parcours :** Administration systèmes et réseaux  
> **Niveau :** Intermédiaire  
> **Prérequis :** Avoir suivi les bases de Linux et du Shell, ou maîtriser les compétences équivalentes.  
> **Environnement conseillé :** Debian ou Ubuntu Server dans une machine virtuelle.  
> **Alternatives :** Fedora, Rocky Linux ou une autre distribution Linux adaptée aux exercices.  
> **Objectif général :** Administrer un système Linux de manière structurée, contrôler les services, gérer le stockage, sécuriser les accès, diagnostiquer les incidents et automatiser les opérations courantes.


# Sommaire

1. Positionnement du cours et objectifs pédagogiques
2. Architecture opérationnelle d'un serveur Linux
3. Gestion avancée des utilisateurs et des groupes
4. Permissions avancées, ACL et umask
5. Administration des processus et des ressources
6. Gestion des services avec systemd
7. Diagnostic et analyse des journaux
8. Gestion avancée du stockage et des systèmes de fichiers
9. Sauvegardes et restauration
10. Administration réseau avec les outils Linux
11. Administration et sécurisation de SSH
12. Pare-feu et contrôle des connexions
13. Gestion des logiciels et maintenance du système
14. Automatisation avec cron et les timers systemd
15. Écriture de scripts Bash robustes
16. Surveillance et diagnostic des performances
17. Sécurisation opérationnelle d'un serveur
18. Méthode professionnelle de résolution d'incidents
19. Travaux pratiques guidés
20. Exercices d'évaluation corrigés
21. Fiche de référence des commandes
22. Challenge final : exploitation d'un serveur Linux
23. Correction détaillée du challenge
24. Checklist de validation des compétences


# 1. Positionnement du cours et objectifs pédagogiques

Le niveau intermédiaire marque une évolution importante dans l'apprentissage de Linux.

Au niveau débutant, l'objectif principal est de savoir naviguer dans le système, manipuler les fichiers et utiliser les commandes fondamentales.

À ce niveau, l'objectif est différent : il faut commencer à **administrer un système, comprendre son état, anticiper les défaillances et appliquer des modifications maîtrisées**.

Un administrateur intermédiaire doit pouvoir examiner un service, comprendre pourquoi il ne démarre pas, identifier un problème de permissions, analyser une saturation disque, vérifier la connectivité réseau et automatiser des contrôles répétitifs.

Il doit également savoir distinguer une action d'observation d'une action modificatrice.

## 1.1 Compétences attendues

À la fin de ce cours, vous devrez être capable de :

- Gérer les comptes locaux et les groupes.
- Comprendre les permissions Unix, les ACL et l'umask.
- Diagnostiquer les processus et les consommations de ressources.
- Administrer les services avec systemd.
- Consulter et filtrer les journaux du système.
- Examiner les disques, les partitions et les systèmes de fichiers.
- Comprendre les points de montage et les entrées de `/etc/fstab`.
- Construire une stratégie de sauvegarde et vérifier une restauration.
- Diagnostiquer les interfaces, routes et sockets réseau.
- Administrer des connexions SSH en limitant les risques.
- Comprendre le rôle d'un pare-feu et les précautions nécessaires à sa configuration.
- Maintenir le système à jour avec son gestionnaire de paquets.
- Planifier des tâches avec cron ou des timers systemd.
- Écrire des scripts Bash adaptés à des tâches d'administration.
- Diagnostiquer les problèmes de CPU, mémoire, stockage et réseau.
- Appliquer une méthode de résolution d'incidents.
- Documenter les modifications et vérifier leurs conséquences.

## 1.2 Ce qui change par rapport au niveau débutant

| Niveau débutant | Niveau intermédiaire |
|---|---|
| Exécuter une commande | Choisir la commande adaptée à un diagnostic |
| Créer un fichier | Comprendre les permissions et les métadonnées du fichier |
| Utiliser `ps` | Analyser les processus et les ressources consommées |
| Consulter un journal | Filtrer les journaux et établir une chronologie |
| Utiliser `ip addr` | Relier les interfaces, les routes et les tests de connectivité |
| Écrire quelques commandes dans un script | Vérifier les entrées, les erreurs et les codes de retour |
| Copier des fichiers | Préparer des sauvegardes et tester leur restauration |
| Utiliser `sudo` | Limiter les privilèges et vérifier les conséquences d'une action |

## 1.3 Les principes d'administration à adopter

Un bon administrateur ne commence pas par modifier le système. Il commence par l'observer.

La méthode générale est la suivante :

```text
+------------------------------------------------+
|              INCIDENT OU BESOIN                |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 1. RECUEILLIR LES INFORMATIONS                  |
| Etat, messages, historique, contexte           |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 2. IDENTIFIER LA CAUSE PROBABLE                |
| Service, disque, permissions, reseau, etc.     |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 3. EVALUER LES RISQUES                          |
| Impact, disponibilite, donnees, acces distant   |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 4. PREPARER UNE CORRECTION                      |
| Sauvegarde, changement minimal, retour arriere  |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 5. APPLIQUER LE CHANGEMENT                      |
| Une modification maitrisee a la fois            |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 6. VERIFIER                                      |
| Tests, journaux, ressources, service             |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
| 7. DOCUMENTER                                   |
| Cause, correction, resultat, suivi               |
+------------------------------------------------+
```

Cette méthode permet de réduire les changements inutiles, de faciliter les diagnostics et de rendre les interventions reproductibles.

## 1.4 Précautions pour les travaux pratiques

Utilisez de préférence une machine virtuelle avec un instantané initial.

Les exercices concernant les services, le pare-feu et le stockage peuvent modifier le fonctionnement du système.

En particulier :

- N'effectuez pas les exercices sur un serveur de production.
- Ne formatez jamais un disque sans identifier précisément le périphérique.
- Ne modifiez pas `/etc/fstab` sans préparer une procédure de retour arrière.
- Ne redémarrez pas arbitrairement le réseau d'une machine administrée par SSH.
- Ne désactivez pas l'authentification existante avant d'avoir testé une méthode de connexion de remplacement.
- N'exécutez pas un script d'administration sans avoir vérifié son contenu.


# 2. Architecture opérationnelle d'un serveur Linux

L'administration efficace suppose de comprendre les relations entre le noyau, les processus, les services, les fichiers de configuration, le stockage et le réseau.

## 2.1 Représentation opérationnelle

```text
+------------------------------------------------------+
|                  UTILISATEURS                        |
|       SSH | Terminal local | Applications            |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
|                  COUCHE UTILISATEUR                  |
|                                                      |
| Bash | Outils systeme | Services | Applications      |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
|                     SYSTEMD                          |
|                                                      |
| Demarrage | Unites | Services | Timers | Journal      |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
|                    NOYAU LINUX                       |
|                                                      |
| Processus | Memoire | Reseau | VFS | Pilotes          |
+------------------------------------------------------+
            |                      |
            v                      v
+----------------------+ +-----------------------------+
| Stockage             | | Reseau                      |
| Disques, FS, volumes | | Interfaces, routes, sockets |
+----------------------+ +-----------------------------+
```

Ce schéma est conceptuel. systemd est un gestionnaire de systèmes et de services utilisé par de nombreuses distributions, mais ce n'est pas le seul système d'initialisation possible.

Le noyau gère les ressources, tandis que les outils et services fonctionnent dans l'environnement utilisateur.

## 2.2 Différencier un processus, un service et une unité systemd

Un **processus** est une instance d'un programme en cours d'exécution.

Un **service** est une fonction fournie par un programme ou un ensemble de programmes. Un serveur Web, par exemple, peut fournir un service HTTP.

Une **unité systemd** est une entité gérée par systemd. Une unité peut représenter un service, un point de montage, un timer, une socket ou un autre objet.

Exemple :

```text
Service HTTP
    |
    +-- Programme : serveur Web
    |
    +-- Processus : instance en execution
    |
    +-- Unite systemd : apache2.service ou nginx.service
```

Le nom de l'unité dépend du logiciel installé.

Un service peut être inactif tout en étant correctement installé. Inversement, un programme peut être lancé manuellement sans qu'une unité systemd correspondante soit active.

Il est donc nécessaire de distinguer :

- La présence du programme.
- L'existence de l'unité.
- Son état actuel.
- Son activation au démarrage.
- La disponibilité effective du service pour ses clients.

## 2.3 Identifier la distribution

Avant d'exécuter des commandes spécifiques à une distribution, identifiez l'environnement.

```bash
cat /etc/os-release
```

Cette commande affiche généralement des informations telles que l'identifiant de la distribution et sa version.

Pour examiner le noyau :

```bash
uname -r
```

Pour obtenir l'architecture de la machine :

```bash
uname -m
```

Pour examiner la durée de fonctionnement et la charge :

```bash
uptime
```

Ces commandes sont essentiellement des outils d'observation. Elles ne modifient pas la configuration du système.

## 2.4 Identifier les ressources principales

Pour examiner rapidement le CPU et la mémoire :

```bash
lscpu
```

Cette commande présente des informations sur l'architecture du processeur.

```bash
free -h
```

Elle affiche une synthèse de la mémoire et de la zone d'échange, avec des tailles lisibles.

```bash
lsblk
```

Cette commande présente les périphériques de stockage en mode bloc et leurs relations.

```bash
ip addr
```

Elle affiche les interfaces réseau et leurs adresses.

### Synthèse des outils d'observation

```text
lscpu      -> processeur et architecture
free -h    -> memoire et swap
lsblk      -> peripheriques de stockage
df -h      -> espace des systemes de fichiers
ip addr    -> interfaces et adresses
ip route   -> table de routage
uptime     -> duree de fonctionnement et charge
```

Il est important de ne pas confondre `lsblk` et `df`.

`lsblk` présente les périphériques de stockage et leur organisation. `df` présente l'utilisation de l'espace des systèmes de fichiers montés.

Un périphérique peut exister sans contenir de système de fichiers monté. Dans ce cas, il peut apparaître dans `lsblk` sans être associé à une ligne habituelle dans `df`.

## 2.5 Comprendre la notion d'état

L'administration exige de distinguer plusieurs états.

Pour un service, on peut examiner son état courant et son activation au démarrage.

Pour un disque, on examine son identité, les partitions éventuelles, le système de fichiers et son point de montage.

Pour une interface réseau, on examine son état administratif, son état de liaison, ses adresses et les routes associées.

Exemple de raisonnement :

```text
Un client ne peut pas acceder a une application Web
                      |
                      v
Le service Web est-il actif ?
          |                     |
         Non                   Oui
          |                     |
          v                     v
Examiner le service       Le port est-il en ecoute ?
                                |
                      +---------+---------+
                      |                   |
                     Non                 Oui
                      |                   |
                      v                   v
              Examiner le serveur    Examiner le reseau,
              et sa configuration   le pare-feu et le client
```

Cette démarche ne couvre pas tous les scénarios, mais elle montre pourquoi un diagnostic doit être progressif.


# 3. Gestion avancée des utilisateurs et des groupes

La gestion des comptes est fondamentale pour le contrôle d'accès.

L'objectif ne consiste pas seulement à créer des utilisateurs, mais à organiser les responsabilités, les groupes, les permissions et les privilèges administratifs.

## 3.1 Comprendre les identifiants

Linux associe les utilisateurs et les groupes à des identifiants numériques.

- UID : identifiant utilisateur.
- GID : identifiant de groupe.

Afficher les informations du compte courant :

```bash
id
```

Afficher l'utilisateur effectif :

```bash
whoami
```

Afficher les groupes associés au compte :

```bash
groups
```

Les noms servent à rendre les informations lisibles. Les identifiants numériques sont utilisés par les mécanismes du système.

## 3.2 Le rôle des groupes

Les groupes permettent d'attribuer un ensemble de droits à plusieurs utilisateurs sans répéter les mêmes réglages individuels.

Exemple :

```text
                    GROUPE support
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
           Alice        Bob         Chlo
             |           |           |
             +-----------+-----------+
                         |
                         v
              Documents partages
```

Cet exemple représente une organisation conceptuelle. Les accès réels dépendront des permissions et des autres contrôles appliqués aux fichiers.

## 3.3 Créer un groupe

Dans un environnement de test, avec les privilèges nécessaires :

```bash
sudo groupadd support
```

Cette commande demande la création du groupe `support`.

Avant de la lancer, vérifiez si le groupe existe déjà. Le comportement exact en cas de doublon dépend des options et de l'outil utilisé.

Pour examiner les informations du groupe :

```bash
getent group support
```

Cette commande demande les informations du groupe au service de résolution de comptes configuré.

## 3.4 Créer un utilisateur

Sur les systèmes qui fournissent `useradd`, la syntaxe générale comprend des options permettant de définir le répertoire personnel, le Shell et les groupes.

Exemple de création d'un compte de test :

```bash
sudo useradd -m -s /bin/bash formation
```

Interprétation :

- `-m` : demande la création du répertoire personnel.
- `-s /bin/bash` : définit Bash comme Shell de connexion.
- `formation` : nom du compte.

La présence de `/bin/bash` doit être vérifiée sur le système concerné.

Définir un mot de passe interactif :

```bash
sudo passwd formation
```

Choisissez un mot de passe adapté à la politique de sécurité de votre environnement de test.

La création effective du compte dépend des règles de la distribution et des fichiers existants.

## 3.5 Ajouter un utilisateur à un groupe

Pour ajouter le compte `formation` au groupe `support` en tant que groupe supplémentaire :

```bash
sudo usermod -aG support formation
```

La combinaison `-aG` est importante :

- `-G` spécifie les groupes supplémentaires.
- `-a` demande d'ajouter ces groupes à la liste existante.

Sans `-a`, une utilisation incorrecte de `-G` peut remplacer la liste des groupes supplémentaires et retirer des appartenances existantes.

Vérifiez le résultat :

```bash
id formation
```

Les nouveaux groupes peuvent ne pas apparaître immédiatement dans une session déjà ouverte par cet utilisateur. Une nouvelle session peut être nécessaire.

## 3.6 Vérifier les informations d'un compte

```bash
getent passwd formation
```

Cette commande examine les informations du compte via le mécanisme de résolution configuré.

Pour vérifier le répertoire personnel :

```bash
ls -ld /home/formation
```

Le chemin réel peut différer si le compte a été créé avec une configuration personnalisée.

## 3.7 Verrouiller ou déverrouiller un compte

Sur les distributions qui utilisent les outils shadow habituels :

```bash
sudo passwd -l formation
```

Cette commande verrouille l'authentification par mot de passe selon le fonctionnement du système.

Pour déverrouiller cette méthode d'authentification :

```bash
sudo passwd -u formation
```

Attention : verrouiller le mot de passe ne désactive pas nécessairement toutes les formes de connexion. Des clés SSH, des mécanismes centralisés ou d'autres méthodes d'authentification peuvent intervenir.

Pour suspendre un compte, évaluez l'ensemble des moyens d'accès et les besoins de conservation des données.

## 3.8 Supprimer un utilisateur : précautions

La commande :

```bash
sudo userdel formation
```

demande la suppression du compte utilisateur.

L'option `-r` peut aussi demander la suppression du répertoire personnel et du courrier local :

```bash
sudo userdel -r formation
```

Cette deuxième commande est plus destructive.

Avant toute suppression, vérifiez :

```bash
id formation
sudo find /home/formation -maxdepth 2 -print
```

Le compte peut posséder des fichiers ailleurs que dans son répertoire personnel, des tâches planifiées, des processus ou des responsabilités sur des services.

**Règle professionnelle :** la suppression d'un compte doit être précédée d'une vérification de ses dépendances et des besoins de conservation des données.

## 3.9 Limiter les privilèges administratifs

Le compte superutilisateur `root` possède des pouvoirs très étendus.

L'utilisation de `sudo` permet de déléguer certaines opérations à des comptes autorisés.

Pour connaître les règles applicables à l'utilisateur courant :

```bash
sudo -l
```

Cette commande affiche les opérations autorisées selon la configuration.

Ne donnez pas systématiquement les privilèges administratifs complets à chaque utilisateur.

Privilégiez une délégation limitée aux besoins réels, notamment dans les environnements professionnels.

Les règles de `sudo` doivent être modifiées avec précaution, idéalement avec `visudo`, qui aide à vérifier la syntaxe.

```bash
sudo visudo
```

N'ajoutez pas de règle donnant des droits illimités simplement pour faire disparaître une erreur de permission.

## 3.10 Atelier : créer un espace partagé

Objectif : préparer un répertoire partagé par les membres d'un groupe.

Dans un environnement de test, avec un groupe `support` déjà créé :

```bash
sudo mkdir -p /srv/support
sudo chown root:support /srv/support
sudo chmod 2770 /srv/support
```

Le mode `2770` sera détaillé dans le chapitre sur les permissions avancées.

Dans les conditions habituelles, il permet :

- Au propriétaire `root` de disposer des permissions `rwx`.
- Au groupe `support` de disposer des permissions `rwx`.
- Aux autres utilisateurs de ne disposer d'aucune permission classique.
- Au bit setgid sur le répertoire de favoriser l'héritage du groupe du répertoire pour les nouveaux éléments créés à l'intérieur.

Vérifiez :

```bash
ls -ld /srv/support
```

Cette opération modifie le système. Réalisez-la uniquement dans une machine de test et vérifiez qu'aucune donnée existante n'est affectée.


# 4. Permissions avancées, ACL et umask

Le modèle classique des permissions ne couvre pas tous les besoins d'un serveur.

Les ACL permettent d'accorder des droits supplémentaires à certains utilisateurs ou groupes. L'umask influence les permissions initiales des nouveaux fichiers et répertoires.

## 4.1 Rappel des permissions classiques

Les permissions classiques sont :

```text
r = lecture
w = ecriture
x = execution ou traversee, selon le type
```

Les catégories sont :

```text
u = proprietaire
g = groupe
o = autres
```

Exemple :

```text
-rwxr-x---
```

Interprétation :

- Propriétaire : lecture, écriture et exécution.
- Groupe : lecture et exécution.
- Autres : aucune permission classique.

## 4.2 Comprendre le bit setgid sur un répertoire

Le bit setgid, noté `2` dans la notation numérique des permissions, peut être appliqué à un répertoire.

Exemple :

```bash
sudo chmod 2770 /srv/support
```

L'objectif est notamment de faciliter le partage des fichiers en favorisant l'héritage du groupe associé au répertoire pour les nouvelles entrées.

Schéma :

```text
+----------------------------------+
| /srv/support                     |
| Groupe : support                 |
| Permissions : 2770                |
+----------------------------------+
                |
                v
+----------------------------------+
| Nouveau fichier cree dans le     |
| repertoire partage               |
+----------------------------------+
                |
                v
+----------------------------------+
| Le groupe support est generalement|
| herite sur la nouvelle entree    |
+----------------------------------+
```

L'héritage des permissions d'accès reste influencé par l'umask, les ACL par défaut et les opérations réalisées par le programme créateur.

Le bit setgid ne garantit donc pas à lui seul que tous les fichiers créés seront modifiables par tous les membres du groupe.

## 4.3 Comprendre le sticky bit

Le sticky bit est couramment utilisé sur des répertoires partagés tels que `/tmp`.

Exemple :

```bash
ls -ld /tmp
```

Les permissions peuvent contenir un `t` à la fin :

```text
drwxrwxrwt
```

Dans un répertoire partagé avec le sticky bit, la suppression ou le renommage des entrées est normalement limité par des règles particulières, notamment en fonction du propriétaire de l'entrée et du répertoire.

Cela réduit le risque qu'un utilisateur supprime arbitrairement les fichiers d'un autre utilisateur dans un répertoire accessible à tous.

Ne modifiez pas les permissions de `/tmp` pendant ce cours.

## 4.4 Comprendre l'umask

L'umask influence les permissions de création des nouveaux fichiers et répertoires.

Afficher l'umask :

```bash
umask
```

Une valeur courante est :

```text
0022
```

L'umask retire des permissions aux permissions de base prévues par le programme créateur.

Les bases habituelles sont :

- Fichiers ordinaires : `666`.
- Répertoires : `777`.

Le bit d'exécution n'est donc normalement pas automatiquement accordé aux fichiers ordinaires créés de cette façon.

### Exemple avec `umask 022`

Pour un fichier ordinaire :

```text
Base habituelle : 666
Umask           : 022
Resultat        : 644
```

Pour un répertoire :

```text
Base habituelle : 777
Umask           : 022
Resultat        : 755
```

Cette représentation illustre le comportement courant. Le résultat final dépend aussi du programme créateur et d'autres mécanismes de permission.

## 4.5 Modifier temporairement l'umask

Dans une session Bash :

```bash
umask 027
```

Les nouvelles créations seront soumises à ce masque dans le contexte concerné.

Avec une base habituelle de `666`, le résultat classique pour un fichier devient `640`.

Avec une base habituelle de `777`, le résultat classique pour un répertoire devient `750`.

Pour examiner le contexte, créez des éléments de test :

```bash
touch test-fichier.txt
mkdir test-repertoire
ls -l test-fichier.txt
ls -ld test-repertoire
```

Puis comparez avec un autre umask :

```bash
umask 022
touch autre-fichier.txt
mkdir autre-repertoire
ls -l autre-fichier.txt
ls -ld autre-repertoire
```

Ne changez pas l'umask global d'un serveur sans comprendre les conséquences pour les applications qui y fonctionnent.

## 4.6 Comprendre les ACL

Les listes de contrôle d'accès, ou ACL, permettent de définir des permissions pour des utilisateurs et groupes supplémentaires au-delà du triplet classique propriétaire, groupe et autres.

Exemple conceptuel :

```text
Fichier : rapport.txt
|
+-- Proprietaire : Alice       -> rw-
|
+-- Groupe       : support     -> r--
|
+-- Autres                    -> ---
|
+-- ACL utilisateur : Bob      -> rw-
```

Dans ce cas, une ACL peut donner des droits à Bob même si celui-ci n'est pas le propriétaire du fichier ni membre du groupe associé.

L'application effective des ACL doit toutefois tenir compte du masque ACL, des permissions des répertoires parents et des autres mécanismes de sécurité.

## 4.7 Examiner les ACL

Selon la distribution, les outils `getfacl` et `setfacl` peuvent être disponibles dans un paquet spécifique.

Examiner les ACL :

```bash
getfacl rapport.txt
```

Le résultat affiche les permissions classiques et, s'il y en a, les entrées ACL.

Si la commande est absente, identifiez le gestionnaire de paquets et le paquet qui fournit l'outil dans votre environnement.

## 4.8 Ajouter une ACL

Dans un répertoire de test contenant `rapport.txt` :

```bash
setfacl -m u:bob:rw- rapport.txt
```

Cette commande demande une ACL accordant la lecture et l'écriture à l'utilisateur `bob`.

L'utilisateur doit exister, et le système de fichiers ainsi que les outils doivent prendre en charge l'opération.

Vérifiez le résultat :

```bash
getfacl rapport.txt
```

Il est essentiel de comprendre les permissions effectives, notamment le masque ACL, avant de déployer ce mécanisme dans un système important.

## 4.9 Supprimer une ACL spécifique

```bash
setfacl -x u:bob rapport.txt
```

Cette commande retire l'entrée ACL correspondant à l'utilisateur `bob`, si elle existe.

Pour retirer les ACL étendues d'un fichier, avec les précautions nécessaires :

```bash
setfacl -b rapport.txt
```

Cette dernière opération supprime les ACL étendues associées au fichier. Elle doit être utilisée uniquement si cette suppression est intentionnelle.

## 4.10 ACL par défaut sur un répertoire

Les ACL par défaut servent à définir une base de permissions pour les nouvelles entrées dans un répertoire.

Exemple, dans un espace de test :

```bash
setfacl -m d:g:support:rwx /srv/support
```

Cette commande demande une ACL par défaut accordant des permissions au groupe `support` pour les nouveaux éléments concernés.

Le résultat effectif dépend aussi de l'umask, des permissions demandées par le programme créateur et du masque ACL.

Vérifiez :

```bash
getfacl /srv/support
```

Testez les résultats sur des fichiers créés spécialement pour l'exercice.

## 4.11 Comparer les mécanismes

| Mécanisme | Objectif |
|---|---|
| Permissions classiques | Définir les droits du propriétaire, du groupe et des autres |
| Umask | Réduire les permissions initiales lors de la création |
| Setgid sur un répertoire | Favoriser l'héritage du groupe du répertoire |
| Sticky bit | Limiter certaines suppressions et certains renommages dans un répertoire partagé |
| ACL | Définir des permissions supplémentaires pour des utilisateurs ou groupes |

Ces mécanismes sont complémentaires et ne doivent pas être confondus.

## 4.12 Atelier de permissions

Sur un système de test :

1. Créez un répertoire de travail.
2. Créez deux comptes de test si cela est possible.
3. Créez un groupe partagé.
4. Affectez le répertoire au groupe.
5. Appliquez le mode `2770`.
6. Ajoutez une ACL à un fichier.
7. Vérifiez le résultat avec `ls -l` et `getfacl`.
8. Créez un fichier avec le compte approprié.
9. Vérifiez ses permissions.
10. Retirez l'ACL d'essai et comparez les résultats.

La compétence attendue n'est pas de mémoriser les commandes, mais d'expliquer pourquoi un accès est accordé ou refusé.


# 5. Administration des processus et des ressources

L'administrateur doit identifier les programmes en cours d'exécution, comprendre leur consommation de ressources et décider quand une intervention est nécessaire.

## 5.1 Afficher les processus

```bash
ps -ef
```

Affiche une liste de processus selon le format sélectionné.

Autre forme courante :

```bash
ps aux
```

Les options utilisent des conventions différentes.

Pour rechercher un programme :

```bash
pgrep -a nginx
```

La commande affiche les processus correspondant au motif recherché lorsqu'elle est disponible et que des correspondances existent.

## 5.2 Comprendre les informations de processus

Les colonnes peuvent comprendre :

- PID : identifiant du processus.
- PPID : identifiant du processus parent.
- USER : utilisateur associé au processus.
- %CPU : consommation du processeur dans le format concerné.
- %MEM : proportion de mémoire dans le format concerné.
- STAT : état du processus.
- COMMAND : commande ou ligne de commande.

La signification précise de certains champs dépend de l'outil et du format utilisé.

## 5.3 Les états de processus

La sortie de `ps` peut inclure des lettres d'état.

Exemples courants :

- `R` : en exécution ou prêt à s'exécuter.
- `S` : attente interruptible.
- `D` : attente généralement non interruptible, souvent liée à une opération du noyau.
- `T` : processus arrêté ou tracé.
- `Z` : processus terminé dont l'entrée de processus reste présente jusqu'à sa collecte par le parent.

Un processus en état `D` n'est pas nécessairement un processus malveillant ou bloqué de manière irrécupérable. Il peut être en attente d'une ressource ou d'une opération.

Des processus `Z` persistants peuvent indiquer un problème de gestion des enfants par un processus parent. Il faut examiner la relation entre les processus plutôt que tenter de tuer directement le zombie.

## 5.4 Observer les ressources avec `top`

```bash
top
```

L'outil permet d'examiner régulièrement les processus et certaines statistiques globales.

Les indicateurs peuvent inclure :

- La charge système.
- L'utilisation du CPU.
- La mémoire.
- Le swap.
- Les processus actifs.
- Les identifiants et les temps CPU des processus.

Les touches disponibles dépendent de l'outil et de sa version. `q` permet généralement de quitter.

## 5.5 Utiliser `htop`

Si `htop` est installé :

```bash
htop
```

Il fournit une vue interactive des processus et des ressources.

Son absence ne signifie pas que le système est défaillant. Il s'agit d'un outil supplémentaire, qui peut être installé avec le gestionnaire de paquets approprié si nécessaire.

## 5.6 Arrêter un processus proprement

Pour demander à un processus de terminer :

```bash
kill -TERM PID
```

Remplacez `PID` par un identifiant réel après l'avoir vérifié.

Le signal `TERM` laisse au processus la possibilité de gérer son arrêt.

Si un processus ne réagit pas, examinez d'abord :

- Son identité.
- Son état.
- Ses journaux.
- Les ressources dont il dépend.
- L'éventualité d'un blocage du stockage ou du réseau.

Le signal `KILL` est un dernier recours, car il ne permet pas au programme d'intercepter la demande pour effectuer son nettoyage habituel.

## 5.7 Priorité et valeur nice

Linux utilise des mécanismes de planification pour répartir le temps CPU.

La valeur nice influence la priorité relative d'un processus ordinaire.

Examiner les informations de priorité :

```bash
ps -eo pid,ni,pri,comm
```

La colonne `NI` représente la valeur nice dans ce format.

En règle générale, les valeurs nice les plus élevées correspondent à une priorité CPU moins favorable pour les processus ordinaires.

## 5.8 Lancer un programme avec une priorité adaptée

Exemple :

```bash
nice -n 10 commande
```

Cette forme demande de lancer `commande` avec une valeur nice de `10`, selon les possibilités de l'environnement.

Elle peut être utile pour lancer une tâche de calcul non urgente.

Les valeurs disponibles et les permissions permettant de modifier les priorités dépendent de la configuration.

## 5.9 Modifier la priorité d'un processus existant

```bash
renice 10 -p PID
```

Cette commande demande d'ajuster la valeur nice du processus désigné.

La permission de modifier une priorité dépend de l'utilisateur effectif, de la valeur demandée et des règles du système.

Ne modifiez pas les priorités d'un service critique sans comprendre l'impact.

## 5.10 Repérer une consommation CPU élevée

```bash
ps -eo pid,ppid,user,%cpu,%mem,stat,comm --sort=-%cpu | head
```

Cette commande fournit un aperçu des processus classés par consommation CPU dans le format utilisé.

Elle permet de faire ressortir rapidement certaines consommations élevées, mais un résultat instantané ne suffit pas toujours à conclure qu'il existe un problème.

Une tâche peut consommer temporairement du CPU de manière parfaitement normale.

Pour un diagnostic, observez la durée, les variations et les conséquences sur les applications.

## 5.11 Repérer une consommation mémoire élevée

```bash
ps -eo pid,ppid,user,%cpu,%mem,rss,comm --sort=-%mem | head
```

La commande présente les processus classés par proportion de mémoire dans le format sélectionné.

La colonne `RSS` représente une approximation de la mémoire résidente du processus, en unités dépendant du format indiqué par l'outil.

La mémoire partagée entre processus et les mécanismes du noyau rendent l'interprétation plus complexe qu'une addition naïve des valeurs.

## 5.12 Comprendre la charge système

```bash
uptime
```

Cette commande affiche notamment la charge moyenne sur plusieurs périodes.

La charge système n'est pas un pourcentage CPU. Elle reflète le nombre de tâches dans certains états d'exécution ou d'attente.

Son interprétation dépend du nombre de processeurs logiques, du type de charge et de la présence éventuelle de tâches en attente non interruptible.

Une charge élevée peut résulter :

- D'une forte activité CPU.
- D'une attente liée au stockage.
- D'un grand nombre de tâches concurrentes.
- D'une combinaison de plusieurs facteurs.

Il faut corréler cette information avec les autres outils.

## 5.13 Identifier les limites de ressources

Linux et ses distributions proposent plusieurs mécanismes de limitation des ressources.

Par exemple, les limites de processus ou de fichiers ouverts peuvent être examinées avec :

```bash
ulimit -a
```

Cette commande affiche certaines limites associées au Shell courant.

Les limites des services systemd peuvent également dépendre des propriétés configurées pour leur unité.

Il ne faut pas modifier ces limites arbitrairement : augmenter une limite ne résout pas nécessairement la cause sous-jacente d'un problème.


# 6. Gestion des services avec systemd

systemd est utilisé par de nombreuses distributions Linux modernes pour gérer le démarrage du système et les unités.

Cette partie est essentielle pour l'exploitation d'un serveur.

## 6.1 Qu'est-ce qu'un service systemd ?

Un service systemd est souvent représenté par une unité portant l'extension `.service`.

Exemples possibles :

```text
ssh.service
nginx.service
apache2.service
cron.service
```

Les noms exacts dépendent de la distribution et des logiciels installés.

Une unité possède une configuration décrivant comment la gérer et peut comporter des dépendances avec d'autres unités.

## 6.2 Examiner l'état d'un service

```bash
systemctl status ssh
```

Sur certains systèmes, le service SSH peut s'appeler `sshd`.

La commande peut afficher :

- L'état courant.
- Des informations sur le processus principal.
- Le PID principal.
- Des messages récents.
- Des indications concernant les dépendances ou l'unité.

Le résultat dépend du service et de la configuration.

## 6.3 Distinguer l'état courant et l'activation au démarrage

Une unité peut être active maintenant sans être configurée pour démarrer automatiquement au prochain démarrage.

À l'inverse, elle peut être activée pour démarrer plus tard, mais être actuellement inactive.

Examiner l'état courant :

```bash
systemctl is-active ssh
```

Examiner si l'unité est activée :

```bash
systemctl is-enabled ssh
```

Ces deux commandes répondent à des questions différentes.

## 6.4 Démarrer un service

```bash
sudo systemctl start nginx
```

Demande le démarrage de l'unité `nginx`.

Si le service n'est pas installé ou si son unité porte un autre nom, la commande ne fonctionnera pas comme prévu.

## 6.5 Arrêter un service

```bash
sudo systemctl stop nginx
```

Demande l'arrêt du service.

Cette action peut interrompre une application utilisée par des clients. Vérifiez les conséquences avant de l'exécuter sur un serveur opérationnel.

## 6.6 Redémarrer un service

```bash
sudo systemctl restart nginx
```

Demande un redémarrage de l'unité.

Cette action peut entraîner une interruption. Elle ne doit pas être utilisée systématiquement comme méthode de dépannage.

Une bonne pratique consiste à :

1. Examiner les journaux.
2. Identifier le problème.
3. Vérifier la configuration.
4. Appliquer la modification nécessaire.
5. Valider la configuration si l'application le permet.
6. Effectuer l'action de gestion adaptée.
7. Vérifier le résultat.

## 6.7 Recharger une configuration

Certaines applications prennent en charge un rechargement de configuration sans redémarrage complet du processus.

Avec systemd, une commande courante est :

```bash
sudo systemctl reload nginx
```

Elle ne fonctionne que si l'unité et l'application prennent en charge cette opération.

Un rechargement systemd ne garantit pas à lui seul que la configuration applicative est valide. Il faut consulter la documentation du service.

## 6.8 Activer un service au démarrage

```bash
sudo systemctl enable nginx
```

Cette commande configure normalement l'activation de l'unité lors des démarrages correspondants.

Pour activer et démarrer immédiatement :

```bash
sudo systemctl enable --now nginx
```

Vérifiez le résultat avec :

```bash
systemctl status nginx
systemctl is-enabled nginx
```

## 6.9 Désactiver l'activation automatique

```bash
sudo systemctl disable nginx
```

Cette commande retire l'activation automatique gérée par l'unité.

Elle ne garantit pas l'arrêt du service actuellement actif.

Pour demander les deux opérations :

```bash
sudo systemctl disable --now nginx
```

N'effectuez cette opération que si vous comprenez l'impact sur les applications qui utilisent le service.

## 6.10 Examiner les unités en échec

```bash
systemctl --failed
```

Cette commande donne un aperçu des unités signalées en échec.

Une unité en échec n'implique pas nécessairement une panne globale. Il faut identifier son rôle et les conséquences de son état.

Pour examiner les unités de service chargées :

```bash
systemctl list-units --type=service
```

Pour rechercher les unités installées correspondant à un motif :

```bash
systemctl list-unit-files
```

Ces sorties peuvent être longues. Utilisez une recherche ciblée lorsque cela est nécessaire.

## 6.11 Comprendre les dépendances

Un service peut dépendre d'autres unités.

Par exemple, une application peut avoir besoin du réseau ou d'un montage de stockage avant de fonctionner correctement.

La présence d'une dépendance dans la configuration ne garantit pas que le service applicatif est prêt à accepter des connexions. Il faut aussi vérifier son état réel et son comportement.

Pour examiner une unité :

```bash
systemctl cat nginx
```

Cette commande affiche l'unité et les éventuels éléments de configuration associés que systemd peut présenter.

## 6.12 Modifier une unité proprement

Les fichiers fournis par les paquets ne devraient pas être modifiés directement sans justification.

Lorsqu'une personnalisation est nécessaire, un mécanisme de surcharge peut permettre d'ajouter des modifications séparées.

```bash
sudo systemctl edit nginx
```

Cette commande ouvre un éditeur pour créer ou modifier une surcharge de l'unité.

La structure exacte de la surcharge dépend de la modification envisagée. Ne copiez pas une directive sans comprendre son effet.

Après une modification de configuration d'unité, systemd peut nécessiter :

```bash
sudo systemctl daemon-reload
```

Cette commande demande à systemd de relire les définitions des unités.

Elle ne redémarre pas automatiquement tous les services. Les mesures supplémentaires dépendent du changement réalisé.

## 6.13 Atelier : diagnostiquer un service

Dans un environnement de test possédant un service connu :

1. Examinez son état avec `systemctl status`.
2. Vérifiez son activation avec `systemctl is-enabled`.
3. Consultez ses journaux avec `journalctl`.
4. Vérifiez les ports en écoute si c'est un service réseau.
5. Examinez sa configuration.
6. Identifiez une modification ou un test sans risque.
7. Effectuez une correction uniquement si nécessaire.
8. Vérifiez à nouveau le service et son comportement.

Le but n'est pas de redémarrer le service systématiquement, mais de comprendre la relation entre son état, ses journaux et son rôle.


# 7. Diagnostic et analyse des journaux

Un journal permet d'observer ce qui s'est passé dans le système ou dans une application.

Il sert notamment à établir une chronologie, identifier des erreurs et vérifier l'effet d'une modification.

## 7.1 Les journaux système

Selon la distribution et les services installés, les journaux peuvent être disponibles dans :

- Le journal géré par systemd.
- Des fichiers situés sous `/var/log/`.
- Les journaux propres à une application.
- Un système de journalisation centralisé.

Il ne faut pas supposer que toutes les distributions utilisent exactement le même mécanisme.

## 7.2 Utiliser `journalctl`

Afficher les messages du journal :

```bash
journalctl
```

Afficher les messages du démarrage courant :

```bash
journalctl -b
```

Afficher les dernières entrées du démarrage courant :

```bash
journalctl -b -n 50
```

Suivre les nouveaux messages :

```bash
journalctl -f
```

Quittez généralement le suivi avec `Ctrl+C`.

## 7.3 Examiner les messages d'un service

```bash
journalctl -u nginx
```

Cette commande filtre les messages associés à l'unité `nginx`, lorsque l'unité et ses journaux sont disponibles.

Pour consulter les entrées du démarrage courant :

```bash
journalctl -b -u nginx
```

Pour limiter le nombre d'entrées :

```bash
journalctl -u nginx -n 100
```

Le résultat dépend du service, de sa configuration et des permissions.

## 7.4 Filtrer par période

Les options exactes dépendent de la version de journalctl, mais des filtres courants permettent de cibler une période.

Exemple :

```bash
journalctl --since "1 hour ago"
```

Affiche les messages depuis environ une heure avant le moment de la commande.

Autre exemple :

```bash
journalctl --since "2026-10-24 08:00:00"
```

La date est illustrative. Utilisez la période réelle correspondant à l'incident et tenez compte du fuseau horaire du système.

## 7.5 Comprendre la priorité des messages

Les journaux peuvent comporter des niveaux de priorité.

Les niveaux courants sont :

| Niveau | Signification générale |
|---|---|
| `emerg` | Situation d'urgence |
| `alert` | Action immédiate requise |
| `crit` | Condition critique |
| `err` | Erreur |
| `warning` | Avertissement |
| `notice` | Événement notable |
| `info` | Information |
| `debug` | Informations de débogage |

Ces niveaux expriment une classification des messages. Un message d'erreur ne signifie pas automatiquement que toute la machine est inutilisable.

## 7.6 Filtrer les erreurs et avertissements

```bash
journalctl -p warning
```

Cette forme affiche les messages correspondant à la priorité choisie et aux niveaux plus prioritaires, selon les règles de journalctl.

Pour examiner le contexte, ne vous limitez pas à une seule ligne. Les messages qui précèdent ou suivent peuvent expliquer l'origine du problème.

## 7.7 Examiner les fichiers sous `/var/log`

```bash
ls -lah /var/log
```

Certains fichiers peuvent être consultés avec `less` :

```bash
less /var/log/syslog
```

ou :

```bash
less /var/log/messages
```

Le fichier disponible dépend de la distribution et de la configuration.

Pour rechercher les lignes associées à un terme :

```bash
grep -i "error" /var/log/exemple.log
```

Remplacez le chemin par un fichier de journal réellement présent.

## 7.8 Comprendre la rotation des journaux

Les journaux peuvent grossir avec le temps.

La rotation permet notamment :

- De créer un nouveau fichier de journal.
- De conserver d'anciennes versions.
- De compresser des fichiers anciens.
- De limiter l'espace utilisé.
- D'adapter la conservation à la politique de l'organisation.

Un outil courant dans de nombreuses distributions est `logrotate`.

Examiner sa documentation :

```bash
man logrotate
```

La rotation exacte dépend des fichiers de configuration installés. Ne modifiez pas les règles globales au hasard.

## 7.9 Construire une chronologie d'incident

Supposons qu'un service Web ne réponde plus.

Procédez de manière structurée :

```text
08:00  Le service fonctionne normalement
  |
  v
08:10  Une modification de configuration est appliquee
  |
  v
08:12  Les clients signalent une indisponibilite
  |
  v
08:13  systemctl indique un echec
  |
  v
08:14  journalctl montre une erreur de configuration
  |
  v
08:20  La configuration est corrigee et validee
  |
  v
08:22  Le service redemarre et les tests reussissent
```

Cette chronologie est illustrative.

Pour construire une chronologie réelle, croisez :

- Les journaux du service.
- Les messages du système.
- Les changements de configuration.
- Les alertes de surveillance.
- Les tests effectués.
- Les témoignages ou rapports des utilisateurs.

Ne concluez pas à une cause uniquement parce qu'un message est proche dans le temps.


# 8. Gestion avancée du stockage et des systèmes de fichiers

Le stockage doit être administré avec rigueur. Une erreur de périphérique ou une mauvaise modification du montage peut rendre des données inaccessibles.

Ce chapitre présente les outils d'observation et les notions essentielles. Les opérations de partitionnement et de formatage doivent être réalisées uniquement sur des périphériques de test correctement identifiés.

## 8.1 Distinguer les notions

Un périphérique de stockage, une partition, un volume logique et un système de fichiers sont des éléments différents.

Un disque peut contenir plusieurs partitions.

Une partition peut contenir un système de fichiers.

Un volume logique LVM peut fournir un espace de stockage abstrait qui sera ensuite utilisé pour créer un système de fichiers.

Le système de fichiers est généralement monté dans l'arborescence Linux pour rendre son contenu accessible.

### Schéma de stockage simple

```text
+---------------------------+
| Disque                    |
| /dev/sdb                  |
+---------------------------+
             |
             v
+---------------------------+
| Partition                 |
| /dev/sdb1                 |
+---------------------------+
             |
             v
+---------------------------+
| Systeme de fichiers       |
| Exemple : ext4            |
+---------------------------+
             |
             v
+---------------------------+
| Point de montage          |
| /srv/donnees              |
+---------------------------+
             |
             v
+---------------------------+
| Fichiers et repertoires   |
+---------------------------+
```

Ce schéma est simplifié. Les volumes chiffrés, RAID, LVM, systèmes de fichiers réseau et autres configurations ajoutent des couches.

## 8.2 Lister les périphériques

```bash
lsblk
```

Pour afficher davantage de détails :

```bash
lsblk -f
```

Selon la configuration, la sortie peut inclure :

- Le nom du périphérique.
- La taille.
- Le type.
- Le système de fichiers.
- L'UUID.
- Le point de montage.

Les périphériques ne doivent jamais être identifiés uniquement à partir d'un nom mémorisé. Leur ordre et leurs noms peuvent changer.

## 8.3 Identifier un système de fichiers

```bash
blkid
```

Cette commande affiche des informations sur les périphériques de bloc et les identifiants connus.

L'accès à toutes les informations peut nécessiter des privilèges.

Pour interroger un périphérique précis identifié avec certitude :

```bash
sudo blkid /dev/sdb1
```

**Avertissement :** `/dev/sdb1` est un exemple. Ne l'utilisez pas sur votre système sans avoir vérifié qu'il désigne bien le périphérique de test voulu.

## 8.4 Examiner l'espace disponible avec `df`

```bash
df -h
```

Cette commande affiche l'utilisation de l'espace des systèmes de fichiers montés.

Colonnes courantes :

- Taille.
- Espace utilisé.
- Espace disponible.
- Pourcentage utilisé.
- Point de montage.

Pour examiner un chemin particulier :

```bash
df -h /srv
```

La commande indique l'espace du système de fichiers auquel ce chemin appartient.

## 8.5 Examiner l'espace utilisé avec `du`

```bash
du -sh /var/log
```

Cette commande estime l'espace utilisé par le répertoire indiqué.

Pour examiner les sous-répertoires immédiats :

```bash
du -h --max-depth=1 /var/log
```

Cette option est courante avec GNU `du`. D'autres versions peuvent utiliser une syntaxe différente.

Pour rechercher les répertoires les plus volumineux, procédez sur un chemin pertinent et analysez les résultats avant de supprimer quoi que ce soit.

## 8.6 Pourquoi `df` et `du` peuvent-ils donner des résultats différents ?

`df` examine l'espace utilisé et disponible du système de fichiers.

`du` estime l'espace associé aux fichiers et répertoires parcourus.

Ils peuvent différer, notamment dans les situations suivantes :

- Fichiers supprimés mais encore ouverts par des processus.
- Espaces de métadonnées du système de fichiers.
- Points de montage imbriqués.
- Restrictions de parcours.
- Fichiers creux ou particularités de comptabilisation.
- Différences entre la taille logique et les blocs réellement alloués.

Un écart ne signifie donc pas automatiquement que l'un des outils est incorrect.

### Diagnostic d'un système de fichiers presque plein

```text
df indique 98 % d'utilisation
            |
            v
Examiner le point de montage
            |
            v
Utiliser du pour reperer les dossiers volumineux
            |
            v
Examiner les journaux, caches et donnees
            |
            v
Identifier les donnees qui peuvent etre nettoyees
            |
            v
Verifier qu'aucun service ou fichier critique n'est affecte
            |
            v
Effectuer un nettoyage maitrise ou etendre le stockage
            |
            v
Verifier de nouveau df et le fonctionnement des services
```

Ne supprimez pas des journaux ou des fichiers en production sans comprendre les besoins de conservation et de diagnostic.

## 8.7 Comprendre les points de montage

Un point de montage est un répertoire dans lequel le contenu d'un système de fichiers est rendu accessible.

Pour afficher les systèmes de fichiers montés :

```bash
findmnt
```

Pour examiner le montage associé à un chemin :

```bash
findmnt /srv
```

Le résultat dépend de la structure de stockage.

Le répertoire utilisé comme point de montage doit être choisi de manière cohérente avec les besoins de l'application.

## 8.8 Monter un système de fichiers

Une commande de montage standard possède la forme :

```bash
sudo mount PERIPHERIQUE POINT_DE_MONTAGE
```

Exemple conceptuel :

```bash
sudo mount /dev/sdb1 /srv/donnees
```

Ne l'exécutez que si vous avez identifié le périphérique et le système de fichiers de test.

Avant un montage :

1. Identifiez le périphérique.
2. Examinez son système de fichiers.
3. Vérifiez si des données importantes existent déjà.
4. Préparez le point de montage.
5. Choisissez des options adaptées.
6. Vérifiez le résultat.

Si le système de fichiers possède déjà des données, monter le périphérique sur un répertoire non vide peut masquer le contenu précédent du répertoire tant que le montage reste actif.

## 8.9 Démonter un système de fichiers

```bash
sudo umount /srv/donnees
```

Cette commande demande le démontage du système de fichiers associé au chemin.

Un démontage peut échouer si le système de fichiers est occupé.

Une cause possible est un processus dont le répertoire courant se trouve sous le point de montage ou qui utilise un fichier ouvert.

Avant de forcer une opération, identifiez les processus et déterminez la manière sûre de les arrêter ou de libérer les ressources.

## 8.10 Comprendre `/etc/fstab`

`/etc/fstab` contient des informations permettant de décrire des systèmes de fichiers et leur montage.

Les entrées comprennent habituellement :

```text
source  point_de_montage  type  options  dump  pass
```

Les champs exacts doivent être interprétés selon le format et la documentation du système.

Une approche fréquente consiste à utiliser l'UUID du système de fichiers plutôt qu'un nom de périphérique pouvant changer.

Exemple fictif :

```text
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx /srv/donnees ext4 defaults,nofail 0 2
```

Cette ligne est **illustrative**. Elle ne doit pas être copiée telle quelle : l'UUID, le type de système de fichiers, les options et le point de montage doivent correspondre à la configuration réelle.

### Précautions avant de modifier `/etc/fstab`

1. Sauvegardez le fichier.
2. Identifiez précisément le système de fichiers.
3. Vérifiez l'UUID avec un outil adapté.
4. Vérifiez le point de montage.
5. Comprenez les options.
6. Validez la configuration avec les outils disponibles sur la distribution.
7. Préparez une possibilité de revenir en arrière.
8. Évitez de provoquer un redémarrage non maîtrisé sur une machine distante.

Une erreur peut compliquer le démarrage ou rendre un montage indisponible.

## 8.11 Comprendre LVM

LVM signifie *Logical Volume Manager*.

Il permet d'organiser le stockage à travers des couches logiques.

Conceptuellement :

```text
+--------------------------------+
| Systeme de fichiers             |
| Exemple : ext4                  |
+--------------------------------+
                |
                v
+--------------------------------+
| Volume logique                  |
| Logical Volume                  |
+--------------------------------+
                |
                v
+--------------------------------+
| Groupe de volumes               |
| Volume Group                    |
+--------------------------------+
                |
                v
+--------------------------------+
| Volumes physiques               |
| Physical Volumes                |
+--------------------------------+
                |
                v
+--------------------------------+
| Disques ou partitions           |
+--------------------------------+
```

LVM peut faciliter l'allocation de volumes logiques et certaines opérations d'extension.

Il ne remplace pas une sauvegarde et ne dispense pas de vérifier les limites du système de fichiers.

## 8.12 Examiner LVM

Si LVM est installé et utilisé :

```bash
sudo pvs
```

Affiche une vue des volumes physiques.

```bash
sudo vgs
```

Affiche une vue des groupes de volumes.

```bash
sudo lvs
```

Affiche une vue des volumes logiques.

Ces commandes peuvent nécessiter des privilèges et ne sont pas nécessairement disponibles sur chaque installation.

## 8.13 Comprendre l'extension d'un volume logique

Étendre un volume logique peut impliquer plusieurs étapes distinctes :

1. Vérifier l'espace disponible dans le groupe de volumes.
2. Étendre le volume logique.
3. Étendre le système de fichiers, si le type et la configuration le permettent.
4. Vérifier la nouvelle taille et l'intégrité de l'application.

Ne confondez pas l'extension du volume logique avec l'extension automatique du système de fichiers.

La procédure dépend du type de système de fichiers et de la configuration du volume.

## 8.14 Les opérations destructives

Des outils tels que `mkfs`, `fdisk` ou `parted` peuvent être utilisés pour créer des systèmes de fichiers ou modifier des partitions.

Ils peuvent également détruire les données si une opération vise le mauvais périphérique.

**Ce cours n'exige pas de formater un disque.** Pour apprendre ces commandes, utilisez un disque virtuel dédié et vérifiez son identité à plusieurs reprises.

Ne lancez jamais une commande de formatage sur un périphérique dont vous n'avez pas confirmé l'identité.


# 9. Sauvegardes et restauration

Une sauvegarde n'est utile que si les données nécessaires peuvent être restaurées.

La préparation d'une sauvegarde doit tenir compte du périmètre, de la fréquence, de la conservation, de la sécurité et des objectifs de restauration.

## 9.1 Pourquoi sauvegarder ?

Les sauvegardes permettent de réduire les conséquences de scénarios tels que :

- Suppression accidentelle.
- Corruption de données.
- Erreur de configuration.
- Défaillance matérielle.
- Incident affectant une application.
- Compromission d'un système.
- Perte d'un environnement de travail.

Une sauvegarde stockée uniquement sur le même disque que les données originales ne protège pas contre toutes les pannes de ce disque.

## 9.2 Comprendre le principe de séparation

```text
+------------------------------+
| Serveur de production        |
| Documents et configurations  |
+------------------------------+
               |
               v
+------------------------------+
| Processus de sauvegarde      |
| Copie planifiee et verifiee  |
+------------------------------+
               |
               v
+------------------------------+
| Stockage de sauvegarde       |
| Emplacement separe           |
+------------------------------+
               |
               v
+------------------------------+
| Test de restauration         |
| Verification des donnees     |
+------------------------------+
```

La destination réelle doit être adaptée aux besoins et au niveau de risque. Une sauvegarde peut nécessiter un stockage distant, une séparation des identifiants ou une protection contre les modifications accidentelles et malveillantes.

## 9.3 Comprendre les objectifs RPO et RTO

Le RPO (*Recovery Point Objective*) indique la perte maximale de données acceptable exprimée en durée.

Le RTO (*Recovery Time Objective*) indique le délai cible de rétablissement d'un service.

Exemple :

```text
RPO cible : 4 heures
RTO cible : 2 heures
```

Interprétation :

- Les données restaurées ne devraient normalement pas être plus anciennes que la limite définie par le RPO.
- Le service devrait être rétabli dans la durée définie par le RTO.

Ces objectifs sont des exemples. Ils doivent être définis en fonction des besoins métiers.

## 9.4 Créer une archive avec `tar`

Pour archiver un répertoire :

```bash
tar -czf sauvegarde-documents.tar.gz documents/
```

Interprétation :

- `-c` : crée une archive.
- `-z` : utilise gzip.
- `-f` : indique le fichier de sortie.

L'option `-v` permet généralement d'afficher les noms traités pendant l'opération :

```bash
tar -czvf sauvegarde-documents.tar.gz documents/
```

L'archive est créée dans le contexte du répertoire courant, sauf indication d'un autre chemin.

## 9.5 Examiner le contenu d'une archive

```bash
tar -tzf sauvegarde-documents.tar.gz
```

Cette commande liste les entrées de l'archive sans extraire leur contenu.

Il est préférable d'examiner une archive d'origine inconnue avant l'extraction, notamment pour repérer des chemins inattendus.

## 9.6 Extraire une archive dans un répertoire de test

Créez un emplacement de test :

```bash
mkdir -p restauration-test
```

Extrayez :

```bash
tar -xzf sauvegarde-documents.tar.gz -C restauration-test
```

`-C` demande à `tar` de travailler depuis le répertoire indiqué pour l'extraction.

Vérifiez les fichiers restaurés :

```bash
find restauration-test -print
```

Ne restaurez pas une archive directement sur les données de production sans plan de restauration et contrôle des chemins.

## 9.7 Sauvegarder avec `rsync`

`rsync` permet de synchroniser des fichiers et des répertoires.

Exemple vers un répertoire de sauvegarde :

```bash
rsync -a --dry-run ~/formation-linux/ ~/sauvegarde-formation-linux/
```

L'option `--dry-run` permet de simuler l'opération et d'examiner ce qui serait effectué.

L'option `-a` active un mode d'archivage courant qui préserve plusieurs attributs de fichiers, sous réserve des possibilités et permissions de l'environnement.

Pour effectuer ensuite la copie après vérification :

```bash
rsync -a ~/formation-linux/ ~/sauvegarde-formation-linux/
```

Vérifiez toujours les chemins source et destination.

Le slash final à la fin de la source a une signification pratique importante : il demande généralement de synchroniser le contenu du répertoire source dans la destination, plutôt que de traiter le répertoire source de la même manière qu'un élément à placer dans la destination.

## 9.8 Les options de suppression dans rsync

Certaines options de rsync peuvent supprimer des éléments dans la destination afin de la faire correspondre à la source.

Ces options peuvent être dangereuses si la destination est mal identifiée.

N'ajoutez pas `--delete` à une commande sans comprendre exactement quels fichiers peuvent être supprimés.

Commencez par une simulation et examinez minutieusement le résultat.

## 9.9 Sauvegarder des configurations

Dans un environnement de test, une archive de fichiers de configuration peut être utile.

Exemple :

```bash
tar -czf configurations-test.tar.gz /etc/hostname /etc/hosts
```

Selon la version de `tar` et la structure des chemins fournis, le contenu de l'archive et les chemins enregistrés peuvent différer.

Pour une sauvegarde professionnelle, définissez explicitement les fichiers inclus, les métadonnées nécessaires et les conditions de restauration.

Certains fichiers de configuration contiennent des secrets ou des informations sensibles. La sauvegarde doit être protégée en conséquence.

## 9.10 Tester une restauration

Une procédure de sauvegarde ne doit pas se terminer à la création de l'archive.

Vérifiez :

1. Que le fichier existe.
2. Qu'il est lisible.
3. Que son contenu est cohérent.
4. Qu'il peut être extrait dans un environnement de test.
5. Que les fichiers importants sont présents.
6. Que les permissions et métadonnées nécessaires sont conservées.
7. Que le résultat correspond aux besoins de l'application.

Le test doit être documenté.

## 9.11 Atelier de sauvegarde

Dans un environnement de test :

```bash
mkdir -p ~/sauvegarde-lab/source
mkdir -p ~/sauvegarde-lab/destination

echo "Configuration initiale" \
    > ~/sauvegarde-lab/source/configuration.txt
```

Simulez la synchronisation :

```bash
rsync -a --dry-run \
    ~/sauvegarde-lab/source/ \
    ~/sauvegarde-lab/destination/
```

Examinez la sortie, puis effectuez la copie :

```bash
rsync -a \
    ~/sauvegarde-lab/source/ \
    ~/sauvegarde-lab/destination/
```

Vérifiez le contenu :

```bash
find ~/sauvegarde-lab -print
cat ~/sauvegarde-lab/destination/configuration.txt
```

Modifiez ensuite le fichier source, refaites une simulation et observez ce que rsync prévoit de modifier.


# 10. Administration réseau avec les outils Linux

Un administrateur intermédiaire doit pouvoir vérifier l'état d'une interface, comprendre les routes, examiner les sockets et distinguer une panne réseau d'une panne applicative.

## 10.1 Examiner les interfaces

```bash
ip addr
```

Affiche les interfaces et leurs adresses.

Pour n'afficher que les liens, sans le détail des adresses :

```bash
ip link
```

Les informations permettent notamment de vérifier le nom, l'état administratif et l'adresse MAC de chaque interface.

L'état `UP` ne garantit pas à lui seul qu'une interface dispose d'une configuration IP correcte ou d'une connectivité fonctionnelle.

## 10.2 Examiner les routes

```bash
ip route
```

Une ligne conceptuelle peut ressembler à :

```text
default via 192.168.1.1 dev eth0
```

La route par défaut est généralement utilisée pour les destinations qui ne correspondent pas à une route plus spécifique.

Le prochain saut peut être un routeur ou un autre équipement selon la topologie.

Pour une recherche réseau correcte, il faut examiner le préfixe de destination, le prochain saut, l'interface et les éventuelles politiques de routage.

## 10.3 Tester la connectivité par étapes

Une erreur de connexion peut se produire à plusieurs niveaux.

```text
Application
    |
    v
Resolution DNS, si un nom est utilise
    |
    v
Adresse IP et route
    |
    v
Connexion TCP ou autre transport
    |
    v
Service distant
    |
    v
Reponse applicative
```

Un test de connectivité doit identifier la couche concernée au lieu de s'appuyer sur une commande unique.

## 10.4 Vérifier une résolution DNS

```bash
getent hosts example.com
```

Cette commande demande au système de résoudre le nom selon ses mécanismes configurés.

Si elle échoue, examinez notamment :

- Le nom recherché.
- Le fonctionnement de la résolution locale.
- La configuration des serveurs DNS.
- Les journaux ou erreurs disponibles.
- La connectivité vers les résolveurs.

Ne modifiez pas les fichiers de résolution ou la configuration réseau sans comprendre quel gestionnaire contrôle la configuration de la machine.

## 10.5 Examiner les routes vers une destination

```bash
ip route get 192.168.1.1
```

La commande demande au noyau comment une destination IPv4 serait acheminée selon les règles applicables.

Utilisez une adresse pertinente pour le diagnostic.

Le résultat peut indiquer l'interface et le prochain saut choisis.

## 10.6 Examiner les sockets avec `ss`

```bash
ss -tuln
```

La commande affiche certaines sockets TCP et UDP en écoute.

Pour examiner également davantage d'informations sur les connexions selon les options disponibles :

```bash
ss -tunap
```

L'affichage de certains processus et détails peut nécessiter des privilèges.

Ne confondez pas une socket en écoute avec une application pleinement opérationnelle. Il faut aussi tester son comportement et ses dépendances.

## 10.7 Identifier un service qui écoute sur un port

Supposons qu'un serveur Web soit censé utiliser le port 443.

Commencez par examiner les sockets :

```bash
ss -tln
```

Recherchez un port correspondant à `443` dans la sortie.

Si le service est absent de la sortie :

1. Vérifiez le service avec systemd.
2. Consultez ses journaux.
3. Vérifiez sa configuration.
4. Vérifiez l'adresse sur laquelle il doit écouter.
5. Recherchez les erreurs de démarrage.

Si le service écoute, mais reste inaccessible depuis un autre hôte, examinez la route, le pare-feu, les règles de filtrage et le chemin réseau.

## 10.8 Vérifier le routage d'un client vers un serveur

Imaginons :

```text
Client : 192.168.10.50/24
Serveur : 192.168.20.10/24
Passerelle du client : 192.168.10.1
```

Ces adresses sont fictives.

Le client et le serveur se trouvent dans des sous-réseaux IPv4 différents selon les préfixes indiqués. Une communication entre eux nécessite normalement un chemin de routage approprié.

Schéma :

```text
+---------------------------+
| Client                    |
| 192.168.10.50/24          |
+---------------------------+
              |
              v
+---------------------------+
| Routeur                   |
| 192.168.10.1               |
| 192.168.20.1               |
+---------------------------+
              |
              v
+---------------------------+
| Serveur                   |
| 192.168.20.10/24          |
+---------------------------+
```

La connectivité dépend aussi des routes de retour, du filtrage réseau et du comportement des systèmes.

Un paquet peut atteindre un serveur sans que la réponse puisse revenir correctement.

## 10.9 Utiliser `ping` avec discernement

```bash
ping -c 4 192.168.1.1
```

Cette commande envoie quatre requêtes ICMP lorsque l'option est prise en charge.

Un échec peut s'expliquer par :

- Une absence de connectivité.
- Une route manquante.
- Un filtrage ICMP.
- Une interface inactive.
- Une destination qui ne répond pas aux requêtes.
- Une restriction particulière de l'environnement.

Un succès confirme uniquement certains aspects du chemin testé.

## 10.10 Examiner la configuration réseau

La manière de configurer le réseau dépend de la distribution et de l'environnement.

Un système peut utiliser NetworkManager, systemd-networkd, Netplan, des fichiers de configuration propres à la distribution ou d'autres mécanismes.

Avant de modifier une configuration :

1. Identifiez l'outil qui la gère.
2. Sauvegardez les fichiers concernés.
3. Préparez une méthode de retour arrière.
4. Vérifiez la cohérence des routes et des adresses.
5. Évitez de modifier à distance le réseau sans accès de secours.

Une mauvaise configuration peut interrompre la session SSH utilisée pour l'administration.


# 11. Administration et sécurisation de SSH

SSH permet d'administrer une machine à distance de manière chiffrée.

La sécurisation doit couvrir l'authentification, les comptes autorisés, la configuration du serveur et la surveillance des connexions.

## 11.1 Examiner le service SSH

Selon la distribution, le service peut se nommer `ssh` ou `sshd`.

Exemples :

```bash
systemctl status ssh
```

ou :

```bash
systemctl status sshd
```

Si aucune unité correspondante n'existe, le serveur SSH peut ne pas être installé ou utiliser une autre configuration.

## 11.2 Comprendre l'authentification par clé

Une clé SSH est généralement constituée d'une partie privée et d'une partie publique.

La clé privée doit rester sous le contrôle de son propriétaire et être protégée.

La clé publique peut être installée sur les systèmes auxquels le compte est autorisé à se connecter.

### Schéma de l'authentification par clé

```text
+--------------------------------+
| Poste client                   |
|                                |
| Cle privee protegee            |
| Cle publique                   |
+--------------------------------+
                |
                | Connexion SSH
                v
+--------------------------------+
| Serveur SSH                    |
|                                |
| Cle publique autorisee         |
| Controle du compte              |
+--------------------------------+
                |
                v
+--------------------------------+
| Session authentifiee           |
+--------------------------------+
```

La clé privée n'a normalement pas besoin d'être transmise au serveur pendant l'authentification.

## 11.3 Générer une clé SSH

Pour générer une paire de clés Ed25519 dans un environnement compatible :

```bash
ssh-keygen -t ed25519
```

L'outil demande habituellement un emplacement de stockage et propose l'utilisation d'une phrase secrète.

Protégez la clé privée et choisissez des paramètres adaptés à la politique de sécurité.

N'écrasez pas une clé existante sans comprendre ses usages.

## 11.4 Installer une clé publique

Si `ssh-copy-id` est disponible et si l'authentification actuelle permet la connexion :

```bash
ssh-copy-id utilisateur@serveur
```

Remplacez les valeurs par le compte et l'hôte réels.

La commande tente d'ajouter la clé publique au compte distant.

Examinez toujours l'hôte ciblé et assurez-vous que vous contrôlez la destination.

## 11.5 Tester avant de modifier la configuration

Avant de modifier le serveur SSH :

1. Ouvrez une session administrative de secours si possible.
2. Générez ou identifiez la clé prévue.
3. Installez la clé publique.
4. Testez la connexion par clé dans une nouvelle session.
5. Vérifiez que l'accès attendu fonctionne.
6. Préparez un retour arrière avant de modifier les options d'authentification.

Ne désactivez jamais une méthode de connexion tant qu'une alternative n'a pas été testée correctement.

## 11.6 Examiner la configuration SSH

La configuration du serveur se trouve fréquemment dans :

```text
/etc/ssh/sshd_config
```

Des fichiers complémentaires peuvent être présents dans :

```text
/etc/ssh/sshd_config.d/
```

La façon dont ils sont pris en compte dépend de la version et de la configuration du serveur SSH.

Pour examiner le fichier principal :

```bash
sudo less /etc/ssh/sshd_config
```

N'appliquez pas une modification uniquement parce qu'elle est souvent recommandée dans un tutoriel. Il faut tenir compte de la politique de sécurité, des comptes utilisés et des méthodes de connexion nécessaires.

## 11.7 Comprendre quelques directives

Parmi les directives possibles :

- `PermitRootLogin` : contrôle certaines méthodes de connexion directe du compte root.
- `PasswordAuthentication` : contrôle l'authentification par mot de passe.
- `PubkeyAuthentication` : contrôle l'authentification par clé publique.
- `AllowUsers` : limite les utilisateurs autorisés selon la configuration.

La valeur appropriée dépend de l'environnement, des mécanismes d'authentification et de la version de SSH.

Ne copiez pas une configuration complète sans vérifier ses effets.

## 11.8 Valider la configuration

OpenSSH fournit généralement un mode de test de configuration :

```bash
sudo sshd -t
```

Le chemin de l'exécutable peut différer selon la distribution.

Cette commande vérifie la syntaxe du fichier de configuration principal et des éléments inclus selon le fonctionnement du serveur.

Une configuration syntaxiquement correcte peut cependant produire une configuration fonctionnellement inadaptée. Les directives effectives et les méthodes de connexion doivent être vérifiées.

## 11.9 Appliquer une modification

Lorsqu'une modification est validée, l'application peut nécessiter un rechargement ou un redémarrage du service.

Le choix dépend de la configuration et de l'environnement systemd.

Ne coupez pas la session SSH existante avant d'avoir ouvert et testé une nouvelle session.

Après le changement, vérifiez :

- L'état de l'unité.
- Les journaux.
- Le port d'écoute.
- L'ouverture d'une nouvelle session.
- Les méthodes d'authentification attendues.

## 11.10 Examiner les journaux SSH

Sur un système où l'unité se nomme `ssh` :

```bash
journalctl -u ssh
```

Sur certains systèmes :

```bash
journalctl -u sshd
```

Cherchez les erreurs de configuration et les informations relatives à l'authentification.

Évitez de publier des journaux contenant des adresses internes, des noms de compte ou d'autres informations sensibles sans les examiner.


# 12. Pare-feu et contrôle des connexions

Un pare-feu contrôle les communications réseau selon un ensemble de règles.

Le but n'est pas de bloquer tout le trafic indistinctement, mais d'autoriser les flux nécessaires et de réduire l'exposition inutile.

## 12.1 Comprendre le rôle d'un pare-feu

```text
+------------------------------+
| Client distant               |
+------------------------------+
               |
               v
+------------------------------+
| Filtrage reseau               |
| Autoriser ou bloquer          |
+------------------------------+
               |
               v
+------------------------------+
| Service local                 |
| Port et adresse d'ecoute      |
+------------------------------+
```

Un service peut fonctionner localement et rester inaccessible à distance à cause d'un pare-feu.

Inversement, une règle de pare-feu autorisant un port ne suffit pas à rendre un service disponible si aucun programme n'écoute sur ce port.

## 12.2 Examiner UFW

UFW est une interface de gestion de pare-feu disponible sur de nombreux systèmes Debian et Ubuntu, mais elle n'est pas nécessairement activée ou installée partout.

Examiner l'état :

```bash
sudo ufw status verbose
```

Cette commande affiche l'état et des informations relatives aux règles UFW lorsqu'il est disponible.

## 12.3 Comprendre la gestion des règles

Une politique de pare-feu doit être conçue en fonction :

- Des services réellement nécessaires.
- Des interfaces utilisées.
- Des sources autorisées.
- Du réseau de gestion.
- Des besoins de sortie.
- Des contraintes de sécurité.

N'appliquez pas une politique par défaut sans comprendre les flux nécessaires.

## 12.4 Précaution pour l'administration distante

Si vous êtes connecté à distance, une règle trop restrictive peut couper la connexion d'administration.

Avant toute modification du pare-feu :

1. Vérifiez le port SSH et les adresses nécessaires.
2. Confirmez les règles existantes.
3. Préparez un accès de secours.
4. Planifiez le changement.
5. Testez une nouvelle connexion après application.
6. Gardez la session existante tant que la vérification n'est pas terminée.

## 12.5 Exemple conceptuel avec UFW

Sur un système de test utilisant UFW, l'ouverture d'un service peut se faire par une règle adaptée au service.

Par exemple, pour autoriser SSH avec le profil approprié :

```bash
sudo ufw allow OpenSSH
```

La présence du profil dépend de l'installation.

Vérifiez ensuite :

```bash
sudo ufw status verbose
```

N'activez pas un pare-feu distant avant d'avoir vérifié les règles permettant de conserver votre accès.

## 12.6 UFW, nftables et iptables

Ces outils ne sont pas interchangeables au niveau de leur interface.

- UFW fournit une interface de gestion simplifiée.
- nftables est une infrastructure moderne de filtrage réseau sous Linux.
- iptables est une interface historique toujours présente dans certains environnements.

La configuration effective dépend de la distribution et des outils employés.

Évitez de mélanger plusieurs gestionnaires de règles sans comprendre comment ils interagissent.

## 12.7 Atelier de diagnostic réseau

Dans un environnement de test :

1. Examinez les interfaces avec `ip addr`.
2. Examinez les routes avec `ip route`.
3. Examinez les ports avec `ss -tuln`.
4. Vérifiez l'état du service concerné.
5. Examinez les règles du pare-feu.
6. Comparez l'accessibilité locale et distante.
7. Identifiez à quel niveau le trafic semble échouer.

La correction doit cibler le véritable problème et ne doit pas consister à désactiver arbitrairement toutes les protections.


# 13. Gestion des logiciels et maintenance du système

Un serveur nécessite des mises à jour, une gestion des paquets et un suivi de la configuration logicielle.

Les commandes dépendent de la distribution.

## 13.1 Identifier le gestionnaire de paquets

```bash
cat /etc/os-release
```

Cette commande permet d'identifier la distribution et sa version.

Familles courantes :

| Distribution | Gestionnaire habituel |
|---|---|
| Debian / Ubuntu | APT |
| Fedora | DNF |
| Arch Linux | Pacman |
| Certaines distributions SUSE | Zypper |

N'exécutez pas une commande de paquetage sans vérifier sa compatibilité.

## 13.2 Actualiser APT

Sur Debian ou Ubuntu :

```bash
sudo apt update
```

Actualise les informations locales sur les paquets dans les dépôts configurés.

## 13.3 Mettre à jour les logiciels

```bash
sudo apt upgrade
```

Cette opération propose des mises à niveau selon les règles d'APT.

Examinez attentivement :

- Les paquets à mettre à jour.
- Les éventuelles suppressions.
- Les nouveaux paquets.
- Les avertissements.
- Les services susceptibles d'être affectés.

Dans une infrastructure professionnelle, utilisez une procédure de maintenance avec sauvegarde, validation, fenêtre d'intervention et possibilité de retour arrière.

## 13.4 Examiner un paquet

```bash
apt show nom-du-paquet
```

Cette commande fournit des informations sur le paquet lorsqu'il est disponible dans les sources configurées.

Pour rechercher un paquet :

```bash
apt search mot-cle
```

Les résultats dépendent des dépôts configurés et des informations disponibles.

## 13.5 Repérer les services affectés par les mises à jour

Une mise à jour peut modifier des exécutables, des bibliothèques ou des fichiers de configuration.

Après une opération importante, examinez notamment :

- Les services en échec.
- Les journaux.
- Les applications essentielles.
- La connectivité réseau.
- La disponibilité des points de montage.

Ne considérez pas un message d'installation réussi comme une validation fonctionnelle de l'ensemble du serveur.

## 13.6 Les mises à jour de sécurité

Les correctifs de sécurité réduisent l'exposition à des vulnérabilités connues, mais leur application doit être planifiée correctement.

Dans un environnement professionnel :

1. Identifiez le périmètre.
2. Consultez les notes de version ou avis pertinents.
3. Vérifiez les dépendances.
4. Préparez la sauvegarde.
5. Effectuez la mise à jour.
6. Vérifiez les services.
7. Documentez les résultats.

Le processus précis dépend de la criticité des systèmes et des règles de l'organisation.

## 13.7 Examiner l'espace occupé par les paquets

Sur un système utilisant APT, les caches de paquets peuvent contribuer à l'espace utilisé.

Avant de supprimer des données :

```bash
df -h
```

Examinez ensuite les répertoires pertinents et les outils disponibles.

Ne supprimez pas manuellement des fichiers de l'arborescence du système de paquets sans comprendre leur rôle.

## 13.8 Atelier de maintenance

Dans un système de test :

1. Identifiez la distribution.
2. Examinez l'état du système.
3. Actualisez les informations des paquets.
4. Consultez les mises à niveau proposées.
5. Effectuez une mise à jour seulement si elle est adaptée à l'exercice.
6. Vérifiez les services après l'opération.
7. Consultez les journaux en cas d'échec.
8. Documentez les résultats.


# 14. Automatisation avec cron et les timers systemd

L'automatisation permet de programmer des opérations répétitives.

Il faut toutefois vérifier que la tâche est appropriée, qu'elle peut être exécutée de manière fiable et que ses erreurs seront visibles.

## 14.1 Comprendre cron

cron est un mécanisme de planification utilisé sur de nombreux systèmes Linux.

Il permet de lancer des commandes selon un calendrier.

La configuration peut différer entre une crontab utilisateur, une crontab système et certains répertoires de tâches planifiées.

## 14.2 Structure d'une entrée cron

Une entrée cron utilisateur utilise généralement cette structure :

```text
minute heure jour_du_mois mois jour_de_la_semaine commande
```

Exemple :

```text
30 2 * * * /home/alice/scripts/controle.sh
```

Cette entrée demande normalement l'exécution quotidienne de la commande à 02 h 30, selon les règles du planificateur et son contexte temporel.

Les champs utilisent généralement :

- Minute : `0` à `59`.
- Heure : `0` à `23`.
- Jour du mois : `1` à `31`.
- Mois : `1` à `12`.
- Jour de la semaine : valeurs définies par l'implémentation, couramment `0` à `7` pour le dimanche dans certaines versions.

La sémantique des champs jour du mois et jour de la semaine mérite une attention particulière. Les implémentations courantes peuvent utiliser une logique spécifique lorsque les deux champs sont restreints.

## 14.3 Examiner la crontab utilisateur

```bash
crontab -l
```

Affiche la crontab de l'utilisateur courant, si elle existe.

Pour l'éditer :

```bash
crontab -e
```

Cette commande ouvre normalement l'éditeur configuré pour modifier les entrées.

Ne remplacez pas toute une crontab existante sans examiner les tâches déjà en place.

## 14.4 Pourquoi une commande qui fonctionne au terminal échoue-t-elle dans cron ?

cron exécute la tâche dans un environnement qui peut être différent de votre session interactive.

Différences possibles :

- Valeur de `PATH`.
- Répertoire de travail.
- Variables d'environnement.
- Permissions.
- Disponibilité du réseau.
- Accès aux fichiers.
- Shell d'exécution.

Un script planifié doit donc utiliser des chemins explicites, vérifier ses entrées et enregistrer les erreurs.

## 14.5 Exemple de tâche de contrôle

Supposons un script enregistré sous :

```text
/home/alice/scripts/controle.sh
```

Une entrée possible est :

```text
*/15 * * * * /home/alice/scripts/controle.sh
```

Cette entrée demande généralement l'exécution toutes les quinze minutes.

L'utilité réelle dépend du contenu du script. Il doit aussi éviter de générer trop de journaux ou de lancer une nouvelle instance si la précédente est encore active.

## 14.6 Rediriger les sorties d'une tâche cron

Une entrée peut utiliser les redirections du Shell :

```text
*/15 * * * * /home/alice/scripts/controle.sh >> /home/alice/controle.log 2>&1
```

Cette forme ajoute la sortie standard et la sortie d'erreur au fichier de journal dans les Shells compatibles.

Une politique de rotation doit être prévue si le fichier risque de grossir continuellement.

## 14.7 Comprendre les timers systemd

Les timers systemd offrent un autre mécanisme de planification.

Un timer est généralement associé à une autre unité, souvent un service.

### Schéma de fonctionnement

```text
+---------------------------+
| Timer systemd             |
| Date ou intervalle        |
+---------------------------+
              |
              v
+---------------------------+
| Unite service             |
| Commande ou script        |
+---------------------------+
              |
              v
+---------------------------+
| Resultat                  |
| Journaux et code de retour|
+---------------------------+
```

Les timers offrent une intégration avec le système de gestion des services et les journaux.

Ils permettent aussi, selon leur configuration, de définir des dépendances ou des comportements spécifiques au démarrage.

## 14.8 Cron ou timer systemd ?

| Critère | cron | Timer systemd |
|---|---|---|
| Simplicité d'une tâche ponctuelle | Très adapté | Adapté |
| Intégration à systemd | Indirecte | Native |
| Gestion du service associé | À organiser | Via l'unité service |
| Journaux | À prévoir ou selon la configuration | Intégration possible avec journalctl |
| Dépendances systemd | Moins intégrées | Disponibles via les unités |

Le choix doit correspondre au système et aux besoins.

## 14.9 Atelier de planification

Dans un environnement de test :

1. Créez un script sans effet destructif.
2. Faites-le écrire une ligne horodatée dans un journal.
3. Exécutez-le manuellement.
4. Vérifiez son code de retour.
5. Configurez une tâche planifiée.
6. Attendez l'exécution selon le calendrier choisi, ou testez la configuration dans un créneau adapté.
7. Vérifiez les journaux.
8. Retirez la tâche après l'exercice si elle n'est plus nécessaire.

N'ajoutez pas de tâche planifiée tant que vous n'avez pas vérifié ce qu'elle exécute et comment elle sera arrêtée.


# 15. Écriture de scripts Bash robustes

Les scripts d'administration doivent être plus fiables que de simples listes de commandes copiées dans un fichier.

Un script robuste vérifie ses entrées, protège les chemins, traite les erreurs et fournit des résultats compréhensibles.

## 15.1 Les caractéristiques d'un bon script

Un bon script doit :

- Avoir un objectif précis.
- Utiliser des chemins explicites.
- Protéger les variables avec des guillemets appropriés.
- Vérifier les dépendances nécessaires.
- Contrôler le résultat des commandes importantes.
- Éviter les effets de bord inattendus.
- Afficher des messages compréhensibles.
- Renvoyer des codes de sortie cohérents.
- Préserver les données.
- Être documenté et testé.

## 15.2 Structure générale

```bash
#!/usr/bin/env bash

# Objectif :
# Description de la tache.

# 1. Definir les variables.
# 2. Verifier l'environnement.
# 3. Valider les arguments.
# 4. Executer les operations.
# 5. Verifier les resultats.
# 6. Afficher un resume.
```

Cette structure facilite la lecture et la maintenance.

## 15.3 Vérifier les dépendances

Supposons qu'un script nécessite `find`.

On peut vérifier la présence de la commande :

```bash
if ! command -v find >/dev/null 2>&1; then
    echo "ERREUR : la commande find est indisponible." >&2
    exit 1
fi
```

Explication :

- `command -v find` cherche comment le Shell résout le nom.
- `!` inverse le résultat.
- `>/dev/null 2>&1` masque les sorties ordinaires et les erreurs dans cet exemple.
- `>&2` envoie le message sur la sortie d'erreur.
- `exit 1` termine le script avec un code signalant un problème.

La forme de redirection utilisée est compatible avec Bash.

## 15.4 Utiliser des variables protégées

```bash
SOURCE="$HOME/formation-linux"
DESTINATION="$HOME/sauvegarde-formation-linux"
```

Ensuite :

```bash
ls -la "$SOURCE"
```

Les guillemets permettent de traiter la valeur comme un argument unique lorsqu'elle contient des espaces et limitent les expansions non souhaitées.

## 15.5 Vérifier les chemins

Avant une sauvegarde :

```bash
if [ ! -d "$SOURCE" ]; then
    echo "ERREUR : source absente." >&2
    exit 1
fi
```

Une vérification similaire doit être adaptée au type de chemin attendu.

Ne supposez pas que l'existence d'un chemin prouve que son contenu est correct ou qu'il peut être utilisé en toute sécurité.

## 15.6 Utiliser les codes de retour

Dans Bash :

```bash
commande
statut=$?
```

La variable `statut` reçoit le code de retour de la commande précédente.

Pourtant, il est généralement plus lisible d'utiliser directement une condition :

```bash
if commande; then
    echo "Operation reussie."
else
    echo "Operation en echec." >&2
    exit 1
fi
```

Cette construction relie l'opération à son traitement d'erreur.

## 15.7 Comprendre `set -u`

Dans Bash :

```bash
set -u
```

demande au Shell de signaler certaines expansions de variables non définies au lieu de les traiter silencieusement comme des valeurs vides.

Cela peut aider à détecter des erreurs de frappe dans les variables.

Il faut néanmoins prévoir les variables qui peuvent être volontairement absentes.

## 15.8 Comprendre `set -o pipefail`

```bash
set -o pipefail
```

Cette option modifie le code de retour d'un pipeline afin qu'un échec dans certaines commandes du pipeline puisse être signalé au lieu de ne considérer que la dernière commande.

Exemple :

```bash
commande_a | commande_b
```

Sans `pipefail`, le code de retour du pipeline dépend normalement de celui de la dernière commande dans Bash.

Avec `pipefail`, l'échec d'une commande précédente peut être reflété par le résultat du pipeline.

Il faut comprendre cette différence pour concevoir des traitements robustes.

## 15.9 Comprendre `set -e`

```bash
set -e
```

Cette option demande à Bash de quitter dans certaines situations lorsqu'une commande retourne un code non nul.

Cependant, son comportement dépend du contexte : conditions, pipelines, listes de commandes et substitutions peuvent changer l'effet attendu.

Elle ne remplace pas une gestion explicite des erreurs importantes.

Pour un script d'administration, utilisez des contrôles compréhensibles sur les opérations critiques plutôt que de supposer que `set -e` garantit une gestion parfaite de toutes les erreurs.

## 15.10 Une structure de script courante

```bash
#!/usr/bin/env bash

set -u
set -o pipefail

echo "Debut du controle"

if ! command -v df >/dev/null 2>&1; then
    echo "ERREUR : df est indisponible." >&2
    exit 1
fi

if ! df -h; then
    echo "ERREUR : impossible d'examiner les systemes de fichiers." >&2
    exit 1
fi

echo "Controle termine."
exit 0
```

Ce script vérifie la disponibilité de `df`, puis affiche les informations des systèmes de fichiers.

Il ne cherche pas encore à déterminer si l'utilisation est acceptable. Une vérification de seuil devra ajouter une logique spécifique et correctement tester les résultats.

## 15.11 Journaliser les opérations

Une tâche d'administration peut écrire dans un journal dédié.

Exemple simple :

```bash
LOG="$HOME/controle.log"

if ! echo "$(date '+%F %T') : controle lance" >> "$LOG"; then
    echo "ERREUR : impossible d'ecrire dans le journal." >&2
    exit 1
fi
```

L'heure affichée dépend de la configuration temporelle du système.

Un journal doit être protégé contre les modifications non souhaitées et sa croissance doit être gérée.

## 15.12 Éviter les scripts destructeurs par défaut

Les opérations automatisées peuvent amplifier les erreurs.

Une commande répétée chaque minute peut causer davantage de dégâts qu'une commande exécutée une seule fois.

Avant d'automatiser :

1. Testez manuellement.
2. Utilisez un environnement isolé.
3. Identifiez les fichiers concernés.
4. Vérifiez les chemins.
5. Ajoutez une simulation lorsque c'est possible.
6. Enregistrez les erreurs.
7. Prévoyez un moyen d'arrêter la tâche.
8. Vérifiez les effets après plusieurs exécutions.

## 15.13 Tester un script

Bash fournit un mode de vérification syntaxique :

```bash
bash -n script.sh
```

Cette commande examine la syntaxe sans exécuter normalement les instructions du script.

Elle ne garantit pas l'absence d'erreurs de logique.

Pour une analyse complémentaire, des outils tels que ShellCheck peuvent être utilisés lorsqu'ils sont disponibles.

La validation manuelle reste nécessaire.

## 15.14 Atelier : un rapport système

Créez `rapport-systeme.sh` :

```bash
#!/usr/bin/env bash

set -u
set -o pipefail

echo "===================================="
echo " RAPPORT SYSTEME"
echo "===================================="

echo
echo "[Date]"
date

echo
echo "[Utilisateur]"
whoami

echo
echo "[Noyau]"
uname -r

echo
echo "[Temps de fonctionnement]"
uptime

echo
echo "[Memoire]"
if ! free -h; then
    echo "ERREUR : impossible d'examiner la memoire." >&2
    exit 1
fi

echo
echo "[Espace disque]"
if ! df -h; then
    echo "ERREUR : impossible d'examiner le stockage." >&2
    exit 1
fi

echo
echo "Rapport termine."
exit 0
```

Rendez-le exécutable :

```bash
chmod u+x rapport-systeme.sh
```

Lancez-le :

```bash
./rapport-systeme.sh
```

Vérifiez sa syntaxe :

```bash
bash -n rapport-systeme.sh
```

Ce script constitue une base d'observation. Il ne prouve pas que le serveur est en bonne santé : il rassemble seulement quelques informations utiles.


# 16. Surveillance et diagnostic des performances

Un serveur peut fonctionner sans erreur apparente tout en présentant des lenteurs.

La surveillance permet d'établir une situation normale, de détecter les écarts et d'orienter les investigations.

## 16.1 Les ressources à surveiller

Les principales catégories sont :

- CPU.
- Mémoire.
- Swap.
- Stockage.
- Latence des entrées-sorties.
- Réseau.
- Processus.
- Disponibilité des services.

### Schéma de diagnostic des performances

```text
               LENTEUR OBSERVEE
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
         CPU        Memoire      Stockage
          |           |           |
          v           v           v
      top, ps      free, vmstat   df, du, iostat
          |           |           |
          +-----------+-----------+
                      |
                      v
               Examiner aussi
                    le reseau
                      |
                      v
           Correlier les indicateurs
              et les journaux
                      |
                      v
             Formuler une hypothese
                      |
                      v
             Tester et valider
```

Les outils listés ne sont pas tous installés par défaut. Leur disponibilité dépend de la distribution.

## 16.2 Examiner le CPU

```bash
top
```

Repérez :

- L'utilisation globale du CPU.
- Les processus les plus actifs.
- Les évolutions dans le temps.
- La charge système.
- Les éventuelles attentes.

Une utilisation élevée du processeur n'est pas automatiquement un incident : certaines tâches peuvent nécessiter temporairement beaucoup de ressources.

## 16.3 Examiner la mémoire

```bash
free -h
```

La commande fournit un aperçu de la mémoire physique et du swap.

Sous Linux, une partie de la mémoire disponible peut être utilisée pour les caches afin d'améliorer les performances.

Il ne faut donc pas interpréter uniquement la quantité affichée comme « utilisée » sans tenir compte des colonnes et du comportement du noyau.

## 16.4 Comprendre le swap

Le swap est un mécanisme qui permet d'utiliser une zone de stockage comme support à certaines pages mémoire.

Il peut s'agir d'une partition ou d'un fichier, selon la configuration.

Le swap peut aider à gérer les pressions mémoire, mais son utilisation ne garantit pas de bonnes performances : le stockage est normalement beaucoup plus lent que la RAM.

Examiner la présence de swap :

```bash
swapon --show
```

Et :

```bash
free -h
```

Une utilisation du swap doit être interprétée avec l'activité mémoire, la charge et les objectifs de la machine.

## 16.5 Examiner l'activité mémoire avec `vmstat`

Si `vmstat` est disponible :

```bash
vmstat 1 5
```

Cette commande demande généralement cinq rapports espacés d'une seconde.

Elle fournit un aperçu de diverses statistiques système, notamment l'activité des processus, de la mémoire, du swap, des entrées-sorties et du CPU.

La première ligne de certaines statistiques est calculée à partir d'un historique antérieur au moment de la commande. Il faut donc interpréter le résultat dans son contexte.

## 16.6 Examiner le stockage

```bash
df -h
```

Pour l'espace des systèmes de fichiers.

```bash
du -sh /var/log
```

Pour estimer l'espace utilisé par les journaux accessibles à cet emplacement.

Si `iostat` est installé :

```bash
iostat -xz 1 5
```

Cette commande, issue d'outils de surveillance des performances, affiche des statistiques d'entrées-sorties du stockage.

Elle n'est pas disponible sur toutes les installations. Le paquet qui la fournit dépend de la distribution.

Une forte activité disque n'indique pas automatiquement un disque défectueux. Il faut examiner la latence, le débit, la charge et les erreurs éventuelles.

## 16.7 Examiner l'activité réseau

```bash
ip -s link
```

Cette commande présente notamment des compteurs et statistiques d'interfaces.

Les compteurs peuvent aider à identifier des erreurs ou des variations d'activité.

Selon la situation, il faut également examiner :

- Les routes.
- Les sockets.
- Les retransmissions ou pertes observables avec les outils appropriés.
- Les journaux des applications.
- Les équipements intermédiaires.
- Les mesures de latence.

## 16.8 Établir une situation de référence

Pour comprendre une alerte, il est utile de connaître le comportement habituel du système.

Exemple de données à documenter :

```text
CPU habituel : plage observee pendant les heures normales
Memoire : consommation normale et marge disponible
Disque : espace utilise par point de montage
Reseau : trafic et latence habituels
Services : etat attendu
Journaux : messages normaux connus
```

Les seuils doivent être adaptés au service. Un serveur de calcul et un serveur de fichiers n'ont pas les mêmes profils de charge.

## 16.9 Corréler les indicateurs

Supposons qu'une application devienne lente.

Vous constatez :

- Une hausse de la charge système.
- Une augmentation du temps de réponse.
- Des processus attendant des opérations de stockage.

Il peut être tentant d'augmenter la capacité CPU immédiatement. Pourtant, si le problème provient du stockage, cette modification risque de ne rien résoudre.

Le diagnostic doit relier les symptômes aux indicateurs disponibles.

## 16.10 Atelier de performance

Exécutez :

```bash
uptime
free -h
df -h
ip -s link
ps -eo pid,user,%cpu,%mem,stat,comm --sort=-%cpu | head
```

Notez les résultats et expliquez :

1. Quelle est la charge moyenne ?
2. Quelle quantité de mémoire est disponible ?
3. Quel système de fichiers utilise le plus d'espace ?
4. Quels processus consomment le plus de CPU dans cet aperçu ?
5. Quelles interfaces présentent une activité réseau ?

Les résultats peuvent varier fortement d'une machine à l'autre.


# 17. Sécurisation opérationnelle d'un serveur

La sécurité d'un serveur Linux dépend de plusieurs couches : comptes, permissions, configuration des services, réseau, mises à jour, sauvegardes et surveillance.

Aucune commande isolée ne garantit une sécurité complète.

## 17.1 Appliquer le principe du moindre privilège

Chaque compte et service devrait disposer uniquement des droits nécessaires à sa fonction.

Cela implique notamment :

- Éviter l'utilisation permanente de `root`.
- Limiter les règles `sudo`.
- Séparer les comptes d'administration et d'usage quotidien lorsque cela est approprié.
- Réduire les services inutiles.
- Limiter les permissions sur les fichiers sensibles.
- Vérifier les comptes et clés qui ne sont plus nécessaires.

## 17.2 Réduire la surface d'exposition

Un serveur n'a pas besoin d'écouter sur tous les ports pour fonctionner.

Examinez les sockets en écoute :

```bash
ss -tuln
```

Puis déterminez :

- Quel service utilise chaque port.
- Si le service est nécessaire.
- Sur quelles adresses il écoute.
- Qui doit pouvoir y accéder.
- Si les règles de pare-feu correspondent aux besoins.

N'arrêtez pas un service uniquement parce que son nom est inconnu. Identifiez d'abord sa fonction et ses dépendances.

## 17.3 Maintenir le système à jour

Les mises à jour corrigent des problèmes connus, notamment des vulnérabilités.

Appliquez une stratégie adaptée :

1. Identifier la distribution et sa version.
2. Consulter les mises à jour disponibles.
3. Prévoir les dépendances et interruptions possibles.
4. Sauvegarder les données importantes.
5. Appliquer les changements prévus.
6. Vérifier les services et le fonctionnement.
7. Documenter les résultats.

## 17.4 Sécuriser les clés et secrets

Les clés privées, les mots de passe et les jetons d'accès doivent être protégés.

Évitez notamment :

- De placer des secrets dans des scripts lisibles par tous.
- De stocker des mots de passe directement dans les commandes.
- De publier des journaux sans les examiner.
- De distribuer des clés privées à plusieurs utilisateurs.
- De donner des permissions trop larges aux fichiers sensibles.

## 17.5 Examiner les comptes inutiles

Utilisez les mécanismes de gestion des comptes pour identifier les comptes qui ne sont plus nécessaires.

Avant toute désactivation ou suppression :

- Vérifiez le propriétaire des fichiers.
- Examinez les services associés.
- Contrôlez les tâches planifiées.
- Vérifiez les moyens d'authentification.
- Tenez compte des obligations de conservation.
- Préparez une procédure de retour arrière si la désactivation est réversible.

## 17.6 Contrôler les journaux

Surveillez les messages concernant :

- Les erreurs de service.
- Les échecs d'authentification.
- Les changements de configuration.
- Les problèmes de stockage.
- Les erreurs réseau.
- Les arrêts inattendus.

Une activité inhabituelle n'est pas automatiquement malveillante, mais elle mérite d'être corrélée avec le contexte.

## 17.7 Éviter les erreurs de sécurité courantes

Évitez :

- De donner des permissions globales excessives.
- De désactiver les protections pour résoudre rapidement une erreur.
- De modifier les règles de pare-feu sans préparer la conservation de l'accès.
- De supprimer les journaux pour masquer une alerte d'espace disque.
- De copier des scripts inconnus depuis des sources non vérifiées.
- De lancer des tâches de maintenance sans journaliser les résultats.
- De supposer qu'une sauvegarde est fiable sans avoir testé une restauration.

## 17.8 Checklist minimale de sécurisation

Pour une revue initiale d'un serveur de test, vérifiez :

```text
[ ] Comptes et groupes connus
[ ] Privilèges administratifs justifies
[ ] Permissions des fichiers sensibles
[ ] Services inutiles identifies
[ ] Ports en ecoute compris
[ ] Regles de pare-feu examinees
[ ] Acces SSH testes et controles
[ ] Mises a jour planifiees
[ ] Journaux consultables
[ ] Sauvegardes disponibles
[ ] Restauration testee
[ ] Procedure de retour arriere documentee
```

Cette liste fournit un point de départ, pas une certification de sécurité.


# 18. Méthode professionnelle de résolution d'incidents

Les incidents ne se résolvent pas tous de la même façon. Il faut construire des hypothèses et les vérifier avec des éléments observables.

## 18.1 Définir le symptôme

Une formulation vague telle que « Linux ne marche plus » ne fournit pas assez d'informations.

Essayez de préciser :

- Quel service est affecté ?
- Depuis quand ?
- Quels utilisateurs sont concernés ?
- Le problème est-il constant ou intermittent ?
- Le système est-il local ou distant ?
- Quelles modifications ont été réalisées récemment ?
- Quel message d'erreur apparaît ?

## 18.2 Distinguer le symptôme de la cause

Exemple :

**Symptôme :** le site Web ne répond pas.

Causes possibles :

- Le serveur Web est arrêté.
- Le serveur manque de mémoire.
- Le port n'écoute pas.
- Le pare-feu bloque la connexion.
- La route est incorrecte.
- Le stockage est plein.
- La configuration de l'application est invalide.
- Une dépendance externe est indisponible.

Le même symptôme peut donc provenir de problèmes très différents.

## 18.3 Construire un arbre de diagnostic

```text
Le site Web ne repond pas
             |
             v
Le serveur est-il accessible au niveau IP ?
       |                     |
      Non                   Oui
       |                     |
       v                     v
Route, lien, DNS       Le port est-il accessible ?
ou filtrage                  |
                    +--------+--------+
                    |                 |
                   Non               Oui
                    |                 |
                    v                 v
             Socket, pare-feu   Reponse applicative
             ou service              |
                                +-----+-----+
                                |           |
                               OK          Erreur
                                |           |
                                v           v
                           Incident     Configuration,
                           termine      dependances,
                                        journaux
```

Cet arbre est volontairement simple. Il sert à organiser les investigations plutôt qu'à remplacer les tests appropriés.

## 18.4 Contrôler le service

Exemple pour un service connu :

```bash
systemctl status nom-du-service
```

Puis :

```bash
journalctl -u nom-du-service -n 100
```

Examiner également le port si le service doit écouter sur le réseau :

```bash
ss -tuln
```

Les commandes exactes doivent correspondre à l'unité et au service réellement installés.

## 18.5 Contrôler le stockage

```bash
df -h
```

Puis :

```bash
df -i
```

`df -i` examine notamment l'utilisation des inodes lorsqu'ils sont pertinents pour le système de fichiers concerné.

Un système de fichiers peut rencontrer une pénurie d'inodes même lorsque l'espace exprimé en octets semble encore disponible.

Pour repérer des répertoires volumineux :

```bash
du -sh /var/log
```

Adaptez le chemin au point de montage et à l'application concernés.

## 18.6 Contrôler les changements récents

Les incidents peuvent apparaître après :

- Une mise à jour.
- Un redémarrage.
- Une modification de configuration.
- Un changement de permission.
- Une extension du stockage.
- Une modification du pare-feu.
- Un changement DNS.

Il ne faut pas conclure automatiquement que le dernier changement est la cause. Il constitue néanmoins un point de départ utile pour établir la chronologie.

## 18.7 Planifier un retour arrière

Avant une modification sensible, définissez :

- L'état initial.
- Le fichier ou service modifié.
- La sauvegarde disponible.
- Les commandes de retour arrière.
- Les résultats attendus.
- Les critères qui indiquent que l'intervention a réussi.
- Les conditions qui imposeraient l'annulation.

Le retour arrière doit être réalisable dans le contexte réel d'exploitation.

## 18.8 Rédiger un compte rendu d'incident

Une structure simple peut être utilisée :

```text
Titre :
Date et heure :

Symptome :
Services ou utilisateurs affectes :

Contexte :
Dernieres modifications connues :

Constats :
Commandes utilisees :
Messages importants :

Cause identifiee :
Correction appliquee :

Tests de validation :
Resultat :

Actions de prevention :
Responsable et suivi :
```

Un compte rendu utile distingue clairement les faits constatés des hypothèses.


# 19. Travaux pratiques guidés

Les travaux pratiques suivants doivent être réalisés dans une machine virtuelle ou un système de test.

## TP 1 — Gestion des comptes et des groupes

### Objectifs

- Créer un groupe.
- Créer un compte.
- Ajouter le compte à un groupe.
- Vérifier l'appartenance.

### Étape 1 : créer un groupe de test

```bash
sudo groupadd equipe-lab
```

### Étape 2 : créer un utilisateur de test

```bash
sudo useradd -m -s /bin/bash utilisateur-lab
sudo passwd utilisateur-lab
```

### Étape 3 : ajouter l'utilisateur au groupe

```bash
sudo usermod -aG equipe-lab utilisateur-lab
```

### Étape 4 : vérifier

```bash
id utilisateur-lab
getent group equipe-lab
```

### Questions

1. À quoi sert le GID ?
2. Pourquoi `-aG` est-il important ?
3. Pourquoi une session déjà ouverte peut-elle ne pas refléter immédiatement le nouveau groupe ?
4. Pourquoi faut-il utiliser un compte de test ?

### Validation

Le compte doit exister et être associé au groupe attendu.

Ne supprimez pas le compte avant d'avoir identifié les fichiers et les autres ressources qu'il peut posséder.


## TP 2 — Permissions avancées et partage

### Objectifs

- Créer un répertoire partagé.
- Associer un groupe.
- Comprendre le setgid.
- Examiner les permissions.

### Étape 1 : créer le répertoire

```bash
sudo mkdir -p /srv/equipe-lab
```

### Étape 2 : associer le groupe

```bash
sudo chown root:equipe-lab /srv/equipe-lab
```

### Étape 3 : appliquer les permissions

```bash
sudo chmod 2770 /srv/equipe-lab
```

### Étape 4 : vérifier

```bash
ls -ld /srv/equipe-lab
```

### Questions

1. Que représente le premier `2` de `2770` ?
2. Pourquoi le propriétaire et le groupe disposent-ils de droits différents des autres utilisateurs ?
3. Pourquoi faut-il vérifier également les ACL si le résultat d'accès est inattendu ?

### Validation

Vous devez pouvoir expliquer la signification des permissions et le rôle du groupe.


## TP 3 — Diagnostic d'un service

### Objectifs

- Examiner l'état d'une unité.
- Consulter ses journaux.
- Identifier ses ports en écoute.

Choisissez une unité existante et non critique.

### Étape 1 : examiner l'état

```bash
systemctl status nom-du-service
```

### Étape 2 : consulter les journaux

```bash
journalctl -u nom-du-service -n 50
```

### Étape 3 : examiner les sockets

```bash
ss -tuln
```

### Étape 4 : rédiger un constat

Répondez :

- L'unité existe-t-elle ?
- Est-elle active ?
- Est-elle activée au démarrage ?
- Quels messages importants apparaissent ?
- Le service utilise-t-il un port réseau ?
- Les résultats sont-ils cohérents avec son rôle ?

Ne redémarrez pas automatiquement l'unité. Le TP porte d'abord sur l'observation.


## TP 4 — Diagnostic du stockage

### Objectifs

- Examiner les périphériques.
- Contrôler l'espace.
- Comparer `df` et `du`.
- Comprendre les points de montage.

### Étape 1 : lister les périphériques

```bash
lsblk -f
```

### Étape 2 : examiner l'espace

```bash
df -h
df -i
```

### Étape 3 : examiner un répertoire

```bash
du -sh ~/formation-linux
```

### Étape 4 : inspecter les montages

```bash
findmnt
```

### Questions

1. Pourquoi un périphérique visible dans `lsblk` peut-il ne pas apparaître dans `df` ?
2. Quelle différence existe entre l'espace disponible et les inodes disponibles ?
3. Pourquoi ne faut-il pas formater un périphérique avant de confirmer son identité ?


## TP 5 — Sauvegarde et restauration

### Objectifs

- Créer une archive.
- Examiner son contenu.
- Restaurer dans un répertoire distinct.
- Vérifier les données récupérées.

### Étape 1 : créer des données de test

```bash
mkdir -p ~/lab-sauvegarde/source
echo "Configuration de test" > ~/lab-sauvegarde/source/config.txt
echo "Deuxieme document" > ~/lab-sauvegarde/source/notes.txt
```

### Étape 2 : créer une archive

```bash
tar -czf ~/lab-sauvegarde/archive.tar.gz -C ~/lab-sauvegarde source
```

### Étape 3 : examiner son contenu

```bash
tar -tzf ~/lab-sauvegarde/archive.tar.gz
```

### Étape 4 : extraire dans un répertoire distinct

```bash
mkdir -p ~/lab-sauvegarde/restauration
tar -xzf ~/lab-sauvegarde/archive.tar.gz -C ~/lab-sauvegarde/restauration
```

### Étape 5 : vérifier

```bash
find ~/lab-sauvegarde/restauration -print
cat ~/lab-sauvegarde/restauration/source/config.txt
```

### Validation

Les fichiers restaurés doivent contenir les données attendues.


## TP 6 — Rapport système automatisé

### Objectifs

- Créer un script.
- Vérifier les commandes nécessaires.
- Produire un rapport.
- Journaliser le résultat.

Créez un fichier `rapport-lab.sh` avec le contenu suivant :

```bash
#!/usr/bin/env bash

set -u
set -o pipefail

RAPPORT="$HOME/rapport-lab.txt"

if ! command -v df >/dev/null 2>&1; then
    echo "ERREUR : df est indisponible." >&2
    exit 1
fi

if ! command -v free >/dev/null 2>&1; then
    echo "ERREUR : free est indisponible." >&2
    exit 1
fi

if ! {
    echo "Rapport systeme"
    date
    echo
    echo "Noyau :"
    uname -r
    echo
    echo "Memoire :"
    free -h
    echo
    echo "Stockage :"
    df -h
} > "$RAPPORT"; then
    echo "ERREUR : impossible de produire le rapport." >&2
    exit 1
fi

echo "Rapport cree : $RAPPORT"
exit 0
```

Rendez-le exécutable :

```bash
chmod u+x rapport-lab.sh
```

Exécutez-le :

```bash
./rapport-lab.sh
```

Vérifiez le résultat :

```bash
cat ~/rapport-lab.txt
```

Le script produit un rapport dans le répertoire personnel.

Pour une utilisation professionnelle, on pourrait ajouter une gestion des horodatages, une politique de conservation, un contrôle des erreurs plus détaillé et une stratégie de journalisation.


# 20. Exercices d'évaluation corrigés

Essayez de répondre seul avant de consulter les corrections.

## Exercice 1 — Identifiants

**Question :** quelle différence existe entre UID et GID ?

**Correction :** l'UID identifie un utilisateur. Le GID identifie un groupe.

## Exercice 2 — Groupe supplémentaire

**Question :** pourquoi utilise-t-on souvent `usermod -aG groupe utilisateur` plutôt que `usermod -G groupe utilisateur` ?

**Correction :** `-aG` demande l'ajout du groupe supplémentaire sans remplacer la liste existante. Avec une utilisation incorrecte de `-G` sans `-a`, d'autres appartenances peuvent être retirées.

## Exercice 3 — Umask

**Question :** quel est le résultat classique de la création d'un fichier ordinaire avec une base `666` et un umask `027` ?

**Correction :** le résultat habituel est `640`, soit `rw-r-----`, en supposant un comportement standard du programme créateur.

## Exercice 4 — Setgid

**Question :** que permet généralement le mode `2770` sur un répertoire ?

**Correction :** il accorde `rwx` au propriétaire et au groupe, aucune permission classique aux autres, et active le bit setgid sur le répertoire. Ce bit favorise l'héritage du groupe associé pour les nouvelles entrées.

## Exercice 5 — ACL

**Question :** à quoi servent les ACL ?

**Correction :** elles permettent de définir des permissions supplémentaires pour des utilisateurs et groupes qui ne sont pas directement couverts par les trois catégories classiques.

## Exercice 6 — Processus

**Question :** pourquoi un processus en état `D` peut-il nécessiter un diagnostic du stockage ?

**Correction :** cet état correspond souvent à une attente non interruptible dans le noyau, parfois liée à une entrée-sortie. Il faut examiner le contexte, le stockage et les messages disponibles.

## Exercice 7 — Service

**Question :** quelle différence existe entre `systemctl start` et `systemctl enable` ?

**Correction :** `start` demande le démarrage immédiat de l'unité ; `enable` configure son activation automatique selon les mécanismes de démarrage de systemd. Ces deux actions ne sont pas équivalentes.

## Exercice 8 — Rechargement

**Question :** `systemctl reload nginx` fonctionne-t-il obligatoirement pour tous les services ?

**Correction :** non. L'unité et l'application doivent prendre en charge le rechargement.

## Exercice 9 — Journaux

**Question :** comment consulter les derniers messages d'un service nommé `nginx` ?

**Correction :**

```bash
journalctl -u nginx -n 100
```

Le nom de l'unité doit correspondre au service réel.

## Exercice 10 — Espace disque

**Question :** quelle différence existe entre `df -h` et `du -sh` ?

**Correction :** `df` examine l'espace des systèmes de fichiers, tandis que `du` estime l'espace associé aux fichiers et répertoires parcourus.

## Exercice 11 — Stockage

**Question :** pourquoi est-il dangereux de lancer une commande de formatage sans identifier précisément le périphérique ?

**Correction :** une erreur de périphérique peut détruire les données d'un disque ou d'une partition autre que celle prévue.

## Exercice 12 — Sauvegarde

**Question :** pourquoi une archive créée ne suffit-elle pas à prouver qu'une stratégie de sauvegarde fonctionne ?

**Correction :** il faut également vérifier l'intégrité, le contenu, les permissions nécessaires et la capacité à restaurer les données dans un environnement adapté.

## Exercice 13 — Réseau

**Question :** que peut signifier le fait qu'un serveur écoute sur le port attendu mais reste inaccessible depuis un autre hôte ?

**Correction :** le problème peut se situer au niveau du routage, du pare-feu, de l'adresse d'écoute, des règles réseau ou du chemin de retour. Il faut examiner ces éléments.

## Exercice 14 — SSH

**Question :** pourquoi faut-il tester une nouvelle connexion SSH avant de fermer une session administrative existante après une modification ?

**Correction :** si la nouvelle configuration bloque l'authentification ou la connexion, la session existante peut être le seul accès disponible pour corriger le problème.

## Exercice 15 — Pare-feu

**Question :** pourquoi une règle autorisant un port ne garantit-elle pas la disponibilité du service ?

**Correction :** il faut aussi qu'un programme écoute effectivement sur le port et que les autres couches du chemin réseau permettent la communication.

## Exercice 16 — cron

**Question :** pourquoi une commande fonctionnant dans un terminal peut-elle échouer lorsqu'elle est planifiée ?

**Correction :** l'environnement d'exécution peut être différent, notamment pour `PATH`, les variables, le répertoire courant, les permissions et l'accès aux fichiers.

## Exercice 17 — Script

**Question :** quelle est la différence entre `bash -n script.sh` et l'exécution normale du script ?

**Correction :** `bash -n` examine la syntaxe sans exécuter normalement les instructions. Il ne détecte pas toutes les erreurs de logique.

## Exercice 18 — Performances

**Question :** une charge système élevée signifie-t-elle automatiquement que le CPU est saturé ?

**Correction :** non. La charge peut aussi refléter des tâches en attente, notamment des attentes liées aux entrées-sorties. Elle doit être interprétée avec les autres indicateurs.

## Exercice 19 — Diagnostic

**Question :** pourquoi faut-il distinguer un symptôme d'une cause ?

**Correction :** plusieurs problèmes différents peuvent produire le même symptôme. Identifier la cause probable permet d'appliquer une correction adaptée au lieu de modifier le système au hasard.

## Exercice 20 — Retour arrière

**Question :** que faut-il préparer avant une modification sensible ?

**Correction :** il faut identifier l'état initial, sauvegarder les éléments concernés, définir les commandes de retour arrière, prévoir les tests de validation et établir les conditions qui imposeraient l'annulation.


# 21. Fiche de référence des commandes

Cette section rassemble les commandes importantes étudiées dans le cours.

## 21.1 Informations système

| Commande | Utilité |
|---|---|
| `cat /etc/os-release` | Identifier la distribution |
| `uname -r` | Afficher la version du noyau |
| `uname -m` | Afficher l'architecture |
| `lscpu` | Examiner le processeur |
| `uptime` | Examiner la durée de fonctionnement et la charge |
| `free -h` | Examiner la mémoire et le swap |
| `ulimit -a` | Examiner certaines limites du Shell |

## 21.2 Comptes et groupes

| Commande | Utilité |
|---|---|
| `id utilisateur` | Examiner les identifiants et groupes |
| `getent passwd utilisateur` | Examiner les informations du compte |
| `getent group groupe` | Examiner les informations d'un groupe |
| `groupadd groupe` | Créer un groupe lorsque cela est autorisé |
| `useradd -m utilisateur` | Créer un compte selon les options choisies |
| `usermod -aG groupe utilisateur` | Ajouter un groupe supplémentaire |
| `passwd utilisateur` | Gérer le mot de passe du compte |
| `sudo -l` | Examiner les privilèges sudo applicables |
| `visudo` | Modifier les règles sudo avec validation de syntaxe |

## 21.3 Permissions et ACL

| Commande | Utilité |
|---|---|
| `ls -l` | Examiner les permissions classiques |
| `chmod 640 fichier` | Définir les permissions classiques |
| `chown utilisateur:groupe fichier` | Modifier le propriétaire ou le groupe |
| `umask` | Afficher le masque de création courant |
| `getfacl fichier` | Examiner les ACL |
| `setfacl -m u:alice:rw fichier` | Ajouter ou modifier une entrée ACL |
| `stat fichier` | Examiner les métadonnées |

## 21.4 Processus et ressources

| Commande | Utilité |
|---|---|
| `ps -ef` | Examiner les processus |
| `pgrep -a nom` | Rechercher des processus |
| `top` | Surveiller les ressources |
| `nice -n valeur commande` | Lancer une commande avec une valeur nice |
| `renice valeur -p PID` | Modifier la valeur nice d'un processus |
| `kill -TERM PID` | Demander la terminaison d'un processus |
| `uptime` | Examiner la charge moyenne |
| `vmstat 1 5` | Examiner certaines statistiques système |
| `iostat -xz 1 5` | Examiner les statistiques d'entrées-sorties si l'outil est disponible |

## 21.5 Services et journaux

| Commande | Utilité |
|---|---|
| `systemctl status service` | Examiner l'état d'un service |
| `systemctl start service` | Demander le démarrage |
| `systemctl stop service` | Demander l'arrêt |
| `systemctl restart service` | Demander un redémarrage |
| `systemctl reload service` | Demander un rechargement si pris en charge |
| `systemctl enable service` | Configurer l'activation automatique |
| `systemctl is-active service` | Examiner l'état courant |
| `systemctl is-enabled service` | Examiner l'activation |
| `systemctl --failed` | Lister les unités en échec |
| `journalctl -b` | Consulter les messages du démarrage courant |
| `journalctl -u service` | Consulter les journaux d'une unité |
| `journalctl -f` | Suivre les nouveaux messages |

## 21.6 Stockage et sauvegardes

| Commande | Utilité |
|---|---|
| `lsblk -f` | Examiner les périphériques de stockage et systèmes de fichiers |
| `blkid` | Examiner les identifiants de systèmes de fichiers |
| `df -h` | Examiner l'espace disponible |
| `df -i` | Examiner l'utilisation des inodes |
| `du -sh repertoire` | Estimer l'espace utilisé |
| `findmnt` | Examiner les montages |
| `mount` | Monter un système de fichiers selon la syntaxe |
| `umount chemin` | Demander le démontage |
| `tar -czf archive.tar.gz dossier` | Créer une archive compressée |
| `tar -tzf archive.tar.gz` | Lister le contenu d'une archive gzip |
| `rsync -a source/ destination/` | Synchroniser des fichiers selon les options |

## 21.7 Réseau et SSH

| Commande | Utilité |
|---|---|
| `ip addr` | Examiner les adresses des interfaces |
| `ip link` | Examiner l'état des interfaces |
| `ip route` | Examiner les routes |
| `ip route get adresse` | Examiner la route choisie vers une destination |
| `ip -s link` | Examiner les statistiques des interfaces |
| `getent hosts nom` | Demander la résolution d'un nom |
| `ss -tuln` | Examiner certaines sockets en écoute |
| `ping -c 4 adresse` | Tester certains aspects de la connectivité |
| `ssh-keygen -t ed25519` | Générer une paire de clés SSH |
| `ssh-copy-id utilisateur@serveur` | Installer une clé publique si l'outil est disponible |
| `sshd -t` | Tester la syntaxe de configuration du serveur SSH |

## 21.8 Planification et scripts

| Commande | Utilité |
|---|---|
| `crontab -l` | Afficher la crontab utilisateur |
| `crontab -e` | Éditer la crontab utilisateur |
| `bash -n script.sh` | Vérifier la syntaxe d'un script |
| `command -v commande` | Examiner la résolution d'un nom de commande |
| `echo $?` | Afficher le code de retour précédent dans le Shell |


# 22. Challenge final — Exploitation d'un serveur Linux

## 22.1 Scénario

Vous êtes chargé d'assurer le suivi opérationnel d'un petit serveur Linux de laboratoire.

Le serveur doit disposer d'un environnement de travail organisé, de permissions adaptées, d'un journal de contrôle et d'un script qui vérifie certains aspects de son état.

Le challenge consiste à mettre en œuvre une procédure d'administration vérifiable, sans prétendre réaliser une supervision complète.

## 22.2 Objectifs

Vous devez :

1. Créer une arborescence de travail.
2. Préparer des fichiers de documentation.
3. Créer un journal d'exploitation.
4. Appliquer des permissions adaptées.
5. Produire un rapport système.
6. Vérifier l'espace disque.
7. Vérifier la présence d'outils requis.
8. Enregistrer le résultat de la vérification.
9. Tester le code de retour du script.
10. Documenter les limites de la solution.

## 22.3 Conditions de sécurité

Le challenge doit être réalisé dans votre répertoire personnel.

Le chemin de travail est :

```text
~/serveur-lab
```

N'utilisez pas de privilèges administrateur pour cette partie, sauf si un exercice indépendant l'exige.

Ne modifiez pas le pare-feu, les services système ou les points de montage pour réussir le challenge.

## 22.4 Étape 1 — Créer l'arborescence

Créez :

```text
serveur-lab/
|
+-- documents/
|
+-- scripts/
|
+-- journaux/
|
+-- rapports/
|
+-- sauvegardes/
```

Vérifiez avec `find`.

## 22.5 Étape 2 — Créer les documents

Dans `documents/`, créez trois fichiers :

```text
architecture.txt
maintenance.txt
securite.txt
```

Ils doivent expliquer respectivement :

- Les principaux composants du système.
- L'importance des opérations de maintenance.
- Le rôle des permissions et des contrôles d'accès.

Chaque document doit contenir au moins deux lignes.

## 22.6 Étape 3 — Préparer le journal

Dans `journaux/`, créez :

```text
exploitation.log
```

Le journal doit mentionner :

```text
Initialisation de l'espace de travail
Creation des documents
Verification initiale
```

Ajoutez ensuite une ligne confirmant que les fichiers ont été contrôlés.

## 22.7 Étape 4 — Définir les permissions

Appliquez le mode `644` aux documents.

Pour le journal, utilisez un mode qui accorde la lecture et l'écriture au propriétaire et aucune permission classique au groupe et aux autres.

Vérifiez avec `ls -l`.

Expliquez les différences entre les deux choix.

## 22.8 Étape 5 — Construire le script de contrôle

Dans `scripts/`, créez :

```text
controle-systeme.sh
```

Le script doit :

- Définir les chemins du projet et du journal.
- Vérifier que le répertoire du projet existe.
- Vérifier la présence des répertoires de travail essentiels.
- Vérifier les trois documents attendus.
- Vérifier la présence des commandes `df` et `free`.
- Créer un rapport dans `rapports/`.
- Ajouter une ligne de résultat au journal.
- Afficher une erreur compréhensible si un contrôle échoue.
- Terminer avec un code de sortie cohérent.

Le script doit utiliser des variables et des conditions.

## 22.9 Étape 6 — Vérifier le script

Contrôlez la syntaxe :

```bash
bash -n ~/serveur-lab/scripts/controle-systeme.sh
```

Puis rendez-le exécutable :

```bash
chmod u+x ~/serveur-lab/scripts/controle-systeme.sh
```

Exécutez-le :

```bash
~/serveur-lab/scripts/controle-systeme.sh
```

Examinez le rapport et le journal.

## 22.10 Étape 7 — Tester un scénario d'échec

Dans votre espace de test, choisissez une manière contrôlée de vérifier que le script signale un fichier manquant.

Par exemple, vous pouvez renommer temporairement un document attendu, exécuter le script, vérifier le message et le code de sortie, puis rétablir immédiatement le nom initial.

Ne supprimez pas de fichiers personnels pour réaliser le test.

Le script doit signaler l'échec et ne pas annoncer un succès complet lorsque les documents requis sont absents.

## 22.11 Étape 8 — Documenter

Rédigez un court compte rendu précisant :

- La structure créée.
- Les permissions retenues.
- Les contrôles exécutés.
- Le résultat normal.
- Le résultat du test d'échec.
- Les limites du script.
- Les améliorations que vous proposeriez.

## 22.12 Barème

| Compétence | Points |
|---|---:|
| Organisation de l'arborescence | 10 |
| Documents et journal | 10 |
| Permissions adaptées | 10 |
| Contrôles de chemins | 15 |
| Vérification des dépendances | 10 |
| Génération du rapport | 15 |
| Gestion des erreurs et codes de retour | 15 |
| Test d'échec | 10 |
| Documentation des limites | 5 |
| **Total** | **100** |

Une bonne solution doit produire des résultats vérifiables et ne pas annoncer le succès lorsque des contrôles essentiels ont échoué.


# 23. Correction détaillée du challenge

Cette correction fournit une implémentation de référence. Essayez d'abord de réaliser le challenge vous-même.

## 23.1 Créer l'arborescence

```bash
mkdir -p ~/serveur-lab/documents
mkdir -p ~/serveur-lab/scripts
mkdir -p ~/serveur-lab/journaux
mkdir -p ~/serveur-lab/rapports
mkdir -p ~/serveur-lab/sauvegardes
```

Vérifiez :

```bash
find ~/serveur-lab -print
```

## 23.2 Créer les documents

```bash
echo "Le noyau gere des ressources et des mecanismes fondamentaux du systeme." \
    > ~/serveur-lab/documents/architecture.txt

echo "La maintenance permet de reduire les risques et de conserver un systeme operationnel." \
    > ~/serveur-lab/documents/maintenance.txt

echo "Les permissions limitent les acces et les operations autorisees." \
    > ~/serveur-lab/documents/securite.txt
```

Ajoutez une deuxième ligne à chaque fichier :

```bash
echo "Les outils d'administration permettent d'observer et de diagnostiquer la machine." \
    >> ~/serveur-lab/documents/architecture.txt

echo "Les mises a jour doivent etre preparees et verifiees." \
    >> ~/serveur-lab/documents/maintenance.txt

echo "Les privileges doivent etre accordes selon le besoin." \
    >> ~/serveur-lab/documents/securite.txt
```

Vérifiez :

```bash
cat ~/serveur-lab/documents/architecture.txt
cat ~/serveur-lab/documents/maintenance.txt
cat ~/serveur-lab/documents/securite.txt
```

## 23.3 Créer le journal

```bash
echo "Initialisation de l'espace de travail" \
    > ~/serveur-lab/journaux/exploitation.log

echo "Creation des documents" \
    >> ~/serveur-lab/journaux/exploitation.log

echo "Verification initiale" \
    >> ~/serveur-lab/journaux/exploitation.log

echo "Documents controles" \
    >> ~/serveur-lab/journaux/exploitation.log
```

## 23.4 Appliquer les permissions

```bash
chmod 644 ~/serveur-lab/documents/architecture.txt
chmod 644 ~/serveur-lab/documents/maintenance.txt
chmod 644 ~/serveur-lab/documents/securite.txt

chmod 600 ~/serveur-lab/journaux/exploitation.log
```

Vérifiez :

```bash
ls -l ~/serveur-lab/documents
ls -l ~/serveur-lab/journaux/exploitation.log
```

## 23.5 Script de contrôle complet

Créez :

```bash
nano ~/serveur-lab/scripts/controle-systeme.sh
```

Collez le code suivant :

```bash
#!/usr/bin/env bash

set -u
set -o pipefail

PROJET="$HOME/serveur-lab"
DOCUMENTS="$PROJET/documents"
JOURNAL="$PROJET/journaux/exploitation.log"
RAPPORT="$PROJET/rapports/rapport-systeme.txt"

erreur() {
    echo "ERREUR : $*" >&2
    exit 1
}

echo "======================================"
echo " CONTROLE DU SERVEUR DE LABORATOIRE"
echo "======================================"

# Verifier le repertoire principal.
if [ ! -d "$PROJET" ]; then
    erreur "Le repertoire principal est absent."
fi

# Verifier les repertoires indispensables.
for repertoire in documents scripts journaux rapports sauvegardes; do
    if [ ! -d "$PROJET/$repertoire" ]; then
        erreur "Repertoire manquant : $repertoire"
    fi
done

# Verifier les documents attendus.
for fichier in architecture.txt maintenance.txt securite.txt; do
    if [ ! -f "$DOCUMENTS/$fichier" ]; then
        erreur "Document manquant : $fichier"
    fi
done

# Verifier les commandes requises.
for commande in date uname df free; do
    if ! command -v "$commande" >/dev/null 2>&1; then
        erreur "Commande requise indisponible : $commande"
    fi
done

# Verifier la presence du journal.
if [ ! -f "$JOURNAL" ]; then
    erreur "Le journal est absent."
fi

# Generer le rapport.
if ! {
    echo "RAPPORT SYSTEME"
    echo "Date : $(date)"
    echo "Utilisateur : $(whoami)"
    echo "Noyau : $(uname -r)"
    echo
    echo "MEMOIRE"
    free -h
    echo
    echo "STOCKAGE"
    df -h
} > "$RAPPORT"; then
    erreur "Impossible de generer le rapport."
fi

# Verifier que le rapport existe.
if [ ! -s "$RAPPORT" ]; then
    erreur "Le rapport est absent ou vide."
fi

# Ajouter un evenement au journal.
if ! echo "$(date '+%F %T') : controle systeme termine" >> "$JOURNAL"; then
    erreur "Impossible d'ecrire dans le journal."
fi

echo
echo "Rapport cree : $RAPPORT"
echo "Journal mis a jour : $JOURNAL"
echo "Controle termine avec succes."

exit 0
```

## 23.6 Comprendre le script

### Les variables

```bash
PROJET="$HOME/serveur-lab"
DOCUMENTS="$PROJET/documents"
JOURNAL="$PROJET/journaux/exploitation.log"
RAPPORT="$PROJET/rapports/rapport-systeme.txt"
```

Ces variables centralisent les chemins utilisés.

Si le répertoire est déplacé, il devient plus facile d'adapter le script en modifiant la définition du chemin principal et les chemins qui en dépendent.

### La fonction `erreur`

```bash
erreur() {
    echo "ERREUR : $*" >&2
    exit 1
}
```

Cette fonction affiche un message sur la sortie d'erreur et termine le script avec un code de sortie non nul.

L'utilisation d'une fonction permet de rendre les contrôles plus lisibles.

### La boucle de vérification des répertoires

```bash
for repertoire in documents scripts journaux rapports sauvegardes; do
```

Le script parcourt une liste de répertoires attendus.

Pour chacun, il vérifie l'existence du chemin.

S'il manque un répertoire, la fonction `erreur` interrompt l'exécution.

### La vérification des documents

```bash
for fichier in architecture.txt maintenance.txt securite.txt; do
```

Le script vérifie la présence des trois fichiers de documentation.

Le test `-f` indique si le chemin désigne un fichier ordinaire accessible selon le contexte.

La présence d'un fichier ne garantit pas que son contenu est correct, mais c'est un contrôle de base nécessaire.

### La vérification des dépendances

```bash
for commande in date uname df free; do
```

Le script vérifie que les noms de commandes nécessaires peuvent être résolus par le Shell.

Cette vérification ne garantit pas que chaque commande fonctionnera dans toutes les circonstances. Elle permet cependant de détecter certaines dépendances absentes.

### La génération du rapport

Le bloc :

```bash
if ! {
    ...
} > "$RAPPORT"; then
```

regroupe plusieurs commandes et redirige leur sortie standard vers le fichier de rapport.

La condition vérifie le résultat global de l'opération.

Le script ne garantit pas que toutes les commandes du rapport contiennent des informations complètes dans chaque environnement, mais il contrôle qu'une erreur est signalée par le groupe d'instructions.

### Le contrôle du fichier créé

```bash
if [ ! -s "$RAPPORT" ]; then
```

Le test `-s` vérifie si le fichier existe et possède une taille supérieure à zéro.

Cela ne prouve pas à lui seul que le contenu est exact. Il s'agit d'un contrôle supplémentaire.

### L'écriture du journal

Le script ajoute une ligne horodatée au journal.

Si l'écriture échoue, il se termine avec un code d'erreur.

### Le code final

```bash
exit 0
```

Le code `0` indique que les contrôles prévus ont réussi.

Il ne signifie pas que le serveur est parfaitement sain. Le script n'examine qu'un ensemble limité d'éléments.

## 23.7 Rendre le script exécutable

```bash
chmod u+x ~/serveur-lab/scripts/controle-systeme.sh
```

Vérifiez sa syntaxe :

```bash
bash -n ~/serveur-lab/scripts/controle-systeme.sh
```

Exécutez-le :

```bash
~/serveur-lab/scripts/controle-systeme.sh
```

Examinez les résultats :

```bash
cat ~/serveur-lab/rapports/rapport-systeme.txt
cat ~/serveur-lab/journaux/exploitation.log
```

Vérifiez aussi :

```bash
echo $?
```

Le code doit être `0` si le script a achevé les contrôles prévus sans signaler d'erreur.

## 23.8 Tester un échec contrôlé

Une méthode possible consiste à renommer temporairement un document attendu dans le répertoire de test.

Avant le test, vérifiez le nom :

```bash
ls -l ~/serveur-lab/documents
```

Renommez le document :

```bash
mv ~/serveur-lab/documents/securite.txt ~/serveur-lab/documents/securite-test.txt
```

Exécutez le script :

```bash
~/serveur-lab/scripts/controle-systeme.sh
```

Le script devrait signaler que `securite.txt` manque et terminer avec un code non nul.

Vérifiez ce code immédiatement après le script :

```bash
echo $?
```

Rétablissez ensuite le nom original :

```bash
mv ~/serveur-lab/documents/securite-test.txt ~/serveur-lab/documents/securite.txt
```

Puis exécutez de nouveau le script et vérifiez le résultat.

Ce test démontre que la détection d'un fichier manquant est effectivement exécutée.

## 23.9 Évaluer les limites du script

Le script ne :

- Vérifie pas la disponibilité d'un service particulier.
- Teste pas l'accessibilité d'un port depuis un autre hôte.
- Contrôle pas l'intégrité complète des fichiers.
- Vérifie pas l'état de tous les systèmes de fichiers.
- Détecte pas toutes les causes possibles d'une saturation mémoire.
- Remplace pas une véritable solution de supervision.

Il s'agit d'un outil de contrôle élémentaire. Pour le rendre plus utile, on pourrait ajouter des seuils configurables, une politique de conservation du rapport, une vérification plus poussée des systèmes de fichiers et un système d'alerte.

Toute amélioration doit conserver le principe : **un résultat de contrôle doit correspondre à une vérification réellement effectuée**.


# 24. Checklist de validation des compétences

Utilisez cette checklist pour évaluer votre autonomie en administration Linux intermédiaire.

## Comptes et permissions

- [ ] Je sais examiner les UID et GID.
- [ ] Je sais créer un compte et un groupe de test.
- [ ] Je comprends l'importance de `usermod -aG`.
- [ ] Je sais utiliser les permissions classiques.
- [ ] Je comprends l'umask.
- [ ] Je sais expliquer le rôle du setgid et du sticky bit.
- [ ] Je sais examiner les ACL.
- [ ] Je comprends pourquoi les privilèges doivent être limités.

## Processus et ressources

- [ ] Je sais examiner les processus avec `ps`.
- [ ] Je sais observer les processus avec `top`.
- [ ] Je comprends le rôle du PID et du PPID.
- [ ] Je sais examiner certaines valeurs de priorité.
- [ ] Je comprends les différences entre CPU, mémoire et stockage.
- [ ] Je sais interpréter les indicateurs de charge avec prudence.
- [ ] Je sais examiner la mémoire et le swap.
- [ ] Je comprends qu'un processus en état `D` nécessite un diagnostic contextuel.

## Services et journaux

- [ ] Je sais examiner l'état d'un service systemd.
- [ ] Je sais distinguer démarrage et activation automatique.
- [ ] Je sais consulter les journaux avec `journalctl`.
- [ ] Je sais filtrer les journaux par unité.
- [ ] Je sais rechercher une chronologie.
- [ ] Je sais vérifier une configuration avant d'appliquer un changement.
- [ ] Je sais documenter les résultats d'une intervention.

## Stockage et sauvegardes

- [ ] Je sais utiliser `lsblk -f`.
- [ ] Je comprends le rôle de `blkid`.
- [ ] Je sais interpréter `df -h`.
- [ ] Je sais interpréter `df -i`.
- [ ] Je sais estimer l'espace avec `du`.
- [ ] Je comprends les points de montage.
- [ ] Je sais expliquer le rôle de `/etc/fstab`.
- [ ] Je comprends les notions de volumes physiques, groupes de volumes et volumes logiques.
- [ ] Je sais créer une archive avec `tar`.
- [ ] Je sais examiner le contenu d'une archive.
- [ ] Je sais restaurer des fichiers dans un répertoire de test.
- [ ] Je sais simuler une opération `rsync`.
- [ ] Je comprends pourquoi une sauvegarde doit être testée.

## Réseau et sécurité

- [ ] Je sais examiner les interfaces et les adresses.
- [ ] Je comprends la table de routage.
- [ ] Je sais examiner les sockets en écoute.
- [ ] Je sais distinguer une panne réseau d'une panne applicative.
- [ ] Je comprends le rôle de SSH.
- [ ] Je sais générer une paire de clés SSH.
- [ ] Je comprends les précautions à prendre avant de modifier `sshd_config`.
- [ ] Je comprends le rôle du pare-feu.
- [ ] Je sais pourquoi il faut protéger l'accès distant pendant une modification de règles.

## Automatisation et dépannage

- [ ] Je sais planifier une tâche avec cron.
- [ ] Je comprends le rôle des timers systemd.
- [ ] Je sais écrire un script avec des variables et des conditions.
- [ ] Je sais vérifier la présence des commandes nécessaires.
- [ ] Je comprends les codes de retour.
- [ ] Je sais examiner la syntaxe d'un script avec `bash -n`.
- [ ] Je sais rechercher une cause avant de corriger un symptôme.
- [ ] Je prépare un retour arrière avant une modification sensible.
- [ ] Je sais documenter les faits, hypothèses et résultats d'un incident.


# Conclusion générale

L'administration Linux intermédiaire consiste à passer de l'exécution de commandes simples à une gestion structurée du système.

Il ne suffit plus de savoir qu'une commande existe. Il faut comprendre les informations qu'elle fournit, ses limites, les risques liés à son utilisation et la manière de vérifier le résultat.

Les comptes et permissions définissent les droits. Les processus et services expliquent l'exécution des applications. Les journaux fournissent des informations sur le fonctionnement. Le stockage doit être contrôlé et sauvegardé. Le réseau doit être étudié selon ses différentes couches. Les scripts permettent d'automatiser les contrôles tout en conservant une gestion explicite des erreurs.

Les compétences acquises ici constituent une base solide pour continuer vers :

- L'administration Linux experte.
- L'exploitation de serveurs de production.
- La haute disponibilité.
- La supervision centralisée.
- L'administration de volumes et du stockage avancé.
- L'automatisation avec Ansible.
- La sécurité Linux approfondie.
- L'administration de services réseau.
- Le diagnostic de performances avancé.

La prochaine étape consiste à reprendre les travaux pratiques sans recopier les corrections, puis à adapter le challenge à un serveur de test réel.

**Principe fondamental :** observer avant de modifier, limiter les privilèges, sauvegarder avant les changements sensibles, vérifier après chaque intervention et documenter les résultats.

Fin du cours — Administration Linux avancée, niveau intermédiaire.