# Challenge d'architecture réseau — Cisco ACI Fabric Multi-Tenant

> **Fichier :** `challenge-fabric-aci-multi-tenant.md`
>
> **Domaine :** Cisco Application Centric Infrastructure (ACI), fabric leaf-spine, segmentation multi-tenant et sécurité applicative.
>
> **Progression :** Débutant → Intermédiaire → Expert.
>
> **Environnement :** datacenter hébergeant plusieurs départements, environnements applicatifs ou clients indépendants.
>
> **Technologies étudiées :** APIC, leaf-spine, VXLAN, Tenant, VRF, Bridge Domain, EPG, Application Profile, Contract, Filter, Subject, L3Out, External EPG, Shared Services, route leaking, RBAC et automatisation.
>
> **Objectif final :** concevoir, déployer, sécuriser et valider une fabric Cisco ACI dans laquelle plusieurs tenants peuvent coexister, être isolés et accéder uniquement aux services partagés explicitement autorisés.
>
> **Important :** les noms, adresses IP, VLAN et identifiants du scénario sont pédagogiques. Les fonctions disponibles, les possibilités de configuration et certains comportements dépendent de la version APIC, des commutateurs et des fonctionnalités activées.


# 1. Présentation du challenge

## 1.1. Contexte

Vous êtes ingénieur réseau et datacenter chez **NovaDC Services**, une entreprise qui exploite une infrastructure Cisco ACI pour héberger plusieurs environnements applicatifs.

Le datacenter accueille trois grandes catégories de ressources :

- Les applications de l'entreprise.
- Les applications de plusieurs clients hébergés.
- Les services communs nécessaires au fonctionnement de l'infrastructure.

La direction souhaite exploiter une seule fabric physique pour accueillir plusieurs environnements tout en maintenant une séparation stricte entre leurs réseaux et leurs politiques.

L'infrastructure actuelle présente plusieurs difficultés :

- Les applications sont réparties entre des VLAN historiques.
- Les règles de sécurité ne sont pas uniformes.
- Certaines machines accèdent à des services qui ne sont pas nécessaires à leur fonction.
- Les équipes veulent créer de nouveaux environnements sans modifier manuellement des dizaines de commutateurs.
- Les services DNS, NTP et de supervision doivent être partagés sans autoriser une communication générale entre tous les clients.
- La connectivité vers l'extérieur doit être contrôlée.
- Les administrateurs de certains tenants ne doivent pas pouvoir modifier les ressources d'autres tenants.
- Les changements de politique doivent être testables avant leur mise en production.

Votre mission est de construire une architecture ACI multi-tenant qui répond à ces exigences.

## 1.2. Objectifs métier

La solution doit permettre de :

1. Héberger plusieurs tenants dans une même fabric.
2. Isoler les réseaux des différents tenants.
3. Séparer les environnements de production et de test.
4. Contrôler les communications entre les EPG.
5. Publier certaines applications vers les réseaux externes.
6. Permettre à plusieurs tenants d'utiliser des services communs.
7. Maintenir une politique d'accès minimale.
8. Contrôler les routes apprises et annoncées par la fabric.
9. Simplifier l'exploitation grâce aux politiques centralisées dans APIC.
10. Limiter les risques lors des changements.
11. Automatiser certaines opérations de validation.
12. Produire des preuves démontrant l'isolation et la connectivité.

## 1.3. Scénario de référence

Le datacenter comprend les éléments suivants :

| Élément | Hypothèse de travail |
|---|---|
| Fabric | Cisco ACI |
| Topologie | Leaf-spine |
| Spines | 2 |
| Leafs de calcul | 2 |
| Leafs de bordure | 2 |
| Contrôleurs APIC | Cluster de 3 contrôleurs |
| Tenants applicatifs | 2 tenants principaux |
| Tenant partagé | `TENANT-COMMON` |
| Tenant de gestion des applications de test | Tenant supplémentaire optionnel |
| Clients | Alpha et Beta |
| Applications par client | Web, Application, Base de données |
| Services partagés | DNS, NTP, supervision et services d'infrastructure autorisés |
| Connectivité externe | L3Out vers un réseau d'entreprise ou un pare-feu |
| Sécurité est-ouest | Contrats ACI |
| Séparation du routage | VRF |
| Segmentation réseau | Bridge Domains et EPG |
| Infrastructure de calcul | Serveurs physiques et/ou hyperviseurs |
| Administration | RBAC et accès de gestion contrôlé |

Cette architecture est un laboratoire de conception. Les modèles précis de commutateurs, les capacités matérielles, les limites d'échelle et les versions logicielles doivent être vérifiés avant un déploiement réel.

## 1.4. Les objectifs techniques ne sont pas interchangeables

Dans ACI, plusieurs objets ont des responsabilités distinctes.

| Objet | Fonction principale |
|---|---|
| Tenant | Conteneur logique de configuration et de politiques, avec séparation administrative |
| VRF | Contexte de routage IP |
| Bridge Domain | Domaine de couche 2 logique, associé à un contexte VRF et à des paramètres réseau |
| Subnet du BD | Adresse de passerelle ou autre préfixe associé au Bridge Domain, selon le besoin |
| Application Profile | Organisation des composants d'une application |
| EPG | Groupe d'endpoints auquel une politique commune est appliquée |
| Contract | Définition d'une relation de communication autorisée |
| Filter | Critères de trafic correspondant au contrat |
| Subject | Association d'un contrat à des filtres et à des comportements |
| L3Out | Connectivité routée entre la fabric et des réseaux extérieurs |
| External EPG | Classification des réseaux ou préfixes externes utilisés dans la politique |
| APIC | Plan de gestion et de programmation des politiques ACI |

La qualité de l'architecture dépend de la bonne association de ces objets.


# 2. Progression des niveaux

## Niveau 1 — Débutant : construire une fabric et un tenant

Vous devez :

- Comprendre la topologie leaf-spine.
- Identifier les fonctions APIC, leaf et spine.
- Créer un tenant.
- Créer une VRF.
- Créer les Bridge Domains.
- Associer les sous-réseaux nécessaires.
- Créer une Application Profile.
- Créer des EPG.
- Associer les EPG aux domaines et aux ports physiques ou virtuels.
- Tester la connectivité.
- Comprendre le comportement par défaut des politiques.

**Livrable :** une fabric de laboratoire avec un tenant fonctionnel, un plan IP et un schéma logique.

## Niveau 2 — Intermédiaire : sécuriser plusieurs tenants

Vous devez :

- Créer deux tenants indépendants.
- Isoler les VRF.
- Définir des contrats entre les EPG.
- Contrôler les flux applicatifs.
- Configurer un L3Out.
- Contrôler les routes externes.
- Publier une application.
- Concevoir des services partagés.
- Étudier le route leaking inter-VRF.
- Tester des communications autorisées et interdites.
- Gérer les rôles administratifs.

**Livrable :** une fabric multi-tenant avec segmentation, contrats, connectivité externe et services partagés contrôlés.

## Niveau 3 — Expert : concevoir une architecture exploitable à grande échelle

Vous devez :

- Concevoir une convention de nommage et de gestion des tenants.
- Comparer plusieurs stratégies de VRF.
- Concevoir la séparation des environnements.
- Étudier les contrats globaux et les risques de portée.
- Contrôler le partage de L3Out.
- Analyser les mécanismes de route leaking.
- Examiner les effets des changements de politique.
- Automatiser la validation.
- Construire une procédure d'incident.
- Étudier les dépendances entre RBAC, routage et sécurité.
- Présenter une architecture cible documentée et des recommandations de production.

**Livrable :** un dossier complet de conception ACI multi-tenant, comprenant une matrice de flux, une stratégie de partage, un plan de tests et un plan de retour arrière.


# 3. Architecture 1 — Fabric physique Cisco ACI

Avant de configurer les tenants, il faut comprendre l'infrastructure physique qui porte les politiques.

## 3.1. Topologie générale

Le scénario comporte deux spines et quatre leafs.

Les deux premiers leafs raccordent les serveurs et hyperviseurs. Les deux autres leafs assurent notamment la connectivité externe.

```text
                      +------------------+
                      |     SPINE-01     |
                      +------------------+
                         |  |  |  |
                         |  |  |  |
                      +------------------+
                      |     SPINE-02     |
                      +------------------+
                         |  |  |  |
                         |  |  |  |
        +----------------+  |  |  +----------------+
        |                   |  |                   |
        v                   v  v                   v

   +-------------+    +-------------+        +-------------+
   | LEAF-101    |    | LEAF-102    |        | LEAF-201    |
   | COMPUTE-A   |    | COMPUTE-B   |        | BORDER-A    |
   +-------------+    +-------------+        +-------------+
         |                  |                       |
         |                  |                       |
         v                  v                       |
     Serveurs A         Serveurs B                  |
                                                    |
                                              Réseau externe
                                                    |
                                              Pare-feu / WAN


                     +-------------+
                     | LEAF-202    |
                     | BORDER-B    |
                     +-------------+
                           |
                      Réseau externe
```

**Règle physique du modèle leaf-spine :** chaque leaf de la fabric doit disposer des liaisons vers les spines prévues par l'architecture. Les liaisons ne doivent pas être interprétées comme une chaîne dans laquelle les leafs transiteraient les uns par les autres.

Le schéma doit être complété, dans le dossier final, par une représentation de chaque lien leaf-spine.

## 3.2. Rôle des spines

Les spines assurent le transit de la fabric entre les leafs.

Ils ne servent généralement pas à raccorder directement les serveurs de l'application dans cette architecture.

Les fonctions attendues comprennent :

- Le transport du trafic de la fabric.
- La redondance des chemins.
- La connectivité vers les leafs.
- Le support des mécanismes de fabric requis par ACI.

Ne transposez pas directement un plan de configuration NX-OS autonome vers un commutateur ACI. La fabric ACI utilise des objets et politiques pilotés par APIC ainsi que des mécanismes propres à son architecture.

## 3.3. Rôle des leafs de calcul

Les leafs de calcul raccordent :

- Les serveurs physiques.
- Les hyperviseurs.
- Les appliances applicatives.
- Certains équipements de service.

Ils participent à l'application des politiques ACI sur le trafic des endpoints.

Un serveur peut être associé à un EPG par un déploiement statique sur un chemin physique ou par une intégration à un domaine de virtualisation compatible.

L'affectation doit correspondre au port, au domaine, à l'encapsulation VLAN et à l'EPG attendus.

## 3.4. Rôle des border leafs

Les border leafs hébergent les connexions vers les réseaux externes définies par les objets L3Out.

