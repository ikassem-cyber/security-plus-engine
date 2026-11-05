import unittest
from pathlib import Path
from dataclasses import replace

from security_plus_engine.main import QUESTIONS
from security_plus_engine.question_validation import (
    load_objective_mappings,
    validate_question_mapping,
)


class TestQuestionValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "security_plus_engine"
            / "data"
            / "sy0_701_objectives.json"
        )
        cls.mappings = load_objective_mappings(path)
        cls.questions = {
            question.question_id: question
            for question in QUESTIONS
        }

    def test_valid_question_mapping(self):
        question = self.questions["Q0002"]

        errors = validate_question_mapping(
            question, self.mappings
        )

        self.assertEqual(errors, [])

    def test_unmapped_concept_detected(self):
        question = self.questions["Q0001"]

        errors = validate_question_mapping(
            question, self.mappings
        )

        self.assertTrue(
            any("Unmapped concept" in error for error in errors)
        )

    def test_unknown_objective_detected(self):
        question = replace(
            self.questions["Q0002"],
            objective_id="9.9",
        )

        errors = validate_question_mapping(
            question, self.mappings
        )

        self.assertTrue(
            any("Unknown objective" in error for error in errors)
        )

    def test_wrong_domain_detected(self):
        question = replace(
            self.questions["Q0002"],
            domain="3.0",
        )

        errors = validate_question_mapping(
            question, self.mappings
        )

        self.assertTrue(
            any("does not match objective" in error for error in errors)
        )

    def test_wrong_concept_detected(self):
        question = replace(
            self.questions["Q0002"],
            concept_id="1.2-C999",
        )

        errors = validate_question_mapping(
            question, self.mappings
        )

        self.assertTrue(
            any("Unmapped concept" in error for error in errors)
        )

    def test_all_objectives_are_loaded(self):
        self.assertEqual(len(self.mappings), 28)