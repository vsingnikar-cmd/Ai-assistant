"""Unit tests for prompt classification, academic context injection, and templates."""

import pytest
from agent.prompt_processor import PromptProcessor, classify_intent
from agent.prompts import SYSTEM_BASE_INSTRUCTIONS, EXPLANATION_STYLES


def test_intent_classification():
    assert classify_intent("Can you make a practice quiz on Operating Systems?") == "quiz_generation"
    assert classify_intent("Generate exam notes for unit 2") == "notes_generation"
    assert classify_intent("I need a study planner timetable for exams") == "study_planning"
    assert classify_intent("Difference between process and thread") == "comparison"
    assert classify_intent("Give me a 2 mark answer on mutex") == "2_marks"
    assert classify_intent("Give me a 5 mark answer on deadlock prevention") == "5_marks"
    assert classify_intent("Give me a 10 marks question on paging") == "10_marks"
    assert classify_intent("According to this document on page 4", has_active_document=True) == "document_question"
    assert classify_intent("What is a binary search tree?") == "academic_question"


def test_prompt_processor_context_injection():
    processor = PromptProcessor({
        "course": "B.Tech Computer Science",
        "branch": "Data Science",
        "semester": "Semester 5",
        "preferred_language": "English",
    })

    prompt, system_inst = processor.build_chat_prompt(
        user_message="Explain Random Forest Algorithm",
        conversation_history=[
            {"role": "user", "content": "What is Decision Tree?"},
            {"role": "assistant", "content": "A decision tree is a hierarchical tree model."},
        ],
    )

    # Verify student context is injected into system instructions
    assert "B.Tech Computer Science" in system_inst
    assert "Data Science" in system_inst
    assert "Semester 5" in system_inst

    # Verify history is included in the prompt
    assert "Recent Conversation Context" in prompt
    assert "What is Decision Tree?" in prompt
    assert "Explain Random Forest Algorithm" in prompt


def test_document_prompt_grounding():
    processor = PromptProcessor()
    prompt, _ = processor.build_chat_prompt(
        user_message="What is the time complexity stated?",
        document_context="The algorithm runs in O(N log N) time.",
    )
    assert "[DOCUMENT CONTEXT START]" in prompt
    assert "O(N log N)" in prompt
