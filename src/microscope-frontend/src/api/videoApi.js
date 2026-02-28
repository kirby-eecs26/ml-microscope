const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function asJsonOrThrow(res) {
  let data = null;
  try {
    data = await res.json();
  } catch {
    // ignore json parse errors
  }

  if (!res.ok) {
    const detail = data?.detail || data?.message || `${res.status} ${res.statusText}`;
    throw new Error(detail);
  }
  return data;
}

export async function startVideo(payload) {
  const res = await fetch(`${BASE}/video/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return asJsonOrThrow(res);
}

export async function analyzeVideo(videoId, payload = {}) {
  const res = await fetch(`${BASE}/video/analyze/${encodeURIComponent(videoId)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return asJsonOrThrow(res);
}

export async function saveVideoToGallery(videoId, payload) {
  const res = await fetch(`${BASE}/video/${encodeURIComponent(videoId)}/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return asJsonOrThrow(res);
}

export async function stopVideo(recordingId) {
  const res = await fetch(`${BASE}/video/stop`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recording_id: recordingId }),
  });
  return asJsonOrThrow(res);
}

export async function getVideoStatus(recordingId) {
  const res = await fetch(`${BASE}/video/${encodeURIComponent(recordingId)}/status`);
  return asJsonOrThrow(res);
}

export async function listVideos() {
  const res = await fetch(`${BASE}/videos`);
  return asJsonOrThrow(res);
}

export async function deleteTempVideo(videoId) {
  const res = await fetch(`${BASE}/video/${encodeURIComponent(videoId)}`, {
    method: "DELETE",
  });
  return asJsonOrThrow(res);
}

export async function deleteVideo(id) {
  const base = import.meta.env.VITE_API_BASE || "";
  const res = await fetch(`${base}/video/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Video delete failed (${res.status})`);
  }
  return res.json().catch(() => ({ ok: true }));
}



/**
 * Convenience URL for <video :src="..."> or a download link.
 * Backend route: GET /video/{id}/download
 */
export function videoDownloadUrl(recordingId) {
  return `${BASE}/video/${encodeURIComponent(recordingId)}/download`;
}