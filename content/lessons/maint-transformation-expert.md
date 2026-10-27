# Transformation numérique (ITSM, IA)

> **Mise en contexte — Transformation numérique** : La transformation numérique n'est pas le remplacement d'un outil par un autre. Elle associe un résultat métier, un modèle opérationnel, des processus, des données, des compétences, une architecture, une gouvernance et une adoption mesurable. L'expert choisit des changements qui améliorent le service et maîtrise les risques de migration, de sécurité, de dépendance et d'adoption. Automatiser un processus défaillant ne le rend pas nécessairement meilleur. Un ITSM peut accélérer la circulation des tickets sans améliorer les décisions ; un modèle d'IA peut produire une recommandation plausible mais inexacte ; une plateforme cloud peut réduire certains coûts visibles tout en créant des frais d'exploitation, des dépendances et une gouvernance insuffisante. La transformation commence par le problème à résoudre et doit définir dès le départ ce qui prouvera sa réussite.

## Objectifs pédagogiques

À l'issue du cours, l'apprenant sera capable de :

- définir une vision numérique liée aux résultats métier
- cartographier processus, parcours utilisateur, données et dépendances
- choisir une feuille de route par valeur, risque et capacité d'adoption
- gouverner intégration ITSM, automatisation, cloud et IA
- préparer sécurité, vie privée, qualité des données et réversibilité
- mesurer la valeur et adapter la transformation par étapes

## Prérequis et cadre de responsabilité

Ce cours s'adresse à un professionnel capable de travailler avec des procédures, tickets, données et décisions opérationnelles. Toute décision financière, technique, contractuelle, humaine ou de production doit respecter les autorisations et politiques applicables. Les exemples sont pédagogiques ; ils ne remplacent pas un avis juridique, une règle comptable, une politique de sécurité ou une validation interne. Ne pas inventer de seuil ou présenter une hypothèse comme une exigence approuvée.

Avant une action importante, définir le périmètre, les objectifs, la source de données, le responsable, le résultat attendu, les risques et les conditions d'arrêt. Séparer les faits observés des estimations et hypothèses. Si la qualité des données est insuffisante, le signaler, éviter les conclusions trop générales et organiser le contrôle complémentaire.

## Vocabulaire de référence

| Terme | Définition |
|---|---|
| Transformation numérique | Évolution coordonnée des capacités, processus, données, technologies et pratiques de travail. |
| ITSM | Gestion des services informatiques, incluant processus, rôles, outils et résultats de service. |
| Produit numérique | Capacité maintenue dans la durée avec un responsable, une feuille de route et des utilisateurs. |
| Dette technique | Coût futur et risque produits par des choix techniques qui rendent les changements plus difficiles. |
| Interopérabilité | Capacité à échanger des données et comportements fiables entre systèmes. |
| Garde-fous | Règles et contrôles qui limitent les actions à un périmètre acceptable. |
| Model drift | Dégradation d'un modèle lorsque les données ou conditions d'usage changent. |
| Adoption | Usage réel et approprié d'une capacité par les personnes auxquelles elle est destinée. |

## Schémas de référence

### Schéma 1 — Vision et décision

