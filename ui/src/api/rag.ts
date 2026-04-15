import { requestJson } from "./client";
import type { HealthResponse, IngestResponse, QueryResponse } from "../types/api";

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health", { method: "GET" });
}

export function postIngest(): Promise<IngestResponse> {
  return requestJson<IngestResponse>("/ingest", {
    method: "POST",
    timeoutMs: 600000,
  });
}

export function postQuery(
  question: string,
  topK: number | null
): Promise<QueryResponse> {
  return requestJson<QueryResponse>("/query", {
    method: "POST",
    body: JSON.stringify({
      question,
      ...(topK ? { top_k: topK } : {}),
    }),
  });
}
