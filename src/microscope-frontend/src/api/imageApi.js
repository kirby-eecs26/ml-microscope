// src/api/imageApi.js

const BASE_URL = "http://127.0.0.1:8000"; // backend port

export async function captureImage(payload) {
  const res = await fetch(`${BASE_URL}/capture`, {
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

export async function moveAbs(x, y, z) {
  const res = await fetch(`${BASE_URL}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      x: Math.round(Number(x)),
      y: Math.round(Number(y)),
      z: Math.round(Number(z)),
    }),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}