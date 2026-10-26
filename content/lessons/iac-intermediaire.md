# Ingénierie IaC et livraison contrôlée — Intermédiaire

> **Mise en contexte.** Une entreprise a plusieurs équipes qui livrent leur infrastructure avec des outils différents. Certaines créent leurs environnements depuis des dépôts personnels, d’autres utilisent des modules copiés et modifiés sans version commune. Les validations varient, les approbations ne sont pas toujours traçables et personne ne sait clairement qui doit traiter une dérive. Le problème ne se résout pas en ajoutant davantage de fichiers : il faut définir un système de livraison reproductible. Ce cours porte sur les pratiques de conception, de collaboration et de livraison. Les détails de syntaxe Terraform et les ateliers réseau restent dans le parcours Administration Réseaux.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir choisir une architecture de dépôt cohérente, définir les responsabilités entre composants, organiser des environnements isolés, concevoir un catalogue de composants réutilisables, construire une chaîne de contrôle, définir les tests adaptés, gérer les approbations et les identités d’exécution, promouvoir un changement entre environnements et organiser le traitement des dérives.

## Prérequis

Connaître le cycle de livraison avec Git, les bases de l’IaC et le rôle général d’un outil de provisionnement. Tu dois comprendre ce qu’est un environnement et savoir expliquer pourquoi une modification doit être vérifiée avant sa mise en production. Ce cours n’exige pas de créer un compte cloud.

## 1. Concevoir la plateforme avant de choisir les fichiers

L’ingénierie IaC consiste à rendre les changements d’infrastructure faciles à proposer, à contrôler et à exploiter sans donner à chaque contributeur des droits illimités.

Une plateforme d’équipe doit répondre à six questions :

- Qui possède chaque domaine d’infrastructure ?
- Où se trouve la définition de référence ?
- Comment les composants sont-ils réutilisés et versionnés ?
- Quels tests sont obligatoires avant une application ?
- Qui peut approuver une modification selon son risque ?
- Comment détecter et traiter un changement qui contourne le processus ?

Une réponse différente peut convenir à une petite équipe et à une organisation de plusieurs centaines de personnes. L’objectif n’est pas d’imposer la structure la plus compliquée, mais de faire correspondre le processus au risque et au périmètre.

## 2. Choisir l’organisation des dépôts

### 2.1 Monorepo

Un monorepo regroupe plusieurs composants ou environnements dans un dépôt commun. Il facilite les changements coordonnés, la découverte des conventions et la réutilisation de contrôles communs. En contrepartie, il peut accroître le bruit des revues, le temps des tests et la difficulté à séparer les droits si les règles sont mal conçues.

### 2.2 Plusieurs dépôts

Une approche multirepo sépare les composants ou les domaines de responsabilité. Elle peut simplifier les permissions et le cycle de publication, mais augmente les exigences de versionnement, de documentation, de découverte et de compatibilité entre dépôts.

### 2.3 Modèle hybride

Un modèle hybride peut conserver les modules partagés dans des dépôts versionnés et les configurations d’environnements dans des dépôts distincts. Il est utile lorsqu’il existe une équipe responsable des composants communs et des équipes qui les consomment.

### 2.4 Méthode de décision

La structure doit suivre le propriétaire et le rayon d’impact, pas uniquement la technologie utilisée. Avant de choisir, répertorie les équipes, les environnements, les niveaux d’accès, la fréquence des changements, les dépendances et les exigences d’audit. Teste ensuite le modèle sur un domaine limité.

## 3. Délimiter la responsabilité et l’isolation

### 3.1 Une ressource, un propriétaire clair

Il faut savoir quel processus a autorité pour modifier chaque ressource. Si plusieurs systèmes cherchent à gérer le même objet, ils risquent de se corriger mutuellement et de créer des changements imprévisibles.

Le modèle de responsabilité doit indiquer :
- le propriétaire opérationnel ;
- le dépôt et le processus de référence ;
- l’outil qui applique les changements ;
- les consommateurs autorisés ;
- les conditions de transfert de responsabilité ;
- le responsable de la correction en cas d’incident.

### 3.2 Séparer les environnements selon le risque

Développement, test et production ne devraient pas partager indistinctement les mêmes identités, secrets et autorisations. Les environnements doivent être isolés selon les conséquences d’une erreur, les contraintes réglementaires et la sensibilité des données.

Séparer les environnements ne signifie pas forcément dupliquer tout le code. Il est souvent préférable de réutiliser une configuration approuvée tout en conservant des paramètres, des identités, des politiques et des frontières de gestion adaptés à chaque environnement.

### 3.3 Définir le périmètre de gestion

Les frontières de responsabilité doivent limiter le rayon d’impact. Un changement sur un environnement temporaire ne devrait pas nécessiter des permissions administrateur sur l’organisation entière. Une ressource partagée exige un propriétaire et une procédure de changement qui tiennent compte de tous ses consommateurs.

