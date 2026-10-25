# Windows Server : bases et Active Directory

## 1. Introduction à Windows Server

Windows Server est un système d'exploitation conçu pour héberger des services et des ressources destinés à plusieurs utilisateurs ou ordinateurs dans un réseau.

Contrairement à un poste Windows utilisé principalement pour les applications bureautiques, un serveur Windows fournit généralement des services centralisés : authentification, résolution de noms, gestion des utilisateurs, partage de fichiers, hébergement d'applications ou administration des postes de travail.

Dans une entreprise, Windows Server peut notamment permettre de :

- centraliser les comptes des collaborateurs ;
- gérer les ordinateurs d'un réseau ;
- authentifier les utilisateurs ;
- appliquer des règles de sécurité ;
- fournir des services DNS ;
- distribuer des adresses IP grâce à DHCP ;
- partager des fichiers et des imprimantes ;
- administrer les accès aux ressources ;
- héberger certaines applications ;
- organiser les politiques de configuration des postes.

Ce cours présente les bases de Windows Server, puis se concentre sur Active Directory Domain Services, le service d'annuaire couramment utilisé dans les environnements Windows d'entreprise.

### 1.1 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- expliquer le rôle d'un serveur Windows ;
- distinguer un serveur autonome d'un contrôleur de domaine ;
- comprendre les rôles, fonctionnalités et services Windows Server ;
- effectuer les premiers réglages d'un serveur ;
- configurer une adresse IP statique ;
- comprendre le fonctionnement d'Active Directory ;
- différencier une forêt, un domaine, un contrôleur de domaine et une unité d'organisation ;
- comprendre pourquoi DNS est essentiel à Active Directory ;
- installer le rôle AD DS ;
- promouvoir un serveur en contrôleur de domaine ;
- créer des utilisateurs, des groupes et des unités d'organisation ;
- joindre un poste client compatible à un domaine ;
- comprendre les stratégies de groupe, ou GPO ;
- appliquer les premières règles de sécurité ;
- utiliser les commandes PowerShell de diagnostic ;
- résoudre les problèmes élémentaires d'authentification et de résolution DNS ;
- comprendre les premières notions de sauvegarde et de récupération d'Active Directory.

### 1.2 Prérequis

Vous devez connaître quelques notions élémentaires :

- ce qu'est une adresse IP ;
- le rôle d'un masque de sous-réseau ;
- la différence entre une adresse IP et un nom DNS ;
- le fonctionnement général d'un réseau local ;
- l'utilisation de base de Windows ;
- quelques commandes du terminal.

Les notions propres à Windows Server et à Active Directory sont expliquées progressivement.

### 1.3 Environnement conseillé

Pour apprendre, privilégiez des machines virtuelles plutôt qu'un serveur utilisé par une entreprise.

Laboratoire de référence :

```text
                 RÉSEAU DE FORMATION
                     192.168.10.0/24
                            |
                +-----------+-----------+
                |                       |
                v                       v
        +---------------+       +---------------+
        | DC1           |       | PC1           |
        | Windows Server|       | Windows 11 Pro|
        |               |       |               |
        | AD DS         |       | Client du     |
        | DNS           |       | domaine       |
        |               |       |               |
        | 192.168.10.10 |       | 192.168.10.20 |
        +---------------+       +---------------+
                |
                v
       Domaine : ad.lab.test
```

Les adresses IP sont des exemples destinés au laboratoire. Le réseau `192.168.10.0/24` est un exemple de réseau privé : vérifiez qu'il ne chevauche pas le réseau utilisé par vos autres équipements.

Le nom `ad.lab.test` est réservé ici à la formation. Pour une infrastructure réelle, choisissez un espace de noms DNS cohérent avec l'environnement de l'organisation.

Le laboratoire repose sur un seul contrôleur de domaine. Il convient à l'apprentissage, mais ne constitue pas une architecture hautement disponible.

## 2. Comprendre les rôles de Windows Server

### 2.1 Qu'est-ce qu'un rôle serveur ?

Un rôle serveur correspond à une fonction principale assurée par la machine.

Par exemple :

| Rôle | Fonction |
|---|---|
| AD DS | Annuaire, authentification et organisation des objets de domaine |
| DNS Server | Résolution des noms |
| DHCP Server | Attribution automatique des paramètres IP |
| File and Storage Services | Partage et gestion du stockage |
| Hyper-V | Virtualisation |
| Web Server (IIS) | Hébergement de sites Web et d'applications compatibles |
| Remote Desktop Services | Publication de bureaux ou d'applications distants, selon la configuration |

Une machine peut héberger plusieurs rôles, mais chaque rôle doit être justifié par les besoins de l'infrastructure.

Sur une architecture importante, il est préférable d'éviter d'ajouter des services inutiles sur les contrôleurs de domaine.

### 2.2 Rôle, fonctionnalité et service Windows

Ces notions sont différentes.

**Rôle serveur :** fonction principale fournie à d'autres équipements ou utilisateurs.

**Fonctionnalité :** composant qui ajoute une capacité au système ou prend en charge un rôle.

**Service Windows :** processus d'arrière-plan géré par le système, souvent démarré automatiquement selon sa configuration.

Exemple :

```text
Windows Server
      |
      +-- Rôle AD DS
      |      |
      |      +-- Active Directory
      |      +-- Authentification du domaine
      |
      +-- Rôle DNS
      |      |
      |      +-- Service de résolution DNS
      |
      +-- Services Windows
             |
             +-- Services d'arrière-plan
```

L'installation d'un rôle peut installer plusieurs composants et services nécessaires à son fonctionnement.

### 2.3 Serveur autonome et contrôleur de domaine

Un serveur autonome appartient à un environnement dans lequel il ne fournit pas nécessairement l'authentification d'un domaine Active Directory.

Il peut disposer de comptes locaux et de ses propres paramètres.

Un contrôleur de domaine, en revanche, héberge une copie de l'annuaire Active Directory du domaine et participe aux mécanismes d'authentification et de gestion des objets.

```text
SERVEUR AUTONOME

Windows Server
    |
    +-- Comptes locaux
    |
    +-- Groupes locaux
    |
    +-- Ressources propres à la machine
```

```text
CONTRÔLEUR DE DOMAINE

Windows Server
    |
    +-- Active Directory
    |
    +-- Comptes du domaine
    |
    +-- Groupes du domaine
    |
    +-- Authentification centralisée
    |
    +-- Stratégies et ressources du domaine
```

Le passage d'un serveur autonome à un contrôleur de domaine implique une opération de promotion après l'installation du rôle AD DS.

## 3. Server Core et Desktop Experience

Windows Server peut être déployé selon différentes options d'installation, notamment Server Core et Server avec Expérience utilisateur.

### 3.1 Server avec Expérience utilisateur

Cette option comprend une interface graphique traditionnelle.

Elle convient notamment :

- à l'apprentissage initial ;
- aux administrateurs qui utilisent régulièrement le Gestionnaire de serveur ;
- aux environnements où des outils graphiques locaux sont utiles.

### 3.2 Server Core

Server Core est une option d'installation minimale, sans bureau graphique traditionnel.

L'administration se réalise principalement avec :

- Windows PowerShell ;
- les outils en ligne de commande ;
- les outils d'administration à distance ;
- Windows Admin Center ou les outils RSAT, selon les besoins.

Server Core réduit l'empreinte du système et la surface d'attaque associée aux composants qui ne sont pas installés. Il n'est cependant pas dépourvu de services ou de fonctions d'administration.

### 3.3 Quel choix pour débuter ?

Pour ce cours, privilégiez une installation de Windows Server avec Expérience utilisateur afin de suivre les étapes graphiques.

Vous utiliserez également PowerShell, car l'automatisation fait partie des compétences importantes pour administrer Windows Server.

Documentation Microsoft :

https://learn.microsoft.com/fr-fr/windows-server/administration/server-core/what-is-server-core

## 4. Installer Windows Server et préparer le serveur

### 4.1 Choisir un environnement adapté

Vous pouvez utiliser une machine physique ou une machine virtuelle.

Pour le laboratoire, une VM présente plusieurs avantages :

- elle permet de recommencer l'installation ;
- elle facilite la création de points de contrôle de formation ;
- elle permet d'isoler les tests ;
- elle évite d'utiliser directement un réseau de production.

Les ressources nécessaires dépendent de la version de Windows Server, des composants installés et de la charge du laboratoire. Pour une installation de formation, attribuez suffisamment de mémoire et de stockage pour que le système et les rôles fonctionnent confortablement.

### 4.2 Installation initiale

Après l'installation de Windows Server :

1. définissez un mot de passe administrateur local robuste ;
2. vérifiez la date, l'heure et le fuseau horaire ;
3. installez les mises à jour prévues ;
4. vérifiez la carte réseau ;
5. attribuez un nom à la machine ;
6. configurez une adresse IP adaptée au réseau ;
7. contrôlez les paramètres du pare-feu ;
8. préparez l'installation des rôles nécessaires.

Dans une infrastructure de production, les modifications doivent suivre les procédures de changement de l'organisation.

### 4.3 Renommer le serveur

Le serveur du laboratoire portera le nom `DC1`.

Ouvrez PowerShell en tant qu'administrateur :

```powershell
Rename-Computer -NewName "DC1" -Restart
```

Cette commande renomme l'ordinateur et demande son redémarrage.

Effectuez ce changement avant de promouvoir le serveur en contrôleur de domaine.

Après redémarrage, vérifiez le nom :

```powershell
$env:COMPUTERNAME
```

Résultat attendu :

```text
DC1
```

Le nom d'une machine doit respecter les contraintes applicables aux noms Windows et DNS. Utilisez un nom simple, clair et documenté.

## 5. Configurer l'adresse IP du serveur

Un contrôleur de domaine doit être accessible à une adresse prévisible dans le réseau.

Dans le laboratoire, nous utiliserons :

| Paramètre | Valeur d'exemple |
|---|---|
| Adresse IPv4 | `192.168.10.10` |
| Masque | `255.255.255.0` |
| Préfixe | `/24` |
| Passerelle | Selon le réseau du laboratoire |
| DNS préféré | `192.168.10.10`, une fois le service DNS opérationnel |

La passerelle dépend du réseau utilisé. Dans un laboratoire strictement isolé, elle peut être absente si aucune communication externe n'est nécessaire.

### 5.1 Configuration avec l'interface graphique

Dans Windows Server avec Expérience utilisateur :

1. ouvrez les paramètres réseau ;
2. accédez aux paramètres des cartes réseau ;
3. identifiez l'interface connectée au réseau du laboratoire ;
4. ouvrez ses propriétés ;
5. sélectionnez IPv4 ;
6. définissez l'adresse et le masque ;
7. définissez la passerelle si elle est nécessaire ;
8. configurez le DNS selon la topologie ;
9. validez les modifications.

Vérifiez l'adaptateur avant de modifier ses paramètres, particulièrement lorsque vous êtes connecté à distance.

