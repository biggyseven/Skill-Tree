# NAPALM — Niveau Expert

> **Fichier :** `napalm-expert.md`  
> **Parcours :** Automatisation réseau avec NAPALM — niveau 3 sur 3  
> **Prérequis :** avoir terminé `napalm-debutant.md` puis `napalm-intermediaire.md`, savoir écrire du Python structuré, utiliser un inventaire, collecter des données multi-équipements, comparer des instantanés, écrire des tests et préparer une configuration candidate.  
> **Révision documentaire :** 23 octobre 2026. Au moment de la vérification, PyPI et les versions publiées du dépôt officiel indiquaient NAPALM 5.2.0 comme dernière version publiée ; PyPI indiquait Python ≥ 3.10. Vérifiez néanmoins la version réellement installée, les dépendances du pilote choisi et les notes de version de votre environnement avant de déployer.  
> **Orientation :** ingénierie de production, gouvernance des changements, fiabilité, évolutivité et maîtrise du risque.


## 0. La place du niveau Expert dans le parcours

Ce document est **la suite directe** des deux niveaux précédents. Il ne recommence pas les bases et ne traite pas NAPALM comme une collection de commandes isolées. Le niveau Débutant a appris à se connecter, à lire quelques états et à préparer une configuration candidate. Le niveau Intermédiaire a transformé ces opérations en un outil structuré, avec inventaire, collecte multi-équipements, données normalisées, contrôles de conformité, tests et premiers garde-fous. Le niveau Expert traite la question suivante : **comment faire fonctionner cet outil durablement, sur un parc réel, malgré les pannes, les changements de topologie, les différences de pilotes et les exigences de sécurité ?**

Un système expert n'est pas celui qui pousse la configuration le plus vite. C'est celui qui sait refuser un changement dangereux, distinguer une panne de collecte d'une non-conformité, limiter le rayon d'impact d'une erreur, reprendre un travail interrompu sans le dupliquer et fournir des preuves vérifiables après chaque opération.

### 0.1 Contrat de progression

À la fin de ce niveau, vous devez savoir concevoir et défendre une architecture dans laquelle :

- l'inventaire, les intentions réseau et les changements sont représentés par des objets versionnés, validés et identifiables ;
- les secrets et les identités techniques sont gérés hors du code et avec des privilèges limités ;
- la capacité réelle de chaque pilote est connue, testée et versionnée ;
- les opérations de lecture sont résilientes sans transformer une erreur transitoire en charge incontrôlée ;
- les changements de configuration suivent une machine à états, exigent une approbation explicite et possèdent des conditions d'arrêt ;
- chaque lot de déploiement est limité en taille, surveillé et validé avant le lot suivant ;
- l'état observé est séparé de l'état attendu, et l'absence de donnée n'est jamais présentée comme la preuve d'une conformité ;
- les journaux, métriques, rapports et artefacts permettent de comprendre qui a lancé quoi, sur quel équipement, avec quel résultat et à partir de quel jeu de données ;
- les tests couvrent les scénarios nominaux, les échecs, les réponses partielles, les pertes de session et les ambiguïtés après application ;
- le système refuse de répéter aveuglément une opération d'écriture si son résultat précédent est incertain.

### 0.2 Carte du parcours complet

```text
NIVEAU 1 — DÉBUTANT
Connexion NAPALM → getters → candidat → diff → notions de sécurité
                         │
                         ▼
NIVEAU 2 — INTERMÉDIAIRE
Inventaire fiable → collecteur multi-équipements → normalisation → conformité
Tests unitaires → rapports → procédure de changement contrôlée
                         │
                         ▼
NIVEAU 3 — EXPERT (ce document)
Contrats d'API → capacités par pilote → orchestration résiliente → politiques
Déploiements canaris → validation après changement → reprise et audit
CI/CD → observabilité → tests de contrat → gouvernance → fiabilité de production
```

### 0.3 Ce qui est réutilisé, plutôt que réécrit

Vous devez déjà maîtriser les concepts suivants : `get_network_driver()`, le cycle `open()`/`close()`, les getters communs, les écarts entre pilotes, les inventaires YAML, les instantanés JSON, les exceptions isolées par appareil, le contrôle des interfaces et des voisins lorsque les getters sont pris en charge, la comparaison d'états, la préparation d'une configuration candidate, `compare_config()`, `discard_config()` et le principe selon lequel un commit doit être précédé de contrôles. Le niveau Expert réutilise ces idées et ajoute des contrats plus stricts autour d'elles.

Si vous n'avez pas encore séparé les données, la logique métier et les effets réseau, commencez par refactoriser votre solution intermédiaire. Ajouter des files de tâches, une API ou du parallélisme sur un script monolithique ne le rend pas expert : cela rend seulement ses défauts plus difficiles à maîtriser.

### 0.4 Règles pédagogiques et sécurité

Tous les exemples de configuration sont illustratifs. Les adresses des exemples appartiennent aux plages de documentation ou sont fictives. N'exécutez aucun laboratoire d'écriture sur un équipement de production. Les opérations de configuration seront montrées en deux temps : **préparer et inspecter**, puis décrire les conditions d'application. Les extraits qui appliquent effectivement une modification resteront séparés, marqués comme exemples de laboratoire et encadrés par des préconditions. Une capacité NAPALM peut dépendre du pilote, de sa version, du système d'exploitation réseau, de la version du système et parfois du type de transport. N'inférez donc jamais une capacité de production uniquement parce qu'une méthode existe dans l'API de base.


# 1. Passer d'un outil à une plateforme d'automatisation

## 1.1 Le changement de perspective

Au niveau Intermédiaire, une exécution peut encore être une commande lancée depuis un terminal qui parcourt l'inventaire et produit un rapport. En production, plusieurs personnes ou systèmes peuvent lancer une collecte en même temps, demander des changements concurrents, interrompre une exécution, renouveler des identifiants ou déployer des versions différentes de l'outil. Le réseau, lui, ne se met pas en pause pendant que le script redémarre.

Une plateforme d'automatisation doit répondre à des questions opérationnelles avant d'envoyer une commande :

1. **Identité :** quel équipement est visé, selon quelle source d'inventaire et à quelle version ?
2. **Intention :** quelle propriété réseau cherche-t-on à maintenir ou à modifier ?
3. **Autorisation :** l'identité qui exécute l'action a-t-elle le droit de le faire sur ce périmètre ?
4. **Préconditions :** les données sont-elles assez récentes et complètes pour décider ?
5. **Capacité :** le pilote prend-il en charge les méthodes et les mécanismes de sûreté requis ?
6. **Risque :** quels liens, clients ou services peuvent être affectés si l'opération échoue ?
7. **Exécution :** comment limiter la concurrence, le délai et le nombre d'équipements touchés ?
8. **Vérification :** quelles preuves indépendantes démontreront que le résultat attendu est réel ?
9. **Reprise :** que faut-il faire si le processus se termine ou si la session tombe après l'application ?
10. **Audit :** quels artefacts permettront de reconstruire la décision et le résultat ?

Si votre solution ne sait pas répondre à ces questions, elle peut rester un excellent outil de laboratoire, mais elle ne doit pas être qualifiée de plateforme de changement de production.

## 1.2 Architecture logique de référence

Une architecture solide distingue au moins le point d'entrée, l'orchestration, la politique, l'adaptateur NAPALM, le stockage et l'observabilité. Ces couches peuvent être des modules Python dans une première version ; elles n'ont pas besoin d'être immédiatement des microservices. La séparation logique importe davantage que le nombre de processus.

<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="590" viewBox="0 0 1120 590" role="img" aria-labelledby="napexp-arch-title napexp-arch-desc">
  <title id="napexp-arch-title">Architecture logique d'une plateforme NAPALM de production</title>
  <desc id="napexp-arch-desc">Le déclencheur soumet une demande à l'orchestrateur, qui consulte les politiques et passe par l'adaptateur NAPALM vers les équipements. L'inventaire alimente l'orchestrateur. Les résultats produisent des artefacts d'audit et des signaux d'observabilité.</desc>
  <defs><marker id="napexp-arch-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#9bb4d8"/></marker></defs>
  <rect x="1" y="1" width="1118" height="588" rx="16" fill="#0b1220" stroke="#27374e" stroke-width="2"/>
  <g stroke="#9bb4d8" stroke-width="2.8" fill="none" marker-end="url(#napexp-arch-arrow)"><path d="M205 91 H235"/><path d="M425 91 H455"/><path d="M645 91 H675"/><path d="M865 91 H895"/></g>
  <g>
    <rect x="25" y="50" width="180" height="82" rx="12" fill="#172c46" stroke="#54c5ef" stroke-width="1.7"/><text x="115" y="82" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Déclenchement</text><text x="115" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">CLI • API • CI/CD</text>
    <rect x="245" y="50" width="180" height="82" rx="12" fill="#20304d" stroke="#9baeff" stroke-width="1.7"/><text x="335" y="82" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Orchestrateur</text><text x="335" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">file • limites • états</text>
    <rect x="465" y="50" width="180" height="82" rx="12" fill="#2f244a" stroke="#c7a5ff" stroke-width="1.7"/><text x="555" y="82" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Politique et gates</text><text x="555" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">droits • risque • feu vert</text>
    <rect x="685" y="50" width="180" height="82" rx="12" fill="#183d37" stroke="#50d6b0" stroke-width="1.7"/><text x="775" y="82" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Adaptateur NAPALM</text><text x="775" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">pilote • session • getters</text>
    <rect x="905" y="50" width="180" height="82" rx="12" fill="#4a2b25" stroke="#ffb27a" stroke-width="1.7"/><text x="995" y="82" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Équipements</text><text x="995" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">routeurs • switches</text>
  </g>
  <path d="M135 240 V195 H335 V137" stroke="#5bd7bd" stroke-width="2.7" stroke-dasharray="8 7" fill="none" marker-end="url(#napexp-arch-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-30" dur="2.5s" repeatCount="indefinite"/></path>
  <text x="155" y="184" font-family="Arial,sans-serif" font-size="12" fill="#9ce9d8">inventaire versionné</text>
  <path d="M775 132 V205 H520 V236" stroke="#73b8ff" stroke-width="2.6" stroke-dasharray="7 6" fill="none" marker-end="url(#napexp-arch-arrow)"/>
  <path d="M995 132 V200 H937 V236" stroke="#73b8ff" stroke-width="2.6" fill="none" marker-end="url(#napexp-arch-arrow)"/>
  <g>
    <rect x="25" y="240" width="220" height="90" rx="12" fill="#153c3d" stroke="#50d6b0" stroke-width="1.7"/><text x="135" y="272" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Inventaire versionné</text><text x="135" y="296" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">identité • rôle • zone</text><text x="135" y="315" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">capacités • secret référencé</text>
    <rect x="405" y="240" width="230" height="90" rx="12" fill="#1d3149" stroke="#73b8ff" stroke-width="1.7"/><text x="520" y="272" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Audit et artefacts</text><text x="520" y="296" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">plans • diffs • résultats</text><text x="520" y="315" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">hash • horodatage</text>
    <rect x="790" y="240" width="295" height="90" rx="12" fill="#1d3149" stroke="#73b8ff" stroke-width="1.7"/><text x="937" y="272" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Observabilité</text><text x="937" y="296" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">logs • métriques • alertes</text><text x="937" y="315" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def2">suivi des vagues et des résultats</text>
  </g>
  <rect x="25" y="385" width="1060" height="155" rx="12" fill="#121e31" stroke="#334763" stroke-width="1.5"/>
  <text x="50" y="419" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#f3f7ff">Comment lire cette architecture</text>
  <text x="50" y="449" font-family="Arial,sans-serif" font-size="14" fill="#d2def2">1. Le flux principal va du déclenchement vers l'orchestrateur, la politique, l'adaptateur puis l'équipement.</text>
  <text x="50" y="475" font-family="Arial,sans-serif" font-size="14" fill="#d2def2">2. L'inventaire alimente l'orchestrateur ; il ne représente pas une commande envoyée aux équipements.</text>
  <text x="50" y="501" font-family="Arial,sans-serif" font-size="14" fill="#d2def2">3. Les artefacts d'audit et l'observabilité sont des sorties de la plateforme, pas des étapes de configuration.</text>
  <text x="50" y="523" font-family="Arial,sans-serif" font-size="13" fill="#9fb4d1">Les blocs représentent des responsabilités logiques ; ils peuvent être réunis dans un même processus.</text>
</svg>

Le diagramme représente des **responsabilités logiques**, pas nécessairement six services distincts. Dans un petit déploiement, l'orchestrateur, le moteur de politique et l'adaptateur peuvent vivre dans un même processus. Les interfaces doivent cependant rester distinctes afin que les tests puissent remplacer les connexions réseau par des doubles de test.

## 1.3 Structure de projet cible

Une structure de départ raisonnable ressemble à ceci :

```text
napalm-platform/
├── pyproject.toml
├── README.md
├── configs/
│   ├── inventory.example.yaml
│   └── policies/
├── src/
│   └── napalm_platform/
│       ├── __init__.py
│       ├── cli.py
│       ├── settings.py
│       ├── inventory.py
│       ├── capabilities.py
│       ├── secrets.py
│       ├── driver_factory.py
│       ├── collectors.py
│       ├── normalize.py
│       ├── snapshots.py
│       ├── policy.py
│       ├── changes.py
│       ├── rollout.py
│       ├── audit.py
│       └── observability.py
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── fixtures/
├── artifacts/                 # hors du dépôt Git
└── docs/
    ├── runbooks/
    └── decisions/
```

Chaque module doit avoir une raison claire d'exister. `driver_factory.py` construit le bon pilote, `collectors.py` réalise les lectures demandées, `normalize.py` traduit les résultats vers votre modèle interne, `policy.py` décide si les preuves satisfont les règles, et `changes.py` gère le cycle d'une modification. Le code de politique ne doit pas appeler directement `get_network_driver()` ; le code du pilote ne doit pas décider si un changement est autorisé par l'organisation.

### 1.3.1 Les frontières à protéger

- **Entrée utilisateur → orchestration :** convertir les paramètres en une demande validée, jamais exécuter directement une chaîne de commande arbitraire.
- **Orchestration → politique :** fournir des données datées, identifiées et suffisamment complètes ; ne pas demander à la politique d'interpréter des erreurs cachées.
- **Politique → adaptateur :** fournir un plan structuré, pas une décision implicite dissimulée dans une fonction d'exécution.
- **Adaptateur → NAPALM :** conserver la dépendance au pilote dans un endroit testable.
- **Résultat réseau → stockage :** normaliser les objets, retirer les secrets, ajouter horodatage et provenance, puis persister.
- **Exécution → audit :** conserver les étapes et les états même lorsqu'une exécution échoue.

## 1.4 Registre des décisions d'architecture

Les décisions qui affectent la sûreté doivent être documentées dans de courts ADR (*Architecture Decision Records*). Un ADR n'est pas un rapport marketing : il enregistre le contexte, les options, la décision, les conséquences et les conditions de réexamen.

Exemple de décision :

```text
ADR-004 — Aucun commit automatique en cas de résultat ambigu

Contexte : la session réseau peut tomber après que l'équipement a accepté une
configuration, mais avant que le client ne reçoive la réponse.

Décision : si l'issue d'une écriture est inconnue, marquer le changement UNKNOWN,
ne pas rejouer automatiquement la commande et lancer une réconciliation en lecture.

Conséquences : une intervention ou une vérification additionnelle peut être
nécessaire. En échange, on évite de dupliquer aveuglément une opération d'écriture.

Réexamen : après intégration d'une API de changement ayant une clé d'idempotence
et un état de transaction vérifiable.
```

Documentez également les limites de NAPALM sur votre parc : les méthodes autorisées, les profils de pilotes testés, les délais par plateforme, les formats de résultats, la stratégie de retour arrière et les cas non pris en charge. Cette documentation est un composant de l'architecture, pas une formalité.


# 2. Contrats de données, modèles et versionnement

## 2.1 Pourquoi le modèle interne compte plus que la forme brute

Les getters NAPALM fournissent des structures Python standardisées dans l'intention, mais les données disponibles peuvent varier selon les capacités du pilote et la plateforme. La forme exacte doit être vérifiée dans la documentation de la version et dans la matrice de prise en charge. Votre moteur métier ne doit donc pas distribuer partout des accès directs aux dictionnaires bruts. Il doit utiliser une couche de normalisation qui :

1. conserve les champs d'origine utiles pour le diagnostic ;
2. expose les propriétés métier minimales et stables ;
3. distingue « absent », « non pris en charge », « collecte échouée » et « valeur vide » ;
4. ajoute la provenance, l'heure et la version du contrat ;
5. refuse de transformer automatiquement une valeur inconnue en valeur correcte par défaut.

Une interface absente d'un dictionnaire n'est pas nécessairement une interface inexistante. Il peut s'agir d'un getter incomplet, d'un résultat partiel, d'un pilote qui ne fournit pas le champ, d'une erreur de parsing, ou d'un filtre intentionnel. Le contrat doit exprimer cette différence.

## 2.2 Enveloppe de résultat normalisée

Définissons une enveloppe pour chaque collecte. Elle est indépendante du getter et permet au reste de l'application de traiter les données avec les mêmes règles.

```python
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Literal

CollectionStatus = Literal[
    "ok", "partial", "unsupported", "failed", "stale"
]

@dataclass(frozen=True)
class CollectionEnvelope:
    schema_version: int
    device_id: str
    operation: str
    status: CollectionStatus
    started_at: str
    finished_at: str
    source_driver: str
    source_driver_version: str
    data: dict[str, Any] | None
    error_code: str | None = None
    error_type: str | None = None
    error_message_safe: str | None = None
    warnings: tuple[str, ...] = ()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def envelope_to_dict(envelope: CollectionEnvelope) -> dict[str, Any]:
    # Les tuples sont convertis en listes par cette fonction de normalisation
    # afin de produire du JSON déterministe.
    result = asdict(envelope)
    result["warnings"] = list(envelope.warnings)
    return result
```

Dans un vrai projet, `source_driver_version` provient de la version exacte du paquet ou du manifeste d'exécution, pas d'une chaîne écrite manuellement dans le code. `error_message_safe` doit être nettoyé : ne laissez pas une exception inclure une chaîne d'authentification, un nom d'utilisateur sensible ou une configuration complète. Les messages techniques bruts peuvent être conservés dans un journal à accès restreint si votre politique l'autorise, mais ils ne doivent jamais être injectés sans filtre dans un rapport destiné à un public large.

Le statut `partial` n'est pas un euphémisme pour « probablement correct ». Il dit qu'une partie des données a été obtenue, mais que le contrat ne peut pas garantir que tous les contrôles demandés ont été réalisés. `unsupported` signifie que la capacité est connue comme indisponible pour ce profil de pilote. `failed` désigne une exécution qui n'a pas produit de résultat exploitable. `stale` signifie que la donnée existe, mais ne satisfait pas les critères de fraîcheur de la décision demandée.

## 2.3 Distinguer les axes de résultat

Évitez un statut global binaire `success = True/False` pour toute l'opération. Une collecte peut être réussie et montrer un écart de conformité. Inversement, elle peut échouer sans permettre de conclure que l'équipement est non conforme. Séparez au minimum :

| Axe | Exemples de valeurs | Question résolue |
|---|---|---|
| État de transport | joignable, timeout, authentification refusée | Peut-on établir la session ? |
| État de collecte | complet, partiel, non pris en charge, échec | Les preuves demandées ont-elles été collectées ? |
| Résultat métier | conforme, non conforme, inconnu | Les preuves satisfont-elles la politique ? |
| Résultat de changement | préparé, appliqué, confirmé, annulé, inconnu | Où en est le changement ? |
| Niveau de risque | faible, moyen, élevé, critique | Quel niveau de contrôle est exigé ? |

Un bon rapport peut donc dire : « équipement joignable ; collecte BGP non prise en charge par ce profil ; conformité BGP indéterminée ; aucun changement exécuté ». Cela paraît moins simple qu'un feu vert, mais c'est beaucoup plus honnête opérationnellement.

## 2.4 Schéma de données versionné

Ajoutez une version de schéma aux instantanés et aux résultats persistés. Lorsque le contrat change, vous pourrez migrer les anciens artefacts ou les exclure explicitement des comparaisons incompatibles.

```json
{
  "schema_version": 2,
  "run_id": "run-2026-10-23T213000Z-a47c",
  "device": {
    "id": "edge-cm-01",
    "hostname_observed": "edge-cm-01",
    "role": "edge",
    "site": "douala-lab"
  },
  "collection": {
    "status": "ok",
    "started_at": "2026-10-23T21:30:01+00:00",
    "finished_at": "2026-10-23T21:30:03+00:00",
    "operations": ["get_facts", "get_interfaces", "get_bgp_neighbors"]
  },
  "software": {
    "napalm": "5.2.0",
    "driver": "example-driver",
    "driver_version": "recorded-by-runtime"
  },
  "data": {},
  "policy": {
    "name": "edge-baseline",
    "version": "3.4.0",
    "result": "unknown",
    "reasons": ["BGP getter not verified for this profile"]
  }
}
```

Les valeurs de ce document sont des exemples. Le champ `run_id` doit être créé au début d'une exécution et transmis à tous ses sous-résultats. Le nom du pilote réel est celui du registre NAPALM utilisé ; n'employez pas `example-driver` dans une configuration opérationnelle.

## 2.5 Canonicalisation et empreintes

Un hash d'instantané peut aider à détecter un doublon ou à prouver qu'un artefact n'a pas changé après génération. Il ne prouve pas que les données étaient exactes à l'origine. Pour obtenir une empreinte stable, il faut d'abord produire une représentation canonique : clés triées, encodage stable, valeurs normalisées et exclusion explicite des champs volatils qui ne font pas partie de la comparaison.

```python
import hashlib
import json
from typing import Any


def canonical_json_bytes(data: dict[str, Any]) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()
```

`allow_nan=False` force à traiter les nombres non conformes au JSON plutôt que de les sérialiser avec une extension tolérée par certains parseurs. Ne supprimez pas indistinctement les horodatages, versions et identifiants pour calculer une empreinte : définissez deux empreintes si nécessaire, une pour l'identité complète de l'artefact et une autre pour l'état métier comparable.

