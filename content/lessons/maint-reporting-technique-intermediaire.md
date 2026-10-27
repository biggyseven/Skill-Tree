# Rédiger un rapport d'incident

> **Mise en contexte**
>
> Une application a été inaccessible pendant quarante minutes. Le ticket contient des messages de plusieurs personnes, les heures ne sont pas toutes cohérentes et le compte rendu se limite à « problème réglé après redémarrage ». Quelques jours plus tard, le même incident se produit et personne ne peut établir précisément l'impact ni expliquer les actions exécutées. Un rapport technique structuré permet de transmettre les faits, d'améliorer le suivi et de préparer l'analyse des causes.

## Objectifs du cours

Tu vas apprendre à documenter l'impact, construire une chronologie, séparer faits et hypothèses, enregistrer les actions de diagnostic et de rétablissement, rédiger un résumé compréhensible pour le métier et définir des suivis sans divulguer de données sensibles.

## 1. Rapport, ticket et analyse post-incident

Le **ticket** suit une demande ou un incident opérationnel jusqu'au traitement et à la clôture. Le **rapport d'incident** rassemble les informations utiles pour comprendre ce qui s'est passé, quand, avec quel impact et quelles actions ont été menées. Une **analyse post-incident** plus approfondie recherche les facteurs causaux, les actions d'amélioration et les enseignements à long terme.

Un incident mineur ne nécessite pas forcément un long rapport. La profondeur doit dépendre de la criticité, de la durée, de l'impact, de la répétition et des exigences locales. Pour un incident majeur, le rapport doit être suffisamment complet pour que les personnes absentes pendant l'événement puissent comprendre la séquence et les décisions.

## 2. La structure d'un bon rapport

Un rapport exploitable comporte habituellement :

- **Identification :** référence, service, date, propriétaire du rapport, statut et audience.
- **Résumé exécutif :** ce qui s'est passé, impact principal, durée approximative ou confirmée, et état actuel.
- **Impact :** utilisateurs, sites, processus métiers, fonctions indisponibles et contournements.
- **Chronologie :** heure, événement, source, décision ou action associée.
- **Diagnostic :** faits techniques, hypothèses testées, résultats et limites de l'investigation.
- **Rétablissement :** action exécutée, autorisation applicable et test qui confirme le retour.
- **Cause :** cause confirmée, cause probable ou cause inconnue, sans transformer une supposition en certitude.
- **Suivi :** actions, responsables, échéances, risque résiduel et ticket ou problème associé.

Adapte les détails au public. Le résumé métier explique les conséquences et le retour du service ; l'annexe technique peut conserver les codes d'erreur, les métriques et les extraits nécessaires. Un rapport ne doit pas reproduire des secrets ou données personnelles qui n'ont pas besoin d'être partagés.

## 3. Construire une chronologie fiable

Une chronologie doit répondre à « quand avons-nous observé quoi ? ». Elle ne doit pas mélanger l'heure à laquelle un utilisateur a signalé le problème, celle où la supervision a déclenché une alerte et celle où l'équipe a confirmé la panne.

| Heure locale / fuseau | Événement | Source ou preuve | Niveau de confiance |
|---|---|---|---|
| 10 h 02 | Premier signalement utilisateur | Ticket INC-204 | Confirmé par le ticket |
| 10 h 04 | Alerte de disponibilité | Historique de supervision | Confirmé par la sonde |
| 10 h 09 | Contrôle applicatif en échec | Résultat du contrôle | Confirmé pour ce point de mesure |
| 10 h 25 | Action de rétablissement exécutée | Journal d'intervention | Confirmée |
| 10 h 31 | Test fonctionnel de nouveau réussi | Sonde et validation utilisateur | Retour observé |

Les heures du tableau sont illustratives. Dans un vrai rapport, remplace-les par les données vérifiées et indique le fuseau. Si deux sources divergent, signale l'écart et indique la règle utilisée plutôt que de choisir arbitrairement l'heure qui semble la plus plausible.

