# GPO et gestion de parc Windows
## Cours intermédiaire — Administration centralisée, standardisation, sécurité et automatisation

## 1. Présentation du cours

### 1.1 Objectifs pédagogiques

Au niveau débutant, tu as appris à installer Windows Server, à créer un domaine Active Directory, à intégrer un poste Windows au domaine, à créer des utilisateurs et des groupes, et à découvrir les stratégies de groupe.

Ce cours prolonge ces connaissances. L'objectif n'est plus de configurer seulement un serveur et un poste : il s'agit désormais de **concevoir, déployer, contrôler et maintenir une configuration cohérente sur un parc complet d'ordinateurs Windows**.

À l'issue de ce cours, tu devras être capable de :

- Concevoir une arborescence d'unités d'organisation adaptée à un parc informatique.
- Comprendre et maîtriser l'héritage des GPO, leur ordre de traitement et la résolution des conflits.
- Cibler précisément des utilisateurs, des ordinateurs et des groupes de sécurité.
- Utiliser les stratégies de groupe classiques et les préférences de stratégie de groupe.
- Déployer des paramètres de sécurité cohérents sur des postes de travail.
- Organiser le déploiement des mises à jour Windows.
- Distribuer certains logiciels avec les outils natifs de Windows.
- Administrer des ordinateurs à distance avec PowerShell.
- Inventorier les machines et repérer les équipements obsolètes.
- Sauvegarder, documenter, tester et restaurer des GPO.
- Diagnostiquer les problèmes d'application des stratégies.
- Automatiser des tâches de gestion de parc avec PowerShell.
- Préparer un environnement professionnel dans lequel chaque modification est testée, traçable et réversible.

### 1.2 Prérequis

Tu dois déjà comprendre les notions suivantes :

- Domaine Active Directory.
- Contrôleur de domaine.
- Utilisateur, ordinateur, groupe de sécurité et unité d'organisation.
- DNS et résolution de noms.
- Adresse IP, passerelle, sous-réseau et connectivité réseau.
- Différence entre un compte utilisateur et un compte ordinateur.
- Administration élémentaire avec PowerShell.
- Notions de droits NTFS et de permissions de partage.

Le laboratoire utilise le domaine `ad.lab.test` et le contrôleur de domaine `DC1`, comme dans le cours débutant.

### 1.3 Environnement pédagogique

Nous utiliserons cette infrastructure fictive :

| Élément | Valeur |
|---|---|
| Domaine Active Directory | `ad.lab.test` |
| Contrôleur de domaine | `DC1.ad.lab.test` |
| Adresse IP de DC1 | `192.168.10.10` |
| Poste utilisateur principal | `PC1.ad.lab.test` |
| Adresse IP de PC1 | `192.168.10.20` |
| Poste pilote supplémentaire | `PC2.ad.lab.test` |
| Groupe des postes pilotes | `GG_Postes_Pilotes` |
| Groupe des utilisateurs de comptabilité | `GG_Comptabilite` |
| Groupe des administrateurs du parc | `GG_Admin_Parc` |

Ces valeurs sont des exemples de laboratoire. Il faudra les adapter à ton infrastructure réelle.

Dans les commandes PowerShell, nous utiliserons le nom DNS complet du domaine et les noms distinctifs Active Directory lorsque cela sera nécessaire.

### 1.4 Règles de travail

Dans un environnement professionnel, une stratégie de groupe peut toucher plusieurs centaines ou plusieurs milliers de postes. Une erreur de configuration peut empêcher l'ouverture de session, bloquer une application ou rendre une machine difficile à administrer.

Nous appliquerons donc les règles suivantes :

1. Concevoir avant de déployer.
2. Tester sur un nombre limité de machines.
3. Sauvegarder les GPO avant une modification importante.
4. Utiliser des groupes de sécurité pour contrôler le périmètre.
5. Documenter les changements.
6. Mesurer le résultat sur les postes pilotes.
7. Généraliser uniquement après validation.
8. Prévoir une procédure de retour arrière.

## 2. Architecture d'une gestion centralisée du parc

### 2.1 Qu'est-ce que la gestion de parc Windows ?

La gestion de parc consiste à administrer de manière cohérente tous les équipements Windows d'une organisation.

Cela comprend notamment :

- Les postes fixes.
- Les ordinateurs portables.
- Les postes partagés.
- Les postes de laboratoire.
- Les serveurs membres.
- Les comptes utilisateurs.
- Les logiciels installés.
- Les mises à jour.
- Les paramètres de sécurité.
- Les ressources réseau.
- Les incidents et les changements.

L'objectif est de réduire les interventions manuelles et de limiter les différences de configuration entre les machines.

Imaginons une entreprise disposant de 150 postes Windows.

Sans administration centralisée, un technicien doit intervenir individuellement pour vérifier les paramètres du pare-feu, configurer les lecteurs réseau, contrôler certains paramètres de sécurité et corriger les configurations non conformes.

Avec une architecture bien conçue, les paramètres communs peuvent être administrés depuis Active Directory et appliqués automatiquement aux équipements concernés.

### 2.2 Rôle d'Active Directory

Active Directory fournit l'annuaire qui permet d'organiser les identités et les ordinateurs du domaine.

Il ne représente toutefois pas, à lui seul, une solution complète d'inventaire matériel, de distribution de logiciels ou de supervision.

Sa fonction principale est ici de fournir une structure permettant de cibler les stratégies.

```text
                    INFRASTRUCTURE WINDOWS
                              |
                 +------------+------------+
                 |                         |
          Active Directory          Outils de gestion
                 |                         |
        +--------+--------+       +--------+--------+
        |                 |       |                 |
   Utilisateurs       Ordinateurs  PowerShell    Outils de
        |                 |       |              supervision
   Groupes et OU       OU/GPO      |                 |
        |                 |       |                 |
        +--------+--------+       +--------+--------+
                 |                         |
                 +------------+------------+
                              |
                       Parc Windows
                              |
              +---------------+---------------+
              |               |               |
             PC1             PC2             PC3
```

Active Directory aide à déterminer **quels utilisateurs et quels ordinateurs sont concernés par une politique**. PowerShell complète cette approche en permettant d'interroger les machines, de produire des rapports et d'automatiser de nombreuses opérations.

### 2.3 Comprendre les composants d'une GPO

Une stratégie de groupe, ou *Group Policy Object*, est constituée de paramètres qui peuvent être appliqués à des utilisateurs ou à des ordinateurs.

Une GPO contient deux grandes parties :

```text
GPO : GPO-Securite-Postes
|
+-- Configuration ordinateur
|   |
|   +-- Stratégies
|   |   +-- Paramètres Windows
|   |   +-- Modèles d'administration
|   |   +-- Paramètres de sécurité
|   |
|   +-- Préférences
|       +-- Paramètres du Registre
|       +-- Fichiers et dossiers
|       +-- Tâches planifiées
|
+-- Configuration utilisateur
    |
    +-- Stratégies
    |   +-- Paramètres Windows
    |   +-- Modèles d'administration
    |
    +-- Préférences
        +-- Mappages de lecteurs
        +-- Raccourcis
        +-- Paramètres du Registre
```

Les catégories exactes disponibles dépendent des extensions et des modèles administratifs installés.

### 2.4 Configuration ordinateur ou configuration utilisateur ?

Cette distinction est fondamentale.

**Configuration ordinateur**

Les paramètres s'appliquent à l'ordinateur lui-même, indépendamment de l'utilisateur connecté.

Exemples :

- Configurer le pare-feu Windows.
- Définir certaines options de sécurité.
- Gérer des paramètres de Windows Update.
- Déployer un logiciel pour tous les utilisateurs d'une machine.
- Configurer des paramètres liés au système.

**Configuration utilisateur**

Les paramètres s'appliquent au compte utilisateur.

Exemples :

- Mapper un lecteur réseau personnel.
- Ajouter un raccourci.
- Configurer certaines options de l'interface.
- Gérer des paramètres utilisateur des applications.
- Définir certaines restrictions de l'environnement de travail.

Schéma conceptuel :

```text
PC1 appartient à : OU=Postes
|
+-- Configuration ordinateur
|      |
|      +-- Pare-feu
|      +-- Mises à jour
|      +-- Paramètres système
|
Utilisateur adiallo appartient à : OU=Utilisateurs
       |
       +-- Configuration utilisateur
              |
              +-- Lecteur réseau personnel
              +-- Raccourcis
              +-- Paramètres utilisateur
```

Une erreur courante consiste à placer un compte utilisateur dans une OU en pensant que les stratégies ordinateur de cette OU s'appliqueront à la machine qu'il utilise.

Ce n'est pas le fonctionnement normal. Les GPO liées à une OU sont évaluées selon l'emplacement de l'objet concerné : l'objet ordinateur pour les paramètres ordinateur, l'objet utilisateur pour les paramètres utilisateur, sauf mécanismes particuliers comme le traitement en boucle décrit plus loin.

## 3. Concevoir une arborescence Active Directory adaptée au parc

### 3.1 Pourquoi l'organisation des OU est-elle importante ?

L'unité d'organisation permet de regrouper des objets Active Directory et de leur appliquer des stratégies.

Une mauvaise organisation peut créer :

- Des GPO répétées.
- Des exceptions difficiles à comprendre.
- Des paramètres contradictoires.
- Des problèmes de ciblage.
- Une administration complexe.
- Des erreurs lors des déplacements d'ordinateurs.

L'objectif n'est pas de créer le maximum d'OU, mais de créer une structure qui traduit les différences réelles de gestion.

### 3.2 Exemple d'une architecture d'OU

Voici une architecture adaptée à une entreprise de taille moyenne :

```text
ad.lab.test
|
+-- OU=Utilisateurs
|   |
|   +-- OU=Administration
|   +-- OU=Comptabilite
|   +-- OU=Direction
|   +-- OU=Support
|   +-- OU=Commercial
|
+-- OU=Ordinateurs
|   |
|   +-- OU=Postes
|   |   |
|   |   +-- OU=Pilotes
|   |   +-- OU=Standard
|   |   +-- OU=Kiosques
|   |   +-- OU=Portables
|   |
|   +-- OU=Serveurs-Membres
|   |
|   +-- OU=Quarantaine
|
+-- OU=Groupes
    |
    +-- GG_Postes_Pilotes
    +-- GG_Comptabilite
    +-- GG_Admin_Parc
```

Les noms des OU doivent être cohérents et compréhensibles. Dans un véritable environnement, il faudra également prévoir les comptes de service et les objets d'administration selon les besoins de l'organisation.

### 3.3 Séparer les utilisateurs des ordinateurs

Séparer les OU des utilisateurs et celles des ordinateurs présente plusieurs avantages.

Premièrement, une stratégie ordinateur peut être liée à l'OU des postes sans dépendre du service auquel appartient l'utilisateur.

Deuxièmement, les paramètres utilisateur peuvent suivre le compte lorsqu'il change de poste.

Troisièmement, il devient possible de distinguer les politiques d'un poste partagé, d'un portable et d'un serveur.

Exemple :

```text
L'utilisateur adiallo
       |
       +-- Se connecte à PC1
       |
       +-- Se connecte à PC2
       |
       +-- Se connecte à un poste de remplacement

Ses paramètres utilisateur peuvent suivre son compte.

Les paramètres ordinateur varient selon l'OU
et les GPO de chaque équipement.
```

### 3.4 Ne pas organiser toutes les OU uniquement par service

Une entreprise peut être organisée par départements, mais cela ne signifie pas que chaque GPO doit être dupliquée pour chaque département.

Exemple peu efficace :

```text
OU=Comptabilite
   +-- GPO-PareFeu-Comptabilite
   +-- GPO-WindowsUpdate-Comptabilite
   +-- GPO-Parametres-Securite-Comptabilite

OU=Commercial
   +-- GPO-PareFeu-Commercial
   +-- GPO-WindowsUpdate-Commercial
   +-- GPO-Parametres-Securite-Commercial
```

Si les paramètres du pare-feu et de Windows Update sont identiques, les dupliquer multiplie les risques d'incohérence.

Une conception plus maintenable est généralement la suivante :

```text
OU=Ordinateurs
   |
   +-- GPO-SEC-Base-Postes
   +-- GPO-UPD-Postes
   +-- GPO-APP-Configuration-Commune
   |
   +-- OU=Comptabilite
   +-- OU=Commercial
   +-- OU=Pilotes
```

Il faut distinguer deux besoins :

