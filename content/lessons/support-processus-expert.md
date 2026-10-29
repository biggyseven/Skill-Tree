# Définition des processus support : créer un service prévisible, mesurable et améliorable

> **Mise en contexte**
>
> Les incidents se perdent rarement parce que personne ne connaît le bouton « fermer ». Ils se perdent lorsque les responsabilités, les états, les critères de décision et les chemins d'escalade sont ambigus. Un processus support bien conçu donne à chaque demande un chemin explicite, sans imposer la même procédure rigide à toutes les situations. Au niveau expert, l'objectif est de concevoir des processus sûrs, testables et adaptés à la réalité opérationnelle.

## 1. Qu'est-ce qu'un processus support ?

Un processus décrit comment une entrée déclenche un ensemble d'activités coordonnées pour produire un résultat. Il définit le déclencheur, les rôles, les étapes, les règles de décision, les données nécessaires, les exceptions et les critères de sortie. Une procédure détaille plutôt une manière d'exécuter une tâche ; un mode opératoire peut décrire les clics ou commandes exacts. Les trois doivent être cohérents, mais ils ne sont pas interchangeables.

Un processus ne doit pas être conçu pour reproduire exactement l'organigramme. L'utilisateur pense en termes de tâche ou d'interruption métier, pas en termes de frontières internes entre équipes. Le processus doit fournir une continuité visible même lorsque plusieurs groupes interviennent.

Avant d'ajouter un formulaire ou une validation, clarifiez le résultat attendu. Une validation supplémentaire peut réduire le risque, mais peut aussi ajouter un délai. La gouvernance doit expliquer pourquoi le contrôle existe, qui en est responsable et comment les urgences sont traitées sans supprimer les protections essentielles.

## 2. Distinguer les flux ITSM

Un service mature distingue les types de travail qui exigent des contrôles différents.

- **Incident** : rétablir un service perturbé et limiter l'impact.
- **Demande de service** : fournir un service standard défini, comme un logiciel autorisé ou un accès approuvé.
- **Gestion des problèmes** : analyser les causes d'incidents récurrents ou majeurs et réduire leur réapparition.
- **Changement** : évaluer et contrôler une modification d'un service ou de son environnement.
- **Connaissance** : créer, valider, publier, réviser et retirer une information de référence.
- **Accès** : traiter l'attribution et la révocation des droits selon les approbations et contrôles requis.

Ces catégories ne sont pas de simples étiquettes de reporting. Elles influencent les approbations, les priorités, la preuve attendue et les règles de clôture. Un incident critique ne doit pas attendre le même chemin qu'une demande d'installation planifiée ; un changement d'accès privilégié ne doit pas être traité comme une question de procédure courante.

~~~mermaid
flowchart TD
    A[Demande entrante] --> B[Triage et qualification]
    B --> C{Nature du besoin}
    C -->|Service interrompu| I[Processus incident]
    C -->|Service standard demandé| R[Demande de service]
    C -->|Répétition ou cause incertaine| P[Processus problème]
    C -->|Modification planifiée| H[Processus changement]
    I --> V[Validation du résultat]
    R --> V
    P --> K[Actions de prévention]
    H --> V
    V --> C
~~~

Le processus peut relier des enregistrements : plusieurs incidents peuvent être rattachés à un problème ; un incident peut être lié à un changement récent ; un article de connaissance peut documenter une solution temporaire. Ces liens permettent la continuité et une analyse plus solide.

## 3. Cartographier le flux avant de l'automatiser

Commencez par observer le processus réel, y compris les échanges informels, les feuilles de calcul et les contournements. Construisez une carte « actuel » avec les étapes, les acteurs, les files d'attente et les décisions. Les temps d'attente doivent être distingués du temps de travail actif : un dossier peut être traité pendant vingt minutes mais attendre plusieurs jours une approbation.

La méthode SIPOC aide à cadrer le périmètre : fournisseurs, entrées, processus, sorties et clients. Une carte de flux aide à voir les boucles, doublons et transferts. Ces outils sont des aides de discussion ; ils ne remplacent pas l'observation et la validation auprès des équipes qui exécutent le travail.

~~~mermaid
flowchart LR
    A[Fournisseurs : utilisateur, supervision] --> B[Entrées : symptôme, contexte, preuve]
    B --> C[Qualification]
    C --> D[Diagnostic et action]
    D --> E[Validation avec le demandeur]
    E --> F[Sortie : service confirmé et ticket tracé]
    F --> G[Client : utilisateur et responsable du service]
~~~

Documentez les exceptions. Une carte qui ne représente que le parcours idéal sera contournée dans la pratique. Ajoutez les cas d'information manquante, de doublon, de refus d'approbation, de fournisseur indisponible, de panne de l'outil de tickets et de demande urgente. Pour chaque exception, définissez une voie de traitement et un propriétaire.

