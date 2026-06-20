<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1F2937]">演出任务</h1>
      <button class="btn-primary flex items-center gap-2" @click="openCreate">
        <Plus :size="18" />
        新建演出任务
      </button>
    </div>

    <div v-if="performancesStore.loading" class="text-center py-16 text-[#6B7280] text-lg">
      加载中...
    </div>

    <div v-else-if="!performancesStore.performances.length" class="text-center py-16">
      <CalendarCheck :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无演出任务</p>
      <button class="btn-primary mt-4" @click="openCreate">创建第一个演出任务</button>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="task in performancesStore.performances"
        :key="task.id"
        class="card cursor-pointer hover:shadow-md transition-shadow"
        @click="goToDetail(task.id)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-[#1F2937]">{{ task.name }}</h3>
              <span class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                {{ task.song_tasks.length }} 首曲目
              </span>
            </div>

            <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 text-sm mb-3">
              <div class="flex items-center gap-1.5 text-[#6B7280]">
                <MapPin :size="14" />
                <span>{{ task.location }}</span>
              </div>
              <div class="flex items-center gap-1.5 text-[#6B7280]">
                <Clock :size="14" />
                <span>集合: {{ formatTime(task.meeting_time) }}</span>
              </div>
              <div class="flex items-center gap-1.5 text-[#6B7280]">
                <PlayCircle :size="14" />
                <span>开演: {{ formatTime(task.start_time) }}</span>
              </div>
              <div class="flex items-center gap-1.5 text-[#6B7280]">
                <Users :size="14" />
                <span>{{ task.total_members }} 人参演</span>
              </div>
            </div>

            <div class="flex items-center gap-4">
              <div class="flex items-center gap-1.5">
                <div class="w-2.5 h-2.5 rounded-full bg-green-500"></div>
                <span class="text-sm text-[#6B7280]">已确认 {{ task.confirmed_count }}</span>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="w-2.5 h-2.5 rounded-full bg-yellow-500"></div>
                <span class="text-sm text-[#6B7280]">未确认 {{ task.unconfirmed_count }}</span>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="w-2.5 h-2.5 rounded-full bg-red-500"></div>
                <span class="text-sm text-[#6B7280]">请假 {{ task.leave_count }}</span>
              </div>
              <div class="flex-1">
                <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-green-500 rounded-full transition-all duration-300"
                    :style="{ width: getConfirmedRate(task) * 100 + '%' }"
                  ></div>
                </div>
              </div>
              <span class="text-sm font-medium text-[#1F2937]">
                {{ (getConfirmedRate(task) * 100).toFixed(0) }}%
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2 ml-4" @click.stop>
            <button
              class="p-2 text-[#6B7280] hover:text-[#E53935] hover:bg-[#E53935]/10 rounded-lg transition-colors"
              @click="openEdit(task)"
              title="编辑"
            >
              <Pencil :size="16" />
            </button>
            <button
              class="p-2 text-[#6B7280] hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              @click="confirmDelete(task)"
              title="删除"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>

        <div class="mt-3 pt-3 border-t border-[#E5E7EB] flex flex-wrap gap-2">
          <span
            v-for="song in task.song_tasks"
            :key="song.id"
            class="px-2 py-1 text-xs rounded bg-gray-100 text-[#6B7280]"
          >
            {{ song.song_name }}
          </span>
        </div>
      </div>
    </div>

    <PerformanceFormModal
      v-if="showModal"
      :editing-task="editingTask"
      @close="closeModal"
      @saved="onSaved"
    />

    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
        <div class="modal-content p-6">
          <h2 class="text-xl font-semibold text-[#1F2937] mb-3">确认删除</h2>
          <p class="text-base text-[#6B7280] mb-5">
            确定要删除演出任务「{{ deleteTarget.name }}」吗？此操作不可恢复。
          </p>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, CalendarCheck, MapPin, Clock, PlayCircle, Users, Pencil, Trash2 } from 'lucide-vue-next'
import type { PerformanceTask } from '@/types'
import { usePerformancesStore } from '@/stores/performances'
import PerformanceFormModal from '@/components/PerformanceFormModal.vue'

const router = useRouter()
const performancesStore = usePerformancesStore()

const showModal = ref(false)
const editingTask = ref<PerformanceTask | null>(null)
const deleteTarget = ref<PerformanceTask | null>(null)

function formatTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hours}:${minutes}`
}

function getConfirmedRate(task: PerformanceTask): number {
  if (task.total_members === 0) return 0
  return task.confirmed_count / task.total_members
}

function openCreate() {
  editingTask.value = null
  showModal.value = true
}

function openEdit(task: PerformanceTask) {
  editingTask.value = task
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingTask.value = null
}

function onSaved() {
  closeModal()
  performancesStore.fetchList()
}

function confirmDelete(task: PerformanceTask) {
  deleteTarget.value = task
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await performancesStore.remove(deleteTarget.value.id)
    deleteTarget.value = null
  } catch {
    alert('删除失败，请重试')
  }
}

function goToDetail(id: number) {
  router.push(`/performances/${id}`)
}

onMounted(() => {
  performancesStore.fetchList()
})
</script>
