"""Personalized Study Planner UI Component.

Generates structured multi-subject exam preparation schedules,
manages individual tasks, toggles completion, and tracks real progress.
"""

from datetime import date, timedelta
from typing import Any, Dict
import streamlit as st
from agent.academic_agent import AcademicAgent


def render_study_planner(student_profile: Dict[str, Any], user_id: str):
    """Render the personalized study planner interface."""
    st.title("📅 Personalized Study Planner")
    st.caption("AI-optimized study timetables balanced across syllabus difficulty and exam deadlines.")

    agent = AcademicAgent(user_id=user_id)

    tab_create, tab_active = st.tabs(["✨ Generate New Plan", "📌 My Active Plans & Tasks"])

    with tab_create:
        with st.form("study_plan_form"):
            col1, col2 = st.columns(2)
            with col1:
                subjects = st.text_input(
                    "Subjects / Course Units *",
                    placeholder="e.g. Data Structures, Discrete Mathematics, Operating Systems",
                )
                topics = st.text_area(
                    "Topics / Modules to Cover *",
                    placeholder="e.g. Trees & Graphs, Sorting algorithms, Relations, Memory Management",
                    height=90,
                )
            with col2:
                c_d1, c_d2 = st.columns(2)
                today = date.today()
                with c_d1:
                    start_d = st.date_input("Plan Start Date", value=today, min_value=today)
                with c_d2:
                    exam_d = st.date_input("Examination Date", value=today + timedelta(days=14), min_value=today + timedelta(days=1))

                daily_hours = st.slider("Available Daily Study Time (Hours)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)

            submit_plan = st.form_submit_button("Generate Personalized Study Plan", type="primary", use_container_width=True)

        if submit_plan:
            if not subjects or not topics:
                st.error("Please fill in the subjects and topics to cover.")
            elif start_d >= exam_d:
                st.error("Exam date must be after the start date.")
            else:
                with st.spinner("Calculating optimal topic schedule and spaced repetition plan..."):
                    success, plan_json, err = agent.create_study_plan(
                        subjects=subjects,
                        topics=topics,
                        exam_date=str(exam_d),
                        daily_hours=daily_hours,
                        start_date=str(start_d),
                        end_date=str(exam_d),
                    )
                    if success and plan_json:
                        st.success(f"Study Plan '{plan_json.get('plan_title')}' created and saved successfully!")
                        st.session_state.latest_plan = plan_json
                        st.rerun()
                    else:
                        st.error(f"Failed to generate study plan: {err}")

    with tab_active:
        plans = agent.plan_repo.get_user_plans(user_id)
        if not plans:
            st.info("No saved study plans found. Generate your first study schedule in the 'Generate New Plan' tab.")
        else:
            plan_titles = {p["id"]: f"{p['title']} ({p['subject']}) - {p['start_date']} to {p['end_date']}" for p in plans}
            selected_plan_id = st.selectbox(
                "Select Active Plan",
                options=list(plan_titles.keys()),
                format_func=lambda x: plan_titles[x],
            )

            if selected_plan_id:
                col_btn, _ = st.columns([2, 5])
                with col_btn:
                    if st.button("🗑️ Delete Selected Plan", type="secondary"):
                        agent.plan_repo.delete_plan(user_id, selected_plan_id)
                        st.success("Plan deleted.")
                        st.rerun()

                tasks = agent.task_repo.get_plan_tasks(user_id, selected_plan_id)
                if not tasks:
                    st.info("No individual tasks found for this plan.")
                else:
                    completed_count = sum(1 for t in tasks if t.get("status") == "completed")
                    total_count = len(tasks)
                    pct = (completed_count / total_count) if total_count else 0.0

                    st.markdown(f"**Progress:** {completed_count}/{total_count} tasks completed ({int(pct * 100)}%)")
                    st.progress(pct)

                    st.markdown("### 📋 Schedule Checklist")
                    for t in tasks:
                        t_id = t["id"]
                        is_done = t.get("status") == "completed"
                        col_chk, col_info = st.columns([1, 10])

                        with col_chk:
                            chk = st.checkbox("", value=is_done, key=f"task_chk_{t_id}")
                            if chk != is_done:
                                new_status = "completed" if chk else "pending"
                                agent.update_study_task(user_id, t_id, new_status)
                                st.rerun()

                        with col_info:
                            priority = t.get("priority", "Medium")
                            badge = "🔴 High" if priority == "High" else ("🟡 Medium" if priority == "Medium" else "🟢 Low")
                            duration = t.get("estimated_duration", 60)
                            due = t.get("due_date", "")
                            st.markdown(
                                f"""
                                <div style="padding: 4px 0;">
                                    <strong style="text-decoration: {'line-through' if is_done else 'none'}; font-size: 1rem; color: {'#94a3b8' if is_done else '#f8fafc'};">
                                        {t.get('task_title')}
                                    </strong>
                                    &nbsp; <span style="font-size: 0.8rem; background: #334155; padding: 2px 6px; border-radius: 4px;">{badge}</span>
                                    &nbsp; <span style="font-size: 0.8rem; color: #94a3b8;">⏱️ {duration}m &nbsp;|&nbsp; 📅 Due: {due}</span>
                                    <p style="margin: 2px 0 0 0; font-size: 0.85rem; color: #94a3b8;">{t.get('description', '')}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        st.markdown("<hr style='margin: 4px 0;'/>", unsafe_allow_html=True)
