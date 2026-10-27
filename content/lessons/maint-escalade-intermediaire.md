# Gestion de l'escalade (N1/N2/N3)

> **Mise en contexte**
>
> Un lundi matin, plusieurs utilisateurs ne peuvent plus accéder à une application de facturation. Le centre de support reçoit des tickets identiques. Certains techniciens tentent de résoudre chaque demande séparément ; d'autres transfèrent les tickets sans expliquer les contrôles déjà réalisés. Le responsable ne sait ni combien de personnes sont touchées ni si le délai de rétablissement risque d'être dépassé. Une escalade structurée permet de mobiliser le bon niveau d'expertise sans perdre le fil de l'incident.

## Objectifs du cours

Tu vas apprendre à qualifier un incident, distinguer escalade fonctionnelle et hiérarchique, répartir les rôles N1/N2/N3, établir des critères de transfert, communiquer pendant l'incident et conserver un historique exploitable jusqu'à la résolution.

## 1. Ce que signifie escalader

L'escalade consiste à transférer une demande ou une décision vers un niveau de compétence ou d'autorité plus adapté. Elle ne signifie pas se débarrasser d'un ticket.

Deux formes doivent être distinguées :

- **Escalade fonctionnelle :** le ticket est confié à une équipe disposant des compétences ou des accès requis, par exemple réseau, systèmes, base de données ou application.
- **Escalade hiérarchique :** un responsable est mobilisé lorsque l'impact est important, qu'une décision dépasse l'autorité de l'équipe, que les ressources sont insuffisantes ou qu'un engagement critique est menacé.

Une même situation peut exiger les deux. Un incident affectant les paiements peut être transféré à l'équipe applicative et simultanément signalé au responsable d'astreinte.

## 2. Les responsabilités N1, N2 et N3

Les niveaux sont une organisation de responsabilités, pas une mesure de la valeur des techniciens. Les frontières exactes dépendent de l'entreprise et doivent être documentées.

| Niveau | Mission habituelle | Exemples | Limite à respecter |
|---|---|---|---|
| N1 | Accueil, qualification, contrôles standard, communication et résolution connue | Réinitialisation autorisée, vérification d'incident connu, collecte des symptômes | Ne pas contourner les contrôles d'accès ni exécuter une action non autorisée |
| N2 | Diagnostic technique approfondi et corrections maîtrisées dans le périmètre de l'équipe | Analyse réseau, journaux systèmes, configuration d'un service, tests contrôlés | Escalader si l'autorité, la compétence ou le risque dépasse le périmètre |
| N3 | Expertise spécialisée, éditeur, développement ou ingénierie | Défaut logiciel complexe, anomalie du noyau, problème produit reproductible | Documenter les preuves et suivre les procédures de changement |

L'affectation initiale peut être faite au N1 même si la résolution finale nécessite le N3. Le N1 conserve la responsabilité de qualification et de communication selon le processus, tandis que l'équipe technique responsable réalise le diagnostic.

## 3. Qualifier avant de transférer

Un ticket transférable doit permettre au destinataire de comprendre l'impact, de reproduire ou confirmer le symptôme et de savoir ce qui a déjà été essayé. Inclue au minimum :

- l'identifiant du ticket, le service et l'actif concernés ;
- l'heure de début estimée, le dernier moment où le service fonctionnait et le fuseau horaire si pertinent ;
- les utilisateurs, sites ou processus métiers affectés ;
- le message d'erreur exact et les étapes de reproduction ;
- les tests réalisés, avec leurs résultats plutôt qu'une mention vague « vérifié » ;
- les changements récents connus et les hypothèses encore non confirmées ;
- la priorité, le délai de prochaine mise à jour et le contact de suivi.

N'ajoute pas de mots de passe, jetons, clés privées ni captures qui exposent inutilement des données personnelles. Les preuves doivent être partagées par le canal approuvé, avec les permissions appropriées.

## 4. Priorité, impact et urgence

La priorité doit suivre une matrice partagée entre impact et urgence. Le nombre de tickets n'est pas toujours le meilleur indicateur : un seul utilisateur peut exécuter une fonction essentielle, tandis qu'une panne limitée à un laboratoire peut toucher beaucoup de comptes sans interrompre la production.