## 4. Séparer les faits des hypothèses

Une phrase comme « la mise à jour a cassé le serveur » contient une conclusion causale qui doit être démontrée. Une formulation plus fiable est : « Une mise à jour a été enregistrée à 09 h 50 ; les erreurs applicatives ont été observées à 10 h 04. Le lien causal est en cours de vérification. »

Utilise des formulations précises :
- **Fait confirmé :** « Le contrôle HTTP a échoué trois fois entre 10 h 04 et 10 h 08. »
- **Hypothèse :** « La dépendance de données pourrait avoir contribué à la latence. »
- **Conclusion étayée :** « Les journaux montrent des délais sur la dépendance pendant l'incident et le test contrôlé a reproduit le symptôme. »
- **Inconnu :** « La raison de l'accumulation des requêtes n'est pas déterminée à ce stade. »

Indique les éléments qui soutiennent une conclusion et les limites des données. Un rapport crédible peut contenir une cause inconnue et un plan d'investigation clair.

## 5. Collecter et présenter des preuves techniques

Les preuves peuvent comprendre la chronologie de supervision, les journaux, les résultats de tests, les versions de configuration, l'identifiant du changement, les alertes et les observations des utilisateurs. Utilise les sources autorisées, conserve les références et protège les données sensibles.

Sur un système Linux, une collecte initiale en lecture seule peut par exemple utiliser :

~~~bash
date -Is
hostnamectl
uptime
df -h
systemctl --failed
journalctl -p warning --since "1 hour ago"
~~~

Ces commandes produisent un aperçu utile, mais elles ne conviennent pas toutes à chaque incident. Le choix de l'hôte, de la plage horaire et des permissions doit être validé. Les journaux peuvent contenir des identifiants ou données personnelles : filtre et partage seulement ce qui est nécessaire. N'efface pas ou ne réécris pas les journaux pour rendre le rapport plus simple.

Une capture d'écran isolée peut manquer le contexte. Préfère, quand c'est possible, joindre la référence de l'événement, la période, la source, l'extrait pertinent et l'heure de collecte.

## 6. Flux de rédaction et de validation

~~~mermaid
flowchart TD
    A[Identifier l'incident et l'audience] --> B[Collecter les sources autorisées]
    B --> C[Construire la chronologie]
    C --> D[Séparer faits et hypothèses]
    D --> E[Rédiger impact et rétablissement]
    E --> F[Relecture technique et confidentialité]
    F --> G{Preuves suffisantes ?}
    G -->|Non| H[Marquer les inconnues et les suivis]
    G -->|Oui| I[Valider et publier]
    H --> I
    I --> J[Relier les actions et suivre les échéances]
~~~

Le rapport doit être relu au regard de sa destination. Le technicien confirme l'exactitude technique ; le responsable de service confirme l'impact et les communications ; les équipes de sécurité ou de conformité participent si le type d'incident l'exige.

## 7. Actions de suivi vérifiables

Une action de suivi doit décrire un résultat attendu. « Améliorer la supervision » est vague. « Ajouter un contrôle HTTP sur le parcours critique, confirmer son fonctionnement en environnement de test, définir le seuil avec le propriétaire du service et vérifier la qualité des alertes durant la période convenue » est vérifiable.

Pour chaque action, note un propriétaire, une échéance, une priorité, une dépendance et un critère d'acceptation. Distingue les actions déjà réalisées des actions prévues. Lorsque l'action nécessite un changement en production, renvoie au processus d'autorisation applicable.

## 8. Exemple de résumé exécutif

**Résumé illustratif :** « Entre 10 h 04 et 10 h 31, le contrôle applicatif a signalé une indisponibilité depuis le point de mesure central. Les utilisateurs de deux agences ont signalé des échecs d'accès. Le réseau vers le serveur restait joignable, mais les vérifications HTTP échouaient. Une action de rétablissement a été réalisée selon la procédure autorisée ; le test HTTP et la vérification fonctionnelle ont ensuite réussi. La cause racine n'est pas confirmée. Une investigation est suivie dans le problème PRB-018, et l'équipe vérifiera la récurrence ainsi que la pertinence des alertes.»

