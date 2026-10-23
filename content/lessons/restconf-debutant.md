# RESTCONF et NETCONF — Débutant
## Comprendre les API réseau, lire les données YANG et effectuer ses premières requêtes

**Nom du fichier :** `restconf-debutant.md`  
**Niveau :** Débutant  
**Parcours :** Débutant → Intermédiaire → Expert  
**Prérequis :** notions de réseau IP, HTTP, JSON et XML  
**Langage des exemples :** Python, cURL, XML et JSON  
**Objectif :** apprendre à interroger un équipement réseau et comprendre les mécanismes qui permettent ensuite de l'automatiser sans dépendre exclusivement de commandes CLI.

---

# SOMMAIRE

1. Comprendre pourquoi les API réseau existent
2. Comprendre l'architecture model-driven
3. YANG : le langage qui décrit les données réseau
4. NETCONF : le protocole de gestion XML
5. RESTCONF : l'API de gestion basée sur HTTP
6. Comparer RESTCONF et NETCONF
7. Préparer son environnement de laboratoire
8. Réaliser sa première requête RESTCONF
9. Interroger NETCONF avec Python
10. Lire les données, distinguer configuration et état opérationnel
11. Comprendre les erreurs et les réponses
12. Sécurité des API de gestion
13. Laboratoires progressifs
14. Projet final guidé
15. Dépannage
16. Exercices d'évaluation
17. Glossaire
18. Références officielles

---

# 1. COMPRENDRE POURQUOI LES API RÉSEAU EXISTENT

## 1.1. La gestion traditionnelle par CLI

Dans les cours d'administration réseau, vous avez probablement utilisé des commandes comme :

```text
show ip interface brief
show version
show ip route
show running-config
```

Ces commandes sont pratiques pour un administrateur. Elles permettent d'obtenir rapidement des informations sur un routeur ou un commutateur.

Mais imaginons que vous deviez interroger 200 équipements tous les matins.

Une méthode manuelle obligerait à ouvrir 200 sessions, exécuter plusieurs commandes, copier les résultats, les comparer et rédiger un rapport.

L'opération serait répétitive, lente et exposée aux erreurs humaines.

Un script Python utilisant SSH peut déjà automatiser cette démarche. Toutefois, il doit souvent reconnaître les invites du terminal, interpréter du texte et gérer les particularités de la CLI.

Par exemple, le résultat suivant est lisible par un humain :

```text
Interface              IP-Address      Status
GigabitEthernet0/0      192.0.2.1       up
GigabitEthernet0/1      unassigned      down
```

Mais un programme doit savoir où commencent les colonnes, comment reconnaître les espaces, comment traiter une interface dont le nom est plus long et comment réagir si la sortie change après une mise à jour logicielle.

Cette difficulté ne rend pas la CLI inutile. Elle montre simplement qu'une interface conçue pour les humains n'est pas toujours la meilleure interface pour les applications.

## 1.2. Le principe d'une API réseau

Une API, ou *Application Programming Interface*, permet à un programme de communiquer avec un autre logiciel selon des règles définies.

Dans le cas d'un équipement réseau, une API peut permettre à une application de :

- lire les interfaces ;
- consulter la configuration ;
- récupérer certaines informations opérationnelles ;
- modifier des paramètres autorisés ;
- vérifier l'état obtenu ;
- utiliser les données dans un système de supervision ou d'automatisation.

L'application n'a alors plus besoin de reconnaître systématiquement un prompt CLI et de découper arbitrairement un texte.

Elle reçoit des données conformes au modèle et au format prévus par l'interface.

Les deux protocoles étudiés ici sont NETCONF et RESTCONF. Ils permettent l'accès programmatique aux données de gestion décrites par des modèles, notamment YANG. [RFC 6241](https://www.rfc-editor.org/rfc/rfc6241.html) · [RFC 8040](https://www.rfc-editor.org/rfc/rfc8040.html)

## 1.3. Exemple d'automatisation traditionnelle

Un script SSH utilisant une CLI suit approximativement le processus suivant :

```text
Python
  |
  | connexion SSH
  v
Invite CLI de l'équipement
  |
  | commande textuelle
  v
Sortie CLI
  |
  | parsing du texte
  v
Données utilisables par Python
```

L'application doit souvent connaître la commande exacte à envoyer et le format du texte attendu.

## 1.4. Exemple d'automatisation model-driven

Avec une API model-driven, le programme travaille avec une structure de données décrite par un modèle.

```text
Application
    |
    v
RESTCONF ou NETCONF
    |
    v
Données conformes au modèle YANG
    |
    v
Équipement réseau
```

L'application doit toujours connaître le modèle, les ressources ou opérations disponibles et les règles du serveur. L'API ne fait pas disparaître la nécessité de comprendre l'équipement.

Elle permet cependant d'utiliser des interfaces structurées et de réduire la dépendance à l'analyse de sorties CLI arbitraires.

## 1.5. Premier schéma SVG animé : de la CLI aux API model-driven

