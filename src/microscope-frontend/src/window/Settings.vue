<template>
  <div class="settingsPage">
    <!-- Settings sidebar (right of main sidebar) -->
    <aside class="settingsSidebar">
      <!-- Application Settings Section -->
      <div class="settingsSection">
        <div class="sectionTitle">Application Settings</div>
        <div class="settingsNav">
          <div class="navItem active">
            Display
          </div>
          <div class="navItem">
            Features
          </div>
        </div>
      </div>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- Microscope Settings Section -->
      <div class="settingsSection">
        <div class="sectionTitle" id="MicroscopeSettingsTitle">Microscope Settings</div>
        <div class="settingsNav">
          <div class="navItem">
            Camera
          </div>
          <div class="navItem">
            Stage
          </div>
          <div class="navItem">
            Camera / Stage Mapping
          </div>
          <div class="navItem">
            General
          </div>
        </div>
      </div>

    </aside>

    <!-- Main settings content area -->
    <main class="settingsContent">
      <!-- Display settings (active tab) -->
      <div class="displaySettings">
        <h2 class="contentTitle">Display Settings</h2>

        <!-- Theme section -->
        <div class="settingGroup">
          <h3 class="settingTitle">Theme</h3>
          <div class="settingControl">
            <select id="themeSelect" v-model="selectedTheme" class="themeDropdown">
              <option value="system">System</option>
              <option value="dark">Dark Mode</option>
            </select>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Theme selection
const selectedTheme = ref('system')
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

.themeDropdown:focus {
  outline: none;
  border-color: #1f4b7a;
}
</style>