"""
LLM client abstraction — supports any OpenAI-compatible provider.
Provider/model are configured via environment variables.
"""
import logging
import time
from typing import Optional
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        kwargs = {
            "api_key": settings.LLM_API_KEY or "sk-no-key",
        }
        base_url = settings.get_llm_base_url()
        if base_url:
            kwargs["base_url"] = base_url
        _client = OpenAI(**kwargs)
    return _client


def call_llm(
    system_prompt: str,
    messages: list[dict],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    retries: int = 2,
) -> str:
    """
    Call the configured LLM. Returns the response text.
    Handles retries for rate limits and timeouts.
    Falls back to a safe error message on persistent failure.
    """
    client = _get_client()
    model = model or settings.LLM_MODEL
    temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    max_tokens = max_tokens or settings.LLM_MAX_TOKENS

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = response.choices[0].message.content or ""
            return text.strip()

        except RateLimitError as e:
            wait = 2 ** attempt
            logger.warning(f"Rate limit hit, waiting {wait}s (attempt {attempt+1}): {e}")
            if attempt < retries:
                time.sleep(wait)
            else:
                return (
                    "I'm currently experiencing high demand. Please try again in a moment. "
                    "Your issue has been noted and a ticket is being created."
                )

        except APITimeoutError as e:
            logger.warning(f"LLM timeout (attempt {attempt+1}): {e}")
            if attempt < retries:
                time.sleep(1)
            else:
                return (
                    "My response timed out. I've logged your request. "
                    "A support representative will follow up shortly."
                )

        except APIError as e:
            logger.error(f"LLM API error (attempt {attempt+1}): {e}")
            if attempt < retries:
                time.sleep(1)
            else:
                return (
                    "I encountered a technical issue generating a response. "
                    "Please try again or contact support directly."
                )

        except Exception as e:
            logger.error(f"Unexpected LLM error: {e}")
            return (
                "An unexpected error occurred. Your message has been logged. "
                "Please try again."
            )

    return "Unable to generate a response at this time."
