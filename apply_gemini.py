"""Run from repository root: python apply_gemini.py"""
from pathlib import Path
p=Path('app.py')
s=p.read_text(encoding='utf-8')
old='from integrations import paypal_sandbox_order_status, ai_purchase_draft'
assert old in s, 'Unexpected app.py version: import not found'
s=s.replace(old, 'from integrations import paypal_sandbox_order_status\nfrom gemini_integration import gemini_purchase_draft')
s=s.replace("openai_key = secrets.get('OPENAI_API_KEY', '')", "gemini_key = secrets.get('GEMINI_API_KEY', '')")
s=s.replace('openai_key = paypal_id = paypal_secret = \'\'', 'gemini_key = paypal_id = paypal_secret = \'\'')
s=s.replace('disabled=not bool(openai_key)', 'disabled=not bool(gemini_key)')
s=s.replace('ai_purchase_draft(openai_key, request_text)', 'gemini_purchase_draft(gemini_key, request_text)')
s=s.replace('if not openai_key:', 'if not gemini_key:')
s=s.replace('AI integration not configured: add OPENAI_API_KEY to Streamlit app secrets to enable live model responses.', 'Gemini integration not configured: add GEMINI_API_KEY to Streamlit app secrets to enable live model responses.')
s=s.replace('AI service unavailable. Check server-side API configuration and retry.', 'Gemini service unavailable. Check Streamlit logs, API key, model access and free-tier quota.')
s=s.replace('AI-assisted purchase drafting', 'Gemini AI-assisted purchase drafting')
p.write_text(s,encoding='utf-8')
r=Path('README.md')
if r.exists():
    t=r.read_text(encoding='utf-8').replace('OpenAI Responses API', 'Google Gemini API').replace('OPENAI_API_KEY', 'GEMINI_API_KEY').replace('OpenAI draft', 'Gemini draft')
    r.write_text(t,encoding='utf-8')
print('Updated app.py and README.md to use Gemini.')
