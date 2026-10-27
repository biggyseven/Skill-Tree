"""Chargement du contenu externe (content/) vers la base SQLite."""
from __future__ import annotations

import json
import re
from . import db_compat as sqlite3
from dataclasses import dataclass
from pathlib import Path

from .domain import ProofKind

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
PROOF_KINDS = {kind.value for kind in ProofKind}
LAB_MODES = {"exact", "contains", "regex", "all", "any"}
NODE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
DEVICE_TYPES = {
    "router",
    "switch",
    "pc",
    "plc",
    "firewall",
    "server",
    "cloud",
    "wifi",
    "laptop",
    "spine",
    "leaf",
    "apic",
    "vpc",
    "subnet",
}


class ContentError(Exception):
    """Contenu invalide ou incomplet (message destiné à l'utilisateur)."""


@dataclass(frozen=True)
class ChallengeSpec:
    expected_topology: dict
    time_limit: int
    brief: dict


@dataclass(frozen=True)
class NodeSpec:
    id: str
    title: str
    description: str
    category: str
    module: str
    order: int
    prereqs: tuple[str, ...]
    requirements: tuple[tuple[str, int], ...]
    node_type: str = "skill"
    challenge: ChallengeSpec | None = None


@dataclass(frozen=True)
class QuestionSpec:
    prompt: str
    choices: tuple[str, ...]
    answer: int | str
    explanation: str
    question_type: str = "qcm"
    answer_regex: str | None = None


@dataclass(frozen=True)
class LabData:
    node_id: str
    mode: str
    pattern: str
    prompt: str
    hint: str
    kind: str = "text"


@dataclass(frozen=True)
class TerminalData:
    node_id: str
    prompt: str
    answer: str
    pattern: str
    explanation: str = ""


@dataclass(frozen=True)
class LoadReport:
    nodes: int
    edges: int
    quiz_questions: int
    exam_questions: int
    labs: int
    lessons: int = 0
    removed_nodes: tuple[str, ...] = ()


def _read_json(path: Path):
    if not path.is_file():
        raise ContentError(f"Fichier de contenu manquant : {path}")
    try:
        with path.open(encoding="utf-8-sig") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise ContentError(
            f"JSON invalide dans {path} (ligne {error.lineno}, colonne {error.colno}) : {error.msg}"
        )
    except OSError as error:
        raise ContentError(f"Lecture impossible de {path} : {error}")


