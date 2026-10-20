"""Exécution des labs Docker : conteneur jetable + vérification par script shell."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

IMAGE = "skilltree/lab:latest"
MAX_LOG = 4000
CLEANUP_TIMEOUT = 30
MAX_LAB_TIMEOUT = 300
INTERACTIVE_SLEEP_SECONDS = 3600
INTERACTIVE_COMMAND_TIMEOUT = 20
INTERACTIVE_MAX_COMMAND = 2000
INTERACTIVE_MAX_OUTPUT = 8000


class LabRunnerError(Exception):
    """Erreur d'infrastructure : Docker absent, image manquante, timeout."""


class LabSessionError(LabRunnerError):
    """Session de lab interactive inconnue, expirée ou déjà fermée."""


@dataclass(frozen=True)
class LabResult:
    passed: bool
    score: int
    detail: str
    logs: str


@dataclass
class InteractiveLab:
    lab_id: str
    node_id: str
    container_id: str
    container_name: str
    lab_dir: Path
    setup_logs: str
    timeout: int
    commands: list[str]
    created_at: float


@dataclass(frozen=True)
class LabCommandResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool


@dataclass(frozen=True)
class LabValidation:
    node_id: str
    commands: list[str]
    result: LabResult


_INTERACTIVE_LABS: dict[str, InteractiveLab] = {}
_INTERACTIVE_LOCK = threading.Lock()


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


def _start_container(
    name: str,
    image: str,
    lab_dir: Path,
    timeout: int,
    *,
    sleep_seconds: int = 300,
) -> str:
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
            str(sleep_seconds),
        ],
        timeout=timeout,
    )
    if created.returncode != 0:
        raise LabRunnerError("Impossible de démarrer le conteneur : " + _output(created).strip())
    if not _wait_ready(name, timeout):
        raise LabRunnerError("Le conteneur n'a pas démarré à temps.")
    return (created.stdout or "").strip() or name


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


def _cleanup_interactive_labs() -> None:
    """Supprime les conteneurs interactifs dont la session a expiré."""
    now = time.time()
    stale: list[InteractiveLab] = []
    with _INTERACTIVE_LOCK:
        for lab_id, lab in list(_INTERACTIVE_LABS.items()):
            if now - lab.created_at > INTERACTIVE_SLEEP_SECONDS:
                stale.append(_INTERACTIVE_LABS.pop(lab_id))
    for lab in stale:
        _remove_container(lab.container_name)


def _get_interactive_lab(lab_id: str) -> InteractiveLab:
    if not isinstance(lab_id, str) or not lab_id.strip():
        raise LabSessionError("Identifiant de lab invalide.")
    with _INTERACTIVE_LOCK:
        lab = _INTERACTIVE_LABS.get(lab_id)
    if lab is None:
        raise LabSessionError("Session de lab introuvable ou expirée.")
    return lab


