# Observabilité avancée (Tracing, Logs)

## Niveau expert

## 1. Présentation générale

Au niveau débutant, nous avons appris à consulter les journaux et à comprendre les principales métriques d'un système. Au niveau intermédiaire, nous avons construit une plateforme de supervision avec Prometheus, Grafana, des exportateurs et des alertes.

Ce niveau expert aborde une difficulté supplémentaire : comprendre ce qui se passe **à l'intérieur d'une transaction distribuée qui traverse plusieurs services**, puis relier cette transaction aux journaux, aux métriques et aux événements d'exploitation.

Dans une architecture moderne, une requête peut traverser un reverse proxy, une API, un service d'authentification, une file de messages, plusieurs microservices et une base de données. Chaque composant peut fonctionner correctement individuellement alors que la transaction complète est lente ou échoue.

L'observabilité avancée permet de reconstituer ce parcours, d'identifier les étapes coûteuses, de corréler les événements et d'examiner les causes probables d'une dégradation.

Nous allons approfondir quatre axes :

- **Distributed tracing** : suivre une transaction entre plusieurs composants.
- **Centralisation des journaux** : collecter, structurer, rechercher et corréler les événements.
- **Corrélation des signaux** : associer traces, journaux et métriques pour diagnostiquer les incidents.
- **Industrialisation de l'observabilité** : instrumentation, OpenTelemetry Collector, échantillonnage, sécurité, rétention, coût et fiabilité.

Le laboratoire s'appuiera sur les technologies suivantes :

| Composant | Rôle |
|---|---|
| OpenTelemetry | Instrumenter les applications et normaliser la télémétrie |
| OpenTelemetry Collector | Recevoir, traiter et transmettre les signaux |
| Grafana Tempo | Stocker et rechercher les traces |
| Grafana Loki | Collecter et interroger les journaux |
| Grafana Alloy | Collecter et transmettre les journaux du laboratoire |
| Prometheus | Collecter les métriques système |
| Grafana | Explorer et corréler les données |
| FastAPI | Fournir une application de démonstration instrumentée |

Les exemples sont conçus pour un environnement pédagogique. La configuration du stockage local, l'absence d'authentification interne sur certains composants et l'utilisation de versions flottantes doivent être adaptées avant tout déploiement de production.

## 2. Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit pouvoir :

1. Expliquer la différence entre logs, métriques, traces et profils.
2. Comprendre la structure d'une trace distribuée.
3. Interpréter les relations parent-enfant entre les spans.
4. Expliquer la propagation du contexte entre services.
5. Comprendre les identifiants `trace_id` et `span_id`.
6. Instrumenter une application avec OpenTelemetry.
7. Déployer un OpenTelemetry Collector.
8. Configurer un backend de traces avec Tempo.
9. Centraliser des journaux avec Loki et Grafana Alloy.
10. Structurer les logs au format JSON.
11. Corréler une erreur applicative, une trace et des métriques.
12. Interroger les journaux avec LogQL.
13. Rechercher les traces avec TraceQL.
14. Comprendre l'échantillonnage en tête et en fin de trace.
15. Réduire la cardinalité des métriques et des labels de journaux.
16. Concevoir une politique de rétention et de protection des données.
17. Diagnostiquer un incident distribué.
18. Mesurer la latence, le taux d'erreur et le débit des services.
19. Sécuriser une chaîne d'observabilité.
20. Construire un laboratoire démontrant la corrélation des trois signaux principaux.

## 3. Pourquoi les métriques et les journaux ne suffisent-ils pas toujours ?

### 3.1 Exemple d'une application distribuée

Imaginons une plateforme de commerce électronique.

Lorsqu'un utilisateur commande un produit, le navigateur appelle un serveur Web. Celui-ci sollicite une API de commande, qui vérifie le stock, demande une autorisation de paiement et enregistre la transaction.

```text
                UTILISATEUR
                     |
                     v
               REVERSE PROXY
                     |
                     v
                SERVICE WEB
                     |
                     v
                 API COMMANDE
                     |
          +----------+----------+
          |                     |
          v                     v
     SERVICE STOCK        SERVICE PAIEMENT
          |                     |
          v                     v
      BASE STOCK           API EXTERNE
          |
          v
     BASE COMMANDE
```

Chaque service possède ses propres journaux et peut exposer ses métriques.

Une équipe peut constater que :

- Le serveur Web fonctionne.
- L'API de commande est accessible.
- Le service de stock répond normalement.
- La base de données accepte les connexions.

Pourtant, l'utilisateur attend huit secondes avant de recevoir une réponse.

Les métriques indiquent la dégradation, mais ne donnent pas nécessairement la chronologie précise de la transaction. Les journaux peuvent contenir des événements pertinents, sans permettre de déterminer facilement lesquels appartiennent à la même requête.

Le tracing répond à cette difficulté.

### 3.2 Les trois signaux principaux

<box-placeholder/>

```text
                         TRANSACTION
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
          METRIQUES         JOURNAUX           TRACES
             |                |                |
             v                v                v
        QUANTIFIER         EXPLIQUER       RECONSTITUER
             |                |                |
             +----------------+----------------+
                              |
                              v
                     DIAGNOSTIC COMPLET
```

Les métriques servent à mesurer une tendance ou un comportement. Les journaux décrivent des événements. Les traces montrent le parcours d'une opération entre ses composants.

Ces données deviennent beaucoup plus utiles lorsqu'elles partagent des informations de corrélation cohérentes.

### 3.3 Le quatrième signal : les profils

Le profilage continu, ou *continuous profiling*, permet d'observer la consommation des ressources à l'intérieur du code, par exemple le temps CPU passé dans certaines fonctions ou les allocations mémoire.

Les profils peuvent aider lorsqu'une trace indique qu'un service est lent, mais ne permet pas d'identifier la fonction responsable.

Il faut distinguer les quatre approches :

| Signal | Question principale |
|---|---|
| Métriques | Quand et à quelle fréquence le problème se produit-il ? |
| Journaux | Quels événements ont été enregistrés ? |
| Traces | Où le temps est-il passé dans la transaction ? |
| Profils | Quelles fonctions consomment les ressources ? |

Ce cours approfondit surtout les traces et les journaux, tout en conservant les métriques comme point d'entrée du diagnostic.

## 4. Comprendre le distributed tracing

### 4.1 Qu'est-ce qu'une trace ?

Une trace représente le parcours logique d'une opération dans un système distribué.

Elle peut représenter :

- Une requête HTTP.
- Une opération de paiement.
- Une transaction métier.
- Un traitement asynchrone.
- Un travail transmis par une file de messages.
- Une requête traversant plusieurs services.

Une trace comporte un identifiant commun, appelé `trace_id`, et un ensemble de spans décrivant les opérations associées.

### 4.2 Qu'est-ce qu'un span ?

Un span représente une unité de travail observée pendant une durée donnée.

Il contient généralement :

- Un identifiant de trace.
- Un identifiant de span.
- Une référence au span parent, lorsqu'il existe.
- Un nom d'opération.
- Une heure de début.
- Une durée.
- Des attributs.
- Des événements éventuellement associés.
- Un statut.

Exemple :

```text
Trace : commande-12345

Span racine : POST /orders
  Durée : 850 ms
  |
  +-- Span : inventory.check
  |     Durée : 110 ms
  |
  +-- Span : payment.authorize
  |     Durée : 520 ms
  |
  +-- Span : database.insert_order
        Durée : 90 ms
```

Les durées des spans enfants ne doivent pas être additionnées systématiquement pour obtenir la durée totale. Certains spans peuvent se chevaucher ou représenter des travaux parallèles.

### 4.3 Trace et span

Une trace peut contenir un ou plusieurs spans.

```text
TRACE
  trace_id = 4bf92f3577b34da6a3ce929d0e0e4736

  SPAN RACINE
    span_id = 00f067aa0ba902b7
    operation = POST /orders

      SPAN ENFANT
        span_id = 1111111111111111
        operation = inventory.check

      SPAN ENFANT
        span_id = 2222222222222222
        operation = payment.authorize
```

Les identifiants du dessin sont illustratifs. Une véritable trace utilise les identifiants générés par le système d'instrumentation.

Le `trace_id` permet de retrouver la trace. Le `span_id` permet d'identifier une opération précise dans cette trace.

### 4.4 Identifier la durée et les relations

Une visualisation de trace présente généralement les spans sous forme de chronologie.

```text
Temps ---------------------------------------------------->

POST /orders       |======================================|
inventory.check       |======|
payment.authorize             |==================|
database.insert_order                              |=====|
```

Ce schéma simplifie volontairement les durées et les chevauchements.

En examinant une trace réelle, on peut rechercher :

- Un span qui prend anormalement longtemps.
- Un appel HTTP externe lent.
- Une opération de base de données coûteuse.
- Un délai d'attente.
- Un traitement asynchrone.
- Une erreur remontée par un service dépendant.

## 5. La structure complète d'un span

### 5.1 Nom de l'opération

Le nom doit représenter une opération compréhensible.

Exemples utiles :

```text
GET /products/{product_id}
POST /orders
inventory.check
payment.authorize
database.query
```

Éviter les noms qui changent pour chaque requête :

```text
GET /products/123
GET /products/124
GET /products/125
```

Si l'identifiant du produit est intégré au nom du span, le nombre d'opérations distinctes peut devenir très élevé.

Préférer une route normalisée et conserver les attributs de la requête dans des champs adaptés, lorsque cela est pertinent et conforme aux exigences de confidentialité.

### 5.2 Attributs

Les attributs sont des paires clé-valeur qui décrivent le contexte d'une opération.

Exemples :

```text
service.name                  = checkout-api
service.version               = 1.0.0
http.request.method           = POST
http.response.status_code     = 500
deployment.environment.name   = production
db.system.name                = postgresql
```

Les noms doivent suivre autant que possible les conventions sémantiques OpenTelemetry.

Les conventions évoluent selon les versions. Il faut vérifier la convention correspondant aux bibliothèques utilisées, notamment pour les attributs HTTP, base de données et messagerie.

### 5.3 Événements

Un span peut contenir des événements horodatés décrivant des moments importants.

Exemple :

```text
Span : payment.authorize
Durée totale : 520 ms

Événements :
  +000 ms : appel commencé
  +120 ms : réponse intermédiaire reçue
  +450 ms : nouvelle tentative
  +520 ms : résultat final reçu
```

Un événement n'est pas nécessairement un span supplémentaire. Il peut annoter un span existant.

### 5.4 Statut d'un span

Le statut indique notamment si l'opération a échoué.

Les principaux états OpenTelemetry sont :

- `UNSET` : aucun statut explicite n'a été défini.
- `OK` : l'opération a été explicitement considérée comme réussie.
- `ERROR` : l'opération a échoué.

Il est important de ne pas considérer automatiquement tous les statuts `UNSET` comme des erreurs. De nombreuses opérations réussies conservent leur statut initial.

L'instrumentation doit définir les erreurs selon la sémantique réelle de l'opération.

### 5.5 Type de span

Les types de spans, aussi appelés *span kinds*, décrivent la relation entre une opération et son environnement.

| Type | Utilisation habituelle |
|---|---|
| `SERVER` | Traitement d'une requête reçue par un service |
| `CLIENT` | Appel effectué vers un service ou système externe |
| `INTERNAL` | Opération interne au service |
| `PRODUCER` | Production d'un message asynchrone |
| `CONSUMER` | Consommation d'un message asynchrone |

Cette classification facilite la lecture des traces et l'analyse des relations entre composants.

### 5.6 Links entre spans

La relation parent-enfant ne représente pas tous les scénarios.

Dans certains traitements asynchrones, un span peut être lié à un autre sans être son enfant direct. Les liens sont notamment utiles pour les travaux qui agrègent plusieurs événements ou contextes.

