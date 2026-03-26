from __future__ import annotations

import requests

from app.core.config import settings


class GenerationService:
    def build_prompt(self, question: str, contexts: list[dict]) -> str:
        context_text = "\n\n".join(
            [f"[{i + 1}] {item['text']}" for i, item in enumerate(contexts)]
        )
        return (
            "Use the provided context to answer the question. "
            "If the answer is not in context, say you are not sure.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )

    def generate(self, question: str, contexts: list[dict]) -> str:
        prompt = self.build_prompt(question, contexts)

        if settings.llm_provider == "huggingface" and settings.huggingface_token:
            return self._generate_with_hf(prompt)

        return self._generate_mock(question, contexts)

    def _generate_mock(self, question: str, contexts: list[dict]) -> str:
        if not contexts:
            return "I could not find relevant context in the local knowledge base."
        top = contexts[0]["text"]
        return (
            f"(Mock answer) Based on local docs, a likely answer to '{question}' is: "
            f"{top[:300]}"
        )

    def _generate_with_hf(self, prompt: str) -> str:
        url = f"https://api-inference.huggingface.co/models/{settings.huggingface_model}"
        headers = {"Authorization": f"Bearer {settings.huggingface_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 180, "temperature": 0.2},
        }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data and "generated_text" in data[0]:
            return str(data[0]["generated_text"])
        if isinstance(data, dict) and "generated_text" in data:
            return str(data["generated_text"])
        return str(data)


generation_service = GenerationService()