- **Emplacement administratif** : l'OU détermine la structure et l'héritage.
- **Ciblage fonctionnel** : un groupe de sécurité détermine quels utilisateurs ou ordinateurs doivent recevoir une configuration particulière.

Une bonne architecture combine ces mécanismes plutôt que de multiplier les OU sans nécessité.

### 3.5 Déplacer un ordinateur dans une OU

Avec les outils graphiques :

1. Ouvrir `dsa.msc`.
2. Rechercher l'ordinateur.
3. Cliquer avec le bouton droit sur l'objet.
4. Choisir l'option permettant de le déplacer.
5. Sélectionner l'OU de destination.
6. Vérifier les stratégies qui s'appliqueront ensuite.

Avec PowerShell :

```powershell
Import-Module ActiveDirectory

$ordinateur = Get-ADComputer -Identity "PC1"

$ouDestination = "OU=Pilotes,OU=Postes,OU=Ordinateurs,DC=ad,DC=lab,DC=test"

Move-ADObject `
    -Identity $ordinateur.DistinguishedName `
    -TargetPath $ouDestination `
    -WhatIf
```

L'option `-WhatIf` permet d'afficher l'action envisagée sans l'effectuer.

Après vérification, on peut exécuter la commande sans `-WhatIf` :

```powershell
Move-ADObject `
    -Identity $ordinateur.DistinguishedName `
    -TargetPath $ouDestination
```

Il faut évidemment que l'OU existe et que le compte utilisé dispose des droits nécessaires.

Attention : déplacer un ordinateur peut changer les GPO qu'il reçoit. Le déplacement n'est donc pas une opération purement administrative ; il peut modifier le comportement de la machine.

## 4. Comprendre l'ordre de traitement des GPO

### 4.1 La règle LSDOU

La stratégie de groupe suit normalement l'ordre suivant :

- **L** : stratégie locale, *Local*.
- **S** : stratégie liée au site Active Directory, *Site*.
- **D** : stratégie liée au domaine, *Domain*.
- **OU** : stratégies liées aux unités d'organisation, *Organizational Unit*.

Les paramètres sont généralement appliqués dans cet ordre. À configuration contradictoire, une stratégie traitée plus tard prend habituellement le dessus, sous réserve des règles d'héritage, du filtrage, des options de priorité et des mécanismes particuliers.

Pour une OU imbriquée, les stratégies de l'OU parente sont traitées avant celles de l'OU enfant.

### 4.2 Schéma du traitement

```text
Utilisateur ou ordinateur
          |
          v
  1. GPO locale
          |
          v
  2. GPO du site
          |
          v
  3. GPO du domaine
          |
          v
  4. GPO de l'OU parente
          |
          v
  5. GPO de l'OU enfant
          |
          v
  Résultat final des stratégies
```

Exemple de structure :

```text
ad.lab.test
|
+-- GPO-Domaine-Commun
|
+-- OU=Ordinateurs
    |
    +-- GPO-SEC-Base-Postes
    |
    +-- OU=Pilotes
        |
        +-- GPO-Pilote-Configuration
```

Si une stratégie du domaine configure un paramètre à `A` et une stratégie plus spécifique le configure à `B`, c'est généralement `B` qui sera retenu si aucun mécanisme particulier ne modifie la priorité.

### 4.3 Exemple de conflit entre deux GPO

Imaginons ces deux stratégies :

| GPO | Emplacement | Paramètre |
|---|---|---|
| `GPO-Base-Entreprise` | Domaine | Écran de verrouillage après 15 minutes |
| `GPO-Pilote-Postes` | OU Pilotes | Écran de verrouillage après 10 minutes |

Pour un ordinateur dans l'OU Pilotes, la seconde stratégie est plus spécifique et le paramètre final devrait être de 10 minutes.

Toutefois, il est nécessaire de vérifier :

- Que la GPO est activée.
- Que sa liaison est activée.
- Que les permissions autorisent son application.
- Que les paramètres sont bien définis dans la bonne partie.
- Qu'aucun mécanisme spécial ne modifie l'ordre.
- Que la machine a actualisé ses stratégies.

C'est précisément pour cette raison que l'administrateur doit savoir produire et lire un rapport de stratégie résultante.

### 4.4 L'héritage des stratégies

Par défaut, une OU enfant reçoit les stratégies applicables liées à ses ancêtres.

Exemple :

```text
Domaine
  |
  +-- GPO-A
  |
  +-- OU=Postes
        |
        +-- GPO-B
        |
        +-- OU=Pilotes
              |
              +-- GPO-C
```

Un ordinateur situé dans l'OU Pilotes peut recevoir les GPO A, B et C, à condition que chacune soit dans son périmètre d'application.

### 4.5 Bloquer l'héritage

L'option de blocage de l'héritage permet à une OU d'empêcher l'application des GPO héritées depuis les niveaux supérieurs, sous réserve notamment du traitement des liaisons forcées.

Ce mécanisme est puissant mais doit être utilisé avec prudence.

Exemple :

```text
Domaine
  |
  +-- GPO-Base-Securite
  |
  +-- OU=Serveurs-Sensibles
        |
        +-- Blocage de l'héritage
        |
        +-- GPO-Serveurs-Sensibles
```

Le blocage peut empêcher la réception de paramètres importants, y compris des politiques de sécurité prévues pour l'ensemble de l'entreprise.

Il ne faut donc pas l'utiliser simplement pour résoudre un conflit dont la cause n'a pas été identifiée.

Avant de bloquer l'héritage, il faut déterminer :

1. Quelle stratégie pose problème.
2. Pourquoi elle s'applique à l'OU.
3. Si une liaison forcée est présente.
4. Si la GPO peut être corrigée ou son périmètre limité.
5. Comment les paramètres essentiels continueront d'être appliqués.

### 4.6 Forcer une liaison de GPO

Une liaison peut être marquée comme forcée dans la console de gestion des stratégies de groupe.

Ce mécanisme permet à une GPO liée à un niveau supérieur de conserver sa priorité et de traverser certaines restrictions d'héritage appliquées plus bas.

Le terme « forcée » ne signifie pas que tous les problèmes d'application seront contournés. Les permissions, la disponibilité du contrôleur de domaine, les filtres et les conditions nécessaires à l'application continuent de compter.

Il est recommandé de limiter les GPO forcées à des usages clairement justifiés.

### 4.7 Ordre de liaison

Lorsque plusieurs GPO sont liées au même conteneur, leur ordre de liaison intervient également dans la résolution des paramètres contradictoires.

Dans la console de gestion, il faut distinguer :

- L'ordre entre les niveaux d'Active Directory.
- L'ordre de traitement des GPO d'un même niveau.
- Le blocage de l'héritage.
- La liaison forcée.
- Le filtrage de sécurité.
- Les filtres WMI.
- Le traitement en boucle des paramètres utilisateur.

Ne cherche pas à mémoriser une règle simplifiée qui ignorerait ces éléments. Le rapport de stratégie résultante est le meilleur moyen de confirmer ce qui s'est réellement appliqué.

Documentation : [Traitement des stratégies de groupe](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-processing).

## 5. Filtrage de sécurité et ciblage précis

### 5.1 À quoi sert le filtrage de sécurité ?

Une GPO peut être liée à une OU tout en étant destinée à un sous-ensemble des utilisateurs ou des ordinateurs concernés.

Le filtrage de sécurité permet de définir quels principaux de sécurité ont le droit d'appliquer cette GPO.

Prenons l'exemple d'une stratégie réservée aux postes pilotes.

```text
OU=Postes
|
+-- PC1
+-- PC2
+-- PC3
+-- PC4

GPO : GPO-Pilote-Test

Filtrage de sécurité :
GG_Postes_Pilotes

Membres du groupe :
PC1
PC2
```

La GPO est liée à l'OU Postes, mais son application est limitée aux ordinateurs pilotes qui possèdent les permissions adéquates et qui se trouvent dans son périmètre.

### 5.2 Créer un groupe pour les postes pilotes

Dans Active Directory, il est recommandé d'utiliser un groupe de sécurité identifiable.

Exemple PowerShell :

```powershell
Import-Module ActiveDirectory

New-ADGroup `
    -Name "GG_Postes_Pilotes" `
    -SamAccountName "GG_Postes_Pilotes" `
    -GroupCategory Security `
    -GroupScope Global `
    -Path "OU=Groupes,DC=ad,DC=lab,DC=test"
```

L'OU Groupe doit exister dans ton environnement.

Ajouter un ordinateur au groupe se fait à l'aide de son compte ordinateur, dont le nom se termine généralement par `$`.

```powershell
Add-ADGroupMember `
    -Identity "GG_Postes_Pilotes" `
    -Members "PC1$","PC2$"
```

Pour vérifier les membres :

```powershell
Get-ADGroupMember -Identity "GG_Postes_Pilotes"
```

Selon le contexte et le moment où l'appartenance change, le poste peut devoir redémarrer ou renouveler son contexte machine pour que toutes les conditions d'appartenance soient prises en compte.

### 5.3 Utilisateurs et ordinateurs ne sont pas interchangeables

Il s'agit d'une des erreurs les plus fréquentes en administration des GPO.

Pour une GPO contenant des paramètres ordinateur, le principal qui doit être en mesure d'appliquer la stratégie est généralement le compte ordinateur.

Pour une GPO contenant des paramètres utilisateur, c'est généralement le compte utilisateur qui doit être autorisé.

Exemple :

```text
GPO : GPO-PareFeu-Postes
Ciblage : comptes ordinateurs

GPO : GPO-Lecteur-Comptabilite
Ciblage : comptes utilisateurs
```

Ajouter `adiallo` au groupe des postes pilotes ne fait pas du PC qu'il utilise un membre de ce groupe. De même, ajouter `PC1$` au groupe des postes pilotes ne rend pas automatiquement l'utilisateur `adiallo` membre d'un groupe utilisateur.

### 5.4 Conserver les permissions de lecture

Une GPO doit pouvoir être lue par le principal concerné afin d'être traitée.

Si tu modifies le filtrage de sécurité, ne supprime pas des permissions au hasard.

Par exemple, supprimer complètement l'accès de lecture d'un principal nécessaire peut empêcher la stratégie d'être évaluée correctement.

La démarche habituelle consiste à vérifier les permissions de la GPO et à garantir que les utilisateurs ou ordinateurs ciblés possèdent les droits appropriés, notamment la lecture et l'application lorsque cela est nécessaire.

Le filtrage de sécurité s'applique à la GPO entière. Il ne permet pas de sélectionner certains paramètres de la GPO pour les appliquer à un groupe et d'autres paramètres pour un second groupe.

### 5.5 Filtrage WMI

Un filtre WMI permet de conditionner l'application d'une GPO à des caractéristiques de la machine, par exemple son système d'exploitation.

Schéma :

```text
La GPO est liée à une OU
          |
          v
Le filtre de sécurité est satisfait ?
          |
       Oui / Non
          |
          v
Le filtre WMI est-il vrai ?
          |
       Oui / Non
          |
          v
Application ou non de la GPO
```

Exemple de filtre WMI basé sur le nom du système :

```sql
SELECT * FROM Win32_OperatingSystem
WHERE ProductType = "1"
```

Dans cette classe WMI, `ProductType = "1"` correspond aux systèmes clients. Les valeurs 2 et 3 correspondent respectivement aux contrôleurs de domaine et aux serveurs membres dans la classification de cette propriété.

Ce filtre peut servir à exclure les systèmes serveur d'une politique destinée aux clients.

Pour un environnement donné, il faut néanmoins vérifier le résultat sur les versions de Windows réellement utilisées.

### 5.6 Quand utiliser un filtre WMI ?

Utilise-le lorsque la différence est véritablement liée à une caractéristique de la machine, comme son type ou son système d'exploitation.

Évite de créer des filtres WMI complexes pour reproduire une organisation qui pourrait être exprimée plus clairement par des OU ou des groupes de sécurité.

Les filtres WMI sont évalués sur les ordinateurs et peuvent augmenter le temps de traitement des stratégies. Des requêtes mal conçues compliquent également le dépannage.

Pour cibler précisément quelques postes, un groupe de sécurité est souvent plus simple à maintenir.

## 6. Traitement en boucle : Group Policy Loopback

### 6.1 Le problème que Loopback résout

Normalement, les paramètres utilisateur suivent l'objet utilisateur dans Active Directory.

Mais certaines machines sont destinées à des usages particuliers.

Exemples :

