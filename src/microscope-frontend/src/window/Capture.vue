<template>
  <div class="capturePage">
    <!-- Left sidebar with image (top) and video (bottom) controls -->
    <section class="controls">
      <!-- Image Section -->
      <div class="section">
        <div class="header">IMAGE</div>
        <div class="section-scroll">
          <div class="block">
            <div class="label">Resolution</div>
            <div class="segmented">
            	<button class="segBtn" :class="{ active: imageResolution === 'FULL' }" @click="imageResolution = 'FULL'">
              FULL
              </button>
              <button class="segBtn" :class="{ active: imageResolution === 'RAW' }" @click="imageResolution = 'RAW'">
              LOW
              </button>
            </div>
          </div>

          <button class="captureBtn" @click="handleCaptureImage" :disabled="imageBusy">
              <span v-if="imageBusy && imageBusyMode === 'capture'" class="spinner"></span>
              {{ imageBusy && imageBusyMode === 'capture' ? 'CAPTURING...' : 'CAPTURE' }}
          </button>
          <div v-if="imageStatus" class="statusTextSmall">{{ imageStatus }}</div>
        </div>
      </div>

      <div class="sectionDivider"></div>

      <!-- Video Section -->
      <div class="section">
        <div class="header">VIDEO</div>

        <div class="section-scroll">
          <div class="block">
            <div class="label">Resolution</div>
            <div class="segmented">
              <button class="segBtn" :class="{ active: videoResolution === 'FULL' }" @click="videoResolution = 'FULL'">
              FULL</button>
              <button  class="segBtn" :class="{ active: videoResolution === 'RAW' }" @click="videoResolution = 'RAW'">
              LOW</button>
            </div>
          </div>

          <div class="block">
            <div class="label">Frames-per-Minute (FPM)</div>

            <div class="row2">
              <button
                class="pill"
                :class="{ active: !motionClipOn && frameRate === 60 }"
                @click="setPreset(60)"
                :disabled="recording"
                type="button"
              >
                60
              </button>

              <button
                class="pill"
                :class="{ active: !motionClipOn && frameRate === 30 }"
                @click="setPreset(30)"
                :disabled="recording"
                type="button"
              >
                30
              </button>
            </div>

            <!-- Motion clip preset -->
            <div class="row1" style="margin-top: 10px;">
              <button
                class="pill pillWide"
                :class="{ active: motionClipOn }"
                @click="toggleMotionClip"
                :disabled="recording"
                type="button"
                title="Records 5 seconds at 25 fps and stops automatically"
              >
                Motion Clip • 25 FPS • 5s
              </button>
            </div>

            <div v-if="motionClipOn" class="statusTextSmall">
              Auto-stops after 5 seconds (125 frames)
            </div>
          </div>
					<button v-if="!recording" class="primaryBtn" @click="startRecording" :disabled="videoBusy">
            <span v-if="videoBusy && videoBusyMode === 'start'" class="spinner"></span>
            {{ videoBusy && videoBusyMode === 'start' ? 'STARTING...' : 'START VIDEO' }}
          </button>

          <!-- If motion clip is on, don't show manual stop -->
          <button
            v-else-if="recording && !motionClipOn"
            class="primaryBtn stopBtn"
            @click="stopRecording"
            :disabled="videoBusy"
          >
            <span v-if="videoBusy && videoBusyMode === 'stop'" class="spinner"></span>
            {{ videoBusy && videoBusyMode === 'stop' ? 'STOPPING...' : 'STOP VIDEO' }}
          </button>

          <div v-else class="statusTextSmall">
            Recording motion clip… auto-stopping
          </div>
					<div v-if="videoStatus" class="statusTextSmall">{{ videoStatus }}</div>
				</div>
			</div>
    </section>

    <!-- Center live preview -->
    <section class="preview">
      <CameraPreview />
    </section>

    <!-- Image Capture Modal -->
    <div v-if="imageModalOpen" class="backdrop" @click.self="closeImageModal">
      <div class="imageModal">
        <div class="imageModalHeader">
          <div class="imageModalTitle">Image</div>
          <button class="closeX" @click="closeImageModal">×</button>
        </div>

        <div class="imageModalBody">
          <div class="modalLeft">
            <!-- Filename -->
            <div class="modalField">
              <div class="modalLabel">Filename</div>
              <input class="textInput" v-model="imageModalFilename" placeholder="filename" />
            </div>

            <!-- Notes -->
            <div class="modalField">
              <div class="modalLabel">Notes</div>
              <textarea class="textArea" v-model="imageModalNotes" placeholder="Notes"></textarea>
            </div>

            <!-- Annotations -->
            <div class="modalField">
              <div class="modalLabel">Annotations</div>
              <div class="annoRow">
                <input class="miniInput" v-model="imageAnnoKey" placeholder="key" />
                <input class="miniInput" v-model="imageAnnoValue" placeholder="value" />
                <button class="plusBtn" @click="addImageAnnotation" title="Add annotation">
                  <span class="material-symbols-outlined">add_circle</span>
                </button>
              </div>
              <div v-if="imageModalAnnotations.length" class="chips">
                <div class="chip" v-for="(a, i) in imageModalAnnotations" :key="i">
                  {{ a.key }}: {{ a.value }}
                  <button class="chipX" @click="imageModalAnnotations.splice(i, 1)" title="Remove">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Tags -->
            <div class="modalField">
              <div class="modalLabel">Tags</div>
              <div class="tagRow">
                <input class="miniInput" v-model="imageTagInput" placeholder="tag" />
                <button class="plusBtn" @click="addImageTag" title="Add tag">
                  <span class="material-symbols-outlined">add_circle</span>
                </button>
              </div>
              <div v-if="imageModalTags.length" class="chips">
                <div class="chip" v-for="(t, i) in imageModalTags" :key="i">
                  {{ t }}
                  <button class="chipX" @click="imageModalTags.splice(i, 1)" title="Remove">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Save to Gallery -->
            <div class="modalFooterLeft">
              <button class="saveBtn" @click="saveImageToGallery" :disabled="imageBusy || !capturedImageId">
                <span v-if="imageBusy && imageBusyMode === 'save'" class="spinner"></span>
                {{ imageBusy && imageBusyMode === 'save' ? 'SAVING...' : 'SAVE TO GALLERY' }}
              </button>
            </div>
          </div>

          <div class="modalRight">
            <div class="modalPreviewFrame">
              <div v-if="imageBusy && imageBusyMode === 'capture'" class="modalLoading">
                <div class="spinner big"></div>
                <div class="loadingText">
                  Capturing {{ imageResolution === 'RAW' ? 'RAW' : 'FULL' }} image…
                </div>
              </div>
              <img v-else class="modalPreviewImg" :src="imagePreviewUrl || '/cell.jpg'" alt="Captured preview"/>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Video Stop Modal -->
    <div v-if="stopModalOpen" class="backdrop" @click.self="closeStopModal">
      <div class="videoModal">
        <div class="videoModalHeader">
          <div class="videoModalTitle">Video</div>
          <button class="closeX" @click="closeStopModal">×</button>
        </div>

        <div class="videoModalBody">
          <div class="modalLeft">
            <!-- Filename -->
            <div class="modalField">
              <div class="modalLabel">Filename</div>
              <input class="textInput" v-model="videoModalFilename" placeholder="filename" />
            </div>

            <!-- Notes -->
            <div class="modalField">
              <div class="modalLabel">Notes</div>
              <textarea class="textArea" v-model="videoModalNotes" placeholder="Notes"></textarea>
            </div>

            <!-- Annotations -->
            <div class="modalField">
              <div class="modalLabel">Annotations</div>
              <div class="annoRow">
                <input class="miniInput" v-model="videoAnnoKey" placeholder="key" />
                <input class="miniInput" v-model="videoAnnoValue" placeholder="value" />
                <button class="plusBtn" @click="addVideoAnnotation" title="Add annotation">
                  <span class="material-symbols-outlined">add_circle</span>
                </button>
              </div>
              <div v-if="videoModalAnnotations.length" class="chips">
                <div class="chip" v-for="(a, i) in videoModalAnnotations" :key="i">
                  {{ a.key }}: {{ a.value }}
                  <button class="chipX" @click="videoModalAnnotations.splice(i, 1)" title="Remove">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Tags -->
            <div class="modalField">
              <div class="modalLabel">Tags</div>
              <div class="tagRow">
                <input class="miniInput" v-model="videoTagInput" placeholder="tag" />
                <button class="plusBtn" @click="addVideoTag" title="Add tag">
                  <span class="material-symbols-outlined">add_circle</span>
                </button>
              </div>
              <div v-if="videoModalTags.length" class="chips">
                <div class="chip" v-for="(t, i) in videoModalTags" :key="i">
                  {{ t }}
                  <button class="chipX" @click="videoModalTags.splice(i, 1)" title="Remove">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Save -->
            <div class="modalFooterLeft">
              <button
                class="saveBtn"
                @click="saveVideoToGallery"
                :disabled="videoBusy || !recordedVideoId"
              >
                <span v-if="videoBusy && videoBusyMode === 'save'" class="spinner"></span>
                {{ videoBusy && videoBusyMode === 'save' ? 'SAVING...' : 'SAVE TO GALLERY' }}
              </button>
            </div>
          </div>

          <div class="modalRight">
            <div class="modalPreviewFrame">
              <video
                v-if="stopPreviewUrl"
                :src="stopPreviewUrl"
                controls
                class="modalPreviewVideo"
              ></video>

              <CameraPreview v-else />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import CameraPreview from "../components/CameraPreview.vue";
