# Fondamentaux de l’Infrastructure as Code — Débutant

> **Mise en contexte.** Une équipe recrée manuellement son environnement de test à chaque nouvelle version. Les paramètres changent d’une personne à l’autre, certaines règles de sécurité sont oubliées et il devient difficile de savoir pourquoi deux environnements ne se comportent pas de la même façon. L’Infrastructure as Code (IaC) vise à rendre ces changements explicites, revus et reproductibles. Ce cours enseigne les principes communs à différentes familles d’outils. Le cours Terraform du parcours Administration Réseaux reste la référence pour apprendre en détail HCL, les ressources et les commandes Terraform.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois pouvoir expliquer les avantages et les limites de l’IaC, distinguer une approche déclarative d’une approche impérative, décrire le cycle de livraison d’un changement d’infrastructure, reconnaître les principaux types d’outils, repérer les risques liés aux secrets et aux droits d’accès, et préparer une demande de changement qui peut être revue par une équipe.

## Prérequis

Il est utile de connaître les bases de Git, des réseaux et des environnements cloud, mais aucun compte cloud n’est nécessaire pour les activités de ce cours. Les ateliers portent sur la conception et la revue d’un changement. Ils ne créent aucune ressource payante.

## 1. Pourquoi décrire l’infrastructure dans des fichiers ?

Une infrastructure peut inclure des réseaux virtuels, des sous-réseaux, des machines, des bases de données, des règles de pare-feu, des comptes, des politiques d’accès et des services applicatifs. Lorsqu’une personne configure tout depuis une console, le résultat peut fonctionner, mais une partie de la procédure reste dans sa mémoire.

Cette connaissance implicite produit plusieurs difficultés :

- une autre personne ne peut pas reproduire précisément l’environnement ;
- les étapes oubliées sont difficiles à identifier ;
- l’historique des changements est dispersé entre des journaux et des souvenirs ;
- la comparaison entre développement, test et production devient compliquée ;
- une modification urgente peut être appliquée sans revue ni procédure de retour.

L’IaC consiste à représenter tout ou partie de l’infrastructure dans des fichiers maintenus comme du code. Ces fichiers deviennent un support de discussion, de validation et d’automatisation. Ils ne remplacent toutefois ni la supervision, ni les sauvegardes, ni les décisions d’architecture.

## 2. Les notions fondamentales

### 2.1 L’état souhaité et l’état réel

L’**état souhaité** décrit ce que l’équipe entend obtenir. L’**état réel** correspond aux ressources qui existent effectivement dans l’environnement. L’outil ou le processus de livraison compare ces deux états afin d’identifier les opérations nécessaires.

Exemple : la configuration approuvée indique qu’un sous-réseau de test doit utiliser une plage réseau précise et que l’accès administratif doit être limité à un point d’entrée connu. Si une intervention manuelle élargit le filtrage, l’état réel ne correspond plus à l’état souhaité.

Le code ne garantit pas à lui seul que l’état réel restera conforme. Il faut également des permissions adaptées, une détection des écarts et des procédures de correction.

### 2.2 Déclaratif et impératif

Une approche déclarative exprime le résultat attendu. Une approche impérative décrit les actions à exécuter dans un ordre donné.

Exemple conceptuel :

    Déclaratif :
      service web = présent
      capacité = 2 instances
      accès public = HTTPS seulement

    Impératif :
      créer une instance
      configurer le service
      ajouter une règle HTTPS
      vérifier que l’instance est opérationnelle

Les deux approches peuvent être utiles. La déclaration facilite la comparaison entre le résultat attendu et les ressources existantes. Un script impératif peut être pertinent pour une procédure spécifique, mais il faut réfléchir à ce qui se passe si le script est relancé après une interruption.

### 2.3 Répétabilité, idempotence et dérive

La **répétabilité** signifie qu’une procédure documentée peut être reproduite dans des conditions connues. L’**idempotence** désigne, dans un contexte donné, une opération dont la répétition ne produit pas de changement supplémentaire une fois le résultat atteint. La **dérive** est un écart entre la configuration de référence et l’infrastructure réelle.

Ces notions sont liées mais ne sont pas synonymes. Un processus peut être répétable sans être idempotent. Une dérive peut apparaître après une intervention manuelle, un incident, une mise à jour externe ou une erreur de configuration.

## 3. Comprendre le cycle de changement

Un changement d’infrastructure ne devrait pas commencer directement par une commande d’application. Il doit suivre un cycle contrôlé.

    Demande de changement
            |
            v
    Analyse du besoin et du risque
            |
            v
    Modification versionnée
            |
            v
    Vérifications automatiques
            |
            v
    Revue humaine et aperçu des effets
            |
            v
    Approbation adaptée au risque
            |
            v
    Application contrôlée
            |
            v
    Vérification du résultat et traçabilité

