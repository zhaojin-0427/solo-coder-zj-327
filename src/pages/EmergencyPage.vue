<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1F2937]">突发事件登记</h1>
      <button class="btn-primary flex items-center gap-2" @click="openAddModal">
        <Plus :size="18" />
        快速登记
      </button>
    </div>

    <div class="card mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <div class="flex items-center gap-2">
          <span class="text-sm text-[#6B7280]">检查单：</span>
          <select v-model="filterChecklistId" class="input w-48">
            <option :value="null">全部检查单</option>
            <option v-for="c in safetyStore.checklists" :key="c.id" :value="c.id">
              {{ c.song_name }} - {{ formatDate(c.rehearsal_date) }}
            </option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-[#6B7280]">成员：</span>
          <select v-model="filterMemberId" class="input w-40">
            <option :value="null">全部成员</option>
            <option v-for="m in membersStore.members" :key="m.id" :value="m.id">
              {{ m.name }}
            </option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm text-[#6B7280]">状态：</span>
          <select v-model="filterStatus" class="input w-36">
            <option value="all">全部状态</option>
            <option value="active">处理中</option>
            <option value="resolved">已解决</option>
          </select>
        </div>
        <button class="btn-secondary text-sm" @click="resetFilters">
          <RotateCcw :size="14" class="inline mr-1" />
          重置筛选
        </button>
      </div>
    </div>

    <div v-if="safetyStore.loading" class="text-center py-16 text-[#6B7280] text-lg">加载中...</div>

    <div v-else-if="!filteredIncidents.length" class="text-center py-16">
      <AlertCircle :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无突发事件记录</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="incident in filteredIncidents"
        :key="incident.id"
        class="card hover:shadow-md transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 mb-2">
              <span
                class="px-2.5 py-0.5 text-xs rounded-full font-medium"
                :class="INCIDENT_SEVERITY_COLOR_MAP[incident.severity]"
              >
                {{ INCIDENT_SEVERITY_MAP[incident.severity] }}
              </span>
              <span
                class="px-2.5 py-0.5 text-xs rounded-full font-medium"
                :class="incident.resolved ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'"
              >
                {{ incident.resolved ? '已解决' : '处理中' }}
              </span>
              <span class="text-sm font-medium text-[#1F2937]">
                {{ INCIDENT_TYPE_MAP[incident.incident_type] }}
              </span>
            </div>
            <div class="flex flex-wrap items-center gap-4 text-sm text-[#6B7280] mb-3">
              <span class="flex items-center gap-1.5">
                <User :size="14" />
                {{ incident.member_name }}
              </span>
              <span v-if="incident.song_name" class="flex items-center gap-1.5">
                <Music :size="14" />
                {{ incident.song_name }}
              </span>
              <span v-if="incident.formation_position" class="flex items-center gap-1.5">
                <MapPin :size="14" />
                站位: {{ incident.formation_position }}
              </span>
              <span class="flex items-center gap-1.5">
                <Clock :size="14" />
                {{ formatDateTime(incident.incident_time) }}
              </span>
            </div>
            <p v-if="incident.description" class="text-sm text-[#4B5563] mb-3 line-clamp-2">
              {{ incident.description }}
            </p>
            <div class="flex flex-wrap items-center gap-4 text-xs text-[#6B7280]">
              <span v-if="incident.treated_by" class="flex items-center gap-1">
                <Stethoscope :size="12" />
                处理人: {{ incident.treated_by }}
              </span>
              <span v-if="incident.family_notified" class="flex items-center gap-1 text-green-600">
                <Phone :size="12" />
                已通知家属
              </span>
              <span v-if="incident.community_leader_notified" class="flex items-center gap-1 text-blue-600">
                <Users :size="12" />
                已通知社区负责人
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-4 shrink-0">
            <button
              class="px-3 py-1.5 text-xs font-medium text-[#6B7280] bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              @click="viewDetail(incident)"
            >
              查看详情
            </button>
            <button
              v-if="!incident.resolved"
              class="px-3 py-1.5 text-xs font-medium text-green-600 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
              @click="confirmResolve(incident)"
            >
              标记解决
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-content w-[640px] max-h-[85vh] flex flex-col p-0 overflow-hidden">
          <div class="px-6 py-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              {{ editingIncident ? '编辑突发事件' : '快速登记突发事件' }}
            </h3>
            <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="showAddModal = false">
              <X :size="18" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-6">
            <div class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-1.5">事件类型 <span class="text-red-500">*</span></label>
                  <select v-model="incidentForm.incident_type" class="input">
                    <option v-for="(label, value) in INCIDENT_TYPE_MAP" :key="value" :value="value">
                      {{ label }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-1.5">严重程度 <span class="text-red-500">*</span></label>
                  <select v-model="incidentForm.severity" class="input">
                    <option v-for="(label, value) in INCIDENT_SEVERITY_MAP" :key="value" :value="value">
                      {{ label }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-1.5">关联成员 <span class="text-red-500">*</span></label>
                  <select v-model="incidentForm.member_id" class="input">
                    <option :value="null">请选择成员</option>
                    <option v-for="m in membersStore.members" :key="m.id" :value="m.id">
                      {{ m.name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-1.5">关联检查单 <span class="text-red-500">*</span></label>
                  <select v-model="incidentForm.checklist_id" class="input">
                    <option :value="null">请选择检查单</option>
                    <option v-for="c in safetyStore.checklists" :key="c.id" :value="c.id">
                      {{ c.song_name }} - {{ formatDate(c.rehearsal_date) }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-1.5">关联曲目</label>
                  <select v-model="incidentForm.song_id" class="input">
                    <option :value="null">未关联</option>
                    <option v-for="s in songsStore.songs" :key="s.id" :value="s.id">
                      {{ s.name }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-[#1F2937] mb-1.5">队形位置</label>
                  <input v-model="incidentForm.formation_position" type="text" class="input" placeholder="如：P1, 前排中间" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-[#1F2937] mb-1.5">事件描述</label>
                <textarea
                  v-model="incidentForm.description"
                  class="input min-h-[80px] resize-none"
                  placeholder="请详细描述事件发生情况"
                ></textarea>
              </div>
              <div class="border-t border-[#E5E7EB] pt-4">
                <h4 class="text-sm font-semibold text-[#1F2937] mb-3">处理记录</h4>
                <div class="space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-[#1F2937] mb-1.5">处理方式</label>
                      <textarea
                        v-model="incidentForm.treatment_given"
                        class="input min-h-[60px] resize-none"
                        placeholder="如：冰敷、休息、送医等"
                      ></textarea>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-[#1F2937] mb-1.5">处理人</label>
                      <input v-model="incidentForm.treated_by" type="text" class="input" placeholder="处理人姓名" />
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input
                          v-model="incidentForm.family_notified"
                          type="checkbox"
                          class="w-4 h-4 text-[#E53935] rounded"
                        />
                        <span class="text-sm text-[#1F2937]">已通知家属</span>
                      </label>
                      <input
                        v-if="incidentForm.family_notified"
                        v-model="incidentForm.family_notification_details"
                        type="text"
                        class="input mt-2"
                        placeholder="通知详情（选填）"
                      />
                    </div>
                    <div>
                      <label class="flex items-center gap-2 cursor-pointer">
                        <input
                          v-model="incidentForm.community_leader_notified"
                          type="checkbox"
                          class="w-4 h-4 text-[#E53935] rounded"
                        />
                        <span class="text-sm text-[#1F2937]">已通知社区负责人</span>
                      </label>
                      <input
                        v-if="incidentForm.community_leader_notified"
                        v-model="incidentForm.community_notification_details"
                        type="text"
                        class="input mt-2"
                        placeholder="通知详情（选填）"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-[#E5E7EB] flex gap-3 justify-end">
            <button class="btn-secondary" @click="showAddModal = false">取消</button>
            <button class="btn-primary" @click="saveIncident" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDetailModal" class="modal-overlay" @click.self="showDetailModal = false">
        <div class="modal-content w-[600px] max-h-[85vh] flex flex-col p-0 overflow-hidden">
          <div class="px-6 py-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">事件详情</h3>
            <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="showDetailModal = false">
              <X :size="18" />
            </button>
          </div>
          <div v-if="selectedIncident" class="flex-1 overflow-y-auto p-6">
            <div class="space-y-5">
              <div class="flex items-center gap-3">
                <span
                  class="px-2.5 py-0.5 text-xs rounded-full font-medium"
                  :class="INCIDENT_SEVERITY_COLOR_MAP[selectedIncident.severity]"
                >
                  {{ INCIDENT_SEVERITY_MAP[selectedIncident.severity] }}
                </span>
                <span
                  class="px-2.5 py-0.5 text-xs rounded-full font-medium"
                  :class="selectedIncident.resolved ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'"
                >
                  {{ selectedIncident.resolved ? '已解决' : '处理中' }}
                </span>
                <span class="text-base font-semibold text-[#1F2937]">
                  {{ INCIDENT_TYPE_MAP[selectedIncident.incident_type] }}
                </span>
              </div>

              <div class="bg-[#F9FAFB] rounded-xl p-4">
                <h4 class="text-sm font-semibold text-[#1F2937] mb-3 flex items-center gap-2">
                  <User :size="16" class="text-[#E53935]" />
                  成员信息
                </h4>
                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span class="text-[#6B7280]">姓名：</span>
                    <span class="text-[#1F2937] font-medium">{{ selectedIncident.member_name }}</span>
                  </div>
                  <div>
                    <span class="text-[#6B7280]">联系电话：</span>
                    <span class="text-[#1F2937]">{{ selectedIncident.member_phone || '暂无' }}</span>
                  </div>
                  <div>
                    <span class="text-[#6B7280]">紧急联系人：</span>
                    <span class="text-[#1F2937]">{{ selectedIncident.emergency_contact || '暂无' }}</span>
                  </div>
                  <div>
                    <span class="text-[#6B7280]">事件时间：</span>
                    <span class="text-[#1F2937]">{{ formatDateTime(selectedIncident.incident_time) }}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 class="text-sm font-semibold text-[#1F2937] mb-2">事件描述</h4>
                <p class="text-sm text-[#4B5563] bg-white border border-[#E5E7EB] rounded-lg p-3">
                  {{ selectedIncident.description || '暂无描述' }}
                </p>
              </div>

              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-[#6B7280]">关联曲目：</span>
                  <span class="text-[#1F2937]">{{ selectedIncident.song_name || '未关联' }}</span>
                </div>
                <div>
                  <span class="text-[#6B7280]">队形位置：</span>
                  <span class="text-[#1F2937]">{{ selectedIncident.formation_position || '未记录' }}</span>
                </div>
              </div>

              <div class="bg-[#F0FDF4] rounded-xl p-4">
                <h4 class="text-sm font-semibold text-[#1F2937] mb-3 flex items-center gap-2">
                  <Stethoscope :size="16" class="text-green-600" />
                  处理记录
                </h4>
                <div class="space-y-3 text-sm">
                  <div>
                    <span class="text-[#6B7280]">处理方式：</span>
                    <span class="text-[#1F2937]">{{ selectedIncident.treatment_given || '暂无' }}</span>
                  </div>
                  <div>
                    <span class="text-[#6B7280]">处理人：</span>
                    <span class="text-[#1F2937]">{{ selectedIncident.treated_by || '暂无' }}</span>
                  </div>
                  <div class="flex flex-wrap gap-4">
                    <span
                      class="inline-flex items-center gap-1.5"
                      :class="selectedIncident.family_notified ? 'text-green-600' : 'text-[#9CA3AF]'"
                    >
                      <CheckCircle v-if="selectedIncident.family_notified" :size="14" />
                      <XCircle v-else :size="14" />
                      家属{{ selectedIncident.family_notified ? '已' : '未' }}通知
                    </span>
                    <span
                      class="inline-flex items-center gap-1.5"
                      :class="selectedIncident.community_leader_notified ? 'text-blue-600' : 'text-[#9CA3AF]'"
                    >
                      <CheckCircle v-if="selectedIncident.community_leader_notified" :size="14" />
                      <XCircle v-else :size="14" />
                      社区负责人{{ selectedIncident.community_leader_notified ? '已' : '未' }}通知
                    </span>
                  </div>
                  <div v-if="selectedIncident.family_notification_details" class="text-xs text-[#6B7280]">
                    家属通知详情：{{ selectedIncident.family_notification_details }}
                  </div>
                  <div v-if="selectedIncident.community_notification_details" class="text-xs text-[#6B7280]">
                    社区通知详情：{{ selectedIncident.community_notification_details }}
                  </div>
                </div>
              </div>

              <div v-if="selectedIncident.resolved" class="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle :size="16" />
                <span>已于 {{ formatDateTime(selectedIncident.resolved_time) }} 解决</span>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-[#E5E7EB] flex gap-3 justify-end">
            <button
              v-if="selectedIncident && !selectedIncident.resolved"
              class="btn-primary flex-1"
              @click="confirmResolve(selectedIncident)"
            >
              标记已解决
            </button>
            <button class="btn-secondary flex-1" @click="showDetailModal = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="resolveTarget" class="modal-overlay" @click.self="resolveTarget = null">
        <div class="modal-content p-6">
          <h2 class="text-xl font-semibold text-[#1F2937] mb-3">确认解决</h2>
          <p class="text-base text-[#6B7280] mb-5">
            确定要将「{{ INCIDENT_TYPE_MAP[resolveTarget.incident_type] }} - {{ resolveTarget.member_name }}」标记为已解决吗？
          </p>
          <div class="flex gap-3">
            <button class="btn-primary flex-1" @click="doResolve">确认解决</button>
            <button class="btn-secondary flex-1" @click="resolveTarget = null">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Plus, X, User, Music, MapPin, Clock, AlertCircle,
  Stethoscope, Phone, Users, CheckCircle, XCircle,
  RotateCcw,
} from 'lucide-vue-next'
import type { EmergencyIncident, IncidentType, IncidentSeverity } from '@/types'
import {
  INCIDENT_TYPE_MAP,
  INCIDENT_SEVERITY_MAP,
  INCIDENT_SEVERITY_COLOR_MAP,
} from '@/types'
import { useSafetyStore } from '@/stores/safety'
import { useMembersStore } from '@/stores/members'
import { useSongsStore } from '@/stores/songs'

const safetyStore = useSafetyStore()
const membersStore = useMembersStore()
const songsStore = useSongsStore()

const filterChecklistId = ref<number | null>(null)
const filterMemberId = ref<number | null>(null)
const filterStatus = ref<string>('all')

const showAddModal = ref(false)
const editingIncident = ref<EmergencyIncident | null>(null)
const saving = ref(false)
const incidentForm = ref({
  checklist_id: null as number | null,
  member_id: null as number | null,
  incident_type: 'sprain' as IncidentType,
  song_id: null as number | null,
  position_id: '',
  formation_position: '',
  description: '',
  severity: 'minor' as IncidentSeverity,
  treatment_given: '',
  treated_by: '',
  family_notified: false,
  family_notification_details: '',
  community_leader_notified: false,
  community_notification_details: '',
  follow_up_required: false,
  follow_up_notes: '',
})

const showDetailModal = ref(false)
const selectedIncident = ref<EmergencyIncident | null>(null)

const resolveTarget = ref<EmergencyIncident | null>(null)

const filteredIncidents = computed(() => {
  return safetyStore.incidents.filter((incident) => {
    if (filterChecklistId.value !== null && incident.checklist_id !== filterChecklistId.value) return false
    if (filterMemberId.value !== null && incident.member_id !== filterMemberId.value) return false
    if (filterStatus.value === 'active' && incident.resolved) return false
    if (filterStatus.value === 'resolved' && !incident.resolved) return false
    return true
  }).sort((a, b) => {
    const timeA = a.incident_time ? new Date(a.incident_time).getTime() : 0
    const timeB = b.incident_time ? new Date(b.incident_time).getTime() : 0
    return timeB - timeA
  })
})

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

function formatDateTime(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hours}:${minutes}`
}

function resetFilters() {
  filterChecklistId.value = null
  filterMemberId.value = null
  filterStatus.value = 'all'
}

function openAddModal() {
  editingIncident.value = null
  incidentForm.value = {
    checklist_id: safetyStore.checklists[0]?.id || null,
    member_id: null,
    incident_type: 'sprain',
    song_id: null,
    position_id: '',
    formation_position: '',
    description: '',
    severity: 'minor',
    treatment_given: '',
    treated_by: '',
    family_notified: false,
    family_notification_details: '',
    community_leader_notified: false,
    community_notification_details: '',
    follow_up_required: false,
    follow_up_notes: '',
  }
  showAddModal.value = true
}

async function saveIncident() {
  if (!incidentForm.value.checklist_id) {
    alert('请选择关联检查单')
    return
  }
  if (!incidentForm.value.member_id) {
    alert('请选择关联成员')
    return
  }

  saving.value = true
  try {
    const data = {
      checklist_id: incidentForm.value.checklist_id,
      member_id: incidentForm.value.member_id,
      incident_type: incidentForm.value.incident_type,
      song_id: incidentForm.value.song_id || undefined,
      position_id: incidentForm.value.position_id || undefined,
      formation_position: incidentForm.value.formation_position || undefined,
      description: incidentForm.value.description || undefined,
      severity: incidentForm.value.severity,
      treatment_given: incidentForm.value.treatment_given || undefined,
      treated_by: incidentForm.value.treated_by || undefined,
      family_notified: incidentForm.value.family_notified,
      family_notification_details: incidentForm.value.family_notification_details || undefined,
      community_leader_notified: incidentForm.value.community_leader_notified,
      community_notification_details: incidentForm.value.community_notification_details || undefined,
      follow_up_required: incidentForm.value.follow_up_required,
      follow_up_notes: incidentForm.value.follow_up_notes || undefined,
    }

    if (editingIncident.value) {
      await safetyStore.updateIncident(editingIncident.value.id, data)
    } else {
      await safetyStore.createIncident(data)
    }

    showAddModal.value = false
  } catch (e) {
    console.error('Failed to save incident', e)
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

function viewDetail(incident: EmergencyIncident) {
  selectedIncident.value = incident
  showDetailModal.value = true
}

function confirmResolve(incident: EmergencyIncident) {
  resolveTarget.value = incident
}

async function doResolve() {
  if (!resolveTarget.value) return
  try {
    await safetyStore.resolveIncident(resolveTarget.value.id)
    resolveTarget.value = null
    showDetailModal.value = false
  } catch (e) {
    console.error('Failed to resolve incident', e)
    alert('操作失败，请重试')
  }
}

async function loadData() {
  await Promise.all([
    safetyStore.fetchIncidents(),
    safetyStore.fetchChecklists(),
    membersStore.fetchMembers(),
    songsStore.fetchSongs(),
  ])
}

onMounted(() => {
  loadData()
})
</script>
