from dataclasses import dataclass


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
        concept_id="1.2-C01",
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


def check_answer(question: Question, answer: int) -> bool:
    """Return True only when the answer is valid and correct."""
    if not 1 <= answer <= len(question.options):
        return False

    return answer == question.correct_answer


def run_quiz() -> None:
    score = 0
    user_answers = []
    print("\n=== Security+ SY0-701 Study Engine ===")
    print(f"You have {len(QUESTIONS)} questions.\n")

    for number, question in enumerate(QUESTIONS, start=1):
        domain_name = DOMAINS[question.domain]["name"]

        print(f"Question {number}: {domain_name}")
        print(f"Topic: {question.topic}")
        print(question.prompt)

        for index, option in enumerate(question.options, start=1):
            print(f"  {index}. {option}")

        while True:
            answer = input(f"Your answer (1-{len(question.options)}): ").strip()

            if answer.isdigit() and 1 <= int(answer) <= len(question.options):
                break

            print(f"Please enter a number from 1 to {len(question.options)}.")

        user_answers.append(int(answer))

        if check_answer(question, int(answer)):
            print("Correct!")
            score += 1
        else:
            correct = question.options[question.correct_answer - 1]
            print(f"Incorrect. Correct answer: {correct}")

        print(f"Explanation: {question.explanation}\n")

    percentage = score / len(QUESTIONS) * 100

    print("=== Quiz Results ===")
    print(f"Score: {score}/{len(QUESTIONS)}")
    print(f"Percentage: {percentage:.1f}%")


    print("\n=== Domain Performance ===")

    domain_results = calculate_domain_performance(QUESTIONS, user_answers)

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

if __name__ == "__main__":
    run_quiz()
