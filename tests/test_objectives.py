import json
import unittest
from pathlib import Path


OBJECTIVES_FILE = (
    Path(__file__).parent.parent
    / "src"
    / "security_plus_engine"
    / "data"
    / "sy0_701_objectives.json"
)


class TestSecurityPlusObjectives(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with OBJECTIVES_FILE.open(encoding="utf-8") as file:
            cls.data = json.load(file)

    def test_exam_code(self):
        self.assertEqual(self.data["exam_code"], "SY0-701")

    def test_five_domains_exist(self):
        self.assertEqual(len(self.data["domains"]), 5)

    def test_domain_weights_total_100(self):
        total = sum(
            domain["weight"] for domain in self.data["domains"]
        )
        self.assertEqual(total, 100)

    def test_28_objectives_exist(self):
        objectives = [
            objective
            for domain in self.data["domains"]
            for objective in domain["objectives"]
        ]
        self.assertEqual(len(objectives), 28)

    def test_objective_ids_are_unique(self):
        ids = [
            objective["id"]
            for domain in self.data["domains"]
            for objective in domain["objectives"]
        ]
        self.assertEqual(len(ids), len(set(ids)))

    def test_concept_ids_are_unique(self):
        concept_ids = [
            topic["concept_id"]
            for domain in self.data["domains"]
            for objective in domain["objectives"]
            for topic in objective["concepts"]
        ]
        self.assertEqual(len(concept_ids), len(set(concept_ids)))

    def test_concepts_have_required_fields(self):
        for domain in self.data["domains"]:
            for objective in domain["objectives"]:
                for topic in objective["concepts"]:
                    with self.subTest(topic=topic.get("concept_id")):
                        self.assertTrue(topic["concept_id"])
                        self.assertTrue(topic["name"])
                        self.assertTrue(topic["category"])
                        self.assertTrue(topic["keywords"])
                        self.assertTrue(topic["question_types"])

    def test_question_types_are_valid(self):
        allowed_types = {
            "MCQ",
            "scenario",
            "short_answer",
            "PBQ",
        }

        for domain in self.data["domains"]:
            for objective in domain["objectives"]:
                for topic in objective["concepts"]:
                    for question_type in topic["question_types"]:
                        self.assertIn(question_type, allowed_types)


if __name__ == "__main__":
    unittest.main()
