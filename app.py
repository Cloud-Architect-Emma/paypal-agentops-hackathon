
"""PayPal AgentOps: AI -> policy -> buyer decision -> audit."""

import json
import logging

import streamlit as st

from ai_proposal import MERCHANT_CATEGORIES
from engine import Policy, new_proposal, resolve, event
from gemini_proposal import generate_ai_proposal
from integrations import paypal_sandbox_order_status


st.set_page_config(
    page_title="PayPal AgentOps | Trusted Agentic Commerce",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top:2rem;max-width:1150px}
    h1,h2,h3 {letter-spacing:-.035em}
    [data-testid="stMetric"] {
        border:1px solid #d9dfe7;
        border-radius:12px;
        padding:14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛡️ PayPal AgentOps")
st.caption(
    "The Control Plane for Trusted Agentic Commerce · Hackathon MVP"
)
st.warning(
    "SIMULATION ONLY — payment execution is disabled. "
    "PayPal sandbox order lookup is READ-ONLY. "
    "AI suggestions require policy checks and human review. "
    "No captures or transfers."
)

if "txs" not in st.session_state:
    st.session_state.txs = []

if "ai_candidate" not in st.session_state:
    st.session_state.ai_candidate = None


def save_proposal(tx):
    """Save a proposal and refresh all tabs."""
    st.session_state.txs.insert(0, tx)
    st.session_state.latest_proposal_id = tx["id"]
    st.rerun()


with st.sidebar:
    st.header("Demo control plane")
    st.success("Payment execution: DISABLED")
    st.info(
        "Session-only demo data. Browser session reset "
        "clears the history."
    )
    st.markdown("**Demo scenarios**")
    st.markdown(
        "1. £49.99 Office Supplies → approval required\n\n"
        "2. £150 Office Supplies → blocked\n\n"
        "3. £30 Unknown Merchant → blocked"
    )

    if st.button("Clear demo session", use_container_width=True):
        st.session_state.txs = []
        st.session_state.ai_candidate = None
        st.session_state.pop("latest_proposal_id", None)
        st.session_state.pop("submission_notice", None)
        st.session_state.pop("ai_suggestion", None)
        st.rerun()


t1, t2, t3, t4, t5 = st.tabs([
    "01 · Agent proposal",
    "02 · Buyer decision",
    "03 · Audit trail",
    "04 · Architecture",
    "05 · AI + PayPal sandbox",
])


# ---------------------------------------------------
# TAB 01 — MANUAL AGENT PROPOSAL
# ---------------------------------------------------

with t1:
    st.subheader("Create a purchase proposal")
    st.caption(
        "Manual simulation is available here. "
        "For live Gemini proposals, use tab 05."
    )

    with st.form("proposal"):
        a, b = st.columns(2)

        with a:
            merchant = st.selectbox(
                "Merchant category",
                MERCHANT_CATEGORIES,
            )
            amount = st.number_input(
                "Purchase amount · GBP",
                min_value=0.01,
                value=49.99,
                step=1.0,
            )
            description = st.text_input(
                "Reason for purchase",
                "Purchase supplies for team",
            )

        with b:
            limit = st.number_input(
                "Maximum permitted amount · GBP",
                min_value=1.0,
                value=100.0,
            )
            allowed = st.multiselect(
                "Buyer-approved merchant categories",
                MERCHANT_CATEGORIES[:-1],
                default=["Office Supplies", "Cloud Tools"],
            )

        submit = st.form_submit_button(
            "Evaluate purchase policy",
            type="primary",
            use_container_width=True,
        )

    if submit:
        tx = new_proposal(
            merchant,
            amount,
            description,
            Policy(limit, tuple(allowed)),
        )
        save_proposal(tx)


# ---------------------------------------------------
# TAB 02 — HUMAN APPROVAL
# ---------------------------------------------------

with t2:
    st.subheader("Human-in-the-loop approval")

    latest_id = st.session_state.get("latest_proposal_id")

    latest_tx = next(
        (
            tx for tx in st.session_state.txs
            if tx["id"] == latest_id
        ),
        None,
    )

    if latest_tx:
        status = latest_tx["status"]

        if status == "PENDING_APPROVAL":
            st.info(
                f"Proposal {latest_id} is awaiting your approval."
            )

        elif status == "SIMULATED_APPROVED":
            st.success(
                f"Proposal {latest_id} was approved in simulation. "
                "No payment was executed."
            )

        elif status == "REJECTED":
            st.warning(
                f"Proposal {latest_id} was rejected by the buyer."
            )

        elif status == "BLOCKED":
            st.error(
                f"Proposal {latest_id} was blocked by policy: "
                f"{latest_tx['reason']}"
            )

    pending = [
        tx for tx in st.session_state.txs
        if tx["status"] == "PENDING_APPROVAL"
    ]

    if not pending:
        st.info(
            "No proposals pending. Create a new proposal "
            "in tab 01 or tab 05."
        )

    else:
        ids = {tx["id"]: tx for tx in pending}

        chosen = st.selectbox(
            "Pending proposal",
            list(ids),
            format_func=lambda key: (
                f"{key} · {ids[key]['merchant']} · "
                f"£{ids[key]['amount']:.2f}"
            ),
        )

        tx = ids[chosen]

        st.write(
            f"**Merchant category:** {tx['merchant']} · "
            f"**Amount:** £{tx['amount']:.2f}"
        )
        st.write(f"**Reason:** {tx['description']}")
        st.write(f"**Policy:** {tx['reason']}")

        st.caption(
            "A merchant category is not a verified seller. "
            "No payment can be initiated in this demo."
        )

        consent = st.checkbox(
            "I explicitly approve this proposed category "
            "and exact amount (simulation only).",
            key="consent_" + chosen,
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                "Approve (simulate only)",
                type="primary",
                disabled=not consent,
                use_container_width=True,
            ):
                resolve(tx, True)
                st.session_state.latest_proposal_id = tx["id"]
                st.rerun()

        with c2:
            if st.button(
                "Reject proposal",
                use_container_width=True,
            ):
                resolve(tx, False)
                st.session_state.latest_proposal_id = tx["id"]
                st.rerun()


# ---------------------------------------------------
# TAB 03 — AUDIT TRAIL
# ---------------------------------------------------

with t3:
    st.subheader("Explainable transaction decisions")

    txs = st.session_state.txs

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Proposals", len(txs))
    c2.metric(
        "Pending",
        sum(
            tx["status"] == "PENDING_APPROVAL"
            for tx in txs
        ),
    )
    c3.metric(
        "Blocked",
        sum(tx["status"] == "BLOCKED" for tx in txs),
    )
    c4.metric(
        "Simulated approvals",
        sum(
            tx["status"] == "SIMULATED_APPROVED"
            for tx in txs
        ),
    )

    if not txs:
        st.info("No proposals recorded yet.")

    for tx in txs:
        with st.expander(
            f"{tx['id']} · {tx['merchant']} · "
            f"£{tx['amount']:.2f} · {tx['status']}"
        ):
            st.write("**Decision:**", tx["reason"])
            st.write("**Purchase reason:**", tx["description"])

            st.dataframe(
                tx["events"],
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "Download this audit record (JSON)",
                json.dumps(tx, indent=2),
                file_name=tx["id"] + ".json",
                mime="application/json",
                key="download_" + tx["id"],
            )


# ---------------------------------------------------
# TAB 04 — ARCHITECTURE
# ---------------------------------------------------

with t4:
    st.subheader("Architecture and integration boundaries")

    st.code(
        "Gemini AI proposal\n"
        "       ↓\n"
        "Validate proposal fields\n"
        "       ↓\n"
        "AgentOps policy evaluation\n"
        "       ↓\n"
        "Blocked OR Pending buyer approval\n"
        "       ↓\n"
        "Human approves or rejects\n"
        "       ↓\n"
        "Simulated outcome + Audit trail",
        language="text",
    )

    st.markdown(
        """
        **What this demo executes:** Gemini generates a
        structured draft. The application validates the
        category, amount and description. The policy engine
        blocks or marks the proposal pending. A buyer can
        approve or reject it.

        **What is not executed:** Payment creation, payment
        capture, Firebase token verification, webhooks or
        persistent storage.

        **Security boundary:** Gemini cannot approve purchases
        or change the policy. Merchant categories are not
        verified merchant identities. Payment execution is
        intentionally disconnected.
        """
    )


# ---------------------------------------------------
# TAB 05 — GEMINI + PAYPAL SANDBOX
# ---------------------------------------------------

with t5:
    st.subheader(
        "Live Gemini → policy evaluation → buyer approval"
    )
    st.caption(
        "Gemini proposes; policy decides; "
        "only a human can approve. No payment is executed."
    )

    try:
        secrets = st.secrets
        gemini_key = secrets.get("GEMINI_API_KEY", "")
        paypal_id = secrets.get(
            "PAYPAL_SANDBOX_CLIENT_ID", ""
        )
        paypal_secret = secrets.get(
            "PAYPAL_SANDBOX_CLIENT_SECRET", ""
        )
    except Exception:
        logging.exception(
            "Could not read Streamlit secrets configuration"
        )
        gemini_key = paypal_id = paypal_secret = ""

    request_text = st.text_area(
        "Describe what you want an agent to buy",
        "Suggest a suitable office supply purchase under £100.",
    )

    with st.form("ai_policy"):
        col1, col2 = st.columns(2)

        with col1:
            ai_limit = st.number_input(
                "Buyer spending limit · GBP",
                min_value=1.0,
                value=100.0,
                key="ai_limit",
            )

        with col2:
            ai_allowed = st.multiselect(
                "Approved merchant categories",
                MERCHANT_CATEGORIES[:-1],
                default=["Office Supplies", "Cloud Tools"],
                key="ai_allowed",
            )

        generate = st.form_submit_button(
            "Generate AI purchase proposal",
            disabled=not bool(gemini_key),
            type="primary",
            use_container_width=True,
        )

    if generate:
        st.session_state.ai_candidate = None

        try:
            proposal = generate_ai_proposal(
                gemini_key,
                request_text,
            )

            st.session_state.ai_candidate = {
                **proposal,
                "request": request_text,
                "policy_limit": ai_limit,
                "policy_allowed": tuple(ai_allowed),
            }

            st.success(
                "Gemini generated a structured proposal. "
                "Review it before policy evaluation."
            )

        except Exception:
            logging.exception(
                "Gemini structured proposal generation failed"
            )
            st.error(
                "Gemini request failed. "
                "Check Streamlit logs."
            )

    candidate = st.session_state.ai_candidate

    if candidate:
        st.markdown("#### Review AI-generated proposal")

        st.write(
            f"**Description:** {candidate['description']}"
        )
        st.write(
            f"**Merchant category:** {candidate['merchant']}"
        )
        st.write(
            f"**Estimated amount:** £{candidate['amount']:.2f}"
        )

        st.caption(
            f"Policy snapshot: "
            f"£{candidate['policy_limit']:.2f} limit; "
            f"approved categories: "
            f"{', '.join(candidate['policy_allowed']) or 'none'}."
        )

        st.warning(
            "Gemini-generated details are unverified estimates. "
            "Submitting evaluates policy; it does not pay."
        )

        if st.button(
            "Submit AI proposal to policy engine",
            type="primary",
            use_container_width=True,
        ):
            tx = new_proposal(
                candidate["merchant"],
                candidate["amount"],
                candidate["description"],
                Policy(
                    candidate["policy_limit"],
                    candidate["policy_allowed"],
                ),
            )

            event(
                tx,
                "AI_GENERATED_PROPOSAL",
                "Structured Gemini proposal submitted for "
                "policy evaluation. No payment executed.",
            )

            st.session_state.ai_candidate = None
            save_proposal(tx)

    if not gemini_key:
        st.info(
            "Add GEMINI_API_KEY to Streamlit secrets "
            "to enable Gemini."
        )

    st.divider()
    st.markdown(
        "#### PayPal sandbox · read-only order status"
    )

    order_id = st.text_input(
        "Existing sandbox order ID",
        help="An order created in your separate "
             "PayPal sandbox development environment.",
    )

    if st.button(
        "Retrieve sandbox order status",
        disabled=not bool(paypal_id and paypal_secret),
    ):
        try:
            result = paypal_sandbox_order_status(
                paypal_id,
                paypal_secret,
                order_id,
            )
            st.json(result)

        except ValueError as exc:
            st.warning(str(exc))

        except Exception:
            logging.exception(
                "PayPal sandbox order lookup failed"
            )
            st.error(
                "Sandbox lookup failed. "
                "Check credentials and order ID."
            )

    if not (paypal_id and paypal_secret):
        st.info(
            "Add PAYPAL_SANDBOX_CLIENT_ID and "
            "PAYPAL_SANDBOX_CLIENT_SECRET "
            "to Streamlit secrets."
        )

    st.caption(
        "Read-only API operations: OAuth token exchange "
        "and GET /v2/checkout/orders/{id}. "
        "No payment creation, authorization or capture."
    )
