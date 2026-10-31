# PayPal AgentOps — Hackathon Submission

**Project:** PayPal AgentOps — The Control Plane for Trusted Agentic Commerce

**One-liner:** A buyer-first control plane concept that applies spending policies, requires explicit approval, and records explainable decisions before AI-initiated purchases can proceed.

**Problem:** Autonomous shopping agents can streamline commerce, but users need transparent controls over merchant choice, spending limits, and consent.

**Solution:** AgentOps evaluates simulated agent purchase proposals against buyer policy, routes permitted proposals to an explicit approval step, and displays an audit trail of every decision.

**Demo scope:** A standalone Streamlit MVP demonstrating policy gating, buyer approval/rejection, simulated outcomes, and session-only audit history. This public demo intentionally does not execute PayPal transactions or integrate a live AI agent.

**Integration direction:** In a fuller implementation, an authenticated agent would submit purchase intents to AgentOps, which would apply authorization and buyer policy before an isolated PayPal payment service is allowed to execute. Previous PayPal sandbox experiments were carried out separately; they are not part of this demo runtime.

**Project links:**
- **Live interactive demo:** https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/
- **GitHub repository:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon
- **Demo recording guide:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon/blob/main/DEMO_SCRIPT.md

**Video status:** The demo recording has not yet been published. The live interactive demo and source code are available using the verified links above. The recording URL can be added after publication.

**Claims to avoid:** "Live PayPal integration in this demo", "production-ready", "real AI agent transactions", "immutable audit trail", "money transferred".
