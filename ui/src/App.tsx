import { FormEvent, useEffect, useMemo, useState } from "react";

import { getHealth, postIngest, postQuery } from "./api/rag";
import type { HealthResponse, QueryResponse } from "./types/api";

function toLocalTime(value: string | null): string {
  if (!value) {
    return "Not ingested yet";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [ingestLoading, setIngestLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [topKInput, setTopKInput] = useState("3");
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");

  const topKNumber = useMemo(() => {
    const parsed = Number(topKInput);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      return null;
    }
    return Math.floor(parsed);
  }, [topKInput]);

  async function loadHealth(): Promise<void> {
    setHealthLoading(true);
    setError("");
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load health");
    } finally {
      setHealthLoading(false);
    }
  }

  async function handleIngest(): Promise<void> {
    setIngestLoading(true);
    setError("");
    setMessage("");
    try {
      const result = await postIngest();
      setMessage(`${result.status}: ${result.message}`);
      await loadHealth();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingest failed");
    } finally {
      setIngestLoading(false);
    }
  }

  async function handleQuery(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!question.trim()) {
      setError("Question is required");
      return;
    }
    setQueryLoading(true);
    setError("");
    setMessage("");
    try {
      const result = await postQuery(question.trim(), topKNumber);
      setQueryResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
      setQueryResult(null);
    } finally {
      setQueryLoading(false);
    }
  }

  useEffect(() => {
    void loadHealth();
  }, []);

  return (
    <div className="page">
      <div className="glow glow-left" />
      <div className="glow glow-right" />
      <main className="container">
        <header>
          <p className="eyebrow">Local API Playground</p>
          <h1>RAG Chatbot UI</h1>
          <p className="subtitle">
            Lightweight React + Vite frontend for `/health`, `/ingest`, and `/query`.
          </p>
        </header>

        <section className="card">
          <div className="card-head">
            <h2>Service Health</h2>
            <button onClick={() => void loadHealth()} disabled={healthLoading}>
              {healthLoading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
          {health ? (
            <div className="grid">
              <p>
                <strong>Status:</strong> {health.status}
              </p>
              <p>
                <strong>App:</strong> {health.app}
              </p>
              <p>
                <strong>Version:</strong> {health.version}
              </p>
              <p>
                <strong>Index:</strong> {health.index_exists ? "ready" : "missing"}
              </p>
              <p>
                <strong>Metadata:</strong> {health.metadata_exists ? "ready" : "missing"}
              </p>
              <p>
                <strong>Last successful ingest:</strong>{" "}
                {toLocalTime(health.last_success_ingestion_time)}
              </p>
            </div>
          ) : (
            <p>Loading service status...</p>
          )}
        </section>

        <section className="card">
          <div className="card-head">
            <h2>Ingest Markdown</h2>
            <button onClick={() => void handleIngest()} disabled={ingestLoading}>
              {ingestLoading ? "Running..." : "Trigger /ingest"}
            </button>
          </div>
          <p className="hint">Ingest scans `raw_docs/*.md` and updates FAISS + metadata.</p>
        </section>

        <section className="card">
          <h2>Ask Question</h2>
          <form onSubmit={handleQuery} className="query-form">
            <label>
              Question
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Summarize the docs in one paragraph"
                rows={4}
              />
            </label>
            <label>
              Top-K
              <input
                type="number"
                min={1}
                max={20}
                value={topKInput}
                onChange={(event) => setTopKInput(event.target.value)}
              />
            </label>
            <button type="submit" disabled={queryLoading}>
              {queryLoading ? "Querying..." : "Run /query"}
            </button>
          </form>

          {queryResult && (
            <div className="result">
              <h3>Answer</h3>
              <p>{queryResult.answer}</p>
              <p>
                <strong>Used Top-K:</strong> {queryResult.used_top_k}
              </p>
              <h3>Retrieved Chunks ({queryResult.retrieved_chunks.length})</h3>
              <ul>
                {queryResult.retrieved_chunks.map((chunk) => (
                  <li key={chunk.chunk_id}>
                    <strong>{chunk.chunk_id}</strong> | score: {chunk.score.toFixed(4)} |
                    source: {chunk.source_path}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {message && <p className="notice success">{message}</p>}
        {error && <p className="notice error">{error}</p>}
      </main>
    </div>
  );
}
