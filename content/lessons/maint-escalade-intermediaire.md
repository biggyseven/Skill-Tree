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
