<template>
  <div class="galleryPage">
    <!-- Top bar -->
    <header class="topbar">
      <div class="title">GALLERY</div>

      <div class="searchWrap">
        <input class="search" v-model="query" placeholder="Search" />
        <span class="material-symbols-outlined searchIcon">search</span>
      </div>

      <div class="actionButtons">
        <button class="csvBtn" @click="downloadCSV">Download CSV</button>

        <button class="downloadAll" @click="downloadAll" :disabled="zipBusy">
          {{ zipBusy ? "Creating..." : (zipReady ? "Download Zip" : "Create Zip") }}
        </button>
      </div>
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
          v-for="img in paged"
          :key="img.id"
          class="card"
          :class="{ selected: selectedId === img.id }"
        >
          <div class="thumb" @click="openPreview(img)">
            <img
              v-if="img.type !== 'video'"
              :src="img.thumbUrl || img.url || '/cell.jpg'"
              alt="thumbnail"
            />
            <div v-else class="videoThumb">
              <video :src="img.url" muted playsinline preload="metadata"></video>
              <div class="playOverlay">
                <span class="material-symbols-outlined">play_circle</span>
              </div>
            </div>
          </div>

          <div class="meta" @click="openDetails(img)">
            <div class="filename">{{ img.name }}</div>
            <div class="datetime">{{ formatDate(img.datetime) }}</div>

            <div class="actions">
              <button
                class="iconBtn"
                type="button"
                title="Export annotations CSV"
                @click.stop="downloadAnnotationsCsv(img)"
              >
                <!--<span class="material-symbols-outlined">bar_chart</span>-->
                <span class="material-symbols-outlined">csv</span>
              </button>

              <button class="iconBtn" @click.stop="downloadOne(img)">
                <span class="material-symbols-outlined">download</span>
              </button>

              <button class="iconBtn" @click.stop="askDelete(img)">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </div>

            <button class="analyzeBtn" @click.stop="runAnalysis(img)">
              ANALYZE
            </button>
            <!-- Tags row (visible on card) -->
            <div class="cardTags" :class="{ empty: displayTags(img).length === 0 }">
                <span
                  v-for="t in displayTags(img)"
                  :key="t"
                  class="tagChip"
                  :title="`Remove tag '${t}'`"
                  @click.stop="askRemoveTag(img, t)"
                >
                  {{ t }}
                </span>
                 <!-- Add Tag chip (always at end/right of the row) -->
                <button
                  class="tagChip tagAddChip"
                  @click.stop="openAddTag(img)"
                  title="Add tag"
                  type="button"
                >
                  + ADD
                </button>
            </div>
          </div>
        </div>
      </div>


      <!-- Pagination -->
      <footer v-if="totalPages > 1" class="pager">
        <button class="navBtn" :disabled="page === 1" @click="page = Math.max(1, page - 1)">
          ← Previous
        </button>

        <button
          v-for="it in pageModel"
          :key="it.type === 'page' ? it.page : it.key"
          class="pageBtn"
          :class="{ active: it.type === 'page' && it.page === page, ellipsis: it.type === 'ellipsis' }"
          :disabled="it.type === 'ellipsis'"
          @click="it.type === 'page' && (page = it.page)"
        >
          {{ it.type === 'page' ? it.page : '…' }}
        </button>

        <button class="navBtn" :disabled="page === totalPages" @click="page = Math.min(totalPages, page + 1)">
          Next →
        </button>
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
          <div class="analysisHeaderLeft">
            <div class="analysisTitle">Analysis</div>
            <div class="analysisSubTitle">{{ analysisItem?.name }}</div>
          </div>

          <button class="closeX" @click="closeAnalysisModal">×</button>
        </div>

        <div class="analysisDivider"></div>

        <div class="analysisGrid">
          <!-- LEFT: image + toggle -->
          <div class="analysisLeft">
            <div class="viewerHeader">
              <div class="viewerLabel">
                {{ analysisItem?.type === "video" ? "Video Preview" : "Image Preview" }}
              </div>

              <div class="viewerControls">
                <!-- Sensitivity (VIDEO ONLY) -->
                <div v-if="analysisItem?.type === 'video'" class="sensControl">
                  <div class="sensLabel">Sensitivity</div>

                  <div class="segmented">
                    <button
                      class="segBtn"
                      :class="{ active: motionSensitivity === 'low' }"
                      :disabled="analysisLoading"
                      @click="setSensitivity('low')"
                      type="button"
                    >
                      Low
                    </button>

                    <button
                      class="segBtn"
                      :class="{ active: motionSensitivity === 'medium' }"
                      :disabled="analysisLoading"
                      @click="setSensitivity('medium')"
                      type="button"
                    >
                      Med
                    </button>

                    <button
                      class="segBtn"
                      :class="{ active: motionSensitivity === 'high' }"
                      :disabled="analysisLoading"
                      @click="setSensitivity('high')"
                      type="button"
                    >
                      High
                    </button>
                  </div>
                </div>

                <!-- Image toggle -->
                <button
                  v-if="analysisItem?.type !== 'video'"
                  class="toggleBtn"
                  :disabled="!analysisResult?.overlayImageUrl"
                  @click="overlayOn = !overlayOn"
                >
                  {{ overlayOn ? "Show Original" : "Show Overlay" }}
                </button>

                <!-- Video toggle -->
                <button
                  v-if="analysisItem?.type === 'video'"
                  class="toggleBtn"
                  :disabled="!analysisResult?.overlayVideoUrl"
                  @click="videoOverlayOn = !videoOverlayOn"
                >
                  {{ videoOverlayOn ? "Show Original" : "Show Tracks" }}
                </button>
              </div>
            </div>

            <div class="viewerFrame">
              <!-- IMAGE -->
              <img
                v-if="analysisItem?.type !== 'video'"
                class="viewerImg"
                :src="overlayOn && analysisResult?.overlayImageUrl
                  ? analysisResult.overlayImageUrl
                  : (analysisItem?.url || analysisItem?.thumbUrl || '/cell.jpg')"
                alt="analysis preview"
              />

              <!-- VIDEO -->
              <video
                v-else
                :key="videoOverlayOn
                  ? `tracks-${analysisResult?.overlayVideoUrl || ''}`
                  : `orig-${analysisItem?.url || ''}`"
                class="viewerImg"
                :src="videoOverlayOn && analysisResult?.overlayVideoUrl
                  ? analysisResult.overlayVideoUrl
                  : analysisItem?.url"
                controls
                playsinline
                @error="onVideoError"
                @loadedmetadata="onVideoMeta"
                @canplay="onVideoCanPlay"
              ></video>

              <div v-if="analysisLoading" class="viewerOverlay">Analyzing...</div>
              <div v-else-if="analysisError" class="viewerOverlay error">{{ analysisError }}</div>

              <div
                v-else-if="analysisItem?.type !== 'video' && overlayOn && !analysisResult?.overlayImageUrl"
                class="viewerOverlay warn"
              >
                Overlay not available yet
              </div>
            </div>
          </div>

          <!-- RIGHT: results panel -->
          <div class="analysisRight">
            <div class="resultsTitle">Results:</div>

            <!-- IMAGE RESULTS -->
            <div v-if="analysisItem?.type !== 'video'" class="countBlock">
              <div class="countLabel">Blob Count</div>
              <div class="countValue">
                {{ analysisResult?.blobCount ?? "—" }}
              </div>
            </div>
            <!-- VIDEO RESULTS -->
            <div v-else class="countBlock">
              <div class="countLabel">Motility</div>
              <div class="countValue" style="font-size: 34px;">
                {{ analysisResult?.label ?? "—" }}
              </div>
              <div style="margin-top: 10px; font-size: 12px; opacity: 0.95;">
                <div><b>Motility Ratio:</b> {{ analysisResult?.motility_ratio ?? "—" }}</div>
                <div><b>Motion Score:</b> {{ analysisResult?.motion_score ?? "—" }}</div>
                <div><b>Avg Speed (px/s):</b> {{ analysisResult?.avg_speed_px_per_s ?? "—" }}</div>
                <div><b>Tracks:</b> {{ analysisResult?.tracks ?? "—" }}</div>
              </div>
            </div>

            <div class="resultsMeta">
              <div class="metaRow">
                <div class="metaKey">Image</div>
                <div class="metaVal">{{ analysisItem?.name }}</div>
              </div>
              <div class="metaRow">
                <div class="metaKey">ID</div>
                <div class="metaVal mono">{{ analysisItem?.id }}</div>
              </div>
              <div class="metaRow">
                <div class="metaKey">Time</div>
                <div class="metaVal">{{ formatDate(analysisItem?.datetime) }}</div>
              </div>
            </div>

            <div class="analysisFooter">
              <div v-if="savingAnalysis" class="saveStatus">
                <span class="spinner"></span>
                Saving...
              </div>

              <div v-else-if="saveOk" class="saveStatus ok">
                <span class="check">✓</span>
                Saved
              </div>

              <button class="saveBtn" :disabled="analysisLoading || !analysisResult || savingAnalysis" @click="saveAnalysis">
                SAVE ANALYSIS
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Fullscreen Preview -->
    <div v-if="previewOpen" class="imgBackdrop" @click="closePreview">
      <div class="imgModal" @click.stop>
        <button class="imgClose" @click="closePreview">×</button>

        <img
          v-if="previewItem?.type !== 'video'"
          class="imgFull"
          :src="previewItem?.url || previewItem?.thumbUrl || '/cell.jpg'"
          alt="full"
        />

        <video
          v-else
          class="imgFull"
          :src="previewItem?.url"
          controls
          autoplay
        ></video>

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
          <div class="label">Notes</div>
          <div v-if="getNotes(detailsItem)" class="detailText">
            {{ getNotes(detailsItem) }}
          </div>
          <div v-else class="muted">No notes</div>
        </div>

        <div class="divider"></div>

        <div class="section">
          <div class="label">Annotations</div>

          <div v-if="getAnnotationPairs(detailsItem).length" class="annoList">
            <div class="annoRowRead" v-for="a in getAnnotationPairs(detailsItem)" :key="a.key">
              <div class="annoKey">{{ a.key }}</div>
              <div class="annoVal">{{ a.value }}</div>
            </div>
          </div>

          <div v-else class="muted">No annotations</div>
        </div>

        <div class="modalFooter">
          <button class="okBtn" @click="closeDetails">OK</button>
        </div>
      </div>
    </div>

    <!-- Remove Tag Modal -->
    <div v-if="removeTagOpen" class="backdrop" @click.self="closeRemoveTag">
      <div class="miniModal" @click.stop>
        <div class="miniTitle">Remove tag "{{ removeTagValue }}"?</div>

        <div class="miniActions">
          <button class="miniBtn ghost" @click="closeRemoveTag" :disabled="removeTagBusy">No</button>
          <button class="miniBtn danger" @click="confirmRemoveTag" :disabled="removeTagBusy">
            {{ removeTagBusy ? "Removing..." : "Yes" }}
          </button>
        </div>

        <div v-if="removeTagError" class="miniError">{{ removeTagError }}</div>
      </div>
    </div>

    <!-- Add Tag Modal -->
    <div v-if="addTagOpen" class="backdrop" @click.self="closeAddTag">
      <div class="miniModal" @click.stop>
        <div class="miniTitle">Add tag</div>

        <input
          class="miniInput"
          v-model="addTagValue"
          placeholder="e.g. sample1"
          @keydown.enter.prevent="confirmAddTag"
        />

        <div class="miniActions">
          <button class="miniBtn ghost" @click="closeAddTag" :disabled="addTagBusy">
            Cancel
          </button>
          <button class="miniBtn danger" @click="confirmAddTag" :disabled="addTagBusy || !addTagValue.trim()">
            {{ addTagBusy ? "Saving..." : "Save" }}
          </button>
        </div>

        <div v-if="addTagError" class="miniError">{{ addTagError }}</div>
      </div>
    </div>

    <!-- Delete Image Modal -->
    <div v-if="confirmOpen" class="backdrop" @click.self="closeConfirm">
      <div class="miniModal" @click.stop>
        <div class="miniTitle">Delete "{{ confirmItem?.name }}"?</div>

        <div class="miniActions">
          <button class="miniBtn ghost" @click="closeConfirm" :disabled="deleting">
            No
          </button>
          <button class="miniBtn danger" @click="confirmDelete" :disabled="deleting">
            {{ deleting ? "Deleting..." : "Yes" }}
          </button>
        </div>

        <div v-if="deleteError" class="miniError">{{ deleteError }}</div>
      </div>
    </div>

