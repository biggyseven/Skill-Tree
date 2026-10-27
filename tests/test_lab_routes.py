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

    def test_supported_network_scenarios_load_with_real_topology_and_rules(self) -> None:
        scenario_ids = (
            "routing-debutant",
            "ospf-intermediaire",
            "ospf-expert",
            "vlan-expert",
            "firewall-debutant",
            "secu-l2-intermediaire",
            "reseau-linux-intermediaire",
            "nat-debutant",
            "ipv6-intermediaire",
            "stp-intermediaire",
            "stp-expert",
            "bgp-intermediaire",
            "bgp-expert",
            "eigrp-intermediaire",
            "eigrp-expert",
            "dhcp-dns-intermediaire",
            "dhcp-dns-expert",
            "secu-l2-expert",
            "zero-trust-intermediaire",
            "zero-trust-expert",
            "isis-intermediaire",
            "isis-expert",
            "vrf-intermediaire",
            "vrf-expert",
            "mpls-intermediaire",
            "mpls-expert",
            "qos-intermediaire",
            "qos-expert",
            "multicast-intermediaire",
            "multicast-expert",
            "netflow-intermediaire",
            "ha-intermediaire",
            "ha-expert",
            "vxlan-intermediaire",
            "vxlan-expert",
            "sd-wan-intermediaire",
            "sd-wan-expert",
            "segment-routing-intermediaire",
            "segment-routing-expert",
            "aws-vpc-intermediaire",
            "aws-vpc-expert",
            "azure-vnet-intermediaire",
            "azure-vnet-expert",
            "cloud-aws-intermediaire",
            "cloud-azure-intermediaire",
            "cloud-gcp-intermediaire",
        )
        for lab_id in scenario_ids:
            with self.subTest(lab_id=lab_id):
                payload = lab_routes._load_lab_file(lab_id)
                self.assertIsNotNone(payload)
                definition = payload["definition"]
                self.assertGreaterEqual(len(definition.initial_topology.nodes), 2)
                self.assertGreaterEqual(len(definition.initial_topology.links), 1)
                self.assertEqual(definition.check.type, "config_assertions")
                self.assertGreaterEqual(len(definition.check.rules), 3)
                initial_result = lab_routes._evaluate_lab_check(
                    definition, definition.initial_topology
                )
                self.assertFalse(initial_result["passed"])


    def test_all_courses_requiring_lab_have_a_loadable_v2_scenario(self) -> None:
        catalog_path = lab_routes.PROJECT_ROOT / "content" / "nodes.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
        required = [
            node for node in catalog
            if any(
                isinstance(requirement, dict) and requirement.get("kind") == "lab"
                for requirement in node.get("requirements", [])
            )
        ]
        self.assertEqual(len(required), 78, "Le périmètre de l'audit a changé ; actualiser le contrôle explicitement.")

        new_scenario_ids = ["automation-intermediaire","ddos-mitigation-intermediaire","ddos-mitigation-expert","incident-ospf","lab_bridge","lab_netns","lab_tshoot_dns","lab_tshoot_mtu","lab_tshoot_route","lab_troubleshoot_vlan","linux-intermediaire","db-intermediaire","users-intermediaire","scripting-intermediaire","ha-sys-intermediaire","windows-server-intermediaire","virt-intermediaire","web-server-intermediaire","scripting-debutant","storage-intermediaire","monitoring-intermediaire","cicd-intermediaire","docker-debutant","docker-intermediaire","git-debutant","iac-intermediaire","k8s-intermediaire","observability-intermediaire","voice-sip-intermediaire"]
        for course in required:
            with self.subTest(course=course["id"]):
                payload = lab_routes._load_lab_file(course["id"])
                self.assertIsNotNone(payload, f"Aucun scénario v2 ne résout {course['id']}")
                definition = payload["definition"]
                self.assertEqual(definition.id, course["id"])
                # Les anciens scénarios ont 3 équipements de base + les 16 équipements EXT-*.
                self.assertGreaterEqual(len(definition.initial_topology.nodes), 19)
                self.assertGreaterEqual(len(definition.initial_topology.links), 19)

        for lab_id in new_scenario_ids:
            with self.subTest(new_lab=lab_id):
                definition = lab_routes._load_lab_file(lab_id)["definition"]
                self.assertEqual(definition.check.type, "config_assertions")
                self.assertGreaterEqual(len(definition.check.rules), 3)
                self.assertGreaterEqual(len(definition.initial_topology.nodes), 25)
                self.assertGreaterEqual(len(definition.initial_topology.links), 24)
                result = lab_routes._evaluate_lab_check(definition, definition.initial_topology)
                self.assertFalse(result["passed"], "Un scénario neuf ne doit pas réussir avant la configuration.")
                malformed_paths = [
                    item["message"] for item in result["results"]
                    if "Chemin invalide" in item["message"]
                ]
                self.assertEqual(malformed_paths, [], "Chaque contrôle doit cibler un champ existant du schéma.")


    def test_linux_firewall_nat_intermediate_scenario_has_topology_and_real_checks(self) -> None:
        payload = lab_routes._load_lab_file("reseau-linux-intermediaire")
        self.assertIsNotNone(payload)
        definition = payload["definition"]
        topology = lab_routes.model_to_dict(definition.initial_topology, by_alias=True)
        nodes = {node["id"]: node for node in topology["nodes"]}

        self.assertEqual(definition.title, "Filtrage et NAT sous Linux — nftables / iptables")
        self.assertGreaterEqual(len(topology["nodes"]), 21)
        self.assertGreaterEqual(len(topology["links"]), 20)
        self.assertEqual(
            sum(node["id"].startswith("EXT-") for node in topology["nodes"]), 16
        )
        self.assertEqual(
            sum(link["id"].startswith("EXT-LINK-") for link in topology["links"]), 16
        )
        self.assertEqual(nodes["FW1"]["type"], "firewall")
        self.assertEqual(len(definition.check.rules), 9)
        self.assertFalse(definition.initial_topology.nodes == [])
        self.assertFalse(lab_routes._evaluate_lab_check(
            definition, definition.initial_topology
        )["passed"])

        nat = nodes["FW1"]["config"]["services"]["nat"]
        self.assertFalse(nat["enabled"])
        self.assertFalse(nat["masquerade"])
        self.assertEqual(nat["port_forward"][0]["destination_port"], 8080)


    def test_every_course_lab_has_a_large_connected_practice_branch(self) -> None:
        scenario_paths = sorted(lab_routes.LABS_V2_DIR.glob("*.json"))
        self.assertGreaterEqual(len(scenario_paths), 30)
        for path in scenario_paths:
            with self.subTest(lab=path.stem):
                payload = lab_routes._load_lab_file(path.stem)
                self.assertIsNotNone(payload)
                topology = payload["definition"].initial_topology
                extension_nodes = {
                    node.id for node in topology.nodes if node.id.startswith("EXT-")
                }
                extension_links = [
                    link for link in topology.links if link.id.startswith("EXT-LINK-")
                ]
                self.assertEqual(len(extension_nodes), 16)
                self.assertEqual(len(extension_links), 16)
                all_node_ids = {node.id for node in topology.nodes}
                for link in extension_links:
                    self.assertIn(link.from_endpoint.node, all_node_ids)
                    self.assertIn(link.to_endpoint.node, all_node_ids)


    def test_opening_old_saved_topology_merges_new_equipment_without_overwriting_work(self) -> None:
        definition = self._definition()
        definition.initial_topology.nodes = [
            Device(
                id="SW1", type="switch", label="SW1",
                ports=[
                    Port(id="Fa0/1", name="Fa0/1", state="up"),
                    Port(id="Fa0/2", name="Fa0/2", state="up"),
                ],
                config=DeviceConfig(hostname="SW1"),
            ),
            Device(
                id="PC1", type="pc", label="PC1",
                ports=[Port(id="eth0", name="eth0", state="up")],
                config=DeviceConfig(hostname="PC1"),
            ),
        ]
        definition.initial_topology.links = [
            Link(
                id="L1",
                from_endpoint={"node": "PC1", "port": "eth0"},
                to_endpoint={"node": "SW1", "port": "Fa0/1"},
                cable_type="copper_straight",
            )
        ]
        # Simule une sauvegarde de l'ancienne topologie, avant les nouveaux équipements.
        saved_topology = lab_routes.model_to_dict(
            definition.initial_topology, by_alias=True
        )
        # Un réglage utilisateur doit survivre à la fusion.
        saved_topology["nodes"][0]["config"]["hostname"] = "SW1-PERSONNALISE"
        current_payload = lab_routes._lab_payload_from_definition("lab-1", definition)

        conn = self._connect()
        try:
            conn.execute(
                "CREATE TABLE topologies (id INTEGER PRIMARY KEY, name TEXT NOT NULL, data TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT INTO topologies (name, data, updated_at) VALUES (?, ?, ?)",
                ("lab_lab-1", json.dumps(saved_topology), "2026-10-27T00:00:00Z"),
            )
            conn.commit()
        finally:
            conn.close()

        with patch.object(lab_routes, "_fetch_lab", return_value=current_payload), patch.object(
            lab_routes, "_database_connection", side_effect=self._connect
        ), patch.object(lab_routes, "_course_lab_context", return_value=None):
            opened = lab_routes.get_lab_v2("lab-1")

        topology = opened["initial_topology"]
        node_ids = {node["id"] for node in topology["nodes"]}
        link_ids = {link["id"] for link in topology["links"]}
        nodes_by_id = {node["id"]: node for node in topology["nodes"]}

        self.assertTrue({"SW1", "PC1", "EXT-SW1", "EXT-PC01", "EXT-SRV01", "EXT-FW1", "EXT-R1", "EXT-CLOUD1"}.issubset(node_ids))
        self.assertEqual(len([node_id for node_id in node_ids if node_id.startswith("EXT-")]), 16)
        self.assertEqual(len([link_id for link_id in link_ids if link_id.startswith("EXT-LINK-")]), 16)
        self.assertEqual(nodes_by_id["SW1"]["config"]["hostname"], "SW1-PERSONNALISE")
        self.assertIn("Fa0/3", {port["id"] for port in nodes_by_id["SW1"]["ports"]})
        self.assertTrue(opened["has_saved_topology"])

        # La réponse est enrichie sans réécrire la sauvegarde existante en base.
        conn = self._connect()
        try:
            stored = json.loads(conn.execute(
                "SELECT data FROM topologies WHERE name = ?", ("lab_lab-1",)
            ).fetchone()["data"])
        finally:
            conn.close()
        self.assertEqual(len(stored["nodes"]), 2)
        self.assertEqual(len(stored["links"]), 1)

    def test_merging_the_same_saved_topology_twice_does_not_duplicate_extensions(self) -> None:
        definition = self._definition()
        definition.initial_topology.nodes = [
            Device(id="SW1", type="switch", label="SW1", ports=[Port(id="Fa0/1", name="Fa0/1")])
        ]
        current_payload = lab_routes._lab_payload_from_definition("lab-1", definition)
        baseline = lab_routes.model_to_dict(definition.initial_topology, by_alias=True)
        first = lab_routes._merge_saved_topology_extensions(
            {"schema_version": 2, "nodes": [{"id": "SW1", "type": "switch", "ports": [{"id": "Fa0/1", "name": "Fa0/1"}]}], "links": []},
            baseline,
        )
        second = lab_routes._merge_saved_topology_extensions(first, baseline)
        self.assertEqual(
            sum(node["id"].startswith("EXT-") for node in second["nodes"]), 16
        )
        self.assertEqual(
            sum(link["id"].startswith("EXT-LINK-") for link in second["links"]), 16
        )

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
        node_ids = {node.id for node in definition.initial_topology.nodes}
        self.assertTrue({"PC-A", "SW1", "PC-B"}.issubset(node_ids))
        self.assertGreaterEqual(len(node_ids), 19)
        self.assertGreaterEqual(len(definition.initial_topology.links), 18)
        self.assertEqual(
            sum(node.id.startswith("EXT-") for node in definition.initial_topology.nodes), 16
        )
        self.assertEqual(
            sum(link.id.startswith("EXT-LINK-") for link in definition.initial_topology.links), 16
        )

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

    def test_locked_course_lab_allows_practice_but_blocks_submission_rewards(self) -> None:
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
            self.assertIn("Prérequis de test", opened["course_lock_message"])
            self.assertIn("prereq-1", opened["course_lock_message"])

            checked = lab_routes.check_lab_v2(
                "lab-1", CheckRequest(topology=self._topology("edge-1"))
            )
            self.assertTrue(checked["passed"])
            self.assertEqual(checked["score"], 1.0)
            self.assertTrue(checked["locked"])
            self.assertTrue(checked["practice_only"])
            self.assertTrue(checked["course_locked"])
            self.assertIn("prereq-1", checked["course_lock_message"])
            self.assertIn("mode entraînement", checked["message"].lower())

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
