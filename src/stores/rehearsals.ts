import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RehearsalRecord, RehearsalDetail } from '@/types'
import { useApi } from '@/composables/useApi'

export const useRehearsalsStore = defineStore('rehearsals', () => {
  const api = useApi()
  const rehearsals = ref<RehearsalRecord[]>([])
  const loading = ref(false)

  async function fetchRehearsals(songId?: number) {
    loading.value = true
    try {
      rehearsals.value = await api.rehearsals.list(songId)
    } catch (e) {
      console.error('Failed to fetch rehearsals', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id: number): Promise<RehearsalDetail | null> {
    try {
      return await api.rehearsals.get(id)
    } catch (e) {
      console.error('Failed to fetch rehearsal detail', e)
      return null
    }
  }

  async function createRehearsal(data: {
    song_id: number
    date: string
    duration_minutes?: number
    teacher_notes?: string
    errors?: { position_id: string; error_type: string; beat_number?: number; description?: string }[]
  }) {
    try {
      const record = await api.rehearsals.create(data)
      rehearsals.value.push(record)
      return record
    } catch (e) {
      console.error('Failed to create rehearsal', e)
      throw e
    }
  }

  return { rehearsals, loading, fetchRehearsals, fetchDetail, createRehearsal }
})
