# Automatisation réseau — Niveau débutant

## Comprendre, préparer et construire les bases de l'automatisation réseau


## Présentation du cours

L'automatisation réseau consiste à utiliser des programmes et des outils pour exécuter des opérations d'administration de manière répétable, contrôlée et vérifiable.

Au lieu de se connecter manuellement à chaque routeur ou commutateur pour effectuer toujours les mêmes opérations, l'administrateur décrit les tâches à exécuter, les équipements concernés, les résultats attendus et les règles de sécurité.

L'automatisation ne consiste pas simplement à remplacer les commandes tapées au clavier par un script. Elle demande une méthode : comprendre les opérations, structurer les données, vérifier les entrées, contrôler les erreurs et confirmer les résultats.

Ce cours pose les fondations nécessaires avant d'aborder les connexions multi-équipements, les sauvegardes automatisées, les comparaisons de configurations et les déploiements plus avancés.

### Positionnement dans le parcours

Ce cours appartient à une progression en trois niveaux :

```text
PARCOURS COMPLET D'AUTOMATISATION RÉSEAU
========================================

                 NIVEAU 1
                 DÉBUTANT
                    |
                    v
       Comprendre les principes fondamentaux
       Découvrir Python et les données JSON
       Construire un inventaire d'équipements
       Valider les données avant toute action
       Comprendre SSH et les règles de sécurité
       Réaliser un premier projet sans risque
                    |
                    v
               NIVEAU 2
             INTERMÉDIAIRE
                    |
                    v
       Réutiliser le projet du niveau débutant
       Se connecter à plusieurs équipements
       Exécuter des commandes en lecture seule
       Automatiser les sauvegardes
       Comparer les résultats
       Produire des rapports et traiter les erreurs
                    |
                    v
                NIVEAU 3
                 EXPERT
                    |
                    v
       Définir un état réseau attendu
       Contrôler la conformité
       Tester les changements
       Gérer les déploiements et le retour arrière
       Organiser les journaux et la traçabilité
       Intégrer l'automatisation à une chaîne CI/CD
```

**Règle pédagogique :** les trois niveaux constituent une seule progression. Le cours intermédiaire devra reprendre le projet construit ici, et le cours expert devra prolonger les réalisations du niveau intermédiaire.


## Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit être capable de :

1. Expliquer le rôle de l'automatisation dans l'administration réseau.
2. Distinguer une opération manuelle, un script ponctuel et un processus automatisé contrôlé.
3. Identifier les composants d'une architecture d'automatisation.
4. Comprendre le rôle de Python dans l'automatisation réseau.
5. Lire et exploiter un inventaire JSON.
6. Écrire un script Python qui valide des données.
7. Comprendre le rôle de SSH dans l'administration distante.
8. Identifier les risques liés aux identifiants, aux autorisations et aux modifications de configuration.
9. Expliquer les différences entre observation, sauvegarde et comparaison.
10. Construire un premier projet d'automatisation reproductible.
11. Préparer le projet pour les développements du niveau intermédiaire.

## Prérequis

Il est recommandé de connaître les notions suivantes :

- Le rôle d'un routeur et d'un commutateur.
- Les bases de l'adressage IPv4.
- Les principes élémentaires des VLAN.
- Le rôle d'une configuration réseau.
- La différence entre un équipement réseau et un poste d'administration.
- Les bases de l'utilisation d'un terminal.

La maîtrise de Python n'est pas nécessaire. Les exemples de code sont expliqués progressivement.

## Environnement pédagogique

Les exercices sont conçus pour être réalisés dans un laboratoire. Les adresses IP et les équipements cités dans les exemples sont fictifs.

**Aucune commande de modification de configuration n'est nécessaire pour réussir ce cours.** L'objectif est d'apprendre à préparer et à valider une automatisation avant de l'utiliser sur des équipements.


# PARTIE 1 — COMPRENDRE L'AUTOMATISATION RÉSEAU

## 1. Pourquoi automatiser un réseau ?

Imaginons une entreprise qui possède :

- 2 routeurs ;
- 15 commutateurs ;
- 3 pare-feu ;
- plusieurs sites distants.

L'administrateur doit vérifier régulièrement les versions logicielles, récupérer des informations, contrôler certains paramètres et conserver des sauvegardes.

Si chaque opération est réalisée manuellement sur chaque équipement, le travail peut devenir long et difficile à reproduire exactement.

Une personne peut oublier un équipement, copier une information au mauvais endroit ou exécuter une commande différente de celle prévue.

L'automatisation permet de décrire ces tâches dans un programme et d'établir un processus cohérent.

### 1.1 Exemple d'une opération manuelle

```text
ADMINISTRATEUR
      |
      v
Se connecte au routeur R1
      |
      v
Exécute une commande
      |
      v
Copie le résultat
      |
      v
Se déconnecte
      |
      v
Se connecte au commutateur SW1
      |
      v
Recommence les mêmes opérations
      |
      v
Recommence sur les équipements suivants
```

Cette méthode peut convenir pour un dépannage ponctuel ou pour apprendre à administrer un équipement.

Elle devient moins pratique lorsqu'une opération identique doit être répétée régulièrement sur un grand nombre de systèmes.

### 1.2 La même opération avec un processus automatisé

```text
ADMINISTRATEUR
      |
      v
Définit l'objectif
      |
      v
Prépare l'inventaire
      |
      v
Lance le programme
      |
      v
Le programme contrôle les données
      |
      v
Les équipements autorisés sont traités
      |
      +-----------------------+
      |                       |
      v                       v
Résultats enregistrés    Erreurs signalées
      |                       |
      +-----------+-----------+
                  |
                  v
         Rapport vérifiable
                  |
                  v
        Contrôle par l'humain
```

L'administrateur conserve la responsabilité de définir ce qui doit être exécuté et de vérifier que les résultats sont acceptables.

## 2. Les avantages de l'automatisation

### 2.1 Répétabilité

Une tâche peut être exécutée plusieurs fois avec la même procédure.

Par exemple, un script peut contrôler chaque matin la disponibilité d'un ensemble d'équipements.

La répétabilité ne garantit pas à elle seule que le programme est correct. Un script mal conçu peut répéter une erreur à chaque exécution.

### 2.2 Cohérence

Les mêmes contrôles et les mêmes règles peuvent être appliqués à plusieurs équipements.

Cela réduit les différences dues aux habitudes de travail de chaque administrateur.

### 2.3 Gain de temps

Le programme peut accomplir les étapes répétitives pendant que l'administrateur se concentre sur l'analyse des résultats et la résolution des problèmes.

### 2.4 Traçabilité

Un processus bien conçu peut conserver :

- La date de l'exécution.
- Les équipements traités.
- Les opérations réalisées.
- Les résultats obtenus.
- Les erreurs rencontrées.
- Le statut final de chaque opération.

Ces informations facilitent le diagnostic et l'audit.

### 2.5 Réduction de certaines erreurs humaines

L'automatisation peut éviter des oublis et des erreurs de saisie lorsque les tâches sont correctement définies et testées.

Elle n'élimine cependant pas toutes les erreurs. Le code, les données et les décisions de conception peuvent eux-mêmes être incorrects.

## 3. Les limites de l'automatisation

L'automatisation présente aussi des risques.

Un programme peut :

- Utiliser une mauvaise adresse IP.
- Se connecter au mauvais équipement.
- Répéter une commande dangereuse.
- Écraser une sauvegarde précédente.
- Exposer des identifiants.
- Continuer après un échec sans le signaler correctement.
- Appliquer une modification à trop d'équipements.

Le nombre d'équipements traités ne doit jamais être considéré comme une mesure suffisante de la qualité d'une automatisation.

### Schéma — amplification possible d'une erreur

```text
Une erreur dans le code
        |
        v
Le programme démarre
        |
        v
Le programme répète l'opération
        |
        +----> Équipement 1
        |
        +----> Équipement 2
        |
        +----> Équipement 3
        |
        +----> Équipement 4
        |
        v
Plusieurs équipements affectés
```