### 5.2 Vérifier l'adresse

Dans PowerShell :

```powershell
Get-NetIPConfiguration
```

Pour afficher les cartes réseau :

```powershell
Get-NetAdapter
```

Pour afficher les adresses IPv4 :

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

Vérifiez que l'adresse prévue est affectée à la bonne interface et qu'aucune adresse concurrente ne l'utilise.

### 5.3 Pourquoi utiliser une adresse stable ?

Un contrôleur de domaine doit pouvoir être localisé par les clients. Si son adresse change sans mise à jour appropriée des paramètres réseau et DNS, certains clients peuvent ne plus le trouver correctement.

L'adresse statique ou une réservation correctement organisée évite certaines difficultés d'adressage.

Pour le laboratoire, une configuration IPv4 statique est une manière simple de maîtriser les paramètres.

## 6. Comprendre Active Directory

Active Directory Domain Services, généralement abrégé **AD DS**, est un service d'annuaire Microsoft.

Il stocke des informations relatives aux objets d'un réseau et fournit les mécanismes permettant aux utilisateurs et aux administrateurs de retrouver ces objets et de leur appliquer les autorisations appropriées.

Ces objets peuvent inclure :

- des comptes utilisateurs ;
- des comptes d'ordinateurs ;
- des groupes ;
- des unités d'organisation ;
- des objets liés à des ressources ;
- des informations nécessaires aux mécanismes de sécurité.

### 6.1 Le problème que résout Active Directory

Sans annuaire centralisé, une organisation peut devoir créer séparément des comptes sur chaque machine.

```text
SANS ANNuaire CENTRALISÉ

PC1                   PC2                   PC3
 |                     |                     |
 +-- Compte A          +-- Compte A          +-- Compte A
 |
 +-- Gestion locale    +-- Gestion locale    +-- Gestion locale
```

Cela complique la gestion des mots de passe, des départs, des arrivées et des droits.

Avec Active Directory, les comptes et une partie des règles peuvent être gérés centralement.

```text
AVEC ACTIVE DIRECTORY

                +-------------------+
                | Active Directory  |
                | Comptes / Groupes |
                +---------+---------+
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
         PC1             PC2             PC3
          |               |               |
          +---------------+---------------+
                          |
                          v
                Authentification du domaine
```

Les utilisateurs peuvent utiliser leur identité de domaine pour accéder aux ressources auxquelles ils sont autorisés.

Cela ne signifie pas que tous les droits sont accordés à tous les utilisateurs. Les autorisations restent définies selon les ressources et les règles de sécurité.

### 6.2 Annuaire et authentification

L'annuaire stocke des informations sur les objets. Les contrôleurs de domaine assurent différents services liés à l'authentification et à l'autorisation.

Dans une architecture de domaine classique :

- Kerberos est un protocole central d'authentification ;
- LDAP est utilisé pour accéder à des informations de l'annuaire selon les autorisations ;
- DNS permet de localiser les services du domaine ;
- les stratégies de groupe configurent de nombreux paramètres des utilisateurs et ordinateurs.

Ces composants collaborent, mais ils n'ont pas le même rôle.

### 6.3 Active Directory et comptes Microsoft personnels

Un compte Microsoft personnel et un compte utilisateur Active Directory d'entreprise sont deux identités différentes.

Un ordinateur peut utiliser divers mécanismes d'identité, mais rejoindre un domaine AD DS classique nécessite un système client et une configuration compatibles.

Dans ce cours, l'objectif est de construire un domaine Active Directory traditionnel.

Documentation officielle :

https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/active-directory-domain-services

## 7. Comprendre la forêt, le domaine et le contrôleur de domaine

Les notions de forêt, de domaine et de contrôleur de domaine structurent Active Directory.

### 7.1 Le domaine

Un domaine Active Directory constitue une unité logique d'administration et de réplication des objets de domaine.

Dans notre laboratoire :

```text
Domaine DNS : ad.lab.test
Nom NetBIOS : LAB
```

Le domaine fournit un espace dans lequel on organise les comptes, les groupes, les ordinateurs et les autres objets du domaine.

### 7.2 Le contrôleur de domaine

Un contrôleur de domaine, ou DC (*Domain Controller*), héberge une copie de l'annuaire Active Directory pour son domaine.

Il participe aux mécanismes d'authentification, de recherche des objets et, dans une architecture à plusieurs contrôleurs de domaine, à la réplication de l'annuaire.

Dans notre laboratoire, le serveur `DC1` deviendra le premier contrôleur de domaine de la forêt.

### 7.3 La forêt

Une forêt est la structure logique de plus haut niveau d'un environnement Active Directory classique.

Elle contient un ou plusieurs domaines qui partagent notamment un schéma et des informations de configuration selon l'architecture AD DS.

Dans une petite entreprise, une seule forêt avec un seul domaine peut suffire.

### 7.4 Schéma conceptuel

```text
FORÊT : ad.lab.test
|
+-- DOMAINE : ad.lab.test
    |
    +-- DC1
    |
    +-- Utilisateurs
    |
    +-- Groupes
    |
    +-- Ordinateurs
    |
    +-- Unités d'organisation
```

Le schéma représente une forêt comportant un domaine. Il ne s'agit pas d'une obligation d'architecture : certaines organisations possèdent plusieurs domaines dans une même forêt.

### 7.5 Domaine et nom DNS

Le nom DNS est utilisé notamment pour localiser les services du domaine.

Le nom NetBIOS est un ancien format de nom court encore rencontré dans certaines interfaces et certains mécanismes Windows.

Exemple :

```text
Nom DNS      : ad.lab.test
Nom NetBIOS  : LAB
```

Les deux noms peuvent être utilisés dans des contextes différents.

Un nom d'utilisateur peut être écrit sous différentes formes :

```text
LAB\adiallo
```

ou :

```text
adiallo@ad.lab.test
```

Le premier utilise la forme de type domaine NetBIOS suivie du nom de compte. Le second utilise le format UPN (*User Principal Name*).

## 8. Comprendre les objets Active Directory

Active Directory organise l'information sous forme d'objets.

### 8.1 Utilisateur

Un objet utilisateur représente une identité pouvant notamment être utilisée pour l'authentification.

Il peut comprendre :

- un nom ;
- un identifiant de connexion ;
- un UPN ;
- des informations de contact ;
- une appartenance à des groupes ;
- des paramètres de compte.

Exemple :

```text
Nom complet : Amina Diallo
Compte      : adiallo
UPN         : adiallo@ad.lab.test
```

### 8.2 Ordinateur

Un objet ordinateur représente généralement une machine membre du domaine.

Il peut s'agir d'un poste de travail, d'un serveur ou d'une autre machine Windows compatible.

Exemple :

```text
PC1
 |
 +-- Objet ordinateur dans Active Directory
```

L'objet ordinateur est lié à une identité utilisée notamment pour les échanges sécurisés avec le domaine.

### 8.3 Groupe

Un groupe permet de rassembler plusieurs utilisateurs, ordinateurs ou autres identités selon les règles applicables.

Au lieu de donner individuellement un droit à dix personnes, on peut accorder le droit à un groupe, puis gérer les membres de ce groupe.

```text
Groupe : GG_Comptabilite
           |
           +-- Amina
           |
           +-- Paul
           |
           +-- Sara
```

Les utilisateurs héritent des droits qui leur sont attribués par leur appartenance au groupe et les autorisations appliquées aux ressources.

### 8.4 Unité d'organisation

Une unité d'organisation, ou OU (*Organizational Unit*), sert à organiser les objets du domaine et à appliquer des stratégies de groupe selon les besoins.

Exemple :

```text
ad.lab.test
|
+-- OU=Utilisateurs
|     |
|     +-- OU=Comptabilite
|     |
|     +-- OU=Support
|
+-- OU=Ordinateurs
      |
      +-- OU=Postes
      |
      +-- OU=Serveurs
```

Une OU n'est pas la même chose qu'un groupe.

L'OU organise les objets et fournit un périmètre de délégation et d'application des GPO. Le groupe sert notamment à gérer les appartenances et les autorisations.

## 9. Comprendre les identités et les autorisations

### 9.1 Authentification

L'authentification consiste à vérifier l'identité présentée par un utilisateur ou un service.

Exemple :

```text
Utilisateur
    |
    | Identité et informations d'authentification
    v
Contrôleur de domaine
    |
    v
Résultat du mécanisme d'authentification
```

Les informations d'authentification doivent être protégées. Il ne faut jamais demander à un utilisateur de communiquer son mot de passe pour effectuer une opération ordinaire de support.

### 9.2 Autorisation

L'autorisation consiste à déterminer ce qu'une identité a le droit de faire.

Un utilisateur peut s'authentifier correctement, mais ne pas avoir le droit d'accéder à un dossier.

```text
Authentification réussie
          |
          v
Tentative d'accès au dossier
          |
          v
Vérification des autorisations
          |
          +-- Autorisé : accès accordé
          |
          +-- Non autorisé : accès refusé
```

Authentification et autorisation sont deux étapes différentes.

### 9.3 Pourquoi utiliser des groupes ?

Une entreprise peut organiser les droits de cette manière :

```text
Utilisateurs
     |
     v
Groupe GG_Comptabilite
     |
     v
Groupe de droits ou autorisation attribuée
     |
     v
Dossier Comptabilite
```

Les droits accordés au groupe peuvent être maintenus même lorsque les personnes changent.

Cette méthode facilite l'administration et réduit le risque de permissions oubliées ou accordées individuellement de manière incohérente.

## 10. Pourquoi DNS est indispensable à Active Directory

DNS n'est pas seulement utilisé pour convertir un nom de machine en adresse IP.

Active Directory utilise aussi DNS pour localiser les contrôleurs de domaine et certains services nécessaires à l'authentification et à la réplication.

### 10.1 Exemple de résolution

Un poste doit rejoindre le domaine `ad.lab.test`.

Il doit notamment trouver les services du domaine.

```text
PC1
 |
 | Recherche des services du domaine
 v
Serveur DNS
 |
 | Retourne les enregistrements correspondant
 | aux contrôleurs de domaine
 v
DC1
 |
 v
Authentification et jointure de domaine
```

Le serveur DNS permet donc au client de découvrir les services plutôt que de dépendre d'une adresse codée en dur pour chaque opération.

### 10.2 Enregistrements DNS

Les enregistrements les plus courants comprennent :

| Type | Rôle |
|---|---|
| A | Associe un nom à une adresse IPv4 |
| AAAA | Associe un nom à une adresse IPv6 |
| CNAME | Crée un alias de nom |
| MX | Désigne des serveurs de messagerie pour un domaine |
| PTR | Permet une résolution inverse |
| SRV | Décrit l'emplacement d'un service, notamment les services de domaine |

Active Directory utilise notamment des enregistrements SRV pour permettre aux clients de trouver des contrôleurs de domaine.

