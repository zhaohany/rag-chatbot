from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MetadataStore:
    def __init__(self, metadata_path: Path) -> None:
        self.metadata_path = metadata_path

    def exists(self) -> bool:
        return self.metadata_path.exists()

    def load(self) -> dict[str, Any]:
        if not self.exists():
            return {"entries": []}
        with self.metadata_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, payload: dict[str, Any]) -> None:
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with self.metadata_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def get_next_doc_number(self) -> int:
        data = self.load()
        entries = data.get("entries", [])
        doc_ids = {e.get("doc_id") for e in entries if e.get("doc_id")}
        max_num = 0
        for doc_id in doc_ids:
            try:
                value = int(str(doc_id).split("_")[-1])
                max_num = max(max_num, value)
            except ValueError:
                continue
        return max_num + 1

    def append_entries(self, entries: list[dict[str, Any]]) -> None:
        data = self.load()
        existing = data.get("entries", [])
        existing.extend(entries)
        data["entries"] = existing
        self.save(data)

    def by_vector_id(self) -> dict[int, dict[str, Any]]:
        data = self.load()
        result: dict[int, dict[str, Any]] = {}
        for entry in data.get("entries", []):
            vector_id = entry.get("vector_id")
            if isinstance(vector_id, int):
                result[vector_id] = entry
        return result
