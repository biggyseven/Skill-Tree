
# CI/CD et Git pour le réseau — Niveau débutant

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Niveau actuel :** Débutant  
> **Objectif :** apprendre à versionner, contrôler et préparer les changements réseau de manière reproductible et sécurisée.

---

## Sommaire

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Pourquoi utiliser Git dans un réseau ?](#2-pourquoi-utiliser-git-dans-un-réseau-)
3. [Les notions essentielles](#3-les-notions-essentielles)
4. [Créer son premier dépôt réseau](#4-créer-son-premier-dépôt-réseau)
5. [Comprendre le cycle Git](#5-comprendre-le-cycle-git)
6. [Branches et revue des changements](#6-branches-et-revue-des-changements)
7. [Comprendre la CI/CD réseau](#7-comprendre-la-cicd-réseau)
8. [Créer son premier pipeline de validation](#8-créer-son-premier-pipeline-de-validation)
9. [Sécurité et protection des équipements](#9-sécurité-et-protection-des-équipements)
10. [Tests et retour arrière](#10-tests-et-retour-arrière)
11. [Atelier pratique complet](#11-atelier-pratique-complet)
12. [Dépannage](#12-dépannage)
13. [Évaluation et corrigé](#13-évaluation-et-corrigé)
14. [Synthèse et préparation du niveau intermédiaire](#14-synthèse-et-préparation-du-niveau-intermédiaire)

---

# 1. Contexte et objectifs

## 1.1 Contexte professionnel

Dans un réseau d'entreprise, les administrateurs configurent des commutateurs, des routeurs, des pare-feu et d'autres équipements. Les changements concernent, par exemple, les VLAN, les interfaces, les routes, les listes de contrôle d'accès (ACL), le routage dynamique et les paramètres de sécurité.

Une modification effectuée directement sur un équipement peut fonctionner, mais elle peut aussi interrompre un service ou créer une incohérence entre plusieurs appareils.

Sans méthode de suivi, il devient difficile de répondre à des questions fondamentales :

- Qui a effectué la modification ?
- Pourquoi cette modification était-elle nécessaire ?
- Quelles lignes ont été modifiées ?
- Qui a vérifié le changement ?
- Comment retrouver la version précédente ?
- Comment vérifier que le résultat attendu a réellement été obtenu ?

**Git et la CI/CD permettent de structurer ce processus.**

Git conserve l'historique des fichiers. La CI/CD automatise des contrôles et organise les étapes de préparation, de validation et de livraison d'un changement.

Dans ce cours, les premiers exercices sont réalisés sur des fichiers. Aucun pipeline présenté ici ne doit modifier automatiquement un réseau de production.

## 1.2 Prérequis

Vous devez connaître les notions de base suivantes :

- routeur et commutateur ;
- adresse IP et sous-réseau ;
- VLAN et interface réseau ;
- terminal et système de fichiers.

Aucune expérience préalable de Git ou de CI/CD n'est nécessaire.

## 1.3 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

1. expliquer l'utilité de Git pour l'administration réseau ;
2. créer un dépôt et enregistrer des versions de fichiers ;
3. examiner un diff avant de valider une modification ;
4. créer une branche de travail ;
5. expliquer le principe d'une pull request ou merge request ;
6. distinguer intégration continue, livraison continue et déploiement continu ;
7. comprendre les étapes d'un pipeline CI/CD réseau ;
8. réaliser quelques contrôles automatiques sans contacter les équipements ;
9. identifier les risques liés aux secrets et aux déploiements automatiques ;
10. préparer une méthode de changement comprenant des vérifications et un retour arrière.

---

# 2. Pourquoi utiliser Git dans un réseau ?

## 2.1 Le problème des modifications manuelles

Imaginez que trois administrateurs modifient successivement la configuration d'un même commutateur. L'un ajoute un VLAN, le deuxième change un port d'accès et le troisième corrige une description.

Si aucun historique commun n'est conservé, il devient compliqué de savoir quelle version fait référence, pourquoi une ligne a été supprimée ou à quel moment un incident a commencé.

Le même problème existe lorsqu'une configuration est copiée dans plusieurs fichiers portant des noms comme :

```text
switch-final.cfg
switch-final-v2.cfg
switch-final-corrige.cfg
switch-final-vraiment-final.cfg
```

Ces fichiers ne constituent pas un historique fiable.

## 2.2 Ce que Git apporte

Git est un système de gestion de versions. Il conserve l'évolution des fichiers au moyen de commits, permet de comparer des versions et facilite le travail sur des branches distinctes.

Dans un projet réseau, Git peut suivre :

- les configurations de référence ;
- les inventaires d'équipements ;
- les modèles de configuration ;
- les scripts d'automatisation ;
- les tests ;
- les procédures et la documentation.

Git ne configure pas lui-même les équipements. Il fournit une base de traçabilité pour les fichiers utilisés par les équipes et les outils d'automatisation.

## 2.3 Avant et après l'adoption de Git

| Sans gestion de versions | Avec Git et une méthode de changement |
|---|---|
| Copies multiples de fichiers | Historique organisé |
| Changements difficiles à comparer | Diff explicite |
| Modifications souvent isolées | Travail partagé sur des branches |
| Contrôles manuels uniquement | Possibilité d'automatiser des validations |
| Retour arrière improvisé | Version de référence identifiable |
| Décisions parfois non documentées | Commits, revues et procédures traçables |

**Attention :** Git améliore la traçabilité, mais ne remplace ni une sauvegarde opérationnelle ni une procédure de retour arrière testée.

---

# 3. Les notions essentielles

| Terme | Signification | Exemple réseau |
|---|---|---|
| Dépôt (*repository*) | Espace de fichiers suivi par Git | `reseau-automation/` |
| Commit | Enregistrement d'un ensemble de changements | Ajout d'un VLAN |
| Branche (*branch*) | Ligne de travail distincte | `feature/ajout-vlan-30` |
| Diff | Comparaison entre deux versions | Une ligne de VLAN ajoutée |
| Index (*staging area*) | Zone des changements préparés pour le prochain commit | Fichier ajouté avec `git add` |
| Dépôt distant | Dépôt partagé sur un serveur ou une plateforme | Dépôt Git de l'équipe |
| Pull request | Proposition de fusion et de revue sur certaines plateformes | Demande de validation d'un changement |
| CI | Intégration continue | Contrôles automatiques des fichiers |
| CD | Livraison continue ou déploiement continu selon le contexte | Préparation ou application contrôlée d'un changement |
| Pipeline | Suite d'étapes exécutées dans un ordre défini | Contrôles, tests, approbation |
| Artefact | Résultat produit par le pipeline | Rapport de validation |
| Rollback | Retour à un état connu et stable | Restauration selon une procédure approuvée |

## 3.1 Les trois distinctions à retenir

**Git n'est pas la CI/CD.** Git conserve l'historique des fichiers. La CI/CD orchestre les vérifications et les étapes de livraison.

**Un commit n'est pas une autorisation de déployer.** Un changement peut être enregistré tout en étant incorrect, non testé ou non approuvé.

**Un pipeline vert n'est pas une garantie absolue.** Il signifie que les contrôles configurés ont réussi. Il ne prouve pas que toutes les situations possibles ont été vérifiées.

---

# 4. Créer son premier dépôt réseau

Nous allons créer un projet fictif appelé `reseau-automation`.

## 4.1 Vérifier que Git est disponible

Dans un terminal :

```bash
git --version
```

Si une version apparaît, Git est disponible. Dans le cas contraire, installez Git à partir du site officiel :

https://git-scm.com/downloads

Configurez ensuite l'identité utilisée dans les commits :

```bash
git config --global user.name "Administrateur Réseau"
git config --global user.email "admin@example.net"
```

Remplacez l'adresse d'exemple par celle prévue pour votre environnement de travail.

## 4.2 Initialiser le dépôt

```bash
mkdir reseau-automation
cd reseau-automation
git init
```

Git initialise un dépôt dans le dossier courant.

Créez maintenant une structure simple :

```text
reseau-automation/
├── .gitignore
├── configs/
│   └── sw-access-01.cfg
├── inventory/
│   └── devices.example.yml
├── docs/
│   └── workflow.md
└── tests/
    └── README.md
```

Sur un terminal Bash, vous pouvez créer les dossiers avec :

```bash
mkdir -p configs inventory docs tests
```

Sous Windows PowerShell, vous pouvez utiliser :

```powershell
New-Item -ItemType Directory -Force configs, inventory, docs, tests
```

## 4.3 Ajouter une configuration de référence

Dans `configs/sw-access-01.cfg`, saisissez cet exemple pédagogique :

```text
! Configuration de référence fictive
hostname SW-ACCESS-01
!
vlan 10
 name USERS
!
vlan 20
 name VOICE
!
interface GigabitEthernet1/0/1
 description Poste-utilisateur
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
```

Cette syntaxe est inspirée de Cisco IOS. Elle doit être adaptée au modèle d'équipement, à sa version logicielle et à la syntaxe du constructeur avant toute utilisation réelle.

Une configuration conservée dans Git ne devient pas automatiquement la configuration active d'un appareil.

## 4.4 Ajouter un inventaire d'exemple

Dans `inventory/devices.example.yml` :

```yaml
devices:
  - name: SW-ACCESS-01
    platform: cisco_ios
    role: access
    management_address: 192.0.2.11

  - name: RTR-EDGE-01
    platform: cisco_ios
    role: edge
    management_address: 192.0.2.1
```

Les adresses du réseau `192.0.2.0/24` sont réservées à la documentation. Elles illustrent la structure attendue et ne désignent pas de véritables équipements à administrer.

Un inventaire réel devra tenir compte des plateformes, des adresses de gestion, des environnements et des règles de sécurité de l'organisation.

## 4.5 Créer le premier commit

Vérifiez l'état du dépôt :

```bash
git status
```

Git affiche notamment les fichiers qui ne sont pas encore suivis.

Ajoutez la configuration, puis enregistrez-la :

```bash
git add configs/sw-access-01.cfg
git commit -m "Ajoute la configuration de référence du commutateur"
```

Vérifiez ensuite :

```bash
git status
git log --oneline
```

`git log --oneline` affiche les commits de manière compacte.

**À retenir :** `git add` prépare les changements ; `git commit` enregistre les changements préparés dans l'historique.

---

# 5. Comprendre le cycle Git

Le cycle de travail local comporte trois zones conceptuelles :

1. le répertoire de travail ;
2. l'index ;
3. l'historique des commits.

Les fichiers passent du répertoire de travail à l'index avec `git add`, puis de l'index à l'historique avec `git commit`.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="335" viewBox="0 0 960 335" role="img" aria-labelledby="git-cycle-title git-cycle-desc">
  <title id="git-cycle-title">Cycle Git en trois zones</title>
  <desc id="git-cycle-desc">Le répertoire de travail passe à l'index avec git add, puis à l'historique avec git commit. Les flux animés sont représentés par des tirets sur les lignes directionnelles, sans objet mobile.</desc>
  <defs>
    <marker id="git-cycle-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .gc-box{fill:#15253a;stroke:#60a5fa;stroke-width:2}
      .gc-title{font:700 19px Arial,sans-serif;fill:#f8fafc}
      .gc-text{font:14px Arial,sans-serif;fill:#dbeafe}
      .gc-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#git-cycle-arrow);animation:gc-dash 2s linear infinite}
      @keyframes gc-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="333" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="28" y="35" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LES TROIS ZONES DU CYCLE LOCAL</text>
  <rect class="gc-box" x="30" y="95" width="250" height="130" rx="12"/>
  <text class="gc-title" x="155" y="130" text-anchor="middle">1. Travail</text>
  <text class="gc-text" x="155" y="160" text-anchor="middle">Fichiers modifiés</text>
  <text class="gc-text" x="155" y="190" text-anchor="middle">git status · git diff</text>
  <rect class="gc-box" x="355" y="95" width="250" height="130" rx="12"/>
  <text class="gc-title" x="480" y="130" text-anchor="middle">2. Index</text>
  <text class="gc-text" x="480" y="160" text-anchor="middle">Changements préparés</text>
  <text class="gc-text" x="480" y="190" text-anchor="middle">git add</text>
  <rect class="gc-box" x="680" y="95" width="250" height="130" rx="12"/>
  <text class="gc-title" x="805" y="130" text-anchor="middle">3. Historique</text>
  <text class="gc-text" x="805" y="160" text-anchor="middle">Version enregistrée</text>
  <text class="gc-text" x="805" y="190" text-anchor="middle">git commit</text>
  <path class="gc-flow" d="M280 160 H347"/>
  <path class="gc-flow" d="M605 160 H672"/>
  <text class="gc-text" x="480" y="265" text-anchor="middle">Relire le diff avant d'ajouter et avant de commiter.</text>
  <text class="gc-text" x="480" y="291" text-anchor="middle">Un commit enregistre l'index, pas tous les fichiers automatiquement.</text>
</svg>

## 5.1 Observer les changements

Modifiez la configuration du commutateur, par exemple en changeant le VLAN d'accès du port de 10 à 20.

Avant d'enregistrer le changement, exécutez :

```bash
git status
git diff
```

Un diff ressemble à ceci :

```diff
 interface GigabitEthernet1/0/1
  description Poste-utilisateur
  switchport mode access
- switchport access vlan 10
+ switchport access vlan 20
  spanning-tree portfast
```

La ligne précédée de `-` est retirée de la version comparée. La ligne précédée de `+` est ajoutée.

Ce changement peut être syntaxiquement acceptable tout en étant incorrect pour le poste connecté au port. Il faut donc vérifier le besoin fonctionnel, et pas simplement la présence d'une modification.

## 5.2 Préparer le commit

```bash
git add configs/sw-access-01.cfg
git diff --cached
git commit -m "Place le port utilisateur dans le VLAN 20"
```

`git diff --cached` montre les changements qui seront inclus dans le prochain commit.

Prenez l'habitude de relire ce résultat avant de commiter. C'est une manière simple d'éviter d'enregistrer des lignes accidentelles ou des changements non prévus.

## 5.3 Retrouver l'historique

```bash
git log --oneline
```

Pour examiner un commit particulier :

```bash
git show <IDENTIFIANT_DU_COMMIT>
```

Remplacez le texte entre chevrons par un identifiant réel fourni par Git.

Ne confondez pas la possibilité de retrouver une ancienne version de fichier avec la restauration automatique d'un équipement réseau. Cette opération nécessite une procédure distincte.

---

# 6. Branches et revue des changements

## 6.1 Pourquoi utiliser des branches ?

Une branche permet de travailler sur une modification sans modifier directement la branche principale.

Par convention, la branche principale est souvent appelée `main`. Une branche de fonctionnalité peut porter un nom comme `feature/ajout-vlan-30`.

Créez une branche :

```bash
git switch -c feature/ajout-vlan-30
```

Sur les anciennes versions de Git qui ne reconnaissent pas `git switch`, utilisez :

```bash
git checkout -b feature/ajout-vlan-30
```

Effectuez votre modification dans cette branche et enregistrez-la :

```bash
git add configs/sw-access-01.cfg
git diff --cached
git commit -m "Ajoute la définition du VLAN 30"
```

## 6.2 Schéma du flux de branches

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-labelledby="branch-title branch-desc">
  <title id="branch-title">Branche de fonctionnalité et intégration</title>
  <desc id="branch-desc">La branche feature part d'un commit de main, reçoit deux commits, puis est intégrée à main après revue et contrôles. L'animation se limite aux tirets du trajet.</desc>
  <defs>
    <marker id="branch-flow-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#86efac"/>
    </marker>
    <style>
      .br-main{fill:none;stroke:#38bdf8;stroke-width:4}
      .br-feature{fill:none;stroke:#a5b4fc;stroke-width:4;stroke-dasharray:8 7;animation:br-dash 2s linear infinite}
      .br-merge{fill:none;stroke:#86efac;stroke-width:4;marker-end:url(#branch-flow-arrow)}
      .br-node{fill:#0f172a;stroke:#e2e8f0;stroke-width:3}
      .br-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .br-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      @keyframes br-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="348" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="26" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UNE MODIFICATION ISOLÉE JUSQU'À LA REVUE</text>
  <text class="br-title" x="28" y="91">main</text>
  <path class="br-main" d="M95 85 H920"/>
  <circle class="br-node" cx="145" cy="85" r="8"/>
  <circle class="br-node" cx="390" cy="85" r="8"/>
  <circle class="br-node" cx="655" cy="85" r="8"/>
  <circle class="br-node" cx="885" cy="85" r="8"/>
  <text class="br-text" x="145" y="65" text-anchor="middle">commit A</text>
  <text class="br-text" x="390" y="65" text-anchor="middle">base stable</text>
  <text class="br-text" x="655" y="65" text-anchor="middle">fusion</text>
  <text class="br-text" x="885" y="65" text-anchor="middle">version intégrée</text>
  <text class="br-title" x="28" y="205">feature</text>
  <path class="br-feature" d="M390 85 C390 145 435 195 500 195 H655"/>
  <circle class="br-node" cx="500" cy="195" r="8"/>
  <circle class="br-node" cx="655" cy="195" r="8"/>
  <text class="br-text" x="500" y="221" text-anchor="middle">commit B</text>
  <text class="br-text" x="655" y="221" text-anchor="middle">commit C</text>
  <path class="br-merge" d="M655 187 C655 150 655 123 655 98"/>
  <text class="br-text" x="790" y="176" text-anchor="middle">Revue + contrôles</text>
  <rect x="170" y="260" width="620" height="55" rx="10" fill="#172554" stroke="#818cf8"/>
  <text class="br-title" x="480" y="283" text-anchor="middle">La branche organise le travail</text>
  <text class="br-text" x="480" y="302" text-anchor="middle">Elle ne constitue pas une autorisation de déploiement.</text>
</svg>

## 6.3 Bonnes pratiques de nommage

Choisissez des noms explicites :

```text
feature/ajout-vlan-30
fix/correction-description-port
docs/procedure-retour-arriere
```

Évitez les noms vagues comme `test`, `modif2` ou `nouveau`.

Les messages de commit doivent également être précis :

```text
Ajoute le VLAN 30 au modèle du commutateur
Corrige la description du port utilisateur
Documente la procédure de retour arrière
```

## 6.4 Dépôt distant et demande de fusion

Une plateforme hébergeant Git permet à une équipe de partager les dépôts, de revoir les différences et de mettre en place des contrôles automatiques.

Après avoir créé un dépôt distant vide sur votre plateforme :

```bash
git remote add origin <URL_DU_DEPOT>
git push -u origin main
```

Remplacez `<URL_DU_DEPOT>` par l'URL fournie par votre plateforme.

Pour publier une branche :

```bash
git push -u origin feature/ajout-vlan-30
```

Ouvrez ensuite une pull request ou merge request selon la plateforme choisie.

La revue doit vérifier, entre autres :

- la raison du changement ;
- les équipements et services concernés ;
- la cohérence du VLAN, de l'adressage ou des routes selon le cas ;
- les modifications inattendues dans le diff ;
- le résultat des contrôles automatiques ;
- les risques et la procédure de retour arrière.

---

# 7. Comprendre la CI/CD réseau

## 7.1 Intégration continue (CI)

La CI exécute automatiquement des contrôles sur les changements proposés ou enregistrés dans le dépôt.

Dans un projet réseau débutant, elle peut :

- vérifier que certains fichiers existent ;
- contrôler les champs obligatoires d'un inventaire ;
- détecter certaines erreurs de format ;
- vérifier des conventions de nommage ;
- rechercher des motifs ressemblant à des secrets ;
- produire un rapport de validation.

La qualité de la CI dépend des contrôles définis. Elle ne peut pas vérifier un comportement qu'elle ne teste pas.

## 7.2 Livraison continue et déploiement continu

La livraison continue désigne une démarche dans laquelle un changement validé est préparé pour pouvoir être livré de manière fiable, souvent avec une approbation avant la mise en production.

Le déploiement continu automatise aussi la mise en production des changements qui satisfont les conditions prévues.

Dans un réseau, le risque d'une modification peut être important. Une mise à jour de VLAN ou de routage peut affecter plusieurs services et utilisateurs.

C'est pourquoi une équipe peut automatiser les tests tout en conservant une approbation humaine pour le déploiement.

## 7.3 Schéma du pipeline CI/CD réseau

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420" role="img" aria-labelledby="pipeline-title pipeline-desc">
  <title id="pipeline-title">Pipeline CI/CD réseau avec étapes de sécurité</title>
  <desc id="pipeline-desc">Un changement passe par Git, la revue, la CI, les tests en laboratoire puis une approbation. Après le déploiement contrôlé, les vérifications confirment le résultat. En cas d'échec, une procédure de remédiation ou de retour arrière est déclenchée. Les animations portent uniquement sur les traits du flux.</desc>
  <defs>
    <marker id="pipeline-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .pl-box{fill:#172033;stroke:#38bdf8;stroke-width:2}
      .pl-gate{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .pl-safe{fill:#123126;stroke:#4ade80;stroke-width:2}
      .pl-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .pl-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .pl-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#pipeline-arrow);animation:pl-dash 1.8s linear infinite}
      @keyframes pl-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="418" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="24" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DU CHANGEMENT AU CONTRÔLE OPÉRATIONNEL</text>
  <rect class="pl-box" x="22" y="68" width="164" height="78" rx="10"/>
  <text class="pl-title" x="104" y="96" text-anchor="middle">1. Changement Git</text>
  <text class="pl-text" x="104" y="119" text-anchor="middle">Branche + diff</text>
  <rect class="pl-box" x="214" y="68" width="164" height="78" rx="10"/>
  <text class="pl-title" x="296" y="96" text-anchor="middle">2. Revue</text>
  <text class="pl-text" x="296" y="119" text-anchor="middle">Validation humaine</text>
  <rect class="pl-box" x="406" y="68" width="164" height="78" rx="10"/>
  <text class="pl-title" x="488" y="96" text-anchor="middle">3. CI</text>
  <text class="pl-text" x="488" y="119" text-anchor="middle">Contrôles automatiques</text>
  <rect class="pl-box" x="598" y="68" width="164" height="78" rx="10"/>
  <text class="pl-title" x="680" y="96" text-anchor="middle">4. Laboratoire</text>
  <text class="pl-text" x="680" y="119" text-anchor="middle">Tests isolés</text>
  <rect class="pl-gate" x="790" y="68" width="188" height="78" rx="10"/>
  <text class="pl-title" x="884" y="96" text-anchor="middle">5. Approbation</text>
  <text class="pl-text" x="884" y="119" text-anchor="middle">Barrière avant production</text>
  <path class="pl-flow" d="M186 107 H207"/>
  <path class="pl-flow" d="M378 107 H399"/>
  <path class="pl-flow" d="M570 107 H591"/>
  <path class="pl-flow" d="M762 107 H783"/>
  <path class="pl-flow" d="M884 146 V208 H720 V245"/>
  <rect class="pl-safe" x="565" y="245" width="310" height="76" rx="10"/>
  <text class="pl-title" x="720" y="273" text-anchor="middle">6. Déploiement contrôlé</text>
  <text class="pl-text" x="720" y="296" text-anchor="middle">Périmètre et fenêtre définis</text>
  <path class="pl-flow" d="M565 283 H494"/>
  <rect class="pl-box" x="185" y="245" width="309" height="76" rx="10"/>
  <text class="pl-title" x="339" y="273" text-anchor="middle">7. Vérification après changement</text>
  <text class="pl-text" x="339" y="296" text-anchor="middle">État, connectivité et services</text>
  <path d="M339 321 V352 H720 V327" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="6 6"/>
  <text class="pl-text" x="520" y="374" text-anchor="middle">Échec : arrêter, diagnostiquer et appliquer une procédure validée</text>
  <text class="pl-text" x="500" y="402" text-anchor="middle">Un contrôle réussi réduit certains risques, mais ne garantit pas l'absence d'incident.</text>
</svg>

## 7.4 Explication des étapes

1. **Changement Git :** un administrateur propose une modification dans une branche.
2. **Revue :** une autre personne vérifie l'intention, les risques et le périmètre.
3. **CI :** les contrôles automatiques recherchent des erreurs détectables.
4. **Laboratoire :** le changement est testé sur une maquette ou un environnement isolé lorsque cela est possible.
5. **Approbation :** une personne autorisée valide le passage à l'étape suivante.
6. **Déploiement contrôlé :** le changement est appliqué selon une procédure définie.
7. **Vérification :** les résultats sont comparés aux critères prévus. En cas d'échec, la progression est arrêtée et la procédure appropriée est suivie.

Pour commencer, les étapes de déploiement et de vérification peuvent être simulées. Le but est d'apprendre à contrôler les changements avant de donner au pipeline des permissions d'accès aux équipements.

---

# 8. Créer son premier pipeline de validation

Nous allons créer un pipeline qui vérifie l'existence des fichiers attendus et recherche certains motifs pouvant correspondre à des secrets.

Il ne se connecte à aucun routeur et ne modifie aucune configuration en production.

## 8.1 Préparer les fichiers

Vérifiez que ces fichiers existent :

```text
configs/sw-access-01.cfg
inventory/devices.example.yml
tests/README.md
```

Dans `tests/README.md`, ajoutez :

```markdown
# Contrôles initiaux

- Vérifier la présence des fichiers requis.
- Contrôler que l'inventaire contient les informations attendues.
- Rechercher certains motifs ressemblant à des secrets.
- Produire un résultat exploitable par l'équipe.
- Ne pas se connecter aux équipements pendant ces contrôles.
```

## 8.2 Ajouter un workflow GitHub Actions

L'exemple ci-dessous est destiné à un dépôt hébergé sur GitHub. Créez :

`.github/workflows/validate.yml`

```yaml
name: Validate network repository

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  basic-checks:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v7

      - name: Check required files
        run: |
          test -f configs/sw-access-01.cfg
          test -f inventory/devices.example.yml
          test -f tests/README.md

      - name: Check for obvious secret assignments
        shell: bash
        run: |
          set +e
          grep -RniE '(password|passwd|secret|token)[[:space:]]*[:=][[:space:]]*[^[:space:]#]+' configs inventory
          result=$?
          set -e

          if [ "$result" -eq 0 ]; then
            echo "Possible secret detected. Review the matched lines."
            exit 1
          elif [ "$result" -eq 1 ]; then
            echo "No matching secret pattern detected."
          else
            echo "The secret-pattern scan encountered an error."
            exit "$result"
          fi
```

Le fichier doit se trouver dans le chemin exact `.github/workflows/validate.yml` pour être reconnu par GitHub Actions.

La référence `actions/checkout@v7` correspond à la branche de version v7 de l'action Checkout. Consultez la documentation officielle avant une utilisation professionnelle et vérifiez les exigences de votre environnement : https://github.com/actions/checkout/releases

## 8.3 Comment fonctionne ce pipeline ?

La section `on` indique que le workflow doit être déclenché lors d'une pull request et lors d'un push sur `main`.

La section `permissions` limite le jeton GitHub aux permissions de lecture du contenu du dépôt.

`actions/checkout` récupère les fichiers du dépôt sur l'environnement d'exécution.

Le premier contrôle vérifie la présence des fichiers requis. Si un fichier est absent, la commande `test -f` renvoie un code d'échec et le job s'arrête.

Le contrôle suivant recherche certains motifs de texte fréquents dans les secrets. S'il trouve un motif, le pipeline échoue.

## 8.4 Limites importantes

Ce pipeline est pédagogique :

- Il ne garantit pas la validité syntaxique de toutes les configurations réseau.
- Le contrôle textuel peut produire des faux positifs.
- Il peut manquer des secrets qui n'utilisent pas les mots recherchés.
- Il ne vérifie pas le fonctionnement des VLAN, du routage ou des ACL sur de vrais équipements.
- Il ne déploie aucun changement sur le réseau.
- Il ne remplace pas un véritable outil de détection des secrets.

Un pipeline doit être amélioré au fur et à mesure que les besoins, les plateformes et les contrôles deviennent plus avancés.

**Principe fondamental :** un contrôle doit indiquer clairement s'il réussit ou échoue. Un simple avertissement qui laisse systématiquement passer une erreur ne constitue pas une barrière fiable.

---

# 9. Sécurité et protection des équipements

Un dépôt réseau peut contenir des informations sensibles, notamment des topologies, des adresses de gestion, des règles de filtrage et, parfois par erreur, des identifiants.

## 9.1 Ne pas versionner les secrets

Évitez d'ajouter à Git :

- des mots de passe en clair ;
- des clés privées ;
- des jetons d'accès ;
- des chaînes de connexion avec des identifiants ;
- des configurations ou sauvegardes exposant des secrets non protégés.

Utilisez un gestionnaire de secrets approuvé par votre organisation lorsque des identifiants sont nécessaires à une automatisation.

Un dépôt privé n'est pas une raison pour enregistrer des secrets en clair.

## 9.2 Utiliser `.gitignore`

Exemple de fichier `.gitignore` :

```gitignore
# Secrets et fichiers d'environnement locaux
.env
.env.*
secrets/
credentials/
*.key
*.pem

# Fichiers temporaires
*.tmp
*.bak
*.swp
.DS_Store
```

Ce fichier réduit les risques d'ajout accidentel. Il ne protège pas un secret déjà suivi par Git.

Si un secret est exposé, le supprimer dans un commit ultérieur ne l'efface pas nécessairement de l'historique. Il faut le révoquer ou le renouveler et appliquer la procédure de réponse à incident de l'organisation.

## 9.3 Limiter les permissions

Un pipeline qui vérifie des fichiers n'a pas besoin d'identifiants permettant de modifier des routeurs.

Lorsqu'un projet évoluera vers un déploiement automatisé :

- séparez les environnements de test et de production ;
- accordez uniquement les permissions nécessaires ;
- protégez les branches principales ;
- séparez les identifiants de lecture et de déploiement ;
- limitez les équipements et opérations autorisés ;
- exigez une approbation pour les changements sensibles ;
- consignez les opérations et vérifiez le résultat du déploiement.

## 9.4 Pourquoi le déploiement automatique est-il risqué ?

Une mauvaise route, une ACL incorrecte ou un VLAN mal affecté peut couper l'accès à plusieurs services.

L'objectif n'est pas de refuser l'automatisation. Il est de construire une automatisation adaptée au risque, avec des tests, des limites, des autorisations et une méthode de récupération.

---

# 10. Tests et retour arrière

Les différents tests ne donnent pas tous le même niveau de garantie.

| Type de contrôle | Question posée | Exemple |
|---|---|---|
| Vérification du dépôt | Les fichiers requis sont-ils présents ? | Fichier d'inventaire |
| Validation des données | Les champs attendus sont-ils renseignés ? | Nom et plateforme de chaque équipement |
| Analyse statique | Le contenu respecte-t-il certaines règles ? | Présence d'un VLAN attendu |
| Test en laboratoire | Le changement se comporte-t-il comme prévu dans une maquette ? | Vérification d'un accès VLAN |
| Précontrôle sur équipement | L'équipement est-il joignable et dans l'état attendu ? | Lecture de l'état des interfaces |
| Déploiement limité | Le changement fonctionne-t-il sur un petit périmètre ? | Équipement pilote |
| Vérification après changement | Le résultat attendu a-t-il été obtenu ? | Connectivité et état des services |

## 10.1 Définir un retour arrière

Un plan de changement doit définir, avant le déploiement :

1. l'état initial connu ;
2. les équipements et services concernés ;
3. les critères déclenchant l'arrêt ;
4. la procédure de retour arrière ;
5. les personnes autorisées à prendre la décision ;
6. les tests permettant de confirmer le rétablissement.

Un commit Git permet de retrouver une ancienne version des fichiers. Il ne restaure pas automatiquement la configuration d'un commutateur ou d'un routeur.

Le retour arrière opérationnel doit être conçu, testé et adapté à la plateforme utilisée.

## 10.2 Bonnes pratiques avant un changement

Avant d'appliquer une modification réseau, vérifiez les points suivants :

- [ ] Le besoin est documenté.
- [ ] Les fichiers modifiés ont été relus.
- [ ] Le diff ne contient que les changements attendus.
- [ ] Les contrôles automatiques sont passés.
- [ ] Les tests adaptés au risque ont été exécutés.
- [ ] Le périmètre de déploiement est identifié.
- [ ] Une procédure de retour arrière existe.
- [ ] La fenêtre et les approbations requises sont définies.
- [ ] Les vérifications après déploiement sont prévues.

---

# 11. Atelier pratique complet

## 11.1 Scénario

Une équipe souhaite ajouter un VLAN nommé `IOT-LAB`, avec l'identifiant 30, au modèle de configuration d'un commutateur de laboratoire.

Le changement ne doit pas être appliqué à un équipement de production. Vous devez créer la proposition, la contrôler, l'enregistrer et expliquer les étapes de revue.

## Étape 1 — Créer une branche

Depuis le dépôt :

```bash
git switch -c feature/vlan-30-iot-lab
```

Cette branche isole le travail.

## Étape 2 — Modifier la configuration

Dans `configs/sw-access-01.cfg`, ajoutez :

```text
vlan 30
 name IOT-LAB
```

Ne modifiez pas d'autres lignes sans raison documentée.

## Étape 3 — Examiner le diff

```bash
git status
git diff
```

Vérifiez que seules les lignes prévues ont été ajoutées. Si d'autres différences apparaissent, comprenez leur origine avant de continuer.

## Étape 4 — Préparer le changement

```bash
git add configs/sw-access-01.cfg
git diff --cached
```

Relisez le diff préparé avant de l'enregistrer.

## Étape 5 — Créer le commit

```bash
git commit -m "Ajoute le VLAN 30 IOT-LAB au modèle"
```

Vérifiez le résultat :

```bash
git log --oneline
git status
```

## Étape 6 — Publier la branche

Si un dépôt distant a déjà été configuré :

```bash
git push -u origin feature/vlan-30-iot-lab
```

Si la commande échoue parce qu'aucun dépôt distant n'est configuré, définissez d'abord le dépôt distant suivant les instructions de votre plateforme.

## Étape 7 — Faire relire le changement

Ouvrez une pull request ou merge request. Expliquez l'objectif du VLAN et demandez une revue.

Le relecteur doit notamment vérifier :

- la légitimité de l'identifiant VLAN ;
- la cohérence avec le plan de segmentation ;
- les besoins de connectivité ;
- les équipements et liens concernés ;
- les tests à effectuer ;
- les risques et le retour arrière.

## Étape 8 — Décider de la suite

Si le changement est accepté, il peut être fusionné selon les règles de l'équipe.

La fusion dans Git ne signifie pas que le VLAN est déjà créé sur les équipements. Un éventuel déploiement constitue une étape opérationnelle distincte.

---

# 12. Dépannage

## 12.1 « J'ai modifié le fichier, mais mon commit ne contient pas le changement »

Exécutez :

```bash
git status
git diff
git diff --cached
```

Vous avez peut-être oublié `git add`, ajouté un autre fichier ou effectué la modification dans un dossier différent.

## 12.2 « Le commit contient une ligne inattendue »

Examinez le commit et le diff. Si le commit a déjà été partagé, coordonnez la correction avec l'équipe au lieu de réécrire un historique partagé sans autorisation.

## 12.3 « Le pipeline est vert, donc le déploiement est sûr »

Pas nécessairement. Le pipeline a exécuté uniquement les contrôles configurés. Il faut encore tenir compte de leurs limites, de la revue, du risque et de la procédure opérationnelle.

## 12.4 « J'ai supprimé le mot de passe ; le dépôt est maintenant sûr »

Pas forcément. Le secret peut rester présent dans des commits précédents, des journaux ou des artefacts. Il faut traiter l'exposition, révoquer ou renouveler le secret et appliquer la procédure de sécurité de l'organisation.

## 12.5 « La configuration est valide dans Git, donc le routeur l'acceptera »

Git ne valide pas la syntaxe propre au constructeur. Même un analyseur ou un test en laboratoire ne garantit pas à lui seul le comportement en production. Il faut des vérifications adaptées à la plateforme et au risque.

## 12.6 « Git refuse de changer de branche à cause de mes modifications »

Exécutez :

```bash
git status
```

Examinez les modifications non enregistrées. Ne les supprimez pas aveuglément avec une commande destructive. En fonction du besoin, vous pouvez les commiter, les préparer dans un autre endroit ou les mettre de côté avec une procédure appropriée.

---

# 13. Évaluation et corrigé

Répondez aux questions avant de consulter les solutions.

## 13.1 Questions

1. Quelle est la différence entre `git add` et `git commit` ?
2. Pourquoi créer une branche avant de modifier un fichier réseau ?
3. Que montre `git diff --cached` ?
4. Git et la CI/CD remplissent-ils le même rôle ?
5. Pourquoi un pipeline vert ne suffit-il pas à autoriser un déploiement ?
6. Pourquoi un secret supprimé dans un commit ultérieur peut-il rester exposé ?
7. Citez trois contrôles qui peuvent être effectués sans connexion aux équipements.
8. Pourquoi faut-il tester la procédure de retour arrière à l'avance ?
9. Quelle différence existe entre une configuration stockée dans Git et une configuration active sur un routeur ?
10. Quel est l'intérêt d'une revue humaine avant une modification risquée ?

## 13.2 Corrigé

**1. `git add` et `git commit`**

`git add` prépare des changements dans l'index. `git commit` enregistre les changements préparés dans l'historique.

**2. Utilité d'une branche**

Une branche isole la modification et facilite la revue sans changer directement la branche principale pendant la préparation.

**3. `git diff --cached`**

Cette commande affiche les changements préparés pour le prochain commit.

**4. Différence entre Git et CI/CD**

Git versionne les fichiers. La CI/CD automatise des contrôles et orchestre les étapes de validation ou de livraison.

**5. Limites d'un pipeline vert**

Le résultat signifie uniquement que les contrôles configurés ont réussi. Il ne remplace pas la vérification du risque, la revue ou les tests qui n'ont pas été exécutés.

**6. Secret supprimé**

Le secret peut subsister dans l'historique Git, les journaux ou les artefacts. Il faut le révoquer ou le renouveler et traiter l'exposition.

**7. Contrôles sans équipement**

Vérifier que les fichiers requis existent, valider la présence des champs d'inventaire, vérifier des conventions de nommage ou rechercher certains motifs de secrets.

**8. Retour arrière testé**

Une procédure non testée peut échouer au moment où le réseau est dégradé. Le test permet d'identifier les prérequis, les limites et les étapes nécessaires à la récupération.

**9. Fichier et configuration active**

Le fichier est une représentation versionnée. La configuration active est l'état réellement appliqué à l'équipement. Les deux peuvent différer.

**10. Revue humaine**

Elle permet de vérifier l'intention, le périmètre, les impacts, les hypothèses et les risques qu'un contrôle automatique ne sait pas nécessairement détecter.

---

# 14. Synthèse et préparation du niveau intermédiaire

## 14.1 Le workflow de référence

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="325" viewBox="0 0 960 325" role="img" aria-labelledby="summary-title summary-desc">
  <title id="summary-title">Workflow de base d'un changement réseau</title>
  <desc id="summary-desc">Un changement passe par la définition du besoin, une branche Git, l'inspection du diff, les contrôles et la revue. L'application en production reste séparée et nécessite un plan de changement. L'animation est limitée aux tirets des flèches directionnelles.</desc>
  <defs>
    <marker id="summary-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#93c5fd"/>
    </marker>
    <style>
      .sm-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .sm-flow{fill:none;stroke:#93c5fd;stroke-width:3;stroke-dasharray:7 6;marker-end:url(#summary-arrow);animation:sm-dash 2s linear infinite}
      .sm-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .sm-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      @keyframes sm-dash{to{stroke-dashoffset:-26}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="323" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="24" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UNE MODIFICATION TRAÇABLE ET CONTRÔLÉE</text>
  <rect class="sm-box" x="22" y="68" width="168" height="76" rx="10"/>
  <text class="sm-title" x="106" y="96" text-anchor="middle">1. Besoin</text>
  <text class="sm-text" x="106" y="119" text-anchor="middle">Définir l'objectif</text>
  <rect class="sm-box" x="214" y="68" width="168" height="76" rx="10"/>
  <text class="sm-title" x="298" y="96" text-anchor="middle">2. Branche</text>
  <text class="sm-text" x="298" y="119" text-anchor="middle">Isoler le changement</text>
  <rect class="sm-box" x="406" y="68" width="168" height="76" rx="10"/>
  <text class="sm-title" x="490" y="96" text-anchor="middle">3. Diff</text>
  <text class="sm-text" x="490" y="119" text-anchor="middle">Relire les lignes</text>
  <rect class="sm-box" x="598" y="68" width="168" height="76" rx="10"/>
  <text class="sm-title" x="682" y="96" text-anchor="middle">4. CI + tests</text>
  <text class="sm-text" x="682" y="119" text-anchor="middle">Détecter les erreurs</text>
  <rect class="sm-box" x="790" y="68" width="150" height="76" rx="10"/>
  <text class="sm-title" x="865" y="96" text-anchor="middle">5. Revue</text>
  <text class="sm-text" x="865" y="119" text-anchor="middle">Obtenir l'accord</text>
  <path class="sm-flow" d="M190 106 H207"/>
  <path class="sm-flow" d="M382 106 H399"/>
  <path class="sm-flow" d="M574 106 H591"/>
  <path class="sm-flow" d="M766 106 H783"/>
  <rect x="150" y="205" width="660" height="78" rx="12" fill="#132b22" stroke="#4ade80" stroke-width="2"/>
  <text class="sm-title" x="480" y="234" text-anchor="middle">Fusionner n'est pas déployer</text>
  <text class="sm-text" x="480" y="257" text-anchor="middle">La production exige un plan, une approbation et des vérifications adaptées au risque.</text>
  <path class="sm-flow" d="M865 144 V173 H810 V205"/>
</svg>

## 14.2 Les commandes essentielles

```bash
git init
git status
git diff
git add <fichier>
git diff --cached
git commit -m "Description du changement"
git log --oneline
git switch -c feature/nom-du-changement
git push -u origin feature/nom-du-changement
```

La commande `git push` suppose qu'un dépôt distant a été configuré.

## 14.3 Ce que vous devez savoir faire avant de passer au niveau suivant

Vous devez être capable de :

- créer et organiser un dépôt réseau ;
- versionner une configuration et un inventaire fictifs ;
- lire un diff ;
- préparer un commit sans inclure de changements inattendus ;
- créer et publier une branche ;
- expliquer le principe d'une revue ;
- comprendre le rôle d'une CI simple ;
- reconnaître qu'un pipeline ne remplace pas les contrôles opérationnels ;
- expliquer les risques liés aux secrets ;
- décrire une méthode de retour arrière.

## 14.4 Suite du parcours : niveau intermédiaire

Le niveau intermédiaire pourra s'appuyer sur les bases de ce cours pour introduire progressivement :

- la validation automatique des inventaires YAML ;
- des tests de données et de configuration plus stricts ;
- des analyseurs adaptés aux plateformes réseau ;
- des environnements de laboratoire et des simulations ;
- des rapports de validation produits par les pipelines ;
- des conditions d'approbation et une séparation des environnements ;
- l'intégration de bibliothèques d'automatisation réseau ;
- les contrôles avant et après changement ;
- une stratégie de déploiement progressif et de retour arrière.

Le niveau expert pourra ensuite traiter l'architecture des pipelines, les stratégies de déploiement à grande échelle, les contrôles d'état attendu, les tests d'intégration avancés et la gouvernance des changements.

**La priorité du niveau débutant n'est pas de déployer plus vite. C'est de rendre chaque changement compréhensible, traçable, vérifiable et préparé pour une récupération maîtrisée.**

---

## Références utiles

- Git — documentation officielle : https://git-scm.com/doc
- Documentation GitHub Actions : https://docs.github.com/actions
- Versions et notes de publication de l'action Checkout : https://github.com/actions/checkout/releases

**Fichier :** `cicd-network-debutant.md`  
**Niveau :** Débutant  
**Fin du cours**
