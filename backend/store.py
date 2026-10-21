"""Persistance simple (JSON) de l'état utilisateur + chargement des nœuds."""
import json
from pathlib import Path
from datetime import date, datetime
from threading import Lock

DATA_DIR = Path(__file__).parent / "data"
STATE_FILE = DATA_DIR / "user_state.json"

DEFAULT_STATE = {
    "user_name": "Ton Nom",
    "validated_nodes": [],
    "attempts": [],          # { node_id, kind, score, passed, ts }
    "total_xp": 0,
    "coins": 0,
    "current_level": 1,
    "level_name": "Débutant",
    "streak_days": 0,
    "last_active": None,
    "flashcards_known": 0,
    "flashcards_review": 0,
    "topology": None,
}

LEVELS = [
    (0,    1, "Débutant"),
    (100,  2, "Apprenti"),
    (300,  3, "Confirmé"),
    (600,  4, "Avancé"),
    (1000, 5, "Expert"),
    (1500, 6, "Senior"),
]


class Store:
    def __init__(self):
        self._lock = Lock()
        self._state = self._load_state()
        self.nodes = self._load("nodes.json", [])
        self.flashcards = self._load("flashcards.json", [])
        self.diagnostics = self._load("diagnostics.json", {})
        self.nodes_by_id = {n["id"]: n for n in self.nodes}

    # ---------- IO ----------
    def _load(self, name, default):
        p = DATA_DIR / name
        if not p.exists():
            return default
        return json.loads(p.read_text(encoding="utf-8"))

    def _load_state(self):
        if STATE_FILE.exists():
            try:
                return {**DEFAULT_STATE, **json.loads(STATE_FILE.read_text(encoding="utf-8"))}
            except Exception:
                return dict(DEFAULT_STATE)
        return dict(DEFAULT_STATE)

    def save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ---------- Accès ----------
    @property
    def state(self):
        return self._state

    def update_state(self, **kwargs):
        with self._lock:
            self._state.update(kwargs)
            self.save_state()

    # ---------- Logique métier ----------
    def _validated_set(self):
        return set(self._state["validated_nodes"])

    def compute_status(self, node):
        if node["id"] in self._validated_set():
            return "validated"
        prereqs = node.get("prereqs", [])
        if not all(p in self._validated_set() for p in prereqs):
            return "locked"
        if any(a["node_id"] == node["id"] for a in self._state["attempts"]):
            return "in_progress"
        return "available"

    def is_unlocked(self, node):
        return all(p in self._validated_set() for p in node.get("prereqs", []))

    def meets_requirements(self, node):
        reqs = node.get("requirements", [])
        if not reqs:
            return False  # jamais auto-validé sans requirements
        attempts = [a for a in self._state["attempts"] if a["node_id"] == node["id"]]
        for req in reqs:
            kind = req["kind"]
            min_score = req.get("min_score", 0)
            if not any(a["kind"] == kind and a["score"] >= min_score for a in attempts):
                return False
        return True

    def register_attempt(self, node_id, kind, score):
        """Enregistre une tentative. Retourne (node_validated, attempt_record)."""
        node = self.nodes_by_id.get(node_id)
        min_score = 0
        if node:
            for req in node.get("requirements", []):
                if req["kind"] == kind:
                    min_score = req.get("min_score", 0)
                    break
        passed = score >= min_score
        attempt = {
            "node_id": node_id,
            "kind": kind,
            "score": score,
            "passed": passed,
            "ts": datetime.utcnow().isoformat(),
        }
        with self._lock:
            self._state["attempts"].append(attempt)
            newly_validated = False
            if node and node_id not in self._state["validated_nodes"]:
                if self.meets_requirements(node):
                    self._state["validated_nodes"].append(node_id)
                    self._state["total_xp"] += node.get("xp", 0)
                    self._state["coins"] += node.get("coins", 0)
                    self._recalc_level()
                    newly_validated = True
            self._touch_streak()
            self.save_state()
        return newly_validated, attempt

    def _recalc_level(self):
        xp = self._state["total_xp"]
        for t_xp, lvl, name in reversed(LEVELS):
            if xp >= t_xp:
                self._state["current_level"] = lvl
                self._state["level_name"] = name
                return

    def _touch_streak(self):
        today = date.today().isoformat()
        last = self._state.get("last_active")
        if last == today:
            return
        if last:
            try:
                delta = (date.today() - date.fromisoformat(last)).days
                self._state["streak_days"] = self._state["streak_days"] + 1 if delta == 1 else 1
            except Exception:
                self._state["streak_days"] = 1
        else:
            self._state["streak_days"] = 1
        self._state["last_active"] = today

    def get_lesson(self, node_id):
        p = DATA_DIR / "lessons" / f"{node_id}.md"
        return p.read_text(encoding="utf-8") if p.exists() else None

    def public_node(self, node, include_detail=False):
        base = {
            "id": node["id"],
            "title": node["title"],
            "category": node["category"],
            "status": self.compute_status(node),
            "prereqs": node.get("prereqs", []),
            "requirements_detail": node.get("requirements", []),
        }
        if include_detail:
            base.update({
                "requirements": node.get("requirements", []),
                "terminal": node.get("terminal"),
                "lab": node.get("lab"),
                "xp": node.get("xp", 0),
                "coins": node.get("coins", 0),
            })
        return base