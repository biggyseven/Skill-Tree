# Gestion experte des paquets Linux

> **Fichier :** `packages-expert.md`  
> **Niveau :** Expert  
> **Domaine :** Administration système, ingénierie des paquets, sécurité de la chaîne d'approvisionnement et maintenance logicielle  
> **Systèmes principaux :** Debian et Ubuntu  
> **Systèmes complémentaires :** Fedora/RHEL et Arch Linux  
> **Prérequis :** Maîtriser `packages-debutant.md` et `packages-intermediaire.md`. Connaître les services Linux, les permissions, les journaux, Bash, les dépendances et les procédures de sauvegarde.


# Sommaire

1. Objectifs et périmètre du niveau expert
2. Architecture complète du système de paquetage Debian
3. Cycle de vie interne d'une transaction APT/dpkg
4. États avancés de dpkg, scripts de maintenance et déclencheurs
5. Résolution experte des dépendances
6. Algorithme de sélection des versions APT
7. Pinning, priorités et contrôle des versions
8. Sources APT, deb822 et politiques de confiance
9. Chaîne de confiance, signatures et sécurité des dépôts
10. Vérification de l'intégrité des fichiers installés
11. Paquets locaux, versions particulières et rétrogradation
12. Réparation avancée d'un système de paquets incohérent
13. Suppressions, diversions, alternatives et fichiers partagés
14. Mises à jour de sécurité et gestion des vulnérabilités
15. Mises à jour automatiques et maintenance planifiée
16. Déploiement de paquets sur plusieurs serveurs
17. Inventaire, reproductibilité et gestion de configuration
18. Acquisition de paquets, caches et environnements hors ligne
19. Construction de paquets Debian à partir des sources
20. Dépôts internes et distribution d'entreprise
21. Gestion experte des paquets RPM avec DNF
22. Gestion experte des paquets Arch Linux avec Pacman
23. Systèmes immuables et mises à jour atomiques
24. Sécurité de la chaîne d'approvisionnement logicielle
25. Scripts avancés et automatisation contrôlée
26. Méthodologie de dépannage expert
27. Travaux pratiques guidés
28. Exercices d'application
29. Corrections détaillées
30. Défi final : gouvernance des paquets d'un parc Linux
31. Correction détaillée du défi final
32. Checklist de compétences expertes
33. Fiche de référence des commandes
34. Glossaire technique
35. Documentation officielle


# 1. Objectifs et périmètre du niveau expert

## 1.1. Passer de l'administration des paquets à l'ingénierie logicielle du système

Au niveau débutant, on apprend à installer et supprimer un logiciel.

Au niveau intermédiaire, on analyse les dépendances, les versions candidates, les dépôts, les paquets retenus et les erreurs de configuration.

Au niveau expert, on doit pouvoir expliquer et maîtriser l'ensemble du cycle de vie des composants logiciels qui constituent un système Linux.

Les situations suivantes relèvent de ce niveau :

- plusieurs dépôts proposent des versions incompatibles d'une bibliothèque ;
- une mise à jour entraîne une modification importante de l'arbre des dépendances ;
- une installation échoue pendant un script de maintenance ;
- la base `dpkg` contient des paquets partiellement configurés ;
- une mise à jour de sécurité doit être déployée sur plusieurs serveurs ;
- une nouvelle version doit être évaluée avant son déploiement en production ;
- une application exige une version particulière d'une bibliothèque ;
- des fichiers système ont été modifiés en dehors du gestionnaire de paquets ;
- une organisation doit reconstruire un environnement logiciel connu ;
- un dépôt tiers compromet la cohérence des versions ;
- des paquets doivent être distribués dans un réseau isolé ;
- une mise à jour doit être annulée alors que des données applicatives ont éventuellement évolué ;
- un incident nécessite de déterminer précisément quel paquet a modifié un fichier ou une dépendance.

Le rôle de l'administrateur expert consiste à comprendre les mécanismes, à établir une politique de maintenance, à maîtriser les risques et à prouver que l'état final est acceptable.

## 1.2. Les cinq dimensions de la gestion experte

```text
GESTION EXPERTE DES PAQUETS
|
+-- 1. Cohérence
|      +-- Dépendances
|      +-- Versions
|      +-- Architecture
|
+-- 2. Sécurité
|      +-- Signatures
|      +-- Provenance
|      +-- Correctifs
|      +-- Chaîne d'approvisionnement
|
+-- 3. Fiabilité
|      +-- Transactions
|      +-- Sauvegardes
|      +-- Restauration
|      +-- Vérification post-installation
|
+-- 4. Reproductibilité
|      +-- Inventaire
|      +-- Sources
|      +-- Versions
|      +-- Configuration
|
+-- 5. Gouvernance
       +-- Fenêtres de maintenance
       +-- Validation
       +-- Déploiement
       +-- Traçabilité
```

Ces dimensions sont liées. Un système qui possède les dernières versions disponibles n'est pas nécessairement un système cohérent, correctement configuré ou adapté à une application métier.

## 1.3. Principes non négociables

Dans les exemples de ce cours, les principes suivants doivent être appliqués :

1. Examiner avant de modifier.
2. Vérifier les sources avant d'accorder sa confiance.
3. Simuler les transactions lorsqu'une opération peut modifier plusieurs paquets.
4. Ne pas confondre une mise à jour de paquets avec une mise à niveau de distribution.
5. Ne pas employer les options de forçage pour contourner un problème mal compris.
6. Sauvegarder les données et configurations pertinentes.
7. Vérifier les services et les fonctions applicatives après une modification importante.
8. Documenter les versions, les commandes et le résultat.
9. Éviter de lancer simultanément plusieurs opérations incompatibles de gestion de paquets.
10. Traiter les scripts d'installation et les paquets locaux comme du code pouvant avoir un impact privilégié.


# 2. Architecture complète du système de paquetage Debian

## 2.1. Les composants

Sur Debian et Ubuntu, la gestion des paquets associe plusieurs mécanismes.

| Composant | Fonction principale |
|---|---|
| Dépôts | Héberger des paquets et métadonnées |
| Index APT | Décrire les versions et les relations disponibles |
| APT | Sélectionner les versions et résoudre les dépendances |
| `dpkg` | Dépaqueter, configurer et enregistrer les paquets |
| Base locale | Conserver les informations sur l'état des paquets |
| Scripts de maintenance | Effectuer des opérations prévues lors des transactions |
| Services système | Exploiter certains logiciels installés |
| Journaux | Permettre de retracer les changements et les erreurs |

L'ensemble forme une chaîne de gestion logicielle.

```text
DÉPÔTS
  |
  v
MÉTADONNÉES SIGNÉES
  |
  v
INDEX APT
  |
  v
SÉLECTION DES VERSIONS
  |
  v
RÉSOLUTION DES DÉPENDANCES
  |
  v
TÉLÉCHARGEMENT DES PAQUETS
  |
  v
VÉRIFICATION PRÉVUE
  |
  v
DPKG : DÉPAQUETAGE ET CONFIGURATION
  |
  v
BASE LOCALE ET SYSTÈME DE FICHIERS
  |
  v
VÉRIFICATION DES SERVICES
```

Les mécanismes réels comportent des étapes supplémentaires, mais ce schéma permet de distinguer la sélection des paquets de leur installation effective.

## 2.2. Les index ne sont pas les paquets

La commande :

```bash
sudo apt update
```

actualise les index des sources configurées.

Elle ne télécharge pas nécessairement le contenu de tous les paquets et ne les installe pas.

Les index servent à connaître ce que les dépôts proposent.

La commande :

```bash
apt-cache policy nom-du-paquet
```

permet ensuite d'examiner certaines versions connues, leurs origines et leurs priorités.

## 2.3. Base locale et dépôts distants

La base locale de `dpkg` décrit les paquets connus du système.

Elle peut contenir des informations sur des paquets installés, supprimés partiellement ou conservant des éléments de configuration.

Les index APT décrivent ce que les sources configurées publient.

Ces deux états peuvent diverger :

```text
SOURCES DISTANTES
      |
      v
INDEX APT ACTUELS
      |
      +-- Version disponible : 4.2
      |
      v
BASE DPKG LOCALE
      |
      +-- Version installée : 4.1
      |
      v
ANALYSE DE LA MISE À NIVEAU
```

Une version disponible n'est pas nécessairement la version candidate, et la version candidate n'est pas nécessairement déjà installée.

## 2.4. Le répertoire de la base `dpkg`

La base locale de `dpkg` se trouve couramment sous :

```text
/var/lib/dpkg/
```

On y trouve notamment les informations d'état des paquets et les listes de fichiers enregistrés.

Les détails d'organisation sont liés à l'implémentation de `dpkg`.

**Ne modifie jamais directement les fichiers internes de la base pour contourner une erreur de gestion des paquets.** Utilise les interfaces documentées et les procédures de réparation appropriées.

La modification manuelle de ces fichiers peut créer un état contradictoire entre la base et le système de fichiers.

## 2.5. Les verrous et la cohérence

Les opérations APT et `dpkg` peuvent nécessiter des verrous afin de protéger les bases partagées contre des modifications concurrentes incompatibles.

Le verrou n'est pas simplement un obstacle à supprimer. Il protège un état qui pourrait être endommagé si plusieurs transactions modifiaient simultanément les mêmes structures.

Lorsqu'une opération échoue parce qu'un verrou est utilisé, il faut rechercher le processus responsable avant d'envisager une intervention.


# 3. Cycle de vie interne d'une transaction APT/dpkg

## 3.1. Une transaction dépasse l'installation des fichiers

Une transaction logicielle peut comprendre :

1. la lecture des sources et index ;
2. la sélection des versions ;
3. la résolution des dépendances ;
4. le téléchargement des archives ;
5. la vérification des informations d'authenticité et d'intégrité prévues ;
6. la préparation de l'installation ;
7. le dépaquetage ;
8. l'exécution des étapes de configuration ;
9. l'exécution des déclencheurs ;
10. l'enregistrement de l'état final.

Une erreur peut se produire à n'importe quelle étape.

C'est pourquoi le message initial doit être conservé lors d'un dépannage.

## 3.2. Préparation et résolution

Avant une installation, APT calcule une solution aux contraintes de dépendances disponibles.

Cette solution peut nécessiter des changements qui vont au-delà du seul paquet demandé.

Exemples :

- installer une nouvelle bibliothèque ;
- mettre à niveau une dépendance ;
- supprimer un paquet incompatible ;
- conserver une version particulière ;
- refuser la transaction si aucune solution acceptable n'existe.

Il faut examiner le plan proposé avant confirmation, surtout si l'opération concerne un serveur.

## 3.3. Dépaquetage et configuration

Le dépaquetage correspond à la mise en place des fichiers du paquet.

La configuration représente une étape distincte, qui peut comprendre des opérations de maintenance nécessaires à l'utilisation du logiciel.

Un paquet peut donc avoir des fichiers présents sur le disque alors que sa configuration n'est pas terminée.

Dans ce cas, la présence de l'exécutable n'est pas une preuve suffisante de réussite.

## 3.4. Déclencheurs

Debian utilise des mécanismes de déclencheurs (*triggers*) pour différer ou coordonner certaines opérations entre paquets.

Par exemple, des composants peuvent nécessiter la mise à jour de caches ou l'exécution d'outils de maintenance après l'installation de plusieurs paquets.

Le mécanisme évite de reproduire certaines opérations à chaque installation individuelle lorsque plusieurs transactions sont effectuées ensemble.

Un problème pendant le traitement d'un déclencheur peut entraîner une configuration qui semble incomplète.

Il faut lire les messages de `dpkg` et identifier l'opération concernée.

## 3.5. Les scripts de maintenance

Les paquets Debian peuvent fournir des scripts tels que :

```text
preinst
postinst
prerm
postrm
```

Leur rôle et leur ordre d'exécution dépendent de la transaction et de l'action effectuée.

Ces scripts peuvent notamment :

- préparer les fichiers ;
- créer ou mettre à jour des éléments nécessaires au service ;
- effectuer des opérations de migration prévues ;
- nettoyer certains composants ;
- intégrer le paquet à d'autres mécanismes du système.

Ces scripts s'exécutent dans un contexte qui peut disposer de privilèges élevés.

Un paquet doit donc être considéré comme du code potentiellement puissant, et non comme une simple archive de fichiers.

## 3.6. Que faire lorsqu'un script échoue ?

Il faut identifier :

- le paquet ;
- l'étape de maintenance ;
- le message d'erreur exact ;
- les commandes ou fichiers concernés ;
- les dépendances nécessaires ;
- l'état actuel du paquet ;
- les conséquences d'une nouvelle tentative.