La même automatisation, correctement testée, peut aussi prévenir des erreurs répétitives.

La qualité dépend donc de la conception, de la validation, des essais et des mécanismes de contrôle.

### Règle essentielle

**Automatiser une opération sans comprendre son effet revient à reproduire une action dont on ne maîtrise pas les conséquences.**

Avant d'automatiser une tâche, l'administrateur doit connaître :

1. Son objectif.
2. Son fonctionnement manuel.
3. Ses effets potentiels.
4. Son résultat attendu.
5. Ses erreurs possibles.
6. Les moyens de vérifier le résultat.
7. La procédure de reprise en cas de problème.


# PARTIE 2 — LES NIVEAUX D'AUTOMATISATION

## 4. Distinguer les approches

Toutes les automatisations n'ont pas le même degré de maturité.

### 4.1 Administration manuelle

L'administrateur se connecte directement à l'équipement et exécute les commandes.

Exemple :

```text
Administrateur
      |
      v
Connexion SSH
      |
      v
Commande de vérification
      |
      v
Lecture de la réponse
```

Cette méthode reste importante pour apprendre et pour les opérations ponctuelles.

### 4.2 Script ponctuel

Un programme exécute une série d'instructions.

Exemple :

```text
Script Python
      |
      v
Lit une liste de cibles
      |
      v
Exécute une opération
      |
      v
Affiche les résultats
```

Le script réduit la répétition manuelle, mais il peut rester fragile si les données ne sont pas validées ou si les erreurs ne sont pas traitées.

### 4.3 Automatisation contrôlée

Une automatisation mieux conçue ajoute :

- Des contrôles des données.
- Des limites sur les équipements concernés.
- Une gestion des erreurs.
- Des journaux.
- Une validation du résultat.
- Une procédure d'arrêt.
- Une stratégie de récupération.

```text
              INVENTAIRE
                  |
                  v
          VALIDATION DES DONNÉES
                  |
                  v
          VÉRIFICATION DU PÉRIMÈTRE
                  |
                  v
          EXÉCUTION DE L'OPÉRATION
                  |
          +-------+-------+
          |               |
          v               v
      Succès            Échec
          |               |
          v               v
  Résultat stocké    Erreur journalisée
          |               |
          +-------+-------+
                  |
                  v
          RAPPORT FINAL
                  |
                  v
       Vérification humaine
```

Le niveau débutant permet de construire la base de cette démarche.


# PARTIE 3 — COMPRENDRE L'ARCHITECTURE

## 5. Les composants d'un système d'automatisation

Un processus d'automatisation réseau peut être représenté avec plusieurs composants.

```text
+----------------------------------------+
| ADMINISTRATEUR                         |
| Définit l'objectif et les règles       |
+-------------------+--------------------+
                    |
                    v
+----------------------------------------+
| INVENTAIRE                             |
| Noms, adresses, rôles, plateformes     |
+-------------------+--------------------+
                    |
                    v
+----------------------------------------+
| PROGRAMME D'AUTOMATISATION              |
| Lecture, validation, traitement        |
+-------------------+--------------------+
                    |
                    v
+----------------------------------------+
| MÉCANISME DE COMMUNICATION              |
| SSH ou interface adaptée               |
+-------------------+--------------------+
                    |
             +------+------+
             |      |      |
             v      v      v
           ROUTEUR SWITCH  PARE-FEU
             |      |      |
             +------+------+
                    |
                    v
+----------------------------------------+
| RÉSULTATS ET JOURNAUX                   |
| Réponses, états, erreurs               |
+-------------------+--------------------+
                    |
                    v
+----------------------------------------+
| CONTRÔLE ET ANALYSE                     |
| Vérification des résultats             |
+----------------------------------------+
```

## 6. Le rôle de chaque composant

### 6.1 L'administrateur

Il définit l'objectif, choisit les équipements concernés, fixe les contraintes et vérifie les résultats.

L'automatisation ne supprime pas la nécessité de comprendre les besoins métier et les conséquences techniques.

### 6.2 L'inventaire

L'inventaire contient les informations nécessaires pour identifier les systèmes à traiter.

Il peut notamment contenir :

- Un nom logique.
- Une adresse IP ou un nom DNS.
- Une plateforme.
- Un rôle.
- Un environnement.
- Des informations de regroupement.

Il ne devrait pas servir de fichier contenant des mots de passe en clair.

### 6.3 Le programme

Le programme lit les données et applique les règles définies.

Il peut, selon son objectif :

1. Valider les entrées.
2. Sélectionner les équipements.
3. Établir les connexions nécessaires.
4. Exécuter une opération autorisée.
5. Enregistrer les résultats.
6. Signaler les erreurs.
7. Produire un rapport.

### 6.4 Le mécanisme de communication

Le programme utilise un protocole ou une interface appropriée pour communiquer avec les équipements.

SSH est courant dans l'administration réseau, mais il ne constitue pas le seul mécanisme possible.

Le choix dépend du matériel, du système d'exploitation réseau, des interfaces disponibles et de la tâche à réaliser.

### 6.5 Les résultats

Les résultats peuvent être conservés sous plusieurs formes :

- Fichier texte.
- Fichier JSON.
- Rapport CSV.
- Journaux d'exécution.
- Sauvegarde de configuration.
- Rapport de différences.

Le format dépend du besoin. Il doit être facile à lire et à exploiter.


# PARTIE 4 — DÉCOUVRIR PYTHON

## 7. Pourquoi utiliser Python ?

Python est un langage de programmation qui permet de lire des fichiers, manipuler des données, traiter des erreurs et communiquer avec des systèmes externes grâce à des bibliothèques adaptées.

Il est utilisé dans de nombreux projets d'administration système et réseau.

Dans ce cours, Python sert principalement à :

- Lire un inventaire.
- Vérifier la structure des données.
- Détecter des entrées incorrectes.
- Produire un résultat lisible.
- Préparer la base d'un futur programme réseau.

Le premier objectif n'est pas de créer un système complexe. Il est de comprendre comment un programme transforme des données en résultats prévisibles.

## 8. Vérifier l'installation de Python

Depuis un terminal, essayez :

```bash
python --version
```

Si cette commande n'est pas reconnue, essayez :

```bash
python3 --version
```

Sous Windows, selon l'installation, la commande suivante peut également être disponible :

```powershell
py --version
```

Une version récente de Python 3 est recommandée.

## 9. Premier programme Python

Créez un fichier appelé `hello_automation.py`.

```python
print("Bienvenue dans le cours d'automatisation réseau.")
print("Première étape : comprendre les données.")
print("Deuxième étape : vérifier les entrées.")
print("Troisième étape : préparer les traitements.")
```

Exécutez-le :

```bash
python hello_automation.py
```

Le programme affiche plusieurs lignes.

La fonction `print()` affiche du texte dans le terminal. Elle est utile pour comprendre ce que le programme exécute et pour afficher des résultats simples.

Un programme professionnel ne doit cependant pas dépendre uniquement des messages affichés au terminal. Au fur et à mesure de sa complexité, il devient nécessaire de structurer les messages et les journaux.

## 10. Les variables

Une variable permet de donner un nom à une valeur.

```python
device_name = "R1"
device_host = "192.0.2.11"
device_role = "router"

print(device_name)
print(device_host)
print(device_role)
```

Dans cet exemple :

- `device_name` contient un nom logique.
- `device_host` contient une adresse de démonstration.
- `device_role` contient le rôle de l'équipement.

Les noms des variables doivent exprimer leur utilité. Des noms vagues rendent le code plus difficile à comprendre.

## 11. Les listes

Une liste permet de regrouper plusieurs valeurs.

```python
devices = ["R1", "SW1", "SW2"]

for device in devices:
    print(device)
```

La boucle `for` parcourt les éléments de la liste.

La même logique sera utilisée lorsque le programme devra traiter plusieurs équipements.

