# Gouvernance et plateforme IaC — Expert

> **Mise en contexte.** Une organisation a réussi à automatiser le provisionnement de nombreux environnements. Avec la croissance, les problèmes changent : les équipes n’utilisent pas les mêmes standards, les composants partagés sont difficiles à faire évoluer, les droits sont trop larges, les audits demandent des preuves dispersées et les changements urgents contournent parfois les règles. Le défi expert n’est plus d’écrire une configuration isolée. Il consiste à exploiter une plateforme qui donne de l’autonomie aux équipes tout en maîtrisant les risques, les coûts et la conformité.

## Positionnement et objectifs

Le parcours est organisé ainsi :

- **Débutant :** comprendre les principes de l’IaC, la livraison versionnée et les différences entre les familles d’outils.
- **Intermédiaire :** organiser les dépôts, les composants, les contrôles et la promotion des changements entre environnements.
- **Expert :** gouverner une plateforme à l’échelle d’une organisation, définir le modèle opérationnel, contrôler les risques, gérer plusieurs outils et mesurer la qualité du service rendu aux équipes.

Le parcours Terraform d’Administration Réseaux reste l’endroit où l’on apprend en détail les mécanismes propres à Terraform, les providers, les opérations sur le state, les plans, les importations et les commandes. Ici, ces mécanismes sont considérés comme des capacités d’une plateforme et servent à prendre des décisions d’organisation.

À la fin du cours, tu dois pouvoir concevoir un modèle opérationnel, choisir des frontières de responsabilité, gouverner un catalogue de composants, gérer les identités et les exceptions, prévoir la reprise après incident, intégrer la sécurité et les coûts au cycle de vie et définir des indicateurs qui permettent d’améliorer la plateforme.

## 1. Traiter l’IaC comme une plateforme interne

Une plateforme IaC robuste doit être pensée comme un produit proposé aux équipes. Ses utilisateurs ont besoin d’un chemin recommandé, d’une documentation, de composants maintenus, d’un support, de garanties de sécurité et d’une manière claire de demander une exception.

Le modèle du **chemin recommandé** consiste à fournir une façon standard de réaliser les tâches fréquentes sans interdire les besoins particuliers légitimes. Ce chemin peut inclure des dépôts modèles, des composants approuvés, des pipelines, des politiques, des identités d’exécution et des tableaux de bord.

Une plateforme utile réduit la charge cognitive des équipes. Une plateforme trop rigide provoque des contournements ; une plateforme sans règles provoque une multiplication des pratiques et des risques. Il faut donc mesurer à la fois l’adoption, la sécurité et la capacité à traiter les exceptions.

### 1.1 Définir le modèle opérationnel

Pour chaque responsabilité, il faut identifier le rôle qui décide, celui qui exécute, celui qui contrôle et celui qui est informé. Les responsabilités peuvent inclure l’exploitation du socle, le catalogue de composants, les identités, les politiques, les coûts, les incidents et les relations avec les équipes applicatives.

Les équipes de plateforme ne devraient pas devenir l’approbateur manuel de chaque modification. Elles doivent définir des garde-fous réutilisables et rendre les décisions locales sûres dans un cadre connu. Les décisions à fort impact restent soumises à un contrôle explicite.

## 2. Définir les frontières de responsabilité et le rayon d’impact

Le découpage d’une plateforme doit refléter les frontières de sécurité et d’exploitation. Une seule configuration géante peut rendre un changement anodin dépendant d’un grand périmètre et augmenter le risque de destruction. À l’inverse, trop de petits périmètres créent une orchestration complexe et une multiplication des dépendances.

Pour définir une frontière, examine :
- le propriétaire opérationnel et les personnes autorisées ;
- la criticité et la classification des données ;
- les dépendances et les consommateurs ;
- le cycle de vie des ressources ;
- la fréquence de changement ;
- les besoins de récupération ;
- les limites de coût et les exigences d’audit.

Un état ou une unité de déploiement doit correspondre à une frontière de responsabilité qui peut être exploitée indépendamment. Ce n’est ni une simple question de taille de dépôt ni une règle universelle sur le nombre de ressources.

