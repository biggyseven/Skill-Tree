# NETMIKO EXPERT
## De scripts réseau à une automatisation professionnelle, fiable et industrialisable

**Fichier :** `netmiko-expert.md`  
**Parcours pédagogique :** Débutant → Intermédiaire → Expert  
**Domaine :** automatisation des réseaux, Python, SSH, Netmiko et pratiques NetDevOps  
**Public cible :** administrateurs réseau, ingénieurs réseau, ingénieurs infrastructure, NetDevOps et responsables d'automatisation  
**Objectif final :** construire une application d'automatisation qui ne se contente pas d'envoyer des commandes, mais qui contrôle les entrées, limite les risques, vérifie les résultats, conserve des preuves et sait réagir aux échecs.

---

# AVANT-PROPOS — LE NIVEAU EXPERT EST LA SUITE DU PARCOURS

Ce document ne constitue pas un cours indépendant destiné à remplacer les deux niveaux précédents. Il en représente le prolongement naturel.

Vous avez d'abord appris à écrire du Python, à comprendre les dictionnaires, à parcourir des listes, à créer des fonctions et à établir une connexion SSH avec Netmiko. Vous avez ensuite appris à réutiliser ces bases pour interroger plusieurs équipements, organiser les commandes, gérer les premières erreurs et commencer à automatiser les tâches réseau.

Le niveau Expert conserve ces acquis, mais les inscrit dans une architecture plus rigoureuse.

## Ce qui change entre les trois niveaux

| Niveau | Compétence centrale | Résultat attendu |
|---|---|---|
| Débutant | Comprendre et utiliser Netmiko | Se connecter, envoyer une commande, lire la réponse et fermer la session |
| Intermédiaire | Réutiliser et organiser les opérations | Automatiser plusieurs équipements, créer des fonctions, collecter et traiter les résultats |
| Expert | Concevoir un système exploitable | Valider, sécuriser, tester, mesurer, contrôler les changements et produire des preuves |

Le niveau Expert ne vous demande donc pas d'abandonner `ConnectHandler`, `send_command()` ou `send_config_set()`. Il vous apprend plutôt à intégrer ces méthodes dans un système où leurs conséquences sont anticipées et contrôlées.

La différence fondamentale est la suivante :

- Le Débutant apprend à exécuter une opération.
- L'Intermédiaire apprend à répéter cette opération sur plusieurs équipements.
- L'Expert apprend à garantir que l'opération est autorisée, correctement exécutée, vérifiée, documentée et récupérable en cas de problème.

Un script peut fonctionner parfaitement lors d'une démonstration et demeurer dangereux en production. Un mot de passe codé en dur, une liste de cibles incorrecte, une commande rejetée sans exception Python ou une erreur qui passe inaperçue peuvent transformer un script apparemment réussi en source d'incident.

C'est précisément ce que ce cours doit vous apprendre à éviter.

## Les acquis préalables

Vous devriez déjà savoir :

- utiliser Python et ses types de données principaux ;
- manipuler des listes, des dictionnaires, des fonctions et des exceptions ;
- établir une connexion avec `ConnectHandler(**device)` ;
- utiliser `send_command()` pour une commande de lecture ;
- comprendre l'utilisation de `send_config_set()` pour une séquence de configuration ;
- distinguer une commande de collecte d'une commande qui modifie l'état d'un équipement ;
- charger des informations depuis un inventaire ;
- traiter plusieurs équipements sans recopier manuellement tout le code ;
- fermer proprement une connexion Netmiko ;
- reconnaître que les commandes dépendent du constructeur, du système d'exploitation réseau et parfois de la version logicielle.

Si ces bases ne sont pas encore suffisamment maîtrisées, révisez les niveaux précédents avant de poursuivre. Les chapitres qui suivent s'appuient sur ces compétences : ils ne les remplacent pas.

## Les compétences que vous allez construire

À la fin du cours, vous devrez être capable de :

1. concevoir une architecture Python organisée par responsabilités ;
2. charger et valider un inventaire d'équipements ;
3. séparer les données d'inventaire, les secrets et les paramètres d'exploitation ;
4. établir des connexions Netmiko avec des délais maîtrisés ;
5. respecter la confiance SSH et les règles de moindre privilège ;
6. exécuter des opérations sur plusieurs équipements sans surcharger le réseau ;
7. normaliser les résultats et distinguer les différentes catégories d'échec ;
8. travailler avec des sorties CLI, des parseurs et des données structurées ;
9. préparer un changement de configuration avant de l'appliquer ;
10. comparer l'état initial à l'état final ;
11. valider l'état obtenu au lieu de se contenter d'une réponse textuelle ;
12. concevoir une stratégie de récupération et de retour arrière réaliste ;
13. écrire des tests unitaires sans équipement réseau réel ;
14. enregistrer des logs utiles sans y exposer des secrets ;
15. produire des rapports adaptés à une exploitation professionnelle ;
16. intégrer des contrôles automatisés dans une chaîne d'intégration continue ;
17. terminer un projet d'automatisation avec une documentation et une procédure opérationnelle.

> **Principe essentiel :** Netmiko facilite l'interaction avec une interface CLI. Il ne garantit pas à lui seul que la commande est valide, que le changement est correct, que la configuration est sauvegardée ou que le service réseau fonctionne comme prévu. Ces garanties doivent être construites autour de lui.

---

# TABLE DES MATIÈRES

1. Le contrat de progression
2. Comprendre la place de Netmiko dans une architecture experte
3. Environnement de développement et reproductibilité
4. Organisation du projet
5. Architecture et responsabilités des modules
6. Inventaire : validation et sélection du périmètre
7. Secrets, comptes de service et sécurité SSH
8. Gestion robuste des connexions
9. Collecte des données et commandes autorisées
10. Parsing et normalisation des sorties
11. Exécution concurrente contrôlée
12. Gestion des erreurs et des reprises
13. Gestion professionnelle des changements de configuration
14. Idempotence, validation et stratégie de récupération
15. Observabilité, journaux et rapports
16. Tests unitaires et intégration continue
17. Industrialisation et gouvernance
18. Laboratoires progressifs
19. Projet final : NetOps Change Runner
20. Dépannage avancé
21. Évaluation de sortie
22. Références officielles

---

# 1. LE CONTRAT DE PROGRESSION

## 1.1. Du premier script à l'application maintenable

Au niveau Débutant, un script de connexion peut être écrit ainsi :

```python
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "192.0.2.10",
    "username": "netops",
    "password": "secret",
}

connection = ConnectHandler(**device)

output = connection.send_command("show ip interface brief")
print(output)

connection.disconnect()
```

Ce code est utile pour comprendre le cycle de base :

1. créer les paramètres de connexion ;
2. établir une session ;
3. envoyer une commande ;
4. récupérer la sortie ;
5. fermer la session.

Cependant, ce script n'est pas encore une application de production.

Le mot de passe apparaît directement dans le code. L'adresse IP est codée en dur. Si la connexion échoue, le programme peut s'interrompre sans produire de rapport normalisé. Si la commande renvoie un message d'erreur dans sa sortie, le programme peut la considérer à tort comme réussie. Enfin, si une exception se produit avant `disconnect()`, la fermeture de session n'est pas garantie.

Au niveau Intermédiaire, nous aurions probablement déplacé les paramètres dans un inventaire, ajouté une fonction et parcouru plusieurs équipements.

Au niveau Expert, nous allons pousser cette progression plus loin :

- les entrées sont validées avant toute connexion ;
- le périmètre des cibles est explicite ;
- les secrets sont séparés des données de configuration ;
- les paramètres SSH sont définis selon une politique connue ;
- chaque opération dispose d'un délai maximal ;
- chaque session est fermée, même après une exception ;
- chaque résultat reçoit un statut normalisé ;
- les erreurs de connexion sont distinguées des erreurs de commande ;
- les opérations de configuration sont soumises à des contrôles supplémentaires ;
- les résultats sont conservés sous une forme exploitable ;
- les tests permettent de valider la logique sans matériel réel.

L'objectif n'est pas d'ajouter de la complexité pour elle-même. L'objectif est de supprimer les ambiguïtés et de réduire les risques.

## 1.2. Les contrats d'une opération réseau

Une opération professionnelle est définie par cinq éléments.

### A. Les entrées

Les données sont-elles valides ? L'équipement appartient-il au périmètre autorisé ? La commande fait-elle partie du catalogue approuvé ? Le profil d'identifiants est-il autorisé ?

### B. Les préconditions

L'équipement est-il dans l'état attendu ? La version logicielle est-elle compatible ? La fenêtre de changement est-elle ouverte ? La sauvegarde initiale est-elle disponible ?

### C. L'exécution

Une session est-elle établie avec les bons paramètres ? Le délai est-il borné ? Une autre tâche peut-elle agir en même temps sur la même cible ? Le code sait-il interrompre l'opération si une limite est dépassée ?

### D. Les résultats

L'opération a-t-elle été transportée correctement ? La CLI a-t-elle accepté la commande ? L'état recherché a-t-il été obtenu ? Les preuves sont-elles disponibles ?

### E. La récupération

Si l'état final n'est pas conforme, le système doit-il s'arrêter, recommencer une lecture, revenir à un état précédent ou demander l'intervention d'un opérateur ?

Ces décisions doivent être prises au moment de concevoir le workflow, et non improvisées après un incident.

## 1.3. Tout ne doit pas être automatisé sans contrôle humain

L'automatisation peut préparer un plan, effectuer une collecte, détecter un écart, générer un diff et exécuter une opération autorisée.

En revanche, le périmètre d'autorisation, la fenêtre de maintenance, les critères d'abandon et les conséquences acceptables doivent être définis par l'organisation.

Un programme ne doit pas considérer qu'un changement est acceptable simplement parce que sa syntaxe Python est correcte ou parce que Netmiko n'a pas levé d'exception.

---

# 2. COMPRENDRE LA PLACE DE NETMIKO DANS UNE ARCHITECTURE EXPERTE

Netmiko facilite les interactions avec les interfaces CLI de nombreux équipements réseau. Il fournit des pilotes adaptés aux particularités des différentes plateformes et des méthodes permettant d'envoyer des commandes, de reconnaître des invites et de manipuler des modes de configuration.

Mais Netmiko n'est pas, à lui seul :

- un inventaire de référence ;
- un coffre de secrets ;
- un système de contrôle des changements ;
- un parseur universel ;
- un moteur de politique de sécurité ;
- une solution de supervision réseau ;
- une garantie de sauvegarde de configuration ;
- un mécanisme universel de rollback ;
- un système complet de validation métier.

## 2.1. Trois résultats différents

Considérons une commande envoyée à un routeur.

### Niveau 1 : le transport

La connexion existe, la commande a été envoyée et Netmiko a pu récupérer une réponse.

Cela prouve que l'interaction CLI a fonctionné à un certain niveau.

### Niveau 2 : la commande

La commande n'a pas été visiblement rejetée. La sortie contient les informations ou le résultat que le programme s'attendait à voir.

Cela constitue une preuve plus forte, mais reste insuffisant dans certains cas.

### Niveau 3 : l'état métier

L'équipement possède réellement l'état souhaité, et les contrôles associés confirment que le changement a produit le résultat attendu.

Par exemple, après avoir modifié le VLAN d'un port, il ne suffit pas que `send_config_set()` ait renvoyé une chaîne. Il faut vérifier que le port existe, qu'il appartient au VLAN attendu et que les contrôles de service définis pour ce changement sont satisfaits.

La règle est simple :

**Une réponse CLI n'est pas une preuve suffisante de conformité de l'état final.**

## 2.2. Choisir l'outil adapté

Netmiko convient particulièrement lorsqu'il faut automatiser une interface CLI existante.

D'autres options peuvent être mieux adaptées à certains besoins :

