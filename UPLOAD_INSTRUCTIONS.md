# Gemini switch for PayPal AgentOps

1. Download this ZIP and extract it.
2. Copy `gemini_integration.py`, `apply_gemini.py`, and `tests/test_gemini_integration.py` into the matching paths of your locally cloned GitHub repository. Do not replace your existing tests.
3. From repository root, run `python apply_gemini.py` once. This updates existing `app.py` and `README.md`.
4. Run `python -m unittest discover -s tests -v`.
5. Commit and push `app.py`, `README.md`, `gemini_integration.py`, and `tests/test_gemini_integration.py` (do not commit secrets).
6. In Streamlit Cloud → App settings → Secrets add `GEMINI_API_KEY = "your-key"`; retain the PayPal sandbox credentials.
7. Redeploy and click Generate AI suggestion. Verify response. Payment execution remains disabled.

This release was tested locally with mocked Gemini responses. Real Gemini API calls require your private key and were not tested here.