## 2.6 Compatibilité entre versions

Une comparaison entre deux instantanés est valide seulement si les données ont un périmètre comparable. Vérifiez au minimum :

- la version du schéma ;
- la liste des opérations exécutées ;
- la version de la politique ;
- l'identité stable de l'équipement ;
- le contexte de collecte (VRF, interfaces filtrées, familles d'adresses, etc.) ;
- la présence d'erreurs ou de valeurs partielles ;
- la fraîcheur des données et l'heure de collecte ;
- la version du pilote si elle influence la structure des résultats.

Si le schéma a changé, utilisez une migration explicite et testée ou refusez la comparaison. Une conversion improvisée pendant l'audit risque de transformer une différence de modèle en différence réseau.


# 3. Capabilities registry : connaître les limites réelles de chaque pilote

## 3.1 Une API uniforme n'est pas une garantie d'uniformité totale

NAPALM fournit une abstraction multi-constructeurs, mais l'ensemble des méthodes, la qualité des données et les mécanismes de changement diffèrent selon les pilotes, les versions de système réseau et parfois la configuration de transport. Les matrices officielles de prise en charge comportent des précautions et doivent être lues avec leurs notes. Elles sont une aide à la sélection, pas un substitut à un test sur la combinaison réellement déployée.

Le système expert doit donc traiter les capacités comme des données versionnées. Évitez les conditions dispersées du type `if driver_name == "..."` dans douze modules. Centralisez les profils et associez chaque capacité à une preuve : version testée, date de recette, type de transport, méthodes autorisées, résultat des tests d'intégration et restrictions connues.

## 3.2 Exemple de profil de capacités

```yaml
profiles:
  edge-os-a-netconf:
    napalm_driver: "nom-du-pilote-verifie"
    transport: "netconf"
    tested_software_ranges:
      - "version-minimum-et-maximum-valides-dans-votre-lab"
    read_operations:
      - get_facts
      - get_interfaces
      - get_interfaces_ip
      - get_lldp_neighbors
      - get_bgp_neighbors
    change_operations:
      candidate_merge: true
      candidate_replace: true
      compare_config: true
      commit_confirm: false
      rollback: "tested-only-in-lab"
    restrictions:
      - "Vérifier le format du diff avec la version cible"
      - "Ne pas inférer atomicité sans test documentaire et de laboratoire"
    validation:
      tested_at: "2026-10-10T11:15:00Z"
      test_suite_version: "capabilities-2.3.0"
      evidence_ref: "lab-run-00482"
```

Ce fichier est un modèle de gouvernance, non une déclaration de support pour un constructeur particulier. Remplacez les valeurs d'exemple par des données confirmées sur votre parc. La valeur `rollback: tested-only-in-lab` signifie qu'une capacité ne doit pas être considérée comme fiable en production avant une qualification appropriée.

## 3.3 Ne pas confondre présence, prise en charge et fiabilité

Il faut distinguer trois niveaux :

1. **Présence API :** la méthode existe sur l'objet ou dans la classe de base.
2. **Prise en charge déclarée :** la combinaison pilote/plateforme est annoncée comme prenant en charge la méthode.
3. **Capacité qualifiée :** votre propre recette confirme que le résultat, les erreurs, les effets et les limites correspondent au contrat attendu.

Seul le troisième niveau doit autoriser une opération critique de production. Une méthode peut être présente mais non implémentée utilement sur le pilote utilisé ; un getter peut fonctionner mais omettre un champ précis ; un diff peut être synthétique ; une fonction de rollback peut ne pas posséder les mêmes garanties qu'un mécanisme natif sur un autre système.

## 3.4 Vérifier les capacités au démarrage

La vérification ne doit pas forcément se connecter à chaque équipement au démarrage. Une stratégie courante consiste à valider la configuration locale et le profil testé, puis à confirmer la présence des méthodes nécessaires avant de créer une tâche. Le test d'intégration réel est exécuté dans une étape de qualification distincte.

```python
from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class RequiredCapabilities:
    getters: tuple[str, ...]
    needs_compare_config: bool = False
    needs_commit_confirm: bool = False


def verify_object_surface(
    driver: Any,
    required: RequiredCapabilities,
) -> list[str]:
    """Vérifie la surface Python, sans prétendre certifier la capacité réseau."""
    missing: list[str] = []
    for name in required.getters:
        if not callable(getattr(driver, name, None)):
            missing.append(name)
    if required.needs_compare_config and not callable(
        getattr(driver, "compare_config", None)
    ):
        missing.append("compare_config")
    if required.needs_commit_confirm:
        for name in ("has_pending_commit", "confirm_commit"):
            if not callable(getattr(driver, name, None)):
                missing.append(name)
    return missing
```

Ce code vérifie seulement la surface de l'objet. Il ne vérifie ni la réponse réelle de l'équipement ni l'effet d'une opération. Les capacités liées au changement doivent être issues du registre validé et de la recette du couple pilote/plateforme. Même si `has_pending_commit` existe, ne considérez pas le commit-confirm comme disponible sans confirmer les détails et limites de votre environnement.

## 3.5 Tests de contrat par profil

Pour chaque profil approuvé, créez une suite qui confirme :

- que les méthodes obligatoires renvoient les clés minimales attendues ;
- que les champs optionnels absents ne font pas échouer le normaliseur ;
- qu'une erreur d'authentification ou de transport est correctement classée ;
- que les noms d'interfaces et les identifiants de voisins sont normalisés de façon cohérente ;
- que le diff est significatif et stable pour des changements connus ;
- que les scénarios de chargement, d'abandon et de reprise fonctionnent dans le laboratoire ;
- que les délais de collecte sont mesurés ;
- que les versions du pilote et du système réseau sont enregistrées dans le résultat de recette.

Ne lancez pas ces tests de modification sur les équipements de production. Le jeu d'essai doit inclure une topologie isolée, un compte technique avec droits limités et un plan de restauration vérifié.


# 4. Secrets, identités et modèle de menace

## 4.1 La sécurité commence par les flux de données

Les identifiants ne se limitent pas au mot de passe fourni au constructeur NAPALM. Ils peuvent apparaître dans les variables d'environnement, les exceptions, les arguments de processus, les traces de débogage, les fichiers de configuration, les rapports CI, les artefacts de test ou un dump d'objet. Un système expert inventorie les endroits où les secrets peuvent transiter et décide à chaque frontière ce qui peut être conservé.

Les principaux risques sont :

- vol d'un compte technique capable de configurer le cœur du réseau ;
- exposition de secrets dans les journaux ou les artefacts CI ;
- exécution d'une action hors du périmètre autorisé ;
- attaque de type homme-du-milieu si l'identité de l'équipement n'est pas vérifiée ;
- utilisation d'un inventaire modifié par un acteur non autorisé ;
- rejeu involontaire d'une opération après un résultat ambigu ;
- approbation séparée du changement réellement appliqué ;
- modification du code ou de la politique entre la revue et l'exécution ;
- collecte excessive d'informations sensibles (configuration complète, utilisateurs, clés, communautés ou données client).

## 4.2 Identités techniques à privilège minimal

Séparez autant que possible les identités de lecture et d'écriture. Une tâche quotidienne de télémétrie n'a pas besoin d'un compte superutilisateur si un compte lecture suffit. Un compte de déploiement ne doit pas automatiquement pouvoir modifier tous les équipements et tous les domaines. Attribuez les droits par rôle, zone, classe d'équipement et type d'opération.

Une segmentation minimale peut ressembler à ceci :

| Identité | Fonctions autorisées | Interdictions typiques |
|---|---|---|
| `net-readonly` | getters nécessaires, collecte et audit | tout changement de configuration |
| `net-change-staging` | préparer les candidates en laboratoire | aucun accès à la production |
| `net-change-approved` | appliquer les changements approuvés sur une zone déterminée | modification hors périmètre ou sans identifiant de changement |
| `net-breakglass` | restauration exceptionnelle, accès contrôlé | usage quotidien et usage automatisé sans validation spécifique |

Les noms sont illustratifs. Le modèle réel doit s'aligner sur les capacités d'autorisation du système réseau. Le privilège minimum signifie aussi limiter les secrets à une durée de vie appropriée, révoquer les identités inutilisées, tracer les élévations de privilège et vérifier régulièrement les droits effectifs.

## 4.3 Intégrer un gestionnaire de secrets par interface

Évitez de coder un fournisseur précis dans le moteur de politique. Définissez une petite interface que l'implémentation peut relier à un coffre-fort, un gestionnaire de secrets d'entreprise ou un mécanisme de CI approuvé.

```python
from typing import Protocol


class SecretProvider(Protocol):
    def get_secret(self, reference: str) -> str:
        """Retourne le secret associé à une référence autorisée ou lève une erreur."""


def build_connection_parameters(device: dict, secrets: SecretProvider) -> dict:
    ref = device.get("credential_ref")
    if not isinstance(ref, str) or not ref:
        raise ValueError("Référence d'identifiant absente")

    # Ne jamais écrire la valeur renvoyée dans les logs.
    credential = secrets.get_secret(ref)
    if not credential:
        raise RuntimeError("Le fournisseur n'a pas fourni de secret utilisable")

    return {
        "hostname": device["hostname"],
        "username": device["username"],
        "password": credential,
        "timeout": device.get("timeout", 30),
        "optional_args": device.get("optional_args", {}),
    }
```

Une interface n'est sûre que si ses consommateurs le sont aussi. Le `dict` renvoyé contient un secret : ne le sérialisez pas pour le journaliser, ne l'ajoutez pas au message d'exception et ne le transmettez qu'au constructeur de session qui en a besoin. Préférez des objets de connexion non représentés en clair (`repr=False` pour un champ de dataclass) si vous créez un modèle de paramètres.

## 4.4 Vérification d'identité de l'équipement

Une connexion chiffrée n'est pas automatiquement une connexion à l'équipement attendu. Validez les clés hôtes SSH, les certificats TLS ou les mécanismes d'identité exposés par le transport. N'acceptez pas une nouvelle clé parce que « le script échoue sinon ». Une rotation de clé doit être un changement documenté dans l'inventaire ou dans l'infrastructure de confiance, avec une procédure de vérification indépendante.

Sur le plan opérationnel :

- gérez les clés hôtes ou certificats via une source de confiance ;
- surveillez les changements inattendus d'identité ;
- refusez les hôtes inconnus en environnement sensible ;
- documentez les options de vérification réellement employées par le pilote ;
- testez que l'environnement non interactif ne désactive pas silencieusement la validation ;
- ne désactivez pas la vérification d'identité pour résoudre un simple problème de déploiement.

Les options nécessaires varient selon le transport et le pilote. Consultez leur documentation exacte et testez la configuration effective, car passer une option au mauvais niveau peut ne produire aucun effet.

## 4.5 Nettoyage des journaux et des artefacts

Établissez une liste d'exclusion explicite : mots de passe, clés privées, tokens, chaînes de connexion, communautés SNMP, clés API, valeurs confidentielles d'`optional_args`, extraits de configuration contenant des secrets. Ne tentez pas de retirer seulement `password=` d'une chaîne : un secret peut être nommé autrement ou encodé dans une structure imbriquée.

Principes :

- journalisez les références de secret, jamais les valeurs ;
- enregistrez l'identité de l'exécuteur et le résultat sans exposer son jeton ;
- stockez les configurations brutes dans un espace d'accès restreint, chiffré et avec rétention définie ;
- gardez les rapports destinés aux utilisateurs séparés des traces de diagnostic ;
- appliquez un contrôle de taille et de durée de vie aux artefacts ;
- testez automatiquement les logs avec des chaînes-canaris correspondant à des faux secrets, et vérifiez qu'elles n'apparaissent pas dans les sorties.


# 5. Résilience : délais, tentatives, disjoncteurs et résultats incertains

## 5.1 Trois problèmes différents derrière un échec

Un échec d'opération réseau peut signifier trois choses très différentes :

1. **Échec certain avant effet :** l'opération n'a jamais atteint l'équipement ou a été rejetée avant toute modification.
2. **Échec certain avec effet absent :** la plateforme confirme que l'opération a été rejetée ou annulée.
3. **Résultat ambigu :** la commande a pu être appliquée, mais la connexion est tombée ou le client a expiré avant de recevoir une confirmation fiable.

Pour une lecture, un résultat ambigu peut souvent être corrigé par une nouvelle collecte. Pour une écriture, répéter la même commande peut être dangereux. Le système ne doit pas convertir toutes les exceptions en « retry » générique.

## 5.2 Définir les délais comme une enveloppe

Il existe généralement plusieurs délais distincts :

- **délai de connexion** : temps nécessaire pour établir la session ;
- **délai de commande** : attente maximale d'une opération sur l'équipement ;
- **délai d'une collecte** : somme des lectures prévues pour cet appareil ;
- **délai d'une tâche** : temps maximal alloué au traitement complet de cet appareil ;
- **délai de vague** : durée maximale de la phase d'un déploiement sur un lot ;
- **délai global** : budget temporel de la demande complète, incluant orchestration et écriture des artefacts.

Un délai de commande de 30 secondes n'implique pas qu'une collecte de 10 getters prendra au maximum 30 secondes. Définissez des budgets par opération et mesurés par profil de pilote. Ne placez pas arbitrairement un délai énorme « pour éviter les timeouts » : une tâche lente peut consommer un worker et retarder toutes les autres.

Une règle utile consiste à suivre les percentiles de durée plutôt que la seule moyenne. Si 95 % des lectures se terminent en 2 secondes et 5 % dépassent 45 secondes, la moyenne ne révèle pas à elle seule les problèmes d'exploitation. Surveillez P50, P90, P95 et P99, avec des dimensions raisonnables telles que profil de pilote, type d'opération et site. Évitez de créer une série métrique unique par nom d'interface ou numéro de série si cela crée une cardinalité incontrôlable.

## 5.3 Politique de retry par catégorie

| Opération | Retry automatique ? | Condition recommandée |
|---|---|---|
| Connexion de lecture | Souvent oui | erreur reconnue comme transitoire, nombre limité de tentatives |
| Getter idempotent | Parfois | uniquement si le délai global le permet et si la session est reconstruite proprement |
| Lecture de vérification après commit | Oui, de façon limitée | la vérification ne provoque pas de changement et l'état observé reste daté |
| Chargement d'une candidate | Pas universellement | uniquement si le pilote et l'état de candidate sont compris, avec nettoyage connu |
| Commit ou autre écriture | Pas de retry aveugle | le résultat précédent doit être réconcilié avant toute répétition |
| Rollback | Pas de répétition aveugle | déterminer si un retour arrière est déjà en cours ou terminé |

Le retry doit être explicable. Réessayez seulement les erreurs considérées comme transitoires par un profil et une politique documentés. Les erreurs d'authentification, de certificat, de paramètre invalide ou de droits insuffisants sont généralement des signaux à traiter, pas à marteler.

## 5.4 Backoff exponentiel avec jitter

Quand plusieurs workers réessaient simultanément après une panne, ils peuvent créer un effet de troupeau et aggraver la surcharge. Un délai croissant avec un aléa (« jitter ») aide à répartir la charge. Il doit être plafonné et respecter le délai global de la tâche.

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry_read(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 4.0,
    retryable: Callable[[Exception], bool],
) -> T:
    """Retry limité pour une lecture reconnue comme sûre à répéter.

    Ne pas utiliser cette fonction comme décorateur générique autour d'un commit.
    """
    if attempts < 1:
        raise ValueError("attempts doit être >= 1")
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as exc:
            is_last = attempt == attempts - 1
            if is_last or not retryable(exc):
                raise
            ceiling = min(max_delay, base_delay * (2 ** attempt))
            time.sleep(random.uniform(0.0, ceiling))
    raise RuntimeError("État inaccessible")  # protection défensive
```

La fonction `retryable` doit être fournie par votre adaptation, et ne devrait pas simplement retourner `True` pour chaque exception. Le `sleep()` convient à un worker synchrone isolé ; dans un orchestrateur asynchrone ou piloté par une file, utilisez un mécanisme d'attente qui ne bloque pas toute la boucle. Pour les changements de configuration, créez une politique dédiée à la réconciliation, pas un décorateur `retry` générique.

## 5.5 Disjoncteur (*circuit breaker*) et isolement des pannes

Si un site ou un groupe de routeurs ne répond plus, continuer à ouvrir des sessions à cadence élevée peut surcharger les équipements, la ligne d'administration ou le système d'automatisation. Un circuit breaker introduit trois états conceptuels :

- **CLOSED** : les requêtes passent normalement ; les échecs sont mesurés.
- **OPEN** : au-delà d'un seuil documenté, les nouvelles requêtes sont refusées temporairement ; le système n'insiste pas.
- **HALF_OPEN** : après une période d'attente, une ou quelques requêtes de test sont permises afin de vérifier si le service est revenu.

Appliquez le disjoncteur à une clé pertinente : appareil, site, profil de pilote ou service de gestion. Un disjoncteur global peut bloquer des équipements sains à cause d'un seul site ; un disjoncteur trop fin peut ne jamais détecter une panne commune. Choisissez la granularité à partir des dépendances de votre réseau d'administration.

Le circuit breaker ne remplace pas le timeout ou le quota. Le timeout borne la durée d'une opération ; le quota borne le volume de travail ; le disjoncteur suspend les requêtes vers une cible qui présente des échecs répétés.

## 5.6 Ne pas confondre erreur et absence d'information

Un résultat `None`, une collection vide et une exception ne sont pas interchangeables. Chaque getter doit avoir une interprétation documentée. Par exemple, une liste de voisins LLDP vide peut représenter un équipement sans voisin découvert, mais un échec d'appel LLDP n'est pas une liste vide. De même, une absence de voisin BGP dans un champ d'une réponse partielle ne doit pas être convertie en nombre de voisins égal à zéro sans validation du contrat.

Adoptez des règles de normalisation explicites :

```python
from dataclasses import dataclass
from typing import Any, Literal

ValueState = Literal["observed", "empty", "unsupported", "failed", "unknown"]

@dataclass(frozen=True)
class ObservedValue:
    state: ValueState
    value: Any = None
    reason: str | None = None


def classify_collection(*, supported: bool, succeeded: bool, value: Any) -> ObservedValue:
    if not supported:
        return ObservedValue("unsupported", reason="capability_not_enabled")
    if not succeeded:
        return ObservedValue("failed", reason="collection_failed")
    if value is None:
        return ObservedValue("unknown", reason="getter_returned_none")
    if value == {} or value == []:
        return ObservedValue("empty", value=value)
    return ObservedValue("observed", value=value)
```

Cette fonction n'est qu'un exemple générique ; le sens d'une valeur vide dépend du getter. `empty` ne veut pas dire « conforme » : c'est simplement une observation. La politique métier décide ensuite si le vide est attendu.


# 6. Orchestration multi-équipements à grande échelle

## 6.1 Le parallélisme doit être borné

Le niveau Intermédiaire a introduit le `ThreadPoolExecutor`. À grande échelle, la difficulté ne se limite plus à choisir `max_workers`. Il faut considérer le nombre de connexions par équipement, la limite de sessions imposée par les équipements, les ressources du serveur, le nombre de contrôleurs de management, la capacité du bastion, les contraintes par site et le caractère synchrone ou bloquant des pilotes.

Commencez avec une limite conservatrice. Augmentez-la seulement après avoir mesuré le temps de connexion, la durée des getters, les timeouts, les erreurs d'équipement et l'utilisation des ressources. Il est rarement utile de multiplier les workers si le plan d'administration ou les équipements saturent déjà.

## 6.2 Une concurrence à plusieurs niveaux

Une plateforme peut appliquer des limites en couches :

- **globale** : nombre maximum de tâches actives dans le processus ;
- **par site** : éviter qu'un site ne consomme tous les workers ;
- **par équipement** : empêcher deux changements concurrents sur la même cible ;
- **par opération** : limiter certaines lectures particulièrement coûteuses ;
- **par vague** : arrêter l'élargissement du déploiement tant que la vague actuelle n'est pas validée.

La limite globale seule ne garantit pas le comportement désiré. Par exemple, si les 20 premières tâches sont toutes des routeurs d'un même centre de données, il faut une contrainte par site pour préserver la capacité des autres zones. Les limites doivent être appliquées dans l'orchestrateur, pas uniquement dans les fonctions de collecte.

## 6.3 Exemple de collecte parallèle avec résultats isolés

Le code suivant fournit un modèle de collecte pour les opérations de lecture. Il ne doit pas être réutilisé tel quel pour des changements de configuration.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from time import monotonic
from typing import Any, Callable

@dataclass(frozen=True)
class DeviceTaskResult:
    device_id: str
    status: str
    duration_seconds: float
    data: dict[str, Any] | None = None
    error_type: str | None = None
    safe_message: str | None = None


def collect_one(device: dict, collect_fn: Callable[[dict], dict]) -> DeviceTaskResult:
    started = monotonic()
    device_id = str(device.get("id", "unknown"))
    try:
        result = collect_fn(device)
        if not isinstance(result, dict):
            raise TypeError("Le collecteur doit retourner un dictionnaire")
        return DeviceTaskResult(
            device_id=device_id,
            status="ok",
            duration_seconds=monotonic() - started,
            data=result,
        )
    except Exception as exc:
        # Le message du driver est volontairement omis à moins d'être nettoyé.
        return DeviceTaskResult(
            device_id=device_id,
            status="failed",
            duration_seconds=monotonic() - started,
            error_type=type(exc).__name__,
            safe_message="Échec de collecte ; consulter les traces restreintes.",
        )


def collect_many(
    devices: list[dict],
    collect_fn: Callable[[dict], dict],
    *,
    max_workers: int = 8,
) -> list[DeviceTaskResult]:
    if max_workers < 1:
        raise ValueError("max_workers doit être positif")
    output: list[DeviceTaskResult] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(collect_one, item, collect_fn): str(item.get("id", "unknown"))
            for item in devices
        }
        for future in as_completed(futures):
            # collect_one is designed not to leak ordinary device failures out.
            # This branch still protects the orchestrator from programming errors.
            try:
                output.append(future.result())
            except Exception:
                output.append(DeviceTaskResult(
                    device_id=futures[future],
                    status="internal_error",
                    duration_seconds=0.0,
                    safe_message="Échec interne du worker.",
                ))
    return output
```

Ce modèle isole les erreurs par appareil, mais il n'implémente pas à lui seul des quotas par site, une file persistante ou une limite de durée globale. En outre, annuler un `Future` ne garantit pas qu'un appel bloqué dans un pilote sera interrompu immédiatement. Les délais du client réseau restent nécessaires. Surveillez la fermeture des sessions même quand une exception survient.

## 6.4 Une file de tâches pour les exécutions durables

Quand une exécution doit survivre au redémarrage d'un worker, une file en mémoire ne suffit plus. Une file persistante ou une table de tâches doit enregistrer au minimum :

- identifiant stable de tâche ;
- type de travail (collecte, audit, préparation, déploiement, vérification) ;
- périmètre d'équipements et version de l'inventaire ;
- version de code et de politique ;
- état courant et dernière transition ;
- heure de création, échéance et nombre de tentatives ;
- identifiant de changement ou de demande ;
- statut de l'approbation lorsque nécessaire ;
- références vers les artefacts de preuve.

N'enregistrez pas les secrets dans la file. Celle-ci stocke une référence au secret et un identifiant d'exécution. La tâche doit revalider ses autorisations et ses préconditions lors de l'exécution : une tâche approuvée hier peut ne plus être sûre aujourd'hui si l'inventaire a changé, si l'appareil a été déplacé de zone ou si la fenêtre de maintenance est terminée.

## 6.5 Idempotence au niveau de l'orchestration

Une opération d'orchestration est idempotente si répéter la demande n'entraîne pas de duplication indésirable. Définissez une clé à partir des éléments qui déterminent réellement le travail, par exemple : identifiant de demande, appareil, version de candidat, version de politique et phase. N'utilisez pas seulement l'heure actuelle comme identifiant : un retry créerait une nouvelle clé et pourrait lancer le même changement une deuxième fois.

Il faut distinguer :

- **idempotence de demande** : un double clic ou une répétition HTTP ne crée pas deux travaux ;
- **idempotence de préparation** : la préparation produit la même candidate pour les mêmes entrées ;
- **idempotence de changement** : répéter l'action ne cause pas de modification additionnelle indésirable ;
- **idempotence de vérification** : la lecture peut être répétée sans effet secondaire.

Il est plus facile d'assurer l'idempotence d'une demande que celle d'une opération réseau. Votre couche d'orchestration doit empêcher les doublons évidents, mais elle ne doit jamais supposer que le constructeur a appliqué ou non un commit uniquement parce qu'une tâche a perdu sa connexion.

## 6.6 Verrouillage des changements concurrents

Deux demandes peuvent viser le même équipement à quelques secondes d'intervalle. Un verrou local protège un seul processus ; il ne protège pas plusieurs workers sur plusieurs serveurs. Pour une plateforme distribuée, utilisez un mécanisme de verrouillage partagé ou une file qui garantit un seul changement actif par équipement. Le verrou doit être acquis avant la phase de préconditions et garder une durée de vie appropriée, avec un mécanisme de bail si un worker disparaît.

Cependant, ne confondez pas un verrou de votre application avec le verrou de configuration natif de l'équipement. Les deux répondent à des problèmes différents : le premier coordonne les processus de votre plateforme ; le second protège potentiellement une candidate ou une session de configuration sur l'appareil. La prise en charge du verrou natif varie selon le pilote.

Recommandations :

1. définir une clé de verrou stable par équipement et, si besoin, par domaine de configuration ;
2. refuser un deuxième changement si le premier est dans un état actif ou ambigu ;
3. associer le verrou à l'identifiant du changement ;
4. renouveler un bail tant que la tâche est réellement active ;
5. ne pas libérer le verrou à la simple expiration du worker si une modification peut rester en suspens ;
6. réconcilier l'état de l'équipement avant de laisser entrer une nouvelle écriture après un crash.

## 6.7 Contrôle de pression et arrêt d'urgence

Une plateforme expert possède un mécanisme d'arrêt global et des mécanismes d'arrêt partiel : suspendre les nouvelles écritures, arrêter l'extension des lots, mettre un profil de pilote en quarantaine ou interrompre les collectes non essentielles vers un site en incident. L'arrêt d'urgence doit être indépendant du code de changement en cours autant que possible.

Définissez clairement les effets du bouton d'arrêt : bloque-t-il seulement les nouveaux travaux, annule-t-il les candidats non commis, tente-t-il un rollback, ou place-t-il les changements en état `UNKNOWN` ? Il serait dangereux de supposer qu'un arrêt logiciel arrête une opération déjà acceptée par l'équipement. La politique d'urgence doit faire partie des répétitions de simulation d'incident.


# 7. Collecte avancée, fraîcheur et cohérence temporelle

## 7.1 Une collecte n'est pas un instantané atomique

Une série de getters est généralement constituée d'appels distincts. Les interfaces peuvent changer entre `get_interfaces()` et `get_interfaces_counters()`, un voisin BGP peut se réinitialiser entre deux lectures, et l'inventaire peut être mis à jour pendant une longue exécution. L'instantané obtenu représente donc une fenêtre de temps, pas nécessairement un état atomique de l'appareil.

Le système doit enregistrer l'heure de début et de fin de chaque opération, pas uniquement l'heure de démarrage du processus. Quand une règle métier compare plusieurs domaines, fixez une limite de décalage acceptable. Par exemple, une décision de bascule peut exiger que les informations de deux routeurs soient collectées dans une fenêtre de quelques secondes, tandis qu'un audit de conformité hebdomadaire peut tolérer une fenêtre de plusieurs minutes.

## 7.2 Fraîcheur par politique

La fraîcheur doit dépendre de l'usage. Une donnée âgée de dix minutes peut rester utile pour une version logicielle, mais être dangereusement ancienne pour confirmer l'état d'une session BGP après un changement.

```python
from datetime import datetime, timezone


def is_fresh(timestamp: datetime, max_age_seconds: int, *, now=None) -> bool:
    if timestamp.tzinfo is None:
        raise ValueError("Les horodatages doivent inclure un fuseau horaire")
    current = now or datetime.now(timezone.utc)
    age = (current - timestamp.astimezone(timezone.utc)).total_seconds()
    # Une date dans le futur indique probablement un problème d'horloge ou de donnée.
    if age < -2:
        return False
    return age <= max_age_seconds
```

L'exemple considère qu'un décalage futur supérieur à deux secondes invalide la fraîcheur ; ce seuil est un paramètre à adapter. Ne manipulez pas des horodatages naïfs en supposant qu'ils sont en UTC. Vérifiez également la synchronisation de l'horloge des serveurs d'automatisation : les timestamps incohérents compromettent les audits, la corrélation des événements et l'analyse des délais.

## 7.3 Snapshot complet ou snapshot delta

Un snapshot complet facilite la reconstitution de l'état, mais il peut être coûteux et stocker des données sensibles. Un delta réduit le volume, mais il est plus difficile à reconstruire si un événement est perdu ou mal ordonné. Une architecture courante conserve des snapshots périodiques et des événements de changement entre les deux.

Le choix doit tenir compte de :

- la capacité de stockage et la durée de rétention ;
- la fréquence des changements ;
- la sensibilité des configurations et données ;
- le coût de reconstruction historique ;
- l'exigence de preuve après incident ;
- la nécessité de détecter une dérive non provoquée par la plateforme.

Si vous stockez des configurations complètes, traitez-les comme des données sensibles. Si vous ne stockez que des hashes, vous ne pourrez pas toujours expliquer le contenu d'une dérive. Une politique de données peut conserver un diff nettoyé accessible à un groupe limité et une empreinte plus largement consultable.

## 7.4 Corrélation des données entre appareils

Les états réseau s'interprètent souvent en relation avec plusieurs équipements : voisins LLDP, sessions BGP, liens redondants, circuits, VRF ou appartenances de zone. Une collecte réussie sur un seul routeur ne suffit pas à conclure qu'un chemin entier est disponible.

Chaque relation doit être associée à une source de vérité : inventaire, protocole découvert ou référentiel de services. Par exemple, un voisin attendu de l'inventaire peut être comparé au résultat LLDP observé, mais un voisin LLDP ne définit pas nécessairement l'intention métier. Le système doit également distinguer les noms d'interface locaux, les interfaces normalisées et les identifiants physiques ou logiques de circuits.

Construisez une couche topologique qui peut répondre à des questions telles que : « quels équipements et services risquent d'être affectés si ce lien est indisponible ? » Elle ne doit pas supposer que chaque lien découvert est un lien métier ni que chaque lien métier dispose d'un voisin LLDP visible.

## 7.5 État inconnu et mode de sécurité par défaut

Dans une décision importante, « inconnu » doit généralement empêcher une écriture. Cela ne signifie pas qu'une collecte ratée doit rendre l'organisation incapable de travailler : cela signifie que l'automatisation demande une nouvelle preuve, une analyse ou une approbation exceptionnelle au lieu de transformer l'absence de preuve en feu vert.

Adoptez une matrice explicite :

| Precondition | Comportement expert typique |
|---|---|
| Toutes les données critiques sont présentes et fraîches | poursuivre si les autres conditions sont satisfaites |
| Donnée non critique absente | poursuivre avec avertissement si la politique le permet |
| Donnée critique ancienne | relancer la lecture, puis bloquer si elle reste ancienne |
| Getter requis non pris en charge | bloquer le scénario qui dépend de ce getter ou utiliser une preuve approuvée équivalente |
| Collecte échouée | ne pas conclure conforme ; interrompre le changement qui exige cette preuve |
| Horodatage ou identité incohérents | quarantaine de l'artefact et investigation |

Cette matrice est une politique de sûreté, pas une règle NAPALM. Chaque équipe doit préciser les données critiques pour ses propres changements.


# 8. Construire un moteur de politique explicite

## 8.1 Le moteur de politique ne doit pas être un ensemble de `if` dispersés

Au niveau Expert, les règles d'exploitation doivent être lisibles, versionnées, testables et évaluées de manière reproductible. Une politique exprime ce qui est autorisé dans un contexte donné. Elle ne doit pas se cacher dans la fonction qui ouvre une connexion réseau ou dans une condition ajoutée au dernier moment avant un commit.

Une bonne politique comprend :

- son nom, son identifiant stable et sa version ;
- le périmètre d'équipement auquel elle s'applique ;
- les preuves exigées et leurs délais de fraîcheur ;
- les seuils de risque et les conditions d'approbation ;
- les états d'entrée possibles et la signification d'une valeur absente ;
- la décision produite (autoriser, refuser, demander une nouvelle preuve, exiger une approbation) ;
- les raisons lisibles associées à la décision ;
- les tests de régression correspondant aux cas normaux et aux exceptions.

Une politique qui renvoie `False` sans expliquer pourquoi complique l'exploitation. Une politique qui renvoie `True` lorsque des preuves sont absentes crée un défaut de sécurité. Préférez une décision structurée plutôt qu'un booléen.

## 8.2 Modèle de décision

```python
from dataclasses import dataclass
from typing import Literal

DecisionAction = Literal["allow", "deny", "need_evidence", "need_approval"]

@dataclass(frozen=True)
class PolicyDecision:
    action: DecisionAction
    policy_name: str
    policy_version: str
    reasons: tuple[str, ...]
    required_approvals: tuple[str, ...] = ()
    risk_level: str = "unknown"


def require_fresh_bgp(
    *,
    collection_status: str,
    age_seconds: float | None,
    max_age_seconds: int,
    established_neighbors: int | None,
    minimum_neighbors: int,
) -> PolicyDecision:
    policy_name = "edge-bgp-precondition"
    policy_version = "1.0.0"

    if collection_status in {"unsupported", "failed", "partial", "stale"}:
        return PolicyDecision(
            action="need_evidence",
            policy_name=policy_name,
            policy_version=policy_version,
            reasons=("La preuve BGP est absente, partielle ou invalide",),
        )
    if age_seconds is None or age_seconds > max_age_seconds:
        return PolicyDecision(
            action="need_evidence",
            policy_name=policy_name,
            policy_version=policy_version,
            reasons=("La preuve BGP est trop ancienne ou sans horodatage",),
        )
    if established_neighbors is None:
        return PolicyDecision(
            action="need_evidence",
            policy_name=policy_name,
            policy_version=policy_version,
            reasons=("Le nombre de voisins établis est indéterminé",),
        )
    if established_neighbors < minimum_neighbors:
        return PolicyDecision(
            action="deny",
            policy_name=policy_name,
            policy_version=policy_version,
            reasons=("Le seuil minimum de voisins établis n'est pas satisfait",),
            risk_level="high",
        )
    return PolicyDecision(
        action="allow",
        policy_name=policy_name,
        policy_version=policy_version,
        reasons=("Les préconditions BGP déclarées sont satisfaites",),
        risk_level="medium",
    )
```

Le nombre de voisins doit avoir été calculé à partir d'un contrat de données du profil ciblé. Les exemples ne déterminent pas à eux seuls quel seuil est correct pour un site : un routeur de laboratoire, un routeur de bordure redondé et un routeur de transit peuvent avoir des exigences différentes. La version de politique est attachée à la décision afin qu'un audit sache exactement quelle règle a été évaluée.

## 8.3 Policy-as-code et données de politique

Une équipe peut exprimer les paramètres variables en YAML et conserver la logique de calcul en Python :

```yaml
policy:
  name: edge-change-safety
  version: "3.1.0"
  scope:
    roles: [edge]
    environments: [lab, staging, production]
  evidence:
    bgp:
      required: true
      max_age_seconds: 90
      minimum_established_neighbors: 2
    interfaces:
      required: true
      max_age_seconds: 90
    inventory:
      require_current_revision: true
  change:
    require_ticket: true
    require_second_approver_for_risk: high
    max_devices_per_canary_wave: 1
    stop_on_unknown_result: true
```

Ce document représente une forme de politique possible ; les clés ne sont pas une syntaxe NAPALM native. Votre application doit valider la structure, les types, les seuils et les valeurs autorisées. L'utilisateur ne doit pas pouvoir remplacer `max_devices_per_canary_wave` ou lever l'exigence d'approbation via un paramètre caché de la CLI sans droits spécifiques.

Ne mettez pas de secret ou de donnée personnelle inutile dans la politique. Les valeurs de seuil doivent être expliquées et revues comme du code. Un changement de seuil peut modifier les risques de l'ensemble du parc et doit suivre le même processus de revue que les autres règles critiques.

## 8.4 Score de risque : utile, mais jamais magique

Une note chiffrée peut aider à classer un changement, mais elle ne remplace pas des règles bloquantes. Par exemple, il est raisonnable de combiner l'étendue du changement, le rôle de l'équipement, sa criticité, l'incertitude du diff et les résultats des contrôles. En revanche, une preuve critique absente ne doit pas être compensée par une faible note sur d'autres dimensions.

Un modèle possible :

| Dimension | Exemple de facteur | Question |
|---|---|---|
| Rayon d'impact | un appareil / un site / plusieurs régions | Combien de services peuvent être touchés ? |
| Criticité | labo / accès / distribution / cœur | Quelle est la gravité potentielle ? |
| Incertitude | diff connu / diff ambigu / données incomplètes | Comprenons-nous ce qui va changer ? |
| Réversibilité | rollback testé / procédure manuelle / aucune garantie | Peut-on restaurer l'état antérieur ? |
| Exposition | management isolé / route de management dépendante du changement | Le changement peut-il couper son propre accès ? |
| Fenêtre | maintenance approuvée / période interdite | Le changement peut-il être absorbé ? |

Utilisez des seuils explicites qui déclenchent des contrôles. Le résultat « risque faible » n'autorise pas à ignorer la liste des interdictions. Les critères d'approbation doivent être vérifiables et ne pas dépendre seulement d'un jugement subjectif du demandeur.

## 8.5 Contrat de décision : raisons et preuves

Chaque résultat de politique doit inclure les références vers les preuves utilisées : identifiants d'instantanés, horodatages, hash de l'inventaire, version de la politique, version du profil de capacités et résultats de contrôles. Les raisons doivent être assez claires pour être comprises par un opérateur, tout en évitant de recopier des secrets ou des configurations complètes.

Une décision n'est pas une preuve par elle-même. Le rapport doit permettre de remonter de « autorisé » vers les données de base, de vérifier leur fraîcheur et de reproduire la règle. Si l'artefact manque, si l'horodatage est incohérent ou si la version de politique n'est pas disponible, signalez explicitement que la décision ne peut pas être reconstruite complètement.


# 9. Gestion des changements comme machine à états

## 9.1 Pourquoi un simple `try/except` est insuffisant

Le déploiement d'une configuration comporte plusieurs phases : validation de la demande, collecte des préconditions, rendu du candidat, préparation sur l'équipement, inspection du diff, approbation, application, vérification et clôture. Chaque phase peut échouer différemment. Un processus peut aussi être interrompu entre deux étapes ou perdre sa connexion au moment le plus critique.

Un code de la forme suivante est trop faible pour un changement de production :

```python
try:
    device.load_merge_candidate(config=payload)
    device.commit_config()
except Exception:
    print("Échec")
```

Il ne permet pas de savoir si la candidate est chargée, si le commit a été envoyé, si l'équipement a appliqué la modification, si le transport a perdu seulement la réponse ou si une configuration est encore en attente. Il risque également d'oublier la fermeture de session ou l'abandon d'une candidate.

## 9.2 États recommandés

Voici un modèle d'états de changement :

- `REQUESTED` : la demande est enregistrée mais pas encore validée ;
- `VALIDATED` : l'inventaire, le profil, le bundle et la portée sont valides ;
- `PREFLIGHT_OK` : les preuves préalables satisfont la politique ;
- `PREPARED` : la candidate a été chargée et un diff a été conservé ;
- `AWAITING_APPROVAL` : le changement attend l'approbation requise ;
- `APPROVED` : l'approbation porte sur la bonne version du candidat et du diff ;
- `APPLYING` : l'opération d'écriture a commencé ;
- `VERIFYING` : les contrôles post-changement sont en cours ;
- `CONFIRMED` : le résultat attendu est observé et le changement peut être clôturé ;
- `ABORTED` : le changement a été arrêté avant application ou la candidate a été abandonnée ;
- `ROLLED_BACK` : le retour arrière a été effectué et vérifié ;
- `FAILED` : l'échec est connu et les impacts sont compris ;
- `UNKNOWN` : l'état d'application n'est pas certain et une réconciliation est nécessaire.

`UNKNOWN` est essentiel. Une plateforme mature ne le remplace pas par `FAILED` pour des raisons esthétiques. Une écriture peut avoir réussi côté équipement et échoué côté client ; l'état inconnu exige une lecture indépendante avant toute nouvelle écriture.

<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="690" viewBox="0 0 1120 690" role="img" aria-labelledby="napexp-sm-title napexp-sm-desc">
  <title id="napexp-sm-title">Machine à états cohérente d'un changement NAPALM</title>
  <desc id="napexp-sm-desc">Le flux normal est REQUESTED, VALIDATED, PREFLIGHT_OK, PREPARED, APPROVED, APPLYING, VERIFYING, CONFIRMED. Un refus préalable conduit à ABORTED. Un échec établi conduit à FAILED. Si l'application est ambiguë, UNKNOWN mène à RECONCILIATION et ne retourne jamais directement vers APPLYING.</desc>
  <defs><marker id="napexp-sm-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#9bb4d8"/></marker></defs>
  <rect x="1" y="1" width="1118" height="688" rx="16" fill="#0b1220" stroke="#27374e" stroke-width="2"/>
  <g stroke="#9bb4d8" stroke-width="2.7" fill="none" marker-end="url(#napexp-sm-arrow)"><path d="M160 95 H185"/><path d="M335 95 H360"/><path d="M520 95 H545"/><path d="M695 95 H720"/><path d="M870 95 H890"/><path d="M990 130 V185"/><path d="M895 225 H850"/></g>
  <path d="M990 130 V185" stroke="#50d6b0" stroke-width="2.7" stroke-dasharray="6 7" fill="none"><animate attributeName="stroke-dashoffset" from="0" to="-28" dur="2.2s" repeatCount="indefinite"/></path>
  <path d="M895 225 H850" stroke="#50d6b0" stroke-width="2.7" stroke-dasharray="6 7" fill="none"><animate attributeName="stroke-dashoffset" from="0" to="-28" dur="2.2s" repeatCount="indefinite"/></path>
  <g>
    <rect x="20" y="60" width="140" height="70" rx="10" fill="#172c46" stroke="#65c9ef" stroke-width="1.6"/><text x="90" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">REQUESTED</text><text x="90" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">demande créée</text>
    <rect x="190" y="60" width="145" height="70" rx="10" fill="#172c46" stroke="#65c9ef" stroke-width="1.6"/><text x="262" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">VALIDATED</text><text x="262" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">périmètre accepté</text>
    <rect x="365" y="60" width="155" height="70" rx="10" fill="#173d39" stroke="#54d6b0" stroke-width="1.6"/><text x="442" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f3f7ff">PREFLIGHT_OK</text><text x="442" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">preuves fraîches</text>
    <rect x="545" y="60" width="150" height="70" rx="10" fill="#173d39" stroke="#54d6b0" stroke-width="1.6"/><text x="620" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">PREPARED</text><text x="620" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">diff conservé</text>
    <rect x="720" y="60" width="150" height="70" rx="10" fill="#382d1b" stroke="#f5c36a" stroke-width="1.6"/><text x="795" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">APPROVED</text><text x="795" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">même bundle et diff</text>
    <rect x="895" y="60" width="190" height="70" rx="10" fill="#4b2928" stroke="#ff9e8a" stroke-width="1.6"/><text x="990" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">APPLYING</text><text x="990" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">écriture lancée</text>
    <rect x="895" y="185" width="190" height="75" rx="10" fill="#4b2928" stroke="#ff9e8a" stroke-width="1.6"/><text x="990" y="216" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">VERIFYING</text><text x="990" y="238" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">postchecks métier</text>
    <rect x="680" y="190" width="165" height="70" rx="10" fill="#173d39" stroke="#54d6b0" stroke-width="1.6"/><text x="762" y="218" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">CONFIRMED</text><text x="762" y="239" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">résultat prouvé</text>
    <rect x="70" y="190" width="160" height="70" rx="10" fill="#3d2028" stroke="#ff8296" stroke-width="1.6"/><text x="150" y="218" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">ABORTED</text><text x="150" y="239" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">refus avant écriture</text>
    <rect x="260" y="300" width="170" height="70" rx="10" fill="#3d2028" stroke="#ff8296" stroke-width="1.6"/><text x="345" y="328" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">FAILED</text><text x="345" y="349" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">échec établi</text>
  </g>
  <path d="M262 130 V158 H150 V185" stroke="#ff8296" stroke-width="2.5" fill="none" marker-end="url(#napexp-sm-arrow)"/>
  <path d="M990 260 V278 H345 V295" stroke="#ff8296" stroke-width="2.5" fill="none" marker-end="url(#napexp-sm-arrow)"/>
  <path d="M1085 95 H1100 V377 H1085" stroke="#ffb27a" stroke-width="3" stroke-dasharray="8 7" fill="none" marker-end="url(#napexp-sm-arrow)"/>
  <text x="824" y="305" font-family="Arial,sans-serif" font-size="12" fill="#ffc99d">session perdue / résultat ambigu</text>
  <rect x="820" y="345" width="260" height="64" rx="11" fill="#482b20" stroke="#ffb27a" stroke-width="1.8"/><text x="950" y="372" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#fff4e8">UNKNOWN</text><text x="950" y="393" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#f2d8c3">ne pas réappliquer en aveugle</text>
  <path d="M950 409 V440" stroke="#9bb4d8" stroke-width="2.6" fill="none" marker-end="url(#napexp-sm-arrow)"/>
  <rect x="820" y="445" width="260" height="68" rx="11" fill="#1c3147" stroke="#76baff" stroke-width="1.8"/><text x="950" y="473" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">RECONCILIATION</text><text x="950" y="494" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d0def3">lecture indépendante</text>
  <path d="M950 513 V540" stroke="#9bb4d8" stroke-width="2.6" fill="none" marker-end="url(#napexp-sm-arrow)"/>
  <rect x="600" y="545" width="480" height="112" rx="11" fill="#121e31" stroke="#334763" stroke-width="1.5"/><text x="622" y="570" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Décision après réconciliation</text><text x="622" y="593" font-family="Arial,sans-serif" font-size="12.5" fill="#d2def2">État attendu prouvé → CONFIRMED</text><text x="622" y="613" font-family="Arial,sans-serif" font-size="12.5" fill="#d2def2">Retour arrière exécuté et vérifié → ROLLED_BACK</text><text x="622" y="633" font-family="Arial,sans-serif" font-size="12.5" fill="#d2def2">Échec compris → FAILED ; preuve insuffisante → UNKNOWN + escalade</text>
  <rect x="25" y="395" width="550" height="250" rx="12" fill="#111f32" stroke="#344862" stroke-width="1.5"/><text x="50" y="428" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Invariants de sécurité</text><text x="50" y="460" font-family="Arial,sans-serif" font-size="13" fill="#d0def3">• APPROVED reste valide seulement pour le même bundle et le même diff.</text><text x="50" y="491" font-family="Arial,sans-serif" font-size="13" fill="#d0def3">• UNKNOWN doit passer par une lecture indépendante et une réconciliation.</text><text x="50" y="522" font-family="Arial,sans-serif" font-size="13" fill="#d0def3">• FAILED signifie que l'échec est compris ; il ne prouve pas l'absence d'écriture.</text><text x="50" y="553" font-family="Arial,sans-serif" font-size="13" fill="#d0def3">• ABORTED s'applique uniquement si l'écriture n'a pas commencé.</text><text x="50" y="584" font-family="Arial,sans-serif" font-size="13" fill="#d0def3">• Tout rollback doit lui-même être vérifié et audité.</text><text x="50" y="615" font-family="Arial,sans-serif" font-size="12.5" fill="#9fb4d1">Les transitions exactes doivent être persistées et testées dans l'application.</text>
</svg>

## 9.3 Transitions autorisées et invariants

Une transition doit vérifier que l'état précédent autorise le nouvel état. La transition `PREPARED → APPROVED` ne devrait pas être permise si le candidat, l'inventaire ou la politique ont changé depuis la revue. La transition `APPLYING → CONFIRMED` devrait être impossible sans contrôles de validation réussis et preuves enregistrées.

Un ensemble d'invariants utiles :

- chaque changement possède un identifiant stable et une clé d'idempotence ;
- chaque transition est horodatée et reliée à l'identité de l'acteur ou du worker ;
- la demande approuvée pointe vers le hash du candidat, du diff et de la politique ;
- un changement ne démarre pas si un autre changement incompatible tient un verrou sur le même appareil ;
- une fois l'écriture démarrée, toute interruption peut mener à `UNKNOWN` ;
- `UNKNOWN` exige une réconciliation en lecture avant une nouvelle écriture ;
- le système ne peut pas déclarer `CONFIRMED` si une preuve obligatoire est `failed`, `unsupported` ou `stale` ;
- un abandon de candidate et une restauration sont enregistrés séparément de la clôture métier.

## 9.4 Approver la bonne chose

L'approbation doit être liée à un objet immuable. Si l'opérateur approuve un diff, puis qu'un template, un inventaire ou une valeur de variable change, l'ancien accord ne doit pas approuver le nouveau candidat par accident.

En pratique, enregistrez :

```json
{
  "change_id": "CHG-2026-1042",
  "candidate_hash": "sha256:...",
  "diff_hash": "sha256:...",
  "inventory_revision": "inv-2026-10-23.4",
  "policy_revision": "edge-change-safety@3.1.0",
  "capability_profile_revision": "edge-os-a-netconf@2.3.0",
  "approver_id": "operator-17",
  "approved_at": "2026-10-23T19:40:00Z",
  "valid_until": "2026-10-23T20:10:00Z"
}
```

Les identifiants sont fictifs et l'exemple ne représente pas un format standard NAPALM. La plateforme doit invalider l'approbation dès que le contenu couvert par le hash change, que sa durée de validité expire ou qu'une précondition critique est modifiée.

## 9.5 Exemple d'interface de stockage des transitions

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

@dataclass(frozen=True)
class ChangeEvent:
    change_id: str
    old_state: str
    new_state: str
    actor: str
    at: str
    reason_code: str
    artifact_refs: tuple[str, ...] = ()


class ChangeStore(Protocol):
    def get_state(self, change_id: str) -> str: ...
    def append_event(self, event: ChangeEvent) -> None: ...


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "REQUESTED": {"VALIDATED", "ABORTED", "FAILED"},
    "VALIDATED": {"PREFLIGHT_OK", "ABORTED", "FAILED"},
    "PREFLIGHT_OK": {"PREPARED", "ABORTED", "FAILED"},
    "PREPARED": {"AWAITING_APPROVAL", "ABORTED", "FAILED"},
    "AWAITING_APPROVAL": {"APPROVED", "ABORTED"},
    "APPROVED": {"APPLYING", "ABORTED"},
    "APPLYING": {"VERIFYING", "UNKNOWN", "FAILED"},
    "VERIFYING": {"CONFIRMED", "UNKNOWN", "ROLLED_BACK", "FAILED"},
    "UNKNOWN": {"VERIFYING", "ROLLED_BACK", "FAILED"},
    "CONFIRMED": set(),
    "ABORTED": set(),
    "ROLLED_BACK": set(),
    "FAILED": set(),
}


