const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function requestJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
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
}