### 2.1 Limiter les changements transverses

Une modification qui affecte plusieurs domaines doit être coordonnée avec les propriétaires concernés. Les dépendances inter-domaines devraient transmettre le minimum d’informations nécessaires et éviter les liens implicites qui obligent à déployer toute la plateforme dans un ordre fragile.

Les interfaces contractuelles, les versions, les événements de changement et les procédures de migration aident à réduire le couplage. Les dépendances critiques doivent être documentées avec un responsable, une mesure de santé et une solution de repli.

## 3. Établir une stratégie multi-outils

Une organisation peut utiliser un outil pour provisionner les ressources cloud, un autre pour configurer les systèmes, un autre pour construire des images et d’autres pour déployer des applications. L’objectif n’est pas d’unifier artificiellement toutes les opérations dans le même outil. Il est de rendre leurs frontières compréhensibles et contrôlées.

### 3.1 Construire une matrice de responsabilité

Pour chaque domaine, documente l’outil de référence, le propriétaire, le type d’objet géré, les interfaces d’entrée et de sortie, les journaux, les identités, les tests et le mécanisme de reprise.

    Domaine              Outil ou service maître
    Ressources cloud     Outil de provisionnement déclaré
    Configuration OS    Outil de gestion de configuration
    Images de base      Chaîne de construction d’images
    Applications        Chaîne de livraison applicative
    Identités            Système central d’identité
    Politiques           Contrôle versionné et vérifiable

Cette matrice est un exemple. L’organisation choisit les outils réels en fonction de ses plateformes et de son modèle de support. Le principe essentiel est qu’une ressource ne soit pas gérée simultanément par plusieurs systèmes indépendants sans mécanisme d’arbitrage.

### 3.2 Gérer les transferts de responsabilité

Lorsqu’une équipe adopte une ressource existante, elle doit vérifier l’état réel, identifier les dépendances et obtenir l’accord du propriétaire actuel. Le transfert doit inclure un plan de changement, une période de vérification et une preuve que l’ancien processus ne modifiera plus l’objet.

Une migration d’outil n’est pas simplement une conversion de syntaxe. Elle modifie potentiellement l’identité des ressources, le stockage d’état, les permissions, les procédures opérationnelles et les responsabilités. Il faut tester le processus sur un périmètre représentatif avant de généraliser.

## 4. Gouverner un catalogue de composants

Un catalogue mature comprend des composants avec des propriétaires, une finalité, une version, un niveau de support, une politique de sécurité et des critères de retrait.

### 4.1 Cycle de vie d’un composant

Le cycle de vie peut être résumé ainsi :

    Proposition
        |
        v
    Conception et analyse des risques
        |
        v
    Tests et revue
        |
        v
    Publication d’une version
        |
        v
    Consommation et suivi
        |
        v
    Nouvelle version ou dépréciation
        |
        v
    Migration et retrait contrôlé

Chaque composant doit indiquer quelles garanties il fournit et quelles responsabilités restent à la charge de son consommateur. Un module réseau, par exemple, peut appliquer des règles standards, mais son consommateur reste responsable de la classification de l’application et des besoins métier qui déterminent ces règles.

### 4.2 Compatibilité et retrait

Les évolutions incompatibles nécessitent une stratégie de migration. Une politique de retrait doit communiquer l’échéance, la version de remplacement, les risques, la procédure de migration et les consommateurs qui n’ont pas encore migré. La suppression immédiate d’un composant utilisé peut transformer une amélioration de sécurité en incident de production.

### 4.3 Éviter le catalogue incontrôlé

Le nombre de composants n’est pas une mesure de maturité. Un catalogue avec de nombreuses variantes presque identiques peut augmenter les coûts de maintenance. Identifie les usages répétés, mesure les exceptions et fusionne les abstractions seulement lorsque leurs contrats sont réellement compatibles.

## 5. Construire une gouvernance par politiques

La gouvernance par politiques consiste à définir des règles vérifiables et à les appliquer au bon endroit dans le cycle de changement. Les règles doivent être explicites, testées et liées à une raison : sécurité, conformité, coût, fiabilité ou responsabilité opérationnelle.