import { captureImage, deleteCapture } from "../api/imageApi";
import {
  startVideo,
  stopVideo,
  analyzeVideo,
  saveVideoToGallery as saveVideo,
  deleteTempVideo
} from "../api/videoApi";
const router = useRouter();

// ----- Image state -----
const imageResolution = ref("FULL");
const imageBusy = ref(false);
const imageBusyMode = ref(""); // "capture", "save"
const imageStatus = ref("");

const imageModalOpen = ref(false);
const imageModalFilename = ref("");
const imageModalNotes = ref("");
const imageModalAnnotations = ref([]);
const imageModalTags = ref([]);
const imageAnnoKey = ref("");
const imageAnnoValue = ref("");
const imageTagInput = ref("");
const imagePreviewUrl = ref("");
const lastCaptureIsRaw = ref(false);
const capturedImageId = ref(null);

// ----- Video state -----
const videoResolution = ref("FULL");
const frameRate = ref(60);
const recording = ref(false);
const videoBusy = ref(false);
const videoBusyMode = ref(""); // "start", "stop", "count", "save"
const videoStatus = ref("");
const recordingId = ref(null);
const recordedVideoId = ref(null);

const stopModalOpen = ref(false);
const stopPreviewUrl = ref("");
const videoModalFilename = ref("filename");
const videoModalNotes = ref("");
const videoModalAnnotations = ref([]);
const videoModalTags = ref([]);
const videoAnnoKey = ref("");
const videoAnnoValue = ref("");
const videoTagInput = ref("");
const cellCount = ref(null);
const videoSaved = ref(false);

