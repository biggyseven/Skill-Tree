# Scripting réseau avec Python et Netmiko — Niveau intermédiaire

> **Encadré de mise en contexte**
>
> **Niveau :** Intermédiaire  
> **Place dans la série :** ce cours est la suite directe du fichier `netmiko-debutant.md` (niveau Débutant). Il suppose que tu sais déjà créer un environnement Python, installer Netmiko, établir une session SSH, appeler `send_command()`, parcourir une liste d'équipements et sauvegarder du texte. Ces gestes ne sont pas réenseignés depuis zéro : ils sont assemblés en une application mieux conçue, testable, mesurable et plus sûre. Le niveau Expert reprendra cette base pour aborder l'orchestration de changements, le traitement avancé des états et l'intégration aux systèmes d'exploitation réseau.
>
> **Prérequis concrets :** avoir réalisé le script de collecte du niveau Débutant, comprendre les listes, dictionnaires, fonctions, `try/except`, fichiers JSON/CSV et fermeture de session. Les annotations de type utilisant `str | None` supposent Python 3.10 ou ultérieur ; adapte-les si ton environnement utilise une version plus ancienne. Un équipement de laboratoire autorisé est recommandé ; une grande partie des exercices s'exécute toutefois sans connexion réelle.
>
> **Objectif du cours :** produire un collecteur multi-équipements organisé en modules, capable de lire un inventaire versionné, de garder les secrets à part, d'exécuter des commandes de lecture seule, de transformer les réponses CLI en données structurées, de valider ces données, d'émettre des rapports fiables et de tester les erreurs. Une introduction aux changements contrôlés est incluse, mais le projet principal ne modifie pas la configuration.
>
> **Fil pédagogique :** reprendre → structurer → parser → valider → paralléliser prudemment → tester → observer → préparer le changement contrôlé.
>
> **Sécurité :** exécute les exemples de connexion uniquement sur les équipements auxquels tu es autorisé à accéder. Les adresses `192.0.2.0/24` utilisées ici sont des adresses de documentation et doivent être remplacées par les cibles de ton laboratoire. Les exemples de configuration restent illustratifs et ne doivent pas être exécutés sur une infrastructure de production sans changement approuvé.

## 1. Ce qui change entre le niveau débutant et le niveau intermédiaire

Au niveau Débutant, le succès consiste à établir une session, exécuter une commande, afficher sa réponse et fermer proprement la connexion. Ce premier jalon est essentiel : tant qu'on ne comprend pas la relation entre Python, la session SSH et l'invite du CLI, il est prématuré de construire des automatismes complexes. Mais dès que ce geste fonctionne sur plusieurs équipements, de nouvelles questions apparaissent. Où placer l'inventaire ? Comment éviter de dupliquer les paramètres ? Comment savoir qu'une sortie a réellement été comprise ? Comment comparer les appareils entre eux ? Comment garantir qu'un timeout sur une cible ne fait pas perdre tous les résultats des autres ? Comment tester un parseur sans se connecter à un routeur à chaque modification ?

Le niveau intermédiaire répond à ces questions. Le changement principal n'est pas une méthode Netmiko spectaculaire ; c'est une architecture et une méthode. Le code cesse d'être un script unique rempli de paramètres, de boucles et de `print()`. Il devient un outil possédant des entrées définies, des fonctions à responsabilité claire, un format de résultat cohérent, une politique d'erreur et un rapport exploitable.

Le mot **fiable** doit être compris précisément. Une exécution fiable ne signifie pas que tous les équipements répondent toujours. Dans un réseau réel, certains appareils peuvent être indisponibles, en maintenance ou temporairement lents. La fiabilité signifie plutôt que chaque cas reçoit un état honnête, que les erreurs sont isolées, que le programme termine ou s'arrête selon une règle connue, et qu'un autre opérateur peut comprendre ce qui s'est passé.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 530" role="img" aria-labelledby="d1title d1desc" width="1200" height="530">
<title id="d1title">Une série progressive, pas trois cours isolés</title><desc id="d1desc">Chaque niveau réutilise les acquis et augmente la rigueur du livrable.</desc>
<defs><linearGradient id="d1bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d1arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d1h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d1sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d1title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d1body{font:14px system-ui,sans-serif;fill:#dbeafe}.d1edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d1arrow);animation:d1move 1.2s linear infinite}@keyframes d1move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d1edge{animation:none}}</style></defs>
<rect width="1200" height="530" rx="24" fill="url(#d1bg)"/><text x="42" y="48" class="d1h">Une série progressive, pas trois cours isolés</text><text x="42" y="77" class="d1sub">Chaque niveau réutilise les acquis et augmente la rigueur du livrable.</text><path class="d1edge" d="M378 245 L425 245"/><path class="d1edge" d="M765 245 L812 245"/><rect x="48" y="132" width="330" height="235" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="67" y="162" class="d1title">01 · Débutant</text><text x="67" y="194" class="d1body">Session SSH et commandes</text><text x="67" y="216" class="d1body">Liste d’équipements</text><text x="67" y="238" class="d1body">Fichiers de sortie</text><text x="67" y="260" class="d1body">Exceptions de base</text><text x="67" y="282" class="d1body">Acquis : une collecte fonctionne</text><rect x="435" y="132" width="330" height="235" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="454" y="162" class="d1title">02 · Intermédiaire</text><text x="454" y="194" class="d1body">Inventaire et secrets séparés</text><text x="454" y="216" class="d1body">Parsing et validation</text><text x="454" y="238" class="d1body">Rapports et tests</text><text x="454" y="260" class="d1body">Concurrence limitée</text><text x="454" y="282" class="d1body">Résultat : outil maintenable</text><rect x="822" y="132" width="330" height="235" rx="15" fill="#334155" stroke="#a5b4fc" stroke-width="2"/><text x="841" y="162" class="d1title">03 · Expert</text><text x="841" y="194" class="d1body">Orchestration robuste</text><text x="841" y="216" class="d1body">Transactions et rollback</text><text x="841" y="238" class="d1body">Observabilité approfondie</text><text x="841" y="260" class="d1body">Intégration aux systèmes</text><text x="841" y="282" class="d1body">Résultat : changement maîtrisé</text></svg>



### 1.1 Le contrat de résultat remplace le simple affichage

Au lieu que chaque branche imprime un message différent, établis un petit contrat commun. Chaque équipement produit un enregistrement contenant au minimum : son nom logique, son adresse, la date de collecte, l'état de l'opération, les commandes tentées, les commandes réussies, les avertissements et la durée. La sortie brute peut être enregistrée séparément parce qu'elle peut être volumineuse ou contenir des éléments sensibles. Le rapport synthétique ne doit pas forcer un opérateur à ouvrir vingt fichiers pour découvrir quels appareils ont échoué.

Voici un exemple de forme logique :

```python
{
    "device": "access-sw-01",
    "host": "192.0.2.11",
    "status": "partial",
    "started_at": "2026-10-23T19:40:00+00:00",
    "duration_seconds": 2.84,
    "commands_total": 3,
    "commands_ok": 2,
    "warnings": ["Parser sans résultat sur show inventory"],
    "errors": []
}
```

L'heure ci-dessus n'est qu'un exemple. Le format ISO 8601 avec fuseau rend le champ non ambigu. L'état `partial` évite le faux choix entre succès complet et échec total : un équipement peut avoir répondu à deux commandes et échoué à la troisième. Les catégories doivent rester cohérentes d'une exécution à l'autre pour permettre les comparaisons.

### 1.2 Les responsabilités à séparer

- **Inventaire :** décrit l'identité, la plateforme, le site, le rôle et les groupes d'un appareil. Il n'inclut pas de mot de passe.
- **Connexion :** ouvre la session avec les paramètres attendus et la ferme dans un bloc `finally`.
- **Collecte :** choisit les commandes autorisées et conserve le texte brut.
- **Parsing :** transforme le texte dans un format structuré, sans s'occuper de la connexion.
- **Validation :** vérifie que le résultat a une forme et des valeurs plausibles.
- **Rapport :** regroupe les résultats et les écrit en JSON, CSV ou autre format adapté.
- **Orchestration :** coordonne l'ordre, les arguments, les limites de concurrence et le code de sortie.

Ce découpage ne signifie pas qu'il faille immédiatement créer un grand framework de quinze fichiers. Pour un petit projet, quelques modules suffisent. L'objectif est que les responsabilités restent lisibles, que les tests soient abordables et qu'une évolution ne force pas à modifier tout le programme.

## 2. Architecture minimale d'un projet maintenable

Un script monolithique semble simple lorsqu'il tient dans une page. Au fur et à mesure qu'on ajoute les délais, les parseurs, les rapports, les tests et les erreurs, ce même script devient fragile : une modification du format d'export peut toucher la connexion, un changement d'inventaire peut altérer le parsing, et un correctif de timeout peut casser la sauvegarde. La séparation des responsabilités réduit cette propagation.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 620" role="img" aria-labelledby="d3title d3desc" width="1200" height="620">
<title id="d3title">Séparer les responsabilités pour tester chaque partie</title><desc id="d3desc">Le programme principal orchestre les modules ; il ne contient pas tous les détails.</desc>
<defs><linearGradient id="d3bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d3arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d3h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d3sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d3title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d3body{font:14px system-ui,sans-serif;fill:#dbeafe}.d3edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d3arrow);animation:d3move 1.2s linear infinite}@keyframes d3move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d3edge{animation:none}}</style></defs>
<rect width="1200" height="620" rx="24" fill="url(#d3bg)"/><text x="42" y="48" class="d3h">Séparer les responsabilités pour tester chaque partie</text><text x="42" y="77" class="d3sub">Le programme principal orchestre les modules ; il ne contient pas tous les détails.</text><path class="d3edge" d="M600 182 L600 208"/><path class="d3edge" d="M600 208 L192 226"/><path class="d3edge" d="M600 208 L600 226"/><path class="d3edge" d="M600 208 L1008 226"/><path class="d3edge" d="M600 331 L192 382"/><path class="d3edge" d="M600 331 L600 382"/><path class="d3edge" d="M600 331 L1008 382"/><rect x="430" y="110" width="340" height="72" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="449" y="140" class="d3title">main.py · Orchestration</text><text x="449" y="172" class="d3body">Arguments, plan, synthèse</text><rect x="42" y="226" width="300" height="105" rx="15" fill="#334155" stroke="#cbd5e1" stroke-width="2"/><text x="61" y="256" class="d3title">Inventaire</text><text x="61" y="288" class="d3body">Cibles et plateforme</text><text x="61" y="310" class="d3body">Aucun secret en clair</text><rect x="450" y="226" width="300" height="105" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="469" y="256" class="d3title">collector.py</text><text x="469" y="288" class="d3body">Connexion et commandes</text><text x="469" y="310" class="d3body">Résultat par équipement</text><rect x="858" y="226" width="300" height="105" rx="15" fill="#3f365f" stroke="#c4b5fd" stroke-width="2"/><text x="877" y="256" class="d3title">Settings / secrets</text><text x="877" y="288" class="d3body">Timeouts, variables</text><text x="877" y="310" class="d3body">Confiance des clés SSH</text><rect x="42" y="382" width="300" height="105" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="61" y="412" class="d3title">parser.py</text><text x="61" y="444" class="d3body">Texte vers données typées</text><text x="61" y="466" class="d3body">Fixtures de test</text><rect x="450" y="382" width="300" height="105" rx="15" fill="#23344a" stroke="#93a4b8" stroke-width="2"/><text x="469" y="412" class="d3title">validator.py</text><text x="469" y="444" class="d3body">Contrôles métier</text><text x="469" y="466" class="d3body">Avertissements utiles</text><rect x="858" y="382" width="300" height="105" rx="15" fill="#1e3a8a" stroke="#7eb5ff" stroke-width="2"/><text x="877" y="412" class="d3title">reporter.py / logs</text><text x="877" y="444" class="d3body">JSON, CSV, durées</text><text x="877" y="466" class="d3body">Pas de secrets journalisés</text></svg>



### 2.1 Organisation de dossiers suggérée

```text
netmiko-intermediaire/
├── inventory/
│   └── devices.json
├── src/
│   └── netops/
│       ├── __init__.py
│       ├── inventory.py
│       ├── collector.py
│       ├── parser.py
│       ├── validator.py
│       └── reporter.py
├── tests/
│   ├── fixtures/
│   │   ├── show_ip_interface_brief.txt
│   │   └── show_ip_interface_brief.json
│   ├── test_parser.py
│   └── test_validator.py
├── output/
├── logs/
├── main.py
├── README.md
└── requirements.txt
```

Il n'est pas indispensable de créer immédiatement le paquet `src/netops`. On peut commencer avec `collector.py`, `parser.py` et `main.py`. Ce qui compte, c'est le principe : les entrées sont clairement définies, les fonctions ont une responsabilité compréhensible et les sorties ont un format stable.

`output/` contient les rapports et les extraits de collecte. `logs/` contient les événements d'exécution. Ces deux types de données ne sont pas interchangeables. Les journaux racontent les étapes du programme ; les fichiers de résultats conservent les données collectées. Leur politique de conservation et leurs permissions peuvent être différentes.

### 2.2 Le programme principal doit rester court

Le fichier principal a idéalement cette forme logique : charger les arguments, lire et valider l'inventaire, préparer les paramètres, lancer les collectes, écrire les résultats puis calculer un code de sortie. Il ne devrait pas contenir l'intégralité des regex d'un constructeur ou le code spécifique à une colonne CSV.

```python
def main() -> int:
    """Point d'entrée : valider, collecter, rapporter et retourner un statut."""
    devices = load_inventory("inventory/devices.json")
    validate_inventory(devices)
    results = collect_fleet(devices)
    write_reports(results, output_dir="output")
    return summarize_exit_code(results)


if __name__ == "__main__":
    raise SystemExit(main())
```