Chaque étape répond à une question. La demande explique pourquoi la modification est nécessaire. La revue vérifie si le changement répond au besoin. L’aperçu des effets permet de repérer les opérations inattendues. La vérification post-déploiement confirme que le service fonctionne réellement.

Une validation technique réussie ne vaut pas approbation métier. Un fichier peut être syntaxiquement valide tout en autorisant une règle de réseau trop large ou en supprimant une ressource critique.

## 4. Les grandes familles d’outils

Les outils d’IaC ont des domaines d’application qui se recoupent parfois.

| Famille | Exemples | Usage fréquent |
|---|---|---|
| Provisionnement déclaratif multi-environnements | Terraform, OpenTofu | Décrire et gérer des ressources d’infrastructure au moyen de providers |
| Services d’infrastructure d’un fournisseur | AWS CloudFormation, Azure Bicep | Décrire les ressources d’un environnement cloud donné |
| Gestion de configuration | Ansible | Configurer des systèmes, des services et des équipements après leur création |
| Infrastructure définie en langage de programmation | Pulumi | Décrire l’infrastructure avec des langages de programmation pris en charge |
| Construction d’images et déploiement applicatif | Packer, Helm et outils associés | Préparer des images ou déployer des composants qui s’appuient sur une infrastructure |

Ce tableau n’est pas un classement universel. Le choix dépend du périmètre, des compétences de l’équipe, des contraintes de sécurité, des plateformes prises en charge, de la maintenance et du coût d’exploitation.

Il est fréquent de combiner plusieurs outils. La difficulté est alors de délimiter clairement les responsabilités : deux systèmes ne doivent pas gérer indépendamment le même objet sans stratégie explicite.

## 5. Les fichiers font partie d’un processus d’équipe

Un dépôt IaC utile doit permettre à un collègue de comprendre ce qui est géré et comment un changement est autorisé. Une organisation simple peut ressembler à ceci :

    infrastructure/
      README.md
      environments/
        dev/
        test/
        prod/
      components/
      policies/
      tests/
      docs/

Cette structure est illustrative, pas une règle à appliquer mécaniquement. Un petit projet peut utiliser une structure plus simple. Une organisation importante peut séparer les dépôts par domaine ou par responsabilité. La décision doit refléter le périmètre réel de gestion et les droits nécessaires.

Les fichiers de référence doivent expliquer les entrées attendues, les environnements concernés, les commandes ou processus autorisés, les tests à lancer et les conditions d’approbation. Les secrets et les données d’état ne doivent pas être ajoutés au dépôt par commodité.

### 5.1 Pourquoi Git est essentiel

Git fournit un historique des modifications et permet de proposer une modification sans l’appliquer immédiatement à l’infrastructure. Une pull request ou une merge request sert à expliquer le besoin, examiner la différence, lancer des contrôles et conserver la décision de revue.

Le message de commit doit expliquer l’intention. Le titre d’une demande de fusion devrait indiquer le résultat recherché. Le contenu de la revue doit porter sur les conséquences du changement, pas uniquement sur la mise en forme du fichier.

## 6. Les risques à connaître dès le début

### 6.1 Secrets et identités

Les mots de passe, clés d’accès et jetons ne doivent pas être commis dans le dépôt. Il faut préférer un gestionnaire de secrets et des identités temporaires lorsque la plateforme le permet. Les identités d’exécution doivent disposer uniquement des permissions nécessaires à leur tâche.

### 6.2 Destruction involontaire

Une modification courte peut supprimer une base de données, remplacer une adresse ou interrompre des connexions. Avant de l’appliquer, il faut examiner les effets prévus et identifier les ressources critiques. Une sauvegarde utile doit être testée : la présence d’un fichier de sauvegarde ne prouve pas qu’une restauration est possible.

### 6.3 Écart entre validation et réalité

Un contrôle statique peut repérer une erreur de format ou une valeur interdite, mais il ne prouve pas que l’application fonctionnera. Il faut des tests adaptés et une vérification après déploiement.

### 6.4 Coûts et nettoyage

Un environnement de laboratoire peut consommer des ressources ou laisser des ressources actives après l’exercice. Le propriétaire, le budget, la durée de vie et la procédure de nettoyage doivent être définis avant de créer les ressources.

## 7. TP guidé : préparer une demande de changement IaC

### Situation

Une équipe veut créer un environnement de test pour une nouvelle application. L’environnement doit être isolé de la production, accessible uniquement aux personnes de l’équipe et automatiquement supprimé lorsqu’il n’est plus utilisé. Le travail demandé consiste à préparer une demande de changement sûre, pas à créer réellement des ressources.

### Étape A — Décrire le résultat attendu

