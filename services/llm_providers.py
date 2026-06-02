"""
LLM Provider Abstraction Layer.
Supports local Ollama (offline) and cloud Groq (high-performance) backends.
Selected via the LLM_PROVIDER environment variable.
"""

import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

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
    """Local offline provider utilizing local Ollama server endpoints."""
    def __init__(self):
        self.api_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
        self.model = os.environ.get("OLLAMA_MODEL", "mistral")
        self.timeout = int(os.environ.get("OLLAMA_TIMEOUT", "90"))
        logger.info(f"OllamaProvider initialized with model={self.model} at url={self.api_url}")

    def generate(self, prompt: str) -> Optional[str]:
        try:
            if not prompt or not prompt.strip():
                logger.warning("Empty prompt provided to OllamaProvider")
                return None

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
                logger.error(f"Ollama provider error: {response.status_code} - {response.text}")
                return None

            result = response.json()
            output = result.get("response", "")

            if not output.strip():
                logger.warning("Empty response from Ollama provider")
                return None

            logger.info(f"Ollama provider generated {len(output)} characters")
            return output

        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timeout after {self.timeout} seconds")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to local Ollama API at {self.api_url}. Run 'ollama serve'")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in OllamaProvider: {e}")
            return None


class GroqProvider(LLMProvider):
    """Cloud provider utilizing the official Groq API endpoint for high-speed inference."""
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.model = os.environ.get("GROQ_MODEL", "llama3-8b-8192")
        logger.info(f"GroqProvider initialized with model={self.model}")

    def generate(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            logger.error("GROQ_API_KEY environment variable is missing. Groq calls will fail.")
            print("❌ Error: GROQ_API_KEY environment variable not set.")
            return None

        try:
            if not prompt or not prompt.strip():
                logger.warning("Empty prompt provided to GroqProvider")
                return None

            from groq import Groq
            client = Groq(api_key=self.api_key)

            logger.info(f"Sending prompt to Groq model {self.model}...")
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.1
            )

            output = chat_completion.choices[0].message.content
            if not output or not output.strip():
                logger.warning("Empty response from Groq provider")
                return None

            logger.info(f"Groq provider generated {len(output)} characters")
            return output

        except ImportError:
            logger.error("groq package not installed. Run 'pip install groq'")
            return None
        except Exception as e:
            logger.error(f"Error during Groq generation API call: {e}")
            return None


def get_llm_provider() -> LLMProvider:
    """
    Factory function resolving the active LLM provider from the environment.
    
    Returns:
        LLMProvider: Active LLM provider instance (Ollama or Groq)
    """
    provider_name = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()
    
    if provider_name == "groq":
        return GroqProvider()
    else:
        # Default fallback is local Ollama
        return OllamaProvider()
