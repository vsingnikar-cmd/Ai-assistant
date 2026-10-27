"""AI Academic Chatbot UI Component.

Provides pedagogical conversational assistant with customizable explanation formats
(Simple, Detailed, 2-Mark, 5-Mark, 10-Mark, Comparison Table), memory retention,
and clear/new session controls.
"""

from typing import Any, Dict, Optional
import streamlit as st
from agent.academic_agent import AcademicAgent
from services.memory_service import MemoryService


def render_chat(student_profile: Dict[str, Any], user_id: str):
    """Render interactive academic chat interface."""
    st.title("💬 AI Academic Chat")
    st.caption("Ask academic concepts, semester exam answers, algorithm walkthroughs, and comparisons.")

    memory_service = MemoryService(user_id=user_id)
    agent = AcademicAgent(user_id=user_id)

    # Top Toolbar
    col_t1, col_t2, col_t3, col_t4 = st.columns([3, 2, 2, 2])
    with col_t1:
        subject_filter = st.text_input("Active Subject (Optional)", placeholder="e.g. Operating Systems")
    with col_t2:
        format_selector = st.selectbox(
            "Desired Response Style",
            ["Detailed Academic", "Simple / Beginner", "2-Mark Short Answer", "5-Mark Exam Answer", "10-Mark Long Answer", "Comparison Table", "Step-by-Step Solution"],
            index=0,
        )
    with col_t3:
        if st.button("➕ New Chat Session", use_container_width=True):
            conv_id = memory_service.start_new_conversation(
                title=f"{subject_filter or 'Academic'} Session",
                subject=subject_filter,
            )
            st.success("New conversation started!")
            st.rerun()
    with col_t4:
        if st.button("🧹 Clear Chat", use_container_width=True):
            memory_service.clear_active_chat()
            st.info("Current conversation cleared.")
            st.rerun()

    st.markdown("---")

    # Render Chat History
    chat_history = memory_service.get_current_chat_messages()

    if not chat_history:
        st.markdown(
            """
            <div style="background: #1e293b; border: 1px dashed #475569; border-radius: 12px; padding: 32px; text-align: center; margin: 20px 0;">
                <h3 style="color: #94a3b8; font-weight: 500;">No messages in this session yet</h3>
                <p style="color: #64748b; font-size: 0.95rem;">
                    Try asking: <em>"Explain Process Synchronization and Semaphores in OS"</em> or <em>"Give me a 5-mark answer on ACID properties in DBMS"</em>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            with st.chat_message("user" if role == "user" else "assistant"):
                st.markdown(content)

    # Chat Input Box
    if user_input := st.chat_input("Ask any academic question or request an exam-format answer..."):
        # Format query according to selected style
        styled_query = user_input
        if format_selector == "2-Mark Short Answer" and "2 mark" not in user_input.lower():
            styled_query = f"{user_input} (Give me a concise 2-mark answer)"
        elif format_selector == "5-Mark Exam Answer" and "5 mark" not in user_input.lower():
            styled_query = f"{user_input} (Give me a structured 5-mark exam answer)"
        elif format_selector == "10-Mark Long Answer" and "10 mark" not in user_input.lower():
            styled_query = f"{user_input} (Give me an in-depth 10-mark comprehensive answer with diagrams and examples)"
        elif format_selector == "Comparison Table" and "table" not in user_input.lower():
            styled_query = f"{user_input} (Format as a comparison table)"
        elif format_selector == "Simple / Beginner" and "simple" not in user_input.lower():
            styled_query = f"{user_input} (Explain in simple language with an analogy)"

        # 1. Display and save user message
        memory_service.append_message("user", styled_query)
        with st.chat_message("user"):
            st.markdown(styled_query)

        # 2. Generate response via Academic Agent
        with st.chat_message("assistant"):
            with st.spinner("Analyzing curriculum and formulating academic response..."):
                # Pass recent conversation context
                success, response_text = agent.answer_academic_query(
                    query=styled_query,
                    conversation_history=chat_history,
                )
                if success:
                    st.markdown(response_text)
                    memory_service.append_message("assistant", response_text)
                else:
                    st.error(response_text)
