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
        @edit="openEdit"
        @delete="confirmDelete"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Music } from 'lucide-vue-next'
import type { Song } from '@/types'
import { useSongsStore } from '@/stores/songs'
import SongCard from '@/components/SongCard.vue'
import SongFormModal from '@/components/SongFormModal.vue'

const songsStore = useSongsStore()

const showModal = ref(false)
const editingSong = ref<Song | null>(null)
const deleteTarget = ref<Song | null>(null)

const sortedSongs = computed(() =>
  [...songsStore.songs].sort((a, b) => a.performance_order - b.performance_order)
)

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

onMounted(() => {
  songsStore.fetchSongs()
})
</script>
