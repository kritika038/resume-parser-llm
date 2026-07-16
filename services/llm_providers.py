"""
LLM Provider Abstraction Layer for Generative AI Platforms.
Supports Multi-provider LLM orchestration with local inference (Ollama offline) and cloud API inference (Groq serverless LPUs).
Implements resilient request retries, timeout management, and dynamic failover routing.
Keywords: LLMs, Generative AI, Production AI, AI Engineering, Multi-provider LLM, Resilience.
"""

import os
import requests
import logging
import time
import uuid
from typing import Optional

logger = logging.getLogger(__name__)


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves configuration keys prioritizing environment variables,
    with an automatic fallback to Streamlit secrets for Cloud platform compatibility.
    """
    # 1. Try environment variables
    val = os.environ.get(key)
    if val:
        return val
    # 2. Try Streamlit Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


class LLMProvider:
    """Base class defining the unified interface for LLM operations."""
    def generate(self, prompt: str) -> Optional[str]:
        """
        Generates text completion for the provided prompt.
        
        Args:
            prompt: Text prompt with task instructions and context
            
        Returns:
            str: Raw generated completion text
            None: If the provider call fails
        """
        raise NotImplementedError("Providers must implement the generate method.")


class OllamaProvider(LLMProvider):
    """Local offline/remote provider utilizing Ollama server endpoints."""
    def __init__(self):
        ollama_base = get_config_value("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        # Preserve backward compatibility with OLLAMA_API_URL if set
        self.api_url = get_config_value("OLLAMA_API_URL", f"{ollama_base}/api/generate")
        self.model = get_config_value("OLLAMA_MODEL", "mistral")
        self.timeout = int(get_config_value("OLLAMA_TIMEOUT", "90"))
        logger.info(f"OllamaProvider initialized with model={self.model} at url={self.api_url}")

    def generate(self, prompt: str) -> Optional[str]:
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[Request {request_id}] Starting Ollama request with model={self.model} at url={self.api_url}")

        if not prompt or not prompt.strip():
            logger.warning(f"[Request {request_id}] Empty prompt provided to OllamaProvider")
            return None

        max_retries = 3
        backoff_factor = 1.0

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"[Request {request_id}] Attempt {attempt + 1}/{max_retries + 1}: POST to {self.api_url}")
                response = requests.post(
                    self.api_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    logger.error(f"[Request {request_id}] Ollama provider error (status code {response.status_code}): {response.text}")
                    # Retry on 5xx server errors or rate limit (429)
                    if response.status_code >= 500 or response.status_code == 429:
                        if attempt < max_retries:
                            sleep_time = backoff_factor * (2 ** attempt)
                            logger.info(f"[Request {request_id}] Retrying in {sleep_time}s due to status code {response.status_code}...")
                            time.sleep(sleep_time)
                            continue
                    return None

                result = response.json()
                output = result.get("response", "")

                # Capture token usage for Ollama
                import streamlit as st
                prompt_tokens = result.get("prompt_eval_count", 0)
                completion_tokens = result.get("eval_count", 0)
                total_tokens = prompt_tokens + completion_tokens
                if total_tokens > 0:
                    try:
                        st.session_state["token_usage"] = {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": total_tokens
                        }
                    except Exception as e:
                        # Session state might not exist when running evaluation or testing
                        logger.debug(f"[Request {request_id}] Could not write to st.session_state: {e}")

                if not output.strip():
                    logger.warning(f"[Request {request_id}] Empty response from Ollama provider")
                    return None

                logger.info(f"[Request {request_id}] Ollama provider generated {len(output)} characters")
                return output

            except requests.exceptions.Timeout:
                logger.error(f"[Request {request_id}] Ollama request timeout on attempt {attempt + 1}/{max_retries + 1} after {self.timeout} seconds")
                if attempt < max_retries:
                    sleep_time = backoff_factor * (2 ** attempt)
                    logger.info(f"[Request {request_id}] Retrying in {sleep_time}s due to timeout...")
                    time.sleep(sleep_time)
                    continue
                return None
            except requests.exceptions.ConnectionError:
                logger.error(f"[Request {request_id}] Cannot connect to Ollama API at {self.api_url} on attempt {attempt + 1}/{max_retries + 1}")
                if attempt < max_retries:
                    sleep_time = backoff_factor * (2 ** attempt)
                    logger.info(f"[Request {request_id}] Retrying in {sleep_time}s due to connection error...")
                    time.sleep(sleep_time)
                    continue
                return None
            except Exception as e:
                logger.error(f"[Request {request_id}] Unexpected error in OllamaProvider on attempt {attempt + 1}/{max_retries + 1}: {e}")
                if attempt < max_retries:
                    sleep_time = backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
                    continue
                return None


class GroqProvider(LLMProvider):
    """Cloud provider utilizing the official Groq API endpoint for high-speed inference."""
    def __init__(self):
        self.api_key = get_config_value("GROQ_API_KEY")
        self.model = get_config_value("GROQ_MODEL", "llama-3.1-8b-instant")
        logger.info(f"GroqProvider initialized with model={self.model}")

    def generate(self, prompt: str) -> Optional[str]:
        request_id = str(uuid.uuid4())[:8]

        if not self.api_key:
            logger.error(f"[Request {request_id}] GROQ_API_KEY environment variable is missing. Groq calls will fail.")
            return None

        try:
            if not prompt or not prompt.strip():
                logger.warning(f"[Request {request_id}] Empty prompt provided to GroqProvider")
                return None

            from groq import Groq
            client = Groq(api_key=self.api_key)

            logger.info(f"[Request {request_id}] Sending prompt to Groq model {self.model}...")
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.0,
                top_p=0.1
            )

            output = chat_completion.choices[0].message.content
            
            # Capture token usage for Groq
            import streamlit as st
            if hasattr(chat_completion, "usage") and chat_completion.usage:
                try:
                    st.session_state["token_usage"] = {
                        "prompt_tokens": chat_completion.usage.prompt_tokens,
                        "completion_tokens": chat_completion.usage.completion_tokens,
                        "total_tokens": chat_completion.usage.total_tokens
                    }
                except Exception as e:
                    logger.debug(f"[Request {request_id}] Could not write to st.session_state: {e}")

            if not output or not output.strip():
                logger.warning(f"[Request {request_id}] Empty response from Groq provider")
                return None

            logger.info(f"[Request {request_id}] Groq provider generated {len(output)} characters")
            return output

        except ImportError:
            logger.error(f"[Request {request_id}] groq package not installed. Run 'pip install groq'")
            return None
        except Exception as e:
            logger.error(f"[Request {request_id}] Error during Groq generation API call: {e}")
            return None


def get_llm_provider() -> LLMProvider:
    """
    Factory function resolving the active LLM provider from the environment.
    
    Returns:
        LLMProvider: Active LLM provider instance (Ollama or Groq)
    """
    is_hf_space = "SPACE_ID" in os.environ or get_config_value("SPACE_ID") is not None
    is_prod = "RENDER" in os.environ or "RAILWAY_STATIC_URL" in os.environ or "PORT" in os.environ or get_config_value("RENDER") is not None or get_config_value("PORT") is not None
    default_provider = "groq" if (is_hf_space or is_prod) else "ollama"
    provider_name = get_config_value("LLM_PROVIDER", default_provider).strip().lower()
    
    if provider_name == "groq":
        return GroqProvider()
    else:
        # Default fallback is local/remote Ollama
        return OllamaProvider()
