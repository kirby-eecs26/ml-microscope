<template>
  <div class="videoPage">
    <!-- LEFT: only Resolution + Frame rate -->
    <section class="controls">
      <div class="controlTitle">VIDEO</div>

      <div class="field">
        <div class="label">Resolution</div>
        <div class="row2">
          <button class="pill" :class="{ active: resolution === 'FULL' }" @click="resolution = 'FULL'">FULL</button>
          <button class="pill" :class="{ active: resolution === 'RAW' }" @click="resolution = 'RAW'">RAW</button>
        </div>
      </div>

      <div class="field">
        <div class="label">Frames-per-Minute (FPM)</div>
        <div class="row2">
          <button class="pill" :class="{ active: frameRate === 60 }" @click="setPreset(60)">60</button>
          <button class="pill" :class="{ active: frameRate === 30 }" @click="setPreset(30)">30</button>
        </div>

        <div class="rowCustom">
          <input class="miniInput" v-model.number="customRate" type="number" placeholder="fpm" min="1" />
          <button class="setBtn" @click="setCustom">SET</button>
        </div>
      </div>

      <div class="spacer"></div>

      <button v-if="!recording" class="primaryBtn" @click="startRecording" :disabled="busy">
        <span v-if="busy && busyMode === 'start'" class="spinner"></span>
        {{ busy && busyMode === "start" ? "STARTING..." : "START VIDEO" }}
      </button>

      <button v-else class="primaryBtn" @click="stopRecording" :disabled="busy">
        <span v-if="busy && busyMode === 'stop'" class="spinner"></span>
        {{ busy && busyMode === "stop" ? "STOPPING..." : "STOP VIDEO" }}
      </button>

      <div class="statusTextSmall" v-if="status">{{ status }}</div>
    </section>

    <!-- CENTER live preview  -->
    <section class="preview">
      <CameraPreview />
    </section>

    <!-- RIGHT status -->
    <section class="statusPanel">
      <div class="statusRow">
        <span class="dot" :class="{ on: connected }"></span>
        <span class="statusText">{{ connected ? "Connected" : "Disconnected" }}</span>
      </div>
    </section>

    <!-- STOP -> Modal -->
    <div v-if="stopModalOpen" class="backdrop" @click.self="closeStopModal">
      <div class="videoModal">
        <div class="videoModalHeader">
          <div class="videoModalTitle">Video</div>
          <button class="closeX" @click="closeStopModal">×</button>
        </div>

        <div class="videoModalBody">
          <!-- Left pane in modal -->
          <div class="modalLeft">
            <!-- Filename -->
            <div class="modalField">
              <div class="modalLabel">Filename</div>
              <input class="textInput" v-model="modalFilename" placeholder="filename" />
            </div>

            <!-- Notes -->
            <div class="modalField">
              <div class="modalLabel">Notes</div>
              <textarea class="textArea" v-model="modalNotes" placeholder="Notes"></textarea>
            </div>

            <!-- Annotations -->
            <div class="modalField">
              <div class="modalLabel">Annotations</div>
              <div class="annoRow">
                <input class="miniInput" v-model="annoKey" placeholder="key" />
                <input class="miniInput" v-model="annoValue" placeholder="value" />
                <button class="plusBtn" @click="addAnnotation" title="Add annotation">
                  <span class="material-symbols-outlined">add_circle</span>
                </button>
              </div>

              <div v-if="modalAnnotations.length" class="chips">
                <div class="chip" v-for="(a, i) in modalAnnotations" :key="i">
                  {{ a.key }}: {{ a.value }}
                  <button class="chipX" @click="modalAnnotations.splice(i, 1)" title="Remove">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Tags -->
            <div class="modalField">
              <div class="modalLabel">Tags</div>
              <div class="tagRow">
                <input class="miniInput" v-model="tagInput" placeholder="tag" />
                <button class="plusBtn" @click="addTag" title="Add tag">
                  <span class="material-symbols-outlined">add_circle</span>
                </button>
              </div>

              <div v-if="modalTags.length" class="chips">
                <div class="chip" v-for="(t, i) in modalTags" :key="i">
                  {{ t }}
                  <button class="chipX" @click="modalTags.splice(i, 1)" title="Remove">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Analyze -->
            <div class="modalField">
              <div class="modalLabel">Analyze</div>
              <button class="countBtn" @click="countCells" :disabled="busy || !recordedVideoId">
                <span v-if="busy && busyMode === 'count'" class="spinner"></span>
                {{ busy && busyMode === "count" ? "COUNTING..." : "COUNT CELLS" }}
              </button>
              <div v-if="cellCount !== null" class="countResult">Cell Count: {{ cellCount }}</div>
            </div>

            <!-- Save -->
            <div class="modalFooterLeft">
              <button class="saveBtn" @click="saveToGallery" :disabled="busy || !recordedVideoId">
                <span v-if="busy && busyMode === 'save'" class="spinner"></span>
                {{ busy && busyMode === "save" ? "SAVING..." : "SAVE TO GALLERY" }}
              </button>
            </div>
          </div>

          <!-- Right preview in modal (live view OR preview frame if backend provides) -->
          <div class="modalRight">
            <div class="modalPreviewFrame">
              <img v-if="stopPreviewUrl" class="modalPreviewImg" :src="stopPreviewUrl" alt="Video frame preview" />
              <CameraPreview v-else />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import CameraPreview from "../components/CameraPreview.vue";
