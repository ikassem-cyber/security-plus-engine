import argparse
from io import StringIO
from unittest.mock import patch
from dataclasses import dataclass
import json
from pathlib import Path

from security_plus_engine.history import (
    create_attempt_record,
    load_history,
    save_history,
    calculate_historical_concept_performance,
)

@dataclass
class Question:
    question_id: str
    domain: str
    objective_id: str
    concept_id: str
    difficulty: str
    question_type: str
    prompt: str
    options: list[str]
    correct_answer: int
    explanation: str
    source: str


DOMAINS = {
    "1.0": {
        "name": "General Security Concepts",
        "weight": 12,
    },
    "2.0": {
        "name": "Threats, Vulnerabilities, and Mitigations",
        "weight": 22,
    },
    "3.0": {
        "name": "Security Architecture",
        "weight": 18,
    },
    "4.0": {
        "name": "Security Operations",
        "weight": 28,
    },
    "5.0": {
        "name": "Security Program Management and Oversight",
        "weight": 20,
    },
}


QUESTIONS = [
    Question(
        question_id="Q0001",
        domain="4.0",
        objective_id="4.1",
        concept_id="4.1-C01",
        difficulty="foundational",
        question_type="MCQ",
        prompt="Which protocol is commonly used to securely browse websites?",
        options=["FTP", "HTTPS", "Telnet", "SNMP"],
        correct_answer=2,
        explanation="HTTPS uses TLS to protect communication between a browser and a web server.",
        source="Original sample question",
    ),
    Question(
        question_id="Q0002",
        domain="1.0",
        objective_id="1.2",
        concept_id="1.2-C06",
        difficulty="foundational",
        question_type="MCQ",
        prompt="Which security principle requires users to receive only the permissions they need?",
        options=[
            "Separation of duties",
            "Least privilege",
            "Non-repudiation",
            "Open access",
        ],
        correct_answer=2,
        explanation="Least privilege limits access rights to only what is necessary for a user's role.",
        source="Original sample question",
    ),
    Question(
        question_id="Q0003",
        domain="1.0",
        objective_id="1.4",
        concept_id="1.4-C01",
        difficulty="foundational",
        question_type="MCQ",
        prompt="Which cryptographic method uses the same secret key to encrypt and decrypt data?",
        options=[
            "Asymmetric encryption",
            "Hashing",
            "Symmetric encryption",
            "Digital signatures",
        ],
        correct_answer=3,
        explanation="Symmetric encryption uses the same secret key for encryption and decryption.",
        source="Original sample question",
    ),
]

def calculate_domain_performance(
    questions: list[Question],
    user_answers: list[int],
) -> dict:
    """Calculate quiz accuracy for each exam domain."""

    performance = {
        domain_id: {
            "correct": 0,
            "total": 0,
            "accuracy": 0.0,
        }
        for domain_id in DOMAINS
    }

    for question, answer in zip(questions, user_answers):
        performance[question.domain]["total"] += 1

        if check_answer(question, answer):
            performance[question.domain]["correct"] += 1

    for domain_data in performance.values():
        if domain_data["total"] > 0:
            domain_data["accuracy"] = (
                domain_data["correct"] / domain_data["total"]
            ) * 100

    return performance


def load_valid_concept_ids() -> set[str]:
    """Load mapped concept IDs from the SY0-701 objectives database."""

    path = (
        Path(__file__).resolve().parent
        / "data"
        / "sy0_701_objectives.json"
    )

    data = json.loads(path.read_text(encoding="utf-8"))

    return {
        concept["concept_id"]
        for domain in data["domains"]
        for objective in domain["objectives"]
        for concept in objective["concepts"]
    }


def calculate_concept_performance(
    questions: list[Question],
    user_answers: list[int],
) -> dict:
    """Calculate quiz accuracy for each attempted concept."""

    if len(questions) != len(user_answers):
        raise ValueError(
            "Questions and answers must have matching lengths."
        )

    performance = {}

    for question, answer in zip(questions, user_answers):
        concept_id = question.concept_id

        if concept_id not in performance:
            performance[concept_id] = {
                "correct": 0,
                "total": 0,
                "accuracy": 0.0,
            }

        performance[concept_id]["total"] += 1

        if check_answer(question, answer):
            performance[concept_id]["correct"] += 1

    for results in performance.values():
        results["accuracy"] = (
            results["correct"] / results["total"]
        ) * 100

    return performance



