<template>
  <div class="galleryPage">
    <!-- Top bar -->
    <header class="topbar">
      <div class="title">GALLERY</div>

      <div class="searchWrap">
        <input class="search" v-model="query" placeholder="Search" />
        <span class="material-symbols-outlined searchIcon">search</span>
      </div>

      <button class="downloadAll" @click="downloadAll">
        Download
      </button>
    </header>


    <!-- Content -->
    <div class="content">
      <!-- Empty state -->
      <div v-if="filtered.length === 0" class="emptyState">
        No images yet. Capture an image to see it here.
      </div>

      <!-- Cards grid -->
      <div v-else class="grid">
        <div
          v-for="img in filtered"
          :key="img.id"
          class="card"
          :class="{ selected: selectedId === img.id }"
        >
          <div class="thumb" @click="openPreview(img)">
            <img :src="img.thumbUrl || img.url || '/cell.jpg'" alt="thumbnail" />
          </div>

          <div class="meta" @click="openDetails(img)">
            <div class="filename">{{ img.name }}</div>
            <div class="datetime">{{ formatDate(img.datetime) }}</div>

            <div class="actions">
              <button class="iconBtn" @click.stop="openAnalysisModal(img)">
                <span class="material-symbols-outlined">bar_chart</span>
              </button>

              <button class="iconBtn" @click.stop="downloadOne(img)">
                <span class="material-symbols-outlined">download</span>
              </button>

              <button class="iconBtn" @click.stop="deleteOne(img)">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </div>

            <button class="analyzeBtn" @click.stop="runAnalysis(img)">
              ANALYZE
            </button>
          </div>
        </div>
      </div>


      <!-- Pagination -->
      <footer class="pager">
        <button class="pageBtn active">1</button>
      </footer>
    </div>

    <!-- Modal -->
    <div v-if="modalOpen" class="backdrop" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modalTitle">{{ modalItem?.name }}</div>

        <div class="rowLine"><b>Path:</b> {{ modalItem?.path }}</div>
        <div class="rowLine"><b>Datetime:</b> {{ formatDate(modalItem?.datetime) }}</div>
        <div class="rowLine"><b>ID:</b> {{ modalItem?.id }}</div>
        <div class="rowLine"><b>Format:</b> {{ modalItem?.format }}</div>

        <div class="divider"></div>

        <div class="section">
          <div class="label">Notes</div>
          <textarea class="textArea" v-model="modalNotes" placeholder="Notes"></textarea>
        </div>

        <div class="divider"></div>

        <div class="section">
          <div class="label">Annotations</div>
          <div class="annoRow">
            <input class="miniInput" v-model="annoKey" placeholder="key" />
            <input class="miniInput" v-model="annoValue" placeholder="value" />
            <button class="plusBtn" @click="addModalAnnotation">
              <span class="material-symbols-outlined">add_circle</span>
            </button>
          </div>

          <div class="chips" v-if="modalAnnotations.length">
            <div class="chip" v-for="(a, i) in modalAnnotations" :key="i">
              {{ a.key }}: {{ a.value }}
              <button class="chipX" @click="modalAnnotations.splice(i,1)">
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <div class="section">
          <div class="label">Tags</div>
          <div class="tagRow">
            <input class="miniInput" v-model="tagInput" placeholder="tag" />
            <button class="plusBtn" @click="addModalTag">
              <span class="material-symbols-outlined">add_circle</span>
            </button>
          </div>

          <div class="chips" v-if="modalTags.length">
            <div class="chip" v-for="(t, i) in modalTags" :key="i">
              {{ t }}
              <button class="chipX" @click="modalTags.splice(i,1)">
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>
        </div>

        <div class="modalFooter">
          <button class="okBtn" @click="saveModal">OK</button>
        </div>
      </div>
    </div>
  </div>

    <!-- Analysis Modal -->
    <div v-if="analysisOpen" class="analysisBackdrop" @click.self="closeAnalysisModal">
      <div class="analysisModal">
        <div class="analysisHeader">
          <div class="analysisTitle">Analysis</div>
          <button class="closeX" @click="closeAnalysisModal">×</button>
        </div>

        <div class="analysisDivider"></div>

        <div class="analysisBody">
          <div v-if="analysisItem?.analysis">
            <div class="analysisLine">Cell Count: {{ analysisItem.analysis.cellCount }}</div>
          </div>
          <div v-else class="analysisHint">
            No analysis found. Run <b>ANALYZE</b> first.
          </div>
        </div>

        <div class="analysisFooter">
          <button class="saveBtn" :disabled="!analysisItem?.analysis" @click="saveAnalysis">
            SAVE ANALYSIS
          </button>
        </div>
      </div>
    </div>
    <!-- Fullscreen Preview -->
    <div v-if="previewOpen" class="imgBackdrop" @click="closePreview">
      <div class="imgModal" @click.stop>
        <button class="imgClose" @click="closePreview">×</button>
        <img
          class="imgFull"
          :src="previewItem?.url || previewItem?.thumbUrl || '/cell.jpg'"
          alt="full"
        />
        <div class="imgCaption">
          <div><b>{{ previewItem?.name }}</b></div>
          <div class="muted">{{ formatDate(previewItem?.datetime) }}</div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="detailsOpen" class="backdrop" @click.self="closeDetails">
      <div class="modal" @click.stop>
        <div class="modalTitle">{{ detailsItem?.name }}</div>

        <div class="rowLine"><b>Time:</b> {{ formatDate(detailsItem?.datetime) }}</div>
        <div class="rowLine"><b>ID:</b> {{ detailsItem?.id }}</div>
        <div class="rowLine"><b>Format:</b> {{ detailsItem?.format || 'jpeg' }}</div>
        <div class="rowLine"><b>Resolution:</b> {{ displayResolution(detailsItem) }}</div>

        <div class="divider"></div>

        <div class="section">
          <div class="label">Tags</div>
          <div class="chips" v-if="(detailsItem?.tags || []).length">
            <div class="chip" v-for="(t, i) in detailsItem.tags" :key="i">
              {{ t }}
            </div>
          </div>
          <div v-else class="muted">No tags</div>
        </div>

        <div class="modalFooter">
          <button class="okBtn" @click="closeDetails">OK</button>
        </div>
      </div>
    </div>

