# PayPal AgentOps — connected AI proposal workflow

## Files to add or replace

- Replace `app.py` with the included `app.py`.
- Add `ai_proposal.py` to the repository root.
- Add `gemini_proposal.py` to the repository root.
- Add `tests/test_ai_proposal.py` to the `tests` folder.
- Leave `engine.py`, `integrations.py`, `gemini_integration.py`, and `requirements.txt` unchanged.

## Quick upload via Codespaces

Unzip the bundle into the repository root, then run:

```bash
python -m unittest discover -s tests -v
git add app.py ai_proposal.py gemini_proposal.py tests/test_ai_proposal.py
git commit -m "Connect Gemini proposals to AgentOps policy and buyer approval"
git push
```

Do not commit `.streamlit/secrets.toml` or API keys. Existing `GEMINI_API_KEY` in Streamlit Cloud secrets remains valid.

## Demo

1. Tab 05: enter purchase request and policy settings, click Generate AI purchase proposal.
2. Review structured category, amount, and description; click Submit AI proposal to policy engine.
3. If eligible, tab 02: approve or reject. If blocked, inspect tab 03.
4. Tab 03: download the audit JSON.

Payment execution is intentionally disabled. The policy uses merchant categories, not verified merchant identities.
