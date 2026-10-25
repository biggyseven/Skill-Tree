# Gestion des paquets Linux — Niveau Intermédiaire

> **Fichier :** `packages-intermediaire.md`  
> **Niveau :** Intermédiaire  
> **Domaine :** Administration système Linux, maintenance logicielle et gestion des dépendances  
> **Environnement principal :** Debian et Ubuntu  
> **Environnements complémentaires :** Fedora/RHEL avec DNF/RPM et Arch Linux avec Pacman  
> **Prérequis :** Maîtriser les notions et commandes du cours `packages-debutant.md`.


# Sommaire

1. Positionnement du niveau intermédiaire
2. Architecture de la gestion des paquets
3. Comprendre précisément les versions de paquets
4. Résoudre les dépendances complexes
5. Examiner les transactions avant modification
6. Comprendre les priorités APT et les versions candidates
7. Contrôler les paquets avec `apt-mark`
8. Gérer les paquets retenus et les versions particulières
9. Comprendre les dépôts et leurs priorités
10. Configurer proprement les sources APT
11. Installer et inspecter les paquets locaux
12. Comprendre les états de `dpkg`
13. Réparer une base de paquets incohérente
14. Vérifier et réinstaller les fichiers d'un paquet
15. Maîtriser les suppressions, purges et dépendances résiduelles
16. Gérer les mises à jour en environnement serveur
17. Automatiser les mises à jour de sécurité
18. Comprendre les journaux et l'historique des transactions
19. Diagnostiquer les verrous et les erreurs de gestionnaire
20. Gérer les dépendances et les conflits entre dépôts
21. Préparer un inventaire et un état logiciel reproductible
22. Automatiser les contrôles avec Bash
23. Maintenance avancée avec DNF/RPM
24. Maintenance avancée avec Pacman
25. Bonnes pratiques en production
26. Travaux pratiques guidés
27. Exercices d'application
28. Corrections détaillées des exercices
29. Défi final : maintenance contrôlée d'un serveur
30. Correction détaillée du défi final
31. Checklist de compétences
32. Fiche de révision
33. Glossaire
34. Documentation de référence


# 1. Positionnement du niveau intermédiaire

## 1.1. Ce qui change par rapport au niveau débutant

Au niveau débutant, tu as appris à rechercher, installer, mettre à jour et supprimer des paquets.

Tu as aussi découvert les dépôts, les dépendances, les paquets locaux, les commandes APT et l'interrogation de la base `dpkg`.

Au niveau intermédiaire, tu dois comprendre pourquoi le gestionnaire sélectionne une version plutôt qu'une autre, comment les priorités influencent les choix, comment identifier et réparer un état incohérent et comment préparer une opération de maintenance sans prendre de risques inutiles.

Les situations suivantes font partie du travail d'un administrateur :

- une mise à jour n'est pas proposée alors qu'une version plus récente existe ;
- un paquet reste bloqué à une ancienne version ;
- plusieurs dépôts proposent des versions différentes ;
- une installation de paquet local échoue à cause des dépendances ;
- `dpkg` signale des paquets non configurés ;
- une mise à jour propose de supprimer un composant important ;
- un service ne fonctionne plus après une mise à niveau ;
- un verrou APT empêche une installation ;
- un script de maintenance doit détecter une situation sans modifier le système ;
- plusieurs serveurs doivent être maintenus selon une procédure comparable.

Le but n'est donc plus seulement de connaître une commande, mais de comprendre son effet sur l'ensemble du système.

## 1.2. Méthode de travail

La méthode de maintenance de référence est la suivante :

```text
DEMANDE DE MODIFICATION
          |
          v
IDENTIFIER LE SYSTÈME
          |
          v
EXAMINER LES SOURCES
          |
          v
CONNAÎTRE L'ÉTAT ACTUEL
          |
          v
CONTRÔLER LES VERSIONS
          |
          v
SIMULER LA TRANSACTION
          |
          v
ÉVALUER LES RISQUES
          |
          v
APPLIQUER LA MODIFICATION
          |
          v
VÉRIFIER LES PAQUETS ET SERVICES
          |
          v
CONSERVER UNE TRACE
```

Une installation ou une mise à niveau ne doit pas être considérée comme réussie simplement parce que le gestionnaire a terminé son affichage.

Il faut aussi vérifier l'état enregistré, les fichiers utiles et, si nécessaire, le service qui dépend du paquet.

## 1.3. Environnement de référence

Ce cours utilise principalement les systèmes Debian et Ubuntu.

Les commandes et les exemples supposent que les outils APT et `dpkg` sont disponibles.

Les différences de version, de configuration et de système d'initialisation peuvent modifier certains résultats. Lorsque c'est nécessaire, consulte le manuel local :

```bash
man apt
```

```bash
man apt_preferences
```

```bash
man dpkg
```

```bash
man dpkg-query
```

Pour les environnements RPM et Arch Linux, les équivalences sont étudiées dans des sections dédiées.


# 2. Architecture de la gestion des paquets

## 2.1. Les quatre éléments principaux

La gestion des paquets Debian et Ubuntu repose notamment sur quatre éléments :

1. les dépôts configurés ;
2. les index de paquets disponibles ;
3. la base locale des paquets ;
4. le moteur de résolution et d'installation.

On peut représenter leur relation ainsi :

```text
DÉPÔTS DISTANTS
      |
      v
INDEX DE PAQUETS
      |
      v
APT
 |  \
 |   \--- Analyse des dépendances
 |
 v
DPKG
 |
 +-- Dépaquetage
 +-- Configuration
 +-- Base locale
 |
 v
FICHIERS INSTALLÉS
```

Les dépôts contiennent les paquets et leurs métadonnées. APT exploite les index pour choisir les versions et résoudre les dépendances. `dpkg` réalise les opérations de bas niveau sur les paquets DEB.

## 2.2. Les index APT

Les index décrivent les paquets que les dépôts rendent disponibles.

Ils contiennent notamment des informations sur les versions, les architectures, les dépendances et les descriptions.

La commande :

```bash
sudo apt update
```

actualise ces index selon les sources configurées.

Cette commande ne réalise pas la mise à niveau habituelle de tous les paquets installés.

L'état des index est important : si les index sont périmés, les décisions du gestionnaire peuvent s'appuyer sur des informations qui ne correspondent plus à l'état actuel des dépôts.

## 2.3. La base locale `dpkg`

`dpkg` conserve des informations relatives aux paquets connus localement et à leur état.

Cette base permet notamment d'interroger :

- les paquets installés ;
- leurs versions ;
- leur état de configuration ;
- certains fichiers associés ;
- certaines informations concernant les dépendances.

Il faut distinguer cette base des index distants d'APT.

```text
INDEX APT
    |
    +-- Ce qui est disponible dans les sources connues


BASE DPKG
    |
    +-- Ce qui est enregistré localement
```

Un paquet peut être disponible dans un dépôt sans être installé. Inversement, un paquet installé peut ne plus être proposé par les sources actuelles.

## 2.4. Pourquoi APT est-il généralement préférable à `dpkg` pour les installations ordinaires ?

`dpkg` peut installer un fichier DEB local, mais ne résout pas à lui seul toutes les dépendances en s'appuyant sur les dépôts de la même manière qu'APT.

APT est donc généralement préférable lorsqu'il faut installer, mettre à niveau ou supprimer un logiciel et ses dépendances.

`dpkg` reste particulièrement utile pour consulter l'état d'un paquet, analyser les fichiers enregistrés, diagnostiquer une configuration incomplète ou examiner un paquet local.

## 2.5. Interfaces interactives et scripts

`apt` est conçu pour une utilisation interactive et peut ajuster ses messages ou son comportement de présentation.

Pour les scripts classiques, `apt-get` est souvent préférable :

```bash
apt-get -s upgrade
```

Cette commande simule une opération de mise à niveau dans le contexte local.

La distinction n'implique pas qu'APT soit incapable d'automatisation, mais un script doit privilégier une interface adaptée, analyser les codes de retour et traiter les erreurs explicitement.

