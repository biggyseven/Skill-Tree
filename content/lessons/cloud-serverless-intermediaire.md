# Architectures Serverless — Intermédiaire

> **Mise en contexte**
>
> Skill-Tree dispose d'un backend FastAPI, d'une base SQLite, d'un système de labs et d'un Lab Workspace capable de vérifier des configurations et d'enregistrer des tentatives.
>
> Imaginons maintenant que le nombre d'utilisateurs augmente. Certains réalisent plusieurs labs simultanément. Une soumission doit être enregistrée, les XP doivent être attribués, les badges doivent être mis à jour et les statistiques doivent être calculées. Des notifications peuvent également être envoyées.
>
> Si l'un de ces traitements échoue après l'enregistrement d'une tentative, comment garantir que le travail sera repris ? Comment empêcher une seconde livraison du même événement d'attribuer les XP deux fois ? Comment éviter qu'une panne de notification bloque la validation d'un lab ?
>
> C'est précisément le type de problème que l'on apprend à résoudre au niveau intermédiaire du serverless.
>
> Nous allons progressivement construire une architecture dans laquelle les opérations essentielles sont enregistrées de façon fiable, tandis que les traitements secondaires peuvent être exécutés indépendamment. Le travail pratique utilisera Python et SQLite pour rendre ces principes observables localement, avant de les transposer vers un véritable service cloud.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu devras être capable de :

- Concevoir une architecture serverless événementielle composée de plusieurs services.
- Définir des contrats d'événements stables et versionnés.
- Comprendre les garanties de livraison et les traitements en double.
- Concevoir des fonctions idempotentes.
- Mettre en œuvre le principe de l'outbox transactionnelle.
- Définir des stratégies de reprise sur erreur et utiliser une file d'échec définitif.
- Gérer la concurrence, la pression sur les dépendances et les limites d'exécution.
- Organiser des traitements distribués avec des mécanismes de compensation.
- Mettre en place une stratégie de sécurité, de journalisation et de surveillance.
- Tester les fonctions, les contrats d'événements et les scénarios de panne.
- Comprendre les étapes d'un déploiement reproductible.
- Concevoir un traitement serverless qui s'intègre conceptuellement au Lab Workspace de Skill-Tree.

## 2. Prérequis et continuité avec le niveau débutant

Tu dois déjà connaître les principes de base du serverless :

- Une fonction est déclenchée par un événement ou une requête.
- Les fonctions utilisent des services de stockage pour conserver les informations.
- Une file d'attente permet de dissocier la production d'un travail de son traitement.
- Un événement peut être traité plus d'une fois.
- La mise à l'échelle automatique ne garantit pas que les dépendances suivront la charge.

Le niveau intermédiaire change de perspective.

Au niveau débutant, tu apprends à créer une fonction qui calcule un résultat.

Au niveau intermédiaire, tu apprends à concevoir le système autour de cette fonction pour que le résultat reste correct malgré les pannes, les délais, les doublons, les relances et les traitements simultanés.

Prenons un exemple :

**Niveau débutant**

```text
Soumission d'un lab
        |
        v
Fonction de validation
        |
        v
Résultat et XP
```

**Niveau intermédiaire**

```text
Soumission d'un lab
        |
        v
Validation côté serveur
        |
        v
Enregistrement durable
        |
        v
Événement enregistré dans l'outbox
        |
        v
Publication et consommation de l'événement
        |
        v
Vérification de l'idempotence
        |
        v
Attribution atomique de la récompense
        |
        v
Suivi des erreurs et des tentatives
```

La deuxième architecture comporte davantage de composants, mais elle permet de mieux maîtriser les conséquences des défaillances.

## 3. Concevoir une architecture événementielle complète

### 3.1. Pourquoi séparer les responsabilités ?

Une application peut réaliser plusieurs opérations à la suite d'une seule action utilisateur.

Dans Skill-Tree, la soumission réussie d'un lab pourrait déclencher :

- L'enregistrement du résultat.
- L'attribution des XP.
- Le déverrouillage d'un badge.
- La mise à jour des statistiques.
- L'envoi d'une notification.
- L'actualisation d'un tableau de bord.

Si toutes les opérations sont exécutées dans une seule requête HTTP, la disponibilité de cette requête dépend de tous les composants qu'elle utilise.

Imaginons que la validation et l'enregistrement d'un lab prennent 150 ms, mais que le fournisseur de messagerie mette 4 secondes à répondre. Une opération secondaire peut augmenter fortement le temps d'attente de l'utilisateur.

Une séparation des responsabilités permet de distinguer les opérations critiques du parcours utilisateur des traitements qui peuvent être différés.

### 3.2. Le chemin synchrone et le chemin asynchrone

Le **chemin synchrone** réalise ce dont l'appelant a besoin pour obtenir une réponse immédiate.

Pour un lab, il peut comprendre :

- La vérification de l'identité et des autorisations.
- La validation de la soumission.
- La détermination du résultat par le backend.
- L'enregistrement durable de la tentative.

Le **chemin asynchrone** réalise ensuite les opérations qui ne doivent pas obligatoirement terminer avant le retour HTTP, selon les règles métier.

Il peut comprendre :

- L'envoi des notifications.
- La mise à jour de certaines statistiques.
- La génération des rapports.
- Les traitements analytiques.
- La projection de données destinées à un tableau de bord.

L'attribution des XP peut aussi être asynchrone si l'application est conçue pour supporter un délai de cohérence. Il faut alors rendre explicite le statut de traitement et ne pas afficher une progression comme définitivement mise à jour avant que cela soit justifié.

### 3.3. Architecture de référence pour Skill-Tree

```text
                 Navigateur Skill-Tree
                           |
                           | HTTPS
                           v
                    ┌─────────────┐
                    │ FastAPI     │
                    │ Lab Workspace│
                    └──────┬──────┘
                           |
                           v
                Vérification du lab
                           |
                           v
                ┌──────────────────┐
                │ Base transactionnelle│
                │                  │
                │ Tentative        │
                │ Événement outbox │
                └────────┬─────────┘
                         |
                         v
                  Relais d'événements
                         |
                         v
                  ┌───────────────┐
                  │ File durable  │
                  └───────┬───────┘
                          |
             ┌────────────┼────────────┐
             v            v            v
        Traitement     Traitement   Traitement
        des XP         des badges   des notifications
             |            |            |
             v            v            v
        Statistiques   Progression   Service externe
```

Cette architecture est une proposition cible. Elle ne signifie pas que l'application actuelle est déjà organisée ainsi.

Le relais d'événements est responsable du transfert des événements enregistrés dans l'outbox vers le système de messagerie. Chaque consommateur doit gérer les échecs et les doublons.

### 3.4. Choisir une frontière de service

Il ne faut pas créer une fonction distincte pour chaque ligne de code.

Une fonction ou un service doit correspondre à une responsabilité suffisamment claire, avec des entrées, des sorties et des règles compréhensibles.

Exemples de responsabilités :