Les fonctions appelées seront développées dans les sections suivantes. Cette forme rend le déroulement compréhensible avant même d'en connaître les détails. `raise SystemExit(main())` permet de communiquer un statut au shell : zéro peut signifier que la collecte s'est terminée selon les critères de succès définis, tandis qu'un statut non nul peut indiquer des erreurs. Il faut définir cette politique explicitement et ne pas retourner zéro simplement parce que le processus Python a atteint la dernière ligne.

## 3. Inventaire piloté par les données

Lorsque les paramètres de chaque routeur sont écrits à la main dans le code, chaque changement de nom, d'adresse ou de rôle nécessite une modification du script. Un inventaire externe sépare les données propres au réseau de la logique du programme. JSON est un bon point de départ : la bibliothèque `json` est intégrée à Python, et sa structure peut contenir listes, dictionnaires, chaînes, nombres, booléens et valeurs nulles.

### 3.1 Exemple d'inventaire JSON

Crée `inventory/devices.json` :

```json
{
  "devices": [
    {
      "name": "core-rtr-01",
      "host": "192.0.2.11",
      "device_type": "cisco_ios",
      "site": "campus-nord",
      "role": "core",
      "enabled": true,
      "commands": ["show version", "show ip interface brief"]
    },
    {
      "name": "access-sw-02",
      "host": "192.0.2.12",
      "device_type": "cisco_ios",
      "site": "campus-nord",
      "role": "access",
      "enabled": true,
      "commands": ["show version", "show interfaces status"]
    }
  ]
}
```

Les noms de commandes restent spécifiques à l'OS : ne recopie pas automatiquement les commandes d'un équipement vers une autre plateforme. L'inventaire doit refléter les commandes réellement approuvées pour le groupe et le type d'appareil. La propriété `enabled` fournit un contrôle explicite : un équipement présent dans le fichier n'est pas nécessairement autorisé à être interrogé lors de chaque exécution.

La valeur `device_type` doit correspondre à un type pris en charge par la version de Netmiko installée. L'adresse d'exemple est réservée à la documentation et ne désigne pas un hôte réel. En laboratoire, remplace-la par une adresse autorisée et vérifie que le nom du pilote est approprié.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 530" role="img" aria-labelledby="d4title d4desc" width="1200" height="530">
<title id="d4title">Les paramètres et les secrets n’ont pas le même rôle</title><desc id="d4desc">L’inventaire doit pouvoir être partagé et contrôlé sans divulguer de mot de passe.</desc>
<defs><linearGradient id="d4bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d4arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d4h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d4sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d4title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d4body{font:14px system-ui,sans-serif;fill:#dbeafe}.d4edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d4arrow);animation:d4move 1.2s linear infinite}@keyframes d4move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d4edge{animation:none}}</style></defs>
<rect width="1200" height="530" rx="24" fill="url(#d4bg)"/><text x="42" y="48" class="d4h">Les paramètres et les secrets n’ont pas le même rôle</text><text x="42" y="77" class="d4sub">L’inventaire doit pouvoir être partagé et contrôlé sans divulguer de mot de passe.</text><path class="d4edge" d="M358 220 L435 220"/><path class="d4edge" d="M755 220 L832 220"/><path class="d4edge" d="M600 315 L600 355"/><rect x="48" y="130" width="310" height="185" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="67" y="160" class="d4title">Inventaire JSON</text><text x="67" y="192" class="d4body">name : access-sw-01</text><text x="67" y="214" class="d4body">host : 192.0.2.11</text><text x="67" y="236" class="d4body">device_type : cisco_ios</text><text x="67" y="258" class="d4body">site : campus-nord</text><rect x="445" y="130" width="310" height="185" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="464" y="160" class="d4title">Politique du script</text><text x="464" y="192" class="d4body">conn_timeout : 8 s</text><text x="464" y="214" class="d4body">read_timeout : 30 s</text><text x="464" y="236" class="d4body">Clé d’hôte obligatoire</text><text x="464" y="258" class="d4body">Travailleurs limités</text><rect x="842" y="130" width="310" height="185" rx="15" fill="#4b2833" stroke="#fda4af" stroke-width="2"/><text x="861" y="160" class="d4title">Secrets séparés</text><text x="861" y="192" class="d4body">NETMIKO_USERNAME</text><text x="861" y="214" class="d4body">NETMIKO_PASSWORD</text><text x="861" y="236" class="d4body">Coffre de secrets</text><text x="861" y="258" class="d4body">Jamais dans Git</text><rect x="268" y="365" width="664" height="92" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="287" y="395" class="d4title">Paramètres assemblés en mémoire</text><text x="287" y="427" class="d4body">Cible + plateforme + délais + identifiants + confiance SSH</text></svg>



### 3.2 Charger puis valider l'inventaire

Le fait qu'un fichier JSON soit syntaxiquement valide ne signifie pas que son contenu soit utilisable. Il peut manquer `host`, contenir une liste de commandes à la place d'une chaîne ou déclarer la même cible deux fois. Vérifie la forme des données avant d'ouvrir la moindre session SSH.

```python
import json
from pathlib import Path
from typing import Any


def load_inventory(path: str) -> list[dict[str, Any]]:
    """Charge un inventaire JSON et renvoie la liste des appareils activés."""
    inventory_path = Path(path)
    with inventory_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    if not isinstance(document, dict):
        raise ValueError("La racine JSON doit être un objet.")

    devices = document.get("devices")
    if not isinstance(devices, list):
        raise ValueError("Le champ 'devices' doit être une liste.")

    enabled_devices = []
    seen_names = set()
    seen_hosts = set()

    for index, device in enumerate(devices):
        if not isinstance(device, dict):
            raise ValueError(f"L'entrée devices[{index}] doit être un objet.")
        for field in ("name", "host", "device_type"):
            value = device.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"devices[{index}].{field} doit être une chaîne non vide.")
        commands = device.get("commands", [])
        if not isinstance(commands, list) or not all(
            isinstance(command, str) and command.strip() for command in commands
        ):
            raise ValueError(f"Liste de commandes invalide pour {device['name']}.")
        if device["name"] in seen_names:
            raise ValueError(f"Nom dupliqué : {device['name']}")
        if device["host"] in seen_hosts:
            raise ValueError(f"Adresse dupliquée : {device['host']}")
        seen_names.add(device["name"])
        seen_hosts.add(device["host"])
        if device.get("enabled", True):
            enabled_devices.append(device)

    return enabled_devices
```

Ce contrôle est volontairement simple. Dans une application plus grande, tu peux ajouter des règles : autoriser uniquement certaines plateformes, exiger un nom de site, limiter les caractères des noms de fichier et bloquer les commandes non approuvées. Une validation d'inventaire doit expliquer quelle entrée est invalide et quel champ pose problème, afin que le correctif soit rapide.

### 3.3 Préparer des groupes de commandes sans dupliquer le programme

Un équipement de cœur, un commutateur d'accès et un pare-feu n'ont pas toujours les mêmes commandes de vérification. On peut définir des profils de collecte, par exemple `baseline_ios`, `edge_switch` ou `firewall_readonly`, puis faire pointer les équipements vers le profil approprié. Cette approche est préférable à une longue cascade `if device_type == ...` dispersée dans le script.

Ne fais pas dépendre l'inventaire d'un système de règles tellement complexe qu'il devient difficile de savoir quelles commandes seront exécutées. Pour ce niveau, un groupe nommé avec des listes visibles est suffisant. Chaque commande doit pouvoir être examinée avant l'exécution.

### 3.4 Choisir entre JSON et YAML

JSON suffit pour le cours et ne demande aucun paquet supplémentaire. YAML peut être plus confortable pour des inventaires volumineux ou hiérarchiques, mais il nécessite une bibliothèque de chargement, une convention d'équipe et une vigilance particulière sur les types interprétés. Netmiko rend certaines dépendances optionnelles ; ne suppose donc pas qu'un paquet accessoire est installé avec la bibliothèque de base. Le format le plus utile est celui que l'équipe peut valider, relire et maintenir correctement.

## 4. Identifiants, clés SSH et politique de confiance

Le niveau Débutant a présenté les paramètres de connexion. Ici, on les assemble sans confondre inventaire et secret. Les identifiants peuvent provenir d'un gestionnaire de secrets, de variables d'environnement ou d'une saisie interactive pour un laboratoire. Ils ne doivent pas être ajoutés dans le JSON de l'inventaire, dans les captures d'écran, dans Git ou dans les journaux.

### 4.1 Variables d'environnement et saisie masquée

```python
import os
from getpass import getpass


def load_credentials() -> tuple[str, str]:
    """Lit les identifiants hors du code, en demandant le mot de passe si nécessaire."""
    username = os.environ.get("NETMIKO_USERNAME", "").strip()
    if not username:
        username = input("Nom d'utilisateur réseau : ").strip()

    password = os.environ.get("NETMIKO_PASSWORD")
    if password is None:
        password = getpass("Mot de passe réseau : ")

    if not username or not password:
        raise ValueError("Les identifiants ne peuvent pas être vides.")
    return username, password
```

Les variables d'environnement réduisent la probabilité d'inscrire un secret dans le code, mais elles ne constituent pas à elles seules un coffre-fort. Un processus lancé avec des variables sensibles peut être inspecté par des acteurs disposant de privilèges suffisants ; l'environnement d'exécution, les permissions du système et le gestionnaire de secrets restent importants. Pour un processus non interactif, prévois un fournisseur de secrets adapté et un mécanisme de rotation.

### 4.2 Vérification des clés d'hôte

Les clés SSH permettent au client de vérifier l'identité cryptographique de l'hôte auquel il se connecte. L'option `ssh_strict=True` de Netmiko permet de rejeter une clé inconnue, et `system_host_keys=True` demande l'utilisation du fichier de clés d'hôtes connu du système. Le comportement exact dépend aussi du fichier `known_hosts`, de la version installée et des paramètres choisis. Consulte la documentation de la version exécutée.

Pour un environnement contrôlé, la séquence recommandée est : obtenir la clé du périphérique par un canal fiable ou par une procédure d'enrôlement approuvée, comparer son empreinte par une source indépendante, puis ajouter la clé au magasin de confiance de façon contrôlée. `ssh-keyscan` peut aider à récupérer une clé présentée par un hôte, mais ne prouve pas, à lui seul, que cette clé appartient à l'équipement attendu. Ne transforme pas le mode strict en mode d'acceptation automatique pour rendre une exécution « verte ».

### 4.3 Construire le dictionnaire de connexion

```python
def build_connection_params(device, username, password):
    """Assemble les paramètres Netmiko pour une seule cible autorisée."""
    return {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": username,
        "password": password,
        "port": int(device.get("port", 22)),
        "conn_timeout": 8,
        "banner_timeout": 12,
        "auth_timeout": 12,
        "ssh_strict": True,
        "system_host_keys": True,
        "allow_agent": False,
        "fast_cli": False,
    }
```

Les temporisations de connexion sont séparées volontairement. `fast_cli=False` peut être utile comme choix conservateur lorsqu'on commence à diagnostiquer le comportement d'un équipement ou d'une session lente ; cela ne remplace pas une temporisation de lecture correctement définie pour les commandes. Les options disponibles et leur effet peuvent varier par plateforme et version. Vérifie les paramètres exposés par le manuel Netmiko de ton installation.

Le profil ci-dessus suppose que la clé de l'hôte est déjà présente dans la base de clés de confiance. Si ce n'est pas le cas, l'échec est attendu. Il faut résoudre la confiance de l'hôte, et non supprimer le contrôle de clé.

## 5. Construire une collecte robuste, un équipement à la fois

Le premier script débutant montre qu'une session peut être ouverte et qu'une commande peut être envoyée. Le niveau intermédiaire impose un contrat plus strict : chaque équipement doit produire un résultat identifiable, chaque commande doit avoir son propre statut et la session doit être fermée même lorsqu'une erreur survient. Une collecte partielle doit rester exploitable sans être présentée comme un succès complet.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 520" role="img" aria-labelledby="d2title d2desc" width="1200" height="520">
<title id="d2title">Une sortie CLI n’est pas encore une donnée fiable</title><desc id="d2desc">Chaque transformation doit être explicite, testable et observable.</desc>
<defs><linearGradient id="d2bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d2arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d2h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d2sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d2title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d2body{font:14px system-ui,sans-serif;fill:#dbeafe}.d2edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d2arrow);animation:d2move 1.2s linear infinite}@keyframes d2move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d2edge{animation:none}}</style></defs>
<rect width="1200" height="520" rx="24" fill="url(#d2bg)"/><text x="42" y="48" class="d2h">Une sortie CLI n’est pas encore une donnée fiable</text><text x="42" y="77" class="d2sub">Chaque transformation doit être explicite, testable et observable.</text><path class="d2edge" d="M205 219 L222 219"/><path class="d2edge" d="M395 219 L412 219"/><path class="d2edge" d="M585 219 L602 219"/><path class="d2edge" d="M775 219 L792 219"/><path class="d2edge" d="M965 219 L982 219"/><rect x="35" y="145" width="170" height="155" rx="15" fill="#26374c" stroke="#9ca3af" stroke-width="2"/><text x="54" y="175" class="d2title">1. Collecter</text><text x="54" y="207" class="d2body">Texte brut</text><text x="54" y="229" class="d2body">Commande + cible</text><text x="54" y="251" class="d2body">Horodatage</text><rect x="225" y="145" width="170" height="155" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="244" y="175" class="d2title">2. Normaliser</text><text x="244" y="207" class="d2body">Espaces et lignes</text><text x="244" y="229" class="d2body">Écho / invite</text><text x="244" y="251" class="d2body">Source conservée</text><rect x="415" y="145" width="170" height="155" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="434" y="175" class="d2title">3. Parser</text><text x="434" y="207" class="d2body">TextFSM / regex</text><text x="434" y="229" class="d2body">Champs nommés</text><text x="434" y="251" class="d2body">Listes / objets</text><rect x="605" y="145" width="170" height="155" rx="15" fill="#3f365f" stroke="#c4b5fd" stroke-width="2"/><text x="624" y="175" class="d2title">4. Valider</text><text x="624" y="207" class="d2body">Schéma attendu</text><text x="624" y="229" class="d2body">Valeurs</text><text x="624" y="251" class="d2body">plausibles</text><text x="624" y="273" class="d2body">Anomalies</text><rect x="795" y="145" width="170" height="155" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="814" y="175" class="d2title">5. Enrichir</text><text x="814" y="207" class="d2body">Site et rôle</text><text x="814" y="229" class="d2body">Référence</text><text x="814" y="251" class="d2body">attendue</text><text x="814" y="273" class="d2body">État calculé</text><rect x="985" y="145" width="170" height="155" rx="15" fill="#334155" stroke="#cbd5e1" stroke-width="2"/><text x="1004" y="175" class="d2title">6. Persister</text><text x="1004" y="207" class="d2body">JSON / CSV</text><text x="1004" y="229" class="d2body">Journal structuré</text><text x="1004" y="251" class="d2body">Rapport traçable</text></svg>



