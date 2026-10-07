import os
import time
from google import genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client():
    api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=api_key)


def ask_gemini(prompt, model_name='gemini-3.6-flash', max_retries=3):
    """Send a prompt to Gemini with automatic retry on 503/429 errors."""
    client = get_client()
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            last_error = e
            error_str = str(e)
            # Retry on temporary errors
            if '503' in error_str or 'UNAVAILABLE' in error_str or '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                wait_time = (attempt + 1) * 3  # 3s, 6s, 9s
                logger.warning(f"Gemini busy (attempt {attempt+1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                # Non-retryable error
                raise

    logger.error(f"Gemini failed after {max_retries} attempts: {last_error}")
    raise last_error


def test_gemini_connection():
    try:
        response = ask_gemini("Reply with exactly: CPIP_GEMINI_OK")
        return {'success': True, 'response': response}
    except Exception as e:
        return {'success': False, 'error': str(e)}