const motionClipOn = ref(false);
const motionStopTimer = ref(null);

// constants for the motion clip preset
const MOTION_FPS = 25;
const MOTION_SECONDS = 5;
const MOTION_FPM = MOTION_FPS * 60;          // 1500
const MOTION_FRAMES = MOTION_FPS * MOTION_SECONDS; // 125

// ----- Helper functions (video) -----
function setPreset(n) {
  motionClipOn.value = false;
  frameRate.value = n;
}

function toggleMotionClip() {
  motionClipOn.value = !motionClipOn.value;
  if (motionClipOn.value) {
  }
}

onUnmounted(() => {
  if (motionStopTimer.value) clearTimeout(motionStopTimer.value);
  motionStopTimer.value = null;
});

// ----- Image functions -----
async function handleCaptureImage() {
  imageModalOpen.value = true;
  imagePreviewUrl.value = "";
  capturedImageId.value = null;

  try {
    imageBusy.value = true;
    imageBusyMode.value = "capture";
    imageStatus.value = "Capturing image...";

    const isRaw = imageResolution.value === "RAW";

    const annotationsDict = {};
    for (const a of imageModalAnnotations.value) {
      if (a?.key) annotationsDict[a.key] = a.value ?? "";
    }
    if (imageModalNotes.value?.trim()) annotationsDict["Notes"] = imageModalNotes.value.trim();

    const payload = {
      filename: imageModalFilename.value?.trim() || "capture",
      temporary: true,
      use_video_port: isRaw,
      bayer: isRaw,
      annotations: annotationsDict,
      tags: imageModalTags.value,
    };

    const result = await captureImage(payload);
    const cap = result.capture;
    capturedImageId.value = cap?.id ?? cap?.saved_as ?? cap?.filename ?? "";
    const base = import.meta.env.VITE_API_BASE || "";
    imagePreviewUrl.value = `${base}/captures/${encodeURIComponent(capturedImageId.value)}/image`;
    lastCaptureIsRaw.value = isRaw;
    imageStatus.value = `Captured: ${capturedImageId.value}`;
  } catch (err) {
    console.error(err);
    imageStatus.value = `Error: ${err.message}`;
  } finally {
    imageBusy.value = false;
    imageBusyMode.value = "";
  }
}

function closeImageModal() {
  const id = capturedImageId.value;
  imageModalOpen.value = false;
  capturedImageId.value = null;
  imagePreviewUrl.value = "";
  if (id) {
    imageBusyMode.value = "delete";
    deleteCapture(id).catch((e) => console.warn("Failed to delete temp capture:", e))
      .finally(() => {
        if (imageBusyMode.value === "delete") imageBusyMode.value = "";
      });
  }
}