La bonne unité de traitement est une cible. Une fonction reçoit une entrée validée, crée une session, exécute une liste autorisée de commandes en lecture seule, capture les résultats, ferme la session puis rend un objet résultat. Elle ne doit pas modifier la configuration et ne doit pas afficher un mot de passe ni un objet de connexion complet dans les journaux.

### 5.1 Un résultat structuré

Un dictionnaire de résultat minimal devrait distinguer :

- `host` : identifiant connu de l'inventaire, pas un secret ;
- `status` : `success`, `partial` ou `failed` ;
- `started_at` et `finished_at` : horodatages ISO 8601 ;
- `commands` : résultat individuel de chaque commande, avec statut et sortie ;
- `error_type` et `error_message` : renseignés sans inclure les identifiants ;
- `duration_seconds` : durée observée ;
- `software_version` : version de Netmiko et, idéalement, de Python.

`partial` est essentiel : si trois commandes réussissent et que la quatrième expire, les trois premières sorties ne doivent pas être jetées ni marquées comme un inventaire totalement réussi. En revanche, il faut éviter qu'un rapport ne traite silencieusement un résultat partiel comme un état de référence complet.

### 5.2 Fonction de collecte de référence

L'exemple suivant est un squelette de collecte en lecture seule. Les commandes doivent être adaptées au constructeur et à la plateforme. Le dictionnaire d'inventaire et les identifiants ont déjà été validés par les fonctions précédentes.

```python
from datetime import datetime, timezone
from time import perf_counter

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)


APPROVED_READ_ONLY_COMMANDS = {
    "show version",
    "show clock",
    "show ip interface brief",
    "show interfaces status",
}


def commands_for_device(device):
    """Valide la liste demandée contre un petit catalogue autorisé."""
    commands = device.get("commands", [])
    if not isinstance(commands, list) or not commands:
        raise ValueError(f"Aucune commande définie pour {device.get('name', 'cible inconnue')}.")
    if any(
        not isinstance(command, str) or command not in APPROVED_READ_ONLY_COMMANDS
        for command in commands
    ):
        raise ValueError(
            f"Une commande n'est pas dans la liste de lecture autorisée pour {device.get('name')}."
        )
    return commands


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def collect_one_device(device, username, password):
    started_at = utc_now()
    timer = perf_counter()
    result = {
        "device_id": device["name"],
        "host": device["host"],
        "status": "failed",
        "started_at": started_at,
        "finished_at": None,
        "duration_seconds": None,
        "commands": [],
        "error_type": None,
        "error_message": None,
    }
    connection = None

    try:
        # Valider toutes les commandes avant d'ouvrir une session réseau.
        commands = commands_for_device(device)
        params = build_connection_params(device, username, password)
        connection = ConnectHandler(**params)

        for command in commands:
            command_started = perf_counter()
            try:
                output = connection.send_command(
                    command,
                    read_timeout=30,
                    strip_prompt=True,
                    strip_command=True,
                )
                result["commands"].append({
                    "command": command,
                    "status": "success",
                    "duration_seconds": round(
                        perf_counter() - command_started, 3
                    ),
                    "output": output,
                    "error": None,
                })
            except (NetmikoTimeoutException, OSError, ValueError) as exc:
                result["commands"].append({
                    "command": command,
                    "status": "failed",
                    "duration_seconds": round(
                        perf_counter() - command_started, 3
                    ),
                    "output": None,
                    "error": type(exc).__name__,
                })
                # Pour cette première version, interrompre les commandes
                # suivantes évite de multiplier une erreur de session.
                break

        command_statuses = [item["status"] for item in result["commands"]]
        successes = sum(status == "success" for status in command_statuses)
        if successes == len(commands):
            result["status"] = "success"
        elif successes > 0:
            result["status"] = "partial"
        else:
            result["status"] = "failed"

    except NetmikoAuthenticationException as exc:
        result["error_type"] = type(exc).__name__
        result["error_message"] = "Authentification SSH refusée."
    except NetmikoTimeoutException as exc:
        result["error_type"] = type(exc).__name__
        result["error_message"] = "Délai de connexion ou de bannière dépassé."
    except (OSError, ValueError) as exc:
        result["error_type"] = type(exc).__name__
        result["error_message"] = str(exc)[:300]
    finally:
        if connection is not None:
            try:
                connection.disconnect()
            except Exception:
                # Ne pas remplacer la cause initiale par une erreur de fermeture.
                pass
        result["finished_at"] = utc_now()
        result["duration_seconds"] = round(perf_counter() - timer, 3)

    return result
```

Ce code illustre la structure et demande une revue avant production. En particulier, certaines plateformes renvoient des messages d'erreur dans le texte plutôt que de lever une exception Python. C'est pourquoi il faut également contrôler le contenu, la forme attendue et le statut de chaque commande. La liste de commandes est volontairement centralisée : elle est facile à relire, à tester et à approuver.

### 5.3 Profils de commandes et liste d'autorisation

Les commandes sont propres à la plateforme. L'exemple d'inventaire contient une liste `commands`, mais une chaîne issue d'un fichier externe ne doit pas devenir exécutable sans contrôle. Dans l'exemple de collecte, `commands_for_device()` refuse une liste vide ou toute commande absente du petit catalogue de démonstration `APPROVED_READ_ONLY_COMMANDS`. Cette liste est volontairement limitée et doit être étendue par revue de code lorsqu'une commande supplémentaire est approuvée.

Pour un parc multi-constructeur, remplace ce catalogue unique par des profils indexés par plateforme ou par famille, par exemple `cisco_ios_baseline` et `juniper_junos_baseline`. Chaque profil contient un ensemble revu de commandes en lecture seule ; le validateur vérifie que l'identifiant du profil est autorisé pour le `device_type`. Les tests doivent prouver qu'une commande inconnue est refusée avant l'ouverture de la session. Cette conception protège contre les erreurs d'inventaire et évite qu'un champ éditable serve à lancer une commande arbitraire.

### 5.4 Garder les causes distinctes

Une erreur de résolution DNS, un refus TCP, une erreur d'authentification, une clé SSH inconnue et une commande refusée sont des événements différents. Ne remplace pas toutes ces situations par `Connexion échouée`. La distinction oriente l'action corrective et rend les rapports utiles à l'exploitation.

Par ailleurs, évite `except Exception: return {"status": "failed"}` autour de toute la fonction : cette pratique masque des erreurs de programmation, comme un nom de variable incorrect ou une mauvaise hypothèse sur la structure d'un objet. Attrape les erreurs attendues au niveau où tu peux apporter une réponse appropriée. Un gestionnaire global de dernier recours peut journaliser une trace technique, mais ne doit pas cacher le diagnostic.

## 6. Temporisations, pagination et commandes qui répondent lentement

Une connexion SSH est une chaîne de phases : ouverture TCP, échange de bannière, négociation SSH, authentification, préparation du canal, envoi de la commande et lecture de la réponse. Une seule temporisation n'est pas toujours capable de couvrir proprement toutes ces phases.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 480" role="img" aria-labelledby="d6title d6desc" width="1200" height="480">
<title id="d6title">Un timeout doit décrire l’étape qui attend</title><desc id="d6desc">Augmenter tous les délais sans diagnostic masque la cause et prolonge les incidents.</desc>
<defs><linearGradient id="d6bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d6arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d6h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d6sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d6title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d6body{font:14px system-ui,sans-serif;fill:#dbeafe}.d6edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d6arrow);animation:d6move 1.2s linear infinite}@keyframes d6move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d6edge{animation:none}}</style></defs>
<rect width="1200" height="480" rx="24" fill="url(#d6bg)"/><text x="42" y="48" class="d6h">Un timeout doit décrire l’étape qui attend</text><text x="42" y="77" class="d6sub">Augmenter tous les délais sans diagnostic masque la cause et prolonge les incidents.</text><path class="d6edge" d="M298 220 L320 220"/><path class="d6edge" d="M580 220 L602 220"/><path class="d6edge" d="M862 220 L884 220"/><rect x="48" y="145" width="250" height="150" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="67" y="175" class="d6title">1. Transport TCP</text><text x="67" y="207" class="d6body">conn_timeout</text><text x="67" y="229" class="d6body">Route, port, ACL</text><text x="67" y="251" class="d6body">Connexion établie ?</text><rect x="330" y="145" width="250" height="150" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="349" y="175" class="d6title">2. Bannière SSH</text><text x="349" y="207" class="d6body">banner_timeout</text><text x="349" y="229" class="d6body">Démon / proxy</text><text x="349" y="251" class="d6body">Surcharge éventuelle</text><rect x="612" y="145" width="250" height="150" rx="15" fill="#3f365f" stroke="#c4b5fd" stroke-width="2"/><text x="631" y="175" class="d6title">3. Authentification</text><text x="631" y="207" class="d6body">auth_timeout</text><text x="631" y="229" class="d6body">Compte / clé / AAA</text><text x="631" y="251" class="d6body">Méthode acceptée ?</text><rect x="894" y="145" width="250" height="150" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="913" y="175" class="d6title">4. Lecture CLI</text><text x="913" y="207" class="d6body">read_timeout</text><text x="913" y="229" class="d6body">Commande volumineuse ?</text><text x="913" y="251" class="d6body">Pagination / invite</text></svg>



| Paramètre ou notion | Rôle | Erreur fréquente |
|---|---|---|
| `conn_timeout` | Attente de l'établissement de la connexion réseau | L'augmenter pour masquer une route ou un port incorrect |
| `banner_timeout` | Attente de la bannière SSH | L'ignorer lorsque la bannière d'un équipement est très lente |
| `auth_timeout` | Attente liée à l'authentification | Traiter toute expiration comme un mauvais mot de passe |
| `read_timeout` | Temps accordé à la lecture d'une commande | Donner la même valeur à toutes les commandes, sans mesure |
| Timeout du système d'exploitation | Limite de bas niveau ou de transport | Supposer qu'il a la même sémantique que Netmiko |

### 6.1 Mesurer avant d'augmenter les délais

Ajoute une mesure de durée autour de chaque commande. Après plusieurs exécutions représentatives, observe la médiane, les valeurs extrêmes et les plateformes qui répondent plus lentement. Définis un délai tenant compte du temps opérationnel acceptable et de la variabilité réelle. Une valeur démesurée rend la collecte lente lorsque l'équipement ne répond plus ; une valeur trop faible produit de faux échecs.

Avec les versions modernes de Netmiko 4.x, `read_timeout` est le paramètre explicite pour les commandes. Les anciens exemples qui utilisent `delay_factor` ou `max_loops` peuvent provenir d'anciennes interfaces et sont dépréciés ou retirés de certains chemins modernes. Ne copie pas un exemple trouvé en ligne sans vérifier la documentation de la version installée.

### 6.2 `send_command` et `send_command_timing`

`send_command` attend la détection du prompt, ce qui convient aux commandes ordinaires lorsque Netmiko sait identifier le prompt de la plateforme. `send_command_timing` s'appuie principalement sur le comportement temporel du flux et peut être approprié à des commandes dont les invitations ou les prompts ne sont pas standard. Cette deuxième méthode demande une attention accrue : elle peut s'arrêter trop tôt, attendre trop longtemps ou capturer une réponse incomplète si les paramètres ne correspondent pas au comportement de l'équipement.

Ne choisis pas `send_command_timing` uniquement parce qu'une commande échoue avec la méthode normale. Commence par inspecter la sortie, le prompt, la pagination et les messages d'invitation. Si la commande demande une confirmation ou plusieurs réponses interactives, conçois une séquence explicite, spécifique à la plateforme et testée en laboratoire. Une commande d'exploitation habituelle ne doit jamais être automatiquement transformée en commande interactive sans avoir défini ce que signifie une réponse sûre.

### 6.3 Pagination et commandes volumineuses

De nombreux équipements affichent un prompt de pagination comme `--More--`. Netmiko dispose de mécanismes spécifiques à ses plateformes, mais la configuration et le comportement dépendent du driver. Dans le cas d'un driver personnalisé, vérifie la commande de désactivation de la pagination, le prompt détecté et la quantité de données renvoyée.

Pour une commande qui produit des milliers de lignes, demande-toi si l'outil est adapté, si les sorties peuvent être filtrées par l'équipement, et si une interface structurée est disponible. Collecter toute la table de routage de toute une flotte à chaque minute crée de la charge, des fichiers massifs et des risques de rétention de données. Il est souvent préférable de séparer collecte périodique légère, collecte complète planifiée et diagnostic à la demande.

## 7. Passer du texte aux données fiables

