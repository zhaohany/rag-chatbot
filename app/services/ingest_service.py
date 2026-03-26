from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.metadata_store import MetadataStore
from app.services.vector_store import FaissVectorStore
from app.state import ingest_state
from app.shared.chunking import chunk_text
from app.shared.ids import make_chunk_id, make_doc_id


class IngestService:
    def __init__(self) -> None:
        self.metadata_store = MetadataStore(settings.metadata_path)
        self.vector_store = FaissVectorStore(settings.faiss_index_path)

    def run_ingest(self) -> None:
        try:
            raw_files = sorted(settings.raw_docs_dir.glob("*.md"))
            if not raw_files:
                ingest_state.last_status = "failed"
                ingest_state.last_message = "No markdown files found in raw_docs"
                return

            next_doc_number = self.metadata_store.get_next_doc_number()

            chunk_payloads: list[dict] = []
            chunk_texts: list[str] = []

            for raw_file in raw_files:
                content = raw_file.read_text(encoding="utf-8")
                chunks = chunk_text(
                    content,
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                )
                if not chunks:
                    continue

                doc_id = make_doc_id(next_doc_number)
                next_doc_number += 1

                for i, chunk in enumerate(chunks, start=1):
                    chunk_id = make_chunk_id(doc_id, i)
                    chunk_texts.append(chunk.text)
                    chunk_payloads.append(
                        {
                            "doc_id": doc_id,
                            "chunk_id": chunk_id,
                            "source_path": str(raw_file),
                            "text": chunk.text,
                            "start_char": chunk.start_char,
                            "end_char": chunk.end_char,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            if not chunk_texts:
                ingest_state.last_status = "failed"
                ingest_state.last_message = "No valid content after chunking"
                return

            vectors = embedding_service.encode(chunk_texts)

            if self.vector_store.exists():
                self.vector_store.load()
            else:
                self.vector_store.create(len(vectors[0]))

            start_id, _ = self.vector_store.add(vectors)
            self.vector_store.save()

            for offset, payload in enumerate(chunk_payloads):
                payload["vector_id"] = start_id + offset

            self.metadata_store.append_entries(chunk_payloads)

            ingest_state.last_success_ingestion_time = datetime.now(
                timezone.utc
            ).isoformat()
            ingest_state.last_status = "completed"
            ingest_state.last_message = (
                f"Ingested {len(raw_files)} files, {len(chunk_payloads)} chunks"
            )
        except Exception as exc:  # noqa: BLE001
            ingest_state.last_status = "failed"
            ingest_state.last_message = f"Ingest error: {exc}"
        finally:
            ingest_state.is_running = False


ingest_service = IngestService()
