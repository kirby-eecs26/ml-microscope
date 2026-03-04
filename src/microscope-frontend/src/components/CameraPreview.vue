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
import { ref, onMounted } from "vue";
import { getLiveInfo, microscopeHealth } from "../api/imageApi";

const mjpegUrl = ref("");
const error = ref("");

function onImgError() {
  error.value =
    "Live feed unavailable (microscope not reachable from this PC).";
  mjpegUrl.value = "";
}

onMounted(async () => {
  try {
    // 1) quick check (optional but gives nicer error)
    const ok = await microscopeHealth().catch(() => false);
    if (!ok) {
      error.value =
        "Microscope not connected. Plug it in / join its network, then reopen.";
      return;
    }

    // 2) ask backend for the direct URL (no proxy)
    const info = await getLiveInfo();
    mjpegUrl.value = info.mjpeg_url; // e.g. http://microscope.local:5000/api/v2/streams/mjpeg
  } catch (e) {
    error.value = e?.message ?? String(e);
  }
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