Au niveau débutant, conserver la sortie brute permet de consulter le résultat et de comprendre les différences de terminal. Au niveau intermédiaire, la sortie brute reste précieuse, mais le traitement automatique ne doit plus dépendre de recherches textuelles vagues. Une sortie structurée permet de comparer des champs plutôt que des lignes dont les espaces changent d'une version à l'autre.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 540" role="img" aria-labelledby="d5title d5desc" width="1200" height="540">
<title id="d5title">Parser : passer d’un affichage à des champs exploitables</title><desc id="d5desc">Le parsing doit être testé sur des sorties connues et signaler les changements de format.</desc>
<defs><linearGradient id="d5bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d5arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d5h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d5sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d5title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d5body{font:14px system-ui,sans-serif;fill:#dbeafe}.d5edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d5arrow);animation:d5move 1.2s linear infinite}@keyframes d5move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d5edge{animation:none}}</style></defs>
<rect width="1200" height="540" rx="24" fill="url(#d5bg)"/><text x="42" y="48" class="d5h">Parser : passer d’un affichage à des champs exploitables</text><text x="42" y="77" class="d5sub">Le parsing doit être testé sur des sorties connues et signaler les changements de format.</text><path class="d5edge" d="M512 245 L580 245"/><path class="d5edge" d="M770 245 L840 245"/><rect x="42" y="125" width="470" height="245" rx="15" fill="#0b1320" stroke="#64748b" stroke-width="2"/><text x="61" y="155" class="d5title">Sortie CLI · texte brut</text><text x="61" y="187" class="d5body">Interface       IP-Address    Status</text><text x="61" y="209" class="d5body">Gi1/0/1         192.0.2.10    up</text><text x="61" y="231" class="d5body">Gi1/0/2         unassigned    down</text><text x="61" y="253" class="d5body">Lisible à l’écran ; colonnes variables</text><rect x="590" y="125" width="180" height="245" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="609" y="155" class="d5title">Parser</text><text x="609" y="187" class="d5body">TextFSM</text><text x="609" y="209" class="d5body">Regex ciblée</text><text x="609" y="231" class="d5body">TTP</text><text x="609" y="253" class="d5body">Template versionné</text><rect x="848" y="125" width="310" height="245" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="867" y="155" class="d5title">Données structurées</text><text x="867" y="187" class="d5body">interface: Gi1/0/1</text><text x="867" y="209" class="d5body">ip: 192.0.2.10</text><text x="867" y="231" class="d5body">status: up</text><text x="867" y="253" class="d5body">Filtrer, comparer, exporter</text></svg>



### 7.1 Les stratégies de parsing

Dans l'ordre où il est généralement préférable de les étudier :

1. **API ou sortie structurée du constructeur**, lorsqu'elles sont disponibles et autorisées.
2. **TextFSM avec les modèles NTC**, si la commande et la plateforme sont couverts par un modèle fiable.
3. **Parser explicite du projet**, avec une grammaire simple et des tests sur sorties réelles connues.
4. **Expressions régulières**, pour une portion bien délimitée dont le format est stable.
5. **Recherche de sous-chaînes**, seulement pour une détection très simple, pas comme parseur universel.

Les commandes réseau n'ont pas toutes une sortie identique. Une interface peut être administrativement arrêtée, absente, en mode sous-interface, ou apparaître dans un format qui varie selon la version du système. Ne traite pas une expression régulière qui fonctionne sur une sortie de laboratoire comme une règle universelle.

### 7.2 Utiliser TextFSM avec Netmiko

Netmiko peut utiliser TextFSM, et les modèles maintenus dans le dépôt NTC Templates couvrent de nombreuses plateformes et commandes. Le paquet `ntc-templates` peut être installé séparément selon l'environnement ; assure-toi que la variable d'environnement et la version du paquet sont correctement configurées si nécessaire.

```python
from netmiko import ConnectHandler

params = {
    "device_type": "cisco_ios",
    "host": "192.0.2.11",
    "username": username,
    "password": password,
    "ssh_strict": True,
    "system_host_keys": True,
}

with ConnectHandler(**params) as connection:
    parsed = connection.send_command(
        "show ip interface brief",
        use_textfsm=True,
        read_timeout=30,
    )

if not isinstance(parsed, list):
    raise TypeError("Le résultat parsé n'est pas une liste.")

if parsed and not all(isinstance(row, dict) for row in parsed):
    raise TypeError("Le résultat ne contient pas des enregistrements dictionnaires.")

print(f"Interfaces décodées : {len(parsed)}")
```

Le type exact du résultat dépend de la combinaison plateforme, commande et options. Vérifie ce que renvoie réellement la version utilisée. Une liste vide peut signifier que le modèle n'a pas reconnu des lignes, que l'équipement n'a aucune ligne correspondante ou que la commande n'a pas produit le format attendu. Il faut détecter cette ambiguïté plutôt que considérer toute liste vide comme une réussite.

### 7.3 Vérifier que le parser a vraiment fonctionné

Un parseur doit être testé sur au moins trois jeux d'essai : une sortie normale, une sortie comportant un cas limite et une sortie inattendue. Un bon test peut confirmer le nombre minimal d'enregistrements, la présence des clés indispensables et le format de champs sensibles. Si le modèle ne correspond pas, conserver le texte brut et marquer `parse_status="failed"` est souvent plus utile que de supprimer la sortie.

Pour une validation de forme, par exemple, exige que chaque entrée contienne les champs attendus et vérifie qu'une adresse IPv4 décodée est réellement une adresse. Ne transforme pas des chaînes `N/A`, `unassigned` ou des valeurs constructeur dans une valeur nulle sans conserver la raison de cette transformation. La donnée originale et la donnée normalisée peuvent toutes deux être utiles au dépannage.

### 7.4 Parser maison pour un format connu

Voici une illustration volontairement limitée à une sortie de type Cisco IOS `show ip interface brief`. Elle accepte les champs communs de chaque ligne, mais ne remplace pas une validation par tests contre les sorties des plateformes ciblées.

```python
import re
from ipaddress import IPv4Address

INTERFACE_ROW = re.compile(
    r"^(?P<interface>\S+)\s+"
    r"(?P<ip_address>\S+)\s+"
    r"\S+\s+\S+\s+"
    r"(?P<status>\S+)\s+"
    r"(?P<protocol>\S+)\s*$"
)


def parse_interface_brief(text: str) -> list[dict[str, str | None]]:
    rows = []
    for line in text.splitlines():
        match = INTERFACE_ROW.match(line.strip())
        if not match:
            continue
        item = match.groupdict()
        ip_value = item["ip_address"]
        try:
            IPv4Address(ip_value)
        except ValueError:
            if ip_value.lower() in {"unassigned", "unset", "none"}:
                item["ip_address"] = None
            else:
                # Une valeur inconnue ne doit pas être convertie en silence.
                raise ValueError(f"Adresse non reconnue : {ip_value!r}")
        rows.append(item)
    return rows
```

Avant d'utiliser ce parser, compare la regex à plusieurs sorties réelles : l'espacement, les champs de méthode IP et les libellés peuvent différer. Le principe intermédiaire n'est pas de coder toutes les variantes du monde dans une seule regex, mais de fixer un périmètre clair et de faire échouer explicitement les formats imprévus.

## 8. Normalisation et validation métier

Le parsing répond à « quelles données ai-je extraites ? ». La validation métier répond à « ces données ont-elles du sens pour mon réseau ? ». Une sortie parfaitement parsée peut encore être incohérente : mauvaise plage d'adresses, interface attendue absente, état administrativement désactivé ou version logicielle non approuvée.

### 8.1 Séparer extraction et règles métier

Évite de mélanger la connexion SSH, l'expression régulière, le calcul de l'état de conformité et la production du rapport dans une seule fonction de plusieurs centaines de lignes. Préfère un flux lisible : la couche collecte des sorties, la couche parsing transforme ces sorties, la couche validation applique les règles métier, puis la couche rapport sérialise les résultats.

Cela rend les tests beaucoup plus faciles. Une fonction `validate_interfaces(rows, expected)` peut recevoir un objet en mémoire et s'exécuter sans réseau, sans identifiant et sans session Netmiko. De même, le parseur peut être testé sur une chaîne de test. Seul le code de collecte a besoin d'un équipement accessible.

### 8.2 Exemple de validation d'interface

```python
from ipaddress import IPv4Address


def validate_interface_records(rows: list[dict]) -> list[dict]:
    problems = []
    for index, row in enumerate(rows, start=1):
        required = {"interface", "ip_address", "status", "protocol"}
        missing = required - row.keys()
        if missing:
            problems.append({
                "row": index,
                "reason": "missing_fields",
                "fields": sorted(missing),
            })
            continue

        ip_value = row["ip_address"]
        if ip_value is not None:
            try:
                IPv4Address(ip_value)
            except (ValueError, TypeError):
                problems.append({
                    "row": index,
                    "reason": "invalid_ipv4",
                    "interface": row["interface"],
                })

        status = str(row["status"]).strip().lower()
        protocol = str(row["protocol"]).strip().lower()
        if status in {"up", "connected"} and protocol not in {"up", "connected"}:
            problems.append({
                "row": index,
                "reason": "status_protocol_mismatch",
                "interface": row["interface"],
                "status": status,
                "protocol": protocol,
            })
    return problems
```

Les termes `connected`, `up`, `administratively down` et les colonnes disponibles varient selon l'équipement. Adapte donc les règles à la plateforme et au parser utilisés. Une règle de conformité doit être explicite, versionnée et accompagnée de cas de test ; une règle qui signale trop de faux positifs finit par être ignorée.

### 8.3 Comparer état attendu et état observé

Définis les attentes séparément de la sortie de collecte, par exemple dans un fichier YAML/JSON versionné ne contenant pas de secrets. Une règle peut préciser quelles interfaces doivent être actives, quelles versions logicielles sont approuvées ou si un équipement doit répondre. Chaque règle doit spécifier son comportement quand la donnée est manquante : `unknown`, `not_checked` ou `failed` ne sont pas synonymes de `non_conforme`.

Ne réduis pas le résultat à un booléen unique si plusieurs contrôles ont des états différents. Dans un rapport de flotte, affiche le total d'équipements ciblés, joignables, partiellement collectés, impossibles à authentifier, et conformes selon chaque règle. Le résumé doit garder la différence entre l'équipement inconnu du système de collecte et l'équipement réellement non conforme.

## 9. Erreurs, reprise et politique de nouvelle tentative

Les reprises peuvent rendre les collectes plus robustes, mais elles peuvent aussi amplifier une panne ou masquer une configuration incorrecte. Avant de recommencer, classe l'erreur et décide si elle est transitoire, permanente ou ambiguë.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 560" role="img" aria-labelledby="d7title d7desc" width="1200" height="560">
<title id="d7title">Classer l’échec avant de relancer</title><desc id="d7desc">La reprise automatique est une décision, pas un réflexe.</desc>
<defs><linearGradient id="d7bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d7arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d7h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d7sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d7title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d7body{font:14px system-ui,sans-serif;fill:#dbeafe}.d7edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d7arrow);animation:d7move 1.2s linear infinite}@keyframes d7move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d7edge{animation:none}}</style></defs>
<rect width="1200" height="560" rx="24" fill="url(#d7bg)"/><text x="42" y="48" class="d7h">Classer l’échec avant de relancer</text><text x="42" y="77" class="d7sub">La reprise automatique est une décision, pas un réflexe.</text><path class="d7edge" d="M600 178 L150 225"/><path class="d7edge" d="M600 178 L450 225"/><path class="d7edge" d="M600 178 L750 225"/><path class="d7edge" d="M600 178 L1050 225"/><path class="d7edge" d="M150 345 L600 405"/><path class="d7edge" d="M450 345 L600 405"/><path class="d7edge" d="M750 345 L600 405"/><path class="d7edge" d="M1050 345 L600 405"/><rect x="400" y="108" width="400" height="70" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="419" y="138" class="d7title">Échec ou résultat suspect</text><rect x="30" y="225" width="240" height="120" rx="15" fill="#4b2833" stroke="#fda4af" stroke-width="2"/><text x="49" y="255" class="d7title">Connectivité</text><text x="49" y="287" class="d7body">Timeout TCP</text><text x="49" y="309" class="d7body">Route / ACL / port</text><text x="49" y="331" class="d7body">Vérifier le chemin</text><rect x="330" y="225" width="240" height="120" rx="15" fill="#3f365f" stroke="#c4b5fd" stroke-width="2"/><text x="349" y="255" class="d7title">SSH / identité</text><text x="349" y="287" class="d7body">Clé inconnue</text><text x="349" y="309" class="d7body">Authentification refusée</text><text x="349" y="331" class="d7body">Vérifier la confiance</text><rect x="630" y="225" width="240" height="120" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="649" y="255" class="d7title">Commande / lecture</text><text x="649" y="287" class="d7body">Prompt ou délai</text><text x="649" y="309" class="d7body">Commande invalide</text><text x="649" y="331" class="d7body">Comparer au CLI</text><rect x="930" y="225" width="240" height="120" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="949" y="255" class="d7title">Donnée / parsing</text><text x="949" y="287" class="d7body">Sortie vide</text><text x="949" y="309" class="d7body">Template absent</text><text x="949" y="331" class="d7body">Conserver le brut</text><rect x="245" y="405" width="710" height="108" rx="15" fill="#0b1320" stroke="#49637b" stroke-width="2"/><text x="264" y="435" class="d7title">Classer · journaliser · décider</text><text x="264" y="467" class="d7body">Retry limité pour une lecture transitoire ; pas de retry aveugle sur une mutation.</text></svg>



| Famille d'erreur | Reprise automatique ? | Action recommandée |
|---|---|---|
| Délai réseau intermittent | Parfois, avec limite | Une ou deux nouvelles tentatives, temporisation progressive, journal explicite |
| Clé SSH inconnue ou changée | Non | Vérifier l'identité de l'hôte par la procédure de confiance |
| Authentification refusée | Non par défaut | Contrôler l'identifiant, les droits, le verrouillage et le coffre de secrets |
| Commande non prise en charge | Non | Adapter la commande à la plateforme ou corriger l'inventaire |
| Parsing non reconnu | Pas de répétition réseau automatique par défaut | Conserver le brut, marquer l'échec de parsing et tester le modèle |
| Erreur de configuration appliquée | Ne pas rejouer aveuglément | Arrêter le lot, inspecter l'état et revenir au plan de changement approuvé |

