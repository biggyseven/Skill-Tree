
# NETCONF, YANG et RESTCONF — Niveau débutant

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Niveau :** Débutant  
> **Objectif :** comprendre les modèles de données réseau YANG, découvrir NETCONF et RESTCONF, et effectuer ses premières lectures structurées sans risque pour les équipements.


## Sommaire

1. Contexte et objectifs
2. Pourquoi automatiser la gestion du réseau ?
3. Comprendre NETCONF, YANG et RESTCONF
4. Découvrir les modèles YANG
5. Comprendre NETCONF
6. Comprendre RESTCONF
7. Comparer les deux protocoles
8. Atelier pratique
9. Sécurité et bonnes pratiques
10. Évaluation corrigée
11. Préparation du niveau intermédiaire


# 1. Contexte et objectifs

## 1.1 Contexte professionnel

Les administrateurs réseau doivent configurer et surveiller des équipements : routeurs, commutateurs, pare-feu et équipements d'infrastructure.

Traditionnellement, une partie du travail est réalisée au moyen d'une interface en ligne de commande (CLI). Cette méthode reste utile, mais automatiser un grand nombre d'équipements par des commandes textuelles peut devenir difficile.

Les problèmes fréquents sont :

- des différences de syntaxe entre constructeurs ;
- des sorties difficiles à analyser automatiquement ;
- des changements qui ne sont pas homogènes ;
- des erreurs provoquées par des commandes inadaptées ;
- une difficulté à identifier précisément les données disponibles sur un équipement.

NETCONF et RESTCONF fournissent des interfaces de gestion structurées. YANG permet de décrire les données manipulées par ces interfaces.

L'objectif n'est pas de supprimer systématiquement la CLI. Il est d'apprendre à exploiter des données et des opérations structurées pour rendre l'automatisation plus prévisible.

## 1.2 Objectifs pédagogiques

À la fin du cours, vous serez capable de :

1. expliquer la différence entre NETCONF, YANG et RESTCONF ;
2. comprendre la structure générale d'un modèle YANG ;
3. reconnaître les données de configuration et les données d'état ;
4. comprendre le rôle des messages XML de NETCONF ;
5. reconnaître les méthodes HTTP utilisées par RESTCONF ;
6. expliquer comment un client découvre les capacités d'un équipement ;
7. identifier les limites liées à la compatibilité entre constructeurs ;
8. effectuer des lectures de données avec des exemples adaptés à un laboratoire ;
9. appliquer des règles fondamentales de sécurité.

## 1.3 Prérequis

Vous devez connaître les notions suivantes :

- adresse IP et sous-réseau ;
- routeur et commutateur ;
- interface réseau ;
- configuration de base d'un équipement ;
- notions élémentaires de XML et de JSON.

La connaissance de Python est utile, mais elle n'est pas obligatoire pour ce premier niveau.


# 2. Pourquoi automatiser la gestion du réseau ?

## 2.1 Les limites d'une approche uniquement fondée sur la CLI

Imaginons que vous vouliez relever le nom, l'état administratif et l'état opérationnel de 50 interfaces réparties sur plusieurs commutateurs.

Avec une approche manuelle, vous pourriez vous connecter à chaque équipement, exécuter une commande et lire la sortie.

Cette méthode peut suffire à petite échelle, mais elle rend plus difficile :

- l'extraction automatique des champs recherchés ;
- la comparaison entre plusieurs équipements ;
- la détection cohérente des anomalies ;
- la collecte régulière des mêmes données ;
- la génération de rapports exploitables par un programme.

Une interface structurée permet à un client d'interroger des éléments identifiés par leur modèle de données.

## 2.2 Exemple de données structurées

Au lieu d'analyser une sortie textuelle, un programme peut recevoir une représentation comme celle-ci :

```json
{
  "interface": {
    "name": "Loopback0",
    "enabled": true,
    "description": "Interface de laboratoire"
  }
}
```

Cet exemple illustre la forme générale de données. Les noms de champs réellement exposés dépendent du modèle YANG pris en charge par l'équipement.

