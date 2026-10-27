import json
import re
from collections import Counter
from pathlib import Path

EXAM_DIR = Path(__file__).resolve().parents[1] / "content" / "exam"
EXAM_IDS = ("ipv6-expert", "bgp-expert")
PLACEHOLDER = re.compile(
    r"avez-vous bien lu|question temporaire|question placeholder|"
    r"généré automatiquement|(?:^|\s)réponse\s+[a-d](?:\s|$)",
    re.IGNORECASE,
)
ANCHORS = {
    "ipv6-expert": (
        "Pourquoi une politique de pare-feu IPv6 ne doit-elle pas bloquer indistinctement tout ICMPv6 ?",
        3,
        "Neighbor Discovery",
    ),
    "bgp-expert": (
        "Quel est l’objectif du comportement eBGP par défaut de RFC 8212 sur les équipements conformes ?",
        3,
        "politiques d’import et d’export explicites",
    ),
}


def _load(exam_id: str) -> dict:
    return json.loads((EXAM_DIR / f"{exam_id}.json").read_text(encoding="utf-8"))


def test_exam_banks_have_twenty_valid_questions_and_balanced_keys():
    prompts = set()
    for exam_id in EXAM_IDS:
        bank = _load(exam_id)
        assert bank["node_id"] == exam_id
        assert bank["scope"] == "exam"
        assert len(bank["questions"]) == 20, f"{exam_id}: expected 20 questions"
        answer_positions = Counter()
        local_prompts = set()
        for question in bank["questions"]:
            assert question["type"] == "qcm"
            assert question["prompt"].strip()
            assert question["explanation"].strip()
            assert len(question["choices"]) == 4
            assert all(choice.strip() for choice in question["choices"])
            assert len(set(question["choices"])) == 4
            assert type(question["answer"]) is int and 0 <= question["answer"] < 4
            assert not PLACEHOLDER.search(
                question["prompt"] + " " + " ".join(question["choices"]) + " " + question["explanation"]
            )
            assert question["prompt"] not in local_prompts
            assert question["prompt"] not in prompts
            local_prompts.add(question["prompt"])
            prompts.add(question["prompt"])
            answer_positions[question["answer"]] += 1
        assert answer_positions == Counter({0: 5, 1: 5, 2: 5, 3: 5}), (
            f"{exam_id}: unbalanced answer positions {answer_positions}"
        )


def test_exam_banks_have_technical_answer_anchors():
    for exam_id, (prompt, expected_index, fragment) in ANCHORS.items():
        matches = [
            question for question in _load(exam_id)["questions"]
            if question["prompt"] == prompt
        ]
        assert len(matches) == 1, f"{exam_id}: anchor missing or duplicated"
        question = matches[0]
        assert question["answer"] == expected_index
        assert fragment.casefold() in question["choices"][expected_index].casefold()


def test_ipv6_exam_covers_expert_operational_topics():
    content = " ".join(
        question["prompt"] + " " + " ".join(question["choices"]) + " " + question["explanation"]
        for question in _load("ipv6-expert")["questions"]
    ).casefold()
    for concept in ("slaac", "dhcpv6-pd", "icmpv6", "pmTUD".casefold(), "dns64", "nat64", "bgp"):
        assert concept in content, f"IPv6 exam coverage missing: {concept}"


def test_bgp_exam_covers_policy_security_and_operations():
    content = " ".join(
        question["prompt"] + " " + " ".join(question["choices"]) + " " + question["explanation"]
        for question in _load("bgp-expert")["questions"]
    ).casefold()
    for concept in ("rfc 8212", "rpki", "otc", "graceful restart", "max-prefix", "route reflector", "longest-prefix match"):
        assert concept in content, f"BGP exam coverage missing: {concept}"
