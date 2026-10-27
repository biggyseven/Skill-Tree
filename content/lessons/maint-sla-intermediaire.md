# SLA, OLA et satisfaction utilisateur

> **Mise en contexte**
>
> Un service est annoncé « disponible à 99,9 % ». Pourtant, un incident majeur a empêché les agents de travailler pendant une longue période, et le rapport mensuel indique que l'engagement est respecté. L'équipe utilise manifestement une définition de disponibilité différente de celle attendue par les utilisateurs. Les engagements de service doivent préciser ce qui est mesuré, sur quelle période, avec quelles exclusions et quelles responsabilités.

## Objectifs du cours

Tu apprendras à différencier SLA, OLA et engagement fournisseur, définir les indicateurs d'un service, interpréter des objectifs de disponibilité, distinguer prise en charge et résolution, relier les objectifs aux processus opérationnels et intégrer la satisfaction utilisateur sans réduire la qualité à un seul chiffre.

## 1. SLA, OLA et contrat fournisseur

- **SLA (Service Level Agreement)** : accord de niveau de service entre le fournisseur du service et le client ou utilisateur métier. Il définit des objectifs mesurables, leur période et les modalités de suivi.
- **OLA (Operational Level Agreement)** : accord opérationnel interne entre des équipes qui contribuent à fournir le service. Il répartit les responsabilités nécessaires pour soutenir l'engagement global.
- **Engagement fournisseur ou contrat de support :** obligation convenue avec un tiers, qui peut contribuer au service sans être identique au SLA présenté au client.

Un SLA ne doit pas promettre un résultat qu'aucune équipe ou dépendance ne peut soutenir. Les OLA aident à répartir les étapes : support, réseau, systèmes, application et fournisseur. Les objectifs internes sont souvent plus exigeants que l'engagement global pour laisser du temps à la coordination, mais ils doivent rester réalistes et définis.

## 2. Définir un indicateur mesurable

Un indicateur utile précise le service, la population, l'unité, la source, la période, la méthode de calcul, les exclusions, le responsable et la conduite à tenir si l'objectif n'est pas atteint. Les termes « rapide » ou « disponible presque tout le temps » ne sont pas mesurables.

| Indicateur | Ce qu'il décrit | Exemple de définition à préciser |
|---|---|---|
| Disponibilité | Part de la période où le service répond selon la définition retenue | Contrôle synthétique pendant les heures de service ou 24 h/24 selon le contrat |
| Temps de réponse | Délai pour accuser réception ou fournir une première réponse | Horodatages du ticket et règles de pause explicites |
| Temps de rétablissement | Temps jusqu'au retour du service selon un critère validé | Début et fin de l'interruption, vérifiés à partir des preuves |
| Taux de résolution au premier contact | Part des tickets résolus sans transfert ni nouvelle interaction selon une définition convenue | Catégories de tickets incluses et règles de réouverture |
| Satisfaction | Retour des utilisateurs sur l'expérience et la communication | Question, échelle, population et taux de réponse |

Le temps de première réponse n'est pas le temps de résolution. Un ticket peut recevoir une réponse rapide mais nécessiter une longue investigation. Le temps de rétablissement d'un service critique peut être différent de l'heure de clôture administrative du ticket.

## 3. Comprendre le calcul de disponibilité

La formule simple est :

**Disponibilité (%) = (durée de service prévue − indisponibilité comptabilisée) / durée de service prévue × 100**

La définition de « durée prévue » et des interruptions prises en compte doit être convenue. Si un SLA mesure 30 jours en continu, la durée théorique est de 30 × 24 × 60 = 43 200 minutes. Un objectif de 99,9 % correspond alors à 0,1 % d'indisponibilité, soit environ 43,2 minutes sur cette période. Ce calcul ne s'applique pas tel quel si le service n'est couvert que pendant certaines heures ou si le contrat prévoit d'autres règles.

Une moyenne peut masquer un incident très pénalisant. Un tableau de bord de disponibilité doit être accompagné d'informations sur les incidents majeurs, les utilisateurs affectés et la durée des interruptions.

## 4. Aligner les OLA et les dépendances

Imagine un service métier qui dépend du réseau, d'un serveur applicatif, d'une base de données et d'un fournisseur externe. Le SLA global est compromis si chaque équipe attend que l'autre agisse, ou si les délais internes dépassent l'objectif disponible pour le rétablissement.

