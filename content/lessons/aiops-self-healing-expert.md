# Réseaux auto-cicatrisants — Expert

> **Mise en contexte :** un opérateur multisite subit des interruptions intermittentes. Les alertes arrivent en rafale, plusieurs équipes interviennent en parallèle et une action de correction peut aggraver la situation si elle s'applique au mauvais équipement. Le réseau auto-cicatrisant vise à détecter un écart, sélectionner une réponse sûre, vérifier le résultat et apprendre de l'exécution. Il ne s'agit ni d'un réseau qui se répare toujours seul ni d'une autorisation donnée à une IA d'exécuter n'importe quelle commande. Les manipulations de ce cours sont conçues pour un laboratoire isolé ; toute transposition en production exige une analyse de risque et une procédure approuvée.

## Sommaire

1. Objectifs et périmètre
2. Définir précisément l'auto-cicatrisation
3. Architecture de référence et boucle de contrôle
4. Observabilité, contexte et qualité des données
5. Diagnostic et sélection d'une action
6. Garde-fous, privilèges et rayon d'impact
7. Idempotence, préconditions et postconditions
8. Exécution, vérification et retour arrière
9. Politiques déterministes et composants d'IA
10. Architecture de déploiement
11. Implémentation guidée en Python
12. TP : concevoir une réponse sûre à une perte de connectivité
13. Tests, simulation et injection de pannes
14. Exploitation, métriques et amélioration continue
15. Dépannage et erreurs fréquentes
16. Exercices corrigés
17. Défi final corrigé
18. Checklist de mise en production et glossaire

## 1. Objectifs et périmètre

Un réseau auto-cicatrisant utilise une boucle de contrôle pour reconnaître un état anormal et appliquer, lorsque les conditions sont réunies, une action connue dont le résultat peut être vérifié. La boucle complète relie l'observation, le diagnostic, la décision, l'exécution, la mesure du résultat et l'apprentissage. Elle peut fonctionner entièrement avec des règles, avec des modèles statistiques, ou avec un mélange contrôlé de règles et de modèles. L'intelligence du système ne se mesure pas au nombre de commandes exécutées ; elle se mesure à la réduction des interruptions, à la précision des décisions et à l'absence d'effets secondaires inacceptables.

À la fin du cours, vous devez être capable de distinguer un système de réparation automatique d'un simple script de remédiation, de dessiner une architecture avec des frontières de confiance, de formuler des préconditions et des postconditions, d'établir une stratégie de retour arrière, de simuler des incidents et d'évaluer le comportement avec des indicateurs observables. Vous devez aussi pouvoir expliquer pourquoi certaines situations imposent une intervention humaine : données incohérentes, impact sur un service critique, action irréversible, confiance insuffisante ou situation jamais testée.

Ce cours suppose une connaissance des réseaux IP, des VLAN, du routage, des ACL, de la supervision et des scripts d'automatisation. Les exemples Python sont volontairement indépendants d'un constructeur. Ils illustrent le contrôle d'un plan de décision et n'établissent aucune session réelle sur un routeur. Pour utiliser une API ou un outil d'orchestration dans un environnement concret, il faudra ajouter une bibliothèque maintenue, l'authentification, les délais d'attente, la validation du certificat, les limites de débit et le traitement des erreurs propres à la plateforme.

### Vocabulaire de base

- **Auto-cicatrisation** : détection et correction contrôlée d'une dégradation, avec vérification indépendante du résultat.
- **Précondition** : état qui doit être vrai avant de tenter une action.
- **Postcondition** : état observable qui doit être vrai après l'action pour la considérer comme réussie.
- **Garde-fou** : contrôle qui limite les actions possibles ou leur portée.
- **Rayon d'impact** : ensemble des services, équipements et utilisateurs susceptibles d'être affectés.
- **Abstention** : décision explicite de ne pas agir automatiquement parce que la preuve ou l'autorisation est insuffisante.
- **Retour arrière** : procédure définie pour revenir à un état sûr connu, quand cela reste possible.
- **Mode fantôme** : le système calcule et journalise une recommandation sans l'exécuter.

## 2. Définir précisément l'auto-cicatrisation

L'auto-cicatrisation n'est pas un attribut binaire. Un dispositif peut automatiser la collecte tout en laissant les humains diagnostiquer, puis automatiser seulement les actions à faible risque. Une progression maîtrisée commence par l'observation, continue par la recommandation et l'approbation, puis autorise certaines actions bornées lorsque leur innocuité a été démontrée. Les opérations qui ont un impact important restent soumises à une autorisation proportionnée au risque.

### 2.1 Les niveaux d'autonomie

| Niveau | Comportement | Exemple | Contrôle humain |
|---|---|---|---|
| 0 — Observation | Collecte et corrélation sans recommandation | Afficher un pic d'erreurs CRC | L'opérateur interprète |
| 1 — Assistance | Présenter des hypothèses et des tests | Proposer de vérifier l'optique et le câble | L'opérateur décide |
| 2 — Action approuvée | Préparer une action puis attendre une validation | Générer un changement de préférence de route | Approbation avant application |
| 3 — Autonomie bornée | Exécuter une action connue dans un périmètre autorisé | Réessayer une collecte ou fermer une session de test | Supervision et seuils d'arrêt |
| 4 — Boucle adaptative gouvernée | Réviser les modèles et politiques à partir de résultats contrôlés | Ajuster un seuil après validation | Gouvernance formelle, audits et contrôle des versions |

Ces niveaux ne représentent pas une échelle obligatoire. Une entreprise peut autoriser une remédiation de niveau 3 dans un environnement de laboratoire et garder une opération similaire au niveau 1 sur un réseau de production. Le périmètre, la criticité du service, les obligations métier et la capacité à revenir à un état sûr priment sur le désir d'autonomie.

### 2.2 Script de remédiation ou boucle fermée ?

Un script traditionnel peut être déclenché manuellement pour redémarrer un service lorsqu'un opérateur connaît déjà la cause. Une boucle fermée vérifie en plus si le signal initial est valable, si les conditions de sécurité sont réunies, si le service a réellement récupéré et si l'action doit être stoppée. Elle enregistre la décision, ses preuves et le résultat. Sans mesure postérieure à l'action, la réussite est seulement supposée.

