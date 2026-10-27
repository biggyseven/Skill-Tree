# Frameworks ITIL (incidents, changements)

> **Mise en contexte**
>
> Dans une équipe informatique, certains tickets décrivent une panne, d'autres une demande d'accès, un changement planifié ou un problème qui réapparaît chaque semaine. Lorsque toutes ces situations suivent le même circuit, les urgences se mélangent aux demandes ordinaires et les changements risqués sont exécutés sans analyse suffisante. Les pratiques de gestion des services aident à distinguer les objectifs et à rendre les décisions explicables.

## Objectifs du cours

Tu vas apprendre à distinguer incident, demande de service, problème et changement ; à comprendre les pratiques ITIL liées à la gestion des incidents, des problèmes et des changements ; à évaluer le risque, préparer une validation, définir un retour arrière et mesurer l'amélioration du service.

## 1. ITIL : un cadre de pratiques, pas une recette unique

ITIL est un ensemble de recommandations pour gérer des services numériques et améliorer leur valeur pour les utilisateurs et l'organisation. Il ne remplace pas la connaissance technique, les règles de sécurité, les contrats ni les procédures locales. Les pratiques doivent être adaptées à la taille de l'équipe, au risque et aux obligations du service.

L'objectif n'est pas de produire le plus de formulaires possible. Il est de décider de manière cohérente, de réduire les interruptions évitables, de contrôler les modifications et d'apprendre des incidents.

## 2. Distinguer les principaux flux de travail

| Type | But | Exemple | Résultat attendu |
|---|---|---|---|
| Incident | Rétablir un service interrompu ou dégradé | Une application ne répond plus | Service restauré et impact réduit |
| Demande de service | Fournir une demande standard pré-approuvée | Accès à un outil selon les règles | Demande exécutée, contrôlée et tracée |
| Problème | Comprendre et traiter la cause d'un ou plusieurs incidents | La même panne revient chaque semaine | Cause confirmée ou documentée, actions de réduction du risque |
| Changement | Modifier un service ou son environnement de manière contrôlée | Mise à jour d'un serveur en production | Modification évaluée, autorisée, vérifiée et documentée |

Un incident peut être résolu avant que sa cause profonde soit connue. Le traitement du problème peut continuer après le rétablissement. Une demande de service n'est pas automatiquement un changement : la mise à disposition d'un accès standard peut suivre un flux préautorisé, tandis qu'une modification de droits sensibles peut exiger une validation différente.

## 3. Gestion des incidents

Le processus d'incident cherche à restaurer le service aussi rapidement et sûrement que possible. Il comprend habituellement la détection, l'enregistrement, la catégorisation, l'évaluation de l'impact et de l'urgence, l'investigation, l'escalade si nécessaire, le rétablissement, la validation et la clôture.

La priorité doit reposer sur des critères communs. Le ticket doit conserver les symptômes observés, les utilisateurs affectés, les contrôles, la chronologie et les communications. Un contournement peut restaurer le service même si la cause n'est pas encore corrigée ; dans ce cas, indique clairement les risques résiduels et ouvre ou rattache un problème si le processus le demande.

## 4. Gestion des problèmes et des erreurs connues

Un problème concerne la cause ou les causes potentielles d'incidents, ainsi que les moyens de réduire la probabilité ou l'impact de leur réapparition. L'analyse peut conduire à une cause racine confirmée, à une erreur connue assortie d'un contournement ou à une conclusion encore incertaine.

Ne déclare pas une cause racine simplement parce qu'une corrélation existe. Compare la chronologie, les éléments techniques, les hypothèses concurrentes et les résultats des tests. Documente les mesures immédiates séparément des actions de fond : redémarrer un service peut rétablir le service sans éliminer la raison pour laquelle il s'est arrêté.

## 5. Gestion des changements

Un changement doit être décrit, évalué, autorisé selon le risque et vérifié après exécution. Le dossier précise le but, le périmètre, les actifs et services concernés, les dépendances, les risques, la fenêtre, les tests, le plan de communication et le retour arrière.

Trois catégories sont courantes dans les modèles de gestion, avec une terminologie qui peut varier selon l'organisation :

- **Changement standard :** faible risque, procédure documentée et autorisation préapprouvée dans un périmètre défini.
- **Changement normal :** évalué et autorisé selon le processus applicable avant exécution.
- **Changement d'urgence :** nécessaire pour traiter une menace ou une situation urgente ; il suit un chemin accéléré défini à l'avance et reçoit une revue adaptée ensuite.

« Urgent » ne signifie pas « sans contrôle ». Même dans une urgence, consigne l'autorité qui a autorisé l'action, les risques acceptés, le plan de rétablissement et les tests. Un comité de changement peut intervenir pour certains changements importants, mais toutes les petites tâches n'ont pas besoin d'une réunion formelle si la politique a prévu une autre voie sûre.