Exemple :

```text
Message A ----+
              |
Message B ----+----> Traitement d'agrégation
              |
Message C ----+
```

Le traitement d'agrégation peut être lié aux contextes des messages sources au lieu de représenter toute la durée du traitement comme un simple enfant d'un seul span précédent.

## 6. L'identité d'une trace : `trace_id` et `span_id`

### 6.1 Le trace ID

Le `trace_id` identifie une trace.

Dans le format habituellement utilisé par OpenTelemetry, un trace ID valide est représenté par 32 caractères hexadécimaux minuscules.

Exemple :

```text
4bf92f3577b34da6a3ce929d0e0e4736
```

Les spans appartenant à la même trace partagent ce trace ID.

### 6.2 Le span ID

Le `span_id` identifie un span.

Il est habituellement représenté par 16 caractères hexadécimaux minuscules.

Exemple :

```text
00f067aa0ba902b7
```

Deux spans différents ne doivent pas partager le même identifiant dans le contexte d'une trace.

### 6.3 Pourquoi enregistrer les deux dans les journaux ?

Le trace ID permet de retrouver la transaction globale. Le span ID permet de rapprocher un événement de l'opération précise qui l'a produit.

Exemple de journal structuré :

```json
{
  "timestamp": "2026-10-24T09:42:13.125Z",
  "level": "error",
  "service_name": "checkout-api",
  "event": "payment_authorization_failed",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7"
}
```

Les identifiants sont des valeurs d'exemple. Dans une application réelle, ils doivent être injectés automatiquement depuis le contexte actif, et non recopiés manuellement.

## 7. Propagation du contexte distribué

### 7.1 Pourquoi la propagation est-elle nécessaire ?

Supposons qu'un service Web reçoive une requête puis appelle une API interne.

Sans propagation, chaque service peut créer une trace indépendante. Les événements existent, mais il devient difficile de reconstituer le parcours complet.

Avec propagation, le service appelant transmet le contexte de traçage à la requête suivante.

```text
Service A
  Crée une trace
      |
      v
  Envoie le contexte
      |
      v
Service B
  Reçoit le contexte
      |
      v
  Crée un span enfant
      |
      v
Service C
  Reçoit et propage le contexte
```

Le contexte établit le lien entre les opérations sans nécessiter de convention manuelle pour chaque appel.

### 7.2 Le standard W3C Trace Context

Le mécanisme W3C Trace Context définit notamment l'en-tête HTTP `traceparent`.

Exemple de format :

```text
traceparent:
00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
```

Il contient généralement :

```text
00                       Version
4bf92f3577b34da6a3ce929d0e0e4736
                         Trace ID
00f067aa0ba902b7          Parent ID
01                       Trace flags
```

Ces champs transportent l'identité de la trace et celle du span précédent, ainsi que des informations de propagation.

Le contenu d'un en-tête ne constitue pas une identité fiable de l'utilisateur et ne doit jamais être utilisé comme mécanisme d'autorisation.

### 7.3 Le baggage

Le baggage permet de transmettre des paires clé-valeur associées au contexte distribué.

Il peut être utilisé, par exemple, pour transporter une information de routage ou un contexte métier non sensible.

Il faut éviter d'y placer des mots de passe, des jetons, des données personnelles ou toute information confidentielle. Le baggage peut être propagé au travers de plusieurs services, ce qui augmente le nombre de composants susceptibles de recevoir ces données.

Les services doivent définir une politique claire sur les informations autorisées.

### 7.4 Propagation à travers les frontières

Une propagation automatique ne fonctionnera que si les composants sont compatibles et configurés correctement.

Il faut notamment examiner :

- Les bibliothèques d'instrumentation.
- Les en-têtes acceptés et transmis.
- Les reverse proxies.
- Les API externes.
- Les clients HTTP.
- Les files de messages.
- Les tâches asynchrones.
- Les frontières de confiance.

Un service externe peut ne pas propager le contexte. Il faut aussi tenir compte du risque de recevoir un contexte fourni par un client non fiable.

## 8. OpenTelemetry : architecture et composants

### 8.1 Qu'est-ce qu'OpenTelemetry ?

OpenTelemetry est un ensemble de spécifications, d'API, de SDK et d'outils destinés à produire, collecter et exporter des données d'observabilité.

Il permet de normaliser l'instrumentation et la transmission des signaux sans imposer un unique backend de stockage ou de visualisation.

OpenTelemetry n'est pas, à lui seul, une plateforme de stockage ou une interface graphique.

### 8.2 Les composants principaux

**API :** définit les interfaces utilisées pour créer les spans et émettre des mesures.

**SDK :** implémente la collecte, l'échantillonnage, les processeurs et l'export des données.

**Instrumentation :** ajoute les informations de télémétrie dans le code ou autour de bibliothèques existantes.

**Exporter :** transmet les données vers une destination compatible.

**Collector :** reçoit, traite et exporte les signaux selon une configuration.

**Backend :** stocke les données et permet de les interroger.

**Visualisation :** fournit les tableaux de bord, explorateurs et outils de diagnostic.

### 8.3 Architecture type

```text
                APPLICATIONS
                     |
            +--------+--------+
            |                 |
            v                 v
      Instrumentation     Logs structurés
            |                 |
            v                 v
       SDK OpenTelemetry   Collecteur de logs
            |                 |
            v                 v
            +--------+--------+
                     |
                     v
              OpenTelemetry
                 Collector
                     |
          +----------+----------+
          |                     |
          v                     v
       Export Traces        Export Logs
          |                     |
          v                     v
         Tempo                  Loki
          |                     |
          +----------+----------+
                     |
                     v
                  Grafana
```

Dans une architecture réelle, les journaux peuvent suivre un pipeline distinct, comme Alloy vers Loki, tandis que le Collector reçoit les traces et éventuellement les métriques et journaux OTLP.

Cette séparation est acceptable si les schémas de corrélation restent cohérents.

### 8.4 OTLP

OTLP signifie OpenTelemetry Protocol. Il définit un protocole de transmission des données OpenTelemetry.

Les ports courants d'un Collector recevant OTLP sont :

- `4317` pour OTLP sur gRPC.
- `4318` pour OTLP sur HTTP.

Ces ports peuvent être modifiés par la configuration.

Il faut différencier le port, le protocole et l'endpoint. Un exporteur gRPC et un exporteur HTTP ne construisent pas leurs requêtes de la même manière.

### 8.5 Pourquoi introduire un Collector ?

Sans Collector, chaque application peut envoyer ses traces directement vers un backend.

Cette approche est acceptable pour un laboratoire ou une application isolée, mais elle complique l'exploitation quand les applications sont nombreuses.

Le Collector permet de centraliser :

- La réception.
- Les traitements communs.
- La limitation mémoire.
- Le regroupement des données.
- La transformation des attributs.
- La suppression de champs sensibles.
- L'échantillonnage lorsque cela est nécessaire.
- L'export vers plusieurs systèmes selon la configuration.

Le Collector est lui-même un composant critique qui nécessite supervision, dimensionnement et sécurisation.

## 9. Les pipelines de l'OpenTelemetry Collector

### 9.1 Structure d'un pipeline

Un pipeline comporte généralement des receivers, des processors et des exporters.

```text
             RECEIVER
        Réception des données
                  |
                  v
             PROCESSORS
       Filtrage / Transformation
       Limitation / Regroupement
                  |
                  v
             EXPORTER
       Transmission à destination
```

Les catégories sont les suivantes :

**Receivers :** acceptent les données depuis une application ou une source.

**Processors :** transforment ou filtrent les données avant export.

**Exporters :** transmettent les données à un backend ou service.

D'autres composants existent, notamment les extensions et connecteurs. Leur disponibilité dépend de la distribution du Collector employée.

### 9.2 Exemples de composants

| Composant | Utilité |
|---|---|
| OTLP receiver | Recevoir les signaux OTLP |
| Batch processor | Regrouper les données avant export |
| Memory limiter | Limiter les risques liés à une consommation mémoire excessive |
| Attributes processor | Modifier ou supprimer des attributs |
| Resource processor | Modifier les attributs des ressources |
| Filter processor | Filtrer certaines données |
| Tail sampling processor | Échantillonner les traces à partir du contenu observé |
| OTLP exporter | Transmettre les signaux à une destination OTLP |

Un composant doit être disponible dans la distribution du Collector utilisée. Les distributions Core, Contrib et certaines distributions commerciales n'incluent pas nécessairement les mêmes composants.

### 9.3 Ordre des processors

L'ordre des processors est important.

Exemple :

```text
Réception OTLP
      |
      v
Limitation mémoire
      |
      v
Filtrage des données sensibles
      |
      v
Echantillonnage éventuel
      |
      v
Regroupement
      |
      v
Export
```

L'ordre exact dépend du besoin et du comportement des processors.

Il faut notamment éviter de transmettre des données interdites au backend simplement parce que la suppression des champs sensibles se trouve après l'export.

### 9.4 Gestion de la mémoire

Un Collector peut recevoir un volume de télémétrie supérieur à sa capacité de traitement.

Sans contrôles appropriés, les files d'attente peuvent augmenter, la mémoire se saturer et le processus devenir instable.

Le dimensionnement doit prendre en compte :

- Le débit des spans.
- Le volume des attributs.
- Le nombre de services.
- Les délais d'export.
- Le taux de nouvelles tentatives.
- La capacité du backend.
- Les limites mémoire.
- La charge sur le réseau.

Le processor `memory_limiter` est utile, mais il ne remplace pas le dimensionnement ni la supervision de la chaîne de collecte.

## 10. Échantillonnage des traces

### 10.1 Pourquoi échantillonner ?

Un système très sollicité peut générer des millions de traces par jour.

Conserver toutes les traces peut augmenter les coûts de stockage, de transfert et de requête.

L'échantillonnage consiste à décider quelles traces seront conservées dans le système d'observabilité.

Il ne doit pas être appliqué sans évaluer les besoins de diagnostic, les exigences de sécurité, les contraintes d'audit et les objectifs de service.

### 10.2 Head sampling

Le *head sampling* prend une décision au début de la trace ou lors de la création des spans.

Exemple conceptuel :

```text
Requête entrante
      |
      v
Décision d'échantillonnage
      |
      +------> Conservée
      |
      +------> Rejetée
```

Avantages :

- Simple à comprendre.
- Décision prise tôt.
- Réduction du volume de données avant leur export.
- Moins de ressources nécessaires en aval.

Limite principale : la décision est prise avant de connaître le résultat final de la trace. Il peut donc être difficile de conserver systématiquement toutes les traces qui échoueront plus tard.

### 10.3 Tail sampling

Le *tail sampling* décide après avoir observé une partie importante ou l'ensemble disponible d'une trace.

Exemple :

```text
Trace créée
    |
    v
Spans collectés
    |
    v
Observation de la trace
    |
    +------> Erreur détectée ? ------> Conserver
    |
    +------> Durée excessive ? ------> Conserver
    |
    +------> Cas ordinaire ? --------> Echantillonner
```

Cette stratégie permet de sélectionner les traces selon leurs résultats, leur durée ou certains attributs.

Elle nécessite davantage de ressources et une conception adaptée à la distribution des traces entre collecteurs.

### 10.4 Exemple de politique

Une politique peut chercher à :

- Conserver toutes les traces contenant un statut d'erreur.
- Conserver les traces dont la durée dépasse un seuil.
- Conserver une proportion des traces ordinaires.
- Conserver davantage de traces pour certains services critiques.
- Adapter l'échantillonnage selon l'environnement.

Il faut déterminer la politique à partir des besoins réels, pas seulement du volume disponible.

### 10.5 Limite importante du tail sampling distribué