</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { listCaptures, deleteCapture, analyzeCapture } from "../api/imageApi";

const gallery = ref([]); // will be loaded from backend
const query = ref("");

/** Fullscreen preview (lightbox) */
const previewOpen = ref(false);
const previewItem = ref(null);

/** Delete confirmation */
const confirmOpen = ref(false);
const confirmItem = ref(null);
const deleting = ref(false);
const deleteError = ref("");

/** Analysis modal */
const analysisOpen = ref(false);
const analysisItem = ref(null);
const analysisLoading = ref(false);
const analysisError = ref("");
const analysisResult = ref(null); // { blobCount, overlayImageUrl, maskImageUrl }

const filtered = computed(() => {
  const q = query.value?.trim().toLowerCase();
  if (!q) return gallery.value;
  return gallery.value.filter((img) => (img.name || "").toLowerCase().includes(q));
});

function formatDate(d) {
  return d ? String(d).replace("T", " ").slice(0, 19) : "";
}

/**
 * Normalize whatever your backend returns into:
 * { id, name, datetime, url, thumbUrl }
 */
function normalizeCaptures(payload) {
  const items = payload?.captures ?? payload ?? [];
  const base = import.meta.env.VITE_API_BASE || "";

  return items.map((c) => {
    const id = c.id;
    return {
      id,
      name: c.name ?? "capture",
      datetime: c.time ?? "",
      url: `${base}/captures/${encodeURIComponent(id)}/image`,
      thumbUrl: `${base}/captures/${encodeURIComponent(id)}/image`,
      tags: c.tags ?? [],
      raw: c,
    };
  });
}

async function refreshCaptures() {
  const data = await listCaptures();
  gallery.value = normalizeCaptures(data);
}

onMounted(async () => {
  try {
    await refreshCaptures();
  } catch (e) {
    console.error(e);
  }
});