</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { listCaptures, deleteCapture, analyzeCapture, deleteTag } from "../api/imageApi";
import { listVideos, deleteVideo, analyzeVideo } from "../api/videoApi";

console.log("BUILD_MARKER_GALLERY", Date.now());

const gallery = ref([
]); // will be loaded from backend
const query = ref("");

/** Pagination */
const page = ref(1);
const pageSize = 12; // 2 rows * 6 per row

const totalPages = computed(() => {
  const n = filtered.value.length;
  return Math.max(1, Math.ceil(n / pageSize));
});
/*
const pageNumbers = computed(() =>
  Array.from({ length: totalPages.value }, (_, i) => i + 1)
); */

// The items actually shown on the current page
const paged = computed(() => {
  const start = (page.value - 1) * pageSize;
  return filtered.value.slice(start, start + pageSize);
});

const pageModel = computed(() => {
  const t = totalPages.value;
  const p = page.value;

  // small counts: just show all
  if (t <= 7) {
    return Array.from({ length: t }, (_, i) => ({ type: "page", page: i + 1 }));
  }

  const items = [];
  const addPage = (n) => items.push({ type: "page", page: n });
  const addEllipsis = (key) => items.push({ type: "ellipsis", key });

  addPage(1);

  const start = Math.max(2, p - 2);
  const end = Math.min(t - 1, p + 2);

  if (start > 2) addEllipsis("l");

  for (let n = start; n <= end; n++) addPage(n);

  if (end < t - 1) addEllipsis("r");

  addPage(t);

  return items;
});

