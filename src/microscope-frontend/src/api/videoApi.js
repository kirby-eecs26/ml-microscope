const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function startVideo(payload) {
  const res = await fetch(`${BASE}/video/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function stopVideo(videoId) {
  const res = await fetch(`${BASE}/video/stop/${videoId}`, {
    method: "POST",
  });
  return res.json();
}

export async function analyzeVideo(videoId) {
  const res = await fetch(`${BASE}/video/analyze/${videoId}`, {
    method: "POST",
  });
  return res.json();
}

export async function saveVideoToGallery(videoId, payload) {
  const res = await fetch(`${BASE}/video/save/${videoId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}