## 6. Cycle contrôlé d'un changement

~~~mermaid
flowchart TD
    A[Demande de changement] --> B[Portée et actifs concernés]
    B --> C[Analyse du risque et des dépendances]
    C --> D[Tests, fenêtre et retour arrière]
    D --> E[Autorisation selon la politique]
    E --> F[Exécution et journal de preuve]
    F --> G[Tests après changement]
    G --> H{Critères atteints ?}
    H -->|Oui| I[Clôture et mise à jour documentaire]
    H -->|Non| J[Arrêt, retour arrière ou escalade]
    J --> K[Rapport et revue]
    K --> I
~~~

Le changement est réussi si le service atteint les critères définis, pas uniquement si la commande s'est terminée. Le plan de retour arrière est une décision préparée avant l'exécution, avec les personnes autorisées, le temps nécessaire et les contrôles après retour.

## 7. Relations entre incident, problème et changement

Un incident entraîne la restauration. Si le même symptôme se répète ou si le risque l'exige, un problème est enregistré pour analyser la cause. La correction durable peut nécessiter un changement contrôlé. L'incident et le problème doivent rester reliés, afin que le support puisse identifier un contournement connu et mesurer la répétition.

Cette relation évite deux erreurs courantes : garder un incident ouvert indéfiniment tant que la cause racine n'est pas confirmée, ou clôturer tous les suivis après un simple rétablissement et perdre la trace de la cause récurrente.

## 8. Indicateurs et amélioration continue

Les métriques doivent guider les décisions, pas punir les personnes. Suis selon les besoins le volume d'incidents, le temps de prise en charge, le temps de rétablissement, les réouvertures, les changements échoués, les retours arrière, les incidents récurrents et les problèmes avec actions en retard. Définis précisément la période, les règles de calcul, les exclusions et la source de données.

Un indicateur qui s'améliore peut masquer un effet indésirable. Une baisse du nombre de tickets peut refléter une sous-déclaration. Une réduction du temps moyen peut résulter de clôtures trop rapides. Compare les chiffres à l'impact utilisateur, à la qualité de résolution et au contexte du service.

## Mise en pratique

### Laboratoire : router correctement quatre scénarios

Pour chaque scénario, sélectionne le flux principal et justifie-le :

1. Un utilisateur ne peut plus accéder à une application utilisée par son équipe.
2. Un nouvel employé demande un accès standard que le responsable a validé.
3. La même erreur revient après trois redémarrages et le service est rétabli à chaque fois.
4. L'équipe doit appliquer une mise à jour de sécurité sur un serveur critique.

Pour le quatrième cas, rédige un dossier de changement minimal : périmètre, risque, fenêtre, sauvegarde ou mécanisme de reprise, tests avant/après, autorisation et critères de retour arrière. Pour le troisième, rattache les incidents et définis une investigation, sans présumer de la cause.

**Résultat attendu :** un tableau qui montre le type de flux, le propriétaire, les preuves requises et les critères de clôture.

## Exercices corrigés

**1. Un incident est rétabli, mais sa cause est encore inconnue. Peut-on clôturer l'incident ?**

Correction : oui si le processus autorise la clôture après validation du service et si les données nécessaires sont conservées. Le problème ou l'analyse de cause doit rester suivi séparément lorsqu'il est nécessaire.

**2. Une mise à jour urgente doit être appliquée. Peut-on ignorer l'analyse de risque ?**

Correction : non. Le processus d'urgence peut être accéléré, mais il doit toujours définir une autorité, les risques acceptés, les étapes, le rétablissement et une revue adaptée.

**3. Pourquoi relier les incidents répétés à un problème ?**

Correction : pour rendre les répétitions visibles, analyser une cause possible, identifier les contournements et préparer des actions de fond plutôt que corriger chaque symptôme isolément.

**4. Une demande d'accès standard est-elle toujours un changement normal ?**

Correction : pas nécessairement. Une demande standard peut suivre un flux préapprouvé, si elle respecte le périmètre, les droits et les contrôles de l'organisation. Une demande qui modifie un service ou un privilège sensible peut nécessiter un autre processus.

## Défi final corrigé

Une équipe redémarre chaque semaine le même service en production. Après le redémarrage, les utilisateurs peuvent travailler. Un ingénieur propose une modification de configuration pour éviter la répétition.

**Correction attendue :** traiter chaque occurrence comme un incident, préserver les preuves et valider le service après le contournement ; ouvrir ou relier un problème pour analyser la répétition ; documenter l'hypothèse technique et la confirmer par des éléments ; préparer la modification comme un changement avec portée, risque, approbation, tests, fenêtre, retour arrière et contrôle post-changement ; puis mesurer si les incidents reviennent. Le redémarrage rétablit le service mais ne démontre pas la cause racine.