Si les spans d'une même trace sont répartis entre plusieurs collecteurs qui prennent leurs décisions indépendamment, la trace peut être incomplète.

Une architecture distribuée avec tail sampling doit s'assurer que les spans d'une même trace arrivent au composant qui détient l'état permettant la décision.

Un répartiteur réseau aléatoire ne garantit pas ce comportement. Il faut concevoir la répartition en tenant compte de l'identifiant de trace, des files, des délais d'attente et des ressources de mémoire.

### 10.6 Exemple de fragment de configuration

Le fragment ci-dessous montre le principe du tail sampling dans un Collector Contrib. Il doit être intégré à un pipeline complet et testé avec la version précise du composant.

```yaml
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 50000
    expected_new_traces_per_sec: 1000
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes:
            - ERROR

      - name: slow-traces
        type: latency
        latency:
          threshold_ms: 1000
```

Les valeurs sont illustratives et ne sont pas un dimensionnement de production.

Cette politique cherche à conserver les traces contenant des erreurs et celles qui dépassent le seuil de latence. Le reste du pipeline, notamment la configuration de la réception et de l'export, doit être défini séparément.

Les ressources nécessaires dépendent du débit, du nombre de spans par trace, du délai de décision et du nombre de traces simultanément conservées en mémoire.

## 11. Architecture de référence pour le laboratoire expert

Nous allons mettre en place une plateforme locale combinant :

- Prometheus pour les métriques.
- Node Exporter pour les métriques système Linux.
- OpenTelemetry Collector pour les traces.
- Tempo pour stocker les traces.
- Loki pour stocker les journaux.
- Grafana Alloy pour lire et transformer les journaux JSON.
- Grafana pour rechercher et corréler les données.
- Une application FastAPI instrumentée, produisant des traces et des journaux structurés.

### 11.1 Architecture

```text
                   APPLICATION FASTAPI
                     checkout-api
                          |
             +------------+------------+
             |                         |
             v                         v
       SDK OpenTelemetry          Logs JSON
             |                         |
             v                         v
      OTLP vers Collector        Fichier partagé
             |                         |
             v                         v
     OpenTelemetry Collector      Grafana Alloy
             |                         |
             v                         v
            Tempo                     Loki
             |                         |
             +------------+------------+
                          |
                          v
                        Grafana
                          ^
                          |
                     Prometheus
                          |
                          v
                     Node Exporter
```

Les traces sont transmises au Collector par OTLP. Le Collector les exporte vers Tempo.

Les journaux sont écrits dans un fichier JSON local au laboratoire. Alloy lit ce fichier, extrait les champs pertinents et envoie les entrées à Loki.

Les identifiants de trace et de span sont présents dans les journaux. Ils permettront de passer d'un log à une trace, sans imposer ces identifiants comme labels Loki à forte cardinalité.

## 12. Préparer le laboratoire

### 12.1 Prérequis

Installer Docker Engine et le plugin Docker Compose.

Vérifier les versions disponibles :

```bash
docker --version
docker compose version
```

Le laboratoire est surtout destiné à Linux. La collecte des métriques de l'hôte avec des montages comme `/proc`, `/sys` et `/` dépend de l'environnement Docker.

Sur Docker Desktop sous Windows ou macOS, Node Exporter peut observer la machine virtuelle ou l'environnement Linux sous-jacent plutôt que l'hôte attendu. Dans ce cas, utiliser un exportateur adapté au système réel ou réaliser le laboratoire de métriques sur une machine Linux.

### 12.2 Créer les répertoires

```bash
mkdir -p observability-expert/demo-app
mkdir -p observability-expert/grafana/provisioning/datasources
mkdir -p observability-expert/lab-logs

cd observability-expert
```

Nous allons créer les fichiers suivants :

```text
observability-expert/
|
+-- compose.yml
+-- prometheus.yml
+-- tempo.yml
+-- loki.yml
+-- otel-collector.yml
+-- alloy.alloy
|
+-- grafana/
|   |
|   +-- provisioning/
|       |
|       +-- datasources/
|           |
|           +-- datasources.yml
|
+-- demo-app/
|   |
|   +-- Dockerfile
|   +-- requirements.txt
|   +-- app.py
|
+-- lab-logs/
```

Les fichiers se trouvent à la racine du répertoire `observability-expert`, sauf ceux explicitement placés dans les sous-répertoires.

## 13. Créer le laboratoire Docker Compose

Créer `compose.yml` avec le contenu suivant :

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: obs-prometheus
    restart: unless-stopped
    ports:
      - "127.0.0.1:9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--storage.tsdb.retention.time=7d"
    volumes:
      - "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"
      - "prometheus-data:/prometheus"
    depends_on:
      - node-exporter

  node-exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: obs-node-exporter
    restart: unless-stopped
    pid: host
    command:
      - "--path.procfs=/host/proc"
      - "--path.sysfs=/host/sys"
      - "--path.rootfs=/host"
    volumes:
      - "/proc:/host/proc:ro"
      - "/sys:/host/sys:ro"
      - "/:/host:ro,rslave"
    expose:
      - "9100"

  tempo:
    image: grafana/tempo:latest
    container_name: obs-tempo
    restart: unless-stopped
    command:
      - "-config.file=/etc/tempo.yml"
    volumes:
      - "./tempo.yml:/etc/tempo.yml:ro"
      - "tempo-data:/var/tempo"
    expose:
      - "3200"
      - "4317"
      - "4318"

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    container_name: obs-otel-collector
    restart: unless-stopped
    command:
      - "--config=/etc/otelcol-contrib/config.yaml"
    volumes:
      - "./otel-collector.yml:/etc/otelcol-contrib/config.yaml:ro"
    expose:
      - "4317"
      - "4318"
    depends_on:
      - tempo

  loki:
    image: grafana/loki:latest
    container_name: obs-loki
    restart: unless-stopped
    command:
      - "-config.file=/etc/loki/local-config.yaml"
    volumes:
      - "./loki.yml:/etc/loki/local-config.yaml:ro"
      - "loki-data:/loki"
    expose:
      - "3100"

  alloy:
    image: grafana/alloy:latest
    container_name: obs-alloy
    restart: unless-stopped
    command:
      - "run"
      - "--server.http.listen-addr=0.0.0.0:12345"
      - "--storage.path=/var/lib/alloy/data"
      - "/etc/alloy/config.alloy"
    volumes:
      - "./alloy.alloy:/etc/alloy/config.alloy:ro"
      - "./lab-logs:/var/log/demo:ro"
      - "alloy-data:/var/lib/alloy/data"
    depends_on:
      - loki

  demo-app:
    build:
      context: ./demo-app
    container_name: obs-demo-app
    restart: unless-stopped
    environment:
      OTEL_COLLECTOR_ENDPOINT: "otel-collector:4317"
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - "./lab-logs:/var/log/demo"
    depends_on:
      - otel-collector

  grafana:
    image: grafana/grafana:latest
    container_name: obs-grafana
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      GF_USERS_ALLOW_SIGN_UP: "false"
    volumes:
      - "grafana-data:/var/lib/grafana"
      - "./grafana/provisioning/datasources/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml:ro"
    depends_on:
      - prometheus
      - tempo
      - loki

volumes:
  prometheus-data:
  tempo-data:
  loki-data:
  grafana-data:
  alloy-data:
```

### 13.1 Comprendre cette architecture

Les interfaces Web sont liées à `127.0.0.1` pour éviter de les publier directement sur toutes les interfaces réseau de l'hôte.

Tempo, Loki et le Collector communiquent sur le réseau interne Docker. Les endpoints de réception OTLP ne sont pas publiés directement sur l'hôte dans cet exemple.

L'application peut joindre le Collector grâce au nom de service `otel-collector`.

Alloy lit uniquement le répertoire de journaux du laboratoire, monté en lecture seule dans le conteneur.

Les volumes nommés permettent de conserver les données de Tempo, Loki, Prometheus, Grafana et Alloy au-delà du cycle de vie d'un conteneur.

Les balises d'image `latest` simplifient le premier lancement mais ne sont pas adaptées à une stratégie de versionnement stricte. Dans un environnement durable, verrouiller les versions, valider les mises à niveau et utiliser une procédure de restauration.

`depends_on` organise le démarrage des services, mais ne garantit pas automatiquement que tous les composants sont prêts à traiter des requêtes lorsque leurs dépendances démarrent.

## 14. Configurer Tempo

Créer `tempo.yml` :

```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

ingester:
  max_block_duration: 5m

compactor:
  compaction:
    block_retention: 24h

storage:
  trace:
    backend: local
    wal:
      path: /var/tempo/wal
    local:
      path: /var/tempo/blocks
```

### 14.1 Rôle des paramètres

Le port `3200` sert à l'interface HTTP et aux API de Tempo.

Le distributeur reçoit les traces via OTLP sur les endpoints gRPC ou HTTP indiqués.

L'ingester gère les traces reçues et leur préparation pour le stockage.

Le compactor réalise les opérations de compaction et de rétention associées à la configuration.

Le backend local est utilisé ici pour un laboratoire. Pour une plateforme de production, le stockage objet est généralement préférable pour répondre aux exigences d'échelle, de disponibilité et d'exploitation de Tempo.

### 14.2 Les limites de ce stockage local

Cette configuration ne fournit pas, à elle seule, une architecture hautement disponible.

Il faut notamment considérer :

- La disponibilité du disque.
- Les sauvegardes nécessaires.
- La perte de l'hôte.
- Le volume de traces.
- Les politiques de rétention.
- Les performances de requête.
- Les mécanismes de contrôle d'accès.

Une configuration de développement ne doit pas être interprétée comme une architecture de production validée.

## 15. Configurer Loki

Créer `loki.yml` :

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-04-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  allow_structured_metadata: true
```

### 15.1 Les labels Loki

Loki utilise des labels pour identifier les flux de journaux. Chaque combinaison distincte de labels peut créer un flux séparé.

Exemples de labels raisonnables :

```text
environment = lab
service_name = checkout-api
job = demo-app
level = error
```

Éviter d'utiliser systématiquement comme labels :

```text
trace_id
span_id
request_id
user_id
identifiant de transaction unique
URL contenant des identifiants arbitraires
```

Ces valeurs peuvent avoir énormément de valeurs distinctes. Il est préférable de conserver les identifiants uniques dans le message JSON, dans les champs extraits ou dans les métadonnées structurées lorsque la configuration le permet.

### 15.2 Sécurité de cette configuration

L'authentification est désactivée dans le fichier de laboratoire. Ce choix simplifie l'exercice et n'est acceptable que dans un environnement isolé, non exposé à des utilisateurs non fiables.

Une configuration de production doit définir le modèle d'authentification, l'autorisation, le TLS, le stockage et l'isolation des utilisateurs. Un proxy d'authentification ou une architecture multi-tenant adaptée peut être nécessaire selon la plateforme.

## 16. Configurer l'OpenTelemetry Collector

Créer `otel-collector.yml` :

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 256
    spike_limit_mib: 64

  batch:
    timeout: 5s
    send_batch_size: 512

exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers:
        - otlp
      processors:
        - memory_limiter
        - batch
      exporters:
        - otlp/tempo
```

### 16.1 Explication

Le receiver OTLP reçoit les données de l'application.

Le processor `memory_limiter` aide à maîtriser la pression mémoire.

Le processor `batch` regroupe les données avant leur transmission.

L'exporter OTLP transmet les traces vers le service Tempo.

Le champ `tls.insecure: true` est utilisé ici pour la communication en clair sur le réseau isolé du laboratoire. Il ne doit pas devenir une valeur par défaut dans un environnement où le trafic traverse des réseaux non fiables.

### 16.2 Pourquoi le Collector est-il utile ?

Sans Collector, chaque application devrait connaître directement le backend de stockage.

Avec un Collector, le chemin de transmission est séparé du code métier :

```text
APPLICATION
    |
    v
