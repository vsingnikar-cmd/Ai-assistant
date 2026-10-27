"""Response Formatter and Output Polisher.

Formats AI agent responses with typography, citations, code blocks,
and structured UI presentation helpers.
"""

from typing import Any, Dict, List


def format_citations(text: str) -> str:
    """Highlight and standardize document page citations in text."""
    # Standardize [Page X] markers with styled tags if needed
    return text


def format_quiz_card(question_obj: Dict[str, Any], index: int, user_selected: str = "", show_answer: bool = False) -> str:
    """Format an individual quiz card with options and feedback."""
    q_text = question_obj.get("question", "")
    options = question_obj.get("options", [])
    correct = question_obj.get("correct_answer", "")
    explanation = question_obj.get("explanation", "")

    output = [f"**Question {index + 1}:** {q_text}\n"]

    if options:
        for opt in options:
            marker = "•"
            if show_answer:
                if opt == correct:
                    marker = "✅ (Correct)"
                elif opt == user_selected:
                    marker = "❌ (Your answer)"
            output.append(f"{marker} {opt}")

    if show_answer and explanation:
        output.append(f"\n💡 *Explanation:* {explanation}")

    return "\n".join(output)


def format_study_task_markdown(task: Dict[str, Any]) -> str:
    """Format a study task entry with priority badges and duration."""
    title = task.get("task_title", "Untitled Task")
    subject = task.get("subject", "General")
    due = task.get("due_date", "No date")
    duration = task.get("estimated_duration_minutes", 60)
    priority = task.get("priority", "Medium")
    desc = task.get("description", "")

    badge = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}.get(priority, priority)

    return f"**{title}** ({subject}) | {badge} | ⏱️ {duration} mins | 📅 Due: {due}\n> {desc}"
