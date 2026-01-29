<template>
  <div class="movePage">
    <!-- Left control panel -->
    <section class="controls">
      <div class="group">
        <div class="groupTitle">Step Size</div>

        <div class="row3">
          <button
            class="pill"
            :class="{ active: stepAxis === 'x' }"
            @click="stepAxis = 'x'"
          >
            x-step
          </button>
          <button
            class="pill"
            :class="{ active: stepAxis === 'y' }"
            @click="stepAxis = 'y'"
          >
            y-step
          </button>
          <button
            class="pill"
            :class="{ active: stepAxis === 'z' }"
            @click="stepAxis = 'z'"
          >
            z-step
          </button>
        </div>
      </div>

      <hr class="divider" />

      <div class="group">
        <div class="groupTitle">Move</div>

        <!-- Arrow pad (matches look: up arrow row, inputs row, down arrow row) -->
        <div class="arrowPad">
          <div class="padRow">
            <button class="circle" @click="nudge('x', +1)" title="+X">
              <span class="material-symbols-outlined">arrow_drop_up</span>
            </button>
            <button class="circle" @click="nudge('y', +1)" title="+Y">
              <span class="material-symbols-outlined">arrow_drop_up</span>
            </button>
            <button class="circle" @click="nudge('z', +1)" title="+Z">
              <span class="material-symbols-outlined">arrow_drop_up</span>
            </button>
          </div>

          <div class="padRow inputs">
            <input class="axisInput" v-model.number="pos.x" type="number" />
            <input class="axisInput" v-model.number="pos.y" type="number" />
            <input class="axisInput" v-model.number="pos.z" type="number" />
          </div>

          <div class="padRow">
            <button class="circle" @click="nudge('x', -1)" title="-X">
              <span class="material-symbols-outlined">arrow_drop_down</span>
            </button>
            <button class="circle" @click="nudge('y', -1)" title="-Y">
              <span class="material-symbols-outlined">arrow_drop_down</span>
            </button>
            <button class="circle" @click="nudge('z', -1)" title="-Z">
              <span class="material-symbols-outlined">arrow_drop_down</span>
            </button>
          </div>
        </div>

        <button class="primaryBtn" @click="moveNow">
          MOVE
        </button>

        <button class="secondaryBtn" @click="zeroCoordinates">
          ZERO COORDINATES
        </button>
      </div>

      <hr class="divider" />

      <div class="group">
        <div class="groupTitle">Auto-Focus</div>
        <div class="row3">
          <button
            class="pill outline"
            :class="{ active: autofocus === 'FAST' }"
            @click="runAutofocus('FAST')"
          >
            FAST
          </button>
          <button
            class="pill outline"
            :class="{ active: autofocus === 'MEDIUM' }"
            @click="runAutofocus('MEDIUM')"
          >
            MEDIUM
          </button>
          <button
            class="pill outline"
            :class="{ active: autofocus === 'FINE' }"
            @click="runAutofocus('FINE')"
          >
            FINE
          </button>
        </div>
      </div>

      <!-- Optional: tiny status line (helpful) -->
      <div class="status">
        Step: <b>{{ step }}</b> ({{ stepAxis.toUpperCase() }}) ·
        Pos: <b>{{ pos.x }}</b>, <b>{{ pos.y }}</b>, <b>{{ pos.z }}</b>
      </div>
    </section>

    <!-- Microscope preview panel -->
    <section class="preview">
      <!-- Put your camera placeholder here for now -->
      <img class="previewImg" src="/sample.jpg" alt="Microscope preview" />
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";

// Which axis step-size control is focused (matches your x-step/y-step/z-step pills)
const stepAxis = ref("x");

// Step size value used for nudging
const step = ref(1);

// Position fields (for now, just local state)
const pos = reactive({ x: 0, y: 0, z: 0 });

// Autofocus selection
const autofocus = ref("");

// Nudge logic: adjust position by +/- step
function nudge(axis, direction) {
  const delta = direction * step.value;
  pos[axis] = (Number(pos[axis]) || 0) + delta;
}

// Placeholder: later you’ll call your Python API here
function moveNow() {
  console.log("MOVE clicked:", { ...pos, step: step.value, axis: stepAxis.value });
  // Example later:
  // await fetch("/api/move", { method:"POST", headers:{...}, body: JSON.stringify({...}) })
}

function zeroCoordinates() {
  pos.x = 0; pos.y = 0; pos.z = 0;
  console.log("ZERO COORDINATES clicked");
}

function runAutofocus(mode) {
  autofocus.value = mode;
  console.log("AUTOFOCUS:", mode);
}
</script>

<style scoped>
/* Page layout: controls left, preview right */
.movePage {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 0;
  height: calc(100vh - 36px); /* matches your dark outer frame spacing */
}

/* Controls panel */
.controls {
  background: #efefef;
  color: #111;
  border-right: 1px solid #cfcfcf;
  padding: 12px;
}

.groupTitle {
  font-weight: 700;
  font-size: 12px;
  margin: 2px 0 8px;
}

.divider {
  border: none;
  border-top: 1px solid #d0d0d0;
  margin: 12px 0;
}

/* 3 buttons row */
.row3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

/* Pills (x-step/y-step/z-step, autofocus) */
.pill {
  border: 1px solid #bdbdbd;
  background: #f7f7f7;
  color: #333;
  border-radius: 8px;
  padding: 8px 6px;
  font-size: 12px;
  cursor: pointer;
}

.pill:hover {
  background: #ededed;
}

.pill.active {
  background: #1f4b7a;
  color: #fff;
  border-color: #1f4b7a;
}

.pill.outline {
  background: #fff;
}

/* Arrow pad */
.arrowPad {
  margin-top: 8px;
  display: grid;
  gap: 8px;
}

.padRow {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  align-items: center;
}

.padRow.inputs {
  gap: 10px;
}

/* Circular arrow buttons */
.circle {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: none;
  background: #1f4b7a;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.circle:hover {
  filter: brightness(1.05);
}

.circle .material-symbols-outlined {
  color: #fff;
  font-size: 22px;
  line-height: 22px;
}

/* Axis number boxes */
.axisInput {
  width: 100%;
  height: 28px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 8px;
  font-size: 12px;
  background: #fff;
}

/* MOVE / ZERO buttons */
.primaryBtn {
  width: 100%;
  margin-top: 10px;
  height: 34px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
}

.primaryBtn:hover {
  filter: brightness(1.05);
}

.secondaryBtn {
  width: 100%;
  margin-top: 10px;
  height: 34px;
  border-radius: 6px;
  border: 1px solid #1f4b7a;
  background: #fff;
  color: #1f4b7a;
  font-weight: 700;
  cursor: pointer;
}

.secondaryBtn:hover {
  background: #f3f6fb;
}

/* Small status line */
.status {
  margin-top: 12px;
  font-size: 11px;
  opacity: 0.8;
}

/* Preview area */
.preview {
  background: #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.previewImg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
