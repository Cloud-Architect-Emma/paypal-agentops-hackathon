# PayPal AgentOps — Control Plane for Trusted Agentic Commerce

**Hackathon demonstration / simulation only.** No money moves; no PayPal API calls occur in this repository.

## Project links
- **Live demo:** https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/
- **GitHub repository:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon
- **Recording guide:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon/blob/main/DEMO_SCRIPT.md
- **Submission details:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon/blob/main/SUBMISSION_COPY.md

## Problem
AI shopping agents can initiate purchases, but buyers and operators need transparent policy gates, explicit consent, and auditable decisions before any payment execution.

## Demo
1. Propose a £49.99 purchase from **Office Supplies** with a £100 spending limit.
2. See a policy pass and explicit buyer approval requirement.
3. Approve the proposal and inspect the simulated outcome and audit timeline.
4. Propose a £150 purchase to see an automatic spending-limit block.
5. Propose £30 at **Unknown Merchant** to see a merchant-policy block.

## Run locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Public deployment
The Streamlit application is live at https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/. It deploys from branch `main` with entrypoint `app.py`. No secrets are required.

## Architecture
```text
Simulated AI agent proposal
          |
          v
  AgentOps policy evaluation ----- blocked -----> audit trail
          |
          v
 Explicit buyer decision --------- rejected ----> audit trail
          |
          v
 Simulated approval (NO PAYMENT EXECUTION) -----> audit trail
```

## Security and scope
- No Firebase or PayPal dependency; no API credentials.
- No real AI agent or PayPal calls; purchase requests are simulated UI inputs.
- All transaction state is held in a single Streamlit session and is not persistent.
- Policy logic is deterministic and intentionally simplified; not production-grade authorization.
- Existing full AgentOps backend and database are **not** part of this demo repository.
- Do not claim real payment execution, real AI agent integration, or immutable audit persistence.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Submission assets
See `DEMO_SCRIPT.md` and `SUBMISSION_COPY.md`.