OpenTelemetry SDK
    |
    v
OTLP
    |
    v
Collector
    |
    v
Backend de traces
```

Cette architecture permet de modifier la politique d'export ou certains traitements sans changer nécessairement toutes les applications.

### 16.3 Évolution vers plusieurs pipelines

Un Collector peut comporter des pipelines pour les traces, les métriques et les journaux.

Exemple de structure conceptuelle :

```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/tempo]

    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]

    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [destination-logs]
```

Ce fragment est uniquement une illustration du modèle de pipeline. Les noms de composants doivent correspondre à ceux réellement disponibles dans la distribution du Collector et à une destination configurée et compatible.

Le laboratoire envoie les traces au Collector et les journaux vers Loki par l'intermédiaire d'Alloy.

## 17. Configurer Prometheus

Créer `prometheus.yml` :

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets:
          - "prometheus:9090"

  - job_name: "linux"
    static_configs:
      - targets:
          - "node-exporter:9100"
```

Cette configuration permet de collecter les métriques de Prometheus et celles exposées par Node Exporter.

Le comportement de Node Exporter dans un environnement Docker Desktop peut différer de celui d'une installation Linux native. Vérifier que les métriques observées correspondent bien à la machine que l'on souhaite surveiller.

Les traces, les logs et les métriques n'ont pas besoin de partager exactement le même pipeline, mais ils doivent utiliser des noms de service et des informations d'environnement cohérents afin de faciliter les corrélations.

## 18. Configurer Grafana

Créer `grafana/provisioning/datasources/datasources.yml` :

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    uid: loki
    type: loki
    access: proxy
    url: http://loki:3100

  - name: Tempo
    uid: tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
```

Grafana charge ainsi trois sources de données.

Prometheus est utilisé pour les métriques. Loki est utilisé pour les journaux. Tempo est utilisé pour les traces.

Les adresses utilisent les noms des services Docker, car Grafana contacte les composants depuis le réseau du projet.

## 19. Collecter les journaux avec Grafana Alloy

Créer `alloy.alloy` :

```alloy
loki.source.file "demo" {
  targets = [
    {
      "__path__" = "/var/log/demo/*.jsonl",
      "job" = "demo-app",
      "environment" = "lab",
    },
  ]

  forward_to = [loki.process.demo.receiver]

  file_match {
    enabled = true
    sync_period = "5s"
  }
}

loki.process "demo" {
  forward_to = [loki.write.local.receiver]

  stage.json {
    expressions = {
      level        = "level",
      service_name = "service_name",
      event        = "event",
      trace_id     = "trace_id",
      span_id      = "span_id",
    }
  }

  stage.labels {
    values = {
      level        = "level",
      service_name = "service_name",
    }
  }

  stage.structured_metadata {
    values = {
      trace_id = "trace_id",
      span_id  = "span_id",
    }
  }
}

loki.write "local" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

### 19.1 Que fait Alloy ?

Alloy recherche les fichiers JSON dans `/var/log/demo`.

Il transmet les lignes à une chaîne de traitement :

1. Analyse JSON.
2. Extraction de `level`, `service_name`, `event`, `trace_id` et `span_id`.
3. Ajout des labels à faible cardinalité `level` et `service_name`.
4. Ajout de `trace_id` et `span_id` comme métadonnées structurées.
5. Envoi des entrées vers Loki.

Les identifiants de corrélation ne deviennent pas des labels de flux. Cela réduit le risque d'explosion de cardinalité.

### 19.2 Pourquoi conserver les identifiants dans les métadonnées ?

Le trace ID est très utile pour retrouver une trace précise. Mais une nouvelle valeur peut être générée pour presque chaque requête.

Si chaque trace ID devenait un label Loki, le nombre de flux pourrait augmenter très rapidement.

En gardant cet identifiant dans le JSON ou les métadonnées structurées, il reste exploitable pour les recherches sans imposer la même cardinalité à l'index des labels.

## 20. Instrumenter une application Python

Nous allons créer une application FastAPI qui génère :

- Des traces automatiques pour les requêtes HTTP.
- Des spans enfants pour certaines opérations.
- Des journaux JSON.
- Des identifiants de trace et de span dans ces journaux.
- Une requête normale.
- Une requête lente.
- Une requête en erreur.

### 20.1 Fichier `demo-app/requirements.txt`

```text
fastapi
uvicorn[standard]
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-grpc
opentelemetry-instrumentation-fastapi
```

Ce fichier est adapté à un laboratoire pédagogique.

En production, fixer les versions des dépendances, conserver un fichier de verrouillage compatible avec le processus de livraison et vérifier les notes de version avant les mises à niveau.

### 20.2 Fichier `demo-app/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 20.3 Fichier `demo-app/app.py`

```python
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode


# ---------------------------------------------------------
# OpenTelemetry : configuration de la ressource et du tracer
# ---------------------------------------------------------

resource = Resource.create(
    {
        "service.name": "checkout-api",
        "service.version": "1.0.0",
        "deployment.environment.name": "lab",
    }
)

provider = TracerProvider(resource=resource)

collector_endpoint = os.getenv(
    "OTEL_COLLECTOR_ENDPOINT",
    "otel-collector:4317",
)

span_exporter = OTLPSpanExporter(
    endpoint=collector_endpoint,
    insecure=True,
)

provider.add_span_processor(
    BatchSpanProcessor(span_exporter)
)

trace.set_tracer_provider(provider)

tracer = trace.get_tracer("checkout-api")


# ---------------------------------------------------------
# Journaux JSON avec identifiants de trace et de span
# ---------------------------------------------------------

LOG_DIR = Path("/var/log/demo")
LOG_DIR.mkdir(parents=True, exist_ok=True)


class TraceContextFilter(logging.Filter):
    """Ajoute le contexte OpenTelemetry au journal actif."""

    def filter(self, record):
        context = trace.get_current_span().get_span_context()

        if context.is_valid:
            record.trace_id = f"{context.trace_id:032x}"
            record.span_id = f"{context.span_id:016x}"
        else:
            record.trace_id = None
            record.span_id = None

        return True


class JsonFormatter(logging.Formatter):
    """Produit un événement JSON lisible par Alloy et Loki."""

    def format(self, record):
        timestamp = datetime.fromtimestamp(
            record.created,
            tz=timezone.utc,
        ).isoformat().replace("+00:00", "Z")

        payload = {
            "timestamp": timestamp,
            "level": record.levelname.lower(),
            "service_name": "checkout-api",
            "logger": record.name,
            "message": record.getMessage(),
        }

        event_name = getattr(record, "event", None)
        trace_id = getattr(record, "trace_id", None)
        span_id = getattr(record, "span_id", None)

        if event_name:
            payload["event"] = event_name

        if trace_id:
            payload["trace_id"] = trace_id

        if span_id:
            payload["span_id"] = span_id

        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("checkout-api")
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.propagate = False

formatter = JsonFormatter()
context_filter = TraceContextFilter()

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.addFilter(context_filter)

file_handler = logging.FileHandler(
    LOG_DIR / "app.jsonl",
    encoding="utf-8",
)
file_handler.setFormatter(formatter)
file_handler.addFilter(context_filter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# ---------------------------------------------------------
# Application FastAPI
# ---------------------------------------------------------

app = FastAPI(title="Checkout API")

# Crée les spans des requêtes HTTP FastAPI.
FastAPIInstrumentor.instrument_app(app)


@app.get("/")
async def root():
    logger.info(
        "Requête principale traitée",
        extra={"event": "request_ok"},
    )

    return {
        "service": "checkout-api",
        "status": "ok",
    }


@app.get("/slow")
async def slow_request():
    with tracer.start_as_current_span("catalog.lookup") as span:
        span.set_attribute("catalog.operation", "lookup")
        span.set_attribute("catalog.result_count", 12)

        logger.info(
            "Début de recherche dans le catalogue",
            extra={"event": "catalog_lookup_started"},
        )

        await asyncio.sleep(1.2)

        logger.info(
            "Recherche dans le catalogue terminée",
            extra={"event": "catalog_lookup_completed"},
        )

    return {
        "status": "ok",
        "operation": "slow",
    }


@app.get("/error")
async def simulated_error():
    with tracer.start_as_current_span("payment.authorize") as span:
        span.set_attribute("payment.provider", "simulated")
        span.set_status(
            Status(
                StatusCode.ERROR,
                "simulated_downstream_failure",
            )
        )

        logger.error(
            "Echec simulé du fournisseur de paiement",
            extra={"event": "payment_authorization_failed"},
        )

        raise HTTPException(
            status_code=500,
            detail="Echec de paiement simulé",
        )
```

### 20.4 Ce que fait cette application

FastAPIInstrumentor crée des spans pour les requêtes HTTP.

L'application crée également un span interne pour l'opération `catalog.lookup` et un span pour `payment.authorize`.

Le processeur de spans regroupe les données et les transmet via OTLP au Collector.

Le filtre de journalisation lit le span actif et ajoute ses identifiants au log.

Les journaux sont écrits à la fois sur la sortie standard et dans un fichier partagé avec Alloy.

L'exemple d'erreur est volontaire. Il permet de vérifier qu'une trace avec un statut d'erreur arrive bien dans le backend de tracing.

Les traces ne sont pas garanties d'être conservées pendant toute la durée du processus : le résultat dépend de l'exporteur, du pipeline, du backend, de l'échantillonnage et de la configuration d'exploitation.

## 21. Démarrer le laboratoire

Depuis le répertoire `observability-expert`, vérifier d'abord la configuration Docker Compose :

```bash
docker compose config
```

Construire et démarrer les services :

```bash
docker compose up -d --build
```

Vérifier l'état général :

```bash
docker compose ps
```

Consulter les journaux du Collector :

```bash
docker compose logs --tail=100 otel-collector
```

Consulter les journaux Tempo :

```bash
docker compose logs --tail=100 tempo
```

Consulter les journaux Alloy :

```bash
docker compose logs --tail=100 alloy
```

Si les composants démarrent trop vite les uns par rapport aux autres, attendre leur état prêt avant de lancer les tests. `depends_on` organise le démarrage mais ne prouve pas que les dépendances acceptent déjà les requêtes.

## 22. Générer les premières traces

### 22.1 Appeler le service normal

```bash
curl http://localhost:8000/
```

Réponse attendue :

```json
{
  "service": "checkout-api",
  "status": "ok"
}
```

Une trace correspondant à la requête doit être exportée au travers du Collector vers Tempo.

### 22.2 Appeler le service lent

```bash
curl http://localhost:8000/slow
```

La réponse est retardée volontairement. Cette opération doit produire une trace contenant notamment un span enfant nommé `catalog.lookup`.

### 22.3 Appeler le service en erreur

```bash
curl -i http://localhost:8000/error
```

La route retourne un statut HTTP 500. La trace contient un span associé à `payment.authorize`, dont le statut est marqué en erreur.

### 22.4 Vérifier les journaux JSON

Depuis l'hôte Linux du laboratoire :

```bash
cat lab-logs/app.jsonl
```

Puis examiner uniquement les événements correspondant au paiement :

```bash
grep "payment_authorization_failed" lab-logs/app.jsonl
```

On doit retrouver des champs comparables à :

```json
{
  "timestamp": "2026-10-24T09:42:13.125Z",
  "level": "error",
  "service_name": "checkout-api",
  "logger": "checkout-api",
  "message": "Echec simulé du fournisseur de paiement",
  "event": "payment_authorization_failed",
  "trace_id": "identifiant-de-trace",
  "span_id": "identifiant-du-span"
}
```

Les identifiants exacts seront générés par OpenTelemetry.

