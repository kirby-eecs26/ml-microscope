<template>
  <div class="videoPage">
    <!-- Left control panel -->
    <section class="controls">
      <div class="controlTitle">VIDEO</div>

      <div class="field">
        <div class="label">Filename</div>
        <input class="textInput" v-model="filename" placeholder="filename" />
      </div>

      <div class="field">
        <div class="label">Resolution</div>
        <div class="row2">
          <button class="pill" :class="{ active: resolution === 'FULL' }" @click="resolution = 'FULL'">
            FULL
          </button>
          <button class="pill" :class="{ active: resolution === 'RAW' }" @click="resolution = 'RAW'">
            RAW
          </button>
        </div>
      </div>

      <div class="field">
        <div class="label">Frames-per-Hour (FPH)</div>
        <div class="row2">
          <button class="pill" :class="{ active: fphPreset === 60 }" @click="setPreset(60)">
            60 FPH
          </button>
          <button class="pill" :class="{ active: fphPreset === 30 }" @click="setPreset(30)">
            30 FPH
          </button>
        </div>

        <div class="rowCustom">
          <input class="miniInput" v-model.number="customFph" type="number" placeholder="fph" min="1" />
          <button class="setBtn" @click="setCustomFph">SET FPH</button>
        </div>
      </div>

      <div class="field">
        <div class="label">Notes</div>
        <textarea class="textArea" v-model="notes" placeholder="Notes" />
      </div>

      <div class="field">
        <div class="label">Annotations</div>
        <div class="annoRow">
          <input class="miniInput" v-model="annoKey" placeholder="key" />
          <input class="miniInput" v-model="annoValue" placeholder="value" />
          <button class="plusBtn" @click="addAnnotation" title="Add annotation">
            <span class="material-symbols-outlined">add_circle</span>
          </button>
        </div>

        <div v-if="annotations.length" class="chips">
          <div class="chip" v-for="(a, i) in annotations" :key="i">
            {{ a.key }}: {{ a.value }}
            <button class="chipX" @click="annotations.splice(i, 1)" title="Remove">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
      </div>

      <div class="field">
        <div class="label">Tags</div>
        <div class="tagRow">
          <input class="miniInput" v-model="tagInput" placeholder="tag" />
          <button class="plusBtn" @click="addTag" title="Add tag">
            <span class="material-symbols-outlined">add_circle</span>
          </button>
        </div>

        <div v-if="tags.length" class="chips">
          <div class="chip" v-for="(t, i) in tags" :key="i">
            {{ t }}
            <button class="chipX" @click="tags.splice(i, 1)" title="Remove">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
      </div>

      <div class="spacer"></div>

      <button class="startBtn" @click="startVideo">
        START VIDEO
      </button>
    </section>

    <!-- Center preview -->
    <section class="preview">
      <!-- If you already have a live stream component, swap this in -->
      <!-- <CameraPreview /> -->

      <!-- Placeholder image to match your other screens -->
      <img class="previewImg" src="/cell.jpg" alt="Microscope preview" />
    </section>

    <!-- Right status panel -->
    <section class="statusPanel">
      <div class="statusRow">
        <span class="dot" :class="{ on: connected }"></span>
        <span class="statusText">{{ connected ? "Connected" : "Disconnected" }}</span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from "vue";
// import CameraPreview from "../components/CameraPreview.vue";

const connected = ref(true);

const filename = ref("");
const resolution = ref("FULL"); // FULL | RAW

const fphPreset = ref(60);
const customFph = ref(null);

const notes = ref("");

const annoKey = ref("");
const annoValue = ref("");
const annotations = ref([]);

const tagInput = ref("");
const tags = ref([]);

function setPreset(n) {
  fphPreset.value = n;
  customFph.value = null;
}

function setCustomFph() {
  const n = Number(customFph.value);
  if (!Number.isFinite(n) || n <= 0) return;
  fphPreset.value = n; // treat custom as the active FPH value
}

function addAnnotation() {
  if (!annoKey.value || !annoValue.value) return;
  annotations.value.push({ key: annoKey.value, value: annoValue.value });
  annoKey.value = "";
  annoValue.value = "";
}

function addTag() {
  const t = tagInput.value.trim();
  if (!t) return;
  tags.value.push(t);
  tagInput.value = "";
}

function startVideo() {
  // Replace this with your API call later
  const payload = {
    filename: filename.value.trim(),
    resolution: resolution.value,
    fph: fphPreset.value,
    notes: notes.value,
    annotations: annotations.value,
    tags: tags.value,
  };
  console.log("START VIDEO:", payload);
}
</script>

<style scoped>
/* 3 columns: controls | preview | status */
.videoPage {
  height: calc(100vh - 36px);
  display: grid;
  grid-template-columns: 260px 1fr 220px;
  background: var(--content-bg);
}

/* LEFT: controls */
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

.field {
  display: grid;
  gap: 6px;
}

.label {
  font-size: 12px;
  font-weight: 700;
}

.textInput {
  height: 30px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
  color: #111;
  outline: none;
}

.textArea {
  min-height: 90px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12px;
  background: #fff;
  color: #111;
  outline: none;
  resize: vertical;
}

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

.annoRow,
.tagRow {
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

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
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

.spacer {
  flex: 1;
}

.startBtn {
  height: 34px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
}

.startBtn:hover,
.setBtn:hover {
  filter: brightness(0.95);
}

/* CENTER: preview */
.preview {
  background: var(--content-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.previewImg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* RIGHT: status */
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

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #9a9a9a;
}

.dot.on {
  background: #2ecc71;
}
</style>
