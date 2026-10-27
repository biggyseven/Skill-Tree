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
