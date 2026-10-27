"""Quiz Processing and Evaluation Service.

Validates generated quiz schemas and computes evaluation scores deterministically
in Python without asking the LLM to perform arithmetic.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError


class QuizQuestionModel(BaseModel):
    """Schema for individual question validation."""
    id: int
    type: str = Field(default="mcq", description="mcq, true_false, or short")
    question: str
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    explanation: Optional[str] = ""


class QuizPayloadModel(BaseModel):
    """Schema for complete quiz payload validation."""
    subject: str
    topic: str
    difficulty: str = "Medium"
    questions: List[QuizQuestionModel]


def validate_quiz_json(raw_json: Dict[str, Any]) -> tuple[bool, Optional[QuizPayloadModel], str]:
    """Validate model-generated quiz against strict schema."""
    if not isinstance(raw_json, dict):
        return False, None, "Quiz payload must be a JSON object."
    try:
        validated = QuizPayloadModel(**raw_json)
        if not validated.questions:
            return False, None, "Quiz must contain at least one question."
        return True, validated, ""
    except ValidationError as e:
        return False, None, f"Quiz validation error: {str(e)}"


def score_quiz_submission(
    questions: List[Dict[str, Any]],
    user_answers: Dict[int, str],
) -> Dict[str, Any]:
    """Calculate quiz score in pure Python.

    Args:
        questions: List of question dicts containing id, question, correct_answer, explanation.
        user_answers: Mapping of question id (or index) to student selected string.

    Returns:
        Dict with total, correct_count, percentage, and detailed question breakdown.
    """
    total = len(questions)
    if total == 0:
        return {
            "total_questions": 0,
            "correct_count": 0,
            "score": 0.0,
            "percentage": 0.0,
            "passed": False,
            "breakdown": [],
        }

    correct_count = 0
    breakdown = []

    for idx, q in enumerate(questions):
        q_id = q.get("id", idx + 1)
        # Try both integer key and string key, or index
        selected = user_answers.get(q_id)
        if selected is None:
            selected = user_answers.get(str(q_id), user_answers.get(idx, ""))

        correct = str(q.get("correct_answer", "")).strip()
        selected_clean = str(selected).strip()

        # Evaluation logic
        q_type = q.get("type", "mcq").lower()
        is_correct = False

        if q_type in ("mcq", "true_false"):
            # Normalize whitespace and case comparison
            is_correct = selected_clean.lower() == correct.lower()
        else:
            # Short answer: exact match or partial keyword match
            if selected_clean and (
                selected_clean.lower() == correct.lower()
                or (len(correct) > 3 and correct.lower() in selected_clean.lower())
                or (len(selected_clean) > 3 and selected_clean.lower() in correct.lower())
            ):
                is_correct = True

        if is_correct:
            correct_count += 1

        breakdown.append({
            "id": q_id,
            "question": q.get("question", ""),
            "selected_answer": selected_clean,
            "correct_answer": correct,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    percentage = round((correct_count / total) * 100.0, 1)

    return {
        "total_questions": total,
        "correct_count": correct_count,
        "score": percentage,
        "percentage": percentage,
        "passed": percentage >= 60.0,
        "breakdown": breakdown,
    }
