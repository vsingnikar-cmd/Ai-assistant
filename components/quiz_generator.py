"""Quiz Generator and Auto-Grader UI Component.

Generates custom practice tests and quizzes, receives student responses,
calculates evaluation deterministically in Python, reveals explanations,
and logs the attempt into Supabase.
"""

from typing import Any, Dict
import streamlit as st
from agent.academic_agent import AcademicAgent


def render_quiz_generator(student_profile: Dict[str, Any], user_id: str):
    """Render interactive practice test and quiz interface."""
    st.title("🎯 Quiz & Practice Test Generator")
    st.caption("Generate subject-specific quizzes to test your exam readiness with instant feedback.")

    agent = AcademicAgent(user_id=user_id)

    # Quiz Configuration Form
    with st.expander("⚙️ Configure New Practice Quiz", expanded=st.session_state.get("current_quiz") is None):
        with st.form("quiz_config_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                subject = st.text_input("Subject *", placeholder="e.g. Computer Networks")
                topic = st.text_input("Topic *", placeholder="e.g. TCP/IP vs OSI Model, IP Addressing")
            with col2:
                difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
                num_q = st.select_slider("Number of Questions", options=[3, 5, 8, 10], value=5)
            with col3:
                quiz_format = st.selectbox(
                    "Question Format",
                    ["Multiple Choice Questions (MCQ)", "True or False", "Short Answer Questions"],
                    index=0,
                )
                fmt_code = "mcq" if "MCQ" in quiz_format else ("true_false" if "True" in quiz_format else "short")

            generate_quiz_btn = st.form_submit_button("Generate Practice Test", type="primary", use_container_width=True)

        if generate_quiz_btn:
            if not subject or not topic:
                st.error("Please specify both Subject and Topic.")
            else:
                with st.spinner("Generating academic quiz questions and validating answer keys..."):
                    success, quiz_data, err = agent.generate_quiz(
                        subject=subject,
                        topic=topic,
                        difficulty=difficulty,
                        num_questions=num_q,
                        quiz_format=fmt_code,
                    )
                    if success and quiz_data:
                        st.session_state.current_quiz = quiz_data
                        st.session_state.quiz_user_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_result = None
                        st.success(f"Generated {len(quiz_data.get('questions', []))} questions for {topic}!")
                        st.rerun()
                    else:
                        st.error(f"Failed to generate quiz: {err}")

    # Active Quiz Form
    quiz = st.session_state.get("current_quiz")
    if quiz and "questions" in quiz:
        questions = quiz.get("questions", [])
        st.markdown("---")
        st.markdown(
            f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                <h3 style="margin: 0; color: #38bdf8;">📝 Test: {quiz.get('topic')}</h3>
                <p style="margin: 4px 0 0 0; color: #94a3b8;">
                    Subject: {quiz.get('subject')} | Difficulty: <strong>{quiz.get('difficulty')}</strong> | {len(questions)} Questions
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        submitted = st.session_state.get("quiz_submitted", False)
        result = st.session_state.get("quiz_result")

        # Result Banner if submitted
        if submitted and result:
            score = result.get("percentage", 0.0)
            passed = result.get("passed", False)
            color = "#22c55e" if passed else "#ef4444"
            st.markdown(
                f"""
                <div style="background: rgba(30, 41, 59, 0.8); border: 2px solid {color}; border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 24px;">
                    <h2 style="margin: 0; color: {color};">Score: {score}% ({result.get('correct_count')}/{result.get('total_questions')} Correct)</h2>
                    <p style="color: #cbd5e1; margin: 6px 0 0 0;">
                        {'🎉 Great job! You demonstrated strong mastery of this topic.' if passed else '📚 Keep practicing! Review the detailed explanations below.'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Questions Display
        user_answers = st.session_state.setdefault("quiz_user_answers", {})

        with st.form("quiz_submission_form"):
            for idx, q in enumerate(questions):
                q_id = q.get("id", idx + 1)
                st.markdown(f"#### Question {idx + 1}")
                st.markdown(f"**{q.get('question')}**")

                q_type = q.get("type", "mcq")
                options = q.get("options", [])

                if q_type in ("mcq", "true_false") and options:
                    current_val = user_answers.get(q_id, options[0] if options else "")
                    user_answers[q_id] = st.radio(
                        f"Select your answer for Q{idx + 1}:",
                        options=options,
                        key=f"radio_q_{idx}",
                        disabled=submitted,
                        index=options.index(current_val) if current_val in options else 0,
                    )
                else:
                    user_answers[q_id] = st.text_input(
                        f"Your answer for Q{idx + 1}:",
                        value=user_answers.get(q_id, ""),
                        key=f"text_q_{idx}",
                        disabled=submitted,
                    )

                # Show breakdown and explanation if already submitted
                if submitted and result:
                    bd = result["breakdown"][idx] if idx < len(result["breakdown"]) else None
                    if bd:
                        if bd["is_correct"]:
                            st.success(f"✅ Correct! Answer: {bd['correct_answer']}")
                        else:
                            st.error(f"❌ Incorrect. Your answer: {bd['selected_answer']} | Correct answer: {bd['correct_answer']}")
                        if bd.get("explanation"):
                            st.info(f"💡 Explanation: {bd['explanation']}")

                st.markdown("---")

            if not submitted:
                submit_test = st.form_submit_button("Submit Quiz for Evaluation", type="primary", use_container_width=True)
                if submit_test:
                    with st.spinner("Grading answers and saving test attempt..."):
                        eval_result = agent.evaluate_quiz(
                            questions=questions,
                            user_answers=user_answers,
                            subject=quiz.get("subject", "General"),
                            topic=quiz.get("topic", "General"),
                            difficulty=quiz.get("difficulty", "Medium"),
                        )
                        st.session_state.quiz_submitted = True
                        st.session_state.quiz_result = eval_result
                        st.rerun()
            else:
                retake_btn = st.form_submit_button("Retake This Quiz", use_container_width=True)
                if retake_btn:
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_user_answers = {}
                    st.session_state.quiz_result = None
                    st.rerun()
