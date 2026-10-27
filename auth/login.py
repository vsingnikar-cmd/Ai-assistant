"""Streamlit Login Page Component.

Renders a login form supporting username or email login, password toggle,
forgot password workflow, and redirection to registration.
"""

import streamlit as st
from auth.auth_service import AuthService
from auth.session import set_auth_session


def render_login(on_navigate_register=None):
    """Render the student login view."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="font-size: 2.2rem; font-weight: 800; color: #1e293b; margin-bottom: 6px;">
                AI Student Assistant Agent
            </h1>
            <p style="color: #64748b; font-size: 1rem;">
                Sign in with your academic username or registered email
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auth_service = AuthService()

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            tab_login, tab_forgot = st.tabs(["Sign In", "Forgot Password"])

            with tab_login:
                with st.form("login_form", clear_on_submit=False):
                    identifier = st.text_input(
                        "Username or Email",
                        placeholder="e.g. alex_cs or student@university.edu",
                        help="Enter your unique student username or registered email address.",
                    )
                    show_password = st.checkbox("Show password", value=False)
                    password = st.text_input(
                        "Password",
                        type="default" if show_password else "password",
                        placeholder="••••••••",
                    )

                    submit_login = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                    if submit_login:
                        if not identifier or not password:
                            st.error("Please enter both your username/email and password.")
                        else:
                            with st.spinner("Authenticating student credentials..."):
                                success, msg, user_data = auth_service.sign_in(identifier, password)
                                if success and user_data:
                                    set_auth_session(user_data["id"], user_data["email"], user_data.get("session"))
                                    st.success("Authenticated successfully! Redirecting...")
                                    st.rerun()
                                else:
                                    st.error(msg)

                st.markdown("---")
                col_reg1, col_reg2 = st.columns([3, 2])
                with col_reg1:
                    st.caption("Don't have a student account yet?")
                with col_reg2:
                    if st.button("Create Account", use_container_width=True):
                        if on_navigate_register:
                            on_navigate_register()
                        st.session_state.auth_view = "register"
                        st.rerun()

            with tab_forgot:
                st.caption("Enter your email address and we will send you password reset instructions.")
                with st.form("forgot_password_form"):
                    reset_email = st.text_input("Registered Email", placeholder="student@university.edu")
                    submit_reset = st.form_submit_button("Send Reset Link", use_container_width=True)

                    if submit_reset:
                        if not reset_email:
                            st.error("Please enter your registered email address.")
                        else:
                            with st.spinner("Processing password reset request..."):
                                _, msg = auth_service.reset_password(reset_email)
                                st.info(msg)
