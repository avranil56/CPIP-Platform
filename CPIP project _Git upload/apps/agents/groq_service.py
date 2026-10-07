import os
import time
from groq import Groq
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client():
    api_key = settings.GROQ_API_KEY or os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in .env")
    return Groq(api_key=api_key)

def ask_groq(prompt, model_name='openai/gpt-oss-120b', max_retries=3):
    """Send a prompt to Groq with automatic retry on 429/503 errors."""
    client = get_client()
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e)
            if '429' in error_str or '503' in error_str or 'rate' in error_str.lower():
                wait_time = (attempt + 1) * 3
                logger.warning(f"Groq busy (attempt {attempt+1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise

    logger.error(f"Groq failed after {max_retries} attempts: {last_error}")
    raise last_error


def test_groq_connection():
    try:
        response = ask_groq("Reply with exactly: CPIP_GROQ_OK")
        return {'success': True, 'response': response}
    except Exception as e:
        return {'success': False, 'error': str(e)}