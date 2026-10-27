"""Supabase Client Initialization and Connection Management.

Handles Supabase client singleton setup, credentials verification,
and graceful failure reporting if configuration is missing.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We lazily import supabase to allow running offline/test suites
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    create_client = None  # type: ignore
    Client = None  # type: ignore
    SUPABASE_AVAILABLE = False

_client_instance: Optional[object] = None


def get_supabase_credentials() -> tuple[Optional[str], Optional[str]]:
    """Retrieve Supabase URL and anon key from environment variables."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    return url or None, key or None


def is_supabase_configured() -> bool:
    """Check if valid Supabase credentials have been configured."""
    url, key = get_supabase_credentials()
    return bool(url and key and SUPABASE_AVAILABLE)


def get_supabase_client():
    """Get or create singleton Supabase client instance.

    Returns:
        Supabase Client if configured, or None if unconfigured/unavailable.
    """
    global _client_instance
    if _client_instance is not None:
        return _client_instance

    url, key = get_supabase_credentials()
    if not url or not key:
        return None

    if not SUPABASE_AVAILABLE:
        return None

    try:
        _client_instance = create_client(url, key)
        return _client_instance
    except Exception as err:
        # Avoid leaking keys or raw URLs in log
        print(f"[SupabaseClient] Initialization failed: {type(err).__name__}")
        return None


def reset_client_instance() -> None:
    """Reset the singleton instance (primarily for testing)."""
    global _client_instance
    _client_instance = None
