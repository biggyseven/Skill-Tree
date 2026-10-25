# SRE : SLI, SLO et gestion des incidents

## Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit être capable de :

- Comprendre les principes du Site Reliability Engineering.
- Différencier SLA, SLI, SLO, indicateurs techniques et objectifs métier.
- Définir des objectifs de fiabilité mesurables.
- Calculer un budget d'erreur et piloter les changements en fonction du risque.
- Construire des alertes orientées symptômes et impact utilisateur.
- Utiliser les métriques, logs et traces pour diagnostiquer un incident.
- Organiser la réponse aux incidents de production.
- Définir les rôles, les procédures d'escalade et la communication de crise.
- Conduire une analyse post-incident sans recherche de coupable.
- Mettre en œuvre des exercices de résilience et des game days.
- Automatiser une partie du suivi SRE avec Prometheus, Grafana et des pipelines CI/CD.
- Construire un tableau de bord de fiabilité exploitable par une équipe technique.

## 1. Positionnement dans le parcours DevOps

Les cours précédents ont introduit les outils et pratiques nécessaires pour livrer et exploiter des applications. Ce cours ajoute une dimension essentielle : mesurer la fiabilité du service rendu et décider comment la préserver.

Le SRE ne consiste pas simplement à installer un outil de monitoring. Il s'agit d'une discipline d'ingénierie qui applique des méthodes mesurables à l'exploitation des systèmes.

### 1.1 Du déploiement à la fiabilité

```text
Développement
     |
     v
Git et revues de code
     |
     v
CI/CD : tests, construction, validation
     |
     v
Conteneurs et orchestration
     |
     v
Déploiement en production
     |
     v
Observabilité
     |
     +---- Métriques
     +---- Logs
     +---- Traces
     |
     v
SLI : mesurer le service réellement rendu
     |
     v
SLO : fixer une cible de fiabilité
     |
     v
Budget d'erreur : quantifier le risque accepté
     |
     v
Décisions de livraison et de fiabilité
     |
     v
Gestion des incidents et amélioration continue
```

Le pipeline CI/CD permet de livrer une modification. L'observabilité permet de comprendre son comportement. Les SLO permettent de déterminer si le service reste suffisamment fiable.

### 1.2 Les responsabilités complémentaires

| Domaine | Question principale |
|---|---|
| DevOps | Comment fluidifier la livraison et l'exploitation ? |
| Observabilité | Que se passe-t-il dans le système et pourquoi ? |
| SRE | Quel niveau de fiabilité devons-nous fournir et comment le maintenir ? |
| Gestion des incidents | Comment rétablir rapidement le service lorsqu'il se dégrade ? |
| Gestion des problèmes | Comment réduire le risque de réapparition ? |

Ces disciplines sont complémentaires. Une équipe peut disposer d'une excellente plateforme de monitoring sans avoir défini un objectif de fiabilité pertinent.

## 2. Comprendre le SRE

### 2.1 Définition

Le Site Reliability Engineering est une approche d'ingénierie de la fiabilité des services informatiques. Elle repose notamment sur :

- des objectifs de service mesurables ;
- l'automatisation des tâches répétitives ;
- la réduction du travail opérationnel manuel ;
- la gestion du risque de changement ;
- la réponse structurée aux incidents ;
- l'apprentissage à partir des défaillances.

L'objectif n'est pas d'éliminer toute panne. Il est de réduire la probabilité, la durée et l'impact des défaillances à un niveau compatible avec les besoins métier.

### 2.2 Fiabilité et disponibilité

La disponibilité est une dimension de la fiabilité, mais elle ne la représente pas entièrement.

Un service peut répondre aux requêtes tout en étant inutilisable :

- les pages mettent trente secondes à s'afficher ;
- les résultats sont incomplets ;
- les transactions échouent après une réponse HTTP 200 ;
- les données sont incorrectes ;
- les opérations sont exécutées en double.

Une stratégie SRE doit donc mesurer plusieurs dimensions lorsque cela est nécessaire : disponibilité, latence, correction des résultats, fraîcheur des données et capacité à terminer une opération.

### 2.3 Le travail opérationnel répétitif

Le terme anglais *toil* désigne le travail opérationnel répétitif, manuel, automatisable et souvent peu durable.

Exemples :

- redémarrer manuellement le même service chaque jour ;
- augmenter régulièrement la capacité sans mécanisme automatique ;
- traiter chaque alerte avec les mêmes commandes ;
- reconstruire manuellement un environnement après chaque incident.

Le SRE cherche à supprimer la cause de ce travail plutôt qu'à simplement accélérer son exécution.

Une tâche manuelle n'est pas nécessairement du toil : une intervention exceptionnelle, complexe et nécessitant un jugement humain peut être parfaitement légitime.

## 3. SLA, SLI et SLO

Ces trois notions sont fondamentales et ne doivent pas être confondues.

### 3.1 SLI : Service Level Indicator

Un SLI est un indicateur qui mesure une dimension précise du service réellement fourni.

Exemples :

- proportion de requêtes réussies ;
- proportion de requêtes terminées sous 300 ms ;
- proportion de transactions correctement enregistrées ;
- proportion de données actualisées dans les délais attendus.

Un bon SLI est défini de manière précise, mesurable et reproductible.

### 3.2 SLO : Service Level Objective

Un SLO est un objectif fixé pour un SLI sur une période déterminée.

Exemple :

> Au moins 99,9 % des requêtes éligibles doivent être réussies sur une fenêtre glissante de 30 jours.

Un SLO doit spécifier :

1. le service concerné ;
2. l'événement mesuré ;
3. les événements inclus et exclus ;
4. la cible numérique ;
5. la fenêtre temporelle ;
6. la source des données ;
7. le propriétaire de l'objectif.

### 3.3 SLA : Service Level Agreement

Un SLA est un engagement formel vis-à-vis d'un client ou d'une autre partie. Il peut prévoir des crédits, des pénalités ou d'autres conséquences contractuelles si les engagements ne sont pas respectés.

Un SLA peut utiliser un SLI et un SLO comme fondation, mais les deux notions ne sont pas interchangeables.