// Optional but recommended: when search changes, go back to page 1
watch(query, () => {
  page.value = 1;
});


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
const overlayOn = ref(false);
const videoOverlayOn = ref(false);
const savingAnalysis = ref(false);
const saveOk = ref(false);
const saveMsg = ref("");
const motionSensitivity = ref("medium"); // 'low' | 'medium' | 'high'

/** Remove tag */
const removeTagOpen = ref(false);
const removeTagBusy = ref(false);
const removeTagError = ref("");
const removeTagItem = ref(null);
const removeTagValue = ref("");

/** Add tag */
const addTagOpen = ref(false);
const addTagBusy = ref(false);
const addTagError = ref("");
const addTagItem = ref(null);
const addTagValue = ref("");

/** Zip builder */
const zipBusy = ref(false);
const zipReady = ref(false);
const zipId = ref(null);
const zipError = ref(""); 

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  window.location.origin || // if UI is served by uvicorn
  "http://127.0.0.1:8000";  // fallback for packaged app

const filtered = computed(() => {
  const q = query.value?.trim().toLowerCase();
  if (!q) return gallery.value;
  return gallery.value.filter((img) => (img.name || "").toLowerCase().includes(q));
});

function formatDate(d) {
  return d ? String(d).replace("T", " ").slice(0, 19) : "";
}

