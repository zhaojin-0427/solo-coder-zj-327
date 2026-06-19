<template>
  <div class="flex gap-5 h-[calc(100vh-3rem)]">
    <div class="w-64 bg-white rounded-xl border border-[#E5E7EB] flex flex-col shrink-0">
      <div class="p-4 border-b border-[#E5E7EB]">
        <h2 class="text-lg font-semibold text-[#1F2937]">选择曲目</h2>
      </div>
      <div class="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-thin">
        <div
          v-for="song in sortedSongs"
          :key="song.id"
          class="px-3 py-2.5 rounded-lg cursor-pointer transition-colors text-base"
          :class="[
            selectedSongId === song.id
              ? 'bg-[#E53935]/10 text-[#E53935] font-semibold'
              : 'text-[#6B7280] hover:bg-gray-50',
          ]"
          @click="selectSong(song.id)"
        >
          <div class="flex items-center justify-between">
            <span>{{ song.name }}</span>
            <span class="badge-gray text-xs">第{{ song.performance_order }}位</span>
          </div>
        </div>
        <div v-if="!songsStore.songs.length" class="text-center py-8 text-[#9CA3AF] text-sm">
          暂无曲目
        </div>
      </div>
    </div>

    <div class="flex-1 flex flex-col min-w-0">
      <div v-if="!selectedSongId" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <LayoutGrid :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
          <p class="text-lg text-[#6B7280]">请先在左侧选择一个曲目</p>
        </div>
      </div>

      <template v-else>
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-[#1F2937]">{{ currentSong?.name }} - 队形编排</h2>
            <p class="text-sm text-[#6B7280]" v-if="currentFormation">
              版本 v{{ currentFormation.version }}
              <span v-if="currentFormation.is_locked" class="badge-accent ml-2 text-xs">已锁定</span>
            </p>
          </div>
          <div class="flex gap-2">
            <button class="btn-accent flex items-center gap-1.5" @click="handleGenerate">
              <Sparkles :size="16" />
              生成初稿
            </button>
            <button
              class="btn-primary flex items-center gap-1.5"
              :disabled="!currentFormation || currentFormation.is_locked"
              @click="handleSave"
            >
              <Save :size="16" />
              保存
            </button>
            <button
              class="btn-secondary flex items-center gap-1.5"
              :disabled="!currentFormation || currentFormation.is_locked"
              @click="handleLock"
            >
              <Lock :size="16" />
              锁定版本
            </button>
          </div>
        </div>

        <div class="flex-1 flex items-center justify-center">
          <div v-if="formationsStore.loading" class="text-[#6B7280] text-lg">加载中...</div>
          <div v-else-if="!currentFormation" class="text-center">
            <p class="text-base text-[#6B7280]">暂无队形数据</p>
            <p class="text-sm text-[#9CA3AF] mt-1">点击「生成初稿」创建队形</p>
          </div>
          <FormationCanvas
            v-else
            :positions="currentFormation.positions"
            :canvas-width="700"
            :canvas-height="450"
            :dot-size="48"
            @position-move="handlePositionMove"
          />
        </div>

        <div v-if="formationsStore.versions.length" class="mt-4 bg-white rounded-xl border border-[#E5E7EB] p-4">
          <h3 class="text-base font-semibold text-[#1F2937] mb-3">版本历史</h3>
          <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
            <button
              v-for="f in formationsStore.versions"
              :key="f.id"
              class="shrink-0 px-4 py-2 rounded-lg border-2 text-sm font-medium transition-colors"
              :class="[
                currentFormation?.id === f.id
                  ? 'border-[#E53935] bg-[#E53935]/5 text-[#E53935]'
                  : 'border-[#E5E7EB] text-[#6B7280] hover:border-gray-300',
              ]"
              @click="formationsStore.loadFormationById(f.id)"
            >
              <span>v{{ f.version }}</span>
              <span v-if="f.is_locked" class="ml-1 text-xs">🔒</span>
              <span class="block text-xs text-[#9CA3AF] mt-0.5">{{ formatDate(f.created_at) }}</span>
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { LayoutGrid, Sparkles, Save, Lock } from 'lucide-vue-next'
import { useSongsStore } from '@/stores/songs'
import { useFormationsStore } from '@/stores/formations'
import { useMembersStore } from '@/stores/members'
import FormationCanvas from '@/components/FormationCanvas.vue'

const songsStore = useSongsStore()
const formationsStore = useFormationsStore()
const membersStore = useMembersStore()

const selectedSongId = ref<number | null>(null)

const sortedSongs = computed(() =>
  [...songsStore.songs].sort((a, b) => a.performance_order - b.performance_order)
)

const currentSong = computed(() =>
  songsStore.songs.find((s) => s.id === selectedSongId.value) || null
)

const currentFormation = computed(() => formationsStore.currentFormation)

function selectSong(id: number) {
  selectedSongId.value = id
  formationsStore.fetchFormation(id)
}

async function handleGenerate() {
  if (!selectedSongId.value || !currentSong.value) return
  try {
    await formationsStore.generateFormation(selectedSongId.value)
  } catch {
    alert('生成队形失败，请重试')
  }
}

async function handleSave() {
  if (!currentFormation.value) return
  try {
    await formationsStore.saveFormation(currentFormation.value.id, currentFormation.value.positions)
  } catch {
    alert('保存失败，请重试')
  }
}

async function handleLock() {
  if (!currentFormation.value) return
  if (!confirm('锁定后不可修改，确认锁定吗？')) return
  try {
    await formationsStore.lockFormation(currentFormation.value.id)
  } catch {
    alert('锁定失败，请重试')
  }
}

function handlePositionMove(positionId: number, x: number, y: number) {
  if (!currentFormation.value) return
  const pos = currentFormation.value.positions.find((p) => p.id === positionId)
  if (pos) {
    pos.x = x
    pos.y = y
  }
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  songsStore.fetchSongs()
  membersStore.fetchMembers()
})
</script>