Il ne faut pas contourner immédiatement l'échec avec un mécanisme de forçage.

La procédure consiste à corriger la cause, puis à relancer l'étape documentée lorsque cela est approprié.


# 4. États avancés de dpkg, scripts de maintenance et déclencheurs

## 4.1. Les états intermédiaires

`dpkg` enregistre différents états pour les paquets.

Certains sont normaux pendant une transaction, mais deviennent problématiques s'ils persistent après un échec.

Les commandes suivantes permettent une première inspection :

```bash
dpkg --audit
```

```bash
dpkg -l
```

```bash
dpkg -s nom-du-paquet
```

Pour les états détaillés, consulte :

```bash
man dpkg
```

Il faut distinguer l'action souhaitée, l'état courant et les indicateurs d'erreur lorsqu'ils sont affichés.

## 4.2. Identifier les paquets nécessitant une attention particulière

```bash
dpkg --audit
```

Cette commande peut signaler des paquets dépaquetés, partiellement configurés ou dans un état nécessitant une investigation.

Elle ne constitue pas une réparation complète et ne démontre pas que tous les fichiers de l'installation sont cohérents.

## 4.3. Récupérer une configuration interrompue

```bash
sudo dpkg --configure -a
```

Cette commande demande à `dpkg` de configurer les paquets dépaquetés mais non configurés qui peuvent être traités.

Elle peut échouer si une dépendance est absente, si un script échoue ou si l'environnement n'est pas dans l'état requis.

Elle doit donc être précédée d'un diagnostic lorsque l'échec initial est connu.

## 4.4. Différence entre réparation et forçage

Une réparation vise à restaurer un état cohérent en satisfaisant les dépendances et les étapes de configuration nécessaires.

Un forçage peut contourner certaines contraintes sans résoudre la cause.

Le fait qu'une commande parvienne à terminer une transaction ne signifie pas que l'ensemble du système soit cohérent.

Avant toute option de forçage, il faut connaître précisément la contrainte qu'elle contourne, le risque créé et la méthode de retour arrière.

## 4.5. Les déclencheurs en attente

Une transaction peut signaler qu'un traitement de déclencheur doit être achevé.

Dans un dépannage, recherche le nom du paquet ou du déclencheur signalé dans les messages.

Le problème peut être associé à une tâche de maintenance d'un autre paquet, pas nécessairement à celui initialement demandé.

Il faut donc examiner la transaction complète au lieu de considérer le premier nom affiché comme l'unique cause.


# 5. Résolution experte des dépendances

## 5.1. Le problème de satisfaction des contraintes

Un paquet ne peut être sélectionné indépendamment de ses relations avec les autres composants.

Une solution doit satisfaire les contraintes de dépendances, de versions, d'architecture, de conflits et de disponibilité.

```text
PAQUET A
  |
  +-- requiert B >= 3
  |
  +-- entre en conflit avec C < 2
  |
  v
APT CHERCHE UNE SOLUTION
  |
  +-- Sélection de versions
  +-- Vérification des relations
  +-- Analyse des conflits
  |
  v
TRANSACTION ACCEPTABLE OU ÉCHEC
```

Le solveur ne dispose que des métadonnées accessibles et des contraintes configurées. Une relation applicative non déclarée peut donc ne pas être prise en compte.

## 5.2. Dépendances de version

Les dépendances peuvent spécifier des opérateurs tels que :

- version supérieure ou égale ;
- version strictement supérieure ;
- version égale ;
- version inférieure ou égale ;
- version strictement inférieure.

La syntaxe et l'interprétation exacte dépendent du format de relation du paquet.

Une dépendance qui exige une version minimale peut rendre une installation impossible si la version requise n'est disponible dans aucune des sources configurées.

## 5.3. Dépendances virtuelles

Un paquet peut annoncer qu'il fournit une capacité abstraite.

Cela permet à d'autres paquets de dépendre d'une fonctionnalité sans exiger une implémentation unique.

Lorsqu'une dépendance virtuelle ne peut être résolue, il faut examiner les fournisseurs disponibles et les relations déclarées plutôt que d'installer arbitrairement un paquet ressemblant par son nom.

## 5.4. Conflicts, Breaks, Replaces et Provides

Ces relations représentent des contraintes différentes.

- `Conflicts` exprime une incompatibilité déclarée.
- `Breaks` indique notamment qu'une version de paquet ne peut pas fonctionner correctement avec certaines versions d'un autre paquet dans les conditions spécifiées.
- `Replaces` permet de décrire certains remplacements de fichiers ou de paquets.
- `Provides` annonce qu'un paquet fournit une capacité ou un nom virtuel.

Une résolution experte doit comprendre la relation qui provoque l'échec.

Il est dangereux de considérer tous ces champs comme des synonymes de « dépendance ».

## 5.5. Examiner la résolution

Commandes de diagnostic :

```bash
apt-cache depends nom-du-paquet
```

```bash
apt-cache rdepends nom-du-paquet
```

```bash
apt-cache policy nom-du-paquet
```

Simulation d'une installation avec sortie de diagnostic supplémentaire :

```bash
apt-get -s -o Debug::pkgProblemResolver=yes install nom-du-paquet
```

La sortie de débogage peut être volumineuse. Elle doit être interprétée à partir de la version d'APT installée et des métadonnées présentes.

Cette méthode permet d'examiner certains choix du solveur ; elle ne remplace pas l'analyse de la configuration des dépôts.

## 5.6. Les causes habituelles d'une impasse

- Mélange de dépôts incompatibles.
- Version installée plus récente que celles actuellement disponibles.
- Paquets retenus.
- Préférences APT trop larges.
- Dépendances absentes pour l'architecture.
- Paquets locaux prévus pour une autre version.
- Dépôt tiers en retard sur les dépendances.
- Base locale dans un état intermédiaire.
- Conflits de fichiers ou de versions.
- Transition de paquet incomplète.

La méthode consiste à identifier la contrainte précise, vérifier les versions disponibles, puis corriger la source ou la sélection plutôt que de forcer aveuglément l'installation.


# 6. Algorithme de sélection des versions APT

## 6.1. Les versions présentes dans les dépôts

Plusieurs dépôts peuvent proposer différentes versions d'un même paquet.

APT utilise les versions disponibles, les priorités et les contraintes de dépendances pour déterminer quelles versions sont candidates.

La commande :

```bash
apt-cache policy nom-du-paquet
```

constitue l'un des premiers outils à utiliser pour expliquer ce choix.

## 6.2. Version installée et version candidate

Les informations importantes sont :

- la version enregistrée localement ;
- la version candidate ;
- les versions disponibles dans les sources ;
- les priorités associées.

Une candidate n'est pas nécessairement la plus récente version publiée par le développeur du logiciel. Elle est sélectionnée selon les règles d'APT et les informations connues localement.

## 6.3. Comparer des versions correctement

Ne compare pas les versions Debian avec une comparaison lexicale de chaînes.

Utilise les règles de version de `dpkg` :

```bash
dpkg --compare-versions 1.10 gt 1.9
printf 'Code de retour : %s\n' "$?"
```

Pour ce test, `0` indique que la condition de comparaison est vraie.

Dans des scripts, il faut interpréter précisément les opérateurs et les codes de retour documentés.

## 6.4. Consulter les versions disponibles

Selon le système et les index accessibles :

```bash
apt-cache madison nom-du-paquet
```

Cette commande peut aider à lister les versions connues par les sources APT et certaines informations d'origine.

Pour une vue plus détaillée des priorités, utilise :

```bash
apt-cache policy nom-du-paquet
```

## 6.5. Version installée non disponible dans les dépôts

Une version installée peut ne plus apparaître dans les sources configurées, par exemple après un changement de dépôt ou une évolution de distribution.

Cela ne signifie pas nécessairement qu'elle est défectueuse.

Il faut identifier comment elle a été installée, si une version antérieure a été retirée du dépôt et quelles sont les implications pour la maintenance.

Un paquet installé provenant d'une source qui n'existe plus peut compliquer les mises à niveau et la reconstruction d'un système.


# 7. Pinning, priorités et contrôle des versions

## 7.1. Le pinning

Le pinning APT permet d'influencer la sélection des versions selon des règles de préférence.

La configuration se trouve généralement dans :

```text
/etc/apt/preferences
/etc/apt/preferences.d/
```

Ces fichiers permettent d'exprimer des priorités associées à des paquets, versions ou origines.

La syntaxe exacte doit être vérifiée dans la documentation de la version d'APT concernée.

## 7.2. Pourquoi le pinning est-il dangereux lorsqu'il est mal configuré ?

Une priorité trop large peut influencer de nombreux paquets au-delà du logiciel visé.

Conséquences possibles :

- choisir des versions inadaptées à la distribution ;
- extraire des dépendances d'une autre suite ;
- introduire des conflits de bibliothèques ;
- rendre les mises à niveau ultérieures difficiles ;
- sélectionner des versions inattendues pour des paquets essentiels.

Il faut limiter le périmètre de la règle et vérifier ses effets.

## 7.3. Exemple de structure de préférence

Une préférence APT peut utiliser des champs tels que :

```text
Package:
Pin:
Pin-Priority:
```

Cette structure est indicative, pas une règle opérationnelle complète.

Une configuration réelle doit indiquer clairement quels paquets ou quelles origines sont concernés, puis être testée.

Avant et après modification :

```bash
apt-cache policy nom-du-paquet
```

Puis simule la transaction :

```bash
apt-get -s install nom-du-paquet
```

## 7.4. Choisir une version précise

APT permet de demander une version particulière lorsqu'elle est disponible :

```bash
sudo apt install nom-du-paquet=VERSION
```

Remplace `VERSION` par une version réellement disponible.

Cette commande peut déclencher une résolution de dépendances plus large. Il faut examiner la transaction avant de confirmer.

La version demandée peut être absente, incompatible ou ne plus être disponible dans les sources configurées.

## 7.5. Épingler une version n'est pas un plan de maintenance

Une règle qui favorise une version ne dispense pas de :

- suivre les correctifs de sécurité ;
- réévaluer régulièrement le besoin ;
- vérifier les dépendances ;
- vérifier les sources ;
- documenter la raison de la règle ;
- supprimer la règle lorsqu'elle n'est plus utile.

Toute contrainte exceptionnelle sur les versions doit être documentée et révisée.