### 9.1 Reprise exponentielle avec jitter

Pour les erreurs réellement transitoires, la temporisation progressive réduit les tentatives répétées au même instant. Une petite composante aléatoire (*jitter*) évite que tous les workers se reconnectent ensemble après une panne partagée.

```python
import random
import time


def retry_delay(attempt: int, base: float = 1.0, maximum: float = 20.0) -> float:
    if attempt < 1:
        raise ValueError("attempt doit commencer à 1")
    ceiling = min(maximum, base * (2 ** (attempt - 1)))
    return random.uniform(0.0, ceiling)


# Exemple d'utilisation : maximum trois tentatives en tout.
for attempt in range(1, 4):
    try:
        # Appeler ici une fonction idempotente de collecte en lecture seule.
        result = collect_read_only_target(target)
        break
    except TransientNetworkError:
        if attempt == 3:
            raise
        time.sleep(retry_delay(attempt))
```

`TransientNetworkError` est ici un nom de classe que ton projet doit définir à partir des exceptions qu'il sait classer avec fiabilité. Ce n'est pas une exception native de Netmiko. Ne classe pas toute `OSError` comme transitoire, et ne réessaie jamais un changement de configuration non idempotent sans réconcilier l'état effectif.

### 9.2 Idempotence et limites de reprise

Une opération est idempotente lorsque la répéter produit le même état final qu'une exécution unique, dans le contexte défini. Lire une version logicielle est naturellement sans effet sur la configuration, mais peut quand même solliciter fortement un équipement. Ajouter une route, recréer une ACL ou exécuter une commande de remise à zéro n'est pas automatiquement idempotent.

Même une commande de configuration qui semble idempotente peut avoir des effets annexes, un ordre dépendant, ou changer de sens selon la plateforme. Avant d'autoriser une reprise, établis le point de départ, le résultat attendu et une méthode de détection de l'état partiellement modifié. Toute nouvelle tentative doit être comptée dans le rapport ; un résultat finalement réussi après deux échecs est un succès avec avertissement opérationnel, pas une absence d'incident.

## 10. Rapports reproductibles : JSON, CSV et sorties brutes

Un bon rapport distingue les données brutes, les valeurs normalisées, les validations et les métadonnées d'exécution. Évite de remplacer la sortie brute par son parse : lors d'un changement de version constructeur, la sortie d'origine peut permettre de corriger le modèle ou de confirmer pourquoi l'analyse a échoué.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 530" role="img" aria-labelledby="d10title d10desc" width="1200" height="530">
<title id="d10title">Un outil exploitable explique ce qu’il a fait</title><desc id="d10desc">Les journaux, données structurées et rapports doivent converger sans exposer les secrets.</desc>
<defs><linearGradient id="d10bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d10arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d10h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d10sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d10title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d10body{font:14px system-ui,sans-serif;fill:#dbeafe}.d10edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d10arrow);animation:d10move 1.2s linear infinite}@keyframes d10move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d10edge{animation:none}}</style></defs>
<rect width="1200" height="530" rx="24" fill="url(#d10bg)"/><text x="42" y="48" class="d10h">Un outil exploitable explique ce qu’il a fait</text><text x="42" y="77" class="d10sub">Les journaux, données structurées et rapports doivent converger sans exposer les secrets.</text><path class="d10edge" d="M332 274 L445 274"/><path class="d10edge" d="M745 274 L858 274"/><rect x="42" y="140" width="290" height="270" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="61" y="170" class="d10title">Journal technique</text><text x="61" y="202" class="d10body">Horodatage UTC</text><text x="61" y="224" class="d10body">Cible et étape</text><text x="61" y="246" class="d10body">Durée</text><text x="61" y="268" class="d10body">Type d’exception</text><text x="61" y="290" class="d10body">Commande sans secret</text><text x="61" y="312" class="d10body">Détails de diagnostic</text><rect x="455" y="140" width="290" height="270" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="474" y="170" class="d10title">Résultats structurés</text><text x="474" y="202" class="d10body">success / partial / failed</text><text x="474" y="224" class="d10body">Commandes réussies / total</text><text x="474" y="246" class="d10body">Temps écoulé</text><text x="474" y="268" class="d10body">Échec du parsing</text><text x="474" y="290" class="d10body">Compteur de reprises</text><rect x="868" y="140" width="290" height="270" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="887" y="170" class="d10title">Rapport d’exploitation</text><text x="887" y="202" class="d10body">JSON détaillé</text><text x="887" y="224" class="d10body">CSV de synthèse</text><text x="887" y="246" class="d10body">Anomalies résumées</text><text x="887" y="268" class="d10body">Horodatage</text><text x="887" y="290" class="d10body">Décision / audit</text></svg>



### 10.1 Écrire du JSON atomiquement

Une bonne stratégie consiste à écrire d'abord un fichier temporaire dans le même dossier, à vider et fermer le flux, puis à remplacer la destination finale. Cela réduit le risque de laisser un fichier partiel sous le nom du rapport attendu si le processus est interrompu.

```python
import json
import os
from pathlib import Path


def write_json_atomic(path: Path, payload) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        finally:
            raise
```

La stratégie ci-dessus s'occupe de l'écriture atomique au niveau du système de fichiers habituel, mais ne résout pas toutes les questions de durabilité, de permissions ou de fonctionnement sur des systèmes de fichiers réseau. Fixe des permissions appropriées au répertoire et au fichier. Les données sensibles doivent être exclues ou protégées avant la sérialisation.

### 10.2 CSV pour les tableaux, JSON pour les objets hiérarchiques

CSV convient aux lignes homogènes : un hôte par ligne, une commande par ligne ou une anomalie par ligne. Les résultats hiérarchiques avec liste de commandes et liste de problèmes sont généralement plus naturels en JSON. Dans les deux cas, définis le schéma et l'encodage, écris les en-têtes, et indique si une valeur vide signifie « donnée inconnue », « champ absent » ou « chaîne vide ».

Attention à l'injection de formule lors de l'ouverture d'un CSV dans un tableur : des champs textuels commençant par certains caractères peuvent être interprétés comme une formule. Si des noms d'hôtes, messages ou sorties sont contrôlés par l'équipement, échappe ces champs avant une exportation destinée à être ouverte dans un tableur, tout en conservant une version brute de confiance dans un format approprié.

### 10.3 Noms de fichiers et rétention

Préférer un horodatage UTC et un identifiant d'exécution maîtrisé, par exemple `collecte_2026-10-23T225500Z.json`, plutôt que de construire un chemin depuis un nom d'hôte non validé. Vérifie que le chemin de sortie reste dans le répertoire autorisé et crée les dossiers de façon contrôlée. Prévois une politique de rétention et de rotation ; les sorties CLI peuvent exposer des détails internes, des adresses, des noms d'utilisateurs et parfois des informations confidentielles.

## 11. Journalisation exploitable

Les impressions à l'écran restent utiles lors d'un exercice, mais un projet intermédiaire doit utiliser le module standard `logging`. Chaque entrée doit porter un niveau, un horodatage et un contexte suffisant pour comprendre l'événement sans divulguer un secret. Le `device_id`, l'identifiant d'exécution et le nom de la commande sont généralement plus utiles qu'un message vague comme « erreur ».

```python
import logging


def configure_logging(log_path):
    log_path = str(log_path)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        force=True,
    )
```

Exemples de messages raisonnables : `device_id=core-01 event=connect_start`, `device_id=edge-02 command=show_clock status=success duration=0.42`, `device_id=dist-03 event=auth_failed`. Les champs peuvent être intégrés de façon structurée si la plateforme de journalisation le permet. Ne consigne jamais `password`, `secret`, les paramètres complets de connexion, un jeton, ni des sorties brutes sans vérifier qu'elles peuvent être conservées.

Pour un programme réutilisable comme bibliothèque, évite de modifier la configuration globale du logging à l'import du module. Configure les handlers dans le point d'entrée du programme et laisse les fonctions métier émettre leurs messages via `logging.getLogger(__name__)`. Cette séparation facilite les tests et l'intégration avec les outils d'observabilité de l'entreprise.

## 12. Collecter plusieurs équipements sans perdre le contrôle

La boucle séquentielle du niveau débutant est simple et constitue une excellente référence. Son défaut apparaît lorsque le parc grandit : si chaque connexion prend plusieurs secondes, la durée totale augmente avec le nombre de cibles. La tentation est alors de lancer toutes les connexions en parallèle. Une automatisation sérieuse utilise plutôt une concurrence bornée, des limites de charge, un délai maximum et des résultats associés à chaque cible.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 555" role="img" aria-labelledby="d8title d8desc" width="1200" height="555">
<title id="d8title">Aller plus vite sans saturer les équipements</title><desc id="d8desc">Une file de cibles alimente quelques travailleurs ; chaque tâche possède sa propre session.</desc>
<defs><linearGradient id="d8bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d8arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d8h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d8sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d8title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d8body{font:14px system-ui,sans-serif;fill:#dbeafe}.d8edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d8arrow);animation:d8move 1.2s linear infinite}@keyframes d8move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d8edge{animation:none}}</style></defs>
<rect width="1200" height="555" rx="24" fill="url(#d8bg)"/><text x="42" y="48" class="d8h">Aller plus vite sans saturer les équipements</text><text x="42" y="77" class="d8sub">Une file de cibles alimente quelques travailleurs ; chaque tâche possède sa propre session.</text><path class="d8edge" d="M252 300 L300 300"/><path class="d8edge" d="M853 300 L900 300"/><rect x="42" y="145" width="210" height="300" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="61" y="175" class="d8title">File d’attente</text><text x="61" y="207" class="d8body">SW-01</text><text x="61" y="229" class="d8body">SW-02</text><text x="61" y="251" class="d8body">RTR-03</text><text x="61" y="273" class="d8body">FW-04</text><text x="61" y="295" class="d8body">AP-05</text><text x="61" y="317" class="d8body">… autres cibles</text><rect x="308" y="132" width="545" height="340" rx="15" fill="#0b1320" stroke="#49637b" stroke-width="2"/><text x="327" y="162" class="d8title">Pool · max_workers = 4</text><text x="327" y="194" class="d8body">Travailleur A — session propre</text><text x="327" y="216" class="d8body">Travailleur B — session propre</text><text x="327" y="238" class="d8body">Travailleur C — session propre</text><text x="327" y="260" class="d8body">Travailleur D — session propre</text><rect x="908" y="145" width="250" height="300" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="927" y="175" class="d8title">Résultats</text><text x="927" y="207" class="d8body">Succès / partiel</text><text x="927" y="229" class="d8body">Timeout / auth</text><text x="927" y="251" class="d8body">Durée par cible</text><text x="927" y="273" class="d8body">JSON / CSV</text><text x="927" y="295" class="d8body">Journal central</text></svg>



### 12.1 Pourquoi une limite explicite est indispensable

Un réseau de cent équipements n'implique pas qu'il soit raisonnable d'ouvrir cent sessions simultanées. Les équipements peuvent disposer d'une capacité limitée de gestion ; les bastions et serveurs AAA peuvent également imposer une limite. Une connexion massive peut faire apparaître des refus temporaires, activer des mécanismes de protection ou perturber la supervision.

Commence par une valeur faible, telle que deux à cinq workers pour un petit laboratoire, puis mesure la durée, les échecs et la charge. Ce nombre n'est pas universel : il doit être décidé selon les autorisations, la capacité des équipements et les contraintes de l'environnement. Un plafond doit rester un paramètre explicite et révisable, pas une valeur cachée dans une fonction.

### 12.2 Modèle avec `ThreadPoolExecutor`

Les sessions réseau sont principalement des tâches d'attente I/O. Les threads peuvent donc améliorer le temps total d'une collecte sans nécessiter un modèle de processus séparé. Chaque worker doit ouvrir et fermer sa propre session Netmiko ; ne partage pas un objet `ConnectHandler` actif entre threads.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


def collect_device_task(device, username, password):
    # La fonction ouvre sa propre session, la ferme dans finally,
    # et retourne un objet résultat pour cette cible uniquement.
    return collect_one_device(device, username, password)


def collect_fleet(devices, username, password, max_workers=4):
    if not isinstance(max_workers, int) or max_workers < 1:
        raise ValueError("max_workers doit être un entier positif")
    if max_workers > 10:
        raise ValueError("Le plafond local est limité à 10 workers ; revoir explicitement la politique")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                collect_device_task, device, username, password
            ): device
            for device in devices
        }
        for future in as_completed(futures):
            device = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                # Dernier filet : conserver l'erreur liée à la cible,
                # mais journaliser une trace technique pour le diagnostic.
                logger.exception("Échec interne pour device_id=%s", device["name"])
                result = {
                    "device_id": device["name"],
                    "host": device["host"],
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "error_message": "Échec inattendu du worker ; consulter le journal.",
                    "commands": [],
                }
            results.append(result)
    return results