Ils peuvent établir des relations de routage avec :

- Un pare-feu externe.
- Un réseau de campus.
- Un backbone IP.
- Un routeur de fournisseur.
- Une autre infrastructure de datacenter.

Le choix entre routes statiques, OSPF, BGP ou un autre mécanisme dépend du type de connexion et des capacités de l'équipement externe.

Les border leafs ne sont pas automatiquement des pare-feu. Les fonctions de routage et les politiques ACI ne remplacent pas toutes les fonctions de sécurité d'un pare-feu dédié lorsque celui-ci est nécessaire.

## 3.5. Rôle des contrôleurs APIC

APIC constitue le plan de gestion de la fabric.

Il permet notamment :

- De créer les tenants et politiques.
- De définir les VRF et Bridge Domains.
- De créer les EPG et leurs relations.
- De configurer les contrats.
- De gérer les connexions L3Out.
- De définir les politiques d'accès aux ports.
- De gérer les intégrations prises en charge.
- De superviser l'état de la fabric et de ses objets.

APIC ne doit pas être considéré comme un commutateur de transit pour le trafic de production. Les équipements de fabric effectuent le transfert des paquets dans le plan de données.

Pour ce scénario, un cluster de trois APIC est proposé afin de fournir un plan de gestion adapté à une infrastructure d'entreprise. Le dimensionnement exact doit tenir compte de la version APIC, des recommandations du constructeur et de l'échelle de la fabric.

## 3.6. Connectivité de gestion

L'administration des contrôleurs, commutateurs et systèmes doit être séparée des réseaux des applications.

Il faut définir :

- Les interfaces de gestion utilisées.
- Les chemins d'accès OOB et, si nécessaire, in-band.
- Les sources autorisées.
- Les comptes.
- Les rôles RBAC.
- Les journaux.
- Les mécanismes d'authentification.
- Les conditions de reprise lorsque l'accès principal est indisponible.

Le réseau OOB doit être conçu comme un chemin distinct lorsqu'une véritable isolation physique est exigée. Le simple fait d'utiliser une adresse IP différente ne crée pas à lui seul une séparation physique.


# 4. Architecture 2 — Modèle logique multi-tenant

Le modèle logique ACI organise les réseaux et politiques dans des tenants.

## 4.1. Les tenants du scénario

Nous allons utiliser trois tenants :

- `TENANT-ALPHA` : environnement applicatif du client Alpha.
- `TENANT-BETA` : environnement applicatif du client Beta.
- `TENANT-COMMON` : services partagés dont l'utilisation est explicitement autorisée.

Les trois tenants sont hébergés dans la même fabric physique.

```text
                  FABRIC CISCO ACI
                         |
         +---------------+---------------+
         |               |               |
         v               v               v

 +---------------+ +---------------+ +----------------+
 | TENANT-ALPHA  | | TENANT-BETA   | | TENANT-COMMON  |
 +---------------+ +---------------+ +----------------+
         |               |               |
         v               v               v
   Applications     Applications     Services partagés
   Client Alpha     Client Beta      DNS / NTP / outils
```

Un tenant représente un conteneur logique de configuration et une frontière de gestion des politiques. Il ne constitue pas, à lui seul, une table de routage IP isolée distincte.

La séparation du trafic repose notamment sur les VRF, Bridge Domains, EPG, contrats et les mécanismes de routage configurés.

## 4.2. Pourquoi séparer les clients en tenants ?

Le tenant permet d'organiser la configuration et les responsabilités.

Dans cet exercice, Alpha et Beta ne doivent pas pouvoir :

- Consulter la configuration interne de l'autre tenant au-delà des droits qui leur sont attribués.
- Atteindre les réseaux privés de l'autre client sans autorisation explicite.
- Modifier les contrats de l'autre tenant.
- Accéder aux données ou applications de l'autre client.
- Modifier les ressources communes.
- Contourner les règles de sécurité au moyen d'une modification administrative.

Il faut toutefois distinguer deux objectifs :

**Isolation administrative :** qui peut créer, modifier ou supprimer des objets de configuration.

**Isolation du plan de données :** quels paquets peuvent réellement circuler entre les endpoints.

Les rôles d'administration et les politiques de trafic doivent être conçus séparément puis validés ensemble.

## 4.3. Hiérarchie logique d'un tenant

La structure conceptuelle suivante est utile pour comprendre les relations entre les objets.

```text
TENANT-ALPHA
    |
    +-- VRF-ALPHA-PROD
    |       |
    |       +-- BD-ALPHA-WEB
    |       |       |
    |       |       +-- Subnet / Gateway
    |       |
    |       +-- BD-ALPHA-APP
    |       |       |
    |       |       +-- Subnet / Gateway
    |       |
    |       +-- BD-ALPHA-DB
    |               |
    |               +-- Subnet / Gateway
    |
    +-- Application Profile : AP-ALPHA
            |
            +-- EPG-ALPHA-WEB
            |
            +-- EPG-ALPHA-APP
            |
            +-- EPG-ALPHA-DB
```

L'Application Profile organise les EPG applicatifs. Chaque EPG est associé à un Bridge Domain. Le Bridge Domain est associé à une VRF.

Ce schéma est conceptuel. Les attributs et associations exacts doivent être réalisés à partir du modèle d'objets de la version ACI utilisée.


# 5. Défi 1 — Comprendre Tenant, VRF, BD et EPG

Cette section est fondamentale. La suite du challenge suppose que les différences entre ces objets sont comprises.

## 5.1. Tenant

Le Tenant est un conteneur logique dans lequel les politiques et ressources d'une organisation sont regroupées.

Il peut représenter :

- Un client hébergé.
- Un département.
- Un environnement administratif.
- Un ensemble de services gérés par une équipe.
- Une zone d'administration distincte.

Un tenant ne doit pas automatiquement être assimilé à un unique réseau IP.

## 5.2. VRF

La VRF définit le contexte de routage.

Elle permet notamment de maintenir des tables de routage distinctes. Deux VRF différentes peuvent utiliser des préfixes IP identiques, car ces routes appartiennent à des contextes de routage distincts.

Cependant, dès que des communications entre VRF sont nécessaires, la conception doit prévoir les routes et les règles qui autorisent ces échanges.

Le fait de créer deux VRF n'autorise pas automatiquement les paquets à passer de l'une à l'autre.

## 5.3. Bridge Domain

Le Bridge Domain représente un domaine de couche 2 logique et possède des paramètres réseau associés.

Il est rattaché à une VRF pour le routage IP associé. Il peut également définir un sous-réseau qui sert notamment de passerelle pour les endpoints.

Le BD joue un rôle dans la connectivité réseau, tandis que l'EPG porte l'appartenance logique des endpoints et la politique appliquée à ceux-ci.

Un Bridge Domain et un EPG ne sont donc pas le même objet.

## 5.4. EPG

Un Endpoint Group regroupe des endpoints auxquels une politique commune s'applique.

Les endpoints peuvent être classés au moyen de mécanismes supportés par la plateforme, par exemple :

- Une affectation statique de chemin.
- Une intégration à un domaine de virtualisation.
- D'autres mécanismes de classification pris en charge.

L'EPG n'est pas simplement une étiquette descriptive. Il participe à l'identification des groupes de source et de destination utilisés par les politiques ACI.

## 5.5. Application Profile

L'Application Profile organise les EPG représentant les composants d'une application.

Pour une application à trois niveaux :

- EPG Web.
- EPG Application.
- EPG Base de données.

Cette organisation permet de définir et de documenter les relations entre les composants.

L'Application Profile ne remplace pas la VRF ni le Bridge Domain.

## 5.6. Contract

Le contrat définit une relation de communication entre des groupes de endpoints.

Il s'appuie sur des filtres et des sujets afin de déterminer le trafic concerné et l'action appliquée.

Dans le modèle ACI avec enforcement, les EPG ne doivent pas être considérés comme autorisés à communiquer librement entre eux simplement parce qu'ils appartiennent au même tenant.

Les options comme le mode unenforced, le Preferred Group ou `vzAny` ont des effets particuliers et doivent être utilisées en connaissance de cause.

## 5.7. Tableau récapitulatif

| Objet | Question à laquelle il répond |
|---|---|
| Tenant | Dans quel conteneur logique et administratif place-t-on la configuration ? |
| VRF | Dans quel contexte de routage se trouve la destination ? |
| Bridge Domain | Quel domaine L2 et quels paramètres réseau sont associés au segment ? |
| EPG | À quel groupe de politique appartient l'endpoint ? |
| Application Profile | Comment organise-t-on les EPG d'une application ? |
| Contract | Quels échanges entre groupes sont autorisés ? |
| Filter | Quels protocoles, ports et critères de trafic sont concernés ? |
| Subject | Comment les filtres et comportements sont-ils regroupés dans un contrat ? |
| L3Out | Comment la fabric communique-t-elle avec un réseau routé externe ? |
| External EPG | Comment le trafic externe est-il classifié pour les politiques et routes ? |

### Exercice obligatoire

Expliquez avec vos propres mots la différence entre :

1. Un Tenant et une VRF.
2. Une VRF et un Bridge Domain.
3. Un Bridge Domain et un EPG.
4. Un EPG et un Application Profile.
5. Un Contract et un Filter.
6. Une isolation administrative et une isolation du trafic.

Vous ne devez pas passer au niveau intermédiaire tant que vous ne pouvez pas expliquer ces différences à l'aide d'un schéma cohérent.


# 6. Architecture 3 — Plan d'adressage multi-tenant

Le plan IP doit être cohérent avec la segmentation logique et les besoins de routage.

Pour éviter les ambiguïtés au début du challenge, les réseaux des trois tenants utilisent des préfixes distincts.

## 6.1. Plan IP de référence

### Tenant Alpha

| Bridge Domain | EPG associé | Sous-réseau | Passerelle illustrative |
|---|---|---|---|
| `BD-ALPHA-WEB` | `EPG-ALPHA-WEB` | `10.101.10.0/24` | `10.101.10.1` |
| `BD-ALPHA-APP` | `EPG-ALPHA-APP` | `10.101.20.0/24` | `10.101.20.1` |
| `BD-ALPHA-DB` | `EPG-ALPHA-DB` | `10.101.30.0/24` | `10.101.30.1` |

### Tenant Beta

| Bridge Domain | EPG associé | Sous-réseau | Passerelle illustrative |
|---|---|---|---|
| `BD-BETA-WEB` | `EPG-BETA-WEB` | `10.102.10.0/24` | `10.102.10.1` |
| `BD-BETA-APP` | `EPG-BETA-APP` | `10.102.20.0/24` | `10.102.20.1` |
| `BD-BETA-DB` | `EPG-BETA-DB` | `10.102.30.0/24` | `10.102.30.1` |

