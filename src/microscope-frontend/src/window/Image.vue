<template>
  <div class="imagePage">
    <!-- Left control panel -->
    <section class="controls">
      <div class="header">IMAGE</div>

      <div class="block">
        <div class="label">Resolution</div>
        <div class="segmented">
          <button class="segBtn" :class="{ active: resolution === 'FULL' }" @click="resolution = 'FULL'">
            FULL
          </button>
          <button class="segBtn" :class="{ active: resolution === 'RAW' }" @click="resolution = 'RAW'">
            RAW
          </button>
        </div>
      </div>

      <button class="captureBtn" @click="capture" :disabled="busy">
        <span v-if="busy && busyMode === 'capture'" class="spinner"></span>
        {{ busy && busyMode === "capture" ? "CAPTURING..." : "CAPTURE" }}
      </button>
    </section>

    <!-- Live preview -->
    <section class="preview">
      <CameraPreview />
    </section>

    <!-- Image Modal -->
    <div v-if="imageModalOpen" class="backdrop" @click.self="closeCaptureModal">
      <div class="imageModal">
        <!-- Modal Header -->
        <div class="imageModalHeader">
          <div class="imageModalTitle">Image</div>
          <button class="closeX" @click="closeCaptureModal">x</button>
        </div>

        <!-- Modal Body -->
        <div class="imageModalBody">
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

            <!-- Count Cells 
            <div class="modalField">
              <div class="modalLabel">Analyze</div>
              <button class="countBtn">COUNT CELLS</button>
            </div> -->

            <!-- Save to Gallery -->
            <div class="modalFooterLeft">
              <button class="saveBtn" @click="saveToGallery" :disabled="busy || !capturedImageId">
                <span v-if="busy && busyMode === 'save'" class="spinner"></span>
                {{ busy && busyMode === "save" ? "SAVING..." : "SAVE TO GALLERY" }}
              </button>
            </div>
          </div>

          <div class="modalRight">
            <div class="modalPreviewFrame">
              <div v-if="busy && busyMode === 'capture'" class="modalLoading">
                <div class="spinner big"></div>
                <div class="loadingText">
                  Capturing {{ resolution === "RAW" ? "RAW" : "FULL" }} image…
                </div>
              </div>

              <img
                v-else
                class="modalPreviewImg"
                :src="previewUrl || '/cell.jpg'"
                alt="Captured preview"
              />
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>

</template>

<script setup>
import { captureImage, deleteCapture, updateCaptureMetadata } from "../api/imageApi";
import { ref } from "vue";
import CameraPreview from "../components/CameraPreview.vue";
import { useRouter } from 'vue-router';

const router = useRouter();

const resolution = ref("FULL");
const status = ref("");
const busy = ref(false);
const busyMode = ref(""); // "", "capture", "save", "delete"

// Image Capture reference
const capturedImageId = ref(null);

// Modal Constants
const imageModalOpen = ref(false);

const modalFilename = ref("");
const modalNotes = ref("");
const modalAnnotations = ref([]);
const modalTags = ref([]);

const annoKey = ref("");
const annoValue = ref("");
const tagInput = ref("");
const previewUrl = ref("");
const lastCaptureIsRaw = ref(false);

async function capture() {
  imageModalOpen.value = true;
  previewUrl.value = "";
  capturedImageId.value = null;

  try {
    busy.value = true;
    busyMode.value = "capture";
    status.value = "Capturing image...";

    const isRaw = resolution.value === "RAW";

    const annotationsDict = {};
    for (const a of modalAnnotations.value) {
      if (a?.key) annotationsDict[a.key] = a.value ?? "";
    }
    if (modalNotes.value?.trim()) annotationsDict["Notes"] = modalNotes.value.trim();

    const payload = {
      filename: modalFilename.value?.trim() || "capture",
      temporary: true,
      use_video_port: isRaw,
      bayer: isRaw,
      annotations: annotationsDict,
      tags: modalTags.value,
    };

    const result = await captureImage(payload);

    const cap = result.capture;
    capturedImageId.value = cap?.id ?? cap?.saved_as ?? cap?.filename ?? "";
    const base = import.meta.env.VITE_API_BASE || "";
    previewUrl.value = `${base}/captures/${encodeURIComponent(capturedImageId.value)}/image`;
    lastCaptureIsRaw.value = isRaw;

    status.value = `Captured: ${capturedImageId.value}`;
  } catch (err) {
    console.error(err);
    status.value = `Error: ${err.message}`;
  } finally {
    busy.value = false;
    busyMode.value = "";
  }
}


// Modal Functions
function openCaptureModal() {
  modalNotes.value = "";
  modalAnnotations.value = [];
  modalTags.value = [];
  annoKey.value = "";
  annoValue.value = "";
  tagInput.value = "";

  imageModalOpen.value = true;
}

