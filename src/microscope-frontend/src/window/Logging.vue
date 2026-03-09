<script setup>
import { ref, computed, onMounted } from "vue";
import { fetchLogs } from "../api/loggingApi";
import { watch } from "vue";

const selectedPriority = ref("ALL"); // DEBUG/INFO/WARNING/ERROR/ALL
const loading = ref(false);
const error = ref("");
const logs = ref([]); // raw events

function levelChip(level) {
  return String(level || "").toUpperCase();
}

const filteredLogs = computed(() => {
  const lvl = selectedPriority.value?.toUpperCase() || "ALL";
  if (lvl === "ALL") return logs.value;
  return logs.value.filter(e => (e?.data?.levelname || "").toUpperCase() === lvl);
});

function formatTs(iso) {
  if (!iso) return "";
  // show like OpenFlexure-ish: M/D/YYYY HH:MM:SS AM/PM
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}

async function refreshLogs() {
  loading.value = true;
  error.value = "";
  try {
    const lvl = selectedPriority.value?.toUpperCase() || "ALL";
    const data = await fetchLogs(lvl);
    logs.value = Array.isArray(data) ? data : [];
  } catch (e) {
    error.value = String(e?.message || e);
  } finally {
    loading.value = false;
  }
}

function downloadLogFile() {
  const lines = filteredLogs.value.map((e) => {
    const ts = formatTs(e?.timestamp || e?.data?.created);
    const level = levelChip(e?.data?.levelname);
    const file = e?.data?.filename ? ` (${e.data.filename}:${e.data.lineno})` : "";
    const msg = e?.data?.message ?? "";
    return `[${ts}] ${level}${file}\n${msg}\n`;
  });

  const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `microscope_logs_${new Date().toISOString().replaceAll(":", "-")}.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

onMounted(refreshLogs);
</script>

<template>
  <div class="loggingPage">
    <div class="header">
      <div class="header-left">
        <select v-model="selectedPriority" class="priority-dropdown">
          <option value="DEBUG">DEBUG</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="ALL">ALL</option>
        </select>
      </div>

      <div class="header-right">
        <button class="refresh-btn" @click="refreshLogs" :disabled="loading">
          {{ loading ? "REFRESHING..." : "REFRESH LOGS" }}
        </button>
        <button class="download-btn" @click="downloadLogFile" :disabled="filteredLogs.length === 0">
          DOWNLOAD LOG FILE
        </button>
      </div>
    </div>

    <div class="logs-container">
      <div v-if="error" class="errorBox">{{ error }}</div>
      <div v-else-if="loading" class="muted">Loading logs...</div>
      <div v-else-if="filteredLogs.length === 0" class="muted">No logs to display.</div>

      <div v-else class="logList">
        <div v-for="(e, idx) in filteredLogs" :key="idx" class="logCard">
          <div class="logTop">
            <div class="logTime">{{ formatTs(e?.timestamp || e?.data?.created) }}</div>
            <div class="logLevel" :data-level="levelChip(e?.data?.levelname)">
              {{ levelChip(e?.data?.levelname) }}
            </div>
          </div>
          <div class="logMsg">{{ e?.data?.message }}</div>
          <div v-if="e?.data?.filename" class="logMeta">
            {{ e.data.filename }}:{{ e.data.lineno }} • {{ e.data.name }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loggingPage {
  padding: 20px;
  height: calc(100vh - 36px);
  background: var(--content-bg);
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #b3b3b3;
}

.priority-dropdown {
  height: 34px;
  padding: 0 12px;
  border: 1px solid #1f4b7a;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}
.priority-dropdown:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(31, 75, 122, 0.25);
}

.header-right { display: flex; gap: 10px; }

.refresh-btn,
.download-btn {
  height: 34px;
  padding: 0 14px;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  border: 1px solid #1f4b7a;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}

.refresh-btn:hover,
.download-btn:hover {
  filter: brightness(0.95);
}

.download-btn:disabled,
.refresh-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.logs-container {
  flex: 1;
  padding-top: 14px;
  overflow: auto;
}

.logList {
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}

.logCard {
  width: min(860px, 92%);
  border: 1px solid #1f4b7a;
  border-radius: 6px;
  padding: 14px 16px;
  background: #1f4b7a;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.logCard:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
}

.logTop {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.logTime {
  font-size: 12px;
  font-weight: 800;
  opacity: 0.9;
}

.logLevel {
  font-size: 11px;
  font-weight: 900;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.25);
  opacity: 0.95;
}

.logLevel[data-level="ERROR"] { background: rgba(221, 27, 27, 0.637); }
.logLevel[data-level="WARNING"] { background: rgba(255, 170, 0, 0.733); }
.logLevel[data-level="INFO"] { background: rgba(80, 159, 255, 0.733); }
.logLevel[data-level="DEBUG"] { background: rgba(180, 180, 180, 0.12); }

.logMsg {
  white-space: pre-wrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.35;
}

.logMeta {
  margin-top: 8px;
  font-size: 11px;
  opacity: 0.75;
}

.muted { opacity: 0.75; color: #fff; }

.errorBox {
  width: min(860px, 92%);
  margin: 0 auto;
  padding: 12px 14px;
  border: 1px solid rgba(255,80,80,0.45);
  background: rgba(255,80,80,0.12);
  border-radius: 6px;
  color: #fff;
}
</style>