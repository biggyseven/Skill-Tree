
# NETCONF, YANG et RESTCONF — Niveau expert

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** maîtriser les modèles YANG, les échanges XML et JSON, les capacités NETCONF, les requêtes RESTCONF, les validateurs et les clients Python.  
> **Objectif :** concevoir des opérations de gestion réseau sûres, comprendre les mécanismes transactionnels, gérer les capacités et les écarts de modèles, contrôler les changements et vérifier l'état opérationnel réel.


## Sommaire

1. Architecture avancée des interfaces de gestion
2. YANG, datastores et architecture NMDA
3. Découverte de schémas et compatibilité des modèles
4. Transactions NETCONF et commit confirmé
5. Gestion des erreurs et des changements concurrents
6. Opérations RESTCONF avancées
7. Conception d'un moteur d'automatisation
8. Sécurité et contrôle d'accès
9. Cohérence, idempotence et état attendu
10. Vérification opérationnelle et notifications
11. Architecture de référence
12. Atelier expert
13. Étude de défaillance
14. Évaluation corrigée


# 1. Architecture avancée des interfaces de gestion

## 1.1 Le problème n'est plus simplement d'envoyer une requête

Une interface de gestion peut accepter une requête tout en laissant subsister un écart entre l'état attendu et le fonctionnement réel du réseau.

Le résultat dépend notamment :

- des modèles et révisions exposés par l'équipement ;
- des capacités du protocole ;
- des contraintes métier ;
- du datastore ciblé ;
- des permissions ;
- de l'état initial ;
- des dépendances avec d'autres équipements ;
- des éventuels changements concurrents ;
- du comportement réel après application.

Une architecture experte doit répondre à trois questions :

1. **Que peut-on demander à l'équipement ?**
2. **Dans quelles conditions la demande peut-elle être exécutée sans risque excessif ?**
3. **Comment démontrer que le résultat obtenu correspond à l'objectif ?**

Ces questions ne peuvent pas être résolues uniquement par un client NETCONF ou RESTCONF. Elles nécessitent une architecture qui combine modèles, contrôles, permissions, suivi et procédures opérationnelles.

## 1.2 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- expliquer les principaux datastores de l'architecture NMDA ;
- comprendre les limites des mécanismes transactionnels disponibles ;
- utiliser les capacités NETCONF pour conditionner les opérations ;
- distinguer commit normal et commit confirmé ;
- appliquer une stratégie de gestion des erreurs ;
- contrôler la compatibilité des modèles YANG ;
- comprendre les protections contre les écritures concurrentes ;
- utiliser des mécanismes de lecture et de modification RESTCONF adaptés ;
- définir un cycle précontrôle, changement et post-contrôle ;
- construire une méthode de récupération cohérente.


# 2. YANG, datastores et architecture NMDA

## 2.1 Le rôle de YANG dans une architecture complète

YANG définit la structure des données, les types, les contraintes et certaines opérations. Le protocole de gestion organise l'accès à ces données. Les datastores donnent un cadre conceptuel à leur stockage et à leur exposition.

Il faut distinguer :

- le modèle de données ;
- les valeurs présentes dans un datastore ;
- les opérations disponibles sur ce datastore ;
- l'état opérationnel réellement observé.

Ces éléments sont associés, mais ils ne sont pas interchangeables.

## 2.2 Configuration et état opérationnel

Une interface peut avoir une configuration administrative qui demande qu'elle soit active. Pourtant, elle peut être opérationnellement indisponible à cause d'une panne physique ou d'un problème de liaison.

Dans un modèle d'interface, on peut rencontrer des données telles que :

- `name` : identité de l'interface ;
- `enabled` : état administratif demandé ;
- `oper-status` : état opérationnel observé ;
- des compteurs et statistiques.

Le modèle standard `ietf-interfaces`, défini dans la RFC 8343, fournit une base pour la gestion des interfaces. Les détails disponibles dépendent du serveur et des extensions utilisées.

**Une valeur configurée n'est pas une preuve du comportement réel de l'équipement.**

## 2.3 NMDA : comprendre les datastores

L'architecture NMDA (*Network Management Datastore Architecture*), définie dans la RFC 8342, formalise plusieurs notions de datastore.

Parmi les éléments importants figurent :

| Datastore | Rôle général |
|---|---|
| `running` | Configuration courante du système |
| `candidate` | Configuration candidate séparée, lorsqu'elle est prise en charge |
| `startup` | Configuration de démarrage, selon l'implémentation |
| `intended` | Configuration prévue après les traitements applicables |
| `operational` | Vue des données reflétant l'état opérationnel du système |

Ces concepts ne sont pas exposés de manière identique par tous les protocoles et tous les équipements. Il ne faut donc pas supposer que chaque appareil fournit tous les datastores.

La configuration `intended` aide notamment à distinguer l'intention de configuration de l'état opérationnel constaté. L'opérationnel peut inclure des données apprises ou calculées par le système.

