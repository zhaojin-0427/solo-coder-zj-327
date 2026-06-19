import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Member, HeightRange } from '@/types'
import { useApi } from '@/composables/useApi'

export const useMembersStore = defineStore('members', () => {
  const api = useApi()
  const members = ref<Member[]>([])
  const loading = ref(false)

  async function fetchMembers() {
    loading.value = true
    try {
      members.value = await api.members.list()
    } catch (e) {
      console.error('Failed to fetch members', e)
    } finally {
      loading.value = false
    }
  }

  async function createMember(data: { name: string; height_range: HeightRange; phone?: string; song_ids?: number[]; substitute_positions?: string[] }) {
    try {
      const member = await api.members.create(data)
      members.value.push(member)
      return member
    } catch (e) {
      console.error('Failed to create member', e)
      throw e
    }
  }

  async function updateMember(id: number, data: { name?: string; height_range?: HeightRange; phone?: string; song_ids?: number[]; substitute_positions?: string[] }) {
    try {
      const member = await api.members.update(id, data)
      const idx = members.value.findIndex((m) => m.id === id)
      if (idx !== -1) members.value[idx] = member
      return member
    } catch (e) {
      console.error('Failed to update member', e)
      throw e
    }
  }

  async function deleteMember(id: number) {
    try {
      await api.members.delete(id)
      members.value = members.value.filter((m) => m.id !== id)
    } catch (e) {
      console.error('Failed to delete member', e)
      throw e
    }
  }

  function getMemberById(id: number) {
    return members.value.find((m) => m.id === id)
  }

  return { members, loading, fetchMembers, createMember, updateMember, deleteMember, getMemberById }
})