Ce résumé distingue impact, observation, action et incertitude. Dans un rapport réel, les durées, les agences, les références et les résultats doivent être issus de preuves disponibles.

## Mise en pratique

### Laboratoire : rédiger le rapport d'un incident fictif

Scénario : l'application est inaccessible de 10 h 04 à 10 h 31 selon la sonde centrale. Deux agences signalent des erreurs. Le ping du serveur réussit, mais HTTP échoue. Le service est rétabli après une action autorisée ; la cause n'est pas encore connue.

1. Rédige un résumé exécutif de cinq à huit lignes.
2. Construis la chronologie en indiquant l'heure et la source.
3. Décris l'impact sans inventer le nombre de personnes touchées.
4. Liste les contrôles effectués et leur résultat.
5. Sépare la cause confirmée, les hypothèses et les inconnues.
6. Propose deux actions de suivi mesurables, avec responsables et critères d'acceptation.
7. Relis le rapport pour supprimer les secrets et les données personnelles inutiles.

**Résultat attendu :** un rapport compréhensible par le responsable métier et assez précis pour qu'un technicien poursuive l'analyse sans reconstruire toute la chronologie.

## Exercices corrigés

**1. Pourquoi « le serveur est tombé » n'est-il pas toujours une description correcte ?**

Correction : le symptôme peut concerner l'application alors que l'hôte répond encore. Il faut préciser le contrôle et le point de mesure : ping réussi, HTTP en échec, ou système réellement indisponible.

**2. Comment rédiger une cause qui n'est pas encore confirmée ?**

Correction : la présenter explicitement comme une hypothèse, citer les éléments disponibles, expliquer ce qui manque et inscrire une investigation avec son propriétaire.

**3. Quel est le rôle du résumé exécutif ?**

Correction : permettre au décideur de comprendre rapidement l'impact, la période, le rétablissement et les risques encore ouverts, sans devoir lire tous les journaux techniques.

**4. Pourquoi un rapport doit-il être relu avant diffusion ?**

Correction : pour vérifier les faits, l'impact, les références, la confidentialité, les interprétations causales et les actions. Une relecture adaptée au public limite aussi les malentendus.

## Défi final corrigé

Un rapport annonce que « la panne est corrigée définitivement » parce qu'un redémarrage a rétabli l'application. Aucune cause n'a été testée et aucune mesure de suivi n'est prévue.

**Correction attendue :** remplacer la conclusion définitive par une déclaration de rétablissement observé, préciser l'heure et le test qui a réussi, décrire le redémarrage comme action de rétablissement et noter que la cause reste non confirmée. Ouvrir ou relier une analyse de problème si le risque le justifie, attribuer des actions vérifiables et définir une période d'observation pertinente. Le rapport ne doit pas confondre retour du service et élimination durable de la cause.


## 9. Définir l'audience et l'usage du rapport

Le rapport technique s'adresse aux équipes qui doivent comprendre les faits, reproduire l'analyse et agir. Un résumé exécutif s'adresse aux responsables qui ont besoin de savoir ce qui a été affecté, pendant combien de temps, quelle décision reste nécessaire et comment éviter une récidive. Le détail peut être placé dans des annexes, mais le résumé ne doit pas simplifier au point de transformer une hypothèse en cause confirmée.

Avant de rédiger, demande-toi quelles décisions le document doit soutenir : autoriser une dépense, choisir une action corrective, informer un client, accepter un risque, réviser un contrat ou clôturer un incident majeur. Le niveau de détail dépend de ces décisions. Un rapport sans lecteur cible devient une collection d'informations qui ne répond à aucune question.