## 4. Concevoir des composants réutilisables comme des produits

Un composant réutilisable ne se limite pas à un dossier que l’on copie dans plusieurs projets. Il fournit une interface stable, une version, des exemples, une politique de support et une procédure de retrait.

### 4.1 Définir un contrat

Un contrat de composant décrit :
- les paramètres obligatoires et les valeurs permises ;
- les sorties et leurs formats ;
- les préconditions et les hypothèses ;
- les responsabilités de sécurité ;
- les dépendances externes ;
- les ressources créées et les effets secondaires ;
- les erreurs attendues et la procédure de mise à jour.

Exemple de contrat conceptuel :

    Composant : environnement de test
    Entrées : propriétaire, région autorisée, durée de vie
    Garanties : réseau isolé, journalisation activée
    Restrictions : aucun accès administratif public
    Sorties : identifiants des ressources et points de contrôle
    Fin de vie : nettoyage après validation des données à conserver

Ce contrat décrit le comportement recherché. Il ne dépend pas de la syntaxe d’un outil particulier.

### 4.2 Versionner et faire évoluer

La version publiée doit être identifiable et immuable. Une modification incompatible ne devrait pas être introduite silencieusement sous la même version. Une politique de versionnement explicite différencie les corrections compatibles, les ajouts compatibles et les changements qui nécessitent une migration.

Avant de publier une nouvelle version, teste le composant, vérifie les exemples et documente les changements. Une version obsolète doit être retirée progressivement : annoncer la fin du support, fournir une cible de migration, suivre les consommateurs encore présents et éviter de supprimer brutalement une dépendance utilisée en production.

### 4.3 Mesurer la réutilisation

La réutilisation n’est pas une fin en soi. Un composant partagé qui masque trop de paramètres, impose des hypothèses implicites ou force des exceptions permanentes peut augmenter le risque. Préfère un petit contrat compréhensible à une abstraction générale qui tente de prendre en charge tous les cas.

## 5. Concevoir une chaîne de livraison

Une chaîne de livraison décrit les contrôles qui doivent s’exécuter avant une application. Les étapes peuvent être adaptées au contexte, mais chaque étape doit apporter une garantie identifiable.

    Modification proposée
           |
           v
    Contrôle de format et de structure
           |
           v
    Tests de composants et contrôles statiques
           |
           v
    Génération de l’aperçu des changements
           |
           v
    Tests de politiques et de conformité
           |
           v
    Revue humaine et approbation du risque
           |
           v
    Application par une identité limitée
           |
           v
    Vérification et audit

La chaîne doit échouer de manière visible lorsqu’un contrôle obligatoire ne passe pas. Il faut aussi éviter de confondre un avertissement, une validation automatique et une autorisation d’application.

### 5.1 Les différents types de contrôle

| Contrôle | Question traitée |
|---|---|
| Structure et format | Le dépôt suit-il les conventions attendues ? |
| Tests de composants | Les entrées valides et invalides produisent-elles le comportement prévu ? |
| Analyse statique | Existe-t-il des erreurs connues ou des motifs risqués ? |
| Politique | Le changement respecte-t-il les règles de l’organisation ? |
| Aperçu des effets | Quelles ressources seront ajoutées, modifiées ou supprimées ? |
| Revue humaine | Le changement répond-il au besoin et son risque est-il acceptable ? |
| Vérification après application | Le service réel respecte-t-il les critères d’acceptation ? |

Aucun contrôle isolé ne suffit. Par exemple, une analyse statique peut repérer un accès public interdit, mais elle ne prouve pas qu’une application répond correctement après déploiement.

## 6. Organiser la promotion entre environnements

Un changement est proposé, validé, essayé dans un environnement adapté, puis promu vers les environnements plus sensibles. La promotion doit conserver une identité claire : version du code, dépendances, artefacts de validation, auteur, approbateurs et résultat du déploiement.

Évite de reconstruire arbitrairement une configuration différente au moment de la production. Si des paramètres changent entre les environnements, ils doivent être identifiés, validés et audités. Un artefact ou un aperçu qui contient des données sensibles doit être protégé comme une donnée confidentielle et supprimé selon une politique définie.

Les règles d’approbation doivent dépendre du risque. Une mise à jour documentaire n’exige pas forcément la même approbation qu’une modification de routage, une suppression de stockage ou une ouverture d’accès.

## 7. Sécuriser la chaîne d’exécution

### 7.1 Identités

La chaîne de livraison devrait utiliser des identités dédiées et à privilèges minimaux. Lorsque la plateforme le permet, une identité temporaire liée à une exécution approuvée est préférable à une clé durable partagée entre plusieurs pipelines.

