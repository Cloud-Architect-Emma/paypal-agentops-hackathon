"""Generate a structured, untrusted purchase proposal with Gemini.

No PayPal payment endpoints are called here. Model output is validated locally.
"""
import json
import logging
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ai_proposal import MERCHANT_CATEGORIES, validate_ai_proposal

BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'
MODELS = ('gemini-3.1-flash-lite', 'gemini-3.8-flash')


def _request(url, headers, body):
    req = Request(url, data=body, headers=headers, method='POST')
    with urlopen(req, timeout=45) as response:
        return json.load(response)


def _response_text(response):
    chunks = []
    for candidate in response.get('candidates') or []:
        for part in (candidate.get('content') or {}).get('parts') or []:
            if isinstance(part, dict) and isinstance(part.get('text'), str):
                chunks.append(part['text'])
    return ''.join(chunks).strip()


def generate_ai_proposal(api_key, user_request, request_fn=None):
    """Return {merchant, amount, description}; caller must run the policy engine."""
    if not api_key or not api_key.strip():
        raise ValueError('Gemini API key is not configured')
    if not isinstance(user_request, str) or not user_request.strip():
        raise ValueError('Enter a purchase request')
    request_fn = request_fn or _request
    payload = {
        'systemInstruction': {'parts': [{'text': (
            'You are a purchase proposal assistant, not a payment agent. '
            'Return only JSON with merchant_category, estimated_amount_gbp and description. '
            'merchant_category MUST be one of: ' + ', '.join(MERCHANT_CATEGORIES) + '. '
            'Use Unknown Merchant if no category fits. '
            'Choose a plausible GBP amount. A stated budget is a maximum, not a target. '
            'Do not claim payment or approval. The output will be validated by a separate policy engine.'
        )}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_request.strip()[:1500]}]}],
        'generationConfig': {
            'temperature': 0.2,
            'maxOutputTokens': 1024,
            'responseMimeType': 'application/json',
            'responseSchema': {
                'type': 'OBJECT',
                'properties': {
                    'merchant_category': {'type': 'STRING', 'enum': list(MERCHANT_CATEGORIES)},
                    'estimated_amount_gbp': {'type': 'NUMBER'},
                    'description': {'type': 'STRING'},
                },
                'required': ['merchant_category', 'estimated_amount_gbp', 'description'],
            },
        },
    }
    headers = {'x-goog-api-key': api_key.strip(), 'Content-Type': 'application/json'}
    body = json.dumps(payload).encode('utf-8')
    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                result = request_fn(f'{BASE_URL}/{model}:generateContent', headers, body)
                raw = _response_text(result)
                if not raw:
                    raise ValueError('Gemini returned no structured proposal')
                return validate_ai_proposal(json.loads(raw))
            except HTTPError as exc:
                last_error = exc
                if exc.code == 404:
                    logging.warning('Gemini model %s unavailable; trying fallback', model)
                    break
                if exc.code in (429, 500, 502, 503, 504):
                    logging.warning('Temporary Gemini HTTP %s on %s', exc.code, model)
                    if attempt == 0:
                        time.sleep(2)
                        continue
                    break
                raise
            except (TimeoutError, socket.timeout, URLError) as exc:
                last_error = exc
                logging.warning('Gemini request failed on %s: %s', model, type(exc).__name__)
                if attempt == 0:
                    time.sleep(2)
                    continue
                break
    raise RuntimeError('Gemini is temporarily unavailable. Try again later.') from last_error
