"""Exam Notes Generator UI Component.

Synthesizes high-yield, structured semester examination revision notes,
including definitions, core concepts, diagrams, examples, and practice questions.
Enables downloading notes as Markdown.
"""

from typing import Any, Dict
import streamlit as st
from agent.academic_agent import AcademicAgent


def render_notes_generator(student_profile: Dict[str, Any], user_id: str):
    """Render the exam revision notes generator."""
    st.title("📝 Exam Notes Generator")
    st.caption("Generate exam-oriented revision notes, 2/5/10 mark answers, and practice questions.")

    agent = AcademicAgent(user_id=user_id)

    with st.form("exam_notes_form"):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input(
                "Subject *",
                placeholder="e.g. Database Management Systems, Compiler Design",
            )
            unit = st.text_input(
                "Unit / Module / Chapter",
                placeholder="e.g. Unit 3: Normalization and Functional Dependencies",
            )
            topic = st.text_input(
                "Specific Topic / Question *",
                placeholder="e.g. BCNF vs 3NF, QuickSort Algorithm, Virtual Memory",
            )

        with col2:
            format_type = st.selectbox(
                "Notes Target Format",
                [
                    "Complete Unit Study Guide (All Marks)",
                    "2-Mark Quick Revision Points",
                    "5-Mark Structured Answer with Diagram",
                    "10-Mark Comprehensive Exam Answer",
                    "Comparison Table & Analysis",
                ],
            )
            detail_level = st.select_slider(
                "Detail Level",
                options=["High-Yield Summary", "Standard Exam Depth", "Exhaustive / Detailed"],
                value="Standard Exam Depth",
            )
            syllabus_text = st.text_area(
                "Paste Syllabus Excerpt or Key Points (Optional)",
                placeholder="Paste relevant syllabus topics to customize exam alignment...",
                height=90,
            )

        submit_notes = st.form_submit_button("Generate Exam Notes", type="primary", use_container_width=True)

    if submit_notes:
        if not subject or not topic:
            st.error("Please provide both Subject and Topic.")
        else:
            with st.spinner("Synthesizing comprehensive university exam study guide..."):
                success, notes_text = agent.generate_exam_notes(
                    subject=subject,
                    unit=unit,
                    topic=topic,
                    format_type=format_type,
                    detail_level=detail_level,
                    syllabus_text=syllabus_text,
                )

                if success:
                    st.session_state.current_notes = notes_text
                    st.session_state.current_notes_topic = topic
                    st.session_state.current_notes_subject = subject
                else:
                    st.error(notes_text)

    # Display generated notes
    if "current_notes" in st.session_state and st.session_state.current_notes:
        st.markdown("---")
        st.subheader("📖 Generated Study Guide")

        col_d1, col_d2 = st.columns([4, 1])
        with col_d2:
            filename = f"{st.session_state.get('current_notes_subject', 'Exam')}_{st.session_state.get('current_notes_topic', 'Notes')}.md".replace(" ", "_")
            st.download_button(
                label="📥 Download (.md)",
                data=st.session_state.current_notes,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown(st.session_state.current_notes)
