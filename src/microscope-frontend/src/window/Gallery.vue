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
          @click="selectedId = img.id"
        >
          <div class="thumb">
            <img :src="img.thumbUrl" alt="thumbnail" />
          </div>

          <div class="meta">
            <div class="filename">{{ img.name }}</div>
            <div class="datetime">{{ formatDate(img.datetime) }}</div>

            <div class="actions">
              <button class="iconBtn" @click.stop="openDetails(img)">
                <span class="material-symbols-outlined">bar_chart</span>
              </button>

              <button class="iconBtn" @click.stop="downloadOne(img)">
                <span class="material-symbols-outlined">download</span>
              </button>

              <button class="iconBtn" @click.stop="deleteOne(img)">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </div>

            <button class="analyzeBtn" @click.stop="analyze(img)">
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
</template>

<script setup>
import { ref, computed } from "vue";

const gallery = ref([
  
]); // START EMPTY
const query = ref("");
const selectedId = ref("");

const modalOpen = ref(false);
const modalItem = ref(null);
const modalNotes = ref("");
const modalAnnotations = ref([]);
const modalTags = ref([]);

const annoKey = ref("");
const annoValue = ref("");
const tagInput = ref("");

const filtered = computed(() => {
  if (!query.value) return gallery.value;
  return gallery.value.filter(img =>
    img.name.toLowerCase().includes(query.value.toLowerCase())
  );
});

function formatDate(d) {
  return d ? d.replace("T", " ").slice(0, 19) : "";
}

function openDetails(img) {
  modalItem.value = img;
  modalNotes.value = img.notes || "";
  modalAnnotations.value = [...(img.annotations || [])];
  modalTags.value = [...(img.tags || [])];
  modalOpen.value = true;
}

function closeModal() {
  modalOpen.value = false;
}

function addModalAnnotation() {
  if (!annoKey.value || !annoValue.value) return;
  modalAnnotations.value.push({ key: annoKey.value, value: annoValue.value });
  annoKey.value = annoValue.value = "";
}

function addModalTag() {
  if (!tagInput.value) return;
  modalTags.value.push(tagInput.value);
  tagInput.value = "";
}

function saveModal() {
  Object.assign(modalItem.value, {
    notes: modalNotes.value,
    annotations: modalAnnotations.value,
    tags: modalTags.value,
  });
  modalOpen.value = false;
}

function analyze(img) { console.log("ANALYZE", img.name); }
function downloadOne(img) { console.log("DOWNLOAD", img.name); }
function deleteOne(img) {
  gallery.value = gallery.value.filter(x => x.id !== img.id);
}
function downloadAll() { console.log("DOWNLOAD ALL"); }
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
  grid-template-columns: repeat(auto-fit, 240px);
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
  height: 140px;
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
</style>
