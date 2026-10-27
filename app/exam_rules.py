"""Règles communes de réussite des examens.

Les seuils des quiz et des labs restent configurables séparément.
"""

EXAM_PASS_SCORE = 80


def effective_requirement_score(kind, configured_score: int) -> int:
    """Retourne le seuil effectif d'une exigence du parcours.

    Les anciennes données peuvent encore contenir un seuil d'examen différent.
    Le seuil officiel des examens est désormais uniforme à 80 %.
    """
    kind_value = getattr(kind, "value", kind)
    if str(kind_value).strip().lower() == "exam":
        return EXAM_PASS_SCORE
    return int(configured_score)