```text
LISTE D'ÉQUIPEMENTS
        |
        v
   +---------+
   |   R1    |
   +---------+
        |
        v
   +---------+
   |   SW1   |
   +---------+
        |
        v
   +---------+
   |   SW2   |
   +---------+
        |
        v
      FIN
```

Le schéma représente la progression logique. Dans un programme réel, l'ordre de traitement dépend de la manière dont les données sont organisées.


# PARTIE 5 — COMPRENDRE JSON ET LES INVENTAIRES

## 12. Pourquoi structurer les données ?

Un programme d'automatisation doit savoir quels équipements existent, comment les identifier et quelles propriétés leur sont associées.

Un simple texte libre est difficile à contrôler lorsqu'il contient de nombreuses informations.

Comparons deux exemples.

### Liste non structurée

```text
Routeur R1 - 192.0.2.11 - IOS
Switch SW1 - 192.0.2.21 - IOS
```

Ces informations sont compréhensibles pour une personne, mais le programme devrait interpréter une chaîne de caractères et déduire où chaque propriété commence et se termine.

### Liste structurée

```json
[
  {
    "name": "R1",
    "host": "192.0.2.11",
    "platform": "ios",
    "role": "router"
  },
  {
    "name": "SW1",
    "host": "192.0.2.21",
    "platform": "ios",
    "role": "switch"
  }
]
```

Chaque propriété possède un nom explicite.

Ce format permet au programme d'accéder directement à la valeur correspondant à `name`, `host`, `platform` ou `role`.

## 13. Les éléments essentiels de JSON

JSON est un format textuel de représentation des données.

Il utilise notamment :

- Des objets entourés d'accolades.
- Des tableaux entourés de crochets.
- Des chaînes de caractères entre guillemets doubles.
- Des nombres.
- Des valeurs booléennes.
- La valeur `null`.

Exemple d'objet :

```json
{
  "name": "R1",
  "host": "192.0.2.11",
  "enabled": true
}
```

Les noms de propriétés et les chaînes doivent utiliser des guillemets doubles.

JSON n'accepte pas les commentaires comme `// commentaire` à l'intérieur d'un document JSON standard.

## 14. Créer l'inventaire du laboratoire

Créez le fichier suivant :

`inventory/devices.json`

Contenu :

```json
[
  {
    "name": "R1",
    "host": "192.0.2.11",
    "platform": "ios",
    "role": "router",
    "environment": "lab"
  },
  {
    "name": "SW1",
    "host": "192.0.2.21",
    "platform": "ios",
    "role": "switch",
    "environment": "lab"
  },
  {
    "name": "SW2",
    "host": "192.0.2.22",
    "platform": "ios",
    "role": "switch",
    "environment": "lab"
  }
]
```

Les adresses de la plage `192.0.2.0/24` sont réservées à la documentation. Elles sont utilisées ici comme exemples et ne désignent pas des équipements de production.

### Comprendre les champs

| Champ | Signification | Exemple |
|---|---|---|
| `name` | Identifiant logique de l'équipement | `R1` |
| `host` | Adresse de destination | `192.0.2.11` |
| `platform` | Famille de plateforme | `ios` |
| `role` | Fonction réseau | `router` |
| `environment` | Environnement prévu | `lab` |

Le nom logique doit être unique dans cet inventaire. Sans identifiant distinct, il devient plus difficile d'associer les résultats au bon équipement.

### Schéma — rôle de l'inventaire

```text
FICHIER JSON
     |
     v
+-----------------------------+
| Équipement R1                |
| name = R1                    |
| host = 192.0.2.11            |
| platform = ios               |
| role = router                |
| environment = lab            |
+-----------------------------+
     |
     v
Le programme sait comment
identifier l'équipement
     |
     v
Le programme peut valider
les propriétés obligatoires
```

## 15. Lire un fichier JSON avec Python

Créez le fichier `scripts/read_inventory.py`.

```python
import json
from pathlib import Path

inventory_path = Path("inventory/devices.json")

if not inventory_path.exists():
    raise SystemExit(
        f"Inventaire introuvable : {inventory_path}"
    )

try:
    with inventory_path.open("r", encoding="utf-8") as file:
        devices = json.load(file)
except json.JSONDecodeError as exc:
    raise SystemExit(
        f"Le fichier JSON est invalide : {exc}"
    ) from exc

print(f"Nombre d'entrées : {len(devices)}")

for device in devices:
    print(
        f"{device['name']} - "
        f"{device['host']} - "
        f"{device['role']}"
    )
```

Exécution depuis la racine du projet :

```bash
python scripts/read_inventory.py
```

Résultat attendu avec l'inventaire d'exemple :

```text
Nombre d'entrées : 3
R1 - 192.0.2.11 - router
SW1 - 192.0.2.21 - switch
SW2 - 192.0.2.22 - switch
```

Le programme suppose encore que les entrées contiennent les propriétés attendues. Il faut maintenant apprendre à les vérifier.


# PARTIE 6 — VALIDER LES DONNÉES AVANT D'AGIR

## 16. Pourquoi valider l'inventaire ?

Un inventaire peut contenir :

- Un champ manquant.
- Une adresse vide.
- Un nom en double.
- Une faute de frappe.
- Une structure JSON incorrecte.
- Un équipement qui appartient à un autre environnement.

Si le programme utilise immédiatement ces données, il risque de produire des résultats incorrects ou de cibler un mauvais système.

La validation permet de repérer les problèmes avant d'effectuer une opération réseau.

### Schéma — validation avant exécution

```text
             FICHIER JSON
                  |
                  v
          Lecture du document
                  |
                  v
          JSON syntaxiquement valide ?
             /             \
           NON             OUI
            |               |
            v               v
       Arrêt avec       Vérification
       message clair    de la structure
                            |
                            v
                   Champs obligatoires présents ?
                       /             \
                     NON             OUI
                      |               |
                      v               v
                 Arrêt contrôlé   Vérification
                                 des valeurs
                                      |
                                      v
                                 Inventaire
                                   accepté
```

## 17. Script de validation complet

Créez le fichier `scripts/inventory_check.py`.

```python
import json
import ipaddress
from pathlib import Path

INVENTORY_PATH = Path("inventory/devices.json")

REQUIRED_FIELDS = {
    "name",
    "host",
    "platform",
    "role",
    "environment",
}


def fail(message: str) -> None:
    """Affiche une erreur puis arrête le programme."""
    raise SystemExit(f"ERREUR : {message}")


def load_inventory(path: Path) -> list:
    """Charge l'inventaire JSON et vérifie sa structure générale."""
    if not path.exists():
        fail(f"Inventaire introuvable : {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        fail(f"JSON invalide à la ligne {exc.lineno} : {exc.msg}")
    except OSError as exc:
        fail(f"Impossible de lire le fichier : {exc}")

    if not isinstance(data, list):
        fail("La racine du JSON doit être une liste.")

    return data


def validate_inventory(devices: list) -> None:
    """Vérifie les champs et les principales contraintes de l'inventaire."""
    if not devices:
        fail("L'inventaire est vide.")

    seen_names = set()

    for index, device in enumerate(devices, start=1):
        if not isinstance(device, dict):
            fail(f"Entrée {index} : un objet JSON est attendu.")

        missing_fields = REQUIRED_FIELDS - device.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            fail(f"Entrée {index} : champs manquants : {missing}")

        name = device["name"]
        host = device["host"]
        platform = device["platform"]
        role = device["role"]
        environment = device["environment"]

        for field_name, value in (
            ("name", name),
            ("host", host),
            ("platform", platform),
            ("role", role),
            ("environment", environment),
        ):
            if not isinstance(value, str) or not value.strip():
                fail(
                    f"Entrée {index} : "
                    f"le champ {field_name!r} est vide ou invalide."
                )

        if name in seen_names:
            fail(f"Nom dupliqué dans l'inventaire : {name}")

        seen_names.add(name)

        try:
            ipaddress.ip_address(host)
        except ValueError:
            fail(f"{name} : adresse IP invalide : {host}")

        if environment not in {"lab", "staging", "production"}:
            fail(
                f"{name} : environnement inconnu : {environment}"
            )

    print(f"Inventaire valide : {len(devices)} équipement(s).")


def main() -> None:
    devices = load_inventory(INVENTORY_PATH)
    validate_inventory(devices)

    print("\nÉquipements déclarés :")

    for device in devices:
        print(
            f"- {device['name']:5} | "
            f"{device['host']:15} | "
            f"{device['platform']:10} | "
            f"{device['role']:8} | "
            f"{device['environment']}"
        )


if __name__ == "__main__":
    main()
```

