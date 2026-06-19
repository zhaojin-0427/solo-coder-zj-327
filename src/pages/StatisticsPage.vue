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
import type { ErrorPositionItem } from '@/types'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const statisticsStore = useStatisticsStore()
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
  await statisticsStore.fetchAll()
  if (statisticsStore.errorPositions.length) {
    nextTick(() => drawHeatmap(statisticsStore.errorPositions))
  }
})
</script>
