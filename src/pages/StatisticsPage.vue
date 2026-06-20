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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { BarChart3 } from 'lucide-vue-next'
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
import type { ErrorPositionItem } from '@/types'
import { CHECK_CATEGORY_MAP } from '@/types'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const statisticsStore = useStatisticsStore()
const checklistsStore = useChecklistsStore()
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
  ])
  if (statisticsStore.errorPositions.length) {
    nextTick(() => drawHeatmap(statisticsStore.errorPositions))
  }
})
</script>