```text
SLI
 |  Mesure réelle du service
 v
SLO
 |  Objectif interne ou opérationnel
 v
SLA
    Engagement contractuel éventuel
    et conséquences définies par contrat
```

Exemple :

- SLI : pourcentage de requêtes valides réussies.
- SLO interne : 99,9 % de réussite sur 30 jours.
- SLA client : disponibilité contractuelle de 99,5 %, selon une définition et des exclusions précisées au contrat.

L'objectif interne peut être plus exigeant que l'engagement contractuel afin de conserver une marge de sécurité.

## 4. Définir des SLI pertinents

### 4.1 Commencer par le parcours utilisateur

Un SLI technique ne doit pas être choisi uniquement parce qu'il est facile à collecter.

Pour une plateforme de commerce, les questions importantes peuvent être :

- Le catalogue est-il consultable ?
- Les utilisateurs peuvent-ils ajouter des articles au panier ?
- Le paiement aboutit-il ?
- La commande est-elle enregistrée correctement ?

Une API peut avoir un taux de réponses HTTP 200 élevé tout en échouant à enregistrer les commandes dans la base de données.

Le SLI doit donc mesurer le résultat qui compte pour l'utilisateur.

### 4.2 SLI basé sur les événements

Pour un SLI de réussite :

\[
SLI = \frac{\text{Événements réussis}}{\text{Événements éligibles}} \times 100
\]

Exemple :

- 100 000 requêtes éligibles ;
- 99 920 requêtes réussies.

\[
SLI = \frac{99\,920}{100\,000}\times100 = 99,92\%
\]

Pour un SLI de latence, on peut mesurer la proportion de requêtes qui terminent sous un seuil :

\[
SLI_{latence} =
\frac{\text{Requêtes terminées sous le seuil}}
{\text{Requêtes éligibles}}\times100
\]

Si 98 700 requêtes sur 100 000 terminent en moins de 300 ms, le SLI de latence sous ce seuil est de 98,7 %.

### 4.3 Bien définir le dénominateur

Le dénominateur détermine ce qui compte dans la mesure.

Il faut préciser :

- si les requêtes de santé sont incluses ;
- si les requêtes invalides des clients sont exclues ;
- comment les délais d'attente sont comptabilisés ;
- si les tentatives répétées sont considérées comme plusieurs événements ;
- si les erreurs internes sont toutes considérées comme des échecs ;
- comment sont traitées les périodes où aucune requête n'arrive.

Les exclusions ne doivent pas servir à masquer les défaillances du service. Une exclusion doit avoir une justification explicite.

### 4.4 Les quatre signaux d'or

Une approche classique de la surveillance des services repose sur quatre signaux :

| Signal | Ce qu'il mesure | Exemples |
|---|---|---|
| Latence | Temps de réponse | p50, p95, p99 |
| Trafic | Volume de demandes | requêtes/s, transactions/min |
| Erreurs | Échecs visibles ou fonctionnels | taux d'erreur, paiements refusés à tort |
| Saturation | Proximité des limites de capacité | CPU, mémoire, pool de connexions |

Ces signaux sont utiles au diagnostic, mais tous ne constituent pas directement un SLI utilisateur.

La CPU peut être saturée sans que le service soit actuellement en échec. Inversement, un service peut être indisponible alors que sa CPU est faible.

## 5. Fenêtres de mesure et latence

### 5.1 Fenêtre temporelle

Un SLO doit utiliser une fenêtre définie.

Exemples :

- fenêtre glissante de 30 jours ;
- fenêtre de 7 jours pour un suivi opérationnel ;
- période calendaire contractuelle, si le SLA le demande.

Une fenêtre glissante permet de suivre en permanence le comportement récent du service. Une période calendaire peut être utile pour le reporting contractuel.

Il faut éviter de mélanger les deux sans l'indiquer.

### 5.2 Pourquoi les percentiles sont utiles

La moyenne peut masquer les requêtes lentes.

Supposons ces temps de réponse :

```text
50 ms, 55 ms, 60 ms, 65 ms, 70 ms, 80 ms, 100 ms, 120 ms, 900 ms
```

La majorité des requêtes est rapide, mais une requête atteint 900 ms.

- p50 : temps sous lequel se trouvent environ 50 % des observations ;
- p95 : temps sous lequel se trouvent environ 95 % des observations ;
- p99 : temps sous lequel se trouvent environ 99 % des observations.

Les percentiles décrivent la distribution, mais ils ne remplacent pas un SLI clairement défini.

Pour un SLO exigeant que 99 % des requêtes terminent en moins de 300 ms, la mesure la plus directe est la proportion de requêtes respectant ce seuil. Un percentile peut être utilisé pour le suivi, à condition de bien comprendre la méthode de calcul et les limites statistiques.

## 6. Concevoir un SLO exploitable

### 6.1 Exemple de fiche SLO

```text
Service             : API de commandes
Parcours utilisateur: Créer une commande
SLI                 : Proportion de commandes correctement enregistrées
Cible               : 99,9 %
Fenêtre             : 30 jours glissants
Source              : Événements applicatifs et confirmation de persistance
Exclusions          : Requêtes invalides selon le contrat API
Propriétaire        : Équipe plateforme e-commerce
Alerte              : Consommation rapide du budget d'erreur
Revue               : Mensuelle et après incident majeur
```

Cette fiche permet de vérifier si l'objectif est mesurable et si les responsabilités sont clairement établies.

### 6.2 Plusieurs SLO pour un même service

Un service peut avoir plusieurs objectifs :

- disponibilité des requêtes ;
- latence des lectures ;
- réussite des paiements ;
- fraîcheur des données ;
- délai de traitement d'une file.

Il ne faut pas créer un SLO pour chaque métrique technique. Trop d'objectifs rendent la gouvernance difficile et encouragent l'optimisation d'indicateurs qui n'améliorent pas réellement le service.

Commencer par quelques SLO liés aux parcours métier critiques est généralement plus efficace.

## 7. Calculer le budget d'erreur

### 7.1 Définition

Le budget d'erreur est la quantité de défaillance tolérée par rapport à un SLO sur une fenêtre donnée.

Pour un SLO de réussite de 99,9 % :

\[
Budget = 1 - 0,999 = 0,001
\]

