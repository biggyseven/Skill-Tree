"""Objets métier, indépendants de SQLite."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"


class ProofKind(str, Enum):
    QUIZ = "quiz"
    LAB = "lab"
    EXAM = "exam"
    MANUAL = "manual"
    TERMINAL = "terminal"


STATUS_LABELS = {
    Status.LOCKED: "verrouillé",
    Status.AVAILABLE: "disponible",
    Status.IN_PROGRESS: "en cours",
    Status.VALIDATED: "validé",
}

STATUS_MARKERS = {
    Status.LOCKED: "-",
    Status.AVAILABLE: " ",
    Status.IN_PROGRESS: "~",
    Status.VALIDATED: "+",
}


@dataclass(frozen=True)
class Requirement:
    kind: ProofKind
    min_score: int = 80


@dataclass(frozen=True)
class Attempt:
    id: int
    node_id: str
    kind: ProofKind
    score: int
    passed: bool
    evidence: str
    detail: str
    created_at: str


@dataclass(frozen=True)
class LabSpec:
    node_id: str
    mode: str
    pattern: str
    prompt: str
    hint: str
    kind: str = "text"


@dataclass(frozen=True)
class Question:
    id: int
    node_id: str
    scope: ProofKind
    prompt: str
    choices: tuple[str, ...]
    answer: int | str
    explanation: str
    question_type: str = "qcm"
    answer_regex: str | None = None


@dataclass(frozen=True)
class Node:
    id: str
    title: str
    description: str
    module: str
    category: str
    sort_order: int
    prereqs: tuple[str, ...] = ()
    requirements: tuple[Requirement, ...] = ()
    attempts: tuple[Attempt, ...] = ()
    lesson_started: bool = False
    lesson_progress_percent: int = 0
    lesson_active_seconds: int = 0
    lesson_read_completed: bool = False

    def requirement(self, kind: ProofKind) -> Requirement | None:
        for requirement in self.requirements:
            if requirement.kind == kind:
                return requirement
        return None

    def best(self, kind: ProofKind) -> Attempt | None:
        successes = [a for a in self.attempts if a.kind == kind and a.passed]
        return max(successes, key=lambda a: a.score, default=None)