## 2.4 Schéma des datastores

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="nmda-title nmda-desc">
  <title id="nmda-title">Configuration attendue et état opérationnel NMDA</title>
  <desc id="nmda-desc">Les données de configuration alimentent la configuration prévue, qui est traitée par le système réseau. Le datastore opérationnel expose l'état observé, y compris les éléments dynamiques. Les flux sont indiqués par des lignes directionnelles animées en tirets, sans objet mobile.</desc>
  <defs>
    <marker id="nmda-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .nd-config{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .nd-state{fill:#123126;stroke:#4ade80;stroke-width:2}
      .nd-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .nd-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .nd-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#nmda-arrow);animation:nd-dash 1.8s linear infinite}
      @keyframes nd-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LE MODÈLE, LA CONFIGURATION ET L'ÉTAT NE SONT PAS IDENTIQUES</text>
  <rect class="nd-config" x="25" y="82" width="205" height="82" rx="10"/>
  <text class="nd-title" x="127" y="111" text-anchor="middle">running / candidate</text>
  <text class="nd-text" x="127" y="136" text-anchor="middle">Datastores de configuration</text>
  <rect class="nd-config" x="300" y="82" width="205" height="82" rx="10"/>
  <text class="nd-title" x="402" y="111" text-anchor="middle">intended</text>
  <text class="nd-text" x="402" y="136" text-anchor="middle">État de configuration prévu</text>
  <rect class="nd-config" x="575" y="82" width="180" height="82" rx="10"/>
  <text class="nd-title" x="665" y="111" text-anchor="middle">Traitement</text>
  <text class="nd-text" x="665" y="136" text-anchor="middle">Application au système</text>
  <rect class="nd-state" x="800" y="82" width="175" height="82" rx="10"/>
  <text class="nd-title" x="887" y="111" text-anchor="middle">operational</text>
  <text class="nd-text" x="887" y="136" text-anchor="middle">État observé</text>
  <path class="nd-flow" d="M230 123 H292"/>
  <path class="nd-flow" d="M505 123 H567"/>
  <path class="nd-flow" d="M755 123 H792"/>
  <rect class="nd-state" x="200" y="238" width="600" height="80" rx="12"/>
  <text class="nd-title" x="500" y="268" text-anchor="middle">Vérification des écarts</text>
  <text class="nd-text" x="500" y="291" text-anchor="middle">Comparer les valeurs attendues aux données réellement exposées</text>
  <path class="nd-flow" d="M887 164 V210 H800 V246"/>
  <path d="M200 278 H105 V198 H127 V171" fill="none" stroke="#a5b4fc" stroke-width="3" stroke-dasharray="7 7"/>
  <text class="nd-text" x="500" y="352" text-anchor="middle">L'état opérationnel peut différer de la configuration attendue.</text>
  <text class="nd-text" x="500" y="371" text-anchor="middle">Les datastores effectivement accessibles dépendent du protocole et de l'équipement.</text>
</svg>

## 2.5 Conséquence opérationnelle

Un moteur de conformité ne doit pas comparer aveuglément toutes les données de l'état opérationnel à un fichier de configuration.

Certaines valeurs sont dynamiques : compteurs, routes apprises, états calculés, statistiques ou informations dépendant de la topologie.

Il faut définir quelles propriétés doivent correspondre à l'intention, lesquelles sont uniquement surveillées et lesquelles ne peuvent pas être considérées comme stables.


# 3. Découverte de schémas et compatibilité des modèles

## 3.1 Pourquoi la révision du modèle est importante

Le nom d'un module ne suffit pas à identifier toute sa sémantique. Des révisions successives peuvent modifier les descriptions, ajouter des nœuds ou, dans certains cas, introduire des changements de comportement importants.

Un client doit connaître le schéma sur lequel ses requêtes reposent.

Pour chaque équipement ou groupe homogène, il est utile de suivre :

- la plateforme et sa version logicielle ;
- les modules YANG disponibles ;
- les révisions de modules ;
- les imports et les dépendances ;
- les fonctionnalités activées ;
- les extensions ou écarts documentés ;
- les opérations de protocole annoncées.

## 3.2 YANG Library

La YANG Library, définie notamment par la RFC 8525, décrit les modules, schémas et datastores utilisés par un serveur.

Elle offre un mécanisme de découverte important pour les clients qui doivent adapter leurs requêtes aux modèles réels.

La liste de modules d'un serveur ne doit pas être confondue avec une liste de capacités NETCONF. Les capacités du protocole et les schémas sont complémentaires.

## 3.3 Validation de compatibilité

Une chaîne de gestion peut effectuer plusieurs contrôles avant d'autoriser une opération :

1. vérifier que le module requis est présent ;
2. contrôler la révision ou le schéma attendu ;
3. résoudre les imports ;
4. confirmer que les nœuds requis existent ;
5. examiner les `features` et les éventuelles extensions ;
6. vérifier les permissions ;
7. s'assurer que l'opération demandée est disponible.

Lorsqu'un serveur change de logiciel ou de modèle, les résultats de tests précédents ne doivent pas être considérés comme automatiquement valables pour la nouvelle version.

## 3.4 Contrats de données et tests de compatibilité

Le dépôt doit définir quelles propriétés sont indispensables pour chaque automatisation.

Par exemple, un client qui utilise `interfaces/interface/name` et `interfaces/interface/enabled` doit vérifier la disponibilité de ces nœuds et leur type avant de s'appuyer sur eux.

Si l'un des nœuds n'existe pas, le client doit échouer explicitement ou appliquer une stratégie de compatibilité documentée. Il ne doit pas inventer un résultat par défaut sans signaler l'incertitude.


# 4. Transactions NETCONF et commit confirmé

## 4.1 La notion de transaction

Une opération de gestion n'est pas nécessairement une transaction complète couvrant tous les équipements d'un réseau.

NETCONF définit des mécanismes permettant de préparer et appliquer des changements dans les conditions prises en charge par le serveur. Le datastore `candidate`, lorsqu'il existe, permet de séparer la préparation de l'application au datastore courant.

Cela ne garantit pas à lui seul une transaction globale entre plusieurs équipements indépendants.

## 4.2 Cycle de modification avec `candidate`

Lorsque le serveur annonce la capacité nécessaire, un client peut utiliser un cycle de ce type :

