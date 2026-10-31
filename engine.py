"""Pure, side-effect-free demo policy engine. No network or payment APIs."""
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

@dataclass(frozen=True)
class Policy:
    limit_gbp: float
    approved_merchants: tuple[str, ...]

def decide(amount: float, merchant: str, policy: Policy) -> tuple[str, str]:
    if amount <= 0:
        return 'BLOCKED', 'Purchase amount must be positive.'
    if amount > policy.limit_gbp:
        return 'BLOCKED', f'Amount exceeds the £{policy.limit_gbp:.2f} spending limit.'
    if merchant not in policy.approved_merchants:
        return 'BLOCKED', 'Merchant is not approved by the buyer policy.'
    return 'PENDING_APPROVAL', 'Policy passed. Explicit buyer approval is required.'

def new_proposal(merchant: str, amount: float, description: str, policy: Policy) -> dict:
    status, reason = decide(amount, merchant, policy)
    tx = dict(id='DEMO-' + uuid4().hex[:8].upper(), merchant=merchant,
              amount=round(float(amount), 2), currency='GBP', description=description,
              status=status, reason=reason, events=[])
    event(tx, 'AGENT_PROPOSED', 'Simulated AI agent purchase request created.')
    event(tx, 'POLICY_DECISION', reason)
    return tx

def event(tx: dict, name: str, message: str) -> None:
    tx['events'].append(dict(at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                             type=name, detail=message))

def resolve(tx: dict, approved: bool) -> None:
    if tx['status'] != 'PENDING_APPROVAL':
        raise ValueError('Only pending proposals can be decided.')
    if approved:
        tx['status'] = 'SIMULATED_APPROVED'
        tx['reason'] = 'Buyer explicitly approved this proposed purchase.'
        event(tx, 'BUYER_APPROVED', tx['reason'])
        event(tx, 'PAYMENT_NOT_EXECUTED', 'Simulation only; no PayPal request or funds transfer.')
    else:
        tx['status'] = 'REJECTED'
        tx['reason'] = 'Buyer rejected this proposed purchase.'
        event(tx, 'BUYER_REJECTED', tx['reason'])
