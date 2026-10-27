# Pilotage et évaluation des fournisseurs

> **Mise en contexte**
>
> Une entreprise s'appuie sur plusieurs prestataires : hébergement, maintenance des équipements, licences, sauvegarde externalisée, connectivité et assistance. Les rapports mensuels affichent des SLA convenables, mais les incidents récurrents augmentent, les sous-traitants ne sont pas tous connus et la récupération des données dépend d'un format propriétaire. Le pilotage expert ne consiste pas à attribuer une note annuelle : il faut maîtriser la dépendance, comparer la performance aux engagements réels, traiter les risques de sécurité et organiser une sortie réaliste.
>
> Un fournisseur peut être performant sur un indicateur tout en présentant un risque majeur sur un autre. La décision doit combiner service rendu, criticité, coûts, sécurité, continuité et possibilité de remplacement.

## Objectifs pédagogiques

Tu vas apprendre à segmenter les fournisseurs selon le risque, construire une évaluation qui repose sur des preuves, interpréter des SLA sans confusion, intégrer le risque de chaîne d'approvisionnement et de sous-traitance, définir des exigences contractuelles mesurables, gérer les incidents fournisseurs et préparer un plan de sortie.

## Prérequis

Une compréhension des contrats de services, des changements, de la gestion des incidents et des niveaux de service est recommandée. Les décisions contractuelles et juridiques finales relèvent des personnes habilitées de l'organisation ; le technicien apporte les critères techniques, les preuves et l'analyse du risque.

## 1. Comprendre le cycle de vie d'un fournisseur

Le risque existe avant la signature et demeure après la fin du contrat. Il faut distinguer la qualification, la sélection, l'intégration, l'exploitation, la revue, le renouvellement et la sortie. À chaque étape, l'organisation doit savoir qui décide, quels éléments de preuve sont exigés et comment un risque non acceptable est traité.

### Schéma 1 — Cycle de gouvernance

