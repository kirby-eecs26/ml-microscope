const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function fetchLogs(level = "ALL") {
  const url = `${BASE}/logging?level=${encodeURIComponent(level)}`;

  const res = await fetch(url, { headers: { "Accept": "application/json" } });
  const text = await res.text();

  if (!res.ok) throw new Error(text || `HTTP ${res.status}`);

  if (text.trim().startsWith("<!doctype") || text.trim().startsWith("<html")) {
    throw new Error(
      `Got HTML instead of JSON. Check that BASE points to the backend and that uvicorn was restarted.\n` +
      `URL: ${url}\nFirst bytes: ${text.slice(0, 120)}`
    );
  }

  return JSON.parse(text);
}