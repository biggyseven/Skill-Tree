
# CI/CD et Git pour le réseau — Niveau expert

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** Git, validation YAML, tests Python, pipelines CI, gestion des branches et sécurité des secrets.  
> **Objectif :** concevoir une chaîne de changements réseau gouvernée, traçable, reproductible, observable et capable de gérer les échecs de déploiement.

---

## Sommaire

1. Architecture et responsabilités d'une chaîne CI/CD experte
2. Du dépôt de configuration à l'état attendu
3. GitOps et réconciliation de l'état réseau
4. Conception d'un pipeline multi-étapes
5. Validation approfondie et tests de bout en bout
6. Génération d'un artefact de release
7. Déploiement progressif et contrôle du périmètre
8. Précontrôles, post-contrôles et critères d'arrêt
9. Gestion des échecs partiels et retour arrière
10. Gouvernance, sécurité et traçabilité
11. Mesure de la fiabilité du processus
12. Architecture de référence
13. Atelier expert
14. Étude de défaillance
15. Évaluation corrigée

---

# 1. Architecture et responsabilités d'une chaîne CI/CD experte

## 1.1 Le changement réseau comme processus contrôlé

Au niveau débutant, Git permet de conserver l'historique. Au niveau intermédiaire, les validateurs et les tests détectent une partie des erreurs avant la fusion.

Au niveau expert, la question centrale devient :

**Comment garantir que chaque changement autorisé est associé à un état initial connu, à des contrôles vérifiables, à une autorisation explicite et à une stratégie de récupération adaptée ?**

Une chaîne avancée doit distinguer plusieurs activités :

- la définition du changement ;
- la validation des données et des règles ;
- la construction de l'artefact de déploiement ;
- l'approbation de la release ;
- l'application sur les équipements ;
- la vérification de l'état obtenu ;
- la clôture ou la gestion de l'échec.

Ces activités ne doivent pas être confondues dans un script unique qui modifie les équipements sans contrôle intermédiaire.

## 1.2 Objectifs experts

À la fin de ce cours, vous serez capable de :

1. définir une architecture de pipeline avec des responsabilités séparées ;
2. distinguer état attendu, état observé et artefact de déploiement ;
3. expliquer l'intérêt et les limites de GitOps ;
4. construire un manifeste de release traçable ;
5. organiser des tests unitaires, d'intégration et opérationnels ;
6. concevoir un déploiement progressif par lots ;
7. définir des critères d'arrêt mesurables ;
8. gérer les échecs partiels sans poursuivre aveuglément le déploiement ;
9. traiter le retour arrière comme une opération contrôlée ;
10. appliquer des règles de sécurité et de séparation des responsabilités ;
11. mesurer la qualité et la fiabilité de la chaîne de changement.

---

# 2. Du dépôt de configuration à l'état attendu

## 2.1 Trois états distincts

Dans une architecture d'automatisation, il faut distinguer trois éléments.

**L'état attendu** représente ce que le réseau devrait respecter selon les modèles, les données et les règles approuvées.

**L'état observé** représente ce que les équipements exposent réellement au moment d'un contrôle.

**L'artefact de release** représente le résultat précis construit et approuvé pour une livraison donnée : données rendues, changements candidats, rapports, références de versions et métadonnées.

Ces éléments peuvent diverger.

Par exemple, l'inventaire peut déclarer qu'un équipement appartient au site A alors que l'adresse interrogée correspond à une autre plateforme. Le déploiement doit être interrompu si l'identité de l'équipement ou son état initial ne correspond pas aux préconditions.

Une chaîne experte ne suppose donc pas que le contenu de Git décrit parfaitement le réseau réel. Elle vérifie explicitement les écarts qui comptent.

## 2.2 Structure avancée du dépôt

```text
network-platform/
├── .github/
│   └── workflows/
│       ├── pull-request.yml
│       ├── release.yml
│       └── deploy.yml
├── inventory/
│   ├── lab.yml
│   ├── staging.yml
│   └── production.yml
├── schemas/
│   ├── inventory.schema.json
│   └── release.schema.json
├── intended-state/
│   ├── vlans.yml
│   ├── routing.yml
│   └── access-policy.yml
├── templates/
│   ├── vendor-a/
│   └── vendor-b/
├── src/
│   ├── validate.py
│   ├── render.py
│   ├── precheck.py
│   └── postcheck.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── acceptance/
├── releases/
│   └── README.md
├── docs/
│   ├── change-management.md
│   ├── rollback.md
│   └── runbooks/
├── requirements.txt
└── README.md
```

Cette structure est un exemple d'organisation, pas une obligation universelle. Une équipe peut préférer plusieurs dépôts ou un monorepo selon les responsabilités, les plateformes et les contraintes de sécurité.

Le choix doit préserver la possibilité d'identifier la source d'un changement, ses dépendances, son artefact et son approbation.

## 2.3 Séparation des responsabilités

| Composant | Responsabilité |
|---|---|
| Dépôt Git | Historique, diff et collaboration |
| Validateur | Conformité aux règles des données |
| Générateur | Produit les fichiers candidats à partir des sources approuvées |
| Tests | Vérifient des propriétés définies |
| Gestionnaire de release | Associe les résultats à une version déterminée |
| Orchestrateur de déploiement | Contrôle l'ordre, le périmètre et les préconditions |
| Vérificateur opérationnel | Compare l'état observé à des critères attendus |
| Gouvernance | Définit qui peut approuver et dans quelles conditions |

Une personne ou un outil peut remplir plusieurs fonctions dans un petit environnement, mais les responsabilités doivent rester compréhensibles. Pour une opération à haut risque, les capacités d'approbation et de déploiement doivent être séparées conformément aux règles de l'organisation.

---

# 3. GitOps et réconciliation de l'état réseau

## 3.1 Le principe

GitOps est une approche dans laquelle un dépôt versionné sert de source de vérité déclarative pour l'état souhaité d'un système, tandis qu'un mécanisme automatisé applique ou réconcilie cet état selon des règles définies.

