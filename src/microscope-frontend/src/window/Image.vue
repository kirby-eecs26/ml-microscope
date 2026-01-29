<template>
  <div class="imagePage">
    <!-- Left control panel -->
    <section class="controls">
      <div class="header">IMAGE</div>

      <div class="block">
        <div class="label">Filename</div>
        <input class="textInput" v-model="filename" placeholder="filename" />
      </div>

      <div class="divider"></div>

      <div class="block">
        <div class="label">Resolution</div>
        <div class="segmented">
          <button
            class="segBtn"
            :class="{ active: resolution === 'FULL' }"
            @click="resolution = 'FULL'"
          >
            FULL
          </button>
          <button
            class="segBtn"
            :class="{ active: resolution === 'RAW' }"
            @click="resolution = 'RAW'"
          >
            RAW
          </button>
        </div>
      </div>

      <div class="divider"></div>

      <div class="block">
        <div class="label">Notes</div>
        <textarea class="textArea" v-model="notes" placeholder="Notes"></textarea>
      </div>

      <div class="divider"></div>

      <div class="block">
        <div class="label">Annotations</div>

        <div class="row">
          <input class="miniInput" v-model="annoKey" placeholder="key" />
          <input class="miniInput" v-model="annoValue" placeholder="value" />
          <button class="iconBtn" @click="addAnnotation" title="Add annotation">
            <span class="material-symbols-outlined">add_circle</span>
          </button>
        </div>

        <div class="list" v-if="annotations.length">
          <div class="chip" v-for="(a, i) in annotations" :key="i">
            <span class="chipText">{{ a.key }}: {{ a.value }}</span>
            <button class="chipX" @click="removeAnnotation(i)" title="Remove">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="block">
        <div class="label">Tags</div>

        <div class="row">
          <input class="miniInput" v-model="tagInput" placeholder="tag" />
          <button class="iconBtn" @click="addTag" title="Add tag">
            <span class="material-symbols-outlined">add_circle</span>
          </button>
        </div>

        <div class="list" v-if="tags.length">
          <div class="chip" v-for="(t, i) in tags" :key="i">
            <span class="chipText">{{ t }}</span>
            <button class="chipX" @click="removeTag(i)" title="Remove">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
      </div>

      <div class="divider"></div>

      <div class="block">
        <button class="grayBtn" @click="countCells">
          COUNT CELLS
        </button>
      </div>

      <div class="spacer"></div>

      <button class="captureBtn" @click="capture">
        CAPTURE
      </button>
    </section>

    <!-- Live preview -->
    <section class="preview">
      <CameraPreview />
    </section>
  </div>
</template>

<script setup>
import { captureImage} from "../api/imageApi";
import { ref } from "vue";
import CameraPreview from "../components/CameraPreview.vue";

const filename = ref("");
const resolution = ref("FULL");
const notes = ref("");

const annoKey = ref("");
const annoValue = ref("");
const annotations = ref([]);

const tagInput = ref("");
const tags = ref([]);

const status = ref("");
const busy = ref(false);

function addAnnotation() {
  const k = annoKey.value.trim();
  const v = annoValue.value.trim();
  if (!k || !v) return;
  annotations.value.push({ key: k, value: v });
  annoKey.value = "";
  annoValue.value = "";
}

function removeAnnotation(i) {
  annotations.value.splice(i, 1);
}

function addTag() {
  const t = tagInput.value.trim();
  if (!t) return;
  tags.value.push(t);
  tagInput.value = "";
}

function removeTag(i) {
  tags.value.splice(i, 1);
}

// Frontend-only placeholders for now
function countCells() {
  console.log("COUNT CELLS", {
    filename: filename.value,
    resolution: resolution.value,
    notes: notes.value,
    annotations: annotations.value,
    tags: tags.value,
  });
}

async function capture() {
  try {
    busy.value = true;
    status.value = "Capturing image...";
    const payload = {
      filename: filename.value,
      resolution: resolution.value,
      notes: notes.value,
      annotations: annotations.value,
      tags: tags.value,
    };

    const result = await captureImage(payload);
    console.log("CAPTURE RESULT:", result); // browser console proof
    status.value = `Saved: ${result.saved_as ?? "success"}`;
  } catch (err) {
    console.error(err);
    status.value = `Error: ${err.message}`;
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
}

.captureBtn:hover {
  filter: brightness(1.05);
}

/* Preview */
.preview {
  background: #d9d9d9;
  overflow: hidden;
}
</style>