Le budget représente donc 0,1 % des événements éligibles.

### 7.2 Exemple sur 30 jours

Pour une fenêtre de 30 jours et un objectif de disponibilité de 99,9 % :

\[
30 \times 24 \times 60 = 43\,200\text{ minutes}
\]

\[
43\,200 \times 0,001 = 43,2\text{ minutes}
\]

Dans une approximation basée sur le temps, le budget équivaut à 43,2 minutes d'indisponibilité sur 30 jours.

Attention : si le SLI est basé sur les requêtes, ce budget représente une proportion de requêtes en échec, pas directement une durée. Un service peut subir une panne complète pendant une minute ou des erreurs intermittentes pendant plusieurs heures et consommer le même budget, selon le trafic.

### 7.3 Comparaison des objectifs

| SLO | Budget relatif | Équivalent temporel sur 30 jours |
|---|---:|---:|
| 99 % | 1 % | 7 h 12 min |
| 99,5 % | 0,5 % | 3 h 36 min |
| 99,9 % | 0,1 % | 43 min 12 s |
| 99,95 % | 0,05 % | 21 min 36 s |
| 99,99 % | 0,01 % | 4 min 19 s environ |

L'équivalent temporel est une illustration valable pour un objectif de disponibilité mesuré dans le temps. Pour un SLI basé sur les événements, il faut calculer le nombre d'événements tolérés à partir du volume éligible.

### 7.4 Consommation du budget

Supposons :

- 1 000 000 de requêtes éligibles ;
- un SLO de 99,9 % ;
- 1 500 requêtes en échec.

Le budget maximal est :

\[
1\,000\,000 \times 0,001 = 1\,000
\]

La consommation est de 1 500 échecs sur un budget de 1 000, soit 150 % du budget.

Le SLO est dépassé. Le service ne respecte plus son objectif sur la période mesurée.

## 8. Taux de consommation et burn rate

Le *burn rate* exprime la vitesse à laquelle le budget d'erreur est consommé par rapport à la vitesse compatible avec le SLO.