### 5.1 Règles préventives et détectives

Les contrôles préventifs bloquent un changement avant application lorsqu’il viole une règle impérative. Les contrôles détectifs recherchent les écarts qui apparaissent après le déploiement. Certains contrôles peuvent être informatifs ou exiger une justification plutôt qu’un blocage absolu.

Exemples de règles :
- interdire l’exposition publique d’un service de gestion ;
- imposer des journaux pour une ressource critique ;
- exiger une classification et un propriétaire ;
- limiter les régions ou les types de ressources autorisés ;
- exiger une expiration pour les environnements temporaires ;
- demander une approbation spécifique pour une opération destructive ;
- interdire les identités permanentes dans les pipelines lorsque des identités temporaires sont disponibles.

### 5.2 Exceptions contrôlées

Une politique sans procédure d’exception encourage les contournements. Une exception doit avoir un propriétaire, une justification, une portée précise, des mesures compensatoires et une date d’expiration. Les exceptions à fort risque requièrent une approbation indépendante et un suivi jusqu’à leur fermeture.

L’exception ne doit pas supprimer la trace du risque. Elle doit rendre visible la décision, le contexte, les mesures compensatoires et la personne qui en accepte la responsabilité.

### 5.3 Tester les politiques comme du code

Chaque politique importante doit être accompagnée d’exemples conformes, non conformes et limites. Les tests doivent montrer qu’une règle bloque le comportement interdit sans casser les cas légitimes. Une modification de politique doit suivre sa propre revue et être testée avant une mise en application globale.

## 6. Sécuriser l’identité et la chaîne d’approvisionnement

La sécurité du code n’est qu’une partie de la sécurité IaC. Les identités, les permissions, les dépendances, les exécuteurs, les artefacts de planification et les journaux peuvent tous devenir des chemins d’attaque.

### 6.1 Identités limitées et temporaires

Il faut distinguer les identités qui valident le code de celles qui peuvent modifier l’infrastructure. Les droits doivent être limités au périmètre et à la durée nécessaires. Les identités d’urgence doivent être surveillées et leur utilisation auditée.

Lorsque cela est possible, privilégie les identités fédérées ou temporaires à des secrets statiques partagés. Le processus d’approbation doit être lié à l’exécution et à la version précises qui seront appliquées.

### 6.2 Protéger les exécuteurs et dépendances

Les exécuteurs de pipeline doivent être isolés selon les niveaux de confiance. Une contribution non approuvée ne doit pas pouvoir lire les secrets de production ni réutiliser un exécuteur privilégié contenant des informations sensibles.

Les dépendances téléchargées doivent être identifiables et leurs versions maîtrisées. Les composants, images et actions partagés doivent avoir un propriétaire et une procédure de mise à jour. Les artefacts qui contiennent des informations d’infrastructure doivent être traités comme des données confidentielles lorsqu’ils exposent des détails sensibles.

### 6.3 Preuves et audit

La preuve utile d’un changement relie la demande, le commit ou la version, les tests, l’aperçu des effets, les approbations, l’identité d’application et la vérification post-déploiement. Conserver seulement les journaux d’exécution ne suffit pas si l’on ne peut pas les rattacher au changement qui les a produits.

## 7. Exploiter une chaîne de livraison à grande échelle

À mesure que le nombre d’équipes augmente, les goulets d’étranglement deviennent importants : exécuteurs partagés, files d’attente, limites d’API, tests redondants, validations globales et approbations manuelles.

Il faut mesurer avant d’optimiser. Les améliorations possibles incluent l’exécution parallèle de tests indépendants, la validation limitée aux composants touchés lorsque la dépendance est connue, la réutilisation sûre des dépendances et l’isolation des exécuteurs selon le niveau de confiance.

L’optimisation ne doit pas supprimer les contrôles nécessaires. Un cache invalide, une dépendance flottante ou un aperçu périmé peut faire gagner du temps tout en rendant le déploiement moins sûr.

### 7.1 Services d’exécution centralisés