function addImageAnnotation() {
  if (!imageAnnoKey.value || !imageAnnoValue.value) return;
  imageModalAnnotations.value.push({ key: imageAnnoKey.value, value: imageAnnoValue.value });
  imageAnnoKey.value = "";
  imageAnnoValue.value = "";
}

function addImageTag() {
  const t = imageTagInput.value.trim();
  if (!t) return;
  imageModalTags.value.push(t);
  imageTagInput.value = "";
}

async function saveImageToGallery() {
  try {
    imageBusy.value = true;
    imageBusyMode.value = "save";
    imageStatus.value = "Saving to gallery...";

    const annotationsDict = {};
    for (const a of imageModalAnnotations.value) {
      if (a?.key?.trim()) annotationsDict[a.key.trim()] = String(a.value ?? "");
    }
    if (imageModalNotes.value?.trim()) annotationsDict["Notes"] = imageModalNotes.value.trim();

    const payload = {
      filename: imageModalFilename.value?.trim() || "capture",
      temporary: false,
      use_video_port: lastCaptureIsRaw.value,
      bayer: lastCaptureIsRaw.value,
      annotations: annotationsDict,
      tags: imageModalTags.value.map(t => t.trim()).filter(Boolean),
    };

    await captureImage(payload); // save permanently
    const tempId = capturedImageId.value;
    imageModalOpen.value = false;
    router.push("/gallery");

    capturedImageId.value = null;
    imagePreviewUrl.value = "";

    if (tempId) {
      deleteCapture(tempId).catch((e) => console.warn("Failed to delete temp capture:", e));
    }
  } catch (e) {
    console.error(e);
    imageStatus.value = `Save failed: ${e.message}`;
  } finally {
    imageBusy.value = false;
    imageBusyMode.value = "";
  }
}

// ----- Video functions -----
async function startRecording() {
  try {
    videoBusy.value = true;
    videoBusyMode.value = "start";
    videoStatus.value = "Starting recording...";
    const isMotion = motionClipOn.value;
    const payload = {
      fpm: isMotion ? MOTION_FPM : frameRate.value,
      max_frames: isMotion ? MOTION_FRAMES : 300,
      max_h: videoResolution.value === "RAW" ? 624 : 1080,
    };
    const result = await startVideo(payload);
    recordingId.value =
      result?.recording_id ??
      result?.id ??
      result?.recording?.id ??
      null;
    if (!recordingId.value) {
      throw new Error("Start succeeded but no recording id returned from backend");
    }
    recording.value = true;
    videoStatus.value = isMotion ? "Recording motion clip..." : "Recording...";
    if (isMotion) {
      if (motionStopTimer.value) clearTimeout(motionStopTimer.value);
      motionStopTimer.value = setTimeout(() => {
        if (recording.value && recordingId.value) stopRecording(true);
      }, MOTION_SECONDS * 1000);
    }
  } catch (e) {
    console.error(e);
    videoStatus.value = `Start failed: ${e?.message ?? e}`;
  } finally {
    videoBusy.value = false;
    videoBusyMode.value = "";
  }
}

async function stopRecording(isAuto = false) {
  try {
    if (!recordingId.value) return;
    if (motionStopTimer.value) clearTimeout(motionStopTimer.value);
    motionStopTimer.value = null;
    videoBusy.value = true;
    videoBusyMode.value = "stop";
    videoStatus.value = isAuto ? "Auto-stopping motion clip..." : "Stopping recording...";
    const result = await stopVideo(recordingId.value);
    recordedVideoId.value =
      result?.id ??
      result?.video_id ??
      result?.video?.id ??
      result?.recording?.video_id ??
      null;
    if (!recordedVideoId.value) {
      throw new Error("Stop succeeded but no video id returned from backend");
    }
    recordingId.value = null;
    recording.value = false;
    const preview = result?.preview_url;
    if (preview) {
      stopPreviewUrl.value = preview;
    } else {
      const base = import.meta.env.VITE_API_BASE || "";
      stopPreviewUrl.value = `${base}/video/${encodeURIComponent(recordedVideoId.value)}/download?t=${Date.now()}`;
    }
    openStopModal();
    videoStatus.value = "Stopped.";
  } catch (e) {
    console.error(e);
    videoStatus.value = `Stop failed: ${e?.message ?? e}`;
  } finally {
    videoBusy.value = false;
    videoBusyMode.value = "";
  }
}

