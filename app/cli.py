"""CLI du skill tree."""
from __future__ import annotations

import argparse
import os
import re
from . import db_compat as sqlite3
import sys
from pathlib import Path

from backup import create_backup
from .db import DEFAULT_DB, connect, ensure_ready, initialize
from .domain import (
    STATUS_LABELS,
    STATUS_MARKERS,
    LabSpec,
    Node,
    ProofKind,
    Status,
)
from .engine import DomainError, SkillTree, check_lab, requirement_met
from .labs_runner import LabRunnerError, debug_shell, run_lab
from .loader import CONTENT_DIR, ContentError, LoadReport, find_lab_dir, load_content
from .seed import ExportError, export_content

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[90m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
}

STATUS_COLORS = {
    Status.LOCKED: "dim",
    Status.AVAILABLE: "cyan",
    Status.IN_PROGRESS: "yellow",
    Status.VALIDATED: "green",
}


class Style:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def paint(self, text: str, *names: str) -> str:
        if not self.enabled or not names:
            return text
        prefix = "".join(ANSI[name] for name in names)
        return f"{prefix}{text}{ANSI['reset']}"


STYLE = Style()


def status_text(status: Status) -> str:
    return STYLE.paint(STATUS_LABELS[status], STATUS_COLORS[status])


def marker_text(status: Status) -> str:
    return f"[{STATUS_MARKERS[status]}]"


def depth_map(nodes: list[Node]) -> dict[str, int]:
    by_id = {node.id: node for node in nodes}
    cache: dict[str, int] = {}

    def depth(node_id: str, visiting: tuple[str, ...] = ()) -> int:
        if node_id in cache:
            return cache[node_id]
        node = by_id[node_id]
        parents = [p for p in node.prereqs if p in by_id]
        if not parents or node_id in visiting:
            cache[node_id] = 0
            return 0
        value = 1 + max(depth(parent, visiting + (node_id,)) for parent in parents)
        cache[node_id] = value
        return value

    for node_id in by_id:
        depth(node_id)
    return cache