| Situation illustrative | Impact | Urgence | Orientation indicative |
|---|---|---|---|
| Service métier critique indisponible pour plusieurs équipes | Élevé | Élevée | Mobiliser rapidement le responsable et l'équipe technique compétente |
| Un utilisateur a un problème avec une solution de contournement approuvée | Faible à moyen | Moyenne ou faible | Traiter selon la file et le délai défini |
| Alarme de sécurité crédible ou suspicion de compromission | Potentiellement élevé | Élevée | Suivre le processus de sécurité et préserver les éléments de preuve |
| Demande d'évolution sans incident immédiat | Variable | Planifiable | Passer par le processus de demande ou de changement approprié |

Cette table n'impose pas des délais universels. Les délais de prise en charge, de réponse et de résolution doivent être définis par les engagements internes et externes.

## 5. Déclencheurs d'escalade

Escalade lorsque l'un des critères documentés est atteint : le délai de diagnostic arrive à sa limite, l'impact augmente, la panne touche un service critique, l'action nécessaire réclame des droits absents, une dépendance externe est impliquée ou les contrôles standard n'ont pas permis d'isoler la cause.

La sécurité prime sur la vitesse. Si un comportement évoque une compromission, un technicien ne doit pas effacer les journaux, réinstaller immédiatement le poste ni communiquer les détails sensibles à des personnes non habilitées. Il doit appliquer le circuit de signalement prévu et préserver les informations utiles.

## 6. Flux d'escalade

~~~mermaid
flowchart TD
    A[Ticket reçu] --> B[Qualifier impact et urgence]
    B --> C[Contrôles N1 autorisés]
    C --> D{Résolution connue et vérifiée ?}
    D -->|Oui| E[Informer et clôturer selon le processus]
    D -->|Non| F{Expertise N1 suffisante ?}
    F -->|Oui| G[Continuer le diagnostic N1]
    F -->|Non| H[Escalade fonctionnelle vers N2 ou N3]
    B --> I{Impact majeur ou décision urgente ?}
    I -->|Oui| J[Escalade hiérarchique et communication]
    I -->|Non| K[Suivi normal du ticket]
    H --> L[Diagnostic et mise à jour]
    J --> L
    K --> L
    L --> M[Validation du service et compte rendu]
    M --> E
~~~

Le transfert et la communication peuvent se dérouler en parallèle. Ne retarde pas une notification critique au seul motif qu'une équipe n'a pas encore identifié la cause.

## 7. Accusé de réception, passation et suivi

Un transfert réussi comporte un destinataire explicite, une raison, les preuves pertinentes, les actions déjà réalisées, le risque connu et la prochaine étape demandée. L'équipe qui reçoit le ticket doit confirmer sa prise en charge selon le processus. Si personne n'accepte un incident critique, applique le mécanisme d'astreinte ou d'escalade prévu plutôt que de supposer que le transfert a fonctionné.

Pendant le suivi, une mise à jour destinée aux utilisateurs doit décrire l'impact connu, les mesures de contournement autorisées, la prochaine heure de communication et les limites de ce qui est confirmé. Évite les promesses de résolution non étayées et les hypothèses présentées comme des faits.

À la clôture, vérifie le rétablissement avec un test pertinent, consigne l'heure de fin et la solution, indique si une analyse de problème reste ouverte et rattache les tickets liés lorsque cela est utile.

## 8. Exemple concret

Une agence signale que l'application métier est inaccessible. Le N1 vérifie l'identité du service, l'heure de début, le nombre d'utilisateurs affectés et le message exact. Le test de connectivité vers le serveur fonctionne, mais le contrôle applicatif échoue. Le N1 documente ce résultat, consulte les incidents connus, puis transfère au N2 applicatif avec les preuves. Plusieurs agences étant touchées, le responsable de service est informé selon le processus. Le N2 confirme ensuite qu'une dépendance de base de données est indisponible et fait intervenir l'équipe compétente. Le support communique les mises à jour prévues, valide l'application après rétablissement et clôture uniquement lorsque le contrôle fonctionnel réussit.

La bonne escalade n'a pas consisté à deviner la cause ; elle a transmis des faits vérifiables à l'équipe capable d'agir.

## Mise en pratique

### Laboratoire : simuler un incident avec trois niveaux

