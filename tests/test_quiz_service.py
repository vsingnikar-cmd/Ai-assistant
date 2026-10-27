"""Unit tests for quiz scoring arithmetic, schema validation, and feedback."""

import pytest
from services.quiz_service import score_quiz_submission, validate_quiz_json


def test_score_quiz_submission_perfect():
    questions = [
        {"id": 1, "type": "mcq", "question": "What is 2+2?", "correct_answer": "4"},
        {"id": 2, "type": "true_false", "question": "Python is interpreted?", "correct_answer": "True"},
    ]
    user_answers = {1: "4", 2: "True"}

    result = score_quiz_submission(questions, user_answers)
    assert result["total_questions"] == 2
    assert result["correct_count"] == 2
    assert result["percentage"] == 100.0
    assert result["passed"] is True


def test_score_quiz_submission_partial():
    questions = [
        {"id": 1, "type": "mcq", "question": "Capital of France?", "correct_answer": "Paris"},
        {"id": 2, "type": "mcq", "question": "Capital of Italy?", "correct_answer": "Rome"},
    ]
    user_answers = {1: "Paris", 2: "Milan"}

    result = score_quiz_submission(questions, user_answers)
    assert result["total_questions"] == 2
    assert result["correct_count"] == 1
    assert result["percentage"] == 50.0
    assert result["passed"] is False
    assert result["breakdown"][0]["is_correct"] is True
    assert result["breakdown"][1]["is_correct"] is False


def test_validate_quiz_json():
    valid_payload = {
        "subject": "Computer Science",
        "topic": "Algorithms",
        "difficulty": "Medium",
        "questions": [
            {
                "id": 1,
                "type": "mcq",
                "question": "What is the worst-case time complexity of QuickSort?",
                "options": ["O(N log N)", "O(N^2)", "O(N)", "O(1)"],
                "correct_answer": "O(N^2)",
                "explanation": "When the pivot chosen is consistently the smallest or largest element.",
            }
        ],
    }

    ok, validated, err = validate_quiz_json(valid_payload)
    assert ok is True
    assert validated is not None
    assert len(validated.questions) == 1

    bad_payload = {"subject": "Math"}
    ok_bad, _, _ = validate_quiz_json(bad_payload)
    assert ok_bad is False
