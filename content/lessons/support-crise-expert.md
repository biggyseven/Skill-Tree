# Gestion de crise support : coordonner la réponse aux incidents majeurs

> **Mise en contexte**
>
> Pendant une crise, plusieurs équipes peuvent agir en parallèle, les informations se contredisent et les utilisateurs réclament une réponse immédiate. La pression ne doit pas supprimer la discipline : il faut protéger les personnes et les données, rétablir le service, conserver une chronologie et communiquer honnêtement. La gestion de crise consiste à réduire le chaos en attribuant clairement les rôles, les décisions et les prochaines mises à jour.

## 1. Reconnaître une crise et activer le dispositif

Un incident devient majeur lorsque son impact, son étendue, sa durée, sa criticité ou son risque justifie une coordination renforcée. Les critères doivent être définis avant l'événement : service critique indisponible, plusieurs sites affectés, risque de perte de données, atteinte potentielle à la sécurité, impact important sur une activité métier ou impossibilité d'exécuter une fonction essentielle.

La classification ne doit pas dépendre uniquement du nombre de tickets. Un seul incident peut être majeur s'il touche un service essentiel. Inversement, un grand volume de demandes peut rester un phénomène support normal si l'impact est limité. Les critères d'activation doivent être documentés et testés en exercice.

Préparez un canal de crise indépendant du service susceptible d'être indisponible, un annuaire actuel, un modèle de situation, une règle d'escalade et un moyen de joindre les responsables sans utiliser un seul outil. Définissez aussi qui peut activer ou lever le dispositif et comment la décision est enregistrée.

