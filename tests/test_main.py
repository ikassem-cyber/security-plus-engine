from dataclasses import replace
import unittest
from io import StringIO
from unittest import result
from unittest.mock import patch
import json
from pathlib import Path


from security_plus_engine.main import (
    Question,
)


from security_plus_engine.main import (
    DOMAINS,
    QUESTIONS,
    calculate_domain_performance,
    calculate_concept_performance,
    load_valid_concept_ids,
    select_adaptive_questions,
    check_answer,
    get_adaptive_question_order,
    run_quiz,   
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


class TestQuestionMetadata(unittest.TestCase):

    def test_question_ids_are_unique(self):
        ids = [question.question_id for question in QUESTIONS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_question_has_objective_id(self):
        for question in QUESTIONS:
            self.assertTrue(question.objective_id)

    def test_every_question_has_concept_id(self):
        for question in QUESTIONS:
            self.assertTrue(question.concept_id)

    def test_question_difficulties_are_valid(self):
        valid_difficulties = {
            "foundational",
            "applied",
            "advanced",
            "expert",
        }

        for question in QUESTIONS:
            self.assertIn(question.difficulty, valid_difficulties)

    def test_question_types_are_valid(self):
        valid_types = {
            "MCQ",
            "scenario",
            "PBQ",
            "short_answer",
        }

        for question in QUESTIONS:
            self.assertIn(question.question_type, valid_types)

    def test_every_question_has_source(self):
        for question in QUESTIONS:
            self.assertTrue(question.source)





class TestInteractiveQuiz(unittest.TestCase):

    
    def test_adaptive_quiz_prioritizes_weaker_concepts(self):
        authentication_question = replace(
            QUESTIONS[1],
            question_id="TEST_AUTH",
            concept_id="1.2-C05",
            prompt="Authentication test question",
        )

        authorization_question = QUESTIONS[1]

        historical_attempts = [
            {"concept_id": "1.2-C05", "correct": False},
            {"concept_id": "1.2-C06", "correct": True},
        ]

        self.mock_load_history.return_value = historical_attempts

        with patch(
            "security_plus_engine.main.QUESTIONS",
            [authorization_question, authentication_question],
        ):
            with patch("builtins.input", side_effect=["2", "2"]):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    run_quiz(adaptive=True)

        text = output.getvalue()

        authentication_position = text.index(
            "Authentication test question"
        )

        authorization_position = text.index(
            authorization_question.prompt
        )

        self.assertLess(
            authentication_position,
            authorization_position,
        )

        self.assertIn("Score: 2/2", text)

        self.mock_save_history.assert_called_once()

        saved_history = self.mock_save_history.call_args.args[0]

        self.assertEqual(len(saved_history), 4)

        self.assertEqual(
            saved_history[-2]["question_id"],
            "TEST_AUTH",
        )

        self.assertEqual(
            saved_history[-1]["question_id"],
            "Q0002",
        )


    
    def test_adaptive_quiz_handles_empty_question_bank(self):
        with patch(
            "security_plus_engine.main.get_adaptive_question_order",
            return_value=[],
        ):
            with patch("builtins.input") as mock_input:
                with patch("sys.stdout", new_callable=StringIO) as output:
                    run_quiz(adaptive=True)

        text = output.getvalue()

        self.assertIn(
            "No validated questions are available for this quiz mode.",
            text,
        )

        mock_input.assert_not_called()
        self.mock_save_history.assert_not_called()


    
    def test_adaptive_quiz_uses_validated_questions(self):
        with patch("builtins.input", side_effect=["2", "3"]):
            with patch("sys.stdout", new_callable=StringIO) as output:
                run_quiz(adaptive=True)

        text = output.getvalue()

        self.assertIn("You have 2 questions.", text)
        self.assertIn("Score: 2/2", text)
        self.assertIn("Percentage: 100.0%", text)

        self.assertIn("1.2-C06: 1/1 correct", text)
        self.assertIn("1.4-C11: 1/1 correct", text)

        self.assertNotIn("Which protocol is commonly used", text)

        self.mock_save_history.assert_called_once()

        saved_history = self.mock_save_history.call_args.args[0]

        self.assertEqual(len(saved_history), 2)
        self.assertEqual(
            [attempt["question_id"] for attempt in saved_history],
            ["Q0002", "Q0003"],
        )
        self.assertTrue(
            all(attempt["correct"] for attempt in saved_history)
        )


    
    def setUp(self):
        self.history_patcher = patch(
            "security_plus_engine.main.load_history",
            return_value=[],
        )
        self.save_patcher = patch(
            "security_plus_engine.main.save_history",
        )

        self.mock_load_history = self.history_patcher.start()
        self.mock_save_history = self.save_patcher.start()

        self.addCleanup(self.history_patcher.stop)
        self.addCleanup(self.save_patcher.stop)


    def test_quiz_runs_without_crashing(self):
        from security_plus_engine.main import run_quiz

        simulated_answers = ["2", "2", "3"]

        with patch("builtins.input", side_effect=simulated_answers):
            with patch("sys.stdout", new_callable=StringIO) as output:
                run_quiz()

        result = output.getvalue()

        self.assertIn("=== Quiz Results ===", result)
        self.assertIn("Score: 3/3", result)
        self.assertIn("=== Domain Performance ===", result)

        self.assertIn("=== Validated Concept Performance ===", result)
        self.assertIn("1.2-C06: 1/1 correct (100.0%)", result)
        self.assertIn("1.4-C11: 1/1 correct (100.0%)", result)
        self.assertNotIn("4.1-C01:", result)

    
    def test_unmapped_concepts_are_excluded_from_report(self):
        from security_plus_engine.main import run_quiz

        simulated_answers = ["2", "2", "3"]

        with patch("builtins.input", side_effect=simulated_answers):
            with patch("sys.stdout", new_callable=StringIO) as output:
                run_quiz()

        result = output.getvalue()

        concept_report = result.split(
            "=== Validated Concept Performance ==="
        )[1]

        self.assertIn("1.2-C06:", concept_report)
        self.assertIn("1.4-C11:", concept_report)
        self.assertNotIn("4.1-C01:", concept_report)

        
    def test_quiz_saves_all_attempts(self):
        from security_plus_engine.main import run_quiz

        simulated_answers = ["2", "1", "3"]

        with patch("builtins.input", side_effect=simulated_answers):
            with patch("sys.stdout", new_callable=StringIO):
                run_quiz()

        self.mock_load_history.assert_called_once()
        self.mock_save_history.assert_called_once()

        saved_history = self.mock_save_history.call_args.args[0]

        self.assertEqual(len(saved_history), 3)

        self.assertEqual(
            [record["question_id"] for record in saved_history],
            ["Q0001", "Q0002", "Q0003"],
        )

        self.assertEqual(
            [record["correct"] for record in saved_history],
            [True, False, True],
        )

        for record in saved_history:
            self.assertIn("timestamp", record)
            self.assertIn("concept_id", record)
            self.assertIn("objective_id", record)



class TestQuestionConceptMapping(unittest.TestCase):

    def test_question_concept_mappings(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "src/security_plus_engine/data/sy0_701_objectives.json"
        )

        data = json.loads(path.read_text(encoding="utf-8"))

        valid_mappings = {
            (objective["id"], concept["concept_id"])
            for domain in data["domains"]
            for objective in domain["objectives"]
            for concept in objective["concepts"]
        }

        provisional_question_ids = {"Q0001", "Q0003"}

        for question in QUESTIONS:
            with self.subTest(question_id=question.question_id):
                if question.question_id in provisional_question_ids:
                    continue

                self.assertIn(
                    (question.objective_id, question.concept_id),
                    valid_mappings,
                    f"Invalid concept mapping for {question.question_id}",
                )


class TestConceptPerformance(unittest.TestCase):

    def test_all_correct_answers(self):
        results = calculate_concept_performance(
            QUESTIONS, [2, 2, 3]
        )

        self.assertEqual(results["1.2-C06"]["correct"], 1)
        self.assertEqual(results["1.2-C06"]["total"], 1)
        self.assertEqual(results["1.2-C06"]["accuracy"], 100.0)

    def test_incorrect_answer(self):
        results = calculate_concept_performance(
            QUESTIONS, [2, 1, 3]
        )

        self.assertEqual(results["1.2-C06"]["correct"], 0)
        self.assertEqual(results["1.2-C06"]["total"], 1)
        self.assertEqual(results["1.2-C06"]["accuracy"], 0.0)

    def test_repeated_concept(self):
        repeated_questions = [
            QUESTIONS[1],
            QUESTIONS[1],
            QUESTIONS[1],
        ]

        results = calculate_concept_performance(
            repeated_questions, [2, 1, 2]
        )

        self.assertEqual(results["1.2-C06"]["correct"], 2)
        self.assertEqual(results["1.2-C06"]["total"], 3)
        self.assertAlmostEqual(
            results["1.2-C06"]["accuracy"], 66.6667, places=3
        )

    def test_mismatched_answer_count(self):
        with self.assertRaises(ValueError):
            calculate_concept_performance(
                QUESTIONS, [2, 2]
            )

    def test_empty_quiz(self):
        results = calculate_concept_performance([], [])
        self.assertEqual(results, {})



class TestConceptValidation(unittest.TestCase):

    def test_mapped_concepts_are_recognized(self):
        valid_concepts = load_valid_concept_ids()

        self.assertIn("1.2-C01", valid_concepts)
        self.assertIn("1.2-C06", valid_concepts)
        self.assertIn("1.2-C10", valid_concepts)

    def test_unmapped_concepts_are_not_recognized(self):
        valid_concepts = load_valid_concept_ids()

        self.assertNotIn("1.4-C40", valid_concepts)
        self.assertNotIn("4.1-C01", valid_concepts)

    def test_all_mapped_concepts_are_loaded(self):
        valid_concepts = load_valid_concept_ids()

        self.assertEqual(len(valid_concepts), 122)


class TestAdaptiveQuestionSelection(unittest.TestCase):

    def test_unattempted_concepts_come_first(self):
        performance = {
            "1.2-C06": {
                "correct": 1,
                "total": 1,
                "accuracy": 100.0,
            },
        }

        selected = select_adaptive_questions(
            QUESTIONS, performance
        )

        self.assertEqual(
            [q.question_id for q in selected],
            ["Q0001", "Q0003", "Q0002"],
        )

    def test_weaker_concepts_come_first(self):
        performance = {
            "4.1-C01": {
                "correct": 1,
                "total": 4,
                "accuracy": 25.0,
            },
            "1.2-C06": {
                "correct": 4,
                "total": 4,
                "accuracy": 100.0,
            },
            "1.4-C11": {
                "correct": 2,
                "total": 4,
                "accuracy": 50.0,
            },
        }

        selected = select_adaptive_questions(
            QUESTIONS, performance
        )

        self.assertEqual(
            [q.question_id for q in selected],
            ["Q0001", "Q0003", "Q0002"],
        )

    def test_original_question_order_is_unchanged(self):
        original_ids = [q.question_id for q in QUESTIONS]

        select_adaptive_questions(QUESTIONS, {})

        self.assertEqual(
            [q.question_id for q in QUESTIONS],
            original_ids,
        )




class TestHistoricalAdaptiveOrdering(unittest.TestCase):

    def test_history_prioritizes_weaker_concepts(self):
        authentication_question = Question(
            question_id="TEST001",
            domain="1.0",
            objective_id="1.2",
            concept_id="1.2-C05",
            difficulty="foundational",
            question_type="MCQ",
            prompt="Test authentication question",
            options=["A", "B"],
            correct_answer=1,
            explanation="Test explanation",
            source="Unit test",
        )

        authorization_question = Question(
            question_id="TEST002",
            domain="1.0",
            objective_id="1.2",
            concept_id="1.2-C06",
            difficulty="foundational",
            question_type="MCQ",
            prompt="Test authorization question",
            options=["A", "B"],
            correct_answer=1,
            explanation="Test explanation",
            source="Unit test",
        )

        history = [
            {"concept_id": "1.2-C05", "correct": False},
            {"concept_id": "1.2-C05", "correct": False},
            {"concept_id": "1.2-C06", "correct": True},
            {"concept_id": "1.2-C06", "correct": True},
        ]

        selected = get_adaptive_question_order(
            [authorization_question, authentication_question],
            history,
        )

        self.assertEqual(
            [question.question_id for question in selected],
            ["TEST001", "TEST002"],
        )

    def test_unmapped_questions_are_excluded(self):
        selected = get_adaptive_question_order(
            QUESTIONS,
            [],
        )

        self.assertEqual(
            [question.question_id for question in selected],
            ["Q0002", "Q0003"],
        )



if __name__ == "__main__":
    unittest.main()