/** Thumbnail click => fullscreen preview */
function openPreview(img) {
  previewItem.value = img;
  previewOpen.value = true;
}
function closePreview() {
  previewOpen.value = false;
  previewItem.value = null;
}

const detailsOpen = ref(false);
const detailsItem = ref(null);

function openDetails(img) {
  detailsItem.value = img;
  detailsOpen.value = true;
}

function closeDetails() {
  detailsOpen.value = false;
  detailsItem.value = null;
}

function displayResolution(img) {
  const ann = img?.raw?.annotations || {};
  if (ann.Size) return String(ann.Size);
  if (ann.Resolution === "RAW") return "832x624";
  if (ann.Resolution === "FULL") return "3280x2464";
  return "Unknown";
}

/** Delete */
function askDelete(img) {
  confirmItem.value = img;
  deleteError.value = "";
  confirmOpen.value = true;
}
function closeConfirm() {
  confirmOpen.value = false;
  confirmItem.value = null;
}

async function confirmDelete() {
  if (!confirmItem.value) return;
  deleting.value = true;
  deleteError.value = "";
  try {
    await deleteCapture(confirmItem.value.id);

    // remove locally
    gallery.value = gallery.value.filter((x) => x.id !== confirmItem.value.id);

    closeConfirm();
  } catch (e) {
    deleteError.value = String(e?.message || e);
  } finally {
    deleting.value = false;
  }
}

/** Analyze */
async function runAnalysis(img) {
  analysisItem.value = img;
  analysisOpen.value = true;
  analysisLoading.value = true;
  analysisError.value = "";
  analysisResult.value = null;

  try {
    const res = await analyzeCapture(img.id);
    analysisResult.value = {
      blobCount: res.blobCount ?? res.count ?? 0,
      overlayImageUrl: res.overlayImageUrl ?? null,
      maskImageUrl: res.maskImageUrl ?? null,
    };
  } catch (e) {
    analysisError.value = String(e?.message || e);
  } finally {
    analysisLoading.value = false;
  }
}

function closeAnalysisModal() {
  analysisOpen.value = false;
  analysisItem.value = null;
  analysisResult.value = null;
  analysisError.value = "";
  analysisLoading.value = false;
}
</script>


<style scoped>
.galleryPage {
  height: calc(100vh - 36px);
  display: flex;
  flex-direction: column;
  background: #d9d9d9;
}

/* Top bar */
.topbar {
  display: grid;
  grid-template-columns: 120px 1fr 140px;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #cfcfcf;
  background: #d9d9d9;
}

.title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.6px;
  opacity: 0.35; /* Figma title is very subtle */
}

/* Search (pill centered + icon on right) */
.searchWrap {
  position: relative;
  display: flex;
  justify-content: center;
}

.search {
  width: min(520px, 100%);
  height: 30px;
  border: 1px solid #bdbdbd;
  border-radius: 999px;
  padding: 0 36px 0 14px; /* room for icon on right */
  font-size: 12px;
  background: #fff;
  outline: none;
}

.searchIcon {
  position: absolute;
  right: calc(50% - min(260px, 50%) + 12px); /* places icon inside input */
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: #777;
  pointer-events: none;
}

/* Download button (dark blue rounded) */
.downloadAll {
  justify-self: end;
  height: 30px;
  padding: 0 18px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
}

.downloadAll:hover {
  filter: brightness(0.95);
}


.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 18px 22px;
}

.emptyState {
  flex: 1;
  font-size: 14px;
  opacity: 0.7;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, 210px);
  gap: 22px;
}

.card {
  background: #efefef;
  border: 1px solid #bdbdbd;
  cursor: pointer;
}

.card.selected {
  background: #2b5c96;
  color: white;
}

.thumb {
  height: 120px;
  background: #ccc;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pager {
  margin-top: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 18px 0 10px;
}