Exécutez le programme :

```bash
python scripts/inventory_check.py
```

Résultat attendu :

```text
Inventaire valide : 3 équipement(s).

Équipements déclarés :
- R1    | 192.0.2.11      | ios        | router   | lab
- SW1   | 192.0.2.21      | ios        | switch   | lab
- SW2   | 192.0.2.22      | ios        | switch   | lab
```

### Ce que le programme vérifie

1. Le fichier existe.
2. Le fichier peut être lu.
3. Le JSON respecte la syntaxe attendue.
4. La racine du document est une liste.
5. Chaque entrée est un objet.
6. Les propriétés obligatoires existent.
7. Les propriétés sont renseignées avec des chaînes non vides.
8. Les noms sont uniques.
9. Les adresses correspondent à une représentation d'adresse IP reconnue par Python.
10. L'environnement appartient à la liste autorisée.

### Ce que le programme ne vérifie pas

Ce programme ne prouve pas :

- Que l'équipement existe réellement.
- Que l'adresse IP est joignable.
- Que SSH est activé.
- Que les identifiants sont valides.
- Que les autorisations sont suffisantes.
- Que la plateforme déclarée correspond à la plateforme réelle.
- Que l'opération envisagée serait sans risque.

La validation des données n'est qu'une étape du processus.


# PARTIE 7 — PRÉPARER L'ENVIRONNEMENT DE TRAVAIL

## 18. Organisation du projet

Une organisation cohérente facilite la maintenance et la réutilisation du code.

Créez cette arborescence :

```text
automation-lab/
|
+-- README.md
|
+-- inventory/
|   |
|   +-- devices.json
|
+-- scripts/
|   |
|   +-- read_inventory.py
|   |
|   +-- inventory_check.py
|
+-- data/
|   |
|   +-- sample_devices.json
|
+-- reports/
|   |
|   +-- .gitkeep
|
+-- backups/
|   |
|   +-- .gitkeep
|
+-- tests/
    |
    +-- README.md
```

### Rôle des dossiers

| Élément | Utilité |
|---|---|
| `README.md` | Explique le projet et son utilisation |
| `inventory/` | Contient les inventaires utilisés par le projet |
| `scripts/` | Contient les programmes Python |
| `data/` | Contient les données d'exemple |
| `reports/` | Destiné aux rapports générés |
| `backups/` | Destiné aux sauvegardes du laboratoire |
| `tests/` | Contient les notes et tests du projet |

Les fichiers `.gitkeep` servent couramment à conserver des dossiers vides dans certains dépôts Git. Ils ne sont pas nécessaires au fonctionnement de Python.

## 19. Créer et exécuter le projet

Depuis un terminal, créez le répertoire principal et les dossiers.

Sous un environnement Linux ou macOS :

```bash
mkdir -p automation-lab/inventory
mkdir -p automation-lab/scripts
mkdir -p automation-lab/data
mkdir -p automation-lab/reports
mkdir -p automation-lab/backups
mkdir -p automation-lab/tests
```

Puis placez-vous dans le répertoire :

```bash
cd automation-lab
```

Sous Windows, les dossiers peuvent être créés avec l'Explorateur de fichiers ou avec les commandes adaptées du terminal utilisé.

Il est important d'exécuter les exemples depuis la racine `automation-lab/`, car les chemins des fichiers sont relatifs à ce répertoire.

### Structure logique

```text
TERMINAL
   |
   v
automation-lab/
   |
   +---- inventory/
   |          |
   |          v
   |      devices.json
   |
   +---- scripts/
              |
              v
       inventory_check.py
              |
              v
       Lit l'inventaire
              |
              v
       Vérifie les données
              |
              v
       Affiche le résultat
```


# PARTIE 8 — COMPRENDRE SSH

## 20. Qu'est-ce que SSH ?

SSH signifie *Secure Shell*. C'est un protocole qui permet notamment d'administrer des systèmes à distance au moyen d'une connexion sécurisée.

Dans un environnement réseau, SSH est fréquemment utilisé pour se connecter à un routeur ou à un commutateur.

L'administrateur peut ouvrir une session, s'authentifier puis exécuter les commandes autorisées par le système distant.

### Schéma — connexion SSH

```text
+-------------------------+
| POSTE D'ADMINISTRATION  |
|                         |
| Script ou client SSH    |
+------------+------------+
             |
             |
             | Réseau IP
             |
             v
+-------------------------+
| ÉQUIPEMENT RÉSEAU       |
|                         |
| Service SSH             |
| Vérification d'identité |
| Contrôle des droits     |
+-------------------------+
```

La communication doit être autorisée par le réseau et par la politique de sécurité de l'équipement.

## 21. Les étapes conceptuelles d'une connexion

```text
1. Identifier la cible
          |
          v
2. Vérifier que l'accès est autorisé
          |
          v
3. Établir la connexion SSH
          |
          v
4. Vérifier l'identité du serveur
          |
          v
5. Authentifier l'utilisateur
          |
          v
6. Obtenir les droits autorisés
          |
          v
7. Exécuter l'opération permise
          |
          v
8. Récupérer le résultat
          |
          v
9. Fermer la session proprement
```

Cette représentation simplifie les détails du protocole, mais elle permet de comprendre les grandes étapes.

## 22. Pourquoi vérifier la clé d'hôte ?

Lorsqu'un client SSH se connecte à un serveur, il doit pouvoir vérifier l'identité du serveur.

La clé d'hôte joue un rôle important dans cette vérification.

Désactiver la vérification pour faire disparaître un avertissement n'est pas une bonne pratique. Un changement de clé doit être examiné selon la procédure de l'environnement.

Un programme d'automatisation doit respecter les contrôles d'identité plutôt que de les contourner.

## 23. Les identifiants et la gestion des secrets

Ne placez pas de mots de passe en clair dans :

- Le code Python.
- Un inventaire partagé.
- Un dépôt Git.
- Un rapport d'exécution.
- Une capture d'écran.
- Un fichier d'exemple destiné à être distribué.

Les solutions de gestion des secrets varient selon l'environnement : coffre de secrets, mécanisme d'identifiants fourni par la plateforme d'automatisation, variables d'environnement contrôlées ou autres mécanismes adaptés.

Le choix dépend de l'infrastructure, du système d'exploitation, de la politique de sécurité et des droits d'accès.

### Schéma — séparation des données et des secrets

```text
PROJET
  |
  +---- Code Python
  |       |
  |       +---- Logique et contrôles
  |
  +---- Inventaire
  |       |
  |       +---- Noms et adresses
  |
  +---- Gestion des secrets
  |       |
  |       +---- Accès restreint
  |
  +---- Résultats
          |
          +---- État observé
          +---- Journaux
          +---- Rapports
```

Les identifiants ne doivent pas être exposés simplement parce qu'un programme est automatisé.

## 24. Le principe du moindre privilège

Un compte utilisé par une automatisation doit disposer uniquement des droits nécessaires à l'opération prévue.

Par exemple, un script qui collecte des informations en lecture seule ne devrait pas recevoir par défaut tous les privilèges nécessaires pour modifier l'ensemble de la configuration.

Il faut également limiter les équipements accessibles par ce compte, lorsque l'environnement le permet.

```text
BESOIN DU SCRIPT
       |
       v
Déterminer l'opération exacte
       |
       v
Identifier les autorisations nécessaires
       |
       v
Attribuer uniquement ces autorisations
       |
       v
Tester les accès dans le laboratoire
       |
       v
Contrôler les résultats
```