```

L'exemple impose un plafond local de dix workers à titre de garde-fou de démonstration. Il faut définir ce plafond selon les contraintes de l'équipe, et les contrôles doivent être cohérents avec la capacité réelle du parc. Le `future.result()` peut lever une exception inattendue ; celle-ci est capturée par cible afin qu'un seul worker ne fasse pas perdre les résultats de toute la collecte.

### 12.3 Ordonner les résultats

`as_completed` rend les résultats à mesure que les tâches terminent : l'ordre de la liste n'est donc pas garanti. Pour un rapport déterministe, trie les résultats par identifiant ou restaure l'ordre défini dans l'inventaire. Ne suppose pas que l'ordre de fin des sessions reflète la topologie ou la priorité des équipements.

La concurrence multiplie aussi les sources de pression : le nombre de sessions ouvertes, la taille de chaque sortie en mémoire, les tentatives de reprise et l'écriture sur disque. Pour de très grands parcs, envisage une file de tâches, un traitement par lots et un stockage incrémental. Une collecte qui accumule la sortie complète de milliers d'équipements dans une seule liste peut saturer la mémoire même si chaque commande individuelle reste raisonnable.

### 12.4 Limite de sécurité

Paralléliser des commandes de configuration est considérablement plus risqué que paralléliser des lectures. Le modèle présenté ci-dessus doit rester dédié à la collecte en lecture seule. La phase de changement doit avoir un mécanisme différent, un plafond de concurrence plus strict, une fenêtre approuvée, un arrêt global, une vérification indépendante et une stratégie de restauration.

## 13. Construire une architecture de projet maintenable

Une collection de scripts peut suffire pour un seul exercice, mais un projet qui grandit doit distinguer l'entrée utilisateur, l'inventaire, la connexion, la collecte, le parsing, les validations, le rapport et les tests. Cette séparation empêche une modification de l'inventaire de casser les tests du parseur ou une modification du rapport de changer la façon dont une session se ferme.



Une structure de dépôt simple peut ressembler à ceci :

```text
netmiko-project/
├── README.md
├── pyproject.toml
├── .gitignore
├── inventory/
│   └── lab.json
├── src/
│   └── netauto/
│       ├── __init__.py
│       ├── inventory.py
│       ├── credentials.py
│       ├── connection.py
│       ├── collect.py
│       ├── parse.py
│       ├── validate.py
│       ├── report.py
│       └── cli.py
├── tests/
│   ├── fixtures/
│   │   ├── show_version_ios.txt
│   │   └── show_ip_interface_brief.txt
│   ├── test_inventory.py
│   ├── test_parse.py
│   └── test_validate.py
├── runs/
│   └── .gitkeep
└── docs/
    └── decisions.md
```

Le répertoire `runs/` contient des sorties d'exécution ; selon leur sensibilité, il peut être exclu de Git et soumis à une politique de rétention. Les fixtures de test doivent être nettoyées et ne pas intégrer de mots de passe, de clés privées, de jetons ou de données client. Ne versionne pas une sortie brute de production sans analyse de sensibilité et procédure d'approbation.

### 13.1 Les responsabilités des modules

| Module | Responsabilité | Ce qu'il ne devrait pas faire |
|---|---|---|
| `inventory.py` | Charger, valider et normaliser les cibles | Ouvrir des sessions SSH |
| `credentials.py` | Obtenir les secrets depuis la source définie | Écrire les secrets dans les logs |
| `connection.py` | Construire les paramètres autorisés et connecter une cible | Calculer la conformité métier |
| `collect.py` | Exécuter les commandes autorisées et conserver les résultats | Faire la présentation finale des rapports |
| `parse.py` | Convertir une sortie en données structurées | Se connecter à un équipement |
| `validate.py` | Comparer données et règles attendues | Deviner silencieusement les valeurs manquantes |
| `report.py` | Sérialiser les résultats et les résumés | Modifier l'état des équipements |
| `cli.py` | Lire arguments et options, coordonner le flux | Contenir toute la logique métier |

Cette structure n'est pas une obligation dogmatique. Pour un projet de taille moyenne, quelques modules peuvent être réunis. Le critère est la clarté des dépendances et la facilité de test, pas le nombre de fichiers. Si un module devient difficile à nommer ou teste plusieurs responsabilités à la fois, c'est un signal qu'il faut revoir sa frontière.

### 13.2 Dépendances explicites

Épingle les versions testées de Python et des bibliothèques dans le gestionnaire de dépendances du projet. Un fichier de dépendances reproductible n'implique pas que la version soit toujours la plus récente ; cela signifie que les personnes du projet installent et valident une combinaison connue. Mène les mises à jour dans un environnement de test, relance les tests et vérifie les changements d'API avant de déployer.

Ne mélange pas des guides Netmiko 3.x et 4.x sans noter les différences. La version installée est consultable depuis le même interpréteur Python que celui qui lance le script :

```bash
python -c "import netmiko; print(netmiko.__version__)"
python -m pip show netmiko
python -m pip check
```

Le choix de `python -m pip` limite le risque d'installer un paquet dans un autre interpréteur que celui exécutant le script. Si le projet utilise un environnement virtuel, active-le ou appelle directement son exécutable Python.

## 14. Tests automatisés sans équipement réel

Un cours intermédiaire doit réduire la dépendance aux laboratoires physiques pour les cas de test courants. On ne peut pas simuler tous les aspects du protocole SSH avec de simples fixtures, mais on peut tester à peu de frais le chargement d'inventaire, le parsing, la validation, la normalisation, la sélection des commandes et la génération de rapports.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 500" role="img" aria-labelledby="d11title d11desc" width="1200" height="500">
<title id="d11title">Tester sans dépendre du routeur à chaque exécution</title><desc id="d11desc">La plupart des erreurs de parsing, validation et rapport se testent localement.</desc>
<defs><linearGradient id="d11bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d11arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d11h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d11sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d11title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d11body{font:14px system-ui,sans-serif;fill:#dbeafe}.d11edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d11arrow);animation:d11move 1.2s linear infinite}@keyframes d11move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d11edge{animation:none}}</style></defs>
<rect width="1200" height="500" rx="24" fill="url(#d11bg)"/><text x="42" y="48" class="d11h">Tester sans dépendre du routeur à chaque exécution</text><text x="42" y="77" class="d11sub">La plupart des erreurs de parsing, validation et rapport se testent localement.</text><path class="d11edge" d="M382 270 L420 270"/><path class="d11edge" d="M770 270 L808 270"/><rect x="42" y="145" width="340" height="260" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="61" y="175" class="d11title">1. Tests unitaires</text><text x="61" y="207" class="d11body">Parser sur fixtures</text><text x="61" y="229" class="d11body">Validation sur valeurs connues</text><text x="61" y="251" class="d11body">Fonctions pures</text><text x="61" y="273" class="d11body">Rapports JSON / CSV</text><rect x="430" y="145" width="340" height="260" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="449" y="175" class="d11title">2. Tests d’intégration</text><text x="449" y="207" class="d11body">Inventaire → collecteur</text><text x="449" y="229" class="d11body">Exceptions simulées</text><text x="449" y="251" class="d11body">Résultat partiel</text><text x="449" y="273" class="d11body">Sessions fermées</text><rect x="818" y="145" width="340" height="260" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="837" y="175" class="d11title">3. Laboratoire contrôlé</text><text x="837" y="207" class="d11body">SSH réel</text><text x="837" y="229" class="d11body">Plateforme connue</text><text x="837" y="251" class="d11body">Cible non critique</text><text x="837" y="273" class="d11body">Plan d’arrêt et rollback</text></svg>



### 14.1 Tests unitaires du parseur

```python
import unittest


class ParseTests(unittest.TestCase):
    def test_parse_interface_brief(self):
        sample = """Interface IP-Address OK? Method Status Protocol
GigabitEthernet0/0 192.0.2.1 YES manual up up
GigabitEthernet0/1 unassigned YES unset administratively down down
"""
        rows = parse_interface_brief(sample)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["interface"], "GigabitEthernet0/0")
        self.assertEqual(rows[0]["ip_address"], "192.0.2.1")
        self.assertIsNone(rows[1]["ip_address"])

    def test_parse_empty_input(self):
        self.assertEqual(parse_interface_brief(""), [])


if __name__ == "__main__":
    unittest.main()
```

Le test d'entrée vide est important : il garantit le comportement du code, mais il ne doit pas être confondu avec l'acceptation métier d'une collecte vide. Une commande de production qui devrait retourner des interfaces ne devient pas conforme parce que le parseur renvoie une liste vide sans exception. La couche d'orchestration doit vérifier le résultat attendu.

### 14.2 Tester les dépendances avec des mocks

Pour vérifier que ta logique transmet les paramètres prévus sans établir de véritable connexion, utilise `unittest.mock`. Le mock remplace la dépendance réseau dans le test ; il ne prouve pas que le protocole SSH, le driver constructeur ou la plateforme physique fonctionnent. Ces aspects restent du ressort d'un test d'intégration sur un laboratoire contrôlé.

```python
from unittest import TestCase
from unittest.mock import patch


class ConnectionFactoryTests(TestCase):
    @patch("netauto.connection.ConnectHandler")
    def test_factory_uses_host_key_validation(self, connect_handler):
        connect_handler.return_value.__enter__.return_value = object()
        # Appeler ici la fonction de connexion du projet.
        # Puis vérifier les arguments transmis au constructeur :
        args = connect_handler.call_args.kwargs
        self.assertTrue(args["ssh_strict"])
        self.assertTrue(args["system_host_keys"])
```

Le chemin à patcher doit être celui où la dépendance est importée et utilisée par ton module de production. Si `ConnectHandler` est importé dans `netauto.connection`, c'est ce nom qu'il faut patcher. Le test complet doit aussi préparer les paramètres d'entrée et appeler la fonction réelle du projet ; le fragment ci-dessus montre le principe de l'assertion et n'est pas un test prêt à passer sans cette préparation.

### 14.3 Couverture utile plutôt que couverture décorative

Une couverture élevée n'est pas une garantie d'exactitude. Donne priorité aux cas qui peuvent produire une décision erronée : inventaire mal formé, identifiant manquant, clé d'hôte inconnue, timeout, commande partiellement retournée, résultat de parsing vide, champ attendu absent, échec d'écriture, interruption du processus et tentative de changement sans validation. Chaque bug trouvé en production devrait, lorsque c'est possible, conduire à un test de régression qui échoue avant le correctif et réussit après.

### 14.4 Test d'intégration dans un laboratoire

Un test d'intégration confirme la compatibilité réelle entre version de Netmiko, dépendances SSH, système de l'équipement, commande et comportement du prompt. Utilise un équipement virtuel ou matériel autorisé avec un jeu de commandes limité et non destructif. Enregistre les versions, paramètres non sensibles, comportement attendu et résultat. Ne bascule pas automatiquement les tests d'intégration sur des équipements de production à chaque exécution du test unitaire.

## 15. Ajouter une interface en ligne de commande claire

À mesure que le projet grandit, les variables codées en dur dans `main()` deviennent difficiles à gérer. `argparse`, disponible dans Python, permet de définir des options explicites, de valider certains paramètres et de générer une aide automatiquement.

```python
import argparse
from pathlib import Path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collecte réseau Netmiko en lecture seule"
    )
    parser.add_argument(
        "--inventory", type=Path, required=True,
        help="Chemin de l'inventaire JSON validé",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("runs"),
        help="Répertoire de rapports",
    )
    parser.add_argument(
        "--workers", type=int, default=4,
        help="Nombre maximal de connexions simultanées",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Valide l'inventaire et affiche le plan sans connexion réseau",
    )
    return parser
