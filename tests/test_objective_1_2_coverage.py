
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


EXPECTED_CONCEPTS = {
    "1.2-C01": "Confidentiality",
    "1.2-C02": "Integrity",
    "1.2-C03": "Availability",
    "1.2-C04": "Non-repudiation",
    "1.2-C05": "Authentication",
    "1.2-C06": "Authorization",
    "1.2-C07": "Accounting",
    "1.2-C08": "Authorization models",
    "1.2-C09": "Gap analysis",
    "1.2-C10": "Zero Trust architecture",
    "1.2-C11": "Control plane",
    "1.2-C12": "Adaptive identity",
    "1.2-C13": "Threat scope reduction",
    "1.2-C14": "Policy-driven access control",
    "1.2-C15": "Secured zones",
    "1.2-C16": "Data plane",
    "1.2-C17": "Subject/system",
    "1.2-C18": "Policy engine",
    "1.2-C19": "Policy administrator",
    "1.2-C20": "Policy enforcement point",
    "1.2-C21": "Bollards",
    "1.2-C22": "Access control vestibule",
    "1.2-C23": "Fencing",
    "1.2-C24": "Video surveillance",
    "1.2-C25": "Security guards",
    "1.2-C26": "Access badges",
    "1.2-C27": "Lighting",
    "1.2-C28": "Physical security sensors",
    "1.2-C29": "Infrared sensors",
    "1.2-C30": "Pressure sensors",
    "1.2-C31": "Microwave sensors",
    "1.2-C32": "Ultrasonic sensors",
    "1.2-C33": "Honeypot",
    "1.2-C34": "Honeynet",
    "1.2-C35": "Honeyfile",
    "1.2-C36": "Honeytoken",
}


class TestObjective12Coverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with OBJECTIVES_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        cls.objective = next(
            objective
            for domain in data["domains"]
            for objective in domain["objectives"]
            if objective["id"] == "1.2"
        )

    def test_all_expected_concepts_exist(self):
        actual = {
            concept["concept_id"]: concept["name"]
            for concept in self.objective["concepts"]
        }

        for concept_id, expected_name in EXPECTED_CONCEPTS.items():
            with self.subTest(concept_id=concept_id):
                self.assertIn(concept_id, actual)
                self.assertEqual(actual[concept_id], expected_name)

    def test_all_concepts_have_keywords(self):
        for concept in self.objective["concepts"]:
            with self.subTest(concept=concept["concept_id"]):
                self.assertGreater(
                    len(concept["keywords"]), 0
                )

    def test_all_concepts_have_relationships(self):
        for concept in self.objective["concepts"]:
            with self.subTest(concept=concept["concept_id"]):
                self.assertGreater(
                    len(concept["related_concepts"]), 0
                )


if __name__ == "__main__":
    unittest.main()