Il faut distinguer les permissions nécessaires pour lire le dépôt, valider le code, produire un aperçu et appliquer les changements. Une étape de test ne devrait pas recevoir automatiquement les droits de production.

### 7.2 Déclencheurs et événements non fiables

Une exécution déclenchée par une contribution externe ou par un événement non approuvé ne doit pas hériter de secrets de production. Il faut examiner les déclencheurs du pipeline, les permissions de jeton, les dépendances téléchargées et les scripts qui s’exécutent pendant les contrôles.

### 7.3 Journalisation

Les journaux doivent permettre de comprendre qui a proposé, approuvé et appliqué un changement. Ils ne doivent pas exposer des secrets, des plans sensibles ou des informations confidentielles inutilement. La durée de conservation doit correspondre aux besoins d’exploitation et d’audit.

## 8. Tests à plusieurs niveaux

La stratégie de test doit être rapide pour les contrôles fréquents et plus approfondie pour les changements risqués.

- **Tests de contrat :** vérifier les entrées, sorties et contraintes du composant.
- **Tests unitaires :** contrôler une règle ou une transformation sans créer de vraies ressources.
- **Tests de politique :** soumettre des exemples conformes et non conformes.
- **Tests d’intégration :** confirmer l’interaction de composants dans un environnement contrôlé.
- **Tests après livraison :** vérifier disponibilité, connectivité, permissions, journalisation et critères métier.

Les tests ne doivent pas créer involontairement des ressources facturables. Ils doivent avoir un périmètre, un compte ou un environnement clairement défini, un nettoyage et une limite de temps. Les résultats doivent être reproductibles et attribuables à la version testée.

## 9. Traiter les dérives sans automatisme aveugle

Une dérive peut venir d’une intervention urgente, d’un changement manuel, d’un déploiement d’un autre outil ou d’une évolution externe. La réponse doit distinguer trois questions :

1. L’écart est-il dangereux maintenant ?
2. La configuration approuvée reste-t-elle la bonne référence ?
3. Faut-il corriger le code, l’infrastructure réelle ou les deux ?

Une procédure raisonnable consiste à détecter l’écart, évaluer son impact, désigner un responsable, décider de la correction, obtenir l’approbation adaptée, appliquer la correction puis vérifier et documenter le résultat.

La correction automatique est dangereuse si elle annule une mesure d’urgence, détruit une ressource ou ignore un changement légitime. Les écarts critiques peuvent déclencher une alerte immédiate, mais leur remédiation doit respecter une politique claire.

## 10. Modèle de travail Git et revue

Une demande de changement de qualité contient au minimum :
- la raison métier et le résultat attendu ;
- le domaine et les environnements touchés ;
- les contrôles effectués et les résultats ;
- l’aperçu des effets ;
- les risques et les opérations destructives ;
- le plan de retour ou de récupération ;
- la personne qui vérifiera le résultat.

La revue doit rechercher les changements inattendus, les valeurs trop permissives, les dépendances non maîtrisées, les écarts de configuration entre environnements et les effets sur les consommateurs. Une approbation ne doit pas être une formalité automatique qui ignore le contenu du changement.

## 11. TP guidé : concevoir une chaîne de livraison d’équipe

### Situation

Trois équipes partagent un catalogue de composants d’infrastructure. Elles veulent livrer les modifications en développement, test et production. La production exige une approbation explicite ; les équipes ne doivent pas partager de clés d’accès durables. Tu dois concevoir le processus avant de choisir une implémentation.

### Étape A — Établir les responsabilités

Pour chaque domaine, identifie le propriétaire, les consommateurs, le dépôt de référence et les permissions nécessaires. Décide où un composant partagé est publié et comment ses utilisateurs sont avertis d’une nouvelle version.

### Étape B — Définir les contrôles

Propose des tests de structure, des tests de contrat, des politiques de sécurité, un aperçu des effets et une revue des changements destructifs. Définis quels contrôles bloquent la chaîne et lesquels produisent seulement un avertissement.

### Étape C — Définir la promotion

Précise comment la même version est identifiée d’un environnement à l’autre, quelles différences de paramètres sont permises et qui autorise la production. Les secrets de production ne doivent pas être exposés au processus de validation d’une contribution non fiable.

### Étape D — Définir l’exploitation

Décide qui reçoit les alertes de dérive, qui évalue l’impact, comment les corrections sont journalisées et comment les environnements temporaires sont nettoyés.

### Proposition de correction

Le dépôt des composants partagés est géré par une équipe propriétaire. Les configurations d’environnement sont versionnées séparément ou dans des espaces clairement isolés selon la stratégie retenue. Chaque changement ouvre une revue, exécute des tests de contrat, des contrôles de sécurité et produit un aperçu. Une promotion en production nécessite une approbation indépendante. Les applications utilisent des identités séparées et minimales. Les dérives critiques déclenchent une procédure de réponse documentée, tandis que les écarts non critiques sont priorisés et corrigés via le même processus versionné.

