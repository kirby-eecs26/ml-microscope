<template>
  <div class="previewFrame">
    <!-- Placeholder for live stream -->
    <img
      class="previewImage"
      src="/cell.jpg"
      alt="Microscope camera feed"
    />
  </div>
</template>

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
</style>
