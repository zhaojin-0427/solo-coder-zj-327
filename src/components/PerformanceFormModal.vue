<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-content w-[680px] max-h-[85vh] flex flex-col p-0 overflow-hidden">
        <div class="px-6 py-4 border-b border-[#E5E7EB] flex items-center justify-between">
          <h2 class="text-xl font-semibold text-[#1F2937]">
            {{ editingTask ? '编辑演出任务' : '新建演出任务' }}
          </h2>
          <button class="text-[#9CA3AF] hover:text-[#6B7280]" @click="$emit('close')">
            <X :size="20" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-5">
          <div>
            <label class="block text-sm font-medium text-[#1F2937] mb-1.5">演出名称 <span class="text-red-500">*</span></label>
            <input
              v-model="form.name"
              type="text"
              class="input"
              placeholder="请输入演出名称"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[#1F2937] mb-1.5">演出地点 <span class="text-red-500">*</span></label>
            <input
              v-model="form.location"
              type="text"
              class="input"
              placeholder="请输入演出地点"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">集合时间 <span class="text-red-500">*</span></label>
              <input
                v-model="form.meeting_time"
                type="datetime-local"
                class="input"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">正式开始时间 <span class="text-red-500">*</span></label>
              <input
                v-model="form.start_time"
                type="datetime-local"
                class="input"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-[#1F2937] mb-1.5">关联曲目 <span class="text-red-500">*</span></label>
            <div class="border border-[#E5E7EB] rounded-lg p-3 max-h-40 overflow-y-auto space-y-2">
              <label
                v-for="song in songsStore.songs"
                :key="song.id"
                class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 px-2 py-1 rounded"
              >
                <input
                  type="checkbox"
                  :checked="selectedSongIds.has(song.id)"
                  @change="toggleSong(song.id)"
                  class="w-4 h-4 text-[#E53935] rounded"
                />
                <span class="text-sm text-[#1F2937]">{{ song.name }}</span>
              </label>
              <div v-if="!songsStore.songs.length" class="text-center text-sm text-[#9CA3AF] py-4">
                暂无曲目
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-[#1F2937] mb-1.5">参演人员 <span class="text-red-500">*</span></label>
            <div class="border border-[#E5E7EB] rounded-lg p-3 max-h-48 overflow-y-auto space-y-2">
              <label
                v-for="member in membersStore.members"
                :key="member.id"
                class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 px-2 py-1 rounded"
              >
                <input
                  type="checkbox"
                  :checked="selectedMemberIds.has(member.id)"
                  @change="toggleMember(member.id)"
                  class="w-4 h-4 text-[#E53935] rounded"
                />
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-semibold"
                  :class="getHeightColor(member.height_range)"
                >
                  {{ member.name.charAt(0) }}
                </div>
                <span class="text-sm text-[#1F2937]">{{ member.name }}</span>
                <span class="text-xs text-[#9CA3AF]">{{ member.phone || '暂无电话' }}</span>
              </label>
              <div v-if="!membersStore.members.length" class="text-center text-sm text-[#9CA3AF] py-4">
                暂无成员
              </div>
            </div>
            <div class="flex gap-3 mt-2">
              <button type="button" class="text-xs text-[#E53935] hover:underline" @click="selectAllMembers">
                全选
              </button>
              <button type="button" class="text-xs text-[#6B7280] hover:underline" @click="clearAllMembers">
                清空
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-[#1F2937] mb-1.5">服装/道具要求</label>
            <textarea
              v-model="form.costume_requirements"
              class="input min-h-[80px] resize-none"
              placeholder="请输入服装和道具要求"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-[#1F2937] mb-1.5">注意事项</label>
            <textarea
              v-model="form.notes"
              class="input min-h-[80px] resize-none"
              placeholder="请输入注意事项"
            ></textarea>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-[#E5E7EB] flex gap-3 justify-end">
          <button class="btn-secondary" @click="$emit('close')">取消</button>
          <button class="btn-primary" @click="handleSubmit" :disabled="submitting">
            {{ submitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { X } from 'lucide-vue-next'
import type { PerformanceTask, HeightRange } from '@/types'
import { useSongsStore } from '@/stores/songs'
import { useMembersStore } from '@/stores/members'
import { usePerformancesStore } from '@/stores/performances'

const props = defineProps<{
  editingTask?: PerformanceTask | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const songsStore = useSongsStore()
const membersStore = useMembersStore()
const performancesStore = usePerformancesStore()

const submitting = ref(false)
const selectedSongIds = ref<Set<number>>(new Set())
const selectedMemberIds = ref<Set<number>>(new Set())

const form = ref({
  name: '',
  location: '',
  meeting_time: '',
  start_time: '',
  costume_requirements: '',
  notes: '',
})

const heightColorMap: Record<HeightRange, string> = {
  short: 'bg-green-500',
  medium: 'bg-blue-500',
  tall: 'bg-orange-500',
}

function getHeightColor(range: HeightRange) {
  return heightColorMap[range]
}

function toggleSong(songId: number) {
  const set = new Set(selectedSongIds.value)
  if (set.has(songId)) {
    set.delete(songId)
  } else {
    set.add(songId)
  }
  selectedSongIds.value = set
}

function toggleMember(memberId: number) {
  const set = new Set(selectedMemberIds.value)
  if (set.has(memberId)) {
    set.delete(memberId)
  } else {
    set.add(memberId)
  }
  selectedMemberIds.value = set
}

function selectAllMembers() {
  selectedMemberIds.value = new Set(membersStore.members.map((m) => m.id))
}

function clearAllMembers() {
  selectedMemberIds.value = new Set()
}

function formatDateTimeLocal(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

function formatSubmitDateTime(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toISOString()
}

watch(
  () => props.editingTask,
  (task) => {
    if (task) {
      form.value = {
        name: task.name,
        location: task.location,
        meeting_time: formatDateTimeLocal(task.meeting_time),
        start_time: formatDateTimeLocal(task.start_time),
        costume_requirements: task.costume_requirements || '',
        notes: task.notes || '',
      }
      selectedSongIds.value = new Set(task.song_tasks.map((st) => st.song_id))
      if (task.total_members > 0 && 'confirmations' in task) {
        selectedMemberIds.value = new Set(
          (task as any).confirmations.map((c: any) => c.member_id)
        )
      }
    } else {
      form.value = {
        name: '',
        location: '',
        meeting_time: '',
        start_time: '',
        costume_requirements: '',
        notes: '',
      }
      selectedSongIds.value = new Set()
      selectedMemberIds.value = new Set()
    }
  },
  { immediate: true }
)

async function handleSubmit() {
  if (!form.value.name.trim()) {
    alert('请输入演出名称')
    return
  }
  if (!form.value.location.trim()) {
    alert('请输入演出地点')
    return
  }
  if (!form.value.meeting_time) {
    alert('请选择集合时间')
    return
  }
  if (!form.value.start_time) {
    alert('请选择正式开始时间')
    return
  }
  if (selectedSongIds.value.size === 0) {
    alert('请至少选择一首曲目')
    return
  }
  if (selectedMemberIds.value.size === 0) {
    alert('请至少选择一名参演人员')
    return
  }

  submitting.value = true
  try {
    const song_tasks = Array.from(selectedSongIds.value).map((songId, idx) => ({
      song_id: songId,
      performance_order: idx + 1,
    }))

    const data = {
      name: form.value.name,
      location: form.value.location,
      meeting_time: formatSubmitDateTime(form.value.meeting_time),
      start_time: formatSubmitDateTime(form.value.start_time),
      costume_requirements: form.value.costume_requirements || null,
      notes: form.value.notes || null,
      song_tasks,
      member_ids: Array.from(selectedMemberIds.value),
    }

    if (props.editingTask) {
      await performancesStore.update(props.editingTask.id, data)
    } else {
      await performancesStore.create(data)
    }
    emit('saved')
  } catch (e) {
    console.error('Failed to save performance task', e)
    alert('保存失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([songsStore.fetchSongs(), membersStore.fetchMembers()])
})
</script>
