# Security+ Study Engine

A Python-based study application designed to help learners prepare for the CompTIA Security+ certification.

## Current Features

- Interactive multiple-choice quizzes
- Questions organized by cybersecurity topic
- Automatic answer validation
- Input validation
- Explanations after each answer
- Automatic score calculation
- Automated unit tests

## Technologies

- Python 3.10+
- Git and GitHub
- Python unittest
- Setuptools

## Installation

Clone the repository:

```bash
git clone https://github.com/ikassem-cyber/security-plus-engine.git
cd security-plus-engine

```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project:

```bash
python -m pip install -e .
```

## Run the Application

```bash
python -m security_plus_engine.main
```

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## Project Status

Early development. The current version includes a working interactive quiz with a small sample question bank and automated tests.