def transition(
    store: ChangeStore,
    *,
    change_id: str,
    new_state: str,
    actor: str,
    reason_code: str,
    artifact_refs: tuple[str, ...] = (),
) -> None:
    old_state = store.get_state(change_id)
    allowed = ALLOWED_TRANSITIONS.get(old_state)
    if allowed is None or new_state not in allowed:
        raise ValueError(f"Transition interdite : {old_state} -> {new_state}")
    store.append_event(ChangeEvent(
        change_id=change_id,
        old_state=old_state,
        new_state=new_state,
        actor=actor,
        at=datetime.now(timezone.utc).isoformat(),
        reason_code=reason_code,
        artifact_refs=artifact_refs,
    ))
```

Cet exemple illustre le contrat, pas une implémentation complète de base de données. En production, la lecture de l'état et l'ajout de l'événement doivent être une opération atomique (par exemple une transaction ou une comparaison-et-échange), sinon deux workers peuvent valider la même transition à partir du même ancien état. Ajoutez une contrainte de version, une unicité de transition ou un verrou. Les changements de schéma et les transitions doivent être testés avant migration.


# 10. Préparer et examiner une configuration candidate de manière déterministe

## 10.1 Distinguer les étapes de configuration

Une candidate n'est pas équivalente à une configuration validée. Il faut distinguer :

1. **rendu** : la configuration est produite à partir des intentions, templates et variables ;
2. **validation statique** : les entrées, syntaxes et règles de politique sont contrôlées ;
3. **préparation NAPALM** : la candidate est chargée sur l'équipement ;
4. **diff** : la différence fournie par le pilote est collectée et examinée ;
5. **approbation** : un acteur autorisé approuve les artefacts exacts ;
6. **application** : le changement est exécuté selon une procédure documentée ;
7. **validation après changement** : les effets réseau sont contrôlés ;
8. **confirmation ou restauration** : l'opération est confirmée, abandonnée ou réconciliée.

Le rendu et le diff doivent être reproductibles. Si le même bundle, les mêmes variables, la même version de template et les mêmes paramètres de cible sont fournis, le système doit produire le même candidat, à l'exception d'éléments explicitement marqués comme variables et justifiés.

## 10.2 Versionner un bundle de changement

Un bundle est l'unité immuable qui lie l'intention, le périmètre et les artefacts de changement. Il devrait inclure :

- identifiant de la demande ou du ticket ;
- révision de l'inventaire ciblé ;
- rôles et appareils concernés ;
- version du template et paramètres non sensibles ;
- empreinte de la configuration rendue ;
- version de la politique et du profil de capacités ;
- résultats des tests statiques et de laboratoire ;
- contrôle pré-changement et données de référence ;
- fenêtre de maintenance et limites de vague ;
- plan de validation et stratégie de retour arrière.

N'enregistrez pas les mots de passe et tokens dans le bundle. Les secrets ne devraient généralement pas être intégrés dans les lignes de configuration générées non plus ; lorsque le système réseau exige des chaînes sensibles, la génération et le stockage doivent suivre une procédure dédiée et restreinte.

## 10.3 Rendu déterministe et prévention des dérives accidentelles

Le générateur de configuration ne doit pas employer des valeurs implicites dépendant du poste de travail, de l'ordre du dictionnaire, de l'heure courante ou de variables non versionnées. Les valeurs de template devraient venir d'une source contrôlée, être typées et faire l'objet d'une validation métier avant le rendu.

Exemples de contrôles statiques :

- le VLAN existe dans le modèle de site ;
- le préfixe IP est bien une adresse réseau conforme à l'intention ;
- l'ASN appartient au domaine déclaré ;
- le voisin BGP se trouve dans un périmètre connu ;
- aucune interface de gestion n'est modifiée par une tâche qui ne le prévoit pas ;
- le candidat ne contient pas d'adresse ou de nom d'hôte hors du périmètre approuvé ;
- une configuration de remplacement ne supprimerait pas un bloc non géré par la plateforme ;
- la taille du diff et le nombre de suppressions restent sous les seuils autorisés.

Le dernier point mérite une attention spéciale. Une configuration `replace` peut supprimer des sections que l'outil n'a pas l'intention de gérer. Utilisez-la uniquement si le contrat de propriété de la configuration est clair. Si l'automatisation ne possède qu'un domaine limité, le remplacement complet de la configuration est généralement une mauvaise frontière de responsabilité.

## 10.4 Merge contre replace : un choix de propriété

Un merge introduit ou modifie des lignes sans nécessairement décrire tout l'état cible. Il peut être adapté à un périmètre fonctionnel restreint, mais ses effets exacts dépendent de la grammaire du système et du pilote. Un replace vise à remplacer un périmètre de configuration plus large, avec un risque accru de supprimer des objets non inclus dans le rendu.

Il faut répondre à trois questions :

1. **Qui possède la configuration ?** L'automatisation est-elle propriétaire de tout le fichier ou d'un ensemble de sections ?
2. **Quelle sémantique de remplacement est réellement prise en charge ?** Est-ce un remplacement natif ou une stratégie simulée ?
3. **Comment prouver le résultat ?** Le diff peut-il être fiable et le rollback a-t-il été qualifié sur cette plateforme ?

La documentation officielle souligne qu'il faut comprendre les limites de `merge`, `replace`, du diff, de l'atomicité, de `commit-confirm` et du rollback pour le pilote exact. N'en déduisez pas une garantie universelle à partir du fait que la méthode est disponible dans l'API commune.

## 10.5 Inspecter le diff automatiquement, puis humainement

Un diff lisible ne devient pas automatiquement sûr parce qu'il est court. Définissez un parseur ou un contrôle qui identifie les classes de modification, mais conservez aussi le diff original produit par le pilote. Un parseur générique de diff de configuration peut se tromper sur les retraits, les blocs hiérarchiques et les différences de format propres à une plateforme.

Contrôles automatiques possibles :

- nombre de lignes ajoutées et supprimées ;
- modifications d'éléments de routage, d'interfaces ou d'accès d'administration ;
- présence de commandes interdites ou inattendues ;
- changement de routes, de voisinages ou de politiques sensibles ;
- suppression d'objets hors du périmètre géré ;
- divergence entre le hash du candidat approuvé et celui à appliquer ;
- détection d'une chaîne de configuration vide ou anormalement volumineuse ;
- absence de candidat si le rendu est supposé produire une modification.

La revue humaine reste nécessaire quand la politique l'exige. Elle doit afficher la cible, le rôle, le risque, les préconditions, le diff, l'effet prévu et le plan de retour arrière, pas seulement le texte brut.

## 10.6 Exemple de phase de préparation uniquement

L'exemple ci-dessous charge une candidate et enregistre le diff, mais **ne fait pas de commit**. Il montre volontairement un point d'arrêt explicite où le workflow doit sauvegarder les preuves, faire appliquer la politique et recueillir l'approbation.

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class PreparedCandidate:
    device_id: str
    bundle_id: str
    diff: str
    diff_is_empty: bool
    profile_revision: str


def prepare_candidate(
    device: Any,
    *,
    device_id: str,
    bundle_id: str,
    rendered_config: str,
    profile_revision: str,
    diff_path: Path,
) -> PreparedCandidate:
    if not rendered_config.strip():
        raise ValueError("Le rendu de configuration est vide")

    device.load_merge_candidate(config=rendered_config)
    try:
        diff = device.compare_config()
        if not isinstance(diff, str):
            raise TypeError("compare_config() n'a pas retourné du texte")
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(diff, encoding="utf-8")
        return PreparedCandidate(
            device_id=device_id,
            bundle_id=bundle_id,
            diff=diff,
            diff_is_empty=(not diff.strip()),
            profile_revision=profile_revision,
        )
    except Exception:
        # La tentative d'abandon est défensive. En cas d'échec réseau pendant
        # le nettoyage, l'état doit être enregistré comme incertain et réconcilié.
        try:
            device.discard_config()
        except Exception:
            pass
        raise
```