Un service d’exécution centralisé peut faciliter la gestion des identités, des permissions, des journaux et des approbations. Il peut aussi devenir un point critique de disponibilité et un goulot d’étranglement. Il faut définir ses objectifs de disponibilité, sa capacité, sa stratégie de mise à jour, ses sauvegardes et le moyen de poursuivre les opérations en cas de panne.

### 7.2 Définir les niveaux de service

Les équipes doivent savoir ce que la plateforme garantit : disponibilité du service de livraison, délai de validation attendu, délai de support, conservation de l’audit et temps de traitement d’une demande d’exception. Les objectifs doivent être réalistes, mesurés et révisés en fonction de l’usage.

## 8. Gérer la dérive et les incidents

Une dérive est à la fois un problème de configuration et un signal opérationnel. Son traitement doit tenir compte de la gravité, de l’exposition, des données, de la disponibilité et de la cause.

### 8.1 Triage

Classe les écarts selon leur impact :
- **Critique :** exposition immédiate, perte de contrôle ou menace active ; déclencher la réponse à incident.
- **Élevé :** violation importante de politique ou risque de disponibilité ; traiter rapidement avec le propriétaire du domaine.
- **Modéré :** différence non urgente mais non souhaitée ; planifier une correction versionnée.
- **Faible :** écart documenté et acceptable dans le contexte ; conserver une échéance de réévaluation.

Ces catégories doivent être adaptées aux risques réels de l’organisation. Le classement n’est utile que si chaque classe déclenche une réponse connue.

### 8.2 Ne pas corriger toutes les dérives automatiquement

Une intervention manuelle peut avoir été faite pour rétablir un service. Une remédiation automatique qui restaure sans analyse l’ancienne configuration peut réintroduire la panne. Le système doit alerter, contextualiser et appliquer les corrections automatiques uniquement lorsque le comportement est sûr et explicitement autorisé.

### 8.3 Après un incident

Après une correction urgente, l’équipe doit réconcilier la référence versionnée avec l’état opérationnel, documenter la cause, vérifier les contrôles qui ont échoué et ajouter les protections nécessaires. Le retour d’expérience doit améliorer la plateforme, et pas seulement ajouter une nouvelle étape manuelle.

## 9. Préparer la reprise et la résilience

Sauvegarder la configuration, l’état de gestion et les données applicatives ne répond pas au même besoin. Une copie d’un état de gestion ne restaure pas les ressources ni leurs données. La stratégie de reprise doit distinguer les informations permettant de reconstruire le système des données qui doivent être restaurées depuis des sauvegardes applicatives.

Une procédure de reprise doit définir :
- les scénarios de perte et de corruption ;
- les responsables et leurs moyens d’escalade ;
- les données de référence à protéger ;
- les sauvegardes et leur fréquence ;
- les objectifs de temps et de perte de données acceptables ;
- les validations qui confirment le rétablissement ;
- les conditions de retour au fonctionnement normal.

Les exercices de reprise doivent être exécutés dans un environnement contrôlé. Ils doivent vérifier la capacité de retrouver les identifiants, les dépendances, les données et les permissions nécessaires, pas seulement la présence des sauvegardes.

## 10. Intégrer les coûts et la capacité dans la gouvernance

L’IaC peut contribuer à éviter les dépenses inutiles, mais la présence de code n’empêche pas les coûts de dériver. Les politiques doivent tenir compte de la capacité, de la durée de vie, de la criticité et du besoin métier.

Les contrôles possibles incluent les budgets, les limites de ressources, les étiquettes de propriétaire, les dates d’expiration, les rapports d’utilisation, la détection des environnements inactifs et les revues d’architecture. Les estimations de coût ne sont pas des factures garanties : l’usage réel, les transferts de données, la capacité réservée et les services annexes peuvent modifier le coût final.

Le nettoyage automatique doit être prudent. Une ressource apparemment inactive peut contenir des données ou servir de dépendance à un autre service. La suppression doit respecter le propriétaire, les règles de conservation et le niveau de risque.

## 11. Choisir des indicateurs de maturité utiles

Évite de mesurer la maturité par le nombre de fichiers, de modules ou de pipelines. Les indicateurs doivent mesurer l’efficacité et le risque du système.

