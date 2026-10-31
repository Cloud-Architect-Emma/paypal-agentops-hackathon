# PayPal AgentOps — Demo script (under 3 minutes)

**00:00–00:20 — Problem.** “AI can recommend purchases, but it must not spend without buyer policy and explicit consent. AgentOps adds that control plane.” Show the five-tab app.

**00:20–00:50 — Proposal and policy.** In **01 · Agent proposal**, propose £49.99 of Office Supplies with a £100 limit and Office Supplies approved. Show `PENDING_APPROVAL`. Briefly explain that **05 · AI + PayPal sandbox** can generate structured proposals with Gemini, then validate them before policy evaluation.

**00:50–01:20 — Buyer checkpoint.** In **02 · Buyer decision**, explicitly approve the pending proposal. Explain that approval is simulated and does not execute a payment.

**01:20–01:55 — Real PayPal sandbox integration.** Separately confirm **Create PayPal sandbox order (no capture)**. Show the returned real PayPal sandbox Order ID and `CREATED` status. Explain that no funds are authorized or captured.

**01:55–02:25 — Explainable audit.** Open **03 · Audit trail**. Expand the proposal and show `AGENT_PROPOSED`, `POLICY_DECISION`, `BUYER_APPROVED` and `PAYPAL_SANDBOX_ORDER_CREATED`, including UTC timestamps and the linked PayPal Order ID.

**02:25–02:45 — Guardrails.** Demonstrate or reference a £150 request against a £100 limit and an unapproved merchant category; both are blocked. Show that Gemini does not override policy.

**02:45–02:58 — Close.** “AgentOps makes AI-assisted commerce explainable and buyer-controlled: AI proposes, policy decides, people approve, and PayPal sandbox records the checkout order.”

**Recording tips:** Use actual application footage, avoid displaying API secrets, keep the final video below three minutes, and publish it publicly on YouTube for Devpost. If a live API call fails during recording, do not imply it succeeded; use an existing legitimate audit record and state what it demonstrates.

**Live app:** https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/