Les privilèges doivent évoluer uniquement lorsque les fonctions du projet le nécessitent et que les risques ont été évalués.


# PARTIE 9 — DÉCOUVRIR LES OUTILS D'AUTOMATISATION

## 25. Python, Netmiko, NAPALM et Ansible

Plusieurs outils sont utilisés dans l'automatisation réseau. Ils ont des rôles différents.

### 25.1 Python

Python est un langage de programmation généraliste.

Il permet de construire la logique du programme : lire des données, faire des contrôles, choisir les actions et produire les résultats.

Python ne fournit pas à lui seul une méthode universelle pour administrer toutes les plateformes réseau. Des bibliothèques peuvent être nécessaires.

### 25.2 Netmiko

Netmiko facilite les connexions et l'exécution de commandes sur de nombreux équipements réseau, notamment par SSH, en tenant compte des particularités de certaines plateformes.

Il peut être utilisé dans un script Python pour récupérer des informations ou réaliser d'autres opérations autorisées.

La prise en charge exacte dépend des équipements et de leur configuration.

### 25.3 NAPALM

NAPALM fournit une interface commune pour certaines opérations réseau et expose des fonctions qui dépendent des pilotes et des plateformes pris en charge.

Il peut notamment servir à récupérer des informations structurées et à travailler avec certaines notions de configuration.

Toutes les plateformes ne proposent pas exactement les mêmes fonctions.

### 25.4 Ansible

Ansible permet de décrire des tâches d'administration au moyen d'inventaires, de modules et de fichiers de définition des opérations.

Il est adapté à l'exécution répétée de tâches sur des groupes de systèmes.

Il n'est pas nécessaire de maîtriser Ansible pour réaliser les exercices de ce cours.

### Comparaison générale

| Outil | Type | Utilisation fréquente |
|---|---|---|
| Python | Langage | Logique et programmes personnalisés |
| Netmiko | Bibliothèque Python | Connexions et commandes réseau |
| NAPALM | Bibliothèque Python | Opérations réseau avec une interface commune |
| Ansible | Outil d'automatisation | Orchestration de tâches et gestion d'inventaires |

### Schéma — relation entre les outils

```text
             OBJECTIF RÉSEAU
                   |
                   v
           Choix de l'approche
                   |
        +----------+----------+
        |                     |
        v                     v
  SCRIPT PYTHON            ANSIBLE
        |                     |
        v                     v
 Bibliothèque adaptée    Modules et tâches
        |
        +--------------------------+
        |                          |
        v                          v
     NETMIKO                    NAPALM
        |                          |
        v                          v
 Connexion et commandes     Opérations prises
 selon la plateforme        en charge par le pilote
```

Ce schéma présente des possibilités générales, et non une obligation d'associer tous ces outils dans un même projet.

## 26. Comment choisir un outil ?

Le choix dépend de plusieurs critères :

1. Le type d'équipements à administrer.
2. Les protocoles et interfaces pris en charge.
3. Le type d'opération à réaliser.
4. Le niveau de standardisation recherché.
5. La facilité de test.
6. La gestion des erreurs.
7. La possibilité de produire des résultats exploitables.
8. Les compétences disponibles dans l'équipe.

Il est préférable de choisir l'outil après avoir défini le besoin plutôt que de commencer par installer plusieurs bibliothèques sans objectif précis.

Dans ce premier cours, l'apprentissage de Python et la validation des données restent prioritaires.


# PARTIE 10 — OBSERVER, SAUVEGARDER ET COMPARER

## 27. Trois opérations à distinguer

L'observation, la sauvegarde et la comparaison sont souvent associées dans un projet d'automatisation, mais elles ne correspondent pas à la même action.

### 27.1 Observer

Observer consiste à recueillir l'état d'un équipement.

Cela peut comprendre :

- La version du système.
- Les interfaces présentes.
- L'état des liens.
- Les VLAN déclarés.
- Les routes connues.
- Certains paramètres de configuration.

L'information obtenue dépend des commandes disponibles et du système utilisé.

### 27.2 Sauvegarder

Sauvegarder consiste à conserver une représentation d'un état à un moment donné.

Une sauvegarde doit être associée au bon équipement et à une date identifiable. Son emplacement, ses permissions et sa politique de conservation doivent être prévus.

### 27.3 Comparer

Comparer consiste à mettre en relation deux ensembles d'informations.

La comparaison peut porter sur deux sauvegardes, deux états observés ou un état réel et un état attendu.

Une différence n'est pas nécessairement une anomalie. Elle peut être la conséquence d'une opération autorisée.

### Schéma — cycle de lecture et de comparaison

```text
                 TEMPS T0
                    |
                    v
             Observation initiale
                    |
                    v
              Sauvegarde A
                    |
                    |
                    | Temps et opérations
                    v
                 TEMPS T1
                    |
                    v
             Nouvelle observation
                    |
                    v
              Sauvegarde B
                    |
                    v
               Comparaison
                    |
                    v
            Liste des différences
                    |
                    v
          Analyse et vérification
                    |
          +---------+---------+
          |                   |
          v                   v
  Changement prévu      Changement suspect
          |                   |
          v                   v
 Documentation          Investigation
 et validation          complémentaire
```

## 28. La différence entre état observé et état attendu

L'état observé est celui que les données collectées décrivent.

L'état attendu est celui que l'organisation souhaite atteindre ou maintenir.

Exemple :

```text
ÉTAT ATTENDU
SW1 doit posséder le VLAN 10.
SW1 doit posséder le VLAN 20.

ÉTAT OBSERVÉ
SW1 possède le VLAN 10.
SW1 possède le VLAN 20.
SW1 possède également le VLAN 30.

COMPARAISON
VLAN 10 : conforme
VLAN 20 : conforme
VLAN 30 : différence à examiner
```

La présence du VLAN 30 ne suffit pas à conclure qu'il s'agit d'une erreur. Il faut vérifier s'il est autorisé, planifié ou nécessaire.

L'automatisation peut signaler une différence. La décision de la traiter doit suivre les règles de l'environnement.

## 29. Pourquoi conserver les résultats ?

Un résultat sans date, sans nom d'équipement et sans contexte peut être difficile à interpréter.

Un enregistrement exploitable doit idéalement permettre de retrouver :

- L'identité de l'équipement.
- La date de l'observation.
- La source de l'information.
- Le type de contrôle réalisé.
- Le résultat.
- L'éventuelle erreur.

Au niveau intermédiaire, le projet ajoutera une véritable collecte, des sauvegardes et des rapports. Le cours actuel prépare la structure de ces évolutions.


# PARTIE 11 — TRAITER LES ERREURS

## 30. Les catégories d'erreurs

Un processus d'automatisation peut rencontrer plusieurs catégories d'erreurs.

### Erreurs de données

Exemples :

- Fichier JSON mal formé.
- Adresse IP incorrecte.
- Nom d'équipement en double.
- Champ obligatoire manquant.

### Erreurs d'environnement

Exemples :

- Python n'est pas disponible.
- Le fichier n'est pas accessible.
- Le répertoire de sortie n'existe pas.
- L'utilisateur n'a pas le droit d'écrire un rapport.

### Erreurs de communication

Exemples :

- Équipement indisponible.
- Chemin réseau interrompu.
- Connexion refusée.
- Délai d'attente dépassé.

### Erreurs d'autorisation

Exemples :

- Identifiants incorrects.
- Compte verrouillé.
- Privilèges insuffisants.
- Accès interdit par la politique de sécurité.

### Erreurs de logique

Exemples :

- Mauvais équipement sélectionné.
- Condition de validation incorrecte.
- Résultat interprété de manière erronée.
- Fichier précédent écrasé involontairement.

## 31. Principes de gestion des erreurs

Une automatisation robuste doit :

1. Détecter les erreurs possibles.
2. Présenter un message compréhensible.
3. Conserver les informations utiles au diagnostic.
4. Éviter de déclarer une opération réussie si elle a échoué.
5. Déterminer si elle doit continuer, réessayer ou s'arrêter.
6. Ne pas exposer les secrets dans les messages.
7. Permettre une vérification des résultats partiels.

