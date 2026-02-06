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

        <button class="primaryBtn" @click="moveNow">MOVE</button>

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

      <div class="status">
        Step: <b>{{ step }}</b> ({{ stepAxis.toUpperCase() }}) ·
        Pos: <b>{{ pos.x }}</b>, <b>{{ pos.y }}</b>, <b>{{ pos.z }}</b>
      </div>

      <div class="status" v-if="moveStatus">
        {{ moveStatus }}
      </div>
    </section>

    <!-- Microscope preview panel -->
    <section class="preview">
      <CameraPreview />
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import CameraPreview from "../components/CameraPreview.vue";
import { moveAbs } from "../api/imageApi";

const stepAxis = ref("x");
const step = ref(500); // 1 is too small for noticeable movement

const pos = reactive({ x: 0, y: 0, z: 0 });

const autofocus = ref("");
const moveStatus = ref("");

async function nudge(axis, direction) {
  const old = pos[axis];
  const delta = direction * step.value;
  pos[axis] = (Number(pos[axis]) || 0) + delta;

  // If the backend rejects bounds, revert so you don't "lose" the coordinate truth
  try {
    await moveNow();
  } catch {
    pos[axis] = old;
  }
}

async function moveNow() {
  moveStatus.value = "Moving...";
  try {
    await moveAbs(pos.x, pos.y, pos.z);
    moveStatus.value = "Move sent ✅";
  } catch (e) {
    moveStatus.value = `Move failed: ${e?.message ?? String(e)}`;
    throw e; // important so nudge() can revert on failure
  }
}

function zeroCoordinates() {
  pos.x = 0;
  pos.y = 0;
  pos.z = 0;
  moveStatus.value = "Zeroed (not moved yet)";
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
  height: calc(100vh - 36px);
}

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

.row3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

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

.axisInput {
  width: 100%;
  height: 28px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 8px;
  font-size: 12px;
  background: #fff;
}

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

.status {
  margin-top: 12px;
  font-size: 11px;
  opacity: 0.8;
}

.preview {
  background: #d9d9d9;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
