<template>
  <aside class="sidebar">
    <RouterLink class="nav" to="/view">
      <span class="material-symbols-outlined icon">visibility</span>
      <span class="label">View</span>
    </RouterLink>

    <RouterLink class="nav" to="/gallery">
      <span class="material-symbols-outlined icon">photo_library</span>
      <span class="label">Gallery</span>
    </RouterLink>

    <RouterLink class="nav" to="/move">
      <span class="material-symbols-outlined icon">open_with</span>
      <span class="label">Move</span>
    </RouterLink>

    <RouterLink class="nav" to="/capture">
      <span class="material-symbols-outlined icon">photo_camera</span>
      <span class="label">Capture</span>
    </RouterLink>
    
    <div class="spacer"></div>

    <RouterLink class="nav" to="/about">
      <span class="material-symbols-outlined icon">info</span>
      <span class="label">About</span>
    </RouterLink>

    <RouterLink class="nav" to="/logging">
      <span class="material-symbols-outlined icon">description</span>
      <span class="label">Logging</span>
    </RouterLink>

    <RouterLink class="nav" to="/settings">
      <span class="material-symbols-outlined icon">settings</span>
      <span class="label">Settings</span>
    </RouterLink>

    <a class="nav plain" href="#" @click.prevent="openExitModal">
      <span class="material-symbols-outlined icon">power_settings_new</span>
      <span class="label">Exit</span>
    </a>
  </aside>

  <ExitModal :visible="exitModalVisible" @shutdown="shutdown" @restart="restart" @cancel="closeExitModal" @close="closeExitModal"/>

</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ExitModal from './Exit.vue';

const router = useRouter();
const exitModalVisible = ref(false);

function openExitModal() {
  exitModalVisible.value = true;
}

function closeExitModal() {
  exitModalVisible.value = false;
}
async function shutdown() {
  try {
    closeExitModal();

    if (window.electronAPI?.quitApp) {
      await window.electronAPI.quitApp();
      return;
    }
    window.close();
  } catch (e) {
    console.error('Shutdown failed:', e);
  }
}

function restart() {
  closeExitModal();
  router.push('/');
}
</script>

<style scoped>
.sidebar {
  width: 90px;
  background: var(--sidebar-bg);
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 6px;
  border-radius: 6px;
  text-decoration: none;
  color: var(--text-dark);
  font-size: 11px;
}

.nav:hover {
  background: var(--sidebar-hover);
}

.nav.router-link-active {
  background: var(--sidebar-active);
  color: #fff;
}

.icon {
  font-size: 18px;
  line-height: 18px;
}

.label {
  line-height: 12px;
}

.spacer {
  flex: 1;
}

.plain {
  cursor: pointer;
}
</style>