### 10.3 Pourquoi le DNS public ne doit pas être configuré directement comme DNS préféré du client de domaine

Un poste membre du domaine doit utiliser un serveur DNS capable de résoudre les zones Active Directory.

Si le client utilise directement un résolveur public qui ne connaît pas les zones internes, il peut être incapable de trouver les services d'annuaire et de joindre le domaine.

Dans une infrastructure classique :

```text
Poste client
     |
     v
DNS interne Windows
     |
     +-- Zone ad.lab.test
     |
     +-- Enregistrements des contrôleurs de domaine
     |
     +-- Redirections éventuelles pour les noms externes
```

Le serveur DNS interne peut être configuré avec des redirecteurs afin de résoudre des noms externes.

Il ne faut pas configurer arbitrairement un DNS public comme serveur DNS secondaire d'un poste membre en espérant que Windows interrogera toujours le DNS interne pour les noms du domaine. Le comportement de sélection des serveurs DNS dépend du contexte et peut rendre la résolution intermittente.

### 10.4 Vérifier les enregistrements SRV

Depuis PowerShell sur un poste qui utilise le DNS du domaine :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

Cette commande demande les enregistrements SRV liés à la localisation des services LDAP des contrôleurs de domaine dans l'espace de noms indiqué.

On peut également tester :

```powershell
Resolve-DnsName dc1.ad.lab.test
```

La réponse doit correspondre à l'adresse IP configurée pour le contrôleur de domaine, selon la zone et les enregistrements présents.

Documentation Microsoft :

https://learn.microsoft.com/fr-fr/windows-server/networking/dns/dns-overview

https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/plan/dns-and-ad-ds

## 11. Installer le rôle Active Directory Domain Services

Nous allons installer AD DS sur `DC1`.

Deux méthodes sont possibles :

- Gestionnaire de serveur ;
- Windows PowerShell.

Pour débuter, il est utile de comprendre les deux.

### 11.1 Installation graphique avec Gestionnaire de serveur

Ouvrez le Gestionnaire de serveur.

Suivez les étapes générales :

1. sélectionnez **Gérer** ;
2. choisissez **Ajouter des rôles et fonctionnalités** ;
3. sélectionnez l'installation basée sur un rôle ou une fonctionnalité ;
4. choisissez le serveur local ;
5. sélectionnez **Services de domaine Active Directory** ;
6. ajoutez les fonctionnalités de gestion proposées ;
7. poursuivez l'assistant ;
8. vérifiez les sélections ;
9. lancez l'installation.

L'installation du rôle ne signifie pas encore que le serveur est un contrôleur de domaine. La promotion constitue une étape distincte.

### 11.2 Installation avec PowerShell

Ouvrez PowerShell en tant qu'administrateur.

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
```

Explication :

- `Install-WindowsFeature` installe un rôle ou une fonctionnalité Windows Server ;
- `AD-Domain-Services` désigne le rôle Active Directory Domain Services ;
- `-IncludeManagementTools` demande aussi les outils d'administration nécessaires.

Pour vérifier l'installation :

```powershell
Get-WindowsFeature AD-Domain-Services
```

Le résultat permet de vérifier si le rôle est installé.

### 11.3 Installation et promotion : deux opérations distinctes

```text
Installation du rôle AD DS
          |
          v
Composants AD DS disponibles
          |
          v
Promotion du serveur
          |
          v
Configuration du domaine
          |
          v
Redémarrage demandé par l'installation
          |
          v
Contrôleur de domaine opérationnel
```

La prochaine étape consiste à créer une nouvelle forêt, car le laboratoire ne possède encore aucun domaine.

Documentation Microsoft :

https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/deploy/install-active-directory-domain-services--level-100-

## 12. Créer le premier domaine Active Directory

### 12.1 Choisir le nom du domaine de laboratoire

Nous utiliserons :

```text
Nom DNS du domaine : ad.lab.test
Nom NetBIOS        : LAB
Nom du serveur     : DC1
Adresse IP         : 192.168.10.10
```

Le nom `ad.lab.test` est réservé au laboratoire pédagogique.

Pour une organisation réelle, choisissez un espace DNS adapté à son environnement et à ses exigences de gestion des noms. Évitez de choisir un nom de domaine interne sans avoir réfléchi à sa compatibilité avec la stratégie DNS de l'entreprise.

### 12.2 Comprendre la première forêt

Puisque c'est le premier domaine du laboratoire, la promotion créera également une nouvelle forêt.

```text
Nouvelle forêt
     |
     v
Domaine racine : ad.lab.test
     |
     v
Premier contrôleur de domaine : DC1
```

Lors de la création du premier domaine, le rôle DNS est généralement installé pour répondre aux besoins de résolution du domaine, en particulier lorsque la configuration proposée prévoit DNS.

### 12.3 Promouvoir le serveur avec Gestionnaire de serveur

Après l'installation du rôle AD DS :

1. ouvrez le Gestionnaire de serveur ;
2. sélectionnez la notification liée à la configuration d'AD DS ;
3. choisissez **Promouvoir ce serveur en contrôleur de domaine** ;
4. sélectionnez l'option permettant d'ajouter une nouvelle forêt ;
5. saisissez `ad.lab.test` comme nom du domaine racine ;
6. choisissez les options de contrôleur de domaine adaptées au laboratoire ;
7. définissez le mot de passe DSRM ;
8. poursuivez les vérifications de prérequis ;
9. lisez les avertissements et corrigez ceux qui sont nécessaires ;
10. lancez la promotion.

Le serveur doit redémarrer pour terminer l'opération.

Le DSRM (*Directory Services Restore Mode*) est un mode spécial de récupération d'Active Directory. Son mot de passe est distinct du compte administrateur de domaine.

Conservez-le de manière sécurisée. Il ne doit pas être utilisé comme mot de passe ordinaire de l'administrateur du domaine.

### 12.4 Promouvoir le serveur avec PowerShell

Sur le serveur après installation du rôle :

```powershell
Install-ADDSForest -DomainName "ad.lab.test" -DomainNetbiosName "LAB" -InstallDNS
```

La commande lance la création d'une nouvelle forêt et installe le service DNS conformément aux paramètres utilisés.

L'assistant PowerShell demande les informations nécessaires, notamment le mot de passe DSRM. Il peut également demander une confirmation et le redémarrage requis.

Avant d'exécuter cette commande, assurez-vous que le serveur est bien destiné à devenir le premier contrôleur de domaine de cette nouvelle forêt.

Ne lancez pas cette commande sur un serveur de production en supposant qu'elle ne fera qu'ajouter le rôle AD DS.

### 12.5 Après le redémarrage

Connectez-vous avec le compte administrateur de domaine créé ou configuré pendant l'installation, selon les paramètres du système.

La forme de connexion peut ressembler à :

```text
LAB\Administrator
```

ou utiliser l'UPN approprié.

Vérifiez le nom du domaine :

```powershell
Get-ADDomain
```

Puis la forêt :

```powershell
Get-ADForest
```

Le serveur est maintenant censé fonctionner comme contrôleur de domaine pour le domaine de laboratoire, sous réserve de la réussite de la promotion et de l'état des services.

## 13. Vérifier le fonctionnement initial d'Active Directory

Après la promotion, il faut contrôler l'état du service plutôt que supposer qu'une installation réussie garantit que toutes les fonctionnalités sont opérationnelles.

### 13.1 Vérifier les services

```powershell
Get-Service NTDS, DNS, Netlogon, KDC
```

Cette commande affiche l'état de plusieurs services importants dans une installation AD DS utilisant DNS et les composants d'authentification classiques.

Les noms exacts des services doivent être interprétés selon le système et les composants installés.

### 13.2 Vérifier le domaine

```powershell
Get-ADDomain
```

Cette commande affiche des informations sur le domaine Active Directory courant.

### 13.3 Vérifier la forêt

```powershell
Get-ADForest
```

Cette commande affiche les informations relatives à la forêt.

Les commandes `Get-ADDomain` et `Get-ADForest` nécessitent le module PowerShell Active Directory, généralement installé avec les outils de gestion correspondants.

### 13.4 Diagnostiquer le contrôleur de domaine

```powershell
dcdiag
```

`dcdiag` effectue des vérifications de diagnostic sur le contrôleur de domaine.

La sortie peut contenir des informations nombreuses. Il faut examiner les tests qui échouent, comprendre le message et vérifier le contexte avant d'appliquer une correction.

Pour examiner la partie DNS :

```powershell
dcdiag /test:dns /v
```

Cette commande fournit des informations plus détaillées sur les contrôles DNS réalisés par l'outil.

### 13.5 Vérifier la résolution DNS

```powershell
Resolve-DnsName dc1.ad.lab.test
```

Puis :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

Si les requêtes échouent, vérifiez la configuration DNS du serveur, les zones attendues, les enregistrements et les journaux.

### 13.6 Vérifier l'heure

Kerberos dépend d'une synchronisation temporelle adéquate entre les systèmes.

Pour examiner l'état de la synchronisation :

```powershell
w32tm /query /status
```

Un défaut d'heure peut provoquer des problèmes d'authentification, même si DNS et les services AD DS sont opérationnels.

Dans une infrastructure réelle, la hiérarchie de synchronisation temporelle doit être conçue explicitement et configurée selon les exigences de l'organisation.

## 14. Comprendre les OU : unités d'organisation

Une unité d'organisation est un conteneur logique dans Active Directory.

Elle permet de regrouper des objets pour faciliter l'organisation, la délégation administrative et l'application des stratégies de groupe.

### 14.1 Exemple de structure d'entreprise

```text
ad.lab.test
|
+-- OU=Utilisateurs
|     |
|     +-- OU=Comptabilite
|     |
|     +-- OU=Support
|     |
|     +-- OU=Direction
|
+-- OU=Ordinateurs
|     |
|     +-- OU=Postes
|     |
|     +-- OU=Serveurs
|
+-- OU=Groupes
```

Cette organisation est un exemple. Une entreprise doit choisir des OU qui correspondent à ses besoins de gestion, à la délégation et aux règles de stratégie de groupe.

### 14.2 Pourquoi créer des OU ?

Les OU permettent notamment de :

- séparer les catégories d'utilisateurs ;
- organiser les ordinateurs ;
- appliquer des GPO à une partie du domaine ;
- déléguer certaines tâches d'administration ;
- maintenir une arborescence lisible.

### 14.3 Une OU n'est pas un groupe

Cette distinction est fondamentale.

| Unité d'organisation | Groupe |
|---|---|
| Organise les objets | Rassemble des identités |
| Peut servir de cible pour une GPO | Sert notamment à gérer les autorisations |
| Peut servir de périmètre de délégation | Peut recevoir des droits sur des ressources |
| Ne remplace pas les droits d'accès aux fichiers | Ne remplace pas une structure d'organisation des objets |

Il ne faut pas accorder des droits sur un dossier simplement parce qu'un utilisateur est placé dans une OU. Les autorisations de la ressource doivent être configurées séparément.

## 15. Créer les OU avec l'interface graphique

Après l'installation des outils d'administration :

1. ouvrez **Outils** dans le Gestionnaire de serveur ;
2. sélectionnez **Utilisateurs et ordinateurs Active Directory** ;
3. développez le domaine `ad.lab.test` ;
4. faites un clic droit sur le domaine ;
5. sélectionnez **Nouveau**, puis **Unité d'organisation** ;
6. créez les OU nécessaires.

Pour le laboratoire, créez :

```text
Utilisateurs
Ordinateurs
Groupes
```

Vous pouvez ensuite créer une OU `Comptabilite` sous `Utilisateurs`, puis une OU `Support`.

Ne multipliez pas les niveaux d'arborescence sans raison. L'objectif est d'organiser efficacement les objets et les stratégies.

## 16. Créer les OU avec PowerShell

Vérifiez que le module Active Directory est disponible :

```powershell
Get-Module -ListAvailable ActiveDirectory
```

S'il est présent, importez-le :

```powershell
Import-Module ActiveDirectory
```

### 16.1 Créer l'OU Utilisateurs

```powershell
New-ADOrganizationalUnit `
    -Name "Utilisateurs" `
    -Path "DC=ad,DC=lab,DC=test"
