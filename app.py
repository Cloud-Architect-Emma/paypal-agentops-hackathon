"""Hackathon demo with optional read-only sandbox and AI integrations."""
import json
import streamlit as st
from engine import Policy, new_proposal, resolve
from integrations import paypal_sandbox_order_status, ai_purchase_draft

st.set_page_config(page_title='PayPal AgentOps | Trusted Agentic Commerce', page_icon='🛡️', layout='wide')
st.markdown('''<style>
.block-container{padding-top:2rem;max-width:1150px}
h1,h2,h3{letter-spacing:-.035em}
[data-testid="stMetric"]{border:1px solid #d9dfe7;border-radius:12px;padding:14px}
</style>''', unsafe_allow_html=True)
st.title('🛡️ PayPal AgentOps')
st.caption('The Control Plane for Trusted Agentic Commerce · Hackathon MVP')
st.warning('SIMULATION ONLY — payment execution is disabled. Optional PayPal sandbox order lookup is READ-ONLY; AI suggestions require human review. No captures or transfers.')

if 'txs' not in st.session_state:
    st.session_state.txs = []

with st.sidebar:
    st.header('Demo control plane')
    st.success('Payment execution: DISABLED')
    st.info('Session-only demo data. Browser session reset clears the history.')
    st.markdown('**Demo scenarios**')
    st.markdown('1. £49.99 Office Supplies → approval required\n\n2. £150 Office Supplies → blocked\n\n3. £30 Unknown Merchant → blocked')
    if st.button('Clear demo session', use_container_width=True):
        st.session_state.txs = []
        st.rerun()

t1,t2,t3,t4,t5=st.tabs(['01 · Agent proposal','02 · Buyer decision','03 · Audit trail','04 · Architecture','05 · AI + PayPal sandbox'])
with t1:
    st.subheader('AI agent proposes a purchase')
    st.caption('This simulates an AI agent request. No external agent is invoked.')
    with st.form('proposal'):
        a,b=st.columns(2)
        with a:
            merchant=st.selectbox('Merchant',['Office Supplies','Cloud Tools','Travel Booking','Unknown Merchant'])
            amount=st.number_input('Purchase amount · GBP',min_value=0.01,value=49.99,step=1.0)
            description=st.text_input('Reason for purchase','Purchase supplies for team')
        with b:
            limit=st.number_input('Maximum permitted amount · GBP',min_value=1.0,value=100.0)
            allowed=st.multiselect('Buyer-approved merchants',['Office Supplies','Cloud Tools','Travel Booking'],default=['Office Supplies','Cloud Tools'])
        submit=st.form_submit_button('Evaluate purchase policy',type='primary',use_container_width=True)
    if submit:
        tx=new_proposal(merchant,amount,description,Policy(limit,tuple(allowed)))
        st.session_state.txs.insert(0,tx)
        if tx['status']=='BLOCKED':st.error(f"BLOCKED · {tx['reason']}")
        else:st.success(f"POLICY PASSED · {tx['reason']} Open Buyer decision to approve or reject.")
        st.code(tx['id'])
with t2:
    st.subheader('Human-in-the-loop approval')
    pending=[x for x in st.session_state.txs if x['status']=='PENDING_APPROVAL']
    if not pending:st.info('No proposals pending. Create a policy-compliant proposal first.')
    else:
        ids={x['id']:x for x in pending}
        chosen=st.selectbox('Pending proposal',list(ids),format_func=lambda k:f"{k} · {ids[k]['merchant']} · £{ids[k]['amount']:.2f}")
        tx=ids[chosen]
        st.write(f"**Merchant:** {tx['merchant']} · **Amount:** £{tx['amount']:.2f} · **Reason:** {tx['description']}")
        st.write(f"**Policy:** {tx['reason']}")
        consent=st.checkbox('I explicitly approve this merchant and exact amount.',key='consent_'+chosen)
        c1,c2=st.columns(2)
        with c1:
            if st.button('Approve (simulate only)',type='primary',disabled=not consent,use_container_width=True):
                resolve(tx,True);st.success('Approval recorded. No payment executed.');st.rerun()
        with c2:
            if st.button('Reject proposal',use_container_width=True):
                resolve(tx,False);st.error('Proposal rejected.');st.rerun()