function isVideo(item) {
  return item?.type === "video";
}

function onVideoError(e) {
  const v = e?.target;
  console.log("[video] ERROR", {
    src: v?.currentSrc,
    networkState: v?.networkState,
    readyState: v?.readyState,
    error: v?.error ? { code: v.error.code, message: v.error.message } : null,
  });
}

function onVideoMeta(e) {
  const v = e?.target;
  console.log("[video] loadedmetadata", {
    src: v?.currentSrc,
    duration: v?.duration,
    videoWidth: v?.videoWidth,
    videoHeight: v?.videoHeight,
  });
}

function onVideoCanPlay(e) {
  const v = e?.target;
  console.log("[video] canplay", { src: v?.currentSrc, t: Date.now() });
}

/**
 * Normalize whatever your backend returns into:
 * { id, name, datetime, url, thumbUrl }
 */
function normalizeCaptures(payload) {
  const items = payload?.captures ?? payload ?? [];
  return items.map((c) => {
    const id = c.id;
    return {
      id,
      type: "image",
      name: c.name ?? "capture",
      datetime: c.time ?? "",
      url: `${API_BASE}/captures/${encodeURIComponent(id)}/image`,
      thumbUrl: `${API_BASE}/captures/${encodeURIComponent(id)}/image`,
      tags: c.tags ?? [],
      raw: c,
    };
  });
}

function normalizeVideos(payload) {
  const items = payload?.videos ?? payload ?? [];
  return items.map((v) => ({
    id: v.id,
    type: "video",
    name: v.name ?? "video",
    datetime: v.time ?? "",
    url: `${API_BASE}/video/${encodeURIComponent(v.id)}/download`,
    thumbUrl: null,
    tags: v.tags ?? [],
    raw: v,
  }));
}

async function refreshAll() {
  const [caps, vids] = await Promise.all([listCaptures(), listVideos()]);
  const images = normalizeCaptures(caps).map(x => ({ ...x, type: "image" }));
  const videos = normalizeVideos(vids);
  gallery.value = [...videos, ...images];
}

function getNotes(img) {
  const ann = img?.raw?.annotations || {};
  const notes = ann?.Notes;
  return notes ? String(notes) : "";
}

function getAnnotationPairs(img) {
  const ann = img?.raw?.annotations || {};
  return Object.entries(ann)
    .filter(([k]) => k && k !== "Notes") // Notes displayed separately
    .map(([k, v]) => ({ key: String(k), value: String(v ?? "") }));
}

function askRemoveTag(img, tag) {
  removeTagItem.value = img;
  removeTagValue.value = tag;
  removeTagError.value = "";
  removeTagOpen.value = true;
}

function closeRemoveTag(force = false) {
  if (removeTagBusy.value && !force) return;
  removeTagOpen.value = false;
  removeTagItem.value = null;
  removeTagValue.value = "";
  removeTagError.value = "";
}