Dans un réseau, un modèle GitOps peut comparer l'état attendu aux propriétés observées, détecter les écarts et éventuellement proposer ou appliquer une correction autorisée.

GitOps n'est pas synonyme de déploiement automatique sans contrôle. Un système peut détecter et signaler les écarts sans corriger automatiquement les équipements.

## 3.2 Détection d'un écart

Supposons que le dépôt exige :

```yaml
interfaces:
  - name: GigabitEthernet1/0/10
    description: IOT-LAB
    access_vlan: 30
    admin_state: up
```

Une collecte d'état pourrait observer que le port utilise le VLAN 20 au lieu du VLAN 30.

Le système doit alors déterminer :

1. si la collecte identifie correctement l'équipement ;
2. si l'écart est réel ou dû à des données périmées ;
3. si le port est soumis à une exception approuvée ;
4. si le changement candidat est sûr ;
5. si l'action corrective entre dans le périmètre autorisé.

Une différence textuelle n'indique pas automatiquement qu'une correction doit être appliquée. L'état réel peut contenir des éléments dynamiques, des paramètres gérés par un autre contrôleur ou des exceptions opérationnelles légitimes.

## 3.3 Modes de réconciliation

| Mode | Comportement | Usage |
|---|---|---|
| Observation | Collecte l'état et signale les écarts | Découverte et audit |
| Évaluation | Compare l'état et génère une proposition | Revue de changement |
| Simulation | Évalue les effets prévus sans appliquer de modification | Analyse de risque |
| Application contrôlée | Applique un changement approuvé | Déploiement opérationnel |
| Réconciliation continue | Réévalue régulièrement et corrige selon une politique autorisée | Environnements adaptés et bien maîtrisés |

La réconciliation continue nécessite des garde-fous supplémentaires. Une boucle de correction qui répète une action non sûre peut amplifier une erreur, annuler une intervention manuelle légitime ou provoquer une instabilité.