with t3:
    st.subheader('Explainable transaction decisions')
    txs=st.session_state.txs
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Proposals',len(txs))
    c2.metric('Pending',sum(x['status']=='PENDING_APPROVAL' for x in txs))
    c3.metric('Blocked',sum(x['status']=='BLOCKED' for x in txs))
    c4.metric('Simulated approvals',sum(x['status']=='SIMULATED_APPROVED' for x in txs))
    if not txs:st.info('No proposals yet. Create one in Agent proposal.')
    for tx in txs:
        with st.expander(f"{tx['id']} · {tx['merchant']} · £{tx['amount']:.2f} · {tx['status']}"):
            st.write('**Decision:**',tx['reason'])
            st.write('**Purchase reason:**',tx['description'])
            st.dataframe(tx['events'],use_container_width=True,hide_index=True)
            st.download_button('Download this audit record (JSON)',json.dumps(tx,indent=2),file_name=tx['id']+'.json',mime='application/json',key='download_'+tx['id'])
with t4:
    st.subheader('Architecture and integration boundaries')
    st.code('AI agent proposal → AgentOps policy gate → Explicit buyer decision\n                 ↓ blocked             ↓ approved\n             Audit decision     Simulated outcome → Audit events',language='text')
    st.markdown('''**What this demo actually executes:** deterministic local policy evaluation, explicit approval/rejection, and session-scoped audit events.\n\n**What is not executed:** payment creation/capture, Firebase token verification, webhooks, or persistent storage. Optional AI drafting and PayPal sandbox read-only lookup are available only when configured with server-side credentials.\n\n**Production integration concept:** an authenticated agent would submit a purchase proposal; AgentOps would apply tenant/buyer policy and require consent before any separate PayPal execution service is enabled. Payment execution remains intentionally disconnected in this release.\n\n**Earlier sandbox development:** PayPal sandbox API and webhook experiments belong to the separate development backend; this demo does not call or validate those integrations.''')
    st.caption('Designed for a truthful, safe product demonstration—not a production payment system.')

with t5:
    st.subheader('Optional external integrations · safe sandbox mode')
    st.caption('The integrations below use server-side secrets. Neither can initiate or capture a payment.')
    try:
        secrets = st.secrets
        openai_key = secrets.get('OPENAI_API_KEY', '')
        paypal_id = secrets.get('PAYPAL_SANDBOX_CLIENT_ID', '')
        paypal_secret = secrets.get('PAYPAL_SANDBOX_CLIENT_SECRET', '')
    except Exception:
        openai_key = paypal_id = paypal_secret = ''
    st.markdown('#### AI-assisted purchase drafting')
    request_text = st.text_area('Describe what you want an agent to buy', 'Suggest a suitable office supply purchase under £100.')
    if st.button('Generate AI suggestion', disabled=not bool(openai_key)):
        try:
            suggestion = ai_purchase_draft(openai_key, request_text)
            st.session_state.ai_suggestion = suggestion
        except Exception:
            st.error('AI service unavailable. Check server-side API configuration and retry.')
    if 'ai_suggestion' in st.session_state:
        st.info(st.session_state.ai_suggestion)
        st.caption('AI output is advisory only. Enter the merchant and amount in Agent proposal; policy and buyer consent still apply.')
    if not openai_key:
        st.info('AI integration not configured: add OPENAI_API_KEY to Streamlit app secrets to enable live model responses.')
    st.divider()
    st.markdown('#### PayPal sandbox · read-only order status')
    order_id = st.text_input('Existing sandbox order ID', help='An order already created in your separate PayPal sandbox development environment.')
    if st.button('Retrieve sandbox order status', disabled=not bool(paypal_id and paypal_secret)):
        try:
            result = paypal_sandbox_order_status(paypal_id, paypal_secret, order_id)
            st.json(result)
        except ValueError as exc:
            st.warning(str(exc))
        except Exception:
            st.error('Sandbox lookup failed. Verify order ID, credentials, and sandbox access.')
    if not (paypal_id and paypal_secret):
        st.info('PayPal sandbox not configured: add PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_CLIENT_SECRET to Streamlit app secrets.')
    st.caption('Read-only API operations: OAuth token exchange and GET /v2/checkout/orders/{id}. No POST to create/capture/authorize endpoints.')