## 4. Concevoir les états, transitions et critères de sortie

Les états doivent décrire une réalité compréhensible : nouveau, qualifié, en cours, en attente d'une partie externe, résolu, fermé ou annulé, selon le modèle. Les transitions doivent avoir des conditions précises. « En attente » ne devrait pas être un état fourre-tout : distinguez si possible l'attente utilisateur, fournisseur ou changement planifié, afin de suivre les délais réels.

Un état ne remplace pas l'information. Un ticket « en cours » doit posséder un responsable, un prochain pas et une date de revue. Un ticket « résolu » doit contenir la solution appliquée, les preuves de vérification et la confirmation selon la règle établie. La fermeture automatique doit se comporter de manière transparente, tenir compte des risques et conserver les événements utiles.

Définissez des transitions interdites ou soumises à autorisation. Par exemple, un incident critique ne peut pas être clos sans vérification du service, et un changement à risque peut nécessiter une validation indépendante. Une règle doit être testée sur les cas limites, pas seulement sur le parcours heureux.

~~~mermaid
stateDiagram-v2
    [*] --> Nouveau
    Nouveau --> Qualifie
    Qualifie --> EnCours
    EnCours --> EnAttente
    EnAttente --> EnCours
    EnCours --> Resolu
    Resolu --> Ferme
    Resolu --> EnCours: Réouverture justifiée
    Nouveau --> Annule: Demande invalide confirmée
    Ferme --> [*]
~~~

## 5. Définir des responsabilités et des contrôles

Attribuez au processus un propriétaire responsable de sa finalité, de ses définitions, de ses indicateurs et de ses évolutions. Les responsables d'étape exécutent les activités ; les équipes spécialisées apportent leur expertise ; la sécurité et les métiers valident les contrôles relevant de leur autorité. Le propriétaire de processus ne doit pas décider seul de contourner les politiques.

Une matrice RACI rend explicites les décisions qui provoquent le plus souvent des retards : priorisation, approbation des accès, changement, escalade fournisseur, communication d'incident majeur et clôture. Limitez les contrôles en double. Lorsque deux groupes réalisent la même vérification sans raison claire, examinez si l'une des étapes peut être supprimée ou si les deux répondent à des risques distincts.

Le processus doit conserver une piste d'audit proportionnée : qui a changé l'état, à quel moment, pourquoi, quelle approbation a été donnée et quelle preuve soutient la décision. La trace doit rester accessible aux personnes autorisées et éviter la collecte de données personnelles inutiles.

## 6. Relier SLA, priorités et engagements

Un SLA exprime un engagement de service ; un objectif opérationnel interne peut organiser la contribution de plusieurs équipes à cet engagement. Définissez clairement la mesure : prise en charge, première réponse utile, résolution ou rétablissement. Indiquez le calendrier de service, les priorités, les pauses autorisées et les exclusions. Un indicateur dont la définition varie entre équipes ne peut pas soutenir une comparaison fiable.

La priorité doit être fondée sur l'impact et l'urgence selon les règles approuvées, pas uniquement sur le statut hiérarchique du demandeur. Des voies adaptées peuvent exister pour les rôles critiques, mais elles doivent être documentées et contrôlées. Ne changez pas la priorité uniquement pour rendre le rapport plus favorable.

Mesurez les écarts et leurs causes : attentes d'approbation, compétence rare, dépendance fournisseur, information initiale incomplète ou demande supérieure à la capacité. Une cible de délai ne corrige pas automatiquement la contrainte. Si l'équipe accélère en supprimant un contrôle nécessaire, le processus a été rendu moins sûr.

## 7. Automatiser avec des garde-fous

L'automatisation est pertinente pour le tri, le routage, les notifications, la détection de doublons, les validations de champs et les gestes répétitifs à faible risque. Elle doit être limitée lorsque la décision exige un jugement ou peut avoir des conséquences graves : suppression de données, accès privilégié, fermeture d'incident critique ou modification de production.

Avant un déploiement, définissez les entrées attendues, les conditions, les résultats, les exceptions, les journaux, les permissions et le mécanisme de retour arrière. Testez les cas absents ou incohérents, les doublons, les pannes d'intégration et les tentatives non autorisées. Une règle qui fonctionne sur les tickets simples peut échouer sur les situations rares mais importantes.

