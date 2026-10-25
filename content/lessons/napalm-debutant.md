# NAPALM — Niveau Débutant
## Automatisation réseau multi-constructeurs avec Python

**Fichier :** `napalm-debutant.md`  
**Niveau :** Débutant  
**Parcours pédagogique :** Débutant → Intermédiaire → Expert  
**Technologies :** Python, NAPALM, SSH, API réseau, configuration et collecte d'informations  
**Public cible :** étudiants en réseaux, administrateurs réseau débutants, techniciens et futurs ingénieurs NetDevOps  
**Prérequis :** bases de Python, adressage IP, SSH et configuration élémentaire d'équipements réseau  
**Objectif :** apprendre à se connecter à un équipement réseau avec NAPALM, récupérer des informations structurées, comprendre l'abstraction multi-constructeurs et réaliser les premières opérations d'automatisation dans un environnement de laboratoire.


# AVANT-PROPOS — LA PREMIÈRE ÉTAPE DU PARCOURS NAPALM

L'automatisation réseau ne consiste pas simplement à exécuter des commandes plus rapidement. Elle consiste à transformer des tâches répétitives en opérations programmables, vérifiables et réutilisables.

Un administrateur peut se connecter manuellement à un routeur pour consulter sa version, vérifier ses interfaces ou examiner sa configuration. Cette méthode convient à une intervention ponctuelle. Elle devient plus difficile à maintenir lorsque les mêmes opérations doivent être répétées sur plusieurs équipements, plusieurs sites ou plusieurs environnements.

Python permet d'automatiser ces opérations. Cependant, si chaque constructeur possède ses propres commandes, ses propres méthodes d'accès et ses propres formats de sortie, le programme peut rapidement devenir complexe.

**NAPALM** est une bibliothèque Python qui cherche précisément à simplifier ce travail en fournissant une API commune pour de nombreuses opérations de gestion réseau, tout en utilisant des pilotes adaptés aux systèmes pris en charge. <Cite refs={["turn591003view0","turn591003view1"]}/>

Dans ce premier niveau, nous allons apprendre à utiliser cette bibliothèque étape par étape.

Nous ne commencerons pas par une architecture d'entreprise compliquée. Nous allons d'abord comprendre une connexion, récupérer les informations d'un équipement, lire l'état de ses interfaces, examiner des données structurées et construire un petit outil d'audit.

Ensuite, nous introduirons prudemment le chargement d'une configuration candidate, la comparaison des changements et la distinction entre préparer une modification et l'appliquer réellement.

Le principe est de construire des compétences que les niveaux suivants pourront réutiliser.

## La progression des trois niveaux

| Niveau | Compétence principale | Résultat attendu |
|---|---|---|
| Débutant | Comprendre et utiliser NAPALM | Se connecter, collecter des informations et effectuer un premier audit |
| Intermédiaire | Structurer l'automatisation | Gérer plusieurs équipements, valider les données, traiter les erreurs et préparer des changements contrôlés |
| Expert | Industrialiser l'automatisation | Mettre en place des workflows de changement, des tests, des contrôles de sécurité, une observabilité et une gouvernance adaptées à la production |

Le niveau Intermédiaire réutilisera les fonctions de collecte et les modèles de données appris ici. Le niveau Expert reprendra les mêmes opérations pour les intégrer à un moteur d'automatisation plus complet.

Nous n'allons donc pas considérer le code du niveau Débutant comme du code jetable. Nous allons commencer avec de petites fonctions, puis les rendre progressivement plus fiables.

## À la fin du niveau Débutant, vous devrez savoir

1. expliquer ce que NAPALM apporte à un programme Python ;
2. installer la bibliothèque et ses dépendances ;
3. choisir le pilote approprié à un équipement pris en charge ;
4. établir et fermer une connexion ;
5. récupérer les informations générales avec `get_facts()` ;
6. interroger les interfaces avec `get_interfaces()` ;
7. récupérer des informations IP avec `get_interfaces_ip()` ;
8. consulter les voisins LLDP si la plateforme prend en charge l'opération ;
9. lire une configuration avec `get_config()` lorsqu'elle est disponible ;
10. comprendre les limites de l'abstraction multi-constructeurs ;
11. traiter les premières erreurs de connexion ;
12. travailler avec un inventaire de plusieurs équipements ;
13. produire un rapport JSON ;
14. préparer un changement avec une configuration candidate ;
15. comparer et abandonner un changement avant de l'appliquer ;
16. comprendre pourquoi la comparaison et la validation sont indispensables avant une modification.

> **Règle fondamentale :** la réussite d'une connexion NAPALM ne prouve pas que l'état du réseau est correct. L'automatisation doit vérifier les données obtenues et, lorsqu'elle modifie une configuration, contrôler le résultat de cette modification.


# SOMMAIRE

1. Comprendre l'automatisation réseau
2. Qu'est-ce que NAPALM ?
3. Comprendre les pilotes
4. Installer l'environnement Python
5. Choisir le bon pilote
6. Établir sa première connexion
7. Comprendre `get_facts()`
8. Collecter l'état des interfaces
9. Récupérer les adresses IP et les voisins LLDP
10. Lire une configuration
11. Comprendre les données structurées
12. Gérer les erreurs et fermer les connexions
13. Automatiser plusieurs équipements
14. Préparer un changement de configuration
15. Comparer, valider, appliquer ou abandonner
16. Tester les fonctions sans équipement réel
17. Laboratoires progressifs
18. Projet final : NAPALM Network Auditor
19. Dépannage
20. Exercices d'évaluation
21. Glossaire
22. Références officielles


# 1. COMPRENDRE L'AUTOMATISATION RÉSEAU

## 1.1. La gestion manuelle

Imaginons que vous administriez trois routeurs.

Chaque matin, vous devez vérifier :

- leur nom d'hôte ;
- leur version logicielle ;
- leurs interfaces ;
- leurs adresses IP ;
- leur état opérationnel.

Avec une méthode manuelle, vous pourriez ouvrir une session sur chaque équipement et exécuter plusieurs commandes CLI.

Cette approche fonctionne, mais elle présente plusieurs limites :

- les tâches doivent être répétées manuellement ;
- une commande peut être oubliée ;
- les résultats peuvent être copiés de façon incorrecte ;
- les différences entre constructeurs compliquent les vérifications ;
- les rapports prennent du temps à préparer.

Une automatisation permet de répéter ces opérations de manière contrôlée.

## 1.2. Première solution : Python avec une CLI

Un script utilisant SSH peut envoyer des commandes à un équipement.

Par exemple, l'automatisation peut lancer une commande d'affichage, récupérer son texte et analyser le résultat.

Cependant, les commandes et sorties peuvent varier selon le système réseau.

Un programme qui analyse des colonnes de texte doit comprendre leur structure exacte. Si la sortie change, le script peut commencer à interpréter incorrectement les informations.

Cela ne signifie pas que l'automatisation CLI est mauvaise. Elle reste utile, notamment avec des bibliothèques comme Netmiko. Cela signifie qu'une abstraction fondée sur des méthodes communes peut simplifier certaines opérations.

## 1.3. Le principe de NAPALM

NAPALM signifie *Network Automation and Programmability Abstraction Layer with Multivendor support*.

La bibliothèque fournit des méthodes communes pour effectuer certaines opérations de gestion réseau sur différents systèmes compatibles, tout en utilisant des pilotes spécifiques. Elle propose notamment des mécanismes de collecte de données et de gestion des configurations. <Cite refs={["turn591003view0","turn591003view2"]}/>

Par exemple, pour récupérer des informations générales sur un équipement, l'application peut appeler :

```python
facts = device.get_facts()
```

La fonction retourne un dictionnaire contenant des informations comme le nom de l'équipement, le modèle, la version logicielle et la liste des interfaces, sous réserve de la prise en charge du pilote.

Le programme n'a pas besoin de construire lui-même une commande spécifique pour chaque constructeur afin de commencer cette collecte.

## 1.4. Ce que NAPALM simplifie

La bibliothèque fournit une interface commune pour de nombreuses opérations, notamment :

- l'ouverture et la fermeture des sessions ;
- la collecte des faits ;
- la récupération des informations d'interfaces ;
- la collecte de voisins réseau ;
- la lecture de configurations ;
- la préparation de modifications ;
- la comparaison de configurations candidates ;
- certaines opérations de validation, de commit et de rollback selon le pilote.

Cette API commune ne signifie pas que chaque méthode fonctionne sur tous les équipements. La prise en charge dépend du pilote, du système d'exploitation réseau, de sa version et parfois de sa configuration. La matrice officielle distingue les fonctionnalités disponibles par plateforme. <Cite refs={["turn591003view4","turn591003view2"]}/>

