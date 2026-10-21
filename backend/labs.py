"""Gestion des labs Docker (fallback mock si Docker indisponible)."""
import logging
import uuid

try:
    import docker
    _DOCKER_AVAILABLE = True
except ImportError:
    _DOCKER_AVAILABLE = False

log = logging.getLogger("labs")


class LabManager:
    def __init__(self):
        self.client = None
        self.sessions = {}  # lab_id -> { container, node_id, history: [str] }
        if _DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                self.client.ping()
            except Exception as e:
                log.warning(f"Docker indisponible : {e}")
                self.client = None

    def start(self, node_id, image="alpine:latest"):
        if not self.client:
            lab_id = "mock-" + str(uuid.uuid4())
            self.sessions[lab_id] = {"node_id": node_id, "history": [], "mock": True}
            return {
                "lab_id": lab_id,
                "container_id": "mock",
                "setup_logs": "⚠️ Docker indisponible, mode mock actif. Les commandes sont simulées.",
            }
        try:
            container = self.client.containers.run(
                image, "sleep infinity",
                detach=True, remove=True,
                mem_limit="256m", nano_cpus=500_000_000,
                network_disabled=False,
            )
        except Exception as e:
            raise RuntimeError(f"Impossible de démarrer le container : {e}")
        lab_id = str(uuid.uuid4())
        self.sessions[lab_id] = {"container": container, "node_id": node_id, "history": []}
        return {
            "lab_id": lab_id,
            "container_id": container.short_id,
            "setup_logs": f"✅ Container {container.short_id} prêt (image {image}).",
        }

    def exec(self, lab_id, command):
        s = self.sessions.get(lab_id)
        if not s:
            return {"stdout": "", "stderr": "Lab inconnu ou expiré."}
        s["history"].append(command)
        if s.get("mock"):
            return {"stdout": f"[mock] $ {command}\n(exécution simulée)", "stderr": ""}
        try:
            res = s["container"].exec_run(command, demux=True)
            out, err = res.output
            return {
                "stdout": (out or b"").decode(errors="replace"),
                "stderr": (err or b"").decode(errors="replace"),
            }
        except Exception as e:
            return {"stdout": "", "stderr": str(e)}

    def validate(self, lab_id, expected_cmd=None):
        s = self.sessions.get(lab_id)
        if not s:
            return {"passed": False, "detail": "Lab inconnu."}
        history = s["history"]
        if not history:
            return {"passed": False, "detail": "Aucune commande exécutée."}
        if expected_cmd and not any(expected_cmd in h for h in history):
            return {"passed": False, "detail": f"Commande attendue non trouvée : {expected_cmd}"}
        return {"passed": True, "detail": f"OK — {len(history)} commande(s) exécutée(s)."}

    def stop(self, lab_id):
        s = self.sessions.pop(lab_id, None)
        if s and not s.get("mock") and self.client:
            try:
                s["container"].kill()
            except Exception:
                pass


lab_manager = LabManager()