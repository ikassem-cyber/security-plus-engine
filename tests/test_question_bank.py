import json
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace

from security_plus_engine.main import Question
from security_plus_engine.question_bank import load_question_bank


class TestQuestionBank(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)

        self.valid_question = {
            "question_id": "Q1000",
            "domain": "2.0",
            "objective_id": "2.1",
            "concept_id": "2.1-C01",
            "difficulty": "hard",
            "question_type": "MCQ",
            "prompt": "Which threat actor is most likely state-sponsored?",
            "options": [
                "Nation-state",
                "Unskilled attacker",
                "Hacktivist",
                "Shadow IT",
            ],
            "correct_answer": 1,
            "explanation": "Nation-state actors operate on behalf of governments.",
            "source": "Original test question",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_questions(self, questions):
        path = self.directory / "domain_2.json"
        path.write_text(
            json.dumps(questions),
            encoding="utf-8",
        )


    def get_objectives_path(self):
        return (
            Path(__file__).resolve().parents[1]
            / "src"
            / "security_plus_engine"
            / "data"
            / "sy0_701_objectives.json"
        )
    
    def test_load_valid_question(self):
        self.write_questions([self.valid_question])

        questions = load_question_bank(
            self.directory,
            Question,
        )

        self.assertEqual(len(questions), 1)
        self.assertIsInstance(questions[0], Question)
        self.assertEqual(questions[0].concept_id, "2.1-C01")

    def test_missing_required_field(self):
        question = self.valid_question.copy()
        del question["explanation"]

        self.write_questions([question])

        with self.assertRaises(ValueError):
            load_question_bank(self.directory, Question)

    def test_duplicate_question_ids(self):
        self.write_questions([
            self.valid_question,
            self.valid_question.copy(),
        ])

        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_question_bank(self.directory, Question)

    def test_invalid_difficulty(self):
        question = self.valid_question.copy()
        question["difficulty"] = "impossible"

        self.write_questions([question])

        with self.assertRaises(ValueError):
            load_question_bank(self.directory, Question)

    def test_invalid_answer(self):
        question = self.valid_question.copy()
        question["correct_answer"] = 5

        self.write_questions([question])

        with self.assertRaises(ValueError):
            load_question_bank(self.directory, Question)

    def test_invalid_options(self):
        question = self.valid_question.copy()
        question["options"] = ["A", "B"]

        self.write_questions([question])

        with self.assertRaises(ValueError):
            load_question_bank(self.directory, Question)

    def test_missing_directory(self):
        missing = self.directory / "nonexistent"

        with self.assertRaises(FileNotFoundError):
            load_question_bank(missing, Question)

    def test_empty_question_bank(self):
        self.write_questions([])

        with self.assertRaises(ValueError):
            load_question_bank(self.directory, Question)


    def test_strict_mode_accepts_valid_mapping(self):
        self.write_questions([self.valid_question])

        questions = load_question_bank(
            self.directory,
            Question,
            objectives_path=self.get_objectives_path(),
        )

        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].concept_id, "2.1-C01")

    def test_strict_mode_rejects_unmapped_concept(self):
        question = self.valid_question.copy()
        question["concept_id"] = "2.1-C999"

        self.write_questions([question])

        with self.assertRaisesRegex(
            ValueError, "Unmapped concept"
        ):
            load_question_bank(
                self.directory,
                Question,
                objectives_path=self.get_objectives_path(),
            )

    def test_strict_mode_rejects_wrong_domain(self):
        question = self.valid_question.copy()
        question["domain"] = "3.0"

        self.write_questions([question])

        with self.assertRaisesRegex(
            ValueError, "does not match objective"
        ):
            load_question_bank(
                self.directory,
                Question,
                objectives_path=self.get_objectives_path(),
            )