~~~mermaid
flowchart TD
    A[Besoin d'automatisation] --> B[Évaluer risque et fréquence]
    B --> C[Définir règle et contrôles]
    C --> D[Test sur cas normaux et exceptions]
    D --> E{Résultats conformes ?}
    E -->|Non| F[Corriger ou abandonner]
    E -->|Oui| G[Pilote avec journalisation]
    G --> H[Revue des effets et garde-fous]
    H --> I[Déploiement progressif]
    I --> J[Surveillance et retour arrière]
~~~

## 8. Mesurer et améliorer le processus

Les indicateurs doivent révéler le fonctionnement réel : temps actif, temps d'attente, nombre de transferts, réaffectations, dossiers retournés pour information manquante, taux de réouverture, respect des engagements et incidents liés à une mauvaise transition. L'analyse par étape aide à repérer où le flux se bloque.

Ne cherchez pas seulement à réduire le nombre d'étapes. Une étape de validation peut sembler coûteuse, mais être essentielle à la sécurité. La bonne question est de savoir si elle réduit un risque proportionné et si son exécution peut être simplifiée sans perdre sa fonction.

Une revue périodique rassemble données, retours agents, incidents, exceptions et changements métier. Les modifications du processus doivent être versionnées, approuvées et communiquées. L'équipe doit savoir quelle version appliquer et à partir de quelle date.

## 9. Atelier pratique corrigé : demande d'accès à une application

**Situation.** Les demandes d'accès passent par courriel, le responsable hiérarchique approuve parfois dans un canal différent et l'équipe support ne sait pas si le droit est encore nécessaire. Les délais sont élevés et les traces dispersées.

**Étape 1 — Définir le périmètre.** Séparer demandes standard, accès sensibles et accès temporaires. Identifier le propriétaire métier de l'application, les données concernées et le responsable des règles d'autorisation.

**Étape 2 — Cartographier.** Décrire la demande, la validation d'identité, l'approbation, l'exécution, le contrôle de résultat et la notification. Relier les preuves au ticket et éviter les approbations uniquement dans les messages privés.

**Étape 3 — Concevoir.** Utiliser un formulaire avec l'identité, le rôle demandé, la justification, la durée, l'approbateur et la catégorie de risque. Prévoir une voie d'escalade si l'approbation tarde. La voie urgente n'élimine pas les contrôles obligatoires.

**Étape 4 — Automatiser.** Router les demandes standard vers l'équipe autorisée, rappeler les approbations en retard et notifier l'échéance des accès temporaires. Les décisions sensibles restent soumises aux contrôles validés.

**Étape 5 — Vérifier.** Mesurer le délai par étape, les demandes incomplètes, les approbations manquantes et les accès qui dépassent leur échéance. Tester également le refus d'accès, l'indisponibilité du système d'approbation et le départ d'un collaborateur.

## 10. Exercices corrigés

**Exercice A.** Une équipe veut supprimer l'étape de validation qui crée la plus longue attente. Quelle analyse faut-il mener ?

**Correction.** Identifier le risque contrôlé, les preuves produites, les cas où la validation évite une erreur et les possibilités d'approbation plus rapide. Tester une simplification avec un périmètre et des garde-fous ; ne pas supprimer la validation avant d'avoir démontré qu'une protection équivalente existe.

**Exercice B.** Un ticket transféré au fournisseur reste sans propriétaire interne. Quelle faiblesse de processus cela révèle-t-il ?

**Correction.** La règle de responsabilité n'est pas explicite. L'organisation doit conserver un propriétaire interne qui suit le fournisseur, communique au demandeur et escalade le retard, même si l'action technique est externalisée.

## 11. Défi final corrigé

**Défi.** Concevez le processus de traitement d'un incident prioritaire avec plusieurs équipes internes et un fournisseur externe. Décrivez états, responsabilités, communication, preuves de résolution, règles de délai et mesure de performance.

**Proposition de correction.** Le ticket est qualifié selon impact et urgence, un propriétaire interne est désigné, puis les équipes contribuent avec des mises à jour datées. Le fournisseur reçoit un dossier complet et reste lié à l'incident parent. Les changements risqués utilisent leur procédure approuvée, même sous pression. Les communications comportent impact connu, action en cours et prochaine mise à jour. La résolution exige des preuves de rétablissement, la validation fonctionnelle définie et une procédure de retour en cours en cas de réapparition. Les métriques suivent le temps de rétablissement, l'attente par partie, les transferts, les réouvertures et les incidents de sécurité.

## 12. Checklist de maturité

- Le périmètre, les entrées et les sorties sont définis.
- Les flux incidents, demandes, problèmes et changements sont distingués.
- Les états, transitions et exceptions sont testables.
- Chaque dossier a un propriétaire et un prochain pas.
- Les validations et traces répondent à un risque documenté.
- Les règles de SLA et de priorité sont communes et explicites.
- Les automatisations ont des permissions limitées, des tests et un retour arrière.
- Le processus est versionné, mesuré et révisé avec les équipes.

**À retenir :** un bon processus ne multiplie pas la bureaucratie. Il rend la responsabilité claire, sécurise les décisions importantes et permet d'exécuter un travail complexe de manière cohérente et améliorable.