\[
BurnRate = \frac{\text{Taux d'erreur observé}}
{\text{Taux d'erreur autorisé}}
\]

Pour un SLO de 99,9 %, le taux d'erreur autorisé est de 0,1 %.

Si le taux d'erreur observé est de 1 % :

\[
BurnRate = \frac{1\%}{0,1\%} = 10
\]

Le budget est consommé dix fois plus vite que le rythme compatible avec l'objectif.

### 8.1 Interprétation

- Burn rate inférieur à 1 : consommation inférieure au rythme autorisé sur la période considérée.
- Burn rate égal à 1 : consommation au rythme autorisé.
- Burn rate supérieur à 1 : consommation trop rapide pour respecter l'objectif si cette situation persiste.

Le burn rate ne signifie pas à lui seul que le SLO est déjà dépassé. La durée d'observation et le budget restant sont également importants.

### 8.2 Alertes multi-fenêtres

Une alerte sur une seule fenêtre peut être trop sensible ou trop lente.

Une stratégie consiste à combiner :

- une fenêtre courte pour détecter une dégradation brutale ;
- une fenêtre plus longue pour confirmer qu'elle est significative.

Exemple de politique :

```text
Fenêtre longue : burn rate > 14,4
ET
Fenêtre courte : burn rate > 14,4
--------------------------------
Action : alerte urgente
```

Pour une fenêtre SLO de 30 jours, un burn rate de 14,4 consomme théoriquement tout le budget en environ 50 heures s'il persiste.

Une seconde règle peut détecter une consommation plus lente, avec un burn rate inférieur mais persistant.

Les seuils doivent être adaptés au service, à son trafic et au niveau d'urgence attendu. Il ne faut pas copier aveuglément des valeurs sans vérifier leur signification.

## 9. Politique de gestion du budget d'erreur

Le budget d'erreur permet de prendre des décisions explicites.

### 9.1 Budget confortable

Lorsque la consommation est faible :

- poursuivre les livraisons selon les contrôles habituels ;
- maintenir les tests et les validations ;
- corriger les défauts identifiés ;
- surveiller les tendances.

### 9.2 Budget qui diminue rapidement

Lorsque le budget est consommé trop vite :

- analyser les changements récents ;
- renforcer les tests de non-régression ;
- réduire la taille des déploiements ;
- améliorer les mécanismes de rollback ;
- consacrer davantage de capacité à la fiabilité.

### 9.3 Budget épuisé

Une politique peut limiter les changements non urgents tant que le risque n'est pas réduit.

Elle doit prévoir des exceptions pour les changements nécessaires à la restauration de la sécurité, à la correction de la panne ou à la réduction d'un risque critique.

```text
Budget disponible
       |
       v
Consommation normale ?
   |             |
  Oui           Non
   |             |
   v             v
Livraisons       Analyse de la dégradation
normales         et des causes
   |             |
   v             v
Surveillance     Budget épuisé ?
                 |          |
                Non        Oui
                 |          |
                 v          v
           Renforcer les   Appliquer la politique
           contrôles       de limitation du risque
                 |          |
                 +----+-----+
                      |
                      v
              Mesurer l'amélioration
```

Cette politique ne doit pas devenir une punition. Le budget est un outil de gestion du risque collectif.

## 10. Instrumentation et architecture d'observabilité

### 10.1 Architecture de référence

```text
Utilisateurs
    |
    v
Load balancer / Ingress
    |
    v
Applications
    |
    +---- Métriques ----> Prometheus
    |                         |
    |                         v
    |                      Grafana
    |                         |
    |                         v
    |                   Alertmanager
    |
    +---- Logs ----------> Collecteur de logs
    |                         |
    |                         v
    |                  Stockage / recherche
    |
    +---- Traces --------> Collecteur OpenTelemetry
                              |
                              v
                         Backend de traces

SLI / SLO
    |
    +---- Calcul à partir des données fiables
    |
    +---- Tableau de bord de fiabilité
    |
    +---- Alertes de consommation du budget
    |
    +---- Décisions opérationnelles
```

Prometheus, Grafana, OpenTelemetry et un backend de logs ou de traces sont des exemples d'outils. Le choix exact dépend de l'environnement.

### 10.2 Métriques applicatives

Pour mesurer le taux de réussite, une application peut exposer des compteurs :

```text
http_requests_total{status="200"}
http_requests_total{status="500"}
```

Une métrique de latence peut être exposée sous forme d'histogramme :

```text
http_request_duration_seconds_bucket
http_request_duration_seconds_sum
http_request_duration_seconds_count
```

Les noms et labels exacts dépendent de l'instrumentation utilisée.

Éviter les labels à cardinalité très élevée comme `user_id`, `request_id` ou des URL contenant des identifiants dynamiques. Ils peuvent provoquer une consommation excessive de mémoire et de ressources.

### 10.3 Logs et traces

Les logs apportent des événements détaillés. Les traces distribuées montrent le parcours d'une requête entre plusieurs services.

Pour investiguer une erreur, il est utile de disposer d'un identifiant de corrélation partagé entre :

- la requête entrante ;
- les logs applicatifs ;
- les traces ;
- les appels aux dépendances.

Ne pas utiliser des identifiants personnels ou des secrets comme labels de métriques.

### 10.4 La qualité des données

Un SLO n'est fiable que si les données le sont.

Il faut vérifier :

- la couverture de l'instrumentation ;
- la synchronisation temporelle ;
- les pertes de données ;
- les redémarrages et réinitialisations de compteurs ;
- la cohérence des labels ;
- la prise en compte des erreurs fonctionnelles ;
- le comportement pendant les périodes sans trafic.

Une absence de métrique ne doit pas automatiquement être interprétée comme une réussite.

## 11. Prometheus : calculer un taux de réussite

Les exemples suivants supposent une métrique de compteur `http_requests_total`, avec un label `status` contenant le code HTTP.

### 11.1 Taux de requêtes en échec

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

Cette expression estime la proportion de requêtes répondant par un code 5xx sur cinq minutes.

Elle ne couvre pas nécessairement tous les échecs. Les erreurs réseau, les délais d'attente, les réponses fonctionnellement incorrectes ou les codes 4xx pertinents peuvent nécessiter une instrumentation complémentaire.

### 11.2 Pourcentage de réussite

```promql
100 * (
  1 -
  (
    sum(rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total[5m]))
  )
)
```

Cette expression doit être interprétée avec prudence lorsque le trafic est nul ou lorsque les métriques sont absentes.

En production, on peut utiliser des règles d'enregistrement, une instrumentation dédiée et une gestion explicite des cas sans données.

### 11.3 Exemple d'alerte simple

```yaml
groups:
  - name: api-reliability
    rules:
      - alert: HighHttp5xxRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.02
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Taux d'erreurs HTTP 5xx élevé"
          description: "Le taux de 5xx dépasse 2 % depuis cinq minutes."
```

Cette règle est un exemple pédagogique. Avant utilisation en production, il faut définir le comportement lorsque le dénominateur est nul, vérifier les labels et adapter le seuil à la criticité du service.

Une alerte technique sur les 5xx ne remplace pas une alerte fondée sur la consommation du budget d'erreur.

## 12. Alertes orientées symptômes

### 12.1 Symptômes et causes

Une alerte de symptôme indique que le service rendu à l'utilisateur se dégrade.

Exemples :

- le taux de réussite diminue ;
- le p99 dépasse un seuil critique ;
- le budget d'erreur est consommé trop rapidement.

Une alerte de cause indique un problème interne potentiel :

- CPU élevée ;
- mémoire proche de la limite ;
- disque presque plein ;
- nombre de connexions élevé.

Les alertes de cause sont utiles pour le diagnostic et la prévention, mais ne prouvent pas toujours qu'un incident utilisateur est en cours.

### 12.2 Une alerte doit être actionnable

Chaque alerte importante devrait préciser :

- le symptôme ;
- la portée et l'impact probable ;
- la gravité ;
- le service concerné ;
- le tableau de bord pertinent ;
- les premières vérifications ;
- la procédure d'escalade ;
- le propriétaire de l'alerte.

Une alerte sans action possible ou sans responsable risque de devenir du bruit.

### 12.3 Réduire la fatigue d'alerte

La fatigue d'alerte apparaît lorsque les opérateurs reçoivent trop de notifications, souvent répétitives ou non actionnables.

Pour la réduire :

- supprimer les alertes sans action utile ;
- regrouper les alertes liées à une même cause ;
- appliquer des fenêtres de maintien adaptées ;
- utiliser des seuils fondés sur l'impact ;
- distinguer les notifications des pages urgentes ;
- tester régulièrement les règles ;
- documenter les procédures associées.

## 13. Gestion des incidents

### 13.1 Définition d'un incident

Un incident est un événement qui dégrade ou menace le service au-delà de ce qui est acceptable.

Exemples :

- panne complète de l'API ;
- hausse importante des échecs de paiement ;
- corruption de données ;
- latence qui rend l'application inutilisable ;
- compromission de sécurité ;
- perte d'une dépendance critique.

La gravité dépend de l'impact, pas uniquement du composant technique affecté.

### 13.2 Cycle de vie

```text
Détection
   |
   v
Qualification
   |
   v
Déclaration de l'incident
   |
   v
Mobilisation des intervenants
   |
   v
Confinement et mitigation
   |
   v
Restauration du service
   |
   v
Vérification des SLI
   |
   v
Clôture opérationnelle
   |
   v
Postmortem et actions correctives
```

La restauration du service doit généralement être prioritaire sur l'identification immédiate de la cause racine.

### 13.3 Gravité des incidents

Exemple de classification à adapter :

| Niveau | Impact | Exemple |
|---|---|---|
| SEV-1 | Critique, service majeur indisponible ou risque grave | Tous les paiements échouent |
| SEV-2 | Dégradation importante d'un parcours essentiel | Une part importante des commandes échoue |
| SEV-3 | Impact limité avec contournement possible | Fonction secondaire dégradée |
| SEV-4 | Anomalie mineure ou sans impact utilisateur immédiat | Défaut non bloquant d'un tableau de bord |

La classification doit être documentée. Elle ne doit pas dépendre uniquement de l'intuition de la personne de garde.

## 14. Rôles pendant un incident

Pour les incidents importants, il est utile de séparer les responsabilités.

### 14.1 Incident Commander

L'Incident Commander coordonne la réponse :

- fixe les priorités ;
- distribue les tâches ;
- suit les décisions ;
- contrôle le rythme des communications ;
- demande des renforts ;
- vérifie que la situation est comprise collectivement.

Il ne doit pas nécessairement être la personne qui effectue le diagnostic technique.

### 14.2 Responsable technique

Le responsable technique :

- conduit l'investigation ;
- formule et teste les hypothèses ;
- coordonne les modifications techniques ;
- vérifie les résultats ;
- propose la stratégie de mitigation.

### 14.3 Responsable communication

Il communique les informations validées aux parties prenantes selon la politique de l'organisation.

La communication doit préciser les faits connus, les impacts confirmés, les mesures engagées et la prochaine mise à jour prévue.

### 14.4 Journal de décision

Un journal chronologique évite de perdre le contexte :

```text
09:00 - Détection d'une hausse des erreurs de paiement
09:04 - Incident SEV-2 déclaré
09:06 - Incident Commander désigné
09:10 - Déploiement récent identifié comme suspect
09:14 - Décision de suspendre les déploiements
09:18 - Rollback lancé
09:23 - Taux d'erreur en baisse
09:30 - Vérification des transactions en attente
09:45 - Service stabilisé, surveillance renforcée
```

Les heures ci-dessus sont fictives. Le journal doit distinguer les faits, les hypothèses et les décisions.

## 15. Mitigation et restauration

### 15.1 Priorité à la restauration

Pendant un incident, il peut être plus efficace de revenir à une version connue comme saine que de chercher immédiatement à corriger le code en production.

Options possibles :

- rollback ;
- désactivation d'une fonctionnalité ;
- réduction temporaire du trafic ;
- bascule vers une région ou un environnement de secours ;
- arrêt d'une tâche défectueuse ;
- augmentation temporaire de capacité ;
- isolation d'une dépendance défaillante.

Toute action doit être évaluée en fonction de ses risques et de sa réversibilité.

### 15.2 Ne pas confondre mitigation et correction définitive

La mitigation réduit l'impact immédiat. La correction définitive élimine ou réduit durablement la cause du problème.

Exemple :

- Mitigation : désactiver une fonctionnalité qui provoque des erreurs.
- Correction durable : corriger le défaut, ajouter un test de régression et améliorer le déploiement progressif.

### 15.3 Vérifier la restauration

Une amélioration ponctuelle d'une métrique ne prouve pas que l'incident est terminé.

Vérifier :

- le taux de réussite ;
- la latence ;
- les transactions en attente ;
- la cohérence des données ;
- l'état des dépendances ;
- la consommation du budget d'erreur ;
- les éventuels effets secondaires.

La clôture doit être une décision explicite, documentée et validée selon la procédure.

## 16. Déploiements sûrs et fiabilité

La gestion des incidents est étroitement liée à la stratégie de livraison.

### 16.1 Déploiement progressif

Un déploiement progressif expose une modification à une partie limitée du trafic avant de l'étendre.

```text
Version stable
      |
      v
Déploiement sur 5 %
      |
      v
Vérification des SLI
      |
      +---- Dégradation ----> Arrêt / rollback
      |
      v
Déploiement sur 25 %
      |
      v
Nouvelle vérification
      |
      v
Déploiement complet
```

Les seuils de progression doivent être définis avant la livraison.

### 16.2 Canary release

Une version canary reçoit une fraction du trafic réel. Les indicateurs de la nouvelle version sont comparés à ceux de la version stable.

Surveiller notamment :

- les erreurs ;
- la latence ;
- les ressources ;
- les erreurs métier ;
- le budget d'erreur consommé pendant la fenêtre.

Une canary doit disposer d'un mécanisme d'arrêt ou de retour arrière fiable.

### 16.3 Intégration dans la CI/CD

Une politique de déploiement peut vérifier :

- la réussite des tests ;
- la présence d'une procédure de rollback ;
- l'état du service après déploiement ;
- les SLI de la version candidate ;
- les alertes actives ;
- la politique de budget d'erreur.

L'automatisation ne doit pas bloquer aveuglément toute correction urgente. Les exceptions doivent être contrôlées et auditées.

## 17. Kubernetes et SRE

Dans un cluster Kubernetes, la santé des pods ne suffit pas à déterminer si le service est fiable.

Un pod peut être `Running` alors que l'application renvoie des erreurs. À l'inverse, un pod peut être redémarré correctement par le contrôleur sans que l'impact utilisateur soit nul.

### 17.1 Signaux Kubernetes

Surveiller notamment :

- les redémarrages de conteneurs ;
- les pods en attente ;
- les erreurs de démarrage ;
- les échecs de probes ;
- les saturations CPU et mémoire ;
- les erreurs de routage réseau ;
- les problèmes de DNS ;
- les volumes indisponibles ;
- les délais de démarrage après déploiement.

### 17.2 Commandes de diagnostic

```bash
kubectl get pods -A
kubectl get deployments -A
kubectl get events -A --sort-by=.lastTimestamp
kubectl describe pod NOM_DU_POD -n NOM_NAMESPACE
kubectl logs NOM_DU_POD -n NOM_NAMESPACE --since=15m
kubectl logs NOM_DU_POD -n NOM_NAMESPACE --previous
kubectl rollout status deployment/NOM_DEPLOYMENT -n NOM_NAMESPACE
kubectl rollout history deployment/NOM_DEPLOYMENT -n NOM_NAMESPACE
```

Ces commandes fournissent des indices techniques. Il faut ensuite les relier à l'impact mesuré par les SLI.

### 17.3 Probes

- `startupProbe` : donne à l'application le temps nécessaire pour démarrer.
- `readinessProbe` : détermine si le pod peut recevoir du trafic.
- `livenessProbe` : permet de détecter une application bloquée nécessitant éventuellement un redémarrage.

Une probe mal conçue peut provoquer des redémarrages en cascade ou retirer trop de pods du service. Les probes doivent être testées sous charge et en situation de dégradation.

## 18. Postmortem sans recherche de coupable

### 18.1 Objectif

Un postmortem documente l'incident, ses effets, les décisions prises et les améliorations nécessaires.

L'objectif n'est pas de désigner une personne fautive. Il est de comprendre comment les conditions techniques et organisationnelles ont permis à l'incident de survenir et de durer.

### 18.2 Contenu recommandé

```text
Titre :
Date et durée :
Services affectés :
Gravité :
Résumé :
Impact utilisateur :
SLI et SLO concernés :
Chronologie :
Cause technique :
Facteurs contributifs :
Moyens de détection :
Mesures de mitigation :
Ce qui a bien fonctionné :
Ce qui a compliqué la réponse :
Actions correctives :
Responsables :
Échéances :
Méthode de vérification :
```

### 18.3 Distinguer cause et facteurs contributifs

Une panne n'a pas toujours une cause unique.

Exemple :

- un changement augmente le nombre de requêtes vers la base ;
- le pool de connexions atteint sa limite ;
- les délais d'attente augmentent ;
- les requêtes répétées amplifient la charge ;
- les alertes sont déclenchées tardivement ;
- le rollback nécessite une intervention manuelle.

La cause technique initiale ne suffit pas à expliquer toute la durée de l'incident.

### 18.4 Transformer les constats en actions

Une action corrective doit être vérifiable.

Action trop vague :

> Améliorer le monitoring.

Action exploitable :

> Ajouter une alerte sur la consommation rapide du budget d'erreur de l'API, vérifier sa réception en environnement de test et documenter la procédure d'escalade avant le 15 du mois.

Les actions peuvent être classées par catégorie :

- prévention ;
- détection ;
- mitigation ;
- récupération ;
- réduction du rayon d'impact ;
- amélioration des procédures.

## 19. Mesurer la qualité de la réponse aux incidents

Quelques indicateurs peuvent aider à comprendre les performances opérationnelles.

| Indicateur | Signification |
|---|---|
| MTTD | Temps moyen ou médian entre le début d'un incident et sa détection |
| MTTA | Temps entre l'alerte et sa prise en charge |
| MTTR | Temps de restauration ou de résolution, selon une définition explicite |
| Taux de récurrence | Fréquence de réapparition d'incidents similaires |
| Actions postmortem en retard | Actions correctives non terminées à échéance |
| Part des incidents détectés par les utilisateurs | Capacité de détection interne à améliorer |

Les définitions exactes doivent être fixées avant de comparer les équipes ou les périodes.

Le MTTR est ambigu : certaines organisations l'utilisent pour le temps de réparation, d'autres pour la restauration du service. Il faut préciser la définition retenue.

Ces indicateurs ne doivent pas devenir des objectifs isolés qui encouragent à fermer prématurément les incidents ou à éviter leur déclaration.

## 20. Game days et ingénierie de la résilience

Un game day est un exercice planifié dans lequel une équipe teste sa capacité à détecter, diagnostiquer et maîtriser une défaillance.

Exemples :

- perte d'une dépendance ;
- hausse de latence ;
- saturation d'un pool de connexions ;
- redémarrage d'un pod ;
- indisponibilité d'une zone ;
- expiration d'un certificat ;
- indisponibilité du système de collecte de métriques.

### 20.1 Préparer un exercice

Avant l'exercice :

1. définir le scénario ;
2. préciser les systèmes concernés ;
3. obtenir les autorisations nécessaires ;
4. définir les critères d'arrêt ;
5. préparer le retour à l'état normal ;
6. avertir les participants ;
7. mesurer les résultats attendus.

Un exercice en production ne doit pas être improvisé. Il doit avoir un périmètre, des garde-fous et un plan de restauration.

### 20.2 Exemple de scénario

```text
Objectif :
Vérifier la réaction à une dépendance lente.

Hypothèse :
L'API conserve un niveau acceptable de réussite
si la dépendance dépasse temporairement son délai normal.

Injection :
Augmenter de manière contrôlée la latence de la dépendance.

Observations :
- taux d'erreur ;
- p95 et p99 ;
- taille des files ;
- nombre de connexions ;
- burn rate ;
- délai de détection.

Critères d'arrêt :
- dépassement du seuil de sécurité ;
- impact utilisateur inattendu ;
- perte de contrôle de l'exercice.

Résultat attendu :
Dégradation détectée, trafic maîtrisé et retour à l'état normal.
```

## 21. Tableau de bord SRE

Un tableau de bord de fiabilité doit répondre à des questions opérationnelles.

### 21.1 Vue exécutive

- SLO actuels ;
- budget d'erreur restant ;
- tendance de consommation ;
- incidents majeurs ;
- impact métier ;
- évolution sur plusieurs périodes.

### 21.2 Vue opérationnelle

- taux de réussite ;
- distribution de la latence ;
- volume de trafic ;
- saturation ;
- dépendances ;
- burn rate ;
- alertes actives ;
- déploiements récents.

### 21.3 Vue diagnostic

- logs corrélés ;
- traces distribuées ;
- événements Kubernetes ;
- erreurs par version ;
- dépendances lentes ;
- changements récents.

Il faut éviter de réunir toutes les métriques dans un seul écran illisible. Les vues doivent correspondre aux besoins des utilisateurs : responsables métier, ingénieurs de garde et spécialistes du diagnostic.

## 22. Gouvernance des SLO

### 22.1 Qui définit les objectifs ?

Les SLO doivent être définis avec les personnes qui comprennent les besoins métier, les contraintes techniques et les engagements contractuels.

Le processus peut inclure :

1. identification des parcours critiques ;
2. définition des SLI ;
3. choix des objectifs ;
4. validation par les responsables du service ;
5. mise en place des données et des alertes ;
6. revue périodique ;
7. ajustement selon l'expérience.

### 22.2 Éviter les SLO irréalistes

Un SLO de 99,999 % ne doit pas être choisi simplement parce qu'il semble professionnel.

Un objectif très exigeant peut nécessiter :

- redondance supplémentaire ;
- architecture multi-zone ;
- réplication de données ;
- mécanismes de bascule ;
- capacité de récupération rapide ;
- procédures de maintenance complexes ;
- coûts d'infrastructure plus élevés.

Le niveau de fiabilité doit être cohérent avec les besoins réels du service.

### 22.3 Dépendances externes

Si une application dépend d'un fournisseur externe, son propre SLO peut être limité par cette dépendance.

Il faut distinguer :

- le SLO de l'application ;
- le SLO de la dépendance ;
- l'engagement contractuel du fournisseur ;
- l'expérience réellement observée par l'utilisateur.

Une dépendance fiable individuellement peut néanmoins produire des erreurs lorsqu'elle est intégrée dans une architecture mal conçue.

## 23. Sécurité et incidents de fiabilité

La disponibilité ne doit pas être obtenue au détriment de la sécurité.

Exemples de situations à traiter :

- saturation provoquée par une attaque ;
- fuite de secrets ;
- compromission d'un compte de service ;
- déploiement d'une image vulnérable ;
- suppression accidentelle de données ;
- indisponibilité des outils de supervision après compromission.

Les procédures d'incident doivent définir quand mobiliser les responsables sécurité, les administrateurs, les équipes applicatives et les personnes chargées de la communication.

La collecte de données d'observabilité doit respecter les règles de confidentialité. Les secrets, mots de passe, jetons et données personnelles inutiles ne doivent pas être inscrits dans les logs.

## 24. Travaux pratiques : définir les SLO d'une API

### Contexte

Une API de commandes reçoit 2 millions de requêtes éligibles sur une période de 30 jours.

Les mesures sont les suivantes :

- 1 996 000 requêtes réussies ;
- 4 000 requêtes en échec ;
- objectif de réussite : 99,9 %.

### Étape 1 : calculer le SLI

\[
SLI = \frac{1\,996\,000}{2\,000\,000}\times100
\]

Le résultat est 99,8 %.

### Étape 2 : calculer le budget autorisé

Le budget de 0,1 % représente :

\[
2\,000\,000 \times 0,001 = 2\,000
\]

Le budget autorisé est de 2 000 requêtes en échec.

### Étape 3 : comparer au résultat

Le service a enregistré 4 000 échecs.

\[
Consommation = \frac{4\,000}{2\,000}\times100 = 200\%
\]

Le budget est consommé à 200 %. Le SLO n'est pas respecté.

### Étape 4 : proposer des actions

Actions possibles :

- analyser les erreurs par version ;
- corréler les échecs avec les déploiements ;
- examiner les traces des requêtes échouées ;
- vérifier les dépendances ;
- établir un plan de réduction des erreurs ;
- revoir la politique de déploiement si nécessaire.

### Étape 5 : vérifier la qualité du SLI

Il faut encore confirmer que les 2 millions d'événements correspondent au bon périmètre : requêtes éligibles, doublons, erreurs métier, événements manquants et instrumentation.

## 25. Travaux pratiques : construire une procédure d'incident

### Scénario

Après un déploiement, le taux de 5xx passe de 0,2 % à 6 %. La latence p99 augmente fortement. Les pods restent majoritairement `Running`.

### Travail demandé

1. Définir la gravité initiale.
2. Identifier les données à examiner.
3. Choisir les rôles à mobiliser.
4. Proposer une mitigation.
5. Définir les critères de restauration.
6. Préparer les éléments du postmortem.

### Corrigé indicatif

**1. Gravité**

Une hausse importante des erreurs peut justifier un incident SEV-2, voire SEV-1 selon l'impact réel sur les commandes et les paiements. La gravité ne peut pas être déterminée à partir du seul taux de 5xx.

**2. Données à examiner**

- taux d'erreur par version ;
- traces distribuées ;
- logs applicatifs ;
- changements récents ;
- erreurs de dépendances ;
- métriques de base de données ;
- événements Kubernetes ;
- état des SLI métier.

**3. Rôles**

- Incident Commander ;
- responsable technique ;
- spécialistes des dépendances ;
- responsable communication si nécessaire.

**4. Mitigation**

Si la corrélation avec le déploiement est forte et si la version précédente est saine, envisager un rollback contrôlé. Vérifier d'abord les risques liés aux migrations de données et à la compatibilité.

**5. Restauration**

Confirmer la baisse du taux d'erreur, le retour de la latence à un niveau acceptable, la reprise des transactions et l'absence d'effets secondaires.

**6. Postmortem**

Documenter la chronologie, l'impact, la cause technique, les facteurs contributifs, la qualité de la détection et les actions correctives vérifiables.

## 26. Exercices corrigés

### Exercice 1 : budget d'erreur

Un service possède un SLO de 99,5 % et reçoit 500 000 requêtes éligibles.

Combien d'échecs sont autorisés par le budget ?

**Correction**

Le taux d'erreur autorisé est :

\[
1 - 0,995 = 0,005
\]

Le budget vaut :

\[
500\,000 \times 0,005 = 2\,500
\]

Le budget est de 2 500 événements en échec.

### Exercice 2 : burn rate

Le SLO est de 99,9 %. Le taux d'erreur observé est de 0,5 %.

Quel est le burn rate ?

**Correction**

\[
BurnRate = \frac{0,5\%}{0,1\%} = 5
\]

Le budget est consommé cinq fois plus vite que le rythme compatible avec l'objectif si le taux persiste.

### Exercice 3 : moyenne et percentile

La latence moyenne est de 100 ms, mais le p99 atteint 2 secondes.

Peut-on conclure que l'expérience utilisateur est bonne ?

**Correction**

Non. La moyenne masque la lenteur subie par une partie des utilisateurs. Il faut examiner la distribution, le volume d'échantillons, les parcours concernés et la proportion de requêtes dépassant le seuil SLO.

### Exercice 4 : alerte CPU

Une alerte indique que la CPU est à 95 %, mais les SLI restent conformes.

Faut-il déclarer automatiquement un incident majeur ?

**Correction**

Non. La CPU élevée est un signal de saturation et un risque potentiel. Il faut évaluer sa durée, la marge de capacité, la latence, le taux d'erreur et la possibilité d'une dégradation prochaine. La gravité dépend de l'impact et du risque.

### Exercice 5 : postmortem

Un incident est attribué à « une erreur humaine lors du déploiement ».

Pourquoi cette conclusion est-elle insuffisante ?

**Correction**

Elle ne décrit pas les conditions ayant permis l'erreur ni les mécanismes qui auraient pu la prévenir ou la détecter. Il faut examiner les contrôles, la revue, les tests, l'automatisation, les permissions, les procédures de rollback et la visibilité sur l'impact.

## 27. Projet final : plateforme SRE pour une API

### Objectif

Concevoir une démarche SRE complète pour une API conteneurisée, déployée par CI/CD et exploitée sur Kubernetes.

### Livrables

1. Une fiche de service et une description des parcours critiques.
2. Deux SLI mesurables au minimum.
3. Deux SLO avec cibles et fenêtres définies.
4. Un calcul de budget d'erreur.
5. Une politique de consommation du budget.
6. Un tableau de bord de fiabilité.
7. Une procédure d'incident.
8. Un modèle de postmortem.
9. Une stratégie de rollback.
10. Un exercice de résilience documenté.

### Architecture cible

```text
Développeur
    |
    v
Git
    |
    v
CI/CD
    |
    +---- Tests
    +---- Analyse de sécurité
    +---- Construction d'image
    |
    v
Déploiement Kubernetes
    |
    v
API et dépendances
    |
    +---- Métriques
    +---- Logs
    +---- Traces
    |
    v
Plateforme d'observabilité
    |
    v
Calcul des SLI
    |
    v
Évaluation des SLO
    |
    v
Suivi du budget d'erreur
    |
    +---- Livraison normale
    +---- Livraison renforcée
    +---- Mitigation et amélioration
```

### Critères de réussite

Le projet est réussi si :

- les SLI mesurent une expérience utilisateur pertinente ;
- les objectifs sont vérifiables à partir des données disponibles ;
- les exclusions sont documentées ;
- le budget d'erreur est calculable ;
- les alertes sont actionnables ;
- les rôles d'incident sont définis ;
- le rollback est testé ;
- les actions post-incident ont des responsables et des critères de validation.

## 28. Checklist opérationnelle SRE

### SLI et SLO

- [ ] Les parcours critiques sont identifiés.
- [ ] Les SLI mesurent des résultats pertinents.
- [ ] Les événements inclus et exclus sont documentés.
- [ ] Les SLO disposent d'une cible et d'une fenêtre.
- [ ] La source de données est fiable.
- [ ] Les budgets d'erreur sont calculés automatiquement.
- [ ] Les objectifs sont révisés périodiquement.

### Alertes

- [ ] Les alertes importantes correspondent à des symptômes ou à des risques actionnables.
- [ ] Les procédures d'escalade sont documentées.
- [ ] Les alertes ont des propriétaires.
- [ ] Les alertes de burn rate sont testées.
- [ ] Les notifications inutiles sont régulièrement supprimées.

### Incidents

- [ ] Les niveaux de gravité sont définis.
- [ ] Les rôles sont connus.
- [ ] Le journal de décision est accessible.
- [ ] Les moyens de rollback sont testés.
- [ ] Les critères de restauration sont explicites.
- [ ] Les communications sont préparées.

### Amélioration continue

- [ ] Les incidents importants font l'objet d'une analyse.
- [ ] Les actions correctives sont suivies.
- [ ] Les scénarios de panne sont testés.
- [ ] Le travail opérationnel répétitif est identifié.
- [ ] Les changements sont évalués selon le risque.

## 29. Glossaire

- **SRE** : discipline d'ingénierie appliquée à la fiabilité des services.
- **SLI** : indicateur mesurant un aspect du service rendu.
- **SLO** : objectif chiffré pour un SLI sur une fenêtre définie.
- **SLA** : engagement formel, souvent contractuel.
- **Budget d'erreur** : quantité de défaillance autorisée par le SLO.
- **Burn rate** : vitesse de consommation du budget d'erreur relativement au rythme autorisé.
- **MTTD** : délai moyen ou médian de détection, selon la définition retenue.
- **MTTA** : délai de prise en charge d'un incident.
- **MTTR** : durée de réparation ou de restauration selon la convention adoptée.
- **Postmortem** : analyse documentée d'un incident et des améliorations à apporter.
- **Canary release** : déploiement progressif exposant une version à une fraction du trafic.
- **Toil** : travail opérationnel répétitif et automatisable.
- **Golden signals** : latence, trafic, erreurs et saturation.
- **Cardinalité** : nombre de séries temporelles distinctes produites par les combinaisons de labels.
- **Mitigation** : action réduisant l'impact immédiat d'un incident.
- **Résilience** : capacité d'un système à continuer de fonctionner ou à récupérer après une perturbation.

## 30. Références officielles

### Google SRE

- Site officiel du livre SRE : https://sre.google/books/
- Site Reliability Engineering : https://sre.google/sre-book/table-of-contents/
- SLO Engineering : https://sre.google/workbook/table-of-contents/
- Monitoring Distributed Systems : https://sre.google/sre-book/monitoring-distributed-systems/
- Alerting on SLOs : https://sre.google/workbook/alerting-on-slos/

### Prometheus et Grafana

- Documentation Prometheus : https://prometheus.io/docs/introduction/overview/
- Configuration des règles : https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/
- Documentation PromQL : https://prometheus.io/docs/prometheus/latest/querying/basics/
- Documentation Grafana : https://grafana.com/docs/grafana/latest/

### OpenTelemetry et Kubernetes

- Documentation OpenTelemetry : https://opentelemetry.io/docs/
- Documentation Kubernetes : https://kubernetes.io/docs/
- Monitoring Kubernetes : https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/

### Incident management

- Google SRE Workbook : https://sre.google/workbook/table-of-contents/
- PagerDuty Incident Response Documentation : https://response.pagerduty.com/

## Conclusion

La maturité SRE ne se mesure pas au nombre de tableaux de bord ou d'alertes installés. Elle se mesure à la capacité d'une organisation à définir la fiabilité attendue, à mesurer le service réel, à gérer le risque de changement et à rétablir rapidement un service dégradé.

Les SLI fournissent les mesures, les SLO fixent les objectifs, les budgets d'erreur guident les décisions et la gestion des incidents organise la réponse. Associés à une observabilité de qualité, à une CI/CD maîtrisée et à une démarche d'amélioration continue, ces mécanismes transforment l'exploitation en une discipline d'ingénierie mesurable.