function openStopModal() {
  stopModalOpen.value = true;
  cellCount.value = null;
  videoSaved.value = false;
}

async function closeStopModal() {
  stopModalOpen.value = false;
  stopPreviewUrl.value = "";
  const vid = recordedVideoId.value;
  if (vid && !videoSaved.value) {
    try {
      await deleteTempVideo(vid);
    } catch (e) {
      console.warn("Failed to delete temp video:", e);
    }
  }

  recordedVideoId.value = null;
  videoSaved.value = false;
}

function addVideoAnnotation() {
  if (!videoAnnoKey.value || !videoAnnoValue.value) return;
  videoModalAnnotations.value.push({ key: videoAnnoKey.value, value: videoAnnoValue.value });
  videoAnnoKey.value = "";
  videoAnnoValue.value = "";
}

function addVideoTag() {
  const t = videoTagInput.value.trim();
  if (!t) return;
  videoModalTags.value.push(t);
  videoTagInput.value = "";
}

async function countCells() {
  try {
    videoBusy.value = true;
    videoBusyMode.value = "count";
    videoStatus.value = "Running analysis...";

    const result = await analyzeVideo(recordedVideoId.value, { type: "count_cells" });
    cellCount.value = result?.cell_count ?? result?.analysis?.cell_count ?? result?.count ?? 0;
    videoStatus.value = "Analysis complete.";
  } catch (e) {
    console.error(e);
    videoStatus.value = `Analysis failed: ${e?.message ?? e}`;
  } finally {
    videoBusy.value = false;
    videoBusyMode.value = "";
  }
}

async function saveVideoToGallery() {
  try {
    videoBusy.value = true;
    videoBusyMode.value = "save";
    videoStatus.value = "Saving to gallery...";

    const annotationsDict = {};
    for (const a of videoModalAnnotations.value) {
      if (a?.key?.trim()) annotationsDict[a.key.trim()] = String(a.value ?? "");
    }
    if (videoModalNotes.value?.trim()) annotationsDict["Notes"] = videoModalNotes.value.trim();

    const payload = {
      filename: videoModalFilename.value?.trim() || "video",
      notes: videoModalNotes.value,
      annotations: annotationsDict,
      tags: videoModalTags.value.map(t => t.trim()).filter(Boolean),
      resolution: videoResolution.value,
      frames_per_minute: frameRate.value,
    };
    if (cellCount.value !== null) payload.analysis = { cell_count: cellCount.value };

    await saveVideo(recordedVideoId.value, payload);
    videoSaved.value = true
    stopModalOpen.value = false;
    videoStatus.value = "Saved.";
  } catch (e) {
    console.error(e);
    videoStatus.value = `Save failed: ${e?.message ?? e}`;
  } finally {
    videoBusy.value = false;
    videoBusyMode.value = "";
  }
}
</script>

<style scoped>
.capturePage {
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
	height: 100%;
  overflow-y: hidden;
}

.section {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-height: 0;
  margin-bottom: 0;
}

.section-scroll {
  flex: 1;                    
  overflow-y: auto;           
  padding-right: 4px;       
}

.sectionDivider {
  height: 1px;
  background: #d0d0d0;
  margin: 10px 0;
}

.header {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.6px;
  opacity: 0.35;
  margin-bottom: 15px;
}

.block {
  margin-bottom: 10px;
}

.label {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 6px;
}

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
  margin-top: 6px;
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

.row1 {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.pillWide {
  width: 100%;
}

.miniInput {
  height: 30px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
  outline: none;
  width: 100%;
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
  margin-top: 8px;
}

.captureBtn:hover,
.setBtn:hover,
.primaryBtn:hover {
  filter: brightness(0.95);
}

.primaryBtn {
  height: 40px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  font-size: 12px;
  cursor: pointer;
  width: 100%;
}

.primaryBtn.stopBtn {
  background: #b00020;
}

.primaryBtn.stopBtn:hover {
  background: #8b0000;
}

.statusTextSmall {
  font-size: 12px;
  opacity: 0.75;
  margin-top: 4px;
}

/* Preview */
.preview {
  background: #d9d9d9;
  overflow: hidden;
}

/* ----- Modal styles (shared) ----- */
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.imageModal,
.videoModal {
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

.imageModalHeader,
.videoModalHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.imageModalTitle,
.videoModalTitle {
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

.imageModalBody,
.videoModalBody {
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
  width: 100%;
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
  width: 100%;
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
  overflow: hidden;
}

.modalPreviewImg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modalPreviewVideo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
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

/* Optional count button (if uncommented) */
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

.countResult {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #333;
}
</style>