~~~mermaid
flowchart TD
    A[Besoin et criticité] --> B[Qualification du fournisseur]
    B --> C[Due diligence et analyse du risque]
    C --> D[Sélection et contrat]
    D --> E[Intégration et contrôle des accès]
    E --> F[Suivi du service et des risques]
    F --> G{Renouveler ?}
    G -- Oui --> H[Revue et plan d'amélioration]
    H --> F
    G -- Non --> I[Sortie, transfert et révocation des accès]
~~~

Le contrat doit correspondre au service réellement fourni. Un service de support standard ne présente pas les mêmes dépendances qu'une plateforme de sauvegarde ou qu'un fournisseur qui administre à distance les équipements de cœur de réseau. Documente les fonctions, les données, les accès, les dépendances, les délais de reprise et les conséquences d'une indisponibilité.

## 2. Segmenter les fournisseurs selon le risque

Une segmentation utile prend en compte plusieurs dimensions :

- **Criticité métier** : impact sur la continuité, la sécurité ou le fonctionnement de l'entreprise.
- **Accès** : privilèges, accès à distance, accès aux données sensibles et capacité de modification.
- **Dépendance** : difficulté de remplacement, portabilité des données, exclusivité technique.
- **Exposition** : connectivité externe, chaîne de sous-traitance, surface d'attaque et maturité de sécurité.
- **Concentration** : part du service ou des actifs dépendant d'un seul fournisseur.
- **Récupération** : disponibilité d'une solution de repli, délai de transition et compétences internes.

Évite une formule qui donne une fausse impression de précision. Une grille qualitative peut être appropriée si les critères sont définis et documentés. Pour un fournisseur critique, une faiblesse sur les contrôles d'accès ou l'absence d'une voie de sortie peut bloquer la validation même si le score moyen reste élevé.

### Exemple de classement

| Classe | Exemple | Revue attendue |
|---|---|---|
| Critique | Hébergement de systèmes essentiels, sauvegarde centrale, réseau cœur | Revue approfondie et périodique, exercices de continuité, suivi des incidents majeurs |
| Élevée | Fournisseur d'un service important avec données ou accès privilégiés | Vérification des accès, sécurité, SLA et plans de remédiation |
| Modérée | Service métier important mais facilement remplaçable | Suivi de la performance et vérification des obligations pertinentes |
| Faible | Prestation limitée sans accès sensible ni dépendance forte | Contrôle proportionné et réévaluation si le périmètre change |

## 3. Réaliser une due diligence utile

La due diligence ne se réduit pas à demander une brochure. Elle vérifie que le fournisseur est capable de délivrer le service de manière durable et dans les conditions de risque acceptées. Selon la criticité, recueille les éléments sur l'organisation, la sécurité, les accès, la gestion des vulnérabilités, les mises à jour, le traitement des incidents, la continuité, la localisation des données, les sous-traitants, les pratiques de sauvegarde et la gestion des changements.

Demande des preuves ciblées : rapports de contrôle pertinents, procédures, résultats de tests, attestations dont le périmètre est clair, plans de traitement d'écarts et dates de dernière revue. Une attestation ne prouve pas nécessairement que tous les services ou toutes les régions sont couverts. Vérifie les exclusions, la période et les systèmes concernés. Lorsque les preuves ne peuvent pas être obtenues, note la limite et évalue le risque compensatoire.

### Schéma 2 — Chaîne de confiance

~~~mermaid
flowchart LR
    A[Organisation] --> B[Fournisseur principal]
    B --> C[Sous-traitant]
    C --> D[Service technique spécialisé]
    A --> E[Critères et obligations]
    E --> B
    E --> C
    E --> D
    D --> F[Preuves et suivi du risque]
    F --> A
~~~

La responsabilité ne disparaît pas parce qu'une tâche est sous-traitée. Identifie qui assure le contrôle, qui reçoit les alertes et qui peut autoriser une dérogation. Vérifie les accès tiers, leur durée, la traçabilité des actions, la révocation et le traitement d'un compte compromis.

## 4. Définir les engagements de service de manière mesurable

Un SLA doit définir le service, le début et la fin d'une mesure, la période, les exclusions, la source des données, la méthode de calcul et les responsabilités de chaque partie. « Disponibilité de 99,9 % » ne suffit pas sans préciser le service mesuré, la fenêtre, les maintenances exclues et la façon de gérer les pannes partielles.

Distingue les temps de prise en charge, de réponse technique, de restauration du service et de résolution définitive. Ils décrivent des résultats différents. Un fournisseur peut répondre rapidement à un ticket sans rétablir le service. De même, un accord peut exclure une panne qui est pourtant importante pour l'entreprise ; il faut alors examiner l'adéquation du contrat au besoin métier.

Établis un dictionnaire des indicateurs. Pour chaque KPI, note le propriétaire, l'origine, la fréquence, les règles de calcul, les seuils, les limites et la décision déclenchée. Compare les données internes et les rapports du fournisseur, surtout après un incident majeur. Des périodes d'indisponibilité arrondies, des horodatages non alignés ou des exclusions mal appliquées peuvent changer le résultat.

## 5. Construire un scorecard sans cacher les risques critiques

Un tableau de bord peut rassembler :

- performance du service et respect des engagements ;
- incidents, récurrence, gravité et qualité de résolution ;
- qualité de communication et de reporting ;
- conformité aux exigences de sécurité et délai de traitement des écarts ;
- continuité, résultats d'essais et disponibilité du plan de sortie ;
- prévisibilité des coûts, transparence des changements et facturation ;
- qualité de la coopération et réalisation des actions d'amélioration.

Choisis les pondérations avant la revue et documente les preuves. Un score agrégé ne doit pas effacer un échec critique. Par exemple, un bon respect des délais de ticket ne compense pas une incapacité à révoquer rapidement un accès privilégié ou à restaurer des données. Définis les critères bloquants et les règles d'escalade séparément du score moyen.

### Schéma 3 — Revue des performances

~~~mermaid
flowchart TD
    A[Mesures internes et rapport fournisseur] --> B[Réconcilier les définitions]
    B --> C[Vérifier période et exclusions]
    C --> D[Comparer aux engagements et au risque]
    D --> E[Identifier tendance et écarts]
    E --> F[Action avec responsable et échéance]
    F --> G[Revue d'efficacité]
~~~

## 6. Gérer un incident fournisseur

Pendant une panne, stabiliser le service et protéger les personnes passe avant l'évaluation contractuelle. Utilise le processus d'incident : qualifier l'impact, coordonner les équipes, conserver les événements, communiquer selon les responsabilités, valider le rétablissement et documenter les décisions. Le contrat aide à activer l'escalade, mais ne remplace pas le plan technique d'urgence.

Après la stabilisation, évalue la chronologie, l'information reçue, les décisions et les dépendances. Distingue la cause technique, les facteurs contributifs et la qualité de réponse du fournisseur. Demande des actions avec une preuve mesurable et suis leur réalisation. Si les engagements ont été respectés mais que le service reste insuffisant pour le besoin réel, révise les exigences internes plutôt que de s'en tenir à un indicateur contractuel inadapté.

## 7. Intégrer le risque cyber de la chaîne d'approvisionnement

Le risque peut provenir d'un logiciel vulnérable, d'un accès d'administration externalisé, d'une sous-traitance inconnue, d'une mise à jour non maîtrisée, d'un composant contrefait ou d'une défaillance de disponibilité. Définis des obligations proportionnées : authentification forte, comptes nominatifs, accès limité dans le temps, journalisation, notification d'incident, contrôle des sous-traitants, gestion des vulnérabilités, support de sécurité, protection des données et suppression vérifiable en fin de service.

Les exigences doivent préciser le délai et le canal de notification, les informations attendues, la coopération lors des investigations et les conditions d'utilisation des données. Vérifie aussi les modalités de récupération, l'export dans un format exploitable, les délais, les coûts de sortie, l'effacement et la preuve de révocation des accès. Une clause vague comme « le fournisseur appliquera les bonnes pratiques » est difficile à contrôler.

### Fiche de revue cyber

- Quels actifs, données et environnements sont accessibles au fournisseur ?
- Les accès sont-ils nominaux, approuvés, limités et journalisés ?
- Les sous-traitants et leurs rôles sont-ils identifiés ?
- Comment sont gérés les correctifs et vulnérabilités critiques ?
- Qui doit notifier un incident et dans quel délai convenu ?
- Quels éléments de preuve sont disponibles et quelle est leur période de couverture ?
- Comment les données sont-elles exportées et supprimées lors de la sortie ?
- Quel plan de continuité existe en cas d'indisponibilité du fournisseur ?

## 8. Préparer une stratégie de sortie réaliste

La sortie doit être préparée avant l'urgence. Identifie les données à récupérer, les formats, les dépendances, les comptes, les clés, les configurations, les licences, les contrats liés et les compétences nécessaires au transfert. Vérifie qu'un autre fournisseur peut reprendre le service et que l'organisation pourra accéder aux données pendant la transition.

Un plan de sortie devrait préciser le déclencheur, le décideur, le calendrier, la séquence de transfert, les critères d'acceptation, la continuité temporaire, la révocation des accès, les preuves d'effacement et le sort des composants. Effectue un exercice pour les fournisseurs critiques. Un plan jamais testé peut échouer au moment où le temps et les ressources manquent.

## 9. TP guidé : évaluer un fournisseur de sauvegarde

**Scénario.** Un prestataire héberge des copies de sauvegarde et gère une console d'administration distante. Son rapport annonce un SLA conforme, mais les restaurations complètes ne sont testées qu'une fois par an.

1. Cartographie les données, les accès, les sous-traitants et les dépendances.
2. Définis les résultats de reprise attendus avec les propriétaires métier.
3. Vérifie les règles de notification, la couverture du contrat et les exclusions du SLA.
4. Examine les preuves d'accès, de journalisation, de protection et de révocation.
5. Conçois un test de restauration autorisé en environnement adapté.
6. Évalue le plan de sortie et la portabilité des données.
7. Produit un scorecard avec preuves, points bloquants, actions, responsables et échéances.

**Critère de réussite :** la conclusion relie chaque note à une donnée ou une preuve, indique les incertitudes et ne laisse pas un bon score global masquer une lacune critique.

## 10. Exercices corrigés

### Exercice 1 — SLA conforme, service insatisfaisant

Le fournisseur respecte les délais de réponse, mais les interruptions restent longues. Quelle analyse faut-il faire ?

**Correction.** Sépare réponse, restauration et résolution. Vérifie les définitions contractuelles, la période de calcul, les exclusions et les données internes. Si le SLA n'exige qu'une réponse rapide, l'indicateur ne mesure pas la restauration. Propose une mesure adaptée à l'impact métier et engage la révision contractuelle via les personnes compétentes.

### Exercice 2 — Score global élevé, risque critique

Un fournisseur obtient 92/100 mais ne peut pas démontrer la révocation des accès d'un sous-traitant. Peut-on le déclarer acceptable ?

**Correction.** Pas automatiquement. Définis la lacune comme un point bloquant ou un risque explicitement accepté par l'autorité prévue. Demande la preuve de révocation, limite les accès si c'est autorisé et vérifie la chaîne de sous-traitance. Un score moyen ne remplace pas les seuils critiques.

### Exercice 3 — Absence de plan de sortie

Le fournisseur affirme qu'un export de données « sera possible ». Quelles preuves demander ?

**Correction.** Le format et le périmètre des données, les délais, les coûts, les dépendances de licences, les procédures, les contrôles d'intégrité, les accès pendant la transition, l'effacement et les tests. Pour les dépendances critiques, organise un exercice de transfert dans un environnement de test autorisé.

## 11. Défi final corrigé

**Mission.** Tu dois présenter à un comité de service la revue annuelle de trois fournisseurs : un hébergeur critique, un prestataire de support et un service d'inventaire.

**Correction type.** Segmente les fournisseurs par criticité et dépendance. Définis des indicateurs correspondant à chaque service et des critères bloquants de sécurité. Réconcilie les mesures, documente les preuves et les exclusions, examine les incidents et les tendances, puis classe les actions selon le risque. Pour l'hébergeur, valide la continuité et la sortie ; pour le support, vérifie la qualité d'escalade et de résolution ; pour l'inventaire, vérifie la qualité des données et la gestion des accès. Chaque décision de renouvellement doit expliciter le risque restant et l'autorité qui l'accepte.

## Références pour approfondir

- [NIST SP 800-161 Rev. 1, mise à jour 1 — Cybersecurity Supply Chain Risk Management Practices](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) — risques cyber de la chaîne d'approvisionnement et gestion des dépendances.
- [NIST Cyber Supply Chain Risk Management](https://csrc.nist.gov/Projects/Cyber-Supply-Chain-Risk-Management) — ressources et pratiques de gestion du risque fournisseur.
- Les clauses contractuelles doivent être validées par les équipes juridiques, sécurité, achats et responsables métier de l'organisation.
