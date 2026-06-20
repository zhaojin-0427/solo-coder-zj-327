<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1F2937]">风险成员管理</h1>
      <div class="flex items-center gap-3">
        <select
          v-model="filterRiskLevel"
          class="px-3 py-2 text-sm border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935]"
        >
          <option value="all">全部风险等级</option>
          <option value="critical">极高风险</option>
          <option value="high">高风险</option>
          <option value="medium">中风险</option>
          <option value="low">低风险</option>
        </select>
        <select
          v-model="filterStatus"
          class="px-3 py-2 text-sm border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935]"
        >
          <option value="all">全部状态</option>
          <option value="pending">待处理</option>
          <option value="adjusted">已调整站位</option>
          <option value="resting">安排休息</option>
          <option value="monitoring">持续观察</option>
        </select>
        <button
          class="btn-primary text-sm flex items-center gap-1.5"
          @click="refreshData"
        >
          <RefreshCw :size="16" />
          刷新
        </button>
      </div>
    </div>

    <div v-if="safetyStore.loading" class="text-center py-16 text-[#6B7280] text-lg">加载中...</div>

    <div v-else-if="!filteredRiskMembers.length" class="text-center py-16">
      <AlertCircle :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无高风险成员</p>
    </div>

    <div v-else class="space-y-5">
      <div
        v-for="riskMember in filteredRiskMembers"
        :key="riskMember.id"
        class="card"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <div class="flex items-center gap-2">
                <User :size="20" class="text-[#6B7280]" />
                <h3 class="text-lg font-semibold text-[#1F2937]">{{ riskMember.member_name }}</h3>
              </div>
              <span
                class="px-2 py-0.5 text-xs rounded-full font-medium"
                :class="RISK_LEVEL_COLOR_MAP[riskMember.risk_level]"
              >
                {{ RISK_LEVEL_MAP[riskMember.risk_level] }}
              </span>
              <span
                class="px-2 py-0.5 text-xs rounded-full font-medium"
                :class="RISK_MEMBER_STATUS_COLOR_MAP[riskMember.status]"
              >
                {{ RISK_MEMBER_STATUS_MAP[riskMember.status] }}
              </span>
              <span v-if="riskMember.member_age" class="text-sm text-[#6B7280]">
                年龄: {{ riskMember.member_age }}岁
              </span>
            </div>
            <div class="flex items-center gap-4 text-sm text-[#6B7280]">
              <span v-if="riskMember.risk_factors" class="flex items-center gap-1.5">
                <AlertTriangle :size="14" />
                风险因素: {{ riskMember.risk_factors }}
              </span>
              <span class="flex items-center gap-1.5">
                <Clock :size="14" />
                创建时间: {{ formatTime(riskMember.created_at) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              class="btn-secondary text-sm flex items-center gap-1.5"
              @click="viewHealthRecords(riskMember)"
            >
              <FileText :size="16" />
              健康档案
            </button>
            <button
              class="btn-primary text-sm flex items-center gap-1.5"
              @click="openUpdateStatus(riskMember)"
            >
              <Edit3 :size="16" />
              更新状态
            </button>
          </div>
        </div>

        <div v-if="riskMember.recommendation" class="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div class="flex items-start gap-2">
            <Lightbulb :size="18" class="text-blue-600 mt-0.5 shrink-0" />
            <div>
              <p class="text-sm font-medium text-blue-900 mb-1">建议措施</p>
              <p class="text-sm text-blue-800">{{ riskMember.recommendation }}</p>
            </div>
          </div>
        </div>

        <div v-if="riskMember.action_taken" class="p-4 bg-green-50 rounded-lg border border-green-100">
          <div class="flex items-start gap-2">
            <CheckCircle :size="18" class="text-green-600 mt-0.5 shrink-0" />
            <div>
              <p class="text-sm font-medium text-green-900 mb-1">已采取的措施</p>
              <p class="text-sm text-green-800">{{ riskMember.action_taken }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showHealthModal" class="modal-overlay" @click.self="closeHealthModal">
        <div class="modal-content w-[800px] max-h-[85vh] overflow-hidden flex flex-col p-0">
          <div class="p-6 pb-4 border-b border-[#E5E7EB] flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#1F2937]">
              {{ selectedRiskMember?.member_name }} - 健康档案
            </h3>
            <div class="flex items-center gap-3">
              <button
                class="btn-primary text-sm flex items-center gap-1.5"
                @click="openAddHealthRecord"
              >
                <Plus :size="14" />
                添加健康记录
              </button>
              <button class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg" @click="closeHealthModal">
                <X :size="18" />
              </button>
            </div>
          </div>

          <div v-if="safetyStore.loading" class="flex-1 flex items-center justify-center py-16 text-[#6B7280]">
            加载中...
          </div>

          <div v-else-if="!memberHealthRecords.length && !memberWithHealth" class="flex-1 flex items-center justify-center py-16">
            <div class="text-center">
              <FileText :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
              <p class="text-[#6B7280]">暂无健康档案</p>
            </div>
          </div>

          <div v-else class="flex-1 overflow-y-auto p-6">
            <div v-if="memberWithHealth" class="mb-6 p-4 bg-gray-50 rounded-lg border border-[#E5E7EB]">
              <h4 class="text-base font-semibold text-[#1F2937] mb-3">基本信息</h4>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-[#6B7280]">姓名：</span>
                  <span class="text-[#1F2937] font-medium">{{ memberWithHealth.name }}</span>
                </div>
                <div>
                  <span class="text-[#6B7280]">年龄：</span>
                  <span class="text-[#1F2937] font-medium">{{ memberWithHealth.age || '未填写' }}</span>
                </div>
                <div>
                  <span class="text-[#6B7280]">身高：</span>
                  <span class="text-[#1F2937] font-medium">{{ HEIGHT_RANGE_MAP[memberWithHealth.height_range] }}</span>
                </div>
                <div>
                  <span class="text-[#6B7280]">联系电话：</span>
                  <span class="text-[#1F2937] font-medium">{{ memberWithHealth.phone || '未填写' }}</span>
                </div>
                <div>
                  <span class="text-[#6B7280]">紧急联系人：</span>
                  <span class="text-[#1F2937] font-medium">{{ memberWithHealth.emergency_contact || '未填写' }}</span>
                </div>
              </div>
            </div>

            <div v-if="memberHealthRecords.length">
              <h4 class="text-base font-semibold text-[#1F2937] mb-3">健康状况历史</h4>
              <div class="space-y-3">
                <div
                  v-for="record in memberHealthRecords"
                  :key="record.id"
                  class="p-4 border border-[#E5E7EB] rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div class="flex items-start justify-between mb-2">
                    <div class="flex items-center gap-2">
                      <span class="px-2 py-0.5 text-xs rounded-full bg-purple-100 text-purple-700 font-medium">
                        {{ HEALTH_CONDITION_MAP[record.condition_type] }}
                      </span>
                      <span v-if="record.is_chronic" class="px-2 py-0.5 text-xs rounded-full bg-orange-100 text-orange-700 font-medium">
                        慢性病
                      </span>
                      <span class="text-sm text-[#6B7280]">{{ formatTime(record.record_date) }}</span>
                    </div>
                    <button
                      class="p-1.5 text-[#6B7280] hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                      @click="confirmDeleteRecord(record)"
                    >
                      <Trash2 :size="14" />
                    </button>
                  </div>
                  <p v-if="record.description" class="text-sm text-[#1F2937] mb-2">{{ record.description }}</p>
                  <div v-if="record.needs_accommodation" class="text-sm text-amber-700 bg-amber-50 px-2 py-1 rounded">
                    <span class="font-medium">需要特殊照顾：</span>{{ record.accommodation_notes || '请根据实际情况安排' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showAddHealthRecordModal" class="modal-overlay" @click.self="showAddHealthRecordModal = false">
        <div class="modal-content w-[520px] p-6">
          <h3 class="text-lg font-semibold text-[#1F2937] mb-4">添加健康记录</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">记录日期</label>
              <input v-model="healthRecordForm.record_date" type="date" class="input" />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">健康状况类型</label>
              <select v-model="healthRecordForm.condition_type" class="input">
                <option v-for="(label, value) in HEALTH_CONDITION_MAP" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">详细描述</label>
              <textarea
                v-model="healthRecordForm.description"
                class="input min-h-[100px] resize-none"
                placeholder="请描述健康状况的详细情况"
              ></textarea>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model="healthRecordForm.is_chronic"
                type="checkbox"
                id="is_chronic"
                class="w-4 h-4 text-[#E53935] rounded focus:ring-[#E53935]"
              />
              <label for="is_chronic" class="text-sm text-[#1F2937]">是否为慢性病</label>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model="healthRecordForm.needs_accommodation"
                type="checkbox"
                id="needs_accommodation"
                class="w-4 h-4 text-[#E53935] rounded focus:ring-[#E53935]"
              />
              <label for="needs_accommodation" class="text-sm text-[#1F2937]">需要特殊照顾</label>
            </div>
            <div v-if="healthRecordForm.needs_accommodation">
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">特殊照顾说明</label>
              <textarea
                v-model="healthRecordForm.accommodation_notes"
                class="input min-h-[80px] resize-none"
                placeholder="请说明需要哪些特殊照顾"
              ></textarea>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button class="btn-secondary flex-1" @click="showAddHealthRecordModal = false">取消</button>
            <button class="btn-primary flex-1" @click="saveHealthRecord" :disabled="savingHealthRecord">
              {{ savingHealthRecord ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showUpdateStatusModal" class="modal-overlay" @click.self="showUpdateStatusModal = false">
        <div class="modal-content w-[520px] p-6">
          <h3 class="text-lg font-semibold text-[#1F2937] mb-4">更新风险成员状态</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">成员</label>
              <p class="text-sm text-[#6B7280]">{{ selectedRiskMember?.member_name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">风险等级</label>
              <select v-model="statusForm.risk_level" class="input">
                <option v-for="(label, value) in RISK_LEVEL_MAP" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">处理状态</label>
              <select v-model="statusForm.status" class="input">
                <option v-for="(label, value) in RISK_MEMBER_STATUS_MAP" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">建议措施</label>
              <div class="space-y-2">
                <label class="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    :checked="statusForm.recommendation?.includes('调整站位')"
                    @change="toggleRecommendation('调整站位')"
                    class="w-4 h-4 text-[#E53935] rounded focus:ring-[#E53935]"
                  />
                  调整站位
                </label>
                <label class="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    :checked="statusForm.recommendation?.includes('减少高强度动作')"
                    @change="toggleRecommendation('减少高强度动作')"
                    class="w-4 h-4 text-[#E53935] rounded focus:ring-[#E53935]"
                  />
                  减少高强度动作
                </label>
                <label class="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    :checked="statusForm.recommendation?.includes('安排休息')"
                    @change="toggleRecommendation('安排休息')"
                    class="w-4 h-4 text-[#E53935] rounded focus:ring-[#E53935]"
                  />
                  安排休息
                </label>
              </div>
              <textarea
                v-model="statusForm.recommendation_text"
                class="input min-h-[80px] resize-none mt-2"
                placeholder="其他建议措施（选填）"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">已采取的措施</label>
              <textarea
                v-model="statusForm.action_taken"
                class="input min-h-[100px] resize-none"
                placeholder="请记录已采取的具体措施"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">风险因素说明</label>
              <input
                v-model="statusForm.risk_factors"
                type="text"
                class="input"
                placeholder="如：高血压、心脏病、年龄偏大等"
              />
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button class="btn-secondary flex-1" @click="showUpdateStatusModal = false">取消</button>
            <button class="btn-primary flex-1" @click="updateRiskMemberStatus" :disabled="updatingStatus">
              {{ updatingStatus ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="deleteTargetRecord" class="modal-overlay" @click.self="deleteTargetRecord = null">
        <div class="modal-content p-6">
          <h2 class="text-xl font-semibold text-[#1F2937] mb-3">确认删除</h2>
          <p class="text-base text-[#6B7280] mb-5">
            确定要删除这条健康记录吗？此操作不可撤销。
          </p>
          <div class="flex gap-3">
            <button class="btn-primary flex-1" @click="doDeleteRecord">确认删除</button>
            <button class="btn-secondary flex-1" @click="deleteTargetRecord = null">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  User, AlertCircle, AlertTriangle, Clock, FileText, Edit3, Plus, X,
  RefreshCw, CheckCircle, Lightbulb, Trash2,
} from 'lucide-vue-next'
import type {
  RiskMember,
  MemberHealthRecord,
  MemberWithHealth,
  RiskLevel,
  RiskMemberStatus,
  HealthConditionType,
} from '@/types'
import {
  RISK_LEVEL_MAP,
  RISK_LEVEL_COLOR_MAP,
  RISK_MEMBER_STATUS_MAP,
  RISK_MEMBER_STATUS_COLOR_MAP,
  HEALTH_CONDITION_MAP,
  HEIGHT_RANGE_MAP,
} from '@/types'
import { useSafetyStore } from '@/stores/safety'
import { useMembersStore } from '@/stores/members'

const safetyStore = useSafetyStore()
const membersStore = useMembersStore()

const filterRiskLevel = ref<string>('all')
const filterStatus = ref<string>('all')

const showHealthModal = ref(false)
const selectedRiskMember = ref<RiskMember | null>(null)
const memberHealthRecords = ref<MemberHealthRecord[]>([])
const memberWithHealth = ref<MemberWithHealth | null>(null)

const showAddHealthRecordModal = ref(false)
const savingHealthRecord = ref(false)
const healthRecordForm = ref({
  record_date: new Date().toISOString().slice(0, 10),
  condition_type: 'other' as HealthConditionType,
  description: '',
  is_chronic: false,
  needs_accommodation: false,
  accommodation_notes: '',
})

const showUpdateStatusModal = ref(false)
const updatingStatus = ref(false)
const statusForm = ref({
  risk_level: 'high' as RiskLevel,
  status: 'pending' as RiskMemberStatus,
  recommendation: [] as string[],
  recommendation_text: '',
  action_taken: '',
  risk_factors: '',
})

const deleteTargetRecord = ref<MemberHealthRecord | null>(null)

const filteredRiskMembers = computed(() => {
  return safetyStore.riskMembers.filter((rm) => {
    if (filterRiskLevel.value !== 'all' && rm.risk_level !== filterRiskLevel.value) return false
    if (filterStatus.value !== 'all' && rm.status !== filterStatus.value) return false
    return true
  })
})

function formatTime(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${year}年${month}月${day}日`
}

async function refreshData() {
  await Promise.all([
    safetyStore.fetchRiskMembers(),
    membersStore.fetchMembers(),
  ])
}

async function viewHealthRecords(riskMember: RiskMember) {
  selectedRiskMember.value = riskMember
  showHealthModal.value = true
  try {
    await Promise.all([
      safetyStore.fetchHealthRecords(riskMember.member_id),
      safetyStore.fetchMemberWithHealth(riskMember.member_id),
    ])
    const records = safetyStore.healthRecords
    const memberHealth = safetyStore.memberWithHealth
    memberHealthRecords.value = records
    memberWithHealth.value = memberHealth
  } catch {
    memberHealthRecords.value = []
    memberWithHealth.value = null
  }
}

function closeHealthModal() {
  showHealthModal.value = false
  selectedRiskMember.value = null
  memberHealthRecords.value = []
  memberWithHealth.value = null
}

function openAddHealthRecord() {
  healthRecordForm.value = {
    record_date: new Date().toISOString().slice(0, 10),
    condition_type: 'other',
    description: '',
    is_chronic: false,
    needs_accommodation: false,
    accommodation_notes: '',
  }
  showAddHealthRecordModal.value = true
}

async function saveHealthRecord() {
  if (!selectedRiskMember.value) return
  savingHealthRecord.value = true
  try {
    const result = await safetyStore.createHealthRecord({
      member_id: selectedRiskMember.value.member_id,
      record_date: healthRecordForm.value.record_date,
      condition_type: healthRecordForm.value.condition_type,
      description: healthRecordForm.value.description || undefined,
      is_chronic: healthRecordForm.value.is_chronic,
      needs_accommodation: healthRecordForm.value.needs_accommodation,
      accommodation_notes: healthRecordForm.value.accommodation_notes || undefined,
    })
    memberHealthRecords.value.unshift(result)
    showAddHealthRecordModal.value = false
  } catch {
    alert('保存失败，请重试')
  } finally {
    savingHealthRecord.value = false
  }
}

function confirmDeleteRecord(record: MemberHealthRecord) {
  deleteTargetRecord.value = record
}

async function doDeleteRecord() {
  if (!deleteTargetRecord.value) return
  try {
    await safetyStore.deleteHealthRecord(deleteTargetRecord.value.id)
    memberHealthRecords.value = memberHealthRecords.value.filter((r) => r.id !== deleteTargetRecord.value!.id)
    deleteTargetRecord.value = null
  } catch {
    alert('删除失败')
  }
}

function openUpdateStatus(riskMember: RiskMember) {
  selectedRiskMember.value = riskMember
  const recommendations = riskMember.recommendation?.split('；') || []
  statusForm.value = {
    risk_level: riskMember.risk_level,
    status: riskMember.status,
    recommendation: recommendations.filter((r) => ['调整站位', '减少高强度动作', '安排休息'].includes(r)),
    recommendation_text: recommendations.filter((r) => !['调整站位', '减少高强度动作', '安排休息'].includes(r)).join('；'),
    action_taken: riskMember.action_taken || '',
    risk_factors: riskMember.risk_factors || '',
  }
  showUpdateStatusModal.value = true
}

function toggleRecommendation(item: string) {
  const idx = statusForm.value.recommendation.indexOf(item)
  if (idx >= 0) {
    statusForm.value.recommendation.splice(idx, 1)
  } else {
    statusForm.value.recommendation.push(item)
  }
}

async function updateRiskMemberStatus() {
  if (!selectedRiskMember.value) return
  updatingStatus.value = true
  try {
    const allRecommendations = [...statusForm.value.recommendation]
    if (statusForm.value.recommendation_text.trim()) {
      allRecommendations.push(statusForm.value.recommendation_text.trim())
    }
    const recommendation = allRecommendations.join('；')

    await safetyStore.updateRiskMember(selectedRiskMember.value.id, {
      risk_level: statusForm.value.risk_level,
      status: statusForm.value.status,
      recommendation: recommendation || undefined,
      action_taken: statusForm.value.action_taken || undefined,
      risk_factors: statusForm.value.risk_factors || undefined,
    })
    showUpdateStatusModal.value = false
    await safetyStore.fetchRiskMembers()
  } catch {
    alert('更新失败，请重试')
  } finally {
    updatingStatus.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    safetyStore.fetchRiskMembers(),
    membersStore.fetchMembers(),
  ])
})
</script>
