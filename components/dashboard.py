"""Student Assistant Dashboard Component.

Displays student welcome overview, real stored academic progress,
quick action navigation shortcuts, recent quiz results, and study plan tasks.
"""

from typing import Any, Dict
import streamlit as st
from agent.academic_agent import AcademicAgent


def render_dashboard(student_profile: Dict[str, Any], user_id: str, on_navigate=None):
    """Render main application dashboard."""
    full_name = student_profile.get("full_name", "Student")
    course = student_profile.get("course", "Degree")
    branch = student_profile.get("branch", "Branch")
    semester = student_profile.get("semester", "Semester")
    college = student_profile.get("college", "University")

    # Header Card
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    border: 1px solid #334155; border-radius: 12px; padding: 24px; margin-bottom: 24px; color: #f8fafc;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="background: #3b82f6; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
                        Active Student
                    </span>
                    <h2 style="margin: 8px 0 4px 0; font-size: 1.8rem; font-weight: 700;">Welcome back, {full_name}! 👋</h2>
                    <p style="margin: 0; color: #94a3b8; font-size: 0.95rem;">
                        🎓 {course} • {branch} &nbsp;|&nbsp; 📚 {semester} &nbsp;|&nbsp; 🏛️ {college}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Agent Tools: Fetch REAL stored progress metrics
    agent = AcademicAgent(user_id=user_id)
    with st.spinner("Loading academic progress..."):
        metrics = agent.get_study_progress(user_id)

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Study Plans", metrics["total_plans"])
    with m2:
        st.metric("Tasks Completed", f"{metrics['completed_tasks']}/{metrics['total_tasks']}")
    with m3:
        st.metric("Task Completion Rate", f"{metrics['completion_rate']}%")
    with m4:
        st.metric("Avg Quiz Score", f"{metrics['average_quiz_score']}%" if metrics["total_quizzes"] > 0 else "N/A")

    st.markdown("---")

    # Action Shortcuts Row
    st.subheader("⚡ Quick Academic Actions")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("💬 Ask AI Agent\n\nInstant academic explanations", use_container_width=True):
            if on_navigate:
                on_navigate("AI Academic Chat")
    with c2:
        if st.button("📄 PDF Assistant\n\nAsk questions about notes", use_container_width=True):
            if on_navigate:
                on_navigate("PDF Study Assistant")
    with c3:
        if st.button("📝 Exam Notes\n\nGenerate revision guides", use_container_width=True):
            if on_navigate:
                on_navigate("Exam Notes Generator")
    with c4:
        if st.button("🎯 Practice Quiz\n\nTest understanding", use_container_width=True):
            if on_navigate:
                on_navigate("Quiz Generator")
    with c5:
        if st.button("📅 Study Planner\n\nExam schedule & tasks", use_container_width=True):
            if on_navigate:
                on_navigate("Study Planner")

    st.markdown("---")

    # Lower Grid: Recent Plans & Quizzes
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Active Study Plans")
        active_plans = metrics.get("active_plans", [])
        if active_plans:
            for p in active_plans:
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: #38bdf8; font-size: 1rem;">{p.get('title')}</h4>
                        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                            Subject: {p.get('subject')} | 📅 {p.get('start_date')} to {p.get('end_date')}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No study plans created yet. Use the Study Planner to generate one!")

    with col_right:
        st.subheader("🏆 Recent Quiz Results")
        recent_quizzes = metrics.get("recent_quizzes", [])
        if recent_quizzes:
            for q in recent_quizzes:
                score = q.get("score", 0)
                badge_color = "#22c55e" if score >= 70 else ("#eab308" if score >= 50 else "#ef4444")
                st.markdown(
                    f"""
                    <div style="background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #f8fafc; font-size: 1rem;">{q.get('topic')}</h4>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                                {q.get('subject')} • Difficulty: {q.get('difficulty', 'Medium')}
                            </p>
                        </div>
                        <span style="background: {badge_color}; color: white; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.9rem;">
                            {score}%
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No quizzes taken yet. Test your knowledge in the Quiz Generator!")
