# RESTCONF et NETCONF — Niveau Expert
## Architecture, sécurité, transactions, observabilité et automatisation réseau à grande échelle

**Fichier :** `restconf-expert.md`  
**Parcours :** Débutant → Intermédiaire → Expert  
**Domaine :** automatisation réseau model-driven, RESTCONF, NETCONF, YANG, HTTP, Python et NetDevOps  
**Public :** ingénieurs réseau, architectes d'automatisation, ingénieurs NetDevOps, administrateurs infrastructure  
**Objectif :** construire une plateforme d'automatisation capable de découvrir les capacités des équipements, de comprendre leurs modèles, d'effectuer des opérations contrôlées, de détecter les conflits, de vérifier les changements et de produire des preuves d'exécution exploitables.


# AVANT-PROPOS — LE NIVEAU EXPERT PROLONGE LE PARCOURS

Ce document termine le parcours RESTCONF et NETCONF commencé dans `restconf-debutant.md` puis poursuivi dans `restconf-intermediaire.md`.

Le niveau Débutant vous a appris à comprendre les protocoles, à découvrir les bases de YANG, à effectuer des lectures RESTCONF et NETCONF et à interpréter les premières réponses.

Le niveau Intermédiaire vous a appris à créer un client Python réutilisable, à construire des URI, à sélectionner les données, à découvrir les modèles, à valider les réponses, à gérer les erreurs et à préparer des modifications conditionnelles.

Le niveau Expert reprend ces composants. Il ne les remplace pas par des scripts indépendants : il les transforme en une architecture cohérente et exploitable.

## La progression cumulative

| Niveau | Compétence centrale | Résultat attendu |
|---|---|---|
| Débutant | Comprendre les protocoles et les données | Lire des ressources et interpréter XML, JSON et YANG |
| Intermédiaire | Construire un client réutilisable | Filtrer, valider, gérer les erreurs et préparer des modifications |
| Expert | Industrialiser l'automatisation | Découvrir dynamiquement les capacités, contrôler les changements, tester les contrats, tracer les opérations et exploiter plusieurs équipements de façon maîtrisée |

Le client `RestconfClient` du niveau précédent constitue donc un point de départ, pas un exemple à jeter.

Nous allons conserver sa séparation entre configuration, transport, erreurs et validation, puis compléter ses capacités avec :

- une découverte dynamique du serveur ;
- une gestion correcte des chemins `/restconf/data` et `/restconf/ds` ;
- une lecture plus approfondie de la YANG Library ;
- une sélection des datastores fondée sur NMDA ;
- un cache contrôlé des métadonnées et des réponses ;
- des opérations conditionnelles fondées sur les ETags ;
- une gestion rigoureuse des conflits ;
- des modifications groupées et validées ;
- une stratégie de concurrence limitée ;
- une politique de reprise adaptée à chaque catégorie d'opération ;
- des contrôles de sécurité ;
- des tests unitaires, contractuels et d'intégration ;
- des rapports d'audit structurés ;
- un mécanisme d'arrêt et une procédure de récupération documentée.

> **Principe central :** un système expert ne se contente pas d'exécuter une opération RESTCONF. Il sait pourquoi cette opération est possible, sur quelle ressource elle s'applique, quelles sont ses préconditions, ce qu'elle peut modifier et comment vérifier son résultat.

## Références normatives utilisées

Les références principales du cours sont :

- RFC 8040 — RESTCONF Protocol ;
- RFC 7950 — YANG 1.1 ;
- RFC 7951 — JSON Encoding of Data Modeled with YANG ;
- RFC 8072 — YANG Patch ;
- RFC 8341 — Network Configuration Access Control Model ;
- RFC 8342 — Network Management Datastore Architecture ;
- RFC 8525 — YANG Library ;
- RFC 8527 — RESTCONF Extensions to Support NMDA ;
- RFC 8639, RFC 8641 et RFC 8650 — notifications et abonnements de données ;
- RFC 10035 — extension récente de la YANG Library.

Les RFC définissent des mécanismes standards ; ils ne garantissent pas qu'un équipement particulier implémente toutes les fonctionnalités optionnelles. La compatibilité doit toujours être vérifiée sur le serveur cible.


# SOMMAIRE

1. Objectifs et modèle mental Expert
2. Architecture d'une plateforme d'automatisation RESTCONF
3. Établir les contrats du client
4. Concevoir un client RESTCONF centralisé
5. Découverte des capacités du serveur
6. YANG Library et dépendances entre modules
7. Datastores NMDA et RESTCONF
8. Sélection avancée des données
9. Validation sémantique et normalisation
10. ETag, If-Match et détection des conflits
11. Modifications contrôlées et YANG Patch
12. Idempotence, reprises et cohérence
13. Sécurité avancée et contrôle des accès
14. Exécution multi-équipements et limitation de débit
15. Notifications, flux d'événements et télémétrie
16. Tests unitaires, contractuels et d'intégration
17. Observabilité, audit et rapports
18. Intégration continue et exploitation
19. Laboratoires progressifs
20. Projet final : RESTCONF Automation Controller
21. Dépannage Expert
22. Évaluation de sortie
23. Glossaire
24. Références officielles


# 1. OBJECTIFS ET MODÈLE MENTAL EXPERT

## 1.1. Un protocole ne constitue pas une architecture

Dans les niveaux précédents, une requête RESTCONF pouvait se résumer à :

```python
response = session.get(url, timeout=20)
data = response.json()
```

Cette opération suffit à montrer le fonctionnement général de HTTP.

Mais une plateforme d'automatisation doit répondre à beaucoup d'autres questions :

- L'URL correspond-elle bien au serveur autorisé ?
- L'équipement expose-t-il le modèle attendu ?
- La requête vise-t-elle le bon datastore ?
- Le compte a-t-il le droit de lire ou de modifier la ressource ?
- Le type de réponse correspond-il à celui demandé ?
- Les données sont-elles cohérentes avec le schéma ?
- Une autre application a-t-elle modifié la ressource depuis sa dernière lecture ?
- La commande d'édition est-elle sûre à répéter ?
- Si la réponse n'arrive pas, comment déterminer si le changement a été appliqué ?
- Comment savoir si l'état final correspond à l'objectif ?
- Comment produire une preuve de ce qui s'est passé ?

Ces questions définissent l'architecture autour du protocole.

RESTCONF demeure le mécanisme de communication. Les garanties d'exploitation viennent des composants complémentaires.

## 1.2. Le contrat d'une opération

Chaque opération automatisée doit définir un contrat.

### Préconditions

Le client doit connaître l'identité de la cible, son modèle, la ressource ciblée, les permissions requises et les éventuelles conditions de fonctionnement.

### Action

Le client doit envoyer une requête construite à partir de paramètres validés, avec une méthode HTTP appropriée, un corps conforme au modèle et des délais maîtrisés.

### Résultat technique

Le client doit vérifier le statut HTTP, la représentation reçue et les éventuelles métadonnées pertinentes.

### Résultat métier

L'application doit vérifier que les données correspondent à l'objectif attendu.

### Récupération

Si l'état obtenu est incertain ou incorrect, le client doit suivre une procédure prévue au lieu d'improviser une nouvelle modification.

Cette structure s'applique aussi bien à une simple lecture qu'à un changement de configuration critique.

## 1.3. Quatre catégories de réussite

Une plateforme avancée peut distinguer ces résultats :

| Catégorie | Question | Exemple |
|---|---|---|
| Transport | La communication est-elle possible ? | TLS établi, serveur joignable |
| Protocole | La requête a-t-elle été acceptée ? | HTTP 200, réponse RESTCONF valide |
| Contrat de données | Les données ont-elles la forme attendue ? | Champs présents, types conformes |
| Résultat métier | L'objectif est-il atteint ? | État opérationnel conforme à la politique |

Une opération peut réussir au niveau HTTP tout en échouant au niveau métier. Le rapport doit conserver cette distinction.

## 1.4. Le rôle de NETCONF dans ce niveau

RESTCONF demeure l'axe principal du cours.

NETCONF est réintroduit lorsqu'il apporte un mécanisme utile pour comprendre les datastores, les capacités, les verrous, les opérations de configuration et les pratiques de contrôle d'état.

Il ne s'agit pas d'affirmer que NETCONF est toujours supérieur à RESTCONF. La bonne architecture choisit l'interface qui fournit les capacités nécessaires sur les équipements réellement exploités.


# 2. ARCHITECTURE D'UNE PLATEFORME D'AUTOMATISATION RESTCONF

## 2.1. Organiser les responsabilités

Une plateforme experte peut être organisée en couches.

**Couche Inventaire**

Identifie les appareils, leur environnement, leur modèle de compatibilité et leur périmètre autorisé.

**Couche Découverte**

Identifie les capacités RESTCONF, les datastores et les modules YANG pertinents.

**Couche Transport**

Gère les sessions HTTP, TLS, les délais, l'authentification et les connexions.

**Couche Données**

Construit les URI, sélectionne les ressources et valide les représentations XML ou JSON.

**Couche Opérations**

Définit les lectures, les modifications autorisées et les critères de validation.

**Couche Orchestration**

Contrôle l'ordre des opérations, le nombre de requêtes simultanées, les délais et l'arrêt en cas d'incident.

**Couche Audit**

Enregistre les résultats, les erreurs, les durées et les éléments permettant de reconstruire l'exécution.