## 1.5. Schéma SVG animé — de l'administrateur au programme

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="intro-title intro-desc" style="max-width:100%;height:auto">
  <title id="intro-title">Passer de la gestion manuelle à l'automatisation NAPALM</title>
  <desc id="intro-desc">Python utilise NAPALM, qui choisit un pilote adapté et communique avec un équipement. Les données structurées sont ensuite utilisées pour construire un rapport.</desc>
  <defs>
    <marker id="intro-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#5abfe6"/></marker>
    <style>
      @keyframes nap-intro-flow { to { stroke-dashoffset:-28 } }
      .nap-intro-link { fill:none;stroke:#5abfe6;stroke-width:2.5;stroke-dasharray:7 7;marker-end:url(#intro-arrow);animation:nap-intro-flow 2s linear infinite }
      .nap-intro-label { fill:#f1f6ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-intro-small { fill:#bccbe0;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="338" rx="14" fill="#0c1421" stroke="#2d4058"/>
  <rect x="22" y="84" width="168" height="76" rx="10" fill="#292440" stroke="#b1a1ee" stroke-width="1.5"/>
  <text x="106" y="111" class="nap-intro-label">Python</text><text x="106" y="133" class="nap-intro-small">script d'audit</text>
  <rect x="227" y="84" width="168" height="76" rx="10" fill="#193246" stroke="#61bce7" stroke-width="1.5"/>
  <text x="311" y="111" class="nap-intro-label">NAPALM</text><text x="311" y="133" class="nap-intro-small">API commune</text>
  <rect x="432" y="84" width="168" height="76" rx="10" fill="#17352e" stroke="#65c7a5" stroke-width="1.5"/>
  <text x="516" y="111" class="nap-intro-label">Pilote</text><text x="516" y="133" class="nap-intro-small">adapté au système</text>
  <rect x="637" y="84" width="278" height="76" rx="10" fill="#34291e" stroke="#e4b15f" stroke-width="1.5"/>
  <text x="776" y="111" class="nap-intro-label">Équipement réseau</text><text x="776" y="133" class="nap-intro-small">IOS, EOS, Junos, IOS-XR...</text>
  <path class="nap-intro-link" d="M190 122 H222"/><path class="nap-intro-link" d="M395 122 H427"/><path class="nap-intro-link" d="M600 122 H632"/>
  <path class="nap-intro-link" d="M776 160 V218 H516 V165"/>
  <rect x="240" y="220" width="552" height="58" rx="10" fill="#1d2a3f" stroke="#8ba4c8" stroke-width="1.5"/>
  <text x="516" y="243" class="nap-intro-label">Résultats structurés</text><text x="516" y="262" class="nap-intro-small">faits, interfaces, adresses, voisins, état</text>
  <text x="470" y="315" class="nap-intro-small">Le programme traite des données ; il ne dépend pas uniquement de texte CLI brut.</text>
</svg>

## 1.6. Ce que NAPALM ne garantit pas

Il est important de comprendre les limites de l'outil dès le début.

NAPALM ne garantit pas automatiquement :

- la compatibilité avec tous les constructeurs ;
- la prise en charge de chaque méthode sur chaque pilote ;
- l'identité d'une cible au-delà des vérifications réalisées par le transport sous-jacent ;
- la validité métier d'une configuration ;
- la réussite d'un changement simplement parce qu'aucune exception n'a été levée ;
- la possibilité d'annuler chaque opération sur tous les équipements ;
- une transaction atomique universelle entre plusieurs routeurs ;
- une configuration identique à travers tous les constructeurs.

Ces limites ne sont pas des défauts du cours. Elles constituent précisément une partie importante de l'apprentissage de l'automatisation réseau.


# 2. QU'EST-CE QUE NAPALM ?

## 2.1. La bibliothèque et ses pilotes

Le code d'un programme NAPALM commence généralement par importer la fabrique des pilotes :

```python
from napalm import get_network_driver
```

Cette fonction permet de sélectionner le pilote utilisé pour un type de système réseau.

Exemple :

```python
driver = get_network_driver("ios")
```

Le nom `"ios"` représente le pilote choisi. Il ne s'agit pas d'une valeur universelle pour tous les équipements Cisco, ni d'un paramètre que l'on peut remplacer par n'importe quel nom arbitraire.

D'autres identifiants existent, tels que `eos`, `junos`, `iosxr`, `iosxr_netconf`, `nxos` ou `nxos_ssh`, suivant les pilotes intégrés et leurs contraintes. Vérifiez la matrice de compatibilité et la documentation de la version installée avant de choisir le nom du pilote. <Cite refs={["turn591003view1","turn591003view4"]}/>

## 2.2. L'API commune

Voici le modèle général d'utilisation :

```python
from napalm import get_network_driver

driver = get_network_driver("ios")

device = driver(
    hostname="192.0.2.10",
    username="netops",
    password="secret",
)

device.open()

facts = device.get_facts()
print(facts)

device.close()
```

Ce code illustre la séquence de base :

1. choisir un pilote ;
2. créer l'objet de connexion ;
3. ouvrir la connexion ;
4. exécuter une méthode ;
5. traiter le résultat ;
6. fermer la connexion.

Les valeurs `192.0.2.10`, `netops` et `secret` sont des exemples. Ne mettez jamais un vrai mot de passe dans un fichier Python destiné à être versionné.

Nous améliorerons ce premier exemple pour garantir la fermeture de la connexion en cas d'erreur.

## 2.3. Les méthodes essentielles du niveau Débutant

| Méthode | Utilité générale |
|---|---|
| `open()` | Établir la connexion |
| `close()` | Fermer la connexion |
| `is_alive()` | Vérifier certains indicateurs de disponibilité de la connexion |
| `get_facts()` | Collecter des informations générales |
| `get_interfaces()` | Collecter l'état et des attributs des interfaces |
| `get_interfaces_ip()` | Collecter les informations IP des interfaces |
| `get_lldp_neighbors()` | Récupérer les voisins LLDP, lorsque pris en charge |
| `get_bgp_neighbors()` | Récupérer des informations sur les voisins BGP, lorsque pris en charge |
| `get_config()` | Lire des configurations, selon les capacités du pilote |
| `load_merge_candidate()` | Préparer une configuration à fusionner |
| `load_replace_candidate()` | Préparer une configuration de remplacement |
| `compare_config()` | Comparer configuration courante et candidate |
| `commit_config()` | Appliquer une configuration candidate, selon le pilote |
| `discard_config()` | Abandonner la configuration candidate |

La disponibilité de ces méthodes, leur contenu de retour et leurs limites sont définis par le pilote et la documentation de la version installée. Une méthode documentée dans l'API commune peut être non supportée ou présenter des limitations selon la plateforme. <Cite refs={["turn591003view2","turn591003view4"]}/>

## 2.4. Le principe d'abstraction

Supposons que vous deviez récupérer les informations générales de dix routeurs compatibles, dont certains utilisent des systèmes différents.

Sans une interface commune, votre programme peut nécessiter dix ensembles de commandes et de parsers.

Avec NAPALM, vous pouvez commencer par un flux commun :

```python
facts = device.get_facts()
```

Le pilote sélectionné se charge du mécanisme spécifique à la plateforme.

Attention : les champs retournés peuvent être absents, vides ou particuliers selon les capacités du système. Il faut donc toujours vérifier la réponse plutôt que supposer que tous les équipements fournissent exactement les mêmes informations.

## 2.5. Schéma SVG animé — le rôle des pilotes

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="driver-title driver-desc" style="max-width:100%;height:auto">
  <title id="driver-title">NAPALM et ses pilotes multi-constructeurs</title>
  <desc id="driver-desc">Une application appelle la même API NAPALM qui sélectionne un pilote adapté à un équipement. Chaque pilote utilise le mécanisme de gestion supporté par sa plateforme.</desc>
  <defs>
    <marker id="driver-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#67c8a5"/></marker>
    <style>
      @keyframes nap-driver-flow { to { stroke-dashoffset:-27 } }
      .nap-driver-link { fill:none;stroke:#67c8a5;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#driver-arrow);animation:nap-driver-flow 2s linear infinite }
      .nap-driver-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-driver-small { fill:#becadd;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="353" rx="14" fill="#0d1420" stroke="#2e4158"/>
  <rect x="30" y="130" width="190" height="80" rx="10" fill="#292440" stroke="#b2a2ef" stroke-width="1.5"/>
  <text x="125" y="160" class="nap-driver-label">Application</text><text x="125" y="182" class="nap-driver-small">get_facts()</text><text x="125" y="198" class="nap-driver-small">get_interfaces()</text>
  <rect x="300" y="130" width="175" height="80" rx="10" fill="#193246" stroke="#61bee6" stroke-width="1.5"/>
  <text x="387" y="160" class="nap-driver-label">NAPALM</text><text x="387" y="182" class="nap-driver-small">API commune</text>
  <path class="nap-driver-link" d="M220 170 H295"/>
  <rect x="550" y="54" width="160" height="60" rx="9" fill="#17352f" stroke="#66c8a7" stroke-width="1.5"/>
  <text x="630" y="79" class="nap-driver-label">Pilote IOS</text><text x="630" y="97" class="nap-driver-small">exemple</text>
  <rect x="550" y="140" width="160" height="60" rx="9" fill="#17352f" stroke="#66c8a7" stroke-width="1.5"/>
  <text x="630" y="165" class="nap-driver-label">Pilote EOS</text><text x="630" y="183" class="nap-driver-small">exemple</text>
  <rect x="550" y="226" width="160" height="60" rx="9" fill="#17352f" stroke="#66c8a7" stroke-width="1.5"/>
  <text x="630" y="251" class="nap-driver-label">Pilote Junos</text><text x="630" y="269" class="nap-driver-small">exemple</text>
  <path class="nap-driver-link" d="M475 170 H510 V84 H545"/>
  <path class="nap-driver-link" d="M475 170 H545"/>
  <path class="nap-driver-link" d="M475 170 H510 V256 H545"/>
  <rect x="760" y="85" width="150" height="180" rx="10" fill="#30281e" stroke="#e1b15f" stroke-width="1.5"/>
  <text x="835" y="117" class="nap-driver-label">Équipements</text><text x="835" y="143" class="nap-driver-small">systèmes différents</text><text x="835" y="165" class="nap-driver-small">transport adapté</text><text x="835" y="187" class="nap-driver-small">fonctions propres</text><text x="835" y="209" class="nap-driver-small">à la plateforme</text>
  <path class="nap-driver-link" d="M710 84 H735 V123 H755"/>
  <path class="nap-driver-link" d="M710 170 H755"/>
  <path class="nap-driver-link" d="M710 256 H735 V226 H755"/>
  <text x="470" y="324" class="nap-driver-small">Une API commune ne rend pas toutes les fonctionnalités universelles.</text>
</svg>


# 3. INSTALLER L'ENVIRONNEMENT PYTHON

## 3.1. Vérifier la version de Python

À la date de rédaction, PyPI indique NAPALM 5.2.0 comme version publiée la plus récente que nous avons vérifiée, avec Python 3.10 ou supérieur comme prérequis de cette release. Consultez PyPI avant une nouvelle installation ou une mise à jour afin de confirmer les contraintes actuelles. <Cite refs={["turn568966search3","turn568966search1"]}/>

Vérifiez votre installation :

```bash
python --version
python -m pip --version
```

Si votre version de Python est trop ancienne, utilisez un environnement compatible au lieu de forcer l'installation d'une version de NAPALM dont les dépendances ne correspondent pas à votre système.

## 3.2. Créer un environnement virtuel

Linux ou macOS :

```bash
mkdir napalm-debutant
cd napalm-debutant

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
```

Windows PowerShell :

```powershell
mkdir napalm-debutant
cd napalm-debutant

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
```

Un environnement virtuel sépare les dépendances de ce projet de celles d'autres applications Python.

Cette isolation est particulièrement utile lorsqu'une bibliothèque réseau dépend de packages qui ne sont pas utilisés ailleurs dans votre environnement.

## 3.3. Installer NAPALM

Installation générale :

```bash
python -m pip install napalm
```

Vérifier l'installation :

```bash
python -m pip show napalm
python -m pip check
```

Le paquet NAPALM inclut ses dépendances principales pour les pilotes disponibles, mais certaines plateformes peuvent nécessiter des prérequis particuliers. Il faut consulter la documentation du pilote et vérifier les fonctionnalités supportées pour la version réellement installée. <Cite refs={["turn591003view0","turn591003view4"]}/>

## 3.4. Verrouiller l'environnement

Après avoir testé l'installation et vérifié son fonctionnement :

```bash
python -m pip freeze > requirements-lock.txt
```

Le fichier généré permet de conserver une trace des versions installées.

Pour un usage professionnel, les versions doivent être testées et mises à jour de manière contrôlée. Il ne faut pas modifier automatiquement les dépendances d'un outil d'automatisation de production sans tests.

## 3.5. Arborescence du laboratoire

Nous allons organiser les fichiers de la façon suivante :

```text
napalm-debutant/
├── requirements-lock.txt
├── README.md
├── .gitignore
├── inventory/
│   └── devices.yaml
├── examples/
│   ├── connect_device.py
│   ├── collect_facts.py
│   ├── collect_interfaces.py
│   └── audit_inventory.py
├── reports/
└── tests/
    └── test_validation.py
```

Le dossier `reports/` peut contenir des données d'inventaire et des détails de configuration. Ne le publiez pas dans un dépôt public sans avoir évalué les informations qu'il contient.

### `.gitignore`

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
reports/
*.log
*.secret
```

Ne mettez pas de vrais mots de passe dans le code, dans l'inventaire ou dans les fichiers de test.


# 4. CHOISIR LE BON PILOTE

## 4.1. Le pilote est le lien entre l'API commune et le système

Avant de se connecter, le programme doit sélectionner le pilote approprié.

Exemple :

```python
from napalm import get_network_driver

driver = get_network_driver("ios")
```

La chaîne `"ios"` indique au programme le pilote à utiliser. Elle doit correspondre au système d'exploitation réseau et au mécanisme de connexion supporté.

NAPALM distingue par exemple les pilotes IOS-XR utilisant NETCONF et ceux utilisant XML-Agent. Des variantes existent également pour certains accès NX-OS. <Cite refs={["turn591003view1","turn591003view4"]}/>

## 4.2. Exemples de noms de pilotes

| Pilote | Plateforme ou mécanisme | Précaution |
|---|---|---|
| `ios` | Cisco IOS | Vérifier la version et les limitations |
| `iosxr` | Cisco IOS-XR avec XML-Agent | Vérifier les prérequis du service |
| `iosxr_netconf` | Cisco IOS-XR avec NETCONF | Vérifier l'accès NETCONF et les capacités |
| `eos` | Arista EOS | Vérifier eAPI, version et options du pilote |
| `junos` | Juniper Junos | Vérifier les prérequis Junos/PyEZ |
| `nxos` | Cisco NX-OS avec le mécanisme pris en charge par le pilote | Vérifier NX-API et la version |
| `nxos_ssh` | Variante utilisant SSH pour certaines opérations NX-OS | Les capacités diffèrent de `nxos` |

Ce tableau donne des repères. Il ne remplace pas la matrice officielle, qui précise les versions minimales, les dépendances et les limites propres aux pilotes. <Cite refs={["turn591003view1","turn591003view4"]}/>

## 4.3. Pourquoi le nom du pilote importe

Un pilote peut être capable de récupérer les interfaces tout en ne supportant pas certaines autres méthodes.

Par exemple, la prise en charge de `get_facts()` ne prouve pas que `get_arp_table()` ou `get_network_instances()` sera disponible sur le même pilote.

Il faut vérifier les méthodes utilisées dans le projet au lieu de supposer que le mot « multi-constructeurs » signifie « toutes les méthodes sur toutes les plateformes ».

## 4.4. Identifier la méthode de gestion

Les pilotes peuvent utiliser différents mécanismes :

- API constructeur ;
- SSH et CLI ;
- NETCONF ;
- XML-Agent ou autres interfaces propres à la plateforme.

Le choix du transport et les prérequis ne sont pas décidés par l'application à chaque appel de `get_facts()`. Le pilote les gère selon sa conception et sa configuration.

## 4.5. Un premier contrôle du pilote

```python
from napalm import get_network_driver


def main() -> None:
    driver_name = "ios"

    driver = get_network_driver(driver_name)

    print("Pilote chargé :", driver_name)
    print("Classe :", driver)


if __name__ == "__main__":
    main()
```

Ce programme vérifie que la fabrique retourne un pilote. Il ne prouve pas que l'équipement est accessible, que le système est compatible ou que l'authentification réussira.

La compatibilité réelle doit être vérifiée par un test sur un équipement ou un environnement de laboratoire autorisé.


# 5. ÉTABLIR SA PREMIÈRE CONNEXION

## 5.1. Les éléments de connexion

Une connexion NAPALM nécessite généralement :

- le pilote ;
- le nom d'hôte ou l'adresse IP ;
- le nom d'utilisateur ;
- le mot de passe ou un mécanisme d'authentification supporté ;
- éventuellement des arguments de pilote supplémentaires ;
- un délai d'attente adapté.

L'exemple suivant est destiné à un environnement de laboratoire :

```python
from napalm import get_network_driver


driver = get_network_driver("ios")

device = driver(
    hostname="192.0.2.10",
    username="netops",
    password="EXAMPLE-ONLY",
    timeout=30,
)
```

L'adresse de documentation `192.0.2.10` doit être remplacée par la cible autorisée. La chaîne de mot de passe est un exemple fictif.

Il ne faut jamais enregistrer les mots de passe réels dans un dépôt Git.

## 5.2. Ouvrir la session

La séquence élémentaire est :

```python
device.open()

try:
    print(device.get_facts())
finally:
    device.close()
```

Le bloc `finally` garantit que le programme tente de fermer la session lorsque le corps du `try` se termine, y compris en présence d'une exception.

Cette discipline doit devenir systématique.

## 5.3. Utiliser le gestionnaire de contexte

NAPALM prend en charge un gestionnaire de contexte pour la gestion habituelle des sessions. Il ouvre et ferme la session lorsque cela est approprié, ce qui simplifie le nettoyage du code. <Cite refs={["turn406991search10","turn591003view2"]}/>

Exemple :

```python
from napalm import get_network_driver


driver = get_network_driver("ios")

with driver(
    hostname="192.0.2.10",
    username="netops",
    password="EXAMPLE-ONLY",
    timeout=30,
) as device:

    facts = device.get_facts()

    print(facts)
```

La connexion est gérée par le bloc `with`.

C'est la forme à privilégier pour les exemples simples, les collectes et les opérations qui ne nécessitent pas une gestion de session manuelle plus complexe.

## 5.4. Ne pas confondre objet et connexion

La création de l'objet `device` sélectionne le pilote et prépare ses paramètres. Cela ne signifie pas nécessairement que toutes les étapes de la connexion ont été effectuées.

La méthode `open()` établit la connexion effective dans le modèle classique.

Cette distinction est utile lorsqu'on doit classer les erreurs : le problème peut survenir pendant l'initialisation du pilote, l'établissement de session ou l'appel à une méthode de collecte.

## 5.5. Schéma SVG animé — cycle d'une connexion

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="connection-title connection-desc" style="max-width:100%;height:auto">
  <title id="connection-title">Cycle de connexion NAPALM</title>
  <desc id="connection-desc">Le programme charge le pilote, crée un objet, ouvre une session, collecte des informations, ferme la connexion et produit un résultat.</desc>
  <defs>
    <marker id="connection-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#5bbde5"/></marker>
    <style>
      @keyframes nap-connection-flow { to { stroke-dashoffset:-26 } }
      .nap-connection-link { fill:none;stroke:#5bbde5;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#connection-arrow);animation:nap-connection-flow 2s linear infinite }
      .nap-connection-label { fill:#f2f5ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-connection-small { fill:#bccbde;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="338" rx="14" fill="#0c1421" stroke="#2b4058"/>
  <rect x="20" y="73" width="155" height="70" rx="9" fill="#292440" stroke="#b1a2ef" stroke-width="1.5"/>
  <text x="97" y="99" class="nap-connection-label">Pilote</text><text x="97" y="120" class="nap-connection-small">sélection</text>
  <rect x="195" y="73" width="155" height="70" rx="9" fill="#193246" stroke="#60bde6" stroke-width="1.5"/>
  <text x="272" y="99" class="nap-connection-label">Objet</text><text x="272" y="120" class="nap-connection-small">paramètres</text>
  <rect x="370" y="73" width="155" height="70" rx="9" fill="#17352e" stroke="#65c7a5" stroke-width="1.5"/>
  <text x="447" y="99" class="nap-connection-label">open()</text><text x="447" y="120" class="nap-connection-small">session</text>
  <rect x="545" y="73" width="155" height="70" rx="9" fill="#183448" stroke="#60bde6" stroke-width="1.5"/>
  <text x="622" y="99" class="nap-connection-label">Collecte</text><text x="622" y="120" class="nap-connection-small">get_facts()</text>
  <rect x="720" y="73" width="195" height="70" rx="9" fill="#33291e" stroke="#e3b05e" stroke-width="1.5"/>
  <text x="817" y="99" class="nap-connection-label">close()</text><text x="817" y="120" class="nap-connection-small">fermeture</text>
  <path class="nap-connection-link" d="M175 108 H190"/><path class="nap-connection-link" d="M350 108 H365"/><path class="nap-connection-link" d="M525 108 H540"/><path class="nap-connection-link" d="M700 108 H715"/>
  <path d="M817 143 V201 H622 V148" fill="none" stroke="#e3b05e" stroke-width="2.2" stroke-dasharray="6 7" style="animation:nap-connection-flow 2.3s linear infinite"/>
  <rect x="250" y="203" width="495" height="57" rx="10" fill="#1d2b40" stroke="#8aa4ca" stroke-width="1.5"/>
  <text x="497" y="226" class="nap-connection-label">Résultat exploitable</text><text x="497" y="245" class="nap-connection-small">données structurées et statut d'exécution</text>
  <text x="470" y="299" class="nap-connection-small">Un échec doit aussi déclencher la fermeture de la session ouverte.</text>
</svg>


# 6. COMPRENDRE `get_facts()`

## 6.1. Pourquoi commencer par les facts ?

Avant de vérifier les interfaces ou les routes, il est utile de connaître l'équipement que l'on interroge.

NAPALM propose `get_facts()` pour retourner un ensemble d'informations générales dans un dictionnaire Python. La définition commune inclut des valeurs telles que l'hôte, le modèle, la version logicielle, le numéro de série, le temps de fonctionnement et la liste des interfaces, sous réserve de la façon dont le pilote renseigne ces champs. <Cite refs={["turn406991search4","turn591003view2"]}/>

## 6.2. Exemple complet

Créez `examples/collect_facts.py` :

```python
import os

from napalm import get_network_driver


def main() -> None:
    driver_name = os.environ["NAPALM_DRIVER"]
    hostname = os.environ["NAPALM_HOST"]
    username = os.environ["NAPALM_USERNAME"]
    password = os.environ["NAPALM_PASSWORD"]

    driver = get_network_driver(driver_name)

    with driver(
        hostname=hostname,
        username=username,
        password=password,
        timeout=30,
    ) as device:

        facts = device.get_facts()

        print("Informations générales de l'équipement")

        for field, value in facts.items():
            print(f"{field}: {value}")


if __name__ == "__main__":
    main()
```

Ce programme récupère les paramètres depuis l'environnement, sélectionne le pilote et collecte les facts.

Le nom du pilote et les identifiants doivent correspondre à un équipement réellement pris en charge.

## 6.3. Exemples de données retournées

Un dictionnaire peut ressembler à ceci :

```python
{
    "hostname": "router-lab-01",
    "fqdn": "router-lab-01.example.net",
    "vendor": "Example Vendor",
    "model": "Virtual Router",
    "serial_number": "LAB-SERIAL-001",
    "os_version": "Example-OS-Version",
    "uptime": 86400,
    "interface_list": [
        "Ethernet1",
        "Ethernet2",
        "Loopback0",
    ],
}
```

Les valeurs ci-dessus sont fictives.

Ne supposez pas que les clés contiendront les mêmes valeurs sur tous les équipements. Il faut valider les données et consulter la documentation du pilote pour les champs concernés.

## 6.4. Lire certains champs

Vous pouvez lire un élément en utilisant sa clé :

```python
facts = device.get_facts()

hostname = facts.get("hostname")
model = facts.get("model")
version = facts.get("os_version")

print("Nom :", hostname)
print("Modèle :", model)
print("Version :", version)
```

`dict.get()` permet d'obtenir `None` lorsque la clé est absente au lieu de provoquer directement un `KeyError`.

Cependant, une valeur manquante peut être importante. Dans un audit, il peut être nécessaire de signaler le champ absent au lieu de simplement l'ignorer.

## 6.5. Contrôler les champs obligatoires

```python
def validate_facts(facts: dict) -> None:
    required_fields = {
        "hostname",
        "model",
        "os_version",
        "interface_list",
    }

    missing = required_fields - facts.keys()

    if missing:
        raise ValueError(
            f"Facts incomplets : {sorted(missing)}"
        )

    if not isinstance(facts["hostname"], str):
        raise ValueError("hostname doit être une chaîne.")

    if not isinstance(facts["interface_list"], list):
        raise ValueError("interface_list doit être une liste.")
```

Ce validateur correspond au contrat de données choisi pour le laboratoire. Si un pilote légitime ne renseigne pas un champ, le contrat de votre application doit le prévoir explicitement.

Le but n'est pas de considérer chaque valeur vide comme une panne, mais de décider quelles informations sont nécessaires à une opération donnée.

## 6.6. Ce que `get_facts()` ne vous dit pas

Cette méthode ne remplace pas toutes les méthodes de collecte.

Les facts peuvent identifier la version et la liste d'interfaces, mais ils ne donnent pas nécessairement tous les détails nécessaires pour comprendre l'état IP, les voisins LLDP, le routage ou la santé des protocoles.

Pour ces besoins, le programme doit utiliser les getters adaptés.


# 7. COLLECTER L'ÉTAT DES INTERFACES

## 7.1. Pourquoi `get_interfaces()` est utile

Les interfaces sont parmi les premières ressources à inspecter lors d'un audit réseau.

NAPALM propose `get_interfaces()` pour obtenir des informations structurées sur les interfaces supportées par le pilote.

Cette méthode permet notamment d'examiner leur état administratif, leur état opérationnel et d'autres attributs disponibles selon la plateforme. La prise en charge de la méthode doit être vérifiée dans la matrice correspondant à votre environnement. <Cite refs={["turn591003view2","turn591003view4"]}/>

## 7.2. Premier exemple

```python
interfaces = device.get_interfaces()

for name, data in interfaces.items():
    print(name, data)
```

Le dictionnaire est généralement organisé avec le nom de l'interface comme clé et un autre dictionnaire comme valeur.

Les champs disponibles et leur interprétation doivent être vérifiés dans la documentation de la version installée et du pilote utilisé.

## 7.3. Exemple de données illustratives

```python
{
    "Ethernet1": {
        "is_up": True,
        "is_enabled": True,
        "description": "UPLINK",
        "speed": 1000,
        "mac_address": "00:11:22:33:44:55",
        "mtu": 1500,
    },
    "Ethernet2": {
        "is_up": False,
        "is_enabled": True,
        "description": "LAB-PORT",
        "speed": 1000,
        "mac_address": "00:11:22:33:44:66",
        "mtu": 1500,
    },
}
```

Ces données sont inventées pour l'apprentissage.

Elles montrent un point important : l'état administratif et l'état opérationnel représentent deux informations différentes.

Une interface peut être administrativement activée (`is_enabled=True`) tout en étant opérationnellement inactive (`is_up=False`).

## 7.4. Filtrer les interfaces inactives

```python
interfaces = device.get_interfaces()

for name, data in interfaces.items():
    if not data.get("is_up", False):
        print(f"Interface potentiellement inactive : {name}")
```

Ce code repère les interfaces dont la valeur `is_up` est fausse ou absente.

Il ne faut cependant pas déclarer immédiatement une panne. Une interface inactive peut être désactivée volontairement, non raccordée, réservée à une utilisation ultérieure ou soumise à une politique particulière.

Le programme détecte un état à examiner ; il n'en connaît pas automatiquement la cause.

## 7.5. Détecter les incohérences administratives et opérationnelles

```python
def find_enabled_but_down(interfaces: dict) -> list[str]:
    results = []

    for name, data in interfaces.items():
        enabled = data.get("is_enabled")
        up = data.get("is_up")

        if enabled is True and up is False:
            results.append(name)

    return results
```

Cette fonction identifie les interfaces configurées comme activées mais opérationnellement inactives.

Elle n'affirme pas que toutes ces interfaces sont défectueuses. Elle produit une liste de contrôles possibles.

Dans un réseau de production, vous devrez comparer les résultats à l'inventaire attendu, au rôle du port et à la topologie.

## 7.6. Schéma SVG animé — état des interfaces

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 345" role="img" aria-labelledby="if-title if-desc" style="max-width:100%;height:auto">
  <title id="if-title">Collecte et interprétation des interfaces</title>
  <desc id="if-desc">NAPALM récupère des informations structurées, sépare les états administratif et opérationnel, puis les transmet à une fonction de contrôle.</desc>
  <defs>
    <marker id="if-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#67c8a5"/></marker>
    <style>
      @keyframes nap-if-flow { to { stroke-dashoffset:-27 } }
      .nap-if-link { fill:none;stroke:#67c8a5;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#if-arrow);animation:nap-if-flow 2s linear infinite }
      .nap-if-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-if-small { fill:#becbde;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="343" rx="14" fill="#0c1421" stroke="#2d4058"/>
  <rect x="25" y="87" width="205" height="77" rx="10" fill="#292440" stroke="#b1a1ef" stroke-width="1.5"/>
  <text x="127" y="115" class="nap-if-label">get_interfaces()</text><text x="127" y="137" class="nap-if-small">données structurées</text>
  <rect x="280" y="56" width="250" height="65" rx="10" fill="#193246" stroke="#60bee6" stroke-width="1.5"/>
  <text x="405" y="81" class="nap-if-label">État administratif</text><text x="405" y="101" class="nap-if-small">is_enabled</text>
  <rect x="280" y="145" width="250" height="65" rx="10" fill="#17352e" stroke="#66c8a7" stroke-width="1.5"/>
  <text x="405" y="170" class="nap-if-label">État opérationnel</text><text x="405" y="190" class="nap-if-small">is_up</text>
  <rect x="624" y="87" width="285" height="77" rx="10" fill="#33291e" stroke="#e2b15f" stroke-width="1.5"/>
  <text x="766" y="115" class="nap-if-label">Vérification métier</text><text x="766" y="137" class="nap-if-small">comparer à l'état attendu</text>
  <path class="nap-if-link" d="M230 126 H255 V88 H275"/>
  <path class="nap-if-link" d="M230 126 H255 V177 H275"/>
  <path class="nap-if-link" d="M530 88 H570 V126 H619"/>
  <path class="nap-if-link" d="M530 177 H570 V126"/>
  <text x="470" y="264" class="nap-if-label">État administratif ≠ état opérationnel</text>
  <text x="470" y="288" class="nap-if-small">Une interface down n'est pas automatiquement une panne.</text>
  <text x="470" y="313" class="nap-if-small">La validation tient compte du rôle, du contexte et de la politique réseau.</text>
</svg>

## 7.7. Comparer la liste d'interfaces avec les facts

Les facts donnent généralement une liste d'interfaces. `get_interfaces()` fournit les données associées.

Vous pouvez comparer les deux :

```python
facts = device.get_facts()
interfaces = device.get_interfaces()

expected_names = set(facts["interface_list"])
observed_names = set(interfaces.keys())

missing_from_details = expected_names - observed_names
not_listed_in_facts = observed_names - expected_names

print("Absentes du détail :", missing_from_details)
print("Non listées dans les facts :", not_listed_in_facts)
```

Un écart ne signifie pas nécessairement une panne. Les données peuvent avoir été collectées à des moments différents ou représenter des périmètres différents selon le pilote.

Ce type de comparaison est néanmoins utile pour apprendre à contrôler la cohérence des informations.


# 8. RÉCUPÉRER LES ADRESSES IP ET LES VOISINS LLDP

## 8.1. Récupérer les informations IP

`get_interfaces_ip()` permet d'obtenir les informations IP associées aux interfaces, lorsque la méthode est prise en charge par le pilote.

Exemple :

```python
interfaces_ip = device.get_interfaces_ip()

for interface_name, details in interfaces_ip.items():
    print(interface_name, details)
```

Le contenu est structuré par interface et par famille d'adresses. Il peut inclure des informations IPv4 et IPv6 selon les données exposées par le pilote.

## 8.2. Exemple illustratif

```python
{
    "Loopback0": {
        "ipv4": {
            "192.0.2.1": {
                "prefix_length": 32,
            }
        },
        "ipv6": {},
    }
}
```

Les adresses utilisées ici sont illustratives.

La forme détaillée du dictionnaire est définie par l'API de NAPALM, tandis que la disponibilité des données dépend du pilote.

## 8.3. Examiner les voisins LLDP

LLDP permet aux équipements de découvrir certains voisins directement connectés qui annoncent leur présence via ce protocole.

NAPALM propose `get_lldp_neighbors()` et, sur les pilotes qui le supportent, `get_lldp_neighbors_detail()`.

Exemple :

```python
neighbors = device.get_lldp_neighbors()

for local_interface, neighbor_list in neighbors.items():
    print("Interface locale :", local_interface)

    for neighbor in neighbor_list:
        print("  Voisin :", neighbor)
```

La méthode permet de commencer à inventorier la connectivité directe.

Elle ne constitue pas une carte complète du réseau : seuls les voisins annoncés et observables selon la configuration de LLDP et les capacités du pilote pourront être retournés.

## 8.4. Pourquoi les informations de topologie sont utiles

L'association de `get_facts()`, `get_interfaces()` et `get_lldp_neighbors()` permet de construire une première vue d'un équipement :

- son identité ;
- ses interfaces ;
- l'état de ses interfaces ;
- certains paramètres IP ;
- les voisins directs observables.

Dans les niveaux suivants, nous réutiliserons ces données pour construire des rapports multi-équipements et effectuer des vérifications de cohérence.

## 8.5. Schéma SVG animé — construire une vue d'équipement

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 360" role="img" aria-labelledby="facts-title facts-desc" style="max-width:100%;height:auto">
  <title id="facts-title">Construire l'inventaire d'un équipement avec NAPALM</title>
  <desc id="facts-desc">Les facts, les interfaces, les adresses IP et les voisins LLDP sont collectés par différentes méthodes, puis réunis dans un inventaire.</desc>
  <defs>
    <marker id="facts-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#60bee5"/></marker>
    <style>
      @keyframes nap-facts-flow { to { stroke-dashoffset:-26 } }
      .nap-facts-link { fill:none;stroke:#60bee5;stroke-width:2.3;stroke-dasharray:6 7;marker-end:url(#facts-arrow);animation:nap-facts-flow 2s linear infinite }
      .nap-facts-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-facts-small { fill:#bdcbdf;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="358" rx="14" fill="#0c1421" stroke="#2e4058"/>
  <rect x="330" y="30" width="280" height="56" rx="9" fill="#292440" stroke="#b1a1ef" stroke-width="1.5"/>
  <text x="470" y="53" class="nap-facts-label">Équipement</text><text x="470" y="72" class="nap-facts-small">pilote NAPALM</text>
  <rect x="25" y="140" width="195" height="65" rx="9" fill="#183346" stroke="#60bee5" stroke-width="1.5"/>
  <text x="122" y="165" class="nap-facts-label">get_facts()</text><text x="122" y="185" class="nap-facts-small">identité et version</text>
  <rect x="255" y="140" width="195" height="65" rx="9" fill="#17352e" stroke="#64c7a5" stroke-width="1.5"/>
  <text x="352" y="165" class="nap-facts-label">get_interfaces()</text><text x="352" y="185" class="nap-facts-small">état des ports</text>
  <rect x="485" y="140" width="195" height="65" rx="9" fill="#183346" stroke="#60bee5" stroke-width="1.5"/>
  <text x="582" y="165" class="nap-facts-label">get_interfaces_ip()</text><text x="582" y="185" class="nap-facts-small">adresses</text>
  <rect x="715" y="140" width="195" height="65" rx="9" fill="#33291e" stroke="#e2b15f" stroke-width="1.5"/>
  <text x="812" y="165" class="nap-facts-label">get_lldp_neighbors()</text><text x="812" y="185" class="nap-facts-small">voisins directs</text>
  <path class="nap-facts-link" d="M470 86 V112 H122 V135"/>
  <path class="nap-facts-link" d="M470 86 V112 H352 V135"/>
  <path class="nap-facts-link" d="M470 86 V112 H582 V135"/>
  <path class="nap-facts-link" d="M470 86 V112 H812 V135"/>
  <rect x="230" y="260" width="480" height="60" rx="10" fill="#1d2b40" stroke="#8aa5c9" stroke-width="1.5"/>
  <text x="470" y="284" class="nap-facts-label">Inventaire structuré</text><text x="470" y="304" class="nap-facts-small">identité + interfaces + IP + voisinage</text>
  <path class="nap-facts-link" d="M122 205 V233 H470 V255"/>
  <path class="nap-facts-link" d="M352 205 V233"/>
  <path class="nap-facts-link" d="M582 205 V233"/>
  <path class="nap-facts-link" d="M812 205 V233 H710 V255"/>
</svg>


# 9. LIRE UNE CONFIGURATION

## 9.1. Pourquoi lire la configuration ?

Les données opérationnelles et les informations générales ne montrent pas nécessairement comment l'équipement est configuré.

NAPALM propose `get_config()` pour récupérer les configurations disponibles dans les limites du pilote.

Selon l'implémentation, les sources peuvent inclure la configuration en cours, la configuration de démarrage et une configuration candidate. Il faut vérifier la documentation de la plateforme pour comprendre les sources disponibles et leur sémantique. <Cite refs={["turn591003view2","turn591003view4"]}/>

## 9.2. Lire la configuration en cours

Exemple :

```python
configurations = device.get_config(
    retrieve="running"
)

running_config = configurations.get("running", "")

print(running_config)
```

Le nom `"running"` désigne ici la configuration que l'on souhaite récupérer.

La présence et le fonctionnement exact des sources dépendent du pilote. Ne supposez pas que toutes les plateformes exposent les mêmes datastores ou les mêmes méthodes d'accès.

## 9.3. Pourquoi les configurations doivent être protégées

Un fichier de configuration peut contenir des informations sensibles :

- adresses IP internes ;
- architecture du réseau ;
- règles d'accès ;
- détails d'authentification ;
- clés ou secrets mal protégés ;
- noms de systèmes ;
- informations de topologie ;
- détails de routage.

Il ne faut pas afficher ou archiver ces informations sans réfléchir à leur sensibilité.

Pour le laboratoire, évitez de committer les configurations recueillies dans un dépôt public.

## 9.4. Sauvegarder dans un fichier contrôlé

Exemple simple :

```python
from pathlib import Path


def save_running_config(
    device,
    output_path: str | Path,
) -> None:
    result = device.get_config(
        retrieve="running"
    )

    config_text = result.get("running")

    if not isinstance(config_text, str) or not config_text:
        raise ValueError(
            "La configuration running n'a pas été récupérée."
        )

    destination = Path(output_path)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        config_text,
        encoding="utf-8",
    )
```

Cette fonction écrit le contenu dans un fichier. Elle ne chiffre pas le fichier, ne définit pas les permissions et ne met pas en place une politique de rétention.

Pour un usage professionnel, choisissez un répertoire protégé et décidez qui peut lire les sauvegardes.

## 9.5. Éviter les comparaisons de configuration mal interprétées

Un changement textuel peut être important ou anodin suivant son contexte.

Une comparaison est une aide à l'analyse, mais elle ne remplace pas les contrôles sur le service réseau.

Avant d'appliquer un changement, déterminez ce que le diff représente et quels sont ses effets possibles.


# 10. COMPRENDRE LES DONNÉES STRUCTURÉES

## 10.1. Pourquoi les dictionnaires sont utiles

NAPALM retourne beaucoup de résultats sous forme de dictionnaires Python.

Exemple :

```python
facts = device.get_facts()

print(facts["hostname"])
print(facts["model"])
```

Chaque clé permet d'accéder à une information particulière.

Pour une collection d'interfaces, le dictionnaire peut contenir un dictionnaire pour chaque interface.

Cette structure rend les données faciles à parcourir, à comparer et à transformer en rapport JSON.

## 10.2. Parcourir un dictionnaire

```python
interfaces = device.get_interfaces()

for interface_name, attributes in interfaces.items():
    print("Interface :", interface_name)

    for attribute_name, value in attributes.items():
        print(
            "  ",
            attribute_name,
            "=",
            value,
        )
```

Le programme n'a pas besoin de connaître à l'avance chaque valeur : il parcourt les clés disponibles.

Cela est particulièrement utile pendant la découverte des données d'un nouvel équipement de laboratoire.

## 10.3. Dictionnaires et listes

Les facts contiennent généralement une liste d'interfaces.

```python
facts = device.get_facts()

for name in facts.get("interface_list", []):
    print(name)
```

L'utilisation de `get()` avec une liste vide par défaut empêche le programme d'échouer immédiatement si le champ n'est pas présent.

Toutefois, lorsqu'un champ est indispensable à un audit, il faut signaler son absence et ne pas la transformer silencieusement en liste valide.

## 10.4. Transformer les données en JSON

```python
import json

facts = device.get_facts()

json_text = json.dumps(
    facts,
    indent=2,
    ensure_ascii=False,
)

print(json_text)
```

Cette conversion est utile pour produire des rapports ou transmettre des informations à d'autres outils.

Pour un rapport de production, ajoutez aussi le nom logique de la cible, la date de collecte, le résultat et une indication des éventuelles erreurs.

## 10.5. Valider avant de produire le rapport

```python
def summarize_facts(facts: dict) -> dict:
    hostname = facts.get("hostname")

    if not isinstance(hostname, str) or not hostname:
        raise ValueError("Hostname manquant ou invalide.")

    interfaces = facts.get("interface_list")

    if not isinstance(interfaces, list):
        raise ValueError("La liste d'interfaces est invalide.")

    if not all(isinstance(name, str) for name in interfaces):
        raise ValueError("Un nom d'interface est invalide.")

    return {
        "hostname": hostname,
        "model": facts.get("model"),
        "os_version": facts.get("os_version"),
        "interface_count": len(interfaces),
    }
```

Cette fonction produit un résumé, pas une copie complète des facts.

La validation doit correspondre aux besoins du rapport. Si le numéro de série est obligatoire, ajoutez une règle explicite plutôt que de supposer qu'il sera toujours fourni.


# 11. GÉRER LES ERREURS ET FERMER LES CONNEXIONS

## 11.1. Les principales catégories d'erreur

Les erreurs peuvent apparaître pendant différentes étapes :

- sélection du pilote ;
- création de l'objet ;
- établissement de la connexion ;
- authentification ;
- exécution d'une méthode ;
- parsing ou validation des données ;
- fermeture de la session.

Il est préférable de distinguer ces situations au lieu de traiter toutes les exceptions comme un simple problème de réseau.

## 11.2. Un premier traitement d'erreurs

```python
import os

from napalm import get_network_driver


def main() -> int:
    driver_name = os.environ["NAPALM_DRIVER"]
    hostname = os.environ["NAPALM_HOST"]
    username = os.environ["NAPALM_USERNAME"]
    password = os.environ["NAPALM_PASSWORD"]

    try:
        driver = get_network_driver(driver_name)

        with driver(
            hostname=hostname,
            username=username,
            password=password,
            timeout=30,
        ) as device:

            facts = device.get_facts()

            if not facts:
                print("Aucun fact exploitable n'a été retourné.")
                return 1

            print("Collecte réussie.")
            print(facts)

            return 0

    except Exception as exc:
        # Le message complet n'est pas imprimé ici afin d'éviter
        # de publier des détails sensibles sans contrôle.
        print(
            "Échec de la collecte :",
            type(exc).__name__,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Ce code constitue un exemple de départ. Dans un programme plus complet, classez explicitement les exceptions de la bibliothèque et les erreurs de validation afin d'aider au diagnostic.

La classe exacte d'une exception dépend de l'étape concernée et du pilote.

## 11.3. Pourquoi ne pas intercepter toutes les erreurs en les ignorant ?

Cette écriture est dangereuse :

```python
try:
    facts = device.get_facts()
except Exception:
    facts = {}
```

Elle remplace l'erreur par un dictionnaire vide.

Le programme en aval peut ensuite traiter ce résultat comme une collecte normale, alors qu'aucune information n'a été récupérée.

Une approche plus sûre consiste à produire un statut d'échec explicite.

## 11.4. Gérer la fermeture

Les méthodes `open()` et `close()` font partie du modèle classique de connexion NAPALM. Le gestionnaire de contexte est préférable pour les exemples simples, car il automatise la fermeture de la session. <Cite refs={["turn406991search10","turn591003view2"]}/>

Lorsque l'ouverture manuelle est nécessaire, utilisez un `try/finally` et réfléchissez au cas où la connexion n'a pas été initialisée.

## 11.5. Vérifier la disponibilité

```python
status = device.is_alive()

print(status)
```

La méthode `is_alive()` renvoie des informations sur la disponibilité du dispositif selon l'interface et le pilote.

Ce résultat ne remplace pas une collecte métier. Une session qui semble active peut ne pas permettre une opération particulière ; inversement, une méthode de vérification de disponibilité peut avoir un périmètre propre au pilote.


# 12. AUTOMATISER PLUSIEURS ÉQUIPEMENTS

Le niveau Débutant doit apprendre à utiliser un même programme sur plusieurs cibles sans recopier la connexion pour chaque appareil.

## 12.1. Utiliser un inventaire

Créez `inventory/devices.yaml` :

```yaml
devices:
  - name: router-lab-01
    hostname: 192.0.2.10
    driver: ios
    enabled: true
    site: lab-douala

  - name: router-lab-02
    hostname: 192.0.2.11
    driver: eos
    enabled: true
    site: lab-douala

  - name: router-lab-03
    hostname: 192.0.2.12
    driver: junos
    enabled: false
    site: lab-douala
```

Les adresses IP sont des exemples réservés à la documentation. Le pilote doit correspondre à l'équipement réel.

L'inventaire décrit les métadonnées. Il ne doit pas contenir des mots de passe réels.

## 12.2. Pourquoi un champ `enabled` est utile

Le champ `enabled` permet d'exclure volontairement une cible.

Une cible désactivée ne doit pas recevoir de requête simplement parce qu'elle figure dans le fichier.

Ce comportement réduit le risque d'une exécution involontaire sur un équipement qui n'appartient pas au lot actuel.

## 12.3. Charger le YAML

Installez PyYAML si votre environnement ne le possède pas :

```bash
python -m pip install PyYAML
```

Puis :

```python
from pathlib import Path
import yaml


def load_inventory(path: str) -> list[dict]:
    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError("L'inventaire doit être un objet YAML.")

    if set(data) != {"devices"}:
        raise ValueError(
            "L'inventaire doit contenir uniquement devices."
        )

    devices = data["devices"]

    if not isinstance(devices, list):
        raise ValueError("devices doit être une liste.")

    return devices
```

Ce chargeur valide la forme générale du fichier. Une application plus complète doit également valider chaque champ et vérifier que les valeurs du pilote figurent parmi les pilotes autorisés.

## 12.4. Sélectionner les cibles actives

```python
devices = load_inventory(
    "inventory/devices.yaml"
)

selected = [
    device
    for device in devices
    if device.get("enabled") is True
]
```

Une valeur manquante ou incorrecte ne doit pas être interprétée automatiquement comme une autorisation.

## 12.5. Séparer les identifiants de l'inventaire

Pour un laboratoire, on peut fournir les identifiants par variables d'environnement :

```python
import os

username = os.environ["NAPALM_USERNAME"]
password = os.environ["NAPALM_PASSWORD"]
```

Cela évite de coder les valeurs dans chaque entrée.

En production, la gestion des secrets doit être adaptée au système d'exécution. Les variables d'environnement ne sont pas, à elles seules, un coffre de secrets.

## 12.6. Collecte séquentielle de plusieurs équipements

```python
import os
from napalm import get_network_driver


def collect_one(device_info: dict) -> dict:
    device_name = device_info["name"]

    if device_info.get("enabled") is not True:
        return {
            "device": device_name,
            "status": "skipped",
            "facts": None,
        }

    username = os.environ["NAPALM_USERNAME"]
    password = os.environ["NAPALM_PASSWORD"]

    try:
        driver = get_network_driver(
            device_info["driver"]
        )

        with driver(
            hostname=device_info["hostname"],
            username=username,
            password=password,
            timeout=30,
        ) as device:

            facts = device.get_facts()

            return {
                "device": device_name,
                "status": "success",
                "facts": facts,
            }

    except Exception as exc:
        return {
            "device": device_name,
            "status": "failed",
            "error_type": type(exc).__name__,
            "facts": None,
        }


def main() -> None:
    inventory = load_inventory(
        "inventory/devices.yaml"
    )

    results = []

    for device_info in inventory:
        results.append(collect_one(device_info))

    for result in results:
        print(result)


if __name__ == "__main__":
    main()
```

Cette collecte est séquentielle : elle traite une cible après l'autre.

Pour le niveau Débutant, cette approche est plus simple à comprendre et à déboguer que l'exécution parallèle.

## 12.7. Pourquoi commencer en séquentiel ?

Une collecte séquentielle permet de :

- comprendre le cycle de connexion ;
- identifier les erreurs par cible ;
- limiter la pression sur les équipements ;
- vérifier le format des données ;
- maîtriser l'ordre des opérations.

La concurrence sera abordée au niveau Intermédiaire, lorsque la collecte simple sera comprise et testée.

## 12.8. Schéma SVG animé — inventaire multi-équipements

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="inventory-title inventory-desc" style="max-width:100%;height:auto">
  <title id="inventory-title">Collecte NAPALM depuis un inventaire</title>
  <desc id="inventory-desc">Un inventaire validé sélectionne les équipements actifs. Le programme collecte les faits séquentiellement et agrège les statuts dans un rapport.</desc>
  <defs>
    <marker id="inventory-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#60bee6"/></marker>
    <style>
      @keyframes nap-inv-flow { to { stroke-dashoffset:-27 } }
      .nap-inv-link { fill:none;stroke:#60bee6;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#inventory-arrow);animation:nap-inv-flow 2s linear infinite }
      .nap-inv-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-inv-small { fill:#becadd;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="353" rx="14" fill="#0c1421" stroke="#2c4058"/>
  <rect x="25" y="90" width="190" height="78" rx="10" fill="#292440" stroke="#b2a2ef" stroke-width="1.5"/>
  <text x="120" y="117" class="nap-inv-label">Inventaire YAML</text><text x="120" y="139" class="nap-inv-small">cibles et pilotes</text>
  <rect x="270" y="90" width="190" height="78" rx="10" fill="#193246" stroke="#61bce6" stroke-width="1.5"/>
  <text x="365" y="117" class="nap-inv-label">Sélection</text><text x="365" y="139" class="nap-inv-small">actif + autorisé</text>
  <rect x="515" y="90" width="190" height="78" rx="10" fill="#17352e" stroke="#65c8a6" stroke-width="1.5"/>
  <text x="610" y="117" class="nap-inv-label">Collecte</text><text x="610" y="139" class="nap-inv-small">une cible à la fois</text>
  <rect x="760" y="90" width="150" height="78" rx="10" fill="#33291e" stroke="#e3b15e" stroke-width="1.5"/>
  <text x="835" y="117" class="nap-inv-label">Rapport</text><text x="835" y="139" class="nap-inv-small">statuts</text>
  <path class="nap-inv-link" d="M215 129 H265"/><path class="nap-inv-link" d="M460 129 H510"/><path class="nap-inv-link" d="M705 129 H755"/>
  <rect x="220" y="220" width="500" height="62" rx="10" fill="#1d2b40" stroke="#8aa4c9" stroke-width="1.5"/>
  <text x="470" y="244" class="nap-inv-label">Statuts par équipement</text><text x="470" y="263" class="nap-inv-small">succès · échec · ignoré</text>
  <path class="nap-inv-link" d="M835 168 V197 H720 V251"/>
  <text x="470" y="317" class="nap-inv-small">Une cible en erreur ne doit pas effacer les résultats des autres.</text>
</svg>


# 13. PRÉPARER UN CHANGEMENT DE CONFIGURATION

Jusqu'à présent, nous avons uniquement récupéré des informations.

NAPALM fournit également une interface pour préparer et appliquer des changements de configuration sur les plateformes compatibles.

Les méthodes importantes comprennent `load_merge_candidate()`, `load_replace_candidate()`, `compare_config()`, `commit_config()` et `discard_config()`. Le modèle exact d'application, de verrouillage, de commit ou de rollback dépend du pilote et de l'équipement. <Cite refs={["turn591003view3","turn591003view4"]}/>

**Les exemples de cette section doivent être pratiqués uniquement dans un laboratoire autorisé.**

## 13.1. Comprendre la différence entre préparer et appliquer

Le principe général est :

1. préparer une configuration candidate ;
2. comparer la candidate à l'état actuel ;
3. examiner les changements ;
4. appliquer si le plan est approuvé ;
5. abandonner la candidate si le changement est incorrect.

La configuration candidate n'est pas nécessairement appliquée dès son chargement. Cette séparation permet de détecter les erreurs avant l'étape de changement.

Les mécanismes internes varient selon les plateformes ; il faut vérifier comment le pilote réalise chaque étape.

## 13.2. `load_merge_candidate()`

Cette méthode charge une configuration destinée à être fusionnée avec la configuration existante.

Exemple pédagogique :

```python
candidate_config = """
interface Ethernet1
 description LAB-UPLINK
"""

device.load_merge_candidate(
    config=candidate_config
)
```

La syntaxe de configuration présentée dépend du système réseau. `interface Ethernet1` est un exemple ; ce fragment ne doit pas être copié tel quel vers toutes les plateformes.

Le chargement de la candidate ne signifie pas que la configuration est forcément appliquée immédiatement. Le comportement exact doit être compris dans la documentation du pilote.

## 13.3. `load_replace_candidate()`

Cette méthode prépare un remplacement de configuration lorsque le pilote le prend en charge.

Exemple :

```python
device.load_replace_candidate(
    filename="candidate.conf"
)
```

Le fichier doit être adapté à la plateforme cible.

Un remplacement peut avoir des conséquences beaucoup plus importantes qu'une fusion. Une configuration incomplète pourrait supprimer des paramètres existants. Il faut donc comprendre précisément le contenu du fichier et la sémantique du pilote avant de l'utiliser.

Pour les premiers laboratoires, commencez par de petits changements de fusion non critiques.

## 13.4. Le diff avec `compare_config()`

Une fois la candidate chargée :

```python
diff = device.compare_config()

print(diff)
```

La fonction renvoie une représentation des différences entre la configuration courante et la candidate. La prise en charge et le niveau de détail peuvent varier selon la plateforme. <Cite refs={["turn591003view2","turn591003view3"]}/>

Le diff constitue une aide à la revue. Il n'est pas une garantie absolue que tous les effets métier de la modification sont visibles dans le texte.

Avant d'appliquer une configuration :

- vérifiez les cibles ;
- comprenez chaque différence ;
- vérifiez le périmètre du changement ;
- contrôlez les dépendances ;
- déterminez le résultat attendu ;
- vérifiez les possibilités de récupération.

## 13.5. Appliquer avec `commit_config()`

Dans un laboratoire dont le changement a été vérifié :

```python
device.commit_config()
```

Cette méthode demande au pilote d'appliquer la configuration candidate.

Ne l'utilisez pas dans un programme qui applique automatiquement n'importe quel fichier sans validation.

Il faut savoir si la plateforme prend en charge une candidate, un commit atomique ou un mécanisme de confirmation. NAPALM ne peut pas transformer un équipement sans capacité de transaction en équipement qui possède cette capacité.

## 13.6. Abandonner avec `discard_config()`

Si le diff ne correspond pas à l'objectif :

```python
device.discard_config()
```

Cette opération demande au pilote d'abandonner la candidate. Son comportement exact dépend de la plateforme et du type de candidat.

Avant d'abandonner, vérifiez que vous comprenez l'état du processus. Ne supposez pas qu'une configuration a forcément été laissée dans le même état sur tous les équipements.

## 13.7. Cycle de changement en résumé

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 360" role="img" aria-labelledby="change-title change-desc" style="max-width:100%;height:auto">
  <title id="change-title">Préparer et appliquer un changement NAPALM</title>
  <desc id="change-desc">Le programme charge une candidate, compare le diff, décide de l'appliquer ou de l'abandonner, puis vérifie le résultat.</desc>
  <defs>
    <marker id="change-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#65c7a6"/></marker>
    <style>
      @keyframes nap-change-flow { to { stroke-dashoffset:-27 } }
      .nap-change-link { fill:none;stroke:#65c7a6;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#change-arrow);animation:nap-change-flow 2s linear infinite }
      .nap-change-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle }
      .nap-change-small { fill:#becadd;font:12px sans-serif;text-anchor:middle }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="358" rx="14" fill="#0c1421" stroke="#2d4058"/>
  <rect x="25" y="68" width="190" height="68" rx="9" fill="#292440" stroke="#b1a1ef" stroke-width="1.5"/>
  <text x="120" y="95" class="nap-change-label">Candidate</text><text x="120" y="116" class="nap-change-small">chargée</text>
  <rect x="250" y="68" width="190" height="68" rx="9" fill="#193246" stroke="#60bde6" stroke-width="1.5"/>
  <text x="345" y="95" class="nap-change-label">Diff</text><text x="345" y="116" class="nap-change-small">compare_config()</text>
  <rect x="475" y="68" width="190" height="68" rx="9" fill="#34291e" stroke="#e3b15f" stroke-width="1.5"/>
  <text x="570" y="95" class="nap-change-label">Revue</text><text x="570" y="116" class="nap-change-small">décision contrôlée</text>
  <rect x="700" y="68" width="215" height="68" rx="9" fill="#17352e" stroke="#65c7a6" stroke-width="1.5"/>
  <text x="807" y="95" class="nap-change-label">Vérification</text><text x="807" y="116" class="nap-change-small">résultat final</text>
  <path class="nap-change-link" d="M215 102 H245"/><path class="nap-change-link" d="M440 102 H470"/><path class="nap-change-link" d="M665 102 H695"/>
  <path d="M570 136 V203 H345 V141" fill="none" stroke="#e1ad5d" stroke-width="2.3" stroke-dasharray="6 7" style="animation:nap-change-flow 2.3s linear infinite"/>
  <rect x="180" y="205" width="330" height="54" rx="9" fill="#30251c" stroke="#e1ad5d" stroke-width="1.5"/>
  <text x="345" y="228" class="nap-change-label">Diff non satisfaisant</text><text x="345" y="246" class="nap-change-small">discard_config()</text>
  <text x="470" y="299" class="nap-change-label">Une candidate ne doit pas être validée sans revue.</text>
  <text x="470" y="322" class="nap-change-small">Les capacités de commit et de récupération dépendent du pilote.</text>
</svg>


# 14. COMPARER, VALIDER, APPLIQUER OU ABANDONNER

## 14.1. Exemple pédagogique de cycle de modification

Le fragment suivant illustre la structure du workflow. Le nom de pilote, la syntaxe de configuration et la prise en charge des méthodes doivent être vérifiés sur le système de laboratoire.

```python
from napalm import get_network_driver


def main() -> None:
    driver = get_network_driver("ios")

    with driver(
        hostname="192.0.2.10",
        username="netops",
        password="EXAMPLE-ONLY",
        timeout=30,
    ) as device:

        candidate = """
interface GigabitEthernet0/1
 description LAB-UPLINK
"""

        device.load_merge_candidate(
            config=candidate
        )

        diff = device.compare_config()

        print("Diff proposé :")
        print(diff)

        # Cette section est volontairement laissée
        # comme point de décision dans le laboratoire.
        #
        # Si le diff n'est pas conforme :
        #     device.discard_config()
        #
        # Si le diff a été revu et approuvé :
        #     device.commit_config()


if __name__ == "__main__":
    main()
```

Cet exemple ne doit pas être lancé sur un réseau de production tel quel.

Il s'agit d'un modèle d'apprentissage. Pour un véritable laboratoire, ajoutez une procédure de confirmation explicite, un périmètre défini et des contrôles avant et après le changement.

## 14.2. Pourquoi le code ne commit-il pas automatiquement ?

Le programme montre le diff, mais ne prend pas une décision automatique.

C'est volontaire.

La première expérience doit vous apprendre à reconnaître ce qui est sur le point d'être modifié. L'application automatique de tout diff sans contrôle créerait un risque inutile.

Dans les niveaux suivants, le processus d'approbation sera amélioré avec des règles, des tests et une représentation structurée de l'intention de changement.

## 14.3. Le commit-confirmed

Certaines plateformes prennent en charge un mécanisme de commit avec confirmation, qui peut permettre le retour automatique à l'état précédent si le changement n'est pas confirmé avant l'expiration d'un délai.

NAPALM expose certaines méthodes liées à cette fonctionnalité, comme `commit_config(revert_in=...)`, `has_pending_commit()` et `confirm_commit()` lorsqu'elles sont prises en charge. La disponibilité dépend du pilote et de la plateforme. <Cite refs={["turn591003view2","turn591003view3","turn591003view4"]}/>

Ce mécanisme n'est pas universel.

Il faut vérifier :

- si le pilote le prend en charge ;
- si le système réseau possède un véritable commit-confirmed ou si le comportement est simulé ;
- comment le retour arrière est déclenché ;
- quelles limites s'appliquent ;
- comment vérifier l'état rétabli.

Ne supposez pas qu'une méthode `rollback()` ou `commit_config(revert_in=...)` garantit les mêmes propriétés sur toutes les plateformes.

## 14.4. Vérifier l'état après changement

Après un commit, relisez l'information concernée.

Par exemple, si vous avez modifié une description d'interface, récupérez l'état des interfaces et vérifiez que la description attendue est présente.

```python
interfaces = device.get_interfaces()

interface_name = "GigabitEthernet0/1"

if interface_name not in interfaces:
    raise RuntimeError("L'interface attendue est absente.")

actual_description = interfaces[interface_name].get(
    "description"
)

if actual_description != "LAB-UPLINK":
    raise RuntimeError(
        "La description n'est pas conforme à l'objectif."
    )
```

Le nom d'interface et le nom du champ doivent correspondre à la plateforme et à ce que renvoie le pilote. Ce fragment est donc une illustration de validation postérieure, pas une garantie de compatibilité universelle.

Le principe reste fondamental : un commit techniquement réussi doit être suivi de vérifications adaptées à l'objectif.


# 15. TESTER LES FONCTIONS SANS ÉQUIPEMENT RÉEL

Les tests sont essentiels pour rendre l'automatisation prévisible.

Certaines fonctions peuvent être testées sans connexion réseau : validation d'inventaire, sélection de cible, construction de rapports et interprétation des résultats.

## 15.1. Installer pytest

```bash
python -m pip install pytest
```

Lancer les tests :

```bash
python -m pytest -q
```

## 15.2. Tester le chargement de l'inventaire

`tests/test_validation.py` :

```python
import pytest


def validate_device_record(device: dict) -> None:
    required = {
        "name",
        "hostname",
        "driver",
        "enabled",
    }

    missing = required - device.keys()

    if missing:
        raise ValueError(
            f"Champs manquants : {sorted(missing)}"
        )

    if not isinstance(device["name"], str):
        raise ValueError("name doit être une chaîne.")

    if not isinstance(device["hostname"], str):
        raise ValueError("hostname doit être une chaîne.")

    if not isinstance(device["driver"], str):
        raise ValueError("driver doit être une chaîne.")

    if not isinstance(device["enabled"], bool):
        raise ValueError("enabled doit être un booléen.")


def test_valid_device_record():
    validate_device_record({
        "name": "router-lab-01",
        "hostname": "192.0.2.10",
        "driver": "ios",
        "enabled": True,
    })


def test_missing_driver_is_rejected():
    with pytest.raises(ValueError):
        validate_device_record({
            "name": "router-lab-01",
            "hostname": "192.0.2.10",
            "enabled": True,
        })


def test_enabled_must_be_boolean():
    with pytest.raises(ValueError):
        validate_device_record({
            "name": "router-lab-01",
            "hostname": "192.0.2.10",
            "driver": "ios",
            "enabled": "yes",
        })
```

Ce module montre les validations essentielles du modèle d'inventaire. Le programme réel doit les appeler avant d'ouvrir la moindre session.

## 15.3. Tester une fonction de contrôle d'interfaces

La logique de validation peut être testée avec des données fabriquées :

```python
def find_enabled_but_down(interfaces: dict) -> list[str]:
    return [
        name
        for name, data in interfaces.items()
        if (
            data.get("is_enabled") is True
            and data.get("is_up") is False
        )
    ]


def test_find_enabled_but_down():
    interfaces = {
        "Ethernet1": {
            "is_enabled": True,
            "is_up": False,
        },
        "Ethernet2": {
            "is_enabled": True,
            "is_up": True,
        },
        "Ethernet3": {
            "is_enabled": False,
            "is_up": False,
        },
    }

    assert find_enabled_but_down(interfaces) == [
        "Ethernet1",
    ]
```

Ce test vérifie une règle métier simple sans se connecter à un équipement.

Dans une application plus complète, vous devrez également gérer les champs absents, les données incorrectes et les interfaces qui sont volontairement inactives.

## 15.4. Tester la production de résumés

```python
def summarize_facts(facts: dict) -> dict:
    hostname = facts.get("hostname")
    interfaces = facts.get("interface_list")

    if not isinstance(hostname, str) or not hostname:
        raise ValueError("Hostname invalide.")

    if not isinstance(interfaces, list):
        raise ValueError("Liste d'interfaces invalide.")

    return {
        "hostname": hostname,
        "model": facts.get("model"),
        "os_version": facts.get("os_version"),
        "interface_count": len(interfaces),
    }
```

Le test peut vérifier que la fonction produit les bonnes données à partir d'un dictionnaire d'exemple, puis qu'elle rejette une entrée invalide.

## 15.5. Pourquoi les tests unitaires ne suffisent pas

Les tests unitaires démontrent que certaines fonctions se comportent comme prévu pour les données fournies.

Ils ne démontrent pas que le pilote fonctionne sur un équipement réel.

Il faudra donc compléter les tests locaux par des essais sur une plateforme autorisée, avec des versions logicielles documentées.

## 15.6. Les niveaux de test

| Niveau de test | Exemple | Matériel réel requis ? |
|---|---|---|
| Unitaire | Valider une entrée d'inventaire | Non |
| Fonctionnel local | Détecter une incohérence d'interface à partir de données fictives | Non |
| Test de pilote | Appeler `get_facts()` sur un appareil supporté | Oui, ou environnement simulé compatible |
| Test de configuration | Charger et comparer une candidate | Laboratoire réel recommandé |
| Test de récupération | Vérifier une restauration ou un commit confirmé | Laboratoire représentatif indispensable |
| Test d'exploitation | Collecter un groupe de cibles et examiner les résultats | Environnement contrôlé |


# 16. LABORATOIRES PROGRESSIFS

Les laboratoires sont conçus pour être réalisés dans l'ordre. Le code et les structures produits par un exercice seront réutilisés dans le suivant.

Ne sautez pas directement à la modification de configuration : les collectes et la validation doivent être comprises avant l'application d'un changement.

## Laboratoire 1 — Installer et vérifier NAPALM

**Objectif :** préparer un environnement reproductible.

Étapes :

1. vérifier la version de Python ;
2. créer un environnement virtuel ;
3. installer NAPALM ;
4. exécuter `pip show napalm` ;
5. exécuter `pip check` ;
6. noter la version installée ;
7. consulter la matrice du pilote à utiliser.

**Critères de réussite :**

- l'environnement est activé ;
- NAPALM est installé ;
- ses dépendances sont cohérentes ;
- le pilote choisi est documenté.

**Question :** pourquoi n'est-il pas suffisant de savoir que NAPALM est installé pour affirmer que toutes les méthodes fonctionneront sur votre équipement ?

## Laboratoire 2 — Sélectionner un pilote

**Objectif :** comprendre le rôle du pilote.

Étapes :

1. importer `get_network_driver` ;
2. sélectionner un pilote de laboratoire ;
3. afficher la classe retournée ;
4. consulter la documentation de ce pilote ;
5. relever ses prérequis ;
6. déterminer quel mécanisme de gestion il utilise.

**Critère :** vous pouvez expliquer pourquoi le nom du pilote doit correspondre à la plateforme et non être choisi arbitrairement.

## Laboratoire 3 — Connexion et `get_facts()`

**Objectif :** récupérer les informations générales d'un équipement.

Étapes :

1. obtenir l'adresse de laboratoire ;
2. fournir les identifiants de manière contrôlée ;
3. créer l'objet NAPALM ;
4. établir la connexion ;
5. appeler `get_facts()` ;
6. examiner les clés et les types ;
7. fermer correctement la session.

**Critères de réussite :**

- la connexion fonctionne ;
- les facts sont affichés ou enregistrés ;
- les erreurs sont visibles ;
- aucun mot de passe réel n'est enregistré ;
- la session est fermée après l'opération.

## Laboratoire 4 — Audit des interfaces

**Objectif :** récupérer les interfaces et distinguer état administratif et état opérationnel.

Étapes :

1. appeler `get_interfaces()` ;
2. parcourir le dictionnaire ;
3. afficher les descriptions ;
4. relever les interfaces opérationnellement inactives ;
5. distinguer les ports administrativement désactivés ;
6. comparer les résultats aux informations attendues du laboratoire.

**Critère :** le programme signale les états à examiner sans qualifier automatiquement toutes les interfaces down de pannes.

## Laboratoire 5 — IP et LLDP

**Objectif :** enrichir la collecte.

Étapes :

1. appeler `get_interfaces_ip()` ;
2. inspecter les adresses retournées ;
3. appeler `get_lldp_neighbors()` si la méthode est supportée ;
4. organiser les informations par équipement ;
5. documenter les données absentes ;
6. définir un statut précis si une méthode n'est pas disponible.

**Critère :** le programme sait distinguer une absence de voisin d'une erreur d'interrogation.

## Laboratoire 6 — Lire la configuration

**Objectif :** comprendre les configurations récupérables.

Étapes :

1. vérifier les permissions du compte ;
2. appeler `get_config()` ;
3. récupérer la source `running` si elle est supportée ;
4. vérifier que la chaîne obtenue est exploitable ;
5. sauvegarder dans un répertoire contrôlé ;
6. examiner les données sensibles susceptibles d'apparaître.

**Critère :** la sauvegarde est identifiable et protégée, et le rapport ne contient pas toute la configuration sans nécessité.

## Laboratoire 7 — Préparer une modification

**Objectif :** charger une configuration candidate sans l'appliquer immédiatement.

Étapes :

1. choisir une plateforme de laboratoire ;
2. écrire un fragment de configuration adapté ;
3. appeler `load_merge_candidate()` ;
4. examiner `compare_config()` ;
5. vérifier que le diff correspond à l'objectif ;
6. abandonner la candidate avec `discard_config()`.

**Critère :** vous savez inspecter et abandonner un changement sans appliquer une configuration non vérifiée.

## Laboratoire 8 — Appliquer et vérifier un changement simple

**Objectif :** comprendre le cycle complet d'une modification, dans un environnement isolé.

Préconditions :

- équipement de laboratoire ;
- sauvegarde préalable ;
- compte autorisé ;
- fragment de configuration compris ;
- procédure de retour arrière connue.

Étapes :

1. lire l'état initial ;
2. charger la candidate ;
3. examiner le diff ;
4. valider les préconditions ;
5. appliquer uniquement le changement approuvé ;
6. relire l'état ;
7. vérifier la valeur attendue ;
8. enregistrer le résultat.

**Critère :** aucun succès n'est déclaré avant le contrôle du résultat.

Si le pilote dispose d'un mécanisme de commit confirmé, étudiez-le séparément et vérifiez son comportement dans votre environnement.

## Laboratoire 9 — Audit de plusieurs cibles

**Objectif :** réutiliser une fonction pour plusieurs équipements.

Étapes :

1. créer un inventaire ;
2. vérifier les champs requis ;
3. sélectionner les cibles actives ;
4. collecter les facts séquentiellement ;
5. conserver un statut par cible ;
6. simuler une erreur sur une cible ;
7. vérifier que les résultats des autres sont conservés ;
8. générer un rapport JSON.

**Critère :** l'échec d'un équipement ne fait pas disparaître tout le rapport.

## Laboratoire 10 — Construire un outil réutilisable

**Objectif :** réunir les compétences du niveau Débutant.

L'application doit :

- charger l'inventaire ;
- valider les entrées ;
- sélectionner le pilote ;
- collecter les facts ;
- interroger les interfaces ;
- gérer les erreurs ;
- fermer les connexions ;
- produire un rapport ;
- éviter les secrets en clair ;
- documenter les prérequis de chaque plateforme.

**Livrable final :** code source, inventaire de laboratoire, exemples de résultats, tests locaux, rapport JSON et documentation de lancement.


# 17. PROJET FINAL — NAPALM NETWORK AUDITOR

## 17.1. Mission

Construire un petit outil nommé **NAPALM Network Auditor**.

Sa mission est de collecter des informations sur plusieurs équipements de laboratoire, de vérifier leur cohérence et de produire un rapport d'audit.

La première version doit être en lecture seule. Une extension de gestion des configurations peut être ajoutée après validation du système de collecte.

## 17.2. Architecture du projet

```text
napalm-network-auditor/
├── README.md
├── requirements-lock.txt
├── .gitignore
├── inventory/
│   └── devices.yaml
├── src/
│   └── auditor/
│       ├── inventory.py
│       ├── connection.py
│       ├── collect.py
│       ├── validation.py
│       └── reporting.py
├── tests/
│   ├── test_inventory.py
│   └── test_validation.py
└── reports/
```

## 17.3. Exigences fonctionnelles

Le programme doit :

1. lire l'inventaire ;
2. valider chaque équipement ;
3. ignorer les cibles désactivées ;
4. sélectionner le bon pilote ;
5. ouvrir et fermer les sessions ;
6. récupérer les facts ;
7. collecter les interfaces ;
8. distinguer erreurs et données manquantes ;
9. compter les interfaces ;
10. identifier les interfaces à examiner ;
11. conserver un résultat par cible ;
12. générer un rapport JSON.

## 17.4. Exemple de rapport attendu

```json
{
  "schema_version": 1,
  "run_id": "NAPALM-LAB-001",
  "operation": "network_audit",
  "summary": {
    "total": 3,
    "success": 2,
    "failed": 1,
    "skipped": 0
  },
  "devices": [
    {
      "name": "router-lab-01",
      "status": "success",
      "facts_valid": true,
      "interface_count": 12,
      "interfaces_requiring_review": 1
    },
    {
      "name": "router-lab-02",
      "status": "success",
      "facts_valid": true,
      "interface_count": 8,
      "interfaces_requiring_review": 0
    },
    {
      "name": "router-lab-03",
      "status": "failed",
      "error_category": "connection"
    }
  ]
}
```

Les valeurs sont fictives. Le programme devra produire ses propres résultats à partir de l'inventaire et des données collectées.

## 17.5. Exigences de qualité

Le code doit :

- être organisé en fonctions ;
- valider les données d'entrée ;
- éviter les mots de passe dans les fichiers ;
- utiliser le gestionnaire de contexte lorsque cela convient ;
- fermer toutes les connexions ;
- retourner des statuts cohérents ;
- ne pas traiter un échec comme un dictionnaire vide normal ;
- produire des rapports lisibles ;
- documenter les pilotes et les limitations ;
- inclure des tests unitaires.

## 17.6. Barème d'évaluation sur 100 points

| Domaine | Points |
|---|---:|
| Installation et environnement | 10 |
| Inventaire et sélection des cibles | 12 |
| Choix du pilote | 10 |
| Gestion des connexions | 12 |
| Collecte des facts | 12 |
| Collecte et validation des interfaces | 12 |
| Gestion des erreurs | 12 |
| Rapport JSON | 10 |
| Tests et documentation | 10 |
| **Total** | **100** |

Un projet ne devrait pas être considéré comme réussi si :

- des mots de passe sont codés en dur ;
- les erreurs sont silencieusement ignorées ;
- les sessions ne sont pas fermées ;
- le pilote sélectionné n'est pas compatible avec les équipements ;
- les rapports déclarent un succès sans vérifier les données essentielles.


# 18. DÉPANNAGE

## 18.1. NAPALM ne s'installe pas

Vérifiez :

- la version de Python ;
- l'environnement virtuel ;
- les messages du gestionnaire de dépendances ;
- les prérequis spécifiques au pilote ;
- les contraintes du système d'exploitation.

Utilisez une version de Python compatible avec la version de NAPALM choisie, puis vérifiez la documentation officielle. La version 5.2.0 que nous avons vérifiée requiert Python 3.10 ou supérieur. <Cite refs={["turn568966search3","turn568966search1"]}/>

## 18.2. Le pilote n'est pas reconnu

Vérifiez le nom exact transmis à `get_network_driver()` et la version installée.

Ne supposez pas que le constructeur ou la famille commerciale est automatiquement le nom du pilote.

Consultez la liste officielle des pilotes et la documentation de compatibilité.

## 18.3. La connexion échoue

Examinez successivement :

1. l'adresse de gestion ;
2. la connectivité réseau ;
3. le service de gestion et le transport attendu ;
4. le nom d'utilisateur ;
5. le mécanisme d'authentification ;
6. les permissions du compte ;
7. les prérequis du système ;
8. les paramètres optionnels du pilote.

Une connexion SSH fonctionnelle ne garantit pas que chaque mécanisme d'accès utilisé par NAPALM est correctement configuré.

## 18.4. `get_facts()` retourne une erreur

Le problème peut provenir de la session, du pilote, de la version logicielle, de la méthode de collecte ou d'un prérequis manquant.

Vérifiez si le pilote est compatible avec le système et si ses prérequis sont satisfaits.

Testez d'abord une seule cible avant d'étendre le script à plusieurs appareils.

## 18.5. Une méthode n'est pas supportée

La matrice NAPALM distingue les méthodes supportées selon les pilotes. Une méthode peut fonctionner sur IOS et ne pas être disponible sous la même forme sur un autre pilote. <Cite refs={["turn591003view4","turn591003view2"]}/>

La bonne démarche est :

1. identifier le pilote exact ;
2. consulter sa matrice ;
3. regarder les éventuelles limitations ;
4. déterminer si une autre méthode répond au besoin ;
5. définir clairement les cas non supportés dans le code.

Il ne faut pas considérer l'absence de données comme un résultat vide normal si l'opération a réellement échoué.

## 18.6. Les données retournées diffèrent de l'exemple

Les exemples de ce document sont illustratifs.

Comparez le résultat réel à la documentation de la méthode. Vérifiez les champs disponibles, leurs types et les limites de la version.

Évitez de coder des hypothèses sur les valeurs ou l'ordre des clés d'un dictionnaire.

## 18.7. `get_config()` n'obtient pas la configuration attendue

Vérifiez le droit de lecture, le nom de la source demandé et la prise en charge du pilote.

Certaines plateformes peuvent présenter des contraintes sur les sources de configuration et les opérations disponibles. La matrice et les avertissements propres au pilote doivent être consultés.

## 18.8. `compare_config()` ne montre pas le diff attendu

Vérifiez que la candidate a bien été chargée, que sa syntaxe est valide pour la plateforme et que le pilote fournit une comparaison compatible avec cette opération.

Un diff vide signifie qu'aucune différence n'a été signalée par le mécanisme de comparaison pour cette opération. Il ne constitue pas une preuve universelle que le service est conforme à l'objectif métier.

## 18.9. `commit_config()` échoue

Vérifiez les permissions de configuration, le mode de gestion, la validité de la candidate et les particularités du système.

Ne relancez pas aveuglément le commit après une erreur de transport sans déterminer si l'opération a pu être appliquée.

Relisez l'état et consultez les journaux appropriés avant toute nouvelle tentative.

## 18.10. Une opération de retour arrière n'est pas disponible

Le rollback dépend du pilote et de la plateforme.

Il faut vérifier si la fonction est supportée, si elle est simulée ou si elle s'appuie sur un mécanisme natif du système.

N'utilisez pas une procédure universelle supposée fonctionner sur chaque équipement. Testez le cycle de changement et de récupération dans le laboratoire.


# 19. EXERCICES D'ÉVALUATION

Répondez à ces questions sans simplement recopier les définitions.

1. Que signifie NAPALM ?
2. Quel problème l'API commune de NAPALM cherche-t-elle à simplifier ?
3. Qu'est-ce qu'un pilote ?
4. Pourquoi `get_network_driver("ios")` ne convient-il pas automatiquement à tout équipement Cisco ?
5. Que fait la méthode `open()` ?
6. Pourquoi utiliser `close()` dans un `finally` ou un gestionnaire de contexte ?
7. Quelles informations peut-on obtenir avec `get_facts()` ?
8. Quelle différence existe entre `get_facts()` et `get_interfaces()` ?
9. Pourquoi une interface peut-elle être administrativement activée mais opérationnellement inactive ?
10. Que peut apporter `get_interfaces_ip()` ?
11. Quelle différence existe entre l'état d'une interface et une table de voisins LLDP ?
12. Pourquoi faut-il protéger les configurations récupérées par `get_config()` ?
13. Quelle différence existe entre `load_merge_candidate()` et `load_replace_candidate()` ?
14. À quoi sert `compare_config()` ?
15. Quelle différence existe entre charger une candidate et appliquer un commit ?
16. Pourquoi le comportement d'un rollback ne doit-il pas être supposé identique sur tous les pilotes ?
17. Pourquoi une erreur de collecte ne doit-elle pas être remplacée par un dictionnaire vide ?
18. Comment conserver les résultats de plusieurs équipements lorsqu'un seul échoue ?
19. Pourquoi est-il préférable de commencer avec une collecte séquentielle ?
20. Comment vérifier que le changement réellement appliqué correspond à l'objectif attendu ?

## Mini-projet de synthèse

Vous devez créer un outil qui :

- interroge deux équipements de laboratoire ;
- récupère leur nom et leur version ;
- compte les interfaces ;
- identifie les interfaces à examiner ;
- génère un rapport JSON ;
- conserve un statut séparé pour chaque équipement.

Le programme doit continuer la collecte du second équipement si le premier échoue.

Une fois ce résultat obtenu, vous disposerez des bases nécessaires pour aborder le niveau Intermédiaire : validation plus poussée, inventaires structurés, concurrence contrôlée et workflow de modification plus robuste.


# 20. GLOSSAIRE

**API** — Interface qui permet à un logiciel d'interagir avec un autre système.

**Candidat de configuration** — Configuration préparée pour comparaison et application éventuelle.

**Commit** — Opération qui applique une configuration candidate selon le comportement du pilote et de la plateforme.

**Driver / pilote** — Composant qui adapte l'API NAPALM à un système réseau particulier.

**Faits / facts** — Informations générales sur l'équipement, telles que la version, le modèle et le nom d'hôte.

**Getter** — Méthode de collecte permettant de lire certaines informations structurées.

**LLDP** — Protocole de découverte de voisins de couche 2.

**Merge** — Fusion d'une configuration préparée avec la configuration existante selon le mécanisme supporté.

**NAPALM** — *Network Automation and Programmability Abstraction Layer with Multivendor support*.

**NetDevOps** — Approche associant développement logiciel, tests et exploitation réseau.

**Rollback** — Retour à un état antérieur selon les mécanismes disponibles et les procédures définies.

**Remplacement de configuration** — Opération destinée à remplacer la configuration ciblée, selon la sémantique du pilote.

**Validation** — Contrôle permettant de vérifier que les données ou l'état répondent à des critères définis.


# 21. RÉFÉRENCES OFFICIELLES

Consultez la documentation de la version installée avant de développer un workflow d'exploitation.

## Projet et installation

- **NAPALM sur PyPI**  
  https://pypi.org/project/napalm/

- **Dépôt officiel NAPALM**  
  https://github.com/napalm-automation/napalm

- **Documentation officielle**  
  https://napalm.readthedocs.io/en/latest/

- **Installation**  
  https://napalm.readthedocs.io/en/latest/installation/

## Utilisation de base

- **Tutoriels NAPALM**  
  https://napalm.readthedocs.io/en/latest/tutorials/

- **Programmation et exemples**  
  https://napalm.readthedocs.io/en/latest/tutorials/samples.html

- **Gestion du contexte**  
  https://napalm.readthedocs.io/en/latest/tutorials/context_manager.html

- **API NetworkDriver**  
  https://napalm.readthedocs.io/en/latest/base.html

## Compatibilité

- **Matrice des équipements supportés**  
  https://napalm.readthedocs.io/en/latest/support/

- **Pilotes et limites IOS**  
  https://napalm.readthedocs.io/en/latest/support/ios.html

- **Pilote Arista EOS**  
  https://napalm.readthedocs.io/en/latest/support/eos.html

- **Validation des déploiements**  
  https://napalm.readthedocs.io/en/latest/validate/

## Gestion des configurations

- **Tutoriel de modification de configuration**  
  https://napalm.readthedocs.io/en/latest/tutorials/changing_the_config.html

- **API NetworkDriver et méthodes de configuration**  
  https://napalm.readthedocs.io/en/latest/base.html

Les liens de documentation peuvent évoluer avec les versions. Si une page présente des différences avec votre installation, vérifiez la documentation liée à la release utilisée et les éventuelles limitations du pilote.


# CONCLUSION — LES FONDATIONS DU PARCOURS NAPALM

Dans ce niveau Débutant, vous avez appris à installer NAPALM, sélectionner un pilote, ouvrir une connexion, collecter des facts, inspecter les interfaces et examiner certaines informations réseau.

Vous avez également découvert comment charger une configuration candidate, comparer un diff, distinguer l'abandon de l'application d'un changement et comprendre pourquoi les capacités de gestion varient selon les plateformes.

Vous disposez maintenant des fondations nécessaires pour construire un premier outil d'audit réseau.

La prochaine étape consiste à faire évoluer les exemples en fonctions réutilisables, à valider plus rigoureusement l'inventaire, à mieux classer les erreurs, à traiter plusieurs équipements, à contrôler les données et à structurer les rapports.

C'est le rôle du niveau Intermédiaire.

Le niveau Expert s'appuiera ensuite sur ces mêmes méthodes pour traiter les workflows de changement, les tests avancés, la gouvernance et l'exploitation à grande échelle.

Retenez ces cinq règles :

1. **Choisir un pilote compatible avec la plateforme réelle.**
2. **Fermer proprement chaque connexion.**
3. **Contrôler les données retournées au lieu de supposer qu'elles sont complètes.**
4. **Comparer et vérifier une configuration avant de l'appliquer.**
5. **Ne jamais considérer une opération comme réussie sans avoir contrôlé le résultat attendu.**

NAPALM réduit une partie de la complexité des opérations multi-constructeurs. C'est la compréhension du pilote, des données, des limites et du résultat qui transforme cette bibliothèque en outil d'automatisation fiable.

**Objectif du niveau Débutant : passer d'une intervention manuelle à un premier programme NAPALM capable de collecter des informations de manière structurée et vérifiable.**