async function confirmRemoveTag() {
  if (!removeTagItem.value || !removeTagValue.value) return;

  removeTagBusy.value = true;
  removeTagError.value = "";

  try {
    const id = removeTagItem.value.id;
    const tag = removeTagValue.value;
    const base = import.meta.env.VITE_API_BASE || "";
    if (removeTagItem.value.type === "video") {
      const res = await fetch(
        `${base}/video/${encodeURIComponent(id)}/tags/${encodeURIComponent(tag)}`,
        { method: "DELETE" }
      );
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Failed to remove tag (${res.status})`);
      }
    } else {
      await deleteTag(id, tag);
    }
    const target = gallery.value.find((x) => x.id === id);
    if (target) {
      target.tags = (target.tags || []).filter(
        (t) => String(t) !== String(tag)
      );
    }
    closeRemoveTag(true);
  } catch (e) {
    removeTagError.value = String(e?.message || e);
  } finally {
    removeTagBusy.value = false;
  }
}

function openAddTag(img) {
  addTagItem.value = img;
  addTagValue.value = "";
  addTagError.value = "";
  addTagOpen.value = true;
}

function closeAddTag(force = false) {
  if (addTagBusy.value && !force) return;
  addTagOpen.value = false;
  addTagItem.value = null;
  addTagValue.value = "";
  addTagError.value = "";
}

async function confirmAddTag() {
  if (!addTagItem.value) return;
  const newTag = addTagValue.value.trim();
  if (!newTag) return;
  addTagBusy.value = true;
  addTagError.value = "";

  try {
    const id = addTagItem.value.id;
    const current = Array.isArray(addTagItem.value.tags) ? addTagItem.value.tags : [];
    const merged = Array.from(new Set([...current, newTag]))
      .map(t => String(t).trim())
      .filter(t => t && t !== "temporary");
    const base = import.meta.env.VITE_API_BASE || "";
    const res = await fetch(
      addTagItem.value.type === "video"
        ? `${base}/video/${encodeURIComponent(id)}/tags`
        : `${base}/captures/${encodeURIComponent(id)}/tags`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tags: merged }),
      }
    );
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `Failed to add tag (${res.status})`);
    }
    const target = gallery.value.find((x) => x.id === id);
    if (target) target.tags = merged;
    closeAddTag(true);
  } catch (e) {
    addTagError.value = String(e?.message || e);
  } finally {
    addTagBusy.value = false;
  }
}

onMounted(async () => {
  try {
    await refreshAll();
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
  console.log("DETAILS ITEM RAW:", img.raw);
  console.log("DETAILS TAGS FIELD:", img.tags);
  detailsItem.value = img;
  detailsOpen.value = true;
}

function closeDetails() {
  detailsOpen.value = false;
  detailsItem.value = null;
}

async function downloadOne(img) {
  try {
    const base = import.meta.env.VITE_API_BASE || "";
    const url =
      img.type === "video"
        ? `${base}/video/${encodeURIComponent(img.id)}/download?dl=1`
        : `${base}/captures/${encodeURIComponent(img.id)}/image`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Download failed: ${res.status} ${res.statusText}`);
    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);
    const rawName = (img.name || (img.type === "video" ? `video_${img.id}` : `capture_${img.id}`)).trim();
    const safeName = rawName.replace(/[^\w.-]+/g, "_");
    let filename = safeName;
    if (img.type === "video") {
      if (!filename.toLowerCase().endsWith(".mp4")) filename += ".mp4";
    } else {
      const lower = filename.toLowerCase();
      const hasImgExt = lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".png");
      if (!hasImgExt) filename += ".jpeg";
    }
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(objectUrl);
  } catch (e) {
    console.error(e);
  }
}

async function downloadAnnotationsCsv(item) {
  try {
    const itemType = item.type === "video" ? "video" : "capture";
    const url = `${API_BASE}/export/annotations/${itemType}/${encodeURIComponent(item.id)}`;

    const res = await fetch(url);
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(text || `CSV download failed (${res.status})`);
    }

    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);

    const rawName = (item.name || `${itemType}_${item.id}`).trim();
    const safeName = rawName.replace(/[^\w.-]+/g, "_");
    const filename = `${safeName}_annotations.csv`;

    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(objectUrl);
  } catch (e) {
    console.error(e);
  }
}


function displayResolution(img) {
  const ann = img?.raw?.annotations || {};
  if (ann.Size) return String(ann.Size);
  if (ann.Resolution === "RAW") return "832x624";
  if (ann.Resolution === "FULL") return "3280x2464";
  return "Unknown";
}

function displayTags(cap) {
  const tags = Array.isArray(cap?.tags) ? cap.tags : [];
  return tags.map(t => String(t).trim()).filter(t => t && t !== "temporary");
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
    if (confirmItem.value.type === "video") {
      await deleteVideo(confirmItem.value.id);
    } else {
      await deleteCapture(confirmItem.value.id);
    }
    gallery.value = gallery.value.filter((x) => x.id !== confirmItem.value.id);
    closeConfirm();
  } catch (e) {
    deleteError.value = String(e?.message || e);
  } finally {
    deleting.value = false;
  }
}

async function downloadAll() {
  try {
    zipError.value = "";
    const base = import.meta.env.VITE_API_BASE || "";
    if (zipReady.value && zipId.value) {
      await downloadZipById(zipId.value);
      return;
    }
    zipBusy.value = true;
    zipReady.value = false;
    zipId.value = null;
    const startRes = await fetch(`${base}/zip/build`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!startRes.ok) {
      const text = await startRes.text();
      throw new Error(text || `Zip build failed (${startRes.status})`);
    }
    const startJson = await startRes.json();
    const newZipId = startJson?.id;
    if (!newZipId) throw new Error("Zip build did not return an id");
    zipId.value = newZipId;
    zipReady.value = true;
    await downloadZipById(newZipId);
  } catch (e) {
    console.error(e);
    zipError.value = String(e?.message || e);
  } finally {
    zipBusy.value = false;
  }
}

async function downloadZipById(id) {
  const base = import.meta.env.VITE_API_BASE || "";
  const url = `${base}/zip/get/${encodeURIComponent(id)}`;

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Zip download failed: ${res.status} ${res.statusText}`);

  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = `gallery_${id}.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(objectUrl);
}