S'il n'y a aucun identifiant dans un événement, vérifier si un span valide était actif au moment de la journalisation et si l'instrumentation entoure bien le traitement.

## 23. Explorer les traces dans Grafana Tempo

### 23.1 Ouvrir Grafana

Accéder à :

`http://localhost:3000`

La source de données Tempo doit être disponible grâce au fichier de provisionnement.

Ouvrir la section d'exploration de données, puis sélectionner Tempo comme source.

### 23.2 Rechercher les traces de l'application

Dans l'interface Explore de Tempo, utiliser la recherche de traces et les critères proposés.

Une requête TraceQL possible, si les attributs de ressource ont été correctement enregistrés, est :

```traceql
{ resource.service.name = "checkout-api" }
```

La syntaxe exacte peut dépendre des fonctions et de la version de Tempo utilisée. Si aucun résultat n'apparaît, vérifier la fenêtre temporelle, la source de données sélectionnée et les attributs réellement présents sur les traces.

### 23.3 Rechercher les traces en erreur

```traceql
{ status = error }
```

Cette requête permet de rechercher les traces contenant des spans dont le statut est `ERROR`, selon la sémantique TraceQL.

Les erreurs HTTP et les erreurs métier ne sont pas toujours équivalentes. Une application peut retourner un statut HTTP d'erreur sans que toutes les opérations métier soient en échec, ou inversement.

### 23.4 Rechercher les traces lentes

Exemple de filtre sur la durée :

```traceql
{ trace:duration > 1s }
```

Le filtre permet de rechercher les traces dont la durée dépasse le seuil indiqué.

Pour les mesures de durée, distinguer la durée totale de la trace et la durée d'un span interne. Un service peut avoir un span très lent dans une trace dont la durée totale reste acceptable, ou l'inverse en présence de plusieurs attentes et dépendances.

### 23.5 Explorer une trace

Lorsqu'une trace est ouverte, examiner :

- Le span racine.
- Les spans enfants.
- Les durées.
- Les statuts.
- Les attributs.
- Les événements.
- Les relations parent-enfant.
- Les spans qui ne semblent pas avoir été propagés correctement.

Une trace incomplète peut révéler une absence d'instrumentation ou une perte de contexte. Elle ne prouve pas nécessairement qu'un service n'a pas été exécuté.

## 24. Explorer les journaux dans Loki

### 24.1 Ouvrir Grafana Explore

Dans Grafana, ouvrir Explore et sélectionner Loki.

Pour lister les journaux du service :

```logql
{service_name="checkout-api"}
```

Pour sélectionner les journaux de niveau `error` :

```logql
{service_name="checkout-api", level="error"}
```

Ces requêtes supposent que les labels sont extraits et ajoutés comme défini dans `alloy.alloy`.

### 24.2 Rechercher une erreur de paiement

```logql
{service_name="checkout-api"} |= "payment_authorization_failed"
```

Le filtre `|=` recherche la chaîne dans la ligne de journal.

Pour analyser les champs JSON, on peut parser le message à la requête :

```logql
{service_name="checkout-api"} | json
```

Puis filtrer sur le champ `event` :

```logql
{service_name="checkout-api"}
  | json
  | event="payment_authorization_failed"
```

Le formatage sur plusieurs lignes est présenté uniquement pour faciliter la lecture. Dans l'interface Grafana, on peut saisir l'expression selon les conventions de l'éditeur.

### 24.3 Rechercher une trace à partir de son identifiant

Les journaux JSON contiennent le champ `trace_id`.

Exemple :

```logql
{service_name="checkout-api"}
  | json
  | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"
```

Remplacer le trace ID par celui d'un événement réellement observé.

Le parser JSON extrait le champ de la ligne pour le filtrage. L'identifiant ne doit pas nécessairement être un label Loki.

### 24.4 Pourquoi ne pas faire du trace ID un label ?

Un identifiant de trace est pratiquement unique pour chaque transaction. Si on le stocke comme label de flux, Loki peut devoir gérer un très grand nombre de flux distincts.

Il est préférable de conserver les identifiants à forte cardinalité comme données structurées ou champs extraits, puis de les utiliser lorsqu'une recherche précise est nécessaire.

Cette règle s'applique également aux identifiants de span, aux identifiants de requête et à de nombreux identifiants utilisateur.

## 25. Corréler les journaux et les traces dans Grafana

### 25.1 Objectif de la corrélation

L'objectif est de naviguer d'un événement de journal vers la trace correspondante, ou d'une trace vers les journaux associés.

```text
Journal d'erreur
      |
      | trace_id
      v
Trace distribuée
      |
      | span_id
      v
Opération concernée
      |
      v
Journaux et attributs complémentaires
```

Cette navigation réduit le besoin de copier manuellement des identifiants entre plusieurs interfaces.

### 25.2 Configurer le lien depuis Loki vers Tempo

Dans Grafana, ouvrir la configuration de la source Loki et chercher la section des champs dérivés, souvent nommée *Derived fields*.

Créer un champ dérivé :

- Nom : `TraceID`
- Type de correspondance : expression régulière
- Expression : `"trace_id"\s*:\s*"([a-f0-9]{32})"`
- Source de données cible : Tempo
- Champ utilisé comme valeur : le groupe capturé correspondant au trace ID

L'objectif est de détecter la valeur du champ dans le JSON et de proposer un lien vers la trace correspondante.

Selon la version de Grafana, l'interface des champs dérivés ou les options de lien peuvent varier. Vérifier le comportement du champ dérivé après sauvegarde et adapter l'expression aux lignes réellement enregistrées.

### 25.3 Corrélation depuis la trace vers les logs

La configuration de la source Tempo peut inclure un lien vers la source Loki.

Configurer la navigation vers les logs en utilisant :

- La source de données Loki.
- La fenêtre de temps autour du span.
- Le nom de service approprié.
- Le contexte ou l'identifiant de trace disponible.
- Les labels cohérents définis dans les logs.

Le résultat doit permettre d'examiner les journaux correspondant à la trace sélectionnée.

### 25.4 Si la corrélation ne fonctionne pas

Vérifier :

1. Que le trace ID se trouve réellement dans le journal.
2. Que les spans correspondants existent dans Tempo.
3. Que les horodatages utilisent une base cohérente.
4. Que le champ dérivé capture la bonne valeur.
5. Que la source de données cible possède le bon identifiant.
6. Que le temps de rétention couvre les données.
7. Que les expressions de recherche utilisent les labels présents.
8. Que les filtres de temps n'excluent pas la trace recherchée.

La présence d'un trace ID dans un journal ne garantit pas que la trace soit conservée. L'échantillonnage, une perte de données ou un échec d'export peuvent laisser les journaux disponibles sans la trace associée.

## 26. La corrélation avec les métriques

### 26.1 Pourquoi la corrélation est-elle importante ?

Les métriques indiquent souvent quand un service est en difficulté. Les traces permettent ensuite de comprendre quelles opérations expliquent la dégradation.

Exemple :

```text
08:00  Taux d'erreur normal
08:05  Latence p95 en hausse
08:06  CPU stable
08:07  Span payment.authorize très lent
08:08  Journaux du fournisseur signalant des délais
```

Cette chronologie suggère que le service de paiement pourrait être un facteur important.

Cependant, la proximité temporelle ne prouve pas la causalité. Il faut examiner les détails, les dépendances et les données de plusieurs requêtes.

### 26.2 Prometheus et Tempo

Tempo peut générer des métriques à partir des spans, par exemple des métriques RED :

- Rate : débit de requêtes.
- Errors : taux d'erreur.
- Duration : durée des opérations.

Les métriques générées peuvent être envoyées vers un backend Prometheus-compatible.

Elles permettent de construire des tableaux de bord et des alertes à partir des données de tracing.

Il faut toutefois tenir compte de l'échantillonnage. Si la génération de métriques est effectuée après l'échantillonnage, les statistiques décrivent l'échantillon retenu plutôt que nécessairement l'ensemble du trafic.

### 26.3 Exemplars

Les exemplars permettent d'associer une observation de métrique à un identifiant de trace.

Lorsqu'ils sont activés et correctement pris en charge dans la chaîne de collecte, il devient possible de sélectionner une période ou une valeur dans un graphique et de naviguer vers une trace représentative.

```text
Graphique de latence
        |
        v
Observation associée à un exemplar
        |
        v
Trace ID
        |
        v
Trace dans Tempo
        |
        v
Spans lents ou en erreur
```

Cette approche est particulièrement utile lorsqu'un graphique révèle une anomalie mais ne permet pas de déterminer quelle requête en est à l'origine.

La configuration exacte dépend de l'instrumentation, du backend de métriques, de l'exporteur et de Grafana.

## 27. Concevoir une stratégie d'instrumentation

### 27.1 Instrumentation automatique

L'instrumentation automatique ajoute la collecte à certaines bibliothèques ou frameworks sans devoir modifier manuellement chaque fonction métier.

Exemples :

- Framework HTTP.
- Client HTTP.
- Couche de persistance.
- Client de messagerie.
- Bibliothèque de base de données.

Avantages :

- Mise en place rapide.
- Couverture uniforme des opérations prises en charge.
- Moins de code spécifique à l'observabilité.

Limites :

- Les opérations métier peuvent rester opaques.
- Les versions de bibliothèques peuvent être incompatibles.
- Les attributs collectés peuvent demander un filtrage.
- Certaines opérations asynchrones peuvent nécessiter une instrumentation supplémentaire.

### 27.2 Instrumentation manuelle

L'instrumentation manuelle ajoute des spans et des attributs métier directement dans le code.

Exemple conceptuel en Python :

```python
from opentelemetry import trace

tracer = trace.get_tracer("checkout-api")

def process_order(order_id):
    with tracer.start_as_current_span("order.process") as span:
        span.set_attribute("order.operation", "process")
        span.set_attribute("order.priority", "standard")

        # Logique métier à exécuter.
        result = do_business_operation(order_id)

        return result
```

Cet exemple illustre la création du span et l'ajout d'attributs. Il suppose que `do_business_operation` est défini dans l'application.

L'instrumentation manuelle est utile lorsqu'on veut comprendre une opération métier, mais elle doit rester cohérente et éviter de surcharger les traces avec des attributs inutiles.

### 27.3 Combiner les deux

Une stratégie efficace utilise souvent :

- L'instrumentation automatique pour les interactions HTTP et la base de données.
- L'instrumentation manuelle pour les opérations métier importantes.
- Les journaux structurés pour les événements détaillés.
- Les métriques pour les tendances et les indicateurs d'exploitation.

L'objectif n'est pas de créer un span pour chaque instruction, mais de décrire les opérations nécessaires au diagnostic.

## 28. Bonnes pratiques pour les attributs et les conventions sémantiques

### 28.1 Utiliser des attributs cohérents

Les attributs doivent être compréhensibles et cohérents entre les services.

Exemple :

```text
service.name = checkout-api
service.version = 1.0.0
deployment.environment.name = production
http.request.method = POST
http.response.status_code = 500
```

Les conventions sémantiques sont publiées par OpenTelemetry et peuvent évoluer. Il faut les vérifier pour les bibliothèques et versions employées.

### 28.2 Éviter les attributs inutiles

Un attribut doit aider à comprendre une opération, à filtrer une recherche ou à établir une relation utile.

Éviter les attributs dont la valeur :

- Est identique pour tous les spans.
- N'a aucun usage opérationnel.
- Contient des données sensibles.
- Crée une quantité de valeurs uniques très élevée.
- Duplique inutilement des informations déjà fournies par la ressource.

### 28.3 Attributs de ressource

Les attributs de ressource décrivent le producteur de télémétrie plutôt que chaque opération individuelle.

Exemples :

```text
service.name
service.version
deployment.environment.name
host.name
```