1. examiner les capacités ;
2. verrouiller le datastore approprié si le mécanisme est disponible et requis par la procédure ;
3. lire l'état initial ;
4. effectuer les modifications sur `candidate` ;
5. demander une validation si la capacité existe ;
6. examiner les erreurs ;
7. commiter seulement lorsque les conditions sont satisfaites ;
8. effectuer des vérifications opérationnelles ;
9. libérer le verrou.

Cette séquence doit être adaptée à l'implémentation. Elle ne peut pas être exécutée aveuglément sur un serveur qui ne prend pas en charge les opérations requises.

## 4.3 Verrouillage et concurrence

Un datastore `candidate` peut être partagé entre plusieurs sessions. Un client doit tenir compte de ce risque avant de modifier les données.

Le verrouillage sert à contrôler certaines modifications concurrentes lorsque les mécanismes sont supportés. Il ne supprime pas tous les changements externes possibles et ne constitue pas un verrou global sur toute l'infrastructure.

Les opérations de verrouillage et de déverrouillage doivent être suivies correctement. Une session qui échoue peut laisser une situation à examiner suivant les règles du serveur et du protocole.

## 4.4 Validation avant commit

Lorsque la capacité `:validate` est disponible, un client peut demander au serveur de vérifier la configuration candidate.

Exemple de requête de validation :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rpc message-id="41"
     xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <validate>
    <source>
      <candidate/>
    </source>
  </validate>