## 12. Diagnostic de situations fréquentes

### Les pipelines sont tous lents

Ne commence pas par augmenter le parallélisme. Identifie les tâches qui prennent du temps, les téléchargements répétés, les contrôles redondants, les accès distants et les dépendances entre étapes. Mets en cache uniquement les éléments dont l’intégrité peut être garantie, puis mesure le résultat.

### Les équipes utilisent des versions incompatibles du même composant

Établis une politique de versionnement, documente la compatibilité, publie une version de migration et identifie les consommateurs. N’impose pas une mise à jour globale non testée sur toutes les productions.

### Une validation réussit alors qu’un changement reste dangereux

Vérifie que les contrôles couvrent le risque réel et pas seulement la syntaxe. Ajoute des tests de politique et une revue des effets, puis protège les opérations destructives par une approbation adaptée.

### Une clé de production est présente dans un pipeline de test

Révoque ou remplace la clé, vérifie les journaux et les exécutions concernées, limite les permissions, puis passe à une identité dédiée. Supprimer la clé du dernier commit ne suffit pas si elle reste valide dans l’historique ou les journaux.

## 13. Exercices corrigés

### Exercice 1 — Monorepo ou multirepo ?

Deux équipes autonomes livrent des composants avec des droits différents, mais certains composants partagés ont besoin d’un cycle de publication indépendant.

**Correction :** un modèle hybride peut séparer les composants partagés versionnés des configurations propres à chaque équipe. Un monorepo reste possible si les règles d’accès, les propriétaires et les contrôles permettent la même isolation.

### Exercice 2 — Promotion en production

Une équipe veut recréer un plan différent en production sans conserver de trace de la version validée en test.

**Correction :** cette stratégie réduit la traçabilité et peut introduire des différences non examinées. Il faut identifier la version promue, documenter les paramètres spécifiques, reconstruire l’aperçu dans le contexte approprié et exiger l’approbation adaptée.

### Exercice 3 — Une dérive légitime

Après un incident, un administrateur a désactivé temporairement une règle qui bloquait le trafic. La remédiation automatisée envisage de rétablir immédiatement la règle.

**Correction :** ne pas lancer une correction aveugle. Évaluer le risque actuel, consigner l’exception, définir une échéance, mettre à jour la référence si nécessaire et restaurer la protection dès que le service est prêt.

### Exercice 4 — Composant partagé sans version

Chaque équipe copie le même composant et ajoute ses propres options. Une correction de sécurité doit être appliquée partout.

**Correction :** définir un contrat, publier un composant versionné, identifier les consommateurs, tester une migration et suivre l’adoption. Éviter de multiplier les forks permanents sans propriétaire ni échéance.

## 14. Défi final corrigé : proposer une plateforme de livraison

### Travail demandé

Conçois une chaîne d’IaC pour plusieurs équipes avec trois environnements, un catalogue de composants, des contrôles de sécurité, une identité distincte par étape, une procédure de promotion et un traitement des dérives.

### Correction attendue

Une architecture cohérente identifie un propriétaire par domaine, sépare les permissions selon l’environnement, versionne les composants et définit un contrat stable. La chaîne teste les changements dès la proposition, produit un aperçu contrôlable, vérifie les politiques, exige une approbation pour les opérations sensibles et conserve la preuve de la version appliquée. La détection des dérives est reliée à un processus de triage avec responsable, niveau d’urgence, correction versionnée et vérification après application.

### Critères d’évaluation

La solution doit expliciter les responsabilités, isoler les identités, définir des contrôles bloquants, protéger les artefacts sensibles, éviter la double gestion d’une ressource et garder une trace de chaque décision importante.

## 15. À retenir

L’ingénierie IaC intermédiaire porte sur la façon dont une équipe conçoit, teste, approuve, livre et maintient ses changements. Les modules sont des produits avec un contrat et un cycle de vie. Les pipelines sont des barrières de contrôle, pas de simples scripts de commandes. Les environnements, les identités, les états et les droits doivent suivre des responsabilités explicites. Le niveau expert prolongera ces principes à une plateforme commune, à plusieurs équipes, à plusieurs outils et à des exigences d’organisation plus larges.

## Références utiles

- Bonnes pratiques Terraform : https://developer.hashicorp.com/terraform/intro
- Documentation OpenTofu : https://opentofu.org/docs/
- GitHub Actions — sécurité : https://docs.github.com/actions/security-guides
- GitLab CI/CD : https://docs.gitlab.com/ee/ci/
- Open Policy Agent : https://www.openpolicyagent.org/docs/latest/