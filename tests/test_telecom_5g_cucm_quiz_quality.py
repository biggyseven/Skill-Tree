import json
import re
from collections import Counter
from pathlib import Path

QUIZ_DIR = Path(__file__).resolve().parents[1] / "content" / "quiz"
QUIZ_IDS = (
    "telecom-5g-debutant",
    "telecom-5g-intermediaire",
    "telecom-5g-expert",
    "voice-cucm-debutant",
    "voice-cucm-intermediaire",
    "voice-cucm-expert",
)
PLACEHOLDER_RE = re.compile(
    r"avez-vous bien lu|question temporaire|placeholder|(?:^|\\s)réponse\\s+[a-d](?:\\s|$)|"
    r"question placeholder|généré automatiquement|quiz généré automatiquement",
    re.IGNORECASE,
)
EXPECTED_ANCHORS = {
    "telecom-5g-debutant": (
        "Quel composant fournit l’accès radio en 5G NR ?", 0, "gNodeB"
    ),
    "telecom-5g-intermediaire": (
        "Quelle fonction du cœur 5G gère notamment l’enregistrement et la mobilité de l’UE ?",
        0, "AMF"
    ),
    "telecom-5g-expert": (
        "Quel rôle joue le Network Repository Function (NRF) dans l’architecture 5G basée sur les services ?",
        0, "fonctions réseau"
    ),
    "voice-cucm-debutant": (
        "Quel est le rôle principal de CUCM ?", 0, "contrôle d’appel"
    ),
    "voice-cucm-intermediaire": (
        "Un SIP trunk est déclaré actif, mais certains numéros échouent. Que faut-il conclure ?",
        1, "ne garantit pas"
    ),
    "voice-cucm-expert": (
        "Quel rôle général distingue le Publisher des Subscribers dans un cluster CUCM ?",
        0, "base de configuration principale"
    ),
}


def _load(quiz_id: str) -> dict:
    path = QUIZ_DIR / f"{quiz_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_six_quizzes_have_eight_valid_questions():
    all_prompts = set()
    for quiz_id in QUIZ_IDS:
        quiz = _load(quiz_id)
        assert quiz["node_id"] == quiz_id
        assert quiz["scope"] == "quiz"
        questions = quiz["questions"]
        assert len(questions) == 8, f"{quiz_id}: expected 8 questions"

        answer_positions = Counter()
        local_prompts = set()
        for question in questions:
            assert question["type"] == "qcm"
            assert question["prompt"].strip()
            assert question["explanation"].strip()
            assert len(question["choices"]) == 4
            assert all(isinstance(choice, str) and choice.strip() for choice in question["choices"])
            assert len(set(question["choices"])) == 4
            assert type(question["answer"]) is int
            assert 0 <= question["answer"] <= 3
            assert not PLACEHOLDER_RE.search(
                question["prompt"] + " " + " ".join(question["choices"]) + " " + question["explanation"]
            )
            assert question["prompt"] not in local_prompts, f"{quiz_id}: duplicated prompt"
            assert question["prompt"] not in all_prompts, "duplicate prompt across quiz levels"
            local_prompts.add(question["prompt"])
            all_prompts.add(question["prompt"])
            answer_positions[question["answer"]] += 1

        assert answer_positions == Counter({0: 2, 1: 2, 2: 2, 3: 2}), (
            f"{quiz_id}: answer key positions must be balanced, got {answer_positions}"
        )


def test_technical_answer_anchors():
    for quiz_id, (prompt, answer_index, answer_fragment) in EXPECTED_ANCHORS.items():
        questions = _load(quiz_id)["questions"]
        matches = [question for question in questions if question["prompt"] == prompt]
        assert len(matches) == 1, f"{quiz_id}: missing or duplicate anchor question"
        question = matches[0]
        assert question["answer"] == answer_index
        assert answer_fragment.casefold() in question["choices"][answer_index].casefold()


def test_5g_and_cucm_core_concepts_are_covered():
    all_content = {
        quiz_id: " ".join(
            question["prompt"] + " " + " ".join(question["choices"]) + " " + question["explanation"]
            for question in _load(quiz_id)["questions"]
        ).casefold()
        for quiz_id in QUIZ_IDS
    }
    assert "gNodeB".casefold() in all_content["telecom-5g-debutant"]
    assert "S-NSSAI".casefold() in all_content["telecom-5g-intermediaire"]
    assert "UPF".casefold() in all_content["telecom-5g-expert"]
    assert "calling search space" in all_content["voice-cucm-debutant"]
    assert "route group" in all_content["voice-cucm-intermediaire"]
    assert "srtp" in all_content["voice-cucm-expert"]