async function downloadCSV() {
  try {
    const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
    const res = await fetch(`${base}/export/csv`);
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(text || `CSV export failed (${res.status})`);
    }
    const blob = await res.blob();
    const objectUrl = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = "gallery_export.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(objectUrl);
  } catch (e) {
    console.error(e);
  }
}

/** Analyze */
async function runAnalysis(item) {
  analysisItem.value = item;
  analysisOpen.value = true;
  analysisLoading.value = true;
  analysisError.value = "";
  analysisResult.value = null;
  overlayOn.value = false;
  try {
    const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
    if (!isVideo(item)) {
      const res = await analyzeCapture(item.id);
      const overlayUrlRaw = res.overlayImageUrl ?? null;
      const overlayUrl = overlayUrlRaw
        ? (overlayUrlRaw.startsWith("http") ? overlayUrlRaw : `${base}${overlayUrlRaw}`)
        : null;
      analysisResult.value = {
        kind: "image",
        blobCount: res.blobCount ?? 0,
        overlayImageUrl: overlayUrl,
      };
    } else {
      const res = await analyzeVideo(item.id, {
        type: "motion_tracking",
        mode: "ml_kmeans",
        sensitivity: motionSensitivity.value,
      });
      const a = res.analysis || {};
      const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
      const overlayVideoUrlRaw = res.overlayVideoUrl ?? null;
      const overlayVideoUrl = overlayVideoUrlRaw
        ? (
            overlayVideoUrlRaw.startsWith("http")
              ? `${overlayVideoUrlRaw}${overlayVideoUrlRaw.includes("?") ? "&" : "?"}t=${Date.now()}`
              : `${base}${overlayVideoUrlRaw}?t=${Date.now()}`
          )
        : null;
      analysisResult.value = {
        kind: "video",
        overlayVideoUrl,
        label: a.label ?? "—",
        motion_score: a.motion_score ?? 0,
        motility_ratio: a.motility_ratio ?? 0,
        avg_speed_px_per_s: a.avg_speed_px_per_s ?? 0,
        tracks: a.tracks ?? 0,
        ml: a.ml ?? null,
        debug: a.debug ?? null,
      };
      videoOverlayOn.value = false;
    }
  } catch (e) {
    analysisError.value = String(e?.message || e);
  } finally {
    analysisLoading.value = false;
  }
}

async function saveAnalysis() {
  if (!analysisItem.value || !analysisResult.value) return;

  savingAnalysis.value = true;
  saveOk.value = false;
  saveMsg.value = "";

  try {
    const base = import.meta.env.VITE_API_BASE || "";

    if (analysisItem.value.type !== "video") {
      const existingAnn = analysisItem.value?.raw?.annotations || {};
      const nextAnn = {
        ...existingAnn,
        ML_BlobCount: Number(analysisResult.value.blobCount ?? 0),
        ML_AnalyzedAt: new Date().toISOString(),
      };
      const res = await fetch(`${base}/captures/${encodeURIComponent(analysisItem.value.id)}/metadata`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ annotations: nextAnn }),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Save analysis failed: ${res.status} ${txt}`);
      }
    } else {
      const payload = {
        analysis: {
          type: "motion_tracking",
          label: analysisResult.value.label,
          motility_ratio: analysisResult.value.motility_ratio,
          motion_score: analysisResult.value.motion_score,
          avg_speed_px_per_s: analysisResult.value.avg_speed_px_per_s,
          tracks: analysisResult.value.tracks,
          ml: analysisResult.value.ml ?? null,
          analyzed_at: new Date().toISOString(),
        },
      };
      const res = await fetch(`${base}/video/${encodeURIComponent(analysisItem.value.id)}/analysis`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Save analysis failed: ${res.status} ${txt}`);
      }
    }

    saveOk.value = true;
    saveMsg.value = "Saved";

    await refreshAll();
    const updated = gallery.value.find((x) => x.id === analysisItem.value.id);
    if (updated) analysisItem.value = updated;

    setTimeout(() => {
      saveOk.value = false;
      saveMsg.value = "";
    }, 1500);
  } catch (e) {
    saveOk.value = false;
    saveMsg.value = String(e?.message || e);
    analysisError.value = saveMsg.value;
  } finally {
    savingAnalysis.value = false;
  }
}

async function setSensitivity(level) {
  motionSensitivity.value = level;
  if (!analysisItem.value || analysisItem.value.type !== "video") return;
  videoOverlayOn.value = false;
  analysisResult.value = null;
  await runAnalysis(analysisItem.value);
}

