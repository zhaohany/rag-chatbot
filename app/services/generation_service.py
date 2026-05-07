from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings


class PromptTemplateError(RuntimeError):
    pass


class PromptSaveError(RuntimeError):
    pass


def _read_template(template_path: Path) -> str:
    if not template_path.exists():
        raise PromptTemplateError(
            f"Prompt template not found: {template_path}. "
            "Please create the template file or update RAG_PROMPT_TEMPLATE_PATH."
        )

    try:
        return template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PromptTemplateError(
            f"Failed to read prompt template: {template_path} ({exc})"
        ) from exc


def _build_context_blocks(retrieved_chunks: list[dict[str, Any]]) -> str:
    if not retrieved_chunks:
        return "[No retrieval context found]"

    lines: list[str] = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        text = chunk.get("text") or "[Missing chunk text in metadata]"
        chunk_id = chunk.get("chunk_id") or "unknown_chunk"
        doc_id = chunk.get("doc_id") or "unknown_doc"
        source_path = chunk.get("source_path") or "unknown_source"
        score = chunk.get("score")
        if isinstance(score, (int, float)):
            score_display = f"{float(score):.4f}"
        else:
            score_display = "N/A"

        lines.append(
            f"[{idx}] chunk_id={chunk_id} doc_id={doc_id} source={source_path} score={score_display}\n"
            f"{text}"
        )

    return "\n\n".join(lines)


class GenerationService:
    def build_prompt_v2_homework(
        self,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
    ) -> str:
        """Homework function: build v2 prompt with runtime placeholders.

        Keep current app runnable by default: this function is NOT wired into
        production flow yet. Students should implement this function first, then
        switch one line in `build_prompt` (see hook below).

        Input contract:
        - `question`: user question string
        - `retrieved_chunks`: retrieval rows from query service

        Output contract:
        - Return one final prompt string that is fully rendered from template.

        Required placeholders for v2 template:
        - `{context_blocks}`
        - `{question}`
        - `{top_k}`
        - `{company_policy_version}`
        - `{response_language}`

        Implementation notes:
        1) Read template with `_read_template(settings.prompt_template_path)`.
        2) Build context with `_build_context_blocks(retrieved_chunks)`.
        3) Render template with `template.format(...)` using all placeholders.
        4) Keep existing error handling style: raise `PromptTemplateError` on
           missing keys.

        Homework hook (where to switch usage):
        - In `build_prompt`, replace current `template.format(...)` return path
          with:
              return self.build_prompt_v2_homework(question, retrieved_chunks)
        """
        raise NotImplementedError("Homework: implement v2 prompt rendering")

    def build_prompt(
        self,
        question: str,
        retrieved_chunks: list[dict[str, Any]],
    ) -> str:
        # Homework hook:
        # After implementing `build_prompt_v2_homework`, switch to:
        # return self.build_prompt_v2_homework(question, retrieved_chunks)
        #
        # We keep v1 path as default so current MVP remains runnable.
        template = _read_template(settings.prompt_template_path)
        context_blocks = _build_context_blocks(retrieved_chunks)

        try:
            return template.format(context_blocks=context_blocks, question=question)
        except KeyError as exc:
            raise PromptTemplateError(
                "Prompt template is invalid. It must contain {context_blocks} and {question}."
            ) from exc

    def save_prompt(self, prompt: str) -> None:
        final_prompt_path = settings.final_prompt_path
        try:
            final_prompt_path.parent.mkdir(parents=True, exist_ok=True)
            final_prompt_path.write_text(prompt, encoding="utf-8")
        except OSError as exc:
            raise PromptSaveError(
                f"Failed to save final prompt: {final_prompt_path} ({exc})"
            ) from exc


generation_service = GenerationService()
