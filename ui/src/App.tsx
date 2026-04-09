import { FormEvent, useEffect, useState } from "react";

import { getHealth, postQuery } from "./api/rag";
import type { HealthResponse } from "./types/api";

type Message = {
  role: "user" | "assistant";
  text: string;
};

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthStatus, setHealthStatus] = useState("checking");
  const [healthLoading, setHealthLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  function formatTime(value: string | null): string {
    if (!value) {
      return "not synced";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString();
  }

  async function loadHealth(): Promise<void> {
    setHealthLoading(true);
    try {
      const health = await getHealth();
      setHealth(health);
      setHealthStatus(health.status || "ok");
    } catch {
      setHealth(null);
      setHealthStatus("offline");
    } finally {
      setHealthLoading(false);
    }
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const question = input.trim();
    if (!question || sending) {
      return;
    }

    setInput("");
    setSending(true);
    setMessages((prev) => [...prev, { role: "user", text: question }]);

    try {
      const result = await postQuery(question, null);
      const maybeAnswer = (result as { answer?: unknown }).answer;
      const answer =
        typeof maybeAnswer === "string" && maybeAnswer.trim()
          ? maybeAnswer
          : JSON.stringify(result) || "No answer returned.";
      setMessages((prev) => [...prev, { role: "assistant", text: answer }]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Request failed";
      setMessages((prev) => [...prev, { role: "assistant", text: `Error: ${message}` }]);
    } finally {
      setSending(false);
      void loadHealth();
    }
  }

  useEffect(() => {
    void loadHealth();
  }, []);

  return (
    <main className="app">
      <header className="topbar">
        <h1>Chatbot</h1>
        <button
          type="button"
          className="badge"
          data-status={healthStatus === "ok" ? "ok" : "offline"}
          onClick={() => void loadHealth()}
          disabled={healthLoading}
        >
          {healthLoading ? "Checking..." : `Health: ${healthStatus}`}
        </button>
      </header>

      <section className="health-panel">
        <p>
          <span>Service</span>
          <strong>{healthStatus}</strong>
        </p>
        <p>
          <span>Ingestion</span>
          <strong>{health?.ingestion_status ?? "unknown"}</strong>
        </p>
        <p>
          <span>Doc last sync</span>
          <strong>{formatTime(health?.last_success_ingestion_time ?? null)}</strong>
        </p>
        <p>
          <span>Version</span>
          <strong>{health?.version ?? "-"}</strong>
        </p>
      </section>

      <section className="messages">
        {messages.length === 0 ? (
          <p className="empty">Ask anything to start the chat.</p>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`bubble ${msg.role}`}>
              {msg.text}
            </div>
          ))
        )}
      </section>

      <form className="composer" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type your question..."
        />
        <button type="submit" disabled={sending || !input.trim()}>
          {sending ? "..." : "Send"}
        </button>
      </form>
    </main>
  );
}