### Schéma — décision en cas d'erreur

```text
              OPÉRATION
                  |
                  v
             Succès ?
             /     \
           OUI     NON
            |       |
            v       v
       Enregistrer  Identifier
       le résultat  l'erreur
            |       |
            |       v
            |   Erreur récupérable ?
            |       /       \
            |     OUI       NON
            |      |         |
            |      v         v
            |   Réessayer   Arrêter ou
            |   si prévu    passer à l'étape
            |               suivante selon
            |               la politique
            +-------+---------+
                    |
                    v
             Rapport final
```

Un nouvel essai ne doit être réalisé que si le type d'opération s'y prête. Répéter automatiquement une opération qui modifie la configuration peut produire des effets indésirables si elle n'est pas conçue pour être répétée sans danger.

## 32. Journaliser sans exposer les secrets

Une bonne journalisation décrit les événements nécessaires au diagnostic sans divulguer les mots de passe ou les informations d'authentification.

Exemple de rapport synthétique :

```text
2026-10-24 09:00:00 | INVENTORY | OK | 3 équipements lus
2026-10-24 09:00:01 | VALIDATION | OK | Inventaire accepté
2026-10-24 09:00:02 | R1 | NON TESTÉ | Aucune connexion effectuée
2026-10-24 09:00:02 | SW1 | NON TESTÉ | Aucune connexion effectuée
2026-10-24 09:00:02 | SW2 | NON TESTÉ | Aucune connexion effectuée
```

Ces lignes illustrent une exécution de validation locale. Elles ne prétendent pas que des équipements ont été contactés.

Le format peut être adapté. Le principe reste de distinguer clairement les actions réellement effectuées de celles qui ne l'ont pas été.


# PARTIE 12 — PROJET GUIDÉ

## 33. Mission du projet

Construire une première version du projet `automation-lab`.

Le programme doit :

- Charger un inventaire fictif.
- Vérifier que le fichier existe.
- Détecter un JSON incorrect.
- Contrôler les propriétés obligatoires.
- Détecter les noms dupliqués.
- Vérifier la représentation des adresses IP.
- Refuser les environnements non autorisés.
- Afficher un résumé lisible.
- N'effectuer aucune connexion réseau.

Cette mission constitue le livrable principal du niveau débutant.

## 34. Arborescence à obtenir

```text
automation-lab/
|
+-- README.md
|
+-- inventory/
|   |
|   +-- devices.json
|
+-- scripts/
|   |
|   +-- read_inventory.py
|   |
|   +-- inventory_check.py
|
+-- data/
|   |
|   +-- sample_devices.json
|
+-- reports/
|   |
|   +-- .gitkeep
|
+-- backups/
|   |
|   +-- .gitkeep
|
+-- tests/
    |
    +-- README.md
```

## 35. Étape 1 — Créer l'inventaire

Créez `inventory/devices.json` avec les trois équipements d'exemple fournis dans la partie consacrée à JSON.

Vérifiez particulièrement :

- Les guillemets doubles.
- Les virgules entre les objets.
- L'absence de virgule après le dernier objet.
- La cohérence des noms.
- Les valeurs de l'environnement.

## 36. Étape 2 — Créer le programme de validation

Copiez le script `inventory_check.py` présenté plus haut dans :

```text
automation-lab/scripts/inventory_check.py
```

Exécutez le programme depuis la racine du projet :

```bash
python scripts/inventory_check.py
```

Comparez le résultat obtenu avec le résultat attendu.

## 37. Étape 3 — Tester les erreurs

Un programme ne doit pas seulement fonctionner avec des données correctes. Il doit aussi détecter les situations incorrectes qui ont été prévues.

### Test A — Fichier absent

Renommez temporairement le fichier d'inventaire puis lancez le programme.

Résultat attendu : un message indiquant que l'inventaire est introuvable.

Remettez ensuite le nom du fichier d'origine.

### Test B — JSON incorrect

Dans une copie du fichier, supprimez une virgule nécessaire ou ajoutez une erreur de syntaxe.

Résultat attendu : un message indiquant que le JSON est invalide.

Corrigez le document avant de poursuivre.

### Test C — Champ obligatoire absent

Retirez le champ `role` d'un objet.

Résultat attendu : le script signale le champ manquant et s'arrête.

### Test D — Nom dupliqué

Ajoutez un deuxième objet dont le champ `name` utilise un nom déjà présent.

Résultat attendu : le script refuse l'inventaire à cause du doublon.

### Test E — Adresse invalide

Utilisez temporairement une valeur qui n'est pas une adresse IP valide.

Résultat attendu : le script indique que l'adresse n'est pas valide.

### Test F — Environnement non autorisé

Remplacez `lab` par un environnement qui ne figure pas dans la liste acceptée.

Résultat attendu : le script signale un environnement inconnu.

## 38. Étape 4 — Créer le README

Le fichier `README.md` doit permettre à un autre apprenant de comprendre le projet et de le reproduire.

Modèle :

```markdown
# automation-lab

## Objectif

Apprendre les bases de l'automatisation réseau avec Python.

## Fonction actuelle

Le programme lit un inventaire JSON et valide sa structure.

## Prérequis

- Python 3
- Un terminal
- Un éditeur de texte

## Exécution

Depuis la racine du projet :

    python scripts/inventory_check.py

## Sécurité

Le projet utilise des équipements fictifs.
Aucune connexion réseau n'est effectuée.

## Limites

Le programme valide les données de l'inventaire.
Il ne vérifie pas l'existence réelle des équipements
et ne teste pas la disponibilité des adresses IP.
```

## 39. Étape 5 — Vérifier la qualité du projet

Avant de considérer le projet terminé, contrôlez les points suivants.

| Vérification | Résultat attendu |
|---|---|
| Le fichier JSON existe | Oui |
| Le JSON est valide | Oui |
| Les champs obligatoires sont présents | Oui |
| Les noms sont uniques | Oui |
| Les adresses IP sont bien formées | Oui |
| Les environnements sont autorisés | Oui |
| Les erreurs sont compréhensibles | Oui |
| Aucun secret n'est stocké dans le projet | Oui |
| Aucune connexion réseau n'est effectuée | Oui |
| Le README explique comment exécuter le programme | Oui |

### Schéma — critères d'acceptation

```text
               PROJET TERMINÉ ?
                      |
                      v
              Inventaire valide ?
                 /          \
               NON          OUI
                |            |
                v            v
          Corriger les    Tests d'erreurs
          données             |
                              v
                    Résultats compréhensibles ?
                         /           \
                       NON           OUI
                        |             |
                        v             v
                 Améliorer       Vérifier la sécurité
                 le script             |
                                       v
                              README reproductible ?
                                 /           \
                               NON           OUI
                                |             |
                                v             v
                           Compléter       PROJET
                                           ACCEPTÉ
```


# PARTIE 13 — EXERCICES ET CORRECTIONS

## 40. Exercice 1 — Compréhension générale

**Question :** quelle est la différence entre une opération manuelle, un script ponctuel et un processus automatisé contrôlé ?

### Correction

Une opération manuelle est exécutée directement par une personne.

Un script ponctuel automatise certaines étapes répétitives en suivant des instructions programmées.

Un processus automatisé contrôlé ajoute des vérifications, la gestion des erreurs, la traçabilité, une définition claire du périmètre et un contrôle des résultats.

Ces approches ne s'opposent pas. Une automatisation peut s'appuyer sur des vérifications manuelles et des validations humaines.

## 41. Exercice 2 — Ajouter un équipement

Ajoutez un équipement fictif nommé `SW3`.

Il doit utiliser :

- `name` : `SW3`
- `host` : `192.0.2.23`
- `platform` : `ios`
- `role` : `switch`
- `environment` : `lab`

### Correction

Ajoutez cet objet à la liste JSON :

