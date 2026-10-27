import json
import re
from collections import Counter
from pathlib import Path

QUIZ_DIR = Path(__file__).resolve().parents[1] / "content" / "quiz"
LEVELS = ("debutant", "intermediaire", "expert")
PREFIX = "telecom-bgp-peering"
PLACEHOLDER_RE = re.compile(
    r"avez-vous bien lu|question temporaire|placeholder|réponse [a-d]|"
    r"question placeholder|généré automatiquement|quiz généré automatiquement",
    re.IGNORECASE,
)

EXPECTED_ANCHORS = {
    "debutant": (
        "Quel protocole de transport et quel port sont normalement utilisés par une session BGP ?",
        1,
        "TCP",
    ),
    "intermediaire": (
        "Quel problème les route reflectors résolvent-ils principalement dans un grand domaine iBGP ?",
        3,
        "route reflector",
    ),
    "expert": (
        "Sur un routeur appliquant le comportement défini par RFC 8212, que se passe-t-il sur une session eBGP sans politique d’import ou d’export explicite applicable ?",
        0,
        "routes reçues",
    ),
}


def _load(level: str) -> dict:
    path = QUIZ_DIR / f"{PREFIX}-{level}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_three_levels_have_eight_real_qcm_questions():
    prompts = set()
    for level in LEVELS:
        quiz = _load(level)
        assert quiz["node_id"] == f"{PREFIX}-{level}"
        assert quiz["scope"] == "quiz"
        questions = quiz["questions"]
        assert len(questions) == 8, f"{level}: expected 8 questions"

        answers = Counter()
        level_prompts = set()
        for question in questions:
            assert question["type"] == "qcm"
            assert isinstance(question["prompt"], str) and question["prompt"].strip()
            assert isinstance(question["explanation"], str) and question["explanation"].strip()
            assert len(question["choices"]) == 4
            assert all(isinstance(choice, str) and choice.strip() for choice in question["choices"])
            assert len(set(question["choices"])) == 4
            assert type(question["answer"]) is int
            assert 0 <= question["answer"] < 4
            assert not PLACEHOLDER_RE.search(question["prompt"])
            assert not PLACEHOLDER_RE.search(" ".join(question["choices"]))
            assert not PLACEHOLDER_RE.search(question["explanation"])
            assert question["prompt"] not in level_prompts, f"{level}: duplicated prompt"
            level_prompts.add(question["prompt"])
            assert question["prompt"] not in prompts, "prompt duplicated across levels"
            prompts.add(question["prompt"])
            answers[question["answer"]] += 1

        assert answers == Counter({0: 2, 1: 2, 2: 2, 3: 2}), (
            f"{level}: answer positions should be evenly distributed, got {answers}"
        )


def test_technical_answer_anchors():
    for level, (prompt, expected_index, choice_fragment) in EXPECTED_ANCHORS.items():
        questions = _load(level)["questions"]
        matches = [question for question in questions if question["prompt"] == prompt]
        assert len(matches) == 1, f"{level}: missing or duplicated anchor question"
        question = matches[0]
        assert question["answer"] == expected_index
        assert choice_fragment.casefold() in question["choices"][expected_index].casefold()


def test_quizzes_cover_policy_security_and_operational_topics():
    beginner = " ".join(q["prompt"] + " " + q["explanation"] for q in _load("debutant")["questions"]).casefold()
    intermediate = " ".join(q["prompt"] + " " + q["explanation"] for q in _load("intermediaire")["questions"]).casefold()
    expert = " ".join(q["prompt"] + " " + q["explanation"] for q in _load("expert")["questions"]).casefold()

    assert "peering" in beginner and "port 179" in beginner and "asn" in beginner
    assert "local_pref" in intermediate and "max-prefix" in intermediate and "med" in intermediate
    assert "rfc 8212" in expert and "rpki" in expert and "fuite de routes" in expert