```

La syntaxe `DC=ad,DC=lab,DC=test` représente le nom distingué de la racine du domaine `ad.lab.test`.

### 16.2 Créer l'OU Ordinateurs

```powershell
New-ADOrganizationalUnit `
    -Name "Ordinateurs" `
    -Path "DC=ad,DC=lab,DC=test"
```

### 16.3 Créer l'OU Groupes

```powershell
New-ADOrganizationalUnit `
    -Name "Groupes" `
    -Path "DC=ad,DC=lab,DC=test"
```

### 16.4 Créer une OU imbriquée

```powershell
New-ADOrganizationalUnit `
    -Name "Comptabilite" `
    -Path "OU=Utilisateurs,DC=ad,DC=lab,DC=test"
```

La nouvelle OU est créée sous `Utilisateurs`.

### 16.5 Vérifier les OU

```powershell
Get-ADOrganizationalUnit -Filter *
```

Pour une recherche plus ciblée :

```powershell
Get-ADOrganizationalUnit `
    -Filter 'Name -eq "Utilisateurs"' `
    -SearchBase "DC=ad,DC=lab,DC=test"
```

Ces commandes permettent de vérifier les objets créés dans le domaine.

## 17. Créer des utilisateurs Active Directory

### 17.1 Utilisateur de laboratoire

Nous allons créer le compte `adiallo`, destiné à représenter Amina Diallo.

Les informations sont fictives.

```text
Nom complet : Amina Diallo
Compte      : adiallo
Domaine     : ad.lab.test
UPN         : adiallo@ad.lab.test
```

### 17.2 Création graphique

Dans **Utilisateurs et ordinateurs Active Directory** :

1. développez le domaine ;
2. ouvrez l'OU appropriée ;
3. faites un clic droit dans la liste des objets ;
4. sélectionnez **Nouveau**, puis **Utilisateur** ;
5. renseignez le prénom, le nom et le nom de connexion ;
6. définissez un mot de passe initial ;
7. choisissez les options de sécurité adaptées ;
8. terminez la création.

Pour un environnement réel, le mot de passe initial doit être transmis de façon sécurisée, et les paramètres imposés aux utilisateurs doivent suivre la politique de l'organisation.

### 17.3 Création avec PowerShell

Le module Active Directory doit être chargé.

```powershell
$Password = Read-Host "Mot de passe initial" -AsSecureString

New-ADUser `
    -Name "Amina Diallo" `
    -GivenName "Amina" `
    -Surname "Diallo" `
    -SamAccountName "adiallo" `
    -UserPrincipalName "adiallo@ad.lab.test" `
    -Path "OU=Comptabilite,OU=Utilisateurs,DC=ad,DC=lab,DC=test" `
    -AccountPassword $Password `
    -Enabled $true
```

La commande crée le compte dans l'OU `Comptabilite`.

Le mot de passe est demandé avec `Read-Host -AsSecureString`, plutôt que d'être écrit en clair dans l'instruction.

Assurez-vous que l'OU existe avant d'exécuter la commande. Si elle n'existe pas, l'opération échouera.

### 17.4 Vérifier l'utilisateur

```powershell
Get-ADUser adiallo
```

Pour afficher plusieurs propriétés :

```powershell
Get-ADUser adiallo -Properties DisplayName, Enabled, UserPrincipalName
```

Cette commande permet notamment de vérifier l'identité et l'état du compte.

### 17.5 Activer ou désactiver un compte

Désactiver :

```powershell
Disable-ADAccount -Identity adiallo
```

Réactiver :

```powershell
Enable-ADAccount -Identity adiallo
```

Une désactivation empêche normalement l'utilisation du compte pour de nouvelles authentifications concernées, mais elle ne doit pas être assimilée à une révocation instantanée de toutes les sessions et de tous les tickets déjà obtenus.

Dans une opération réelle de départ d'un salarié, il faut aussi examiner les sessions, les jetons, les accès aux applications et les autres identités associées.

### 17.6 Réinitialiser un mot de passe

```powershell
$NewPassword = Read-Host "Nouveau mot de passe" -AsSecureString

Set-ADAccountPassword `
    -Identity adiallo `
    -Reset `
    -NewPassword $NewPassword
```

Cette commande réinitialise le mot de passe du compte.

La procédure de support doit vérifier l'identité du demandeur et appliquer les règles de sécurité de l'organisation.

## 18. Comprendre les groupes Active Directory

Les groupes simplifient la gestion des autorisations.

Il est généralement préférable de gérer l'accès aux ressources avec des groupes plutôt que d'attribuer les droits individuellement à chaque utilisateur.

### 18.1 Exemple de groupe métier

Nous allons créer un groupe de sécurité :

```text
GG_Comptabilite
       |
       +-- Amina Diallo
       |
       +-- Autres membres autorisés
```

Le groupe peut ensuite recevoir une autorisation sur un dossier, une application ou une ressource partagée.

### 18.2 Groupes de sécurité et groupes de distribution

Les groupes de sécurité servent notamment à accorder des droits.

Les groupes de distribution sont plutôt utilisés dans certains scénarios de communication, notamment lorsque des services de messagerie les prennent en charge.

Pour organiser les autorisations d'accès aux ressources Windows, un groupe de sécurité est généralement le choix à considérer.

### 18.3 Portées de groupes

Les portées courantes comprennent :

- Global ;
- Domain Local ;
- Universal.

Elles déterminent notamment les types d'appartenance et la manière dont les groupes sont utilisés dans la forêt ou le domaine.

Pour débuter, retenez surtout que le choix de portée doit suivre le modèle d'administration et d'attribution des droits. Il ne faut pas choisir une portée au hasard.

### 18.4 Créer un groupe avec PowerShell

```powershell
New-ADGroup `
    -Name "GG_Comptabilite" `
    -SamAccountName "GG_Comptabilite" `
    -GroupCategory Security `
    -GroupScope Global `
    -Path "OU=Groupes,DC=ad,DC=lab,DC=test"
```

Cette commande crée un groupe de sécurité global dans l'OU `Groupes`.

### 18.5 Ajouter l'utilisateur au groupe

```powershell
Add-ADGroupMember `
    -Identity "GG_Comptabilite" `
    -Members "adiallo"
```

L'utilisateur est maintenant membre du groupe.

### 18.6 Vérifier les membres

```powershell
Get-ADGroupMember -Identity "GG_Comptabilite"
```

La commande affiche les objets membres du groupe.

### 18.7 Pourquoi les groupes sont-ils importants ?

Considérons un dossier réservé aux employés de la comptabilité.

```text
Dossier Comptabilite
         |
         v
Autorisation accordée au groupe
GG_Comptabilite
         |
         +-- Amina
         +-- Paul
         +-- Sara
```

Lorsqu'un employé rejoint le service, il suffit généralement de l'ajouter au groupe approprié si les règles de gestion le prévoient.

Lorsqu'il quitte le service, le retrait du groupe permet de supprimer les droits qui provenaient de cette appartenance, sous réserve qu'aucun autre groupe ou mécanisme ne lui accorde les mêmes permissions.

## 19. Les groupes imbriqués et le modèle AGDLP

Dans les environnements Windows, le modèle AGDLP est souvent présenté comme une méthode d'organisation des droits dans un domaine.

Il signifie :

- **A** : Accounts ;
- **G** : Global groups ;
- **DL** : Domain Local groups ;
- **P** : Permissions.

Schéma simplifié :

```text
Comptes utilisateurs
       |
       v
Groupes globaux métier
       |
       v
Groupes locaux de domaine
       |
       v
Permissions sur les ressources
```

Exemple :

```text
Amina
  |
  v
GG_Comptabilite
  |
  v
DL_Dossier_Comptabilite_RW
  |
  v
Dossier Comptabilite
```

Le groupe global représente ici les utilisateurs du service. Le groupe local de domaine porte l'autorisation d'accès à la ressource.

Cette séparation distingue les personnes ou équipes qui doivent accéder à une ressource des permissions qui y sont accordées.

Le modèle doit être adapté à la taille et aux besoins de l'organisation. Dans un laboratoire très simple, il peut sembler plus complexe que nécessaire, mais il prépare à une administration plus structurée.

## 20. Joindre un poste client au domaine

Un poste compatible peut rejoindre un domaine Active Directory afin de participer aux mécanismes d'authentification et d'administration du domaine.

### 20.1 Prérequis

Avant de joindre le poste :

- vérifiez que le domaine existe et fonctionne ;
- assurez-vous que le poste utilise le DNS interne prévu ;
- vérifiez la connectivité avec le contrôleur de domaine ;
- utilisez une édition Windows cliente qui prend en charge la jonction à un domaine AD DS classique ;
- disposez des autorisations nécessaires pour effectuer la jonction ;
- vérifiez que le nom DNS du domaine est correct.

Les éditions Windows Home ne prennent normalement pas en charge la jonction traditionnelle à un domaine Active Directory local. Utilisez une édition cliente compatible, par exemple Windows Pro, Enterprise ou Education selon le contexte.

### 20.2 Configurer le DNS sur le poste

Sur PC1, configurez le DNS préféré à :

```text
192.168.10.10
```

Cette adresse correspond au serveur DNS du contrôleur de domaine dans notre laboratoire.

Vérifiez ensuite la configuration :

```powershell
Get-DnsClientServerAddress
```

### 20.3 Tester la résolution

```powershell
Resolve-DnsName dc1.ad.lab.test
```

Puis :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

Les deux vérifications sont utiles pour déterminer si le client trouve le serveur et les services du domaine.

### 20.4 Joindre le domaine avec l'interface graphique

Sur une édition Windows compatible :

1. ouvrez les propriétés système ;
2. accédez aux paramètres de nom de l'ordinateur ;
3. sélectionnez la modification du domaine ou du groupe de travail ;
4. choisissez le domaine ;
5. saisissez `ad.lab.test` ;
6. fournissez les informations d'identification autorisées ;
7. attendez le message confirmant la réussite ;
8. redémarrez lorsque Windows le demande.

Les intitulés exacts des menus peuvent varier selon la version Windows et son interface.

### 20.5 Joindre le domaine avec PowerShell

Sur le poste client, ouvrez PowerShell en tant qu'administrateur :

```powershell
Add-Computer `
    -DomainName "ad.lab.test" `
    -Credential (Get-Credential) `
    -Restart
```

