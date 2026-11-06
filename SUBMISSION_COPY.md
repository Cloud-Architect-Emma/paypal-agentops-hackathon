# PayPal AgentOps Devpost Submission Copy

## Project name
PayPal AgentOps: The Control Plane for Trusted Agentic Commerce

## Elevator pitch
**AI proposes. Policy decides. Humans approve. PayPal Sandbox creates the checkout order.**

## Inspiration
An AI shopping suggestion is not permission to spend. Buyers need enforceable controls, an explicit approval checkpoint and traceable decisions before a payment-platform action.

## What it does
Google Gemini produces structured purchase proposals. Local validation checks the category, amount and description. A deterministic Python policy engine enforces a buyer's GBP spending limit and allowed merchant categories. Non-compliant proposals are blocked; eligible ones require explicit simulated approval or rejection. Following approval, a separate confirmation creates a **PayPal sandbox checkout order** through Orders v2, without authorizing or capturing funds. UTC audit events link the proposal, policy decision, buyer action and PayPal Order ID; users can export JSON.

## How we built it
- **Python + Streamlit:** Dashboard and buyer workflow.
- **Google Gemini API:** Structured purchase proposals.
- **Deterministic Python policy engine:** Spending and merchant-category controls.
- **PayPal Sandbox REST API:** OAuth2, Orders v2 create-order and read-only order lookup.
- **unittest + GitHub Actions:** Policy unit tests.
- **Streamlit Community Cloud:** Hosted demonstration.

## Challenges
Separating probabilistic AI recommendations from deterministic policies, ensuring buyer approval cannot implicitly trigger payment execution, and distinguishing a created sandbox order from a captured payment.

## Accomplishments
A working proof of concept linking Gemini proposals, deterministic policy decisions, simulated human review, PayPal sandbox order creation and explainable session-based audit events.

## What we learned
AI can draft purchase intent without holding spending authority. Explicit checkpoints and event traceability clarify who or what initiated each stage.

## What's next
Persistent tamper-evident audit storage, verified buyer identities, real-time monitoring, automated alerts, risk analytics and enterprise policy management.

## Honest limitations
Sandbox-only MVP. No actual payment capture or transfer, no authenticated buyer approval, no persistent audit database, no real-time monitoring and no production autonomous commerce.

## Project links
- **Live demo:** https://paypal-agentops-hackathon-eksknbyjh7w4vc8cjb9yiy.streamlit.app/
- **YouTube demo (Public):** https://youtu.be/7R_1syBF8hc
- **Public GitHub:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon
- **Architecture:** https://github.com/Cloud-Architect-Emma/paypal-agentops-hackathon/blob/main/docs/ARCHITECTURE.md