Cet exemple est une base pédagogique, pas un moteur de changement complet. En production, le nettoyage ne doit pas être « oublié » si `discard_config()` échoue : enregistrez l'échec, réconciliez la candidate sur l'équipement et empêchez une nouvelle demande incompatible. De même, si le processus s'arrête après `load_merge_candidate()` et avant l'écriture de l'artefact, le système doit connaître ce risque et disposer d'un moyen de retrouver le bundle.

Le chemin d'artefact doit venir du stockage contrôlé par la plateforme, et non d'une entrée libre permettant d'écraser des fichiers arbitraires. Si le diff peut contenir des informations sensibles, appliquez le contrôle d'accès et la rétention adaptés.

## 10.7 Gestion des différences vides

Un diff vide peut signifier qu'aucun changement n'est nécessaire ; cela peut aussi révéler que le rendu est vide, que l'appel de comparaison n'a pas fonctionné comme prévu ou que la sémantique du pilote n'est pas celle supposée. Le système doit comparer le résultat à l'intention :

- si l'intention demande une modification et que le diff est vide, arrêter et diagnostiquer ;
- si l'intention est déjà satisfaite, clôturer comme `NO_CHANGE` sans commit ;
- si le pilote ne produit pas un diff fiable sur ce type de configuration, exiger un contrôle alternatif qualifié ;
- ne pas exécuter un commit pour « forcer » l'application d'un état qui semble déjà présent.


# 11. Déploiement progressif : canari, vagues et rayon d'impact

## 11.1 Pourquoi un déploiement global est souvent un défaut de conception

Appliquer le même changement à tous les routeurs simultanément maximise la vitesse quand tout se passe bien, mais aussi l'impact potentiel quand une hypothèse est incorrecte. Une erreur dans un template, une politique de routage ou une hypothèse de modèle peut toucher plusieurs régions avant que les premiers symptômes soient identifiés.

Un déploiement progressif sépare le parc en lots et impose une validation entre les lots. Le premier lot est le **canari** : un équipement ou un ensemble très limité, choisi pour être représentatif tout en limitant le risque. Les lots suivants ne démarrent pas seulement parce que le délai prévu est écoulé ; ils démarrent parce que les contrôles définis sont passés.

Le choix d'un canari doit tenir compte de la topologie et de la criticité, pas uniquement de l'ordre alphabétique des noms. Évitez que le premier canari soit le seul chemin de management vers le site, l'unique routeur de bordure d'une région, ou un appareil dont les particularités ne représentent pas le reste du parc.

## 11.2 Stratégie de vagues

Un exemple de plan peut être :

| Vague | Portée indicative | Condition de passage |
|---|---|---|
| Vague 0 | laboratoire représentatif | tests fonctionnels et restauration réussis |
| Vague 1 | un canari de faible criticité | préconditions, diff, vérifications post-changement satisfaits |
| Vague 2 | petite fraction d'un groupe homogène | absence de régression et durée d'observation atteinte |
| Vague 3 | un site ou une zone limitée | taux de réussite et métriques dans les seuils |
| Vague 4 | reste du parc approuvé | validation de chaque vague, arrêt automatique sur anomalie |

Les tailles de vague dépendent du parc. Un parc de six routeurs ne se pilote pas comme un parc de plusieurs milliers d'appareils. Le principe reste identique : l'extension du rayon d'impact est une décision distincte, fondée sur des preuves.

## 11.3 Diagramme d'un déploiement canari

<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="535" viewBox="0 0 1120 535" role="img" aria-labelledby="napexp-can-title napexp-can-desc">
  <title id="napexp-can-title">Déploiement progressif où chaque vague attend sa porte de validation</title>
  <desc id="napexp-can-desc">Le bundle passe au laboratoire, puis une porte de validation autorise le canari. Une seconde porte autorise le petit lot suivant. Après chaque lot, une nouvelle porte doit réussir avant les vagues suivantes. Toute porte en échec ou inconclusive arrête la progression.</desc>
  <defs><marker id="napexp-can-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#9bb4d8"/></marker></defs>
  <rect x="1" y="1" width="1118" height="533" rx="16" fill="#0b1220" stroke="#27374e" stroke-width="2"/>
  <g stroke="#9bb4d8" stroke-width="2.6" fill="none" marker-end="url(#napexp-can-arrow)"><path d="M175 93 H215"/><path d="M375 93 H420"/><path d="M570 93 H615"/><path d="M775 93 H820"/><path d="M825 255 H765"/><path d="M600 255 H540"/></g>
  <g>
    <rect x="25" y="55" width="150" height="76" rx="11" fill="#172b45" stroke="#6ec8f5" stroke-width="1.6"/><text x="100" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f4f7ff">Bundle figé</text><text x="100" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">hash • revue</text>
    <rect x="220" y="55" width="155" height="76" rx="11" fill="#183c38" stroke="#50d6b0" stroke-width="1.6"/><text x="297" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f4f7ff">Vague 0</text><text x="297" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">laboratoire</text>
    <rect x="420" y="55" width="150" height="76" rx="11" fill="#13283d" stroke="#6ec8f5" stroke-width="1.6"/><text x="495" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f4f7ff">Gate 0 • PASS ?</text><text x="495" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">tests labo réussis</text>
    <rect x="620" y="55" width="155" height="76" rx="11" fill="#3c311c" stroke="#f3c46e" stroke-width="1.6"/><text x="697" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f4f7ff">Vague 1</text><text x="697" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">canari observé</text>
    <rect x="820" y="55" width="155" height="76" rx="11" fill="#13283d" stroke="#6ec8f5" stroke-width="1.6"/><text x="897" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f4f7ff">Gate 1 • PASS ?</text><text x="897" y="108" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">santé du canari</text>
    <rect x="825" y="215" width="155" height="80" rx="11" fill="#3c311c" stroke="#f3c46e" stroke-width="1.6"/><text x="902" y="246" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f4f7ff">Vague 2</text><text x="902" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">petit lot limité</text>
    <rect x="600" y="215" width="160" height="80" rx="11" fill="#13283d" stroke="#6ec8f5" stroke-width="1.6"/><text x="680" y="246" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f4f7ff">Gate 2 • PASS ?</text><text x="680" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">état et services</text>
    <rect x="340" y="215" width="195" height="80" rx="11" fill="#183c38" stroke="#50d6b0" stroke-width="1.6"/><text x="437" y="246" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f4f7ff">Vagues suivantes</text><text x="437" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">lot par lot seulement</text>
  </g>
  <path d="M897 131 V209" stroke="#50d6b0" stroke-width="3" stroke-dasharray="7 6" fill="none" marker-end="url(#napexp-can-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-28" dur="2.5s" repeatCount="indefinite"/></path>
  <path d="M680 295 V350 H560 V390" stroke="#ff8e8e" stroke-width="2.8" stroke-dasharray="8 7" fill="none" marker-end="url(#napexp-can-arrow)"/>
  <rect x="300" y="395" width="520" height="82" rx="12" fill="#462528" stroke="#ff9292" stroke-width="1.7"/><text x="560" y="426" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#fff4f4">Depuis n'importe quelle porte : FAIL ou INCONCLUSIVE</text><text x="560" y="451" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="#f4d1d4">STOP • figer le périmètre • réconcilier • reprise approuvée</text>
  <text x="845" y="414" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">La vague suivante</text><text x="845" y="435" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">n'avance qu'après</text><text x="845" y="456" font-family="Arial,sans-serif" font-size="13" fill="#d2def3">des preuves suffisantes.</text>
  <text x="30" y="510" font-family="Arial,sans-serif" font-size="13" fill="#9fb4d1">Le passage d'une vague à la suivante est une décision conditionnelle, jamais une continuation automatique.</text>
