
# NETCONF, YANG et RESTCONF — Niveau intermédiaire

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** comprendre les rôles de YANG, NETCONF et RESTCONF, XML, JSON et les bases des modèles de données.  
> **Objectif :** écrire et valider des modèles YANG, exploiter les capacités des équipements, automatiser des lectures avec Python et comprendre les opérations de modification contrôlée.


## Sommaire

1. Architecture de gestion pilotée par les modèles
2. Écrire des modèles YANG plus robustes
3. Types, contraintes et relations entre les données
4. Valider les modèles avec des outils
5. Découvrir les capacités et modèles d'un serveur NETCONF
6. Automatiser des lectures NETCONF avec Python
7. Lire et modifier les ressources RESTCONF
8. Gérer les erreurs et les modifications concurrentes
9. Sécuriser les clients et les permissions
10. Atelier d'intégration
11. Diagnostic
12. Évaluation corrigée
13. Préparation du niveau expert


# 1. Architecture de gestion pilotée par les modèles

## 1.1 De la découverte à l'automatisation

Au niveau débutant, nous avons appris qu'un modèle YANG décrit les données et que NETCONF ou RESTCONF permet d'y accéder.

Le niveau intermédiaire introduit une démarche plus systématique :

1. découvrir les modèles disponibles ;
2. vérifier leurs versions et leurs capacités ;
3. comprendre les types et les contraintes ;
4. valider les données avant de les envoyer ;
5. utiliser un client adapté au protocole ;
6. contrôler les réponses et les erreurs ;
7. vérifier l'état réel après une modification autorisée.

Il ne suffit pas qu'une requête soit correctement encodée en XML ou en JSON. Les données doivent également correspondre au modèle effectivement pris en charge par le serveur.

