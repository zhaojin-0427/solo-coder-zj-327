<template>
  <div class="flex h-screen overflow-hidden bg-[#F9FAFB]">
    <SideNav />
    <main class="flex-1 overflow-y-auto p-6">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import SideNav from '@/components/SideNav.vue'
</script>
