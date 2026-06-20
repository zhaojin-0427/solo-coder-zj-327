import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  Checklist,
  ChecklistSummary,
  CheckItem,
  CheckItemAbnormalDetail,
  PreCheckStatItem,
  MemberCompletionRankItem,
  FrequentAbnormalTypeItem,
} from '@/types'
import { useApi } from '@/composables/useApi'

export const useChecklistsStore = defineStore('checklists', () => {
  const api = useApi()
  const currentChecklist = ref<Checklist | null>(null)
  const summaries = ref<ChecklistSummary[]>([])
  const abnormalItems = ref<CheckItemAbnormalDetail[]>([])
  const preCheckStats = ref<PreCheckStatItem[]>([])
  const memberRank = ref<MemberCompletionRankItem[]>([])
  const abnormalTypes = ref<FrequentAbnormalTypeItem[]>([])
  const loading = ref(false)

  async function generateChecklist(performanceId: number, items?: { song_id: number; category: string; item_name: string; responsible_member_id?: number; position_id?: string; deadline?: string }[]) {
    loading.value = true
    try {
      currentChecklist.value = await api.checklists.generate(performanceId, items)
    } catch (e) {
      console.error('Failed to generate checklist', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchChecklist(performanceId: number) {
    loading.value = true
    try {
      currentChecklist.value = await api.checklists.getByPerformance(performanceId)
    } catch (e) {
      console.error('Failed to fetch checklist', e)
      currentChecklist.value = null
    } finally {
      loading.value = false
    }
  }

  async function fetchSummary(performanceId: number) {
    try {
      return await api.checklists.getSummary(performanceId)
    } catch (e) {
      console.error('Failed to fetch summary', e)
      return null
    }
  }

  async function fetchAbnormalItems(performanceId: number) {
    try {
      abnormalItems.value = await api.checklists.getAbnormalItems(performanceId)
    } catch (e) {
      console.error('Failed to fetch abnormal items', e)
      abnormalItems.value = []
    }
  }

  async function fetchMemberItems(performanceId: number, memberId: number) {
    try {
      return await api.checklists.getMemberItems(performanceId, memberId)
    } catch (e) {
      console.error('Failed to fetch member items', e)
      return []
    }
  }

  async function updateItem(itemId: number, data: { status?: string; abnormal_description?: string; photo_url?: string }) {
    const result = await api.checklists.updateItem(itemId, data)
    if (currentChecklist.value) {
      const idx = currentChecklist.value.items.findIndex((i) => i.id === itemId)
      if (idx >= 0) {
        currentChecklist.value.items[idx] = result
      }
    }
    return result
  }

  async function addItem(performanceId: number, data: { song_id: number; category: string; item_name: string; responsible_member_id?: number; position_id?: string; deadline?: string }) {
    const result = await api.checklists.addItem(performanceId, data)
    if (currentChecklist.value) {
      currentChecklist.value.items.push(result)
    }
    return result
  }

  async function deleteItem(itemId: number) {
    await api.checklists.deleteItem(itemId)
    if (currentChecklist.value) {
      currentChecklist.value.items = currentChecklist.value.items.filter((i) => i.id !== itemId)
    }
  }

  async function fetchAllSummaries() {
    try {
      summaries.value = await api.checklists.getAllSummaries()
    } catch (e) {
      console.error('Failed to fetch summaries', e)
    }
  }

  async function fetchPreCheckStats() {
    try {
      preCheckStats.value = await api.checklists.getPreCheckStats()
    } catch (e) {
      console.error('Failed to fetch pre-check stats', e)
    }
  }

  async function fetchMemberRank() {
    try {
      memberRank.value = await api.checklists.getMemberRank()
    } catch (e) {
      console.error('Failed to fetch member rank', e)
    }
  }

  async function fetchAbnormalTypes() {
    try {
      abnormalTypes.value = await api.checklists.getAbnormalTypes()
    } catch (e) {
      console.error('Failed to fetch abnormal types', e)
    }
  }

  async function fetchAllStats() {
    loading.value = true
    try {
      await Promise.all([
        fetchAllSummaries(),
        fetchPreCheckStats(),
        fetchMemberRank(),
        fetchAbnormalTypes(),
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    currentChecklist,
    summaries,
    abnormalItems,
    preCheckStats,
    memberRank,
    abnormalTypes,
    loading,
    generateChecklist,
    fetchChecklist,
    fetchSummary,
    fetchAbnormalItems,
    fetchMemberItems,
    updateItem,
    addItem,
    deleteItem,
    fetchAllSummaries,
    fetchPreCheckStats,
    fetchMemberRank,
    fetchAbnormalTypes,
    fetchAllStats,
  }
})
