"""Study Plan Generation and Scheduling Service.

Validates examination timelines, distributes topic workloads evenly,
and manages task scheduling.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError


class StudyTaskSchema(BaseModel):
    task_title: str
    subject: str
    description: Optional[str] = ""
    due_date: str
    estimated_duration_minutes: int = Field(default=60, ge=15, le=360)
    priority: str = Field(default="Medium")


class StudyPlanSchema(BaseModel):
    plan_title: str
    subject: str
    start_date: str
    end_date: str
    total_estimated_hours: Optional[float] = 0.0
    strategy_overview: Optional[str] = ""
    tasks: List[StudyTaskSchema]


def validate_study_plan_json(raw_json: Dict[str, Any]) -> tuple[bool, Optional[StudyPlanSchema], str]:
    """Validate model output against study plan schema."""
    if not isinstance(raw_json, dict):
        return False, None, "Study plan payload must be a JSON object."
    try:
        validated = StudyPlanSchema(**raw_json)
        if not validated.tasks:
            return False, None, "Study plan must contain at least one task."
        return True, validated, ""
    except ValidationError as e:
        return False, None, f"Study plan validation error: {str(e)}"


def calculate_available_days(start_date: date, end_date: date) -> int:
    """Calculate the number of study days between start and exam date."""
    delta = (end_date - start_date).days
    return max(1, delta)