- une API constructeur lorsque les opérations sont disponibles sous une forme structurée ;
- NETCONF ou RESTCONF lorsque l'équipement expose des interfaces de gestion normalisées ;
- NAPALM pour les plateformes et opérations qu'il prend en charge ;
- Ansible pour des workflows déclaratifs et une orchestration existante ;
- Paramiko directement lorsque le besoin porte sur des détails SSH de bas niveau que l'abstraction Netmiko ne couvre pas.

Ces approches ne sont pas nécessairement concurrentes. L'architecture doit sélectionner l'outil qui fournit le meilleur contrôle de l'état et le meilleur contrat de résultat pour l'opération visée.

---

# 3. ENVIRONNEMENT DE DÉVELOPPEMENT ET REPRODUCTIBILITÉ

## 3.1. Vérifier l'environnement Python

Avant de développer, vérifiez la version de Python, celle de Netmiko et l'état des dépendances.

```bash
python --version
python -m pip --version
python -m pip show netmiko
python -m pip check
```

La documentation et l'historique officiel du projet doivent être consultés lorsqu'une mise à jour de Netmiko est envisagée. La version 4.8.0 figure parmi les releases du projet : vérifiez les notes de version et les contraintes de votre environnement avant de la retenir.

Références :
- Releases Netmiko : https://github.com/ktbyers/netmiko/releases
- Documentation API : https://ktbyers.github.io/netmiko/docs/netmiko/

Le principe à retenir est qu'une version doit être testée puis verrouillée. Une installation qui récupère automatiquement la version la plus récente peut modifier le comportement de votre application sans modification de votre code.

## 3.2. Créer un environnement virtuel

Linux ou macOS :

```bash
mkdir netops-change-runner
cd netops-change-runner

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
```

Windows PowerShell :

```powershell
mkdir netops-change-runner
cd netops-change-runner

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
```

Installer les dépendances de départ :

```bash
python -m pip install "netmiko==4.8.0" "PyYAML>=6,<7" "pytest>=8,<10" "ruff>=0.10,<1"
```

Ces contraintes illustrent un environnement contrôlé. Vérifiez les versions disponibles, leurs contraintes Python et les politiques de dépendances de votre organisation avant d'adopter exactement ces valeurs.

Après validation, enregistrez les dépendances installées :

```bash
python -m pip freeze > requirements-lock.txt
python -m pip check
```

Un fichier de dépendances ne devrait pas être modifié en production sans tests. Dans une équipe, les mises à jour doivent suivre un processus prévisible : changement de version, tests, validation et déploiement.

## 3.3. Pourquoi l'environnement doit être reproductible

Imaginez qu'un script fonctionne aujourd'hui, puis échoue après une mise à jour de dépendance qui n'a pas été testée. Si vous ne connaissez ni la version exacte de Netmiko ni celle de Python, il devient plus difficile de déterminer si la cause vient de votre code, de la bibliothèque ou de l'environnement.

Une configuration reproductible réduit cette incertitude.

Elle doit permettre de répondre à ces questions :

- Quelle version de Python a exécuté le lot ?
- Quelle version de Netmiko était installée ?
- Quelles dépendances étaient verrouillées ?
- Quel commit du programme a été exécuté ?
- Avec quels paramètres non secrets ?
- Quelle version de l'inventaire a été utilisée ?

Ces informations deviennent essentielles pendant un incident ou un audit.

---

# 4. ORGANISATION DU PROJET

Au lieu de placer toutes les fonctions dans un seul fichier, nous allons répartir les responsabilités.

Arborescence de référence :

```text
netops-change-runner/
├── README.md
├── requirements-lock.txt
├── .gitignore
├── inventory/
│   └── devices.yaml
├── config/
│   └── policy.yaml
├── artifacts/
│   ├── backups/
│   ├── reports/
│   └── logs/
├── src/
│   └── netops/
│       ├── __init__.py
│       ├── inventory.py
│       ├── credentials.py
│       ├── connections.py
│       ├── operations.py
│       ├── results.py
│       ├── runner.py
│       ├── changes.py
│       └── reporting.py
└── tests/
    ├── test_inventory.py
    ├── test_operations.py
    └── test_changes.py
```

## 4.1. Responsabilité de chaque module

| Module | Responsabilité |
|---|---|
| `inventory.py` | Chargement, validation et sélection des équipements |
| `credentials.py` | Résolution des profils d'identifiants |
| `connections.py` | Création de sessions Netmiko et paramètres SSH |
| `operations.py` | Catalogue de commandes et validations de sortie |
| `results.py` | Modèle standard de résultat |
| `runner.py` | Orchestration des tâches et contrôle de concurrence |
| `changes.py` | Construction et validation des plans de changement |
| `reporting.py` | Journaux, rapports et statistiques |
| `tests/` | Vérification du comportement sans matériel réel |

La séparation doit rester utile. Il ne s'agit pas de créer des dizaines de fichiers inutiles, mais d'éviter que les règles de sécurité, les connexions, les commandes et les rapports soient mélangés dans une fonction unique difficile à tester.

## 4.2. Fichier `.gitignore`

```gitignore
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.env
artifacts/
*.log
*.session
*.secret
```

Les configurations réseau et les journaux de session peuvent contenir des informations sensibles. Les artefacts ne doivent pas être publiés accidentellement dans un dépôt public.

L'exclusion Git ne remplace toutefois pas une politique de conservation. Si une organisation doit conserver des sauvegardes ou des journaux, elle doit le faire dans un stockage approprié, avec des permissions, une rétention et des mécanismes de protection adaptés.

---

# 5. ARCHITECTURE CIBLE ET RESPONSABILITÉS

L'application suivra le flux suivant :

1. chargement de l'inventaire ;
2. validation des données ;
3. sélection d'un périmètre explicite ;
4. résolution du profil d'identifiants ;
5. préparation de l'opération ;
6. ouverture d'une session ;
7. exécution de l'opération autorisée ;
8. validation du résultat ;
9. fermeture de la session ;
10. enregistrement du résultat ;
11. génération d'un rapport.

Chaque couche reçoit des informations déjà préparées par la couche précédente.

Le module d'inventaire ne doit pas ouvrir de session SSH. Le module de connexion ne doit pas décider quel lot de production est autorisé. Le module de rapport ne doit pas modifier un équipement. Cette séparation réduit les effets secondaires inattendus.

## 5.1. Premier schéma SVG animé : architecture

