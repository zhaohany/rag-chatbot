from __future__ import annotations

from google import genai
from google.genai import errors
from google.genai import types

from app.core.config import settings


class GeminiClientError(RuntimeError):
    pass


class GeminiClient:
    def generate_content(self, prompt: str) -> str:
        api_key = settings.gemini_api_key
        if not api_key:
            raise GeminiClientError(
                "Gemini API key is missing. Set RAG_GEMINI_API_KEY in your .env or environment."
            )

        client = genai.Client(api_key=api_key)

        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=settings.llm_max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except errors.APIError as exc:
            raise GeminiClientError(f"Gemini API error: {exc}") from exc
        except Exception as exc:
            raise GeminiClientError(f"Gemini request failed: {exc}") from exc

        text = response.text
        if not isinstance(text, str) or not text.strip():
            raise GeminiClientError("Gemini returned empty text output.")
        return text


gemini_client = GeminiClient()