/* Page number style like Figma */
.pageBtn {
  width: 22px;
  height: 22px;
  border: 1px solid #bdbdbd;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

.pageBtn.active {
  background: #1f4b7a;
  color: #fff;
  border-color: #1f4b7a;
}


/* Card contents */
.meta {
  position: relative;
  padding: 10px 10px 12px;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto;
  column-gap: 8px;
  row-gap: 6px;
  border-top: 1px solid #bdbdbd;
  background: #1f4b7a;
}

.filename {
  grid-column: 1 / 2;
  grid-row: 1;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.datetime {
  grid-column: 1 / 2;
  grid-row: 2;
  font-size: 11px;
  opacity: 0.75;
}

.actions {
  grid-column: 2 / 3;
  grid-row: 1 / 3;
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: flex-end;
}

.iconBtn {
  width: 22px;
  height: 22px;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.iconBtn .material-symbols-outlined {
  font-size: 18px;
  color: #fff;
}

.card.selected .iconBtn .material-symbols-outlined {
  color: #fff;
}

.analyzeBtn {
  grid-column: 1 / 2;
  grid-row: 3;
  justify-self: start;
  height: 22px;
  padding: 0 10px;
  border: 1px solid #bdbdbd;
  background: #fff;
  color: #333;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
}

.card.selected .analyzeBtn {
  background: transparent;
  color: #fff;
  border-color: rgba(255,255,255,0.7);
}

/* Details modal */
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal {
  width: min(720px, 92vw);
  min-height: 360px;
  background: #f6f6f6;
  border-radius: 8px;
  border: 1px solid #cfcfcf;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  padding: 24px 28px;
  font-size: 14px;
  color: #111;
}

.modalTitle {
  font-weight: 800;
  font-size: 16px;
  margin-bottom: 8px;
}

.rowLine {
  font-size: 12px;
  padding: 5px 0;
  border-top: 1px solid #d8d8d8;
}

.rowLine:first-of-type {
  border-top: none;
}

.divider {
  height: 1px;
  background: #d8d8d8;
  margin: 14px 0;
}

.section .label {
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 6px;
}

.textArea {
  width: 100%;
  min-height: 70px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 14px;
  background: #fff;
  outline: none;
  resize: vertical;
}

.annoRow,
.tagRow {
  display: flex;
  gap: 10px;
  align-items: center;
}

.miniInput {
  height: 28px;
  border: 1px solid #bdbdbd;
  border-radius: 6px;
  padding: 0 10px;
  font-size: 12px;
  background: #fff;
  outline: none;
  min-width: 0;
}

.plusBtn {
  width: 32px;
  height: 32px;
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
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid #bdbdbd;
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

.modalFooter {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.okBtn {
  height: 30px;
  padding: 0 20px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
}

/* Analysis modal */
.analysisBackdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.analysisModal {
  width: min(1100px, 92vw);
  height: min(560px, 80vh);
  background: #f7f7f7;
  border: 1px solid #cfcfcf;
  border-radius: 6px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.35);
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
}

.analysisHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.analysisTitle {
  font-size: 14px;
  font-weight: 800;
  color: #111;
}

.closeX {
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #333;
}

.analysisDivider {
  height: 1px;
  background: #d4d4d4;
  margin: 12px 0;
}

.analysisBody {
  flex: 1;
  font-size: 12px;
  color: #333;
}

.analysisLine {
  padding: 6px 0;
}

.analysisHint {
  opacity: 0.85;
}

.analysisFooter {
  display: flex;
  justify-content: flex-end;
}

.saveBtn {
  height: 44px;
  min-width: 240px;
  border: none;
  border-radius: 8px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 900;
  cursor: pointer;
}

.saveBtn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Fullscreen image preview (lightbox) */
.imgBackdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 12000;
}

.imgModal {
  position: relative;
  width: min(1400px, 96vw);
  height: min(900px, 94vh);
  background: #111;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.15);
  box-shadow: 0 18px 50px rgba(0,0,0,0.45);
  display: flex;
  flex-direction: column;
}

.imgClose {
  position: absolute;
  top: 10px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 999px;
  background: rgba(255,255,255,0.15);
  color: white;
  font-size: 22px;
  cursor: pointer;
  z-index: 1;
}

.imgFull {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.imgCaption {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 10px 12px;
  color: #fff;
  background: linear-gradient(to top, rgba(0,0,0,0.7), rgba(0,0,0,0));
  font-size: 12px;
}

.muted {
  opacity: 0.8;
}

</style>
