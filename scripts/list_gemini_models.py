from __future__ import annotations

import os
from pathlib import Path

from google import genai

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "models" / "gemini_models.txt"


def _load_env_file() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> int:
    _load_env_file()
    api_key = os.getenv("RAG_GEMINI_API_KEY")
    if not api_key:
        print("Missing API key. Set RAG_GEMINI_API_KEY.")
        return 1

    client = genai.Client(api_key=api_key)

    lines: list[str] = []
    print("Available Gemini models:")
    for model in client.models.list():
        name = getattr(model, "name", "")
        methods = getattr(model, "supported_generation_methods", None)
        if isinstance(methods, list) and methods:
            methods_text = ", ".join(methods)
            line = f"- {name} | methods: {methods_text}"
            lines.append(line)
            print(line)
        else:
            line = f"- {name}"
            lines.append(line)
            print(line)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved model list to: {OUTPUT_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