Documentation : [`apt_preferences(5)`](https://manpages.debian.org/bookworm/apt/apt_preferences.5.en.html).


# 8. Sources APT, deb822 et politiques de confiance

## 8.1. Les fichiers de sources

Les sources APT se trouvent couramment dans :

```text
/etc/apt/sources.list
/etc/apt/sources.list.d/
```

Les installations récentes utilisent souvent des fichiers de sources au format deb822, portant l'extension `.sources`.

Les anciennes installations ou certaines configurations continuent d'utiliser des fichiers `.list`.

Il faut examiner la configuration réelle, et non supposer qu'un unique fichier représente toutes les sources actives.

## 8.2. Format traditionnel

Une entrée classique peut comporter des éléments correspondant au type de source, à l'URI, à la suite et aux composants.

La syntaxe exacte doit suivre la documentation de la distribution et du dépôt.

## 8.3. Format deb822

Un fichier deb822 comporte des champs explicites. Selon le dépôt, ils peuvent inclure :

```text
Types:
URIs:
Suites:
Components:
Signed-By:
```

Cette structure décrit les paquets recherchés, leurs sources, les suites et les composants associés, ainsi que les paramètres de confiance lorsqu'ils sont précisés.

Les valeurs doivent provenir des instructions appropriées au système concerné.

## 8.4. Examiner toutes les sources

Pour inventorier les fichiers de sources :

```bash
find /etc/apt -maxdepth 2 -type f \
    \( -name '*.list' -o -name '*.sources' \) -print
```

Lis ensuite les fichiers identifiés.

Les fichiers de préférences APT doivent également être examinés si le comportement de sélection des versions est inattendu.

## 8.5. Mélanger des suites de distribution

Mélanger des dépôts de différentes versions de Debian ou Ubuntu peut entraîner des conflits de bibliothèques, des sélections de versions inattendues et des difficultés de maintenance.

La présence d'un paquet dans un dépôt ne signifie pas qu'il est approprié à la distribution installée.

Avant d'ajouter une source, vérifie :

- la version de distribution visée ;
- l'architecture ;
- les dépendances ;
- le calendrier de maintenance ;
- la chaîne de confiance ;
- les conséquences sur la version candidate des paquets existants.

## 8.6. Dépôts tiers

Un dépôt tiers peut être nécessaire lorsqu'un éditeur publie une version spécifique d'un logiciel.

Cependant, il introduit une source de code supplémentaire dans le système.

Il faut comprendre quels paquets il publie et à quelles versions des bibliothèques ils sont liés.

Un dépôt qui ne fournit qu'un seul logiciel peut également influencer les dépendances partagées si ses paquets proposent des versions différentes.

## 8.7. Vérification après modification

Après une modification de sources :

```bash
sudo apt update
```

Examine les avertissements et erreurs.

Puis :

```bash
apt-cache policy nom-du-paquet
```

Vérifie les nouvelles versions connues et les priorités.

Une source qui ne se met pas à jour correctement peut conduire à une sélection inattendue.


# 9. Chaîne de confiance, signatures et sécurité des dépôts

## 9.1. Un dépôt est une source de code

Installer un paquet peut introduire des exécutables, des bibliothèques et des scripts exécutés avec des privilèges élevés.

L'administrateur doit donc s'assurer que la source est authentique et digne de confiance.

La sécurité des paquets repose notamment sur :

- l'identification de la source ;
- la validation des métadonnées ;
- la vérification cryptographique prévue ;
- la gestion correcte des clés ;
- le suivi des correctifs ;
- la limitation des sources autorisées.

## 9.2. La chaîne de confiance APT

APT utilise des mécanismes de signatures et d'authenticité des métadonnées selon la configuration du dépôt.

L'objectif est de vérifier l'authenticité des informations qui permettent d'identifier les paquets disponibles.

La vérification cryptographique ne prouve pas que le logiciel est exempt de vulnérabilités : elle repose aussi sur la confiance accordée aux mainteneurs et aux clés.

## 9.3. `Signed-By`

Une source APT peut associer sa vérification à un trousseau de clés ou à un fichier de clés spécifique avec le mécanisme `Signed-By`.

Cela permet de limiter la portée de certaines clés à une source particulière.

Il faut suivre les instructions du fournisseur et vérifier que le fichier référencé contient la clé correcte.

Une clé ne doit pas être ajoutée à un espace de confiance global sans comprendre quels dépôts et paquets elle pourrait autoriser.

## 9.4. Éviter les méthodes de confiance trop larges

Une méthode qui permet à une clé tierce de signer indistinctement un grand nombre de sources peut augmenter inutilement le périmètre de confiance.

L'approche experte consiste à utiliser le mécanisme documenté qui limite l'autorité de la clé à la source prévue, lorsqu'il est disponible.

## 9.5. Ne pas contourner une erreur de signature

Lorsqu'APT signale une erreur de signature ou d'authenticité :

1. identifie le dépôt concerné ;
2. examine la configuration de la source ;
3. vérifie la procédure officielle de gestion de la clé ;
4. contrôle la date et l'état de la clé ;
5. vérifie la compatibilité de la source ;
6. réexécute la mise à jour après correction.

Ne désactive pas les vérifications de sécurité pour obtenir artificiellement une transaction réussie.

Documentation : [`apt-secure(8)`](https://manpages.debian.org/bookworm/apt/apt-secure.8.en.html).


# 10. Vérification de l'intégrité des fichiers installés

## 10.1. Base locale et contenu réel

La base de paquets décrit l'état attendu selon le gestionnaire.

Les fichiers réellement présents peuvent avoir été modifiés après l'installation par un administrateur, une application ou une autre opération.

Il faut distinguer les fichiers gérés par le paquet des fichiers générés ou modifiés pendant l'exploitation.

## 10.2. Lister les fichiers du paquet

```bash
dpkg -L nom-du-paquet
```

Pour identifier le paquet propriétaire d'un fichier :

```bash
dpkg -S /chemin/du/fichier
```

Ces commandes sont utiles lorsqu'un exécutable ou un fichier de configuration présente un comportement inattendu.

## 10.3. Vérifier certains attributs

```bash
dpkg --verify nom-du-paquet
```

Cette commande peut comparer certains attributs des fichiers avec les informations enregistrées, lorsque ces informations sont disponibles.

Le résultat ne constitue pas une attestation complète d'intégrité et de sécurité de tout le système.

Un fichier de configuration modifié volontairement peut présenter une différence attendue. Toutes les modifications possibles ne sont pas nécessairement détectées par ce mécanisme.

## 10.4. Utiliser `debsums`

Sur les systèmes compatibles, le paquet `debsums` peut fournir des vérifications supplémentaires par somme de contrôle pour les fichiers gérés par les paquets Debian.

S'il est installé :

```bash
debsums -s nom-du-paquet
```

Les possibilités dépendent du paquet, de ses sommes de contrôle enregistrées et de la configuration.

L'absence de sortie ne signifie pas nécessairement que tous les aspects du système sont sûrs.

## 10.5. Comparer les fichiers de configuration

Pour comprendre une configuration modifiée :

1. identifier le paquet propriétaire ;
2. examiner les fichiers gérés ;
3. consulter la documentation de l'application ;
4. rechercher les changements connus du paquet ;
5. comparer les paramètres attendus avec les paramètres présents ;
6. sauvegarder avant de remplacer un fichier ;
7. valider la configuration avec l'outil de l'application lorsqu'il existe.

Une réinstallation ne doit pas être considérée comme un moyen automatique de restaurer tous les fichiers de configuration à leur état par défaut.


# 11. Paquets locaux, versions particulières et rétrogradation

## 11.1. Installer un paquet DEB local

La méthode courante lorsqu'on veut installer un paquet DEB local avec résolution des dépendances est :

```bash
sudo apt install ./fichier.deb
```

Avant l'installation, inspecte le fichier :

```bash
dpkg-deb -I fichier.deb
```

Puis son contenu :

```bash
dpkg-deb -c fichier.deb
```

Ces vérifications permettent d'examiner le paquet, mais n'établissent pas à elles seules l'authenticité du fichier.

## 11.2. Vérifier l'architecture et les dépendances

Un paquet local peut être incompatible avec :

- l'architecture ;
- la distribution ;
- les versions des bibliothèques ;
- les dépendances disponibles ;
- les contraintes de sécurité.

La résolution d'APT n'annule pas les incompatibilités réelles du logiciel.

## 11.3. Installer une version précise

```bash
sudo apt install nom-du-paquet=VERSION
```

La version doit être réellement disponible et compatible avec le système.

Simule la transaction :

```bash
apt-get -s install nom-du-paquet=VERSION
```

Si le plan propose des suppressions importantes, arrête-toi et examine les dépendances et les origines.

## 11.4. Rétrograder un paquet

Une rétrogradation consiste à remplacer une version installée par une version antérieure.

APT permet de demander une version précise lorsque celle-ci est disponible :

```bash
sudo apt install nom-du-paquet=VERSION_ANTERIEURE
```

Mais la disponibilité de cette version, les contraintes de dépendances et les effets sur l'application doivent être vérifiés.

**La rétrogradation n'est pas toujours sûre.** Une version récente peut avoir modifié des formats de données, des bases de données ou des fichiers de configuration. Le retour au binaire précédent ne restaure pas automatiquement ces données.

## 11.5. Préparer un retour arrière

Avant une mise à jour importante :

- sauvegarde les données pertinentes ;
- conserve les fichiers de configuration ;
- relève les versions ;
- examine la disponibilité des anciennes versions ;
- vérifie les éventuelles migrations ;
- prépare une procédure de restauration ;
- teste cette procédure dans un environnement adapté.

Pour une application critique, un retour à un état antérieur peut nécessiter de restaurer les données et pas seulement les paquets.

## 11.6. La rétrogradation et les dépendances

Une version antérieure peut exiger une ancienne version d'une bibliothèque, qui peut ne plus être disponible dans les sources configurées.

La transaction doit donc être examinée dans son ensemble.

Le fait qu'une archive du paquet principal existe ne garantit pas que ses dépendances puissent être satisfaites.


# 12. Réparation avancée d'un système de paquets incohérent

## 12.1. Première règle : identifier l'état exact

Ne commence pas par lancer toutes les commandes de réparation connues.

Commence par relever :

```bash
dpkg --audit
```

Puis :

```bash
dpkg -l
```

Et examine le paquet en erreur :

```bash
dpkg -s nom-du-paquet
```

Cherche ensuite le message qui a déclenché la panne.

## 12.2. Examiner les journaux

Les fichiers courants comprennent :

```text
/var/log/dpkg.log
/var/log/apt/history.log
/var/log/apt/term.log
```

Leur disponibilité dépend de l'historique et de la configuration.

Consulte les lignes autour de l'heure de l'échec.

Il faut identifier l'étape qui a échoué : résolution, téléchargement, dépaquetage, configuration ou déclencheur.

## 12.3. Configurer les paquets en attente

Si la situation le justifie :

```bash
sudo dpkg --configure -a
```

Cette commande est adaptée aux paquets dépaquetés mais non configurés qui peuvent être traités.

Si une erreur persiste, analyse le message plutôt que de répéter la commande sans modification.

## 12.4. Réparer certaines dépendances cassées

```bash
sudo apt --fix-broken install
```

Cette commande peut tenter de résoudre les dépendances insatisfaites.

Examine le plan proposé avant confirmation, car il peut inclure des installations ou suppressions.

Il est essentiel de vérifier si la résolution proposée est cohérente avec la politique de maintenance du système.

## 12.5. Erreur de verrou

Si APT indique qu'un verrou est utilisé, identifie d'abord l'opération en cours.

```bash
ps -ef | grep -E '[a]pt|[d]pkg|[u]nattended-upgrade'
```

Examine les processus trouvés et leur activité.

Vérifie également, si ces unités sont présentes :

```bash
systemctl status apt-daily.service
```

```bash
systemctl status apt-daily-upgrade.service
```

Ne supprime pas manuellement les fichiers de verrou pour contourner une opération encore active.

## 12.6. Défaillance d'un script de maintenance

Si un script d'installation échoue, il faut identifier le paquet et l'étape en difficulté.

Une cause peut être externe au paquet initial : dépendance manquante, permission incorrecte, fichier absent ou service indisponible.

La réparation doit traiter la cause, puis relancer l'opération appropriée.

## 12.7. Éviter les modifications directes de la base

Ne modifie pas les fichiers internes de `/var/lib/dpkg/` pour faire disparaître un état d'erreur.

Les données internes assurent la cohérence entre les paquets, leurs fichiers et leur statut.

Une modification manuelle peut détruire les informations nécessaires aux outils de réparation.


# 13. Suppressions, diversions, alternatives et fichiers partagés

## 13.1. Les paquets ne sont pas les seuls responsables des fichiers du système

Un fichier peut être :

- fourni par un paquet ;
- généré par un service ;
- modifié par un administrateur ;
- créé par une installation externe ;
- déplacé ou redirigé par le mécanisme de paquetage.

La distinction est essentielle lorsqu'un fichier est absent, remplacé ou différent de la version attendue.

## 13.2. Les diversions de `dpkg`

Une diversion permet de gérer certains conflits ou remplacements de chemins entre paquets et fichiers du système.

Pour examiner les diversions enregistrées :

```bash
dpkg-divert --list
```

Les diversions sont un mécanisme avancé. Il ne faut pas en créer ou en supprimer sans comprendre les paquets concernés et les conséquences pour les fichiers.

## 13.3. `update-alternatives`

Certaines distributions utilisent le mécanisme `update-alternatives` pour gérer des choix entre plusieurs implémentations d'une commande ou d'une ressource.

Exemple :

```bash
update-alternatives --display editor
```

La disponibilité et les alternatives déclarées dépendent des paquets installés.

Ce mécanisme n'est pas un moyen de remplacer arbitrairement n'importe quel fichier. Il doit être utilisé pour les alternatives prévues par la distribution et les paquets concernés.

## 13.4. Pourquoi un fichier peut-il différer sans que le paquet soit cassé ?

Une différence peut provenir :

- d'une configuration locale ;
- d'une alternative sélectionnée ;
- d'une diversion ;
- d'une mise à jour ;
- d'une modification manuelle ;
- d'un fichier généré par le service.

Le diagnostic doit donc identifier le propriétaire du fichier et les mécanismes qui peuvent influencer le chemin ou son contenu.


# 14. Mises à jour de sécurité et gestion des vulnérabilités

## 14.1. Installer une mise à jour ne suffit pas toujours

La sécurité d'un logiciel dépend de sa version, du cycle de maintenance, des correctifs appliqués et de sa configuration.

Une version qui semble ancienne peut contenir les correctifs rétroportés par la distribution.

À l'inverse, un paquet qui paraît récent peut provenir d'une source non maintenue ou d'une version inadaptée à la distribution.

Il faut consulter les avis de sécurité de la distribution et les informations officielles relatives au paquet.

## 14.2. Mises à jour de sécurité et dépôts

Il faut identifier les sources de mises à jour réellement configurées.

Sur Ubuntu, les catégories de dépôts et la maintenance disponible dépendent de l'édition, de la version et éventuellement des services de maintenance supplémentaires.

La présence d'un paquet dans un dépôt communautaire ne garantit pas le même niveau de support que celui d'un dépôt officiellement maintenu.

## 14.3. Établir une priorité

Pour un inventaire de vulnérabilités, il faut notamment tenir compte :

- de la présence réelle du paquet ;
- de la version de distribution ;
- du statut de maintenance ;
- des correctifs disponibles ;
- de l'exposition du service ;
- de l'importance métier ;
- de l'existence d'une mitigation ;
- de la possibilité de tester et déployer la correction.

Le numéro de version seul ne suffit pas toujours à établir le statut de sécurité.

## 14.4. Examiner les mises à jour disponibles

Sur Debian ou Ubuntu :

```bash
sudo apt update
```

Puis :

```bash
apt list --upgradable
```

Ces commandes permettent d'actualiser les index et de voir les mises à niveau proposées.

Pour comprendre l'état de sécurité d'un paquet spécifique, consulte également les avis et informations officiels correspondant à la distribution installée.

## 14.5. Vérifier le service après correction

Après l'installation d'un correctif :

```bash
systemctl status nom.service
```

Puis :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Enfin, effectue un test fonctionnel adapté.

Une mise à jour peut être correctement installée mais laisser une application indisponible à cause d'une configuration ou d'une dépendance externe.


# 15. Mises à jour automatiques et maintenance planifiée

## 15.1. Le rôle d'`unattended-upgrades`

Sur Ubuntu, `unattended-upgrades` peut appliquer automatiquement des mises à jour selon la configuration en place.

Les fichiers de configuration courants incluent :

```text
/etc/apt/apt.conf.d/20auto-upgrades
/etc/apt/apt.conf.d/50unattended-upgrades
```

Le contenu effectif doit être examiné avant toute modification.

## 15.2. Pourquoi les sources comptent-elles ?

Ajouter un dépôt tiers ne signifie pas automatiquement que les mises à jour de ce dépôt seront appliquées par le mécanisme automatique.

Les origines autorisées doivent être examinées.

Il faut déterminer quelles sources sont prises en compte et quelle politique est appliquée aux paquets issus de chacune d'elles.

## 15.3. Journaux

Les journaux d'`unattended-upgrades` se trouvent couramment sous :

```text
/var/log/unattended-upgrades/
```

Pour examiner les fichiers présents :

```bash
sudo ls -l /var/log/unattended-upgrades/
```

Consulte ensuite les journaux qui correspondent à la période étudiée.

## 15.4. Paquets exclus des mises à jour automatiques

Une politique peut exclure certains paquets des mises à jour automatiques.

Cette exclusion doit être justifiée et suivie : une exclusion permanente peut maintenir une version vulnérable.

Bloquer un paquet peut aussi empêcher la mise à jour d'autres paquets dont il constitue une dépendance.

## 15.5. Redémarrages et services

Certaines mises à jour exigent un redémarrage ou une action sur un service.

Il faut identifier ce besoin et planifier une action adaptée.

Ne suppose pas que le système est entièrement à jour et fonctionnel simplement parce que l'installation des paquets a réussi.

Documentation officielle Ubuntu : [Automatic updates](https://ubuntu.com/server/docs/how-to/software/automatic-updates/).


# 16. Déploiement de paquets sur plusieurs serveurs

## 16.1. Pourquoi ne pas mettre à jour toutes les machines simultanément ?

Une mise à jour peut révéler un défaut applicatif, une incompatibilité ou une particularité de configuration.

Déployer sur toutes les machines en même temps peut transformer un problème limité en panne généralisée.

Il est préférable de travailler par étapes :

```text
VALIDATION EN LABORATOIRE
          |
          v
SERVEUR DE PRÉPRODUCTION
          |
          v
GROUPE PILOTE
          |
          v
DÉPLOIEMENT PROGRESSIF
          |
          v
CONTRÔLES ET OBSERVABILITÉ
          |
          v
GÉNÉRALISATION
```

Le nombre de groupes et les critères de passage dépendent du contexte.

## 16.2. Définir un état cible

Pour chaque groupe de serveurs, documente :

- la distribution ;
- la version ;
- l'architecture ;
- les dépôts autorisés ;
- les versions logicielles attendues ;
- les paquets retenus ;
- les services critiques ;
- les contraintes de redémarrage ;
- les vérifications post-maintenance.

Sans état cible défini, la comparaison entre machines devient difficile.

## 16.3. Comparer les inventaires

Sur Debian et Ubuntu :

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n'
```

Cette commande permet de générer un inventaire local.

La comparaison entre deux systèmes doit tenir compte de leur rôle. Un serveur Web et un serveur de base de données ne sont pas censés posséder exactement les mêmes paquets.

## 16.4. Déployer progressivement

Un déploiement progressif permet de surveiller :

- le taux d'échec ;
- le fonctionnement des services ;
- les journaux ;
- les performances ;
- les différences de versions ;
- les problèmes liés à l'environnement.

Les critères de généralisation doivent être définis avant le déploiement.

## 16.5. Gérer les différences de configuration

Deux serveurs peuvent posséder les mêmes versions de paquets tout en se comportant différemment à cause de fichiers de configuration, de données, de permissions ou de paramètres d'environnement.

Un inventaire logiciel ne remplace pas la gestion des configurations.

L'administrateur doit donc comparer les versions et les configurations pertinentes.


# 17. Inventaire, reproductibilité et gestion de configuration

## 17.1. Pourquoi un inventaire de paquets ne suffit-il pas ?

Une installation logicielle dépend de plusieurs éléments :

- distribution et version ;
- architecture ;
- dépôts configurés ;
- versions des paquets ;
- priorités APT ;
- configuration des logiciels ;
- données ;
- services ;
- environnement d'exécution.

Conserver uniquement la liste des noms de paquets ne garantit pas la reproduction exacte du système.

## 17.2. Exporter les paquets et versions

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' \
    > inventaire-paquets.tsv
```

Le fichier enregistre les informations de paquets connues au moment de l'export.

Il ne décrit pas les dépôts, les fichiers de configuration ou les données applicatives.

## 17.3. Exporter les paquets manuels

```bash
apt-mark showmanual > paquets-manuels.txt
```

Cette liste peut servir à documenter une partie des intentions d'installation.

Cependant, elle ne représente pas automatiquement l'ensemble des besoins métier de la machine.

## 17.4. Conserver la configuration des sources

Documente les fichiers de sources et de préférences pertinents.

Exemples de chemins :

```text
/etc/apt/sources.list
/etc/apt/sources.list.d/
/etc/apt/preferences
/etc/apt/preferences.d/
```

Leur contenu permet d'expliquer pourquoi certaines versions ont été sélectionnées.

Les clés et fichiers de confiance associés font également partie de la configuration pertinente.

## 17.5. Distinguer inventaire et sauvegarde

Un inventaire de paquets ne constitue pas une sauvegarde complète.

Pour restaurer un service, il faut éventuellement conserver :

- les données ;
- les fichiers de configuration ;
- les secrets stockés selon une procédure adaptée ;
- les paramètres des services ;
- les règles réseau ;
- les versions et sources de paquets ;
- les dépendances externes ;
- les éventuelles migrations de données.

## 17.6. Reproductibilité des environnements

La reproduction d'un environnement logiciel peut nécessiter un dépôt interne, des versions archivées, des fichiers de configuration déclaratifs et des procédures de restauration.

Elle peut aussi utiliser des outils de gestion de configuration, par exemple Ansible, ou des mécanismes de construction d'images.

Le but est de pouvoir expliquer et reconstruire l'état voulu au lieu de dépendre de manipulations manuelles non documentées.


# 18. Acquisition de paquets, caches et environnements hors ligne

## 18.1. Pourquoi préparer un dépôt ou un cache ?

Dans certains environnements, les machines ne peuvent pas télécharger directement des paquets depuis Internet.

Exemples :

- réseau d'entreprise isolé ;
- environnement industriel ;
- laboratoire contrôlé ;
- serveur sans accès externe ;
- déploiement sur un grand nombre de machines.

Il peut alors être nécessaire de préparer les paquets sur un système intermédiaire.

## 18.2. Télécharger un paquet Debian

Pour télécharger un paquet à partir des sources configurées sans l'installer :

```bash
apt-get download nom-du-paquet
```

Cette commande télécharge le paquet binaire demandé dans le répertoire courant.

Elle ne construit pas automatiquement un dépôt complet et ne garantit pas que tous les paquets nécessaires à une installation hors ligne ont été obtenus.

## 18.3. Télécharger les archives d'une transaction

APT peut être configuré pour télécharger les paquets d'une opération sans les installer immédiatement.

Exemple :

```bash
sudo apt-get --download-only upgrade
```

Cette commande demande le téléchargement nécessaire à l'opération selon l'état courant, les sources et le cache.

Il faut vérifier la documentation de la version installée et le résultat pour savoir précisément quelles archives ont été acquises.

## 18.4. Pourquoi la fermeture des dépendances est-elle importante ?

Télécharger uniquement le paquet principal n'est souvent pas suffisant pour une installation hors ligne.

Il faut obtenir l'ensemble des dépendances requises, dans des versions compatibles avec :

- la distribution cible ;
- son architecture ;
- les paquets déjà installés ;
- la suite logicielle ;
- les sources et règles de sélection.

Un ensemble de fichiers DEB sans les dépendances nécessaires peut échouer pendant l'installation.

## 18.5. Préparer un dépôt interne

Un dépôt interne peut servir à distribuer des versions contrôlées et à réduire la répétition des téléchargements.

Il doit gérer :

- la publication des métadonnées ;
- les versions des paquets ;
- l'intégrité et l'authenticité ;
- les architectures ;
- la cohérence des dépendances ;
- la rétention des versions ;
- la traçabilité des publications.

Des outils spécialisés tels qu'Aptly ou reprepro peuvent servir à gérer certains dépôts Debian, selon les exigences du projet.

La configuration doit être adaptée au modèle de distribution choisi et à la politique de sécurité.

## 18.6. Cache de paquets et dépôt ne sont pas la même chose

Un cache conserve des archives qui ont été téléchargées.

Un dépôt publie des paquets et des métadonnées selon un mécanisme que les gestionnaires peuvent interroger.

Un cache peut améliorer l'efficacité d'un réseau, mais ne constitue pas nécessairement un dépôt d'entreprise doté d'une politique de publication et de rétention.

## 18.7. Vérification en environnement isolé

Avant le transfert d'un paquet vers un réseau isolé :

1. vérifie son origine ;
2. contrôle son identité ;
3. confirme l'architecture ;
4. valide la version attendue ;
5. obtiens les dépendances nécessaires ;
6. vérifie les métadonnées de confiance selon la méthode prévue ;
7. conserve un inventaire et une trace du transfert.

La procédure doit éviter de transformer le réseau intermédiaire en source non contrôlée de paquets.


# 19. Construction de paquets Debian à partir des sources

## 19.1. Pourquoi construire un paquet ?

Il peut être nécessaire de construire un paquet lorsqu'un logiciel doit être adapté à une politique d'entreprise ou distribué de façon reproductible.

Exemples :

- application interne ;
- correctif spécifique ;
- intégration d'un service ;
- adaptation d'un fichier d'installation ;
- besoin d'un paquet versionné pour un dépôt interne.

Construire un paquet est différent d'installer directement un programme compilé à la main.

Le paquetage permet d'enregistrer les fichiers, les versions et les relations nécessaires à la gestion.

## 19.2. Code source et paquet binaire

Un paquet source Debian contient les éléments nécessaires à la construction et les métadonnées correspondantes.

Le processus de construction produit des paquets binaires qui pourront être installés avec les outils habituels.

```text
CODE SOURCE
    |
    v
MÉTADONNÉES DE CONSTRUCTION
    |
    v
OUTILS DE CONSTRUCTION
    |
    v
PAQUETS BINAIRES
    |
    v
TESTS ET CONTRÔLES
    |
    v
DÉPÔT DE DISTRIBUTION
    |
    v
INSTALLATION
```

La chaîne exacte dépend du format source, des outils et des règles de construction utilisés.

## 19.3. Lire les informations du paquet source

Pour les paquets disponibles via les sources APT :

```bash
apt-cache showsrc nom-du-paquet
```

Cette commande nécessite que les métadonnées de paquets source soient disponibles dans la configuration des sources.

Si les sources correspondantes ne sont pas configurées, l'information peut être indisponible.

## 19.4. Télécharger les sources

Sur un système configuré pour les paquets source :

```bash
apt-get source nom-du-paquet
```

Cette commande télécharge et dépaquette le paquet source dans le répertoire courant selon les capacités et la configuration disponibles.

Le code récupéré doit être traité comme du code à examiner avant son utilisation.

## 19.5. Dépendances de construction

Les paquets source peuvent déclarer des dépendances de construction.

Sur Debian, ces relations sont notamment décrites dans les métadonnées de construction du paquet.

L'outil suivant peut être utilisé lorsqu'il est disponible :

```bash
sudo apt-get build-dep nom-du-paquet
```

Cette commande demande l'installation des dépendances nécessaires à la construction selon les métadonnées source et l'état actuel du système.

Il faut examiner les changements proposés. Une machine de construction dédiée est préférable à un serveur de production.

## 19.6. Environnements de construction isolés

Construire directement sur le système principal peut installer de nombreux outils de développement et modifier la base logicielle.

Des environnements dédiés peuvent limiter cette pollution.

Des outils tels que `sbuild` ou `pbuilder` peuvent aider à construire les paquets dans un environnement contrôlé.

Le choix dépend de la distribution, du processus de construction et du niveau d'isolation requis.

## 19.7. Vérifier le paquet produit

Avant publication :

- vérifier les métadonnées ;
- vérifier les dépendances ;
- contrôler le contenu ;
- lancer les tests ;
- contrôler les permissions ;
- vérifier la version et l'architecture ;
- examiner les scripts de maintenance ;
- tester l'installation et la suppression ;
- documenter la provenance du code source.

Un paquet qui se construit sans erreur n'est pas nécessairement correct, sûr ou conforme à la politique de l'organisation.

## 19.8. Pourquoi ne pas compiler directement sur un serveur de production ?

La compilation peut installer des outils, des bibliothèques et des composants qui ne sont pas nécessaires à l'exécution.

Elle rend aussi les différences de construction plus difficiles à reproduire.

Il est préférable de produire un artefact versionné dans un environnement contrôlé, de le tester, puis de le distribuer selon une procédure documentée.


# 20. Dépôts internes et distribution d'entreprise

## 20.1. Pourquoi un dépôt interne ?

Un dépôt interne permet d'organiser les paquets approuvés et de contrôler leur publication.

Il peut servir à distribuer :

- des paquets d'applications internes ;
- des versions approuvées de logiciels tiers ;
- des correctifs validés ;
- des versions spécifiques à un parc ;
- des paquets construits par l'organisation.

## 20.2. Les fonctions requises

Un dépôt d'entreprise doit avoir des règles claires concernant :

- les personnes autorisées à publier ;
- les versions acceptées ;
- la provenance des artefacts ;
- la vérification des signatures ;
- la promotion entre environnements ;
- la rétention des anciennes versions ;
- la suppression ou le retrait d'un paquet ;
- la traçabilité ;
- les clés et certificats utilisés.

## 20.3. Promotion par environnement

Une politique courante consiste à séparer les étapes de validation :

```text
PAQUET CONSTRUIT
        |
        v
ENVIRONNEMENT DE TEST
        |
        v
VALIDATION TECHNIQUE
        |
        v
PRÉPRODUCTION
        |
        v
VALIDATION MÉTIER
        |
        v
DÉPÔT DE PRODUCTION
```

Une version ne doit pas être considérée comme approuvée uniquement parce qu'elle a été construite.

Les contrôles doivent couvrir les fonctionnalités, la sécurité et la compatibilité du paquet dans son environnement cible.

## 20.4. Éviter de remplacer silencieusement une version publiée

Remplacer le contenu d'un artefact en conservant le même identifiant de version détruit une partie de la traçabilité.

Les systèmes doivent pouvoir répondre à la question : quel artefact exact a été déployé sur cette machine ?

Il est préférable de conserver une identité de version et un mécanisme de publication qui garantissent la traçabilité des artefacts.

## 20.5. Gouvernance des dépôts

Une organisation doit définir :

- qui approuve un dépôt ;
- comment les clés sont gérées ;
- comment les versions sont testées ;
- comment les incidents de sécurité sont traités ;
- combien de temps les versions sont conservées ;
- comment une version est retirée ;
- comment les machines vérifient l'authenticité.

La gestion de paquets devient ainsi une activité de gouvernance logicielle, pas seulement une suite de commandes.


# 21. Gestion experte des paquets RPM avec DNF

Cette section concerne les distributions utilisant RPM et DNF. Les options peuvent varier selon les versions, notamment entre les générations de DNF.

## 21.1. Examiner les paquets installés

```bash
rpm -qa
```

Cette commande liste les paquets enregistrés dans la base RPM locale.

Pour un paquet particulier :

```bash
rpm -qi nom-du-paquet
```

Pour lister les fichiers enregistrés :

```bash
rpm -ql nom-du-paquet
```

## 21.2. Identifier la provenance et les dépôts

```bash
dnf info nom-du-paquet
```

Pour rechercher des informations sur les paquets disponibles :

```bash
dnf repoquery nom-du-paquet
```

Les possibilités de filtrage varient selon la version de DNF et les extensions installées.

Il faut examiner les dépôts configurés avant de supposer qu'une version publiée est issue d'une source officiellement maintenue.

## 21.3. Examiner les transactions

```bash
dnf history
```

Puis, pour une transaction particulière :

```bash
dnf history info ID
```

Remplace `ID` par l'identifiant réel retourné par l'historique.

L'historique peut aider à comprendre les changements précédents, mais il ne garantit pas qu'une annulation soit possible dans tous les contextes.

## 21.4. Annulation de transaction

Certaines versions de DNF prennent en charge des opérations d'annulation ou de retour d'historique.

Ces opérations peuvent échouer si les paquets nécessaires ne sont plus disponibles ou si l'état actuel a trop changé.

Une transaction d'annulation ne restaure pas automatiquement les données applicatives et fichiers de configuration qui auraient été modifiés par le logiciel.

La documentation de la version installée doit être consultée avant une opération de retour arrière.

## 21.5. Synchroniser les versions

```bash
sudo dnf distro-sync
```

Cette commande demande une synchronisation des paquets installés avec les versions disponibles dans les dépôts configurés.

Elle peut mettre à niveau ou rétrograder certains paquets selon la configuration et les versions disponibles.

Ne l'exécute pas aveuglément : examine les changements, particulièrement sur un serveur critique.

## 21.6. Vérifier des fichiers RPM

```bash
rpm -V nom-du-paquet
```

Cette commande peut détecter certaines différences entre les fichiers et les attributs enregistrés.

Le résultat doit être interprété, notamment lorsque des fichiers de configuration ont été modifiés intentionnellement.

## 21.7. Verrouillage de versions

Des mécanismes d'extension ou de préférence peuvent être utilisés pour contrôler les versions de paquets dans certains environnements DNF.

Leur disponibilité dépend de la version et des extensions installées.

Avant d'appliquer un verrou, il faut comprendre comment il influence les mises à jour et les dépendances.

Un verrou permanent sans procédure de révision peut conserver une version vulnérable ou bloquer une mise à niveau nécessaire.

Documentation : [DNF command reference](https://dnf.readthedocs.io/en/stable/command_ref.html).


# 22. Gestion experte des paquets Arch Linux avec Pacman

## 22.1. Les mises à niveau partielles

Arch Linux adopte un modèle de publication continue.

La cohérence entre les paquets et les bibliothèques publiés dans les dépôts est essentielle.

La commande courante est :

```bash
sudo pacman -Syu
```

Elle synchronise les bases des dépôts puis met à niveau les paquets selon le modèle normal de Pacman.

## 22.2. Pourquoi les mises à niveau partielles sont-elles dangereuses ?

Mettre à jour une bibliothèque sans mettre à jour les composants qui en dépendent peut créer des incompatibilités.

Arch Linux ne doit pas être administré comme un système dont tous les paquets peuvent être mis à niveau indépendamment sans tenir compte de l'ensemble.

Il faut suivre la documentation officielle et éviter les méthodes de mise à jour partielle qui ne sont pas prises en charge.

## 22.3. Vérifier le contenu d'un paquet

```bash
pacman -Ql nom-du-paquet
```

Pour les informations locales :

```bash
pacman -Qi nom-du-paquet
```

Pour examiner des fichiers appartenant à un paquet installé :

```bash
pacman -Qkk nom-du-paquet
```

Les résultats de vérification doivent être interprétés selon le paquet et la configuration.

## 22.4. Paquets étrangers et orphelins

Lister certains paquets étrangers aux dépôts synchronisés :

```bash
pacman -Qm
```

Identifier les dépendances devenues orphelines selon la base locale :

```bash
pacman -Qtd
```

Ces listes ne signifient pas que les paquets sont nécessairement inutiles ou dangereux.

Un paquet installé manuellement peut encore être nécessaire à un usage local. Toute suppression doit être précédée d'une vérification.

## 22.5. Paquets locaux

Pacman permet l'installation d'un paquet local avec `-U`.

Exemple générique :

```bash
sudo pacman -U fichier.pkg.tar.zst
```

Le fichier doit être un paquet valide et compatible avec la machine.

L'installation ne doit pas être utilisée pour contourner des incompatibilités de dépendances sans comprendre leur cause.

Documentation : [ArchWiki — Pacman](https://wiki.archlinux.org/title/Pacman).


# 23. Systèmes immuables et mises à jour atomiques

## 23.1. Tous les systèmes Linux ne gèrent pas les paquets de la même manière

Certaines éditions Linux utilisent des images ou des systèmes de fichiers conçus pour limiter les modifications directes de l'image système.

Dans ces environnements, le mécanisme de mise à jour peut être fondamentalement différent de l'installation classique de paquets sur une racine modifiable.

Il faut identifier le modèle avant de lancer les commandes du système traditionnel.

## 23.2. Mises à jour atomiques

Une stratégie atomique prépare une nouvelle version dans un emplacement distinct, puis fait basculer le système vers cette version lorsqu'elle est prête.

```text
VERSION ACTIVE
      |
      v
PRÉPARATION DE LA NOUVELLE VERSION
      |
      v
VÉRIFICATIONS
      |
      v
ACTIVATION DE LA NOUVELLE VERSION
      |
      v
CONTRÔLE APRÈS REDÉMARRAGE
      |
      +-- Succès : nouvelle version maintenue
      |
      +-- Échec : procédure de retour adaptée
```

Le fonctionnement exact dépend du système, de son gestionnaire de versions et de sa politique de retour arrière.

## 23.3. `systemd-sysupdate`

`systemd-sysupdate` est un outil permettant certaines stratégies de mise à jour atomique de systèmes ou de ressources lorsque les configurations requises sont présentes.

Sa disponibilité et son statut dépendent de la version de systemd et du système utilisé. Certaines versions documentent ce composant comme expérimental.

Il ne faut donc pas présumer qu'il remplace APT ou DNF sur toutes les distributions.

## 23.4. Avantages et limites

Les mises à jour atomiques peuvent améliorer le contrôle de l'activation d'une nouvelle image.

Cependant, elles ne dispensent pas :

- de vérifier la provenance ;
- de contrôler les données persistantes ;
- de tester l'application ;
- de vérifier les compatibilités ;
- de suivre les journaux ;
- de préparer une stratégie de restauration.

Le mécanisme de mise à jour doit être choisi selon l'architecture du système.

Documentation : [systemd-sysupdate](https://www.freedesktop.org/software/systemd/man/latest/systemd-sysupdate.html).


# 24. Sécurité de la chaîne d'approvisionnement logicielle

## 24.1. Un paquet représente plus qu'un fichier

Une chaîne d'approvisionnement logicielle comprend plusieurs étapes :

```text
CODE SOURCE
    |
    v
RÉVISION ET VALIDATION
    |
    v
ENVIRONNEMENT DE CONSTRUCTION
    |
    v
ARTEFACT BINAIRE
    |
    v
MÉTADONNÉES ET SIGNATURE
    |
    v
DÉPÔT
    |
    v
GESTIONNAIRE DE PAQUETS
    |
    v
SYSTÈME CIBLE
```

Une faiblesse peut apparaître à plusieurs endroits :

- source compromise ;
- dépendance vulnérable ;
- environnement de construction non contrôlé ;
- artefact remplacé ;
- clé de signature compromise ;
- dépôt mal configuré ;
- machine cible compromise.

## 24.2. Signature et provenance

Une signature permet de vérifier une relation d'authenticité selon la chaîne de confiance configurée.

Elle ne prouve pas que le code est sans vulnérabilité.

Il faut aussi établir la provenance de l'artefact : source utilisée, procédure de construction, identité de la version et approbation éventuelle.

## 24.3. Sommes de contrôle

Une somme de contrôle cryptographique peut confirmer qu'un fichier correspond à une valeur de référence.

Par exemple, avec SHA-256 :

```bash
sha256sum fichier.deb
```

La valeur obtenue doit être comparée à une valeur de référence obtenue par un canal de confiance.

Calculer une somme de contrôle sans référence fiable ne permet pas, à lui seul, de prouver l'authenticité du fichier.

## 24.4. Builds reproductibles

Un build reproductible vise à permettre la reproduction d'un artefact binaire à partir des mêmes sources et d'un environnement de construction contrôlé.

Cette propriété facilite la comparaison entre un artefact distribué et un artefact reconstruit.

Elle ne garantit pas, à elle seule, que les sources sont sûres. Elle constitue un élément parmi d'autres du processus de confiance.

La documentation du projet [Reproducible Builds](https://reproducible-builds.org/) explique les principes et les méthodes d'évaluation.

## 24.5. SBOM

Une SBOM, ou nomenclature logicielle, décrit les composants qui entrent dans un logiciel ou un artefact.

Elle peut aider à identifier les dépendances présentes et à évaluer l'impact d'une vulnérabilité sur les produits concernés.

Une SBOM doit être maintenue et reliée à l'artefact réel. Une liste ancienne ou associée à une autre version ne suffit pas.

## 24.6. Politique de publication

Une politique de sécurité des paquets doit établir :

- qui peut publier ;
- comment les versions sont identifiées ;
- quels tests sont obligatoires ;
- quelles signatures sont utilisées ;
- comment les vulnérabilités sont traitées ;
- comment les artefacts sont stockés ;
- comment les versions sont retirées ;
- comment les déploiements sont tracés.

Un système de paquets fiable dépend autant des outils que de la gouvernance qui les entoure.


# 25. Scripts avancés et automatisation contrôlée

## 25.1. Principes

Un script d'administration doit séparer la collecte des informations des modifications qui touchent le système.

Il doit aussi :

- valider les arguments ;
- gérer les erreurs ;
- vérifier la disponibilité des outils ;
- éviter les écrasements involontaires ;
- enregistrer les résultats ;
- renvoyer des codes de sortie significatifs ;
- ne pas contourner la sécurité des dépôts ;
- permettre un examen humain avant une transaction importante.

## 25.2. Script : audit d'un paquet installé

Créer `audit-paquet.sh` :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s nom-du-paquet\n' "$0" >&2
    exit 2
fi

PACKAGE=$1

for command_name in dpkg-query apt-cache; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        printf 'Erreur : commande indisponible : %s\n' "$command_name" >&2
        exit 2
    fi
done

printf '=== Paquet : %s ===\n' "$PACKAGE"

if ! dpkg-query -W "$PACKAGE" >/dev/null 2>&1; then
    printf 'Le paquet n’est pas connu dans la base locale.\n' >&2
    exit 1
fi

printf '\n%s\n' '=== État local ==='
dpkg-query -W \
    -f='Package: ${Package}\nVersion: ${Version}\nArchitecture: ${Architecture}\nStatus: ${db:Status-Status}\n' \
    "$PACKAGE"

printf '\n%s\n' '=== Versions et origine connues par APT ==='
apt-cache policy "$PACKAGE"

printf '\n%s\n' '=== Dépendances déclarées ==='
apt-cache depends "$PACKAGE"

printf '\n%s\n' '=== Fichiers enregistrés ==='
dpkg -L "$PACKAGE"
```

Rendre le script exécutable :

```bash
chmod +x audit-paquet.sh
```

Exemple :

```bash
./audit-paquet.sh curl
```

Ce script effectue des consultations. Il ne modifie pas les paquets.

Le fait que le paquet soit connu dans la base locale ne garantit pas qu'il soit entièrement configuré. Il faut lire le statut affiché.

## 25.3. Script : produire un inventaire daté

Créer `inventaire-paquets.sh` :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s fichier-sortie.tsv\n' "$0" >&2
    exit 2
fi

OUTPUT=$1

if [[ -e "$OUTPUT" ]]; then
    printf 'Erreur : le fichier existe déjà : %s\n' "$OUTPUT" >&2
    exit 1
fi

if ! command -v dpkg-query >/dev/null 2>&1; then
    printf 'Erreur : dpkg-query est indisponible.\n' >&2
    exit 2
fi

TMP="${OUTPUT}.tmp"

if [[ -e "$TMP" ]]; then
    printf 'Erreur : fichier temporaire déjà présent : %s\n' "$TMP" >&2
    exit 1
fi

if ! dpkg-query -W \
    -f='${Package}\t${Version}\t${Architecture}\t${db:Status-Status}\n' \
    > "$TMP"; then
    printf 'Erreur : impossible de produire l’inventaire.\n' >&2
    rm -f -- "$TMP"
    exit 1
fi

{
    printf '# Date : %s\n' "$(date '+%F %T')"
    printf '# Machine : %s\n' "$(hostname)"
    printf '# Distribution : '
    . /etc/os-release
    printf '%s %s\n' "${PRETTY_NAME:-inconnue}" "${VERSION_ID:-}"
    printf '# Package\tVersion\tArchitecture\tÉtat\n'
    cat "$TMP"
} > "$OUTPUT"

STATUS=$?
rm -f -- "$TMP"

if [[ "$STATUS" -ne 0 ]]; then
    printf 'Erreur pendant la création du rapport.\n' >&2
    exit 1
fi

printf 'Inventaire créé : %s\n' "$OUTPUT"
```

Rendre le script exécutable :

```bash
chmod +x inventaire-paquets.sh
```

Puis :

```bash
./inventaire-paquets.sh inventaire-serveur.tsv
```

Ce script est un exemple pédagogique. Dans un outil de production, il faudrait aussi prévoir la gestion des chemins relatifs, des permissions, du stockage des inventaires, des erreurs d'écriture et des données sensibles.

## 25.4. Script : simulation de mise à niveau

```bash
#!/usr/bin/env bash

set -u

if ! command -v apt-get >/dev/null 2>&1; then
    printf 'Erreur : apt-get est indisponible.\n' >&2
    exit 2
fi

printf 'Date : %s\n' "$(date '+%F %T')"
printf '%s\n' 'Simulation de mise à niveau : aucun paquet ne doit être modifié.'

apt-get -s upgrade
STATUS=$?

if [[ "$STATUS" -ne 0 ]]; then
    printf 'La simulation a échoué avec le code %s.\n' "$STATUS" >&2
    exit "$STATUS"
fi

printf '%s\n' 'Simulation terminée. Examiner le plan avant toute mise à niveau réelle.'
```

Le script n'effectue pas la mise à niveau. Il fournit une première vue du plan que l'administrateur doit examiner.

## 25.5. Pourquoi les scripts ne doivent-ils pas supprimer automatiquement les paquets ?

Les paquets de base, les bibliothèques et les composants partagés peuvent être nécessaires à des services critiques.

Une règle automatique fondée uniquement sur le nom, la taille ou la consommation supposée d'un paquet est insuffisante.

Les suppressions automatiques doivent s'appuyer sur une politique claire, des tests et une validation appropriée.


# 26. Méthodologie de dépannage expert

## 26.1. Incident : impossible de satisfaire les dépendances

### Collecte

```bash
apt-cache policy nom-du-paquet
```

```bash
apt-cache depends nom-du-paquet
```

```bash
apt-mark showhold
```

### Analyse

Vérifie les sources, les versions disponibles, les contraintes de version, les retenues et les états locaux.

### Action

Corrige la source ou la contrainte qui provoque l'impasse. Évite de forcer l'installation sans comprendre les conséquences.

## 26.2. Incident : paquet dépaqueté mais non configuré

### Collecte

```bash
dpkg --audit
```

```bash
dpkg -s nom-du-paquet
```

Consulte les journaux qui correspondent au moment de l'échec.

### Analyse

Identifie l'étape de configuration, le script concerné et les dépendances nécessaires.

### Action

Corrige la cause, puis utilise la procédure appropriée pour terminer la configuration.

## 26.3. Incident : dépôt non authentifié

### Collecte

Examine le dépôt, les clés associées et les messages d'APT.

### Analyse

Vérifie la provenance de la source et la procédure officielle de renouvellement ou de configuration de la clé.

### Action

Répare la chaîne de confiance. Ne désactive pas les vérifications pour obtenir une installation artificiellement réussie.

## 26.4. Incident : suppression inattendue proposée par APT

### Collecte

```bash
apt-get -s install nom-du-paquet
```

ou :

```bash
apt-get -s upgrade
```

### Analyse

Examiner les dépendances, les versions candidates, les priorités, les retenues et les dépôts.

### Action

Interrompre la transaction réelle jusqu'à ce que le plan soit compris.

## 26.5. Incident : échec après mise à jour

### Collecte

Consulte l'historique de paquetage, les journaux applicatifs et l'état des services.

### Analyse

Compare l'heure de la transaction à celle du premier symptôme.

### Action

Corrige la configuration ou le paquet concerné, ou effectue une restauration contrôlée si elle est justifiée.

Ne suppose pas que l'antériorité temporelle suffit à prouver la causalité.

## 26.6. Incident : espace disque insuffisant

### Collecte

```bash
df -h
```

Puis examine les répertoires pertinents et les fichiers ouverts si nécessaire.

### Analyse

Distingue les archives APT, les journaux, les données applicatives et les fichiers supprimés mais encore ouverts.

### Action

Libère uniquement l'espace identifié comme sûr à supprimer et documente les changements.

## 26.7. Incident : mises à jour automatiques non appliquées

### Collecte

Vérifie la configuration, les sources autorisées, les journaux et les éventuelles exclusions.

### Analyse

Détermine si le paquet appartient à une origine autorisée, si une retenue existe et si l'opération a échoué.

### Action

Corrige la configuration selon la politique de maintenance approuvée et valide le résultat.


# 27. Travaux pratiques guidés

Ces travaux pratiques doivent être effectués dans un environnement de laboratoire. Les opérations de réparation, de mise à niveau et de configuration sont à réaliser uniquement après examen du plan et compréhension des changements prévus.

## TP 1 — Analyser la provenance et la version d'un paquet

### Objectif

Comprendre pourquoi une version est candidate.

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

Consigne la version installée, la candidate et les origines indiquées.

### Étape 5

Explique pourquoi les deux versions peuvent être différentes.


## TP 2 — Simuler des transactions

### Objectif

Évaluer les changements avant modification.

### Étape 1

```bash
apt-get -s install htop
```

### Étape 2

```bash
apt-get -s remove htop
```

### Étape 3

```bash
apt-get -s upgrade
```

### Étape 4

Identifie les paquets ajoutés, mis à jour ou supprimés.

### Résultat attendu

Tu dois pouvoir expliquer les changements proposés sans prétendre que la transaction a été effectuée.


## TP 3 — Examiner la confiance des sources

### Objectif

Comprendre les fichiers qui déterminent les sources logicielles.

### Étape 1

```bash
find /etc/apt -maxdepth 2 -type f \
    \( -name '*.list' -o -name '*.sources' \) -print
```

### Étape 2

Examine les fichiers trouvés.

### Étape 3

Identifie les dépôts, les suites et les paramètres de confiance déclarés.

### Étape 4

Examine les résultats :

```bash
sudo apt update
```

### Résultat attendu

Tu dois pouvoir identifier une source et expliquer pourquoi sa provenance et sa politique de confiance doivent être connues.


## TP 4 — Examiner l'intégrité d'un paquet

### Objectif

Identifier les fichiers associés à un paquet.

### Étape 1

```bash
dpkg -L curl
```

### Étape 2

```bash
dpkg -S /usr/bin/curl
```

### Étape 3

Si la commande est disponible et si la situation le justifie :

```bash
dpkg --verify curl
```

### Étape 4

Interprète les résultats et les limites de la vérification.

### Résultat attendu

Tu dois pouvoir expliquer qu'un paquet enregistré dans la base locale et des fichiers réellement présents sont deux éléments qui doivent être cohérents.


## TP 5 — Exporter un inventaire reproductible

### Objectif

Conserver une trace des paquets installés.

### Étape 1

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' \
    > inventaire-laboratoire.tsv
```

### Étape 2

```bash
less inventaire-laboratoire.tsv
```

### Étape 3

```bash
apt-mark showmanual > paquets-manuels.txt
```

### Étape 4

Compare les deux fichiers conceptuellement.

### Résultat attendu

Tu dois comprendre qu'un inventaire des paquets, une liste de paquets manuels et une sauvegarde de configuration sont trois objets différents.


## TP 6 — Examiner une base `dpkg`

### Objectif

Savoir rechercher un état de paquet nécessitant une attention particulière.

### Étape 1

```bash
dpkg --audit
```

### Étape 2

```bash
dpkg -l | less
```

### Étape 3

Si un paquet est dans un état intermédiaire, examine son statut :

```bash
dpkg -s nom-du-paquet
```

### Étape 4

Consulte les journaux correspondant à l'opération.

### Résultat attendu

Tu dois savoir distinguer une anomalie réellement observée d'une simple commande qui ne renvoie aucune sortie.


## TP 7 — Analyser un paquet DEB

### Objectif

Inspecter un paquet avant installation.

### Étape 1

Prends un fichier DEB provenant d'une source fiable et destiné à ta distribution.

### Étape 2

```bash
dpkg-deb -I fichier.deb
```

### Étape 3

```bash
dpkg-deb -c fichier.deb
```

### Étape 4

Examine la version, l'architecture, les dépendances et les chemins.

### Étape 5

Ne procède à l'installation que si la provenance et les conséquences sont comprises.

### Résultat attendu

Tu dois pouvoir expliquer pourquoi le simple fait de posséder un fichier DEB ne suffit pas à en garantir la sécurité ou la compatibilité.


# 28. Exercices d'application

Réponds aux questions avant de consulter les corrections.

## Exercice 1 — Architecture

Explique la différence entre les index APT et la base locale `dpkg`.

Pourquoi peuvent-ils décrire des états différents ?

## Exercice 2 — Transaction

Cite les principales étapes d'une transaction d'installation, depuis la sélection du paquet jusqu'à la vérification du résultat.

## Exercice 3 — Scripts de maintenance

Pourquoi un paquet doit-il être traité comme du code potentiellement privilégié ?

Quel est le rôle des scripts de maintenance ?

## Exercice 4 — Dépendances

Explique la différence entre une dépendance directe et une dépendance transitive.

Pourquoi un conflit de dépendance peut-il exiger un changement sur plusieurs paquets ?

## Exercice 5 — Priorités APT

À quoi servent les préférences APT ?

Pourquoi une règle de pinning trop large peut-elle être dangereuse ?

## Exercice 6 — Provenance

Cite cinq contrôles à réaliser avant d'ajouter un dépôt tiers.

## Exercice 7 — Version précise

Quelle commande permet de demander une version précise d'un paquet ?

Pourquoi faut-il simuler la transaction avant de la confirmer ?

## Exercice 8 — Rétrogradation

Pourquoi la rétrogradation d'un paquet peut-elle être risquée même si l'ancienne version est disponible ?

## Exercice 9 — Réparation

Quelle commande examine des paquets nécessitant une attention particulière ?

Quelle commande demande la configuration des paquets dépaquetés mais non configurés ?

## Exercice 10 — Intégrité

Quelle est la différence entre la vérification des attributs des fichiers d'un paquet et une garantie complète de sécurité de l'installation ?

## Exercice 11 — Caches et dépôts

Quelle est la différence entre un cache de paquets et un dépôt interne ?

## Exercice 12 — Mises à jour automatiques

Pourquoi l'ajout d'un dépôt n'implique-t-il pas automatiquement son inclusion dans les mises à jour automatiques ?

## Exercice 13 — Construction

Pourquoi est-il généralement préférable de construire un paquet dans un environnement dédié plutôt que directement sur un serveur de production ?

## Exercice 14 — Inventaire

Pourquoi un inventaire de paquets ne suffit-il pas à reconstruire un environnement complet ?

## Exercice 15 — DNF

Quelle commande permet d'examiner l'historique des transactions DNF ?

Pourquoi une opération d'annulation ne garantit-elle pas la restauration de l'application ?

## Exercice 16 — Pacman

Pourquoi faut-il éviter les mises à niveau partielles non prises en charge sur Arch Linux ?

## Exercice 17 — Dépôt interne

Cite cinq responsabilités opérationnelles nécessaires à la gestion d'un dépôt d'entreprise.

## Exercice 18 — Mise à jour de production

Décris une procédure sécurisée de mise à jour pour un serveur important.


# 29. Corrections détaillées

## Correction 1 — Architecture

Les index APT décrivent les paquets et versions disponibles dans les sources configurées.

La base `dpkg` décrit l'état enregistré localement.

Ils peuvent différer parce qu'un paquet est installé sans être disponible dans les sources actuelles, ou parce qu'une nouvelle version est disponible mais n'a pas encore été installée.

## Correction 2 — Transaction

Les étapes comprennent généralement la sélection des versions, la résolution des dépendances, le téléchargement, les vérifications prévues, le dépaquetage, la configuration, les déclencheurs et la vérification de l'état final.

Les détails varient selon le paquet et le gestionnaire.

## Correction 3 — Scripts de maintenance

Les scripts peuvent être exécutés pendant l'installation, la mise à jour ou la suppression avec des privilèges élevés.

Ils peuvent modifier le système, configurer des composants ou exécuter des opérations de maintenance. La provenance et la confiance accordée au paquet sont donc essentielles.

## Correction 4 — Dépendances

Une dépendance directe est déclarée par le paquet lui-même.

Une dépendance transitive est requise indirectement par un autre composant dont dépend le paquet.

Un conflit peut exiger la mise à niveau ou la suppression d'autres paquets afin de satisfaire l'ensemble des contraintes.

## Correction 5 — Priorités APT

Les préférences influencent la sélection des versions et des origines.

Une règle trop large peut faire sélectionner des versions inattendues pour de nombreux paquets, créer des conflits ou compliquer les mises à niveau.

## Correction 6 — Provenance

Les contrôles peuvent inclure :

1. identifier le propriétaire du dépôt ;
2. vérifier la compatibilité avec la distribution ;
3. examiner les versions et dépendances publiées ;
4. valider la clé et la méthode de signature ;
5. lire la politique de maintenance ;
6. comprendre la portée des paquets publiés ;
7. simuler les transactions pertinentes.

## Correction 7 — Version précise

La commande est :

```bash
sudo apt install nom-du-paquet=VERSION
```

La simulation permet d'examiner les dépendances et les éventuelles suppressions avant de modifier le système.

## Correction 8 — Rétrogradation

L'ancienne version peut exiger des dépendances différentes ou être incompatible avec des données modifiées par la version récente.

Revenir au binaire précédent ne restaure donc pas nécessairement les configurations et données antérieures.

## Correction 9 — Réparation

Pour examiner les états anormaux :

```bash
dpkg --audit
```

Pour configurer les paquets dépaquetés mais non configurés :

```bash
sudo dpkg --configure -a
```

Il faut d'abord comprendre l'erreur si l'opération précédente a échoué.

## Correction 10 — Intégrité

La vérification des fichiers peut détecter certaines différences, selon les métadonnées disponibles.

Elle ne prouve pas que tous les aspects du logiciel, de sa configuration et de ses dépendances sont sûrs.

## Correction 11 — Caches et dépôts

Un cache conserve des archives téléchargées.

Un dépôt publie des paquets et des métadonnées selon un mécanisme destiné à être interrogé par les gestionnaires.

Le cache n'est donc pas automatiquement un dépôt complet doté d'une politique de publication.

## Correction 12 — Mises à jour automatiques

Le mécanisme automatique applique les origines et catégories autorisées par sa configuration. L'ajout d'une source doit être suivi d'un contrôle de cette configuration.

## Correction 13 — Construction

Un environnement dédié limite les modifications de la machine de production, améliore la reproductibilité et permet de tester les dépendances sans polluer le système cible.

## Correction 14 — Inventaire

Un inventaire de paquets ne contient pas nécessairement les sources, configurations, données applicatives, secrets, services et dépendances externes.

Il n'est donc qu'un élément d'une stratégie de reconstruction.

## Correction 15 — DNF

La commande est :

```bash
dnf history
```

Une annulation peut être impossible si les versions nécessaires ne sont plus disponibles ou si l'état a évolué. Elle ne restaure pas automatiquement les données ou configurations de l'application.

## Correction 16 — Pacman

Les paquets sont maintenus dans un ensemble cohérent. Une mise à niveau partielle peut introduire des incompatibilités entre bibliothèques et composants.

## Correction 17 — Dépôt interne

Les responsabilités peuvent comprendre :

1. contrôle des publications ;
2. validation des paquets ;
3. gestion des clés et signatures ;
4. traçabilité des versions ;
5. conservation des versions anciennes ;
6. traitement des vulnérabilités ;
7. gestion des retraits ;
8. contrôle des accès.

## Correction 18 — Mise à jour de production

Une procédure correcte comprend notamment :

1. identifier les serveurs et leurs rôles ;
2. vérifier les sources et la version de distribution ;
3. examiner les paquets concernés ;
4. simuler les transactions ;
5. évaluer les dépendances et les risques ;
6. vérifier les sauvegardes ;
7. planifier la maintenance ;
8. déployer d'abord sur un environnement de validation ;
9. appliquer la mise à jour ;
10. vérifier les services et les tests fonctionnels ;
11. documenter les versions et le résultat ;
12. prévoir une restauration adaptée si nécessaire.


# 30. Défi final : gouvernance des paquets d'un parc Linux

## 30.1. Contexte

Une organisation possède plusieurs serveurs Linux répartis entre différentes fonctions.

Elle souhaite standardiser les mises à jour et éviter que les machines divergent sans raison documentée.

La situation initiale révèle :

```text
OBSERVATION A
Plusieurs versions de bibliothèques sont présentes.

OBSERVATION B
Certaines machines disposent de dépôts tiers.

OBSERVATION C
Quelques paquets sont retenus.

OBSERVATION D
Un serveur a échoué pendant une installation.

OBSERVATION E
L'équipe souhaite automatiser l'inventaire.

OBSERVATION F
Une version doit être validée avant son déploiement général.
```

Les causes et les versions exactes ne sont pas encore connues.

## 30.2. Mission

Conçois une procédure permettant de :

1. identifier les systèmes et leurs rôles ;
2. inventorier les paquets et les versions ;
3. comparer les dépôts et les priorités ;
4. identifier les paquets retenus ;
5. diagnostiquer la machine dont l'installation a échoué ;
6. définir une version cible ;
7. vérifier la provenance des paquets ;
8. simuler les changements ;
9. déployer progressivement ;
10. vérifier les services après intervention ;
11. conserver un compte rendu reproductible ;
12. définir les conditions de retour arrière.

## 30.3. Contraintes

- Ne force pas l'installation d'une version pour uniformiser les machines.
- Ne supprime pas toutes les retenues sans examiner leur justification.
- Ne désactive pas les contrôles de signature.
- Ne répare pas la base locale sans examiner l'erreur initiale.
- Ne déploie pas simultanément une version non validée sur tout le parc.
- Ne confonds pas l'inventaire de paquets et la sauvegarde complète.
- Les scripts doivent collecter des données et renvoyer des codes d'état explicites.
- Toute modification doit être vérifiée après exécution.


# 31. Correction détaillée du défi final

## 31.1. Étape 1 — Définir l'état cible

Pour chaque rôle de serveur, définis :

- la distribution et sa version ;
- l'architecture ;
- les sources autorisées ;
- les versions de paquets nécessaires ;
- les services requis ;
- les exceptions documentées ;
- les contraintes de maintenance.

Un seul inventaire global ne suffit pas pour décrire toutes les machines : les rôles diffèrent.

## 31.2. Étape 2 — Collecter les paquets installés

Sur Debian ou Ubuntu :

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\t${db:Status-Status}\n'
```

Enregistre la sortie et la date de collecte.

Pour les paquets manuels :

```bash
apt-mark showmanual
```

Compare les états avec l'état cible, en tenant compte des rôles des machines.

## 31.3. Étape 3 — Examiner les sources et priorités

Inventorie les fichiers de sources :

```bash
find /etc/apt -maxdepth 2 -type f \
    \( -name '*.list' -o -name '*.sources' \) -print
```

Examine également les fichiers de préférences.

Pour les paquets divergents :

```bash
apt-cache policy nom-du-paquet
```

Vérifie si la différence provient d'une source, d'une priorité, d'une retenue ou d'une version installée qui n'est plus disponible.

## 31.4. Étape 4 — Examiner les retenues

```bash
apt-mark showhold
```

Pour chaque retenue, consigne :

- le paquet ;
- la version ;
- la raison de la retenue ;
- le responsable ;
- la condition de révision ;
- le risque de sécurité éventuel.

Une retenue inconnue doit faire l'objet d'une investigation, pas d'une suppression automatique.

## 31.5. Étape 5 — Diagnostiquer l'installation échouée

```bash
dpkg --audit
```

Puis examine le paquet :

```bash
dpkg -s nom-du-paquet
```

Consulte les journaux de la période :

```bash
sudo tail -n 100 /var/log/dpkg.log
```

```bash
sudo tail -n 100 /var/log/apt/term.log
```

La cause peut être une dépendance manquante, un script de maintenance en échec, un problème de disque ou une source incompatible.

La correction doit être choisie après avoir identifié le mécanisme de l'échec.

## 31.6. Étape 6 — Définir la version cible

Vérifie les versions connues :

```bash
apt-cache policy nom-du-paquet
```

Examine les dépendances :

```bash
apt-cache depends nom-du-paquet
```

Définis ensuite la version cible en fonction de la distribution, de la compatibilité et des avis de sécurité.

Ne cherche pas à obtenir le même numéro de version sur tous les systèmes si les distributions ou leurs politiques de maintenance diffèrent.

## 31.7. Étape 7 — Simuler la transaction

```bash
apt-get -s install nom-du-paquet=VERSION
```

Si une mise à niveau de plusieurs composants est nécessaire :

```bash
apt-get -s upgrade
```

Examine les paquets à installer, à mettre à niveau et à supprimer.

Toute suppression inattendue doit être comprise avant confirmation.

## 31.8. Étape 8 — Déployer progressivement

Une séquence possible est :

```text
LABORATOIRE
     |
     v
PRÉPRODUCTION
     |
     v
SERVEUR PILOTE
     |
     v
GROUPE INITIAL
     |
     v
VÉRIFICATION
     |
     v
DÉPLOIEMENT ÉTENDU
```

Définis à l'avance les indicateurs permettant de poursuivre ou d'interrompre le déploiement.

## 31.9. Étape 9 — Vérifier les services

Après une mise à jour :

```bash
systemctl --failed
```

Puis, pour chaque service important :

```bash
systemctl status nom.service
```

Et si nécessaire :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Effectue également un test fonctionnel correspondant au service.

## 31.10. Étape 10 — Préparer la restauration

Le retour arrière doit prendre en compte :

- les versions précédentes des paquets ;
- leur disponibilité ;
- les dépendances ;
- les fichiers de configuration ;
- les données applicatives ;
- les migrations éventuelles ;
- les services dépendants.

Une sauvegarde testée ou un mécanisme de déploiement précédent peut être plus fiable qu'une rétrogradation improvisée.

## 31.11. Étape 11 — Documenter le résultat

```text
RAPPORT DE GOUVERNANCE DES PAQUETS

1. Environnement
   Serveur :
   Fonction :
   Distribution :
   Version :
   Architecture :

2. État initial
   Paquets :
   Versions :
   Sources :
   Préférences :
   Retenues :

3. Incident éventuel
   Paquet :
   Erreur :
   Journaux :
   Cause confirmée :

4. Version cible
   Version :
   Provenance :
   Dépendances :
   Justification :

5. Simulation
   Changements prévus :
   Risques :
   Validation :

6. Intervention
   Date :
   Opération :
   Résultat :

7. Vérification
   État des paquets :
   État des services :
   Tests :
   Anomalies résiduelles :

8. Retour arrière
   Méthode :
   Sauvegarde :
   Conditions de déclenchement :

9. Conclusion
   Décision :
   Actions restantes :
   Responsable :
```

Ce rapport permet de reconstituer l'historique et de comprendre les exceptions.


# 32. Checklist de compétences expertes

## Architecture

- [ ] Je comprends la relation entre dépôts, index, APT, dpkg et base locale.
- [ ] Je peux expliquer le cycle de vie d'une transaction.
- [ ] Je comprends le rôle des scripts de maintenance et des déclencheurs.
- [ ] Je sais reconnaître les états intermédiaires d'un paquet.

## Résolution et sélection

- [ ] Je sais analyser une version candidate.
- [ ] Je comprends les dépendances transitives et les conflits.
- [ ] Je sais examiner les préférences APT.
- [ ] Je comprends les risques du pinning.
- [ ] Je sais simuler des opérations complexes.
- [ ] Je sais contrôler les retenues.

## Sécurité

- [ ] Je comprends la chaîne de confiance des dépôts.
- [ ] Je sais pourquoi une signature n'est pas une garantie d'absence de vulnérabilité.
- [ ] Je sais vérifier la provenance d'un paquet local.
- [ ] Je comprends les limites des vérifications de fichiers.
- [ ] Je sais limiter la portée des clés et sources.
- [ ] Je comprends les principes de reproductibilité et de traçabilité.

## Maintenance

- [ ] Je sais diagnostiquer une base dpkg incohérente.
- [ ] Je sais retrouver les journaux pertinents.
- [ ] Je sais identifier un conflit de versions.
- [ ] Je sais préparer une rétrogradation ou une restauration.
- [ ] Je sais inventorier les paquets et les sources.
- [ ] Je sais déployer progressivement une mise à jour.
- [ ] Je peux vérifier les services après modification.

## Automatisation et gouvernance

- [ ] Je sais concevoir un script de collecte non destructif.
- [ ] Je gère explicitement les erreurs et codes de retour.
- [ ] Je distingue simulation et exécution réelle.
- [ ] Je comprends le rôle d'un dépôt interne.
- [ ] Je sais documenter les exceptions et les retenues.
- [ ] Je sais préparer un rapport reproductible.


# 33. Fiche de référence des commandes

## Versions et dépendances

```bash
apt-cache policy nom-du-paquet
```

```bash
apt-cache madison nom-du-paquet
```

```bash
apt-cache depends nom-du-paquet
```

```bash
apt-cache rdepends nom-du-paquet
```

```bash
dpkg --compare-versions VERSION_A gt VERSION_B
```

## Transactions simulées

```bash
apt-get -s install nom-du-paquet
```

```bash
apt-get -s remove nom-du-paquet
```

```bash
apt-get -s upgrade
```

```bash
apt-get -s dist-upgrade
```

## États et préférences

```bash
dpkg --audit
```

```bash
apt-mark showhold
```

```bash
apt-mark showmanual
```

```bash
apt-mark showauto
```

## Intégrité et inspection

```bash
dpkg -L nom-du-paquet
```

```bash
dpkg -S /chemin/du/fichier
```

```bash
dpkg --verify nom-du-paquet
```

```bash
dpkg-deb -I fichier.deb
```

```bash
dpkg-deb -c fichier.deb
```

## Maintenance

```bash
sudo dpkg --configure -a
```

```bash
sudo apt --fix-broken install
```

```bash
sudo apt install --reinstall nom-du-paquet
```

Ces commandes ne remplacent pas l'identification de la cause. Examine le plan et les erreurs avant de confirmer toute modification.

## Inventaire

```bash
dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n'
```

```bash
apt-mark showmanual
```

## Journaux

```bash
sudo less /var/log/apt/history.log
```

```bash
sudo less /var/log/dpkg.log
```

## DNF/RPM

```bash
dnf history
```

```bash
dnf history info ID
```

```bash
rpm -qi nom-du-paquet
```

```bash
rpm -V nom-du-paquet
```

```bash
sudo dnf distro-sync
```

## Pacman

```bash
sudo pacman -Syu
```

```bash
pacman -Qkk nom-du-paquet
```

```bash
pacman -Qm
```

```bash
pacman -Qtd
```


# 34. Glossaire technique

**APT :** outil de gestion de paquets de haut niveau utilisé notamment par Debian et Ubuntu.

**Base locale :** informations enregistrées par le gestionnaire sur les paquets connus du système.

**Build reproductible :** construction visant à produire un artefact identique à partir de sources et d'un environnement contrôlés.

**Chaîne de confiance :** ensemble des mécanismes et autorités permettant de vérifier l'authenticité des données et des sources.

**Dépôt interne :** dépôt de paquets géré par une organisation pour distribuer des versions contrôlées.

**Dépendance transitive :** relation de dépendance introduite indirectement par un autre paquet.

**`dpkg` :** outil de bas niveau du système de paquetage Debian.

**Déclencheur :** mécanisme Debian permettant de coordonner ou différer certaines opérations de maintenance entre paquets.

**Diversion :** mécanisme de gestion de certains remplacements de chemins dans le système de paquetage Debian.

**Pinning :** mécanisme de préférences influençant la sélection des versions et origines par APT.

**Paquet source :** ensemble d'éléments et de métadonnées utilisés pour construire un paquet binaire.

**Paquet binaire :** paquet contenant les fichiers destinés à l'installation.

**Préférence APT :** règle qui influence la sélection des versions.

**Rétrogradation :** remplacement d'une version par une version antérieure.

**SBOM :** nomenclature qui décrit les composants logiciels inclus dans un artefact.

**Signature :** mécanisme cryptographique permettant de vérifier l'authenticité de données selon une chaîne de confiance.

**Transaction :** ensemble d'opérations effectuées par le gestionnaire de paquets.

**Version candidate :** version qu'APT sélectionne selon les versions disponibles, les priorités et les contraintes connues.

**Version installée :** version enregistrée dans la base locale pour un paquet installé.


# 35. Documentation officielle

## Debian et Ubuntu

1. Gestion des paquets sur Ubuntu Server  
   https://ubuntu.com/server/docs/how-to/software/package-management/

2. Mises à jour automatiques sur Ubuntu Server  
   https://ubuntu.com/server/docs/how-to/software/automatic-updates/

3. Manuel Debian — préférences APT  
   https://manpages.debian.org/bookworm/apt/apt_preferences.5.en.html

4. Manuel Debian — sécurité des sources APT  
   https://manpages.debian.org/bookworm/apt/apt-secure.8.en.html

5. Manuel Debian — interrogation de `dpkg`  
   https://manpages.debian.org/bookworm/dpkg/dpkg-query.1.en.html

6. Manuel Debian — outil `dpkg-deb`  
   https://manpages.debian.org/bookworm/dpkg/dpkg-deb.1.en.html

## RPM et DNF

7. Référence officielle DNF  
   https://dnf.readthedocs.io/en/stable/command_ref.html

8. Documentation RPM  
   https://rpm.org/docs/

## Arch Linux

9. ArchWiki — Pacman  
   https://wiki.archlinux.org/title/Pacman

10. ArchWiki — maintenance système et mises à niveau partielles  
    https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported

## Reproductibilité et mises à jour atomiques

11. Projet Reproducible Builds  
    https://reproducible-builds.org/

12. Documentation systemd-sysupdate  
    https://www.freedesktop.org/software/systemd/man/latest/systemd-sysupdate.html

Les commandes et comportements peuvent différer selon la distribution et la version des outils. Sur un système réel, consulte la documentation correspondant à la version installée, puis teste toute opération de maintenance importante dans un environnement maîtrisé.


# Conclusion générale

La gestion experte des paquets Linux consiste à maîtriser la cohérence des versions, les dépendances, la provenance des logiciels, les transactions, les mécanismes de maintenance et les risques liés aux mises à jour.

Tu dois être capable d'expliquer pourquoi une version est sélectionnée, de diagnostiquer une installation incohérente, de vérifier les fichiers gérés, de comprendre les limites des mécanismes de sécurité et de préparer des déploiements reproductibles.

La compétence ne se limite pas à connaître les commandes APT, DNF ou Pacman. Elle suppose également de savoir construire une politique de maintenance, contrôler les dépôts, préparer la restauration et vérifier les services après chaque opération importante.

La démarche de référence reste :

```text
DÉFINIR L'ÉTAT CIBLE
          |
          v
EXAMINER LES SOURCES ET VERSIONS
          |
          v
COMPRENDRE LES DÉPENDANCES
          |
          v
ÉVALUER LA CONFIANCE ET LES RISQUES
          |
          v
SIMULER ET VALIDER LA TRANSACTION
          |
          v
DÉPLOYER DE MANIÈRE CONTRÔLÉE
          |
          v
VÉRIFIER LES PAQUETS ET LES SERVICES
          |
          v
DOCUMENTER ET PRÉPARER LA RESTAURATION
```

**Un administrateur expert ne cherche pas seulement à obtenir une transaction réussie. Il doit pouvoir démontrer que la provenance des paquets est maîtrisée, que l'état obtenu est cohérent, que les risques ont été évalués et que la maintenance peut être reproduite ou corrigée.**