Un nom de service cohérent est essentiel pour regrouper les traces provenant de plusieurs instances d'une même application.

Il est préférable de définir ces attributs au niveau de la ressource et d'éviter de les recopier manuellement dans chaque span.

## 29. Structurer les journaux pour une exploitation experte

### 29.1 Pourquoi préférer le JSON ?

Un journal en texte libre est facile à produire, mais moins facile à filtrer lorsqu'il ne possède pas de structure stable.

Format libre :

```text
Echec du paiement pour la requête 12345.
```

Format structuré :

```json
{
  "timestamp": "2026-10-24T10:15:00Z",
  "level": "error",
  "service_name": "checkout-api",
  "event": "payment_authorization_failed",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7"
}
```

Le format structuré facilite le filtrage, l'agrégation et la corrélation.

Il ne faut toutefois pas faire dépendre toute la logique de recherche d'un message descriptif susceptible de changer à chaque modification de l'application.

### 29.2 Champs recommandés

Selon le besoin et la convention retenue, un journal peut contenir :

| Champ | Utilité |
|---|---|
| `timestamp` | Moment de l'événement |
| `level` | Gravité |
| `service_name` | Service producteur |
| `event` | Nom stable de l'événement |
| `message` | Message lisible |
| `trace_id` | Identifiant de trace |
| `span_id` | Identifiant du span |
| `request_id` | Identifiant d'une requête si nécessaire |
| `environment` | Environnement concerné |

Éviter d'enregistrer des mots de passe, des jetons complets et des données personnelles qui ne sont pas nécessaires au diagnostic.

### 29.3 Stabilité des événements

Préférer un champ `event` stable :

```json
{
  "event": "payment_authorization_failed",
  "message": "Le fournisseur de paiement ne répond pas"
}
```

Le message peut évoluer, tandis que le nom de l'événement reste stable pour les requêtes et les alertes.

Cette séparation facilite l'évolution de l'application et la maintenance des tableaux de bord.

## 30. Rechercher et analyser avec LogQL

LogQL est le langage de requête utilisé par Loki.

### 30.1 Sélectionner un flux

```logql
{service_name="checkout-api"}
```

Cette expression sélectionne les journaux possédant le label `service_name` égal à `checkout-api`.

### 30.2 Filtrer du texte

```logql
{service_name="checkout-api"} |= "Echec"
```

L'opérateur `|=` garde les lignes qui contiennent le texte recherché.

L'opérateur `!=` peut être utilisé pour exclure certaines lignes, tandis que les opérateurs correspondant aux expressions régulières permettent des filtres plus flexibles.

### 30.3 Parser le JSON

```logql
{service_name="checkout-api"} | json
```

Cette expression extrait les propriétés JSON de chaque ligne pour permettre des filtres et des transformations à l'étape de requête.

Exemple :

```logql
{service_name="checkout-api"}
  | json
  | level="error"
```

### 30.4 Rechercher un identifiant de trace

```logql
{service_name="checkout-api"}
  | json
  | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"
```

Utiliser le trace ID qui apparaît dans les journaux de l'application.

Cette requête peut être utile lors d'une enquête, mais il ne faut pas créer un label de flux permanent pour chaque identifiant unique.

### 30.5 Filtrer par durée si elle est enregistrée

Si une application journalise une durée numérique dans le champ `duration_ms`, le filtre peut porter sur le champ parsé :

```logql
{service_name="checkout-api"}
  | json
  | duration_ms > 1000
```

La présence de ce champ dépend du schéma de journal choisi.

Un champ de durée dans un log n'est pas automatiquement une métrique temporelle. Pour des analyses de tendance, une métrique d'histogramme appropriée reste souvent plus adaptée.

## 31. Rechercher et analyser avec TraceQL

TraceQL est le langage de requête associé à Tempo.

### 31.1 Rechercher les erreurs

```traceql
{ status = error }
```

### 31.2 Rechercher un service

```traceql
{ resource.service.name = "checkout-api" }
```

Les attributs disponibles dépendent de l'instrumentation et du contenu réellement stocké dans Tempo.

### 31.3 Rechercher les opérations HTTP lentes

Exemple conceptuel :

```traceql
{
  span.http.request.method = "POST" &&
  duration > 500ms
}
```

Les noms d'attributs doivent être adaptés à la version des conventions sémantiques utilisées par l'instrumentation. Une application utilisant un nom d'attribut différent nécessite une requête correspondante.

### 31.4 Rechercher une erreur HTTP

```traceql
{ span.http.response.status_code >= 500 }
```

Cette recherche est valable si l'attribut de statut HTTP est présent sur les spans concernés.

Pour les recherches complexes, vérifier la grammaire TraceQL de la version installée. Les champs disponibles ne sont pas toujours présents sur tous les spans.

### 31.5 Pourquoi une requête TraceQL peut-elle ne rien renvoyer ?

Causes fréquentes :

- La fenêtre temporelle est trop courte.
- Aucune trace ne correspond.
- Le service n'est pas instrumenté.
- Les traces ne parviennent pas au backend.
- L'échantillonnage a supprimé les données recherchées.
- L'attribut ou son nom est incorrect.
- La trace a expiré selon la rétention.

Commencer par rechercher les traces récentes et vérifier les noms réels des attributs avant de complexifier l'expression.

## 32. Concevoir la corrélation d'un incident

### 32.1 Scénario : latence élevée et erreur applicative

Une équipe remarque que la latence du service de commande augmente et que plusieurs requêtes échouent.

La méthode d'analyse doit combiner les trois signaux.

```text
ALERTE DE LATENCE
       |
       v
METRIQUES
  Le taux d'erreur augmente
  La durée p95 augmente
       |
       v
TRACES
  payment.authorize est lent
       |
       v
JOURNAUX
  fournisseur externe en délai dépassé
       |
       v
HYPOTHESE
  La dépendance externe ralentit
       |
       v
VERIFICATION
  Comparaison de plusieurs traces
  et examen des logs du client HTTP
       |
       v
ACTION
  Mesure corrective et validation
```

Cette chronologie fournit une hypothèse à tester. Elle ne constitue pas une preuve suffisante tant que les dépendances, les données et l'impact ne sont pas vérifiés.

### 32.2 Questions à poser pendant le diagnostic

- Le problème touche-t-il toutes les requêtes ou seulement certaines routes ?
- L'erreur concerne-t-elle une seule instance ?
- Les autres services présentent-ils la même dégradation ?
- Quel span consomme la majorité de la durée ?
- La latence est-elle due à un calcul, une attente réseau ou une base de données ?
- Les journaux confirment-ils la même chronologie ?
- Les traces sont-elles complètes ?
- Une modification récente peut-elle expliquer le changement ?
- Le problème disparaît-il lorsqu'une dépendance revient à la normale ?

### 32.3 Distinguer la cause et la corrélation

Deux événements peuvent se produire au même moment sans que l'un soit la cause de l'autre.

Pour établir une cause probable, collecter des preuves :

- Chronologie.
- Comparaison de plusieurs requêtes.
- Spans concernés.
- Journaux du service dépendant.
- Métriques avant et pendant l'incident.
- Résultats des tests ciblés.
- Effets d'une mesure corrective contrôlée.

Le but est de réduire progressivement les hypothèses jusqu'à obtenir une explication suffisamment étayée.

## 33. Sécurité et confidentialité de l'observabilité

### 33.1 Pourquoi ces données sont sensibles

Les traces et journaux peuvent contenir des informations sur :

- Les endpoints internes.
- Les versions des logiciels.
- Les noms des systèmes.
- Les dépendances externes.
- Les opérations métier.
- Les clients et leurs identifiants.
- Les erreurs et faiblesses techniques.
- Les données de requête.
- Les informations d'authentification si elles sont mal journalisées.

Les systèmes d'observabilité doivent être traités comme des composants sensibles de l'infrastructure.

### 33.2 Réduire les données collectées

Avant de créer un attribut ou un journal, se demander :

1. Quelle question opérationnelle doit-il aider à résoudre ?
2. Qui a besoin de cette donnée ?
3. Peut-elle identifier une personne ?
4. Contient-elle un secret ?
5. Peut-on la remplacer par une catégorie moins sensible ?
6. Combien de temps faut-il la conserver ?
7. Quels composants la recevront ?

Il est souvent préférable d'enregistrer un code d'erreur et un identifiant de corrélation plutôt qu'un contenu complet de requête.

### 33.3 Masquage et suppression

Les données sensibles peuvent être supprimées ou transformées à différents niveaux :

- Dans l'application avant l'émission du log.
- Dans les processeurs de l'OpenTelemetry Collector.
- Dans les étapes de traitement des logs d'Alloy.
- Dans les règles de collecte.
- Dans certains mécanismes d'accès et d'export.

La suppression côté source reste particulièrement importante. Si une donnée est interdite au stockage, il est préférable de ne pas l'émettre.

### 33.4 Baggage et propagation des en-têtes

Ne jamais accepter aveuglément que tout contenu d'en-tête fourni par une requête externe soit transmis à toutes les dépendances.

Le baggage et certains champs de contexte peuvent traverser des frontières de confiance.

Une politique d'instrumentation doit définir les valeurs autorisées, leur validation, leur durée de vie et les endroits où elles peuvent être propagées.

### 33.5 Contrôle d'accès

Prévoir :

- Des comptes nominatifs.
- Une authentification adaptée au niveau de risque.
- Une séparation des rôles.
- Des restrictions réseau.
- Le chiffrement des communications nécessaires.
- Un contrôle de l'export des données.
- Des audits des actions sensibles.
- Une politique de conservation.
- Une procédure de révocation des accès.

L'interface Grafana n'est pas la seule surface à protéger. Les endpoints du Collector, les exportateurs, les API de stockage, les interfaces de santé et les fichiers de configuration doivent également être contrôlés.

## 34. Rétention, volume et coût

### 34.1 Les traces sont-elles toutes nécessaires ?

La valeur d'une trace dépend de ce que l'équipe cherche à observer.

Les traces détaillées aident au diagnostic, mais leur stockage peut devenir coûteux à grande échelle.

Il faut équilibrer :

- La quantité de données conservées.
- La probabilité d'observer les problèmes rares.
- La durée de conservation.
- Le niveau de détail des spans.
- La cardinalité des attributs.
- Le coût de stockage.
- Le besoin d'analyse rétrospective.

L'échantillonnage ne doit pas masquer les incidents rares que l'équipe doit absolument pouvoir enquêter.

### 34.2 Les journaux ont aussi un coût

Le coût des journaux dépend notamment :

- Du nombre d'événements.
- De la taille moyenne des lignes.
- De la fréquence des erreurs.
- De la duplication des messages.
- De la durée de conservation.
- Des métadonnées attachées.
- Du mode de stockage et de compression.

Une erreur répétée des milliers de fois par seconde peut saturer le pipeline et masquer d'autres événements importants.

### 34.3 Réduire le volume sans perdre l'information utile

Actions possibles :

- Éliminer les journaux redondants.
- Réduire les messages répétitifs.
- Normaliser les événements.
- Corriger les niveaux de gravité incorrects.
- Supprimer les champs inutiles.
- Appliquer une rétention adaptée.
- Échantillonner les traces ordinaires.
- Conserver les traces en erreur selon une politique réfléchie.
- Surveiller la consommation et la cardinalité.

La réduction de volume doit être évaluée à partir des besoins de diagnostic et des obligations de conservation.

## 35. Fiabilité des pipelines de télémétrie

### 35.1 Une donnée peut être perdue entre deux composants

Les étapes d'une pipeline peuvent échouer indépendamment.

```text
Application
    |
    v
SDK
    |
    v
Collector
    |
    v
Réseau
    |
    v
Backend
    |
    v
Stockage
    |
    v
Exploration Grafana
```

