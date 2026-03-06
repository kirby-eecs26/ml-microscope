<template>
  <div class="settingsPage">
    <!-- Settings sidebar (right of main sidebar) -->
    <aside class="settingsSidebar">
      <!-- Application Settings Section -->
      <div class="settingsSection">
        <div class="sectionTitle">Application Settings</div>
        <div class="settingsNav">
          <div class="navItem" :class="{ active: activeTab === 'display' }" @click="activeTab = 'display'">Display</div>
        </div>
      </div>

      <div class="divider"></div>

      <!-- Microscope Settings Section -->
      <div class="settingsSection">
        <div class="sectionTitle" id="MicroscopeSettingsTitle">Microscope Settings</div>
        <div class="settingsNav">
          <div class="navItem" :class="{ active: activeTab === 'camera' }" @click="activeTab = 'camera'">Camera</div>
        </div>
      </div>
    </aside>

    <!-- Main settings content area -->
    <main class="settingsContent">
      <!-- DISPLAY -->
      <div class="displaySettings" v-if="activeTab === 'display'">
        <h2 class="contentTitle">Display Settings</h2>

        <div class="settingGroup">
          <h3 class="settingTitle">Theme</h3>
          <div class="settingControl">
            <select id="themeSelect" v-model="selectedTheme" class="themeDropdown">
              <option value="system">System</option>
              <option value="dark">Dark Mode</option>
              <option value="light">Light Mode</option>
            </select>
          </div>
        </div>

        <div class="settingGroup">
          <h3 class="settingTitle">Stream settings</h3>
          <div class="settingDescription">
            These options affect the embedded web stream of the camera.
          </div>

          <div class="formRow">
            <label class="checkRow">
              <input type="checkbox" v-model="disableWebStream" />
              <span>Disable web stream</span>
            </label>
          </div>
        </div>
      </div>

      <!-- CAMERA -->
      <div class="cameraSettings" v-if="activeTab === 'camera'">
        <h2 class="contentTitle">Camera Settings</h2>

        <div class="camera-layout">

          <!-- LEFT COLUMN (ALL YOUR SETTINGS) -->
          <div class="camera-left">

            <div class="settingGroup">
              <h3 class="settingTitle">Pi Camera Settings</h3>

              <div class="grid2">
                <div class="formRow">
                  <label>Exposure time</label>
                  <input class="textInput" type="number" v-model.number="camExposure" />
                </div>

                <div class="formRow">
                  <label>Analogue gain</label>
                  <input class="textInput" type="number" step="0.01" v-model.number="camAnalogueGain" />
                </div>

                <div class="formRow">
                  <label>Digital gain</label>
                  <input class="textInput" type="number" step="0.01" v-model.number="camDigitalGain" />
                </div>
              </div>

              <div class="subTitle">White Balance gains</div>

              <div class="grid2">
                <div class="formRow">
                  <label>R</label>
                  <input class="textInput" type="number" step="0.01" v-model.number="wbR" />
                </div>

                <div class="formRow">
                  <label>B</label>
                  <input class="textInput" type="number" step="0.01" v-model.number="wbB" />
                </div>
              </div>
            </div>

            <div class="settingGroup">
              <h3 class="settingTitle">Image Quality</h3>

              <div class="grid2">
                <div class="formRow">
                  <label>JPEG capture quality (%)</label>
                  <input class="textInput" type="number" min="1" max="100" v-model.number="jpegQuality" />
                </div>

                <div class="formRow">
                  <label>Stream resolution</label>
                  <select class="themeDropdown wide" v-model="streamResolution">
                    <option value="higher">Higher (832, 624)</option>
                    <option value="normal">Normal (640, 480)</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="settingGroup">
              <h3 class="settingTitle">Advanced</h3>

              <div class="grid2">
                <div class="formRow">
                  <label>Camera bitrate</label>
                  <select class="themeDropdown wide" v-model="cameraBitrate">
                    <option value="max">Maximum (unlimited)</option>
                    <option value="high">High (25 Mbps)</option>
                    <option value="normal">Normal (17 Mbps)</option>
                    <option value="low">Low (5 Mbps)</option>
                    <option value="verylow">Very low (2.5 Mbps)</option>
                  </select>
                </div>

                <div class="formRow">
                  <label>Camera framerate</label>
                  <select class="themeDropdown wide" v-model="cameraFramerate">
                    <option :value="30">Normal (30fps)</option>
                    <option :value="15">Low (15fps)</option>
                    <option :value="10">Very low (10fps)</option>
                  </select>
                </div>
              </div>

              <div class="formRow">
                <button class="primaryAction" @click="applyCameraSettings">
                  APPLY SETTINGS
                </button>
              </div>
            </div>

            <div class="settingGroup">
              <h3 class="settingTitle">Automatic calibration</h3>

              <div class="btnStack">
                <button class="secondaryAction" @click="runCalibration('FULL_AUTO_CALIBRATE')">
                  FULL AUTO-CALIBRATE
                </button>

                <button class="secondaryAction" @click="runCalibration('AUTO_GAIN_SHUTTER')">
                  AUTO GAIN & SHUTTER SPEED
                </button>

                <button class="secondaryAction" @click="runCalibration('AUTO_WHITE_BALANCE')">
                  AUTO WHITE BALANCE
                </button>

                <button class="secondaryAction" @click="runCalibration('AUTO_FLAT_FIELD')">
                  AUTO FLAT FIELD CORRECTION
                </button>

                <button class="secondaryAction danger" @click="runCalibration('DISABLE_FLAT_FIELD')">
                  DISABLE FLAT FIELD CORRECTION
                </button>
              </div>
            </div>

          </div>

          <!-- RIGHT COLUMN (LIVE CAMERA STREAM) -->
          <div class="camera-right">

            <h3 class="previewTitle">Live Preview</h3>

            <div class="previewBox">

              <!-- If stream disabled -->
              <div v-if="disableWebStream" class="notConnected">
                Web stream disabled
              </div>

              <!-- Otherwise show stream -->
              <template v-else>
                <img
                  v-if="mjpegUrl"
                  class="mjpegPreview"
                  :src="mjpegUrl"
                  alt="Live camera preview"
                  @error="onPreviewError"
                  @load="onPreviewLoad"
                />

              <div v-if="previewError" class="previewError">
                Preview unavailable. Check microscope connection.
              </div>
            </template>
          </div>

            <div class="previewHint">
              Live MJPEG stream from the microscope camera.
            </div>

          </div>

        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { applyTheme, getSavedTheme } from "../utils/theme";