| Indicateur | Ce qu’il aide à comprendre |
|---|---|
| Délai entre proposition et livraison | La capacité de la chaîne à faire avancer les changements |
| Taux d’échec des changements | La qualité des validations et de l’exploitation |
| Délai de détection d’une dérive | La capacité à découvrir un écart dangereux |
| Temps de correction d’un écart critique | L’efficacité de la réponse opérationnelle |
| Part des composants supportés | Le niveau de maîtrise du catalogue |
| Exceptions expirées encore actives | La qualité de la gouvernance |
| Ressources sans propriétaire ou expiration | La dette opérationnelle et financière |
| Taux de réussite des exercices de reprise | La capacité à restaurer effectivement les services |

Les indicateurs doivent être interprétés ensemble. Par exemple, réduire le délai de livraison en diminuant les tests n’est pas une amélioration si le taux d’échec augmente.

## 12. Architecture de référence

Une plateforme d’entreprise peut être représentée de manière simplifiée :

    Équipes produit
        |
        v
    Dépôts versionnés et catalogue de composants
        |
        v
    Revue + tests + politiques + aperçu
        |
        v
    Approbation proportionnée au risque
        |
        v
    Exécuteurs isolés et identités dédiées
        |
        v
    Comptes / environnements / fournisseurs
        |
        v
    Observabilité + coûts + audit + détection de dérive
        |
        v
    Retour d’expérience vers la plateforme

Les contrôles transverses — identité, politiques, audit, coûts et observabilité — doivent être cohérents sans retirer à chaque équipe la responsabilité de son application. La plateforme fournit un cadre commun et des mécanismes sûrs ; les équipes produit restent responsables de leurs exigences métier et des changements qu’elles demandent.

## 13. TP expert : construire le modèle opérationnel d’une plateforme IaC

### Situation

Une organisation possède quatre équipes, deux fournisseurs cloud et plusieurs outils de provisionnement et de configuration. Les équipes partagent des composants, mais l’audit ne permet pas toujours d’identifier qui a approuvé un changement. Les environnements temporaires consomment des ressources après la fin des projets et les exceptions de sécurité ne sont pas suivies.

### Étape A — Définir la gouvernance

Établis les rôles de la plateforme, des équipes produit, de la sécurité et des opérations. Identifie les décisions centralisées, celles qui restent locales et le processus d’exception.

### Étape B — Délimiter les domaines

Propose des frontières de gestion selon les propriétaires, les environnements, les données et le rayon d’impact. Définis les interfaces entre les outils et choisis un seul propriétaire par objet géré.

### Étape C — Créer la chaîne de preuve

Relie chaque demande de changement à une version, des tests, un aperçu, des approbations, une identité d’application et une vérification post-déploiement. Spécifie comment sont protégés les journaux et les artefacts sensibles.

### Étape D — Intégrer coûts et résilience

Définis des propriétaires et une durée de vie pour les environnements temporaires, une politique d’expiration, une procédure de nettoyage et un test de reprise. Toute suppression doit vérifier les données à conserver et les dépendances.

### Proposition de correction

Le modèle retient une plateforme centrale responsable des chemins recommandés, du catalogue, des politiques partagées et de l’identité d’exécution. Chaque équipe possède ses domaines et approuve les changements relevant de sa responsabilité. Les composants sont versionnés avec un contrat et une politique de retrait. Les pipelines appliquent des contrôles communs mais accordent des permissions selon l’environnement. Les exceptions sont limitées dans le temps et suivies. Les dérives critiques déclenchent un triage explicite. Les ressources temporaires portent un propriétaire et une date d’expiration, et les procédures de reprise sont testées régulièrement.

## 14. Étude de défaillance : l’automatisation rétablit une panne

### Situation

Un opérateur désactive temporairement une règle de sécurité afin de rétablir un service critique. Un mécanisme de remédiation remet immédiatement la règle précédente. La panne revient et la même action est répétée.

### Analyse

