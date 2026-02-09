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
            <input class="axisInput" v-model.number="target.x" type="number" />
            <input class="axisInput" v-model.number="target.y" type="number" />
            <input class="axisInput" v-model.number="target.z" type="number" />
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

        <button class="secondaryBtn" @click="centerNow">
          CENTER STAGE
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
        Step: <b>{{ step }}</b> ·
        Target: <b>{{ target.x }}</b>, <b>{{ target.y }}</b>, <b>{{ target.z }}</b> ·
        Current: <b>{{ current.x }}</b>, <b>{{ current.y }}</b>, <b>{{ current.z }}</b>
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
import { reactive, ref, onMounted } from "vue";
import CameraPreview from "../components/CameraPreview.vue";
import { moveAbs, getPosition, centerStage } from "../api/imageApi";

const stepAxis = ref("x");
const step = ref(500);

const target = reactive({ x: 0, y: 0, z: 0 });   // editable values (UI)
const current = reactive({ x: 0, y: 0, z: 0 });  // actual microscope position

const autofocus = ref("");
const moveStatus = ref("");

function setBoth(pos) {
  target.x = Number(pos.x) || 0;
  target.y = Number(pos.y) || 0;
  target.z = Number(pos.z) || 0;

  current.x = Number(pos.x) || 0;
  current.y = Number(pos.y) || 0;
  current.z = Number(pos.z) || 0;

  localStorage.setItem("lastStagePos", JSON.stringify({ x: current.x, y: current.y, z: current.z }));
}

function normalizePos(data) {
  const pos = data?.position ?? data ?? {};
  return {
    x: Number(pos.x) || 0,
    y: Number(pos.y) || 0,
    z: Number(pos.z) || 0,
  };
}

async function refreshPositionSafe() {
  const data = await getPosition();
  const pos = normalizePos(data);

  current.x = pos.x;
  current.y = pos.y;
  current.z = pos.z;

  localStorage.setItem("lastStagePos", JSON.stringify(pos));
  return pos;
}

function almostEqual(a, b, tol = 50) {
  return Math.abs(a - b) <= tol;
}

function atTarget(pos, tgt, tol = 50) {
  return (
    almostEqual(pos.x, tgt.x, tol) &&
    almostEqual(pos.y, tgt.y, tol) &&
    almostEqual(pos.z, tgt.z, tol)
  );
}

async function waitUntilAtTarget(tgt, maxMs = 45000) {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    const pos = await refreshPositionSafe();
    if (atTarget(pos, tgt, 50)) return true;
    await new Promise((r) => setTimeout(r, 300));
  }
  throw new Error("Timed out waiting for stage to reach target");
}

async function refreshPosition() {
  const data = await getPosition();
  const pos = normalizePos(data);
  setBoth(pos);
}

onMounted(async () => {
  const cached = localStorage.getItem("lastStagePos");
  if (cached) {
    try {
      const p = JSON.parse(cached);
      target.x = p.x; target.y = p.y; target.z = p.z;
      current.x = p.x; current.y = p.y; current.z = p.z;
    } catch {}
  }

  try {
    await refreshPosition();
    moveStatus.value = "Synced with microscope ✅";
  } catch (e) {
    moveStatus.value = "Could not reach microscope (showing last known position)";
  }
});

function nudge(axis, direction) {
  const delta = direction * step.value;
  target[axis] = (Number(target[axis]) || 0) + delta;
  moveStatus.value = "Target changed (not moved yet)";
}

async function moveNow() {
  moveStatus.value = "Moving...";
  const tgt = { x: target.x, y: target.y, z: target.z };

  try {
    await moveAbs(tgt.x, tgt.y, tgt.z);
    await waitUntilAtTarget(tgt, 45000);
    moveStatus.value = "Move complete ✅";
  } catch (e) {
    moveStatus.value = "Move in progress… (syncing current position)";
    await refreshPositionSafe();
  }
}


async function centerNow() {
  moveStatus.value = "Centering...";

  target.x = 0; target.y = 0; target.z = 0;
  try {
    await centerStage();
  } catch (e) {
    console.warn("centerStage request failed (may still be moving):", e);
  }

  try {
    await waitUntilAtTarget({ x: 0, y: 0, z: 0 }, 45000);
    moveStatus.value = "Centered ✅";
  } catch (e) {
    moveStatus.value = "Center in progress… (syncing current position)";
    await refreshPositionSafe();
  }
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
