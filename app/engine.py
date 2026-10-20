"""Règles du skill tree : déblocage, validation, correction des labs."""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime

from .db import award_attempt_xp, touch_daily_streak
from .domain import (
    Attempt,
    LabSpec,
    Node,
    ProofKind,
    Question,
    Requirement,
    Status,
)
from .labs_runner import LabResult

MAX_DETAIL = 4000

BADGE_DEFINITIONS = {
    "first-blood": {
        "nom": "Premier Sang",
        "description": "Valider son premier nœud du skill tree.",
        "icone": "🩸",
    },
    "war-machine": {
        "nom": "Machine de Guerre",
        "description": "Valider cinq labs différents.",
        "icone": "⚔️",
    },
    "architect": {
        "nom": "Architecte",
        "description": "Sauvegarder une topologie dans le canvas.",
        "icone": "🏛️",
    },
    "flawless": {
        "nom": "Sans Faute",
        "description": "Obtenir 100 % à un examen.",
        "icone": "🎯",
    },
}

KIND_ORDER = {
    ProofKind.QUIZ: 0,
    ProofKind.LAB: 1,
    ProofKind.EXAM: 2,
    ProofKind.MANUAL: 3,
    ProofKind.TERMINAL: 4,
}


class DomainError(Exception):
    """Erreur destinée à l'utilisateur (verrou, prérequis, saisie invalide...)."""


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(";").strip()


def check_lab(spec: LabSpec, answer: str) -> tuple[bool, str]:
    """Corrige une réponse de lab. Retourne (réussi, explication).

    Mode « contains » : recherche avec délimiteurs de mots.
        "switchport mode trunk"                        -> OK
        "interface Gi0/1; switchport mode trunk"       -> OK
        "fooswitchport mode trunk"                     -> KO (pas de word boundary)
        "switchport mode trunking"                     -> KO (trunking != trunk)
        "switchport mode access"                       -> KO
    """
    if spec.mode == "exact":
        return normalize(answer) == normalize(spec.pattern), f"réponse attendue : {spec.pattern}"

    if spec.mode == "contains":
        normalized_answer = normalize(answer)
        normalized_pattern = normalize(spec.pattern)
        regex = r"\b" + re.escape(normalized_pattern) + r"\b"
        found = re.search(regex, normalized_answer) is not None
        return found, f"la réponse doit contenir : {spec.pattern}"

    if spec.mode == "regex":
        found = re.search(spec.pattern, answer, re.IGNORECASE | re.MULTILINE) is not None
        return found, f"motif attendu : {spec.pattern}"

    patterns = json.loads(spec.pattern)
    hits = [re.search(p, answer, re.IGNORECASE | re.MULTILINE) is not None for p in patterns]
    if spec.mode == "all":
        return all(hits), "motifs attendus : " + " | ".join(patterns)
    if spec.mode == "any":
        return any(hits), "un des motifs attendus : " + " | ".join(patterns)
    raise DomainError(f"Mode de correction inconnu : {spec.mode}")


def requirement_met(requirement: Requirement, node: Node) -> bool:
    return any(
        attempt.kind == requirement.kind
        and attempt.passed
        and attempt.score >= requirement.min_score
        for attempt in node.attempts
    )


def is_validated(node: Node) -> bool:
    return bool(node.requirements) and all(
        requirement_met(requirement, node) for requirement in node.requirements
    )


def status_of(node: Node, validated_ids: set[str]) -> Status:
    if is_validated(node):
        return Status.VALIDATED
    if any(prereq not in validated_ids for prereq in node.prereqs):
        return Status.LOCKED
    if node.attempts:
        return Status.IN_PROGRESS
    return Status.AVAILABLE


