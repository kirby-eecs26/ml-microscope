<template>
  <div class="shell">
    <Sidebar v-if="!$route.meta.hideSidebar" />  
    <main class="content" :class="{ 'full-width': $route.meta.hideSidebar }">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import Sidebar from "./components/Sidebar.vue";
</script>
