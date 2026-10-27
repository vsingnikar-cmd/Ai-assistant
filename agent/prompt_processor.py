"""Prompt Processing and Context Assembly Engine.

Classifies user intent, injects student academic profile context,
assembles conversation memory, and formats prompts for educational accuracy.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from agent.prompts import SYSTEM_BASE_INSTRUCTIONS, EXPLANATION_STYLES


def classify_intent(query: str, has_active_document: bool = False) -> str:
    """Identify the student's pedagogical intent from their input query.

    Categories:
    - document_question
    - notes_generation
    - quiz_generation
    - study_planning
    - comparison
    - exam_marks (2_marks, 5_marks, 10_marks)
    - academic_question
    """
    q_lower = query.lower()

    if re.search(r"\b(quiz|test|mcq|practice questions)\b", q_lower):
        return "quiz_generation"

    if re.search(r"\b(notes|exam notes|revision guide|summary of unit|cheat sheet)\b", q_lower):
        return "notes_generation"

    if re.search(r"\b(study plan|schedule|timetable|planner|exam plan)\b", q_lower):
        return "study_planning"

    if re.search(r"\b(compare|difference between|vs|versus)\b", q_lower):
        return "comparison"

    if re.search(r"\b(2 mark|2 marks|two marks|short answer)\b", q_lower):
        return "2_marks"

    if re.search(r"\b(5 mark|5 marks|five marks)\b", q_lower):
        return "5_marks"

    if re.search(r"\b(10 mark|10 marks|ten marks|long answer)\b", q_lower):
        return "10_marks"

    if has_active_document and re.search(r"\b(document|pdf|this chapter|page|according to the text)\b", q_lower):
        return "document_question"

    return "academic_question"


class PromptProcessor:
    """Processes user queries and constructs grounded pedagogical prompts."""

    def __init__(self, student_profile: Optional[Dict[str, Any]] = None):
        self.profile = student_profile or {}

    def set_student_profile(self, profile: Dict[str, Any]) -> None:
        """Update active student profile."""
        self.profile = profile

    def build_system_context(self, style_key: str = "detailed") -> str:
        """Build student-tailored system instructions."""
        course = self.profile.get("course", "Undergraduate")
        branch = self.profile.get("branch", "General")
        semester = self.profile.get("semester", "Current Semester")
        language = self.profile.get("preferred_language", "English")

        profile_context = f"""
Student Academic Level:
- Course/Degree: {course}
- Branch/Major: {branch}
- Current Semester: {semester}
- Preferred Language: {language}

Tailor all explanations, technical terminology, and mathematical depth to a student in {course} ({branch}), {semester}.
If preferred language is not English, provide technical terms in English followed by explanations in {language}.
"""
        style_instruction = EXPLANATION_STYLES.get(style_key, EXPLANATION_STYLES["detailed"])

        return f"{SYSTEM_BASE_INSTRUCTIONS}\n{profile_context}\nAnswer Format Requirement:\n{style_instruction}"

    def build_chat_prompt(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        max_history_turns: int = 5,
        document_context: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Construct prompt and system instructions with memory sliding window.

        Returns:
            Tuple of (formatted_prompt, system_instruction)
        """
        # Determine explanation style
        style_key = "detailed"
        if re.search(r"\b(simple|explain like i'm|eli5|beginner)\b", user_message.lower()):
            style_key = "simple"
        elif re.search(r"\b(2 mark|2 marks)\b", user_message.lower()):
            style_key = "2_marks"
        elif re.search(r"\b(5 mark|5 marks)\b", user_message.lower()):
            style_key = "5_marks"
        elif re.search(r"\b(10 mark|10 marks)\b", user_message.lower()):
            style_key = "10_marks"
        elif re.search(r"\b(compare|table|vs)\b", user_message.lower()):
            style_key = "comparison"
        elif re.search(r"\b(step by step|solve|numerical)\b", user_message.lower()):
            style_key = "step_by_step"

        system_instruction = self.build_system_context(style_key)

        prompt_parts = []

        # 1. Include sliding conversation history
        if conversation_history:
            recent_turns = conversation_history[-max_history_turns:]
            history_text = "Recent Conversation Context:\n"
            for turn in recent_turns:
                role = "Student" if turn.get("role") == "user" else "Assistant"
                content = turn.get("content", "").strip()
                history_text += f"{role}: {content}\n"
            prompt_parts.append(history_text)

        # 2. Document grounding context if present
        if document_context:
            prompt_parts.append(f"[DOCUMENT CONTEXT START]\n{document_context}\n[DOCUMENT CONTEXT END]")

        # 3. User's immediate query
        prompt_parts.append(f"Student: {user_message}")

        full_prompt = "\n\n".join(prompt_parts)
        return full_prompt, system_instruction