| Composant | Responsabilité |
|---|---|
| Soumission du lab | Vérifier et enregistrer une tentative. |
| Traitement des récompenses | Déterminer et appliquer les XP autorisés. |
| Traitement des badges | Évaluer les conditions d'attribution. |
| Notifications | Envoyer les messages et suivre leurs résultats. |
| Statistiques | Calculer les données destinées au tableau de bord. |

Il faut également éviter de transformer chaque composant en microservice indépendant sans bénéfice démontré. Un système trop fragmenté augmente le nombre d'interfaces, les besoins de surveillance et les difficultés de débogage.

## 4. Définir des contrats d'événements fiables

### 4.1. Qu'est-ce qu'un contrat d'événement ?

Un événement doit transporter suffisamment d'informations pour que son consommateur puisse comprendre ce qui s'est produit.

Il ne doit pas dépendre de variables conservées dans la mémoire d'une fonction précédente.

Dans Skill-Tree, le type d'événement pourrait être :

`lab.submitted`

Il indique qu'une tentative de lab a été enregistrée.

Exemple de structure :

```json
{
  "event_id": "lab.submitted:attempt-001",
  "event_type": "lab.submitted",
  "event_version": 1,
  "occurred_at": "2026-10-25T09:30:00Z",
  "data": {
    "attempt_id": "attempt-001",
    "user_id": "user-42",
    "lab_id": "ospf-3-routers",
    "passed": true,
    "xp_reward": 100
  }
}
```

Cet exemple illustre un contrat applicatif. Il ne prétend pas être un événement conforme à un fournisseur cloud particulier.

### 4.2. Identifiant d'événement et identifiant métier

Ces identifiants ne doivent pas être confondus.

**Identifiant de l'événement :** il identifie une occurrence logique de l'événement et permet de reconnaître sa nouvelle livraison.

**Identifiant de tentative :** il identifie la tentative de lab conservée par Skill-Tree.

Par exemple :

```text
event_id   = lab.submitted:attempt-001
attempt_id = attempt-001
```

Si le message est livré trois fois, il doit conserver le même identifiant d'événement.

En revanche, si l'utilisateur recommence le lab, il crée une nouvelle tentative et donc un nouvel événement.

Cette distinction est essentielle pour la déduplication.

### 4.3. Concevoir un événement indépendant

Un événement robuste doit :

- Posséder un identifiant stable.
- Identifier son type et sa version.
- Contenir un horodatage si celui-ci est utile au métier.
- Décrire les données nécessaires au traitement.
- Éviter les données confidentielles inutiles.
- Préciser les identifiants métier concernés.
- Être validé avant d'être traité.

Un événement ne doit pas contenir un mot de passe, un jeton d'accès ou une clé privée simplement parce que le consommateur pourrait en avoir besoin.

Les secrets doivent être obtenus auprès d'un gestionnaire de secrets ou d'une configuration sécurisée autorisée.

### 4.4. Faire évoluer le contrat sans casser les consommateurs

Imaginons que la version 1 comporte :

```json
{
  "attempt_id": "attempt-001",
  "lab_id": "ospf-3-routers",
  "passed": true
}
```

Dans la version 2, on souhaite ajouter :

```json
{
  "attempt_id": "attempt-001",
  "lab_id": "ospf-3-routers",
  "passed": true,
  "completion_duration_seconds": 420
}
```

L'ajout d'un champ facultatif peut être compatible avec les anciens consommateurs, à condition qu'ils ignorent les champs inconnus et ne supposent pas que la structure est strictement identique.

Les changements suivants sont plus risqués :

- Supprimer un champ existant.
- Modifier le type d'un champ.
- Changer le sens d'une valeur.
- Renommer un événement sans préparer les consommateurs.
- Rendre obligatoire un champ que les anciennes versions ne fournissent pas.

Une bonne stratégie consiste à documenter les contrats, ajouter les évolutions de manière compatible et tester les producteurs et consommateurs avant le déploiement.

## 5. Comprendre les garanties de livraison

### 5.1. Livraison au moins une fois

Un système de messagerie peut transmettre un événement une première fois, puis le retransmettre lorsqu'il ne reçoit pas la confirmation attendue.

Le destinataire peut donc recevoir le même événement plusieurs fois.

C'est une propriété importante des systèmes distribués : une nouvelle livraison ne signifie pas nécessairement que l'événement n'avait jamais été traité.

### 5.2. Livraison au plus une fois

Dans une stratégie au plus une fois, un événement n'est pas nécessairement retransmis après un échec.

Cette approche peut réduire le risque de duplication, mais elle peut aussi entraîner la perte d'un traitement si la stratégie de livraison ne garantit pas sa reprise.

Elle peut être acceptable pour certaines données non critiques, mais elle est généralement insuffisante pour garantir l'attribution de récompenses importantes.

### 5.3. Le problème du traitement exactement une fois

L'expression « exactement une fois » doit être utilisée avec précaution.

Un fournisseur peut proposer certaines garanties de déduplication ou de traitement, mais ces garanties ne s'étendent pas automatiquement à tous les systèmes concernés.

Imaginons ce scénario :

1. Une fonction reçoit un événement.
2. Elle attribue 100 XP dans la base de données.
3. Elle tombe en panne avant de confirmer le message.
4. La file retransmet l'événement.
5. Une nouvelle invocation tente d'attribuer les mêmes XP.

Même si la file possède certaines garanties de livraison, la base de données a déjà enregistré une modification lors de la première invocation.

La solution consiste à concevoir le traitement métier de façon à ce qu'une répétition ne crée pas d'effet supplémentaire.

La documentation AWS Lambda et celle d'Azure Functions détaillent les conséquences de ces mécanismes de livraison et l'importance de l'idempotence. Consulte notamment :

