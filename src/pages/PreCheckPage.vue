<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1F2937]">演前物资核验</h1>
    </div>

    <div v-if="performancesStore.loading" class="text-center py-16 text-[#6B7280] text-lg">加载中...</div>

    <div v-else-if="!performancesStore.performances.length" class="text-center py-16">
      <ClipboardCheck :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无演出任务</p>
    </div>

    <div v-else class="space-y-5">
      <div
        v-for="task in performancesStore.performances"
        :key="task.id"
        class="card"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-[#1F2937]">{{ task.name }}</h3>
              <span class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                {{ task.song_tasks.length }} 首曲目
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm text-[#6B7280]">
              <span class="flex items-center gap-1.5">
                <MapPin :size="14" />
                {{ task.location }}
              </span>
              <span class="flex items-center gap-1.5">
                <Clock :size="14" />
                {{ formatTime(task.start_time) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="!getChecklistSummary(task.id)"
              class="btn-primary text-sm flex items-center gap-1.5"
              @click="openGenerate(task)"
            >
              <Plus :size="16" />
              生成检查清单
            </button>
            <button
              v-else
              class="btn-secondary text-sm flex items-center gap-1.5"
              @click="viewChecklist(task)"
            >
              <Eye :size="16" />
              查看清单
            </button>
          </div>
        </div>

        <div v-if="getChecklistSummary(task.id)" class="border-t border-[#E5E7EB] pt-4">
          <div class="flex items-center gap-4 mb-3">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-gray-400"></div>
              <span class="text-sm text-[#6B7280]">未开始 {{ getChecklistSummary(task.id)!.not_started_count }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-blue-500"></div>
              <span class="text-sm text-[#6B7280]">进行中 {{ getChecklistSummary(task.id)!.in_progress_count }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-red-500"></div>
              <span class="text-sm text-[#6B7280]">异常 {{ getChecklistSummary(task.id)!.abnormal_count }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-green-500"></div>
              <span class="text-sm text-[#6B7280]">已完成 {{ getChecklistSummary(task.id)!.completed_count }}</span>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden flex">
              <div
                class="h-full bg-green-500 transition-all duration-300"
                :style="{ width: getChecklistSummary(task.id)!.completion_rate * 100 + '%' }"
              ></div>
              <div
                class="h-full bg-red-500 transition-all duration-300"
                :style="{ width: (getChecklistSummary(task.id)!.abnormal_count / getChecklistSummary(task.id)!.total_items) * 100 + '%' }"
              ></div>
              <div
                class="h-full bg-blue-500 transition-all duration-300"
                :style="{ width: (getChecklistSummary(task.id)!.in_progress_count / getChecklistSummary(task.id)!.total_items) * 100 + '%' }"
              ></div>
            </div>
            <span class="text-sm font-semibold text-[#1F2937] w-12 text-right">
              {{ (getChecklistSummary(task.id)!.completion_rate * 100).toFixed(0) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showChecklistModal" class="modal-overlay" @click.self="closeChecklistModal">
        <div class="modal-content w-[900px] max-h-[85vh] overflow-hidden flex flex-col p-0">
          <div class="p-6 pb-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              {{ selectedTask?.name }} - 演前检查清单
            </h3>
            <div class="flex items-center gap-3">
              <select
                v-model="filterStatus"
                class="px-3 py-1.5 text-sm border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              >
                <option value="all">全部状态</option>
                <option value="not_started">未开始</option>
                <option value="in_progress">进行中</option>
                <option value="abnormal">异常</option>
                <option value="completed">已完成</option>
              </select>
              <select
                v-model="filterCategory"
                class="px-3 py-1.5 text-sm border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935]"
              >
                <option value="all">全部类别</option>
                <option value="costume">服装</option>
                <option value="prop">道具</option>
                <option value="audio">音响</option>
                <option value="accompaniment">伴奏文件</option>
                <option value="transport">交通集合</option>
                <option value="substitute">替补到位</option>
              </select>
              <button
                class="btn-primary text-sm flex items-center gap-1.5"
                @click="openAddItem"
              >
                <Plus :size="14" />
                新增检查项
              </button>
              <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="closeChecklistModal">
                <X :size="18" />
              </button>
            </div>
          </div>

          <div v-if="checklistsStore.loading" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            加载中...
          </div>

          <div v-else-if="!checklistsStore.currentChecklist" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            暂无检查清单
          </div>

          <div v-else class="flex-1 overflow-y-auto p-6">
            <div
              v-for="group in groupedItems"
              :key="group.song_id"
              class="mb-6"
            >
              <div class="flex items-center gap-2 mb-3">
                <Music class="text-[#E53935]" :size="18" />
                <h4 class="text-base font-semibold text-[#1F2937]">{{ group.song_name }}</h4>
                <span class="text-xs text-[#6B7280]">{{ group.items.length }} 项</span>
              </div>
              <div class="space-y-2">
                <div
                  v-for="item in group.items"
                  :key="item.id"
                  class="flex items-center gap-4 p-3 rounded-lg border border-[#E5E7EB] hover:bg-gray-50 transition-colors"
                >
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <span
                        class="px-2 py-0.5 text-xs rounded-full font-medium"
                        :class="CHECK_STATUS_COLOR_MAP[item.status]"
                      >
                        {{ CHECK_STATUS_MAP[item.status] }}
                      </span>
                      <span
                        class="px-2 py-0.5 text-xs rounded-full bg-purple-100 text-purple-700 font-medium"
                      >
                        {{ CHECK_CATEGORY_MAP[item.category] }}
                      </span>
                      <span class="text-sm font-medium text-[#1F2937]">{{ item.item_name }}</span>
                      <span v-if="item.position_id" class="text-xs text-[#6B7280] bg-gray-100 px-1.5 py-0.5 rounded">
                        站位: {{ item.position_id }}
                      </span>
                    </div>
                    <div class="flex items-center gap-4 text-xs text-[#6B7280]">
                      <span v-if="item.responsible_member_name" class="flex items-center gap-1">
                        <User :size="12" />
                        {{ item.responsible_member_name }}
                      </span>
                      <span v-if="item.deadline" class="flex items-center gap-1">
                        <Clock :size="12" />
                        截止: {{ formatTime(item.deadline) }}
                      </span>
                      <span v-if="item.completed_at" class="flex items-center gap-1 text-green-600">
                        <CheckCircle :size="12" />
                        {{ formatTime(item.completed_at) }}
                      </span>
                    </div>
                    <div v-if="item.abnormal_description" class="mt-1 text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                      异常说明: {{ item.abnormal_description }}
                    </div>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <button
                      v-if="item.status === 'not_started'"
                      class="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                      @click="startItem(item)"
                    >
                      开始
                    </button>
                    <button
                      v-if="item.status === 'in_progress'"
                      class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                      @click="completeItem(item)"
                    >
                      完成
                    </button>
                    <button
                      v-if="item.status === 'in_progress' || item.status === 'not_started'"
                      class="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                      @click="openAbnormal(item)"
                    >
                      标记异常
                    </button>
                    <button
                      v-if="item.status === 'abnormal'"
                      class="px-3 py-1.5 text-xs font-medium text-orange-600 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
                      @click="resolveItem(item)"
                    >
                      已解决
                    </button>
                    <button
                      class="p-1.5 text-[#6B7280] hover:text-[#E53935] hover:bg-[#E53935]/10 rounded transition-colors"
                      @click="openEditItem(item)"
                    >
                      <Pencil :size="14" />
                    </button>
                    <button
                      class="p-1.5 text-[#6B7280] hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                      @click="confirmDeleteItem(item)"
                    >
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="!filteredItems.length" class="text-center py-8 text-[#9CA3AF]">
              暂无匹配的检查项
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showAddItemModal" class="modal-overlay" @click.self="showAddItemModal = false">
        <div class="modal-content w-[520px] p-6">
          <h3 class="text-lg font-semibold text-[#1F2937] mb-4">{{ editingItem ? '编辑检查项' : '新增检查项' }}</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">曲目</label>
              <select v-model="itemForm.song_id" class="input" :disabled="!!editingItem">
                <option v-for="st in selectedTask?.song_tasks" :key="st.song_id" :value="st.song_id">
                  {{ st.song_name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">检查类别</label>
              <select v-model="itemForm.category" class="input" :disabled="!!editingItem">
                <option value="costume">服装</option>
                <option value="prop">道具</option>
                <option value="audio">音响</option>
                <option value="accompaniment">伴奏文件</option>
                <option value="transport">交通集合</option>
                <option value="substitute">替补到位</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">检查项名称</label>
              <input v-model="itemForm.item_name" type="text" class="input" placeholder="如：演出服装到位检查" />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">责任成员</label>
              <select v-model="itemForm.responsible_member_id" class="input">
                <option :value="null">未指定</option>
                <option v-for="m in membersStore.members" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">关联站位</label>
              <input v-model="itemForm.position_id" type="text" class="input" placeholder="如：P1, P2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">截止时间</label>
              <input v-model="itemForm.deadline" type="datetime-local" class="input" />
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button class="btn-secondary flex-1" @click="showAddItemModal = false">取消</button>
            <button class="btn-primary flex-1" @click="saveItem" :disabled="savingItem">
              {{ savingItem ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showAbnormalModal" class="modal-overlay" @click.self="showAbnormalModal = false">
        <div class="modal-content w-[480px] p-6">
          <h3 class="text-lg font-semibold text-[#1F2937] mb-4">标记异常</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">检查项</label>
              <p class="text-sm text-[#6B7280]">{{ abnormalItem?.item_name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">异常说明</label>
              <textarea
                v-model="abnormalDescription"
                class="input min-h-[100px] resize-none"
                placeholder="请描述异常情况"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">现场照片URL</label>
              <input v-model="abnormalPhotoUrl" type="text" class="input" placeholder="照片链接地址（选填）" />
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button class="btn-secondary flex-1" @click="showAbnormalModal = false">取消</button>
            <button class="btn-primary flex-1" @click="submitAbnormal" :disabled="submittingAbnormal">
              {{ submittingAbnormal ? '提交中...' : '确认异常' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="deleteTargetItem" class="modal-overlay" @click.self="deleteTargetItem = null">
        <div class="modal-content p-6">
          <h2 class="text-xl font-semibold text-[#1F2937] mb-3">确认删除</h2>
          <p class="text-base text-[#6B7280] mb-5">
            确定要删除检查项「{{ deleteTargetItem.item_name }}」吗？
          </p>
          <div class="flex gap-3">
            <button class="btn-primary flex-1" @click="doDeleteItem">确认删除</button>
            <button class="btn-secondary flex-1" @click="deleteTargetItem = null">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus, Clock, MapPin, Music, User, CheckCircle,
  Pencil, Trash2, X, Eye, ClipboardCheck,
} from 'lucide-vue-next'
import type { PerformanceTask, CheckItem, CheckItemCategory, CheckItemStatus, ChecklistSummary } from '@/types'
import { CHECK_STATUS_MAP, CHECK_STATUS_COLOR_MAP, CHECK_CATEGORY_MAP } from '@/types'
import { usePerformancesStore } from '@/stores/performances'
import { useChecklistsStore } from '@/stores/checklists'
import { useMembersStore } from '@/stores/members'

const router = useRouter()
const performancesStore = usePerformancesStore()
const checklistsStore = useChecklistsStore()
const membersStore = useMembersStore()

const summaryMap = ref<Record<number, ChecklistSummary>>({})
const showChecklistModal = ref(false)
const selectedTask = ref<PerformanceTask | null>(null)
const filterStatus = ref<string>('all')
const filterCategory = ref<string>('all')

const showAddItemModal = ref(false)
const editingItem = ref<CheckItem | null>(null)
const savingItem = ref(false)
const itemForm = ref({
  song_id: 0,
  category: 'costume' as CheckItemCategory,
  item_name: '',
  responsible_member_id: null as number | null,
  position_id: '',
  deadline: '',
})

const showAbnormalModal = ref(false)
const abnormalItem = ref<CheckItem | null>(null)
const abnormalDescription = ref('')
const abnormalPhotoUrl = ref('')
const submittingAbnormal = ref(false)

const deleteTargetItem = ref<CheckItem | null>(null)

function formatTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hours}:${minutes}`
}

function getChecklistSummary(taskId: number): ChecklistSummary | null {
  return summaryMap.value[taskId] || null
}

const filteredItems = computed(() => {
  const items = checklistsStore.currentChecklist?.items || []
  return items.filter((item) => {
    if (filterStatus.value !== 'all' && item.status !== filterStatus.value) return false
    if (filterCategory.value !== 'all' && item.category !== filterCategory.value) return false
    return true
  })
})

const groupedItems = computed(() => {
  const groups: Record<number, { song_id: number; song_name: string; items: CheckItem[] }> = {}
  for (const item of filteredItems.value) {
    if (!groups[item.song_id]) {
      groups[item.song_id] = { song_id: item.song_id, song_name: item.song_name, items: [] }
    }
    groups[item.song_id].items.push(item)
  }
  return Object.values(groups)
})

async function loadSummaries() {
  try {
    await checklistsStore.fetchAllSummaries()
    const map: Record<number, ChecklistSummary> = {}
    for (const s of checklistsStore.summaries) {
      map[s.performance_id] = s
    }
    summaryMap.value = map
  } catch {
    // ignore
  }
}

async function openGenerate(task: PerformanceTask) {
  try {
    await checklistsStore.generateChecklist(task.id)
    await loadSummaries()
    viewChecklist(task)
  } catch {
    alert('生成检查清单失败，请重试')
  }
}

async function viewChecklist(task: PerformanceTask) {
  selectedTask.value = task
  filterStatus.value = 'all'
  filterCategory.value = 'all'
  showChecklistModal.value = true
  try {
    await checklistsStore.fetchChecklist(task.id)
  } catch {
    // checklist might not exist yet
  }
}

function closeChecklistModal() {
  showChecklistModal.value = false
  selectedTask.value = null
  loadSummaries()
}

function openAddItem() {
  editingItem.value = null
  const firstSong = selectedTask.value?.song_tasks[0]
  itemForm.value = {
    song_id: firstSong?.song_id || 0,
    category: 'costume',
    item_name: '',
    responsible_member_id: null,
    position_id: '',
    deadline: '',
  }
  showAddItemModal.value = true
}

function openEditItem(item: CheckItem) {
  editingItem.value = item
  itemForm.value = {
    song_id: item.song_id,
    category: item.category,
    item_name: item.item_name,
    responsible_member_id: item.responsible_member_id,
    position_id: item.position_id || '',
    deadline: item.deadline ? new Date(item.deadline).toISOString().slice(0, 16) : '',
  }
  showAddItemModal.value = true
}

async function saveItem() {
  if (!selectedTask.value || !itemForm.value.item_name) return
  savingItem.value = true
  try {
    if (editingItem.value) {
      await checklistsStore.deleteItem(editingItem.value.id)
      await checklistsStore.addItem(selectedTask.value.id, {
        song_id: itemForm.value.song_id,
        category: itemForm.value.category,
        item_name: itemForm.value.item_name,
        responsible_member_id: itemForm.value.responsible_member_id || undefined,
        position_id: itemForm.value.position_id || undefined,
        deadline: itemForm.value.deadline || undefined,
      })
    } else {
      await checklistsStore.addItem(selectedTask.value.id, {
        song_id: itemForm.value.song_id,
        category: itemForm.value.category,
        item_name: itemForm.value.item_name,
        responsible_member_id: itemForm.value.responsible_member_id || undefined,
        position_id: itemForm.value.position_id || undefined,
        deadline: itemForm.value.deadline || undefined,
      })
    }
    showAddItemModal.value = false
  } catch {
    alert('保存失败，请重试')
  } finally {
    savingItem.value = false
  }
}

async function startItem(item: CheckItem) {
  try {
    await checklistsStore.updateItem(item.id, { status: 'in_progress' })
  } catch {
    alert('操作失败')
  }
}

async function completeItem(item: CheckItem) {
  try {
    await checklistsStore.updateItem(item.id, { status: 'completed' })
  } catch {
    alert('操作失败')
  }
}

async function resolveItem(item: CheckItem) {
  try {
    await checklistsStore.updateItem(item.id, { status: 'completed', abnormal_description: '' })
  } catch {
    alert('操作失败')
  }
}

function openAbnormal(item: CheckItem) {
  abnormalItem.value = item
  abnormalDescription.value = ''
  abnormalPhotoUrl.value = ''
  showAbnormalModal.value = true
}

async function submitAbnormal() {
  if (!abnormalItem.value) return
  submittingAbnormal.value = true
  try {
    await checklistsStore.updateItem(abnormalItem.value.id, {
      status: 'abnormal',
      abnormal_description: abnormalDescription.value || undefined,
      photo_url: abnormalPhotoUrl.value || undefined,
    })
    showAbnormalModal.value = false
  } catch {
    alert('提交失败')
  } finally {
    submittingAbnormal.value = false
  }
}

function confirmDeleteItem(item: CheckItem) {
  deleteTargetItem.value = item
}

async function doDeleteItem() {
  if (!deleteTargetItem.value) return
  try {
    await checklistsStore.deleteItem(deleteTargetItem.value.id)
    deleteTargetItem.value = null
  } catch {
    alert('删除失败')
  }
}

onMounted(async () => {
  await Promise.all([
    performancesStore.fetchList(),
    membersStore.fetchMembers(),
    loadSummaries(),
  ])
})
</script>