import { startVideo, stopVideo, analyzeVideo, saveVideoToGallery } from "../api/videoApi";

const connected = ref(true);

const resolution = ref("FULL"); // FULL | RAW
const frameRate = ref(60);      // Frames-per-Minute (demo)
const customRate = ref(null);

const recording = ref(false);
const busy = ref(false);
const busyMode = ref(""); // "start" | "stop" | "count" | "save"
const status = ref("");

const recordingId = ref(null);     // id returned by startVideo
const recordedVideoId = ref(null); // id returned by stopVideo (final artifact)

// STOP modal
const stopModalOpen = ref(false);
const stopPreviewUrl = ref(""); // optional preview image from backend

const modalFilename = ref("filename");
const modalNotes = ref("");
const modalAnnotations = ref([]);
const modalTags = ref([]);
const annoKey = ref("");
const annoValue = ref("");
const tagInput = ref("");
const cellCount = ref(null);

function setPreset(n) {
  frameRate.value = n;
  customRate.value = null;
}

function setCustom() {
  const n = Number(customRate.value);
  if (!Number.isFinite(n) || n <= 0) return;
  frameRate.value = n;
}

async function startRecording() {
  try {
    busy.value = true;
    busyMode.value = "start";
    status.value = "Starting recording...";

    const isRaw = resolution.value === "RAW";
    const payload = {
      resolution: resolution.value,
      frames_per_minute: frameRate.value,
      use_video_port: isRaw,
      bayer: isRaw,
    };

    const result = await startVideo(payload);

    // accept either { id } or { recording: { id } }
    recordingId.value = result?.id ?? result?.recording?.id ?? null;
    recording.value = true;
    status.value = "Recording...";
  } catch (e) {
    console.error(e);
    status.value = `Start failed: ${e?.message ?? e}`;
  } finally {
    busy.value = false;
    busyMode.value = "";
  }
}

async function stopRecording() {
  try {
    busy.value = true;
    busyMode.value = "stop";
    status.value = "Stopping recording...";

    const result = await stopVideo({ recording_id: recordingId.value });

    // accept either { video: { id } } or { id }
    recordedVideoId.value = result?.video?.id ?? result?.id ?? recordingId.value;
    recordingId.value = null;
    recording.value = false;

    // optional preview image endpoint from backend
    const preview = result?.preview_url;
    if (preview) {
      stopPreviewUrl.value = preview;
    } else {
      const base = import.meta.env.VITE_API_BASE || "";
      // if backend exposes a still frame for the recorded video
      stopPreviewUrl.value = recordedVideoId.value ? `${base}/videos/${encodeURIComponent(recordedVideoId.value)}/preview` : "";
    }

    openStopModal();
    status.value = "Stopped.";
  } catch (e) {
    console.error(e);
    status.value = `Stop failed: ${e?.message ?? e}`;
  } finally {
    busy.value = false;
    busyMode.value = "";
  }
}

function openStopModal() {
  stopModalOpen.value = true;
  cellCount.value = null;
}

function closeStopModal() {
  stopModalOpen.value = false;
  stopPreviewUrl.value = "";
}

function addAnnotation() {
  if (!annoKey.value || !annoValue.value) return;
  modalAnnotations.value.push({ key: annoKey.value, value: annoValue.value });
  annoKey.value = "";
  annoValue.value = "";
}

function addTag() {
  const t = tagInput.value.trim();
  if (!t) return;
  modalTags.value.push(t);
  tagInput.value = "";
}

function buildMetadataPayload() {
  const annotationsDict = {};
  for (const a of modalAnnotations.value) {
    if (a?.key?.trim()) annotationsDict[a.key.trim()] = String(a.value ?? "");
  }
  if (modalNotes.value?.trim()) annotationsDict["Notes"] = modalNotes.value.trim();

  return {
    filename: modalFilename.value?.trim() || "video",
    notes: modalNotes.value,
    annotations: annotationsDict,
    tags: modalTags.value.map(t => t.trim()).filter(Boolean),
    resolution: resolution.value,
    frames_per_minute: frameRate.value,
  };
}

async function countCells() {
  try {
    busy.value = true;
    busyMode.value = "count";
    status.value = "Running analysis...";

    const id = recordedVideoId.value;
    const result = await analyzeVideo(id, { type: "count_cells" });

    // accept either { cell_count } or { analysis: { cell_count } }
    cellCount.value = result?.cell_count ?? result?.analysis?.cell_count ?? result?.count ?? 0;
    status.value = "Analysis complete.";
  } catch (e) {
    console.error(e);
    status.value = `Analysis failed: ${e?.message ?? e}`;
  } finally {
    busy.value = false;
    busyMode.value = "";
  }
}