Le mouvement des tirets illustre le sens des échanges entre l'application et les différentes interfaces. L'animation reste limitée aux liaisons : aucun cercle mobile partagé entre les schémas n'est utilisé.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 330" role="img" aria-labelledby="intro-title intro-desc" style="max-width:100%;height:auto">
  <title id="intro-title">Évolution de l'automatisation réseau</title>
  <desc id="intro-desc">L'approche traditionnelle passe par une CLI et nécessite souvent le parsing de texte. L'approche model-driven utilise RESTCONF ou NETCONF et des données conformes à YANG.</desc>
  <defs>
    <marker id="intro-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#55c2e8"/></marker>
    <style>
      @keyframes intro-dash { to { stroke-dashoffset:-30 } }
      .intro-link { fill:none;stroke:#55c2e8;stroke-width:2.5;stroke-dasharray:7 7;marker-end:url(#intro-arrow);animation:intro-dash 2s linear infinite }
      .intro-box { fill:#18283f;stroke:#55c2e8;stroke-width:1.6 }
      .intro-title { font:600 15px sans-serif;fill:#f2f6ff;text-anchor:middle }
      .intro-small { font:12px sans-serif;fill:#bacbe2;text-anchor:middle }
      .intro-muted { fill:#a9bbd3;font:13px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="328" rx="14" fill="#0d1420" stroke="#2c3f59"/>
  <text x="235" y="34" class="intro-title">Gestion traditionnelle</text>
  <text x="704" y="34" class="intro-title">Gestion model-driven</text>
  <rect class="intro-box" x="35" y="65" width="145" height="58" rx="9"/>
  <text class="intro-title" x="107" y="89">Script Python</text><text class="intro-small" x="107" y="108">SSH / CLI</text>
  <rect class="intro-box" x="35" y="165" width="145" height="58" rx="9"/>
  <text class="intro-title" x="107" y="189">Invite CLI</text><text class="intro-small" x="107" y="208">commandes texte</text>
  <rect class="intro-box" x="35" y="265" width="145" height="45" rx="9"/>
  <text class="intro-title" x="107" y="292">Parsing texte</text>
  <path class="intro-link" d="M107 123 V160"/><path class="intro-link" d="M107 223 V260"/>
  <path d="M194 193 H251" fill="none" stroke="#8ca1be" stroke-width="1.5" stroke-dasharray="4 6"/>
  <text x="222" y="178" class="intro-muted">ou</text>
  <rect class="intro-box" x="275" y="91" width="150" height="60" rx="9"/>
  <text class="intro-title" x="350" y="116">Données</text><text class="intro-small" x="350" y="135">non normalisées</text>
  <rect class="intro-box" x="480" y="91" width="150" height="60" rx="9"/>
  <text class="intro-title" x="555" y="116">API</text><text class="intro-small" x="555" y="135">RESTCONF / NETCONF</text>
  <rect x="685" y="65" width="220" height="58" rx="9" fill="#15342e" stroke="#63c9a5" stroke-width="1.6"/>
  <text class="intro-title" x="795" y="89">Données YANG</text><text class="intro-small" x="795" y="108">schéma et règles connus</text>
  <rect x="685" y="165" width="220" height="58" rx="9" fill="#15342e" stroke="#63c9a5" stroke-width="1.6"/>
  <text class="intro-title" x="795" y="189">Équipement réseau</text><text class="intro-small" x="795" y="208">configuration et état</text>
  <path class="intro-link" d="M630 121 H680"/><path class="intro-link" d="M795 123 V160"/>
  <path d="M795 227 V251 H555 V155" fill="none" stroke="#63c9a5" stroke-width="2.3" stroke-dasharray="7 7" style="animation:intro-dash 2.4s linear infinite"/>
  <text x="563" y="278" class="intro-small">Réponse structurée vers l'application</text>
</svg>

**À retenir :** une API ne rend pas les commandes CLI obsolètes. Elle ajoute un moyen structuré d'accéder à certaines données et opérations, lorsque l'équipement prend ces fonctions en charge.

---

# 2. COMPRENDRE L'ARCHITECTURE MODEL-DRIVEN

Avant de comparer RESTCONF et NETCONF, il faut comprendre leur élément commun essentiel : **le modèle de données**.

## 2.1. Les trois notions fondamentales

### A. Le modèle de données

Il décrit la structure et les règles des données qu'un système accepte.

Exemple conceptuel :

```text
Interface
├── name
├── description
├── enabled
├── mtu
└── statistiques
```

Ce modèle peut préciser que `name` est une chaîne identifiant l'interface, que `enabled` est un booléen et que `mtu` est une valeur numérique soumise à des contraintes.

### B. Le protocole

Le protocole définit comment le client communique avec le serveur.

NETCONF utilise des messages RPC XML et un modèle de session.

RESTCONF utilise HTTP et des ressources identifiées par des URI.

### C. L'encodage

L'encodage détermine comment les données sont représentées dans les messages.

NETCONF utilise XML pour ses messages et pour les données transportées dans ses opérations.

RESTCONF peut utiliser un encodage XML ou JSON, selon les capacités du serveur. [RFC 7950](https://www.rfc-editor.org/rfc/rfc7950.html) · [RFC 7951](https://www.rfc-editor.org/rfc/rfc7951.html)

## 2.2. Pourquoi le modèle YANG est nécessaire

Supposons que deux constructeurs utilisent des interfaces différentes pour représenter une interface réseau.

L'un peut proposer une structure qui ressemble à :

```json
{
  "name": "GigabitEthernet0/0",
  "enabled": true
}
```

Un autre peut utiliser une structure différente, avec des noms de champs et des chemins différents.

Le modèle YANG fournit une manière déclarative de décrire les champs et les relations entre données. Des modèles standardisés peuvent améliorer l'interopérabilité, mais il faut toujours vérifier leur prise en charge par les équipements.

Un modèle standard ne signifie pas que tous les équipements :

- implémentent toutes ses fonctionnalités ;
- exposent exactement le même périmètre ;
- prennent en charge toutes les opérations de modification ;
- possèdent les mêmes contraintes spécifiques au matériel ;
- renvoient les mêmes valeurs dans tous les états.

Les modèles disponibles et les fonctions exposées doivent donc être vérifiés sur les équipements réellement utilisés.

## 2.3. Deuxième schéma SVG animé : les différentes couches

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390" role="img" aria-labelledby="layers-title layers-desc" style="max-width:100%;height:auto">
  <title id="layers-title">Couches d'une API réseau model-driven</title>
  <desc id="layers-desc">L'application utilise un protocole de gestion, transporte des données XML ou JSON et s'appuie sur des modèles YANG supportés par le serveur.</desc>
  <defs>
    <marker id="layers-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#b49af7"/></marker>
    <style>
      @keyframes layers-run { to { stroke-dashoffset:-26 } }
      .layers-flow { fill:none;stroke:#b49af7;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#layers-arrow);animation:layers-run 2s linear infinite }
      .layers-t { fill:#f4f5ff;font:600 16px sans-serif;text-anchor:middle }
      .layers-s { fill:#c0c9e0;font:13px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="918" height="388" rx="14" fill="#111525" stroke="#303653"/>
  <text x="460" y="33" class="layers-t">Les données, le transport et le protocole sont distincts</text>
  <rect x="170" y="58" width="580" height="62" rx="10" fill="#232545" stroke="#b49af7" stroke-width="1.5"/>
  <text x="460" y="83" class="layers-t">Application cliente</text><text x="460" y="103" class="layers-s">Python, outil d'administration, supervision</text>
  <path class="layers-flow" d="M460 120 V146"/>
  <rect x="170" y="151" width="580" height="62" rx="10" fill="#1b3342" stroke="#62b9dd" stroke-width="1.5"/>
  <text x="460" y="176" class="layers-t">Protocole de gestion</text><text x="460" y="196" class="layers-s">RESTCONF avec HTTP(S) ou NETCONF avec SSH</text>
  <path class="layers-flow" d="M460 213 V239"/>
  <rect x="170" y="244" width="580" height="62" rx="10" fill="#23352d" stroke="#69cba9" stroke-width="1.5"/>
  <text x="460" y="269" class="layers-t">Représentation des données</text><text x="460" y="289" class="layers-s">JSON / XML, selon le protocole et les capacités</text>
  <path class="layers-flow" d="M460 306 V330"/>
  <rect x="170" y="335" width="580" height="39" rx="9" fill="#352c1d" stroke="#e4b45f" stroke-width="1.5"/>
  <text x="460" y="360" class="layers-t">Modèle YANG : structure, types et contraintes</text>
</svg>

## 2.4. L'architecture en une phrase

Le client utilise RESTCONF ou NETCONF pour manipuler des données exposées par l'équipement selon des modèles.

Il n'est pas nécessaire de mémoriser tous les RFC pour débuter. Il faut d'abord savoir reconnaître le rôle de chaque élément :

| Élément | Question à laquelle il répond |
|---|---|
| YANG | Quelles données existent et comment sont-elles structurées ? |
| NETCONF | Comment envoyer une opération RPC et recevoir une réponse XML ? |
| RESTCONF | Comment accéder aux ressources de gestion via HTTP ? |
| XML ou JSON | Sous quelle forme les données sont-elles représentées ? |
| SSH ou TLS | Comment protéger le transport des échanges ? |
| Datastore | Quel ensemble de configuration ou d'état est consulté ou modifié ? |

---

# 3. YANG : LE LANGAGE QUI DÉCRIT LES DONNÉES RÉSEAU

## 3.1. Définition

YANG est un langage de modélisation utilisé pour décrire des données de configuration, des données d'état, des opérations et des notifications de gestion réseau.

La spécification YANG 1.1 est décrite dans le [RFC 7950](https://www.rfc-editor.org/rfc/rfc7950.html).

Un modèle YANG n'est pas en soi un protocole de communication. C'est la définition structurée des données qu'un protocole tel que NETCONF ou RESTCONF pourra utiliser.

## 3.2. Exemple très simple de modèle

Voici un petit extrait pédagogique :

```yang
module exemple-interfaces {
  yang-version 1.1;

  namespace "urn:example:interfaces";
  prefix ex-if;

  container interfaces {
    list interface {
      key "name";

      leaf name {
        type string;
      }

      leaf description {
        type string;
      }

      leaf enabled {
        type boolean;
        default true;
      }
    }
  }
}
```

Cet exemple décrit :

- un conteneur `interfaces` ;
- une liste `interface` ;
- une clé de liste `name` ;
- un champ `description` ;
- un champ `enabled` de type booléen.

Il s'agit d'un modèle d'apprentissage. Il ne représente pas à lui seul le modèle officiel complet d'un constructeur.

## 3.3. Comprendre les principaux mots-clés

| Mot-clé YANG | Signification générale |
|---|---|
| `module` | Déclare un module de données |
| `namespace` | Identifie son espace de noms |
| `prefix` | Définit un préfixe utilisé pour référencer le module |
| `container` | Regroupe plusieurs nœuds de données |
| `list` | Définit une collection d'éléments structurés |
| `key` | Identifie les éléments d'une liste |
| `leaf` | Définit une donnée simple, souvent une valeur unique |
| `leaf-list` | Définit une liste de valeurs simples |
| `type` | Définit le type d'une valeur |
| `description` | Documente l'élément |
| `mandatory` | Peut exiger la présence d'une donnée selon les règles du modèle |
| `default` | Définit une valeur par défaut selon les règles YANG |
| `config` | Distingue notamment les nœuds destinés à la configuration de ceux en lecture seule |
| `choice` et `case` | Décrivent des alternatives structurées |

Ces mots-clés sont présentés ici comme des premières notions. Les contraintes réelles peuvent également inclure des plages numériques, des motifs, des références entre données et des règles de validation plus avancées.

## 3.4. Troisième schéma SVG animé : lire un arbre de données YANG

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 370" role="img" aria-labelledby="yang-title yang-desc" style="max-width:100%;height:auto">
  <title id="yang-title">Structure hiérarchique des données d'interfaces</title>
  <desc id="yang-desc">L'arbre contient le conteneur interfaces, une liste interface et des feuilles name, description et enabled.</desc>
  <defs>
    <marker id="yang-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#f0b864"/></marker>
    <style>
      @keyframes yang-dash { to { stroke-dashoffset:-22 } }
      .yang-link { fill:none;stroke:#f0b864;stroke-width:2.3;stroke-dasharray:6 7;marker-end:url(#yang-arrow);animation:yang-dash 2s linear infinite }
      .yang-box { fill:#24243b;stroke:#a99af4;stroke-width:1.5 }
      .yang-leaf { fill:#16352f;stroke:#69caa7;stroke-width:1.5 }
      .yang-text { fill:#f4f4ff;font:600 15px sans-serif;text-anchor:middle }
      .yang-sub { fill:#c6cbe0;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="918" height="368" rx="14" fill="#111525" stroke="#343653"/>
  <text x="460" y="33" class="yang-text">Une structure hiérarchique devient un chemin d'accès</text>
  <rect class="yang-box" x="330" y="51" width="260" height="49" rx="9"/>
  <text x="460" y="72" class="yang-text">interfaces</text><text x="460" y="89" class="yang-sub">container</text>
  <rect class="yang-box" x="330" y="130" width="260" height="49" rx="9"/>
  <text x="460" y="151" class="yang-text">interface</text><text x="460" y="168" class="yang-sub">list · clé name</text>
  <path class="yang-link" d="M460 100 V125"/>
  <path d="M460 179 V204 H157 V235 M460 204 V235 M460 204 H763 V235" fill="none" stroke="#f0b864" stroke-width="2.3" stroke-dasharray="6 7" style="animation:yang-dash 2.2s linear infinite"/>
  <rect class="yang-leaf" x="48" y="235" width="218" height="63" rx="9"/>
  <text x="157" y="261" class="yang-text">name</text><text x="157" y="281" class="yang-sub">clé · string</text>
  <rect class="yang-leaf" x="351" y="235" width="218" height="63" rx="9"/>
  <text x="460" y="261" class="yang-text">description</text><text x="460" y="281" class="yang-sub">string</text>
  <rect class="yang-leaf" x="654" y="235" width="218" height="63" rx="9"/>
  <text x="763" y="261" class="yang-text">enabled</text><text x="763" y="281" class="yang-sub">boolean</text>
  <text x="460" y="337" class="yang-sub">Le modèle définit les champs ; l'instance fournit leurs valeurs.</text>
</svg>

## 3.5. Modèle et instance : ne pas confondre

Le modèle décrit les champs possibles.

Une instance est une représentation concrète avec des valeurs.

Modèle conceptuel :

```text
interface
├── name : string
├── description : string
└── enabled : boolean
```

Exemple d'instance en JSON :

```json
{
  "name": "Loopback0",
  "description": "Interface de laboratoire",
  "enabled": true
}
```

Les valeurs concrètes doivent respecter les contraintes du modèle. L'exemple JSON ci-dessus illustre la structure de l'objet, mais son enveloppe exacte dans une requête RESTCONF dépend du chemin demandé et du modèle utilisé.

## 3.6. Modèles standard et modèles constructeur

Vous rencontrerez plusieurs familles de modèles.

### Modèles standardisés

Les modèles IETF définissent des structures destinées à favoriser l'interopérabilité entre différentes implémentations.

Exemples :
- `ietf-interfaces` pour des éléments liés aux interfaces ;
- `ietf-ip` pour certaines données IP ;
- `ietf-routing` pour les modèles de routage pris en charge.

### Modèles spécifiques aux constructeurs

Certains modèles décrivent des paramètres ou des fonctionnalités propres à un constructeur ou à une plateforme.

Ils peuvent être nécessaires pour accéder à des capacités qui ne sont pas représentées par le modèle standard utilisé.

### Une précaution importante

Le nom d'un modèle dans une documentation n'implique pas qu'il est présent sur tous les équipements de la gamme.

Avant de construire des requêtes, il faut vérifier :

- les modules YANG disponibles ;
- les versions de modules ;
- les fonctionnalités effectivement prises en charge ;
- les chemins et champs exposés ;
- les opérations de lecture ou de modification autorisées.

La YANG Library fournit des informations sur les modules et les schémas utilisés par un serveur lorsque cette fonctionnalité est disponible. Voir le [RFC 8525](https://www.rfc-editor.org/rfc/rfc8525.html).

---

# 4. NETCONF : LE PROTOCOLE DE GESTION XML

## 4.1. Définition

NETCONF signifie *Network Configuration Protocol*.

C'est un protocole standard de gestion d'équipements réseau. Il permet notamment de lire, installer, modifier et supprimer des données de configuration en s'appuyant sur des opérations structurées. Les messages NETCONF utilisent XML et le protocole fonctionne selon un modèle RPC.

La spécification principale est le [RFC 6241](https://www.rfc-editor.org/rfc/rfc6241.html).

## 4.2. Comment se déroule une opération NETCONF ?

Le client ouvre une session vers le serveur NETCONF.

Les deux côtés échangent des informations sur leurs capacités.

Le client envoie ensuite une opération RPC en XML. Le serveur traite la demande et renvoie une réponse XML.

Exemple conceptuel :

```text
Client
  |
  | ouverture de session
  v
Serveur NETCONF
  |
  | échange des capacités
  v
Session prête
  |
  | RPC XML
  v
Traitement de la requête
  |
  | réponse XML
  v
Client
```

## 4.3. NETCONF fonctionne généralement sur SSH

L'utilisation de NETCONF au-dessus de SSH est décrite dans le [RFC 6242](https://www.rfc-editor.org/rfc/rfc6242.html).

Le port TCP 830 est le port standard affecté au sous-système NETCONF sur SSH. Une implémentation peut prévoir d'autres réglages, mais il faut vérifier la configuration réelle de l'équipement.

Cela ne signifie pas qu'une session SSH ordinaire sur le port 22 devient automatiquement une session NETCONF. Le serveur doit prendre en charge le sous-système NETCONF et le client doit l'invoquer selon le protocole.

## 4.4. Les messages RPC

NETCONF utilise des opérations RPC pour demander une action au serveur.

Exemple de demande conceptuelle de lecture de la configuration active :

```xml
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
     message-id="101">
  <get-config>
    <source>
      <running/>
    </source>
  </get-config>
</rpc>
```

L'attribut `message-id` permet d'associer la réponse à la demande correspondante.

Le document XML ci-dessus illustre la structure de l'opération. Dans une vraie session, NETCONF utilise également les mécanismes de cadrage des messages prévus par la version du protocole et le transport. Un simple envoi de texte XML sur une session SSH de terminal ne suffit pas à implémenter correctement NETCONF.

## 4.5. Les opérations de base

| Opération | Fonction générale |
|---|---|
| `<get>` | Lire des données de configuration et d'état accessibles |
| `<get-config>` | Lire les données de configuration d'un datastore |
| `<edit-config>` | Modifier les données de configuration d'un datastore |
| `<copy-config>` | Copier une configuration entre des sources et cibles autorisées |
| `<delete-config>` | Supprimer une configuration lorsque la cible et les capacités le permettent |
| `<lock>` | Verrouiller un datastore pris en charge |
| `<unlock>` | Libérer un verrou |
| `<commit>` | Valider une configuration candidate lorsque la capacité correspondante est disponible |
| `<close-session>` | Fermer proprement la session |
| `<kill-session>` | Terminer une autre session selon les règles du protocole et les permissions |

Toutes les opérations ne sont pas disponibles pour tous les datastores ni dans toutes les implémentations.

Il faut notamment éviter de supposer que `<candidate>`, `<startup>` ou `<commit>` existent sur n'importe quel équipement. Les capacités annoncées par le serveur et les fonctions réellement prises en charge déterminent les opérations utilisables.

## 4.6. Comprendre les datastores

Un datastore représente un ensemble de données de gestion.

Les premiers noms à reconnaître sont :

- **`running`** : configuration en cours d'utilisation, lorsqu'elle est exposée selon le modèle NETCONF ;
- **`candidate`** : configuration candidate modifiable avant validation, si cette capacité est prise en charge ;
- **`startup`** : configuration de démarrage, lorsque le datastore et les opérations associées sont disponibles.

Leur présence et leur comportement dépendent des capacités du serveur.

### Pourquoi `candidate` peut être utile

Lorsqu'un équipement le prend en charge, le datastore `candidate` permet de préparer certaines modifications avant de les valider. L'administrateur peut alors utiliser les mécanismes de validation disponibles avant de rendre les changements effectifs.

Cela ne constitue pas une garantie universelle de rollback et ne signifie pas que toutes les modifications sont automatiquement annulées après une erreur. Il faut comprendre les capacités exactes, les contraintes de la plateforme et le fonctionnement de la validation.

## 4.7. Quatrième schéma SVG animé : cycle NETCONF

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 350" role="img" aria-labelledby="netconf-title netconf-desc" style="max-width:100%;height:auto">
  <title id="netconf-title">Fonctionnement d'une session NETCONF</title>
  <desc id="netconf-desc">Le client ouvre une session SSH NETCONF, négocie les capacités, envoie une opération RPC XML, puis reçoit une réponse.</desc>
  <defs>
    <marker id="netconf-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#5db9ea"/></marker>
    <style>
      @keyframes netconf-dash { to { stroke-dashoffset:-28 } }
      .netconf-link { fill:none;stroke:#5db9ea;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#netconf-arrow);animation:netconf-dash 2s linear infinite }
      .netconf-box { fill:#192740;stroke:#5db9ea;stroke-width:1.5 }
      .netconf-text { fill:#f4f7ff;font:600 14px sans-serif;text-anchor:middle }
      .netconf-sub { fill:#b8c8df;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="348" rx="14" fill="#0c1421" stroke="#2c3e57"/>
  <rect x="35" y="70" width="220" height="68" rx="10" fill="#282341" stroke="#b2a2f3" stroke-width="1.7"/>
  <text x="145" y="98" class="netconf-text">Client NETCONF</text><text x="145" y="119" class="netconf-sub">application ou script</text>
  <rect class="netconf-box" x="685" y="70" width="220" height="68" rx="10"/>
  <text x="795" y="98" class="netconf-text">Serveur NETCONF</text><text x="795" y="119" class="netconf-sub">équipement réseau</text>
  <path class="netconf-link" d="M255 92 H680"/>
  <text x="470" y="80" class="netconf-sub">1. établissement de session</text>
  <path class="netconf-link" d="M685 117 H260"/>
  <text x="470" y="139" class="netconf-sub">2. échange des capacités</text>
  <rect x="280" y="180" width="380" height="62" rx="10" fill="#15342e" stroke="#62c9a5" stroke-width="1.5"/>
  <text x="470" y="205" class="netconf-text">Opération RPC encodée en XML</text><text x="470" y="225" class="netconf-sub">get / get-config / edit-config…</text>
  <path class="netconf-link" d="M145 138 V209 H275"/>
  <path class="netconf-link" d="M685 138 V209 H665"/>
  <rect x="280" y="273" width="380" height="49" rx="9" fill="#34291d" stroke="#e7b35c" stroke-width="1.5"/>
  <text x="470" y="295" class="netconf-text">Réponse XML</text><text x="470" y="311" class="netconf-sub">ok, données ou rpc-error</text>
  <path class="netconf-link" d="M795 138 V297 H665"/>
</svg>

## 4.8. Réponse positive et erreur RPC

Une réponse NETCONF peut contenir une indication de réussite, des données ou une erreur de protocole.

Réponse positive simplifiée :

```xml
<rpc-reply
    xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
    message-id="101">
  <ok/>
</rpc-reply>
```

Exemple conceptuel de lecture :

```xml
<rpc-reply
    xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
    message-id="102">
  <data>
    <!-- Les données de l'équipement seraient ici -->
  </data>
</rpc-reply>
```

Une réponse contenant `<ok/>` signifie que l'opération a été acceptée conformément à la sémantique de la méthode. Cela ne prouve pas nécessairement qu'un service réseau fonctionne correctement. Les contrôles métier doivent toujours être adaptés au besoin.

---

# 5. RESTCONF : L'API DE GESTION BASÉE SUR HTTP

## 5.1. Définition

RESTCONF fournit une interface de gestion fondée sur HTTP pour accéder à des données et opérations décrites en YANG.

La spécification de référence est le [RFC 8040](https://www.rfc-editor.org/rfc/rfc8040.html).

Contrairement à NETCONF, qui organise ses échanges autour d'opérations RPC et de messages XML, RESTCONF expose des ressources auxquelles le client accède avec des URI et des méthodes HTTP.

RESTCONF ne remplace pas NETCONF dans tous les scénarios. Il fournit une autre interface de gestion reposant sur HTTP et compatible avec les concepts de modèles YANG et de datastores.

## 5.2. La structure d'une URI RESTCONF

Une URI identifie une ressource.

Exemple conceptuel :

```text
https://routeur.example/restconf/data/ietf-interfaces:interfaces
```

Décomposition :

| Partie | Rôle |
|---|---|
| `https` | Schéma de transport HTTP sécurisé |
| `routeur.example` | Nom de l'équipement ou adresse de gestion |
| `/restconf` | Racine de l'interface RESTCONF |
| `/data` | Espace d'accès aux données |
| `ietf-interfaces:interfaces` | Ressource basée sur un nœud du modèle YANG |

Le chemin exact dépend du modèle, de ses modules, des clés des listes et des ressources que le serveur expose.

Ne supposez jamais qu'un chemin de documentation pour une famille de produits fonctionne sur tous les modèles de la gamme.

## 5.3. Les méthodes HTTP principales

RESTCONF utilise des méthodes HTTP pour réaliser des opérations sur les ressources.

| Méthode | Usage courant | Prudence |
|---|---|---|
| `GET` | Lire une ressource | Habituellement utilisé en premier pour découvrir les données |
| `POST` | Créer une ressource ou invoquer certaines opérations prévues | Vérifier la ressource ciblée et la sémantique de l'opération |
| `PUT` | Créer ou remplacer une ressource selon les règles applicables | Peut remplacer des données : vérifier soigneusement le chemin et le corps |
| `PATCH` | Modifier partiellement une ressource | La sémantique dépend du type de modification pris en charge |
| `DELETE` | Supprimer une ressource | Peut avoir des conséquences importantes ; nécessite une autorisation explicite |

Toutes les méthodes ne sont pas autorisées sur toutes les ressources. Le modèle, les capacités de l'implémentation et les permissions du compte influencent ce qui est réellement possible.

Pour débuter, commencez par `GET`. N'expérimentez pas des modifications de configuration sur un équipement de production.

## 5.4. Quel format de données RESTCONF utilise-t-il ?

RESTCONF peut utiliser un encodage XML ou JSON, selon les capacités annoncées par le serveur.

Par exemple, une réponse JSON simplifiée pourrait ressembler à ceci :

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

Cette structure sert à expliquer le principe. La réponse réelle peut comporter d'autres champs, des espaces de noms ou des restrictions selon le modèle, les modules et l'implémentation.

La présence d'une propriété dans cet exemple ne garantit pas qu'elle soit disponible sur votre équipement.

## 5.5. Les en-têtes HTTP

Deux en-têtes sont particulièrement importants.

### `Accept`

Il indique le type de représentation que le client souhaite recevoir.

Pour demander du JSON RESTCONF :

```http
Accept: application/yang-data+json
```

Pour demander du XML RESTCONF :

```http
Accept: application/yang-data+xml
```

### `Content-Type`

Lorsqu'une requête envoie un corps de données, l'en-tête `Content-Type` précise son format.

Exemple :

```http
Content-Type: application/yang-data+json
```

Il ne suffit pas d'annoncer du JSON : le corps doit aussi respecter la structure attendue par le modèle YANG et l'opération ciblée.

## 5.6. Cinquième schéma SVG animé : une requête RESTCONF

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 350" role="img" aria-labelledby="rest-title rest-desc" style="max-width:100%;height:auto">
  <title id="rest-title">Échange RESTCONF par HTTP</title>
  <desc id="rest-desc">Un client envoie une requête GET HTTP avec une URI et un en-tête Accept. Le serveur consulte les données et retourne une réponse JSON avec un code HTTP.</desc>
  <defs>
    <marker id="rest-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#67c4a6"/></marker>
    <style>
      @keyframes rest-flow { to { stroke-dashoffset:-26 } }
      .rest-link { fill:none;stroke:#67c4a6;stroke-width:2.5;stroke-dasharray:7 7;marker-end:url(#rest-arrow);animation:rest-flow 2s linear infinite }
      .rest-label { fill:#f3f6ff;font:600 15px sans-serif;text-anchor:middle }
      .rest-small { fill:#bac9df;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="348" rx="14" fill="#0d1420" stroke="#2c3f58"/>
  <rect x="28" y="90" width="210" height="82" rx="10" fill="#262440" stroke="#b3a3f3" stroke-width="1.6"/>
  <text x="133" y="120" class="rest-label">Client API</text><text x="133" y="143" class="rest-small">Python / cURL</text>
  <rect x="702" y="90" width="210" height="82" rx="10" fill="#15352f" stroke="#67c4a6" stroke-width="1.6"/>
  <text x="807" y="120" class="rest-label">Serveur RESTCONF</text><text x="807" y="143" class="rest-small">équipement réseau</text>
  <path class="rest-link" d="M238 108 H696"/>
  <text x="468" y="91" class="rest-small">GET + URI + Accept</text>
  <path class="rest-link" d="M702 151 H244"/>
  <text x="468" y="175" class="rest-small">HTTP 200 + données JSON/XML</text>
  <rect x="275" y="220" width="390" height="84" rx="10" fill="#202d41" stroke="#5ebbe7" stroke-width="1.5"/>
  <text x="470" y="246" class="rest-label">Traitement structuré</text>
  <text x="470" y="267" class="rest-small">URI → ressource → modèle YANG</text>
  <text x="470" y="285" class="rest-small">vérifier le statut et le corps de la réponse</text>
  <path class="rest-link" d="M807 172 V262 H670"/>
</svg>

## 5.7. Les codes de réponse HTTP

Le code HTTP indique le résultat général du traitement de la requête.

| Code | Interprétation courante |
|---|---|
| `200 OK` | La requête a réussi et une réponse est fournie |
| `201 Created` | Une ressource a été créée |
| `204 No Content` | L'opération a réussi sans corps de réponse |
| `400 Bad Request` | Requête invalide ou mal formée |
| `401 Unauthorized` | Authentification absente ou invalide |
| `403 Forbidden` | Accès interdit par les règles du serveur |
| `404 Not Found` | Ressource inexistante ou inaccessible via ce chemin |
| `405 Method Not Allowed` | Méthode non autorisée pour la ressource |
| `409 Conflict` | Conflit avec l'état de la ressource ou la requête |
| `412 Precondition Failed` | Une précondition de requête n'a pas été satisfaite |
| `415 Unsupported Media Type` | Type de contenu non pris en charge |
| `500 Internal Server Error` | Erreur interne du serveur |

Les réponses exactes dépendent de la requête et de l'implémentation. Le corps de la réponse peut contenir des détails utiles.

Un code de succès doit être interprété avec le contenu retourné et les vérifications métier nécessaires.

## 5.8. Découvrir les ressources disponibles

L'accès RESTCONF commence par l'identification de la racine du service et des ressources prises en charge.

Dans de nombreuses implémentations RESTCONF, `/restconf` donne accès à la ressource API et `/restconf/data` aux données. La racine ou certains chemins peuvent être présentés différemment dans la documentation propre au produit ; vérifiez le guide de la version logicielle.

Le modèle de données disponible, les chemins corrects et les opérations valides doivent être identifiés avant de construire des requêtes.

---

# 6. COMPARER RESTCONF ET NETCONF

## 6.1. Tableau comparatif

| Caractéristique | NETCONF | RESTCONF |
|---|---|---|
| Modèle de communication | RPC | Ressources HTTP |
| Encodage des messages | XML | XML ou JSON selon le serveur |
| Transport courant | SSH | HTTPS/TLS |
| Port habituel | TCP 830 pour NETCONF sur SSH | TCP 443 pour HTTPS, sauf configuration différente |
| Lecture des données | Opérations telles que `get` et `get-config` | Requête HTTP `GET` |
| Modification des données | Opérations telles que `edit-config` | Méthodes telles que `POST`, `PUT` ou `PATCH`, selon le cas |
| Contrôle des datastores | Opérations NETCONF et capacités du serveur | Accès aux ressources de gestion exposées |
| Compatibilité YANG | Oui, pour les données modélisées concernées | Oui |
| Format de retour | Messages NETCONF XML | Réponses HTTP avec XML ou JSON |
| Erreurs | Réponses et éléments `rpc-error` | Codes HTTP et éventuels détails dans le corps |
| Gestion de session | Modèle explicite de session NETCONF | Modèle de requêtes HTTP |
| Disponibilité | Dépend de l'implémentation | Dépend de l'implémentation |

Les ports indiqués sont les valeurs courantes ou standardisées pour les transports concernés. Ils ne remplacent pas la vérification de la configuration de l'équipement.

## 6.2. Sixième schéma SVG animé : deux protocoles, un objectif

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="compare-title compare-desc" style="max-width:100%;height:auto">
  <title id="compare-title">Comparaison NETCONF et RESTCONF</title>
  <desc id="compare-desc">NETCONF et RESTCONF suivent deux chemins de communication différents mais peuvent manipuler des données définies par YANG.</desc>
  <defs>
    <marker id="compare-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#d4b16c"/></marker>
    <style>
      @keyframes compare-flow { to { stroke-dashoffset:-24 } }
      .compare-link { fill:none;stroke:#d4b16c;stroke-width:2.3;stroke-dasharray:6 7;marker-end:url(#compare-arrow);animation:compare-flow 2s linear infinite }
      .compare-label { fill:#f3f5ff;font:600 15px sans-serif;text-anchor:middle }
      .compare-sub { fill:#c1cbe0;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="338" rx="14" fill="#0e1422" stroke="#2d3b55"/>
  <rect x="310" y="20" width="320" height="52" rx="10" fill="#243025" stroke="#72c9a4" stroke-width="1.6"/>
  <text x="470" y="42" class="compare-label">Objectif commun</text><text x="470" y="59" class="compare-sub">manipuler des données modélisées</text>
  <path class="compare-link" d="M388 72 L235 114"/><path class="compare-link" d="M552 72 L705 114"/>
  <rect x="50" y="116" width="370" height="78" rx="10" fill="#282441" stroke="#b2a1f1" stroke-width="1.6"/>
  <text x="235" y="143" class="compare-label">NETCONF</text><text x="235" y="164" class="compare-sub">RPC XML · session SSH</text><text x="235" y="181" class="compare-sub">get / get-config / edit-config</text>
  <rect x="520" y="116" width="370" height="78" rx="10" fill="#193043" stroke="#65bfe8" stroke-width="1.6"/>
  <text x="705" y="143" class="compare-label">RESTCONF</text><text x="705" y="164" class="compare-sub">HTTP(S) · ressources URI</text><text x="705" y="181" class="compare-sub">GET / POST / PUT / PATCH</text>
  <path class="compare-link" d="M235 194 V225 H470 V249"/><path class="compare-link" d="M705 194 V225 H470"/>
  <rect x="280" y="250" width="380" height="56" rx="10" fill="#1a352e" stroke="#72c9a4" stroke-width="1.6"/>
  <text x="470" y="274" class="compare-label">Modèles YANG</text><text x="470" y="293" class="compare-sub">schémas et contraintes applicables</text>
  <text x="470" y="326" class="compare-sub">Deux protocoles ; un modèle de données commun lorsque pris en charge.</text>
</svg>

## 6.3. Quel protocole faut-il apprendre en premier ?

Pour un débutant, RESTCONF peut être plus facile à tester, notamment parce que l'on peut commencer avec un client HTTP et examiner directement le JSON retourné.

NETCONF est particulièrement important pour comprendre les opérations RPC, la gestion des datastores et les capacités du serveur.

Le choix dans une infrastructure réelle dépend :

- des capacités de l'équipement ;
- de l'interface recommandée par le constructeur ;
- de l'opération à accomplir ;
- des exigences d'accès et de contrôle de configuration ;
- des outils et bibliothèques disponibles ;
- des politiques de sécurité de l'organisation.

Il ne faut pas choisir RESTCONF simplement parce que JSON paraît plus familier, ni choisir NETCONF en supposant qu'il offre automatiquement toutes les fonctions souhaitées.

---

# 7. PRÉPARER SON ENVIRONNEMENT DE LABORATOIRE

## 7.1. Ce qu'il faut réunir

Pour suivre les exercices, vous aurez besoin de :

- Python ;
- un environnement virtuel Python ;
- une machine de laboratoire ou un équipement virtuel compatible ;
- un compte autorisé à accéder à l'API ;
- l'adresse de gestion de l'équipement ;
- la documentation du constructeur correspondant à la version logicielle ;
- les paramètres de confiance TLS ou SSH ;
- les modules YANG et fonctionnalités exposés par le serveur, si nécessaires.

Vous pouvez également travailler sur un environnement de simulation ou un équipement virtuel. La simulation permet de commencer sans toucher à un réseau de production.

Les exemples utilisent des adresses de documentation telles que `192.0.2.10`. Elles ne correspondent pas à un véritable équipement accessible.

## 7.2. Préparer Python

Créez un dossier :

```bash
mkdir api-reseau-lab
cd api-reseau-lab

python -m venv .venv
```

Activation sous Linux/macOS :

```bash
source .venv/bin/activate
```

Activation sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installez les bibliothèques utiles aux exercices :

```bash
python -m pip install --upgrade pip
python -m pip install requests ncclient
```

`requests` sera utilisé pour RESTCONF. `ncclient` fournit une interface Python de haut niveau pour NETCONF.

Consultez les pages officielles des bibliothèques avant de fixer les versions de votre environnement :

- Requests : https://requests.readthedocs.io/
- ncclient : https://github.com/ncclient/ncclient

Pour un environnement de production, testez et verrouillez les versions installées.

## 7.3. Préparer les informations de connexion

Pour RESTCONF, rassemblez :

```text
Adresse de gestion HTTPS :
Port :
Nom d'utilisateur :
Méthode d'authentification :
Chemin de la ressource :
Modules YANG disponibles :
```

Pour NETCONF :

```text
Adresse de gestion :
Port NETCONF sur SSH :
Nom d'utilisateur :
Méthode d'authentification SSH :
Clé d'hôte attendue :
Capacités NETCONF annoncées :
Datastores disponibles :
```

Ne placez pas les mots de passe directement dans les exemples de code ou dans le dépôt. Utilisez un mécanisme adapté à votre environnement.

## 7.4. Précaution relative aux équipements réels

L'activation de RESTCONF ou de NETCONF varie selon le constructeur et la version du système.

Certaines plateformes nécessitent l'activation de services, d'autres des paramètres TLS, des comptes ou des profils d'accès particuliers.

N'appliquez pas une commande d'activation trouvée pour un produit sur un autre produit sans consulter sa documentation. L'activation d'une API de gestion crée une nouvelle surface d'accès qui doit être protégée.

---

# 8. RÉALISER SA PREMIÈRE REQUÊTE RESTCONF

Nous allons commencer en lecture seule. Le but est de récupérer des données, pas de modifier la configuration.

## 8.1. Les éléments d'une requête GET

Une requête comprend :

1. une méthode HTTP, ici `GET` ;
2. une URI identifiant la ressource ;
3. un mécanisme d'authentification ;
4. des en-têtes indiquant le format souhaité ;
5. une réponse contenant un statut et éventuellement des données.

Exemple conceptuel :

```http
GET /restconf/data/ietf-interfaces:interfaces HTTP/1.1
Host: 192.0.2.10
Accept: application/yang-data+json
```

L'authentification et le transport sécurisé doivent également être correctement configurés pour que la requête fonctionne.

## 8.2. Tester avec cURL

Sous Linux, macOS ou Windows avec une version compatible de cURL :

```bash
curl --fail-with-body \
     --silent \
     --show-error \
     --user "$RESTCONF_USERNAME" \
     --header "Accept: application/yang-data+json" \
     "https://192.0.2.10/restconf/data/ietf-interfaces:interfaces"
```

Lorsque l'on fournit uniquement le nom d'utilisateur à l'option `--user`, cURL peut demander le mot de passe interactivement.

Cet exemple suppose que l'équipement accepte l'authentification utilisée et que le certificat HTTPS est reconnu par le système. Si une autorité de certification interne est utilisée, configurez sa chaîne de confiance, par exemple avec un fichier CA approprié.

**N'utilisez pas `-k` ou `--insecure` comme solution permanente.** Ces options désactivent la vérification du certificat du serveur et exposent la connexion à des risques d'usurpation.

L'adresse et le chemin utilisés sont des exemples. Il faut remplacer l'adresse et vérifier que le modèle `ietf-interfaces` ainsi que le chemin demandé sont exposés par l'équipement.

## 8.3. Comprendre la réponse

Si la requête réussit, le serveur peut retourner des données JSON semblables à celles-ci :

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

Interprétez la structure :

- `ietf-interfaces:interfaces` identifie un nœud de données du module ;
- `interface` représente une collection d'interfaces dans ce modèle ;
- `name` identifie une entrée ;
- `description` décrit l'entrée ;
- `enabled` est une propriété booléenne de configuration dans le modèle concerné.

La réponse réelle peut contenir plus de propriétés. Certaines peuvent être absentes si elles ne sont pas exposées, non pertinentes ou non prises en charge.

Il ne faut pas traiter cet extrait comme une réponse garantie d'un routeur quelconque.

## 8.4. Faire une requête RESTCONF avec Python

Créez `restconf_get.py` :

```python
import os
import sys

import requests


def main() -> int:
    host = os.environ.get("RESTCONF_HOST")
    username = os.environ.get("RESTCONF_USERNAME")
    password = os.environ.get("RESTCONF_PASSWORD")

    if not host or not username or not password:
        print(
            "Configurez RESTCONF_HOST, RESTCONF_USERNAME "
            "et RESTCONF_PASSWORD."
        )
        return 2

    url = (
        f"https://{host}/restconf/data/"
        "ietf-interfaces:interfaces"
    )

    headers = {
        "Accept": "application/yang-data+json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=(username, password),
            timeout=(5, 20),
            verify=True,
        )

        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            print("La réponse reçue n'est pas un JSON valide.")
            return 1

        print("Requête RESTCONF réussie.")
        print(f"Code HTTP : {response.status_code}")
        print(data)

        return 0

    except requests.exceptions.SSLError:
        print(
            "Erreur TLS : vérifiez le certificat du serveur "
            "et la chaîne de confiance."
        )
        return 1

    except requests.exceptions.Timeout:
        print("La requête RESTCONF a dépassé le délai autorisé.")
        return 1

    except requests.exceptions.HTTPError as exc:
        print(f"Erreur HTTP : {exc}")
        if exc.response is not None:
            print(f"Code HTTP : {exc.response.status_code}")
            print(exc.response.text)
        return 1

    except requests.exceptions.RequestException as exc:
        print(f"Erreur de communication : {type(exc).__name__}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### Comprendre les choix du code

**`timeout=(5, 20)`** définit deux délais : l'un pour l'établissement de la connexion et l'autre pour la lecture de la réponse. Il s'agit d'une borne de départ pour le laboratoire, à adapter au réseau réel.

**`verify=True`** conserve la vérification TLS. L'application ne doit pas supposer qu'une réponse reçue est fiable simplement parce que le serveur a répondu.

**`raise_for_status()`** fait remonter les réponses HTTP d'erreur au niveau de Requests. Le programme peut ainsi distinguer une erreur HTTP d'une réponse JSON valide.

**`response.json()`** décode le corps JSON. Cela ne valide cependant pas sa conformité au modèle YANG attendu : il faut ajouter des contrôles sur la structure et les champs pour les traitements métier.

Le programme affiche la réponse pour l'apprentissage. Dans une application réelle, évitez d'afficher ou d'enregistrer des données sensibles sans nécessité.

## 8.5. Préparer les variables d'environnement

Exemple temporaire sous Linux/macOS :

```bash
export RESTCONF_HOST="192.0.2.10"
export RESTCONF_USERNAME="api-reader"
read -s RESTCONF_PASSWORD
export RESTCONF_PASSWORD
python restconf_get.py
unset RESTCONF_PASSWORD
```

Les variables d'environnement servent ici à éviter de coder le mot de passe dans le fichier Python. Elles ne constituent pas automatiquement un coffre sécurisé. La méthode adaptée dépend de l'environnement d'exécution et de la politique de sécurité.

Pour un usage régulier, utilisez un mécanisme approuvé de gestion des secrets.

## 8.6. Comprendre l'URI avant de l'automatiser

L'URI de l'exemple contient :

```text
/restconf/data/ietf-interfaces:interfaces
```

Ce chemin ne représente pas forcément toutes les données de l'équipement. Il cible une ressource du modèle correspondant.

Si vous voulez cibler une entrée de liste, le chemin peut inclure sa clé. Pour une interface nommée `Loopback0`, un chemin pourrait ressembler à :

```text
/restconf/data/ietf-interfaces:interfaces/interface=Loopback0
```

Le chemin exact dépend du schéma et de l'implémentation. Les clés contenant des caractères spéciaux doivent être encodées correctement dans l'URI. Vérifiez toujours la syntaxe du chemin dans le modèle et la documentation RESTCONF de l'équipement.

---

# 9. INTERROGER NETCONF AVEC PYTHON

## 9.1. Installer et importer `ncclient`

La bibliothèque `ncclient` aide les programmes Python à établir des sessions NETCONF et à effectuer des opérations.

```bash
python -m pip install ncclient
```

Dans un script :

```python
from ncclient import manager
```

Le programme ne doit pas ouvrir un simple terminal SSH et envoyer un document XML sans gérer le protocole. Utilisez une bibliothèque NETCONF qui prend en charge l'établissement de la session, l'échange des capacités, l'encodage des messages et leur cadrage.

## 9.2. Effectuer une première lecture de configuration

Créez `netconf_get.py` :

```python
import os

from ncclient import manager


def main() -> None:
    host = os.environ["NETCONF_HOST"]
    username = os.environ["NETCONF_USERNAME"]
    password = os.environ["NETCONF_PASSWORD"]

    with manager.connect(
        host=host,
        port=830,
        username=username,
        password=password,
        hostkey_verify=True,
        timeout=30,
    ) as connection:

        print("Session NETCONF établie.")

        print("Capacités annoncées par le serveur :")
        for capability in connection.server_capabilities:
            print(capability)

        reply = connection.get_config(source="running")

        print("Réponse NETCONF reçue.")
        print(reply.xml)


if __name__ == "__main__":
    main()
```

Ce programme est un exemple pédagogique. Il suppose :

- que NETCONF est activé ;
- que le sous-système NETCONF est accessible ;
- que TCP 830 est utilisé ;
- que le compte dispose des permissions nécessaires ;
- que la clé d'hôte du serveur peut être vérifiée ;
- que le serveur expose le datastore `running`.

Consultez la documentation de la version installée de `ncclient` et les paramètres propres au serveur ciblé.

`hostkey_verify=True` évite de désactiver délibérément la vérification de la clé d'hôte. Pour que cette vérification fonctionne, les clés de confiance doivent être gérées correctement dans l'environnement d'exécution.

## 9.3. Comprendre `server_capabilities`

NETCONF permet au serveur de présenter ses capacités pendant l'établissement de session.

Ces capacités peuvent annoncer des opérations ou fonctionnalités prises en charge.

L'application peut s'en servir pour déterminer si certaines fonctions sont disponibles avant de les employer.

Par exemple, avant d'essayer d'utiliser un datastore `candidate`, il faut vérifier que le serveur annonce la capacité correspondante et comprendre les contraintes de l'implémentation.

Il ne faut pas coder en dur l'hypothèse que chaque serveur NETCONF dispose du même ensemble de fonctions.

## 9.4. Lire seulement certaines données

La méthode `get_config(source="running")` peut récupérer une grande partie de la configuration active.

C'est utile pour un premier exercice, mais peut être peu pratique lorsque l'équipement contient une configuration très longue.

Il est préférable, lorsque le modèle et les opérations le permettent, de cibler les données nécessaires.

Exemple conceptuel d'une opération de lecture ciblée en XML :

```xml
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
     message-id="103">
  <get>
    <filter type="subtree">
      <!-- Filtre conforme au modèle YANG visé -->
    </filter>
  </get>
</rpc>
```

Le contenu du filtre doit respecter l'espace de noms et la structure du modèle de données. Le commentaire ci-dessus est un emplacement pédagogique, pas un filtre complet à envoyer tel quel.

Pour les opérations concrètes, consultez la documentation du modèle YANG et les exemples de la bibliothèque choisie.

## 9.5. Comprendre la différence entre l'API et la bibliothèque

NETCONF est le protocole. `ncclient` est une bibliothèque Python qui l'implémente côté client.

Il faut distinguer :

- le protocole standard et ses opérations ;
- les capacités de l'équipement ;
- les fonctions exposées par la version de `ncclient` ;
- le code métier de votre application.

Une bibliothèque peut fournir des méthodes pratiques pour certaines opérations, mais elle ne peut pas inventer une capacité absente de l'équipement.

---

# 10. LIRE LES DONNÉES, DISTINGUER CONFIGURATION ET ÉTAT OPÉRATIONNEL

## 10.1. Configuration et état ne sont pas identiques

La configuration représente généralement les paramètres contrôlés par l'utilisateur ou l'application de gestion.

L'état opérationnel représente ce qui est observé ou produit par le fonctionnement de l'équipement.

Par exemple :

- **Configuration :** une interface est administrativement activée.
- **État opérationnel :** l'interface est effectivement en état `up` ou `down`.

Ces deux informations sont liées, mais elles ne sont pas équivalentes.

Une interface configurée comme activée peut rester `down` si aucune liaison physique n'est présente ou si un autre problème affecte son fonctionnement.

## 10.2. Exemple conceptuel

Configuration attendue :

```json
{
  "name": "GigabitEthernet0/0",
  "enabled": true
}
```

État observé :

```json
{
  "name": "GigabitEthernet0/0",
  "oper-status": "down"
}
```

Ces structures illustrent deux notions différentes. Le nom exact des champs et les chemins permettant d'accéder aux données varient selon le modèle utilisé.

Le programme doit comprendre quelle question il pose :

- « La configuration demande-t-elle une activation ? »
- « L'équipement rapporte-t-il un état opérationnel actif ? »

Une application ne doit pas confondre ces deux réponses.

## 10.3. Datastores et architecture de gestion

L'architecture des datastores est un sujet important de NETCONF et RESTCONF. Le [RFC 8342](https://www.rfc-editor.org/rfc/rfc8342.html) décrit l'architecture NMDA (*Network Management Datastore Architecture*).

À ce stade du parcours, retenez les points suivants :

1. un datastore n'est pas simplement un fichier JSON ;
2. les données de configuration et d'état peuvent être distinguées ;
3. l'accès dépend des capacités du serveur et du modèle de données ;
4. deux équipements peuvent exposer des ensembles de datastores différents ;
5. une application doit connaître le sens des données qu'elle lit.

## 10.4. Septième schéma SVG animé : configuration et état

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 350" role="img" aria-labelledby="state-title state-desc" style="max-width:100%;height:auto">
  <title id="state-title">Différence entre configuration et état opérationnel</title>
  <desc id="state-desc">La configuration décrit ce qui est demandé. L'équipement produit un état opérationnel. Le contrôleur compare l'état observé à l'objectif.</desc>
  <defs>
    <marker id="state-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#66c8a7"/></marker>
    <style>
      @keyframes state-flow { to { stroke-dashoffset:-28 } }
      .state-link { fill:none;stroke:#66c8a7;stroke-width:2.5;stroke-dasharray:7 7;marker-end:url(#state-arrow);animation:state-flow 2s linear infinite }
      .state-label { fill:#f4f6ff;font:600 15px sans-serif;text-anchor:middle }
      .state-small { fill:#becbe0;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="348" rx="14" fill="#0d1420" stroke="#293d56"/>
  <rect x="35" y="66" width="240" height="82" rx="10" fill="#282440" stroke="#b4a5f3" stroke-width="1.6"/>
  <text x="155" y="96" class="state-label">Configuration</text><text x="155" y="119" class="state-small">objectif déclaré</text><text x="155" y="135" class="state-small">ex. interface activée</text>
  <rect x="350" y="66" width="240" height="82" rx="10" fill="#183144" stroke="#62bee6" stroke-width="1.6"/>
  <text x="470" y="96" class="state-label">Équipement</text><text x="470" y="119" class="state-small">traitement réel</text><text x="470" y="135" class="state-small">configuration + environnement</text>
  <rect x="665" y="66" width="240" height="82" rx="10" fill="#17352e" stroke="#66c8a7" stroke-width="1.6"/>
  <text x="785" y="96" class="state-label">État opérationnel</text><text x="785" y="119" class="state-small">état observé</text><text x="785" y="135" class="state-small">ex. interface down</text>
  <path class="state-link" d="M275 107 H345"/><path class="state-link" d="M590 107 H660"/>
  <path class="state-link" d="M785 148 V206 H470 V153"/>
  <rect x="285" y="207" width="370" height="62" rx="10" fill="#332a1e" stroke="#e6b35e" stroke-width="1.6"/>
  <text x="470" y="231" class="state-label">Validation du besoin</text><text x="470" y="251" class="state-small">comparer l'état observé à l'objectif</text>
  <text x="470" y="305" class="state-small">Une configuration correcte ne garantit pas à elle seule un service opérationnel.</text>
</svg>

## 10.5. Exemple d'une validation métier

Supposons que votre objectif soit de vérifier qu'une interface est activée et opérationnelle.

Une validation simplifiée pourrait comporter :

1. vérifier que la configuration contient le champ attendu ;
2. récupérer l'état opérationnel ;
3. identifier l'interface correcte ;
4. comparer les valeurs ;
5. créer un résultat qui distingue conformité et non-conformité.

Une valeur manquante ne doit pas être automatiquement interprétée comme une valeur fausse ou comme une preuve de succès. Le programme doit tenir compte de la structure réellement retournée et de la sémantique du modèle.

---

# 11. COMPRENDRE LES ERREURS ET LES RÉPONSES

## 11.1. Pourquoi la distinction est importante

Une requête échouée peut provenir de plusieurs causes :

- problème DNS ;
- problème de routage ;
- port inaccessible ;
- serveur RESTCONF ou NETCONF désactivé ;
- authentification refusée ;
- permission insuffisante ;
- URI incorrecte ;
- modèle YANG indisponible ;
- encodage invalide ;
- opération non supportée ;
- validation métier incorrecte.

Une bonne automatisation doit aider à distinguer ces catégories.

## 11.2. Exemple de diagnostic RESTCONF

| Symptôme | Vérification initiale |
|---|---|
| Délai dépassé | Réseau, adresse, port, disponibilité du serveur |
| Erreur TLS | Certificat, chaîne de confiance, nom du serveur |
| `401` | Identifiants et méthode d'authentification |
| `403` | Permissions et règles d'accès |
| `404` | URI, modèle, ressource et chemin |
| `405` | Méthode autorisée pour la ressource |
| `415` | `Content-Type` et encodage demandé |
| `400` | Syntaxe, contenu ou contraintes de la requête |
| `5xx` | Erreur côté serveur ; consulter les détails autorisés |

Le code HTTP aide à classer le problème, mais le diagnostic peut demander d'examiner le corps de la réponse et les journaux de l'équipement.

## 11.3. Erreurs NETCONF

NETCONF utilise des réponses protocolaires et peut retourner des éléments `rpc-error`.

Le détail d'erreur peut inclure des informations telles que le type d'erreur, son emplacement ou un message explicatif, selon ce que le serveur fournit.

Les principales distinctions à faire sont :

- session impossible à établir ;
- erreur d'authentification ;
- erreur de protocole ou de capacité ;
- erreur de validation de la requête ;
- permission refusée ;
- erreur liée au datastore ;
- erreur de configuration ou de validation métier.

Un client ne doit pas interpréter toute exception comme une simple panne réseau.

## 11.4. Une requête techniquement réussie peut être insuffisante

Considérons une requête `GET` qui renvoie `200 OK`.

Cela prouve que le serveur a fourni une réponse HTTP avec ce statut. Cela ne prouve pas automatiquement que :

- toutes les interfaces ont été retournées ;
- le modèle contient tous les champs attendus ;
- les données sont assez récentes ;
- les valeurs sont conformes au besoin ;
- le service réseau fonctionne.

Il faut contrôler le schéma de données et les critères métier.

---

# 12. SÉCURITÉ DES API DE GESTION

Une API réseau permet souvent de lire des données sensibles et parfois de modifier directement la configuration d'un équipement. Elle doit donc être protégée au même titre que les autres interfaces d'administration.

## 12.1. Chiffrer les communications

RESTCONF doit être utilisé avec HTTPS/TLS dans un déploiement sécurisé. NETCONF sur SSH doit conserver les contrôles d'identité et d'authentification.

Le chiffrement du transport est nécessaire, mais pas suffisant.

Il faut également contrôler :

- l'identité du serveur ;
- l'identité du client ;
- les autorisations ;
- le réseau depuis lequel l'API est accessible ;
- la gestion des secrets ;
- la journalisation ;
- les opérations disponibles pour chaque compte.

## 12.2. Utiliser le principe du moindre privilège

Le compte de lecture doit pouvoir lire seulement les données nécessaires.

Le compte de modification doit disposer des permissions justifiées par les tâches qu'il effectue.

Ne donnez pas des privilèges administrateur complets à chaque script par facilité.

Une séparation des comptes réduit l'impact d'une erreur dans un programme de collecte et rend l'accès plus facile à auditer.

## 12.3. Protéger les certificats et les clés SSH

Pour TLS, conservez la vérification des certificats et gérez correctement la chaîne de confiance.

Pour SSH, vérifiez les clés d'hôtes au lieu de les accepter automatiquement sans contrôle.

Si la clé d'un équipement change, cette modification doit être expliquée et vérifiée par une source fiable.

## 12.4. Protéger les secrets

Évitez :

```python
password = "MonMotDePasseSuperSecret"
```

Préférez une méthode de résolution de secrets adaptée à l'environnement d'exécution.

Les variables d'environnement peuvent être pratiques pour un laboratoire ou certains pipelines, mais elles ne remplacent pas toujours un coffre de secrets géré.

Ne placez pas de mots de passe dans :

- le code source ;
- les fichiers d'inventaire ;
- le dépôt Git ;
- les journaux ;
- les messages d'erreur ;
- les rapports générés ;
- les captures d'écran partagées.

## 12.5. Protéger les opérations de modification

Une opération de lecture et une opération de configuration ne présentent pas les mêmes risques.

Avant toute modification :

1. identifier explicitement la cible ;
2. vérifier les autorisations ;
3. valider le corps de la requête ;
4. vérifier le chemin et le modèle ;
5. connaître l'effet de la méthode HTTP ou de l'opération RPC ;
6. prévoir un contrôle après modification ;
7. documenter la récupération si l'état final est incorrect.

Le mécanisme d'accès contrôlé de NETCONF et RESTCONF peut notamment être étudié dans le [RFC 8341 — Network Configuration Access Control Model](https://www.rfc-editor.org/rfc/rfc8341.html).

## 12.6. Huitième schéma SVG animé : défense en profondeur

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 360" role="img" aria-labelledby="security-title security-desc" style="max-width:100%;height:auto">
  <title id="security-title">Sécurité d'une API de gestion réseau</title>
  <desc id="security-desc">Une API de gestion doit protéger les identités, le transport, les autorisations, le périmètre et les opérations.</desc>
  <defs>
    <marker id="security-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#e7b363"/></marker>
    <style>
      @keyframes security-dash { to { stroke-dashoffset:-24 } }
      .security-link { fill:none;stroke:#e7b363;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#security-arrow);animation:security-dash 2s linear infinite }
      .security-label { fill:#f4f6ff;font:600 14px sans-serif;text-anchor:middle }
      .security-small { fill:#c2cde1;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="358" rx="14" fill="#111522" stroke="#313951"/>
  <text x="470" y="34" class="security-label">Plusieurs protections complémentaires</text>
  <rect x="40" y="70" width="190" height="64" rx="10" fill="#262340" stroke="#b2a1f0" stroke-width="1.6"/>
  <text x="135" y="96" class="security-label">Identité</text><text x="135" y="116" class="security-small">compte + secret</text>
  <rect x="266" y="70" width="190" height="64" rx="10" fill="#183144" stroke="#63bfe7" stroke-width="1.6"/>
  <text x="361" y="96" class="security-label">Transport</text><text x="361" y="116" class="security-small">TLS ou SSH</text>
  <rect x="492" y="70" width="190" height="64" rx="10" fill="#17352e" stroke="#68c9a5" stroke-width="1.6"/>
  <text x="587" y="96" class="security-label">Autorisation</text><text x="587" y="116" class="security-small">actions permises</text>
  <rect x="718" y="70" width="182" height="64" rx="10" fill="#33291d" stroke="#e7b363" stroke-width="1.6"/>
  <text x="809" y="96" class="security-label">Périmètre</text><text x="809" y="116" class="security-small">cibles autorisées</text>
  <path class="security-link" d="M230 102 H261"/><path class="security-link" d="M456 102 H487"/><path class="security-link" d="M682 102 H713"/>
  <rect x="190" y="190" width="560" height="75" rx="11" fill="#1b2538" stroke="#8aa6ca" stroke-width="1.6"/>
  <text x="470" y="218" class="security-label">Opération contrôlée</text>
  <text x="470" y="239" class="security-small">entrée validée · effet compris · résultat vérifié</text>
  <path class="security-link" d="M809 134 V167 H470 V185"/>
  <rect x="280" y="294" width="380" height="42" rx="9" fill="#24332a" stroke="#68c9a5" stroke-width="1.6"/>
  <text x="470" y="320" class="security-label">Logs protégés et preuve d'exécution</text>
  <path class="security-link" d="M470 265 V289"/>
</svg>

---

# 13. LABORATOIRES PROGRESSIFS

Les laboratoires ci-dessous constituent une progression. Chacun réutilise les notions acquises au laboratoire précédent.

Ne commencez pas par l'écriture automatique d'une configuration. Apprenez d'abord à lire, à contrôler les réponses et à comprendre les erreurs.

## Laboratoire 1 — Reconnaître une API

**Objectif :** comprendre les éléments de base d'une requête.

À faire :

1. identifier l'adresse de l'interface de gestion dans votre laboratoire ;
2. noter le protocole et le port utilisés ;
3. identifier le mécanisme d'authentification ;
4. repérer la racine RESTCONF ou l'accès NETCONF dans la documentation ;
5. vérifier la présence d'un modèle YANG pertinent ;
6. documenter les prérequis nécessaires à une requête.

**Livrable :** une fiche décrivant l'interface, son transport, les conditions d'accès et le modèle utilisé.

**Critères de réussite :** vous pouvez expliquer la différence entre API, protocole, encodage et modèle de données.

## Laboratoire 2 — Lire une ressource RESTCONF avec cURL

**Objectif :** envoyer une requête de lecture.

Étapes :

1. préparer les variables de connexion ;
2. vérifier la chaîne de confiance TLS ;
3. construire une URI valide ;
4. envoyer une requête `GET` ;
5. demander du JSON avec l'en-tête `Accept` ;
6. observer le code HTTP ;
7. inspecter la réponse ;
8. déterminer quels champs de données sont retournés.

**Variantes à tester :**

- URI incorrecte ;
- authentification invalide ;
- permission insuffisante ;
- mauvais en-tête de format ;
- serveur inaccessible.

**Critères de réussite :** chaque résultat est classé correctement et les erreurs sont interprétées sans désactiver les contrôles de sécurité.

## Laboratoire 3 — Reproduire la lecture avec Python

**Objectif :** réutiliser la requête dans un programme.

Étapes :

1. créer `restconf_get.py` ;
2. importer Requests ;
3. charger les paramètres depuis l'environnement ;
4. créer l'URI ;
5. ajouter l'en-tête d'acceptation ;
6. ajouter l'authentification ;
7. fixer un timeout ;
8. contrôler le certificat TLS ;
9. vérifier le statut HTTP ;
10. décoder le JSON ;
11. contrôler la structure retournée.

**Critères de réussite :** le programme termine proprement en cas d'erreur, ne stocke pas les secrets dans le code et vérifie au moins les éléments essentiels de la réponse.

## Laboratoire 4 — Découvrir les modèles

**Objectif :** comprendre quelle structure de données est réellement disponible.

Étapes :

1. identifier le modèle demandé ;
2. consulter la documentation et, si disponible, la YANG Library ;
3. relever les champs importants ;
4. relever les types ;
5. identifier les listes et leurs clés ;
6. repérer les nœuds de configuration et les données en lecture seule ;
7. confronter le modèle à la réponse reçue.

**Livrable :** un tableau du type :

| Champ | Type attendu | Présence observée | Utilité |
|---|---|---|---|
| `name` | chaîne | à vérifier | Identifiant |
| `description` | chaîne | à vérifier | Description |
| `enabled` | booléen | à vérifier | Configuration d'activation |
| `oper-status` | valeur du modèle | à vérifier | État opérationnel |

Les noms exacts, types et chemins doivent être vérifiés dans le modèle ciblé. Le tableau constitue un exercice, pas une promesse sur le contenu de chaque serveur.

## Laboratoire 5 — Lire une configuration avec NETCONF

**Objectif :** établir une session NETCONF et récupérer des données.

Étapes :

1. installer `ncclient` ;
2. identifier le port du service ;
3. vérifier l'accès SSH et la clé d'hôte ;
4. ouvrir une session avec `manager.connect()` ;
5. afficher les capacités ;
6. interroger le datastore `running`, s'il est disponible ;
7. afficher une partie de la réponse ;
8. fermer la session en fin d'exécution.

**Critères de réussite :** vous pouvez expliquer le rôle de la session, des capacités, de l'opération RPC et de la réponse XML.

## Laboratoire 6 — Comparer les résultats

**Objectif :** comprendre que les données peuvent être exprimées différemment suivant l'interface, le format et le modèle disponible.

Étapes :

1. récupérer une information d'interface avec RESTCONF ;
2. obtenir l'information correspondante avec NETCONF si les deux interfaces l'exposent ;
3. identifier les champs communs ;
4. vérifier les différences de représentation ;
5. examiner si la différence est due à l'encodage ou au modèle ;
6. noter les limites de la comparaison.

Ne supposez pas que les deux interfaces utilisent toujours la même ressource ou renvoient exactement les mêmes champs sur tous les équipements.

**Critère de réussite :** vous savez expliquer la différence entre une différence de représentation et une différence réelle de données.

## Laboratoire 7 — Vérifier configuration et état opérationnel

**Objectif :** aller au-delà d'une lecture syntaxique.

Étapes :

1. choisir une interface de laboratoire ;
2. récupérer sa configuration ;
3. récupérer son état opérationnel si le modèle le propose ;
4. identifier les champs pertinents ;
5. définir l'objectif attendu ;
6. écrire une vérification simple ;
7. produire un résultat explicite si l'état ne correspond pas à l'objectif.

**Critère :** un état non conforme ne doit jamais être signalé comme un succès simplement parce que les requêtes API ont fonctionné.

## Laboratoire 8 — Construire un mini-rapport d'audit

**Objectif :** produire un résultat exploitable.

Le rapport devrait contenir :

- l'identifiant du lot ;
- la cible ;
- le protocole utilisé ;
- l'heure de la requête ;
- le statut HTTP ou le résultat NETCONF ;
- les champs utiles collectés ;
- la validation métier ;
- le statut final ;
- une catégorie d'erreur en cas d'échec.

Évitez de consigner des identifiants ou des données sensibles sans nécessité.

---

# 14. PROJET FINAL GUIDÉ

## 14.1. Mission

Construire un petit programme nommé **Network API Auditor**.

Sa mission est de lire des informations sur un équipement de laboratoire via RESTCONF ou NETCONF, de vérifier la structure obtenue et de produire un rapport JSON.

Pour ce premier niveau, l'objectif est la lecture et la validation, pas la modification automatique de configuration.

## 14.2. Exigences fonctionnelles

Le programme doit :

1. charger les paramètres sans coder de mot de passe en dur ;
2. identifier le protocole utilisé ;
3. effectuer une lecture ;
4. gérer un délai maximal ;
5. contrôler les erreurs de transport et d'authentification ;
6. vérifier le format de réponse ;
7. valider la présence des champs requis ;
8. produire un résultat exploitable ;
9. ne pas enregistrer de secret ;
10. fermer la session NETCONF ou libérer les ressources HTTP ;
11. distinguer une lecture réussie d'une validation métier réussie.

## 14.3. Exemple de rapport final

```json
{
  "schema_version": 1,
  "target": "router-lab-01",
  "protocol": "RESTCONF",
  "operation": "read_interfaces",
  "status": "success",
  "validation": {
    "schema_ok": true,
    "required_fields_ok": true
  },
  "errors": []
}
```

Cette structure est un format pédagogique. Un projet réel devrait également documenter l'horodatage, l'identifiant du lot, la version du code et les détails nécessaires à la traçabilité.

## 14.4. Cas d'échec à tester

Un bon projet doit gérer au minimum :

- équipement inaccessible ;
- timeout ;
- certificat non valide ;
- authentification refusée ;
- permission insuffisante ;
- URI incorrecte ;
- réponse mal formée ;
- JSON valide mais structure inattendue ;
- champ obligatoire absent ;
- erreur NETCONF ;
- capacité nécessaire non disponible.

## 14.5. Barème conseillé

| Domaine | Points |
|---|---:|
| Compréhension du protocole | 15 |
| Connexion sécurisée | 15 |
| Lecture des données | 15 |
| Validation du contenu | 20 |
| Gestion des erreurs | 15 |
| Rapport JSON | 10 |
| Documentation et tests | 10 |
| **Total** | **100** |

Seuil recommandé : 80/100.

Une connexion fonctionnelle ne suffit pas si les certificats ne sont pas vérifiés, si les secrets sont codés en dur ou si l'application signale un succès malgré des données incorrectes.

---

# 15. DÉPANNAGE

## 15.1. RESTCONF ne répond pas

Vérifiez :

- la connectivité vers l'adresse de gestion ;
- le port HTTPS réellement utilisé ;
- l'activation du service RESTCONF ;
- le certificat ;
- les règles de pare-feu ;
- l'URI de base ;
- les paramètres propres à la version logicielle.

Un port ouvert ne prouve pas que le service RESTCONF est disponible sur le chemin demandé.

## 15.2. La requête renvoie `401`

Il faut vérifier l'authentification : identité, méthode acceptée, validité du compte et paramètres d'exécution.

N'affichez pas le mot de passe pour déboguer le problème. Vérifiez plutôt que le programme lit le bon secret et qu'il utilise la méthode attendue par l'équipement.

## 15.3. La requête renvoie `403`

L'authentification peut avoir réussi, mais l'opération ou les données ne sont pas autorisées pour ce compte.

Vérifiez les permissions et les règles d'accès au modèle ou à la ressource.

N'augmentez pas automatiquement les privilèges du compte. L'objectif est d'accorder les droits nécessaires, pas de donner des droits administrateur à toutes les applications.

## 15.4. La requête renvoie `404`

Vérifiez :

- la racine RESTCONF ;
- le chemin `/data` ;
- le nom du module ;
- la ressource ciblée ;
- les clés de la liste ;
- la disponibilité de la ressource dans le modèle.

La ressource peut être absente, le chemin peut être incorrect ou l'implémentation peut ne pas exposer les données attendues.

## 15.5. La requête renvoie `415`

Vérifiez l'en-tête `Content-Type` lorsque vous envoyez un corps, puis les types de représentation acceptés par le serveur.

Pour une lecture, examinez l'en-tête `Accept` ainsi que les capacités de l'implémentation.

Le format demandé doit correspondre à ce que le serveur peut fournir.

## 15.6. NETCONF ne s'établit pas

Vérifiez :

1. si NETCONF est activé ;
2. le port réellement configuré ;
3. le sous-système NETCONF ;
4. le compte et ses permissions ;
5. les clés SSH ;
6. les règles de pare-feu ;
7. la compatibilité de la bibliothèque ;
8. les capacités du serveur.

Une session SSH terminal fonctionnelle ne garantit pas que le sous-système NETCONF est activé.

## 15.7. `get-config` échoue

Le datastore demandé peut ne pas être pris en charge, l'utilisateur peut ne pas avoir le droit de lecture ou l'implémentation peut exposer des limitations spécifiques.

Examinez les capacités annoncées et les détails de l'erreur retournée. Ne supposez pas que tous les datastores existent sur toutes les plateformes.

## 15.8. Les données reçues ne correspondent pas au JSON attendu

Vérifiez le modèle, l'encodage demandé, la version du système et le chemin exact de la ressource.

Puis validez le contenu.

Un programme ne devrait pas simplement afficher « succès » parce que `response.json()` a fonctionné. Il faut également vérifier que les champs essentiels sont présents et respectent les types attendus.

## 15.9. L'API fonctionne mais les données semblent incorrectes

Une API peut renvoyer une configuration correcte alors que le service réseau n'est pas opérationnel.

Assurez-vous que vous lisez la bonne catégorie de données : configuration ou état opérationnel.

Définissez ensuite les critères métier adaptés à l'objectif du contrôle.

---

# 16. EXERCICES D'ÉVALUATION

Répondez avec vos propres mots et donnez un exemple lorsque cela est demandé.

1. Quelle différence existe entre une CLI et une API ?
2. Quel est le rôle de YANG ?
3. NETCONF et RESTCONF sont-ils des langages de modélisation ?
4. Quel format NETCONF utilise-t-il pour ses messages ?
5. Quels encodages de données RESTCONF peut-il utiliser ?
6. À quoi sert une URI RESTCONF ?
7. Quelle différence existe entre `GET`, `PUT` et `PATCH` ?
8. Pourquoi ne faut-il pas désactiver la vérification du certificat TLS ?
9. Quelle est la fonction de `ncclient` ?
10. Que sont les capacités NETCONF ?
11. À quoi correspondent les datastores `running` et `candidate` ?
12. Peut-on considérer qu'un `200 OK` prouve que le service réseau fonctionne ?
13. Pourquoi un champ YANG manquant ne doit-il pas être interprété automatiquement comme une valeur fausse ?
14. Pourquoi un modèle standard ne garantit-il pas que tous les équipements exposent exactement les mêmes fonctionnalités ?
15. Quels contrôles doit-on effectuer avant une modification de configuration via RESTCONF ou NETCONF ?

## Mini-exercice pratique

Supposons que vous souhaitiez consulter l'état de toutes les interfaces d'un équipement.

Répondez aux questions suivantes :

1. Quel protocole allez-vous tester en premier, et pourquoi ?
2. Quel module YANG pourrait être pertinent ?
3. Comment allez-vous découvrir si ce module est exposé ?
4. Quel type de requête ou d'opération allez-vous employer ?
5. Quels champs allez-vous contrôler dans la réponse ?
6. Comment distinguerez-vous un problème de transport d'un problème de permission ?
7. Comment indiquerez-vous qu'une interface est administrativement activée mais opérationnellement `down` ?

Vous pouvez ensuite implémenter le contrôle sous forme d'un petit script Python, puis produire un rapport JSON.

---

# 17. GLOSSAIRE

**API** — Interface définissant comment une application peut interagir avec un autre système.

**CRUD** — Create, Read, Update, Delete : créer, lire, mettre à jour et supprimer.

**Datastore** — Ensemble de données de gestion pouvant être utilisé par des opérations de lecture ou de configuration.

**HTTP** — Protocole de communication utilisé notamment pour les applications web.

**HTTPS** — HTTP protégé par TLS.

**JSON** — Format textuel de données structuré en objets, tableaux et valeurs.

**NETCONF** — Protocole de gestion des équipements réseau fondé sur des opérations RPC et des messages XML.

**RESTCONF** — Protocole de gestion basé sur HTTP donnant accès à des données et opérations modélisées avec YANG.

**RPC** — Remote Procedure Call, mécanisme par lequel un client demande l'exécution d'une opération à un serveur.

**SSH** — Protocole sécurisé permettant notamment des connexions distantes.

**TLS** — Protocole cryptographique qui protège les communications, notamment HTTPS.

**URI** — Identifiant de ressource utilisé notamment dans les requêtes HTTP.

**XML** — Format textuel utilisant des éléments et des attributs pour représenter des données structurées.

**YANG** — Langage de modélisation des données de gestion réseau.

**YANG Library** — Mécanisme fournissant des informations sur les modules et les schémas YANG utilisés par un serveur lorsqu'il est disponible.

---

# 18. RÉFÉRENCES OFFICIELLES

Les liens suivants conduisent aux spécifications et aux documentations à utiliser pour approfondir le sujet.

## Protocoles

- **RFC 6241 — Network Configuration Protocol (NETCONF)**  
  https://www.rfc-editor.org/rfc/rfc6241.html

- **RFC 6242 — Using the NETCONF Protocol over Secure Shell (SSH)**  
  https://www.rfc-editor.org/rfc/rfc6242.html

- **RFC 8040 — RESTCONF Protocol**  
  https://www.rfc-editor.org/rfc/rfc8040.html

## Modèles de données

- **RFC 7950 — The YANG 1.1 Data Modeling Language**  
  https://www.rfc-editor.org/rfc/rfc7950.html

- **RFC 7951 — JSON Encoding of Data Modeled with YANG**  
  https://www.rfc-editor.org/rfc/rfc7951.html

- **RFC 8342 — Network Management Datastore Architecture (NMDA)**  
  https://www.rfc-editor.org/rfc/rfc8342.html

- **RFC 8525 — YANG Library**  
  https://www.rfc-editor.org/rfc/rfc8525.html

- **RFC 8341 — Network Configuration Access Control Model (NACM)**  
  https://www.rfc-editor.org/rfc/rfc8341.html

## Bibliothèques

- **Requests pour Python**  
  https://requests.readthedocs.io/

- **ncclient pour Python**  
  https://github.com/ncclient/ncclient

- **Documentation de Python**  
  https://docs.python.org/3/

---

# CONCLUSION — LES FONDATIONS DU PARCOURS

Dans ce premier niveau, vous avez découvert pourquoi les API sont utiles pour l'automatisation réseau et pourquoi une approche model-driven diffère d'une interaction CLI traditionnelle.

Vous avez appris à distinguer trois éléments complémentaires :

- YANG décrit la structure des données ;
- NETCONF utilise des opérations RPC et des messages XML ;
- RESTCONF expose des ressources de gestion via HTTP.

Vous avez ensuite découvert les datastores, les capacités, les URI, les méthodes HTTP, les formats de données et les principaux contrôles de sécurité. Les laboratoires vous ont permis de passer progressivement de la lecture d'une requête à la construction d'un petit outil Python de collecte et de validation.

Ce socle sera réutilisé dans les niveaux suivants.

Au niveau Intermédiaire, le parcours pourra évoluer vers la sélection de ressources complexes, l'exploitation avancée des modèles YANG, la normalisation de plusieurs équipements, la gestion structurée des erreurs et la construction de collecteurs réutilisables.

Au niveau Expert, les mêmes bases serviront à construire des workflows de changement contrôlés, à gérer les datastores, à renforcer les validations, à intégrer les tests et à mettre en place une automatisation plus industrialisée.

**La règle à retenir :** une API ne se limite pas à une URL ou à une connexion SSH. Une automatisation fiable doit comprendre le protocole, le modèle de données, les droits accordés, le résultat observé et les conséquences de l'opération.

C'est à partir de cette compréhension que l'on passe d'une simple requête à une véritable automatisation réseau.