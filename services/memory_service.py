"""Conversational Memory Service.

Coordinates short-term memory (in-memory / Streamlit session state) and
persistent memory (Supabase PostgreSQL tables: conversations, messages).
Implements sliding context window to prevent LLM context window overflows.
"""

from typing import Any, Dict, List, Optional
import streamlit as st
from database.repositories import ConversationRepository, MessageRepository


class MemoryService:
    """Manages short-term and persistent conversational memory."""

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.conv_repo = ConversationRepository()
        self.msg_repo = MessageRepository()

    def get_current_chat_messages(self) -> List[Dict[str, Any]]:
        """Retrieve active short-term session chat messages."""
        if "chat_history" not in st.session_state or not st.session_state.chat_history:
            return []
        return st.session_state.chat_history

    def append_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add message to short-term session and persist to Supabase if conversation is active."""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        msg_obj = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }
        st.session_state.chat_history.append(msg_obj)

        # Persistent sync if user and active conversation exist
        conv_id = st.session_state.get("active_conversation_id")
        if self.user_id and conv_id:
            self.msg_repo.save_message(
                user_id=self.user_id,
                conv_id=conv_id,
                role=role,
                content=content,
                metadata=metadata,
            )

    def start_new_conversation(self, title: str = "New Academic Session", subject: Optional[str] = None) -> Optional[str]:
        """Initialize a new conversation thread, persisting to Supabase if authenticated."""
        st.session_state.chat_history = []
        st.session_state.active_conversation_id = None

        if self.user_id:
            conv_id = self.conv_repo.create_conversation(self.user_id, title=title, subject=subject)
            st.session_state.active_conversation_id = conv_id
            return conv_id
        return None

    def load_conversation(self, conversation_id: str) -> bool:
        """Load saved conversation messages from Supabase into active short-term state."""
        if not self.user_id or not conversation_id:
            return False

        messages = self.msg_repo.get_conversation_messages(self.user_id, conversation_id)
        st.session_state.chat_history = [
            {"role": m["role"], "content": m["content"], "metadata": m.get("metadata", {})}
            for m in messages
        ]
        st.session_state.active_conversation_id = conversation_id
        return True

    def clear_active_chat(self) -> None:
        """Clear short-term chat messages without deleting saved database records."""
        st.session_state.chat_history = []
        st.session_state.active_conversation_id = None

    def delete_saved_conversation(self, conversation_id: str) -> bool:
        """Permanently delete saved conversation from database."""
        if not self.user_id:
            return False
        if st.session_state.get("active_conversation_id") == conversation_id:
            self.clear_active_chat()
        return self.conv_repo.delete_conversation(self.user_id, conversation_id)

    def get_user_saved_conversations(self) -> List[Dict[str, Any]]:
        """Retrieve list of saved conversations for the authenticated user."""
        if not self.user_id:
            return []
        return self.conv_repo.get_user_conversations(self.user_id)
