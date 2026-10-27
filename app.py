"""AI Student Assistant Agent - Main Application Entry Point.

Demonstrates all seven core components of an AI Agent:
1. User Interface (Streamlit UI with sidebar navigation)
2. Prompt Processing (agent.prompt_processor)
3. Large Language Model (Google Gemini API via google-genai)
4. Memory Module (short-term session state & Supabase PostgreSQL)
5. Tool Integration (11 internal Python tools)
6. Response Generation (structured cards, Markdown, citations)
7. Deployment Platform (Streamlit & Cloud)

Local Run Command: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

from auth.session import (
    init_session_state,
    get_auth_state,
    AuthState,
    clear_auth_session,
)
from auth.login import render_login
from auth.register import render_register, render_complete_profile
from auth.auth_service import AuthService
from database.supabase_client import is_supabase_configured, get_supabase_credentials
from agent.gemini_client import GeminiClient

from components.dashboard import render_dashboard
from components.chat import render_chat
from components.pdf_assistant import render_pdf_assistant
from components.notes_generator import render_notes_generator
from components.quiz_generator import render_quiz_generator
from components.study_planner import render_study_planner
from components.profile import render_profile
from database.repositories import QuizAttemptRepository, ConversationRepository

# Configure Streamlit page layout
st.set_page_config(
    page_title="AI Student Assistant Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_settings_page():
    """Render application settings and environment verification."""
    st.title("⚙️ System Settings & API Configuration")
    st.caption("Verify Gemini AI and Supabase database integrations.")

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    supa_url, supa_key = get_supabase_credentials()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 Google Gemini LLM")
        if gemini_key:
            st.success(f"✅ Gemini API Key detected (Configured Model: {gemini_model})")
        else:
            st.warning("⚠️ GEMINI_API_KEY is not set in environment or .env file.")

        client = GeminiClient()
        if client.is_configured():
            st.info("LLM Client initialized and ready.")
        else:
            st.error("LLM Client is not ready. Verify API credentials.")

    with col2:
        st.subheader("🗄️ Supabase PostgreSQL & Auth")
        if supa_url and supa_key:
            st.success(f"✅ Supabase configured (URL: {supa_url[:24]}...)")
        else:
            st.warning("⚠️ SUPABASE_URL or SUPABASE_ANON_KEY missing in .env file.")

    st.markdown("---")
    st.subheader("📚 Database Schema Verification")
    st.markdown(
        """
        To initialize the database tables with Row-Level Security, execute the script located at:
        `database/schema.sql` in your Supabase SQL Editor.
        """
    )
    with st.expander("View database/schema.sql snippet"):
        try:
            with open("database/schema.sql", "r") as f:
                st.code(f.read(), language="sql")
        except Exception:
            st.caption("schema.sql available in workspace.")


def render_history_page(user_id: str):
    """Render student study history and past quiz logs."""
    st.title("📜 My Study History")
    st.caption("Review your past quiz scores, test attempts, and saved conversations.")

    tab_quizzes, tab_chats = st.tabs(["🎯 Past Quiz Attempts", "💬 Saved Conversations"])

    with tab_quizzes:
        quiz_repo = QuizAttemptRepository()
        attempts = quiz_repo.get_user_attempts(user_id, limit=30)
        if not attempts:
            st.info("No past quiz attempts found.")
        else:
            for att in attempts:
                score = att.get("score", 0)
                badge_color = "#22c55e" if score >= 70 else ("#eab308" if score >= 50 else "#ef4444")
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #38bdf8;">{att.get('topic')} ({att.get('subject')})</h4>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                                📅 {att.get('created_at', '')[:10]} &nbsp;|&nbsp; Difficulty: {att.get('difficulty')} &nbsp;|&nbsp; Questions: {att.get('total_questions')}
                            </p>
                        </div>
                        <span style="background: {badge_color}; color: white; padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 1.1rem;">
                            {score}%
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_chats:
        conv_repo = ConversationRepository()
        convs = conv_repo.get_user_conversations(user_id)
        if not convs:
            st.info("No saved chat conversations found.")
        else:
            for c in convs:
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #f8fafc;">💬 {c.get('title')}</h4>
                        <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 0.8rem;">
                            Subject: {c.get('subject') or 'General'} &nbsp;|&nbsp; Last active: {c.get('updated_at', '')[:10]}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def main():
    """Main application orchestrator."""
    init_session_state()

    auth_state = get_auth_state()

    # 1. Check if Supabase Service is available
    if auth_state == AuthState.SERVICE_UNAVAILABLE:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 40px; margin-bottom: 24px;">
                <h1 style="font-size: 2.2rem; font-weight: 800; color: #f8fafc;">AI Student Assistant Agent</h1>
                <p style="color: #94a3b8;">Central Academic Architecture Setup</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.warning(
            "⚠️ **Supabase Database & Authentication Configuration Required**\n\n"
            "The application requires Supabase connection details to ensure row-level security and student profile persistence.\n\n"
            "Please create a `.env` file (copied from `.env.example`) or configure environment variables with:\n"
            "- `SUPABASE_URL`\n"
            "- `SUPABASE_ANON_KEY`\n"
            "- `GEMINI_API_KEY`"
        )
        with st.expander("Quick-Start Setup Guide", expanded=True):
            st.markdown(
                """
                1. Create a free project at [Supabase](https://supabase.com).
                2. In Project Settings > API, copy the Project URL and anon public key.
                3. Go to SQL Editor in Supabase, paste and run the contents of `database/schema.sql`.
                4. Obtain a Gemini API Key from Google AI Studio.
                5. Populate `.env`:
                ```bash
                GEMINI_API_KEY="your_gemini_api_key"
                GEMINI_MODEL="gemini-2.5-flash"
                SUPABASE_URL="https://your-project.supabase.co"
                SUPABASE_ANON_KEY="your_anon_key"
                ```
                """
            )
        return

    # 2. Handle Unauthenticated / Session Expired
    if auth_state in (AuthState.UNAUTHENTICATED, AuthState.SESSION_EXPIRED):
        auth_view = st.session_state.get("auth_view", "login")
        if auth_view == "register":
            render_register()
        else:
            render_login()
        return

    # 3. Handle Incomplete Student Profile
    if auth_state == AuthState.PROFILE_INCOMPLETE:
        user_id = st.session_state.get("user_id")
        user_email = st.session_state.get("user_email", "")
        render_complete_profile(user_id=user_id, email=user_email)
        return

    # 4. Authenticated Student Dashboard & Sidebar Navigation
    user_id = st.session_state.get("user_id")
    student_profile = st.session_state.get("student_profile", {})

    # Sidebar Navigation (Section 8)
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0; text-align: center;">
                <h2 style="margin: 0; font-size: 1.3rem; color: #38bdf8;">🎓 AI Student Assistant</h2>
                <span style="font-size: 0.8rem; color: #94a3b8;">Academic Mentor Agent</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        nav_options = [
            "Dashboard",
            "AI Academic Chat",
            "PDF Study Assistant",
            "Exam Notes Generator",
            "Quiz Generator",
            "Study Planner",
            "My Study History",
            "My Profile",
            "Settings",
        ]

        current_nav = st.session_state.get("current_page", "Dashboard")
        selected_page = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index(current_nav) if current_nav in nav_options else 0,
            label_visibility="collapsed",
        )
        st.session_state.current_page = selected_page

        st.markdown("---")
        # Student Mini Profile in Sidebar
        st.caption(f"Logged in as: **{student_profile.get('full_name', 'Student')}**")
        st.caption(f"Course: {student_profile.get('course', '')} ({student_profile.get('branch', '')})")

        # Logout Button (Section 6.5)
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            auth_svc = AuthService()
            auth_svc.sign_out()
            clear_auth_session()
            st.rerun()

    # Page Router
    def handle_navigate(target_page: str):
        st.session_state.current_page = target_page
        st.rerun()

    if selected_page == "Dashboard":
        render_dashboard(student_profile, user_id, on_navigate=handle_navigate)
    elif selected_page == "AI Academic Chat":
        render_chat(student_profile, user_id)
    elif selected_page == "PDF Study Assistant":
        render_pdf_assistant(student_profile, user_id)
    elif selected_page == "Exam Notes Generator":
        render_notes_generator(student_profile, user_id)
    elif selected_page == "Quiz Generator":
        render_quiz_generator(student_profile, user_id)
    elif selected_page == "Study Planner":
        render_study_planner(student_profile, user_id)
    elif selected_page == "My Study History":
        render_history_page(user_id)
    elif selected_page == "My Profile":
        render_profile(student_profile, user_id)
    elif selected_page == "Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