### Tenant Common

| Bridge Domain | EPG associé | Sous-réseau | Passerelle illustrative |
|---|---|---|---|
| `BD-COMMON-DNS` | `EPG-COMMON-DNS` | `10.100.10.0/24` | `10.100.10.1` |
| `BD-COMMON-NTP` | `EPG-COMMON-NTP` | `10.100.20.0/24` | `10.100.20.1` |
| `BD-COMMON-MONITORING` | `EPG-COMMON-MONITORING` | `10.100.30.0/24` | `10.100.30.1` |

Ce plan est destiné au laboratoire. Les adresses de passerelle doivent être créées et associées aux Bridge Domains selon les fonctionnalités et options de configuration de la version utilisée.

## 6.2. Plan logique consolidé

```text
TENANT-ALPHA
  VRF-ALPHA-PROD
    10.101.10.0/24  WEB
    10.101.20.0/24  APP
    10.101.30.0/24  DB

TENANT-BETA
  VRF-BETA-PROD
    10.102.10.0/24  WEB
    10.102.20.0/24  APP
    10.102.30.0/24  DB

TENANT-COMMON
  VRF-COMMON
    10.100.10.0/24  DNS
    10.100.20.0/24  NTP
    10.100.30.0/24  MONITORING
```

Les trois VRF sont indépendantes dans le modèle de référence.

Les services communs ne sont accessibles qu'au travers des mécanismes de partage prévus. Une simple ressemblance d'adresse IP ou de nom de service n'établit aucune connectivité entre VRF.

## 6.3. Vérifications du plan IP

Vous devez confirmer :

- L'absence de chevauchement entre préfixes qui doivent être routés ensemble.
- L'unicité des passerelles.
- L'association des BD aux VRF correctes.
- La cohérence entre EPG et BD.
- La cohérence des paramètres d'adressage.
- La présence des routes attendues.
- L'absence de routes partagées non prévues.
- Le comportement lorsque deux VRF sont isolées.

Dans une architecture multi-tenant, des préfixes qui se chevauchent peuvent être acceptables dans des VRF distinctes. Toutefois, leur utilisation devient plus complexe si une connectivité partagée, un L3Out ou des routes importées les relient.

Pour ce challenge, conservez des préfixes uniques, sauf dans un exercice spécifique sur les chevauchements et le route leaking.


# 7. Défi 2 — Concevoir les tenants Alpha et Beta

Chaque tenant possède une application à trois niveaux :

1. Web.
2. Application.
3. Base de données.

Les trois niveaux ne doivent pas communiquer librement.

## 7.1. Structure du tenant Alpha

```text
TENANT-ALPHA
    |
    +-- VRF-ALPHA-PROD
    |       |
    |       +-- BD-ALPHA-WEB
    |       |       Subnet : 10.101.10.0/24
    |       |
    |       +-- BD-ALPHA-APP
    |       |       Subnet : 10.101.20.0/24
    |       |
    |       +-- BD-ALPHA-DB
    |               Subnet : 10.101.30.0/24
    |
    +-- AP-ALPHA
            |
            +-- EPG-ALPHA-WEB
            |
            +-- EPG-ALPHA-APP
            |
            +-- EPG-ALPHA-DB
```

## 7.2. Structure du tenant Beta

```text
TENANT-BETA
    |
    +-- VRF-BETA-PROD
    |       |
    |       +-- BD-BETA-WEB
    |       |       Subnet : 10.102.10.0/24
    |       |
    |       +-- BD-BETA-APP
    |       |       Subnet : 10.102.20.0/24
    |       |
    |       +-- BD-BETA-DB
    |               Subnet : 10.102.30.0/24
    |
    +-- AP-BETA
            |
            +-- EPG-BETA-WEB
            |
            +-- EPG-BETA-APP
            |
            +-- EPG-BETA-DB
```

Les deux tenants possèdent une structure comparable, mais les noms, préfixes, politiques et associations doivent rester distincts.

Il ne faut pas copier une configuration d'un tenant vers l'autre sans vérifier les noms des objets, les ports, les domaines, les règles de sécurité et les adresses IP.

## 7.3. Politique de communication de chaque application

Le modèle attendu est le suivant :

```text
                    TENANT ALPHA

     +------------+       +------------+       +------------+
     | EPG-WEB     | ----> | EPG-APP     | ----> | EPG-DB      |
     +------------+       +------------+       +------------+
          |                     |                     |
       HTTPS                API autorisée         SQL autorisé

       Autres flux non prévus : bloqués selon le modèle
       de politique et la configuration effective.


                    TENANT BETA

     +------------+       +------------+       +------------+
     | EPG-WEB     | ----> | EPG-APP     | ----> | EPG-DB      |
     +------------+       +------------+       +------------+
          |                     |                     |
       HTTPS                API autorisée         SQL autorisé

       Aucun accès implicite aux EPG d'Alpha.
```

Les flèches représentent les communications initiées qui sont autorisées par la politique. Les exigences de trafic retour, les éventuels protocoles supplémentaires et les règles précises doivent être définis dans les contrats et validés sur la plateforme.

## 7.4. Politique d'isolation entre tenants

Par défaut, Alpha ne doit pas accéder aux ressources de Beta.

Beta ne doit pas accéder aux ressources d'Alpha.

Cette interdiction doit être vérifiée au niveau du plan de données. La simple existence de deux tenants dans APIC n'est pas une preuve suffisante.

### Tests attendus

Depuis une VM Alpha :

- Accès aux services Alpha autorisés.
- Accès aux bases Alpha seulement selon la politique.
- Accès aux services communs uniquement selon les contrats prévus.
- Tentative d'accès aux services Beta : refusée.

Depuis une VM Beta :

- Accès aux services Beta autorisés.
- Accès aux services communs uniquement selon les contrats prévus.
- Tentative d'accès aux services Alpha : refusée.

Vous devez documenter le chemin réellement emprunté et l'endroit où la politique est appliquée.


# 8. Architecture 4 — Segmentation des applications avec EPG et Contracts

## 8.1. Pourquoi utiliser des EPG ?

Les EPG permettent d'associer des endpoints à des groupes de politique.

Dans un modèle applicatif, les groupes peuvent correspondre à des fonctions :

- Frontend.
- Serveur applicatif.
- Base de données.
- Services d'administration.
- Supervision.

Cette approche est différente d'une simple segmentation par adresses IP.

Un groupe de endpoints partage une politique. L'appartenance à un EPG dépend des mécanismes de classification et d'association prévus dans ACI.

## 8.2. Exemple d'une application à trois niveaux

Le scénario Alpha utilise les EPG suivants :

| EPG | Rôle | BD | Sous-réseau |
|---|---|---|---|
| `EPG-ALPHA-WEB` | Frontend | `BD-ALPHA-WEB` | `10.101.10.0/24` |
| `EPG-ALPHA-APP` | API / logique métier | `BD-ALPHA-APP` | `10.101.20.0/24` |
| `EPG-ALPHA-DB` | Base de données | `BD-ALPHA-DB` | `10.101.30.0/24` |

## 8.3. Modèle de contrat

Le contrat définit les échanges autorisés entre des EPG consommateurs et fournisseurs.

Dans notre convention :

- L'EPG Web consomme le contrat Web-vers-Application.
- L'EPG Application fournit ce contrat.
- L'EPG Application consomme le contrat Application-vers-Base.
- L'EPG Base fournit ce contrat.

Schéma :

```text
EPG-ALPHA-WEB
      |
      | Consomme : CT-WEB-APP
      v
EPG-ALPHA-APP
      |
      | Consomme : CT-APP-DB
      v
EPG-ALPHA-DB
```

Cette notation représente les relations consumer/provider. Les paramètres du contrat, les filtres et les comportements doivent correspondre au trafic nécessaire.

## 8.4. Contrats de référence

| Contrat | Consumer | Provider | Flux principal | Filtre indicatif |
|---|---|---|---|---|
| `CT-ALPHA-WEB-APP` | EPG Web | EPG Application | Requêtes Web vers API | Port réel de l'API |
| `CT-ALPHA-APP-DB` | EPG Application | EPG Base | Application vers base | TCP 5432 dans cet exemple |
| `CT-BETA-WEB-APP` | EPG Web Beta | EPG Application Beta | Requêtes Web vers API | Port réel de l'API |
| `CT-BETA-APP-DB` | EPG Application Beta | EPG Base Beta | Application vers base | TCP 5432 dans cet exemple |

Le port TCP 5432 est utilisé ici comme exemple pour une application utilisant PostgreSQL. Il ne s'agit pas d'un port obligatoire pour toutes les bases de données.

Les filtres doivent être construits à partir des besoins réels de l'application. N'autorisez pas tous les ports simplement pour éviter d'avoir à connaître les dépendances.

## 8.5. Contrats et filtrage par défaut

Dans une VRF où l'enforcement est activé, les communications entre EPG dépendent des politiques configurées.

Les options ACI telles que :

- Unenforced mode.
- Preferred Group.
- `vzAny`.
- Contract scope.
- Inheritance.

doivent être comprises avant d'être utilisées.

Elles ne sont pas interchangeables et peuvent modifier la portée ou la manière dont la politique est appliquée.

Pour ce challenge, conservez un modèle restrictif et utilisez des contrats explicites entre les EPG qui doivent communiquer.

## 8.6. Exercice

Pour chaque contrat, renseignez :

| Champ | Description |
|---|---|
| Nom | Identifiant unique |
| Tenant | Tenant propriétaire du contrat |
| Consumer | EPG qui initie la communication selon la politique |
| Provider | EPG qui offre le service |
| Scope | Portée du contrat |
| Filter | Critères réseau autorisés |
| Subject | Filtres et comportements associés |
| Justification | Besoin applicatif |
| Test positif | Communication qui doit fonctionner |
| Test négatif | Communication qui doit être refusée |
| Preuve | Résultat de test et journaux |


# 9. Défi 3 — Séparer l'administration et le trafic applicatif

La politique d'administration est distincte de la politique de communication entre applications.

## 9.1. Architecture de gestion

Les administrateurs doivent pouvoir gérer les équipements sans rendre les interfaces de gestion accessibles à tous les endpoints.

Schéma :

```text
                  ADMINISTRATEUR ACI
                          |
                          v
                  POSTE D'ADMINISTRATION
                          |
                  Authentification contrôlée
                          |
                          v
                       APIC
                          |
             +------------+-------------+
             |            |             |
             v            v             v
          Politiques    Leafs         Spines
```

