import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  PerformanceTask,
  PerformanceTaskDetail,
  PerformanceTaskWithSongDetails,
  PerformanceConfirmation,
  PerformanceSongTaskCreate,
} from '@/types'
import { useApi } from '@/composables/useApi'

export const usePerformancesStore = defineStore('performances', () => {
  const api = useApi()
  const performances = ref<PerformanceTask[]>([])
  const currentPerformance = ref<PerformanceTaskDetail | PerformanceTaskWithSongDetails | null>(null)
  const loading = ref(false)

  const unconfirmedCount = computed(() => {
    return performances.value.reduce((sum, p) => sum + p.unconfirmed_count, 0)
  })

  async function fetchList() {
    loading.value = true
    try {
      performances.value = await api.performances.list()
    } catch (e) {
      console.error('Failed to fetch performances', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id: number) {
    loading.value = true
    try {
      currentPerformance.value = await api.performances.get(id)
    } catch (e) {
      console.error('Failed to fetch performance detail', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchWithSongDetails(id: number) {
    loading.value = true
    try {
      currentPerformance.value = await api.performances.getWithSongDetails(id)
    } catch (e) {
      console.error('Failed to fetch performance with song details', e)
    } finally {
      loading.value = false
    }
  }

  async function create(data: {
    name: string
    location: string
    meeting_time: string
    start_time: string
    costume_requirements?: string | null
    notes?: string | null
    song_tasks?: PerformanceSongTaskCreate[]
    member_ids?: number[]
  }) {
    const result = await api.performances.create(data)
    await fetchList()
    return result
  }

  async function update(
    id: number,
    data: {
      name?: string
      location?: string
      meeting_time?: string
      start_time?: string
      costume_requirements?: string | null
      notes?: string | null
      song_tasks?: PerformanceSongTaskCreate[]
      member_ids?: number[]
    }
  ) {
    const result = await api.performances.update(id, data)
    await fetchList()
    return result
  }

  async function remove(id: number) {
    await api.performances.delete(id)
    await fetchList()
  }

  async function updateConfirmation(taskId: number, memberId: number, data: {
    status?: string
    transport_mode?: string | null
    remark?: string | null
    phone_reminded?: boolean
  }) {
    const result = await api.performances.updateConfirmation(taskId, memberId, data)
    if (currentPerformance.value) {
      await fetchWithSongDetails(taskId)
    }
    return result
  }

  async function markPhoneReminded(taskId: number, memberId: number) {
    return updateConfirmation(taskId, memberId, { phone_reminded: true })
  }

  return {
    performances,
    currentPerformance,
    loading,
    unconfirmedCount,
    fetchList,
    fetchDetail,
    fetchWithSongDetails,
    create,
    update,
    remove,
    updateConfirmation,
    markPhoneReminded,
  }
})
