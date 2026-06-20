<template>
  <div>
    <h1 class="text-2xl font-bold text-[#1F2937] mb-6">统计分析</h1>

    <div v-if="statisticsStore.loading" class="text-center py-16 text-[#6B7280] text-lg">加载中...</div>

    <div v-else-if="!statisticsStore.rehearsalCounts.length && !statisticsStore.substituteRates.length" class="text-center py-16">
      <BarChart3 :size="48" class="mx-auto text-[#D1D5DB] mb-4" />
      <p class="text-lg text-[#6B7280]">暂无统计数据</p>
      <button class="btn-primary mt-4" @click="statisticsStore.fetchAll()">刷新数据</button>
    </div>

    <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-5">
      <div class="card">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">排练次数统计</h3>
        <div class="h-64">
          <Bar :data="rehearsalChartData" :options="rehearsalChartOptions" />
        </div>
      </div>

      <div class="card">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">替补发生率</h3>
        <div class="h-64 flex items-center justify-center">
          <Doughnut :data="substituteChartData" :options="substituteChartOptions" />
        </div>
      </div>

      <div class="card">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">高频错位位置热力图</h3>
        <div class="flex items-center justify-center h-64">
          <canvas ref="heatmapRef" width="400" height="280"></canvas>
        </div>
      </div>

      <div class="card">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">成员出勤活跃度</h3>
        <div class="space-y-3 max-h-64 overflow-y-auto pr-2 scrollbar-thin">
          <div
            v-for="(item, idx) in attendanceList"
            :key="item.member_id"
            class="flex items-center gap-3"
          >
            <span class="text-sm font-medium text-[#6B7280] w-6 text-right">{{ idx + 1 }}</span>
            <span class="text-base text-[#1F2937] w-20 truncate">{{ item.member_name }}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="getRateColor(item.attendance_rate)"
                :style="{ width: item.attendance_rate * 100 + '%' }"
              ></div>
            </div>
            <span class="text-sm font-semibold w-12 text-right" :class="getRateTextColor(item.attendance_rate)">
              {{ (item.attendance_rate * 100).toFixed(0) }}%
            </span>
          </div>
          <div v-if="!attendanceList.length" class="text-center text-sm text-[#9CA3AF] py-4">暂无数据</div>
        </div>
      </div>

      <div class="card xl:col-span-2">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">演出确认统计</h3>
        <div v-if="!statisticsStore.performanceConfirmations.length" class="text-center py-8 text-[#9CA3AF]">
          暂无演出数据
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-[#6B7280] border-b border-[#E5E7EB]">
                <th class="pb-3 font-medium">演出名称</th>
                <th class="pb-3 font-medium">演出日期</th>
                <th class="pb-3 font-medium text-center">总人数</th>
                <th class="pb-3 font-medium text-center">已确认</th>
                <th class="pb-3 font-medium text-center">未确认</th>
                <th class="pb-3 font-medium text-center">请假</th>
                <th class="pb-3 font-medium">确认率</th>
                <th class="pb-3 font-medium">电话提醒率</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#F3F4F6]">
              <tr v-for="item in statisticsStore.performanceConfirmations" :key="item.performance_id">
                <td class="py-3 text-[#1F2937] font-medium">{{ item.performance_name }}</td>
                <td class="py-3 text-[#6B7280]">{{ item.performance_date }}</td>
                <td class="py-3 text-center text-[#1F2937]">{{ item.total_members }}</td>
                <td class="py-3 text-center text-green-600 font-medium">{{ item.confirmed_count }}</td>
                <td class="py-3 text-center text-yellow-600 font-medium">{{ item.unconfirmed_count }}</td>
                <td class="py-3 text-center text-red-600 font-medium">{{ item.leave_count }}</td>
                <td class="py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-100 rounded-full h-2.5 max-w-[100px] overflow-hidden">
                      <div
                        class="h-full bg-green-500 rounded-full"
                        :style="{ width: item.confirmation_rate * 100 + '%' }"
                      ></div>
                    </div>
                    <span class="text-xs font-medium text-[#1F2937] w-10">
                      {{ (item.confirmation_rate * 100).toFixed(0) }}%
                    </span>
                  </div>
                </td>
                <td class="py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-100 rounded-full h-2.5 max-w-[100px] overflow-hidden">
                      <div
                        class="h-full bg-blue-500 rounded-full"
                        :style="{ width: item.phone_reminder_rate * 100 + '%' }"
                      ></div>
                    </div>
                    <span class="text-xs font-medium text-[#1F2937] w-10">
                      {{ (item.phone_reminder_rate * 100).toFixed(0) }}%
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card xl:col-span-2">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">演前准备统计</h3>
        <div v-if="!checklistsStore.preCheckStats.length && !checklistsStore.memberRank.length" class="text-center py-8 text-[#9CA3AF]">
          暂无演前检查数据
        </div>
        <div v-else class="space-y-6">
          <div>
            <h4 class="text-base font-medium text-[#1F2937] mb-3">各演出检查完成率</h4>
            <div v-if="!checklistsStore.preCheckStats.length" class="text-sm text-[#9CA3AF]">暂无数据</div>
            <div v-else class="space-y-3">
              <div
                v-for="item in checklistsStore.preCheckStats"
                :key="item.performance_id"
                class="flex items-center gap-3"
              >
                <span class="text-sm text-[#1F2937] w-40 truncate font-medium">{{ item.performance_name }}</span>
                <span class="text-xs text-[#6B7280] w-20">{{ item.performance_date }}</span>
                <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :class="getRateColor(item.completion_rate)"
                    :style="{ width: item.completion_rate * 100 + '%' }"
                  ></div>
                </div>
                <span class="text-sm font-semibold w-12 text-right" :class="getRateTextColor(item.completion_rate)">
                  {{ (item.completion_rate * 100).toFixed(0) }}%
                </span>
                <span class="text-xs text-[#6B7280] w-16 text-right">
                  {{ item.completed_count }}/{{ item.total_items }}
                </span>
                <span
                  v-if="item.abnormal_count > 0"
                  class="px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-700 font-medium"
                >
                  {{ item.abnormal_count }} 异常
                </span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div>
              <h4 class="text-base font-medium text-[#1F2937] mb-3">责任成员完成排行</h4>
              <div v-if="!checklistsStore.memberRank.length" class="text-sm text-[#9CA3AF]">暂无数据</div>
              <div v-else class="space-y-2 max-h-48 overflow-y-auto pr-2 scrollbar-thin">
                <div
                  v-for="(item, idx) in checklistsStore.memberRank"
                  :key="item.member_id"
                  class="flex items-center gap-3"
                >
                  <span class="text-sm font-medium w-6 text-right" :class="idx < 3 ? 'text-[#E53935]' : 'text-[#6B7280]'">
                    {{ idx + 1 }}
                  </span>
                  <span class="text-sm text-[#1F2937] w-20 truncate">{{ item.member_name }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-500"
                      :class="getRateColor(item.completion_rate)"
                      :style="{ width: item.completion_rate * 100 + '%' }"
                    ></div>
                  </div>
                  <span class="text-xs font-semibold w-10 text-right" :class="getRateTextColor(item.completion_rate)">
                    {{ (item.completion_rate * 100).toFixed(0) }}%
                  </span>
                  <span class="text-xs text-[#6B7280] w-20 text-right">
                    {{ item.completed_count }}/{{ item.total_assigned }}项
                  </span>
                  <span
                    v-if="item.abnormal_count > 0"
                    class="text-xs text-red-500"
                  >
                    {{ item.abnormal_count }}异常
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h4 class="text-base font-medium text-[#1F2937] mb-3">高频异常类型</h4>
              <div v-if="!checklistsStore.abnormalTypes.length" class="text-sm text-[#9CA3AF]">暂无异常数据</div>
              <div v-else class="space-y-3">
                <div
                  v-for="item in checklistsStore.abnormalTypes"
                  :key="item.category"
                  class="flex items-center gap-3"
                >
                  <span class="text-sm text-[#1F2937] w-20 font-medium">{{ CHECK_CATEGORY_MAP[item.category] }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                    <div
                      class="h-full bg-[#E53935] rounded-full transition-all duration-500"
                      :style="{ width: (item.count / maxAbnormalCount) * 100 + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-semibold text-[#E53935] w-8 text-right">{{ item.count }}</span>
                  <span class="text-xs text-[#6B7280]">次</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card xl:col-span-2">
        <h3 class="text-lg font-semibold text-[#1F2937] mb-4">安全统计</h3>
        <div v-if="!safetyStore.statsOverview && !safetyStore.incidentTypeStats.length" class="text-center py-8 text-[#9CA3AF]">
          暂无安全统计数据
        </div>
        <div v-else class="space-y-6">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
              <div class="flex items-center gap-2 mb-2">
                <ShieldCheck class="text-blue-600" :size="20" />
                <span class="text-sm text-blue-700 font-medium">安全检查单</span>
              </div>
              <p class="text-2xl font-bold text-blue-800">{{ safetyStore.statsOverview?.total_checklists || 0 }}</p>
            </div>
            <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4">
              <div class="flex items-center gap-2 mb-2">
                <AlertTriangle class="text-orange-600" :size="20" />
                <span class="text-sm text-orange-700 font-medium">突发事件</span>
              </div>
              <p class="text-2xl font-bold text-orange-800">{{ safetyStore.statsOverview?.total_incidents || 0 }}</p>
            </div>
            <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4">
              <div class="flex items-center gap-2 mb-2">
                <UserX class="text-red-600" :size="20" />
                <span class="text-sm text-red-700 font-medium">高风险成员</span>
              </div>
              <p class="text-2xl font-bold text-red-800">{{ safetyStore.statsOverview?.high_risk_member_count || 0 }}</p>
            </div>
            <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4">
              <div class="flex items-center gap-2 mb-2">
                <CheckCircle class="text-green-600" :size="20" />
                <span class="text-sm text-green-700 font-medium">隐患解决率</span>
              </div>
              <p class="text-2xl font-bold text-green-800">{{ ((safetyStore.statsOverview?.hazard_resolution_rate || 0) * 100).toFixed(0) }}%</p>
            </div>
          </div>

          <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div>
              <h4 class="text-base font-medium text-[#1F2937] mb-3">突发事件类型分布</h4>
              <div v-if="!safetyStore.incidentTypeStats.length" class="text-sm text-[#9CA3AF] py-8 text-center">暂无数据</div>
              <div v-else class="h-64">
                <Bar :data="incidentTypeChartData" :options="incidentTypeChartOptions" />
              </div>
            </div>

            <div>
              <h4 class="text-base font-medium text-[#1F2937] mb-3">场地隐患类型统计</h4>
              <div v-if="!safetyStore.hazardTypeStats.length" class="text-sm text-[#9CA3AF] py-8 text-center">暂无数据</div>
              <div v-else class="space-y-3">
                <div
                  v-for="item in safetyStore.hazardTypeStats"
                  :key="item.hazard_type"
                  class="flex items-center gap-3"
                >
                  <span class="text-sm text-[#1F2937] w-24 font-medium">{{ HAZARD_TYPE_MAP[item.hazard_type] }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                    <div
                      class="h-full bg-[#E53935] rounded-full transition-all duration-500"
                      :style="{ width: (item.count / maxHazardCount) * 100 + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-semibold text-[#E53935] w-8 text-right">{{ item.count }}</span>
                  <span v-if="item.unresolved_count > 0" class="text-xs text-red-500 bg-red-50 px-2 py-0.5 rounded">
                    {{ item.unresolved_count }}待处理
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div>
              <h4 class="text-base font-medium text-[#1F2937] mb-3">高风险成员名单</h4>
              <div v-if="!safetyStore.highRiskMemberStats.length" class="text-sm text-[#9CA3AF] py-8 text-center">暂无高风险成员</div>
              <div v-else class="space-y-2 max-h-64 overflow-y-auto pr-2 scrollbar-thin">
                <div
                  v-for="item in safetyStore.highRiskMemberStats"
                  :key="item.member_id"
                  class="flex items-center gap-3 p-3 rounded-lg border border-[#E5E7EB] hover:bg-gray-50"
                >
                  <div class="w-10 h-10 rounded-full bg-[#E53935]/10 flex items-center justify-center shrink-0">
                    <User class="text-[#E53935]" :size="20" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="text-sm font-medium text-[#1F2937]">{{ item.member_name }}</span>
                      <span v-if="item.member_age" class="text-xs text-[#6B7280]">{{ item.member_age }}岁</span>
                      <span :class="RISK_LEVEL_COLOR_MAP[item.risk_level]" class="px-2 py-0.5 text-xs rounded-full font-medium">
                        {{ RISK_LEVEL_MAP[item.risk_level] }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2 text-xs text-[#6B7280]">
                      <span>事件: {{ item.incident_count }}次</span>
                      <span v-if="item.last_incident_date">· 最近: {{ formatShortDate(item.last_incident_date) }}</span>
                    </div>
                    <div v-if="item.health_conditions.length" class="flex flex-wrap gap-1 mt-1">
                      <span v-for="cond in item.health_conditions" :key="cond" class="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                        {{ cond }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 class="text-base font-medium text-[#1F2937] mb-3">应急处置统计</h4>
              <div v-if="!safetyStore.emergencyResponseStats" class="text-sm text-[#9CA3AF] py-8 text-center">暂无数据</div>
              <div v-else class="space-y-4">
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-gray-50 rounded-lg p-3">
                    <p class="text-xs text-[#6B7280] mb-1">事件解决率</p>
                    <div class="flex items-center gap-2">
                      <div class="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          class="h-full bg-green-500 rounded-full"
                          :style="{ width: safetyStore.emergencyResponseStats.resolution_rate * 100 + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm font-semibold text-green-600">
                        {{ (safetyStore.emergencyResponseStats.resolution_rate * 100).toFixed(0) }}%
                      </span>
                    </div>
                    <p class="text-xs text-[#6B7280] mt-1">
                      {{ safetyStore.emergencyResponseStats.resolved_count }}/{{ safetyStore.emergencyResponseStats.total_incidents }}
                    </p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-3">
                    <p class="text-xs text-[#6B7280] mb-1">家属通知率</p>
                    <div class="flex items-center gap-2">
                      <div class="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          class="h-full bg-blue-500 rounded-full"
                          :style="{ width: safetyStore.emergencyResponseStats.family_notification_rate * 100 + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm font-semibold text-blue-600">
                        {{ (safetyStore.emergencyResponseStats.family_notification_rate * 100).toFixed(0) }}%
                      </span>
                    </div>
                    <p class="text-xs text-[#6B7280] mt-1">
                      {{ safetyStore.emergencyResponseStats.family_notified_count }}/{{ safetyStore.emergencyResponseStats.total_incidents }}
                    </p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-3">
                    <p class="text-xs text-[#6B7280] mb-1">社区通知率</p>
                    <div class="flex items-center gap-2">
                      <div class="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          class="h-full bg-purple-500 rounded-full"
                          :style="{ width: safetyStore.emergencyResponseStats.community_notification_rate * 100 + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm font-semibold text-purple-600">
                        {{ (safetyStore.emergencyResponseStats.community_notification_rate * 100).toFixed(0) }}%
                      </span>
                    </div>
                    <p class="text-xs text-[#6B7280] mt-1">
                      {{ safetyStore.emergencyResponseStats.community_notified_count }}/{{ safetyStore.emergencyResponseStats.total_incidents }}
                    </p>
                  </div>
                  <div class="bg-gray-50 rounded-lg p-3">
                    <p class="text-xs text-[#6B7280] mb-1">平均响应时间</p>
                    <p class="text-lg font-bold text-[#1F2937]">
                      {{ safetyStore.emergencyResponseStats.avg_response_time_minutes || '-' }}
                      <span class="text-xs font-normal text-[#6B7280]">分钟</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 class="text-base font-medium text-[#1F2937] mb-3">历次排练安全记录</h4>
            <div v-if="!safetyStore.rehearsalStats.length" class="text-sm text-[#9CA3AF] py-4 text-center">暂无数据</div>
            <div v-else class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-left text-[#6B7280] border-b border-[#E5E7EB]">
                    <th class="pb-3 font-medium">排练日期</th>
                    <th class="pb-3 font-medium">曲目</th>
                    <th class="pb-3 font-medium text-center">风险等级</th>
                    <th class="pb-3 font-medium text-center">突发事件</th>
                    <th class="pb-3 font-medium text-center">场地隐患</th>
                    <th class="pb-3 font-medium text-center">高风险成员</th>
                    <th class="pb-3 font-medium text-center">家属通知</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#F3F4F6]">
                  <tr v-for="item in safetyStore.rehearsalStats" :key="item.rehearsal_id">
                    <td class="py-3 text-[#1F2937]">{{ item.rehearsal_date }}</td>
                    <td class="py-3 text-[#6B7280]">{{ item.song_name }}</td>
                    <td class="py-3 text-center">
                      <span :class="RISK_LEVEL_COLOR_MAP[item.risk_level]" class="px-2 py-0.5 text-xs rounded-full font-medium">
                        {{ RISK_LEVEL_MAP[item.risk_level] }}
                      </span>
                    </td>
                    <td class="py-3 text-center">
                      <span :class="item.incident_count > 0 ? 'text-orange-600' : 'text-green-600'" class="font-medium">
                        {{ item.incident_count }}
                      </span>
                    </td>
                    <td class="py-3 text-center">
                      <span :class="item.hazard_count > 0 ? 'text-red-600' : 'text-green-600'" class="font-medium">
                        {{ item.hazard_count }}
                      </span>
                    </td>
                    <td class="py-3 text-center">
                      <span :class="item.high_risk_member_count > 0 ? 'text-orange-600' : 'text-[#6B7280]'" class="font-medium">
                        {{ item.high_risk_member_count }}
                      </span>
                    </td>
                    <td class="py-3 text-center">
                      <span :class="item.family_notified_count > 0 ? 'text-blue-600' : 'text-[#6B7280]'" class="font-medium">
                        {{ item.family_notified_count }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { BarChart3, ShieldCheck, AlertTriangle, UserX, CheckCircle, User } from 'lucide-vue-next'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from 'chart.js'
import { useStatisticsStore } from '@/stores/statistics'
import { useChecklistsStore } from '@/stores/checklists'
import { useSafetyStore } from '@/stores/safety'
import type { ErrorPositionItem } from '@/types'
import { CHECK_CATEGORY_MAP, HAZARD_TYPE_MAP, RISK_LEVEL_MAP, RISK_LEVEL_COLOR_MAP, INCIDENT_TYPE_MAP } from '@/types'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const statisticsStore = useStatisticsStore()
const checklistsStore = useChecklistsStore()
const safetyStore = useSafetyStore()
const heatmapRef = ref<HTMLCanvasElement>()

const rehearsalChartData = computed(() => {
  const data = statisticsStore.rehearsalCounts
  return {
    labels: data.map((d) => d.song_name),
    datasets: [
      {
        label: '排练次数',
        data: data.map((d) => d.count),
        backgroundColor: '#E53935',
        borderRadius: 6,
      },
    ],
  }
})

const rehearsalChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1, font: { size: 13 } },
    },
    x: {
      ticks: { font: { size: 13 } },
    },
  },
}

const substituteChartData = computed(() => {
  const data = statisticsStore.substituteRates
  const colors = ['#E53935', '#FFB300', '#1E88E5', '#43A047', '#8E24AA', '#00ACC1']
  return {
    labels: data.map((d) => d.song_name),
    datasets: [
      {
        data: data.map((d) => +(d.rate * 100).toFixed(1)),
        backgroundColor: colors.slice(0, data.length),
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  }
})

const substituteChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right' as const,
      labels: { font: { size: 13 } },
    },
    tooltip: {
      callbacks: {
        label: (ctx: any) => `${ctx.label}: ${ctx.parsed}%`,
      },
    },
  },
}

const attendanceList = computed(() => {
  return statisticsStore.attendanceStats
})

const maxAbnormalCount = computed(() => {
  return Math.max(...checklistsStore.abnormalTypes.map((t) => t.count), 1)
})

const maxHazardCount = computed(() => {
  return Math.max(...safetyStore.hazardTypeStats.map((t) => t.count), 1)
})

const incidentTypeChartData = computed(() => {
  const data = safetyStore.incidentTypeStats
  return {
    labels: data.map((d) => INCIDENT_TYPE_MAP[d.incident_type]),
    datasets: [
      {
        label: '发生次数',
        data: data.map((d) => d.count),
        backgroundColor: [
          '#E53935', '#FF9800', '#F44336', '#9C27B0',
          '#FF5722', '#2196F3', '#4CAF50', '#FFC107',
          '#673AB7', '#607D8B',
        ],
        borderRadius: 6,
      },
    ],
  }
})

const incidentTypeChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { stepSize: 1, font: { size: 12 } },
    },
    x: {
      ticks: { font: { size: 11 } },
    },
  },
}

function getRateColor(rate: number) {
  if (rate >= 0.8) return 'bg-green-500'
  if (rate >= 0.6) return 'bg-[#FFB300]'
  return 'bg-[#E53935]'
}

function getRateTextColor(rate: number) {
  if (rate >= 0.8) return 'text-green-600'
  if (rate >= 0.6) return 'text-[#FFB300]'
  return 'text-[#E53935]'
}

function formatShortDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

function drawHeatmap(data: ErrorPositionItem[]) {
  const canvas = heatmapRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height
  ctx.clearRect(0, 0, width, height)

  const rows = 3
  const cols = 4
  const cellW = width / cols
  const cellH = height / rows
  const padding = 4

  const maxCount = Math.max(...data.map((d) => d.count), 1)

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const posIndex = r * cols + c + 1
      const posId = `P${posIndex}`
      const item = data.find((d) => d.position_id === posId)
      const intensity = item ? item.count / maxCount : 0

      const x = c * cellW + padding
      const y = r * cellH + padding
      const w = cellW - padding * 2
      const h = cellH - padding * 2

      ctx.fillStyle = `rgba(229, 57, 53, ${intensity * 0.8 + 0.05})`
      ctx.beginPath()
      ctx.roundRect(x, y, w, h, 8)
      ctx.fill()

      ctx.fillStyle = intensity > 0.4 ? '#fff' : '#1F2937'
      ctx.font = '13px Noto Sans SC'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(item ? `${item.count}次` : posId, x + w / 2, y + h / 2)
    }
  }
}

watch(
  () => statisticsStore.errorPositions,
  (val) => {
    if (val.length) {
      nextTick(() => drawHeatmap(val))
    }
  }
)

onMounted(async () => {
  await Promise.all([
    statisticsStore.fetchAll(),
    checklistsStore.fetchAllStats(),
    safetyStore.fetchAllStats(),
  ])
  if (statisticsStore.errorPositions.length) {
    nextTick(() => drawHeatmap(statisticsStore.errorPositions))
  }
})
</script>