~~~mermaid
flowchart TD
    A[Signal d'incident] --> B[Évaluer impact, portée et risque]
    B --> C{Critères de crise atteints ?}
    C -->|Non| D[Processus incident standard avec surveillance]
    C -->|Oui| E[Déclarer incident majeur]
    E --> F[Nommer les rôles et ouvrir le canal]
    F --> G[Établir la situation initiale]
    G --> H[Actions coordonnées et mises à jour]
~~~

## 2. Séparer coordination, investigation et communication

Une crise nécessite plusieurs fonctions. Le coordinateur de l'incident maintient la vision globale, priorise les décisions et gère les dépendances. Les responsables techniques conduisent les diagnostics et les actions autorisées. Le responsable de communication prépare des messages cohérents pour les publics concernés. Le représentant métier décrit les fonctions affectées et valide les critères de rétablissement du point de vue opérationnel. Les fonctions sécurité, juridique, protection des données ou direction sont impliquées selon le risque.

Une même personne peut porter plusieurs rôles dans un incident limité, mais les responsabilités doivent être annoncées et les conflits de charge anticipés. Le responsable de crise ne doit pas dicter chaque commande technique ; les experts ne doivent pas tous communiquer séparément aux utilisateurs. La séparation réduit les actions contradictoires et les informations non vérifiées.

~~~mermaid
flowchart TD
    C[Coordinateur de crise] --> T[Responsables techniques]
    C --> M[Communication et utilisateurs]
    C --> B[Responsable métier]
    C --> S[Sécurité et fonctions de contrôle]
    T --> U[Résultats et risques techniques]
    B --> V[Critères métier de rétablissement]
    S --> W[Contraintes, notifications et protections]
    U --> C
    V --> C
    W --> C
~~~

Le coordinateur tient une liste de décisions : question, options, risque, décideur, heure, décision et condition de réévaluation. Une décision provisoire doit être marquée comme telle. Si une nouvelle preuve invalide une hypothèse, le plan est mis à jour explicitement au lieu de laisser plusieurs équipes suivre des versions différentes.

## 3. Construire une situation partagée

Le premier rapport de situation doit distinguer ce qui est confirmé, ce qui est suspecté, ce qui reste inconnu et ce qui est en cours de vérification. Il contient le service touché, l'heure de début connue, la portée, l'impact métier, les symptômes, les changements récents, les actions déjà tentées, le propriétaire et le prochain point de situation.

Une chronologie fiable indique les heures et fuseaux, les événements techniques et les décisions. Ne réécrivez pas l'historique pour rendre une hypothèse initiale plus cohérente. Conservez les corrections et indiquez quand une information a été confirmée ou retirée.

Pendant la crise, limitez les canaux de décision. Un canal technique, un journal de décision et un canal de communication contrôlé sont souvent plus utiles que des conversations parallèles non traçables. Les canaux de travail ne doivent pas partager de secrets, mots de passe ou données sensibles au-delà du besoin autorisé.

## 4. Prioriser le rétablissement et sécuriser les actions

L'objectif prioritaire est de réduire l'impact tout en maîtrisant les risques. Le chemin le plus rapide n'est pas toujours le plus sûr : redémarrer un système peut accélérer le retour du service mais compromettre des preuves, aggraver une corruption ou interrompre une récupération. Les options sont évaluées selon l'impact, les chances de réussite, les dépendances, la réversibilité et les risques secondaires.

Distinguez rétablissement, contournement et résolution définitive. Un contournement peut restaurer une fonction critique sans corriger la cause. Il doit être documenté, validé, limité dans le temps et suivi d'un plan pour retirer la mesure temporaire. Communiquez les limites à l'activité métier.

Lorsqu'un incident de sécurité est suspecté, protégez les preuves et suivez le plan de réponse correspondant. Ne faites pas de nettoyage ou de réinstallation improvisée susceptible de détruire des données nécessaires à l'investigation. Les actions d'urgence restent dans le périmètre des rôles autorisés.

~~~mermaid
flowchart LR
    A[Options de rétablissement] --> B[Impact métier]
    A --> C[Probabilité de succès]
    A --> D[Réversibilité]
    A --> E[Risque technique et sécurité]
    B --> F[Décision autorisée]
    C --> F
    D --> F
    E --> F
    F --> G[Exécuter et vérifier]
    G --> H[Documenter les effets]
    H --> I{Service et garde-fous conformes ?}
    I -->|Oui| J[Stabiliser et surveiller]
    I -->|Non| A
~~~

## 5. Maîtriser la communication de crise

Une communication utile indique les faits connus, l'impact, l'action en cours, ce que les utilisateurs doivent faire, les éléments non confirmés et l'heure de la prochaine mise à jour. Ne promettez pas une heure de résolution si elle n'est pas soutenue par les preuves. Il est préférable de s'engager sur la prochaine communication que d'inventer un délai de restauration.

Adaptez le niveau de détail à chaque public sans modifier les faits. Les équipes techniques ont besoin des symptômes et des journaux ; les utilisateurs ont besoin de savoir quelles fonctions sont touchées et quelles solutions de contournement sont autorisées ; la direction a besoin de l'impact, des risques, des décisions et des options. Les messages externes peuvent nécessiter une validation supplémentaire.

~~~text
Situation : [service et zone touchés]
Début observé : [date, heure et fuseau]
Impact confirmé : [fonctions et publics affectés]
État actuel : [faits confirmés, inconnues explicites]
Actions en cours : [responsable et prochaine étape]
Action utilisateur : [consigne autorisée, ou aucune action]
Prochaine mise à jour : [heure et fuseau]
~~~

Mettez à jour même si la résolution n'est pas encore trouvée. Une absence de nouvelles pousse les utilisateurs à multiplier les tickets et peut créer des hypothèses contradictoires. Si une information publiée était incorrecte, corrigez-la clairement avec une note de correction ; ne la supprimez pas silencieusement.

## 6. Coordonner les fournisseurs et dépendances

Une crise implique parfois un opérateur réseau, un hébergeur, un éditeur, un prestataire d'identité ou un service partagé. Préparez à l'avance les contrats d'escalade, références de compte, canaux d'urgence, preuves attendues, fuseaux horaires et règles de communication. Un numéro de support non testé n'est pas un dispositif de crise fiable.

Envoyez au fournisseur un dossier exploitable : identifiant du service, début de l'incident, étendue, symptômes, tests, changements connus, pièces jointes minimisées et niveau d'impact. N'envoyez jamais de secrets non nécessaires. Conservez un responsable interne qui suit les engagements du fournisseur, rassemble les mises à jour et garde la responsabilité de la communication aux métiers.

Si plusieurs prestataires se renvoient la cause, le coordinateur organise une investigation commune avec une chronologie partagée et des questions vérifiables. Les débats contractuels ne doivent pas empêcher les actions d'atténuation urgentes, mais les décisions restent autorisées et tracées.

## 7. Décider quand la crise est terminée

La fin de crise ne doit pas être déclarée uniquement parce qu'un serveur répond au ping ou que le volume de tickets diminue. Définissez des critères de rétablissement avec le responsable métier : fonctions essentielles testées, données cohérentes, performance suffisante, files de messages maîtrisées, contrôles de sécurité respectés et surveillance active.

Après le rétablissement, maintenez une période d'observation et un propriétaire de suivi. Fermez le dispositif de crise lorsque les critères sont atteints et que les risques résiduels sont attribués. Les tâches de résolution permanente, de réparation de données, de notification et d'amélioration peuvent continuer sous des dossiers liés.

Le journal de crise conserve la chronologie, les décisions, les communications, les hypothèses retenues ou rejetées et les résultats des tests. Les informations sensibles restent protégées selon les règles de conservation. Le rapport final doit permettre de comprendre le phénomène sans dépendre de la mémoire d'une seule personne.

## 8. Retours d'expérience sans blâme

Organisez le retour d'expérience lorsque la pression est retombée et que les faits sont suffisamment disponibles. Le but est de comprendre le système : quels signaux étaient disponibles, quelles procédures ont aidé, où les responsabilités étaient ambiguës, quels contrôles ont manqué et quelles actions réduiront la répétition.

Distinguez l'erreur honnête, le contexte qui l'a rendue probable, les lacunes de conception et les actions intentionnelles qui relèvent d'un traitement séparé. La revue ne doit pas devenir une enquête publique sur les personnes. Elle doit produire des actions concrètes avec propriétaires, échéances et mesure d'efficacité.

~~~mermaid
flowchart TD
    A[Fin du rétablissement] --> B[Reconstituer la chronologie]
    B --> C[Comparer détection, décision et actions]
    C --> D[Identifier les facteurs contributifs]
    D --> E[Créer des actions vérifiables]
    E --> F[Attribuer propriétaires et dates]
    F --> G[Revue d'efficacité]
    G --> H[Mettre à jour procédures et exercices]
~~~

Une action post-crise ne doit pas se limiter à « améliorer la communication ». Précisez le public, le canal, la fréquence, le responsable et la preuve attendue. Pour une alerte manquée, définissez le seuil, le destinataire, la relève et le test de validation. Pour un transfert qui a échoué, définissez l'acceptation obligatoire et le mécanisme d'escalade.

## 9. Atelier pratique corrigé : indisponibilité du service d'identité

**Situation.** Plusieurs applications d'entreprise refusent les connexions. L'incident touche trois sites et une équipe soupçonne un changement récent. Les informations sont incomplètes et le fournisseur d'identité est sollicité.

**Étape 1 — Activation.** Vérifier les critères d'impact, déclarer l'incident majeur si nécessaire, nommer le coordinateur, le responsable technique, la communication et le représentant métier. Ouvrir un canal de crise indépendant du service affecté.

**Étape 2 — Situation initiale.** Consolider les sites, applications, premiers symptômes, heure UTC, changements connus et tests déjà réalisés. Marquer l'hypothèse du changement comme non confirmée tant que les preuves ne sont pas disponibles.

**Étape 3 — Atténuation.** Évaluer les solutions autorisées avec l'équipe identité et sécurité. Toute mesure de contournement doit être limitée, tracée et évaluée pour ses risques. Ne pas désactiver globalement les contrôles de sécurité pour accélérer la connexion.

**Étape 4 — Communication.** Informer les utilisateurs des services affectés, des actions autorisées et de l'heure de prochaine mise à jour. Éviter de promettre un retour complet avant validation.

**Étape 5 — Validation.** Tester des connexions représentatives, confirmer les fonctions métier et surveiller les erreurs. Le retour à l'état nominal ne sera annoncé qu'après confirmation des propriétaires de service.

**Étape 6 — Après-crise.** Relier les tickets, les changements et les logs, analyser les causes, attribuer les actions et tester le dispositif lors d'un exercice ultérieur.

## 10. Exercices corrigés

**Exercice A.** La direction exige une heure de résolution estimée alors que la cause est inconnue. Que doit répondre le coordinateur ?

**Correction.** Communiquer les faits, les options explorées et l'incertitude. S'engager sur une heure de prochaine mise à jour et non sur une résolution inventée. Si une estimation conditionnelle est disponible, expliquer ses hypothèses et sa marge d'incertitude.

**Exercice B.** Le service semble revenir, mais les équipes métiers n'ont pas validé les transactions en attente. Peut-on lever la crise ?

**Correction.** Pas encore si les critères de rétablissement incluent l'intégrité ou la complétude des transactions. Il faut tester les fonctions métier, suivre les files en attente et attribuer les tâches résiduelles avant de déclarer la situation stabilisée.

## 11. Défi final corrigé

**Défi.** Préparez un plan de crise pour l'indisponibilité d'un service critique, avec activation, rôles, communication, coordination fournisseur, critères de rétablissement et retour d'expérience.

**Proposition de correction.** Définir les seuils d'activation, un annuaire et un canal indépendant. Nommer un coordinateur et des responsables techniques, métier, communication et sécurité. Créer une chronologie UTC, un registre de décisions et une cadence de mise à jour. Évaluer les options selon impact, réversibilité et risque, puis tester les fonctions essentielles avant le retour au nominal. Conserver un propriétaire interne pour les fournisseurs. Après l'incident, produire une revue factuelle et un plan d'actions avec responsable, date, mesure et exercice de validation.

## 12. Checklist de préparation

- Les critères d'activation et de levée de crise sont documentés.
- Les rôles et remplaçants sont définis et entraînés.
- Un canal de crise fonctionne lorsque l'outil principal est indisponible.
- Les faits, hypothèses, décisions et horodatages sont distingués.
- Les actions d'urgence sont autorisées, réversibles autant que possible et tracées.
- La communication annonce un prochain point sans inventer de résolution.
- Les fournisseurs disposent d'une voie d'escalade testée.
- Les critères de rétablissement incluent la validation métier et les garde-fous.
- Le retour d'expérience génère des actions mesurables et vérifiées.

**À retenir :** une crise se gère par une coordination claire, des décisions traçables, une communication honnête et une validation explicite du rétablissement. La vitesse importe, mais elle ne doit pas sacrifier la sécurité, la preuve ni la confiance.
