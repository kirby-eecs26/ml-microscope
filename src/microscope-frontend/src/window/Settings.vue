<template>
  <div class="settingsPage">
    <!-- Settings sidebar (right of main sidebar) -->
    <aside class="settingsSidebar">
      <!-- Application Settings Section -->
      <div class="settingsSection">
        <div class="sectionTitle">Application Settings</div>
        <div class="settingsNav">
          <div class="navItem" :class="{ active: activeTab === 'display' }" @click="activeTab = 'display'">Display</div>
          <div class="navItem" :class="{ active: activeTab === 'features' }" @click="activeTab = 'features'">Features</div>
        </div>
      </div>

      <div class="divider"></div>

      <!-- Microscope Settings Section -->
      <div class="settingsSection">
        <div class="sectionTitle" id="MicroscopeSettingsTitle">Microscope Settings</div>
        <div class="settingsNav">
          <div class="navItem" :class="{ active: activeTab === 'camera' }" @click="activeTab = 'camera'">Camera</div>
          <div class="navItem" :class="{ active: activeTab === 'stage' }" @click="activeTab = 'stage'">Stage</div>
          <div class="navItem" :class="{ active: activeTab === 'mapping' }" @click="activeTab = 'mapping'">Camera / Stage Mapping</div>
          <div class="navItem" :class="{ active: activeTab === 'general' }" @click="activeTab = 'general'">General</div>
        </div>
      </div>
    </aside>

    <!-- Main settings content area -->
    <main class="settingsContent">
      <!-- DISPLAY -->
      <div class="displaySettings" v-if="activeTab === 'display'">
        <h2 class="contentTitle">Appearance</h2>

        <div class="settingGroup">
          <h3 class="settingTitle">Theme</h3>
          <div class="settingControl">
            <select id="themeSelect" v-model="selectedTheme" class="themeDropdown">
              <option value="system">System</option>
              <option value="dark">Dark Mode</option>
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

        <div class="settingGroup">
          <h3 class="settingTitle">Microscope display output</h3>
          <div class="settingDescription">
            Toggle GPU preview and whether the preview tracks the window.
          </div>

          <div class="formRow">
            <label class="checkRow">
              <input type="checkbox" v-model="enableGpuPreview" />
              <span>Enable GPU preview</span>
            </label>
          </div>

          <div class="formRow">
            <label class="checkRow">
              <input type="checkbox" v-model="trackWindow" />
              <span>Track window</span>
            </label>
          </div>
        </div>

        <div class="settingGroup">
          <button class="primaryAction" @click="saveDisplaySettings">APPLY SETTINGS</button>
        </div>
      </div>

      <!-- FEATURES -->
      <div class="featuresSettings" v-if="activeTab === 'features'">
        <h2 class="contentTitle">Features</h2>

        <div class="settingGroup">
          <h3 class="settingTitle">Experimental</h3>
          <div class="settingDescription">
            Enable or disable optional UI features. (Demo wiring for frontend.)
          </div>

          <div class="formRow">
            <label class="checkRow">
              <input type="checkbox" v-model="featureAutoSave" />
              <span>Auto-save annotations</span>
            </label>
          </div>

          <div class="formRow">
            <label class="checkRow">
              <input type="checkbox" v-model="featureHotkeys" />
              <span>Enable keyboard shortcuts</span>
            </label>
          </div>

          <div class="formRow">
            <button class="primaryAction" @click="saveFeatureSettings">APPLY SETTINGS</button>
          </div>
        </div>
      </div>

      <!-- CAMERA -->
      <div class="cameraSettings" v-if="activeTab === 'camera'">
        <h2 class="contentTitle">Manual camera settings</h2>

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
                <option value="medium">Medium (640, 480)</option>
                <option value="lower">Lower (416, 312)</option>
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
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div class="formRow">
              <label>Camera framerate</label>
              <select class="themeDropdown wide" v-model="cameraFramerate">
                <option :value="30">Normal (30fps)</option>
                <option :value="15">Low (15fps)</option>
                <option :value="60">High (60fps)</option>
              </select>
            </div>
          </div>

          <div class="formRow">
            <button class="primaryAction" @click="applyCameraSettings">APPLY SETTINGS</button>
          </div>
        </div>

        <div class="settingGroup">
          <h3 class="settingTitle">Automatic calibration</h3>

          <div class="btnStack">
            <button class="secondaryAction" @click="runCalibration('FULL_AUTO_CALIBRATE')">FULL AUTO-CALIBRATE</button>
            <button class="secondaryAction" @click="runCalibration('AUTO_GAIN_SHUTTER')">AUTO GAIN &amp; SHUTTER SPEED</button>
            <button class="secondaryAction" @click="runCalibration('AUTO_WHITE_BALANCE')">AUTO WHITE BALANCE</button>
            <button class="secondaryAction" @click="runCalibration('AUTO_FLAT_FIELD')">AUTO FLAT FIELD CORRECTION</button>
            <button class="secondaryAction danger" @click="runCalibration('DISABLE_FLAT_FIELD')">DISABLE FLAT FIELD CORRECTION</button>
            <button class="secondaryAction" @click="downloadLensShadingTable">DOWNLOAD LENS-SHADING TABLE</button>
          </div>
        </div>
      </div>

      <!-- Stage Tab -->
      <div class="stageSettings" v-if="activeTab === 'stage'">
        <h2 class="contentTitle">Stage Settings</h2>
      </div>

      <!-- Camera/Stage Mapping Tab -->
      <div class="mappingSettings" v-if="activeTab === 'mapping'">
        <h2 class="contentTitle">Camera/Stage Mapping Settings</h2>
      </div>

      <!-- General Tab -->
      <div class="generalSettings" v-if="activeTab === 'general'">
        <h2 class="contentTitle">General Settings</h2>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('display')

