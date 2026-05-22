from __future__ import annotations

from google import genai
from google.genai import errors
from google.genai import types

from app.core.config import settings


class GeminiClientError(RuntimeError):
    pass


class GeminiClient:
    def generate_content(self, prompt: str) -> str:
        """Homework function: implement Gemini API call section.

        Scope:
        - Implement ONLY this function for LLM integration practice.
        - Do not change route/service schemas or retrieval flow.

        Input:
        - `prompt`: non-empty user/system prompt string.

        Output:
        - Return model raw text output as `str`.
        - Output must be non-empty.

        Required behavior:
        - Keep the prewritten validation blocks unchanged.
        - Implement the middle API invocation block.
        1) Build Gemini client: `genai.Client(api_key=api_key)`.
        2) Call `client.models.generate_content(...)` with:
           - `model=settings.gemini_model`
           - `contents=prompt`
           - `config=types.GenerateContentConfig(...)` including:
             - `max_output_tokens=settings.llm_max_output_tokens`
             - `response_mime_type="application/json"`
        3) Convert API/SDK/runtime errors to GeminiClientError with clear message.

        Notes:
        - Keep error messages actionable for local debugging.
        - JSON parsing is handled in upper layer (`generation_service`), not here.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise GeminiClientError("Prompt must be a non-empty string.")

        api_key = settings.gemini_api_key
        if not api_key:
            raise GeminiClientError(
                "Gemini API key is missing. Set RAG_GEMINI_API_KEY in your .env or environment."
            )

        # TODO(homework): implement only the API invocation block below.
        # Requirements:
        # - create client: genai.Client(api_key=api_key)
        # - call client.models.generate_content(...) with required config
        # - map errors.APIError and generic Exception to GeminiClientError
        try:
            # TODO(homework):
            # 1) create client with genai.Client(api_key=api_key)
            # 2) call client.models.generate_content(...) and assign to `response`
            #    with:
            #    - model=settings.gemini_model
            #    - contents=prompt
            #    - config=types.GenerateContentConfig(
            #        max_output_tokens=settings.llm_max_output_tokens,
            #        response_mime_type="application/json",
            #      )
            raise NotImplementedError("Homework: implement Gemini API call in try block")
        except errors.APIError as exc:
            raise GeminiClientError(f"Gemini API error: {exc}") from exc
        except Exception as exc:
            raise GeminiClientError(f"Gemini request failed: {exc}") from exc

        text = response.text
        if not isinstance(text, str) or not text.strip():
            raise GeminiClientError("Gemini returned empty text output.")
        return text


gemini_client = GeminiClient()
