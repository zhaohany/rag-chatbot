export type HealthResponse = {
  status: string;
  version: string;
  ingestion_status: string;
  last_success_ingestion_time: string | null;
};

export type IngestResponse = {
  status: string;
  message: string;
};

export type RetrievedChunk = {
  vector_id: number;
  chunk_id: string;
  doc_id: string;
  score: number;
  text: string;
  source_path: string;
};

export type QueryResponse = {
  answer?: string;
  used_top_k?: number;
  retrieved_chunks?: RetrievedChunk[];
  [key: string]: unknown;
};
