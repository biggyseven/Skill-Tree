import os
import re
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.environ.get("SKILLTREE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
DATA_IDS = [
    "data-bases-debutant",
    "data-sql-1-debutant",
    "data-modelisation-debutant",
    "data-sql-2-debutant",
    "data-normalisation-debutant",
    "data-sql-pratique-debutant",
    "data-dba-role-intermediaire",
    "data-sql-avance-intermediaire",
    "data-optimisation-intermediaire",
    "data-sauvegarde-intermediaire",
    "data-nosql-intermediaire",
    "data-warehouse-intermediaire",
    "data-bigdata-expert",
    "data-streaming-expert",
    "data-datalake-expert",
    "data-securite-expert",
    "data-gouvernance-expert",
    "data-ingestion-expert",
]

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))

        # Vérifier que le catalogue chargé par l'application contient les 18 cours Data.
        response = page.request.get(f"{BASE_URL}/api/tree")
        require(response.status == 200, f"/api/tree returned HTTP {response.status}")
        tree = response.json()
        node_by_id = {node["id"]: node for node in tree.get("nodes", [])}
        actual_ids = {node_id for node_id in node_by_id if node_id.startswith("data-")}
        require(actual_ids == set(DATA_IDS), f"Unexpected Data IDs: {sorted(actual_ids)}")

        # Contrôler le véritable contrat HTTP de chaque leçon et quiz.
        for node_id in DATA_IDS:
            node_response = page.request.get(f"{BASE_URL}/api/node/{node_id}")
            require(node_response.status == 200, f"{node_id}: node HTTP {node_response.status}")
            node = node_response.json()
            require(node.get("id") == node_id, f"{node_id}: mismatched node payload")

            lesson_response = page.request.get(f"{BASE_URL}/api/node/{node_id}/lesson")
            require(lesson_response.status == 200, f"{node_id}: lesson HTTP {lesson_response.status}")
            lesson = lesson_response.text()
            require(len(lesson.split()) >= 5000, f"{node_id}: lesson content is missing or too short")
            require("Mise en contexte" in lesson, f"{node_id}: missing lesson context box")

            quiz_response = page.request.get(f"{BASE_URL}/api/node/{node_id}/quiz")
            require(quiz_response.status == 200, f"{node_id}: quiz HTTP {quiz_response.status}")
            quiz = quiz_response.json()
            questions = quiz.get("questions", [])
            require(quiz.get("node_id") == node_id, f"{node_id}: mismatched quiz payload")
            require(5 <= len(questions) <= 8, f"{node_id}: unexpected quiz length {len(questions)}")
            for index, question in enumerate(questions, start=1):
                require(question.get("prompt"), f"{node_id} question {index}: missing prompt")
                require(len(question.get("choices", [])) == 4,
                        f"{node_id} question {index}: expected four choices")
                require("answer" not in question and "answer_regex" not in question,
                        f"{node_id} question {index}: private answer leaked by GET API")

        # Parcours navigateur réel : ouvrir le module, filtrer les 18 cours,
        # ouvrir la première leçon, charger son quiz puis soumettre des réponses.
        page_response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        require(page_response is not None and page_response.status == 200, "Dashboard did not load")
        module_button = page.locator("button.card-sm").filter(has_text="Data & Bases de données")
        expect(module_button).to_have_count(1, timeout=20000)
        module_button.click()

        data_course_buttons = page.locator("#tree-grid section button")
        expect(data_course_buttons).to_have_count(18, timeout=20000)
        visible_cards = "\n".join(button.inner_text() for button in data_course_buttons.all())
        for node_id in DATA_IDS:
            require(node_by_id[node_id]["title"] in visible_cards,
                    f"Filtered catalogue does not show {node_id}")

        first_title = node_by_id["data-bases-debutant"]["title"]
        first_course = page.locator("#tree-grid section button").filter(has_text=first_title)
        expect(first_course).to_have_count(1)
        first_course.click()

        dialog = page.get_by_role("dialog")
        expect(dialog).to_be_visible()
        expect(dialog.get_by_role("heading", name=first_title)).to_be_visible()
        expect(dialog.locator(".lesson-prose")).to_contain_text("Mise en contexte", timeout=20000)

        page_errors_before_quiz = len(page_errors)
        expect(dialog.get_by_role("button", name=re.compile("Passer à l'exercice"))).to_be_visible()
        dialog.get_by_role("button", name=re.compile("Passer à l'exercice")).click()
        expect(dialog.get_by_role("button", name="Démarrer l'exercice")).to_be_visible()

        quiz_url = f"{BASE_URL}/api/node/data-bases-debutant/quiz"
        with page.expect_response(lambda r: r.url == quiz_url and r.request.method == "GET") as quiz_response_info:
            dialog.get_by_role("button", name="Démarrer l'exercice").click()
        ui_quiz_response = quiz_response_info.value
        require(ui_quiz_response.status == 200,
                f"UI quiz loading returned HTTP {ui_quiz_response.status}")

        fieldsets = dialog.locator("fieldset")
        expect(fieldsets).to_have_count(5, timeout=15000)
        for fieldset in fieldsets.all():
            fieldset.locator('input[type="radio"]').first.check()

        with page.expect_response(lambda r: r.url == quiz_url and r.request.method == "POST") as submit_info:
            dialog.get_by_role("button", name="Valider mes réponses").click()
        submit_response = submit_info.value
        require(submit_response.status == 200,
                f"UI quiz submission returned HTTP {submit_response.status}")
        result = submit_response.json()
        require(result.get("success") is True and result.get("total") == 5,
                f"Unexpected quiz submission response: {result}")
        expect(dialog.locator('div[x-show="quizResult"] p')).to_contain_text("/100", timeout=15000)

        new_page_errors = page_errors[page_errors_before_quiz:]
        require(not new_page_errors, f"Browser JavaScript errors during course/quiz journey: {new_page_errors}")

        print("PASS: 18 Data nodes, 18 lessons, 18 quiz APIs, Data filter, lesson reader and quiz submission.")
        browser.close()

if __name__ == "__main__":
    main()