</svg>

## 11.4 Gates de progression

Chaque porte de validation doit être testable par un script et être rapportée sous une forme structurée : `PASS`, `FAIL` ou `INCONCLUSIVE`. `INCONCLUSIVE` ne doit pas être converti en `PASS` parce que le délai de maintenance se termine. La réponse à une preuve indisponible dépend de la politique : elle peut entraîner un arrêt, une collecte complémentaire, ou une approbation exceptionnelle documentée.

Exemples de gates :

- toutes les sessions critiques prévues sont établies ;
- nombre de voisins BGP attendus atteint et stabilité pendant une fenêtre définie ;
- interfaces critiques toujours `is_up` et `is_enabled` selon le rôle ;
- absence d'augmentation anormale des erreurs ou des drops, quand les compteurs sont disponibles et comparables ;
- résolution de noms et synchronisation NTP conformes si le changement les affecte ;
- mesures de service externes dans les seuils, depuis un point de mesure pertinent ;
- pas d'alerte critique nouvelle liée à la cible ;
- résultat de conformité après changement satisfaisant ;
- accès d'administration et capacité de restauration toujours disponibles.

Les contrôles doivent être choisis selon l'effet du changement. Un changement de description d'interface ne nécessite pas nécessairement le même jeu de gates qu'un changement de politique BGP ou que le déplacement d'une passerelle.

## 11.5 Calculer la taille des vagues à partir du risque

Une taille fixe n'est pas suffisante pour toutes les opérations. Une règle de contrôle peut imposer un seul équipement à la fois pour un changement qui touche le plan de contrôle, tout en autorisant des groupes plus grands pour un changement localisé et qualifié. Définissez les critères à partir de la criticité, du partage de domaine de panne, de la redondance et du caractère réversible du changement.

Une erreur courante consiste à grouper par modèle d'équipement mais à ignorer la topologie. Plusieurs équipements du même modèle peuvent être deux membres d'une même paire redondante ; les modifier simultanément peut supprimer la redondance. Les lots doivent respecter les dépendances topologiques et les limites d'impact, pas seulement les propriétés matérielles.

## 11.6 Arrêter l'expansion n'est pas toujours restaurer

Quand une gate échoue, arrêtez les vagues nouvelles immédiatement. Décidez ensuite, selon l'état observé, s'il faut :

- simplement stopper et collecter davantage d'informations ;
- laisser le changement en place sous une surveillance renforcée ;
- effectuer un retour arrière automatique déjà approuvé et vérifié ;
- demander une décision à un responsable d'incident ;
- déclencher la procédure manuelle de restauration.

Un retour arrière automatique peut être aussi dangereux que le changement initial si la situation a évolué depuis sa préparation. Une procédure de restauration est un plan, pas un réflexe inconditionnel.


# 12. Validation post-changement et réconciliation

## 12.1 La validation ne doit pas être un écho du diff

Un diff indique ce que le pilote estime avoir changé dans la configuration ; il ne prouve pas que le comportement attendu est effectivement disponible. Les contrôles post-changement doivent examiner des données indépendantes lorsque c'est possible : getters, sessions protocolaires, interfaces, chemin de management et vérifications de service depuis des points externes.

Exemple : un changement BGP peut rendre la configuration conforme tout en laissant un voisin en état Idle, une route attendue absente ou un chemin applicatif dégradé. La validation doit couvrir le résultat fonctionnel et le rayon d'impact, pas seulement les lignes de configuration.

## 12.2 Avant/après : les mêmes questions, avec un contexte comparable

Un contrôle avant/après n'est utile que si les mesures sont suffisamment comparables. Conservez les opérations exécutées, les horodatages, les paramètres, la version du normaliseur et la version de politique. Si le contrôle avant utilisait un getter que le contrôle après n'a pas pu exécuter, affichez un résultat inconnu et non une comparaison vide.

La comparaison peut comporter :

- état des interfaces requises ;
- nombre et identité des voisins attendus ;
- sessions BGP ou autre état de protocole pertinent ;
- adresses et routes attendues ;
- compteurs d'erreurs mesurés sur un intervalle comparable ;
- synchronisation NTP ou autres services qui sont dans le périmètre du changement ;
- connectivité de management ;
- tests de service externes ;
- différence de configuration effective, si la méthode peut être interprétée de façon fiable.

## 12.3 Comparer des compteurs avec prudence

Un compteur cumulatif seul ne révèle pas un taux. Pour estimer un taux d'erreurs, il faut comparer deux échantillons horodatés sur un intervalle adéquat, en tenant compte des remises à zéro, des changements de compteur et des débordements éventuels. Un compteur réinitialisé à zéro ne signifie pas automatiquement que l'équipement s'est amélioré.

Pour un compteur `errors`, le taux peut être calculé par :

```text
rate = (errors_t2 - errors_t1) / (time_t2 - time_t1)
```

La formule n'est valide que si les compteurs sont comparables et non remis à zéro. Si `errors_t2 < errors_t1`, ne produisez pas un taux négatif sans investigation. Marquez l'échantillon comme discontinu ou utilisez une logique spécifique au compteur et à la plateforme.

## 12.4 Réconciliation après perte de session

Scénario critique : le processus appelle une méthode d'application, puis perd la connexion avant de recevoir une réponse. Ne présumez ni le succès ni l'échec. Utilisez une procédure de réconciliation en lecture :

1. enregistrer la tâche dans l'état `UNKNOWN` et arrêter tout retry d'écriture ;
2. conserver les identifiants du bundle, la version du candidat, le diff, l'heure d'application et l'erreur ;
3. laisser le système récupérer la session ou utiliser une autre route d'administration approuvée ;
4. collecter l'état effectif et la configuration avec un accès lecture adapté ;
5. comparer l'état réel aux états « avant », « attendu » et, si disponible, aux indices de transaction du constructeur ;
6. déterminer si la configuration souhaitée est appliquée, absente, partiellement appliquée ou indéterminée ;
7. si le résultat est encore ambigu, garder le verrou de changement et escalader ;
8. une fois l'état établi, décider de confirmer, corriger ou restaurer selon la politique approuvée.

Une simple égalité de configuration ne garantit pas à elle seule que le service fonctionne. Une simple réussite du getter ne garantit pas que la configuration est identique à la candidate. Utilisez plusieurs preuves lorsque le changement le justifie.

## 12.5 Exemple de résultat de vérification

```json
{
  "change_id": "CHG-2026-1042",
  "device_id": "edge-cm-01",
  "verification_revision": "edge-postcheck@2.2.0",
  "started_at": "2026-10-23T20:01:00Z",
  "finished_at": "2026-10-23T20:01:11Z",
  "status": "INCONCLUSIVE",
  "checks": [
    {"name": "management_reachable", "status": "PASS", "evidence_ref": "ev-8821"},
    {"name": "critical_interfaces", "status": "PASS", "evidence_ref": "ev-8822"},
    {"name": "expected_bgp_neighbors", "status": "INCONCLUSIVE", "evidence_ref": "ev-8823"},
    {"name": "service_probe", "status": "PASS", "evidence_ref": "ev-8824"}
  ],
  "decision": "STOP_NEXT_WAVE",
  "reason": "Une preuve critique BGP est indéterminée"
}
```

Les identifiants et résultats sont fictifs. Ce résultat n'est pas « presque conforme » : il montre que plusieurs contrôles passent mais qu'une preuve critique demeure incertaine. Le moteur de vague arrête l'expansion et déclenche la procédure de diagnostic.

## 12.6 Idée fondamentale : une preuve doit être réfutable

Pour chaque contrôle, définissez ce qui permet de le déclarer réussi, échoué ou indéterminé. Un contrôle du type « aucune erreur trouvée » sans vérifier que la collecte a réussi n'est pas réfutable : il ne permet pas de distinguer une situation normale d'une absence de données. Un contrôle expert doit expliquer ses conditions de succès et ses limites.


# 13. Retour arrière, commit-confirm et stratégies de récupération

## 13.1 Le rollback est une procédure à qualifier

Le terme « rollback » recouvre plusieurs mécanismes : retour à une configuration candidate précédente, annulation d'un commit temporaire, remplacement depuis une sauvegarde, annulation manuelle ou restauration par le mécanisme natif du constructeur. Ils n'offrent pas les mêmes garanties. Certaines plateformes possèdent un mécanisme natif de confirmation temporisée ; d'autres ne le prennent pas en charge ou l'émulent de manière différente. La sémantique doit être validée pour le pilote et la version exacts.

Avant d'autoriser une automatisation de rollback, répondez à ces questions :

- L'opération restaure-t-elle une configuration précise ou appelle-t-elle un mécanisme constructeur dont le périmètre peut varier ?
- Le rollback affecte-t-il l'ensemble de la configuration ou seulement la dernière candidate ?
- Est-il atomique, et si non, quelles modifications partielles sont possibles ?
- Quel état est restauré si un autre opérateur a modifié la configuration depuis la préparation ?
- Que se passe-t-il si la session tombe pendant la restauration ?
- La voie d'administration nécessaire au rollback reste-t-elle accessible après le changement ?
- Quel test fonctionnel démontre que la restauration est réussie ?
- Qui a le droit de déclencher un rollback d'urgence et dans quelles conditions ?

Une procédure de rollback ne doit pas être qualifiée seulement parce que son appel retourne sans exception. Elle doit être exécutée dans le laboratoire, suivie de contrôles sur la configuration et le fonctionnement, avec archivage des preuves.

## 13.2 Commit-confirm : un garde-fou puissant, pas universel

Lorsqu'un pilote et la plateforme ciblée prennent réellement en charge la confirmation temporisée, ce mécanisme peut offrir une protection utile : l'application du changement est provisoire, et il doit être confirmé avant l'expiration d'un délai sous peine de retour automatique. Cependant, sa sémantique exacte, les paramètres disponibles et les garanties varient selon les plateformes. Vérifiez la documentation du pilote et la matrice de compatibilité à la version utilisée.

Procédure conceptuelle :

1. vérifier la capacité `commit-confirm` dans le profil qualifié ;
2. vérifier que le délai de restauration est supérieur à la durée attendue des contrôles et du diagnostic initial ;
3. préparer la candidate, examiner le diff et collecter une approbation liée aux artefacts exacts ;
4. appliquer avec un mécanisme de confirmation temporisée compatible ;
5. vérifier la connectivité de management, les contrôles protocolaires et les tests de service ;
6. confirmer uniquement si les contrôles critiques passent ;
7. en cas d'échec, utiliser la restauration prévue ou laisser expirer le timer si c'est la procédure testée ;
8. collecter et archiver l'état final indépendamment du retour de la commande d'application.

Le délai de confirmation ne doit pas être choisi arbitrairement. Il doit couvrir les temps de connexion, les lectures, les délais de convergence réseau, la période d'observation et la décision humaine éventuelle. Un timer trop court peut restaurer un changement correct avant la fin des contrôles ; un timer trop long prolonge la période où l'état peut rester temporaire.

## 13.3 Exemple de commit-confirm conditionnel pour un laboratoire

**N'exécutez ce modèle que dans un laboratoire isolé**, après avoir confirmé que le pilote de la cible prend en charge `commit_config(revert_in=...)`, `has_pending_commit()` et `confirm_commit()`. Le profil de production peut interdire ces méthodes si elles n'ont pas été qualifiées.

```python
from typing import Any, Callable


def lab_commit_confirm(
    device: Any,
    *,
    revert_seconds: int,
    postcheck: Callable[[], bool],
    capability_profile_allows: bool,
) -> str:
    """Modèle de démonstration : ne constitue pas un déployeur de production."""
    if not capability_profile_allows:
        raise RuntimeError("Le profil n'autorise pas commit-confirm")
    if revert_seconds < 120:
        raise ValueError("Le timer de labo est volontairement borné")

    required_methods = ("commit_config", "has_pending_commit", "confirm_commit")
    missing = [name for name in required_methods if not callable(getattr(device, name, None))]
    if missing:
        raise RuntimeError(f"Capacités manquantes : {', '.join(missing)}")

    # Le chargement de la candidate, son diff et son approbation doivent avoir
    # été réalisés avant d'appeler cette fonction.
    device.commit_config(revert_in=revert_seconds)

    # Après commit, toute exception ou résultat ambigu doit être traité par
    # la machine à états, et non par un retry automatique de commit.
    if not device.has_pending_commit():
        # Selon le pilote, l'absence de commit pending doit être interprétée
        # à partir de son contrat qualifié : ce n'est pas une preuve universelle.
        raise RuntimeError("Aucun commit en attente détecté : état à réconcilier")

    if not postcheck():
        # Dans un runbook validé, on peut choisir un rollback immédiat ou laisser
        # expirer le timer, selon la sémantique prouvée sur cette plateforme.
        raise RuntimeError("Postcheck en échec : ne pas confirmer ; escalader selon runbook")

    device.confirm_commit()
    return "confirmed"
```

Cet exemple est volontairement prudent. Un échec de `postcheck()` ne se transforme pas automatiquement en appel de rollback générique, car il faut savoir si le commit est en attente, s'il a été appliqué et quel mécanisme exact est fiable. Dans un vrai orchestrateur, l'état serait persisté avant et après chaque étape. Les exceptions de la méthode de commit seraient classées en résultat certain ou ambigu ; l'absence de confirmation serait traitée par la machine à états.

## 13.4 Plan de retour arrière écrit avant le changement

Le rollback doit être défini avant l'approbation et contenir :

- l'état initial enregistré, avec sa provenance et son horodatage ;
- la stratégie de restauration supportée pour ce profil ;
- les conditions qui déclenchent une restauration ;
- les conditions qui interdisent une restauration automatique ;
- les commandes ou appels autorisés à utiliser dans le laboratoire, adaptés à la plateforme ;
- la durée attendue et la fenêtre disponible ;
- la personne ou le rôle habilité à décider ;
- les vérifications qui prouvent le retour à l'état acceptable ;
- l'action prévue si le rollback échoue ou si l'état reste inconnu.

Une restauration peut être bloquée si un changement indépendant est intervenu après la prise de l'instantané ou si la configuration de référence n'est plus valide. Le plan doit expliquer comment gérer ce conflit plutôt que d'écraser une modification récente par une version ancienne.

## 13.5 Après un rollback, il faut vérifier à nouveau

Ne marquez pas un changement `ROLLED_BACK` simplement parce que le constructeur a accepté une commande. Vérifiez l'état de la configuration, les sessions de protocole, les interfaces et les tests de service pertinents. Comparez les résultats au niveau de base et expliquez les différences résiduelles.

Le rollback peut réussir sur la configuration et échouer sur le service si la convergence prend du temps ou si un état externe a changé. Le résultat peut aussi être partiel ; la plateforme doit rester capable d'afficher l'incertitude et de lancer un runbook d'incident.


# 14. NAPALM Validate et contrôles de conformité à grande échelle

## 14.1 Validation de l'état versus modification de la configuration

NAPALM Validate permet de comparer des données obtenues auprès de l'équipement à des critères déclarés. Le détail du schéma, les getters disponibles et le comportement des modes de validation doivent être vérifiés dans la version utilisée. La validation ne remplace ni la collecte ni l'examen du risque : elle formalise une partie de vos attentes et fournit un rapport à interpréter.

Séparez quatre questions :

- le getter a-t-il réussi ?
- la réponse est-elle complète pour les champs attendus ?
- les valeurs observées respectent-elles la règle ?
- cette règle représente-t-elle encore l'intention métier valide ?

Une configuration peut être conforme à un document de validation devenu obsolète. Un document trop strict peut signaler de faux positifs à chaque ajout légitime de voisin ou d'interface. Un document trop permissif peut laisser passer une suppression dangereuse. La politique de conformité doit être testée et versionnée comme le code.

## 14.2 Modes stricts et périmètre de comparaison

La documentation de Validate décrit des modes permettant de contrôler plus ou moins strictement certaines parties de la structure. Un contrôle strict peut être utile quand une liste exacte de voisins ou d'objets est attendue ; il peut aussi devenir fragile si un ajout est normal dans ce domaine. Documentez précisément le niveau où le mode strict est appliqué.

Par exemple, une règle peut exiger un voisin BGP spécifique sans interdire tous les autres voisins du routeur ; une règle stricte au niveau de la liste peut au contraire exiger exactement le jeu de voisins déclaré. Ce sont deux intentions différentes. Ne les confondez pas.

## 14.3 Séparer le baseline et les exceptions approuvées

Dans un grand parc, une politique unique ne suffit pas toujours. Il existe des exceptions de site, des périodes de migration, des versions logicielles différentes et des zones historiques. Utilisez une hiérarchie de politiques limitée et explicite : baseline commune, surcharge de rôle, surcharge de site, exception approuvée avec durée d'expiration.

Une exception doit posséder :

- un identifiant et un responsable ;
- la règle concernée et la justification ;
- son périmètre précis ;
- sa date de création et d'expiration ;
- la preuve qu'elle a été approuvée ;
- le plan qui permettra de la supprimer.

Évitez les exceptions permanentes sans propriétaire. Un système de conformité peut sembler « stable » si toutes les anomalies sont exclues, mais il ne protège alors plus l'intention métier.

## 14.4 Éviter les faux positifs et les faux négatifs

Les faux positifs créent de la fatigue d'alerte ; les faux négatifs masquent de vrais problèmes. Pour réduire les deux :

- versionnez les règles et les fixtures de test ;
- collectez des exemples représentatifs de chaque profil de pilote ;
- distinguez les champs obligatoires des champs informatifs ;
- appliquez un délai d'observation pour les états transitoires lorsque c'est justifié ;
- ne faites pas disparaître les contrôles parce qu'ils génèrent trop d'alertes ;
- mesurez la proportion d'écarts confirmés après investigation ;
- analysez les changements de modèle qui rendent une règle obsolète ;
- conservez les résultats inconclusifs plutôt que de les convertir en conformes.

## 14.5 Évaluer une politique sur un historique

Avant de rendre une nouvelle règle bloquante, exécutez-la en mode observation sur un historique représentatif. Calculez le nombre de cibles qui seraient conformes, non conformes ou indéterminées, et expliquez les cas où la donnée manque. Comparez la nouvelle version avec l'ancienne et revoyez les changements de classification.

Cet exercice ne doit pas être interprété comme la permission d'ignorer un défaut critique pendant une période d'observation. Les contrôles de sécurité impératifs peuvent rester bloquants dès le départ. Le mode observation convient aux règles dont le périmètre ou le seuil doit être calibré, pas aux protections essentielles.


# 15. CI/CD et GitOps pour l'automatisation réseau

## 15.1 Qu'est-ce qui doit être versionné ?

Un système d'automatisation réseau ne se limite pas au code Python. Le dépôt doit versionner ce qui définit le comportement, tout en gardant les secrets et artefacts sensibles dans des espaces séparés. Les éléments à versionner incluent généralement :

- code de l'application et dépendances verrouillées ;
- templates de configuration ;
- schémas et règles de validation de l'inventaire ;
- politiques de conformité et de changement ;
- profils de capacités des pilotes ;
- fixtures anonymisées et données de test ;
- runbooks, standards de journalisation et critères de déploiement ;
- scripts de migration de schéma ;
- décisions d'architecture.

Ne versionnez pas les secrets, les configurations de production complètes non nettoyées, les tokens CI ou les sauvegardes d'accès libre. Le fait que les fichiers soient « dans Git privé » ne suffit pas à en faire un coffre-fort : l'historique et les clones rendent la suppression ultérieure difficile.

## 15.2 Construire une chaîne de promotion

Une promotion robuste fait passer un même artefact à travers plusieurs environnements, plutôt que de reconstruire la configuration différemment à chaque étape. Le candidat testé et approuvé doit être celui qui atteint la production. Si la différence d'environnement exige des variables, elles doivent être séparées du code et incluses dans l'empreinte de la candidate.