- Salle de formation.
- Poste en libre-service.
- Kiosque d'accueil.
- Serveur de bureau à distance.
- Poste partagé entre de nombreux employés.

Dans ces scénarios, l'organisation peut vouloir que les paramètres utilisateur dépendent du poste sur lequel la personne se connecte.

Le traitement en boucle, ou *Loopback Processing*, sert à contrôler ce comportement.

### 6.2 Mode Remplacer

En mode Remplacer, les paramètres utilisateur provenant de leur emplacement habituel sont remplacés par ceux résultant du traitement des stratégies utilisateur définies pour l'ordinateur.

Schéma :

```text
Utilisateur adiallo
      |
      +-- Se connecte au PC1 personnel
      |       |
      |       +-- Stratégies utilisateur habituelles
      |
      +-- Se connecte au KIOSK01
              |
              +-- Loopback : Remplacer
              |
              +-- Paramètres utilisateur adaptés au kiosque
```

Ce mode est adapté lorsque l'environnement doit être presque entièrement déterminé par l'ordinateur.

### 6.3 Mode Fusionner

En mode Fusionner, les paramètres utilisateur habituels sont traités, puis les paramètres utilisateur liés au contexte de l'ordinateur sont ajoutés et peuvent prendre la priorité en cas de conflit.

Cela permet de conserver une partie de l'environnement habituel de l'utilisateur tout en ajoutant des restrictions ou des paramètres spécifiques au poste partagé.

### 6.4 Exemple d'utilisation

Une salle de formation contient vingt ordinateurs.

L'objectif est que chaque utilisateur retrouve un environnement limité sur ces machines, même s'il utilise habituellement un poste personnel.

Une GPO dédiée aux postes de formation peut configurer les paramètres utilisateur adaptés à cet environnement. Le traitement en boucle est configuré dans la partie ordinateur d'une GPO appropriée et liée aux ordinateurs concernés.

Le paramètre de traitement en boucle se trouve dans la catégorie des stratégies système relatives à la stratégie de groupe, dans les modèles administratifs. Le libellé précis peut varier selon la langue et les modèles administratifs utilisés.

### 6.5 Précautions

Le Loopback ne doit pas être activé partout par facilité.

Il peut rendre le diagnostic plus complexe, car les paramètres utilisateur dépendent alors du poste sur lequel la session s'ouvre.

Il est préférable de le réserver aux postes ayant un usage fonctionnel particulier et de documenter le mode choisi.

## 7. Stratégies classiques et préférences de stratégie de groupe

### 7.1 Les stratégies classiques

Les paramètres de stratégie classiques servent à imposer une configuration.

Lorsqu'un administrateur définit un paramètre de manière contraignante, l'utilisateur ne peut généralement pas le modifier de manière permanente à travers l'interface habituelle de Windows.

Exemples typiques :

- Paramètres de sécurité.
- Paramètres de pare-feu.
- Paramètres imposés des composants Windows.
- Restrictions administratives.
- Certaines configurations de Windows Update.

### 7.2 Les préférences de stratégie de groupe

Les préférences de stratégie de groupe permettent de distribuer des configurations que l'utilisateur peut parfois modifier.

Exemples :

- Mapper un lecteur réseau.
- Créer un raccourci.
- Créer un dossier.
- Copier un fichier de configuration.
- Créer une tâche planifiée.
- Gérer certains paramètres du Registre.
- Configurer des imprimantes.

Une préférence est généralement réappliquée au cycle de mise à jour de la stratégie, mais elle n'empêche pas nécessairement l'utilisateur de la modifier entre deux actualisations.

### 7.3 Comparaison

| Critère | Stratégie classique | Préférence |
|---|---|---|
| Objectif principal | Imposer un paramètre | Distribuer une configuration |
| Modification par l'utilisateur | Généralement bloquée pour le paramètre géré | Peut être possible |
| Exemples | Paramètres de sécurité, règles imposées | Lecteurs réseau, raccourcis, fichiers |
| Ciblage par élément | Selon les mécanismes du paramètre | Ciblage au niveau de l'élément disponible |
| Gestion de la suppression | Dépend du paramètre de stratégie | Peut nécessiter une action de suppression explicite |

Les paramètres de stratégie peuvent prendre le dessus sur les préférences lorsqu'ils gèrent le même réglage.

### 7.4 Créer un lecteur réseau avec une préférence

Imaginons que les utilisateurs de la comptabilité doivent accéder au partage :

`\\FILE1\Comptabilite`

La lettre de lecteur choisie sera `S:`.

Dans la console GPMC :

1. Créer une GPO appelée `GPO-USER-Lecteur-Comptabilite`.
2. L'associer à l'OU adaptée ou la cibler par un groupe.
3. Modifier la GPO.
4. Aller dans Configuration utilisateur.
5. Ouvrir Préférences.
6. Ouvrir Paramètres Windows.
7. Sélectionner Mappages de lecteurs.
8. Créer un nouvel élément.
9. Choisir l'action adaptée, généralement `Mettre à jour` ou `Créer`.
10. Renseigner la lettre `S:`.
11. Renseigner le chemin UNC `\\FILE1\Comptabilite`.
12. Configurer le ciblage approprié.
13. Tester sur un compte de la comptabilité.

Le serveur `FILE1` doit exister, le partage doit être accessible et les permissions de partage ainsi que les permissions NTFS doivent autoriser l'accès.

Un lecteur réseau correctement mappé n'accorde pas, à lui seul, l'autorisation de lire ou de modifier les fichiers.

### 7.5 Comprendre les actions des préférences

Les préférences proposent généralement plusieurs actions, selon l'extension concernée :

- **Créer** : créer l'élément s'il n'existe pas.
- **Mettre à jour** : créer ou modifier l'élément pour atteindre les valeurs définies.
- **Remplacer** : supprimer puis recréer l'élément.
- **Supprimer** : retirer l'élément concerné.

Il faut comprendre les conséquences de chaque action.

Par exemple, remplacer un lecteur ou un fichier à chaque actualisation peut entraîner une réinitialisation indésirable de certaines informations ou provoquer des interruptions.

L'option de suppression automatique lorsque l'élément n'est plus dans le périmètre peut également être utile, mais elle doit être configurée et testée explicitement.

### 7.6 Ciblage au niveau de l'élément

Les préférences peuvent inclure des règles de ciblage supplémentaires.

Par exemple, une même GPO peut contenir plusieurs éléments :

```text
GPO : GPO-USER-Ressources
|
+-- Lecteur S:
|      Ciblage : Groupe GG_Comptabilite
|
+-- Lecteur V:
|      Ciblage : Groupe GG_Commercial
|
+-- Raccourci Documentation
       Ciblage : Tous les utilisateurs concernés
```

Le ciblage au niveau de l'élément est utile lorsqu'une GPO peut être partagée entre différents profils d'utilisateurs.

Il faut toutefois éviter d'accumuler trop de conditions complexes dans une même stratégie. Une GPO lisible et simple est plus facile à maintenir.

Documentation : [Préférences de stratégie de groupe](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-preferences).

## 8. Structurer les GPO de manière professionnelle

### 8.1 Une GPO doit avoir un objectif clair

Une GPO qui contient des dizaines de paramètres sans rapport entre eux est difficile à administrer.

Par exemple, il est préférable de séparer :

- La sécurité de base.
- La configuration de Windows Update.
- Les paramètres d'environnement utilisateur.
- Les paramètres propres à une application.
- Les paramètres des postes pilotes.
- Les paramètres des postes partagés.

Cela ne veut pas dire qu'il faut créer une GPO pour chaque paramètre. Trop de petites GPO peuvent aussi augmenter la complexité et les besoins de traitement.

La bonne approche est de regrouper les paramètres qui partagent la même finalité, le même périmètre et le même cycle de changement.

### 8.2 Convention de nommage

Une convention cohérente aide à comprendre rapidement le rôle d'une stratégie.

Exemple :

```text
GPO-SEC-Base-Postes
GPO-SEC-PareFeu-Postes
GPO-SEC-BitLocker-Portables
GPO-UPD-Pilote-Windows
GPO-UPD-Production-Windows
GPO-USER-Lecteur-Comptabilite
GPO-APP-Configuration-Navigateur
GPO-LAB-Restrictions-Formation
GPO-SRV-Parametres-Membres
```

Les préfixes sont des conventions d'entreprise, pas des exigences techniques de Windows.

Ils doivent rester suffisamment courts pour être lisibles dans les consoles et les rapports.

### 8.3 Documenter le périmètre d'une GPO

Pour chaque GPO importante, documente :

- Son objectif.
- Son propriétaire administratif.
- Son OU de liaison.
- Son type de paramètres.
- Ses groupes de sécurité.
- Son filtre WMI éventuel.
- Les versions de Windows visées.
- Les prérequis.
- Les dépendances.
- Les tests effectués.
- La date de la dernière modification.
- La procédure de retour arrière.

Exemple de fiche :

```text
Nom : GPO-SEC-Base-Postes
Objectif : appliquer la configuration de sécurité standard
Périmètre : OU=Postes
Exceptions : kiosques et machines de laboratoire selon la politique
Type : Configuration ordinateur
Responsable : équipe systèmes
Validation : parc pilote
Retour arrière : restauration de la GPO précédente
Dépendances : modèles administratifs validés
```

### 8.4 Désactiver une partie inutilisée de la GPO

Une GPO contient une partie ordinateur et une partie utilisateur.

Si une stratégie ne contient que des paramètres ordinateur, sa partie utilisateur peut être désactivée dans la console de gestion, et inversement.

Cela peut réduire une partie du travail de traitement inutile et clarifier l'intention de la GPO.

Ne désactive pas une partie sans avoir vérifié qu'aucun paramètre nécessaire n'y est défini.

## 9. Gestion des modèles administratifs ADMX

### 9.1 À quoi servent les fichiers ADMX ?

Les modèles administratifs fournissent les définitions permettant d'afficher et de configurer de nombreux paramètres de Windows et de certaines applications.

Les fichiers ADMX décrivent la structure des paramètres. Les fichiers de langue ADML fournissent les libellés localisés.

Une console qui utilise des modèles différents de ceux attendus peut présenter des paramètres manquants, des libellés incorrects ou des différences d'affichage.

### 9.2 Le magasin central

Dans un domaine Active Directory, le magasin central permet d'utiliser un ensemble commun de modèles administratifs pour administrer les GPO.

Le chemin conventionnel est :

`\\ad.lab.test\SYSVOL\ad.lab.test\Policies\PolicyDefinitions`

Ce dossier doit être préparé si l'organisation décide d'utiliser un magasin central.

Schéma :

```text
\\ad.lab.test\SYSVOL\ad.lab.test\Policies\
|
+-- PolicyDefinitions
    |
    +-- Windows.admx
    +-- System.admx
    +-- Explorer.admx
    |
    +-- fr-FR
    |   |
    |   +-- Windows.adml
    |   +-- System.adml
    |
    +-- en-US
        |
        +-- Windows.adml
        +-- System.adml
```

Il s'agit d'un exemple simplifié. Les noms et la quantité de fichiers dépendent des produits et des modèles installés.

### 9.3 Procédure de préparation

Avant de remplacer les modèles :

1. Inventorier les modèles actuellement utilisés.
2. Télécharger les modèles provenant d'une source officielle.
3. Vérifier leur adéquation avec les systèmes administrés.
4. Sauvegarder le contenu du magasin central existant.
5. Préparer une copie de test.
6. Copier les fichiers ADMX et leurs fichiers ADML correspondants.
7. Vérifier les langues nécessaires.
8. Ouvrir GPMC et vérifier l'affichage des paramètres.
9. Tester l'édition et la génération des rapports.
10. Documenter la version des modèles déployés.

Il faut éviter de copier aveuglément un mélange de fichiers de versions différentes. Les dépendances entre les fichiers doivent être prises en compte.

### 9.4 Les modèles ne mettent pas automatiquement à jour les systèmes

Mettre à jour un fichier ADMX met à jour les définitions disponibles dans les outils d'administration ; cela ne met pas automatiquement à jour Windows sur les postes clients.

La prise en charge réelle d'un paramètre dépend notamment du système cible, de sa version, de ses composants et de l'existence du paramètre sur cet OS.

La documentation du modèle ou du produit doit donc être vérifiée avant le déploiement d'une configuration récente.

## 10. Sauvegarde, restauration et gestion du changement

### 10.1 Pourquoi sauvegarder les GPO ?

Une GPO est un objet important de l'infrastructure.