~~~mermaid
flowchart TD
    A[Engagement SLA du service] --> B[OLA du support]
    A --> C[OLA réseau et systèmes]
    A --> D[OLA applicatif et données]
    A --> E[Engagement fournisseur]
    B --> F[Coordination de l'incident]
    C --> F
    D --> F
    E --> F
    F --> G[Mesures, communication et revue]
~~~

Chaque accord interne doit préciser les interfaces : qui accepte un transfert, quelles informations sont requises, qui communique, quand une escalade est déclenchée et quelles preuves valident la résolution. Un contrat fournisseur ne transfère pas automatiquement à celui-ci la responsabilité de la communication envers les utilisateurs.

## 5. Priorité et objectifs de service

Définis les objectifs selon la priorité et le type de service. Par exemple, un incident critique peut imposer une prise en charge immédiate et des mises à jour fréquentes, tandis qu'une demande standard suit une file planifiée. Les valeurs exactes doivent venir du contrat et de la politique locale.

Pour éviter les ambiguïtés, précise :
- le moment exact où le chronomètre démarre ;
- les pauses autorisées, par exemple l'attente d'une information utilisateur, si le contrat le prévoit ;
- le calendrier applicable, les jours fériés et le fuseau horaire ;
- les règles de priorité et les conditions de reclassement ;
- le critère objectif de service rétabli ;
- les exceptions prévues et leur justification ;
- le propriétaire de la mesure et la procédure de contestation.

Les pauses ne doivent pas être utilisées pour améliorer artificiellement les résultats. Toute exclusion doit être prévue, traçable et cohérente avec l'accord.

## 6. Mesurer la satisfaction sans déformer la réalité

Une enquête de satisfaction aide à comprendre si la communication, la solution et le délai ont répondu aux attentes. Elle doit être interprétée avec son taux de réponse et la population interrogée. Les personnes très satisfaites ou très mécontentes répondent parfois plus souvent que les autres.

Complète les notes de satisfaction par les réouvertures, les incidents récurrents, les délais réels et les commentaires qualitatifs. Un technicien ne doit pas pousser un utilisateur à donner une bonne note. Les commentaires doivent être traités avec respect et partagés uniquement avec les personnes autorisées.

Une mauvaise satisfaction n'implique pas toujours une mauvaise exécution technique : elle peut révéler une communication insuffisante, un contournement peu pratique ou un engagement qui ne correspond plus aux besoins du métier.

## 7. Reporting et traitement des écarts

Le rapport périodique doit présenter les objectifs, les résultats, les tendances, les incidents ayant affecté les engagements, les exceptions, les actions correctives, les propriétaires et les échéances. Le calcul doit être reproductible et provenir d'une source de données identifiée.

Lorsqu'un objectif n'est pas respecté :
1. valide les horodatages et la définition du calcul ;
2. confirme l'impact réel et les exclusions prévues ;
3. informe les parties selon le processus ;
4. cherche les facteurs contributifs et les dépendances en cause ;
5. attribue les actions et mesure leur progression ;
6. vérifie que l'amélioration produit un meilleur résultat pour l'utilisateur.

Ne modifie pas rétroactivement la définition d'un indicateur pour effacer un écart. Toute modification du SLA ou de l'OLA doit être approuvée, documentée et annoncée.

## Mise en pratique

### Laboratoire : définir un SLA et ses OLA

Choisis un service fictif, par exemple un outil de ticketing disponible durant les heures de travail ou une application métier utilisée en continu. Rédige une fiche contenant périmètre, calendrier, disponibilité cible, délais de première réponse selon la priorité, critère de rétablissement, méthode de calcul, exclusions autorisées, source des horodatages et responsable.

Établis ensuite les contributions du support, de l'équipe réseau/systèmes et de l'équipe applicative. Pour chaque OLA, indique le délai de prise en charge, le contenu d'une passation correcte, le déclencheur d'escalade et le propriétaire de la communication. Calcule un exemple de disponibilité avec des données fictives et explique les limites du résultat.

**Résultat attendu :** un engagement que deux personnes peuvent interpréter de la même manière, vérifier à partir des mêmes données et utiliser pour déclencher une action.

## Exercices corrigés

**1. Quelle différence entre SLA et OLA ?**

Correction : le SLA décrit les objectifs convenus pour le service fourni au client ou au métier ; l'OLA décrit les accords opérationnels entre équipes internes qui contribuent à cet engagement.

**2. Un ticket reçoit une première réponse en cinq minutes, mais le service reste indisponible pendant deux heures. Le délai de résolution est-il respecté ?**

Correction : cela dépend des objectifs distincts définis. La première réponse rapide ne prouve pas que le délai de rétablissement a été respecté.

**3. Quelle indisponibilité correspond à 99,9 % sur 30 jours continus ?**

Correction : 30 jours correspondent à 43 200 minutes ; 0,1 % de cette période représente 43,2 minutes. Il faut adapter le calcul au calendrier et aux règles d'exclusion convenus.

**4. Pourquoi suivre le taux de réponse d'une enquête de satisfaction ?**

Correction : parce que les réponses peuvent ne pas représenter tous les utilisateurs. Le taux et la composition des répondants aident à interpréter les notes avec prudence.

## Défi final corrigé

Un rapport affiche une disponibilité mensuelle de 99,9 %. Pourtant, plusieurs équipes ont été bloquées par un incident de deux heures. Le support affirme que son SLA est respecté parce que tous les tickets ont reçu une réponse initiale rapide.

**Correction attendue :** vérifier la définition contractuelle de disponibilité, le calendrier et les périodes incluses ; examiner les preuves et l'impact de l'incident ; distinguer disponibilité, première réponse et rétablissement ; calculer à nouveau avec la méthode approuvée ; vérifier si les engagements internes des équipes ont soutenu la cible globale ; communiquer les écarts selon le processus et attribuer des actions. Si le contrat ne couvre pas correctement l'expérience métier, proposer une révision formelle plutôt que modifier rétroactivement les règles.