Documentation officielle Ubuntu : [Install and manage packages](https://ubuntu.com/server/docs/how-to/software/package-management/).


# 3. Comprendre précisément les versions de paquets

## 3.1. Une version peut contenir plusieurs composants

Dans Debian, une version de paquet peut inclure :

- une époque, ou *epoch* ;
- une version amont ;
- une révision spécifique au paquet Debian.

Exemple fictif :

```text
2:4.8.1-2ubuntu3
```

Cette chaîne peut être décomposée ainsi :

```text
2          : epoch
4.8.1      : version amont
2ubuntu3   : révision du paquet
```

L'époque est facultative. Elle sert notamment à gérer des changements de numérotation qui doivent influencer l'ordre de comparaison des versions.

La révision du paquet est également importante : une distribution peut appliquer des correctifs ou adapter un logiciel sans publier une nouvelle version amont de la même manière que le projet original.

## 3.2. Pourquoi ne faut-il pas comparer les versions lexicalement ?

Les versions de paquets doivent être comparées avec les règles du gestionnaire, pas simplement comme des chaînes de caractères.

Par exemple, une comparaison textuelle peut ordonner les nombres de façon inattendue parce que les caractères sont comparés individuellement.

Pour Debian, il vaut mieux utiliser les outils de comparaison de versions du système, par exemple :

```bash
dpkg --compare-versions 1.9 gt 1.8
echo $?
```

Le code de retour `0` indique que la comparaison est vraie selon la condition demandée.

Dans cet exemple, `1.9` est plus récent que `1.8` selon les règles de comparaison de versions de `dpkg`.

Pour comparer deux versions dans un script, utilise les opérateurs documentés et évite les comparaisons textuelles improvisées.

## 3.3. Version installée, version candidate et versions disponibles

Ces notions sont différentes.

- **Version installée :** version enregistrée dans la base locale.
- **Version candidate :** version qu'APT sélectionne actuellement comme candidate à l'installation ou à la mise à niveau.
- **Versions disponibles :** versions connues dans les index configurés.

Pour examiner ces informations :

```bash
apt-cache policy curl
```

La sortie peut ressembler à :

```text
curl:
  Installed: 7.x-y
  Candidate: 7.x-z
  Version table:
     7.x-z 500
        500 http://archive.example.invalid stable/main amd64 Packages
 *** 7.x-y 100
        100 /var/lib/dpkg/status
```

Cet exemple est fictif. Les versions, les dépôts et les priorités affichés sur ta machine seront différents.

Il faut lire le tableau complet pour comprendre pourquoi une version est sélectionnée.

## 3.4. Vérifier la version installée

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' curl
```

Cette commande interroge la base locale de `dpkg`.

Elle permet de connaître la version enregistrée et l'architecture du paquet installé.

Pour examiner les versions connues des sources :

```bash
apt-cache policy curl
```

La comparaison des deux résultats aide à déterminer si une mise à jour est disponible et si APT la considère comme candidate.

## 3.5. Pourquoi une version plus récente peut-elle ne pas être sélectionnée ?

Plusieurs raisons sont possibles :

- les index ne sont pas à jour ;
- le dépôt ne propose pas cette version pour cette distribution ;
- le paquet est retenu ;
- une priorité APT favorise une autre version ;
- un dépôt tiers n'est pas configuré ;
- une contrainte de dépendance empêche la sélection ;
- une règle de sélection des versions s'applique ;
- la version récente n'est pas adaptée à l'architecture ou à la suite configurée.

La bonne démarche consiste à examiner les versions et les priorités avant de modifier le système.


# 4. Résoudre les dépendances complexes

## 4.1. Les dépendances ne sont pas uniquement une liste

Une dépendance peut imposer une contrainte de version ou un autre type de relation.

Dans les métadonnées Debian, on peut rencontrer des relations comme :

```text
Depends
Pre-Depends
Recommends
Suggests
Conflicts
Breaks
Provides
Replaces
Enhances
```

Ces champs ne sont pas interchangeables.

Ils permettent aux gestionnaires de déterminer les conditions dans lesquelles un paquet peut être installé, configuré ou remplacé.

## 4.2. Dépendances directes et transitives

Une dépendance directe est déclarée par le paquet lui-même.

Une dépendance transitive est requise indirectement par une autre dépendance.

Exemple :

```text
APPLICATION A
     |
     v
BIBLIOTHÈQUE B
     |
     v
BIBLIOTHÈQUE C
     |
     v
BIBLIOTHÈQUE D
```

Si A dépend de B et que B dépend de C, le gestionnaire peut devoir installer B, C et d'autres composants requis pour que la transaction aboutisse.

L'administrateur n'a pas besoin de calculer manuellement toute cette chaîne : le solveur APT s'en charge à partir des métadonnées.

## 4.3. Examiner les dépendances

Pour un paquet disponible :

```bash
apt-cache depends curl
```

Pour afficher les relations inverses déclarées :

```bash
apt-cache rdepends libcurl4
```

Remplace le nom du paquet par celui qui correspond à ton cas.

Les dépendances inverses peuvent être nombreuses. Elles aident à comprendre l'impact d'une suppression, mais ne remplacent pas le plan de transaction proposé par APT.

## 4.4. Dépendances de version

Une dépendance peut exiger une version minimale, une plage de versions ou une relation particulière.

Un paquet peut donc être disponible tout en étant impossible à installer dans la configuration actuelle.

Exemples de situations :

- une bibliothèque installée est trop ancienne ;
- une nouvelle version d'application exige une autre bibliothèque ;
- une bibliothèque présente entre en conflit avec une autre version ;
- une version particulière n'est disponible que dans un dépôt tiers.

Il faut alors examiner les versions candidates et les sources avant de tenter de forcer l'installation.

## 4.5. Paquets virtuels

Certains paquets déclarent fournir une capacité plutôt qu'un nom de logiciel spécifique.

Par exemple, plusieurs implémentations peuvent déclarer fournir une même capacité virtuelle.

Cela permet à des logiciels de dépendre d'une fonction sans exiger nécessairement un seul paquet concret.

Pour rechercher les fournisseurs d'une capacité, tu peux utiliser les informations de dépendance disponibles et consulter les métadonnées des paquets.

```bash
apt-cache showpkg nom-virtuel
```

Cette commande permet d'examiner certaines informations relatives au paquet ou à la capacité recherchée.

## 4.6. Pourquoi une suppression peut-elle affecter d'autres logiciels ?

Un paquet peut être nécessaire à plusieurs applications.

La suppression d'une bibliothèque ou d'un composant partagé peut donc provoquer la suppression de dépendances ou rendre des logiciels indisponibles.

Avant de confirmer une suppression, examine le plan proposé par APT et les paquets qui seront concernés.

```bash
apt-get -s remove nom-du-paquet
```

La simulation est un outil d'analyse. Elle ne garantit pas que toutes les conditions seront identiques lors de la transaction réelle.

## 4.7. Dépendances et recommandations

APT peut installer certains paquets recommandés, selon sa configuration.

La présence d'une recommandation ne signifie pas nécessairement que le paquet est absolument indispensable.

Il faut comprendre la différence entre les dépendances obligatoires et les recommandations avant de modifier le comportement de l'installation.

Les options qui désactivent globalement l'installation de paquets recommandés peuvent réduire certaines installations, mais également omettre des fonctions que les mainteneurs considèrent utiles.

Il vaut mieux comprendre le besoin de l'application avant de changer le comportement global du gestionnaire.


# 5. Examiner les transactions avant modification

## 5.1. Pourquoi simuler une transaction ?

Une opération peut installer ou supprimer plusieurs paquets, pas seulement celui que tu as demandé.

Sur un serveur, une transaction inattendue peut affecter le réseau, l'accès distant, la base de données ou un autre service.

La simulation permet de repérer certains risques avant de modifier l'état du système.

## 5.2. Simuler une installation

```bash
apt-get -s install curl
```

## 5.3. Simuler une suppression

```bash
apt-get -s remove curl
```

## 5.4. Simuler une mise à niveau

```bash
apt-get -s upgrade
```

## 5.5. Simuler une mise à niveau complexe

```bash
apt-get -s dist-upgrade
```

Sur les systèmes Debian et Ubuntu, `dist-upgrade` peut tenir compte de changements complexes de dépendances, y compris des installations ou suppressions de paquets nécessaires à la résolution.

La version interactive moderne `apt full-upgrade` correspond à un usage apparenté.

La simulation permet de repérer les changements prévus, mais ne prouve pas que la transaction réelle se comportera exactement de la même manière : l'état du système ou des sources peut évoluer entre-temps.

## 5.6. Lire le résumé

Avant de confirmer une transaction réelle, examine :

- le nombre de paquets installés ;
- le nombre de paquets mis à jour ;
- le nombre de paquets supprimés ;
- les dépendances nouvellement installées ;
- les versions sélectionnées ;
- les éventuels messages d'erreur ;
- l'espace disque requis.

Une longue liste de modifications n'est pas nécessairement anormale, mais doit être comprise.

Une suppression inattendue d'un composant essentiel doit conduire à interrompre l'opération et à rechercher la cause.

## 5.7. Une simulation ne remplace pas une sauvegarde

La simulation montre les changements prévus par le gestionnaire dans son état courant.

Elle ne protège pas contre :

- un problème matériel ;
- une erreur de configuration ;
- un défaut logiciel ;
- des données applicatives corrompues ;
- un changement externe ;
- une modification imprévue du comportement d'une application.

Les mises à jour importantes doivent être accompagnées des sauvegardes et procédures de restauration adaptées à la fonction du système.


# 6. Comprendre les priorités APT et les versions candidates

## 6.1. Pourquoi APT a-t-il besoin de priorités ?

APT peut connaître plusieurs versions d'un même paquet provenant de sources différentes.

Il doit déterminer quelle version privilégier en fonction des versions disponibles, des règles de sélection et des priorités.

La priorité contribue à ce choix, mais elle n'est pas l'unique facteur : les contraintes de dépendance et les états locaux comptent également.

## 6.2. Afficher les priorités

```bash
apt-cache policy curl
```

La sortie peut montrer des priorités telles que `500`, `100` ou d'autres valeurs.

Ces nombres sont des priorités de sélection, pas des notes de qualité du paquet.

Ils permettent à APT de choisir entre certaines versions disponibles.

## 6.3. La notion de pinning

Le *pinning* permet de définir des préférences de version ou d'origine.

Il sert notamment à contrôler la sélection des versions lorsque plusieurs sources sont présentes.

La configuration est généralement documentée dans :

```text
/etc/apt/preferences
/etc/apt/preferences.d/
```

Les chemins et la syntaxe doivent être vérifiés pour la version d'APT utilisée.

## 6.4. Pourquoi le pinning est-il sensible ?

Une règle trop large peut modifier la sélection de nombreux paquets.

Cela peut conduire à :

- sélectionner des paquets issus d'une autre version de distribution ;
- tirer des dépendances d'une source inattendue ;
- bloquer certaines mises à niveau ;
- créer une combinaison de versions difficile à maintenir.

Le pinning doit être aussi ciblé que nécessaire.

Ne copie pas une règle de priorité globale depuis une autre machine sans comprendre les effets sur l'ensemble des paquets.

## 6.5. Exemple conceptuel de préférence

Supposons que tu veuilles donner une priorité particulière à une version identifiée d'un paquet. Une règle de préférence peut être construite à partir des champs et mécanismes de sélection documentés par APT.

La structure générale d'un fichier de préférences utilise des champs comme :

```text
Package:
Pin:
Pin-Priority:
```

Le contenu exact dépend du paquet, de l'origine ou de la version à sélectionner.

**Cet exemple décrit la structure, pas une configuration complète à copier.** Une règle doit être conçue à partir des versions et des origines réellement observées.

Avant et après toute modification de préférences, compare :

```bash
apt-cache policy nom-du-paquet
```

et simule la transaction concernée :

```bash
apt-get -s install nom-du-paquet
```

## 6.6. Consulter la documentation appropriée

La documentation de référence est :

```bash
man apt_preferences
```

Elle explique les champs, la hiérarchie des priorités et les règles de sélection.

Une bonne configuration de pinning doit répondre à un besoin précis, être documentée et être testée avant d'être appliquée à un ensemble de serveurs.


# 7. Contrôler les paquets avec `apt-mark`

## 7.1. Paquets installés manuellement et automatiquement

APT conserve des informations permettant de distinguer les paquets installés explicitement par l'administrateur de ceux ajoutés automatiquement comme dépendances.

Cette distinction influence notamment la commande `autoremove`.

Un paquet installé automatiquement peut rester nécessaire à un autre paquet.

Lorsqu'il n'est plus considéré nécessaire, APT peut le proposer pour suppression.

## 7.2. Afficher les paquets marqués comme manuels

```bash
apt-mark showmanual
```

Cette commande affiche les paquets marqués comme installés manuellement.

Elle peut être utile pour créer un inventaire des composants explicitement demandés.

Toutefois, cette liste n'est pas automatiquement une liste complète des logiciels métier réellement nécessaires. Un paquet peut être requis par un script ou par une configuration non représentée dans les relations de dépendances.

## 7.3. Afficher les paquets marqués comme automatiques

```bash
apt-mark showauto
```

Cette commande affiche les paquets marqués comme installés automatiquement.

Il faut distinguer cette information du fait qu'un paquet soit actuellement nécessaire à une application particulière.

## 7.4. Marquer un paquet comme manuel

```bash
sudo apt-mark manual nom-du-paquet
```

Cette commande marque le paquet comme installé manuellement dans les métadonnées d'APT.

Elle peut être utile pour éviter qu'un paquet important soit considéré comme une dépendance automatiquement supprimable.

Ne marque pas arbitrairement tous les paquets comme manuels : cela réduit l'efficacité du nettoyage et complique la gestion des dépendances.

## 7.5. Marquer un paquet comme automatique

```bash
sudo apt-mark auto nom-du-paquet
```

Cette commande marque le paquet comme installé automatiquement.

Utilise-la avec précaution : si le paquet n'est plus nécessaire à aucun autre composant selon l'analyse d'APT, il pourrait ensuite être proposé par `autoremove`.

## 7.6. Quand utiliser `apt-mark` ?

Exemple de situation :

Un administrateur souhaite conserver une bibliothèque parce qu'elle est utilisée par un outil local qui ne déclare pas correctement sa dépendance.

Il peut décider de la marquer comme manuelle, après avoir confirmé le besoin.

Cette décision doit être documentée, car elle représente une dépendance opérationnelle qui n'est pas nécessairement décrite dans le graphe standard des paquets.


# 8. Gérer les paquets retenus et les versions particulières

## 8.1. Qu'est-ce qu'un paquet retenu ?

Un paquet retenu est un paquet dont la mise à niveau normale est empêchée par un mécanisme de retenue.

Sur Debian et Ubuntu, les retenues peuvent être gérées avec `apt-mark`.

Afficher les paquets retenus :

```bash
apt-mark showhold
```

Cette commande aide à repérer les paquets qui ne suivent pas les mises à niveau habituelles.

## 8.2. Retenir une version installée

```bash
sudo apt-mark hold nom-du-paquet
```

La commande marque le paquet comme retenu.

Il peut être utile de retenir un paquet lors d'une maintenance contrôlée lorsqu'une mise à jour doit être différée pour une raison documentée.

Cependant, la retenue ne corrige pas un problème de compatibilité et peut empêcher l'application de mises à jour de sécurité.

## 8.3. Retirer la retenue

```bash
sudo apt-mark unhold nom-du-paquet
```

Après la suppression de la retenue, examine les mises à jour disponibles et le plan de transaction avant d'appliquer une mise à niveau.

## 8.4. Pourquoi les retenues doivent-elles être suivies ?

Une retenue oubliée peut entraîner :

- le maintien d'une version vulnérable ;
- des différences de paquets entre serveurs ;
- des dépendances qui compliquent une future mise à niveau ;
- un écart entre l'état souhaité et l'état réel.

Une retenue doit donc avoir une raison, un propriétaire, une date de révision et une condition de retrait lorsque le contexte l'exige.

## 8.5. La retenue n'est pas une protection absolue de toutes les opérations possibles

Une retenue influence les opérations habituelles de gestion des paquets.

Elle ne doit pas être considérée comme une garantie que toutes les options, tous les outils de bas niveau ou toutes les modifications locales respecteront nécessairement le même comportement.

Il faut comprendre le mécanisme employé par la procédure d'administration.


# 9. Comprendre les dépôts et leurs priorités

## 9.1. Les dépôts ne sont pas tous équivalents

Les sources peuvent inclure :

- les dépôts officiels de la distribution ;
- des dépôts de maintenance ou de mises à jour de sécurité ;
- des dépôts de rétroportage ;
- des dépôts de fournisseurs ;
- des dépôts internes à une organisation.

Un même nom de paquet peut être disponible dans plusieurs sources avec des versions différentes.

L'origine et la priorité peuvent donc influencer le résultat de la transaction.

## 9.2. Examiner la liste des sources

Sur Debian et Ubuntu, consulte les fichiers présents dans :

```text
/etc/apt/sources.list
/etc/apt/sources.list.d/
```

Les installations récentes d'Ubuntu peuvent notamment utiliser des fichiers au format deb822 tels que :

```text
/etc/apt/sources.list.d/ubuntu.sources
```

Les versions et configurations plus anciennes peuvent organiser les sources autrement.

Pour un inventaire :

```bash
find /etc/apt -maxdepth 2 -type f \
    \( -name '*.list' -o -name '*.sources' \) -print
```

Cette commande liste les fichiers de sources correspondants dans l'arborescence APT.

Les noms des fichiers ne suffisent pas à connaître toutes les sources effectives : il faut examiner leur contenu et leur statut.

## 9.3. Examiner une configuration de source

Une source deb822 peut comporter des champs tels que :

```text
Types:
URIs:
Suites:
Components:
Signed-By:
```

Ces champs permettent de décrire les types de paquets, les adresses, les suites et les composants disponibles, ainsi que les paramètres de confiance associés.

La configuration exacte varie selon la source.

Ne remplace pas aveuglément les sources d'une distribution par celles d'une autre version.

## 9.4. Éviter le mélange de versions de distribution

Mélanger les dépôts de plusieurs versions ou de plusieurs distributions peut introduire des dépendances incompatibles.

Cela peut rendre une future mise à niveau difficile, provoquer des conflits ou remplacer des composants fondamentaux.

Avant d'ajouter un dépôt :

1. identifie la distribution et sa version ;
2. vérifie que le dépôt est compatible ;
3. comprends les versions de paquets qu'il peut fournir ;
4. examine sa politique de mise à jour ;
5. vérifie les clés ou mécanismes de confiance ;
6. simule les opérations sensibles.

## 9.5. Dépôts tiers et signatures

Un dépôt tiers peut fournir une version utile d'un logiciel, mais il apporte aussi une source supplémentaire de code et de dépendances.

Les métadonnées du dépôt doivent être vérifiées selon le mécanisme de confiance prévu par APT.

Pour une source tierce, il est préférable d'utiliser une clé dédiée et un mécanisme de restriction de son champ d'application, comme `Signed-By`, lorsque c'est adapté.

Évite de désactiver les vérifications d'authenticité pour contourner un problème de clé.


# 10. Configurer proprement les sources APT

## 10.1. Examiner avant de modifier

Avant de modifier les sources :

```bash
cat /etc/apt/sources.list
```

Si le fichier n'existe pas ou ne contient pas les sources actives, examine le répertoire :

```bash
ls -l /etc/apt/sources.list.d/
```

Lis les fichiers de sources présents.

Ne suppose pas qu'une configuration utilise obligatoirement un seul fichier.

## 10.2. Sauvegarder la configuration

Avant une modification importante :

```bash
sudo cp -a /etc/apt/sources.list.d /etc/apt/sources.list.d.backup
```

Cette commande crée une copie du répertoire avec ses attributs dans un emplacement distinct.

Vérifie que le chemin de sauvegarde n'existe pas déjà avant de l'utiliser dans une procédure répétable.

Si le fichier `/etc/apt/sources.list` existe et doit également être modifié, sauvegarde-le séparément.

Une sauvegarde locale ne protège toutefois pas contre la perte complète du système de fichiers. Pour une maintenance importante, utilise un mécanisme de sauvegarde adapté.

## 10.3. Ne pas inventer une source de dépôt

Une ligne de dépôt dépend notamment :

- de l'éditeur ;
- de la distribution ;
- de la version de distribution ;
- de l'architecture ;
- de la méthode de signature ;
- des paquets publiés par cette source.

Il ne faut donc pas inventer un dépôt ou copier une ligne depuis une documentation qui concerne une autre distribution.

Utilise les instructions officielles de la source concernée, vérifie leur compatibilité et comprends leur portée.

## 10.4. Vérifier après modification

Après un changement de source :

```bash
sudo apt update
```

Examine les messages.

Puis, pour un paquet concerné :

```bash
apt-cache policy nom-du-paquet
```

Cette vérification permet de déterminer quelles versions sont désormais disponibles et comment les priorités influencent leur sélection.

## 10.5. Pourquoi ne pas ignorer une erreur de signature ?

Une erreur de signature peut provenir d'une clé manquante, expirée, incorrecte ou associée à une configuration erronée.

Il faut identifier le problème et suivre la procédure officielle de la source.

Désactiver la vérification peut exposer le système à des paquets qui ne sont pas authentifiés comme attendu.


# 11. Installer et inspecter les paquets locaux

## 11.1. Installer un fichier DEB local

La forme courante est :

```bash
sudo apt install ./fichier.deb
```

Le fichier doit correspondre à une archive DEB présente dans le répertoire courant ou à un chemin valide.

APT peut résoudre les dépendances à partir des dépôts configurés, selon la compatibilité et les informations disponibles.

## 11.2. Inspecter un paquet avant installation

L'outil `dpkg-deb` permet d'examiner un fichier DEB.

Afficher ses métadonnées :

```bash
dpkg-deb -I fichier.deb
```

Lister son contenu :

```bash
dpkg-deb -c fichier.deb
```

Ces commandes aident à examiner le nom du paquet, sa version, les relations déclarées et les chemins fournis.

Elles ne remplacent pas les vérifications de confiance ou de compatibilité nécessaires avant une installation.

## 11.3. Pourquoi un paquet local peut-il être incompatible ?

Un paquet peut être prévu pour :

- une autre version de distribution ;
- une autre architecture ;
- des bibliothèques plus récentes ;
- des dépendances absentes ;
- un environnement particulier.

Le fait que le fichier porte l'extension `.deb` ne garantit pas qu'il convient au système.

## 11.4. Vérifier l'origine du fichier

Avant d'installer un paquet local :

1. retrouver son origine ;
2. confirmer que la source est fiable ;
3. vérifier sa version et son architecture ;
4. examiner ses dépendances ;
5. consulter les signatures, sommes de contrôle ou mécanismes officiels disponibles ;
6. simuler l'installation si possible ;
7. vérifier le résultat après installation.

Une somme de contrôle permet de vérifier l'identité d'un fichier par rapport à une valeur de référence fiable. Elle ne prouve pas à elle seule que le logiciel est sûr.

Une signature correctement vérifiée, associée à une clé de confiance légitime, fournit une propriété supplémentaire d'authenticité.

## 11.5. Quand utiliser `dpkg -i` ?

```bash
sudo dpkg -i fichier.deb
```

Cette commande effectue une installation de bas niveau du paquet local.

Elle peut laisser le paquet dans un état nécessitant une configuration ou une résolution de dépendances.

Pour les opérations ordinaires, APT est généralement préférable si les dépendances peuvent être satisfaites à partir des sources configurées.

Ne tente pas de contourner les erreurs avec des options de forçage sans comprendre exactement la contrainte rencontrée.


# 12. Comprendre les états de `dpkg`

## 12.1. Pourquoi l'état de paquet est-il important ?

Un paquet peut être téléchargé, dépaqueté, configuré ou dans un état intermédiaire après une interruption.

La présence des fichiers sur le disque ne prouve pas nécessairement que le paquet a été configuré correctement.

## 12.2. Examiner les informations

```bash
dpkg -s nom-du-paquet
```

Cette commande affiche les informations enregistrées dans la base locale.

Pour examiner la liste des paquets et leurs états :

```bash
dpkg -l
```

La sortie comporte des colonnes de statut.

Un paquet en état entièrement installé est généralement représenté par `ii` dans la colonne de statut de `dpkg -l`, mais d'autres états existent.

## 12.3. Les grandes catégories d'état

Les informations de statut distinguent notamment :

- l'action souhaitée ;
- l'état actuel ;
- certains indicateurs d'erreur.

Les états possibles comprennent l'installation, la configuration, la suppression, la purge ou des étapes intermédiaires.

Pour une interprétation exacte des codes, consulte :

```bash
man dpkg
```

Un état intermédiaire doit être examiné avant de considérer l'installation comme réussie.

## 12.4. Détecter les paquets à vérifier

```bash
dpkg --audit
```

Cette commande peut signaler des paquets dont l'installation ou la configuration nécessite une attention particulière.

Le résultat doit être interprété en fonction de l'état réel du système.

## 12.5. Pourquoi une interruption peut-elle laisser un état intermédiaire ?

Une installation peut être interrompue à la suite :

- d'un arrêt de la machine ;
- d'un problème d'alimentation ;
- d'une erreur dans un script de maintenance ;
- d'un manque d'espace disque ;
- d'une dépendance indisponible ;
- d'une intervention qui a échoué.

Dans ces situations, le gestionnaire peut avoir dépaqueté un paquet sans terminer toutes les étapes de configuration.

La réparation doit commencer par l'identification de l'erreur initiale.


# 13. Réparer une base de paquets incohérente

## 13.1. Première étape : collecter les erreurs

Avant de lancer des commandes de réparation, examine :

```bash
dpkg --audit
```

Puis :

```bash
sudo tail -n 100 /var/log/dpkg.log
```

Et :

```bash
sudo tail -n 100 /var/log/apt/term.log
```

Le fichier `term.log` peut être absent selon l'historique ou la configuration.

Lis les messages qui expliquent l'échec plutôt que de lancer automatiquement toutes les commandes de réparation possibles.

## 13.2. Configurer les paquets dépaquetés mais non configurés

La commande :

```bash
sudo dpkg --configure -a
```

demande à `dpkg` de configurer les paquets dépaquetés mais non configurés qui peuvent être traités.

Elle peut échouer de nouveau si une dépendance manque ou si un script de configuration ne fonctionne pas.

Il faut alors examiner le message précis et traiter sa cause.

## 13.3. Corriger des dépendances cassées

APT propose une opération prévue pour aider à résoudre certaines situations de dépendances cassées :

```bash
sudo apt --fix-broken install
```

Cette commande peut proposer d'installer ou de supprimer des paquets.

**Examine toujours le plan avant de confirmer.** Une commande de réparation n'est pas automatiquement sans risque.

Il est préférable de traiter le problème qui empêche la résolution plutôt que de forcer l'installation.

## 13.4. Ordre de diagnostic recommandé

```text
ERREUR APT OU DPKG
        |
        v
LIRE LE MESSAGE INITIAL
        |
        v
EXAMINER dpkg --audit
        |
        v
IDENTIFIER LE PAQUET EN ÉCHEC
        |
        v
EXAMINER LES DÉPENDANCES
        |
        v
CORRIGER LA CAUSE
        |
        v
SIMULER SI POSSIBLE
        |
        v
CONFIGURER OU RÉPARER
        |
        v
VÉRIFIER L'ÉTAT FINAL
```

## 13.5. Pourquoi ne faut-il pas supprimer les fichiers de verrou ?

Les fichiers de verrou sont utilisés par les outils pour coordonner les opérations.

Supprimer le fichier de verrou ne termine pas le processus qui utilise la base de paquets.

Si une transaction est encore en cours, forcer une seconde opération peut aggraver l'incohérence.

La bonne démarche consiste à identifier le processus qui travaille, vérifier son état et comprendre pourquoi le verrou reste présent.

## 13.6. Ne pas utiliser les options de forçage comme solution ordinaire

Des options de forçage de `dpkg` existent pour certains cas particuliers.

Elles peuvent contourner des contraintes qui protègent la cohérence du système.

Elles ne doivent pas être utilisées comme une méthode standard pour « faire passer » une installation.

Il faut d'abord comprendre si le paquet est incompatible, si une dépendance est absente, si la base locale est en état intermédiaire ou si un script de maintenance a échoué.


# 14. Vérifier et réinstaller les fichiers d'un paquet

## 14.1. Identifier les fichiers gérés

```bash
dpkg -L nom-du-paquet
```

Cette commande liste les chemins enregistrés dans la base locale pour le paquet.

Elle aide à vérifier où le paquet place ses exécutables, bibliothèques, fichiers de configuration et documents.

## 14.2. Identifier le propriétaire d'un fichier

```bash
dpkg -S /chemin/du/fichier
```

Cette commande recherche le paquet propriétaire du chemin selon la base locale.

Elle peut ne rien trouver si le fichier n'est pas géré par un paquet connu.

## 14.3. Vérifier certains attributs des fichiers

Sur un système Debian ou Ubuntu, on peut utiliser :

```bash
dpkg --verify nom-du-paquet
```

Cette commande peut comparer certains attributs et sommes de contrôle enregistrés, lorsque les informations nécessaires sont disponibles.

**Cette vérification n'est pas une garantie exhaustive de l'intégrité ou de la sécurité de toute l'installation.**

Les fichiers de configuration peuvent être modifiés légitimement, et toutes les modifications possibles ne sont pas nécessairement détectées par cette seule commande.

## 14.4. Réinstaller un paquet

Si un paquet semble incomplet et que sa source est fiable :

```bash
sudo apt install --reinstall nom-du-paquet
```

APT demande la réinstallation du paquet.

Cette action ne doit pas être utilisée comme remède universel à tout problème logiciel. Elle ne corrige pas automatiquement les erreurs de configuration, les données corrompues de l'application ou les problèmes de dépendances externes.

## 14.5. Pourquoi la réinstallation peut-elle ne pas suffire ?

Une application peut dépendre de :

- fichiers de configuration modifiés ;
- données situées hors des fichiers du paquet ;
- bases de données ;
- permissions spéciales ;
- services dépendants ;
- ressources externes ;
- fichiers générés pendant l'exploitation.

Réinstaller le paquet ne réinitialise pas nécessairement tous ces éléments.

Avant une réinstallation, identifie le problème et sauvegarde les données pertinentes.


# 15. Maîtriser les suppressions, purges et dépendances résiduelles

## 15.1. `remove` et `purge`

```bash
sudo apt remove nom-du-paquet
```

demande la suppression du paquet.

```bash
sudo apt purge nom-du-paquet
```

demande également la suppression des fichiers de configuration suivis par le paquetage, selon les règles Debian.

La purge ne garantit pas l'effacement de toutes les données de l'application. Des fichiers générés, des données utilisateur et des contenus situés hors des chemins gérés peuvent subsister.

## 15.2. Suppression d'une dépendance

Avant une suppression :

```bash
apt-get -s remove nom-du-paquet
```

Lis les paquets concernés.

Si une bibliothèque utilisée par plusieurs applications est proposée à la suppression, comprends les conséquences avant de confirmer.

## 15.3. `autoremove`

```bash
sudo apt autoremove
```

APT propose de supprimer les paquets installés automatiquement qui ne sont plus considérés nécessaires.

La liste doit être vérifiée.

Certains paquets peuvent être requis par des tâches administratives ou des applications qui ne déclarent pas correctement leurs dépendances. Il faut donc connaître les besoins réels du système avant de confirmer la suppression.

## 15.4. `clean` et `autoclean`

```bash
sudo apt clean
```

Supprime les archives téléchargées dans le cache APT.

```bash
sudo apt autoclean
```

Nettoie certaines archives devenues obsolètes ou qui ne peuvent généralement plus être téléchargées depuis les sources configurées.

Ces opérations ne désinstallent pas directement les paquets.

## 15.5. Pourquoi un nettoyage ne doit-il pas être automatique dans tous les cas ?

Le nettoyage du cache peut réduire l'espace consommé par les archives, mais il peut aussi obliger le système à retélécharger des paquets lors d'une opération ultérieure.

Sur une machine sans accès réseau fiable, le cache peut avoir une valeur opérationnelle.

Le nettoyage doit donc être relié à un besoin identifié, à la capacité disque et aux conditions de maintenance.


# 16. Gérer les mises à jour en environnement serveur

## 16.1. Une mise à jour est une modification de l'environnement logiciel

Une mise à jour peut remplacer des bibliothèques, corriger des vulnérabilités, modifier un exécutable, exécuter des scripts ou changer les versions utilisées par les services.

Le résultat doit être évalué selon le rôle de la machine.

## 16.2. Procédure de base

La séquence habituelle sur Debian et Ubuntu est :

```bash
sudo apt update
```

Puis :

```bash
apt list --upgradable
```

Ensuite, après examen du contexte :

```bash
sudo apt upgrade
```

Ces commandes ne constituent pas à elles seules une procédure complète de maintenance pour un serveur critique.

Elles doivent s'intégrer à la sauvegarde, à la planification et aux contrôles postérieurs nécessaires.

## 16.3. Examiner les paquets retenus

```bash
apt-mark showhold
```

Les paquets retenus peuvent ne pas suivre le cycle de mise à jour habituel.

Chaque retenue doit être justifiée et suivie.

## 16.4. Examiner les paquets modifiés par la transaction

Les journaux de transaction peuvent aider à savoir quels paquets ont été modifiés.

Sur Debian et Ubuntu :

```bash
sudo tail -n 100 /var/log/apt/history.log
```

Et :

```bash
sudo tail -n 100 /var/log/dpkg.log
```

Il faut tenir compte de la rotation des journaux et rechercher les fichiers archivés si l'incident est ancien.

## 16.5. Contrôler les services après l'opération

```bash
systemctl --failed
```

Cette commande est pertinente sur un système utilisant `systemd`.

Pour les services sensibles :

```bash
systemctl status nom.service
```

Puis :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Enfin, utilise des tests fonctionnels adaptés à l'application.

Un service peut être marqué actif tout en rencontrant une erreur de traitement.

## 16.6. Vérifier si un redémarrage est nécessaire

Certaines mises à jour peuvent nécessiter un redémarrage du service ou du système.

Sur Ubuntu et certains systèmes Debian, le fichier suivant peut indiquer que certaines mises à jour ont signalé la nécessité d'un redémarrage :

```bash
test -e /var/run/reboot-required && echo "Redémarrage indiqué"
```

La disponibilité et la signification exacte de ce mécanisme dépendent de la distribution et des paquets installés.

L'absence de ce fichier ne prouve pas qu'aucun redémarrage ne sera jamais nécessaire ; les procédures officielles de la distribution et des applications restent la référence.

## 16.7. Préparer le retour arrière

Avant une mise à jour importante, identifie les moyens de restauration :

- sauvegardes des données ;
- sauvegardes des fichiers de configuration ;
- instantané de machine virtuelle si adapté ;
- procédure de retour à un paquet précédent, si elle est fiable ;
- mécanisme de déploiement précédent ;
- accès console si l'accès distant risque d'être interrompu.

Une rétrogradation de paquet n'est pas toujours simple. Les bases de données, les fichiers de configuration et les migrations peuvent avoir été modifiés pendant la mise à niveau.

Il ne faut donc pas supposer qu'une simple commande de retour à l'ancienne version restaure l'état complet de l'application.


# 17. Automatiser les mises à jour de sécurité

## 17.1. Pourquoi automatiser certaines mises à jour ?

Les mises à jour de sécurité corrigent des vulnérabilités et peuvent réduire l'exposition du système.

L'automatisation peut contribuer à installer rapidement des correctifs lorsque la politique de maintenance le prévoit.

Mais elle doit tenir compte du rôle du serveur, des applications, des fenêtres d'intervention et des risques de mise à jour.

## 17.2. `unattended-upgrades`

Sur Ubuntu, le mécanisme `unattended-upgrades` peut appliquer des mises à jour selon la configuration. Les installations par défaut et les sources prises en compte varient selon la version et l'image utilisée.

Vérifier l'installation :

```bash
dpkg -s unattended-upgrades
```

Consulter les configurations pertinentes :

```text
/etc/apt/apt.conf.d/20auto-upgrades
/etc/apt/apt.conf.d/50unattended-upgrades
```

L'état réel doit être vérifié dans les fichiers présents.

## 17.3. Les mises à jour automatiques ne s'appliquent pas nécessairement à toutes les sources

L'ajout d'un dépôt supplémentaire ne garantit pas que `unattended-upgrades` appliquera automatiquement les mises à jour provenant de cette source.

Les origines autorisées doivent être examinées dans la configuration.

Il faut vérifier quelles sources sont prises en compte et quelles catégories de mises à jour sont autorisées.

## 17.4. Examiner les journaux

Le répertoire suivant est couramment utilisé par `unattended-upgrades` :

```text
/var/log/unattended-upgrades/
```

Pour examiner les fichiers présents :

```bash
sudo ls -l /var/log/unattended-upgrades/
```

Pour consulter les dernières lignes d'un journal précis, choisis son chemin réel et utilise `tail` ou `less`.

Les journaux permettent de comprendre quelles mises à jour ont été appliquées ou pourquoi une opération a échoué.

## 17.5. Tester la configuration

Il est possible d'utiliser les options de vérification ou de simulation documentées par la version installée.

Consulte :

```bash
man unattended-upgrade
```

Ne lance pas un outil de test avec des options copiées d'une autre version sans en vérifier la signification.

## 17.6. L'automatisation n'est pas une garantie de sécurité

Les mises à jour automatiques doivent être associées à :

- une source de paquets digne de confiance ;
- une politique de versions claire ;
- une surveillance des erreurs ;
- des sauvegardes adaptées ;
- des tests de fonctionnement ;
- un processus de gestion des exceptions ;
- une politique de redémarrage.

Certaines applications peuvent nécessiter une action après la mise à niveau.

Documentation officielle Ubuntu : [Automatic updates](https://ubuntu.com/server/docs/how-to/software/automatic-updates/).


# 18. Comprendre les journaux et l'historique des transactions

## 18.1. Pourquoi consulter l'historique ?

Lorsque l'état d'un système change, l'administrateur doit pouvoir déterminer :

- quel paquet a été installé ;
- quelle version a été mise à niveau ;
- quel paquet a été supprimé ;
- quand l'opération a eu lieu ;
- quelles erreurs sont apparues pendant la transaction.

Les journaux facilitent cette analyse.

## 18.2. Les principaux journaux Debian/Ubuntu

Les fichiers peuvent inclure :

```text
/var/log/apt/history.log
/var/log/apt/term.log
/var/log/dpkg.log
```

Leur présence et leur contenu dépendent de l'historique et de la configuration.

## 18.3. Examiner les opérations APT

```bash
sudo less /var/log/apt/history.log
```

Ce journal peut présenter le début et la fin d'une transaction, les commandes et les paquets concernés.

Il permet de distinguer une transaction réalisée d'une simple simulation.

## 18.4. Examiner les événements `dpkg`

```bash
sudo less /var/log/dpkg.log
```

Le journal permet d'étudier des événements liés à l'installation, à la mise à niveau ou à la suppression des paquets.

Les événements peuvent être présents dans des fichiers de journal archivés lorsque la rotation a eu lieu.

## 18.5. Rechercher une erreur

```bash
sudo grep -iE 'error|fail|warning' /var/log/dpkg.log
```

Le résultat n'est qu'une recherche textuelle. Certaines erreurs peuvent être décrites sans employer exactement ces mots.

Une recherche utile doit être limitée à la période ou au paquet pertinent.

## 18.6. Construire une chronologie

Lorsqu'un service ne démarre plus après une mise à jour :

```text
HEURE 1
Installation ou mise à niveau du paquet

HEURE 2
Échec du démarrage du service

HEURE 3
Message d'erreur dans le journal applicatif

HEURE 4
Intervention de l'administrateur

HEURE 5
Vérification du service après intervention
```

Ce schéma est illustratif.

La chronologie aide à rechercher la relation entre les opérations de paquet et les symptômes. Elle ne démontre pas à elle seule la causalité.

## 18.7. Conserver les preuves

Avant de supprimer ou de faire tourner un journal, vérifie qu'il ne contient pas des informations nécessaires au diagnostic ou à un audit.

Les fichiers de trace peuvent contenir des chemins, des noms d'utilisateur et d'autres informations internes. Leur accès et leur conservation doivent respecter la politique de sécurité du système.


# 19. Diagnostiquer les verrous et les erreurs de gestionnaire

## 19.1. Pourquoi un verrou existe-t-il ?

Les gestionnaires de paquets modifient une base locale et certains fichiers système.

Un mécanisme de verrouillage permet d'éviter que plusieurs opérations incompatibles travaillent simultanément sur les mêmes structures.

## 19.2. Message indiquant qu'un verrou est utilisé

Un message de verrouillage peut signifier qu'une installation ou une mise à jour est encore en cours.

Avant toute intervention, vérifie les processus actifs :

```bash
ps -ef | grep -E '[a]pt|[d]pkg|[u]nattended-upgrade'
```

Cette commande est une recherche textuelle indicative. Examine les lignes obtenues, car la présence d'un processus ne suffit pas à dire s'il est bloqué ou s'il effectue une opération légitime.

## 19.3. Vérifier l'état de la machine

Vérifie également l'activité de maintenance automatique si le système en utilise :

```bash
systemctl status apt-daily.service
```

```bash
systemctl status apt-daily-upgrade.service
```

Ces unités ne sont présentes que dans les environnements qui les utilisent.

## 19.4. Pourquoi ne pas supprimer le verrou ?

Supprimer un fichier de verrou ne termine pas la transaction qui est en cours.

Cela peut permettre à une autre opération de démarrer alors que la première manipule toujours la base.

Il faut d'abord déterminer si une transaction est active, terminée ou réellement bloquée.

Une interruption forcée doit être réservée aux situations diagnostiquées et traitées selon une procédure contrôlée.

## 19.5. Un processus semble bloqué

Si la commande ne progresse plus, examine son état, le temps écoulé, les journaux et les ressources disponibles.

Il peut être nécessaire de vérifier :

- la connectivité aux dépôts ;
- l'espace disque ;
- les dépendances ;
- une erreur de script de maintenance ;
- une attente de saisie interactive ;
- une opération de configuration ;
- les messages du noyau ou du service.

Il ne faut pas envoyer un signal au processus gestionnaire uniquement parce que l'affichage n'a pas changé pendant quelques secondes.


# 20. Gérer les dépendances et les conflits entre dépôts

## 20.1. Pourquoi les conflits apparaissent-ils ?

Les conflits peuvent provenir :

- de dépôts qui fournissent des versions incompatibles ;
- de paquets qui déclarent des relations contradictoires ;
- d'un paquet local construit pour une autre version de distribution ;
- de retenues ;
- de préférences APT ;
- d'une base de paquets incomplètement configurée.

Le gestionnaire peut alors refuser la transaction parce qu'il ne trouve pas de combinaison de versions satisfaisant les contraintes.

## 20.2. Examiner l'origine d'un paquet

```bash
apt-cache policy nom-du-paquet
```

Cette commande aide à identifier les versions et les priorités connues.

Elle est particulièrement importante lorsque plusieurs dépôts sont présents.

## 20.3. Examiner les dépendances

```bash
apt-cache depends nom-du-paquet
```

Puis, si nécessaire :

```bash
apt-cache rdepends nom-du-paquet
```

Ces commandes peuvent montrer les relations déclarées qui expliquent une contrainte.

## 20.4. Examiner les paquets retenus

```bash
apt-mark showhold
```

Une retenue peut empêcher une mise à niveau qu'une autre dépendance nécessite.

Ne retire pas automatiquement toutes les retenues. Comprends pourquoi elles ont été placées.

## 20.5. Simuler la résolution

```bash
apt-get -s install nom-du-paquet
```

Pour une mise à niveau :

```bash
apt-get -s upgrade
```

Si la simulation propose des suppressions inattendues, annule l'opération réelle et cherche les dépendances ou priorités à l'origine du plan.

## 20.6. Résoudre le conflit

Une procédure générale consiste à :

1. identifier la version installée ;
2. identifier les versions disponibles ;
3. contrôler les dépôts ;
4. examiner les retenues et préférences ;
5. comprendre les dépendances incompatibles ;
6. déterminer la version cible appropriée ;
7. simuler le changement ;
8. appliquer une correction contrôlée ;
9. vérifier les services et les paquets après opération.

Il faut éviter les installations forcées qui masquent le conflit sans en corriger la cause.


# 21. Préparer un inventaire et un état logiciel reproductible

## 21.1. Pourquoi produire un inventaire ?

Un inventaire permet de comparer plusieurs machines et de comprendre les écarts.

Il peut servir à :

- préparer une maintenance ;
- rechercher un paquet absent ;
- identifier des versions différentes ;
- documenter un serveur ;
- reconstruire une installation de laboratoire ;
- préparer un audit.

## 21.2. Exporter les paquets installés

Sur Debian et Ubuntu :

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n'
```

Cette commande produit des lignes avec le nom, la version et l'architecture des paquets connus dans la base locale.

Pour conserver le résultat :

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' \
    > inventaire-paquets.tsv
```

Le fichier représente l'état au moment de l'export.

Il ne contient pas à lui seul toutes les informations nécessaires à la reproduction exacte d'un système.

## 21.3. Inventorier les sources

Il faut aussi conserver les informations sur les dépôts et les priorités.

Les sources APT se trouvent couramment dans :

```text
/etc/apt/sources.list
/etc/apt/sources.list.d/
```

Les fichiers de préférences peuvent se trouver dans :

```text
/etc/apt/preferences
/etc/apt/preferences.d/
```

Leur contenu doit être traité comme une partie importante de la configuration système.

## 21.4. Inventorier les paquets manuels

```bash
apt-mark showmanual
```

Cette liste aide à identifier les paquets explicitement marqués comme manuels.

Elle ne doit pas être considérée comme une définition complète de l'intention d'administration.

## 21.5. Pourquoi un inventaire ne suffit-il pas à reproduire un système ?

Une installation dépend aussi :

- de la version de distribution ;
- des dépôts configurés ;
- des priorités APT ;
- des fichiers de configuration ;
- des données applicatives ;
- des services activés ;
- des variables d'environnement ;
- des dépendances externes ;
- des versions disponibles au moment de l'installation.

Un inventaire de paquets est donc une composante d'une documentation reproductible, et non une sauvegarde complète.


# 22. Automatiser les contrôles avec Bash

## 22.1. Principes d'un script de maintenance fiable

Un script doit :

- valider ses arguments ;
- vérifier la disponibilité des outils ;
- distinguer une absence de résultat d'une erreur ;
- enregistrer les informations pertinentes ;
- vérifier les codes de retour ;
- éviter les modifications implicites ;
- ne pas contourner la sécurité des dépôts ;
- séparer les contrôles des opérations qui modifient le système.

Les opérations de modification doivent être explicites et documentées.

## 22.2. Script : vérifier un paquet

Créer `verifier-paquet.sh` :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s nom-du-paquet\n' "$0" >&2
    exit 2
fi

PACKAGE=$1

if ! command -v dpkg-query >/dev/null 2>&1; then
    printf 'Erreur : dpkg-query est indisponible.\n' >&2
    exit 2
fi

STATUS=$(
    dpkg-query -W -f='${db:Status-Status}' "$PACKAGE" 2>/dev/null
) || {
    printf 'Paquet absent de la base locale : %s\n' "$PACKAGE" >&2
    exit 1
}

if [[ "$STATUS" != "installed" ]]; then
    printf 'État inattendu pour %s : %s\n' "$PACKAGE" "$STATUS" >&2
    exit 1
fi

printf 'Paquet installé : %s\n' "$PACKAGE"

dpkg-query -W \
    -f='Version : ${Version}\nArchitecture : ${Architecture}\n' \
    "$PACKAGE"
```

Rendre le script exécutable :

```bash
chmod +x verifier-paquet.sh
```

Lancer :

```bash
./verifier-paquet.sh curl
```

Le paquet `curl` est un exemple ; le résultat dépend de l'installation réelle.

## 22.3. Pourquoi le script utilise-t-il une commande de substitution ?

Le script récupère le statut retourné par `dpkg-query`.

Il distingue ainsi une commande qui échoue d'un paquet dont le statut n'est pas celui attendu.

Cette distinction évite d'interpréter toute sortie vide comme une preuve d'absence ou de succès.

## 22.4. Script : produire un inventaire

```bash
#!/usr/bin/env bash

set -u

OUTPUT=${1:-inventaire-paquets.tsv}

if ! command -v dpkg-query >/dev/null 2>&1; then
    printf 'Erreur : dpkg-query est indisponible.\n' >&2
    exit 2
fi

if [[ -e "$OUTPUT" ]]; then
    printf 'Erreur : le fichier existe déjà : %s\n' "$OUTPUT" >&2
    exit 1
fi

if ! dpkg-query -W \
    -f='${Package}\t${Version}\t${Architecture}\n' > "$OUTPUT"; then
    printf 'Erreur pendant la création de l’inventaire.\n' >&2
    rm -f -- "$OUTPUT"
    exit 1
fi

printf 'Inventaire créé : %s\n' "$OUTPUT"
```

Exécuter :

```bash
chmod +x inventaire-paquets.sh
```

Puis :

```bash
./inventaire-paquets.sh
```

Ce script refuse d'écraser un fichier existant.

Il s'agit d'un exemple destiné à un environnement de laboratoire. Pour une utilisation en production, il faut aussi gérer les chemins de sortie, les permissions, les journaux, les erreurs et la politique de conservation.

## 22.5. Automatisation des mises à jour : précaution importante

Un script qui exécute systématiquement :

```bash
apt-get update
apt-get -y upgrade
```

peut modifier le système sans donner à l'administrateur l'occasion d'examiner la transaction.

Dans un environnement automatisé bien conçu, il faut notamment prévoir :

- les sources autorisées ;
- la politique de mise à jour ;
- la gestion des erreurs ;
- les paquets retenus ;
- les changements susceptibles de nécessiter un redémarrage ;
- les tests fonctionnels ;
- la supervision des résultats ;
- le retour arrière ou la restauration.

Il ne faut pas ajouter `-y` uniquement pour supprimer les questions sans avoir défini une politique de maintenance et une méthode de contrôle.


# 23. Maintenance avancée avec DNF/RPM

Cette section complète les opérations Debian/Ubuntu pour les environnements utilisant le format RPM.

## 23.1. Identifier les paquets installés

```bash
rpm -qa
```

Cette commande liste les paquets connus de la base RPM locale.

## 23.2. Examiner les informations d'un paquet

```bash
rpm -qi nom-du-paquet
```

Elle affiche les informations disponibles dans la base locale.

## 23.3. Rechercher les fichiers fournis

```bash
rpm -ql nom-du-paquet
```

Cette commande liste les fichiers enregistrés pour le paquet installé.

Pour identifier le propriétaire d'un fichier :

```bash
rpm -qf /chemin/du/fichier
```

## 23.4. Examiner la transaction historique

DNF fournit une fonction d'historique :

```bash
dnf history
```

Elle permet d'examiner les transactions enregistrées.

Pour les détails d'une transaction :

```bash
dnf history info ID
```

Remplace `ID` par l'identifiant réel de la transaction.

La documentation de DNF explique également les commandes d'annulation et les limites liées à l'état courant de la base RPM. Une opération d'annulation ne peut pas toujours être réalisée si l'état actuel ne permet pas de revenir à la situation précédente.

## 23.5. Rechercher les paquets disponibles dans les dépôts

```bash
dnf repoquery nom-du-paquet
```

`repoquery` recherche des informations dans les dépôts connus de DNF.

Les options disponibles varient selon la version de DNF.

## 23.6. Examiner les mises à jour

```bash
dnf check-update
```

Cette commande vérifie les mises à jour disponibles.

Dans certains cas, un code de retour `100` signifie que des mises à jour sont disponibles. Les scripts doivent traiter ce résultat selon la documentation de la version installée au lieu de considérer tout code non nul comme une panne.

## 23.7. Examiner l'intégrité des fichiers

```bash
rpm -V nom-du-paquet
```

Cette commande compare les attributs connus du paquet avec ceux des fichiers, lorsque les informations de vérification sont disponibles.

Les différences doivent être interprétées. Un fichier de configuration modifié volontairement peut produire une différence attendue.

## 23.8. Réparer une installation RPM

Une réparation dépend du message d'erreur, de la base locale, de la version de DNF et de l'état des paquets.

N'utilise pas une option de réparation au hasard. Examine d'abord :

- les journaux ;
- l'historique DNF ;
- les paquets en erreur ;
- les dépôts ;
- les versions ;
- les messages de dépendance.

Documentation : [DNF Command Reference](https://dnf.readthedocs.io/en/stable/command_ref.html).


# 24. Maintenance avancée avec Pacman

## 24.1. Mise à niveau cohérente du système

Arch Linux est une distribution à publication continue.

La mise à niveau du système doit être réalisée de façon cohérente.

La commande habituelle est :

```bash
sudo pacman -Syu
```

Elle synchronise les bases des dépôts puis met à niveau les paquets dans le cadre prévu par Pacman.

La documentation Arch Linux déconseille les mises à niveau partielles non prises en charge, par exemple synchroniser les bases puis installer seulement un paquet sans mettre à niveau le reste du système.

## 24.2. Pourquoi les mises à niveau partielles sont-elles risquées ?

Les paquets d'Arch Linux sont préparés pour fonctionner avec l'état cohérent des bibliothèques et composants publiés dans les dépôts.

Mettre à niveau une bibliothèque sans les logiciels qui dépendent de son ancienne version peut entraîner des incompatibilités.

Il faut donc suivre la procédure documentée de la distribution et éviter les combinaisons de paquets qui ne correspondent pas à un état cohérent des dépôts.

## 24.3. Examiner les paquets orphelins

```bash
pacman -Qtd
```

Cette commande peut aider à identifier des paquets installés comme dépendances dont plus aucun paquet ne dépend, selon la base locale.

Un paquet considéré orphelin n'est pas nécessairement inutile dans tous les usages. Il peut être requis manuellement par l'administrateur.

Vérifie son rôle avant de le supprimer.

## 24.4. Examiner les paquets étrangers

```bash
pacman -Qm
```

Cette commande liste des paquets locaux qui ne correspondent pas aux paquets présents dans les bases des dépôts synchronisées, selon la définition de Pacman.

La sortie peut inclure des paquets installés manuellement ou d'autres sources externes. Elle ne doit pas être interprétée comme une liste de logiciels malveillants.

## 24.5. Signatures des paquets

Pacman utilise des mécanismes de vérification des signatures, selon la configuration du système.

Une erreur de signature doit être diagnostiquée à partir des clés, de l'état du trousseau de confiance, des dépôts et de la documentation officielle.

Ne désactive pas les vérifications de signature pour contourner un problème.

Documentation : [ArchWiki — Pacman](https://wiki.archlinux.org/title/Pacman) et [ArchWiki — Package signing](https://wiki.archlinux.org/title/Pacman/Package_signing).


# 25. Bonnes pratiques en production

## 25.1. Toujours vérifier la portée

Avant une opération :

- identifier la machine ;
- connaître son rôle ;
- identifier les paquets concernés ;
- examiner la transaction ;
- comprendre les services dépendants ;
- vérifier les sauvegardes ;
- prévoir les contrôles après intervention.

## 25.2. Ne pas modifier les sources sans nécessité

Un nouveau dépôt peut affecter bien plus qu'un seul paquet.

Il peut changer la version candidate de dépendances partagées ou modifier le résultat de futures mises à jour.

Toute source ajoutée doit avoir une justification, une origine vérifiée et une politique de maintenance documentée.

## 25.3. Éviter les corrections qui masquent la cause

Exemples d'approches dangereuses :

- désactiver les vérifications de signature ;
- supprimer les verrous manuellement ;
- forcer des dépendances incompatibles ;
- mélanger des dépôts de versions différentes sans stratégie ;
- supprimer tous les fichiers d'une application à la main ;
- lancer des réparations automatiques sans lire les changements prévus.

La bonne pratique consiste à comprendre la cause de l'erreur puis à choisir la correction la plus ciblée.

## 25.4. Maintenir une trace

Un journal de maintenance doit mentionner :

```text
Date et heure :
Machine :
Distribution :
Sources concernées :
Paquets :
Versions avant :
Versions après :
Commandes :
Erreurs :
Services vérifiés :
Résultat :
Actions restantes :
```

Ce document facilite le diagnostic futur et la comparaison entre environnements.

## 25.5. Vérifier les services après une modification

L'installation d'un paquet ne suffit pas à prouver que le service fonctionne.

Sur un système utilisant `systemd` :

```bash
systemctl --failed
```

Puis, pour chaque unité critique concernée :

```bash
systemctl status nom.service
```

Si nécessaire :

```bash
journalctl -u nom.service -n 100 --no-pager
```

La validation doit aussi inclure un test fonctionnel correspondant à l'application lorsque cela est possible.


# 26. Travaux pratiques guidés

Les travaux pratiques sont conçus pour une machine de laboratoire Debian ou Ubuntu.

Lis les résultats simulés et les transactions proposées avant de confirmer des modifications.

## TP 1 — Examiner les versions et les sources

### Objectif

Comprendre pourquoi APT sélectionne une version particulière.

### Étape 1

```bash
sudo apt update
```

### Étape 2

```bash
apt-cache policy curl
```

### Étape 3

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' curl
```

### Étape 4

Compare :

- la version installée ;
- la version candidate ;
- les versions disponibles ;
- les priorités affichées ;
- les sources associées.

### Résultat attendu

Tu dois pouvoir expliquer si une mise à niveau est proposée et d'où provient la version candidate.


## TP 2 — Examiner les dépendances

### Objectif

Comprendre les dépendances directes et inversement déclarées.

### Étape 1

```bash
apt-cache depends curl
```

### Étape 2

Identifier une bibliothèque pertinente à partir du résultat.

### Étape 3

Examiner les dépendances inverses déclarées d'un paquet réellement présent :

```bash
apt-cache rdepends libcurl4
```

Si le nom diffère sur ta distribution, utilise le paquet réellement indiqué par les métadonnées disponibles.

### Étape 4

Simuler la suppression d'un paquet de laboratoire :

```bash
apt-get -s remove nom-du-paquet
```

### Résultat attendu

Tu dois comprendre pourquoi supprimer un paquet partagé peut affecter d'autres logiciels et pourquoi il faut examiner le plan de transaction.


## TP 3 — Simuler une mise à niveau

### Objectif

Examiner les changements prévus avant de modifier le système.

### Étape 1

```bash
sudo apt update
```

### Étape 2

```bash
apt list --upgradable
```

### Étape 3

```bash
apt-get -s upgrade
```

### Étape 4

Repérer les paquets prévus, les éventuels blocages et les messages d'avertissement.

### Étape 5

Dans un laboratoire, si tu souhaites réellement appliquer les mises à niveau et que tu as compris la transaction, exécute la procédure appropriée.

### Résultat attendu

Tu dois savoir distinguer une simulation d'une mise à niveau réelle.


## TP 4 — Examiner les paquets retenus

### Objectif

Comprendre l'effet d'une retenue sur une mise à jour.

### Étape 1

```bash
apt-mark showhold
```

### Étape 2

Si une retenue existe, identifie sa raison avant toute modification.

### Étape 3

Dans un laboratoire seulement, si le besoin de la retenue a été évalué, examine comment l'enlever :

```bash
sudo apt-mark unhold nom-du-paquet
```

### Étape 4

Vérifie ensuite les versions disponibles :

```bash
apt-cache policy nom-du-paquet
```

### Résultat attendu

Tu dois comprendre pourquoi les retenues doivent être documentées et révisées.


## TP 5 — Examiner un fichier DEB local

### Objectif

Comprendre ce qu'un fichier DEB déclare avant son installation.

### Étape 1

Utilise un fichier DEB provenant d'une source fiable et correspondant à ton système.

### Étape 2

Examiner les métadonnées :

```bash
dpkg-deb -I fichier.deb
```

### Étape 3

Lister le contenu :

```bash
dpkg-deb -c fichier.deb
```

### Étape 4

Examiner ses dépendances et son architecture.

### Étape 5

Ne procède à l'installation que si l'origine, la compatibilité et les changements sont compris.

### Résultat attendu

Tu dois pouvoir expliquer pourquoi l'extension `.deb` ne garantit ni la compatibilité ni la sécurité.


## TP 6 — Diagnostiquer un état de paquet

### Objectif

Savoir détecter des paquets nécessitant une attention particulière.

### Étape 1

```bash
dpkg --audit
```

### Étape 2

```bash
dpkg -l | less
```

### Étape 3

Si un paquet présente un état inhabituel, consulte sa fiche :

```bash
dpkg -s nom-du-paquet
```

### Étape 4

Examine les journaux APT et dpkg disponibles :

```bash
sudo tail -n 100 /var/log/dpkg.log
```

### Résultat attendu

Tu dois savoir identifier l'état enregistré d'un paquet et retrouver les informations nécessaires à son diagnostic.


## TP 7 — Produire un inventaire

### Objectif

Enregistrer les paquets installés et leurs versions.

### Étape 1

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n'
```

### Étape 2

Enregistrer le résultat dans un fichier de laboratoire :

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' \
    > inventaire-paquets.tsv
```

### Étape 3

Examiner le fichier :

```bash
less inventaire-paquets.tsv
```

### Étape 4

Expliquer pourquoi ce fichier ne remplace pas une sauvegarde de la configuration et des données applicatives.

### Résultat attendu

Tu dois pouvoir générer un inventaire de paquets exploitable pour comparer des machines ou documenter une maintenance.


# 27. Exercices d'application

Réponds aux questions avant de consulter la correction.

## Exercice 1 — Version candidate

Explique la différence entre la version installée, la version candidate et les versions disponibles.

Quelle commande aide à les examiner ?

## Exercice 2 — Dépendances

Explique la différence entre une dépendance directe et une dépendance transitive.

Pourquoi faut-il examiner les suppressions proposées par APT ?

## Exercice 3 — Priorités APT

À quoi sert le pinning ?

Pourquoi une règle de préférence trop large peut-elle être dangereuse ?

## Exercice 4 — Paquets retenus

Quelle commande affiche les paquets retenus ?

Pourquoi faut-il documenter les retenues ?

## Exercice 5 — Paquets manuels et automatiques

Quelle commande affiche les paquets marqués comme manuels ?

Quelle est la relation entre cet état et `autoremove` ?

## Exercice 6 — Transaction

Pourquoi une simulation de transaction ne remplace-t-elle pas une sauvegarde ?

## Exercice 7 — Dépôts tiers

Cite quatre vérifications à effectuer avant d'ajouter un dépôt tiers.

## Exercice 8 — Paquet local

Quelle est la différence entre `apt install ./fichier.deb` et `dpkg -i fichier.deb` ?

## Exercice 9 — État incomplet

Quelle commande permet d'examiner des paquets qui nécessitent une attention particulière ?

Quelle commande demande la configuration des paquets dépaquetés mais non configurés ?

## Exercice 10 — Dépendances cassées

Pourquoi `apt --fix-broken install` ne doit-il pas être exécuté sans lire les changements proposés ?

## Exercice 11 — Réinstallation

Quelle commande demande la réinstallation d'un paquet ?

Pourquoi cette action ne garantit-elle pas la réparation d'une application entière ?

## Exercice 12 — Journaux

Cite deux journaux permettant d'étudier les opérations de paquets sur Debian ou Ubuntu.

## Exercice 13 — Mises à jour automatiques

Pourquoi l'ajout d'un dépôt ne garantit-il pas qu'il sera pris en compte par les mises à jour automatiques ?

## Exercice 14 — Historique RPM

Quelle commande permet de consulter l'historique des transactions DNF ?

## Exercice 15 — Arch Linux

Pourquoi faut-il éviter les mises à niveau partielles non prises en charge dans Arch Linux ?

## Exercice 16 — Serveur de production

Cite au moins huit éléments à vérifier avant et après une mise à jour importante d'un serveur.


# 28. Corrections détaillées des exercices

## Correction 1 — Version candidate

La version installée est la version enregistrée localement.

La version candidate est celle qu'APT sélectionne pour l'installation ou la mise à niveau selon les informations disponibles et ses règles de sélection.

Les versions disponibles sont les versions connues dans les index des sources configurées.

La commande utile est :

```bash
apt-cache policy nom-du-paquet
```

## Correction 2 — Dépendances

Une dépendance directe est déclarée par le paquet lui-même.

Une dépendance transitive est nécessaire parce qu'un autre composant dont dépend le paquet en a besoin.

Les suppressions proposées doivent être examinées, car elles peuvent concerner des bibliothèques ou des composants utilisés par d'autres logiciels.

## Correction 3 — Priorités APT

Le pinning permet d'influencer la sélection des versions et des origines.

Une règle trop large peut faire sélectionner des versions inattendues, provoquer des conflits ou rendre une mise à niveau incohérente.

## Correction 4 — Paquets retenus

La commande est :

```bash
apt-mark showhold
```

Les retenues doivent être documentées parce qu'elles peuvent bloquer des mises à jour et maintenir une ancienne version.

## Correction 5 — Paquets manuels et automatiques

La commande est :

```bash
apt-mark showmanual
```

Les paquets marqués comme automatiques peuvent être proposés par `autoremove` lorsqu'APT les considère inutiles selon les dépendances connues.

## Correction 6 — Transaction

La simulation montre les changements prévus selon l'état courant du gestionnaire, mais elle ne protège pas contre un problème de données, une panne matérielle, un défaut logiciel ou une modification imprévue.

Elle ne remplace donc pas une sauvegarde testée.

## Correction 7 — Dépôts tiers

Les vérifications peuvent comprendre :

1. vérifier l'origine et le propriétaire ;
2. confirmer la compatibilité avec la distribution ;
3. examiner les clés et mécanismes de signature ;
4. consulter les versions et dépendances fournies ;
5. lire la politique de maintenance ;
6. simuler les opérations importantes ;
7. évaluer les conséquences sur les futures mises à niveau.

## Correction 8 — Paquet local

`apt install ./fichier.deb` permet à APT de gérer la transaction et de tenter de résoudre les dépendances à partir des sources configurées.

`dpkg -i fichier.deb` installe le paquet de bas niveau et peut laisser des dépendances non satisfaites.

## Correction 9 — État incomplet

Pour examiner les paquets nécessitant une attention particulière :

```bash
dpkg --audit
```

Pour demander la configuration des paquets dépaquetés mais non configurés :

```bash
sudo dpkg --configure -a
```

Cette dernière commande peut encore échouer si le problème sous-jacent n'est pas résolu.

## Correction 10 — Dépendances cassées

La commande peut proposer plusieurs installations ou suppressions. Il faut donc vérifier la liste et comprendre les dépendances avant de confirmer.

Une réparation automatique ne garantit pas que le résultat soit adapté à tous les besoins d'exploitation.

## Correction 11 — Réinstallation

La commande est :

```bash
sudo apt install --reinstall nom-du-paquet
```

Elle réinstalle le paquet, mais ne corrige pas nécessairement les fichiers de configuration, les données, les permissions et les dépendances externes.

## Correction 12 — Journaux

Deux journaux courants sont :

```text
/var/log/apt/history.log
/var/log/dpkg.log
```

Leur présence et leurs contenus dépendent de l'historique et de la configuration.

## Correction 13 — Mises à jour automatiques

Le mécanisme de mise à jour automatique applique les origines et catégories autorisées par sa configuration.

Il faut vérifier les sources qu'il prend en compte et ne pas supposer qu'un nouveau dépôt est inclus automatiquement.

## Correction 14 — Historique RPM

La commande est :

```bash
dnf history
```

Elle affiche les transactions connues du gestionnaire.

## Correction 15 — Arch Linux

Les paquets et bibliothèques d'une distribution à publication continue sont maintenus dans un ensemble cohérent.

Une mise à niveau partielle peut créer des incompatibilités entre une bibliothèque mise à jour et les logiciels qui en dépendent.

## Correction 16 — Serveur de production

Une bonne réponse comprend notamment :

1. identification du système ;
2. contrôle des dépôts et versions ;
3. examen des transactions proposées ;
4. vérification des dépendances ;
5. sauvegarde des données et configurations pertinentes ;
6. vérification de l'espace disque ;
7. planification de la maintenance ;
8. relevé des versions avant intervention ;
9. vérification des services après mise à niveau ;
10. consultation des journaux ;
11. test fonctionnel ;
12. documentation du résultat et des actions restantes.


# 29. Défi final : maintenance contrôlée d'un serveur

## 29.1. Contexte

Tu dois assurer la maintenance d'un serveur Debian ou Ubuntu qui héberge plusieurs services.

L'équipe indique que :

```text
SITUATION A
Des mises à jour sont disponibles.

SITUATION B
Un paquet utilisé par une application semble être retenu.

SITUATION C
Une ancienne installation de logiciel a échoué.

SITUATION D
Un administrateur souhaite installer un paquet DEB local.

SITUATION E
Le résultat doit être documenté avant et après intervention.
```

Les informations sont volontairement incomplètes : il faut examiner l'état réel du système avant de décider d'une correction.

## 29.2. Mission

Réalise une procédure de diagnostic qui permette :

1. d'identifier le système et son architecture ;
2. d'examiner les sources APT ;
3. d'identifier les mises à jour disponibles ;
4. d'examiner les paquets retenus ;
5. de rechercher le paquet concerné ;
6. d'examiner l'état de `dpkg` ;
7. de retrouver l'erreur de l'installation précédente ;
8. d'examiner le paquet DEB local avant installation ;
9. de simuler la transaction ;
10. d'appliquer uniquement les opérations justifiées ;
11. de vérifier l'état final ;
12. de rédiger un compte rendu.

## 29.3. Contraintes

- Ne retire pas toutes les retenues sans comprendre leur objectif.
- Ne force pas l'installation du paquet DEB.
- Ne désactive pas les contrôles d'authenticité.
- Ne supprime pas manuellement les fichiers de verrou.
- Ne lance pas une réparation APT sans lire le plan proposé.
- Ne prétends pas qu'une opération a été effectuée si elle a seulement été simulée.
- Vérifie le fonctionnement des services concernés après intervention.


# 30. Correction détaillée du défi final

## 30.1. Étape 1 — Identifier le système

```bash
cat /etc/os-release
```

Puis :

```bash
uname -r
```

Et :

```bash
dpkg --print-architecture
```

Ces informations permettent de confirmer la distribution, la version et l'architecture de paquetage.

## 30.2. Étape 2 — Examiner les sources

```bash
find /etc/apt -maxdepth 2 -type f \
    \( -name '*.list' -o -name '*.sources' \) -print
```

Lis les fichiers pertinents.

Identifie les sources officielles, les sources tierces, les suites de distribution et les paramètres de signature.

Ne modifie pas encore les sources si aucune cause ne le justifie.

## 30.3. Étape 3 — Actualiser les index et contrôler les mises à jour

```bash
sudo apt update
```

Lis les résultats et traite les erreurs de source avant de continuer.

Puis :

```bash
apt list --upgradable
```

Cette commande présente les mises à niveau proposées selon les index disponibles.

## 30.4. Étape 4 — Examiner les retenues

```bash
apt-mark showhold
```

Identifie le paquet signalé.

Avant de retirer sa retenue, recherche la raison de cette décision : une incompatibilité applicative peut avoir conduit à la placer.

## 30.5. Étape 5 — Examiner les versions

```bash
apt-cache policy nom-du-paquet
```

Puis :

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' nom-du-paquet
```

Compare les versions installées et candidates, et vérifie la source de la version envisagée.

## 30.6. Étape 6 — Examiner l'état de la base

```bash
dpkg --audit
```

Si un paquet est en état inhabituel, consulte :

```bash
dpkg -s nom-du-paquet
```

Puis examine les journaux pertinents :

```bash
sudo tail -n 100 /var/log/dpkg.log
```

```bash
sudo tail -n 100 /var/log/apt/term.log
```

Les fichiers de journal peuvent être absents ou avoir été archivés. Il faut rechercher les traces disponibles sur la période de l'incident.

## 30.7. Étape 7 — Examiner le paquet local

```bash
dpkg-deb -I fichier.deb
```

Puis :

```bash
dpkg-deb -c fichier.deb
```

Vérifie l'origine, l'architecture, la version et les dépendances déclarées.

Si le paquet est incompatible ou provient d'une source non vérifiée, ne l'installe pas.

## 30.8. Étape 8 — Simuler l'installation

```bash
apt-get -s install ./fichier.deb
```

Si la simulation propose des suppressions ou des changements importants, arrête-toi et examine leurs causes.

La simulation ne dispense pas des vérifications de provenance et de compatibilité.

## 30.9. Étape 9 — Appliquer la correction adaptée

La correction dépend des preuves collectées.

Exemples :

- si le paquet est retenu sans raison encore connue, retrouver d'abord la raison de la retenue ;
- si le dépôt est incorrect, corriger la source conformément à sa documentation officielle ;
- si la base est incohérente, identifier l'erreur de configuration ou de dépendance ;
- si le paquet local n'est pas compatible, rechercher une version adaptée ;
- si une dépendance manque, vérifier sa disponibilité et la transaction prévue.

Il n'existe pas une commande universelle permettant de corriger toutes ces situations.

## 30.10. Étape 10 — Vérifier la transaction

Après l'opération retenue :

```bash
dpkg --audit
```

Puis, pour le paquet concerné :

```bash
dpkg -s nom-du-paquet
```

Vérifie sa version :

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' nom-du-paquet
```

Si un service dépend du paquet :

```bash
systemctl status nom.service
```

Et :

```bash
journalctl -u nom.service -n 100 --no-pager
```

La validation doit inclure le fonctionnement réel du service lorsqu'un test approprié est disponible.

## 30.11. Étape 11 — Construire le rapport

```text
RAPPORT DE MAINTENANCE DES PAQUETS

1. Système
   Distribution :
   Version :
   Architecture :

2. Sources
   Fichiers examinés :
   Sources concernées :
   Erreurs éventuelles :

3. Paquets
   Paquets concernés :
   Versions installées :
   Versions candidates :
   Retenues :
   Dépendances importantes :

4. Diagnostic
   État dpkg :
   Journaux examinés :
   Cause confirmée :
   Hypothèses restantes :

5. Simulation
   Commande :
   Changements proposés :
   Risques examinés :

6. Intervention
   Action réellement exécutée :
   Heure :
   Résultat :

7. Validation
   Statut final des paquets :
   Services contrôlés :
   Tests fonctionnels :
   Erreurs restantes :

8. Conclusion
   Résultat :
   Actions complémentaires :
   Mesures préventives :
```

Le rapport doit séparer les faits observés des hypothèses et des actions qui ont réellement été exécutées.


# 31. Checklist de compétences

## Gestion des versions et dépendances

- [ ] Je sais distinguer version installée, version candidate et versions disponibles.
- [ ] Je comprends les règles générales de comparaison des versions Debian.
- [ ] Je sais examiner les dépendances directes et inverses.
- [ ] Je comprends les relations de dépendance et les conflits.
- [ ] Je sais pourquoi la suppression d'une bibliothèque peut affecter plusieurs applications.

## APT et dpkg

- [ ] Je sais simuler une installation, une suppression et une mise à niveau.
- [ ] Je sais examiner les priorités avec `apt-cache policy`.
- [ ] Je comprends le rôle des préférences APT.
- [ ] Je sais examiner les paquets retenus.
- [ ] Je comprends les marqueurs d'installation manuelle et automatique.
- [ ] Je sais examiner un paquet local avant installation.
- [ ] Je comprends les états de `dpkg`.
- [ ] Je sais utiliser `dpkg --audit`.
- [ ] Je sais examiner les journaux APT et dpkg.

## Dépôts et sécurité

- [ ] Je sais examiner les fichiers de sources APT.
- [ ] Je comprends les risques du mélange de dépôts incompatibles.
- [ ] Je vérifie l'origine des paquets locaux.
- [ ] Je ne désactive pas les vérifications d'authenticité pour contourner une erreur.
- [ ] Je sais vérifier quelles sources sont prises en compte par les mises à jour automatiques.
- [ ] Je sais contrôler les services après une mise à jour importante.

## Automatisation et maintenance

- [ ] Je peux générer un inventaire des paquets installés.
- [ ] Je sais valider les arguments d'un script de maintenance.
- [ ] Je comprends pourquoi il faut distinguer une absence de résultat d'une erreur.
- [ ] Je sais pourquoi une simulation ne remplace pas une sauvegarde.
- [ ] Je peux rédiger un compte rendu de maintenance reproductible.
- [ ] Je sais pourquoi il ne faut pas supprimer manuellement un verrou de paquet.

## Autres distributions

- [ ] Je sais examiner les transactions DNF.
- [ ] Je comprends la vérification de fichiers avec RPM.
- [ ] Je comprends l'importance d'une mise à niveau cohérente avec Pacman.
- [ ] Je sais que les commandes ne sont pas interchangeables entre familles de distributions.


# 32. Fiche de révision

## Informations du système

```bash
cat /etc/os-release
```

```bash
dpkg --print-architecture
```

## Versions et dépendances

```bash
apt-cache policy nom
```

```bash
apt-cache depends nom
```

```bash
apt-cache rdepends nom
```

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' nom
```

## Simulation

```bash
apt-get -s install nom
```

```bash
apt-get -s remove nom
```

```bash
apt-get -s upgrade
```

```bash
apt-get -s dist-upgrade
```

## Retenues et états

```bash
apt-mark showhold
```

```bash
apt-mark showmanual
```

```bash
apt-mark showauto
```

```bash
dpkg --audit
```

## Paquet local

```bash
dpkg-deb -I fichier.deb
```

```bash
dpkg-deb -c fichier.deb
```

```bash
sudo apt install ./fichier.deb
```

## Réparation

```bash
sudo dpkg --configure -a
```

```bash
sudo apt --fix-broken install
```

Ces commandes doivent être utilisées après avoir identifié la cause du problème et examiné les changements proposés.

## Fichiers et vérification

```bash
dpkg -L nom
```

```bash
dpkg -S /chemin/du/fichier
```

```bash
dpkg --verify nom
```

```bash
sudo apt install --reinstall nom
```

## Mises à jour

```bash
sudo apt update
```

```bash
apt list --upgradable
```

```bash
sudo apt upgrade
```

## Journaux

```bash
sudo less /var/log/apt/history.log
```

```bash
sudo less /var/log/dpkg.log
```


# 33. Glossaire

**APT :** ensemble d'outils de gestion de paquets de haut niveau utilisé par Debian et ses dérivées.

**Base locale :** informations enregistrées sur les paquets connus par le gestionnaire local.

**Candidat :** version qu'APT sélectionne pour une installation ou une mise à niveau selon les versions et priorités disponibles.

**Conffile :** fichier de configuration suivi par le mécanisme de paquetage Debian.

**Dépendance directe :** dépendance déclarée par le paquet étudié.

**Dépendance transitive :** dépendance nécessaire indirectement, via un autre paquet.

**Dépôt :** source de paquets et de métadonnées.

**`dpkg` :** outil de bas niveau chargé des opérations sur les paquets Debian.

**`dpkg --audit` :** commande qui peut signaler des paquets nécessitant une attention particulière.

**Pinning :** mécanisme de préférences permettant d'influencer la sélection des versions et origines par APT.

**Paquet automatique :** paquet marqué comme installé automatiquement, souvent pour satisfaire une dépendance.

**Paquet manuel :** paquet marqué comme explicitement installé par l'administrateur.

**Paquet retenu :** paquet dont la mise à niveau ordinaire est empêchée par un mécanisme de retenue.

**Paquet virtuel :** capacité fournie par un ou plusieurs paquets concrets selon les relations déclarées.

**Purge :** suppression d'un paquet avec demande de suppression des fichiers de configuration gérés.

**Rétroportage :** paquet adapté à une version de distribution à partir d'un logiciel ou d'une branche plus récente, selon la politique du dépôt.

**Signature :** mécanisme cryptographique permettant de vérifier l'authenticité de données selon une chaîne de confiance.

**Transaction :** ensemble cohérent d'opérations de gestion de paquets.

**Version installée :** version actuellement enregistrée dans la base locale.

**Version candidate :** version qu'APT privilégie selon les informations et règles de sélection.


# 34. Documentation de référence

## Debian et Ubuntu

1. Documentation Ubuntu Server — gestion des paquets  
   https://ubuntu.com/server/docs/how-to/software/package-management/

2. Manuel Debian — `apt_preferences`  
   https://manpages.debian.org/bookworm/apt/apt_preferences.5.en.html

3. Manuel Debian — `dpkg-query`  
   https://manpages.debian.org/bookworm/dpkg/dpkg-query.1.en.html

4. Manuel Debian — `dpkg-deb`  
   https://manpages.debian.org/bookworm/dpkg/dpkg-deb.1.en.html

5. Documentation Ubuntu — mises à jour automatiques  
   https://ubuntu.com/server/docs/how-to/software/automatic-updates/

6. Documentation Ubuntu — sécurité et mises à jour  
   https://documentation.ubuntu.com/security/security-updates/

## Fedora et RPM

7. Documentation officielle DNF — référence des commandes  
   https://dnf.readthedocs.io/en/stable/command_ref.html

8. Documentation officielle RPM  
   https://rpm.org/docs/

## Arch Linux

9. ArchWiki — Pacman  
   https://wiki.archlinux.org/title/Pacman

10. ArchWiki — mises à niveau partielles  
    https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported

Les comportements précis peuvent varier selon la version de la distribution et de ses outils. En cas de différence, consulte le manuel local et la documentation officielle correspondant à la version réellement installée.


# Conclusion générale

La gestion intermédiaire des paquets exige de comprendre le comportement du solveur de dépendances, la sélection des versions, l'origine des paquets et les états de la base locale.

Tu sais maintenant examiner les versions candidates, diagnostiquer les conflits, contrôler les paquets retenus, simuler les transactions et retrouver les causes d'une installation incomplète. Tu as également étudié les dépôts tiers, les signatures, les mises à jour de sécurité, l'historique des transactions et la création d'inventaires.

La méthode essentielle demeure :

```text
IDENTIFIER LE SYSTÈME
          |
          v
EXAMINER LES SOURCES
          |
          v
CONNAÎTRE L'ÉTAT LOCAL
          |
          v
COMPRENDRE LES VERSIONS ET DÉPENDANCES
          |
          v
SIMULER LES CHANGEMENTS
          |
          v
ÉVALUER LES RISQUES
          |
          v
APPLIQUER UNE MODIFICATION JUSTIFIÉE
          |
          v
VÉRIFIER LES PAQUETS ET LES SERVICES
          |
          v
DOCUMENTER
```

**Un administrateur intermédiaire ne se contente pas de lancer les commandes d'installation et de mise à jour. Il comprend pourquoi une version est choisie, quelles dépendances seront touchées, comment retrouver un état incohérent et comment effectuer une maintenance contrôlée sans perdre la cohérence du système.**