L'absence de données dans Grafana ne prouve pas nécessairement que l'application n'a rien émis.

La défaillance peut se trouver à n'importe quelle étape.

### 35.2 Points à contrôler

- L'instrumentation crée-t-elle les spans ?
- Le SDK exporte-t-il les données ?
- Le Collector reçoit-il les requêtes ?
- Les processeurs acceptent-ils les données ?
- L'exporteur réussit-il la transmission ?
- Le backend accepte-t-il les données ?
- Les données sont-elles conservées ?
- La requête d'exploration est-elle correcte ?
- La période temporelle correspond-elle aux données ?

### 35.3 Files et nouvelles tentatives

Une configuration de production doit examiner les files d'export, les délais, les nouvelles tentatives et la politique en cas d'indisponibilité prolongée du backend.

Une file d'attente ne garantit pas une livraison permanente. Elle utilise des ressources et possède des limites.

Si le backend est indisponible trop longtemps, des données peuvent être perdues. Il faut dimensionner les files, superviser les erreurs d'export et connaître les limites de durabilité de chaque composant.

### 35.4 Superviser le Collector

Le Collector doit être surveillé à l'aide de métriques, de journaux et éventuellement de traces.

Indicateurs pertinents :

- Données reçues et exportées.
- Erreurs d'export.
- Nombre de données rejetées.
- Utilisation mémoire.
- Pression sur les files.
- Temps de traitement.
- Délais d'envoi.
- Disponibilité des endpoints.

Les noms exacts des métriques dépendent de la version et de la configuration du Collector.

## 36. Haute disponibilité et mise à l'échelle

### 36.1 Le laboratoire n'est pas hautement disponible

Le laboratoire utilise un seul conteneur pour la plupart des composants.

La perte de l'hôte ou du stockage peut arrêter toute la plateforme. Les données locales ne constituent pas une stratégie de sauvegarde complète.

Cette architecture est adaptée à l'apprentissage et non à une exigence de continuité élevée.

### 36.2 Éléments d'une architecture de production

Une conception de production doit étudier :

- La répartition de la charge.
- La disponibilité des collecteurs.
- La gestion de la collecte sous forte charge.
- Le stockage durable.
- La politique de rétention.
- La séparation des environnements.
- Les mécanismes d'accès.
- La résilience du backend.
- La surveillance de la chaîne elle-même.
- La restauration des configurations.
- Les limites de débit et de cardinalité.

Tempo propose plusieurs modes de déploiement. Le stockage objet est adapté à de nombreux scénarios de production, contrairement au stockage local de ce laboratoire.

### 36.3 Agent et gateway

Une architecture peut combiner un agent proche de la source et une gateway centrale.

```text
Application
    |
    v
Collector / Agent local
    |
    v
Gateway de collecte
    |
    v
Backend de télémétrie
```

L'agent local réduit les dépendances directes de chaque application envers le backend central. La gateway applique des politiques communes et facilite l'export.

Cette architecture demande de gérer les mises à jour, la capacité, l'authentification, les files et les relations entre les collecteurs.

## 37. Méthodologie de diagnostic expert

### 37.1 Incident : la latence p95 augmente

Première phase : confirmer que l'indicateur est correct et que les données sont présentes.

Deuxième phase : segmenter les résultats par service, route, version ou environnement lorsque ces dimensions sont disponibles.

Troisième phase : examiner les traces lentes.

Quatrième phase : rechercher le span qui domine la durée.

Cinquième phase : retrouver les événements associés dans les journaux.

Sixième phase : comparer les métriques système et celles des dépendances.

Septième phase : tester une hypothèse puis valider la correction.

### 37.2 Incident : la trace manque

Vérifier :

- La période de recherche.
- Le backend sélectionné.
- L'échantillonnage.
- L'instrumentation.
- La propagation du contexte.
- L'état de l'exporteur.
- Le pipeline du Collector.
- Les erreurs de stockage.

Les traces peuvent manquer parce qu'elles n'ont pas été exportées, parce qu'elles ont été échantillonnées ou parce qu'elles ont expiré. Il faut distinguer ces possibilités.

### 37.3 Incident : journal présent, trace absente

Causes plausibles :

- L'application écrit le log mais le span n'est pas actif.
- Le contexte n'est pas propagé.
- L'échantillonnage n'a pas conservé la trace.
- L'export a échoué.
- La trace est stockée dans un autre backend.
- La rétention de Tempo est plus courte que celle de Loki.

Le log doit être conservé avec suffisamment de contexte pour que l'équipe puisse enquêter, mais il ne faut pas inventer un identifiant de trace lorsqu'aucun contexte valide n'existe.

### 37.4 Incident : trace présente, journal absent

Causes plausibles :

- Le service n'a pas émis de journal.
- Le niveau de journalisation a filtré l'événement.
- Le fichier n'a pas été collecté.
- Alloy n'a pas accès au fichier.
- Loki a rejeté l'entrée.
- Une règle de traitement a supprimé le champ ou la ligne.
- Le log et la trace ne partagent pas le même identifiant.

Comparer les horodatages et vérifier le pipeline de collecte avant de conclure que l'application n'a rien journalisé.

## 38. Travaux pratiques

### TP 1 — Reconstituer une transaction

Objectif : retrouver le parcours d'une requête depuis sa trace.

Étapes :

1. Appeler la route `/`.
2. Appeler la route `/slow`.
3. Appeler la route `/error`.
4. Rechercher les traces de `checkout-api`.
5. Examiner le span racine.
6. Identifier les spans enfants.
7. Comparer les durées.
8. Rechercher le span `payment.authorize`.
9. Identifier le statut d'erreur.
10. Documenter le résultat.

Livrable : une fiche présentant le trace ID, les spans, leurs durées et la cause simulée.

### TP 2 — Retrouver une trace depuis les journaux

Objectif : comprendre la corrélation entre Loki et Tempo.

Étapes :

1. Rechercher les journaux de niveau `error`.
2. Identifier le champ `trace_id`.
3. Copier la valeur du trace ID.
4. Interroger Loki avec ce champ.
5. Rechercher la même trace dans Tempo.
6. Comparer les événements et spans.
7. Configurer un champ dérivé pour faciliter la navigation.
8. Vérifier le lien de navigation.

Livrable : une preuve montrant qu'un événement de log peut conduire à la trace correspondante.

### TP 3 — Détecter une dégradation

Objectif : identifier l'opération responsable d'une augmentation de latence.

Étapes :

1. Générer plusieurs requêtes `/`.
2. Générer plusieurs requêtes `/slow`.
3. Observer les durées dans Tempo.
4. Comparer les spans internes.
5. Vérifier les métriques système.
6. Examiner les journaux autour de la même période.
7. Expliquer la différence de comportement.

Livrable : un rapport précisant la durée de chaque type de requête et l'opération responsable du délai artificiel.

### TP 4 — Étudier une erreur distribuée

Objectif : analyser une trace en erreur.

Étapes :

1. Appeler `/error`.
2. Récupérer le trace ID depuis le log.
3. Rechercher la trace.
4. Identifier le span en erreur.
5. Examiner le statut et les attributs.
6. Rechercher les journaux associés.
7. Reconstituer la chronologie.
8. Distinguer le symptôme de la cause simulée.

Livrable : une chronologie de l'incident et une hypothèse expliquée.

### TP 5 — Définir une politique d'échantillonnage

Objectif : proposer une politique adaptée à une application à fort trafic.

Définir :

- Les traces qui doivent toujours être conservées.
- Les traces ordinaires qui peuvent être échantillonnées.
- Le seuil de durée retenu.
- Le comportement en cas de perte du contexte.
- Les conséquences du volume sur le stockage.
- Les moyens de vérifier que les erreurs importantes sont encore visibles.

Livrable : une politique argumentée, précisant ses limites.

### TP 6 — Réduire la cardinalité

Objectif : identifier les attributs pouvant créer trop de séries ou de flux.

Étudier les champs suivants :

```text
service_name
environment
trace_id
span_id
request_id
http.route
http.status_code
user_id
```

Pour chaque champ, décider s'il convient plutôt à :

- Un label de métrique.
- Un label Loki.
- Un attribut de span.
- Une métadonnée structurée.
- Un champ de journal.
- Une donnée à supprimer.

Livrable : une matrice expliquant le choix et ses conséquences sur la recherche et la capacité.

## 39. Exercices corrigés

### Exercice 1 — Identifier le composant lent

Une trace présente les durées suivantes :

```text
POST /orders                1 500 ms
inventory.check               100 ms
payment.authorize            1 100 ms
database.insert_order         120 ms
```

Question : quelle opération doit être examinée en premier ?

**Correction :**

`payment.authorize` constitue la première piste, car sa durée est importante par rapport aux autres spans. Il faut rechercher les détails de l'appel, les événements et les journaux correspondants avant d'affirmer qu'il est la cause unique de la latence.

La durée des spans enfants n'est pas nécessairement additive si les opérations se chevauchent.

### Exercice 2 — Trace ID différent sur deux services

Le service A possède le trace ID `AAA...`, tandis que le service B possède le trace ID `BBB...` pour ce que l'équipe pense être la même requête.

Citer plusieurs causes possibles.

**Correction :**

- Le contexte de trace n'a pas été transmis.
- Le service B a créé une trace indépendante.
- Un proxy a supprimé ou remplacé les en-têtes.
- L'instrumentation du client HTTP est absente.
- La requête est passée par un composant non instrumenté.
- Les deux logs correspondent à des requêtes différentes.

Il faut vérifier les identifiants complets, les en-têtes propagés et les horodatages avant de conclure.

### Exercice 3 — Log présent, trace absente

Un log contient un trace ID mais Tempo ne renvoie aucun résultat.

**Correction :**

Vérifier l'export, l'échantillonnage, la fenêtre de temps, le backend, la rétention et l'état du Collector. Il est possible que le log ait été conservé mais que la trace n'ait jamais été exportée ou qu'elle ait été rejetée par une politique d'échantillonnage.

### Exercice 4 — Cardinalité Loki

Un ingénieur ajoute `trace_id` comme label Loki.

Quels problèmes peut-il rencontrer ?

**Correction :**

Le nombre de flux peut augmenter fortement, car chaque trace peut introduire une nouvelle valeur de label. Cela peut accroître les coûts de stockage, dégrader les performances et compliquer l'exploitation.

Conserver le trace ID comme donnée structurée ou champ extrait est généralement plus approprié.

### Exercice 5 — Head sampling ou tail sampling ?

Une organisation veut conserver toutes les traces en erreur et seulement une partie des requêtes ordinaires.

Quelle approche peut répondre au besoin ?

**Correction :**

Le tail sampling peut appliquer une décision à partir du contenu observé de la trace, notamment son statut ou sa durée. Il doit être dimensionné et configuré pour recevoir les spans nécessaires à la décision.

Le head sampling prend sa décision tôt et ne peut pas garantir à lui seul la conservation de toutes les traces qui échoueront plus tard.

### Exercice 6 — Problème de propagation HTTP

Une API appelle un autre service, mais la trace s'interrompt au niveau de l'API.

Que vérifier ?

**Correction :**

Vérifier l'instrumentation du client HTTP, les en-têtes W3C Trace Context, les règles du proxy, la réception du contexte par le service distant et les configurations des SDK. Vérifier aussi que les traces du service appelé atteignent le même backend.

### Exercice 7 — Une métrique indique une forte latence, mais aucun span lent n'existe

Donner plusieurs explications possibles.

**Correction :**

Le tracing peut être incomplet, les traces lentes peuvent être échantillonnées, l'application peut ne pas instrumenter le composant responsable ou la métrique peut mesurer une partie du chemin qui n'est pas couverte par les spans. La fenêtre temporelle ou les labels peuvent aussi être incorrects.