## 3.4 Schéma GitOps

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="expert-gitops-title expert-gitops-desc">
  <title id="expert-gitops-title">Architecture GitOps pour le réseau</title>
  <desc id="expert-gitops-desc">Le dépôt versionné décrit l'état attendu. Un pipeline valide et publie un artefact. Un contrôleur compare l'état observé à l'état attendu et remonte les écarts. Seule une action approuvée peut conduire au déploiement. Les flux utilisent une animation de tirets, sans objet mobile.</desc>
  <defs>
    <marker id="expert-gitops-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .eg-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .eg-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .eg-net{fill:#123126;stroke:#4ade80;stroke-width:2}
      .eg-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .eg-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .eg-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#expert-gitops-arrow);animation:eg-dash 1.8s linear infinite}
      .eg-return{fill:none;stroke:#c4b5fd;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#expert-gitops-arrow);animation:eg-dash 1.8s linear infinite}
      @keyframes eg-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">ÉTAT ATTENDU, ÉTAT OBSERVÉ ET ACTION CONTRÔLÉE</text>
  <rect class="eg-box" x="25" y="75" width="205" height="78" rx="10"/>
  <text class="eg-title" x="127" y="104" text-anchor="middle">Dépôt Git</text>
  <text class="eg-text" x="127" y="127" text-anchor="middle">État attendu versionné</text>
  <rect class="eg-box" x="280" y="75" width="205" height="78" rx="10"/>
  <text class="eg-title" x="382" y="104" text-anchor="middle">CI + rendu</text>
  <text class="eg-text" x="382" y="127" text-anchor="middle">Tests et artefact</text>
  <rect class="eg-gate" x="535" y="75" width="205" height="78" rx="10"/>
  <text class="eg-title" x="637" y="104" text-anchor="middle">Approbation</text>
  <text class="eg-text" x="637" y="127" text-anchor="middle">Autorisation explicite</text>
  <rect class="eg-net" x="790" y="75" width="185" height="78" rx="10"/>
  <text class="eg-title" x="882" y="104" text-anchor="middle">Réseau</text>
  <text class="eg-text" x="882" y="127" text-anchor="middle">État opérationnel</text>
  <path class="eg-flow" d="M230 114 H273"/>
  <path class="eg-flow" d="M485 114 H528"/>
  <path class="eg-flow" d="M740 114 H783"/>
  <rect class="eg-box" x="285" y="242" width="430" height="75" rx="10"/>
  <text class="eg-title" x="500" y="271" text-anchor="middle">Contrôleur de conformité</text>
  <text class="eg-text" x="500" y="294" text-anchor="middle">Compare l'état attendu et l'état observé</text>
  <path class="eg-return" d="M882 153 V205 H715 V250"/>
  <path class="eg-return" d="M285 279 H127 V190 H127 V160"/>
  <text class="eg-text" x="500" y="350" text-anchor="middle">Écart détecté ≠ correction automatique obligatoire.</text>
  <text class="eg-text" x="500" y="369" text-anchor="middle">Évaluer l'identité, le contexte, les exceptions et l'autorisation avant toute action.</text>
</svg>

---

# 4. Conception d'un pipeline multi-étapes

## 4.1 Principes d'architecture

Une chaîne experte doit pouvoir distinguer clairement les résultats de chaque étape :

- validation des données ;
- génération de configuration ;
- tests et simulation ;
- construction de l'artefact ;
- revue et approbation ;
- précontrôles ;
- déploiement limité ;
- post-contrôles ;
- clôture ou gestion de l'échec.

Le pipeline doit aussi rendre explicites les dépendances entre ces étapes. Le déploiement doit être impossible si une validation obligatoire a échoué ou si l'artefact ne correspond pas à celui qui a été approuvé.

## 4.2 Exemple de workflow CI et tests

Le fichier suivant représente une partie de la chaîne. Il valide les données, exécute les tests et produit un rapport. Il ne déploie pas sur le réseau.

Créez `.github/workflows/pull-request.yml` :

```yaml
name: Network CI

on:
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout source
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Validate inventory
        run: |
          python src/validate.py

      - name: Run unit tests
        run: |
          python -m unittest discover -s tests/unit -v

      - name: Run static policy checks
        run: |
          python src/policy_check.py

      - name: Record build metadata
        if: always()
        run: |
          mkdir -p reports
          {
            echo "commit=$GITHUB_SHA"
            echo "run_id=$GITHUB_RUN_ID"
            echo "workflow=$GITHUB_WORKFLOW"
            echo "event=$GITHUB_EVENT_NAME"
          } > reports/build-metadata.txt

      - name: Upload metadata
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: build-metadata
          path: reports/build-metadata.txt
          if-no-files-found: error
          retention-days: 14
```

Ce fichier est un modèle d'architecture. Les scripts `src/validate.py` et `src/policy_check.py` doivent exister, être testés et être documentés avant que le workflow soit activé.

La référence de version des actions doit être maintenue selon les règles de sécurité de l'organisation. Dans un environnement exigeant, l'équipe peut préférer des références immuables par SHA de commit, en documentant la provenance de chaque action.

## 4.3 Pourquoi séparer CI et déploiement ?

La CI traite les changements proposés et établit des résultats de validation. Le processus de déploiement doit appliquer des règles d'accès et d'approbation plus strictes.

Cette séparation réduit le risque qu'un code soumis dans une pull request dispose de secrets ou de permissions opérationnelles.

Un workflow de déploiement ne doit pas simplement répéter la CI puis lancer une commande privilégiée. Il doit vérifier que l'artefact, le commit et l'approbation correspondent bien à la release autorisée.

## 4.4 Contrôles de promotion entre environnements

Une stratégie de promotion peut suivre cette séquence :

1. valider le changement ;
2. créer un artefact identifié ;
3. tester cet artefact en laboratoire ;
4. vérifier que le même artefact est conservé pour l'étape suivante ;
5. soumettre la release à approbation ;
6. déployer sur un périmètre limité ;
7. vérifier les résultats avant de poursuivre.

La promotion d'un artefact consiste à autoriser son passage vers un autre environnement. Elle ne signifie pas nécessairement reconstruire la configuration à chaque étape.

Lorsque l'artefact doit être reconstruit pour un environnement donné, ses différences doivent être explicites et les résultats de validation doivent rester traçables.

---

# 5. Validation approfondie et tests de bout en bout

## 5.1 Les différentes couches de test

| Couche | Objet testé | Limite principale |
|---|---|---|
| Validation de données | Inventaire et paramètres | Ne prouve pas le comportement réseau |
| Tests unitaires | Fonctions et règles de validation | Ne couvre pas toute l'intégration |
| Analyse statique | Configurations et règles de sécurité | Dépend des règles implémentées |
| Tests de rendu | Configuration produite à partir d'un modèle | Ne prouve pas l'acceptation par le matériel |
| Tests d'intégration | Interaction entre composants ou services | Reproduit rarement tous les scénarios réels |
| Simulation ou laboratoire | Comportement dans une topologie contrôlée | Le laboratoire peut différer de la production |
| Tests d'acceptation | Résultat fonctionnel attendu | Nécessite des critères mesurables |
| Vérification opérationnelle | État réel après déploiement | Peut nécessiter une collecte spécifique au constructeur |

La qualité d'une chaîne repose sur la combinaison de ces couches et sur la compréhension de leurs limites.

## 5.2 Tests de propriétés plutôt que simple comparaison textuelle

Une configuration peut être présentée différemment sans changer son sens. À l'inverse, une modification d'une seule ligne peut avoir un impact fonctionnel important.

Il est donc utile de définir certaines propriétés attendues :

- les VLAN requis existent ;
- aucun VLAN interdit n'est affecté à un port sensible ;
- les interfaces critiques ne sont pas désactivées sans autorisation ;
- les réseaux de destination des routes sont cohérents ;
- les règles d'accès ne sont pas plus permissives que la politique ;
- les protocoles et paramètres de gestion correspondent aux standards de l'organisation.

Ces propriétés doivent être adaptées aux plateformes et aux architectures concernées. Un contrôle générique ne peut pas comprendre tous les comportements propres à chaque constructeur.

## 5.3 Validation des changements de routage

Un changement de routage nécessite des contrôles plus approfondis qu'une modification descriptive.

Selon le périmètre, ils peuvent examiner :

- les préfixes attendus ;
- les prochains sauts autorisés ;
- les distances ou préférences de route ;
- la présence des routes critiques ;
- les modifications de redistribution ;
- l'exposition de préfixes non autorisés ;
- les routes de secours ;
- la connectivité des services nécessaires.

Un diff qui ne comporte que quelques lignes peut modifier le chemin de trafic de nombreux utilisateurs.

## 5.4 Tests négatifs

Un bon jeu de tests doit aussi démontrer le rejet des changements interdits.

Exemples :

- un inventaire qui référence un équipement inconnu ;
- une interface critique désactivée sans exception ;
- un réseau non autorisé ajouté à une politique de routage ;
- un changement qui dépasse le périmètre d'une release ;
- une version de configuration construite avec un modèle non approuvé.

Les tests négatifs sont particulièrement importants pour les contrôles de sécurité. Un système qui accepte tous les changements ne valide rien.

---

# 6. Génération d'un artefact de release

## 6.1 Pourquoi un manifeste ?

Une release doit pouvoir être identifiée sans ambiguïté. Les équipes doivent savoir quels fichiers, outils, versions, rapports et paramètres ont contribué au changement.

Un manifeste de release peut documenter :

- l'identifiant de release ;
- le commit source ;
- les versions des outils ;
- les références des inventaires et modèles ;
- le périmètre d'équipements ;
- les résultats des validations ;
- les références des rapports ;
- l'approbation requise ;
- la politique de retour arrière.

Exemple de `release-manifest.example.yml` :

```yaml
release:
  id: "NET-CHANGE-2026-0042"
  source_commit: "REPLACE_WITH_REAL_COMMIT_SHA"
  created_at_utc: "REPLACE_WITH_BUILD_TIMESTAMP"

  scope:
    environment: lab
    devices:
      - SW-ACCESS-01

  inputs:
    inventory_path: inventory/lab.yml
    template_revision: "REPLACE_WITH_REAL_REVISION"

  validation:
    inventory: passed
    unit_tests: passed
    policy_checks: passed
    lab_tests: pending

  deployment:
    authorized: false
    approval_reference: null

  recovery:
    plan: docs/rollback.md
    status: not_executed
```

Les valeurs `REPLACE_WITH...` et les résultats d'exemple doivent être remplacés par des valeurs produites réellement. Le manifeste ci-dessus est un modèle illustratif, pas une preuve de test ni une autorisation de déploiement.

## 6.2 Construction reproductible

Pour pouvoir reconstruire ou vérifier une release, conservez les éléments nécessaires à son identification :

- commit exact ;
- version ou empreinte des modèles ;
- versions des dépendances ;
- paramètres non secrets ;
- version des scripts ;
- empreintes des artefacts générés ;
- rapports issus des tests.

L'objectif est de déterminer si un artefact consulté ultérieurement correspond bien à celui qui a été testé puis approuvé.

## 6.3 Intégrité de l'artefact

Un SHA-256 peut servir à calculer une empreinte d'un fichier :

```bash
sha256sum release-manifest.yml
```

Sous PowerShell :

```powershell
Get-FileHash release-manifest.yml -Algorithm SHA256
```

Une empreinte permet de détecter une différence de contenu. Elle ne prouve pas à elle seule qui a créé le fichier, que les tests étaient corrects ou que la release était autorisée.

Pour ces objectifs, il faut relier l'artefact à des sources de confiance, à des contrôles traçables et à une approbation vérifiable.

---

# 7. Déploiement progressif et contrôle du périmètre

## 7.1 Pourquoi déployer par étapes ?

Un changement sur un équipement pilote permet de détecter certaines erreurs avant d'étendre le changement à tout un parc.

Le déploiement progressif ne supprime pas le risque. Il limite le nombre d'équipements exposés à une erreur, à condition que les lots soient définis de façon pertinente et qu'une vérification permette de décider de la poursuite.

Une séquence possible :

1. équipement de laboratoire ;
2. équipement pilote non critique ;
3. petit lot de production ;
4. lot suivant après vérification ;
5. généralisation selon le plan approuvé.

Les environnements disponibles et le nombre de lots varient selon l'organisation.

## 7.2 Schéma de déploiement par lots

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400" viewBox="0 0 1000 400" role="img" aria-labelledby="expert-batch-title expert-batch-desc">
  <title id="expert-batch-title">Déploiement progressif par lots</title>
  <desc id="expert-batch-desc">Après l'approbation, le changement est appliqué au lot pilote et vérifié. Si les critères sont satisfaits, le lot suivant peut être autorisé. Si les critères échouent, la progression s'arrête et un plan de remédiation est déclenché. Les lignes animées montrent le flux sans boule mobile.</desc>
  <defs>
    <marker id="expert-batch-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .eb-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .eb-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .eb-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .eb-stop{fill:#3b201f;stroke:#fb7185;stroke-width:2}
      .eb-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .eb-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .eb-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#expert-batch-arrow);animation:eb-dash 1.8s linear infinite}
      .eb-fail{fill:none;stroke:#fb7185;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#expert-batch-arrow);animation:eb-dash 1.8s linear infinite}
      @keyframes eb-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="398" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">CHAQUE LOT DOIT PASSER UNE BARRIÈRE DE VÉRIFICATION</text>
  <rect class="eb-gate" x="25" y="78" width="175" height="75" rx="10"/>
  <text class="eb-title" x="112" y="105" text-anchor="middle">Approbation</text>
  <text class="eb-text" x="112" y="128" text-anchor="middle">Périmètre autorisé</text>
  <rect class="eb-box" x="250" y="78" width="175" height="75" rx="10"/>
  <text class="eb-title" x="337" y="105" text-anchor="middle">Lot pilote</text>
  <text class="eb-text" x="337" y="128" text-anchor="middle">Déployer et observer</text>
  <rect class="eb-gate" x="475" y="78" width="175" height="75" rx="10"/>
  <text class="eb-title" x="562" y="105" text-anchor="middle">Barrière qualité</text>
  <text class="eb-text" x="562" y="128" text-anchor="middle">Comparer aux critères</text>
  <rect class="eb-box" x="700" y="78" width="175" height="75" rx="10"/>
  <text class="eb-title" x="787" y="105" text-anchor="middle">Lot suivant</text>
  <text class="eb-text" x="787" y="128" text-anchor="middle">Extension autorisée</text>
  <path class="eb-flow" d="M200 115 H243"/>
  <path class="eb-flow" d="M425 115 H468"/>
  <path class="eb-flow" d="M650 115 H693"/>
  <rect class="eb-ok" x="700" y="220" width="175" height="70" rx="10"/>
  <text class="eb-title" x="787" y="247" text-anchor="middle">Clôture</text>
  <text class="eb-text" x="787" y="269" text-anchor="middle">Vérifications finales</text>
  <path class="eb-flow" d="M787 153 V212"/>
  <rect class="eb-stop" x="250" y="220" width="400" height="70" rx="10"/>
  <text class="eb-title" x="450" y="247" text-anchor="middle">Critère critique non satisfait</text>
  <text class="eb-text" x="450" y="269" text-anchor="middle">Stopper les lots, diagnostiquer et appliquer le plan prévu</text>
  <path class="eb-fail" d="M562 153 V195 H450 V212"/>
  <text class="eb-text" x="500" y="332" text-anchor="middle">Ne jamais poursuivre un lot suivant après un échec critique non résolu.</text>
  <text class="eb-text" x="500" y="352" text-anchor="middle">Le retour arrière peut lui-même être risqué et doit être soumis à des conditions explicites.</text>
</svg>

## 7.3 Définir un lot cohérent

Un lot doit être choisi selon l'architecture et le risque, pas uniquement selon un nombre fixe d'équipements.

On peut regrouper les équipements selon :

- le site ;
- la fonction réseau ;
- la criticité ;
- la dépendance à un service ;
- la fenêtre de changement ;
- la possibilité de vérifier le résultat de façon indépendante.

Évitez de placer dans un même lot tous les équipements dont l'échec simultané interromprait un service critique.

## 7.4 Autoriser le lot suivant

La décision de poursuivre doit dépendre de critères mesurables, par exemple :

- tous les équipements concernés ont-ils répondu aux contrôles attendus ?
- les services critiques sont-ils toujours accessibles ?
- les routes et interfaces attendues sont-elles présentes ?
- les erreurs ou alarmes nouvelles restent-elles sous les seuils autorisés ?
- les résultats ont-ils été associés au bon lot et au bon commit ?

Un message de réussite de la commande de déploiement ne remplace pas ces vérifications.

---

# 8. Précontrôles, post-contrôles et critères d'arrêt

## 8.1 Précontrôles

Les précontrôles doivent confirmer que les conditions prévues sont bien réunies.

Ils peuvent vérifier :

- l'identité du périphérique ;
- la version logicielle attendue ;
- la disponibilité de l'accès de gestion ;
- l'état des interfaces critiques ;
- la présence d'une sauvegarde ou d'un état de référence ;
- l'absence d'un changement concurrent ;
- le respect du créneau autorisé.

Si l'état initial diffère de la situation pour laquelle le changement a été approuvé, arrêtez le processus et réévaluez le changement.

## 8.2 Post-contrôles

Les post-contrôles doivent examiner les propriétés opérationnelles affectées.

Par exemple, après une modification de VLAN, les tests peuvent vérifier l'appartenance des ports, la connectivité attendue et la persistance des services existants.

Après une modification de routage, la validation doit examiner les routes et la connectivité des destinations critiques prévues.

Chaque test doit définir :

- les données d'entrée ;
- la source de vérité ;
- le résultat attendu ;
- le délai maximal ;
- le seuil d'échec ;
- la conduite à tenir si le contrôle ne peut pas être exécuté.

Un test qui n'a pas pu s'exécuter doit produire un résultat distinct d'un test qui a réussi.

## 8.3 Exemple de politique d'arrêt

```yaml
change_policy:
  stop_on:
    - unexpected_device_identity
    - precheck_failure
    - critical_connectivity_failure
    - unexpected_route_change
    - postcheck_timeout
    - unauthorized_scope_change

  require:
    - approved_release
    - approved_change_window
    - known_initial_state
    - tested_recovery_plan
```

Ce fichier illustre la forme d'une politique. Une implémentation doit définir chaque condition avec des règles précises, des données de confiance et des tests démontrant qu'elle déclenche bien l'arrêt attendu.

Les noms de conditions ne suffisent pas à garantir qu'un orchestrateur les applique correctement.

---

# 9. Gestion des échecs partiels et retour arrière

## 9.1 Tous les déploiements ne sont pas atomiques

Un changement de réseau peut être appliqué sur plusieurs équipements. Si trois équipements sur cinq ont été modifiés avant un échec, le réseau se trouve dans un état partiellement transformé.

Le pipeline doit savoir :

- quels équipements ont été traités ;
- quels changements ont réussi ;
- lesquels ont échoué ;
- quels post-contrôles ont été exécutés ;
- quels équipements sont dans un état incertain ;
- quelles actions sont autorisées ensuite.

Une erreur ne doit pas effacer l'historique des actions déjà effectuées.

## 9.2 Le retour arrière n'est pas une commande universelle

Le retour arrière dépend du changement, de la plateforme et de l'état réel de l'équipement.

Certaines modifications peuvent être annulées par une action inverse. D'autres nécessitent une restauration de configuration, un mécanisme constructeur spécifique ou une intervention manuelle.

Un retour arrière peut aussi être dangereux si d'autres changements ont été appliqués depuis. Il faut donc vérifier l'état et les dépendances avant de le lancer.

## 9.3 Exemple de registre d'exécution

Un orchestrateur peut conserver un journal structuré par équipement :

```yaml
execution:
  release_id: "NET-CHANGE-2026-0042"
  batch: "site-lab-a"

  devices:
    - name: SW-ACCESS-01
      precheck: passed
      deployment: succeeded
      postcheck: passed

    - name: SW-ACCESS-02
      precheck: passed
      deployment: succeeded
      postcheck: failed

    - name: SW-ACCESS-03
      precheck: not_started
      deployment: not_started
      postcheck: not_started

  decision:
    status: stopped
    reason: postcheck_failure
    next_action: investigate
```

Ces résultats sont fictifs. Un système de production doit produire le registre à partir d'événements réels, horodatés et associés au bon équipement.

La décision `stopped` doit déclencher le comportement correspondant dans l'orchestrateur. Un champ YAML seul ne stoppe rien.

## 9.4 Procédure de récupération

Une procédure de récupération doit préciser :

1. comment déterminer l'état réel de chaque équipement ;
2. comment arrêter la poursuite des lots ;
3. comment protéger l'accès d'administration ;
4. comment décider entre réparation et retour arrière ;
5. comment appliquer l'action approuvée ;
6. comment vérifier que les services sont rétablis ;
7. comment enregistrer les résultats et les actions manuelles ;
8. comment autoriser la reprise du processus.

Une récupération peut exiger une intervention humaine. L'objectif n'est pas de rendre chaque panne entièrement automatique, mais d'éviter les réactions non contrôlées et les décisions prises sans informations suffisantes.

---

# 10. Gouvernance, sécurité et traçabilité

## 10.1 Séparation des responsabilités

Pour un changement sensible, séparez clairement les fonctions suivantes :

| Fonction | Responsabilité |
|---|---|
| Auteur | Prépare le changement |
| Relecteur | Examine le diff et l'intention |
| CI | Exécute les contrôles automatiques |
| Approbateur | Autorise le passage à l'étape sensible |
| Orchestrateur | Exécute le changement dans le périmètre autorisé |
| Validateur opérationnel | Vérifie le résultat réel |
| Responsable d'incident | Coordonne la récupération en cas d'échec |

Une équipe réduite peut regrouper certaines fonctions. Les changements à haut risque doivent néanmoins respecter les règles de séparation des responsabilités de l'organisation.

## 10.2 Protéger les environnements de déploiement

Sur une plateforme qui le permet, un environnement `production` peut imposer des réviseurs requis, limiter les branches autorisées et contrôler l'accès aux secrets de l'environnement.

Ces protections doivent être configurées dans la plateforme et testées. Le simple fait d'ajouter une propriété `environment: production` dans un workflow ne signifie pas que toutes les approbations souhaitées sont déjà configurées.

Documentation GitHub :

https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments

https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments

## 10.3 Gestion des identités et des secrets

Pour les accès de déploiement :

- privilégiez une identité dédiée au pipeline ;
- limitez les permissions aux équipements et opérations nécessaires ;
- séparez les accès en lecture de ceux qui permettent de modifier ;
- évitez les identifiants personnels partagés ;
- utilisez les mécanismes de secrets approuvés ;
- faites tourner les identifiants selon la politique de sécurité ;
- auditez l'utilisation des accès privilégiés ;
- interdisez l'exposition des secrets dans les rapports et les journaux.

Lorsqu'une plateforme prend en charge une fédération d'identité ou des identifiants de courte durée, cette approche peut réduire le besoin de conserver des secrets persistants. La méthode exacte doit être adaptée au système d'automatisation utilisé.

## 10.4 Traçabilité de bout en bout

Pour un changement important, il doit être possible de relier :

- le ticket ou besoin métier ;
- la pull request ;
- le commit approuvé ;
- le résultat des contrôles ;
- la release et son manifeste ;
- l'identité de l'approbateur ;
- les équipements concernés ;
- les résultats avant et après changement ;
- les éventuelles actions de récupération.

La traçabilité permet d'expliquer ce qui s'est produit et facilite l'analyse après un incident.

---

# 11. Mesure de la fiabilité du processus

## 11.1 Indicateurs utiles

| Indicateur | Ce qu'il aide à mesurer |
|---|---|
| Taux de réussite des contrôles CI | Stabilité de la validation et qualité des changements proposés |
| Durée des pipelines | Temps de validation |
| Taux de changements échoués | Risque opérationnel observé |
| Nombre de retours arrière | Fréquence des changements nécessitant une récupération |
| Durée moyenne de récupération | Temps nécessaire pour rétablir un service |
| Écarts entre état attendu et observé | Conformité de l'infrastructure |
| Changements sans preuve de post-contrôle | Qualité de la clôture opérationnelle |
| Incidents liés à une release | Impact réel du processus de changement |

Les indicateurs doivent être interprétés avec prudence. Un nombre de changements échoués faible peut indiquer une bonne qualité, mais peut aussi refléter un système qui effectue trop peu de contrôles ou ne détecte pas ses incidents.

## 11.2 Exemple de tableau de suivi

```text
Release                  Résultat   Échec post-check   Récupération
NET-CHANGE-2026-0040      Succès     Non                Non
NET-CHANGE-2026-0041      Échec      Oui                Oui
NET-CHANGE-2026-0042      Arrêt      Oui                En cours
```

Ces données sont fictives et illustrent un format. Dans un système réel, les valeurs doivent provenir du registre opérationnel.

## 11.3 Amélioration continue

Après chaque incident ou changement ayant rencontré une difficulté :

1. identifier le point exact de détection ou d'échec ;
2. déterminer si le contrôle était absent, incorrect ou mal interprété ;
3. vérifier si une donnée, une permission ou une procédure manquait ;
4. ajouter un test reproductible lorsqu'il est possible de le faire ;
5. mettre à jour la documentation et le plan de récupération ;
6. suivre si la même cause réapparaît.

L'objectif est de réduire la récurrence des défaillances et d'améliorer la confiance dans les changements futurs.

---

# 12. Architecture de référence

## 12.1 Vue d'ensemble

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430" role="img" aria-labelledby="expert-arch-title expert-arch-desc">
  <title id="expert-arch-title">Architecture de référence CI/CD réseau expert</title>
  <desc id="expert-arch-desc">Les sources versionnées passent par validation, tests, génération de release et approbation. L'orchestrateur applique le changement par lots. Les collectes de l'état opérationnel alimentent les post-contrôles et l'observabilité. Les flux sont représentés par des lignes directionnelles en tirets.</desc>
  <defs>
    <marker id="expert-arch-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .ea-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .ea-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .ea-net{fill:#123126;stroke:#4ade80;stroke-width:2}
      .ea-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .ea-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .ea-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#expert-arch-arrow);animation:ea-dash 1.8s linear infinite}
      .ea-return{fill:none;stroke:#c4b5fd;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#expert-arch-arrow);animation:ea-dash 1.8s linear infinite}
      @keyframes ea-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="428" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DE LA SOURCE DE VÉRITÉ À L'ÉTAT OPÉRATIONNEL</text>
  <rect class="ea-box" x="25" y="70" width="190" height="76" rx="10"/>
  <text class="ea-title" x="120" y="99" text-anchor="middle">Git + sources</text>
  <text class="ea-text" x="120" y="122" text-anchor="middle">Inventaire, règles, modèles</text>
  <rect class="ea-box" x="260" y="70" width="190" height="76" rx="10"/>
  <text class="ea-title" x="355" y="99" text-anchor="middle">CI + tests</text>
  <text class="ea-text" x="355" y="122" text-anchor="middle">Validation reproductible</text>
  <rect class="ea-box" x="495" y="70" width="190" height="76" rx="10"/>
  <text class="ea-title" x="590" y="99" text-anchor="middle">Release immuable</text>
  <text class="ea-text" x="590" y="122" text-anchor="middle">Artefact + manifeste</text>
  <rect class="ea-gate" x="730" y="70" width="245" height="76" rx="10"/>
  <text class="ea-title" x="852" y="99" text-anchor="middle">Approbation + précontrôles</text>
  <text class="ea-text" x="852" y="122" text-anchor="middle">Vérification du contexte</text>
  <path class="ea-flow" d="M215 108 H253"/>
  <path class="ea-flow" d="M450 108 H488"/>
  <path class="ea-flow" d="M685 108 H723"/>
  <rect class="ea-net" x="640" y="230" width="245" height="76" rx="10"/>
  <text class="ea-title" x="762" y="259" text-anchor="middle">Orchestrateur de lots</text>
  <text class="ea-text" x="762" y="282" text-anchor="middle">Ordre et limites autorisés</text>
  <rect class="ea-net" x="310" y="230" width="245" height="76" rx="10"/>
  <text class="ea-title" x="432" y="259" text-anchor="middle">Équipements réseau</text>
  <text class="ea-text" x="432" y="282" text-anchor="middle">Changement opérationnel</text>
  <rect class="ea-box" x="35" y="340" width="285" height="62" rx="10"/>
  <text class="ea-title" x="177" y="365" text-anchor="middle">État observé + post-contrôles</text>
  <text class="ea-text" x="177" y="385" text-anchor="middle">Résultat réel et critères d'acceptation</text>
  <rect class="ea-box" x="640" y="340" width="300" height="62" rx="10"/>
  <text class="ea-title" x="790" y="365" text-anchor="middle">Journal d'audit + indicateurs</text>
  <text class="ea-text" x="790" y="385" text-anchor="middle">Release, résultats, décisions, incidents</text>
  <path class="ea-flow" d="M852 146 V190 H762 V223"/>
  <path class="ea-flow" d="M640 268 H562"/>
  <path class="ea-return" d="M432 306 V330 H320 V371"/>
  <path class="ea-flow" d="M320 371 H632"/>
  <text class="ea-text" x="500" y="418" text-anchor="middle">Les données de contrôle alimentent la décision de clôture ou de récupération.</text>
</svg>

## 12.2 Principes incontournables

Une architecture experte doit préserver les propriétés suivantes :

**Traçabilité :** chaque changement peut être relié à sa source et à sa release.

**Reproductibilité :** les données, modèles, dépendances et contrôles sont identifiables.

**Moindre privilège :** chaque étape ne reçoit que les capacités dont elle a besoin.

**Cohérence :** un déploiement ne poursuit pas son parcours si les préconditions critiques ne sont plus vraies.

**Observabilité :** les actions et leurs résultats peuvent être consultés et corrélés.

**Récupération maîtrisée :** l'échec déclenche une stratégie prévue et vérifiable plutôt qu'une réaction improvisée.

---

# 13. Atelier expert

## Scénario

Une équipe doit modifier un paramètre de routage sur trois routeurs. Le changement doit d'abord être testé en laboratoire, puis appliqué à un lot pilote. Le déploiement général n'est autorisé qu'après des post-contrôles concluants.

Vous devez concevoir le flux du changement, sans exécuter de commandes de configuration sur des équipements de production.

## Étape A — Définir le changement

Créez une branche :

```bash
git switch -c feature/routing-policy-update
```

Documentez :

- le besoin ;
- les préfixes ou routes concernés ;
- les équipements visés ;
- l'état attendu ;
- les dépendances ;
- les risques ;
- le plan de récupération.

## Étape B — Ajouter les règles de validation

Les tests doivent détecter au minimum :

- un équipement non autorisé ;
- une route attendue absente ;
- une route interdite ;
- une modification hors périmètre ;
- un inventaire incohérent.

Ajoutez les règles et des tests négatifs reproduisant ces situations.

## Étape C — Construire et identifier la release

Le pipeline doit enregistrer :

- le commit source ;
- l'identifiant de release ;
- les versions des outils ;
- les résultats des tests ;
- le périmètre autorisé ;
- l'empreinte de l'artefact ;
- les références des rapports.

La release doit rester associée à cet ensemble de données.

## Étape D — Préparer le lot pilote

Définissez les préconditions, les contrôles attendus et les critères d'arrêt.

Le pipeline de production ne doit pas pouvoir passer directement du succès des tests à une commande privilégiée. Il doit vérifier l'approbation, l'identité du lot, la release et l'état initial.

## Étape E — Définir le comportement en cas d'échec

Supposons que le premier routeur soit modifié, mais qu'un post-contrôle échoue.

Le processus doit :

1. interrompre l'extension du déploiement ;
2. enregistrer les actions déjà effectuées ;
3. collecter l'état actuel des équipements concernés ;
4. évaluer les effets de l'écart ;
5. appliquer une stratégie de récupération autorisée ;
6. revérifier les critères de service ;
7. documenter les résultats et obtenir l'autorisation nécessaire avant une reprise.

Un simple statut rouge ne suffit pas. L'orchestrateur doit être conçu pour interrompre effectivement les actions qui ne sont plus autorisées.

## Étape F — Clôturer la release

La clôture doit enregistrer le résultat réel, les équipements traités, les écarts détectés, les éventuelles récupérations et les validations de fin.

Ne marquez pas la release comme réussie si certains post-contrôles obligatoires n'ont pas été exécutés ou si leur résultat est inconnu.

---

# 14. Étude de défaillance

## Situation

Un changement de politique de routage est validé par les tests statiques. Le premier lot est appliqué. Un service distant devient inaccessible. Le pipeline continue pourtant de lancer les changements suivants.

## 14.1 Analyse de la défaillance

Plusieurs causes sont possibles :

- les tests ne couvraient pas la connectivité concernée ;
- la modification était correcte syntaxiquement mais incorrecte fonctionnellement ;
- le post-contrôle n'était pas défini ;
- l'échec a été enregistré sans bloquer l'orchestrateur ;
- l'état initial n'avait pas été vérifié ;
- les lots étaient trop larges ou mal organisés ;
- le système de surveillance ne permettait pas d'identifier rapidement l'impact.

Il ne faut pas conclure automatiquement qu'un seul composant est responsable. L'incident peut résulter de plusieurs faiblesses combinées.

## 14.2 Mesures correctives

1. Réexaminer le périmètre et arrêter l'extension.
2. Collecter l'état réel des équipements concernés.
3. Identifier le changement appliqué et le service affecté.
4. Déterminer si la réparation ou le retour arrière est la meilleure option.
5. Appliquer la procédure autorisée.
6. Vérifier le rétablissement du service.
7. Reproduire le scénario en laboratoire.
8. Ajouter un test qui aurait détecté le défaut avant la généralisation.
9. Vérifier que l'orchestrateur arrête effectivement les lots lors d'un post-contrôle critique.
10. Documenter la cause, les preuves, les décisions et les améliorations.

## 14.3 Leçon principale

Une chaîne avancée ne doit pas simplement exécuter une suite de commandes. Elle doit gérer des états, contrôler les conditions de passage, enregistrer les résultats et interrompre les actions lorsque les hypothèses deviennent invalides.

---

# 15. Évaluation corrigée

## Questions

1. Quelle différence existe entre l'état attendu et l'état observé ?
2. GitOps signifie-t-il que chaque écart doit être corrigé automatiquement ?
3. Pourquoi faut-il identifier précisément l'artefact de release ?
4. Pourquoi une release testée doit-elle rester associée à son artefact ?
5. Que permet un déploiement progressif ?
6. Pourquoi les précontrôles sont-ils indispensables ?
7. Quelle différence existe entre un post-contrôle qui échoue et un post-contrôle qui n'a pas pu s'exécuter ?
8. Pourquoi une application partielle complique-t-elle le retour arrière ?
9. Pourquoi le succès d'une commande de configuration ne garantit-il pas le succès fonctionnel ?
10. Quel est le rôle de la séparation des responsabilités ?
11. Pourquoi une empreinte cryptographique ne prouve-t-elle pas à elle seule l'approbation d'une release ?
12. Que doit faire l'orchestrateur lorsqu'un critère d'arrêt critique est déclenché ?

## Corrigé

**1. État attendu et observé**

L'état attendu décrit ce que les modèles et politiques exigent. L'état observé est ce que les équipements exposent réellement à un instant donné.

**2. GitOps et correction automatique**

Non. GitOps peut servir à observer, comparer, signaler, simuler ou appliquer un changement contrôlé. La correction automatique dépend de la politique et des protections définies.

**3. Identité de la release**

Pour établir la correspondance entre les sources, les tests, l'approbation et les actions opérationnelles.

**4. Association avec l'artefact**

Pour éviter qu'un fichier différent de celui qui a été testé ou approuvé soit déployé.

**5. Déploiement progressif**

Pour limiter le périmètre exposé à un défaut et évaluer le résultat sur un lot avant d'étendre le changement.

**6. Précontrôles**

Ils vérifient que l'équipement, son état, le périmètre et les conditions sont conformes aux hypothèses du changement.

**7. Échec ou impossibilité de tester**

Un échec signifie que le contrôle a été exécuté et que son critère n'est pas satisfait. Un contrôle non exécuté ne fournit pas de preuve permettant de conclure à la réussite.

**8. Déploiement partiel**

Les équipements peuvent se trouver dans des états différents. Une procédure de récupération doit tenir compte de ce qui a réellement été appliqué.

**9. Succès d'une commande**

La commande peut être acceptée alors que le service attendu reste indisponible, que la route est incorrecte ou qu'un autre élément du réseau empêche le résultat fonctionnel.

**10. Séparation des responsabilités**

Elle limite les risques liés aux erreurs, aux privilèges excessifs et aux décisions non contrôlées, particulièrement pour les changements sensibles.

**11. Empreinte cryptographique**

Elle permet de vérifier l'intégrité du contenu comparé à une empreinte de référence, mais n'établit pas l'identité de l'auteur, la validité des tests ni l'autorisation de déployer.

**12. Critère d'arrêt**

L'orchestrateur doit bloquer les actions dépendantes, enregistrer l'état de l'exécution et diriger le processus vers la stratégie de diagnostic ou de récupération prévue.

---

# Conclusion — Le niveau expert

Une chaîne CI/CD réseau avancée ne se définit pas par le nombre d'outils ou par la quantité d'étapes dans un fichier YAML.

Elle se définit par sa capacité à :

- rendre les changements traçables ;
- produire des artefacts identifiables ;
- tester les propriétés pertinentes ;
- limiter les permissions ;
- vérifier l'état réel ;
- contrôler les autorisations ;
- interrompre une progression dangereuse ;
- récupérer d'un échec sans perdre l'historique ;
- améliorer ses contrôles à partir des incidents.

Le parcours est désormais cohérent :

**Débutant :** comprendre Git, les branches, le diff et les pipelines élémentaires.

**Intermédiaire :** valider les données, écrire des tests, produire des rapports et structurer la CI.

**Expert :** gouverner les releases, contrôler les déploiements progressifs, comparer l'état attendu à l'état réel et gérer les échecs opérationnels.

La maturité CI/CD ne consiste pas à supprimer toute intervention humaine. Elle consiste à automatiser ce qui peut être vérifié de façon fiable et à encadrer explicitement les décisions qui engagent la stabilité du réseau.

---

## Références officielles

- Git : https://git-scm.com/doc
- GitHub Actions : https://docs.github.com/actions
- Sécurité des workflows : https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- Environnements de déploiement : https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments
- Approbation des déploiements : https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments
- Action Checkout : https://github.com/actions/checkout
- Action Setup Python : https://github.com/actions/setup-python
- Documentation Python : https://docs.python.org/3/

**Fichier :** `cicd-network-expert.md`  
**Niveau :** Expert  
**Fin du cours**