<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520" role="img" aria-labelledby="napexp-ci-title napexp-ci-desc">
  <title id="napexp-ci-title">Pipeline CI/CD avec approbation, gate après canari et observations continues</title>
  <desc id="napexp-ci-desc">Le commit passe les contrôles et le laboratoire, puis produit un bundle immuable approuvé. La production commence par un canari. Une gate décide si une vague peut être promue. Après chaque vague, les contrôles sont rejoués. Audit et observabilité reçoivent les résultats pendant l'exécution.</desc>
  <defs><marker id="napexp-ci-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#9bb4d8"/></marker></defs>
  <rect x="1" y="1" width="1118" height="518" rx="16" fill="#0b1220" stroke="#27374e" stroke-width="2"/>
  <g stroke="#9bb4d8" stroke-width="2.3" fill="none" marker-end="url(#napexp-ci-arrow)"><path d="M158 97 H187"/><path d="M341 97 H370"/><path d="M524 97 H553"/><path d="M707 97 H736"/><path d="M890 97 H919"/></g>
  <g>
    <rect x="24" y="55" width="134" height="84" rx="11" fill="#172c46" stroke="#69c8f2" stroke-width="1.5"/><text x="91" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Commit Git</text><text x="91" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d1def2">revue et diff</text>
    <rect x="187" y="55" width="154" height="84" rx="11" fill="#172c46" stroke="#69c8f2" stroke-width="1.5"/><text x="264" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Qualité statique</text><text x="264" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d1def2">lint • types • schéma</text>
    <rect x="370" y="55" width="154" height="84" rx="11" fill="#183c38" stroke="#50d6b0" stroke-width="1.5"/><text x="447" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Tests automatisés</text><text x="447" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d1def2">unitaires • contrat</text>
    <rect x="553" y="55" width="154" height="84" rx="11" fill="#183c38" stroke="#50d6b0" stroke-width="1.5"/><text x="630" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Laboratoire</text><text x="630" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d1def2">intégration • restore</text>
    <rect x="736" y="55" width="154" height="84" rx="11" fill="#3b301c" stroke="#f4c66e" stroke-width="1.5"/><text x="813" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Bundle immuable</text><text x="813" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d1def2">hash • manifeste</text>
    <rect x="919" y="55" width="174" height="84" rx="11" fill="#3b301c" stroke="#f4c66e" stroke-width="1.5"/><text x="1006" y="86" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Approbation</text><text x="1006" y="109" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#d1def2">diff et cible figés</text>
  </g>
  <path d="M1006 139 V183 H175 V215" stroke="#9bb4d8" stroke-width="2.3" fill="none" marker-end="url(#napexp-ci-arrow)"/>
  <g>
    <rect x="60" y="220" width="230" height="76" rx="11" fill="#4b2928" stroke="#ff9d8c" stroke-width="1.6"/><text x="175" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Production : canari</text><text x="175" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d1def2">préchecks + postchecks</text>
    <rect x="365" y="220" width="200" height="76" rx="11" fill="#13283d" stroke="#70c4f5" stroke-width="1.6"/><text x="465" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Gate de validation</text><text x="465" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d1def2">PASS / FAIL / inconclusif</text>
    <rect x="665" y="220" width="210" height="76" rx="11" fill="#183c38" stroke="#50d6b0" stroke-width="1.6"/><text x="770" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f3f7ff">Promouvoir un lot</text><text x="770" y="273" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d1def2">un lot à la fois</text>
  </g>
  <g stroke="#9bb4d8" stroke-width="2.3" fill="none" marker-end="url(#napexp-ci-arrow)"><path d="M290 258 H360"/><path d="M565 258 H660"/></g>
  <path d="M770 296 V326 H465 V302" stroke="#6ec8f5" stroke-width="2.5" stroke-dasharray="7 6" fill="none" marker-end="url(#napexp-ci-arrow)"><animate attributeName="stroke-dashoffset" from="0" to="-28" dur="2.4s" repeatCount="indefinite"/></path>
  <text x="505" y="319" font-family="Arial,sans-serif" font-size="12" fill="#a8dfff">après chaque lot, la gate est rejouée</text>
  <path d="M390 296 V350 H275 V375" stroke="#ff9494" stroke-width="2.5" stroke-dasharray="8 6" fill="none" marker-end="url(#napexp-ci-arrow)"/>
  <path d="M770 296 V350 H835 V375" stroke="#73b8ff" stroke-width="2.4" stroke-dasharray="6 7" fill="none" marker-end="url(#napexp-ci-arrow)"/>
  <rect x="45" y="380" width="445" height="88" rx="11" fill="#44262a" stroke="#ff9494" stroke-width="1.5"/><text x="267" y="411" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#fff4f4">Gate échouée ou inconclusive</text><text x="267" y="436" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#f4d1d4">arrêter l'expansion • réconcilier</text><text x="267" y="454" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#f4d1d4">aucune promotion automatique</text>
  <rect x="585" y="380" width="500" height="88" rx="11" fill="#172c46" stroke="#69c8f2" stroke-width="1.5"/><text x="835" y="411" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f3f7ff">Audit et observabilité — flux parallèle</text><text x="835" y="436" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#d1def2">logs • métriques • diffs • décisions • résultats par vague</text><text x="835" y="454" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#9fb4d1">consultés avant chaque promotion</text>
  <text x="45" y="495" font-family="Arial,sans-serif" font-size="13" fill="#9fb4d1">Le même bundle hashé est promu ; toute modification invalide l'approbation précédente.</text>
</svg>

## 15.3 Pipeline de pull request

Une pull request modifiant un template ou une politique devrait déclencher automatiquement :

1. formatage, lint et vérifications de types ;
2. validation de la syntaxe et du schéma de l'inventaire ;
3. tests unitaires du normaliseur, du moteur de politique et de la machine à états ;
4. tests de contrat sur les données de fixture de chaque profil concerné ;
5. tests comparatifs sur la production de configuration de test ;
6. vérification d'absence de secrets dans les fichiers modifiés et les artefacts ;
7. test d'intégration dans un laboratoire représentatif si la nature du changement l'exige ;
8. revue obligatoire par un propriétaire du module ou du domaine réseau ;
9. production d'un manifeste comprenant versions et empreintes ;
10. préparation de plan de déploiement et de restauration.

Tous les changements ne nécessitent pas les mêmes tests matériels, mais l'exemption doit être documentée et déterminée par des règles, pas accordée par habitude. Une correction de documentation peut passer par une voie plus simple qu'une modification du moteur de commit-confirm.

## 15.4 Séparer les droits entre CI et production

La CI peut avoir le droit de calculer des diffs, de tester dans le laboratoire et de produire un bundle, sans avoir le droit de modifier les équipements de production. Le système de déploiement de production peut accepter uniquement les artefacts signés ou produits par une pipeline approuvée et vérifier leur empreinte avant application.

Cette séparation réduit les conséquences d'une dépendance malveillante, d'un token CI exposé ou d'une pull request compromise. Si la même identité peut modifier le code, approuver le changement, écrire sur les équipements et supprimer les logs, l'audit n'est plus indépendant.

## 15.5 GitOps : éviter la boucle de correction aveugle

Dans un modèle GitOps, l'état déclaré vit dans un dépôt et une boucle détecte la différence avec l'état observé. Mais tout écart n'est pas automatiquement une permission de réécrire l'équipement. L'écart peut provenir d'une urgence, d'une action manuelle approuvée, d'une panne d'inventaire ou d'une collecte partielle.

Séparez au minimum :

- **drift détecté** : l'état observé diffère de l'état déclaré ;
- **drift classé** : le système a identifié le périmètre et la confiance dans la preuve ;
- **drift autorisé à corriger** : la politique permet une correction automatique ;
- **drift nécessitant une intervention** : conflit, incertitude ou changement critique.

Une boucle de réconciliation qui corrige toute différence sans contexte peut écraser une restauration d'urgence ou créer une oscillation permanente. La boucle doit respecter les fenêtres de maintenance, les verrous, le budget de changements et les états `UNKNOWN`.


# 16. Stratégie de tests de niveau Expert

## 16.1 La pyramide de tests

Aucun type de test ne suffit à lui seul. Les tests unitaires sont rapides et isolent les fonctions ; les tests de contrat vérifient les interfaces et formes de données ; les tests d'intégration confirment le comportement réel du pilote ; les tests de système valident le workflow complet ; les exercices de panne vérifient la reprise.

Une stratégie raisonnable comprend :

- **tests unitaires** : normalisation, politique, calcul du risque, transitions, empreintes ;
- **tests basés sur propriétés** : invariants sur des entrées nombreuses ou générées ;
- **tests de contrat** : structure attendue des getters et des réponses d'erreur ;
- **tests d'intégration** : sessions réelles sur une plateforme de labo qualifiée ;
- **tests de bout en bout** : demande, approbation, exécution, validation et audit ;
- **tests de résilience** : coupure de transport, timeout, reprise du worker, indisponibilité du stockage ;
- **tests de sécurité** : fuite de secrets, accès hors périmètre, approbation périmée ;
- **tests de charge contrôlée** : saturation progressive et limites de concurrence ;
- **exercices de restauration** : rollback et procédure manuelle suivis de validation.

## 16.2 Tester une machine à états par propriétés

Pour chaque transition, testez le chemin attendu et les transitions interdites. Les propriétés globales à vérifier incluent : un changement confirmé possède un événement de vérification réussie ; une tâche inconnue ne lance aucune écriture avant réconciliation ; une approbation dont le hash n'est plus celui du bundle ne peut pas progresser vers `APPLYING` ; une exécution terminée n'accepte plus de transition d'application.

Exemple de tests avec `pytest` :

```python
import pytest


def test_transition_illegale_est_refusee(fake_store):
    fake_store.states["CHG-1"] = "UNKNOWN"
    with pytest.raises(ValueError):
        transition(
            fake_store,
            change_id="CHG-1",
            new_state="APPLYING",
            actor="worker-test",
            reason_code="unexpected_retry",
        )


def test_transition_autorisee_est_enregistree(fake_store):
    fake_store.states["CHG-2"] = "PREPARED"
    transition(
        fake_store,
        change_id="CHG-2",
        new_state="AWAITING_APPROVAL",
        actor="worker-test",
        reason_code="diff_saved",
        artifact_refs=("artifact-diff-22",),
    )
    assert fake_store.events[-1].new_state == "AWAITING_APPROVAL"
```

Ce snippet suppose un faux stockage `fake_store` implémentant `ChangeStore`; définissez ce fixture dans votre suite. Testez également la course entre deux transitions concurrentes. Si votre stockage est local et non transactionnel, ajoutez un test qui démontre le risque puis migrez vers une opération atomique avant la production distribuée.

## 16.3 Les doubles de test doivent échouer de façon réaliste

Un mock qui retourne toujours une réponse parfaite donne une fausse confiance. Implémentez des doubles de pilotes capables de simuler :

- l'ouverture réussie puis un timeout pendant un getter ;
- l'échec de `open()` ;
- une erreur d'authentification ;
- un getter non pris en charge ;
- un dictionnaire incomplet ;
- un résultat vide valide ;
- un diff vide malgré une intention non vide ;
- l'échec du `discard_config()` ;
- une exception après l'envoi d'un commit ;
- la session qui tombe pendant le postcheck ;
- une fermeture qui échoue ;
- une donnée dont l'horodatage est incohérent.

Ces scénarios testent la capacité du système à afficher l'incertitude au lieu d'inventer un résultat positif.

## 16.4 Tests de contrat avec des données capturées

Les fixtures peuvent être extraites d'un laboratoire ou construites manuellement à partir de données anonymisées. Supprimez les numéros de série, adresses publiques sensibles, noms internes, utilisateurs, secrets et informations client, en préservant la structure utile. Étiquetez chaque fixture par profil de pilote, version, getter et contexte de collecte.

Les tests de contrat devraient vérifier des invariants plutôt qu'une égalité totale trop fragile quand des champs optionnels peuvent évoluer. Exemple : `get_facts()` doit contenir les champs obligatoires pour votre normaliseur, mais le test ne doit pas échouer pour chaque champ informatif ajouté par le pilote si le contrat n'en dépend pas.

## 16.5 Tests d'intégration non destructifs

Avant d'exécuter un test de configuration, vérifiez qu'il est sur un équipement de laboratoire explicitement autorisé, avec un inventaire dont le périmètre est limité à la zone de test. Ne vous contentez pas d'un flag `--test` que l'utilisateur peut oublier de définir ; construisez des contrôles croisés, par exemple une étiquette d'environnement signée, une plage de noms de laboratoire et une identité technique qui n'a aucun droit sur la production.

Les tests d'intégration peuvent vérifier les getters, les données et les propriétés du pilote sans modifier la configuration. Les tests qui modifient la configuration doivent être isolés dans une suite spécifique et inclure une restauration vérifiée. L'exécution de ces tests doit être visible, limitée et répertoriée.

## 16.6 Tester les pannes entre les étapes

Le test le plus intéressant ne simule pas uniquement une exception à l'intérieur d'une fonction ; il simule un processus qui s'arrête après chaque étape. Par exemple :

- après la réservation du verrou ;
- après la collecte pré-changement ;
- après le chargement de candidate ;
- après l'écriture du diff ;
- après l'approbation ;
- juste avant le commit ;
- juste après l'appel du commit ;
- après le commit mais avant l'enregistrement de l'état ;
- pendant la validation post-changement ;
- pendant l'archivage des preuves.

À chaque point d'arrêt, redémarrez le worker et vérifiez qu'il peut retrouver l'état, ne duplique pas l'écriture et ne déclare pas une réussite non prouvée. C'est le test fondamental des workflows durables.

## 16.7 Gérer les tests de performance

Un test de charge doit être prudent avec les équipements réels : commencez par le laboratoire ou par des lectures à faible impact, annoncez la fenêtre et surveillez les sessions de management. Faites varier la concurrence de façon contrôlée et mesurez le débit utile, le temps P95, les timeouts, les erreurs et la charge système. Le but n'est pas de maximiser le nombre de sessions, mais de trouver un régime fiable avec de la capacité de réserve.


# 17. Observabilité : journaux, métriques, traces et preuves

## 17.1 Trois piliers, trois usages

- **Journaux** : expliquent les événements et les décisions. Ils doivent être structurés, datés, corrélés et dépourvus de secrets.
- **Métriques** : montrent les tendances et les seuils : taux d'échec, latence, concurrence, taille de file, taux de conformité ou durée des changements.
- **Traces** : relient les étapes d'une exécution à travers les modules et services. Elles permettent de comprendre où le temps est consommé et à quelle dépendance appartient une erreur.

Les artefacts d'audit constituent un quatrième élément : ils contiennent les preuves durables associées à une demande ou à un changement. Les métriques ne remplacent pas les artefacts, et les logs ne devraient pas être la seule source de preuve d'un changement de configuration.

## 17.2 Journal JSON structuré

Préférez un journal avec des champs nommés à une phrase libre difficile à rechercher. Exemple de forme :

```json
{
  "timestamp": "2026-10-23T20:01:11.328Z",
  "level": "INFO",
  "event": "postcheck_completed",
  "run_id": "run-8a02",
  "change_id": "CHG-2026-1042",
  "device_id": "edge-cm-01",
  "site": "douala-lab",
  "profile": "edge-os-a-netconf",
  "operation": "verify_bgp",
  "status": "PASS",
  "duration_ms": 1830,
  "policy_revision": "edge-change-safety@3.1.0",
  "artifact_ref": "ev-8823"
}
```

Cette forme est illustrative. Les champs `device_id`, `run_id` et `change_id` doivent être stables et non secrets. N'ajoutez pas la sortie complète de `get_config()` à une ligne de journal. Si vous avez besoin de diagnostic détaillé, référencez un artefact restreint et conservé selon une politique de rétention.

## 17.3 Utiliser un logger sans exposer les secrets

```python
import logging

logger = logging.getLogger("napalm_platform")


def log_operation_result(
    *,
    run_id: str,
    device_id: str,
    operation: str,
    status: str,
    duration_ms: int,
    error_type: str | None = None,
) -> None:
    logger.info(
        "network_operation_completed",
        extra={
            "run_id": run_id,
            "device_id": device_id,
            "operation": operation,
            "status": status,
            "duration_ms": duration_ms,
            "error_type": error_type,
        },
    )
```

La prise en charge exacte des champs `extra` dépend du formatter utilisé. Configurez un formatter JSON qui n'imprime que les clés attendues et évitez les objets arbitraires qui pourraient embarquer des identifiants. Les exceptions doivent être filtrées, classées et écrites dans le bon niveau d'accès. Un `logger.exception()` peut révéler des détails du pilote ; assurez-vous que le stockage des traces est à accès restreint et qu'aucun secret ne peut y être inclus.

## 17.4 Métriques utiles

Définissez des métriques associées aux questions opérationnelles :

- nombre de tâches en file, actives, bloquées et en état `UNKNOWN` ;
- taux de réussite des getters par profil et type d'opération ;
- latence P50/P95/P99 des connexions et opérations ;
- nombre de retries et raison du retry ;
- taux de collecte partielle ou non prise en charge ;
- durée de préparation et durée de validation des changements ;
- proportion de gates `PASS`, `FAIL` et `INCONCLUSIVE` ;
- nombre de changements arrêtés, restaurés et réconciliés ;
- taille moyenne et maximale des lots ;
- âge des dernières données pour les équipements critiques ;
- âge des exceptions de conformité ;
- délai entre demande, approbation, application et confirmation.

Évitez les compteurs qui mélangent des opérations de lecture et d'écriture. Évitez également les séries où chaque `run_id` crée une nouvelle dimension métrique à forte cardinalité. Le `run_id` se trouve dans les logs et traces ; les métriques doivent rester agrégées par dimensions limitées.

## 17.5 Alertes actionnables

Une alerte utile indique : le périmètre touché, la gravité, ce qui a été observé, ce qui a été attendu, l'heure du premier événement et le runbook à suivre. « NAPALM failed » n'est pas une alerte opérationnelle suffisante.

Exemples :

- « La collecte BGP est inconclusive sur 4 routeurs de bordure du site A depuis 6 minutes ; les changements sur ce site sont suspendus. »
- « Trois changements sont en état `UNKNOWN` après une perte de transport ; aucun nouveau commit n'est autorisé sur les équipements concernés. »
- « La latence P95 des getters a dépassé le seuil pendant 15 minutes ; la concurrence a été réduite automatiquement. »
- « Une modification de politique augmente les équipements non conformes de 2 % à 37 % ; la promotion de la règle est bloquée en attendant une revue. »

Les seuils et délais sont propres à l'organisation. Testez les alertes avec une simulation et associez-les à un responsable. Une alerte jamais traitée ne constitue pas un contrôle.

## 17.6 Audit et chaîne de preuves

Pour un changement, conservez au minimum : demande, acteur, approbations, versions de code et politiques, révision d'inventaire, profil de capacités, préconditions, candidat, diff, horodatages des étapes, résultat d'application, vérifications post-changement, décision finale et références vers les sauvegardes autorisées.

Pour limiter le risque de modification a posteriori, stockez les événements dans un système avec contrôle d'accès, journalisation des changements et règles de rétention. Des empreintes cryptographiques peuvent aider à détecter une altération, mais elles ne garantissent pas l'origine si les clés, comptes de stockage ou processus qui calculent ces empreintes sont compromis. La gouvernance des accès est aussi importante que le hash.

## 17.7 Objectifs de service pour la plateforme

Une plateforme d'automatisation peut définir des SLO : délai de génération des rapports, taux de collecte réussie sur le périmètre qualifié, durée de mise en quarantaine d'une opération incertaine, disponibilité du service d'orchestration et délai de conservation des preuves. Les SLO ne doivent pas inciter les équipes à convertir des `UNKNOWN` en `PASS` pour améliorer les statistiques.

Suivez séparément l'efficacité et la sécurité. Exemple : « 98 % des collectes terminées dans le délai » est un indicateur de capacité ; « 100 % des changements appliqués ont des preuves d'approbation et un résultat de validation conservés » est un indicateur de gouvernance. Une plateforme rapide mais incapable de prouver ce qu'elle a fait n'est pas une plateforme fiable.


# 18. Performance, capacité et maîtrise de la charge

## 18.1 Mesurer le coût d'une opération complète

Le temps d'une opération n'est pas uniquement la durée rapportée par un getter. Il inclut le temps passé en file, la préparation des paramètres, la récupération du secret, la connexion, l'exécution de la lecture, la normalisation, l'écriture d'artefacts et l'émission de journaux. Mesurez les différentes phases afin de savoir si le goulot d'étranglement est le réseau de management, le pilote, le traitement Python, le stockage ou l'orchestration.

Un découpage de mesure utile :

```text
queue_wait_ms
secret_lookup_ms
connect_ms
operation_ms
normalize_ms
persist_ms
cleanup_ms
total_task_ms
```

Ces champs doivent être obtenus à partir de mesures réelles. Ne les déduisez pas en répartissant artificiellement le temps total. Les résultats doivent être corrélables par `run_id` et par appareil, sans générer une cardinalité excessive dans les métriques agrégées.

## 18.2 Estimer la durée d'un parc

Pour une collecte séquentielle, une approximation de la durée est la somme des temps des équipements. En parallèle, une première approximation est :

```text
durée ≈ max(temps des groupes de tâches) + coût d'orchestration
```

Cette approximation ignore les limites du plan de management, les dépendances entre tâches, les files internes des équipements et les erreurs. Elle sert à formuler une hypothèse, pas à prédire exactement la production.

Supposons 600 appareils et une durée médiane de 2 secondes par collecte. 600 × 2 secondes donne 1 200 secondes en séquentiel dans un scénario idéal sans coût supplémentaire. Avec 20 workers, la borne naïve serait environ 60 secondes, mais ce n'est pas une garantie : les équipements n'ont pas la même latence, les getters ne sont pas indépendants, et les connexions simultanées peuvent réduire les performances. Le résultat réel doit être mesuré en préproduction.

## 18.3 Backpressure plutôt que l'accumulation infinie

Un système qui accepte davantage de tâches qu'il ne peut en traiter finit par accumuler une file de plus en plus vieille. Les utilisateurs peuvent alors prendre des décisions sur des instantanés obsolètes ou créer des doublons parce qu'ils pensent que leur demande a échoué.

Mettez en place :

- une limite de taille de file ;
- des priorités explicites entre collecte périodique, audit ponctuel et changement de production ;
- une date limite de validité pour les tâches ;
- une fusion contrôlée des collectes identiques quand les exigences de fraîcheur le permettent ;
- un rejet ou une mise en attente explicite quand le système est au maximum ;
- un mécanisme d'annulation des tâches devenues obsolètes ;
- une alerte lorsque l'âge de la tâche en tête dépasse un seuil.

Ne supprimez pas silencieusement une tâche de changement parce que la file est pleine. Les demandes de changement doivent recevoir un état clair et rester auditées.

## 18.4 Priorités et classes de travail

Les tâches n'ont pas la même valeur opérationnelle. Une collecte de conformité périodique peut être différée pendant un incident de plan d'administration ; un postcheck de changement peut être prioritaire ; un chargement de configuration ne doit pas se faufiler derrière des milliers de collectes de faible priorité.

Un exemple de classes :

1. **P0 — sécurité et réconciliation** : résultat ambigu, accès de management ou vérification après changement critique ;
2. **P1 — vérification post-changement** : gates qui conditionnent l'expansion des vagues ;
3. **P2 — collecte opérationnelle** : données demandées par un opérateur ou un audit ;
4. **P3 — collecte périodique** : rafraîchissement de fond ;
5. **P4 — exploration ou expérimentation** : tâches non critiques, limitées et isolées.

Ces classes sont un exemple, pas une norme universelle. Une priorité ne doit jamais autoriser une opération interdite par la politique de sécurité. Priorité élevée signifie traitement plus tôt, pas privilège de configuration supérieur.

