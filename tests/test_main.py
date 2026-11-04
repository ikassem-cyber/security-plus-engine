import unittest

from security_plus_engine.main import QUESTIONS, check_answer


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


if __name__ == "__main__":
    unittest.main()
