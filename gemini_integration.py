"""Gemini-assisted purchase drafting; AI output is advisory only."""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent'


def gemini_purchase_draft(api_key, user_request, request_fn=None):
    if not api_key:
        raise ValueError('Gemini API key is not configured')
    if not (user_request or '').strip():
        raise ValueError('Enter a purchase request')
    payload = {
        'systemInstruction': {'parts': [{'text': 'Suggest a concise purchase description and merchant category for human review. Never claim to have purchased anything or approve payments. Use plain text, maximum 90 words.'}]},
        'contents': [{'role': 'user', 'parts': [{'text': user_request[:1500]}]}],
        'generationConfig': {'maxOutputTokens': 250, 'temperature': 0.3},
    }
    if request_fn is None:
        def request_fn(url, headers, body):
            request = Request(url, data=body, headers=headers, method='POST')
            with urlopen(request, timeout=20) as response:
                return json.load(response)
    response = request_fn(GEMINI_ENDPOINT, {'x-goog-api-key': api_key, 'Content-Type': 'application/json'}, json.dumps(payload).encode('utf-8'))
    candidates = response.get('candidates') or []
    parts = candidates[0].get('content', {}).get('parts', []) if candidates else []
    result = ' '.join(p.get('text', '') for p in parts if isinstance(p, dict)).strip()
    if not result:
        raise ValueError('Gemini returned no purchase suggestion')
    return result