Utilise un scénario fictif ou un environnement de test autorisé. Une application interne ne répond plus depuis 10 h 05 ; le ping du serveur réussit ; deux agences signalent le problème ; le contrôle HTTP échoue ; aucun changement n'est encore confirmé.

1. Ouvre un ticket fictif et rédige une qualification séparant faits et hypothèses.
2. Définis l'impact et l'urgence avec la matrice locale de l'organisation.
3. Note les vérifications N1 déjà effectuées et les résultats précis.
4. Rédige le message de transfert au N2 : service, heure, agences affectées, test réussi, test échoué, changement récent inconnu et action attendue.
5. Décide si une escalade hiérarchique est également nécessaire, et justifie-la.
6. Prépare une mise à jour destinée aux utilisateurs sans annoncer une cause non confirmée.
7. Simule le rétablissement, définis le test fonctionnel et rédige la clôture.

**Résultat attendu :** un dossier permettant à l'équipe suivante de continuer sans refaire inutilement les contrôles, avec un propriétaire clair et une communication cohérente.

## Exercices corrigés

**1. Un technicien transfère un ticket avec le texte « ça ne marche pas ». Pourquoi est-ce insuffisant ?**

Correction : le destinataire ignore le service, le périmètre, l'heure, l'impact, les tests et les actions déjà réalisées. Il faut des faits, des résultats et une demande claire.

**2. Quelle différence entre escalade fonctionnelle et hiérarchique ?**

Correction : l'escalade fonctionnelle mobilise une expertise ou une équipe responsable ; l'escalade hiérarchique mobilise une autorité pour une décision, une priorité ou une coordination qui dépasse le niveau courant.

**3. Le ping fonctionne, mais l'application ne répond pas. Le N1 doit-il clôturer ?**

Correction : non. Le ping ne valide que la connectivité visée. Le ticket reste ouvert jusqu'à une résolution ou un transfert approprié, puis un test fonctionnel du service.

**4. Le N2 ne répond pas et l'impact augmente. Que faire ?**

Correction : suivre le circuit d'astreinte ou d'escalade hiérarchique, documenter l'absence de prise en charge et continuer la communication selon le processus. Il ne faut pas supposer qu'un transfert sans accusé de réception a été accepté.

## Défi final corrigé

Un service de paie est indisponible pour plusieurs agences. Le N1 a confirmé le problème applicatif, le réseau répond et les contrôles standard n'apportent pas de solution. Le délai de prise en charge approche de sa limite.

**Correction attendue :** classer l'incident selon la matrice d'impact et d'urgence ; transmettre immédiatement au niveau technique adapté avec les faits, les tests et l'heure de début ; alerter le responsable si l'impact ou l'engagement l'exige ; demander un accusé de réception ; fournir aux utilisateurs une information factuelle et l'heure de prochaine mise à jour ; préserver les preuves et suivre l'incident jusqu'au test de rétablissement. Le ticket ne peut être clôturé sur la seule base d'une correction supposée.


## 9. Construire un paquet d'escalade complet

Un transfert efficace évite au niveau suivant de recommencer les tests déjà réalisés. Il doit inclure l'identifiant du ticket, le service affecté, le périmètre, l'impact, l'heure de début, les symptômes, la priorité et la raison précise du transfert. Ajoute les tests réalisés, les résultats exacts, les hypothèses examinées, les actions appliquées, les effets observés, les éléments encore inconnus et l'action attendue du destinataire.

Évite les formulations « ça ne marche toujours pas », « vérifier le réseau » ou « urgent ». Elles ne disent ni ce qui a été observé ni ce qui est attendu. Préfère « Depuis 10 h 18, trois postes du VLAN utilisateurs ne résolvent plus le nom de l'application ; la passerelle répond, le DNS configuré ne renvoie aucune réponse au test autorisé. Aucune modification n'a été faite. Demande : vérifier le service DNS ou la connectivité vers le résolveur. » Cette forme relie le fait, la preuve et la demande.

~~~mermaid
flowchart TD
    A[Ticket qualifié] --> B[Symptôme et impact]
    B --> C[Contrôles et résultats]
    C --> D[Actions et limites]
    D --> E[Question précise pour le niveau suivant]
    E --> F[Accusé de réception]
    F --> G[Diagnostic et retour au demandeur]