~~~mermaid
flowchart TD
    A[Événements et preuves] --> B[Rapport technique détaillé]
    A --> C[Résumé exécutif]
    B --> D[Diagnostic et actions]
    C --> E[Impact, risque et décisions]
    D --> F[Plan d'amélioration]
    E --> F
    F --> G[Validation et suivi]
~~~

Le rapport doit indiquer son périmètre, sa période, son auteur ou son rôle, sa date de production, les sources utilisées et son statut de validation. Les destinataires externes ou non techniques ne doivent pas recevoir d'informations sensibles qui ne sont pas nécessaires, comme des secrets, des adresses internes complètes ou des détails d'exploitation qui augmentent le risque.

## 10. Construire une chronologie fiable

Une chronologie doit enregistrer les événements importants avec leur heure, leur fuseau ou leur convention, leur source et leur degré de certitude. Distingue l'heure de détection, l'heure présumée du début, la prise en charge, les changements, les actions de diagnostic, le début de la correction, le rétablissement technique, la validation utilisateur et la clôture. Ces instants ne sont pas nécessairement identiques.

Si plusieurs systèmes utilisent des horloges différentes, explique la normalisation effectuée. Ne fabrique pas une précision à la seconde lorsque les sources ne fournissent que l'heure à la minute. Les éléments contradictoires doivent être signalés et, si possible, rapprochés par une source de référence. Le but de la chronologie est de permettre à un autre analyste de comprendre la séquence.

~~~mermaid
flowchart LR
    A[Détection] --> B[Prise en charge]
    B --> C[Diagnostic et hypothèses]
    C --> D[Action corrective ou contournement]
    D --> E[Rétablissement technique]
    E --> F[Test fonctionnel]
    F --> G[Communication et clôture]
~~~

Une chronologie courte peut être présentée dans le corps du rapport avec une annexe détaillée. Évite les captures sans titre ni heure. Si une entrée provient d'un utilisateur, marque-la comme un signalement ; si elle est confirmée par les journaux ou les tests, indique la preuve. Cette distinction réduit la confusion entre la perception, l'observation et la conclusion.

## 11. Présenter l'impact de manière vérifiable

Décris le service affecté, les fonctions indisponibles ou dégradées, les utilisateurs ou sites concernés, le début et la fin selon la méthode retenue, les solutions de contournement, les transactions potentiellement perdues et les obligations qui pourraient être touchées. Distingue la portée confirmée de celle qui reste à déterminer.

Évite de quantifier sans preuve. « Tous les clients ont été affectés » est une affirmation forte ; « les journaux disponibles montrent 120 échecs de connexion sur deux sites pendant 24 minutes » est plus exploitable, avec une note sur les limites de ces journaux. Si l'impact financier ou le volume d'utilisateurs est estimé, indique les hypothèses et l'incertitude.

Le rapport doit aussi expliquer l'impact évité ou limité lorsqu'un contournement a fonctionné, mais éviter d'attribuer ce résultat à une action si la preuve manque. Les incidents techniques et les incidents métier ne se recouvrent pas toujours parfaitement ; le propriétaire du service doit valider la traduction de symptômes techniques en conséquences métier.

## 12. Séparer faits, hypothèses, causes et actions

Le lecteur doit savoir ce qui est confirmé, ce qui est probable et ce qui reste inconnu. Un rapport peut comporter quatre rubriques distinctes : observations et preuves, hypothèses testées, cause confirmée ou niveau de certitude, actions immédiates et préventives. Une analyse post-incident n'a pas besoin d'inventer une cause unique si les preuves ne le permettent pas.

~~~mermaid
flowchart TD
    A[Observation] --> B[Preuve et source]
    B --> C[Hypothèse]
    C --> D[Test discriminant]
    D --> E{Conclusion soutenue ?}
    E -->|Non| F[Revoir l'hypothèse]
    F --> C
    E -->|Oui| G[Cause au niveau de preuve disponible]
    G --> H[Action et critère d'efficacité]
~~~

Une action doit être SMART de façon pragmatique : une description concrète, un responsable, une date cible, une dépendance, une priorité et une preuve de clôture. « Améliorer la supervision » est insuffisant. « Ajouter un contrôle de fraîcheur pour la métrique X, tester sa notification dans le laboratoire, puis vérifier pendant deux semaines qu'aucun trou de collecte n'est silencieux » est vérifiable.

Les actions de confinement ne sont pas nécessairement des corrections permanentes. Un contournement peut restaurer le service mais laisser une cause ouverte. Le rapport doit le dire, attribuer le suivi et préciser les conditions qui imposeraient une nouvelle escalade.

## 13. Préserver la confidentialité et la qualité éditoriale

Ne recopie pas de mots de passe, clés, jetons, données personnelles inutiles ou informations contractuelles non nécessaires. Pour illustrer une commande, masque les paramètres sensibles tout en conservant l'élément nécessaire à la compréhension. Les annexes techniques peuvent être restreintes séparément du résumé destiné à un public plus large.

Les captures et journaux doivent être prélevés dans les systèmes autorisés et conservés selon les règles de l'organisation. Le rapport doit préciser si des données ont été expurgées, comment les heures ont été alignées et si une partie des journaux manque. Il vaut mieux exposer une limite que présenter une conclusion apparemment complète sur des données partielles.

L'analyse doit être orientée vers l'apprentissage. Décrire le rôle d'une équipe ou la décision prise peut être nécessaire pour comprendre le processus ; accuser une personne sans preuves ne l'est pas. Les rapports de qualité évitent les formulations culpabilisantes et recherchent les causes systémiques : procédure ambiguë, signal trop tardif, dépendance non documentée, changement mal contrôlé ou accès inadapté.

## 14. Travaux pratiques avancés

### TP 6 — Écrire un résumé exécutif

Un service de facturation a été inaccessible pendant 26 minutes. Le service a été rétabli par un contournement. La cause racine n'est pas encore confirmée et deux actions restent ouvertes.

**Correction attendue :** le résumé indique le service affecté, la durée selon la mesure définie, les conséquences confirmées, le rétablissement via contournement, l'état de la cause et les actions ouvertes avec responsables et échéances. Il ne prétend pas que l'incident est définitivement résolu si une cause reste à étudier.

### TP 7 — Corriger une chronologie ambiguë

Un brouillon contient « 9 h : panne, 9 h 10 : réparé, 9 h 20 : tout va bien » sans source ni test final.

**Correction attendue :** identifier l'origine de chaque heure, distinguer détection et début présumé, préciser l'action appliquée et décrire le test de rétablissement. Si la preuve manque, écrire que l'heure ou le résultat reste à confirmer.

### TP 8 — Associer des actions à des preuves

Un rapport propose de « former les équipes », « améliorer l'alerte » et « prévenir le problème ».

**Correction attendue :** définir un livrable et une mesure pour chaque action : procédure de formation et vérification de compréhension ; règle d'alerte testée et notification reçue ; contrôle automatisé ou changement avec critères de réussite. Chaque action possède un responsable, une date et un statut.

## 15. Défi final — Rapport post-incident réutilisable

Rédige un rapport sur un incident fictif affectant deux sites, avec une chronologie, l'impact, les preuves, les hypothèses, les causes établies ou encore ouvertes, les actions, le résumé exécutif, les limites et l'annexe technique.

**Correction détaillée :** l'exécutif peut comprendre la situation en moins d'une minute et sait quelles décisions sont nécessaires. Le technicien retrouve les contrôles, les valeurs, les heures, les versions et les limites. Les faits sont séparés des hypothèses ; les actions sont mesurables et assignées. Le rapport ne contient aucun secret, ne confond pas rétablissement et correction définitive et précise les données manquantes.

## 16. Sources utiles

- Atlassian, Incident Management Handbook : https://wac-cdn.atlassian.com/dam/jcr%3Af79066c7-2877-4b1d-8779-bb0af946b59a/Atlassian-incident-management-handbook-.pdf?cdnVersion=2756
- Atlassian, métriques de gestion des incidents et définitions de MTTR/MTTA/MTBF : https://www.atlassian.com/incident-management/kpis/common-metrics