import CameraPreview from "../components/CameraPreview.vue"
import { getLiveInfo, microscopeHealth } from "../api/imageApi";

const activeTab = ref('display')

/* Display */
const selectedTheme = ref('system')

onMounted(() => {
  selectedTheme.value = getSavedTheme();
});

watch(selectedTheme, (val) => {
  applyTheme(val);
});

const disableWebStream = ref(false)
const STREAM_KEY = "disable_web_stream";
const enableGpuPreview = ref(false)
const trackWindow = ref(true)

/* Disable Webstream */
onMounted(() => {
  const saved = localStorage.getItem(STREAM_KEY);
  if (saved === "1") disableWebStream.value = true;
});

watch(disableWebStream, (val) => {
  localStorage.setItem(STREAM_KEY, val ? "1" : "0");

  if (val) {
    mjpegUrl.value = "";
  } else if (activeTab.value === "camera") {
    loadPreviewUrl();
  }
});

/* Camera */
const camExposure = ref(33243)
const camAnalogueGain = ref(2.10)
const camDigitalGain = ref(1.0)
const wbR = ref(1.41)
const wbB = ref(1.49)
const jpegQuality = ref(100)
const streamResolution = ref('higher')
const cameraBitrate = ref('max')
const cameraFramerate = ref(30)
const mjpegUrl = ref("");
const previewError = ref(false)
const previewNonce = ref(Date.now())
function onImgError() {
  previewError.value = true;
  mjpegUrl.value = "";
}
async function loadPreviewUrl() {
  previewError.value = false;
  const ok = await microscopeHealth().catch(() => false);
  if (!ok) {
    previewError.value = true;
    mjpegUrl.value = "";
    return;
  }
  const info = await getLiveInfo();
  mjpegUrl.value = info.mjpeg_url;
}