```json
{
  "name": "SW3",
  "host": "192.0.2.23",
  "platform": "ios",
  "role": "switch",
  "environment": "lab"
}
```

L'objet doit être séparé des objets précédents par une virgule. Il ne faut pas placer de virgule après le dernier objet de la liste.

Relancez ensuite le script de validation.

Résultat attendu : l'inventaire contient maintenant quatre équipements.

## 42. Exercice 3 — Champ manquant

**Question :** pourquoi le script doit-il détecter l'absence d'un champ obligatoire avant d'essayer de se connecter à un équipement ?

### Correction

Le programme a besoin de données cohérentes pour identifier la cible et appliquer les règles prévues.

Une propriété absente peut provoquer une erreur de code, rendre une opération ambiguë ou entraîner le traitement d'une cible différente de celle attendue.

La validation doit se faire avant les opérations réseau afin d'éviter de commencer un traitement sur des données incorrectes.

## 43. Exercice 4 — Secrets dans Git

**Question :** pourquoi est-il dangereux de placer un mot de passe dans `devices.json` et d'enregistrer le fichier dans un dépôt Git ?

### Correction

Le fichier peut être copié ou partagé. De plus, les anciennes versions peuvent rester conservées dans l'historique du dépôt même après la suppression du mot de passe dans la version courante.

La gestion des secrets doit être séparée de l'inventaire et du code. Les droits doivent être limités aux personnes et aux services qui en ont besoin.

Si un secret est publié par erreur, sa suppression du fichier ne suffit pas nécessairement : il faut suivre la procédure de révocation et de remplacement prévue par l'organisation.

## 44. Exercice 5 — Connexion SSH

**Question :** un script échoue parce que la clé d'hôte SSH reçue est différente de celle attendue. Faut-il désactiver automatiquement la vérification pour faire fonctionner le script ?

### Correction

Non. Le changement doit être examiné avant de poursuivre.

Il peut correspondre à un remplacement légitime de l'équipement, mais il peut aussi indiquer que la cible n'est pas celle attendue ou qu'une communication est interceptée.

L'identité du serveur doit être vérifiée à l'aide de la procédure de confiance de l'environnement.

## 45. Exercice 6 — Lecture et sauvegarde

**Question :** expliquez la différence entre observer un équipement, sauvegarder son état et comparer deux états.

### Correction

Observer signifie recueillir des informations sur l'état actuel.

Sauvegarder signifie conserver un état recueilli dans un fichier ou un système de stockage.

Comparer signifie mettre en relation deux états afin d'identifier les différences.

Une sauvegarde est un enregistrement. Une comparaison est une analyse de deux ensembles d'informations.

## 46. Exercice 7 — Une différence est-elle toujours une erreur ?

Un rapport indique qu'un équipement possède un VLAN supplémentaire par rapport à la sauvegarde de la semaine précédente.

**Question :** peut-on conclure immédiatement que la configuration est incorrecte ?

### Correction

Non.

Il faut notamment :

1. Vérifier que les deux états concernent le même équipement.
2. Confirmer les dates et le périmètre des données.
3. Consulter les changements planifiés.
4. Vérifier si le VLAN est autorisé.
5. Examiner les éléments de preuve disponibles.
6. Faire valider la conclusion par la personne responsable.

Le rapport identifie une différence. Il ne prouve pas automatiquement qu'il s'agit d'un incident.

## 47. Exercice 8 — Préparer une future sauvegarde automatisée

**Question :** quelles vérifications un programme devrait-il effectuer avant de lancer un processus de sauvegarde multi-équipements ?

### Correction indicative

Il devrait au minimum :

- Vérifier que l'inventaire existe et qu'il est valide.
- Détecter les noms dupliqués.
- Vérifier le périmètre des cibles autorisées.
- Confirmer le répertoire de sortie.
- Vérifier que le répertoire est accessible en écriture.
- Prévoir les erreurs de connexion.
- Définir un mécanisme de journalisation.
- Éviter l'écrasement accidentel des sauvegardes.
- Prévoir des délais d'attente adaptés.
- Distinguer les sauvegardes réussies des échecs.
- Prévoir une vérification de la qualité des fichiers produits.
- Protéger les informations sensibles.

Ces exigences seront développées davantage au niveau intermédiaire.


# PARTIE 14 — ERREURS FRÉQUENTES

## 48. Erreur : commencer par modifier la configuration

Un débutant peut être tenté de créer directement un script qui change la configuration d'un équipement.

Le problème est qu'il devient alors nécessaire de gérer les autorisations, les impacts, les erreurs partielles et le retour arrière.

**Bonne pratique :** commencer avec un programme de validation et des opérations en lecture seule. Les modifications seront abordées plus tard, dans un environnement contrôlé.

## 49. Erreur : faire confiance à un inventaire sans le vérifier

Un fichier JSON syntaxiquement valide peut tout de même contenir des données incorrectes.

Par exemple, un équipement peut être associé à une mauvaise adresse IP.

**Bonne pratique :** vérifier à la fois la structure des données et les contraintes métier nécessaires au projet.

## 50. Erreur : confondre adresse valide et équipement accessible

Une adresse IP peut avoir un format valide sans qu'un équipement soit joignable à cette adresse.

**Bonne pratique :** distinguer la validation syntaxique des adresses des tests de connectivité et de l'authentification.

Ces opérations vérifient des choses différentes.

## 51. Erreur : ignorer les erreurs

Un programme qui continue après un échec sans l'enregistrer peut produire un résultat incomplet tout en donnant l'impression d'avoir fonctionné correctement.

**Bonne pratique :** rendre les erreurs visibles et présenter clairement les résultats réussis, échoués ou non exécutés.

## 52. Erreur : mélanger toutes les opérations dans une seule fonction

Un programme très long et mal structuré devient difficile à tester.

**Bonne pratique :** séparer les responsabilités :

```text
PROGRAMME PRINCIPAL
       |
       +----> Charger l'inventaire
       |
       +----> Valider les données
       |
       +----> Préparer l'opération
       |
       +----> Exécuter l'action permise
       |
       +----> Enregistrer les résultats
       |
       +----> Produire le rapport
```

Cette séparation facilite la lecture et permettra d'ajouter des fonctionnalités sans devoir réécrire toute l'application.


# PARTIE 15 — GLOSSAIRE

## 53. Termes à maîtriser

**Automatisation réseau :** utilisation de programmes et de mécanismes d'exécution pour réaliser des tâches d'administration réseau de manière contrôlée et répétable.

**Script :** fichier contenant des instructions qu'un interpréteur ou un environnement d'exécution peut exécuter.

**Python :** langage de programmation utilisé dans de nombreuses tâches d'automatisation.

**Inventaire :** ensemble structuré d'informations sur les équipements concernés par une opération.

**JSON :** format textuel permettant de représenter des données structurées.

**SSH :** protocole permettant notamment d'administrer des systèmes à distance au moyen d'une connexion sécurisée.

**Validation :** contrôle visant à vérifier que les données respectent les règles attendues.

**Journalisation :** enregistrement d'événements, de résultats et d'erreurs utiles au suivi et au diagnostic.

**Sauvegarde :** conservation d'une copie d'informations ou d'un état à un moment donné.

**État observé :** état décrit par les informations recueillies sur le système.

**État attendu :** état que l'on souhaite obtenir ou conserver.

**Comparaison :** opération consistant à examiner les différences entre deux ensembles de données.

**Idempotence :** propriété d'une opération qui, lorsqu'elle est répétée dans les mêmes conditions, n'entraîne pas de changement supplémentaire une fois l'état cible atteint. Toutes les opérations réseau ne sont pas idempotentes.

**Moindre privilège :** principe consistant à accorder uniquement les autorisations nécessaires à une tâche.

**Gestion des secrets :** méthodes et outils permettant de stocker, de distribuer et de contrôler l'accès aux informations sensibles d'authentification.

**Retour arrière :** procédure prévue pour revenir à un état antérieur lorsque les circonstances et les mécanismes disponibles le permettent.

