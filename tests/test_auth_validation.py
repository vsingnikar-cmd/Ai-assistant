"""Unit tests for authentication, password validation, and registration constraints."""

import pytest
from auth.auth_service import (
    validate_email,
    validate_username,
    validate_password,
    validate_registration_payload,
)


def test_valid_email_passes():
    ok, msg = validate_email("alex@university.edu")
    assert ok is True
    assert msg == ""


@pytest.mark.parametrize("invalid_email", [
    "",
    "not-an-email",
    "@missingusername.com",
    "missingat.com",
    "user@.com",
    "a" * 260 + "@university.edu",
])
def test_invalid_email_fails(invalid_email):
    ok, msg = validate_email(invalid_email)
    assert ok is False
    assert len(msg) > 0


def test_valid_username_passes():
    ok, msg = validate_username("john_doe_99")
    assert ok is True
    assert msg == ""


@pytest.mark.parametrize("invalid_username", [
    "",
    "ab",                  # too short (<3)
    "a" * 35,              # too long (>30)
    "user name",           # contains space
    "user@name",           # illegal character
    "student-name",        # hyphen not allowed
])
def test_invalid_username_fails(invalid_username):
    ok, msg = validate_username(invalid_username)
    assert ok is False


def test_valid_password_passes():
    ok, msg = validate_password("SecurePass123")
    assert ok is True


@pytest.mark.parametrize("weak_password", [
    "",
    "short1",              # < 8 chars
    "alllowercaseletters",  # no digits
    "1234567890",          # no letters
])
def test_weak_password_fails(weak_password):
    ok, msg = validate_password(weak_password)
    assert ok is False


def test_valid_registration_payload():
    payload = {
        "username": "sarah_eng",
        "email": "sarah@college.edu",
        "password": "Password2026",
        "confirm_password": "Password2026",
        "full_name": "Sarah Connor",
        "course": "B.Tech Computer Science",
        "branch": "Artificial Intelligence",
        "semester": "Semester 4",
        "graduation_year": 2027,
    }
    ok, msg = validate_registration_payload(payload)
    assert ok is True
    assert msg == ""


def test_mismatched_password_fails():
    payload = {
        "username": "sarah_eng",
        "email": "sarah@college.edu",
        "password": "Password2026",
        "confirm_password": "DifferentPassword123",
        "full_name": "Sarah Connor",
        "course": "B.Tech",
        "branch": "AI",
        "semester": "Semester 4",
    }
    ok, msg = validate_registration_payload(payload)
    assert ok is False
    assert "Passwords do not match" in msg