Il faut comparer le périmètre des métriques et celui des traces avant de conclure.

### Exercice 8 — Données sensibles

Une application ajoute le jeton d'authentification complet aux attributs des spans pour faciliter le diagnostic.

Quelle est la bonne décision ?

**Correction :**

Ne pas enregistrer le jeton. Il faut supprimer ou masquer cette valeur et vérifier si elle a déjà été transmise à des backends ou à des exports. Les traces doivent contenir des informations utiles sans exposer les secrets.

### Exercice 9 — Choisir un signal

L'équipe veut savoir combien de requêtes échouent par minute, retrouver une requête en erreur et comprendre quelle dépendance a ralenti cette requête.

Quel signal utiliser pour chaque question ?

**Correction :**

- Nombre d'erreurs par minute : métriques.
- Événement détaillé : journaux.
- Parcours et durée par dépendance : traces.

La corrélation entre ces signaux permet une enquête plus efficace.

### Exercice 10 — Collector en surcharge

Le Collector reçoit plus de spans qu'il ne peut en exporter.

Que faut-il examiner ?

**Correction :**

Examiner le débit reçu, le débit exporté, les erreurs, les délais, les files, l'utilisation mémoire et la capacité du backend. Il faut ensuite agir sur la capacité, les ressources, les processeurs et éventuellement l'échantillonnage en fonction des exigences de conservation.

Une réduction aveugle des données peut masquer des incidents importants.

## 40. Projet de fin de niveau expert

### Concevoir une plateforme d'observabilité distribuée

L'apprenant doit réaliser une solution permettant de surveiller une application composée d'au moins trois composants logiques.

Exemple :

```text
Reverse proxy
     |
     v
API principale
     |
     +------> Service de catalogue
     |
     +------> Service de paiement
```

Les trois services peuvent être déployés sur des machines ou des conteneurs selon les moyens disponibles. L'essentiel est de démontrer la propagation et la corrélation du contexte.

### Livrable A — Architecture

Documenter :

- Les services.
- Les interactions.
- Les flux OTLP.
- Les collecteurs.
- Les backends.
- La rétention.
- Les contrôles d'accès.
- Les points de défaillance.

### Livrable B — Instrumentation

Démontrer :

- Les spans HTTP.
- Les spans enfants.
- Les attributs de ressource.
- Les statuts d'erreur.
- La propagation du contexte.
- Les identifiants de corrélation.

### Livrable C — Journaux structurés

Fournir :

- Le format JSON.
- Les champs obligatoires.
- Les champs de corrélation.
- Les règles de masquage.
- Les labels Loki.
- La stratégie évitant la cardinalité excessive.

### Livrable D — Corrélation

Démontrer le parcours suivant :

```text
Alerte ou métrique
       |
       v
Identification du service concerné
       |
       v
Trace lente ou en erreur
       |
       v
Span identifié
       |
       v
Journaux correspondants
       |
       v
Diagnostic et validation
```

### Livrable E — Fiabilité

Documenter :

- L'échantillonnage.
- La gestion des erreurs d'export.
- Les limites de stockage.
- Les alertes de pipeline.
- Les procédures de restauration.
- La stratégie de sauvegarde.
- Le contrôle de l'accès aux données.

### Livrable F — Sécurité

Expliquer :

- Les données sensibles exclues.
- Les frontières de confiance.
- Les accès aux interfaces.
- Les ports exposés.
- La protection des secrets.
- La rétention.
- Les mesures de réduction de cardinalité.

### Livrable G — Incident simulé

Créer une erreur et une dégradation de latence, puis fournir :

- Le trace ID.
- La liste des spans.
- Les durées observées.
- Les journaux associés.
- Les métriques de la période.
- La cause confirmée ou l'hypothèse retenue.
- La correction appliquée.
- La preuve du rétablissement.
- Les améliorations proposées.

Le projet n'est pas validé simplement parce que Grafana affiche des traces. Il doit démontrer que les données permettent réellement d'analyser un incident distribué.

## 41. Bonnes pratiques à retenir

### Tracing

- Instrumenter les opérations importantes.
- Utiliser les conventions sémantiques adaptées.
- Conserver des noms de spans stables.
- Propager le contexte entre services.
- Distinguer durée de span et durée de trace.
- Échantillonner selon des objectifs documentés.
- Contrôler les attributs sensibles.
- Prévoir les cas d'instrumentation incomplète.

### Journaux

- Préférer une structure stable.
- Ajouter les trace ID et span ID lorsqu'un contexte valide existe.
- Utiliser un nom d'événement stable.
- Enregistrer les erreurs avec suffisamment de contexte.
- Éviter les secrets et données inutiles.
- Garder les identifiants uniques hors des labels Loki à forte cardinalité.
- Définir la rétention et les permissions.

### OpenTelemetry Collector

- Limiter l'usage mémoire.
- Grouper les données lorsque c'est pertinent.
- Surveiller les erreurs d'export.
- Vérifier la disponibilité des composants configurés.
- Contrôler la politique d'échantillonnage.
- Sécuriser les endpoints.
- Tester les modifications de pipeline.

### Loki et Tempo

- Adapter le stockage à la volumétrie.
- Définir une politique de rétention.
- Vérifier la protection des données.
- Surveiller les performances.
- S'assurer que les traces et logs sont corrélables.
- Ne pas confondre données manquantes et absence d'erreur.
- Tester la recherche avec les attributs réels.

### Grafana

- Configurer les sources de données explicitement.
- Construire une navigation entre logs, traces et métriques.
- Définir des plages temporelles cohérentes.
- Éviter les visualisations trop chargées.
- Protéger les rôles et les accès.
- Vérifier les liens dérivés de corrélation.

## 42. Référence opérationnelle rapide

| Besoin | Outil ou méthode |
|---|---|
| Instrumenter une application | OpenTelemetry SDK et instrumentations |
| Transmettre la télémétrie | OTLP |
| Collecter et transformer les signaux | OpenTelemetry Collector |
| Traces distribuées | Tempo |
| Journaux centralisés | Loki |
| Collecter les journaux du laboratoire | Grafana Alloy |
| Rechercher des traces | TraceQL |
| Rechercher des journaux | LogQL |
| Collecter les métriques système Linux | Node Exporter |
| Stocker les métriques | Prometheus |
| Visualiser les données | Grafana |
| Corréler un journal à une trace | `trace_id` et champ dérivé |
| Corréler une trace à une opération | `span_id`, attributs et chronologie |
| Réduire le volume de traces | Head sampling ou tail sampling |
| Limiter la cardinalité Loki | Labels peu nombreux et stables |
| Valider un pipeline de collecte | Tests de bout en bout et journaux des composants |

## 43. Glossaire

**Attribut :** paire clé-valeur qui décrit une opération ou une ressource de télémétrie.

**Baggage :** ensemble de paires clé-valeur propagées à travers les frontières d'un système distribué.

**Cardinalité :** nombre de combinaisons distinctes de séries ou de labels.

**Collector :** composant qui reçoit, traite et exporte de la télémétrie.

**Contexte distribué :** informations propagées entre services permettant notamment de relier les spans d'une même trace.

**Exemplar :** association entre une observation de métrique et une trace, utilisée pour faciliter la navigation entre signaux.

**Head sampling :** échantillonnage décidé au début du parcours de trace.

**LogQL :** langage de requête des journaux Loki.

**OpenTelemetry :** ensemble de spécifications, d'API, de SDK et d'outils de télémétrie.

**OTLP :** protocole de transmission des signaux OpenTelemetry.

**Propagation :** mécanisme qui transmet le contexte d'observabilité à travers les frontières des services.

**Resource :** ensemble d'attributs décrivant la source qui produit la télémétrie.

**Span :** unité de travail observée, avec durée et métadonnées.

**Span ID :** identifiant d'un span donné.

**Tail sampling :** échantillonnage décidé à partir des informations observées dans la trace.

**Tempo :** backend de stockage et de recherche de traces distribué.

**Trace :** représentation du parcours d'une opération à travers un système.

**Trace ID :** identifiant d'une trace.

**TraceQL :** langage de requête des traces Tempo.

**Trace Context :** format standardisé de propagation du contexte des traces, notamment par les en-têtes HTTP W3C.

**Alloy :** outil Grafana de collecte, traitement et transmission de données d'observabilité.

**Loki :** système de centralisation et de recherche de journaux.

## 44. Documentation officielle

### OpenTelemetry

- Concepts des traces : https://opentelemetry.io/docs/concepts/signals/traces/
- Propagation du contexte : https://opentelemetry.io/docs/concepts/context-propagation/
- Échantillonnage : https://opentelemetry.io/docs/concepts/sampling/
- Configuration du Collector : https://opentelemetry.io/docs/collector/configuration/
- Configuration des exporteurs OTLP : https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/
- Conventions sémantiques : https://opentelemetry.io/docs/specs/semconv/
- Spécification du contexte W3C : https://www.w3.org/TR/trace-context/

### Tempo et TraceQL

- Documentation Tempo : https://grafana.com/docs/tempo/latest/
- Installation et configuration : https://grafana.com/docs/tempo/latest/set-up-for-tracing/
- Architecture Tempo : https://grafana.com/docs/tempo/latest/introduction/architecture/
- Métriques générées à partir des traces : https://grafana.com/docs/tempo/latest/metrics-from-traces/
- Exemples TraceQL : https://grafana.com/docs/grafana/latest/datasources/tempo/query-editor/traceql-query-examples/

### Loki et Alloy

- Documentation Loki : https://grafana.com/docs/loki/latest/
- Requêtes LogQL : https://grafana.com/docs/loki/latest/query/
- Traitement des journaux dans Alloy : https://grafana.com/docs/alloy/latest/reference/components/loki/loki.process/
- Lecture des fichiers de journaux : https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.file/
- Documentation Alloy : https://grafana.com/docs/alloy/latest/

### Grafana et Prometheus

- Documentation Grafana : https://grafana.com/docs/grafana/latest/
- Source de données Tempo : https://grafana.com/docs/grafana/latest/datasources/tempo/
- Source de données Loki : https://grafana.com/docs/grafana/latest/datasources/loki/
- Documentation Prometheus : https://prometheus.io/docs/
- Guide Node Exporter : https://prometheus.io/docs/guides/node-exporter/

Les configurations de ce cours sont des bases pédagogiques. Avant une utilisation en production, vérifier les versions, les schémas de configuration, les dépendances et les consignes de sécurité correspondant aux composants effectivement déployés.

## 45. Conclusion du niveau expert

L'observabilité avancée ne consiste pas à accumuler des métriques, des journaux et des traces indépendamment les uns des autres. Elle consiste à créer un ensemble cohérent de données permettant de comprendre le comportement d'un système distribué.

Les métriques signalent les variations et les dégradations. Les traces montrent le parcours d'une opération et les dépendances qui interviennent. Les journaux expliquent les événements. Les identifiants de corrélation permettent de passer d'un signal à un autre.

OpenTelemetry standardise la production et la transmission de la télémétrie. Le Collector fournit un point de traitement contrôlé. Tempo et Loki répondent à des besoins complémentaires, tandis que Grafana aide à explorer les données et à reconstituer les incidents.

La maîtrise experte suppose également de connaître les limites de la chaîne : échantillonnage, perte de contexte, cardinalité, saturation, rétention, sécurité, données sensibles et erreurs d'export.

L'objectif final est de pouvoir suivre une transaction depuis son entrée jusqu'à ses dépendances, d'identifier les opérations responsables d'une dégradation, de retrouver les journaux pertinents et de démontrer par des mesures que le service a été rétabli.

**Une observabilité de qualité ne se mesure pas au volume de données collectées, mais à la capacité de ces données à répondre rapidement, précisément et de manière sécurisée aux questions opérationnelles.**