Le chemin d'administration des APIC et celui des endpoints de production doivent être identifiés séparément.

L'accès administratif doit être limité aux personnes et rôles autorisés.

## 9.2. RBAC

Le Role-Based Access Control, ou contrôle d'accès fondé sur les rôles, détermine quelles opérations de gestion une personne ou une équipe peut effectuer.

Exemples de rôles à définir :

- Administrateur global de la fabric.
- Administrateur réseau Alpha.
- Administrateur réseau Beta.
- Opérateur de supervision.
- Auditeur.
- Équipe responsable des services communs.

La capacité d'un utilisateur à modifier une configuration ne doit pas être déduite uniquement du fait qu'il appartient à un tenant applicatif.

Le dossier doit préciser les utilisateurs, rôles, domaines de ressources et opérations autorisées.

## 9.3. Matrice RBAC de référence

| Rôle | Tenant Alpha | Tenant Beta | Tenant Common | Configuration de fabric |
|---|---|---|---|---|
| Administrateur global | Gestion selon le rôle | Gestion selon le rôle | Gestion selon le rôle | Selon les autorisations globales |
| Admin Alpha | Gestion autorisée | Pas de gestion | Pas de gestion des politiques | Pas de gestion globale par défaut |
| Admin Beta | Pas de gestion | Gestion autorisée | Pas de gestion des politiques | Pas de gestion globale par défaut |
| Admin Common | Pas de gestion directe par défaut | Pas de gestion directe par défaut | Gestion des services partagés | Pas de gestion globale par défaut |
| Opérateur supervision | Lecture limitée | Lecture limitée | Lecture des outils | Lecture selon la mission |
| Auditeur | Lecture approuvée | Lecture approuvée | Lecture approuvée | Lecture approuvée |

Cette matrice est illustrative. Les rôles effectifs doivent être traduits dans le modèle RBAC disponible, avec des restrictions adaptées à la version APIC et à l'organisation.

## 9.4. Tests RBAC

Avec des comptes de test distincts :

1. Connectez-vous en tant qu'administrateur Alpha.
2. Vérifiez qu'il peut réaliser les opérations autorisées sur Alpha.
3. Vérifiez qu'il ne peut pas modifier les objets Beta.
4. Vérifiez qu'il ne peut pas modifier les politiques globales non autorisées.
5. Répétez les contrôles avec l'administrateur Beta.
6. Testez le rôle de lecture.
7. Vérifiez les journaux et événements d'audit.

Ne faites pas ces essais en modifiant des objets de production sans une procédure de test et une méthode de retour arrière.


# 10. Défi 4 — Configurer les domaines d'accès et l'association des ports

Créer un EPG ne suffit pas à placer automatiquement un serveur dans cet EPG.

Le chemin d'accès doit être associé à l'EPG au moyen d'un mécanisme pris en charge par l'environnement.

## 10.1. Les objets d'accès

Les objets impliqués peuvent comprendre :

- VLAN Pool.
- Physical Domain ou VMM Domain.
- Attachable Access Entity Profile (AAEP).
- Interface Policy Group.
- Interface Profile.
- Switch Profile.
- Static Path Binding.
- Configuration d'intégration de virtualisation.

Les noms et associations exacts dépendent du modèle de configuration ACI utilisé.

## 10.2. Schéma des associations

```text
                     TENANT
                       |
                 Application Profile
                       |
                      EPG
                       |
              Association au domaine
                       |
                 VLAN / Encapsulation
                       |
                Chemin statique ou VMM
                       |
                   Port du leaf
                       |
                     Serveur
```

Le chemin d'accès physique et l'appartenance au groupe de politique sont deux éléments à valider.

## 10.3. Déployer un serveur dans `EPG-ALPHA-APP`

Le serveur applicatif doit être raccordé à un leaf, sur un port configuré pour son usage.

Vous devez confirmer :

1. Le leaf et le port corrects.
2. Le mode de connexion.
3. Le VLAN d'encapsulation attendu.
4. L'association au domaine correct.
5. L'AAEP appliqué.
6. Le chemin statique ou l'intégration VMM.
7. Le BD lié à l'EPG.
8. Le sous-réseau prévu.
9. La classification de l'endpoint.
10. Les contrats fournis et consommés.

Un port attaché au mauvais EPG peut provoquer un mélange de politiques ou une absence de connectivité.

## 10.4. Exercice de diagnostic

Un serveur est physiquement raccordé et son interface est active, mais il n'est pas accessible comme prévu.

Vérifiez :

- L'état du port.
- Le chemin de déploiement.
- Le VLAN d'encapsulation.
- Le domaine d'accès.
- Le pool VLAN.
- L'AAEP.
- Le Static Path Binding ou l'association au domaine VMM.
- L'EPG.
- Le BD.
- La VRF.
- Les contrats.
- Les éventuelles erreurs d'adresse IP.

Ne concluez pas qu'un problème provient forcément du contrat : un endpoint mal classé peut produire des symptômes semblables.


# 11. Architecture 5 — Services partagés entre tenants

Les services communs doivent pouvoir être utilisés par les tenants qui en ont besoin, sans donner à ces derniers un accès général à toutes les ressources partagées.

Le scénario utilise un tenant `TENANT-COMMON`.

## 11.1. Services partagés proposés

| Service | Fonction | Accès nécessaire |
|---|---|---|
| DNS | Résolution de noms | Requêtes autorisées depuis les réseaux approuvés |
| NTP | Synchronisation de l'heure | Requêtes depuis les systèmes autorisés |
| Supervision | Collecte des mesures | Sources et protocoles explicitement définis |
| Services d'identité | Authentification, selon l'architecture | Accès strictement contrôlé |
| Dépôt de logiciels | Distribution des paquets approuvés | Clients et protocoles autorisés |
| Journalisation | Centralisation des événements | Agents, API et endpoints autorisés |

Les flux à prévoir varient selon le service. N'autorisez pas l'ensemble des ports d'un serveur simplement parce qu'il héberge plusieurs fonctions.

## 11.2. Schéma de partage

```text
                     TENANT-COMMON
                            |
                    +----------------+
                    | VRF-COMMON     |
                    +----------------+
                            |
             +--------------+---------------+
             |              |               |
             v              v               v
         EPG-DNS         EPG-NTP        EPG-MONITORING
             |              |               |
             +--------------+---------------+
                            |
                     Contrats de partage
                            |
          +-----------------+-----------------+
          |                                   |
          v                                   v
     TENANT-ALPHA                        TENANT-BETA
          |                                   |
     EPGs autorisés                      EPGs autorisés
```

Le schéma montre les relations de politique souhaitées, pas une connectivité automatique entre les VRF.

Les méthodes de partage doivent être définies selon le type de service, la version APIC et le comportement de routage voulu.

## 11.3. Contrats partagés de référence

| Contrat | Provider | Consumers | Flux |
|---|---|---|---|
| `CT-COMMON-DNS` | `EPG-COMMON-DNS` | EPGs Alpha et Beta autorisés | Requêtes DNS |
| `CT-COMMON-NTP` | `EPG-COMMON-NTP` | EPGs autorisés | Synchronisation NTP |
| `CT-COMMON-MONITORING` | `EPG-COMMON-MONITORING` ou modèle de collecte adapté | Agents et endpoints selon le modèle | Flux de supervision définis |

La direction des contrats doit correspondre à la communication réellement initiée.

Pour la supervision, par exemple, la politique peut être différente selon que le collecteur interroge les endpoints ou que les agents envoient eux-mêmes leurs métriques.

## 11.4. Exercice

Pour chaque service commun :

1. Identifiez les tenants consommateurs.
2. Identifiez les EPG consommateurs.
3. Identifiez l'EPG fournisseur.
4. Définissez les filtres.
5. Choisissez la portée du contrat.
6. Déterminez si un partage entre VRF est nécessaire.
7. Déterminez si un partage d'adresses ou de routes est nécessaire.
8. Vérifiez le chemin aller et le chemin retour.
9. Testez les flux autorisés.
10. Testez les flux non autorisés.


# 12. Défi intermédiaire — Route leaking inter-VRF

Cette partie doit être abordée après la compréhension des contrats et des VRF.

Un contrat et un partage de routes sont deux aspects liés mais distincts. Dans les architectures ACI inter-VRF, une politique de contrat appropriée ne suffit pas nécessairement, à elle seule, à rendre les préfixes du réseau fournisseur accessibles dans une autre VRF.

Le partage des services doit être conçu au moyen des fonctions prévues par la plateforme, notamment les paramètres de sous-réseaux partagés et de route leaking lorsqu'ils sont nécessaires.

La configuration exacte doit être vérifiée dans la documentation APIC de la version utilisée.

## 12.1. Cas de laboratoire

Alpha et Beta doivent utiliser le service DNS de `TENANT-COMMON`.

Les VRF sont distinctes :

- `VRF-ALPHA-PROD`
- `VRF-BETA-PROD`
- `VRF-COMMON`

Le service DNS est situé dans `VRF-COMMON`.

Schéma :

```text
                  VRF-ALPHA-PROD
                         |
                   EPG Alpha autorisé
                         |
                  Contrat de partage
                         |
                         v
                    VRF-COMMON
                         |
                    EPG-COMMON-DNS
                         |
                     Service DNS
                         ^
                         |
                  Contrat de partage
                         |
                   EPG Beta autorisé
                         |
                    VRF-BETA-PROD
```

Cette représentation illustre l'intention du partage. Le routage inter-VRF et la politique de trafic doivent tous les deux être correctement mis en place.

## 12.2. Questions à résoudre

1. Le service et les consommateurs sont-ils dans la même VRF ?
2. Un mécanisme de partage de routes est-il nécessaire ?
3. Le sous-réseau du service peut-il être partagé selon l'architecture retenue ?
4. Quel est le scope du contrat ?
5. Le fournisseur et les consommateurs sont-ils dans le même tenant ?
6. Le partage traverse-t-il plusieurs tenants ?
7. Comment les routes sont-elles rendues accessibles ?
8. Où la politique est-elle appliquée ?
9. Quel chemin emprunte le trafic retour ?
10. Comment éviter de partager d'autres préfixes ?

## 12.3. Attention à la portée du contrat

ACI offre différentes portées de contrat, dont les portées Application, VRF, Tenant et Global, selon la fonction et la version utilisées.

Leur effet varie. Une portée plus large peut permettre une réutilisation de politique plus importante, mais elle augmente également le risque d'autoriser involontairement des communications entre groupes qui ne devraient pas communiquer.

