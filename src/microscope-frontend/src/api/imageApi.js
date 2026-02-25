// src/api/imageApi.js

const BASE_URL = import.meta.env.VITE_API_BASE || ""; // backend port

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

export async function getPosition() {
  const r = await fetch(`${BASE_URL}/position`);
  if (!r.ok) throw new Error(await r.text());
  return r.json(); // { position: {x,y,z} }
}

export async function centerStage() {
  const r = await fetch(`${BASE_URL}/center`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function listCaptures() {
  const r = await fetch(`${BASE_URL}/captures`);
  if (!r.ok) throw new Error(`captures failed: ${r.status}`);
  return r.json();
}

export async function deleteCapture(captureId) {
  const r = await fetch(`${BASE_URL}/captures/${encodeURIComponent(captureId)}`, {
    method: "DELETE",
  });
  if (!r.ok) throw new Error(`delete failed: ${r.status}`);
  return r.json().catch(() => ({}));
}

export async function analyzeCapture(captureId) {
  const res = await fetch(`${BASE_URL}/captures/${encodeURIComponent(captureId)}/analyze`, {
    method: "POST",
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function updateCaptureMetadata(captureId, payload) {
  const r = await fetch(`${BASE_URL}/captures/${encodeURIComponent(captureId)}/metadata`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getLiveInfo() {
  const r = await fetch(`${BASE_URL}/live`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function microscopeHealth() {
  const r = await fetch(`${BASE_URL}/microscope/health`);
  return r.ok;
}

export async function deleteTag(captureId, tag) {
  const base = import.meta.env.VITE_API_BASE || "";
  const r = await fetch(
    `${base}/captures/${encodeURIComponent(captureId)}/tags/${encodeURIComponent(tag)}`,
    { method: "DELETE" }
  );
  if (!r.ok) throw new Error(await r.text());
  return r.json().catch(() => ({}));
}
