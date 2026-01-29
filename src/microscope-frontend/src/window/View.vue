<template>
  <div class="viewWindow">
    <CameraPreview />
  </div>
</template>

<script setup>
import CameraPreview from "../components/CameraPreview.vue";
</script>

<style scoped>
.viewWindow {
  height: 100%;
  width: 100%;
}
</style>