/* Display */
const selectedTheme = ref('system')
const disableWebStream = ref(false)
const enableGpuPreview = ref(false)
const trackWindow = ref(true)

/* Features */
const featureAutoSave = ref(false)
const featureHotkeys = ref(false)

/* Camera */
const camExposure = ref(33243)
const camAnalogueGain = ref(2.10)
const camDigitalGain = ref(1.0)
const wbR = ref(1.41)
const wbB = ref(1.49)
const jpegQuality = ref(95)
const streamResolution = ref('higher')
const cameraBitrate = ref('max')
const cameraFramerate = ref(30)

/* Stage */
const stageStepSize = ref(10)
const stageMaxSpeed = ref(100)

/* Mapping */
const pixelsPerUm = ref(0.25)
const rotationDeg = ref(0)

/* General */
const captureDirectory = ref('/capture/images')
const filenamePrefix = ref('image')

function saveDisplaySettings() {
  console.log('APPLY DISPLAY', {
    theme: selectedTheme.value,
    disableWebStream: disableWebStream.value,
    enableGpuPreview: enableGpuPreview.value,
    trackWindow: trackWindow.value,
  })
}

function saveFeatureSettings() {
  console.log('APPLY FEATURES', {
    autoSave: featureAutoSave.value,
    hotkeys: featureHotkeys.value,
  })
}

function applyCameraSettings() {
  console.log('APPLY CAMERA', {
    exposure: camExposure.value,
    analogueGain: camAnalogueGain.value,
    digitalGain: camDigitalGain.value,
    wbR: wbR.value,
    wbB: wbB.value,
    jpegQuality: jpegQuality.value,
    streamResolution: streamResolution.value,
    cameraBitrate: cameraBitrate.value,
    cameraFramerate: cameraFramerate.value,
  })
}

function runCalibration(kind) {
  console.log('CALIBRATION', kind)
}

function downloadLensShadingTable() {
  console.log('DOWNLOAD LENS SHADING TABLE')
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

function saveGeneralSettings() {
  console.log('APPLY GENERAL', {
    captureDirectory: captureDirectory.value,
    filenamePrefix: filenamePrefix.value,
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
</style>
