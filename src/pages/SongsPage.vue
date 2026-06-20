<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1F2937]">曲目档案</h1>
      <button class="btn-primary flex items-center gap-2" @click="showModal = true">
        <Plus :size="18" />
        新增曲目
      </button>
    </div>

    <div v-if="songsStore.loading" class="text-center py-12 text-[#6B7280] text-lg">加载中...</div>

    <div v-else-if="!songsStore.songs.length" class="text-center py-16">
      <Music :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无曲目，点击新增按钮添加</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <SongCard
        v-for="song in sortedSongs"
        :key="song.id"
        :song="song"
        :rehearsal-count="getRehearsalCount(song.id)"
        @edit="openEdit"
        @delete="confirmDelete"
        @view-rehearsals="openRehearsalPanel"
      />
    </div>

    <SongFormModal
      v-if="showModal"
      :song="editingSong"
      @close="closeModal"
      @saved="onSaved"
    />

    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
        <div class="modal-content p-6">
          <h2 class="text-xl font-semibold text-[#1F2937] mb-3">确认删除</h2>
          <p class="text-base text-[#6B7280] mb-5">确定要删除曲目「{{ deleteTarget.name }}」吗？此操作不可撤销。</p>
          <div class="flex gap-3">
            <button class="btn-primary flex-1" @click="doDelete">确认删除</button>
            <button class="btn-secondary flex-1" @click="deleteTarget = null">取消</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showRehearsalPanel && currentRehearsalSong" class="modal-overlay" @click.self="closeRehearsalPanel">
        <div class="modal-content w-[600px] max-h-[80vh] flex flex-col">
          <div class="p-6 border-b border-[#E5E7EB] flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-[#1F2937]">{{ currentRehearsalSong.name }} - 排练记录</h2>
              <p class="text-sm text-[#6B7280] mt-1">共 {{ getRehearsalCount(currentRehearsalSong.id) }} 次排练</p>
            </div>
            <button
              class="btn-primary flex items-center gap-1.5 text-sm"
              @click="openAddRehearsal"
            >
              <Plus :size="16" />
              新增记录
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-3 scrollbar-thin">
            <div
              v-for="r in songRehearsals"
              :key="r.id"
              class="p-4 rounded-xl bg-[#F9FAFB] border border-[#E5E7EB]"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <Calendar :size="18" class="text-[#E53935]" />
                  <span class="font-semibold text-[#1F2937]">{{ r.date }}</span>
                </div>
                <span class="text-sm text-[#6B7280]">{{ r.duration_minutes }}分钟</span>
              </div>
              <div v-if="r.teacher_notes" class="text-sm text-[#6B7280] mt-2 pl-7">
                <span class="font-medium text-[#1F2937]">老师提示：</span>{{ r.teacher_notes }}
              </div>
            </div>
            <div v-if="!songRehearsals.length" class="text-center py-12">
              <FileText :size="40" class="mx-auto text-[#D1D5DB] mb-3" />
              <p class="text-base text-[#6B7280]">暂无排练记录</p>
              <button class="btn-primary mt-4 text-sm" @click="openAddRehearsal">
                添加第一条记录
              </button>
            </div>
          </div>
          <div class="p-4 border-t border-[#E5E7EB] flex justify-end">
            <button class="btn-secondary" @click="closeRehearsalPanel">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <RehearsalFormModal
      v-if="showRehearsalModal && currentRehearsalSong"
      :song-id="currentRehearsalSong.id"
      :song-name="currentRehearsalSong.name"
      @close="showRehearsalModal = false"
      @saved="onRehearsalSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Music, Calendar, FileText } from 'lucide-vue-next'
import type { Song } from '@/types'
import { useSongsStore } from '@/stores/songs'
import { useRehearsalsStore } from '@/stores/rehearsals'
import { useFormationsStore } from '@/stores/formations'
import { useStatisticsStore } from '@/stores/statistics'
import SongCard from '@/components/SongCard.vue'
import SongFormModal from '@/components/SongFormModal.vue'
import RehearsalFormModal from '@/components/RehearsalFormModal.vue'

const songsStore = useSongsStore()
const rehearsalsStore = useRehearsalsStore()
const formationsStore = useFormationsStore()
const statisticsStore = useStatisticsStore()

const showModal = ref(false)
const editingSong = ref<Song | null>(null)
const deleteTarget = ref<Song | null>(null)
const showRehearsalPanel = ref(false)
const showRehearsalModal = ref(false)
const currentRehearsalSong = ref<Song | null>(null)

const sortedSongs = computed(() =>
  [...songsStore.songs].sort((a, b) => a.performance_order - b.performance_order)
)

const songRehearsals = computed(() => {
  if (!currentRehearsalSong.value) return []
  return rehearsalsStore.rehearsals
    .filter((r) => r.song_id === currentRehearsalSong.value!.id)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

function getRehearsalCount(songId: number) {
  return rehearsalsStore.rehearsals.filter((r) => r.song_id === songId).length
}

function openEdit(song: Song) {
  editingSong.value = song
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingSong.value = null
}

function onSaved() {
  songsStore.fetchSongs()
}

function confirmDelete(song: Song) {
  deleteTarget.value = song
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await songsStore.deleteSong(deleteTarget.value.id)
    deleteTarget.value = null
  } catch {
    alert('删除失败，请重试')
  }
}

async function openRehearsalPanel(song: Song) {
  currentRehearsalSong.value = song
  showRehearsalPanel.value = true
  await Promise.all([
    rehearsalsStore.fetchRehearsals(song.id),
    formationsStore.fetchFormation(song.id),
  ])
}

function closeRehearsalPanel() {
  showRehearsalPanel.value = false
  currentRehearsalSong.value = null
}

function openAddRehearsal() {
  showRehearsalModal.value = true
}

function onRehearsalSaved() {
  if (currentRehearsalSong.value) {
    rehearsalsStore.fetchRehearsals(currentRehearsalSong.value.id)
    statisticsStore.fetchAll()
  }
}

onMounted(async () => {
  await Promise.all([
    songsStore.fetchSongs(),
    rehearsalsStore.fetchRehearsals(),
  ])
})
</script>