async function saveToGallery() {
  try {
    busy.value = true;
    busyMode.value = "save";
    status.value = "Saving to gallery...";

    const id = recordedVideoId.value;
    const payload = buildMetadataPayload();

    // include analysis result if present
    if (cellCount.value !== null) payload.analysis = { cell_count: cellCount.value };

    await saveVideoToGallery(id, payload);

    stopModalOpen.value = false;
    status.value = "Saved.";
  } catch (e) {
    console.error(e);
    status.value = `Save failed: ${e?.message ?? e}`;
  } finally {
    busy.value = false;
    busyMode.value = "";
  }
}
</script>

<style scoped>
.videoPage {
  height: calc(100vh - 36px);
  display: grid;
  grid-template-columns: 260px 1fr 220px;
  background: var(--content-bg);
}

/* LEFT controls */
.controls {
  background: var(--sidebar-bg);
  color: var(--text-dark);
  border-right: 1px solid #cfcfcf;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.controlTitle {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.6px;
  opacity: 0.35;
  margin-bottom: 2px;
}

.field { display: grid; gap: 6px; }
.label { font-size: 12px; font-weight: 700; }

.row2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.rowCustom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-items: center;
}

.pill {
  height: 30px;
  border: 1px solid #bdbdbd;
  background: #fff;
  color: #333;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.pill.active {
  background: #1f4b7a;
  color: #fff;
  border-color: #1f4b7a;
}

.miniInput {
  height: 30px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
  color: #111;
  outline: none;
  min-width: 0;
}

.setBtn {
  height: 30px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
}

.spacer { flex: 1; }

.primaryBtn {
  height: 34px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
}

.primaryBtn:hover, .setBtn:hover { filter: brightness(0.95); }

.statusTextSmall {
  font-size: 12px;
  opacity: 0.75;
}

/* CENTER preview */
.preview {
  background: var(--content-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* RIGHT status */
.statusPanel {
  background: var(--sidebar-bg);
  border-left: 1px solid #cfcfcf;
  padding: 12px;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
}

.statusRow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-dark);
  font-size: 12px;
  font-weight: 700;
}

.dot { width: 8px; height: 8px; border-radius: 999px; background: #9a9a9a; }
.dot.on { background: #2ecc71; }

/* Modal */
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.videoModal {
  width: min(1100px, 92vw);
  height: min(640px, 84vh);
  background: #efefef;
  border: 1px solid #cfcfcf;
  border-radius: 6px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.35);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
}

.videoModalHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.videoModalTitle { font-size: 14px; font-weight: 800; color: #111; }

.closeX {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #333;
}

.videoModalBody {
  margin-top: 10px;
  flex: 1;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 14px;
  min-height: 0;
}

/* left pane */
.modalLeft {
  background: #f6f6f6;
  border: 1px solid #d0d0d0;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.modalField {
  display: grid;
  gap: 6px;
  padding-bottom: 10px;
  border-bottom: 1px solid #d8d8d8;
}

.modalField:last-of-type { border-bottom: none; padding-bottom: 0; }

.modalLabel { font-size: 12px; font-weight: 800; }

.textInput {
  height: 30px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
  outline: none;
}

.textArea {
  min-height: 80px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12px;
  background: #fff;
  outline: none;
  resize: vertical;
}

.annoRow, .tagRow {
  display: grid;
  grid-template-columns: 1fr 1fr 34px;
  gap: 8px;
  align-items: center;
}

.plusBtn {
  width: 34px;
  height: 30px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.plusBtn .material-symbols-outlined {
  font-size: 22px;
  color: #1f4b7a;
}

.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #bdbdbd;
  background: #fff;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
}

.chipX {
  border: none;
  background: transparent;
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 0;
}

.chipX .material-symbols-outlined { font-size: 16px; color: #666; }

.countBtn {
  height: 30px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
  width: 160px;
}

.countResult { margin-top: 8px; font-size: 12px; font-weight: 700; color: #333; }

.modalFooterLeft { margin-top: auto; display: flex; justify-content: flex-start; }

.saveBtn {
  height: 34px;
  width: 210px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
}

.saveBtn:hover, .countBtn:hover { filter: brightness(0.95); }

/* right pane */
.modalRight {
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e3e3e3;
  border: 1px solid #d0d0d0;
  padding: 12px;
}

.modalPreviewFrame {
  width: 100%;
  height: 100%;
  max-height: 520px;
  border: 1px solid #8f8f8f;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.modalPreviewImg { width: 100%; height: 100%; object-fit: cover; }

/* spinner for busy buttons */
.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: rgba(255,255,255,1);
  border-radius: 999px;
  margin-right: 8px;
  vertical-align: -2px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