La portée doit être choisie intentionnellement.

Ne définissez pas un contrat Global simplement pour contourner un problème de connectivité sans vérifier :

- Les EPG consommateurs.
- Les EPG fournisseurs.
- Les VRF.
- Le besoin de route leaking.
- Les sous-réseaux concernés.
- Les autres objets qui pourraient réutiliser le même contrat.

## 12.4. Validation du partage

Pour chaque partage inter-VRF, fournissez les preuves suivantes :

- Contrat présent et associé correctement.
- Filtres correspondant aux flux attendus.
- Routes nécessaires disponibles.
- Paramètres de partage cohérents.
- Trafic aller fonctionnel.
- Trafic retour fonctionnel.
- Accès interdit vers les autres services.
- Journaux ou compteurs cohérents.
- Aucun partage de routes supplémentaire non prévu.


# 13. Défi 5 — Connectivité externe avec L3Out

Le L3Out définit la connectivité routée entre la fabric ACI et un réseau extérieur.

Les routes externes peuvent être apprises ou annoncées au moyen d'un protocole de routage ou de routes statiques, selon le scénario.

## 13.1. Architecture de bordure

```text
                 RÉSEAU EXTERNE / CAMPUS
                           |
                      +---------+
                      | PARE-FEU|
                      +---------+
                           |
                 +---------+---------+
                 |                   |
                 v                   v
             +-----------+       +-----------+
             | LEAF-201  |       | LEAF-202  |
             | BORDER-A  |       | BORDER-B  |
             +-----------+       +-----------+
                 |                   |
                 +---------+---------+
                           |
                     FABRIC ACI
                           |
            +--------------+--------------+
            |                             |
            v                             v
       TENANT-ALPHA                  TENANT-BETA
```

Le L3Out et ses External EPGs déterminent comment la connectivité externe est représentée dans ACI et comment les politiques sont appliquées aux échanges avec les réseaux externes.

Les détails de conception dépendent du type de connexion, de la version et du modèle de bordure retenu.

## 13.2. Exemple de plan IP pour le transit

Pour le laboratoire, supposons que les border leafs sont connectés à un équipement externe.

| Élément | Adresse illustrative |
|---|---|
| Transit externe | `172.31.255.0/29` |
| Équipement externe | `172.31.255.1` |
| Border A | `172.31.255.2` |
| Border B | `172.31.255.3` |

Ces valeurs représentent un exemple de réseau de transit. La configuration effective dépend du mode d'attachement et de la prise en charge des interfaces utilisées.

## 13.3. External EPG

Un External EPG permet de classer les réseaux externes pour les politiques ACI.

Il ne remplace pas une table de routage. Les routes et la politique de sécurité restent deux éléments à vérifier.

Vous devez définir :

- Les préfixes externes concernés.
- Les routes acceptées.
- Les routes annoncées.
- Les contrats avec les EPG internes.
- Les sources autorisées.
- Les destinations autorisées.
- Les filtres des flux.
- Les mécanismes de redondance.

## 13.4. Publication d'une application Web

Le scénario prévoit que des utilisateurs du réseau externe accèdent à l'EPG Web d'Alpha.

```text
                 RÉSEAU EXTERNE
                        |
                        v
                     PARE-FEU
                        |
                        v
                  L3Out / EXTERNAL EPG
                        |
                  Contrat de publication
                        |
                        v
                 EPG-ALPHA-WEB
                        |
                        v
                 EPG-ALPHA-APP
                        |
                        v
                 EPG-ALPHA-DB
```

Ce schéma représente une intention de flux. Le parcours réel dépend de la localisation du pare-feu, des routes, des External EPGs, des contrats et des points de filtrage.

Ne publiez pas directement la base de données.

## 13.5. Tests L3Out

Vous devez confirmer :

1. L'état de la connectivité physique.
2. L'état du voisinage de routage lorsque nécessaire.
3. Les routes reçues.
4. Les routes annoncées.
5. Les politiques de contrôle des routes.
6. L'association entre L3Out et VRF.
7. Les External EPGs et leurs préfixes.
8. Les contrats de publication.
9. Les tests positifs depuis les sources autorisées.
10. Les tests négatifs depuis les sources non autorisées.


# 14. Architecture 6 — Séparer tenants, VRF et environnements

Une question importante de conception consiste à déterminer combien de tenants et combien de VRF doivent être créés.

## 14.1. Une VRF partagée par tenant

Dans un premier modèle, chaque tenant possède une VRF de production.

```text
TENANT-ALPHA
    |
    +-- VRF-ALPHA
           |
           +-- BD WEB
           +-- BD APP
           +-- BD DB

TENANT-BETA
    |
    +-- VRF-BETA
           |
           +-- BD WEB
           +-- BD APP
           +-- BD DB
```

Avantages :

- Structure simple.
- Réduction de la complexité.
- Segmentation logique lisible.
- Adapté à des clients dont les applications partagent un même contexte de routage.

Limites :

- Les réseaux du même tenant partagent une VRF, sauf mécanismes particuliers.
- La séparation entre applications repose davantage sur les BD, EPG et politiques de contrat.
- Les migrations ou modifications de contexte peuvent devenir complexes si les besoins évoluent.

## 14.2. VRF distinctes pour la production et le test

Un autre modèle sépare les environnements.

```text
TENANT-ALPHA
    |
    +-- VRF-ALPHA-PROD
    |       |
    |       +-- BD / EPG Production
    |
    +-- VRF-ALPHA-TEST
            |
            +-- BD / EPG Test
```

Avantages :

- Contexte de routage distinct.
- Séparation plus forte des chemins et préfixes.
- Possibilité de traiter différemment les routes.
- Meilleure lisibilité des frontières d'environnement.

Limites :

- Partage des services plus complexe.
- Risque de configuration supplémentaire.
- Nécessité d'une stratégie explicite pour le DNS, la supervision et les services communs.

## 14.3. Plusieurs applications dans une VRF

Dans certains scénarios, plusieurs applications peuvent partager une VRF mais posséder des EPG distincts.

L'isolement du trafic dépend alors des contrats et des autres mécanismes de politique.

Ce choix doit être justifié par les besoins et les risques.

Il ne faut pas considérer qu'une VRF supplémentaire résout tous les problèmes d'isolation. Inversement, un unique contexte de routage peut être adapté lorsque la séparation EPG et les politiques correspondent réellement aux exigences.

## 14.4. Exercice d'architecture

Proposez deux variantes :

**Variante A :** une VRF de production par tenant.

**Variante B :** une VRF de production et une VRF de test par tenant.

Comparez les deux selon :

- La lisibilité.
- La facilité de déploiement.
- Le partage des services.
- La gestion des routes.
- La complexité RBAC.
- Le nombre de contrats.
- Les risques d'erreur.
- L'exploitation quotidienne.
- Les évolutions futures.

Choisissez une architecture et justifiez-la avec les exigences métier du scénario.


# 15. Défi expert — Portée des contrats et risques de sécurité

La portée d'un contrat est un élément essentiel dans un environnement multi-tenant.

Un contrat réutilisé plus largement peut modifier les politiques effectives entre EPG.

## 15.1. Portées conceptuelles

Les portées généralement rencontrées dans le modèle ACI comprennent :

- Application.
- VRF.
- Tenant.
- Global.

Le sens exact dépend de l'objet, de la configuration et de la version. Vérifiez le comportement de la plateforme avant de réutiliser un contrat.

## 15.2. Risque d'un contrat global

Supposons que l'organisation crée un contrat commun pour autoriser l'accès à un service.

Si ce contrat est utilisé à une portée trop large, il peut devenir réutilisable par des groupes qui n'étaient pas dans le périmètre initialement prévu.

```text
                CONTRAT GLOBAL
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       EPG Alpha    EPG Beta    EPG Test

  Risque :
  association involontaire ou trop large
  si la politique n'est pas conçue et revue.
```

Le schéma illustre le risque de portée. Il ne signifie pas que le simple fait de créer un contrat Global autorise immédiatement tous les échanges : les associations de contrat et les conditions nécessaires restent importantes.

## 15.3. Évaluer le scope minimal

Pour chaque contrat, répondez aux questions suivantes :

1. Les EPG consommateurs et fournisseurs sont-ils dans le même Application Profile ?
2. Sont-ils dans la même VRF ?
3. Sont-ils dans le même tenant ?
4. Un partage inter-tenant est-il nécessaire ?
5. Un partage inter-VRF est-il nécessaire ?
6. Le contrat doit-il réellement être global ?
7. Peut-on utiliser un contrat plus restreint ?
8. Quelles autres associations existent déjà ?
9. Comment vérifier la politique programmée ?
10. Quels tests négatifs doivent être réalisés après le changement ?

## 15.4. Audit des contrats

Créez un inventaire des contrats avec :

- Nom.
- Tenant propriétaire.
- Portée.
- Consumers.
- Providers.
- Filtres.
- Subjects.
- Justification.
- Ressources concernées.
- Date de dernière revue.
- Responsable.
- Tests associés.

Tout contrat sans justification documentée doit être examiné avant d'être conservé.


# 16. Défi expert — Partage d'un L3Out entre tenants

Le partage d'un L3Out peut permettre à plusieurs tenants d'utiliser un même point de connectivité externe, sous réserve des mécanismes de partage et de routage configurés.

Cette architecture peut être intéressante si de nombreux tenants doivent communiquer avec le même réseau externe.

Elle nécessite cependant de contrôler la portée des routes et l'application des contrats.

## 16.1. Schéma de partage

```text
                    RÉSEAU EXTERNE
                          |
                       PARE-FEU
                          |
                    L3Out partagé
                          |
                 +--------+--------+
                 |                 |
                 v                 v
            TENANT-ALPHA      TENANT-BETA
                 |                 |
              EPG Alpha          EPG Beta
                 |                 |
                 +--------+--------+
                          |
                 Contrats explicites
                 et routes autorisées
```

## 16.2. Points de contrôle

Vous devez documenter :

- Le tenant hébergeant le L3Out.
- La VRF à laquelle le L3Out est associé.
- Les préfixes externes.
- Les routes partagées.
- Les EPG qui consomment le service.
- Les contrats associés.
- Les éventuelles fonctions de route leaking inter-VRF.
- Les règles de filtrage.
- Les conditions de routage retour.
- Les risques d'accès involontaire entre tenants.

Un L3Out partagé ne doit pas être considéré comme une autorisation automatique pour chaque tenant d'utiliser toutes les routes externes.

## 16.3. Exercice

Le tenant Alpha doit accéder à Internet, mais le tenant Beta ne doit accéder qu'à un réseau partenaire.