## 18.5 Caching : utile seulement avec une politique de fraîcheur

Mettre en cache les données peut réduire la charge, mais un cache n'est pas une preuve fraîche par défaut. Chaque entrée doit stocker son heure de collecte, sa provenance, le périmètre, le statut, la version du schéma et une politique de durée de validité. N'utilisez pas les données mises en cache pour une action qui exige des preuves en temps réel, sauf si une règle métier l'autorise explicitement.

Un cache ne doit pas remplacer un résultat d'échec par l'ancien résultat comme s'il venait d'être collecté. Si le système choisit d'utiliser la dernière donnée connue, le rapport doit indiquer son âge et la décision doit le prendre en compte.

## 18.6 Éviter la surcharge inutile des getters

Tous les getters n'ont pas besoin d'être appelés pour chaque demande. Conservez des profils de collecte adaptés aux usages : inventaire, contrôle d'interface, contrôle de protocole, audit de configuration et préconditions de changement. Une collecte qui appelle systématiquement tous les getters disponibles consomme inutilement du temps et peut multiplier les erreurs liées aux fonctionnalités non prises en charge.

Le profil doit préciser les getters requis, optionnels et interdits pour la tâche. Si une collecte requise échoue, elle doit être marquée partielle ou échouée selon la politique. Les getters optionnels ne doivent pas masquer les échecs des champs nécessaires à une décision critique.


# 19. Étendre NAPALM sans fragiliser l'abstraction

## 19.1 Quand ne pas étendre le pilote

Il peut être tentant d'ajouter une méthode personnalisée au pilote pour résoudre un cas particulier. Avant de le faire, vérifiez :

- si un getter NAPALM existant fournit déjà l'information ;
- si la différence est seulement un problème de normalisation dans votre application ;
- si une méthode existante accepte une option configurée officiellement ;
- si l'opération relève d'un outil complémentaire ou d'une API native mieux adaptée ;
- si cette fonctionnalité doit être portable entre plusieurs familles d'équipements.

Une extension du pilote augmente la surface de maintenance. Elle peut se rompre avec une mise à jour et doit être testée contre les attentes de la classe de base et les conventions de retour.

## 19.2 Créer une interface interne plutôt qu'un fork immédiat

Si une fonctionnalité spécifique est nécessaire, vous pouvez définir un adaptateur au niveau de votre application. Il expose l'opération métier à vos modules, puis implémente la fonction via NAPALM si la capacité existe, ou par une méthode spécifique dûment documentée si la politique l'autorise.

```python
from typing import Protocol, Any


class NetworkReadAdapter(Protocol):
    def facts(self) -> dict[str, Any]: ...
    def interfaces(self) -> dict[str, Any]: ...
    def bgp_neighbors(self) -> dict[str, Any]: ...


class NapalmReadAdapter:
    def __init__(self, driver: Any, *, profile: dict[str, Any]):
        self._driver = driver
        self._profile = profile

    def facts(self) -> dict[str, Any]:
        return self._driver.get_facts()

    def interfaces(self) -> dict[str, Any]:
        return self._driver.get_interfaces()

    def bgp_neighbors(self) -> dict[str, Any]:
        if "get_bgp_neighbors" not in self._profile.get("read_operations", []):
            raise NotImplementedError("get_bgp_neighbors n'est pas qualifié pour ce profil")
        return self._driver.get_bgp_neighbors()
```

Le profil qualifié est obligatoire ici : la présence de `get_bgp_neighbors()` ne suffit pas. Les méthodes réelles de l'adaptateur doivent être testées avec les versions et les données visées. Dans une application plus large, injectez l'adaptateur au lieu de construire un pilote à l'intérieur de chaque fonction métier.

## 19.3 Contribuer en amont à NAPALM

Si une correction est générale, reproductible et utile à plusieurs utilisateurs, envisagez une contribution en amont plutôt que de maintenir un fork permanent. Les projets communautaires ont des conventions de style, de tests, de documentation et de compatibilité. Avant de soumettre une évolution, lisez la procédure de contribution, créez un test qui reproduit le défaut et documentez le comportement attendu.

Pour un nouveau pilote, il faut comprendre les contrats de la classe `NetworkDriver`, les formes de données retournées, les exceptions, les tests de la suite et la matrice de prise en charge. Un pilote qui se connecte mais retourne des structures non conformes peut perturber silencieusement les applications qui s'appuient sur l'abstraction commune.

## 19.4 Pourquoi les commandes CLI brutes ne doivent pas devenir la règle

La capacité d'exécuter des commandes brutes peut être utile pour le diagnostic, mais elle affaiblit la portabilité. Une commande propre à un constructeur n'a pas nécessairement d'équivalent sur les autres systèmes. Les données retournées ne sont pas toujours normalisées et peuvent changer de format selon la version du système réseau.

Si une commande spécifique est inévitable :

- enregistrez son objectif métier et son profil de compatibilité ;
- encadrez les commandes autorisées par une liste de contrôle, jamais par une chaîne libre non validée ;
- séparez le parsing de sortie de la commande elle-même ;
- ajoutez des fixtures pour plusieurs versions prises en charge ;
- traitez la sortie vide, les erreurs de commande et les variations de syntaxe ;
- évitez d'utiliser le résultat brut pour une décision critique sans validation ;
- préférez un getter structuré ou une intégration officielle quand elle répond au besoin.

## 19.5 Maintenir un adaptateur par domaine

Dans une architecture plus complexe, séparez les tâches par domaine : lecture d'état, gestion de configuration, validation métier et inventaire. Cela permet d'échanger la source d'une preuve sans réécrire tout le moteur de politique. Par exemple, un audit de service peut combiner NAPALM, un contrôleur de supervision et des tests réseau externes ; chaque source doit préciser sa confiance, son horodatage et son contexte.

Ne cachez pas l'origine d'une donnée derrière un modèle « universel » qui prétend que tous les champs ont les mêmes garanties. Chaque champ normalisé peut porter un attribut de provenance ou de qualité. Le contrat commun doit simplifier la logique métier sans mentir sur les capacités des sources.


# 20. Exposer une CLI ou une API opérationnelle

## 20.1 L'interface ne doit pas contourner les garde-fous

Une CLI est utile pour l'exploitation et le diagnostic. Une API est utile pour CI/CD et les systèmes externes. Dans les deux cas, l'interface doit appeler la même couche d'orchestration. N'implémentez pas une voie CLI avec toutes les validations et une route API qui appelle directement le pilote.

Une interface devrait proposer des opérations distinctes, par exemple :

```text
napalm-platform inventory validate
napalm-platform collect --profile interfaces-read --scope site-a
napalm-platform audit --policy edge-baseline --scope edge-routers
napalm-platform change prepare --bundle change.yaml
napalm-platform change show-diff --change CHG-2026-1042
napalm-platform change approve --change CHG-2026-1042
napalm-platform change apply --change CHG-2026-1042
napalm-platform change status --change CHG-2026-1042
napalm-platform reconcile --change CHG-2026-1042
```

Ces commandes sont une illustration de design. Une interface réelle doit vérifier les rôles, demander des identifiants de changement, limiter les cibles et conserver les événements. Il est recommandé de séparer `prepare`, `approve` et `apply` pour éviter qu'une commande ambiguë fasse tout en une seule étape.

## 20.2 Validation d'entrée stricte

Validez les paramètres avant toute connexion : nom de profil connu, périmètre autorisé, format de ticket, durée raisonnable, fichiers dans le répertoire approuvé, valeurs dans la liste blanche. Ne construisez pas de commandes système en concaténant des chaînes issues de l'utilisateur. Si l'outil utilise des processus externes, passez des arguments structurés et évitez `shell=True`.

Refusez les entrées vides, les noms d'équipements inconnus, les références d'inventaire qui changent entre approbation et application et les chemins qui pointent hors de la zone d'artefacts. La validation d'entrée doit être testée par des cas limites, pas seulement par le parcours normal.

## 20.3 API durable et statut de tâche

Une requête API longue ne devrait généralement pas garder le client HTTP ouvert jusqu'à la fin de centaines de connexions réseau. Créez une tâche durable, retournez un identifiant, puis fournissez un endpoint de statut et des références d'artefacts. Le client doit pouvoir reprendre l'interrogation après un timeout sans soumettre un deuxième changement.

Une API de changement doit appliquer une clé d'idempotence à la demande, être authentifiée et autorisée, limiter les requêtes et vérifier le bundle au moment de l'exécution. Ne comptez pas sur un identifiant de requête fourni par l'utilisateur comme unique garantie d'idempotence ; le stockage doit empêcher les doublons selon un contrat défini.

## 20.4 Authentification, autorisation et séparation des responsabilités

L'authentification dit qui fait la demande. L'autorisation dit ce que cette identité peut faire. La séparation des responsabilités exige que certains changements critiques soient approuvés par une autre identité que celle qui les a proposés, selon la politique organisationnelle.

Appliquez :

- rôle lecture, préparation, approbation et application ;
- autorisation par site, rôle d'équipement et classe de changement ;
- durée de vie limitée des sessions et tokens ;
- limitation de débit ;
- journaux d'accès ;
- refus par défaut quand un rôle ou un périmètre est inconnu ;
- protection contre les attaques de rejeu et les requêtes dupliquées ;
- désactivation rapide d'une identité compromise.

Une revue de sécurité doit tester les voies directes et indirectes. Une personne qui ne peut pas appeler `apply` ne doit pas pouvoir modifier une variable ou un fichier que le worker lit sans validation puis obtenir une application indirecte.

## 20.5 Exposer les erreurs sans exposer le système

Les clients ont besoin d'erreurs utiles, mais pas de traces internes complètes ou de sorties de configuration. Retournez un code stable (`INVALID_INVENTORY`, `CAPABILITY_NOT_QUALIFIED`, `PREFLIGHT_INCONCLUSIVE`, `APPROVAL_EXPIRED`, `CHANGE_STATE_UNKNOWN`) et un identifiant de corrélation. Les détails internes sont accessibles aux opérateurs autorisés via le système de journalisation.


# 21. Projet intégrateur — construire une plateforme de changement contrôlée

## 21.1 Objectif du projet

Le projet final consiste à construire un service de changement réseau qui consomme un bundle versionné, prépare une configuration candidate avec NAPALM, applique les règles de sécurité, demande une approbation, puis applique le changement par canari et vérifie le résultat. La plateforme doit être capable d'arrêter le workflow et de reprendre après redémarrage sans rejouer une écriture dont l'effet n'est pas connu.

Le projet n'est pas validé si le scénario nominal fonctionne uniquement sur un équipement de laboratoire. Il doit également montrer qu'il refuse une donnée non conforme, une approbation périmée, un profil non qualifié, une preuve trop ancienne et un état `UNKNOWN`. Il doit prouver que ces refus ne déclenchent pas de commande de configuration.

## 21.2 Cahier des charges fonctionnel

La solution finale doit fournir au minimum :

1. une CLI pour valider l'inventaire, préparer une demande, examiner son diff, afficher son statut et lancer une réconciliation ;
2. un registre de capacités par profil de pilote ;
3. un fournisseur de secrets injecté, avec un adaptateur de développement explicitement limité au laboratoire ;
4. une enveloppe de résultat et un format d'instantané versionné ;
5. une couche de normalisation qui distingue la donnée absente de l'erreur de collecte ;
6. un moteur de politique donnant une décision structurée et les raisons ;
7. une machine à états persistée avec protection contre les transitions interdites ;
8. un mécanisme de verrouillage empêchant les écritures concurrentes sur une même cible ;
9. une préparation de candidate sans commit implicite ;
10. un système de collecte des approbations lié au hash du candidat et du diff ;
11. une stratégie de vague avec canari et portes de validation ;
12. un statut `UNKNOWN` pour les résultats d'écriture ambigus ;
13. une procédure de réconciliation qui travaille par lecture avant toute nouvelle écriture ;
14. des journaux structurés et des artefacts d'audit ;
15. des tests unitaires, de contrat et d'intégration en laboratoire ;
16. une documentation d'exploitation et un runbook de panne.

## 21.3 Scénario de laboratoire

Utilisez un petit laboratoire composé de deux ou trois appareils virtuels compatibles avec les pilotes retenus, ou d'un banc fourni par une plateforme de formation. Définissez explicitement quels appareils sont autorisés pour les tests d'écriture. L'inventaire de laboratoire doit porter un champ `environment: lab`, et le moteur doit refuser les changements si la cible ne satisfait pas la politique de laboratoire attendue.

Le scénario peut être volontairement limité : changer une description d'interface de test ou ajouter un paramètre non critique clairement défini. Choisissez une opération supportée par votre plateforme. N'utilisez pas un changement de routage global comme premier test de l'orchestrateur.

## 21.4 Exemple de bundle de changement

```yaml
change:
  id: CHG-LAB-0042
  description: "Mettre à jour une description sur une interface de laboratoire"
  environment: lab
  requester: trainee-01
  ticket_ref: LAB-0042
  created_at: "2026-10-23T18:00:00Z"
  expires_at: "2026-10-23T21:00:00Z"
  target:
    device_ids:
      - lab-edge-01
    required_environment: lab
    required_role: edge
  configuration:
    strategy: merge
    template: interface_description.j2
    template_version: "1.0.0"
    variables:
      interface_name: "Ethernet2"
      description: "LAB-MANAGED-TEST"
  policy:
    name: lab-safe-change
    version: "1.0.0"
  rollout:
    canary_size: 1
    max_parallel_devices: 1
    require_postcheck: true
    stop_on_inconclusive: true
```

Le document est un exemple pédagogique et ne constitue pas une syntaxe NAPALM. Le validateur doit vérifier les champs, le type de stratégie autorisé et les limites de périmètre. L'exemple n'inclut aucun secret ; les identifiants sont fournis séparément par le fournisseur de secrets.

## 21.5 Workflow de bout en bout

```text
1. Recevoir bundle
   ├── contrôler schéma, environnement, cible et expiration
   ├── fixer hash des entrées et révision de l'inventaire
   └── créer change_id et clé d'idempotence

2. Préconditions
   ├── verrouiller la cible
   ├── charger le profil de capacités qualifié
   ├── vérifier la connectivité et la fraîcheur des preuves
   ├── collecter le baseline et archiver les preuves
   └── appliquer la politique ; bloquer si inconclusive

3. Préparation
   ├── rendre la configuration déterministement
   ├── contrôles statiques et filtre de commandes interdites
   ├── charger candidate NAPALM
   ├── récupérer le diff et calculer les empreintes
   └── archiver le candidat et le diff ; ne pas committer

4. Approbation
   ├── afficher cible, risque, diff et plan de retour arrière
   ├── collecter l'approbation exigée
   └── vérifier que hash et préconditions n'ont pas changé

5. Application canari
   ├── mettre l'état à APPLYING avant l'écriture
   ├── appliquer selon le profil qualifié
   ├── si résultat ambigu : UNKNOWN, aucune répétition aveugle
   └── si retour certain : VERIFYING

6. Validation post-changement
   ├── vérifier état réseau et tests externes
   ├── PASS : confirmer et conserver la preuve
   ├── FAIL : arrêter la vague et exécuter le runbook approuvé
   └── INCONCLUSIVE : arrêter l'expansion et réconcilier

7. Promotion par vagues
   ├── appliquer les mêmes artefacts approuvés aux cibles autorisées
   ├── respecter le plan topologique et les limites par site
   └── s'arrêter après toute porte de validation non passée

8. Clôture
   ├── enregistrer l'état final et les artefacts
   ├── libérer le verrou seulement lorsque l'état est connu
   ├── publier le rapport et les métriques
   └── conserver les preuves selon la politique de rétention
```

## 21.6 Contrat de vérification de postcheck

Plutôt que d'avoir une fonction qui retourne un seul booléen, modélisez chaque contrôle avec un statut et une référence à sa preuve.

```python
from dataclasses import dataclass
from typing import Literal

CheckStatus = Literal["PASS", "FAIL", "INCONCLUSIVE", "SKIPPED"]

@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    summary: str
    evidence_ref: str | None = None
    reason_code: str | None = None


def overall_status(results: list[CheckResult], *, required_checks: set[str]) -> str:
    by_name = {item.name: item for item in results}
    missing = required_checks - set(by_name)
    if missing:
        return "INCONCLUSIVE"
    required = [by_name[name] for name in required_checks]
    if any(item.status == "FAIL" for item in required):
        return "FAIL"
    if any(item.status != "PASS" for item in required):
        return "INCONCLUSIVE"
    return "PASS"
```

La fonction traite l'absence d'un contrôle obligatoire comme `INCONCLUSIVE`. Dans une version plus stricte, elle devrait aussi refuser les noms en double et vérifier la fraîcheur des références de preuve. La fonction n'enregistre pas elle-même les résultats ; l'orchestrateur doit les conserver avant de calculer et publier le statut global.

## 21.7 Invariants du projet final

Les conditions suivantes doivent être prouvées par des tests automatisés :

- une demande dont l'environnement est `production` ne peut pas être exécutée par le provider de laboratoire ;
- un bundle modifié après approbation devient invalide ;
- une cible qui n'est pas dans le périmètre approuvé est refusée ;
- une méthode de configuration non qualifiée est refusée même si elle existe sur l'objet NAPALM ;
- une preuve obligatoire absente ou trop ancienne n'autorise pas l'application ;
- deux demandes concurrentes sur la même cible ne peuvent pas appliquer simultanément ;
- un échec pendant `load_*_candidate()` est enregistré et la candidate est nettoyée ou réconciliée ;
- un diff inattendu ou trop vaste bloque l'étape d'approbation ;
- l'approbation d'un diff ne peut pas être réutilisée pour une candidate différente ;
- une exception pendant l'appel de commit ne déclenche pas un deuxième commit automatique ;
- une tâche `UNKNOWN` ne peut pas repasser directement à `APPLYING` ;
- les gates critiques doivent toutes passer pour marquer `CONFIRMED` ;
- aucune nouvelle vague ne démarre après un résultat `FAIL` ou `INCONCLUSIVE` ;
- les artefacts de configuration et de journal ne contiennent pas les secrets de test ;
- le worker peut redémarrer depuis chaque état persistant et reprend sans duplications.

## 21.8 Critères d'acceptation

Le projet est accepté si :

1. il fonctionne sur le laboratoire qualifié à partir d'une installation propre documentée ;
2. les préconditions, le candidat, le diff, la décision, l'application et la vérification sont des étapes distinctes ;
3. chaque changement peut être retracé de la demande au résultat final ;
4. les tests vérifient au minimum un scénario nominal, un refus de politique, un timeout de lecture, un échec de préparation, une approbation périmée et une perte de connexion pendant l'application ;
5. le système démontre qu'il passe à `UNKNOWN` au lieu de réessayer aveuglément une écriture ;
6. la procédure de restauration a été testée dans le laboratoire et les preuves sont conservées ;
7. une collecte échouée n'est jamais interprétée comme une absence de voisin ou comme une conformité ;
8. les logs sont structurés et ne contiennent pas les valeurs des secrets ;
9. une personne autre que l'auteur peut suivre le runbook et comprendre les états ;
10. la documentation indique les limites du parc qualifié et les opérations interdites.


# 22. Travaux pratiques experts progressifs

Les travaux pratiques doivent être exécutés dans un laboratoire autorisé. Ils sont ordonnés pour suivre le parcours du cours : commencer par les contrats de données, puis la résilience, ensuite l'orchestration et enfin les changements contrôlés. Chaque TP doit produire des tests et des artefacts, pas seulement une capture d'écran de terminal.

## TP 1 — Schéma et migration d'instantanés

**But :** rendre les instantanés versionnés et comparables. Ajoutez un champ `schema_version`, un `run_id`, les horodatages de collecte et les versions des politiques et profils. Écrivez un validateur qui refuse une comparaison entre schémas incompatibles.

**Livrables :** modèle JSON, validateur, deux fixtures de versions différentes, test d'acceptation et document de migration. **Réussite :** une ancienne fixture est explicitement migrée ou refusée ; aucune valeur manquante n'est inventée silencieusement.

## TP 2 — Registre de capacités par profil

**But :** centraliser les méthodes disponibles, les opérations interdites et la preuve de qualification. Créez deux profils de laboratoire dont les capacités diffèrent. Faites refuser une tâche nécessitant une méthode non qualifiée.

**Livrables :** YAML, validateur de profil, tests de surface et de politique, compte rendu de recette. **Réussite :** la méthode présente sur l'objet mais absente du profil qualifié n'est jamais appelée par le moteur métier.

## TP 3 — Backoff et isolation des erreurs

**But :** gérer les erreurs transitoires sans écraser les pannes permanentes. Injectez un timeout temporaire, une erreur d'authentification et une réponse partielle. Mesurez le nombre d'essais, le délai et le statut produit.

**Livrables :** fonction de retry, taxonomie des erreurs, métriques de tentative et tests. **Réussite :** l'erreur d'authentification n'est pas réessayée sans changement de credentials, et les tentatives respectent le budget de temps.

## TP 4 — Verrou distribué et clé d'idempotence

**But :** simuler deux workers qui tentent de préparer un changement sur le même équipement. Implémentez un stockage de tâche atomique et un verrou partagé ou simulez-le avec un composant de test.

**Livrables :** contrat de lock, tests de concurrence, procédure de récupération après expiration de bail. **Réussite :** une tâche en cours bloque le concurrent et un worker redémarré ne crée pas une deuxième écriture.

## TP 5 — Machine à états et crash recovery

**But :** enregistrer les transitions et redémarrer un workflow à partir d'un état persistant. Injectez un crash après chaque transition.

**Livrables :** machine à états, stockage transactionnel, tests de reprise et journal des événements. **Réussite :** la reprise se fait de manière déterministe et l'état ambigu n'est jamais transformé arbitrairement en succès ou en échec certain.

## TP 6 — Politique d'admission et explication des décisions

**But :** créer des règles de fraîcheur, de périmètre, d'approbation et de criticité. Comparez une décision `allow`, `deny` et `need_evidence`.

**Livrables :** politique versionnée, cas de tests et sortie lisible de décision. **Réussite :** chaque refus produit une raison et chaque autorisation référence des preuves identifiables.

