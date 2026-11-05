import json
from pathlib import Path


def load_objective_mappings(path: Path) -> dict:
    """Build a lookup of domains, objectives, and concepts."""

    data = json.loads(path.read_text(encoding="utf-8"))
    mappings = {}

    for domain in data["domains"]:
        for objective in domain["objectives"]:
            objective_id = objective["id"]

            mappings[objective_id] = {
                "domain": f"{objective_id.split('.')[0]}.0",
                "concepts": {
                    concept["concept_id"]
                    for concept in objective["concepts"]
                },
            }

    return mappings


def validate_question_mapping(question, mappings: dict) -> list[str]:
    """Return mapping errors for a question."""

    errors = []

    objective = mappings.get(question.objective_id)

    if objective is None:
        errors.append(
            f"{question.question_id}: Unknown objective "
            f"{question.objective_id}"
        )
        return errors

    if question.domain != objective["domain"]:
        errors.append(
            f"{question.question_id}: Domain {question.domain} "
            f"does not match objective {question.objective_id}"
        )

    if question.concept_id not in objective["concepts"]:
        errors.append(
            f"{question.question_id}: Unmapped concept "
            f"{question.concept_id}"
        )

    return errors