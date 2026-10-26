
# Infrastructure as Code avec Terraform — Niveau expert

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** maîtriser HCL, les providers, les modules, les tests, les plans et la gestion élémentaire du state.  
> **Objectif :** concevoir une plateforme Terraform sécurisée, reproductible, gouvernée et capable de maîtriser les changements d'infrastructure à l'échelle d'une organisation.


> **Lien avec le parcours DevOps IaC :** ce cours approfondit les mécanismes Terraform de production, notamment le state, les plans, la dérive et les opérations contrôlées. Le cours expert IaC traite plutôt du modèle opérationnel d’entreprise, de la gouvernance multi-outils, du catalogue, des coûts et de la résilience de la plateforme.

## Sommaire

1. Architecture d'entreprise
2. Stratégie des states et backends distants
3. Verrouillage et concurrence
4. Plans immuables et promotion des changements
5. Gouvernance et politiques de sécurité
6. Modules et contrats d'architecture
7. Détection des dérives
8. Importation et refactorisation
9. Gestion avancée des secrets
10. CI/CD de production
11. Reprise après incident
12. Observabilité et indicateurs
13. Architecture de référence
14. Atelier expert
15. Étude de défaillance
16. Évaluation corrigée


# 1. Architecture d'entreprise

## 1.1 Terraform comme chaîne de gestion

Une architecture Terraform mature ne se limite pas à des fichiers `.tf` correctement formatés.

Elle doit définir comment une modification est proposée, validée, planifiée, autorisée, appliquée et contrôlée.

Les responsabilités essentielles sont :

- les sources de configuration ;
- les modules et leurs dépendances ;
- le state et son stockage ;
- les providers et les identités d'accès ;
- les contrôles statiques et les tests ;
- les plans et leur approbation ;
- l'application des changements ;
- la vérification opérationnelle ;
- la traçabilité et la récupération.

Chaque étape doit avoir un objectif clair et une limite de responsabilité définie.

## 1.2 Objectifs experts

À la fin du cours, vous serez capable de :

1. concevoir une architecture Terraform multi-environnements ;
2. protéger le state distant et empêcher les écritures concurrentes ;
3. distinguer un plan préparé d'un plan autorisé à être appliqué ;
4. construire un workflow de promotion et d'approbation ;
5. définir des politiques de sécurité vérifiables ;
6. organiser des modules et des interfaces stables ;
7. diagnostiquer les dérives entre la configuration et l'infrastructure ;
8. importer et déplacer des ressources sans provoquer de destructions inutiles ;
9. limiter l'exposition des données sensibles ;
10. préparer des mécanismes de récupération et d'audit.

## 1.3 Principes fondamentaux

Une plateforme Terraform d'entreprise doit préserver au minimum les propriétés suivantes :

**Traçabilité :** chaque changement est lié à un commit, un plan et une exécution.

**Reproductibilité :** les versions des outils, des providers et des modules sont contrôlées.

**Isolation :** les environnements et leurs états sont séparés selon les risques.

**Moindre privilège :** chaque identité ne reçoit que les capacités nécessaires.

**Approbation :** les changements sensibles sont soumis à des contrôles explicites.

**Vérification :** le résultat appliqué est contrôlé et pas seulement supposé.

**Récupération :** les erreurs de state, les changements partiels et les ressources inattendues peuvent être traités méthodiquement.


# 2. Stratégie des states et backends distants

## 2.1 Pourquoi le state est critique

Terraform utilise le state pour relier les déclarations de configuration aux ressources qu'il gère.

Le state est une donnée opérationnelle centrale. Sa perte ou sa corruption peut compliquer fortement les opérations ultérieures.

Il peut contenir :

- des identifiants de ressources ;
- des adresses et propriétés réseau ;
- des attributs retournés par les providers ;
- des valeurs sensibles ;
- des informations utiles à la gestion des dépendances.

Le state doit donc être protégé avec le même sérieux que les données de gestion de l'infrastructure.

## 2.2 State local et state distant

| Critère | State local | State distant |
|---|---|---|
| Mise en place | Simple | Nécessite un backend |
| Collaboration | Difficile à coordonner | Adaptée à une équipe si le backend est bien configuré |
| Verrouillage | Pas de coordination distribuée automatique entre copies locales | Disponible selon le backend |
| Sauvegarde | À organiser | Dépend des fonctionnalités et de la politique du backend |
| Contrôle d'accès | Droits du système de fichiers | Permissions et politiques du service |
| Usage conseillé | Laboratoire local | Équipes et infrastructures gérées en commun |

Un backend distant ne rend pas automatiquement le state sûr. Les permissions, les sauvegardes, le chiffrement, le verrouillage et les procédures de récupération doivent être configurés.

## 2.3 Exemple de backend S3 avec verrouillage natif

L'exemple suivant illustre un backend AWS S3. Le bucket doit exister avant l'initialisation du backend et doit être configuré avec les protections appropriées.

Dans `versions.tf` :

