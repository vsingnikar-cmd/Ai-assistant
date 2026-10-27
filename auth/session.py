"""Session Guard and Authentication State Management.

Supports rigorous states:
- UNAUTHENTICATED
- AUTHENTICATED
- PROFILE_INCOMPLETE
- EMAIL_VERIFICATION_PENDING
- SESSION_EXPIRED
- SERVICE_UNAVAILABLE
"""

from enum import Enum
from typing import Any, Dict, Optional
import streamlit as st
from database.supabase_client import is_supabase_configured, get_supabase_client
from database.repositories import ProfileRepository


class AuthState(Enum):
    UNAUTHENTICATED = "unauthenticated"
    AUTHENTICATED = "authenticated"
    PROFILE_INCOMPLETE = "profile_incomplete"
    EMAIL_VERIFICATION_PENDING = "email_verification_pending"
    SESSION_EXPIRED = "session_expired"
    SERVICE_UNAVAILABLE = "service_unavailable"


def init_session_state() -> None:
    """Initialize necessary Streamlit session state keys if not set."""
    defaults = {
        "user_id": None,
        "user_email": None,
        "student_profile": None,
        "auth_token": None,
        "current_page": "Dashboard",
        "chat_history": [],
        "active_conversation_id": None,
        "active_pdf_name": None,
        "active_pdf_chunks": [],
        "current_quiz": None,
        "quiz_user_answers": {},
        "quiz_submitted": False,
        "quiz_result": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_auth_state() -> AuthState:
    """Evaluate current authentication state against Supabase and database profile.

    Does NOT rely on a simple boolean flag; validates session and profile completeness.
    """
    if not is_supabase_configured():
        return AuthState.SERVICE_UNAVAILABLE

    client = get_supabase_client()
    if not client:
        return AuthState.SERVICE_UNAVAILABLE

    # Check if a user ID is held in session
    user_id = st.session_state.get("user_id")
    if not user_id:
        return AuthState.UNAUTHENTICATED

    # Verify session with client
    try:
        session = client.auth.get_session()
        if not session or not session.user or session.user.id != user_id:
            # Session expired or mismatch
            clear_auth_session()
            return AuthState.SESSION_EXPIRED
    except Exception:
        # If network error or unable to check session
        pass

    # Check profile completeness
    profile = st.session_state.get("student_profile")
    if not profile or not profile.get("profile_completed"):
        # Fetch directly from repository to verify
        repo = ProfileRepository()
        db_profile = repo.get_profile(user_id)
        if not db_profile or not db_profile.get("profile_completed"):
            return AuthState.PROFILE_INCOMPLETE
        st.session_state.student_profile = db_profile

    return AuthState.AUTHENTICATED


def set_auth_session(user_id: str, email: str, session_data: Optional[Any] = None) -> None:
    """Store authenticated user session."""
    st.session_state.user_id = user_id
    st.session_state.user_email = email
    st.session_state.auth_token = getattr(session_data, "access_token", None) if session_data else None

    # Load profile
    repo = ProfileRepository()
    profile = repo.get_profile(user_id)
    st.session_state.student_profile = profile


def clear_auth_session() -> None:
    """Clear all authentication and user data from session state upon logout."""
    keys_to_clear = [
        "user_id",
        "user_email",
        "student_profile",
        "auth_token",
        "chat_history",
        "active_conversation_id",
        "active_pdf_name",
        "active_pdf_chunks",
        "current_quiz",
        "quiz_user_answers",
        "quiz_submitted",
        "quiz_result",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None
    st.session_state.chat_history = []
    st.session_state.active_pdf_chunks = []
    st.session_state.quiz_user_answers = {}
    st.session_state.current_page = "Dashboard"