def _text(value, field: str, where: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ContentError(f"{where} : « {field} » doit être une chaîne.")
    text = value.strip()
    if not text and not allow_empty:
        raise ContentError(f"{where} : « {field} » ne peut pas être vide.")
    return text


def _integer(value, field: str, where: str, low: int | None = None, high: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ContentError(f"{where} : « {field} » doit être un entier.")
    if low is not None and value < low:
        raise ContentError(f"{where} : « {field} » doit être >= {low}.")
    if high is not None and value > high:
        raise ContentError(f"{where} : « {field} » doit être <= {high}.")
    return value


def _string_list(value, field: str, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ContentError(f"{where} : « {field} » doit être une liste de chaînes non vides.")
    return [item.strip() for item in value]


def _parse_expected_topology(value, where: str) -> dict:
    if not isinstance(value, dict):
        raise ContentError(f"{where} : « expected_topology » doit être un objet.")

    raw_nodes = value.get("nodes")
    if not isinstance(raw_nodes, dict) or not raw_nodes:
        raise ContentError(f"{where} : « expected_topology.nodes » doit être un objet non vide.")
    nodes: dict[str, int] = {}
    for device_type, count in raw_nodes.items():
        if device_type not in DEVICE_TYPES:
            raise ContentError(
                f"{where} : type d'équipement attendu inconnu « {device_type} »."
            )
        nodes[device_type] = _integer(count, f"nodes.{device_type}", where, 1, 100)

    raw_connections = value.get("connections")
    if not isinstance(raw_connections, list):
        raise ContentError(f"{where} : « expected_topology.connections » doit être une liste.")
    connections: list[dict[str, str]] = []
    for index, raw in enumerate(raw_connections, 1):
        connection_where = f"{where}.connections[{index}]"
        if not isinstance(raw, dict):
            raise ContentError(f"{connection_where} : un objet est attendu.")
        source = _text(raw.get("from"), "from", connection_where)
        target = _text(raw.get("to"), "to", connection_where)
        if source not in nodes or target not in nodes:
            raise ContentError(
                f"{connection_where} : chaque extrémité doit correspondre à un type d'équipement déclaré."
            )
        connections.append({"from": source, "to": target})
    raw_constraints = value.get("constraints", [])
    if not isinstance(raw_constraints, list):
        raise ContentError(f"{where} : « expected_topology.constraints » doit être une liste.")

    constraints: list[dict] = []
    for index, raw in enumerate(raw_constraints, 1):
        constraint_where = f"{where}.constraints[{index}]"
        if not isinstance(raw, dict):
            raise ContentError(f"{constraint_where} : un objet est attendu.")
        kind = _text(raw.get("kind"), "kind", constraint_where)
        if kind in {"all_pairs", "min_peer_count"}:
            source = _text(raw.get("from"), "from", constraint_where).lower()
            target = _text(raw.get("to"), "to", constraint_where).lower()
            if source not in nodes or target not in nodes:
                raise ContentError(
                    f"{constraint_where} : « from » et « to » doivent désigner des types déclarés dans nodes."
                )
            if source == target and kind == "all_pairs":
                raise ContentError(
                    f"{constraint_where} : « all_pairs » exige deux types distincts."
                )
            rule = {"kind": kind, "from": source, "to": target}
            if kind == "min_peer_count":
                minimum = _integer(raw.get("min_peers"), "min_peers", constraint_where, 1, 100)
                if minimum > nodes[target]:
                    raise ContentError(
                        f"{constraint_where} : « min_peers » dépasse le nombre attendu de « {target} »."
                    )
                rule["min_peers"] = minimum
            constraints.append(rule)
        elif kind == "separated_by":
            source = _text(raw.get("from"), "from", constraint_where).lower()
            target = _text(raw.get("to"), "to", constraint_where).lower()
            via = _text(raw.get("via"), "via", constraint_where).lower()
            if source not in nodes or target not in nodes or via not in nodes:
                raise ContentError(
                    f"{constraint_where} : « from », « to » et « via » doivent désigner "
                    "des types déclarés dans nodes."
                )
            if len({source, target, via}) != 3:
                raise ContentError(
                    f"{constraint_where} : « separated_by » exige trois types distincts."
                )
            constraints.append({"kind": kind, "from": source, "to": target, "via": via})
        elif kind == "connected":
            device_type = _text(raw.get("type"), "type", constraint_where).lower()
            if device_type not in nodes:
                raise ContentError(
                    f"{constraint_where} : « type » doit désigner un type déclaré dans nodes."
                )
            constraints.append({"kind": kind, "type": device_type})
        else:
            raise ContentError(
                f"{constraint_where} : règle « {kind} » inconnue "
                "(attendu : all_pairs, min_peer_count, connected ou separated_by)."
            )

    if not connections:
        raise ContentError(f"{where} : le défi doit exiger au moins une connexion.")

    return {"nodes": nodes, "connections": connections, "constraints": constraints}


def _parse_challenge_brief(value, where: str) -> dict:
    """Valide le mini-brief pédagogique optionnel d'un défi d'architecture."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ContentError(f"{where} : « challenge.brief » doit être un objet.")
    context = _text(value.get("context"), "brief.context", where)
    evaluation_scope = _text(value.get("evaluation_scope"), "brief.evaluation_scope", where)
    debrief = _text(value.get("debrief"), "brief.debrief", where)

    def text_items(field: str, minimum: int, maximum: int) -> list[str]:
        items = _string_list(value.get(field), f"brief.{field}", where)
        if not minimum <= len(items) <= maximum:
            raise ContentError(
                f"{where} : « brief.{field} » doit contenir entre {minimum} et {maximum} éléments."
            )
        return items

    objectives = text_items("objectives", 2, 6)
    mission_steps = text_items("mission_steps", 3, 6)
    success_criteria = text_items("success_criteria", 2, 6)
    hints = text_items("hints", 2, 4)
    raw_concepts = value.get("concepts")
    if not isinstance(raw_concepts, list) or not 2 <= len(raw_concepts) <= 6:
        raise ContentError(f"{where} : « brief.concepts » doit contenir entre 2 et 6 notions.")
    concepts: list[dict[str, str]] = []
    for index, raw in enumerate(raw_concepts, 1):
        concept_where = f"{where}.brief.concepts[{index}]"
        if not isinstance(raw, dict):
            raise ContentError(f"{concept_where} : un objet est attendu.")
        concepts.append({
            "term": _text(raw.get("term"), "term", concept_where),
            "explanation": _text(raw.get("explanation"), "explanation", concept_where),
        })
    return {
        "context": context,
        "objectives": objectives,
        "concepts": concepts,
        "mission_steps": mission_steps,
        "success_criteria": success_criteria,
        "hints": hints,
        "evaluation_scope": evaluation_scope,
        "debrief": debrief,
    }


def _parse_nodes(path: Path) -> list[NodeSpec]:
    payload = _read_json(path)
    if not isinstance(payload, list):
        raise ContentError(f"{path.name} : la racine doit être une liste de nœuds.")
    if not payload:
        raise ContentError(f"{path.name} : aucun nœud déclaré.")

    nodes: list[NodeSpec] = []
    seen: set[str] = set()

    for index, raw in enumerate(payload, 1):
        where = f"{path.name}[{index}]"
        if not isinstance(raw, dict):
            raise ContentError(f"{where} : un nœud doit être un objet JSON.")

        node_id = _text(raw.get("id"), "id", where)
        if not NODE_ID_RE.match(node_id):
            raise ContentError(
                f"{where} : identifiant « {node_id} » invalide "
                "(minuscules, chiffres, tirets et underscores uniquement)."
            )
        if node_id in seen:
            raise ContentError(f"{where} : identifiant « {node_id} » en double dans {path.name}.")
        seen.add(node_id)

        title = _text(raw.get("title"), "title", where)
        description = _text(raw.get("description", ""), "description", where, allow_empty=True)
        category = _text(raw.get("category", "Général"), "category", where)
        
        # CORRECTION 1 : On extrait le module avec une valeur par défaut
        module = _text(raw.get("module", "Administration Réseaux"), "module", where)
        
        order = _integer(raw.get("order", 0), "order", where)
        node_type = _text(raw.get("type", "skill"), "type", where)
        if node_type not in {"skill", "architecture"}:
            raise ContentError(f"{where} : type de nœud « {node_type} » inconnu.")

        challenge = None
        raw_challenge = raw.get("challenge")
        challenge_file = raw.get("challenge_file")
        if node_type == "architecture":
            if raw_challenge is not None and challenge_file is not None:
                raise ContentError(
                    f"{where} : utilise soit « challenge », soit « challenge_file », pas les deux."
                )
            if challenge_file is not None:
                challenge_name = _text(challenge_file, "challenge_file", where)
                content_root = path.parent.resolve()
                challenge_path = (content_root / challenge_name).resolve()
                try:
                    challenge_path.relative_to(content_root)
                except ValueError:
                    raise ContentError(
                        f"{where} : « challenge_file » doit rester dans le dossier content/."
                    )
                raw_challenge = _read_json(challenge_path)
            if not isinstance(raw_challenge, dict):
                raise ContentError(
                    f"{where} : un nœud architecture exige un objet « challenge » "
                    "ou un fichier « challenge_file »."
                )
            time_limit = _integer(raw_challenge.get("time_limit"), "time_limit", where, 1, 3600)
            expected_topology = raw_challenge.get("expected_topology")
            challenge = ChallengeSpec(
                expected_topology=_parse_expected_topology(expected_topology, where),
                time_limit=time_limit,
                brief=_parse_challenge_brief(raw_challenge.get("brief"), where),
            )
        elif raw_challenge is not None or challenge_file is not None:
            raise ContentError(
                f"{where} : seul un nœud architecture peut définir « challenge » "
                "ou « challenge_file »."
            )

        prereqs: list[str] = []
        for prereq in _string_list(raw.get("prereqs", []), "prereqs", where):
            if prereq == node_id:
                raise ContentError(f"{where} : le nœud « {node_id} » ne peut pas être son propre prérequis.")
            if prereq in prereqs:
                raise ContentError(f"{where} : prérequis « {prereq} » en double.")
            prereqs.append(prereq)

        raw_requirements = raw.get("requirements")
        if not isinstance(raw_requirements, list) or not raw_requirements:
            raise ContentError(f"{where} : « requirements » doit être une liste non vide.")

        requirements: list[tuple[str, int]] = []
        kinds: set[str] = set()
        for req_index, raw_requirement in enumerate(raw_requirements, 1):
            req_where = f"{where}.requirements[{req_index}]"
            if not isinstance(raw_requirement, dict):
                raise ContentError(f"{req_where} : un objet JSON est attendu.")
            kind = _text(raw_requirement.get("kind"), "kind", req_where)
            if kind not in PROOF_KINDS:
                raise ContentError(
                    f"{req_where} : kind « {kind} » inconnu "
                    f"(attendu : {', '.join(sorted(PROOF_KINDS))})."
                )
            if kind in kinds:
                raise ContentError(f"{req_where} : exigence « {kind} » en double pour « {node_id} ».")
            kinds.add(kind)
            min_score = _integer(raw_requirement.get("min_score", 80), "min_score", req_where, 0, 100)
            requirements.append((kind, min_score))

        if node_type == "architecture" and ("manual", 100) not in requirements:
            raise ContentError(
                f"{where} : un nœud architecture doit exiger une preuve manual avec min_score 100."
            )

        nodes.append(
            NodeSpec(
                id=node_id,
                title=title,
                description=description,
                category=category,
                module=module, # CORRECTION 2 : On passe le module à NodeSpec
                order=order,
                prereqs=tuple(prereqs),
                requirements=tuple(requirements),
                node_type=node_type,
                challenge=challenge,
            )
        )

    # Les prérequis inconnus sont ignorés au chargement des arêtes dans _write().
    # On laisse passer le contenu afin qu'une référence obsolète ne bloque pas le démarrage.
    _check_cycles(nodes, path.name)
    return nodes


def _check_cycles(nodes: list[NodeSpec], filename: str) -> None:
    graph = {node.id: node.prereqs for node in nodes}
    state: dict[str, int] = {}

    def visit(node_id: str, trail: tuple[str, ...]) -> None:
        current = state.get(node_id, 0)
        if current == 1:
            cycle = " -> ".join(trail + (node_id,))
            raise ContentError(f"{filename} : cycle de prérequis détecté : {cycle}.")
        if current == 2:
            return
        state[node_id] = 1
        for prereq in graph[node_id]:
            # Une référence absente de nodes.json ne fait pas partie du graphe chargé.
            if prereq in graph:
                visit(prereq, trail + (node_id,))
        state[node_id] = 2

    for node in nodes:
        visit(node.id, ())


def _parse_bank(directory: Path, scope: str, node_ids: set[str]) -> dict[str, list[QuestionSpec]]:
    if not directory.exists():
        return {}
    if not directory.is_dir():
        raise ContentError(f"{directory} doit être un dossier.")

    bank: dict[str, list[QuestionSpec]] = {}
    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if not isinstance(payload, dict):
            raise ContentError(f"{path} : la racine doit être un objet JSON.")

        node_id = _text(payload.get("node_id"), "node_id", path.name)
        if node_id != path.stem:
            raise ContentError(
                f"{path} : node_id « {node_id} » ne correspond pas au nom de fichier « {path.stem}.json »."
            )
        if node_id not in node_ids:
            raise ContentError(f"{path} : node_id « {node_id} » absent de nodes.json.")
        if node_id in bank:
            raise ContentError(f"{path} : plusieurs fichiers {scope} pour le nœud « {node_id} ».")

        raw_scope = payload.get("scope")
        # Un scope absent/null/vide prend celui du dossier (quiz ou exam).
        if raw_scope is None or (isinstance(raw_scope, str) and not raw_scope.strip()):
            declared_scope = scope
        else:
            declared_scope = _text(raw_scope, "scope", path.name)
        if declared_scope != scope:
            raise ContentError(
                f"{path} : scope « {declared_scope} » inattendu (attendu : « {scope} »)."
            )

        raw_questions = payload.get("questions")
        if not isinstance(raw_questions, list) or not raw_questions:
            raise ContentError(f"{path} : « questions » doit être une liste non vide.")

        questions: list[QuestionSpec] = []
        prompts: set[str] = set()
        for index, raw in enumerate(raw_questions, 1):
            where = f"{path.name}.questions[{index}]"
            if not isinstance(raw, dict):
                raise ContentError(f"{where} : un objet JSON est attendu.")

            prompt = _text(raw.get("prompt"), "prompt", where)
            key = " ".join(prompt.lower().split())
            if key in prompts:
                raise ContentError(f"{where} : énoncé en double pour le nœud « {node_id} ».")
            prompts.add(key)

            question_type = _text(raw.get("type", "qcm"), "type", where)
            if question_type == "qcm":
                choices = _string_list(raw.get("choices"), "choices", where)
                if len(choices) != 4:
                    raise ContentError(f"{where} : un QCM doit contenir exactement quatre choix.")
                if len(set(choices)) != len(choices):
                    raise ContentError(f"{where} : propositions en double.")
                answer = _integer(raw.get("answer"), "answer", where, 0, len(choices) - 1)
                answer_regex = None
            elif question_type in {"input", "terminal"}:
                choices = []
                answer = _text(raw.get("answer"), "answer", where)
                answer_regex = _text(raw.get("regex"), "regex", where)
                _check_regex(answer_regex, path)
                if re.fullmatch(answer_regex, answer, re.IGNORECASE) is None:
                    raise ContentError(f"{where} : « answer » ne correspond pas au motif regex.")
            else:
                raise ContentError(
                    f"{where} : type de question « {question_type} » inconnu "
                    "(attendu : qcm, input ou terminal)."
                )
            explanation = _text(raw.get("explanation", ""), "explanation", where, allow_empty=True)

            questions.append(
                QuestionSpec(
                    prompt=prompt,
                    choices=tuple(choices),
                    answer=answer,
                    explanation=explanation,
                    question_type=question_type,
                    answer_regex=answer_regex,
                )
            )

        bank[node_id] = questions

    return bank


def load_lessons(
    directory: str | Path = CONTENT_DIR,
    node_ids: set[str] | None = None,
) -> dict[str, str]:
    """Lit les leçons Markdown et les associe au nœud nommé par le fichier."""
    directory = Path(directory)
    lessons_dir = directory / "lessons"
    if not lessons_dir.exists():
        return {}
    if not lessons_dir.is_dir():
        raise ContentError(f"{lessons_dir} doit être un dossier.")

    if node_ids is None:
        node_ids = {node.id for node in _parse_nodes(directory / "nodes.json")}

    lessons: dict[str, str] = {}
    for path in sorted(lessons_dir.glob("*.md")):
        node_id = path.stem
        if not NODE_ID_RE.fullmatch(node_id):
            raise ContentError(f"{path} : identifiant de nœud invalide dans le nom de fichier.")
        if node_id not in node_ids:
            raise ContentError(f"{path} : nœud « {node_id} » absent de nodes.json.")
        if node_id in lessons:
            raise ContentError(f"{path} : plusieurs leçons pour le nœud « {node_id} ».")
        try:
            content = path.read_text(encoding="utf-8").strip()
        except OSError as error:
            raise ContentError(f"Lecture impossible de {path} : {error}")
        if not content:
            raise ContentError(f"{path} : la leçon ne peut pas être vide.")
        lessons[node_id] = content

    return lessons


def find_lab_dir(
    node_id: str,
    directory: str | Path = CONTENT_DIR,
) -> Path | None:
    """Retourne le dossier Docker dont lab.json cible ce nœud."""
    labs_dir = Path(directory) / "labs"
    direct = labs_dir / node_id
    if (direct / "lab.json").is_file():
        return direct

    if labs_dir.is_dir():
        for candidate in sorted(labs_dir.iterdir()):
            config = candidate / "lab.json"
            if not config.is_file():
                continue
            try:
                payload = json.loads(config.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and payload.get("node_id") == node_id:
                return candidate
    return None


def _check_regex(pattern: str, path: Path) -> None:
    try:
        re.compile(pattern)
    except re.error as error:
        raise ContentError(f"{path} : motif regex invalide « {pattern} » ({error}).")


def _parse_labs(directory: Path, node_ids: set[str]) -> dict[str, LabData]:
    if not directory.exists():
        return {}
    if not directory.is_dir():
        raise ContentError(f"{directory} doit être un dossier.")

    labs: dict[str, LabData] = {}
    for entry in sorted(directory.iterdir()):
        if entry.is_dir():
            lab = _parse_docker_lab(entry, node_ids)
        elif entry.suffix == ".json":
            lab = _parse_text_lab(entry, node_ids)
        else:
            continue

        if lab.node_id in labs:
            raise ContentError(f"{entry} : plusieurs labs pour le nœud « {lab.node_id} ».")
        labs[lab.node_id] = lab

    return labs


def _parse_terminals(directory: Path, node_ids: set[str]) -> dict[str, TerminalData]:
    if not directory.exists():
        return {}
    if not directory.is_dir():
        raise ContentError(f"{directory} doit être un dossier.")

    terminals: dict[str, TerminalData] = {}
    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if not isinstance(payload, dict):
            raise ContentError(f"{path} : la racine doit être un objet JSON.")
        node_id = _text(payload.get("node_id"), "node_id", path.name)
        if node_id != path.stem:
            raise ContentError(
                f"{path} : node_id « {node_id} » ne correspond pas au nom de fichier."
            )
        if node_id not in node_ids:
            raise ContentError(f"{path} : node_id « {node_id} » absent de nodes.json.")
        if node_id in terminals:
            raise ContentError(f"{path} : plusieurs spécifications terminal pour « {node_id} ».")

        prompt = _text(payload.get("prompt"), "prompt", path.name)
        answer = _text(payload.get("answer"), "answer", path.name)
        pattern = _text(payload.get("regex"), "regex", path.name)
        _check_regex(pattern, path)
        if re.fullmatch(pattern, answer, re.IGNORECASE) is None:
            raise ContentError(f"{path} : « answer » ne correspond pas au motif regex.")
        explanation = _text(
            payload.get("explanation", ""),
            "explanation",
            path.name,
            allow_empty=True,
        )
        terminals[node_id] = TerminalData(node_id, prompt, answer, pattern, explanation)

    return terminals


def _parse_text_lab(path: Path, node_ids: set[str]) -> LabData:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ContentError(f"{path} : la racine doit être un objet JSON.")

    node_id = _text(payload.get("node_id"), "node_id", path.name)
    if node_id != path.stem:
        raise ContentError(
            f"{path} : node_id « {node_id} » ne correspond pas au nom de fichier « {path.stem}.json »."
        )
    if node_id not in node_ids:
        raise ContentError(f"{path} : node_id « {node_id} » absent de nodes.json.")

    kind = _text(payload.get("kind", "text"), "kind", path.name)
    if kind != "text":
        raise ContentError(
            f"{path} : kind « {kind} » invalide pour un fichier .json "
            "(utilise un dossier <node_id>/ pour un lab docker)."
        )

    mode = _text(payload.get("mode"), "mode", path.name)
    if mode not in LAB_MODES:
        raise ContentError(
            f"{path} : mode « {mode} » inconnu (attendu : {', '.join(sorted(LAB_MODES))})."
        )

    raw_pattern = payload.get("pattern")
    if mode in ("all", "any"):
        if isinstance(raw_pattern, str):
            patterns = [raw_pattern.strip()]
        else:
            patterns = _string_list(raw_pattern, "pattern", path.name)
        if not patterns or not all(patterns):
            raise ContentError(f"{path} : le mode « {mode} » exige au moins un motif non vide.")
        for pattern in patterns:
            _check_regex(pattern, path)
        stored = json.dumps(patterns, ensure_ascii=False)
    else:
        stored = _text(raw_pattern, "pattern", path.name)
        if mode == "regex":
            _check_regex(stored, path)

    prompt = _text(payload.get("prompt"), "prompt", path.name)
    hint = _text(payload.get("hint", ""), "hint", path.name, allow_empty=True)

    return LabData(
        node_id=node_id,
        kind="text",
        mode=mode,
        pattern=stored,
        prompt=prompt,
        hint=hint,
    )


def _parse_docker_lab(directory: Path, node_ids: set[str]) -> LabData:
    path = directory / "lab.json"
    if not path.is_file():
        raise ContentError(f"{directory} : lab.json manquant.")

    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ContentError(f"{path} : la racine doit être un objet JSON.")

    # Le nom du dossier reste libre (par exemple lab_ospf/) : c'est
    # lab.json.node_id qui identifie le nœud destinataire.
    node_id = _text(payload.get("node_id"), "node_id", path.name)
    if node_id not in node_ids:
        raise ContentError(f"{path} : node_id « {node_id} » absent de nodes.json.")

    kind = _text(payload.get("kind", "docker"), "kind", path.name)
    if kind != "docker":
        raise ContentError(
            f"{path} : kind « {kind} » invalide pour un dossier de lab (attendu : « docker »)."
        )

    image = _text(payload.get("image", "skilltree/lab:latest"), "image", path.name)
    timeout = _integer(payload.get("timeout", 60), "timeout", path.name, 1, 600)
    prompt = _text(payload.get("prompt"), "prompt", path.name)
    hint = _text(payload.get("hint", ""), "hint", path.name, allow_empty=True)

    for script in ("setup.sh", "check.sh", "consigne.md"):
        if not (directory / script).is_file():
            raise ContentError(f"{directory} : fichier « {script} » manquant.")

    return LabData(
        node_id=node_id,
        kind="docker",
        mode="exact",
        pattern="",
        prompt=prompt,
        hint=hint,
    )


def _check_requirements(
    nodes: list[NodeSpec],
    quizzes: dict[str, list[QuestionSpec]],
    exams: dict[str, list[QuestionSpec]],
    labs: dict[str, LabData],
    terminals: dict[str, TerminalData],
    directory: Path,
) -> None:
    for node in nodes:
        for kind, _ in node.requirements:
            if kind == "quiz" and node.id not in quizzes:
                raise ContentError(
                    f"Le nœud « {node.id} » exige un quiz mais "
                    f"{directory / 'quiz' / (node.id + '.json')} est absent."
                )
            if kind == "exam" and node.id not in exams:
                raise ContentError(
                    f"Le nœud « {node.id} » exige un examen mais "
                    f"{directory / 'exam' / (node.id + '.json')} est absent."
                )
            if kind == "lab" and node.id not in labs:
                raise ContentError(
                    f"Le nœud « {node.id} » exige un lab mais "
                    f"{directory / 'labs' / (node.id + '.json')} est absent."
                )
            if kind == "terminal" and node.id not in terminals:
                raise ContentError(
                    f"Le nœud « {node.id} » exige un terminal mais "
                    f"{directory / 'terminal' / (node.id + '.json')} est absent."
                )
    requirements_by_node = {
        node.id: {kind for kind, _ in node.requirements}
        for node in nodes
    }
    for node_id in terminals:
        if "terminal" not in requirements_by_node[node_id]:
            raise ContentError(
                f"Le nœud « {node_id} » a une spécification terminal mais aucune exigence terminal."
            )


def _write(
    conn: sqlite3.Connection,
    nodes: list[NodeSpec],
    quizzes: dict[str, list[QuestionSpec]],
    exams: dict[str, list[QuestionSpec]],
    labs: dict[str, LabData],
    terminals: dict[str, TerminalData],
) -> set[str]:
    existing = {row["id"] for row in conn.execute("SELECT id FROM nodes")}
    removed = existing - {node.id for node in nodes}

    with conn:
        conn.execute("DELETE FROM edges")
        conn.execute("DELETE FROM requirements")
        conn.execute("DELETE FROM lab_specs")
        conn.execute("DELETE FROM questions")
        conn.execute("DELETE FROM terminal_specs")
        conn.execute("DELETE FROM challenge_sessions")
        conn.execute("DELETE FROM exam_sessions")
        conn.execute("DELETE FROM challenges")
        for node_id in removed:
            conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))

        for node in nodes:
            # CORRECTION 3 : La requête SQL inclut maintenant le champ module
            conn.execute(
                "INSERT INTO nodes (id, title, description, category, module, sort_order)"
                " VALUES (?, ?, ?, ?, ?, ?)"
                " ON CONFLICT(id) DO UPDATE SET"
                " title = excluded.title,"
                " description = excluded.description,"
                " category = excluded.category,"
                " module = excluded.module,"
                " sort_order = excluded.sort_order",
                (node.id, node.title, node.description, node.category, node.module, node.order),
            )
            for kind, min_score in node.requirements:
                conn.execute(
                    "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
                    (node.id, kind, min_score),
                )

        # Insérer les arêtes uniquement après avoir créé TOUS les nœuds : le prérequis
        # peut apparaître plus loin dans nodes.json. Les références inconnues sont ignorées.
        node_ids = {node.id for node in nodes}
        for node in nodes:
            for prereq in node.prereqs:
                if prereq not in node_ids:
                    print(
                        f"⚠️ Pré-requis ignoré : le nœud « {node.id} » référence "
                        f"« {prereq} », absent de nodes.json."
                    )
                    continue
                conn.execute(
                    "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)",
                    (node.id, prereq),
                )

        for scope, bank in (("quiz", quizzes), ("exam", exams)):
            for node_id, questions in bank.items():
                for position, question in enumerate(questions):
                    conn.execute(
                        "INSERT INTO questions"
                        " (node_id, scope, prompt, choices, answer, question_type, answer_text,"
                        " answer_regex, explanation, position)"
                        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            node_id,
                            scope,
                            question.prompt,
                            json.dumps(question.choices, ensure_ascii=False),
                            question.answer if question.question_type == "qcm" else 0,
                            question.question_type,
                            question.answer if question.question_type in {"input", "terminal"} else None,
                            question.answer_regex,
                            question.explanation,
                            position,
                        ),
                    )

        for lab in labs.values():
            conn.execute(
                "INSERT INTO lab_specs (node_id, kind, mode, pattern, prompt, hint)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (lab.node_id, lab.kind, lab.mode, lab.pattern, lab.prompt, lab.hint),
            )

        for terminal in terminals.values():
            conn.execute(
                "INSERT INTO terminal_specs "
                "(node_id, prompt, answer, pattern, explanation) VALUES (?, ?, ?, ?, ?)",
                (
                    terminal.node_id,
                    terminal.prompt,
                    terminal.answer,
                    terminal.pattern,
                    terminal.explanation,
                ),
            )

        for node in nodes:
            if node.challenge is not None:
                expected_topology = dict(node.challenge.expected_topology)
                if node.challenge.brief:
                    # Le brief partage le JSON existant : pas de migration SQL nécessaire.
                    # Les validateurs n'utilisent que nodes, connections et constraints.
                    expected_topology["brief"] = node.challenge.brief
                conn.execute(
                    "INSERT INTO challenges (node_id, expected_topology, time_limit)"
                    " VALUES (?, ?, ?)",
                    (
                        node.id,
                        json.dumps(expected_topology, ensure_ascii=False),
                        node.challenge.time_limit,
                    ),
                )

    return removed


def load_content(conn: sqlite3.Connection, directory: str | Path = CONTENT_DIR) -> LoadReport:
    """Charge tout content/ dans la base. Les tentatives existantes sont conservées."""
    directory = Path(directory)
    if not directory.is_dir():
        raise ContentError(
            f"Dossier de contenu introuvable : {directory}. "
            "Lance `python main.py export` pour le générer depuis le seed intégré."
        )

    nodes = _parse_nodes(directory / "nodes.json")
    node_ids = {node.id for node in nodes}
    quizzes = _parse_bank(directory / "quiz", "quiz", node_ids)
    exams = _parse_bank(directory / "exam", "exam", node_ids)
    labs = _parse_labs(directory / "labs", node_ids)
    terminals = _parse_terminals(directory / "terminal", node_ids)
    lessons = load_lessons(directory, node_ids)
    _check_requirements(nodes, quizzes, exams, labs, terminals, directory)

    removed = _write(conn, nodes, quizzes, exams, labs, terminals)
    return LoadReport(
        nodes=len(nodes),
        edges=sum(1 for node in nodes for prereq in node.prereqs if prereq in node_ids),
        quiz_questions=sum(len(questions) for questions in quizzes.values()),
        exam_questions=sum(len(questions) for questions in exams.values()),
        labs=len(labs),
        lessons=len(lessons),
        removed_nodes=tuple(sorted(removed)),
    )

def sync_content_additions(
    conn: sqlite3.Connection,
    directory: str | Path = CONTENT_DIR,
) -> dict[str, int]:
    """Réconcilie le catalogue sans réinitialiser les données de progression.

    Contrairement à load_content(), cette fonction ne supprime ni nœud, ni tentative,
    ni session. Elle ajoute les nouveaux nœuds, leurs prérequis et leurs banques absentes.
    Elle remplace également un quiz de cours uniquement lorsque ses questions stockées
    sont manifestement temporaires, afin de ne pas écraser un quiz déjà renseigné.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise ContentError(f"Dossier de contenu introuvable : {directory}")

    nodes = _parse_nodes(directory / "nodes.json")
    node_ids = {node.id for node in nodes}
    existing_ids = {
        row["id"] for row in conn.execute("SELECT id FROM nodes").fetchall()
    }
    new_nodes = [node for node in nodes if node.id not in existing_ids]

    quizzes = _parse_bank(directory / "quiz", "quiz", node_ids)
    exams = _parse_bank(directory / "exam", "exam", node_ids)
    labs = _parse_labs(directory / "labs", node_ids)
    terminals = _parse_terminals(directory / "terminal", node_ids)

    banks_by_kind = {
        "quiz": quizzes,
        "exam": exams,
        "lab": labs,
        "terminal": terminals,
    }
    for node in new_nodes:
        for kind, _min_score in node.requirements:
            if kind in banks_by_kind and node.id not in banks_by_kind[kind]:
                raise ContentError(
                    f"Le nouveau nœud « {node.id} » exige « {kind} », "
                    "mais sa ressource de contenu est absente."
                )

    report = {
        "nodes_added": len(new_nodes),
        "quiz_banks_added": 0,
        "quiz_banks_refreshed": 0,
        "exam_banks_added": 0,
        "lab_specs_added": 0,
        "terminal_specs_added": 0,
        "challenges_added": 0,
    }

    temporary_question_markers = (
        "question placeholder",
        "option a (placeholder)",
        "option b (placeholder)",
        "option c (placeholder)",
        "option d (placeholder)",
        "question temporaire",
        "à rédiger après le cours",
        "[contenu de 5000 mots à rédiger]",
        "quiz généré automatiquement",
    )

    def insert_questions(scope: str, node_id: str, questions: list[QuestionSpec]) -> None:
        for position, question in enumerate(questions):
            conn.execute(
                "INSERT INTO questions"
                " (node_id, scope, prompt, choices, answer, question_type, answer_text,"
                " answer_regex, explanation, position)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    node_id,
                    scope,
                    question.prompt,
                    json.dumps(question.choices, ensure_ascii=False),
                    question.answer if question.question_type == "qcm" else 0,
                    question.question_type,
                    question.answer if question.question_type in {"input", "terminal"} else None,
                    question.answer_regex,
                    question.explanation,
                    position,
                ),
            )

    with conn:
        # Le JSON reste la source de vérité des métadonnées visibles du parcours.
        # Ces UPSERT ne touchent ni aux tentatives, ni aux statistiques, ni aux sessions.
        for node in nodes:
            conn.execute(
                "INSERT INTO nodes (id, title, description, category, module, sort_order)"
                " VALUES (?, ?, ?, ?, ?, ?)"
                " ON CONFLICT(id) DO UPDATE SET"
                " title = excluded.title,"
                " description = excluded.description,"
                " category = excluded.category,"
                " module = excluded.module,"
                " sort_order = excluded.sort_order",
                (
                    node.id,
                    node.title,
                    node.description,
                    node.category,
                    node.module,
                    node.order,
                ),
            )
            for kind, min_score in node.requirements:
                conn.execute(
                    "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)"
                    " ON CONFLICT(node_id, kind) DO NOTHING",
                    (node.id, kind, min_score),
                )

        # Ajoute les relations manquantes sans effacer des relations ou progrès existants.
        for node in nodes:
            for prereq in node.prereqs:
                if prereq not in node_ids:
                    continue
                conn.execute(
                    "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)"
                    " ON CONFLICT(node_id, prereq_id) DO NOTHING",
                    (node.id, prereq),
                )

        for scope, bank in (("quiz", quizzes), ("exam", exams)):
            for node_id, questions in bank.items():
                if not questions:
                    continue
                stored = conn.execute(
                    "SELECT prompt, choices, explanation FROM questions"
                    " WHERE node_id = ? AND scope = ? ORDER BY position",
                    (node_id, scope),
                ).fetchall()
                if not stored:
                    insert_questions(scope, node_id, questions)
                    if scope == "quiz":
                        report["quiz_banks_added"] += 1
                    else:
                        report["exam_banks_added"] += 1
                    continue

                # Ne remplace que les quiz de cours clairement restés à l'état de squelette.
                # Les réponses déjà enregistrées restent dans attempts, indépendante de questions.
                stored_text = " ".join(
                    " ".join(
                        str(row[field] or "")
                        for field in ("prompt", "choices", "explanation")
                    ).lower()
                    for row in stored
                )
                incoming_text = " ".join(
                    " ".join(
                        str(value or "")
                        for value in (
                            question.prompt,
                            question.choices,
                            question.explanation,
                        )
                    ).lower()
                    for question in questions
                )
                stored_is_temporary = any(
                    marker in stored_text for marker in temporary_question_markers
                )
                incoming_is_temporary = any(
                    marker in incoming_text for marker in temporary_question_markers
                )
                if scope == "quiz" and stored_is_temporary and not incoming_is_temporary:
                    conn.execute(
                        "DELETE FROM questions WHERE node_id = ? AND scope = ?",
                        (node_id, scope),
                    )
                    insert_questions(scope, node_id, questions)
                    report["quiz_banks_refreshed"] += 1

        for lab in labs.values():
            found = conn.execute(
                "SELECT 1 FROM lab_specs WHERE node_id = ?", (lab.node_id,)
            ).fetchone()
            if found is None:
                conn.execute(
                    "INSERT INTO lab_specs (node_id, kind, mode, pattern, prompt, hint)"
                    " VALUES (?, ?, ?, ?, ?, ?)"
                    " ON CONFLICT(node_id) DO NOTHING",
                    (lab.node_id, lab.kind, lab.mode, lab.pattern, lab.prompt, lab.hint),
                )
                report["lab_specs_added"] += 1

        for terminal in terminals.values():
            found = conn.execute(
                "SELECT 1 FROM terminal_specs WHERE node_id = ?", (terminal.node_id,)
            ).fetchone()
            if found is None:
                conn.execute(
                    "INSERT INTO terminal_specs (node_id, prompt, answer, pattern, explanation)"
                    " VALUES (?, ?, ?, ?, ?)"
                    " ON CONFLICT(node_id) DO NOTHING",
                    (
                        terminal.node_id,
                        terminal.prompt,
                        terminal.answer,
                        terminal.pattern,
                        terminal.explanation,
                    ),
                )
                report["terminal_specs_added"] += 1

        for node in nodes:
            if node.challenge is None:
                continue
            found = conn.execute(
                "SELECT 1 FROM challenges WHERE node_id = ?", (node.id,)
            ).fetchone()
            if found is not None:
                continue
            expected_topology = dict(node.challenge.expected_topology)
            if node.challenge.brief:
                expected_topology["brief"] = node.challenge.brief
            conn.execute(
                "INSERT INTO challenges (node_id, expected_topology, time_limit)"
                " VALUES (?, ?, ?) ON CONFLICT(node_id) DO NOTHING",
                (
                    node.id,
                    json.dumps(expected_topology, ensure_ascii=False),
                    node.challenge.time_limit,
                ),
            )
            report["challenges_added"] += 1

    return report