async function closeAnalysisModal() {
  try {
    const id = analysisItem.value?.id;
    const type = analysisItem.value?.type;
    const base = import.meta.env.VITE_API_BASE || "";
    if (id) {
      if (type === "video") {
        fetch(`${base}/analysis/video/${encodeURIComponent(id)}/tracks`, { method: "DELETE" });
      } else {
        fetch(`${base}/analysis/${encodeURIComponent(id)}`, { method: "DELETE" });
      }
    }
  } catch (e) {
  }
  analysisOpen.value = false;
  analysisItem.value = null;
  analysisResult.value = null;
  analysisError.value = "";
  analysisLoading.value = false;
  if (typeof videoOverlayOn !== "undefined") videoOverlayOn.value = false;
  if (typeof overlayOn !== "undefined") overlayOn.value = false;
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
  grid-template-columns: 120px 1fr auto;
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

.cardTags {
  grid-column: 1 / -1;
  grid-row: 4;

  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 26px;
  padding-top: 2px;
}

.tagChip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.92);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tagAddChip {
  background: rgba(255,255,255,0.16);
  border: 1px dashed rgba(255,255,255,0.45);
  color: rgba(255,255,255,0.9);
  cursor: pointer;
}

.tagAddChip:hover {
  background: rgba(255,255,255,0.22);
}

.tagAddChip:active {
  transform: translateY(1px);
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-self: end;   
}

.csvBtn {
  height: 30px;
  padding: 0 18px;
  margin: 0 20px;
  border: none;
  border-radius: 6px;
  background: #1f4b7a;  
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}

.csvBtn:hover {
  filter: brightness(0.95);
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
  grid-template-columns: repeat(6, 210px);
  gap: 22px;
  justify-content: start; 
}

.card {
  border: 1px solid #bdbdbd;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  background: #1f4b7a;
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

.pager{
  margin-top: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 18px 0 10px;
}

.pageBtn.active{
  background: #1f4b7a;   
  border-color: #1f4b7a;
  color: #ffffff;
  font-weight: 800;
  box-shadow: 0 0 0 2px rgba(31,75,122,0.25);
}

/* shared button baseline */
.navBtn,
.pageBtn{
  height: 26px;
  min-height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 26px;
  font-size: 12px;
  font-weight: 700;
  border-radius: 8px;
  border: 1px solid #bdbdbd;
  background: #fff;
  color: #111;
  padding: 0 10px;
  cursor: pointer;
  vertical-align: middle;
  user-select: none;
}

/* numbers are square-ish pills */
.pageBtn{
  width: 26px;
  padding: 0;
}

/* ellipsis */
.pageBtn.ellipsis{
  border: none;
  background: transparent;
  width: auto;
  padding: 0 6px;
  cursor: default;
  color: rgba(255,255,255,0.75);
}

/* disabled */
.navBtn:disabled,
.pageBtn:disabled{
  opacity: 0.45;
  cursor: not-allowed;
}

html.theme-dark .navBtn,
html.theme-dark .pageBtn{
  background: rgba(255,255,255,0.92);
  border-color: rgba(255,255,255,0.65);
  color: #111;
}


/* Card contents */
.meta {
  position: relative;
  padding: 10px 10px 12px;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto auto auto;
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
  font-size: 14ggpx;
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
  width: min(1240px, 94vw);
  height: min(760px, 88vh);
  background: #ffffff;
  border: 1px solid #cfcfcf;
  border-radius: 10px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.35);
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
}

.analysisHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.analysisHeaderLeft {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.analysisTitle {
  font-size: 14px;
  font-weight: 900;
  color: #1f4b7a;
  letter-spacing: 0.2px;
}

.analysisSubTitle {
  font-size: 12px;
  color: #3b3b3b;
  opacity: 0.85;
}

.closeX {
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  font-size: 26px;
  line-height: 1;
  cursor: pointer;
  color: #1f4b7a;
  border-radius: 8px;
}
.closeX:hover {
  background: rgba(31, 75, 122, 0.08);
}

.analysisDivider {
  height: 1px;
  background: #e2e2e2;
  margin: 12px 0;
}

/* Layout: left viewer + right results */
.analysisGrid {
  flex: 1;
  display: grid;
  grid-template-columns: 1.6fr 0.85fr;
  gap: 14px;
  min-height: 0; /* IMPORTANT so children can scroll/fit */
}

.analysisLeft,
.analysisRight {
  min-height: 0;
  border-radius: 10px;
}

.viewerControls{
  display: flex;
  align-items: center;
  gap: 10px;
}

.sensControl{
  display: flex;
  align-items: center;
  gap: 10px;
  padding-right: 8px;
  border-right: 1px solid rgba(31, 75, 122, 0.18);
  margin-right: 6px;
}

.sensLabel{
  font-size: 11px;
  font-weight: 900;
  color: #1f4b7a;
  opacity: 0.95;
}

.segmented{
  display: inline-flex;
  border: 1px solid rgba(31, 75, 122, 0.35);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(31, 75, 122, 0.06);
}

.segBtn{
  height: 34px;
  padding: 0 12px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 900;
  color: #1f4b7a;
  cursor: pointer;
}

.segBtn:hover{
  background: rgba(31, 75, 122, 0.08);
}

.segBtn.active{
  background: #1f4b7a;
  color: #fff;
}

.segBtn:disabled{
  opacity: 0.5;
  cursor: not-allowed;
}

/* LEFT */
.analysisLeft {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.viewerHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.viewerLabel {
  font-size: 12px;
  font-weight: 900;
  color: #1f4b7a;
  letter-spacing: 0.2px;
}

.toggleBtn {
  height: 34px;
  padding: 0 14px;
  border-radius: 8px;
  background: #1f4b7a;
  color: #fff;
  border: 1px solid #1f4b7a;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}
.toggleBtn:hover {
  filter: brightness(0.95);
}
.toggleBtn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* Image frame keeps image contained without changing its actual resolution */
.viewerFrame {
  position: relative;
  flex: 1;
  min-height: 0;
  border-radius: 10px;
  border: 1px solid rgba(31, 75, 122, 0.25);
  background: rgba(31, 75, 122, 0.06);
  overflow: hidden;
  display: grid;
  place-items: center;
}

.viewerImg {
  width: 100%;
  height: 100%;
  object-fit: contain; /* KEY: contained, not stretched */
  display: block;
}

/* status overlays */
.viewerOverlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(0,0,0,0.35);
  color: #fff;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.2px;
}
.viewerOverlay.error {
  background: rgba(176, 0, 32, 0.55);
}
.viewerOverlay.warn {
  background: rgba(31, 75, 122, 0.55);
}

/* RIGHT */
.analysisRight {
  border: 1px solid rgba(31, 75, 122, 0.25);
  background: rgba(31, 75, 122, 0.06);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.resultsTitle {
  font-size: 13px;
  font-weight: 900;
  color: #1f4b7a;
}

.countBlock {
  border-radius: 12px;
  background: #1f4b7a;
  color: #fff;
  padding: 14px 14px;
  border: 1px solid rgba(255,255,255,0.18);
}

.countLabel {
  font-size: 12px;
  font-weight: 900;
  opacity: 0.95;
  letter-spacing: 0.2px;
}

.countValue {
  font-size: 56px;
  font-weight: 1000;
  line-height: 1.0;
  margin-top: 6px;
}

.resultsMeta {
  display: grid;
  gap: 10px;
  padding: 12px;
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(31, 75, 122, 0.15);
  border-radius: 12px;
}

.metaRow {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 10px;
  align-items: baseline;
}

.metaKey {
  font-size: 11px;
  font-weight: 900;
  color: #1f4b7a;
  opacity: 0.95;
}

.metaVal {
  font-size: 12px;
  color: #222;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.metaVal.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

/* Footer pinned to bottom */
.analysisFooter {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
}

.saveBtn {
  height: 44px;
  min-width: 220px;
  border: none;
  border-radius: 10px;
  background: #1f4b7a;
  color: #fff;
  font-weight: 1000;
  cursor: pointer;
}
.saveBtn:hover {
  filter: brightness(0.95);
}
.saveBtn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
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

.detailText {
  white-space: pre-wrap;
  font-size: 12px;
  color: #111;
}

.annoList {
  display: grid;
  gap: 8px;
  margin-top: 8px;
}

.annoRowRead {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 10px;
  padding: 8px 10px;
  border: 1px solid #d8d8d8;
  border-radius: 8px;
  background: #fff;
}

.annoKey {
  font-weight: 800;
  color: #111;
  font-size: 12px;
}

.annoVal {
  color: #333;
  font-size: 12px;
  white-space: pre-wrap;
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

.miniModal {
  width: min(380px, 92vw);
  background: #f6f6f6;
  border: 1px solid #cfcfcf;
  border-radius: 10px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.35);
  padding: 16px 18px;
}

.miniTitle {
  font-size: 14px;
  font-weight: 800;
  color: #111;
}

.miniActions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}

.miniBtn {
  height: 32px;
  padding: 0 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
  border: none;
}

.miniBtn.ghost {
  background: transparent;
  border: 1px solid #bdbdbd;
  color: #333;
}

.miniBtn.danger {
  background: #1f4b7a;
  color: #fff;
}

.miniBtn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.miniError {
  margin-top: 10px;
  font-size: 12px;
  color: #b00020;
}

/* Save analysis button */
.saveStatus {
  margin-right: auto;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 900;
  color: #1f4b7a;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(31, 75, 122, 0.08);
  border: 1px solid rgba(31, 75, 122, 0.18);
}

.saveStatus.ok {
  background: rgba(31, 75, 122, 0.12);
}

.check {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: #1f4b7a;
  color: #fff;
  font-size: 14px;
  line-height: 1;
}

.spinner {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  border: 2px solid rgba(31, 75, 122, 0.25);
  border-top-color: #1f4b7a;
  animation: spin 0.8s linear infinite;
}

.videoThumb { position: relative; width: 100%; height: 100%; }
.videoThumb video { width: 100%; height: 100%; object-fit: cover; }
.playOverlay {
  position: absolute; inset: 0;
  display: grid; place-items: center;
  background: rgba(0,0,0,0.25);
}
.playOverlay .material-symbols-outlined { font-size: 44px; color: #fff; }

@keyframes spin {
  to { transform: rotate(360deg); }
}

</style>
