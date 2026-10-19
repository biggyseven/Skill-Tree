"""Exécution des labs Docker : conteneur jetable + vérification par script shell."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

IMAGE = "skilltree/lab:latest"
MAX_LOG = 4000
CLEANUP_TIMEOUT = 30
MAX_LAB_TIMEOUT = 300


class LabRunnerError(Exception):
    """Erreur d'infrastructure : Docker absent, image manquante, timeout."""


@dataclass(frozen=True)
class LabResult:
    passed: bool
    score: int
    detail: str
    logs: str


def _output(result: subprocess.CompletedProcess) -> str:
    return (result.stdout or "") + (result.stderr or "")


def _truncate(text: str, limit: int = MAX_LOG) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 20].rstrip() + "\n... (tronqué)"


def _docker(
    args: list[str],
    *,
    timeout: int,
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["docker", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        raise LabRunnerError("Docker n'est pas installé ou n'est pas dans le PATH.")
    except subprocess.TimeoutExpired:
        raise LabRunnerError(f"Le lab a dépassé le temps limite ({timeout}s).")


def check_docker() -> tuple[bool, str]:
    """Vérifie Docker et la présence de l'image de lab."""
    if shutil.which("docker") is None:
        return False, "Docker n'est pas installé ou n'est pas dans le PATH."

    try:
        version = _docker(["version"], timeout=30)
    except LabRunnerError as error:
        return False, str(error)
    if version.returncode != 0:
        return False, "Docker n'est pas installé ou n'est pas dans le PATH."

    try:
        image = _docker(["image", "inspect", IMAGE], timeout=30)
    except LabRunnerError as error:
        return False, str(error)
    if image.returncode != 0:
        return False, (
            f"L'image {IMAGE} est absente. Lance : "
            f"docker build -t {IMAGE} docker/lab"
        )
    return True, ""


def _lab_config(lab_dir: Path) -> dict:
    path = lab_dir / "lab.json"
    if not path.is_file():
        raise LabRunnerError(f"lab.json introuvable : {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LabRunnerError(f"lab.json illisible : {path} ({error})")

    timeout = payload.get("timeout", 60)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0:
        timeout = 60
    timeout = min(timeout, MAX_LAB_TIMEOUT)

    image = payload.get("image") or IMAGE
    if not isinstance(image, str):
        image = IMAGE
    return {"image": image, "timeout": timeout}


def _remove_container(name: str) -> None:
    try:
        subprocess.run(
            ["docker", "rm", "-f", name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CLEANUP_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def _wait_ready(name: str, timeout: int) -> bool:
    for _ in range(5):
        try:
            probe = _docker(["exec", name, "true"], timeout=timeout)
        except LabRunnerError:
            raise
        if probe.returncode == 0:
            return True
        time.sleep(0.5)
    return False


def _start_container(name: str, image: str, lab_dir: Path, timeout: int) -> None:
    _remove_container(name)
    # --privileged : nécessaire pour `ip netns` et pour écrire les sysctl
    # par namespace (net.ipv4.ip_forward), que Docker monte en lecture seule.
    created = _docker(
        [
            "run",
            "--rm",
            "-d",
            "--name",
            name,
            "--privileged",
            "-v",
            f"{lab_dir.resolve()}:/lab:ro",
            image,
            "sleep",
            "300",
        ],
        timeout=timeout,
    )
    if created.returncode != 0:
        raise LabRunnerError("Impossible de démarrer le conteneur : " + _output(created).strip())
    if not _wait_ready(name, timeout):
        raise LabRunnerError("Le conteneur n'a pas démarré à temps.")


def _to_lf(text: str) -> str:
    """Force les fins de ligne en LF (les CRLF cassent sh : « set: illegal option - »)."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _stage_script(text: str) -> Path:
    """Écrit un script en LF dans un fichier temporaire local.

    On ne passe jamais par stdin : sous Windows, subprocess peut retraduire les
    sauts de ligne. Un fichier écrit avec newline="\\n" puis copié par `docker cp`
    arrive intact dans le conteneur.
    """
    handle = tempfile.NamedTemporaryFile(
        "w",
        suffix=".sh",
        delete=False,
        encoding="utf-8",
        newline="\n",
    )
    try:
        handle.write(_to_lf(text))
    finally:
        handle.close()
    return Path(handle.name)


def _push_script(
    name: str,
    local: Path,
    remote: str,
    timeout: int,
) -> subprocess.CompletedProcess:
    return _docker(["cp", str(local), f"{name}:{remote}"], timeout=timeout)


def _user_script(commands: list[str]) -> str:
    """Construit /tmp/user.sh en LF uniquement, sans ligne vide parasite."""
    lines = []
    for command in commands:
        for line in _to_lf(command).split("\n"):
            line = line.rstrip()
            if line:
                lines.append(line)
    return "#!/bin/sh\nset -e\n" + "".join(f"{line}\n" for line in lines)


def run_lab(node_id: str, commands: list[str], lab_dir: str | Path) -> LabResult:
    """Exécute les commandes utilisateur dans un conteneur puis check.sh."""
    ok, message = check_docker()
    if not ok:
        raise LabRunnerError(message)

    lab_dir = Path(lab_dir)
    config = _lab_config(lab_dir)
    timeout = config["timeout"]

    for script in ("setup.sh", "check.sh"):
        if not (lab_dir / script).is_file():
            raise LabRunnerError(f"Fichier manquant dans le lab : {lab_dir / script}")

    name = f"skilltree-lab-{uuid.uuid4().hex[:12]}"
    temp_files: list[Path] = []
    try:
        _start_container(name, config["image"], lab_dir, timeout)

        setup_local = _stage_script((lab_dir / "setup.sh").read_text(encoding="utf-8"))
        temp_files.append(setup_local)
        pushed = _push_script(name, setup_local, "/tmp/setup.sh", timeout)
        if pushed.returncode != 0:
            return LabResult(False, 0, "setup échoué", _truncate(_output(pushed)))

        setup = _docker(["exec", name, "sh", "/tmp/setup.sh"], timeout=timeout)
        if setup.returncode != 0:
            return LabResult(False, 0, "setup échoué", _truncate(_output(setup)))

        user_local = _stage_script(_user_script(commands))
        temp_files.append(user_local)
        pushed = _push_script(name, user_local, "/tmp/user.sh", timeout)
        if pushed.returncode != 0:
            raise LabRunnerError(
                "Impossible de copier les commandes dans le conteneur : "
                + _output(pushed).strip()
            )

        executed = _docker(["exec", name, "sh", "/tmp/user.sh"], timeout=timeout)
        if executed.returncode != 0:
            return LabResult(False, 0, "commande échouée", _truncate(_output(executed)))

        check_local = _stage_script((lab_dir / "check.sh").read_text(encoding="utf-8"))
        temp_files.append(check_local)
        pushed = _push_script(name, check_local, "/tmp/check.sh", timeout)
        if pushed.returncode != 0:
            return LabResult(False, 0, "check échoué", _truncate(_output(pushed)))

        checked = _docker(["exec", name, "sh", "/tmp/check.sh"], timeout=timeout)
        logs = _truncate(_output(checked))
        if checked.returncode == 0:
            return LabResult(True, 100, "check réussi", logs)
        return LabResult(False, 0, f"check échoué (code {checked.returncode})", logs)
    finally:
        for local in temp_files:
            try:
                local.unlink()
            except OSError:
                pass
        _remove_container(name)


def debug_shell(node_id: str, lab_dir: str | Path, timeout: int | None = None) -> None:
    """Lance le lab et ouvre un shell interactif, sans rien valider."""
    ok, message = check_docker()
    if not ok:
        raise LabRunnerError(message)

    lab_dir = Path(lab_dir)
    config = _lab_config(lab_dir)
    timeout = timeout or config["timeout"]

    name = f"skilltree-lab-{uuid.uuid4().hex[:12]}"
    temp_files: list[Path] = []
    try:
        _start_container(name, config["image"], lab_dir, timeout)

        setup_local = _stage_script((lab_dir / "setup.sh").read_text(encoding="utf-8"))
        temp_files.append(setup_local)
        pushed = _push_script(name, setup_local, "/tmp/setup.sh", timeout)
        if pushed.returncode != 0:
            raise LabRunnerError("setup échoué : " + _output(pushed).strip())

        setup = _docker(["exec", name, "sh", "/tmp/setup.sh"], timeout=timeout)
        if setup.returncode != 0:
            raise LabRunnerError("setup échoué : " + _output(setup).strip())

        print(f"Shell de debug dans {name}. Tape 'exit' pour terminer.")
        try:
            subprocess.run(["docker", "exec", "-it", name, "sh"], check=False)
        except OSError as error:
            raise LabRunnerError(f"Impossible d'ouvrir le shell : {error}")
    finally:
        for local in temp_files:
            try:
                local.unlink()
            except OSError:
                pass
        _remove_container(name)
