
"""PayPal Sandbox integration for PayPal AgentOps.

Provides OAuth2 authentication, Orders v2 checkout-order creation,
and read-only order-status lookup.

Order creation uses the PayPal sandbox environment only.
This module does not authorize, capture, refund, or transfer funds.
"""

import base64
import json
import re
from urllib.request import Request, urlopen
from urllib.parse import urlencode

PAYPAL_SANDBOX = "https://api-m.sandbox.paypal.com"
OPENAI_RESPONSES = "https://api.openai.com/v1/responses"

def _request(url, method="GET", headers=None, body=None, timeout=12):
    req = Request(url, data=body, headers=headers or {}, method=method)
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)

def paypal_sandbox_order_status(client_id, client_secret, order_id, request_fn=_request):
    """Read existing sandbox order metadata. NEVER creates or captures an order."""
    if not client_id or not client_secret:
        raise ValueError("PayPal sandbox credentials are not configured")
    if not re.fullmatch(r"[A-Za-z0-9]{8,32}", order_id or ""):
        raise ValueError("Invalid PayPal sandbox order ID")
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    token = request_fn(PAYPAL_SANDBOX + "/v1/oauth2/token", method="POST", headers={"Authorization": "Basic " + basic, "Content-Type": "application/x-www-form-urlencoded"}, body=urlencode({"grant_type":"client_credentials"}).encode())
    access_token = token.get("access_token")
    if not access_token:
        raise ValueError("PayPal sandbox authentication did not return an access token")
    order = request_fn(PAYPAL_SANDBOX + "/v2/checkout/orders/" + order_id, headers={"Authorization": "Bearer " + access_token})
    return {"id":order.get("id"), "status":order.get("status"), "intent":order.get("intent"), "environment":"sandbox", "note":"Read-only lookup; no payment operation executed"}

def ai_purchase_draft(api_key, user_request, model="gpt-4.1-mini", request_fn=_request):
    """Use OpenAI to suggest a proposal; output is untrusted and never bypasses policy."""
    if not api_key: raise ValueError("AI API key is not configured")
    if not (user_request or "").strip(): raise ValueError("Enter a purchase request")
    payload={"model":model,"instructions":"Suggest a concise purchase description and merchant category for a human to review. Never claim to have bought anything, and never approve or execute payments. Output plain text, max 90 words.","input":user_request[:1500],"max_output_tokens":180}
    response=request_fn(OPENAI_RESPONSES,method="POST",headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"},body=json.dumps(payload).encode())
    fragments=[]
    for item in response.get("output",[]):
        for part in item.get("content",[]):
            if part.get("type")=="output_text": fragments.append(part.get("text",""))
    result=" ".join(fragments).strip()
    if not result: raise ValueError("AI response did not include text")
    return result


def paypal_sandbox_create_order(
    client_id, client_secret, proposal_id, amount_gbp,
    request_fn=_request,
):
    """Create a sandbox order only. Never capture or authorize."""
    from decimal import Decimal, InvalidOperation

    if not client_id or not client_secret:
        raise ValueError("PayPal sandbox credentials are missing")

    if not re.fullmatch(r"DEMO-[A-F0-9]{8}", proposal_id or ""):
        raise ValueError("Invalid AgentOps proposal ID")

    try:
        amount = Decimal(str(amount_gbp))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Invalid purchase amount") from exc

    if (
        not amount.is_finite()
        or amount <= 0
        or amount != amount.quantize(Decimal("0.01"))
    ):
        raise ValueError("Invalid GBP amount")

    basic = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    token = request_fn(
        PAYPAL_SANDBOX + "/v1/oauth2/token",
        method="POST",
        headers={
            "Authorization": "Basic " + basic,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body=urlencode({
            "grant_type": "client_credentials"
        }).encode(),
    )

    access_token = token.get("access_token")

    if not access_token:
        raise ValueError("PayPal authentication failed")

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": proposal_id,
                "custom_id": proposal_id,
                "amount": {
                    "currency_code": "GBP",
                    "value": f"{amount:.2f}",
                },
                "description": "AgentOps sandbox approved proposal",
            }
        ],
    }

    order = request_fn(
        PAYPAL_SANDBOX + "/v2/checkout/orders",
        method="POST",
        headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
            "PayPal-Request-Id": proposal_id,
            "Prefer": "return=representation",
        },
        body=json.dumps(payload).encode(),
    )

    order_id = order.get("id")

    if not order_id or not re.fullmatch(
        r"[A-Za-z0-9]{8,32}", order_id
    ):
        raise ValueError("PayPal did not return a valid order ID")

    return {
        "id": order_id,
        "status": order.get("status"),
        "environment": "sandbox",
    }