function closeCaptureModal() {
  const id = capturedImageId.value;
  imageModalOpen.value = false;
  capturedImageId.value = null;
  previewUrl.value = "";
  if (id) {
    busyMode.value = "delete";
    deleteCapture(id).catch((e) => console.warn("Failed to delete temp capture:", e))
      .finally(() => {
        if (busyMode.value === "delete") busyMode.value = "";
      });
  }
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

function buildCapturePayload({ temporary }) {
  const annotationsDict = {};

  for (const a of modalAnnotations.value) {
    if (a?.key?.trim()) annotationsDict[a.key.trim()] = String(a.value ?? "");
  }

  if (modalNotes.value?.trim()) annotationsDict["Notes"] = modalNotes.value.trim();

  return {
    filename: modalFilename.value?.trim() || "capture",
    temporary,
    use_video_port: lastCaptureIsRaw.value,
    bayer: lastCaptureIsRaw.value,
    annotations: annotationsDict,
    tags: modalTags.value.map(t => t.trim()).filter(Boolean),
  };
}

async function saveToGallery() {
  try {
    busy.value = true;
    status.value = "Saving to gallery...";
    const payload = buildCapturePayload({ temporary: false });
    await captureImage(payload);
    const tempId = capturedImageId.value;
    imageModalOpen.value = false;
    router.push("/gallery");

    capturedImageId.value = null;
    previewUrl.value = "";

    if (tempId) {
      deleteCapture(tempId).catch((e) =>
        console.warn("Failed to delete temp capture:", e)
      );
    }
  } catch (e) {
    console.error(e);
    status.value = `Save failed: ${e.message}`;
  } finally {
    busy.value = false;
  }
}




</script>

<style scoped>
.imagePage {
  display: grid;
  grid-template-columns: 260px 1fr;
  height: calc(100vh - 36px);
}

/* Left panel */
.controls {
  background: #efefef;
  color: #111;
  border-right: 1px solid #cfcfcf;
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.header {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.6px;
  margin-bottom: 10px;
  opacity: 0.85;
}

.block {
  margin-bottom: 10px;
}

.label {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 6px;
}

.divider {
  height: 1px;
  background: #d0d0d0;
  margin: 10px 0;
}

.textInput {
  width: 100%;
  height: 28px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
}

.textArea {
  width: 100%;
  height: 78px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12px;
  resize: none;
  background: #fff;
}

/* Resolution buttons */
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.segBtn {
  height: 30px;
  border-radius: 6px;
  border: 1px solid #1f4b7a;
  background: #fff;
  color: #1f4b7a;
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
}

.segBtn.active {
  background: #1f4b7a;
  color: #fff;
}

/* Key/value rows */
.row {
  display: grid;
  grid-template-columns: 1fr 1fr 32px;
  gap: 8px;
  align-items: center;
}

.miniInput {
  width: 100%;
  height: 28px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
}

.iconBtn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.iconBtn .material-symbols-outlined {
  font-size: 22px;
  color: #1f4b7a;
}

/* Chips list */
.list {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1px solid #cfcfcf;
  border-radius: 999px;
  padding: 4px 8px 4px 10px;
  font-size: 11px;
}

.chipText {
  white-space: nowrap;
}

.chipX {
  border: none;
  background: transparent;
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 0;
}

.chipX .material-symbols-outlined {
  font-size: 16px;
  color: #666;
}

/* Buttons */
.grayBtn {
  width: 100%;
  height: 34px;
  border-radius: 6px;
  border: 1px solid #8a8a8a;
  background: #e5e5e5;
  color: #333;
  font-weight: 700;
  cursor: pointer;
}

.grayBtn:hover {
  filter: brightness(0.98);
}

.spacer {
  flex: 1;
}

.captureBtn {
  width: 100%;
  height: 40px;
  border-radius: 6px;
  border: none;
  background: #1f4b7a;
  color: #fff;
  font-weight: 800;
  letter-spacing: 0.6px;
  cursor: pointer;
  margin-top: auto;
}

.captureBtn:hover {
  filter: brightness(1.05);
}

/* Preview */
.preview {
  background: #d9d9d9;
  overflow: hidden;
}

/* ===== Modal styles ===== */
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.imageModal {
  width: min(1100px, 92vw);
  height: min(640px, 84vh);
  background: #efefef;
  border: 1px solid #cfcfcf;
  border-radius: 6px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
}

.imageModalHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.imageModalTitle {
  font-size: 14px;
  font-weight: 800;
  color: #111;
}

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

.imageModalBody {
  margin-top: 10px;
  flex: 1;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 14px;
  min-height: 0;
}

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

.modalField:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.modalLabel {
  font-size: 12px;
  font-weight: 800;
}

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

.annoRow,
.tagRow {
  display: grid;
  grid-template-columns: 1fr 1fr 34px;
  gap: 8px;
  align-items: center;
}

.miniInput {
  height: 28px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
  width: 100%;
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

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

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

.chipX .material-symbols-outlined {
  font-size: 16px;
  color: #666;
}

/*.countBtn {
  height: 30px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: default;   inert – no pointer 
  width: 160px;
  opacity: 0.8;
}*/

.modalFooterLeft {
  margin-top: auto;
  display: flex;
  justify-content: flex-start;
}

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

.saveBtn:hover {
  filter: brightness(0.95);
}

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
}

.modalPreviewImg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captureBtn:disabled,
.saveBtn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.6);
  border-top-color: rgba(255,255,255,1);
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

.spinner.big {
  width: 26px;
  height: 26px;
  border-width: 3px;
  margin-right: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modalLoading {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  gap: 10px;
  color: #fff;
}

.loadingText {
  font-size: 14px;
  font-weight: 700;
  opacity: 0.9;
}

</style>