```hcl
terraform {
  required_version = ">= 1.10.0, < 2.0.0"

  backend "s3" {
    bucket       = "example-company-terraform-state"
    key          = "network/production/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

Les noms de bucket, le chemin du state et la région sont des valeurs fictives à remplacer. Cet exemple ne crée pas le bucket du backend : celui-ci doit être préparé au préalable avec les règles d'accès, de sauvegarde et de récupération appropriées.

Le backend S3 permet d'utiliser un fichier de verrouillage dédié avec `use_lockfile = true`. La gestion des identifiants AWS doit reposer sur le mécanisme d'authentification approuvé, et non sur des clés inscrites dans le fichier Terraform.

Référence : https://developer.hashicorp.com/terraform/language/backend/s3

## 2.4 Protéger le stockage

Pour un backend S3 de production, examinez notamment :

- l'activation de la gestion de versions du bucket ;
- le chiffrement au repos ;
- la validation de l'identité TLS pendant les communications ;
- les permissions minimales sur le state et le fichier de verrouillage ;
- les restrictions sur les comptes autorisés à lire ou modifier les états ;
- la surveillance des accès ;
- les mécanismes de récupération après suppression accidentelle ;
- les obligations de conservation et de conformité.

Ne donnez pas à tous les développeurs un accès de modification aux states de production simplement parce qu'ils contribuent aux fichiers Terraform.

## 2.5 Migrer vers un backend distant

Une migration nécessite de choisir le backend cible, de vérifier les prérequis et de planifier le transfert.

Une séquence de principe :

1. identifier le state local faisant autorité ;
2. sauvegarder l'état actuel selon la procédure approuvée ;
3. créer et sécuriser le stockage distant ;
4. configurer le bloc `backend` ;
5. exécuter `terraform init -migrate-state` lorsque cette option correspond à la migration prévue ;
6. examiner les messages et confirmer le transfert ;
7. vérifier que le state distant contient les objets attendus ;
8. tester un plan sans changement inattendu ;
9. protéger ou supprimer les copies locales conformément à la politique.

N'effacez pas l'ancien state avant d'avoir vérifié que la migration est terminée et que l'état distant est exploitable.


# 3. Verrouillage et concurrence

## 3.1 Pourquoi verrouiller le state ?

Supposons que deux opérateurs lancent simultanément des opérations Terraform utilisant le même state.

Si les deux tentent de modifier l'état sans coordination, leurs changements peuvent entrer en conflit et provoquer une incohérence entre les opérations enregistrées et les ressources réelles.

Le verrouillage permet au backend, lorsqu'il le prend en charge, de protéger les opérations qui écrivent le state.

Terraform indique normalement qu'une opération est bloquée si elle ne parvient pas à obtenir le verrou. Il ne faut pas contourner ce contrôle sans avoir compris la situation.

## 3.2 Le verrouillage n'est pas une transaction réseau globale

Le verrouillage du state protège la coordination des opérations qui utilisent le backend concerné. Il ne verrouille pas l'ensemble des équipements réseau, des API externes et des interventions manuelles.

Des changements externes peuvent encore survenir. Ils doivent être traités avec des contrôles de dérive, des procédures de changement et des permissions adaptées.

## 3.3 Le danger de `force-unlock`

La commande :

```bash
terraform force-unlock <LOCK_ID>
```

peut être nécessaire si un verrou est resté bloqué après une opération interrompue et qu'il est établi qu'il appartient à votre exécution.

Elle ne doit pas être utilisée comme moyen ordinaire de résoudre une attente.

**Ne forcez jamais le déverrouillage d'un état tant qu'une autre opération légitime peut encore l'utiliser.** Des écrivains concurrents risquent de corrompre l'état ou de produire des changements incohérents.

Référence : https://developer.hashicorp.com/terraform/language/state/locking


# 4. Plans immuables et promotion des changements

## 4.1 Configuration, plan et application

Un plan est calculé à partir de la configuration, de l'état, des providers et des données observées. Il représente les actions que Terraform prévoit d'effectuer.

Le plan ne doit pas être assimilé à une autorisation. Un plan acceptable techniquement peut tout de même violer une politique de sécurité ou dépasser le périmètre approuvé.

Une chaîne gouvernée sépare donc :

1. la préparation du plan ;
2. l'analyse des résultats ;
3. la décision d'approbation ;
4. l'application du plan approuvé ;
5. la vérification opérationnelle.

## 4.2 Enregistrer et inspecter un plan

```bash
terraform plan -out=production.tfplan
terraform show production.tfplan
```

Le fichier de plan doit être conservé dans un espace adapté à la sensibilité des données qu'il contient.

Une représentation JSON peut être générée pour une analyse automatisée :

```bash
terraform show -json production.tfplan > production-plan.json
```

Le fichier JSON peut également contenir des informations sensibles. Il ne doit pas être publié dans un dépôt public ni transmis sans contrôle d'accès.

## 4.3 Appliquer le plan examiné

Lorsqu'un plan précis a été examiné et autorisé :

```bash
terraform apply production.tfplan
```

Cette commande applique les actions enregistrées dans le plan lorsqu'elles restent applicables.

Le plan peut être rejeté s'il est devenu obsolète. Il ne faut pas contourner cette protection en recréant discrètement un plan différent après l'approbation.

En cas de changement de l'état ou de modification du contexte, le processus doit revenir à la planification, produire un nouveau résultat puis demander une nouvelle autorisation si la politique l'exige.

## 4.4 Un plan n'est pas éternellement valide

Entre la création du plan et son application, des conditions peuvent changer :

- une ressource a été modifiée manuellement ;
- un autre opérateur a appliqué une modification ;
- un objet externe a disparu ;
- un quota ou une permission a changé ;
- la configuration ou les dépendances ont évolué.

Le processus doit gérer cette situation comme un événement nécessitant une nouvelle évaluation. Le plan enregistré doit rester lié à la configuration, au state et au contexte pour lesquels il a été calculé.

## 4.5 Schéma de promotion d'une release

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="tf-expert-plan-title tf-expert-plan-desc">
  <title id="tf-expert-plan-title">Promotion contrôlée d'un plan Terraform</title>
  <desc id="tf-expert-plan-desc">Un commit validé produit un plan protégé. Le plan est examiné et approuvé avant son application exacte. L'état résultant est vérifié. Si le plan devient obsolète ou si un contrôle critique échoue, l'application s'arrête et le processus retourne à l'évaluation.</desc>
  <defs>
    <marker id="tf-expert-plan-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .tp-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .tp-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .tp-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .tp-stop{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .tp-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .tp-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .tp-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tf-expert-plan-arrow);animation:tp-dash 1.8s linear infinite}
      .tp-fail{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#tf-expert-plan-arrow);animation:tp-dash 1.8s linear infinite}
      @keyframes tp-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UN PLAN IDENTIFIÉ, EXAMINÉ ET APPLIQUÉ SOUS CONTRÔLE</text>
  <rect class="tp-box" x="25" y="78" width="175" height="76" rx="10"/>
  <text class="tp-title" x="112" y="106" text-anchor="middle">Commit validé</text>
  <text class="tp-text" x="112" y="129" text-anchor="middle">Code + dépendances</text>
  <rect class="tp-box" x="235" y="78" width="175" height="76" rx="10"/>
  <text class="tp-title" x="322" y="106" text-anchor="middle">Plan protégé</text>
  <text class="tp-text" x="322" y="129" text-anchor="middle">Actions prédites</text>
  <rect class="tp-gate" x="445" y="78" width="175" height="76" rx="10"/>
  <text class="tp-title" x="532" y="106" text-anchor="middle">Revue + décision</text>
  <text class="tp-text" x="532" y="129" text-anchor="middle">Politique + approbateur</text>
  <rect class="tp-ok" x="655" y="78" width="150" height="76" rx="10"/>
  <text class="tp-title" x="730" y="106" text-anchor="middle">Apply du plan</text>
  <text class="tp-text" x="730" y="129" text-anchor="middle">Même artefact</text>
  <rect class="tp-ok" x="840" y="78" width="135" height="76" rx="10"/>
  <text class="tp-title" x="907" y="106" text-anchor="middle">Contrôle</text>
  <text class="tp-text" x="907" y="129" text-anchor="middle">Résultat</text>
  <path class="tp-flow" d="M200 116 H228"/>
  <path class="tp-flow" d="M410 116 H438"/>
  <path class="tp-flow" d="M620 116 H648"/>
  <path class="tp-flow" d="M805 116 H833"/>
  <rect class="tp-stop" x="270" y="245" width="460" height="65" rx="10"/>
  <text class="tp-title" x="500" y="271" text-anchor="middle">Plan obsolète ou contrôle critique en échec</text>
  <text class="tp-text" x="500" y="291" text-anchor="middle">Arrêter, réévaluer l'état et préparer un nouveau plan si nécessaire</text>
  <path class="tp-fail" d="M730 154 V205 H680 V238"/>
  <path class="tp-fail" d="M270 277 H112 V198 H112 V162"/>
  <text class="tp-text" x="500" y="345" text-anchor="middle">Un plan différent exige une nouvelle évaluation et, si nécessaire, une nouvelle approbation.</text>
  <text class="tp-text" x="500" y="365" text-anchor="middle">Protégez l'artefact de plan comme une donnée sensible.</text>
</svg>


# 5. Gouvernance et politiques de sécurité

## 5.1 Pourquoi une politique as code ?

Une revue humaine peut détecter des erreurs, mais certaines règles doivent être appliquées de manière systématique.

Une politique peut, par exemple, interdire :

- certains types de ressources en production ;
- les réseaux dont le CIDR n'appartient pas aux plages autorisées ;
- les règles d'accès qui ouvrent inutilement des services à Internet ;
- la désactivation du chiffrement requis ;
- des tags obligatoires absents ;
- des tailles de ressources dépassant une limite approuvée ;
- des régions non autorisées ;
- des suppressions de ressources protégées sans procédure particulière.

La politique doit être testable et associée à un niveau d'application explicite : avertissement, blocage ou dérogation contrôlée.

## 5.2 Où exécuter les politiques ?

Les contrôles peuvent être exécutés :

- pendant la validation du code ;
- lors de l'analyse du plan ;
- dans une plateforme de gouvernance Terraform ;
- dans un pipeline séparé ;
- après l'application pour vérifier les propriétés réelles.

Une politique qui ne lit que le code peut manquer des risques visibles uniquement dans le plan ou dans l'état réel.

## 5.3 Exemple de règles réseau

Considérons les règles suivantes :

```text
POLITIQUE RÉSEAU

