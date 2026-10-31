# Suggested 2–3 minute demo video

**0:00–0:25 — Problem.** "AI agents can shop on our behalf, but who enforces spending limits and obtains explicit buyer approval before money moves?"

**0:25–0:45 — Solution.** "AgentOps is a proposed control plane for trusted agentic commerce. This hackathon MVP is a standalone simulation of the policy and approval experience. No payment executes in this demo."

**0:45–1:20 — Allowed purchase.** In Agent proposal choose Office Supplies, £49.99, £100 limit, approved merchant. Click Evaluate. Point out policy pass and approval requirement.

**1:20–1:45 — Human consent.** Open Buyer decision. Show merchant and exact amount; tick explicit approval; approve. Say "This records a simulated approval, not a PayPal charge."

**1:45–2:10 — Audit trail.** Open Audit trail. Expand transaction and show policy decision, buyer approval, and PAYMENT_NOT_EXECUTED. Download JSON if useful.

**2:10–2:35 — Guardrails.** Return to Agent proposal. Set £150, limit £100; show block. Optionally demonstrate Unknown Merchant block.

**2:35–3:00 — Vision.** Open Architecture. Explain future integration boundaries: authenticated agent, buyer policy, explicit consent, separate gated PayPal execution. "The core experience is demonstrable today; real payments are intentionally disabled."

**Before recording:** use a clean browser tab, reset demo session, check all flows, turn off notifications, zoom to readable size. Avoid showing secrets or personal details.