Prenons un lien qui affiche une hausse d'erreurs. Un script naïf pourrait désactiver puis réactiver le port à chaque alerte. La boucle de contrôle se demande d'abord si la télémétrie est fraîche, si une maintenance est en cours, si les erreurs sont localisées, si le port transporte un service critique et si une opération similaire a déjà échoué. Elle choisit ensuite un diagnostic non disruptif, ou s'abstient si les conditions sont inconnues.

### 2.3 Ce que le système ne doit pas promettre

Une architecture sérieuse annonce ses limites. Elle ne garantit pas l'absence de panne, ne déduit pas toujours la cause racine d'une corrélation et ne peut pas compenser une télémétrie absente sans signaler l'incertitude. Un modèle peut classer un incident comme probable ; cela ne constitue pas une preuve que l'action suggérée est sûre. Des dépendances non recensées, des changements simultanés ou une panne de la plateforme d'orchestration peuvent empêcher toute correction automatique.

Le bon objectif est de réduire le délai de détection et le délai de restauration sur un périmètre défini, tout en gardant un taux d'actions incorrectes sous une limite explicite. Il est préférable qu'un système s'arrête proprement et escalade plutôt que d'insister jusqu'à épuisement des tentatives.

## 3. Architecture de référence et boucle de contrôle

Une architecture de référence sépare au minimum la collecte, l'analyse, la politique de décision, l'exécution, la vérification et l'audit. Ces composants peuvent être déployés dans un même service pour un petit laboratoire, mais leurs responsabilités doivent rester distinctes dans le code et les permissions. Séparer les rôles réduit le risque qu'une erreur d'analyse produise directement une commande sans contrôle intermédiaire.