PowerShell demande les informations d'identification. Utilisez un compte autorisé à joindre la machine au domaine.

N'enregistrez pas un mot de passe administrateur en clair dans un script.

### 20.6 Vérifier la jonction

Après le redémarrage, exécutez :

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name, Domain, PartOfDomain
```

Le résultat doit indiquer que PC1 appartient au domaine prévu.

Vous pouvez également vérifier le contrôleur de domaine découvert :

```powershell
nltest /dsgetdc:ad.lab.test
```

Cette commande permet de demander au système de localiser un contrôleur de domaine pour le domaine indiqué.

### 20.7 Se connecter avec un compte de domaine

Sur l'écran de connexion, utilisez un compte de domaine autorisé.

Exemple :

```text
LAB\adiallo
```

ou :

```text
adiallo@ad.lab.test
```

Le compte doit exister, être activé et être autorisé à ouvrir une session sur le poste concerné.

L'appartenance au domaine ne garantit pas que toute identité peut ouvrir une session sur n'importe quel serveur. Les droits de connexion locale et les stratégies de sécurité restent déterminants.

## 21. Comprendre les stratégies de groupe (GPO)

Une stratégie de groupe, ou GPO (*Group Policy Object*), permet de centraliser de nombreux paramètres de configuration et de sécurité pour les utilisateurs et les ordinateurs Windows.

Elle peut notamment servir à :

- configurer certains paramètres du système ;
- contrôler certaines options utilisateur ;
- déployer des paramètres de sécurité ;
- organiser certaines restrictions ;
- gérer certaines configurations de postes ;
- appliquer des paramètres de scripts pris en charge.

### 21.1 Principe général

```text
Active Directory
       |
       v
Stratégie de groupe (GPO)
       |
       v
OU ou autre conteneur ciblé
       |
       +--------------+
       |              |
       v              v
      PC1            PC2
       |              |
       v              v
Paramètres appliqués selon la portée
et les droits de l'objet concerné
```

Une GPO n'est pas simplement un objet utilisateur ou un groupe. Elle est liée à des conteneurs et traite des paramètres selon les mécanismes de stratégie de groupe.

### 21.2 Où les GPO peuvent-elles s'appliquer ?

Les stratégies peuvent être liées à différents conteneurs Active Directory appropriés, notamment :

- le site ;
- le domaine ;
- l'unité d'organisation.

L'héritage, les filtres, les options de lien et les paramètres de priorité influencent le résultat final.

### 21.3 Ordre général de traitement

Le traitement des GPO suit généralement l'ordre suivant :

```text
Stratégie locale
       |
       v
Stratégies liées au site
       |
       v
Stratégies liées au domaine
       |
       v
Stratégies liées aux OU parentes
       |
       v
Stratégies liées aux OU enfants
```

Des exceptions et mécanismes de contrôle peuvent modifier le résultat, notamment l'héritage bloqué, les liens imposés et le filtrage de sécurité.

Il faut examiner l'ensemble des GPO applicables à l'objet pour expliquer un paramètre effectif.

### 21.4 Pourquoi utiliser des OU dédiées ?

Une OU dédiée permet de cibler une stratégie sans appliquer automatiquement le même paramètre à tous les objets du domaine.

Par exemple :

```text
OU=Ordinateurs
       |
       +-- OU=Postes
               |
               +-- PC1
               +-- PC2
               +-- PC3
```

Une GPO liée à `OU=Postes` peut s'appliquer aux ordinateurs qui y sont placés, en fonction des paramètres de stratégie et de leur portée.

## 22. Créer une GPO de test

### 22.1 Ouvrir la console

Dans Gestionnaire de serveur, ouvrez les outils d'administration, puis **Gestion de stratégie de groupe**.

Selon l'installation, les outils nécessaires doivent être ajoutés avec les fonctionnalités de gestion appropriées.

### 22.2 Créer une stratégie

Dans la console :

1. développez la forêt et le domaine ;
2. identifiez une OU de test ;
3. créez une GPO liée à cette OU ;
4. donnez-lui un nom explicite, par exemple `GPO_Laboratoire_Postes` ;
5. modifiez uniquement un paramètre de test dont l'effet est compris.

Ne commencez pas par désactiver des protections ou modifier des paramètres critiques.

### 22.3 Mettre à jour les stratégies

Sur un poste client membre du domaine :

```powershell
gpupdate /force
```

Cette commande demande une actualisation des stratégies de groupe.

Certaines modifications nécessitent une fermeture de session ou un redémarrage avant que leur effet soit complet.

### 22.4 Vérifier les stratégies appliquées

```powershell
gpresult /r
```

Cette commande présente les résultats de stratégie selon le contexte de l'utilisateur et de l'ordinateur.

Pour obtenir un rapport HTML :

```powershell
gpresult /h "$env:TEMP\gpresult.html"
```

Le fichier produit peut être ouvert sur le poste pour examiner les informations détaillées.

### 22.5 Bonnes pratiques pour les GPO

- Testez les stratégies sur une OU pilote.
- N'appliquez pas immédiatement une nouvelle politique à tous les postes.
- Donnez un nom explicite à chaque GPO.
- Documentez son objectif et ses paramètres.
- Vérifiez les comptes et ordinateurs effectivement ciblés.
- Évitez les liens et filtres difficiles à comprendre.
- Conservez une procédure de retour arrière.

Documentation Microsoft :

https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview

## 23. Gestion des utilisateurs et des ordinateurs

### 23.1 Recherche d'utilisateurs

Avec PowerShell :

```powershell
Get-ADUser -Filter *
```

Cette commande peut retourner un nombre important de résultats dans un domaine volumineux. Il vaut mieux filtrer les objets lorsqu'on sait ce que l'on recherche.

Exemple :

```powershell
Get-ADUser -Filter 'Enabled -eq $true' |
    Select-Object Name, SamAccountName
```

Cette requête affiche les utilisateurs activés correspondant au filtre pris en charge par le module AD.

### 23.2 Recherche des ordinateurs

```powershell
Get-ADComputer -Filter * |
    Select-Object Name, DNSHostName
```

La commande permet d'afficher des objets ordinateur et certaines de leurs propriétés.

### 23.3 Déplacer un objet ordinateur

```powershell
Move-ADObject `
    -Identity "CN=PC1,CN=Computers,DC=ad,DC=lab,DC=test" `
    -TargetPath "OU=Postes,OU=Ordinateurs,DC=ad,DC=lab,DC=test"
```

Cette commande illustre le déplacement d'un objet vers une OU dédiée.

Le chemin source doit correspondre à l'emplacement réel de l'objet. La localisation des comptes ordinateurs créés par défaut et leur emplacement de stockage peuvent dépendre de la configuration du domaine.

Avant de déplacer un objet, vérifiez l'effet des GPO et de la délégation sur son emplacement de destination.

### 23.4 Supprimer ou désactiver un compte

Pour désactiver un compte utilisateur :

```powershell
Disable-ADAccount -Identity adiallo
```

La désactivation est généralement préférable à la suppression immédiate lorsqu'il faut conserver l'objet pour une enquête, un audit ou une procédure de départ.

La suppression d'un objet est une opération différente. Elle doit respecter la politique de cycle de vie et de conservation de l'organisation.

### 23.5 Le principe du moindre privilège

Ne donnez pas systématiquement le statut d'administrateur du domaine aux utilisateurs qui ont besoin d'une fonction particulière.

Il faut distinguer :

- les droits d'un utilisateur ordinaire ;
- les permissions sur une ressource ;
- les droits d'administration délégués ;
- les privilèges élevés du domaine.

Les privilèges d'administration de domaine sont extrêmement sensibles. Ils doivent être utilisés uniquement dans les contextes appropriés.

## 24. Partage de fichiers et permissions : introduction

Windows Server peut aussi héberger des partages de fichiers. La sécurité d'un fichier repose sur plusieurs éléments.

### 24.1 Deux niveaux de permissions

Pour un accès via SMB, il faut notamment considérer :

- les autorisations du partage ;
- les autorisations NTFS du système de fichiers.

Les droits effectifs résultent de la combinaison de ces contrôles et des appartenances aux groupes, sous réserve des règles d'accès applicables.

### 24.2 Exemple d'organisation

```text
Serveur de fichiers
       |
       +-- Dossier Comptabilite
       |       |
       |       +-- Autorisations pour groupes adaptés
       |
       +-- Dossier Support
               |
               +-- Autorisations pour groupes adaptés
```

Un utilisateur membre du groupe de comptabilité peut recevoir un accès au dossier de comptabilité grâce à une autorisation attribuée au groupe.

Le dossier doit être protégé avec des permissions qui correspondent aux besoins métier.

### 24.3 Pourquoi les groupes sont-ils utiles ?

Une approche courante consiste à attribuer les droits à des groupes plutôt qu'à chaque utilisateur.

```text
Utilisateurs
     |
     v
Groupes métier
     |
     v
Groupes de droits
     |
     v
