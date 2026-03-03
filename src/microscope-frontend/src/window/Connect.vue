<template>
  <div class="connect-page">
    <div class="connect-panel">
      <div class="connect-text">Connect Locally</div>

      <div v-if="connectionType === 'local'" class="connection-section">
        <div class="button-row">
          <button class="btn primary" @click="goToView">Connect</button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const connectionType = ref('local');
const host = ref('microscope.local');
const port = ref('5000');

function goToView() {
  // TODO: Add actual connection logic here
  console.log('Connecting with:', connectionType.value, host.value, port.value);
  router.push('/view');
}
</script>

<style scoped>
.connect-page {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  height: 100vh;
  width: 100%;
  background: var(--content-bg, #f5f7fa);
  padding: 40px;
  box-sizing: border-box;
}

.connect-panel {
  background: white;
  border-radius: 8px;
  padding: 32px;
  width: 100%;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.connect-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  margin-bottom: 20px;
}

.button-row {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn {
  height: 36px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  padding: 0 20px;
  border: 1px solid #1f4b7a;
  transition: filter 0.2s;
  width: 100%;
}

.btn.primary {
  background: #1f4b7a;
  color: white;
  border: 1px solid #1f4b7a;
}

.btn:hover {
  filter: brightness(0.95);
}

@media (max-width: 600px) {
  .connect-page {
    padding: 20px;
  }
  .connect-panel {
    padding: 24px;
  }
}
</style>