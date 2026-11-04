
import json
import unittest
from pathlib import Path


OBJECTIVES_FILE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "security_plus_engine"
    / "data"
    / "sy0_701_objectives.json"
)


class TestObjective13Coverage(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        data = json.loads(
            OBJECTIVES_FILE.read_text(encoding="utf-8")
        )

        cls.objective = next(
            objective
            for domain in data["domains"]
            for objective in domain["objectives"]
            if objective["id"] == "1.3"
        )

        cls.concepts = cls.objective["concepts"]

    def test_objective_has_18_concepts(self):
        self.assertEqual(len(self.concepts), 18)

    def test_concept_ids_are_unique(self):
        concept_ids = [
            concept["concept_id"]
            for concept in self.concepts
        ]

        self.assertEqual(
            len(concept_ids),
            len(set(concept_ids)),
        )

    def test_all_expected_concept_ids_exist(self):
        expected_ids = {
            f"1.3-C{i:02d}"
            for i in range(1, 19)
        }

        actual_ids = {
            concept["concept_id"]
            for concept in self.concepts
        }

        self.assertEqual(actual_ids, expected_ids)

    def test_all_concepts_have_required_fields(self):
        required_fields = {
            "concept_id",
            "name",
            "category",
            "keywords",
            "related_concepts",
            "question_types",
        }

        for concept in self.concepts:
            with self.subTest(
                concept_id=concept["concept_id"]
            ):
                self.assertTrue(
                    required_fields.issubset(concept)
                )

    def test_all_concepts_have_keywords(self):
        for concept in self.concepts:
            with self.subTest(
                concept_id=concept["concept_id"]
            ):
                self.assertTrue(concept["keywords"])

    def test_all_concepts_support_question_types(self):
        expected_types = {"MCQ", "scenario", "PBQ"}

        for concept in self.concepts:
            with self.subTest(
                concept_id=concept["concept_id"]
            ):
                self.assertEqual(
                    set(concept["question_types"]),
                    expected_types,
                )

    
    def test_official_concept_names_and_categories(self):
        concepts_by_id = {
            concept["concept_id"]: concept
            for concept in self.concepts
        }

        self.assertEqual(
            concepts_by_id["1.3-C05"]["name"],
            "Test results",
        )

        self.assertEqual(
            concepts_by_id["1.3-C18"]["name"],
            "Version control",
        )

        self.assertEqual(
            concepts_by_id["1.3-C18"]["category"],
            "Version control",
        )

        self.assertEqual(
            concepts_by_id["1.3-C05"]["category"],
            "Business processes",
        )


if __name__ == "__main__":
    unittest.main()