## 2.2. Schéma SVG animé — architecture complète

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-labelledby="expert-arch-title expert-arch-desc" style="max-width:100%;height:auto">
  <title id="expert-arch-title">Architecture d'une plateforme RESTCONF Expert</title>
  <desc id="expert-arch-desc">L'inventaire et la découverte alimentent un orchestrateur qui utilise le client RESTCONF pour agir sur les ressources. Les réponses passent par la validation, les rapports et l'audit.</desc>
  <defs>
    <marker id="expert-arch-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#60c5e7"/></marker>
    <style>
      @keyframes expert-arch-flow { to { stroke-dashoffset:-30; } }
      @keyframes expert-arch-glow { 0%,100% { stroke-opacity:.65; } 50% { stroke-opacity:1; } }
      .expert-arch-link { fill:none;stroke:#60c5e7;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#expert-arch-arrow);animation:expert-arch-flow 2s linear infinite; }
      .expert-arch-node { fill:#172740;stroke:#60c5e7;stroke-width:1.5;animation:expert-arch-glow 3s ease-in-out infinite; }
      .expert-arch-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .expert-arch-small { fill:#b6c7df;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="388" rx="14" fill="#0c1421" stroke="#2b3f58"/>
  <text x="480" y="32" class="expert-arch-label" font-size="17">La couche réseau est entourée de contrôles explicites</text>
  <rect class="expert-arch-node" x="24" y="60" width="175" height="62" rx="9"/>
  <text x="111" y="84" class="expert-arch-label">Inventaire</text><text x="111" y="103" class="expert-arch-small">cibles autorisées</text>
  <rect class="expert-arch-node" x="224" y="60" width="175" height="62" rx="9"/>
  <text x="311" y="84" class="expert-arch-label">Découverte YANG</text><text x="311" y="103" class="expert-arch-small">capacités + datastores</text>
  <rect class="expert-arch-node" x="424" y="60" width="175" height="62" rx="9"/>
  <text x="511" y="84" class="expert-arch-label">Politique</text><text x="511" y="103" class="expert-arch-small">préconditions + plan</text>
  <rect class="expert-arch-node" x="624" y="60" width="150" height="62" rx="9"/>
  <text x="699" y="84" class="expert-arch-label">Orchestrateur</text><text x="699" y="103" class="expert-arch-small">limites + statuts</text>
  <rect class="expert-arch-node" x="799" y="60" width="137" height="62" rx="9"/>
  <text x="867" y="84" class="expert-arch-label">Client HTTP</text><text x="867" y="103" class="expert-arch-small">TLS + requêtes</text>
  <path class="expert-arch-link" d="M199 91 H219"/><path class="expert-arch-link" d="M399 91 H419"/><path class="expert-arch-link" d="M599 91 H619"/><path class="expert-arch-link" d="M774 91 H794"/>
  <path class="expert-arch-link" d="M867 122 V157"/>
  <rect x="740" y="159" width="196" height="66" rx="9" fill="#15352e" stroke="#67c9a8" stroke-width="1.6"/>
  <text x="838" y="184" class="expert-arch-label">Serveur RESTCONF</text><text x="838" y="204" class="expert-arch-small">modèles et ressources</text>
  <path d="M740 193 H665 V157 H511 V122" fill="none" stroke="#e5b365" stroke-width="2.2" stroke-dasharray="6 7" style="animation:expert-arch-flow 2.4s linear infinite"/>
  <rect x="230" y="160" width="395" height="66" rx="9" fill="#212b40" stroke="#8ba8cd" stroke-width="1.5"/>
  <text x="427" y="184" class="expert-arch-label">Validation et preuves</text><text x="427" y="204" class="expert-arch-small">contrat de données + résultat métier</text>
  <path class="expert-arch-link" d="M740 210 H630"/>
  <rect x="230" y="260" width="395" height="63" rx="9" fill="#30271e" stroke="#dfb05f" stroke-width="1.5"/>
  <text x="427" y="285" class="expert-arch-label">Observabilité et audit</text><text x="427" y="305" class="expert-arch-small">journaux, compte rendu, état d'exécution</text>
  <path class="expert-arch-link" d="M427 226 V255"/>
  <text x="480" y="358" class="expert-arch-small">Chaque requête doit être explicable, mesurable et contrôlable.</text>
</svg>

## 2.3. Les responsabilités ne doivent pas se mélanger

Le client HTTP ne doit pas décider si un changement est autorisé.

L'inventaire ne doit pas envoyer de requêtes.

La fonction de validation ne doit pas modifier la ressource.

Le module de rapport ne doit pas réinterpréter les données comme si elles étaient déjà validées.

Une couche claire facilite les tests indépendants et limite les effets secondaires.

## 2.4. Les contrats entre modules

Une opération doit recevoir un objet de données déjà validé et retourner un résultat structuré.

Exemple :

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class OperationResult:
    device: str
    operation: str
    status: str
    http_status: int | None
    duration_ms: int
    data: Any = None
    error_category: str | None = None
    correlation_id: str | None = None
```

Ce modèle ne contient ni mot de passe ni objet de session HTTP.

Il doit distinguer l'identité de la cible, l'opération exécutée, la durée, le statut et les données pertinentes.


# 3. ÉTABLIR LES CONTRATS DU CLIENT

## 3.1. Une opération doit définir ses préconditions

Avant une lecture :

- le serveur doit être identifié ;
- l'URL doit correspondre à une cible autorisée ;
- la ressource doit être plausible au regard du modèle ;
- le compte doit disposer de droits de lecture ;
- le format de réponse doit être accepté.

Avant une modification, ajoutez :

- une permission de changement explicitement accordée ;
- un modèle compatible ;
- une ressource et un datastore identifiés ;
- des paramètres validés ;
- un plan approuvé lorsque la politique l'exige ;
- un mécanisme de contrôle des modifications concurrentes si disponible ;
- des critères de validation postérieurs ;
- une stratégie de récupération.

## 3.2. Contrat technique contre contrat métier

Le contrat technique indique par exemple qu'une réponse `GET` est reçue en JSON.

Le contrat métier indique que la réponse contient une interface connue, que certains champs sont présents et que les valeurs respectent les règles de l'opération.

Le client doit pouvoir échouer à l'un sans confondre les deux.

## 3.3. Structure de statut recommandée

```json
{
  "run_id": "RUN-EXPERT-001",
  "device": "router-lab-01",
  "operation": "read_interfaces",
  "transport_status": "success",
  "protocol_status": "success",
  "validation_status": "success",
  "business_status": "success",
  "http_status": 200,
  "duration_ms": 240
}
```

Les valeurs sont illustratives.

Cette structure sert à séparer les étapes. Si la réponse JSON est valide mais que la structure attendue n'existe pas, `validation_status` doit le signaler sans effacer le succès du transport.


# 4. CONCEVOIR UN CLIENT RESTCONF CENTRALISÉ

Le client créé au niveau Intermédiaire utilisait principalement la racine `/restconf/data`.

Au niveau Expert, il doit distinguer les ressources de données historiques et les ressources de datastore NMDA sous `/restconf/ds`.

Cette distinction est essentielle : le chemin d'un datastore n'est pas un simple chemin de ressource ajouté après `/restconf/data`.

## 4.1. Arborescence du module

```text
src/restconf_platform/
├── __init__.py
├── config.py
├── client.py
├── errors.py
├── discovery.py
├── yang_library.py
├── validation.py
├── operations.py
├── change_control.py
├── retry.py
├── concurrency.py
├── telemetry.py
└── reporting.py
```

## 4.2. Paramètres de connexion contrôlés

`src/restconf_platform/config.py` :

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RestconfConfig:
    origin: str
    username: str
    password: str
    verify_tls: bool | str = True
    connect_timeout: float = 5.0
    read_timeout: float = 25.0
    ca_bundle: str | None = None

    def __post_init__(self) -> None:
        if not self.origin.startswith("https://"):
            raise ValueError("L'origine doit utiliser HTTPS.")

        if self.origin.endswith("/"):
            object.__setattr__(
                self,
                "origin",
                self.origin.rstrip("/"),
            )

        if self.connect_timeout <= 0 or self.read_timeout <= 0:
            raise ValueError("Les délais doivent être positifs.")

        if self.ca_bundle:
            ca_path = Path(self.ca_bundle)

            if not ca_path.is_file():
                raise ValueError("Le fichier CA configuré est absent.")
```

L'origine représente le schéma et l'hôte, éventuellement un port spécifique. Le chemin `/restconf` sera ajouté par le client.

La configuration n'est pas un coffre de secrets : le mot de passe doit être fourni par un mécanisme approprié à l'environnement.

## 4.3. Erreurs applicatives

`src/restconf_platform/errors.py` :

```python
class RestconfError(RuntimeError):
    """Classe de base des erreurs RESTCONF."""


class RestconfTransportError(RestconfError):
    """Erreur TLS, connexion ou délai dépassé."""


class RestconfHttpError(RestconfError):
    """Réponse HTTP non conforme au contrat."""

    def __init__(
        self,
        status_code: int,
        method: str,
        path: str,
    ):
        self.status_code = status_code
        self.method = method
        self.path = path

        super().__init__(
            f"{method} {path}: statut HTTP {status_code}"
        )


class RestconfDecodeError(RestconfError):
    """Réponse impossible à décoder selon le contrat."""


class RestconfValidationError(RestconfError):
    """Données reçues non conformes au contrat métier."""


class RestconfCapabilityError(RestconfError):
    """Fonction ou capacité requise non disponible."""


class RestconfConflictError(RestconfError):
    """Conflit de modification ou de précondition."""


class RestconfPolicyError(RestconfError):
    """Opération refusée par la politique locale."""
```

Le client peut convertir les erreurs spécifiques de Requests en `RestconfTransportError` et conserver un code HTTP exploitable dans `RestconfHttpError`.

Il ne doit pas ajouter le mot de passe, les en-têtes d'authentification ou le corps complet des réponses aux messages d'erreur par défaut.

## 4.4. Client prenant en charge plusieurs racines RESTCONF

`src/restconf_platform/client.py` :

```python
from __future__ import annotations

from urllib.parse import urlsplit
import requests

from .config import RestconfConfig
from .errors import (
    RestconfDecodeError,
    RestconfHttpError,
    RestconfTransportError,
)


JSON_MEDIA = "application/yang-data+json"
XML_MEDIA = "application/yang-data+xml"


class RestconfClient:
    def __init__(self, config: RestconfConfig):
        parsed = urlsplit(config.origin)

        if parsed.scheme.lower() != "https":
            raise ValueError("HTTPS est obligatoire.")

        if not parsed.hostname:
            raise ValueError("Hôte absent de l'origine.")

        if parsed.username or parsed.password:
            raise ValueError(
                "Les identifiants ne doivent pas être placés dans l'URL."
            )

        if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ValueError(
                "origin doit contenir uniquement schéma, hôte et port."
            )

        self.config = config
        self.restconf_root = f"{config.origin}/restconf"
        self.data_root = f"{self.restconf_root}/data"
        self.ds_root = f"{self.restconf_root}/ds"

        self.session = requests.Session()
        self.session.auth = (
            config.username,
            config.password,
        )

        self.session.headers.update({
            "Accept": JSON_MEDIA,
        })

        self.verify_tls = (
            config.ca_bundle
            if config.ca_bundle
            else config.verify_tls
        )

        self.timeout = (
            config.connect_timeout,
            config.read_timeout,
        )

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "RestconfClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    @staticmethod
    def _validate_relative_path(path: str) -> str:
        path = path.lstrip("/")

        if not path:
            return ""

        if "://" in path or path.startswith("//"):
            raise ValueError("Une ressource relative est attendue.")

        if any(segment in {".", ".."} for segment in path.split("/")):
            raise ValueError("Segment de chemin interdit.")

        if "?" in path or "#" in path:
            raise ValueError(
                "Les paramètres et fragments doivent être séparés du chemin."
            )

        return path

    def build_data_url(self, resource: str = "") -> str:
        safe_path = self._validate_relative_path(resource)

        if safe_path:
            return f"{self.data_root}/{safe_path}"

        return self.data_root

    def build_ds_url(
        self,
        datastore: str,
        resource: str = "",
    ) -> str:
        safe_datastore = self._validate_relative_path(datastore)
        safe_path = self._validate_relative_path(resource)

        if "/" in safe_datastore or not safe_datastore:
            raise ValueError("Identité de datastore incorrecte.")

        url = f"{self.ds_root}/{safe_datastore}"

        if safe_path:
            url = f"{url}/{safe_path}"

        return url

    def request_url(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json_body: dict | list | None = None,
        headers: dict | None = None,
        allowed_statuses: set[int] | None = None,
    ) -> requests.Response:
        parsed = urlsplit(url)

        if parsed.scheme != "https":
            raise ValueError("La requête doit utiliser HTTPS.")

        if parsed.netloc != urlsplit(self.config.origin).netloc:
            raise ValueError(
                "La destination ne correspond pas à l'hôte autorisé."
            )

        if not (
            parsed.path == "/restconf"
            or parsed.path.startswith("/restconf/")
        ):
            raise ValueError("Chemin hors de la racine RESTCONF.")

        method = method.upper()

        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_tls,
                allow_redirects=False,
            )

        except requests.exceptions.SSLError as exc:
            raise RestconfTransportError(
                "Échec de validation TLS."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise RestconfTransportError(
                "Délai RESTCONF dépassé."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise RestconfTransportError(
                f"Erreur de communication : {type(exc).__name__}"
            ) from exc

        if allowed_statuses is None:
            allowed_statuses = {200, 201, 202, 204}

        if response.status_code not in allowed_statuses:
            raise RestconfHttpError(
                response.status_code,
                method,
                parsed.path,
            )

        return response

    def get_json_data(
        self,
        resource: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
        allowed_statuses: set[int] | None = None,
    ) -> tuple[dict | list, requests.Response]:
        url = self.build_data_url(resource)

        response = self.request_url(
            "GET",
            url,
            params=params,
            headers=headers,
            allowed_statuses=allowed_statuses or {200},
        )

        if response.status_code == 304:
            return {}, response

        media_type = (
            response.headers.get("Content-Type", "")
            .split(";", 1)[0]
            .strip()
            .lower()
        )

        if media_type != JSON_MEDIA:
            raise RestconfDecodeError(
                f"Type de contenu inattendu : {media_type!r}"
            )

        try:
            result = response.json()
        except ValueError as exc:
            raise RestconfDecodeError(
                "Corps de réponse JSON invalide."
            ) from exc

        if not isinstance(result, (dict, list)):
            raise RestconfDecodeError(
                "La racine JSON n'est ni un objet ni une liste."
            )

        return result, response

    def get_json_datastore(
        self,
        datastore: str,
        resource: str = "",
        *,
        params: dict | None = None,
        headers: dict | None = None,
        allowed_statuses: set[int] | None = None,
    ) -> tuple[dict | list, requests.Response]:
        url = self.build_ds_url(datastore, resource)

        response = self.request_url(
            "GET",
            url,
            params=params,
            headers=headers,
            allowed_statuses=allowed_statuses or {200},
        )

        if response.status_code == 304:
            return {}, response

        media_type = (
            response.headers.get("Content-Type", "")
            .split(";", 1)[0]
            .strip()
            .lower()
        )

        if media_type != JSON_MEDIA:
            raise RestconfDecodeError(
                f"Type de contenu inattendu : {media_type!r}"
            )

        try:
            result = response.json()
        except ValueError as exc:
            raise RestconfDecodeError(
                "Corps de réponse JSON invalide."
            ) from exc

        if not isinstance(result, (dict, list)):
            raise RestconfDecodeError(
                "La racine JSON n'est ni un objet ni une liste."
            )

        return result, response
```

### À vérifier avant d'utiliser ce client

Ce code fournit une structure de travail, pas une certification de compatibilité avec tous les serveurs.

Il faut également :

- tester les réponses vides des méthodes non-GET ;
- définir les types de contenu acceptés par opération ;
- adapter la gestion des corps XML si cette représentation est nécessaire ;
- gérer les codes `304`, `204` et les autres statuts selon la méthode ;
- imposer une politique d'authentification appropriée ;
- examiner les options de certificat et les permissions réelles ;
- vérifier la prise en charge des chemins de datastore NMDA ;
- compléter la validation des chemins selon les modèles exploités.

La séparation des méthodes `build_data_url()` et `build_ds_url()` évite de confondre les deux espaces de ressources.

## 4.5. Pourquoi la validation de destination importe

Une application experte peut recevoir un inventaire provenant de fichiers, d'une interface utilisateur ou d'un système de gestion.

Elle ne doit pas accepter aveuglément une URL qui permettrait d'envoyer des identifiants vers un hôte inattendu.

Pour une plateforme de production, ajoutez une politique d'hôtes autorisés fondée sur l'inventaire approuvé, la résolution réseau et les restrictions d'environnement.


# 5. DÉCOUVERTE DES CAPACITÉS DU SERVEUR

## 5.1. Pourquoi la découverte est une étape obligatoire

Au niveau Débutant, une URI pouvait être connue à l'avance.

Au niveau Expert, l'application doit vérifier ce que le serveur expose réellement.

Un équipement peut posséder :

- des modèles YANG différents ;
- des révisions distinctes ;
- des options RESTCONF absentes ;
- des datastores différents ;
- certaines extensions constructeur ;
- des règles d'accès spécifiques.

Le fait qu'une autre machine prenne en charge une fonctionnalité ne garantit pas que la cible la prend en charge.

## 5.2. La ressource racine RESTCONF

Le RFC 8040 définit une ressource racine RESTCONF, accessible à l'URI `/restconf`.

Elle peut fournir des informations sur l'API et les chemins d'accès exposés. Les détails de découverte et les ressources de surveillance peuvent varier selon la génération d'implémentation.

Exemple avec le client :

```python
response = client.request_url(
    "GET",
    client.restconf_root,
    allowed_statuses={200},
    headers={
        "Accept": "application/yang-data+json",
    },
)
```

Ce premier appel vise la racine `/restconf`, pas `/restconf/data`.

Traitez cette ressource selon son propre contrat de contenu.

## 5.3. Découvrir les capacités RESTCONF

Le RFC 8040 définit un mécanisme permettant d'examiner les capacités du serveur, notamment via les ressources de surveillance RESTCONF.

Une ressource de capacités historiquement utilisée est :

```text
/restconf/data/ietf-restconf-monitoring:restconf-state/capabilities
```

Exemple :

```python
payload, response = client.get_json_data(
    "ietf-restconf-monitoring:restconf-state/capabilities"
)
```

La ressource doit être disponible sur le serveur ciblé. Vérifiez sa prise en charge et la génération de l'interface RESTCONF concernée.

L'application devrait extraire les capacités et les conserver dans un objet interne normalisé.

## 5.4. Construire un modèle de capacités

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RestconfCapabilities:
    supports_fields: bool
    supports_depth: bool
    supports_with_defaults: bool
    supports_yang_patch: bool
    supports_nmda: bool
    capability_uris: tuple[str, ...]
```

Les valeurs sont déduites de la découverte réelle. Elles ne doivent pas être fixées arbitrairement à `True`.

Lorsque le serveur ne fournit pas les informations attendues, utilisez un état explicite tel que « inconnu » ou refusez une opération qui exige cette capacité.

Il ne faut pas transformer automatiquement une capacité non découverte en capacité supportée.

## 5.5. Vérifier les capacités avant d'exécuter

Exemple :

```python
def require_capability(
    capabilities: set[str],
    capability_uri: str,
) -> None:
    if capability_uri not in capabilities:
        raise RuntimeError(
            f"Capacité RESTCONF non disponible : {capability_uri}"
        )
```

Utilisation :

```python
FIELDS_CAPABILITY = (
    "urn:ietf:params:restconf:capability:fields:1.0"
)

require_capability(
    discovered_capabilities,
    FIELDS_CAPABILITY,
)
```

Le nom exact de la variable `discovered_capabilities` dépend de la fonction de découverte que vous implémentez.

La fonction de contrôle doit être appelée avant d'utiliser la fonction facultative.

## 5.6. Les capacités dépendent des ressources

Une capacité générale du serveur ne garantit pas que chaque méthode est autorisée sur chaque ressource.

Le client doit donc vérifier trois éléments :

1. la fonctionnalité existe sur le serveur ;
2. elle est adaptée à l'opération demandée ;
3. la ressource ciblée autorise cette opération et l'identité dispose des permissions nécessaires.


# 6. YANG LIBRARY ET DÉPENDANCES ENTRE MODULES

La YANG Library est l'un des éléments les plus importants pour une application model-driven.

Elle fournit les informations nécessaires pour identifier les modèles pris en charge et leur association avec les schémas et datastores.

## 6.1. L'architecture NMDA et la YANG Library

Selon le RFC 8527, un serveur RESTCONF qui prend en charge NMDA doit exposer le datastore opérationnel et la YANG Library correspondante.

La ressource de données du datastore opérationnel peut être adressée comme suit :

```text
/restconf/ds/ietf-datastores:operational/ietf-yang-library:yang-library
```

Cette URI appartient à l'espace `/restconf/ds`, pas à `/restconf/data`.

Exemple :

```python
payload, response = client.get_json_datastore(
    "ietf-datastores:operational",
    "ietf-yang-library:yang-library",
)
```

Le serveur doit effectivement prendre en charge NMDA et exposer le module de YANG Library correspondant.

Références :
- [RFC 8527 — RESTCONF Extensions to Support NMDA](https://www.rfc-editor.org/rfc/rfc8527.html)
- [RFC 8525 — YANG Library](https://www.rfc-editor.org/rfc/rfc8525.html)

## 6.2. Modéliser l'inventaire des modèles

Une application ne devrait pas manipuler directement une structure YANG Library très complexe à travers tous ses modules.

Il est préférable de convertir la découverte en objets internes.

Exemple pédagogique :

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class YangModuleInfo:
    name: str
    revision: str | None
    namespace: str | None
    conformance_type: str | None


@dataclass(frozen=True)
class YangSchemaInfo:
    content_id: str | None
    modules: tuple[YangModuleInfo, ...]
```

Une fonction de parsing devra construire ces objets à partir du document réel reçu. Elle devra prendre en compte le schéma et la version de YANG Library présents sur l'équipement.

Il serait incorrect d'implémenter un parseur universel qui suppose uniquement un seul format de YANG Library ou qui ignore les révisions de modules.

## 6.3. Suivre le `content-id`

Le RFC 8525 définit un identifiant de contenu de YANG Library qui change lorsque les informations de la bibliothèque changent.

Il peut être utilisé par un client pour savoir si son cache de métadonnées demeure pertinent.

Une stratégie raisonnable :

1. lire la YANG Library ;
2. enregistrer le `content-id` ;
3. construire le schéma local utile ;
4. comparer ultérieurement l'identifiant ;
5. recalculer ou invalider le cache si l'identifiant a changé.

Le client ne doit pas inventer lui-même un `content-id` et le traiter comme une preuve de version.

## 6.4. Attention au RFC 10035

**Le RFC 10035, publié en août 2026, met à jour le RFC 8525 en ajoutant la liste `augmented-by`.**

Cette extension facilite la découverte des dépendances inverses entre modules YANG : autrement dit, elle permet d'identifier les modules qui étendent un module donné via des mécanismes d'augmentation.

Cela améliore la capacité du client à reconstituer les dépendances nécessaires pour comprendre un schéma, notamment dans les environnements où les modules standard sont complétés par des modèles supplémentaires.

Référence :
https://www.rfc-editor.org/rfc/rfc10035.html

Le support de cette extension doit être vérifié dans les modèles et les implémentations réellement utilisées. Son absence sur un serveur ne signifie pas automatiquement que la YANG Library entière est inutilisable.

## 6.5. Pourquoi les dépendances inverses sont importantes

Prenons deux modèles :

- `ietf-interfaces`, qui décrit des informations liées aux interfaces ;
- `ietf-ip`, qui peut ajouter des nœuds liés à IP.

Le premier modèle peut être nécessaire pour identifier l'interface, tandis que le second peut être nécessaire pour interpréter certaines données relatives aux adresses ou au forwarding.

Une application qui télécharge uniquement le modèle principal sans tenir compte des augmentations peut manquer une partie de la sémantique des données.

Les relations de dépendance aident à identifier quels schémas complémentaires sont nécessaires.

## 6.6. Sécurité de la découverte

Les modèles disponibles peuvent révéler des informations sur les logiciels, les fonctionnalités et les particularités d'un équipement.

Le contrôle d'accès à la YANG Library et aux métadonnées doit donc être pensé en termes de sécurité. Le fait qu'une donnée soit en lecture seule ne signifie pas nécessairement qu'elle est sans sensibilité.

Le RFC 8341 décrit le modèle de contrôle d'accès pour NETCONF et RESTCONF :
https://www.rfc-editor.org/rfc/rfc8341.html

## 6.7. Schéma SVG animé — découverte des modèles

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="yanglib-title yanglib-desc" style="max-width:100%;height:auto">
  <title id="yanglib-title">Découverte dynamique des modèles YANG</title>
  <desc id="yanglib-desc">Le client lit la YANG Library, identifie les modules, révisions, datastores et dépendances, puis crée un cache de schéma contrôlé.</desc>
  <defs>
    <marker id="yanglib-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#b59cf4"/></marker>
    <style>
      @keyframes yanglib-flow { to { stroke-dashoffset:-26; } }
      .yanglib-link { fill:none;stroke:#b59cf4;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#yanglib-arrow);animation:yanglib-flow 2s linear infinite; }
      .yanglib-text { fill:#f3f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .yanglib-small { fill:#bdc9df;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="353" rx="14" fill="#0d1421" stroke="#30415a"/>
  <rect x="26" y="72" width="205" height="76" rx="10" fill="#292440" stroke="#b39ff3" stroke-width="1.5"/>
  <text x="128" y="100" class="yanglib-text">Client Expert</text><text x="128" y="122" class="yanglib-small">découverte + cache</text>
  <rect x="290" y="72" width="350" height="76" rx="10" fill="#183246" stroke="#61bee7" stroke-width="1.5"/>
  <text x="465" y="100" class="yanglib-text">YANG Library</text><text x="465" y="122" class="yanglib-small">modules, révisions, schémas, content-id</text>
  <rect x="699" y="72" width="215" height="76" rx="10" fill="#17352f" stroke="#66c8a7" stroke-width="1.5"/>
  <text x="806" y="100" class="yanglib-text">Modèles dérivés</text><text x="806" y="122" class="yanglib-small">dépendances YANG</text>
  <path class="yanglib-link" d="M231 110 H285"/><path class="yanglib-link" d="M640 110 H694"/>
  <path class="yanglib-link" d="M806 148 V196 H465 V153"/>
  <rect x="245" y="199" width="440" height="65" rx="10" fill="#1c2d40" stroke="#83a5cd" stroke-width="1.5"/>
  <text x="465" y="224" class="yanglib-text">Validation des capacités</text><text x="465" y="245" class="yanglib-small">incompatibilité détectée avant l'opération</text>
  <rect x="245" y="292" width="440" height="38" rx="9" fill="#30281e" stroke="#e3b260" stroke-width="1.5"/>
  <text x="465" y="316" class="yanglib-text">Cache versionné par content-id</text>
  <path class="yanglib-link" d="M465 264 V287"/>
</svg>


# 7. DATASTORES NMDA ET RESTCONF

## 7.1. Pourquoi les datastores sont importants

Le datastore définit l'ensemble de données auquel l'opération s'applique.

Dans un système de gestion réseau, il faut notamment distinguer :

- la configuration courante ;
- la configuration prévue ;
- l'état opérationnel ;
- d'éventuelles configurations candidates ou de démarrage selon les capacités de la plateforme.

Le [RFC 8342 — Network Management Datastore Architecture](https://www.rfc-editor.org/rfc/rfc8342.html) formalise ces notions.

## 7.2. Les principaux datastores NMDA

### `running`

La configuration qui est actuellement dans le datastore de configuration en cours.

Elle n'est pas toujours identique à l'ensemble de la configuration effectivement appliquée au comportement du système.

### `intended`

La configuration destinée à être utilisée par le système après les transformations de configuration prévues.

Ce datastore est en lecture seule dans l'architecture NMDA telle que définie par le RFC 8342.

### `operational`

L'état opérationnel de l'équipement : configuration appliquée et données d'état du système selon les règles du modèle.

Un serveur conforme à NMDA expose le datastore opérationnel par RESTCONF.

### `candidate` et `startup`

Ces concepts existent dans l'architecture de gestion et dans certaines capacités NETCONF, mais ils ne doivent pas être considérés comme des ressources RESTCONF NMDA automatiquement disponibles sur tous les serveurs.

Il faut vérifier les datastores effectivement pris en charge.

## 7.3. Les chemins des datastores NMDA

Le RFC 8527 définit la structure des URI :

```text
/restconf/ds/<datastore>
```

Exemples :

```text
/restconf/ds/ietf-datastores:operational
/restconf/ds/ietf-datastores:running
/restconf/ds/ietf-datastores:intended
```

Un serveur NMDA doit exposer le datastore opérationnel. Les autres ressources de datastore peuvent dépendre des capacités de l'implémentation.

## 7.4. Un chemin ne doit pas être placé sous la mauvaise racine

La ressource :

```text
/restconf/data/ietf-interfaces:interfaces
```

appartient à l'espace de données.

La ressource :

```text
/restconf/ds/ietf-datastores:operational/ietf-interfaces:interfaces
```

appartient à l'espace du datastore opérationnel défini par le RFC 8527.

Ces chemins ne sont pas interchangeables simplement parce qu'ils peuvent contenir des nœuds YANG du même modèle.

## 7.5. Comparer l'état opérationnel avec la configuration

Supposons que la configuration demande qu'une interface soit activée. Il reste important de connaître l'état opérationnel réel de cette interface.

Les requêtes doivent viser les données adaptées à la question métier :

- la configuration courante ;
- la configuration destinée à être appliquée ;
- les valeurs opérationnelles ;
- les statistiques ou états en lecture seule.

La différence peut expliquer pourquoi un équipement possède un paramètre de configuration particulier sans produire encore le comportement attendu.

## 7.6. Origine des données opérationnelles

Le RFC 8527 introduit le paramètre `with-origin` dans les requêtes GET vers le datastore opérationnel ou des datastores dérivés de celui-ci, lorsque cette capacité est prise en charge.

Ce paramètre permet de demander les annotations indiquant l'origine des valeurs opérationnelles.

Exemple conceptuel :

```python
payload, response = client.get_json_datastore(
    "ietf-datastores:operational",
    "ietf-interfaces:interfaces",
    params={
        "with-origin": "true",
    },
)
```

Le client doit vérifier la capacité annoncée et la conformité de l'implémentation avant de dépendre de ce mécanisme.

L'origine peut aider à distinguer les valeurs issues de la configuration prévue, des valeurs par défaut, de la configuration apprise ou d'autres mécanismes selon le modèle applicable.

## 7.7. Les valeurs par défaut

Les données YANG peuvent posséder des valeurs par défaut.

La façon dont ces valeurs sont rapportées dépend du protocole, du datastore et du paramètre `with-defaults`, dans les limites de prise en charge de l'implémentation.

Des modes tels que `report-all`, `trim`, `explicit` et `report-all-tagged` influencent la manière de présenter les valeurs par défaut.

Ces distinctions sont importantes lorsqu'un programme compare la configuration attendue avec l'état reçu. L'absence d'un champ et la présence explicite d'une valeur par défaut ne doivent pas être confondues sans tenir compte du modèle et des règles de représentation.

## 7.8. Schéma SVG animé — architecture des datastores

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 365" role="img" aria-labelledby="ds-title ds-desc" style="max-width:100%;height:auto">
  <title id="ds-title">Datastores de l'architecture NMDA</title>
  <desc id="ds-desc">Le client accède séparément aux datastores running, intended et operational. Le datastore opérationnel associe configuration appliquée et état système.</desc>
  <defs>
    <marker id="ds-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#65c5a4"/></marker>
    <style>
      @keyframes ds-flow { to { stroke-dashoffset:-28; } }
      .ds-link { fill:none;stroke:#65c5a4;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#ds-arrow);animation:ds-flow 2s linear infinite; }
      .ds-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .ds-small { fill:#becadd;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="363" rx="14" fill="#0c1421" stroke="#2d4057"/>
  <rect x="25" y="65" width="225" height="78" rx="10" fill="#282440" stroke="#b1a1ef" stroke-width="1.5"/>
  <text x="137" y="91" class="ds-label">running</text><text x="137" y="113" class="ds-small">configuration courante</text><text x="137" y="129" class="ds-small">ressource NMDA si exposée</text>
  <rect x="358" y="65" width="225" height="78" rx="10" fill="#193245" stroke="#62bce7" stroke-width="1.5"/>
  <text x="470" y="91" class="ds-label">intended</text><text x="470" y="113" class="ds-small">configuration prévue</text><text x="470" y="129" class="ds-small">lecture seule dans NMDA</text>
  <rect x="690" y="65" width="225" height="78" rx="10" fill="#17352e" stroke="#65c5a4" stroke-width="1.5"/>
  <text x="802" y="91" class="ds-label">operational</text><text x="802" y="113" class="ds-small">configuration appliquée</text><text x="802" y="129" class="ds-small">+ état système</text>
  <path class="ds-link" d="M250 104 H353"/><path class="ds-link" d="M583 104 H685"/>
  <rect x="180" y="218" width="580" height="65" rx="10" fill="#1d2b40" stroke="#89a5cc" stroke-width="1.5"/>
  <text x="470" y="243" class="ds-label">Contrôle métier</text><text x="470" y="264" class="ds-small">quelle donnée répond exactement à la question posée ?</text>
  <path class="ds-link" d="M802 143 V184 H470 V213"/>
  <text x="470" y="324" class="ds-small">Ne confondez jamais intention, configuration courante et état observé.</text>
</svg>


# 8. SÉLECTION AVANCÉE DES DONNÉES

## 8.1. Pourquoi la sélection doit être explicite

Une réponse volumineuse augmente les coûts de transfert, de parsing et de stockage. Elle augmente aussi la quantité d'informations sensibles que le client doit traiter.

Au niveau Expert, la requête doit être conçue en fonction du contrat de l'opération.

Il ne faut pas appliquer un filtre uniquement parce qu'il semble réduire la réponse : le programme doit encore recevoir tous les champs dont il a besoin pour valider le résultat.

## 8.2. Paramètres utiles

Le RFC 8040 définit notamment les paramètres de requête suivants selon le type de ressource et la méthode :

- `content` ;
- `depth` ;
- `fields` ;
- `with-defaults` ;
- ainsi que des paramètres qui ont des usages spécifiques aux flux d'événements ou aux listes ordonnées.

Les paramètres optionnels et leur comportement doivent être vérifiés dans les capacités de la version du serveur.

## 8.3. `content`

Le paramètre `content` permet de sélectionner la catégorie de données demandée pour les ressources concernées.

Les valeurs usuelles sont :

- `config` ;
- `nonconfig` ;
- `all`.

Exemple :

```python
params = {
    "content": "config",
}
```

Ne supposez pas que ce paramètre fonctionne de façon identique sur toutes les ressources ou tous les datastores. La compatibilité et la sémantique doivent être vérifiées dans le protocole et l'implémentation.

## 8.4. `depth`

Ce paramètre limite la profondeur des données retournées dans les cas où il est applicable.

Exemple :

```python
params = {
    "depth": "3",
}
```

La valeur acceptée peut être un nombre défini par le protocole ou la chaîne `unbounded`, dans les limites applicables.

La limitation de profondeur ne doit pas supprimer un champ critique sans que l'application s'en aperçoive.

## 8.5. `fields`

Le paramètre `fields` demande un sous-ensemble de nœuds dans une ressource.

Exemple conceptuel :

```python
params = {
    "fields": "interface(name;description;enabled)",
}
```

La grammaire de l'expression doit respecter les noms de nœuds, les chemins et la syntaxe de RESTCONF.

Le client doit vérifier la capacité `fields:1.0` si l'implémentation utilise les mécanismes de découverte de capacités du RFC 8040.

## 8.6. `with-defaults`

Ce paramètre contrôle la présentation des valeurs par défaut dans les ressources concernées.

Il peut avoir un impact sur :

- la comparaison de configuration ;
- la détection des changements ;
- l'interprétation d'un champ absent ;
- les différences entre configurations explicites et implicites.

Une application doit choisir un mode adapté à son objectif et documenter ce choix. Deux collectes effectuées avec des modes différents ne doivent pas être comparées sans tenir compte de la sémantique des valeurs rapportées.

## 8.7. Les filtres d'événements

Le paramètre `filter` de RESTCONF a un usage spécifique pour certains flux d'événements. Il ne doit pas être confondu avec une expression de filtrage arbitraire applicable aux ressources de données.

Une extension constructeur peut proposer d'autres mécanismes, mais ceux-ci doivent être identifiés et validés comme des extensions.

## 8.8. Ne pas supposer l'existence d'une pagination

Le protocole RESTCONF de base ne doit pas être traité comme s'il possédait automatiquement un mécanisme universel de pagination à la manière de certaines API web.

Si un serveur fournit une extension de pagination, l'application doit la détecter et suivre son contrat. Sinon, elle doit choisir une ressource plus ciblée, utiliser les paramètres de sélection supportés ou adopter une autre stratégie de collecte.

## 8.9. Schéma SVG animé — requête optimisée

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="select-title select-desc" style="max-width:100%;height:auto">
  <title id="select-title">Optimisation d'une requête RESTCONF</title>
  <desc id="select-desc">Le client connaît les champs requis et applique des paramètres de sélection. La réponse réduite reste ensuite soumise à la validation sémantique.</desc>
  <defs>
    <marker id="select-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#64c6a4"/></marker>
    <style>
      @keyframes select-flow { to { stroke-dashoffset:-25; } }
      .select-link { fill:none;stroke:#64c6a4;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#select-arrow);animation:select-flow 2s linear infinite; }
      .select-label { fill:#f3f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .select-small { fill:#bcc9dd;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="338" rx="14" fill="#0d1420" stroke="#2f4158"/>
  <rect x="24" y="67" width="230" height="110" rx="10" fill="#29243e" stroke="#b2a1ee" stroke-width="1.5"/>
  <text x="139" y="93" class="select-label">Contrat de données</text><text x="139" y="116" class="select-small">champs requis</text><text x="139" y="135" class="select-small">types attendus</text><text x="139" y="154" class="select-small">règles métier</text>
  <rect x="352" y="67" width="230" height="110" rx="10" fill="#193346" stroke="#63bee6" stroke-width="1.5"/>
  <text x="467" y="93" class="select-label">Paramètres RESTCONF</text><text x="467" y="116" class="select-small">content</text><text x="467" y="135" class="select-small">depth</text><text x="467" y="154" class="select-small">fields</text>
  <rect x="680" y="67" width="230" height="110" rx="10" fill="#17352f" stroke="#65c7a6" stroke-width="1.5"/>
  <text x="795" y="93" class="select-label">Réponse ciblée</text><text x="795" y="116" class="select-small">transfert réduit</text><text x="795" y="135" class="select-small">champs nécessaires</text><text x="795" y="154" class="select-small">validations requises</text>
  <path class="select-link" d="M254 122 H347"/><path class="select-link" d="M582 122 H675"/>
  <path class="select-link" d="M795 177 V225 H467 V182"/>
  <rect x="280" y="225" width="375" height="58" rx="10" fill="#33291e" stroke="#e4b25f" stroke-width="1.5"/>
  <text x="467" y="249" class="select-label">Valider la réponse obtenue</text><text x="467" y="268" class="select-small">une réponse plus petite reste à vérifier</text>
  <text x="467" y="315" class="select-small">L'optimisation ne doit jamais diminuer la fiabilité du contrôle métier.</text>
</svg>


# 9. VALIDATION SÉMANTIQUE ET NORMALISATION

## 9.1. Le parsing n'est pas la validation

Une réponse JSON valide peut ne pas respecter les exigences de l'application.

Exemple :

```json
{
  "ietf-interfaces:interfaces": {
    "interface": [
      {
        "name": "Loopback0",
        "enabled": "true"
      }
    ]
  }
}
```

La syntaxe JSON est correcte, mais si `enabled` est modélisé comme un booléen, la chaîne `"true"` n'est pas interchangeable avec `true`.

Une validation experte doit contrôler les types réels, les champs et les règles attendues.

## 9.2. Contrat de données

Exemple d'objet de sortie normalisé :

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class InterfaceRecord:
    name: str
    enabled: bool
    description: str | None
```

Cette représentation correspond au contrat métier de l'application, pas forcément à la représentation JSON complète du serveur.

Le code d'adaptation doit convertir les données reçues en objets de ce type seulement après validation.

## 9.3. Validation de champs

```python
def parse_interface_item(item: dict) -> InterfaceRecord:
    if not isinstance(item, dict):
        raise ValueError("Une interface doit être un objet JSON.")

    if "name" not in item:
        raise ValueError("Le champ name est absent.")

    if "enabled" not in item:
        raise ValueError("Le champ enabled est absent.")

    if not isinstance(item["name"], str):
        raise ValueError("name doit être une chaîne.")

    if not isinstance(item["enabled"], bool):
        raise ValueError("enabled doit être un booléen.")

    description = item.get("description")

    if description is not None and not isinstance(description, str):
        raise ValueError("description doit être une chaîne.")

    return InterfaceRecord(
        name=item["name"],
        enabled=item["enabled"],
        description=description,
    )
```

Cette fonction est illustrative et doit correspondre à la structure réellement renvoyée par le modèle cible. En particulier, les enveloppes qualifiées par le nom de module et les types présents doivent être traités avant de passer les éléments à ce parseur.

## 9.4. Validation d'un ensemble de résultats

Un contrôle peut inclure :

- unicité des identifiants ;
- champs obligatoires ;
- types de valeurs ;
- présence des éléments attendus ;
- absence d'éléments interdits ;
- cohérence entre plusieurs ressources ;
- valeurs attendues selon l'environnement ;
- détection de valeurs inconnues ou non interprétables.

## 9.5. Ne pas normaliser en supprimant les informations essentielles

Un modèle standard et un modèle constructeur peuvent utiliser des noms et des conventions différents.

La normalisation doit préserver les informations utiles et documenter les transformations.

Ne supprimez pas automatiquement les espaces de noms, les distinctions de configuration et d'état ou les annotations dont votre application dépend.

## 9.6. Contrat versionné

Une architecture avancée peut associer à chaque opération :

```text
operation_id
schema_version
model_names
model_revisions
required_fields
allowed_values
validation_rules
```

Lorsque la YANG Library change, l'application peut déterminer si son contrat est toujours applicable ou si des tests ou adaptations sont nécessaires.

## 9.7. Diff entre données structurées

Il est préférable de comparer des données normalisées plutôt que des corps JSON bruts.

La comparaison devrait :

- ignorer l'ordre des propriétés d'un objet JSON ;
- préserver l'ordre lorsque la sémantique de la liste le demande ;
- différencier l'absence et la valeur explicite ;
- tenir compte des types ;
- exclure les métadonnées volatiles uniquement selon une règle documentée ;
- produire une liste de différences intelligible.

Cette approche réduit les faux positifs et aide à préparer des changements réellement utiles.


# 10. ETAG, IF-MATCH ET DÉTECTION DES CONFLITS

Le RFC 8040 définit des mécanismes permettant de détecter certaines modifications concurrentes par ETag et préconditions HTTP.

## 10.1. Le problème de concurrence

Deux clients lisent la même ressource.

Le premier prépare une modification.

Le second modifie la ressource avant que le premier n'envoie son changement.

Si le premier envoie son plan sans vérifier l'état courant, sa modification peut être appliquée sur une hypothèse devenue obsolète.

Ce problème peut exister même si chacun des clients fonctionne correctement.

## 10.2. Le rôle d'ETag

Un ETag est une valeur opaque produite par le serveur. Elle identifie une représentation ou une version de ressource selon les règles du protocole.

Le client doit la conserver exactement comme elle est retournée. Il ne doit pas calculer un ETag en hachant le JSON et supposer que le serveur acceptera cette valeur.

Le RFC 8040 prévoit notamment un ETag pour la ressource datastore et décrit le comportement des ETags pour les ressources de données.

Référence :
https://www.rfc-editor.org/rfc/rfc8040.html

## 10.3. `If-Match`

Le client peut envoyer :

```http
If-Match: "etag-obtenu-du-serveur"
```

La valeur doit être l'ETag pertinent retourné par le serveur.

Si la précondition n'est plus satisfaite, le serveur peut rejeter l'opération. Ce rejet doit être traité comme un conflit à résoudre et non comme un simple problème à réessayer immédiatement.

## 10.4. Contrôler les modifications concurrentes

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="etag-expert-title etag-expert-desc" style="max-width:100%;height:auto">
  <title id="etag-expert-title">Conflit de modification avec ETag</title>
  <desc id="etag-expert-desc">Le client lit une ressource, un autre acteur la modifie, puis le client tente une modification conditionnelle. La précondition permet de détecter le changement concurrent.</desc>
  <defs>
    <marker id="etag-expert-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#64c4a4"/></marker>
    <style>
      @keyframes etag-expert-flow { to { stroke-dashoffset:-25; } }
      .etag-expert-link { fill:none;stroke:#64c4a4;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#etag-expert-arrow);animation:etag-expert-flow 2s linear infinite; }
      .etag-expert-label { fill:#f3f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .etag-expert-small { fill:#bec9de;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="353" rx="14" fill="#0c1421" stroke="#2d4058"/>
  <rect x="25" y="60" width="220" height="74" rx="10" fill="#282440" stroke="#b2a1f0" stroke-width="1.5"/>
  <text x="135" y="88" class="etag-expert-label">Client A</text><text x="135" y="110" class="etag-expert-small">GET + conservation ETag</text>
  <rect x="360" y="60" width="220" height="74" rx="10" fill="#193245" stroke="#63bee6" stroke-width="1.5"/>
  <text x="470" y="88" class="etag-expert-label">Serveur RESTCONF</text><text x="470" y="110" class="etag-expert-small">version courante</text>
  <rect x="695" y="60" width="220" height="74" rx="10" fill="#17352e" stroke="#65c6a5" stroke-width="1.5"/>
  <text x="805" y="88" class="etag-expert-label">Client B</text><text x="805" y="110" class="etag-expert-small">modification concurrente</text>
  <path class="etag-expert-link" d="M245 82 H355"/><path class="etag-expert-link" d="M355 118 H250"/>
  <path d="M805 134 V177 H470 V138" fill="none" stroke="#e3af5f" stroke-width="2.3" stroke-dasharray="6 7" style="animation:etag-expert-flow 2.2s linear infinite"/>
  <text x="655" y="172" class="etag-expert-small">ETag potentiellement périmé</text>
  <rect x="210" y="212" width="520" height="61" rx="10" fill="#252b3d" stroke="#93a8cb" stroke-width="1.5"/>
  <text x="470" y="237" class="etag-expert-label">PATCH avec If-Match</text><text x="470" y="257" class="etag-expert-small">le serveur vérifie la précondition</text>
  <path class="etag-expert-link" d="M135 134 V242 H205"/>
  <text x="470" y="311" class="etag-expert-label">En cas de conflit : relire, comparer, revalider</text>
  <text x="470" y="332" class="etag-expert-small">Ne pas renouveler l'ETag et rejouer aveuglément la modification.</text>
</svg>

## 10.5. Lecture conditionnelle avec `If-None-Match`

Le mécanisme `If-None-Match` permet également de demander au serveur de ne renvoyer la représentation que si l'ETag ne correspond pas à la valeur fournie.

Exemple :

```python
headers = {
    "If-None-Match": cached_etag,
}
```

Si le serveur répond `304 Not Modified`, le client peut réutiliser son cache sous réserve que celui-ci soit associé à la bonne ressource, au bon contenu et aux bonnes conditions d'accès.

Ne confondez pas une réponse 304 avec un objet JSON vide : la réponse indique que la représentation n'a pas été retransmise parce que la précondition a été satisfaite.

## 10.6. Cache conditionnel

Un cache avancé devrait enregistrer :

- l'identité de l'équipement ;
- l'URI canonique ;
- les paramètres de requête ;
- le format demandé ;
- l'ETag ;
- la date de collecte ;
- les métadonnées de contexte nécessaires.

Une réponse pour `fields=name` ne doit pas être réutilisée comme représentation complète. De même, une ressource du datastore opérationnel ne doit pas être assimilée à la même représentation sous un autre datastore.

## 10.7. ETag et limites de protection

L'ETag aide à détecter certaines modifications concurrentes. Il ne remplace pas :

- l'autorisation ;
- les validations des données ;
- le contrôle de périmètre ;
- la procédure de récupération ;
- la vérification postérieure.

Il ne prouve pas non plus que les changements externes au système de gestion sont impossibles.


# 11. MODIFICATIONS CONTRÔLÉES ET YANG PATCH

## 11.1. Les méthodes HTTP ont des conséquences différentes

| Méthode | Usage | Précaution |
|---|---|---|
| `POST` | Créer une ressource ou invoquer une opération prévue | Vérifier l'emplacement et la sémantique |
| `PUT` | Remplacer une représentation de ressource | Un corps incomplet peut supprimer des nœuds absents |
| `PATCH` | Modifier partiellement une ressource | Vérifier le mécanisme de patch et son type de contenu |
| `DELETE` | Supprimer une ressource | Risque destructif ; périmètre exact obligatoire |

Le choix ne doit pas se fonder uniquement sur le fait que la méthode « semble correspondre » au besoin. La sémantique de RESTCONF et le modèle YANG ciblé déterminent le traitement.

## 11.2. Contrôle préalable au changement

Avant chaque modification, l'application devrait :

1. identifier le serveur et la ressource ;
2. lire l'état actuel ;
3. vérifier les champs et types pertinents ;
4. calculer le plan de changement ;
5. vérifier les autorisations ;
6. présenter le plan ;
7. enregistrer les préconditions et les preuves ;
8. appliquer le changement selon la méthode appropriée ;
9. interpréter la réponse ;
10. relire l'état final ;
11. valider l'objectif métier ;
12. produire le résultat final.

## 11.3. Le *plain patch*

Le RFC 8040 définit un mécanisme *plain patch* qui fusionne la représentation fournie avec la ressource ciblée selon les règles applicables.

Cette méthode peut convenir à une modification partielle simple.

Elle ne signifie pas que n'importe quel corps JSON peut être appliqué n'importe où. Le contenu, les chemins et les types doivent correspondre au modèle réel.

## 11.4. YANG Patch

Le RFC 8072 définit un type de contenu et un mécanisme de patch permettant de décrire des opérations d'édition ordonnées.

Il peut convenir lorsqu'un changement nécessite plusieurs sous-opérations contrôlées.

Le type de contenu associé est :

```http
application/yang-patch+json
```

ou sa représentation XML.

La prise en charge doit être découverte, notamment au moyen des capacités et du comportement `OPTIONS` / `Accept-Patch`.

Référence :
https://www.rfc-editor.org/rfc/rfc8072.html

## 11.5. Atomicité de YANG Patch

Selon le RFC 8072, lorsqu'un serveur prend en charge YANG Patch, si le document complet ne peut pas être appliqué avec succès, aucune partie du patch ne doit être appliquée.

Cette propriété d'atomicité porte sur le patch tel que défini par le protocole.

Elle ne garantit pas que toute chaîne d'opérations distinctes dans une application constitue une seule transaction, ni qu'une conséquence externe au datastore soit automatiquement annulée.

Il faut distinguer :

- l'atomicité d'une requête YANG Patch ;
- la cohérence globale d'un workflow multi-équipements ;
- la récupération d'une modification ;
- la validation d'un service réseau.

## 11.6. Construire le plan indépendamment de l'exécution

Une bonne application doit pouvoir produire un plan sans l'appliquer.

Exemple de représentation interne :

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChangeOperation:
    change_id: str
    device: str
    datastore: str
    resource: str
    method: str
    payload: dict[str, Any]
    expected_fields: dict[str, Any]
```

Cette structure représente l'intention et les résultats attendus. Elle ne doit pas contenir un champ arbitraire `command` ou une URL libre provenant d'un utilisateur non contrôlé.

## 11.7. Ne pas relancer aveuglément un PATCH après un timeout

Si le serveur a appliqué un changement mais que le client n'a pas reçu la réponse, l'état final peut être ambigu.

Le client doit relire l'état et déterminer si :

- l'objectif est déjà atteint ;
- le changement n'a pas été appliqué ;
- l'état est partiellement différent ;
- une intervention est nécessaire.

Cette lecture doit être elle-même protégée par les politiques de sécurité appropriées.

## 11.8. Schéma SVG animé — cycle de changement expert

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" role="img" aria-labelledby="change-exp-title change-exp-desc" style="max-width:100%;height:auto">
  <title id="change-exp-title">Cycle de changement RESTCONF sécurisé</title>
  <desc id="change-exp-desc">Le client découvre les capacités, lit l'état, génère un plan, vérifie l'ETag, applique la modification et valide l'état final.</desc>
  <defs>
    <marker id="change-exp-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#62c7a6"/></marker>
    <style>
      @keyframes change-exp-flow { to { stroke-dashoffset:-27; } }
      .change-exp-link { fill:none;stroke:#62c7a6;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#change-exp-arrow);animation:change-exp-flow 2s linear infinite; }
      .change-exp-label { fill:#f1f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .change-exp-small { fill:#bdc9df;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="368" rx="14" fill="#0d1420" stroke="#2c4058"/>
  <rect x="20" y="65" width="150" height="75" rx="9" fill="#282440" stroke="#b1a0ef" stroke-width="1.5"/>
  <text x="95" y="91" class="change-exp-label">Découverte</text><text x="95" y="113" class="change-exp-small">capacité + modèle</text>
  <rect x="202" y="65" width="150" height="75" rx="9" fill="#193244" stroke="#63bee5" stroke-width="1.5"/>
  <text x="277" y="91" class="change-exp-label">État initial</text><text x="277" y="113" class="change-exp-small">GET + ETag</text>
  <rect x="384" y="65" width="150" height="75" rx="9" fill="#242b3e" stroke="#91a5ca" stroke-width="1.5"/>
  <text x="459" y="91" class="change-exp-label">Plan</text><text x="459" y="113" class="change-exp-small">préconditions</text>
  <rect x="566" y="65" width="150" height="75" rx="9" fill="#34291d" stroke="#e4b261" stroke-width="1.5"/>
  <text x="641" y="91" class="change-exp-label">Application</text><text x="641" y="113" class="change-exp-small">PATCH contrôlé</text>
  <rect x="748" y="65" width="190" height="75" rx="9" fill="#17352e" stroke="#65c8a6" stroke-width="1.5"/>
  <text x="843" y="91" class="change-exp-label">Validation finale</text><text x="843" y="113" class="change-exp-small">état et objectif</text>
  <path class="change-exp-link" d="M170 103 H197"/><path class="change-exp-link" d="M352 103 H379"/><path class="change-exp-link" d="M534 103 H561"/><path class="change-exp-link" d="M716 103 H743"/>
  <path d="M843 142 V211 H641 V144" fill="none" stroke="#e4b261" stroke-width="2.3" stroke-dasharray="6 7" style="animation:change-exp-flow 2.3s linear infinite"/>
  <rect x="375" y="211" width="350" height="59" rx="9" fill="#30251c" stroke="#e4b261" stroke-width="1.5"/>
  <text x="550" y="235" class="change-exp-label">Conflit ou validation négative</text><text x="550" y="254" class="change-exp-small">relecture, arrêt, décision documentée</text>
  <text x="480" y="319" class="change-exp-label">Aucune opération n'est clôturée sans contrôle du résultat.</text>
  <text x="480" y="341" class="change-exp-small">Planifier, autoriser, appliquer, relire et valider sont des étapes distinctes.</text>
</svg>


# 12. IDEMPOTENCE, REPRISES ET COHÉRENCE

## 12.1. Définir l'idempotence

Une opération est idempotente lorsque sa répétition conduit au même état final qu'une seule exécution, sous les hypothèses définies.

La répétabilité d'une requête HTTP et l'idempotence métier sont liées, mais ne doivent pas être confondues de manière simpliste.

Un GET peut être destiné à être réessayé après certains échecs transitoires. Un POST qui crée une ressource peut produire un doublon si l'opération est rejouée après un timeout ambigu.

Un PATCH qui définit une valeur donnée peut sembler répétable, mais il faut toujours vérifier le modèle, les effets et les contraintes.

## 12.2. Tableau de stratégie de reprise

| Opération | Reprise automatique possible ? | Condition |
|---|---|---|
| GET d'une ressource | Souvent | Erreur transitoire identifiée et délai borné |
| Découverte de capacités | Souvent | Requête sans effet secondaire et limites respectées |
| Génération d'un rapport | Oui, selon le stockage | Écriture contrôlée et résultat idempotent |
| PUT de remplacement | À analyser | Préconditions et sémantique vérifiées |
| PATCH de configuration | Pas aveuglément | Relire l'état en cas de résultat ambigu |
| POST de création | Pas aveuglément | Vérifier si la ressource a déjà été créée |
| DELETE | Pas aveuglément | Vérifier l'état courant et la cible exacte |
| Action réseau à effet externe | Très prudent | Contrat de récupération et vérification obligatoires |

## 12.3. Backoff avec jitter

Une politique de reprise peut utiliser un délai progressif afin d'éviter que de nombreux clients réessaient en même temps.

Exemple pédagogique :

```python
import random


def retry_delay(
    attempt: int,
    *,
    base_delay: float = 0.5,
    max_delay: float = 15.0,
) -> float:
    if attempt < 1:
        raise ValueError("attempt doit être positif.")

    exponential = min(
        max_delay,
        base_delay * (2 ** (attempt - 1)),
    )

    jitter = random.uniform(0.0, exponential * 0.2)

    return min(max_delay, exponential + jitter)
```

Cette fonction calcule un délai ; elle n'implémente pas, à elle seule, une politique de reprise complète.

Dans une application réelle, ajoutez une limite globale de tentatives, une classification d'erreurs, un budget temporel et l'interdiction explicite de reprendre aveuglément certaines opérations de modification.

## 12.4. Ne réessayez pas toutes les erreurs

Une erreur de validation JSON n'est pas nécessairement transitoire.

Un `403` indique un problème d'autorisation.

Un `404` peut indiquer un chemin erroné.

Un `412` ou un autre rejet de précondition exige une réévaluation du contexte.

Le client doit donc classer les erreurs avant d'envisager une reprise.

## 12.5. État inconnu après une rupture

Lorsqu'une requête de modification expire sans réponse, l'état final peut être inconnu.

Le statut doit refléter cette incertitude.

Exemples de statuts applicatifs :

- `success` ;
- `rejected` ;
- `validation_failed` ;
- `conflict` ;
- `unknown_after_timeout` ;
- `recovery_required`.

Un statut tel que `unknown_after_timeout` est préférable à un faux `failed` si le changement a peut-être été appliqué.


# 13. SÉCURITÉ AVANCÉE ET CONTRÔLE DES ACCÈS

## 13.1. L'authentification ne constitue pas l'autorisation

Le serveur peut reconnaître l'identité d'un client sans lui permettre toutes les opérations.

La plateforme doit donc différencier l'identification du compte et la permission d'effectuer une opération donnée.

Le modèle NACM décrit par le RFC 8341 définit des mécanismes de contrôle d'accès applicables à NETCONF et RESTCONF.

Référence :
https://www.rfc-editor.org/rfc/rfc8341.html

## 13.2. Séparer les profils d'accès

Prévoyez des profils distincts, par exemple :

- `restconf_read` : lecture des données nécessaires ;
- `restconf_discovery` : découverte des schémas et capacités autorisés ;
- `restconf_change` : modifications précises ;
- `restconf_audit` : lecture des informations nécessaires à la traçabilité.

Ces noms sont des conventions internes. Les droits réels doivent être configurés sur le serveur.

Ne donnez pas de privilèges de modification à un collecteur qui doit uniquement réaliser un inventaire.

## 13.3. TLS

La vérification TLS doit rester activée.

Dans un environnement avec autorité interne, fournissez la chaîne de confiance appropriée.

Ne désactivez pas les validations de certificats pour contourner une erreur. Il faut identifier si le problème vient du nom du serveur, de la chaîne de confiance, de l'expiration ou de la configuration.

## 13.4. Réduire la surface d'accès

Le serveur de gestion devrait être accessible uniquement depuis les zones et systèmes autorisés.

Les contrôles de niveau réseau complètent les permissions applicatives.

Le compte d'automatisation doit également avoir une portée limitée afin qu'une compromission ou une erreur du programme n'affecte pas tout le parc.

## 13.5. Sécurité de l'inventaire

L'inventaire peut conduire le client à contacter une adresse donnée. Il est donc une donnée critique.

Un fichier modifié pourrait élargir le périmètre de l'automatisation.

La plateforme doit valider :

- les cibles ;
- les noms DNS ;
- les environnements ;
- les chemins ;
- les profils d'identifiants ;
- les opérations autorisées ;
- les destinations HTTPS.

## 13.6. Sécurité des journaux

Les journaux ne doivent pas contenir :

- les mots de passe ;
- les en-têtes d'authentification ;
- les jetons ;
- les clés privées ;
- les corps complets de configuration quand cela n'est pas nécessaire ;
- des informations sensibles non filtrées.

Les logs et les sauvegardes peuvent être sensibles même lorsqu'ils ne contiennent aucun mot de passe.

## 13.7. Sécurité du modèle

La YANG Library peut révéler des modules, des révisions et des extensions disponibles.

Ces informations peuvent être utiles à une application de gestion, mais elles ne doivent être exposées qu'aux identités autorisées.

Le contrôle d'accès doit prendre en compte la lecture de métadonnées et de notifications, pas seulement la modification de configuration.

## 13.8. Politique de changement

Une opération de modification doit être liée à une politique explicite, avec des éléments tels que :

- identifiant de changement ;
- environnement ;
- liste de cibles ;
- type d'opération ;
- paramètres autorisés ;
- critères de succès ;
- critères d'arrêt ;
- approbation ;
- stratégie de récupération.

Il ne suffit pas qu'un utilisateur puisse appeler l'API. Il faut aussi que le changement corresponde à son autorisation dans l'organisation.


# 14. EXÉCUTION MULTI-ÉQUIPEMENTS ET LIMITATION DE DÉBIT

## 14.1. Le nombre de workers est une décision opérationnelle

Une forte concurrence peut réduire la durée totale des collectes, mais augmenter :

- la charge des équipements ;
- la pression sur les serveurs d'authentification ;
- les délais de réponse ;
- le volume de journaux ;
- le taux d'erreurs transitoires ;
- les risques de conflit lorsque plusieurs opérations concernent la même cible.

Le réglage doit être mesuré sur l'environnement cible.

## 14.2. Un modèle de résultat par équipement

Chaque tâche devrait renvoyer un résultat indépendant.

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceExecution:
    device: str
    run_id: str
    operation: str
    status: str
    duration_ms: int
    http_status: int | None
    error_category: str | None
    data: Any = None
```

Le résultat doit permettre d'agréger les données sans perdre l'identité de l'équipement ou la catégorie de problème.

## 14.3. Limiter le débit

Il faut distinguer :

- le nombre de tâches parallèles ;
- le nombre de requêtes par seconde ;
- la charge imposée par une opération ;
- la limitation éventuelle définie par le serveur.

Un grand nombre de requêtes GET simples n'a pas nécessairement le même coût qu'une collecte de grosses ressources ou qu'une série de changements.

La plateforme peut utiliser une file d'attente, une limite de workers et un régulateur de débit.

## 14.4. Limitation de débit simple

Exemple de régulateur pour un seul processus :

```python
from threading import Lock
from time import monotonic, sleep


class SimpleRateLimiter:
    def __init__(self, requests_per_second: float):
        if requests_per_second <= 0:
            raise ValueError(
                "requests_per_second doit être positif."
            )

        self.interval = 1.0 / requests_per_second
        self.lock = Lock()
        self.next_allowed = 0.0

    def acquire(self) -> None:
        with self.lock:
            now = monotonic()

            if now < self.next_allowed:
                sleep(self.next_allowed - now)

            current = monotonic()
            self.next_allowed = max(
                self.next_allowed,
                current,
            ) + self.interval
```

Cette implémentation donne un rythme de départ partagé par les threads du même processus. Elle n'est pas un limiteur distribué et ne couvre pas plusieurs processus ou plusieurs serveurs d'automatisation.

Elle ne tient pas non plus compte du coût variable des opérations. Les collectes et changements à fort impact peuvent nécessiter des politiques spécifiques.

## 14.5. Traiter les erreurs par cible

Une erreur sur une cible ne doit pas supprimer tous les résultats du lot.

Le rapport doit distinguer les équipements exécutés, en échec, ignorés et non traités après un arrêt.

Dans un workflow de changement, les équipements non traités ne doivent pas être confondus avec ceux dont le changement a été tenté sans que son résultat soit confirmé.

## 14.6. Ordonnancement des changements

L'automatisation de changements doit respecter les dépendances topologiques et opérationnelles.

Par exemple, modifier en même temps des équipements redondants sans contrôle de l'état pourrait réduire la disponibilité.

Le nombre de workers ne peut pas remplacer une politique d'ordonnancement. Les lots et leur ordre doivent correspondre à l'impact du changement.

## 14.7. Schéma SVG animé — contrôle du débit

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 355" role="img" aria-labelledby="rate-title rate-desc" style="max-width:100%;height:auto">
  <title id="rate-title">Orchestration et limitation de débit</title>
  <desc id="rate-desc">La file d'opérations passe par un limiteur et un pool contrôlé. Les résultats sont classés par équipement avant agrégation.</desc>
  <defs>
    <marker id="rate-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#63bce7"/></marker>
    <style>
      @keyframes rate-flow { to { stroke-dashoffset:-24; } }
      .rate-link { fill:none;stroke:#63bce7;stroke-width:2.3;stroke-dasharray:6 7;marker-end:url(#rate-arrow);animation:rate-flow 2s linear infinite; }
      .rate-label { fill:#f2f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .rate-small { fill:#bccadd;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="353" rx="14" fill="#0c1421" stroke="#2c4059"/>
  <rect x="25" y="85" width="190" height="82" rx="10" fill="#292440" stroke="#b2a2ee" stroke-width="1.5"/>
  <text x="120" y="112" class="rate-label">File d'opérations</text><text x="120" y="134" class="rate-small">cibles et priorités</text><text x="120" y="150" class="rate-small">validées</text>
  <rect x="255" y="85" width="190" height="82" rx="10" fill="#193245" stroke="#63bce7" stroke-width="1.5"/>
  <text x="350" y="112" class="rate-label">Limiteur de débit</text><text x="350" y="134" class="rate-small">budget et cadence</text><text x="350" y="150" class="rate-small">concurrence</text>
  <rect x="485" y="85" width="190" height="82" rx="10" fill="#17352e" stroke="#64c7a4" stroke-width="1.5"/>
  <text x="580" y="112" class="rate-label">Workers</text><text x="580" y="134" class="rate-small">sessions isolées</text><text x="580" y="150" class="rate-small">délai contrôlé</text>
  <rect x="715" y="85" width="200" height="82" rx="10" fill="#34291e" stroke="#e4b15d" stroke-width="1.5"/>
  <text x="815" y="112" class="rate-label">Équipements</text><text x="815" y="134" class="rate-small">charge surveillée</text><text x="815" y="150" class="rate-small">opérations autorisées</text>
  <path class="rate-link" d="M215 126 H250"/><path class="rate-link" d="M445 126 H480"/><path class="rate-link" d="M675 126 H710"/>
  <path class="rate-link" d="M815 167 V227 H580 V173"/>
  <rect x="316" y="229" width="530" height="58" rx="10" fill="#1d2b3f" stroke="#86a4cd" stroke-width="1.5"/>
  <text x="581" y="252" class="rate-label">Résultats par cible</text><text x="581" y="272" class="rate-small">succès, échec, ignoré ou état inconnu</text>
  <text x="470" y="319" class="rate-small">Plus de concurrence n'est pas toujours synonyme de meilleure exploitation.</text>
</svg>


# 15. NOTIFICATIONS, FLUX D'ÉVÉNEMENTS ET TÉLÉMÉTRIE

RESTCONF peut prendre en charge des flux de notifications YANG et des mécanismes d'abonnement lorsque les capacités nécessaires sont disponibles.

Le niveau Expert doit comprendre la différence entre :

- interroger périodiquement une ressource ;
- recevoir des notifications d'événements ;
- s'abonner aux mises à jour d'un datastore ;
- maintenir une connexion de flux ;
- traiter la perte d'une notification ou d'une connexion.

## 15.1. Polling et notifications

### Polling

Le client effectue périodiquement une requête GET.

Avantages :
- simple à mettre en œuvre ;
- facile à comprendre ;
- adapté aux collectes peu fréquentes.

Inconvénients :
- délai entre deux collectes ;
- requêtes répétées même sans changement ;
- charge potentielle sur les équipements et le réseau.

### Notifications

Le serveur envoie des événements correspondant à un flux ou un abonnement.

Avantages :
- l'application peut recevoir les événements au fur et à mesure ;
- les informations ne sont pas nécessairement redemandées à intervalle fixe ;
- les mécanismes d'abonnement peuvent préciser les filtres et la portée.

Inconvénients :
- gestion des connexions de flux ;
- perte possible de connectivité ;
- gestion de l'état de l'abonnement ;
- besoin de contrôler les permissions et la consommation de ressources ;
- nécessité de définir une stratégie de resynchronisation.

## 15.2. Les standards concernés

Le RFC 8639 définit les mécanismes d'abonnement aux notifications YANG.

Le RFC 8641 couvre les abonnements aux mises à jour de datastores et les mécanismes YANG-Push correspondants.

Le RFC 8650 définit le transport RESTCONF pour les abonnements dynamiques et les notifications concernées.

Références :

- https://www.rfc-editor.org/rfc/rfc8639.html
- https://www.rfc-editor.org/rfc/rfc8641.html
- https://www.rfc-editor.org/rfc/rfc8650.html

## 15.3. Découvrir les flux

Ne construisez pas en dur une URL de flux en supposant qu'elle est identique sur tous les appareils.

Les ressources de flux ou les capacités d'abonnement doivent être découvertes selon les mécanismes disponibles.

Dans les implémentations RESTCONF qui exposent les ressources de surveillance traditionnelles, le conteneur des flux peut être accessible via le module `ietf-restconf-monitoring`. Les mécanismes d'abonnement plus récents utilisent les modèles et opérations définis par les RFC d'abonnement.

Il faut vérifier quelle famille de fonctionnalités est prise en charge par le serveur cible.

## 15.4. Le flux SSE

RESTCONF peut utiliser Server-Sent Events (SSE) pour transmettre les événements dans un flux HTTP.

Le client doit alors traiter un flux continu, et non tenter de lire une réponse JSON unique puis fermer la connexion.

Le mécanisme de souscription dynamique prévu par le RFC 8650 crée d'abord un abonnement via un POST d'opération, puis utilise l'URI fournie pour démarrer la réception du flux.

La construction exacte de la requête dépend du modèle d'opérations d'abonnement exposé par le serveur.

## 15.5. Pourquoi un flux n'est pas une vérité complète éternelle

Une notification informe le client qu'un événement ou une mise à jour est survenu. Elle ne garantit pas à elle seule que l'application possède toujours un état complet et parfaitement synchronisé.

Le client doit concevoir :

- une stratégie de reconnexion ;
- une politique de resynchronisation ;
- une gestion des doublons éventuels si l'application en rencontre ;
- une stratégie d'identification des événements ;
- une surveillance de l'état de la souscription ;
- des limites de consommation et de stockage ;
- des contrôles d'autorisation.

## 15.6. Exemple conceptuel de traitement d'événements

Pseudo-code :

```python
def consume_event_stream(stream_response):
    for event in parse_sse(stream_response):
        validate_event_shape(event)
        persist_event(event)
        update_internal_state(event)
```

`parse_sse()` représente le parseur SSE que vous devez choisir ou implémenter selon une bibliothèque adaptée.

`validate_event_shape()` doit respecter le modèle et le type d'événement reçus.

`persist_event()` conserve les informations nécessaires selon la politique de rétention.

`update_internal_state()` met à jour une projection des données observées et doit savoir détecter ou corriger un état incomplet.

Ce pseudo-code décrit l'architecture et n'est pas un consommateur RESTCONF prêt à exécuter.

## 15.7. Limiter les souscriptions

Les abonnements consomment des ressources sur les équipements et les systèmes qui les reçoivent.

Une application doit connaître le nombre d'abonnements actifs, leurs paramètres, leur durée de vie et leur état.

La création répétée de souscriptions sans contrôle peut créer une charge inutile. Le client doit également être capable de supprimer ou terminer les abonnements qu'il a créés lorsque c'est prévu par le protocole et autorisé.

## 15.8. Schéma SVG animé — polling et notifications

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 365" role="img" aria-labelledby="notify-title notify-desc" style="max-width:100%;height:auto">
  <title id="notify-title">Comparaison entre polling et notifications</title>
  <desc id="notify-desc">Le polling répète des requêtes à intervalle régulier. Les notifications transmettent les événements via un flux d'abonnement lorsque le serveur prend en charge cette fonction.</desc>
  <defs>
    <marker id="notify-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#64c6a5"/></marker>
    <style>
      @keyframes notify-flow { to { stroke-dashoffset:-25; } }
      .notify-link { fill:none;stroke:#64c6a5;stroke-width:2.4;stroke-dasharray:7 7;marker-end:url(#notify-arrow);animation:notify-flow 2s linear infinite; }
      .notify-label { fill:#f2f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .notify-small { fill:#bac8dd;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="363" rx="14" fill="#0c1421" stroke="#2d3f57"/>
  <text x="245" y="34" class="notify-label">Polling</text>
  <text x="704" y="34" class="notify-label">Notifications</text>
  <rect x="34" y="65" width="180" height="62" rx="9" fill="#282440" stroke="#b0a0ef" stroke-width="1.5"/>
  <text x="124" y="90" class="notify-label">Client</text><text x="124" y="109" class="notify-small">GET périodique</text>
  <rect x="278" y="65" width="180" height="62" rx="9" fill="#183245" stroke="#60bce5" stroke-width="1.5"/>
  <text x="368" y="90" class="notify-label">Serveur</text><text x="368" y="109" class="notify-small">réponse à chaque GET</text>
  <path class="notify-link" d="M214 80 H272"/><path class="notify-link" d="M278 111 H220"/>
  <path d="M124 134 V165 H368 V134" fill="none" stroke="#8ba5ca" stroke-width="2" stroke-dasharray="5 7" style="animation:notify-flow 2.6s linear infinite"/>
  <text x="245" y="190" class="notify-small">requêtes répétées</text>
  <rect x="501" y="65" width="180" height="62" rx="9" fill="#282440" stroke="#b0a0ef" stroke-width="1.5"/>
  <text x="591" y="90" class="notify-label">Client</text><text x="591" y="109" class="notify-small">souscription</text>
  <rect x="745" y="65" width="160" height="62" rx="9" fill="#17352e" stroke="#64c6a5" stroke-width="1.5"/>
  <text x="825" y="90" class="notify-label">Serveur</text><text x="825" y="109" class="notify-small">flux SSE</text>
  <path class="notify-link" d="M681 91 H739"/>
  <path class="notify-link" d="M825 127 V190 H591 V133"/>
  <text x="704" y="216" class="notify-small">événements lorsqu'ils surviennent</text>
  <rect x="180" y="246" width="580" height="59" rx="10" fill="#1b2b3e" stroke="#829fc8" stroke-width="1.5"/>
  <text x="470" y="269" class="notify-label">La bonne stratégie dépend du besoin</text><text x="470" y="289" class="notify-small">latence, capacité du serveur, reprise et cohérence d'état</text>
  <text x="470" y="335" class="notify-small">Une souscription nécessite découverte, permissions et gestion de connexion.</text>
</svg>


# 16. TESTS UNITAIRES, CONTRACTUELS ET D'INTÉGRATION

Un projet Expert ne peut pas dépendre exclusivement d'un équipement physique.

Chaque couche doit pouvoir être testée à son niveau.

## 16.1. Tests unitaires

Les tests unitaires vérifient la logique locale :

- validation des entrées ;
- encodage des clés ;
- construction des URI ;
- normalisation des données ;
- classification des statuts ;
- création des plans ;
- génération des rapports.

Ils doivent être rapides et ne pas ouvrir de connexion réseau.

## 16.2. Tests contractuels

Les tests contractuels vérifient si les réponses et les structures réelles respectent les contrats attendus.

Par exemple, une opération peut exiger les champs `name` et `enabled`.

Le test doit vérifier que le contrat est satisfait sur les corps de réponse représentatifs.

Ce type de test est utile lorsque des changements de modèle ou de version de système sont possibles.

## 16.3. Tests d'intégration

Les tests d'intégration vérifient l'interface réelle :

- validation TLS ;
- authenticité du serveur ;
- URI et permissions ;
- découverte des capacités ;
- disponibilité des datastores ;
- traitement des opérations ;
- réponses HTTP ;
- modifications en laboratoire.

Ces tests doivent être limités à un environnement autorisé.

## 16.4. Tests de résilience

Les scénarios doivent inclure :

- serveur indisponible ;
- timeout de lecture ;
- certificat refusé ;
- authentification invalide ;
- réponse HTTP inattendue ;
- JSON mal formé ;
- modèle absent ;
- conflit ETag ;
- modification appliquée mais réponse perdue ;
- perte du flux de notifications ;
- changement de `content-id` ;
- dépassement du budget de concurrence.

Le test de résilience doit vérifier que l'application ne transforme pas ces situations en faux succès.

## 16.5. Test du constructeur d'URI

Exemple :

```python
def test_data_url_builder():
    config = RestconfConfig(
        origin="https://router-lab.example",
        username="reader",
        password="dummy",
    )

    client = RestconfClient(config)

    try:
        assert client.build_data_url(
            "ietf-interfaces:interfaces"
        ) == (
            "https://router-lab.example/restconf/data/"
            "ietf-interfaces:interfaces"
        )

        assert client.build_ds_url(
            "ietf-datastores:operational",
            "ietf-interfaces:interfaces",
        ) == (
            "https://router-lab.example/restconf/ds/"
            "ietf-datastores:operational/"
            "ietf-interfaces:interfaces"
        )

    finally:
        client.close()
```

Ce test ne nécessite aucune connexion réelle.

Il faut ajouter les tests négatifs, par exemple pour refuser les chemins absolus ou les segments interdits.

## 16.6. Test de validation des données

```python
import pytest


def test_enabled_must_be_boolean():
    bad = {
        "name": "Loopback0",
        "enabled": "true",
    }

    with pytest.raises(ValueError):
        validate_interface_item(bad)
```

Le contrat doit être défini avec les types prévus par le modèle réel. Ce test démontre qu'une chaîne ne doit pas être acceptée automatiquement comme un booléen.

## 16.7. Tester les ETags

Les tests du contrôle conditionnel doivent vérifier :

- le stockage de l'ETag retourné ;
- la présence de `If-Match` dans le changement ;
- le traitement d'une précondition rejetée ;
- la relecture de l'état après conflit ;
- l'absence de reprise aveugle.

Une réponse de conflit est un résultat attendu d'un test, pas nécessairement un défaut du serveur.

## 16.8. Tests de régression de modèle

Lorsqu'une révision du modèle change, relancez les tests qui vérifient les contrats de données.

Les changements peuvent être sans effet pour certaines opérations et importants pour d'autres.

Une architecture avancée devrait savoir quelles opérations dépendent d'un module ou d'une révision spécifique.

## 16.9. Pyramide de tests

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="test-title test-desc" style="max-width:100%;height:auto">
  <title id="test-title">Pyramide de tests d'une plateforme RESTCONF</title>
  <desc id="test-desc">La majorité des tests sont unitaires et rapides. Les tests contractuels et d'intégration contrôlent les modèles et les interfaces réelles. Les tests de bout en bout sont plus rares.</desc>
  <defs>
    <style>
      .test-label { fill:#f2f5ff;font:600 14px sans-serif;text-anchor:middle; }
      .test-small { fill:#d0d9e7;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="338" rx="14" fill="#0d1420" stroke="#2f4057"/>
  <text x="470" y="32" class="test-label">Tester chaque couche avec le bon niveau d'effort</text>
  <path d="M470 58 L310 130 H630 Z" fill="#34304c" stroke="#b4a4f1" stroke-width="1.5"/>
  <text x="470" y="102" class="test-label">Bout en bout</text>
  <path d="M310 136 L230 210 H710 L630 136 Z" fill="#1b3447" stroke="#64bce4" stroke-width="1.5"/>
  <text x="470" y="179" class="test-label">Intégration et contrats</text>
  <path d="M230 216 L130 292 H810 L710 216 Z" fill="#19362f" stroke="#66c8a5" stroke-width="1.5"/>
  <text x="470" y="256" class="test-label">Tests unitaires</text>
  <text x="470" y="277" class="test-small">validation, URI, erreurs, rapports</text>
  <text x="470" y="321" class="test-small">Les tests de laboratoire complètent les tests locaux ; ils ne les remplacent pas.</text>
</svg>


# 17. OBSERVABILITÉ, AUDIT ET RAPPORTS

## 17.1. Un identifiant d'exécution

Chaque exécution doit recevoir un identifiant stable.

Exemple :

```text
RUN-2026-10-23-RESTCONF-0001
```

Cette valeur est illustrative. En production, générer un ID unique selon une convention contrôlée permet de relier les logs, le manifeste, les résultats, les changements et les rapports.

## 17.2. Les champs de journal recommandés

Un événement de journal structuré peut contenir :

```json
{
  "timestamp": "2026-10-23T10:15:00Z",
  "run_id": "RUN-EXPERT-001",
  "device": "router-lab-01",
  "operation": "get_operational_interfaces",
  "method": "GET",
  "duration_ms": 247,
  "http_status": 200,
  "status": "success",
  "validation_status": "success"
}
```

Les valeurs sont illustratives.

Ajoutez les métadonnées de modèle ou de version seulement lorsqu'elles sont utiles au diagnostic.

## 17.3. Mesures de fonctionnement

Suivez notamment :

- le nombre d'opérations ;
- le taux de réussite ;
- le temps de réponse ;
- les timeouts ;
- les conflits ;
- les erreurs par cible ;
- les erreurs par modèle ;
- les changements rejetés ;
- les changements validés ;
- les résultats métier non conformes ;
- les souscriptions actives et leurs erreurs, si les notifications sont utilisées.

## 17.4. Les logs doivent être protégés

Un log structuré n'est pas nécessairement non sensible.

N'enregistrez pas par défaut des corps complets de configuration. Le niveau de détail doit répondre à un besoin opérationnel précis.

Les données sensibles doivent être filtrées, protégées et conservées selon une politique définie.

## 17.5. Rapport d'exécution

Un rapport final pourrait ressembler à ceci :

```json
{
  "schema_version": 1,
  "run_id": "RUN-EXPERT-001",
  "operation": "inventory_audit",
  "summary": {
    "planned": 20,
    "attempted": 20,
    "success": 18,
    "failed": 2,
    "skipped": 0
  },
  "results": [
    {
      "device": "router-lab-01",
      "status": "success",
      "http_status": 200,
      "validation_status": "success"
    },
    {
      "device": "router-lab-02",
      "status": "failed",
      "http_status": 403,
      "validation_status": "not_run"
    }
  ]
}
```

Le rapport complet doit être généré à partir des résultats réels et non être codé en dur. Les informations d'erreur doivent être assainies avant d'être publiées.

## 17.6. Savoir expliquer une exécution

Un opérateur doit pouvoir répondre à ces questions sans examiner chaque ligne du programme :

- quelles cibles étaient prévues ?
- quelles cibles ont été traitées ?
- quels modèles ont été requis ?
- quelles opérations ont été effectuées ?
- quelle réponse a été obtenue ?
- quels contrôles ont réussi ?
- quels changements ont été exécutés ?
- quelles cibles restent dans un état incertain ?
- quelles preuves sont conservées ?

## 17.7. Schéma SVG animé — observabilité

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="obs-title obs-desc" style="max-width:100%;height:auto">
  <title id="obs-title">Observabilité et audit RESTCONF</title>
  <desc id="obs-desc">Les requêtes génèrent des événements, des métriques et des résultats validés, qui sont agrégés en rapports protégés.</desc>
  <defs>
    <marker id="obs-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#63bee6"/></marker>
    <style>
      @keyframes obs-flow { to { stroke-dashoffset:-26; } }
      .obs-link { fill:none;stroke:#63bee6;stroke-width:2.3;stroke-dasharray:6 7;marker-end:url(#obs-arrow);animation:obs-flow 2s linear infinite; }
      .obs-label { fill:#f3f6ff;font:600 14px sans-serif;text-anchor:middle; }
      .obs-small { fill:#bdcade;font:12px sans-serif;text-anchor:middle; }
    </style>
  </defs>
  <rect x="1" y="1" width="938" height="338" rx="14" fill="#0d1421" stroke="#304157"/>
  <rect x="34" y="74" width="195" height="76" rx="10" fill="#282440" stroke="#b0a0ef" stroke-width="1.5"/>
  <text x="131" y="101" class="obs-label">Opérations</text><text x="131" y="123" class="obs-small">RESTCONF + contrôles</text>
  <rect x="286" y="74" width="195" height="76" rx="10" fill="#193245" stroke="#61bce6" stroke-width="1.5"/>
  <text x="383" y="101" class="obs-label">Événements</text><text x="383" y="123" class="obs-small">résultats normalisés</text>
  <rect x="538" y="74" width="170" height="76" rx="10" fill="#17352e" stroke="#64c6a4" stroke-width="1.5"/>
  <text x="623" y="101" class="obs-label">Métriques</text><text x="623" y="123" class="obs-small">latence + erreurs</text>
  <rect x="765" y="74" width="145" height="76" rx="10" fill="#34291d" stroke="#e4b05e" stroke-width="1.5"/>
  <text x="837" y="101" class="obs-label">Rapport</text><text x="837" y="123" class="obs-small">audit protégé</text>
  <path class="obs-link" d="M229 112 H281"/><path class="obs-link" d="M481 112 H533"/><path class="obs-link" d="M708 112 H760"/>
  <path class="obs-link" d="M623 150 V215 H383 V155"/>
  <rect x="245" y="219" width="470" height="58" rx="10" fill="#1e2b40" stroke="#86a3ca" stroke-width="1.5"/>
  <text x="480" y="243" class="obs-label">Corrélation par run_id</text><text x="480" y="262" class="obs-small">cible, opération, durée, statut et preuve</text>
  <text x="470" y="313" class="obs-small">La traçabilité permet de comprendre l'exécution sans exposer les secrets.</text>
</svg>


# 18. INTÉGRATION CONTINUE ET EXPLOITATION

## 18.1. Ne pas confondre livraison de code et autorisation de changement

Un pipeline qui valide le code doit pouvoir s'exécuter sans modifier le réseau.

Un workflow de changement doit exiger les permissions et approbations prévues.

Séparez donc :

- les tests de code ;
- la validation des modèles ;
- la génération du plan ;
- l'approbation ;
- l'exécution sur les équipements ;
- le rapport final.

## 18.2. Étapes recommandées du pipeline

1. Vérification du style et de la syntaxe.
2. Tests unitaires.
3. Vérification des dépendances.
4. Recherche de secrets.
5. Tests contractuels.
6. Vérification de l'inventaire.
7. Découverte des capacités en laboratoire.
8. Production du plan.
9. Validation et approbation.
10. Exécution pilote.
11. Contrôle postérieur.
12. Déploiement progressif.
13. Rapport et archivage.

La séquence doit être adaptée aux risques du changement.

## 18.3. Versionner les contrats

Le code, les modèles utilisés, les règles de validation et les dépendances doivent être versionnés.

Lorsqu'un module YANG change, il peut être nécessaire de revoir les chemins, les types de données ou les validations.

Un contrat versionné aide à savoir ce qui a réellement été testé.

## 18.4. Stratégie de déploiement progressif

Une modification importante ne devrait pas être appliquée à l'ensemble d'un parc hétérogène sans phase de contrôle.

Une stratégie possible :

- laboratoire ;
- préproduction ;
- cible pilote ;
- lot restreint ;
- progression conditionnelle ;
- clôture après vérification.

Le contenu du lot dépend de la topologie, des dépendances et de la criticité. Il ne faut pas choisir son périmètre uniquement en fonction d'un pourcentage.

## 18.5. Critères d'arrêt

L'application doit interrompre le lot si :

- une cible ne correspond pas à l'inventaire autorisé ;
- un modèle requis est absent ;
- une précondition n'est plus satisfaite ;
- le plan ne correspond plus à l'état ;
- le serveur renvoie un conflit ;
- la validation métier échoue ;
- le taux d'erreur dépasse le seuil ;
- un budget de temps est dépassé ;
- une étape critique de récupération est incertaine.

Le comportement en cas d'arrêt doit distinguer les cibles non traitées, les cibles réussies et les cibles qui ont subi une opération dont le résultat est ambigu.


# 19. LABORATOIRES PROGRESSIFS

Ces laboratoires complètent ceux du niveau Débutant et du niveau Intermédiaire. Réutilisez la même structure de projet et le même client.

## Laboratoire 1 — Client unifié

**Objectif :** prendre en charge les ressources `/restconf/data` et `/restconf/ds`.

Étapes :

1. reprendre le client RESTCONF du niveau Intermédiaire ;
2. séparer les constructeurs de chemins de données et de datastores ;
3. valider l'hôte ;
4. imposer HTTPS ;
5. définir les délais ;
6. tester les chemins normaux ;
7. tester les chemins invalides ;
8. vérifier la fermeture de session.

**Critère d'acceptation :** le client ne confond pas une ressource de données avec une ressource datastore NMDA.

## Laboratoire 2 — Découverte des capacités

**Objectif :** éviter de coder en dur les capacités du serveur.

Étapes :

1. lire la racine RESTCONF ;
2. découvrir les capacités accessibles ;
3. identifier les options nécessaires à une opération ;
4. représenter les capacités en objets Python ;
5. refuser une fonction requise si elle n'est pas découverte ;
6. consigner les capacités observées.

**Critère d'acceptation :** une opération facultative ne se lance pas sur la seule base d'une hypothèse.

## Laboratoire 3 — Cache de YANG Library

**Objectif :** construire un cache de métadonnées contrôlé.

Étapes :

1. lire la YANG Library ;
2. extraire l'identifiant de contenu lorsqu'il existe ;
3. conserver les modules et révisions ;
4. créer un cache versionné ;
5. simuler un changement de contenu ;
6. vérifier l'invalidation ;
7. tester le cas d'une bibliothèque ancienne.

**Critère d'acceptation :** un changement de schéma détecté déclenche une revalidation au lieu d'utiliser des métadonnées périmées.

## Laboratoire 4 — Exploration de NMDA

**Objectif :** comprendre la différence entre la configuration et l'état opérationnel.

Étapes :

1. vérifier si le serveur prend en charge NMDA ;
2. interroger `operational` ;
3. interroger `running` si disponible ;
4. comparer les champs utiles ;
5. documenter les valeurs absentes ;
6. tester un cas où la configuration attendue diffère de l'état observé.

**Critère d'acceptation :** le rapport distingue les sources de données et ne déclare pas un succès métier si l'objectif n'est pas atteint.

## Laboratoire 5 — Validation des contrats JSON

**Objectif :** créer des contrats versionnés pour les opérations.

Étapes :

1. définir les ressources nécessaires ;
2. choisir les champs requis ;
3. spécifier les types ;
4. écrire des validateurs ;
5. ajouter des tests négatifs ;
6. conserver des réponses d'exemple assainies ;
7. vérifier le comportement lorsque le modèle change.

**Critère d'acceptation :** une réponse valide du point de vue syntaxique, mais incompatible avec le contrat, est signalée explicitement.

## Laboratoire 6 — Cache conditionnel

**Objectif :** utiliser ETag pour réduire les lectures inutiles et détecter des changements.

Étapes :

1. lire une ressource ;
2. récupérer son ETag ou celui du datastore selon les règles disponibles ;
3. stocker le cache avec l'URI et ses paramètres ;
4. effectuer une nouvelle lecture conditionnelle ;
5. traiter la réponse `304` ;
6. invalider le cache lorsque le contexte change.

**Critère d'acceptation :** le cache n'est jamais réutilisé pour une autre ressource, un autre encodage ou une autre sélection de données.

## Laboratoire 7 — PATCH avec précondition

**Objectif :** pratiquer une modification contrôlée en laboratoire.

Étapes :

1. choisir une ressource non critique ;
2. collecter l'état initial ;
3. calculer le plan ;
4. vérifier le périmètre ;
5. lire l'ETag disponible ;
6. exécuter le PATCH avec la précondition appropriée ;
7. gérer un rejet de précondition ;
8. relire la ressource ;
9. comparer les valeurs finales ;
10. produire un rapport.

**Critère d'acceptation :** une modification n'est pas répétée automatiquement après un conflit ou un timeout ambigu.

## Laboratoire 8 — YANG Patch

**Objectif :** construire un patch de plusieurs opérations, si le serveur le prend en charge.

Étapes :

1. vérifier `OPTIONS` ;
2. lire `Accept-Patch` ;
3. confirmer le type de contenu pris en charge ;
4. construire un patch valide en laboratoire ;
5. tester l'opération ;
6. provoquer volontairement une erreur de validation ;
7. constater le comportement du serveur ;
8. documenter les résultats.

**Critère d'acceptation :** le programme sait distinguer le mécanisme supporté de celui qui ne l'est pas et ne suppose pas une transaction universelle.

## Laboratoire 9 — Collecte concurrente

**Objectif :** collecter plusieurs équipements sans surcharge ni perte de résultats.

Étapes :

1. charger l'inventaire ;
2. valider les cibles ;
3. découvrir les capacités nécessaires ;
4. définir une concurrence maximale ;
5. appliquer une limitation de débit ;
6. traiter les lectures indépendantes ;
7. simuler plusieurs erreurs ;
8. produire des statuts par cible ;
9. comparer les performances à une collecte séquentielle.

**Critère d'acceptation :** un échec par cible n'empêche pas l'ensemble du lot de produire un rapport cohérent.

## Laboratoire 10 — Notifications et résilience

**Objectif :** comprendre les mécanismes de souscription lorsque disponibles.

Étapes :

1. découvrir les capacités de notification ;
2. déterminer le mécanisme adapté à l'implémentation ;
3. créer une souscription en environnement de laboratoire ;
4. établir le flux ;
5. traiter les messages ;
6. simuler une perte de connexion ;
7. rétablir le flux ;
8. décider quand une resynchronisation est nécessaire ;
9. libérer la souscription selon les règles prévues.

**Critère d'acceptation :** les événements, l'état de la souscription et les éventuelles incertitudes sont traités explicitement.

## Laboratoire 11 — Pipeline de validation

**Objectif :** rendre les contrôles reproductibles.

Étapes :

1. exécuter les tests unitaires ;
2. vérifier les dépendances ;
3. tester les contrats ;
4. valider l'inventaire ;
5. découvrir les capacités en laboratoire ;
6. générer un plan sans application ;
7. enregistrer les résultats ;
8. définir des critères qui interdisent la mise en production.

**Critère d'acceptation :** le pipeline détecte les défauts connus avant toute modification réelle.

## Laboratoire 12 — Audit de bout en bout

**Objectif :** réunir les composants dans un workflow complet.

Étapes :

1. générer un identifiant d'exécution ;
2. charger l'inventaire ;
3. découvrir les modèles et datastores ;
4. lire l'état initial ;
5. créer un plan ;
6. appliquer l'approbation nécessaire ;
7. exécuter sur un lot pilote ;
8. vérifier l'état final ;
9. arrêter le lot si un critère est atteint ;
10. produire le rapport ;
11. examiner les journaux ;
12. conserver les preuves suivant la politique définie.

**Livrables :**

- code ;
- tests unitaires et d'intégration ;
- exemple de YANG Library ;
- contrat de données ;
- plan d'opération ;
- rapports ;
- procédure d'arrêt ;
- procédure de récupération ;
- guide d'exploitation.


# 20. PROJET FINAL — RESTCONF AUTOMATION CONTROLLER

## 20.1. Mission

Construire une application Python capable de découvrir les capacités de plusieurs équipements, d'effectuer une collecte model-driven, d'effectuer une comparaison d'état et de préparer ou d'exécuter un changement explicitement autorisé.

Le projet doit prolonger le client développé dans le niveau Intermédiaire.

Il ne doit pas se transformer en un seul fichier contenant inventaire, transport, parsing, changement et rapport.

## 20.2. Architecture de référence

```text
restconf-automation-controller/
├── README.md
├── pyproject.toml
├── config/
│   ├── inventory.yaml
│   └── policy.yaml
├── src/
│   └── controller/
│       ├── config.py
│       ├── client.py
│       ├── discovery.py
│       ├── yang_library.py
│       ├── validation.py
│       ├── operations.py
│       ├── concurrency.py
│       ├── change_control.py
│       ├── telemetry.py
│       └── reporting.py
├── tests/
│   ├── test_client.py
│   ├── test_discovery.py
│   ├── test_validation.py
│   ├── test_changes.py
│   └── test_reporting.py
├── examples/
└── artifacts/
```

## 20.3. Interface de commande attendue

Exemple conceptuel :

```text
controller audit --inventory config/inventory.yaml

controller discover --device router-lab-01

controller collect --inventory config/inventory.yaml --workers 3

controller plan --change config/CHG-EXAMPLE.yaml

controller apply --change config/CHG-EXAMPLE.yaml --approval approvals/CHG-EXAMPLE.json

controller report --run-id RUN-EXAMPLE-001
```

Cette interface doit être implémentée par le projet. Elle n'est pas une commande native de RESTCONF.

## 20.4. Exigences fonctionnelles

Le contrôleur doit :

- valider l'inventaire ;
- vérifier le périmètre autorisé ;
- utiliser HTTPS ;
- gérer les secrets correctement ;
- découvrir les capacités ;
- découvrir les modèles et les révisions ;
- distinguer les espaces `/data` et `/ds` ;
- sélectionner les datastores selon l'opération ;
- valider les réponses JSON ;
- appliquer les contrats métier ;
- gérer ETag et les préconditions lorsqu'ils sont disponibles ;
- distinguer les échecs techniques et métier ;
- limiter la concurrence ;
- limiter le débit ;
- éviter les reprises aveugles ;
- produire un résultat par équipement ;
- générer un rapport final ;
- conserver les preuves nécessaires ;
- empêcher un changement non autorisé ;
- vérifier l'état final après une modification.

## 20.5. Exigences non fonctionnelles

**Sécurité :** contrôle TLS, permissions minimales et secrets exclus des journaux.

**Compatibilité :** découverte des capacités et modèles avant les opérations dépendantes.

**Résilience :** temps limites, gestion des erreurs et traitement des résultats partiels.

**Testabilité :** tests unitaires et d'intégration reproductibles.

**Auditabilité :** ID d'exécution, version du code, modèle observé et plan associé au résultat.

**Maintenabilité :** modules à responsabilités claires.

**Exploitabilité :** rapport utile à un opérateur, statuts compréhensibles et procédure d'arrêt.

## 20.6. Barème recommandé

| Domaine | Points |
|---|---:|
| Architecture et modularité | 10 |
| Client RESTCONF centralisé | 10 |
| Découverte dynamique | 12 |
| YANG Library et NMDA | 12 |
| Contrats et validation de données | 12 |
| Sécurité | 12 |
| Contrôle de changement et ETag | 12 |
| Gestion des erreurs et des reprises | 8 |
| Concurrence et observabilité | 6 |
| Tests, documentation et rapport | 6 |
| **Total** | **100** |

Une seule faille critique peut interdire l'acceptation, indépendamment du score :

- vérification TLS désactivée par défaut ;
- secret en clair dans le dépôt ;
- opération hors périmètre ;
- modification risquée rejouée aveuglément après un timeout ;
- succès métier déclaré sans contrôle postérieur ;
- absence de gestion d'un conflit lorsque la précondition est rejetée ;
- erreur masquée par un rapport globalement positif.

## 20.7. Définition de la réussite

Le projet est terminé lorsque le code sait démontrer :

- ce qu'il a découvert ;
- pourquoi la ressource choisie est compatible ;
- quelle opération a été exécutée ;
- quelles préconditions étaient satisfaites ;
- comment le résultat a été validé ;
- quels échecs ont été rencontrés ;
- comment les risques ont été contrôlés ;
- quelles preuves sont disponibles.


# 21. DÉPANNAGE EXPERT

## 21.1. La découverte des capacités est incomplète

Vérifiez les ressources de surveillance, les versions de modules et les droits du compte. Une ressource de découverte absente peut être liée à l'implémentation ou aux permissions.

Ne remplacez pas la découverte par une liste de capacités supposées valides sur tous les équipements.

## 21.2. La YANG Library a changé

Comparez le `content-id` si disponible, examinez les modules et révisions, puis vérifiez les contrats qui dépendent des données modifiées.

Une variation peut être sans impact pour certaines opérations et critique pour d'autres.

N'invalidez pas une ressource réseau simplement parce que le schéma a changé : identifiez les données et les comportements concernés.

## 21.3. Le chemin `/restconf/ds` renvoie une erreur

Vérifiez que le serveur prend en charge NMDA, le nom qualifié du datastore, l'URI complète et les permissions nécessaires.

N'essayez pas de déplacer le chemin sous `/restconf/data` pour contourner l'erreur. Ces espaces ont des sémantiques différentes.

## 21.4. L'ETag change entre deux lectures

Cela peut indiquer une modification de configuration intervenue entre les deux requêtes.

Relisez l'état, identifiez les différences et vérifiez si votre plan demeure valide.

Ne renouvelez pas simplement l'ETag pour faire accepter l'opération initiale.

## 21.5. Une précondition est rejetée

Le rejet doit déclencher une relecture et une décision.

Si le changement est devenu inutile, abandonnez-le.

Si l'objectif demeure nécessaire, recalculer un plan à partir du nouvel état peut être approprié, mais l'approbation requise doit rester valable pour ce nouveau plan.

## 21.6. La ressource existe mais un champ manque

Vérifiez :

- le modèle ;
- la révision ;
- le datastore ;
- les paramètres `fields` et `depth` ;
- les permissions ;
- l'encodage ;
- les règles de présence des valeurs par défaut.

L'absence d'un champ ne doit pas être automatiquement assimilée à une valeur par défaut ou à un succès.

## 21.7. Le serveur accepte un PATCH mais l'objectif n'est pas atteint

Le succès HTTP ne constitue pas la validation métier.

Relisez la ressource, vérifiez les champs concernés, examinez l'état opérationnel et déterminez si la modification a été appliquée complètement.

Le rapport doit conserver les informations nécessaires pour distinguer une opération transportée correctement d'un objectif non atteint.

## 21.8. Le serveur ne supporte pas YANG Patch

Vérifiez `OPTIONS`, `Accept-Patch`, les capacités et la documentation de l'implémentation.

Si le mécanisme n'est pas disponible, le client peut choisir une autre approche autorisée après évaluation du risque et des garanties. Il ne doit pas supposer que plusieurs requêtes distinctes offrent l'atomicité d'un patch.

## 21.9. Le volume de données est excessif

Sélectionnez une ressource plus précise, utilisez `fields` ou `depth` lorsqu'ils sont supportés et contrôlez la structure réellement nécessaire.

Évaluez également si le polling est la meilleure méthode ou si un mécanisme d'événement est pertinent.

N'adoptez pas une pagination constructeur sans la détecter et sans tester son contrat.

## 21.10. Le taux d'erreur augmente pendant une collecte parallèle

Réduisez la concurrence et le débit. Identifiez les cibles, modèles ou ressources associés aux erreurs.

Ne créez pas une vague de reprises immédiates. Une surcharge peut exiger un ralentissement, un arrêt et une analyse des causes.

## 21.11. Un flux de notifications s'interrompt

Vérifiez l'état de la connexion, la souscription, les permissions, les paramètres du flux et les éventuels événements de suspension ou de terminaison.

La politique de reprise doit savoir si le client peut reprendre le flux ou s'il doit reconstruire son état à partir d'une lecture complète.

Ne considérez pas que le client dispose toujours d'un état correct après une interruption non réconciliée.

## 21.12. Une mise à jour de bibliothèque Python modifie le comportement

Comparez l'environnement, les versions et les tests contractuels. Les dépendances doivent être verrouillées et les mises à jour testées.

En production, la reproductibilité est essentielle pour distinguer un défaut applicatif d'un changement de bibliothèque.


# 22. ÉVALUATION DE SORTIE

Répondez en vous appuyant sur le projet final.

1. Pourquoi faut-il séparer le client HTTP, la découverte, la validation et le changement ?
2. Pourquoi les chemins `/restconf/data` et `/restconf/ds` ne sont-ils pas interchangeables ?
3. Comment utiliser la YANG Library pour vérifier la compatibilité d'une opération ?
4. Quel rôle joue le `content-id` ?
5. À quoi sert l'information `augmented-by` introduite par le RFC 10035 ?
6. Quelle différence existe entre `running`, `intended` et `operational` ?
7. Comment le paramètre `with-origin` peut-il aider à comprendre une valeur opérationnelle ?
8. Quelle différence existe entre un succès HTTP et une validation métier ?
9. Pourquoi un ETag doit-il être conservé tel que le serveur l'a fourni ?
10. Comment interpréter un conflit lors d'un `If-Match` ?
11. Pourquoi n'est-il pas prudent de rejouer un PATCH après un timeout ?
12. Dans quelles conditions YANG Patch peut-il fournir une atomicité ?
13. Pourquoi cette atomicité ne constitue-t-elle pas une transaction universelle multi-équipements ?
14. Comment distinguer une lecture qui doit être retentée d'un changement dont l'issue est inconnue ?
15. Quels contrôles de sécurité faut-il appliquer aux modèles et à la YANG Library ?
16. Pourquoi une session HTTP partagée entre threads demande-t-elle une politique explicite ?
17. Comment limiter le débit sans perdre la traçabilité des échecs ?
18. Comment un client sait-il qu'une souscription doit être resynchronisée ?
19. Quels éléments doivent être conservés dans le manifeste d'exécution ?
20. Quelles conditions doivent arrêter un déploiement ?
21. Pourquoi des tests de contrat sont-ils nécessaires en plus des tests unitaires ?
22. Quelles informations doivent apparaître dans un rapport d'audit ?
23. Comment construire une stratégie de récupération sans promettre un rollback universel ?
24. Dans quelles conditions une API structurée est-elle préférable à une CLI ?
25. Comment démontrer qu'un changement correspond réellement à l'objectif attendu ?

## Grille d'auto-évaluation

**Expert en construction :** vous savez organiser les modules, découvrir les capacités, vérifier les modèles et tester les contrats.

**Expert intermédiaire :** vous gérez les conflits, les datastores, les changements et les erreurs avec des résultats normalisés.

**Prêt pour l'exploitation contrôlée :** vous disposez des contrôles de sécurité, de l'audit, des critères d'arrêt, des tests sur les plateformes réelles et des procédures de récupération vérifiées.

**Prêt pour l'industrialisation :** votre application est reproductible, observable, compatible avec les exigences de gouvernance et capable de prouver ce qu'elle a exécuté et les résultats obtenus.


# 23. GLOSSAIRE

**API** — Interface par laquelle des applications communiquent.

**Atomicité** — Propriété selon laquelle une opération prévue est appliquée intégralement ou n'est pas appliquée, dans les limites définies par le protocole concerné.

**Backoff** — Délai progressif utilisé entre certaines tentatives.

**Datastore** — Ensemble de données de gestion identifié par le protocole.

**ETag** — Identifiant opaque associé à une représentation ou à une version de ressource.

**If-Match** — Précondition HTTP permettant de conditionner une requête à un ETag.

**Idempotence** — Propriété d'une opération répétée qui conserve le même état final sous les hypothèses définies.

**NMDA** — *Network Management Datastore Architecture*.

**NACM** — *Network Configuration Access Control Model*.

**RESTCONF** — Protocole de gestion model-driven reposant sur HTTP et les modèles YANG.

**Résultat métier** — Évaluation de la conformité d'une opération par rapport à son objectif.

**Retry** — Nouvelle tentative d'exécution après un échec classé comme éventuellement transitoire.

**SSE** — *Server-Sent Events*, mécanisme permettant de transmettre un flux d'événements sur HTTP.

**YANG** — Langage de modélisation des données de gestion réseau.

**YANG Library** — Mécanisme permettant de découvrir les modules et schémas YANG supportés par un serveur.

**YANG Patch** — Mécanisme de modification fondé sur un document décrivant plusieurs opérations d'édition de données YANG.

**YANG-Push** — Mécanismes d'abonnement aux mises à jour des datastores selon les standards applicables.


# 24. RÉFÉRENCES OFFICIELLES

Ces documents constituent les références principales pour adapter le code à une implémentation réelle.

## RESTCONF et HTTP

- RFC 8040 — RESTCONF Protocol  
  https://www.rfc-editor.org/rfc/rfc8040.html

- RFC 8527 — RESTCONF Extensions to Support the Network Management Datastore Architecture  
  https://www.rfc-editor.org/rfc/rfc8527.html

- RFC 5789 — PATCH Method for HTTP  
  https://www.rfc-editor.org/rfc/rfc5789.html

## Modèles YANG et datastores

- RFC 7950 — YANG 1.1 Data Modeling Language  
  https://www.rfc-editor.org/rfc/rfc7950.html

- RFC 7951 — JSON Encoding of Data Modeled with YANG  
  https://www.rfc-editor.org/rfc/rfc7951.html

- RFC 8342 — Network Management Datastore Architecture  
  https://www.rfc-editor.org/rfc/rfc8342.html

- RFC 8525 — YANG Library  
  https://www.rfc-editor.org/rfc/rfc8525.html

- RFC 10035 — YANG Library: Addition of the augmented-by List  
  https://www.rfc-editor.org/rfc/rfc10035.html

## Sécurité et modifications

- RFC 8341 — Network Configuration Access Control Model  
  https://www.rfc-editor.org/rfc/rfc8341.html

- RFC 8072 — YANG Patch Media Type  
  https://www.rfc-editor.org/rfc/rfc8072.html

## Notifications et télémétrie

- RFC 8639 — Subscription to YANG Notifications  
  https://www.rfc-editor.org/rfc/rfc8639.html

- RFC 8641 — Subscription to YANG Notifications for Datastore Updates  
  https://www.rfc-editor.org/rfc/rfc8641.html

- RFC 8650 — Dynamic Subscription to YANG Events and Datastores over RESTCONF  
  https://www.rfc-editor.org/rfc/rfc8650.html

## Outils Python

- Requests  
  https://requests.readthedocs.io/

- pytest  
  https://docs.pytest.org/

- Documentation Python  
  https://docs.python.org/3/


# CONCLUSION — L'EXPERTISE EST DANS LA MAÎTRISE DU SYSTÈME

Le niveau Débutant vous a appris à interroger un équipement. Le niveau Intermédiaire vous a appris à construire un client réutilisable et à traiter les données de façon structurée.

Le niveau Expert relie ces mécanismes aux exigences d'une exploitation professionnelle.

Vous avez étudié la découverte des capacités, les modèles YANG, l'architecture NMDA, les datastores opérationnels, les dépendances entre modules, la validation sémantique, les ETags, les préconditions, les modifications groupées, la sécurité, les stratégies de reprise, la concurrence, les notifications et les tests.

La qualité d'une automatisation ne se mesure pas uniquement au nombre d'équipements qu'elle peut interroger.

Elle se mesure à la capacité de répondre clairement aux questions suivantes :

- Pourquoi cette opération est-elle autorisée ?
- Pourquoi cette ressource a-t-elle été choisie ?
- Quelle version du modèle a été utilisée ?
- Que savons-nous réellement de l'état initial ?
- Comment détectons-nous un changement concurrent ?
- Quelles erreurs pouvons-nous retenter ?
- Comment déterminons-nous si un changement a réussi ?
- Quelles preuves permettent de comprendre le résultat ?
- Comment arrêtons-nous l'opération lorsque les conditions ne sont plus valides ?

La réponse ne vient pas uniquement de RESTCONF ou de NETCONF. Elle vient de l'architecture qui entoure ces protocoles : contrats de données, sécurité, gouvernance, tests, orchestration et observabilité.

**Règle finale du parcours :** aucune opération ne doit être exécutée hors de son périmètre autorisé ; aucune modification n'est considérée comme réussie sans validation de son résultat ; aucune incertitude ne doit être masquée par un statut de succès ; aucune stratégie de reprise ne doit supposer que l'opération initiale a échoué simplement parce que sa réponse n'a pas été reçue.

C'est cette maîtrise des opérations et de leurs conséquences qui transforme un client RESTCONF en une véritable plateforme d'automatisation réseau.