Partages et autorisations NTFS
```

Cette organisation limite les modifications individuelles dispersées et facilite les audits.

### 24.4 Ne pas accorder des droits excessifs

Évitez d'accorder `Everyone: Full Control` sur des partages sensibles pour résoudre rapidement un problème d'accès.

Il faut identifier la permission manquante et appliquer le changement minimal nécessaire.

## 25. Les services complémentaires : DNS, DHCP et fichiers

### 25.1 DNS Server

DNS permet aux clients et aux serveurs de résoudre les noms et de localiser les services.

Dans Active Directory, DNS est essentiel pour la découverte des contrôleurs de domaine et les opérations liées au domaine.

Le serveur DNS peut aussi répondre aux requêtes portant sur des zones externes, selon sa configuration.

### 25.2 DHCP Server

DHCP peut attribuer automatiquement aux postes :

- une adresse IP ;
- un masque ;
- une passerelle ;
- des serveurs DNS ;
- d'autres paramètres réseau selon les options configurées.

Dans une architecture Active Directory, le DNS doit être configuré avec attention afin que les clients utilisent un résolveur capable de trouver le domaine.

Un serveur DHCP déployé sur Windows Server dans un domaine Active Directory doit être autorisé dans l'environnement prévu, selon les exigences applicables. Cette précaution permet de réduire certains risques d'attribution d'adresses par un serveur DHCP non autorisé.

### 25.3 Services de fichiers

Le serveur peut héberger des partages SMB et fournir des autorisations centralisées sur les ressources.

Il est souvent préférable de documenter les groupes, dossiers, propriétaires et permissions pour faciliter l'exploitation.

### 25.4 Ne pas installer tous les rôles sur le contrôleur de domaine

Un laboratoire peut héberger plusieurs rôles sur une même machine pour réduire le nombre de VM.

En production, il faut évaluer les risques liés à la concentration des rôles et aux privilèges associés.

Les contrôleurs de domaine doivent être protégés. L'installation de fonctions supplémentaires doit être justifiée et suivie.

## 26. Sécurité élémentaire de Windows Server et Active Directory

La sécurité d'Active Directory repose sur la protection des identités, des contrôleurs de domaine, des secrets et des accès administratifs.

### 26.1 Comptes administratifs

Les comptes à privilèges élevés doivent être peu nombreux et fortement contrôlés.

Il est préférable d'utiliser des comptes distincts pour les tâches ordinaires et les tâches d'administration lorsque le modèle opérationnel de l'organisation le permet.

Un compte administrateur ne doit pas être utilisé inutilement pour consulter des sites Web ou effectuer des tâches bureautiques ordinaires.

### 26.2 Mots de passe et authentification

Définissez une politique cohérente concernant :

- les mots de passe ;
- la protection contre les tentatives répétées ;
- la gestion des comptes inutilisés ;
- les méthodes d'authentification ;
- les procédures de réinitialisation ;
- les comptes de service.

Les exigences ne doivent pas être réduites à une règle isolée. La protection des identités nécessite également une politique d'administration, de surveillance et de récupération.

### 26.3 DNS et sécurité

Le DNS interne doit être géré afin que les clients résolvent correctement les ressources du domaine.

Les mises à jour, les droits de modification des zones, les redirecteurs et les règles réseau doivent être contrôlés.

Une modification DNS erronée peut rendre les services difficiles à localiser ou orienter un client vers une mauvaise destination.

### 26.4 Mises à jour

Maintenez Windows Server à jour selon la stratégie de maintenance de l'organisation.

Avant une mise à jour importante d'un contrôleur de domaine, vérifiez :

- l'état des autres contrôleurs de domaine, s'il y en a ;
- les sauvegardes disponibles ;
- les dépendances de l'infrastructure ;
- les possibilités de restauration ;
- les procédures de redémarrage ;
- le fonctionnement du DNS et de l'authentification après l'opération.

### 26.5 Pare-feu

Ne désactivez pas globalement le pare-feu Windows pour résoudre un problème de connexion.

Il faut identifier les ports et protocoles requis entre les clients, les contrôleurs de domaine et les services utilisés, puis autoriser les flux nécessaires selon la topologie.

Une jointure de domaine peut utiliser plusieurs protocoles et services, notamment DNS, Kerberos, LDAP, SMB et RPC. Le port 389 ou le port 445 seul ne décrit donc pas l'ensemble des besoins réseau.

### 26.6 Sauvegarde de l'état du système

Active Directory dépend d'éléments comme sa base de données d'annuaire, les fichiers nécessaires à SYSVOL et sa configuration système.

Une stratégie de sauvegarde adaptée au contrôleur de domaine est donc indispensable.

Ne supposez pas qu'une simple copie du répertoire de la base de données Active Directory suffit pour une restauration prise en charge.

## 27. Sauvegarde et récupération : premières notions

### 27.1 Pourquoi sauvegarder un contrôleur de domaine ?

Une sauvegarde adaptée permet de préparer la récupération après :

- une erreur d'administration ;
- un incident de stockage ;
- une perte importante du système ;
- certains incidents affectant l'annuaire ;
- une défaillance nécessitant la restauration de l'état du système.

### 27.2 Sauvegarde de l'état du système

Windows Server Backup fournit des mécanismes permettant de sauvegarder l'état du système, selon les fonctionnalités installées et la méthode retenue.

Sur un contrôleur de domaine, la planification et la restauration de l'état du système doivent suivre une procédure compatible avec Active Directory.

Une sauvegarde non restaurable n'est pas une stratégie de reprise suffisante.

### 27.3 Installer Windows Server Backup

Dans un environnement où la fonctionnalité est disponible :

```powershell
Install-WindowsFeature Windows-Server-Backup
```

Cette commande installe la fonctionnalité Windows Server Backup.

### 27.4 Exemple de sauvegarde de l'état du système

Dans un laboratoire, si la sauvegarde vers le lecteur cible est préparée et si les prérequis sont satisfaits :

```powershell
wbadmin start systemstatebackup -backuptarget:E: -quiet
```

Le lecteur `E:` est un exemple. Il doit correspondre à une destination de sauvegarde adaptée et disponible.

Ne remplacez pas une destination sécurisée par un répertoire quelconque du même volume que l'installation Windows. Il faut vérifier la prise en charge du scénario, la capacité du stockage et l'accès aux sauvegardes.

### 27.5 Vérifier les sauvegardes

Contrôlez que l'opération a réellement réussi et examinez les journaux du système.

Une sauvegarde n'est pas validée uniquement parce que le processus a commencé.

Il faut périodiquement tester les procédures de restauration dans un environnement maîtrisé.

### 27.6 Attention à la restauration d'Active Directory

La récupération d'un contrôleur de domaine dépend de la situation :

- contrôleur unique ;
- plusieurs contrôleurs répliqués ;
- perte de la base locale ;
- restauration d'une sauvegarde ;
- incident logique touchant des objets ;
- besoin de récupération autoritaire ou non autoritaire selon le scénario.

Ne restaurez pas un contrôleur de domaine en copiant manuellement des fichiers de base de données depuis un autre serveur.

Pour un environnement réel, utilisez les procédures officielles et une méthode de récupération correspondant à l'incident.

## 28. Comprendre les contrôleurs de domaine supplémentaires

Notre laboratoire utilise un seul contrôleur de domaine. Cela permet d'apprendre les bases, mais introduit un point de défaillance unique.

### 28.1 Pourquoi avoir plusieurs contrôleurs de domaine ?

Une organisation peut déployer plusieurs contrôleurs de domaine afin de :

- améliorer la disponibilité de l'authentification ;
- fournir des copies répliquées de l'annuaire ;
- répartir certains traitements ;
- maintenir des services lorsque l'un des contrôleurs devient indisponible.

### 28.2 Architecture avec deux contrôleurs

```text
             +-------------------+
             | Active Directory  |
             | Domaine           |
             +-------------------+
                      |
             +--------+--------+
             |                 |
             v                 v
         +-------+         +-------+
         | DC1   |<------->| DC2   |
         | AD DS | Réplica | AD DS |
         | DNS   |         | DNS   |
         +-------+         +-------+
             |                 |
             +--------+--------+
                      |
                      v
                Postes clients
```

Les contrôleurs de domaine répliquent les modifications selon les mécanismes d'Active Directory.

Un contrôleur supplémentaire doit être installé et configuré de manière appropriée. Il ne suffit pas d'ajouter une deuxième machine au réseau avec le même rôle affiché dans le Gestionnaire de serveur.

### 28.3 Réplication Active Directory

Active Directory utilise sa propre réplication d'annuaire entre contrôleurs de domaine.

Il faut distinguer cette réplication de celle utilisée par d'autres technologies comme les clusters de bases de données.

Les contrôleurs partagent les objets d'annuaire selon la topologie et les mécanismes de réplication prévus.

### 28.4 Vérifier l'état de réplication

Sur un environnement comportant plusieurs contrôleurs de domaine :

```powershell
repadmin /replsummary
```

Cette commande fournit un résumé de l'état de réplication.

Sur un domaine à un seul contrôleur, elle n'apporte pas les mêmes informations, puisqu'il n'existe pas de paire de contrôleurs entre laquelle observer une réplication d'annuaire.

### 28.5 Un deuxième DC ne remplace pas la sauvegarde

Les suppressions et modifications d'objets peuvent se répliquer.

Plusieurs contrôleurs améliorent certains aspects de disponibilité, mais ne constituent pas une protection indépendante contre toutes les erreurs administratives ou les incidents logiques.

## 29. Les erreurs fréquentes et leur diagnostic

### 29.1 Un poste ne peut pas rejoindre le domaine

Causes possibles :

- le poste utilise le mauvais serveur DNS ;
- le domaine DNS est mal orthographié ;
- les services AD DS ou DNS ne fonctionnent pas ;
- un pare-feu bloque les communications nécessaires ;
- les informations d'identification sont incorrectes ;
- des restrictions de sécurité empêchent la jointure.

Vérifiez le DNS :

```powershell
Get-DnsClientServerAddress
```

Puis :

```powershell
Resolve-DnsName ad.lab.test
Resolve-DnsName dc1.ad.lab.test
```

Enfin, demandez la localisation d'un contrôleur de domaine :

```powershell
nltest /dsgetdc:ad.lab.test
```

### 29.2 Le nom du domaine ne se résout pas

Contrôlez :

```powershell
ipconfig /all
```

Vérifiez notamment le serveur DNS utilisé.

Puis :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

Si les enregistrements SRV ne sont pas trouvés, examinez les zones DNS et l'état du contrôleur de domaine.

### 29.3 Un utilisateur ne peut pas ouvrir une session

Vérifiez :

- que le compte existe ;
- que le compte est activé ;
- que le mot de passe est correct ;
- que le poste est membre du domaine ;
- que le réseau et DNS fonctionnent ;
- que les paramètres temporels sont cohérents ;
- que les droits d'ouverture de session sont appropriés ;
- que les journaux du poste et du contrôleur de domaine ne révèlent pas d'erreur particulière.

Ne désactivez pas la politique de sécurité simplement pour contourner une erreur d'authentification.

### 29.4 Les GPO ne sont pas appliquées

Sur le poste client :

```powershell
gpupdate /force
```

Puis :

```powershell
gpresult /r
```

Examinez le résultat, les GPO applicables et les erreurs éventuelles.

Vérifiez aussi que l'utilisateur ou l'ordinateur se trouve dans l'OU prévue, et que les filtres et autorisations de la GPO permettent son application.

### 29.5 Le serveur DNS répond, mais le domaine reste inaccessible

Un serveur DNS qui répond à une requête de nom simple n'assure pas nécessairement que tous les enregistrements requis par Active Directory existent et sont corrects.

Il faut vérifier :

- les enregistrements A ;
- les enregistrements SRV ;
- l'adresse du contrôleur de domaine ;
- la zone DNS intégrée à Active Directory ;
- l'état de Netlogon ;
- les journaux DNS et AD DS ;
- la connectivité vers les services requis.

### 29.6 Journaux de diagnostic

Utilisez l'Observateur d'événements pour examiner les journaux liés notamment à :

- Directory Service ;
- DNS Server ;
- System ;
- Security ;
- GroupPolicy ;
- Netlogon, selon les composants et les journaux disponibles.

Le journal exact à consulter dépend de la nature du problème.

La méthode de diagnostic doit partir du symptôme observé et suivre la chaîne de dépendances : réseau, DNS, localisation du contrôleur, authentification, puis autorisation.

Documentation Microsoft :

https://learn.microsoft.com/fr-fr/troubleshoot/windows-server/identity/active-directory-domain-join-troubleshooting-guidance

## 30. Travaux pratiques guidés

Les exercices suivants utilisent le laboratoire `ad.lab.test`.

### TP 1 — Préparer DC1

**Objectif :** préparer le serveur avant l'installation d'Active Directory.

Effectuez les opérations suivantes :

- installer Windows Server ;
- renommer le serveur en `DC1` ;
- configurer l'adresse `192.168.10.10/24` ;
- définir le DNS selon la préparation du laboratoire ;
- vérifier la connectivité du réseau ;
- vérifier la date et l'heure.

Vérification PowerShell :

```powershell
$env:COMPUTERNAME
Get-NetIPConfiguration
Get-NetAdapter
```

Résultat attendu : le serveur porte le nom `DC1` et utilise l'adresse prévue sur l'interface du laboratoire.

### TP 2 — Installer AD DS

Dans PowerShell administrateur :

```powershell
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
```

Vérifiez le rôle :

```powershell
Get-WindowsFeature AD-Domain-Services
```

Résultat attendu : le rôle est installé.

### TP 3 — Créer la forêt

Exécutez :

```powershell
Install-ADDSForest -DomainName "ad.lab.test" -DomainNetbiosName "LAB" -InstallDNS
```

Répondez aux demandes de configuration et conservez le mot de passe DSRM de manière sécurisée.

Le serveur doit redémarrer après l'installation.

Résultat attendu : le domaine `ad.lab.test` est créé et le serveur devient contrôleur de domaine si la promotion se termine correctement.

### TP 4 — Vérifier le contrôleur de domaine

Après redémarrage :

```powershell
Get-ADDomain
Get-ADForest
dcdiag
```

Puis :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

Résultat attendu : les informations de domaine et de forêt sont disponibles, les tests ne révèlent pas de problème majeur et les enregistrements SRV du domaine sont trouvés.

Si une commande échoue, examinez les journaux avant d'appliquer des corrections.

### TP 5 — Créer les unités d'organisation

Créez les OU :

```powershell
New-ADOrganizationalUnit -Name "Utilisateurs" -Path "DC=ad,DC=lab,DC=test"
New-ADOrganizationalUnit -Name "Ordinateurs" -Path "DC=ad,DC=lab,DC=test"
New-ADOrganizationalUnit -Name "Groupes" -Path "DC=ad,DC=lab,DC=test"
```

Créez l'OU de comptabilité :

```powershell
New-ADOrganizationalUnit -Name "Comptabilite" -Path "OU=Utilisateurs,DC=ad,DC=lab,DC=test"
```

Vérifiez :

```powershell
Get-ADOrganizationalUnit -Filter *
```

Résultat attendu : les OU apparaissent dans le domaine.

Si vous avez déjà créé ces objets, vérifiez leur existence avant de relancer les commandes.

### TP 6 — Créer un utilisateur

```powershell
$Password = Read-Host "Mot de passe initial" -AsSecureString