~~~

Un transfert doit nommer un interlocuteur ou une file qui a effectivement la responsabilité du sujet. Le simple changement d'affectation dans l'outil ne garantit pas que la nouvelle équipe a vu le ticket. Selon les règles du service, le niveau d'origine reste responsable jusqu'à l'accusé de réception ou jusqu'à ce qu'un rôle de coordination assume clairement le suivi.

## 10. Escalade fonctionnelle, hiérarchique et incident majeur

L'escalade **fonctionnelle** transfère la résolution à une équipe possédant les compétences ou accès nécessaires : réseau, système, base de données, sécurité, fournisseur. L'escalade **hiérarchique** sollicite un responsable pour arbitrer les priorités, les ressources, les risques ou la communication. Une escalade fonctionnelle peut être nécessaire même lorsqu'aucune hiérarchie n'est impliquée ; une escalade hiérarchique peut être nécessaire lorsque plusieurs services se disputent une ressource rare.

Pour un incident majeur, il est utile de distinguer plusieurs rôles : responsable de l'incident, pilote technique, personne chargée de la communication, équipes de résolution et représentant métier. Dans une petite équipe, une personne peut assumer plusieurs rôles, mais cette répartition doit être explicite. Le pilote de l'incident maintient la chronologie et les décisions ; les spécialistes mènent les investigations ; la communication fournit des mises à jour cohérentes ; le propriétaire métier valide les conséquences et le retour.