def start_interactive_lab(node_id: str, lab_dir: str | Path) -> InteractiveLab:
    """Démarre un conteneur persistant, exécute setup.sh et garde le lab ouvert."""
    ok, message = check_docker()
    if not ok:
        raise LabRunnerError(message)

    lab_dir = Path(lab_dir)
    config = _lab_config(lab_dir)
    for script in ("setup.sh", "check.sh"):
        if not (lab_dir / script).is_file():
            raise LabRunnerError(f"Fichier manquant dans le lab : {lab_dir / script}")

    _cleanup_interactive_labs()
    name = f"skilltree-lab-{uuid.uuid4().hex[:12]}"
    lab_id = uuid.uuid4().hex
    temp_files: list[Path] = []
    try:
        container_id = _start_container(
            name,
            config["image"],
            lab_dir,
            config["timeout"],
            sleep_seconds=INTERACTIVE_SLEEP_SECONDS,
        )
        try:
            setup_local = _stage_script((lab_dir / "setup.sh").read_text(encoding="utf-8"))
            temp_files.append(setup_local)
            pushed = _push_script(name, setup_local, "/tmp/setup.sh", config["timeout"])
            if pushed.returncode != 0:
                raise LabRunnerError("setup échoué : " + _output(pushed).strip())

            setup = _docker(["exec", name, "sh", "/tmp/setup.sh"], timeout=config["timeout"])
            if setup.returncode != 0:
                raise LabRunnerError("setup échoué : " + _output(setup).strip())

            check_local = _stage_script((lab_dir / "check.sh").read_text(encoding="utf-8"))
            temp_files.append(check_local)
            pushed_check = _push_script(name, check_local, "/tmp/check.sh", config["timeout"])
            if pushed_check.returncode != 0:
                raise LabRunnerError(
                    "check.sh n'a pas pu être copié : " + _output(pushed_check).strip()
                )
            setup_logs = _truncate(_output(setup))
        finally:
            for local in temp_files:
                try:
                    local.unlink()
                except OSError:
                    pass
    except Exception:
        _remove_container(name)
        raise

    session = InteractiveLab(
        lab_id=lab_id,
        node_id=node_id,
        container_id=container_id,
        container_name=name,
        lab_dir=lab_dir,
        setup_logs=setup_logs,
        timeout=config["timeout"],
        commands=[],
        created_at=time.time(),
    )
    with _INTERACTIVE_LOCK:
        _INTERACTIVE_LABS[lab_id] = session
    return session


def exec_in_lab(lab_id: str, command: str) -> LabCommandResult:
    """Exécute une commande avec timeout dans le conteneur du lab."""
    lab = _get_interactive_lab(lab_id)
    if not isinstance(command, str) or not command.strip():
        raise LabRunnerError("La commande est vide.")
    command = command.strip()
    if len(command) > INTERACTIVE_MAX_COMMAND:
        raise LabRunnerError(
            f"La commande dépasse {INTERACTIVE_MAX_COMMAND} caractères."
        )
    if "\x00" in command:
        raise LabRunnerError("La commande contient un caractère nul.")

    with _INTERACTIVE_LOCK:
        lab.commands.append(command)

    executed = _docker(
        [
            "exec",
            lab.container_name,
            "timeout",
            str(INTERACTIVE_COMMAND_TIMEOUT),
            "sh",
            "-c",
            command,
        ],
        timeout=INTERACTIVE_COMMAND_TIMEOUT + 10,
    )

    stderr = executed.stderr or ""
    if executed.returncode != 0 and (
        "is not running" in stderr or "No such container" in stderr
    ):
        with _INTERACTIVE_LOCK:
            _INTERACTIVE_LABS.pop(lab_id, None)
        raise LabSessionError("Le conteneur du lab n'est plus actif. Redémarre le lab.")

    return LabCommandResult(
        stdout=_truncate(executed.stdout or "", INTERACTIVE_MAX_OUTPUT),
        stderr=_truncate(stderr, INTERACTIVE_MAX_OUTPUT),
        exit_code=executed.returncode,
        timed_out=executed.returncode in (124, 143),
    )


def validate_lab(lab_id: str) -> LabValidation:
    """Lance check.sh, ferme le conteneur et retourne les commandes jouées."""
    with _INTERACTIVE_LOCK:
        lab = _INTERACTIVE_LABS.pop(lab_id, None)
    if lab is None:
        raise LabSessionError("Session de lab introuvable ou déjà validée.")

    try:
        checked = _docker(
            ["exec", lab.container_name, "sh", "/tmp/check.sh"],
            timeout=lab.timeout,
        )
        logs = _truncate(_output(checked))
        if checked.returncode == 0:
            result = LabResult(True, 100, "check réussi", logs)
        else:
            result = LabResult(
                False,
                0,
                f"check échoué (code {checked.returncode})",
                logs,
            )
    finally:
        _remove_container(lab.container_name)

    return LabValidation(lab.node_id, list(lab.commands), result)