watch(activeTab, (t) => {
  if (t === "camera" && !disableWebStream.value && !mjpegUrl.value) {
    loadPreviewUrl();
  }
});

onMounted(() => {
  if (activeTab.value === "camera" && !disableWebStream.value) {
    loadPreviewUrl();
  }
});

function onPreviewError() {
  previewError.value = true
}
function onPreviewLoad() {
  previewError.value = false
}

/* Stage */
const stageStepSize = ref(10)
const stageMaxSpeed = ref(100)

/* Mapping  
const pixelsPerUm = ref(0.25)
const rotationDeg = ref(0)
*/

/* General */
const captureDirectory = ref('/capture/images')
const filenamePrefix = ref('image')

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

async function requestJson(method, path, body = null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : null,
  });

  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`${path} failed: ${res.status} ${txt}`);
  }
  return res.json().catch(() => ({}));
}


function saveDisplaySettings() {
  console.log('APPLY DISPLAY', {
    theme: selectedTheme.value,
    disableWebStream: disableWebStream.value,
    enableGpuPreview: enableGpuPreview.value,
    trackWindow: trackWindow.value,
  })
}

async function applyCameraSettings() {
  try {
    const payload = {
      exposure: Number(camExposure.value ?? 0),
      analogueGain: Number(camAnalogueGain.value ?? 1.0),
      digitalGain: Number(camDigitalGain.value ?? 1.0),
      wbR: Number(wbR.value ?? 1.0),
      wbB: Number(wbB.value ?? 1.0),
      jpegQuality: Number(jpegQuality.value ?? 100),
      streamResolution: streamResolution.value,
      cameraBitrate: cameraBitrate.value,
      cameraFramerate: Number(cameraFramerate.value ?? 30),
    };
    const out = await requestJson("POST", "/settings/camera/apply", payload);
    console.log("APPLY SETTINGS OK", out);
  } catch (e) {
    console.error("APPLY SETTINGS ERROR", e);
  }
}

async function runCalibration(kind) {
  const routes = {
    FULL_AUTO_CALIBRATE: "/settings/calibration/full_autocalibrate",
    AUTO_GAIN_SHUTTER: "/settings/calibration/auto_gain_shutter",
    AUTO_WHITE_BALANCE: "/settings/calibration/auto_white_balance",
    AUTO_FLAT_FIELD: "/settings/calibration/auto_flat_field",
    DISABLE_FLAT_FIELD: "/settings/calibration/disable_flat_field",
  };
  const url = routes[kind];
  console.log("runCalibration kind:", kind);
  console.log("runCalibration url:", url);

  if (!url) {
    console.error("Unknown calibration kind:", kind);
    return;
  }
  try {
    const out = await requestJson("POST", url);
    console.log("CALIBRATION OK", kind, out);
  } catch (e) {
    console.error("CALIBRATION ERROR", kind, e);
  }
}

function saveStageSettings() {
  console.log('APPLY STAGE', {
    stepSize: stageStepSize.value,
    maxSpeed: stageMaxSpeed.value,
  })
}

function saveMappingSettings() {
  console.log('APPLY MAPPING', {
    pixelsPerUm: pixelsPerUm.value,
    rotationDeg: rotationDeg.value,
  })
}
</script>

<style scoped>
.settingsPage {
  display: grid;
  grid-template-columns: 220px 1fr;
  height: calc(100vh - 36px);
  background: var(--content-bg);
}