Définissez :

1. Les préfixes autorisés pour Alpha.
2. Les préfixes autorisés pour Beta.
3. Les routes reçues et annoncées.
4. Les External EPGs nécessaires.
5. Les contrats.
6. Le modèle de partage du L3Out.
7. Les tests d'accès positifs.
8. Les tests d'accès négatifs.
9. Les événements à surveiller.
10. La procédure de retour arrière.


# 17. Défi 6 — Fabric, overlay VXLAN et plan de données

ACI utilise une architecture de fabric qui repose sur un overlay VXLAN pour fournir une abstraction des réseaux et des politiques.

L'administrateur ne doit pas confondre les objets logiques ACI avec un ensemble de tunnels VXLAN qu'il configurerait manuellement comme dans une architecture VXLAN autonome.

## 17.1. Modèle logique et transport

```text
                    OBJETS LOGIQUES ACI
                 +-------------------------+
                 | Tenants                 |
                 | VRF                     |
                 | Bridge Domains          |
                 | EPG                     |
                 | Contracts               |
                 +-------------------------+
                              |
                       APIC programme
                       la politique ACI
                              |
                              v
                    FABRIC LEAF-SPINE
                 +-------------------------+
                 | Underlay / Transport    |
                 | Overlay VXLAN           |
                 +-------------------------+
                              |
                 Endpoints raccordés aux leafs
```

Le modèle logique décrit ce que l'administrateur veut obtenir. La fabric utilise ses mécanismes internes pour transporter le trafic et appliquer les politiques correspondantes.

## 17.2. Trafic entre deux endpoints

Lorsqu'un endpoint communique avec un endpoint situé sur un autre leaf, la fabric doit pouvoir identifier les endpoints, leur appartenance, la destination et les politiques applicables.

Le fonctionnement dépend notamment :

- De l'apprentissage des endpoints.
- Des associations aux EPG.
- Du BD et de la VRF.
- De l'adressage.
- Des contrats.
- De la disponibilité des leafs.
- Du fonctionnement de la fabric.

Le détail du transport interne et des métadonnées est géré par l'architecture ACI. Le dépannage doit d'abord vérifier le modèle de politique et l'état de la fabric plutôt que présumer d'une erreur de configuration d'un tunnel manuel.

## 17.3. Exercice

Pour deux VMs raccordées à des leafs différents :

1. Vérifiez leur appartenance aux EPG.
2. Vérifiez leurs BD.
3. Vérifiez leurs VRF.
4. Vérifiez leurs adresses IP.
5. Déterminez si les communications sont dans le même sous-réseau ou entre sous-réseaux.
6. Vérifiez les contrats.
7. Observez le chemin effectif.
8. Consultez les journaux ou outils de dépannage disponibles.
9. Confirmez que les restrictions inter-EPG sont respectées.


# 18. Défi 7 — Supervision de la fabric ACI

Un environnement ACI doit être exploitable par une équipe qui sait distinguer une panne physique, une erreur de classification d'endpoint, une erreur de politique et un problème de routage.

## 18.1. Éléments à surveiller

| Domaine | Informations à contrôler |
|---|---|
| Fabric | État global, équipements et anomalies |
| Spines | État des liens, erreurs et connectivité |
| Leafs | État des ports, erreurs et déploiement des politiques |
| APIC | Disponibilité du cluster, santé et événements |
| Tenants | Objets incohérents, politiques et changements |
| VRF | Routes et paramètres |
| Bridge Domains | Sous-réseaux, passerelles et paramètres de BD |
| EPG | Classification des endpoints et association au BD |
| Contracts | Associations et règles programmées |
| L3Out | Sessions de routage, routes et état de connectivité |
| Endpoints | Localisation, apprentissage et incohérences |
| RBAC | Modifications, accès et événements d'audit |

Les indicateurs exacts dépendent de la version et des outils de supervision disponibles.

## 18.2. Journaux à conserver

Les événements importants peuvent comprendre :

- Changements de configuration.
- Connexions d'administration.
- Échecs de déploiement de politiques.
- Changements d'état de ports.
- Pannes de voisinages de routage.
- Modifications de contrats.
- Modifications de L3Out.
- Changements de route leaking.
- Déplacements d'endpoints.
- Anomalies des contrôleurs.
- Modifications d'accès RBAC.

## 18.3. Tableau de bord minimal

Le tableau de bord doit permettre de répondre à ces questions :

- La fabric est-elle opérationnelle ?
- Les leafs et spines sont-ils joignables ?
- Les endpoints sont-ils classés dans les EPG attendus ?
- Les contrats ont-ils les associations prévues ?
- Les routes externes sont-elles présentes ?
- Les services partagés sont-ils accessibles aux bons tenants ?
- Des modifications inattendues ont-elles eu lieu ?
- Les communications interdites sont-elles bloquées ?

## 18.4. Exercice

Provoquez un incident dans un laboratoire et rassemblez :

1. L'état des interfaces.
2. L'état des objets concernés.
3. L'appartenance de l'endpoint.
4. Le contrat attendu.
5. Les routes nécessaires.
6. Les journaux.
7. Les tests positifs et négatifs.
8. La preuve de restauration du comportement.


# 19. Défi 8 — Dépannage ACI par symptôme

Le dépannage ACI doit examiner le chemin complet de la communication :

1. Endpoint.
2. Classification EPG.
3. Bridge Domain.
4. VRF.
5. Contrat.
6. Routage.
7. Connectivité externe éventuelle.
8. Service cible.

Toutes les pannes ne nécessitent pas d'examiner chaque objet dans cet ordre. Le symptôme et les preuves disponibles doivent guider l'investigation.

## Scénario A — Un endpoint n'apparaît pas dans l'EPG attendu

### Symptôme

Un serveur démarre, mais la communication n'est pas conforme à la politique attendue.

### Hypothèses

- Mauvais port physique.
- Chemin statique absent.
- VLAN d'encapsulation incorrect.
- Domaine incorrect.
- VLAN Pool ou AAEP mal associé.
- Intégration VMM absente ou incorrecte.
- Endpoint classé dans un autre groupe.
- Problème de liaison ou de carte réseau.

### Démarche

1. Identifier le leaf et le port du serveur.
2. Vérifier l'état physique.
3. Vérifier les associations du chemin.
4. Vérifier le domaine.
5. Vérifier le VLAN utilisé pour l'encapsulation.
6. Contrôler l'association EPG/BD.
7. Vérifier les informations d'endpoint.
8. Comparer avec un serveur fonctionnel du même rôle.
9. Corriger le point de configuration responsable.
10. Refaire les tests d'accès.

### Preuve attendue

Le serveur est classé dans l'EPG prévu et les règles appliquées correspondent à ce groupe.


## Scénario B — Deux EPG d'une même VRF ne communiquent pas

### Hypothèses

- Contrat absent.
- Mauvais consumer/provider.
- Filtre incorrect.
- Mauvaise association au BD.
- Mauvaise adresse IP.
- Mauvais port d'application.
- Erreur de classification.
- Problème applicatif.
- Politique d'enforcement ou exception spécifique.

### Démarche

1. Vérifier les EPG de source et de destination.
2. Vérifier leurs BD et VRF.
3. Contrôler les contrats consommés et fournis.
4. Vérifier le filtre.
5. Vérifier le port et le protocole.
6. Vérifier le chemin et les tables de routage.
7. Consulter les journaux.
8. Tester un service de contrôle.
9. Réaliser un test positif et un test négatif.
10. Corriger la politique minimale nécessaire.


## Scénario C — Alpha accède à une application de Beta

### Gravité

Élevée si aucun échange entre les tenants n'a été autorisé.

### Hypothèses

- Route leaking inattendu.
- Contrat de portée trop large.
- Association de contrat incorrecte.
- VRF mal configurée.
- Shared Services configurés trop largement.
- L3Out partagé avec une politique trop permissive.
- Chemin externe alternatif.
- Erreur de classification d'endpoint.
- Configuration de l'application ou du système d'exploitation qui contourne le chemin prévu.

### Démarche

1. Identifier la source et la destination.
2. Vérifier les tenants et EPG concernés.
3. Rechercher tous les contrats associés.
4. Vérifier leur portée.
5. Examiner les VRF.
6. Identifier les routes disponibles.
7. Rechercher les mécanismes de partage de routes.
8. Contrôler les relations L3Out si elles interviennent.
9. Vérifier le chemin du trafic.
10. Révoquer l'autorisation non prévue au point de contrôle adapté.
11. Tester l'isolation.
12. Vérifier que les communications légitimes restent opérationnelles.

Ne supprimez pas un contrat global sans déterminer qui l'utilise et quelles applications en dépendent.


## Scénario D — Un service partagé est inaccessible depuis Alpha

### Symptôme

Le service DNS de Common fonctionne depuis certaines sources mais échoue depuis Alpha.

### Hypothèses

- Contrat absent.
- Contrat consommé par le mauvais EPG.
- Route vers le service indisponible.
- Partage inter-VRF incomplet.
- Sous-réseau de service non partagé lorsque cela est nécessaire.
- Réponse de retour incorrecte.
- Port DNS bloqué.
- Problème d'endpoint.

### Démarche

1. Identifier l'EPG consommateur.
2. Identifier l'EPG fournisseur.
3. Vérifier le contrat et ses filtres.
4. Confirmer la relation entre VRF.
5. Vérifier le mécanisme de route leaking utilisé.
6. Vérifier la visibilité du sous-réseau.
7. Tester le service avec le protocole réel.
8. Examiner le retour.
9. Consulter les journaux.
10. Réparer le mécanisme manquant sans autoriser un accès général au tenant Common.


## Scénario E — Le tenant reçoit une route externe inattendue

### Symptôme

Un tenant peut atteindre un préfixe qui ne devrait pas être accessible.

### Hypothèses

- Préfixe trop largement annoncé.
- Route leak.
- L3Out partagé de façon incorrecte.
- External EPG trop large.
- Contrat trop large.
- Route statique incorrecte.
- Politique de contrôle des routes insuffisante.
- Partage inter-VRF mal documenté.

### Démarche

1. Identifier le préfixe.
2. Identifier sa source.
3. Examiner les routes reçues et annoncées.
4. Vérifier la VRF.
5. Vérifier le L3Out.
6. Vérifier l'External EPG.
7. Rechercher les contrats associés.
8. Contrôler les paramètres de partage de routes.
9. Déterminer si le préfixe doit réellement être accessible.
10. Corriger l'annonce ou le mécanisme de partage.
11. Valider les autres routes externes.


