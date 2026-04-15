const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const DEFAULT_API_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? "120000");

type RequestJsonInit = RequestInit & {
  timeoutMs?: number;
};

export async function requestJson<T>(
  path: string,
  init?: RequestJsonInit
): Promise<T> {
  const timeoutMs = init?.timeoutMs ?? DEFAULT_API_TIMEOUT_MS;
  const controller = new AbortController();
  const timeoutId =
    timeoutMs > 0
      ? setTimeout(() => {
          controller.abort();
        }, timeoutMs)
      : null;

  const { timeoutMs: _timeoutMs, ...requestInit } = init ?? {};

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(requestInit.headers ?? {}),
      },
      ...requestInit,
      signal: requestInit.signal ?? controller.signal,
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = (await response.json()) as { detail?: string };
        if (body.detail) {
          detail = body.detail;
        }
      } catch {
        detail = response.statusText || detail;
      }
      throw new Error(detail);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`Request timeout after ${timeoutMs}ms`);
    }
    throw error;
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  }
}
