<template>
  <nav class="w-56 bg-white border-r border-[#E5E7EB] flex flex-col h-full shrink-0">
    <div class="p-5 border-b border-[#E5E7EB]">
      <h1 class="text-lg font-bold text-[#E53935] font-['Noto_Serif_SC']">广场舞队形编排</h1>
      <p class="text-sm text-[#6B7280] mt-0.5">社区舞蹈管理系统</p>
    </div>
    <div class="flex-1 py-3 px-3 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-base font-medium transition-colors duration-150"
        :class="[
          isActive(item.path)
            ? 'bg-[#E53935]/10 text-[#E53935]'
            : 'text-[#6B7280] hover:bg-gray-50 hover:text-[#1F2937]',
        ]"
      >
        <component :is="item.icon" :size="20" />
        <span>{{ item.label }}</span>
      </router-link>
    </div>
    <div class="p-4 border-t border-[#E5E7EB]">
      <p class="text-xs text-[#9CA3AF]">社区广场舞 v1.0</p>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Music, LayoutGrid, Users, ArrowLeftRight, BarChart3 } from 'lucide-vue-next'

const route = useRoute()

const navItems = [
  { path: '/songs', label: '曲目档案', icon: Music },
  { path: '/formation', label: '队形编排', icon: LayoutGrid },
  { path: '/members', label: '成员站位', icon: Users },
  { path: '/substitute', label: '替补调整', icon: ArrowLeftRight },
  { path: '/statistics', label: '统计分析', icon: BarChart3 },
]

function isActive(path: string) {
  return route.path === path
}
</script>
