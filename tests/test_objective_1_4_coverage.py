import json
import unittest
from pathlib import Path


OBJECTIVES_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "security_plus_engine"
    / "data"
    / "sy0_701_objectives.json"
)


def find_objective(node, objective_id):
    if isinstance(node, dict):
        if node.get("id") == objective_id:
            return node

        for value in node.values():
            result = find_objective(value, objective_id)
            if result is not None:
                return result

    elif isinstance(node, list):
        for item in node:
            result = find_objective(item, objective_id)
            if result is not None:
                return result

    return None


class TestObjective14Coverage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with OBJECTIVES_PATH.open(encoding="utf-8") as file:
            data = json.load(file)

        cls.objective = find_objective(data, "1.4")

        if cls.objective is None:
            raise AssertionError("Objective 1.4 not found")

        cls.concepts = cls.objective["concepts"]

    def test_objective_has_39_concepts(self):
        self.assertEqual(len(self.concepts), 39)

    def test_all_expected_concept_ids_exist(self):
        expected = {
            f"1.4-C{number:02d}"
            for number in range(1, 40)
        }

        actual = {
            concept["concept_id"]
            for concept in self.concepts
        }

        self.assertEqual(actual, expected)

    def test_concept_ids_are_unique(self):
        ids = [
            concept["concept_id"]
            for concept in self.concepts
        ]

        self.assertEqual(len(ids), len(set(ids)))

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
            with self.subTest(concept=concept["concept_id"]):
                self.assertTrue(
                    required_fields.issubset(concept)
                )

    def test_all_concepts_have_keywords(self):
        for concept in self.concepts:
            with self.subTest(concept=concept["concept_id"]):
                self.assertTrue(concept["keywords"])

    def test_all_concepts_support_question_types(self):
        required_types = {"MCQ", "scenario", "PBQ"}

        for concept in self.concepts:
            with self.subTest(concept=concept["concept_id"]):
                self.assertTrue(
                    required_types.issubset(
                        set(concept["question_types"])
                    )
                )

    def test_essential_cryptography_keywords(self):
        all_keywords = {
            keyword.lower()
            for concept in self.concepts
            for keyword in concept["keywords"]
        }

        required_keywords = {
            "aes",
            "rsa",
            "ecc",
            "diffie-hellman",
            "ecdhe",
            "tls",
            "sha-256",
            "pbkdf2",
            "bcrypt",
            "tpm",
            "hsm",
            "kms",
            "crl",
            "ocsp",
            "csr",
            "bitlocker",
            "efs",
            "tde",
        }

        self.assertTrue(
            required_keywords.issubset(all_keywords),
            f"Missing keywords: {required_keywords - all_keywords}"
        )

    def test_all_nine_cryptographic_categories_exist(self):
        expected_categories = {
            "PKI",
            "Encryption",
            "Cryptographic tools",
            "Obfuscation",
            "Hashing",
            "Digital signatures",
            "Key stretching",
            "Blockchain",
            "Certificates",
        }

        actual_categories = {
            concept["category"]
            for concept in self.concepts
        }

        self.assertEqual(actual_categories, expected_categories)


    def test_related_concepts_reference_valid_ids(self):
        valid_ids = {
            concept["concept_id"]
            for concept in self.concepts
        }

        for concept in self.concepts:
            concept_id = concept["concept_id"]

            for related_id in concept["related_concepts"]:
                with self.subTest(
                    concept=concept_id,
                    related=related_id,
                ):
                    self.assertIn(related_id, valid_ids)
                    self.assertNotEqual(concept_id, related_id)

    def test_relationships_are_reciprocal(self):
        concept_lookup = {
            concept["concept_id"]: concept
            for concept in self.concepts
        }

        for concept in self.concepts:
            concept_id = concept["concept_id"]

            for related_id in concept["related_concepts"]:
                with self.subTest(
                    concept=concept_id,
                    related=related_id,
                ):
                    self.assertIn(
                        concept_id,
                        concept_lookup[related_id]["related_concepts"],
                    )