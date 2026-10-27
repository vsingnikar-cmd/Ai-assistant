"""Unit tests for memory module, sliding context, and repositories."""

import pytest
from unittest.mock import MagicMock
from agent.prompt_processor import PromptProcessor
from database.repositories import ConversationRepository, MessageRepository


def test_sliding_window_memory():
    processor = PromptProcessor()
    # Create 10 turns of history
    long_history = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message turn {i}"}
        for i in range(10)
    ]

    # With max_history_turns=4, only turns 6, 7, 8, 9 should be included
    prompt, _ = processor.build_chat_prompt(
        user_message="Summarize our chat",
        conversation_history=long_history,
        max_history_turns=4,
    )

    assert "Message turn 9" in prompt
    assert "Message turn 6" in prompt
    assert "Message turn 2" not in prompt


def test_conversation_repo_with_mock():
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table

    repo = ConversationRepository(client=mock_client)
    mock_table.insert.return_value.execute.return_value.data = [{"id": "conv-123"}]

    conv_id = repo.create_conversation("user-1", "DBMS Session", "DBMS")
    assert conv_id == "conv-123"
    mock_client.table.assert_called_with("conversations")