class SkillTree:
    """Accès en lecture/écriture à l'arbre stocké en SQLite."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.last_reward: dict | None = None
        self.last_badges: list[dict] = []

    # --- lecture ---------------------------------------------------------
    def nodes(self) -> list[Node]:
        rows = self.conn.execute(
            "SELECT id, title, description, category, sort_order FROM nodes"
            " ORDER BY sort_order, id"
        ).fetchall()

        prereqs: dict[str, list[str]] = {}
        for row in self.conn.execute("SELECT node_id, prereq_id FROM edges ORDER BY prereq_id"):
            prereqs.setdefault(row["node_id"], []).append(row["prereq_id"])

        requirements: dict[str, list[Requirement]] = {}
        for row in self.conn.execute("SELECT node_id, kind, min_score FROM requirements"):
            requirements.setdefault(row["node_id"], []).append(
                Requirement(ProofKind(row["kind"]), row["min_score"])
            )

        attempts: dict[str, list[Attempt]] = {}
        for row in self.conn.execute(
            "SELECT id, node_id, kind, score, passed, evidence, detail, created_at"
            " FROM attempts ORDER BY created_at, id"
        ):
            attempts.setdefault(row["node_id"], []).append(
                Attempt(
                    id=row["id"],
                    node_id=row["node_id"],
                    kind=ProofKind(row["kind"]),
                    score=row["score"],
                    passed=bool(row["passed"]),
                    evidence=row["evidence"],
                    detail=row["detail"],
                    created_at=row["created_at"],
                )
            )

        nodes = []
        for row in rows:
            node_id = row["id"]
            nodes.append(
                Node(
                    id=node_id,
                    title=row["title"],
                    description=row["description"],
                    category=row["category"],
                    sort_order=row["sort_order"],
                    prereqs=tuple(prereqs.get(node_id, ())),
                    requirements=tuple(
                        sorted(requirements.get(node_id, ()), key=lambda r: KIND_ORDER[r.kind])
                    ),
                    attempts=tuple(attempts.get(node_id, ())),
                )
            )
        return nodes

    def node(self, node_id: str) -> Node:
        for node in self.nodes():
            if node.id == node_id:
                return node
        raise DomainError(f"Nœud inconnu : {node_id}")

    def validated_ids(self) -> set[str]:
        return {node.id for node in self.nodes() if is_validated(node)}

    def statuses(self) -> dict[str, Status]:
        nodes = self.nodes()
        validated = {node.id for node in nodes if is_validated(node)}
        return {node.id: status_of(node, validated) for node in nodes}

    def status(self, node_id: str) -> Status:
        statuses = self.statuses()
        if node_id not in statuses:
            raise DomainError(f"Nœud inconnu : {node_id}")
        return statuses[node_id]

    def lab_spec(self, node_id: str) -> LabSpec | None:
        row = self.conn.execute("SELECT * FROM lab_specs WHERE node_id = ?", (node_id,)).fetchone()
        if row is None:
            return None
        return LabSpec(
            node_id=row["node_id"],
            mode=row["mode"],
            pattern=row["pattern"],
            prompt=row["prompt"],
            hint=row["hint"],
            kind=row["kind"],
        )

    def questions(self, node_id: str, scope: ProofKind) -> list[Question]:
        rows = self.conn.execute(
            "SELECT * FROM questions WHERE node_id = ? AND scope = ? ORDER BY position, id",
            (node_id, scope.value),
        ).fetchall()
        return [
            Question(
                id=row["id"],
                node_id=row["node_id"],
                scope=ProofKind(row["scope"]),
                prompt=row["prompt"],
                choices=tuple(json.loads(row["choices"])),
                answer=(
                    row["answer_text"]
                    if row["question_type"] in {"input", "terminal"}
                    else row["answer"]
                ),
                explanation=row["explanation"],
                question_type=row["question_type"],
                answer_regex=row["answer_regex"],
            )
            for row in rows
        ]

    # --- écriture --------------------------------------------------------
    def playable(self, node_id: str) -> Node:
        """Retourne le nœud s'il peut recevoir une preuve, sinon lève DomainError."""
        node = self.node(node_id)
        validated = self.validated_ids()
        status = status_of(node, validated)
        if status is Status.VALIDATED:
            raise DomainError(f"Le nœud « {node_id} » est déjà validé.")
        if status is Status.LOCKED:
            missing = [p for p in node.prereqs if p not in validated]
            raise DomainError(
                f"Le nœud « {node_id} » est verrouillé. "
                f"Prérequis manquants : {', '.join(missing)}."
            )
        return node

    def record(
        self,
        node_id: str,
        kind: ProofKind,
        score: int,
        passed: bool,
        evidence: str = "",
        detail: str = "",
    ) -> tuple[Attempt, bool]:
        """Enregistre une tentative. Retourne (tentative, nœud désormais validé)."""
        self.playable(node_id)
        score = max(0, min(100, int(score)))
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.execute(
            "INSERT INTO attempts (node_id, kind, score, passed, evidence, detail, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (node_id, kind.value, score, int(passed), evidence, detail, created_at),
        )
        self.conn.commit()
        touch_daily_streak(self.conn)
        self.last_reward = award_attempt_xp(self.conn, kind) if passed else None
        self.last_badges = check_badges(self)
        attempt = Attempt(
            id=cursor.lastrowid,
            node_id=node_id,
            kind=kind,
            score=score,
            passed=passed,
            evidence=evidence,
            detail=detail,
            created_at=created_at,
        )
        return attempt, is_validated(self.node(node_id))

    def record_docker_lab(
        self,
        node_id: str,
        commands: list[str],
        result: LabResult,
    ) -> tuple[Attempt, bool]:
        """Enregistre le résultat d'un lab Docker (logs tronqués à 4000 caractères)."""
        node = self.playable(node_id)
        requirement = node.requirement(ProofKind.LAB)
        if requirement is None:
            raise DomainError(f"Le nœud « {node_id} » ne se valide pas par lab.")

        score = 100 if result.passed else 0
        passed = result.passed and score >= requirement.min_score
        evidence = "\n".join(commands)[:MAX_DETAIL]
        detail = result.detail
        if result.logs:
            detail = f"{detail}\n{result.logs}" if detail else result.logs
        detail = detail.strip()
        if len(detail) > MAX_DETAIL:
            detail = detail[: MAX_DETAIL - 20].rstrip() + "\n... (tronqué)"
        return self.record(node_id, ProofKind.LAB, score, passed, evidence=evidence, detail=detail)

    def reset(self, node_id: str) -> int:
        self.node(node_id)
        cursor = self.conn.execute("DELETE FROM attempts WHERE node_id = ?", (node_id,))
        self.conn.commit()
        return cursor.rowcount


