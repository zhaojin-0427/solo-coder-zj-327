import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  OverviewStats,
  RehearsalCountItem,
  SubstituteRateItem,
  ErrorPositionItem,
  AttendanceStatItem,
  PerformanceConfirmationStatItem,
} from '@/types'
import { useApi } from '@/composables/useApi'

export const useStatisticsStore = defineStore('statistics', () => {
  const api = useApi()
  const overview = ref<OverviewStats | null>(null)
  const rehearsalCounts = ref<RehearsalCountItem[]>([])
  const substituteRates = ref<SubstituteRateItem[]>([])
  const errorPositions = ref<ErrorPositionItem[]>([])
  const attendanceStats = ref<AttendanceStatItem[]>([])
  const performanceConfirmations = ref<PerformanceConfirmationStatItem[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [ov, rc, sr, ep, as, pc] = await Promise.all([
        api.statistics.overview(),
        api.statistics.rehearsalCounts(),
        api.statistics.substituteRates(),
        api.statistics.errorPositions(),
        api.statistics.attendance(),
        api.statistics.performanceConfirmations(),
      ])
      overview.value = ov
      rehearsalCounts.value = rc
      substituteRates.value = sr
      errorPositions.value = ep
      attendanceStats.value = as
      performanceConfirmations.value = pc
    } catch (e) {
      console.error('Failed to fetch statistics', e)
    } finally {
      loading.value = false
    }
  }

  return {
    overview,
    rehearsalCounts,
    substituteRates,
    errorPositions,
    attendanceStats,
    performanceConfirmations,
    loading,
    fetchAll,
  }
})