```

Le `--dry-run` doit être une vraie simulation de planification : charger l'inventaire, vérifier le schéma, valider les commandes, calculer les chemins de sortie, puis afficher ce qui serait fait sans établir de session. Une option qui s'appelle `dry-run` mais ouvre quand même des connexions n'est pas une simulation fiable. De même, le `--workers` doit être validé contre la limite approuvée et ne pas être transmis directement sans contrôle.

### 15.1 Codes de sortie

Définis des codes de sortie cohérents afin que l'outil puisse être utilisé dans un ordonnanceur ou une pipeline CI :

- `0` : exécution terminée conformément à la politique et sans échec critique ;
- `1` : exécution partielle, selon la définition adoptée pour l'équipe ;
- `2` : paramètres de ligne de commande ou inventaire invalide ;
- `3` : échec de l'outil, d'écriture du rapport ou autre incident global.

Ces valeurs sont une convention du projet, pas une convention imposée par Netmiko. Documente le contrat et respecte-le au point d'entrée. Un outil qui termine avec le code zéro alors que la moitié de l'inventaire n'a pas été collectée peut créer une fausse assurance lorsqu'il est appelé automatiquement.

## 16. Comparer un état de référence sans confondre écart et panne

Une collecte devient plus utile lorsqu'elle compare l'état observé à un état attendu défini à part. Cette comparaison s'appelle souvent *drift detection* : elle cherche les différences entre la politique approuvée et l'état actuellement observé. L'écart n'est toutefois pas automatiquement une panne : il peut être prévu, temporaire, lié à une donnée manquante ou provenir d'un problème de collecte.

### 16.1 Une politique simple

```json
{
  "device_id": "dist-01",
  "rules": {
    "required_interfaces_up": ["GigabitEthernet1/0/1", "GigabitEthernet1/0/2"],
    "allowed_software_versions": ["17.9.4", "17.9.5"],
    "max_clock_offset_seconds": 120
  }
}
```

Il s'agit d'une donnée d'exemple : adapte les formats à tes vrais résultats parsés et aux conventions de la plateforme. La liste des interfaces ne doit être comparée qu'après confirmation que la commande et le parseur ont réussi. Si la collecte des interfaces échoue, le résultat de la règle est `unknown` et pas `pass` ou `fail`.

Une sortie de conformité intéressante comprend la valeur attendue, la valeur observée, le résultat, une explication et le lien vers les preuves. Par exemple : « interface attendue active ; état observé administratively down ; règle `required_interfaces_up` en échec ; source `show ip interface brief`, commande réussie ». Cela permet de comprendre l'alerte sans reconstruire toute la collecte.

### 16.2 Éviter les changements automatiques implicites

Ne relie pas immédiatement une détection d'écart à une correction automatique. Les actions auto-remédiées exigent des règles de portée, une évaluation d'impact, des autorisations, des limites de répétition et une validation après changement. Au niveau intermédiaire, l'objectif est de produire une preuve et un plan d'action lisibles avant d'automatiser la correction.

Les règles de comparaison sont souvent révisées au fil du temps. Versionne les règles, date leur approbation, teste les modifications avec des résultats historiques et identifie le responsable métier. Une politique trop stricte peut générer des alertes constantes ; une politique trop permissive peut masquer de réelles dérives.

## 17. Introduire les changements de configuration avec un garde-fou

La lecture et la modification n'ont pas le même profil de risque. Une lecture mal formulée peut solliciter l'équipement ou produire des données trompeuses ; une configuration incorrecte peut couper l'accès de gestion, modifier le routage, exposer des services ou affecter des utilisateurs. Le module intermédiaire doit donc traiter tout changement comme une opération distincte, précédée d'une préparation et suivie d'une vérification indépendante.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 575" role="img" aria-labelledby="d9title d9desc" width="1200" height="575">
<title id="d9title">Une modification doit être une opération contrôlée</title><desc id="d9desc">Le succès d’envoi n’est pas synonyme de réussite de configuration.</desc>
<defs><linearGradient id="d9bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d9arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d9h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d9sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d9title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d9body{font:14px system-ui,sans-serif;fill:#dbeafe}.d9edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d9arrow);animation:d9move 1.2s linear infinite}@keyframes d9move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d9edge{animation:none}}</style></defs>
<rect width="1200" height="575" rx="24" fill="url(#d9bg)"/><text x="42" y="48" class="d9h">Une modification doit être une opération contrôlée</text><text x="42" y="77" class="d9sub">Le succès d’envoi n’est pas synonyme de réussite de configuration.</text><path class="d9edge" d="M292 178 L323 178"/><path class="d9edge" d="M583 178 L614 178"/><path class="d9edge" d="M874 178 L905 178"/><path class="d9edge" d="M1037 230 L760 300"/><path class="d9edge" d="M960 350 L1000 430"/><rect x="42" y="125" width="250" height="105" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="61" y="155" class="d9title">1. Précontrôle</text><text x="61" y="187" class="d9body">Cible et sauvegarde</text><text x="61" y="209" class="d9body">État de référence</text><rect x="333" y="125" width="250" height="105" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="352" y="155" class="d9title">2. Plan / diff</text><text x="352" y="187" class="d9body">Commandes limitées</text><text x="352" y="209" class="d9body">Périmètre défini</text><rect x="624" y="125" width="250" height="105" rx="15" fill="#3f365f" stroke="#c4b5fd" stroke-width="2"/><text x="643" y="155" class="d9title">3. Approbation</text><text x="643" y="187" class="d9body">Dry-run par défaut</text><text x="643" y="209" class="d9body">Confirmation explicite</text><rect x="915" y="125" width="243" height="105" rx="15" fill="#7f1d1d" stroke="#fca5a5" stroke-width="2"/><text x="934" y="155" class="d9title">4. Appliquer</text><text x="934" y="187" class="d9body">Une cible à la fois</text><text x="934" y="209" class="d9body">Timeout encadré</text><rect x="560" y="300" width="400" height="100" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="579" y="330" class="d9title">5. Vérification indépendante</text><text x="579" y="362" class="d9body">État attendu + critères concrets</text><rect x="800" y="430" width="358" height="102" rx="15" fill="#334155" stroke="#cbd5e1" stroke-width="2"/><text x="819" y="460" class="d9title">6. Décision</text><text x="819" y="492" class="d9body">Validé : archiver / documenter</text><text x="819" y="514" class="d9body">Échec : escalade / rollback préparé</text><rect x="42" y="300" width="450" height="232" rx="15" fill="#0b1320" stroke="#49637b" stroke-width="2"/><text x="61" y="330" class="d9title">Garde-fous non négociables</text><text x="61" y="362" class="d9body">Allowlist de cibles et commandes</text><text x="61" y="384" class="d9body">Sauvegarde et critères d’arrêt</text><text x="61" y="406" class="d9body">Pas de retry aveugle sur mutation</text><text x="61" y="428" class="d9body">Confirmation explicite</text><text x="61" y="450" class="d9body">Plan de retour arrière</text></svg>



### 17.1 Cycle recommandé

1. **Périmètre :** sélectionner les cibles et confirmer qu'elles sont autorisées.
2. **État initial :** collecter les données nécessaires, sauvegarder la configuration selon la procédure approuvée et vérifier l'accès de gestion.
3. **Plan :** définir l'état attendu, les commandes exactes et la méthode de validation.
4. **Dry-run :** afficher le plan et le diff sans appliquer de commandes.
5. **Approbation :** validation humaine selon le processus de changement du site.
6. **Application limitée :** commencer par un équipement de laboratoire ou un canari, avec un plafond de concurrence faible.
7. **Vérification :** contrôler l'état réellement obtenu, la connectivité et les métriques qui comptent.
8. **Arrêt ou restauration :** si la vérification échoue, interrompre le lot et suivre le plan de restauration autorisé.
9. **Rapport :** conserver la chronologie, l'approbation, les résultats et les écarts.

### 17.2 Garder l'application désactivée par défaut

Le fragment ci-dessous illustre un garde-fou de commande. Il ne contient pas de commandes de configuration prêtes à l'emploi, puisque celles-ci doivent être spécifiques au constructeur, approuvées et testées dans le laboratoire correspondant.

```python
import argparse


def require_apply_confirmation(args):
    if not args.apply:
        print("DRY-RUN : aucune commande de configuration envoyée.")
        return False
    if args.change_id is None or not args.change_id.strip():
        raise ValueError("--apply exige un identifiant de changement approuvé")
    if args.approval_token != "APPROVED-IN-CHANGE-WINDOW":
        raise ValueError("L'approbation attendue n'a pas été fournie")
    return True


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
parser.add_argument("--change-id")
parser.add_argument("--approval-token")
args = parser.parse_args()

if require_apply_confirmation(args):
    raise NotImplementedError(
        "Brancher ici uniquement le moteur de changement validé du projet."
    )
