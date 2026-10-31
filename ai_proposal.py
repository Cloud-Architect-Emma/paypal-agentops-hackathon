"""Validate Gemini proposals before passing them to the deterministic policy engine."""
from decimal import Decimal, InvalidOperation

MERCHANT_CATEGORIES = ('Office Supplies', 'Cloud Tools', 'Travel Booking', 'Unknown Merchant')


def validate_ai_proposal(data):
    if not isinstance(data, dict):
        raise ValueError('AI proposal must be a JSON object')
    merchant = data.get('merchant_category')
    if merchant not in MERCHANT_CATEGORIES:
        raise ValueError('AI proposed an unsupported merchant category')
    amount = data.get('estimated_amount_gbp')
    if isinstance(amount, bool) or not isinstance(amount, (int, float, str)):
        raise ValueError('AI proposed an invalid amount')
    try:
        decimal_amount = Decimal(str(amount))
    except InvalidOperation as exc:
        raise ValueError('AI proposed an invalid amount') from exc
    if not decimal_amount.is_finite() or decimal_amount <= 0 or decimal_amount > 1000000:
        raise ValueError('AI proposed an invalid amount')
    if decimal_amount.as_tuple().exponent < -2:
        raise ValueError('Amount must have no more than two decimal places')
    description = data.get('description')
    if not isinstance(description, str) or not description.strip():
        raise ValueError('AI proposal needs a purchase description')
    if len(description) > 500:
        raise ValueError('AI purchase description is too long')
    return {'merchant': merchant, 'amount': float(decimal_amount), 'description': description.strip()}