~~~mermaid
flowchart LR
  A[Problème métier] --> B[Résultat mesurable]
  B --> C[Cas d'usage priorisé]
  C --> D[Pilote]
  D --> E[Preuve de valeur]
~~~

Vision et valeur : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 2 — Rôles et contrôles

~~~mermaid
flowchart TD
  A[Demande] --> B[Qualification]
  B --> C[Décision]
  C --> D[Exécution]
  D --> E[Validation]
  E --> F[Retour et mesure]
~~~

Cartographie du processus : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 3 — Données et dépendances

~~~mermaid
flowchart LR
  A[Source] --> B[Mapping]
  B --> C[Nettoyage contrôlé]
  C --> D[Migration test]
  D --> E[Rapprochement]
  E --> F[Acceptation ou retour]
~~~

Migration données : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 4 — Cycle de mise en œuvre

~~~mermaid
flowchart TD
  A[Cas d'usage] --> B[Évaluation du risque]
  B --> C[Données et contrôles]
  C --> D[Test représentatif]
  D --> E[Supervision humaine]
  E --> F[Surveillance continue]
~~~

Gouvernance IA : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 5 — Risque et exceptions

~~~mermaid
flowchart TD
  A[Tâche candidate] --> B{Règles déterministes ?}
  B -->|Oui| C[Automatisation classique]
  B -->|Non| D{IA adaptée et contrôlée ?}
  D -->|Non| E[Clarifier le processus]
  D -->|Oui| F[Suggestion avec contrôle humain]
~~~

Choix d'automatisation : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 6 — Validation des résultats

~~~mermaid
flowchart LR
  A[Analyse des rôles] --> B[Co-conception]
  B --> C[Formation par tâche]
  C --> D[Pilote]
  D --> E[Feedback et support]
~~~

Adoption : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 7 — Gouvernance et mesure

~~~mermaid
flowchart TD
  A[Stratégie] --> B[Landing zone et identité]
  B --> C[Sécurité et logs]
  C --> D[Migrer par vagues]
  D --> E[Surveiller coûts et service]
~~~

Cloud governance : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 8 — Traitement des écarts

~~~mermaid
flowchart TD
  A[Prototype] --> B[Test et sécurité]
  B --> C[Pilote limité]
  C --> D{Seuils atteints ?}
  D -->|Non| E[Corriger ou arrêter]
  D -->|Oui| F[Extension contrôlée]
~~~

Déploiement progressif : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 9 — Amélioration continue

~~~mermaid
flowchart LR
  A[Baseline] --> D[Valeur constatée]
  B[Qualité et erreurs] --> D
  C[Adoption et coûts] --> D
  D --> E[Décision sur le portefeuille]
~~~

Mesure de valeur : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 10 — Sortie et apprentissage

~~~mermaid
flowchart TD
  A[Solution active] --> B[Exporter les données]
  B --> C[Portabilité des interfaces]
  C --> D[Remplacer le service]
  D --> E[Révoquer accès et clôturer]
~~~

Réversibilité : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

## 1. Partir de la valeur et du parcours utilisateur

Définir le problème avec des utilisateurs et des propriétaires de processus. Mesurer le parcours actuel : demande, qualification, approbation, exécution, validation, communication et clôture. Identifier les étapes d'attente, les transferts inutiles, les doubles saisies, les exceptions et les décisions qui dépendent d'une personne. L'état futur doit améliorer un résultat mesurable et ne pas se limiter à reproduire numériquement le formulaire existant.

Construire une vision cible réaliste qui précise les services concernés, les utilisateurs, les résultats, les principes, les restrictions et les changements du modèle opérationnel. La vision peut viser le traitement de demandes plus cohérent, le diagnostic guidé, la visibilité des actifs, la détection proactive ou la réduction des erreurs de changement. Les résultats sont formulés en termes métier, pas uniquement comme une liste de plateformes à déployer.

Prioriser les cas d'usage selon valeur, risque, maturité des données, complexité d'intégration et capacité de changement. Une démonstration spectaculaire peut avoir une valeur faible si elle ne traite qu'une exception rare, tandis qu'une amélioration simple du catalogage ou de la qualité d'inventaire peut bénéficier à de nombreux processus. Définir un MVP qui produit une preuve de valeur sans laisser de contrôles indispensables de côté.

Cartographier les parties prenantes et les effets du changement. Un nouveau workflow peut modifier les rôles des équipes, la charge des approbateurs, le support, la gestion des données et les compétences. Les communications doivent expliquer pourquoi le processus change, ce qui va changer pour chaque groupe et comment obtenir du soutien. L'adoption doit être testée en pratique, pas déduite du fait que la plateforme est accessible.

## 2. Moderniser les processus ITSM

L'ITSM doit être défini par les pratiques et résultats qu'il cherche à fournir : gestion des incidents, demandes, problèmes, changements, connaissances, actifs et niveaux de service. Une migration de plateforme qui copie des catégories incohérentes, des approbations redondantes et des données de mauvaise qualité reproduit les problèmes à grande échelle. Stabiliser les termes, les règles de décision, les rôles et les critères de clôture avant d'automatiser les étapes.

Concevoir les workflows autour d'états explicites, des transitions autorisées, des champs nécessaires et des exceptions. Chaque automatisation doit rendre visible ce qui déclenche l'action, quelles conditions sont contrôlées, comment traiter une erreur et qui reprend la main. Les actions qui modifient la production, donnent des privilèges, ferment un incident critique ou exécutent un changement doivent posséder des contrôles adaptés au risque.

L'intégration exige un contrat de données : identifiants, schémas, règles de mise à jour, autorité de chaque champ, fréquence, gestion des doublons, erreurs, reprise et surveillance. Si la CMDB et la supervision attribuent des identifiants différents au même actif, l'automatisation peut créer des dossiers séparés ou appliquer une action au mauvais système. Les rapprochements doivent être testés et les ambiguïtés mises en quarantaine.

La migration d'historique doit préserver le sens des données. Documenter le mapping des statuts, des priorités, des propriétaires, des dates et des pièces jointes. Comparer des échantillons, les totaux, la qualité des liens et les règles de rétention avant le basculement. Prévoir les opérations en attente, les mises à jour concurrentes, le mode de lecture seule, le retour arrière et le rapprochement de données créées pendant la transition.

## 3. Encadrer automatisation, cloud et IA

L'automatisation déterministe convient aux tâches définies avec règles claires et résultats vérifiables. Les outils d'IA peuvent assister la recherche, le classement, la synthèse ou la suggestion, mais les sorties probabilistes demandent une validation proportionnée au risque. Ne pas autoriser un modèle à exécuter directement des actions destructives ou à modifier des privilèges sans garde-fous, validation, traçabilité et possibilité d'interrompre.

Pour chaque cas d'usage d'IA, décrire les utilisateurs, l'objectif, les données d'entrée, la sortie, les décisions affectées, les conséquences d'une erreur et le niveau de supervision humaine. Vérifier la provenance des données, les droits, les biais pertinents, la confidentialité, la rétention, les injections malveillantes, les erreurs plausibles et les limites connues. Le cadre de risque doit couvrir conception, acquisition, déploiement, monitoring et retrait, pas uniquement la phase d'expérimentation.

La transformation cloud nécessite stratégie, préparation, gouvernance, sécurité, exploitation et optimisation. Avant migration, classifier les applications, identifier les dépendances, définir la zone d'accueil, les contrôles d'identité, les journaux, les sauvegardes, la gestion de coûts et les responsabilités de service. « Déplacer d'abord » n'est pas toujours optimal ; certaines charges doivent être modernisées, conservées, remplacées ou retirées après analyse.

Les garde-fous techniques doivent être conçus par couches : moindre privilège, approbation, limites de périmètre, validation d'entrée, environnement de test, segmentation, journalisation, monitoring et retour arrière. Les exceptions sont visibles et soumises à une autorisation. Un contrôle automatisé dont les échecs ne sont pas surveillés devient une nouvelle source de risque.

## 4. Conduire l'adoption et la transformation du travail

L'adoption se prépare dès la conception. Identifier les groupes qui changent de tâches, leurs objectifs, les résistances possibles, les compétences nécessaires et les impacts sur la qualité du travail. Des ateliers de co-conception révèlent des exceptions et créent une appropriation, mais la consultation doit pouvoir modifier le design. Recueillir le feedback sans traiter les problèmes signalés comme une résistance au changement.

La formation est organisée par rôle et tâche : utilisateur final, technicien, propriétaire de processus, administrateur, analyste et responsable. Un parcours de formation utile combine démonstration, exercice, cas d'erreur et vérification d'autonomie. Une présence à un webinaire ne prouve pas que les personnes sont prêtes à traiter les demandes et incidents dans le nouvel outil.

Le modèle d'exploitation doit définir les propriétaires des produits numériques, les SLO ou niveaux de service, la gestion des incidents, les mises à jour, l'architecture, la sécurité, les coûts et les demandes d'évolution. Une équipe projet peut livrer une solution sans personne responsable des opérations quotidiennes ; cette lacune crée des retards de correction, des incidents et une dette de gouvernance.

La transformation se fait par étapes lorsque le contexte permet de réduire le risque : pilote contrôlé, retour d'expérience, adaptation, extension et retrait de l'ancien dispositif. Chaque vague possède des critères de décision et un plan de continuité. Le basculement est suspendu si la qualité des données, la capacité de support ou les contrôles de sécurité ne satisfont pas le seuil convenu.

## 5. Mesurer les résultats et gouverner la valeur

Définir une baseline avant le projet : temps de cycle, réouvertures, erreurs, satisfaction, coût, capacité de traitement, couverture de données et incidents. Fixer un ensemble équilibré d'indicateurs. Une transformation peut réduire le temps d'une tâche tout en augmentant les demandes de support ou en créant des erreurs de classification ; le succès doit inclure les effets secondaires et la sécurité.

Lier chaque initiative à une hypothèse : « si nous automatisons la validation de champs, le nombre de tickets incomplets diminuera sans augmenter les rejets légitimes ». Définir une période et un seuil, mesurer la qualité, tester les exceptions et documenter les changements concurrents. Si les résultats ne sont pas conformes, décider de corriger, étendre, maintenir en expérimentation ou arrêter. La sunk cost ne justifie pas la continuation d'une solution qui n'apporte pas de valeur.

Le portefeuille doit être arbitré selon bénéfices, risques, dépendances, capacité d'équipe, coût complet et impact opérationnel. Les initiatives partagent souvent les mêmes ressources de sécurité, données et intégration. Un plan qui lance trop de projets à la fois augmente le temps de coordination et la dette. Une feuille de route doit montrer les prérequis, les étapes, les responsables et les décisions nécessaires.

Gouverner la sortie est aussi important que l'entrée. Définir comment exporter les données, sauvegarder configurations, remplacer des connecteurs, retirer les comptes, conserver les journaux et mettre fin à des abonnements. Une transformation peut devenir dépendante d'un fournisseur ou d'un modèle propriétaire ; évaluer la portabilité et la possibilité de continuer en mode dégradé dès l'architecture initiale.

## Procédure opérationnelle recommandée

1. Formuler le besoin et le résultat métier attendu, avant de choisir un outil ou une solution.
2. Définir le périmètre, les parties prenantes, les hypothèses, les contraintes et les critères de réussite.
3. Établir un état initial à partir de sources traçables, vérifier leur qualité et documenter les lacunes.
4. Comparer plusieurs options, leurs bénéfices, coûts, risques, dépendances, réversibilité et effets secondaires.
5. Définir la gouvernance, les approbations, les responsabilités, les délais et les conditions d'arrêt.
6. Tester l'option retenue dans un cadre proportionné au risque, en définissant les preuves attendues.
7. Mettre en œuvre par étapes, conserver la traçabilité et communiquer les écarts.
8. Mesurer le résultat selon les critères initialement retenus, analyser la comparabilité et les effets secondaires.
9. Attribuer les actions restantes, les responsables, les échéances et le test d'efficacité.
10. Réviser la décision ou la stratégie lorsque les preuves, les risques ou les hypothèses changent.

## Gouvernance, mesure et amélioration

Toute mesure utile dispose d'une définition, d'une source, d'un propriétaire, d'une période, d'une fréquence, d'un dénominateur et d'une décision associée. Publier le niveau de couverture et les exceptions lorsque des données sont manquantes. Des chiffres calculés avec des méthodes ou des populations différentes ne sont pas comparables sans analyse de la rupture.

Les décisions importantes doivent être reliées aux preuves, aux risques et aux responsabilités. Une approbation ne prouve pas que l'action a été réalisée ; la réalisation ne prouve pas toujours que le résultat attendu est atteint. Définir séparément la preuve d'implémentation et la vérification d'efficacité. Les écarts doivent rester visibles, avec des mesures provisoires et un risque résiduel accepté par une personne habilitée.

## Atelier pratique — moderniser le cycle d'incident sans automatiser les risques

### Situation de départ

Une organisation migre son processus d'incident vers un nouvel ITSM et souhaite ajouter un assistant IA pour suggérer des catégories et résumer les dossiers. Le référentiel d'actifs est incomplet et les équipes utilisent des catégories différentes. La direction prévoit une mise en service générale dans six semaines. Le groupe doit construire un plan qui prouve la valeur tout en protégeant les décisions à risque.

### Phase A — Baseline et parcours

Mesurer le délai de qualification, les réouvertures, le taux de dossiers incomplets, la satisfaction et la couverture d'actifs. Cartographier l'état actuel, identifier les exceptions et valider les résultats attendus avec les utilisateurs.

### Phase B — Design et données

Définir les catégories, les identifiants, les règles de migration, les sources de référence et les erreurs de synchronisation. Établir les états et approbations qui doivent rester explicites. Préparer les cas normaux et les cas d'erreur.

### Phase C — Gouvernance IA

Limiter l'IA à une suggestion vérifiable, afficher les incertitudes, conserver les sources et permettre le rejet humain. Interdire tout changement de priorité critique ou action de production sans contrôle prévu. Tester les erreurs, les données sensibles et les sorties incohérentes.

### Phase D — Pilote et adoption

Choisir un groupe pilote, former chaque rôle, définir le support de démarrage et maintenir une voie de repli. Tester les volumes, la migration historique, les droits, la surveillance et les procédures de récupération.

### Phase E — Décision de déploiement

Comparer les résultats à la baseline, examiner sécurité et adoption, inventorier les défauts ouverts et décider de généraliser, corriger ou reporter. Documenter les critères qui autorisent la vague suivante.

### Critères de réussite

Le dossier doit être repris par une personne qui n'a pas participé à l'exercice. Il doit montrer le besoin, la méthode, les données, les décisions, les risques et les validations. Les hypothèses non vérifiées restent identifiées ; les actions sont attribuées et mesurables ; le résultat est confronté à une baseline ou à des critères approuvés. Une conclusion convaincante mais non reproductible n'est pas validée.

## Études de cas

### Cas 1 — Automatiser le mauvais processus

Le nouveau workflow reproduit des approbations inutiles et ajoute de la charge. Simplifier les règles et vérifier qui possède chaque décision avant d'automatiser.

### Cas 2 — Résumé IA inexact

L'assistant attribue à tort la cause d'un incident. Conserver la source, présenter la sortie comme proposition, exiger la validation et mesurer les erreurs sur un jeu représentatif.

### Cas 3 — Coûts cloud inattendus

Les tests et logs consomment beaucoup plus que prévu. Définir budgets, étiquettes de coût, alertes, responsables, limites de rétention et revue de consommation avant extension.

## Exercices d'application avec corrigés

### Exercice 1 — Définir et comparer

**Question.** Pourquoi commencer par une baseline ?

**Corrigé expliqué.** Pour comparer le résultat après changement dans des conditions définies et distinguer progrès, variation de population et effet d'autres changements.

### Exercice 2 — Interpréter le résultat

**Question.** L'IA classe un ticket automatiquement. Quel garde-fou est prioritaire ?

**Corrigé expliqué.** Définir l'usage autorisé, les données, la confiance, le recours humain, la traçabilité et les conséquences d'une erreur ; les décisions à risque doivent rester contrôlées.

### Exercice 3 — Sélectionner une méthode

**Question.** Que faut-il vérifier avant une migration d'ITSM ?

**Corrigé expliqué.** Mapping des statuts, identifiants, données, pièces jointes, accès, intégrations, qualité, historiques, tests de recette, opérations concurrentes et retour arrière.

### Exercice 4 — Traiter un risque

**Question.** Pourquoi une migration lift-and-shift peut-elle échouer ?

**Corrigé expliqué.** Elle transporte aussi des dépendances, défauts et coûts sans nécessairement améliorer le processus ou l'architecture. La stratégie doit arbitrer migration, modernisation, remplacement ou retrait.

### Exercice 5 — Évaluer la preuve

**Question.** Comment savoir si une formation a fonctionné ?

**Corrigé expliqué.** Vérifier une tâche réelle ou un scénario représentatif, les erreurs, l'autonomie et le feedback, pas seulement l'assistance au cours.

### Exercice 6 — Vérifier l'efficacité

**Question.** Quand faut-il arrêter un pilote ?

**Corrigé expliqué.** Lorsque les critères de sécurité, qualité ou valeur prédéfinis ne sont pas atteints et qu'une correction ou un nouveau test n'est pas encore justifié. La décision et le risque doivent être tracés.

## Défi final — mise en situation experte

Élaborer une feuille de route numérique de douze mois pour les processus de maintenance : ITSM, qualité du référentiel, automatisation et un cas d'usage IA à risque contrôlé. Définir baseline, objectifs, architecture et données, sécurité, rôles produit, plan d'adoption, étapes pilotes, critères de déploiement, gouvernance des coûts et stratégie de sortie. Le corrigé priorise la valeur, décrit les contrôles et montre comment décider d'étendre ou d'arrêter chaque initiative.

**Livrable attendu.** Produire un dossier qui présente la situation, la décision, les options, les preuves, les risques et le plan de suivi. Chaque recommandation doit être liée à une raison, un propriétaire et un critère de réussite. Expliquer les incertitudes, les limites du périmètre et les conditions qui feraient réviser la décision.

**Correction attendue.** Une solution experte est cohérente, mesurable et gouvernée. Elle ne confond pas une estimation et un résultat confirmé, ne masque pas les coûts ou risques, compare les options dans un cadre commun et prévoit le contrôle de fin. Elle identifie les décisions qui nécessitent une validation spécialisée et laisse une piste compréhensible pour une revue ultérieure.


## Feuille de route, architecture cible et gouvernance des cas d'usage d'IA

La transformation doit être découpée en capacités livrables plutôt qu'en achats isolés. Une feuille de route réaliste relie chaque capacité à des prérequis, un responsable, une décision de passage, un budget, des risques et une preuve de valeur. Les dépendances typiques comprennent qualité d'inventaire, identité, classification des données, intégration, compétences, support de niveau 2, sécurité et gestion de changement.

### Exemple de feuille de route en vagues

| Vague | Travaux principaux | Critères de passage |
|---|---|---|
| Cadrage | Résultats, baseline, parcours, risques, propriétaire et architecture | Besoin priorisé et critères de valeur approuvés |
| Préparation | Qualité des données, identité, intégrations, rôles, logging et support | Contrôles de base validés et données de test représentatives |
| Pilote | Petit groupe, scénarios normaux et erreurs, formation et support | Valeur mesurée, défauts critiques résolus, utilisateurs capables d'agir |
| Extension | Déploiement progressif, surveillance, accompagnement des équipes | Capacités et support suffisants, résultats stables |
| Optimisation | Réduction des coûts, retrait d'anciens workflows, amélioration continue | Dette, redondances et objectifs de service revus |

Chaque vague comprend une décision « go/no-go ». Les critères ne doivent pas être modifiés uniquement pour respecter le calendrier. Si le pilote montre que les identifiants d'actifs ne sont pas fiables, l'organisation peut poursuivre les travaux qui ne dépendent pas de ces identifiants, mais doit limiter les automatismes qui pourraient appliquer une action au mauvais actif.

### Gouvernance d'un cas d'usage IA

Un dossier d'usage décrit les données, le modèle ou service, les sorties, l'utilisateur, le domaine de décision, les erreurs possibles et leurs conséquences. Évaluer l'impact d'une recommandation incorrecte : une suggestion de tag est généralement moins risquée qu'une décision automatique d'accès, de fermeture d'incident ou de commande de pièces. Le contrôle doit correspondre à ce risque. L'utilisateur doit comprendre quand une sortie est une proposition et quelles sources doivent être vérifiées avant action.

Une validation humaine n'est efficace que si la personne dispose du temps, de la compétence et de l'information nécessaires. Si l'interface pousse à accepter toutes les suggestions, l'humain devient une simple approbation automatique. Mesurer les corrections apportées, les erreurs détectées, la qualité des sources, les cas sans réponse et les conditions dans lesquelles le système doit s'abstenir. Les mécanismes d'accès aux données et la confidentialité doivent être intégrés au design.

La surveillance couvre les changements de données, la qualité des réponses, les incidents, les retours utilisateur, les versions et les dépendances du fournisseur. Un modèle peut se dégrader même si le code n'a pas changé, par exemple lorsque les types d'incident ou les produits sont nouveaux. Définir le propriétaire du monitoring, les seuils d'arrêt, le processus de mise à jour et la méthode de retour à une procédure humaine ou déterministe.

### Architecture cible et responsabilités

Le modèle d'architecture précise les systèmes de référence, les flux d'événements, les APIs, l'identité, les journaux, le chiffrement, les environnements et la gestion des erreurs. Chaque interface doit définir le propriétaire de chaque champ, la gestion des conflits, les reprises, la limite de débit, la version, les notifications et la surveillance. Les intégrations ne doivent pas accepter silencieusement un champ inconnu ou un identifiant absent.

Un modèle de responsabilité opérationnelle identifie qui tient la feuille de route du produit, qui soutient les utilisateurs, qui traite les incidents, qui valide les changements, qui suit les coûts, qui revoit les privilèges et qui peut arrêter le service. Sans propriétaire après le départ de l'équipe projet, même une plateforme correctement installée devient vulnérable à l'obsolescence et à la dérive de configuration.

### Valeur, adoption et arrêt

Définir un indicateur pour le résultat métier, un pour la qualité, un pour le risque et un pour l'adoption. Une diminution du délai de qualification peut être accompagnée d'un taux de mauvaise classification et de réouverture. Un outil de recherche IA peut augmenter le nombre de réponses mais réduire la confiance si les citations ou sources sont erronées. La décision de poursuivre repose sur le résultat global et les limites, pas sur une métrique favorable isolée.

Documenter aussi le plan d'arrêt : export des données, retrait des intégrations, maintien d'un workflow de secours, révocation des accès, conservation des preuves, résiliation des services et communication. La sortie doit être testée à partir d'un périmètre représentatif, car la portabilité annoncée n'est pas toujours égale à une exportation réellement exploitable.


## Ressources techniques et références

- [Microsoft Learn — Azure Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/overview)
- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

Ces ressources apportent des principes et des méthodes ; vérifier leur édition, leur périmètre et leur applicabilité avant de les utiliser comme critères de décision. Les règles locales de finance, de contrat, de sécurité, de ressources humaines et de maintenance restent à confirmer avec les responsables compétents.

## Synthèse

Transformation numérique (ITSM, IA) demande une articulation cohérente entre objectifs, pratiques, gouvernance, ressources et preuves. Une démarche experte formule des critères avant d'agir, documente les risques et les incertitudes, vérifie le résultat réel et transforme les écarts en actions. Le niveau de maîtrise se mesure moins au nombre d'outils ou de rapports qu'à la qualité des décisions et à la capacité du système à s'améliorer durablement.