/* Settings Sidebar */
.settingsSidebar {
  background: var(--sidebar-bg);
  padding: 20px 0;
  border-right: 1px solid #d0d0d0;
}

.settingsSection {
  padding: 0 16px;
}

.sectionTitle {
  font-size: 0.8rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

#MicroscopeSettingsTitle {
  margin-top: 12px;
}

.settingsNav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.navItem {
  padding: 7px 12px;
  font-size: 0.85rem;
  color: #555;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.navItem:hover {
  background: var(--sidebar-hover);
  color: #333;
}

.navItem.active {
  background: var(--sidebar-active);
  color: #fff;
  font-weight: 600;
}

.divider {
  height: 1px;
  background: #d0d0d0;
  margin: 10px;
  margin-top: 5px;
}

.camera-layout {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 24px;
  align-items: start;
}

.camera-left {
  min-width: 0;
}

.camera-right {
  position: sticky;
  top: 16px;
}

.previewTitle {
  margin: 0 0 10px 0;
  font-size: 1rem;
  font-weight: 700;
  color: #333;
}

.previewBox {
  position: relative;
  width: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #000;
  overflow: hidden;
}

.mjpegPreview {
  display: block;
  width: 100%;
  height: auto;
}

.previewError {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: white;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.55);
  padding: 12px;
  text-align: center;
}

.previewHint {
  margin-top: 10px;
  font-size: 0.85rem;
  color: #666;
}

@media (max-width: 1100px) {
  .camera-layout {
    grid-template-columns: 1fr;
  }
  .camera-right {
    position: static;
  }
}

/* Settings Content */
.settingsContent {
  padding: 24px;
  overflow-y: auto;
}

.contentTitle {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f4b7a;
  margin-top: 0;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eaeaea;
}

.settingGroup {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.settingGroup:last-child {
  border-bottom: none;
}

.settingTitle {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.settingDescription {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 16px;
  line-height: 1.4;
}

.settingControl {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 300px;
}

.settingControl label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.themeDropdown {
  padding: 8px 12px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  background: #fff;
  font-size: 0.85rem;
  color: #333;
  cursor: pointer;
  max-width: 200px;
}

.themeDropdown.wide {
  max-width: 320px;
}

.themeDropdown:focus {
  outline: none;
  border-color: #1f4b7a;
}

/* NEW: compact form helpers (keeps your existing CSS theme) */
.formRow {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  max-width: 520px;
}

.formRow label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.textInput {
  padding: 8px 12px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  background: #fff;
  font-size: 0.85rem;
  color: #333;
  max-width: 320px;
}

.textInput:focus {
  outline: none;
  border-color: #1f4b7a;
}

.checkRow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #333;
  user-select: none;
}

.grid2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 14px 24px;
  align-items: start;
  max-width: 760px;
}

.subTitle {
  margin-top: 6px;
  margin-bottom: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #333;
}

.primaryAction {
  height: 36px;
  padding: 0 16px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 800;
  font-size: 0.85rem;
  cursor: pointer;
  width: fit-content;
}

.primaryAction:hover {
  filter: brightness(0.95);
}

.btnStack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 340px;
}

.secondaryAction {
  height: 36px;
  padding: 0 14px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  background: #fff;
  color: #333;
  font-weight: 800;
  font-size: 0.85rem;
  cursor: pointer;
  text-align: left;
}

.secondaryAction:hover {
  background: #f5f5f5;
}

.secondaryAction.danger {
  border-color: #e0b4b4;
  color: #8a1f1f;
}

.mapping-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.left-col {
  max-width: 400px;  
}

.livePreviewBox {
  width: 100%;
  max-width: 520px;        /* adjust if you want bigger */
  aspect-ratio: 4 / 3;     /* keeps it “camera-like” */
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  overflow: hidden;
  display: grid;
  place-items: center;
}

.livePreview {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.notConnected {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  color: var(--text-dark);
  opacity: 0.85;
  font-weight: 600;
}
</style>
