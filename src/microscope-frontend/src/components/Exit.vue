<template>
  <Teleport to="body">
    <div v-if="visible" class="exit-backdrop" @click.self="handleBackdropClick">
      <div class="exit-modal">
        <template v-if="!confirmShutdown">
          <div class="exit-title">Exit Application</div>

          <div class="exit-buttons">
            <button class="exit-btn shutdown" @click="confirmShutdown = true">
              Exit Application
            </button>
            <button class="exit-btn restart" @click="emit('restart')">
              Restart
            </button>
            <button class="exit-btn cancel" @click="emit('cancel')">
              Cancel
            </button>
          </div>
        </template>

        <template v-else>
          <div class="exit-title">Are you sure?</div>
          <div class="exit-subtitle">Do you want to close Cellular Imaging Studio?</div>

          <div class="exit-buttons">
            <button class="exit-btn shutdown" @click="emit('shutdown')">
              Yes, Exit
            </button>
            <button class="exit-btn cancel" @click="confirmShutdown = false">
              No, Go Back
            </button>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(["shutdown", "restart", "cancel", "close"]);

const confirmShutdown = ref(false);

watch(
  () => props.visible,
  (val) => {
    if (!val) confirmShutdown.value = false;
  }
);

function handleBackdropClick() {
  confirmShutdown.value = false;
  emit("close");
}
</script>

<style scoped>
.exit-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.exit-modal {
  background: #fff;
  border-radius: 8px;
  padding: 24px 32px;
  min-width: 320px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.exit-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f1f1f;
}

.exit-subtitle {
  font-size: 14px;
  color: #444;
  text-align: center;
}

.exit-buttons {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 12px;
}

.exit-btn {
  height: 40px;
  border-radius: 6px;
  border: 1px solid #1f4b7a;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: filter 0.2s;
  width: 100%;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.exit-btn:hover {
  filter: brightness(0.95);
}

.exit-btn.shutdown {
  background: #1f4b7a;
  color: #fff;
  border: 1px solid #1f4b7a;
}

.exit-btn.restart,
.exit-btn.cancel {
  background: #fff;
  color: #1f4b7a;
  border: 1px solid #1f4b7a;
}
</style>