Règle 1 :
  Tous les réseaux doivent utiliser des plages CIDR approuvées.

Règle 2 :
  Aucun service administratif ne doit être ouvert à tous
  les réseaux si cette exposition n'est pas explicitement autorisée.

Règle 3 :
  Chaque ressource de production doit posséder les tags obligatoires.

Règle 4 :
  Les changements destructifs de ressources critiques
  exigent une approbation renforcée.

Règle 5 :
  L'application en production doit utiliser une identité
  de déploiement distincte de l'identité de validation.
```

Ces règles sont des exemples de politique. Pour être appliquées, elles doivent être traduites en contrôles adaptés aux ressources et aux données du plan.

## 5.4 Sentinel, OPA et validations personnalisées

Selon l'environnement, des politiques peuvent être écrites avec les mécanismes pris en charge par la plateforme Terraform ou avec des outils externes de politique as code.

Quelle que soit la technologie retenue, les règles doivent :

- traiter les cas permis et interdits ;
- échouer de manière lisible ;
- disposer de tests ;
- indiquer la ressource et la propriété concernées ;
- être versionnées ;
- faire l'objet d'une procédure d'exception contrôlée.

Un contrôle de politique ne doit pas se réduire à chercher un texte approximatif dans un fichier de configuration. Il doit analyser les données pertinentes.


# 6. Modules et contrats d'architecture

## 6.1 Les modules comme interfaces

Un module partagé définit une interface entre l'équipe qui le maintient et les équipes qui l'utilisent.

Ses variables représentent des entrées validées, et ses sorties exposent les valeurs utiles. Sa responsabilité doit être compréhensible.

Un module réseau peut gérer un composant clairement délimité, comme un VPC et ses sous-réseaux. Il ne devrait pas introduire silencieusement des règles de sécurité non documentées ou des ressources dont les consommateurs ne connaissent pas les conséquences.

## 6.2 Stratégie de versions

Les modules publiés doivent avoir une politique de version explicite.

Une mise à jour peut modifier :

- les types et validations des variables ;
- les sorties ;
- les dépendances entre ressources ;
- les attributs qui entraînent un remplacement ;
- les conventions de tags ;
- les hypothèses de sécurité ;
- les versions requises de Terraform ou des providers.

Une version du module doit être testée avant d'être promue dans les environnements consommateurs.

## 6.3 Contrat de module

Documentez au minimum :

- la fonction du module ;
- les variables et valeurs par défaut ;
- les contraintes ;
- les sorties ;
- les versions compatibles ;
- les dépendances ;
- les ressources créées ;
- les effets possibles d'une mise à jour ;
- la stratégie de test ;
- les limitations connues ;
- la méthode de migration.

Un module partagé sans contrat documenté devient rapidement une source de dépendances difficiles à maîtriser.

## 6.4 Arbre de modules

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="340" viewBox="0 0 960 340" role="img" aria-labelledby="tf-mod-title tf-mod-desc">
  <title id="tf-mod-title">Architecture modulaire Terraform</title>
  <desc id="tf-mod-desc">Le module racine compose des modules réseau, sécurité et observabilité. Chaque module possède une interface d'entrée et des sorties. Les flèches animées représentent les dépendances entre composants.</desc>
  <defs>
    <marker id="tf-mod-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .md-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .md-root{fill:#18314d;stroke:#a5b4fc;stroke-width:2}
      .md-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .md-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .md-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tf-mod-arrow);animation:md-dash 1.8s linear infinite}
      @keyframes md-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="338" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">COMPOSER LES COMPOSANTS SANS MASQUER LEURS RESPONSABILITÉS</text>
  <rect class="md-root" x="330" y="60" width="300" height="65" rx="12"/>
  <text class="md-title" x="480" y="87" text-anchor="middle">Module racine</text>
  <text class="md-text" x="480" y="108" text-anchor="middle">Entrées d'environnement</text>
  <rect class="md-box" x="35" y="205" width="250" height="75" rx="12"/>
  <text class="md-title" x="160" y="233" text-anchor="middle">Module réseau</text>
  <text class="md-text" x="160" y="255" text-anchor="middle">VPC, sous-réseaux, routes</text>
  <rect class="md-box" x="355" y="205" width="250" height="75" rx="12"/>
  <text class="md-title" x="480" y="233" text-anchor="middle">Module sécurité</text>
  <text class="md-text" x="480" y="255" text-anchor="middle">Règles et politiques</text>
  <rect class="md-box" x="675" y="205" width="250" height="75" rx="12"/>
  <text class="md-title" x="800" y="233" text-anchor="middle">Module observabilité</text>
  <text class="md-text" x="800" y="255" text-anchor="middle">Collecte et alarmes</text>
  <path class="md-flow" d="M420 125 L160 197"/>
  <path class="md-flow" d="M480 125 V197"/>
  <path class="md-flow" d="M540 125 L800 197"/>
  <text class="md-text" x="480" y="312" text-anchor="middle">Un module doit proposer une interface documentée et une responsabilité identifiable.</text>
</svg>


# 7. Détection des dérives

## 7.1 Qu'est-ce qu'une dérive ?

Une dérive survient lorsque l'infrastructure réelle ne correspond plus aux hypothèses ou aux déclarations du projet.

Elle peut être provoquée par :

- un changement manuel ;
- une autre automatisation ;
- une opération externe ;
- une ressource supprimée ou modifiée ;
- un changement du service cloud ;
- une modification d'une dépendance ;
- une valeur dynamique qui n'est pas gérée par Terraform.

Une dérive ne signifie pas automatiquement qu'il faut appliquer immédiatement le contenu du dépôt. Il faut identifier la cause, les conséquences et l'autorité qui doit décider de la correction.

## 7.2 Examiner un plan de rafraîchissement

La commande suivante peut être utilisée pour examiner un plan qui ne cherche qu'à actualiser les informations d'état :

```bash
terraform plan -refresh-only
```

Elle permet d'inspecter les différences entre les données suivies par le state et les informations obtenues à partir des providers.

Cette commande ne doit pas être confondue avec une correction de l'infrastructure. Elle sert à évaluer les changements d'état liés à l'actualisation.

Avant de mettre à jour le state, examinez les résultats et déterminez si le décalage reflète une modification légitime, une dérive à corriger ou un problème d'accès ou de collecte.

## 7.3 Deux types de dérive

**Dérive d'infrastructure :** une propriété gérée a été modifiée en dehors du processus Terraform.

**Dérive d'état :** le state ne correspond plus à la représentation actuelle des ressources ou à leurs associations.

Les deux situations peuvent être liées, mais elles ne sont pas identiques. Il faut les diagnostiquer avant de choisir une action.

## 7.4 Cycle de gestion des dérives

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-labelledby="tf-drift-title tf-drift-desc">
  <title id="tf-drift-title">Cycle de gestion des dérives Terraform</title>
  <desc id="tf-drift-desc">Un contrôle périodique compare l'infrastructure à la configuration. Un écart déclenche une analyse pour déterminer s'il est légitime, accidentel ou lié à une mauvaise collecte. Une décision approuvée mène à une correction ou une mise à jour contrôlée de l'état.</desc>
  <defs>
    <marker id="tf-drift-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .dr-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .dr-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .dr-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .dr-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .dr-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .dr-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tf-drift-arrow);animation:dr-dash 1.8s linear infinite}
      @keyframes dr-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DÉTECTER N'EST PAS CORRIGER AUTOMATIQUEMENT</text>
  <rect class="dr-box" x="25" y="90" width="195" height="80" rx="10"/>
  <text class="dr-title" x="122" y="119" text-anchor="middle">Collecte + plan</text>
  <text class="dr-text" x="122" y="142" text-anchor="middle">État observé</text>
  <rect class="dr-gate" x="270" y="90" width="195" height="80" rx="10"/>
  <text class="dr-title" x="367" y="119" text-anchor="middle">Analyser l'écart</text>
  <text class="dr-text" x="367" y="142" text-anchor="middle">Cause et impact</text>
  <rect class="dr-gate" x="515" y="90" width="195" height="80" rx="10"/>
  <text class="dr-title" x="612" y="119" text-anchor="middle">Décision</text>
  <text class="dr-text" x="612" y="142" text-anchor="middle">Règle + approbation</text>
  <rect class="dr-ok" x="760" y="90" width="175" height="80" rx="10"/>
  <text class="dr-title" x="847" y="119" text-anchor="middle">Action contrôlée</text>
  <text class="dr-text" x="847" y="142" text-anchor="middle">Correction ou état</text>
  <path class="dr-flow" d="M220 130 H263"/>
  <path class="dr-flow" d="M465 130 H508"/>
  <path class="dr-flow" d="M710 130 H753"/>
  <text class="dr-text" x="480" y="240" text-anchor="middle">Un écart peut être légitime, accidentel ou causé par un problème de collecte.</text>
  <text class="dr-text" x="480" y="264" text-anchor="middle">Ne forcez pas une correction avant d'avoir identifié la situation réelle.</text>
  <text class="dr-text" x="480" y="300" text-anchor="middle">Conservez le rapport, la décision, l'action et les résultats de vérification.</text>
</svg>


# 8. Importation et refactorisation

## 8.1 Importer une ressource existante

Il arrive qu'une infrastructure soit déjà en production avant l'adoption de Terraform. Il peut alors être nécessaire d'importer des ressources dans le state et de décrire leur configuration.

Une déclaration `import` permet d'exprimer l'intention d'importation dans la configuration, lorsque le provider prend en charge la ressource concernée.

Exemple :

```hcl
import {
  to = aws_vpc.main
  id = "vpc-0123456789abcdef0"
}
```

L'identifiant ci-dessus est fictif. Remplacez-le par celui d'une ressource dont vous êtes autorisé à gérer le cycle de vie.

L'importation ne signifie pas que toute la configuration de la ressource a déjà été rédigée correctement. Il faut décrire les paramètres attendus, examiner le plan et déterminer les éventuelles différences avant une application.

Ne tentez pas d'importer une ressource dans un projet en production sans avoir identifié le state concerné et vérifié que la ressource n'est pas déjà gérée ailleurs.

## 8.2 Refactoriser sans recréer inutilement

Lorsqu'une ressource est déplacée vers un module ou renommée dans le code, Terraform peut parfois interpréter le changement comme la suppression d'une adresse suivie et la création d'une nouvelle adresse.

Le bloc `moved` permet d'indiquer une transition d'adresse de ressource ou de module afin d'éviter une destruction et une recréation inutiles lorsque le déplacement est compatible.

Exemple conceptuel :

```hcl
moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}
```

Ce bloc illustre un déplacement depuis une ressource du module racine vers une ressource interne du module `network`. Il doit correspondre à la refactorisation réellement effectuée.

Un bloc `moved` ne transforme pas automatiquement une ressource d'un type en un autre type incompatible. Le changement doit être vérifié avec un plan.

## 8.3 Import et refactorisation : différences

| Mécanisme | Objectif |
|---|---|
| `import` | Associer une ressource existante à une adresse suivie par Terraform |
| `moved` | Déclarer une transition d'adresse dans la configuration |
| `terraform state mv` | Opérer un déplacement d'adresse dans le state via la CLI |
| `terraform state rm` | Retirer une association du state sans détruire automatiquement l'objet distant |

Ces mécanismes ne sont pas interchangeables. Ils doivent être choisis selon l'objectif, et les modifications d'état doivent être sauvegardées et planifiées.


# 9. Gestion avancée des secrets

## 9.1 Le marquage `sensitive`

Exemple :

```hcl
variable "api_token" {
  description = "Jeton du service externe"
  type        = string
  sensitive   = true
}
```

Le marquage `sensitive` permet notamment de masquer la valeur dans certaines sorties de la CLI et dans les interfaces qui tiennent compte de cette propriété.

Il ne garantit pas que la valeur est absente du state ou des plans. Le traitement réel dépend des arguments utilisés et du provider.

## 9.2 Valeurs éphémères

Les valeurs éphémères (*ephemeral*) peuvent être disponibles pendant l'exécution sans être enregistrées dans les fichiers de state et de plan, dans les contextes permis par Terraform.

Exemple de variable :

```hcl
variable "temporary_api_token" {
  description = "Jeton utilisé temporairement pendant une opération"
  type        = string
  sensitive   = true
  ephemeral   = true
}
```

Les valeurs éphémères existent à l'exécution mais sont soumises à des restrictions d'utilisation. Elles doivent être utilisées uniquement lorsque le flux de données et le provider sont compatibles.

La prise en charge de `ephemeral` pour les variables et sorties nécessite Terraform 1.10 ou une version ultérieure. Les arguments de ressources permettant d'écrire sans conserver certaines valeurs dépendent également de la version et du provider.

## 9.3 Ne pas confondre masquage et absence de stockage

| Mécanisme | Masque la valeur dans certaines sorties | Empêche automatiquement tout stockage dans le state |
|---|---|---|
| `sensitive = true` | Oui, selon le contexte | Non |
| `ephemeral = true` | Pas seul dans tous les contextes | Permet l'omission du state et des plans dans les usages pris en charge |
| Gestionnaire de secrets | Dépend de l'outil et de l'intégration | Dépend de la manière dont la valeur est ensuite utilisée |
| Backend distant protégé | Pas nécessairement | Non, il protège surtout le stockage et les accès |

Il faut analyser le parcours complet du secret : variable, provider, ressource, sortie, state, plan, logs et artefacts.

Référence : https://developer.hashicorp.com/terraform/language/manage-sensitive-data


# 10. CI/CD de production

## 10.1 Séparer validation et application

Une architecture de production peut utiliser plusieurs étapes :

1. vérifications statiques ;
2. validation Terraform ;
3. tests de modules ;
4. génération et examen du plan ;
5. contrôles de politique ;
6. approbation de la release ;
7. application du plan autorisé ;
8. contrôles après application ;
9. enregistrement du résultat.

Le workflow de validation doit éviter d'avoir des permissions de production inutiles.

Pour des modifications sensibles, le processus d'approbation doit être configuré sur la plateforme et vérifié indépendamment du fichier YAML.

## 10.2 Exemple de workflow de validation

Le fichier ci-dessous illustre le contrôle du code. Il ne possède pas d'identifiants cloud et ne tente pas de créer des ressources.

`.github/workflows/validate.yml` :

```yaml
name: Terraform CI

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout source
        uses: actions/checkout@v7

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v4
        with:
          terraform_version: "1.10.0"

      - name: Format
        run: terraform fmt -check -recursive

      - name: Initialize without remote backend
        run: terraform init -backend=false

      - name: Validate
        run: terraform validate

      - name: Test
        run: terraform test
