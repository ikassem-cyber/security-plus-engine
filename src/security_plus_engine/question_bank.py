import json
from pathlib import Path

from security_plus_engine.question_validation import (
    load_objective_mappings,
    validate_question_mapping,
)


QUESTION_FIELDS = {
    "question_id",
    "domain",
    "objective_id",
    "concept_id",
    "difficulty",
    "question_type",
    "prompt",
    "options",
    "correct_answer",
    "explanation",
    "source",
}

VALID_DIFFICULTIES = {
    "foundational",
    "easy",
    "medium",
    "hard",
}


def load_question_bank(
    directory: Path,
    question_class,
    objectives_path: Path | None = None,
) -> list:

    
    """Load and validate questions from domain JSON files."""

    if not directory.is_dir():
        raise FileNotFoundError(
            f"Question-bank directory not found: {directory}"
        )

    questions = []
    seen_ids = set()

    mappings = (
        load_objective_mappings(objectives_path)
        if objectives_path is not None
        else None
    )

    for path in sorted(directory.glob("domain_*.json")):
        with path.open(encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError(
                f"{path.name} must contain a JSON array."
            )

        for number, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise ValueError(
                    f"{path.name}, question {number}: "
                    "Expected a JSON object."
                )

            missing = QUESTION_FIELDS - record.keys()

            if missing:
                raise ValueError(
                    f"{path.name}, question {number}: "
                    f"Missing fields: {sorted(missing)}"
                )

            question_id = record["question_id"]

            if not isinstance(question_id, str) or not question_id:
                raise ValueError("Question ID must be a nonempty string.")

            if question_id in seen_ids:
                raise ValueError(
                    f"Duplicate question ID: {question_id}"
                )

            seen_ids.add(question_id)

            if record["difficulty"] not in VALID_DIFFICULTIES:
                raise ValueError(
                    f"Invalid difficulty for {question_id}"
                )

            options = record["options"]

            if (
                not isinstance(options, list)
                or len(options) != 4
                or not all(
                    isinstance(option, str) and option.strip()
                    for option in options
                )
            ):
                raise ValueError(
                    f"{question_id} must have four nonempty options."
                )

            answer = record["correct_answer"]

            if type(answer) is not int or not 1 <= answer <= 4:
                raise ValueError(
                    f"Invalid correct answer for {question_id}"
                )

            question = question_class(
                **{
                    field: record[field]
                    for field in QUESTION_FIELDS
                }
            )

            if mappings is not None:
                errors = validate_question_mapping(
                    question,
                    mappings,
                )

                if errors:
                    raise ValueError(
                        "Invalid question mapping:\n"
                        + "\n".join(errors)
                    )

            questions.append(question)

    questions.sort(key=lambda question: question.question_id)
    
    if not questions:
        raise ValueError("No questions found in the question bank.")

    return questions