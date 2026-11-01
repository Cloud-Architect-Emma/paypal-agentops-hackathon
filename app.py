"""PayPal AgentOps hackathon MVP: AI -> policy -> buyer decision -> audit."""
import json
import logging

import streamlit as st

from ai_proposal import MERCHANT_CATEGORIES
from engine import Policy, new_proposal, resolve, event
from gemini_proposal import generate_ai_proposal
from integrations import paypal_sandbox_order_status, paypal_sandbox_create_order

st.set_page_config(page_title='PayPal AgentOps | Trusted Agentic Commerce', page_icon='🛡️', layout='wide')
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {--ink:#eaf3fa;--muted:#9db2c4;--teal:#32d8be;--edge:#244258;--panel:#10283c}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {font-family:'DM Sans',sans-serif}
[data-testid="stAppViewContainer"] {background:radial-gradient(ellipse 1000px 520px at 82% -15%,#16465b 0%,transparent 65%),#071a2a;color:#eaf3fa}
[data-testid="stSidebar"] {background:#0a2032;border-right:1px solid #254155}
[data-testid="stSidebar"] * {color:#e4eff6}
.block-container{padding-top:1.4rem;max-width:1370px;padding-bottom:4rem}
h1,h2,h3 {font-family:'Manrope',sans-serif;letter-spacing:-.045em;color:#f2fbff}
h1 {font-size:2.1rem!important} h2{font-size:1.55rem!important} h3{font-size:1.2rem!important}
p, label {line-height:1.65}
[data-testid="stMetric"]{background:linear-gradient(145deg,#112e43,#0b2335);border:1px solid #28485c;border-radius:17px;padding:19px 22px;box-shadow:0 12px 25px #04131e44}
[data-testid="stMetricLabel"]{color:#9fb9ca}[data-testid="stMetricValue"]{color:#f2fbff;font-family:'Manrope',sans-serif}
[data-testid="stForm"], [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"]>div {border-radius:15px}
[data-testid="stForm"]{background:#0e273b;border:1px solid #29475a;padding:19px}
[data-testid="stExpander"]{background:#0d2639;border:1px solid #29475a}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;flex-wrap:wrap}
[data-testid="stTabs"] button[role="tab"]{background:#102b40;border:1px solid #294b60;border-radius:11px;padding:9px 15px;color:#b6cfde}
[data-testid="stTabs"] button[aria-selected="true"]{background:#155267;color:#fff;border-color:#2acbb7}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{background:#2bd4bb;color:#062333;border:0;font-weight:800;border-radius:10px}
.stButton button,.stDownloadButton button{border-radius:10px}
[data-testid="stAlert"]{border-radius:12px}
.hero{border:1px solid #29566a;border-radius:23px;padding:32px 36px;background:linear-gradient(115deg,#103c53,#10273d 65%,#102f43);margin:12px 0 25px;box-shadow:0 20px 50px #04121e55}
.hero-kicker{font-size:12px;font-weight:800;letter-spacing:2.5px;color:#46e2c9;text-transform:uppercase}
.hero-title{font:800 clamp(28px,3.2vw,45px)/1.18 'Manrope',sans-serif;letter-spacing:-1.7px;color:#fff;margin:14px 0}
.hero-copy{font-size:16px;line-height:1.7;color:#bad0df;max-width:720px}
.pill{display:inline-block;border:1px solid #397485;border-radius:30px;padding:6px 12px;font-size:12px;color:#6aefda;background:#103e4d;margin-top:15px}
.section-kicker{font-size:12px;color:#46d9c3;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;margin:25px 0 8px}
.feature-card{min-height:158px;border:1px solid #2a4a5f;border-radius:17px;background:linear-gradient(140deg,#123147,#0b2335);padding:23px;margin-bottom:15px}
.feature-icon{font-size:24px}.feature-title{font:700 18px 'Manrope',sans-serif;color:#f4fbff;margin:11px 0 8px}.feature-copy{color:#aec5d4;font-size:14px;line-height:1.6}
.flow-node{border:1px solid #31576a;border-radius:15px;background:#113146;padding:17px 12px;text-align:center;min-height:120px}
.flow-node strong{display:block;color:#f5fcff;font-size:15px;margin:8px 0}.flow-node span{color:#a8c6d5;font-size:12px}
.safe-banner{background:#0d3540;border:1px solid #237b75;border-radius:12px;padding:13px 17px;color:#b8f2e8;font-size:13px;margin:14px 0 22px}
@media(max-width:760px){.hero{padding:23px}.hero-title{font-size:28px}.block-container{padding-top:1rem}}

/* Explicit contrast for text fields, including BaseWeb inner controls. */

/* High-contrast, visible typing controls across Streamlit/BaseWeb versions. */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="input"] input {
    background: #ffffff !important;
    color: #10283c !important;
    -webkit-text-fill-color: #10283c !important;
    caret-color: #10283c !important;
    opacity: 1 !important;
    font-size: 16px !important;
}
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-baseweb="textarea"] > div,
[data-baseweb="input"] > div {
    background-color: #ffffff !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-baseweb="textarea"] textarea:focus,
[data-baseweb="input"] input:focus {
    outline: 2px solid #32d8be !important;
    outline-offset: 1px !important;
    caret-color: #10283c !important;
}
[data-baseweb="textarea"] textarea::placeholder,
[data-baseweb="input"] input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}


/* Audit trail: dark headers with readable white text */
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {
    background-color: #102b40 !important;
    color: #ffffff !important;
}

[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary svg {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stExpander"] summary:hover {
    background-color: #19445a !important;
}

[data-testid="stExpander"] summary:focus-visible {
    outline: 2px solid #32d8be !important;
}

/* AGENTOPS home: original large shield/heading styling, but clickable. */
[data-testid="stSidebar"] .st-key-go_home button {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    color: #f2fbff !important;
    -webkit-text-fill-color: #f2fbff !important;
    padding: 6px 0 !important;
    min-height: 42px !important;
    justify-content: flex-start !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .st-key-go_home button p {
    color: #f2fbff !important;
    -webkit-text-fill-color: #f2fbff !important;
    font: 800 22px/1.3 'Manrope', sans-serif !important;
}
[data-testid="stSidebar"] .st-key-go_home button:hover {
    background: #123147 !important;
}
[data-testid="stSidebar"] .st-key-go_home button:focus-visible {
    outline: 2px solid #32d8be !important;
}
/* Keep the navigation in the original dark-themed visual family. */
[data-testid="stRadio"] [role="radiogroup"] {gap: 8px; flex-wrap: wrap;}
[data-testid="stRadio"] [role="radiogroup"] label {
    border: 1px solid #294b60 !important;
    background: #102b40 !important;
    border-radius: 11px !important;
    padding: 8px 12px !important;
}
[data-testid="stRadio"] [role="radiogroup"] label p {
    color: #eaf3fa !important;
    -webkit-text-fill-color: #eaf3fa !important;
}
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background: #155267 !important;
    border-color: #32d8be !important;
}
/* The expander header must never become white with white text. */
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: #102b40 !important;
    color: #f2fbff !important;
}
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p {
    color: #f2fbff !important;
    -webkit-text-fill-color: #f2fbff !important;
}

/* All interactive sidebar controls: dark, readable and no white glare. */
[data-testid="stSidebar"] .stButton button {
    background: #102b40 !important;
    color: #f2fbff !important;
    -webkit-text-fill-color: #f2fbff !important;
    border: 1px solid #31576a !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
    text-align: left !important;
    white-space: normal !important;
    height: auto !important;
    min-height: 42px !important;
}
[data-testid="stSidebar"] .stButton button p {
    color: #f2fbff !important;
    -webkit-text-fill-color: #f2fbff !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #19445a !important;
    border-color: #32d8be !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton button:focus-visible {
    outline: 2px solid #32d8be !important;
    box-shadow: none !important;
}
/* AGENTOPS logo retains its original large appearance. */
[data-testid="stSidebar"] .st-key-go_home button {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 6px 0 !important;
}
[data-testid="stSidebar"] .st-key-go_home button p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font: 800 22px/1.3 'Manrope', sans-serif !important;
}
[data-testid="stSidebar"] .st-key-go_home button:hover {
    background: #123147 !important;
    border: 0 !important;
}

</style>""",unsafe_allow_html=True)

if 'txs' not in st.session_state:
    st.session_state.txs = []
if 'ai_candidate' not in st.session_state:
    st.session_state.ai_candidate = None


def open_page(page_name):
    st.session_state['agentops_page'] = page_name


def run_demo(merchant, amount, description, destination):
    """Run the same deterministic policy engine as manual proposals."""
    demo_policy = Policy(100.0, ('Office Supplies', 'Cloud Tools'))
    tx = new_proposal(merchant, amount, description, demo_policy)
    st.session_state.txs.insert(0, tx)
    st.session_state.latest_proposal_id = tx['id']
    open_page(destination)


with st.sidebar:
    if st.button('🛡️ AGENTOPS', key='go_home', use_container_width=True):
        open_page('◈ Overview')
        st.rerun()

    st.caption('TRUSTED AGENTIC COMMERCE')
    st.divider()
    st.markdown('**ENVIRONMENT**')
    if st.button('● PayPal Sandbox', key='sidebar_environment', use_container_width=True):
        open_page('05 · AI + PayPal')
        st.rerun()

    st.markdown('**EXECUTION POLICY**')
    if st.button('🛡 Order creation only · No captures or transfers', key='sidebar_policy', use_container_width=True):
        open_page('04 · Architecture')
        st.rerun()

    st.divider()
    st.markdown('**DEMO SCENARIOS**')
    if st.button('✓ £49.99 Office Supplies — approval required', key='demo_approved', use_container_width=True):
        run_demo('Office Supplies', 49.99, 'Demo: purchase office supplies', '02 · Approvals')
        st.rerun()

    if st.button('⊘ £150 Office Supplies — blocked', key='demo_amount_blocked', use_container_width=True):
        run_demo('Office Supplies', 150.0, 'Demo: purchase exceeds the £100 limit', '03 · Audit trail')
        st.rerun()

    if st.button('⊘ Unknown Merchant — blocked', key='demo_merchant_blocked', use_container_width=True):
        run_demo('Unknown Merchant', 49.99, 'Demo: merchant category not approved', '03 · Audit trail')
        st.rerun()

    st.divider()
    st.caption('Data lives in this Streamlit session. Reset clears local demo history, not PayPal sandbox orders.')
    if st.button('↺ Reset demo session', key='reset_demo_session', use_container_width=True):
        st.session_state.txs = []
        st.session_state.ai_candidate = None
        for key in ('ai_suggestion', 'submission_notice', 'latest_proposal_id', 'sandbox_order_choice'):
            st.session_state.pop(key, None)
        for key in list(st.session_state.keys()):
            if key.startswith(('consent_', 'order_consent_')):
                del st.session_state[key]
        open_page('◈ Overview')
        st.rerun()

st.markdown('<div class="hero-kicker">PAYPAL AGENTOPS / CONTROL PLANE</div>', unsafe_allow_html=True)
st.title('Trusted Agentic Commerce')
st.caption('AI-assisted purchasing · Buyer policy enforcement · Human-in-the-loop approval')
st.markdown('<div class="safe-banner">🔒 SANDBOX ONLY &nbsp;·&nbsp; Explicit buyer confirmation required &nbsp;·&nbsp; No authorization, captures or transfers</div>',unsafe_allow_html=True)

pages = [
    '◈ Overview', '01 · Proposals', '02 · Approvals',
    '03 · Audit trail', '04 · Architecture', '05 · AI + PayPal',
]
if st.session_state.get('agentops_page') not in pages:
    st.session_state['agentops_page'] = pages[0]
page = st.radio(
    'Navigate AgentOps', pages, horizontal=True,
    key='agentops_page', label_visibility='collapsed',
)

if page == pages[0]:
    st.markdown("""<div class="hero">
      <div class="hero-kicker">THE COMMERCE TRUST LAYER</div>
      <div class="hero-title">Give AI the ability to propose.<br>Keep people in control.</div>
      <div class="hero-copy">An explainable control plane for agent-driven purchases. Gemini drafts the request, deterministic policy decides what is allowed, and buyers retain final approval before a PayPal sandbox order can be created.</div>
      <span class="pill">● Live sandbox integration</span> &nbsp; <span class="pill">✓ Human approval required</span>
    </div>""",unsafe_allow_html=True)
    txs_home=st.session_state.txs
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Total proposals',len(txs_home))
    c2.metric('Awaiting review',sum(x['status']=='PENDING_APPROVAL' for x in txs_home))
    c3.metric('Policy blocked',sum(x['status']=='BLOCKED' for x in txs_home))
    c4.metric('Sandbox orders',sum(bool(x.get('paypal_order_id')) for x in txs_home))
    st.markdown('<div class="section-kicker">CORE CAPABILITIES</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:
        st.markdown('<div class="feature-card"><div class="feature-icon">✦</div><div class="feature-title">AI Purchase Intelligence</div><div class="feature-copy">Gemini produces structured proposals. Suggestions are validated before entering the policy engine.</div></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="feature-card"><div class="feature-icon">🛡</div><div class="feature-title">Deterministic Policy</div><div class="feature-copy">Buyer-defined amount limits and approved merchant categories prevent non-compliant requests.</div></div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="feature-card"><div class="feature-icon">✓</div><div class="feature-title">Human-Governed Checkout</div><div class="feature-copy">A separate buyer confirmation is required to create a PayPal sandbox order; no capture occurs.</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">RECENT ACTIVITY</div>',unsafe_allow_html=True)
    if txs_home:
        for tx in txs_home[:5]:
            left,right=st.columns([4,1])
            with left: st.markdown(f"**{tx['id']}** · {tx['merchant']} · £{tx['amount']:.2f}")
            with right: st.caption(tx['status'].replace('_',' '))
            st.divider()
    else:
        st.info('No activity yet. Open **01 · Proposals** to create your first purchase request, or **05 · AI + PayPal** to generate one with Gemini.')
    st.caption('Session-only audit history · Sandbox orders are not payments · No real money moves')

if page == pages[1]:
    st.markdown('<div class="section-kicker">PURCHASE INTELLIGENCE</div>',unsafe_allow_html=True)
    st.subheader('Create a purchase proposal')
    st.caption('Manual simulation is available here. For a live Gemini-generated proposal, use tab 05.')
    with st.form('proposal'):
        a, b = st.columns(2)
        with a:
            merchant = st.selectbox('Merchant', MERCHANT_CATEGORIES)
            amount = st.number_input('Purchase amount · GBP', min_value=0.01, value=49.99, step=1.0)
            description = st.text_input('Reason for purchase', 'Purchase supplies for team')
        with b:
            limit = st.number_input('Maximum permitted amount · GBP', min_value=1.0, value=100.0)
            allowed = st.multiselect('Buyer-approved merchant categories', MERCHANT_CATEGORIES[:-1], default=['Office Supplies', 'Cloud Tools'])
        submit = st.form_submit_button('Evaluate purchase policy', type='primary', use_container_width=True)
    if submit:
        tx = new_proposal(merchant, amount, description, Policy(limit, tuple(allowed)))
        st.session_state.txs.insert(0, tx)
        st.session_state.latest_proposal_id = tx['id']
        st.rerun()

if page == pages[2]:
    st.markdown('<div class="section-kicker">BUYER CONTROL</div>',unsafe_allow_html=True)
    st.subheader('Human-in-the-loop approval')
    latest_id = st.session_state.get('latest_proposal_id')
    latest = next((x for x in st.session_state.txs if x['id'] == latest_id), None)
    if latest:
        if latest['status'] == 'PENDING_APPROVAL':
            st.info(f"Proposal {latest_id} awaits human approval.")
        elif latest['status'] == 'SIMULATED_APPROVED':
            st.success(f"Proposal {latest_id} was approved. No payment captured.")
        elif latest['status'] == 'BLOCKED':
            st.warning(f"Proposal {latest_id} blocked: {latest['reason']}")
        elif latest['status'] == 'REJECTED':
            st.warning(f"Proposal {latest_id} rejected by buyer.")
    pending = [x for x in st.session_state.txs if x['status'] == 'PENDING_APPROVAL']
    if not pending:
        st.info('No proposals pending. Create a policy-compliant proposal in tab 01 or tab 05.')
    else:
        ids = {x['id']: x for x in pending}
        chosen = st.selectbox('Pending proposal', list(ids), format_func=lambda k: f"{k} · {ids[k]['merchant']} · £{ids[k]['amount']:.2f}")
        tx = ids[chosen]
        st.write(f"**Merchant category:** {tx['merchant']} · **Amount:** £{tx['amount']:.2f} · **Reason:** {tx['description']}")
        st.write(f"**Policy:** {tx['reason']}")
        st.caption('A merchant category is not a verified seller. Approval does not initiate or capture payment.')
        consent = st.checkbox('I explicitly approve this proposed category and exact amount (simulation only).', key='consent_' + chosen)
        c1, c2 = st.columns(2)
        with c1:
            if st.button('Approve (simulate only)', type='primary', disabled=not consent, use_container_width=True):
                resolve(tx, True)
                st.session_state.latest_proposal_id = tx['id']
                st.rerun()
        with c2:
            if st.button('Reject proposal', use_container_width=True):
                resolve(tx, False)
                st.session_state.latest_proposal_id = tx['id']
                st.rerun()


    st.divider()
    st.subheader('Create PayPal sandbox order after approval')
    st.caption('Separate explicit confirmation is required. This creates an unapproved sandbox checkout order only; it does not authorize or capture funds.')
    try:
        sandbox_id = st.secrets.get('PAYPAL_SANDBOX_CLIENT_ID', '')
        sandbox_secret = st.secrets.get('PAYPAL_SANDBOX_CLIENT_SECRET', '')
    except Exception:
        sandbox_id = sandbox_secret = ''
    approved = {x['id']: x for x in st.session_state.txs if x['status'] == 'SIMULATED_APPROVED'}
    if not approved:
        st.info('No approved proposals. Approve a policy-compliant proposal first.')
    else:
        selected_id = st.selectbox('Approved proposal', list(approved), format_func=lambda k: f"{k} · {approved[k]['merchant']} · £{approved[k]['amount']:.2f}")
        selected = approved[selected_id]
        st.write(f"**Amount:** £{selected['amount']:.2f} · **Category:** {selected['merchant']}")
        if selected.get('paypal_order_id'):
            st.success('PayPal sandbox order created; no payment captured.')
            st.code(selected['paypal_order_id'])
            st.write('**PayPal order status:**', selected.get('paypal_order_status', 'Unknown'))
        else:
            consent_order = st.checkbox('I explicitly confirm creation of a PayPal SANDBOX order for this exact amount. No payment will be captured.', key='order_consent_' + selected_id)
            if st.button('Create PayPal sandbox order (no capture)', type='primary', disabled=not (consent_order and sandbox_id and sandbox_secret), use_container_width=True):
                if selected['status'] != 'SIMULATED_APPROVED' or selected.get('paypal_order_id'):
                    st.error('This proposal is not eligible for a new sandbox order.')
                else:
                    try:
                        result = paypal_sandbox_create_order(sandbox_id, sandbox_secret, selected['id'], selected['amount'])
                        selected['paypal_order_id'] = result['id']
                        selected['paypal_order_status'] = result['status']
                        event(selected, 'PAYPAL_SANDBOX_ORDER_CREATED', f"PayPal Order ID: {result['id']}; status: {result['status']}; sandbox only; no capture.")
                        st.rerun()
                    except Exception:
                        logging.exception('PayPal sandbox order creation failed; inspect logs before retrying')
                        st.error('Order creation could not be confirmed. Check Streamlit logs before retrying; do not retry blindly.')
    if not (sandbox_id and sandbox_secret):
        st.info('Set PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET in Streamlit secrets.')

if page == pages[3]:
    st.markdown('<div class="section-kicker">TRANSACTION OBSERVABILITY</div>',unsafe_allow_html=True)
    st.subheader('Explainable transaction decisions')
    txs = st.session_state.txs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Proposals', len(txs))
    c2.metric('Pending', sum(x['status'] == 'PENDING_APPROVAL' for x in txs))
    c3.metric('Blocked', sum(x['status'] == 'BLOCKED' for x in txs))
    c4.metric('Simulated approvals', sum(x['status'] == 'SIMULATED_APPROVED' for x in txs))
    if not txs:
        st.info('No proposals yet. Create one in Agent proposal or AI + PayPal sandbox.')
    for tx in txs:
        with st.expander(f"{tx['id']} · {tx['merchant']} · £{tx['amount']:.2f} · {tx['status']}"):
            st.write('**Decision:**', tx['reason'])
            st.write('**Purchase reason:**', tx['description'])
            st.write('**AgentOps proposal ID:**', tx['id'])
            st.write('**PayPal sandbox Order ID:**', tx.get('paypal_order_id') or 'Not created')
            st.write('**PayPal sandbox status:**', tx.get('paypal_order_status') or 'Not applicable')
            st.markdown('**Decision timeline**')
            for item in tx['events']:
                st.markdown(f"**{item['type'].replace('_', ' ').title()}** · `{item['at']}`")
                st.caption(item['detail'])
            with st.expander('View raw audit events'):
                st.dataframe(tx['events'], use_container_width=True, hide_index=True)
            st.download_button('Download this audit record (JSON)', json.dumps(tx, indent=2), file_name=tx['id'] + '.json', mime='application/json', key='download_' + tx['id'])

if page == pages[4]:
    st.markdown('<div class="section-kicker">SYSTEM DESIGN</div>',unsafe_allow_html=True)
    st.subheader('Architecture and integration boundaries')
    st.markdown('### Execution policy')
    st.info('PayPal Sandbox checkout orders are created only after policy evaluation, simulated buyer approval, and a separate explicit confirmation.')
    st.markdown("""**Sidebar demo policy:** £100 maximum per proposal. Approved categories: Office Supplies and Cloud Tools.

**Blocked requests:** Amounts above £100 or merchant categories outside the allowlist.

**Payment restrictions:** No authorization, capture, refund, or transfer operations are implemented.

**Audit:** Proposal and decision events are recorded in the current Streamlit session, not a persistent database.""")
    st.caption('A layered trust boundary separates AI recommendations, deterministic decisions and sandbox API access.')
    stages=[('✦','Gemini AI','Structured proposal'),('▣','Validation','Schema + amount'),('🛡','Policy engine','Limit + allowlist'),('✓','Buyer review','Approve / reject'),('◎','PayPal Sandbox','Create order only')]
    columns=st.columns(5)
    for column,(symbol,name,desc) in zip(columns,stages):
        with column:
            st.markdown(f'<div class="flow-node"><div style="font-size:22px;color:#45dfc8">{symbol}</div><strong>{name}</strong><span>{desc}</span></div>',unsafe_allow_html=True)
    st.markdown('**Decision branches:** Invalid or non-compliant requests → `BLOCKED` + audit event. Buyer rejection → `REJECTED` + audit event. Buyer approval → optional, separately confirmed sandbox order creation + audit event.')
    st.divider()
    st.markdown('''**What this demo executes:** Gemini generates a structured draft; the application validates its category, amount and description; the deterministic policy engine blocks or marks it pending; a buyer can approve or reject a pending proposal; all decisions are recorded in session-scoped audit events.

**PayPal integration:** After policy checks and buyer approval, a separately confirmed action can create a sandbox checkout order. Order lookup is read-only. No authorization, capture, Firebase token verification, webhooks or persistent storage.

**Security boundary:** Gemini cannot approve purchases or change the policy. AI-generated categories are not verified merchant identities, and the approval is only simulated. No capture or authorization service is connected.''')
    st.caption('Designed for a truthful, safe hackathon demonstration—not a production payment system.')

if page == pages[5]:
    st.markdown('<div class="section-kicker">LIVE INTEGRATIONS</div>',unsafe_allow_html=True)
    st.subheader('Live Gemini → policy evaluation → buyer approval')
    st.caption('Gemini proposes; your policy decides; only a human can approve. No payment is executed.')
    try:
        secrets = st.secrets
        gemini_key = secrets.get('GEMINI_API_KEY', '')
        paypal_id = secrets.get('PAYPAL_SANDBOX_CLIENT_ID', '')
        paypal_secret = secrets.get('PAYPAL_SANDBOX_CLIENT_SECRET', '')
    except Exception:
        logging.exception('Could not read Streamlit secrets configuration')
        gemini_key = paypal_id = paypal_secret = ''

    request_text = st.text_area('Describe what you want an agent to buy', 'Suggest a suitable office supply purchase under £100.')
    with st.form('ai_policy'):
        col1, col2 = st.columns(2)
        with col1:
            ai_limit = st.number_input('Buyer spending limit · GBP', min_value=1.0, value=100.0, key='ai_limit')
        with col2:
            ai_allowed = st.multiselect('Approved merchant categories', MERCHANT_CATEGORIES[:-1], default=['Office Supplies', 'Cloud Tools'], key='ai_allowed')
        generate = st.form_submit_button('Generate AI purchase proposal', disabled=not bool(gemini_key), type='primary', use_container_width=True)
    if generate:
        st.session_state.ai_candidate = None
        try:
            proposal = generate_ai_proposal(gemini_key, request_text)
            st.session_state.ai_candidate = {
                **proposal,
                'request': request_text,
                'policy_limit': ai_limit,
                'policy_allowed': tuple(ai_allowed),
            }
            st.success('Gemini generated a structured proposal. Review it before sending it to policy evaluation.')
        except Exception:
            logging.exception('Gemini structured proposal generation failed')
            st.error('Gemini request failed. Check Streamlit application logs for the detailed error.')

    candidate = st.session_state.ai_candidate
    if candidate:
        st.markdown('#### Review AI-generated proposal')
        st.write(f"**Description:** {candidate['description']}")
        st.write(f"**Merchant category:** {candidate['merchant']}")
        st.write(f"**Estimated amount:** £{candidate['amount']:.2f}")
        st.caption(f"Policy snapshot: £{candidate['policy_limit']:.2f} limit; approved categories: {', '.join(candidate['policy_allowed']) or 'none'}.")
        st.warning('Gemini-generated details are unverified estimates. Submitting runs the policy engine; it does not approve or pay.')
        if st.button('Submit AI proposal to policy engine', type='primary', use_container_width=True):
            tx = new_proposal(candidate['merchant'], candidate['amount'], candidate['description'], Policy(candidate['policy_limit'], candidate['policy_allowed']))
            event(tx, 'AI_GENERATED_PROPOSAL', 'Structured Gemini proposal validated and submitted for policy evaluation. AI did not approve or execute payment.')
            st.session_state.txs.insert(0, tx)
            st.session_state.ai_candidate = None
            st.session_state.latest_proposal_id = tx['id']
            st.rerun()
    if not gemini_key:
        st.info('Add GEMINI_API_KEY to Streamlit app secrets to enable live model responses.')

    st.divider()
    st.markdown('#### PayPal sandbox · read-only order status')
    known_orders = [x for x in st.session_state.txs if x.get('paypal_order_id')]
    if known_orders:
        st.caption('Choose an Order ID generated by this app, or paste another existing PayPal sandbox Order ID.')
        selected_order = st.selectbox('Created sandbox orders', known_orders, format_func=lambda x: f"{x['paypal_order_id']} · {x['id']}", key='sandbox_order_choice')
        default_order_id = selected_order['paypal_order_id']
    else:
        default_order_id = ''
    order_id = st.text_input('PayPal sandbox Order ID (not DEMO- ID)', value=default_order_id, help='Use the PayPal Order ID shown in the Audit trail after successful sandbox order creation.')
    if st.button('Retrieve sandbox order status', disabled=not bool(paypal_id and paypal_secret)):
        try:
            result = paypal_sandbox_order_status(paypal_id, paypal_secret, order_id)
            st.json(result)
        except ValueError as exc:
            st.warning(str(exc))
        except Exception:
            logging.exception('PayPal sandbox order lookup failed')
            st.error('Sandbox lookup failed. Verify order ID, credentials, and sandbox access.')
    if not (paypal_id and paypal_secret):
        st.info('Add PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET to Streamlit app secrets for read-only lookup.')
    st.caption('Read-only API operations: OAuth token exchange and GET /v2/checkout/orders/{id}. POST creates an order only after approval and separate confirmation; GET retrieves status. No authorize/capture calls.')
