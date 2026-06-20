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
              <span class="ml-3">共排练 {{ rehearsalCount }} 次</span>
            </p>
          </div>
          <div class="flex gap-2">
            <button class="btn-secondary flex items-center gap-1.5" @click="showRehearsalPanel = true">
              <FileText :size="16" />
              排练记录
            </button>
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

        <div class="mt-4 grid grid-cols-2 gap-4">
          <div v-if="formationsStore.versions.length" class="bg-white rounded-xl border border-[#E5E7EB] p-4">
            <h3 class="text-base font-semibold text-[#1F2937] mb-3 flex items-center gap-2">
              <History :size="16" class="text-[#E53935]" />
              版本历史
            </h3>
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

          <div class="bg-white rounded-xl border border-[#E5E7EB] p-4">
            <h3 class="text-base font-semibold text-[#1F2937] mb-3 flex items-center gap-2 justify-between">
              <span class="flex items-center gap-2">
                <ClipboardList :size="16" class="text-[#FFB300]" />
                最近排练
              </span>
              <button
                class="text-xs text-[#E53935] font-medium hover:underline"
                @click="openRehearsalModal"
              >
                + 添加记录
              </button>
            </h3>
            <div class="space-y-2 max-h-[140px] overflow-y-auto scrollbar-thin">
              <div
                v-for="r in recentRehearsals"
                :key="r.id"
                class="p-2 rounded-lg bg-[#F9FAFB] text-sm border border-[#E5E7EB]"
              >
                <div class="flex justify-between">
                  <span class="font-medium text-[#1F2937]">{{ r.date }}</span>
                  <span class="text-[#9CA3AF] text-xs">{{ r.duration_minutes }}分钟</span>
                </div>
                <p v-if="r.teacher_notes" class="text-xs text-[#6B7280] mt-1 line-clamp-1">{{ r.teacher_notes }}</p>
              </div>
              <div v-if="!recentRehearsals.length" class="text-center py-4 text-sm text-[#9CA3AF]">
                暂无排练记录
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <Teleport to="body">
      <div v-if="showRehearsalPanel && currentSong" class="modal-overlay" @click.self="showRehearsalPanel = false">
        <div class="modal-content w-[650px] max-h-[85vh] flex flex-col">
          <div class="p-6 border-b border-[#E5E7EB] flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-[#1F2937]">{{ currentSong.name }} - 排练记录</h2>
              <p class="text-sm text-[#6B7280] mt-1">共 {{ rehearsalCount }} 次排练</p>
            </div>
            <button
              class="btn-primary flex items-center gap-1.5 text-sm"
              @click="openRehearsalModal"
            >
              <Plus :size="16" />
              新增记录
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-3 scrollbar-thin">
            <div
              v-for="r in allRehearsals"
              :key="r.id"
              class="p-4 rounded-xl bg-[#F9FAFB] border border-[#E5E7EB] cursor-pointer hover:border-[#E53935] transition-colors"
              @click="viewRehearsalDetail(r.id)"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <Calendar :size="18" class="text-[#E53935]" />
                  <span class="font-semibold text-[#1F2937]">{{ r.date }}</span>
                </div>
                <span class="text-sm text-[#6B7280]">{{ r.duration_minutes }}分钟</span>
              </div>
              <div v-if="r.teacher_notes" class="text-sm text-[#6B7280] mt-2 pl-7 line-clamp-2">
                <span class="font-medium text-[#1F2937]">老师提示：</span>{{ r.teacher_notes }}
              </div>
            </div>
            <div v-if="!allRehearsals.length" class="text-center py-12">
              <FileText :size="40" class="mx-auto text-[#D1D5DB] mb-3" />
              <p class="text-base text-[#6B7280]">暂无排练记录</p>
              <button class="btn-primary mt-4 text-sm" @click="openRehearsalModal">
                添加第一条记录
              </button>
            </div>
          </div>
          <div class="p-4 border-t border-[#E5E7EB] flex justify-end">
            <button class="btn-secondary" @click="showRehearsalPanel = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showRehearsalDetail && rehearsalDetail" class="modal-overlay" @click.self="showRehearsalDetail = false">
        <div class="modal-content w-[600px] max-h-[80vh] flex flex-col">
          <div class="p-6 border-b border-[#E5E7EB]">
            <h2 class="text-xl font-semibold text-[#1F2937]">排练详情</h2>
            <p class="text-sm text-[#6B7280] mt-1">{{ rehearsalDetail.date }} · {{ rehearsalDetail.duration_minutes }}分钟</p>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-5 scrollbar-thin">
            <div>
              <h3 class="text-base font-semibold text-[#1F2937] mb-3 flex items-center gap-2">
                <AlertCircle :size="16" class="text-red-500" />
                错拍片段
              </h3>
              <div class="space-y-2">
                <div
                  v-for="(err, idx) in beatErrors"
                  :key="'b' + idx"
                  class="p-3 rounded-lg bg-red-50 border border-red-100 text-sm"
                >
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-red-700">{{ err.position_id }}</span>
                    <span class="text-red-500">第{{ err.beat_number }}拍</span>
                  </div>
                  <p v-if="err.description" class="text-red-600 mt-1">{{ err.description }}</p>
                </div>
                <p v-if="!beatErrors.length" class="text-sm text-[#9CA3AF]">无错拍记录</p>
              </div>
            </div>
            <div>
              <h3 class="text-base font-semibold text-[#1F2937] mb-3 flex items-center gap-2">
                <MoveHorizontal :size="16" class="text-orange-500" />
                换位失误位置
              </h3>
              <div class="space-y-2">
                <div
                  v-for="(err, idx) in positionErrors"
                  :key="'p' + idx"
                  class="p-3 rounded-lg bg-orange-50 border border-orange-100 text-sm"
                >
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-orange-700">{{ err.position_id }}</span>
                  </div>
                  <p v-if="err.description" class="text-orange-600 mt-1">{{ err.description }}</p>
                </div>
                <p v-if="!positionErrors.length" class="text-sm text-[#9CA3AF]">无换位失误记录</p>
              </div>
            </div>
            <div>
              <h3 class="text-base font-semibold text-[#1F2937] mb-3 flex items-center gap-2">
                <MessageSquare :size="16" class="text-blue-500" />
                老师提示
              </h3>
              <div class="p-4 rounded-lg bg-blue-50 border border-blue-100 text-sm text-blue-700">
                {{ rehearsalDetail.teacher_notes || '暂无提示' }}
              </div>
            </div>
          </div>
          <div class="p-4 border-t border-[#E5E7EB] flex justify-end">
            <button class="btn-secondary" @click="showRehearsalDetail = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <RehearsalFormModal
      v-if="showRehearsalModal && selectedSongId && currentSong"
      :song-id="selectedSongId"
      :song-name="currentSong.name"
      @close="showRehearsalModal = false"
      @saved="onRehearsalSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { LayoutGrid, Sparkles, Save, Lock, FileText, History, ClipboardList, Plus, Calendar, AlertCircle, MoveHorizontal, MessageSquare } from 'lucide-vue-next'
