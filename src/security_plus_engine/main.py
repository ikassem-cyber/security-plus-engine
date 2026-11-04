from dataclasses import dataclass


@dataclass
class Question:
    topic: str
    prompt: str
    options: list[str]
    correct_answer: int
    explanation: str


QUESTIONS = [
    Question(
        topic="Network Security",
        prompt="Which protocol is commonly used to securely browse websites?",
        options=["FTP", "HTTPS", "Telnet", "SNMP"],
        correct_answer=2,
        explanation="HTTPS uses TLS to protect communication between a browser and a web server.",
    ),
    Question(
        topic="Authentication",
        prompt="Which security principle requires users to receive only the permissions they need?",
        options=[
            "Separation of duties",
            "Least privilege",
            "Non-repudiation",
            "Open access",
        ],
        correct_answer=2,
        explanation="Least privilege limits access rights to only what is necessary for a user's role.",
    ),
    Question(
        topic="Cryptography",
        prompt="Which cryptographic method uses the same secret key to encrypt and decrypt data?",
        options=[
            "Asymmetric encryption",
            "Hashing",
            "Symmetric encryption",
            "Digital signatures",
        ],
        correct_answer=3,
        explanation="Symmetric encryption uses the same secret key for encryption and decryption.",
    ),
]


def check_answer(question: Question, answer: int) -> bool:
    """Return True only when the answer is valid and correct."""
    if not 1 <= answer <= len(question.options):
        return False

    return answer == question.correct_answer


def run_quiz() -> None:
    score = 0

    print("\n=== Security+ Study Engine ===")
    print(f"You have {len(QUESTIONS)} questions.\n")

    for number, question in enumerate(QUESTIONS, start=1):
        print(f"Question {number}: {question.topic}")
        print(question.prompt)

        for index, option in enumerate(question.options, start=1):
            print(f"  {index}. {option}")

        while True:
            answer = input(f"Your answer (1-{len(question.options)}): ").strip()

            if answer.isdigit() and 1 <= int(answer) <= len(question.options):
                break

            print(f"Please enter a number from 1 to {len(question.options)}.")

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


if __name__ == "__main__":
    run_quiz()