## 1.2 Architecture fonctionnelle

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="360" viewBox="0 0 1000 360" role="img" aria-labelledby="mid-arch-title mid-arch-desc">
  <title id="mid-arch-title">Chaîne intermédiaire de gestion par modèles</title>
  <desc id="mid-arch-desc">Les modèles YANG et les données attendues passent par une validation avant qu'un client choisisse NETCONF ou RESTCONF. Le serveur de gestion applique ses modèles, permissions et opérations prises en charge. Des contrôles vérifient ensuite la réponse et l'état observé.</desc>
  <defs>
    <marker id="mid-arch-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .ma-box{fill:#16263b;stroke:#60a5fa;stroke-width:2}
      .ma-check{fill:#123126;stroke:#4ade80;stroke-width:2}
      .ma-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .ma-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .ma-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#mid-arch-arrow);animation:ma-dash 1.8s linear infinite}
      @keyframes ma-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DE LA STRUCTURE À LA VALIDATION OPÉRATIONNELLE</text>
  <rect class="ma-box" x="25" y="85" width="190" height="84" rx="10"/>
  <text class="ma-title" x="120" y="115" text-anchor="middle">Modèle YANG</text>
  <text class="ma-text" x="120" y="139" text-anchor="middle">Schéma et contraintes</text>
  <rect class="ma-check" x="270" y="85" width="190" height="84" rx="10"/>
  <text class="ma-title" x="365" y="115" text-anchor="middle">Validation locale</text>
  <text class="ma-text" x="365" y="139" text-anchor="middle">Données et types</text>
  <rect class="ma-box" x="515" y="55" width="190" height="64" rx="10"/>
  <text class="ma-title" x="610" y="81" text-anchor="middle">Client NETCONF</text>
  <text class="ma-text" x="610" y="101" text-anchor="middle">RPC et XML</text>
  <rect class="ma-box" x="515" y="137" width="190" height="64" rx="10"/>
  <text class="ma-title" x="610" y="163" text-anchor="middle">Client RESTCONF</text>
  <text class="ma-text" x="610" y="183" text-anchor="middle">HTTP et données YANG</text>
  <rect class="ma-box" x="760" y="85" width="215" height="84" rx="10"/>
  <text class="ma-title" x="867" y="115" text-anchor="middle">Serveur réseau</text>
  <text class="ma-text" x="867" y="139" text-anchor="middle">Modèles et permissions</text>
  <path class="ma-flow" d="M215 127 H262"/>
  <path class="ma-flow" d="M460 112 L507 87"/>
  <path class="ma-flow" d="M460 142 L507 169"/>
  <path class="ma-flow" d="M705 87 L752 112"/>
  <path class="ma-flow" d="M705 169 L752 142"/>
  <rect class="ma-check" x="270" y="245" width="460" height="67" rx="10"/>
  <text class="ma-title" x="500" y="272" text-anchor="middle">Vérification du résultat</text>
  <text class="ma-text" x="500" y="293" text-anchor="middle">Réponse, état attendu, erreurs et journal de l'action</text>
  <path class="ma-flow" d="M867 169 V219 H730 V278"/>
  <text class="ma-text" x="500" y="337" text-anchor="middle">Une réponse valide sur le plan du protocole ne garantit pas le résultat fonctionnel attendu.</text>
</svg>

## 1.3 Le modèle réellement pris en charge fait autorité

Un modèle standardisé facilite l'interopérabilité, mais il faut vérifier :

- le nom du module ;
- son espace de noms ;
- sa révision ;
- les modules importés ;
- les éventuels `features` ;
- les écarts ou extensions du constructeur ;
- les opérations et datastores annoncés par le serveur.

Un client ne doit pas construire des requêtes uniquement à partir d'une documentation générale si le serveur expose un ensemble de modèles différent.


# 2. Écrire des modèles YANG plus robustes

## 2.1 Les éléments courants

YANG distingue plusieurs catégories de nœuds.

| Élément | Usage |
|---|---|
| `container` | Regrouper des nœuds |
| `list` | Décrire une collection d'entrées |
| `leaf` | Décrire une valeur unique |
| `leaf-list` | Décrire une liste de valeurs simples |
| `choice` / `case` | Décrire des alternatives mutuellement organisées |
| `typedef` | Réutiliser un type nommé |
| `grouping` / `uses` | Réutiliser une structure |
| `identity` | Définir une identité extensible |
| `augment` | Ajouter des nœuds à un modèle existant |
| `must` | Ajouter une contrainte exprimée par une expression XPath |
| `when` | Conditionner la présence d'un nœud |
| `description` | Documenter l'intention d'un nœud |

Les contraintes doivent être conçues en fonction du besoin métier. Une restriction syntaxique ne suffit pas à prouver qu'une configuration est sûre dans tous les contextes.

## 2.2 Exemple de modèle avec contraintes

Créez `lab-port-policy.yang` :

```yang
module lab-port-policy {
  yang-version 1.1;

  namespace "urn:example:lab-port-policy";
  prefix lpp;

  description
    "Modèle pédagogique d'une politique de ports.";

  revision 2026-01-01 {
    description "Première version du modèle.";
  }

  typedef vlan-id {
    type uint16 {
      range "1..4094";
    }
    description
      "Identifiant VLAN valide pour l'exercice.";
  }

  container port-policy {
    list port {
      key "name";

      leaf name {
        type string {
          length "1..64";
        }
      }

      leaf access-vlan {
        type vlan-id;
        mandatory true;
      }

      leaf description {
        type string {
          length "0..128";
        }
      }

      leaf enabled {
        type boolean;
        default true;
      }
    }
  }
}
```

Ce modèle définit une structure et restreint les valeurs acceptables pour le VLAN. Il reste pédagogique : une valeur comprise entre 1 et 4094 ne prouve pas que le VLAN est autorisé dans une organisation ou disponible sur un équipement particulier.

Les politiques métier doivent donc être ajoutées explicitement au processus de validation lorsqu'elles ne peuvent pas être exprimées dans le modèle seul.

## 2.3 Utiliser les contraintes intelligemment

`range` limite les valeurs numériques.

`length` impose une longueur de chaîne.

`pattern` permet de vérifier un motif textuel.

`mandatory true` exige la présence d'un nœud dans les contextes prévus par YANG.

`must` exprime une contrainte sur les données accessibles à son contexte.

`when` conditionne la présence ou l'applicabilité d'un nœud.

`leafref` exprime une référence vers une autre donnée du modèle.

Il faut également comprendre la différence entre une valeur absente et une valeur présente mais vide. La façon correcte de traiter ces situations dépend du type et des propriétés déclarées.

## 2.4 Réutiliser des structures

Les mécanismes `typedef`, `grouping` et `uses` aident à éviter la duplication de définitions.

Cette réutilisation peut améliorer la cohérence, mais elle introduit aussi des dépendances. Une évolution d'un type partagé peut affecter plusieurs modèles.

Avant de modifier une définition commune, identifiez ses consommateurs et ajoutez des tests couvrant les usages pertinents.

## 2.5 Extensions et écarts

`augment` permet d'ajouter des nœuds à un arbre existant.

`deviation` permet de décrire certains écarts par rapport à une définition de référence.

Ces mécanismes peuvent aider à intégrer les extensions ou limites d'une plateforme, mais ne doivent pas être utilisés pour masquer silencieusement des différences importantes.

Une automatisation portable doit documenter les hypothèses et identifier les modèles nécessaires à chaque équipement.


# 3. Types, contraintes et relations entre les données

## 3.1 Types standards et types dérivés

YANG comprend des types simples : chaînes, booléens, nombres signés ou non signés, énumérations, bits, types vides et identifiants de références.

D'autres modules définissent des types réutilisables, notamment pour les adresses IP et les préfixes.

Avant de développer une validation Python, vérifiez si le modèle déclare déjà un type adapté. Réimplémenter partiellement les règles d'un type standard peut introduire des divergences.

## 3.2 Les identités et `identityref`

Un `identity` permet de définir une valeur extensible. `identityref` représente une référence à une identité autorisée.

Ce mécanisme est utilisé dans certains modèles réseau pour représenter des types d'interfaces ou des choix technologiques.

Dans les encodages XML ou JSON, la valeur doit respecter les règles de l'identité et de l'espace de noms. Une chaîne ressemblant à un nom de technologie ne suffit pas forcément.

## 3.3 Relations entre les données

Une propriété peut être individuellement valide tout en étant incohérente avec les autres données.

Exemples :

- un identifiant VLAN est compris dans la plage numérique, mais n'est pas autorisé sur le site ;
- une interface existe dans l'inventaire, mais pas sur l'équipement ;
- une référence vers une autre entrée n'existe pas ;
- une combinaison de paramètres est interdite par la politique réseau ;
- une option de configuration dépend d'une fonctionnalité qui n'est pas disponible.

Il faut séparer les contrôles pouvant être décrits directement en YANG des vérifications opérationnelles ou métier qui nécessitent d'autres informations.


# 4. Valider les modèles avec des outils

## 4.1 Utiliser un validateur YANG

`pyang` est un outil permettant notamment d'analyser et de vérifier des modules YANG. `yanglint`, fourni avec libyang, peut aussi servir à analyser des modèles et certaines données structurées.

Installez les outils selon les instructions officielles et la méthode adaptée à votre système.

Pour analyser un fichier avec pyang :

```bash
pyang lab-port-policy.yang
```

Pour afficher l'arbre du modèle :

```bash
pyang -f tree lab-port-policy.yang
```

Pour analyser un module qui importe d'autres modules, configurez le chemin des modèles avec l'option `-p` selon la structure de votre dépôt.

Les messages produits doivent être examinés : un avertissement et une erreur ne sont pas interchangeables.

## 4.2 Valider les modèles réellement disponibles

Pour un équipement de laboratoire, récupérez les modules correspondant à sa plateforme et à sa version.

Vérifiez :

- que les imports peuvent être résolus ;
- que la révision nécessaire est disponible ;
- que les fonctionnalités conditionnelles sont comprises ;
- que l'outil et le serveur interprètent les mêmes modèles ;
- que les validations des données sont réalisées avec le schéma attendu.

Ne remplacez pas silencieusement les modèles fournis par un appareil par une version téléchargée différente.

## 4.3 Contrôles de qualité du dépôt

Une CI de modèles peut exécuter :

1. l'analyse syntaxique de chaque modèle ;
2. la résolution des imports ;
3. les contrôles de cohérence ;
4. les tests des contraintes importantes ;
5. les tests des données d'exemple ;
6. la comparaison entre les versions lorsque des modifications sont proposées.

Un changement de modèle peut modifier le comportement des clients sans changer le protocole. C'est pourquoi les révisions et la compatibilité doivent être traitées comme des éléments importants du processus.


# 5. Découvrir les capacités et modèles d'un serveur NETCONF

## 5.1 Échange `hello`

Au démarrage d'une session NETCONF, le client et le serveur échangent des messages `hello`.

Ces messages annoncent les capacités et les espaces de noms de protocole pris en charge.

Un client peut notamment vérifier la présence des capacités associées à :

- `candidate` ;
- `validate` ;
- `confirmed-commit` ;
- `rollback-on-error` ;
- des fonctionnalités supplémentaires liées aux datastores ou aux opérations.

La présence d'une capacité doit être interprétée selon sa définition standard et sa version. Le client ne doit pas déduire qu'une option existe uniquement parce qu'un constructeur la propose sur certains modèles.

## 5.2 Capacités et modèle de données

Les capacités de protocole et les modèles YANG décrivent deux dimensions différentes.

Les capacités NETCONF indiquent les opérations et mécanismes de protocole disponibles.

Les modèles YANG décrivent les données que le serveur peut interpréter.

Une automatisation doit connaître les deux.

## 5.3 La YANG Library

La YANG Library fournit des informations sur les modules et les schémas utilisés par un serveur, selon le mécanisme implémenté et la version du standard.

Elle aide le client à découvrir les modèles pertinents plutôt que de deviner les données exposées.

Pour un client robuste, cette découverte est particulièrement utile lorsqu'il gère des équipements dont les fonctionnalités ou les modèles varient.

Référence : RFC 8525, YANG Library. Vérifiez les mises à jour et la version prise en charge par votre implémentation.


# 6. Automatiser des lectures NETCONF avec Python

## 6.1 Installation de ncclient

`ncclient` est une bibliothèque Python couramment utilisée comme client NETCONF.

Installez-la dans un environnement Python isolé, selon les instructions de sa documentation officielle et la politique de dépendances de votre projet.

```bash
python -m venv .venv
```

Activez l'environnement, puis installez la dépendance adaptée :

```bash
python -m pip install ncclient
```

En production, verrouillez les versions approuvées dans le système de dépendances du projet.

## 6.2 Exemple de lecture de configuration

L'exemple ci-dessous se limite à une lecture. Il suppose que le compte a le droit de lire la configuration et que l'équipement prend en charge NETCONF sur SSH.

Définissez les variables `NETCONF_HOST`, `NETCONF_USER` et `NETCONF_PASSWORD` via un mécanisme sécurisé. N'écrivez pas les identifiants en clair dans le script.

```python
import os
from ncclient import manager


host = os.environ["NETCONF_HOST"]
username = os.environ["NETCONF_USER"]
password = os.environ["NETCONF_PASSWORD"]

with manager.connect(
    host=host,
    port=830,
    username=username,
    password=password,
    hostkey_verify=True,
    device_params={"name": "default"},
    timeout=30,
    allow_agent=False,
    look_for_keys=False,
) as session:
    print("Capacités du serveur :")
    for capability in session.server_capabilities:
        print(capability)

    reply = session.get_config(source="running")
    print("Configuration reçue :")
    print(reply.data_xml)
```

### Points importants

- `hostkey_verify=True` demande la vérification de la clé d'hôte SSH selon la configuration de l'environnement.
- Les identifiants sont lus dans l'environnement du processus et non écrits dans le code.
- `get_config(source="running")` peut retourner une configuration volumineuse et sensible. Utilisez un filtre adapté à votre besoin lorsque c'est possible.
- La réussite de la connexion et de la lecture ne prouve pas que le contenu reçu correspond à l'état souhaité.
- Certains équipements nécessitent un nom de plateforme ou des paramètres de session spécifiques à ncclient.

N'utilisez cet exemple que sur un équipement de laboratoire ou dans un environnement pour lequel l'accès de lecture a été explicitement autorisé.

## 6.3 Filtrer les lectures

L'objectif est de limiter la réponse aux données nécessaires. En NETCONF, les opérations de lecture peuvent utiliser des filtres selon les règles du protocole et les capacités prises en charge.

Un filtre mal construit peut retourner un résultat vide sans que la connexion soit en panne. Il faut donc distinguer :

- connexion impossible ;
- échec d'authentification ;
- erreur RPC ;
- réponse valide mais vide ;
- réponse contenant des données ;
- données reçues mais incompatibles avec les attentes du client.

Un programme ne doit pas interpréter tous ces résultats comme un même échec générique.


# 7. Lire et modifier les ressources RESTCONF

## 7.1 Lecture ciblée

Une requête GET permet d'obtenir une ressource identifiée par son chemin RESTCONF.

Exemple de lecture :

```bash
curl --silent --show-error \
  --cacert ./lab-ca.pem \
  --user "$RESTCONF_USER" \
  --header "Accept: application/yang-data+json" \
  "https://router-lab.example.net/restconf/data/ietf-interfaces:interfaces/interface=Loopback0"
```

Le chemin d'exemple dépend du serveur et du modèle disponibles. Adaptez l'identité de l'interface et la façon dont les caractères spéciaux sont encodés dans l'URI.

Les modèles standard définissent des chemins logiques, mais le client doit connaître les modèles pris en charge par le serveur et utiliser le chemin correspondant à la donnée réellement recherchée.

## 7.2 Lire une réponse de manière robuste

Un client ne doit pas se limiter au corps de la réponse. Il doit également examiner :

- le code HTTP ;
- le type de contenu retourné ;
- le corps et sa structure ;
- les éventuels détails d'erreur ;
- le temps de réponse ;
- la ressource ciblée.

Une réponse `401` suggère un problème d'authentification, tandis qu'une réponse `403` signale généralement un refus d'autorisation. Une réponse `404` peut correspondre à une ressource absente ou à un chemin incorrect. D'autres codes peuvent être renvoyés selon le contexte.

Ne convertissez pas toute réponse non-2xx en message générique sans préserver les éléments utiles au diagnostic.

## 7.3 Comprendre les écritures RESTCONF

`POST`, `PUT`, `PATCH` et `DELETE` modifient les données lorsque le serveur autorise l'opération et que les contraintes du modèle sont satisfaites.

Le choix dépend du besoin :

- `POST` : créer une entrée ou une ressource dans le contexte prévu ;
- `PUT` : créer ou remplacer la ressource ciblée selon la sémantique du protocole ;
- `PATCH` : modifier partiellement la ressource ;
- `DELETE` : supprimer la ressource ciblée.

Une opération valide sur le plan HTTP peut néanmoins être rejetée par le modèle, les contraintes métier ou les permissions.

## 7.4 Exemple pédagogique de PATCH

Cet exemple illustre une modification de description sur une interface d'un équipement de laboratoire. Il suppose que le serveur expose le modèle standard `ietf-interfaces`, que le chemin correspond à une interface existante et que le compte possède les droits requis.

```bash
curl --silent --show-error \
  --request PATCH \
  --cacert ./lab-ca.pem \
  --user "$RESTCONF_USER" \
  --header "Accept: application/yang-data+json" \
  --header "Content-Type: application/yang-data+json" \
  --data '{
    "ietf-interfaces:interface": [
      {
        "name": "Loopback0",
        "description": "Interface de laboratoire"
      }
    ]
  }' \
  "https://router-lab.example.net/restconf/data/ietf-interfaces:interfaces/interface=Loopback0"
```

**Ne lancez pas cette commande directement sur la production.** Vérifiez la structure attendue par la ressource et le serveur, testez d'abord en laboratoire et adaptez le corps à l'implémentation utilisée.

L'exemple illustre la forme d'une demande. Il ne garantit pas que chaque serveur accepte exactement les mêmes sous-ensembles, extensions et règles de mise à jour.

## 7.5 Concurrence et fraîcheur des données

Entre la lecture et l'écriture, un autre client peut modifier la même ressource.

Lorsque le serveur expose des mécanismes de validation conditionnelle HTTP, l'utilisation d'un `ETag` et d'un en-tête `If-Match` peut contribuer à prévenir l'application d'une écriture fondée sur un état périmé.

Cette protection dépend des ressources et des fonctionnalités prises en charge. Il ne faut pas supposer que tous les serveurs fournissent le même comportement pour toutes les opérations.


# 8. Gérer les erreurs et les modifications concurrentes

## 8.1 Les erreurs se produisent à plusieurs niveaux

Une requête peut échouer :

1. avant d'atteindre le serveur ;
2. pendant l'établissement de la session ;
3. pendant l'authentification ;
4. au niveau du transport ou du protocole ;
5. lors de l'analyse des données ;
6. lors de la vérification des contraintes ;
7. à cause des permissions ;
8. pendant l'application de la modification ;
9. pendant la vérification post-opérationnelle.

L'outil d'automatisation doit préserver suffisamment d'informations pour distinguer ces situations.

## 8.2 Gestion robuste des erreurs

Pour chaque opération importante :

- définir les erreurs attendues ;
- imposer des délais d'attente ;
- limiter les tentatives automatiques ;
- ne pas réessayer aveuglément une opération d'écriture ;
- conserver des journaux sans secrets ;
- vérifier l'état après une réponse ambiguë ;
- fournir un résultat distinct pour succès, échec et résultat inconnu.

Une perte de connexion après l'envoi d'une écriture ne permet pas toujours de savoir si le serveur a appliqué le changement avant la rupture. Avant de répéter l'opération, il peut être nécessaire de lire l'état actuel.

## 8.3 NETCONF et la gestion de configuration

Si le serveur annonce la capacité `candidate`, une application peut préparer des modifications dans ce datastore avant de les appliquer selon le mécanisme de commit supporté.

Si `candidate` ou `validate` n'est pas disponible, le client doit utiliser une stratégie adaptée aux capacités réellement exposées. Il ne doit pas inventer un cycle de transaction que le serveur ne prend pas en charge.


# 9. Sécuriser les clients et les permissions

## 9.1 Comptes et autorisations

Créez des comptes dédiés aux opérations d'automatisation lorsque la plateforme le permet.

Séparez au minimum les droits de lecture et les droits d'écriture pour les usages qui le justifient.

Le modèle d'accès peut permettre de limiter les opérations, les ressources ou les portions de données qu'un utilisateur est autorisé à lire ou modifier.

## 9.2 Protéger les certificats et les clés

Ne désactivez pas la vérification des clés d'hôte SSH ou des certificats TLS pour faire fonctionner un script.

Documentez l'installation des autorités de confiance, la rotation des certificats et la gestion des clés. En cas d'échec de validation de l'identité du serveur, interrompez l'opération et corrigez la cause.

## 9.3 Secrets et journalisation

Ne consignez pas les mots de passe, jetons ou clés privées dans les journaux.

Avant de publier un XML ou un JSON de réponse dans un rapport, examinez s'il contient des éléments sensibles : les réponses de configuration peuvent révéler des informations d'exploitation importantes.


# 10. Atelier d'intégration

## Situation

Un laboratoire possède un équipement qui expose NETCONF et RESTCONF. L'équipe veut collecter le nom et la description de certaines interfaces, puis vérifier que les données correspondent à un inventaire prévu.

## Étape A — Découverte

Identifiez les modèles et les capacités du serveur.

N'inventez pas les chemins RESTCONF ou les noms de modules. Utilisez les informations exposées par l'appareil et sa documentation.

## Étape B — Lecture

Écrivez un client qui effectue une lecture limitée. Pour NETCONF, exploitez une opération de lecture et analysez la réponse structurée. Pour RESTCONF, inspectez la réponse HTTP, puis parsez les données JSON ou XML selon le format demandé.

## Étape C — Normalisation

Transformez les résultats en un format interne cohérent, par exemple une liste d'objets contenant :

```json
[
  {
    "name": "Loopback0",
    "description": "Interface de laboratoire"
  }
]
```

Ce format interne ne remplace pas le modèle de l'équipement. Il sert uniquement à faciliter les comparaisons dans votre application.

## Étape D — Contrôle de cohérence

Comparez les données collectées à l'inventaire attendu.

Distinguez clairement :

- une interface absente ;
- une description différente ;
- une donnée indisponible ;
- une erreur de lecture ;
- un résultat incomplet.

## Étape E — Rapport

Produisez un rapport qui présente les écarts sans exposer d'identifiants ou de configurations sensibles.

L'exercice est réussi lorsque le client peut effectuer la lecture de manière reproductible et expliquer précisément les écarts détectés.

Aucune écriture réseau n'est nécessaire pour valider cet atelier.


# 11. Diagnostic

## 11.1 Le client NETCONF se connecte, mais le filtre ne renvoie rien

Vérifiez le namespace XML, la forme du filtre, les modèles disponibles et les autorisations. Une réponse vide n'est pas nécessairement une panne du transport.

## 11.2 Le serveur rejette une valeur YANG

Vérifiez les types, les contraintes, les références et les dépendances. Si le modèle diffère de celui attendu par le client, mettez à jour les hypothèses de l'automatisation.

## 11.3 RESTCONF renvoie une erreur HTTP

Inspectez le code, les en-têtes et le message d'erreur. Vérifiez le chemin, l'authentification, l'autorisation, le format de contenu et les contraintes du modèle.

## 11.4 Le changement semble accepté mais le résultat n'est pas visible

L'acceptation d'une requête ne doit pas remplacer la vérification de l'état attendu. Interrogez la ressource concernée et établissez si la valeur observée correspond réellement à la modification demandée.

## 11.5 La lecture fonctionne sur un appareil et échoue sur un autre

Comparez les modèles, leurs révisions, les capacités, la version logicielle et les permissions. Deux équipements compatibles avec un même protocole ne prennent pas nécessairement en charge les mêmes modules.


# 12. Évaluation corrigée

## Questions

1. Pourquoi faut-il connaître les modèles YANG disponibles avant d'automatiser un équipement ?
2. À quoi sert `leafref` ?
3. Quelle différence existe entre une contrainte de modèle et une règle métier ?
4. Pourquoi la découverte des capacités NETCONF est-elle indispensable ?
5. Quel est l'intérêt de `pyang` ?
6. Pourquoi ne faut-il pas lire systématiquement toute la configuration ?
7. Pourquoi une écriture peut-elle échouer alors que le JSON semble valide ?
8. Comment reconnaître les principales erreurs HTTP de RESTCONF ?
9. Quel risque existe si un programme réessaie immédiatement une écriture après une rupture de connexion ?
10. Quel est l'intérêt d'une vérification après modification ?

## Corrigé

1. Pour connaître les données, les types, les contraintes et les fonctions réellement exposés.
2. À représenter une référence vers une autre donnée selon les règles du modèle.
3. Une contrainte de modèle décrit des règles de données. Une règle métier peut nécessiter des connaissances supplémentaires sur la politique ou l'état du réseau.
4. Elle permet d'utiliser uniquement les opérations effectivement prises en charge.
5. Il peut analyser des modèles YANG et aider à vérifier leur cohérence.
6. Pour réduire le volume, limiter l'exposition d'informations sensibles et faciliter l'analyse.
7. Le contenu peut violer le modèle, les permissions ou les contraintes du serveur.
8. En inspectant le statut HTTP et les détails d'erreur, puis en vérifiant le contexte.
9. L'opération initiale peut avoir été appliquée avant la perte de connexion ; un nouvel envoi peut provoquer un effet inattendu.
10. Elle confirme que le résultat réel correspond au résultat attendu.


# 13. Préparation du niveau expert

Le niveau expert approfondira :

- les datastores et l'architecture NMDA ;
- les transactions NETCONF et le commit confirmé ;
- le verrouillage et la gestion des changements concurrents ;
- le `rollback-on-error` lorsque disponible ;
- la découverte approfondie des modèles et des schémas ;
- la sécurisation des API et la séparation des rôles ;
- les différences de comportement entre serveurs ;
- l'idempotence et la récupération après réponse ambiguë ;
- les tests d'intégration et de bout en bout ;
- l'observabilité des opérations de gestion.

**Le niveau intermédiaire transforme les notions de protocole en clients et validations réutilisables. Le niveau expert construit des opérations sûres, transactionnelles lorsque possible, et adaptées aux capacités réelles de chaque équipement.**


## Références officielles

- YANG 1.1 — RFC 7950 : https://www.rfc-editor.org/rfc/rfc7950.html
- NETCONF — RFC 6241 : https://www.rfc-editor.org/rfc/rfc6241.html
- RESTCONF — RFC 8040 : https://www.rfc-editor.org/rfc/rfc8040.html
- YANG Library — RFC 8525 : https://www.rfc-editor.org/rfc/rfc8525.html
- NMDA — RFC 8342 : https://www.rfc-editor.org/rfc/rfc8342.html
- Modèle d'interfaces — RFC 8343 : https://www.rfc-editor.org/rfc/rfc8343.html
- pyang : https://github.com/mbj4668/pyang
- ncclient : https://github.com/ncclient/ncclient
- Documentation Python : https://docs.python.org/3/

**Fichier :** `netconf-yang-intermediaire.md`  
**Niveau :** Intermédiaire  
**Fin du cours**
