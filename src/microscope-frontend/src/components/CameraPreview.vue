<template>
  <div class="previewFrame">
    <div v-if="error" class="status">{{ error }}</div>
    <div v-else-if="!mjpegUrl" class="status">Loading live feed…</div>

    <!-- MJPEG streams work directly in <img> -->
    <img
      v-else
      class="previewImage"
      :src="mjpegUrl"
      alt="Microscope camera feed"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const mjpegUrl = ref("");
const error = ref("");

onMounted(async () => {
  try {
    // simplest approach: just point directly at your backend stream endpoint
    mjpegUrl.value = "http://microscope.local:5000/api/v2/streams/mjpeg";
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
  padding: 12px;
  font-size: 16px;
}
</style>