## Scénario F — La configuration APIC est correcte en apparence, mais le serveur ne fonctionne pas

### Hypothèses

- Problème du système d'exploitation.
- Mauvaise passerelle.
- Erreur de masque.
- Adresse IP dupliquée.
- Problème de service.
- Politique de pare-feu local.
- DNS incorrect.
- Erreur de classification ou contrat.
- Dépendance externe inaccessible.

### Démarche

1. Vérifier la configuration IP du serveur.
2. Contrôler sa connectivité locale.
3. Vérifier l'EPG auquel il appartient.
4. Vérifier le BD et sa VRF.
5. Vérifier les contrats pertinents.
6. Examiner les routes.
7. Tester le port applicatif.
8. Examiner les journaux du serveur.
9. Comparer avec un endpoint similaire.
10. Déterminer si la cause se situe dans ACI ou dans le système hébergé.

Le fait qu'une politique ait été déployée ne garantit pas le bon fonctionnement du service applicatif.


# 20. Défi 9 — Plan de changement ACI

Une modification de contrat ou de route peut affecter plusieurs services.

Les changements doivent donc suivre une procédure documentée.

## 20.1. Cycle de changement

```text
                    DEMANDE DE CHANGEMENT
                             |
                             v
                     ANALYSE DU BESOIN
                             |
                             v
                     IDENTIFICATION DES OBJETS
                             |
                             v
                       REVUE D'IMPACT
                             |
                             v
                     SAUVEGARDE / EXPORT
                             |
                             v
                     CHANGEMENT CONTRÔLÉ
                             |
                             v
                     TESTS POSITIFS
                             |
                             v
                     TESTS NÉGATIFS
                             |
                             v
                     VALIDATION FINALE
                             |
                             v
                MISE À JOUR DE LA DOCUMENTATION
```

## 20.2. Informations à conserver

Pour toute modification importante, documentez :

- Le tenant.
- La VRF.
- Le BD.
- Les EPG concernés.
- Les contrats associés.
- Les routes et L3Out concernés.
- Les objectifs.
- Les risques.
- Les tests préalables.
- Le changement effectué.
- Les tests après changement.
- La procédure de retour arrière.
- La personne responsable.
- L'historique de validation.

## 20.3. Exercice de changement

Le client Alpha demande un accès HTTPS à une nouvelle API hébergée dans son EPG Application.

Vous devez :

1. Identifier le flux exact.
2. Vérifier le consumer et le provider.
3. Vérifier l'existence du filtre nécessaire.
4. Déterminer si le contrat doit être modifié ou si un contrat distinct est préférable.
5. Choisir la portée minimale suffisante.
6. Vérifier si d'autres EPG consomment déjà ce contrat.
7. Préparer une sauvegarde.
8. Appliquer la modification en laboratoire.
9. Tester l'API.
10. Vérifier que Beta ne peut pas accéder à cette API.
11. Documenter le changement et le retour arrière.


# 21. Défi expert — Automatisation et API APIC

ACI permet d'administrer des objets et politiques au moyen des interfaces et mécanismes pris en charge par APIC.

L'automatisation peut réduire les erreurs répétitives, mais une mauvaise définition de la source de vérité peut aussi propager une erreur dans plusieurs tenants.

## 21.1. Éléments à automatiser

Dans le cadre du challenge, vous pouvez automatiser :

- La génération de la convention de nommage.
- L'inventaire des tenants.
- L'inventaire des VRF.
- Le contrôle des Bridge Domains.
- Le contrôle des EPG.
- La collecte des contrats et portées.
- L'inventaire des associations consumer/provider.
- Le contrôle des L3Out.
- La collecte des routes attendues.
- La détection des objets non documentés.
- La comparaison de la configuration observée avec un modèle de référence.

## 21.2. Modèle de données

Un modèle de référence peut prendre la forme suivante :

```text
Tenant:
  TENANT-ALPHA

VRF:
  VRF-ALPHA-PROD

Bridge Domains:
  BD-ALPHA-WEB
  BD-ALPHA-APP
  BD-ALPHA-DB

EPGs:
  EPG-ALPHA-WEB
  EPG-ALPHA-APP
  EPG-ALPHA-DB

Contrats:
  CT-ALPHA-WEB-APP
  CT-ALPHA-APP-DB

Politiques attendues:
  WEB -> APP : autorisé sur les ports applicatifs requis
  APP -> DB  : autorisé sur le port DB requis
  Alpha -> Beta : refusé
  Alpha -> Common : uniquement les services partagés approuvés
```

Il s'agit d'un modèle conceptuel, pas d'un document de configuration APIC directement importable.

## 21.3. Contrôles automatiques

L'automatisation doit pouvoir signaler :

- Un EPG sans BD attendu.
- Un BD dans une VRF incorrecte.
- Un contrat sans justification.
- Un contrat Global inattendu.
- Un EPG ayant une association non documentée.
- Une route externe non prévue.
- Un endpoint classé dans un EPG inattendu.
- Une différence entre le modèle souhaité et le modèle réel.

## 21.4. Garde-fous

- Valider le modèle avant le déploiement.
- Contrôler le plan de modification.
- Tester d'abord en laboratoire.
- Éviter les changements globaux non nécessaires.
- Sauvegarder les données de référence.
- Journaliser les opérations.
- Prévoir une procédure de retour arrière.
- Utiliser des identités d'automatisation aux droits limités.
- Ne pas placer de secrets dans les fichiers partagés.


# 22. Défi final — Incident multi-tenant combiné

Vous êtes administrateur de la fabric et plusieurs anomalies apparaissent.

1. Alpha ne peut plus accéder à son application.
2. Beta semble pouvoir atteindre une ressource d'Alpha.
3. Le service DNS commun est inaccessible depuis certains EPG.
4. Une route inattendue apparaît dans une VRF.
5. Un changement récent a modifié la portée d'un contrat.
6. Une application externe publiée par L3Out ne répond plus.
7. Les administrateurs d'Alpha signalent des permissions insuffisantes dans APIC.

Vous ne savez pas si ces incidents ont une cause commune.

## 22.1. Règles d'intervention

Vous devez :

- Préserver les journaux.
- Identifier le périmètre de chaque anomalie.
- Prioriser l'exposition inter-tenant.
- Ne pas supprimer immédiatement tous les contrats globaux.
- Ne pas modifier toutes les VRF simultanément.
- Ne pas désactiver les politiques d'enforcement pour rétablir la connectivité.
- Ne pas annoncer de nouveaux préfixes sans analyse.
- Vérifier les chemins et politiques.
- Documenter les changements.
- Conserver des tests positifs et négatifs.

## 22.2. Tableau de collecte

| Symptôme | Première vérification |
|---|---|
| Application Alpha inaccessible | EPG, BD, VRF, contrats et service cible |
| Accès Alpha vers Beta | Source, destination, contrat, scope et route leak |
| DNS commun inaccessible | Consumer/provider, filtres et partage inter-VRF |
| Route inattendue | VRF, L3Out, préfixe, partage et contrats |
| Contrat modifié récemment | Historique, scope et associations |
| Publication externe en panne | L3Out, External EPG, routes et contrat |
| RBAC insuffisant | Rôle, domaine administratif et permissions effectives |

## 22.3. Phase 1 — Définir les faits

Pour chaque symptôme, identifiez :

- Les endpoints concernés.
- Les EPG de source et de destination.
- Les BD.
- Les VRF.
- Le tenant propriétaire.
- Les contrats consommés et fournis.
- Les routes disponibles.
- Les L3Out concernés.
- Les changements récents.
- Les résultats observés.

## 22.4. Phase 2 — Déterminer les causes possibles

Exemples :

- Une connexion Alpha vers Beta peut être liée à une politique trop large ou à un partage inattendu.
- Le DNS commun peut être affecté par un contrat ou par le mécanisme de connectivité inter-VRF.
- Une route inattendue peut être liée à une annonce externe ou à une configuration de route leaking.
- Une publication L3Out peut être affectée par le routage, les External EPGs ou les contrats.
- Un problème RBAC peut être indépendant du plan de données.

Ne considérez pas automatiquement qu'un changement récent explique tous les symptômes.

## 22.5. Phase 3 — Corriger

Pour chaque incident :

1. Formuler une hypothèse.
2. Identifier la preuve nécessaire.
3. Sauvegarder les éléments concernés.
4. Identifier le changement minimal.
5. Appliquer la modification dans le cadre autorisé.
6. Vérifier le résultat.
7. Réaliser des tests positifs.
8. Réaliser des tests négatifs.
9. Vérifier l'absence de régression.
10. Mettre à jour la documentation.

## 22.6. Rapport final

Le rapport doit contenir :

- La chronologie.
- Le périmètre des incidents.
- Les objets concernés.
- Les hypothèses testées.
- Les preuves collectées.
- La cause démontrée.
- Les corrections.
- Les tests après correction.
- Les impacts sur les autres tenants.
- Les risques résiduels.
- Les mesures de prévention.


# 23. Architecture cible consolidée

## 23.1. Vue générale de la fabric

```text
                         FABRIC CISCO ACI
                                |
                +---------------+---------------+
                |               |               |
                v               v               v

           +-----------+    +-----------+    +-----------+
           | TENANT    |    | TENANT    |    | TENANT    |
           | ALPHA     |    | BETA      |    | COMMON    |
           +-----------+    +-----------+    +-----------+
                |               |               |
                v               v               v
            VRF-ALPHA        VRF-BETA        VRF-COMMON
                |               |               |
           +----+----+      +----+----+      +----+----+
           |    |    |      |    |    |      |    |    |
           v    v    v      v    v    v      v    v    v
          WEB  APP   DB    WEB  APP   DB     DNS  NTP MON

                \               |               /
                 \              |              /
                  +-------------+-------------+
                                |
                     Contrats et partage
                     explicitement contrôlés
                                |
                                v
                           L3Out / WAN
                                |
                           Pare-feu externe
```

Ce schéma représente l'organisation logique. Il ne signifie pas que tous les tenants partagent nécessairement une même VRF ou une même route externe.

Chaque relation doit être définie à partir de la politique de communication prévue.

## 23.2. Résumé des décisions

| Domaine | Décision de référence |
|---|---|
| Fabric | Leaf-spine |
| Plan de gestion | APIC avec rôles contrôlés |
| Tenants applicatifs | Alpha et Beta |
| Tenant de services | Common |
| Routage | VRF séparées |
| Segmentation L2 | Bridge Domains |
| Groupes de politique | EPG |
| Organisation applicative | Application Profiles |
| Filtrage est-ouest | Contracts et Filters |
| Connectivité externe | L3Out et External EPG |
| Services partagés | Contracts et mécanismes de routage nécessaires |
| Route leaking | Seulement pour les cas justifiés |
| Contrats globaux | Utilisés avec prudence |
| RBAC | Rôles dédiés à chaque périmètre |
| Validation | Tests positifs et négatifs |
| Exploitation | Journaux, inventaire et procédures de changement |


