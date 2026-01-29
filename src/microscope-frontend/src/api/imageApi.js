// src/api/imageApi.js

const BASE_URL = "http://127.0.0.1:8000"; // backend port

export async function captureImage(payload) {
  const res = await fetch(`${BASE_URL}/api/capture/image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Capture failed (${res.status}): ${text}`);
  }

  return await res.json();
}