</rpc>
```

Cet exemple suppose que la capacité correspondante est annoncée et que le datastore `candidate` est disponible.

Une validation réussie signifie que les contrôles du serveur acceptent la configuration candidate selon les règles qu'il applique. Cela ne démontre pas que le service fonctionnera correctement après son application.

## 4.5 `confirmed-commit`

La capacité de commit confirmé permet, sur les serveurs qui la prennent en charge, de demander une modification temporairement appliquée qui doit être confirmée dans le délai prévu.

Si le commit n'est pas confirmé avant l'expiration du délai, le serveur doit revenir à l'état antérieur conformément au mécanisme standard et aux règles applicables.

L'intérêt opérationnel est de limiter certains risques liés à une modification qui coupe l'accès ou provoque une dégradation.

Cette protection exige une planification précise. Le client doit savoir comment confirmer le commit et comment vérifier que la session, les chemins de gestion et les services nécessaires restent disponibles.

### Exemple conceptuel

Le flux suivant est illustratif :

```text
1. Vérifier :confirmed-commit:1.1
2. Préparer et valider candidate
3. Envoyer un commit confirmé avec un délai adapté
4. Vérifier les accès et les services critiques
5. Si les critères sont satisfaits : confirmer le commit
6. Sinon : laisser le mécanisme expirer ou annuler le commit selon le protocole
7. Vérifier l'état final et enregistrer le résultat
```

Le délai doit être suffisamment long pour effectuer les contrôles requis, mais pas choisi arbitrairement. Il doit tenir compte des opérations, des temps de convergence et de la capacité de récupération.

## 4.6 `rollback-on-error`

La capacité `:rollback-on-error`, lorsqu'elle est annoncée, permet de demander au serveur de revenir sur les modifications d'une opération d'édition en cas d'erreur, selon la sémantique du protocole.

Elle ne doit pas être confondue avec un mécanisme garantissant l'annulation de tout changement réparti entre plusieurs équipements.

Il faut vérifier la capacité annoncée et la portée exacte de l'opération concernée.

## 4.7 Schéma transactionnel NETCONF

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="410" viewBox="0 0 1000 410" role="img" aria-labelledby="expert-tx-title expert-tx-desc">
  <title id="expert-tx-title">Cycle transactionnel NETCONF</title>
  <desc id="expert-tx-desc">Le client vérifie les capacités, prépare les données sur candidate, valide, effectue un commit normal ou confirmé si disponible, puis vérifie l'état réel. Les branches d'échec arrêtent la progression et déclenchent la stratégie prévue.</desc>
  <defs>
    <marker id="expert-tx-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .tx-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .tx-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .tx-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .tx-stop{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .tx-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .tx-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .tx-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#expert-tx-arrow);animation:tx-dash 1.8s linear infinite}
      .tx-fail{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#expert-tx-arrow);animation:tx-dash 1.8s linear infinite}
      @keyframes tx-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="408" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">PRÉPARER, VALIDER, APPLIQUER ET VÉRIFIER</text>
  <rect class="tx-box" x="25" y="75" width="170" height="70" rx="10"/>
  <text class="tx-title" x="110" y="101" text-anchor="middle">Capacités</text>
  <text class="tx-text" x="110" y="123" text-anchor="middle">Session et schéma</text>
  <rect class="tx-box" x="225" y="75" width="170" height="70" rx="10"/>
  <text class="tx-title" x="310" y="101" text-anchor="middle">Candidate</text>
  <text class="tx-text" x="310" y="123" text-anchor="middle">Préparer les données</text>
  <rect class="tx-box" x="425" y="75" width="170" height="70" rx="10"/>
  <text class="tx-title" x="510" y="101" text-anchor="middle">Validate</text>
  <text class="tx-text" x="510" y="123" text-anchor="middle">Si pris en charge</text>
  <rect class="tx-gate" x="625" y="75" width="170" height="70" rx="10"/>
  <text class="tx-title" x="710" y="101" text-anchor="middle">Commit</text>
  <text class="tx-text" x="710" y="123" text-anchor="middle">Normal ou confirmé</text>
  <rect class="tx-ok" x="825" y="75" width="150" height="70" rx="10"/>
  <text class="tx-title" x="900" y="101" text-anchor="middle">Post-contrôles</text>
  <text class="tx-text" x="900" y="123" text-anchor="middle">État réel</text>
  <path class="tx-flow" d="M195 110 H218"/>
  <path class="tx-flow" d="M395 110 H418"/>
  <path class="tx-flow" d="M595 110 H618"/>
  <path class="tx-flow" d="M795 110 H818"/>
  <rect class="tx-stop" x="270" y="230" width="460" height="62" rx="10"/>
  <text class="tx-title" x="500" y="255" text-anchor="middle">Erreur ou résultat inattendu</text>
  <text class="tx-text" x="500" y="275" text-anchor="middle">Arrêt, diagnostic et procédure de récupération</text>
  <path class="tx-fail" d="M510 145 V205 H620 V223"/>
  <path class="tx-fail" d="M900 145 V205 H730 V230"/>
  <text class="tx-text" x="500" y="332" text-anchor="middle">Le commit et le rollback dépendent des capacités annoncées.</text>
  <text class="tx-text" x="500" y="352" text-anchor="middle">Une validation de configuration ne remplace pas les tests du service réel.</text>
  <text class="tx-text" x="500" y="379" text-anchor="middle">Les transactions NETCONF ne créent pas automatiquement une transaction réseau multi-équipements.</text>
</svg>


# 5. Gestion des erreurs et des changements concurrents

## 5.1 Distinguer les erreurs de protocole et les erreurs fonctionnelles

Un moteur avancé doit différencier :

- une connexion impossible ;
- un échec d'authentification ;
- un refus d'autorisation ;
- un élément ou une opération non pris en charge ;
- une contrainte YANG non satisfaite ;
- un conflit lié au verrouillage ;
- un délai dépassé ;
- une réponse ambiguë après une déconnexion ;
- un échec du post-contrôle fonctionnel.

Chaque catégorie doit conduire à une réaction définie.

Il est dangereux de relancer indifféremment toutes les erreurs. Une commande d'écriture dont le résultat est inconnu peut avoir été appliquée avant que la connexion soit interrompue.

## 5.2 Gestion des sessions et des verrous

Les applications doivent terminer proprement les sessions, libérer les verrous qu'elles ont pris et préserver les détails nécessaires au diagnostic.

Une application robuste doit prévoir les échecs qui surviennent :

- avant le verrouillage ;
- pendant la préparation ;
- pendant la validation ;
- pendant le commit ;
- après un commit confirmé mais avant sa confirmation ;
- pendant la lecture de vérification.

La stratégie exacte dépend des capacités annoncées et du comportement documenté du serveur.

## 5.3 Résultat inconnu

Il faut représenter explicitement un résultat inconnu. Un timeout ne prouve pas forcément que l'opération a échoué.

Lorsqu'une réponse n'a pas été reçue, le programme peut devoir relire l'état actuel ou consulter les journaux avant de décider si une action doit être réessayée.

Cette approche est plus sûre que de supposer qu'une opération idempotente ou non idempotente peut toujours être répétée sans conséquence.

## 5.4 Concurrence et changement externe

Les opérations de gestion peuvent entrer en concurrence avec :

- une autre application ;
- un administrateur ;
- un contrôleur réseau ;
- un système de configuration planifiée ;
- un processus de réconciliation.

Un verrou ou une lecture préalable ne remplace pas toutes les mesures de coordination. Le moteur doit détecter les écarts et déterminer si son autorisation reste valable au moment d'écrire.


# 6. Opérations RESTCONF avancées

## 6.1 RESTCONF et les ressources ciblées

RESTCONF expose les données définies en YANG sous forme de ressources. L'opération doit cibler la ressource appropriée et fournir un contenu conforme à son modèle.

La méthode HTTP utilisée ne suffit pas à déterminer le résultat : le chemin, le corps de la requête, le modèle et les permissions participent à la sémantique.

## 6.2 Contrôle des mises à jour concurrentes

Lorsqu'un serveur fournit une représentation versionnée d'une ressource au moyen d'un `ETag` et prend en charge les requêtes conditionnelles, le client peut utiliser `If-Match` afin d'éviter certaines écritures basées sur un état périmé.

Exemple de principe :

```text
1. GET de la ressource
2. Lecture de l'ETag retourné
3. Validation du changement candidat
4. PATCH avec If-Match utilisant cet ETag
5. Analyse du code HTTP et du corps
6. GET de vérification
```

Le client doit suivre la sémantique définie par RESTCONF et par le serveur. Si le mécanisme de conditionnalité n'est pas disponible, une stratégie alternative de coordination doit être conçue.

## 6.3 Les écritures RESTCONF ne sont pas des commits NETCONF

RESTCONF ne fournit pas un équivalent générique à tous les mécanismes NETCONF, notamment au cycle explicite `candidate`/`validate`/`commit` et au commit confirmé.

RESTCONF utilise les opérations HTTP sur les ressources exposées. Il ne faut pas déduire d'un succès HTTP la présence d'une transaction atomique traversant plusieurs équipements ou ressources.

Pour un changement à haut risque, l'application doit construire ses propres étapes de précontrôle, de validation, de limitation du périmètre et de post-contrôle dans les limites de ce que les protocoles et équipements permettent.

## 6.4 Contrôles après écriture

Après une modification RESTCONF :

1. examiner le statut HTTP ;
2. interpréter les éventuels détails d'erreur ;
3. relire la ressource pertinente ;
4. comparer la valeur observée à la valeur attendue ;
5. contrôler l'état opérationnel lorsque cela est nécessaire ;
6. enregistrer le résultat et l'identité de la release.

Une réponse réussie est une preuve de résultat au niveau de la requête, mais ne suffit pas toujours à prouver l'état fonctionnel attendu.


# 7. Conception d'un moteur d'automatisation

## 7.1 Séparer la logique des protocoles

Un moteur de gestion peut être organisé en composants distincts :

- **découverte** : recueille les capacités et les modèles ;
- **validation** : vérifie les données et les politiques ;
- **lecture** : collecte l'état initial ;
- **planification** : détermine les changements nécessaires ;
- **exécution** : applique les opérations autorisées ;
- **vérification** : compare l'état obtenu à l'état prévu ;
- **journalisation** : enregistre les actions et résultats ;
- **récupération** : suit une stratégie en cas d'échec.

Cette séparation évite de mélanger la construction de données avec l'exécution d'opérations privilégiées.

## 7.2 Exemple de résultat interne

Le moteur peut représenter le résultat de chaque équipement de la manière suivante :

```json
{
  "device": "SW-ACCESS-01",
  "release": "NET-CHANGE-0042",
  "capabilities_checked": true,
  "precheck": "passed",
  "validation": "passed",
  "execution": "not_started",
  "postcheck": "not_started",
  "decision": "awaiting_approval"
}
```

Cet objet représente un format de journal pédagogique, pas un résultat réel.

Les états doivent être définis précisément. Par exemple, `not_started`, `skipped`, `failed` et `unknown` doivent être distinguables. Ils ne doivent pas être regroupés sous un unique état « terminé ».

## 7.3 Idempotence

Une opération est idempotente si la répéter dans les mêmes conditions ne produit pas de changement supplémentaire au-delà du résultat déjà obtenu.

L'idempotence est une propriété importante pour l'automatisation déclarative, mais elle ne doit pas être supposée pour n'importe quelle opération. Certaines actions déclenchent des événements, créent des ressources ou ont des effets répétés.

Un moteur doit connaître la sémantique des opérations et, lorsque cela est possible, lire l'état avant de décider quoi changer.

## 7.4 État attendu et plan de changement

Une bonne chaîne peut calculer un plan de changement à partir :

- des données attendues ;
- de l'état réellement observé ;
- des modèles compatibles ;
- des exceptions autorisées ;
- du périmètre approuvé.

Le plan doit montrer ce qui sera modifié avant l'exécution. Il ne doit pas être appliqué automatiquement si les préconditions ou les autorisations ne sont plus valides.


# 8. Sécurité et contrôle d'accès

## 8.1 Transport sécurisé

Pour NETCONF sur SSH, vérifiez l'identité de l'hôte et limitez l'accès réseau au service de gestion.

Pour RESTCONF, utilisez HTTPS avec validation du certificat et une configuration TLS appropriée.

Le chiffrement du transport n'empêche pas un compte trop privilégié d'effectuer des modifications dangereuses.

## 8.2 Contrôle d'accès au niveau des données

Le modèle de contrôle d'accès réseau, défini dans la RFC 8341, décrit un mécanisme permettant de contrôler l'accès aux données et aux opérations de gestion NETCONF ou RESTCONF dans les implémentations compatibles.

Il peut servir à limiter les possibilités des utilisateurs selon leur rôle et les ressources concernées.

Une bonne séparation peut distinguer :

- la lecture d'état ;
- la lecture de configuration ;
- les modifications non critiques ;
- les modifications sensibles ;
- les opérations privilégiées ;
- l'administration de la politique d'accès.

La granularité exacte dépend de l'implémentation.

## 8.3 Comptes d'automatisation

Les identités utilisées par les clients doivent être dédiées, traçables et limitées aux capacités nécessaires.

Les mots de passe et clés ne doivent pas être inscrits dans le code, les dépôts ou les journaux. Un mécanisme de secrets doit être prévu, de même qu'une procédure de rotation et de révocation.

## 8.4 Journalisation sans exposition excessive

Les journaux devraient contenir suffisamment d'informations pour diagnostiquer une opération :

- identifiant de release ;
- équipement concerné ;
- opération et ressource visées ;
- horodatage ;
- résultat ;
- classe d'erreur ;
- référence du changement ;
- résultat de vérification.

Ils ne doivent pas recopier intégralement les données sensibles lorsque cela n'est pas nécessaire.


# 9. Cohérence, idempotence et état attendu

## 9.1 Une configuration valide peut être incohérente

Exemple : le modèle indique une interface active, mais le lien physique est indisponible. Les données sont syntaxiquement valides, mais le service attendu n'est pas assuré.

L'automatisation doit distinguer la conformité des paramètres et la conformité opérationnelle.

## 9.2 Définir les propriétés de conformité

Pour chaque changement, identifiez les propriétés à vérifier.

Exemples :

- le VLAN attendu existe ;
- la description d'une interface correspond au plan ;
- les routes critiques sont présentes ;
- une politique d'accès conserve les restrictions voulues ;
- les services critiques restent joignables ;
- les compteurs ou états ne montrent pas une dégradation définie comme critique.

Les tests doivent être proportionnés au changement. Une modification de description peut nécessiter moins de contrôles qu'une modification de routage ou de sécurité.

## 9.3 Ne pas imposer aveuglément la totalité d'un état

Les données observées peuvent contenir des éléments dynamiques et des exceptions légitimes. Une comparaison naïve entre deux arbres complets peut générer des écarts inutiles ou pousser le système à corriger des propriétés qu'il ne devrait pas contrôler.

Il est préférable de définir explicitement :

- les données gérées ;
- les données surveillées ;
- les données dynamiques ;
- les exceptions autorisées ;
- les propriétés critiques ;
- les critères d'arrêt.


# 10. Vérification opérationnelle et notifications

## 10.1 Vérification après changement

Après une modification, vérifiez à la fois les données de configuration et les propriétés fonctionnelles pertinentes.

Pour un changement d'interface, cela peut comprendre :

- l'état administratif demandé ;
- l'état opérationnel observé ;
- le statut de la liaison ;
- les compteurs adaptés au cas ;
- la connectivité d'un service critique.

Pour une modification de routage, la vérification peut porter sur la présence des routes attendues et sur la connectivité des destinations concernées.

La réussite d'un seul contrôle ne doit pas remplacer tous les autres contrôles qui ont été définis comme obligatoires.

## 10.2 Notifications et surveillance

NETCONF et l'écosystème YANG peuvent être utilisés avec des mécanismes de notification selon les modèles et fonctionnalités pris en charge.

Les notifications peuvent aider à détecter certains événements, mais elles ne remplacent pas nécessairement une lecture de vérification. Un événement peut être perdu, retardé ou insuffisant pour établir l'état complet d'un équipement.

Le système doit savoir comment recouper événements, collectes d'état et journaux de changement.

## 10.3 État d'un contrôle

Utilisez au minimum des résultats distincts pour :

- réussi ;
- échec ;
- non exécuté ;
- résultat inconnu ;
- ignoré selon une règle explicite.

Un post-contrôle qui n'a pas pu être exécuté ne doit pas être présenté comme réussi.


# 11. Architecture de référence

## 11.1 Vue globale

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420" role="img" aria-labelledby="expert-architecture-title expert-architecture-desc">
  <title id="expert-architecture-title">Architecture experte de gestion NETCONF et RESTCONF</title>
  <desc id="expert-architecture-desc">Les sources et modèles passent par la découverte des capacités, les validations et la planification. Une autorisation encadre l'exécution. Le résultat est vérifié sur les données opérationnelles, puis enregistré dans les journaux. En cas d'échec, les actions s'arrêtent selon une stratégie contrôlée.</desc>
  <defs>
    <marker id="expert-architecture-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .ex-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .ex-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .ex-state{fill:#123126;stroke:#4ade80;stroke-width:2}
      .ex-error{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .ex-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .ex-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .ex-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#expert-architecture-arrow);animation:ex-dash 1.8s linear infinite}
      .ex-fail{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#expert-architecture-arrow);animation:ex-dash 1.8s linear infinite}
      @keyframes ex-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="418" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">MODÈLES, AUTORISATIONS, EXÉCUTION ET PREUVES</text>
  <rect class="ex-box" x="25" y="70" width="175" height="74" rx="10"/>
  <text class="ex-title" x="112" y="98" text-anchor="middle">Sources + YANG</text>
  <text class="ex-text" x="112" y="121" text-anchor="middle">État attendu</text>
  <rect class="ex-box" x="230" y="70" width="175" height="74" rx="10"/>
  <text class="ex-title" x="317" y="98" text-anchor="middle">Découverte + tests</text>
  <text class="ex-text" x="317" y="121" text-anchor="middle">Schéma et capacités</text>
  <rect class="ex-box" x="435" y="70" width="175" height="74" rx="10"/>
  <text class="ex-title" x="522" y="98" text-anchor="middle">Plan de changement</text>
  <text class="ex-text" x="522" y="121" text-anchor="middle">Diff + préconditions</text>
  <rect class="ex-gate" x="640" y="70" width="165" height="74" rx="10"/>
  <text class="ex-title" x="722" y="98" text-anchor="middle">Autorisation</text>
  <text class="ex-text" x="722" y="121" text-anchor="middle">Permissions + revue</text>
  <rect class="ex-state" x="835" y="70" width="140" height="74" rx="10"/>
  <text class="ex-title" x="905" y="98" text-anchor="middle">Équipement</text>
  <text class="ex-text" x="905" y="121" text-anchor="middle">Opération réelle</text>
  <path class="ex-flow" d="M200 107 H223"/>
  <path class="ex-flow" d="M405 107 H428"/>
  <path class="ex-flow" d="M610 107 H633"/>
  <path class="ex-flow" d="M805 107 H828"/>
  <rect class="ex-box" x="300" y="240" width="400" height="70" rx="10"/>
  <text class="ex-title" x="500" y="268" text-anchor="middle">Post-contrôles et réconciliation</text>
  <text class="ex-text" x="500" y="290" text-anchor="middle">Configuration, état et critères de service</text>
  <path class="ex-flow" d="M905 144 V205 H700 V248"/>
  <rect class="ex-error" x="30" y="240" width="220" height="70" rx="10"/>
  <text class="ex-title" x="140" y="267" text-anchor="middle">Échec ou incertitude</text>
  <text class="ex-text" x="140" y="289" text-anchor="middle">Arrêt + diagnostic</text>
  <path class="ex-fail" d="M300 275 H258"/>
  <rect class="ex-state" x="750" y="240" width="220" height="70" rx="10"/>
  <text class="ex-title" x="860" y="267" text-anchor="middle">Audit et clôture</text>
  <text class="ex-text" x="860" y="289" text-anchor="middle">Preuves + résultats</text>
  <path class="ex-flow" d="M700 275 H742"/>
  <text class="ex-text" x="500" y="351" text-anchor="middle">Les opérations sensibles nécessitent des autorisations et des critères mesurables.</text>
  <text class="ex-text" x="500" y="373" text-anchor="middle">Une réponse de protocole ne remplace pas les preuves de conformité opérationnelle.</text>
  <text class="ex-text" x="500" y="395" text-anchor="middle">Toute incertitude critique doit empêcher la progression automatique tant qu'elle n'est pas résolue.</text>
</svg>

## 11.2 Garanties de conception

Une architecture solide doit établir :

**Compatibilité :** les modèles et capacités requis sont vérifiés.

**Validation :** les données et contraintes sont contrôlées avant l'exécution.

**Autorisation :** l'identité et les droits de l'opération sont vérifiés.

**Isolation :** les changements sont limités au périmètre approuvé.

**Cohérence :** l'état observé est comparé à des critères précis.

**Récupération :** un échec entraîne une décision contrôlée.

**Traçabilité :** chaque opération reste associée à ses résultats et à sa release.


# 12. Atelier expert

## Scénario

Une équipe doit modifier l'état administratif d'une interface sur un équipement de laboratoire. L'équipement expose NETCONF et un modèle d'interfaces standard. Le changement doit pouvoir être annulé automatiquement si le résultat attendu n'est pas obtenu, sous réserve du support réel des capacités requises.

L'atelier doit être réalisé sur un laboratoire isolé. Il ne doit pas être adapté à la production sans étude de risque, validation et approbation.

## Étape A — Découvrir le contexte

Avant toute opération :

- ouvrir une session de lecture ;
- inventorier les capacités NETCONF ;
- découvrir les modèles disponibles ;
- vérifier la présence de `candidate` ;
- vérifier la capacité de validation ;
- vérifier le support du commit confirmé ;
- relever l'état initial ;
- déterminer les services et accès qui doivent rester fonctionnels.

Si les mécanismes requis ne sont pas disponibles, arrêtez l'atelier et documentez une autre stratégie adaptée à l'équipement.

## Étape B — Construire le changement candidat

Le changement doit être représenté sous forme structurée et validé localement avant d'être envoyé.

Le programme doit vérifier :

- l'identité de l'équipement ;
- l'identifiant et le nom exact de l'interface ;
- la valeur souhaitée ;
- le périmètre autorisé ;
- la compatibilité avec le modèle ;
- l'existence d'une procédure de récupération.

## Étape C — Préparer le changement

Si le serveur le permet et que la procédure l'exige :

1. verrouiller le datastore approprié ;
2. relire l'état initial ;
3. modifier `candidate` ;
4. demander la validation ;
5. analyser le résultat et les erreurs éventuelles ;
6. interrompre le processus si une condition obligatoire échoue.

N'appliquez pas le changement en utilisant un mécanisme supposé. Les opérations doivent correspondre aux capacités réellement annoncées.

## Étape D — Appliquer sous protection

Lorsque le commit confirmé est disponible, le client peut utiliser cette fonctionnalité avec un délai adapté à la fenêtre de vérification.

La configuration candidate doit être appliquée uniquement après que les préconditions et les contrôles requis ont été satisfaits.

Après l'application, vérifiez immédiatement :

- que l'équipement reste accessible ;
- que l'état administratif correspond à la demande ;
- que l'état opérationnel est conforme aux attentes ;
- que les services critiques sont dans l'état prévu ;
- que le changement est bien appliqué au bon équipement.

## Étape E — Décision finale

Si tous les critères sont satisfaits, le client confirme le commit avant expiration du délai.

Si les contrôles échouent, la procédure doit permettre au changement de revenir à l'état antérieur conformément au mécanisme utilisé. Il faut ensuite vérifier que le rétablissement s'est effectivement produit.

Si le résultat est inconnu ou si le mécanisme de récupération ne fonctionne pas comme prévu, le système doit s'arrêter et requérir l'intervention prévue. Il ne doit pas continuer à agir comme si le retour arrière avait réussi.

## Étape F — Enregistrer les preuves

Le registre doit inclure :

- l'identité de l'équipement ;
- le modèle et les capacités constatés ;
- l'état initial ;
- le changement demandé ;
- les opérations exécutées ;
- les résultats des validations ;
- le résultat des post-contrôles ;
- la décision finale ;
- la confirmation ou l'expiration du commit confirmé ;
- les éventuelles actions manuelles.

L'atelier est réussi lorsque le cycle complet peut être expliqué et que chaque état correspond à un résultat effectivement observé.


# 13. Étude de défaillance

## Situation

Un client NETCONF prépare une modification. Le commit confirmé est envoyé, mais la connexion de gestion se coupe avant que le client reçoive la réponse.

Le programme ne sait pas si le changement a été appliqué.

## 13.1 Mauvaise stratégie

Une approche incorrecte consisterait à considérer automatiquement le changement comme échoué, puis à renvoyer la même écriture sans vérifier l'état.

Le premier commit peut avoir été accepté. Le second peut provoquer une action inattendue ou créer une nouvelle situation concurrente.

## 13.2 Stratégie robuste

1. Marquer le résultat comme inconnu.
2. Ne pas poursuivre les opérations dépendantes.
3. Tenter de retrouver un accès fiable à l'équipement.
4. Lire les datastores et données opérationnelles pertinents.
5. Vérifier les délais et l'état du commit confirmé selon les capacités du serveur.
6. Établir si la configuration est revenue à l'état initial, demeure appliquée ou présente un autre état.
7. Décider de la suite à partir de données observées et d'une procédure autorisée.
8. Documenter l'incident et les éléments qui ont permis d'établir le résultat.

Cette démarche évite de confondre perte de réponse et échec de l'opération.


# 14. Évaluation corrigée

## Questions

1. Quelle différence existe entre `running`, `candidate`, `intended` et `operational` ?
2. Pourquoi une transaction NETCONF ne garantit-elle pas une transaction réseau multi-équipements ?
3. Quel est l'intérêt du commit confirmé ?
4. Que permet `rollback-on-error` lorsqu'il est pris en charge ?
5. Pourquoi une validation réussie ne garantit-elle pas la disponibilité d'un service ?
6. Quel est l'intérêt de la YANG Library ?
7. Pourquoi une perte de connexion pendant un commit doit-elle produire un état inconnu ?
8. Comment un `ETag` et `If-Match` peuvent-ils réduire certains risques de concurrence ?
9. Pourquoi une opération RESTCONF ne doit-elle pas être assimilée à un commit NETCONF ?
10. Quel est le rôle de NACM ?
11. Pourquoi faut-il vérifier l'état opérationnel après une modification ?
12. Quelles informations faut-il conserver pour assurer la traçabilité d'une opération ?

## Corrigé

**1. Les datastores**

`running` correspond à la configuration courante ; `candidate` est une configuration de travail distincte lorsqu'elle existe ; `intended` représente la configuration prévue après les traitements applicables ; `operational` expose l'état opérationnel.

**2. Limite d'une transaction NETCONF**

Le mécanisme transactionnel agit sur les datastores pris en charge par un serveur. Il ne fournit pas automatiquement une transaction atomique globale sur des équipements indépendants.

**3. Commit confirmé**

Il permet d'appliquer provisoirement une modification qui doit être confirmée dans un délai défini, sinon le mécanisme prévu revient à l'état antérieur.

**4. Retour arrière sur erreur**

Lorsqu'il est disponible, il permet de demander le retour arrière des modifications de l'opération d'édition en cas d'erreur, dans le périmètre défini par le protocole.

**5. Validation et service**

Elle confirme uniquement les règles vérifiées. Des dépendances physiques, de routage, de sécurité ou de topologie peuvent encore provoquer une défaillance.

**6. YANG Library**

Elle aide le client à découvrir les modèles, schémas et modules exposés par un serveur.

**7. Résultat inconnu**

L'opération peut avoir été acceptée avant la perte de connexion. Le client doit observer l'état actuel avant de décider d'une nouvelle action.

**8. ETag et If-Match**

Lorsqu'ils sont pris en charge, ils permettent de conditionner une écriture à la version de ressource connue afin d'éviter certaines modifications basées sur un état périmé.

**9. RESTCONF et commit NETCONF**

RESTCONF applique la sémantique de ses ressources HTTP et ne fournit pas, de manière générique, le même cycle transactionnel NETCONF `candidate`/`validate`/`commit`.

**10. NACM**

Il fournit un modèle de contrôle d'accès aux données et opérations de gestion pour les implémentations compatibles.

**11. Contrôle opérationnel**

Il permet de confirmer que le changement a obtenu le résultat réel prévu, et pas seulement qu'une requête a été acceptée.

**12. Traçabilité**

Il faut conserver le contexte de l'opération, les données pertinentes, l'identité de la release, les actions effectuées, les résultats, les erreurs, les décisions et les preuves de vérification, tout en protégeant les éléments sensibles.


# Conclusion — Le niveau expert

NETCONF, YANG et RESTCONF forment un ensemble complémentaire, mais ils ne suffisent pas, à eux seuls, à garantir la sécurité d'un changement réseau.

Une approche experte doit :

- découvrir les capacités et les modèles réellement disponibles ;
- contrôler la cohérence de l'état attendu ;
- sélectionner les opérations adaptées ;
- utiliser les mécanismes transactionnels lorsqu'ils sont pris en charge ;
- traiter correctement les erreurs et les résultats inconnus ;
- protéger les identités et les permissions ;
- vérifier le résultat réel après modification ;
- conserver des preuves exploitables ;
- préparer la récupération avant l'exécution.

Le parcours est désormais cohérent :

**Débutant :** comprendre les rôles, les modèles et les protocoles.

**Intermédiaire :** valider les modèles, découvrir les capacités et construire des clients fiables.

**Expert :** maîtriser les transactions disponibles, la concurrence, la cohérence de l'état et la récupération opérationnelle.

**Le véritable niveau expert ne consiste pas à envoyer davantage de commandes : il consiste à contrôler ce qui peut être changé, à savoir ce qui a réellement changé et à réagir correctement quand le résultat n'est pas celui qui était attendu.**


## Références officielles

- NETCONF — RFC 6241 : https://www.rfc-editor.org/rfc/rfc6241.html
- NETCONF sur SSH — RFC 6242 : https://www.rfc-editor.org/rfc/rfc6242.html
- YANG 1.1 — RFC 7950 : https://www.rfc-editor.org/rfc/rfc7950.html
- RESTCONF — RFC 8040 : https://www.rfc-editor.org/rfc/rfc8040.html
- Architecture NMDA — RFC 8342 : https://www.rfc-editor.org/rfc/rfc8342.html
- Modèle d'interfaces — RFC 8343 : https://www.rfc-editor.org/rfc/rfc8343.html
- YANG Library — RFC 8525 : https://www.rfc-editor.org/rfc/rfc8525.html
- Network Configuration Access Control Model — RFC 8341 : https://www.rfc-editor.org/rfc/rfc8341.html
- JSON Encoding of YANG Data — RFC 7951 : https://www.rfc-editor.org/rfc/rfc7951.html
- ncclient : https://github.com/ncclient/ncclient
- pyang : https://github.com/mbj4668/pyang

**Fichier :** `netconf-yang-expert.md`  
**Niveau :** Expert  
**Fin du cours**