Le schéma utilise des tirets animés dans les liaisons plutôt qu'un cercle qui circule sur tous les diagrammes. Les identifiants SVG et les animations sont propres à ce schéma.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 330" role="img" aria-labelledby="arch-title arch-desc" style="max-width:100%;height:auto">
  <title id="arch-title">Architecture du projet Netmiko Expert</title>
  <desc id="arch-desc">L'inventaire validé et le plan approuvé alimentent l'orchestrateur, qui utilise Netmiko pour communiquer avec les équipements. Les résultats reviennent vers la couche de validation et de rapport.</desc>
  <defs>
    <marker id="arch-arrow-head" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#4bb9e8"/></marker>
    <style>
      @keyframes arch-flow { to { stroke-dashoffset: -28; } }
      @keyframes arch-glow { 0%,100% { stroke-opacity: .65; } 50% { stroke-opacity: 1; } }
      .arch-line { fill:none; stroke:#4bb9e8; stroke-width:2.5; stroke-dasharray:7 7; animation:arch-flow 2s linear infinite; marker-end:url(#arch-arrow-head); }
      .arch-node { fill:#152338; stroke:#4bb9e8; stroke-width:1.6; animation:arch-glow 3s ease-in-out infinite; }
      .arch-label { font:600 15px sans-serif; text-anchor:middle; fill:#f1f5ff; }
      .arch-small { font:12px sans-serif; text-anchor:middle; fill:#b0c2df; }
    </style>
  </defs>
  <rect x="1" y="1" width="918" height="328" rx="14" fill="#0b1322" stroke="#2a3b54"/>
  <text x="460" y="37" font-family="sans-serif" font-size="18" text-anchor="middle" fill="#e8f0ff">Une opération contrôlée de bout en bout</text>
  <rect class="arch-node" x="24" y="88" width="150" height="82" rx="10"/>
  <text class="arch-label" x="99" y="120">Inventaire</text>
  <text class="arch-small" x="99" y="143">cibles validées</text>
  <rect class="arch-node" x="207" y="88" width="150" height="82" rx="10"/>
  <text class="arch-label" x="282" y="120">Politique</text>
  <text class="arch-small" x="282" y="143">plan autorisé</text>
  <rect class="arch-node" x="390" y="88" width="150" height="82" rx="10"/>
  <text class="arch-label" x="465" y="120">Orchestrateur</text>
  <text class="arch-small" x="465" y="143">délai + concurrence</text>
  <rect class="arch-node" x="573" y="88" width="140" height="82" rx="10"/>
  <text class="arch-label" x="643" y="120">Netmiko</text>
  <text class="arch-small" x="643" y="143">sessions SSH</text>
  <rect class="arch-node" x="746" y="88" width="150" height="82" rx="10"/>
  <text class="arch-label" x="821" y="120">Équipements</text>
  <text class="arch-small" x="821" y="143">CLI réelle</text>
  <path class="arch-line" d="M174 129 H202"/>
  <path class="arch-line" d="M357 129 H385"/>
  <path class="arch-line" d="M540 129 H568"/>
  <path class="arch-line" d="M713 129 H741"/>
  <path d="M821 180 V220 H465 V177" fill="none" stroke="#f1a75b" stroke-width="2.4" stroke-dasharray="5 7" style="animation:arch-flow 2.5s linear infinite"/>
  <rect x="315" y="220" width="300" height="47" rx="9" fill="#2a211b" stroke="#f1a75b"/>
  <text x="465" y="240" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#ffe0b0">Validation + preuves</text>
  <text x="465" y="255" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#eacda5">statut, logs, rapport</text>
  <text x="460" y="302" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#bac9de">La réussite se mesure sur l'état obtenu, pas uniquement sur le transport.</text>
</svg>

## 5.2. Principes d'architecture

### Faible couplage

Un changement du format YAML ne doit pas nécessiter une réécriture des connexions SSH.

### Contrats de données

Le résultat d'une opération doit respecter une structure connue, qu'elle réussisse ou échoue.

### Comportements prévisibles

Chaque composant doit avoir des limites claires. Une commande ne doit pas tourner indéfiniment ; une tâche en échec ne doit pas disparaître du rapport.

### Séparation des privilèges

La lecture et la modification ne devraient pas utiliser le même niveau de privilège par défaut.

### Preuves

L'application doit pouvoir expliquer ce qu'elle a exécuté, sur quelle cible, à quel moment, avec quel statut et selon quel plan autorisé.

---

# 6. INVENTAIRE : VALIDATION ET SÉLECTION DU PÉRIMÈTRE

L'inventaire décrit les équipements. Ce n'est pas un script exécutable et ce n'est pas un coffre de mots de passe.

## 6.1. Exemple d'inventaire YAML

`inventory/devices.yaml` :

```yaml
devices:
  - name: edge-r1
    host: 192.0.2.11
    port: 22
    device_type: cisco_ios
    platform_family: ios
    site: lab-douala
    role: edge
    enabled: true
    credential_profile: netops_ro
    tags: [lab, edge, read-only]

  - name: core-r2
    host: 192.0.2.12
    port: 22
    device_type: cisco_ios
    platform_family: ios
    site: lab-douala
    role: core
    enabled: true
    credential_profile: netops_change
    tags: [lab, core, change-window]
```

Les adresses `192.0.2.0/24` appartiennent à une plage de documentation. Remplacez-les par les adresses de votre laboratoire ou de votre réseau autorisé.

Les champs ont des rôles distincts :

- `name` : identifiant stable utilisé dans les rapports ;
- `host` : adresse IP ou nom DNS ;
- `port` : port SSH ;
- `device_type` : nom du pilote Netmiko ;
- `platform_family` : profil de commandes et validations retenu par le projet ;
- `site` : site logique ou physique ;
- `role` : rôle de l'équipement ;
- `enabled` : indique si l'équipement peut être sélectionné ;
- `credential_profile` : profil d'identifiants résolu séparément ;
- `tags` : attributs utiles à une sélection explicite.

Le fait de placer un équipement dans un inventaire ne signifie pas automatiquement qu'il est autorisé à recevoir n'importe quelle opération.

## 6.2. Définir un modèle validé

`src/netops/inventory.py` :

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ipaddress
import re
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,62}$")

ALLOWED_DEVICE_TYPES = {
    "cisco_ios",
    "cisco_xe",
    "cisco_nxos",
    "arista_eos",
    "juniper_junos",
}

ALLOWED_FAMILIES = {"ios", "nxos", "eos", "junos"}


@dataclass(frozen=True)
class Device:
    name: str
    host: str
    port: int
    device_type: str
    platform_family: str
    site: str
    role: str
    enabled: bool
    credential_profile: str
    tags: tuple[str, ...]


def validate_device(raw: dict[str, Any]) -> Device:
    required = {
        "name",
        "host",
        "port",
        "device_type",
        "platform_family",
        "site",
        "role",
        "enabled",
        "credential_profile",
        "tags",
    }

    missing = required - raw.keys()
    unknown = raw.keys() - required

    if missing:
        raise ValueError(f"Champs obligatoires absents : {sorted(missing)}")

    if unknown:
        raise ValueError(f"Champs non reconnus : {sorted(unknown)}")

    name = raw["name"]

    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise ValueError("Nom d'équipement invalide")

    host = raw["host"]

    if not isinstance(host, str) or not host.strip():
        raise ValueError(f"{name}: host doit être une chaîne non vide")

    try:
        ipaddress.ip_address(host)
    except ValueError:
        normalized_host = host.rstrip(".")

        if (
            not normalized_host
            or len(normalized_host) > 253
            or any(
                not label
                or len(label) > 63
                or not re.fullmatch(
                    r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?",
                    label,
                )
                for label in normalized_host.split(".")
            )
        ):
            raise ValueError(f"{name}: adresse IP ou nom DNS invalide")

    port = raw["port"]

    if isinstance(port, bool) or not isinstance(port, int):
        raise ValueError(f"{name}: port doit être un entier")

    if not 1 <= port <= 65535:
        raise ValueError(f"{name}: port hors limites")

    device_type = raw["device_type"]

    if device_type not in ALLOWED_DEVICE_TYPES:
        raise ValueError(f"{name}: device_type non autorisé")

    family = raw["platform_family"]

    if family not in ALLOWED_FAMILIES:
        raise ValueError(f"{name}: platform_family non autorisée")

    enabled = raw["enabled"]

    if not isinstance(enabled, bool):
        raise ValueError(f"{name}: enabled doit être un booléen")

    profile = raw["credential_profile"]

    if not isinstance(profile, str) or not NAME_RE.fullmatch(profile):
        raise ValueError(f"{name}: credential_profile invalide")

    tags = raw["tags"]

    if not isinstance(tags, list):
        raise ValueError(f"{name}: tags doit être une liste")

    if not all(
        isinstance(tag, str) and NAME_RE.fullmatch(tag)
        for tag in tags
    ):
        raise ValueError(f"{name}: tags contient une valeur invalide")

    for field in ("site", "role"):
        if not isinstance(raw[field], str) or not raw[field].strip():
            raise ValueError(f"{name}: {field} doit être renseigné")

    return Device(
        name=name,
        host=host,
        port=port,
        device_type=device_type,
        platform_family=family,
        site=raw["site"],
        role=raw["role"],
        enabled=enabled,
        credential_profile=profile,
        tags=tuple(tags),
    )


def load_inventory(path: str | Path) -> list[Device]:
    source = Path(path)

    with source.open("r", encoding="utf-8") as handle:
        raw_data = yaml.safe_load(handle)

    if not isinstance(raw_data, dict) or set(raw_data) != {"devices"}:
        raise ValueError(
            "La racine de l'inventaire doit contenir uniquement 'devices'"
        )

    records = raw_data["devices"]

    if not isinstance(records, list):
        raise ValueError("'devices' doit être une liste")

    devices = [validate_device(item) for item in records]

    names = [device.name for device in devices]

    if len(names) != len(set(names)):
        raise ValueError("Les noms d'équipement doivent être uniques")

    return devices
```

## 6.3. Pourquoi ces validations sont importantes

### Refuser les champs inconnus

Sans ce contrôle, une faute de frappe peut être ignorée. Le script peut alors fonctionner avec une valeur par défaut que personne n'avait prévue.

### Refuser les noms dupliqués

Deux cibles qui portent le même nom peuvent provoquer des collisions dans les fichiers de sortie ou rendre un rapport ambigu.

### Restreindre les pilotes

Transmettre aveuglément un pilote arbitraire ne constitue pas une politique de sélection fiable. La liste autorisée doit correspondre aux plateformes du parc réellement géré.

### Refuser les secrets dans l'inventaire

L'inventaire ne contient pas de mot de passe. Si quelqu'un tente d'ajouter un champ `password`, la validation le détectera.

### Valider avant la connexion

Toutes ces opérations doivent précéder l'ouverture de sessions. Une erreur de données doit être détectée avant qu'une commande ne parte vers un équipement.

## 6.4. Sélection explicite du périmètre

`src/netops/inventory.py` :

```python
def select_devices(
    devices: list[Device],
    *,
    site: str,
    role: str | None = None,
    required_tags: set[str] | None = None,
) -> list[Device]:
    selected = []

    for device in devices:
        if not device.enabled:
            continue

        if device.site != site:
            continue

        if role is not None and device.role != role:
            continue

        if required_tags and not required_tags.issubset(set(device.tags)):
            continue

        selected.append(device)

    return selected
```

Ne traitez pas l'intégralité de l'inventaire par défaut. Le programme doit recevoir un périmètre explicite, par exemple le site, le rôle et les étiquettes requises.

Pour les changements sensibles, ajoutez un contrôle d'autorisation externe à l'inventaire : identifiant de changement, approbation, environnement et liste de cibles autorisées.

---

# 7. SECRETS, COMPTES DE SERVICE ET SÉCURITÉ SSH

## 7.1. Inventaire et secrets sont deux choses différentes

L'inventaire contient les métadonnées des appareils. Les secrets doivent être obtenus par un mécanisme distinct.

Approches possibles :

- saisie interactive avec `getpass` pour un essai manuel ;
- variables d'environnement fournies par un système d'exécution protégé ;
- coffre de secrets d'entreprise ;
- clés SSH gérées par une politique de sécurité ;
- identités temporaires ou comptes dédiés selon les capacités de l'infrastructure.

Les variables d'environnement ne sont pas automatiquement un coffre de secrets. Il faut également contrôler l'accès au processus, à la machine d'exécution, aux logs, aux dumps et aux paramètres de pipeline.

## 7.2. Créer le module de gestion des identifiants

`src/netops/credentials.py` :

```python
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str | None = None
    secret: str | None = None
    key_file: str | None = None


PROFILE_ENV = {
    "netops_ro": ("NETOPS_RO_USERNAME", "NETOPS_RO_PASSWORD"),
    "netops_change": (
        "NETOPS_CHANGE_USERNAME",
        "NETOPS_CHANGE_PASSWORD",
    ),
}


def credentials_for(profile: str) -> Credentials:
    if profile not in PROFILE_ENV:
        raise ValueError("Profil d'identifiants non autorisé")

    username_var, password_var = PROFILE_ENV[profile]

    username = os.environ.get(username_var)
    password = os.environ.get(password_var)

    if not username or not password:
        raise RuntimeError(
            f"Identifiants absents pour le profil {profile}"
        )

    return Credentials(
        username=username,
        password=password,
    )
```

Cet exemple convient à un laboratoire. En production, remplacez le résolveur par une intégration au système de gestion des secrets de votre organisation.

Ne faites jamais de l'inventaire YAML un dépôt de mots de passe, et n'affichez pas les identifiants en cas d'erreur.

## 7.3. Séparer les privilèges

Prévoyez des profils distincts.

**Compte de lecture seule :**
- collecte de versions ;
- inventaire des interfaces ;
- diagnostic ;
- état de référence ;
- vérifications postérieures lorsqu'elles ne nécessitent pas de privilèges élevés.

**Compte de changement :**
- utilisé seulement pour les tâches qui en ont besoin ;
- associé à un périmètre et une approbation ;
- soumis aux restrictions disponibles sur la plateforme ;
- séparé du chemin de collecte ordinaire.

Un programme de collecte ne devrait pas avoir besoin des privilèges nécessaires à une modification.

## 7.4. La confiance SSH

Une connexion chiffrée ne suffit pas si le client ne vérifie pas qu'il parle au bon serveur. La vérification de la clé d'hôte participe à la protection contre l'usurpation de l'identité de l'équipement.

Les paramètres Netmiko associés à la confiance SSH dépendent de la configuration utilisée :

```python
ssh_options = {
    "ssh_strict": True,
    "system_host_keys": True,
}
```

Cette configuration s'appuie sur les clés d'hôtes connues au niveau système. Dans un parc géré, utilisez un mécanisme de distribution et de mise à jour des clés vérifié et documenté.

Les options `alt_host_keys` et `alt_key_file` peuvent être pertinentes selon votre environnement. Consultez la documentation de la version installée pour déterminer le fichier et le comportement exacts.

Ne désactivez pas les contrôles de clés d'hôte uniquement parce qu'une connexion échoue. Une clé changée doit être vérifiée via une source de confiance avant de mettre à jour le fichier de confiance.

---

# 8. GESTION ROBUSTE DES CONNEXIONS

## 8.1. Centraliser les paramètres Netmiko

`src/netops/connections.py` :

```python
from netmiko import ConnectHandler
from netmiko.base_connection import BaseConnection

from .inventory import Device
from .credentials import Credentials


def open_connection(
    device: Device,
    credentials: Credentials,
) -> BaseConnection:
    params = {
        "device_type": device.device_type,
        "host": device.host,
        "port": device.port,
        "username": credentials.username,
        "password": credentials.password,
        "secret": credentials.secret or "",
        "conn_timeout": 10,
        "banner_timeout": 15,
        "auth_timeout": 15,
        "blocking_timeout": 20,
        "session_timeout": 45,
        "fast_cli": False,
        "ssh_strict": True,
        "system_host_keys": True,
    }

    if credentials.key_file:
        params["use_keys"] = True
        params["key_file"] = credentials.key_file

    return ConnectHandler(**params)
```

Ces valeurs sont des paramètres de départ pour un laboratoire, pas des constantes adaptées à tous les réseaux. Mesurez les comportements sur vos équipements, définissez des profils par environnement et utilisez la documentation de la version Netmiko installée.

## 8.2. Comprendre les différents délais

Il ne faut pas confondre :

- `conn_timeout` : délai lié à l'établissement de la connexion ;
- `banner_timeout` : délai d'attente de la bannière SSH ;
- `auth_timeout` : délai associé à l'authentification ;
- `blocking_timeout` : paramètre de lecture bloquante au niveau de la session ;
- `read_timeout` : délai de lecture utilisé par des méthodes telles que `send_command()` ;
- `session_timeout` : paramètre de gestion de session utilisé notamment pour les mécanismes de verrouillage et de partage.

La version de Netmiko et la méthode employée déterminent le comportement exact de certains paramètres. Consultez la documentation officielle avant de construire une politique de délais.

Un délai trop court provoque des échecs intermittents. Un délai trop long peut immobiliser des ressources et ralentir la détection d'une panne. Un délai désactivé ou sans borne explicite peut être encore plus difficile à gérer.

Le but est d'associer chaque opération à un budget de temps raisonnable et testé.

## 8.3. Toujours fermer la connexion

Le nettoyage doit être garanti même lorsque l'opération échoue.

```python
connection = None

try:
    connection = open_connection(device, credentials)

    output = connection.send_command(
        "show version",
        read_timeout=30,
    )

finally:
    if connection is not None:
        connection.disconnect()
```

Le bloc `finally` s'exécute même lorsque l'opération déclenche une exception.

Dans une application plus complète, cette responsabilité peut être encapsulée dans un gestionnaire de contexte ou un helper. L'important est d'éviter les connexions abandonnées.

## 8.4. `send_command()` et `send_command_timing()`

`send_command()` convient aux commandes pour lesquelles Netmiko peut identifier la fin de la réponse, généralement au moyen de l'invite ou d'un motif attendu.

`send_command_timing()` se base davantage sur les périodes d'inactivité et peut être adapté à certains dialogues particuliers.

Une interaction interactive doit être conçue selon des états attendus, des délais bornés et des réponses connues. Il ne faut pas accumuler des `sleep()` arbitraires en espérant que l'équipement réponde à la vitesse prévue.

Exemple de commande longue :

```python
output = connection.send_command(
    "show tech-support",
    read_timeout=180,
    strip_prompt=True,
    strip_command=True,
)
```

Cette commande peut générer une charge importante et produire des informations sensibles. Elle doit faire l'objet d'une décision opérationnelle particulière, et non être lancée simultanément sur tout un parc sans analyse.

## 8.5. Un prompt ne prouve pas la santé du service

`find_prompt()` aide à identifier une invite reconnue. Cela ne prouve pas que la table de routage contient la route attendue, que les interfaces sont dans le bon état ou que le service fonctionne.

Les vérifications de transport et les validations métier sont deux niveaux distincts.

---

# 9. COLLECTE DES DONNÉES ET COMMANDES AUTORISÉES

## 9.1. Définir un catalogue explicite

Évitez de construire des commandes à partir de valeurs libres saisies par un utilisateur. Utilisez un catalogue d'opérations connu, versionné et testé.

`src/netops/operations.py` :

```python
from dataclasses import dataclass
from typing import Callable

from netmiko.base_connection import BaseConnection


@dataclass(frozen=True)
class CommandSpec:
    name: str
    command: str
    read_timeout: float
    validator: Callable[[str], bool]


def nonempty_output(output: str) -> bool:
    return bool(output.strip())


READ_ONLY_COMMANDS = {
    "ios": {
        "version": CommandSpec(
            "version",
            "show version",
            30,
            nonempty_output,
        ),
        "interfaces": CommandSpec(
            "interfaces",
            "show ip interface brief",
            30,
            nonempty_output,
        ),
        "routes": CommandSpec(
            "routes",
            "show ip route",
            45,
            nonempty_output,
        ),
    },
    "nxos": {
        "version": CommandSpec(
            "version",
            "show version",
            30,
            nonempty_output,
        ),
        "interfaces": CommandSpec(
            "interfaces",
            "show interface brief",
            30,
            nonempty_output,
        ),
    },
    "eos": {
        "version": CommandSpec(
            "version",
            "show version",
            30,
            nonempty_output,
        ),
        "interfaces": CommandSpec(
            "interfaces",
            "show ip interface brief",
            30,
            nonempty_output,
        ),
    },
    "junos": {
        "version": CommandSpec(
            "version",
            "show version",
            30,
            nonempty_output,
        ),
        "interfaces": CommandSpec(
            "interfaces",
            "show interfaces terse",
            45,
            nonempty_output,
        ),
    },
}


def collect_one(
    connection: BaseConnection,
    family: str,
    operation_name: str,
) -> dict[str, str]:
    try:
        spec = READ_ONLY_COMMANDS[family][operation_name]
    except KeyError as exc:
        raise ValueError(
            "Opération de collecte non autorisée pour cette plateforme"
        ) from exc

    output = connection.send_command(
        spec.command,
        read_timeout=spec.read_timeout,
    )

    if not spec.validator(output):
        raise RuntimeError(
            f"Validation de sortie échouée pour {spec.name}"
        )

    return {
        "operation": spec.name,
        "output": output,
    }
```

Les commandes données ici sont des exemples de profils par famille. Vérifiez leur disponibilité sur les plateformes et versions que vous utilisez réellement.

Une même famille peut contenir des différences de syntaxe ou de sortie selon le modèle et la version du système. En environnement de production, les profils doivent correspondre à une matrice de compatibilité testée.

## 9.2. Une sortie non vide n'est pas forcément une sortie valide

La validation `nonempty_output()` est un garde-fou minimal. Elle ne suffit pas pour des opérations critiques.

Une commande peut renvoyer du texte tout en signalant un rejet. Certaines plateformes incluent des avertissements ou des erreurs textuelles sans déclencher d'exception Python.

Exemple :

```python
CLI_ERROR_MARKERS = (
    "% Invalid input",
    "% Incomplete command",
    "% Ambiguous command",
    "syntax error",
)


def reject_known_cli_errors(output: str) -> None:
    for marker in CLI_ERROR_MARKERS:
        if marker.lower() in output.lower():
            raise RuntimeError(
                f"La CLI signale un rejet : {marker}"
            )
```

Cette liste ne constitue pas un détecteur universel. Les marqueurs doivent être maintenus par plateforme et être accompagnés de tests. Une règle trop générale peut produire des faux positifs ou manquer une erreur.

## 9.3. Contrat des données collectées

Pour chaque collecte, conservez une enveloppe stable :

```json
{
  "schema_version": 1,
  "run_id": "RUN-EXAMPLE-001",
  "device": "edge-r1",
  "operation": "interfaces",
  "status": "success",
  "duration_ms": 842,
  "data_format": "text",
  "payload": "..."
}
```

Les valeurs sont illustratives.

Indiquez clairement si `payload` contient du texte brut ou une structure normalisée. Ne laissez pas le consommateur supposer qu'une sortie CLI est déjà un objet métier valide.

---

# 10. PARSING ET NORMALISATION DES SORTIES

Les sorties CLI peuvent changer selon la version logicielle, la longueur des noms, la langue, les paramètres de terminal ou les caractéristiques de l'équipement.

Un texte brut est utile à l'analyse, mais il n'est pas toujours adapté à un traitement automatisé.

## 10.1. Trois méthodes courantes

### Méthode A : expressions régulières ciblées

Appropriées lorsque le format est simple, stable et bien couvert par des tests.

### Méthode B : TextFSM et NTC Templates

Ces outils peuvent transformer certaines sorties CLI en données structurées lorsqu'un template compatible existe.

### Méthode C : API structurée

Lorsqu'une API ou un modèle de données supporté permet d'obtenir directement l'état attendu, cette méthode peut être préférable à l'analyse d'un texte CLI.

## 10.2. Exemple TextFSM

Lorsque le template correspondant est disponible et validé :

```python
result = connection.send_command(
    "show ip interface brief",
    use_textfsm=True,
    read_timeout=30,
)
```

Le parsing ne sera pas disponible pour toutes les commandes et toutes les plateformes. Vérifiez explicitement le type retourné et le schéma des données.

Référence NTC Templates :

https://github.com/networktocode/ntc-templates

## 10.3. Ne pas transformer silencieusement une erreur de parsing en succès

Si le programme attend une liste de dictionnaires et reçoit une chaîne de texte inattendue, il ne doit pas continuer comme si les données étaient correctes.

La validation devrait contrôler :

- le type retourné ;
- la présence des champs obligatoires ;
- la valeur des champs critiques ;
- la cohérence des données ;
- le nombre d'éléments lorsque ce nombre est connu ;
- les cas où la sortie est vide ou partielle.

Un format incorrect doit produire un statut intelligible, par exemple `validation_failed`.

## 10.4. Séparer les données de la présentation

La logique métier ne doit pas dépendre directement d'un format de console. Une fonction peut normaliser la sortie en objets Python, puis une autre fonction produit un rapport JSON ou un tableau lisible.

Cette séparation simplifie les tests et évite de mélanger extraction des données et présentation.

---

# 11. EXÉCUTION CONCURRENTE CONTRÔLÉE

## 11.1. Pourquoi la concurrence doit être limitée

Exécuter plusieurs connexions en parallèle peut réduire le temps global, mais augmente aussi la pression sur :

- les équipements ;
- les serveurs AAA ;
- le réseau de gestion ;
- le processus Python ;
- les systèmes centralisés de logs ;
- les ressources SSH disponibles sur chaque appareil.

Une vague simultanée de reconnexions peut aggraver un incident en cours. Le nombre de workers doit donc être une décision opérationnelle, pas un nombre arbitraire.

## 11.2. Une session indépendante par worker

Ne partagez pas un objet de connexion Netmiko entre plusieurs workers qui exécutent leurs commandes simultanément.

La tâche d'une cible doit :

1. recevoir un équipement et un profil d'identifiants ;
2. ouvrir sa session ;
3. exécuter les opérations définies ;
4. créer un résultat ;
5. fermer sa session ;
6. renvoyer le résultat au coordinateur.

## 11.3. Modèle de résultat commun

`src/netops/results.py` :

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class DeviceResult:
    device: str
    status: str
    started_at: str
    duration_ms: int
    data: dict[str, Any]
    error_type: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
```

Ce modèle sépare le statut opérationnel des données retournées. Il permet de représenter un succès, un échec de connexion ou une validation incorrecte avec une structure commune.

Il ne doit pas contenir de mot de passe, de clé privée ou d'objet Netmiko.

## 11.4. Worker de collecte

`src/netops/runner.py` :

```python
from __future__ import annotations

from time import monotonic

from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from .connections import open_connection
from .inventory import Device
from .operations import collect_one
from .results import DeviceResult, utc_now_iso


def run_readonly_job(
    device: Device,
    credentials,
) -> DeviceResult:
    started_iso = utc_now_iso()
    start = monotonic()
    connection = None

    try:
        connection = open_connection(device, credentials)

        data = {
            "version": collect_one(
                connection,
                device.platform_family,
                "version",
            ),
        }

        return DeviceResult(
            device=device.name,
            status="success",
            started_at=started_iso,
            duration_ms=int((monotonic() - start) * 1000),
            data=data,
        )

    except NetmikoAuthenticationException:
        return DeviceResult(
            device=device.name,
            status="authentication_failed",
            started_at=started_iso,
            duration_ms=int((monotonic() - start) * 1000),
            data={},
            error_type="authentication",
            error_message=(
                "Authentification refusée ; vérifier le profil et les droits"
            ),
        )

    except NetmikoTimeoutException:
        return DeviceResult(
            device=device.name,
            status="connection_timeout",
            started_at=started_iso,
            duration_ms=int((monotonic() - start) * 1000),
            data={},
            error_type="timeout",
            error_message="Connexion Netmiko expirée",
        )

    except Exception as exc:
        return DeviceResult(
            device=device.name,
            status="failed",
            started_at=started_iso,
            duration_ms=int((monotonic() - start) * 1000),
            data={},
            error_type=type(exc).__name__,
            error_message=(
                "Échec de l'opération ; consulter le journal protégé"
            ),
        )

    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception:
                # En production, enregistrer l'erreur de fermeture
                # séparément sans masquer le résultat principal.
                pass
```

Vérifiez les classes d'exception réellement émises par la version installée de Netmiko et Paramiko. Les délais de lecture, erreurs de pilote et problèmes SSH peuvent nécessiter une classification plus détaillée.

Le gestionnaire générique de l'exemple constitue un dernier filet de sécurité. Il ne remplace pas la classification précise des erreurs attendues dans votre environnement.

## 11.5. Exécuteur concurrent

Ajoutez à `runner.py` :

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_batch(
    devices: list[Device],
    credentials_by_profile: dict,
    max_workers: int = 5,
) -> list[DeviceResult]:
    if max_workers < 1:
        raise ValueError(
            "max_workers doit être supérieur ou égal à 1"
        )

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        for device in devices:
            credentials = credentials_by_profile[
                device.credential_profile
            ]

            future = executor.submit(
                run_readonly_job,
                device,
                credentials,
            )

            futures[future] = device

        for future in as_completed(futures):
            device = futures[future]

            try:
                results.append(future.result())

            except Exception:
                results.append(
                    DeviceResult(
                        device=device.name,
                        status="worker_failed",
                        started_at=utc_now_iso(),
                        duration_ms=0,
                        data={},
                        error_type="UnhandledWorkerError",
                        error_message=(
                            "Échec non géré dans le worker"
                        ),
                    )
                )

    return sorted(results, key=lambda result: result.device)
```

Ici, `max_workers=5` est une valeur d'exemple. Elle doit être configurable et ajustée selon les caractéristiques du parc.

## 11.6. Comprendre le résultat partiel

Si 47 équipements sur 50 répondent, le programme ne doit ni afficher un succès total sans réserve ni perdre l'ensemble des résultats.

Le rapport doit indiquer :

- le nombre total de cibles prévues ;
- le nombre de cibles traitées ;
- le nombre de succès ;
- le nombre d'échecs ;
- le nombre de cibles ignorées ;
- les raisons des échecs ;
- les cibles dont l'état est incertain ;
- la durée du lot.

Un résultat partiel est souvent acceptable pour une collecte indépendante. Pour un changement distribué, il peut au contraire signaler une situation incohérente qui exige un arrêt immédiat.

---

# 12. GESTION DES ERREURS ET DES REPRISES

## 12.1. Une taxonomie opérationnelle

Utilisez des statuts stables. Évitez de mettre toute l'information dans une phrase libre qui rendrait le rapport difficile à agréger.

| Statut | Signification | Action |
|---|---|---|
| `success` | Opération et validation réussies | Conserver la preuve |
| `skipped` | Cible volontairement exclue | Consigner la raison |
| `inventory_invalid` | Données invalides avant connexion | Corriger l'inventaire |
| `dns_failed` | Résolution du nom échouée | Vérifier DNS et nom |
| `connection_timeout` | Connexion non établie à temps | Vérifier le réseau de gestion |
| `authentication_failed` | Authentification refusée | Vérifier compte et méthode |
| `host_key_rejected` | Clé d'hôte inattendue | Vérifier l'identité réelle |
| `read_timeout` | Réponse non reçue dans le délai | Diagnostiquer la commande |
| `cli_rejected` | Rejet explicitement détecté | Corriger commande ou profil |
| `validation_failed` | État non conforme à l'objectif | Arrêter ou récupérer |
| `rollback_required` | Une récupération est requise | Appliquer le runbook approuvé |
| `rollback_failed` | Récupération non confirmée | Escalade opérationnelle |

## 12.2. Pourquoi il ne faut pas relancer aveuglément une commande

Considérons un changement de configuration.

Le programme envoie une commande. L'équipement la reçoit et l'applique, mais la réponse n'arrive jamais parce que la connexion tombe au mauvais moment.

Le programme voit un timeout.

Cela ne signifie pas que la commande a échoué. Elle a peut-être réussi avant la rupture de connexion.

Une nouvelle tentative immédiate peut donc :

- répéter une action non idempotente ;
- aggraver un changement partiellement appliqué ;
- produire un résultat différent de celui attendu ;
- rendre l'état final ambigu.

En cas de timeout après une modification, il faut d'abord reconnecter si cela est autorisé, relire l'état pertinent et déterminer si le changement a été appliqué.

## 12.3. Reprises bornées pour les opérations sûres

Pour une opération de lecture, une politique de reprise peut être adaptée à certains échecs transitoires.

Elle doit inclure :

- une liste restreinte d'erreurs réessayables ;
- un nombre maximal de tentatives ;
- un délai croissant entre tentatives ;
- éventuellement un jitter pour éviter que tous les workers réessaient au même instant ;
- une trace du numéro de tentative ;
- une limite globale de pression sur le parc.

La politique de reprise doit être plus restrictive pour les modifications de configuration.

## 12.4. Séparer les messages utilisateur des journaux protégés

Le rapport destiné aux opérateurs peut contenir :

- la cible ;
- le statut ;
- la catégorie d'erreur ;
- la durée ;
- une explication assainie ;
- le lien vers le diagnostic protégé.

Le journal technique protégé peut contenir davantage de contexte. Il doit néanmoins exclure les secrets et respecter la politique de gestion des données sensibles.

Ne supposez pas qu'un journal de session est inoffensif. Il peut révéler la configuration complète, la topologie et les détails d'accès.

---

# 13. GESTION PROFESSIONNELLE DES CHANGEMENTS DE CONFIGURATION

La configuration est la zone où une automatisation imprudente peut transformer une erreur en incident.

La règle centrale est la suivante :

**Préparer, sauvegarder, appliquer, vérifier, puis clôturer.**

## 13.1. Cycle de changement

1. charger le périmètre approuvé ;
2. valider l'inventaire ;
3. vérifier la plateforme et les préconditions ;
4. collecter l'état initial ;
5. créer une sauvegarde selon la méthode supportée ;
6. produire un plan de changement ;
7. afficher le plan à l'opérateur ;
8. obtenir l'approbation selon le workflow retenu ;
9. appliquer sur un petit lot pilote ;
10. inspecter la réponse CLI ;
11. relire l'état après changement ;
12. exécuter les contrôles de service ;
13. comparer état attendu et état obtenu ;
14. arrêter le déploiement si les critères d'échec sont atteints ;
15. déclencher la récupération prévue si nécessaire ;
16. produire le rapport final.

## 13.2. Idempotence

Une opération est idempotente lorsque sa répétition ne modifie pas davantage l'état final après que l'objectif a été atteint, sous les hypothèses définies.

La propriété dépend de l'opération et de la plateforme.

L'envoi répété de :

```python
connection.send_config_set([
    "interface GigabitEthernet1/0/10",
    "description UPLINK-TO-CORE",
])
```

peut être répétable sur certaines plateformes. Mais cela ne prouve ni que l'interface existe, ni que la commande est valide sur la version logicielle, ni que l'état final est correct.

Une opération experte doit lire l'état courant, le comparer à l'état désiré, construire les seules commandes nécessaires, appliquer le plan approuvé puis relire l'état.

## 13.3. Demande métier de changement

Exemple de `config/CHG-2026-1042.yaml` :

```yaml
change_id: CHG-2026-1042
environment: lab
site: lab-douala

target_devices:
  - edge-r1

change_type: interface_description

parameters:
  interface: GigabitEthernet1/0/10
  description: UPLINK-TO-CORE

approval_required: true
```

Ce document décrit l'intention métier ; il ne doit pas contenir une commande CLI arbitraire à exécuter sans validation.

Le moteur doit vérifier :

- l'existence et le format de l'ID ;
- le périmètre ;
- l'état d'approbation ;
- le type de changement autorisé ;
- les paramètres requis ;
- l'absence de paramètres inattendus ;
- la compatibilité plateforme ;
- les préconditions d'exécution.

## 13.4. Valider les paramètres avant de générer des commandes

Exemple limité à un laboratoire Cisco IOS. Adaptez et testez la grammaire d'interface pour les plateformes réelles.

`src/netops/changes.py` :

```python
import re
from dataclasses import dataclass


INTERFACE_RE = re.compile(
    r"^(?:GigabitEthernet|TenGigabitEthernet|Ethernet|Port-channel)"
    r"[0-9]+(?:/[0-9]+){0,3}$"
)


@dataclass(frozen=True)
class InterfaceDescriptionChange:
    interface: str
    description: str


def validate_interface_change(
    raw: dict,
) -> InterfaceDescriptionChange:
    allowed = {"interface", "description"}

    if set(raw) != allowed:
        raise ValueError("Paramètres de changement invalides")

    interface = raw["interface"]
    description = raw["description"]

    if (
        not isinstance(interface, str)
        or not INTERFACE_RE.fullmatch(interface)
    ):
        raise ValueError("Format d'interface non autorisé")

    if not isinstance(description, str):
        raise ValueError("La description doit être une chaîne")

    if not 1 <= len(description) <= 80:
        raise ValueError("Longueur de description hors limites")

    if any(ord(char) < 32 for char in description):
        raise ValueError("Caractère de contrôle interdit")

    return InterfaceDescriptionChange(
        interface=interface,
        description=description,
    )


def build_ios_description_plan(
    change: InterfaceDescriptionChange,
) -> list[str]:
    return [
        f"interface {change.interface}",
        f"description {change.description}",
    ]
```

Cette validation est pédagogique. La grammaire réelle varie selon les gammes et les versions. Elle doit être confirmée par des tests de compatibilité.

L'interdiction de caractères de contrôle et le refus de paramètres non prévus contribuent à empêcher que des données d'entrée deviennent des commandes imprévues.

## 13.5. Prévisualiser le plan

Avant toute application, produisez un affichage intelligible :

```text
Changement : CHG-2026-1042
Environnement : lab
Cible : edge-r1
Opération : description d'interface

Paramètres :
  Interface : GigabitEthernet1/0/10
  Description : UPLINK-TO-CORE

Contrôles :
  - interface présente dans l'état initial
  - sauvegarde initiale disponible
  - cible autorisée
  - approbation valide
  - validation postérieure prévue

Décision :
  APPROUVER / REFUSER
```

Dans un système réel, l'approbation doit être rattachée à une identité, à un horodatage, au périmètre exact et au contenu précis du plan. Un simple booléen modifiable dans un fichier local n'offre pas une piste d'audit suffisante.

## 13.6. Sauvegarde et état initial

Les méthodes de collecte de configuration dépendent du constructeur, du système et du mode de configuration.

Certaines plateformes permettent de lire la configuration active avec une commande CLI. D'autres disposent de modèles de configuration candidate, de mécanismes de commit et de fonctions de sauvegarde spécifiques.

Il ne faut pas supposer qu'une même commande de sauvegarde est valable partout.

Pour chaque famille, documentez :

- comment obtenir l'état initial ;
- comment confirmer que la capture est complète ;
- où stocker les artefacts ;
- comment comparer les états ;
- comment rendre la configuration persistante ;
- quelle stratégie de récupération est supportée ;
- quelles préconditions sont requises ;
- comment vérifier que la récupération a réussi.

Les configurations peuvent contenir des informations sensibles. Le stockage des sauvegardes doit être protégé.

## 13.7. État final et diff

Après modification, relisez l'état pertinent et comparez-le à l'état attendu.

Un diff textuel est utile mais ne suffit pas toujours à interpréter l'équivalence fonctionnelle. Deux configurations textuellement différentes peuvent avoir un comportement équivalent, tandis que des changements apparemment minimes peuvent modifier un chemin critique.

La validation métier doit définir ce qui constitue l'état conforme.

Pour une description d'interface, par exemple, la vérification peut être relativement simple. Pour un changement de routage, de sécurité ou de redondance, elle nécessite des contrôles adaptés à l'impact potentiel.

---

# 14. IDEMPOTENCE, VALIDATION ET STRATÉGIE DE RÉCUPÉRATION

## 14.1. Ne pas promettre un rollback universel

Il n'existe pas de méthode de retour arrière universelle applicable à tous les constructeurs et à toutes les plateformes.

Certains équipements prennent en charge un mode de configuration candidate ou un mécanisme de commit. D'autres appliquent les commandes immédiatement.

La stratégie de récupération doit être adaptée au système réellement utilisé.

## 14.2. Tester la récupération avant la production

Un test de récupération digne de ce nom comprend les étapes suivantes :

1. capturer l'état initial ;
2. vérifier que la sauvegarde est exploitable ;
3. appliquer un changement de laboratoire ;
4. provoquer volontairement une non-conformité contrôlée ;
5. détecter l'échec de validation ;
6. lancer la méthode de récupération documentée ;
7. relire l'état ;
8. vérifier indépendamment que l'état attendu a été rétabli ;
9. conserver les preuves de l'incident et de la récupération.

Une commande de rollback qui renvoie du texte ne suffit pas à prouver que la configuration précédente est rétablie.

Si la récupération échoue ou si l'état final reste incertain, le résultat doit être classé `rollback_failed` ou dans un statut équivalent clairement documenté. Une alerte opérationnelle doit être émise.

## 14.3. Deuxième schéma SVG animé : cycle de changement

Les animations sont limitées aux liaisons et aux contours des blocs. Elles ne reposent sur aucune bille mobile partagée avec les autres schémas.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 350" role="img" aria-labelledby="change-title change-desc" style="max-width:100%;height:auto">
  <title id="change-title">Cycle de changement contrôlé</title>
  <desc id="change-desc">Le changement passe par l'approbation, la capture de l'état initial, l'application, la validation et la clôture. L'échec mène à un arrêt et à une récupération encadrée.</desc>
  <defs>
    <marker id="change-arrow-head" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#5ec8a7"/></marker>
    <style>
      @keyframes change-flow { to { stroke-dashoffset:-32; } }
      @keyframes change-outline { 0%,100% { stroke-opacity:.7; } 50% { stroke-opacity:1; } }
      .change-line { fill:none; stroke:#5ec8a7; stroke-width:2.5; stroke-dasharray:8 8; marker-end:url(#change-arrow-head); animation:change-flow 2s linear infinite; }
      .change-node { fill:#17263a; stroke:#5ec8a7; stroke-width:1.8; animation:change-outline 2.8s ease-in-out infinite; }
      .change-label { fill:#f2f7ff; font:600 14px sans-serif; text-anchor:middle; }
      .change-sub { fill:#b1c1d9; font:12px sans-serif; text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="348" rx="14" fill="#0d1420" stroke="#293951"/>
  <text x="470" y="36" fill="#eaf2ff" text-anchor="middle" font-size="18" font-family="sans-serif">Un changement n'est clôturé qu'après validation</text>
  <rect class="change-node" x="22" y="90" width="160" height="78" rx="10"/>
  <text class="change-label" x="102" y="120">Approbation</text>
  <text class="change-sub" x="102" y="143">périmètre + plan</text>
  <rect class="change-node" x="209" y="90" width="160" height="78" rx="10"/>
  <text class="change-label" x="289" y="120">État initial</text>
  <text class="change-sub" x="289" y="143">capture + preuve</text>
  <rect class="change-node" x="396" y="90" width="160" height="78" rx="10"/>
  <text class="change-label" x="476" y="120">Application</text>
  <text class="change-sub" x="476" y="143">lot limité</text>
  <rect class="change-node" x="583" y="90" width="160" height="78" rx="10"/>
  <text class="change-label" x="663" y="120">Validation</text>
  <text class="change-sub" x="663" y="143">état + service</text>
  <rect x="770" y="90" width="148" height="78" rx="10" fill="#153128" stroke="#5ec8a7" stroke-width="2"/>
  <text class="change-label" x="844" y="120">Clôture</text>
  <text class="change-sub" x="844" y="143">rapport + preuves</text>
  <path class="change-line" d="M182 129 H204"/>
  <path class="change-line" d="M369 129 H391"/>
  <path class="change-line" d="M556 129 H578"/>
  <path class="change-line" d="M743 129 H765"/>
  <path d="M663 173 V220 H476 V173" fill="none" stroke="#eda85d" stroke-width="2.5" stroke-dasharray="5 7" style="animation:change-flow 2.4s linear infinite"/>
  <rect x="345" y="220" width="262" height="54" rx="10" fill="#302317" stroke="#eda85d" stroke-width="1.6"/>
  <text class="change-label" x="476" y="241">Validation en échec</text>
  <text class="change-sub" x="476" y="258">arrêt + récupération approuvée</text>
  <text x="470" y="316" fill="#c2cee0" text-anchor="middle" font-size="12" font-family="sans-serif">Les critères d'arrêt doivent être définis avant l'exécution.</text>
</svg>

---

# 15. OBSERVABILITÉ, JOURNAUX ET RAPPORTS

## 15.1. Les questions auxquelles les logs doivent répondre

Pour qu'une automatisation soit exploitable, le journal doit permettre de déterminer :

- quel lot était en cours ;
- quelle cible était traitée ;
- quelle opération logique a été exécutée ;
- à quelle heure elle a commencé ;
- combien de temps elle a duré ;
- quel statut a été obtenu ;
- quelle catégorie d'erreur est apparue ;
- quel identifiant de changement lui est associé.

Évitez de consigner automatiquement l'intégralité des échanges CLI. Les configurations et les journaux de session peuvent révéler des informations sensibles.

Les journaux de session Netmiko doivent être traités comme des artefacts sensibles. Le mécanisme de filtrage de secrets ne doit pas être considéré comme une garantie que toutes les informations confidentielles seront systématiquement masquées.

## 15.2. Logs JSON

Exemple de formateur :

```python
import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in (
            "run_id",
            "device",
            "operation",
            "status",
            "duration_ms",
        ):
            value = getattr(record, key, None)

            if value is not None:
                entry[key] = value

        return json.dumps(entry, ensure_ascii=False)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("netops")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)
    logger.propagate = False

    return logger
```

Utilisation :

```python
logger = configure_logging()

logger.info(
    "opération terminée",
    extra={
        "run_id": "RUN-2026-10-23-001",
        "device": "edge-r1",
        "operation": "collect_version",
        "status": "success",
        "duration_ms": 842,
    },
)
```

Le `run_id` doit rester stable à travers l'ensemble des workers d'un lot.

Pour un déploiement réel, prévoyez également :

- rotation et archivage ;
- droits d'accès ;
- synchronisation de l'heure ;
- filtrage des données confidentielles ;
- transmission vers un agrégateur de logs ;
- durée de conservation ;
- corrélation avec les tickets et approbations.

## 15.3. Générer un rapport JSON

`src/netops/reporting.py` :

```python
import json
from pathlib import Path


def write_report(results, output_path: str | Path) -> None:
    records = [result.to_dict() for result in results]

    summary = {
        "total": len(records),
        "success": sum(
            item["status"] == "success"
            for item in records
        ),
        "skipped": sum(
            item["status"] == "skipped"
            for item in records
        ),
        "failed": sum(
            item["status"] not in {"success", "skipped"}
            for item in records
        ),
    }

    report = {
        "schema_version": 1,
        "summary": summary,
        "results": records,
    }

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
```

Un JSON de rapport ne constitue pas automatiquement une piste d'audit inviolable. Pour les opérations critiques, associez les preuves au code exécuté, au plan, à l'approbation et au système de stockage utilisé.

## 15.4. Éviter les faux succès globaux

Un taux de réussite de 98 % ne suffit pas à comprendre la situation. Les deux échecs restants peuvent concerner les équipements les plus critiques du parc.

Le rapport doit afficher les nombres absolus et les détails des échecs.

Il doit également préciser le dénominateur : le total prévu, le total tenté et le total réellement validé ne sont pas nécessairement identiques.

---

# 16. TESTS UNITAIRES ET INTÉGRATION CONTINUE

Un projet d'automatisation ne peut pas dépendre exclusivement de tests sur des routeurs physiques.

La validation des entrées, la construction d'un plan, la sélection des équipements, la classification des résultats et la génération des rapports peuvent être testées sans connexion réseau.

Les tests d'intégration avec les vraies plateformes restent indispensables, mais ils viennent compléter les tests unitaires.

## 16.1. Installer et lancer les tests

```bash
python -m pytest -q
```

## 16.2. Tester l'inventaire

`tests/test_inventory.py` :

```python
import pytest

from netops.inventory import validate_device


VALID_DEVICE = {
    "name": "edge-r1",
    "host": "192.0.2.11",
    "port": 22,
    "device_type": "cisco_ios",
    "platform_family": "ios",
    "site": "lab-douala",
    "role": "edge",
    "enabled": True,
    "credential_profile": "netops_ro",
    "tags": ["lab", "edge"],
}


def test_valid_device_is_loaded():
    device = validate_device(VALID_DEVICE)

    assert device.name == "edge-r1"
    assert device.port == 22
    assert device.enabled is True


def test_invalid_port_is_rejected():
    bad = {
        **VALID_DEVICE,
        "port": 70000,
    }

    with pytest.raises(ValueError):
        validate_device(bad)


def test_unknown_device_type_is_rejected():
    bad = {
        **VALID_DEVICE,
        "device_type": "unknown_platform",
    }

    with pytest.raises(ValueError):
        validate_device(bad)


def test_unexpected_password_field_is_rejected():
    bad = {
        **VALID_DEVICE,
        "password": "should-not-be-here",
    }

    with pytest.raises(ValueError):
        validate_device(bad)


def test_boolean_port_is_rejected():
    bad = {
        **VALID_DEVICE,
        "port": True,
    }

    with pytest.raises(ValueError):
        validate_device(bad)
```

Le dernier test couvre une subtilité de Python : `bool` est un sous-type de `int`. Une validation de port doit donc refuser explicitement les booléens.

## 16.3. Tester le plan de changement

`tests/test_changes.py` :

```python
import pytest

from netops.changes import (
    build_ios_description_plan,
    validate_interface_change,
)


def test_build_description_plan():
    change = validate_interface_change({
        "interface": "GigabitEthernet1/0/10",
        "description": "UPLINK-TO-CORE",
    })

    assert build_ios_description_plan(change) == [
        "interface GigabitEthernet1/0/10",
        "description UPLINK-TO-CORE",
    ]


def test_control_characters_are_rejected():
    with pytest.raises(ValueError):
        validate_interface_change({
            "interface": "GigabitEthernet1/0/10",
            "description": "uplink\nreload",
        })


def test_unknown_parameters_are_rejected():
    with pytest.raises(ValueError):
        validate_interface_change({
            "interface": "GigabitEthernet1/0/10",
            "description": "UPLINK",
            "command": "free-form command",
        })
```

## 16.4. Simuler une connexion

`unittest.mock` permet de remplacer une connexion réelle par un objet simulé.

```python
from unittest.mock import MagicMock

from netops.operations import collect_one


def test_collect_one_uses_expected_command():
    fake_connection = MagicMock()
    fake_connection.send_command.return_value = "Version 17.x"

    result = collect_one(
        fake_connection,
        "ios",
        "version",
    )

    fake_connection.send_command.assert_called_once_with(
        "show version",
        read_timeout=30,
    )

    assert result["operation"] == "version"
```

Ce test valide le contrat de la fonction sans ouvrir de session SSH.

Ajoutez ensuite des tests pour les sorties vides, les marqueurs de rejet, les exceptions et les erreurs de parsing.

## 16.5. Tester la fermeture des connexions

Le test d'un worker doit vérifier qu'une connexion est fermée aussi bien après un succès qu'après une exception.

Une logique de test appropriée peut simuler :

- une connexion qui retourne une sortie valide ;
- une connexion dont la commande déclenche une exception ;
- une erreur de fermeture ;
- un timeout ;
- un rejet de commande.

La fermeture doit se trouver dans le chemin de nettoyage garanti, généralement avec `finally`.

## 16.6. Vérifications automatiques du code

```bash
python -m ruff check src tests
python -m pytest -q
python -m pip check
```

Les outils peuvent également inclure un vérificateur de secrets, un audit des dépendances, une analyse statique et une vérification de types.

Attention : un code qui passe tous les linters ne prouve pas qu'il est sûr pour le réseau. Ces contrôles détectent certaines classes de défauts, pas l'ensemble des conséquences opérationnelles.

## 16.7. Pipeline conseillé

1. vérifier le style et la syntaxe ;
2. exécuter les tests unitaires ;
3. vérifier les dépendances ;
4. rechercher les secrets accidentellement ajoutés ;
5. valider l'inventaire ;
6. produire un plan sans l'appliquer ;
7. obtenir l'approbation requise ;
8. exécuter sur un équipement pilote ;
9. contrôler l'état postérieur ;
10. autoriser progressivement le reste du périmètre ;
11. produire le rapport et archiver les preuves.

La réussite du pipeline de code ne doit pas entraîner automatiquement un changement réseau si l'approbation opérationnelle n'a pas été donnée.

---

# 17. INDUSTRIALISATION ET GOUVERNANCE

## 17.1. Identifier chaque exécution

Chaque lot devrait posséder un manifeste :

- ID du lot ;
- identité de l'exécutant ou du processus ;
- environnement ;
- ID du ticket ou du changement ;
- version du code ;
- version des dépendances ;
- digest ou version du plan ;
- liste des cibles ;
- fenêtre d'exécution ;
- statut final ;
- liens vers les preuves.

Sans ces informations, il est difficile de répondre à la question :

« Quel code a modifié cet équipement, avec quelle autorisation, et comment le résultat a-t-il été vérifié ? »

## 17.2. Déployer progressivement

Les lots de changement doivent être conçus selon la criticité et la topologie, pas seulement selon le nombre d'équipements.

Un déploiement gradué peut comporter :

1. un test en laboratoire ;
2. une cible représentative en préproduction ;
3. un équipement pilote en production ;
4. un groupe limité ;
5. le reste du périmètre si les contrôles restent satisfaisants.

Le nombre exact de cibles par étape dépend du réseau. Dix pour cent du parc peuvent être un lot raisonnable dans un cas et inclure une proportion critique du cœur de réseau dans un autre.

## 17.3. Définir des critères d'arrêt

Le moteur de changement doit savoir quand suspendre le lot.

Exemples :

- la sauvegarde initiale n'a pas été vérifiée ;
- l'équipement n'est pas celui qui était attendu ;
- le changement n'est pas approuvé ;
- l'état initial diffère de façon inattendue ;
- un contrôle postérieur échoue ;
- le taux d'échec dépasse le seuil prévu ;
- la fenêtre de maintenance est close ;
- un contrôle de santé réseau devient négatif.

L'arrêt doit distinguer :

- les équipements non encore traités ;
- les équipements où l'application a été tentée ;
- les équipements validés ;
- les équipements dont l'état est incertain ;
- les équipements nécessitant une récupération.

## 17.4. Le comportement de reprise doit être documenté

Pour chaque opération, écrivez explicitement si elle peut être retentée.

Exemples :

- une collecte de version peut souvent être retentée après un échec transitoire ;
- la génération d'un rapport peut généralement être relancée ;
- une commande de configuration non vérifiée ne doit pas être rejouée aveuglément après un timeout ;
- une opération de redémarrage doit faire l'objet d'un contrôle spécifique et d'une validation préalable.

La reprise fait partie du contrat de l'opération. Ce n'est pas une simple boucle ajoutée après coup.

---

# 18. LABORATOIRES PROGRESSIFS

Chaque laboratoire réutilise les mêmes modules et les mêmes conventions. Ne repartez pas de fichiers indépendants à chaque exercice : complétez progressivement le même projet.

## LABORATOIRE 1 — Audit de l'inventaire

**Objectif :** valider le périmètre avant la première connexion.

Étapes :

1. créer un inventaire YAML contenant deux équipements de laboratoire ;
2. implémenter `Device` et `validate_device()` ;
3. implémenter `load_inventory()` ;
4. tester les noms et ports invalides ;
5. introduire un `device_type` inconnu ;
6. ajouter un champ inattendu ;
7. vérifier que l'application échoue avant toute connexion.

**Critères d'acceptation :**

- noms uniques ;
- champs obligatoires contrôlés ;
- champs inconnus refusés ;
- aucun secret dans l'inventaire ;
- aucune connexion réseau pendant la validation ;
- erreurs compréhensibles.

**Question :** une adresse IP valide suffit-elle à autoriser un équipement à être automatisé ? Expliquez pourquoi la sélection doit aussi s'appuyer sur une politique de périmètre.

## LABORATOIRE 2 — Première collecte architecturée

**Objectif :** reprendre `ConnectHandler` du niveau Débutant en l'intégrant aux modules du projet.

Étapes :

1. charger l'inventaire validé ;
2. sélectionner une seule cible de laboratoire ;
3. charger le profil d'identifiants ;
4. ouvrir une connexion avec des délais explicites ;
5. exécuter `show version` par le catalogue d'opérations ;
6. vérifier la sortie ;
7. fermer la session ;
8. produire un résultat normalisé.

Tester aussi :

- mot de passe incorrect ;
- hôte inaccessible ;
- clé SSH inconnue ;
- délai dépassé ;
- commande non supportée ;
- sortie vide.

**Critère d'acceptation :** chaque scénario produit un statut cohérent et aucune information secrète n'apparaît dans le rapport.

## LABORATOIRE 3 — Collecte concurrente

**Objectif :** traiter plusieurs équipements tout en gardant les sessions et les résultats indépendants.

Étapes :

1. réutiliser le worker du laboratoire 2 ;
2. ajouter un `ThreadPoolExecutor` ;
3. permettre le réglage de `max_workers` ;
4. commencer avec un seul worker ;
5. augmenter progressivement la concurrence ;
6. rendre volontairement une cible indisponible ;
7. vérifier que les autres résultats restent disponibles ;
8. trier les résultats et produire les statistiques.

**Critères d'acceptation :**

- une session indépendante par worker ;
- fermeture garantie ;
- échecs partiels visibles ;
- aucune réussite globale trompeuse ;
- concurrence configurable.

Mesurez les durées avec plusieurs nombres de workers. Observez aussi les échecs, les timeouts et la charge des équipements.

## LABORATOIRE 4 — Parsing et validation

**Objectif :** convertir une sortie CLI en données réellement exploitables.

Étapes :

1. choisir une commande en lecture seule ;
2. collecter plusieurs sorties représentatives ;
3. identifier un parseur adapté ou un mécanisme structuré ;
4. définir le schéma de sortie ;
5. écrire un test par cas important ;
6. introduire une sortie non vide mais invalide ;
7. vérifier que le programme renvoie `validation_failed`.

**Critère :** le programme doit détecter au moins un cas où la sortie contient du texte mais ne représente pas un résultat exploitable.

## LABORATOIRE 5 — Plan de changement sans application

**Objectif :** générer un plan à partir de paramètres contrôlés.

Étapes :

1. créer un modèle de changement ;
2. exiger un ID et un périmètre explicite ;
3. valider les paramètres ;
4. générer les commandes avec un gabarit spécifique à la plateforme ;
5. afficher le plan sans l'appliquer ;
6. tester les entrées vides, incorrectes et inattendues ;
7. ajouter les validations postérieures prévues.

**Critères d'acceptation :**

- aucune commande libre n'est acceptée ;
- l'équipement est autorisé ;
- le plan est visible ;
- l'ID est présent ;
- aucune modification n'est appliquée pendant la phase de planification.

## LABORATOIRE 6 — État initial, état final et diff

**Objectif :** construire des preuves autour d'une modification contrôlée.

Étapes :

1. capturer l'état initial d'une cible de laboratoire ;
2. vérifier et protéger l'artefact ;
3. générer le plan approuvé ;
4. appliquer le changement sur la cible pilote ;
5. capturer l'état final ;
6. produire le diff ;
7. valider l'état attendu ;
8. simuler une validation négative ;
9. vérifier que le déploiement s'arrête.

**Critère :** une validation en échec ne doit jamais être convertie en succès parce que la commande CLI a renvoyé du texte.

N'activez une récupération automatique qu'après avoir testé la procédure sur la plateforme concernée.

## LABORATOIRE 7 — Rapport d'exploitation

**Objectif :** produire un rapport qui permet de diagnostiquer un lot.

Étapes :

1. ajouter un `run_id` ;
2. enregistrer l'heure et la durée ;
3. classer les statuts ;
4. compter les résultats ;
5. générer le JSON ;
6. fournir une synthèse lisible ;
7. rechercher des valeurs sensibles dans le rapport ;
8. définir les permissions et la rétention.

**Critère :** un autre opérateur doit pouvoir comprendre le résultat sans devoir lire le code source.

## LABORATOIRE 8 — Workflow complet

**Objectif :** réunir l'ensemble du parcours en un workflow reproductible.

Préconditions :

- environnement de laboratoire autorisé ;
- compte en lecture seule ;
- compte de changement distinct si nécessaire ;
- inventaire validé ;
- confiance SSH préparée ;
- méthode de sauvegarde testée ;
- procédure de récupération documentée ;
- fenêtre d'intervention définie.

Étapes :

1. charger et valider l'inventaire ;
2. sélectionner les cibles ;
3. collecter l'état initial ;
4. construire le plan ;
5. afficher le plan ;
6. obtenir une approbation selon le workflow retenu ;
7. appliquer sur le lot pilote ;
8. vérifier la réponse CLI ;
9. relire l'état final ;
10. effectuer les contrôles métier ;
11. poursuivre ou arrêter selon les critères prévus ;
12. produire un rapport complet ;
13. examiner les logs et les artefacts.

**Livrables :**

- code source organisé ;
- inventaire fictif ou de laboratoire ;
- tests automatisés ;
- exemple de plan ;
- rapport JSON ;
- procédure de déploiement ;
- procédure d'arrêt ;
- procédure de récupération ;
- documentation d'exploitation.

---

# 19. PROJET FINAL — NETOPS CHANGE RUNNER

## 19.1. Mission

Construire un outil CLI capable de collecter des informations sur plusieurs équipements et de préparer puis appliquer un changement simple dans un environnement contrôlé.

Le projet doit réutiliser tout ce qui a été développé précédemment. Il ne doit pas devenir un fichier monolithique qui mélange inventaire, secrets, connexions, commandes, tests et rapports.

## 19.2. Interface attendue

L'interface souhaitée peut ressembler à ceci :

```text
netops audit --inventory inventory/devices.yaml --site lab-douala

netops collect --inventory inventory/devices.yaml --site lab-douala --workers 3

netops plan --change config/CHG-2026-1042.yaml

netops apply --change config/CHG-2026-1042.yaml --approval-file approvals/CHG-2026-1042.json

netops report --run-id RUN-2026-10-23-001
```

Ces commandes sont une spécification de projet, pas des commandes fournies nativement par Netmiko. Le parseur CLI et les règles associées doivent être implémentés.

## 19.3. Exigences fonctionnelles

L'application doit :

- refuser les inventaires invalides avant connexion ;
- limiter le périmètre aux équipements autorisés ;
- gérer les profils d'identifiants de façon sécurisée ;
- contrôler la confiance SSH ;
- exécuter les commandes autorisées selon la plateforme ;
- séparer la collecte des changements ;
- borner la concurrence ;
- fermer les sessions ;
- produire un résultat par équipement ;
- distinguer les catégories d'échec ;
- capturer l'état initial avant une modification ;
- présenter le plan ;
- vérifier l'approbation selon le workflow retenu ;
- appliquer un changement autorisé ;
- contrôler l'état final ;
- arrêter le lot lorsqu'un critère d'arrêt est atteint ;
- éviter les reprises aveugles d'opérations non idempotentes ;
- produire des logs et un rapport ;
- protéger les artefacts sensibles.

## 19.4. Exigences non fonctionnelles

**Sécurité :** aucun secret en clair dans le dépôt, privilèges minimaux et logs assainis.

**Maintenabilité :** fonctions courtes, types utiles et modules à responsabilités limitées.

**Testabilité :** tests unitaires pour validation, sélection, planification, résultat et rapport.

**Exploitabilité :** ID de lot, statuts cohérents, code de sortie et logs utiles.

**Résilience :** délais limités, concurrence contrôlée et critères d'arrêt.

**Auditabilité :** plan, approbation et résultats rattachés à une même exécution.

**Reproductibilité :** code et dépendances contrôlés.

**Validation métier :** le résultat final est vérifié indépendamment de la simple réponse CLI.

## 19.5. Barème sur 100 points

| Domaine | Points |
|---|---:|
| Inventaire et validation | 12 |
| Connexion, SSH et secrets | 12 |
| Collecte et normalisation | 12 |
| Concurrence contrôlée | 10 |
| Gestion des erreurs | 12 |
| Cycle de changement | 18 |
| Tests et qualité | 10 |
| Logs et rapports | 8 |
| Documentation | 6 |
| **Total** | **100** |

Seuil conseillé : 80/100.

Certaines erreurs doivent interdire la mise en production quel que soit le score :

- secret découvert dans le dépôt ;
- cible non autorisée traitée ;
- modification rejouée aveuglément après un timeout ;
- succès déclaré sans vérification de l'état final ;
- absence de procédure de récupération pour une modification critique ;
- contournement de la confiance SSH pour éviter de résoudre un problème de clé.

## 19.6. Définition du projet terminé

Le projet n'est pas terminé parce qu'une commande a fonctionné une fois sur le routeur du développeur.

Il est terminé lorsque :

- les scénarios d'échec sont testés ;
- le programme gère les équipements indisponibles ;
- les résultats restent disponibles en cas d'échec partiel ;
- un opérateur peut arrêter le lot ;
- l'état final est vérifiable ;
- les preuves peuvent être reliées à l'exécution ;
- les procédures de récupération ont été éprouvées ;
- les dépendances peuvent être reconstruites ;
- les opérations risquées exigent les autorisations prévues.

---

# 20. DÉPANNAGE AVANCÉ

## 20.1. L'authentification SSH échoue

Vérifiez :

1. le nom d'utilisateur ;
2. la source du mot de passe ou de la clé ;
3. le mode d'authentification autorisé ;
4. la validité de la clé et de sa passphrase ;
5. les droits du compte ;
6. l'état du compte ;
7. le serveur AAA si l'authentification est centralisée ;
8. les restrictions sur les sessions simultanées.

Ne journalisez pas le secret pour comprendre l'erreur.

Si une connexion interactive fonctionne mais que le script échoue, comparez les paramètres et les mécanismes d'authentification réellement utilisés.

## 20.2. `NetmikoTimeoutException`

Cette exception peut apparaître à différentes étapes du cycle de connexion.

Déterminez si le problème survient pendant :

- la connexion TCP ;
- l'attente de la bannière ;
- l'authentification ;
- la préparation de la session ;
- une autre étape couverte par le pilote.

Examinez ensuite le routage, les ACL, le service SSH, les délais, la charge des équipements et les limites de sessions.

Ne passez pas immédiatement tous les délais à plusieurs minutes sans avoir identifié l'étape en cause.

## 20.3. `ReadTimeout`

Une commande longue peut nécessiter un délai de lecture plus élevé. Mais un délai peut également signaler une interaction qui attend une réponse, une invite inattendue, un problème de commande ou une sortie plus importante que prévu.

Mesurez la durée de la commande dans une session contrôlée. Comparez les comportements selon la plateforme et la version. Pour une commande interactive, concevez un échange dédié plutôt que d'augmenter simplement le délai.

## 20.4. Invite ou pagination inattendue

Les bannières, les confirmations interactives, les invites différentes et les paramètres de terminal peuvent modifier le dialogue.

Vérifiez le pilote, la famille de système et la version logicielle. Évitez d'ajouter des `sleep()` arbitraires sans comprendre le mécanisme qui bloque la session.

Un délai artificiel peut sembler résoudre le problème dans un environnement lent tout en rendant le script instable dans un autre.

## 20.5. La CLI signale une erreur sans exception Python

Une commande rejetée peut produire une sortie textuelle sans déclencher d'exception au niveau transport.

Pour chaque profil de commande important, définissez :

- les marqueurs de rejet connus ;
- le format de sortie attendu ;
- les validations de contenu ;
- les conditions d'échec.

Les tests doivent comporter des exemples de sorties normales et de sorties rejetées.

## 20.6. Le mode rapide se comporte différemment

Le paramètre `fast_cli` influence les stratégies temporelles de Netmiko. Il ne corrige pas une commande incorrecte, une authentification invalide ou un problème réseau.

Si le mode rapide échoue, comparez les délais et les sorties, isolez le cas reproductible et retenez un réglage validé pour la plateforme.

Ne l'activez pas globalement avant d'avoir testé le comportement sur l'ensemble des pilotes concernés.

## 20.7. Le parsing TextFSM ne renvoie pas le résultat attendu

Vérifiez :

- la commande exacte ;
- le template ;
- la plateforme ;
- la version de NTC Templates ;
- la version logicielle de l'équipement ;
- les variations de la sortie CLI ;
- le type réellement retourné.

Ajoutez des tests représentatifs. Ne laissez pas une sortie brute être utilisée silencieusement à la place d'une structure attendue.

## 20.8. Les échecs apparaissent seulement en concurrence

Réduisez `max_workers` pour isoler le problème.

Examinez ensuite :

- les limites de sessions ;
- le système AAA ;
- la capacité du plan de contrôle ;
- les délais de réponse ;
- les erreurs concentrées sur un site ou une famille ;
- la synchronisation des tentatives ;
- la charge du serveur d'automatisation.

Ne relancez pas instantanément tous les échecs en parallèle. Une tempête de reprises peut amplifier le problème.

## 20.9. La commande semble avoir réussi mais l'état est incorrect

Arrêtez le lot concerné.

Conservez le plan, l'état initial, la réponse CLI et l'état final observé. Déterminez si la commande a été rejetée, partiellement appliquée, exécutée dans le mauvais contexte ou si le contrôle postérieur lit une source inadaptée.

Utilisez la stratégie de récupération approuvée et confirmez le résultat avec un contrôle indépendant.

Ne qualifiez pas l'opération de succès avant que l'état attendu soit effectivement vérifié.

## 20.10. Une clé d'hôte SSH a changé

Ce changement doit être expliqué.

Il peut correspondre à un remplacement planifié, une réinstallation ou un changement d'équipement, mais il peut également représenter un problème d'identité ou un risque d'interception.

Vérifiez la nouvelle clé au moyen d'une source de confiance, puis mettez à jour le fichier de confiance selon la procédure prévue.

Ne supprimez pas globalement les vérifications de clés d'hôte pour contourner le problème.

---

# 21. ÉVALUATION DE SORTIE

Répondez à ces questions en justifiant vos réponses et en vous appuyant sur des exemples de votre projet.

1. Pourquoi faut-il valider l'inventaire avant la première connexion ?
2. Quelle est la différence entre un timeout de connexion et un timeout de lecture ?
3. Pourquoi ne doit-on pas partager une connexion Netmiko entre plusieurs workers simultanés ?
4. Pourquoi une réponse CLI n'est-elle pas une preuve suffisante de conformité ?
5. Que signifie réellement l'idempotence d'une opération ?
6. Pourquoi le compte de collecte doit-il être séparé du compte de changement ?
7. Pourquoi un timeout après une modification ne prouve-t-il pas l'échec de la commande ?
8. Comment distinguer les erreurs de transport d'un rejet CLI ?
9. Pourquoi conserver un état initial avant une modification ?
10. Quels éléments doit-on associer au `run_id` ?
11. Pourquoi une sortie TextFSM doit-elle être vérifiée en type et en contenu ?
12. Quelles conditions doivent arrêter un lot de changement ?
13. Quelles opérations peuvent être retentées après un échec et lesquelles demandent une vérification préalable ?
14. Comment démontrer que le rollback a réellement fonctionné ?
15. Pourquoi un pourcentage global de succès ne suffit-il pas ?
16. Comment garantir que les secrets n'apparaissent pas dans les journaux ?
17. Pourquoi verrouiller les dépendances ?
18. Comment limiter les risques d'un déploiement sur un parc hétérogène ?
19. Quelles différences faut-il prévoir entre les procédures de sauvegarde selon les plateformes ?
20. Comment séparer une validation syntaxique d'une validation métier ?

## Grille d'auto-évaluation

**Niveau à renforcer :** vous savez ouvrir une session mais les erreurs, la sécurité, les délais et les validations restent difficiles à expliquer.

**Intermédiaire solide :** vous automatisez plusieurs équipements et avez structuré les premières fonctions, mais vous manquez encore de contrats de résultat, de tests et de contrôle du changement.

**Expert en construction :** les couches sont séparées, les données sont validées, les erreurs sont classées, les tests sont automatisés et les rapports sont cohérents.

**Prêt pour une exploitation contrôlée :** les opérations sont testées sur les plateformes réelles, la gestion des autorisations est effective, les critères d'arrêt sont actifs et les procédures de récupération sont éprouvées.

---

# 22. RÉFÉRENCES OFFICIELLES

Les exemples doivent être adaptés à la version de Netmiko, au constructeur et au système d'exploitation réseau réellement utilisés. Consultez la documentation avant d'introduire une nouvelle plateforme ou de modifier un réglage important.

- **Projet Netmiko :** https://github.com/ktbyers/netmiko
- **Releases Netmiko :** https://github.com/ktbyers/netmiko/releases
- **Documentation API Netmiko :** https://ktbyers.github.io/netmiko/docs/netmiko/
- **Documentation de `BaseConnection` :** https://ktbyers.github.io/netmiko/docs/netmiko/base_connection.html
- **Plateformes supportées :** https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md
- **Exemples Netmiko :** https://github.com/ktbyers/netmiko/blob/develop/EXAMPLES.md
- **Documentation PyYAML :** https://pyyaml.org/wiki/PyYAMLDocumentation
- **Documentation pytest :** https://docs.pytest.org/
- **NTC Templates :** https://github.com/networktocode/ntc-templates

Une plateforme mentionnée par un projet comme étant supportée n'implique pas que toutes les commandes fonctionnent sur toutes les versions logicielles d'une gamme. Il faut valider les couples plateforme-version-commande réellement exploités.

---

# CONCLUSION — CE QUI DISTINGUE L'EXPERT

Le parcours a commencé avec un objectif simple : se connecter à un équipement, envoyer une commande, lire la réponse et fermer la session.

Le niveau Intermédiaire a étendu ces bases à des fonctions réutilisables et à plusieurs équipements.

Le niveau Expert conserve exactement ce socle, mais transforme son usage. L'opération Netmiko fait désormais partie d'un système qui vérifie les entrées, limite le périmètre, protège les secrets, maîtrise les délais et la concurrence, classe les erreurs, conserve les preuves, teste la logique et contrôle l'état final.

L'expertise ne se mesure pas au nombre de lignes de Python, ni au nombre d'équipements qu'un script peut interroger en une minute.

Elle se mesure à la capacité de comprendre ce qui s'est passé, à prévenir les actions imprévues, à détecter rapidement les erreurs et à récupérer correctement lorsque les résultats ne correspondent pas à l'objectif.

Retenez ces cinq règles :

1. **Aucune cible n'est traitée sans validation et périmètre explicite.**
2. **Aucune session n'est laissée ouverte par accident.**
3. **Aucun résultat n'est déclaré valide sur la seule base d'une réponse CLI.**
4. **Aucune commande de modification risquée n'est rejouée aveuglément après un timeout.**
5. **Aucun changement n'est considéré comme terminé avant que l'état attendu soit vérifié et que les preuves soient conservées.**

Le code Python fournit le mécanisme. La validation, la sécurité, les tests, la gouvernance et l'observabilité transforment ce mécanisme en une automatisation professionnelle.

**C'est le véritable objectif du niveau Expert : passer d'un script qui exécute des commandes à un système qui contrôle ses actions et sait démontrer ses résultats.**