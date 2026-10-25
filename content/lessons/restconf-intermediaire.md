# RESTCONF et NETCONF — Niveau Intermédiaire

## Construire un client RESTCONF fiable, exploiter YANG et automatiser les opérations réseau

**Nom du fichier :** `restconf-intermediaire.md`  
**Niveau :** Intermédiaire  
**Parcours pédagogique :** Débutant → Intermédiaire → Expert  
**Technologies :** RESTCONF, HTTP, HTTPS, JSON, XML, YANG, Python, Requests et notions de NETCONF  
**Prérequis :** avoir suivi le niveau Débutant ou posséder les connaissances équivalentes  
**Objectif général :** passer des requêtes isolées à un client Python structuré, capable de découvrir les ressources, sélectionner les données utiles, contrôler les erreurs et exécuter des opérations autorisées avec des garanties supplémentaires.


# AVANT-PROPOS — NOUS CONTINUONS LE MÊME PARCOURS

Ce document est la suite du fichier `restconf-debutant.md`.

Le niveau Débutant vous a appris à comprendre les rôles respectifs de RESTCONF, NETCONF et YANG, à envoyer une première requête HTTP, à lire du JSON, à établir une session NETCONF et à distinguer les principaux problèmes de connexion.

Le niveau Intermédiaire réutilise ces bases et les développe. Vous allez désormais apprendre à concevoir du code que vous pourrez conserver, tester et réutiliser dans plusieurs projets d'automatisation.

Nous n'allons donc pas nous limiter à répéter :

```python
response = requests.get(url)
print(response.json())
```

Ce code est un bon point de départ, mais il ne suffit pas pour développer une application d'automatisation sérieuse.

Une application doit notamment connaître :

- l'URL de base de l'API ;
- les chemins de ressources compatibles avec les modèles disponibles ;
- le format des réponses ;
- les identifiants utilisés ;
- les délais de connexion et de lecture ;
- les catégories d'erreurs HTTP ;
- les règles de validation des données ;
- les opérations autorisées sur chaque ressource ;
- les conditions dans lesquelles une modification peut être tentée ;
- les moyens de vérifier l'état après modification.

Nous allons construire ces capacités progressivement.

## La progression des trois niveaux

| Niveau | Question centrale | Compétence principale |
|---|---|---|
| Débutant | Comment communiquer avec l'équipement ? | Lire les premières ressources et comprendre RESTCONF, NETCONF et YANG |
| Intermédiaire | Comment organiser et contrôler les opérations ? | Écrire un client réutilisable, filtrer les données, valider les réponses et effectuer des modifications maîtrisées |
| Expert | Comment industrialiser l'ensemble ? | Déployer à grande échelle, renforcer la gouvernance des changements, superviser l'exécution et intégrer l'automatisation à des systèmes d'exploitation réseau |

Le niveau Expert ne remplacera pas le client RESTCONF que nous allons construire. Il le réutilisera et y ajoutera des contrôles, de l'observabilité, des tests d'intégration, des politiques de changement plus avancées et des mécanismes de déploiement.

## Ce que vous saurez faire à la fin

À l'issue de ce cours, vous devrez être capable de :

1. créer un client RESTCONF Python réutilisable ;
2. centraliser les paramètres de connexion ;
3. réutiliser une session HTTP ;
4. contrôler les certificats TLS ;
5. construire correctement des URI RESTCONF ;
6. sélectionner les champs et la profondeur des données ;
7. distinguer les paramètres de requête RESTCONF des extensions propres à un constructeur ;
8. découvrir les modèles YANG annoncés par un serveur ;
9. comprendre les règles importantes de l'encodage JSON pour YANG ;
10. gérer les réponses HTTP et les erreurs RESTCONF ;
11. employer `GET`, `POST`, `PUT`, `PATCH` et `DELETE` en comprenant leurs différences ;
12. utiliser les mécanismes de précondition lorsqu'ils sont pris en charge ;
13. limiter les risques d'écrasement ou de suppression accidentelle ;
14. valider les résultats avant et après une modification ;
15. tester le client sans équipement réel ;
16. effectuer des collectes multi-équipements avec une concurrence limitée ;
17. structurer un rapport d'audit ;
18. expliquer quand NETCONF peut compléter ou remplacer RESTCONF pour une opération donnée.

> **Règle de ce niveau :** toute lecture doit être vérifiée, toute modification doit être explicitement autorisée et toute opération critique doit être suivie d'un contrôle de l'état obtenu.


# SOMMAIRE

1. Rappel des fondations et objectifs intermédiaires
2. Architecture d'un client RESTCONF
3. Environnement de développement
4. Concevoir un client Python réutilisable
5. Construire et encoder les URI
6. Sélectionner les données avec les paramètres RESTCONF
7. Découvrir les modèles YANG et la YANG Library
8. Comprendre les détails de l'encodage JSON
9. Gérer les réponses et les erreurs
10. Sécuriser les requêtes et contrôler les droits
11. Modifier une ressource avec PATCH
12. Comprendre PUT, POST et DELETE
13. Appliquer YANG Patch
14. Détecter les modifications concurrentes avec ETag
15. Vérifier l'état avant et après un changement
16. Organiser les collectes sur plusieurs équipements
17. Tester le client RESTCONF
18. Relier RESTCONF et NETCONF
19. Laboratoires progressifs
20. Projet final : RESTCONF Inventory Auditor
21. Dépannage intermédiaire
22. Exercices et critères d'évaluation
23. Glossaire
24. Références officielles


# 1. RAPPEL DES FONDATIONS ET OBJECTIFS INTERMÉDIAIRES

## 1.1. Ce que nous avons appris au niveau Débutant

Le niveau précédent a établi quatre bases.

### Base 1 — RESTCONF utilise HTTP

Les opérations RESTCONF passent par des requêtes HTTP et identifient les ressources au moyen d'URI.

La méthode employée dépend de l'objectif :

- lire une ressource ;
- créer un élément ;
- remplacer ou modifier une ressource ;
- supprimer une ressource ;
- invoquer une opération définie par un modèle.

### Base 2 — Les données sont décrites par YANG

YANG décrit les nœuds disponibles, leur organisation, leur type et leurs contraintes.

Le client doit connaître le modèle utilisé par le serveur pour construire les chemins et les corps de requête corrects.

### Base 3 — JSON est un encodage, pas le modèle lui-même

Une réponse JSON est une représentation des données. Elle doit respecter les règles de l'encodage JSON pour YANG défini par le RFC 7951.

Deux réponses qui se ressemblent superficiellement ne sont pas nécessairement interchangeables si leurs modèles ou leurs types sont différents.

### Base 4 — L'accès doit être sécurisé

Le client doit authentifier le serveur, protéger les identifiants, utiliser les permissions appropriées et éviter de désactiver TLS pour contourner un problème de certificat.

Ces quatre bases restent valables dans tous les chapitres suivants.

## 1.2. Le véritable changement au niveau Intermédiaire

Un script Débutant fonctionne souvent pour une seule requête.

Un programme Intermédiaire doit fonctionner de manière prévisible lorsqu'il :

- interroge plusieurs ressources ;
- traite des réponses volumineuses ;
- rencontre un serveur lent ;
- reçoit un document JSON inattendu ;
- se connecte à plusieurs équipements ;
- doit modifier une donnée sans écraser le reste ;
- rencontre un conflit avec un autre administrateur ;
- doit expliquer précisément pourquoi une opération a échoué.

Le but est de construire un ensemble de composants réutilisables plutôt qu'une accumulation de petits scripts isolés.

## 1.3. Les résultats à distinguer

Pour chaque opération, le programme doit différencier au moins trois questions :

1. **Le transport a-t-il fonctionné ?** Le client a-t-il pu joindre le serveur et recevoir une réponse ?
2. **La requête a-t-elle été acceptée ?** Le code HTTP et le contenu correspondent-ils au succès attendu ?
3. **Le résultat métier est-il correct ?** Les données sont-elles conformes au modèle et à l'objectif ?

Par exemple, `200 OK` peut être un succès HTTP, mais le programme peut découvrir ensuite qu'un champ important manque dans la réponse. Dans ce cas, la lecture a réussi techniquement, mais la validation métier a échoué.


# 2. ARCHITECTURE D'UN CLIENT RESTCONF

Nous allons développer le même client tout au long du cours.

Le client sera composé de plusieurs fonctions logiques :

- une configuration de connexion ;
- une session HTTP réutilisable ;
- un constructeur de chemins de ressources ;
- une méthode générique d'envoi ;
- une méthode de lecture JSON ;
- une classification des erreurs ;
- une validation des données ;
- des méthodes spécifiques aux opérations ;
- une couche de rapport.

