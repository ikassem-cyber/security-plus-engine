from datetime import datetime
from security_plus_engine.main import QUESTIONS

from unittest.mock import patch
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from security_plus_engine.history import (
    load_history,
    save_history,
    create_attempt_record,
    calculate_historical_concept_performance,
)


class TestStudyHistory(unittest.TestCase):

    
    def test_historical_concept_accuracy(self):
        history = [
            {"concept_id": "1.2-C06", "correct": True},
            {"concept_id": "1.2-C06", "correct": False},
            {"concept_id": "1.2-C06", "correct": True},
            {"concept_id": "1.2-C06", "correct": False},
        ]

        results = calculate_historical_concept_performance(
            history,
            {"1.2-C06"},
        )

        self.assertEqual(results["1.2-C06"]["correct"], 2)
        self.assertEqual(results["1.2-C06"]["total"], 4)
        self.assertEqual(results["1.2-C06"]["accuracy"], 50.0)

    def test_multiple_concepts_are_tracked_separately(self):
        history = [
            {"concept_id": "1.2-C05", "correct": False},
            {"concept_id": "1.2-C05", "correct": True},
            {"concept_id": "1.2-C06", "correct": True},
        ]

        results = calculate_historical_concept_performance(
            history,
            {"1.2-C05", "1.2-C06"},
        )

        self.assertEqual(results["1.2-C05"]["accuracy"], 50.0)
        self.assertEqual(results["1.2-C06"]["accuracy"], 100.0)

    def test_unmapped_concepts_are_excluded(self):
        history = [
            {"concept_id": "1.2-C06", "correct": True},
            {"concept_id": "4.1-C01", "correct": False},
        ]

        results = calculate_historical_concept_performance(
            history,
            {"1.2-C06"},
        )

        self.assertIn("1.2-C06", results)
        self.assertNotIn("4.1-C01", results)

    def test_empty_history_returns_empty_performance(self):
        results = calculate_historical_concept_performance(
            [],
            {"1.2-C06"},
        )

        self.assertEqual(results, {})

    
    def test_failed_save_preserves_existing_history(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"

            original_attempts = [
                {
                    "question_id": "Q0002",
                    "concept_id": "1.2-C06",
                    "answer": 2,
                    "correct": True,
                }
            ]

            save_history(original_attempts, path)

            new_attempts = [
                {
                    "question_id": "Q0002",
                    "concept_id": "1.2-C06",
                    "answer": 1,
                    "correct": False,
                }
            ]

            with patch(
                "security_plus_engine.history.os.replace",
                side_effect=OSError("Simulated save failure"),
            ):
                with self.assertRaises(OSError):
                    save_history(new_attempts, path)

            self.assertEqual(
                load_history(path),
                original_attempts,
            )

            self.assertEqual(
                list(path.parent.glob(".study_history_*.tmp")),
                [],
            )

    def test_missing_history_returns_empty_list(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"

            self.assertEqual(load_history(path), [])

    def test_save_and_load_history(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"

            attempts = [
                {
                    "question_id": "Q0002",
                    "concept_id": "1.2-C06",
                    "answer": 2,
                    "correct": True,
                }
            ]

            save_history(attempts, path)
            loaded = load_history(path)

            self.assertEqual(loaded, attempts)

    def test_invalid_history_structure(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "history.json"
            path.write_text(
                '{"invalid": "structure"}',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_history(path)

    def test_save_creates_parent_directory(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "history.json"

            save_history([], path)

            self.assertTrue(path.exists())
            self.assertEqual(load_history(path), [])


    
    def test_create_attempt_record(self):
        question = QUESTIONS[1]

        record = create_attempt_record(
            question,
            answer=2,
            correct=True,
        )

        self.assertEqual(record["question_id"], "Q0002")
        self.assertEqual(record["objective_id"], "1.2")
        self.assertEqual(record["concept_id"], "1.2-C06")
        self.assertEqual(record["difficulty"], "foundational")
        self.assertEqual(record["answer"], 2)
        self.assertTrue(record["correct"])
        self.assertIn("timestamp", record)

    def test_attempt_timestamp_uses_utc(self):
        question = QUESTIONS[1]

        record = create_attempt_record(
            question,
            answer=1,
            correct=False,
        )

        timestamp = datetime.fromisoformat(record["timestamp"])

        self.assertIsNotNone(timestamp.tzinfo)
        self.assertEqual(
            timestamp.utcoffset().total_seconds(),
            0,
        )