# 24. Barème d'évaluation sur 100 points

| Domaine | Points |
|---|---:|
| Compréhension de la fabric leaf-spine et des composants | 8 |
| Compréhension des tenants, VRF, BD et EPG | 12 |
| Plan d'adressage et cohérence des objets | 8 |
| Déploiement des endpoints et domaines d'accès | 8 |
| Contrats, Filters et Subjects | 12 |
| Isolation entre tenants | 12 |
| Services partagés et route leaking | 10 |
| L3Out et connectivité externe | 8 |
| RBAC et séparation d'administration | 5 |
| Dépannage et analyse d'incidents | 7 |
| Automatisation et gestion des changements | 5 |
| Documentation et références | 5 |
| **Total** | **100** |

## 24.1. Critères d'excellence

Une architecture de qualité doit :

- Utiliser les objets ACI de manière cohérente.
- Distinguer correctement tenant et VRF.
- Associer les BD aux VRF prévues.
- Définir des EPG dont le rôle est clair.
- Limiter les contrats à la portée nécessaire.
- Démontrer l'isolation entre Alpha et Beta.
- Documenter les routes externes.
- Partager les services avec des règles précises.
- Contrôler le route leaking.
- Séparer les droits administratifs.
- Fournir des preuves de validation.
- Prévoir les changements et leur retour arrière.

## 24.2. Erreurs graves

Les erreurs suivantes doivent entraîner une pénalité importante :

- Considérer que le tenant fournit à lui seul toute l'isolation du plan de données.
- Confondre EPG et Bridge Domain.
- Placer des EPG dans une VRF sans comprendre les conséquences de routage.
- Autoriser les échanges entre tenants sans justification.
- Créer des contrats très larges pour résoudre un problème rapidement.
- Utiliser Global sans analyser les associations existantes.
- Croire qu'un contrat suffit toujours à assurer le route leaking inter-VRF.
- Ouvrir un L3Out sans politique de contrôle des routes.
- Publier la base de données au lieu de l'application nécessaire.
- Donner aux administrateurs d'un tenant des privilèges globaux injustifiés.
- Valider l'isolation sans test de communication interdite.
- Ne pas tester les changements de politique.
- Ne pas conserver les journaux.


# 25. Modèle du dossier technique final

## 25.1. Résumé exécutif

Présentez :

- Le besoin de multi-tenancy.
- Le nombre de tenants.
- Les exigences d'isolation.
- Le modèle de services partagés.
- La stratégie de connectivité externe.
- Les risques principaux.
- Les choix de conception.

## 25.2. Architecture physique

Fournissez :

- Le schéma des spines et leafs.
- Le rôle de chaque leaf.
- Les liens vers les serveurs.
- Les liens vers les hyperviseurs.
- Les connexions L3Out.
- Les connexions APIC.
- Les chemins de gestion.
- Les mécanismes physiques de redondance.

## 25.3. Architecture logique

Documentez :

- Les tenants.
- Les VRF.
- Les Bridge Domains.
- Les sous-réseaux.
- Les Application Profiles.
- Les EPG.
- Les contrats.
- Les Services partagés.
- Les L3Out.
- Les External EPGs.
- Les relations inter-VRF.
- Les relations inter-tenant.

## 25.4. Matrice de communication

| Champ | Description |
|---|---|
| Identifiant | Référence unique |
| Tenant source | Tenant de l'EPG source |
| EPG source | Groupe qui initie le flux |
| Tenant destination | Tenant cible |
| EPG destination | Groupe fournisseur |
| Protocole | TCP, UDP, ICMP ou autre |
| Port | Port requis |
| Contrat | Contrat qui autorise le flux |
| Scope | Portée configurée |
| Routage | VRF et éventuel partage nécessaire |
| Justification | Besoin métier |
| Test positif | Communication autorisée |
| Test négatif | Communication interdite |
| Preuve | Résultat du test et journaux |

## 25.5. Tableau de validation

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | Endpoint Alpha | Classé dans l'EPG prévu | À renseigner | À exécuter |
| T02 | EPG Alpha Web → Application | Autorisé par contrat | À renseigner | À exécuter |
| T03 | EPG Alpha Application → DB | Autorisé sur le service requis | À renseigner | À exécuter |
| T04 | Alpha → Beta | Refusé | À renseigner | À exécuter |
| T05 | Alpha → DNS Common | Autorisé selon la politique | À renseigner | À exécuter |
| T06 | Alpha → autre service Common | Refusé si non autorisé | À renseigner | À exécuter |
| T07 | Route externe | Préfixes conformes | À renseigner | À exécuter |
| T08 | Publication L3Out | Service autorisé accessible | À renseigner | À exécuter |
| T09 | Contrat trop large | Détection par audit | À renseigner | À exécuter |
| T10 | RBAC Alpha | Accès aux seuls objets autorisés | À renseigner | À exécuter |
| T11 | Route leaking | Préfixes partagés prévus uniquement | À renseigner | À exécuter |
| T12 | Retour arrière | Configuration rétablie et validée | À renseigner | À exécuter |

Un résultat ne doit pas être marqué « OK » tant que le test correspondant n'a pas été effectué et qu'une preuve n'est pas disponible.


# 26. Checklist finale

## Fabric

- [ ] La topologie leaf-spine est documentée.
- [ ] Chaque leaf possède les liens prévus vers les spines.
- [ ] Les fonctions des leafs de calcul et de bordure sont claires.
- [ ] Les connexions des APIC sont documentées.
- [ ] La gestion de la fabric est protégée.
- [ ] Les chemins de redondance ont été vérifiés.

## Modèle logique

- [ ] Chaque tenant a un rôle explicite.
- [ ] Les VRF correspondent aux besoins de routage.
- [ ] Chaque Bridge Domain appartient à la VRF prévue.
- [ ] Les sous-réseaux sont cohérents.
- [ ] Les Application Profiles organisent les EPG attendus.
- [ ] Les EPG correspondent aux rôles applicatifs.
- [ ] Les endpoints sont correctement classés.

## Sécurité

- [ ] Les contrats correspondent aux besoins.
- [ ] Les filtres sont précis.
- [ ] Les scopes sont justifiés.
- [ ] Les tenants ne communiquent pas librement.
- [ ] Les services partagés sont contrôlés.
- [ ] Les chemins inter-VRF sont documentés.
- [ ] Le route leaking est limité aux préfixes nécessaires.
- [ ] Les L3Out et External EPGs sont documentés.
- [ ] Les permissions RBAC sont testées.

## Exploitation

- [ ] Les configurations sont sauvegardées.
- [ ] Les changements sont tracés.
- [ ] Les journaux sont disponibles.
- [ ] Les procédures de diagnostic sont documentées.
- [ ] Les contrats importants sont inventoriés.
- [ ] Les routes externes sont surveillées.
- [ ] Les tests positifs et négatifs sont conservés.
- [ ] Les procédures de retour arrière existent.


# 27. Références techniques officielles

Les références ci-dessous permettent de vérifier les mécanismes étudiés et d'approfondir la configuration.

- [Cisco ACI Design Guide](https://www.cisco.com/c/en/us/td/docs/dcn/whitepapers/cisco-application-centric-infrastructure-design-guide.html) — conception physique, fabric, tenants et infrastructure.
- [Cisco APIC Basic Configuration Guide, Release 6.2(x) — Basic User Tenant Configuration](https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/basic-configuration/cisco-apic-basic-configuration-guide-62x/basic-user-tenant-configuration-62x.html) — tenants, VRF, BD, EPG et contrats.
- [Cisco ACI Contract Guide](https://www.cisco.com/c/en/us/products/collateral/networking/cloud-networking/application-centric-infrastructure/contract-guide.html) — contrats, portée, Preferred Group, `vzAny` et considérations inter-VRF.
- [Cisco APIC Layer 3 Networking Configuration Guide, Release 6.2(x)](https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/l3-configuration/cisco-apic-layer-3-networking-configuration-guide-62x/routed-connectivity-to-external-nets-layer3-config-62x/layer3-routed-connectivity-to-outside-networks.html) — L3Out et connectivité routée externe.
- [Cisco APIC Layer 3 Networking Configuration Guide — Shared Services](https://www.cisco.com/c/en/us/td/docs/dcn/aci/apic/6x/l3-configuration/cisco-apic-layer-3-networking-configuration-guide-61x/shared-l3out-layer3-config-61x.html) — partage de L3Out et services inter-VRF.
- [Cisco ACI Initial Deployment Cookbook](https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/white_papers/Cisco-ACI-Initial-Deployment-Cookbook.html) — exemple de déploiement initial et construction d'un tenant.

La syntaxe, les options disponibles, les comportements de contrat et les procédures détaillées peuvent différer selon la version APIC et le matériel. Avant de déployer, vérifiez la documentation correspondant exactement à votre environnement.


# Conclusion

Ce challenge doit démontrer que Cisco ACI ne se limite pas à remplacer des VLAN traditionnels par des objets administrés depuis APIC.

Une architecture multi-tenant fiable doit associer :

1. **Une fabric physique cohérente** : les leafs, spines, contrôleurs et chemins externes sont correctement conçus.
2. **Une segmentation logique claire** : les tenants, VRF, BD et EPG remplissent des rôles distincts.
3. **Une politique applicative explicite** : les contrats définissent les communications autorisées entre groupes.
4. **Un partage maîtrisé des services** : les routes et contrats inter-VRF ou inter-tenant ne sont créés que lorsque cela est nécessaire.
5. **Une administration contrôlée** : les rôles RBAC et les accès à APIC correspondent aux responsabilités.
6. **Des preuves opérationnelles** : les flux autorisés fonctionnent, les flux interdits sont bloqués et les changements sont réversibles.

Le choix d'un Tenant ne suffit pas à prouver une isolation complète. La sécurité doit être vérifiée dans le modèle de routage, les politiques d'EPG, les contrats, les L3Out et les mécanismes de partage utilisés.

**La meilleure fabric ACI multi-tenant est celle dans laquelle chaque groupe d'applications possède les ressources dont il a besoin, ne peut pas accéder aux ressources des autres tenants sans autorisation explicite et reste administrable sans créer de dépendances ou de privilèges excessifs.**