Rédige les exigences sous forme vérifiable : isolation réseau, identité autorisée, journalisation, durée de vie, responsable et procédure de nettoyage. Évite les formulations vagues telles que « sécurisé » ou « correctement configuré ».

### Étape B — Définir le périmètre

Identifie les objets concernés, le dépôt propriétaire, les systèmes qui les gèrent et les dépendances. Si une ressource est déjà contrôlée par un autre outil, il faut convenir d’un transfert de responsabilité ou d’une interface entre outils.

### Étape C — Préparer la revue

La demande de fusion doit comprendre le contexte, les objets affectés, les contrôles exécutés, les effets attendus, les risques, le plan de retour et la personne chargée de vérifier le déploiement.

### Étape D — Préparer la fin de vie

Définis comment détecter les ressources encore présentes, qui autorise le nettoyage et comment préserver les données qui doivent être conservées. La suppression d’un environnement ne doit pas entraîner celle d’une donnée partagée ou d’une ressource de production.

## 8. Exercices corrigés

### Exercice 1 — Choisir une approche

Une équipe veut décrire la création de réseaux et de sous-réseaux dans plusieurs environnements cloud. Elle souhaite versionner les changements et revoir les effets avant application.

**Correction :** un outil de provisionnement déclaratif comme Terraform ou OpenTofu peut convenir, sous réserve de vérifier les providers, la gouvernance, les contraintes et les compétences. Le choix ne doit pas être fait uniquement parce qu’un outil est populaire.

### Exercice 2 — Repérer l’approche impérative

Un script crée systématiquement une nouvelle règle de filtrage à chaque exécution, sans vérifier si cette règle existe déjà.

**Correction :** le script risque de produire des doublons et ne garantit pas un résultat stable après plusieurs exécutions. Il faut rendre l’opération idempotente ou utiliser un mécanisme déclaratif qui compare l’état attendu à l’état existant.

### Exercice 3 — Identifier une dérive

Un administrateur élargit manuellement une règle d’accès après le déploiement. Aucun changement n’est enregistré dans le dépôt.

**Correction :** l’état réel ne correspond plus à la configuration versionnée. Il faut évaluer le risque immédiat, enregistrer l’écart, décider si la correction doit être appliquée dans le code ou si le changement manuel est légitime, puis rétablir une référence approuvée.

### Exercice 4 — Validation réussie, changement dangereux

Un contrôle automatique réussit, mais l’aperçu indique la suppression d’une base de données contenant des données utiles.

**Correction :** il ne faut pas appliquer automatiquement le changement. Le responsable doit comprendre la cause, vérifier les dépendances et les sauvegardes, puis faire corriger le plan ou approuver explicitement la suppression selon une procédure adaptée.

## 9. Défi final corrigé : définir un processus de changement sûr

### Travail demandé

Propose un processus de livraison pour un environnement de test. Il doit inclure le dépôt de référence, la revue, les validations, l’approbation, la gestion des secrets, la vérification après déploiement et le nettoyage.

### Correction attendue

Une solution acceptable contient les éléments suivants :

1. Une demande documentée avec un propriétaire, un périmètre, des critères d’acceptation et un budget.
2. Une modification versionnée proposée par branche, puis relue par une autre personne.
3. Des contrôles automatiques portant sur la structure, les tests, les règles de sécurité et les politiques de l’équipe.
4. Un aperçu des opérations prévues, examiné avant toute application.
5. Une identité d’exécution limitée et aucun secret stocké dans le dépôt.
6. Une approbation proportionnée au risque, avec une approbation renforcée pour toute destruction sensible.
7. Une vérification après déploiement, une trace de la décision et une procédure de retour.
8. Un mécanisme de nettoyage assorti d’une date d’expiration et d’une protection des données à conserver.

### Critères d’évaluation

La proposition est complète si chaque étape a un responsable, si les contrôles ne sont pas confondus avec les approbations, si les ressources critiques sont protégées et si le nettoyage ne peut pas supprimer involontairement une ressource partagée.

## 10. À retenir

L’IaC est une méthode de gestion et de livraison de l’infrastructure, pas seulement un format de fichier. Elle repose sur une configuration explicite, un historique versionné, des contrôles, une revue proportionnée au risque et une observation de l’état réel. Les cours Terraform du parcours Administration Réseaux approfondissent la mise en œuvre technique de ces principes avec un outil précis. Le parcours IaC les replace dans une démarche utilisable par une équipe, quel que soit l’outil retenu.

## Références utiles

- Principes Terraform : https://developer.hashicorp.com/terraform/intro
- Documentation OpenTofu : https://opentofu.org/docs/
- AWS CloudFormation : https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html
- Azure Bicep : https://learn.microsoft.com/azure/azure-resource-manager/bicep/overview
- Ansible : https://docs.ansible.com/ansible/latest/getting_started/index.html