def check_badges(tree: SkillTree) -> list[dict]:
    """Débloque les badges dont les conditions sont satisfaites.

    La table ``badges`` ne contient que les succès déjà obtenus ; les
    définitions restent dans ``BADGE_DEFINITIONS`` pour pouvoir faire évoluer
    les libellés sans migration. Retourne uniquement les nouveaux badges.
    """
    conn = tree.conn
    conditions = {
        "first-blood": len(tree.validated_ids()) >= 1,
        "war-machine": bool(
            conn.execute(
                "SELECT COUNT(DISTINCT node_id) FROM attempts"
                " WHERE kind = 'lab' AND passed = 1"
            ).fetchone()[0]
            >= 5
        ),
        "architect": bool(
            conn.execute("SELECT COUNT(*) FROM topologies").fetchone()[0] >= 1
        ),
        "flawless": bool(
            conn.execute(
                "SELECT COUNT(*) FROM exam_sessions"
                " WHERE submitted = 1 AND passed = 1 AND score = 100"
            ).fetchone()[0]
            >= 1
            or conn.execute(
                "SELECT COUNT(*) FROM attempts"
                " WHERE kind = 'exam' AND passed = 1 AND score = 100"
            ).fetchone()[0]
            >= 1
        ),
    }

    unlocked: list[dict] = []
    unlocked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for badge_id, is_unlocked in conditions.items():
        if not is_unlocked:
            continue
        definition = BADGE_DEFINITIONS[badge_id]
        cursor = conn.execute(
            "INSERT OR IGNORE INTO badges"
            " (id, nom, description, icone, condition_debloquee_le)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                badge_id,
                definition["nom"],
                definition["description"],
                definition["icone"],
                unlocked_at,
            ),
        )
        if cursor.rowcount:
            unlocked.append(
                {
                    "id": badge_id,
                    **definition,
                    "condition_debloquee_le": unlocked_at,
                }
            )
    if unlocked:
        conn.commit()
    return unlocked


DAILY_REVIEW_AFTER_DAYS = 3


def _attempt_datetime(attempt: Attempt) -> datetime:
    try:
        return datetime.fromisoformat(attempt.created_at)
    except (TypeError, ValueError):
        return datetime.min


