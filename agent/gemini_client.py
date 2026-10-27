"""Gemini API Client for Student Assistant Agent.

Interfaces with Google Gemini via the official google-genai SDK.
Handles API key configuration, model selection, rate limiting, retries,
and structured JSON parsing.
"""

import os
import json
import re
import time
from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Attempt importing official google-genai SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore
    types = None  # type: ignore
    GENAI_AVAILABLE = False


DEFAULT_MODEL = "gemini-3.5-flash-lite"


class GeminiClient:
    """Wrapper around Google Gemini client."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = model_name or os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
        self._client = None

        if self.api_key and GENAI_AVAILABLE:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as err:
                print(f"[GeminiClient] Client initialization error: {type(err).__name__}")
                self._client = None

    def is_configured(self) -> bool:
        """Check if Gemini API key is configured and SDK is installed."""
        return bool(self.api_key and self._client is not None)

    def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 2,
    ) -> Tuple[bool, str]:
        """Generate response from Gemini model with automatic retry.

        Returns:
            Tuple of (success, text_or_error_message)
        """
        if not self.is_configured():
            if not self.api_key:
                return (
                    False,
                    "Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable "
                    "or configure it in Settings.",
                )
            return False, "The google-genai SDK is not installed in the Python environment."

        for attempt in range(max_retries + 1):
            try:
                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction
                if temperature is not None:
                    config["temperature"] = temperature

                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config if config else None,
                )

                if response and response.text:
                    return True, response.text.strip()
                return False, "Received an empty response from Gemini."

            except Exception as e:
                err_msg = str(e)
                # Rate limit or quota error
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    if attempt < max_retries:
                        time.sleep(2 * (attempt + 1))
                        continue
                    return False, "Gemini API rate limit reached. Please wait a moment and try again."

                if attempt < max_retries:
                    time.sleep(1)
                    continue

                return False, f"AI generation encountered an error: {err_msg[:120]}"

        return False, "Failed to generate response after multiple attempts."

    def generate_structured_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_retries: int = 2,
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Generate structured JSON from model and parse output safely.

        Returns:
            Tuple of (success, parsed_dict_or_none, error_message)
        """
        success, text = self.generate_response(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.2,  # Lower temperature for JSON fidelity
            max_retries=max_retries,
        )

        if not success:
            return False, None, text

        # Parse JSON from output, stripping markdown code blocks if present
        clean_json_str = text.strip()
        if clean_json_str.startswith("```"):
            clean_json_str = re.sub(r"^```[a-zA-Z]*\n", "", clean_json_str)
            clean_json_str = re.sub(r"\n```$", "", clean_json_str)

        try:
            parsed = json.loads(clean_json_str)
            return True, parsed, ""
        except json.JSONDecodeError as err:
            # Fallback regex search for JSON object inside response
            match = re.search(r"(\{.*\})", clean_json_str, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    return True, parsed, ""
                except json.JSONDecodeError:
                    pass
            return False, None, f"Failed to parse model output as JSON: {str(err)}"
