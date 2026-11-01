# Apply these files to GitHub

GitHub returned HTTP 403 for direct updates, so these files have NOT been committed automatically.

1. Replace repository-root `README.md` with this package's `README.md`. The current file is mistakenly a screenshot checklist.
2. Replace `docs/ARCHITECTURE.md`, `screenshots/README.md`, `SUBMISSION_COPY.md` and `DEMO_SCRIPT.md` with the matching files.
3. Keep working code: `app.py`, `engine.py`, `ai_proposal.py`, `gemini_proposal.py`, `integrations.py`, `requirements.txt`, `runtime.txt`, tests, `.gitignore`, GitHub Actions and `LICENSE`.
4. In `integrations.py`, correct only its outdated opening docstring to say: `PayPal sandbox OAuth2, Orders v2 order creation and read-only lookup. No authorization or capture endpoints are called.`
5. `gemini_integration.py` is legacy and is not imported by the current app; delete it only if no external workflow depends on it.
6. Capture real screenshots and upload them; this package contains documentation only.
7. Verify the hosted app's Gemini and PayPal sandbox functionality is accessible to judges and publish the required YouTube demo.

No API credentials, fake screenshots or fictitious YouTube URL have been added.