def progress_bar(done: int, total: int, width: int = 24) -> str:
    ratio = done / total if total else 0.0
    filled = round(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {ratio * 100:.0f}%"


def requirement_summary(node: Node) -> str:
    return " + ".join(f"{r.kind.value}>{r.min_score}" for r in node.requirements)


# --- commandes -----------------------------------------------------------
def describe_report(report: LoadReport) -> str:
    lines = [
        f"Contenu chargé : {report.nodes} nœuds, {report.edges} prérequis.",
        f"  {report.quiz_questions} questions de quiz, "
        f"{report.exam_questions} questions d'examen, {report.labs} labs.",
    ]
    if report.removed_nodes:
        lines.append(
            "  Nœuds retirés (tentatives associées supprimées) : "
            + ", ".join(report.removed_nodes)
        )
    return "\n".join(lines)


def cmd_init(conn: sqlite3.Connection, args: argparse.Namespace) -> int:
    if args.force:
        conn.execute("DELETE FROM nodes")
        conn.commit()
        print(describe_report(load_content(conn)))
    else:
        ensure_ready(conn)
    nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    print(f"Base prête : {nodes} nœuds.")
    return 0


def cmd_import(conn: sqlite3.Connection, _args: argparse.Namespace) -> int:
    print(describe_report(load_content(conn)))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    if args.force:
        print(
            STYLE.paint(
                "ATTENTION : content/ va être écrasé depuis les constantes de seed.py.",
                "red",
            )
        )
        if not args.yes:
            try:
                reply = input("tape 'oui' pour confirmer : ").strip().lower()
            except EOFError:
                reply = ""
            if reply != "oui":
                print("Export annulé.")
                return 1

    try:
        report = export_content(force=args.force)
    except ExportError as error:
        print(str(error), file=sys.stderr)
        return 1

    print(f"Contenu exporté vers {report.directory}")
    print(f"  {report.nodes} nœuds")
    print(f"  {report.quiz_files} fichiers de quiz ({report.quiz_questions} questions)")
    print(f"  {report.exam_files} fichiers d'examen ({report.exam_questions} questions)")
    print(f"  {report.lab_files} labs")
    return 0


def cmd_tree(tree: SkillTree, _args: argparse.Namespace) -> int:
    nodes = tree.nodes()
    statuses = tree.statuses()
    done = sum(1 for status in statuses.values() if status is Status.VALIDATED)
    total = len(nodes)

    print(STYLE.paint(f"Skill tree — {done}/{total} nœuds validés", "bold"))
    print(progress_bar(done, total))
    print()

    depths = depth_map(nodes)
    current_category = None
    for node in nodes:
        if node.category != current_category:
            if current_category is not None:
                print()
            print(STYLE.paint(node.category, "bold"))
            current_category = node.category

        status = statuses[node.id]
        indent = "  " * depths[node.id]
        marker = STYLE.paint(marker_text(status), STATUS_COLORS[status])
        title = STYLE.paint(f"{node.title:<40}", STATUS_COLORS[status])
        print(f"  {indent}{marker} {node.id:<16} {title} {STYLE.paint(requirement_summary(node), 'dim')}")

    print()
    print(
        STYLE.paint("Légende : ", "dim")
        + "[+] validé  [~] en cours  [ ] disponible  [-] verrouillé"
    )
    return 0


def cmd_stats(tree: SkillTree, _args: argparse.Namespace) -> int:
    nodes = tree.nodes()
    statuses = tree.statuses()
    counts = {status: 0 for status in Status}
    for status in statuses.values():
        counts[status] += 1

    print(STYLE.paint("Progression", "bold"))
    for status in Status:
        print(f"  {STATUS_LABELS[status]:<12} {counts[status]:>3}")
    print(f"  {'total':<12} {len(nodes):>3}")
    print()
    print(f"Tentatives enregistrées : {sum(len(node.attempts) for node in nodes)}")
    print()
    print(STYLE.paint("Par catégorie", "bold"))
    by_category: dict[str, list[int]] = {}
    for node in nodes:
        entry = by_category.setdefault(node.category, [0, 0])
        entry[1] += 1
        if statuses[node.id] is Status.VALIDATED:
            entry[0] += 1
    for category, (done, total) in by_category.items():
        print(f"  {category:<28} {done}/{total}")
    return 0


def cmd_show(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.node(args.node)
    status = tree.status(node.id)

    print(STYLE.paint(f"{node.title} ({node.id})", "bold"))
    print(f"Catégorie   : {node.category}")
    print(f"Statut      : {status_text(status)}")
    if node.description:
        print(f"Description : {node.description}")

    if node.prereqs:
        print("Prérequis   :")
        for prereq in node.prereqs:
            prereq_status = tree.status(prereq)
            print(f"  - {prereq:<16} {STATUS_LABELS[prereq_status]}")
    else:
        print("Prérequis   : aucun (nœud racine)")

    print("Exigences   :")
    for requirement in node.requirements:
        met = requirement_met(requirement, node)
        best = node.best(requirement.kind)
        detail = f"meilleur score {best.score}" if best else "aucune réussite"
        verdict = STYLE.paint("OK", "green") if met else STYLE.paint("KO", "red")
        print(
            f"  - {requirement.kind.value:<6} seuil {requirement.min_score:<3} "
            f"{verdict} ({detail})"
        )

    spec = tree.lab_spec(node.id)
    if spec is not None:
        print("Lab         :")
        print(f"  énoncé : {spec.prompt}")
        if spec.hint:
            print(f"  indice : {STYLE.paint(spec.hint, 'dim')}")

    if node.attempts:
        print("Tentatives  :")
        for attempt in node.attempts[-10:]:
            result = "réussi" if attempt.passed else "échec"
            print(
                f"  {attempt.created_at}  {attempt.kind.value:<6} "
                f"{attempt.score:>3}/100  {result:<7} {attempt.detail}"
            )
    return 0


def cmd_history(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.node(args.node)
    if not node.attempts:
        print(f"Aucune tentative pour {node.id}.")
        return 0
    print(STYLE.paint(f"Historique — {node.title}", "bold"))
    for attempt in node.attempts:
        result = "réussi" if attempt.passed else "échec"
        print(f"{attempt.created_at}  {attempt.kind.value:<6} {attempt.score:>3}/100  {result}")
        if attempt.detail:
            print(f"    détail : {attempt.detail}")
        if attempt.evidence:
            print(f"    preuve : {attempt.evidence}")
    return 0


def _run_qcm(tree: SkillTree, node_id: str, kind: ProofKind, answers: str | None) -> int:
    node = tree.playable(node_id)
    requirement = node.requirement(kind)
    if requirement is None:
        raise DomainError(f"Le nœud « {node_id} » ne se valide pas par {kind.value}.")
    questions = tree.questions(node_id, kind)
    if not questions:
        raise DomainError(f"Aucune question {kind.value} pour « {node_id} ».")

    # On conserve les réponses brutes : les QCM seront convertis en int
    # uniquement au moment de la correction.
    provided: list[str] | None = None
    if answers:
        provided = [part.strip() for part in answers.split(",")]
        if len(provided) != len(questions):
            raise DomainError(f"{len(questions)} réponses attendues, {len(provided)} fournies.")

    print(STYLE.paint(f"{kind.value.upper()} — {node.title}", "bold"))
    print(f"Seuil de validation : {requirement.min_score}/100")
    print()

    correct = 0
    for index, question in enumerate(questions, 1):
        print(f"{index}. {question.prompt}")
        if question.question_type == "qcm":
            for choice_index, choice in enumerate(question.choices, 1):
                print(f"   {choice_index}. {choice}")

        if provided is not None:
            raw = provided[index - 1]
            print(f"   > {raw}")
        elif question.question_type in {"input", "terminal"}:
            raw = input("   Ta réponse/commande (q pour quitter) : ").strip()
            if raw.lower() == "q":
                print("Abandon : aucune tentative enregistrée.")
                return 0
        else:
            valid = {str(i) for i in range(1, len(question.choices) + 1)} | {"q"}
            raw = ""
            while raw not in valid:
                raw = input("   Ta réponse (numéro, q pour quitter) : ").strip().lower()
            if raw == "q":
                print("Abandon : aucune tentative enregistrée.")
                return 0

        if question.question_type == "qcm":
            try:
                choice = int(raw)
            except (TypeError, ValueError):
                raise DomainError(f"Réponse invalide à la question {index}.")
            if not 1 <= choice <= len(question.choices):
                raise DomainError(f"Réponse hors bornes à la question {index}.")
            is_correct = choice - 1 == question.answer
        else:
            is_correct = re.fullmatch(
                question.answer_regex or "",
                raw,
                re.IGNORECASE,
            ) is not None

        if is_correct:
            correct += 1
            print(STYLE.paint("   correct", "green"))
        else:
            print(STYLE.paint("   faux", "red"))
        if question.explanation:
            print(f"   {question.explanation}")
        print()

    score = round(100 * correct / len(questions))
    passed = score >= requirement.min_score
    attempt, validated = tree.record(
        node_id, kind, score, passed, detail=f"{correct}/{len(questions)} bonnes réponses"
    )

    label = "RÉUSSI" if passed else "ÉCHEC"
    print(
        STYLE.paint(f"Score : {score}/100 (seuil {requirement.min_score}) — {label}",
                    "green" if passed else "red")
        + f"  [{attempt.created_at}]"
    )
    if validated:
        print(STYLE.paint(f"Nœud validé : {node_id}", "bold", "green"))
    elif passed:
        print("Tentative réussie, mais d'autres exigences restent à satisfaire.")
    return 0


def cmd_quiz(tree: SkillTree, args: argparse.Namespace) -> int:
    return _run_qcm(tree, args.node, ProofKind.QUIZ, args.answers)


def cmd_exam(tree: SkillTree, args: argparse.Namespace) -> int:
    return _run_qcm(tree, args.node, ProofKind.EXAM, args.answers)


def cmd_lab(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.playable(args.node)
    requirement = node.requirement(ProofKind.LAB)
    if requirement is None:
        raise DomainError(f"Le nœud « {args.node} » ne se valide pas par lab.")
    spec = tree.lab_spec(args.node)
    if spec is None:
        raise DomainError(f"Aucun lab défini pour « {args.node} ».")
    if spec.kind == "docker":
        raise DomainError(
            f"Le lab « {args.node} » est un lab Docker : "
            f"utilise `python main.py labd {args.node}`."
        )

    print(STYLE.paint(f"LAB — {node.title}", "bold"))
    print(spec.prompt)
    if spec.hint:
        print(STYLE.paint(f"indice : {spec.hint}", "dim"))

    answer = args.answer
    if not answer:
        answer = input("> ").strip()

    ok, explanation = check_lab(spec, answer)
    score = 100 if ok else 0
    passed = ok and score >= requirement.min_score
    attempt, validated = tree.record(
        args.node, ProofKind.LAB, score, passed, evidence=answer, detail=explanation
    )

    if ok:
        print(STYLE.paint("Lab réussi.", "green"))
    else:
        print(STYLE.paint("Lab échoué.", "red") + f" {explanation}")
    print(f"Score : {score}/100 (seuil {requirement.min_score})  [{attempt.created_at}]")
    if validated:
        print(STYLE.paint(f"Nœud validé : {args.node}", "bold", "green"))
    elif passed:
        print("Tentative réussie, mais d'autres exigences restent à satisfaire.")
    return 0


def _lab_dir(node_id: str) -> Path:
    return find_lab_dir(node_id) or (CONTENT_DIR / "labs" / node_id)


def _require_docker_lab(tree: SkillTree, node_id: str) -> LabSpec:
    spec = tree.lab_spec(node_id)
    lab_dir = _lab_dir(node_id)
    if spec is None or spec.kind != "docker" or not (lab_dir / "lab.json").is_file():
        raise DomainError("Ce nœud n'a pas de lab docker.")
    return spec


def cmd_labd(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.playable(args.node)
    spec = _require_docker_lab(tree, node.id)
    lab_dir = _lab_dir(node.id)

    consigne = lab_dir / "consigne.md"
    if consigne.is_file():
        print(consigne.read_text(encoding="utf-8").strip())
    else:
        print(spec.prompt)
    if spec.hint:
        print(STYLE.paint(f"indice : {spec.hint}", "dim"))
    print()

    commands: list[str] = []
    while True:
        try:
            line = input("commande (vide pour terminer) : ")
        except EOFError:
            break
        if not line.strip():
            break
        commands.append(line)

    if not commands:
        print("Aucune commande saisie.")

    print("Exécution du lab...")
    try:
        result = run_lab(node.id, commands, lab_dir)
    except LabRunnerError as error:
        raise DomainError(str(error))

    if result.logs:
        print(STYLE.paint("--- logs ---", "dim"))
        print(result.logs)
    if result.passed:
        print(STYLE.paint("Lab réussi", "green"))
    else:
        print(STYLE.paint(f"Lab échoué : {result.detail}", "red"))

    attempt, validated = tree.record_docker_lab(node.id, commands, result)
    if validated:
        print(STYLE.paint(f"Nœud validé : {node.id}", "bold", "green"))
    elif result.passed:
        print("Tentative réussie, mais d'autres exigences restent à satisfaire.")
    return 0 if result.passed else 1


def cmd_lab_shell(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.node(args.node)
    _require_docker_lab(tree, node.id)
    try:
        debug_shell(node.id, _lab_dir(node.id))
    except LabRunnerError as error:
        raise DomainError(str(error))
    return 0


def cmd_prove(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.playable(args.node)
    requirement = node.requirement(ProofKind.MANUAL)
    if requirement is None:
        raise DomainError(f"Le nœud « {args.node} » n'accepte pas de preuve manuelle.")

    evidence = args.evidence.strip()
    if not evidence:
        raise DomainError("--evidence est obligatoire.")

    attempt, validated = tree.record(
        args.node, ProofKind.MANUAL, 100, True, evidence=evidence, detail="preuve manuelle"
    )
    print(STYLE.paint("Preuve enregistrée.", "green") + f"  [{attempt.created_at}]")
    if validated:
        print(STYLE.paint(f"Nœud validé : {args.node}", "bold", "green"))
    else:
        print("Preuve enregistrée, mais d'autres exigences restent à satisfaire.")
    return 0


def cmd_reset(tree: SkillTree, args: argparse.Namespace) -> int:
    node = tree.node(args.node)
    before = {node_id for node_id, status in tree.statuses().items() if status is Status.LOCKED}
    count = tree.reset(node.id)
    after = {node_id for node_id, status in tree.statuses().items() if status is Status.LOCKED}
    print(f"{count} tentative(s) supprimée(s) pour « {node.id} ».")
    newly_locked = sorted(after - before)
    if newly_locked:
        print(
            "Attention : ces nœuds redeviennent verrouillés : "
            + ", ".join(newly_locked)
        )
    return 0


def cmd_backup(_args: argparse.Namespace) -> int:
    create_backup()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skilltree",
        description="Skill tree d'apprentissage réseau, validation par preuve.",
    )
    parser.add_argument("--db", default=DEFAULT_DB, help=f"base SQLite (défaut : {DEFAULT_DB})")
    parser.add_argument("--no-color", action="store_true", help="désactive les couleurs")

    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="crée la base et charge le contenu")
    init.add_argument("--force", action="store_true", help="efface tout et recharge le contenu")

    sub.add_parser("tree", help="affiche l'arbre complet")
    sub.add_parser("stats", help="affiche la progression")

    show = sub.add_parser("show", help="détail d'un nœud")
    show.add_argument("node")

    quiz = sub.add_parser("quiz", help="passe le quiz d'un nœud")
    quiz.add_argument("node")
    quiz.add_argument("--answers", help="réponses séparées par des virgules (mode non interactif)")

    exam = sub.add_parser("exam", help="passe l'examen blanc d'un nœud")
    exam.add_argument("node")
    exam.add_argument("--answers", help="réponses séparées par des virgules (mode non interactif)")

    lab = sub.add_parser("lab", help="soumet la réponse d'un lab")
    lab.add_argument("node")
    lab.add_argument("answer", nargs="?", help="réponse (demandée si absente)")

    labd = sub.add_parser("labd", help="lab Docker interactif")
    labd.add_argument("node")

    lab_shell = sub.add_parser("lab-shell", help="shell de debug dans un lab Docker")
    lab_shell.add_argument("node")

    prove = sub.add_parser("prove", help="enregistre une preuve manuelle")
    prove.add_argument("node")
    prove.add_argument("--evidence", required=True, help="description de la preuve")

    history = sub.add_parser("history", help="historique des tentatives d'un nœud")
    history.add_argument("node")

    reset = sub.add_parser("reset", help="supprime les tentatives d'un nœud")
    reset.add_argument("node")

    sub.add_parser("import", help="recharge le contenu depuis content/")
    sub.add_parser("backup", help="sauvegarde la base SQLite et content/")

    export = sub.add_parser("export", help="génère content/ depuis le seed intégré")
    export.add_argument("--force", action="store_true", help="écrase un content/ existant")
    export.add_argument(
        "--yes", action="store_true", help="confirme l'écrasement sans demander (avec --force)"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    args = build_parser().parse_args(argv)

    STYLE.enabled = not args.no_color and sys.stdout.isatty()
    if STYLE.enabled and os.name == "nt":
        os.system("")

    if args.command == "export":
        return cmd_export(args)
    if args.command == "backup":
        return cmd_backup(args)

    conn = connect(args.db)
    try:
        initialize(conn)
        if args.command not in ("init", "import"):
            ensure_ready(conn)
        tree = SkillTree(conn)

        if args.command == "init":
            return cmd_init(conn, args)
        if args.command == "import":
            return cmd_import(conn, args)
        if args.command == "tree":
            return cmd_tree(tree, args)
        if args.command == "stats":
            return cmd_stats(tree, args)
        if args.command == "show":
            return cmd_show(tree, args)
        if args.command == "quiz":
            return cmd_quiz(tree, args)
        if args.command == "exam":
            return cmd_exam(tree, args)
        if args.command == "lab":
            return cmd_lab(tree, args)
        if args.command == "labd":
            return cmd_labd(tree, args)
        if args.command == "lab-shell":
            return cmd_lab_shell(tree, args)
        if args.command == "prove":
            return cmd_prove(tree, args)
        if args.command == "history":
            return cmd_history(tree, args)
        if args.command == "reset":
            return cmd_reset(tree, args)
        raise DomainError(f"Commande inconnue : {args.command}")
    except (DomainError, ContentError) as error:
        print(STYLE.paint(f"Erreur : {error}", "red"), file=sys.stderr)
        return 1
    finally:
        conn.close()