Une erreur peut avoir un effet immédiat ou différé sur plusieurs machines. Il est donc nécessaire de pouvoir retrouver les paramètres antérieurs.

Il faut sauvegarder les GPO :

- Avant un changement important.
- Avant une mise à jour des modèles administratifs.
- Avant une réorganisation des OU.
- Avant une modification des filtres.
- Avant l'introduction d'une nouvelle politique de sécurité.
- À intervalles réguliers selon les exigences de l'entreprise.

La sauvegarde doit être conservée sur un emplacement protégé, séparé autant que possible de l'environnement qu'elle protège, et couvert par une politique de sauvegarde.

### 10.2 Sauvegarder toutes les GPO avec PowerShell

Sur une machine où le module `GroupPolicy` est disponible :

```powershell
Import-Module GroupPolicy

$cheminSauvegarde = "C:\GPO-Backups"

New-Item `
    -Path $cheminSauvegarde `
    -ItemType Directory `
    -Force

Backup-GPO `
    -All `
    -Path $cheminSauvegarde `
    -Comment "Sauvegarde avant changement"
```

Le chemin doit être accessible et correctement protégé. Pour une sauvegarde de production, l'emplacement doit être choisi conformément à la politique de sauvegarde de l'organisation.

`Backup-GPO` sauvegarde les objets de stratégie. La sauvegarde d'une GPO ne remplace pas une stratégie complète de protection des données d'Active Directory et de SYSVOL.

### 10.3 Générer un rapport de toutes les GPO

Un rapport HTML permet de documenter les stratégies existantes.

```powershell
Import-Module GroupPolicy

New-Item `
    -Path "C:\Rapports-GPO" `
    -ItemType Directory `
    -Force

Get-GPOReport `
    -All `
    -ReportType Html `
    -Path "C:\Rapports-GPO\Toutes-les-GPO.html"
```

Le rapport sert à examiner le contenu des GPO et à préparer les changements.

Il ne constitue pas une preuve que chaque paramètre a été appliqué à chaque poste. Pour cela, il faut consulter le résultat effectif sur les machines concernées.

### 10.4 Lister les GPO

```powershell
Get-GPO -All |
    Select-Object DisplayName,
                  Id,
                  GpoStatus,
                  CreationTime,
                  ModificationTime |
    Sort-Object DisplayName
```

Ce rapport peut servir de base à un inventaire des objets de stratégie.

### 10.5 Restaurer une GPO

Une restauration de GPO doit être préparée et testée, notamment parce qu'une GPO peut avoir été modifiée ou liée à des OU différentes depuis sa sauvegarde.

Pour restaurer une GPO existante depuis une sauvegarde :

```powershell
Restore-GPO `
    -Name "GPO-SEC-Base-Postes" `
    -Path "C:\GPO-Backups"
```

La sauvegarde doit bien contenir une version correspondant à l'objet concerné.

La cmdlet de restauration rétablit le contenu de la GPO ; elle ne remplace pas la vérification de ses liaisons, du filtrage de sécurité et des effets sur les postes.

### 10.6 Gérer les changements en environnement de production

Une bonne procédure de changement suit le cycle suivant :

```text
Demande de changement
        |
        v
Analyse des risques
        |
        v
Sauvegarde des GPO
        |
        v
Création ou modification
        |
        v
Test sur quelques postes
        |
        v
Validation technique et fonctionnelle
        |
        v
Déploiement progressif
        |
        v
Vérification des résultats
        |
        v
Documentation et clôture
```

Si le test échoue, le changement ne doit pas être généralisé.

La mise en production ne doit pas être basée sur le seul fait que le paramètre apparaît correctement dans la console GPMC. Il faut vérifier le résultat sur les machines.

## 11. Sécuriser le parc avec les GPO

### 11.1 La sécurité doit être cohérente

Les postes doivent appliquer un socle de sécurité homogène, tout en tenant compte des usages.

Les objectifs peuvent être :

- Réduire les droits administratifs locaux.
- Maintenir le pare-feu activé.
- Limiter les protocoles et services inutiles.
- Protéger les identifiants.
- Activer des paramètres de journalisation.
- Contrôler les mises à jour.
- Chiffrer les équipements portables lorsque la politique l'exige.
- Réduire les configurations non conformes.
- Protéger l'accès aux ressources sensibles.

Ces objectifs ne nécessitent pas nécessairement une seule GPO. Ils doivent être traduits en politiques documentées puis testées.

### 11.2 Construire un socle de sécurité

Exemple de découpage :

```text
GPO-SEC-Base-Postes
|
+-- Paramètres système communs
+-- Paramètres de sécurité applicables
+-- Politique de journalisation
+-- Paramètres des fonctions Windows prises en charge

GPO-SEC-PareFeu-Postes
|
+-- Profils de pare-feu
+-- Règles autorisées nécessaires
+-- Vérification des exceptions

GPO-SEC-BitLocker-Portables
|
+-- Politique de chiffrement adaptée
+-- Sauvegarde des clés de récupération
+-- Conditions de conformité

GPO-SEC-LAPS
|
+-- Gestion des mots de passe administrateur locaux
+-- Accès contrôlé aux mots de passe
+-- Rotation et audit
```

Ce schéma est une proposition d'organisation, pas une liste de paramètres à appliquer aveuglément.

### 11.3 Le pare-feu Windows

Le pare-feu Windows doit faire partie du socle de sécurité des postes.

Avant de modifier sa configuration :

1. Inventorier les applications qui nécessitent des connexions entrantes.
2. Identifier les flux réellement nécessaires.
3. Tester les règles sur un poste pilote.
4. Éviter les autorisations trop larges.
5. Vérifier que les règles de gestion à distance restent opérationnelles.
6. Vérifier les journaux et la connectivité après changement.

Une règle autorisant tout le trafic entrant pour résoudre un problème d'application est une mauvaise pratique. Il faut identifier les ports, les protocoles, les profils réseau et les destinations nécessaires.

### 11.4 Réduire les privilèges administratifs

Les utilisateurs standards ne devraient pas disposer de droits administratifs locaux sans justification.

L'administration quotidienne du parc ne devrait pas non plus exiger que chaque technicien utilise systématiquement un compte Domain Admin.

Sépare les usages :

```text
Compte utilisateur quotidien
        |
        +-- Courrier, navigation et applications métier

Compte d'administration dédié
        |
        +-- Tâches d'administration autorisées

Compte Domain Admin
        |
        +-- Opérations exceptionnellement nécessaires
            sur le domaine et les contrôleurs de domaine
```

Les comptes Domain Admin doivent être particulièrement protégés, avec un périmètre d'utilisation strictement limité.

Pour les postes de travail, des groupes d'administration dédiés et des permissions limitées sont préférables.

### 11.5 Gérer les mots de passe des administrateurs locaux avec Windows LAPS

Un parc peut contenir de nombreux comptes administrateurs locaux.

Réutiliser le même mot de passe local sur tous les postes crée un risque important : la compromission d'une machine peut faciliter la compromission d'autres machines utilisant le même secret.

Windows LAPS permet de gérer des mots de passe administrateur locaux uniques et renouvelés automatiquement, avec sauvegarde des mots de passe dans un annuaire autorisé selon le scénario retenu.

Dans le cas d'un domaine Active Directory classique, Windows LAPS peut être configuré par stratégie de groupe pour stocker les secrets dans Active Directory, si les conditions requises sont réunies.

Les tâches principales sont :

1. Vérifier que les versions de Windows sont compatibles.
2. Préparer les permissions Active Directory nécessaires.
3. Définir le compte administrateur local à gérer.
4. Configurer la politique Windows LAPS.
5. Définir la durée de vie et la complexité des mots de passe.
6. Restreindre les personnes autorisées à lire les secrets.
7. Vérifier la sauvegarde des mots de passe et la rotation.
8. Examiner les journaux et tester la récupération autorisée.

Il ne suffit pas d'activer une GPO : il faut aussi configurer correctement le répertoire, les autorisations de lecture des secrets et les procédures opérationnelles.

**Ne stocke jamais un mot de passe administrateur partagé dans un script ou dans une préférence de stratégie de groupe.** Les anciennes méthodes de déploiement de mots de passe avec certaines préférences présentent des risques connus. Utilise une méthode dédiée comme Windows LAPS.

