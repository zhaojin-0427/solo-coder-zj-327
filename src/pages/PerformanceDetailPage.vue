<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <button
        class="p-2 text-[#6B7280] hover:text-[#1F2937] hover:bg-gray-100 rounded-lg"
        @click="goBack"
      >
        <ArrowLeft :size="20" />
      </button>
      <h1 class="text-2xl font-bold text-[#1F2937]">演出任务详情</h1>
    </div>

    <div v-if="performancesStore.loading" class="text-center py-16 text-[#6B7280] text-lg">
      加载中...
    </div>

    <div v-else-if="!performance" class="text-center py-16">
      <p class="text-lg text-[#6B7280]">演出任务不存在</p>
    </div>

    <div v-else class="space-y-6">
      <div class="card">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h2 class="text-xl font-semibold text-[#1F2937] mb-2">{{ performance.name }}</h2>
            <div class="flex items-center gap-4 text-sm text-[#6B7280]">
              <span class="flex items-center gap-1.5">
                <MapPin :size="14" />
                {{ performance.location }}
              </span>
              <span class="flex items-center gap-1.5">
                <Clock :size="14" />
                集合: {{ formatDateTime(performance.meeting_time) }}
              </span>
              <span class="flex items-center gap-1.5">
                <PlayCircle :size="14" />
                开演: {{ formatDateTime(performance.start_time) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-4 text-sm">
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ performance.confirmed_count }}</div>
                <div class="text-[#6B7280]">已确认</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-yellow-600">{{ performance.unconfirmed_count }}</div>
                <div class="text-[#6B7280]">未确认</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{{ performance.leave_count }}</div>
                <div class="text-[#6B7280]">请假</div>
              </div>
              <div class="text-center pl-4 border-l border-[#E5E7EB]">
                <div class="text-2xl font-bold text-[#1F2937]">{{ performance.total_members }}</div>
                <div class="text-[#6B7280]">总人数</div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div v-if="performance.costume_requirements">
            <h4 class="text-sm font-medium text-[#1F2937] mb-1">服装/道具要求</h4>
            <p class="text-sm text-[#6B7280]">{{ performance.costume_requirements }}</p>
          </div>
          <div v-if="performance.notes">
            <h4 class="text-sm font-medium text-[#1F2937] mb-1">注意事项</h4>
            <p class="text-sm text-[#6B7280]">{{ performance.notes }}</p>
          </div>
        </div>
      </div>

      <div v-if="checkSummary" class="card">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-base font-semibold text-[#1F2937] flex items-center gap-2">
            <ClipboardCheck class="text-[#E53935]" :size="18" />
            演前检查进度
          </h3>
          <button
            class="text-sm text-[#E53935] hover:underline"
            @click="router.push('/pre-check')"
          >
            查看详情
          </button>
        </div>
        <div class="flex items-center gap-4 mb-3">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-gray-400"></div>
            <span class="text-sm text-[#6B7280]">未开始 {{ checkSummary.not_started_count }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-blue-500"></div>
            <span class="text-sm text-[#6B7280]">进行中 {{ checkSummary.in_progress_count }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-red-500"></div>
            <span class="text-sm text-[#6B7280]">异常 {{ checkSummary.abnormal_count }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
            <span class="text-sm text-[#6B7280]">已完成 {{ checkSummary.completed_count }}</span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden flex">
            <div
              class="h-full bg-green-500 transition-all duration-300"
              :style="{ width: checkSummary.completion_rate * 100 + '%' }"
            ></div>
            <div
              class="h-full bg-red-500 transition-all duration-300"
              :style="{ width: (checkSummary.abnormal_count / checkSummary.total_items) * 100 + '%' }"
            ></div>
            <div
              class="h-full bg-blue-500 transition-all duration-300"
              :style="{ width: (checkSummary.in_progress_count / checkSummary.total_items) * 100 + '%' }"
            ></div>
          </div>
          <span class="text-sm font-semibold text-[#1F2937] w-12 text-right">
            {{ (checkSummary.completion_rate * 100).toFixed(0) }}%
          </span>
        </div>

        <div v-if="checkAbnormalItems.length" class="mt-4 pt-3 border-t border-[#E5E7EB]">
          <h4 class="text-sm font-medium text-red-600 mb-2 flex items-center gap-1.5">
            <AlertTriangle :size="14" />
            异常项联动提示
          </h4>
          <div class="space-y-2">
            <div
              v-for="abn in checkAbnormalItems"
              :key="abn.item_id"
              class="flex items-start gap-2 text-sm"
            >
              <span class="px-1.5 py-0.5 text-xs rounded bg-red-100 text-red-700 font-medium shrink-0">
                {{ CHECK_CATEGORY_MAP[abn.category] }}
              </span>
              <div class="flex-1">
                <span class="text-[#1F2937]">{{ abn.item_name }}</span>
                <span class="text-[#6B7280] mx-1">·</span>
                <span class="text-[#6B7280]">{{ abn.song_name }}</span>
                <span v-if="abn.position_id" class="text-[#6B7280] mx-1">·</span>
                <span v-if="abn.position_id" class="text-yellow-600 font-medium">站位 {{ abn.position_id }} 存在风险</span>
                <span v-if="abn.responsible_member_name" class="text-[#6B7280] mx-1">·</span>
                <span v-if="abn.responsible_member_name" class="text-[#6B7280]">负责人: {{ abn.responsible_member_name }}</span>
                <div v-if="abn.abnormal_description" class="text-red-500 text-xs mt-0.5">
                  {{ abn.abnormal_description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-2 mb-4">
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === 'confirmations' ? 'bg-[#E53935] text-white' : 'bg-white text-[#6B7280] hover:bg-gray-50 border border-[#E5E7EB]'"
          @click="activeTab = 'confirmations'"
        >
          成员确认列表
        </button>
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === 'songs' ? 'bg-[#E53935] text-white' : 'bg-white text-[#6B7280] hover:bg-gray-50 border border-[#E5E7EB]'"
          @click="activeTab = 'songs'"
        >
          曲目队形详情
        </button>
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="activeTab === 'checklist' ? 'bg-[#E53935] text-white' : 'bg-white text-[#6B7280] hover:bg-gray-50 border border-[#E5E7EB]'"
          @click="activeTab = 'checklist'"
        >
          演前检查清单
        </button>
      </div>

      <div v-if="activeTab === 'confirmations'" class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-[#1F2937]">成员确认情况</h3>
          <div class="flex items-center gap-2">
            <select
              v-model="filterStatus"
              class="px-3 py-1.5 text-sm border border-[#E5E7EB] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E53935]"
            >
              <option value="all">全部状态</option>
              <option value="unconfirmed">未确认</option>
              <option value="confirmed">已确认</option>
              <option value="leave">请假</option>
            </select>
          </div>
        </div>

        <div v-if="!confirmations.length" class="text-center py-8 text-[#9CA3AF]">
          暂无确认数据
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="text-left text-sm text-[#6B7280] border-b border-[#E5E7EB]">
                <th class="pb-3 font-medium">成员</th>
                <th class="pb-3 font-medium">状态</th>
                <th class="pb-3 font-medium">交通方式</th>
                <th class="pb-3 font-medium">备注</th>
                <th class="pb-3 font-medium">电话提醒</th>
                <th class="pb-3 font-medium">确认时间</th>
                <th class="pb-3 font-medium text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#F3F4F6]">
              <tr v-for="conf in filteredConfirmations" :key="conf.id" class="text-sm">
                <td class="py-3">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
                      :class="getMemberHeightColor(conf.member_id)"
                    >
                      {{ conf.member_name.charAt(0) }}
                    </div>
                    <div>
                      <div class="text-[#1F2937] font-medium">{{ conf.member_name }}</div>
                      <div class="text-xs text-[#9CA3AF]">{{ conf.member_phone || '暂无电话' }}</div>
                    </div>
                  </div>
                </td>
                <td class="py-3">
                  <span
                    class="px-2 py-1 text-xs rounded-full font-medium"
                    :class="CONFIRMATION_STATUS_COLOR_MAP[conf.status]"
                  >
                    {{ CONFIRMATION_STATUS_MAP[conf.status] }}
                  </span>
                </td>
                <td class="py-3 text-[#6B7280]">{{ conf.transport_mode || '-' }}</td>
                <td class="py-3 text-[#6B7280] max-w-[180px] truncate" :title="conf.remark || ''">
                  {{ conf.remark || '-' }}
                </td>
                <td class="py-3">
                  <span v-if="conf.phone_reminded" class="text-green-600 text-xs flex items-center gap-1">
                    <CheckCircle :size="14" />
                    已提醒
                  </span>
                  <span v-else class="text-[#9CA3AF] text-xs">未提醒</span>
                </td>
                <td class="py-3 text-[#6B7280]">
                  {{ conf.confirmed_at ? formatDateTime(conf.confirmed_at) : '-' }}
                </td>
                <td class="py-3 text-right">
                  <button
                    v-if="!conf.phone_reminded"
                    class="text-xs text-[#E53935] hover:underline"
                    @click="markPhoneReminded(conf)"
                  >
                    标记已提醒
                  </button>
                  <button
                    class="text-xs text-[#6B7280] hover:underline ml-3"
                    @click="openEditConfirmation(conf)"
                  >
                    编辑
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="activeTab === 'songs'" class="space-y-4">
        <div
          v-for="songDetail in songDetails"
          :key="songDetail.song_id"
          class="card"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-[#E53935]/10 flex items-center justify-center">
                <Music class="text-[#E53935]" :size="20" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-[#1F2937]">{{ songDetail.song_name }}</h3>
                <p class="text-sm text-[#6B7280]">
                  队形版本: v{{ songDetail.formation_version || '暂无' }}
                  · 共 {{ songDetail.total_positions }} 个站位
                </p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div class="p-4 bg-red-50 rounded-lg">
              <div class="flex items-center gap-2 mb-2">
                <UserX class="text-red-500" :size="18" />
                <span class="text-sm font-medium text-red-700">请假成员</span>
                <span class="ml-auto text-lg font-bold text-red-600">
                  {{ songDetail.leave_members.length }}
                </span>
              </div>
              <div v-if="!songDetail.leave_members.length" class="text-sm text-red-400">
                暂无请假
              </div>
              <div v-else class="space-y-1">
                <div
                  v-for="item in songDetail.leave_members"
                  :key="item.position_id"
                  class="text-sm text-red-700 flex items-center gap-2"
                >
                  <span class="text-xs bg-red-200 text-red-800 px-1.5 py-0.5 rounded">
                    {{ item.position_id }}
                  </span>
                  <span>{{ item.member_name }}</span>
                </div>
              </div>
            </div>

            <div class="p-4 bg-green-50 rounded-lg">
              <div class="flex items-center gap-2 mb-2">
                <UserCheck class="text-green-500" :size="18" />
                <span class="text-sm font-medium text-green-700">已确认替补</span>
                <span class="ml-auto text-lg font-bold text-green-600">
                  {{ songDetail.confirmed_substitutes.length }}
                </span>
              </div>
              <div v-if="!songDetail.confirmed_substitutes.length" class="text-sm text-green-400">
                暂无确认替补
              </div>
              <div v-else class="space-y-1">
                <div
                  v-for="item in songDetail.confirmed_substitutes"
                  :key="item.position_id"
                  class="text-sm text-green-700 flex items-center gap-2"
                >
                  <span class="text-xs bg-green-200 text-green-800 px-1.5 py-0.5 rounded">
                    {{ item.position_id }}
                  </span>
                  <span>{{ item.substitute_member_name }}</span>
                </div>
              </div>
            </div>

            <div class="p-4 bg-yellow-50 rounded-lg">
              <div class="flex items-center gap-2 mb-2">
                <AlertTriangle class="text-yellow-500" :size="18" />
                <span class="text-sm font-medium text-yellow-700">仍缺口位置</span>
                <span class="ml-auto text-lg font-bold text-yellow-600">
                  {{ songDetail.gap_positions.length }}
                </span>
              </div>
              <div v-if="!songDetail.gap_positions.length" class="text-sm text-green-600">
                全部就位
              </div>
              <div v-else class="flex flex-wrap gap-1">
                <span
                  v-for="pos in songDetail.gap_positions"
                  :key="pos"
                  class="text-xs bg-yellow-200 text-yellow-800 px-2 py-0.5 rounded"
                >
                  {{ pos }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="getSongAbnormalItems(songDetail.song_id).length" class="mt-4 pt-3 border-t border-[#E5E7EB]">
            <h4 class="text-sm font-medium text-red-600 mb-2 flex items-center gap-1.5">
              <AlertTriangle :size="14" />
              该曲目检查异常项
            </h4>
            <div class="space-y-1">
              <div
                v-for="abn in getSongAbnormalItems(songDetail.song_id)"
                :key="abn.item_id"
                class="text-sm flex items-center gap-2"
              >
                <span class="px-1.5 py-0.5 text-xs rounded bg-red-100 text-red-700">{{ CHECK_CATEGORY_MAP[abn.category] }}</span>
                <span class="text-[#1F2937]">{{ abn.item_name }}</span>
                <span v-if="abn.position_id" class="text-yellow-600 text-xs">站位{{ abn.position_id }}风险</span>
                <span v-if="abn.responsible_member_name" class="text-[#6B7280] text-xs">- {{ abn.responsible_member_name }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!songDetails.length" class="card text-center py-8 text-[#9CA3AF]">
          暂无曲目数据
        </div>
      </div>

      <div v-if="activeTab === 'checklist'" class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-[#1F2937]">演前检查清单</h3>
          <button
            v-if="!checklistsStore.currentChecklist"
            class="btn-primary text-sm flex items-center gap-1.5"
            @click="generateChecklist"
          >
            <Plus :size="14" />
            生成检查清单
          </button>
        </div>

        <div v-if="!checklistsStore.currentChecklist" class="text-center py-8 text-[#9CA3AF]">
          尚未生成检查清单，请点击上方按钮生成
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="group in checklistGroupedItems"
            :key="group.song_id"
            class="border border-[#E5E7EB] rounded-lg p-4"
          >
            <div class="flex items-center gap-2 mb-3">
              <Music class="text-[#E53935]" :size="16" />
              <h4 class="text-base font-semibold text-[#1F2937]">{{ group.song_name }}</h4>
            </div>
            <div class="space-y-2">
              <div
                v-for="item in group.items"
                :key="item.id"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50"
              >
                <span
                  class="px-2 py-0.5 text-xs rounded-full font-medium shrink-0"
                  :class="CHECK_STATUS_COLOR_MAP[item.status]"
                >
                  {{ CHECK_STATUS_MAP[item.status] }}
                </span>
                <span class="px-2 py-0.5 text-xs rounded-full bg-purple-100 text-purple-700 font-medium shrink-0">
                  {{ CHECK_CATEGORY_MAP[item.category] }}
                </span>
                <span class="text-sm text-[#1F2937] flex-1">{{ item.item_name }}</span>
                <span v-if="item.responsible_member_name" class="text-xs text-[#6B7280]">{{ item.responsible_member_name }}</span>
                <div class="flex items-center gap-1">
                  <button
                    v-if="item.status === 'not_started'"
                    class="px-2 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100"
                    @click="startItem(item)"
                  >开始</button>
                  <button
                    v-if="item.status === 'in_progress'"
                    class="px-2 py-1 text-xs text-green-600 bg-green-50 rounded hover:bg-green-100"
                    @click="completeItem(item)"
                  >完成</button>
                  <button
                    v-if="item.status === 'in_progress' || item.status === 'not_started'"
                    class="px-2 py-1 text-xs text-red-600 bg-red-50 rounded hover:bg-red-100"
                    @click="openAbnormalFromDetail(item)"
                  >异常</button>
                  <button
                    v-if="item.status === 'abnormal'"
                    class="px-2 py-1 text-xs text-orange-600 bg-orange-50 rounded hover:bg-orange-100"
                    @click="resolveItem(item)"
                  >已解决</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showConfirmationModal" class="modal-overlay" @click.self="showConfirmationModal = false">
        <div class="modal-content w-[480px] p-6">
          <h3 class="text-lg font-semibold text-[#1F2937] mb-4">编辑确认信息</h3>
          <div v-if="editingConfirmation" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">成员</label>
              <p class="text-sm text-[#6B7280]">{{ editingConfirmation.member_name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">状态</label>
              <select
                v-model="confirmationForm.status"
                class="input"
              >
                <option value="unconfirmed">未确认</option>
                <option value="confirmed">已确认参加</option>
                <option value="leave">请假</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">交通方式</label>
              <input
                v-model="confirmationForm.transport_mode"
                type="text"
                class="input"
                placeholder="如：自驾、公交、步行等"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#1F2937] mb-1.5">备注</label>
              <textarea
                v-model="confirmationForm.remark"
                class="input min-h-[80px] resize-none"
                placeholder="请输入备注信息"
              ></textarea>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button class="btn-secondary flex-1" @click="showConfirmationModal = false">取消</button>
            <button class="btn-primary flex-1" @click="saveConfirmation" :disabled="savingConfirmation">
              {{ savingConfirmation ? '保存中...' : '保存' }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  MapPin,
  Clock,
  PlayCircle,
  Music,
  UserX,
  UserCheck,
  AlertTriangle,
  CheckCircle,
  Plus,
  ClipboardCheck,
} from 'lucide-vue-next'
import type {
  PerformanceConfirmation,
  PerformanceConfirmationStatus,
  SongPerformanceDetail,
  PerformanceTaskWithSongDetails,
  HeightRange,
  CheckItem,
  ChecklistSummary,
  CheckItemAbnormalDetail,
} from '@/types'
import {
  CONFIRMATION_STATUS_MAP,
  CONFIRMATION_STATUS_COLOR_MAP,
  CHECK_STATUS_MAP,
  CHECK_STATUS_COLOR_MAP,
  CHECK_CATEGORY_MAP,
} from '@/types'
import { usePerformancesStore } from '@/stores/performances'
import { useMembersStore } from '@/stores/members'
import { useChecklistsStore } from '@/stores/checklists'

const route = useRoute()
const router = useRouter()
const performancesStore = usePerformancesStore()
const membersStore = useMembersStore()
const checklistsStore = useChecklistsStore()

const activeTab = ref<'confirmations' | 'songs' | 'checklist'>('confirmations')
const filterStatus = ref<string>('all')
const showConfirmationModal = ref(false)
const editingConfirmation = ref<PerformanceConfirmation | null>(null)
const savingConfirmation = ref(false)
const confirmationForm = ref({
  status: 'unconfirmed' as PerformanceConfirmationStatus,
  transport_mode: '',
  remark: '',
})

const checkSummary = ref<ChecklistSummary | null>(null)
const checkAbnormalItems = ref<CheckItemAbnormalDetail[]>([])

const showAbnormalModal = ref(false)
const abnormalItem = ref<CheckItem | null>(null)
const abnormalDescription = ref('')
const abnormalPhotoUrl = ref('')
const submittingAbnormal = ref(false)

const performance = computed(() => performancesStore.currentPerformance)

const confirmations = computed(() => {
  if (!performance.value || !('confirmations' in performance.value)) return []
  return (performance.value as PerformanceTaskWithSongDetails).confirmations || []
})

const songDetails = computed((): SongPerformanceDetail[] => {
  if (!performance.value || !('song_details' in performance.value)) return []
  return (performance.value as PerformanceTaskWithSongDetails).song_details || []
})

const filteredConfirmations = computed(() => {
  if (filterStatus.value === 'all') return confirmations.value
  return confirmations.value.filter((c) => c.status === filterStatus.value)
})

const checklistGroupedItems = computed(() => {
  const items = checklistsStore.currentChecklist?.items || []
  const groups: Record<number, { song_id: number; song_name: string; items: CheckItem[] }> = {}
  for (const item of items) {
    if (!groups[item.song_id]) {
      groups[item.song_id] = { song_id: item.song_id, song_name: item.song_name, items: [] }
    }
    groups[item.song_id].items.push(item)
  }
  return Object.values(groups)
})

function getSongAbnormalItems(songId: number): CheckItemAbnormalDetail[] {
  return checkAbnormalItems.value.filter((a) => a.song_id === songId)
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${hours}:${minutes}`
}

function getMemberHeightColor(memberId: number): string {
  const member = membersStore.getMemberById(memberId)
  if (!member) return 'bg-gray-400'
  const colorMap: Record<HeightRange, string> = {
    short: 'bg-green-500',
    medium: 'bg-blue-500',
    tall: 'bg-orange-500',
  }
  return colorMap[member.height_range]
}

function goBack() {
  router.push('/performances')
}

function openEditConfirmation(conf: PerformanceConfirmation) {
  editingConfirmation.value = conf
  confirmationForm.value = {
    status: conf.status,
    transport_mode: conf.transport_mode || '',
    remark: conf.remark || '',
  }
  showConfirmationModal.value = true
}

async function saveConfirmation() {
  if (!editingConfirmation.value) return
  savingConfirmation.value = true
  try {
    const taskId = Number(route.params.id)
    await performancesStore.updateConfirmation(
      taskId,
      editingConfirmation.value.member_id,
      {
        status: confirmationForm.value.status,
        transport_mode: confirmationForm.value.transport_mode || null,
        remark: confirmationForm.value.remark || null,
      }
    )
    showConfirmationModal.value = false
  } catch (e) {
    console.error('Failed to save confirmation', e)
    alert('保存失败，请重试')
  } finally {
    savingConfirmation.value = false
  }
}

async function markPhoneReminded(conf: PerformanceConfirmation) {
  try {
    const taskId = Number(route.params.id)
    await performancesStore.markPhoneReminded(taskId, conf.member_id)
  } catch (e) {
    console.error('Failed to mark phone reminded', e)
    alert('操作失败，请重试')
  }
}

async function generateChecklist() {
  const taskId = Number(route.params.id)
  try {
    await checklistsStore.generateChecklist(taskId)
    await loadCheckData(taskId)
  } catch {
    alert('生成检查清单失败，请重试')
  }
}

async function startItem(item: CheckItem) {
  try {
    await checklistsStore.updateItem(item.id, { status: 'in_progress' })
    await loadCheckData(Number(route.params.id))
  } catch {
    alert('操作失败')
  }
}

async function completeItem(item: CheckItem) {
  try {
    await checklistsStore.updateItem(item.id, { status: 'completed' })
    await loadCheckData(Number(route.params.id))
  } catch {
    alert('操作失败')
  }
}

async function resolveItem(item: CheckItem) {
  try {
    await checklistsStore.updateItem(item.id, { status: 'completed', abnormal_description: '' })
    await loadCheckData(Number(route.params.id))
  } catch {
    alert('操作失败')
  }
}

function openAbnormalFromDetail(item: CheckItem) {
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
    await loadCheckData(Number(route.params.id))
  } catch {
    alert('提交失败')
  } finally {
    submittingAbnormal.value = false
  }
}

async function loadCheckData(taskId: number) {
  try {
    checkSummary.value = await checklistsStore.fetchSummary(taskId)
  } catch {
    checkSummary.value = null
  }
  try {
    await checklistsStore.fetchAbnormalItems(taskId)
    checkAbnormalItems.value = checklistsStore.abnormalItems
  } catch {
    checkAbnormalItems.value = []
  }
  try {
    await checklistsStore.fetchChecklist(taskId)
  } catch {
    // no checklist yet
  }
}

onMounted(async () => {
  const taskId = Number(route.params.id)
  await membersStore.fetchMembers()
  await performancesStore.fetchWithSongDetails(taskId)
  await loadCheckData(taskId)
})
</script>