```

Les versions mentionnées sont des exemples de configuration à maintenir selon la politique de dépendances du dépôt. Vérifiez la disponibilité, la compatibilité et la confiance de chaque action avant son adoption en production.

Cette CI ne remplace pas les contrôles de politique et les tests qui nécessitent l'accès à un environnement réel. Elle n'a volontairement aucune étape `apply`.

## 10.3 Concevoir un déploiement protégé

Un workflow d'application en production devrait utiliser :

- une identité dédiée à l'exécution ;
- des permissions limitées ;
- un backend et un state correctement sélectionnés ;
- un plan traçable ;
- une approbation requise configurée sur la plateforme ;
- une politique de refus des changements non autorisés ;
- une stratégie de vérification après application ;
- une procédure d'interruption et de récupération.

La méthode d'authentification doit suivre les recommandations actuelles de la plateforme. Lorsqu'une fédération d'identité ou des identifiants de courte durée sont disponibles et adaptés, ils peuvent réduire le besoin de secrets persistants.

## 10.4 Promotion et non-reconstruction arbitraire

L'approbation doit viser un changement identifié, et non une intention vague.

Si la configuration ou le state évolue après l'examen du plan, le processus doit évaluer le nouveau contexte. Il ne doit pas appliquer silencieusement un plan recalculé différent de celui qui a été examiné.

Les fichiers de plan et les rapports de production doivent être accessibles uniquement aux personnes et systèmes qui en ont besoin.


# 11. Reprise après incident

## 11.1 Les situations possibles

Un incident Terraform peut être provoqué par :

- une application partielle ;
- un timeout d'API ;
- une interruption de session ;
- la perte d'un verrou ;
- un state devenu indisponible ;
- un changement manuel externe ;
- un plan contenant une destruction inattendue ;
- une erreur de permissions ;
- une migration de state incomplète ;
- une ressource supprimée en dehors de Terraform.

Chaque situation nécessite un diagnostic différent.

## 11.2 Principes de récupération

1. arrêter les opérations concurrentes ou dépendantes lorsque cela est nécessaire ;
2. préserver les logs et les identifiants de run ;
3. examiner le verrouillage et l'état courant ;
4. vérifier ce qui a été appliqué dans l'infrastructure ;
5. identifier les associations entre state et ressources ;
6. établir un plan de récupération avant toute modification du state ;
7. effectuer les opérations contrôlées ;
8. vérifier l'infrastructure et le state après récupération ;
9. documenter la cause et les mesures correctives.

Une récupération ne doit pas commencer par la suppression arbitraire du fichier state.

## 11.3 La destruction n'est pas un rollback universel

Un `terraform destroy` ne constitue pas la méthode générale de retour arrière d'un changement de production.

Il peut supprimer des ressources encore nécessaires, interrompre des services et entraîner une perte de données. Le rollback doit être adapté au changement et à l'état réel de l'infrastructure.

Dans certains cas, une correction en avant peut être plus sûre qu'un retour à l'état précédent.


# 12. Observabilité et indicateurs

## 12.1 Journal d'exécution

Un journal d'exécution doit permettre de relier :

- commit ;
- plan ;
- identité ayant lancé le run ;
- environnement ;
- ressources ciblées ;
- résultat des politiques ;
- décision d'approbation ;
- début et fin d'application ;
- contrôles post-application ;
- erreurs et actions de récupération.

Les journaux doivent éviter les secrets et les valeurs sensibles inutiles.

## 12.2 Indicateurs de qualité

| Indicateur | Utilité |
|---|---|
| Taux de réussite de validation | Qualité des configurations soumises |
| Nombre de remplacements inattendus | Stabilité des changements |
| Taux de changements échoués | Fiabilité de la chaîne |
| Taux de dérive | Écart entre les déclarations et l'infrastructure |
| Durée de récupération | Capacité de rétablissement |
| Nombre de verrous forcés | Signal possible de problèmes opérationnels |
| Changements appliqués sans post-contrôle | Indicateur de lacune de gouvernance |
| Échecs de politique as code | Conformité et qualité des propositions |

Ces mesures doivent servir à améliorer le processus, pas à encourager des objectifs statistiques qui compromettraient la sécurité.

## 12.3 Audit et amélioration continue

Après un incident, demandez-vous :

- le plan permettait-il de comprendre l'impact ?
- les contrôles couvraient-ils le risque ?
- l'identité utilisée avait-elle les permissions nécessaires et uniquement celles-ci ?
- le pipeline a-t-il appliqué exactement le plan examiné ?
- l'état était-il protégé et récupérable ?
- l'erreur a-t-elle été détectée rapidement ?
- la procédure de récupération était-elle appropriée ?

Les réponses doivent conduire à des contrôles testables, des modifications de politique et une documentation corrigée.


# 13. Architecture de référence

## 13.1 Vue de bout en bout

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="410" viewBox="0 0 1000 410" role="img" aria-labelledby="tf-enterprise-title tf-enterprise-desc">
  <title id="tf-enterprise-title">Architecture Terraform d'entreprise</title>
  <desc id="tf-enterprise-desc">Le dépôt est validé et testé. Un plan est créé et soumis à la politique et à l'approbation. Le state distant coordonne l'exécution autorisée. Après application, les résultats sont vérifiés et consignés. Un échec critique mène à une récupération contrôlée.</desc>
  <defs>
    <marker id="tf-enterprise-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .te-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .te-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .te-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .te-stop{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .te-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .te-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .te-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tf-enterprise-arrow);animation:te-dash 1.8s linear infinite}
      .te-fail{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#tf-enterprise-arrow);animation:te-dash 1.8s linear infinite}
      @keyframes te-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="408" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">GOUVERNER LE CHANGEMENT DE BOUT EN BOUT</text>
  <rect class="te-box" x="25" y="70" width="170" height="70" rx="10"/>
  <text class="te-title" x="110" y="97" text-anchor="middle">Git + modules</text>
  <text class="te-text" x="110" y="120" text-anchor="middle">Sources identifiées</text>
  <rect class="te-box" x="225" y="70" width="170" height="70" rx="10"/>
  <text class="te-title" x="310" y="97" text-anchor="middle">Tests + CI</text>
  <text class="te-text" x="310" y="120" text-anchor="middle">Qualité</text>
  <rect class="te-box" x="425" y="70" width="170" height="70" rx="10"/>
  <text class="te-title" x="510" y="97" text-anchor="middle">Plan protégé</text>
  <text class="te-text" x="510" y="120" text-anchor="middle">Actions prévues</text>
  <rect class="te-gate" x="625" y="70" width="170" height="70" rx="10"/>
  <text class="te-title" x="710" y="97" text-anchor="middle">Politique + accord</text>
  <text class="te-text" x="710" y="120" text-anchor="middle">Autorisation</text>
  <rect class="te-ok" x="825" y="70" width="150" height="70" rx="10"/>
  <text class="te-title" x="900" y="97" text-anchor="middle">Apply</text>
  <text class="te-text" x="900" y="120" text-anchor="middle">Plan approuvé</text>
  <path class="te-flow" d="M195 105 H218"/>
  <path class="te-flow" d="M395 105 H418"/>
  <path class="te-flow" d="M595 105 H618"/>
  <path class="te-flow" d="M795 105 H818"/>
  <rect class="te-box" x="300" y="220" width="400" height="70" rx="10"/>
  <text class="te-title" x="500" y="248" text-anchor="middle">State distant + verrouillage</text>
  <text class="te-text" x="500" y="270" text-anchor="middle">Coordination et traçabilité</text>
  <path class="te-flow" d="M900 140 V190 H700 V228"/>
  <rect class="te-ok" x="740" y="320" width="230" height="60" rx="10"/>
  <text class="te-title" x="855" y="344" text-anchor="middle">Post-contrôles + audit</text>
  <text class="te-text" x="855" y="365" text-anchor="middle">Résultat et preuves</text>
  <path class="te-flow" d="M700 255 H730 V350 H732"/>
  <rect class="te-stop" x="30" y="320" width="230" height="60" rx="10"/>
  <text class="te-title" x="145" y="344" text-anchor="middle">Échec critique</text>
  <text class="te-text" x="145" y="365" text-anchor="middle">Stop + diagnostic</text>
  <path class="te-fail" d="M300 255 H145 V312"/>
  <text class="te-text" x="500" y="405" text-anchor="middle">Chaque étape doit laisser une preuve vérifiable et un état d'exécution identifiable.</text>
</svg>

## 13.2 Propriétés attendues

Une plateforme opérationnelle doit permettre d'identifier exactement :

- ce qui est proposé ;
- ce qui a été planifié ;
- ce qui a été approuvé ;
- ce qui a été appliqué ;
- ce qui a été vérifié ;
- ce qui doit être corrigé.

Cette séparation est particulièrement importante pour les ressources réseau, car un changement apparemment limité peut affecter des systèmes et services dépendants.


# 14. Atelier expert

## Scénario

Une équipe exploite un réseau cloud dont les ressources sont suivies par Terraform. Elle veut déplacer la configuration du réseau vers un module partagé, protéger le state et instaurer une procédure d'approbation des plans de production.

L'atelier est architectural : ne migrez pas un state de production sans autorisation, sauvegarde et procédure de migration validée.

## Étape A — Examiner le projet existant

Identifiez :

- le backend actuel ;
- les ressources suivies ;
- les contraintes de versions ;
- les dépendances ;
- les sorties consommées par d'autres modules ;
- les valeurs sensibles ;
- les éventuels changements manuels.

Conservez un état initial exploitable.

## Étape B — Préparer la refactorisation

Créez le module partagé, ses variables et ses sorties.

Si des ressources changent d'adresse Terraform sans changer d'identité réelle, préparez les `moved` blocs nécessaires lorsque le déplacement est compatible.

Exécutez un plan et examinez les destructions, créations et remplacements. La refactorisation ne doit pas être supposée sans risque simplement parce que le code paraît plus propre.

## Étape C — Protéger le state

Préparez le backend distant, ses permissions, le chiffrement, les sauvegardes et le verrouillage.

Planifiez la migration et vérifiez après l'initialisation que les objets attendus sont toujours associés au state.

## Étape D — Ajouter les contrôles de politique

Écrivez des règles testables portant sur les réseaux autorisés, les paramètres de sécurité et les ressources critiques.

Chaque règle doit posséder des cas de test permis et interdits.

## Étape E — Construire le workflow de promotion

Préparez une séquence où :

1. la CI valide le code ;
2. un plan est généré ;
3. le plan est protégé et inspecté ;
4. les contrôles de politique sont évalués ;
5. une personne autorisée approuve la release ;
6. le plan autorisé est appliqué ;
7. l'infrastructure et le state sont vérifiés ;
8. le résultat est enregistré.

## Étape F — Préparer la récupération

Définissez la procédure à appliquer si le plan devient obsolète, si le state est inaccessible ou si l'application ne produit pas le résultat attendu.

La procédure doit commencer par un diagnostic et éviter les modifications manuelles arbitraires du state.


# 15. Étude de défaillance

## Situation

Un administrateur modifie manuellement une règle de routage dans le cloud. Le prochain plan Terraform prévoit de rétablir l'ancienne valeur. L'équipe ne sait pas si la modification manuelle corrigeait un incident ou introduisait une dérive.

## Analyse

Appliquer automatiquement le plan pourrait supprimer une correction nécessaire. Ignorer indéfiniment la dérive pourrait également laisser une infrastructure non conforme.

Les questions à examiner sont :

- quel acteur a modifié la ressource ?
- existe-t-il un ticket ou un incident associé ?
- la modification est-elle conforme à la politique ?
- le fichier Terraform doit-il être mis à jour ?
- une exception temporaire a-t-elle été autorisée ?
- la ressource est-elle dans un état stable ?
- quels services seront touchés si la configuration est rétablie ?

## Procédure recommandée

1. Suspendre l'application automatique de ce changement sensible.
2. Collecter l'état et le plan courants.
3. Rechercher la cause de la modification manuelle.
4. Comparer les impacts de l'état réel et de l'état déclaré.
5. Décider si l'infrastructure doit être corrigée ou si le code doit être mis à jour.
6. Soumettre la décision à revue.
7. Produire un nouveau plan.
8. Appliquer après autorisation.
9. Vérifier les services concernés.
10. Documenter la cause et renforcer les contrôles nécessaires.

**Leçon :** détecter une dérive ne suffit pas. Il faut comprendre si elle représente une erreur, une correction légitime ou une divergence de source de vérité.


# 16. Évaluation corrigée

## Questions

1. Quel est le rôle du state Terraform ?
2. Pourquoi un backend distant doit-il être sécurisé ?
3. À quoi sert le verrouillage du state ?
4. Pourquoi un plan approuvé ne doit-il pas être remplacé discrètement par un autre ?
5. Quelle différence existe entre détection de dérive et correction de dérive ?
6. Qu'apporte une politique as code ?
7. Quel est le rôle d'un bloc `moved` ?
8. Quel est le rôle d'une déclaration `import` ?
9. Pourquoi `sensitive` ne garantit-il pas l'absence de stockage d'une valeur ?
10. Pourquoi un plan enregistré doit-il être protégé ?
11. Pourquoi le `force-unlock` est-il dangereux ?
12. Que faut-il faire lorsqu'une application Terraform se termine avec un résultat inconnu ?

## Corrigé

**1. Le state**

Il maintient les correspondances entre les ressources gérées et les objets d'infrastructure suivis par Terraform.

**2. Sécurisation du backend**

Le state peut contenir des propriétés d'infrastructure et des secrets. L'accès, le stockage et les sauvegardes doivent être protégés.

**3. Verrouillage**

Il évite certaines écritures concurrentes sur le même state lorsque le backend prend en charge le mécanisme.

**4. Plan approuvé**

Un plan différent peut contenir des actions différentes de celles qui ont été examinées. Toute modification importante du contexte doit déclencher une nouvelle évaluation et éventuellement une nouvelle approbation.

**5. Détection et correction**

La détection révèle l'écart. La correction implique une décision et une action destinées à rétablir l'état attendu.

**6. Politique as code**

Elle applique des règles de manière reproductible et vérifiable sur les configurations ou les plans.

**7. Bloc `moved`**

Il décrit une transition d'adresse Terraform pour éviter des destructions et recréations inutiles lors de refactorisations compatibles.

**8. Bloc `import`**

Il décrit l'intention d'associer une ressource existante à une adresse suivie par Terraform.

**9. Limites de `sensitive`**

Il masque des valeurs dans certains affichages, mais n'empêche pas à lui seul leur conservation dans le state.

**10. Protection des plans**

Un plan peut contenir des informations sensibles et représente des actions préparées. Il doit être conservé dans un espace dont l'accès est contrôlé.

**11. Danger du `force-unlock`**

Il peut supprimer un verrou encore légitime, ce qui risque de permettre des écritures concurrentes.

**12. Résultat inconnu**

Il faut préserver les logs, vérifier l'état et l'infrastructure actuels, déterminer les opérations déjà appliquées et choisir une stratégie de récupération autorisée.


# Conclusion — Le niveau expert

Terraform devient un outil d'entreprise fiable lorsque la description de l'infrastructure s'inscrit dans un processus de changement contrôlé.

Une architecture mature doit combiner :

- des sources versionnées ;
- des modules et providers maîtrisés ;
- un state protégé ;
- des plans examinés ;
- des politiques testables ;
- des identités de moindre privilège ;
- des approbations adaptées au risque ;
- une détection des dérives ;
- des procédures de migration et de récupération ;
- une traçabilité de bout en bout.

Le parcours est maintenant cohérent :

**Débutant :** comprendre l'IaC, HCL, le plan, l'application et le state.

**Intermédiaire :** construire des infrastructures réseau, des modules, des tests et une CI.

**Expert :** gouverner le state et les releases, protéger les applications, contrôler les politiques, détecter les dérives et récupérer des erreurs de manière structurée.

La maîtrise de Terraform ne consiste pas uniquement à créer rapidement des ressources. Elle consiste à s'assurer que chaque changement est intentionnel, compréhensible, autorisé, vérifiable et récupérable.


## Références officielles

- Présentation de Terraform : https://developer.hashicorp.com/terraform/intro
- Langage Terraform : https://developer.hashicorp.com/terraform/language
- State : https://developer.hashicorp.com/terraform/language/state
- Verrouillage : https://developer.hashicorp.com/terraform/language/state/locking
- Backend S3 : https://developer.hashicorp.com/terraform/language/backend/s3
- Gestion des données sensibles : https://developer.hashicorp.com/terraform/language/manage-sensitive-data
- Contraintes de versions : https://developer.hashicorp.com/terraform/language/expressions/version-constraints
- Modules réutilisables : https://developer.hashicorp.com/terraform/language/modules/develop
- Meta-arguments : https://developer.hashicorp.com/terraform/language/meta-arguments
- Tests : https://developer.hashicorp.com/terraform/language/tests
- Tutoriels officiels : https://developer.hashicorp.com/terraform/tutorials