## TP 7 — Bundle immuable et revue du diff

**But :** générer un candidat de configuration, en calculer l'empreinte et conserver le diff. Modifiez ensuite une variable après approbation et vérifiez que le bundle est rejeté.

**Livrables :** manifeste, hash, diff nettoyé, test d'approbation périmée. **Réussite :** l'application n'accepte jamais une configuration dont le hash diffère de la version approuvée.

## TP 8 — Postcheck et gates de canari

**But :** créer au moins trois checks, dont un peut être `INCONCLUSIVE`. Le déploiement doit s'arrêter si un check critique échoue ou devient indéterminé.

**Livrables :** collecteur de postcheck, moteur de gate, simulation de vagues et rapport d'exécution. **Réussite :** aucune vague suivante ne démarre après un échec ou une preuve manquante ; le résultat est archivé.

## TP 9 — Perte de session pendant l'application

**But :** simuler une perte de connexion après que l'appel de commit a été envoyé, sans savoir si l'appareil a appliqué le changement.

**Livrables :** test de fault injection, état `UNKNOWN`, réconciliation en lecture, runbook. **Réussite :** le système ne renvoie pas de commit automatiquement et l'accès de lecture permet de décider de la suite.

## TP 10 — Audit et journalisation anti-fuite

**But :** diffuser de faux secrets dans des messages de test, exceptions et fixtures puis vérifier qu'ils ne sortent pas dans les journaux normaux ou artefacts partagés.

**Livrables :** logger structuré, filtre, tests de fuite, matrice de droits et rétention. **Réussite :** le secret-canari n'apparaît dans aucune sortie non autorisée ; chaque événement porte des identifiants de corrélation.

## TP 11 — Simulation de panne de plateforme

**But :** rendre le stockage d'artefacts indisponible alors qu'un postcheck est en cours. Évaluez comment l'état du changement est conservé et si la vague suivante est bloquée.

**Livrables :** scénario de panne, stratégie de tampon ou de refus, test de restauration du stockage. **Réussite :** le système ne confirme pas un changement s'il ne peut pas conserver les preuves obligatoires conformément à la politique choisie.

## TP 12 — Revue d'architecture

**But :** présenter votre architecture à un autre étudiant ou à un collègue qui joue le rôle de relecteur critique. Faites-lui chercher les voies qui contournent la politique, la réutilisation d'une approbation périmée, les états non couverts et les fuites de secrets.

**Livrables :** diagramme, ADR, matrice de menaces, tests ajoutés à la suite et plan de remédiation. **Réussite :** les recommandations identifiées comme critiques sont traitées ou acceptées explicitement avec un responsable et une date.


# 23. Runbooks : que faire quand la plateforme échoue

Les runbooks sont une partie du système. Ils doivent nommer les symptômes, les vérifications sûres, les critères de décision, les actions interdites et les conditions d'escalade. Un runbook n'est pas un catalogue de commandes universelles : adaptez les commandes de diagnostic au profil du constructeur et à la version validée.

## 23.1 Incident : le worker perd la connexion pendant le commit

**Symptôme :** une tâche passe en erreur pendant l'appel d'application ou juste après. Le résultat de l'équipement n'est pas connu.

**Actions immédiates :**

1. arrêter les retries d'écriture et marquer le changement `UNKNOWN` ;
2. conserver l'ID du changement, le hash du bundle, le diff et les horodatages ;
3. garder le verrou sur la cible jusqu'à ce que l'état soit établi ;
4. vérifier le canal de management indépendamment de l'opération précédente ;
5. effectuer une collecte en lecture et comparer l'état réel au baseline et à l'intention ;
6. consulter les traces du pilote, sans exposer les secrets ;
7. suivre le plan de décision : confirmé, écart connu, restauration approuvée ou escalade.

**Ne pas faire :** rejouer le commit par réflexe, lancer une deuxième candidate sur le même appareil, libérer le verrou simplement parce que le worker est mort, ou déclarer le changement échoué sans preuve.

## 23.2 Incident : le diff contient un changement inattendu

**Symptôme :** le candidat inclut une suppression, un changement de routage ou un bloc qui n'était pas prévu par le bundle.

**Actions :**

1. interdire l'approbation et passer la demande en revue requise ou `ABORTED` selon le workflow ;
2. conserver le diff complet dans un artefact protégé ;
3. comparer l'inventaire, les variables, le template et le profil de capacités à leurs versions enregistrées ;
4. rechercher une dérive initiale ou une configuration non possédée par la plateforme ;
5. tester le rendu avec les mêmes entrées figées ;
6. corriger la cause, générer un nouveau bundle, recalculer les empreintes et recommencer l'approbation.

**Ne pas faire :** retirer manuellement quelques lignes du diff après l'approbation si le candidat n'est plus identique, ni remplacer un hash dans le stockage pour préserver l'ancien accord.

## 23.3 Incident : hausse soudaine des timeouts sur un site

**Symptôme :** la collecte en parallèle produit davantage de délais dépassés sur plusieurs équipements d'un même site.

**Actions :**

1. réduire ou suspendre les nouvelles tâches sur la zone en échec ;
2. consulter les métriques de latence et les erreurs groupées par opération et profil ;
3. vérifier le plan de management, les bastions, les ressources des équipements et la connectivité hors bande ;
4. déterminer si la panne touche le transport, l'authentification, un getter ou le stockage ;
5. utiliser un petit nombre de probes contrôlées plutôt que relancer tout le parc ;
6. rouvrir progressivement le service lorsque les contrôles de santé sont bons.

**Ne pas faire :** multiplier les workers en réaction à la lenteur, retirer tous les timeouts, ou répéter une collecte complète sans examiner la saturation potentielle.

## 23.4 Incident : les résultats de conformité deviennent massivement non conformes

**Symptôme :** après une mise à jour de code, de pilote, d'inventaire ou de politique, le taux de non-conformité augmente brutalement.

**Actions :**

1. identifier la version précise de code, schéma, policy et profil associée au changement ;
2. vérifier si les données ont changé ou si leur structure a changé ;
3. comparer les résultats de l'ancienne et de la nouvelle version sur les mêmes fixtures ;
4. sélectionner quelques cibles représentatives et refaire une collecte contrôlée ;
5. distinguer un vrai écart réseau d'un changement de normalisation ou d'un getter devenu indisponible ;
6. mettre en observation ou revenir à la dernière règle approuvée lorsque la procédure autorise ce retour ;
7. documenter la cause et ajouter un test de non-régression.

**Ne pas faire :** désactiver une règle entière pour faire disparaître l'alerte sans documenter le risque résiduel.

## 23.5 Incident : une candidate reste en attente sur l'équipement

**Symptôme :** la préparation a chargé une candidate, mais une exception survient avant l'approbation ou avant la clôture.

**Actions :**

1. vérifier la machine à états et la dernière preuve enregistrée ;
2. si l'équipement est joignable, vérifier l'état de candidate avec les mécanismes qualifiés ;
3. déterminer si elle doit être conservée pour reprise, abandonnée ou réconciliée ;
4. enregistrer l'issue du nettoyage ;
5. ne libérer le verrou qu'après avoir établi l'absence de conflit ou l'état accepté ;
6. tester le cas dans la suite d'intégration si ce scénario n'est pas déjà couvert.

**Ne pas faire :** supposer que fermer la session a supprimé la candidate sur toutes les plateformes. La portée du nettoyage dépend du pilote et de l'équipement.

## 23.6 Incident : les logs contiennent un secret

**Actions :**

1. restreindre immédiatement l'accès aux logs et artefacts concernés ;
2. déterminer le secret, les systèmes et la période d'exposition ;
3. révoquer ou renouveler le secret selon le plan de réponse ;
4. conserver les éléments nécessaires à l'investigation dans un espace protégé ;
5. supprimer ou expurger les copies selon la politique de sécurité et les possibilités du système de logs ;
6. corriger la voie de fuite et ajouter un test avec un secret-canari ;
7. vérifier l'absence de copies dans CI, cache, rapports et historique d'artefacts.

**Ne pas faire :** seulement supprimer la ligne d'une vue si les données restent dans l'index, les sauvegardes ou les exports.


# 24. Checklist de mise en production

Cette checklist doit être traitée comme un blocage de déploiement. Elle peut être adaptée par profil, mais les dérogations sont documentées avec un responsable, un périmètre et une échéance.

## 24.1 Code, dépendances et environnements

- [ ] Version exacte de Python enregistrée et compatible avec la version NAPALM retenue.
- [ ] Version de NAPALM et versions des pilotes verrouillées et testées ensemble.
- [ ] Dépendances installées depuis des sources approuvées et contrôlées.
- [ ] Build reproductible et manifeste d'artefact conservé.
- [ ] Outils de qualité statique et tests exécutés dans la CI.
- [ ] Aucun secret dans le dépôt, les fixtures, les logs de test ou les artefacts publics.
- [ ] Environnements de développement, laboratoire et production séparés.
- [ ] Mise à jour des dépendances planifiée, testée et assortie d'une procédure de retour.

## 24.2 Inventaire, identité et accès

- [ ] Chaque équipement possède un identifiant stable et un rôle explicite.
- [ ] L'environnement et le site sont validés et non déduits uniquement du nom.
- [ ] Les références d'identifiants pointent vers un fournisseur de secrets approuvé.
- [ ] Les accès lecture et écriture sont séparés lorsque c'est possible.
- [ ] Les droits sont limités par périmètre et vérifiés périodiquement.
- [ ] L'identité de l'équipement est vérifiée par le transport utilisé.
- [ ] Les profils de capacités reflètent les combinaisons réellement qualifiées.
- [ ] Les équipements non qualifiés sont explicitement exclus des opérations correspondantes.

## 24.3 Collecte et données

- [ ] Les statuts `ok`, `partial`, `unsupported`, `failed`, `stale` et `unknown` ont un sens documenté.
- [ ] Les timestamps sont timezone-aware et en UTC dans les artefacts durables.
- [ ] Chaque résultat contient son `run_id`, l'identité de l'équipement et les versions pertinentes.
- [ ] Les schémas sont versionnés et migrés de manière explicite.
- [ ] Une valeur absente ne devient pas automatiquement une liste vide ou un zéro.
- [ ] Les getters requis sont adaptés à la tâche et qualifiés pour le profil.
- [ ] Les comparaisons vérifient la compatibilité des instantanés.
- [ ] Les limites de fraîcheur sont définies pour chaque politique critique.

## 24.4 Changements et garde-fous

- [ ] Préconditions, rendu, préparation, diff, approbation, application et postcheck sont séparés.
- [ ] La demande et le candidat sont liés à des empreintes immuables.
- [ ] L'approbation expire et ne survit pas à un changement du diff ou des entrées.
- [ ] La stratégie merge/replace est justifiée et qualifiée par profil.
- [ ] Les commandes ou propriétés interdites sont vérifiées automatiquement.
- [ ] La politique de concurrence et les verrous sont documentés.
- [ ] Les changements sont déployés par canari et vagues bornées.
- [ ] Un résultat de postcheck inconclusif bloque l'expansion selon la politique.
- [ ] Les opérations d'écriture ambiguës passent à `UNKNOWN` et ne sont pas rejouées automatiquement.
- [ ] Le rollback est testé sur le profil exact et vérifié après exécution.
- [ ] La voie de management et le plan de récupération sont connus.

## 24.5 Observabilité et audit

- [ ] Les logs sont structurés et corrélables par run et changement.
- [ ] Les métriques couvrent latence, erreurs, retries, files, état inconnu et taux de gate.
- [ ] Les alertes désignent des actions et des runbooks.
- [ ] Les artefacts d'audit sont protégés et ont une rétention définie.
- [ ] Les événements de transition ne peuvent pas être modifiés sans trace.
- [ ] Les secrets sont exclus des logs et les tests anti-fuite passent.
- [ ] La sauvegarde et la restauration du stockage ont été testées.
- [ ] Les responsabilités opérationnelles et les escalades sont documentées.

## 24.6 Tests et préparation opérationnelle

- [ ] Tests unitaires, contrat, intégration et bout en bout réussis.
- [ ] Tests de crash recovery effectués après les étapes critiques.
- [ ] Tests de timeout, erreur d'authentification, getter non pris en charge et résultats partiels couverts.
- [ ] Test de perte de session pendant le commit effectué dans le laboratoire.
- [ ] Test de rollback et validation de service terminé.
- [ ] Runbook d'arrêt d'urgence et de réconciliation testé par une personne autre que l'auteur.
- [ ] Restauration manuelle documentée si l'automatisation est indisponible.
- [ ] Plan de déploiement contient critères d'arrêt, de retour et d'escalade.


# 25. Grille d'auto-évaluation du niveau Expert

Attribuez à chaque compétence un niveau : **0 — non acquis**, **1 — comprend le principe**, **2 — réalise en laboratoire**, **3 — explique les limites et teste les échecs**, **4 — exploite de manière reproductible et documentée**.

| Compétence | Niveau 0–4 | Preuve à fournir |
|---|---:|---|
| Modèle de données versionné |  | Schéma, migration et tests de compatibilité |
| Registre de capacités par pilote |  | Profil qualifié, preuve de recette et refus de capacité non prise en charge |
| Fournisseur de secrets |  | Tests de fuite et séparation des rôles |
| Résilience des collectes |  | Retry limité, backoff, classement d'erreurs et mesures |
| Orchestration durable |  | Tâche persistée, clé d'idempotence, verrou et test de reprise |
| Politique explicite |  | Décisions expliquées avec preuves référencées |
| Machine à états de changement |  | Transitions atomiques et transitions interdites testées |
| Préparation déterministe |  | Bundle immuable, candidat et diff hashés |
| Déploiement canari |  | Vagues limitées et gates structurées |
| Réconciliation après ambiguïté |  | Test d'un commit dont la réponse est perdue |
| Rollback qualifié |  | Preuve de restauration et postchecks |
| Observabilité |  | Logs, métriques, alertes et audit corrélés |
| CI/CD et promotion |  | Pipeline documentée et artefact promu sans reconstruction |
| Runbooks |  | Scénario d'incident simulé et retour d'expérience |

Une note moyenne élevée ne compense pas un zéro sur un contrôle de sûreté fondamental. Avant une mise en production, exigez un niveau suffisant sur les compétences qui protègent les écritures, l'approbation, la gestion des secrets et la réconciliation.

## 25.1 Questions de soutenance

Vous devriez pouvoir répondre sans consulter le code :

1. Pourquoi un getter échoué ne prouve-t-il pas qu'aucun voisin n'existe ?
2. Pourquoi les capacités doivent-elles être qualifiées par combinaison de pilote, version et plateforme ?
3. Que faites-vous si le transport tombe immédiatement après l'appel de commit ?
4. Quels champs rendent une approbation liée à un candidat précis ?
5. Comment le système empêche-t-il deux workers d'appliquer un changement simultanément ?
6. Qu'est-ce qui distingue un rollback accepté d'un rollback vérifié ?
7. Pourquoi la disponibilité d'une API ou d'une CLI ne doit-elle pas contourner le moteur de politique ?
8. Comment savez-vous que les mesures avant/après sont comparables ?
9. Comment différenciez-vous un vrai drift réseau d'un changement de normalisation ?
10. Quelles preuves devez-vous conserver pour reconstruire la décision plusieurs mois plus tard ?
11. Quels types de tâches doivent être arrêtés lors d'une saturation du plan de management ?
12. Comment gérez-vous une exception de conformité expirée mais encore présente dans le réseau ?


# 26. Glossaire opérationnel

- **Adaptateur :** couche qui expose une interface interne stable tout en s'appuyant sur NAPALM ou une autre source.
- **Artefact :** fichier ou objet immuable représentant une preuve, un candidat, un diff, une collecte ou une décision.
- **Baseline :** état ou ensemble de règles de référence servant à comparer l'état observé.
- **Backpressure :** mécanisme qui limite l'arrivée de nouvelles tâches lorsque le système ne peut pas les absorber de manière sûre.
- **Canari :** première cible ou premier petit lot d'un déploiement progressif.
- **Candidate :** configuration préparée par le pilote et qui n'est pas nécessairement appliquée.
- **Capability profile :** description versionnée des opérations et mécanismes qualifiés pour une combinaison cible donnée.
- **Circuit breaker :** mécanisme qui suspend les requêtes vers une dépendance après une série d'échecs, puis teste son rétablissement.
- **Commit-confirm :** mécanisme conditionnel dans lequel l'application doit être confirmée avant expiration d'un délai, selon la prise en charge du pilote et du système.
- **Conformité :** respect d'une règle vérifiée à partir de preuves valides, et non simple absence d'erreur.
- **Drift :** différence entre l'état observé et l'état déclaré ou attendu.
- **Gate :** condition explicite qui autorise ou bloque la progression d'un workflow.
- **Hash :** empreinte cryptographique d'une représentation donnée ; utile pour détecter des changements, mais pas preuve autonome de l'origine des données.
- **Idempotence :** propriété selon laquelle une répétition contrôlée ne crée pas d'effet supplémentaire indésirable.
- **Inventaire immuable :** révision figée d'une source d'équipements utilisée pour une demande ou une exécution spécifique.
- **Machine à états :** modèle dans lequel les transitions possibles entre états sont limitées, contrôlées et persistées.
- **NAPALM Validate :** mécanisme du projet NAPALM permettant de comparer l'état obtenu à des attentes déclarées, avec une sémantique à vérifier dans la version utilisée.
- **Normalisation :** transformation de résultats sources vers un contrat interne stable, avec conservation de la provenance.
- **Postcheck :** série de vérifications après un changement pour confirmer l'état fonctionnel attendu.
- **Précondition :** preuve nécessaire avant de commencer une opération.
- **Profil de collecte :** ensemble de getters requis et optionnels adapté à un objectif précis.
- **Réconciliation :** procédure qui relit l'état réel pour déterminer ce qui s'est produit après une interruption ou un résultat ambigu.
- **Rollback :** mécanisme ou procédure de retour vers un état antérieur acceptable, qui doit être qualifié et vérifié.
- **SLO :** objectif mesurable de qualité de service de la plateforme.
- **Snapshot :** ensemble d'observations horodatées dont le périmètre et le statut sont documentés.
- **Unknown state :** état où l'effet d'une opération n'est pas connu de façon suffisamment fiable pour poursuivre en sécurité.
- **Vague :** lot de cibles traité comme une phase distincte d'un déploiement.


# 27. Références officielles et stratégie de veille

La documentation et les matrices peuvent évoluer. Utilisez ces sources comme point de départ, puis consultez la documentation correspondant exactement à la version installée et au profil qualifié. Les tableaux de support peuvent être issus d'une branche documentaire plus ancienne que le paquet installé ; ne supposez pas qu'une page générique reflète toutes les capacités de la dernière version ou de chaque version de pilote.

1. **NAPALM sur PyPI** — versions publiées, métadonnées et exigences Python : https://pypi.org/project/napalm/
2. **Versions officielles du dépôt NAPALM** — historique, notes et changements : https://github.com/napalm-automation/napalm/releases
3. **Documentation NAPALM — appareils pris en charge** — matrice, notes, getters, méthodes de configuration et avertissements spécifiques : https://napalm.readthedocs.io/en/stable/support/
4. **Documentation NAPALM — NetworkDriver** — contrat général, getters et méthodes : https://napalm.readthedocs.io/en/latest/base.html
5. **Documentation NAPALM — modification de configuration** — préparation, diff, commit, abandon, commit-confirm et rollback selon la prise en charge : https://napalm.readthedocs.io/en/stable/tutorials/changing_the_config.html
6. **Documentation NAPALM — validation des déploiements** — formats de validation, modes et rapports : https://napalm.readthedocs.io/en/develop/validate/index.html
7. **Dépôt NAPALM** — code source et guide de contribution : https://github.com/napalm-automation/napalm

### 27.1 Procédure de mise à jour documentaire

À chaque mise à jour NAPALM ou de pilote :

1. enregistrer les versions actuelles et les versions candidates ;
2. lire les notes de version et les changements de dépendances ;
3. réexécuter les tests unitaires, de contrat et d'intégration du profil ;
4. vérifier la forme des résultats des getters et les exceptions ;
5. requalifier toutes les capacités de changement qui peuvent être affectées ;
6. comparer les artefacts avant/après sur un jeu de données représentatif ;
7. mettre à jour le registre de capacités et les ADR ;
8. promouvoir la nouvelle version par le même processus CI/CD que le code ;
9. garder un plan de retour vers la version précédemment qualifiée.

Une mise à jour du paquet ne doit pas être déployée directement en production parce qu'elle est « mineure ». Elle peut modifier un parsing, une dépendance, une valeur retournée ou un comportement du pilote. La qualification doit être proportionnée au risque et aux zones touchées.


# Conclusion — l'expertise est la capacité de ne pas agir sans preuve

Le parcours NAPALM se termine ici, mais l'automatisation réseau reste une discipline d'ingénierie continue. Le niveau Débutant vous a appris à dialoguer avec les équipements. Le niveau Intermédiaire vous a appris à structurer les scripts, à collecter les états, à comparer les données et à produire des rapports. Le niveau Expert ajoute le contrôle des capacités réelles, les contrats de données, la résilience, les politiques, les workflows durables, les changements par vagues, la réconciliation et les preuves d'audit.

Le principe central est simple : **l'automatisation ne doit pas prétendre savoir ce qu'elle ne sait pas**. Une collecte indisponible n'est pas une conformité, un diff court n'est pas une garantie de sûreté, un retour de fonction n'est pas toujours une preuve de service, et une exception après un commit ne veut pas dire que l'application n'a pas eu lieu. Une plateforme fiable sait distinguer ces cas, s'arrêter lorsque c'est nécessaire et reprendre à partir de faits établis.

Vous pouvez considérer la formation comme aboutie lorsque vous êtes en mesure de montrer non seulement le scénario réussi, mais aussi les scénarios où la plateforme refuse d'agir, les scénarios où elle s'arrête à mi-parcours et la procédure utilisée pour restaurer ou réconcilier l'état. C'est cette capacité qui transforme un script d'automatisation en système d'exploitation réseau digne de confiance.