New-ADUser `
    -Name "Amina Diallo" `
    -GivenName "Amina" `
    -Surname "Diallo" `
    -SamAccountName "adiallo" `
    -UserPrincipalName "adiallo@ad.lab.test" `
    -Path "OU=Comptabilite,OU=Utilisateurs,DC=ad,DC=lab,DC=test" `
    -AccountPassword $Password `
    -Enabled $true
```

Vérifiez :

```powershell
Get-ADUser adiallo -Properties Enabled, UserPrincipalName
```

Résultat attendu : le compte est présent dans l'OU prévue.

### TP 7 — Créer un groupe et ajouter l'utilisateur

```powershell
New-ADGroup `
    -Name "GG_Comptabilite" `
    -SamAccountName "GG_Comptabilite" `
    -GroupCategory Security `
    -GroupScope Global `
    -Path "OU=Groupes,DC=ad,DC=lab,DC=test"
```

Puis :

```powershell
Add-ADGroupMember -Identity "GG_Comptabilite" -Members "adiallo"
```

Vérifiez :

```powershell
Get-ADGroupMember "GG_Comptabilite"
```

Résultat attendu : Amina apparaît comme membre du groupe.

### TP 8 — Joindre PC1 au domaine

Sur le poste client compatible :

1. configurez l'adresse IP ;
2. définissez le DNS préféré à `192.168.10.10` ;
3. vérifiez la résolution DNS ;
4. joignez `ad.lab.test` ;
5. redémarrez le poste ;
6. vérifiez l'appartenance au domaine.

Commande possible :

```powershell
Add-Computer -DomainName "ad.lab.test" -Credential (Get-Credential) -Restart
```

Résultat attendu : PC1 rejoint le domaine et peut localiser le contrôleur.

### TP 9 — Vérifier le compte de domaine

Sur PC1, tentez d'ouvrir une session avec le compte de domaine créé.

Vérifiez que le compte est activé et que les droits d'ouverture de session sur le poste sont appropriés.

Résultat attendu : l'utilisateur peut s'authentifier si les paramètres, le réseau et les autorisations sont corrects.

### TP 10 — Créer une GPO de laboratoire

Dans Gestion de stratégie de groupe :

1. créez une GPO appelée `GPO_Laboratoire_Postes` ;
2. liez-la à une OU de test contenant un ordinateur du laboratoire ;
3. modifiez un paramètre non critique dont l'effet est compris ;
4. actualisez les stratégies avec `gpupdate /force` ;
5. examinez `gpresult /r` ;
6. vérifiez le résultat sur le poste cible.

Résultat attendu : la stratégie s'applique aux objets prévus si la portée, l'héritage, les permissions et les filtres sont corrects.

### TP 11 — Diagnostiquer une erreur DNS

Sur PC1, remplacez temporairement la configuration DNS par une valeur qui ne résout pas le domaine dans un environnement strictement isolé, puis testez la résolution.

Utilisez :

```powershell
Resolve-DnsName dc1.ad.lab.test
```

Vous devriez observer un échec si le client ne peut plus consulter le DNS qui héberge les enregistrements nécessaires.

Rétablissez ensuite immédiatement le DNS prévu pour le laboratoire.

Ne réalisez pas cet exercice sur un poste de production ni sur un ordinateur qui dépend d'une infrastructure réseau réelle.

### TP 12 — Produire un compte rendu

Documentez :

- le nom et l'adresse du contrôleur de domaine ;
- le domaine DNS et son nom NetBIOS ;
- les services installés ;
- les OU créées ;
- le compte utilisateur ;
- le groupe ;
- la jonction de PC1 ;
- les tests DNS ;
- la GPO appliquée ;
- les difficultés rencontrées et leur correction.

Le compte rendu doit permettre à une autre personne de reproduire le laboratoire.

## 31. Exercices de compréhension avec corrigés

### Exercice 1 — Rôle d'Active Directory

**Question :** pourquoi une entreprise utilise-t-elle Active Directory ?

**Corrigé :**

Active Directory permet de centraliser l'organisation des identités et des objets, d'assurer des fonctions d'authentification et de faciliter l'administration des utilisateurs, des ordinateurs et des stratégies de domaine.

### Exercice 2 — Différence entre forêt et domaine

**Question :** quelle est la différence entre une forêt et un domaine ?

**Corrigé :**

Le domaine constitue une unité logique d'organisation et de gestion des objets. La forêt est une structure de niveau supérieur qui peut contenir un ou plusieurs domaines partageant certains éléments fondamentaux de l'annuaire.

### Exercice 3 — Rôle de DNS

**Question :** pourquoi DNS est-il indispensable à Active Directory ?

**Corrigé :**

Les clients doivent trouver les contrôleurs de domaine et les services nécessaires au domaine. DNS permet notamment de publier et d'interroger les enregistrements qui décrivent ces services.

### Exercice 4 — Contrôleur de domaine

**Question :** un serveur sur lequel AD DS est installé est-il automatiquement un contrôleur de domaine ?

**Corrigé :**

Non. L'installation du rôle et la promotion du serveur en contrôleur de domaine sont deux opérations distinctes.

### Exercice 5 — OU et groupe

**Question :** pourquoi une OU n'est-elle pas équivalente à un groupe ?

**Corrigé :**

Une OU organise les objets et sert notamment de cible à des GPO et à la délégation. Un groupe rassemble des identités et sert notamment à gérer les autorisations.

### Exercice 6 — Compte de domaine

**Question :** quelle est la différence entre un compte local et un compte de domaine ?

**Corrigé :**

Un compte local est géré par une machine particulière. Un compte de domaine est stocké dans Active Directory et peut être utilisé dans le périmètre prévu par la configuration du domaine et les autorisations associées.

### Exercice 7 — GPO

**Question :** une GPO s'applique-t-elle automatiquement à tous les ordinateurs, quel que soit leur emplacement ?

**Corrigé :**

Non. La portée de la stratégie dépend de son lien, de l'emplacement des objets, de l'héritage, des filtres et des permissions applicables.

### Exercice 8 — Groupe de sécurité

**Question :** pourquoi attribuer les droits à un groupe plutôt qu'à chaque utilisateur individuellement ?

**Corrigé :**

L'utilisation de groupes simplifie la gestion des permissions, facilite les arrivées et départs et rend les attributions de droits plus lisibles.

### Exercice 9 — Échec de jonction du domaine

**Question :** quel contrôle doit être réalisé en priorité lorsqu'un poste ne trouve pas le domaine ?

**Corrigé :**

Vérifier la configuration DNS du poste, la résolution du domaine et la présence des enregistrements permettant de localiser le contrôleur de domaine. Il faut ensuite contrôler la connectivité, les autorisations et les informations d'authentification.

### Exercice 10 — Haute disponibilité

**Question :** pourquoi un domaine doté d'un seul contrôleur de domaine peut-il être vulnérable à une panne ?

**Corrigé :**

Si le contrôleur unique devient indisponible, les services qui dépendent de lui peuvent être interrompus. Une architecture avec plusieurs contrôleurs peut améliorer la disponibilité, à condition d'organiser correctement DNS, la réplication, le réseau et la récupération.

## 32. Défi final : créer un petit domaine d'entreprise

### Objectif

Mettre en place un domaine Active Directory de laboratoire avec un contrôleur de domaine, des utilisateurs, des groupes, des OU, une GPO et un poste client membre.

### Cahier des charges

Le domaine doit respecter la configuration suivante :

