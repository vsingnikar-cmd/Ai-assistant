"""Streamlit Registration and Profile Completion Page.

Renders account creation and academic student profile registration.
Validates email, username, password complexity, academic details, and constraints.
"""

from typing import Optional
import streamlit as st
from auth.auth_service import AuthService
from database.repositories import ProfileRepository


def render_register(on_navigate_login=None):
    """Render the student registration and profile form."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 800; color: #1e293b; margin-bottom: 6px;">
                Create Student Account
            </h1>
            <p style="color: #64748b; font-size: 1rem;">
                Join the AI Student Assistant platform with your academic details
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auth_service = AuthService()

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.form("student_registration_form"):
            st.subheader("1. Account Credentials")
            c_u, c_e = st.columns(2)
            with c_u:
                username = st.text_input(
                    "Username *",
                    placeholder="e.g. alex_cs",
                    help="Unique 3-30 character username (letters, numbers, underscore).",
                )
            with c_e:
                email = st.text_input(
                    "Email Address *",
                    placeholder="e.g. alex@university.edu",
                    help="Active academic or personal email address.",
                )

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Min 8 chars, 1 letter, 1 number",
                )
            with c_p2:
                confirm_password = st.text_input(
                    "Confirm Password *",
                    type="password",
                    placeholder="Re-type password",
                )

            st.markdown("---")
            st.subheader("2. Student Academic Profile")

            full_name = st.text_input("Full Name *", placeholder="e.g. Alex Johnson")

            c_c, c_b = st.columns(2)
            with c_c:
                course = st.text_input(
                    "Degree / Course *",
                    placeholder="e.g. B.Tech Computer Science, B.Sc, BCA",
                )
            with c_b:
                branch = st.text_input(
                    "Academic Branch / Specialization *",
                    placeholder="e.g. Information Technology, AI/ML, Electrical",
                )

            c_col, c_sem = st.columns(2)
            with c_col:
                college = st.text_input(
                    "College / University",
                    placeholder="e.g. Stanford University, MIT, IIT Bombay",
                )
            with c_sem:
                semester = st.selectbox(
                    "Current Semester / Year *",
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
                )

            c_gy, c_lang = st.columns(2)
            with c_gy:
                grad_year_str = st.text_input(
                    "Expected Graduation Year",
                    placeholder="e.g. 2027",
                )
            with c_lang:
                preferred_language = st.selectbox(
                    "Preferred Explanation Language",
                    ["English", "Hindi", "Spanish", "French", "German", "Simplified Chinese"],
                    index=0,
                )

            subjects_input = st.text_input(
                "Subjects of Interest (Comma separated)",
                placeholder="e.g. Data Structures, Operating Systems, Machine Learning",
            )

            st.caption("* Indicates required fields. Passwords are encrypted and managed via Supabase Auth.")

            submit_register = st.form_submit_button(
                "Register & Create Profile", use_container_width=True, type="primary"
            )

            if submit_register:
                # Prepare payload
                subjects_list = [s.strip() for s in subjects_input.split(",") if s.strip()]
                grad_year = None
                if grad_year_str.strip():
                    try:
                        grad_year = int(grad_year_str.strip())
                    except ValueError:
                        grad_year = -1  # Will trigger validator error

                payload = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "confirm_password": confirm_password,
                    "full_name": full_name,
                    "course": course,
                    "branch": branch,
                    "college": college,
                    "semester": semester,
                    "graduation_year": grad_year,
                    "subjects_of_interest": subjects_list,
                    "preferred_language": preferred_language,
                }

                with st.spinner("Creating student account and profile..."):
                    success, msg, user_id = auth_service.sign_up(payload)
                    if success:
                        st.session_state.registration_success_message = msg
                    else:
                        st.error(msg)

        registration_success_message = st.session_state.get("registration_success_message")
        if registration_success_message:
            st.success(registration_success_message)
            st.info("You can now sign in using your credentials.")
            if st.button("Proceed to Sign In"):
                st.session_state.pop("registration_success_message", None)
                st.session_state.auth_view = "login"
                st.rerun()

        st.markdown("<div style='text-align: center; margin-top: 16px;'>", unsafe_allow_html=True)
        if st.button("Already have an account? Sign In here"):
            st.session_state.pop("registration_success_message", None)
            if on_navigate_login:
                on_navigate_login()
            st.session_state.auth_view = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_complete_profile(user_id: str, email: str):
    """Render profile completion form for users whose profiles are incomplete."""
    st.warning("Your academic profile is incomplete. Please provide your academic details to access the agent.")

    with st.form("complete_profile_form"):
        full_name = st.text_input("Full Name *")
        course = st.text_input("Degree / Course *")
        branch = st.text_input("Academic Branch *")
        college = st.text_input("College / University")
        semester = st.selectbox(
            "Current Semester *",
            [
                "Semester 1",
                "Semester 2",
                "Semester 3",
                "Semester 4",
                "Semester 5",
                "Semester 6",
                "Semester 7",
                "Semester 8",
            ],
        )
        submit = st.form_submit_button("Complete Profile", type="primary")

        if submit:
            if not full_name or not course or not branch or not semester:
                st.error("Please fill in all mandatory fields.")
            else:
                repo = ProfileRepository()
                success = repo.create_profile(
                    user_id,
                    {
                        "username": email.split("@")[0],
                        "email": email,
                        "full_name": full_name,
                        "course": course,
                        "branch": branch,
                        "college": college,
                        "semester": semester,
                    },
                )
                if success:
                    st.success("Profile saved! Redirecting to dashboard...")
                    st.rerun()
                else:
                    st.error("Could not save profile. Please check database connectivity.")
