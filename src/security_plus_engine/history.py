import os
import tempfile
import json
from pathlib import Path

from datetime import datetime, timezone

HISTORY_PATH = Path("data/user/study_history.json")


def load_history(path: Path = HISTORY_PATH) -> list[dict]:
    """Load previous question attempts from local JSON storage."""

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        history = json.load(file)

    if not isinstance(history, list):
        raise ValueError("Study history must contain a list.")

    return history



def save_history(
    history: list[dict],
    path: Path = HISTORY_PATH,
) -> None:
    """Atomically save question attempts to local JSON storage."""

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".study_history_",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)

            json.dump(history, file, indent=2)
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, path)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)



def create_attempt_record(
    question,
    answer: int,
    correct: bool,
) -> dict:
    """Create a timestamped record of a question attempt."""

    return {
        "question_id": question.question_id,
        "objective_id": question.objective_id,
        "concept_id": question.concept_id,
        "difficulty": question.difficulty,
        "answer": answer,
        "correct": correct,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }



def calculate_historical_concept_performance(
    history: list[dict],
    valid_concept_ids: set[str],
) -> dict:
    """Calculate concept accuracy from saved study attempts."""

    performance = {}

    for attempt in history:
        concept_id = attempt["concept_id"]

        if concept_id not in valid_concept_ids:
            continue

        if concept_id not in performance:
            performance[concept_id] = {
                "correct": 0,
                "total": 0,
                "accuracy": 0.0,
            }

        performance[concept_id]["total"] += 1

        if attempt["correct"]:
            performance[concept_id]["correct"] += 1

    for results in performance.values():
        results["accuracy"] = (
            results["correct"] / results["total"]
        ) * 100

    return performance
