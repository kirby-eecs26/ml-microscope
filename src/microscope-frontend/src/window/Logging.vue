<template>
  <div class="loggingPage">
    <!-- Header with controls -->
    <div class="header">
      <div class="header-left">
        <span class="priority-label">Priority</span>
        <select v-model="selectedPriority" class="priority-dropdown">
          <!-- Change options as needed -->
          <option value="warning">Warning</option>
          <option value="info">Info</option>
          <option value="error">Error</option>
          <option value="debug">Debug</option>
          <option value="all">All</option>
        </select>
      </div>
      
      <div class="header-right">
        <button class="refresh-btn" @click="refreshLogs">
          REFRESH
        </button>
        <button class="download-btn" @click="downloadLogFile">
          DOWNLOAD LOG FILE
        </button>
      </div>
    </div>

    <!-- Log entries table -->
    <div class="logs-container">
      <!-- Empty for now -->
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <!-- a placeholder for now -->
      <span class="pagination-placeholder disabled">← Previous</span>
      <div class="page-numbers">
        <span class="page-number active">1</span>
        <span class="page-number">2</span>
        <span class="page-number">3</span>
      </div>
      <span class="pagination-placeholder">Next →</span>
    </div>
  </div>
</template>

<script setup>
// do script
</script>

<style scoped>
.loggingPage {
  padding: 20px;
  height: calc(100vh - 36px);
  background: var(--content-bg);
  display: flex;
  flex-direction: column;
  width: 100%;
  position: relative;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #B3B3B3;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.priority-label {
  font-size: 1rem;
  font-weight: 600;
  color: #1f4b7a;
}

.priority-dropdown {
  padding: 4px 8px;
  border: 1px solid #bdbdbd;
  border-radius: 4px;
  background: #fff;
  font-size: 0.7rem;
  color: #333;
  cursor: pointer;
  min-width: 100px;
}

.priority-dropdown:focus {
  outline: none;
  border-color: #333;
}

.header-right {
  display: flex;
  gap: 8px;
}

.refresh-btn, .download-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
}

.refresh-btn {
  background: #ffffff;
  color: #333;
  border: 1px solid #8a8a8a;
}

.download-btn {
  background: #1f4b7a;
  color: #fff;
}

/*.refresh-btn:hover {
  background: #d5d5d5;
}

.download-btn:hover {
  background: #163c63;
}*/

/* Pagination */
.pagination {
  display: flex;
  justify-content: center; 
  align-items: center;
  width: 100%;
  padding-top: 10px;
  border-top: 1px solid #B3B3B3;
  margin-top: auto;
}

.pagination-placeholder {
  font-size: 0.7rem;
  color: #333;
  padding: 6px 12px;
  border: 1px solid transparent;
  white-space: nowrap; 
}

.pagination-placeholder.disabled {
  color: #999; 
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 5px;
}

.page-number {
  width: 28px;
  height: 28px;
  /*border: 1px solid #bdbdbd;
  border-radius: 4px; 
  background: #fff;*/
  font-size: 0.7rem;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-number.active {
  background: #1f4b7a; 
  color: #fff; 
  border-color: #1f4b7a; 
}

</style>