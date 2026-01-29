<template>
  <div class="shell">
    <Sidebar />
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import Sidebar from "./components/Sidebar.vue";
</script>