```

Le texte `APPROVED-IN-CHANGE-WINDOW` est un garde-fou didactique, pas un mécanisme d'approbation de sécurité à lui seul. En production, l'autorisation doit provenir d'un processus authentifié et auditable ; une chaîne de texte saisie sur la ligne de commande est facile à copier et ne prouve pas qu'une personne possède les droits requis.

### 17.3 Vérification après modification

Le code de configuration qui retourne sans exception n'est pas la preuve que l'état attendu a été atteint. Un équipement peut accepter une commande mais conserver un état différent, ignorer une partie, appliquer une modification incomplète ou perdre sa session au milieu de la séquence. Après changement, collecte le même indicateur d'état que celui spécifié dans la validation, compare la sortie à l'attendu et marque l'équipement comme `verified`, `failed_verification` ou `unknown`.

La restauration elle-même est une opération de changement, pas un geste magique. La sauvegarde peut être incomplète, l'état a pu évoluer depuis sa création ou la restauration peut être inappropriée. Un plan de rollback doit indiquer qui l'autorise, quelles commandes seront exécutées, comment vérifier le rétablissement et ce qu'il faut faire en cas de perte de connexion.

## 18. Projet final : contrôleur de flotte en lecture seule

Le projet de synthèse combine les acquis du cours débutant avec les mécanismes intermédiaires. Le résultat attendu est un petit programme réutilisable : il lit l'inventaire, valide les données, utilise les identifiants à partir d'une source prévue, collecte des commandes en lecture seule, convertit les résultats en données structurées, applique des règles de validation, écrit des rapports et expose des codes de sortie fiables.



<svg xmlns="http://www.w3.org/2000/svg"   viewBox="0 0 1200 580" role="img" aria-labelledby="d12title d12desc" width="1200" height="580">
<title id="d12title">Livrable attendu à la fin du niveau intermédiaire</title><desc id="d12desc">Un collecteur qui explique ses résultats et ne modifie rien par surprise.</desc>
<defs><linearGradient id="d12bg" x2="1" y2="1"><stop stop-color="#0e1726"/><stop offset="1" stop-color="#203952"/></linearGradient><marker id="d12arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#67e8f9"/></marker>
<style>.d12h{font:700 27px system-ui,sans-serif;fill:#f8fafc}.d12sub{font:15px system-ui,sans-serif;fill:#c4d4e6}.d12title{font:700 18px system-ui,sans-serif;fill:#f8fafc}.d12body{font:14px system-ui,sans-serif;fill:#dbeafe}.d12edge{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 8;marker-end:url(#d12arrow);animation:d12move 1.2s linear infinite}@keyframes d12move{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.d12edge{animation:none}}</style></defs>
<rect width="1200" height="580" rx="24" fill="url(#d12bg)"/><text x="42" y="48" class="d12h">Livrable attendu à la fin du niveau intermédiaire</text><text x="42" y="77" class="d12sub">Un collecteur qui explique ses résultats et ne modifie rien par surprise.</text><path class="d12edge" d="M272 187 L312 187"/><path class="d12edge" d="M552 187 L592 187"/><path class="d12edge" d="M832 187 L872 187"/><rect x="42" y="135" width="230" height="105" rx="15" fill="#203b78" stroke="#7eb5ff" stroke-width="2"/><text x="61" y="165" class="d12title">Inventaire</text><text x="61" y="197" class="d12body">JSON + groupes</text><text x="61" y="219" class="d12body">Sans secrets</text><rect x="322" y="135" width="230" height="105" rx="15" fill="#164e63" stroke="#67e8f9" stroke-width="2"/><text x="341" y="165" class="d12title">Collecteur</text><text x="341" y="197" class="d12body">SSH / timeouts</text><text x="341" y="219" class="d12body">Fermeture garantie</text><rect x="602" y="135" width="230" height="105" rx="15" fill="#3f365f" stroke="#c4b5fd" stroke-width="2"/><text x="621" y="165" class="d12title">Parser + validateur</text><text x="621" y="197" class="d12body">Données typées</text><text x="621" y="219" class="d12body">Anomalies visibles</text><rect x="882" y="135" width="276" height="105" rx="15" fill="#14532d" stroke="#86efac" stroke-width="2"/><text x="901" y="165" class="d12title">Rapports et tests</text><text x="901" y="197" class="d12body">JSON / CSV / métriques</text><text x="901" y="219" class="d12body">Tests reproductibles</text><rect x="42" y="302" width="520" height="225" rx="15" fill="#0b1320" stroke="#49637b" stroke-width="2"/><text x="61" y="332" class="d12title">Critères d’acceptation</text><text x="61" y="364" class="d12body">Un échec ne supprime pas les autres résultats</text><text x="61" y="386" class="d12body">Chaque résultat a une cible, un temps et un statut</text><text x="61" y="408" class="d12body">Le parser est couvert par des fixtures</text><text x="61" y="430" class="d12body">Les secrets restent hors du code et des rapports</text><text x="61" y="452" class="d12body">La synthèse distingue succès, partiel et échec</text><rect x="602" y="302" width="556" height="225" rx="15" fill="#3d1f27" stroke="#fda4af" stroke-width="2"/><text x="621" y="332" class="d12title">Branche séparée : changement contrôlé</text><text x="621" y="364" class="d12body">Précontrôle → sauvegarde → plan → approbation</text><text x="621" y="386" class="d12body">Application → vérification → résultat archivé</text><text x="621" y="408" class="d12body">Désactivée par défaut dans le projet pédagogique</text><text x="621" y="430" class="d12body">Aucune exécution en production sans procédure approuvée</text></svg>



### 18.1 Cahier des charges fonctionnel

Le programme devra :

- accepter un inventaire JSON et un répertoire de sortie par arguments CLI ;
- valider les types, les champs obligatoires, le port, le nom et l'unicité des cibles ;
- ne jamais stocker les mots de passe dans le fichier d'inventaire ;
- valider la clé SSH de chaque hôte selon la politique de confiance ;
- exécuter une liste définie de commandes de lecture seule par type d'équipement ;
- mesurer les durées de connexion et de commande ;
- distinguer connexion impossible, authentification échouée, commande échouée, parsing échoué et validation non conforme ;
- permettre de limiter le nombre de sessions simultanées ;
- produire un fichier JSON de résultat et un résumé destiné à l'opérateur ;
- conserver les sorties brutes nécessaires au diagnostic dans un espace protégé ;
- avoir des tests unitaires des validateurs et parseurs sans accès réseau ;
- fournir un `--dry-run` qui n'établit aucune connexion ;
- arrêter avec un code de sortie significatif en fonction des résultats.

### 18.2 Modèle du résultat global

```json
{
  "run_id": "2026-10-23T22-55-00Z_a1b2c3",
  "started_at": "2026-10-23T22:55:00Z",
  "finished_at": "2026-10-23T22:55:17Z",
  "status": "partial",
  "inventory_count": 6,
  "success_count": 4,
  "partial_count": 1,
  "failed_count": 1,
  "devices": [],
  "summary": {
    "commands_failed": 2,
    "parse_failures": 1,
    "validation_failures": 1
  }
}
```

Les valeurs sont fictives. Le rapport effectif doit inclure les résultats par équipement et définir explicitement comment le statut global est calculé. Si les données d'une seule cible sont critiques, la politique peut exiger un échec global même si les autres cibles ont réussi. Pour une collecte d'inventaire non critique, un état `partial` accompagné d'une alerte peut être plus utile. La politique doit être documentée et cohérente avec l'usage de l'outil.

### 18.3 Critères d'acceptation

Le projet est considéré réussi lorsque : l'inventaire invalide est refusé avant la connexion ; aucun secret ne paraît dans les rapports ni les journaux ; les clés SSH inconnues ne sont pas acceptées automatiquement ; une panne sur une cible ne perd pas les résultats des autres ; une sortie inattendue est marquée comme non reconnue ; chaque session est fermée ; les fichiers sont écrits proprement ; le mode simulation n'ouvre aucune session ; les tests unitaires passent ; et la collecte a été vérifiée sur un petit laboratoire autorisé.

### 18.4 Étapes de réalisation

Réalise le projet par incréments. Commence par valider l'inventaire sans réseau. Ajoute ensuite une seule cible et une commande. Ajoute les statuts de résultat et les journaux. Ajoute le parsing et ses tests. Ajoute plusieurs cibles en séquentiel. Ce n'est qu'après que la version séquentielle est fiable qu'il faut introduire la concurrence bornée. Enfin, construis le rapport global, la simulation et les codes de sortie.

Cette progression permet d'identifier quelle modification a introduit une régression. Si tu écris toutes les couches avant de les tester, la première erreur peut provenir de l'environnement, de l'inventaire, de la session SSH, du parser, du rapport ou du programme principal ; le diagnostic devient inutilement difficile.

## 19. Diagnostic méthodique des incidents courants

### 19.1 Le script fonctionne sur ton ordinateur, mais pas sur celui d'un collègue

Compare l'interpréteur Python, les versions des dépendances, le système d'exploitation, les permissions, les variables d'environnement, le chemin du `known_hosts` et les différences d'accès réseau. Lance `python -m pip show netmiko` dans l'environnement réellement utilisé. Le script ne devrait pas dépendre du répertoire de travail implicite ni d'un paquet installé globalement par hasard.

### 19.2 La commande expire alors que la session est active

Capture la sortie brute de la commande, relève le prompt, vérifie la pagination, le temps d'exécution normal et les options `read_timeout`. Vérifie que le driver Netmiko correspond au type exact de l'équipement. Une commande qui produit beaucoup de lignes peut exiger un délai adapté, mais augmenter la temporisation sans vérifier le prompt peut masquer une commande incompatible ou une sortie tronquée.

### 19.3 Le parsing renvoie une liste vide

Vérifie la sortie brute, le couple plateforme/commande, la version des modèles NTC Templates et la configuration des templates. Ajoute la sortie à un fixture nettoyé, puis crée un test reproduisant le problème. Une liste vide doit donner lieu à un statut d'analyse qui indique le résultat inattendu au lieu de laisser une validation en aval supposer qu'aucune interface n'existe.

### 19.4 Les erreurs apparaissent surtout en parallèle

Réduis le nombre de workers, désactive les reprises pour isoler le phénomène, distingue les erreurs de connexion et d'authentification et compare les journaux du bastion/AAA. Un succès séquentiel et un échec en parallèle peuvent signaler une limite de sessions ou une charge de gestion excessive. La solution n'est pas nécessairement de monter le délai ou d'augmenter encore le nombre de workers.

### 19.5 Le rapport dit `success`, mais la donnée est fausse

Examine la différence entre succès technique et conformité métier. La session et la commande peuvent s'être déroulées correctement alors que la sortie a été mal comprise, que le parser a ignoré une ligne ou que la règle attendue est trop permissive. Ajoute un cas de test pour la sortie qui pose problème, corrige le parser ou la règle, puis relance la vérification sur des données historiques représentatives.

### 19.6 Une clé SSH change après remplacement de l'équipement

Un changement de clé est une information de sécurité, pas une nuisance à éliminer automatiquement. Vérifie le dossier de remplacement par une source indépendante, confirme la nouvelle empreinte avec la procédure prévue, puis mets à jour le magasin de confiance selon la politique. Ne contourne pas la vérification par une option qui accepte silencieusement n'importe quelle clé présentée.

## 20. Sécurité et gouvernance à l'échelle intermédiaire

Le script devient un outil d'exploitation lorsqu'il peut accéder à une flotte : ses privilèges, sa trace d'exécution et ses données doivent donc être traités comme des éléments d'infrastructure.

**Principe du moindre privilège.** Utilise un compte réseau dédié, avec les commandes et niveaux d'accès nécessaires au rôle de collecte. Si le constructeur permet une autorisation par commande, privilégie une politique qui n'accorde pas un mode privilégié global lorsque cela n'est pas nécessaire. Teste les privilèges effectifs : un prompt accessible ne garantit pas que chaque commande soit autorisée.

**Secrets.** Évite le stockage permanent en clair, la saisie de mot de passe dans des arguments de processus et l'inclusion de secrets dans les logs. Prévois rotation, accès limité et révocation. Une variable d'environnement réduit la présence du secret dans le source, mais ne suffit pas comme système de coffre à elle seule.

**Traçabilité.** Pour chaque exécution, conserve identifiant de tâche, utilisateur ou compte de service, version du programme, version de configuration, liste des cibles et résultat. Pour une opération de changement, conserve aussi l'identifiant d'approbation, le plan, le résultat de vérification et la décision de restauration. La traçabilité doit être complète sans enregistrer les secrets eux-mêmes.

**Protection des rapports.** Les sorties CLI peuvent contenir des noms internes, des adresses IP, des noms d'utilisateur, des topologies et d'autres informations sensibles. Limite l'accès, chiffre les stockages appropriés, définis une rétention et sépare les rapports de synthèse des sorties brutes. Prépare des fixtures nettoyés pour le partage et les tests.

**Droits d'exploitation.** Définis qui peut lancer la collecte, qui peut modifier les règles, qui peut approuver un changement et qui peut examiner les résultats. Pour les environnements de production, le droit d'exécuter une collecte en lecture seule ne doit pas automatiquement conférer celui d'exécuter des changements de configuration.

## 21. Exercices pratiques gradués

### Exercice 1 — Inventaire durci

Complète la validation pour refuser une liste vide, un port hors de l'intervalle 1–65535, un `device_type` non supporté par le projet, un nom répété et deux entrées pointant vers le même hôte sans justification. Écris au minimum un test pour chaque règle. L'erreur doit expliquer quel champ est invalide sans afficher de secret.

### Exercice 2 — Reprise maîtrisée

À partir d'un jeu de résultats simulés, crée une politique de reprise qui autorise au plus deux nouvelles tentatives pour certaines erreurs transitoires. Vérifie qu'une erreur d'authentification n'est jamais réessayée automatiquement, que les délais sont bornés et que chaque tentative est journalisée. Ajoute un test pour la dernière tentative.

### Exercice 3 — Parsing testé

Récupère ou crée plusieurs sorties de `show ip interface brief` issues d'un environnement de laboratoire. Écris des fixtures pour une sortie normale, une interface non adressée, un statut inhabituel et une sortie tronquée. Le parser doit soit produire des données exactes, soit signaler explicitement le cas qu'il ne reconnaît pas.

### Exercice 4 — Rapport cohérent

Construis une collecte simulée de cinq cibles dont une ne répond pas, une a une commande en échec et une renvoie un parsing non reconnu. Génère JSON et CSV. Vérifie que le nombre total de cibles reste cinq, que chaque statut individuel est conservé et que le statut global reflète la politique de l'équipe.

### Exercice 5 — Concurrence

Mesure la durée d'une collecte séquentielle et de la même collecte avec deux workers sur un laboratoire adapté. Ajoute ensuite quatre workers, puis compare durée et taux d'erreur. Écris les limites et conclusions ; n'extrapole pas les mesures du petit laboratoire à un parc réel sans nouvelle validation.

### Exercice 6 — Mode simulation

Écris un test prouvant que `--dry-run` charge et valide l'inventaire, affiche les actions planifiées et n'appelle pas `ConnectHandler`. Une simple impression « dry run » ne suffit pas si la connexion a déjà été créée.

### Exercice 7 — Diff et conformité

Compare des enregistrements observés à une politique de test. Distingue `pass`, `fail`, `unknown` et `not_applicable`. Vérifie que l'absence de données n'est jamais convertie implicitement en conformité. Présente pour chaque échec la valeur attendue et la valeur observée.

### Exercice 8 — Préparation au changement contrôlé

Crée une commande qui valide un plan de changement et affiche un diff. Elle doit rester incapable de modifier un équipement tant que le moteur de changement n'est pas connecté à un processus d'approbation réel. Documente le test qui garantit que la voie d'exécution est désactivée par défaut.

## 22. Questions de révision

1. Quelle différence fais-tu entre une collecte partielle et une collecte entièrement réussie ?
2. Pourquoi la validation de l'inventaire devrait-elle précéder l'ouverture des sessions SSH ?
3. Quels problèmes sont traités par `conn_timeout`, `banner_timeout`, `auth_timeout` et `read_timeout` ?
4. Dans quel cas `send_command_timing` peut-il être plus approprié que `send_command`, et pourquoi faut-il être prudent ?
5. Pourquoi une liste TextFSM vide ne prouve-t-elle pas que l'équipement ne possède aucune interface ?
6. Pourquoi faut-il conserver la sortie brute en plus des données parsées ?
7. Quelle différence entre une reprise d'une lecture et une reprise d'un changement de configuration ?
8. Pourquoi les sessions Netmiko ne doivent-elles pas être partagées entre plusieurs threads ?
9. Que doit faire un `dry-run` pour être digne de confiance ?
10. Quelle différence entre état `unknown` et état `non_conforme` ?
11. Pourquoi un rapport JSON doit-il avoir un schéma explicite et un statut global défini ?
12. Pourquoi les clés d'hôtes SSH inconnues ne doivent-elles pas être acceptées automatiquement ?
13. Quels éléments d'une sortie CLI peuvent constituer des données sensibles ?
14. Quelles vérifications faut-il exécuter après un changement de configuration ?
15. Que faudrait-il mesurer avant de choisir le nombre de workers d'une collecte ?

## 23. Liste de contrôle avant de livrer le projet

- [ ] Le projet dispose d'un environnement Python et de dépendances explicitement gérées.
- [ ] La version de Netmiko est documentée et compatible avec les paramètres utilisés.
- [ ] L'inventaire est validé avant toute connexion.
- [ ] Aucun secret n'est commis dans Git ou enregistré dans le rapport.
- [ ] Les clés d'hôtes SSH sont vérifiées selon la politique définie.
- [ ] Les connexions sont fermées même après une erreur.
- [ ] Chaque commande possède un statut et une durée explicites.
- [ ] Les erreurs de connexion, d'authentification, de commande et de parsing sont distinctes.
- [ ] Le parsing est appuyé par des fixtures et des tests.
- [ ] Les règles de validation distinguent `unknown` de `fail`.
- [ ] Les reprises sont limitées, explicites et réservées aux cas appropriés.
- [ ] La concurrence est plafonnée et mesurée.
- [ ] Les rapports sont écrits de façon contrôlée et protégés.
- [ ] Le `dry-run` n'établit aucune connexion et n'applique aucun changement.
- [ ] Les modifications de configuration sont séparées de la collecte.
- [ ] Un test d'intégration a été réalisé dans un environnement autorisé.
- [ ] Le compte rendu expose les limites et les erreurs partielles au lieu de les masquer.

## 24. Transition vers le niveau Expert

La progression se poursuit à partir de ce socle. Au niveau Expert, l'objectif ne sera pas de remplacer l'architecture ci-dessus, mais de l'éprouver et de la pousser plus loin : intégrer un système de gestion de secrets, gérer de grands inventaires et des files de tâches, développer ou choisir des drivers spécifiques, comparer les états déclaratifs et effectifs, tester les changements avec des mécanismes de canari et de rollback, gérer une observabilité de flotte et mesurer la fiabilité de l'automatisation elle-même.

Les compétences intermédiaires constituent les prérequis du niveau Expert : inventaire fiable, secret hors du code, politique de clés SSH, résultat structuré, parser testé, gestion d'erreurs explicite, concurrence bornée, rapports reproductibles et séparation lecture/changement. Si ces éléments ne sont pas solides, la complexité supplémentaire amplifie les défauts au lieu de rendre l'automatisation plus professionnelle.

Le fil directeur de la série reste le même : chaque niveau réutilise les acquis du précédent, et ajoute des garanties techniques et opérationnelles. Un bon outil réseau n'est pas celui qui envoie le plus de commandes ; c'est celui qui sait ce qu'il fait, peut expliquer ce qu'il a observé, reconnaît quand il ne sait pas, protège les systèmes et laisse une trace vérifiable.

## 25. Références techniques officielles

Les interfaces, paramètres et comportements dépendent de la version installée. Contrôle ces références lors de la mise à jour du projet :

- [Dépôt officiel Netmiko](https://github.com/ktbyers/netmiko) — versions, prise en charge des plateformes et historique des changements.
- [Documentation de `BaseConnection`](https://github.com/ktbyers/netmiko/blob/develop/docs/netmiko/base_connection.html) — paramètres de connexion, délais, vérification des clés et méthodes d'envoi.
- [Documentation officielle Netmiko](https://ktbyers.github.io/netmiko/) — guides et références de l'API.
- [NTC Templates](https://github.com/networktocode/ntc-templates) — modèles TextFSM maintenus pour de nombreuses commandes et plateformes.
- [Documentation TextFSM](https://github.com/google/textfsm) — mécanisme de parsing de sorties textuelles vers des enregistrements structurés.
- [Documentation Python `argparse`](https://docs.python.org/3/library/argparse.html) — interface en ligne de commande.
- [Documentation Python `logging`](https://docs.python.org/3/library/logging.html) — journalisation configurable.
- [Documentation Python `unittest`](https://docs.python.org/3/library/unittest.html) — tests automatisés et assertions.

### Conclusion opérationnelle

Le passage du débutant à l'intermédiaire est le passage d'un script qui fonctionne sur un équipement à un programme sur lequel une équipe peut raisonnablement s'appuyer. Cela exige des entrées validées, des identifiants protégés, des clés SSH vérifiées, des sessions bien fermées, des délais mesurés, des erreurs distinctes, des données normalisées, des tests hors réseau, une concurrence contrôlée et des rapports qui décrivent honnêtement la réussite comme l'échec.

Le cours expert pourra ensuite s'appuyer sur ces bases pour construire une automatisation à l'échelle d'une exploitation réelle. Tant que l'outil ne distingue pas une commande réussie d'une donnée fiable, une erreur transitoire d'une erreur de sécurité, et une collecte d'un changement de configuration, il ne doit pas être autorisé à réparer automatiquement le réseau. La maîtrise commence par la mesure, la validation et la capacité d'expliquer le résultat.
