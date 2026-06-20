import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SubstituteAssignment, AttendanceRecord, SubstituteRecommend } from '@/types'
import { useApi } from '@/composables/useApi'

export const useSubstitutesStore = defineStore('substitutes', () => {
  const api = useApi()
  const substitutes = ref<SubstituteAssignment[]>([])
  const attendance = ref<AttendanceRecord[]>([])
  const recommendations = ref<SubstituteRecommend[]>([])
  const loading = ref(false)

  async function fetchSubstitutes(songId: number) {
    loading.value = true
    try {
      substitutes.value = await api.substitutes.list(songId)
    } catch (e) {
      console.error('Failed to fetch substitutes', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchAttendance(songId: number) {
    try {
      attendance.value = await api.attendance.list(songId)
    } catch (e) {
      console.error('Failed to fetch attendance', e)
    }
  }

  async function markAttendance(data: { member_id: number; song_id: number; date: string; status: string }) {
    try {
      const record = await api.attendance.mark(data)
      const idx = attendance.value.findIndex(
        (a) => a.member_id === data.member_id && a.song_id === data.song_id
      )
      if (idx !== -1) {
        attendance.value[idx] = record
      } else {
        attendance.value.push(record)
      }
    } catch (e) {
      console.error('Failed to mark attendance', e)
      throw e
    }
  }

  async function fetchRecommendations(songId: number, absentMemberId: number): Promise<SubstituteRecommend[]> {
    loading.value = true
    try {
      const data = await api.substitutes.recommend(songId, absentMemberId)
      recommendations.value = data
      return data
    } catch (e) {
      console.error('Failed to fetch recommendations', e)
      recommendations.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  async function assignSubstitute(data: { song_id: number; absent_member_id: number; substitute_member_id: number; position_id: string; priority?: number }) {
    try {
      const sub = await api.substitutes.assign(data)
      substitutes.value.push(sub)
      return sub
    } catch (e) {
      console.error('Failed to assign substitute', e)
      throw e
    }
  }

  async function updatePriority(id: number, priority: number) {
    try {
      const updated = await api.substitutes.updatePriority(id, priority)
      const idx = substitutes.value.findIndex((s) => s.id === id)
      if (idx !== -1) substitutes.value[idx] = updated
      return updated
    } catch (e) {
      console.error('Failed to update priority', e)
      throw e
    }
  }

  return {
    substitutes,
    attendance,
    recommendations,
    loading,
    fetchSubstitutes,
    fetchAttendance,
    markAttendance,
    fetchRecommendations,
    assignSubstitute,
    updatePriority,
  }
})