**Conformité :** degré de correspondance entre l'état observé et les règles ou l'état attendu.

**Traçabilité :** capacité à retrouver les informations nécessaires pour comprendre ce qui s'est produit pendant une opération.


# PARTIE 16 — ÉVALUATION DE FIN DE NIVEAU

## 54. Questions théoriques

Répondez aux questions suivantes sans consulter le cours.

1. Pourquoi l'automatisation est-elle utile dans un réseau comportant de nombreux équipements ?
2. Pourquoi un programme automatisé peut-il amplifier une erreur ?
3. Quel est le rôle d'un inventaire ?
4. À quoi sert le format JSON ?
5. Pourquoi faut-il valider les données avant toute opération réseau ?
6. Quelle est la différence entre une adresse IP valide et une cible accessible ?
7. Quel est le rôle de SSH ?
8. Pourquoi faut-il vérifier l'identité du serveur SSH ?
9. Pourquoi ne faut-il pas stocker un mot de passe dans le code ?
10. Que signifie le principe du moindre privilège ?
11. Quelle différence existe entre observer, sauvegarder et comparer ?
12. Pourquoi une différence de configuration n'est-elle pas nécessairement une anomalie ?
13. Pourquoi faut-il enregistrer les erreurs ?
14. Pourquoi est-il préférable de commencer en laboratoire ?
15. Quel est le rôle du fichier README dans un projet d'automatisation ?

## 55. Mise en pratique

Réalisez les tâches suivantes :

1. Créer l'arborescence `automation-lab`.
2. Créer l'inventaire JSON.
3. Écrire le script de validation.
4. Exécuter le programme.
5. Tester un JSON incorrect.
6. Tester un champ manquant.
7. Tester un nom dupliqué.
8. Tester une adresse IP incorrecte.
9. Corriger les erreurs.
10. Rédiger le README.
11. Vérifier qu'aucun secret n'est présent dans les fichiers.
12. Vérifier que le programme n'établit aucune connexion réseau.

## 56. Critères de maîtrise

Le niveau débutant est considéré comme acquis lorsque l'apprenant sait :

- Expliquer le fonctionnement général d'une automatisation.
- Identifier les éléments d'un projet réseau automatisé.
- Manipuler un fichier JSON.
- Lire et expliquer un programme Python simple.
- Valider un inventaire.
- Comprendre les principes de base de SSH et des secrets.
- Distinguer l'observation, la sauvegarde et la comparaison.
- Décrire la manière dont une erreur doit être traitée.
- Réaliser le projet guidé de manière reproductible.

Le but n'est pas de mémoriser toutes les lignes du code. Il est de comprendre les responsabilités des différentes étapes et d'être capable de modifier le projet sans agir au hasard.


# PARTIE 17 — PRÉPARER LE NIVEAU INTERMÉDIAIRE

## 57. Pourquoi la suite doit-elle reprendre ce projet ?

Le projet réalisé dans ce cours doit devenir la base des niveaux suivants.

Il contient déjà :

- Une arborescence de travail.
- Un inventaire JSON.
- Des champs identifiant les équipements.
- Des contrôles de données.
- Une première organisation du code.
- Une documentation d'utilisation.
- Des règles de sécurité de base.

Ces éléments ne doivent pas être abandonnés au début du cours intermédiaire.

Le projet sera enrichi progressivement afin que l'apprenant comprenne comment une petite automatisation se transforme en processus plus complet.

### Schéma — continuité entre les trois niveaux

```text
==========================================================
NIVEAU DÉBUTANT : automation-debutant.md
==========================================================

Projet automation-lab
        |
        +---- Inventaire JSON
        |
        +---- Validation Python
        |
        +---- Vérification des champs
        |
        +---- Détection des erreurs
        |
        +---- README et règles de sécurité
        |
        v

==========================================================
NIVEAU INTERMÉDIAIRE : automation-intermediaire.md
==========================================================

Réutilisation du même projet
        |
        +---- Connexions SSH en laboratoire
        |
        +---- Sélection des équipements autorisés
        |
        +---- Commandes en lecture seule
        |
        +---- Sauvegardes organisées
        |
        +---- Gestion des délais et des erreurs
        |
        +---- Comparaison des résultats
        |
        +---- Rapport d'exécution
        |
        v

==========================================================
NIVEAU EXPERT : automation-expert.md
==========================================================

Évolution du même projet
        |
        +---- Définition d'un état attendu
        |
        +---- Contrôles de conformité
        |
        +---- Tests automatisés
        |
        +---- Validation avant et après changement
        |
        +---- Déploiements contrôlés
        |
        +---- Stratégie de retour arrière
        |
        +---- Journalisation structurée
        |
        +---- Intégration CI/CD
        |
        v

Processus d'automatisation gouverné,
testable et maintenable
```

## 58. Contenu attendu du cours intermédiaire

Le cours intermédiaire devra notamment enseigner :

### Connexion aux équipements

- Différence entre connexion locale et distante.
- Préparation d'un environnement de laboratoire.
- Utilisation d'une bibliothèque adaptée à la plateforme.
- Gestion des clés d'hôte et de l'authentification.
- Délais d'attente et erreurs de connexion.

### Automatisation en lecture seule

- Exécution de commandes d'information.
- Collecte de résultats depuis plusieurs équipements.
- Association correcte de chaque résultat à sa cible.
- Enregistrement des opérations réussies ou échouées.

### Sauvegardes

- Organisation des fichiers.
- Nommage cohérent et daté.
- Protection des données.
- Gestion des échecs.
- Prévention des écrasements accidentels.

### Comparaison

- Comparaison de deux états.
- Détection des différences.
- Classification des écarts.
- Présentation des résultats.
- Validation humaine avant toute décision.

### Fiabilité

- Journalisation.
- Gestion des exceptions.
- Réessais justifiés.
- Contrôle du périmètre des opérations.
- Documentation et tests.

Le cours intermédiaire devra commencer par un rappel du projet débutant, puis introduire ces fonctions sans reprendre intégralement les explications fondamentales.

## 59. Contenu attendu du cours expert

Le niveau expert devra aller plus loin que la simple exécution de commandes.

Il devra aborder :

- La description d'un état réseau attendu.
- La comparaison entre état attendu et état observé.
- Les contrôles de conformité.
- Les tests avant un changement.
- La validation après un changement.
- La gestion des déploiements progressifs.
- Les mécanismes de reprise lorsque c'est possible.
- La gestion des dépendances et des environnements.
- La traçabilité des changements.
- L'intégration dans une chaîne CI/CD.
- Les contrôles de sécurité et les autorisations.
- Les limites de l'automatisation et la supervision humaine.

Les exemples experts devront réutiliser le projet et les conventions construits aux niveaux précédents.


# CONCLUSION GÉNÉRALE

L'automatisation réseau fiable commence par une démarche structurée.

Avant d'exécuter une action sur un routeur ou un commutateur, l'administrateur doit comprendre l'objectif, connaître les équipements concernés, vérifier les données et prévoir les erreurs possibles.

Dans ce cours, l'apprenant a découvert les principes fondamentaux de l'automatisation, les composants d'une architecture, Python, JSON, les inventaires, SSH et les règles élémentaires de sécurité.

Il a également construit une première version du projet `automation-lab`, capable de valider un inventaire sans se connecter aux équipements.

Cette première réalisation peut sembler modeste, mais elle prépare des fonctions essentielles : identifier correctement les cibles, empêcher le traitement de données incorrectes et distinguer une validation réussie d'une opération qui n'a pas été exécutée.

Le niveau intermédiaire réutilisera ces fondations pour ajouter les connexions, la collecte d'informations, les sauvegardes, les comparaisons et les rapports.

Le niveau expert prolongera ensuite cette progression avec la conformité, les tests, les déploiements contrôlés et l'intégration dans une chaîne d'automatisation.

**Principe final : comprendre, valider, observer, enregistrer, comparer, puis modifier uniquement lorsque l'opération est justifiée, testée et contrôlée.**