def select_adaptive_questions(
    questions: list[Question],
    concept_performance: dict,
) -> list[Question]:
    """Prioritize questions from weaker concepts."""

    def priority(question: Question) -> tuple:
        results = concept_performance.get(question.concept_id)

        if results is None or results["total"] == 0:
            return (0, 0)

        return (1, results["accuracy"])

    return sorted(questions, key=priority)



def get_adaptive_question_order(
    questions: list[Question],
    history: list[dict],
) -> list[Question]:
    """Order questions using historical concept performance."""

    valid_concept_ids = load_valid_concept_ids()

    valid_questions = [
        question
        for question in questions
        if question.concept_id in valid_concept_ids
        and question.concept_id.startswith(
            f"{question.objective_id}-"
        )
    ]

    performance = calculate_historical_concept_performance(
        history,
        valid_concept_ids,
    )

    return select_adaptive_questions(
        valid_questions,
        performance,
    )


def check_answer(question: Question, answer: int) -> bool:
    """Return True only when the answer is valid and correct."""
    if not 1 <= answer <= len(question.options):
        return False

    return answer == question.correct_answer


def run_quiz(adaptive: bool = False) -> None:
    score = 0
    user_answers = []
    session_attempts = []

    
    history = load_history()

    if adaptive:
        quiz_questions = get_adaptive_question_order(
            QUESTIONS,
            history,
        )
    else:
        quiz_questions = QUESTIONS

    if not quiz_questions:
        print("No validated questions are available for this quiz mode.")
        return


    print("\n=== Security+ SY0-701 Study Engine ===")
    print(f"You have {len(quiz_questions)} questions.\n")

    for number, question in enumerate(quiz_questions, start=1):
        domain_name = DOMAINS[question.domain]["name"]

        print(f"Question {number}: {domain_name}")
        print(f"Objective: {question.objective_id}")
        print(f"Concept: {question.concept_id}")
        print(question.prompt)

        for index, option in enumerate(question.options, start=1):
            print(f"  {index}. {option}")

        while True:
            answer = input(f"Your answer (1-{len(question.options)}): ").strip()

            if answer.isdigit() and 1 <= int(answer) <= len(question.options):
                break

            print(f"Please enter a number from 1 to {len(question.options)}.")

        user_answers.append(int(answer))
        session_attempts.append(
            create_attempt_record(
            question,
            answer=int(answer),
            correct=check_answer(question, int(answer)),
            )
        )

        if check_answer(question, int(answer)):
            print("Correct!")
            score += 1
        else:
            correct = question.options[question.correct_answer - 1]
            print(f"Incorrect. Correct answer: {correct}")

        print(f"Explanation: {question.explanation}\n")

    history.extend(session_attempts)
    save_history(history)
    percentage = score / len(quiz_questions) * 100

    print("=== Quiz Results ===")
    print(f"Score: {score}/{len(quiz_questions)}")
    print(f"Percentage: {percentage:.1f}%")


    print("\n=== Domain Performance ===")

    domain_results = calculate_domain_performance(quiz_questions, user_answers)
    
    for domain_id, results in domain_results.items():
            domain_name = DOMAINS[domain_id]["name"]
    
            if results["total"] == 0:
                print(f"{domain_name}: Not attempted")
            else:
                print(
                    f"{domain_name}: "
                    f"{results['correct']}/{results['total']} correct "
                    f"({results['accuracy']:.1f}%)"
                )

    
    print("\n=== Validated Concept Performance ===")

    
    validated_questions = []
    validated_answers = []

    valid_concept_ids = load_valid_concept_ids()

    for question, answer in zip(quiz_questions, user_answers):
        if question.concept_id in valid_concept_ids:
            validated_questions.append(question)
            validated_answers.append(answer)


    concept_results = calculate_concept_performance(
        validated_questions,
        validated_answers,
    )

    if not concept_results:
        print("No validated concepts attempted.")
    else:
        for concept_id, results in sorted(concept_results.items()):
            print(
                f"{concept_id}: "
                f"{results['correct']}/{results['total']} correct "
                f"({results['accuracy']:.1f}%)"
            )


    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CompTIA Security+ SY0-701 Study Engine"
    )

    parser.add_argument(
        "--adaptive",
        action="store_true",
        help="Use historical performance to prioritize weaker concepts",
    )

    args = parser.parse_args()

    run_quiz(adaptive=args.adaptive)