~~~mermaid
flowchart TD
  A[Équipements et services] --> B[Collecteurs de télémétrie]
  B --> C[Normalisation et horodatage]
  C --> D[Détection et contexte]
  D --> E[Moteur de politique]
  E -->|Preuve insuffisante| F[Abstention et escalade]
  E -->|Action autorisée| G[Exécuteur à privilèges limités]
  G --> H[Équipement ciblé]
  H --> I[Vérification indépendante]
  I -->|Postcondition vraie| J[Clôture et journal d'audit]
  I -->|Échec ou état inconnu| K[Arrêt, rollback ou intervention humaine]
  K --> F
  J --> L[Mesures et retour d'expérience]
  F --> L
~~~

Le moteur de politique ne doit pas être confondu avec un modèle de diagnostic. Un composant peut générer une hypothèse ou un score, alors que la politique vérifie si l'opération est permise. La séparation empêche un texte convaincant, un score élevé ou une sortie inattendue d'élargir automatiquement les droits d'action.

### 3.1 Collecteurs

Les collecteurs récupèrent les métriques, les journaux, les états de configuration, les événements de changement, les alarmes, les résultats de tests actifs et l'inventaire. Ils doivent préserver l'origine des données, l'heure de collecte, l'heure d'événement si elle existe, l'identité de l'équipement et la qualité du signal. Une valeur n'est pas fiable simplement parce qu'elle a été reçue en JSON : il faut contrôler son type, son unité et sa fraîcheur.

Le collecteur ne doit pas posséder de droits de modification lorsqu'il n'a besoin que de lecture. Si un agent de collecte compromis peut aussi configurer les routeurs, une faiblesse dans le traitement de données augmente immédiatement le risque opérationnel. Les identifiants de collecte sont distincts des identifiants d'exécution et la rotation des secrets doit être possible sans redéployer tous les agents.

### 3.2 Normalisation et contexte

Les constructeurs n'emploient pas toujours les mêmes noms de champs, unités ou formats d'alarme. La normalisation transforme les observations en un modèle commun, tout en conservant le message source et sa provenance. Elle ne doit pas effacer les différences qui sont nécessaires au diagnostic. Un signal peut être marqué « manquant », « en retard », « suspect » ou « valide », plutôt que transformé silencieusement en zéro.

Le contexte enrichit les observations par la topologie, les dépendances métier, les fenêtres de maintenance, les changements récents, les versions et les propriétaires des services. Le contexte doit être daté : une topologie d'hier ne décrit pas nécessairement un réseau après une migration. Une dépendance inconnue doit rester inconnue. Dans le doute, le rayon d'impact est estimé prudemment et l'autonomie peut être réduite.

### 3.3 Moteur de politique

La politique décrit les conditions d'entrée et de sortie d'une action. Elle peut exiger plusieurs signaux indépendants, un périmètre explicitement autorisé, l'absence de changement concurrent, un quota de remédiations et une période sans nouvelle tentative après un échec. Elle vérifie aussi si un opérateur a gelé les automatismes pendant une intervention.

Une règle de sécurité doit être déterministe autant que possible. Si une action n'est autorisée que lorsque cinq conditions sont réunies, ces cinq conditions doivent être évaluables et journalisées. Un modèle génératif peut aider à expliquer les données ou proposer un test, mais il ne remplace pas le contrôle des préconditions.

### 3.4 Exécuteur

L'exécuteur applique une action identifiée par une liste d'autorisations explicites. Il refuse les commandes libres, les cibles non déclarées, les paramètres hors limites et les actions non réversibles dans le mode concerné. Les délais d'attente sont bornés, les erreurs sont capturées et les tentatives sont limitées. Il doit aussi interrompre une exécution lorsque le contrôleur central perd sa capacité à suivre l'état.

Une opération ne doit pas être réessayée de manière aveugle. Certaines opérations sont idempotentes : leur répétition laisse le même état final. D'autres provoquent des effets cumulés, comme l'envoi de multiples demandes de bascule ou la suppression répétée de ressources. L'exécuteur doit connaître cette différence et utiliser des clés d'idempotence ou une lecture d'état préalable lorsque c'est possible.

## 4. Observabilité, contexte et qualité des données

La boucle de contrôle ne peut être meilleure que les signaux qu'elle reçoit. Une alarme isolée peut provenir d'un défaut réel, d'une collecte en retard, d'un compteur réinitialisé ou d'un changement planifié. L'observation doit être replacée dans sa série temporelle et comparée aux autres indicateurs. L'objectif n'est pas de collecter tout ce qui est disponible, mais de collecter suffisamment de preuves pour trancher une question opérationnelle.

### 4.1 Quatre catégories de données utiles

1. **Métriques** : utilisation CPU, mémoire, pertes, latence, erreurs d'interface, occupation des files et disponibilité des services.
2. **Journaux et événements** : changements de configuration, erreurs de protocole, authentifications, redémarrages et alarmes.
3. **État et inventaire** : versions, relations de voisinage, tables de routage, configurations déclarées, rôles et dépendances métier.
4. **Tests actifs** : ping contrôlé, mesure de latence, résolution DNS, vérification TLS, transaction synthétique ou test de chemin.

Ces sources répondent à des questions différentes. Une interface peut sembler active au niveau physique, alors qu'une transaction applicative échoue. Un ping réussi ne démontre pas qu'un service utilise le bon chemin, et un test synthétique peut être affecté par son propre point de mesure. Une stratégie robuste combine une preuve au niveau infrastructure avec une preuve au niveau du service, lorsque cela est possible.

### 4.2 Horodatage, fenêtrage et valeurs manquantes

Les horloges doivent être synchronisées, et le pipeline doit distinguer l'heure à laquelle un événement s'est produit de l'heure à laquelle il a été observé. Les données tardives doivent être traitées explicitement. Une alerte reçue après le rétablissement du service ne devrait pas déclencher la même action qu'une alerte en temps réel.

Le fenêtrage résume un intervalle : moyenne, maximum, quantile, nombre de changements, ou proportion de pertes. La taille de la fenêtre dépend du phénomène. Une fenêtre trop courte amplifie le bruit ; une fenêtre trop longue masque un incident bref. La politique doit être testée pour plusieurs durées et plusieurs profils de trafic.

Une valeur absente n'est pas synonyme de valeur normale. L'absence de collecte peut justement signaler un problème d'agent, de réseau de gestion ou d'authentification. Lorsqu'une métrique critique est inconnue, l'action doit généralement être bloquée ou remplacée par une vérification de la chaîne de collecte.

### 4.3 Définir un indicateur fiable

Pour chaque indicateur, documentez le nom, l'unité, la source, le niveau d'agrégation, la cadence, la fraîcheur maximale, le comportement en cas de manque et la méthode de validation. Si le système utilise « taux de perte », précisez s'il s'agit d'un test actif, d'un compteur d'interface ou d'une estimation applicative. Sans cette précision, deux valeurs numériquement identiques peuvent représenter des phénomènes différents.

Une baseline permet de comparer le comportement à une situation de référence. Elle peut être spécifique à un site, une interface, une période de la journée ou un type d'équipement. Évitez cependant de considérer qu'une référence historique est toujours normale : si le réseau était déjà dégradé pendant la période d'apprentissage, le modèle normalisera une mauvaise situation.

## 5. Diagnostic et sélection d'une action

Le diagnostic produit des hypothèses classées, pas une vérité magique. Une cause candidate doit être associée aux preuves qui la soutiennent, aux éléments qui la contredisent, à un niveau d'incertitude et à un test discriminant. Le test discriminant est une observation qui aide à choisir entre deux explications proches. Cette approche évite de passer directement de « la latence augmente » à « redémarrer le routeur ».

### 5.1 Construire un arbre de décision sûr

Pour une hausse de latence, l'arbre pourrait commencer par confirmer le phénomène depuis plusieurs points de mesure. Il vérifie ensuite la charge, les erreurs d'interface, les changements récents, la santé des chemins et les dépendances applicatives. Si un lien présente des erreurs physiques en même temps que les pertes, le système peut recommander une inspection du lien. Si les métriques de collecte sont absentes, il commence par restaurer la visibilité plutôt que de modifier le réseau.

Un arbre est utile parce que chaque branche possède des critères vérifiables. Il reste limité par les cas qu'il a anticipés. Une analyse statistique peut suggérer des relations inattendues, mais la politique d'action doit revenir à une liste d'opérations approuvées. Un modèle ne doit pas inventer une commande à partir d'une sortie de terminal ou d'un texte non fiable.

### 5.2 Scoring et seuil de confiance

Un score agrège plusieurs éléments, mais sa signification doit être définie. Il peut s'agir d'une probabilité calibrée sur des incidents étiquetés, d'un score d'anomalie ou d'une heuristique. Ces valeurs ne sont pas interchangeables. Un score d'anomalie de 0,9 ne signifie pas qu'il existe 90 % de probabilité d'une panne, sauf si la méthode a été calibrée pour cette interprétation.

Les seuils doivent tenir compte des coûts des erreurs. Une fausse alerte peut mobiliser un opérateur ; une fausse correction peut interrompre tout un site. Le seuil d'autonomie est donc généralement plus élevé que le seuil qui déclenche une enquête. Il faut mesurer séparément la qualité du diagnostic et la qualité de la décision d'action.

### 5.3 La règle d'abstention

Le système doit s'abstenir lorsque les données nécessaires sont périmées, que le périmètre dépasse la politique, qu'une action concurrente est en cours, que le changement serait difficile à annuler ou que des signaux se contredisent sans moyen de trancher. L'abstention est un état normal du système, à instrumenter et à mesurer, et non une panne de conception.

Une décision « je ne sais pas » utile explique ce qui manque : absence d'état avant modification, télémétrie interrompue, fenêtre de maintenance non disponible ou cause candidate insuffisamment discriminée. L'escalade doit inclure un résumé des preuves et la prochaine vérification recommandée afin de ne pas transférer seulement une alerte brute.

## 6. Garde-fous, privilèges et rayon d'impact

La sécurité s'applique avant l'action. Les comptes doivent disposer du strict minimum de droits, et l'exécuteur doit vérifier qu'une cible appartient à un inventaire autorisé. L'authentification forte, la séparation des rôles, le stockage de secrets adapté, la rotation des identifiants et les journaux d'audit sont nécessaires dès que l'automatisation touche un réseau réel.

### 6.1 Allowlist d'actions

Une liste blanche décrit les opérations permises, leurs paramètres et les contextes qui les autorisent. Elle est plus sûre qu'un filtre qui essaie de retirer les commandes dangereuses d'un langage de commande général. Dans le laboratoire, une opération pourrait être « renouveler une collecte de télémétrie » ou « lancer un test de connectivité ». Les opérations « effacer la configuration », « recharger un équipement » ou « modifier globalement une ACL » ne doivent pas être disponibles dans le profil de remédiation automatique sans contrôle exceptionnel.

L'exécuteur reçoit un nom d'action et des paramètres typés, plutôt qu'une chaîne shell libre. Il rejette les clés inconnues et valide chaque champ. Le modèle de diagnostic peut proposer une action sémantique, mais il ne détient ni le secret ni le droit d'exécuter une commande arbitraire.

### 6.2 Rayon d'impact et budgets d'action

Une opération est évaluée selon le nombre d'équipements touchés, la criticité du service, la dépendance à une fenêtre de maintenance, la réversibilité et les effets sur les chemins de secours. Le contrôle le plus sûr peut être de limiter une première action à un seul équipement non critique, d'observer le résultat, puis d'étendre progressivement.

Le budget d'action limite le nombre de remédiations, leur fréquence et leur portée. Par exemple, une politique peut autoriser une tentative par équipement sur une fenêtre donnée et imposer une pause après un échec. Les valeurs exactes relèvent de la politique de l'organisation ; elles doivent être configurées, expliquées et testées, et ne pas être copiées aveuglément depuis un exemple de cours.

### 6.3 Arrêt d'urgence

Le mécanisme d'arrêt doit être indépendant du modèle, accessible aux opérateurs autorisés et testé régulièrement. Il peut désactiver l'exécution automatique tout en conservant la collecte et la recommandation. Un arrêt bien conçu ne doit pas détruire les traces de diagnostic ni bloquer les procédures manuelles de restauration.

Il faut tester l'arrêt dans trois situations : avant l'envoi d'une action, pendant une exécution longue et après application mais avant la vérification. Le système doit savoir reconnaître quel état a été atteint. Si l'état réel ne peut pas être déterminé, il doit déclarer l'exécution incertaine et déclencher une vérification humaine, plutôt que de faire comme si rien ne s'était passé.

## 7. Idempotence, préconditions et postconditions

Une action idempotente peut être répétée sans multiplier les effets. Déclarer une configuration souhaitée peut être idempotent lorsque l'outil compare l'état courant à la cible et n'applique que la différence. Envoyer plusieurs fois une opération de bascule non protégée ne l'est pas nécessairement. La conception doit rechercher l'idempotence, tout en documentant les limites des API et des équipements concernés.

### 7.1 Exemple de contrat d'action

Une action « réparer le chemin de secours » doit avoir un contrat écrit comprenant :
- **Entrées** : identifiant d'équipement, nom d'une politique autorisée, identifiant d'incident.
- **Préconditions** : équipement dans l'inventaire, données fraîches, changement non gelé, état courant connu, chemin de secours disponible.
- **Effet attendu** : appliquer une modification restreinte définie par la politique.
- **Postconditions** : voisinage stable, route attendue présente, test de service réussi, absence d'augmentation des erreurs.
- **Échecs** : refus de précondition, délai d'attente, résultat partiel, vérification impossible.
- **Retour arrière** : restaurer la configuration précédente ou désactiver l'action et escalader si la restauration n'est pas sûre.

Ces éléments empêchent une API qui répond « HTTP 200 » d'être considérée comme une preuve suffisante. Le serveur peut avoir accepté la requête sans avoir terminé la configuration. Une réponse peut également concerner une commande mise en file d'attente. La preuve de résultat doit provenir d'une observation indépendante de l'accusé de réception.

### 7.2 Préconditions optimistes et verrouillage

Entre la lecture de l'état et la modification, un opérateur ou un autre contrôleur peut changer la configuration. L'exécuteur doit relire l'état ou utiliser une version attendue lorsque l'API le permet. Si la version ne correspond plus, il annule la modification automatique et demande une nouvelle évaluation.

Le verrouillage logique évite que deux remédiations concurrentes agissent sur la même ressource. Un verrou doit avoir une durée limitée et un mécanisme de récupération si le propriétaire disparaît. Le système ne doit pas rester bloqué indéfiniment parce qu'un processus a été interrompu. Toutefois, retirer un verrou sans vérifier l'état réel peut créer un conflit encore plus dangereux.

## 8. Exécution, vérification et retour arrière

Chaque action passe par une séquence observable : préparation, validation, approbation éventuelle, exécution, attente bornée, contrôle de postconditions et clôture. Les transitions sont enregistrées avec une heure et un identifiant de corrélation. Un état comme « résultat inconnu » est indispensable : l'absence de réponse ne prouve pas que l'équipement n'a rien appliqué.

### 8.1 Retour arrière avant et après un effet

Certaines actions sont annulables en restaurant une configuration connue ; d'autres ne peuvent pas être parfaitement inversées. Avant une opération, enregistrer un état de référence et vérifier la validité de la méthode de restauration. Il faut notamment considérer les effets indirects : une route peut être restaurée tandis que des sessions applicatives restent interrompues.

Le rollback ne doit pas être une simple commande exécutée à l'aveugle. Il suit lui aussi des préconditions, une portée, un délai d'attente et des postconditions. Si la situation a évolué entre l'action et le rollback, restaurer l'ancien état peut aggraver l'incident. Le moteur doit comparer l'état actuel à l'état attendu et solliciter une intervention humaine lorsque la restauration sûre n'est pas démontrée.

### 8.2 Vérification indépendante

La preuve de rétablissement doit être différente du signal qui a déclenché l'action. Si l'alerte provient d'un compteur d'interface, vérifier uniquement ce compteur peut ne pas suffire. Il est préférable d'ajouter un test de service, une mesure de latence de bout en bout et l'absence de nouvelle alarme sur une fenêtre définie.

La fenêtre de stabilité importe. Un lien qui revient pendant cinq secondes puis retombe n'est pas nécessairement réparé. La durée doit être adaptée au service et aux temps de convergence. La postcondition comprend donc à la fois un état et une période pendant laquelle cet état reste valide.

## 9. Politiques déterministes et composants d'IA

Les modèles statistiques sont utiles lorsqu'ils détectent des motifs complexes dans la télémétrie ; les systèmes de règles restent utiles lorsqu'une condition est connue et qu'une décision doit être explicable. Un LLM peut synthétiser un dossier d'incident ou reformuler une hypothèse, mais il peut inventer une réponse plausible. Il ne doit pas avoir l'autorité de modifier la politique d'exécution à la volée.

### 9.1 Séparer les responsabilités

Une architecture hybride peut se répartir ainsi :
- le modèle classe les incidents et propose des hypothèses ;
- la recherche récupère les runbooks pertinents avec leurs versions et permissions ;
- le moteur de politique vérifie l'action autorisée ;
- l'exécuteur réalise uniquement les opérations déclarées ;
- le vérificateur mesure le résultat réel ;
- l'audit conserve l'ensemble des preuves.

Cette séparation crée une frontière claire entre langage naturel et action technique. Les données d'entrée peuvent contenir des chaînes malveillantes, des commandes collées dans les journaux ou des instructions dissimulées dans des tickets. Tout contenu provenant des équipements ou des utilisateurs doit être traité comme une donnée, jamais comme une autorisation.

### 9.2 Validation des recommandations d'un LLM

Le modèle ne doit pas recevoir des secrets s'ils ne sont pas nécessaires à son analyse. Son résultat est contraint par un schéma : hypothèse, références de preuve, incertitudes, tests proposés et actions candidates parmi un ensemble autorisé. Les références doivent être contrôlées par l'application ; une citation inventée est un échec de vérification, pas une preuve.

Un résultat qui ne respecte pas le schéma, qui propose un équipement inconnu ou qui contredit les preuves est rejeté ou envoyé à un opérateur. Le système doit tester les hallucinations, les attaques par injection d'instructions, les données sensibles dans les journaux et les comportements sur les cas ambigus. L'IA n'élargit jamais les permissions de l'exécuteur.

## 10. Architecture de déploiement

En production, séparer les plans de gestion et de service, utiliser des identités de service distinctes et prévoir la panne du moteur central. Les agents ne doivent pas continuer à exécuter indéfiniment les dernières décisions si le contrôle central devient indisponible. Une politique locale sûre peut autoriser une petite liste d'actions, mais le mode de repli doit être explicite.

Un déploiement par étapes réduit le risque :
1. enregistrer les observations sans produire de recommandation ;
2. afficher des recommandations en mode fantôme ;
3. demander un avis d'opérateur et comparer ses décisions aux recommandations ;
4. autoriser une action sur un équipement de test ;
5. étendre à un petit périmètre avec suivi rapproché ;
6. revoir les incidents et les abstentions avant chaque extension.

Chaque étape possède des critères de sortie. Un taux élevé de recommandations acceptées ne suffit pas si les incidents graves augmentent. Il faut comparer aux procédures existantes, évaluer les faux positifs et faux négatifs, vérifier la traçabilité, tester le rollback et conserver une procédure manuelle praticable.

## 11. Implémentation guidée en Python

Le programme suivant simule le moteur de politique. Il n'ouvre aucune connexion réseau et n'envoie aucune commande. Son but est d'apprendre à distinguer un signal, une autorisation, une tentative d'action et la preuve de réussite.

~~~python
from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class Decision(str, Enum):
    EXECUTE = "execute"
    ABSTAIN = "abstain"
    REJECT = "reject"


@dataclass(frozen=True)
class Observation:
    target: str
    loss_pct: float | None
    observed_age_seconds: int
    maintenance_active: bool
    target_is_approved: bool
    recent_action_failed: bool
    service_criticality: str


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str
    action: str | None = None


ALLOWED_TARGETS: FrozenSet[str] = frozenset({"lab-edge-01", "lab-edge-02"})
MAX_DATA_AGE_SECONDS = 30


def decide(obs: Observation) -> PolicyResult:
    """Décide uniquement si un diagnostic non disruptif est autorisé."""
    if obs.target not in ALLOWED_TARGETS or not obs.target_is_approved:
        return PolicyResult(Decision.REJECT, "Cible absente de la liste autorisée")
    if obs.observed_age_seconds < 0 or obs.observed_age_seconds > MAX_DATA_AGE_SECONDS:
        return PolicyResult(Decision.ABSTAIN, "Télémétrie absente ou trop ancienne")
    if obs.maintenance_active:
        return PolicyResult(Decision.ABSTAIN, "Fenêtre de maintenance active")
    if obs.recent_action_failed:
        return PolicyResult(Decision.ABSTAIN, "Une action récente a échoué")
    if obs.loss_pct is None or not 0 <= obs.loss_pct <= 100:
        return PolicyResult(Decision.ABSTAIN, "Valeur de perte invalide ou inconnue")
    if obs.service_criticality == "critical":
        return PolicyResult(Decision.ABSTAIN, "Validation humaine obligatoire")
    if obs.loss_pct >= 5:
        return PolicyResult(Decision.EXECUTE, "Perte élevée confirmée", "run_read_only_diagnostics")
    return PolicyResult(Decision.ABSTAIN, "Seuil de déclenchement non atteint")


if __name__ == "__main__":
    example = Observation(
        target="lab-edge-01",
        loss_pct=8.2,
        observed_age_seconds=5,
        maintenance_active=False,
        target_is_approved=True,
        recent_action_failed=False,
        service_criticality="standard",
    )
    print(decide(example))
~~~

Le nom run_read_only_diagnostics est volontairement symbolique. Pour brancher un outil réel, il faut créer une interface distincte dont les opérations permises sont définies et testées. Il ne faut pas transformer ce nom en exécution d'une chaîne arbitraire reçue en entrée.

### 11.1 Tests unitaires des règles

~~~python
import unittest


class PolicyTests(unittest.TestCase):
    def observation(self, **changes):
        values = dict(
            target="lab-edge-01",
            loss_pct=8.2,
            observed_age_seconds=5,
            maintenance_active=False,
            target_is_approved=True,
            recent_action_failed=False,
            service_criticality="standard",
        )
        values.update(changes)
        return Observation(**values)

    def test_approved_case_requests_diagnostics(self):
        result = decide(self.observation())
        self.assertEqual(result.decision, Decision.EXECUTE)
        self.assertEqual(result.action, "run_read_only_diagnostics")

    def test_stale_data_abstains(self):
        result = decide(self.observation(observed_age_seconds=100))
        self.assertEqual(result.decision, Decision.ABSTAIN)

    def test_unknown_target_is_rejected(self):
        result = decide(self.observation(target="unknown-router"))
        self.assertEqual(result.decision, Decision.REJECT)

    def test_critical_service_requires_human(self):
        result = decide(self.observation(service_criticality="critical"))
        self.assertEqual(result.decision, Decision.ABSTAIN)

    def test_missing_metric_abstains(self):
        result = decide(self.observation(loss_pct=None))
        self.assertEqual(result.decision, Decision.ABSTAIN)


if __name__ == "__main__":
    unittest.main()
~~~

Lancez les tests dans un environnement Python isolé. Ajouter un test pour chaque règle explicite, puis des tests de limites : valeur à zéro, valeur à cent, âge des données égal à trente secondes et âge juste supérieur à trente secondes. Une bonne suite teste autant le comportement attendu que le refus d'agir.

## 12. TP : concevoir une réponse sûre à une perte de connectivité

### Scénario

Deux équipements de laboratoire relient un réseau utilisateur à un service interne. Une alarme signale une perte de paquets de 8 %. Vous disposez d'un compteur de pertes, de l'état des interfaces, d'un historique des changements et d'un test synthétique. Une maintenance peut être en cours, et le service est parfois classé critique.

### Étape A — Formuler l'objectif

Ne choisissez pas une action avant d'avoir défini le résultat recherché. Ici, l'objectif est de confirmer la dégradation puis de rétablir un niveau acceptable sans interrompre un service critique. Définissez une fenêtre de mesure, une fraîcheur maximale pour les données, un seuil de déclenchement et une durée de stabilité après le test.

### Étape B — Établir les preuves

Réunissez au moins :
- le taux de perte de plusieurs points de mesure ;
- l'état du lien et le compteur d'erreurs physiques ;
- les changements récents et l'existence d'une maintenance ;
- un test applicatif ou une sonde de bout en bout ;
- le propriétaire du service et son niveau de criticité.

Si l'une des preuves déterminantes est manquante, marquez le cas comme incomplet. Ne remplacez pas une donnée absente par zéro.

### Étape C — Décrire les actions

Classez les opérations par risque. Lire les compteurs et lancer une sonde appartiennent généralement aux actions non disruptives. Modifier une route, réinitialiser une interface ou redémarrer un équipement sont des opérations plus risquées. Dans le premier prototype, ne retenez automatiquement que le diagnostic en lecture seule et l'escalade.

### Étape D — Préconditions et postconditions

Avant tout test, vérifiez la cible, la fraîcheur, l'autorisation, la maintenance et l'absence d'une action concurrente. Après le diagnostic, vérifiez que les mesures ont été prises sur la bonne cible et qu'elles couvrent une fenêtre cohérente. Si une remédiation future est approuvée, exigez un résultat indépendant et un plan de retour arrière.

### Étape E — Faire le compte rendu

Documentez l'heure, le signal d'origine, la cible, les données manquantes, la décision, la raison du refus éventuel, l'action exécutée et le résultat. Un opérateur qui reprend l'incident doit pouvoir comprendre pourquoi le système a agi ou s'est abstenu sans lire l'ensemble du code.

### Critères de réussite du TP

Le TP est réussi si toutes les décisions sont explicables, qu'une donnée périmée bloque l'action, qu'une cible inconnue est refusée, que la criticité force une validation humaine et que la réussite n'est jamais déclarée sans postcondition observée. L'action simulée doit être reproductible et ne doit pas modifier un équipement réel.

## 13. Tests, simulation et injection de pannes

Les tests unitaires vérifient chaque règle isolément. Les tests d'intégration vérifient que les composants transmettent correctement les données, les identités et les états d'exécution. Les tests de bout en bout rejouent un incident représentatif depuis le signal de départ jusqu'à la clôture. Aucun test isolé ne garantit la sécurité globale : chaque couche peut fonctionner correctement tout en composant avec une hypothèse invalide d'une autre couche.

### 13.1 Matrice de scénarios

| Situation | Comportement attendu | Résultat à vérifier |
|---|---|---|
| Perte confirmée, données fraîches, cible autorisée | Diagnostic en lecture seule | Décision et preuve journalisées |
| Données trop anciennes | Abstention | Aucune action envoyée |
| Cible inconnue | Rejet | Aucun accès à la cible |
| Maintenance active | Abstention | Motif explicite |
| Service critique | Validation humaine | Pas d'exécution autonome |
| Deux actions concurrentes | Mise en attente ou abstention | Pas de course entre contrôleurs |
| Timeout après commande | État inconnu puis vérification | Pas de répétition aveugle |
| Postcondition fausse | Arrêt et escalade | Pas de clôture comme succès |
| Rollback indisponible | Refus de l'action risquée | Incident escaladé |
| Signal contradictoire | Demande de preuve supplémentaire | Aucune conclusion forcée |

### 13.2 Chaos engineering dans un périmètre sûr

Une injection de panne doit reproduire une hypothèse précise : collecte interrompue, délai réseau, état de configuration divergent ou panne de l'orchestrateur. L'expérience doit avoir une portée définie, un responsable, un arrêt d'urgence et des critères d'abandon. Ne provoquez pas de panne sur une infrastructure partagée sans autorisation, ni dans un environnement dont les mécanismes de reprise ne sont pas connus.

La question n'est pas seulement « le système a-t-il réparé ? ». Il faut demander s'il a reconnu sa perte de visibilité, s'il a évité une action hors périmètre, s'il a signalé un résultat incertain et si l'opérateur a conservé la capacité de reprendre la main. Une réponse sûre peut consister à ne rien modifier et à escalader.

### 13.3 Tester les défaillances de la boucle elle-même

La plateforme de remédiation peut être en panne alors que le réseau fonctionne, ou le réseau de gestion peut être indisponible pendant que le plan de service est opérationnel. Les scénarios doivent aussi inclure la perte d'accès au registre de secrets, une erreur du moteur de politique, un journal d'audit saturé, un résultat de test retardé et un modèle indisponible.

Chaque composant doit avoir une stratégie de repli. L'indisponibilité du LLM ne doit pas désactiver les règles de sécurité. L'indisponibilité de l'audit peut imposer le blocage d'actions risquées, puisque la traçabilité est elle-même une précondition de gouvernance.

## 14. Exploitation, métriques et amélioration continue

Mesurer le nombre d'actions automatiques n'indique pas leur valeur. Il faut combiner des mesures de service, de qualité du diagnostic, de sécurité et d'efficacité opérationnelle. La métrique principale reste liée au résultat métier : disponibilité, temps de restauration, expérience utilisateur ou respect du SLA.

Indicateurs utiles :
- délai moyen entre le début d'une dégradation détectable et sa détection ;
- durée entre la détection et la restauration vérifiée ;
- part des incidents résolus sans interruption supplémentaire ;
- proportion de recommandations acceptées après examen ;
- taux de faux positifs et faux négatifs ;
- proportion d'actions dont les postconditions ont été confirmées ;
- nombre de rollbacks, d'abstentions et d'escalades ;
- taux de récurrence de l'incident après la correction ;
- impact des actions sur les services non ciblés.

Il faut segmenter les indicateurs par criticité, site, constructeur, type d'incident et niveau d'autonomie. Une moyenne qui s'améliore peut masquer une baisse de qualité sur les équipements anciens ou sur un site isolé. Pour les événements rares, examiner chaque cas grave et compléter les métriques agrégées par un retour d'expérience qualitatif.

### 14.1 Événements d'audit

Pour chaque décision, consignez l'identifiant d'incident, les signaux utilisés, les versions du modèle et de la politique, le périmètre, la décision, les raisons, l'approbation éventuelle, l'action, la réponse, les postconditions et la clôture. Ne stockez pas inutilement des secrets ou des données personnelles. Les journaux doivent avoir des droits d'accès, une politique de conservation et une protection contre l'altération.

### 14.2 Apprendre sans normaliser les erreurs

Après une action, l'équipe doit comparer la prédiction au résultat réel. Si la remédiation a échoué, identifier si la cause provient des données, du diagnostic, de la politique, de l'exécution ou de la vérification. Il ne faut pas immédiatement entraîner un modèle sur chaque résultat nouveau : les labels doivent être validés et les incidents ambigus revus par un expert.

Toute modification de politique suit une revue de changement. Les actions précédemment autorisées peuvent devenir risquées après une évolution de topologie ou de service. Les tests de non-régression doivent rejouer les incidents passés, notamment les cas dans lesquels une action avait été correctement refusée.

## 15. Dépannage et erreurs fréquentes

### Le système déclenche des actions sur des alarmes fantômes

Contrôlez l'horodatage, les duplications, la remise à zéro des compteurs, la qualité des collecteurs et les changements de maintenance. Ajoutez des exigences de corroboration et une période d'observation. N'augmentez pas arbitrairement le seuil pour masquer le problème, car cela peut faire disparaître les vrais incidents.

### Le système répète une action sans résultat

Inspectez les clés d'idempotence, les délais d'attente, les états intermédiaires et les postconditions. Un timeout peut survenir après l'application réelle de la commande. Avant une nouvelle tentative, relisez l'état courant et décidez si l'opération peut être répétée sans effet cumulatif.

### La correction rétablit un lien mais casse une application

Le test de postcondition est incomplet ou la dépendance applicative n'est pas représentée. Ajoutez une sonde de service, révisez le rayon d'impact et comparez les effets avant et après. Le réseau peut être stable au niveau physique tout en violant une exigence applicative.

### Le modèle fournit une action convaincante mais dangereuse

Le modèle n'est pas un moteur d'autorisation. Contraignez sa sortie, validez les cibles et les paramètres, et faites passer toute proposition par la politique déterministe. Rejouez des cas adverses et mesurez le taux de refus correct.

### La boucle s'arrête sans explication

Chaque branche de décision doit produire un code de raison stable. Distinguez refus, abstention, erreur technique, timeout et résultat inconnu. Un tableau de bord doit montrer le dernier état atteint, plutôt que d'afficher un simple statut « échec ».

### Le retour arrière échoue

Vérifiez que l'état initial a été sauvegardé, que sa version est cohérente et qu'aucun changement concurrent ne rend la restauration dangereuse. Si l'état est incertain, geler les actions automatiques et escalader. Ne jamais multiplier les commandes de restauration pour forcer un résultat non compris.

## 16. Exercices corrigés

### Exercice 1 — Distinguer détection et preuve

Un modèle estime à 92 % qu'une congestion est la cause d'une dégradation. L'interface est pourtant stable, et aucune mesure applicative n'est disponible. Peut-on appliquer automatiquement une bascule ?

**Correction :** non. Il faut d'abord comprendre la nature du score : probabilité calibrée ou score arbitraire. Les preuves sont contradictoires ou incomplètes et la mesure applicative manque. Le système doit s'abstenir d'une action disruptive et demander un test discriminant. Une confiance numérique n'annule pas les préconditions.

### Exercice 2 — Timeout après application

Une API d'orchestration expire après avoir soumis un changement. Quelle est la bonne première réaction ?

**Correction :** classer le résultat comme inconnu, consulter l'état réel et l'identifiant de la tâche si disponible, puis vérifier les postconditions. Ne pas répéter directement l'opération : la première requête a pu être appliquée malgré l'absence de réponse. Une nouvelle tentative n'est possible qu'après avoir déterminé l'état et établi que l'opération est idempotente ou protégée contre les doublons.

### Exercice 3 — Service critique et politique permissive

Le modèle recommande une correction sur un équipement qui porte un service critique. La règle autorise la correction si la confiance dépasse 0,9.

**Correction :** la règle est insuffisante. La criticité doit intervenir comme garde-fou indépendant. Il faut exiger une approbation, des préconditions spécifiques, un plan de retour arrière testable et une vérification de bout en bout. Le seuil du modèle ne doit jamais annuler une contrainte de sécurité.

### Exercice 4 — Mauvais indicateur de succès

Le taux d'erreur d'une interface revient à zéro après intervention, mais les utilisateurs signalent toujours un échec applicatif.

**Correction :** la postcondition est trop faible. Il faut combiner état du réseau et vérification du service concerné. La clôture attend une stabilité pendant une fenêtre pertinente et doit enregistrer les signaux contradictoires. Si le test applicatif reste en échec, l'incident demeure ouvert.

### Exercice 5 — Trop d'abstentions

Le système s'abstient très souvent lorsque les données arrivent avec du retard.

**Correction :** mesurer le retard et son origine avant de relâcher le garde-fou. Améliorer la collecte, surveiller la fraîcheur et définir des limites adaptées à chaque métrique. Une donnée trop ancienne ne devient pas fiable parce que le taux d'abstention est gênant. L'amélioration doit rendre le signal plus frais ou proposer un diagnostic alternatif non disruptif.

## 17. Défi final corrigé

### Énoncé

Vous devez concevoir une première boucle de remédiation pour un réseau multisite. Trois problèmes sont observés : pertes de paquets sur un lien, erreurs DNS intermittentes et collecte de métriques parfois indisponible. Les équipes veulent automatiser la restauration, mais un mauvais changement peut isoler une agence. La disponibilité d'un service transactionnel est prioritaire.

Rendez un mini-dossier qui comprend l'architecture, les préconditions, la sélection des actions, le mécanisme d'arrêt et les critères de succès. Vous ne devez pas fournir une commande universelle permettant de modifier tous les équipements.

### Proposition de correction

**Architecture.** Les collecteurs en lecture seule envoient des données horodatées à un pipeline qui normalise les événements et vérifie leur fraîcheur. Un moteur d'analyse génère des causes candidates. Un moteur de politique détermine les opérations autorisées. Un exécuteur séparé dispose de droits limités à une liste blanche. Un vérificateur indépendant teste les postconditions. Le système d'audit conserve preuves, décisions et versions.

**Pertes de paquets.** Corroborer les mesures depuis plusieurs points, inspecter erreurs physiques et changements récents, puis lancer un test actif. Si les données sont fraîches, la cible approuvée et le service non critique, un diagnostic en lecture seule peut être automatique. Toute bascule de chemin exige un contrat d'action propre au réseau et, au départ, une validation humaine.

**Erreurs DNS.** Comparer résolution depuis plusieurs résolveurs et postes, contrôler la fraîcheur des caches, les changements de zone et la disponibilité des serveurs. Ne pas redémarrer tous les résolveurs à partir d'un seul échec. La postcondition doit être une résolution correcte et stable depuis les points représentatifs, ainsi qu'une transaction applicative réussie.

**Collecte indisponible.** Le système ne doit pas interpréter l'absence de données comme la santé du réseau. Il doit bloquer les changements qui dépendent du signal manquant et tenter une vérification indépendante de l'agent ou du canal de gestion. Si la visibilité ne peut pas être restaurée, il escalade et reste en mode sans action disruptive.

**Garde-fous.** Allowlist de cibles, privilèges minimaux, fenêtre de maintenance, limites de fréquence, prévention des actions concurrentes, approbation pour les services critiques, timeout borné, audit obligatoire et bouton d'arrêt indépendant. Toute sortie d'un modèle reste une proposition soumise à validation.

**Critères de succès.** Les incidents sont détectés plus vite sans hausse des interruptions liées à l'automatisation ; les postconditions sont mesurées ; la cause probable est séparée des preuves ; les abstentions sont explicables ; les changements sont traçables ; les tests de rollback et d'arrêt d'urgence passent avant l'ouverture de l'autonomie.

**Décision de mise en service.** Démarrer en mode fantôme, comparer pendant une période représentative les recommandations au travail des opérateurs, tester les cas de panne et faire approuver les seuils par les propriétaires de service. L'autonomie n'est étendue qu'après validation des résultats et des échecs, pas sur la seule base d'une démonstration réussie.

## 18. Checklist de mise en production et glossaire

### Checklist

- [ ] Objectif opérationnel et indicateurs définis avec les propriétaires de service.
- [ ] Données sourcées, horodatées, contrôlées et soumises à une règle de fraîcheur.
- [ ] Valeurs absentes et états inconnus représentés explicitement.
- [ ] Actions strictement listées et typées ; aucune commande libre issue d'un modèle.
- [ ] Privilèges minimaux, secrets protégés et identités séparées.
- [ ] Préconditions, postconditions, délai maximal et résultat incertain documentés.
- [ ] Idempotence ou protection contre les répétitions démontrée.
- [ ] Rayon d'impact et budget d'action limités.
- [ ] Arrêt d'urgence et procédure manuelle testés.
- [ ] Rollback testé et adapté à l'état actuel.
- [ ] Vérification indépendante au niveau service.
- [ ] Tests unitaires, intégration, bout en bout et cas adverses réussis.
- [ ] Journaux d'audit protégés et sans secrets inutiles.
- [ ] Mode fantôme et déploiement progressif exécutés.
- [ ] Responsables d'astreinte, escalade et critères d'arrêt identifiés.

### Glossaire rapide

**Boucle fermée :** boucle de contrôle qui mesure le résultat et adapte la suite en fonction de cette mesure. **Dérive :** évolution des données ou des relations qui peut réduire la qualité du modèle. **État inconnu :** situation dans laquelle le système ne peut pas prouver ce que l'action a produit. **Mode fantôme :** recommandation sans exécution. **Postcondition :** preuve que le résultat attendu est atteint. **Précondition :** état préalable nécessaire à l'action. **RCA :** analyse de cause racine. **Rollback :** restauration contrôlée d'un état sûr. **Rayon d'impact :** périmètre potentiellement affecté. **Idempotence :** propriété d'une opération dont la répétition ne multiplie pas l'effet.

### Pour approfondir

- NIST, AI Risk Management Framework : https://www.nist.gov/itl/ai-risk-management-framework
- OpenTelemetry, documentation : https://opentelemetry.io/docs/
- gNMI, spécification et modèles de données : https://github.com/openconfig/gnmi
- Ansible, documentation officielle : https://docs.ansible.com/
- Python, documentation officielle : https://docs.python.org/3/

L'idée essentielle de ce cours est simple : une action automatique n'est acceptable que si la cible est autorisée, les preuves suffisantes, les effets bornés et le résultat vérifié. L'abstention et l'escalade font partie intégrante d'un réseau auto-cicatrisant fiable.