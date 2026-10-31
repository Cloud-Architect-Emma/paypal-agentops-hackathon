# Submission draft — verify event rules and edit as needed

**Project:** PayPal AgentOps — The Control Plane for Trusted Agentic Commerce

**One-liner:** A buyer-first control plane concept that applies spending policies, requires explicit approval, and records explainable decisions before AI-initiated purchases can proceed.

**Problem:** Autonomous shopping agents can streamline commerce, but users need transparent controls over merchant choice, spending limits, and consent.

**Solution:** AgentOps evaluates simulated agent purchase proposals against buyer policy, routes permitted proposals to an explicit approval step, and displays an audit trail of every decision.

**Demo scope:** A standalone Streamlit MVP demonstrating policy gating, buyer approval/rejection, simulated outcomes, and session-only audit history. This public demo intentionally does not execute PayPal transactions or integrate a live AI agent.

**Integration direction:** In a fuller implementation, an authenticated agent would submit purchase intents to AgentOps, which would apply authorization and buyer policy before an isolated PayPal payment service is allowed to execute. Previous PayPal sandbox experiments were carried out separately; they are not part of this demo runtime.

**Links to add before submission:**
- GitHub repository: [ADD URL]
- Deployed demo: [ADD URL]
- Video: [ADD URL]

**Claims to avoid:** "Live PayPal integration in this demo", "production-ready", "real AI agent transactions", "immutable audit trail", "money transferred".