## 2.1. Schéma SVG animé — organisation du client

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 365" role="img" aria-labelledby="client-arch-title client-arch-desc" style="max-width:100%;height:auto">
  <title id="client-arch-title">Architecture d'un client RESTCONF réutilisable</title>
  <desc id="client-arch-desc">La configuration et la sécurité alimentent le client HTTP. Le constructeur d'URI identifie les ressources et les réponses passent par la validation avant d'être utilisées par le métier.</desc>
  <defs>
    <marker id="client-arch-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#59c4e5"/></marker>
    <style>
      @keyframes client-arch-flow { to { stroke-dashoffset:-28; } }
      .client-arch-link { fill:none;stroke:#59c4e5;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#client-arch-arrow);animation:client-arch-flow 2s linear infinite; }
      .client-arch-label { fill:#f0f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .client-arch-small { fill:#b8c9e0;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="363" rx="14" fill="#0c1422" stroke="#2e4058"/>
  <rect x="28" y="55" width="190" height="65" rx="9" fill="#282541" stroke="#b3a2f3" stroke-width="1.5"/>
  <text x="123" y="81" class="client-arch-label">Configuration</text><text x="123" y="102" class="client-arch-small">hôte, auth, TLS, délais</text>
  <rect x="260" y="55" width="190" height="65" rx="9" fill="#193244" stroke="#64bfe7" stroke-width="1.5"/>
  <text x="355" y="81" class="client-arch-label">Client HTTP</text><text x="355" y="102" class="client-arch-small">session réutilisable</text>
  <rect x="492" y="55" width="190" height="65" rx="9" fill="#17342e" stroke="#64c8a6" stroke-width="1.5"/>
  <text x="587" y="81" class="client-arch-label">URI + requête</text><text x="587" y="102" class="client-arch-small">ressource + paramètres</text>
  <rect x="724" y="55" width="188" height="65" rx="9" fill="#34291e" stroke="#e3b05e" stroke-width="1.5"/>
  <text x="818" y="81" class="client-arch-label">Serveur RESTCONF</text><text x="818" y="102" class="client-arch-small">ressources YANG</text>
  <path class="client-arch-link" d="M218 87 H255"/><path class="client-arch-link" d="M450 87 H487"/><path class="client-arch-link" d="M682 87 H719"/>
  <path d="M818 125 V167 H587 V125" fill="none" stroke="#e3b05e" stroke-width="2.2" stroke-dasharray="6 7" style="animation:client-arch-flow 2.4s linear infinite"/>
  <rect x="246" y="167" width="682" height="55" rx="9" fill="#1e2c40" stroke="#6c9ac9" stroke-width="1.5"/>
  <text x="587" y="190" class="client-arch-label">Réponse HTTP</text><text x="587" y="207" class="client-arch-small">statut, en-têtes, corps</text>
  <path class="client-arch-link" d="M587 222 V246"/>
  <rect x="246" y="248" width="682" height="55" rx="9" fill="#18352f" stroke="#64c8a6" stroke-width="1.5"/>
  <text x="587" y="271" class="client-arch-label">Validation</text><text x="587" y="288" class="client-arch-small">structure JSON, types, valeurs attendues</text>
  <path class="client-arch-link" d="M246 275 H139 V144"/>
  <text x="130" y="328" class="client-arch-small">Résultat structuré pour le traitement métier</text>
</svg>

## 2.2. Pourquoi la session HTTP est importante

Requests permet de créer un objet `Session`.

Cet objet peut conserver des paramètres communs et réutiliser les connexions selon les règles de la bibliothèque et du serveur. Cela évite de reconstruire systématiquement tous les paramètres pour chaque requête.

Exemple de départ :

```python
import requests

session = requests.Session()
session.headers.update({
    "Accept": "application/yang-data+json",
})
```

Les en-têtes sont centralisés. Vous pouvez également configurer l'authentification et conserver le contrôle TLS sur le client.

La session ne remplace toutefois ni la validation des réponses ni la gestion des erreurs.

## 2.3. Pourquoi ne pas coder toutes les URL en dur ?

Cette écriture est fragile :

```python
url = "https://192.0.2.10/restconf/data/ietf-interfaces:interfaces"
```

Si l'hôte change, il faut modifier le code. Si vous devez interroger plusieurs ressources, les URL risquent de se retrouver dispersées dans plusieurs fonctions.

Il est préférable de séparer :

- l'hôte et l'URL de base ;
- le chemin de la ressource ;
- les paramètres de requête ;
- le format de réponse attendu.

Cette séparation permet de réutiliser le même client sur plusieurs équipements.


# 3. ENVIRONNEMENT DE DÉVELOPPEMENT

## 3.1. Créer l'environnement

Linux ou macOS :

```bash
mkdir restconf-intermediaire
cd restconf-intermediaire

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install requests pytest
```

Windows PowerShell :

```powershell
mkdir restconf-intermediaire
cd restconf-intermediaire

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install requests pytest
```

Les versions exactes doivent être testées et verrouillées dans l'environnement retenu. Ne laissez pas une installation de production dépendre implicitement de la version la plus récente de chaque bibliothèque.

## 3.2. Arborescence proposée

```text
restconf-intermediaire/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── inventory.yaml
├── src/
│   └── restconf_client/
│       ├── __init__.py
│       ├── client.py
│       ├── errors.py
│       ├── validation.py
│       └── reporting.py
├── examples/
│   ├── read_interfaces.py
│   ├── discover_models.py
│   └── patch_lab_description.py
├── reports/
└── tests/
    ├── test_client.py
    └── test_validation.py
```

Chaque module a une responsabilité précise :

| Module | Fonction |
|---|---|
| `client.py` | Construire et envoyer les requêtes HTTP |
| `errors.py` | Définir des exceptions applicatives cohérentes |
| `validation.py` | Contrôler la forme et les champs des données |
| `reporting.py` | Générer des résultats et des rapports |
| `examples/` | Fournir de petits programmes d'utilisation |
| `tests/` | Vérifier le comportement du client sans équipement |

## 3.3. Gestion de configuration

Le fichier de paramètres ne doit pas contenir de mots de passe réels.

Exemple d'inventaire simple :

```yaml
devices:
  - name: router-lab-01
    host: 192.0.2.10
    restconf_port: 443
    enabled: true
    environment: lab

  - name: router-lab-02
    host: 192.0.2.11
    restconf_port: 443
    enabled: true
    environment: lab
```

Les adresses IP appartiennent ici à une plage de documentation. Remplacez-les par des adresses de laboratoire autorisées.

Les identifiants seront obtenus séparément. La présence d'un équipement dans l'inventaire ne constitue pas à elle seule une autorisation de le modifier.

## 3.4. Variables d'environnement

Exemple d'environnement de laboratoire :

```bash
export RESTCONF_HOST="192.0.2.10"
export RESTCONF_USERNAME="api-reader"
```

Sous PowerShell :

```powershell
$env:RESTCONF_HOST = "192.0.2.10"
$env:RESTCONF_USERNAME = "api-reader"
```

La manière de fournir le mot de passe dépend du système. Pour un usage régulier, privilégiez un mécanisme de gestion des secrets adapté à l'environnement.

N'écrivez pas :

```python
password = "mot-de-passe-reel"
```

dans le code source.

Les variables d'environnement constituent un moyen de séparer les paramètres sensibles du programme, mais elles ne sont pas automatiquement un coffre de secrets.


# 4. CONCEVOIR UN CLIENT PYTHON RÉUTILISABLE

Nous allons maintenant construire un client utilisable dans les exemples et les laboratoires suivants.

## 4.1. Définir des erreurs applicatives

`src/restconf_client/errors.py` :

```python
class RestconfError(RuntimeError):
    """Erreur de base pour le client RESTCONF."""


class RestconfTransportError(RestconfError):
    """Erreur de communication, TLS ou délai dépassé."""


class RestconfHttpError(RestconfError):
    """Réponse HTTP indiquant une erreur."""

    def __init__(
        self,
        status_code: int,
        method: str,
        resource: str,
        message: str,
    ):
        self.status_code = status_code
        self.method = method
        self.resource = resource
        self.message = message

        super().__init__(
            f"{method} {resource}: HTTP {status_code} - {message}"
        )


class RestconfResponseError(RestconfError):
    """Réponse reçue, mais représentation invalide."""
```

Pourquoi créer ses propres erreurs ?

Parce que le reste de l'application ne devrait pas dépendre de toutes les particularités internes de Requests. Le client convertit les erreurs techniques en catégories utiles à son application.

Une erreur TLS, un timeout, un `404` et un document JSON invalide ne signifient pas la même chose.

## 4.2. Construire le client

`src/restconf_client/client.py` :

```python
from __future__ import annotations

from urllib.parse import urlsplit

import requests

from .errors import (
    RestconfHttpError,
    RestconfResponseError,
    RestconfTransportError,
)


JSON_MEDIA_TYPE = "application/yang-data+json"
XML_MEDIA_TYPE = "application/yang-data+xml"


class RestconfClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        *,
        verify: bool | str = True,
        timeout: tuple[float, float] = (5.0, 25.0),
    ):
        parsed = urlsplit(base_url)

        if parsed.scheme.lower() != "https":
            raise ValueError(
                "RESTCONF doit utiliser HTTPS dans ce client."
            )

        if not parsed.hostname:
            raise ValueError("Nom d'hôte absent de l'URL.")

        if parsed.username or parsed.password:
            raise ValueError(
                "Ne placez pas d'identifiants dans l'URL."
            )

        if parsed.query or parsed.fragment:
            raise ValueError(
                "L'URL de base ne doit contenir ni query ni fragment."
            )

        if timeout[0] <= 0 or timeout[1] <= 0:
            raise ValueError("Les délais doivent être positifs.")

        self.base_url = base_url.rstrip("/")
        self.data_url = f"{self.base_url}/restconf/data"
        self.verify = verify
        self.timeout = timeout

        self.session = requests.Session()
        self.session.auth = (username, password)

        self.session.headers.update({
            "Accept": JSON_MEDIA_TYPE,
        })

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "RestconfClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def _url(self, resource: str) -> str:
        resource = resource.lstrip("/")

        if not resource:
            raise ValueError("Le chemin de ressource est vide.")

        return f"{self.data_url}/{resource}"

    def request(
        self,
        method: str,
        resource: str,
        *,
        params: dict | None = None,
        json_body: dict | list | None = None,
        headers: dict | None = None,
        expected_statuses: set[int] | None = None,
    ) -> requests.Response:
        method = method.upper()

        allowed_methods = {
            "GET", "HEAD", "OPTIONS",
            "POST", "PUT", "PATCH", "DELETE",
        }

        if method not in allowed_methods:
            raise ValueError("Méthode HTTP non autorisée par le client.")

        url = self._url(resource)

        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify,
                allow_redirects=False,
            )

        except requests.exceptions.SSLError as exc:
            raise RestconfTransportError(
                "Échec de vérification TLS."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise RestconfTransportError(
                "Délai de requête RESTCONF dépassé."
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            raise RestconfTransportError(
                "Connexion RESTCONF impossible."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise RestconfTransportError(
                f"Erreur du client HTTP : {type(exc).__name__}"
            ) from exc

        if expected_statuses is None:
            expected_statuses = {
                200, 201, 202, 204,
            }

        if response.status_code not in expected_statuses:
            # Ne pas placer automatiquement le corps complet dans
            # les logs : il peut contenir des données sensibles.
            raise RestconfHttpError(
                status_code=response.status_code,
                method=method,
                resource=resource,
                message="La requête n'a pas le statut attendu.",
            )

        return response

    def get_json(
        self,
        resource: str,
        *,
        params: dict | None = None,
    ) -> tuple[dict, requests.Response]:
        response = self.request(
            "GET",
            resource,
            params=params,
            expected_statuses={200},
        )

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "json" not in content_type:
            raise RestconfResponseError(
                "Le serveur n'a pas retourné un type de contenu JSON."
            )

        try:
            payload = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise RestconfResponseError(
                "Le corps de la réponse n'est pas un JSON valide."
            ) from exc
        except ValueError as exc:
            raise RestconfResponseError(
                "Le corps de la réponse ne peut pas être décodé en JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise RestconfResponseError(
                "La racine JSON attendue doit être un objet."
            )

        return payload, response
```

## 4.3. Les décisions importantes de ce client

### Une URL HTTPS imposée

Le client refuse le schéma HTTP. Cette décision évite qu'un oubli du développeur envoie des identifiants ou des données de gestion en clair.

Dans un environnement de laboratoire, il faut préparer la confiance TLS. Il ne faut pas transformer le refus TLS en désactivation permanente de la vérification.

### Une session persistante

L'objet `requests.Session` permet de réutiliser les en-têtes et les paramètres d'authentification. La fermeture explicite libère les ressources détenues par la session.

### Des délais explicites

Le paramètre `timeout=(5, 25)` donne deux valeurs : le délai de connexion et le délai de lecture. Ce ne sont pas des valeurs universelles ; elles doivent être adaptées au réseau et aux opérations.

### Aucun suivi automatique des redirections

Le client utilise `allow_redirects=False`. Cela évite de transférer implicitement une requête vers une autre destination sans contrôle de l'application.

Si une redirection est prévue dans votre infrastructure, traitez-la explicitement et vérifiez la destination avant de poursuivre.

### Des erreurs sans fuite de secret

Le client évite d'inclure automatiquement le contenu complet du corps de réponse dans son message d'erreur. Ce contenu pourrait contenir des informations opérationnelles sensibles.

Le diagnostic détaillé doit être ajouté au bon endroit, avec des règles de filtrage adaptées.

## 4.4. Utiliser le client

Exemple `examples/read_interfaces.py` :

```python
import os

from restconf_client.client import RestconfClient


def main() -> None:
    host = os.environ["RESTCONF_HOST"]
    username = os.environ["RESTCONF_USERNAME"]
    password = os.environ["RESTCONF_PASSWORD"]

    with RestconfClient(
        f"https://{host}",
        username,
        password,
        verify=True,
    ) as client:

        payload, response = client.get_json(
            "ietf-interfaces:interfaces"
        )

        print(f"HTTP {response.status_code}")
        print("ETag :", response.headers.get("ETag"))
        print(payload)


if __name__ == "__main__":
    main()
```

Cet exemple suppose que le serveur expose le module `ietf-interfaces`, que le chemin est disponible et que le compte a le droit d'accès.

Il ne garantit pas que tous les équipements exposent cette ressource sous cette forme.


# 5. CONSTRUIRE ET ENCODER LES URI RESTCONF

La construction des URI devient importante dès que les chemins contiennent des clés de listes, des espaces ou des caractères spéciaux.

## 5.1. Un chemin n'est pas une simple chaîne arbitraire

Un chemin RESTCONF peut ressembler à ceci :

```text
ietf-interfaces:interfaces/interface=Loopback0
```

Ce chemin identifie une ressource dans l'arbre de données.

Il ne faut pas le confondre avec une commande CLI ni supposer que tous les noms de champs sont universels.

## 5.2. Encoder les clés

Pour identifier une entrée de liste, la clé apparaît dans le chemin de ressource.

Une valeur contenant des espaces ou des caractères réservés doit être encodée conformément aux règles URI.

Exemple Python :

```python
from urllib.parse import quote


def encode_key(value: str) -> str:
    if not value:
        raise ValueError("La clé ne doit pas être vide.")

    return quote(value, safe="")
```

Usage :

```python
name = "Loopback 100"
encoded_name = encode_key(name)

resource = (
    "ietf-interfaces:interfaces/"
    f"interface={encoded_name}"
)

print(resource)
```

Résultat :

```text
ietf-interfaces:interfaces/interface=Loopback%20100
```

Cette opération encode la valeur de la clé et conserve les séparateurs que le programme a insérés autour.

**Important :** le nom d'interface utilisé dans l'exemple doit réellement exister et être accessible selon le modèle de l'équipement. Un chemin URI valide ne prouve pas que la ressource existe.

## 5.3. Ne pas encoder le chemin entier aveuglément

Si vous encodiez l'ensemble du chemin, vous pourriez transformer les séparateurs `/`, `:` ou `=` en données au lieu de les conserver comme éléments structurels.

Encodez les valeurs insérées dans le chemin, pas les éléments de syntaxe qui doivent rester des séparateurs.

## 5.4. Les paramètres de requête sont différents du chemin

Le chemin désigne la ressource.

Les paramètres affinent la requête.

Exemple :

```text
/restconf/data/ietf-interfaces:interfaces?content=config&depth=2
```

Dans Requests, il est préférable de fournir les paramètres séparément :

```python
payload, response = client.get_json(
    "ietf-interfaces:interfaces",
    params={
        "content": "config",
        "depth": "2",
    },
)
```

La bibliothèque encode les paramètres URI selon les règles HTTP. Évitez de construire manuellement des chaînes `?x=...&y=...` lorsque les valeurs peuvent contenir des caractères spéciaux.

## 5.5. Construire une ressource à partir d'une clé

Exemple générique :

```python
def interface_resource(name: str) -> str:
    encoded = encode_key(name)

    return (
        "ietf-interfaces:interfaces/"
        f"interface={encoded}"
    )
```

Utilisation :

```python
resource = interface_resource("Loopback0")
print(resource)
```

La séparation entre constructeur de ressource et code de requête facilite les tests et réduit les erreurs de chemin.


# 6. SÉLECTIONNER LES DONNÉES AVEC LES PARAMÈTRES RESTCONF

Un serveur peut retourner beaucoup plus de données que nécessaire. En intermédiaire, il faut apprendre à demander uniquement les informations utiles.

Le protocole RESTCONF définit plusieurs paramètres de requête. Certains peuvent dépendre des capacités annoncées par le serveur. Le détail complet est dans le [RFC 8040, section 4.8](https://www.rfc-editor.org/rfc/rfc8040.html).

## 6.1. Le paramètre `content`

Le paramètre `content` permet de demander des données de configuration, des données non configurables ou l'ensemble des données selon les règles applicables.

Les valeurs principales sont :

- `config` : données de configuration ;
- `nonconfig` : données non configurables ;
- `all` : les deux catégories.

Exemple :

```python
payload, response = client.get_json(
    "ietf-interfaces:interfaces",
    params={
        "content": "config",
    },
)
```

Cela demande au serveur de limiter la réponse aux données de configuration selon les règles du protocole et les ressources ciblées.

Ce paramètre ne change pas les permissions du compte. Il ne permet pas de lire des données auxquelles l'utilisateur n'a pas accès.

## 6.2. Le paramètre `depth`

Le paramètre `depth` limite la profondeur des sous-arbres retournés pour une requête de lecture lorsque cette fonction est prise en charge.

Exemple :

```python
payload, response = client.get_json(
    "ietf-interfaces:interfaces",
    params={
        "depth": "2",
    },
)
```

La profondeur permet de réduire la taille de la réponse et de rendre une inspection plus ciblée.

Une valeur trop faible peut exclure les champs recherchés. Une valeur trop élevée peut produire une réponse volumineuse.

La sémantique exacte du niveau de profondeur doit être comprise avant d'écrire un traitement métier dépendant d'un champ profond dans l'arbre.

## 6.3. Le paramètre `fields`

Le paramètre `fields` permet de demander un sous-ensemble des nœuds dans une ressource de données.

Exemple illustratif :

```python
payload, response = client.get_json(
    "ietf-interfaces:interfaces",
    params={
        "fields": "interface(name;description;enabled)",
    },
)
```

Cet exemple demande des champs associés aux interfaces. Il doit être vérifié avec le modèle YANG et les capacités de l'équipement.

Le chemin exact dépend des noms de nœuds présents dans le modèle et de la grammaire `fields` définie par RESTCONF.

## 6.4. Combiner plusieurs paramètres

```python
payload, response = client.get_json(
    "ietf-interfaces:interfaces",
    params={
        "content": "config",
        "depth": "2",
        "fields": "interface(name;description;enabled)",
    },
)
```

Cela demande une vue de la ressource qui limite la catégorie de données et la quantité de détails retournés.

Avant d'utiliser plusieurs paramètres ensemble, vérifiez qu'ils sont admis pour la ressource et la méthode. La prise en charge des paramètres optionnels doit être vérifiée dans l'implémentation.

## 6.5. Attention au paramètre `filter`

Un point important : le paramètre `filter` défini dans le RFC 8040 est utilisé pour filtrer les événements dans les ressources de flux d'événements. Il ne faut pas le confondre avec les syntaxes de filtre disponibles dans d'autres API ou d'autres protocoles.

Pour sélectionner certains champs d'une ressource de données RESTCONF, étudiez notamment `fields`. Pour des besoins plus spécifiques, vérifiez les mécanismes expressément pris en charge par la ressource et l'implémentation.

Une extension constructeur peut offrir une fonction qui porte un nom similaire. Elle doit être identifiée comme une extension, pas considérée automatiquement comme une règle universelle RESTCONF.

## 6.6. Découvrir les capacités des paramètres

Certaines fonctions RESTCONF sont signalées par des capacités du serveur.

Le client ne devrait donc pas supposer que chaque extension facultative est disponible sur chaque équipement.

La découverte des capacités permet d'éviter d'écrire une application qui échoue parce qu'elle utilise une fonctionnalité optionnelle absente du serveur.

## 6.7. Neuvième schéma SVG animé : réduire une réponse volumineuse

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 350" role="img" aria-labelledby="fields-title fields-desc" style="max-width:100%;height:auto">
  <title id="fields-title">Sélection des données RESTCONF</title>
  <desc id="fields-desc">Une grande ressource YANG est filtrée par catégorie, profondeur et champs, afin de produire une réponse plus petite et ciblée.</desc>
  <defs>
    <marker id="fields-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#65c4a6"/></marker>
    <style>
      @keyframes fields-flow { to { stroke-dashoffset:-24; } }
      .fields-link { fill:none;stroke:#65c4a6;stroke-width:2.4;stroke-dasharray:6 7;marker-end:url(#fields-arrow);animation:fields-flow 2s linear infinite; }
      .fields-label { fill:#f1f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .fields-small { fill:#bcc9dd;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="348" rx="14" fill="#0d1420" stroke="#293f56"/>
  <rect x="30" y="73" width="225" height="158" rx="10" fill="#23263d" stroke="#9b9ae6" stroke-width="1.5"/>
  <text x="142" y="99" class="fields-label">Ressource complète</text>
  <text x="142" y="123" class="fields-small">interfaces</text>
  <text x="142" y="145" class="fields-small">descriptions</text>
  <text x="142" y="167" class="fields-small">adresses</text>
  <text x="142" y="189" class="fields-small">statistiques</text>
  <text x="142" y="211" class="fields-small">autres champs</text>
  <rect x="349" y="88" width="245" height="126" rx="10" fill="#193247" stroke="#62bce5" stroke-width="1.5"/>
  <text x="471" y="114" class="fields-label">Paramètres GET</text>
  <text x="471" y="139" class="fields-small">content=config</text>
  <text x="471" y="159" class="fields-small">depth=2</text>
  <text x="471" y="179" class="fields-small">fields=...</text>
  <path class="fields-link" d="M255 151 H343"/>
  <rect x="690" y="88" width="220" height="126" rx="10" fill="#16352e" stroke="#65c4a6" stroke-width="1.5"/>
  <text x="800" y="114" class="fields-label">Réponse ciblée</text>
  <text x="800" y="141" class="fields-small">champs demandés</text>
  <text x="800" y="162" class="fields-small">volume réduit</text>
  <text x="800" y="183" class="fields-small">validation facilitée</text>
  <path class="fields-link" d="M594 151 H684"/>
  <text x="470" y="270" class="fields-label">Moins de données inutiles, sans réduire le contrôle métier</text>
  <text x="470" y="295" class="fields-small">Toujours vérifier la présence et le type des champs réellement attendus.</text>
</svg>

## 6.8. Pourquoi sélectionner les données ?

La sélection est utile pour :

- réduire le volume de transfert ;
- accélérer certaines collectes ;
- simplifier les validations ;
- éviter de conserver inutilement des données sensibles ;
- limiter le traitement à ce dont l'application a réellement besoin.

Mais une réponse réduite n'est pas nécessairement une réponse complète. Il faut vérifier que tous les champs obligatoires pour l'opération se trouvent bien dans les données reçues.


# 7. DÉCOUVRIR LES MODÈLES YANG ET LA YANG LIBRARY

Au niveau Débutant, vous avez appris à utiliser un chemin de ressource connu. Au niveau Intermédiaire, vous devez commencer à découvrir les capacités et les modèles présents sur le serveur.

## 7.1. Pourquoi la découverte est essentielle

Prenons deux équipements.

Le premier prend en charge un modèle standard et une ressource que votre programme souhaite interroger.

Le second expose une version différente du modèle, un ensemble de données différent ou une extension propre au constructeur.

Si le code suppose que les deux serveurs sont identiques, il risque d'échouer ou de mal interpréter certaines valeurs.

La découverte permet de réduire ces hypothèses.

## 7.2. La YANG Library

Le [RFC 8525 — YANG Library](https://www.rfc-editor.org/rfc/rfc8525.html) décrit un mécanisme permettant à un serveur de communiquer les modules YANG, les datastores et les schémas utilisés.

Dans une implémentation conforme à l'architecture NMDA, la ressource de la YANG Library peut être interrogée dans le datastore opérationnel :

```text
/restconf/ds/ietf-datastores:operational/ietf-yang-library:yang-library
```

Cette URI est un exemple correspondant à l'architecture NMDA. Vérifiez que le serveur prend en charge ces extensions avant d'utiliser ce chemin.

Dans des implémentations plus anciennes, la découverte des modules peut être exposée sous une autre forme, notamment avec les structures historiques de YANG Library.

## 7.3. Effectuer une découverte avec le client

```python
payload, response = client.get_json(
    "ietf-yang-library:yang-library",
    params={
        "depth": "unbounded",
    },
)
```

**Attention :** ce chemin relatif correspond à une ressource du datastore `data`. Pour un serveur utilisant la ressource NMDA décrite plus haut, le chemin doit viser `ds/ietf-datastores:operational/ietf-yang-library:yang-library`. Le client construit dans ce cours pointe par défaut vers `/restconf/data`.

Nous pouvons donc utiliser un chemin configuré pour le datastore opérationnel en étendant le client, ou en créant un accès spécifique au chemin `ds`.

Exemple générique pour accéder à une ressource sous la racine RESTCONF sans imposer le datastore `data` :

```python
def restconf_root_url(host: str) -> str:
    return f"https://{host.rstrip('/')}/restconf"


def operational_yang_library_path() -> str:
    return (
        "ds/ietf-datastores:operational/"
        "ietf-yang-library:yang-library"
    )
```

Dans une application complète, créez un constructeur d'URI distinct pour les ressources sous `/restconf/ds` au lieu de faire passer chaque ressource à travers la racine `/restconf/data`.

Le fait qu'une ressource soit standardisée ne dispense pas de vérifier qu'elle est exposée par la version réelle du serveur.

## 7.4. Découverte de l'état de l'API et des modules

Lorsqu'elle est disponible, la découverte de la YANG Library permet notamment de connaître :

- les noms de modules ;
- les révisions de modules ;
- les schémas associés aux datastores ;
- certaines métadonnées utiles à l'identification du jeu de modèles.

Une application peut ensuite comparer le modèle observé avec les capacités qu'elle attend.

Par exemple, elle peut vérifier si un module nécessaire est présent avant de lancer une opération dépendante de ce modèle.

## 7.5. Ne pas supposer une révision fixe

Un module peut exister avec différentes révisions.

Il est dangereux de supposer qu'un schéma de votre documentation locale correspond nécessairement à la révision effectivement exposée par l'équipement.

Le code doit au minimum conserver l'information de révision et signaler les écarts importants lorsqu'ils affectent son comportement.

## 7.6. Le cache de schéma

La découverte peut être coûteuse si l'application relit systématiquement de nombreux modules avant chaque requête.

La YANG Library fournit des mécanismes qui permettent aux clients de déterminer quand les informations de bibliothèque évoluent.

Une architecture intermédiaire peut :

1. découvrir la YANG Library ;
2. enregistrer un identifiant de contenu ou de révision pertinent ;
3. conserver un cache local de métadonnées ;
4. vérifier si la version des métadonnées a changé ;
5. rafraîchir le cache lorsqu'un changement est détecté.

Ne conservez pas ce cache indéfiniment sans mécanisme d'invalidation. Si les modèles changent, le programme risque d'utiliser un schéma obsolète.

## 7.7. Dixième schéma SVG animé : découvrir les modèles

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 350" role="img" aria-labelledby="library-title library-desc" style="max-width:100%;height:auto">
  <title id="library-title">Découverte de la YANG Library</title>
  <desc id="library-desc">Le client lit la YANG Library, identifie les modules et révisions et sélectionne ensuite les chemins compatibles avec le serveur.</desc>
  <defs>
    <marker id="library-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#bc9cf2"/></marker>
    <style>
      @keyframes library-flow { to { stroke-dashoffset:-28; } }
      .library-link { fill:none;stroke:#bc9cf2;stroke-width:2.5;stroke-dasharray:7 7;marker-end:url(#library-arrow);animation:library-flow 2s linear infinite; }
      .library-label { fill:#f2f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .library-small { fill:#bdc9dd;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="348" rx="14" fill="#101525" stroke="#343653"/>
  <rect x="25" y="86" width="220" height="83" rx="10" fill="#22243c" stroke="#a49ae8" stroke-width="1.5"/>
  <text x="135" y="113" class="library-label">Client RESTCONF</text><text x="135" y="135" class="library-small">découverte des modules</text><text x="135" y="152" class="library-small">et des capacités</text>
  <path class="library-link" d="M245 127 H300"/>
  <rect x="305" y="86" width="290" height="83" rx="10" fill="#173246" stroke="#63bce6" stroke-width="1.5"/>
  <text x="450" y="113" class="library-label">YANG Library</text><text x="450" y="135" class="library-small">modules · révisions</text><text x="450" y="152" class="library-small">datastores · schémas</text>
  <path class="library-link" d="M595 127 H650"/>
  <rect x="655" y="86" width="260" height="83" rx="10" fill="#18372f" stroke="#67c9a7" stroke-width="1.5"/>
  <text x="785" y="113" class="library-label">Client adapté</text><text x="785" y="135" class="library-small">chemins connus</text><text x="785" y="152" class="library-small">validation ciblée</text>
  <rect x="170" y="217" width="600" height="61" rx="10" fill="#322a1e" stroke="#e4b260" stroke-width="1.5"/>
  <text x="470" y="242" class="library-label">Vérifier avant d'exécuter</text><text x="470" y="261" class="library-small">un module absent ou une révision inattendue peut invalider le plan</text>
  <path class="library-link" d="M450 169 V212"/>
</svg>


# 8. COMPRENDRE LES DÉTAILS DE L'ENCODAGE JSON POUR YANG

À ce niveau, connaître JSON ne suffit plus. Vous devez reconnaître les règles qui relient un modèle YANG à sa représentation JSON.

## 8.1. Les objets de premier niveau

Une représentation JSON de données YANG commence par un objet et suit les conventions de nommage et de typage du RFC 7951.

Exemple générique :

```json
{
  "example-network:device": {
    "name": "router-lab-01",
    "enabled": true
  }
}
```

Le préfixe de module est significatif. Il ne faut pas supprimer les noms qualifiés arbitrairement lors de la normalisation des réponses.

## 8.2. Les booléens sont des booléens

Si le modèle prévoit un champ de type `boolean`, les valeurs JSON attendues sont :

```json
{
  "enabled": true
}
```

et :

```json
{
  "enabled": false
}
```

Elles ne sont pas équivalentes aux chaînes `"true"` et `"false"`.

Cette différence est particulièrement importante lorsqu'on construit un corps de modification à partir d'un formulaire ou d'un fichier de paramètres.

## 8.3. Les chaînes numériques particulières

Le RFC 7951 prévoit notamment que certains types numériques YANG de 64 bits, ainsi que `decimal64`, soient représentés sous forme de chaînes JSON.

Par exemple, un champ de type `uint64` peut être représenté comme suit :

```json
{
  "counter": "1234567890123456789"
}
```

Il ne faut pas supposer que toute valeur numérique YANG est toujours un nombre JSON.

Cela peut affecter le parsing, le typage Python et la manière dont un système de rapport sérialise les valeurs.

Référence : [RFC 7951 — JSON Encoding of Data Modeled with YANG](https://www.rfc-editor.org/rfc/rfc7951.html).

## 8.4. Les listes et les clés

Une liste YANG peut être représentée par un tableau JSON.

Exemple :

```json
{
  "example-network:interfaces": {
    "interface": [
      {
        "name": "Loopback0",
        "enabled": true
      },
      {
        "name": "Loopback1",
        "enabled": false
      }
    ]
  }
}
```

Le nom d'interface sert ici d'exemple de clé de liste. Le vrai modèle utilisé par l'équipement détermine les clés et les champs autorisés.

## 8.5. L'ordre des propriétés ne doit pas être une règle métier

L'ordre des membres d'un objet JSON ne doit pas être utilisé pour définir la signification des données.

Il faut accéder aux champs par leur nom :

```python
interface_name = interface["name"]
enabled = interface["enabled"]
```

et non supposer que le premier champ est toujours le nom ou que la description apparaîtra toujours avant le champ `enabled`.

## 8.6. Comparer une réponse au schéma attendu

Exemple simplifié de validation :

```python
def validate_interface_item(item: dict) -> None:
    if not isinstance(item, dict):
        raise ValueError("L'interface doit être un objet JSON.")

    required_fields = {"name", "enabled"}

    missing = required_fields - item.keys()

    if missing:
        raise ValueError(
            f"Champs manquants : {sorted(missing)}"
        )

    if not isinstance(item["name"], str):
        raise ValueError("Le nom doit être une chaîne.")

    if not isinstance(item["enabled"], bool):
        raise ValueError("enabled doit être un booléen.")
```

Cette validation ne remplace pas le schéma YANG complet. Elle démontre le principe : l'application définit explicitement ce dont elle a besoin.

Le modèle peut exiger d'autres champs, utiliser d'autres types ou encadrer les valeurs par des contraintes supplémentaires.

## 8.7. Pourquoi cette validation doit rester spécifique

Une validation universelle de toutes les ressources RESTCONF serait difficile à maintenir sans connaître les modèles concernés.

La solution habituelle consiste à :

1. découvrir les modules et les révisions ;
2. définir un contrat pour chaque opération utilisée ;
3. vérifier les types et les champs nécessaires ;
4. produire une erreur explicite lorsque les données ne respectent pas le contrat.

Le niveau Expert pourra ensuite aller plus loin avec une validation plus systématique fondée sur les modèles disponibles.


# 9. GÉRER LES RÉPONSES ET LES ERREURS

## 9.1. Classer les erreurs par catégorie

Un client intermédiaire ne doit pas traiter chaque problème comme une simple erreur générique.

Il doit au minimum distinguer :

- problème TLS ;
- problème de connexion ;
- timeout ;
- réponse HTTP d'erreur ;
- corps JSON invalide ;
- contenu reçu inattendu ;
- structure de données non conforme ;
- échec de validation métier.

Le module `errors.py` du chapitre 4 donne un premier modèle.

## 9.2. Interpréter les principaux statuts

| Statut | Interprétation possible | Réaction |
|---|---|---|
| `200` | Requête réussie avec une représentation | Vérifier le corps |
| `201` | Ressource créée | Vérifier la réponse et l'emplacement retourné |
| `204` | Opération réussie sans corps | Ne pas tenter de décoder un JSON vide |
| `400` | Requête invalide | Examiner le chemin, les types et les contraintes |
| `401` | Authentification échouée | Vérifier le profil d'accès |
| `403` | Opération interdite | Vérifier les droits |
| `404` | Chemin ou ressource non disponible | Vérifier le modèle et l'URI |
| `405` | Méthode non autorisée pour la ressource | Vérifier l'opération |
| `409` | Conflit possible | Examiner l'état et les règles du serveur |
| `412` | Précondition non satisfaite | Relire l'état et décider de la suite |
| `415` | Type de contenu non pris en charge | Vérifier `Content-Type` |
| `429` | Limitation de débit, si utilisée par le serveur | Réduire le rythme et respecter les indications du serveur |
| `5xx` | Erreur côté serveur | Consulter les journaux autorisés et analyser la cause |

Cette table fournit des repères opérationnels. Les réponses RESTCONF, la présence des informations d'erreur et le comportement de l'équipement doivent être examinés dans leur contexte.

## 9.3. Le corps d'erreur RESTCONF

Une erreur peut inclure des informations structurées permettant de comprendre ce qui s'est passé.

Ne supposez pas que toutes les implémentations utilisent exactement la même formulation du message. Lorsque le corps suit le format RESTCONF défini, vous pouvez en extraire les champs prévus par ce format. Si la réponse est spécifique au constructeur, adaptez le parseur.

Il est utile de garder :

- le statut HTTP ;
- la méthode ;
- la ressource ;
- la catégorie de l'erreur ;
- le détail assaini nécessaire au diagnostic.

En revanche, le corps complet ne devrait pas être copié automatiquement dans les journaux sans contrôle, puisqu'il peut contenir des informations sensibles.

## 9.4. Une erreur de parsing n'est pas un succès

Cette écriture est insuffisante :

```python
try:
    data = response.json()
except ValueError:
    data = {}
```

Elle transforme l'échec en objet vide. Le programme en aval peut ensuite traiter ce résultat comme si le serveur avait renvoyé des données valides.

Une meilleure démarche consiste à lever une erreur précise :

```python
try:
    data = response.json()
except ValueError as exc:
    raise RestconfResponseError(
        "Réponse JSON invalide."
    ) from exc
```

Le résultat invalide n'est pas silencieusement remplacé par des données vides.

## 9.5. Distinguer statut HTTP et statut métier

Vous pouvez représenter le résultat d'une opération avec deux champs :

```json
{
  "transport_status": "success",
  "http_status": 200,
  "validation_status": "failed",
  "reason": "Champ enabled absent"
}
```

L'exemple illustre un point important : une requête peut fonctionner au niveau HTTP tout en échouant lors de la validation de la réponse.

Cette distinction doit être reprise dans les rapports et les tests.


# 10. SÉCURISER LES REQUÊTES ET CONTRÔLER LES DROITS

## 10.1. Vérifier le certificat TLS

Le client du cours utilise `verify=True`.

Dans certains environnements, l'autorité de certification interne doit être fournie explicitement :

```python
with RestconfClient(
    "https://router-lab.example",
    username,
    password,
    verify="/etc/ssl/certs/lab-ca.pem",
) as client:
    ...
```

Le chemin du certificat doit être adapté à votre environnement.

N'utilisez pas `verify=False` comme paramètre par défaut. Cela désactive la validation TLS et peut supprimer une protection importante contre l'usurpation du serveur.

Si un certificat échoue, identifiez la cause : nom ne correspondant pas, certificat expiré, autorité inconnue ou configuration TLS incorrecte.

## 10.2. Réduire les permissions

Un client de collecte devrait utiliser un compte de lecture.

Un client de modification devrait utiliser un profil différent et les permissions strictement nécessaires.

Ne donnez pas à un outil d'inventaire la capacité de supprimer des ressources ou de modifier le routage si cette fonction n'est pas requise.

## 10.3. Protéger les identifiants

Les secrets ne doivent pas se retrouver dans :

- les URI ;
- les fichiers versionnés ;
- le code ;
- les journaux ;
- les rapports ;
- les messages d'erreur ;
- les captures partagées.

L'application doit éviter d'afficher les en-têtes d'authentification, les cookies ou les autres informations confidentielles.

## 10.4. Contrôler les redirections

Le client de référence désactive le suivi automatique des redirections.

Cette décision évite de laisser la bibliothèque transférer une requête vers une destination inattendue sans contrôle du programme.

Si un serveur doit rediriger les requêtes, implémentez un traitement qui valide explicitement la destination et les règles de transmission des identifiants.

## 10.5. Limiter les journaux

Ne journalisez pas systématiquement toutes les données retournées.

Les sorties peuvent contenir des informations de topologie, de configuration ou d'exploitation.

Le meilleur journal est celui qui permet de diagnostiquer l'opération sans exposer les informations qui ne sont pas nécessaires.


# 11. MODIFIER UNE RESSOURCE AVEC PATCH

Au niveau Débutant, nous avons privilégié les lectures. Le niveau Intermédiaire introduit les modifications, mais uniquement dans un environnement de laboratoire autorisé.

## 11.1. Qu'est-ce que PATCH ?

Dans RESTCONF, `PATCH` permet d'apporter une modification partielle à une ressource.

Avec le mécanisme *plain patch* défini par le RFC 8040, le serveur fusionne le contenu fourni avec la ressource ciblée selon la sémantique prévue.

Ce mécanisme est utile lorsqu'on souhaite modifier un champ sans remplacer toute une ressource.

Il ne doit pas être confondu avec tous les autres types de PATCH HTTP existants.

## 11.2. Exemple pédagogique d'une modification partielle

Supposons qu'un équipement de laboratoire expose une ressource correspondant à la description d'une interface selon le modèle `ietf-interfaces`.

Le chemin peut ressembler à :

```text
/restconf/data/ietf-interfaces:interfaces/interface=Loopback0/description
```

Cette URI est un exemple. Vérifiez que le modèle, l'interface et la ressource existent réellement.

Le corps JSON d'une opération de modification doit respecter les règles d'encodage et de qualification des noms définies par YANG et RESTCONF. Pour une ressource précise, la forme exacte doit être vérifiée avec le modèle et la documentation de l'équipement.

La cible de la modification doit toujours être aussi précise que possible. Modifier une ressource parent plus large que nécessaire augmente le risque d'effets imprévus.

## 11.3. Préparer le client pour un PATCH

La méthode `request()` du client accepte déjà `json_body` et `headers`.

Pour envoyer un PATCH :

```python
response = client.request(
    "PATCH",
    resource,
    json_body=payload,
    headers={
        "Content-Type": "application/yang-data+json",
    },
    expected_statuses={200, 204},
)
```

Les variables `resource` et `payload` doivent être construits conformément au modèle YANG réel.

Les réponses `200` et `204` ne doivent pas être traitées de manière identique lorsqu'il s'agit de lire leur contenu. Un statut `204` signifie qu'il n'y a pas de corps de réponse à décoder.

## 11.4. Contrôler le plan avant son application

Avant un PATCH de configuration, le programme devrait :

1. vérifier l'équipement ciblé ;
2. vérifier l'existence de la ressource ;
3. lire l'état initial ;
4. identifier les champs à modifier ;
5. valider le type des valeurs ;
6. préparer le corps de requête ;
7. présenter le plan ;
8. vérifier l'autorisation ;
9. appliquer la modification ;
10. relire la ressource ;
11. comparer l'état obtenu à l'objectif.

Cette séquence réduit le risque d'une opération mal ciblée ou mal comprise.

## 11.5. Une modification peut échouer même si la connexion fonctionne

Une erreur peut survenir si :

- le champ n'existe pas ;
- le type est invalide ;
- la valeur viole une contrainte YANG ;
- le compte n'a pas le droit ;
- la ressource n'existe pas ;
- le serveur ne supporte pas l'opération ;
- une autre modification a créé un conflit ;
- le corps ne respecte pas l'encodage demandé.

Une bonne application classe l'erreur et conserve l'état initial pour aider au diagnostic.


# 12. COMPRENDRE PUT, POST ET DELETE

Les méthodes HTTP ne sont pas interchangeables. Une automatisation doit choisir la méthode correspondant à l'opération sur la ressource.

## 12.1. `PUT` : remplacer une représentation de ressource

`PUT` peut remplacer la représentation d'une ressource ciblée conformément à la sémantique RESTCONF.

Si l'on remplace une ressource par un corps incomplet, des données absentes du corps peuvent être supprimées de la ressource remplacée.

C'est pourquoi `PUT` peut présenter davantage de risques qu'un PATCH ciblant quelques champs.

Exemple conceptuel :

```python
response = client.request(
    "PUT",
    resource,
    json_body=complete_resource_payload,
    headers={
        "Content-Type": "application/yang-data+json",
    },
    expected_statuses={200, 201, 204},
)
```

Le nom `complete_resource_payload` est intentionnel : un PUT doit être construit avec une connaissance suffisante de la ressource ciblée. Ne remplacez pas une ressource complexe avec un objet JSON partiel en supposant qu'il sera fusionné.

Les statuts possibles dépendent du cas d'utilisation et du serveur ; adaptez les résultats attendus à l'opération prévue.

## 12.2. `POST` : créer une ressource ou invoquer une opération

RESTCONF emploie `POST` notamment pour créer certaines ressources enfants ou invoquer les opérations correspondant à des RPC ou des actions YANG.

Il faut distinguer les deux usages.

### Création de ressource

Le chemin cible généralement le parent dans lequel la nouvelle ressource doit être créée.

Le corps doit respecter le modèle et contenir les données requises.

La réponse peut fournir l'emplacement de la ressource créée.

### Invocation d'une opération

RESTCONF peut exposer une opération YANG à travers l'espace de ressources d'opérations.

Le chemin, les paramètres et le résultat dépendent de l'opération définie dans le modèle.

N'invoquez pas une opération en envoyant simplement une chaîne au chemin d'une ressource de données ordinaire.

## 12.3. `DELETE` : supprimer une ressource

`DELETE` supprime la ressource visée, si le serveur accepte l'opération et si les permissions le permettent.

Cette opération est potentiellement destructive.

Avant de l'exécuter :

- vérifiez le chemin exact ;
- relisez la ressource ;
- vérifiez que la suppression est autorisée ;
- contrôlez les dépendances éventuelles ;
- définissez les conditions d'arrêt ;
- vérifiez le résultat ensuite.

N'utilisez pas `DELETE` comme mécanisme de nettoyage automatique sans définir clairement le périmètre.

## 12.4. Tableau récapitulatif

| Méthode | Utilisation typique | Risque principal |
|---|---|---|
| `GET` | Lire une ressource | Interpréter incorrectement la réponse |
| `POST` | Créer une ressource ou invoquer une opération | Créer un élément inattendu ou déclencher une opération |
| `PUT` | Remplacer une ressource | Perdre des champs non présents dans le corps |
| `PATCH` | Modifier partiellement une ressource | Modifier des champs non prévus si le corps est incorrect |
| `DELETE` | Supprimer une ressource | Suppression involontaire |

Aucune méthode ne doit être choisie uniquement parce que son nom paraît correspondre au besoin. Il faut respecter la sémantique RESTCONF, le modèle et la ressource exacte.


# 13. APPLIQUER YANG PATCH

Le *plain patch* de RESTCONF est adapté à certaines modifications simples. Pour décrire une séquence plus précise d'opérations d'édition, le mécanisme YANG Patch existe.

Il est spécifié dans le [RFC 8072 — YANG Patch Media Type](https://www.rfc-editor.org/rfc/rfc8072.html).

## 13.1. Pourquoi YANG Patch existe

Un changement peut inclure plusieurs sous-opérations, par exemple :

- fusionner des données ;
- créer un élément ;
- supprimer un élément ;
- insérer une entrée ;
- appliquer plusieurs modifications ordonnées.

YANG Patch définit une structure pour décrire ces opérations.

Il utilise les types de contenu :

```http
application/yang-patch+json
```

ou :

```http
application/yang-patch+xml
```

Le mécanisme et les opérations prises en charge doivent être vérifiés pour l'implémentation cible.

## 13.2. Découvrir si YANG Patch est disponible

Le client doit vérifier les capacités et les types de PATCH acceptés par le serveur.

Le RFC 8040 prévoit notamment l'utilisation d'une requête `OPTIONS` et l'examen de l'en-tête `Accept-Patch` pour connaître les types pris en charge.

Exemple :

```python
response = client.request(
    "OPTIONS",
    "ietf-interfaces:interfaces",
    expected_statuses={200, 204},
)

print(response.headers.get("Allow"))
print(response.headers.get("Accept-Patch"))
```

Le résultat est propre à la ressource et au serveur. Une absence d'en-tête ou de capacité ne doit pas être transformée arbitrairement en preuve de prise en charge.

## 13.3. Exemple conceptuel de YANG Patch

Le corps d'un YANG Patch contient une structure décrivant le patch, ses identifiants et les opérations associées.

Exemple pédagogique illustrant la forme générale :

```json
{
  "ietf-yang-patch:yang-patch": {
    "patch-id": "lab-change-001",
    "edit": [
      {
        "edit-id": "edit-1",
        "operation": "merge",
        "target": "/example-network:device/description",
        "value": {
          "example-network:description": "LAB-UPDATED"
        }
      }
    ]
  }
}
```

**Important :** les noms de modules, le chemin cible et la structure exacte du corps doivent correspondre aux schémas et à l'encodage du serveur. Cet exemple illustre le principe de la structure YANG Patch ; ce n'est pas une modification directement applicable à tout équipement.

L'implémentation doit utiliser les formes de nœuds et de valeurs exigées par le modèle YANG Patch et le RFC 8072.

## 13.4. Le principe atomique

Le RFC 8072 précise que, pour un protocole prenant en charge le mécanisme YANG Patch, si le document complet ne peut pas être appliqué avec succès, le serveur ne doit pas appliquer une partie des changements.

Cette propriété est importante pour comprendre les modifications multiples.

Elle ne permet toutefois pas de supposer que tout ensemble d'opérations RESTCONF possède une transaction universelle ou que les conséquences métier seront automatiquement annulées dans tous les systèmes externes.

Vérifiez la prise en charge effective de YANG Patch et le comportement documenté du serveur.

## 13.5. Quand utiliser chaque approche ?

- Utilisez le *plain patch* pour une modification ciblée appropriée à sa sémantique.
- Envisagez YANG Patch lorsqu'un ensemble explicite de sous-opérations doit être décrit.
- Utilisez PUT uniquement si la représentation de remplacement est correctement construite.
- Évitez de confondre plusieurs opérations HTTP séquentielles avec une transaction atomique.


# 14. DÉTECTER LES MODIFICATIONS CONCURRENTES AVEC ETAG

Une situation fréquente en administration réseau est celle où deux clients modifient le même équipement.

L'un lit une ressource. Un autre la modifie. Le premier envoie ensuite une modification fondée sur un état devenu obsolète.

Les mécanismes de précondition HTTP peuvent aider à détecter certains conflits.

## 14.1. Qu'est-ce qu'un ETag ?

Un ETag est un identifiant de version opaque que le serveur associe à une ressource ou à une représentation selon les règles applicables.

Dans RESTCONF, le serveur maintient un ETag pour la ressource datastore et le retourne dans les réponses de récupération prévues par le protocole. Des ETags peuvent également être fournis pour des ressources de configuration, avec les règles définies par le RFC 8040.

Le client ne doit pas calculer lui-même l'ETag à partir du JSON. Il doit utiliser celui retourné par le serveur.

## 14.2. Le principe de `If-Match`

Le client lit la ressource et conserve l'ETag retourné.

Lorsqu'il prépare une modification, il envoie cet ETag dans l'en-tête `If-Match`.

Le serveur peut alors rejeter la requête si l'ETag ne correspond plus à celui de la ressource concernée.

C'est une forme de contrôle optimiste des modifications : elle permet de détecter que l'état sur lequel le client s'est fondé a changé.

## 14.3. Flux de contrôle

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="etag-title etag-desc" style="max-width:100%;height:auto">
  <title id="etag-title">Contrôle de concurrence avec ETag et If-Match</title>
  <desc id="etag-desc">Le client lit une ressource et conserve son ETag. Il envoie ensuite une modification avec If-Match. Le serveur accepte si la précondition est satisfaite et peut rejeter si la ressource a changé.</desc>
  <defs>
    <marker id="etag-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#65c4a6"/></marker>
    <style>
      @keyframes etag-flow { to { stroke-dashoffset:-28; } }
      .etag-link { fill:none;stroke:#65c4a6;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#etag-arrow);animation:etag-flow 2s linear infinite; }
      .etag-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .etag-small { fill:#becbe0;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="353" rx="14" fill="#0d1420" stroke="#2e4159"/>
  <rect x="28" y="75" width="205" height="75" rx="10" fill="#282440" stroke="#b2a2f0" stroke-width="1.5"/>
  <text x="130" y="103" class="etag-label">Client</text><text x="130" y="124" class="etag-small">GET + stockage ETag</text>
  <rect x="365" y="75" width="210" height="75" rx="10" fill="#193346" stroke="#64bce6" stroke-width="1.5"/>
  <text x="470" y="103" class="etag-label">Serveur RESTCONF</text><text x="470" y="124" class="etag-small">ETag courant</text>
  <rect x="707" y="75" width="205" height="75" rx="10" fill="#17352e" stroke="#65c4a6" stroke-width="1.5"/>
  <text x="809" y="103" class="etag-label">Autre client</text><text x="809" y="124" class="etag-small">peut modifier l'état</text>
  <path class="etag-link" d="M233 95 H360"/>
  <text x="296" y="83" class="etag-small">GET</text>
  <path class="etag-link" d="M360 132 H238"/>
  <text x="299" y="151" class="etag-small">réponse + ETag</text>
  <path d="M809 150 V194 H470 V155" fill="none" stroke="#e5b161" stroke-width="2.3" stroke-dasharray="6 7" style="animation:etag-flow 2.3s linear infinite"/>
  <text x="661" y="188" class="etag-small">changement concurrent</text>
  <path class="etag-link" d="M233 116 H304 V244 H700"/>
  <text x="470" y="236" class="etag-small">PATCH avec If-Match: ETag lu</text>
  <rect x="707" y="220" width="205" height="80" rx="10" fill="#30251b" stroke="#e5b161" stroke-width="1.5"/>
  <text x="809" y="248" class="etag-label">Évaluation</text><text x="809" y="270" class="etag-small">précondition vraie ?</text>
  <path class="etag-link" d="M809 300 V324 H470"/>
  <text x="621" y="343" class="etag-small">réussite ou conflit à traiter</text>
</svg>

## 14.4. Exemple Python d'une lecture avec ETag

```python
resource = (
    "ietf-interfaces:interfaces/"
    "interface=Loopback0/description"
)

payload, response = client.get_json(resource)

etag = response.headers.get("ETag")

if not etag:
    raise RuntimeError(
        "Aucun ETag disponible pour la ressource lue."
    )

print("ETag obtenu :", etag)
print("Données :", payload)
```

La disponibilité d'un ETag au niveau exact de la ressource dépend du serveur et des règles de RESTCONF. Le protocole prévoit aussi un ETag pour la ressource datastore. Lorsqu'une ressource particulière ne fournit pas son propre ETag, il peut être nécessaire d'utiliser le mécanisme prévu par le protocole pour le datastore.

## 14.5. Exemple d'une modification conditionnelle

Le corps doit respecter le modèle et le chemin exacts.

```python
response = client.request(
    "PATCH",
    resource,
    json_body={
        "ietf-interfaces:description": "LAB-UPDATED",
    },
    headers={
        "Content-Type": "application/yang-data+json",
        "If-Match": etag,
    },
    expected_statuses={200, 204},
)
```

Cet exemple représente le principe de l'opération conditionnelle. Avant de l'utiliser, vérifiez la forme du corps correspondant à la ressource cible, le modèle disponible et la prise en charge des préconditions.

## 14.6. Comment traiter un conflit ?

Si le serveur indique que la précondition n'est plus satisfaite, ne remplacez pas simplement l'ETag par une nouvelle valeur et ne relancez pas immédiatement la modification.

La bonne démarche est :

1. relire la ressource ;
2. constater les différences ;
3. vérifier si un autre client a modifié les données ;
4. comparer l'état actuel à l'objectif ;
5. déterminer si le changement initial reste nécessaire ;
6. préparer une nouvelle opération ;
7. obtenir l'autorisation requise avant de recommencer.

Un conflit est une information importante. Il indique que les hypothèses utilisées lors de la préparation du changement doivent être réévaluées.


# 15. VÉRIFIER L'ÉTAT AVANT ET APRÈS UN CHANGEMENT

La réussite d'une opération HTTP ne garantit pas le résultat final du service réseau.

Il faut comparer l'état obtenu avec l'état attendu.

## 15.1. Le cycle pré/post

Le programme doit pouvoir :

1. lire l'état initial ;
2. vérifier les préconditions ;
3. calculer les changements nécessaires ;
4. préparer le plan ;
5. appliquer le changement autorisé ;
6. relire l'état ;
7. comparer les champs attendus ;
8. produire un résultat clair.

## 15.2. Exemple de validation métier

Voici une fonction générique qui vérifie une propriété dans un objet :

```python
def require_expected_value(
    actual: dict,
    field: str,
    expected,
) -> None:
    if field not in actual:
        raise ValueError(
            f"Le champ obligatoire {field!r} est absent."
        )

    if actual[field] != expected:
        raise ValueError(
            f"Valeur incorrecte pour {field!r}."
        )
```

Cette validation est volontairement simple. Les traitements réels doivent respecter le modèle et les types de données.

Elle montre cependant un principe fondamental : le programme vérifie la valeur attendue au lieu de se contenter de recevoir une réponse.

## 15.3. Ne pas supposer que les valeurs sont toujours présentes

Un champ absent ne signifie pas nécessairement que sa valeur est `false`, zéro ou une chaîne vide.

Le champ peut être absent en raison du modèle, de la sélection des champs, de permissions, de la sémantique de données ou d'un défaut de réponse.

Le programme doit savoir distinguer :

- champ présent et conforme ;
- champ présent mais non conforme ;
- champ absent ;
- réponse invalide ;
- ressource inaccessible.

## 15.4. Éviter les modifications automatiques sur la seule base d'un écart

Une comparaison révèle qu'un état diffère d'une valeur attendue.

Cela ne signifie pas toujours qu'il faut modifier l'équipement immédiatement.

L'écart peut être légitime, volontaire ou lié à un changement en cours. Avant de corriger, vérifiez les règles métier et le périmètre d'autorisation.

## 15.5. Onzième schéma SVG animé : la boucle de validation

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 365" role="img" aria-labelledby="verify-title verify-desc" style="max-width:100%;height:auto">
  <title id="verify-title">Cycle de validation pré et post changement</title>
  <desc id="verify-desc">Le client lit l'état initial, prépare et exécute une modification autorisée, relit l'état final puis compare les valeurs attendues.</desc>
  <defs>
    <marker id="verify-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#5ec5a5"/></marker>
    <style>
      @keyframes verify-flow { to { stroke-dashoffset:-28; } }
      .verify-link { fill:none;stroke:#5ec5a5;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#verify-arrow);animation:verify-flow 2s linear infinite; }
      .verify-label { fill:#f3f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .verify-small { fill:#bccbe0;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="363" rx="14" fill="#0d1420" stroke="#2c4058"/>
  <rect x="22" y="83" width="165" height="73" rx="10" fill="#282440" stroke="#b1a1f0" stroke-width="1.5"/>
  <text x="104" y="111" class="verify-label">Lecture initiale</text><text x="104" y="133" class="verify-small">état connu</text>
  <rect x="207" y="83" width="165" height="73" rx="10" fill="#193246" stroke="#63bce6" stroke-width="1.5"/>
  <text x="289" y="111" class="verify-label">Préconditions</text><text x="289" y="133" class="verify-small">état et accès</text>
  <rect x="392" y="83" width="165" height="73" rx="10" fill="#292b3e" stroke="#8fa4ca" stroke-width="1.5"/>
  <text x="474" y="111" class="verify-label">Plan</text><text x="474" y="133" class="verify-small">changement limité</text>
  <rect x="577" y="83" width="165" height="73" rx="10" fill="#19352f" stroke="#62c7a4" stroke-width="1.5"/>
  <text x="659" y="111" class="verify-label">Application</text><text x="659" y="133" class="verify-small">opération autorisée</text>
  <rect x="762" y="83" width="155" height="73" rx="10" fill="#362b1d" stroke="#e4b35d" stroke-width="1.5"/>
  <text x="839" y="111" class="verify-label">Lecture finale</text><text x="839" y="133" class="verify-small">état observé</text>
  <path class="verify-link" d="M187 119 H202"/><path class="verify-link" d="M372 119 H387"/><path class="verify-link" d="M557 119 H572"/><path class="verify-link" d="M742 119 H757"/>
  <path class="verify-link" d="M839 156 V225 H474 V161"/>
  <rect x="286" y="225" width="376" height="61" rx="10" fill="#202b3f" stroke="#8ba4c9" stroke-width="1.5"/>
  <text x="474" y="249" class="verify-label">Validation du résultat</text><text x="474" y="269" class="verify-small">objectif atteint ou échec visible</text>
  <text x="474" y="326" class="verify-small">Une réponse HTTP favorable ne remplace jamais la vérification des données obtenues.</text>
</svg>


# 16. ORGANISER LES COLLECTES SUR PLUSIEURS ÉQUIPEMENTS

Le niveau Débutant utilise souvent un seul équipement. Le niveau Intermédiaire doit pouvoir traiter une petite liste de cibles sans mélanger leurs résultats.

## 16.1. Choisir les cibles depuis l'inventaire

Exemple :

```python
devices = [
    {
        "name": "router-lab-01",
        "host": "192.0.2.10",
        "enabled": True,
    },
    {
        "name": "router-lab-02",
        "host": "192.0.2.11",
        "enabled": True,
    },
    {
        "name": "router-lab-03",
        "host": "192.0.2.12",
        "enabled": False,
    },
]
```

Filtrez les cibles avant d'ouvrir des connexions :

```python
selected_devices = [
    device
    for device in devices
    if device["enabled"]
]
```

Le périmètre doit être clair. Une erreur d'inventaire ne doit pas lancer une requête sur une cible qui n'aurait pas dû être sélectionnée.

## 16.2. Une session HTTP ne doit pas être partagée aveuglément entre threads

Pour des lectures parallèles, il faut choisir une stratégie claire de gestion des sessions. Ne supposez pas automatiquement qu'un seul objet `requests.Session` partagé entre plusieurs threads fournit tous les comportements de concurrence souhaités.

Une stratégie simple consiste à créer une session par worker ou à limiter la concurrence à un environnement dont le comportement est testé.

Il faut également limiter le nombre de requêtes simultanées pour respecter les capacités du serveur et éviter de créer un pic de charge.

## 16.3. Exemple simple de collecte concurrente

L'exemple suivant démontre une organisation en workers. Il utilise une session indépendante par tâche pour ne pas partager l'objet de session.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from restconf_client.client import RestconfClient


def collect_device(device: dict) -> dict:
    username = os.environ["RESTCONF_USERNAME"]
    password = os.environ["RESTCONF_PASSWORD"]

    if not device["enabled"]:
        return {
            "device": device["name"],
            "status": "skipped",
            "data": None,
        }

    try:
        with RestconfClient(
            f"https://{device['host']}",
            username,
            password,
            verify=True,
            timeout=(5, 20),
        ) as client:
            payload, response = client.get_json(
                "ietf-interfaces:interfaces",
                params={
                    "content": "config",
                    "depth": "2",
                },
            )

            return {
                "device": device["name"],
                "status": "success",
                "http_status": response.status_code,
                "data": payload,
            }

    except Exception as exc:
        return {
            "device": device["name"],
            "status": "failed",
            "error_type": type(exc).__name__,
            "data": None,
        }


def collect_batch(
    devices: list[dict],
    max_workers: int = 3,
) -> list[dict]:
    if max_workers < 1:
        raise ValueError("max_workers doit être positif.")

    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
        futures = {
            executor.submit(collect_device, device): device
            for device in devices
        }

        for future in as_completed(futures):
            device = futures[future]

            try:
                results.append(future.result())
            except Exception:
                results.append({
                    "device": device["name"],
                    "status": "worker_failed",
                    "data": None,
                })

    return sorted(
        results,
        key=lambda item: item["device"],
    )
```

Cet exemple est une base de laboratoire, pas un orchestrateur de production. Il utilise un gestionnaire d'erreur générique dans le résultat du worker ; une application plus complète classerait séparément les erreurs TLS, HTTP, timeout, données invalides et validations métier.

## 16.4. Limiter la concurrence

Le nombre de workers doit dépendre :

- du nombre d'équipements ;
- de la capacité des serveurs RESTCONF ;
- des limites de requêtes ;
- du réseau de gestion ;
- du temps de réponse ;
- de la charge provoquée par les ressources ciblées ;
- des règles opérationnelles.

Commencez avec un faible nombre de workers. Augmentez-le progressivement et observez le taux d'échec avant de retenir un réglage durable.

## 16.5. Les collectes et les modifications n'ont pas les mêmes règles

Une collecte indépendante sur plusieurs cibles peut souvent être exécutée en parallèle à concurrence limitée.

Une modification de configuration est différente. Plusieurs changements simultanés peuvent avoir des dépendances ou créer des conflits.

Ne réutilisez pas automatiquement le même modèle de concurrence pour une opération de lecture et une opération de modification.


# 17. TESTER LE CLIENT RESTCONF

Un client réutilisable doit être testable sans connexion à un équipement réel pour la majorité de sa logique.

## 17.1. Tester la validation JSON

`tests/test_validation.py` :

```python
import pytest


def validate_interface_item(item: dict) -> None:
    if not isinstance(item, dict):
        raise ValueError(
            "L'interface doit être un objet JSON."
        )

    required = {"name", "enabled"}

    missing = required - item.keys()

    if missing:
        raise ValueError(
            f"Champs manquants : {sorted(missing)}"
        )

    if not isinstance(item["name"], str):
        raise ValueError(
            "Le nom doit être une chaîne."
        )

    if not isinstance(item["enabled"], bool):
        raise ValueError(
            "enabled doit être un booléen."
        )


def test_valid_interface():
    validate_interface_item({
        "name": "Loopback0",
        "enabled": True,
    })


def test_missing_name_is_rejected():
    with pytest.raises(ValueError):
        validate_interface_item({
            "enabled": True,
        })


def test_string_boolean_is_rejected():
    with pytest.raises(ValueError):
        validate_interface_item({
            "name": "Loopback0",
            "enabled": "true",
        })


def test_non_object_is_rejected():
    with pytest.raises(ValueError):
        validate_interface_item("Loopback0")
```

Cette fonction illustre un contrat applicatif restreint. Elle peut être placée dans le module `validation.py` et réutilisée par l'application.

## 17.2. Tester une requête sans réseau

`unittest.mock` permet de simuler les réponses HTTP.

```python
from unittest.mock import Mock, patch

from restconf_client.client import RestconfClient


def test_get_json_uses_restconf_media_type():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.headers = {
        "Content-Type": "application/yang-data+json"
    }
    fake_response.json.return_value = {
        "ietf-interfaces:interfaces": {
            "interface": []
        }
    }

    with RestconfClient(
        "https://router-lab.example",
        "api-reader",
        "dummy-password",
    ) as client:

        with patch.object(
            client.session,
            "request",
            return_value=fake_response,
        ) as request_mock:

            data, response = client.get_json(
                "ietf-interfaces:interfaces"
            )

    assert response.status_code == 200

    assert "ietf-interfaces:interfaces" in data

    assert request_mock.call_args.args[0] == "GET"

    headers = request_mock.call_args.kwargs["headers"]

    # Les en-têtes RESTCONF par défaut sont stockés dans Session.
    # Le test peut aussi examiner client.session.headers lorsqu'il
    # s'agit de vérifier le comportement complet des en-têtes.
    assert headers is None or isinstance(headers, dict)
```

Le test utilise un mot de passe factice et une réponse simulée. Il ne se connecte à aucun équipement.

Pour une suite de tests plus complète, il faut vérifier également :

- la construction de l'URL ;
- les paramètres envoyés ;
- les délais ;
- la vérification TLS ;
- le traitement des réponses HTTP ;
- les statuts inattendus ;
- les réponses vides ;
- les corps JSON invalides ;
- la fermeture de la session.

## 17.3. Tester les erreurs HTTP

Le client doit échouer proprement lorsqu'une réponse inattendue arrive.

Vous pouvez remplacer `session.request` par une réponse simulée avec un statut `403`, puis vérifier que `RestconfHttpError` est levée avec le code attendu.

Le test ne doit pas dépendre du texte d'erreur exact envoyé par tous les constructeurs.

## 17.4. Tester sans divulguer de secret

Utilisez des valeurs fictives dans les tests et examinez les logs produits.

Assurez-vous que les objets d'erreur ne contiennent pas le mot de passe et que les journaux ne sérialisent pas les en-têtes d'authentification.

## 17.5. Exécuter les tests

```bash
python -m pytest -q
```

Les tests unitaires valident la logique applicative. Il faut également des tests d'intégration dans un laboratoire autorisé pour vérifier les modèles, les ressources et les opérations réellement prises en charge.


# 18. RELIER RESTCONF ET NETCONF

RESTCONF et NETCONF sont différents, mais leurs concepts peuvent être reliés.

Les deux protocoles peuvent manipuler des données décrites par YANG. Ils n'exposent pas nécessairement exactement les mêmes capacités sur un équipement.

## 18.1. Comprendre les différences pratiques

| Sujet | RESTCONF | NETCONF |
|---|---|---|
| Transport courant | HTTPS | SSH |
| Format des messages | HTTP avec JSON ou XML | RPC XML |
| Accès aux ressources | URI RESTCONF | Opérations RPC et filtres |
| Modification partielle | PATCH, mécanismes pris en charge | `edit-config` et opérations associées |
| Capacités | Découverte des fonctions RESTCONF | Échange des capacités NETCONF |
| Datastores | Ressources RESTCONF prévues par les extensions prises en charge | Datastores accessibles selon les capacités |
| Contrôle de modification | ETag et préconditions lorsqu'elles sont prises en charge | Verrous, datastores et mécanismes NETCONF selon les capacités |
| Erreurs | Codes HTTP et détails RESTCONF | Réponses RPC et `rpc-error` |

Cette comparaison n'indique pas qu'un protocole est toujours meilleur que l'autre. Il faut analyser l'opération et les capacités disponibles.

## 18.2. Exemple de mapping conceptuel

Une lecture de configuration peut se faire par une ressource RESTCONF et par une opération NETCONF adaptée.

Une modification peut être réalisée par une méthode HTTP RESTCONF ou par `edit-config` sur NETCONF.

Mais le détail de la requête et le contrôle disponible dépendent :

- du datastore ciblé ;
- de la version des modèles ;
- des capacités serveur ;
- des permissions ;
- du mécanisme de validation supporté.

## 18.3. Quand envisager NETCONF ?

NETCONF peut être intéressant lorsqu'une plateforme expose des mécanismes de session, de datastores, de verrouillage ou de validation qui répondent mieux au besoin.

Il faut toutefois vérifier la prise en charge de ces capacités : leur présence ne doit jamais être supposée uniquement parce que NETCONF est disponible.

## 18.4. Quand RESTCONF est-il plus pratique ?

RESTCONF peut être adapté lorsque l'application travaille déjà avec HTTP, a besoin d'une API web et peut exploiter les ressources et encodages exposés.

Il est également pratique dans de nombreux environnements d'automatisation Python grâce aux bibliothèques HTTP usuelles.

Le choix doit être fondé sur les besoins réels et la compatibilité des équipements.


# 19. LABORATOIRES PROGRESSIFS

Tous les laboratoires s'appuient sur les composants développés précédemment. Conservez la même structure de projet et améliorez-la au fil des exercices.

## Laboratoire 1 — Transformer la requête Débutant en client réutilisable

**Objectif :** déplacer les paramètres et le transport dans un module de client.

Étapes :

1. créer la structure du projet ;
2. construire `RestconfClient` ;
3. centraliser la session HTTP ;
4. configurer les délais ;
5. forcer HTTPS dans la validation de l'URL ;
6. assurer la fermeture de session ;
7. réécrire le script de lecture avec le client ;
8. tester l'erreur TLS et le timeout.

**Critères d'acceptation :**

- aucune URL complète n'est répétée partout ;
- les identifiants sont séparés du code ;
- les délais sont explicites ;
- une erreur de communication ne devient pas un résultat vide ;
- les connexions sont fermées proprement.

## Laboratoire 2 — Construire des chemins et clés

**Objectif :** gérer plusieurs ressources.

Étapes :

1. écrire une fonction de construction de chemin d'interface ;
2. encoder les valeurs de clé ;
3. séparer chemin et paramètres de requête ;
4. tester un nom avec espace ;
5. tester une valeur vide ;
6. vérifier l'URI finale avant la requête.

**Critère d'acceptation :** l'application ne transforme pas les séparateurs du chemin en données et ne confond pas des valeurs de clé avec la syntaxe de la ressource.

## Laboratoire 3 — Réduire la taille des réponses

**Objectif :** utiliser correctement les paramètres RESTCONF.

Étapes :

1. lire une ressource complète ;
2. mesurer la taille du corps ;
3. ajouter `content=config` ;
4. expérimenter `depth` ;
5. essayer `fields` si le serveur le prend en charge ;
6. comparer les champs reçus ;
7. vérifier la présence des champs obligatoires.

**Livrable :** un petit tableau indiquant les paramètres, leur effet observé et les champs nécessaires à votre traitement.

## Laboratoire 4 — Découvrir les modèles YANG

**Objectif :** éviter de coder des hypothèses sur les ressources.

Étapes :

1. identifier la méthode de découverte disponible ;
2. lire la YANG Library si elle est exposée ;
3. identifier les modules et révisions nécessaires ;
4. vérifier si la ressource de gestion est disponible ;
5. documenter les modèles compatibles ;
6. créer un contrôle de prérequis avant l'exécution.

**Critère d'acceptation :** si un module obligatoire est absent ou incompatible, le programme s'arrête avant la modification.

## Laboratoire 5 — Construire un validateur JSON

**Objectif :** distinguer une réponse HTTP réussie d'une donnée conforme.

Étapes :

1. choisir une ressource ;
2. définir les champs indispensables ;
3. vérifier les types ;
4. tester une réponse normale ;
5. tester un champ manquant ;
6. tester un type invalide ;
7. générer un statut de validation intelligible.

**Critère d'acceptation :** aucun JSON valide mais incomplet ne doit être considéré automatiquement comme conforme.

## Laboratoire 6 — Préparer une modification partielle

**Objectif :** comprendre le cycle de modification sans appliquer immédiatement sur un équipement réel.

Étapes :

1. choisir une ressource de laboratoire modifiable ;
2. lire l'état initial ;
3. définir la valeur attendue ;
4. construire le chemin exact ;
5. construire un corps conforme au modèle ;
6. vérifier les droits du compte ;
7. présenter le plan ;
8. examiner la méthode de modification requise.

**Critère d'acceptation :** le programme peut présenter la ressource ciblée, les champs modifiés et les validations prévues avant toute opération.

## Laboratoire 7 — Mettre en œuvre un PATCH contrôlé

**Objectif :** modifier une donnée non critique, uniquement dans un laboratoire autorisé.

Étapes :

1. sauvegarder l'état initial ;
2. lire l'ETag si disponible ;
3. créer le plan d'opération ;
4. vérifier l'autorisation ;
5. appliquer un PATCH ciblé ;
6. analyser le statut retourné ;
7. relire la ressource ;
8. comparer la valeur observée à l'objectif ;
9. produire un rapport.

**Critères d'acceptation :**

- le client ne considère pas la réponse HTTP comme preuve finale ;
- les erreurs de conflit sont distinguées ;
- l'état final est vérifié ;
- aucune reprise automatique aveugle n'est effectuée.

## Laboratoire 8 — Simuler un conflit d'ETag

**Objectif :** comprendre les modifications concurrentes.

Étapes :

1. lire une ressource et son ETag ;
2. simuler ou effectuer, dans le laboratoire, une modification autorisée par un autre client ;
3. tenter une modification avec l'ancien ETag ;
4. examiner le résultat ;
5. relire la ressource ;
6. décider si un nouveau changement est toujours justifié.

**Critère d'acceptation :** le programme ne remplace pas automatiquement l'ETag et ne renvoie pas la même modification sans revalidation.

## Laboratoire 9 — Collecter plusieurs équipements

**Objectif :** construire une collecte multi-équipements à concurrence bornée.

Étapes :

1. charger un inventaire ;
2. filtrer les cibles autorisées ;
3. établir une session indépendante par worker ;
4. limiter le nombre de workers ;
5. classer les résultats par cible ;
6. simuler une cible indisponible ;
7. vérifier que les autres résultats restent disponibles ;
8. produire les statistiques du lot.

**Critère d'acceptation :** les erreurs d'une cible ne suppriment pas les résultats des autres.

## Laboratoire 10 — Produire un rapport auditable

**Objectif :** construire le premier outil complet du niveau Intermédiaire.

Le rapport doit inclure :

- identifiant d'exécution ;
- cible ;
- ressource lue ;
- méthode ;
- statut HTTP ;
- temps de réponse ;
- statut de validation ;
- champs essentiels ;
- catégorie d'erreur ;
- statut final ;
- métadonnées nécessaires à l'audit.

N'ajoutez pas de secrets ni de données sensibles inutiles.


# 20. PROJET FINAL : RESTCONF INVENTORY AUDITOR

## 20.1. Mission

Construire un programme Python réutilisable nommé `RESTCONF Inventory Auditor`.

Il devra interroger plusieurs équipements de laboratoire, récupérer une sélection de ressources, vérifier les modèles et les champs attendus, puis produire un rapport JSON.

Une extension facultative pourra réaliser une modification non critique sur une ressource de laboratoire après validation et approbation.

## 20.2. Arborescence attendue

```text
restconf-inventory-auditor/
├── README.md
├── requirements.txt
├── inventory/
│   └── devices.yaml
├── src/
│   └── restconf_client/
│       ├── client.py
│       ├── errors.py
│       ├── validation.py
│       ├── discovery.py
│       ├── inventory.py
│       └── reporting.py
├── tests/
│   ├── test_client.py
│   ├── test_validation.py
│   └── test_inventory.py
└── reports/
```

## 20.3. Exigences fonctionnelles

Le programme doit :

- charger l'inventaire ;
- sélectionner seulement les cibles activées et autorisées ;
- construire les chemins RESTCONF ;
- utiliser HTTPS et une validation TLS adaptée ;
- charger les identifiants de manière sécurisée ;
- utiliser une session HTTP réutilisable ;
- fixer des délais explicites ;
- utiliser les paramètres RESTCONF nécessaires ;
- découvrir les modèles pertinents lorsque possible ;
- contrôler les structures JSON reçues ;
- gérer les erreurs HTTP et de transport ;
- effectuer les lectures indépendantes ;
- limiter la concurrence ;
- produire un résultat par équipement ;
- enregistrer un rapport JSON ;
- ne pas enregistrer de secrets ;
- distinguer succès HTTP et succès métier.

## 20.4. Exigences pour la modification facultative

Si la fonction de modification est ajoutée, elle doit en plus :

- être limitée à un environnement autorisé ;
- traiter uniquement une ressource documentée ;
- valider le corps selon le modèle ;
- lire l'état initial ;
- montrer un plan avant application ;
- appliquer seulement la méthode appropriée ;
- utiliser des préconditions lorsque pertinentes et prises en charge ;
- ne jamais relancer aveuglément une opération ambiguë ;
- vérifier l'état final ;
- arrêter la suite en cas d'échec de validation.

## 20.5. Critères de qualité

Une bonne solution devrait inclure :

- un client réutilisable ;
- une structure modulaire ;
- une gestion d'erreurs cohérente ;
- des tests sans équipement ;
- une validation des données ;
- une configuration externalisée ;
- un rapport lisible ;
- un README expliquant l'installation et les prérequis ;
- des exemples testés sur l'environnement déclaré.

## 20.6. Barème sur 100 points

| Domaine | Points |
|---|---:|
| Client HTTP réutilisable | 15 |
| URI et paramètres RESTCONF | 10 |
| Découverte YANG | 10 |
| Validation JSON | 15 |
| Gestion des erreurs | 15 |
| Sécurité et secrets | 10 |
| Collecte multi-équipements | 10 |
| Tests automatisés | 5 |
| Rapport et documentation | 10 |
| **Total** | **100** |

Un bon score ne compense pas une faille majeure. L'utilisation d'un secret en clair, la désactivation systématique de TLS ou une modification exécutée sans contrôle de périmètre doivent empêcher l'acceptation du projet.


# 21. DÉPANNAGE INTERMÉDIAIRE

## 21.1. Le certificat TLS est refusé

Ne désactivez pas la vérification.

Vérifiez :

- l'identité du serveur ;
- le nom utilisé dans l'URL ;
- la chaîne de certification ;
- la date de validité ;
- la CA de confiance ;
- les éventuelles particularités du laboratoire.

Une erreur TLS est un problème à expliquer, pas un obstacle à contourner systématiquement.

## 21.2. `fields` semble ignoré ou renvoie une erreur

Vérifiez :

- si la ressource autorise ce paramètre ;
- si la capacité est annoncée ;
- la syntaxe de l'expression ;
- les noms de champs ;
- les relations parent-enfant dans le modèle.

N'appliquez pas la grammaire d'un parseur de filtre d'une autre API au paramètre `fields` de RESTCONF.

## 21.3. La réponse a un statut HTTP réussi mais le corps est incomplet

Vérifiez les paramètres `depth`, `content` et `fields`. Assurez-vous que le programme n'a pas demandé une vue réduite des données.

Puis vérifiez si les champs absents sont réellement exposés par le serveur et accessibles au compte courant.

## 21.4. `PUT` entraîne la disparition de champs

Un remplacement de ressource n'a pas la même sémantique qu'une fusion partielle.

Relisez le modèle et le corps envoyé. Si une opération de remplacement est requise, fournissez une représentation correcte de la ressource ciblée. Si seuls quelques champs doivent évoluer, examinez si PATCH est approprié.

Ne réparez pas automatiquement la configuration en réenvoyant un gros objet tant que l'état réel n'est pas connu.

## 21.5. `PATCH` échoue sur un type YANG

Vérifiez le type du champ et son encodage JSON.

Exemples d'erreurs possibles :

- chaîne utilisée à la place d'un booléen ;
- nombre encodé incorrectement ;
- nom de module incorrect ;
- champ absent du modèle ;
- valeur hors plage ;
- contrainte de liste non respectée.

La correction doit se baser sur le schéma et la réponse d'erreur, pas sur une série d'essais aléatoires.

## 21.6. Une réponse `204` provoque une erreur JSON

Une réponse `204 No Content` ne contient pas de corps de réponse.

Ne tentez pas de décoder systématiquement toutes les réponses en JSON. Adaptez le traitement au statut HTTP et à l'opération effectuée.

## 21.7. Le chemin semble valide mais la ressource est absente

Vérifiez le module, la clé, l'encodage et le modèle de l'équipement.

Une URI syntaxiquement correcte ne prouve pas que la ressource existe. Elle peut être absente, non prise en charge ou inaccessible dans le contexte d'exécution.

## 21.8. Le même client fonctionne sur une machine mais pas sur une autre

Comparez :

- l'environnement Python ;
- la version des dépendances ;
- les certificats ;
- la résolution DNS ;
- les règles réseau ;
- les variables d'environnement ;
- la méthode d'authentification ;
- les versions de l'équipement.

La reproductibilité facilite le diagnostic de ce type de problème.

## 21.9. Les collectes parallèles échouent par intermittence

Réduisez le nombre de workers. Observez les délais, les ressources ciblées et les éventuelles limites imposées par le serveur.

Ne réessayez pas toutes les requêtes simultanément après une série d'échecs. Une rafale de reprises peut aggraver une surcharge.

## 21.10. L'ETag produit un conflit

Relisez la ressource. L'état peut avoir été modifié par un autre client.

Comparez la version actuelle à l'objectif et déterminez si le changement demeure nécessaire. Un ETag constitue une information de concurrence, pas une erreur à ignorer.


# 22. EXERCICES ET CRITÈRES D'ÉVALUATION

Répondez avec des exemples de votre client.

1. Pourquoi utiliser une session Requests réutilisable ?
2. Quelle est la différence entre un chemin RESTCONF et un paramètre de requête ?
3. Pourquoi les valeurs de clés doivent-elles être encodées correctement ?
4. Que change le paramètre `content` ?
5. Quelle est la fonction du paramètre `depth` ?
6. Pourquoi `fields` ne doit-il pas être utilisé sans vérifier sa syntaxe et sa prise en charge ?
7. À quoi sert une YANG Library ?
8. Pourquoi la révision du module YANG est-elle importante ?
9. Pourquoi un `200 OK` ne prouve-t-il pas la conformité métier ?
10. Quelle est la différence entre `PATCH` et `PUT` ?
11. Dans quel cas `POST` peut-il être utilisé dans RESTCONF ?
12. Quel est le rôle de YANG Patch ?
13. Comment `ETag` et `If-Match` peuvent-ils prévenir certains conflits ?
14. Que devez-vous faire lorsque la précondition n'est plus satisfaite ?
15. Pourquoi ne faut-il pas relancer automatiquement une modification après un timeout ambigu ?
16. Comment distinguer un échec de transport d'une erreur HTTP ?
17. Pourquoi la session Requests ne doit-elle pas être partagée aveuglément entre plusieurs threads ?
18. Comment vérifier qu'un corps JSON respecte les attentes de l'application ?
19. Pourquoi doit-on relire l'état après une modification ?
20. Comment RESTCONF et NETCONF peuvent-ils coexister dans une architecture d'automatisation ?

## Grille d'auto-évaluation

**Bases à renforcer :** vous savez envoyer une requête mais vous ne savez pas expliquer le modèle, les paramètres, les erreurs ou les autorisations.

**Intermédiaire en construction :** vous disposez d'un client réutilisable, contrôlez les réponses, savez filtrer les données et testez vos fonctions.

**Intermédiaire solide :** vous découvrez les modèles, gérez les ressources de manière ciblée, contrôlez les erreurs et mettez en œuvre des lectures multi-équipements.

**Prêt pour le niveau Expert :** vous savez tester les opérations sur les équipements réels, gérer les préconditions et les conflits, préserver les preuves et expliquer les risques avant une modification.


# 23. GLOSSAIRE

**API** — Interface permettant à une application de communiquer avec un système.

**ETag** — Identifiant opaque de version ou de représentation retourné par le serveur selon les règles applicables.

**HTTP** — Protocole de communication utilisé par RESTCONF.

**HTTPS** — HTTP protégé par TLS.

**If-Match** — En-tête HTTP permettant de soumettre une requête à une condition sur l'ETag.

**JSON** — Format de données structuré en objets, tableaux et valeurs.

**NETCONF** — Protocole de gestion réseau utilisant des opérations RPC et des messages XML.

**NMDA** — *Network Management Datastore Architecture*, architecture définissant les concepts de datastores de gestion.

**PATCH** — Méthode HTTP de modification partielle dont la sémantique dépend du mécanisme de patch utilisé.

**POST** — Méthode HTTP pouvant servir à créer une ressource ou à invoquer certaines opérations RESTCONF.

**PUT** — Méthode HTTP utilisée pour remplacer une représentation de ressource conformément à la sémantique RESTCONF.

**RESTCONF** — Protocole de gestion model-driven fondé sur HTTP.

**Requests** — Bibliothèque Python permettant d'effectuer des requêtes HTTP.

**RPC** — *Remote Procedure Call*, opération demandée à un serveur par un client.

**TLS** — Protocole qui protège les communications et permet l'authentification du serveur selon la configuration adoptée.

**URI** — Identifiant d'une ressource.

**YANG** — Langage de modélisation des données de gestion réseau.

**YANG Library** — Mécanisme permettant de découvrir les modules et schémas YANG utilisés par le serveur.

**YANG Patch** — Format et mécanisme permettant de décrire des opérations de modification à l'aide des données YANG.


# 24. RÉFÉRENCES OFFICIELLES

Les références suivantes doivent être consultées lors de l'adaptation des exemples à une version particulière d'un produit.

## RESTCONF et HTTP

- **RFC 8040 — RESTCONF Protocol**  
  https://www.rfc-editor.org/rfc/rfc8040.html

- **RFC 8527 — RESTCONF Extensions to Support NMDA**  
  https://www.rfc-editor.org/rfc/rfc8527.html

- **RFC 5789 — PATCH Method for HTTP**  
  https://www.rfc-editor.org/rfc/rfc5789.html

- **Documentation Requests pour Python**  
  https://requests.readthedocs.io/

## YANG et schémas

- **RFC 7950 — YANG 1.1 Data Modeling Language**  
  https://www.rfc-editor.org/rfc/rfc7950.html

- **RFC 7951 — JSON Encoding of Data Modeled with YANG**  
  https://www.rfc-editor.org/rfc/rfc7951.html

- **RFC 8525 — YANG Library**  
  https://www.rfc-editor.org/rfc/rfc8525.html

- **RFC 8342 — Network Management Datastore Architecture**  
  https://www.rfc-editor.org/rfc/rfc8342.html

- **RFC 8341 — Network Configuration Access Control Model**  
  https://www.rfc-editor.org/rfc/rfc8341.html

## Modifications

- **RFC 8072 — YANG Patch Media Type**  
  https://www.rfc-editor.org/rfc/rfc8072.html

## NETCONF

- **RFC 6241 — Network Configuration Protocol**  
  https://www.rfc-editor.org/rfc/rfc6241.html

- **RFC 6242 — NETCONF over SSH**  
  https://www.rfc-editor.org/rfc/rfc6242.html


# CONCLUSION — DE LA REQUÊTE ISOLÉE AU CLIENT RÉUTILISABLE

Au niveau Débutant, vous avez appris à interroger une ressource RESTCONF, à comprendre le format JSON, à reconnaître les bases de YANG et à établir une première session NETCONF.

Dans ce niveau Intermédiaire, vous avez transformé ces notions en une architecture de client plus structurée.

Vous avez appris à centraliser les paramètres, construire les URI, sélectionner les données, découvrir les modèles, valider les réponses, classer les erreurs et tester le client sans dépendre systématiquement d'un équipement réel.

Vous avez également abordé les opérations de modification, la distinction entre PATCH et PUT, le mécanisme YANG Patch, ainsi que les ETags permettant de détecter certains conflits de modification.

La suite ne consiste pas simplement à envoyer davantage de requêtes. Elle consiste à mieux maîtriser leurs conséquences.

Avant de modifier une ressource, il faut comprendre son modèle, son état initial, ses permissions et la portée de l'opération. Après la modification, il faut vérifier que l'état obtenu correspond à l'objectif.

**Règle finale du niveau Intermédiaire :** un client RESTCONF fiable ne se limite pas à effectuer une requête valide. Il sait choisir la ressource, demander les données nécessaires, contrôler le résultat, détecter les conflits et expliquer les échecs sans masquer les problèmes.

Le niveau Expert s'appuiera sur ce client pour aborder la validation avancée, les workflows de changement industrialisés, l'audit, l'observabilité et l'automatisation à l'échelle du réseau.