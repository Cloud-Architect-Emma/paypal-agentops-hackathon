
"""Gemini-assisted purchase drafting for PayPal AgentOps.

AI output is advisory only.
No payments are created, approved, or executed.
"""

import json
import logging
import socket
import time

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
)

# Both models appeared in your API key's available-model list.
MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]

SYSTEM_PROMPT = (
    "You are the purchase-drafting assistant for PayPal AgentOps. "
    "Suggest a suitable purchase based on the user's request. "
    "Include a purchase description, merchant category, "
    "and an estimated amount in GBP when appropriate. "
    "Keep the response under 90 words. "
    "Never claim that a payment was made, approved, "
    "or executed. All purchases require separate "
    "policy validation and explicit human approval."
)


def _gemini_request(url, headers, body):
    """Send a request to the Gemini API."""

    request = Request(
        url,
        data=body,
        headers=headers,
        method="POST",
    )

    with urlopen(request, timeout=45) as response:
        return json.load(response)


def _extract_text(response):
    """Extract text from a Gemini generateContent response."""

    fragments = []

    for candidate in response.get("candidates", []):
        content = candidate.get("content") or {}

        for part in content.get("parts", []):
            if isinstance(part, dict) and part.get("text"):
                fragments.append(part["text"])

    return " ".join(fragments).strip()


def gemini_purchase_draft(api_key, user_request, request_fn=None):
    """Generate an advisory purchase suggestion using Gemini."""

    if not api_key or not api_key.strip():
        raise ValueError("Gemini API key is not configured")

    if not user_request or not user_request.strip():
        raise ValueError("Enter a purchase request")

    if request_fn is None:
        request_fn = _gemini_request

    payload = {
        "systemInstruction": {
            "parts": [
                {"text": SYSTEM_PROMPT}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": user_request.strip()[:1500]}
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024,
        },
    }

    headers = {
        "x-goog-api-key": api_key.strip(),
        "Content-Type": "application/json",
    }

    body = json.dumps(payload).encode("utf-8")

    last_error = None

    for model in MODELS:
        endpoint = (
            f"{GEMINI_BASE_URL}/{model}:generateContent"
        )

        for attempt in range(3):
            try:
                response = request_fn(
                    endpoint,
                    headers,
                    body,
                )

                result = _extract_text(response)

                if result:
                    logging.info(
                        "Gemini purchase draft generated using %s",
                        model,
                    )
                    return result

                raise ValueError(
                    f"Gemini model {model} returned no text"
                )

            except HTTPError as error:
                last_error = error

                # Retry temporary failures.
                if error.code in (429, 500, 502, 503, 504):
                    logging.warning(
                        "Gemini %s returned HTTP %s "
                        "(attempt %s/3)",
                        model,
                        error.code,
                        attempt + 1,
                    )

                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue

                    break

                # Model unavailable: try the fallback model.
                if error.code == 404:
                    logging.warning(
                        "Gemini model %s unavailable; "
                        "trying next model",
                        model,
                    )
                    break

                # Authentication and request errors should
                # not trigger repeated calls.
                logging.error(
                    "Gemini API returned HTTP %s",
                    error.code,
                )
                raise

            except (TimeoutError, socket.timeout, URLError) as error:
                last_error = error

                logging.warning(
                    "Gemini %s connection error "
                    "(attempt %s/3): %s",
                    model,
                    attempt + 1,
                    type(error).__name__,
                )

                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

                break

            except ValueError as error:
                last_error = error
                logging.warning(
                    "Gemini %s returned no usable text",
                    model,
                )
                break

    raise RuntimeError(
        "Gemini could not generate a purchase suggestion "
        "after trying the available models. "
        "Check Streamlit logs for the underlying error."
    ) from last_error