def _validation_datetime(node: Node) -> datetime | None:
    """Date à laquelle la dernière exigence a été satisfaite, si elle existe."""
    if not node.requirements:
        return None

    dates: list[datetime] = []
    for requirement in node.requirements:
        passing = [
            attempt
            for attempt in node.attempts
            if attempt.kind == requirement.kind
            and attempt.passed
            and attempt.score >= requirement.min_score
        ]
        if not passing:
            return None
        dates.append(max(_attempt_datetime(attempt) for attempt in passing))
    return max(dates)


def _plan_action(node: Node, status: Status, action: str, label: str, reason: str, **extra) -> dict:
    item = {
        "node_id": node.id,
        "title": node.title,
        "category": node.category,
        "order": node.sort_order,
        "status": status.value,
        "action": action,
        "label": label,
        "reason": reason,
    }
    item.update(extra)
    return item


def get_daily_plan(
    tree: SkillTree,
    *,
    limit: int = 3,
    now: datetime | None = None,
) -> dict:
    """Sélectionne une session équilibrée : travaux en cours, révisions et découvertes.

    Une révision espacée est proposée lorsque la validation complète du nœud
    date de plus de ``DAILY_REVIEW_AFTER_DAYS`` jours. Les nœuds disponibles
    n'ont jamais reçu de tentative. Seuls les labs et défis déjà commencés sont
    retenus dans la catégorie « en cours ».
    """
    limit = max(1, int(limit))
    now = now or datetime.now()

    nodes = tree.nodes()
    validated_ids = {node.id for node in nodes if is_validated(node)}
    statuses = {node.id: status_of(node, validated_ids) for node in nodes}
    lab_nodes = {
        row["node_id"] for row in tree.conn.execute("SELECT node_id FROM lab_specs")
    }
    challenge_nodes = {
        row["node_id"] for row in tree.conn.execute("SELECT node_id FROM challenges")
    }

    in_progress: list[dict] = []
    review: list[dict] = []
    available: list[dict] = []

    for node in nodes:
        status = statuses[node.id]

        if status is Status.VALIDATED:
            validated_at = _validation_datetime(node)
            if validated_at is None:
                continue
            age_seconds = (now - validated_at).total_seconds()
            if age_seconds <= DAILY_REVIEW_AFTER_DAYS * 86400:
                continue
            days = int(age_seconds // 86400)
            review.append(
                _plan_action(
                    node,
                    status,
                    "review",
                    f"Réviser {node.title}",
                    f"Dernière validation il y a {days} jours",
                    last_validated_at=validated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    days_since=days,
                )
            )
            continue

        if status is Status.IN_PROGRESS and (node.id in lab_nodes or node.id in challenge_nodes):
            last_attempt = max(node.attempts, key=_attempt_datetime, default=None)
            action = "challenge" if node.id in challenge_nodes else "lab"
            reason = "Défi d'architecture en cours" if action == "challenge" else "Lab en cours"
            label = (
                f"Continuer {node.title}"
                if action == "challenge"
                else f"Faire le lab {node.title}"
            )
            in_progress.append(
                _plan_action(
                    node,
                    status,
                    action,
                    label,
                    reason,
                    last_activity_at=last_attempt.created_at if last_attempt is not None else None,
                )
            )
            continue

        if status is Status.AVAILABLE and not node.attempts:
            available.append(
                _plan_action(
                    node,
                    status,
                    "start",
                    f"Commencer {node.title}",
                    "Nouveau nœud disponible",
                )
            )

    review.sort(key=lambda item: (item["last_validated_at"], item["node_id"]))
    in_progress.sort(
        key=lambda item: (item["last_activity_at"] or "", item["order"], item["node_id"]),
        reverse=True,
    )
    available.sort(key=lambda item: (item["order"], item["node_id"]))

    groups = [in_progress, review, available]
    cursors = [0, 0, 0]
    actions: list[dict] = []
    while len(actions) < limit:
        progressed = False
        for index, group in enumerate(groups):
            if len(actions) >= limit:
                break
            if cursors[index] < len(group):
                actions.append(group[cursors[index]])
                cursors[index] += 1
                progressed = True
        if not progressed:
            break

    return {
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "review_after_days": DAILY_REVIEW_AFTER_DAYS,
        "actions": actions,
        "sections": {
            "in_progress": in_progress[:limit],
            "review": review[:limit],
            "available": available[:limit],
        },
        "counts": {
            "in_progress": len(in_progress),
            "review": len(review),
            "available": len(available),
        },
    }
