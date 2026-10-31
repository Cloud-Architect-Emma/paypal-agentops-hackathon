# PayPal AgentOps — 3-minute demo guide

1. Show the policy gate: £49.99 Office Supplies with £100 limit → pending buyer approval.
2. Explicitly approve; show the audit trail and PAYMENT_NOT_EXECUTED.
3. Show £150 blocked and Unknown Merchant blocked.
4. Open **AI + PayPal sandbox** tab. If secrets are configured, generate a real AI suggestion and retrieve an existing PayPal sandbox order ID read-only. If not configured, do not claim these integrations were executed.
5. Explain the architecture: AI suggestion is advisory; policy and buyer approval remain authoritative; sandbox lookup is read-only; payment execution is disabled.

**Live demo:** https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/
