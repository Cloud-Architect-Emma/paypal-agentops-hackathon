# PayPal AgentOps — Trusted Agentic Commerce

**Live app:** https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/  
**GitHub:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon  
**Demo script:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon/blob/main/DEMO_SCRIPT.md

## Features
- Buyer policy gate, merchant allowlist, spending limit, explicit human consent, session-based audit log.
- **Optional live OpenAI Responses API** for purchase suggestion drafting; its output cannot authorize a transaction.
- **Optional live PayPal sandbox Orders v2 API** for *read-only retrieval* of an existing sandbox order status, authenticated with OAuth2.
- **Payment execution remains disabled**: no create-order, authorization, capture, refunds, or transfers. No live payment environment.

## Enable external integrations
In Streamlit Community Cloud, open the app → Settings → Secrets and enter your **own** credentials (never commit them to GitHub):

```toml
OPENAI_API_KEY = "<your OpenAI API key>"
PAYPAL_SANDBOX_CLIENT_ID = "<your sandbox client ID>"
PAYPAL_SANDBOX_CLIENT_SECRET = "<your sandbox client secret>"
```

The app runs without secrets, but external integrations remain disabled until configured. Use an existing sandbox order ID from your separate development tests to demonstrate read-only PayPal lookup. AI generation may incur API costs.

## Run and test
```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

## Architecture
AI request → OpenAI draft (optional) → human-entered purchase proposal → deterministic policy → buyer consent → **simulated approval only** → session audit. Separately, read-only PayPal sandbox order status lookup is available for an existing order. The sandbox lookup does **not** execute the proposed purchase.

## Security and limitations
- Secrets stay server-side in Streamlit secrets; never put them in source code or public inputs.
- AI output is untrusted advisory text and cannot bypass policy or trigger payments.
- Read-only PayPal sandbox requests use OAuth2 and GET existing order; OAuth token creation is not a payment operation.
- No Firebase integration, production payments, persistence, or real agent orchestration in this public MVP.
- Live integration functionality must be verified **after** setting credentials in Streamlit Cloud.