- [AWS Lambda — conception des applications et idempotence](https://docs.aws.amazon.com/lambda/latest/dg/concepts-application-design.html)
- [Azure Functions — traitement fiable des événements](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reliable-event-processing)
- [Google Cloud — nouvelles tentatives pour les fonctions événementielles](https://docs.cloud.google.com/run/docs/tips/function-retries)

## 6. L'idempotence à l'échelle métier

### 6.1. Définition

Une opération est idempotente lorsque sa répétition ne produit pas d'effet métier supplémentaire après l'application initiale.

Pour Skill-Tree, il faut notamment distinguer deux problèmes :

1. Le même événement est livré plusieurs fois.
2. L'utilisateur réalise plusieurs tentatives distinctes sur un lab déjà récompensé.

Ces situations ne sont pas identiques.

### 6.2. Dédupliquer le même événement

Une table de suivi peut conserver les identifiants des événements traités.

```text
                 Événement reçu
                        |
                        v
               Identifiant connu ?
                   /         \
                 Oui          Non
                  |            |
                  v            v
             Ignorer le     Traiter le
              doublon        contenu
                                |
                                v
                      Enregistrer le succès
```

La vérification et l'enregistrement de l'identifiant doivent être réalisés de manière atomique avec les effets métier qu'ils protègent.

### 6.3. Empêcher la double attribution d'XP

Même avec un identifiant d'événement unique, un utilisateur peut soumettre plusieurs tentatives différentes pour le même lab.

Exemple :

```text
Tentative A : lab réussi → 100 XP
Tentative B : lab réussi → 100 XP
Tentative C : lab réussi → 100 XP
```

Si Skill-Tree prévoit une récompense unique par lab et par utilisateur, le total attendu reste de 100 XP.

Une contrainte de base de données peut exprimer cette règle :

```sql
CREATE TABLE xp_rewards (
    user_id TEXT NOT NULL,
    lab_id TEXT NOT NULL,
    xp_awarded INTEGER NOT NULL,
    source_attempt_id TEXT NOT NULL UNIQUE,
    PRIMARY KEY (user_id, lab_id)
);
```

Cette structure garantit au niveau de la base qu'un utilisateur ne possède pas plusieurs lignes de récompense pour le même lab.

Une contrainte métier importante ne doit pas dépendre uniquement d'un contrôle effectué auparavant par le code : deux exécutions simultanées pourraient toutes deux constater que la récompense n'existe pas encore.

### 6.4. Une progression qui évolue à chaque nouvelle réussite

Tous les produits ne limitent pas les XP à une récompense unique.

Si Skill-Tree devait attribuer des XP à chaque nouvelle réussite, la clé d'unicité devrait plutôt porter sur la tentative ou sur un événement de récompense déterminé.

Le schéma de données doit traduire la véritable règle métier. Il ne faut pas adopter la règle « une récompense par lab » uniquement parce qu'elle est pratique dans un TP.

## 7. L'outbox transactionnelle

### 7.1. Le problème de la double écriture

Imaginons que FastAPI réalise ces deux opérations successives :

```text
1. Enregistrer la tentative dans SQLite.
2. Publier lab.submitted dans une file distante.
```

Un problème apparaît si la première opération réussit mais que la seconde échoue.

La tentative existe bien dans la base, mais aucun consommateur n'est informé.

Le problème inverse est également possible : un événement pourrait être publié sans que la transaction métier correspondante soit correctement enregistrée.

C'est ce qu'on appelle le problème de double écriture.

### 7.2. Le principe de l'outbox

L'outbox transactionnelle résout ce problème en enregistrant la modification métier et l'événement à publier dans la même transaction de base de données.

```text
                Transaction SQLite
                ┌─────────────────────┐
                │ Enregistrer tentative│
                │                     │
                │ Enregistrer événement│
                └──────────┬──────────┘
                           |
                     COMMIT unique
                           |
                           v
                    Données durables
                           |
                           v
                   Relais d'événements
                           |
                           v
                       File cloud
```

Si la transaction échoue, les deux écritures sont annulées.

Si elle réussit, l'événement reste disponible pour le relais, même si le service de messagerie est temporairement inaccessible.

Le relais peut réessayer la publication. Il faut toutefois accepter qu'un événement puisse être publié plusieurs fois si la publication a réussi mais que sa confirmation a été perdue.

L'outbox ne supprime donc pas le besoin d'idempotence.

Référence : [AWS Prescriptive Guidance — modèle d'outbox transactionnelle](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html).

### 7.3. Organisation des données

Une implémentation peut utiliser une table contenant :

| Champ | Rôle |
|---|---|
| `event_id` | Identifiant stable de l'événement. |
| `event_type` | Nature de l'événement. |
| `payload_json` | Données structurées à transmettre. |
| `status` | État de publication ou de traitement. |
| `attempts` | Nombre de tentatives de traitement. |
| `available_at` | Date à partir de laquelle un nouvel essai est autorisé. |
| `created_at` | Date de création. |
| `processed_at` | Date de réussite. |
| `last_error` | Dernière erreur diagnostique. |

Les états exacts dépendent de la conception. Dans notre TP, nous utiliserons `pending`, `retry`, `processed` et `dead_letter`.

Dans une véritable architecture, il faut distinguer le statut de publication vers la file du statut de traitement par le consommateur. Un relais ayant publié l'événement n'est pas nécessairement capable de savoir que chaque consommateur métier a terminé son travail.

## 8. Concevoir une stratégie de reprise sur erreur

### 8.1. Les erreurs transitoires et permanentes

Toutes les erreurs ne doivent pas être traitées de la même façon.

| Type d'erreur | Exemple | Stratégie |
|---|---|---|
| Erreur transitoire | Timeout d'une API ou indisponibilité temporaire | Réessayer selon une politique définie. |
| Erreur permanente | Contrat invalide ou champ obligatoire absent | Corriger ou mettre l'événement en échec définitif. |
| Limite de capacité | Base de données saturée ou service limité | Réduire la pression, surveiller et réessayer de façon contrôlée. |
| Erreur de programmation | Exception répétée due à un bug | Diagnostiquer et corriger avant une nouvelle tentative. |
| Erreur d'autorisation | Permission manquante | Corriger la configuration de sécurité plutôt que relancer sans limite. |

Une politique de reprise doit être adaptée à la nature de l'erreur. Répéter indéfiniment une opération invalide ne la rendra pas valide.

### 8.2. Backoff exponentiel

Lorsque les erreurs sont temporaires, on peut augmenter progressivement le délai avant chaque nouvelle tentative.

Une formule simple est :

\[
d_n = \min(d_{\max}, d_0 \times 2^{n-1})
\]

Avec :

- \(d_n\) : délai de la tentative numéro \(n\).
- \(d_0\) : délai initial.
- \(d_{\max}\) : délai maximal autorisé.

Exemple pour un délai initial de 2 secondes :

| Tentative | Délai indicatif |
|---|---:|
| 1 | 2 secondes |
| 2 | 4 secondes |
| 3 | 8 secondes |
| 4 | 16 secondes |
| 5 | 32 secondes |

En production, on ajoute souvent un facteur aléatoire appelé *jitter*. Cela évite que de nombreuses fonctions, déclenchées simultanément, effectuent toutes une nouvelle tentative au même instant.

Les politiques réelles varient suivant les mécanismes de déclenchement, le fournisseur et le service de messagerie. Il faut les vérifier dans la documentation du service utilisé.

### 8.3. La file d'échec définitif

Une file d'échec définitif, ou *dead-letter queue* (DLQ), conserve les messages qui ne peuvent pas être traités dans les conditions prévues.

Exemple :

```text
                 Message reçu
                       |
                       v
                Première tentative
                       |
                  Échec transitoire
                       |
                       v
                Nouvelle tentative
                       |
                  Échec transitoire
                       |
                       v
                Dernière tentative
                       |
                ┌──────┴───────┐
                |              |
              Succès          Échec
                |              |
                v              v
             Terminé       File DLQ
                               |
                               v
                       Diagnostic opérateur
                               |
                               v
                       Correction et rejeu
```

Une DLQ n'est pas une poubelle que l'on peut ignorer.

Elle doit être surveillée. Les messages doivent rester disponibles suffisamment longtemps pour permettre leur diagnostic, dans le respect des contraintes de stockage et de protection des données.

### 8.4. Rejouer un événement

Un rejeu consiste à demander un nouveau traitement d'un événement précédemment échoué.

Avant de le rejouer, il faut déterminer :

- Si le problème initial a été corrigé.
- Si le traitement a éventuellement eu un effet partiel.
- Si l'événement est encore pertinent.
- Si son identifiant doit rester le même.
- Si le consommateur sait gérer une nouvelle livraison.
- Si une ancienne version du contrat est encore supportée.

Il faut préférer une opération de rejeu explicite et traçable plutôt qu'une modification manuelle des données pour contourner une erreur.

## 9. Ordre des événements et concurrence

### 9.1. Pourquoi l'ordre est important

Certains traitements dépendent de l'ordre d'arrivée des événements.

Exemple :

```text
Événement A : progression passe à 80 %
Événement B : progression passe à 90 %
```

Si B est traité avant A, un consommateur qui remplace simplement la valeur actuelle par celle de l'événement pourrait rétablir une progression obsolète à 80 %.

Plusieurs solutions existent :

- Inclure un numéro de version ou de séquence.
- Enregistrer les changements de manière conditionnelle.
- Conserver un ordre par entité lorsque le service le permet.
- Calculer une progression à partir d'opérations idempotentes.
- Détecter les événements anciens ou incohérents.

L'ordre global de tous les événements n'est pas toujours nécessaire. Il faut déterminer le périmètre exact dans lequel l'ordre est important : utilisateur, tentative, lab ou autre entité métier.

### 9.2. Gérer plusieurs consommateurs

Une file d'attente permet de répartir le travail entre plusieurs instances.

```text
                 File d'attente
                       |
           ┌───────────┼───────────┐
           v           v           v
       Worker A    Worker B    Worker C
           |           |           |
           v           v           v
       Traitement  Traitement  Traitement
```

Cette organisation augmente la capacité de traitement lorsque les ressources en aval suivent le rythme.

Cependant, multiplier les workers ne garantit pas une amélioration des performances si tous se connectent à une même base de données limitée.

### 9.3. La pression sur les dépendances

Supposons que 1 000 événements soient disponibles et que chaque invocation tente d'ouvrir plusieurs connexions vers la base de données.

Une augmentation de la concurrence peut accroître les temps de réponse de la base, provoquer davantage de timeouts et entraîner encore plus de tentatives.

Ce cercle vicieux est une forme de surcharge amplifiée par les reprises.

Il faut contrôler :

- La concurrence maximale.
- La taille des lots de messages.
- Le nombre de connexions.
- Les délais d'attente.
- Les limites de débit des API externes.
- La taille de la file d'attente.
- Les règles de nouvelle tentative.

Une file d'attente sert notamment à dissocier la vitesse de production du travail de la vitesse de consommation. Elle ne rend pas les dépendances en aval infiniment extensibles.

### 9.4. Estimer la concurrence nécessaire

Une estimation simple peut être obtenue à partir du débit et de la durée moyenne.

\[
C \approx \lambda \times T
\]

Avec :

- \(C\) : nombre moyen d'exécutions simultanées.
- \(\lambda\) : nombre moyen de requêtes par seconde.
- \(T\) : durée moyenne d'une requête, en secondes.

Exemple :

Une fonction reçoit en moyenne 40 événements par seconde. Son traitement moyen dure 0,25 seconde.

\[
C \approx 40 \times 0{,}25 = 10
\]

Il faut donc environ 10 exécutions simultanées pour absorber ce débit moyen dans ces conditions.

Cette estimation ne suffit pas pour dimensionner une production. Il faut aussi tenir compte des pics de trafic, des percentiles de latence, des quotas, des limites des dépendances et de la charge des autres fonctions.

Référence complémentaire : [AWS Lambda — configuration de la concurrence réservée](https://docs.aws.amazon.com/fr_fr/lambda/latest/dg/configuration-concurrency.html).

## 10. Orchestration et chorégraphie

### 10.1. La chorégraphie événementielle

Dans une chorégraphie, chaque service réagit à des événements et produit éventuellement de nouveaux événements.

```text
Lab validé
    |
    v
Événement lab.submitted
    |
    ├──> Service XP
    |
    ├──> Service badges
    |
    └──> Service de notifications
```

Cette approche réduit les dépendances directes entre les composants.

Elle convient bien lorsque plusieurs opérations indépendantes doivent réagir au même fait métier.

Son principal défi est la compréhension du flux global : lorsque plusieurs composants publient des événements, il peut devenir difficile de savoir quelle étape a échoué et quelles autres opérations ont déjà été réalisées.

### 10.2. L'orchestration

Dans une orchestration, un composant central pilote les étapes d'un processus.

```text
               Workflow central
                      |
                      v
                Valider le lab
                      |
                      v
                 Enregistrer
                      |
                      v
                Attribuer XP
                      |
                      v
                Débloquer badge
                      |
                      v
                Notifier résultat
```

Le workflow conserve l'état de progression du processus et définit ce qui se passe en cas d'échec.

Cette approche est utile lorsqu'il existe des étapes ordonnées, des branches conditionnelles, des délais d'attente ou des compensations.

### 10.3. Les transactions distribuées et le modèle Saga

Une transaction SQL peut regrouper plusieurs écritures dans une même base.

En revanche, lorsqu'un processus modifie plusieurs services indépendants, il n'est pas toujours possible de réunir toutes les opérations dans une seule transaction atomique.

Le modèle Saga représente un processus comme une séquence d'étapes, chacune possédant éventuellement une action compensatoire.

Exemple de commande :

```text
Réserver le produit
        |
        v
Débiter le paiement
        |
        v
Préparer l'expédition
```

Si le paiement échoue après une réservation, le système peut libérer la réservation.

Dans Skill-Tree, une compensation peut parfois annuler un effet précédemment appliqué. Cependant, toutes les actions ne sont pas réversibles : un courriel envoyé ne peut généralement pas être rappelé.

Il faut donc définir explicitement les étapes, leurs conditions de réussite, leurs compensations et leurs garanties d'idempotence.

## 11. Sécurité des architectures serverless

### 11.1. Authentification et autorisation

L'authentification détermine qui appelle le système.

L'autorisation détermine ce que cet acteur a le droit de faire.

Dans le Lab Workspace, un utilisateur ne doit pas pouvoir modifier librement un identifiant pour consulter les tentatives privées d'un autre utilisateur ou s'attribuer lui-même des XP.

Le backend doit vérifier les droits d'accès à chaque opération sensible.

Une fonction interne déclenchée par une file d'attente doit également utiliser une identité et des permissions appropriées. Le fait qu'elle ne soit pas accessible publiquement ne la rend pas automatiquement sûre.

### 11.2. Ne pas faire confiance aux données du navigateur

Le navigateur peut proposer un résultat, mais il ne doit pas déterminer seul si le lab est réussi.

Le champ suivant ne constitue pas une preuve de réussite lorsqu'il est envoyé par un client :

```json
{
  "passed": true,
  "xp_reward": 1000
}
```

Le serveur doit vérifier la configuration à partir des règles de validation et de la définition du lab. Il doit déterminer lui-même la récompense autorisée.

C'est seulement après cette vérification que le backend peut enregistrer une tentative fiable et publier l'événement correspondant.

### 11.3. Permissions minimales

Chaque fonction doit posséder uniquement les permissions nécessaires.

Par exemple :

| Fonction | Permissions pertinentes |
|---|---|
| Vérification du lab | Lire les définitions autorisées et les données nécessaires. |
| Récompenses XP | Lire les événements et écrire les récompenses et statistiques nécessaires. |
| Notifications | Lire les événements concernés et appeler le fournisseur de messagerie. |
| Statistiques | Lire les données pertinentes et écrire les résultats analytiques. |

Il est préférable d'accorder des permissions spécifiques à un service et à une ressource plutôt qu'un accès administrateur global.

### 11.4. Protéger les secrets

Les clés API, identifiants de base de données et mots de passe ne doivent pas être inscrits directement dans le code source.

Ils doivent être gérés par un mécanisme de configuration sécurisé ou un gestionnaire de secrets.

Les journaux ne doivent pas contenir de secrets, de jetons d'accès ni de données personnelles inutiles.

### 11.5. Valider les événements internes

Un événement reçu par une fonction peut être malformé, ancien ou incompatible avec la version actuellement supportée.

Le consommateur doit vérifier sa structure, son type, ses identifiants et les contraintes métier pertinentes.

Dans un système réel, il faut aussi contrôler que l'événement provient d'un producteur autorisé, au moyen des mécanismes d'authentification et d'autorisation fournis par la plateforme.

## 12. Observabilité : savoir ce qui se passe en production

Une architecture composée de plusieurs fonctions ne peut pas être exploitée correctement si les erreurs sont invisibles.

### 12.1. Les journaux

Les journaux doivent répondre à des questions telles que :

- Quel événement a échoué ?
- Quelle fonction l'a traité ?
- Combien de tentatives ont été réalisées ?
- Quelle catégorie d'erreur a été rencontrée ?
- Quel composant en aval était impliqué ?

Pour faciliter le diagnostic, utilise des identifiants de corrélation stables, notamment `event_id`, `attempt_id` et un identifiant de requête.

Ne confonds pas un identifiant de corrélation avec un jeton d'authentification ou une donnée secrète.

### 12.2. Les métriques

Les métriques utiles incluent :

- Le nombre d'événements reçus.
- Le nombre d'événements traités avec succès.
- Le nombre d'échecs.
- La durée des exécutions.
- Le nombre de tentatives de reprise.
- Le nombre de messages en attente.
- Le nombre de messages en DLQ.
- Le taux d'erreurs des dépendances.
- Le coût par volume de traitements, lorsque les données nécessaires sont disponibles.

Le nombre de messages en attente est particulièrement important. Une fonction peut sembler saine au niveau de ses erreurs alors que la file d'attente augmente continuellement parce que le système consomme moins vite qu'il ne reçoit les messages.

### 12.3. Les traces distribuées

Une trace permet de suivre le parcours logique d'une opération entre plusieurs composants.

```text
Trace : validation d'un lab
  |
  +-- FastAPI : vérification
  |
  +-- SQLite : transaction de soumission
  |
  +-- Relais : publication
  |
  +-- Worker XP : traitement
  |
  +-- Base de données : mise à jour du total
```

Dans une architecture asynchrone, il faut transmettre le contexte de corrélation d'un composant au suivant. Les mécanismes de traçage distribués peuvent alors reconstituer le parcours sans supposer que toutes les opérations se déroulent dans une même requête HTTP.

### 12.4. Définir des objectifs de fiabilité

Un système doit être évalué à partir d'objectifs observables.

Exemples :

- Pourcentage de soumissions correctement enregistrées.
- Délai maximal acceptable avant l'attribution des XP.
- Durée acceptable de présence d'un événement dans la file d'attente.
- Délai de détection d'une accumulation de messages en DLQ.

Il ne faut pas confondre disponibilité de l'API, réussite d'une fonction et réussite du parcours métier complet.

Une API peut répondre avec succès alors qu'un traitement asynchrone est toujours en attente.

## 13. Performance et coûts

### 13.1. Réduire les démarrages coûteux

Un environnement d'exécution peut nécessiter une initialisation avant de traiter une nouvelle invocation. Cette phase peut ajouter de la latence.

Les optimisations courantes comprennent :

- Limiter les dépendances inutiles.
- Éviter les initialisations lourdes lorsque ce n'est pas nécessaire.
- Réutiliser prudemment les connexions et clients compatibles avec le runtime.
- Mesurer les performances avant de modifier l'architecture.
- Choisir le bon environnement d'exécution pour le type de charge.

La réutilisation d'un environnement n'est pas une garantie de persistance. Le code ne doit pas dépendre d'une invocation précédente pour fonctionner correctement.

### 13.2. Maîtriser les connexions à la base de données

Une fonction qui s'adapte rapidement à la charge peut créer un nombre élevé de connexions.

La base de données peut alors devenir le principal goulot d'étranglement.

Il faut donc étudier :

- Le nombre maximal de connexions.
- Les possibilités de mutualisation ou de pooling.
- La durée des transactions.
- Les index nécessaires.
- La taille des lots.
- Le niveau de concurrence des consommateurs.

SQLite est adapté à de nombreux usages locaux et embarqués. Il n'est pas automatiquement le meilleur choix pour une architecture distribuée comportant de nombreux workers concurrents et un stockage partagé. Le moteur de données doit être choisi en fonction du modèle de déploiement réel.

### 13.3. Mesurer le coût global

Le coût d'une architecture serverless peut inclure :

- Les invocations et le temps d'exécution.
- La mémoire ou les ressources consommées.
- Le stockage des données.
- Les opérations sur la base de données.
- Les files de messages.
- Les journaux et les traces.
- Le transfert réseau.
- Les mécanismes de disponibilité ou de capacité réservée.

Les échecs et les reprises consomment également des ressources.

Un bug qui provoque une boucle de nouvelles tentatives peut donc augmenter les coûts et saturer les dépendances.

Il faut définir des alertes de consommation, surveiller les volumes anormaux et examiner régulièrement les coûts par composant.

## 14. Tests et stratégie de déploiement

### 14.1. Les tests unitaires

Ils valident une logique métier de façon isolée.

Exemples :

- Une tentative réussie produit la bonne récompense.
- Une tentative échouée ne produit aucun XP.
- Une donnée invalide est rejetée.
- Un identifiant déjà utilisé ne crée pas une nouvelle tentative.

### 14.2. Les tests d'intégration

Ils vérifient que plusieurs composants fonctionnent ensemble.

Dans le TP, nous utiliserons SQLite pour vérifier que :

- Une tentative et son événement sont enregistrés correctement.
- Une récompense et les statistiques sont mises à jour dans une transaction.
- Une nouvelle livraison ne double pas les XP.
- Les états de reprise sont enregistrés.

Dans un environnement cloud, il faudra aussi vérifier les permissions, les formats de messages, les délais, les quotas et les interactions avec les services externes.

### 14.3. Les tests de contrat

Ils vérifient que les producteurs et consommateurs respectent les formats et les règles des événements.

Ils sont particulièrement utiles lorsqu'un service évolue indépendamment d'un autre.

### 14.4. Les tests de résilience

Ils simulent notamment :

- Une indisponibilité temporaire de la base de données.
- Un timeout de service externe.
- Une livraison répétée.
- Un événement invalide.
- Une accumulation de messages.
- Un dépassement du nombre maximal de tentatives.

Un système robuste doit rester cohérent lorsque ces situations surviennent.

### 14.5. Le pipeline CI/CD

Une chaîne d'intégration et de déploiement continu peut suivre ce parcours :

```text
Modification du code
        |
        v
Vérification du format
        |
        v
Tests unitaires
        |
        v
Tests d'intégration
        |
        v
Analyse de sécurité
        |
        v
Construction de l'artefact
        |
        v
Déploiement en environnement de test
        |
        v
Validation
        |
        v
Déploiement progressif
        |
        v
Surveillance et retour arrière si nécessaire
```

Les environnements de développement, de test et de production doivent utiliser des configurations distinctes.

Les changements d'infrastructure doivent idéalement être versionnés dans du code, au moyen d'un outil d'infrastructure as code tel que Terraform ou d'outils natifs du fournisseur cloud.

### 14.6. Déploiement progressif

Pour réduire le risque, il est possible de déployer une nouvelle version sur une partie du trafic ou de traiter un petit volume d'événements avant de généraliser le changement.

Il faut aussi prévoir les conséquences d'un retour arrière. Revenir à une ancienne version de code ne restaure pas automatiquement les données ou les effets métier déjà produits.

Les schémas de données et les contrats d'événements doivent donc être conçus pour favoriser des déploiements compatibles.

## 15. Traduire l'architecture vers les plateformes cloud

Les principes étudiés sont indépendants d'un fournisseur particulier, mais leur mise en œuvre concrète varie.

| Besoin | AWS | Microsoft Azure | Google Cloud |
|---|---|---|---|
| Exécuter des fonctions | AWS Lambda | Azure Functions | Cloud Run functions |
| Exécuter des services conteneurisés | Services de conteneurs managés selon le besoin | Azure Container Apps, entre autres | Cloud Run |
| File de messages | Amazon SQS | Azure Service Bus ou Queue Storage | Pub/Sub |
| Routage d'événements | Amazon EventBridge | Azure Event Grid | Eventarc |
| Stockage d'objets | Amazon S3 | Azure Blob Storage | Cloud Storage |
| Observabilité | Amazon CloudWatch et outils associés | Azure Monitor et Application Insights | Cloud Logging et Cloud Monitoring |
| Gestion des secrets | AWS Secrets Manager, entre autres | Azure Key Vault | Secret Manager |

Cette table présente des correspondances fonctionnelles, et non des services parfaitement interchangeables. Les garanties de livraison, mécanismes de reprise, quotas, options d'hébergement et modes de facturation dépendent des produits et de leurs configurations.

Pour un approfondissement pratique, consulte les documentations officielles :

- [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/)
- [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Cloud Run](https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run)

## 16. Travail pratique — Pipeline événementiel fiable pour le Lab Workspace

### Objectif

Ce TP reprend un scénario réaliste de Skill-Tree : un utilisateur soumet un lab, le backend enregistre la tentative, puis un traitement distinct gère les récompenses. Il permet d'expérimenter l'outbox transactionnelle, la publication vers une file simulée, l'idempotence, les tentatives de reprise et la file d'échec définitif (DLQ).

Le code du TP est stocké dans le dépôt afin de pouvoir être exécuté et testé :

- [Script principal — serverless_pipeline.py](https://github.com/biggyseven/Skill-Tree/blob/feature/lab-workspace/examples/serverless_intermediaire/serverless_pipeline.py)
- [Tests automatisés — test_serverless_pipeline_intermediaire.py](https://github.com/biggyseven/Skill-Tree/blob/feature/lab-workspace/tests/test_serverless_pipeline_intermediaire.py)

### 16.1. Préparer et exécuter le projet

Le TP nécessite Python 3.10 ou supérieur et utilise uniquement la bibliothèque standard. Aucune installation de dépendances n'est nécessaire.

Depuis la racine du dépôt Skill-Tree, exécute la démonstration :

~~~powershell
python examples/serverless_intermediaire/serverless_pipeline.py
~~~

Puis lance les tests automatisés :

~~~powershell
python -m unittest discover -s tests -p "test_serverless_pipeline_intermediaire.py" -v
~~~

Les tests utilisent des bases SQLite temporaires isolées. Le script de démonstration crée quant à lui le fichier skilltree_serverless_demo.db à côté du script. Le TP ne se connecte pas au backend FastAPI et ne lit ni ne modifie la base réelle skilltree.db.

### 16.2. Comprendre le flux

~~~text
Soumission validée côté serveur
             |
             v
   Transaction SQLite unique
   +--------------------------+
   | Tentative de lab         |
   | Événement dans l'outbox  |
   +--------------------------+
             |
             v
      Relais outbox simulé
             |
             v
       File locale simulée
             |
             v
    Consommateur idempotent
             |
       +-----+------+
       |            |
       v            v
   Récompense XP   Statut traité
       |
       v
   Total utilisateur
~~~

La tentative et l'événement outbox sont enregistrés dans une même transaction. Le relais copie ensuite les événements de l'outbox vers une file locale représentée par une autre table SQLite.

Cette file locale permet de pratiquer les mécanismes sans compte cloud. Elle ne remplace pas un broker distant : dans une vraie architecture, l'envoi vers un broker ne partage généralement pas la transaction de la base métier. Le relais doit donc tolérer les échecs et les publications répétées.

### 16.3. Rôle des fichiers et des tables

Le script principal contient le schéma et la logique de démonstration. Les tests automatisés vérifient les comportements attendus sans toucher à la base de démonstration de l'utilisateur.

| Élément | Rôle |
|---|---|
| **lab_attempts** | Historique des tentatives dont le résultat est déterminé côté serveur. |
| **outbox_events** | Événements à publier, enregistrés avec la tentative. |
| **queue_messages** | File locale qui simule les messages livrés aux consommateurs. |
| **processed_events** | Registre des identifiants déjà traités. |
| **xp_rewards** | Récompenses protégées par une contrainte d'unicité métier. |
| **user_stats** | Total d'XP de chaque utilisateur. |

La démonstration applique une règle pédagogique : une récompense par utilisateur et par lab. Les règles de récompense réelles de Skill-Tree doivent rester la source de vérité avant toute intégration au produit. Si chaque réussite doit donner des XP, il faut adapter la clé d'idempotence métier au lieu de conserver la règle du TP telle quelle.

### 16.4. Scénarios à observer

Lors de l'exécution, le script :

1. Enregistre la réussite de **ospf-3-routers**.
2. Publie l'événement outbox dans la file locale.
3. Simule une erreur temporaire pendant le traitement.
4. Réexécute le message pour montrer la reprise.
5. Simule la livraison répétée du même événement.
6. Enregistre une seconde tentative réussie sur le même lab.
7. Affiche le total final d'XP.

Le résultat attendu est 100 XP au total, pas 200. La seconde livraison du même événement est ignorée et la seconde tentative du même lab ne reçoit pas une récompense supplémentaire selon la règle simplifiée du TP.

### 16.5. États de traitement

| État ou résultat | Signification |
|---|---|
| **pending** | Le message attend son premier traitement. |
| **retry** | Une erreur temporaire a été rencontrée ; une reprise est planifiée. |
| **processed** | Le message a été traité. |
| **duplicate_ignored** | Le même événement avait déjà été traité par un autre message. |
| **already_rewarded** | L'utilisateur a déjà reçu la récompense de ce lab. |
| **dead_letter** | Le message est invalide ou a atteint la limite de reprises ; un diagnostic est nécessaire. |
| **not_due** | Le délai de reprise n'est pas encore écoulé. |

Le paramètre **force=True** est réservé au scénario de démonstration et aux tests : il permet de simuler l'écoulement du délai sans attendre. Un worker réel doit respecter le champ **available_at**.

### 16.6. Garanties et limites

- Les écritures de la tentative et de son événement outbox sont atomiques.
- Les statuts de reprise et les livraisons de démonstration sont enregistrés avec des transactions SQLite explicites.
- Les effets métier, le registre d'événements traités et le statut du message sont validés dans la même transaction locale.
- Les contraintes SQLite protègent contre les doublons d'identifiants et les récompenses répétées selon la règle pédagogique.
- Les erreurs temporaires utilisent un backoff exponentiel plafonné avec un facteur aléatoire.
- Les événements invalides vont en échec définitif plutôt que d'être réessayés sans fin.

Ce code reste un exercice. Il ne déploie pas de file AWS, Azure ou Google Cloud, ne s'intègre pas aux routes FastAPI et ne valide pas une topologie réseau réelle. Avant d'en faire un composant de production, il faut connecter les événements aux résultats de validation réels, confirmer les règles métier, déployer un broker durable, sécuriser les identités et ajouter les alertes et tests de résilience adaptés.

## 17. Prolongement du TP — Plan de déploiement cloud

Une prochaine étape de mise en œuvre consisterait à transposer les composants du TP vers des services managés.

Le schéma cible serait :

```text
                Backend FastAPI
                       |
                       v
               Base de données
                 + outbox
                       |
                       v
                Relais d'événements
                       |
                       v
                 File de messages
                       |
                       v
               Fonction de traitement
                       |
             ┌─────────┴─────────┐
             v                   v
       Base de données       Surveillance
        et récompenses        et alertes
```

Pour un déploiement réel, les étapes seraient :

1. Choisir le fournisseur et le moteur de données compatibles avec le volume et la concurrence visés.
2. Définir les contrats d'événements et les permissions de chaque composant.
3. Déployer la base, la file de messages et les fonctions avec de l'infrastructure as code.
4. Mettre en place le relais outbox et ses règles de reprise.
5. Vérifier l'idempotence dans le système de données réel.
6. Configurer les journaux, métriques, alertes et files d'échec définitif.
7. Exécuter les tests d'intégration et de résilience dans un environnement isolé.
8. Déployer progressivement et observer les résultats avant d'élargir le trafic.

Il ne faut pas brancher ce TP directement sur `skilltree.db` ni remplacer les endpoints actuels de Lab Workspace pour suivre cette leçon. Une migration de l'application réelle demanderait une analyse de ses règles métier existantes, de ses schémas de données et de ses garanties de persistance.

## 18. Exercices d'application corrigés

### Exercice 1 — Identifier une double écriture dangereuse

Un backend enregistre une tentative dans sa base, puis publie un message vers une file cloud. Si la publication échoue, la tentative est conservée, mais aucun consommateur ne reçoit l'événement.

**Question :** quel mécanisme peut réduire ce risque ?

**Correction :** utiliser une outbox transactionnelle afin d'enregistrer la tentative et l'événement dans la même transaction. Un relais indépendant peut ensuite réessayer la publication. Les consommateurs doivent toujours être idempotents, car une publication peut être répétée.

### Exercice 2 — Éviter une double récompense

Une fonction reçoit deux fois le même événement de tentative réussie. Chaque réception ajoute 75 XP au total.

**Question :** comment corriger le modèle ?

**Correction :** conserver un identifiant stable d'événement ou de tentative, vérifier les événements déjà traités et appliquer une contrainte d'unicité correspondant à la règle métier. La vérification de déduplication, l'enregistrement de la récompense et la modification du total doivent être effectués dans une transaction appropriée.

### Exercice 3 — Choisir la stratégie de reprise

Une fonction reçoit un événement contenant un champ obligatoire absent. L'exécution échoue à chaque fois.

**Question :** faut-il réessayer indéfiniment ?

**Correction :** non. Il s'agit d'une erreur de contrat probablement permanente. L'événement doit être rejeté ou placé en échec définitif après la validation appropriée, puis diagnostiqué. Les reprises automatiques sont surtout utiles pour les erreurs réellement transitoires.

### Exercice 4 — Protéger une base de données saturée

Un worker consomme 500 messages simultanément. La base de données devient lente, les timeouts augmentent et la file commence à se remplir davantage.

**Question :** faut-il augmenter encore le nombre de workers ?

**Correction :** pas sans diagnostic. Il faut examiner la capacité de la base, le nombre de connexions et la durée des transactions. Diminuer la concurrence, limiter la taille des lots ou lisser la charge peut être plus efficace qu'augmenter le nombre de fonctions.

### Exercice 5 — Compatibilité d'un contrat

Un producteur supprime le champ `lab_id`, alors que plusieurs consommateurs l'utilisent.

**Question :** quel risque cela crée-t-il ?

**Correction :** les consommateurs peuvent échouer ou ne plus pouvoir identifier le lab concerné. Il faut préparer une évolution compatible, éventuellement introduire le nouveau champ en parallèle, migrer les consommateurs, puis retirer l'ancien champ lorsque la compatibilité n'est plus nécessaire.

### Exercice 6 — Diagnostic d'un événement en DLQ

Un événement a échoué trois fois et se trouve dans la file d'échec définitif.

**Question :** quelle procédure appliquer avant son rejeu ?

**Correction :** consulter les journaux et l'erreur, vérifier le statut métier de la tentative, identifier si un effet a déjà été appliqué, corriger la cause, contrôler la validité du contrat et rejouer avec l'identifiant nécessaire à la déduplication.

## 19. Défi final — Concevoir le pipeline de progression de Skill-Tree

### Situation

Skill-Tree doit traiter les événements de réussite de labs de manière fiable. Plusieurs composants doivent réagir à une soumission :

- L'historique des tentatives doit être conservé.
- Les XP doivent être attribués conformément aux règles métier.
- Les badges doivent être déverrouillés lorsque leurs conditions sont satisfaites.
- Les statistiques doivent être actualisées.
- Les notifications doivent être envoyées.
- Les défaillances transitoires ne doivent pas entraîner une perte silencieuse du traitement.

### Travail demandé

Conçois une architecture et justifie tes choix en répondant à ces questions.

**1.** Que faut-il enregistrer dans la transaction initiale ?

**2.** Où faut-il publier l'événement et comment éviter le problème de double écriture ?

**3.** Comment empêcher les XP d'être attribués deux fois ?

**4.** Comment distinguer une erreur temporaire d'une erreur permanente ?

**5.** Que faut-il conserver dans la DLQ ?

**6.** Comment éviter qu'une surcharge de la base entraîne davantage d'échecs ?

**7.** Quels indicateurs faut-il surveiller ?

**8.** Comment tester la solution avant de la déployer ?

### Correction détaillée

#### 1. Transaction initiale

Le backend vérifie la soumission et détermine lui-même le résultat du lab. Il enregistre la tentative, puis l'événement à publier dans une même transaction.

Le statut de réussite et la récompense autorisée doivent provenir de la logique métier côté serveur, pas de données déclarées par le navigateur.

#### 2. Publication fiable

Le relais consulte les événements disponibles dans l'outbox et les transmet à la file de messages.

Le relais doit supporter les erreurs de publication et les nouvelles tentatives. Une éventuelle publication répétée est acceptable à condition que les consommateurs soient idempotents.

#### 3. Attribution des XP

Le consommateur vérifie l'identifiant de l'événement et les règles de déduplication.

Il vérifie également la contrainte métier qui définit si un utilisateur peut obtenir une nouvelle récompense pour un lab. La récompense et le total d'XP sont enregistrés de manière atomique.

#### 4. Gestion des erreurs

Les timeouts et certaines indisponibilités temporaires peuvent déclencher une reprise avec backoff et jitter.

Les événements invalides, incompatibles ou définitivement interdits doivent être traités comme des erreurs permanentes. Une reprise continue ne doit pas masquer la cause réelle.

#### 5. File d'échec définitif

Elle conserve les messages qui n'ont pas pu être traités selon la politique prévue, accompagnés des informations permettant le diagnostic.

Elle nécessite une surveillance, une procédure de correction et un processus de rejeu contrôlé.

#### 6. Protection des dépendances

Le système limite la concurrence, contrôle la taille des lots et surveille les temps de réponse de la base. La file permet de lisser la charge, mais le consommateur doit rester dimensionné selon les capacités des dépendances.

#### 7. Surveillance

Les indicateurs essentiels sont le temps de traitement, le taux d'erreur, le nombre de reprises, la taille de la file, le nombre de messages en DLQ, la durée d'attente des événements et les coûts.

Les identifiants de corrélation doivent permettre de suivre une soumission du backend au consommateur.

#### 8. Tests

Avant le déploiement, il faut exécuter les tests unitaires, les tests d'intégration, les tests de contrat et les tests de résilience.

Il faut notamment vérifier qu'une transaction interrompue n'enregistre pas une partie seulement des écritures, qu'un événement répété n'attribue pas de nouveaux XP et qu'un événement définitivement invalide n'est pas relancé sans limite.

### Architecture finale proposée

```text
                        Skill-Tree
                            |
                            v
                    FastAPI / Lab API
                            |
                            v
                    Vérification serveur
                            |
                            v
                  ┌─────────────────────┐
                  │ Transaction initiale│
                  │                     │
                  │ Tentative           │
                  │ Événement outbox    │
                  └──────────┬──────────┘
                             |
                             v
                       Relais outbox
                             |
                             v
                       File durable
                             |
                 ┌───────────┼───────────┐
                 v           v           v
             Worker XP   Worker badges  Worker stats
                 |           |           |
                 └───────────┼───────────┘
                             v
                    Persistance fiable

                   File d'échec définitif
                             |
                             v
                  Diagnostic et rejeu contrôlé

                   Observabilité transversale
                  Logs + métriques + traces
```

Cette architecture sépare les responsabilités et permet de reprendre les traitements asynchrones. Sa fiabilité repose toutefois sur l'implémentation exacte des transactions, de l'outbox, de l'idempotence, des permissions et de la surveillance.

## 20. Checklist de validation du niveau intermédiaire

Avant de passer au niveau expert, vérifie que tu sais :

- [ ] Expliquer la différence entre une requête synchrone et un événement asynchrone.
- [ ] Définir un contrat d'événement stable et versionné.
- [ ] Distinguer l'identifiant d'événement de l'identifiant métier.
- [ ] Expliquer pourquoi un message peut être livré plusieurs fois.
- [ ] Concevoir une fonction idempotente.
- [ ] Appliquer une contrainte d'unicité adaptée à une règle métier.
- [ ] Expliquer le problème de double écriture et le principe de l'outbox.
- [ ] Définir une stratégie de reprise avec backoff et jitter.
- [ ] Distinguer les erreurs transitoires et permanentes.
- [ ] Expliquer le rôle d'une DLQ.
- [ ] Identifier les risques associés à l'ordre et à la concurrence.
- [ ] Comprendre l'orchestration, la chorégraphie et le modèle Saga.
- [ ] Protéger les fonctions avec le principe du moindre privilège.
- [ ] Définir des métriques de fiabilité.
- [ ] Organiser une stratégie de tests et de déploiement progressif.
- [ ] Exécuter et comprendre le TP événementiel de Skill-Tree.

## 21. Documentation officielle pour approfondir

Les documentations suivantes permettent de passer de la conception à l'implémentation sur une plateforme cloud :

- [AWS Lambda — bonnes pratiques de conception](https://docs.aws.amazon.com/lambda/latest/dg/concepts-application-design.html)
- [AWS — modèle d'outbox transactionnelle](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- [AWS Lambda — comportement des nouvelles tentatives](https://docs.aws.amazon.com/us_en/lambda/latest/dg/invocation-retries.html)
- [Azure Functions — traitement fiable des événements](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reliable-event-processing)
- [Google Cloud — bonnes pratiques des fonctions](https://docs.cloud.google.com/run/docs/tips/functions-best-practices)
- [Google Cloud — configuration des reprises événementielles](https://docs.cloud.google.com/run/docs/tips/function-retries)

Consulte toujours la documentation correspondant au produit, au déclencheur et au mode de déploiement réellement choisis : les politiques de reprise et les garanties de livraison ne sont pas identiques partout.

## Conclusion

L'architecture serverless intermédiaire consiste à dépasser la simple exécution de fonctions pour construire un système fiable autour de celles-ci.

Les principaux acquis de ce niveau sont la gestion des contrats d'événements, l'idempotence, les reprises contrôlées, l'outbox transactionnelle, la protection des dépendances et l'observabilité.

Dans Skill-Tree, ces principes permettraient de séparer certaines opérations de progression du traitement direct des soumissions de labs, tout en protégeant la cohérence des données et les récompenses.

La règle fondamentale à retenir est la suivante : **un système événementiel robuste ne suppose ni que tous les traitements réussissent du premier coup, ni que chaque message n'arrive qu'une seule fois. Il conserve l'état nécessaire, rend les opérations idempotentes, sait reprendre les erreurs et rend les échecs observables.**
