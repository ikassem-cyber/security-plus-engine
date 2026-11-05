import json
import unittest
from pathlib import Path


OBJECTIVES_PATH = (
    Path(__file__).resolve().parents[1]
    / "src/security_plus_engine/data/sy0_701_objectives.json"
)


class TestObjective21Coverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with OBJECTIVES_PATH.open(encoding="utf-8") as file:
            data = json.load(file)

        cls.objective = next(
            objective
            for domain in data["domains"]
            for objective in domain["objectives"]
            if objective["id"] == "2.1"
        )

        cls.concepts = cls.objective["concepts"]

    def test_all_19_concepts_exist(self):
        self.assertEqual(len(self.concepts), 19)

    def test_expected_concept_ids(self):
        expected = {
            f"2.1-C{i:02d}"
            for i in range(1, 20)
        }
        actual = {
            concept["concept_id"]
            for concept in self.concepts
        }
        self.assertEqual(actual, expected)

    def test_official_topic_categories(self):
        expected = {
            "Threat actors": 6,
            "Attributes of actors": 3,
            "Motivations": 10,
        }

        actual = {
            category: sum(
                concept["category"] == category
                for concept in self.concepts
            )
            for category in expected
        }

        self.assertEqual(actual, expected)

    def test_all_concepts_have_keywords(self):
        for concept in self.concepts:
            with self.subTest(concept=concept["concept_id"]):
                self.assertTrue(concept["keywords"])

    def test_all_concepts_have_required_metadata(self):
        required = {
            "concept_id",
            "name",
            "category",
            "keywords",
            "related_concepts",
            "question_types",
        }

        for concept in self.concepts:
            with self.subTest(concept=concept["concept_id"]):
                self.assertTrue(required.issubset(concept))
                self.assertEqual(
                    set(concept["question_types"]),
                    {"MCQ", "scenario", "PBQ"},
                )

    def test_official_concept_names(self):
        expected = {
            "Nation-state",
            "Unskilled attacker",
            "Hacktivist",
            "Insider threat",
            "Organized crime",
            "Shadow IT",
            "Internal/external",
            "Resources/funding",
            "Level of sophistication/capability",
            "Data exfiltration",
            "Espionage",
            "Service disruption",
            "Blackmail",
            "Financial gain",
            "Philosophical/political beliefs",
            "Ethical",
            "Revenge",
            "Disruption/chaos",
            "War",
        }

        actual = {
            concept["name"]
            for concept in self.concepts
        }

        self.assertEqual(actual, expected)