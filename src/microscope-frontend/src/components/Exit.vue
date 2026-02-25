<template>
  <Teleport to="body">
    <div v-if="visible" class="exit-backdrop" @click.self="handleBackdropClick">
      <div class="exit-modal">
        <div class="exit-buttons">
          <button class="exit-btn shutdown" @click="emit('shutdown')">Shutdown</button>
          <button class="exit-btn restart" @click="emit('restart')">Restart</button>
          <button class="exit-btn cancel" @click="emit('cancel')">Cancel</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['shutdown', 'restart', 'cancel', 'close']);

function handleBackdropClick() {
  emit('close');
}
</script>

<style scoped>
/* Backdrop – same as your video/image modal */
.exit-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

/* Modal panel – clean white, matching your UI */
.exit-modal {
  background: #fff;
  border-radius: 8px;
  padding: 24px 32px;
  min-width: 280px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

/* Button container – vertical stack */
.exit-buttons {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 12px;
}

/* Base button styles – exactly like .segBtn */
.exit-btn {
  height: 40px;              /* slightly taller for easier clicking */
  border-radius: 6px;
  border: 1px solid #1f4b7a;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: filter 0.2s;
  background: 0.2s;
  width: 100%;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Shutdown = active style (blue fill, white text) */
.exit-btn.shutdown {
  background: #1f4b7a;
  color: #fff;
  border: 1px solid #1f4b7a;
}

/* Restart & Cancel = inactive style (white fill, blue text, blue border) */
.exit-btn.restart,
.exit-btn.cancel {
  background: #fff;
  color: #1f4b7a;
  border: 1px solid #1f4b7a;
}
</style>
