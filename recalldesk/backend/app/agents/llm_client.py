"""
LLM client — xKiro gateway (OpenAI-compatible).
Base URL : https://api.xkiro.com/v1
Models   : qwen/qwen3.7-flash:free  (primary — fastest)
           qwen/qwen3.7-max:free    (fallback — higher quality)
           qwen/qwen3.8-omni-flash:free (fallback 2)
"""
import logging
import time
from typing import Optional
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from app.config import get_settings

logger = logging.getLogger(__name__)

FREE_MODELS = [
    "qwen/qwen3.7-flash:free",
    "qwen/qwen3.7-max:free",
    "qwen/qwen3.8-omni-flash:free",
]

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        api_key = settings.LLM_API_KEY.strip()
        base_url = (settings.LLM_BASE_URL or "https://api.xkiro.com/v1").strip()
        logger.info(f"[LLM] base_url={base_url}  model={settings.LLM_MODEL}  key=SET")
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client


def call_llm(
    system_prompt: str,
    messages: list[dict],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    retries: int = 2,
) -> str:
    """Call xKiro LLM. Returns response text. Handles retries + model fallback."""
    settings = get_settings()
    client   = _get_client()
    use_model = model or settings.LLM_MODEL or FREE_MODELS[0]
    use_temp  = temperature if temperature is not None else settings.LLM_TEMPERATURE
    use_tok   = max_tokens or settings.LLM_MAX_TOKENS

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=use_model,
                messages=full_messages,
                temperature=use_temp,
                max_tokens=use_tok,
            )
            text = response.choices[0].message.content or ""
            logger.info(f"[LLM] ✓ {len(text)} chars  model={use_model}")
            return text.strip()

        except RateLimitError as e:
            wait = 2 ** attempt
            logger.warning(f"[LLM] Rate limit attempt {attempt+1}, wait {wait}s: {e}")
            # rotate to next free model
            if use_model in FREE_MODELS:
                idx = FREE_MODELS.index(use_model)
                if idx + 1 < len(FREE_MODELS):
                    use_model = FREE_MODELS[idx + 1]
                    logger.info(f"[LLM] Falling back to {use_model}")
            if attempt < retries:
                time.sleep(wait)
            else:
                return ("I'm experiencing high demand. Please resend your message — "
                        "your conversation context is preserved.")

        except APITimeoutError as e:
            logger.warning(f"[LLM] Timeout attempt {attempt+1}: {e}")
            if attempt < retries:
                time.sleep(2)
            else:
                return "Response timed out. Please try again — your history is saved."

        except APIError as e:
            logger.error(f"[LLM] API error attempt {attempt+1}: {e}")
            if "401" in str(e) or "unauthorized" in str(e).lower():
                return ("⚠️ API authentication failed. Please check your API key.")
            if attempt < retries:
                time.sleep(1)
            else:
                return "I encountered a technical issue. Please try again."

        except Exception as e:
            logger.error(f"[LLM] Unexpected error: {e}", exc_info=True)
            return "An unexpected error occurred. Please try again."

    return "Unable to generate a response at this time."