La structure permet au programme de distinguer explicitement le nom de l'interface, son état administratif et sa description.


# 3. Comprendre NETCONF, YANG et RESTCONF

Ces trois technologies sont complémentaires, mais elles n'ont pas le même rôle.

## 3.1 YANG : le modèle des données

YANG est un langage de modélisation. Il décrit la structure des données, leurs types, leurs relations, certaines contraintes, les opérations et les notifications.

Exemple conceptuel :

```text
interfaces
└── interface
    ├── name
    ├── description
    ├── enabled
    └── oper-status
```

Cette structure décrit les éléments et leur organisation logique. Elle ne précise pas, à elle seule, comment établir une connexion avec le routeur.

## 3.2 NETCONF : le protocole de gestion

NETCONF est un protocole de gestion réseau fondé sur des échanges structurés, généralement encodés en XML.

Il fournit des opérations pour consulter et modifier des données, selon les capacités annoncées par le serveur NETCONF.

Il peut notamment être utilisé pour :

- lire la configuration ;
- lire certaines données d'état ;
- modifier un ensemble de données ;
- valider des changements si les capacités nécessaires sont disponibles ;
- effectuer un commit lorsqu'un datastore `candidate` est pris en charge.

## 3.3 RESTCONF : une interface basée sur HTTP

RESTCONF expose les données modélisées en YANG sous forme de ressources accessibles avec HTTP.

Les clients utilisent notamment :

- `GET` pour lire des ressources ;
- `POST` pour créer des données dans les cas prévus par le modèle ;
- `PUT` pour remplacer une ressource ;
- `PATCH` pour modifier une partie d'une ressource ;
- `DELETE` pour supprimer une ressource, lorsque l'opération est autorisée.

RESTCONF peut utiliser XML ou JSON pour représenter les données selon les règles définies par les standards.