~~~mermaid
flowchart LR
    A[Coordinateur d'incident] --> B[Pilote technique]
    A --> C[Communication utilisateurs]
    B --> D[Équipe réseau]
    B --> E[Équipe systèmes]
    B --> F[Fournisseur ou expert]
    C --> G[Propriétaire métier]
    D --> H[Validation du service]
    E --> H
    F --> H
    G --> A
~~~

Ne confonds pas les niveaux N1/N2/N3 avec une gravité automatique. Un incident très grave peut être détecté au N1 puis immédiatement coordonné par un responsable ; un défaut technique complexe mais sans impact important peut rester un dossier expert planifié. L'escalade doit suivre l'impact, l'urgence, le risque, les compétences nécessaires et la politique de service.

## 11. Définir une matrice d'escalade exploitable

Une matrice doit préciser les critères d'entrée, le destinataire, le délai d'accusé de réception, le contenu requis, la personne qui conserve le suivi et le mécanisme de secours si l'équipe ne répond pas. Les délais exacts viennent des engagements de l'organisation. Évite de fixer des minutes génériques qui ne correspondent pas aux SLA/OLA ou à l'organisation de l'astreinte.

| Situation observée | Orientation indicative | Information requise |
|---|---|---|
| Demande standard bien définie | File de service | Droit, périmètre, utilisateur, échéance |
| Incident local documenté | N1 puis groupe technique adapté | Symptômes, équipement, tests et résultat |
| Dégradation sur plusieurs sites | Coordination d'incident et équipes concernées | Chronologie, périmètre, services et changements |
| Suspicion de compromission | Processus de sécurité dédié | Indicateurs observés, heure, éléments préservés |
| Blocage par autorisation ou ressource | Responsable hiérarchique ou propriétaire | Décision attendue, conséquences du retard |

Une matrice ne doit pas permettre au technicien de retarder l'escalade parce que tous les champs ne sont pas remplis. Si un incident se propage, transfère rapidement les faits déjà connus et complètes ensuite les éléments manquants. En revanche, ne communique pas de secrets, de données personnelles excessives ou des hypothèses non signalées comme telles.

## 12. Suivi après transfert et clôture

Une fois le transfert accepté, le ticket conserve la chronologie et les responsabilités. Le demandeur doit savoir que le dossier évolue, ce qui est confirmé et quand la prochaine mise à jour est prévue. Une estimation doit être présentée comme une estimation, et non une promesse, tant que la cause, la portée et les dépendances ne sont pas confirmées.

Quand la solution est appliquée, demande une vérification du service en regard du symptôme initial. Si la résolution est temporaire, explique la limite, le risque restant et l'action prévue. Lorsque le N1 reprend le suivi, celui-ci doit connaître la solution, les éléments à vérifier, la date et le propriétaire de l'action suivante. Les tickets réouverts doivent être analysés pour déterminer si la résolution était incomplète, si un symptôme est réapparu ou si un critère de clôture était mal défini.

### TP 6 — Escalader sans perdre le contexte

Un service est lent sur deux sites. Tu as vérifié la connectivité locale, comparé les heures de début et trouvé une alerte de saturation sur un lien partagé. Rédige un transfert vers l'équipe réseau, sans affirmer que la saturation est la cause unique.

**Correction :** inclure les sites, les services, le périmètre, les heures, le débit mesuré et la source de la mesure, les contrôles locaux et les résultats. Formuler la saturation comme une hypothèse à vérifier, relier la demande à la capacité et aux événements récents, et indiquer l'action attendue. Informer le coordinateur si plusieurs services sont affectés.

### TP 7 — N2 ne répond pas

Le ticket critique est affecté au N2 mais n'est pas pris en charge pendant la période prévue.

**Correction :** appliquer la matrice de relance ou la relève, conserver la trace des tentatives, notifier le responsable indiqué et continuer les actions sûres déjà autorisées. Ne pas attendre passivement si l'impact augmente. Les délais applicables sont ceux de l'OLA/SLA et de la procédure locale.

### TP 8 — Désaccord sur la priorité

L'utilisateur réclame une priorité maximale, mais les faits indiquent un seul poste affecté et une solution de contournement disponible.

**Correction :** évaluer l'impact et l'urgence avec les critères partagés. L'insistance ne détermine pas la priorité ; un changement de périmètre ou la disparition du contournement justifieraient une réévaluation. Expliquer la décision sans minimiser le problème.

## 13. Défi final — Incident multiservice

Une modification réseau a interrompu l'accès à trois applications dans deux sites. Propose une organisation avec responsable d'incident, experts, communication, critères de changement de priorité, transfert et validation finale.

**Correction :** désigner un coordinateur, créer une chronologie commune, lier les symptômes à un incident principal, assigner des tâches techniques parallèles, communiquer des faits confirmés à intervalle prévu et réserver une seule personne pour les messages externes. La priorité dépend du périmètre, des opérations bloquées et des alternatives. Un changement correctif est autorisé selon la procédure, puis les applications sont testées depuis les deux sites. Le ticket est clôturé uniquement lorsque les critères fonctionnels sont satisfaits et les actions restantes affectées.


## 14. Adapter la communication à la pression opérationnelle

Pendant une interruption majeure, les équipes peuvent recevoir des informations contradictoires. Désigne une source de vérité pour l'état du service et garde une chronologie commune. Les messages aux utilisateurs doivent indiquer ce qui est confirmé, le périmètre connu, le contournement disponible, la prochaine mise à jour et le canal de suivi. Ne publie pas chaque hypothèse technique comme si elle était la cause.

Le coordinateur doit protéger le temps des personnes qui diagnostiquent. Les mises à jour peuvent être rédigées par un responsable de communication pendant que les spécialistes travaillent, ce qui limite les interruptions et les messages contradictoires. Les détails nécessaires au diagnostic restent dans le canal technique et le ticket d'incident ; seuls les éléments pertinents sont partagés à chaque audience.

~~~mermaid
flowchart LR
    A[Sources techniques] --> B[Coordination de l'incident]
    B --> C[État confirmé et incertitudes]
    C --> D[Message utilisateurs]
    C --> E[Priorités pour experts]
    D --> F[Prochaine mise à jour annoncée]
    E --> G[Diagnostic documenté]
~~~

Après rétablissement, vérifie que le transfert ne s'arrête pas à la fermeture du canal d'urgence. Les problèmes structurels, la rédaction d'un rapport, la validation des actions et la revue post-incident doivent avoir des responsables. L'équipe de support conserve la responsabilité du ticket ou confirme explicitement que le suivi est transféré.

Une escalade de qualité est évaluée par sa pertinence, son délai, la complétude des informations, l'acceptation par la bonne équipe et le résultat. Le nombre brut de transferts ne prouve pas que le N1 est inefficace : les tickets complexes nécessitent légitimement une expertise. Les revues doivent chercher les transferts évitables, les mauvais aiguillages et les informations répétées, non punir les escalades justifiées.
