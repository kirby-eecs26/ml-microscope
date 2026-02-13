<template>
  <div class="connect-page">
    <div class="connect-panel">

      <!-- Radio buttons -->
      <div class="radio-group">
        <label class="radio-label">
          <input type="radio" value="local" v-model="connectionType" />
          <span>Connect locally</span>
        </label>
        <label class="radio-label">
          <input type="radio" value="remote" v-model="connectionType" />
          <span>Connect remotely</span>
        </label>
      </div>

      <!-- Local connection section -->
      <div v-if="connectionType === 'local'" class="connection-section">
        <div class="button-row">
          <button class="btn primary" @click="goToView">Connect</button>
          <button class="btn secondary">Save current</button>
        </div>
      </div>

      <!-- Remote connection section -->
      <div v-if="connectionType === 'remote'" class="connection-section">
        <div class="input-group">
          <label for="host">Host</label>
          <input 
            id="host" 
            type="text" 
            v-model="host" 
            placeholder="microscope.local"
          />
        </div>
        <div class="input-group">
          <label for="port">Port</label>
          <input 
            id="port" 
            type="text" 
            v-model="port" 
            placeholder="5000"
          />
        </div>
        <div class="button-row">
          <button class="btn primary" @click="goToView">Connect</button>
          <button class="btn secondary">Save current</button>
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
/* (styles unchanged) */
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
  max-width: 500px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  width: 16px;
  height: 16px;
  accent-color: #1f4b7a;
  margin: 0;
}

.connection-section {
  margin-top: 16px;
  border-top: 1px solid #e0e0e0;
  padding-top: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.input-group label {
  font-size: 12px;
  font-weight: 700;
  color: #555;
}

.input-group input {
  height: 36px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 12px;
  font-size: 14px;
  background: #fff;
  color: #333;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-group input:focus {
  border-color: #1f4b7a;
  box-shadow: 0 0 0 2px rgba(31,75,122,0.1);
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
}

.btn.primary {
  background: #1f4b7a;
  color: white;
  border: 1px solid #1f4b7a;
}

.btn.secondary {
  background: white;
  color: #1f4b7a;
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