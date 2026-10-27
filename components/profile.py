"""Student Profile and Academic Settings UI Component.

Displays and allows editing of student profile details, degree,
academic branch, semester, graduation year, and study preferences.
"""

from typing import Any, Dict
import streamlit as st
from database.repositories import ProfileRepository


def render_profile(student_profile: Dict[str, Any], user_id: str):
    """Render student academic profile management."""
    st.title("👤 My Academic Profile")
    st.caption("Manage your university degree details, current semester, and explanation preferences.")

    repo = ProfileRepository()

    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", value=student_profile.get("full_name", ""))
            username = st.text_input("Username", value=student_profile.get("username", ""), disabled=True)
            email = st.text_input("Email Address", value=student_profile.get("email", ""), disabled=True)
            college = st.text_input("College / University", value=student_profile.get("college", ""))

        with col2:
            course = st.text_input("Degree / Course", value=student_profile.get("course", ""))
            branch = st.text_input("Academic Branch", value=student_profile.get("branch", ""))
            semester = st.selectbox(
                "Current Semester / Year",
                [
                    "Semester 1 (1st Year)",
                    "Semester 2 (1st Year)",
                    "Semester 3 (2nd Year)",
                    "Semester 4 (2nd Year)",
                    "Semester 5 (3rd Year)",
                    "Semester 6 (3rd Year)",
                    "Semester 7 (4th Year)",
                    "Semester 8 (4th Year)",
                    "Graduate / Masters",
                ],
                index=0,
            )
            preferred_language = st.selectbox(
                "Preferred Language for Explanations",
                ["English", "Hindi", "Spanish", "French", "German", "Simplified Chinese"],
                index=0,
            )

        existing_subjects = ", ".join(student_profile.get("subjects_of_interest", []))
        subjects_input = st.text_input("Subjects of Interest (Comma separated)", value=existing_subjects)

        submit_save = st.form_submit_button("Save Profile Changes", type="primary", use_container_width=True)

        if submit_save:
            if not full_name or not course or not branch:
                st.error("Full name, degree, and branch cannot be empty.")
            else:
                subjects_list = [s.strip() for s in subjects_input.split(",") if s.strip()]
                updated_data = {
                    "full_name": full_name.strip(),
                    "college": college.strip(),
                    "course": course.strip(),
                    "branch": branch.strip(),
                    "semester": semester,
                    "preferred_language": preferred_language,
                    "subjects_of_interest": subjects_list,
                }
                with st.spinner("Updating academic profile in database..."):
                    success = repo.update_profile(user_id, updated_data)
                    if success:
                        st.session_state.student_profile = {**student_profile, **updated_data}
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile. Please verify database connectivity.")