```text
Domaine : ad.lab.test
NetBIOS : LAB

Contrôleur :
DC1 - 192.168.10.10

Client :
PC1 - 192.168.10.20

OU principales :
Utilisateurs
Ordinateurs
Groupes

OU métier :
Comptabilite
Support

Utilisateurs :
adiallo
psupport

Groupes :
GG_Comptabilite
GG_Support
```

### Étape A — Préparer le serveur

Installez Windows Server, renommez la machine `DC1`, configurez son adresse IP et vérifiez le réseau.

### Étape B — Installer AD DS et DNS

Installez le rôle AD DS et promouvez le serveur en créant la forêt `ad.lab.test`.

Vérifiez les services et les enregistrements DNS.

### Étape C — Organiser Active Directory

Créez les OU et les groupes nécessaires.

Placez les utilisateurs dans les OU qui correspondent à l'organisation retenue.

### Étape D — Créer les comptes

Créez `adiallo` et `psupport` avec des informations d'identification propres au laboratoire.

Ajoutez chaque utilisateur au groupe métier approprié.

### Étape E — Joindre le poste client

Configurez PC1 pour qu'il utilise le DNS interne. Rejoignez le domaine et vérifiez la découverte du contrôleur.

### Étape F — Appliquer une GPO de test

Créez une GPO de laboratoire et liez-la à la bonne OU de test. Vérifiez son application avec `gpresult`.

### Étape G — Tester les permissions

Préparez un dossier de test et accordez l'accès à un groupe métier approprié.

Vérifiez que l'utilisateur autorisé peut accéder à la ressource et qu'un utilisateur non autorisé ne dispose pas des mêmes droits, en tenant compte de toutes les appartenances et permissions effectives.

### Étape H — Documenter l'environnement

Préparez un rapport qui décrit :

- le domaine ;
- le contrôleur ;
- les paramètres IP et DNS ;
- les objets créés ;
- la structure des OU ;
- les GPO ;
- les groupes et permissions ;
- les tests effectués ;
- les procédures de diagnostic ;
- la sauvegarde prévue.

### Critères de réussite

Le défi est réussi si :

- le contrôleur de domaine fonctionne ;
- DNS résout correctement les noms du domaine ;
- les utilisateurs et groupes existent ;
- PC1 rejoint le domaine ;
- une session de domaine peut être ouverte selon les droits prévus ;
- une GPO de test est appliquée au bon périmètre ;
- les autorisations des ressources de test fonctionnent ;
- les contrôles de base et les procédures de récupération sont documentés.

## 33. Checklist d'administration élémentaire

### Installation et réseau

- [ ] Windows Server est installé et à jour selon la politique prévue.
- [ ] Le nom du serveur est correct.
- [ ] L'adresse IP est adaptée à l'architecture.
- [ ] La passerelle est configurée si elle est nécessaire.
- [ ] DNS pointe vers le serveur approprié pour le domaine.
- [ ] Les paramètres temporels sont cohérents.
- [ ] Les services et rôles installés sont documentés.

### Active Directory

- [ ] Le domaine a été créé correctement.
- [ ] Le contrôleur de domaine fonctionne.
- [ ] Les enregistrements DNS nécessaires existent.
- [ ] Les rôles et outils d'administration sont disponibles.
- [ ] Les utilisateurs sont placés dans les OU prévues.
- [ ] Les groupes sont cohérents avec les droits recherchés.
- [ ] Les objets ordinateurs sont organisés de manière claire.

### GPO et autorisations

- [ ] Les GPO possèdent des noms explicites.
- [ ] Leur portée est comprise.
- [ ] Les stratégies importantes ont été testées.
- [ ] Les autorisations sont attribuées aux groupes appropriés.
- [ ] Les accès aux ressources ont été vérifiés.
- [ ] Les droits administratifs restent limités.

### Maintenance et sécurité

- [ ] Les comptes administratifs sont protégés.
- [ ] Les comptes inutilisés sont examinés.
- [ ] Les mises à jour sont contrôlées.
- [ ] Les journaux sont consultés en cas d'erreur.
- [ ] Une stratégie de sauvegarde adaptée est prévue.
- [ ] Les procédures de récupération sont documentées.
- [ ] La restauration a été testée dans un environnement approprié.

## 34. Fiche de révision rapide

### Gestion du serveur

Afficher le nom :

```powershell
$env:COMPUTERNAME
```

Afficher la configuration IP :

```powershell
Get-NetIPConfiguration
```

Afficher les cartes réseau :

```powershell
Get-NetAdapter
```

Afficher les rôles disponibles ou installés :

```powershell
Get-WindowsFeature
```

### Active Directory

Afficher le domaine :

```powershell
Get-ADDomain
```

Afficher la forêt :

```powershell
Get-ADForest
```

Afficher les utilisateurs :

```powershell
Get-ADUser -Filter *
```

Afficher les groupes :

```powershell
Get-ADGroup -Filter *
```

Afficher les OU :

```powershell
Get-ADOrganizationalUnit -Filter *
```

Afficher les ordinateurs :

```powershell
Get-ADComputer -Filter *
```

### DNS et diagnostic

Tester une résolution :

```powershell
Resolve-DnsName dc1.ad.lab.test
```

Rechercher les enregistrements SRV :

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.ad.lab.test
```

Localiser un contrôleur de domaine :

```powershell
nltest /dsgetdc:ad.lab.test
```

Diagnostiquer AD DS :

```powershell
dcdiag
```

Vérifier l'état temporel :

```powershell
w32tm /query /status
```

### Stratégies de groupe

Actualiser :

```powershell
gpupdate /force
```

Afficher le résultat :

```powershell
gpresult /r
```

Créer un rapport HTML :

```powershell
gpresult /h "$env:TEMP\gpresult.html"
```

### Service et journaux

Vérifier plusieurs services :

```powershell
Get-Service NTDS, DNS, Netlogon, KDC
```

Consulter les journaux dans l'Observateur d'événements ou avec les outils de diagnostic appropriés.

## 35. Glossaire

**Active Directory** : annuaire Microsoft qui organise les identités et objets d'un environnement de domaine.

**AD DS** : service Active Directory Domain Services.

**Contrôleur de domaine** : serveur qui héberge une copie de l'annuaire et assure des services liés au domaine.

**Domaine** : unité logique d'administration et d'organisation d'Active Directory.

**Forêt** : structure de niveau supérieur qui contient un ou plusieurs domaines associés.

**DNS** : système de résolution de noms utilisé notamment pour localiser les contrôleurs de domaine.

**Enregistrement SRV** : enregistrement DNS décrivant l'emplacement d'un service particulier.

**GPO** : objet de stratégie de groupe permettant d'appliquer des paramètres aux utilisateurs et aux ordinateurs concernés.

**Groupe de sécurité** : groupe d'identités qui peut être utilisé pour attribuer des autorisations.

**OU** : unité d'organisation servant à organiser les objets et à faciliter la délégation ou l'application des stratégies.

**Kerberos** : protocole d'authentification utilisé notamment dans les domaines Active Directory.

**LDAP** : protocole permettant d'accéder à des informations d'annuaire.

**Nom NetBIOS** : nom court utilisé dans certains contextes Windows, notamment pour la représentation du domaine.

**UPN** : User Principal Name, nom de connexion généralement présenté sous la forme `utilisateur@domaine`.

**DNS intégré à Active Directory** : configuration dans laquelle les données de certaines zones DNS sont stockées et répliquées au moyen d'Active Directory.

**DSRM** : Directory Services Restore Mode, mode destiné à certaines opérations de récupération d'Active Directory.

**Server Core** : option d'installation minimale de Windows Server sans interface de bureau traditionnelle.

**RSAT** : outils d'administration de serveur distant pour gérer des services Windows depuis une machine appropriée.

**Authentification** : vérification de l'identité présentée par un utilisateur ou un service.

**Autorisation** : détermination des opérations permises à une identité sur une ressource.

**Réplication Active Directory** : propagation des modifications de l'annuaire entre contrôleurs de domaine selon les mécanismes prévus.

## 36. Documentation officielle

Les fonctionnalités, interfaces et paramètres peuvent évoluer selon la version de Windows Server et l'édition du poste client. Consultez les pages correspondant à votre environnement.

### Windows Server

- Documentation Windows Server :  
  https://learn.microsoft.com/fr-fr/windows-server/

- Installation et gestion d'Active Directory Domain Services :  
  https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/deploy/install-active-directory-domain-services--level-100-

- Présentation d'Active Directory Domain Services :  
  https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/active-directory-domain-services

### DNS et contrôleurs de domaine

- Présentation de DNS pour Windows Server :  
  https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-overview

- DNS et Active Directory :  
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/dns-and-ad-ds

- Vérification des enregistrements DNS SRV :  
  https://learn.microsoft.com/fr-fr/troubleshoot/windows-server/networking/verify-srv-dns-records-have-been-created

- Localisation des contrôleurs de domaine :  
  https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/dc-locator

### Stratégies de groupe

- Présentation des stratégies de groupe :  
  https://learn.microsoft.com/fr-fr/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview

- Traitement des stratégies de groupe :  
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-processing

### Diagnostic

- Guide de résolution des problèmes de jonction au domaine :  
  https://learn.microsoft.com/fr-fr/troubleshoot/windows-server/identity/active-directory-domain-join-troubleshooting-guidance

- Diagnostic des erreurs réseau lors de la jonction à un domaine :  
  https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/domain-join-networking-errors

## Conclusion générale

Windows Server fournit les services qui permettent aux organisations de centraliser certaines fonctions informatiques. Active Directory rend possible une gestion structurée des identités, des ordinateurs, des groupes et des stratégies de domaine.

Pour bien débuter, il faut comprendre les relations entre l'adresse IP, DNS, le contrôleur de domaine, les utilisateurs et les stratégies de groupe. Ces composants doivent fonctionner ensemble pour que les postes puissent localiser le domaine, s'authentifier et accéder aux ressources.

La progression recommandée est la suivante :

```text
Installer et préparer Windows Server
              |
              v
Configurer le réseau et le DNS
              |
              v
Installer AD DS
              |
              v
Créer une forêt et un domaine
              |
              v
Créer les OU, utilisateurs et groupes
              |
              v
Joindre un poste client
              |
              v
Appliquer une GPO de test
              |
              v
Contrôler les permissions
              |
              v
Sécuriser et sauvegarder
              |
              v
Diagnostiquer les incidents
```

La compétence essentielle n'est pas seulement de réussir la promotion d'un contrôleur de domaine. Elle consiste à comprendre pourquoi DNS est nécessaire, comment les identités sont organisées, comment les permissions sont attribuées et comment vérifier l'état du système lorsque le domaine ne fonctionne plus comme prévu.

Ces connaissances constituent la base nécessaire pour aborder ensuite l'administration intermédiaire de Windows Server : DNS et DHCP approfondis, stratégies de groupe avancées, gestion des fichiers, délégation d'administration, PowerShell, réplication entre contrôleurs de domaine et supervision de l'infrastructure.