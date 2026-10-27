"""Supabase Authentication Service.

Handles user registration, login (supporting either username or email),
password reset, session verification, and input validation.
"""

import re
from typing import Any, Dict, Optional, Tuple
from database.supabase_client import get_supabase_client
from database.repositories import ProfileRepository


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format and length."""
    if not email or not isinstance(email, str):
        return False, "Email is required."
    email = email.strip()
    if len(email) > 254:
        return False, "Email is too long (maximum 254 characters)."
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False, "Invalid email address format."
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format, length, and characters."""
    if not username or not isinstance(username, str):
        return False, "Username is required."
    username = username.strip()
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username may only contain letters, numbers, and underscores."
    return True, ""


def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength.

    Requires at least 8 characters, at least one letter, and at least one number.
    """
    if not password or not isinstance(password, str):
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password is too long (maximum 128 characters)."
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, ""


def validate_registration_payload(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """Comprehensive validation for account information and student profile."""
    # Account fields
    u_ok, u_msg = validate_username(payload.get("username", ""))
    if not u_ok:
        return False, u_msg

    e_ok, e_msg = validate_email(payload.get("email", ""))
    if not e_ok:
        return False, e_msg

    pwd = payload.get("password", "")
    confirm_pwd = payload.get("confirm_password", "")
    p_ok, p_msg = validate_password(pwd)
    if not p_ok:
        return False, p_msg

    if pwd != confirm_pwd:
        return False, "Passwords do not match."

    # Student Profile mandatory fields
    full_name = str(payload.get("full_name", "")).strip()
    if not full_name or len(full_name) < 2 or len(full_name) > 100:
        return False, "Full name must be between 2 and 100 characters."

    course = str(payload.get("course", "")).strip()
    if not course or len(course) > 80:
        return False, "Degree or course is required (max 80 characters)."

    branch = str(payload.get("branch", "")).strip()
    if not branch or len(branch) > 80:
        return False, "Academic branch is required (max 80 characters)."

    semester = str(payload.get("semester", "")).strip()
    if not semester:
        return False, "Current semester or academic year is required."

    grad_year = payload.get("graduation_year")
    if grad_year is not None and grad_year != "":
        try:
            gy = int(grad_year)
            if gy < 2000 or gy > 2040:
                return False, "Graduation year must be between 2000 and 2040."
        except ValueError:
            return False, "Graduation year must be a valid integer."

    return True, ""


class AuthService:
    """Authentication service providing secure access via Supabase Auth."""

    def __init__(self, profile_repo: Optional[ProfileRepository] = None):
        self.profile_repo = profile_repo or ProfileRepository()

    @property
    def client(self):
        return get_supabase_client()

    def sign_in(self, identifier: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Sign in using either registered email or username.

        Returns:
            Tuple of (success, message, user_data_dict)
        """
        client = self.client
        if not client:
            return False, "Authentication service is currently unavailable. Check your configuration.", None

        identifier = identifier.strip()
        if not identifier or not password:
            return False, "Please enter both identifier (username/email) and password.", None

        # Resolve email if identifier is a username (no '@')
        email_to_use = identifier
        if "@" not in identifier:
            resolved = self.profile_repo.resolve_username_to_email(identifier)
            if not resolved:
                # Use generic error to avoid exposing account existence
                return False, "Invalid email/username or password.", None
            email_to_use = resolved

        try:
            auth_response = client.auth.sign_in_with_password({
                "email": email_to_use,
                "password": password,
            })
            if auth_response and auth_response.user:
                user = auth_response.user
                return True, "Login successful.", {
                    "id": user.id,
                    "email": user.email,
                    "session": auth_response.session,
                }
            return False, "Invalid email/username or password.", None
        except Exception as e:
            # Mask raw error to prevent information leakage
            err_str = str(e).lower()
            if "invalid" in err_str or "credentials" in err_str:
                return False, "Invalid email/username or password.", None
            if "confirm" in err_str or "verified" in err_str:
                return False, "Please verify your email address before logging in.", None
            return False, "Authentication failed. Please check your credentials.", None

    def sign_up(self, registration_data: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """Register a new student account and create their academic profile.

        Returns:
            Tuple of (success, message, user_id)
        """
        client = self.client
        if not client:
            return False, "Authentication service is currently unavailable.", None

        # Validate all fields
        is_valid, val_msg = validate_registration_payload(registration_data)
        if not is_valid:
            return False, val_msg, None

        email = registration_data["email"].strip().lower()
        password = registration_data["password"]

        try:
            # 1. Sign up user in Supabase Auth
            auth_res = client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": registration_data["username"].strip(),
                        "full_name": registration_data["full_name"].strip(),
                    }
                }
            })

            if not auth_res or not auth_res.user:
                return False, "Failed to create account. Please try again.", None

            user_id = auth_res.user.id

            # 2. Persist student profile
            profile_created = self.profile_repo.create_profile(user_id, registration_data)
            if not profile_created:
                # Profile persistence issue: alert student that profile can be completed upon login
                return True, "Account created, but profile setup is pending. You can complete it upon login.", user_id

            return True, "Account registered successfully! You may now log in.", user_id

        except Exception as e:
            err_str = str(e).lower()
            if "already registered" in err_str or "unique constraint" in err_str:
                return False, "An account with this email or username already exists.", None
            return False, "Registration failed. Please check your details and try again.", None

    def reset_password(self, email: str) -> Tuple[bool, str]:
        """Send password reset email."""
        client = self.client
        if not client:
            return False, "Authentication service is unavailable."

        v_ok, v_msg = validate_email(email)
        if not v_ok:
            return False, v_msg

        try:
            client.auth.reset_password_for_email(email.strip().lower())
            return True, "If an account exists for this email, password reset instructions have been sent."
        except Exception:
            # Return same generic response for security
            return True, "If an account exists for this email, password reset instructions have been sent."

    def sign_out(self) -> bool:
        """Sign out the current session."""
        client = self.client
        if not client:
            return True
        try:
            client.auth.sign_out()
            return True
        except Exception:
            return True
