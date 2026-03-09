<template>
  <div class="previewFrame">
    <div v-if="webStreamDisabled" class="status">
      Web stream is disabled.
      <div class="hint">
        Turn it back on in <b>Settings → Display</b>.
      </div>
    </div>

    <!-- Any error (microscope unreachable, etc.) -->
    <div v-else-if="error" class="status">
      {{ error }}
      <div class="hint">
        Make sure you’re on the same network as the microscope and that
        <code>microscope.local</code> resolves on this machine.
      </div>
    </div>

    <div v-else-if="!mjpegUrl" class="status">
      Loading live feed…
    </div>

    <!-- Direct MJPEG stream -->
    <img
      v-else
      class="previewImage"
      :src="mjpegUrl"
      alt="Microscope camera feed"
      @error="onImgError"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { getLiveInfo, microscopeHealth } from "../api/imageApi";

const STREAM_KEY = "disable_web_stream";

const mjpegUrl = ref("");
const error = ref("");
const webStreamDisabled = ref(false);

function readWebStreamPref() {
  webStreamDisabled.value = localStorage.getItem(STREAM_KEY) === "1";
}

function onImgError() {
  error.value =
    "Live feed unavailable (microscope not reachable from this PC).";
  mjpegUrl.value = "";
}

function onWebStreamPrefChanged() {
  readWebStreamPref();

  if (webStreamDisabled.value) {
    mjpegUrl.value = "";
    error.value = "";
  } else {
    loadPreview();
  }
}

async function loadPreview() {
  try {
    error.value = "";
    if (webStreamDisabled.value) {
      mjpegUrl.value = "";
      return;
    }
    const ok = await microscopeHealth().catch(() => false);
    if (!ok) {
      error.value =
        "Microscope not connected. Plug it in / join its network, then reopen.";
      mjpegUrl.value = "";
      return;
    }
    const info = await getLiveInfo();
    mjpegUrl.value = info.mjpeg_url;
  } catch (e) {
    error.value = e?.message ?? String(e);
    mjpegUrl.value = "";
  }
}

onMounted(() => {
  readWebStreamPref();
  loadPreview();

  window.addEventListener("web-stream-pref-changed", onWebStreamPrefChanged);
});

onUnmounted(() => {
  window.removeEventListener("web-stream-pref-changed", onWebStreamPrefChanged);
});
</script>

<style scoped>
.previewFrame {
  width: 100%;
  height: calc(100vh - 70px);
  background: #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.previewImage {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status {
  padding: 14px;
  font-size: 16px;
  color: #111;
  max-width: 700px;
}

.hint {
  margin-top: 10px;
  font-size: 13px;
  opacity: 0.85;
}

code {
  background: rgba(0,0,0,0.08);
  padding: 2px 6px;
  border-radius: 6px;
}
</style>