## 3.4 Schéma général

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-labelledby="nyr-title nyr-desc">
  <title id="nyr-title">Relations entre NETCONF, YANG et RESTCONF</title>
  <desc id="nyr-desc">Un client peut utiliser NETCONF ou RESTCONF pour accéder aux données structurées selon les modèles YANG d'un équipement. Les flèches animées montrent les échanges entre le client, le protocole et l'équipement sans objet mobile.</desc>
  <defs>
    <marker id="nyr-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .nyr-box{fill:#16263b;stroke:#60a5fa;stroke-width:2}
      .nyr-model{fill:#123126;stroke:#4ade80;stroke-width:2}
      .nyr-title{font:700 17px Arial,sans-serif;fill:#f8fafc}
      .nyr-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .nyr-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#nyr-arrow);animation:nyr-dash 1.8s linear infinite}
      @keyframes nyr-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="348" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">TROIS RÔLES COMPLÉMENTAIRES</text>
  <rect class="nyr-box" x="30" y="110" width="220" height="100" rx="12"/>
  <text class="nyr-title" x="140" y="145" text-anchor="middle">Client</text>
  <text class="nyr-text" x="140" y="171" text-anchor="middle">Script ou application</text>
  <text class="nyr-text" x="140" y="191" text-anchor="middle">Demande de données</text>
  <rect class="nyr-box" x="370" y="55" width="220" height="75" rx="12"/>
  <text class="nyr-title" x="480" y="84" text-anchor="middle">NETCONF</text>
  <text class="nyr-text" x="480" y="107" text-anchor="middle">Opérations structurées XML</text>
  <rect class="nyr-box" x="370" y="190" width="220" height="75" rx="12"/>
  <text class="nyr-title" x="480" y="219" text-anchor="middle">RESTCONF</text>
  <text class="nyr-text" x="480" y="242" text-anchor="middle">Ressources et méthodes HTTP</text>
  <rect class="nyr-model" x="710" y="110" width="220" height="100" rx="12"/>
  <text class="nyr-title" x="820" y="145" text-anchor="middle">Équipement réseau</text>
  <text class="nyr-text" x="820" y="171" text-anchor="middle">Serveur de gestion</text>
  <text class="nyr-text" x="820" y="191" text-anchor="middle">Données modélisées en YANG</text>
  <path class="nyr-flow" d="M250 135 L362 95"/>
  <path class="nyr-flow" d="M250 185 L362 226"/>
  <path class="nyr-flow" d="M590 95 L702 135"/>
  <path class="nyr-flow" d="M590 226 L702 185"/>
  <text class="nyr-text" x="480" y="307" text-anchor="middle">YANG décrit les données ; NETCONF et RESTCONF permettent d'y accéder.</text>
  <text class="nyr-text" x="480" y="327" text-anchor="middle">La disponibilité des modèles et des opérations dépend de l'implémentation.</text>
</svg>

## 3.5 Tableau comparatif

| Élément | NETCONF | YANG | RESTCONF |
|---|---|---|---|
| Nature | Protocole de gestion | Langage de modélisation | Protocole de gestion basé sur HTTP |
| Rôle principal | Lire ou modifier les données | Décrire les données et contraintes | Accéder aux données sous forme de ressources |
| Encodage courant | XML | Définit le modèle, pas un unique protocole de transport | XML ou JSON selon l'implémentation |
| Transport courant | SSH, souvent sur le port TCP 830 | Aucun transport propre | HTTPS |
| Transactions de configuration | Opérations de datastore selon les capacités du serveur | Ne réalise pas lui-même les transactions | Méthodes HTTP et sémantique RESTCONF |
| Usage type | Gestion programmée de configuration | Contrat de structure des données | API adaptée aux applications HTTP |

**À retenir :** YANG définit la structure ; NETCONF et RESTCONF transportent des demandes et des données suivant cette structure.


# 4. Découvrir les modèles YANG

## 4.1 Qu'est-ce qu'un modèle ?

Un modèle YANG décrit les éléments de données que le client et le serveur peuvent comprendre.

Un modèle peut inclure :

- des conteneurs ;
- des listes ;
- des feuilles contenant une valeur ;
- des types simples ou dérivés ;
- des contraintes ;
- des données configurables ;
- des données en lecture seule ;
- des opérations et des notifications.

Un équipement peut prendre en charge plusieurs modèles YANG. La liste exacte dépend de son système, de sa version et des fonctionnalités disponibles.

## 4.2 Exemple de module YANG pédagogique

Créez `lab-interfaces.yang` :

```yang
module lab-interfaces {
  yang-version 1.1;

  namespace "urn:example:lab-interfaces";
  prefix li;

  organization
    "Laboratoire de formation réseau";

  description
    "Modèle pédagogique simplifié pour des interfaces.";

  revision 2026-01-01 {
    description
      "Première version pédagogique.";
  }

  container interfaces {
    description
      "Ensemble des interfaces du laboratoire.";

    list interface {
      key "name";

      leaf name {
        type string;
        description
          "Nom de l'interface.";
      }

      leaf description {
        type string;
        description
          "Description de l'interface.";
      }

      leaf enabled {
        type boolean;
        default true;
        description
          "État administratif demandé.";
      }
    }
  }
}
```

Ce module illustre les principaux éléments syntaxiques de YANG. Il ne remplace pas le modèle standard d'interfaces ni un modèle propre à un constructeur.

## 4.3 Comprendre la structure

`module` déclare le modèle.

`yang-version 1.1` indique la version de langage utilisée.

`namespace` identifie l'espace de noms du module.

`prefix` donne un préfixe utilisable dans certains contextes XML.

`container` regroupe des données.

`list` représente un ensemble d'entrées ayant une structure commune.

`key "name"` désigne la clé qui distingue les entrées de la liste.

`leaf` représente une valeur unique.

`type boolean` limite la valeur à `true` ou `false`.

`default true` définit une valeur par défaut dans les conditions prévues par YANG. Cela ne signifie pas qu'un client doit systématiquement écrire cette valeur sur le routeur.

## 4.4 Comment lire l'arbre ?

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="340" viewBox="0 0 960 340" role="img" aria-labelledby="yang-tree-title yang-tree-desc">
  <title id="yang-tree-title">Arbre de données YANG</title>
  <desc id="yang-tree-desc">Le conteneur interfaces possède une liste interface, laquelle contient les feuilles name, description et enabled. Les traits animés relient les niveaux de l'arbre sans déplacer de particules.</desc>
  <defs>
    <style>
      .yt-box{fill:#16263b;stroke:#60a5fa;stroke-width:2}
      .yt-leaf{fill:#123126;stroke:#4ade80;stroke-width:2}
      .yt-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .yt-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .yt-line{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:7 7;animation:yt-dash 2s linear infinite}
      @keyframes yt-dash{to{stroke-dashoffset:-28}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="338" rx="16" fill="#0b1220" stroke="#334155"/>
  <rect class="yt-box" x="330" y="24" width="300" height="55" rx="10"/>
  <text class="yt-title" x="480" y="57" text-anchor="middle">container interfaces</text>
  <path class="yt-line" d="M480 79 V111"/>
  <rect class="yt-box" x="330" y="112" width="300" height="55" rx="10"/>
  <text class="yt-title" x="480" y="145" text-anchor="middle">list interface · key name</text>
  <path class="yt-line" d="M480 167 V190 H165 V213"/>
  <path class="yt-line" d="M480 190 V213"/>
  <path class="yt-line" d="M480 190 H795 V213"/>
  <rect class="yt-leaf" x="40" y="214" width="250" height="62" rx="10"/>
  <text class="yt-title" x="165" y="240" text-anchor="middle">leaf name</text>
  <text class="yt-text" x="165" y="260" text-anchor="middle">type string</text>
  <rect class="yt-leaf" x="355" y="214" width="250" height="62" rx="10"/>
  <text class="yt-title" x="480" y="240" text-anchor="middle">leaf description</text>
  <text class="yt-text" x="480" y="260" text-anchor="middle">type string</text>
  <rect class="yt-leaf" x="670" y="214" width="250" height="62" rx="10"/>
  <text class="yt-title" x="795" y="240" text-anchor="middle">leaf enabled</text>
  <text class="yt-text" x="795" y="260" text-anchor="middle">type boolean</text>
  <text class="yt-text" x="480" y="312" text-anchor="middle">La hiérarchie définit où se trouve chaque donnée.</text>
</svg>

## 4.5 Modèles standard et modèles constructeurs

Il existe des modèles standardisés par l'IETF, par exemple `ietf-interfaces` pour la gestion générique des interfaces.

Les constructeurs peuvent aussi proposer leurs propres modules ou étendre des modèles existants.

Deux équipements peuvent donc exposer des données similaires avec des modèles, des révisions ou des capacités différentes. Avant d'écrire une automatisation, il faut connaître les modèles effectivement pris en charge par l'équipement ciblé.


# 5. Comprendre NETCONF

## 5.1 Comment la connexion fonctionne-t-elle ?

NETCONF utilise un échange de messages structurés. Dans le cas courant de NETCONF sur SSH, le client établit une session SSH et invoque le sous-système `netconf`. Le port TCP 830 est le port assigné par défaut à NETCONF sur SSH, mais un environnement peut utiliser une autre configuration autorisée.

Le client et le serveur échangent des messages `hello` contenant notamment leurs capacités.

Ces capacités permettent au client de connaître les fonctionnalités disponibles. Il ne doit pas supposer qu'un équipement prend en charge toutes les opérations optionnelles.

## 5.2 Les opérations fondamentales

| Opération | Fonction |
|---|---|
| `get` | Lire des données de configuration et d'état selon le filtre et les capacités |
| `get-config` | Lire un datastore de configuration |
| `edit-config` | Modifier des données de configuration |
| `copy-config` | Copier un datastore vers un autre, si pris en charge |
| `delete-config` | Supprimer un datastore lorsque l'opération est autorisée et disponible |
| `lock` / `unlock` | Verrouiller ou déverrouiller un datastore pris en charge |
| `validate` | Demander la validation de données lorsque la capacité correspondante est disponible |
| `commit` | Appliquer le contenu du datastore `candidate` au moyen de l'opération de commit, si disponible |
| `close-session` | Terminer proprement la session |

`candidate`, `startup`, `validate` et le commit confirmé sont liés à des capacités ou à des fonctionnalités qui ne sont pas universellement disponibles sur tous les équipements.

## 5.3 Comprendre les datastores

Un datastore est un espace logique dans lequel des données de configuration ou d'état sont accessibles.

Les noms que vous pouvez rencontrer comprennent :

- `running` : configuration active ;
- `candidate` : configuration candidate séparée lorsqu'elle est prise en charge ;
- `startup` : configuration prévue pour le démarrage lorsqu'elle est prise en charge.

Ne supposez pas que chaque serveur NETCONF expose tous ces datastores.

## 5.4 Exemple d'une requête de lecture

Une requête NETCONF est contenue dans un élément `rpc`. Voici un exemple illustratif de lecture d'une configuration avec un filtre sur le conteneur des interfaces :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="101"
     xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get-config>
    <source>
      <running/>
    </source>
    <filter type="subtree"
      xmlns:if="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      <if:interfaces/>
    </filter>
  </get-config>
</rpc>
```

Le serveur renvoie un `rpc-reply` qui contient les données demandées ou une erreur.

Cet exemple dépend de la prise en charge du modèle d'interfaces et de la forme de filtre acceptée par l'équipement. Le nom `ietf-interfaces` ne garantit pas que le serveur fournisse tous les éléments du modèle.

Le filtre sert à limiter les données demandées. Pour une automatisation à grande échelle, il est préférable de ne demander que les données nécessaires.


# 6. Comprendre RESTCONF

## 6.1 RESTCONF et HTTP

RESTCONF expose les données YANG à travers une API HTTP. L'adresse exacte dépend du serveur et de sa configuration.

Un serveur RESTCONF est normalement utilisé à travers HTTPS afin de protéger les échanges et l'authentification.

L'API permet de cibler une ressource correspondant à un conteneur, une liste ou un nœud défini par le modèle.

## 6.2 Les méthodes HTTP

| Méthode | Rôle général | Précaution |
|---|---|---|
| `GET` | Lire une ressource | Peut exposer des données sensibles |
| `POST` | Créer une entrée dans les contextes où cela est prévu | Vérifier la clé et les contraintes |
| `PUT` | Remplacer la ressource ciblée | Peut remplacer davantage de données que prévu |
| `PATCH` | Modifier partiellement une ressource | Valider précisément le changement |
| `DELETE` | Supprimer la ressource ciblée | Peut interrompre un service |

Ces opérations sont soumises au modèle, aux permissions et aux capacités du serveur.

## 6.3 Exemple de lecture avec curl

L'exemple suivant interroge un équipement de laboratoire qui prend en charge le modèle standard `ietf-interfaces`.

```bash
curl --silent --show-error \
  --cacert ./lab-ca.pem \
  --user "$RESTCONF_USER" \
  --header "Accept: application/yang-data+json" \
  "https://router-lab.example.net/restconf/data/ietf-interfaces:interfaces"
```

Avant l'exécution, configurez `RESTCONF_USER` selon votre environnement d'authentification. Avec l'option `--user`, curl peut demander le mot de passe de manière interactive si aucun mot de passe n'est fourni dans l'argument.

Le fichier `lab-ca.pem` représente ici le certificat d'autorité de confiance utilisé pour vérifier le certificat TLS du serveur.

N'ajoutez pas un mot de passe directement à une commande conservée dans l'historique du terminal. Pour un environnement professionnel, utilisez le mécanisme d'authentification approuvé par l'organisation.

L'adresse, le certificat et le modèle doivent être adaptés à votre équipement. Le nom `router-lab.example.net` est un exemple fictif.

## 6.4 Exemple de réponse JSON

Une réponse possible peut ressembler à ceci :

```json
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "Loopback0",
        "description": "Interface de laboratoire",
        "enabled": true
      }
    ]
  }
}
```

Cet extrait illustre une forme de représentation possible. Les propriétés visibles dépendent des données exposées par le serveur et du modèle utilisé.

Le JSON utilisé par RESTCONF doit respecter les règles d'encodage des données YANG. Il ne s'agit pas d'un objet JSON libre dans lequel les noms et les types peuvent être changés arbitrairement.


# 7. Comparer NETCONF et RESTCONF

NETCONF utilise des opérations de protocole explicitement définies, des messages XML et des datastores dont les capacités sont annoncées par le serveur.

RESTCONF expose des ressources HTTP basées sur les modèles YANG. Il convient naturellement aux applications et outils capables de faire des requêtes HTTP.

| Question | NETCONF | RESTCONF |
|---|---|---|
| Comment envoyer une demande ? | Opération NETCONF dans un message XML | Requête HTTP sur une ressource |
| Comment lire les données ? | `get` ou `get-config` | `GET` |
| Comment modifier les données ? | `edit-config` et autres opérations disponibles | `POST`, `PUT`, `PATCH` ou `DELETE` selon le cas |
| Comment gérer une configuration candidate ? | Opérations de datastore si supportées | Dépend des ressources RESTCONF exposées ; ne pas supposer une transaction équivalente |
| Comment découvrir les capacités ? | Échange `hello` et capacités NETCONF | Ressources et capacités RESTCONF/modèles exposés |
| Comment sécuriser ? | SSH dans le cas courant NETCONF/SSH | HTTPS avec validation du certificat et autorisations adaptées |

Les deux protocoles ne doivent pas être comparés uniquement sur la syntaxe des appels. Les capacités de l'équipement, les besoins transactionnels et la façon dont l'application utilise les données sont tout aussi importants.


# 8. Atelier pratique

## 8.1 Objectif

Vous allez concevoir les premières étapes de lecture d'un équipement de laboratoire. Vous ne modifierez pas sa configuration.

## Étape A — Identifier l'équipement

Documentez :

- la plateforme ;
- la version logicielle ;
- l'adresse de gestion ;
- les moyens d'authentification ;
- les modèles YANG disponibles ;
- les interfaces RESTCONF ou NETCONF activées.

N'activez pas ces interfaces sur un équipement de production sans l'approbation et les protections prévues par votre organisation.

## Étape B — Vérifier NETCONF

Vérifiez que le serveur NETCONF est activé, que le transport est autorisé depuis votre poste et que l'authentification fonctionne.

Sur un équipement compatible NETCONF sur SSH, le service utilise généralement le sous-système SSH `netconf` et le port TCP 830 par défaut.

Une connexion SSH interactive ordinaire n'est pas nécessairement une session NETCONF valide. Le client doit parler le protocole, et non interpréter des invites de CLI.

## Étape C — Découvrir les modèles

Recherchez la documentation de l'équipement et les informations de modèles exposées par sa plateforme.

L'objectif est d'identifier le nom du module, son espace de noms, sa révision et les fonctions prises en charge.

## Étape D — Lire les interfaces

Utilisez l'opération de lecture NETCONF ou la ressource RESTCONF appropriée, en vous limitant aux données nécessaires.

Consignez les résultats dans un rapport non sensible et notez les limites observées.

## Étape E — Comparer les données

Vérifiez qu'un même concept — par exemple le nom d'une interface — est correctement identifié et analysé, en tenant compte du modèle effectivement utilisé.

Ne supposez pas que les deux protocoles exposent automatiquement toutes les mêmes fonctions ou toutes les mêmes données.


# 9. Sécurité et bonnes pratiques

## 9.1 Authentification et transport

NETCONF sur SSH utilise un transport chiffré et une authentification SSH.

RESTCONF doit être déployé avec HTTPS et une validation appropriée du certificat TLS.

Les protections du transport ne remplacent pas les contrôles d'accès. Un utilisateur authentifié ne devrait pas recevoir automatiquement les droits nécessaires pour modifier toute la configuration.

## 9.2 Moindre privilège

Séparez les rôles de lecture et de modification lorsque la plateforme le permet.

Pour un premier exercice, utilisez un compte de lecture seule. Testez les modifications dans un laboratoire isolé, pas directement sur l'infrastructure de production.

## 9.3 Risques à connaître

- **Exposition des données :** les réponses peuvent révéler la topologie, les adresses et des paramètres sensibles.
- **Écriture involontaire :** `PUT`, `PATCH`, `POST` et les opérations NETCONF de modification peuvent altérer l'état réel.
- **Certificats non vérifiés :** désactiver la vérification TLS expose à des risques d'interception.
- **Compatibilité supposée :** un client peut échouer si le modèle ou l'opération attendue n'est pas pris en charge.
- **Données trop volumineuses :** des lectures sans filtre peuvent produire des réponses très importantes.
- **Permissions excessives :** un compte d'automatisation compromis peut causer des changements non autorisés.

La première règle est simple : vérifier les capacités, limiter les droits et commencer par les lectures.


# 10. Évaluation corrigée

## Questions

1. Quel est le rôle de YANG ?
2. NETCONF et RESTCONF sont-ils des langages de modélisation ?
3. Quel encodage est couramment utilisé par NETCONF ?
4. Quel protocole HTTP est utilisé par RESTCONF ?
5. À quoi sert une liste dans un modèle YANG ?
6. Quelle différence existe entre configuration et état opérationnel ?
7. Pourquoi un modèle présent dans la documentation n'est-il pas une garantie de disponibilité sur l'équipement ?
8. Pourquoi utiliser HTTPS avec RESTCONF ?
9. Quel est l'intérêt d'une requête filtrée ?
10. Pourquoi commencer par des opérations de lecture ?

## Corrigé

1. YANG décrit la structure, les types et les contraintes des données de gestion.
2. Non. NETCONF et RESTCONF sont des protocoles de gestion.
3. XML.
4. HTTP, normalement protégé par TLS via HTTPS.
5. Elle représente une collection d'entrées structurées, souvent identifiées par une clé.
6. La configuration exprime les paramètres gérés ; l'état opérationnel reflète les conditions réellement observées sur le système.
7. La prise en charge dépend de la plateforme, de la version logicielle et des modèles activés.
8. HTTPS protège le transport et permet de vérifier l'identité du serveur si les certificats sont correctement contrôlés.
9. Elle réduit les données retournées et facilite l'analyse.
10. La lecture permet de découvrir la structure et les capacités sans prendre le risque d'un changement opérationnel.


# 11. Préparation du niveau intermédiaire

Le niveau intermédiaire approfondira :

- l'écriture et la validation de modèles YANG ;
- les types, clés, contraintes et relations ;
- les capacités annoncées par NETCONF ;
- les datastores et le cycle de configuration ;
- les requêtes RESTCONF de lecture et d'écriture ;
- les scripts Python pour les deux protocoles ;
- les tests automatisés de modèles et de données ;
- le traitement des erreurs et les permissions.

Le but du niveau débutant est de comprendre la séparation entre modèle de données et protocole de gestion.

**À retenir : YANG structure, NETCONF opère sur des données structurées et RESTCONF les expose à travers des ressources HTTP.**


## Références officielles

- NETCONF — RFC 6241 : https://www.rfc-editor.org/rfc/rfc6241.html
- NETCONF sur SSH — RFC 6242 : https://www.rfc-editor.org/rfc/rfc6242.html
- YANG 1.1 — RFC 7950 : https://www.rfc-editor.org/rfc/rfc7950.html
- RESTCONF — RFC 8040 : https://www.rfc-editor.org/rfc/rfc8040.html
- Encodage JSON des données YANG — RFC 7951 : https://www.rfc-editor.org/rfc/rfc7951.html
- Modèle standard des interfaces — RFC 8343 : https://www.rfc-editor.org/rfc/rfc8343.html

**Fichier :** `netconf-yang-debutant.md`  
**Niveau :** Débutant  
**Fin du cours**
