from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import lab_routes
from app.api import app
from app.lab_schema_v2 import CheckDefinition, CheckRequest, CheckRule, Device, DeviceConfig, Link, Port, SubmitRequest, Topology


class LabValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "labs.sqlite3"
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("CREATE TABLE labs (id TEXT PRIMARY KEY, title TEXT NOT NULL DEFAULT '')")
            conn.execute("INSERT INTO labs (id, title) VALUES (?, ?)", ("lab-1", "Lab de test"))
            conn.execute(
                """
                CREATE TABLE badges (
                    id TEXT PRIMARY KEY, nom TEXT NOT NULL, description TEXT NOT NULL,
                    icone TEXT NOT NULL, condition_debloquee_le TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE nodes (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '', category TEXT NOT NULL DEFAULT 'Général',
                    module TEXT NOT NULL DEFAULT 'Administration Réseaux',
                    sort_order INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                "INSERT INTO nodes (id, title) VALUES (?, ?)",
                ("lab-1", "Lab de test"),
            )
            conn.execute(
                "INSERT INTO nodes (id, title) VALUES (?, ?)",
                ("node-sandbox", "Cours de test sans laboratoire"),
            )
            conn.execute(
                "CREATE TABLE edges (node_id TEXT NOT NULL, prereq_id TEXT NOT NULL, PRIMARY KEY (node_id, prereq_id))"
            )
            conn.execute(
                """
                CREATE TABLE requirements (
                    node_id TEXT NOT NULL, kind TEXT NOT NULL, min_score INTEGER NOT NULL DEFAULT 80,
                    PRIMARY KEY (node_id, kind)
                )
                """
            )
            conn.execute(
                "INSERT INTO requirements (node_id, kind, min_score) VALUES ('lab-1', 'lab', 100)"
            )
            conn.execute(
                """
                CREATE TABLE attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT NOT NULL, kind TEXT NOT NULL,
                    score INTEGER NOT NULL DEFAULT 0, passed INTEGER NOT NULL DEFAULT 0,
                    evidence TEXT NOT NULL DEFAULT '', detail TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE daily_streak (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, date_jour TEXT NOT NULL UNIQUE,
                    minutes_etudiees INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE lab_attempts (
                    id TEXT PRIMARY KEY, lab_id TEXT NOT NULL, user_id TEXT,
                    started_at TEXT NOT NULL, finished_at TEXT, passed INTEGER DEFAULT 0,
                    config_snapshot TEXT, check_result_json TEXT,
                    FOREIGN KEY (lab_id) REFERENCES labs(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE user_stats (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    total_xp INTEGER NOT NULL DEFAULT 0 CHECK (total_xp >= 0),
                    current_level INTEGER NOT NULL DEFAULT 1 CHECK (current_level BETWEEN 1 AND 4),
                    coins INTEGER NOT NULL DEFAULT 0 CHECK (coins >= 0)
                )
                """
            )
            conn.execute("INSERT INTO user_stats (id, total_xp, current_level, coins) VALUES (1, 0, 1, 0)")
            conn.commit()
        finally:
            conn.close()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _rule() -> CheckRule:
        return CheckRule(
            id="hostname", description="Le nom attendu est configuré",
            device="R1", path="config.hostname", operator="equals", expected="edge-1",
        )

    def _definition(self, *, check_type: str = "config_assertions", rules=None):
        if rules is None:
            rules = [self._rule()]
        return lab_routes.LabDefinition(
            id="lab-1", title="Lab de test", xp_reward=25, badges=["lab-validated"],
            check=CheckDefinition(type=check_type, rules=rules, pass_threshold=1.0),
        )

    @staticmethod
    def _topology(hostname: str) -> Topology:
        return Topology(nodes=[Device(
            id="R1", label="R1", config=DeviceConfig(hostname=hostname),
            ports=[Port(id="Fa0/0", name="Fa0/0", state="up", vlan=20)],
        )])

    def _mock_lab(self, definition):
        return patch.object(lab_routes, "_fetch_lab", return_value={"id": "lab-1", "definition": definition})

    def test_lab_v2_catalog_lists_real_json_lab_and_excludes_empty_compatibility_sandbox(self) -> None:
        catalog_db = Path(self.temp_dir.name) / "catalog.sqlite3"
        legacy_definition = {
            "schema_version": 2,
            "id": "acl-expert",
            "title": "ACL & filtrage - Expert",
            "level": "expert",
            "module": "Administration Réseaux",
            "prompt": "Ancien exercice de compatibilité",
            "objectives": [],
            "hints": [],
            "duration_min": 15,
            "difficulty": "expert",
            "xp_reward": 0,
            "badges": [],
            "initial_topology": {
                "schema_version": 2,
                "topology_id": "legacy-empty",
                "metadata": {},
                "nodes": [],
                "links": [],
                "simulation": {"state": "idle", "event_log": []},
            },
            "check": {"type": "manual_review", "rules": [], "pass_threshold": 1.0, "time_bonus": {}},
        }
        with sqlite3.connect(str(catalog_db)) as conn:
            conn.execute(
                """
                CREATE TABLE labs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    duration_min INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    schema_version INTEGER NOT NULL,
                    definition_json TEXT
                )
                """
            )
            conn.execute(
                "INSERT INTO labs (id, title, level, module, duration_min, difficulty, schema_version, definition_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "acl-expert",
                    "ACL & filtrage - Expert",
                    "expert",
                    "Administration Réseaux",
                    15,
                    "expert",
                    2,
                    json.dumps(legacy_definition, ensure_ascii=False),
                ),
            )

        def connect_catalog_db():
            connection = sqlite3.connect(str(catalog_db))
            connection.row_factory = sqlite3.Row
            return connection

        with patch.object(lab_routes, "_database_connection", side_effect=connect_catalog_db):
            catalog = lab_routes.list_labs_v2()

        lab_ids = {lab["id"] for lab in catalog}
        self.assertIn("secu-acl-intermediaire", lab_ids)
        self.assertIn("acl-debutant", lab_ids)
        self.assertNotIn("acl-expert", lab_ids)
        acl_lab = next(lab for lab in catalog if lab["id"] == "secu-acl-intermediaire")
        self.assertEqual(acl_lab["title"], "ACL et filtrage avancé")
        self.assertEqual(acl_lab["duration_min"], 20)
        self.assertEqual(acl_lab["schema_version"], 2)

    def test_bom_json_lab_definition_loads(self) -> None:
        labs_dir = Path(self.temp_dir.name) / "labs_v2"
        labs_dir.mkdir()
        definition_path = labs_dir / "lab-1.json"
        definition_path.write_bytes(
            b"\xef\xbb\xbf"
            + json.dumps(
                {"schema_version": 2, "id": "lab-1", "title": "Lab BOM"},
                ensure_ascii=False,
            ).encode("utf-8")
        )
        with patch.object(lab_routes, "LABS_V2_DIR", labs_dir), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            result = lab_routes.get_lab_v2("lab-1")
        self.assertEqual(result["definition"].title, "Lab BOM")

    def test_missing_lab_definition_for_known_course_returns_clear_404(self) -> None:
        labs_dir = Path(self.temp_dir.name) / "empty_labs_v2"
        labs_dir.mkdir()
        with patch.object(lab_routes, "LABS_V2_DIR", labs_dir), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            with self.assertRaises(lab_routes.HTTPException) as raised:
                lab_routes.get_lab_v2("node-sandbox")

        self.assertEqual(raised.exception.status_code, 404)
        self.assertIn("aucune définition exploitable", raised.exception.detail)

    def test_ipv4_beginner_course_loads_the_real_v2_scenario(self) -> None:
        with patch.object(lab_routes, "_database_connection", side_effect=self._connect):
            result = lab_routes.get_lab_v2("ipv4-debutant")

        definition = result["definition"]
        self.assertFalse(result.get("sandbox", False))
        self.assertEqual(result["id"], "ipv4-debutant")
        self.assertEqual(definition.id, "ipv4-debutant")
        self.assertEqual(definition.title, "Adressage IPv4 et sous-réseaux")
        self.assertIn("192.168.10.10", definition.prompt)
        self.assertGreaterEqual(len(definition.objectives), 4)
        self.assertGreaterEqual(len(definition.hints), 3)
        self.assertIn("onglet Hardware", definition.prompt)
        self.assertIn("Soumettre", definition.prompt)
        self.assertEqual(definition.check.type, "config_assertions")
        self.assertEqual(len(definition.check.rules), 8)
        self.assertEqual([node.id for node in definition.initial_topology.nodes], ["PC-A", "SW1", "PC-B"])
        self.assertEqual(len(definition.initial_topology.links), 2)

    def test_empty_legacy_v2_definition_is_treated_as_sandbox(self) -> None:
        db_path = Path(self.temp_dir.name) / "empty-legacy-v2.sqlite3"
        labs_dir = Path(self.temp_dir.name) / "no_v2_files"
        labs_dir.mkdir()
        conn = sqlite3.connect(str(db_path))
        definition = {
            "schema_version": 2,
            "id": "legacy-empty",
            "title": "Ancien lab temporaire",
            "level": "débutant",
            "module": "Réseaux",
            "prompt": "Ancienne consigne de compatibilité",
            "initial_topology": {"schema_version": 2, "nodes": [], "links": []},
            "check": {"type": "manual_review", "rules": []},
        }
        try:
            conn.execute("CREATE TABLE labs (id TEXT PRIMARY KEY, title TEXT, level TEXT, module TEXT, prompt TEXT, objectives TEXT, hints TEXT, duration_min INTEGER, difficulty TEXT, xp_reward INTEGER, badges TEXT, schema_version INTEGER, definition_json TEXT, migration_note TEXT)")
            conn.execute("CREATE TABLE nodes (id TEXT PRIMARY KEY, title TEXT NOT NULL)")
            conn.execute("INSERT INTO nodes (id, title) VALUES (?, ?)", ("legacy-empty", "Ancien cours"))
            conn.execute("INSERT INTO labs (id, title, level, module, prompt, objectives, hints, duration_min, difficulty, xp_reward, badges, schema_version, definition_json, migration_note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("legacy-empty", definition["title"], "débutant", "Réseaux", definition["prompt"], "[]", "[]", 15, "débutant", 0, "[]", 2, json.dumps(definition, ensure_ascii=False), "legacy"))
            conn.commit()
        finally:
            conn.close()

        def connect_test_db():
            connection = sqlite3.connect(str(db_path))
            connection.row_factory = sqlite3.Row
            return connection

        with patch.object(lab_routes, "_database_connection", side_effect=connect_test_db), patch.object(lab_routes, "LABS_V2_DIR", labs_dir):
            result = lab_routes.get_lab_v2("legacy-empty")

        self.assertTrue(result["sandbox"])
        self.assertEqual(result["definition"].initial_topology.nodes, [])

    def test_matching_server_rules_can_pass(self) -> None:
        with self._mock_lab(self._definition()), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            result = lab_routes.check_lab_v2("lab-1", CheckRequest(topology=self._topology("edge-1")))
        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 1.0)

    def test_manual_review_cannot_pass_automatically(self) -> None:
        with self._mock_lab(self._definition(check_type="manual_review")), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            result = lab_routes.check_lab_v2("lab-1", CheckRequest(topology=self._topology("edge-1")))
        self.assertFalse(result["passed"])
        self.assertTrue(result["manual_review_required"])

    def test_check_route_can_grade_a_file_lab_when_database_is_unavailable(self) -> None:
        with self._mock_lab(self._definition()), patch.object(
            lab_routes,
            "_database_connection",
            side_effect=lab_routes.HTTPException(status_code=503, detail="SQLite indisponible"),
        ):
            result = lab_routes.check_lab_v2(
                "lab-1", CheckRequest(topology=self._topology("edge-1"))
            )

        self.assertTrue(result["passed"])
        self.assertEqual(result["score"], 1.0)

    def test_empty_rule_set_fails_closed(self) -> None:
        with self._mock_lab(self._definition(rules=[])), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            result = lab_routes.check_lab_v2("lab-1", CheckRequest(topology=self._topology("edge-1")))
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0.0)

    def test_submit_ignores_forged_client_success(self) -> None:
        request = SubmitRequest(
            topology=self._topology("attacker-value"),
            check_result={"passed": True, "score": 1.0, "results": [{"passed": True}]},
        )
        with self._mock_lab(self._definition()), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            result = lab_routes.submit_lab_v2("lab-1", request)
        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0.0)
        self.assertEqual(result["xp_gained"], 0)
        self.assertEqual(result["badges_unlocked"], [])
        conn = sqlite3.connect(str(self.db_path))
        try:
            passed, result_json = conn.execute("SELECT passed, check_result_json FROM lab_attempts").fetchone()
        finally:
            conn.close()
        self.assertEqual(passed, 0)
        self.assertFalse(json.loads(result_json)["passed"])

    def test_json_only_lab_is_added_to_catalog_before_first_submission(self) -> None:
        definition = self._definition()
        definition.id = "file-lab"
        request = SubmitRequest(topology=self._topology("edge-1"), check_result={"passed": False})
        with patch.object(
            lab_routes,
            "_fetch_lab",
            return_value={"id": "file-lab", "definition": definition},
        ), patch.object(lab_routes, "_database_connection", side_effect=self._connect):
            result = lab_routes.submit_lab_v2("file-lab", request)

        self.assertTrue(result["passed"])
        self.assertEqual(result["lab_id"], "file-lab")
        self.assertTrue(result["attempt_recorded"])
        conn = self._connect()
        try:
            catalog_row = conn.execute(
                "SELECT id, title FROM labs WHERE id = 'file-lab'"
            ).fetchone()
            stored_attempt = conn.execute(
                "SELECT lab_id, passed FROM lab_attempts WHERE lab_id = 'file-lab'"
            ).fetchone()
        finally:
            conn.close()
        self.assertEqual(tuple(catalog_row), ("file-lab", "Lab de test"))
        self.assertEqual(tuple(stored_attempt), ("file-lab", 1))
        self.assertFalse(result["course_attempt_recorded"])
        conn = self._connect()
        try:
            streak_days = conn.execute("SELECT COUNT(*) FROM daily_streak").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(streak_days, 1, "Une tentative de lab autonome doit compter dans la série quotidienne.")

    def test_locked_course_lab_explains_missing_prerequisite_and_blocks_rewards(self) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO nodes (id, title) VALUES (?, ?)",
                ("prereq-1", "Prérequis de test"),
            )
            conn.execute(
                "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)",
                ("lab-1", "prereq-1"),
            )
            conn.commit()
        finally:
            conn.close()

        definition = self._definition()
        request = SubmitRequest(
            topology=self._topology("edge-1"),
            check_result={"passed": True, "score": 1.0},
        )
        with patch.object(
            lab_routes, "_fetch_lab",
            return_value={"id": "lab-1", "definition": definition},
        ), patch.object(lab_routes, "_database_connection", side_effect=self._connect):
            opened = lab_routes.get_lab_v2("lab-1")
            self.assertTrue(opened["course_locked"])
            self.assertIn("prereq-1", opened["course_lock_message"])

            checked = lab_routes.check_lab_v2(
                "lab-1", CheckRequest(topology=self._topology("edge-1"))
            )
            self.assertFalse(checked["passed"])
            self.assertTrue(checked["locked"])
            self.assertIn("prereq-1", checked["results"][0]["message"])

            with self.assertRaises(lab_routes.HTTPException) as raised:
                lab_routes.submit_lab_v2("lab-1", request)
            self.assertEqual(raised.exception.status_code, 423)
            self.assertIn("prérequis", raised.exception.detail.lower())

        conn = self._connect()
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM lab_attempts").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM badges").fetchone()[0], 0)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM daily_streak").fetchone()[0], 0)
            stats = conn.execute("SELECT total_xp, coins FROM user_stats WHERE id = 1").fetchone()
        finally:
            conn.close()
        self.assertEqual(tuple(stats), (0, 0))

    def test_success_reward_is_persisted_once_per_lab(self) -> None:
        request = SubmitRequest(topology=self._topology("edge-1"), check_result={"passed": False})
        with self._mock_lab(self._definition()), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            first = lab_routes.submit_lab_v2("lab-1", request)
            second = lab_routes.submit_lab_v2("lab-1", request)
        self.assertTrue(first["passed"])
        self.assertEqual(first["xp_gained"], 25)
        self.assertTrue(first["first_success"])
        self.assertFalse(second["first_success"])
        self.assertEqual(first["lab_id"], "lab-1")
        self.assertTrue(first["attempt_recorded"])
        self.assertTrue(first["course_attempt_recorded"])
        self.assertEqual(second["xp_gained"], 0)
        self.assertTrue(second["course_attempt_recorded"])
        conn = sqlite3.connect(str(self.db_path))
        try:
            stats = conn.execute("SELECT total_xp FROM user_stats WHERE id = 1").fetchone()
            attempts = conn.execute(
                "SELECT kind, score, passed FROM attempts WHERE node_id = 'lab-1' ORDER BY id"
            ).fetchall()
            streaks = conn.execute("SELECT COUNT(*) FROM daily_streak").fetchone()[0]
            conn.row_factory = sqlite3.Row
            canonical_status = lab_routes.SkillTree(conn).status("lab-1").value
        finally:
            conn.close()
        self.assertEqual(stats[0], 25)
        self.assertEqual([tuple(row) for row in attempts], [("lab", 100, 1), ("lab", 100, 1)])
        self.assertEqual(streaks, 1)
        self.assertEqual(canonical_status, "validated")

    def test_custom_lab_badges_are_persisted_and_returned_once(self) -> None:
        definition = self._definition()
        definition.badges = ["dhcp-nat-master", "first_blood"]
        request = SubmitRequest(
            topology=self._topology("edge-1"),
            check_result={"passed": False, "score": 0},
        )

        with self._mock_lab(definition), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ):
            first = lab_routes.submit_lab_v2("lab-1", request)
            second = lab_routes.submit_lab_v2("lab-1", request)

        self.assertTrue(first["passed"])
        self.assertEqual(
            first["badges_unlocked"],
            [
                {
                    "id": "dhcp-nat-master",
                    "nom": "Maître DHCP/NAT",
                    "description": "Réussir le laboratoire « DHCP et préparation NAT ».",
                    "icone": "🌐",
                },
                {
                    "id": "first-blood",
                    "nom": "Premier Sang",
                    "description": "Valider son premier nœud du skill tree.",
                    "icone": "🩸",
                },
            ],
        )
        self.assertEqual(second["badges_unlocked"], [])
        conn = self._connect()
        try:
            badges = conn.execute("SELECT id, nom FROM badges ORDER BY id").fetchall()
            stats = conn.execute("SELECT total_xp, coins FROM user_stats WHERE id = 1").fetchone()
        finally:
            conn.close()
        self.assertEqual([tuple(row) for row in badges], [
            ("dhcp-nat-master", "Maître DHCP/NAT"),
            ("first-blood", "Premier Sang"),
        ])
        self.assertEqual(tuple(stats), (25, 20))

    def test_all_json_lab_badges_have_resolvable_catalog_definitions(self) -> None:
        for path in lab_routes.LABS_V2_DIR.glob("*.json"):
            with self.subTest(lab=path.name):
                definition = json.loads(path.read_text(encoding="utf-8-sig"))
                for badge_id in definition.get("badges", []):
                    self.assertIsNotNone(
                        lab_routes._resolve_badge_definition(badge_id),
                        f"{path.name} référence un badge sans définition : {badge_id}",
                    )

    def test_sandbox_submit_is_never_reported_as_a_course_validation(self) -> None:
        sandbox = {
            "id": "node-sandbox",
            "sandbox": True,
            "definition": self._definition(),
        }
        request = SubmitRequest(topology=self._topology("edge-1"))
        with patch.object(lab_routes, "_fetch_lab", return_value=sandbox):
            result = lab_routes.submit_lab_v2("node-sandbox", request)

        self.assertTrue(result["sandbox"])
        self.assertFalse(result["passed"])
        self.assertFalse(result["attempt_recorded"])
        self.assertFalse(result["course_attempt_recorded"])
        self.assertEqual(result["xp_gained"], 0)
        self.assertEqual(result["badges_unlocked"], [])

    def test_vlan_and_cross_cable_survive_schema_validation(self) -> None:
        topology = self._topology("edge-1")
        topology.links.append(Link(
            id="L1",
            **{"from": {"node": "R1", "port": "Fa0/0"}, "to": {"node": "R2", "port": "Fa0/0"}},
            cable_type="copper_crossover",
        ))
        payload = lab_routes.model_to_dict(topology, by_alias=True)
        self.assertEqual(payload["nodes"][0]["ports"][0]["vlan"], 20)
        self.assertEqual(payload["links"][0]["cable_type"], "copper_crossover")

    def test_lab_api_routes_are_exposed_once_in_openapi(self) -> None:
        paths = app.openapi()["paths"]
        self.assertIn("/api/lab/v2/{lab_id}", paths)
        self.assertIn("/api/lab/v2/{lab_id}/check", paths)
        self.assertIn("/api/lab/v2/{lab_id}/submit", paths)
        self.assertIn("get", paths["/api/lab/v2/{lab_id}"])
        self.assertIn("post", paths["/api/lab/v2/{lab_id}/check"])
        self.assertIn("post", paths["/api/lab/v2/{lab_id}/submit"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