Le processus traite la dérive sans connaître le contexte opérationnel. Il n’existe pas de mécanisme d’exception d’urgence, de propriétaire chargé de la décision ni de synchronisation entre l’intervention et la référence approuvée. La correction automatique transforme un signal utile en boucle de panne.

### Procédure recommandée

Suspendre le mécanisme de remédiation concerné selon une procédure autorisée, évaluer le risque, documenter l’exception et sa durée, décider du changement acceptable avec les responsables du service et de la sécurité, mettre à jour la configuration de référence si le changement doit persister, puis réactiver le contrôle et vérifier le résultat. Après l’incident, ajouter un garde-fou pour que les futures remédiations connaissent les exceptions actives et les conditions d’arrêt.

## 15. Exercices corrigés

### Exercice 1 — Une équipe utilise une exception sans échéance

**Correction :** identifier le propriétaire et l’impact, ajouter une justification, des mesures compensatoires et une date de fin, puis vérifier périodiquement que l’exception reste nécessaire. Une exception permanente doit être réévaluée comme une règle générale.

### Exercice 2 — Deux outils gèrent le même objet

**Correction :** identifier le propriétaire de référence, geler les changements concurrents si le risque l’exige, comparer l’état réel, définir un transfert et prouver que l’ancien outil n’applique plus de modifications à cet objet.

### Exercice 3 — Les indicateurs de livraison s’améliorent, mais les incidents augmentent

**Correction :** ne pas conclure à une amélioration. Examiner les changements d’indicateurs, la qualité des tests, le taux d’échec après livraison et les types d’incident. Réintroduire les contrôles manquants et équilibrer délai, fiabilité et risque.

### Exercice 4 — Une sauvegarde existe, mais le test de reprise échoue

**Correction :** la sauvegarde n’est pas considérée comme fiable tant que la restauration n’est pas validée. Déterminer si la donnée, les permissions, les clés, les dépendances ou la procédure manquent, corriger la stratégie et refaire l’exercice dans un environnement sûr.

## 16. Projet final corrigé : proposer une plateforme IaC gouvernée

### Travail demandé

Conçois une plateforme pour plusieurs équipes, plusieurs fournisseurs et plusieurs outils. Elle doit offrir un catalogue de composants, une chaîne de livraison contrôlée, une gouvernance par politiques, une procédure d’exception, la gestion des coûts, une détection des dérives et une capacité de reprise vérifiable.

### Livrables attendus

1. Une matrice des responsabilités et des propriétaires.
2. Une architecture des dépôts et des frontières de gestion.
3. Un contrat et un cycle de vie pour les composants partagés.
4. Une chaîne de livraison avec contrôles, preuves et approbations.
5. Une stratégie d’identités et de gestion des artefacts sensibles.
6. Un processus de triage des dérives et des incidents.
7. Une politique de coût et de nettoyage des environnements.
8. Des objectifs de service et des indicateurs mesurables.
9. Un plan d’exercice de reprise et ses critères de réussite.

### Critères d’évaluation

Une proposition réussie délimite clairement les responsabilités, empêche la double gestion non contrôlée, rend les décisions auditables, limite les privilèges, mesure les risques, définit une procédure d’exception et démontre que la reprise a été testée. Les outils choisis doivent servir ce modèle et non le remplacer.

## 17. Conclusion

La maturité IaC se mesure à la capacité d’une organisation à livrer des changements compréhensibles, vérifiables et réversibles autant que possible. Une plateforme experte combine des frontières de responsabilité, des composants maintenus, des identités limitées, des politiques testées, des procédures d’incident, une gestion des coûts et des preuves d’audit. Elle laisse les équipes autonomes dans un cadre explicite, au lieu de les obliger à reproduire manuellement les mêmes décisions de sécurité et d’exploitation.

## Références utiles

- Terraform — gouvernance et exécution : https://developer.hashicorp.com/terraform
- Documentation OpenTofu : https://opentofu.org/docs/
- Open Policy Agent : https://www.openpolicyagent.org/docs/latest/
- Principes de sécurité GitHub Actions : https://docs.github.com/actions/security-guides
- AWS Well-Architected Framework : https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
- Azure Well-Architected Framework : https://learn.microsoft.com/azure/well-architected/