Documentation : [Vue d'ensemble de Windows LAPS](https://learn.microsoft.com/fr-fr/windows-server/identity/laps/laps-overview).

### 11.6 Protéger BitLocker et les clés de récupération

Le chiffrement des postes portables peut protéger les données lorsque l'équipement est perdu ou volé.

Une stratégie de déploiement BitLocker doit tenir compte :

- Des caractéristiques matérielles.
- De la compatibilité TPM.
- Des méthodes d'authentification autorisées.
- De la sauvegarde des clés de récupération.
- Des procédures d'assistance.
- Des conséquences d'une modification des paramètres de démarrage.

Il est indispensable de vérifier que les clés de récupération sont effectivement sauvegardées dans l'emplacement prévu avant de généraliser le chiffrement.

Une stratégie de chiffrement sans procédure de récupération correctement testée risque de transformer un incident matériel ou de configuration en perte d'accès aux données.

### 11.7 Utiliser les bases de référence de sécurité

Microsoft publie des bases de référence de sécurité adaptées à plusieurs produits Windows.

Le **Security Compliance Toolkit** comprend des outils et des configurations de référence qui peuvent aider à comparer une configuration avec les recommandations disponibles.

Une base de référence n'est pas un ensemble à appliquer automatiquement à toutes les machines. Les paramètres proposés doivent être évalués par rapport aux applications, aux contraintes d'exploitation et aux exigences de l'organisation.

La bonne démarche consiste à :

1. Choisir une base adaptée à la version de Windows.
2. Examiner les paramètres.
3. Identifier les différences par rapport à la configuration actuelle.
4. Tester sur un groupe pilote.
5. Mesurer les régressions éventuelles.
6. Adapter la stratégie si un besoin métier le justifie.
7. Documenter les dérogations.

Documentation : [Microsoft Security Compliance Toolkit](https://learn.microsoft.com/windows/security/operating-system-security/device-management/windows-security-configuration-framework/security-compliance-toolkit-10).

## 12. Déployer les mises à jour Windows

### 12.1 Pourquoi organiser les mises à jour ?

Appliquer les mises à jour à tous les postes au même moment sans test peut provoquer des interruptions ou des incompatibilités.

Un processus de gestion des mises à jour doit définir :

- Le périmètre des machines.
- Le calendrier.
- Les groupes pilotes.
- Les conditions de validation.
- Les échéances.
- Les règles de redémarrage.
- Le traitement des échecs.
- Les indicateurs de conformité.

Les GPO permettent de contrôler certains paramètres de Windows Update, tandis que le service ou la solution de gestion retenu détermine les capacités effectives de pilotage.

### 12.2 Les anneaux de déploiement

Une méthode fréquemment utilisée consiste à répartir les machines en anneaux.

```text
Nouvelles mises à jour disponibles
              |
              v
       ANNEAU 0 : LABORATOIRE
       Quelques machines de test
              |
              v
       ANNEAU 1 : PILOTE IT
       Équipe informatique
              |
              v
       ANNEAU 2 : PILOTE MÉTIER
       Groupe limité d'utilisateurs
              |
              v
       ANNEAU 3 : PRODUCTION
       Déploiement plus large
```

Les anneaux permettent d'identifier les problèmes avant qu'ils n'affectent la majorité du parc.

Les périodes et critères de passage doivent dépendre des risques, de la criticité des équipements et du type de mise à jour.

### 12.3 Organiser les OU et les groupes pilotes

Une organisation possible est :

```text
OU=Ordinateurs
|
+-- OU=Pilotes
|   |
|   +-- PC1
|   +-- PC2
|
+-- OU=Production
    |
    +-- PC10
    +-- PC11
    +-- PC12
```

Selon l'architecture retenue, les anneaux peuvent également être gérés par des groupes de sécurité ou par les mécanismes de ciblage de la solution de mise à jour.

Il faut éviter les mécanismes de ciblage concurrents qui rendraient difficile de déterminer pourquoi une mise à jour a été reçue ou retardée.

### 12.4 WSUS et son rôle

Windows Server Update Services, ou WSUS, est un rôle Windows Server qui permet de centraliser la gestion de certaines mises à jour Windows.

Il peut notamment servir à :

- Contrôler les mises à jour proposées aux clients.
- Approuver certaines mises à jour.
- Organiser les équipements dans des groupes.
- Définir une source interne de mises à jour.
- Contrôler certains calendriers de déploiement.

La configuration des clients peut être distribuée par GPO afin de désigner le serveur WSUS et de définir les comportements de mise à jour.

**Point important : WSUS est désormais déconseillé pour le développement de nouvelles fonctionnalités. Il reste pris en charge pour les déploiements de production selon le cycle de vie applicable.** Il est donc nécessaire de vérifier les orientations et capacités Microsoft pertinentes avant de choisir une nouvelle architecture de gestion des mises à jour.

Documentation : [Déployer les mises à jour des clients Windows à l'aide de WSUS](https://learn.microsoft.com/fr-fr/windows/deployment/update/waas-manage-updates-wsus).

### 12.5 Exemple de conception

Supposons que le serveur WSUS interne utilise l'adresse DNS :

`http://WSUS1.ad.lab.test:8530`

La valeur ci-dessus est un exemple de laboratoire ; il faut vérifier le port et le protocole réellement configurés dans l'infrastructure.

Une GPO destinée aux clients concernés peut configurer l'emplacement intranet du service de mise à jour et les paramètres de mise à jour automatique.

Avant le déploiement, vérifie :

- Que le nom du serveur se résout correctement.
- Que le port choisi est accessible depuis les clients.
- Que le service WSUS est opérationnel.
- Que les paramètres GPO sont adaptés aux versions de Windows.
- Que les anneaux de déploiement sont correctement définis.
- Que les machines pilotes reçoivent les mises à jour comme prévu.
- Que les rapports permettent de distinguer les machines à jour des machines en erreur.

### 12.6 Ne pas confondre GPO et moteur de mise à jour

La GPO configure le comportement du client ; elle ne remplace pas nécessairement tous les mécanismes de téléchargement, d'approbation, de déploiement et de reporting.

Un poste qui reçoit correctement la GPO peut encore échouer à télécharger ou installer une mise à jour.

Pour diagnostiquer, il faut examiner à la fois :

- Le résultat de stratégie de groupe.
- La connectivité au service de mise à jour.
- L'état des services pertinents.
- Les journaux Windows Update.
- Le statut de l'installation.
- Les éventuels redémarrages en attente.

## 13. Déployer des logiciels

### 13.1 Les méthodes de distribution

Dans un parc Windows, plusieurs méthodes de distribution peuvent être utilisées :

- Installation manuelle contrôlée.
- Déploiement MSI par stratégie de groupe.
- Script PowerShell d'installation.
- Outil de gestion centralisée des applications.
- Solution de gestion moderne des terminaux.

Le choix dépend de la taille du parc, de la complexité des paquets, des contraintes de sécurité et des besoins d'inventaire.

La fonctionnalité d'installation de logiciels par GPO est adaptée à certains scénarios, notamment aux packages Windows Installer MSI. Elle n'est pas une solution universelle pour tous les formats d'installation modernes.

### 13.2 Installation MSI par GPO

Supposons que le package soit stocké sur un serveur de fichiers :

`\\FILE1\Packages\LogicielA.msi`

Le chemin UNC doit être utilisé plutôt qu'une lettre de lecteur mappée, car l'installation peut être exécutée dans le contexte du compte ordinateur avant l'ouverture de session.

Exemple de conception :

```text
GPO-APP-LogicielA
       |
       v
Configuration ordinateur
       |
       v
Stratégies
       |
       v
Paramètres du logiciel
       |
       v
Installation de logiciels
       |
       v
Package MSI accessible via UNC
       |
       v
Installation au démarrage selon le scénario
```

### 13.3 Procédure générale

1. Vérifier la compatibilité de l'application avec les versions de Windows.
2. Tester le fichier MSI sur une machine pilote.
3. Vérifier la source et l'intégrité du package.
4. Préparer un partage réseau adapté.
5. Accorder aux comptes ordinateur ciblés un accès en lecture au package.
6. Créer une GPO consacrée à ce déploiement.
7. Ajouter le package MSI depuis son chemin UNC.
8. Choisir l'affectation prévue par le scénario.
9. Lier la GPO et configurer son ciblage.
10. Actualiser les stratégies sur un poste pilote.
11. Redémarrer lorsque le type d'installation l'exige.
12. Vérifier que l'application est installée et fonctionne.
13. Examiner les journaux en cas d'échec.
14. Généraliser uniquement après validation.

L'installation doit utiliser un package adapté au mode de déploiement et aux permissions disponibles.

### 13.4 Tester une installation MSI en ligne de commande

Sur un poste de test, une installation silencieuse peut être testée avec `msiexec`.

Exemple :

```powershell
msiexec.exe /i "C:\Packages\LogicielA.msi" /qn /norestart /L*v "C:\Windows\Temp\LogicielA-install.log"
```

Explication :

- `/i` demande l'installation.
- `/qn` n'affiche aucune interface utilisateur.
- `/norestart` demande de ne pas redémarrer automatiquement.
- `/L*v` génère un journal détaillé.

Les options sont à adapter au package et aux exigences de l'application. Une installation silencieuse ne signifie pas que l'installation est nécessairement réussie.

Le code de sortie, le journal et l'état final du logiciel doivent être contrôlés.

Documentation : [Commande msiexec](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/msiexec).

### 13.5 Les autorisations sur le package

Le programme d'installation doit pouvoir lire son package.

Il faut vérifier :

- Les permissions de partage.
- Les permissions NTFS.
- L'accès des comptes ordinateurs concernés.
- La disponibilité du serveur au moment du traitement.
- La résolution DNS.
- La connectivité réseau.
- Les journaux d'installation.

Un utilisateur peut avoir accès à un fichier alors que le compte ordinateur qui exécute l'installation ne peut pas y accéder. C'est particulièrement important pour les installations exécutées pendant le démarrage.

### 13.6 Désinstallation et mise à niveau

Les opérations de désinstallation ou de mise à niveau doivent être planifiées.

Avant de retirer une application :

1. Inventorier les machines qui l'utilisent.
2. Vérifier les dépendances.
3. Tester la désinstallation sur une machine pilote.
4. Prévoir une méthode de réinstallation.
5. Vérifier les données utilisateur concernées.
6. Définir les critères de validation.

Il ne faut pas supprimer immédiatement le package source ou détruire la GPO alors que des postes n'ont pas terminé le traitement prévu.

### 13.7 Quand utiliser une autre solution ?

Un déploiement GPO peut devenir difficile à maintenir si les paquets nécessitent des mises à jour fréquentes, des conditions complexes, des dépendances nombreuses ou un reporting détaillé.

Pour de grandes organisations, une solution de gestion d'applications et de terminaux adaptée à l'environnement peut être plus appropriée.

Une stratégie de groupe doit rester un outil de configuration centralisée, et non être détournée pour reproduire à tout prix un système complet de gestion des applications.

## 14. Administrer les postes à distance avec PowerShell

### 14.1 Pourquoi l'administration distante est-elle utile ?

Une gestion de parc efficace doit limiter les interventions physiques lorsqu'elles ne sont pas nécessaires.

PowerShell permet notamment de :

- Lire les informations système.
- Examiner des services.
- Interroger l'espace disque.
- Exécuter des commandes de diagnostic.
- Collecter des données d'inventaire.
- Actualiser les GPO à distance dans les conditions requises.
- Automatiser certaines opérations de maintenance.

Cette capacité repose sur la connectivité, les permissions et les mécanismes d'administration à distance correctement configurés.

### 14.2 Principe de fonctionnement

```text
Poste administrateur
        |
        | PowerShell Remoting
        v
Mécanisme distant autorisé
        |
        v
Machine cible : PC1
        |
        +-- Exécute la commande
        +-- Renvoie le résultat
```

L'administration distante doit utiliser des comptes autorisés et une méthode de connexion sécurisée.

### 14.3 Vérifier le poste cible

Depuis une machine autorisée :

```powershell
Test-Connection -ComputerName PC1 -Count 2
```

Ce test peut fournir un indice de connectivité, mais l'absence de réponse ICMP ne prouve pas à elle seule que la machine est hors service.

Il faut ensuite vérifier le DNS et les ports de gestion réellement nécessaires.

```powershell
Resolve-DnsName PC1.ad.lab.test
```

La résolution DNS doit renvoyer une réponse cohérente avec l'infrastructure.

### 14.4 PowerShell Remoting

PowerShell Remoting s'appuie fréquemment sur WinRM pour les sessions distantes Windows.

Dans une infrastructure de domaine, la configuration doit être adaptée à la politique de sécurité, aux règles de pare-feu, aux comptes autorisés et aux exigences d'authentification.

Sur une machine de test compatible, un administrateur autorisé peut configurer la gestion à distance selon les recommandations Microsoft, puis vérifier les accès avant d'automatiser des opérations.

N'active pas indistinctement tous les protocoles et toutes les connexions distantes sur l'ensemble du parc.

### 14.5 Exécuter une commande distante

Exemple :

```powershell
Invoke-Command `
    -ComputerName "PC1.ad.lab.test" `
    -ScriptBlock {
        Get-CimInstance Win32_OperatingSystem |
            Select-Object Caption,
                          Version,
                          LastBootUpTime
    }
```

Cette commande interroge les informations du système d'exploitation sur le poste distant.

Elle exige que la méthode de remoting utilisée soit disponible et que le compte dispose des autorisations nécessaires.

### 14.6 Interroger plusieurs postes

Le principe peut être étendu à un groupe limité d'ordinateurs.

```powershell
$ordinateurs = @(
    "PC1.ad.lab.test",
    "PC2.ad.lab.test"
)

Invoke-Command `
    -ComputerName $ordinateurs `
    -ScriptBlock {
        $os = Get-CimInstance Win32_OperatingSystem

        [PSCustomObject]@{
            Ordinateur = $env:COMPUTERNAME
            Systeme    = $os.Caption
            Version    = $os.Version
            Demarrage  = $os.LastBootUpTime
        }
    } `
    -ErrorAction Continue
```

Une machine inaccessible peut provoquer une erreur alors que les autres répondent. En production, il faut capturer les erreurs, enregistrer les résultats et distinguer les machines injoignables des machines ayant retourné un résultat valide.

### 14.7 Sécuriser l'administration à distance

Une bonne configuration d'administration distante doit respecter les principes suivants :

- Utiliser des comptes dédiés et autorisés.
- Limiter les membres des groupes d'administration.
- Éviter de stocker des mots de passe en clair dans des scripts.
- Ne pas désactiver arbitrairement la validation des certificats.
- Ne pas ouvrir de ports à tout le réseau sans justification.
- Consigner les opérations administratives importantes.
- Protéger les scripts de gestion.
- Tester les droits et les flux réseau.
- Séparer les postes d'administration du travail quotidien lorsque l'architecture l'exige.

## 15. Actualiser les stratégies à distance

### 15.1 Actualisation locale

Sur PC1, les deux commandes suivantes sont utiles :

```cmd
gpupdate
```

Pour forcer le retraitement des paramètres :

```cmd
gpupdate /force
```

Le commutateur `/force` force la réapplication des paramètres de stratégie. Il ne garantit pas qu'une GPO inaccessible ou mal ciblée sera corrigée.

Certains paramètres nécessitent une fermeture de session ou un redémarrage pour produire leur effet.

### 15.2 Actualisation à distance avec PowerShell

Le module `GroupPolicy` fournit la commande `Invoke-GPUpdate`.

Exemple :

```powershell
Import-Module GroupPolicy

Invoke-GPUpdate `
    -Computer "PC1" `
    -RandomDelayInMinutes 0 `
    -Force
```

La commande programme l'actualisation de la stratégie sur la machine distante. Elle nécessite les conditions de connectivité, les autorisations et la configuration attendues.

Pour plusieurs postes, il est préférable de commencer par un petit groupe plutôt que de déclencher immédiatement une opération générale.

### 15.3 Actualiser l'ensemble des ordinateurs d'une OU

Exemple de préparation d'une liste :

```powershell
Import-Module ActiveDirectory

$ordinateurs = Get-ADComputer `
    -SearchBase "OU=Pilotes,OU=Postes,OU=Ordinateurs,DC=ad,DC=lab,DC=test" `
    -Filter * |
    Select-Object -ExpandProperty Name

$ordinateurs
```

Le résultat doit être examiné avant de lancer les mises à jour.

Si la liste correspond exactement au périmètre prévu et si les conditions d'administration distante sont réunies :

```powershell
Import-Module GroupPolicy

foreach ($ordinateur in $ordinateurs) {
    try {
        Invoke-GPUpdate `
            -Computer $ordinateur `
            -RandomDelayInMinutes 0 `
            -Force `
            -ErrorAction Stop

        Write-Host "Demande envoyée : $ordinateur"
    }
    catch {
        Write-Warning "Échec pour $ordinateur : $($_.Exception.Message)"
    }
}
```

Le message de réussite signifie que la demande a été envoyée ou programmée, pas nécessairement que tous les paramètres ont été correctement appliqués.

Il faut ensuite vérifier les résultats sur les machines concernées.

Documentation : [Invoke-GPUpdate](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/invoke-gpupdate).

## 16. Inventorier les ordinateurs Active Directory

### 16.1 Annuaire et inventaire ne signifient pas la même chose

L'objet ordinateur Active Directory fournit des informations sur le compte machine.

Un inventaire complet peut aussi nécessiter :

- Le modèle matériel.
- Le fabricant.
- Le numéro de série.
- La mémoire installée.
- Le système d'exploitation.
- La version et le niveau de mise à jour.
- L'espace disque.
- Les applications installées.
- Les informations de chiffrement.
- L'état de protection.
- Le dernier contrôle de conformité.

Toutes ces informations ne sont pas nécessairement présentes dans Active Directory.

Il faut distinguer l'inventaire des objets de l'annuaire de l'inventaire technique réellement collecté sur les équipements.

### 16.2 Lister les ordinateurs d'une OU

```powershell
Import-Module ActiveDirectory

Get-ADComputer `
    -SearchBase "OU=Postes,OU=Ordinateurs,DC=ad,DC=lab,DC=test" `
    -Filter * `
    -Properties OperatingSystem,OperatingSystemVersion,LastLogonDate |
    Select-Object Name,
                  Enabled,
                  OperatingSystem,
                  OperatingSystemVersion,
                  LastLogonDate |
    Sort-Object Name
```

Ce rapport peut servir à examiner les objets ordinateur de l'OU, leurs propriétés disponibles et certaines informations de dernière activité.

Attention : `LastLogonDate` est une valeur construite à partir d'une propriété répliquée. Elle n'est pas équivalente à une mesure exacte et instantanée du dernier accès. Elle peut donc être utilisée comme indicateur, mais pas comme preuve suffisante pour supprimer ou désactiver un ordinateur sans vérifications supplémentaires.

### 16.3 Filtrer les ordinateurs désactivés

```powershell
Get-ADComputer `
    -Filter 'Enabled -eq $false' `
    -Properties OperatingSystem |
    Select-Object Name,
                  DistinguishedName,
                  OperatingSystem
```

Cela permet d'identifier les comptes ordinateur désactivés.

Pour déterminer pourquoi ils l'ont été ou s'ils doivent être supprimés, il faut consulter les procédures et les informations de l'organisation.

### 16.4 Identifier les ordinateurs dont l'activité semble ancienne

```powershell
$seuil = (Get-Date).AddDays(-90)

Get-ADComputer `
    -Filter * `
    -Properties LastLogonDate |
    Where-Object {
        $null -eq $_.LastLogonDate -or
        $_.LastLogonDate -lt $seuil
    } |
    Select-Object Name,
                  Enabled,
                  LastLogonDate,
                  DistinguishedName
```

Ce rapport produit une liste de candidats à vérifier.

Une date ancienne ne signifie pas nécessairement que le poste doit être supprimé. Il peut s'agir d'un équipement en congé prolongé, d'une machine de secours, d'un poste hors site ou d'un objet conservé pour une raison valable.

Il faut croiser les résultats avec l'inventaire matériel, les données de gestion et les informations des équipes responsables.

### 16.5 Collecter des informations techniques à distance

Exemple de collecte sur les postes pilotes :

```powershell
$ordinateurs = @("PC1", "PC2")

$inventaire = foreach ($ordinateur in $ordinateurs) {
    try {
        Invoke-Command `
            -ComputerName $ordinateur `
            -ScriptBlock {
                $os = Get-CimInstance Win32_OperatingSystem
                $ordinateur = Get-CimInstance Win32_ComputerSystem

                [PSCustomObject]@{
                    Nom             = $env:COMPUTERNAME
                    Fabricant       = $ordinateur.Manufacturer
                    Modele          = $ordinateur.Model
                    Systeme         = $os.Caption
                    Version         = $os.Version
                    MemoireTotaleGo = [math]::Round(
                        $ordinateur.TotalPhysicalMemory / 1GB, 2
                    )
                    DernierDemarrage = $os.LastBootUpTime
                }
            } `
            -ErrorAction Stop
    }
    catch {
        [PSCustomObject]@{
            Nom              = $ordinateur
            Fabricant        = $null
            Modele           = $null
            Systeme          = $null
            Version          = $null
            MemoireTotaleGo  = $null
            DernierDemarrage = $null
            Erreur           = $_.Exception.Message
        }
    }
}

$inventaire |
    Export-Csv `
        -Path "C:\Rapports\Inventaire-Postes.csv" `
        -NoTypeInformation `
        -Encoding UTF8
```

Le dossier `C:\Rapports` doit exister ; sinon, crée-le avant l'export.

Le script doit être testé sur un poste puis sur un petit groupe. Il faut tenir compte des erreurs de connexion, des droits disponibles et des différences de versions Windows.

### 16.6 Construire un inventaire de référence

Un fichier CSV est utile pour débuter, mais il faut rapidement définir des champs standardisés.

| Champ | Utilité |
|---|---|
| Nom du poste | Identifiant administratif |
| Service responsable | Affectation métier |
| Utilisateur principal | Suivi opérationnel selon la politique de confidentialité |
| Site physique | Support et réseau |
| Système et version | Compatibilité |
| Fabricant et modèle | Renouvellement du matériel |
| Dernier contrôle | Fraîcheur de l'information |
| État de conformité | Suivi sécurité |
| Responsable technique | Affectation de la maintenance |
| Statut de cycle de vie | Actif, à renouveler, retrait prévu |

L'inventaire doit être suffisamment régulier pour rester utile. Une extraction exécutée une seule fois ne constitue pas un système de gestion de parc durable.

## 17. Automatiser les opérations de gestion de parc

### 17.1 Pourquoi automatiser ?

L'automatisation permet de réduire les tâches répétitives, mais elle augmente aussi la portée d'une erreur.

Un script qui renomme un fichier peut toucher un seul poste. Un script exécuté sur une OU entière peut modifier des centaines de machines.

L'automatisation professionnelle implique donc :

- Un périmètre explicite.
- Une validation des paramètres.
- Une journalisation.
- Une gestion des erreurs.
- Une possibilité de tester sans modifier.
- Une exécution sous un compte suffisamment autorisé, mais pas excessivement privilégié.

### 17.2 Toujours prévoir une simulation

PowerShell propose `-WhatIf` pour de nombreuses opérations prises en charge.

Exemple :

```powershell
Move-ADObject `
    -Identity (Get-ADComputer -Identity "PC1").DistinguishedName `
    -TargetPath "OU=Pilotes,OU=Postes,OU=Ordinateurs,DC=ad,DC=lab,DC=test" `
    -WhatIf
```

Cela permet de vérifier l'opération envisagée.

Cependant, tous les cmdlets ne prennent pas en charge `-WhatIf`, et un script composite ne devient pas automatiquement sûr parce qu'une seule de ses commandes utilise cette option.

### 17.3 Écrire un journal de traitement

Un script de gestion doit rendre les résultats compréhensibles.

Exemple de journal simple :

```powershell
$journal = "C:\Rapports\Journal-Gestion.txt"

New-Item `
    -Path (Split-Path $journal) `
    -ItemType Directory `
    -Force | Out-Null

"[$(Get-Date -Format s)] Début du traitement" |
    Add-Content -Path $journal

try {
    $poste = Get-ADComputer -Identity "PC1" -ErrorAction Stop

    "[$(Get-Date -Format s)] Poste trouvé : $($poste.Name)" |
        Add-Content -Path $journal
}
catch {
    "[$(Get-Date -Format s)] ERREUR : $($_.Exception.Message)" |
        Add-Content -Path $journal
}

"[$(Get-Date -Format s)] Fin du traitement" |
    Add-Content -Path $journal
```

Dans un environnement de production, il faut définir la rotation, la conservation, les permissions et la centralisation éventuelle des journaux.

### 17.4 Ne jamais exécuter une opération destructive sans contrôle

Avant de supprimer des comptes ordinateur, de retirer des logiciels ou de déplacer de nombreux objets :

1. Produire un rapport préalable.
2. Vérifier la liste des objets concernés.
3. Faire approuver l'action lorsque la procédure l'exige.
4. Sauvegarder les données ou objets nécessaires.
5. Tester sur quelques objets.
6. Prévoir un retour arrière.
7. Enregistrer les résultats.

Une liste de candidats doit être examinée avant toute action irréversible.

## 18. Gestion des incidents liés aux GPO

### 18.1 Les symptômes courants

Un administrateur peut rencontrer les situations suivantes :

- Une GPO ne s'applique pas.
- Une partie de la GPO fonctionne mais pas l'autre.
- Un lecteur réseau n'apparaît pas.
- Une ancienne valeur reste présente.
- Un paramètre semble contradictoire.
- Une GPO apparaît dans la liste mais son paramètre est absent.
- La configuration fonctionne sur PC1, mais pas sur PC2.
- Une GPO fonctionne après redémarrage mais pas immédiatement.
- Un paramètre utilisateur dépend du poste de connexion.

La résolution de ces incidents doit suivre une méthode plutôt qu'une succession de modifications aléatoires.

### 18.2 Vérifier le résultat des stratégies

Sur le poste concerné, ouvrir un terminal avec les droits appropriés.

Pour les stratégies appliquées à l'utilisateur et à l'ordinateur :

```cmd
gpresult /r
```

Pour générer un rapport détaillé :

```cmd
gpresult /h C:\Temp\Resultat-GPO.html
```

Pour examiner spécifiquement les paramètres ordinateur :

```cmd
gpresult /scope computer /r
```

Pour examiner spécifiquement les paramètres utilisateur :

```cmd
gpresult /scope user /r
```

Si le dossier `C:\Temp` n'existe pas, il faut le créer avant l'export.

Le rapport aide à identifier les GPO appliquées, les stratégies non appliquées et les raisons de filtrage lorsqu'elles sont disponibles.

### 18.3 Vérifier que la GPO est dans le bon périmètre

Pose-toi les questions suivantes :

1. L'objet ordinateur se trouve-t-il dans l'OU attendue ?
2. Le compte utilisateur se trouve-t-il dans la bonne OU ?
3. La GPO est-elle liée au bon conteneur ?
4. La liaison est-elle activée ?
5. La partie ordinateur ou utilisateur est-elle activée ?
6. Le filtrage de sécurité autorise-t-il le principal correct ?
7. Le filtre WMI renvoie-t-il le résultat attendu ?
8. L'héritage est-il bloqué ?
9. Une liaison forcée influence-t-elle le traitement ?
10. Une autre GPO définit-elle une valeur contradictoire ?

Il faut analyser le résultat avant de modifier la GPO.

### 18.4 Vérifier la connectivité et le DNS

Une machine qui ne contacte pas correctement le domaine peut rencontrer des difficultés d'application des stratégies.

Depuis PC1 :

```cmd
ipconfig /all
```

Vérifie notamment :

- L'adresse IP.
- Le masque.
- La passerelle.
- Les serveurs DNS configurés.
- Le suffixe DNS.
- Les paramètres obtenus par DHCP si applicable.

Teste ensuite la résolution DNS :

```powershell
Resolve-DnsName DC1.ad.lab.test
```

Pour un poste membre d'un domaine Active Directory classique, le DNS utilisé doit pouvoir résoudre les enregistrements nécessaires au fonctionnement du domaine.

Une configuration DNS incohérente peut empêcher la localisation d'un contrôleur de domaine ou perturber les opérations d'annuaire.

### 18.5 Vérifier la localisation d'un contrôleur de domaine

La commande suivante peut aider à identifier un contrôleur de domaine accessible :

```cmd
nltest /dsgetdc:ad.lab.test
```

Si le poste ne trouve pas de contrôleur de domaine, il faut vérifier :

- La résolution DNS.
- La connectivité réseau.
- L'état des services nécessaires.
- La configuration du site Active Directory.
- L'état du contrôleur de domaine.
- L'heure du système.
- Les informations du domaine sur la machine.

### 18.6 Vérifier la réplication et SYSVOL

Les contrôleurs de domaine doivent disposer des informations AD nécessaires et d'un contenu SYSVOL cohérent.

Les deux mécanismes ne doivent pas être confondus :

- La réplication Active Directory réplique les données de l'annuaire.
- La réplication SYSVOL distribue notamment les fichiers des GPO.

Dans les environnements utilisant DFSR, les fichiers du dossier SYSVOL sont répliqués selon la topologie et l'état du service.

Une GPO peut exister dans l'annuaire tout en rencontrant un problème d'accès aux fichiers nécessaires à son traitement.

Les administrateurs doivent vérifier la santé de la réplication et des contrôleurs de domaine avec les outils d'administration adaptés.

### 18.7 Consulter les journaux d'événements

Les événements relatifs au traitement des stratégies sont disponibles dans les journaux Windows pertinents, notamment sous :

`Applications and Services Logs > Microsoft > Windows > GroupPolicy > Operational`

Les libellés affichés dépendent de la langue du système.

L'analyse des journaux peut aider à détecter les extensions clientes qui échouent, les problèmes de connectivité ou les erreurs rencontrées pendant l'application d'un paramètre.

### 18.8 Arbre de diagnostic

```text
Le paramètre attendu ne s'applique pas
                 |
                 v
       L'objet est-il dans la bonne OU ?
                 |
          +------+------+
          |             |
         Non           Oui
          |             |
   Corriger l'OU        v
                 La GPO est-elle applicable ?
                         |
                   +-----+-----+
                   |           |
                  Non         Oui
                   |           |
             Vérifier filtres  v
                        La stratégie apparaît-elle
                        dans gpresult ?
                               |
                         +-----+-----+
                         |           |
                        Non         Oui
                         |           |
                 Vérifier DNS,       v
                 AD, SYSVOL     Le paramètre est-il
                                défini dans la bonne
                                partie et compatible ?
                                      |
                                +-----+-----+
                                |           |
                               Non         Oui
                                |           |
                          Corriger la     Examiner les
                          configuration  conflits, journaux,
                                         version Windows
```

### 18.9 Bonnes pratiques de dépannage

Ne modifie pas simultanément l'OU, le filtrage, la liaison et plusieurs paramètres de la GPO pour résoudre un incident.

Procède par étapes :

1. Reproduire le problème.
2. Collecter les résultats de stratégie.
3. Vérifier l'identité et l'emplacement des objets.
4. Vérifier les permissions et les filtres.
5. Vérifier la connectivité et le DNS.
6. Consulter les journaux.
7. Modifier une variable à la fois.
8. Actualiser et tester.
9. Consigner la cause et le correctif.

Cette méthode facilite le diagnostic et évite de masquer le problème initial.

## 19. Les outils d'administration à connaître

### 19.1 GPMC

La console de gestion des stratégies de groupe permet de :

- Créer et modifier les GPO.
- Lier les GPO à des sites, domaines et OU.
- Gérer le filtrage.
- Examiner l'héritage.
- Générer certains rapports.
- Sauvegarder et restaurer les stratégies.

### 19.2 RSAT

Les outils d'administration de serveur distant, ou RSAT, permettent d'administrer différentes fonctions Windows Server depuis des machines administratives compatibles.

Ils peuvent inclure les outils Active Directory et les outils de stratégie de groupe.

L'installation et la disponibilité des composants dépendent de la version de Windows et du mode d'installation.

### 19.3 PowerShell

PowerShell apporte des capacités essentielles :

```text
ActiveDirectory
    |
    +-- Interroger les utilisateurs
    +-- Interroger les ordinateurs
    +-- Gérer certaines opérations AD
    +-- Déplacer des objets

GroupPolicy
    |
    +-- Lister les GPO
    +-- Générer des rapports
    +-- Sauvegarder les GPO
    +-- Restaurer les GPO
    +-- Déclencher une actualisation distante
```

Quelques commandes à mémoriser :

```powershell
Get-ADComputer
Get-ADUser
Get-ADGroup
Move-ADObject

Get-GPO
Get-GPOReport
Backup-GPO
Restore-GPO
Invoke-GPUpdate
```

Les commandes disponibles dépendent des modules installés et des permissions du compte.

### 19.4 Windows Admin Center

Windows Admin Center fournit une interface d'administration à distance centrée sur la gestion des serveurs Windows et de certains environnements associés.

Il complète les outils MMC et PowerShell.

Il ne remplace pas automatiquement la gestion des stratégies de groupe, ni une solution complète de gestion des terminaux utilisateur.

Documentation : [Vue d'ensemble de Windows Admin Center](https://learn.microsoft.com/en-us/windows-server/manage/windows-admin-center/overview).

## 20. Travaux pratiques guidés

### TP 1 — Construire une OU de postes pilotes

**Objectif :** créer un périmètre de test qui ne touche pas tout le parc.

Prérequis :

- Un domaine `ad.lab.test`.
- Un contrôleur de domaine opérationnel.
- Des droits de gestion Active Directory.

Étapes :

1. Ouvrir `dsa.msc`.
2. Créer ou vérifier l'OU `Ordinateurs`.
3. Créer l'OU `Postes`.
4. Créer l'OU `Pilotes` dans `Postes`.
5. Vérifier les comptes des machines de laboratoire.
6. Déplacer PC1 et PC2 dans l'OU Pilotes.
7. Vérifier leur emplacement avec PowerShell.
8. Examiner les GPO héritées.

Commande de vérification :

```powershell
Get-ADComputer `
    -SearchBase "OU=Pilotes,OU=Postes,OU=Ordinateurs,DC=ad,DC=lab,DC=test" `
    -Filter * |
    Select-Object Name, DistinguishedName
```

Résultat attendu : PC1 et PC2 apparaissent dans l'OU prévue, avec leurs noms distinctifs.

### TP 2 — Créer une GPO de test

**Objectif :** comprendre le cycle complet de création, liaison, actualisation et vérification.

1. Ouvrir la console de gestion des stratégies de groupe.
2. Créer `GPO-LAB-Postes`.
3. Lier la stratégie à l'OU Pilotes.
4. Configurer un paramètre non critique adapté à tes machines de laboratoire.
5. Actualiser les stratégies sur PC1.
6. Vérifier le résultat avec `gpresult /r`.
7. Produire un rapport HTML.
8. Relever le résultat avant et après la modification.

Le paramètre de test doit être choisi de manière à ne pas compromettre l'accès à la machine.

### TP 3 — Appliquer une stratégie à un groupe de machines

**Objectif :** maîtriser le filtrage de sécurité.

1. Créer le groupe `GG_Postes_Pilotes`.
2. Ajouter PC1 et PC2 au groupe.
3. Créer `GPO-Pilote-Test`.
4. Lier la GPO au bon conteneur.
5. Configurer le filtrage de sécurité.
6. Vérifier les permissions de lecture et d'application.
7. Actualiser la stratégie sur PC1 et PC2.
8. Vérifier le résultat.
9. Comparer avec un ordinateur qui n'est pas dans le groupe.

Résultat attendu : les machines autorisées reçoivent la stratégie, les autres ne l'appliquent pas dans les mêmes conditions.

### TP 4 — Créer un lecteur réseau pour la comptabilité

**Objectif :** utiliser les préférences de stratégie de groupe.

Prérequis : un partage `\\FILE1\Comptabilite` fonctionnel.

1. Créer une GPO utilisateur.
2. Configurer une préférence de mappage du lecteur `S:`.
3. Cibler les utilisateurs de la comptabilité.
4. Vérifier les permissions du partage et du dossier.
5. Ouvrir une session avec un compte de test.
6. Actualiser les stratégies.
7. Vérifier la présence du lecteur.
8. Tester l'accès aux fichiers.
9. Vérifier le comportement si l'utilisateur n'appartient pas au groupe.

### TP 5 — Sauvegarder puis restaurer une GPO

**Objectif :** vérifier la procédure de retour arrière.

1. Choisir une GPO de laboratoire.
2. Créer un dossier de sauvegarde protégé.
3. Exécuter `Backup-GPO`.
4. Vérifier le résultat.
5. Modifier un paramètre non critique sur la GPO.
6. Tester la restauration de la sauvegarde sur une stratégie de laboratoire appropriée.
7. Contrôler les paramètres restaurés.
8. Documenter le résultat.

Ne réalise pas ce TP sur une GPO de production sans procédure approuvée et sans avoir vérifié les conséquences.

### TP 6 — Générer un inventaire de parc

**Objectif :** obtenir une vision claire des postes de l'OU pilote.

1. Interroger Active Directory.
2. Exporter les propriétés disponibles.
3. Collecter les informations système des postes accessibles.
4. Distinguer les résultats valides des erreurs de connexion.
5. Exporter le rapport au format CSV.
6. Vérifier quelques lignes en ouvrant le fichier.
7. Identifier les données manquantes.
8. Proposer un mécanisme de mise à jour périodique.

Résultat attendu : un inventaire exploitable, accompagné d'un état des erreurs de collecte.

## 21. Exercices d'application avec corrigés

### Exercice 1 — Comprendre l'héritage

Une GPO au niveau du domaine définit le délai de verrouillage à 15 minutes. Une GPO liée à une OU enfant définit le délai à 10 minutes.

**Question :** quelle valeur est généralement appliquée à une machine située dans l'OU enfant ?

**Corrigé :** généralement 10 minutes, car la GPO de l'OU enfant est traitée après la GPO du domaine. Il faut toutefois vérifier le résultat effectif, le ciblage et les éventuels mécanismes particuliers.

### Exercice 2 — Mauvais objet dans le groupe

Une GPO de configuration du pare-feu est filtrée sur `GG_Postes_Pilotes`. L'administrateur ajoute le compte `adiallo`, mais PC1 ne reçoit pas la stratégie.

**Question :** quelle est l'erreur la plus probable ?

**Corrigé :** pour les paramètres ordinateur, le filtrage doit viser les comptes ordinateurs concernés, dans ce cas PC1 et les machines pilotes. L'appartenance de l'utilisateur ne remplace pas celle de l'ordinateur.

### Exercice 3 — Le lecteur réseau ne se mappe pas

Le rapport de stratégie indique que la GPO utilisateur est appliquée, mais le lecteur `S:` n'apparaît pas.

**Question :** que faut-il examiner ?

**Corrigé :**

- Le paramètre de préférence et son action.
- Le ciblage au niveau de l'élément.
- L'existence du partage.
- La résolution DNS du serveur de fichiers.
- Les permissions.
- Le contexte de connexion de l'utilisateur.
- Les journaux de traitement des préférences.
- Une éventuelle lettre de lecteur déjà utilisée.

### Exercice 4 — Une GPO ne s'applique pas à PC2

PC1 reçoit correctement une GPO liée à l'OU Pilotes, mais PC2 ne la reçoit pas.

**Question :** quelles vérifications effectuer dans l'ordre ?

**Corrigé :**

1. Vérifier l'OU de PC2.
2. Vérifier le compte ordinateur et le filtrage de sécurité.
3. Vérifier les permissions de lecture et d'application.
4. Examiner le filtre WMI.
5. Vérifier les liaisons et l'héritage.
6. Contrôler le résultat avec `gpresult`.
7. Vérifier le DNS et l'accès au domaine.
8. Examiner les journaux de stratégie de groupe.

### Exercice 5 — Mises à jour progressives

L'entreprise veut tester les mises à jour sur cinq postes avant de les déployer sur 200 postes.

**Question :** quelle méthode recommander ?

**Corrigé :** créer un anneau pilote, sélectionner les postes concernés, définir les critères de validation, contrôler les résultats, puis étendre progressivement le déploiement. La méthode exacte dépend du système de mise à jour retenu et des capacités de gestion disponibles.

### Exercice 6 — Inventaire obsolète

Un objet ordinateur affiche une activité datant de 120 jours.

**Question :** faut-il le supprimer immédiatement ?

**Corrigé :** non. La date peut être un indicateur de faible activité, mais elle ne prouve pas que le poste n'existe plus. Il faut vérifier le matériel, l'utilisateur ou le responsable, l'inventaire, le statut de l'équipement et les procédures de retrait.

### Exercice 7 — Choisir entre stratégie et préférence

L'administrateur veut distribuer un raccourci vers une documentation interne.

**Question :** quel mécanisme convient généralement ?

**Corrigé :** une préférence de stratégie de groupe pour les raccourcis constitue généralement un choix adapté. Il faut néanmoins déterminer si le raccourci doit être réappliqué, supprimé lorsqu'il n'est plus dans le périmètre ou laissé à l'utilisateur selon le besoin.

### Exercice 8 — Une GPO a provoqué un incident

Après une modification, plusieurs postes n'appliquent plus les paramètres attendus.

**Question :** quelle est la première démarche ?

**Corrigé :** arrêter la généralisation, analyser le changement, consulter les rapports et journaux, sauvegarder les preuves utiles et revenir à une configuration connue si nécessaire. La restauration doit être faite selon une procédure contrôlée, puis validée sur les postes touchés.

## 22. Projet pratique de synthèse

### Contexte

Une petite entreprise utilise le domaine `ad.lab.test` et possède 30 postes Windows.

Elle veut professionnaliser l'administration de son parc.

Les objectifs sont :

- Standardiser les postes.
- Séparer les postes pilotes de la production.
- Appliquer les règles de sécurité de base.
- Distribuer les lecteurs réseau selon les services.
- Organiser les mises à jour.
- Produire un inventaire.
- Sauvegarder les GPO.
- Définir un processus de validation avant généralisation.

### Architecture cible

```text
ad.lab.test
|
+-- OU=Utilisateurs
|   |
|   +-- OU=Comptabilite
|   +-- OU=Commercial
|   +-- OU=Support
|
+-- OU=Ordinateurs
|   |
|   +-- OU=Postes
|   |   |
|   |   +-- OU=Pilotes
|   |   +-- OU=Production
|   |
|   +-- OU=Serveurs-Membres
|
+-- OU=Groupes
    |
    +-- GG_Postes_Pilotes
    +-- GG_Comptabilite
    +-- GG_Admin_Parc
```

### Partie A — Organiser Active Directory

Créer les OU nécessaires, vérifier l'existence des objets et placer les postes pilotes dans leur périmètre.

Documenter le rôle de chaque OU.

### Partie B — Concevoir les GPO

Préparer les stratégies suivantes :

```text
GPO-SEC-Base-Postes
GPO-SEC-PareFeu-Postes
GPO-UPD-Pilote-Windows
GPO-UPD-Production-Windows
GPO-USER-Lecteur-Comptabilite
```

Pour chaque GPO, noter le type de paramètres, le périmètre, les filtres et la procédure de validation.

### Partie C — Tester les stratégies

Sur PC1 et PC2 :

1. Actualiser les stratégies.
2. Générer un rapport de stratégie résultante.
3. Vérifier le paramètre de sécurité choisi.
4. Vérifier le lecteur réseau si l'utilisateur de test appartient au bon groupe.
5. Examiner les journaux d'événements.
6. Consigner les éventuelles erreurs.

### Partie D — Inventorier les équipements

Produire un CSV contenant les machines connues, les propriétés Active Directory disponibles et, lorsque la connexion le permet, des informations techniques collectées à distance.

Les machines injoignables doivent être identifiées explicitement plutôt que supprimées du rapport.

### Partie E — Organiser le changement

Rédiger une procédure décrivant :

- La sauvegarde préalable.
- Le déploiement pilote.
- Les critères de réussite.
- Le passage en production.
- La vérification.
- Le retour arrière.

### Livrables attendus

Le projet doit se conclure avec :

- Une architecture d'OU documentée.
- Une liste des GPO et de leur périmètre.
- Des rapports de stratégie résultante.
- Un rapport d'inventaire.
- Une sauvegarde des GPO de laboratoire.
- Une procédure d'exploitation.
- Un bilan des tests et des incidents.

Le projet est réussi lorsque les résultats observés correspondent aux objectifs définis et que les opérations peuvent être répétées sans improvisation.

## 23. Défi final — Industrialiser un parc Windows

Une entreprise compte 120 postes Windows répartis entre la comptabilité, le service commercial, le support informatique et la direction.

Elle veut appliquer une politique commune de sécurité, tester les mises à jour sur un groupe pilote, déployer des lecteurs réseau selon le service, contrôler les postes inactifs depuis plusieurs mois et produire un inventaire automatisé.

Tu dois proposer une architecture complète qui répond à ces besoins.

Ton travail doit comporter :

1. Une arborescence d'OU justifiée.
2. Une convention de nommage des GPO.
3. Une stratégie de filtrage de sécurité.
4. Une séparation entre paramètres ordinateur et paramètres utilisateur.
5. Un processus de sauvegarde et de restauration.
6. Une stratégie d'anneaux de mise à jour.
7. Une méthode de déploiement des lecteurs réseau.
8. Une collecte d'inventaire en lecture seule.
9. Une méthode de détection des postes dont l'activité paraît ancienne.
10. Un processus de validation avant suppression ou déplacement d'un objet.
11. Une procédure de diagnostic.
12. Une politique de documentation des changements.

### Critères de réussite

Le travail est validé si :

- Les GPO ont un périmètre compréhensible.
- Les groupes utilisés ciblent les bons objets.
- Les changements sont testés avant leur généralisation.
- Les postes de production ne sont pas utilisés comme premier terrain d'essai.
- L'inventaire distingue les informations connues des erreurs de collecte.
- Les objets inactifs ne sont pas supprimés uniquement sur la base d'une date.
- Les opérations administratives sont journalisées.
- Une restauration contrôlée est possible.
- Les procédures peuvent être reprises par un autre administrateur.

## 24. Bonnes pratiques à retenir

### Architecture

- Sépare les OU des utilisateurs et des ordinateurs lorsque cela facilite la gestion.
- Évite la duplication inutile des GPO.
- Utilise des noms explicites et documentés.
- N'utilise pas le blocage de l'héritage sans raison technique claire.
- Réserve le traitement en boucle aux postes ayant un usage particulier.

### Sécurité

- Applique le principe du moindre privilège.
- Limite l'usage des comptes Domain Admin.
- Ne stocke pas de secrets en clair dans les GPO ou les scripts.
- Utilise Windows LAPS pour les mots de passe administrateur locaux lorsque le scénario est adapté.
- Vérifie la récupération des clés de chiffrement.
- Teste les bases de référence de sécurité.

### Déploiement

- Commence par un petit groupe pilote.
- Sauvegarde avant les modifications importantes.
- Prévois un retour arrière.
- Vérifie le résultat réel sur les postes.
- Évite d'envoyer simultanément des opérations lourdes à tout le parc sans mesurer les conséquences.

### Automatisation

- Définis le périmètre avant l'exécution.
- Utilise `-WhatIf` lorsque le cmdlet le prend en charge.
- Journalise les résultats.
- Traite les erreurs.
- Ne confonds pas l'envoi d'une commande avec la réussite de son résultat.
- Examine les rapports avant les opérations destructives.

### Dépannage

- Commence par `gpresult`.
- Vérifie l'OU, les liaisons et les filtres.
- Vérifie le DNS et l'accès au domaine.
- Examine les journaux de stratégie de groupe.
- Modifie une variable à la fois.
- Documente la cause et la résolution.

## 25. Fiche de révision rapide

| Besoin | Outil ou mécanisme |
|---|---|
| Modifier les stratégies | GPMC |
| Organiser les utilisateurs et ordinateurs | Active Directory |
| Définir le périmètre des stratégies | OU, liaison et filtrage |
| Cibler un groupe de machines | Groupe de sécurité contenant les comptes ordinateurs |
| Cibler les paramètres utilisateur | Groupe de sécurité contenant les utilisateurs concernés |
| Actualiser les GPO localement | `gpupdate` |
| Obtenir le détail des stratégies appliquées | `gpresult /h C:\Temp\Resultat-GPO.html` |
| Actualiser à distance | `Invoke-GPUpdate` |
| Inventorier les objets ordinateur | `Get-ADComputer` |
| Déplacer un objet AD | `Move-ADObject` |
| Lister les GPO | `Get-GPO -All` |
| Produire un rapport de GPO | `Get-GPOReport` |
| Sauvegarder toutes les GPO | `Backup-GPO -All` |
| Restaurer une sauvegarde de GPO | `Restore-GPO` |
| Collecter des informations système à distance | PowerShell Remoting et CIM |
| Configurer des lecteurs réseau | Préférences de stratégie de groupe |
| Déployer certains packages MSI | Installation de logiciels par GPO |
| Contrôler des mises à jour via un serveur interne | WSUS, si cette architecture est retenue |
| Gérer les secrets administrateur locaux | Windows LAPS |
| Administrer des serveurs à distance | Windows Admin Center et PowerShell selon le besoin |

## 26. Glossaire

**AD — Active Directory :** service d'annuaire qui organise les identités et les objets d'un domaine.

**OU — Organizational Unit :** unité d'organisation utilisée pour regrouper des objets et structurer l'administration.

**GPO — Group Policy Object :** objet contenant des paramètres de stratégie de groupe.

**GPMC :** console de gestion des stratégies de groupe.

**LSDOU :** ordre standard de traitement : Local, Site, Domaine, OU.

**Héritage :** mécanisme par lequel les stratégies liées à des conteneurs parents peuvent s'appliquer aux objets des conteneurs enfants.

**Liaison :** association d'une GPO à un site, un domaine ou une OU.

**Filtrage de sécurité :** contrôle de l'application d'une GPO selon les permissions du principal concerné.

**Filtre WMI :** condition fondée sur les caractéristiques du système cible.

**Loopback :** mode de traitement permettant de contrôler les stratégies utilisateur en fonction de l'ordinateur sur lequel l'utilisateur se connecte.

**Préférence de stratégie :** configuration déployée par une GPO, souvent destinée à configurer des éléments que l'utilisateur peut modifier.

**ADMX / ADML :** fichiers décrivant les modèles administratifs et leurs libellés localisés.

**SYSVOL :** partage présent sur les contrôleurs de domaine qui contient notamment les fichiers des stratégies de groupe.

**RSOP :** *Resultant Set of Policy*, ou jeu de stratégies résultant.

**WSUS :** service Windows Server permettant de gérer certaines mises à jour.

**LAPS :** solution de gestion des mots de passe administrateur locaux.

**PowerShell Remoting :** mécanisme permettant d'exécuter des commandes PowerShell à distance selon la configuration et les autorisations prévues.

**Inventaire de parc :** ensemble structuré des informations sur les équipements, leurs caractéristiques et leur état.

**Anneau de déploiement :** groupe de machines auquel une mise à jour est destinée à être appliquée à une étape du déploiement.

## 27. Documentation officielle

Pour approfondir les notions de ce cours, privilégie la documentation Microsoft Learn.

### Stratégies de groupe

- [Vue d'ensemble des stratégies de groupe](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview)
- [Traitement des stratégies de groupe](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-processing)
- [Portée des stratégies de groupe](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-scope)
- [Préférences de stratégie de groupe](https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-preferences)

### Commandes et administration PowerShell

- [`gpupdate`](https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/gpupdate)
- [`gpresult`](https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/gpresult)
- [`Backup-GPO`](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/backup-gpo)
- [`Invoke-GPUpdate`](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/invoke-gpupdate)
- [`Move-ADObject`](https://learn.microsoft.com/en-us/powershell/module/activedirectory/move-adobject)
- [`msiexec`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/msiexec)

### Sécurité et exploitation

- [Vue d'ensemble de Windows LAPS](https://learn.microsoft.com/fr-fr/windows-server/identity/laps/laps-overview)
- [Microsoft Security Compliance Toolkit](https://learn.microsoft.com/windows/security/operating-system-security/device-management/windows-security-configuration-framework/security-compliance-toolkit-10)
- [Déploiement des mises à jour Windows avec WSUS](https://learn.microsoft.com/fr-fr/windows/deployment/update/waas-manage-updates-wsus)
- [Vue d'ensemble de Windows Admin Center](https://learn.microsoft.com/en-us/windows-server/manage/windows-admin-center/overview)

## Conclusion

La gestion de parc Windows ne consiste pas simplement à créer quelques GPO et à les associer à une OU. Une administration efficace repose sur une architecture Active Directory cohérente, un ciblage précis, des paramètres de sécurité adaptés, des tests systématiques, un inventaire exploitable et des procédures d'exploitation reproductibles.

Le niveau intermédiaire demande surtout de passer d'une logique de configuration individuelle à une logique de **gestion contrôlée d'un ensemble de machines**.

La priorité n'est pas de déployer le plus grand nombre de stratégies possible, mais de garantir que chaque stratégie a un objectif clair, qu'elle s'applique aux bons équipements, que son effet est vérifié et que l'administrateur peut corriger ou annuler un changement sans mettre en danger le reste du parc.