import type { RehearsalDetail } from '@/types'
import { useSongsStore } from '@/stores/songs'
import { useFormationsStore } from '@/stores/formations'
import { useMembersStore } from '@/stores/members'
import { useRehearsalsStore } from '@/stores/rehearsals'
import { useStatisticsStore } from '@/stores/statistics'
import FormationCanvas from '@/components/FormationCanvas.vue'
import RehearsalFormModal from '@/components/RehearsalFormModal.vue'

const songsStore = useSongsStore()
const formationsStore = useFormationsStore()
const membersStore = useMembersStore()
const rehearsalsStore = useRehearsalsStore()
const statisticsStore = useStatisticsStore()

const selectedSongId = ref<number | null>(null)
const showRehearsalModal = ref(false)
const showRehearsalPanel = ref(false)
const showRehearsalDetail = ref(false)
const rehearsalDetail = ref<RehearsalDetail | null>(null)

const sortedSongs = computed(() =>
  [...songsStore.songs].sort((a, b) => a.performance_order - b.performance_order)
)

const currentSong = computed(() =>
  songsStore.songs.find((s) => s.id === selectedSongId.value) || null
)

const currentFormation = computed(() => formationsStore.currentFormation)

const allRehearsals = computed(() =>
  rehearsalsStore.rehearsals
    .filter((r) => r.song_id === selectedSongId.value)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
)

const recentRehearsals = computed(() => allRehearsals.value.slice(0, 5))

const rehearsalCount = computed(() => allRehearsals.value.length)

const beatErrors = computed(() =>
  rehearsalDetail.value?.errors.filter((e) => e.error_type === 'beat_error') || []
)

const positionErrors = computed(() =>
  rehearsalDetail.value?.errors.filter((e) => e.error_type === 'position_error') || []
)

function selectSong(id: number) {
  selectedSongId.value = id
  Promise.all([formationsStore.fetchFormation(id), rehearsalsStore.fetchRehearsals(id)])
}

function openRehearsalModal() {
  showRehearsalModal.value = true
}

async function viewRehearsalDetail(id: number) {
  const detail = await rehearsalsStore.fetchDetail(id)
  if (detail) {
    rehearsalDetail.value = detail
    showRehearsalDetail.value = true
  }
}

function onRehearsalSaved() {
  if (selectedSongId.value) {
    rehearsalsStore.fetchRehearsals(selectedSongId.value)
    statisticsStore.fetchAll()
  }
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
    alert('保存成功')
  } catch {
    alert('保存失败，请重试')
  }
}

async function handleLock() {
  if (!currentFormation.value) return
  if (!confirm('锁定后不可修改，确认锁定吗？')) return
  try {
    await formationsStore.lockFormation(currentFormation.value.id)
    alert('锁定成功')
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

watch(currentFormation, (f) => {
  if (f && selectedSongId.value) {
    if (!formationsStore.versions.find((v) => v.id === f.id)) {
      formationsStore.fetchFormation(selectedSongId.value)
    }
  }
})

onMounted(() => {
  songsStore.fetchSongs()
  membersStore.fetchMembers()
})
</script>
