import unittest

from security_plus_engine.main import (
    DOMAINS,
    QUESTIONS,
    calculate_domain_performance,
    check_answer,
)



class TestQuizAnswers(unittest.TestCase):

    def test_correct_answer(self):
        question = QUESTIONS[0]
        self.assertTrue(check_answer(question, 2))

    def test_incorrect_answer(self):
        question = QUESTIONS[0]
        self.assertFalse(check_answer(question, 1))

    def test_another_correct_answer(self):
        question = QUESTIONS[1]
        self.assertTrue(check_answer(question, 2))

    def test_answer_below_valid_range(self):
        question = QUESTIONS[0]
        self.assertFalse(check_answer(question, 0))

    def test_answer_above_valid_range(self):
        question = QUESTIONS[0]
        self.assertFalse(check_answer(question, 5))


class TestExamDomains(unittest.TestCase):

    def test_all_five_domains_exist(self):
        self.assertEqual(len(DOMAINS), 5)

    def test_domain_weights_total_100(self):
        total_weight = sum(
            domain["weight"] for domain in DOMAINS.values()
        )
        self.assertEqual(total_weight, 100)

    def test_every_question_has_valid_domain(self):
        for question in QUESTIONS:
            self.assertIn(question.domain, DOMAINS)


class TestDomainPerformance(unittest.TestCase):

    def test_domain_accuracy(self):
        answers = [2, 2, 3]

        results = calculate_domain_performance(QUESTIONS, answers)

        self.assertEqual(results["1.0"]["correct"], 2)
        self.assertEqual(results["1.0"]["total"], 2)
        self.assertEqual(results["1.0"]["accuracy"], 100.0)

        self.assertEqual(results["4.0"]["correct"], 1)
        self.assertEqual(results["4.0"]["total"], 1)
        self.assertEqual(results["4.0"]["accuracy"], 100.0)

    def test_unattempted_domains_have_zero_accuracy(self):
        results = calculate_domain_performance(QUESTIONS, [2, 2, 3])

        self.assertEqual(results["2.0"]["total"], 0)
        self.assertEqual(results["2.0"]["accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
